from fastapi import FastAPI
import requests
import time
import math

app = FastAPI()

STATE = {
    "equity": 100.0,
    "history": {},
    "last_error": None,
    "data_health": "UNKNOWN"
}

COINS_LIMIT = 100


# =========================
# SAFE DATA FETCH (WITH RETRY)
# =========================
def fetch_market():

    urls = [
        "https://api.coingecko.com/api/v3/coins/markets"
    ]

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": COINS_LIMIT,
        "page": 1,
        "sparkline": "false"
    }

    for url in urls:

        try:
            r = requests.get(url, params=params, timeout=10)

            data = r.json()

            if isinstance(data, list) and len(data) > 10:

                STATE["data_health"] = "OK"

                return data

        except Exception as e:

            STATE["last_error"] = str(e)

            continue

    STATE["data_health"] = "FAILOVER"

    return []


# =========================
# SAFE SCORE ENGINE
# =========================
def score(asset, btc):

    change = asset.get("price_change_percentage_24h") or 0
    volume = asset.get("total_volume") or 1
    rank = asset.get("market_cap_rank") or 100
    symbol = asset.get("symbol", "UNK").upper()

    rel = change - btc
    momentum = change / 10

    volume_log = math.log1p(volume)

    memory = STATE["history"].get(symbol, 0)

    # stable scoring (bounded)
    raw_score = (
        rel * 0.3 +
        momentum * 0.2 +
        volume_log * 0.2 +
        (1 - rank / 100) * 0.15 +
        memory * 0.15
    )

    # clamp to avoid explosion
    final_score = max(min(raw_score, 50), -50)

    # update memory
    STATE["history"][symbol] = memory * 0.7 + rel * 0.3

    return final_score


# =========================
# REGIME DETECTOR
# =========================
def regime(top):

    if top > 25:
        return "EXPANSION"

    if top > 10:
        return "TREND"

    return "CHOP"


# =========================
# MAIN ENGINE
# =========================
def run_v42():

    market = fetch_market()

    # 🚨 GUARANTEE OUTPUT ALWAYS
    if not market:

        return {
            "model": "V42_DEBUG_RESILIENT",
            "status": "NO_DATA",
            "data_health": STATE["data_health"],
            "error": STATE["last_error"],
            "top10": [],
            "portfolio": [],
            "equity": STATE["equity"]
        }

    # BTC anchor safe
    btc = 0
    for m in market:
        if m.get("symbol","").upper() == "BTC":
            btc = m.get("price_change_percentage_24h") or 0

    scored = []

    for m in market:

        try:

            s = score(m, btc)

            scored.append({
                "symbol": m.get("symbol","").upper(),
                "score": round(s, 4),
                "momentum": m.get("price_change_percentage_24h") or 0
            })

        except Exception as e:

            STATE["last_error"] = str(e)
            continue

    # if scoring failed completely
    if not scored:

        return {
            "model": "V42_DEBUG_RESILIENT",
            "status": "SCORING_FAILED",
            "error": STATE["last_error"]
        }

    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    r = regime(top10[0]["score"])

    total = sum(abs(x["score"]) for x in top10) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(abs(x["score"]) / total, 4)
        }
        for x in top10[:5]
    ]

    # safe equity update
    STATE["equity"] += sum(x["score"] for x in top10) / 10000

    return {
        "model": "V42_DEBUG_RESILIENT",
        "regime": r,
        "status": "OK",
        "data_health": STATE["data_health"],
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "error": STATE["last_error"]
    }


# =========================
# API
# =========================
@app.get("/")
def home():
    return {
        "model": "V42_DEBUG_RESILIENT",
        "status": "RUNNING"
    }


@app.get("/update")
def update():
    return run_v42()
