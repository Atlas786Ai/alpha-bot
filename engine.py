import math
import random
import sqlite3

DB_PATH = "atlas_v14.db"


# -----------------------------
# SAFE DB
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT,
            score REAL,
            vol REAL,
            regime TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# MARKET DATA
# -----------------------------
def get_market():

    return [
        {"symbol": "ETH", "price": random.uniform(2500, 3200), "volume": random.uniform(1e9, 3e9), "vol": random.uniform(0.01, 0.1)},
        {"symbol": "SOL", "price": random.uniform(120, 160), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "DOGE", "price": random.uniform(0.1, 0.3), "volume": random.uniform(1e9, 2e9), "vol": random.uniform(0.05, 0.3)},
    ]


# -----------------------------
# FEATURES
# -----------------------------
def features(c):

    price = c["price"]
    vol = c["vol"]
    volume = math.log10(c["volume"] + 1)

    momentum = price * vol
    liquidity = volume * vol
    trend = price * volume

    return momentum, liquidity, trend


# -----------------------------
# RAW SCORE
# -----------------------------
def raw_score(c):

    m, l, t = features(c)

    return (m * 2.0) + (l * 1.2) + (t * 1.5)


# -----------------------------
# NORMALIZATION (CRITICAL FIX)
# -----------------------------
def normalize(scores):

    mn = min(scores)
    mx = max(scores)

    if mx - mn == 0:
        return [0.5 for _ in scores]

    return [(s - mn) / (mx - mn) for s in scores]


# -----------------------------
# SOLANA 2023 SIMILARITY ENGINE (REALISTIC)
# -----------------------------
def sol_similarity(momentum, vol, trend):

    return (
        0.4 * momentum +
        0.35 * (1 - vol) +
        0.25 * trend
    )


# -----------------------------
# REGIME PROBABILITY MODEL
# -----------------------------
def regime(scores):

    spread = max(scores) - min(scores)
    mean = sum(scores) / len(scores)

    p_explosive = min(1.0, spread / 100)
    p_chop = max(0.1, 1 - mean / 200)

    if p_explosive > 0.6:
        return "EXPLOSIVE_ROTATION"
    elif p_chop > 0.5:
        return "CHOP_MARKET"
    else:
        return "HIGH_BETA_TREND"


# -----------------------------
# SAVE
# -----------------------------
def save(symbol, score, vol, reg):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO market_data VALUES (?, ?, ?, ?)
    """, (symbol, score, vol, reg))

    conn.commit()
    conn.close()


# -----------------------------
# MAIN ENGINE V14
# -----------------------------
def run_engine():

    data = get_market()

    raw_scores = []
    computed = []

    for c in data:

        r = raw_score(c)
        raw_scores.append(r)

        m, l, t = features(c)

        sim = sol_similarity(m, c["vol"], t)

        computed.append({
            "symbol": c["symbol"],
            "raw_score": r,
            "sol_similarity": round(sim, 3),
            "vol": c["vol"]
        })

    # normalize scores
    norm = normalize(raw_scores)

    for i in range(len(computed)):
        computed[i]["ai_score"] = round(norm[i] * 100, 2)

    computed = sorted(computed, key=lambda x: x["ai_score"], reverse=True)

    reg = regime([c["ai_score"] for c in computed])

    leader = computed[0]["symbol"]

    # portfolio softmax
    weights_raw = [c["ai_score"] for c in computed]
    total = sum(weights_raw) + 1e-9

    portfolio = []

    for c in computed:

        w = (c["ai_score"] + 1) / total

        # risk cap
        w = min(w, 0.6)

        portfolio.append({
            "symbol": c["symbol"],
            "weight": round(w, 3)
        })

    return {
        "model": "SOLANA_AI_V14_NORMALIZED_QUANT",
        "regime": reg,
        "narrative": f"{leader} leading stabilized quant cycle",
        "signals": computed,
        "portfolio": portfolio,
        "engine": "normalized + probabilistic + solana_similarity_v2"
    }
