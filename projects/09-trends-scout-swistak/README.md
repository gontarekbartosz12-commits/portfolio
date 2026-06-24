# trends_scout + "Świstak" — daily multi-source trend agent

An autonomous agent that runs every morning on a VPS, aggregates trend signals from
four independent sources, ranks them with an LLM for a target niche, and delivers a
digest to Telegram (via the **Świstak** bot) and an Obsidian knowledge vault.

## What it does
```
Reddit (public JSON) ┐
Google Trends        ├─► normalise ─► LLM ranking ─► Świstak (Telegram) + vault
Amazon Movers&Shakers│      (free-model cascade)
TikTok Creative Center┘
```

## Engineering highlights
- **Resilience by design** — each source is isolated; a dead source is logged and the
  run continues. If *all* sources fail, Świstak gets an urgent alert.
- **Free-model cascade** — tries a list of free OpenRouter LLMs until one answers, so
  the whole pipeline costs **$0/month**.
- **Clean secrets** — Telegram + LLM credentials are loaded from env files at runtime;
  nothing is hardcoded (`notify.py` uses `os.getenv`).
- **Chunked delivery** — `notify.py` splits long digests to respect Telegram's 4096-char limit.
- **Scheduled** — cron at 06:00/08:00; output logged and persisted to the vault.

## Files (real production code)
- `main.py` — orchestrator: fetch → score → store → notify, with soft-fail per source.
- `notify.py` — the **Świstak** Telegram sender (chunked, env-based).
- `config.py` — sources, niche and the free-LLM cascade.

## What it demonstrates
A real, deployed **agentic workflow**: scheduled autonomy, multi-source data
integration, LLM ranking with graceful degradation, and a clean human-in-the-loop
notification channel — at zero running cost.

## Stack
Python 3.10 · Reddit/Google Trends/Amazon/TikTok sources · OpenRouter (free models) ·
Telegram Bot API · Obsidian vault · Linux VPS + cron
