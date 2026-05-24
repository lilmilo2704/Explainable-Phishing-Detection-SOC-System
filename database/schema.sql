CREATE TABLE IF NOT EXISTS emails (
  id TEXT PRIMARY KEY,
  mailbox_message_id TEXT,
  subject TEXT,
  sender TEXT,
  sender_domain TEXT,
  recipient TEXT,
  reply_to TEXT,
  received_at DATETIME,
  body_preview TEXT,
  url_count INTEGER DEFAULT 0,
  attachment_count INTEGER DEFAULT 0,
  has_links BOOLEAN DEFAULT 0,
  has_attachment BOOLEAN DEFAULT 0,
  quarantine_status TEXT DEFAULT 'allowed',
  review_status TEXT DEFAULT 'none'
);

CREATE TABLE IF NOT EXISTS predictions (
  id TEXT PRIMARY KEY,
  email_id TEXT,
  prediction TEXT,
  confidence REAL,
  risk_level TEXT,
  recommended_action TEXT,
  model_name TEXT,
  model_version TEXT,
  teacher_model_id TEXT,
  surrogate_model_id TEXT,
  feature_extractor_version TEXT,
  explanation_snapshot JSON,
  created_at DATETIME,
  FOREIGN KEY(email_id) REFERENCES emails(id)
);

CREATE TABLE IF NOT EXISTS explanations (
  id TEXT PRIMARY KEY,
  email_id TEXT,
  prediction_id TEXT,
  explainer_type TEXT,
  model_version TEXT,
  human_summary TEXT,
  top_features JSON,
  created_at DATETIME,
  FOREIGN KEY(email_id) REFERENCES emails(id),
  FOREIGN KEY(prediction_id) REFERENCES predictions(id)
);

CREATE TABLE IF NOT EXISTS feedback (
  id TEXT PRIMARY KEY,
  email_id TEXT,
  prediction_id TEXT,
  feedback_type TEXT,
  original_prediction TEXT,
  original_confidence REAL,
  user_feedback TEXT,
  analyst_label TEXT,
  error_type TEXT,
  reason_category TEXT,
  review_status TEXT DEFAULT 'pending',
  added_to_improvement_dataset BOOLEAN DEFAULT 0,
  reviewed_at DATETIME,
  comments TEXT,
  status TEXT DEFAULT 'pending',
  analyst_id TEXT,
  created_at DATETIME,
  FOREIGN KEY(email_id) REFERENCES emails(id),
  FOREIGN KEY(prediction_id) REFERENCES predictions(id)
);

CREATE TABLE IF NOT EXISTS model_versions (
  id TEXT PRIMARY KEY,
  name TEXT,
  version TEXT,
  is_active BOOLEAN DEFAULT 0,
  accuracy REAL,
  f1_score REAL,
  created_at DATETIME
);
