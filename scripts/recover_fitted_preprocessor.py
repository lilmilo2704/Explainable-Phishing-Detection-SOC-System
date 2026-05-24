"""Deterministically rebuild and validate the missing fitted training preprocessor.

The original repository saved teacher models and the processed dataset but did
not commit its `preprocessor.pkl`. This recovery procedure fits the preserved
training transformation on the original Git LFS raw dataset and only installs
the rebuilt pickle if it reproduces the archived processed split dataset.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pickle
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATASET = PROJECT_ROOT / ".recovery" / "original-research" / "csv" / "raw" / "business_phishing_dataset.csv"
PROCESSED_DATASET = (
    PROJECT_ROOT / ".recovery" / "original-research" / "csv" / "processed" / "processed_dataset_with_split.csv"
)
PIPELINE_SOURCE = (
    PROJECT_ROOT / ".recovery" / "original-research" / "code" / "teacher_training" / "train_model_pipeline.py"
)
ORDER_PATH = PROJECT_ROOT / "models" / "preprocessors" / "processed_feature_order.json"
OUTPUT_PATH = PROJECT_ROOT / "models" / "preprocessors" / "preprocessor.pkl"
PROVENANCE_PATH = PROJECT_ROOT / "models" / "preprocessors" / "preprocessor_provenance.json"

EXPECTED_RAW_SHA256 = "3dada9a6ffad73e62062d9a5304b348a21249af9ad556b20f05576310ae6e20e"
EXPECTED_PROCESSED_SHA256 = "5e505131a5af560b0099f35c59b82fb2d979e3d600acd3010b37dd994d4ba211"
RANDOM_STATE = 42


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_matching_source(path: Path, expected: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required Git LFS training input is missing: {path}")
    actual = _sha256(path)
    if actual != expected:
        raise RuntimeError(f"Training input does not match the original Git LFS object: {path.name}")


def _load_pipeline_helpers():
    if not PIPELINE_SOURCE.exists():
        raise FileNotFoundError(f"Original training script is missing: {PIPELINE_SOURCE}")
    spec = importlib.util.spec_from_file_location("original_training_pipeline", PIPELINE_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the original training pipeline.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    original_cwd = Path.cwd()
    try:
        os.chdir(PIPELINE_SOURCE.parent)
        spec.loader.exec_module(module)
    finally:
        os.chdir(original_cwd)
    return module


def _engineer_training_features(raw_df: pd.DataFrame, source) -> tuple[pd.DataFrame, pd.Series, list[str], list[str], list[str]]:
    text_cols = [
        "subject",
        "body",
        "sender_email",
        "reply_to",
        "urls",
        "attachments",
        "attack_type",
        "source_file",
    ]
    for col in text_cols:
        if col in raw_df.columns:
            raw_df[col] = raw_df[col].fillna("").astype(str)
    if "label" not in raw_df.columns:
        raise ValueError("Original dataset does not contain a label column.")

    feat_df = raw_df.copy()
    feat_df["parsed_urls"] = feat_df["urls"].apply(source.parse_list_cell)
    feat_df["parsed_attachments"] = feat_df["attachments"].apply(source.parse_list_cell)
    feat_df["subject_len"] = feat_df["subject"].str.len()
    feat_df["body_len"] = feat_df["body"].str.len()
    feat_df["subject_word_count"] = feat_df["subject"].str.split().str.len()
    feat_df["body_word_count"] = feat_df["body"].str.split().str.len()
    feat_df["subject_exclamation_count"] = feat_df["subject"].str.count("!")
    feat_df["body_exclamation_count"] = feat_df["body"].str.count("!")
    feat_df["subject_question_count"] = feat_df["subject"].str.count(r"\?")
    feat_df["body_question_count"] = feat_df["body"].str.count(r"\?")
    feat_df["subject_digit_count"] = feat_df["subject"].str.count(r"\d")
    feat_df["body_digit_count"] = feat_df["body"].str.count(r"\d")
    feat_df["subject_upper_ratio"] = feat_df["subject"].apply(
        lambda value: sum(char.isupper() for char in value) / max(len(value), 1)
    )
    feat_df["body_upper_ratio"] = feat_df["body"].apply(
        lambda value: sum(char.isupper() for char in value) / max(len(value), 1)
    )
    feat_df["money_symbol_count"] = feat_df["body"].str.count(r"[$\u20ac\u00a3]")
    feat_df["subject_urgent_word_count"] = feat_df["subject"].apply(
        lambda value: len(source.URGENT_PATTERN.findall(value))
    )
    feat_df["body_urgent_word_count"] = feat_df["body"].apply(
        lambda value: len(source.URGENT_PATTERN.findall(value))
    )
    feat_df["body_action_word_count"] = feat_df["body"].apply(
        lambda value: len(source.ACTION_PATTERN.findall(value))
    )
    feat_df["click_here_count"] = feat_df["body"].str.count(r"click here", flags=source.re.IGNORECASE)
    feat_df["body_email_address_count"] = feat_df["body"].apply(
        lambda value: len(source.EMAIL_ADDRESS_PATTERN.findall(value))
    )
    feat_df["http_count_body"] = feat_df["body"].str.count(r"https?://", flags=source.re.IGNORECASE)
    feat_df["sender_domain"] = feat_df["sender_email"].apply(source.extract_domain_from_email)
    feat_df["replyto_domain"] = feat_df["reply_to"].apply(source.extract_domain_from_email)
    feat_df["sender_tld"] = feat_df["sender_domain"].apply(source.extract_tld_from_domain)
    feat_df["replyto_tld"] = feat_df["replyto_domain"].apply(source.extract_tld_from_domain)
    feat_df["sender_localpart"] = feat_df["sender_email"].apply(source.extract_localpart_from_email)
    feat_df["sender_missing"] = feat_df["sender_domain"].eq("unknown").astype(int)
    feat_df["reply_missing"] = feat_df["replyto_domain"].eq("unknown").astype(int)
    feat_df["sender_reply_domain_same"] = (
        (feat_df["sender_domain"] != "unknown")
        & (feat_df["replyto_domain"] != "unknown")
        & feat_df["sender_domain"].eq(feat_df["replyto_domain"])
    ).astype(int)
    feat_df["sender_reply_domain_mismatch"] = (
        (feat_df["replyto_domain"] != "unknown") & feat_df["sender_domain"].ne(feat_df["replyto_domain"])
    ).astype(int)
    feat_df["sender_domain_has_digit"] = feat_df["sender_domain"].str.contains(r"\d", regex=True).astype(int)
    feat_df["sender_local_has_digit"] = feat_df["sender_localpart"].str.contains(r"\d", regex=True).astype(int)
    feat_df["sender_is_free_provider"] = feat_df["sender_domain"].isin(source.FREE_EMAIL_PROVIDERS).astype(int)
    feat_df["sender_domain_len"] = feat_df["sender_domain"].str.len()
    feat_df["replyto_domain_len"] = feat_df["replyto_domain"].str.len()

    url_features = pd.DataFrame(feat_df["parsed_urls"].apply(source.build_url_features).tolist(), index=feat_df.index)
    attachment_features = pd.DataFrame(
        feat_df["parsed_attachments"].apply(source.build_attachment_features).tolist(), index=feat_df.index
    )
    feat_df = pd.concat([feat_df, url_features, attachment_features], axis=1)
    numeric_features = [
        "subject_len", "body_len", "subject_word_count", "body_word_count",
        "subject_exclamation_count", "body_exclamation_count", "subject_question_count", "body_question_count",
        "subject_digit_count", "body_digit_count", "subject_upper_ratio", "body_upper_ratio",
        "money_symbol_count", "subject_urgent_word_count", "body_urgent_word_count", "body_action_word_count",
        "click_here_count", "body_email_address_count", "http_count_body", "sender_missing", "reply_missing",
        "sender_reply_domain_same", "sender_reply_domain_mismatch", "sender_domain_has_digit",
        "sender_local_has_digit", "sender_is_free_provider", "sender_domain_len", "replyto_domain_len",
        "url_count_parsed", "distinct_url_domain_count", "distinct_url_registered_domain_count",
        "url_https_count", "url_http_count", "url_other_scheme_count", "url_has_ip_host", "url_shortener_count",
        "url_hyphen_host_count", "url_at_symbol_count", "url_query_count", "url_fragment_count", "url_port_count",
        "url_percent_encoded_count", "url_suspicious_token_count", "url_digit_char_count", "max_url_len",
        "mean_url_len", "max_url_dot_count", "primary_url_subdomain_depth", "max_url_path_depth",
        "has_long_url", "attachment_count_parsed", "attachment_has_macro_or_archive", "num_links", "has_links",
        "num_attachments", "has_attachment", "has_urgent_words", "sender_replyto_mismatch",
        "suspicious_sender_domain", "suspicious_attachment_type",
    ]
    numeric_features = [feature for feature in numeric_features if feature in feat_df.columns]
    onehot_features = [feature for feature in ["url_scheme", "url_tld"] if feature in feat_df.columns]
    label_features = [
        feature
        for feature in ["sender_domain", "replyto_domain", "sender_tld", "replyto_tld", "primary_url_registered_domain"]
        if feature in feat_df.columns
    ]
    feat_df["label"] = feat_df["label"].astype(int)
    columns = numeric_features + onehot_features + label_features
    return feat_df[columns].copy(), feat_df["label"].copy(), numeric_features, onehot_features, label_features


def _build_preprocessor(numeric_features: list[str], onehot_features: list[str], label_features: list[str]) -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    label_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("label_encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
            ("scaler", StandardScaler()),
        ]
    )
    try:
        one_hot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        one_hot = OneHotEncoder(handle_unknown="ignore", sparse=False)
    onehot_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", one_hot)]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("onehotcat", onehot_transformer, onehot_features),
            ("labelcat", label_transformer, label_features),
        ]
    )


def _validate_processed_splits(
    preprocessor: ColumnTransformer,
    expected_order: list[str],
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
    y_test: pd.Series,
) -> None:
    reader = pd.read_csv(PROCESSED_DATASET, chunksize=4096)
    pending: pd.DataFrame | None = None
    for split_name, rows, labels in (
        ("train", X_train, y_train),
        ("val", X_val, y_val),
        ("test", X_test, y_test),
    ):
        transformed = np.asarray(preprocessor.transform(rows), dtype=np.float64)
        offset = 0
        while offset < len(rows):
            if pending is None:
                try:
                    pending = next(reader)
                except StopIteration as exc:
                    raise RuntimeError("Original processed dataset ended before validation completed.") from exc
            count = min(len(pending), len(rows) - offset)
            saved = pending.iloc[:count]
            pending = pending.iloc[count:] if count < len(pending) else None
            if not saved["split"].eq(split_name).all():
                raise RuntimeError(f"Saved processed split order differs while validating '{split_name}'.")
            expected_values = saved[expected_order].to_numpy(dtype=np.float64)
            actual_values = transformed[offset : offset + count]
            if not np.allclose(actual_values, expected_values, rtol=1e-10, atol=1e-12):
                mismatched = ~np.isclose(actual_values, expected_values, rtol=1e-10, atol=1e-12)
                column_indexes = np.flatnonzero(mismatched.any(axis=0))
                column_names = [expected_order[index] for index in column_indexes[:10]]
                max_difference = float(np.nanmax(np.abs(actual_values - expected_values)))
                raise RuntimeError(
                    f"Reconstructed preprocessing values differ from the original '{split_name}' split. "
                    f"Mismatched columns include {column_names}; max absolute difference={max_difference:.12g}."
                )
            if not np.array_equal(labels.to_numpy()[offset : offset + count], saved["label"].to_numpy()):
                raise RuntimeError(f"Reconstructed split labels differ from the original '{split_name}' split.")
            offset += count
        del transformed
    if pending is not None and not pending.empty:
        raise RuntimeError("Original processed dataset contains extra rows after validation.")
    try:
        next(reader)
    except StopIteration:
        return
    raise RuntimeError("Original processed dataset contains extra rows after validation.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate a previously installed preprocessor without rewriting it.")
    args = parser.parse_args()
    _require_matching_source(RAW_DATASET, EXPECTED_RAW_SHA256)
    _require_matching_source(PROCESSED_DATASET, EXPECTED_PROCESSED_SHA256)

    with open(ORDER_PATH, "r", encoding="utf-8") as handle:
        expected_order = json.load(handle)
    source = _load_pipeline_helpers()
    raw_df = pd.read_csv(RAW_DATASET, low_memory=False)
    X, y, numeric_features, onehot_features, label_features = _engineer_training_features(raw_df, source)
    del raw_df
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=(2 / 3), random_state=RANDOM_STATE, stratify=y_temp
    )
    del X, y, X_temp, y_temp

    if args.check:
        if not OUTPUT_PATH.exists():
            raise FileNotFoundError(f"Fitted preprocessor has not been installed: {OUTPUT_PATH}")
        with open(OUTPUT_PATH, "rb") as handle:
            preprocessor = pickle.load(handle)
    else:
        preprocessor = _build_preprocessor(numeric_features, onehot_features, label_features)
        preprocessor.fit(X_train)
    fitted_order = [str(name) for name in preprocessor.get_feature_names_out()]
    if fitted_order != expected_order:
        raise RuntimeError("Reconstructed preprocessor feature order differs from the order preserved by the fitted EBM.")
    _validate_processed_splits(preprocessor, expected_order, X_train, X_val, X_test, y_train, y_val, y_test)

    if not args.check:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "wb") as handle:
            pickle.dump(preprocessor, handle)
        provenance = {
            "artifact_type": "fitted_training_preprocessor",
            "recovery_method": "deterministic_refit_verified_against_original_processed_dataset",
            "recovered_at_utc": datetime.now(UTC).isoformat(),
            "raw_dataset_git_lfs_sha256": EXPECTED_RAW_SHA256,
            "processed_dataset_git_lfs_sha256": EXPECTED_PROCESSED_SHA256,
            "training_script": "code/teacher_training/train_model_pipeline.py",
            "feature_count": len(fitted_order),
            "validation": "all_saved_train_val_test_processed_values_and_labels_match",
        }
        with open(PROVENANCE_PATH, "w", encoding="utf-8") as handle:
            json.dump(provenance, handle, indent=2)
            handle.write("\n")
        print(f"Recovered fitted preprocessor: {len(fitted_order)} transformed features validated.")
    else:
        print(f"Validated fitted preprocessor: {len(fitted_order)} transformed features and all saved splits match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
