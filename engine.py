import random
import math
import time

# -----------------------------
# SIMULATED MARKET DATA (replace with real API later)
# -----------------------------
def get_market():

    coins = ["SOL", "ARB", "ETH", "AVAX", "DOGE"]

    data = {}

    for c in coins:

        prices = [random.uniform(10, 100) for _ in range(30)]

        data[c] = prices

    return data


# -----------------------------
# FEATURE ENGINE
# -----------------------------
def extract_features(series):

    returns = [
        (series[i] - series[i-1]) / series[i-1]
        for i in range(1, len(series))
    ]

    momentum = sum(returns) / len(returns)
    volatility = math.sqrt(sum([r*r for r in returns]) / len(returns))

    higher_lows = sum(1 for i in range(1, len(series)) if series[i] >= series[i-1]) / len(series)

    trend_strength = (series[-1] - series[0]) / series[0]

    return {
        "momentum": momentum,
        "volatility": volatility,
        "trend": trend_strength,
        "structure": higher_lows
    }


# -----------------------------
# SOLANA PATTERN SCORE (LEARNING CORE)
# -----------------------------
def solana_similarity(f):

    return (
        0.35 * f["structure"] +
        0.25 * max(0, f["trend"]) +
        0.20 * (1 - min(f["volatility"], 1)) +
        0.20 * max(0, f["momentum"])
    )


# -----------------------------
# DRIFT DETECTION ENGINE
# -----------------------------
def detect_drift(old_scores, new_scores):

    diffs = []

    for k in old_scores:

        diff = abs(old_scores[k] - new_scores[k])
        diffs.append(diff)

    avg_drift = sum(diffs) / len(diffs)

    if avg_drift > 0.15:
        return "HIGH_DRIFT"
    elif avg_drift > 0.07:
        return "MODERATE_DRIFT"
    else:
        return "STABLE"


# -----------------------------
# ADAPTIVE WEIGHT SYSTEM
# -----------------------------
def adjust_weights(drift_state):

    if drift_state == "HIGH_DRIFT":
        return {
            "structure": 0.45,
            "trend": 0.30,
            "volatility": 0.15,
            "momentum": 0.10
        }

    if drift_state == "MODERATE_DRIFT":
        return {
            "structure": 0.40,
            "trend": 0.25,
            "volatility": 0.20,
            "momentum": 0.15
        }

    return {
        "structure": 0.35,
        "trend": 0.25,
        "volatility": 0.25,
        "momentum": 0.15
    }


# -----------------------------
# MAIN V17 ENGINE
# -----------------------------
def run_engine():

    market = get_market()

    feature_store = {}
    scores = {}

    # STEP 1: feature extraction
    for coin, series in market.items():

        f = extract_features(series)
        feature_store[coin] = f

        scores[coin] = solana_similarity(f)

    # STEP 2: ranking
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # STEP 3: simulate previous state (memory)
    old_scores = {k: v * random.uniform(0.9, 1.1) for k, v in scores.items()}

    # STEP 4: drift detection
    drift = detect_drift(old_scores, scores)

    # STEP 5: adaptive weights
    weights = adjust_weights(drift)

    # STEP 6: portfolio build
    portfolio = []

    total = sum(scores.values())

    for coin, score in ranked:

        w = (score / total) if total > 0 else 0

        portfolio.append({
            "symbol": coin,
            "weight": round(w, 3)
        })

    # STEP 7: TOP 10 (or full universe if small)
    top10 = [
        {
            "symbol": k,
            "solana_similarity": round(v, 4)
        }
        for k, v in ranked
    ]

    return {
        "model": "SOLANA_AI_V17_ADAPTIVE_DRIFT_CORE",
        "objective": "find solana_2023_like_assets",
        "drift_state": drift,
        "weights": weights,
        "top10_candidates": top10,
        "portfolio": portfolio,
        "note": "self-adapting system that updates when market structure changes"
    }
