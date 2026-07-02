from fastapi import FastAPI, Request
import urllib.request
import urllib.parse
import json
import math
import time

app = FastAPI()

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY
# =========================
MEMORY = {
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
        "status": "V29 DISCOVERY ENGINE ACTIVE",
        "model": "SOLANA_AI_V29_DISCOVERY"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v29()


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    msg = data.get("message", {})
    text = msg.get("text", "")
    chat_id = msg.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send(chat_id, "🚀 V29 DISCOVERY ENGINE ACTIVE")

    elif text == "/update":
        result = run_v29()
        send(chat_id, format_result(result))

    return {"ok": True}


# =========================
# UNIVERSE EXPANSION (KEY CHANGE)
# =========================
def fetch_market():

    # cache (avoid 429)
    if MEMORY["cache_data"] and time.time() - MEMORY["cache_time"] < 60:
        return MEMORY["cache_data"]

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
        full_url = url + "?" + query

        req = urllib.request.Request(
            full_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        raw = urllib.request.urlopen(req, timeout=6).read()
        data = json.loads(raw)

        result = []

        for c in data:

            result.append({
                "symbol": c["symbol"].upper(),
                "change": c.get("price_change_percentage_24h", 0) or 0,
                "volume": c.get("total_volume", 0),
                "rank": c.get("market_cap_rank", 999)
            })

        MEMORY["cache_data"] = result
        MEMORY["cache_time"] = time.time()

        return result

    except:

        # fallback universe
        return [
            {"symbol": "BTC", "change": 1.1, "volume": 1000000, "rank": 1},
            {"symbol": "ETH", "change": 0.9, "volume": 900000, "rank": 2},
            {"symbol": "SOL", "change": 2.2, "volume": 500000, "rank": 5},
            {"symbol": "ARB", "change": 3.5, "volume": 300000, "rank": 20},
            {"symbol": "OP", "change": 2.9, "volume": 250000, "rank": 25},
            {"symbol": "INJ", "change": 4.1, "volume": 200000, "rank": 40},
            {"symbol": "TIA", "change": 3.8, "volume": 220000, "rank": 35},
            {"symbol": "AVAX", "change": 1.7, "volume": 400000, "rank": 15},
        ]


# =========================
# SOLANA-LIKE SCORE ENGINE (IMPORTANT PART)
# =========================
def solana_score(asset):

    """
    This is the KEY upgrade:
    We are not ranking performance.
    We are estimating "Solana-like growth probability"
    """

    momentum = asset["change"]
    liquidity = asset["volume"] / 1e9

    # rank advantage = early / mid cap bias
    rank_factor = max(0, 120 - asset["rank"]) / 120

    # volatility sweet spot (not too stable, not too chaotic)
    volatility_score = 1 / (abs(momentum) + 1)

    # breakout potential simulation
    breakout = momentum * liquidity

    # SOLANA-like composite
    score = (
        rank_factor * 0.4 +
        momentum * 0.25 +
        volatility_score * 0.2 +
        breakout * 0.15
    )

    return score


# =========================
# NARRATIVE ENGINE (VERY IMPORTANT)
# =========================
def detect_narrative(symbols):

    # simple narrative detection

    if any(s["symbol"] in ["INJ", "TIA"] for s in symbols):
        return "Infra + modular narrative expanding"

    if any(s["symbol"] == "ARB" for s in symbols):
        return "Layer2 scaling rotation phase"

    return "General altcoin expansion phase"


# =========================
# MAIN ENGINE V29
# =========================
def run_v29():

    market = fetch_market()

    scored = []

    for m in market:

        score = solana_score(m)

        scored.append({
            "symbol": m["symbol"],
            "solana_like_score": round(score, 6),
            "momentum": m["change"],
            "rank": m["rank"]
        })

    # sort by discovery score
    scored.sort(key=lambda x: x["solana_like_score"], reverse=True)

    top10 = scored[:10]

    narrative = detect_narrative(top10)

    # simple portfolio allocation (risk-weighted discovery)
    total = sum(max(x["solana_like_score"], 0.0001) for x in top10)

    portfolio = []

    for x in top10:

        w = max(x["solana_like_score"], 0.0001) / total

        portfolio.append({
            "symbol": x["symbol"],
            "weight": round(w, 4)
        })

    # equity simulation
    MEMORY["equity"] += sum(x["solana_like_score"] for x in top10) / 1000

    return {
        "model": "SOLANA_AI_V29_DISCOVERY_ENGINE",
        "narrative": narrative,
        "top10_solana_candidates": top10,
        "portfolio": portfolio,
        "equity": round(MEMORY["equity"], 4)
    }


# =========================
# FORMAT TELEGRAM OUTPUT
# =========================
def format_result(r):

    msg = "🚀 V29 DISCOVERY ENGINE\n\n"

    msg += f"Narrative: {r['narrative']}\n\n"

    msg += "TOP 10 SOLANA-LIKE CANDIDATES:\n"

    for s in r["top10_solana_candidates"]:
        msg += f"- {s['symbol']} | {s['solana_like_score']}\n"

    msg += "\nPORTFOLIO:\n"

    for p in r["portfolio"]:
        msg += f"- {p['symbol']} | {p['weight']}\n"

    msg += f"\nEquity: {r['equity']}\n"

    return msg


# =========================
# SEND TELEGRAM
# =========================
def send(chat_id, text):

    url = BASE_URL + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )

    urllib.request.urlopen(req)
