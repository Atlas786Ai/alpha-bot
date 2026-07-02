from fastapi import FastAPI, Request
import requests

app = FastAPI()

BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# -------------------------
# HEALTH CHECK (Render)
# -------------------------
@app.get("/")
def home():
    return {"status": "Alpha running"}


# -------------------------
# UPDATE ENDPOINT (MANUAL TEST)
# -------------------------
@app.get("/update")
def update():

    # اینجا موقتاً تستی گذاشتیم
    result = {
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

    return result


# -------------------------
# TELEGRAM WEBHOOK (CRITICAL)
# -------------------------
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send_message(chat_id, "🚀 Alpha Bot is active")

    elif text == "/update":
        result = {
            "status": "running",
            "signals": ["BTC", "ETH"],
            "note": "test update response"
        }
        send_message(chat_id, str(result))

    return {"ok": True}


# -------------------------
# SEND MESSAGE FUNCTION
# -------------------------
def send_message(chat_id, text):

    url = f"{TELEGRAM_API}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": text
        })
    except Exception as e:
        print("Telegram error:", e)
