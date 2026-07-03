from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# HEALTH CHECK (ROOT)
# =========================
@app.get("/")
def home():
    return {"status": "OK", "system": "RUNNING"}


# =========================
# TEST UPDATE (BROWSER)
# =========================
@app.get("/update")
def update():
    return {"model": "V34_FIXED", "status": "OK"}


# =========================
# SEND MESSAGE
# =========================
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("DEBUG:", data)

    message = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    if message == "/start":

        send_message(chat_id, "🚀 Bot is ONLINE")

    elif message == "/update":

        send_message(chat_id, "📊 V34 UPDATE WORKING")

    else:

        send_message(chat_id, "Unknown command")

    return {"ok": True}
