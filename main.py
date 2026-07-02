from fastapi import Request

@app.post("/webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    print("TELEGRAM:", data)

    return {"ok": True}
