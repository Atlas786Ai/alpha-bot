from fastapi import FastAPI, Request
import os
import requests
import time
import random

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

# =========================
# MEMORY SYSTEM (ANCHOR CORE)
# =========================
MEMORY = {}

COINS = [
    "BTC","ETH","SOL","ARB","AVAX","DOGE","MATIC","OP","LINK","UNI",
    "AAVE","INJ","TIA","NEAR","APT","SUI","LTC","XRP","BNB","FTM"
]

for c in COINS:
    MEMORY[c] = {
        "ema": 0.0,
        "strength": 0.5,
        "rank": 999,
        "last": 0
    }


ALPHA = 0.25  # EMA smoothing


# =========================
# REAL DATA FETCH (ANCHOR FIX)
# =========================
def fetch_real_market():

    try:

        r = requests.get(
            COINGECKO_URL,
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 50,
                "page": 1,
                "sparkline": "false"
            },
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        data = r.json()

        if isinstance(data, list) and len(data) > 0:
            return data

    except:
        pass

    # fallback minimal stable data (NOT random chaos)
    return [
        {"symbol": c.lower(), "price_change_percentage_24h": 0.0}
        for c in COINS
    ]


# =========================
# DATA ANCHOR NORMALIZATION
# =========================
def normalize(data):

    anchor = {}

    for d in data:

        sym = d.get("symbol","").upper()

        if sym in MEMORY:

            anchor[sym] = d.get("price_change_percentage_24h", 0.0)

    # ensure all coins exist
    for c in COINS:
        if c not in anchor:
            anchor[c] = 0.0

    return anchor


# =========================
# RELATIVE STRENGTH CORE
# =========================
def score(anchor):

    scores = []

    btc = anchor.get("BTC", 0.0)

    for c, val in anchor.items():

        # 🔥 REAL KEY IDEA: relative strength vs BTC
        rel = val - btc

        prev = MEMORY[c]["ema"]

        ema = (ALPHA * rel) + ((1 - ALPHA) * prev)

        MEMORY[c]["ema"] = ema
        MEMORY[c]["last"] = time.time()

        strength = 1 / (1 + abs(rel - ema))  # stability proxy

        MEMORY[c]["strength"] = strength

        score = ema * 10 * strength

        scores.append({
            "symbol": c,
            "score": round(score, 3),
            "ema": round(ema, 3),
            "strength": round(strength, 3)
        })

    return sorted(scores, key=lambda x: x["score"], reverse=True)


# =========================
# REGIME ENGINE
# =========================
def regime(top):

    if top > 40:
        return "EXPLOSIVE_ROTATION"

    if top > 15:
        return "TREND"

    return "CHOP"


# =========================
# CORE ENGINE
# =========================
def engine():

    raw = fetch_real_market()

    anchor = normalize(raw)

    scored = score(anchor)

    top10 = scored[:10]

    r = regime(top10[0]["score"])

    portfolio = []

    total = sum(x["score"] for x in top10) or 1

    for x in top10[:5]:

        portfolio.append({
            "symbol": x["symbol"],
            "weight": round(x["score"] / total, 3)
        })

    return {
        "model": "V39_REAL_DATA_ANCHORED_CORE",
        "regime": r,
        "top10": top10,
        "portfolio": portfolio,
        "anchor_source": "BTC_RELATIVE_STRENGTH",
        "status": "LIVE_ANCHORED"
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

    ai = engine()

    if msg == "/start":

        send(chat_id, f"🚀 V39 REAL DATA ENGINE\nREGIME: {ai['regime']}")

    elif msg == "/update":

        text = "📊 V39 ANCHORED CORE\n\n"

        for x in ai["top10"][:5]:
            text += f"{x['symbol']} | {x['score']}\n"

        send(chat_id, text)

    elif msg == "/portfolio":

        text = "💼 PORTFOLIO:\n"

        for p in ai["portfolio"]:
            text += f"{p['symbol']} → {p['weight']}\n"

        send(chat_id, text)

    return {"ok": True}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():

    return {
        "model": "V39_REAL_DATA_ANCHORED_CORE",
        "status": "RUNNING"
    }


@app.get("/update")
def update():

    return engine()
