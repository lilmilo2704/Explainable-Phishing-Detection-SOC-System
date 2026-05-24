from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Email(Base):
    __tablename__ = "emails"
    __table_args__ = (UniqueConstraint("mailbox_source", "mailbox_message_id", name="uq_mailbox_message"),)

    id = Column(String, primary_key=True, index=True) # e.g., email_001
    mailbox_source = Column(String, default="mock", nullable=False)
    mailbox_message_id = Column(String, index=True)
    subject = Column(String)
    sender = Column(String)
    sender_domain = Column(String)
    recipient = Column(String)
    reply_to = Column(String)
    received_at = Column(DateTime)
    body_preview = Column(Text)
    body = Column(Text, nullable=True)
    urls = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)
    feature_snapshot = Column(JSON, nullable=True)
    content_fingerprint = Column(String, nullable=True)
    url_count = Column(Integer, default=0)
    attachment_count = Column(Integer, default=0)
    has_links = Column(Boolean, default=False)
    has_attachment = Column(Boolean, default=False)
    quarantine_status = Column(String, default="allowed") # allowed, quarantined, released
    review_status = Column(String, default="none") # none, new, in_review, reviewed
    prediction_status = Column(String, default="not_scanned")
    model_error = Column(Text, nullable=True)
    last_scanned_at = Column(DateTime, nullable=True)

    # Relationships
    predictions = relationship("Prediction", back_populates="email")
    explanations = relationship("Explanation", back_populates="email")
    feedback = relationship("Feedback", back_populates="email")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, index=True) # pred_001
    email_id = Column(String, ForeignKey("emails.id"))
    prediction = Column(String) # phishing, legitimate
    confidence = Column(Float)
    risk_level = Column(String) # high, medium, low, critical
    recommended_action = Column(String) # quarantine, allow
    model_name = Column(String)
    model_version = Column(String)
    teacher_model_id = Column(String, nullable=True)
    surrogate_model_id = Column(String, nullable=True)
    feature_extractor_version = Column(String, nullable=True)
    explanation_snapshot = Column(JSON, nullable=True)
    explanation_version = Column(String, nullable=True)
    content_fingerprint = Column(String, nullable=True)
    is_latest = Column(Boolean, default=True, nullable=False)
    trusted_prediction = Column(Boolean, default=False, nullable=False)
    pipeline_status = Column(String, default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email = relationship("Email", back_populates="predictions")

class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(String, primary_key=True, index=True)
    email_id = Column(String, ForeignKey("emails.id"))
    prediction_id = Column(String, ForeignKey("predictions.id"))
    explainer_type = Column(String) # SHAP, LIME, EBM, etc.
    model_version = Column(String)
    human_summary = Column(Text)
    top_features = Column(JSON) # Store list of dicts: feature, value, contribution, direction, human_reason
    snapshot_id = Column(String, nullable=True)
    pipeline_status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email = relationship("Email", back_populates="explanations")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, index=True)
    email_id = Column(String, ForeignKey("emails.id"))
    prediction_id = Column(String, ForeignKey("predictions.id"), nullable=True)
    feedback_type = Column(String) # wrong_detection, false_positive, false_negative, true_positive, true_negative
    original_prediction = Column(String, nullable=True)
    original_confidence = Column(Float, nullable=True)
    user_feedback = Column(Text, nullable=True)
    analyst_label = Column(String, nullable=True)
    error_type = Column(String, nullable=True)
    reason_category = Column(String, nullable=True)
    review_status = Column(String, default="pending") # pending, confirmed, rejected
    added_to_improvement_dataset = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)
    comments = Column(Text)
    status = Column(String, default="pending") # pending, reviewed
    submitted_by = Column(String, nullable=True)
    feedback_source = Column(String, default="user")
    analyst_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email = relationship("Email", back_populates="feedback")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    version = Column(String)
    is_active = Column(Boolean, default=False)
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    email_id = Column(String, ForeignKey("emails.id"), nullable=True)
    actor = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    model_version = Column(String, nullable=True)
    explanation_version = Column(String, nullable=True)
    explanation_snapshot_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MailboxSyncRun(Base):
    __tablename__ = "mailbox_sync_runs"

    id = Column(String, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False)
    actor = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    scanned = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    quarantined = Column(Integer, default=0)
    failure_details = Column(JSON, nullable=True)
    last_error = Column(Text, nullable=True)
