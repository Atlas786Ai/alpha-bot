from fastapi import FastAPI, Request
import urllib.request
import json
import math

app = FastAPI()

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY (INSTITUTIONAL CORE)
# =========================
MEMORY = {
    "equity": 100.0,
    "returns": [],
    "weights": {
        "momentum": 0.30,
        "structure": 0.30,
        "volatility": 0.20,
        "liquidity": 0.20
    }
}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {
        "status": "V27 INSTITUTIONAL CORE LIVE",
        "model": "SOLANA_AI_V27_INSTITUTIONAL"
    }


# =========================
# UPDATE ENDPOINT
# =========================
@app.get("/update")
def update():
    return run_v27()


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
        send(chat_id, "🏦 V27 INSTITUTIONAL CORE ACTIVE")

    elif text == "/update":
        result = run_v27()
        send(chat_id, format_message(result))

    return {"ok": True}


# =========================
# MARKET DATA
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
# SIGNAL SCORING
# =========================
def score(asset, w):

    structure = max(0, 100 - asset["rank"])
    momentum = asset["change"]
    volatility = abs(asset["change"]) / 10
    liquidity = asset["volume"] / 1e9

    return (
        structure * w["structure"] +
        momentum * w["momentum"] +
        (1 / (volatility + 0.01)) * w["volatility"] +
        liquidity * w["liquidity"]
    )


# =========================
# CORRELATION / RISK FILTER (SIMPLIFIED INSTITUTIONAL LOGIC)
# =========================
def risk_adjust(signals):

    avg = sum(s["score"] for s in signals) / len(signals)

    for s in signals:

        deviation = (s["score"] - avg) / (avg + 1e-6)

        # anomaly penalty
        s["risk_adj_score"] = s["score"] * (1 - abs(deviation) * 0.2)

    return signals


# =========================
# REGIME DETECTOR
# =========================
def detect_regime(top):

    avg = sum(x["risk_adj_score"] for x in top) / len(top)

    if avg > 60:
        return "RISK_ON_EXPANSION"
    elif avg > 30:
        return "NEUTRAL_TREND"
    else:
        return "RISK_OFF"


# =========================
# PORTFOLIO OPTIMIZER (RISK PARITY STYLE)
# =========================
def optimize_portfolio(signals):

    total = sum(max(s["risk_adj_score"], 0.01) for s in signals)

    portfolio = []

    for s in signals:

        weight = max(s["risk_adj_score"], 0.01) / total

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(weight, 4)
        })

    return portfolio


# =========================
# MAIN ENGINE (INSTITUTIONAL CORE)
# =========================
def run_v27():

    market = fetch_market()

    w = MEMORY["weights"]

    signals = []

    for m in market:

        s = score(m, w)

        signals.append({
            "symbol": m["symbol"],
            "score": round(s, 4),
            "momentum": m["change"],
            "volume": m["volume"],
            "rank": m["rank"]
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    # top 5
    top5 = signals[:5]

    # risk adjustment (institutional step)
    top5 = risk_adjust(top5)

    # portfolio optimization
    portfolio = optimize_portfolio(top5)

    # regime
    regime = detect_regime(top5)

    # =========================
    # SIMULATED RETURN (REALISTIC SIMPLE MODEL)
    # =========================
    ret = sum(s["risk_adj_score"] for s in top5) / 1000

    MEMORY["returns"].append(ret)

    MEMORY["equity"] += ret

    # =========================
    # DRAWDOWN
    # =========================
    peak = max(MEMORY["equity"], MEMORY["equity"])

    drawdown = (peak - MEMORY["equity"]) / (peak + 1e-6)

    # =========================
    # SHARPE-LIKE METRIC
    # =========================
    if len(MEMORY["returns"]) > 5:

        avg = sum(MEMORY["returns"][-10:]) / len(MEMORY["returns"][-10:])
        std = math.sqrt(sum((x - avg) ** 2 for x in MEMORY["returns"][-10:]) + 1e-9)

        sharpe = avg / std if std != 0 else 0

    else:
        sharpe = 0

    # =========================
    # WEIGHT ADAPTATION (INSTITUTIONAL REBALANCING)
    # =========================
    if sharpe < 0.3:
        w["volatility"] += 0.02
        w["momentum"] += 0.01
        w["structure"] -= 0.01

    else:
        w["liquidity"] += 0.01

    # normalize
    total_w = sum(w.values())

    for k in w:
        w[k] /= total_w

    return {
        "model": "SOLANA_AI_V27_INSTITUTIONAL_CORE",
        "regime": regime,
        "signals": top5,
        "portfolio": portfolio,
        "equity": round(MEMORY["equity"], 4),
        "drawdown": round(drawdown, 4),
        "sharpe": round(sharpe, 4),
        "weights": w
    }


# =========================
# TELEGRAM FORMAT
# =========================
def format_message(r):

    msg = "🏦 V27 INSTITUTIONAL CORE\n\n"

    msg += f"Regime: {r['regime']}\n"
    msg += f"Equity: {r['equity']}\n"
    msg += f"Drawdown: {r['drawdown']}\n"
    msg += f"Sharpe: {r['sharpe']}\n\n"

    msg += "📊 TOP SIGNALS:\n"

    for s in r["signals"]:
        msg += f"- {s['symbol']} | {s['risk_adj_score']}\n"

    msg += "\n💼 PORTFOLIO:\n"

    for p in r["portfolio"]:
        msg += f"- {p['symbol']} | {p['weight']}\n"

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
