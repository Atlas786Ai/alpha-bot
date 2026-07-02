import random
import math
import time

# -----------------------------
# META MEMORY (NOT JUST HISTORY)
# -----------------------------
META_MEMORY = {
    "correct_predictions": 0,
    "wrong_predictions": 0,
    "feature_importance": {
        "momentum": 1.0,
        "volatility": 1.0,
        "structure": 1.0,
        "trend": 1.0
    },
    "strategy_bias": 0.0
}


# -----------------------------
# MARKET DATA
# -----------------------------
def get_market():

    return {
        "SOL": [random.uniform(100, 150) for _ in range(40)],
        "ARB": [random.uniform(1, 3) for _ in range(40)],
        "ETH": [random.uniform(2000, 3500) for _ in range(40)],
        "AVAX": [random.uniform(15, 45) for _ in range(40)],
        "DOGE": [random.uniform(0.08, 0.35) for _ in range(40)]
    }


# -----------------------------
# FEATURES
# -----------------------------
def features(series):

    returns = [
        (series[i] - series[i-1]) / series[i-1]
        for i in range(1, len(series))
    ]

    momentum = sum(returns) / len(returns)
    volatility = math.sqrt(sum(r*r for r in returns) / len(returns))

    structure = sum(
        1 for i in range(1, len(series))
        if series[i] >= series[i-1]
    ) / len(series)

    trend = (series[-1] - series[0]) / series[0]

    return momentum, volatility, structure, trend


# -----------------------------
# META SCORING (DYNAMIC WEIGHTS)
# -----------------------------
def score(m, v, s, t):

    f = META_MEMORY["feature_importance"]

    return (
        f["structure"] * s +
        f["trend"] * max(0, t) +
        f["volatility"] * (1 - min(v, 1)) +
        f["momentum"] * max(0, m)
    )


# -----------------------------
# SELF REPAIR SYSTEM
# -----------------------------
def self_repair(error):

    if error > 0.2:

        # penalize wrong features
        META_MEMORY["feature_importance"]["volatility"] *= 0.95
        META_MEMORY["feature_importance"]["trend"] *= 1.05

    elif error < 0.05:

        # reinforce good behavior
        META_MEMORY["feature_importance"]["structure"] *= 1.02


# -----------------------------
# STRATEGY MUTATION
# -----------------------------
def mutate_strategy():

    META_MEMORY["strategy_bias"] += random.uniform(-0.01, 0.01)

    # clamp
    META_MEMORY["strategy_bias"] = max(-1, min(1, META_MEMORY["strategy_bias"]))


# -----------------------------
# MAIN ENGINE V20
# -----------------------------
def run_engine():

    market = get_market()

    scores = {}

    for coin, series in market.items():

        m, v, s, t = features(series)

        base = score(m, v, s, t)

        adjusted = base + META_MEMORY["strategy_bias"]

        scores[coin] = adjusted

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # simulate "prediction error"
    error = random.uniform(0, 0.25)

    if error > 0.1:
        META_MEMORY["wrong_predictions"] += 1
    else:
        META_MEMORY["correct_predictions"] += 1

    # self learning loops
    self_repair(error)
    mutate_strategy()

    total = sum(scores.values())

    portfolio = [
        {
            "symbol": k,
            "weight": round(v / total, 3)
        }
        for k, v in ranked
    ]

    top10 = [
        {
            "symbol": k,
            "solana_similarity": round(v, 4)
        }
        for k, v in ranked
    ]

    return {
        "model": "SOLANA_AI_V20_META_LEARNING_CORE",
        "objective": "find solana_2023_like_assets",
        "regime": "META_ADAPTIVE",
        "top10_candidates": top10,
        "portfolio": portfolio,
        "meta_memory": {
            "correct": META_MEMORY["correct_predictions"],
            "wrong": META_MEMORY["wrong_predictions"],
            "strategy_bias": round(META_MEMORY["strategy_bias"], 4),
            "feature_importance": META_MEMORY["feature_importance"]
        },
        "note": "self-learning system with self-repair + strategy mutation"
    }
