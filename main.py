from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()


# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

WEBHOOK_URL = "https://alpha-bot-1-6i93.onrender.com/webhook"


# =========================
# AUTO WEBHOOK FIXER
# =========================
def ensure_webhook():

    try:

        url = f"{BASE_URL}/getWebhookInfo"
        r = requests.get(url, timeout=10).json()

        current_url = r.get("result", {}).get("url", "")

        print("CURRENT WEBHOOK:", current_url)

        if current_url != WEBHOOK_URL:

            print("🔁 FIXING WEBHOOK...")

            set_url = f"{BASE_URL}/setWebhook?url={WEBHOOK_URL}"

            res = requests.get(set_url, timeout=10).json()

            print("SET WEBHOOK RESULT:", res)

    except Exception as e:

        print("WEBHOOK CHECK ERROR:", str(e))


# =========================
# STARTUP HOOK
# =========================
ensure_webhook()


# =========================
# BASIC HEALTH
# =========================
@app.get("/")
def home():

    return {
        "system": "V35 AUTO WEBHOOK FIXER ACTIVE",
        "status": "OK"
    }


@app.get("/update")
def update():

    return {
        "model": "V35_WEBHOOK_FIXER",
        "status": "RUNNING"
    }


# =========================
# SEND MESSAGE
# =========================
def send_message(chat_id, text):

    try:

        url = f"{BASE_URL}/sendMessage"

        requests.post(url, json={
            "chat_id": chat_id,
            "text": text
        }, timeout=10)

    except Exception as e:

        print("SEND ERROR:", str(e))


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:

        data = await request.json()

        print("DEBUG WEBHOOK:", data)

        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        # ---------------------
        # START
        # ---------------------
        if message == "/start":

            send_message(chat_id, "🚀 V35 BOT ONLINE (AUTO FIX ACTIVE)")

        # ---------------------
        # UPDATE
        # ---------------------
        elif message == "/update":

            send_message(chat_id, "📊 V35 SYSTEM WORKING")

        # ---------------------
        # UNKNOWN
        # ---------------------
        else:

            send_message(chat_id, "Commands: /start /update")

    except Exception as e:

        print("WEBHOOK ERROR:", str(e))

    return {"ok": True}
