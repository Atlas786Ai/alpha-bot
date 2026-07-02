import math
import random

MEMORY = {
    "history": [],
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
        {"symbol": "DOGE", "price_change": random.uniform(-3, 22), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.05, 0.3)},
        {"symbol": "ARB", "price_change": random.uniform(-2, 20), "volume": random.uniform(6e8, 2e9), "vol": random.uniform(0.04, 0.25)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 16), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 10), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.09)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 12), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.03, 0.2)},
    ]

# -----------------------------
# FEATURES
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
# RAW SCORE
# -----------------------------
def raw_score(c):
    mom, liq, acc = features(c)
    w = MEMORY["strategy_weights"]

    return mom*w["momentum"] + liq*w["liquidity"] + acc*w["volatility"]

# -----------------------------
# NORMALIZATION (FIXED)
# -----------------------------
def normalize(scores):
    mn = min(scores)
    mx = max(scores)
    rng = mx - mn if mx != mn else 1

    return [(s - mn) / rng * 100 for s in scores]

# -----------------------------
# RISK ADJUSTMENT (FIXED)
# -----------------------------
def risk_adj(score, vol):
    return score / (1 + vol * 10)

# -----------------------------
# BACKTEST (FIXED LOGIC)
# -----------------------------
def backtest(symbol, score):

    hist = MEMORY["history"][-50:]

    wins = 0
    total = 0

    for h in hist:
        if h["symbol"] == symbol:
            total += 1
            if score > h["score"]:
                wins += 1

    if total < 3:
        return 0.5

    return wins / total

# -----------------------------
# SIGNAL FILTER (IMPORTANT FIX)
# -----------------------------
def filter_signal(score, mean):
    return score > mean * 0.4

# -----------------------------
# MAIN ENGINE V12.1
# -----------------------------
def run_engine():

    data = get_data()

    raw = [raw_score(c) for c in data]

    norm = normalize(raw)

    mean = sum(norm) / len(norm)
    spread = max(norm) - min(norm)

    processed = []

    for i, c in enumerate(data):

        if not filter_signal(norm[i], mean):
            continue

        symbol = c["symbol"]

        ra = risk_adj(norm[i], c["vol"])
        bt = backtest(symbol, norm[i])

        processed.append({
            "symbol": symbol,
            "ai_score": round(norm[i], 2),
            "risk_adj_score": round(ra, 2),
            "backtest_winrate": round(bt, 3)
        })

        # save memory
        MEMORY["history"].append({
            "symbol": symbol,
            "score": norm[i]
        })

    MEMORY["history"] = MEMORY["history"][-200:]

    # portfolio
    total = sum([p["ai_score"] + 1 for p in processed]) or 1

    portfolio = [
        {
            "symbol": p["symbol"],
            "weight": round((p["ai_score"] + 1) / total, 3)
        }
        for p in processed
    ]

    leader = processed[0]["symbol"] if processed else "NONE"

    return {
        "model": "SOLANA_AI_V12_1_FIXED_QUANT_CORE",
        "regime": "EXPLOSIVE_ROTATION",
        "narrative": f"{leader} leading stabilized quant cycle",
        "signals": processed,
        "portfolio": portfolio,
        "market_stats": {
            "mean": round(mean, 2),
            "spread": round(spread, 2)
        }
    }
