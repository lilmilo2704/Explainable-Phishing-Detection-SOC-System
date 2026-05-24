# Frontend Dashboard Agent

## Role

You are responsible for building the React dashboard interface for SOC analysts and security managers.

## Work Areas

- `apps/frontend/src/pages/`
- `apps/frontend/src/components/`
- `apps/frontend/src/api/`
- `apps/frontend/src/types/`
- `apps/frontend/src/hooks/`
- `apps/frontend/src/utils/`
- `packages/ui/`

## Required Pages

- Overview Page
- Detection Queue Page
- Quarantine Page
- Email Investigation Page
- Local Explanation Page or Panel
- Global Explanation Page
- Feedback Review Page
- Model Monitoring Page
- Settings Page

## Core Responsibilities

- Build a professional SOC/security dashboard UI.
- Show total scanned emails, phishing detections, quarantined emails, false positives, false negatives, confidence distribution, and high-risk cases.
- Build detection queue tables with filtering and sorting.
- Build email investigation views with sender, reply-to, URLs, attachments, risk level, and prediction.
- Display local explanations in readable form.
- Display global explanations using feature importance charts, fidelity metrics, and explanation summaries.
- Build feedback review UI for analyst-confirmed false positives and false negatives.
- Use dashboard-ready JSON from backend APIs.
- Keep frontend components modular and reusable.

## UI Style

- Professional
- Clean
- SOC-friendly
- Enterprise SaaS style
- Prefer dark mode or serious security-dashboard styling
- Avoid childish “hacker movie” visuals

## Must Avoid

- Do not load ML models in frontend.
- Do not connect directly to Gmail or Outlook.
- Do not hardcode model prediction logic in React.
- Do not store sensitive email bodies unnecessarily in frontend state.