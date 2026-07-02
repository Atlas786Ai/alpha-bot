import math
import random

# -----------------------------
# MARKET SIM
# -----------------------------
def get_data():

    return [
        {"symbol": "ARB", "price_change": random.uniform(-2, 15), "volume": random.uniform(5e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "DOGE", "price_change": random.uniform(-3, 16), "volume": random.uniform(6e8, 2e9), "vol": random.uniform(0.05, 0.22)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 14), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.02, 0.15)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 8), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.01, 0.08)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 10), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.03, 0.2)},
    ]


# -----------------------------
# FEATURE ENGINE
# -----------------------------
def features(c):

    momentum = c["price_change"]
    volume = math.log10(c["volume"] + 1)
    vol = c["vol"]

    breakout = momentum * vol * 10
    liquidity = volume * vol
    interaction = momentum * volume * vol

    return momentum, volume, vol, breakout, liquidity, interaction


# -----------------------------
# AI SCORE
# -----------------------------
def score(c):

    m, v, vol, b, l, i = features(c)

    return b * 2.2 + l * 1.3 + math.log1p(abs(i)) * 2


# -----------------------------
# CONFIDENCE MODEL (NEW)
# -----------------------------
def confidence(c):

    _, _, vol, _, _, _ = features(c)

    # lower volatility = higher confidence
    return round(1 / (1 + vol), 3)


# -----------------------------
# ANOMALY DETECTION (NEW)
# -----------------------------
def anomaly(c):

    m, _, vol, b, _, _ = features(c)

    z = abs(m * vol * 10)

    if z > 2:
        return "EXTREME"
    elif z > 1:
        return "HIGH"
    else:
        return "NORMAL"


# -----------------------------
# REGIME PROBABILITY (NEW)
# -----------------------------
def regime_probability(scores):

    avg = sum(scores) / len(scores)
    spread = max(scores) - min(scores)

    prob = {
        "EXPLOSIVE_ROTATION": 0.0,
        "HIGH_BETA_TREND": 0.0,
        "EARLY_ACCUMULATION": 0.0,
        "CHOP_MARKET": 0.0
    }

    # soft probabilistic model (not hard rules)

    prob["EXPLOSIVE_ROTATION"] = min(1.0, max(0.0, (avg + spread) / 20))
    prob["HIGH_BETA_TREND"] = min(1.0, max(0.0, avg / 12))
    prob["EARLY_ACCUMULATION"] = min(1.0, max(0.0, (10 - spread) / 10))
    prob["CHOP_MARKET"] = 1 - (prob["EXPLOSIVE_ROTATION"] + prob["HIGH_BETA_TREND"]) / 2

    # normalize
    total = sum(prob.values()) or 1
    for k in prob:
        prob[k] = round(prob[k] / total, 3)

    return prob


# -----------------------------
# MAIN ENGINE
# -----------------------------
def run_engine():

    data = get_data()

    signals = []
    scores = []

    for c in data:

        s = score(c)
        scores.append(s)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(s, 3),
            "confidence": confidence(c),
            "anomaly": anomaly(c),
            "momentum": round(c["price_change"], 3),
            "vol": round(c["vol"], 3)
        })

    signals = sorted(signals, key=lambda x: x["ai_score"], reverse=True)

    top = signals[:5]

    total = sum([abs(s["ai_score"]) + 1 for s in top]) or 1

    portfolio = [
        {
            "symbol": s["symbol"],
            "weight": round((abs(s["ai_score"]) + 1) / total, 3)
        }
        for s in top
    ]

    # regime probabilities (NEW AI layer)
    regime_probs = regime_probability(scores)

    best_regime = max(regime_probs, key=regime_probs.get)

    leader = top[0]["symbol"]

    # AI narrative (more intelligent now)
    narrative = f"{leader} leading market flow with probabilistic regime: {best_regime}"

    return {
        "model": "SOLANA_AI_PROBABILISTIC_V5",
        "regime": best_regime,
        "regime_probabilities": regime_probs,
        "narrative": narrative,
        "signals": top,
        "portfolio": portfolio
    }
