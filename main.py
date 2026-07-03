from fastapi import FastAPI
import requests
import time
import math

app = FastAPI()

STATE = {
    "cache": None,
    "cache_time": 0,
    "equity": 100.0,
    "history": {}
}

COINS_LIMIT = 100


# =========================
# SAFE FETCH (ANTI CRASH)
# =========================
def fetch_market():

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": COINS_LIMIT,
                "page": 1,
                "sparkline": "false"
            },
            timeout=10
        )

        data = r.json()

        if not isinstance(data, list):
            return []

        return data

    except:
        return []


# =========================
# SAFE ENGINE
# =========================
def engine(asset, btc):

    change = asset.get("price_change_percentage_24h") or 0
    volume = asset.get("total_volume") or 1
    rank = asset.get("market_cap_rank") or 100

    rel = change - btc
    momentum = change / 10

    volume_log = math.log1p(volume)

    memory = STATE["history"].get(asset["symbol"], 0)

    score = (
        rel * 0.35 +
        momentum * 0.20 +
        volume_log * 0.20 +
        (1 - rank / 100) * 0.15 +
        memory * 0.10
    )

    STATE["history"][asset["symbol"]] = rel * 0.7 + memory * 0.3

    return score


# =========================
# CORE
# =========================
def run():

    market = fetch_market()

    if not market:
        return {
            "model": "V41_SAFE_FIX",
            "status": "NO_DATA"
        }

    btc = 0
    for m in market:
        if m.get("symbol","").upper() == "BTC":
            btc = m.get("price_change_percentage_24h") or 0

    scored = []

    for m in market:

        score = engine(m, btc)

        scored.append({
            "symbol": m.get("symbol","").upper(),
            "score": round(score, 6)
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    return {
        "model": "V41_SAFE_FIX",
        "top10": top10,
        "equity": STATE["equity"]
    }


# =========================
# API
# =========================
@app.get("/update")
def update():
    return run()


@app.get("/")
def home():
    return {
        "model": "V41_SAFE_FIX",
        "status": "RUNNING"
    }
