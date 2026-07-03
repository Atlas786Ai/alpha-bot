from fastapi import FastAPI
import requests
import time
import math
import statistics

app = FastAPI()

# =========================
# STATE
# =========================
STATE = {
    "equity": 100.0,
    "history_equity": [],
    "last_error": None
}

COINS_LIMIT = 100


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {
        "model": "V44_INSTITUTIONAL_QUANT",
        "status": "LIVE HEDGE-FUND STYLE ENGINE"
    }


# =========================
# UPDATE
# =========================
@app.get("/update")
def update():
    return run_v44()


# =========================
# DATA SOURCE (SAFE)
# =========================
def fetch_market():

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": COINS_LIMIT,
                "page": 1,
                "sparkline": "false"
            },
            timeout=8
        )

        data = r.json()

        if isinstance(data, list) and len(data) > 10:
            return data

    except Exception as e:
        STATE["last_error"] = str(e)

    return []


# =========================
# REGIME DETECTOR (REALISTIC)
# =========================
def detect_regime(market):

    changes = [
        m.get("price_change_percentage_24h") or 0
        for m in market
    ]

    avg = statistics.mean(changes)

    if avg > 1.5:
        return "BULL"

    if avg < -1.5:
        return "BEAR"

    return "ACCUMULATION"


# =========================
# VOLATILITY
# =========================
def volatility(market):

    changes = [
        m.get("price_change_percentage_24h") or 0
        for m in market
    ]

    if len(changes) < 2:
        return 0

    return statistics.pstdev(changes)


# =========================
# SCORE ENGINE V44
# =========================
def score(asset, btc, vol_regime):

    change = asset.get("price_change_percentage_24h") or 0
    volume = asset.get("total_volume") or 1
    rank = asset.get("market_cap_rank") or 100

    rel = change - btc

    momentum = change / 10

    volume_log = math.log1p(volume)

    rank_score = 1 - min(rank / 100, 1)

    stability = 1 / (1 + abs(momentum))

    # volatility penalty (IMPORTANT NEW)
    vol_penalty = 1 / (1 + vol_regime)

    return (
        rel * 0.30 +
        momentum * 0.20 +
        volume_log * 0.20 +
        rank_score * 0.15 +
        stability * 0.10 +
        vol_penalty * 0.05
    )


# =========================
# SHARPE-LIKE EQUITY TRACKER
# =========================
def update_equity(return_val):

    STATE["equity"] += return_val

    STATE["history_equity"].append(STATE["equity"])

    if len(STATE["history_equity"]) > 50:
        STATE["history_equity"].pop(0)


# =========================
# MAX DRAWDOWN
# =========================
def max_drawdown():

    equity = STATE["history_equity"]

    if len(equity) < 2:
        return 0

    peak = equity[0]
    max_dd = 0

    for x in equity:

        if x > peak:
            peak = x

        dd = (peak - x) / peak

        max_dd = max(max_dd, dd)

    return max_dd


# =========================
# MAIN ENGINE V44
# =========================
def run_v44():

    market = fetch_market()

    if not market:
        return {
            "model": "V44_INSTITUTIONAL_QUANT",
            "status": "NO_DATA_SAFE_MODE"
        }

    # REGIME + VOLATILITY
    reg = detect_regime(market)
    vol = volatility(market)

    btc = 0

    for m in market:
        if m.get("symbol","").upper() == "BTC":
            btc = m.get("price_change_percentage_24h") or 0

    scored = []

    for m in market:

        s = score(m, btc, vol)

        scored.append({
            "symbol": m.get("symbol","").upper(),
            "score": round(s, 6),
            "momentum": m.get("price_change_percentage_24h") or 0
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    total = sum(abs(x["score"]) for x in top10) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(abs(x["score"]) / total, 4)
        }
        for x in top10[:5]
    ]

    # simulated return (institutional proxy)
    daily_return = sum(x["score"] for x in top10) / 20000

    update_equity(daily_return)

    dd = max_drawdown()

    return {
        "model": "V44_INSTITUTIONAL_QUANT",
        "regime": reg,
        "volatility": round(vol, 4),
        "max_drawdown": round(dd, 4),
        "equity": round(STATE["equity"], 4),
        "top10": top10,
        "portfolio": portfolio
    }
