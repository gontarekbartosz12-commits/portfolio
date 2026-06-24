"""
Polymarket Copy Trading Bot v1.0
Mirrors NEW positions from top on-chain traders, in $SIM (paper) mode.

PORTFOLIO NOTE: this is a sanitised copy. All secrets are loaded from the
environment — there are no API keys in this file. Set them before running:
    export SIMMER_KEY="..."
"""
import requests, json, time, os
from datetime import datetime

# --- secrets via environment (never hardcode keys) ---
SIMMER_KEY = os.getenv("SIMMER_KEY", "")
BASE = "https://api.simmer.markets/api/sdk"
HEADERS = {"Authorization": f"Bearer {SIMMER_KEY}", "Content-Type": "application/json"}
CLOB = "https://clob.polymarket.com"

# Public on-chain wallets to mirror (addresses are public ledger data)
WALLETS = {
    "ColdMath": "0x594edb9112f526fa6a80b8f858a6379c8a2c1c11",
    "Sorrowful": "0xdc876e6873772d38716fda7f2452a78d426d7ab6",
    "Whale3":   "0x2a2C53bD278c04DA9962Fcf96490E17F3DfB9Bc1",
}

# Risk config
COPY_PCT = 0.02          # 2% of balance per copied trade
MIN_POSITION_VALUE = 5   # min $5 position to copy
MAX_TRADE_SIZE = 50      # max $50 per copy trade ($SIM)
SCAN_INTERVAL = 120      # check every 2 min
KNOWN_POSITIONS = {}     # {wallet: {condition_id: side}}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_balance():
    try:
        r = requests.get(f"{BASE}/portfolio", headers=HEADERS, timeout=10)
        return r.json().get("sim_balance", 0)
    except Exception:
        return 0


def fetch_wallet_positions(address):
    """Fetch active positions from the public Polymarket data API."""
    try:
        r = requests.get(
            "https://data-api.polymarket.com/positions",
            params={"user": address, "limit": 50, "sizeThreshold": "0.1"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        if r.status_code == 200 and isinstance(r.json(), list):
            return [p for p in r.json() if float(p.get("currentValue", 0)) > 0]
        return []
    except Exception as e:
        log(f"  Error fetching {address[:10]}: {e}")
        return []


def find_simmer_market(question):
    try:
        r = requests.get(f"{BASE}/markets",
                         params={"query": question[:50], "status": "active", "limit": 5},
                         headers=HEADERS, timeout=10)
        if r.status_code == 200 and r.json():
            return r.json()[0]
    except Exception:
        pass
    return None


def place_copy_trade(market_id, side, amount):
    try:
        payload = {"market_id": market_id, "side": side, "amount": amount, "venue": "simmer"}
        r = requests.post(f"{BASE}/trade", headers=HEADERS, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def scan_and_copy():
    balance = get_balance()
    log(f"=== COPY TRADING SCAN === Balance: ${balance:.2f} $SIM")

    for name, address in WALLETS.items():
        positions = fetch_wallet_positions(address)
        if not positions:
            continue

        prev = KNOWN_POSITIONS.get(name, {})
        current, new_trades = {}, []

        for pos in positions:
            cond_id = pos.get("conditionId", "")
            if not cond_id:
                continue
            value = float(pos.get("currentValue", 0))
            current[cond_id] = {"side": pos.get("outcome", ""), "value": value}
            # only act on the DELTA: a position we haven't seen before
            if cond_id not in prev and value >= MIN_POSITION_VALUE:
                new_trades.append({
                    "title": pos.get("title", "")[:60],
                    "side": pos.get("outcome", ""),
                    "value": value,
                    "cond_id": cond_id,
                })

        KNOWN_POSITIONS[name] = current

        for t in new_trades[:5]:
            copy_amount = min(balance * COPY_PCT, MAX_TRADE_SIZE)
            market = find_simmer_market(t["title"])
            if market:
                mid = market.get("id") or market.get("market_id")
                result = place_copy_trade(mid, t["side"], copy_amount)
                log(f"    COPY ${copy_amount:.2f} {t['side']} -> {json.dumps(result)[:100]}")


def main():
    log("POLYMARKET COPY TRADING BOT v1.0 | mode: $SIM (paper)")
    scan_and_copy()  # build baseline first
    while True:
        time.sleep(SCAN_INTERVAL)
        try:
            scan_and_copy()
        except Exception as e:
            log(f"ERROR: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
