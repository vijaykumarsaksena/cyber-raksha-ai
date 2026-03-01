"""
database.py
─────────────────────────────────────────────
Cyber-Raksha का SQLite Database Manager
सभी शिकायतें, स्कैन लॉग और Admin यहाँ सेव होते हैं।
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cyber_raksha.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """पहली बार चलाने पर Tables बनाएं।"""
    conn = get_conn()
    cur  = conn.cursor()

    # शिकायत Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            description TEXT    NOT NULL,
            alert_count INTEGER DEFAULT 0,
            district    TEXT    DEFAULT '',   -- Bihar district
            source      TEXT    DEFAULT 'streamlit',
            created_at  TEXT    NOT NULL
        )
    """)

    # Migration — पुरानी DB में district column जोड़ें अगर नहीं है
    try:
        cur.execute("ALTER TABLE complaints ADD COLUMN district TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass  # Column पहले से है

    # स्कैन लॉग Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            message     TEXT    NOT NULL,
            alert_count INTEGER DEFAULT 0,
            risk_level  TEXT    DEFAULT 'सुरक्षित',
            source      TEXT    DEFAULT 'streamlit',
            created_at  TEXT    NOT NULL
        )
    """)

    # Admin Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL
        )
    """)

    conn.commit()

    # Default Admin बनाएं (अगर कोई नहीं है)
    cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        _create_admin(cur, "kdsp_admin", "Raksha@2025")
        conn.commit()
        print("✅ Default Admin बना: username=kdsp_admin | password=Raksha@2025")
        print("⚠️  Login के बाद पासवर्ड जरूर बदलें!")

    conn.close()


# ── Password ───────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _create_admin(cur, username: str, password: str):
    cur.execute(
        "INSERT INTO admins (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, _hash(password), datetime.now().isoformat())
    )


# ── Admin Auth ─────────────────────────────────────────
def verify_admin(username: str, password: str) -> bool:
    conn = get_conn()
    row  = conn.execute(
        "SELECT password_hash FROM admins WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return False
    return row["password_hash"] == _hash(password)


def change_password(username: str, new_password: str) -> bool:
    conn = get_conn()
    conn.execute(
        "UPDATE admins SET password_hash = ? WHERE username = ?",
        (_hash(new_password), username)
    )
    conn.commit()
    conn.close()
    return True


# ── शिकायत ─────────────────────────────────────────────
def save_complaint(name: str, phone: str, description: str,
                   alert_count: int, source: str = "streamlit",
                   district: str = "") -> int:
    conn = get_conn()
    cur  = conn.execute(
        """INSERT INTO complaints (name, phone, description, alert_count, district, source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, phone, description, alert_count, district, source, datetime.now().isoformat())
    )
    complaint_id = cur.lastrowid
    conn.commit()
    conn.close()
    return complaint_id


def get_all_complaints(limit: int = 100) -> list:
    conn  = get_conn()
    rows  = conn.execute(
        "SELECT * FROM complaints ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_complaint_stats() -> dict:
    conn = get_conn()
    total    = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    high_risk= conn.execute("SELECT COUNT(*) FROM complaints WHERE alert_count >= 4").fetchone()[0]
    today    = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE date(created_at) = date('now')"
    ).fetchone()[0]
    conn.close()
    return {"total": total, "high_risk": high_risk, "today": today}


# ── स्कैन लॉग ──────────────────────────────────────────
def save_scan(message: str, alert_count: int,
              risk_level: str, source: str = "streamlit"):
    # संवेदनशील डेटा: पूरा message नहीं, सिर्फ MD5 hash और पहले 60 chars
    import hashlib
    preview = message[:60].replace("\n", " ") + ("…" if len(message) > 60 else "")
    msg_hash = hashlib.md5(message.encode()).hexdigest()
    conn = get_conn()
    conn.execute(
        """INSERT INTO scan_logs (message, alert_count, risk_level, source, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (f"[{msg_hash[:8]}] {preview}", alert_count, risk_level, source, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_scan_stats() -> dict:
    conn  = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM scan_logs").fetchone()[0]
    safe  = conn.execute(
        "SELECT COUNT(*) FROM scan_logs WHERE alert_count = 0"
    ).fetchone()[0]
    danger= conn.execute(
        "SELECT COUNT(*) FROM scan_logs WHERE alert_count >= 4"
    ).fetchone()[0]
    conn.close()
    return {"total": total, "safe": safe, "danger": danger}


# ── Charts के लिए Data ────────────────────────────────────
def get_daily_complaints(days: int = 7) -> list:
    """पिछले N दिनों की शिकायतें — bar chart के लिए।"""
    conn = get_conn()
    rows = conn.execute("""
        SELECT date(created_at) as day, COUNT(*) as count
        FROM complaints
        WHERE created_at >= date('now', ? || ' days')
        GROUP BY day ORDER BY day ASC
    """, (f"-{days}",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_source_breakdown() -> dict:
    """App vs WhatsApp शिकायतें।"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT source, COUNT(*) as count FROM complaints GROUP BY source"
    ).fetchall()
    conn.close()
    return {r["source"]: r["count"] for r in rows}


def get_risk_distribution() -> dict:
    """Risk level distribution।"""
    conn = get_conn()
    buckets = {
        "सुरक्षित (0)":        conn.execute("SELECT COUNT(*) FROM complaints WHERE alert_count = 0").fetchone()[0],
        "संदिग्ध (1-3)":       conn.execute("SELECT COUNT(*) FROM complaints WHERE alert_count BETWEEN 1 AND 3").fetchone()[0],
        "खतरनाक (4-5)":        conn.execute("SELECT COUNT(*) FROM complaints WHERE alert_count BETWEEN 4 AND 5").fetchone()[0],
        "अत्यंत खतरनाक (6+)": conn.execute("SELECT COUNT(*) FROM complaints WHERE alert_count >= 6").fetchone()[0],
    }
    conn.close()
    return buckets


def get_daily_scans(days: int = 7) -> list:
    """पिछले N दिनों के स्कैन।"""
    conn = get_conn()
    rows = conn.execute("""
        SELECT date(created_at) as day, COUNT(*) as count
        FROM scan_logs
        WHERE created_at >= date('now', ? || ' days')
        GROUP BY day ORDER BY day ASC
    """, (f"-{days}",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# DB शुरू करें
init_db()

# ── Feedback ────────────────────────────────────────────

def save_feedback(vote: str, message: str = "", risk_level: str = "",
                  comment: str = "", scan_id: int = None,
                  source: str = "streamlit") -> int:
    """
    User feedback save करें।
    vote: 'correct' | 'wrong' | 'unsure'
    """
    conn = get_conn()
    # Feedback table create करें अगर नहीं है
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id    INTEGER,
            vote       TEXT    NOT NULL,
            message    TEXT,
            risk_level TEXT,
            comment    TEXT,
            source     TEXT    DEFAULT 'streamlit',
            created_at TEXT    NOT NULL
        )
    """)
    cur = conn.execute(
        """INSERT INTO feedback (scan_id, vote, message, risk_level, comment, source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (scan_id, vote, message[:500], risk_level, comment[:300],
         source, datetime.now().isoformat())
    )
    fid = cur.lastrowid
    conn.commit()
    conn.close()
    return fid


def get_feedback_stats() -> dict:
    """Feedback statistics।"""
    conn = get_conn()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, vote TEXT, created_at TEXT)")
        total    = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        correct  = conn.execute("SELECT COUNT(*) FROM feedback WHERE vote='correct'").fetchone()[0]
        wrong    = conn.execute("SELECT COUNT(*) FROM feedback WHERE vote='wrong'").fetchone()[0]
        unsure   = conn.execute("SELECT COUNT(*) FROM feedback WHERE vote='unsure'").fetchone()[0]
        accuracy = round(correct / total * 100, 1) if total > 0 else 0
    except Exception:
        total = correct = wrong = unsure = 0
        accuracy = 0
    conn.close()
    return {
        "total":    total,
        "correct":  correct,
        "wrong":    wrong,
        "unsure":   unsure,
        "accuracy": accuracy,
    }


def get_recent_feedback(limit: int = 20) -> list:
    """Recent feedback entries।"""
    conn = get_conn()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, vote TEXT, risk_level TEXT, comment TEXT, created_at TEXT)")
        rows = conn.execute(
            """SELECT id, vote, risk_level, comment, created_at
               FROM feedback ORDER BY created_at DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    except Exception:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


def get_district_distribution() -> dict:
    """District-wise complaint count — real data।"""
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT district, COUNT(*) as count
               FROM complaints
               WHERE district != '' AND district IS NOT NULL
               GROUP BY district
               ORDER BY count DESC"""
        ).fetchall()
    except Exception:
        rows = []
    conn.close()
    return {r["district"]: r["count"] for r in rows}
