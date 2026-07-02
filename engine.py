import requests

def get_market():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }

    res = requests.get(url, params=params)

    print("STATUS:", res.status_code)
    print("TEXT:", res.text[:500])  # فقط 500 کاراکتر اول

    return res.json()


def run_engine():

    data = get_market()

    print("DATA TYPE:", type(data))
    print("DATA SAMPLE:", data[:1] if isinstance(data, list) else data)

    results = []

    for c in data:

        if isinstance(c, dict):
            results.append({
                "symbol": c.get("symbol"),
                "score": c.get("price_change_percentage_24h", 0) or 0
            })

    return {"top10": results}
