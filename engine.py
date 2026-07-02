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

    res = requests.get(url, params=params, timeout=10)

    print("STATUS:", res.status_code)
    print("TEXT:", res.text[:200])

    if res.status_code != 200:
        return []

    try:
        data = res.json()
    except Exception as e:
        print("JSON ERROR:", e)
        return []

    print("DATA TYPE:", type(data))

    return data


def run_engine():

    data = get_market()

    print("LEN:", len(data) if isinstance(data, list) else "NO LIST")

    signals = []

    for i, c in enumerate(data):

        print("COIN:", i, c)

        if not isinstance(c, dict):
            continue

        change = c.get("price_change_percentage_24h", 0) or 0

        signals.append({
            "symbol": c.get("symbol"),
            "score": change
        })

    return {
        "debug_len": len(data) if isinstance(data, list) else 0,
        "signals": signals
    }
