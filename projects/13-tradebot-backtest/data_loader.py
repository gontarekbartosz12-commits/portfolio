"""
yfinance data loader with parquet disk cache and 24h TTL.

Public API:
    fetch_prices(tickers, start, end, cache_dir, force_refresh=False) -> dict[str, pd.DataFrame]
    build_panel(price_dict, field) -> pd.DataFrame
    apply_universe_filters(price_dict, min_adv_usd, min_price) -> dict[str, pd.DataFrame]

Each ticker is cached individually so partial failures don't poison the cache.
"""
from __future__ import annotations

import time
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf

CACHE_TTL_HOURS: int = 24
_RETRY_ATTEMPTS: int = 3
_RETRY_DELAY_S: float = 2.0


def _cache_path(cache_dir: Path, ticker: str) -> Path:
    safe = ticker.replace("/", "_").replace(" ", "_")
    return cache_dir / f"{safe}.parquet"


def _is_cache_fresh(path: Path, ttl_hours: int = CACHE_TTL_HOURS) -> bool:
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age = datetime.now(timezone.utc) - mtime
    return age < timedelta(hours=ttl_hours)


def _fetch_one(
    ticker: str,
    start: str,
    end: str,
) -> pd.DataFrame | None:
    """Fetch a single ticker with retries. Returns None on permanent failure."""
    last_err: Exception | None = None
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    progress=False,
                    auto_adjust=True,
                    actions=False,
                    threads=False,
                )
            if df is None or df.empty:
                last_err = RuntimeError("empty frame")
                time.sleep(_RETRY_DELAY_S * (attempt + 1))
                continue
            # Flatten yfinance multiindex if present (single-ticker download
            # sometimes returns a 2-level column index in newer yfinance).
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
            df.columns = ["open", "high", "low", "close", "volume"]
            return df.dropna(how="all")
        except Exception as exc:  # broad — yfinance raises many flavors
            last_err = exc
            time.sleep(_RETRY_DELAY_S * (attempt + 1))
    print(f"  [skip] {ticker}: {last_err}")
    return None


def fetch_prices(
    tickers: Iterable[str],
    start: str,
    end: str,
    cache_dir: str | Path,
    force_refresh: bool = False,
    verbose: bool = True,
) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV for many tickers. Returns dict[ticker -> DataFrame].

    Cache layout: one parquet per ticker. TTL 24h.
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    tickers = list(dict.fromkeys(tickers))  # dedupe, preserve order
    out: dict[str, pd.DataFrame] = {}
    skipped: list[str] = []
    fetched_from_cache = 0
    fetched_from_net = 0

    for i, ticker in enumerate(tickers, 1):
        path = _cache_path(cache_path, ticker)
        if not force_refresh and _is_cache_fresh(path):
            try:
                df = pd.read_parquet(path)
                out[ticker] = df
                fetched_from_cache += 1
                continue
            except Exception:
                pass  # fall through to refetch

        if verbose and i % 10 == 1:
            print(f"  fetching {i}/{len(tickers)} ...")
        df = _fetch_one(ticker, start, end)
        if df is None:
            skipped.append(ticker)
            continue
        try:
            df.to_parquet(path)
        except Exception as exc:
            print(f"  [warn] could not write cache for {ticker}: {exc}")
        out[ticker] = df
        fetched_from_net += 1

    if verbose:
        print(
            f"  Loaded {len(out)} tickers ({fetched_from_cache} from cache, "
            f"{fetched_from_net} from network). Skipped {len(skipped)}: {skipped[:10]}"
            f"{'...' if len(skipped) > 10 else ''}"
        )
    return out


def build_panel(price_dict: dict[str, pd.DataFrame], field: str) -> pd.DataFrame:
    """Stack one OHLCV field across tickers into a single (date x ticker) panel.

    Aligns on outer-join of dates, forward-fill is NOT applied — leave NaNs to
    represent missing trading days for delisted/late-listed names.
    """
    if not price_dict:
        return pd.DataFrame()
    series = {ticker: df[field] for ticker, df in price_dict.items() if field in df.columns}
    panel = pd.DataFrame(series).sort_index()
    return panel


def apply_universe_filters(
    price_dict: dict[str, pd.DataFrame],
    min_adv_usd: float = 50_000_000,
    min_price: float = 10.0,
    lookback_days: int = 60,
) -> dict[str, pd.DataFrame]:
    """Drop tickers failing ADV>$50M or price>$10 over the most recent lookback.

    Filter is applied using the LAST `lookback_days` rows so it reflects current
    liquidity at the start of evaluation. We re-check throughout the backtest
    via the same filter logic in `strategy.py`.

    Returns a new dict with offenders removed.
    """
    kept: dict[str, pd.DataFrame] = {}
    for ticker, df in price_dict.items():
        tail = df.tail(lookback_days)
        if tail.empty:
            continue
        last_close = float(tail["close"].iloc[-1])
        avg_dollar_vol = float((tail["close"] * tail["volume"]).mean())
        if last_close < min_price:
            continue
        if avg_dollar_vol < min_adv_usd:
            continue
        kept[ticker] = df
    return kept


if __name__ == "__main__":
    # Smoke test with 3 tickers
    here = Path(__file__).parent / "data" / "cache"
    test = fetch_prices(["AAPL", "MSFT", "NVDA"], "2023-01-01", "2024-01-01", here)
    for tk, df in test.items():
        print(tk, df.shape, df.index.min(), df.index.max())
