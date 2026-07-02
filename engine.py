import requests

def get_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 30,
        "page": 1,
        "sparkline": False
    }

    res = requests.get(url, params=params, timeout=10)

    if res.status_code != 200:
        return []

    data = res.json()

    if not isinstance(data, list):
        return []

    return data


def solana_similarity(c):

    change = c.get("price_change_percentage_24h", 0) or 0
    vol = c.get("total_volume", 0) or 0
    mc = c.get("market_cap", 1) or 1

    # normalize درست
    liquidity_ratio = (vol / mc) if mc > 0 else 0

    # scaling واقعی
    momentum = change * 1.0
    liquidity = liquidity_ratio * 50   # مهم: scale شد

    return momentum + liquidity


def market_regime(data):

    changes = [(c.get("price_change_percentage_24h", 0) or 0) for c in data]

    avg = sum(changes) / len(changes) if changes else 0

    if avg > 2:
        return "BULL"
    elif avg < -2:
        return "BEAR"
    return "NEUTRAL"


def action(score):

    if score > 15:
        return "SOLANA BREAKOUT 🚀"
    elif score > 8:
        return "STRONG BUY"
    elif score > 3:
        return "BUY"
    elif score > 0:
        return "WATCH"
    else:
        return "NOISE"


def run_engine():

    data = get_market()

    regime = market_regime(data)

    signals = []

    for c in data:

        if not isinstance(c, dict):
            continue

        score = solana_similarity(c)

        signals.append({
            "symbol": c.get("symbol", "unknown"),
            "score": round(score, 2),
            "action": action(score)
        })

    # مهم: حداقل threshold حذف شد
    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    total = sum([abs(s["score"]) + 1 for s in top10])

    portfolio = []

    for s in top10:

        weight = (abs(s["score"]) + 1) / total

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(weight, 3),
            "action": s["action"]
        })

    return {
        "regime": regime,
        "signals": top10,
        "portfolio": portfolio
    }
