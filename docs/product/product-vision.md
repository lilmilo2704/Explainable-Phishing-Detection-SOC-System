# Product Vision

## Product Name

Working name:

```text
Explainable Phishing Detection Dashboard
```

Alternative names:

```text
PhishXAI Dashboard
SOC Explainable Phishing Console
Explainable Mail Security Dashboard
```

---

## Product Identity

This product is a SOC-friendly explainable phishing detection and model-governance dashboard for business mailboxes.

It extends an existing research project on global explainability and explanation latency in phishing email detection into an operational software product.

The product should not be positioned as only:

```text
An AI phishing detector
```

It should be positioned as:

```text
A phishing detection, explanation, quarantine, feedback, and model-governance platform for SOC analysts.
```

---

## Problem

Phishing detection models can identify suspicious emails, but many machine learning models behave like black boxes. SOC analysts and security managers may not know why an email was classified as phishing, what features the model generally relies on, or where the model tends to fail.

Existing local explanation methods such as SHAP and LIME are useful for individual predictions, but they can be computationally expensive and do not fully explain the overall behaviour of the model.

This product addresses that gap by combining:

- phishing email classification
- local explanation for individual emails
- global explanation of model behaviour
- analyst feedback review
- model monitoring
- quarantine and release workflow

---

## Product Goal

The product should help security teams answer:

```text
Is this email phishing?
Why was this email classified this way?
What indicators made the model suspicious?
What does the model generally rely on?
Where does the model tend to fail?
Which false positives and false negatives need review?
How can confirmed feedback support future model improvement?
```

---

## Target Users

### Primary Users

SOC analysts and email security analysts.

They use the product to:

- triage suspicious emails
- review quarantined emails
- inspect local explanations
- confirm phishing or legitimate emails
- mark false positives and false negatives
- release legitimate emails
- escalate dangerous cases

### Secondary Users

General employees or mailbox users.

They use the product to:

- report suspicious emails
- mark wrongly detected emails
- view simple warning reasons

They should not need to understand model details.

### Management Users

Security managers, CISOs, risk teams, and compliance teams.

They use the product to:

- monitor detection volume
- monitor false positive/false negative trends
- understand model behaviour
- review global explanation metrics
- assess trustworthiness and governance

### Technical Users

ML engineers, model owners, and security engineers.

They use the product to:

- inspect model behaviour
- analyse failure patterns
- review feedback data
- compare model versions
- prepare future retraining

---

## Main Product Capabilities

### 1. Mailbox Scanning

The system should connect to a mock mailbox for MVP, then later Gmail or Microsoft 365.

It should read incoming or selected emails and send them for classification.

### 2. Phishing Detection

The system should classify emails as:

```text
phishing
legitimate
```

It should return:

- confidence score
- risk level
- recommended action
- model name
- model version

### 3. Quarantine Workflow

High-risk emails should be moved to a safe review/quarantine state.

The product must not permanently delete emails.

### 4. Local Explanation

For each detected email, the system should explain why the email was classified that way.

Example:

```text
This email was classified as phishing mainly because the reply-to address does not match the sender, the sender domain appears suspicious, and the email contains an unusually long URL.
```

### 5. Global Explanation

The system should show model-level explanation using EBM and GAMI-Net surrogate outputs.

It should show:

- global feature importance
- feature effect plots
- interaction effects
- accuracy fidelity
- F1 fidelity
- error fidelity
- failure pattern summaries

### 6. Feedback Review

Users and analysts can flag wrong detections.

SOC analysts must confirm the true label before feedback can be used for future retraining.

### 7. Model Monitoring

The dashboard should show:

- current detector model
- current surrogate model
- model version
- detection metrics
- explanation metrics
- feedback case count
- improvement readiness

---

## Differentiation

The product is different from a normal phishing filter because it provides two explanation levels:

### Local Explanation

Answers:

```text
Why was this specific email classified as phishing?
```

### Global Explanation

Answers:

```text
What does the model generally rely on across many emails?
```

This makes the product more useful for SOC analysts, security managers, and model governance.

---

## Product Principles

1. Explanations must be practical for analysts.
2. Global explanation is a core feature, not an extra chart.
3. Feedback must be validated before it affects the model.
4. Quarantine must be reversible.
5. Model version and explanation snapshot must be preserved.
6. The system should support auditability.
7. The first MVP should use mock data before live mailbox APIs.
8. The interface should feel like a serious SOC dashboard.

---

## Long-Term Vision

The long-term product could become a full explainable email security assistant for organisations.

Future capabilities may include:

- Microsoft 365 integration
- Gmail integration
- live mailbox scanning
- automated quarantine workflow
- SOC analyst case management
- threat campaign clustering
- domain reputation enrichment
- model drift detection
- controlled improvement tracking
- model version comparison
- security governance reporting
