# Lumibot Alpaca Paper Trading Bot - Operational Runbook

## Files (lines)

| Path | Lines | Purpose |
|------|------:|---------|
| `main.py` | 60 | Live entrypoint; loads env, wires Alpaca broker, hardcodes PAPER=True |
| `backtest.py` | 100 | Backtest entrypoint via YahooDataBacktesting |
| `verify.py` | 130 | Post-deploy smoke test: Alpaca auth, orders, positions, Telegram, journal |
| `strategies/conservative_v1.py` | 320 | ConservativeV1 strategy (RSI + Bollinger + SMA50/200 trend filter) |
| `strategies/__init__.py` | 4 | Package exports |
| `tests/test_signals.py` | 75 | Pure-logic unit tests for entry signal stack |
| `deploy/lumibot-alpaca.service` | 30 | systemd unit with resource limits + hardening |
| `deploy/deploy.sh` | 130 | Idempotent on-VPS deploy (8 phases) |
| `deploy/deploy_sync.sh` | 35 | Workstation-side rsync + remote trigger |
| `requirements.txt` | 12 | Pinned deps |

## Quickstart (workstation)

```bash
cd /c/Users/gonta/Obsidian/vault/20-Bots/alpaca-lumibot
bash deploy/deploy_sync.sh
```

This rsyncs the tree to `ghostshell:/root/lumibot-alpaca/` and runs `deploy.sh` remotely.

## Manual steps if SSH is rate-limited

```bash
# 1) Copy in a single tarball to avoid 8-9 SSH round trips
tar -czf /tmp/alpaca-lumibot.tgz -C /c/Users/gonta/Obsidian/vault/20-Bots alpaca-lumibot
scp /tmp/alpaca-lumibot.tgz ghostshell:/root/

# 2) On VPS
ssh ghostshell '
  set -e
  mkdir -p /root/lumibot-alpaca
  tar -xzf /root/alpaca-lumibot.tgz -C /root --strip-components=1 alpaca-lumibot
  bash /root/lumibot-alpaca/deploy/deploy.sh
'
```

## Kill switch

```bash
systemctl stop lumibot-alpaca
```

This is non-destructive - positions stay open in Alpaca paper account, will be managed when re-started (or close manually in dashboard).

## Paper -> Live flip (DO NOT DO YET)

When you want real money:

1. Edit `/root/lumibot-alpaca/main.py`, change `"PAPER": True` -> `"PAPER": False`
2. Edit `/root/sportowiec/.env`, set `ALPACA_PAPER_MODE=false`
3. Replace `ALPACA_API_KEY` / `ALPACA_API_SECRET` with LIVE keys (NOT paper keys)
4. `systemctl restart lumibot-alpaca`
5. Verify in Alpaca dashboard you are on the LIVE account

NOTE: ConservativeV1 has NOT been validated for live use. Run live for 2+ weeks paper first, audit win rate vs. backtest.

## Telegram sample (from `verify.py`)

```
alpaca_lumibot verify.py
epoch=1736870400
If you see this, alerting works.
```

## Live order alert sample (from `conservative_v1.py`)

```
ALPACA PAPER BUY
  Asset: BTC
  Qty:   0.004821
  Price: $103,250.00
  Notional: $497.78
  Cash left: $98,325.22
  Strategy: ConservativeV1
  See: https://app.alpaca.markets/dashboard/overview
```

## Monitoring

```bash
# Service status
systemctl status lumibot-alpaca

# Live logs
journalctl -u lumibot-alpaca -f

# Journal tail (all signals + orders)
tail -f /root/lumibot-alpaca/journal/alpaca_journal.jsonl

# Order count last 24h
grep -c '"event": "order_submitted"' /root/lumibot-alpaca/journal/alpaca_journal.jsonl

# Open positions via Alpaca API
curl -s -H "APCA-API-KEY-ID: $ALPACA_API_KEY" \
     -H "APCA-API-SECRET-KEY: $ALPACA_API_SECRET" \
     https://paper-api.alpaca.markets/v2/positions | jq .
```

## Expected behaviour (first 24h)

| Window | Expected events |
|--------|----------------|
| First minute | Telegram "service started" alert |
| First hour | 1 tick log; likely 0 entries (signal is rare) |
| First 24h | 0-2 entries (conservative by design) |
| First week | 1-5 round-trip trades |

If you see >5 entries on day 1, something's miscalibrated - stop the bot and inspect journal.

## Backtest gate

Deploy script runs an equity-only 12-month backtest before enabling the service. If the backtest exits non-zero, the service is NOT enabled - you must manually inspect `/root/lumibot-alpaca/backtest_results/` and decide.

## What this bot does NOT touch

- `/root/sportowiec/` (volume bot + sniper) - read-only via env file only
- `/root/.hermes/` (agent/gateway)
- Polymarket wallet `0x3f35F56724066DA10983DeD36129D7E283D1cFD7`
- Freqtrade is STOPPED but kept on disk for archaeology

## Failure modes & fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `systemctl status` shows `Failed` | Alpaca auth bad | Check env keys, re-run verify.py |
| No journal lines after 2h | Strategy not ticking | `journalctl -u lumibot-alpaca` for traceback |
| Backtest returns 0 trades | Signal too strict | Loosen RSI threshold 30 -> 35 or BB std 2.0 -> 1.8 |
| Telegram silent | Bot token bad / chat ID missing | `python3 -c "import os; print(os.environ['TELEGRAM_CHAT_ID'])"` inside venv |
| Orders rejected (`status: rejected`) | Market closed for equity | Expected outside US trading hours; crypto should still work |

## Brutal honesty - known limitations

1. **Lumibot YahooDataBacktesting** has rough edges for crypto. `--equity-only` flag exists for that reason. If you want real crypto backtest, swap in `PolygonDataBacktesting` (paid) or `AlpacaBacktesting` (uses your Alpaca data subscription).
2. **Survivorship & lookahead** are not explicitly handled - SPY/QQQ are survivor-biased ETFs by construction so that's fine, but adding individual names later will need work.
3. **RSI/BB on daily bars** is a slow signal. Expect long flat periods. Do not be alarmed by 0 trades for a week.
4. **No regime detector** - in 2022-style cross-asset bear, even SMA50>SMA200 can fail. ConservativeV1 will sit on cash in such regimes; that's a feature, not a bug.
5. **Slippage modeled = 0** in backtest. Reality on Alpaca paper: marketable orders fill near mid for liquid names, slippage ~1-5bps. Negligible for this size.

## Resume from cold (after VPS reboot)

systemd handles it: `WantedBy=multi-user.target` + `Restart=on-failure`. No action needed.
