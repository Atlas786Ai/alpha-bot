from fastapi import FastAPI, Request
import random
import urllib.request
import json

app = FastAPI()

# =========================
# CONFIG
# =========================
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY (SELF-LEARNING)
# =========================
MEMORY = {
    "mode_used": [],
    "last_accuracy": 0.5,
    "fail_count": 0
}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {
        "status": "V23 HYBRID LIVE",
        "mode": "AUTO SWITCH ENABLED"
    }


# =========================
# MAIN UPDATE ENDPOINT
# =========================
@app.get("/update")
def update():

    data = run_hybrid_engine()
    return data


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send_message(chat_id, "🚀 V23 HYBRID AI ACTIVE")

    elif text == "/update":
        result = run_hybrid_engine()
        send_message(chat_id, format_result(result))

    return {"ok": True}


# =========================
# HYBRID ENGINE (LIVE + FALLBACK)
# =========================
def run_hybrid_engine():

    try:
        data = fetch_live_market()

        MEMORY["mode_used"].append("LIVE")

        return build_ai_output(data, mode="LIVE")

    except Exception as e:

        print("LIVE FAILED → switching fallback:", e)

        MEMORY["fail_count"] += 1
        MEMORY["mode_used"].append("FALLBACK")

        data = generate_fallback_market()

        return build_ai_output(data, mode="FALLBACK")


# =========================
# LIVE DATA (CoinGecko)
# =========================
def fetch_live_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }

    query = urllib.parse.urlencode(params)
    full_url = url + "?" + query

    response = urllib.request.urlopen(full_url, timeout=5)
    raw = response.read()
    data = json.loads(raw)

    market = []

    for c in data:

        market.append({
            "symbol": c["symbol"].upper(),
            "change": c.get("price_change_percentage_24h", 0) or 0,
            "rank": c.get("market_cap_rank", 999),
            "volume": c.get("total_volume", 0)
        })

    return market


# =========================
# FALLBACK DATA
# =========================
def generate_fallback_market():

    symbols = ["SOL", "ETH", "BTC", "ARB", "AVAX", "DOGE"]

    market = []

    for s in symbols:

        market.append({
            "symbol": s,
            "change": random.uniform(-5, 5),
            "rank": random.randint(1, 100),
            "volume": random.uniform(1e8, 1e9)
        })

    return market


# =========================
# AI CORE SCORING
# =========================
def build_ai_output(market, mode="LIVE"):

    signals = []

    for m in market:

        structure = max(0, 100 - m["rank"])
        momentum = m["change"]
        volatility = abs(m["change"]) / 10
        volume = m["volume"] / 1e9

        score = (
            structure * 0.4 +
            momentum * 2.2 +
            (1 / (volatility + 0.01)) * 0.8 +
            volume * 0.6
        )

        signals.append({
            "symbol": m["symbol"],
            "score": round(score, 4),
            "momentum": round(momentum, 3),
            "rank": m["rank"]
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top5 = signals[:5]

    total = sum(x["score"] for x in top5)

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(x["score"] / total, 3)
        }
        for x in top5
    ]

    return {
        "model": "SOLANA_AI_V23_HYBRID",
        "mode": mode,
        "fail_count": MEMORY["fail_count"],
        "signals": top5,
        "portfolio": portfolio
    }


# =========================
# TELEGRAM SEND
# =========================
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print("SEND ERROR:", e)


# =========================
# FORMAT RESULT
# =========================
def format_result(result):

    msg = "🚀 V23 HYBRID AI\n\n"

    msg += f"Mode: {result['mode']}\n"
    msg += f"Fail Count: {result['fail_count']}\n\n"

    msg += "📊 TOP SIGNALS:\n"

    for s in result["signals"]:
        msg += f"- {s['symbol']} | score: {s['score']}\n"

    msg += "\n💼 PORTFOLIO:\n"

    for p in result["portfolio"]:
        msg += f"- {p['symbol']}: {p['weight']}\n"

    return msg
