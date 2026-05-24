"""
Feature extraction for a single email dict.
Mirrors the logic from the training pipeline reference file exactly,
so that the pre-trained models receive the same feature space.
"""

import re
from urllib.parse import urlparse

# ── constants ──────────────────────────────────────────────────────────────────
COMMON_MULTI_PART_SUFFIXES = {
    "ac.uk", "co.jp", "co.nz", "co.uk", "com.au", "com.br", "com.cn",
    "com.mx", "com.sg", "com.tr", "gov.au", "gov.uk", "net.au", "org.au", "org.uk",
}
FREE_EMAIL_PROVIDERS = {
    "163.com", "aol.com", "gmail.com", "googlemail.com", "hotmail.com",
    "icloud.com", "mail.com", "outlook.com", "proton.me", "protonmail.com",
    "qq.com", "yahoo.com", "yahoo.com.au", "ymail.com",
}
SHORTENER_DOMAINS = {
    "bit.ly", "buff.ly", "cutt.ly", "goo.gl", "is.gd", "ow.ly", "rb.gy",
    "rebrand.ly", "shorturl.at", "t.co", "tinyurl.com",
}

URGENT_PATTERN = re.compile(
    r"\b(urgent|immediately|asap|verify|verification|suspend|action required|payment|overdue|invoice)\b",
    flags=re.IGNORECASE,
)
ACTION_PATTERN = re.compile(
    r"\b(click here|log in|login|sign in|signin|confirm|update|review|open attachment|reset)\b",
    flags=re.IGNORECASE,
)
EMAIL_ADDRESS_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SUSPICIOUS_URL_TOKEN_PATTERN = re.compile(
    r"(login|verify|update|secure|account|password|invoice|payment|bank|confirm|signin|webscr)",
    flags=re.IGNORECASE,
)
IPV4_PATTERN = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")


# ── helpers ────────────────────────────────────────────────────────────────────
def _safe_urlparse(url: str):
    try:
        return urlparse(url)
    except Exception:
        return None


def _parsed_has_port(parsed) -> bool:
    try:
        return parsed.port is not None
    except Exception:
        return False


def _normalize_domain(value: str) -> str:
    value = str(value or "").strip().lower().strip(".")
    value = value.strip("[]")
    return value or "unknown"


def _extract_domain_from_email(value: str) -> str:
    match = re.search(r"@([^>\s]+)", str(value or ""))
    return _normalize_domain(match.group(1)) if match else "unknown"


def _extract_localpart_from_email(value: str) -> str:
    match = re.search(r"([^@\s<]+)@", str(value or ""))
    return match.group(1).strip().lower() if match else "unknown"


def _extract_tld_from_domain(domain: str) -> str:
    domain = _normalize_domain(domain)
    if domain == "unknown":
        return "none"
    if IPV4_PATTERN.fullmatch(domain):
        return ".ip"
    if "." not in domain:
        return "none"
    return "." + domain.split(".")[-1]


def _extract_registered_domain(hostname: str) -> str:
    hostname = _normalize_domain(hostname)
    if hostname == "unknown" or "." not in hostname:
        return hostname
    if IPV4_PATTERN.fullmatch(hostname):
        return hostname
    parts = [part for part in hostname.split(".") if part]
    if len(parts) < 2:
        return hostname
    two_part_suffix = ".".join(parts[-2:])
    if len(parts) >= 3 and two_part_suffix in COMMON_MULTI_PART_SUFFIXES:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _extract_primary_scheme(urls: list) -> str:
    for url in urls:
        parsed = _safe_urlparse(url)
        if parsed is None:
            continue
        scheme = (parsed.scheme or "").strip().lower()
        if scheme:
            return scheme
    return "none"


def _extract_primary_tld(urls: list) -> str:
    for url in urls:
        parsed = _safe_urlparse(url)
        if parsed is None:
            continue
        hostname = _normalize_domain(parsed.hostname or "")
        if hostname != "unknown" and "." in hostname:
            return _extract_tld_from_domain(hostname)
    return "none"


def _build_url_features(urls: list) -> dict:
    parsed_urls = [p for p in (_safe_urlparse(u) for u in urls) if p is not None]
    hosts = [_normalize_domain(p.hostname or "") for p in parsed_urls
             if _normalize_domain(p.hostname or "") != "unknown"]
    registered_domains = [_extract_registered_domain(h) for h in hosts]
    schemes = [(p.scheme or "").strip().lower() for p in parsed_urls if (p.scheme or "").strip()]

    max_url_len = max((len(u) for u in urls), default=0)
    mean_url_len = (sum(len(u) for u in urls) / len(urls)) if urls else 0.0
    dot_counts = [h.count(".") for h in hosts]
    subdomain_depths = [max(h.count(".") - 1, 0) for h in hosts]
    path_depths = [len([part for part in (p.path or "").split("/") if part]) for p in parsed_urls]

    return {
        "url_scheme": _extract_primary_scheme(urls),
        "url_tld": _extract_primary_tld(urls),
        "primary_url_registered_domain": registered_domains[0] if registered_domains else "none",
        "url_count_parsed": len(urls),
        "distinct_url_domain_count": len(set(hosts)),
        "distinct_url_registered_domain_count": len(set(registered_domains)),
        "url_https_count": sum(s == "https" for s in schemes),
        "url_http_count": sum(s == "http" for s in schemes),
        "url_other_scheme_count": sum(s not in {"http", "https"} for s in schemes),
        "url_has_ip_host": int(any(IPV4_PATTERN.fullmatch(h) for h in hosts)),
        "url_shortener_count": sum(h in SHORTENER_DOMAINS for h in hosts),
        "url_hyphen_host_count": sum("-" in h for h in hosts),
        "url_at_symbol_count": sum("@" in u for u in urls),
        "url_query_count": sum(bool(p.query) for p in parsed_urls),
        "url_fragment_count": sum(bool(p.fragment) for p in parsed_urls),
        "url_port_count": sum(_parsed_has_port(p) for p in parsed_urls),
        "url_percent_encoded_count": sum(u.count("%") for u in urls),
        "url_suspicious_token_count": sum(len(SUSPICIOUS_URL_TOKEN_PATTERN.findall(u)) for u in urls),
        "url_digit_char_count": sum(sum(c.isdigit() for c in u) for u in urls),
        "max_url_len": max_url_len,
        "mean_url_len": mean_url_len,
        "max_url_dot_count": max(dot_counts, default=0),
        "primary_url_subdomain_depth": max(subdomain_depths, default=0),
        "max_url_path_depth": max(path_depths, default=0),
        "has_long_url": int(max_url_len >= 60),
    }


def _build_attachment_features(attachments: list) -> dict:
    lowered = [a.lower() for a in attachments]
    sus_ext = re.compile(r"\.(zip|rar|7z|exe|js|scr|iso|img|hta|lnk|docm|xlsm|pptm)$")
    return {
        "attachment_count_parsed": len(attachments),
        "attachment_has_macro_or_archive": int(any(sus_ext.search(n) for n in lowered)),
    }


# ── public API ─────────────────────────────────────────────────────────────────
def extract_raw_features(email: dict) -> dict:
    """
    Convert a raw email dict into a flat dict of raw (unprocessed) features.

    Expected email keys:
        subject, body, sender_email, reply_to,
        urls (list[str]), attachments (list[str]),
        has_links (int/bool), has_attachment (int/bool),
        num_links (int), num_attachments (int),
        has_urgent_words (int/bool),
        sender_replyto_mismatch (int/bool),
        suspicious_sender_domain (int/bool),
        suspicious_attachment_type (int/bool)

    Missing keys default to safe zero/empty values.
    """
    subject = str(email.get("subject") or "")
    body = str(email.get("body") or "")
    sender_email = str(email.get("sender_email") or email.get("sender") or "")
    reply_to = str(email.get("reply_to") or "")
    urls: list = email.get("urls") or []
    attachments: list = email.get("attachments") or []

    sender_domain = _extract_domain_from_email(sender_email)
    replyto_domain = _extract_domain_from_email(reply_to)
    sender_localpart = _extract_localpart_from_email(sender_email)

    url_feats = _build_url_features(urls)
    att_feats = _build_attachment_features(attachments)

    raw = {
        # text features
        "subject_len": len(subject),
        "body_len": len(body),
        "subject_word_count": len(subject.split()),
        "body_word_count": len(body.split()),
        "subject_exclamation_count": subject.count("!"),
        "body_exclamation_count": body.count("!"),
        "subject_question_count": subject.count("?"),
        "body_question_count": body.count("?"),
        "subject_digit_count": sum(c.isdigit() for c in subject),
        "body_digit_count": sum(c.isdigit() for c in body),
        "subject_upper_ratio": sum(c.isupper() for c in subject) / max(len(subject), 1),
        "body_upper_ratio": sum(c.isupper() for c in body) / max(len(body), 1),
        "money_symbol_count": len(re.findall(r"[$€£]", body)),
        "subject_urgent_word_count": len(URGENT_PATTERN.findall(subject)),
        "body_urgent_word_count": len(URGENT_PATTERN.findall(body)),
        "body_action_word_count": len(ACTION_PATTERN.findall(body)),
        "click_here_count": len(re.findall(r"click here", body, re.IGNORECASE)),
        "body_email_address_count": len(EMAIL_ADDRESS_PATTERN.findall(body)),
        "http_count_body": len(re.findall(r"https?://", body, re.IGNORECASE)),
        # sender features
        "sender_domain": sender_domain,
        "replyto_domain": replyto_domain,
        "sender_tld": _extract_tld_from_domain(sender_domain),
        "replyto_tld": _extract_tld_from_domain(replyto_domain),
        "sender_missing": int(sender_domain == "unknown"),
        "reply_missing": int(replyto_domain == "unknown"),
        "sender_reply_domain_same": int(
            sender_domain != "unknown"
            and replyto_domain != "unknown"
            and sender_domain == replyto_domain
        ),
        "sender_reply_domain_mismatch": int(
            replyto_domain != "unknown" and sender_domain != replyto_domain
        ),
        "sender_domain_has_digit": int(bool(re.search(r"\d", sender_domain))),
        "sender_local_has_digit": int(bool(re.search(r"\d", sender_localpart))),
        "sender_is_free_provider": int(sender_domain in FREE_EMAIL_PROVIDERS),
        "sender_domain_len": len(sender_domain),
        "replyto_domain_len": len(replyto_domain),
        # passthrough / pre-computed flags
        "num_links": int(email.get("num_links") or email.get("url_count") or 0),
        "has_links": int(bool(email.get("has_links"))),
        "num_attachments": int(email.get("num_attachments") or email.get("attachment_count") or 0),
        "has_attachment": int(bool(email.get("has_attachment"))),
        "has_urgent_words": int(bool(email.get("has_urgent_words"))),
        "sender_replyto_mismatch": int(bool(email.get("sender_replyto_mismatch"))),
        "suspicious_sender_domain": int(bool(email.get("suspicious_sender_domain"))),
        "suspicious_attachment_type": int(bool(email.get("suspicious_attachment_type"))),
    }

    raw.update(url_feats)
    raw.update(att_feats)
    return raw
