import requests

def get_market():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    res = requests.get(url, timeout=10)

    if res.status_code != 200:
        return []

    data = res.json()

    # فقط USDT pairs
    filtered = []

    for c in data:

        if "USDT" in c.get("symbol", ""):
            filtered.append(c)

    return filtered[:20]


def run_engine():

    data = get_market()

    signals = []

    for c in data:

        try:
            change = float(c.get("priceChangePercent", 0))
        except:
            change = 0

        try:
            volume = float(c.get("quoteVolume", 0))
        except:
            volume = 0

        score = change + (volume / 1e9)

        signals.append({
            "symbol": c.get("symbol"),
            "score": round(score, 2)
        })

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    total = sum([abs(s["score"]) + 1 for s in top10]) or 1

    portfolio = []

    for s in top10:

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round((abs(s["score"]) + 1) / total, 3)
        })

    return {
        "regime": "LIVE",
        "signals": top10,
        "portfolio": portfolio
    }
