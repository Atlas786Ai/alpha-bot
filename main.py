from fastapi import FastAPI
import os
import datetime
import hashlib

app = FastAPI()


# =========================
# CONFIG
# =========================
DESIRED_MODEL = "SOLANA_AI_V32_UNIVERSE_DISCOVERY"


# =========================
# SIMULATED GIT STATE
# =========================
def get_git_commit():

    """
    Render doesn't always expose git info,
    so we simulate / fallback
    """

    return os.getenv("GIT_COMMIT", "UNKNOWN_COMMIT")


def get_runtime_model():

    return os.getenv("MODEL_VERSION", "SOLANA_AI_V28_LEGACY")


# =========================
# HASH SIGNATURE CHECK
# =========================
def compute_signature():

    base = get_runtime_model() + get_git_commit()

    return hashlib.sha256(base.encode()).hexdigest()


# =========================
# HEALTH SCORE ENGINE
# =========================
def health_score(runtime, desired, commit):

    score = 100

    if runtime != desired:
        score -= 60

    if commit == "UNKNOWN_COMMIT":
        score -= 20

    if runtime.startswith("SOLANA_AI_V28"):
        score -= 25

    return max(score, 0)


# =========================
# VERSION COMPARATOR
# =========================
def vguard_pro():

    runtime = get_runtime_model()
    commit = get_git_commit()

    signature = compute_signature()

    is_outdated = runtime != DESIRED_MODEL

    health = health_score(runtime, DESIRED_MODEL, commit)

    status = "OK"

    if health < 50:
        status = "CRITICAL"
    elif is_outdated:
        status = "OUTDATED"
    elif commit == "UNKNOWN_COMMIT":
        status = "UNSTABLE"

    return {
        "desired_model": DESIRED_MODEL,
        "running_model": runtime,
        "git_commit": commit,
        "signature": signature,
        "health_score": health,
        "status": status,
        "timestamp": str(datetime.datetime.utcnow()),
        "fix_actions": generate_fix(status, runtime)
    }


# =========================
# AUTO FIX SUGGESTION ENGINE
# =========================
def generate_fix(status, runtime):

    fixes = []

    if status == "OUTDATED":
        fixes.append("🔁 Redeploy latest commit on Render")

    if runtime.startswith("SOLANA_AI_V28"):
        fixes.append("⚠ Upgrade main.py to V32 engine")

    if status == "CRITICAL":
        fixes.append("🔥 Restart service + force rebuild")

    if len(fixes) == 0:
        fixes.append("✅ No action required")

    return fixes


# =========================
# ROOT
# =========================
@app.get("/")
def home():

    return {
        "system": "V-GUARD PRO ACTIVE",
        "model": DESIRED_MODEL
    }


# =========================
# UPDATE ENDPOINT
# =========================
@app.get("/update")
def update():

    return {
        "model": DESIRED_MODEL,
        "vguard": vguard_pro()
    }


# =========================
# HEALTH ENDPOINT (NEW)
# =========================
@app.get("/health")
def health():

    v = vguard_pro()

    return {
        "health_score": v["health_score"],
        "status": v["status"],
        "runtime_model": v["running_model"]
    }
