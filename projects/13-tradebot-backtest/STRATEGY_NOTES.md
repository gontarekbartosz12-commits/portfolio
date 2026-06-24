# Strategy 1: Swing Momentum Backtest

Sanity-check backtest using vectorbt before committing to production infrastructure.

## What this does

Validates a swing-momentum strategy on US large caps (top 100 S&P 500 + top 50 NASDAQ-100) with:
- Daily-bar entries on Mondays at next-day OPEN (no look-ahead)
- Composite momentum score: 0.5*ROC(20) + 0.3*ROC(60) + 0.2*(1 - dist_from_52w_high)
- Trend filter: ADX(14) > 20 AND close > SMA(200)
- Top 5 equal-weight ($200/position on $1000 capital)
- Trail stop at entry - 2*ATR(14), drop-out exit, 10-day time stop
- 5 bps slippage per side, 0% commission

## Decision Gates (fail any -> do NOT build production bot)

1. Net Sharpe (annualized) >= 0.5
2. Max drawdown <= 15%
3. Walk-forward median test Sharpe >= 0.3 (6 folds, 18mo train / 6mo test)
4. >= 150 completed trades

## Setup (Windows)

Open PowerShell or CMD inside `C:\Users\gonta\tradebot\backtest\`:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m ipykernel install --user --name=tradebot-bt --display-name "tradebot-bt"
jupyter lab
```

Then open `backtest_strategy_1.ipynb` and select kernel **tradebot-bt**.

Run cells top-to-bottom. First run downloads ~150 tickers from yfinance (~10 min). Subsequent runs hit the parquet cache and complete in <30s up to indicator computation; full backtest with walk-forward takes ~2-5 min.

## Files

- `requirements.txt` — pinned deps
- `universe.py` — static SP500+NDX top-150 list (late-2017 snapshot)
- `data_loader.py` — yfinance fetcher with parquet disk cache + 24h TTL
- `indicators.py` — ROC, SMA, ADX, dist-from-52w-high, ATR (pure pandas)
- `strategy.py` — score computation, weekly Monday signal generation, vectorbt portfolio build
- `backtest_strategy_1.ipynb` — main runnable notebook (10 cells)
- `data/cache/` — parquet cache (gitignored)

## Caveats you MUST understand

### Survivorship bias (significant)
yfinance only gives you data for tickers that EXIST today. Companies that delisted, went bankrupt, or were acquired between 2018-2026 are silently absent from your universe. Real out-of-sample performance will likely be 1-3% lower than what this backtest shows. **Treat the backtest Sharpe as an upper bound.**

### Static universe
Universe is fixed to a late-2017 snapshot. In reality, S&P 500 / NASDAQ-100 composition rotates ~5-10% per year. We do not rebalance the universe quarterly here — this is a known simplification documented in `universe.py`. Impact: missed entrants like NVDA growth phase 2018 are partially mitigated since NVDA was already large in 2017; missed exits (e.g. names that fell out post-2017) bias toward winners.

### yfinance reliability
yfinance is free but unofficial. Symbol changes (e.g. FB -> META, GOOG/GOOGL splits, FB rename), corporate actions, and rate-limiting can break runs. The data loader has retry logic and skips failed tickers; if you see "Skipped N tickers" in the load log, that's why. Verify the count is sane (<10% of universe).

### What backtest costs DO NOT model
- No borrow fees (we are long-only, irrelevant)
- No tax drag
- No slippage scaling with order size (5 bps assumed flat — fine for $200 positions on liquid names)
- No partial fills, no opening auction price impact

If gates pass: still treat this as evidence, not proof. Run paper for 4-8 weeks before live.

If gates fail: do NOT proceed to production. Iterate on the strategy spec, or pivot.

## Troubleshooting

**`ModuleNotFoundError: vectorbt`** — venv not activated. `venv\Scripts\activate` then re-run.

**`yfinance` returns empty for a ticker** — symbol changed or delisted. The loader logs and skips. Check the run log; if too many skips (>15), update `universe.py`.

**Numba compile errors** — vectorbt uses numba JIT. First run on a fresh venv compiles caches (~30s). If errors persist: `pip install --upgrade numba llvmlite`.

**ADX values look wrong** — verify with the assertion cell that ADX is within [0, 100]. We compute Wilder smoothing manually in `indicators.py`.

**Notebook kernel dies on `from_signals`** — RAM. Reduce universe to 100 names or run on a machine with >=8 GB free.
