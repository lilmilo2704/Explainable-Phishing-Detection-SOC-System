import sys
import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter
from pathlib import Path
from dotenv import load_dotenv

# Make project root importable (needed for services/ml-service)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
load_dotenv(_PROJECT_ROOT / ".env", override=False)

# Register the ml-service directory under the alias "services.ml_service"
_ML_SERVICE_DIR = _PROJECT_ROOT / "services" / "ml-service"
if str(_ML_SERVICE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_ML_SERVICE_DIR.parent))

# The hyphenated directory can't be imported directly; import it by adding its path
import importlib, types
_ml_mod = types.ModuleType("services.ml_service")
_ml_mod.__path__ = [str(_ML_SERVICE_DIR)]
sys.modules["services.ml_service"] = _ml_mod

_feat_eng_dir = _ML_SERVICE_DIR / "feature-engineering"
_feat_mod = types.ModuleType("services.ml_service.feature_engineering")
_feat_mod.__path__ = [str(_feat_eng_dir)]
sys.modules["services.ml_service.feature_engineering"] = _feat_mod

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.database import run_startup_migrations
from app.services.mailbox_integration import GmailMailboxProvider
from app.services.model_manager import model_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    gmail_status = GmailMailboxProvider().configuration_status()
    if not gmail_status["configured"]:
        logger.warning(
            "Gmail is not configured (%s missing). Configure local .env or place ignored local files at secrets/gmail/credentials.json and secrets/gmail/token.json.",
            ", ".join(gmail_status["missing"]),
        )
    elif gmail_status["configuration_source"] == "ignored_local_secrets":
        logger.info("Gmail configured from ignored local secrets/gmail files for manual sync.")
    if not model_manager.get_readiness()["safe_for_live_prediction"]:
        logger.warning(
            "Safety mode active: training preprocessing artifacts are not validated. Scans are stored for review and automatic model quarantine is blocked."
        )
    yield


app = FastAPI(
    title="Phishing Detection Dashboard API",
    description="SOC-friendly explainable phishing detection API.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.api_router)
run_startup_migrations()


@app.middleware("http")
async def log_request_summary(request, call_next):
    started = perf_counter()
    response = await call_next(request)
    elapsed_ms = (perf_counter() - started) * 1000
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


@app.get("/health")
def health_check():
    return {"status": "ok"}
