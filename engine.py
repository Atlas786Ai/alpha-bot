import math
import random

# -----------------------------
# MEMORY (in-memory simulation)
# -----------------------------
MEMORY = {
    "last_scores": {},
    "leader_count": {}
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

    return m, v, vol, momentum, liquidity, acceleration


# -----------------------------
# BASE SCORE
# -----------------------------
def base_score(c):

    m, v, vol, mom, liq, acc = features(c)

    return mom * 2.1 + acc * 1.9 + liq * 1.2


# -----------------------------
# TIME DELTA (learning signal)
# -----------------------------
def time_delta(symbol, score):

    last = MEMORY["last_scores"].get(symbol, score)

    delta = score - last

    MEMORY["last_scores"][symbol] = score

    return delta


# -----------------------------
# STABILITY SCORE
# -----------------------------
def stability(symbol, score):

    last = MEMORY["last_scores"].get(symbol, score)

    diff = abs(score - last)

    return max(0, 1 - diff / 50)


# -----------------------------
# LEARNING ADJUSTMENT
# -----------------------------
def learning_adjust(symbol, score):

    count = MEMORY["leader_count"].get(symbol, 0)

    penalty = count * 0.03

    return score * (1 - penalty)


# -----------------------------
# ANOMALY SCORE
# -----------------------------
def anomaly(score, mean):

    return abs(score - mean) / (mean + 1)


# -----------------------------
# CLUSTERING (V10 simplified)
# -----------------------------
def cluster(score, vol):

    if score > 70 and vol < 0.1:
        return "MOMENTUM_LEADER"
    elif score > 40:
        return "ROTATION_CORE"
    elif vol > 0.18:
        return "HIGH_RISK"
    else:
        return "MEAN_REVERSION"


# -----------------------------
# NEXT REGIME PREDICTION
# -----------------------------
def next_regime(avg, spread):

    if spread > 45:
        return "EXPLOSIVE_ROTATION"
    elif avg > 60:
        return "HIGH_BETA_TREND"
    else:
        return "CHOP_OR_ACCUMULATION"


# -----------------------------
# MAIN ENGINE V10
# -----------------------------
def run_engine():

    data = get_data()

    raw = []
    processed = []

    for c in data:

        score = base_score(c)

        score = learning_adjust(c["symbol"], score)

        raw.append(score)

    mean = sum(raw) / len(raw)
    spread = max(raw) - min(raw)

    for i, c in enumerate(data):

        score = raw[i]

        symbol = c["symbol"]

        delta = time_delta(symbol, score)

        stable = stability(symbol, score)

        if score > mean:
            MEMORY["leader_count"][symbol] = MEMORY["leader_count"].get(symbol, 0) + 1

        processed.append({
            "symbol": symbol,
            "ai_score": round(score, 2),
            "cluster": cluster(score, c["vol"]),
            "momentum_delta": round(delta, 3),
            "stability": round(stable, 3),
            "anomaly": round(anomaly(score, mean), 3)
        })

    processed = sorted(processed, key=lambda x: x["ai_score"], reverse=True)

    top = processed[:5]

    total = sum([x["ai_score"] + 1 for x in top]) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round((x["ai_score"] + 1) / total, 3)
        }
        for x in top
    ]

    leader = top[0]["symbol"]

    regime = next_regime(mean, spread)

    return {
        "model": "SOLANA_AI_V10_SELF_LEARNING",
        "regime": regime,
        "narrative": f"{leader} driving {regime} phase",
        "signals": top,
        "portfolio": portfolio,
        "market_stats": {
            "mean": round(mean, 2),
            "spread": round(spread, 2)
        },
        "memory": MEMORY
    }
