from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_models_registry_and_active_config_endpoints():
    reg = client.get("/api/models")
    assert reg.status_code == 200
    body = reg.json()
    teacher_ids = {t["id"] for t in body["teachers"]}
    surrogate_ids = {s["id"] for s in body["surrogates"]}
    assert "random_forest_v1" in teacher_ids
    assert "deep_neural_net_v1" in teacher_ids
    assert "ebm_random_forest_v1" in surrogate_ids

    active = client.get("/api/models/active")
    assert active.status_code == 200
    active_body = active.json()
    assert "teacher_model_id" in active_body
    assert "surrogate_model_id" in active_body


def test_model_pairing_rejects_invalid_combo():
    res = client.post(
        "/api/models/active",
        json={
            "teacher_model_id": "random_forest_v1",
            "surrogate_model_id": "ebm_deep_neural_net_v1",
        },
    )
    assert res.status_code == 400


def test_model_pairing_accepts_valid_combo():
    res = client.post(
        "/api/models/active",
        json={
            "teacher_model_id": "random_forest_v1",
            "surrogate_model_id": "ebm_random_forest_v1",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["teacher_model_id"] == "random_forest_v1"
    assert body["surrogate_model_id"] == "ebm_random_forest_v1"

