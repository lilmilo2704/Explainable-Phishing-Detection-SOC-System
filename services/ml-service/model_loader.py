"""
Model loader for PhishGuard ML service.
Loads teacher models and EBM surrogate models from the models/ directory.
"""

import pickle
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Path to the project root: services/ml-service/model_loader.py → up 2 levels = project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

TEACHER_DIR = PROJECT_ROOT / "models" / "teacher-models"
SURROGATE_DIR = PROJECT_ROOT / "models" / "surrogate-models"

_cache: dict = {}


def _load_pickle(path: Path, label: str):
    if label in _cache:
        return _cache[label]
    if not path.exists():
        logger.warning(f"Model artifact not found: {path}")
        return None
    logger.info(f"Loading {label} from {path} ...")
    with open(path, "rb") as f:
        obj = pickle.load(f)
    _cache[label] = obj
    logger.info(f"Loaded {label} OK.")
    return obj


def get_random_forest():
    return _load_pickle(TEACHER_DIR / "random_forest.pkl", "random_forest")


def get_deep_neural_net():
    return _load_pickle(TEACHER_DIR / "deep_neural_net.pkl", "deep_neural_net")


def get_ebm_random_forest():
    return _load_pickle(SURROGATE_DIR / "ebm_random_forest.pkl", "ebm_random_forest")


def get_ebm_dnn():
    return _load_pickle(SURROGATE_DIR / "ebm_deep_neural_net.pkl", "ebm_deep_neural_net")
