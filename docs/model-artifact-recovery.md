# Model Artifact Recovery

Date: 2026-05-25

## Recovery Status

The live Random Forest teacher expects 292 transformed input columns. The fitted EBM surrogate preserves those exact column names and their order in `feature_names_in_`.

Recovered and validated:

- `models/preprocessors/processed_feature_order.json`: extracted from the active fitted EBM surrogate.
- `models/preprocessors/processed_feature_order_provenance.json`: records the recovery method and SHA-256 hashes of the validating model artifacts.
- `models/preprocessors/preprocessor.pkl`: deterministically reconstructed fitted `ColumnTransformer`.
- `models/preprocessors/preprocessor_provenance.json`: records original Git LFS dataset object hashes and full split validation.

The recovered preprocessor reproduces every transformed value and label in the original saved train, validation, and test processed dataset. Model Readiness now reports `safe_for_live_prediction: true` for the default Random Forest and EBM pairing.

## How The Preprocessor Was Recovered

Both repository branches were inspected:

- `main` contains the original teacher training script and Git LFS-tracked raw and processed datasets.
- `explainability-model` contains the dataset-building formulas used for live feature parity checks.

No branch or commit history contains an original committed `preprocessor.pkl`. The preprocessor was therefore deterministically fitted again using the original Git LFS raw training object and preserved training script. It was accepted only after its 292-feature output matched the original Git LFS `processed_dataset_with_split.csv` across all saved splits.

Original Git LFS object IDs used:

```text
business_phishing_dataset.csv     3dada9a6ffad73e62062d9a5304b348a21249af9ad556b20f05576310ae6e20e
processed_dataset_with_split.csv  5e505131a5af560b0099f35c59b82fb2d979e3d600acd3010b37dd994d4ba211
```

## Validation Commands

To validate the recovered artifacts:

```powershell
python -B scripts/recover_processed_feature_order.py --check
python -B scripts/recover_fitted_preprocessor.py --check
```

To reproduce the reconstruction from a fresh Git LFS checkout:

```text
.recovery/original-research/csv/raw/business_phishing_dataset.csv
.recovery/original-research/csv/processed/processed_dataset_with_split.csv
```

Then run:

```powershell
python -B scripts/recover_fitted_preprocessor.py
```
