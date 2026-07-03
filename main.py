from fastapi import FastAPI
import requests
import time
import math

app = FastAPI()

# =========================
# STATE
# =========================
STATE = {
    "equity": 100.0,
    "cache": None,
    "cache_time": 0,
    "last_error": None,
    "source_health": {
        "coingecko": True,
        "binance": True
    }
}

CACHE_TTL = 60


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "model": "ATLAS_CANONICAL_V7",
        "status": "MULTI_SOURCE_INSTITUTIONAL_ENGINE"
    }


# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {
        "model": "V7",
        "coingecko": STATE["source_health"]["coingecko"],
        "binance": STATE["source_health"]["binance"],
        "cache_age": round(time.time() - STATE["cache_time"], 2),
        "equity": STATE["equity"]
    }


# =========================
# SAFE REQUEST
# =========================
def safe_get(url, params=None):

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=6)

        if r.status_code != 200:
            return None

        data = r.json()

        if not isinstance(data, list):
            return None

        return data

    except Exception as e:
        STATE["last_error"] = str(e)
        return None


# =========================
# BINANCE FALLBACK SOURCE
# =========================
def fetch_binance():

    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=6)
        data = r.json()

        cleaned = []

        for x in data[:50]:

            if "USDT" in x["symbol"]:

                cleaned.append({
                    "symbol": x["symbol"].replace("USDT", ""),
                    "change": float(x.get("priceChangePercent", 0)),
                    "volume": float(x.get("quoteVolume", 0)),
                    "rank": 50
                })

        return cleaned

    except:
        return []


# =========================
# COINGECKO SOURCE
# =========================
def fetch_coingecko():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false"
    }

    return safe_get(url, params)


# =========================
# UNIVERSE BUILDER (MULTI-SOURCE MERGE)
# =========================
def build_universe():

    cg = fetch_coingecko()
    bn = fetch_binance()

    universe = []

    if cg:
        STATE["source_health"]["coingecko"] = True

        for x in cg:
            universe.append({
                "symbol": x.get("symbol", "").upper(),
                "change": x.get("price_change_percentage_24h", 0) or 0,
                "volume": x.get("total_volume", 0) or 0,
                "rank": x.get("market_cap_rank", 999)
            })

    else:
        STATE["source_health"]["coingecko"] = False

    if bn:
        STATE["source_health"]["binance"] = True
        universe.extend(bn)
    else:
        STATE["source_health"]["binance"] = False

    # deduplicate (critical V7 improvement)
    seen = set()
    unique = []

    for x in universe:
        if x["symbol"] not in seen:
            seen.add(x["symbol"])
            unique.append(x)

    return unique


# =========================
# REGIME DETECTION (MARKET STATE)
# =========================
def detect_regime(market):

    changes = [x["change"] for x in market if x["change"] is not None]

    if not changes:
        return "UNKNOWN"

    avg = sum(changes) / len(changes)

    if avg > 1.5:
        return "BULL"
    elif avg < -1.5:
        return "BEAR"
    return "CHOP"


# =========================
# SCORE ENGINE (V7)
# =========================
def score(x, regime):

    momentum = x["change"] / 10
    liquidity = math.log1p(x["volume"])
    rank = 1 - min(x["rank"] / 100, 1)

    stability = 1 / (1 + abs(momentum))

    regime_factor = {
        "BULL": 1.15,
        "BEAR": 0.85,
        "CHOP": 1.0,
        "UNKNOWN": 1.0
    }[regime]

    return (
        momentum * 0.28 +
        liquidity * 0.25 +
        rank * 0.22 +
        stability * 0.25
    ) * regime_factor


# =========================
# CORRELATION DAMPENER (SIMPLIFIED)
# =========================
def dampen(scores):

    symbols = set()
    result = []

    for x in scores:

        # reduce duplication of same exposure
        if x["symbol"] in symbols:
            x["score"] *= 0.7
        else:
            symbols.add(x["symbol"])

        result.append(x)

    return result


# =========================
# UPDATE ENGINE V7
# =========================
@app.get("/update")
def update():

    market = build_universe()

    regime = detect_regime(market)

    scored = []

    for x in market:

        s = score(x, regime)

        scored.append({
            "symbol": x["symbol"],
            "score": round(s, 6),
            "change": x["change"],
            "rank": x["rank"]
        })

    scored = dampen(scored)

    scored.sort(key=lambda x: x["score"], reverse=True)

    top10 = scored[:10]

    total = sum(abs(x["score"]) for x in top10) or 1

    portfolio = [
        {
            "symbol": x["symbol"],
            "weight": round(abs(x["score"]) / total, 4)
        }
        for x in top10[:5]
    ]

    STATE["equity"] += sum(x["score"] for x in top10) / 25000

    return {
        "model": "ATLAS_CANONICAL_V7",
        "status": "MULTI_SOURCE_ACTIVE",
        "regime": regime,
        "universe_size": len(scored),
        "top10": top10,
        "portfolio": portfolio,
        "equity": round(STATE["equity"], 4),
        "sources": STATE["source_health"],
        "last_error": STATE["last_error"]
    }
