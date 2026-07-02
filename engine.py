import requests
import math

# ---------------------------
# DATA
# ---------------------------
def get_data():

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": False
        }

        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            return []

        return r.json()

    except:
        return []


# ---------------------------
# SAFE
# ---------------------------
def safe(x):
    try:
        return float(x)
    except:
        return 0.0


# ---------------------------
# CORE ENGINE (SMART)
# ---------------------------
def run_engine():

    data = get_data()

    if not data:

        return {
            "regime": "FALLBACK",
            "signals": [],
            "portfolio": []
        }

    signals = []

    for c in data:

        symbol = c.get("symbol", "").upper()

        price_change_24h = safe(c.get("price_change_percentage_24h"))
        market_cap = safe(c.get("market_cap"))
        volume = safe(c.get("total_volume"))

        # ---------------------------
        # 🧠 SMART FEATURES
        # ---------------------------

        # momentum (price movement strength)
        momentum = price_change_24h

        # volume shock (log scaled)
        volume_score = math.log10(volume + 1)

        # size normalization
        cap_score = math.log10(market_cap + 1)

        # solana-style heuristic (growth + hype + liquidity)
        score = (
            momentum * 2.0 +
            volume_score * 1.2 +
            cap_score * 0.8
        )

        signals.append({
            "symbol": symbol,
            "score": round(score, 3),
            "momentum": round(momentum, 3)
        })

    # sort by smart score
    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    # ---------------------------
    # PORTFOLIO ALLOCATION
    # ---------------------------
    total = sum([abs(s["score"]) + 1 for s in top10]) or 1

    portfolio = []

    for s in top10:

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round((abs(s["score"]) + 1) / total, 3)
        })

    # ---------------------------
    # REGIME DETECTION (SIMPLE)
    # ---------------------------

    avg_momentum = sum([s["momentum"] for s in top10]) / len(top10)

    if avg_momentum > 3:
        regime = "RISK_ON"
    elif avg_momentum < -2:
        regime = "RISK_OFF"
    else:
        regime = "NEUTRAL"

    return {
        "regime": regime,
        "signals": top10,
        "portfolio": portfolio
    }
