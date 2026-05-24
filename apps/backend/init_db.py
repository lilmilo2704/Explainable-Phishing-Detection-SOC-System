import json
import os
from datetime import datetime
from app.database import engine, Base, SessionLocal
from app.models import Email, Prediction, Explanation, Feedback

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "sample")

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def init_db():
    print("Creating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Load Emails
        print("Loading emails...")
        emails_data = load_json("sample_emails.json")
        for ed in emails_data:
            email = Email(
                id=ed.get("id"),
                mailbox_message_id=ed.get("mailbox_message_id"),
                subject=ed.get("subject"),
                sender=ed.get("sender"),
                sender_domain=ed.get("sender_domain"),
                recipient=ed.get("recipient"),
                reply_to=ed.get("reply_to"),
                received_at=parse_datetime(ed.get("received_at")),
                body_preview=ed.get("body_preview"),
                url_count=ed.get("url_count"),
                attachment_count=ed.get("attachment_count"),
                has_links=ed.get("has_links"),
                has_attachment=ed.get("has_attachment"),
                quarantine_status=ed.get("quarantine_status"),
                review_status=ed.get("review_status")
            )
            db.add(email)
        
        # Load Predictions
        print("Loading predictions...")
        predictions_data = load_json("sample_predictions.json")
        for pd in predictions_data:
            prediction = Prediction(
                id=pd.get("id"),
                email_id=pd.get("email_id"),
                prediction=pd.get("prediction"),
                confidence=pd.get("confidence"),
                risk_level=pd.get("risk_level"),
                recommended_action=pd.get("recommended_action"),
                model_name=pd.get("model_name"),
                model_version=pd.get("model_version"),
                created_at=parse_datetime(pd.get("created_at"))
            )
            db.add(prediction)

        # Load Local Explanations
        print("Loading explanations...")
        explanations_data = load_json("sample_local_explanations.json")
        for exd in explanations_data:
            explanation = Explanation(
                id=exd.get("id"),
                email_id=exd.get("email_id"),
                prediction_id=exd.get("prediction_id"),
                explainer_type=exd.get("explainer_type"),
                model_version=exd.get("model_version"),
                human_summary=exd.get("human_summary"),
                top_features=exd.get("top_features"), # dicts automatically encoded to JSON by SQLAlchemy
                created_at=parse_datetime(exd.get("created_at"))
            )
            db.add(explanation)

        # Load Feedback
        print("Loading feedback...")
        feedback_data = load_json("sample_feedback_cases.json")
        for fb in feedback_data:
            feedback = Feedback(
                id=fb.get("id"),
                email_id=fb.get("email_id"),
                prediction_id=fb.get("prediction_id"),
                feedback_type=fb.get("feedback_type"),
                original_prediction=fb.get("original_prediction"),
                original_confidence=fb.get("original_confidence"),
                user_feedback=fb.get("user_feedback"),
                analyst_label=fb.get("analyst_label"),
                error_type=fb.get("error_type"),
                reason_category=fb.get("reason_category"),
                review_status=fb.get("review_status", "pending"),
                added_to_improvement_dataset=fb.get("added_to_improvement_dataset", False),
                reviewed_at=parse_datetime(fb.get("reviewed_at")),
                comments=fb.get("comments"),
                status=fb.get("status"),
                analyst_id=fb.get("analyst_id"),
                created_at=parse_datetime(fb.get("created_at"))
            )
            db.add(feedback)

        db.commit()
        print("Database initialized and seeded successfully.")
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
