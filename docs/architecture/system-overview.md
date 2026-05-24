# System Overview

## Purpose

This document explains the system architecture for the explainable phishing detection dashboard.

The product turns an existing research pipeline into an operational SOC-style dashboard. The research foundation includes phishing detection teacher models, global surrogate explanation models, local explanation methods, and fidelity/error-fidelity evaluation. The software product wraps these resources into a mailbox scanning, quarantine, explanation, feedback, and monitoring workflow.

---

## Product Identity

The system is:

> A SOC-friendly explainable phishing detection and model-governance dashboard implemented as a live Gmail prototype.

The product should not be treated as only a phishing classifier. Its main value is:

```text
phishing detection
+ local explanation
+ global model behaviour explanation
+ quarantine workflow
+ analyst feedback review
+ model governance
```

---

## High-Level Architecture

```text
Gmail Mailbox / Mock Test Mailbox
        ↓
Mailbox Service
        ↓
Backend API
        ↓
Model Integration & Explainability Service
        ↓
Prediction + Explanation Result
        ↓
Backend API
        ↓
Frontend SOC Dashboard
        ↓
Analyst Review / Feedback / Quarantine Actions
```

More detailed view:

```text
Mailbox / Email Source
        ↓
Email Ingestion
        ↓
Feature Extraction
        ↓
Phishing Detection Model
        ↓
Decision Engine
  ┌───────────────┬────────────────┐
  ↓               ↓                ↓
Allow Email   Warn User       Quarantine Email
        ↓
Explanation Service
  ┌───────────────────────────┬───────────────────────────┐
  ↓                           ↓
Local Explanation             Global Explanation
for one email                 for model behaviour
        ↓
SOC Analyst Dashboard
        ↓
Feedback Review
        ↓
Future model improvement
```

---

## Main System Modules

### 1. Frontend Dashboard

Location:

```text
apps/frontend/
```

Purpose:

- provide the SOC analyst dashboard UI
- display email detections
- show local and global explanations
- allow analyst actions
- display feedback review workflow
- display model monitoring metrics

The frontend must not load model files directly. It must communicate with backend APIs.

---

### 2. Backend API

Location:

```text
apps/backend/
```

Purpose:

- expose REST API endpoints
- serve dashboard data
- coordinate mailbox, model, explanation, feedback, and quarantine services
- validate request and response schemas
- store and retrieve records when persistence is added

The backend should keep route files thin and place business logic in services.

---

### 3. Model Integration & Explainability Service

Location:

```text
services/ml-service/
```

Purpose:

- load existing phishing detection model artifacts
- load existing global surrogate explanation artifacts
- run prediction
- prepare local explanation output
- prepare global explanation output
- convert explanation results into dashboard-ready JSON
- convert technical explanation outputs into human-readable SOC language

This service is not responsible for training new models during the MVP.

---

### 4. Mailbox Service

Location:

```text
services/mailbox-service/
```

Purpose:

- read emails from Gmail through manually initiated sync
- retain a mock mailbox adapter for deterministic tests
- apply reversible Gmail quarantine/release label actions
- provide normalized email objects to the backend

Development order:

```text
mock mailbox
→ Gmail prototype
→ other mailbox providers (future, outside this Gmail prototype)
```

---

### 5. Models and Artifacts

Location:

```text
models/
```

Suggested structure:

```text
models/
├── teacher-models/
├── surrogate-models/
├── preprocessors/
└── explanation-artifacts/
```

Purpose:

- store trained Random Forest and DNN teacher models
- store EBM and GAMI-Net surrogate models
- store preprocessors such as scalers, encoders, and feature columns
- store local/global explanation artifacts and plots

---

### 6. Database

Location:

```text
database/
```

Purpose:

- define schema
- store emails, predictions, explanations, feedback, quarantine actions, and model versions
- support auditability and model governance

For MVP, SQLite or mock JSON can be used first. PostgreSQL can be used later.

---

### 7. Tests

Location:

```text
tests/
```

Purpose:

- verify API behaviour
- verify model output shape
- verify explanation output shape
- verify feedback workflow
- verify quarantine workflow
- verify dashboard flow

---

## Recommended Runtime Architecture for MVP

For the first MVP, keep the architecture simple:

```text
React frontend
        ↓
FastAPI backend
        ↓
Mock data + mock mailbox + sample explanation outputs
```

Then add model integration:

```text
React frontend
        ↓
FastAPI backend
        ↓
ML-service functions
        ↓
Existing .pkl model artifacts
```

Current live mailbox prototype:

```text
React frontend
        ↓
FastAPI backend
        ↓
Mailbox service
        ↓
Gmail API (manual sync only)
```

---

## System Responsibilities

| Layer | Responsibility |
|---|---|
| Frontend | UI, pages, charts, tables, analyst actions |
| Backend | API, business workflow, validation, persistence coordination |
| ML Service | feature extraction, prediction, explanations, model artifact loading |
| Mailbox Service | email ingestion, quarantine/release with mailbox provider |
| Database | long-term records and audit history |
| Models | saved trained models and explanation artifacts |
| Docs | product and technical guidance |
| Tests | validation of core flows |

---

## Important Design Constraints

### No Permanent Deletion

The system must not permanently delete emails. Suspicious emails should be moved to a review/quarantine state.

### No automatic model updating

User feedback must not automatically retrain the model. Feedback must be analyst-confirmed first.

### Explanation Snapshot Required

Every prediction should store:

- model version
- explanation snapshot
- explanation method
- explanation timestamp

### Feature Compatibility

The trained model expects processed feature vectors, not raw emails. The system must reproduce the same feature extraction and preprocessing used during training.

### Gmail Prototype Stage

The mock mailbox and offline workflow remain available for testing. The current product stage adds manual Gmail sync, reversible review-label quarantine, audit logging, and fail-safe review states.

---

## MVP Scope

The first MVP should include:

- Gmail manual sync with mock test fixtures
- mock predictions
- mock local explanations
- mock global explanations
- Overview page
- Detection Queue page
- Email Investigation page
- Global Explanation page
- Feedback Review page
- reversible Gmail quarantine/release workflow

The MVP should not include:

- background mailbox synchronisation
- automatic model updating
- production deployment
- full enterprise authentication
