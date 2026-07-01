from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
URL = "https://YOUR-RENDER-URL.onrender.com/update"


def send_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )


@app.post("/webhook")
async def webhook(req: Request):

    data = await req.json()

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/update":

        res = requests.get(URL).json()

        msg = "🚀 ALPHA UPDATE\n\n"

        for i, x in enumerate(res["top10"], 1):
            msg += f"{i}. {x['symbol'].upper()} | {x['score']}\n"

        send_message(chat_id, msg)

    return {"ok": True}
