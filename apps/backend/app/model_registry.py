from __future__ import annotations

from typing import Any


MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "random_forest_v1": {
        "display_name": "Random Forest v1",
        "description": "Recommended default phishing detector. Stronger benchmark performance.",
        "type": "teacher",
        "path": "models/teacher-models/random_forest.pkl",
        "default": True,
        "expected_features": 292,
        "valid_surrogates": ["ebm_random_forest_v1", "gaminet_random_forest_v1"],
    },
    "deep_neural_net_v1": {
        "display_name": "Deep Neural Network v1",
        "description": "Alternative research detector for comparison.",
        "type": "teacher",
        "path": "models/teacher-models/deep_neural_net.pkl",
        "default": False,
        "expected_features": 292,
        "valid_surrogates": ["ebm_deep_neural_net_v1", "gaminet_deep_neural_net_v1"],
    },
    "ebm_random_forest_v1": {
        "display_name": "EBM for Random Forest v1",
        "description": "Recommended explanation model. Fast and interpretable global surrogate.",
        "type": "surrogate",
        "path": "models/surrogate-models/ebm_random_forest.pkl",
        "teacher": "random_forest_v1",
        "recommended": True,
    },
    "gaminet_random_forest_v1": {
        "display_name": "GAMI-Net for Random Forest v1",
        "description": "Alternative explanation model with smoother neural additive explanations.",
        "type": "surrogate",
        "path": "models/surrogate-models/gaminet_random_forest.pickle",
        "teacher": "random_forest_v1",
        "recommended": False,
    },
    "ebm_deep_neural_net_v1": {
        "display_name": "EBM for Deep Neural Network v1",
        "description": "Recommended explanation model. Fast and interpretable global surrogate.",
        "type": "surrogate",
        "path": "models/surrogate-models/ebm_deep_neural_net.pkl",
        "teacher": "deep_neural_net_v1",
        "recommended": True,
    },
    "gaminet_deep_neural_net_v1": {
        "display_name": "GAMI-Net for Deep Neural Network v1",
        "description": "Alternative explanation model with smoother neural additive explanations.",
        "type": "surrogate",
        "path": "models/surrogate-models/gaminet_deep_neural_net.pickle",
        "teacher": "deep_neural_net_v1",
        "recommended": False,
    },
    # Research-only baselines are intentionally excluded from selectable deployment models.
}


DEFAULT_ACTIVE_CONFIG = {
    "teacher_model_id": "random_forest_v1",
    "surrogate_model_id": "ebm_random_forest_v1",
}

