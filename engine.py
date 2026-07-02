import math
import random
import json
import os

# -----------------------------
# PERSISTENT MEMORY (NEW)
# -----------------------------
MEMORY_FILE = "memory_v12.json"

def load_memory():

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "history": [],
        "performance": {},
        "strategy_weights": {
            "momentum": 2.0,
            "liquidity": 1.2,
            "volatility": 1.5
        }
    }


def save_memory(mem):

    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f)


MEMORY = load_memory()


# -----------------------------
# MARKET DATA
# -----------------------------
def get_data():

    return [
        {"symbol": "ARB", "price_change": random.uniform(-2, 22), "volume": random.uniform(6e8, 2e9), "vol": random.uniform(0.04, 0.25)},
        {"symbol": "DOGE", "price_change": random.uniform(-3, 20), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.05, 0.3)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 16), "volume": random.uniform(9e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 10), "volume": random.uniform(1e9, 2.5e9), "vol": random.uniform(0.01, 0.09)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 12), "volume": random.uniform(4e8, 1.5e9), "vol": random.uniform(0.03, 0.2)},
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

    return momentum, liquidity, acceleration


# -----------------------------
# SCORE ENGINE (V12)
# -----------------------------
def score(c):

    mom, liq, acc = features(c)

    w = MEMORY["strategy_weights"]

    return mom * w["momentum"] + liq * w["liquidity"] + acc * w["volatility"]


# -----------------------------
# RISK ADJUSTED SCORE (SHARPE-LIKE)
# -----------------------------
def risk_adjusted(score, vol):

    return score / (vol + 0.05)


# -----------------------------
# BACKTEST SIMULATOR (NEW CORE)
# -----------------------------
def backtest(symbol, score):

    hist = MEMORY["history"][-20:]  # last 20 states

    wins = 0
    total = 0

    for h in hist:
        if h["symbol"] == symbol:
            total += 1
            if h["score"] < score:
                wins += 1

    if total == 0:
        return 0.5

    return wins / total


# -----------------------------
# STRATEGY EVOLUTION (LEARNING)
# -----------------------------
def evolve_weights(mean, spread):

    w = MEMORY["strategy_weights"]

    if spread > 40:
        w["momentum"] *= 1.03
        w["volatility"] *= 1.02
    else:
        w["liquidity"] *= 1.01

    # normalize
    total = sum(w.values())

    for k in w:
        w[k] = round(w[k] / total * 3, 3)


# -----------------------------
# REGIME DETECTION
# -----------------------------
def regime(mean, spread):

    if spread > 60:
        return "EXPLOSIVE_ROTATION"
    elif mean > 55:
        return "HIGH_BETA_TREND"
    else:
        return "CHOP_OR_ACCUMULATION"


# -----------------------------
# MAIN ENGINE V12
# -----------------------------
def run_engine():

    data = get_data()

    raw = []

    for c in data:

        raw.append(score(c))

    mean = sum(raw) / len(raw)
    spread = max(raw) - min(raw)

    evolve_weights(mean, spread)

    processed = []

    for i, c in enumerate(data):

        symbol = c["symbol"]
        s = raw[i]

        ra = risk_adjusted(s, c["vol"])
        bt = backtest(symbol, s)

        processed.append({
            "symbol": symbol,
            "ai_score": round(s, 2),
            "risk_adj_score": round(ra, 2),
            "backtest_winrate": round(bt, 2)
        })

    processed = sorted(processed, key=lambda x: x["ai_score"], reverse=True)

    leader = processed[0]["symbol"]

    # SAVE HISTORY (NEW)
    for p in processed:
        MEMORY["history"].append({
            "symbol": p["symbol"],
            "score": p["ai_score"]
        })

    MEMORY["history"] = MEMORY["history"][-200:]  # keep last 200

    save_memory(MEMORY)

    total = sum([x["ai_score"] + 1 for x in processed]) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round((x["ai_score"] + 1) / total, 3)
        }
        for x in processed
    ]

    return {
        "model": "SOLANA_AI_V12_QUANT_CORE",
        "regime": regime(mean, spread),
        "narrative": f"{leader} leading adaptive quant cycle",
        "signals": processed,
        "portfolio": portfolio,
        "market_stats": {
            "mean": round(mean, 2),
            "spread": round(spread, 2)
        },
        "strategy_weights": MEMORY["strategy_weights"]
    }
