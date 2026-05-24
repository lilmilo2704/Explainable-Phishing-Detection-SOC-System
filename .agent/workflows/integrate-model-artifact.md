# Workflow: Integrate Model Artifact

Use this workflow when loading a new teacher model, surrogate model, or preprocessing artifact into the ML service.

## Step 1: Artifact Placement
- Place the `.pkl` or `.joblib` file in the correct subfolder under `models/`.
- Update `feature_columns.json` if the expected feature order has changed.

## Step 2: Write Loader Function
- Create or update the loading logic in `services/ml-service/inference/` or `services/ml-service/explainability/`.
- Ensure it handles missing files gracefully (e.g., logging an error instead of crashing the whole app).

## Step 3: Align Preprocessing
- Ensure `services/ml-service/feature-engineering/` perfectly matches the transformations used during model training.

## Step 4: Update Wrapper
- Update the prediction wrapper to include `model_version` in the output.

## Step 5: Test
- Run integration tests locally with a sample email to verify the output shape and confidence scores.
- Check that explanation snapshots are correctly generated.