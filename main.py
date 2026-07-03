from fastapi import FastAPI
import requests
import time
import math
import random

app = FastAPI()

# =========================
# STATE (BACKTEST CORE)
# =========================
STATE = {
    "equity": 100.0,
    "cache": None,
    "cache_time": 0,
    "last_error": None,

    # 🔥 learning memory
    "memory": {},

    # 🔥 backtest stats
    "stats": {}
}

CACHE_TTL = 60


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "model": "ATLAS_CANONICAL_V4",
        "status": "BACKTEST_INTELLIGENCE_ACTIVE"
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
            "model": "ATLAS_CANONICAL_V4",
            "status": "SAFE_ERROR_HANDLED",
            "error": str(e),
            "equity": STATE["equity"]
        }


# =========================
# SAFE DATA FETCH
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

    except:
        pass

    # fallback (stable universe)
    return [
        {"symbol": "BTC", "price_change_percentage_24h": 1.2, "total_volume": 1000000, "market_cap_rank": 1},
        {"symbol": "ETH", "price_change_percentage_24h": 0.9, "total_volume": 900000, "market_cap_rank": 2},
        {"symbol": "SOL", "price_change_percentage_24h": 2.5, "total_volume": 700000, "market_cap_rank": 5},
        {"symbol": "ARB", "price_change_percentage_24h": 3.2, "total_volume": 300000, "market_cap_rank": 20},
        {"symbol": "AVAX", "price_change_percentage_24h": 1.6, "total_volume": 500000, "market_cap_rank": 10},
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
# BASE SCORE ENGINE
# =========================
def score(asset):

    c = asset["change"]
    v = asset["volume"]
    r = asset["rank"]

    momentum = c / 10
    volume_score = math.log1p(v)
    rank_score = 1 - min(r / 100, 1)

    stability = 1 / (1 + abs(momentum))

    return momentum * 0.3 + volume_score * 0.25 + rank_score * 0.25 + stability * 0.2


# =========================
# BACKTEST SIMULATOR (V4 CORE)
# =========================
def simulate_signal(symbol, score_value):

    if symbol not in STATE["stats"]:
        STATE["stats"][symbol] = {
            "wins": 0,
            "losses": 0,
            "trials": 0,
            "drawdown": 0.0
        }

    s = STATE["stats"][symbol]

    # synthetic outcome simulation (proxy backtest logic)
    success_prob = 0.5 + (score_value / 10)

    outcome = random.random() < success_prob

    s["trials"] += 1

    if outcome:
        s["wins"] += 1
    else:
        s["losses"] += 1

    win_rate = s["wins"] / s["trials"]

    # drawdown approximation
    s["drawdown"] = max(s["drawdown"], (1 - win_rate) * 100)

    return win_rate


# =========================
# FINAL SYSTEM
# =========================
def run_system():

    raw = fetch_market()

    market = [normalize(x) for x in raw]

    results = []

    for x in market:

        base = score(x)

        symbol = x["symbol"]

        win_rate = simulate_signal(symbol, base)

        # 🔥 final hybrid score (signal + reliability)
        final_score = base * (0.7 + win_rate * 0.3)

        results.append({
            "symbol": symbol,
            "score": round(final_score, 6),
            "base_score": round(base, 6),
            "win_rate": round(win_rate, 4),
            "rank": x["rank"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    top10 = results[:10]

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
        "model": "ATLAS_CANONICAL_V4",
        "status": "BACKTEST_ACTIVE",
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "symbols_tracked": len(STATE["stats"])
    }
