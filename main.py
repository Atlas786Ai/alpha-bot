from fastapi import FastAPI
import requests
import time
import math
import random

app = FastAPI()

# =========================
# STATE (SIMPLE + SAFE)
# =========================
STATE = {
    "equity": 100.0,
    "last_error": None,
    "cache": None,
    "cache_time": 0
}

CACHE_TTL = 60


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {
        "status": "CLEAN ENGINE ACTIVE",
        "model": "CLEAN_QUANT_V1"
    }


# =========================
# UPDATE (ONLY ONE ENTRY POINT)
# =========================
@app.get("/update")
def update():
    try:
        return run_engine()
    except Exception as e:
        return {
            "status": "ERROR_HANDLED",
            "error": str(e),
            "equity": STATE["equity"]
        }


# =========================
# SAFE REQUEST FUNCTION
# =========================
def safe_get(url, params=None):

    try:
        r = requests.get(url, params=params, timeout=6)

        if r.status_code != 200:
            return None

        return r.json()

    except Exception as e:
        STATE["last_error"] = str(e)
        return None


# =========================
# MARKET DATA (CLEAN LAYER)
# =========================
def get_market():

    # cache first
    if STATE["cache"] and time.time() - STATE["cache_time"] < CACHE_TTL:
        return STATE["cache"]

    data = safe_get(
        "https://api.coingecko.com/api/v3/coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "sparkline": "false"
        }
    )

    # fallback guaranteed data
    if not data:
        data = [
            {"symbol": "BTC", "price_change_percentage_24h": 1.2, "total_volume": 1000000, "market_cap_rank": 1},
            {"symbol": "ETH", "price_change_percentage_24h": 0.8, "total_volume": 900000, "market_cap_rank": 2},
            {"symbol": "SOL", "price_change_percentage_24h": 2.1, "total_volume": 700000, "market_cap_rank": 5},
            {"symbol": "ARB", "price_change_percentage_24h": 3.0, "total_volume": 300000, "market_cap_rank": 20},
            {"symbol": "AVAX", "price_change_percentage_24h": 1.5, "total_volume": 500000, "market_cap_rank": 10},
        ]

    STATE["cache"] = data
    STATE["cache_time"] = time.time()

    return data


# =========================
# SIMPLE SCORE ENGINE
# =========================
def score(asset):

    change = asset.get("price_change_percentage_24h", 0) or 0
    volume = asset.get("total_volume", 1) or 1
    rank = asset.get("market_cap_rank", 100) or 100

    momentum = change / 10
    volume_score = math.log1p(volume)
    rank_score = 1 - min(rank / 100, 1)

    stability = 1 / (1 + abs(momentum))

    return (
        momentum * 0.30 +
        volume_score * 0.20 +
        rank_score * 0.30 +
        stability * 0.20
    )


# =========================
# MAIN ENGINE (ONLY ONE)
# =========================
def run_engine():

    market = get_market()

    scored = []

    for m in market:

        symbol = (m.get("symbol") or "UNK").upper()

        s = score(m)

        scored.append({
            "symbol": symbol,
            "score": round(s, 6),
            "momentum": m.get("price_change_percentage_24h", 0)
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

    # equity simulation (stable)
    STATE["equity"] += sum(x["score"] for x in top10) / 20000

    return {
        "model": "CLEAN_QUANT_V1",
        "status": "OK",
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "cache_age": round(time.time() - STATE["cache_time"], 2),
        "error": STATE["last_error"]
    }
