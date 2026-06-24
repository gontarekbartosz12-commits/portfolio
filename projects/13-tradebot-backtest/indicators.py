"""
Technical indicators in pure pandas — explicit and debuggable.

All functions accept either a Series (per-ticker) or a DataFrame (panel: dates x
tickers) and return the same shape. Indicators that need OHLC (ADX, ATR) take
multiple frames.

Public API:
    roc(close, n)
    sma(close, n)
    dist_from_52w_high(close, lookback=252)
    atr(high, low, close, n=14)        -> Wilder smoothing
    adx(high, low, close, n=14)        -> Wilder smoothing, full ADX

All functions assume ascending date index and that columns are tickers.
"""
from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd

PanelLike = Union[pd.Series, pd.DataFrame]


def roc(close: PanelLike, n: int) -> PanelLike:
    """Rate of change over n bars: (close - close.shift(n)) / close.shift(n)."""
    prior = close.shift(n)
    return (close - prior) / prior


def sma(close: PanelLike, n: int) -> PanelLike:
    """Simple moving average over n bars."""
    return close.rolling(window=n, min_periods=n).mean()


def dist_from_52w_high(close: PanelLike, lookback: int = 252) -> PanelLike:
    """Distance from 52-week (252 trading day) high, expressed as fraction.

    Returns (rolling_high - close) / rolling_high. Range: [0, 1).
    """
    rolling_high = close.rolling(window=lookback, min_periods=lookback).max()
    return (rolling_high - close) / rolling_high


def _wilder_smooth(series: pd.Series, n: int) -> pd.Series:
    """Wilder's smoothing — equivalent to RMA / EMA with alpha=1/n.

    Formula:
        first n-1 values: NaN
        value at index n-1: simple sum of first n values
        thereafter: prev * (n-1)/n + curr / n
                    or equivalently: prev - prev/n + curr  (then divide by n
                    only if you started with a sum, or use ewm alpha=1/n if you
                    started with average — we go ewm because pandas does it
                    cleanly).
    """
    return series.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def _atr_series(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    n: int = 14,
) -> pd.Series:
    """Average True Range (Wilder) for a single ticker."""
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return _wilder_smooth(tr, n)


def atr(
    high: PanelLike,
    low: PanelLike,
    close: PanelLike,
    n: int = 14,
) -> PanelLike:
    """ATR with Wilder smoothing. Per-ticker if DataFrame inputs."""
    if isinstance(high, pd.Series):
        return _atr_series(high, low, close, n)

    out = {}
    for col in high.columns:
        if col not in low.columns or col not in close.columns:
            continue
        out[col] = _atr_series(high[col], low[col], close[col], n)
    return pd.DataFrame(out, index=high.index)


def _adx_series(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    n: int = 14,
) -> pd.Series:
    """ADX (Wilder) for a single ticker.

    Steps:
        1. +DM = max(high - high.shift(1), 0)  if  > -DM, else 0
           -DM = max(low.shift(1) - low, 0)    if  > +DM, else 0
        2. TR as in ATR
        3. Smooth +DM, -DM, TR with Wilder over n
        4. +DI = 100 * smoothed +DM / smoothed TR
           -DI = 100 * smoothed -DM / smoothed TR
        5. DX  = 100 * |+DI - -DI| / (+DI + -DI)
        6. ADX = Wilder-smoothed DX over n
    """
    up_move = high.diff()
    down_move = low.shift(1) - low

    plus_dm_raw = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm_raw = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    plus_dm = _wilder_smooth(plus_dm_raw, n)
    minus_dm = _wilder_smooth(minus_dm_raw, n)
    tr_smooth = _wilder_smooth(tr, n)

    # Avoid divide-by-zero
    tr_safe = tr_smooth.replace(0.0, np.nan)
    plus_di = 100.0 * (plus_dm / tr_safe)
    minus_di = 100.0 * (minus_dm / tr_safe)

    di_sum = plus_di + minus_di
    di_diff = (plus_di - minus_di).abs()
    dx = 100.0 * (di_diff / di_sum.replace(0.0, np.nan))

    return _wilder_smooth(dx, n)


def adx(
    high: PanelLike,
    low: PanelLike,
    close: PanelLike,
    n: int = 14,
) -> PanelLike:
    """ADX panel (Wilder smoothing). Per-ticker if DataFrame inputs."""
    if isinstance(high, pd.Series):
        return _adx_series(high, low, close, n)

    out = {}
    for col in high.columns:
        if col not in low.columns or col not in close.columns:
            continue
        out[col] = _adx_series(high[col], low[col], close[col], n)
    return pd.DataFrame(out, index=high.index)


if __name__ == "__main__":
    # Smoke test with synthetic data
    rng = np.random.default_rng(42)
    n_days = 300
    close_sr = pd.Series(100 * np.cumprod(1 + rng.normal(0.001, 0.02, n_days)))
    high_sr = close_sr * (1 + rng.uniform(0, 0.02, n_days))
    low_sr = close_sr * (1 - rng.uniform(0, 0.02, n_days))

    print("ROC(20):", roc(close_sr, 20).tail(3).values)
    print("SMA(200):", sma(close_sr, 200).tail(3).values)
    print("dist_52w:", dist_from_52w_high(close_sr).tail(3).values)
    a = atr(high_sr, low_sr, close_sr, 14)
    print("ATR(14):", a.tail(3).values)
    x = adx(high_sr, low_sr, close_sr, 14)
    print("ADX(14):", x.tail(3).values)
    assert ((x.dropna() >= 0) & (x.dropna() <= 100)).all(), "ADX out of [0,100]"
    print("indicators.py self-test OK")
