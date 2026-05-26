from fastapi.testclient import TestClient
from types import SimpleNamespace

from app.main import app
from app.api import endpoints
from app.database import SessionLocal
from app.services import data_service
import app.services.model_manager as model_manager_module


client = TestClient(app)


class _PhishingTeacher:
    def predict_proba(self, vector):
        return [[0.01, 0.99]]


class _UnsupportedExplanation:
    def data(self, index):
        return {"names": ["categorical_feature"], "scores": [0.4]}


class _EmptyUsableContributionSurrogate:
    def explain_local(self, vector):
        return _UnsupportedExplanation()


def test_scan_email_requires_review_when_local_explanation_generation_fails(monkeypatch):
    manager = model_manager_module.model_manager
    monkeypatch.setattr(
        model_manager_module,
        "extract_raw_features",
        lambda email: {"subject_urgent_word_count": 2},
    )
    monkeypatch.setattr(model_manager_module, "build_feature_vector", lambda raw_features: object())
    monkeypatch.setattr(
        manager,
        "get_readiness",
        lambda raw_features=None: {
            "safe_for_live_prediction": True,
            "explanation_available": True,
            "warnings": [],
        },
    )
    monkeypatch.setattr(manager, "get_active_models", lambda: (_PhishingTeacher(), object()))
    monkeypatch.setattr(
        manager,
        "explain_with_active_surrogate",
        lambda vector, raw_features: {
            "top_reasons": [],
            "raw_feature_contributions": [],
            "model_failed": True,
        },
    )

    response = client.post("/scan-email", json={"subject": "Urgent verification required"})
    assert response.status_code == 200
    result = response.json()

    assert result["prediction"] == "needs_review"
    assert result["recommended_action"] == "review"
    assert result["risk_level"] == "unknown"
    assert result["trusted_prediction"] is False
    assert result["pipeline_status"] == "explanation_unavailable_review_required"
    assert result["readiness"]["explanation_available"] is False
    assert result["readiness"]["safe_for_live_prediction"] is False
    assert result["explanation"] == result["explanation_snapshot"]
    assert result["explanation_snapshot"]["model_failed"] is True
    assert result["explanation_snapshot"]["failure_stage"] == "local_explanation_generation"
    assert "not evidence" in result["explanation_snapshot"]["uncertainty_notice"].lower()


def test_global_explanation_reports_uncomputed_operational_failure_patterns_with_provenance():
    response = client.get("/global-explanation")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metric_source"] == "research_benchmark"
    assert "live mailbox performance" in payload["benchmark_notice"]
    assert "gmail" not in payload["benchmark_notice"].lower()

    failure_patterns = payload["failure_patterns"]
    assert failure_patterns["source"] == "analyst_confirmed_operational_feedback"
    assert failure_patterns["status"] == "not_computed"
    assert failure_patterns["derived_from_analyst_confirmed_feedback"] is False
    assert failure_patterns["false_positives"] == []
    assert failure_patterns["false_negatives"] == []
    assert "not been computed" in failure_patterns["message"]


def test_dynamic_local_explanation_exposes_unavailable_state_for_dashboard(monkeypatch):
    email = SimpleNamespace(
        subject="Review",
        body="",
        body_preview="Review manually",
        sender="sender@example.com",
        reply_to=None,
        urls=[],
        attachments=[],
        url_count=0,
        has_links=False,
        has_attachment=False,
        attachment_count=0,
    )
    monkeypatch.setattr(endpoints.data_service, "get_local_explanation_by_email_id", lambda db, email_id: None)
    monkeypatch.setattr(endpoints.data_service, "get_email_by_id", lambda db, email_id: email)
    monkeypatch.setattr(
        endpoints.model_manager,
        "predict_email",
        lambda payload: {
            "surrogate_model_name": "EBM surrogate",
            "explanation_version": "ebm_v1",
            "pipeline_status": "explanation_unavailable_review_required",
            "explanation": {
                "top_reasons": ["Review required because explanation generation failed."],
                "raw_feature_contributions": [],
                "model_failed": True,
                "uncertainty_notice": "No proof of phishing.",
            },
        },
    )

    response = client.get("/emails/dynamic_local_failure/local-explanation")
    assert response.status_code == 200
    payload = response.json()
    assert payload["model_failed"] is True
    assert payload["pipeline_status"] == "explanation_unavailable_review_required"


def test_monitoring_fidelity_notice_is_provider_neutral():
    response = client.get("/monitoring/fidelity")
    assert response.status_code == 200
    assert "live mailbox performance" in response.json()["notice"]
    assert "gmail" not in response.json()["notice"].lower()


def test_surrogate_output_without_usable_contributions_is_treated_as_failure(monkeypatch):
    manager = model_manager_module.model_manager
    monkeypatch.setattr(manager, "get_active_models", lambda: (_PhishingTeacher(), _EmptyUsableContributionSurrogate()))

    explanation = manager.explain_with_active_surrogate(object(), {})
    assert explanation["model_failed"] is True
    assert explanation["raw_feature_contributions"] == []


def test_persisted_explanation_failure_exposes_failure_provenance(monkeypatch):
    email_id = "explanation_failure_case"
    with SessionLocal() as db:
        data_service.upsert_email_from_mailbox(
            db,
            {
                "id": email_id,
                "mailbox_source": "mock",
                "mailbox_message_id": email_id,
                "subject": "Review explanation failure",
                "sender": "test@example.com",
                "body_preview": "Review required.",
            },
        )
    failure = {
        "prediction": "needs_review",
        "confidence": 0.0,
        "risk_level": "unknown",
        "recommended_action": "review",
        "model_name": "Random Forest v1",
        "model_version": "random_forest_v1",
        "teacher_model_id": "random_forest_v1",
        "surrogate_model_id": "ebm_random_forest_v1",
        "surrogate_model_name": "EBM surrogate",
        "explanation_version": "ebm_random_forest_v1",
        "feature_extractor_version": "test",
        "trusted_prediction": False,
        "pipeline_status": "explanation_unavailable_review_required",
        "explanation": {
            "top_reasons": ["Explanation unavailable; review required."],
            "raw_feature_contributions": [],
            "model_failed": True,
        },
        "explanation_snapshot": {"model_failed": True},
    }
    monkeypatch.setattr(endpoints.model_manager, "predict_email", lambda payload: failure)

    assert client.post("/scan-email", json={"email_id": email_id}).status_code == 200
    response = client.get(f"/emails/{email_id}/local-explanation")
    assert response.status_code == 200
    payload = response.json()
    assert payload["model_failed"] is True
    assert payload["failure_stage"] == "local_explanation_generation"
    assert "not evidence" in payload["uncertainty_notice"].lower()
