import math
import random
import sqlite3

DB_PATH = "atlas.db"

# -----------------------------
# SAFE DB CONNECTION (FIX THREAD ERROR)
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -----------------------------
# INIT DB
# -----------------------------
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
# MARKET DATA (SIMULATED)
# -----------------------------
def get_market():

    return [
        {"symbol": "DOGE", "price": random.uniform(0.1, 0.3), "volume": random.uniform(1e9, 2e9), "vol": random.uniform(0.05, 0.3)},
        {"symbol": "SOL", "price": random.uniform(120, 160), "volume": random.uniform(8e8, 2e9), "vol": random.uniform(0.03, 0.18)},
        {"symbol": "ETH", "price": random.uniform(2500, 3200), "volume": random.uniform(1e9, 3e9), "vol": random.uniform(0.01, 0.1)},
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
# SCORE
# -----------------------------
def score(c):

    m, l, t = features(c)

    return m * 2.0 + l * 1.2 + t * 1.5


# -----------------------------
# REGIME
# -----------------------------
def regime(scores):

    spread = max(scores) - min(scores)
    mean = sum(scores) / len(scores)

    if spread > 80:
        return "EXPLOSIVE_ROTATION"
    elif mean > 100:
        return "HIGH_BETA_TREND"
    else:
        return "CHOP"


# -----------------------------
# SAVE TO DB (FIXED THREAD SAFE)
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
# MAIN ENGINE
# -----------------------------
def run_engine():

    data = get_market()

    scores = []
    raw = []

    for c in data:

        s = score(c)
        scores.append(s)
        raw.append((c, s))

    reg = regime(scores)

    processed = []

    for c, s in raw:

        processed.append({
            "symbol": c["symbol"],
            "ai_score": round(s, 2)
        })

        save(c["symbol"], s, c["vol"], reg)

    processed = sorted(processed, key=lambda x: x["ai_score"], reverse=True)

    leader = processed[0]["symbol"]

    total = sum([p["ai_score"] + 1 for p in processed])

    portfolio = [
        {
            "symbol": p["symbol"],
            "weight": round((p["ai_score"] + 1) / total, 3)
        }
        for p in processed
    ]

    return {
        "model": "SOLANA_AI_FIXED_THREAD_SAFE_V13",
        "regime": reg,
        "narrative": f"{leader} leading market phase",
        "signals": processed,
        "portfolio": portfolio
    }
