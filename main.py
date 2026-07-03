from fastapi import FastAPI, Request
import os
import requests
import time

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


# =========================
# SAFE MARKET FETCH
# =========================
def fetch_market():

    try:

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "false"
        }

        r = requests.get(COINGECKO_URL, params=params, timeout=10)

        data = r.json()

        if not isinstance(data, list):
            return []

        return data

    except:

        return []


# =========================
# SAFE SCORING
# =========================
def score_assets(data):

    scored = []

    for d in data:

        try:

            momentum = d.get("price_change_percentage_24h") or 0

            score = (momentum * 10)

            scored.append({
                "symbol": d.get("symbol", "UNK").upper(),
                "score": round(score, 3),
                "momentum": round(momentum, 3)
            })

        except:

            continue

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored


# =========================
# CORE ENGINE SAFE
# =========================
def ai_engine():

    market = fetch_market()

    scored = score_assets(market)

    # 🔥 SAFE fallback
    if len(scored) == 0:

        return {
            "model": "V36_SAFE",
            "status": "NO_DATA",
            "equity": 100.0,
            "top10": []
        }

    top10 = scored[:10]

    return {
        "model": "V36_SAFE",
        "status": "OK",
        "equity": 100.0,
        "top10": top10
    }


# =========================
# WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:

        data = await request.json()

        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        ai = ai_engine()

        if message == "/start":

            requests.post(BASE_URL + "/sendMessage", json={
                "chat_id": chat_id,
                "text": "🚀 V36 SAFE RUNNING"
            })

        elif message == "/update":

            text = "📊 V36 UPDATE\n\n"

            for x in ai["top10"]:

                text += f"{x['symbol']} | {x['score']}\n"

            if len(ai["top10"]) == 0:
                text += "\n⚠️ No data from API"

            requests.post(BASE_URL + "/sendMessage", json={
                "chat_id": chat_id,
                "text": text
            })

    except Exception as e:

        print("CRASH FIXED ERROR:", str(e))

    return {"ok": True}


# =========================
# TEST
# =========================
@app.get("/update")
def update():

    return ai_engine()
