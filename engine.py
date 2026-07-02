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

    liquidity_ratio = vol / mc

    momentum = change

    liquidity = liquidity_ratio * 100

    score = momentum + liquidity

    return round(score, 2)


def regime(data):

    changes = []

    for c in data:
        ch = c.get("price_change_percentage_24h", 0) or 0
        changes.append(ch)

    avg = sum(changes) / len(changes) if changes else 0

    if avg > 3:
        return "BULL"
    elif avg < -3:
        return "BEAR"
    else:
        return "NEUTRAL"


def action(score, sim):

    final = score + (sim * 3)

    if final > 25:
        return "SOLANA BREAKOUT 🚀"
    elif final > 15:
        return "STRONG BUY"
    elif final > 8:
        return "BUY"
    elif final > 3:
        return "WATCH"
    else:
        return "NOISE"


def run_engine():

    data = get_market()

    r = regime(data)

    signals = []

    for c in data:

        if not isinstance(c, dict):
            continue

        score = solana_similarity(c)
        sim = solana_similarity(c)

        act = action(score, sim)

        signals.append({
            "symbol": c.get("symbol", "unknown"),
            "score": score,
            "solana_similarity": sim,
            "action": act
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
        "regime": r,
        "signals": top10,
        "portfolio": portfolio
    }
