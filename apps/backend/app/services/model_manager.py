from __future__ import annotations

import json
import pickle
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.model_registry import DEFAULT_ACTIVE_CONFIG, MODEL_REGISTRY
from services.ml_service.feature_engineering.feature_extractor import extract_raw_features
from services.ml_service.preprocessor import (
    N_TOTAL,
    PROCESSED_ORDER_PATH,
    UnsafePreprocessingError,
    build_feature_vector,
    get_preprocessing_readiness,
)


class ModelManagerError(RuntimeError):
    pass


HUMAN_REASONS = {
    "sender_reply_domain_mismatch": "The reply-to domain differs from the sender domain.",
    "sender_replyto_mismatch": "The reply-to address differs from the sender address.",
    "max_url_len": "The email includes an unusually long URL.",
    "url_suspicious_token_count": "A link includes words often used in credential or payment prompts.",
    "url_has_ip_host": "A link uses an IP address rather than a named domain.",
    "url_shortener_count": "A shortened link obscures its destination.",
    "subject_urgent_word_count": "The subject uses urgency-related wording.",
    "body_urgent_word_count": "The message body uses urgency-related wording.",
    "body_action_word_count": "The message requests an action such as logging in or confirming details.",
    "has_attachment": "The email includes one or more attachments.",
}


class ModelManager:
    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[4]
        self.config_path = self.project_root / "apps" / "backend" / "config" / "active_model_config.json"
        self._cache: dict[str, Any] = {}
        self._active_config = self._load_or_init_active_config()

    def _absolute_model_path(self, relative_path: str) -> Path:
        return self.project_root / relative_path

    def _load_pickle(self, model_id: str) -> Any:
        if model_id in self._cache:
            return self._cache[model_id]
        config = MODEL_REGISTRY.get(model_id)
        if not config:
            raise ModelManagerError(f"Unknown model id: {model_id}")
        path = self._absolute_model_path(config["path"])
        if not path.exists():
            raise ModelManagerError(f"Model artifact not found: {path}")
        try:
            with open(path, "rb") as handle:
                model = pickle.load(handle)
        except Exception as exc:
            raise ModelManagerError(f"Unable to load model artifact for '{model_id}': {exc}") from exc
        self._cache[model_id] = model
        return model

    def _model_runtime_status(self, model_id: str) -> tuple[bool, str | None]:
        config = MODEL_REGISTRY.get(model_id, {})
        path = self._absolute_model_path(config.get("path", ""))
        if not path.exists():
            return False, "Model artifact is missing."
        if config.get("type") == "surrogate" and "gaminet" in model_id:
            try:
                __import__("tensorflow")
            except ModuleNotFoundError:
                return False, "TensorFlow is not installed for GAMI-Net runtime."
        return True, None

    def _validate_pairing(self, teacher_model_id: str, surrogate_model_id: str) -> None:
        teacher = MODEL_REGISTRY.get(teacher_model_id)
        surrogate = MODEL_REGISTRY.get(surrogate_model_id)
        if not teacher or teacher.get("type") != "teacher":
            raise ModelManagerError(f"Invalid teacher model: {teacher_model_id}")
        if not surrogate or surrogate.get("type") != "surrogate":
            raise ModelManagerError(f"Invalid surrogate model: {surrogate_model_id}")
        if surrogate_model_id not in teacher.get("valid_surrogates", []) or surrogate.get("teacher") != teacher_model_id:
            raise ModelManagerError(
                f"Incompatible model pairing: teacher '{teacher_model_id}' cannot use '{surrogate_model_id}'."
            )

    def _load_or_init_active_config(self) -> dict[str, str]:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self._write_active_config(DEFAULT_ACTIVE_CONFIG)
            return dict(DEFAULT_ACTIVE_CONFIG)
        with open(self.config_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        teacher_id = data.get("teacher_model_id")
        surrogate_id = data.get("surrogate_model_id")
        try:
            self._validate_pairing(teacher_id, surrogate_id)
        except ModelManagerError:
            self._write_active_config(DEFAULT_ACTIVE_CONFIG)
            return dict(DEFAULT_ACTIVE_CONFIG)
        return {"teacher_model_id": teacher_id, "surrogate_model_id": surrogate_id}

    def _write_active_config(self, config: dict[str, str]) -> None:
        with open(self.config_path, "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2)

    def get_registry_payload(self) -> dict[str, Any]:
        teachers: list[dict[str, Any]] = []
        surrogates: list[dict[str, Any]] = []
        for model_id, config in MODEL_REGISTRY.items():
            available, reason = self._model_runtime_status(model_id)
            row = {"id": model_id, "available": available, "unavailable_reason": reason, **config}
            (teachers if config["type"] == "teacher" else surrogates).append(row)
        return {"teachers": teachers, "surrogates": surrogates}

    def get_active_model_config(self) -> dict[str, Any]:
        teacher_id = self._active_config["teacher_model_id"]
        surrogate_id = self._active_config["surrogate_model_id"]
        teacher = MODEL_REGISTRY[teacher_id]
        surrogate = MODEL_REGISTRY[surrogate_id]
        return {
            "teacher_model_id": teacher_id,
            "teacher_model_name": teacher["display_name"],
            "surrogate_model_id": surrogate_id,
            "surrogate_model_name": surrogate["display_name"],
            "expected_features": int(teacher.get("expected_features", N_TOTAL)),
            "status": "Matched",
        }

    def set_active_model_config(self, teacher_model_id: str, surrogate_model_id: str) -> dict[str, Any]:
        self._validate_pairing(teacher_model_id, surrogate_model_id)
        self._load_pickle(teacher_model_id)
        self._load_pickle(surrogate_model_id)
        self._active_config = {
            "teacher_model_id": teacher_model_id,
            "surrogate_model_id": surrogate_model_id,
        }
        self._write_active_config(self._active_config)
        return self.get_active_model_config()

    def get_active_models(self) -> tuple[Any, Any]:
        return (
            self._load_pickle(self._active_config["teacher_model_id"]),
            self._load_pickle(self._active_config["surrogate_model_id"]),
        )

    def _feature_order_matches_surrogate(self, surrogate_model_id: str) -> tuple[bool, str | None]:
        if not PROCESSED_ORDER_PATH.exists():
            return False, "The exact processed feature order artifact is missing."
        try:
            with open(PROCESSED_ORDER_PATH, "r", encoding="utf-8") as handle:
                processed_order = json.load(handle)
            surrogate = self._load_pickle(surrogate_model_id)
            embedded_order = [str(name) for name in getattr(surrogate, "feature_names_in_", [])]
        except (OSError, ValueError, TypeError, ModelManagerError) as exc:
            return False, f"Processed feature order could not be validated: {exc}"
        if not embedded_order:
            return False, "The active surrogate does not expose its processed feature order."
        if embedded_order != processed_order:
            return False, "The processed feature order does not match the active surrogate artifact."
        return True, None

    def get_readiness(self, raw_features: dict[str, Any] | None = None) -> dict[str, Any]:
        teacher_id = self._active_config["teacher_model_id"]
        surrogate_id = self._active_config["surrogate_model_id"]
        teacher_loaded, teacher_reason = self._model_runtime_status(teacher_id)
        surrogate_loaded, surrogate_reason = self._model_runtime_status(surrogate_id)
        preprocessing = get_preprocessing_readiness(raw_features)
        preprocessor_order_match = preprocessing["feature_order_match"]
        feature_order_match, feature_order_reason = self._feature_order_matches_surrogate(surrogate_id)
        safe = (
            teacher_loaded
            and surrogate_loaded
            and feature_order_match
            and preprocessing["safe_for_live_prediction"]
        )
        return {
            "teacher_model_loaded": teacher_loaded,
            "surrogate_model_loaded": surrogate_loaded,
            "default_teacher": DEFAULT_ACTIVE_CONFIG["teacher_model_id"],
            "default_surrogate": DEFAULT_ACTIVE_CONFIG["surrogate_model_id"],
            "active_teacher": teacher_id,
            "active_surrogate": surrogate_id,
            **preprocessing,
            "preprocessor_feature_order_match": preprocessor_order_match,
            "feature_order_match": feature_order_match,
            "feature_order_source": (
                "fitted_surrogate_feature_names_in_" if feature_order_match else None
            ),
            "explanation_available": surrogate_loaded,
            "safe_for_live_prediction": safe,
            "warnings": [
                warning
                for warning in [
                    teacher_reason,
                    surrogate_reason,
                    None if preprocessing["preprocessor_loaded"] else "The fitted training preprocessor artifact is missing.",
                    feature_order_reason,
                ]
                if warning
            ],
            "recommended_action_if_unsafe": (
                None
                if safe
                else "Keep results in needs-review shadow mode until model artifacts and feature alignment are validated."
            ),
        }

    @staticmethod
    def _readable_reason(feature: str, value: Any, contribution: float) -> str:
        reason = HUMAN_REASONS.get(feature, f"The feature '{feature}' had value {value}.")
        direction = "toward phishing" if contribution > 0 else "away from phishing"
        return f"{reason} This influenced the model {direction}; it does not prove malicious intent."

    def explain_with_active_surrogate(self, vector: Any, raw_features: dict[str, Any]) -> dict[str, Any]:
        _, surrogate = self.get_active_models()
        if not hasattr(surrogate, "explain_local"):
            return {"top_reasons": [], "raw_feature_contributions": [], "model_failed": True}
        try:
            data = surrogate.explain_local(vector).data(0)
            contributions: list[dict[str, Any]] = []
            for name, score in zip(data.get("names", []), data.get("scores", [])):
                if not str(name).startswith("num__"):
                    continue
                feature = str(name).replace("num__", "")
                value = raw_features.get(feature, 0)
                score_float = float(score)
                contributions.append(
                    {
                        "feature": feature,
                        "value": value,
                        "contribution": round(score_float, 4),
                        "direction": "increases_phishing_risk" if score_float > 0 else "decreases_phishing_risk",
                        "human_reason": self._readable_reason(feature, value, score_float),
                    }
                )
            contributions.sort(key=lambda row: abs(row["contribution"]), reverse=True)
            top = contributions[:8]
            return {
                "top_reasons": [row["human_reason"] for row in top[:3]],
                "raw_feature_contributions": top,
                "uncertainty_notice": "These factors influenced the model; they do not prove the email is malicious. Analyst review is recommended.",
            }
        except Exception:
            return {"top_reasons": [], "raw_feature_contributions": [], "model_failed": True}

    def _unsafe_result(self, readiness: dict[str, Any]) -> dict[str, Any]:
        teacher_id = self._active_config["teacher_model_id"]
        surrogate_id = self._active_config["surrogate_model_id"]
        summary = (
            "The email requires review because the live model pipeline cannot be validated against its training "
            "preprocessor and exact feature order. No trusted automatic classification was made."
        )
        explanation = {
            "top_reasons": [summary],
            "raw_feature_contributions": [],
            "missing_features": readiness.get("missing_features", []),
            "pipeline_warning": readiness["recommended_action_if_unsafe"],
            "uncertainty_notice": "This is a pipeline safety warning, not evidence that the email is malicious.",
        }
        return {
            "prediction": "needs_review",
            "confidence": 0.0,
            "phishing_probability": None,
            "risk_level": "unknown",
            "recommended_action": "review",
            "model_name": MODEL_REGISTRY[teacher_id]["display_name"],
            "model_version": teacher_id,
            "teacher_model_id": teacher_id,
            "surrogate_model_id": surrogate_id,
            "surrogate_model_name": MODEL_REGISTRY[surrogate_id]["display_name"],
            "feature_extractor_version": f"v1_{N_TOTAL}f_unvalidated",
            "explanation_version": surrogate_id,
            "trusted_prediction": False,
            "pipeline_status": "unsafe_incomplete_features",
            "readiness": readiness,
            "explanation": explanation,
            "explanation_snapshot": explanation,
        }

    def predict_email(self, email: dict[str, Any]) -> dict[str, Any]:
        teacher_id = self._active_config["teacher_model_id"]
        surrogate_id = self._active_config["surrogate_model_id"]
        raw_features = extract_raw_features(email)
        readiness = self.get_readiness(raw_features)
        if not readiness["safe_for_live_prediction"]:
            return self._unsafe_result(readiness)

        try:
            vector = build_feature_vector(raw_features)
        except UnsafePreprocessingError as exc:
            readiness["warnings"].append(str(exc))
            readiness["safe_for_live_prediction"] = False
            return self._unsafe_result(readiness)
        teacher_model, _ = self.get_active_models()
        if hasattr(teacher_model, "n_jobs"):
            teacher_model.n_jobs = 1
        probability = float(teacher_model.predict_proba(vector)[0][1])
        prediction = "phishing" if probability >= 0.5 else "legitimate"
        confidence = probability if prediction == "phishing" else 1 - probability
        if prediction == "legitimate":
            risk_level, action = "low", "allow"
        elif probability >= 0.9:
            risk_level, action = "critical", "quarantine"
        elif probability >= 0.75:
            risk_level, action = "high", "quarantine"
        elif probability >= 0.55:
            risk_level, action = "medium", "review"
        else:
            risk_level, action = "low", "allow"
        explanation = self.explain_with_active_surrogate(vector, raw_features)
        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "phishing_probability": round(probability, 4),
            "risk_level": risk_level,
            "recommended_action": action,
            "model_name": MODEL_REGISTRY[teacher_id]["display_name"],
            "model_version": teacher_id,
            "teacher_model_id": teacher_id,
            "surrogate_model_id": surrogate_id,
            "surrogate_model_name": MODEL_REGISTRY[surrogate_id]["display_name"],
            "feature_extractor_version": f"v1_{N_TOTAL}f_validated",
            "explanation_version": surrogate_id,
            "trusted_prediction": True,
            "pipeline_status": "validated",
            "readiness": readiness,
            "explanation": explanation,
            "explanation_snapshot": explanation,
        }

    def get_global_explanation(self) -> dict[str, Any]:
        teacher_id = self._active_config["teacher_model_id"]
        surrogate_id = self._active_config["surrogate_model_id"]
        top_features: list[dict[str, Any]] = []
        try:
            surrogate = self._load_pickle(surrogate_id)
            if hasattr(surrogate, "term_importances") and hasattr(surrogate, "term_names_"):
                for name, importance in zip(surrogate.term_names_, surrogate.term_importances()):
                    feature = str(name).replace("num__", "")
                    if str(name).startswith("num__"):
                        top_features.append(
                            {
                                "feature": feature,
                                "importance": round(float(importance), 4),
                                "human_summary": HUMAN_REASONS.get(
                                    feature, f"The feature '{feature}' influenced the benchmark surrogate."
                                ),
                            }
                        )
                top_features.sort(key=lambda row: row["importance"], reverse=True)
        except ModelManagerError:
            pass
        return {
            "model_name": MODEL_REGISTRY[teacher_id]["display_name"],
            "model_version": teacher_id,
            "surrogate_name": MODEL_REGISTRY[surrogate_id]["display_name"],
            "surrogate_version": surrogate_id,
            "metric_source": "research_benchmark",
            "benchmark_notice": "Fidelity values below are research benchmark metrics, not live Gmail performance.",
            "accuracy_fidelity": 0.926,
            "f1_fidelity": 0.928,
            "error_fidelity": 0.7673,
            "top_features": top_features[:15],
            "generated_at": datetime.now(UTC).isoformat(),
        }


model_manager = ModelManager()
