# Polymarket Trading Bots

Algorithmic systems for prediction markets (Polymarket), built to test whether a
retail account can extract a real edge — and to do it safely in paper mode first.

## Files
- `copytrader.py` — mirrors **new** positions from top on-chain wallets, with risk caps.
- `ai_divergence.py` — trades only when an AI fair-value estimate diverges from the live price by ≥10 pp.

> Both files are **sanitised**: no API keys — secrets load from `os.getenv("SIMMER_KEY")`.

## Key engineering ideas
- **Position diffing** — only acts on the *delta* (a newly opened position), never re-copies stale holdings.
- **Risk layer** — copy %, min/max trade size, exposure and drawdown caps enforced before any order.
- **Resilience** — every network call has timeouts + try/except; the loop self-heals on error.
- **Paper-first** — runs in `$SIM` (virtual) mode for validation before any real capital.

## Honest result
Auditing ~3,380 on-chain trades of a "guru" wallet proved naïve copy-trading is
unprofitable at retail scale (fees + slippage ≈ −$222/week on $300). That negative
result killed a bad strategy before risking real money and refocused the project on
model-driven edges.

## Stack
Python · Polymarket Gamma/CLOB + data API · Simmer API · Polygon/Web3 · Linux VPS + cron · Telegram alerts

## Run
```bash
export SIMMER_KEY="your_key_here"
python copytrader.py        # or: python ai_divergence.py
```
