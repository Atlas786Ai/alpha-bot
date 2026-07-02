import random
import math

# ---------------------------
# FAKE BUT REALISTIC MARKET DATA
# ---------------------------
def get_data():

    # simulate real crypto market (stable + همیشه جواب می‌دهد)
    coins = [
        {"symbol": "SOL", "price_change_percentage_24h": random.uniform(-5, 10), "volume": random.uniform(1e8, 1e9), "market_cap": 8e10},
        {"symbol": "BTC", "price_change_percentage_24h": random.uniform(-3, 5), "volume": random.uniform(5e8, 2e9), "market_cap": 1e12},
        {"symbol": "ETH", "price_change_percentage_24h": random.uniform(-4, 6), "volume": random.uniform(4e8, 1.5e9), "market_cap": 5e11},
        {"symbol": "BNB", "price_change_percentage_24h": random.uniform(-3, 7), "volume": random.uniform(2e8, 8e8), "market_cap": 8e10},
        {"symbol": "XRP", "price_change_percentage_24h": random.uniform(-6, 8), "volume": random.uniform(1e8, 7e8), "market_cap": 3e10},
        {"symbol": "DOGE", "price_change_percentage_24h": random.uniform(-8, 12), "volume": random.uniform(2e8, 9e8), "market_cap": 1e10},
    ]

    return coins


def run_engine():

    data = get_data()

    signals = []

    for c in data:

        change = c["price_change_percentage_24h"]
        volume = c["volume"]
        cap = c["market_cap"]

        # ---------------- SMART SCORING ----------------
        momentum = change
        liquidity = math.log10(volume + 1)
        size = math.log10(cap + 1)

        score = momentum * 2.2 + liquidity * 1.1 + size * 0.7

        signals.append({
            "symbol": c["symbol"],
            "score": round(score, 3),
            "momentum": round(momentum, 3)
        })

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    total = sum([abs(s["score"]) + 1 for s in top10]) or 1

    portfolio = []

    for s in top10:

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round((abs(s["score"]) + 1) / total, 3)
        })

    # ---------------- REGIME ----------------
    avg = sum([s["momentum"] for s in top10]) / len(top10)

    if avg > 2:
        regime = "RISK_ON"
    elif avg < -2:
        regime = "RISK_OFF"
    else:
        regime = "NEUTRAL"

    return {
        "regime": regime,
        "source": "SIMULATED_MARKET",
        "signals": top10,
        "portfolio": portfolio
    }
