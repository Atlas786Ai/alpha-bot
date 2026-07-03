from fastapi import FastAPI
import urllib.request
import urllib.parse
import json
import time
import math

app = FastAPI()

# =========================
# STATE (PERSISTENT MEMORY)
# =========================
STATE = {
    "cache_time": 0,
    "cache_data": None,
    "equity": 100.0,
    "btc_last": 0.0
}


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "model": "V40_REAL_QUANT_MAIN",
        "status": "ANCHOR + ENGINE V33 CONNECTED"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v40()


# =========================
# FETCH MARKET
# =========================
def fetch_market():

    if STATE["cache_data"] and time.time() - STATE["cache_time"] < 60:
        return STATE["cache_data"]

    try:

        url = "https://api.coingecko.com/api/v3/coins/markets"

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false"
        }

        query = urllib.parse.urlencode(params)

        req = urllib.request.Request(
            url + "?" + query,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        raw = urllib.request.urlopen(req, timeout=6).read()
        data = json.loads(raw)

        STATE["cache_data"] = data
        STATE["cache_time"] = time.time()

        return data

    except:
        return []


# =========================
# ENGINE IMPORT (V33 LOGIC INLINE)
# =========================
def engine_score(asset, btc):

    import math

    momentum = asset["change"] / 10
    rel = asset["change"] - btc
    volume = math.log1p(asset["volume"])
    rank = 1 - (asset["rank"] / 100)

    stability = 1 / (1 + abs(momentum))

    return (
        rel * 0.35 +
        momentum * 0.20 +
        volume * 0.20 +
        rank * 0.15 +
        stability * 0.10
    )


# =========================
# MAIN V40 ENGINE
# =========================
def run_v40():

    market = fetch_market()

    if not market:
        return {
            "model": "V40_REAL_QUANT_MAIN",
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
            "change": m.get("price_change_percentage_24h", 0) or 0,
            "volume": m.get("total_volume", 0),
            "rank": m.get("market_cap_rank", 100)
        }

        score = engine_score(asset, btc)

        scored.append({
            "symbol": asset["symbol"],
            "score": round(score, 6),
            "momentum": asset["change"],
            "rank": asset["rank"]
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    # portfolio (stable weights)
    total = sum(max(x["score"], 0.0001) for x in top10)

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(x["score"] / total, 4)
        }
        for x in top10[:5]
    ]

    # equity simulation (slower, more realistic)
    STATE["equity"] += sum(x["score"] for x in top10) / 5000

    return {
        "model": "V40_REAL_QUANT_MAIN",
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "btc_anchor": btc
    }
