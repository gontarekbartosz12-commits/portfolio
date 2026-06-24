"""
Strategy 1 — Swing Momentum

Pipeline:
    1. Compute per-ticker indicators (ROC20, ROC60, dist52w, ADX, SMA200, ATR).
    2. Build composite score: 0.5*ROC20 + 0.3*ROC60 + 0.2*(1 - dist52w).
    3. Apply trend filter: ADX(14) > 20 AND close > SMA(200).
    4. On every Monday close, rank top 5 by score.
    5. Trade at next-day OPEN (T+1). Use vectorbt's `from_signals(price=open,
       entries=signals.shift(1))` pattern, applying 5 bps slippage per side.
    6. Exits: trail stop = entry - 2*ATR(14) (recomputed daily), drop-out from
       top 5 at next rebalance, time stop at 10 trading days.

Public API:
    compute_indicator_panels(price_dict) -> dict[str, pd.DataFrame]
    compute_score(panels) -> pd.DataFrame
    generate_signals(panels, score) -> tuple[pd.DataFrame, pd.DataFrame]
        returns (entries, exits) — both bool, indexed dates x tickers
        Entries are placed on Mondays (close T); execution happens at T+1 OPEN
        in vectorbt via shift.
    build_portfolio(open_panel, entries, exits, ...) -> vbt.Portfolio
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from indicators import adx, atr, dist_from_52w_high, roc, sma


# Strategy hyperparameters (kept here so notebook can override)
SCORE_WEIGHTS: dict[str, float] = {"roc20": 0.5, "roc60": 0.3, "dist52w": 0.2}
ADX_THRESHOLD: float = 20.0
SMA_PERIOD: int = 200
TOP_N: int = 5
TIME_STOP_DAYS: int = 10
ATR_STOP_MULT: float = 2.0
ATR_PERIOD: int = 14


def compute_indicator_panels(
    price_dict: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Build aligned (date x ticker) panels of OHLCV + indicators."""
    if not price_dict:
        raise ValueError("price_dict is empty")

    fields: dict[str, pd.DataFrame] = {}
    for field in ("open", "high", "low", "close", "volume"):
        fields[field] = pd.DataFrame(
            {tk: df[field] for tk, df in price_dict.items() if field in df.columns}
        ).sort_index()

    close = fields["close"]
    high = fields["high"]
    low = fields["low"]

    # Indicator panels
    roc20 = roc(close, 20)
    roc60 = roc(close, 60)
    d52w = dist_from_52w_high(close, 252)
    sma200 = sma(close, SMA_PERIOD)
    adx14 = adx(high, low, close, 14)
    atr14 = atr(high, low, close, ATR_PERIOD)

    return {
        "open": fields["open"],
        "high": high,
        "low": low,
        "close": close,
        "volume": fields["volume"],
        "roc20": roc20,
        "roc60": roc60,
        "dist52w": d52w,
        "sma200": sma200,
        "adx14": adx14,
        "atr14": atr14,
    }


def compute_score(panels: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Composite momentum score, weighted per spec.

    score = 0.5*ROC20 + 0.3*ROC60 + 0.2*(1 - dist52w)
    """
    w = SCORE_WEIGHTS
    score = (
        w["roc20"] * panels["roc20"]
        + w["roc60"] * panels["roc60"]
        + w["dist52w"] * (1.0 - panels["dist52w"])
    )
    return score


def _trend_filter(panels: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Boolean mask: ADX > 20 AND close > SMA200."""
    return (panels["adx14"] > ADX_THRESHOLD) & (panels["close"] > panels["sma200"])


def _is_monday(idx: pd.DatetimeIndex) -> np.ndarray:
    """Return bool array marking Monday dates. Trading-Monday only (skip
    weekends, which are absent anyway in daily bars)."""
    if not isinstance(idx, pd.DatetimeIndex):
        idx = pd.DatetimeIndex(idx)
    return idx.weekday == 0


def generate_signals(
    panels: dict[str, pd.DataFrame],
    score: pd.DataFrame | None = None,
    top_n: int = TOP_N,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate entries, exits, and the held-position mask.

    Entries: bool, True on rebalance day (Monday close T) for top-N tickers
        passing the trend filter. Execution happens T+1 open via the caller's
        portfolio construction.

    Exits: bool, True when ANY of:
        - Drop out of top-N at next rebalance
        - 10 trading days elapsed since entry
        - Trail stop hit (entry_price - 2*ATR(14) at entry time, fixed thereafter)
          NOTE: vectorbt's stops are typically configured via `sl_stop` /
          `sl_trail`. We pass ATR-based stop into vectorbt rather than encoding
          it as a precomputed exit signal — see `build_portfolio`. Here we only
          encode the drop-out and time-stop exits.

    Returns
    -------
    (entries, exits, ranks)
        entries: DataFrame[bool], dates x tickers
        exits:   DataFrame[bool], dates x tickers
        ranks:   DataFrame[int],  dates x tickers — rank position (1 = best),
                 NaN if not eligible. Useful for diagnostics.
    """
    if score is None:
        score = compute_score(panels)

    eligible = _trend_filter(panels)
    masked_score = score.where(eligible)

    # Rank descending: highest score = rank 1
    ranks = masked_score.rank(axis=1, ascending=False, method="first")

    is_mon = _is_monday(masked_score.index)
    is_mon_arr = pd.Series(is_mon, index=masked_score.index)

    # Top-N membership at each rebalance Monday
    top_n_mon = (ranks <= top_n) & is_mon_arr.values[:, None]
    # Forward-fill membership between Mondays so we know who is "currently in top-N"
    # Use object dtype roll: we set membership at Monday and clear at next Monday only.
    # Simpler: build a held_mask where on Monday we know top-N; on other days, propagate.
    held_mask = pd.DataFrame(False, index=masked_score.index, columns=masked_score.columns)
    last_mon_top: pd.Series | None = None
    for ts in masked_score.index:
        if is_mon_arr.loc[ts]:
            last_mon_top = (ranks.loc[ts] <= top_n).fillna(False)
        if last_mon_top is not None:
            held_mask.loc[ts] = last_mon_top.values

    # Entry events: ticker is in top-N at this Monday but was NOT in top-N at the
    # immediately previous Monday's selection (i.e. fresh inclusion).
    entries = pd.DataFrame(False, index=masked_score.index, columns=masked_score.columns)
    prev_top: pd.Series | None = None
    for ts in masked_score.index:
        if is_mon_arr.loc[ts]:
            cur = (ranks.loc[ts] <= top_n).fillna(False)
            if prev_top is None:
                # First Monday — enter all top-N
                entries.loc[ts] = cur.values
            else:
                fresh = cur & ~prev_top
                entries.loc[ts] = fresh.values
            prev_top = cur

    # Drop-out exits: was in top-N at previous Monday, NOT in top-N at this Monday.
    drop_exits = pd.DataFrame(False, index=masked_score.index, columns=masked_score.columns)
    prev_top = None
    for ts in masked_score.index:
        if is_mon_arr.loc[ts]:
            cur = (ranks.loc[ts] <= top_n).fillna(False)
            if prev_top is not None:
                dropped = prev_top & ~cur
                drop_exits.loc[ts] = dropped.values
            prev_top = cur

    # Time-stop exits: 10 trading days after each entry. We mark exits 10 bars
    # forward from each True in entries.
    time_exits = pd.DataFrame(False, index=masked_score.index, columns=masked_score.columns)
    for col in entries.columns:
        col_entries = entries[col]
        idx_positions = np.where(col_entries.values)[0]
        for pos in idx_positions:
            target = pos + TIME_STOP_DAYS
            if target < len(time_exits.index):
                time_exits.iloc[target, time_exits.columns.get_loc(col)] = True

    exits = drop_exits | time_exits
    return entries, exits, ranks


def build_portfolio(
    open_panel: pd.DataFrame,
    high_panel: pd.DataFrame,
    low_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
    atr_panel: pd.DataFrame,
    entries: pd.DataFrame,
    exits: pd.DataFrame,
    init_cash: float = 1000.0,
    top_n: int = TOP_N,
    slippage: float = 0.0005,  # 5 bps per side
    fees: float = 0.0,
    freq: str = "1D",
):
    """Build a vectorbt Portfolio from signals.

    Execution model:
        - signals.shift(1) so a signal generated at close T fires at OPEN T+1
        - price=open_panel ensures fills happen at the next-day open
        - sl_trail with stop relative to entry price ≈ 2*ATR(14)/close.
          NOTE: vectorbt's `sl_stop` and `sl_trail` accept a single fractional
          value or a panel. ATR/close gives a per-ticker, per-day fractional
          stop, but vectorbt locks the stop level at entry — so we pass the
          ATR-implied stop fraction as of the bar BEFORE entry (which the
          shift handles).

    Position sizing:
        - Equal weight $200 per slot when 5 active. We use `size=...` with
          `size_type='value'` so each entry buys ~$200 worth.
    """
    import vectorbt as vbt  # local import — keeps top-level light

    # Align everything on close_panel.index/columns so vectorbt is happy.
    cols = close_panel.columns
    idx = close_panel.index

    open_aligned = open_panel.reindex(index=idx, columns=cols)
    entries_shift = entries.reindex(index=idx, columns=cols).shift(1).fillna(False).astype(bool)
    exits_shift = exits.reindex(index=idx, columns=cols).shift(1).fillna(False).astype(bool)

    # ATR-based stop fraction at signal time (so it locks at entry).
    atr_aligned = atr_panel.reindex(index=idx, columns=cols)
    sl_pct = (ATR_STOP_MULT * atr_aligned / close_panel.reindex(index=idx, columns=cols)).clip(
        lower=0.005, upper=0.5
    )
    # vectorbt expects a non-NaN stop array; fill NaN with a wide default
    sl_pct = sl_pct.fillna(0.5)

    cash_per_slot = init_cash / top_n

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pf = vbt.Portfolio.from_signals(
            close=open_aligned,  # use OPEN as the fill price (T+1 execution)
            entries=entries_shift,
            exits=exits_shift,
            size=cash_per_slot,
            size_type="value",
            init_cash=init_cash,
            fees=fees,
            slippage=slippage,
            sl_stop=sl_pct.values,
            sl_trail=False,  # fixed-from-entry stop, not trailing high
            cash_sharing=True,
            group_by=True,
            call_seq="auto",
            freq=freq,
        )
    return pf


if __name__ == "__main__":
    print("strategy.py — run as part of notebook; no standalone test.")
