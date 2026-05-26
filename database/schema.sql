CREATE TABLE IF NOT EXISTS emails (
  id TEXT PRIMARY KEY,
  mailbox_source TEXT NOT NULL DEFAULT 'mock',
  mailbox_message_id TEXT,
  subject TEXT,
  sender TEXT,
  sender_domain TEXT,
  recipient TEXT,
  reply_to TEXT,
  received_at DATETIME,
  body_preview TEXT,
  body TEXT,
  urls JSON,
  attachments JSON,
  feature_snapshot JSON,
  content_fingerprint TEXT,
  url_count INTEGER DEFAULT 0,
  attachment_count INTEGER DEFAULT 0,
  has_links BOOLEAN DEFAULT 0,
  has_attachment BOOLEAN DEFAULT 0,
  quarantine_status TEXT DEFAULT 'allowed',
  review_status TEXT DEFAULT 'none',
  prediction_status TEXT DEFAULT 'not_scanned',
  model_error TEXT,
  last_scanned_at DATETIME,
  UNIQUE(mailbox_source, mailbox_message_id)
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
  explanation_version TEXT,
  content_fingerprint TEXT,
  is_latest BOOLEAN DEFAULT 1,
  trusted_prediction BOOLEAN DEFAULT 0,
  pipeline_status TEXT DEFAULT 'unknown',
  created_at DATETIME,
  FOREIGN KEY(email_id) REFERENCES emails(id)
);

CREATE TABLE IF NOT EXISTS explanations (
  id TEXT PRIMARY KEY,
  snapshot_id TEXT,
  email_id TEXT,
  prediction_id TEXT,
  explainer_type TEXT,
  model_version TEXT,
  human_summary TEXT,
  top_features JSON,
  pipeline_status TEXT,
  created_at DATETIME,
  FOREIGN KEY(email_id) REFERENCES emails(id),
  FOREIGN KEY(prediction_id) REFERENCES predictions(id)
);

CREATE TABLE IF NOT EXISTS feedback (
  id TEXT PRIMARY KEY,
  email_id TEXT,
  prediction_id TEXT,
  explanation_snapshot_id TEXT,
  feedback_type TEXT,
  original_prediction TEXT,
  original_confidence REAL,
  user_feedback TEXT,
  submitted_by TEXT,
  feedback_source TEXT DEFAULT 'user',
  analyst_label TEXT,
  error_type TEXT,
  reason_category TEXT,
  review_status TEXT DEFAULT 'pending_review',
  added_to_improvement_dataset BOOLEAN DEFAULT 0,
  reviewed_at DATETIME,
  comments TEXT,
  status TEXT DEFAULT 'pending',
  analyst_id TEXT,
  created_at DATETIME,
  FOREIGN KEY(email_id) REFERENCES emails(id),
  FOREIGN KEY(prediction_id) REFERENCES predictions(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  email_id TEXT,
  actor TEXT NOT NULL,
  action_type TEXT NOT NULL,
  previous_state JSON,
  new_state JSON,
  reason TEXT,
  model_version TEXT,
  explanation_version TEXT,
  explanation_snapshot_id TEXT,
  created_at DATETIME NOT NULL,
  FOREIGN KEY(email_id) REFERENCES emails(id)
);

CREATE TABLE IF NOT EXISTS mailbox_sync_runs (
  id TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  status TEXT NOT NULL,
  actor TEXT,
  started_at DATETIME NOT NULL,
  completed_at DATETIME,
  scanned INTEGER DEFAULT 0,
  skipped INTEGER DEFAULT 0,
  failed INTEGER DEFAULT 0,
  quarantined INTEGER DEFAULT 0,
  failure_details JSON,
  last_error TEXT
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_latest_prediction_per_email
  ON predictions(email_id) WHERE is_latest = 1;
