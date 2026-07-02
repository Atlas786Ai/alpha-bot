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


# 🧠 SOL 2023 pattern model
def solana_similarity(c):

    change = c.get("price_change_percentage_24h", 0) or 0
    vol = c.get("total_volume", 0) or 0
    mc = c.get("market_cap", 1) or 1

    liquidity_ratio = vol / mc

    momentum_score = max(change, 0) / 10   # normalize
    liquidity_score = min(liquidity_ratio * 1000, 10)

    volatility_penalty = 1 if abs(change) < 20 else 0.7

    # final similarity (0 to ~10)
    score = (momentum_score * 0.5 + liquidity_score * 0.5) * volatility_penalty

    return round(score, 2)


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


def signal(score, sim):

    # ترکیب momentum + similarity به SOL 2023
    final = score + (sim * 2)

    if final > 18:
        return "SOLANA-STYLE BREAKOUT 🚀"
    elif final > 12:
        return "STRONG MOMENTUM"
    elif final > 7:
        return "WATCH"
    elif final > 3:
        return "WEAK SIGNAL"
    else:
        return "NOISE"


def run_engine():

    data = get_market()

    regime = market_regime(data)

    signals = []

    for c in data:

        if not isinstance(c, dict):
            continue

        change = c.get("price_change_percentage_24h", 0) or 0
        vol = c.get("total_volume", 0) or 0
        mc = c.get("market_cap", 1) or 1

        momentum_score = change * 0.6
        liquidity = (vol / mc) * 1000

        base_score = momentum_score + liquidity

        sol_sim = solana_similarity(c)

        action = signal(base_score, sol_sim)

        signals.append({
            "symbol": c.get("symbol", "unknown"),
            "score": round(base_score, 2),
            "solana_similarity": sol_sim,
            "action": action
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
