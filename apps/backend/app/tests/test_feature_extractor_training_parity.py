from app.main import app  # noqa: F401 - registers the ml_service import alias used below
from services.ml_service.feature_engineering.feature_extractor import extract_raw_features


def test_passthrough_features_follow_original_dataset_builder_rules():
    features = extract_raw_features(
        {
            "body": "Important: reset password now at https://example.com",
            "sender": "secure-update9@example.com",
            "reply_to": "help@other.example",
            "urls": ["https://example.com", "https://example.com"],
            "attachments": ["invoice.zip"],
        }
    )

    assert features["num_links"] == 1
    assert features["has_links"] == 1
    assert features["has_urgent_words"] == 1
    assert features["sender_replyto_mismatch"] == 1
    assert features["suspicious_sender_domain"] == 1
    assert features["num_attachments"] == 0
    assert features["has_attachment"] == 0
    assert features["suspicious_attachment_type"] == 0
    assert features["attachment_has_macro_or_archive"] == 1
