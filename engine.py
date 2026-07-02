import requests

def get_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h"
    }

    data = requests.get(url, params=params, timeout=10).json()

    if not isinstance(data, list):
        return []

    return data


def run_engine():

    data = get_market()

    results = []

    for c in data:

        if not isinstance(c, dict):
            continue

        change_24h = c.get("price_change_percentage_24h", 0)

        # مهم: جلوگیری از None
        if change_24h is None:
            change_24h = 0

        score = change_24h

        results.append({
            "symbol": c.get("symbol", "unknown"),
            "score": round(score, 2)
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "top10": results[:10]
    }
