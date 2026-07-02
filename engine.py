from fastapi import FastAPI, Request
import urllib.request
import json
import math
import random

app = FastAPI()

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# HEDGE FUND MEMORY
# =========================
MEMORY = {
    "equity": 100.0,
    "peak": 100.0,
    "returns": [],
    "weights": {
        "momentum": 0.35,
        "structure": 0.30,
        "volatility": 0.20,
        "volume": 0.15
    }
}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {
        "status": "V26 HEDGE FUND CORE LIVE",
        "model": "SOLANA_AI_V26_HEDGE_FUND"
    }


# =========================
# UPDATE ENDPOINT
# =========================
@app.get("/update")
def update():
    return run_v26()


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
        send(chat_id, "🚀 V26 HEDGE FUND ACTIVE")

    elif text == "/update":
        result = run_v26()
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
# SCORE ENGINE (HEDGE FUND STYLE)
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
# REGIME DETECTOR
# =========================
def regime(top):

    avg = sum(x["score"] for x in top) / len(top)

    if avg > 60:
        return "RISK_ON_EXPANSION"
    elif avg > 30:
        return "NEUTRAL_TREND"
    else:
        return "RISK_OFF"


# =========================
# MONTE CARLO SIMULATION
# =========================
def monte_carlo(returns):

    simulations = []

    for _ in range(50):

        sample = random.sample(returns, len(returns)) if len(returns) > 3 else returns

        simulations.append(sum(sample) / len(sample))

    return sum(simulations) / len(simulations)


# =========================
# MAIN ENGINE
# =========================
def run_v26():

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
    # RETURN MODEL (SIMPLIFIED)
    # =========================
    ret = sum(x["score"] for x in top5) / 1000

    MEMORY["returns"].append(ret)

    MEMORY["equity"] += ret

    # peak tracking
    if MEMORY["equity"] > MEMORY["peak"]:
        MEMORY["peak"] = MEMORY["equity"]

    drawdown = (MEMORY["peak"] - MEMORY["equity"]) / MEMORY["peak"]

    # risk metric (pseudo sharpe)
    avg_ret = sum(MEMORY["returns"][-10:]) / max(1, len(MEMORY["returns"][-10:]))
    risk = math.sqrt(sum((x - avg_ret) ** 2 for x in MEMORY["returns"][-10:]) + 1e-9)

    sharpe = avg_ret / risk if risk != 0 else 0

    # Monte Carlo stability check
    stability = monte_carlo(MEMORY["returns"][-10:])

    # =========================
    # WEIGHT ADAPTATION (HEDGE FUND LOGIC)
    # =========================
    if sharpe < 0.3:

        w["momentum"] += 0.02
        w["structure"] += 0.01
        w["volatility"] -= 0.01

    else:

        w["volume"] += 0.01

    # normalize
    total = sum(w.values())

    for k in w:
        w[k] /= total

    return {
        "model": "SOLANA_AI_V26_HEDGE_FUND",
        "regime": regime(top5),
        "signals": top5,
        "equity": round(MEMORY["equity"], 3),
        "drawdown": round(drawdown, 4),
        "sharpe_like": round(sharpe, 4),
        "monte_carlo_stability": round(stability, 4),
        "weights": w
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
def format(r):

    msg = "🚀 V26 HEDGE FUND\n\n"

    msg += f"Regime: {r['regime']}\n"
    msg += f"Equity: {r['equity']}\n"
    msg += f"Drawdown: {r['drawdown']}\n"
    msg += f"Sharpe: {r['sharpe_like']}\n"
    msg += f"Stability: {r['monte_carlo_stability']}\n\n"

    msg += "TOP SIGNALS:\n"

    for s in r["signals"]:
        msg += f"- {s['symbol']} | {s['score']}\n"

    return msg
