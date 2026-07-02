import requests

def get_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,
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


def compute_score(c):

    change = c.get("price_change_percentage_24h", 0) or 0
    volume = c.get("total_volume", 0) or 0
    market_cap = c.get("market_cap", 1) or 1

    # ساده ولی hedge-fund style scoring
    liquidity_score = volume / market_cap

    score = (change * 0.7) + (liquidity_score * 1000)

    return score


def get_signal(score):

    if score > 8:
        return "STRONG BUY"
    elif score > 4:
        return "BUY"
    elif score > 1:
        return "WATCH"
    elif score > 0:
        return "HOLD"
    else:
        return "AVOID"


def run_engine():

    data = get_market()

    signals = []

    for c in data:

        if not isinstance(c, dict):
            continue

        score = compute_score(c)

        signals.append({
            "symbol": c.get("symbol", "unknown"),
            "score": round(score, 2),
            "action": get_signal(score)
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top = signals[:10]

    # portfolio allocation (simple risk model)
    total = sum([max(s["score"], 0.1) for s in top])

    portfolio = []

    for s in top:

        weight = max(s["score"], 0.1) / total

        portfolio.append({
            "symbol": s["symbol"],
            "action": s["action"],
            "weight": round(weight, 3)
        })

    return {
        "signals": top,
        "portfolio": portfolio
    }
