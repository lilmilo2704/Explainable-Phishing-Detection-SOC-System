# IMPLEMENTATION_PLAN.md

This document outlines the step-by-step plan for building the AI-powered explainable phishing detection dashboard.

## Overview
The goal is to build an explainable phishing detection and model-governance dashboard using the following tech stack:
- **Backend**: Python (FastAPI)
- **Frontend**: JavaScript (React)
- **Database**: SQL (SQLite for local development, PostgreSQL for production)
- **ML/XAI**: Python (scikit-learn, SHAP, LIME, interpretML/EBM, GAMI-Net)

*Note: Use only the technologies listed above (Python, JavaScript, React, SQL). Do not introduce other programming languages or frameworks.*

---

## 1. MVP Roadmap

### Phase 1: Offline Dashboard MVP
**Goal**: Prove the dashboard workflow without mailbox API complexity.
- Create mock email data (JSON/CSV files placed in `database/seed/`).
- Create mock prediction and explanation data.
- Build backend endpoints returning mock data.
- Build the React dashboard layout (Overview, Detection Queue, Email Investigation, Local/Global Explanations, Feedback Review).
- **Rule**: Do not implement Gmail/Outlook integration yet.

### Phase 2: Backend and Database Implementation
**Goal**: Set up the real persistence layer.
- Build the SQL database schema (SQLite).
- Set up tables for: `emails`, `predictions`, `explanations`, `feedback`, `model_versions`.
- Implement API endpoints with actual database reads/writes.
- Refactor the backend into a clean repository/service structure.

### Phase 3: ML/XAI Integration
**Goal**: Integrate the real model artifacts.
- Implement the model artifact loader (Random Forest, DNN).
- Implement the feature extraction pipeline.
- Implement the prediction and risk scoring service.
- Generate local explanations (SHAP/LIME) and global explanations (EBM/GAMI-Net) dynamically.
- Implement human-readable summary generation.

### Phase 4: Feedback Workflow
**Goal**: Support safe human-in-the-loop improvements.
- Build user feedback submission.
- Implement analyst review workflow (tagging false positives/negatives).
- Implement the logic to send confirmed feedback to a improvement datasetset.
- Implement model monitoring counters (tracking fidelity, accuracy, etc.).

### Phase 5: Mailbox Integration
**Goal**: Ingest real emails.
- Finalize the mock mailbox flow.
- Implement a Gmail API prototype.
- Plan for Microsoft Graph / Outlook integration.

### Phase 6: Model Improvement Insights and Governance
**Goal**: Support safe model evolution.
- Analyse confirmed false positives and false negatives.
- Show common failure patterns.
- Suggest future dataset improvements.
- Suggest future feature engineering improvements.
- Export analyst-confirmed feedback cases for future offline retraining.
- Do not train, retrain, or replace models automatically.

---

## 2. Immediate Implementation Order

1. Create project structure.
2. Build backend API skeleton with FastAPI.
3. Create mock/sample email dataset as JSON/CSV in `database/seed/`.
4. Create SQL database schema.
5. Implement mock prediction endpoint first.
6. Add real model loading after mock flow works.
7. Build React dashboard shell.
8. Create Overview page.
9. Create Detection Queue page.
10. Create Email Investigation page.
11. Create Local Explanation panel.
12. Create Global Explanation page using existing plots/metrics or mock metrics.
13. Create Feedback Review page.
14. Create Model Monitoring page.
15. Add quarantine simulation.
16. Add Gmail API integration only after offline prototype works.
17. Add analyst-confirmed feedback storage.
18. Add improvement datasetset export.
19. Add model version comparison later.

---

## 3. Recommended Build Order (Agent Workflow)

1. **Product Architect Agent** → Confirm scope, structure, and implementation phase.
2. **Frontend Dashboard Agent** → Build dashboard UI with mock data.
3. **Backend API Agent** → Create mock API endpoints and backend structure.
4. **Model Integration & Explainability Agent** → Connect existing model/explanation artifacts after dashboard flow exists.
5. **Mailbox Integration Agent** → Build mock mailbox first, then Gmail/Outlook later.
6. **Testing / QA Agent** → Test scan, explanation, feedback, and quarantine flows.
7. **Reviewer Agent** → Review architecture, safety, code quality, and requirement alignment.
