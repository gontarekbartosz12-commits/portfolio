"""
Static universe for Strategy 1 backtest.

We hardcode ~150 large-cap US names approximating top-100 S&P 500 +
top-50 NASDAQ-100 by market cap as of late 2017 / early 2018. This is
deliberately STATIC for the backtest period 2018-2026.

KNOWN BIASES:
1. Survivorship bias — yfinance only serves data for tickers that still
   exist today. Names that delisted between 2018-2026 (e.g. various energy
   names, retail) are NOT in this list because we cannot get their data.
   Real performance will be lower.
2. Look-ahead via composition — the late-2017 snapshot is partially
   informed by hindsight (we know which names survived). We mitigate by
   choosing names that were already large in 2017, not names that grew
   later. NVDA, TSLA, AMD were already $50B+ in 2017.
3. No quarterly rebalance — real S&P 500 / NDX rotate ~5-10%/yr.
   For sanity-check purposes, this approximation is acceptable; document
   when promoting to production.

Filters applied at universe load (in data_loader, after fetch):
- Average daily volume > $50M
- Price > $10

Function `get_universe(as_of)` exists for forward-compatibility but in
this backtest returns the same list regardless of date.
"""
from __future__ import annotations

from datetime import date


# Approximation of top-100 S&P 500 + top-50 NDX by market cap, late-2017.
# Deduplicated. Symbols are yfinance-compatible (BRK.B -> BRK-B).
_UNIVERSE: list[str] = [
    # Mega-cap tech (in both SP500 and NDX)
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA",
    "AVGO", "ORCL", "ADBE", "CRM", "NFLX", "CSCO", "INTC", "AMD",
    "QCOM", "TXN", "IBM", "INTU", "AMAT", "MU", "ADI", "LRCX",
    "KLAC", "MRVL", "PANW", "SNPS", "CDNS", "FTNT", "CRWD", "WDAY",
    "ADP", "PAYX", "MCHP", "ROP", "ANSS", "CTSH", "ON", "NXPI",
    # Communication / media
    "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR", "EA", "ATVI",
    # Consumer discretionary
    "HD", "MCD", "NKE", "SBUX", "TJX", "BKNG", "LOW", "TGT",
    "COST", "WMT", "DG", "ROST", "ULTA", "DLTR", "YUM", "MAR",
    "ORLY", "AZO", "GM", "F",
    # Consumer staples
    "PG", "KO", "PEP", "PM", "MO", "MDLZ", "CL", "KMB",
    "GIS", "K", "HSY", "MNST",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "ABT", "LLY",
    "DHR", "BMY", "AMGN", "GILD", "MDT", "CVS", "ELV", "CI",
    "ISRG", "VRTX", "REGN", "BIIB", "ZTS", "BSX", "SYK", "BDX",
    # Financials
    "JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "AXP",
    "SPGI", "MMC", "ICE", "CB", "PGR", "USB", "PNC", "TFC",
    "SCHW", "BRK-B",
    # Industrials
    "BA", "CAT", "DE", "HON", "UPS", "RTX", "GE", "LMT",
    "MMM", "UNP", "CSX", "NSC", "FDX", "EMR", "ETN", "ITW",
    "GD", "NOC",
    # Energy
    "XOM", "CVX", "COP", "EOG", "SLB", "OXY", "PSX", "MPC",
    "VLO", "KMI",
    # Materials
    "LIN", "APD", "FCX", "NEM", "DOW", "SHW",
    # Utilities & REIT (small slice — momentum strategy mostly avoids these but liquid)
    "NEE", "DUK", "SO", "AMT", "PLD", "EQIX", "SPG", "O",
    # Other tech / payments / fintech
    "V", "MA", "PYPL", "SQ", "FIS", "FISV",
]


def get_universe(as_of: date | None = None) -> list[str]:
    """Return the backtest universe.

    Currently returns a static late-2017 snapshot regardless of `as_of`.
    `as_of` is accepted for forward-compatibility with quarterly rebalance.

    Returns
    -------
    list[str]
        Deduplicated list of yfinance-compatible tickers.
    """
    _ = as_of  # unused; keeps signature stable
    seen: set[str] = set()
    deduped: list[str] = []
    for ticker in _UNIVERSE:
        if ticker not in seen:
            deduped.append(ticker)
            seen.add(ticker)
    return deduped


if __name__ == "__main__":
    universe = get_universe()
    print(f"Universe size: {len(universe)}")
    print(universe)
