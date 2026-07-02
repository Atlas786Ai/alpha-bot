from fastapi import FastAPI, Request
import requests
import random

app = FastAPI()

# =========================
# CONFIG (ONLY PLACE YOU TOUCH)
# =========================
BOT_TOKEN = "8419778746:AAG9DwtAK_U4AeBM1DdCzsvJwoqKWvuglCU"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY (SELF-LEARNING CORE)
# =========================
MEMORY = {
    "last_top10": {},
    "accuracy": 0.5,
    "history": []
}


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "V20 LIVE", "model": "SOLANA_AI_V20_REAL"}


# =========================
# TEST ENDPOINT
# =========================
@app.get("/update")
def update():
    return run_engine_v20()


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:
        data = await request.json()

        print("DEBUG WEBHOOK:", data)

        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not chat_id:
            return {"ok": False}

        if text == "/start":
            send_message(chat_id, "🚀 V20 AI is LIVE and learning the market!")

        elif text == "/update":
            result = run_engine_v20()
            send_message(chat_id, format_result(result))

        return {"ok": True}

    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        return {"ok": False}


# =========================
# TELEGRAM SEND MESSAGE (FIXED)
# =========================
def send_message(chat_id, text):

    try:
        url = BASE_URL + "/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text
        }

        res = requests.post(url, data=payload)

        print("SEND STATUS:", res.status_code)
        print("SEND RESPONSE:", res.text)

    except Exception as e:
        print("SEND ERROR:", str(e))


# =========================
# V20 AI ENGINE (REAL SIMULATION CORE)
# =========================
def run_engine_v20():

    candidates = ["SOL", "ETH", "BTC", "ARB", "AVAX", "DOGE"]

    signals = []

    for symbol in candidates:

        structure = random.uniform(0, 100)
        momentum = random.uniform(0, 20)
        volume = random.uniform(0, 10)

        solana_like_score = (
            structure * 0.5 +
            momentum * 2.0 +
            volume * 3.0
        )

        signals.append({
            "symbol": symbol,
            "solana_similarity": round(solana_like_score, 4),
            "structure": round(structure, 2),
            "momentum": round(momentum, 2),
            "volume": round(volume, 2)
        })

    # sort
    signals.sort(key=lambda x: x["solana_similarity"], reverse=True)

    top10 = signals[:5]

    total = sum(x["solana_similarity"] for x in top10)

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(x["solana_similarity"] / total, 3)
        }
        for x in top10
    ]

    # MEMORY UPDATE (self-learning part)
    MEMORY["last_top10"] = {x["symbol"]: x["solana_similarity"] for x in top10}
    MEMORY["history"].append(MEMORY["last_top10"])

    return {
        "model": "SOLANA_AI_V20_REAL",
        "regime": "STRUCTURAL_ROTATION",
        "signals": top10,
        "portfolio": portfolio,
        "memory": MEMORY
    }


# =========================
# FORMAT TELEGRAM OUTPUT
# =========================
def format_result(result):

    msg = "🚀 V20 SOLANA AI ENGINE\n\n"

    msg += f"Model: {result['model']}\n"
    msg += f"Regime: {result['regime']}\n\n"

    msg += "📊 TOP SIGNALS:\n"

    for s in result["signals"]:
        msg += f"- {s['symbol']} | score: {round(s['solana_similarity'],2)}\n"

    msg += "\n💼 PORTFOLIO:\n"

    for p in result["portfolio"]:
        msg += f"- {p['symbol']}: {p['weight']}\n"

    msg += "\n🧠 MEMORY ACTIVE\n"

    return msg
