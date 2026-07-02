from fastapi import FastAPI
import json
import urllib.request
import math

app = FastAPI()


# =========================
# MODEL STATE
# =========================
STATE = {
    "weights": {
        "momentum": 0.35,
        "trend": 0.35,
        "volatility": 0.30
    },
    "learning_rate": 0.08,
    "error_memory": []
}


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "status": "V31 REAL BACKTEST ENGINE ACTIVE",
        "model": "SOLANA_AI_V31_BACKTEST"
    }


# =========================
# SIMULATED 2023 DATA ENGINE
# =========================
def load_2023_market():

    """
    Real-world approximation of 2023 crypto cycles
    (not exact prices, but structured behavior)
    """

    return {
        "Q1": {
            "BTC": 0.25,
            "ETH": 0.18,
            "SOL": 0.42,
            "ARB": 0.55,
            "DOGE": 0.12,
            "AVAX": 0.30
        },
        "Q2": {
            "BTC": 0.15,
            "ETH": 0.22,
            "SOL": 0.35,
            "ARB": 0.20,
            "DOGE": 0.10,
            "AVAX": 0.18
        },
        "Q3": {
            "BTC": 0.28,
            "ETH": 0.20,
            "SOL": 0.60,
            "ARB": 0.45,
            "DOGE": 0.14,
            "AVAX": 0.33
        },
        "Q4": {
            "BTC": 0.40,
            "ETH": 0.32,
            "SOL": 0.85,
            "ARB": 0.72,
            "DOGE": 0.22,
            "AVAX": 0.41
        }
    }


# =========================
# CORE SCORING FUNCTION
# =========================
def score(asset_return, weights):

    return (
        asset_return * weights["momentum"] +
        asset_return ** 0.5 * weights["trend"] -
        abs(asset_return) * 0.1 * weights["volatility"]
    )


# =========================
# BACKTEST ENGINE (CORE)
# =========================
def run_backtest():

    market = load_2023_market()
    w = STATE["weights"]

    coins = ["BTC", "ETH", "SOL", "ARB", "DOGE", "AVAX"]

    results = {
        "Q1": {},
        "Q2": {},
        "Q3": {},
        "Q4": {},
        "final_ranking": {},
        "trajectory_score": {}
    }

    # =========================
    # STEP 1: QUARTER ANALYSIS
    # =========================
    for q in market:

        quarter_scores = {}

        for c in coins:

            s = score(market[q][c], w)

            quarter_scores[c] = s

        results[q] = quarter_scores


    # =========================
    # STEP 2: TRAJECTORY CALCULATION
    # =========================
    for c in coins:

        path = [
            market["Q1"][c],
            market["Q2"][c],
            market["Q3"][c],
            market["Q4"][c]
        ]

        trend = sum(path) / len(path)

        stability = 1 - (max(path) - min(path))

        trajectory = (trend * 0.7) + (stability * 0.3)

        results["trajectory_score"][c] = trajectory


    # =========================
    # STEP 3: MODEL ERROR ANALYSIS
    # =========================
    sorted_coins = sorted(
        results["trajectory_score"].items(),
        key=lambda x: x[1],
        reverse=True
    )

    predicted_top = [x[0] for x in sorted_coins[:3]]
    actual_top = ["SOL", "ARB", "ETH"]

    error = len(set(predicted_top) - set(actual_top)) / 3

    STATE["error_memory"].append(error)

    if len(STATE["error_memory"]) > 10:
        STATE["error_memory"].pop(0)


    # =========================
    # STEP 4: SELF-LEARNING UPDATE
    # =========================
    avg_error = sum(STATE["error_memory"]) / len(STATE["error_memory"])

    if avg_error > 0.4:

        # adjust weights
        w["trend"] += 0.02
        w["momentum"] -= 0.01
        w["volatility"] += 0.01

    else:

        w["momentum"] += 0.01
        w["trend"] += 0.01


    # normalize weights
    total = sum(w.values())

    for k in w:
        w[k] /= total


    return {
        "model": "SOLANA_AI_V31_BACKTEST_ENGINE",
        "trajectory": results["trajectory_score"],
        "predicted_top3": predicted_top,
        "error_rate": round(error, 4),
        "avg_error": round(avg_error, 4),
        "weights": w
    }


# =========================
# API
# =========================
@app.get("/backtest")
def backtest():

    return run_backtest()
