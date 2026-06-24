# BeastBot — Quant Model for YouTube-Views Markets

Prices Polymarket markets on YouTube view counts (MrBeast videos, streamer
milestones) and trades only when the market disagrees with the model.

## Edge
Early view data (T+6h…T+24h) follows a **sigmoid growth curve**. Fit the curve →
project saturation views → convert to a bucket probability with a **Normal CDF** →
trade when market vs. model diverge by **≥8 pp**.

## Architecture
```
sources/   live views (YouTube Data API v3) + scraper fallback
model/     growth_curves (SciPy sigmoid) · historical baseline · bootstrap CI
hermes/    3 agents (api / curve / historical) → weighted consensus
pricer.py  Normal CDF → bucket probabilities
trader.py  main loop      monitor.py  exit logic
```

## What makes it good engineering
- **Calibrated uncertainty** — `SIGMA_BY_HORIZON_HR` widens the band for longer horizons.
- **Multi-agent consensus** — explicit `HERMES_WEIGHTS`; skips low-confidence markets.
- **Clean secrets** — every key via `os.getenv()`, nothing committed.
- **Risk-bounded** — capital, base bet, per-market exposure, daily caps, stop-loss.

## Stack
Python 3.10+ · SciPy · YouTube Data API v3 · Polymarket Gamma API · py-clob-client · VPS cron

> `config.py` here is the real (clean) config file — included as a showcase of how
> secrets and model constants are structured.
