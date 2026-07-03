import math

# =========================
# NORMALIZATION HELPERS
# =========================
def normalize(x, min_v, max_v):
    if max_v - min_v == 0:
        return 0.5
    return (x - min_v) / (max_v - min_v)


def log_scale(x):
    return math.log1p(max(x, 0))


# =========================
# CORE SCORING (REAL QUANT STYLE)
# =========================
def v33_score(asset, market_btc):

    # momentum (normalized)
    momentum = asset["change"] / 10  # scale fix

    # relative strength vs BTC (IMPORTANT FIX)
    rel_strength = asset["change"] - market_btc

    # volume (log-scaled to remove whale bias)
    volume = log_scale(asset["volume"])

    # rank (inverse importance)
    rank_score = 1 - normalize(asset["rank"], 1, 100)

    # stability penalty (prevents pump coins)
    stability = 1 / (1 + abs(momentum))

    # FINAL SCORE (balanced)
    score = (
        rel_strength * 0.35 +
        momentum * 0.20 +
        volume * 0.20 +
        rank_score * 0.15 +
        stability * 0.10
    )

    return score
