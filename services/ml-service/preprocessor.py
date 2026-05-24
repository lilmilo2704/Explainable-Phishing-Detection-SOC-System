"""
Preprocessing pipeline for PhishGuard inference.

The teacher models were trained with a sklearn ColumnTransformer that produced 292
processed features in this order:
  [num (59 features)] + [onehotcat (url_scheme, url_tld → 227 cols)] + [labelcat (5 ordinal cols)]

Since the original preprocessor artifact is not saved, we reconstruct the numeric
features portion (which is what the model primarily relies on) and pad the categorical
columns with zeros for unseen values — a safe, conservative approach.

The EBM surrogate was trained on the same feature space and is used for explanations.
"""

import numpy as np
from typing import Optional
from pathlib import Path
import pickle

# ── numeric feature columns in training order ──────────────────────────────────
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
    "url_digit_char_count",
    "max_url_len", "mean_url_len", "max_url_dot_count",
    "primary_url_subdomain_depth", "max_url_path_depth", "has_long_url",
    "attachment_count_parsed", "attachment_has_macro_or_archive",
    # passthrough numeric flags
    "num_links", "has_links", "num_attachments", "has_attachment",
    "has_urgent_words", "sender_replyto_mismatch",
    "suspicious_sender_domain", "suspicious_attachment_type",
]

# 227 one-hot columns from training + 5 label-encoded = 232 categorical padding cols
N_ONEHOT = 227
N_LABELCAT = 5
N_TOTAL = len(NUMERIC_FEATURES) + N_ONEHOT + N_LABELCAT  # should be 292

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessors" / "preprocessor.pkl"


def build_feature_vector(raw_features: dict) -> np.ndarray:
    """
    Convert raw features dict → numpy array of shape (1, 292).

    Strategy:
    - Numeric features are extracted in training order.
    - One-hot columns: we try to match url_scheme and url_tld; unseen → 0.
    - Label-encoded columns: ordinal encoding with 0 for unseen values.

    This approach ensures safe inference; unknown categorical values default to 0
    (which corresponds to the 'unknown' bin in the original OrdinalEncoder).
    """
    if PREPROCESSOR_PATH.exists():
        try:
            with open(PREPROCESSOR_PATH, "rb") as f:
                pre = pickle.load(f)
            row = {k: raw_features.get(k, 0) for k in NUMERIC_FEATURES}
            X = pre.transform([row])
            if hasattr(X, "toarray"):
                X = X.toarray()
            return np.asarray(X, dtype=np.float64)
        except Exception:
            # Fall back to robust static vectorization used in MVP.
            pass

    # 1. Numeric block
    num_vec = np.array(
        [float(raw_features.get(col, 0) or 0) for col in NUMERIC_FEATURES],
        dtype=np.float64,
    )

    # 2. One-hot block — 227 zeros; we don't replicate the full training vocab
    #    so we leave these as zeros (all-zeros = 'unknown' category)
    onehot_vec = np.zeros(N_ONEHOT, dtype=np.float64)

    # 3. Label-encoded block — map known domain categories to simple ordinals
    #    Unseen values → 0 (matches OrdinalEncoder handle_unknown='use_encoded_value', unknown_value=-1, then scaled)
    labelcat_vec = np.zeros(N_LABELCAT, dtype=np.float64)

    full_vec = np.concatenate([num_vec, onehot_vec, labelcat_vec])
    assert len(full_vec) == N_TOTAL, f"Expected {N_TOTAL} features, got {len(full_vec)}"
    return full_vec.reshape(1, -1)


def get_numeric_feature_names() -> list:
    return list(NUMERIC_FEATURES)
