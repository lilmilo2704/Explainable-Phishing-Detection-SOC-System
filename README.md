# ??? Explainable Phishing Detection SOC System

## Project Overview
This project demonstrates a **SOC-friendly phishing detection and model-governance dashboard** built with a practical security operations workflow in mind, inspired by my research about enhancing global explainability and reducing explanation latency in phishing email detection.

The platform combines:

- **FastAPI backend** for scanning, case workflows, and model APIs
- **React frontend** for SOC triage and investigation
- **Random Forest / DNN teacher models** for phishing classification
- **EBM / GAMI-Net surrogate models** for explainability
- **SQLite persistence** for email, prediction, explanation, and feedback records

The environment is designed to simulate real SOC analyst operations:

- detection queue triage
- quarantine/release decisions
- local explanation review per email
- global model behavior monitoring
- analyst-confirmed feedback governance

## ?? Full Project Documentation
The complete project documentation, including architecture, workflows, MVP scope, and API contracts, is available in this repository:

- `PROJECT_CONTEXT.md`
- `OUTCOME_REQUIREMENTS.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/architecture/system-overview.md`
- `docs/api/api-contracts.md`
- `docs/dashboard/dashboard-pages.md`
- `docs/dashboard/wireframe-notes.md`
- `docs/product/mvp-scope.md`

## ?? Key Focus Areas

- SOC-oriented phishing detection workflow design
- Local and global explainability integration
- Detection-to-quarantine-to-review operations
- Human-in-the-loop feedback governance
- Model pairing/version safety checks (teacher + surrogate)
- Practical productization of research ML/XAI artifacts

## ? Currently Usable Features

- Backend API server with core SOC workflow endpoints
- Dashboard pages for queue, investigation, quarantine, feedback, monitoring, settings
- Local explanation panel integrated into email investigation
- Model pair selection with compatibility checks
- Feedback review and confirmed feedback export
- Quarantine/release actions from UI and API

## ?? Not Fully Working Yet / Placeholder Areas

- Monitoring performance/fidelity metrics are currently placeholder values
- Global explanation fidelity outputs include fallback/static behavior
- Mock mailbox flow has visibility inconsistency with current `/emails` filtering logic
- Gmail integration is scaffolded but requires external credential setup
- Microsoft 365 / Graph integration is not implemented yet
- Production auth/RBAC/audit hardening is not implemented yet

## ?? Quick Start

### Backend
```powershell
cd apps/backend
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend
```powershell
cd apps/frontend
npm install
npm run dev
```

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## ?? How to Use (Demo Flow)

1. Open the dashboard.
2. Click `Sync Mailbox`.
3. Review cases in `Detection Queue`.
4. Open a case in `Email Investigation`.
5. Check prediction, risk, and local explanation.
6. Take analyst action: confirm phishing, quarantine, mark false positive, or release.
7. Review and confirm feedback in `Feedback Review`.
8. Export confirmed feedback for future offline model improvement.
9. Check `Global Explanation` and `Model Monitoring` pages.

## ?? Notes
This repository is intended to showcase hands-on SOC product engineering and explainable AI integration through a practical prototype.

The docs listed above are the authoritative source for detailed requirements and architecture.