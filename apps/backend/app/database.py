from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy import text

# Create the absolute path to the database directory at the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_DIR = os.path.join(BASE_DIR, "database")

# Ensure the directory exists
os.makedirs(DB_DIR, exist_ok=True)

db_path = os.getenv("PHISHGUARD_DB_PATH", os.path.join(DB_DIR, "phishguard.db"))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_startup_migrations() -> None:
    """
    Lightweight in-place migrations for local SQLite compatibility.
    This keeps older DB files working when new optional columns are introduced.
    """
    # Import models so new tables are registered before create_all executes.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    required_prediction_columns = {
        "teacher_model_id": "TEXT",
        "surrogate_model_id": "TEXT",
        "feature_extractor_version": "TEXT",
        "explanation_snapshot": "JSON",
        "explanation_version": "TEXT",
        "content_fingerprint": "TEXT",
        "is_latest": "BOOLEAN DEFAULT 1",
        "trusted_prediction": "BOOLEAN DEFAULT 0",
        "pipeline_status": "TEXT DEFAULT 'unknown'",
    }
    required_email_columns = {
        "mailbox_source": "TEXT DEFAULT 'mock' NOT NULL",
        "body": "TEXT",
        "urls": "JSON",
        "attachments": "JSON",
        "feature_snapshot": "JSON",
        "content_fingerprint": "TEXT",
        "prediction_status": "TEXT DEFAULT 'not_scanned'",
        "model_error": "TEXT",
        "last_scanned_at": "DATETIME",
    }
    required_explanation_columns = {
        "snapshot_id": "TEXT",
        "pipeline_status": "TEXT",
    }
    required_feedback_columns = {
        "submitted_by": "TEXT",
        "feedback_source": "TEXT DEFAULT 'user'",
        "explanation_snapshot_id": "TEXT",
    }
    with engine.begin() as conn:
        for table, required_columns in (
            ("predictions", required_prediction_columns),
            ("emails", required_email_columns),
            ("explanations", required_explanation_columns),
            ("feedback", required_feedback_columns),
        ):
            existing = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            existing_cols = {row[1] for row in existing}
            for col, col_type in required_columns.items():
                if col not in existing_cols:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
        conn.execute(text("UPDATE emails SET mailbox_source = 'gmail' WHERE id LIKE 'gmail_%' AND mailbox_source = 'mock'"))
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_mailbox_message "
            "ON emails(mailbox_source, mailbox_message_id) WHERE mailbox_message_id IS NOT NULL"
        ))
        conn.execute(text("UPDATE predictions SET is_latest = 0"))
        conn.execute(
            text(
                "UPDATE predictions SET is_latest = 1 "
                "WHERE id IN ("
                "SELECT p.id FROM predictions p "
                "WHERE p.id = (SELECT p2.id FROM predictions p2 "
                "WHERE p2.email_id = p.email_id ORDER BY p2.created_at DESC, p2.id DESC LIMIT 1)"
                ")"
            )
        )
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_latest_prediction_per_email "
                "ON predictions(email_id) WHERE is_latest = 1"
            )
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
