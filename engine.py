import requests

def get_market():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1
    }
    return requests.get(url, params=params).json()


def run_engine():

    data = get_market()

    results = []

    for c in data:
        results.append({
            "symbol": c["symbol"],
            "score": (
                (c.get("price_change_percentage_24h", 0) or 0)
            )
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {"top10": results}
