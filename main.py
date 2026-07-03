from fastapi import FastAPI, Request
import os
import requests
import random
import time

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

COINS = [
    "BTC","ETH","SOL","ARB","AVAX","DOGE","MATIC","OP","LINK","UNI",
    "AAVE","INJ","TIA","NEAR","APT","SUI","LTC","XRP","BNB","FTM"
]


# =========================
# MEMORY STORE (REAL CORE)
# =========================
MEMORY = {
    coin: {
        "ema": 0,
        "confidence": 0.5,
        "rank": 999,
        "last_seen": time.time()
    }
    for coin in COINS
}

ALPHA = 0.2  # EMA smoothing factor


# =========================
# MARKET SIM / LIVE HYBRID
# =========================
def market_data():

    return {
        c: random.uniform(-3, 6) for c in COINS
    }


# =========================
# EMA UPDATE ENGINE
# =========================
def update_memory(market):

    scored = []

    for coin, momentum in market.items():

        prev = MEMORY[coin]["ema"]

        ema = (ALPHA * momentum) + ((1 - ALPHA) * prev)

        # confidence grows with stability
        diff = abs(ema - prev)

        confidence = max(0.1, min(1.0, MEMORY[coin]["confidence"] + (0.05 if diff < 1 else -0.05)))

        MEMORY[coin]["ema"] = ema
        MEMORY[coin]["confidence"] = confidence
        MEMORY[coin]["last_seen"] = time.time()

        score = ema * confidence * 10

        scored.append({
            "symbol": coin,
            "score": round(score, 3),
            "ema": round(ema, 3),
            "confidence": round(confidence, 3)
        })

    return scored


# =========================
# STABILITY SORT (ANTI-NOISE)
# =========================
def stable_rank(scored):

    scored.sort(key=lambda x: x["score"], reverse=True)

    for i, s in enumerate(scored):

        MEMORY[s["symbol"]]["rank"] = i + 1

    return scored


# =========================
# REGIME DETECTOR
# =========================
def detect_regime(top):

    if top > 50:
        return "EXPLOSIVE_ROTATION"

    if top > 20:
        return "TREND"

    return "CHOP"


# =========================
# AI CORE
# =========================
def ai_engine():

    market = market_data()

    scored = update_memory(market)

    ranked = stable_rank(scored)

    top10 = ranked[:10]

    regime = detect_regime(top10[0]["score"])

    portfolio = []

    total = sum(x["score"] for x in top10) or 1

    for x in top10[:5]:

        portfolio.append({
            "symbol": x["symbol"],
            "weight": round(x["score"] / total, 3)
        })

    return {
        "model": "V38_MEMORY_QUANT_CORE",
        "regime": regime,
        "top10": top10,
        "portfolio": portfolio,
        "memory": MEMORY
    }


# =========================
# TELEGRAM
# =========================
def send(chat_id, text):

    try:
        requests.post(BASE_URL + "/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        }, timeout=8)
    except:
        pass


# =========================
# WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(req: Request):

    data = await req.json()

    msg = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    ai = ai_engine()

    if msg == "/start":

        send(chat_id, f"🚀 V38 MEMORY CORE ACTIVE\nREGIME: {ai['regime']}")

    elif msg == "/update":

        text = "📊 V38 QUANT CORE\n\n"

        for x in ai["top10"][:5]:

            text += f"{x['symbol']} | {x['score']} | conf:{x['confidence']}\n"

        send(chat_id, text)

    elif msg == "/memory":

        top = sorted(ai["memory"].items(), key=lambda x: x[1]["ema"], reverse=True)[:5]

        text = "🧠 MEMORY TOP 5:\n\n"

        for k, v in top:

            text += f"{k} | EMA:{v['ema']:.2f} | RANK:{v['rank']}\n"

        send(chat_id, text)

    return {"ok": True}


# =========================
# TEST
# =========================
@app.get("/update")
def update():

    return ai_engine()
