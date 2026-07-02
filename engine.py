from fastapi import FastAPI, Request
import urllib.request
import json
import math

app = FastAPI()

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY (QUANT CORE)
# =========================
MEMORY = {
    "weights": {
        "structure": 0.4,
        "momentum": 0.3,
        "volatility": 0.2,
        "volume": 0.1
    },
    "returns_history": [],
    "equity_curve": [],
    "peak": 100.0
}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {
        "status": "V25 QUANT CORE ACTIVE",
        "model": "SOLANA_AI_V25_QUANT"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v25_quant()


# =========================
# TELEGRAM WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    msg = data.get("message", {})
    text = msg.get("text", "")
    chat_id = msg.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False}

    if text == "/start":
        send(chat_id, "🚀 V25 QUANT CORE ACTIVE")

    elif text == "/update":
        result = run_v25_quant()
        send(chat_id, format(result))

    return {"ok": True}


# =========================
# LIVE MARKET
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

    market = []

    for c in data:

        market.append({
            "symbol": c["symbol"].upper(),
            "change": c.get("price_change_percentage_24h", 0) or 0,
            "rank": c.get("market_cap_rank", 999),
            "volume": c.get("total_volume", 0)
        })

    return market


# =========================
# QUANT SCORE ENGINE
# =========================
def score(asset, w):

    structure = max(0, 100 - asset["rank"])
    momentum = asset["change"]
    volatility = abs(asset["change"]) / 10
    volume = asset["volume"] / 1e9

    return (
        structure * w["structure"] +
        momentum * w["momentum"] +
        (1 / (volatility + 0.01)) * w["volatility"] +
        volume * w["volume"]
    )


# =========================
# BACKTEST SIMULATION RETURN
# =========================
def simulate_return(top_assets):

    # fake but structured return model
    r = 0

    for a in top_assets:

        r += a["score"] * 0.01

    noise = 0.05 * (r * 0.1)

    return r + noise


# =========================
# SHARPE RATIO (SIMPLIFIED)
# =========================
def sharpe(returns):

    if len(returns) < 2:
        return 0

    avg = sum(returns) / len(returns)

    variance = sum((x - avg) ** 2 for x in returns) / len(returns)

    std = math.sqrt(variance)

    if std == 0:
        return 0

    return avg / std


# =========================
# MAIN ENGINE
# =========================
def run_v25_quant():

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

    # =========================
    # QUANT RETURN SIMULATION
    # =========================
    ret = simulate_return(top5)

    MEMORY["returns_history"].append(ret)

    MEMORY["equity_curve"].append(
        MEMORY["equity_curve"][-1] + ret if MEMORY["equity_curve"] else 100 + ret
    )

    # =========================
    # DRAWDOWN
    # =========================
    current = MEMORY["equity_curve"][-1]

    if current > MEMORY["peak"]:
        MEMORY["peak"] = current

    drawdown = (MEMORY["peak"] - current) / MEMORY["peak"]

    # =========================
    # SHARPE
    # =========================
    sharpe_score = sharpe(MEMORY["returns_history"][-20:])

    # =========================
    # ADAPTIVE WEIGHT UPDATE
    # =========================
    if sharpe_score < 0.5:

        MEMORY["weights"]["structure"] += 0.02
        MEMORY["weights"]["momentum"] += 0.01
        MEMORY["weights"]["volatility"] -= 0.01

    else:

        MEMORY["weights"]["volume"] += 0.01

    # normalize
    total = sum(MEMORY["weights"].values())

    for k in MEMORY["weights"]:
        MEMORY["weights"][k] /= total

    return {
        "model": "SOLANA_AI_V25_QUANT_CORE",
        "signals": top5,
        "return": round(ret, 4),
        "sharpe": round(sharpe_score, 4),
        "drawdown": round(drawdown, 4),
        "equity": round(MEMORY["equity_curve"][-1], 2),
        "weights": MEMORY["weights"]
    }


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


# =========================
# FORMAT OUTPUT
# =========================
def format(result):

    msg = "🚀 V25 QUANT CORE\n\n"

    msg += f"Return: {result['return']}\n"
    msg += f"Sharpe: {result['sharpe']}\n"
    msg += f"Drawdown: {result['drawdown']}\n"
    msg += f"Equity: {result['equity']}\n\n"

    msg += "📊 SIGNALS:\n"

    for s in result["signals"]:
        msg += f"- {s['symbol']} | {s['score']}\n"

    return msg
