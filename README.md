# Explainable Phishing Detection SOC Dashboard

A SOC-friendly phishing detection and model-governance dashboard that combines machine learning, explainable AI, quarantine workflows, and analyst feedback into a practical security operations prototype.

This project extends research on **global explainability** and **explanation latency reduction** in phishing email detection into an operational dashboard designed for SOC analysts, security managers, and model owners.

---

## Project Overview

Modern phishing detection models can achieve strong predictive performance, but they are often difficult for analysts to trust because their decisions are not transparent. This project addresses that gap by combining phishing classification with both **local explanations** for individual emails and **global explanations** for overall model behaviour.

The system demonstrates how a security team could:

- Scan mailbox emails for phishing risk
- Review suspicious emails through a SOC-style detection queue
- Inspect model predictions and explanation evidence
- Quarantine or release emails
- Track analyst-confirmed feedback
- Monitor model and surrogate explanation behaviour
- Export validated feedback for future model improvement

The goal is not only to detect phishing emails, but to make the detection process understandable, reviewable, and suitable for security operations workflows.

---

## Key Features

### SOC Workflow

- Detection queue for suspicious and reviewed emails
- Email investigation view for individual case analysis
- Quarantine and release workflow
- Feedback review process for false positives and false negatives
- Analyst-oriented interface for triage and decision-making

### Machine Learning Detection

- Random Forest teacher model
- Deep Neural Network / MLP teacher model
- Risk scoring and prediction output
- Model-pair selection between teacher and surrogate models
- Compatibility checks to reduce unsafe model/surrogate pairing

### Explainable AI

- Local explanation panel for individual email decisions
- Global explanation dashboard for model-level behaviour
- EBM and GAMI-Net surrogate models
- Fidelity metrics for evaluating teacher-surrogate agreement
- Error Fidelity support for analysing teacher-model failure behaviour

### Governance and Feedback

- Analyst-confirmed feedback storage
- False-positive and false-negative review flow
- Confirmed feedback export for offline retraining
- Model version and explanation snapshot tracking
- Safer human-in-the-loop improvement process

---

## Technology Stack

### Backend

- FastAPI
- Python
- SQLite
- scikit-learn
- EBM / InterpretML-compatible explanation workflow
- GAMI-Net surrogate explanation workflow

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- SOC-style dashboard pages for triage, investigation, monitoring, and governance

### Persistence

SQLite is currently used for local prototype persistence, including:

- Email records
- Prediction records
- Explanation records
- Quarantine state
- Analyst feedback
- Model configuration metadata

---

## System Architecture

```text
Mailbox / Mock Email Source
        ↓
Email Ingestion / Sync Flow
        ↓
Feature Extraction
        ↓
Teacher Model Prediction
        ↓
Decision Engine
        ↓
Explanation Service
   ┌───────────────┬────────────────┐
   ↓               ↓                ↓
Local Explanation  Global Explanation Feedback Governance
        ↓
SOC Analyst Dashboard
        ↓
Quarantine / Release / Confirm Feedback
