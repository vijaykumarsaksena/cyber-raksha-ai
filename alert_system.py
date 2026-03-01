"""
alert_system.py
─────────────────────────────────────────────────────────
Cyber-Raksha Alert System
जब कोई खतरनाक मैसेज आए → Admin को Email + SMS तुरंत मिले।

Email  : Gmail SMTP (मुफ्त)
SMS    : Fast2SMS API (भारतीय, मुफ्त tier उपलब्ध)

.env में जोड़ें:
    ALERT_EMAIL        = admin@gmail.com
    ALERT_EMAIL_PASS   = your_app_password   ← Gmail App Password
    ALERT_PHONE        = 9XXXXXXXXX          ← Admin का नंबर
    FAST2SMS_API_KEY   = xxxxxxxxxxxx         ← fast2sms.com से
    ALERT_MIN_SCORE    = 3                   ← कितने score पर alert?
"""

import os
import smtplib
import threading
import urllib.request
import urllib.parse
import json
from email.mime.text        import MIMEText
from email.mime.multipart   import MIMEMultipart
from datetime               import datetime
from dotenv                 import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────
ALERT_EMAIL       = os.getenv("ALERT_EMAIL", "")
ALERT_EMAIL_PASS  = os.getenv("ALERT_EMAIL_PASS", "")
ALERT_PHONE       = os.getenv("ALERT_PHONE", "")
FAST2SMS_KEY      = os.getenv("FAST2SMS_API_KEY", "")
ALERT_MIN_SCORE   = int(os.getenv("ALERT_MIN_SCORE", "3"))

# Alert deduplication — DB में store होगा, restart पर भी काम करेगा
def _already_alerted(uid: str) -> bool:
    """क्या यह alert पहले भेजा जा चुका है?"""
    try:
        import sqlite3, os
        db = os.path.join(os.path.dirname(__file__), "cyber_raksha.db")
        conn = sqlite3.connect(db, check_same_thread=False)
        conn.execute("""CREATE TABLE IF NOT EXISTS alert_log (
            uid TEXT PRIMARY KEY, created_at TEXT)""")
        row = conn.execute("SELECT uid FROM alert_log WHERE uid=?", (uid,)).fetchone()
        if row:
            conn.close(); return True
        conn.execute("INSERT INTO alert_log (uid, created_at) VALUES (?,?)",
                     (uid, datetime.now().isoformat()))
        conn.commit(); conn.close()
        return False
    except Exception:
        return False  # DB error पर alert जाने दें


# ══════════════════════════════════════════════════════
#  EMAIL ALERT
# ══════════════════════════════════════════════════════
def send_email_alert(subject: str, body_html: str) -> bool:
    """Gmail SMTP से Email भेजें।"""
    if not ALERT_EMAIL or not ALERT_EMAIL_PASS:
        print("⚠️  Email credentials नहीं हैं — .env चेक करें।")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Cyber-Raksha Alert <{ALERT_EMAIL}>"
        msg["To"]      = ALERT_EMAIL
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(ALERT_EMAIL, ALERT_EMAIL_PASS)
            server.sendmail(ALERT_EMAIL, ALERT_EMAIL, msg.as_string())

        print(f"✅ Email alert भेजा: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


# ══════════════════════════════════════════════════════
#  SMS ALERT (Fast2SMS)
# ══════════════════════════════════════════════════════
def send_sms_alert(message: str) -> bool:
    """Fast2SMS API से SMS भेजें।"""
    if not FAST2SMS_KEY or not ALERT_PHONE:
        print("⚠️  SMS credentials नहीं हैं।")
        return False
    try:
        # SMS 160 chars तक सीमित रखें
        sms_text = message[:155] + "…" if len(message) > 155 else message
        payload  = urllib.parse.urlencode({
            "route":    "q",         # Quick SMS route
            "message":  sms_text,
            "numbers":  ALERT_PHONE,
        }).encode()

        req = urllib.request.Request(
            "https://www.fast2sms.com/dev/bulkV2",
            data=payload,
            headers={
                "authorization": FAST2SMS_KEY,
                "Content-Type":  "application/x-www-form-urlencoded",
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("return"):
                print(f"✅ SMS alert भेजा: {ALERT_PHONE}")
                return True
            else:
                print(f"❌ SMS fail: {result}")
                return False
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False


# ══════════════════════════════════════════════════════
#  HTML Email Template
# ══════════════════════════════════════════════════════
def _build_email_html(alert_type: str, details: dict) -> str:
    color   = "#c0392b" if alert_type == "complaint" else "#e67e22"
    emoji   = "🚨" if alert_type == "complaint" else "⚠️"
    heading = "नई उच्च-जोखिम शिकायत!" if alert_type == "complaint" else "खतरनाक स्कैन!"

    rows = "".join(
        f"<tr><td style='padding:6px 12px;font-weight:bold;color:#555'>{k}</td>"
        f"<td style='padding:6px 12px'>{v}</td></tr>"
        for k, v in details.items()
    )

    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px">
      <div style="max-width:560px;margin:auto;background:#fff;border-radius:8px;
                  border-top:5px solid {color};padding:24px">
        <h2 style="color:{color};margin-top:0">{emoji} {heading}</h2>
        <table style="width:100%;border-collapse:collapse;font-size:14px">{rows}</table>
        <hr style="margin:20px 0;border:none;border-top:1px solid #eee">
        <p style="font-size:12px;color:#999;text-align:center">
          Cyber-Raksha AI | KDSP बिहार<br>
          साइबर हेल्पलाइन: <strong>1930</strong>
        </p>
      </div>
    </body></html>
    """


# ══════════════════════════════════════════════════════
#  मुख्य ALERT फंक्शन
# ══════════════════════════════════════════════════════
def trigger_alert(
    alert_type : str,   # "complaint" या "scan"
    score      : int,
    name       : str  = "",
    phone      : str  = "",
    message    : str  = "",
    complaint_id: int = None,
    source     : str  = "streamlit",
):
    """
    score >= ALERT_MIN_SCORE होने पर Email + SMS दोनों भेजें।
    Background thread में चलता है ताकि UI slow न हो।
    """
    if score < ALERT_MIN_SCORE:
        return  # score कम है — alert नहीं

    # Duplicate check — DB में देखें
    uid = f"{alert_type}_{complaint_id or hash(message[:50])}"
    if _already_alerted(uid):
        return

    # Alert details
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    if alert_type == "complaint":
        details = {
            "🆔 शिकायत ID":  f"CR-{complaint_id:04d}" if complaint_id else "—",
            "👤 नाम":        name or "—",
            "📱 मोबाइल":     phone or "—",
            "🔍 अलर्ट स्कोर": str(score),
            "📡 स्रोत":      source,
            "🕐 समय":        now,
            "📝 विवरण":      (message[:200] + "…") if len(message) > 200 else message,
        }
        subject  = f"🚨 [CR-{complaint_id:04d}] उच्च-जोखिम शिकायत — Score {score}"
        sms_text = (f"CYBER-RAKSHA ALERT! शिकायत CR-{complaint_id:04d} | "
                    f"स्कोर:{score} | {name} {phone} | {now}")
    else:
        details = {
            "🔍 अलर्ट स्कोर": str(score),
            "📡 स्रोत":       source,
            "🕐 समय":         now,
            "📝 मैसेज (आंशिक)": (message[:200] + "…") if len(message) > 200 else message,
        }
        subject  = f"⚠️ खतरनाक स्कैन — Score {score} ({source})"
        sms_text = f"CYBER-RAKSHA: खतरनाक स्कैन! स्कोर:{score} | स्रोत:{source} | {now}"

    html = _build_email_html(alert_type, details)

    # Background thread — UI block नहीं होगा
    def _send():
        send_email_alert(subject, html)
        send_sms_alert(sms_text)

    threading.Thread(target=_send, daemon=True).start()
    print(f"📤 Alert triggered: {subject}")


# ══════════════════════════════════════════════════════
#  Alert Settings — DB में save/load
# ══════════════════════════════════════════════════════
def get_alert_settings() -> dict:
    """वर्तमान alert settings लौटाएं।"""
    return {
        "email":     ALERT_EMAIL,
        "phone":     ALERT_PHONE,
        "min_score": ALERT_MIN_SCORE,
        "email_ok":  bool(ALERT_EMAIL and ALERT_EMAIL_PASS),
        "sms_ok":    bool(FAST2SMS_KEY and ALERT_PHONE),
    }


def test_alert() -> dict:
    """Test alert भेजकर देखें कि सेटअप सही है।"""
    results = {}
    test_html = _build_email_html("scan", {
        "🧪 यह": "Test Alert है",
        "✅ Status": "Cyber-Raksha सही से configured है!",
        "🕐 समय": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    results["email"] = send_email_alert("🧪 Cyber-Raksha Test Alert", test_html)
    results["sms"]   = send_sms_alert("CYBER-RAKSHA TEST: Alert system सही काम कर रहा है!")
    return results
