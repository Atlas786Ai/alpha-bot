from fastapi import FastAPI
import requests
import time
import math
import random
import statistics

app = FastAPI()

# =========================
# STATE (MEMORY SYSTEM)
# =========================
STATE = {
    "equity": 100.0,
    "last_error": None,
    "weights": {
        "momentum": 0.35,
        "volume": 0.25,
        "rank": 0.20,
        "stability": 0.20
    },
    "memory": {},
    "history": []
}

COINS_LIMIT = 100


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "model": "V46_ADAPTIVE_QUANT_AI",
        "status": "LEARNING + MEMORY + ADAPTIVE WEIGHTS ACTIVE"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v46()


# =========================
# USER AGENT ROTATION (ANTI BLOCK)
# =========================
def headers_pool():
    return [
        {"User-Agent": "Mozilla/5.0"},
        {"User-Agent": "Chrome/120.0"},
        {"User-Agent": "Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux)"},
    ]


# =========================
# DATA SOURCE (SAFE MULTI RETRY)
# =========================
def fetch_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    for _ in range(3):

        try:
            r = requests.get(
                url,
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": COINS_LIMIT,
                    "page": 1,
                    "sparkline": "false"
                },
                headers=random.choice(headers_pool()),
                timeout=6
            )

            data = r.json()

            if isinstance(data, list) and len(data) > 10:
                return data

        except Exception as e:
            STATE["last_error"] = str(e)
            time.sleep(0.3)

    return []


# =========================
# REGIME DETECTION (MARKET STATE)
# =========================
def detect_regime(market):

    changes = [m.get("price_change_percentage_24h", 0) for m in market]

    if not changes:
        return "UNKNOWN"

    avg = statistics.mean(changes)

    if avg > 1.5:
        return "BULL"

    if avg < -1.5:
        return "BEAR"

    return "ACCUMULATION"


# =========================
# ADAPTIVE WEIGHT ENGINE (KEY FEATURE V46)
# =========================
def adapt_weights(regime):

    w = STATE["weights"]

    if regime == "BULL":
        w["momentum"] = min(w["momentum"] + 0.05, 0.5)
        w["volume"] = min(w["volume"] + 0.03, 0.4)

    elif regime == "BEAR":
        w["stability"] = min(w["stability"] + 0.05, 0.5)
        w["rank"] = min(w["rank"] + 0.03, 0.4)

    else:
        # neutral balancing
        for k in w:
            w[k] *= 0.99

    total = sum(w.values())

    for k in w:
        w[k] = w[k] / total


# =========================
# SCORE ENGINE (ADAPTIVE)
# =========================
def score(asset, btc):

    change = asset.get("price_change_percentage_24h", 0)
    volume = asset.get("total_volume", 1)
    rank = asset.get("market_cap_rank", 100)

    rel = change - btc
    momentum = change / 10
    volume_log = math.log1p(volume)
    rank_score = 1 - min(rank / 100, 1)
    stability = 1 / (1 + abs(momentum))

    w = STATE["weights"]

    return (
        rel * w["momentum"] +
        momentum * w["momentum"] +
        volume_log * w["volume"] +
        rank_score * w["rank"] +
        stability * w["stability"]
    )


# =========================
# MEMORY UPDATE (LEARNING SYSTEM)
# =========================
def update_memory(symbol, score):

    if symbol not in STATE["memory"]:
        STATE["memory"][symbol] = []

    STATE["memory"][symbol].append(score)

    if len(STATE["memory"][symbol]) > 20:
        STATE["memory"][symbol].pop(0)


# =========================
# MAIN ENGINE V46
# =========================
def run_v46():

    market = fetch_market()

    if not market:
        return {
            "model": "V46_ADAPTIVE_QUANT_AI",
            "status": "NO_DATA_SAFE_FALLBACK"
        }

    changes = [m.get("price_change_percentage_24h", 0) for m in market if m]

    btc = 0

    for m in market:
        if m.get("symbol", "").upper() == "BTC":
            btc = m.get("price_change_percentage_24h", 0)

    regime = detect_regime(market)

    adapt_weights(regime)

    scored = []

    for m in market:

        s = score(m, btc)

        symbol = m.get("symbol", "").upper()

        update_memory(symbol, s)

        scored.append({
            "symbol": symbol,
            "score": round(s, 6),
            "momentum": m.get("price_change_percentage_24h", 0),
            "rank": m.get("market_cap_rank", 100),
            "memory_avg": round(sum(STATE["memory"].get(symbol, [s])) / len(STATE["memory"].get(symbol, [s])), 6)
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

    # equity learning simulation
    STATE["equity"] += sum(x["score"] for x in top10) / 20000

    STATE["history"].append(STATE["equity"])

    if len(STATE["history"]) > 50:
        STATE["history"].pop(0)

    return {
        "model": "V46_ADAPTIVE_QUANT_AI",
        "status": "OK",
        "regime": regime,
        "weights": STATE["weights"],
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "error": STATE["last_error"]
    }
