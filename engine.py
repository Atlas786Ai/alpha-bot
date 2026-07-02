from fastapi import FastAPI, Request
import random

app = FastAPI()


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {
        "status": "ALPHA V22 FALLBACK LIVE",
        "mode": "NO_EXTERNAL_DEPENDENCY"
    }


# =========================
# SIMPLE AI ENGINE (NO INTERNET)
# =========================
def run_fallback_engine():

    symbols = ["SOL", "ETH", "BTC", "ARB", "AVAX", "DOGE"]

    signals = []

    for s in symbols:

        # ساختار مصنوعی ولی پایدار
        base_score = random.uniform(20, 100)

        momentum = random.uniform(0, 15)

        volatility = random.uniform(0.1, 1.0)

        # سولانا-لایک امتیاز ساده ولی پایدار
        score = base_score + (momentum * 2) + (1 / (volatility + 0.01)) * 0.5

        signals.append({
            "symbol": s,
            "score": round(score, 4),
            "momentum": round(momentum, 2),
            "volatility": round(volatility, 3)
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
        "model": "ALPHA_V22_FALLBACK_CORE",
        "regime": "STABLE_SIMULATION",
        "signals": top5,
        "portfolio": portfolio
    }


# =========================
# UPDATE ENDPOINT
# =========================
@app.get("/update")
def update():
    return run_fallback_engine()


# =========================
# TELEGRAM WEBHOOK (SAFE)
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("DEBUG:", data)

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send_message(chat_id, "🚀 ALPHA V22 FALLBACK ACTIVE")

    elif text == "/update":
        result = run_fallback_engine()
        send_message(chat_id, format_message(result))

    return {"ok": True}


# =========================
# TELEGRAM SEND (NO REQUESTS LIB)
# =========================
import urllib.request
import json

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


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
# FORMAT MESSAGE
# =========================
def format_message(result):

    msg = "🚀 ALPHA V22 FALLBACK\n\n"

    msg += f"Model: {result['model']}\n"
    msg += f"Regime: {result['regime']}\n\n"

    msg += "📊 TOP SIGNALS:\n"

    for s in result["signals"]:
        msg += f"- {s['symbol']} | score: {s['score']}\n"

    msg += "\n💼 PORTFOLIO:\n"

    for p in result["portfolio"]:
        msg += f"- {p['symbol']}: {p['weight']}\n"

    return msg
