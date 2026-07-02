from fastapi import FastAPI, Request
from engine import run_engine

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Alpha running"}

@app.get("/update")
def update():

    try:
        return run_engine()
    except Exception as e:
        return {
            "error": str(e)
        }

@app.post("/webhook")
async def webhook(request: Request):

    try:
        data = await request.json()
        print("WEBHOOK:", data)

        return {"ok": True}

    except Exception as e:
        return {
            "error": str(e)
        }
