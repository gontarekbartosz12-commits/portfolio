"""BeastBot configuration — API keys, risk limits, model constants.

Showcase of clean config: all secrets via os.getenv() (nothing hardcoded),
calibrated model constants, and explicit risk limits.
"""
import os
from pathlib import Path

# ---- Paths ----
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
JOURNAL_FILE = ROOT / "journal.json"

# ---- API keys (environment only — never hardcoded) ----
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
POLYMARKET_PK = os.getenv("POLYMARKET_PK", "")    # wallet private key
POLYMARKET_ADDR = os.getenv("POLYMARKET_ADDR", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ---- Endpoints ----
POLYMARKET_GAMMA = "https://gamma-api.polymarket.com"
POLYMARKET_CLOB = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon

# ---- Market discovery ----
YT_MARKET_TAGS = ["streamer", "youtube", "mrbeast"]
MIN_MARKET_VOLUME = 50_000      # $50k min (below = illiquid)
MAX_MARKET_VOLUME = 2_000_000   # $2M max (above = too efficient)

# ---- Risk limits ----
CAPITAL_START = 100.0
BASE_BET = 5.0
MAX_EXPOSURE_PER_MARKET = 20.0
MAX_DAILY_BETS = 10
MAX_DAILY_DRAWDOWN_PCT = 0.15

# ---- Model constants ----
MIN_EDGE = 0.08                 # 8pp minimum edge to trade
MIN_HOURS_AFTER_UPLOAD = 6
MAX_HOURS_AFTER_UPLOAD = 168

# Normal-CDF sigma per horizon (hours to resolution).
# Uncertainty widens for longer horizons (Szabó & Huberman 2010).
SIGMA_BY_HORIZON_HR = {6: 0.25, 12: 0.18, 24: 0.12, 48: 0.08, 72: 0.07, 168: 0.10}

# ---- Exit rules ----
RESIDUAL_EDGE_EXIT = 0.02       # sell when remaining edge < 2pp
STOP_LOSS_PCT = 0.15            # -15% stop loss

# ---- Multi-agent (Hermes) consensus weights ----
HERMES_WEIGHTS = {
    "yt_api_live": 0.40,    # real-time view count
    "growth_curve": 0.35,   # sigmoid projection
    "historical": 0.20,     # baseline avg last 10 videos
    "social_velocity": 0.05,
}
