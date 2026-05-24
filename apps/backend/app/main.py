import sys
from pathlib import Path

# Make project root importable (needed for services/ml-service)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

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


app = FastAPI(
    title="Phishing Detection Dashboard API",
    description="SOC-friendly explainable phishing detection API.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.api_router)
run_startup_migrations()

@app.get("/health")
def health_check():
    return {"status": "ok"}
