from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class PredictionSchema(BaseModel):
    id: str
    email_id: str
    prediction: str
    confidence: float
    risk_level: str
    recommended_action: str
    model_name: str
    model_version: str
    teacher_model_id: Optional[str] = None
    surrogate_model_id: Optional[str] = None
    feature_extractor_version: Optional[str] = None
    explanation_snapshot: Optional[Dict[str, Any]] = None
    explanation_version: Optional[str] = None
    trusted_prediction: bool = False
    pipeline_status: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EmailSchema(BaseModel):
    id: str
    mailbox_message_id: Optional[str] = None
    mailbox_source: str = "mock"
    subject: Optional[str] = None
    sender: Optional[str] = None
    sender_domain: Optional[str] = None
    recipient: Optional[str] = None
    reply_to: Optional[str] = None
    received_at: Optional[datetime] = None
    body_preview: Optional[str] = None
    urls: Optional[List[str]] = None
    url_count: int = 0
    attachment_count: int = 0
    has_links: bool = False
    has_attachment: bool = False
    quarantine_status: str = "allowed"
    review_status: str = "none"
    prediction_status: Optional[str] = None
    model_error: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EmailListSchema(EmailSchema):
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None

class EmailDetailSchema(EmailSchema):
    prediction_details: Optional[PredictionSchema] = None

class ExplanationSchema(BaseModel):
    id: str
    snapshot_id: Optional[str] = None
    email_id: str
    prediction_id: str
    explainer_type: str
    model_version: str
    human_summary: Optional[str] = None
    top_features: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class FeedbackSchema(BaseModel):
    id: str
    email_id: str
    prediction_id: Optional[str] = None
    explanation_snapshot_id: Optional[str] = None
    feedback_type: Optional[str] = None
    original_prediction: Optional[str] = None
    original_confidence: Optional[float] = None
    user_feedback: Optional[str] = None
    analyst_label: Optional[str] = None
    error_type: Optional[str] = None
    reason_category: Optional[str] = None
    review_status: str = "pending"
    added_to_improvement_dataset: bool = False
    reviewed_at: Optional[datetime] = None
    comments: Optional[str] = None
    status: str = "pending"
    analyst_id: Optional[str] = None
    submitted_by: Optional[str] = None
    feedback_source: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackCreateSchema(BaseModel):
    feedback_type: str
    user_comment: Optional[str] = None
    submitted_by: Optional[str] = None


class FeedbackReviewSchema(BaseModel):
    analyst_label: Optional[str] = None
    error_type: Optional[str] = None
    reason_category: Optional[str] = None
    review_status: str = "confirmed"
    added_to_improvement_dataset: bool = False
    actor: str = "analyst"


class MailboxSyncRequestSchema(BaseModel):
    provider: Optional[str] = None
    limit: int = Field(default=25, ge=1, le=200)
    force_rescan: bool = False
    actor: str = "analyst"


class MailboxSyncItemSchema(BaseModel):
    email_id: str
    mailbox_message_id: Optional[str] = None
    prediction: str
    confidence: float
    risk_level: str
    recommended_action: str
    model_version: str
    trusted_prediction: bool = False
    pipeline_status: Optional[str] = None


class MailboxSyncResponseSchema(BaseModel):
    provider: str
    imported: int
    scanned: int
    skipped: int
    failed: int
    quarantined: int
    status: str
    last_sync_time: Optional[datetime] = None
    failures: List[Dict[str, Any]] = Field(default_factory=list)
    items: List[MailboxSyncItemSchema]


class ActiveModelConfigRequestSchema(BaseModel):
    teacher_model_id: str
    surrogate_model_id: str
    actor: str = "analyst"


class MailboxActionSchema(BaseModel):
    provider: Optional[str] = None
    actor: str = "analyst"
    reason: Optional[str] = None
