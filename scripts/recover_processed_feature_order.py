"""Recover the processed feature order embedded in the trained EBM surrogate.

This utility deliberately does not attempt to invent or refit the missing
training preprocessor. It recovers only the exact transformed column order
that is preserved in the fitted surrogate model artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SURROGATE = PROJECT_ROOT / "models" / "surrogate-models" / "ebm_random_forest.pkl"
SECONDARY_SURROGATE = PROJECT_ROOT / "models" / "surrogate-models" / "ebm_deep_neural_net.pkl"
DEFAULT_TEACHER = PROJECT_ROOT / "models" / "teacher-models" / "random_forest.pkl"
ORDER_PATH = PROJECT_ROOT / "models" / "preprocessors" / "processed_feature_order.json"
PROVENANCE_PATH = PROJECT_ROOT / "models" / "preprocessors" / "processed_feature_order_provenance.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_pickle(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required model artifact not found: {path}")
    with open(path, "rb") as handle:
        return pickle.load(handle)


def recover_feature_order(surrogate_path: Path, teacher_path: Path) -> tuple[list[str], dict[str, Any]]:
    surrogate = _load_pickle(surrogate_path)
    embedded = getattr(surrogate, "feature_names_in_", None)
    if embedded is None:
        raise RuntimeError(f"The surrogate does not preserve feature_names_in_: {surrogate_path}")
    feature_order = [str(name) for name in embedded]
    if not feature_order or len(set(feature_order)) != len(feature_order):
        raise RuntimeError("Embedded processed feature order is empty or contains duplicate feature names.")

    teacher = _load_pickle(teacher_path)
    teacher_count = getattr(teacher, "n_features_in_", None)
    if teacher_count != len(feature_order):
        raise RuntimeError(
            "Teacher/surrogate feature count mismatch: "
            f"teacher expects {teacher_count}, surrogate preserves {len(feature_order)} names."
        )

    secondary_match = None
    if SECONDARY_SURROGATE.exists():
        secondary = _load_pickle(SECONDARY_SURROGATE)
        secondary_order = [str(name) for name in getattr(secondary, "feature_names_in_", [])]
        secondary_match = secondary_order == feature_order
        if not secondary_match:
            raise RuntimeError("The EBM surrogate artifacts do not agree on the processed feature order.")

    provenance = {
        "artifact_type": "processed_feature_order",
        "recovery_method": "extracted_from_fitted_surrogate_feature_names_in_",
        "recovered_at_utc": datetime.now(UTC).isoformat(),
        "feature_count": len(feature_order),
        "source_surrogate": str(surrogate_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "source_surrogate_sha256": _sha256(surrogate_path),
        "validated_teacher": str(teacher_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "validated_teacher_sha256": _sha256(teacher_path),
        "teacher_expected_feature_count": int(teacher_count),
        "secondary_surrogate_agrees": secondary_match,
        "preprocessor_recovered": False,
        "preprocessor_note": (
            "This artifact restores processed column order only. A fitted training preprocessor "
            "is still required before trusted live prediction."
        ),
    }
    return feature_order, provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate existing recovered output without writing files.")
    args = parser.parse_args()

    order, provenance = recover_feature_order(DEFAULT_SURROGATE, DEFAULT_TEACHER)
    if args.check:
        if not ORDER_PATH.exists():
            raise FileNotFoundError(f"Recovered order artifact is missing: {ORDER_PATH}")
        with open(ORDER_PATH, "r", encoding="utf-8") as handle:
            existing = json.load(handle)
        if existing != order:
            raise RuntimeError("Existing processed feature-order artifact differs from the fitted surrogate.")
        print(f"Validated processed feature order: {len(order)} columns match the fitted surrogate and teacher.")
        return 0

    ORDER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ORDER_PATH, "w", encoding="utf-8") as handle:
        json.dump(order, handle, indent=2)
        handle.write("\n")
    with open(PROVENANCE_PATH, "w", encoding="utf-8") as handle:
        json.dump(provenance, handle, indent=2)
        handle.write("\n")
    print(f"Recovered processed feature order: {len(order)} columns.")
    print("Validated against the active Random Forest feature count and matching EBM surrogate metadata.")
    print("The fitted training preprocessor remains unavailable; trusted prediction must remain blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
