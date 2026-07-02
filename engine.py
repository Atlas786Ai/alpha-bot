import math
import random

# -----------------------------
# SIMULATED MARKET (stable base)
# -----------------------------
def get_data():

    return [
        {"symbol": "SOL", "price_change": random.uniform(2, 12), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.03, 0.12)},
        {"symbol": "AVAX", "price_change": random.uniform(1, 10), "volume": random.uniform(4e8, 1.2e9), "volatility": random.uniform(0.04, 0.15)},
        {"symbol": "ARB", "price_change": random.uniform(0, 9), "volume": random.uniform(3e8, 1e9), "volatility": random.uniform(0.05, 0.18)},
        {"symbol": "BTC", "price_change": random.uniform(-1, 5), "volume": random.uniform(1e9, 3e9), "volatility": random.uniform(0.01, 0.04)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 6), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.02, 0.06)},
        {"symbol": "DOGE", "price_change": random.uniform(-3, 15), "volume": random.uniform(5e8, 1.5e9), "volatility": random.uniform(0.06, 0.2)},
    ]


# -----------------------------
# SOLANA 2023 BEHAVIOR MODEL
# -----------------------------
def solana_similarity_score(c):

    # core features
    momentum = c["price_change"]
    volume = math.log10(c["volume"] + 1)
    volatility = c["volatility"]

    # -----------------------------
    # "Solana-like behavior traits"
    # -----------------------------

    # 1. breakout strength (momentum spike)
    breakout = momentum * volatility * 10

    # 2. liquidity expansion (volume growth)
    liquidity_expansion = volume * volatility

    # 3. hype factor (non-linear acceleration)
    hype = math.sqrt(abs(momentum)) * volume

    # 4. stability penalty (SOL-like early stage is unstable)
    stability_penalty = -abs(volatility - 0.08) * 5

    # final similarity score
    score = (
        breakout * 2.5 +
        liquidity_expansion * 1.2 +
        math.log1p(hype) +
        stability_penalty
    )

    return score


# -----------------------------
# ENGINE
# -----------------------------
def run_engine():

    data = get_data()

    signals = []

    for c in data:

        score = solana_similarity_score(c)

        signals.append({
            "symbol": c["symbol"],
            "sol_similarity": round(score, 3),
            "momentum": round(c["price_change"], 3),
            "volatility": round(c["volatility"], 3)
        })

    # rank by similarity
    signals = sorted(signals, key=lambda x: x["sol_similarity"], reverse=True)

    top = signals[:5]

    total = sum([abs(s["sol_similarity"]) + 1 for s in top]) or 1

    portfolio = [
        {
            "symbol": s["symbol"],
            "weight": round((abs(s["sol_similarity"]) + 1) / total, 3)
        }
        for s in top
    ]

    # regime detection (behavioral)
    avg_sim = sum([s["sol_similarity"] for s in top]) / len(top)

    if avg_sim > 50:
        regime = "SOLANA_BREAKOUT_LIKE"
    elif avg_sim > 20:
        regime = "HIGH_GROWTH_PHASE"
    else:
        regime = "NORMAL_MARKET"

    return {
        "regime": regime,
        "model": "SOLANA_2023_SIMILARITY_V1",
        "signals": top,
        "portfolio": portfolio
    }
