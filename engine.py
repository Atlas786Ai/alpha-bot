import math
import random

# -----------------------------
# MARKET SIM (still stable, but richer)
# -----------------------------
def get_data():

    return [
        {"symbol": "SOL", "price_change": random.uniform(-2, 12), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.03, 0.15)},
        {"symbol": "ARB", "price_change": random.uniform(-1, 10), "volume": random.uniform(3e8, 1.3e9), "volatility": random.uniform(0.05, 0.2)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 9), "volume": random.uniform(4e8, 1.5e9), "volatility": random.uniform(0.04, 0.18)},
        {"symbol": "DOGE", "price_change": random.uniform(-3, 15), "volume": random.uniform(5e8, 2e9), "volatility": random.uniform(0.06, 0.25)},
        {"symbol": "ETH", "price_change": random.uniform(-2, 7), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.02, 0.08)},
        {"symbol": "BTC", "price_change": random.uniform(-1, 5), "volume": random.uniform(1e9, 3e9), "volatility": random.uniform(0.01, 0.05)},
    ]


# -----------------------------
# AI FEATURE EMBEDDING (key upgrade)
# -----------------------------
def embed(c):

    momentum = c["price_change"]
    volume = math.log10(c["volume"] + 1)
    vol = c["volatility"]

    # normalized behavioral vector
    return [
        momentum / 10,
        volume / 10,
        vol,
        momentum * vol,
        volume * vol,
        abs(momentum) * volume
    ]


# -----------------------------
# "LEARNED STYLE" WEIGHTS (simulated AI memory)
# -----------------------------
def get_dynamic_weights():

    # simulating adaptive learning (like model tuning over time)
    return {
        "w_momentum": random.uniform(1.5, 2.5),
        "w_volume": random.uniform(0.8, 1.5),
        "w_volatility": random.uniform(2.0, 3.5),
        "w_interaction": random.uniform(1.0, 2.0)
    }


# -----------------------------
# AI SCORING FUNCTION
# -----------------------------
def ai_score(c, w):

    momentum = c["price_change"]
    volume = math.log10(c["volume"] + 1)
    vol = c["volatility"]

    interaction = momentum * vol * volume

    score = (
        w["w_momentum"] * momentum +
        w["w_volume"] * volume -
        w["w_volatility"] * abs(vol - 0.08) +
        w["w_interaction"] * math.log1p(abs(interaction))
    )

    return score


# -----------------------------
# CLUSTERING (behavioral regime signal)
# -----------------------------
def detect_ai_regime(scores):

    avg = sum(scores) / len(scores)
    spread = max(scores) - min(scores)

    if avg > 8 and spread > 5:
        return "EXPLOSIVE_ROTATION"
    elif avg > 4:
        return "TRENDING_BIAS"
    elif avg > 0:
        return "EARLY_ACCUMULATION"
    else:
        return "DISTRIBUTION_PHASE"


# -----------------------------
# MAIN ENGINE
# -----------------------------
def run_engine():

    data = get_data()

    weights = get_dynamic_weights()

    signals = []
    scores = []

    for c in data:

        score = ai_score(c, weights)
        scores.append(score)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(score, 3),
            "momentum": round(c["price_change"], 3),
            "vol": round(c["volatility"], 3),
            "volume": round(math.log10(c["volume"] + 1), 3)
        })

    # ranking
    signals = sorted(signals, key=lambda x: x["ai_score"], reverse=True)

    top = signals[:5]

    total = sum([abs(s["ai_score"]) + 1 for s in top]) or 1

    # AI portfolio allocation (risk-aware + score-aware)
    portfolio = []

    for s in top:

        risk_adjust = 1 / (1 + s["vol"])

        weight = ((abs(s["ai_score"]) + 1) * risk_adjust) / total

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(weight, 3)
        })

    regime = detect_ai_regime(scores)

    leader = top[0]["symbol"]

    # AI narrative layer (important upgrade)
    narratives = {
        "EXPLOSIVE_ROTATION": f"{leader} entering high volatility expansion cycle",
        "TRENDING_BIAS": f"{leader} dominating directional flow",
        "EARLY_ACCUMULATION": f"{leader} showing accumulation structure",
        "DISTRIBUTION_PHASE": "market risk-off rotation detected"
    }

    return {
        "model": "SOLANA_AI_SIMILARITY_V3",
        "regime": regime,
        "narrative": narratives.get(regime),
        "signals": top,
        "portfolio": portfolio,
        "weights": weights
    }
