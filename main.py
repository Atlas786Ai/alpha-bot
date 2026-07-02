from fastapi import FastAPI, Request
from engine import run_engine

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Alpha running"}

@app.get("/update")
def update():
    return run_engine()
