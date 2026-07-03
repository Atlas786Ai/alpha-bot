from fastapi import FastAPI
import requests
import time
import math

app = FastAPI()

# =========================
# STATE (LEARNING CORE)
# =========================
STATE = {
    "equity": 100.0,
    "cache": None,
    "cache_time": 0,
    "last_error": None,

    # MEMORY SYSTEM
    "memory": {}  # symbol -> {"ema": float, "count": int}
}

CACHE_TTL = 60


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "model": "ATLAS_CANONICAL_V3",
        "status": "LEARNING_QUANT_CORE_ACTIVE"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    try:
        return run_system()
    except Exception as e:
        return {
            "model": "ATLAS_CANONICAL_V3",
            "status": "SAFE_ERROR_HANDLED",
            "error": str(e),
            "equity": STATE["equity"]
        }


# =========================
# DATA FETCH
# =========================
def fetch_market():

    if STATE["cache"] and time.time() - STATE["cache_time"] < CACHE_TTL:
        return STATE["cache"]

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 50,
                "page": 1,
                "sparkline": "false"
            },
            timeout=6
        )

        data = r.json()

        if isinstance(data, list):
            STATE["cache"] = data
            STATE["cache_time"] = time.time()
            return data

    except Exception as e:
        STATE["last_error"] = str(e)

    # fallback safe universe
    return [
        {"symbol": "BTC", "price_change_percentage_24h": 1.0, "total_volume": 1000000, "market_cap_rank": 1},
        {"symbol": "ETH", "price_change_percentage_24h": 0.8, "total_volume": 900000, "market_cap_rank": 2},
        {"symbol": "SOL", "price_change_percentage_24h": 2.0, "total_volume": 700000, "market_cap_rank": 5},
        {"symbol": "ARB", "price_change_percentage_24h": 3.0, "total_volume": 300000, "market_cap_rank": 20},
        {"symbol": "AVAX", "price_change_percentage_24h": 1.5, "total_volume": 500000, "market_cap_rank": 10},
    ]


# =========================
# NORMALIZATION
# =========================
def normalize(x):

    return {
        "symbol": (x.get("symbol") or "UNK").upper(),
        "change": float(x.get("price_change_percentage_24h") or 0),
        "volume": float(x.get("total_volume") or 1),
        "rank": int(x.get("market_cap_rank") or 100)
    }


# =========================
# MEMORY UPDATE (EMA STYLE)
# =========================
def update_memory(symbol, score):

    if symbol not in STATE["memory"]:
        STATE["memory"][symbol] = {
            "ema": score,
            "count": 1
        }
    else:
        m = STATE["memory"][symbol]

        alpha = 0.2  # learning rate

        m["ema"] = (alpha * score) + ((1 - alpha) * m["ema"])
        m["count"] += 1


# =========================
# SCORE ENGINE (LEARNING-BASED)
# =========================
def score(asset):

    change = asset["change"]
    volume = asset["volume"]
    rank = asset["rank"]

    momentum = change / 10
    volume_score = math.log1p(volume)
    rank_score = 1 - min(rank / 100, 1)

    stability = 1 / (1 + abs(momentum))

    return (
        momentum * 0.30 +
        volume_score * 0.25 +
        rank_score * 0.25 +
        stability * 0.20
    )


# =========================
# MAIN LEARNING ENGINE
# =========================
def run_system():

    raw = fetch_market()

    market = [normalize(x) for x in raw]

    scored = []

    for x in market:

        base_score = score(x)

        symbol = x["symbol"]

        update_memory(symbol, base_score)

        memory_score = STATE["memory"][symbol]["ema"]

        # 🔥 combine real-time + learned memory
        final_score = (base_score * 0.6) + (memory_score * 0.4)

        scored.append({
            "symbol": symbol,
            "score": round(final_score, 6),
            "raw_score": round(base_score, 6),
            "ema_score": round(memory_score, 6),
            "rank": x["rank"]
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    total = sum(abs(x["score"]) for x in top10) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(abs(x["score"]) / total, 4)
        }
        for x in top10[:5]
    ]

    # equity feedback loop (learning signal)
    STATE["equity"] += sum(x["score"] for x in top10) / 20000

    return {
        "model": "ATLAS_CANONICAL_V3",
        "status": "OK",
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "memory_size": len(STATE["memory"]),
        "last_error": STATE["last_error"]
    }
