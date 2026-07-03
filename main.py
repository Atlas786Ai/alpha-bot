from fastapi import FastAPI
import random

app = FastAPI()


# =========================
# UNIVERSE (100 COINS SIMULATION)
# =========================
COINS = [
    "BTC","ETH","SOL","ARB","AVAX","DOGE","MATIC","OP","INJ","TIA",
    "NEAR","SUI","APT","LTC","XRP","BNB","LINK","UNI","AAVE","FTM"
]


# =========================
# INITIAL MODEL WEIGHTS
# =========================
weights = {
    "momentum": 0.35,
    "volatility": 0.25,
    "trend": 0.25,
    "noise": 0.15
}


# =========================
# GENERATE MARKET SNAPSHOT
# =========================
def market_snapshot():

    data = {}

    for c in COINS:

        price_trend = random.uniform(-2, 6)
        volatility = random.uniform(0.01, 0.3)
        momentum = random.uniform(-1, 5)

        score = (
            price_trend * weights["trend"] +
            momentum * weights["momentum"] -
            volatility * weights["volatility"] +
            random.uniform(-0.5, 0.5) * weights["noise"]
        )

        data[c] = {
            "score": round(score, 3),
            "trend": price_trend,
            "momentum": momentum,
            "vol": volatility
        }

    return data


# =========================
# BACKTEST ONE PERIOD (3 MONTHS)
# =========================
def backtest_period(period_id):

    snapshot = market_snapshot()

    ranked = sorted(snapshot.items(), key=lambda x: x[1]["score"], reverse=True)

    top10 = ranked[:10]

    # simulate "truth" (future performance)
    future = {c: random.uniform(-1, 8) for c in COINS}

    correct = 0

    for c, _ in top10:
        if future[c] > 2:  # success threshold
            correct += 1

    win_rate = correct / 10

    return {
        "period": period_id,
        "top10": [{"symbol": c, "score": v["score"]} for c, v in top10],
        "win_rate": round(win_rate, 3)
    }


# =========================
# ADAPTIVE WEIGHT UPDATE
# =========================
def adapt_weights(results):

    avg_win = sum(r["win_rate"] for r in results) / len(results)

    # simple learning rule
    if avg_win < 0.5:
        weights["momentum"] += 0.05
        weights["noise"] -= 0.03

    if avg_win > 0.7:
        weights["trend"] += 0.05
        weights["volatility"] -= 0.02

    # normalize
    total = sum(weights.values())

    for k in weights:
        weights[k] /= total


# =========================
# MAIN BACKTEST ENGINE
# =========================
def run_backtest():

    results = []

    for i in range(4):  # 4 quarters

        res = backtest_period(f"Q{i+1}")
        results.append(res)

    adapt_weights(results)

    avg_win = sum(r["win_rate"] for r in results) / 4

    return {
        "model": "V35_BACKTEST_ENGINE",
        "periods": results,
        "avg_win_rate": round(avg_win, 3),
        "updated_weights": weights
    }


# =========================
# API
# =========================
@app.get("/")
def home():

    return {
        "system": "V35 BACKTEST ENGINE ACTIVE"
    }


@app.get("/backtest")
def backtest():

    return run_backtest()
