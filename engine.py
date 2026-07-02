import math
import random

# -----------------------------
# GLOBAL MEMORY (STATEFUL)
# -----------------------------
MEMORY = {
    "last_scores": {},
    "leader_count": {},
    "performance": {},   # NEW: correctness tracking
    "strategy_weights": {
        "momentum": 2.0,
        "liquidity": 1.2,
        "volatility": 1.5
    }
}


# -----------------------------
# MARKET DATA
# -----------------------------
def get_data():

    return [
        {"symbol": "ARB", "price_change": random.uniform(-2, 20), "volume": random.uniform(6e8, 2e9), "vol": random.uniform(0.04, 0.25)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 16), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 10), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.09)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 12), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.03, 0.2)},
        {"symbol": "DOGE", "price_change": random.uniform(-4, 22), "volume": random.uniform(7e8, 2e9), "vol": random.uniform(0.05, 0.3)},
    ]


# -----------------------------
# FEATURE ENGINE
# -----------------------------
def features(c):

    m = c["price_change"]
    v = math.log10(c["volume"] + 1)
    vol = c["vol"]

    momentum = m * (1 - vol)
    liquidity = v * vol
    acceleration = m * vol * 10

    return momentum, liquidity, acceleration


# -----------------------------
# DYNAMIC SCORE (V11 CORE)
# -----------------------------
def score(c):

    mom, liq, acc = features(c)

    w = MEMORY["strategy_weights"]

    return (
        mom * w["momentum"] +
        liq * w["liquidity"] +
        acc * w["volatility"]
    )


# -----------------------------
# PERFORMANCE UPDATE (NEW)
# -----------------------------
def update_performance(symbol, predicted_leader):

    perf = MEMORY["performance"].get(symbol, {"correct": 0, "wrong": 0})

    if symbol == predicted_leader:
        perf["correct"] += 1
    else:
        perf["wrong"] += 1

    MEMORY["performance"][symbol] = perf


# -----------------------------
# CONFIDENCE CALIBRATION (NEW)
# -----------------------------
def confidence(symbol):

    perf = MEMORY["performance"].get(symbol, {"correct": 1, "wrong": 1})

    total = perf["correct"] + perf["wrong"]

    return round(perf["correct"] / total, 3)


# -----------------------------
# LEARNING UPDATE (STRATEGY EVOLUTION)
# -----------------------------
def evolve_strategy(mean, spread):

    w = MEMORY["strategy_weights"]

    # if market is volatile → momentum matters more
    if spread > 40:
        w["momentum"] *= 1.02
        w["volatility"] *= 1.03

    # if calm market → liquidity matters more
    else:
        w["liquidity"] *= 1.01

    # normalize (important)
    total = sum(w.values())

    for k in w:
        w[k] = round(w[k] / total * 3, 3)


# -----------------------------
# FILTER SIGNALS (VALIDATION LAYER)
# -----------------------------
def filter_signal(score, mean):

    return score > mean * 0.5


# -----------------------------
# NEXT REGIME
# -----------------------------
def regime(mean, spread):

    if spread > 45:
        return "EXPLOSIVE_ROTATION"
    elif mean > 60:
        return "HIGH_BETA_TREND"
    else:
        return "CHOP"


# -----------------------------
# MAIN ENGINE V11
# -----------------------------
def run_engine():

    data = get_data()

    raw = []

    for c in data:

        raw.append(score(c))

    mean = sum(raw) / len(raw)
    spread = max(raw) - min(raw)

    evolve_strategy(mean, spread)

    processed = []

    for i, c in enumerate(data):

        s = raw[i]

        symbol = c["symbol"]

        if not filter_signal(s, mean):
            continue

        processed.append({
            "symbol": symbol,
            "ai_score": round(s, 2),
            "confidence": confidence(symbol)
        })

    processed = sorted(processed, key=lambda x: x["ai_score"], reverse=True)

    leader = processed[0]["symbol"]

    # UPDATE LEARNING MEMORY
    for p in processed:
        update_performance(p["symbol"], leader)

    total = sum([x["ai_score"] + 1 for x in processed]) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round((x["ai_score"] + 1) / total, 3)
        }
        for x in processed
    ]

    return {
        "model": "SOLANA_AI_V11_SELF_EVOLVING",
        "regime": regime(mean, spread),
        "narrative": f"{leader} leading adaptive market phase",
        "signals": processed,
        "portfolio": portfolio,
        "market_stats": {
            "mean": round(mean, 2),
            "spread": round(spread, 2)
        },
        "strategy_weights": MEMORY["strategy_weights"],
        "learning_memory": MEMORY["performance"]
    }
