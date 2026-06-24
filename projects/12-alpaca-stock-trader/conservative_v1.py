"""
Conservative Multi-Asset Strategy (ConservativeV1)
===================================================
Author: Backend Architect, 2026-05-14
License: Internal use only (gonta / ghostshell VPS)

Strategy logic:
  Universe:
    SPY  - S&P 500 ETF (equity, stock-hours)
    QQQ  - Nasdaq-100 ETF (equity, stock-hours)
    BTC/USD - Bitcoin (crypto, 24/7)
    ETH/USD - Ethereum (crypto, 24/7)

  Entry (long-only):
    1. Trend filter:    SMA(50) > SMA(200)         (only buy uptrends)
    2. Mean reversion:  RSI(14) < 30                (oversold)
    3. Bollinger touch: close < BB_lower(20, 2.0)   (statistical extreme)
    4. Free slot:       open_positions < max_concurrent

  Position sizing:
    notional = portfolio_value * 0.05   (5% per trade)
    qty       = floor(notional / price)  (whole shares for equity, fractional for crypto)

  Exits (any-of):
    a. Stop loss:     pnl_pct <= -0.03
    b. Take profit:   pnl_pct >= +0.02
    c. RSI overbought: RSI(14) > 70
    d. Time stop:     held_days >= 7

  Cadence: every 1H during market hours (24/7 effective due to crypto)

Why this is conservative:
  - Slope filter (SMA50>SMA200) blocks falling-knife mean-reversion
  - 5% sizing means a single -3% stop only costs -0.15% of bankroll
  - Max 4 concurrent positions caps max exposure at 20%
  - Time stop kills bag-holding (7-day max hold)
  - Multi-asset reduces single-name risk

Logging:
  Every signal -> /root/lumibot-alpaca/journal/alpaca_journal.jsonl
  Every order  -> Telegram alert via Swistak bot

Safety:
  - Paper mode hard-coded ON in main.py (PAPER=True)
  - Never reads ALPACA_LIVE_* endpoints
  - Honors max_concurrent cap before submitting orders
"""

from __future__ import annotations

import json
import logging
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

try:
    import pandas_ta as ta
except ImportError as e:
    raise RuntimeError(
        "pandas_ta missing - run: pip install pandas-ta==0.3.14b0"
    ) from e

from lumibot.entities import Asset, Order
from lumibot.strategies.strategy import Strategy

LOG = logging.getLogger("ConservativeV1")

JOURNAL_PATH = Path(
    os.environ.get(
        "ALPACA_JOURNAL_PATH",
        "/root/lumibot-alpaca/journal/alpaca_journal.jsonl",
    )
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _journal(event: dict[str, Any]) -> None:
    """Append a single JSON line to the journal. Never raises."""
    try:
        JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": _now_iso(), **event}
        with JOURNAL_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
    except Exception as exc:  # noqa: BLE001
        LOG.warning("journal write failed: %s", exc)


class ConservativeV1(Strategy):
    """Conservative multi-asset mean-reversion in confirmed uptrends."""

    # Lumibot picks up the dict and exposes it via self.parameters
    parameters: dict[str, Any] = {
        "assets": [
            ("SPY", "stock"),
            ("QQQ", "stock"),
            ("BTC", "crypto"),
            ("ETH", "crypto"),
        ],
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "bb_period": 20,
        "bb_std": 2.0,
        "sma_fast": 50,
        "sma_slow": 200,
        "position_size_pct": 0.05,
        "stop_loss_pct": -0.03,
        "take_profit_pct": 0.02,
        "max_concurrent": 4,
        "hold_timeout_days": 7,
        "lookback_days": 260,  # ~13 months of trading days for SMA200 headroom
        "sleeptime": "1H",
    }

    # -------------------------------------------------------------- lifecycle

    def initialize(self) -> None:
        self.sleeptime = self.parameters["sleeptime"]
        self.set_market("24/7")  # crypto extends past equity hours; broker skips closed assets
        # Track entry metadata that Lumibot's Position object does not natively store
        self._entry_meta: dict[str, dict[str, Any]] = {}
        _journal(
            {
                "event": "initialize",
                "params": {
                    k: v
                    for k, v in self.parameters.items()
                    if k != "assets"
                },
                "assets": [a[0] for a in self.parameters["assets"]],
            }
        )
        LOG.info("ConservativeV1 initialized with %d assets", len(self.parameters["assets"]))

    def before_starting_trading(self) -> None:
        # Telegram alert for service start
        self._notify(
            "ConservativeV1 service started\n"
            f"Mode: {'PAPER' if self.is_backtesting is False and self.broker.is_paper else 'BACKTEST/UNKNOWN'}\n"
            f"Cash: ${self.get_cash():,.2f}\n"
            f"Portfolio: ${self.get_portfolio_value():,.2f}\n"
            f"Assets: {', '.join(a[0] for a in self.parameters['assets'])}"
        )

    # -------------------------------------------------------------- core loop

    def on_trading_iteration(self) -> None:
        portfolio_value = self.get_portfolio_value()
        cash = self.get_cash()
        max_concurrent = int(self.parameters["max_concurrent"])

        positions = self.get_positions()
        open_symbols = {p.asset.symbol for p in positions if p.quantity != 0}

        _journal(
            {
                "event": "tick",
                "portfolio_value": portfolio_value,
                "cash": cash,
                "open_positions": list(open_symbols),
            }
        )

        # 1) Manage existing positions (exits)
        for pos in positions:
            if pos.quantity == 0:
                continue
            try:
                self._check_exits(pos)
            except Exception as exc:  # noqa: BLE001
                LOG.exception("exit check failed for %s: %s", pos.asset.symbol, exc)

        # Refresh after potential exits
        open_symbols = {
            p.asset.symbol for p in self.get_positions() if p.quantity != 0
        }
        free_slots = max_concurrent - len(open_symbols)
        if free_slots <= 0:
            return

        # 2) Scan for entries
        for symbol, asset_type in self.parameters["assets"]:
            if symbol in open_symbols:
                continue
            if free_slots <= 0:
                break
            try:
                if self._maybe_enter(symbol, asset_type, portfolio_value):
                    free_slots -= 1
            except Exception as exc:  # noqa: BLE001
                LOG.exception("entry check failed for %s: %s", symbol, exc)

    # -------------------------------------------------------------- entries

    def _maybe_enter(self, symbol: str, asset_type: str, portfolio_value: float) -> bool:
        asset = self._asset(symbol, asset_type)
        bars = self._fetch_bars(asset)
        if bars is None or len(bars) < self.parameters["sma_slow"] + 5:
            _journal({"event": "entry_skip", "symbol": symbol, "reason": "insufficient_history"})
            return False

        close = bars["close"]
        last_close = float(close.iloc[-1])

        rsi = ta.rsi(close, length=self.parameters["rsi_period"])
        bb = ta.bbands(close, length=self.parameters["bb_period"], std=self.parameters["bb_std"])
        if rsi is None or bb is None or bb.empty:
            _journal({"event": "entry_skip", "symbol": symbol, "reason": "indicator_nan"})
            return False

        last_rsi = float(rsi.iloc[-1])
        # pandas_ta bbands columns: BBL_<len>_<std>, BBM_..., BBU_..., BBB_..., BBP_...
        bb_lower_col = [c for c in bb.columns if c.startswith("BBL_")][0]
        last_bb_lower = float(bb[bb_lower_col].iloc[-1])

        sma_fast = close.rolling(self.parameters["sma_fast"]).mean().iloc[-1]
        sma_slow = close.rolling(self.parameters["sma_slow"]).mean().iloc[-1]

        signals = {
            "trend_up": bool(sma_fast > sma_slow),
            "oversold": bool(last_rsi < self.parameters["rsi_oversold"]),
            "bb_touch": bool(last_close < last_bb_lower),
        }
        signal_fired = all(signals.values())

        _journal(
            {
                "event": "entry_eval",
                "symbol": symbol,
                "close": last_close,
                "rsi": last_rsi,
                "bb_lower": last_bb_lower,
                "sma_fast": float(sma_fast),
                "sma_slow": float(sma_slow),
                "signals": signals,
                "fire": signal_fired,
            }
        )
        if not signal_fired:
            return False

        # Sizing
        notional = portfolio_value * float(self.parameters["position_size_pct"])
        if asset_type == "crypto":
            qty = round(notional / last_close, 6)
        else:
            qty = math.floor(notional / last_close)
        if qty <= 0:
            _journal({"event": "entry_skip", "symbol": symbol, "reason": "qty_zero", "notional": notional})
            return False

        order = self.create_order(asset, qty, "buy")
        submitted = self.submit_order(order)
        if submitted is None:
            return False

        self._entry_meta[symbol] = {
            "entry_price": last_close,
            "entry_ts": _now_iso(),
            "qty": qty,
            "asset_type": asset_type,
        }
        _journal(
            {
                "event": "order_submitted",
                "symbol": symbol,
                "side": "buy",
                "qty": qty,
                "entry_price": last_close,
                "notional": qty * last_close,
            }
        )
        self._notify(
            "ALPACA PAPER BUY\n"
            f"  Asset: {symbol}\n"
            f"  Qty:   {qty}\n"
            f"  Price: ${last_close:,.2f}\n"
            f"  Notional: ${qty * last_close:,.2f}\n"
            f"  Cash left: ${self.get_cash():,.2f}\n"
            f"  Strategy: ConservativeV1\n"
            f"  See: https://app.alpaca.markets/dashboard/overview"
        )
        return True

    # -------------------------------------------------------------- exits

    def _check_exits(self, pos) -> None:
        symbol = pos.asset.symbol
        meta = self._entry_meta.get(symbol)
        last_price = float(self.get_last_price(pos.asset) or 0.0)
        if last_price <= 0:
            return

        entry_price = float(meta["entry_price"]) if meta else float(pos.avg_fill_price or last_price)
        pnl_pct = (last_price - entry_price) / entry_price if entry_price else 0.0

        # RSI for exit
        bars = self._fetch_bars(pos.asset)
        rsi_value = None
        if bars is not None and len(bars) > self.parameters["rsi_period"] + 1:
            rsi_series = ta.rsi(bars["close"], length=self.parameters["rsi_period"])
            if rsi_series is not None and not rsi_series.empty:
                rsi_value = float(rsi_series.iloc[-1])

        held_days = 0.0
        if meta and "entry_ts" in meta:
            entry_ts = datetime.fromisoformat(meta["entry_ts"])
            held_days = (datetime.now(timezone.utc) - entry_ts).total_seconds() / 86400.0

        reasons: list[str] = []
        if pnl_pct <= float(self.parameters["stop_loss_pct"]):
            reasons.append("stop_loss")
        if pnl_pct >= float(self.parameters["take_profit_pct"]):
            reasons.append("take_profit")
        if rsi_value is not None and rsi_value >= float(self.parameters["rsi_overbought"]):
            reasons.append("rsi_overbought")
        if held_days >= float(self.parameters["hold_timeout_days"]):
            reasons.append("time_stop")

        _journal(
            {
                "event": "exit_eval",
                "symbol": symbol,
                "last": last_price,
                "entry": entry_price,
                "pnl_pct": pnl_pct,
                "rsi": rsi_value,
                "held_days": round(held_days, 3),
                "reasons": reasons,
            }
        )
        if not reasons:
            return

        # Close full position
        qty = abs(float(pos.quantity))
        order = self.create_order(pos.asset, qty, "sell")
        self.submit_order(order)
        self._entry_meta.pop(symbol, None)
        _journal(
            {
                "event": "order_submitted",
                "symbol": symbol,
                "side": "sell",
                "qty": qty,
                "exit_price": last_price,
                "pnl_pct": pnl_pct,
                "reasons": reasons,
            }
        )
        self._notify(
            "ALPACA PAPER SELL\n"
            f"  Asset: {symbol}\n"
            f"  Qty:   {qty}\n"
            f"  Exit price: ${last_price:,.2f}\n"
            f"  Entry: ${entry_price:,.2f}\n"
            f"  PnL: {pnl_pct * 100:+.2f}%\n"
            f"  Reasons: {', '.join(reasons)}\n"
            f"  Held: {held_days:.2f} days"
        )

    # -------------------------------------------------------------- helpers

    def _asset(self, symbol: str, asset_type: str) -> Asset:
        if asset_type == "crypto":
            return Asset(symbol=symbol, asset_type=Asset.AssetType.CRYPTO)
        return Asset(symbol=symbol, asset_type=Asset.AssetType.STOCK)

    def _fetch_bars(self, asset: Asset) -> Optional[pd.DataFrame]:
        try:
            bars = self.get_historical_prices(
                asset,
                length=int(self.parameters["lookback_days"]),
                timestep="day",
            )
            if bars is None:
                return None
            df = bars.df
            if df is None or df.empty:
                return None
            return df.rename(columns=str.lower)
        except Exception as exc:  # noqa: BLE001
            LOG.warning("fetch_bars failed for %s: %s", asset.symbol, exc)
            return None

    def _notify(self, text: str) -> None:
        """Telegram alert via Swistak bot. Never raises."""
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat:
            return
        try:
            import requests

            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat, "text": text, "disable_web_page_preview": True},
                timeout=8,
            )
        except Exception as exc:  # noqa: BLE001
            LOG.warning("telegram notify failed: %s", exc)
