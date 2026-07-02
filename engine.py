import math
import random
import json
import os

# -----------------------------
# MEMORY FILE (simulated learning storage)
# -----------------------------
MEMORY_FILE = "memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):

        return {
            "w_momentum": 2.0,
            "w_volume": 1.2,
            "w_volatility": 2.5,
            "w_interaction": 1.5,
            "last_regime": "NONE"
        }

    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "w_momentum": 2.0,
            "w_volume": 1.2,
            "w_volatility": 2.5,
            "w_interaction": 1.5,
            "last_regime": "NONE"
        }


def save_memory(mem):

    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem, f)
    except:
        pass


# -----------------------------
# MARKET SIMULATION
# -----------------------------
def get_data():

    return [
        {"symbol": "DOGE", "price_change": random.uniform(-2, 15), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.05, 0.25)},
        {"symbol": "ARB", "price_change": random.uniform(-1, 12), "volume": random.uniform(4e8, 1.5e9), "volatility": random.uniform(0.04, 0.2)},
        {"symbol": "AVAX", "price_change": random.uniform(-2, 10), "volume": random.uniform(3e8, 1.3e9), "volatility": random.uniform(0.03, 0.18)},
        {"symbol": "ETH", "price_change": random.uniform(-1, 7), "volume": random.uniform(8e8, 2e9), "volatility": random.uniform(0.02, 0.08)},
        {"symbol": "SOL", "price_change": random.uniform(-1, 13), "volume": random.uniform(9e8, 2e9), "volatility": random.uniform(0.03, 0.15)},
    ]


# -----------------------------
# FEATURE ENGINE
# -----------------------------
def features(c):

    momentum = c["price_change"]
    volume = math.log10(c["volume"] + 1)
    vol = c["volatility"]

    interaction = momentum * vol * volume

    return momentum, volume, vol, interaction


# -----------------------------
# SELF-LEARNING SCORE
# -----------------------------
def score(c, w):

    momentum, volume, vol, interaction = features(c)

    return (
        w["w_momentum"] * momentum +
        w["w_volume"] * volume -
        w["w_volatility"] * abs(vol - 0.08) +
        w["w_interaction"] * math.log1p(abs(interaction))
    )


# -----------------------------
# REGIME DETECTION
# -----------------------------
def detect(scores):

    avg = sum(scores) / len(scores)
    spread = max(scores) - min(scores)

    if avg > 8 and spread > 6:
        return "EXPLOSIVE_ROTATION"
    elif avg > 4:
        return "HIGH_BETA_TREND"
    elif avg > 0:
        return "EARLY_ACCUMULATION"
    else:
        return "DISTRIBUTION"


# -----------------------------
# SELF LEARNING UPDATE RULE
# -----------------------------
def update_weights(mem, regime):

    # simple reinforcement-like adaptation

    if regime == "EXPLOSIVE_ROTATION":
        mem["w_momentum"] += 0.05
        mem["w_interaction"] += 0.03

    elif regime == "HIGH_BETA_TREND":
        mem["w_volume"] += 0.04

    elif regime == "DISTRIBUTION":
        mem["w_volatility"] += 0.05
        mem["w_momentum"] -= 0.03

    # clamp values
    for k in mem:
        if isinstance(mem[k], float):
            mem[k] = max(0.5, min(mem[k], 5.0))

    return mem


# -----------------------------
# MAIN ENGINE
# -----------------------------
def run_engine():

    mem = load_memory()

    data = get_data()

    signals = []
    scores = []

    for c in data:

        s = score(c, mem)

        scores.append(s)

        signals.append({
            "symbol": c["symbol"],
            "ai_score": round(s, 3),
            "momentum": round(c["price_change"], 3),
            "vol": round(c["volatility"], 3)
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

    regime = detect(scores)

    # -----------------------------
    # 🔥 LEARNING STEP
    # -----------------------------
    mem = update_weights(mem, regime)
    mem["last_regime"] = regime

    save_memory(mem)

    leader = top[0]["symbol"]

    narrative_map = {
        "EXPLOSIVE_ROTATION": f"{leader} driving aggressive expansion cycle",
        "HIGH_BETA_TREND": f"{leader} leading momentum continuation",
        "EARLY_ACCUMULATION": f"{leader} showing accumulation behavior",
        "DISTRIBUTION": "risk-off rotation detected"
    }

    return {
        "model": "SOLANA_AI_SELF_LEARNING_V4",
        "regime": regime,
        "narrative": narrative_map[regime],
        "signals": top,
        "portfolio": portfolio,
        "weights": mem
    }
