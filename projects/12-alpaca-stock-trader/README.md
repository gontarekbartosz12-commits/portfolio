# Alpaca Stock Trader — Lumibot bot + Alpaca MCP

An automated **US-equities paper-trading bot** on Alpaca, plus an AI-driven variant that
lets an LLM place trades through the **official Alpaca MCP** server.

> Paper-first by design (`PAPER=True` is hardcoded in the live entrypoint). Secrets are
> env-based — no keys in this code. Included files: the strategy + its unit tests + the
> operational runbook.

## Two angles
1. **Lumibot strategy bot** — a structured, deployable trading bot built on the Lumibot
   framework with Alpaca as broker.
2. **Alpaca MCP integration** — wiring the **official Alpaca MCP** into Claude so an AI
   agent can query the account and place orders via MCP tools (agentic trading). Paper-first,
   mean-reversion focus.

## The Lumibot bot (engineering)
| File | Purpose |
|------|---------|
| `conservative_v1.py` | **ConservativeV1** strategy — RSI + Bollinger Bands + SMA50/200 trend filter (included). |
| `test_signals.py` | Pure-logic unit tests for the entry-signal stack (included). |
| `RUNBOOK.md` | Operational runbook: deploy, verify, backtest (included). |
| `main.py` | Live entrypoint; loads env, wires the Alpaca broker, `PAPER=True`. |
| `backtest.py` | Backtest via Lumibot `YahooDataBacktesting`. |
| `verify.py` | Post-deploy smoke test: Alpaca auth, orders, positions, Telegram, journal. |
| `deploy/` | **systemd** unit (resource limits + hardening) + idempotent 8-phase `deploy.sh`. |

### What it demonstrates
- **Productionised** trading bot: not a notebook — systemd service, deploy automation,
  a post-deploy smoke test, and unit-tested signal logic.
- **MCP integration** — exactly the "agentic workflows + MCP" skill the role asks for,
  applied to a real broker API.
- **Safety-first** — paper trading hardcoded; secrets via environment.

## Stack
Python · Lumibot · Alpaca API (paper) · Model Context Protocol (Alpaca MCP) · systemd · pytest · Telegram alerts

> Live bot source on VPS (`/root/lumibot-alpaca/`); the strategy, tests and runbook are
> included here as representative, secret-free artifacts.
