from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

URL = "https://YOUR-RENDER-URL.onrender.com/update"


async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = requests.get(URL).json()

    msg = "🚀 ALPHA UPDATE\n\n"

    for i, x in enumerate(data["top10"], 1):
        msg += f"{i}. {x['symbol'].upper()} | {x['score']}\n"

    await update.message.reply_text(msg)


def main():

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("update", update_cmd))

    app.run_polling()


if __name__ == "__main__":
    main()
