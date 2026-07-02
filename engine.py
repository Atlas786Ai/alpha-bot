import math
import random

# -----------------------------
# MARKET DATA
# -----------------------------
def get_data():

    return [
        {"symbol": "DOGE", "price_change": random.uniform(-2, 18), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.05, 0.25)},
        {"symbol": "ARB", "price_change": random.uniform(-1, 15), "volume": random.uniform(6e8, 2e9), "vol": random.uniform(0.04, 0.2)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 14), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.15)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 9), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.08)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 10), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.03, 0.2)},
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
# RAW SCORE
# -----------------------------
def raw_score(c):

    m, v, vol, mom, liq, acc = features(c)

    return mom * 2.0 + acc * 1.8 + liq * 1.2


# -----------------------------
# NORMALIZATION (0–100)
# -----------------------------
def normalize(scores):

    min_s = min(scores)
    max_s = max(scores)
    rng = max_s - min_s or 1

    return [((s - min_s) / rng) * 100 for s in scores]


# -----------------------------
# CLUSTERING (SIMULATED)
# -----------------------------
def cluster(symbol, score, vol):

    if score > 70 and vol < 0.1:
        return "MOMENTUM_LEADER"
    elif score > 40:
        return "TREND_FOLLOW"
    elif vol > 0.15:
        return "HIGH_RISK"
    else:
        return "MEAN_REVERSION"


# -----------------------------
# ANOMALY SCORE (TRUE Z-LIKE)
# -----------------------------
def anomaly(score, mean):

    return abs(score - mean) / (mean + 1)


# -----------------------------
# REGIME STRUCTURE
# -----------------------------
def market_structure(avg, spread):

    if spread > 40 and avg > 60:
        return "EXPANSION"
    elif spread > 30:
        return "ROTATION"
    else:
        return "CHOP"


# -----------------------------
# NEXT MOVE PROBABILITY
# -----------------------------
def forward_bias(score):

    if score > 70:
        return {"continue": 0.72, "reverse": 0.18}
    elif score > 40:
        return {"continue": 0.55, "reverse": 0.35}
    else:
        return {"continue": 0.38, "reverse": 0.52}


# -----------------------------
# MAIN ENGINE V9
# -----------------------------
def run_engine():

    data = get_data()

    raw = []
    signals = []

    for c in data:

        s = raw_score(c)
        raw.append(s)

    norm = normalize(raw)
    mean = sum(norm) / len(norm)

    for i, c in enumerate(data):

        cluster_type = cluster(c["symbol"], norm[i], c["vol"])
        anom = anomaly(norm[i], mean)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(norm[i], 2),
            "cluster": cluster_type,
            "anomaly_score": round(anom, 3),
            "forward_bias": forward_bias(norm[i])
        })

    signals = sorted(signals, key=lambda x: x["ai_score"], reverse=True)

    top = signals[:5]

    total = sum([s["ai_score"] + 1 for s in top]) or 1

    portfolio = [
        {
            "symbol": s["symbol"],
            "weight": round((s["ai_score"] + 1) / total, 3)
        }
        for s in top
    ]

    avg = sum([s["ai_score"] for s in signals]) / len(signals)
    spread = max([s["ai_score"] for s in signals]) - min([s["ai_score"] for s in signals])

    structure = market_structure(avg, spread)

    leader = top[0]["symbol"]

    return {
        "model": "SOLANA_AI_V9_QUANT_INTELLIGENCE",
        "market_structure": structure,
        "narrative": f"{leader} leading {structure} market phase",
        "signals": top,
        "portfolio": portfolio
    }
