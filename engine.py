import math
import random

# -----------------------------
# MARKET DATA
# -----------------------------
def get_data():

    return [
        {"symbol": "ARB", "price_change": random.uniform(-2, 18), "volume": random.uniform(6e8, 2e9), "vol": random.uniform(0.05, 0.22)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 15), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 9), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.08)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 12), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.04, 0.2)},
        {"symbol": "DOGE", "price_change": random.uniform(-3, 20), "volume": random.uniform(7e8, 2e9), "vol": random.uniform(0.05, 0.3)},
    ]


# -----------------------------
# FEATURE ENGINE V8
# -----------------------------
def features(c):

    m = c.get("price_change", 0)
    v = math.log10(c.get("volume", 1) + 1)
    vol = c.get("vol", 0.1)

    momentum_strength = m * (1 - vol)
    acceleration = m * vol * 10
    liquidity = v * vol

    return m, v, vol, momentum_strength, acceleration, liquidity


# -----------------------------
# SCORE V8 (MORE REALISTIC)
# -----------------------------
def score(c):

    m, v, vol, ms, acc, liq = features(c)

    return (
        ms * 2.2 +
        acc * 2.0 +
        liq * 1.3 +
        math.log1p(abs(m)) * 1.1
    )


# -----------------------------
# MARKET STRESS INDEX
# -----------------------------
def stress_index(scores):

    avg = sum(scores) / len(scores)
    spread = max(scores) - min(scores)

    return round((abs(avg) * 0.6 + spread * 0.4), 3)


# -----------------------------
# REGIME DETECTION
# -----------------------------
def regime(scores, stress):

    if stress > 10:
        return "EXTREME_EXPANSION"
    elif stress > 6:
        return "EXPLOSIVE_ROTATION"
    elif stress > 3:
        return "HIGH_BETA_TREND"
    else:
        return "ACCUMULATION_PHASE"


# -----------------------------
# TREND PERSISTENCE
# -----------------------------
def persistence(m):

    # simple proxy: strength of move vs volatility
    return max(0, min(1, 1 / (1 + abs(m))))


# -----------------------------
# FORECAST MODULE (NEW V8 CORE)
# -----------------------------
def forecast(regime, stress):

    if regime == "EXTREME_EXPANSION":
        return "high continuation probability"
    elif regime == "EXPLOSIVE_ROTATION":
        return "breakout continuation with correction risk"
    elif regime == "HIGH_BETA_TREND":
        return "trend continuation with volatility spikes"
    else:
        return "range-bound / accumulation expected"


# -----------------------------
# MAIN ENGINE V8
# -----------------------------
def run_engine():

    data = get_data()

    signals = []
    scores = []

    for c in data:

        s = score(c)
        scores.append(s)

        m, v, vol, ms, acc, liq = features(c)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(s, 3),
            "momentum": round(m, 3),
            "vol": round(vol, 3),
            "momentum_strength": round(ms, 3),
            "persistence": round(persistence(m), 3)
        })

    signals = sorted(signals, key=lambda x: x["ai_score"], reverse=True)

    top = signals[:5]

    total = sum([abs(x["ai_score"]) + 1 for x in top]) or 1

    portfolio = [
        {
            "symbol": s["symbol"],
            "weight": round((abs(s["ai_score"]) + 1) / total, 3)
        }
        for s in top
    ]

    stress = stress_index(scores)
    reg = regime(scores, stress)

    leader = top[0]["symbol"]

    return {
        "model": "SOLANA_AI_V8_PREDICTIVE",
        "regime": reg,
        "market_stress": stress,
        "forecast": forecast(reg, stress),
        "narrative": f"{leader} driving {reg} phase",
        "signals": top,
        "portfolio": portfolio
    }
