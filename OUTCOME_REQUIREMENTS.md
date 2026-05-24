# Explainable Phishing Detection System — Product Outcome Requirements

## 1. Product Goal

Build a **SOC-friendly explainable phishing detection and model-governance system with dashboard for business mailboxes**.

The product must not only answer:

> Is this email phishing?

It must also answer:

> Why was this email detected as phishing?  
> What does the model generally rely on?  
> Where does the model fail?  
> How can analysts use feedback to improve the system safely?

The product should scan mailbox emails, classify phishing risk, quarantine high-risk messages, provide local explanations for individual email detections, provide global explanations of model behaviour through surrogate models, and support human-in-the-loop improvement through analyst-confirmed false positive and false negative feedback.

### Positioning

This should be positioned as:

> A SOC-friendly explainable phishing detection and model-governance system with dashboard for business mailboxes.

Do **not** position it as only:

> An AI phishing detector.

The main differentiator is:

```text
Detection + explanation + governance + human-in-the-loop improvement
```

---

## 2. Existing ML/XAI Foundation

The current project/research resources already provide the machine learning and explainability foundation.

### Existing detection models

- Random Forest phishing detector
- Deep Neural Network / MLP phishing detector

### Existing explanation mechanisms

- Local explanation direction:
  - SHAP
  - LIME
- Global surrogate explanation models:
  - EBM / Explainable Boosting Machine
  - GAMI-Net

### Existing evaluation metrics

- Accuracy
- Precision
- Recall
- F1-score
- Accuracy Fidelity
- F1 Fidelity
- Error Fidelity
- Explanation latency comparison

### Existing research contribution

- Global surrogate models can approximate black-box phishing detectors.
- EBM and GAMI-Net can provide interpretable global explanations.
- Error Fidelity helps evaluate whether surrogate models explain teacher-model failure behaviour.
- EBM and GAMI-Net reduce repeated explanation cost compared with repeated SHAP/LIME explanation generation.

### What still needs to be built

The current repo/research is mainly the **ML/XAI core**. The full operational product still requires:

- Mailbox integration
- Live email ingestion
- Feature extraction for live emails
- Prediction API
- Quarantine workflow
- Database
- SOC dashboard frontend
- Local explanation UI
- Global explanation UI
- Feedback review workflow
- Export confirmed feedback for future offline retraining
- Model version tracking

---

## 3. Main Product Functions

## 3.1 Mailbox Connection

The product must connect to a mailbox and retrieve emails for analysis.

### Prototype mailbox

Use Gmail first for MVP development because Gmail labels are easy for prototyping.

Suggested Gmail workflow:

```text
Gmail inbox
→ Gmail API reads messages
→ Model predicts phishing risk
→ Add label such as “Phishing Review” or “Suspicious”
→ Optionally remove from Inbox
→ Store prediction and explanation in database
→ Display result in dashboard
```

### Production/business target mailbox

Use Microsoft 365 Outlook / Exchange Online as the final production target because it is more common in business and SOC environments.

Suggested Microsoft 365 workflow:

```text
Outlook / Microsoft 365 mailbox
→ Microsoft Graph API reads new emails
→ Feature extraction service processes email
→ Detection model classifies risk
→ High-risk emails moved to “Phishing Review” or quarantine folder
→ Dashboard displays detection, explanation, and analyst workflow
```

### Mailbox module requirements

The mailbox module should support:

| Function | Purpose |
|---|---|
| Read incoming emails | Collect new emails for scanning |
| Read selected emails | Allow analysts to manually scan suspicious messages |
| Extract email metadata | Get sender, recipient, reply-to, subject, timestamp, headers |
| Extract body text | Analyse language, urgency, structure, and content |
| Extract URLs | Analyse number of links, domain structure, URL length, path depth |
| Extract attachment metadata | Check file types and attachment indicators |
| Move suspicious emails | Simulate quarantine by moving to a review folder |
| Release emails | Restore legitimate emails after analyst review |

---

## 3.2 Feature Extraction

The product must convert raw emails into the same feature format used during model training.

The model must not directly classify raw email text without consistent preprocessing. Live emails must be transformed into the same feature space as the training pipeline.

Expected transformation:

```text
Raw email
→ clean text
→ extract subject/body features
→ extract URL features
→ extract sender/reply-to features
→ extract attachment features
→ encode/scale/impute values
→ produce the same prediction-ready feature vector
→ send to detection model
```

### Example feature groups

| Feature type | Example features |
|---|---|
| Textual | subject length, body length, body word count, urgent words, exclamation count |
| Sender metadata | sender domain, reply-to mismatch, suspicious sender domain |
| URL | number of links, max URL length, URL path depth, subdomain depth |
| Attachment | has attachment, suspicious attachment type |
| Structural | digit count, number of special characters, body/subject ratio |

### Required modules

Create modules similar to:

```text
feature_extractor.py
predict_email.py
```

### Example output

```json
{
  "email_id": "abc123",
  "subject": "Urgent invoice payment required",
  "prediction": "phishing",
  "confidence": 0.94,
  "features": {
    "num_links": 5,
    "has_urgent_words": 1,
    "max_url_length": 120,
    "sender_replyto_mismatch": 1
  }
}
```

### Important implementation rule

The feature extraction must match the original model training pipeline exactly. If the live product extracts features differently from training, the model output becomes unreliable.

---

## 3.3 Phishing Detection

The product must classify emails as phishing or legitimate and return a confidence/risk score.

### Supported models

| Model | Role |
|---|---|
| Random Forest | Black-box phishing detector |
| Deep Neural Network / MLP | Black-box phishing detector |

### Prediction output format

```json
{
  "email_id": "email_001",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "recommended_action": "quarantine"
}
```

### Risk-level decision engine

The product should not only output phishing/legitimate. It should convert confidence and security indicators into operational actions.

| Risk level | Example condition | Action |
|---|---|---|
| Low | confidence below threshold | Allow email |
| Medium | suspicious but not certain | Warn user / flag for review |
| High | strong phishing confidence | Move to phishing review/quarantine folder |
| Critical | very high confidence or dangerous indicators | Quarantine and notify SOC |

This reduces business disruption from false positives while still protecting users.

---

## 3.4 Quarantine and Safe Handling

The product must **not permanently delete emails**.

Instead, high-risk emails should be moved to a controlled review location such as:

```text
Phishing Review
Suspicious Emails
Quarantine
SOC Review Queue
```

### Recommended quarantine workflow

```text
Email scanned
→ model predicts high phishing risk
→ email is moved to quarantine/review folder
→ dashboard creates investigation case
→ SOC analyst reviews explanation
→ analyst confirms phishing or releases email
```

### Reason

A real phishing detection product must balance **security** and **business continuity**. False positives can interrupt legitimate business communication, so quarantine/review is safer than deletion.

---

# 4. Explanation Functions

The product must provide two explanation layers:

1. **Local explanation** for individual email predictions
2. **Global explanation** for overall model behaviour

It should also include a failure-analysis layer for false positives and false negatives.

---

## 4.1 Local Explanation

Local explanation answers:

> Why was this specific email classified as phishing or legitimate?

This is used during individual email investigation.

### Local explanation methods

- SHAP
- LIME
- Optional fast surrogate-based local contributions

### Local explanation panel must show

| Local explanation element | Why it should be shown |
|---|---|
| Top contributing features | Shows what pushed this email toward phishing |
| Contribution values | Gives technical evidence for analysts |
| Human-readable reason | Makes the explanation understandable |
| Risk indicators | Helps analysts quickly assess danger |
| Raw email metadata | Allows manual verification |
| Links and domains | Supports phishing investigation |
| Sender/reply-to comparison | Helps detect spoofing or impersonation |
| Analyst action buttons | Lets SOC confirm or correct the result |

### Example local explanation

```text
Email: Urgent invoice payment required
Prediction: Phishing
Confidence: 94%
Action: Quarantined

Top contributing indicators:
+ suspicious_sender_domain: strong phishing influence
+ sender_replyto_mismatch: strong phishing influence
+ max_url_length: moderate phishing influence
+ has_urgent_words: moderate phishing influence

Human-readable explanation:
This email was classified as phishing mainly because the sender domain appears suspicious, the reply-to address does not match the sender, and the email contains a long URL combined with urgent payment wording.
```

### Human-readable explanation requirement

Raw SHAP/LIME/surrogate values must be translated into clear SOC-friendly language.

Example conversion:

```text
Raw explanation:
max_url_length contribution = +0.31
sender_replyto_mismatch contribution = +0.25
has_urgent_words contribution = +0.11

Dashboard explanation:
This email was classified as phishing mainly because it contains an unusually long URL, the reply-to address does not match the sender, and the message uses urgent wording.
```

---

## 4.2 Global Explanation

Global explanation answers:

> What does the model generally rely on across many emails?

This is the main product differentiator because it explains model behaviour at scale.

### Global explanation models

- EBM / Explainable Boosting Machine
- GAMI-Net

### Global explanation page must show

| Global explanation output | Purpose |
|---|---|
| Global feature importance | Shows which features the model relies on most |
| Main effect plots | Shows how each feature affects phishing likelihood |
| Interaction plots | Shows how combinations of features affect risk |
| Model fidelity | Shows how well the surrogate approximates the teacher |
| Error fidelity | Shows how well the surrogate explains teacher errors |
| False positive patterns | Shows why legitimate emails are wrongly flagged |
| False negative patterns | Shows why phishing emails are missed |
| Old vs new model comparison | Shows whether retraining improved behaviour |

### Example global explanation dashboard section

```text
Model Behaviour Summary

Top global phishing indicators:
1. max_url_length
2. sender_replyto_mismatch
3. suspicious_sender_domain
4. exclamation_count
5. max_url_path_depth

Surrogate reliability:
Accuracy Fidelity: 0.9260
F1 Fidelity: 0.9280
Error Fidelity: 0.7673
```

### Key questions the global explanation page must answer

```text
What features does the model generally rely on?
Which features increase phishing likelihood?
Which features reduce phishing likelihood?
Does the surrogate faithfully approximate the teacher model?
Where does the model tend to fail?
What patterns are common in false positives?
What patterns are common in false negatives?
```

---

## 4.3 Failure Explanation

Failure explanation focuses on model mistakes.

It answers:

> Why does the model tend to make certain types of mistakes?

### Required failure-analysis questions

The dashboard should answer:

```text
What are the common causes of false positives?
What are the common causes of false negatives?
Which features are causing repeated mistakes?
Is the model over-relying on weak indicators?
Is the model missing new phishing patterns?
```

### Example failure explanation

```text
False positive pattern:
Many legitimate emails are flagged because they contain urgent words and multiple links.

False negative pattern:
Some phishing emails are missed because they use short URLs, clean-looking sender domains, and avoid obvious urgent language.
```

### Why this matters

This converts individual model mistakes into systematic model-improvement insights.

---

# 5. Target Users and Workflows

## 5.1 General Employees

General employees are secondary users. They should not need to understand ML or XAI terminology.

### Employee actions

| Employee action | Purpose |
|---|---|
| View warning | Understand why an email looks suspicious |
| Report as phishing | Send suspicious email to SOC |
| Mark as safe | Report possible false positive |
| Request release | Ask SOC to release quarantined email |
| View simple reason | Learn from the warning |

### Example employee warning

```text
Warning: This email may be phishing.

Reason:
The sender address looks unusual and the email contains a suspicious link.

Actions:
[Report phishing] [Mark as safe] [Send to security team]
```

Employees are feedback providers, not technical analysts.

---

## 5.2 SOC Analysts

SOC analysts are the primary users.

They use the dashboard to:

- Review suspicious emails
- Confirm detections
- Investigate false positives and false negatives
- Decide whether to quarantine, release, or escalate
- Review user feedback
- Analyse repeated phishing/failure patterns

### SOC analyst requirements

| SOC function | Product support |
|---|---|
| Triage suspicious emails | Detection queue |
| Understand why email was flagged | Local explanation panel |
| Confirm phishing | Analyst decision buttons |
| Release false positives | Quarantine release function |
| Escalate dangerous cases | Escalation workflow |
| Review user reports | Feedback review page |
| Identify campaigns | Sender/domain trend panels |
| Analyse repeated failures | Global/failure explanation page |

### SOC analyst workflow

```text
Open detection queue
→ filter high-risk emails
→ inspect email detail
→ read local explanation
→ check sender, URLs, attachments
→ confirm phishing or legitimate
→ quarantine, release, or escalate
→ mark case outcome
→ feedback saved for model improvement
```

---

## 5.3 Security Managers / CISOs / Risk Teams

Security managers use the dashboard for governance and high-level visibility. They do not inspect every email.

### Questions they need answered

```text
Is the model reliable?
How many emails are being quarantined?
Are false positives disrupting business?
Are false negatives creating risk?
What indicators does the model rely on?
Is model behaviour changing over time?
Can we justify the model’s decisions?
```

### Manager dashboard items

| Manager dashboard item | Why it matters |
|---|---|
| Total scanned emails | Shows operational coverage |
| Detection rate | Shows volume of threats |
| Quarantine rate | Shows business impact |
| False positive rate | Shows disruption risk |
| False negative rate | Shows security risk |
| Model fidelity | Shows surrogate reliability |
| Error fidelity | Shows failure explanation quality |
| Feature importance | Shows whether model reasoning is sensible |
| Trend over time | Shows whether threat landscape/model behaviour is changing |

---

## 5.4 ML Engineers / Model Owners

ML engineers and model owners use the dashboard to improve the system safely.

### Technical user needs

| Technical function | Purpose |
|---|---|
| View confirmed false positives | Understand over-blocking |
| View confirmed false negatives | Understand missed phishing |
| Analyse feature contribution patterns | Improve feature engineering |
| Compare model versions | Prevent regression |
| Retrain with confirmed feedback | Improve detection |
| Generate improvement recommendations | Keep explanations aligned |
| Monitor drift | Detect changes in email patterns |

---

# 6. Human-in-the-Loop Improvement

Human-in-the-loop improvement means the system improves through validated human feedback.

## 6.1 Important rule

The model must **not** automatically learn from every user flag.

User feedback must be reviewed by a SOC analyst before being used for retraining.

### Reason

Users can be wrong, and attackers may abuse feedback to poison the model. For example, an attacker could repeatedly mark phishing emails as safe to weaken detection.

---

## 6.2 Feedback Types

The system must support these feedback outcomes:

| Situation | Meaning |
|---|---|
| Model says phishing, analyst confirms phishing | True positive |
| Model says legitimate, analyst confirms legitimate | True negative |
| Model says phishing, analyst says legitimate | False positive |
| Model says legitimate, analyst says phishing | False negative |

False positives show that the model is too aggressive.  
False negatives show that the model is missing threats.

---

## 6.3 Feedback Workflow

A safe human-in-the-loop workflow should be:

```text
1. Email is scanned.
2. Model predicts phishing or legitimate.
3. System provides local explanation.
4. User or analyst flags the decision.
5. SOC analyst reviews the email.
6. Analyst confirms the true label.
7. System stores the confirmed case.
8. Confirmed cases are added to feedback dataset.
9. Model owner reviews failure patterns.
10. Export confirmed feedback for future offline retraining.
11. Support model version comparison when manually supplied.
12. Old and new models are compared.
13. New model is deployed only if it improves performance safely.
```

---

## 6.4 Feedback Data to Store

Each feedback case should store:

| Field | Why it is needed |
|---|---|
| email_id | Link feedback to the email |
| raw metadata | Preserve investigation context |
| extracted features | use for improvement analysis |
| model prediction | Know what the model originally said |
| confidence score | Measure uncertainty |
| model version | Track which model made the decision |
| local explanation snapshot | Preserve why the model made that decision |
| user feedback | Capture reported problem |
| analyst-confirmed label | Ground truth for improvement |
| error type | False positive / false negative |
| review status | Pending / confirmed / rejected |
| timestamp | Support audit trail |
| analyst ID | Accountability |
| action taken | Quarantined, released, escalated |

---

## 6.5 Retraining Process

The model should be retrained periodically, not instantly.

Recommended improvement cycle:

```text
Confirmed feedback cases
+ original training dataset
+ recent validated emails
→ generate improvement recommendations
→ evaluate on validation/test set
→ evaluate false positives/false negatives
→ evaluate model version comparison
→ compare explanation behaviour
→ deploy if approved
```

### Pre-deployment comparison metrics

Before deploying a new model, compare:

| Metric | Why |
|---|---|
| Accuracy | Overall correctness |
| Precision | Avoid too many false positives |
| Recall | Avoid missing phishing |
| F1-score | Balanced performance |
| False positive rate | Business disruption risk |
| False negative rate | Security risk |
| Accuracy Fidelity | Surrogate agreement |
| F1 Fidelity | Surrogate agreement by class |
| Error Fidelity | Surrogate quality on failure cases |
| Explanation latency | Operational scalability |

---

# 7. Dashboard Requirements

The dashboard must follow a real SOC workflow, not just show charts.

## 7.1 Sidebar Navigation

The sidebar should include:

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

---

## 7.2 Overview Page

### Goal

Give SOC analysts and managers a fast summary of mailbox threat activity and model health.

### Required components

| Dashboard component | Why it should be shown |
|---|---|
| Total emails scanned | Shows system coverage |
| Phishing detected | Shows threat volume |
| Quarantined emails | Shows how many emails were blocked/reviewed |
| Pending review cases | Helps SOC prioritise work |
| False positive reports | Shows possible business disruption |
| False negative reports | Shows possible security gaps |
| Average model confidence | Shows model certainty |
| High-risk detections | Helps analysts focus immediately |
| Phishing trend over time | Shows attack spikes/campaigns |
| Top risky sender domains | Helps identify repeated sources |
| Top risky URL domains | Helps investigate infrastructure |
| Confidence distribution | Shows whether many decisions are uncertain |

### Example layout

```text
Top cards:
- Emails scanned today: 1,248
- Phishing detected: 86
- Quarantined: 42
- Pending review: 17
- False positive reports: 5
- False negative reports: 2

Charts:
- Phishing detections over time
- Risk level distribution
- Top sender domains
- Model confidence distribution

Table:
- Recent high-risk detections
```

---

## 7.3 Detection Queue Page

### Goal

Turn detected emails into investigation cases.

### Required table columns

| Column | Why |
|---|---|
| Received time | Prioritise recent threats |
| Sender | Identify suspicious sources |
| Subject | Understand context |
| Prediction | Phishing/legitimate |
| Confidence | Shows certainty |
| Risk level | Helps triage |
| Action taken | Allowed, warned, quarantined |
| Explanation summary | Quick reason |
| Review status | Pending, confirmed, released |
| Assigned analyst | SOC workflow management |

### Required filters

```text
Risk level
Prediction
Confidence range
Quarantine status
Reviewed / unreviewed
False positive reports
False negative reports
Sender domain
Date range
Attachment present
URL present
```

---

## 7.4 Email Investigation Page

### Goal

Allow analysts to inspect one email deeply.

### Required sections

| Section | Content |
|---|---|
| Email summary | Subject, sender, recipient, timestamp |
| Model decision | Prediction, confidence, risk level |
| Current action | Allowed, warned, quarantined |
| Sender analysis | Sender domain, reply-to, mismatch |
| URL analysis | Links, URL length, domain, path depth |
| Attachment analysis | Attachment count/type |
| Body indicators | Urgent words, exclamation count, digit count |
| Local explanation | Top features and contribution scores |
| Analyst actions | Confirm, release, escalate, mark error |

### Example investigation case

```text
Subject: Urgent Payment Required
Sender: billing@pay-security-support.com
Reply-to: accounts.payments@gmail.com

Prediction: Phishing
Confidence: 94%
Risk level: High
Action: Quarantined

Local explanation:
- Reply-to mismatch strongly increased phishing risk.
- Long URL path increased phishing risk.
- Urgent wording increased phishing risk.
- Suspicious sender domain increased phishing risk.

Analyst actions:
[Confirm phishing] [Release email] [Mark false positive] [Escalate]
```

---

## 7.5 Local Explanation Page / Panel

### Goal

Explain a single prediction.

### Required components

| Component | Why |
|---|---|
| Prediction and confidence | Shows result |
| Feature contribution bar chart | Shows strongest reasons |
| Top positive features | Shows what pushed toward phishing |
| Top negative features | Shows what reduced phishing risk |
| Human-readable explanation | Makes result understandable |
| Raw values | Allows technical verification |
| Explainer method | SHAP, LIME, or surrogate-based |
| Explanation timestamp/model version | Supports auditability |

### Example local explanation

```text
Human-readable explanation:
This email was classified as phishing because the sender domain appears suspicious, the reply-to address does not match the sender, and the URL structure is unusually long and complex.

Top phishing-driving features:
1. sender_replyto_mismatch: +0.24
2. max_url_length: +0.18
3. suspicious_sender_domain: +0.17
4. has_urgent_words: +0.11

Top risk-reducing features:
1. body_length_normal_range: -0.05
2. no_attachment: -0.03
```

---

## 7.6 Global Explanation Page

### Goal

Explain overall model behaviour.

### Required components

| Component | Why |
|---|---|
| Global feature importance | Shows what the model relies on most |
| EBM main effect plots | Shows threshold-like feature behaviour |
| GAMI-Net effect plots | Shows smoother feature behaviour |
| Interaction effects | Shows feature combinations |
| Fidelity metrics | Shows surrogate trustworthiness |
| Error Fidelity | Shows explanation quality on mistakes |
| Teacher/surrogate comparison | Shows which surrogate best explains the model |
| Feature trend changes | Shows behaviour shift over time |

### Example global explanation panel

```text
Global Model Behaviour

Top global indicators:
1. max_url_length
2. max_url_path_depth
3. exclamation_count
4. suspicious_sender_domain
5. sender_replyto_mismatch

Reliability:
Accuracy Fidelity: 0.9260
F1 Fidelity: 0.9280
Error Fidelity: 0.7673

Interpretation:
Longer URLs and deeper URL paths generally increase phishing likelihood. Higher exclamation count also increases risk, suggesting that urgent or emotional language contributes to phishing classification.
```

---

## 7.7 False Positive / False Negative Analysis Page

### Goal

Show where the model fails.

### Required components

| Component | Why |
|---|---|
| Confirmed false positives | Shows over-blocking |
| Confirmed false negatives | Shows missed threats |
| Common false positive features | Reveals overly aggressive signals |
| Common false negative features | Reveals weak detection areas |
| Error Fidelity score | Shows whether surrogate explains failures |
| Failure trend over time | Shows whether the model is improving |
| Recommended improvement actions | Turns analysis into next steps |

### Example failure analysis

```text
False positive pattern:
Legitimate business emails with urgent wording and multiple links are often classified as phishing.

Possible improvement:
Add more legitimate business emails containing urgent language into the retraining set.

False negative pattern:
Phishing emails with short URLs and clean-looking sender domains are sometimes missed.

Possible improvement:
Add stronger sender authentication and domain reputation features.
```

---

## 7.8 Feedback Review Page

### Goal

Support human-in-the-loop improvement.

### Required components

| Component | Why |
|---|---|
| User-reported emails | Shows feedback queue |
| Original model prediction | Shows what the model said |
| Original explanation | Shows why the model made that decision |
| User comment | Captures human context |
| Analyst-confirmed label | Creates reliable ground truth |
| Error type | Categorises false positive/false negative |
| Export to improvement dataset | Supports improvement |
| Reject feedback | Prevents bad feedback from poisoning model |

### Example feedback case

```text
Case: email_1024
Model prediction: Phishing
User feedback: This is a legitimate supplier invoice.
Analyst review: Confirmed legitimate.
Error type: False positive.
Reason category: Legitimate business email with urgent language.
Action: Released from quarantine and exported for future offline retraining.
```

---

## 7.9 Model Monitoring Page

### Goal

Track model health and deployment state.

### Required components

| Component | Why |
|---|---|
| Current model version | Know what is deployed |
| Current surrogate version | Match explanations to model |
| Accuracy/precision/recall/F1 | Monitor detection performance |
| False positive/negative rates | Monitor operational risk |
| Fidelity metrics | Monitor explanation quality |
| Error Fidelity | Monitor failure explanation quality |
| Explanation latency | Monitor dashboard performance |
| Feedback cases collected | Show improvement readiness |
| improvement history | Track improvement |
| Old vs new model comparison | Prevent bad updates |

### Example model monitoring cards

```text
Current detector: Random Forest v1.2
Current global surrogate: EBM v1.2

Detection performance:
Accuracy: 0.9433
F1: 0.9450

Explanation performance:
Accuracy Fidelity: 0.9260
F1 Fidelity: 0.9280
Error Fidelity: 0.7673

Feedback:
Confirmed false positives: 48
Confirmed false negatives: 21
Pending review: 17
```

---

# 8. Full Product Workflow

The final system workflow should be:

```text
1. A new email arrives in the mailbox.
2. The ingestion service reads the email.
3. The feature extraction service converts the email into model features.
4. The phishing detection model predicts:
   - phishing or legitimate
   - confidence score
   - risk level
5. The decision engine decides:
   - allow
   - warn
   - quarantine
   - escalate
6. The explanation service generates:
   - local explanation for this email
   - global explanation references from surrogate model
7. The dashboard displays:
   - detection result
   - risk indicators
   - local explanation
   - email metadata
   - recommended action
8. The SOC analyst reviews the case.
9. The analyst confirms:
   - true positive
   - true negative
   - false positive
   - false negative
10. Confirmed feedback is stored.
11. The model owner reviews failure patterns.
12. Generate improvement recommendations.
13. Support model version comparison when manually supplied.
14. The dashboard shows improved model behaviour and updated global explanations.
```

---

# 9. Technical Outcome Requirements

## 9.1 Backend

Build a backend with:

- FastAPI prediction service
- Feature extraction module
- Model loading module
- Prediction module
- Explanation module
- Feedback storage module
- Quarantine/move-email module
- Model monitoring module
- Retraining trigger/module for future extension

### Suggested API endpoints

```text
POST /scan-email
GET /emails
GET /emails/{id}
GET /emails/{id}/local-explanation
GET /global-explanation
POST /emails/{id}/feedback
POST /emails/{id}/quarantine
POST /emails/{id}/release
GET /model-monitoring
POST /feedback/export-dataset
```

---

## 9.2 Frontend

Build a React/Tailwind SOC dashboard with:

- Overview page
- Detection queue
- Quarantine page
- Email investigation page
- Local explanation panel
- Global explanation page
- False positive / false negative analysis page
- Feedback review page
- Model monitoring page
- Settings page

### Recommended frontend stack

- React
- TypeScript
- Tailwind CSS
- TailAdmin React template
- Recharts or Chart.js for charts

---

## 9.3 Database

Recommended for prototype:

- SQLite

Recommended for realistic product:

- PostgreSQL

### Required tables

```text
emails
predictions
explanations
feedback
model_versions
quarantine_actions
analyst_reviews
```

### emails table should store

- email_id
- mailbox_source
- sender
- recipient
- reply_to
- subject
- received_time
- body_preview
- raw_metadata_json
- urls_json
- attachments_json
- created_at

### predictions table should store

- prediction_id
- email_id
- model_version
- prediction
- confidence
- risk_level
- recommended_action
- created_at

### explanations table should store

- explanation_id
- email_id
- prediction_id
- explainer_type
- top_features_json
- contribution_values_json
- human_readable_explanation
- explanation_snapshot_json
- created_at

### feedback table should store

- feedback_id
- email_id
- prediction_id
- user_feedback
- analyst_confirmed_label
- error_type
- review_status
- analyst_id
- reason_category
- added_to_improvement_dataset
- created_at

### model_versions table should store

- model_version
- detector_type
- surrogate_type
- accuracy
- precision
- recall
- f1
- accuracy_fidelity
- f1_fidelity
- error_fidelity
- explanation_latency
- deployed_at

---

## 9.4 ML/XAI Components

The system should support:

- Random Forest detector
- DNN / MLP detector
- SHAP local explanation
- LIME local explanation
- EBM global surrogate explanation
- GAMI-Net global surrogate explanation
- Fidelity metrics display
- Error Fidelity display
- Explanation latency display

---

# 10. Suggested Tech Stack

## Frontend

```text
React
TypeScript
Tailwind CSS
TailAdmin React template
Recharts or Chart.js
```

## Backend

```text
FastAPI
Python
scikit-learn
pandas
numpy
SHAP
LIME
interpretML / EBM
GAMI-Net implementation
```

## Database

```text
SQLite for prototype
PostgreSQL for realistic deployment
```

## Mailbox API

```text
Prototype: Gmail API
Production target: Microsoft Graph API for Outlook / Microsoft 365
```

## Deployment

```text
Prototype: localhost
More realistic: Docker Compose
Production-like: cloud VM + Docker Compose + reverse proxy + HTTPS
```

---
# 12. UI/Design Requirements

Use a dark SOC-style dashboard, but keep it professional and realistic.

Design direction:

> Microsoft Defender-style seriousness + modern SaaS dashboard clarity.

Avoid:

- Overly flashy “hacker movie” UI
- Excessive neon effects
- Unreadable chart colours
- Too many charts without workflow purpose

Recommended visual structure:

```text
Left sidebar navigation
Top metric cards
Central detection table
Right-side explanation/risk panel
Charts for trend and model behaviour
Clear analyst action buttons
```

---

# 13. Safety and Security Requirements

1. Do not instantly trust user feedback.
   - User feedback must be reviewed before model improvement.

2. Do not permanently delete detected phishing emails.
   - Move them to a quarantine/review folder instead.

3. Store only necessary email data.
   - Avoid storing sensitive email content unless needed.

4. Log model versions.
   - Every prediction should record which model version produced it.

5. Preserve explanation snapshots.
   - If the model changes later, old explanations should still match the old decision.

6. Avoid automatic self-learning from unverified flags.
   - This can cause model poisoning.

7. Make explanations clear but not overconfident.
   - Explanations show what influenced the model, not absolute proof of malicious intent.

8. Ensure quarantine is reversible.
   - Analysts must be able to release false positives.

9. Keep audit trails.
   - Store who reviewed a case, what decision was made, and when.

---

# 14. Expected Final User-Facing Outcome

The final prototype should allow a user to say:

> The system scanned mailbox emails, detected suspicious phishing messages, moved high-risk emails to a review/quarantine folder, explained why each email was flagged, showed how the detection model behaves globally, and allowed analysts to confirm mistakes for future model improvement.

---

# 15. Expected Academic/Research Outcome

The project should be explainable as:

> This product extends the research contribution from an offline explainable phishing detection experiment into an operational SOC-style dashboard. It demonstrates how global surrogate explanations and local explanations can support phishing email triage, model transparency, failure analysis, and human-in-the-loop improvement.

---

# 16. Core Product Value

The strongest value is not just phishing detection. Many tools can detect phishing.

The product value is:

```text
Detection + explanation + governance + feedback improvement
```

| Product value | Explanation |
|---|---|
| Better analyst trust | SOC analysts can see why an email was flagged |
| Faster triage | Local explanation highlights important indicators |
| Better model governance | Global explanation shows overall model behaviour |
| Better failure analysis | Error Fidelity and feedback reveal recurring mistakes |
| Safer improvement | Human-in-the-loop validation avoids unsafe self-learning |
| Business suitability | Quarantine/release workflow reduces disruption |
| Research novelty | Global surrogate explanations address the gap in local-only XAI |

---

# 17. Official Product Goal Statement

Use the following as the official goal statement:

> The goal of this product is to build an explainable phishing email detection platform for business mailboxes. The system will connect to a mailbox, scan incoming emails, extract phishing-relevant features, classify each email using trained machine learning models, assign a risk score, and move high-risk emails into a safe quarantine/review workflow. For each detected email, the system will provide local explanations showing the main reasons behind the classification, such as suspicious sender domains, reply-to mismatch, urgent wording, or abnormal URL structure. At the management level, the system will provide global explanations using surrogate models such as EBM and GAMI-Net to show the overall behaviour of the black-box phishing detector, including feature importance, feature effects, interaction patterns, fidelity, and error-fidelity results. The dashboard will support SOC analysts in triaging suspicious emails, security managers in understanding model reliability, and ML/model owners in identifying recurring false positive and false negative patterns. A human-in-the-loop feedback mechanism will allow users and analysts to flag incorrect detections, but only analyst-confirmed feedback will be added to a improvement datasetset, enabling controlled model improvement while reducing the risk of feedback poisoning. The final outcome is a SOC-friendly phishing detection and model-governance dashboard that does not only detect phishing emails, but also explains, monitors, and improves the detection process over time.

---
