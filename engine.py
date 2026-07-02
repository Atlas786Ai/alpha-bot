import math
import random

# -----------------------------
# SIMULATED PRICE HISTORY (replace with real data later)
# -----------------------------
def get_history(symbol):

    base = random.uniform(10, 100)

    return [
        base * (1 + random.uniform(-0.05, 0.08)) ** i
        for i in range(30)
    ]


# -----------------------------
# SOLANA 2023 PATTERN ENGINE
# -----------------------------
def solana_pattern_score(series):

    highs = 0
    lows = 0

    for i in range(1, len(series)):

        if series[i] >= series[i-1]:
            highs += 1
        else:
            lows += 1

    higher_low_ratio = highs / len(series)

    drawdown = min(series) / max(series)

    recovery = series[-1] / min(series)

    smoothness = 1 - (sum(
        abs(series[i] - series[i-1])
        for i in range(1, len(series))
    ) / len(series)) / max(series)

    return (
        0.40 * higher_low_ratio +
        0.25 * recovery +
        0.20 * smoothness +
        0.15 * drawdown
    )


# -----------------------------
# REGIME DETECTOR (STRUCTURAL)
# -----------------------------
def regime(scores):

    avg = sum(scores) / len(scores)

    if avg > 0.75:
        return "SOLANA_ACCUMULATION_PHASE"
    elif avg > 0.55:
        return "EARLY_TREND_FORMATION"
    else:
        return "NO_STRONG_STRUCTURAL_TREND"


# -----------------------------
# MAIN ENGINE V16
# -----------------------------
def run_engine():

    universe = ["SOL", "ARB", "ETH", "AVAX", "DOGE", "OP", "MATIC", "LINK", "BTC", "BNB"]

    results = []

    for symbol in universe:

        history = get_history(symbol)

        score = solana_pattern_score(history)

        results.append({
            "symbol": symbol,
            "solana_similarity": round(score, 4),
            "trend_class": "STRUCTURAL"
        })

    # sort by similarity
    results = sorted(results, key=lambda x: x["solana_similarity"], reverse=True)

    top10 = results[:10]

    reg = regime([r["solana_similarity"] for r in top10])

    return {
        "model": "SOLANA_AI_V16_STRUCTURE_DETECTOR",
        "objective": "find solana_2023_like_assets",
        "regime": reg,
        "top10_candidates": top10,
        "note": "based on structural price trajectory, not short-term momentum"
    }
