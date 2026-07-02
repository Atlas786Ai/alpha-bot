import math
import random

# -----------------------------
# MARKET DATA (stable simulation)
# -----------------------------
def get_data():

    return [
        {"symbol": "SOL", "price_change": random.uniform(-1, 14), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.15)},
        {"symbol": "ARB", "price_change": random.uniform(-2, 12), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.04, 0.2)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 8), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.08)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 10), "volume": random.uniform(3e8, 1.2e9), "vol": random.uniform(0.03, 0.2)},
        {"symbol": "DOGE", "price_change": random.uniform(-3, 16), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.05, 0.25)},
    ]


# -----------------------------
# FEATURE ENGINE (V7)
# -----------------------------
def features(c):

    momentum = c.get("price_change", 0)
    volume = math.log10(c.get("volume", 1) + 1)
    vol = c.get("vol", 0.1)

    trend_strength = momentum * (1 - vol)
    liquidity_pressure = volume * vol
    acceleration = momentum * vol * 10

    return momentum, volume, vol, trend_strength, liquidity_pressure, acceleration


# -----------------------------
# MARKET HEAT INDEX
# -----------------------------
def market_heat(scores):

    if not scores:
        return 0

    avg = sum(scores) / len(scores)
    spread = max(scores) - min(scores)

    heat = (avg * 0.6) + (spread * 0.4)

    return round(heat, 3)


# -----------------------------
# REGIME DETECTION (IMPROVED V7)
# -----------------------------
def detect_regime(scores, heat):

    if heat > 8:
        return "EXPLOSIVE_ROTATION"
    elif heat > 4:
        return "HIGH_BETA_TREND"
    elif heat > 1.5:
        return "ACCUMULATION"
    else:
        return "CHOP_MARKET"


# -----------------------------
# ANOMALY PRESSURE INDEX
# -----------------------------
def anomaly_index(momentum, vol):

    return abs(momentum) * vol * 10


# -----------------------------
# SCORE FUNCTION (V7)
# -----------------------------
def score(c):

    m, v, vol, trend, liquidity, accel = features(c)

    return (
        trend * 2.0 +
        liquidity * 1.4 +
        accel * 1.8 +
        math.log1p(abs(m)) * 1.2
    )


# -----------------------------
# PORTFOLIO ALLOCATION (V7 SMART RISK)
# -----------------------------
def weight(score, vol):

    risk_adj = 1 / (1 + vol)

    return (abs(score) + 1) * risk_adj


# -----------------------------
# MAIN ENGINE V7
# -----------------------------
def run_engine():

    data = get_data()

    signals = []
    scores = []
    anomalies = []

    for c in data:

        s = score(c)
        scores.append(s)

        m, v, vol, trend, liquidity, accel = features(c)

        anomaly = anomaly_index(m, vol)
        anomalies.append(anomaly)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(s, 3),
            "momentum": round(m, 3),
            "vol": round(vol, 3),
            "trend_strength": round(trend, 3),
            "anomaly_pressure": round(anomaly, 3)
        })

    # ranking
    signals = sorted(signals, key=lambda x: x["ai_score"], reverse=True)

    top = signals[:5]

    # portfolio weights
    raw_weights = []

    for s in top:

        vol = s["vol"]
        w = weight(s["ai_score"], vol)

        raw_weights.append(w)

    total = sum(raw_weights) or 1

    portfolio = []

    for i, s in enumerate(top):

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(raw_weights[i] / total, 3)
        })

    # market intelligence layer
    heat = market_heat(scores)
    regime = detect_regime(scores, heat)

    # regime transition logic (very important V7 feature)
    leader = top[0]["symbol"]

    narrative_map = {
        "EXPLOSIVE_ROTATION": f"{leader} leading aggressive expansion cycle",
        "HIGH_BETA_TREND": f"{leader} driving momentum continuation",
        "ACCUMULATION": f"{leader} showing structured accumulation",
        "CHOP_MARKET": "market in consolidation / uncertainty phase"
    }

    return {
        "model": "SOLANA_AI_V7_INTELLIGENCE",
        "regime": regime,
        "market_heat": heat,
        "narrative": narrative_map[regime],
        "signals": top,
        "portfolio": portfolio,
        "anomaly_avg": round(sum(anomalies) / len(anomalies), 3)
    }
