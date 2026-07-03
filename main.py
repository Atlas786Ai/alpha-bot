from fastapi import FastAPI
import requests
import time
import numpy as np

app = FastAPI()

# =========================
# STATE MEMORY
# =========================
STATE = {
    "cache": None,
    "cache_time": 0,
    "equity": 100.0,
    "history": {}
}

COINS_LIMIT = 100


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {
        "model": "V41_QUANT_SYSTEM_FULL_STACK",
        "status": "MAIN + ENGINE SYNC ACTIVE"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v41()


# =========================
# FETCH MARKET
# =========================
def fetch_market():

    if STATE["cache"] and time.time() - STATE["cache_time"] < 60:
        return STATE["cache"]

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

        STATE["cache"] = data
        STATE["cache_time"] = time.time()

        return data

    except:
        return []


# =========================
# ENGINE V41 CORE
# =========================
def engine_v41(asset, btc):

    # normalize momentum
    momentum = (asset["change"] or 0) / 10

    # relative strength anchor
    rel = (asset["change"] or 0) - btc

    # log volume stabilization
    volume = np.log1p(asset["volume"] or 1)

    # rank stability (0-1)
    rank = 1 - min(asset["rank"] / 100, 1)

    # memory influence (trend persistence)
    symbol = asset["symbol"]

    prev = STATE["history"].get(symbol, 0)

    memory_factor = 0.7 * prev + 0.3 * rel

    # final score (balanced quant model)
    score = (
        rel * 0.30 +
        momentum * 0.15 +
        volume * 0.20 +
        rank * 0.15 +
        memory_factor * 0.20
    )

    # update memory
    STATE["history"][symbol] = memory_factor

    return score


# =========================
# REGIME DETECTOR
# =========================
def detect_regime(top_score):

    if top_score > 30:
        return "EXPANSION"

    if top_score > 15:
        return "TREND"

    return "CHOP"


# =========================
# MAIN V41 ENGINE
# =========================
def run_v41():

    market = fetch_market()

    if not market:
        return {
            "model": "V41_QUANT_SYSTEM_FULL_STACK",
            "status": "NO_DATA"
        }

    # BTC anchor
    btc = 0
    for m in market:
        if m["symbol"].upper() == "BTC":
            btc = m.get("price_change_percentage_24h", 0) or 0

    scored = []

    for m in market:

        asset = {
            "symbol": m["symbol"].upper(),
            "change": m.get("price_change_percentage_24h", 0),
            "volume": m.get("total_volume", 1),
            "rank": m.get("market_cap_rank", 100)
        }

        score = engine_v41(asset, btc)

        scored.append({
            "symbol": asset["symbol"],
            "score": round(score, 6),
            "momentum": asset["change"],
            "rank": asset["rank"]
        })

    # sort
    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    regime = detect_regime(top10[0]["score"])

    # portfolio allocation
    total = sum(max(x["score"], 0.0001) for x in top10)

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(x["score"] / total, 4)
        }
        for x in top10[:5]
    ]

    # equity update (smoothed)
    STATE["equity"] += np.mean([x["score"] for x in top10]) / 3000

    return {
        "model": "V41_QUANT_SYSTEM_FULL_STACK",
        "regime": regime,
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "memory_size": len(STATE["history"])
    }
