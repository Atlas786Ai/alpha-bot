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

        if not isinstance(c, dict):
            continue

        symbol = c.get("symbol")

        if not symbol:
            continue

        # ❗ FIX: safe check (case insensitive + robust)
        if "usdt" not in symbol.lower():
            continue

        change = safe_float(c.get("priceChangePercent"))
        volume = safe_float(c.get("quoteVolume"))

        # normalized score
        score = change * 1.2 + (volume / 1e9)

        signals.append({
            "symbol": symbol,
            "score": round(score, 3)
        })

    # ❗ اگر هنوز خالی بود → debug fallback
    if len(signals) == 0:

        return {
            "regime": "DEBUG_EMPTY",
            "raw_count": len(data),
            "sample": data[:2]
        }

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
