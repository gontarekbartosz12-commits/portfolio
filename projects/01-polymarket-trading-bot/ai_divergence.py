"""
AI Divergence Scanner v1.0
Trades markets where an independent AI fair-value estimate diverges
from the live market price by >= MIN_DIVERGENCE.

PORTFOLIO NOTE: sanitised — secrets come from the environment, not the file.
    export SIMMER_KEY="..."
"""
import requests, json, time, os
from datetime import datetime

SIMMER_KEY = os.getenv("SIMMER_KEY", "")
BASE = "https://api.simmer.markets/api/sdk"
HEADERS = {"Authorization": f"Bearer {SIMMER_KEY}", "Content-Type": "application/json"}

BET_SIZE = 100          # $100 SIM per divergence trade
MIN_DIVERGENCE = 0.10   # 10% minimum divergence to act
SCAN_INTERVAL = 300     # every 5 min
traded = set()


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def get_opportunities():
    try:
        r = requests.get(f"{BASE}/markets/opportunities", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def trade(market_id, side, amount):
    try:
        r = requests.post(f"{BASE}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": side, "amount": amount, "venue": "simmer"
        }, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def scan():
    opps = get_opportunities()
    markets = opps if isinstance(opps, list) else opps.get("opportunities", opps.get("markets", []))
    log(f"=== AI DIVERGENCE SCAN === {len(markets)} opportunities")

    for m in markets:
        mid = m.get("id") or m.get("market_id", "")
        if not mid or mid in traded:
            continue
        market_price = float(m.get("current_price") or m.get("market_price", 0.5))
        ai_price = float(m.get("ai_estimate") or m.get("fair_value", 0.5))
        divergence = ai_price - market_price
        if abs(divergence) < MIN_DIVERGENCE:
            continue

        side = "yes" if divergence > 0 else "no"
        log(f"  DIVERGENCE {m.get('question','')[:55]} | mkt={market_price:.2f} ai={ai_price:.2f} -> {side.upper()}")
        result = trade(mid, side, BET_SIZE)
        traded.add(mid)
        log(f"    TRADE: {json.dumps(result)[:120]}")


def main():
    log(f"AI DIVERGENCE SCANNER v1.0 | bet ${BET_SIZE} SIM | min div {MIN_DIVERGENCE*100:.0f}%")
    while True:
        try:
            scan()
        except Exception as e:
            log(f"ERROR: {e}")
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
