from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Alpha running"}

@app.get("/update")
def update():
    from engine import run_engine
    return run_engine()
