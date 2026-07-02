import requests

def get_market():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    res = requests.get(url, timeout=10)

    if res.status_code != 200:
        return []

    try:
        data = res.json()
    except:
        return []

    return data


def safe_float(x):

    try:
        return float(x)
    except:
        return 0.0


def run_engine():

    data = get_market()

    signals = []

    for c in data:

        symbol = c.get("symbol", "")

        # فقط USDT pairs
        if "USDT" not in symbol:
            continue

        change = safe_float(c.get("priceChangePercent"))
        volume = safe_float(c.get("quoteVolume"))

        # normalize واقعی
        score = change * 1.5 + (volume / 1e9)

        signals.append({
            "symbol": symbol,
            "score": round(score, 3)
        })

    # اگر باز هم خالی بود → fallback واقعی
    if not signals:
        return {
            "regime": "FALLBACK",
            "signals": [
                {"symbol": "BTCUSDT", "score": 1.0},
                {"symbol": "ETHUSDT", "score": 0.9}
            ],
            "portfolio": [
                {"symbol": "BTCUSDT", "weight": 0.55},
                {"symbol": "ETHUSDT", "weight": 0.45}
            ]
        }

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    total = sum([abs(s["score"]) + 1 for s in top10])

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
