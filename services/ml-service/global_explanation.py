"""
Global explanation service for PhishGuard.

Extracts global feature importances and model behaviour metrics
from the EBM surrogate model and returns dashboard-ready JSON.
"""

import logging
import numpy as np
from services.ml_service.model_loader import get_ebm_random_forest
from services.ml_service.preprocessor import NUMERIC_FEATURES

logger = logging.getLogger(__name__)

HUMAN_SUMMARIES: dict[str, str] = {
    "sender_reply_domain_mismatch": "Reply-to domain mismatch is the strongest phishing indicator.",
    "suspicious_sender_domain": "Domains impersonating known brands are highly correlated with phishing.",
    "body_urgent_word_count": "Urgent language in the email body significantly increases phishing risk.",
    "subject_urgent_word_count": "Urgency keywords in the subject line are a strong phishing signal.",
    "body_action_word_count": "Requests for action (verify, confirm, reset) increase phishing risk.",
    "url_suspicious_token_count": "Suspicious tokens in URLs (e.g. 'account', 'verify') strongly indicate phishing.",
    "max_url_len": "Longer URLs generally increase phishing likelihood.",
    "has_long_url": "Presence of unusually long URLs is a phishing indicator.",
    "url_has_ip_host": "IP-based URLs are a strong indicator of phishing infrastructure.",
    "url_shortener_count": "Shortened URLs that mask the real destination increase phishing risk.",
    "sender_is_free_provider": "Phishing emails frequently originate from free email providers.",
    "attachment_has_macro_or_archive": "Macro-enabled or archive attachments are frequently used to deliver malware.",
    "sender_replyto_mismatch": "Reply-to address mismatch with sender is a reliable phishing signal.",
    "has_urgent_words": "The presence of urgency-related words increases phishing likelihood.",
    "click_here_count": "Explicit 'click here' instructions are commonly used in phishing emails.",
    "money_symbol_count": "Financial symbols in the body correlate with financial phishing attacks.",
    "sender_domain_has_digit": "Sender domains containing digits are often spoofed or auto-generated.",
}

FAILURE_PATTERNS = {
    "false_positives": [
        "Legitimate business emails with urgent wording and multiple links are sometimes misclassified.",
        "Automated system alerts from unrecognised internal domains may trigger high risk scores.",
        "Marketing emails from free email providers may be flagged due to free-provider signals.",
    ],
    "false_negatives": [
        "Phishing emails with clean-looking, compromised sender domains and short URLs are occasionally missed.",
        "Spear-phishing lacking urgent language and containing no links (e.g. BEC via reply) can evade detection.",
        "Emails from compromised legitimate accounts may not exhibit typical phishing feature patterns.",
    ],
}


def get_global_explanation() -> dict:
    """
    Generate global explanation from EBM surrogate model.
    Returns dashboard-ready JSON with feature importances and model metadata.
    """
    ebm = get_ebm_random_forest()
    if ebm is None:
        logger.warning("EBM not loaded; returning model-failed response.")
        return _model_failed_response()

    try:
        importances = ebm.term_importances()
        term_names = list(ebm.term_names_)

        # Filter to numeric features only for readability
        numeric_prefix = "num__"
        feature_data = []
        for name, imp in zip(term_names, importances):
            if not name.startswith(numeric_prefix):
                continue
            clean = name[len(numeric_prefix):]
            human_summary = HUMAN_SUMMARIES.get(clean, f"'{clean}' contributes to the phishing detection score.")
            feature_data.append({
                "feature": clean,
                "importance": round(float(imp), 4),
                "human_summary": human_summary,
            })

        # Sort by importance descending, take top 15
        feature_data.sort(key=lambda x: x["importance"], reverse=True)
        top_features = feature_data[:15]

        return {
            "model_name": "Random Forest",
            "model_version": "rf_v1",
            "surrogate_name": "EBM",
            "surrogate_version": "ebm_rf_v1",
            "accuracy_fidelity": 0.926,
            "f1_fidelity": 0.928,
            "error_fidelity": 0.7673,
            "top_features": top_features,
            "failure_patterns": FAILURE_PATTERNS,
            "generated_at": "2026-05-19T00:00:00Z",
        }

    except Exception as e:
        logger.error(f"Global explanation error: {e}")
        return _model_failed_response()


def _model_failed_response() -> dict:
    """Return fallback payload when global explanation model is unavailable."""
    return {
        "model_failed": True,
        "message": "model failed",
        "model_name": "Random Forest",
        "model_version": "rf_v1",
        "surrogate_name": "EBM",
        "surrogate_version": "ebm_rf_v1",
        "accuracy_fidelity": 0.0,
        "f1_fidelity": 0.0,
        "error_fidelity": 0.0,
        "top_features": [],
        "failure_patterns": {
            "false_positives": ["model failed"],
            "false_negatives": ["model failed"],
        },
        "generated_at": "2026-05-19T00:00:00Z",
    }
