# Dashboard Inspiration Images

This folder stores visual reference images for the phishing detection dashboard.

These images are used only as inspiration for layout, workflow, density, and visual style.

---

## Image Location

Place all dashboard inspiration images in this folder:

```text
docs/dashboard/inspiration/
```

Recommended image names:

- `overview-reference.png`
- `detection-queue-reference.png`
- `security-analytics-reference.png`

## How to Use These Images

Coding agents should use the images to understand:

- dark SOC-style dashboard layout
- security metrics overview
- insight/detection queue design
- recent activity panels
- entity/activity tables
- severity and risk indicators
- investigation-style page structure
- data-dense security monitoring UI

## What to Copy Conceptually

Use the images for inspiration around:

- left navigation or dashboard navigation structure
- metric cards
- queue/list layout
- dark enterprise security style
- recent activity feed
- table-heavy investigation pages
- risk/severity badges
- chart placement
- compact operational layout
- security analyst workflow

## What Not to Copy

Do not copy:

- logos
- branding
- exact colours
- exact labels
- exact icons
- copyrighted UI assets
- vendor-specific names
- exact screen layout pixel-for-pixel

These images are visual references only.

## Product-Specific Adaptation

The reference dashboards are general SOC/security dashboards.

This product must adapt them for phishing detection:

| Reference Dashboard Concept | Product-Specific Adaptation |
|---|---|
| Security insights | Phishing email detections |
| Entities | Sender domains, email senders, URL domains |
| Signals | Suspicious email indicators |
| Severity | Phishing risk level |
| Insight detail | Email investigation detail |
| Recent activity | Detection/quarantine/feedback activity |
| Status | New, In Review, Confirmed, Released |
| Alerts | Suspicious email cases |
| Audit/activity tables | Model monitoring and feedback history |

## Dashboard Design Direction

The target design direction is:

**Dark SOC-style dashboard with professional enterprise security feel.**

The dashboard should feel similar in seriousness to:

- Microsoft Defender
- Microsoft Sentinel
- Sumo Logic dashboards
- enterprise SOC dashboards
- modern cybersecurity SaaS dashboards

The dashboard should not feel like:

- a fake hacker terminal
- a gaming dashboard
- a decorative cyber poster
- a generic sales analytics dashboard

## Required Dashboard Pages

The final product should include:

- Overview
- Detection Queue
- Quarantine
- Email Investigation
- Local Explanation
- Global Explanation
- Feedback Review
- Model Monitoring
- Settings

## Key Visual Patterns to Reuse

### Overview Page
Use reference images for:
- top metric cards
- recent activity panel
- system status summary
- risk distribution
- chart-heavy layout

### Detection Queue Page
Use reference images for:
- wide alert cards
- left-side severity strip
- filter bar
- dense case list
- tags
- confidence/risk indicators

### Investigation Pages
Use reference images for:
- detailed panels
- table-heavy evidence sections
- right-side activity/action panel
- security event style

### Global Explanation Page
Use reference images for:
- analytics dashboard layout
- chart panels
- metric cards
- model behaviour summary sections

## Notes for Coding Agents

Before implementing dashboard UI, read:
- `docs/dashboard/dashboard-pages.md`
- `docs/dashboard/wireframe-notes.md`
- `PROJECT_CONTEXT.md`
- `OUTCOME_REQUIREMENTS.md`
- `AGENTS.md`

Use the images to guide layout and visual hierarchy, but follow the product requirements for actual content and functionality.

The dashboard must remain focused on:
- phishing detection
- local explanation
- global explanation
- quarantine/release
- feedback review
- model monitoring
