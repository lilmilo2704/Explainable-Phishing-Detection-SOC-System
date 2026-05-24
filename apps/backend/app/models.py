from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True) # e.g., email_001
    mailbox_message_id = Column(String, index=True)
    subject = Column(String)
    sender = Column(String)
    sender_domain = Column(String)
    recipient = Column(String)
    reply_to = Column(String)
    received_at = Column(DateTime)
    body_preview = Column(Text)
    url_count = Column(Integer, default=0)
    attachment_count = Column(Integer, default=0)
    has_links = Column(Boolean, default=False)
    has_attachment = Column(Boolean, default=False)
    quarantine_status = Column(String, default="allowed") # allowed, quarantined, released
    review_status = Column(String, default="none") # none, new, in_review, reviewed

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
    analyst_id = Column(String)
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
