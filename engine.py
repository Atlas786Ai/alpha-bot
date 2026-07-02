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


def safe(c, key):

    v = c.get(key, 0)
    if v is None:
        return 0
    return v


def compute_raw(c):

    change = safe(c, "price_change_percentage_24h")
    vol = safe(c, "total_volume")
    mc = safe(c, "market_cap")

    if mc == 0:
        mc = 1

    liquidity = vol / mc

    return {
        "symbol": c.get("symbol", "unknown"),
        "change": change,
        "liquidity": liquidity
    }


def run_engine():

    data = get_market()

    processed = [compute_raw(c) for c in data]

    # ❗ ranking-based normalization
    changes = sorted([p["change"] for p in processed], reverse=True)
    liqs = sorted([p["liquidity"] for p in processed], reverse=True)

    signals = []

    for p in processed:

        # rank score instead of raw math
        change_rank = changes.index(p["change"]) if p["change"] in changes else 0
        liq_rank = liqs.index(p["liquidity"]) if p["liquidity"] in liqs else 0

        score = (len(processed) - change_rank) * 0.6 + (len(processed) - liq_rank) * 0.4

        signals.append({
            "symbol": p["symbol"],
            "score": round(score, 2)
        })

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    top10 = signals[:10]

    total = sum([s["score"] for s in top10]) or 1

    portfolio = []

    for s in top10:

        portfolio.append({
            "symbol": s["symbol"],
            "weight": round(s["score"] / total, 3)
        })

    return {
        "regime": "NEUTRAL",
        "signals": top10,
        "portfolio": portfolio
    }
