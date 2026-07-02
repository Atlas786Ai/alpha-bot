from fastapi import FastAPI, Request
import requests

app = FastAPI()

# =========================
# CONFIG (PUT YOUR NEW TOKEN HERE)
# =========================
BOT_TOKEN = "8419778746:AAG9DwtAK_U4AeBM1DdCzsvJwoqKWvuglCU"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "Alpha running"}


# =========================
# TEST ENDPOINT
# =========================
@app.get("/update")
def update():

    return {
        "model": "ALPHA_V1_STABLE",
        "regime": "TEST_MODE",
        "signals": [
            {"symbol": "BTC", "score": 1.0},
            {"symbol": "ETH", "score": 0.9}
        ],
        "portfolio": [
            {"symbol": "BTC", "weight": 0.55},
            {"symbol": "ETH", "weight": 0.45}
        ]
    }


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("DEBUG WEBHOOK:", data)

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send_message(chat_id, "🚀 Alpha Bot is LIVE!")

    elif text == "/update":
        result = update()
        send_message(chat_id, str(result))

    return {"ok": True}


# =========================
# SEND MESSAGE (STABLE)
# =========================
def send_message(chat_id, text):

    url = BASE_URL + "/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    res = requests.post(url, data=payload)

    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)
