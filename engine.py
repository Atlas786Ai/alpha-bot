import requests
import time

CACHE = {
    "data": None,
    "time": 0
}

def get_market():

    global CACHE

    now = time.time()

    # cache برای 60 ثانیه (خیلی مهم)
    if CACHE["data"] and now - CACHE["time"] < 60:
        return CACHE["data"]

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }

    res = requests.get(url, params=params)

    # اگر rate limit خوردیم
    if res.status_code != 200:
        return CACHE["data"] or []

    data = res.json()

    CACHE["data"] = data
    CACHE["time"] = now

    return data


def run_engine():

    data = get_market()

    results = []

    for c in data:

        if not isinstance(c, dict):
            continue

        score = c.get("price_change_percentage_24h", 0) or 0

        results.append({
            "symbol": c.get("symbol", "unknown"),
            "score": round(score, 2)
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {"top10": results}
