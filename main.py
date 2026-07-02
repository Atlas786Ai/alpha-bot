from fastapi import FastAPI
import os
import datetime

app = FastAPI()


# =========================
# DEFINE CURRENT VERSION
# =========================
CURRENT_MODEL = "SOLANA_AI_V32_UNIVERSE_DISCOVERY"


# =========================
# DETECT RUNNING VERSION
# =========================
def detect_running_version():

    """
    This reads what is actually running in memory
    """

    return os.getenv("MODEL_VERSION", "UNKNOWN")


# =========================
# VERSION GUARD CORE
# =========================
def version_guard():

    running = detect_running_version()

    reported = CURRENT_MODEL

    if running == "UNKNOWN":
        status = "UNKNOWN"
    elif running != reported:
        status = "OUTDATED"
    else:
        status = "OK"

    return {
        "reported_model": reported,
        "running_model": running,
        "status": status,
        "timestamp": str(datetime.datetime.utcnow()),
        "fix_hint": (
            "Redeploy Render service"
            if status == "OUTDATED"
            else "System OK"
        )
    }


# =========================
# ROOT
# =========================
@app.get("/")
def home():

    return {
        "system": "V-GUARD ACTIVE",
        "model": CURRENT_MODEL
    }


# =========================
# UPDATE ENDPOINT (IMPORTANT)
# =========================
@app.get("/update")
def update():

    return {
        "model_output": CURRENT_MODEL,
        "version_check": version_guard(),
        "equity": 100.0
    }
