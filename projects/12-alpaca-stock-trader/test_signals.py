"""
Pure-logic unit tests for the ConservativeV1 signal stack.

These tests do NOT require Lumibot installed; they synthesize price series and
exercise the indicator math via pandas_ta directly. Use this to gate the
signal logic before paying the cost of a backtest run.

Usage:
  cd /root/lumibot-alpaca && venv/bin/python -m pytest tests/test_signals.py -v
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pandas_ta as ta
import pytest


def _bars(prices: list[float]) -> pd.Series:
    return pd.Series(prices, dtype=float)


def _entry_fires(close: pd.Series) -> dict:
    rsi = ta.rsi(close, length=14)
    bb = ta.bbands(close, length=20, std=2.0)
    sma_fast = close.rolling(50).mean().iloc[-1]
    sma_slow = close.rolling(200).mean().iloc[-1]
    bb_lower_col = [c for c in bb.columns if c.startswith("BBL_")][0]
    return {
        "trend_up": bool(sma_fast > sma_slow),
        "oversold": bool(rsi.iloc[-1] < 30),
        "bb_touch": bool(close.iloc[-1] < bb[bb_lower_col].iloc[-1]),
        "rsi": float(rsi.iloc[-1]),
        "bb_lower": float(bb[bb_lower_col].iloc[-1]),
        "close": float(close.iloc[-1]),
    }


def test_uptrend_with_pullback_fires_entry():
    rng = np.random.default_rng(42)
    # Build a 250-bar uptrend (linear+noise), then a sharp 8-bar dip
    base = np.linspace(100, 200, 250) + rng.normal(0, 1.5, 250)
    dip = np.linspace(base[-1], base[-1] * 0.93, 8)
    prices = np.concatenate([base, dip])
    out = _entry_fires(_bars(prices.tolist()))
    assert out["trend_up"] is True, "uptrend filter should be True"
    assert out["oversold"] is True, f"RSI should be <30 after dip (got {out['rsi']:.1f})"
    assert out["bb_touch"] is True, "close should be below BB lower after dip"


def test_downtrend_blocks_entry():
    rng = np.random.default_rng(7)
    base = np.linspace(200, 100, 250) + rng.normal(0, 1.5, 250)
    dip = np.linspace(base[-1], base[-1] * 0.93, 8)
    prices = np.concatenate([base, dip])
    out = _entry_fires(_bars(prices.tolist()))
    assert out["trend_up"] is False, "downtrend must block entry"


def test_sideways_no_dip_no_entry():
    rng = np.random.default_rng(11)
    prices = 150 + rng.normal(0, 1.0, 260)
    out = _entry_fires(_bars(prices.tolist()))
    # No sharp dip -> not oversold AND likely not below BB lower
    assert not (out["oversold"] and out["bb_touch"]), "sideways noise must not fire entry"


def test_pnl_thresholds():
    # Sanity on entry/exit math
    entry = 100.0
    stop = -0.03
    tp = 0.02
    assert (97.0 - entry) / entry <= stop
    assert (102.0 - entry) / entry >= tp
    assert (99.0 - entry) / entry > stop  # midfield does not trigger
    assert (101.5 - entry) / entry < tp


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
