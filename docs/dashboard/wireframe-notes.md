# Dashboard Wireframe Notes

## Purpose

This document describes the wireframe and layout direction for the explainable phishing detection dashboard.

The dashboard inspiration is based on dark SOC/security analytics dashboards with metric panels, insight queues, recent activity feeds, entity tables, and investigation-focused layouts.

The goal is to build a dashboard that feels like a professional security operations tool for phishing email detection and explanation.

---

## Inspiration Image Placement

Place all dashboard inspiration images in:

```text
docs/dashboard/inspiration/
```

Recommended structure:

```text
docs/dashboard/inspiration/
├── overview-reference.png
├── detection-queue-reference.png
├── security-analytics-reference.png
└── README.md
```

Do not place inspiration images directly inside `docs/dashboard/`.

## Overall Layout Direction

Use a dark enterprise SOC-style layout.

Recommended visual direction:

- dark navy background
- slightly lighter card panels
- subtle borders
- clear metric cards
- compact tables
- risk/severity badges
- right-side activity panels
- chart-heavy overview
- investigation-focused detail pages

The UI should look serious and operational, not decorative.

### Core Layout Pattern

Use this general structure:

```text
┌──────────────────────────────────────────────┐
│ Top Header / Page Title / Time Range         │
├───────────────┬──────────────────────────────┤
│ Left Sidebar  │ Main Dashboard Content        │
│ Navigation    │ Cards, Tables, Charts, Panels │
└───────────────┴──────────────────────────────┘
```

For pages with investigation detail:

```text
┌──────────────────────────────────────────────┐
│ Page Header + Case Status                    │
├────────────────────────────┬─────────────────┤
│ Main Investigation Content │ Right Side Panel │
│ Email + Explanation        │ Actions/Activity │
└────────────────────────────┴─────────────────┘
```

## 1. Overview Page Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Overview | Time Range Selector                       │
├──────────────────────────────────────────────────────────────┤
│ Metric Cards Row                                             │
│ [Emails Scanned] [Phishing] [Quarantined] [Pending Review]   │
├───────────────────────────────┬──────────────────────────────┤
│ Detection Trend Chart          │ Recent Activity Panel        │
│ Risk Distribution              │ Most Active Sender Domains   │
├───────────────────────────────┴──────────────────────────────┤
│ Recent High-Risk Detections Table                            │
└──────────────────────────────────────────────────────────────┘
```

### Design Notes
- Use cards similar to the first reference image.
- Keep metrics compact but readable.
- Use a right-side Recent Activity panel.
- Use dark cards with subtle borders.
- Use red/orange badges for high-risk detections.
- Use blue/neutral colours for normal analytics.

### Required Components
- `MetricCard`
- `RiskDistributionChart`
- `DetectionTrendChart`
- `RecentActivityPanel`
- `TopRiskyDomainsTable`
- `RecentDetectionsTable`

## 2. Detection Queue Page Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Detection Queue | Total Cases | View Controls        │
├──────────────────────────────────────────────────────────────┤
│ Filter Bar: Search | Status | Risk | Prediction | Date Range │
├──────────────────────────────────────────────────────────────┤
│ Detection Case Card / Table Row                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Created | Subject | Severity | Sender | Signal Data       │ │
│ │ Tags | Status | Confidence | Short Explanation            │ │
│ └──────────────────────────────────────────────────────────┘ │
│ Detection Case Card / Table Row                              │
│ Detection Case Card / Table Row                              │
└──────────────────────────────────────────────────────────────┘
```

### Design Notes
- Strongly follow the second reference image.
- Use wide horizontal detection cards.
- Add a coloured severity strip on the left side of high-risk cards.
- Include tags such as:
  - reply-to mismatch
  - long URL
  - urgent language
  - suspicious domain
- Each row/card should be clickable.
- Keep the queue dense and analyst-friendly.

### Required Components
- `DetectionQueueTable`
- `DetectionCaseCard`
- `FilterBar`
- `RiskBadge`
- `ConfidenceBadge`
- `ReviewStatusBadge`
- `ExplanationSummary`

## 3. Email Investigation Page Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Email Investigation | Case ID | Status | Risk Level  │
├────────────────────────────────────────┬─────────────────────┤
│ Email Metadata                         │ Analyst Actions     │
│ - Subject                              │ - Confirm phishing  │
│ - Release email                        │ - Mark false pos.   │
│ - Sender                               │ - Escalate          │
│ - Reply-to                             │                     │
│ - Recipient                            │                     │
│ - Received time                        │                     │
├────────────────────────────────────────┤ Recent Activity     │
│ Model Decision                         │                     │
│ - Prediction                           │                     │
│ - Confidence                           │                     │
│ - Model version                        │                     │
├────────────────────────────────────────┤                     │
│ Sender / URL / Attachment Analysis     │                     │
├────────────────────────────────────────┤                     │
│ Local Explanation Panel                │                     │
└────────────────────────────────────────┴─────────────────────┘
```

### Design Notes
- This page should feel like an incident detail view.
- Put the most important decision information near the top.
- Keep analyst actions visible on the right.
- Show local explanation as an evidence panel, not as a decorative chart.
- Use human-readable explanation above raw technical values.

### Required Components
- `EmailMetadataPanel`
- `ModelDecisionCard`
- `SenderAnalysisPanel`
- `UrlAnalysisPanel`
- `AttachmentAnalysisPanel`
- `LocalExplanationPanel`
- `AnalystActionPanel`
- `CaseActivityTimeline`

## 4. Local Explanation Panel Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Local Explanation                                             │
├──────────────────────────────────────────────────────────────┤
│ Prediction: Phishing | Confidence: 94% | Model: RF v1         │
├──────────────────────────────────────────────────────────────┤
│ Human-readable Summary                                        │
│ "This email was classified as phishing mainly because..."     │
├──────────────────────────────────────────────────────────────┤
│ Feature Contribution Bar Chart                                │
│ sender_replyto_mismatch   +0.24                               │
│ max_url_length            +0.18                               │
│ suspicious_sender_domain  +0.17                               │
├──────────────────────────────────────────────────────────────┤
│ Technical Details                                             │
│ Explainer: SHAP/LIME/Surrogate | Timestamp | Snapshot ID       │
└──────────────────────────────────────────────────────────────┘
```

### Design Notes
- The human-readable explanation must appear before the technical chart.
- SOC analysts should understand the decision quickly.
- Raw numbers should be available but secondary.
- Use positive/negative contribution direction clearly.

### Required Components
- `HumanReadableReason`
- `FeatureContributionChart`
- `FeatureContributionList`
- `ExplanationMetadata`

## 5. Global Explanation Page Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Global Explanation | Model Selector                  │
├──────────────────────────────────────────────────────────────┤
│ Fidelity Metric Cards                                        │
│ [Accuracy Fidelity] [F1 Fidelity] [Error Fidelity]            │
├───────────────────────────────┬──────────────────────────────┤
│ Global Feature Importance      │ Model Behaviour Summary      │
├───────────────────────────────┴──────────────────────────────┤
│ EBM / GAMI-Net Effect Plots                                   │
├──────────────────────────────────────────────────────────────┤
│ False Positive / False Negative Pattern Summary               │
└──────────────────────────────────────────────────────────────┘
```

### Design Notes
- This page should be more analytical than operational.
- It is for model owners, SOC leads, and security managers.
- Use charts and explanation summaries.
- Show Error Fidelity clearly because it is part of the project’s research contribution.
- Make it clear that global explanations describe general model behaviour, not one email.

### Required Components
- `FidelityMetricCards`
- `GlobalFeatureImportanceChart`
- `ModelBehaviourSummary`
- `EffectPlotGallery`
- `FailurePatternSummary`
- `TeacherSurrogateComparison`

## 6. Feedback Review Page Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Feedback Review | Pending Cases                      │
├──────────────────────────────────────────────────────────────┤
│ Feedback Queue Table                                          │
│ Subject | Original Prediction | User Feedback | Status        │
├────────────────────────────────────────┬─────────────────────┤
│ Selected Feedback Detail               │ Analyst Decision    │
│ - Original prediction                  │ - Confirm phishing  │
│ - Original explanation snapshot        │ - Confirm legit     │
│ - User comment                         │ - Mark FP/FN        │
│ - Email metadata                       │ - Reject feedback   │
└────────────────────────────────────────┴─────────────────────┘
```

### Design Notes
- This page should feel like a review queue.
- Preserve original prediction and explanation snapshot.
- Make analyst validation required before feedback is used.
- Do not show any automatic model updating action as immediate.
- Use wording like “Add to future improvement datasetset” rather than “Retrain now”.

### Required Components
- `FeedbackQueueTable`
- `FeedbackDetailPanel`
- `OriginalExplanationSnapshot`
- `AnalystDecisionPanel`
- `FeedbackStatusBadge`

## 7. Model Monitoring Page Wireframe
### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Model Monitoring                                     │
├──────────────────────────────────────────────────────────────┤
│ Current Model Cards                                          │
│ [Detector] [Surrogate] [Version] [Last Updated]              │
├───────────────────────────────┬──────────────────────────────┤
│ Detection Performance          │ Explanation Performance      │
│ Accuracy / Precision / Recall │ Fidelity / Error Fidelity    │
├───────────────────────────────┴──────────────────────────────┤
│ Feedback and improvement readiness                             │
├──────────────────────────────────────────────────────────────┤
│ Model Version History                                         │
└──────────────────────────────────────────────────────────────┘
```

### Design Notes
- This page should support model governance.
- Show model health in simple cards.
- Show explanation reliability, not just detection accuracy.
- Include confirmed false positives and false negatives.

### Required Components
- `ModelVersionCard`
- `DetectionPerformancePanel`
- `ExplanationPerformancePanel`
- `FeedbackReadinessPanel`
- `ModelVersionHistoryTable`

## Component Naming Suggestions

Use these component names in the frontend:

- `DashboardLayout`
- `Sidebar`
- `TopBar`
- `MetricCard`
- `RiskBadge`
- `ConfidenceBadge`
- `ReviewStatusBadge`
- `DetectionQueueTable`
- `DetectionCaseCard`
- `EmailMetadataPanel`
- `ModelDecisionCard`
- `LocalExplanationPanel`
- `GlobalExplanationPanel`
- `FeatureContributionChart`
- `FeatureImportanceChart`
- `RecentActivityPanel`
- `FeedbackQueueTable`
- `AnalystActionPanel`
- `ModelHealthCard`

## Visual Design Notes
### Colours

Use a dark SOC/security palette.

Suggested direction:
- background: dark navy / near-black
- cards: slightly lighter navy
- borders: subtle blue-gray
- primary accent: blue/cyan
- warning: amber/orange
- high risk: red
- success/closed: green
- neutral text: gray/white

Do not use too many colours at once.

### Typography
- Use clear sans-serif fonts.
- Use larger headings for page titles.
- Use compact but readable table text.
- Avoid tiny labels that are hard to read.

### Density
The dashboard should be data-dense but organised.
SOC analysts need to see many cases quickly, especially on:
- Detection Queue
- Quarantine
- Feedback Review

Use spacing carefully.

### Cards and Tables
Use:
- metric cards for summaries
- tables for queues
- detail panels for investigation
- charts for trends and model behaviour

### Risk Indicators
Every major email case should show:
- prediction
- confidence
- risk level
- review status
- action taken

### Explanation Display
Local explanations should be:
- human-readable first
- technical second

Global explanations should be:
- chart-based
- metric-supported
- clearly labelled as model-level behaviour

## Important Implementation Notes for Coding Agents

Before building dashboard UI, agents must read:
- `PROJECT_CONTEXT.md`
- `OUTCOME_REQUIREMENTS.md`
- `AGENTS.md`
- `docs/dashboard/dashboard-pages.md`
- `docs/dashboard/wireframe-notes.md`

The reference images are visual inspiration only.

Do not copy:
- brand logos
- exact UI assets
- exact text
- exact product names
- proprietary branding

Use the images to understand:
- layout structure
- dashboard density
- SOC workflow
- dark theme
- cards/tables/charts
- recent activity panels
- severity indicators
