from fastapi import FastAPI, Request
import requests

app = FastAPI()

BOT_TOKEN = "YOUR_BOT_TOKEN"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.get("/")
def home():
    return {"status": "Alpha running"}


# =========================
# WEBHOOK FIXED (ROBUST)
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

    # ---------------------
    # START COMMAND
    # ---------------------
    if text == "/start":
        send_message(chat_id, "🚀 Alpha Bot is LIVE and connected!")

    # ---------------------
    # UPDATE COMMAND
    # ---------------------
    elif text == "/update":

        result = run_engine()

        send_message(chat_id, format_result(result))

    return {"ok": True}


# =========================
# SAFE SEND MESSAGE (FIXED)
# =========================
def send_message(chat_id, text):

    try:
        url = f"{API}/sendMessage"

        res = requests.post(url, json={
            "chat_id": chat_id,
            "text": text
        })

        print("SEND STATUS:", res.status_code, res.text)

    except Exception as e:
        print("SEND ERROR:", str(e))


# =========================
# ENGINE (TEST OR AI)
# =========================
def run_engine():

    return {
        "model": "ALPHA_V1_LIVE",
        "regime": "LIVE",
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
# FORMAT OUTPUT (IMPORTANT)
# =========================
def format_result(result):

    return (
        f"📊 Alpha Update\n\n"
        f"Model: {result['model']}\n"
        f"Regime: {result['regime']}\n\n"
        f"Signals: {result['signals']}\n\n"
        f"Portfolio: {result['portfolio']}"
    )
