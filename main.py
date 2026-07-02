from fastapi import FastAPI, Request
import urllib.request
import json
import math

app = FastAPI()

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY
# =========================
MEMORY = {
    "equity": 100.0,
    "returns_window": [],
    "weights": {
        "momentum": 0.30,
        "structure": 0.25,
        "volatility": 0.25,
        "liquidity": 0.20
    }
}


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {"status": "V28 ACTIVE", "model": "SOLANA_AI_V28_REAL_QUANT"}


# =========================
# UPDATE (DIRECT V28)
# =========================
@app.get("/update")
def update():
    return run_v28()


# =========================
# TELEGRAM WEBHOOK (ONLY V28)
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    msg = data.get("message", {})
    text = msg.get("text", "")
    chat_id = msg.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    # ALWAYS V28 ONLY
    if text == "/start":
        send(chat_id, "🚀 V28 REAL QUANT ACTIVE")

    elif text == "/update":
        result = run_v28()
        send(chat_id, format_result(result))

    return {"ok": True}


# =========================
# MARKET
# =========================
def fetch_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 15,
        "page": 1,
        "sparkline": False
    }

    query = urllib.parse.urlencode(params)
    raw = urllib.request.urlopen(url + "?" + query, timeout=5).read()
    data = json.loads(raw)

    return [{
        "symbol": c["symbol"].upper(),
        "change": c.get("price_change_percentage_24h", 0) or 0,
        "volume": c.get("total_volume", 0),
        "rank": c.get("market_cap_rank", 999)
    } for c in data]


# =========================
# SCORE ENGINE (V28 CORE)
# =========================
def score(a, w):

    structure = max(0, 100 - a["rank"])
    momentum = a["change"]
    volatility = abs(a["change"]) / 10
    liquidity = a["volume"] / 1e9

    return (
        structure * w["structure"] +
        momentum * w["momentum"] +
        (1 / (volatility + 0.01)) * w["volatility"] +
        liquidity * w["liquidity"]
    )


# =========================
# V28 CORE ENGINE
# =========================
def run_v28():

    market = fetch_market()
    w = MEMORY["weights"]

    signals = []

    for m in market:

        s = score(m, w)

        signals.append({
            "symbol": m["symbol"],
            "score": round(s, 4),
            "momentum": m["change"]
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top5 = signals[:5]

    # ===== return model =====
    ret = sum(x["score"] for x in top5) / 1000

    MEMORY["returns_window"].append(ret)

    if len(MEMORY["returns_window"]) > 20:
        MEMORY["returns_window"].pop(0)

    # ===== equity =====
    MEMORY["equity"] += ret

    # ===== simple sharpe =====
    avg = sum(MEMORY["returns_window"]) / len(MEMORY["returns_window"])

    std = math.sqrt(sum((x - avg) ** 2 for x in MEMORY["returns_window"]) + 1e-9)

    sharpe = avg / std if std != 0 else 0

    # ===== adaptive learning =====
    if sharpe < 0.3:
        w["volatility"] += 0.02
        w["momentum"] += 0.01
        w["structure"] -= 0.01
    else:
        w["liquidity"] += 0.01

    total = sum(w.values())

    for k in w:
        w[k] /= total

    return {
        "model": "SOLANA_AI_V28_REAL_QUANT",
        "signals": top5,
        "equity": round(MEMORY["equity"], 4),
        "sharpe": round(sharpe, 4),
        "weights": w
    }


# =========================
# FORMAT FOR TELEGRAM
# =========================
def format_result(r):

    msg = "🚀 V28 REAL QUANT\n\n"

    msg += f"Equity: {r['equity']}\n"
    msg += f"Sharpe: {r['sharpe']}\n\n"

    msg += "TOP SIGNALS:\n"

    for s in r["signals"]:
        msg += f"- {s['symbol']} | {s['score']}\n"

    return msg


# =========================
# TELEGRAM SEND
# =========================
def send(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )

    urllib.request.urlopen(req)
