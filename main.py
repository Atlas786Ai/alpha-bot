from fastapi import FastAPI
import requests
import time
import math
import random
import statistics

app = FastAPI()

# =========================
# STATE (DATA MIRROR CORE)
# =========================
STATE = {
    "equity": 100.0,
    "cache": None,
    "cache_time": 0,
    "mirror": {},   # 🔥 local market memory
    "last_error": None
}

COINS_LIMIT = 100
CACHE_TTL = 45  # seconds


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "model": "V47_DATA_INFRA_QUANT_CORE",
        "status": "DATA MIRROR + MULTI SOURCE ACTIVE"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v47()


# =========================
# HEADERS ROTATION (ANTI BLOCK)
# =========================
def headers_pool():
    return [
        {"User-Agent": "Mozilla/5.0"},
        {"User-Agent": "Chrome/120"},
        {"User-Agent": "Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android)"},
    ]


# =========================
# EXPONENTIAL BACKOFF REQUEST
# =========================
def safe_request(url, params=None):

    wait = 0.5

    for i in range(3):

        try:
            r = requests.get(
                url,
                params=params,
                headers=random.choice(headers_pool()),
                timeout=6
            )

            data = r.json()

            if data:
                return data

        except Exception as e:
            STATE["last_error"] = str(e)
            time.sleep(wait)
            wait *= 2  # 🔥 exponential backoff

    return None


# =========================
# COINGECKO SOURCE
# =========================
def fetch_coingecko():

    return safe_request(
        "https://api.coingecko.com/api/v3/coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": COINS_LIMIT,
            "page": 1,
            "sparkline": "false"
        }
    )


# =========================
# BINANCE SOURCE
# =========================
def fetch_binance():

    data = safe_request("https://api.binance.com/api/v3/ticker/24hr")

    if not data:
        return None

    out = []

    for d in data:
        if "USDT" in d.get("symbol", ""):

            try:
                out.append({
                    "symbol": d["symbol"].replace("USDT", ""),
                    "price_change_percentage_24h": float(d.get("priceChangePercent", 0)),
                    "total_volume": float(d.get("volume", 0)),
                    "market_cap_rank": 50
                })
            except:
                continue

    return out if len(out) > 10 else None


# =========================
# SYNTHETIC MARKET (LAST RESORT BUT SMART)
# =========================
def synthetic_market():

    base = STATE["mirror"] if STATE["mirror"] else {}

    symbols = ["BTC","ETH","SOL","ARB","AVAX","LINK","OP","INJ","TIA","MATIC"]

    out = []

    for s in symbols:

        prev = base.get(s, {"change": random.uniform(-1, 2), "volume": 500000})

        new_change = prev["change"] * 0.7 + random.uniform(-1, 2) * 0.3

        out.append({
            "symbol": s,
            "price_change_percentage_24h": new_change,
            "total_volume": prev["volume"],
            "market_cap_rank": random.randint(1, 50)
        })

    return out


# =========================
# UNIFIED DATA LAYER (V47 CORE)
# =========================
def get_market():

    # TTL cache first
    if STATE["cache"] and time.time() - STATE["cache_time"] < CACHE_TTL:
        return STATE["cache"]

    data = fetch_coingecko()

    if not data:
        data = fetch_binance()

    if not data:
        data = synthetic_market()

    STATE["cache"] = data
    STATE["cache_time"] = time.time()

    return data


# =========================
# UPDATE MIRROR (LEARNING MEMORY)
# =========================
def update_mirror(market):

    for m in market:

        s = m.get("symbol", "").upper()
        c = m.get("price_change_percentage_24h", 0)
        v = m.get("total_volume", 0)

        if s not in STATE["mirror"]:
            STATE["mirror"][s] = {"change": c, "volume": v}

        else:
            old = STATE["mirror"][s]

            # smoothing update
            STATE["mirror"][s] = {
                "change": old["change"] * 0.6 + c * 0.4,
                "volume": old["volume"] * 0.8 + v * 0.2
            }


# =========================
# SCORE ENGINE
# =========================
def score(asset):

    change = asset.get("price_change_percentage_24h", 0)
    volume = asset.get("total_volume", 1)
    rank = asset.get("market_cap_rank", 100)

    momentum = change / 10
    volume_log = math.log1p(volume)
    rank_score = 1 - min(rank / 100, 1)
    stability = 1 / (1 + abs(momentum))

    return (
        momentum * 0.25 +
        volume_log * 0.20 +
        rank_score * 0.25 +
        stability * 0.30
    )


# =========================
# MAIN ENGINE V47
# =========================
def run_v47():

    market = get_market()

    update_mirror(market)

    scored = []

    for m in market:

        s = score(m)

        symbol = m.get("symbol", "").upper()

        STATE["mirror"].setdefault(symbol, {"change": 0, "volume": 0})

        scored.append({
            "symbol": symbol,
            "score": round(s, 6),
            "momentum": m.get("price_change_percentage_24h", 0),
            "rank": m.get("market_cap_rank", 100)
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

    STATE["equity"] += sum(x["score"] for x in top10) / 20000

    return {
        "model": "V47_DATA_INFRA_QUANT_CORE",
        "status": "OK",
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "cache_age": round(time.time() - STATE["cache_time"], 2),
        "error": STATE["last_error"]
    }
