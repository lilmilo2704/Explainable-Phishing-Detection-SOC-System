"""
Local explanation service for PhishGuard.

Uses the EBM surrogate model's explain_local() to generate per-instance
feature attributions, then converts them into human-readable SOC analyst output.
"""

import logging
import numpy as np
from services.ml_service.model_loader import get_ebm_random_forest
from services.ml_service.preprocessor import build_feature_vector, get_numeric_feature_names, NUMERIC_FEATURES, N_ONEHOT, N_LABELCAT
from services.ml_service.feature_engineering.feature_extractor import extract_raw_features

logger = logging.getLogger(__name__)

EXPLAINER_TYPE = "EBM (surrogate of Random Forest)"
MODEL_VERSION = "rf_v1"

# Human-readable reason templates for known numeric features
HUMAN_REASONS: dict[str, str] = {
    "subject_len": "The email subject length is unusual.",
    "body_len": "The email body length is a signal for classification.",
    "subject_exclamation_count": "The subject contains exclamation marks which are common in phishing.",
    "body_exclamation_count": "The body contains many exclamation marks, a common phishing tactic.",
    "subject_urgent_word_count": "The subject contains urgent or alarming keywords.",
    "body_urgent_word_count": "The body contains urgent or threatening language.",
    "body_action_word_count": "The body requests an action (e.g. click, verify, confirm).",
    "click_here_count": "The email contains explicit 'click here' instructions.",
    "sender_reply_domain_mismatch": "The reply-to domain does not match the sender domain.",
    "sender_reply_domain_same": "The sender and reply-to addresses share the same domain.",
    "sender_is_free_provider": "The sender is using a free email provider (e.g. Gmail, Yahoo).",
    "sender_domain_has_digit": "The sender domain contains digits, a common spoofing indicator.",
    "sender_missing": "The sender address is missing or malformed.",
    "reply_missing": "No reply-to address is present.",
    "sender_replyto_mismatch": "The reply-to address does not match the sender address.",
    "suspicious_sender_domain": "The sender domain appears suspicious or impersonates a known brand.",
    "max_url_len": "The email contains an unusually long URL.",
    "url_suspicious_token_count": "The URLs contain suspicious tokens (e.g. 'verify', 'login', 'account').",
    "url_has_ip_host": "One or more URLs use a raw IP address instead of a domain name.",
    "url_shortener_count": "The email contains shortened URLs that mask the real destination.",
    "url_at_symbol_count": "URLs contain '@' symbols which can be used to disguise phishing links.",
    "url_https_count": "Number of HTTPS URLs present.",
    "url_http_count": "Number of HTTP (non-secure) URLs present.",
    "has_long_url": "At least one URL is unusually long.",
    "has_links": "The email contains hyperlinks.",
    "has_attachment": "The email contains one or more attachments.",
    "attachment_has_macro_or_archive": "An attachment has a suspicious file type (macro, archive, or executable).",
    "money_symbol_count": "The body contains money symbols, often used in financial phishing.",
    "http_count_body": "The body contains inline HTTP links.",
    "body_email_address_count": "The body contains email addresses, sometimes used in spear-phishing.",
    "has_urgent_words": "The email contains urgency-related keywords.",
    "suspicious_attachment_type": "The attachment type is suspicious.",
    "body_upper_ratio": "A high proportion of uppercase letters in the body text.",
    "subject_upper_ratio": "A high proportion of uppercase letters in the subject line.",
}

DIRECTION_THRESHOLD = 0.0  # contributions > 0 increase risk; < 0 decrease risk


def _get_human_reason(feature_name: str, raw_value, contribution: float) -> str:
    clean = feature_name.replace("num__", "").replace("onehotcat__", "").replace("labelcat__", "")
    reason = HUMAN_REASONS.get(clean)
    if reason:
        return reason
    direction = "increases" if contribution > 0 else "decreases"
    return f"Feature '{clean}' (value: {raw_value}) {direction} phishing risk."


def explain_local(email: dict, email_id: str = "unknown") -> dict:
    """
    Generate a local explanation for a single email using the EBM surrogate.

    Returns a dict matching the expected local explanation schema.
    """
    ebm = get_ebm_random_forest()
    if ebm is None:
        logger.warning("EBM model not available; returning empty explanation.")
        return _fallback_explanation(email_id)

    try:
        raw = extract_raw_features(email)
        X = build_feature_vector(raw)
        explanation = ebm.explain_local(X)
        data = explanation.data(0)

        # data["names"] = feature names, data["scores"] = contributions
        names = data.get("names", [])
        scores = data.get("scores", [])

        # Build feature contribution list — only numeric features for readability
        contributions = []
        for name, score in zip(names, scores):
            if not name.startswith("num__"):
                continue
            clean_name = name[len("num__"):]
            raw_value = raw.get(clean_name, 0)
            direction = "increases_phishing_risk" if score > 0 else "decreases_phishing_risk"
            human_reason = _get_human_reason(name, raw_value, score)
            contributions.append({
                "feature": clean_name,
                "value": raw_value,
                "contribution": round(float(score), 4),
                "direction": direction,
                "human_reason": human_reason,
            })

        # Sort by absolute contribution descending, take top 8
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        top_features = contributions[:8]

        human_summary = _build_human_summary(top_features, email_id)

        return {
            "email_id": email_id,
            "explainer_type": EXPLAINER_TYPE,
            "model_version": MODEL_VERSION,
            "human_summary": human_summary,
            "top_features": top_features,
        }

    except Exception as e:
        logger.error(f"Local explanation error for {email_id}: {e}")
        return _fallback_explanation(email_id)


def _build_human_summary(top_features: list, email_id: str) -> str:
    if not top_features:
        return "No strong feature signals were identified for this email."
    risk_drivers = [f for f in top_features if f["direction"] == "increases_phishing_risk"]
    if not risk_drivers:
        return "This email does not exhibit strong phishing characteristics based on the analysed features."
    reasons = [f["human_reason"].rstrip(".") for f in risk_drivers[:3]]
    joined = "; ".join(reasons)
    return (
        f"This email was flagged primarily because: {joined}. "
        "These factors collectively increase the phishing risk score. "
        "This explanation is provided as analytical support — human analyst review is recommended."
    )


def _fallback_explanation(email_id: str) -> dict:
    return {
        "email_id": email_id,
        "explainer_type": EXPLAINER_TYPE,
        "model_version": MODEL_VERSION,
        "model_failed": True,
        "human_summary": "model failed",
        "top_features": [],
    }
