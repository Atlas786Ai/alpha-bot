from fastapi import FastAPI, Request
import urllib.request
import json
import random
import math

app = FastAPI()

# =========================
# CONFIG
# =========================
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY (ML CORE)
# =========================
MEMORY = {
    "weights": {
        "structure": 0.35,
        "momentum": 0.35,
        "volatility": 0.20,
        "volume": 0.10
    },
    "history": [],
    "accuracy": []
}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {
        "status": "V24 ML CORE ACTIVE",
        "model": "SOLANA_AI_V24_MACHINE_LEARNING"
    }


# =========================
# UPDATE ENDPOINT
# =========================
@app.get("/update")
def update():
    return run_v24_ml()


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
        send_message(chat_id, "🚀 V24 ML CORE ACTIVE")

    elif text == "/update":
        result = run_v24_ml()
        send_message(chat_id, format_result(result))

    return {"ok": True}


# =========================
# LIVE MARKET (CoinGecko)
# =========================
def fetch_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 15,
        "page": 1,
        "sparkline": False
    }

    query = urllib.parse.urlencode(params)
    full_url = url + "?" + query

    response = urllib.request.urlopen(full_url, timeout=5)
    data = json.loads(response.read())

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
# ML SCORING ENGINE
# =========================
def ml_score(asset):

    w = MEMORY["weights"]

    structure = max(0, 100 - asset["rank"])
    momentum = asset["change"]
    volatility = abs(asset["change"]) / 10
    volume = asset["volume"] / 1e9

    score = (
        structure * w["structure"] +
        momentum * w["momentum"] +
        (1 / (volatility + 0.01)) * w["volatility"] +
        volume * w["volume"]
    )

    return score


# =========================
# MAIN ENGINE
# =========================
def run_v24_ml():

    market = fetch_market()

    signals = []

    for m in market:

        score = ml_score(m)

        signals.append({
            "symbol": m["symbol"],
            "score": round(score, 4),
            "momentum": m["change"],
            "rank": m["rank"]
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top5 = signals[:5]

    # store history (for learning)
    MEMORY["history"].append(top5)

    # run ML update
    update_weights(top5)

    return {
        "model": "SOLANA_AI_V24_ML_CORE",
        "signals": top5,
        "weights": MEMORY["weights"],
        "history_size": len(MEMORY["history"])
    }


# =========================
# MACHINE LEARNING UPDATE (KEY PART)
# =========================
def update_weights(top5):

    # simulate reward signal (real future would be backtest return)
    reward = sum([x["score"] for x in top5]) / len(top5)

    # error signal
    error = 100 - reward

    # adaptive learning rate
    lr = 0.01

    # gradient-like update (simple but real ML concept)
    if error > 0:

        MEMORY["weights"]["structure"] += lr * (error * 0.01)
        MEMORY["weights"]["momentum"] += lr * (error * 0.02)
        MEMORY["weights"]["volatility"] -= lr * (error * 0.01)
        MEMORY["weights"]["volume"] += lr * (error * 0.005)

    # normalize weights
    total = sum(MEMORY["weights"].values())

    for k in MEMORY["weights"]:
        MEMORY["weights"][k] /= total

    # store accuracy proxy
    MEMORY["accuracy"].append(1 / (1 + abs(error)))


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

    urllib.request.urlopen(req)


# =========================
# FORMAT MESSAGE
# =========================
def format_result(result):

    msg = "🚀 V24 ML CORE\n\n"

    msg += f"Model: {result['model']}\n"
    msg += f"History: {result['history_size']}\n\n"

    msg += "📊 TOP SIGNALS:\n"

    for s in result["signals"]:
        msg += f"- {s['symbol']} | score: {s['score']}\n"

    msg += "\n🧠 WEIGHTS:\n"

    for k, v in result["weights"].items():
        msg += f"- {k}: {round(v,4)}\n"

    return msg
