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
    # New prediction metadata columns introduced by model-management feature.
    required_prediction_columns = {
        "teacher_model_id": "TEXT",
        "surrogate_model_id": "TEXT",
        "feature_extractor_version": "TEXT",
        "explanation_snapshot": "JSON",
    }
    with engine.begin() as conn:
        table_exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
        ).fetchone()
        if not table_exists:
            return
        existing = conn.execute(text("PRAGMA table_info(predictions)")).fetchall()
        existing_cols = {row[1] for row in existing}
        for col, col_type in required_prediction_columns.items():
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE predictions ADD COLUMN {col} {col_type}"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
