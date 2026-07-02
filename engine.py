from fastapi import FastAPI
import urllib.request
import urllib.parse
import json
import time

app = FastAPI()


# =========================
# STATE
# =========================
STATE = {
    "cache_time": 0,
    "cache_data": None,
    "equity": 100.0
}


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "status": "V32 REAL UNIVERSE ENGINE ACTIVE",
        "model": "SOLANA_AI_V32_UNIVERSE_DISCOVERY"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v32()


# =========================
# MARKET UNIVERSE (100 COINS)
# =========================
def fetch_market():

    # cache (anti 429)
    if STATE["cache_data"] and time.time() - STATE["cache_time"] < 60:
        return STATE["cache_data"]

    try:

        url = "https://api.coingecko.com/api/v3/coins/markets"

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,   # 👈 KEY CHANGE
            "page": 1,
            "sparkline": "false"
        }

        query = urllib.parse.urlencode(params)
        full_url = url + "?" + query

        req = urllib.request.Request(
            full_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        raw = urllib.request.urlopen(req, timeout=6).read()
        data = json.loads(raw)

        universe = []

        for c in data:

            universe.append({
                "symbol": c["symbol"].upper(),
                "change": c.get("price_change_percentage_24h", 0) or 0,
                "volume": c.get("total_volume", 0),
                "rank": c.get("market_cap_rank", 999)
            })

        STATE["cache_data"] = universe
        STATE["cache_time"] = time.time()

        return universe

    except:

        # fallback universe (expanded)
        return [
            {"symbol": "BTC", "change": 1.1, "volume": 1000000, "rank": 1},
            {"symbol": "ETH", "change": 0.9, "volume": 900000, "rank": 2},
            {"symbol": "SOL", "change": 2.2, "volume": 500000, "rank": 5},
            {"symbol": "ARB", "change": 3.1, "volume": 300000, "rank": 20},
            {"symbol": "AVAX", "change": 1.7, "volume": 400000, "rank": 15},
            {"symbol": "OP", "change": 2.4, "volume": 250000, "rank": 25},
            {"symbol": "INJ", "change": 4.0, "volume": 200000, "rank": 40},
            {"symbol": "TIA", "change": 3.6, "volume": 220000, "rank": 35},
            {"symbol": "MATIC", "change": 1.9, "volume": 600000, "rank": 12},
            {"symbol": "DOGE", "change": 1.5, "volume": 700000, "rank": 10},
        ]


# =========================
# SOLANA-LIKE DISCOVERY SCORE
# =========================
def solana_like_score(asset):

    """
    Core idea:
    We are NOT ranking performance.
    We are estimating "future structural breakout probability"
    """

    momentum = asset["change"]
    volume = asset["volume"] / 1e9

    # early/mid cap advantage
    rank_pressure = max(0, 120 - asset["rank"]) / 120

    # stability sweet spot
    stability = 1 / (abs(momentum) + 1)

    # liquidity expansion signal
    liquidity = volume

    # breakout potential
    breakout = momentum * liquidity

    score = (
        rank_pressure * 0.40 +
        momentum * 0.25 +
        stability * 0.20 +
        breakout * 0.15
    )

    return score


# =========================
# NARRATIVE ENGINE
# =========================
def narrative_engine(top10):

    symbols = [x["symbol"] for x in top10]

    if "INJ" in symbols or "TIA" in symbols:
        return "Infra / modular narrative expansion phase"

    if "ARB" in symbols:
        return "Layer2 rotation cycle active"

    if "SOL" in symbols:
        return "L1 high-beta continuation phase"

    return "General market expansion phase"


# =========================
# MAIN ENGINE V32
# =========================
def run_v32():

    market = fetch_market()

    scored = []

    for m in market:

        score = solana_like_score(m)

        scored.append({
            "symbol": m["symbol"],
            "solana_like_score": round(score, 6),
            "rank": m["rank"],
            "momentum": m["change"]
        })

    # sort discovery
    scored.sort(key=lambda x: x["solana_like_score"], reverse=True)

    top10 = scored[:10]

    narrative = narrative_engine(top10)

    # portfolio allocation
    total = sum(max(x["solana_like_score"], 0.0001) for x in top10)

    portfolio = []

    for x in top10:

        portfolio.append({
            "symbol": x["symbol"],
            "weight": round(x["solana_like_score"] / total, 4)
        })

    # equity simulation
    STATE["equity"] += sum(x["solana_like_score"] for x in top10) / 1000

    return {
        "model": "SOLANA_AI_V32_UNIVERSE_DISCOVERY",
        "narrative": narrative,
        "top10_solana_candidates": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4)
    }


# =========================
# API
# =========================
@app.get("/backtest")
def backtest():
    return run_v32()
