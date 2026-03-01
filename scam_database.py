"""
scam_database.py — Scam Database Loader v1.0
─────────────────────────────────────────────
Bihar Police + TRAI + MHA reported scams की local database।
security_engine.py और WhatsApp bot — दोनों यही use करते हैं।
"""

import json
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "scam_database.json")

# Cache — once loaded
_DB = None


def load_db() -> dict:
    global _DB
    if _DB is None:
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                _DB = json.load(f)
        except Exception:
            _DB = {"scam_phones": [], "scam_urls": [],
                   "scam_patterns": [], "safe_domains": [],
                   "tips": {}, "helplines": {}}
    return _DB


def check_phone_in_db(phone: str) -> dict | None:
    """Phone number database में है? Return entry or None।"""
    db = load_db()
    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    for entry in db.get("scam_phones", []):
        db_num = re.sub(r'[\s\-\(\)\+X]', '', entry["number"])
        # Exact match या prefix match (XXXXXX वाले)
        if db_num == phone_clean:
            return entry
        # Prefix match — e.g. "9304" matches "9304123456"
        if len(db_num) <= 6 and phone_clean.startswith(db_num):
            return entry
    return None


def check_url_in_db(url: str) -> dict | None:
    """URL database में है? Return entry or None।"""
    db = load_db()
    url_lower = url.lower()
    for entry in db.get("scam_urls", []):
        if entry["url"].lower() in url_lower:
            return entry
    return None


def is_safe_domain(url: str) -> bool:
    """URL safe domain list में है?"""
    db = load_db()
    url_lower = url.lower()
    for domain in db.get("safe_domains", []):
        if domain in url_lower:
            return True
    return False


def check_patterns(text: str, lang: str = "hi") -> list:
    """
    Text में known scam patterns match करें।
    Returns list of matching pattern entries।
    """
    db = load_db()
    text_lower = text.lower()
    matches = []
    for pattern_entry in db.get("scam_patterns", []):
        # Language filter
        entry_langs = pattern_entry.get("lang", ["hi"])
        if lang not in entry_langs and "hi" not in entry_langs:
            continue
        # Pattern match
        for pattern in pattern_entry.get("patterns", []):
            if pattern.lower() in text_lower:
                matches.append({
                    "id":      pattern_entry["id"],
                    "name":    pattern_entry["name"],
                    "risk":    pattern_entry["risk"],
                    "matched": pattern,
                    "advice":  pattern_entry.get(f"advice_{lang}",
                               pattern_entry.get("advice_hi", "")),
                })
                break  # एक entry से एक ही match काफी
    return matches


def get_tip(lang: str = "hi") -> str:
    """Random tip उस भाषा में।"""
    import random
    db = load_db()
    tips = db.get("tips", {}).get(lang) or db.get("tips", {}).get("hi", [])
    return random.choice(tips) if tips else "🔐 OTP कभी किसी को न दें।"


def get_helpline(lang: str = "hi") -> str:
    """Helpline text उस भाषा में।"""
    db = load_db()
    helplines = db.get("helplines", {})
    return helplines.get(lang) or helplines.get("hi", "📞 1930")


def get_db_stats() -> dict:
    """Database statistics।"""
    db = load_db()
    return {
        "phones":   len(db.get("scam_phones", [])),
        "urls":     len(db.get("scam_urls", [])),
        "patterns": len(db.get("scam_patterns", [])),
        "updated":  db.get("_meta", {}).get("updated", "Unknown"),
        "version":  db.get("_meta", {}).get("version", "1.0"),
    }
