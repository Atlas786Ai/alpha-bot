from fastapi import FastAPI, Request
import urllib.request
import json
import math

app = FastAPI()

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# MEMORY (REAL QUANT CORE)
# =========================
MEMORY = {
    "equity": 100.0,
    "returns_window": [],
    "asset_history": [],
    "factor_history": [],
    "weights": {
        "momentum": 0.30,
        "structure": 0.25,
        "volatility": 0.25,
        "liquidity": 0.20
    }
}


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {
        "status": "V28 REAL QUANT AI ACTIVE",
        "model": "SOLANA_AI_V28_QUANT_CORE"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v28()


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
        send(chat_id, "🚀 V28 REAL QUANT AI ACTIVE")

    elif text == "/update":
        result = run_v28()
        send(chat_id, format_result(result))

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
            "volume": c.get("total_volume", 0),
            "rank": c.get("market_cap_rank", 999)
        })

    return market


# =========================
# FEATURE ENGINE (REAL QUANT FACTORS)
# =========================
def features(asset, w):

    structure = max(0, 100 - asset["rank"])
    momentum = asset["change"]
    volatility = abs(asset["change"]) / 10
    liquidity = asset["volume"] / 1e9

    return {
        "structure": structure,
        "momentum": momentum,
        "volatility": volatility,
        "liquidity": liquidity
    }


# =========================
# Z-SCORE ANOMALY DETECTION
# =========================
def zscore(values, x):

    mean = sum(values) / len(values)
    std = math.sqrt(sum((v - mean) ** 2 for v in values) + 1e-9)

    if std == 0:
        return 0

    return (x - mean) / std


# =========================
# COVARIANCE (SIMPLIFIED)
# =========================
def covariance(x, y):

    n = len(x)

    if n == 0:
        return 0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n

    return cov


# =========================
# MAIN SCORE ENGINE
# =========================
def score(asset, w, context):

    f = features(asset, w)

    return (
        f["structure"] * w["structure"] +
        f["momentum"] * w["momentum"] +
        (1 / (f["volatility"] + 0.01)) * w["volatility"] +
        f["liquidity"] * w["liquidity"]
    )


# =========================
# FACTOR BUILDING (PCA-LIKE SIMULATION)
# =========================
def build_factors(signals):

    momentum_list = [s["momentum"] for s in signals]
    score_list = [s["score"] for s in signals]

    factor_momentum = sum(momentum_list) / len(momentum_list)
    factor_score = sum(score_list) / len(score_list)

    return {
        "factor_momentum": factor_momentum,
        "factor_score": factor_score
    }


# =========================
# PORTFOLIO OPTIMIZER (RISK-ADJUSTED)
# =========================
def optimize(signals):

    scores = [s["score"] for s in signals]

    total = sum(max(s, 0.01) for s in scores)

    portfolio = []

    for s in signals:

        weight = max(s["score"], 0.01) / total

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(weight, 4)
        })

    return portfolio


# =========================
# WALK-FORWARD LEARNING (SIMPLIFIED)
# =========================
def walk_forward_update(history):

    if len(history) < 5:
        return 0

    recent = history[-5:]

    return sum(recent) / len(recent)


# =========================
# MAIN ENGINE
# =========================
def run_v28():

    market = fetch_market()

    signals = []

    w = MEMORY["weights"]

    for m in market:

        s = score(m, w, MEMORY)

        signals.append({
            "symbol": m["symbol"],
            "score": round(s, 4),
            "momentum": m["change"],
            "volume": m["volume"]
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top5 = signals[:5]

    # =========================
    # Z-SCORE ANOMALY DETECTION
    # =========================
    scores = [s["score"] for s in top5]

    anomalies = []

    for s in top5:

        z = zscore(scores, s["score"])

        anomalies.append({
            "symbol": s["symbol"],
            "zscore": round(z, 4),
            "anomaly": "HIGH" if abs(z) > 1 else "NORMAL"
        })

    # =========================
    # FACTORS (PCA-LIKE)
    # =========================
    factors = build_factors(top5)

    # =========================
    # PORTFOLIO OPTIMIZATION
    # =========================
    portfolio = optimize(top5)

    # =========================
    # RETURN SIMULATION
    # =========================
    ret = sum(scores) / 1000

    MEMORY["returns_window"].append(ret)

    if len(MEMORY["returns_window"]) > 20:
        MEMORY["returns_window"].pop(0)

    # =========================
    # WALK FORWARD PERFORMANCE
    # =========================
    wf = walk_forward_update(MEMORY["returns_window"])

    MEMORY["equity"] += ret

    # =========================
    # WEIGHT ADAPTATION (REAL QUANT STYLE)
    # =========================
    if wf < 0:

        w["volatility"] += 0.02
        w["momentum"] += 0.01
        w["structure"] -= 0.01

    else:

        w["liquidity"] += 0.01

    total_w = sum(w.values())

    for k in w:
        w[k] /= total_w

    return {
        "model": "SOLANA_AI_V28_REAL_QUANT",
        "signals": top5,
        "anomalies": anomalies,
        "portfolio": portfolio,
        "factors": factors,
        "walk_forward": round(wf, 6),
        "equity": round(MEMORY["equity"], 4),
        "weights": w
    }


# =========================
# FORMAT
# =========================
def format_result(r):

    msg = "🏦 V28 REAL QUANT AI\n\n"

    msg += f"Equity: {r['equity']}\n"
    msg += f"WalkForward: {r['walk_forward']}\n\n"

    msg += "📊 TOP SIGNALS:\n"

    for s in r["signals"]:
        msg += f"- {s['symbol']} | {s['score']}\n"

    msg += "\n⚠️ ANOMALIES:\n"

    for a in r["anomalies"]:
        msg += f"- {a['symbol']} | {a['anomaly']}\n"

    msg += "\n💼 PORTFOLIO:\n"

    for p in r["portfolio"]:
        msg += f"- {p['symbol']} | {p['weight']}\n"

    msg += "\n🧠 FACTORS:\n"
    for k, v in r["factors"].items():
        msg += f"- {k}: {round(v,4)}\n"

    return msg


# =========================
# SEND TELEGRAM
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
