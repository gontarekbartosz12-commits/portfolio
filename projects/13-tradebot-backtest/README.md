# Tradebot — swing-momentum backtest (research that said "don't ship")

A rigorous **vectorbt** backtest of a swing-momentum strategy on US large caps, built to
**decide whether a production bot was even worth building**. It wasn't yet — and that
disciplined "no" is the point.

> All code here is included and **secret-free** (data via `yfinance`, no API keys).

## The strategy
- Universe: ~150 US large caps (top-100 S&P 500 + top-50 NASDAQ-100), deliberately static for 2018–2026.
- Entry: Mondays at next-day **OPEN** (no look-ahead).
- Signal: composite momentum `0.5·ROC(20) + 0.3·ROC(60) + 0.2·(1 − dist_from_52w_high)`.
- Trend filter: `ADX(14) > 20` **and** `close > SMA(200)`.
- Sizing: top-5 equal-weight ($200/position on $1,000).
- Exits: trailing stop at `entry − 2·ATR(14)`, drop-out, 10-day time stop.
- Costs: 5 bps slippage/side.

## Decision gates (fail any → do NOT build the production bot)
1. Net annualised Sharpe ≥ 0.5
2. Max drawdown ≤ 15%
3. Walk-forward median test Sharpe ≥ 0.3 (6 folds, 18mo train / 6mo test)
4. ≥ 150 completed trades

## Files (included)
- `strategy.py` · `indicators.py` · `universe.py` · `data_loader.py` (yfinance + parquet cache) · `requirements.txt`
- `STRATEGY_NOTES.md` — the original spec + gates.

## What it demonstrates
- **Quant rigor** — walk-forward validation, no-look-ahead entries, explicit cost model.
- **Intellectual honesty** — `universe.py` openly documents survivorship and look-ahead
  biases and how they're mitigated; the project is **gated on evidence**, not vibes.
- Clean Python: cached data loader, separated indicators/strategy/universe modules.

## Stack
Python · vectorbt · pandas · yfinance · Jupyter (backtest notebook)

> Status: paused at the backtest-verdict gate — exactly how a careful trader avoids
> shipping a losing strategy.
