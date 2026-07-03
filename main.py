from fastapi import FastAPI, Request
import os
import requests
import traceback

app = FastAPI()


# =========================
# ENV CONFIG
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# AI ENGINE V33
# =========================
def ai_engine():

    return {
        "model": "SOLANA_AI_V33_TELEGRAM_AI_CORE",
        "regime": "EXPLOSIVE_ROTATION",
        "equity": 100.0,
        "signals": [
            {"symbol": "ARB", "score": 42.8, "momentum": 1.9},
            {"symbol": "SOL", "score": 39.2, "momentum": 2.4},
            {"symbol": "ETH", "score": 28.1, "momentum": 1.1},
            {"symbol": "AVAX", "score": 24.6, "momentum": 0.9},
            {"symbol": "DOGE", "score": 18.3, "momentum": 1.7}
        ]
    }


# =========================
# TELEGRAM SEND (SAFE)
# =========================
def send_message(chat_id, text):

    try:
        url = f"{BASE_URL}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text
        }

        r = requests.post(url, json=payload, timeout=10)

        print("SEND STATUS:", r.status_code, r.text)

    except Exception as e:
        print("SEND ERROR:", str(e))


# =========================
# AUTO DEBUG ENGINE
# =========================
def debug_engine(error):

    err = str(error)

    fixes = []

    if "IndentationError" in err:
        fixes.append("Fix indentation (spaces/tabs mismatch)")

    if "KeyError" in err:
        fixes.append("Missing dictionary key in request")

    if "404" in err:
        fixes.append("Fix Telegram API URL or webhook route")

    if "401" in err:
        fixes.append("Check BOT TOKEN")

    if len(fixes) == 0:
        fixes.append("Unknown error - manual inspection required")

    return fixes


# =========================
# WEBHOOK (MAIN TELEGRAM HANDLER)
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:

        data = await request.json()
        print("DEBUG:", data)

        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        # -------------------------
        # START COMMAND
        # -------------------------
        if message == "/start":

            send_message(chat_id, "🚀 V33 AI BOT IS LIVE")

        # -------------------------
        # UPDATE COMMAND (AI RESPONSE)
        # -------------------------
        elif message == "/update":

            ai = ai_engine()

            text = f"""
🤖 MODEL: {ai['model']}
📊 REGIME: {ai['regime']}
💰 EQUITY: {ai['equity']}

📈 SIGNALS:
"""

            for s in ai["signals"]:
                text += f"\n- {s['symbol']} | score: {s['score']} | mom: {s['momentum']}"

            send_message(chat_id, text)

        else:

            send_message(chat_id, "Unknown command. Use /start or /update")

    except Exception as e:

        print("WEBHOOK CRASH:", str(e))

        fixes = debug_engine(e)

        print("AUTO FIX SUGGESTIONS:", fixes)

    return {"ok": True}


# =========================
# ROOT
# =========================
@app.get("/")
def home():

    return {
        "system": "V33 TELEGRAM AI ACTIVE",
        "status": "OK"
    }


# =========================
# BROWSER TEST UPDATE
# =========================
@app.get("/update")
def update():

    return ai_engine()
