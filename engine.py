import random
import math
from datetime import datetime

# =========================
# MEMORY (REAL BACKTEST CORE)
# =========================
MEMORY = {
    "predictions": [],
    "accuracy_history": [],
    "weights": {
        "structure": 0.45,
        "momentum": 0.30,
        "volatility": 0.15,
        "liquidity": 0.10
    }
}


# =========================
# SIMULATED MARKET FEED
# (in real version → CoinGecko)
# =========================
def get_market_data():

    symbols = ["SOL", "ETH", "BTC", "ARB", "AVAX", "DOGE"]

    market = []

    for s in symbols:

        price_change = random.uniform(-10, 10)  # real outcome
        market.append({
            "symbol": s,
            "future_return": price_change
        })

    return market


# =========================
# V21 ENGINE (PREDICTION)
# =========================
def run_engine_v21():

    symbols = ["SOL", "ETH", "BTC", "ARB", "AVAX", "DOGE"]

    signals = []

    for s in symbols:

        structure = random.uniform(20, 100)
        momentum = random.uniform(0, 20)
        volatility = random.uniform(0.1, 1.0)
        liquidity = random.uniform(0.5, 1.5)

        score = (
            structure * MEMORY["weights"]["structure"] +
            momentum * MEMORY["weights"]["momentum"] +
            (1 / (volatility + 0.01)) * MEMORY["weights"]["volatility"] +
            liquidity * MEMORY["weights"]["liquidity"]
        )

        signals.append({
            "symbol": s,
            "score": round(score, 4)
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top5 = signals[:5]

    prediction = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": "SOLANA_AI_V21_BACKTEST_CORE",
        "predicted_top": [x["symbol"] for x in top5],
        "signals": top5
    }

    MEMORY["predictions"].append(prediction)

    return prediction


# =========================
# BACKTEST ENGINE
# =========================
def run_backtest():

    market = get_market_data()

    correct = 0
    total = len(MEMORY["predictions"])

    if total == 0:
        return {"status": "no predictions yet"}

    last_pred = MEMORY["predictions"][-1]

    predicted = last_pred["predicted_top"]

    # evaluate correctness
    for m in market:

        if m["symbol"] in predicted and m["future_return"] > 0:
            correct += 1

    accuracy = correct / len(predicted)

    MEMORY["accuracy_history"].append(accuracy)

    # =========================
    # SELF LEARNING UPDATE
    # =========================
    if len(MEMORY["accuracy_history"]) > 2:

        avg_acc = sum(MEMORY["accuracy_history"][-5:]) / min(5, len(MEMORY["accuracy_history"]))

        # adjust weights based on performance
        if avg_acc < 0.4:
            MEMORY["weights"]["structure"] += 0.02
            MEMORY["weights"]["momentum"] += 0.02
        else:
            MEMORY["weights"]["volatility"] += 0.01
            MEMORY["weights"]["liquidity"] += 0.01

        # normalize weights
        total_w = sum(MEMORY["weights"].values())
        for k in MEMORY["weights"]:
            MEMORY["weights"][k] /= total_w

    return {
        "model": "SOLANA_AI_V21_BACKTEST_CORE",
        "accuracy": accuracy,
        "market_eval": market,
        "weights": MEMORY["weights"]
    }


# =========================
# COMBINED ENGINE (MAIN CALL)
# =========================
def run_engine_v21_full():

    prediction = run_engine_v21()
    backtest = run_backtest()

    return {
        "prediction": prediction,
        "backtest": backtest,
        "memory": MEMORY
    }
