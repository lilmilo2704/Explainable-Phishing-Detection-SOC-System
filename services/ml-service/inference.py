"""
Inference service for PhishGuard.
Runs prediction using the Random Forest teacher model and returns
a structured result with confidence score, risk level, and recommended action.
"""

import logging
import numpy as np
from services.ml_service.model_loader import get_random_forest
from services.ml_service.preprocessor import build_feature_vector
from services.ml_service.feature_engineering.feature_extractor import extract_raw_features

logger = logging.getLogger(__name__)

MODEL_NAME = "Random Forest"
MODEL_VERSION = "rf_v1"


def _confidence_to_risk(confidence: float, prediction: str) -> tuple[str, str]:
    """Map phishing confidence → risk level + recommended action."""
    if prediction == "legitimate":
        return "low", "allow"
    if confidence >= 0.90:
        return "critical", "quarantine"
    if confidence >= 0.75:
        return "high", "quarantine"
    if confidence >= 0.55:
        return "medium", "review"
    return "low", "allow"


def predict(email: dict) -> dict:
    """
    Run phishing prediction on a raw email dict.

    Args:
        email: dict with keys like subject, body, sender_email, reply_to,
               urls (list), attachments (list), plus any pre-computed flags.

    Returns:
        dict with prediction, confidence, risk_level, recommended_action,
        model_name, model_version.
    """
    rf = get_random_forest()
    if rf is None:
        raise RuntimeError("Random Forest model could not be loaded.")
    if hasattr(rf, "n_jobs"):
        rf.n_jobs = 1

    try:
        raw = extract_raw_features(email)
        X = build_feature_vector(raw)
        proba = rf.predict_proba(X)[0]  # [prob_legit, prob_phishing]
        phishing_prob = float(proba[1])
        prediction = "phishing" if phishing_prob >= 0.5 else "legitimate"
        confidence = phishing_prob if prediction == "phishing" else float(proba[0])
        risk_level, recommended_action = _confidence_to_risk(phishing_prob, prediction)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "phishing_probability": round(phishing_prob, 4),
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
    }
