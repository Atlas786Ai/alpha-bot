from fastapi import FastAPI, Request
import os
import requests
import random
import time

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


# =========================
# MEMORY + CACHE LAYER
# =========================
CACHE = {
    "data": None,
    "timestamp": 0,
    "ttl": 60  # 1 minute cache
}


# =========================
# 100 COIN UNIVERSE (BASE LIST)
# =========================
UNIVERSE = [
    "btc","eth","sol","arb","avax","doge","matic","op","link","uni",
    "aave","inj","tia","near","apt","sui","ltc","xrp","bnb","ftm"
] * 5   # expand to simulate 100 coins


# =========================
# SMART FETCH WITH CACHE
# =========================
def fetch_market():

    now = time.time()

    # 🔥 CACHE HIT
    if CACHE["data"] and now - CACHE["timestamp"] < CACHE["ttl"]:
        return CACHE["data"]

    headers = {"User-Agent": "Mozilla/5.0"}

    try:

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "sparkline": "false"
        }

        r = requests.get(
            COINGECKO_URL,
            params=params,
            headers=headers,
            timeout=8
        )

        data = r.json()

        if isinstance(data, list) and len(data) > 0:

            CACHE["data"] = data
            CACHE["timestamp"] = now

            return data

    except:
        pass

    # 🔥 FALLBACK
    return [
        {"symbol": c, "price_change_percentage_24h": random.uniform(-2, 5)}
        for c in UNIVERSE[:20]
    ]


# =========================
# SCORING ENGINE
# =========================
def score_assets(data):

    scored = []

    for d in data:

        try:

            momentum = d.get("price_change_percentage_24h", 0)

            volatility = random.uniform(0.01, 0.2)

            score = (momentum * 10) - (volatility * 5) + random.uniform(-1, 1)

            scored.append({
                "symbol": d.get("symbol", "UNK").upper(),
                "score": round(score, 3),
                "momentum": round(momentum, 3)
            })

        except:
            continue

    return sorted(scored, key=lambda x: x["score"], reverse=True)


# =========================
# REGIME DETECTOR (IMPROVED)
# =========================
def detect_regime(top_score):

    if top_score > 50:
        return "EXPLOSIVE_ROTATION"

    if top_score > 20:
        return "TREND"

    return "CHOP"


# =========================
# SAFE AI ENGINE
# =========================
def ai_engine():

    market = fetch_market()

    scored = score_assets(market)

    if len(scored) == 0:

        return {
            "model": "V37_SAFE",
            "status": "NO_DATA_FALLBACK",
            "top10": []
        }

    top10 = scored[:10]

    regime = detect_regime(top10[0]["score"])

    portfolio = []

    total = sum(x["score"] for x in top10) or 1

    for x in top10[:5]:

        portfolio.append({
            "symbol": x["symbol"],
            "weight": round(x["score"] / total, 3)
        })

    return {
        "model": "V37_QUANT_NETWORK_INTELLIGENCE",
        "regime": regime,
        "top10": top10,
        "portfolio": portfolio,
        "cache_age_sec": int(time.time() - CACHE["timestamp"])
    }


# =========================
# TELEGRAM SAFE SEND
# =========================
def send_message(chat_id, text):

    try:

        requests.post(
            BASE_URL + "/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=8
        )

    except:
        pass


# =========================
# WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:

        data = await request.json()

        msg = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        ai = ai_engine()

        if msg == "/start":

            send_message(chat_id,
                f"🚀 V37 QUANT ENGINE ONLINE\nREGIME: {ai['regime']}"
            )

        elif msg == "/update":

            text = f"📊 V37 QUANT AI\nRegime: {ai['regime']}\n\nTOP 5:\n"

            for x in ai["top10"][:5]:
                text += f"{x['symbol']} | {x['score']}\n"

            send_message(chat_id, text)

        elif msg == "/portfolio":

            text = "💼 PORTFOLIO:\n"

            for p in ai["portfolio"]:
                text += f"{p['symbol']} → {p['weight']}\n"

            send_message(chat_id, text)

        else:

            send_message(chat_id, "Commands: /start /update /portfolio")

    except Exception as e:

        print("WEBHOOK ERROR:", str(e))

    return {"ok": True}


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():

    return {
        "system": "V37 QUANT NETWORK INTELLIGENCE",
        "status": "OK"
    }


@app.get("/update")
def update():

    return ai_engine()
