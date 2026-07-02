from fastapi import FastAPI, Request
import requests

app = FastAPI()

BOT_TOKEN = "YOUR_BOT_TOKEN"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.get("/")
def home():
    return {"status": "Alpha running"}


# =========================
# TELEGRAM WEBHOOK (FIXED)
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    try:
        data = await request.json()
        print("DEBUG WEBHOOK:", data)

        message = data.get("message", {})
        text = message.get("text")
        chat_id = message.get("chat", {}).get("id")

        if not chat_id:
            return {"ok": False}

        if text == "/start":
            send(chat_id, "🚀 Alpha bot is live")

        elif text == "/update":
            result = run_engine()
            send(chat_id, str(result))

        return {"ok": True}

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return {"ok": False}


# =========================
# TEST ENDPOINT
# =========================
@app.get("/update")
def update():
    return {
        "model": "ALPHA_V1_STABLE",
        "regime": "TEST_MODE",
        "signals": [{"symbol": "BTC", "score": 1.0}],
        "portfolio": [{"symbol": "BTC", "weight": 1.0}]
    }


# =========================
# SEND MESSAGE
# =========================
def send(chat_id, text):
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
    except Exception as e:
        print("SEND ERROR:", e)


# =========================
# DUMMY ENGINE
# =========================
def run_engine():
    return {
        "regime": "LIVE",
        "signals": ["SOL", "ETH", "BTC"],
        "portfolio": [{"symbol": "SOL", "weight": 0.5}]
    }
