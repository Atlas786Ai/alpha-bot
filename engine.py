import math
import random

# -----------------------------
# SAFE MARKET DATA (NO FAILS)
# -----------------------------
def get_data():

    return [
        {"symbol": "DOGE", "price_change": random.uniform(-2, 15), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.05, 0.22)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 12), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.15)},
        {"symbol": "ARB", "price_change": random.uniform(-2, 10), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.04, 0.18)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 8), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.08)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 9), "volume": random.uniform(3e8, 1.2e9), "vol": random.uniform(0.03, 0.2)},
    ]


# -----------------------------
# SAFE FEATURE ENGINE
# -----------------------------
def features(c):

    momentum = c.get("price_change", 0)
    volume = math.log10(c.get("volume", 1) + 1)
    vol = c.get("vol", 0.1)

    breakout = momentum * vol * 10
    liquidity = volume * vol

    return momentum, volume, vol, breakout, liquidity


# -----------------------------
# SAFE SCORE (NO EXPLOSION)
# -----------------------------
def score(c):

    m, v, vol, b, l = features(c)

    return (
        b * 2.0 +
        l * 1.2 +
        math.log1p(abs(m)) * 1.5
    )


# -----------------------------
# REGIME (ROBUST VERSION)
# -----------------------------
def regime(scores):

    if not scores:
        return "CHOP_MARKET"

    avg = sum(scores) / len(scores)
    spread = max(scores) - min(scores)

    if avg > 6 and spread > 4:
        return "EXPLOSIVE_ROTATION"
    elif avg > 3:
        return "HIGH_BETA_TREND"
    elif avg > 1:
        return "EARLY_ACCUMULATION"
    else:
        return "CHOP_MARKET"


# -----------------------------
# CONFIDENCE (SAFE)
# -----------------------------
def confidence(vol):

    return round(1 / (1 + vol), 3)


# -----------------------------
# MAIN ENGINE (NO MEMORY DEPENDENCY → ZERO CRASH)
# -----------------------------
def run_engine():

    data = get_data()

    signals = []
    scores = []

    for c in data:

        s = score(c)
        scores.append(s)

        vol = c.get("vol", 0.1)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(s, 3),
            "momentum": round(c.get("price_change", 0), 3),
            "vol": round(vol, 3),
            "confidence": confidence(vol)
        })

    # ranking
    signals = sorted(signals, key=lambda x: x["ai_score"], reverse=True)

    top = signals[:5]

    total = sum([abs(x["ai_score"]) + 1 for x in top]) or 1

    portfolio = []

    for s in top:

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round((abs(s["ai_score"]) + 1) / total, 3)
        })

    reg = regime(scores)

    leader = top[0]["symbol"]

    narrative = f"{leader} leading flow in {reg} phase"

    return {
        "model": "SOLANA_AI_V6_STABLE",
        "regime": reg,
        "narrative": narrative,
        "signals": top,
        "portfolio": portfolio
    }
