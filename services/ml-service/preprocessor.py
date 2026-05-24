"""Validated preprocessing entry point for live inference.

The runtime may only produce a trusted prediction when the fitted training
preprocessor and processed feature order are present and validate successfully.
A numeric-plus-zero-padding fallback remains available solely for visibly
untrusted shadow-mode previews while missing artifacts are being recovered.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np


NUMERIC_FEATURES = [
    "subject_len", "body_len", "subject_word_count", "body_word_count",
    "subject_exclamation_count", "body_exclamation_count",
    "subject_question_count", "body_question_count",
    "subject_digit_count", "body_digit_count",
    "subject_upper_ratio", "body_upper_ratio",
    "money_symbol_count", "subject_urgent_word_count", "body_urgent_word_count",
    "body_action_word_count", "click_here_count", "body_email_address_count",
    "http_count_body", "sender_missing", "reply_missing",
    "sender_reply_domain_same", "sender_reply_domain_mismatch",
    "sender_domain_has_digit", "sender_local_has_digit", "sender_is_free_provider",
    "sender_domain_len", "replyto_domain_len",
    "url_count_parsed", "distinct_url_domain_count",
    "distinct_url_registered_domain_count",
    "url_https_count", "url_http_count", "url_other_scheme_count",
    "url_has_ip_host", "url_shortener_count", "url_hyphen_host_count",
    "url_at_symbol_count", "url_query_count", "url_fragment_count",
    "url_port_count", "url_percent_encoded_count", "url_suspicious_token_count",
    "url_digit_char_count", "max_url_len", "mean_url_len", "max_url_dot_count",
    "primary_url_subdomain_depth", "max_url_path_depth", "has_long_url",
    "attachment_count_parsed", "attachment_has_macro_or_archive",
    "num_links", "has_links", "num_attachments", "has_attachment",
    "has_urgent_words", "sender_replyto_mismatch",
    "suspicious_sender_domain", "suspicious_attachment_type",
]

N_ONEHOT = 227
N_LABELCAT = 5
N_TOTAL = len(NUMERIC_FEATURES) + N_ONEHOT + N_LABELCAT
CATEGORICAL_FEATURES = [
    "url_scheme",
    "url_tld",
    "sender_domain",
    "replyto_domain",
    "sender_tld",
    "replyto_tld",
    "primary_url_registered_domain",
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessors" / "preprocessor.pkl"
FEATURE_SCHEMA_PATH = PROJECT_ROOT / "models" / "preprocessors" / "expected_feature_schema.json"
PROCESSED_ORDER_PATH = PROJECT_ROOT / "models" / "preprocessors" / "processed_feature_order.json"


class UnsafePreprocessingError(RuntimeError):
    """Raised when a trusted prediction cannot be produced."""


def _load_schema() -> dict[str, Any] | None:
    if not FEATURE_SCHEMA_PATH.exists():
        return None
    with open(FEATURE_SCHEMA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_raw_feature_schema(raw_features: dict[str, Any]) -> dict[str, Any]:
    schema = _load_schema()
    expected = (
        schema.get("numeric_features", NUMERIC_FEATURES)
        + schema.get("categorical_features", CATEGORICAL_FEATURES)
        if schema
        else NUMERIC_FEATURES + CATEGORICAL_FEATURES
    )
    missing = [name for name in expected if name not in raw_features]
    extra = sorted(set(raw_features).difference(expected))
    return {
        "feature_schema_loaded": schema is not None,
        "missing_features": missing,
        "extra_features": extra,
        "raw_feature_count": len(raw_features),
    }


def get_preprocessing_readiness(raw_features: dict[str, Any] | None = None) -> dict[str, Any]:
    default_features = {name: 0 for name in NUMERIC_FEATURES}
    default_features.update({name: "none" for name in CATEGORICAL_FEATURES})
    validation = validate_raw_feature_schema(raw_features or default_features)
    preprocessor_loaded = PREPROCESSOR_PATH.exists()
    order_loaded = PROCESSED_ORDER_PATH.exists()
    feature_count_match = False
    feature_order_match = False
    if order_loaded:
        try:
            with open(PROCESSED_ORDER_PATH, "r", encoding="utf-8") as handle:
                processed_order = json.load(handle)
            feature_count_match = isinstance(processed_order, list) and len(processed_order) == N_TOTAL
            if preprocessor_loaded and feature_count_match:
                with open(PREPROCESSOR_PATH, "rb") as handle:
                    preprocessor = pickle.load(handle)
                fitted_order = [str(name) for name in preprocessor.get_feature_names_out()]
                feature_order_match = fitted_order == processed_order
        except Exception:
            feature_count_match = False
            feature_order_match = False
    safe = (
        preprocessor_loaded
        and validation["feature_schema_loaded"]
        and not validation["missing_features"]
        and feature_count_match
        and feature_order_match
    )
    return {
        **validation,
        "preprocessor_loaded": preprocessor_loaded,
        "feature_count_match": feature_count_match,
        "feature_order_match": feature_order_match,
        "expected_processed_feature_count": N_TOTAL,
        "processed_feature_order_loaded": order_loaded,
        "safe_for_live_prediction": safe,
        "recommended_action_if_unsafe": (
            None
            if safe
            else "Restore and validate the fitted training preprocessor before trusted automatic action."
        ),
    }


def _unsafe_preview_vector(raw_features: dict[str, Any]) -> np.ndarray:
    numeric = np.array([float(raw_features.get(name, 0) or 0) for name in NUMERIC_FEATURES], dtype=np.float64)
    categorical_placeholder = np.zeros(N_ONEHOT + N_LABELCAT, dtype=np.float64)
    return np.concatenate([numeric, categorical_placeholder]).reshape(1, -1)


def build_feature_vector(raw_features: dict[str, Any], *, allow_unsafe_preview: bool = False) -> np.ndarray:
    readiness = get_preprocessing_readiness(raw_features)
    if not readiness["safe_for_live_prediction"]:
        if allow_unsafe_preview:
            return _unsafe_preview_vector(raw_features)
        raise UnsafePreprocessingError(readiness["recommended_action_if_unsafe"])

    try:
        with open(PREPROCESSOR_PATH, "rb") as handle:
            preprocessor = pickle.load(handle)
        row = {name: raw_features.get(name, 0) for name in NUMERIC_FEATURES}
        row.update({name: raw_features.get(name, "none") for name in CATEGORICAL_FEATURES})
        try:
            import pandas as pd

            transformed = preprocessor.transform(pd.DataFrame([row]))
        except ImportError:
            transformed = preprocessor.transform([row])
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()
        vector = np.asarray(transformed, dtype=np.float64)
    except Exception as exc:
        raise UnsafePreprocessingError(f"Training preprocessor could not transform the message: {exc}") from exc

    if vector.shape != (1, N_TOTAL):
        raise UnsafePreprocessingError(
            f"Processed vector does not match the expected training schema: expected (1, {N_TOTAL}), got {vector.shape}."
        )
    return vector


def get_numeric_feature_names() -> list[str]:
    return list(NUMERIC_FEATURES)
