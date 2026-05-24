# Dashboard Pages

## Purpose

This document defines the required dashboard pages for the explainable phishing detection product.

The dashboard should be designed as a professional SOC/security operations interface for phishing email detection, quarantine review, local explanations, global model behaviour analysis, and human-in-the-loop feedback.

The selected UI inspiration follows a dark SOC-style dashboard with:

- left-side navigation
- dark navy/black background
- high-contrast cards
- alert/insight queues
- timeline and activity panels
- table-heavy investigation views
- severity/risk badges
- entity/activity summaries
- recent activity feed
- filters and sorting controls

The goal is not to copy the reference dashboards exactly, but to adapt their security operations workflow and visual structure to the phishing detection product.

---

## Global Dashboard Style

The dashboard should feel like:

> A serious SOC analyst console for explainable phishing detection.

The UI should be:

- professional
- dark themed
- clean and readable
- security-focused
- data-dense but not chaotic
- suitable for SOC analysts and security managers
- similar in seriousness to Microsoft Defender, Sentinel, Sumo Logic, or enterprise SOC dashboards

Avoid:

- childish hacker visuals
- excessive neon colours
- fake terminal effects
- overuse of animations
- decorative cyber backgrounds
- unreadable small labels
- copying logos or branding from reference images

---

## Main Navigation

Use a left sidebar or top-left navigation menu with these pages:

```text
Overview
Detection Queue
Quarantine
Email Investigation
Local Explanation
Global Explanation
Feedback Review
Model Monitoring
Settings
```

The main SOC analyst workflow should be:

```text
Overview
→ Detection Queue
→ Email Investigation
→ Local Explanation
→ Analyst Decision
→ Feedback Review
→ Model Monitoring
```

## 1. Overview Page
### Purpose

The Overview Page gives SOC analysts and security managers a high-level summary of phishing detection activity, system status, recent alerts, and model behaviour.

This page should be inspired by the reference dashboard that shows:

- system metrics
- insight metrics
- circular/radar-style activity visualisation
- recent activity panel
- most active entities
- status distribution

### Main Sections
#### 1.1 Top System Metrics

Show summary cards at the top.

Required cards:

| Card | Meaning |
|---|---|
| Emails Scanned | Total emails processed in selected time window |
| Phishing Detected | Number of emails classified as phishing |
| Quarantined | Number of emails moved to review/quarantine |
| Pending Review | Number of emails awaiting analyst decision |
| False Positive Reports | Emails marked as wrongly detected phishing |
| False Negative Reports | Emails reported as missed phishing |
| Average Confidence | Average model prediction confidence |
| High Risk Cases | Number of high/critical risk detections |

Example:

```text
Emails Scanned: 1,248
Phishing Detected: 86
Quarantined: 42
Pending Review: 17
False Positives: 5
False Negatives: 2
Average Confidence: 91%
```

#### 1.2 Detection Trend Chart

Show phishing detections over time.

Purpose:

- identify spikes
- detect phishing campaigns
- show whether threat activity is increasing

Recommended chart:

- line chart or bar chart
- x-axis: time
- y-axis: number of detections
- series: phishing, legitimate, quarantined

#### 1.3 Risk Distribution

Show the distribution of email risk levels.

Risk levels:

- Low
- Medium
- High
- Critical

Recommended chart:

- donut chart
- stacked bar chart

Purpose:

- let SOC analysts quickly understand how many detections are urgent

#### 1.4 Top Risky Sender Domains

Show sender domains that appear most frequently in suspicious emails.

Columns:

- sender domain
- number of emails
- phishing count
- average confidence
- latest detection time

Purpose:

- identify repeated phishing infrastructure or suspicious sender patterns

#### 1.5 Recent High-Risk Activity

Show a right-side Recent Activity feed similar to the reference dashboard.

Each activity item should include:

- timestamp
- subject or detection title
- action taken
- status change
- analyst if assigned
- severity/risk level

Example:

```text
10:42 AM — Email "Urgent Invoice Payment" classified as High Risk
10:45 AM — Email moved to Quarantine
10:52 AM — Analyst marked case as False Positive
```

#### 1.6 Model Health Snapshot

Show a compact model health card.

Fields:

- current detector model
- current surrogate model
- model version
- accuracy
- F1 score
- accuracy fidelity
- error fidelity

Purpose:

- give managers quick visibility into model reliability

## 2. Detection Queue Page
### Purpose

The Detection Queue Page is the main SOC analyst triage page.

It should be inspired by the reference dashboard that shows multiple security insights as stacked list/table cards with:

- creation time
- title
- severity
- entity
- signal data
- status
- tags

For this product, each row/card represents one scanned email or suspicious detection case.

### Main Components
#### 2.1 Filter Bar

At the top, include filters similar to the reference image.

Required filters:

- search subject/sender
- risk level
- prediction
- confidence range
- quarantine status
- review status
- sender domain
- has links
- has attachment
- date range

Example filters:

```text
Status is not Closed
Risk is High or Critical
Prediction is Phishing
Created desc
```

#### 2.2 Detection Case List

Each detection should be displayed as either a table row or large SOC-style card.

Required fields:

| Field | Meaning |
|---|---|
| Created / Received Time | When the email was received or scanned |
| Subject | Email subject |
| Sender | Sender email/domain |
| Prediction | Phishing or legitimate |
| Confidence | Model confidence |
| Risk Level | Low/Medium/High/Critical |
| Action Taken | Allowed, Warned, Quarantined |
| Review Status | New, In Review, Confirmed, Released |
| Local Reason Summary | Short explanation |
| Assigned Analyst | Analyst handling the case |

Example card layout:

```text
Created: 10/21/2026 6:27 AM
Subject: Urgent Invoice Payment Required
Sender: billing-support@example-security.com
Prediction: Phishing
Confidence: 94%
Severity: High
Action: Quarantined
Status: New
Top Reasons: Reply-to mismatch, suspicious domain, long URL
```

#### 2.3 Severity Badges

Use clear badges:

- Low: muted
- Medium: warning
- High: strong red/orange
- Critical: most visible

The reference dashboard uses strong vertical severity bars. This can be adapted as a left border on each detection card.

#### 2.4 Click-through Behaviour

Clicking a detection should open:

- Email Investigation Page

## 3. Quarantine Page
### Purpose

The Quarantine Page shows emails that have been moved to a safe review state.

The product must not permanently delete emails. Quarantine is a reversible safety workflow.

### Required Components
#### 3.1 Quarantined Email Table

Columns:

- received time
- subject
- sender
- confidence
- risk level
- quarantine reason
- quarantine time
- review status
- assigned analyst

#### 3.2 Actions

Each quarantined email should support:

- open investigation
- confirm phishing
- release email
- mark false positive
- escalate

#### 3.3 Quarantine Summary Cards

Show:

- total quarantined
- pending review
- released today
- confirmed phishing
- false positives found

Purpose:

- help SOC analysts manage business impact caused by quarantine

## 4. Email Investigation Page
### Purpose

The Email Investigation Page is the detailed case view for one email.

This page should feel like a security incident/entity detail page.

### Layout

Use a two-column layout:

Left/main area:
- email metadata
- prediction result
- URL/sender/attachment analysis
- local explanation

Right side panel:
- case status
- analyst actions
- recent activity
- related detections

### Required Sections
#### 4.1 Email Summary

Show:

- subject
- sender
- recipient
- reply-to
- received time
- mailbox source
- current folder/status

#### 4.2 Model Decision

Show:

- prediction label
- confidence score
- risk level
- recommended action
- model name
- model version

Example:

```text
Prediction: Phishing
Confidence: 94%
Risk Level: High
Recommended Action: Quarantine
Model: Random Forest
Version: rf_v1
```

#### 4.3 Sender Analysis

Show:

- sender email
- sender domain
- reply-to email
- reply-to mismatch indicator
- suspicious sender domain indicator

Purpose:

- help analysts validate spoofing or impersonation signals

#### 4.4 URL Analysis

Show:

- number of links
- top URL domains
- maximum URL length
- URL path depth
- suspicious URL indicators

Purpose:

- phishing emails often rely on suspicious or misleading links

#### 4.5 Attachment Analysis

Show:

- attachment count
- attachment names if available
- attachment types
- suspicious attachment type indicator

#### 4.6 Local Explanation Panel

Embed or link to the Local Explanation Page/Panel.

Show:

- top contributing features
- contribution values
- human-readable explanation
- explanation method
- explanation timestamp

#### 4.7 Analyst Actions

Buttons:

- Confirm phishing
- Confirm legitimate
- Mark false positive
- Mark false negative
- Release from quarantine
- Escalate
- Add to improvement datasetset

Important:

Adding to improvement datasetset should only happen after analyst confirmation.

## 5. Local Explanation Page / Panel
### Purpose

Local explanation answers:

> Why was this specific email classified this way?

This is for SOC analyst investigation and user-facing warning explanations.

### Required Components
#### 5.1 Prediction Summary

Show:

- prediction
- confidence
- risk level
- model version

#### 5.2 Feature Contribution Chart

Show a horizontal bar chart of top contributing features.

Suggested fields:

- feature name
- contribution value
- direction
- human-readable reason

Example features:

- sender_replyto_mismatch
- suspicious_sender_domain
- max_url_length
- max_url_path_depth
- has_urgent_words
- exclamation_count
- num_links
- body_length

#### 5.3 Human-Readable Explanation

Example:

```text
This email was classified as phishing mainly because the reply-to address does not match the sender, the sender domain appears suspicious, and the email contains an unusually long URL.
```

#### 5.4 Technical Explanation Details

Show only for analysts:

- explainer method
- SHAP/LIME/surrogate-based contribution
- raw contribution value
- feature raw value
- model version
- timestamp

#### 5.5 Explanation Safety

Do not write:

```text
This email is definitely phishing.
```

Use:

```text
The model classified this email as phishing mainly because...
```

## 6. Global Explanation Page
### Purpose

Global explanation answers:

> What patterns does the model generally rely on across many emails?

This page is mainly for:

- security managers
- model owners
- SOC leads
- governance/risk teams

### Required Components
#### 6.1 Global Feature Importance

Show top global phishing indicators.

Example:

```text
1. max_url_length
2. sender_replyto_mismatch
3. suspicious_sender_domain
4. exclamation_count
5. max_url_path_depth
```

#### 6.2 EBM / GAMI-Net Explanation Charts

Show:

- EBM main effect plots
- GAMI-Net main effect plots
- interaction effect plots
- feature contribution trends

#### 6.3 Fidelity Metrics

Show:

- Accuracy Fidelity
- F1 Fidelity
- Error Fidelity

Purpose:

- explain whether the surrogate is a reliable approximation of the teacher model

#### 6.4 Failure Pattern Summary

Show false positive and false negative patterns.

Examples:

```text
False positive pattern:
Legitimate business emails with urgent wording and multiple links are often classified as phishing.

False negative pattern:
Some phishing emails with clean-looking sender domains and short URLs are missed.
```

#### 6.5 Model Comparison

If available, compare:

- Random Forest teacher
- DNN teacher
- EBM surrogate
- GAMI-Net surrogate

## 7. Feedback Review Page
### Purpose

The Feedback Review Page supports human-in-the-loop improvement.

Users can flag wrong detections, but feedback must be reviewed by a SOC analyst before it is used for future retraining.

### Required Components
#### 7.1 Feedback Queue

Columns:

- email subject
- original prediction
- original confidence
- user feedback
- analyst label
- error type
- review status
- timestamp

#### 7.2 Feedback Detail Panel

Show:

- original model prediction
- original local explanation snapshot
- user comment
- analyst decision
- reason category

#### 7.3 Analyst Actions

Actions:

- confirm phishing
- confirm legitimate
- mark false positive
- mark false negative
- reject feedback
- release from quarantine
- export to improvement dataset

#### 7.4 Error Type Mapping

Use this logic:

| Model Prediction | Analyst Label | Case Type |
|---|---|---|
| phishing | phishing | true positive |
| legitimate | legitimate | true negative |
| phishing | legitimate | false positive |
| legitimate | phishing | false negative |

## 8. Model Monitoring Page
### Purpose

The Model Monitoring Page tracks model health, explanation quality, and model versions.

### Required Components
#### 8.1 Current Model Cards

Show:

- current detector model
- current surrogate model
- model version
- deployment date

#### 8.2 Detection Performance

Show:

- accuracy
- precision
- recall
- F1 score
- false positive rate
- false negative rate

#### 8.3 Explanation Performance

Show:

- accuracy fidelity
- F1 fidelity
- error fidelity
- explanation latency

#### 8.4 Feedback and improvement readiness

Show:

- confirmed false positives
- confirmed false negatives
- pending feedback
- cases exported for future offline retraining
- last model update date

#### 8.5 Model Version History

Show old vs new model versions if available.

## 9. Settings Page
### Purpose

The Settings Page allows configuration of product behaviour.

Possible Settings:
- risk threshold
- quarantine threshold
- selected detector model
- selected explanation method
- mailbox provider
- dashboard time range
- analyst notification settings

For MVP, this page can be simple or placeholder.