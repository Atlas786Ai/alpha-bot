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


def market_regime(data):

    changes = []

    for c in data:
        ch = c.get("price_change_percentage_24h", 0) or 0
        changes.append(ch)

    avg = sum(changes) / len(changes) if changes else 0

    if avg > 2:
        return "BULL"
    elif avg < -2:
        return "BEAR"
    else:
        return "NEUTRAL"


def compute_score(c, regime):

    change = c.get("price_change_percentage_24h", 0) or 0
    vol = c.get("total_volume", 0) or 0
    mc = c.get("market_cap", 1) or 1

    liquidity = vol / mc

    base = change * 0.6 + liquidity * 1000

    # regime adjustment
    if regime == "BULL":
        base *= 1.1
    elif regime == "BEAR":
        base *= 0.9

    # volatility penalty
    if abs(change) > 15:
        base *= 0.7

    return base


def signal(score):

    if score > 10:
        return "STRONG BUY"
    elif score > 6:
        return "BUY"
    elif score > 2:
        return "WATCH"
    elif score > 0:
        return "HOLD"
    else:
        return "AVOID"


def run_engine():

    data = get_market()

    regime = market_regime(data)

    signals = []

    for c in data:

        if not isinstance(c, dict):
            continue

        sc = compute_score(c, regime)

        signals.append({
            "symbol": c.get("symbol", "unknown"),
            "score": round(sc, 2),
            "action": signal(sc)
        })

    signals.sort(key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    total = sum([max(s["score"], 0.1) for s in top10])

    portfolio = []

    for s in top10:

        weight = max(s["score"], 0.1) / total

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
