#!/usr/bin/env python3
"""trends_scout — a daily, multi-source trend aggregator.

Fetches signals from Reddit, Google Trends, Amazon Movers & Shakers and TikTok
Creative Center, ranks them with an LLM for a target niche, then pushes the digest
to Telegram (via the "Świstak" bot) and saves it to an Obsidian vault.

Runs headless on a VPS via cron (06:00/08:00 daily). Cost: $0/month (free LLM +
system Python + free Telegram).

PORTFOLIO NOTE: real production code. No secrets here — credentials are loaded at
runtime from env files; every fetcher fails soft so one dead source never kills the run.
"""
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


def _load_env():
    """Load Telegram + LLM credentials from env files at runtime (never hardcoded)."""
    files = [
        "/root/sportowiec/.env",
        "/root/.hermes/.env",
        "/root/trends_scout/.env",
    ]
    for fp in files:
        p = Path(fp)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if not v or v in ("...", "<value>", "TODO", "REPLACE_ME"):
                continue
            os.environ[k] = v


_load_env()

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import REDDIT_SUBS, GT_SEEDS, AMAZON_DOMAINS, AMAZON_CATEGORIES, LOG_DIR
from sources import reddit, google_trends, amazon_movers, tiktok_cc
from score import score
from notify import send
from store import save


def run():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    print(f"=== trends_scout start {started.isoformat()} ===")

    raw = {}
    fetchers = [
        ("reddit",        lambda: reddit.fetch(REDDIT_SUBS)),
        ("google_trends", lambda: google_trends.fetch(GT_SEEDS, geo="US")),
        ("amazon_movers", lambda: amazon_movers.fetch(AMAZON_DOMAINS, AMAZON_CATEGORIES)),
        ("tiktok_cc",     lambda: tiktok_cc.fetch()),
    ]
    # Each source is isolated: a failure is logged and the run continues.
    for name, fn in fetchers:
        try:
            items = fn() or []
            raw[name] = items
            print(f"[{name}] {len(items)} items")
        except Exception as e:
            print(f"[{name}] FAIL: {e}")
            traceback.print_exc()
            raw[name] = []

    total = sum(len(v) for v in raw.values())
    print(f"=== total signals: {total} ===")

    if total == 0:
        send("❌ All sources returned empty — check logs/run.log", urgent=True)
        return 2

    try:
        ranked = score(raw)
    except Exception as e:
        print(f"[score] failed: {e}")
        traceback.print_exc()
        ranked = (f"⚠️ LLM ranking failed: {e}\n\nRaw counts: "
                  + ", ".join(f"{k}={len(v)}" for k, v in raw.items()))

    paths = save(raw, ranked)
    print(f"[store] {paths}")

    sent = send(ranked)
    print(f"[notify] sent={sent}")
    return 0 if sent else 1


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as exc:
        traceback.print_exc()
        try:
            send(f"💥 trends_scout crash: {exc}", urgent=True)
        except Exception:
            pass
        sys.exit(99)
