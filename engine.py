import requests

# --- SOURCE 1: CoinGecko backup (safe endpoint)
def get_coingecko():

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": False
        }

        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()

        return [
            {
                "symbol": c.get("symbol", "").upper(),
                "change": c.get("price_change_percentage_24h", 0) or 0,
                "volume": c.get("total_volume", 0) or 0
            }
            for c in data
        ]

    except:
        return []


# --- SOURCE 2: fallback fake market (guaranteed)
def fallback_market():

    return [
        {"symbol": "BTC", "change": 2.1, "volume": 1000000000},
        {"symbol": "ETH", "change": 1.5, "volume": 500000000},
        {"symbol": "SOL", "change": 4.2, "volume": 800000000},
        {"symbol": "BNB", "change": 1.1, "volume": 300000000}
    ]


def run_engine():

    data = get_coingecko()

    source = "COINGECKO"

    if len(data) == 0:
        data = fallback_market()
        source = "FALLBACK"

    signals = []

    for c in data:

        score = c["change"] * 1.5 + (c["volume"] / 1e9)

        signals.append({
            "symbol": c["symbol"],
            "score": round(score, 3)
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
        "source": source,
        "regime": "LIVE",
        "signals": top10,
        "portfolio": portfolio
    }
