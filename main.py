from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()


# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN is NOT SET in environment variables")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MODEL OUTPUT (V32)
# =========================
def get_model_output():
    return {
        "model": "SOLANA_AI_V32_UNIVERSE_DISCOVERY",
        "equity": 100.0,
        "status": "RUNNING_OK"
    }


# =========================
# TELEGRAM SEND MESSAGE
# =========================
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print("SEND STATUS:", response.status_code, response.text)

    except Exception as e:
        print("Telegram send error:", str(e))


# =========================
# WEBHOOK ENDPOINT
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:
        data = await request.json()
        print("DEBUG WEBHOOK:", data)

        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        # -------------------------
        # START COMMAND
        # -------------------------
        if message == "/start":

            send_message(chat_id, "🚀 Alpha Bot V32 is LIVE")

        # -------------------------
        # UPDATE COMMAND
        # -------------------------
        elif message == "/update":

            result = get_model_output()

            send_message(
                chat_id,
                f"📊 MODEL: {result['model']}\n💰 EQUITY: {result['equity']}\nSTATUS: {result['status']}"
            )

        else:

            send_message(chat_id, "❓ Unknown command")

    except Exception as e:
        print("WEBHOOK ERROR:", str(e))

    return {"ok": True}


# =========================
# ROOT
# =========================
@app.get("/")
def home():

    return {
        "system": "TELEGRAM V32 FIXED ACTIVE",
        "status": "OK"
    }


# =========================
# UPDATE TEST (browser)
# =========================
@app.get("/update")
def update():

    return get_model_output()
