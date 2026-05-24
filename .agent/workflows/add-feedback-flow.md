# Workflow: Add Feedback Flow

Use this workflow when implementing UI or APIs for handling false positives/negatives.

## Step 1: UI Implementation
- Add Analyst Action buttons (e.g., "Confirm Phishing", "Mark False Positive") in the Email Investigation page.

## Step 2: API Implementation
- Ensure the backend stores the feedback in the `feedback` table.
- Verify that `model_version` and `explanation_snapshot` from the original prediction are preserved alongside the feedback.

## Step 3: Prevent Auto-learning
- Check that the feedback simply marks the database record as "reviewed" or "added_to_improvement_dataset".
- Ensure NO code automatically triggers a model retrain cycle.

## Step 4: Update Counters
- Update the model monitoring endpoints to reflect the new counts of confirmed false positives/negatives.
