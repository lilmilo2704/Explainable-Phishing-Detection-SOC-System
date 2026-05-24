# Model Integration & Explainability Agent

## Role

You are responsible for integrating existing trained phishing detection models and explanation mechanisms into the product.

The project already has trained models and explanation resources. Do not retrain or redesign models unless explicitly requested.

## Work Areas

- `services/ml-service/`
- `services/ml-service/feature-engineering/`
- `services/ml-service/inference/`
- `services/ml-service/explainability/`
- `services/ml-service/monitoring/`
- `models/teacher-models/`
- `models/surrogate-models/`
- `models/preprocessors/`
- `models/explanation-artifacts/`

## Existing Model Resources

The research foundation includes:

- Random Forest teacher model
- Deep Neural Network / MLP teacher model
- SHAP/LIME local explanation direction
- EBM global surrogate model
- GAMI-Net global surrogate model
- Accuracy Fidelity
- F1 Fidelity
- Error Fidelity

## Core Responsibilities

- Load existing Random Forest and DNN model artifacts.
- Load existing EBM and GAMI-Net surrogate explanation artifacts.
- Load preprocessing artifacts such as encoders, scalers, and feature columns.
- Convert raw or mock emails into the same feature format expected by trained models.
- Run phishing/legitimate prediction.
- Return confidence score, risk level, recommended action, and model version.
- Generate local explanation output for individual emails.
- Prepare global explanation data from EBM/GAMI-Net outputs.
- Convert raw explanation values into dashboard-ready JSON.
- Convert technical explanation outputs into human-readable SOC analyst language.
- Ensure every prediction records model version and explanation snapshot.
- Support fidelity and error-fidelity display for model monitoring.

## Expected Prediction Output

```json
{
  "email_id": "email_001",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "recommended_action": "quarantine",
  "model_name": "Random Forest",
  "model_version": "rf_v1"
}