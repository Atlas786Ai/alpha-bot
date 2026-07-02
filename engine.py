import math
import random

# -----------------------------
# MARKET SIMULATION (stable)
# -----------------------------
def get_data():

    return [
        {"symbol": "SOL", "price_change": random.uniform(1, 12), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.03, 0.12)},
        {"symbol": "ARB", "price_change": random.uniform(0, 10), "volume": random.uniform(3e8, 1.2e9), "volatility": random.uniform(0.05, 0.18)},
        {"symbol": "AVAX", "price_change": random.uniform(-1, 9), "volume": random.uniform(4e8, 1.5e9), "volatility": random.uniform(0.04, 0.15)},
        {"symbol": "DOGE", "price_change": random.uniform(-2, 15), "volume": random.uniform(5e8, 1.8e9), "volatility": random.uniform(0.06, 0.22)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 6), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.02, 0.06)},
        {"symbol": "BTC", "price_change": random.uniform(-1, 5), "volume": random.uniform(1e9, 3e9), "volatility": random.uniform(0.01, 0.04)},
    ]


# -----------------------------
# FEATURE ENGINE (professional)
# -----------------------------
def features(c):

    momentum = c["price_change"]
    volume = math.log10(c["volume"] + 1)
    vol = c["volatility"]

    # breakout intensity
    breakout = momentum * vol * 12

    # liquidity pressure
    liquidity = volume * vol

    # acceleration (non-linear hype)
    acceleration = math.sqrt(abs(momentum)) * volume

    # risk distortion (important for regime shift detection)
    risk = abs(vol - 0.08)

    return breakout, liquidity, acceleration, risk, momentum, vol


# -----------------------------
# SOLANA-LIKE NARRATIVE MODEL
# -----------------------------
def solana_similarity(c):

    breakout, liquidity, acceleration, risk, momentum, vol = features(c)

    score = (
        breakout * 3.0 +
        liquidity * 1.4 +
        math.log1p(acceleration) * 2.0 -
        risk * 6.0
    )

    return score


# -----------------------------
# REGIME DETECTOR (NEW)
# -----------------------------
def detect_regime(signals):

    avg = sum([s["sol_score"] for s in signals]) / len(signals)

    volatility_cluster = sum([s["vol"] for s in signals]) / len(signals)

    if avg > 80 and volatility_cluster > 0.1:
        return "MEME_SUPERCYCLE"
    elif avg > 50:
        return "HIGH_BETA_BREAKOUT"
    elif avg > 25:
        return "EARLY_ROTATION"
    else:
        return "CHOP_MARKET"


# -----------------------------
# MAIN ENGINE
# -----------------------------
def run_engine():

    data = get_data()

    signals = []

    for c in data:

        sol_score = solana_similarity(c)

        breakout, liquidity, acceleration, risk, momentum, vol = features(c)

        signals.append({
            "symbol": c["symbol"],
            "sol_score": round(sol_score, 3),
            "momentum": round(momentum, 3),
            "vol": round(vol, 3),
            "breakout": round(breakout, 3),
            "liquidity": round(liquidity, 3)
        })

    # ranking
    signals = sorted(signals, key=lambda x: x["sol_score"], reverse=True)

    top = signals[:5]

    # portfolio (risk-adjusted allocation)
    total = sum([abs(s["sol_score"]) + 1 for s in top]) or 1

    portfolio = []

    for s in top:

        risk_adj = 1 / (1 + s["vol"])

        weight = ((abs(s["sol_score"]) + 1) * risk_adj) / total

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(weight, 3)
        })

    # regime
    regime = detect_regime(top)

    # narrative layer (NEW — very important upgrade)
    leader = top[0]["symbol"]

    if regime == "MEME_SUPERCYCLE":
        narrative = f"{leader} leading speculative expansion phase"
    elif regime == "HIGH_BETA_BREAKOUT":
        narrative = f"{leader} driving high-beta momentum rotation"
    elif regime == "EARLY_ROTATION":
        narrative = f"{leader} showing early accumulation behavior"
    else:
        narrative = "market in consolidation phase"

    return {
        "model": "SOLANA_2023_SIMILARITY_V2",
        "regime": regime,
        "narrative": narrative,
        "signals": top,
        "portfolio": portfolio
    }
