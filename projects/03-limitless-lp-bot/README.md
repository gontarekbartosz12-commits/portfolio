# Limitless LP Bot — automated market-making on Base

Automated liquidity provision and inventory management for the Limitless
prediction protocol on the Base chain, with a full research toolchain around it.

## Components
```
core/limitless_lp_bot.py     main LP / market-making loop
core/limitless_inventory.py  position & inventory tracking
data_sources/limitless_api.py  protocol API client
data_sources/base_chain.py     Base-chain (L2) reads
ops/backtest_limitless.py    historical backtester
ops/limitless_monitor.py     live monitoring
tools/limitless_dry_run.py   safe dry-run before going live
```

## What it demonstrates
- **Backtest-before-deploy discipline** — a strategy is backtested *and* dry-run before any live capital.
- On-chain (L2/Base) data integration and inventory/risk management.
- Separation of concerns: data sources · core logic · ops/monitoring · tooling.

## Stack
Python · Limitless API · Base chain (Web3) · backtesting · VPS monitoring

> Source kept in the private repo; this README documents the architecture.
> All secrets are environment-based.
