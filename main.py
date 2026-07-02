from fastapi import FastAPI, Request

app = FastAPI()

BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.get("/")
def home():
    return {"status": "Alpha running"}


# ✅ این همون چیزیه که تلگرام صدا می‌زنه
@app.post("/webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send_message(chat_id, "Alpha is active 🚀")

    elif text == "/update":
        result = run_engine()
        send_message(chat_id, str(result))

    return {"ok": True}


def send_message(chat_id, text):
    import requests

    url = f"{TELEGRAM_API}/sendMessage"

    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })
