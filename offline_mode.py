"""
offline_mode.py — Offline Mode Manager v1.0
─────────────────────────────────────────────
✅ Internet connectivity check
✅ Offline TTS (pyttsx3 fallback)
✅ Offline URL check (heuristic only)
✅ Offline indicator for UI
✅ Graceful degradation — सब features offline काम करें
"""

import socket
import os
import base64
import tempfile
import streamlit as st


# ══════════════════════════════════════════════════════════
#  CONNECTIVITY CHECK
# ══════════════════════════════════════════════════════════

def check_internet(host: str = "8.8.8.8", port: int = 53,
                   timeout: float = 2.0) -> bool:
    """
    Internet connection है? DNS query से check करें।
    Fast (2 sec timeout), no external dependency।
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.error, OSError):
        return False


def get_connectivity_status() -> dict:
    """
    Full connectivity status।
    Returns: {online, virustotal_ok, gtts_ok, ai_ok}
    """
    online = check_internet()
    return {
        "online":        online,
        "virustotal_ok": online and bool(os.getenv("VIRUSTOTAL_API_KEY")),
        "gtts_ok":       online,
        "ai_ok":         online and bool(os.getenv("ANTHROPIC_API_KEY")),
    }


# ══════════════════════════════════════════════════════════
#  OFFLINE TTS — pyttsx3 fallback
# ══════════════════════════════════════════════════════════

def speak_offline(text: str) -> bool:
    """
    pyttsx3 से offline TTS।
    Returns True if successful।
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # Hindi voice ढूंढें
        voices = engine.getProperty("voices")
        for voice in voices:
            if "hindi" in voice.name.lower() or "hi" in voice.id.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 150)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            engine.save_to_file(text, tmp.name)
            engine.runAndWait()
            tmp_path = tmp.name
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            with open(tmp_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.unlink(tmp_path)
            st.markdown(
                f'<audio autoplay><source src="data:audio/wav;base64,{b64}" '
                f'type="audio/wav"></audio>',
                unsafe_allow_html=True
            )
            return True
    except Exception:
        pass
    return False


def speak_with_fallback(text: str, prefer_online: bool = True):
    """
    Smart TTS — online हो तो gTTS, offline हो तो pyttsx3।
    """
    if prefer_online and check_internet():
        # gTTS (online)
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang="hi")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                path = tmp.name
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.unlink(path)
            st.markdown(
                f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" '
                f'type="audio/mp3"></audio>',
                unsafe_allow_html=True
            )
            return
        except Exception:
            pass

    # Offline fallback
    if not speak_offline(text):
        st.caption(f"🔇 आवाज़ उपलब्ध नहीं | {text[:60]}")


# ══════════════════════════════════════════════════════════
#  OFFLINE URL CHECK
# ══════════════════════════════════════════════════════════

def check_url_offline(url: str) -> dict:
    """
    Offline URL heuristic check (VirusTotal के बिना)।
    """
    from security_engine import check_url_heuristic
    result = check_url_heuristic(url)
    result["offline"] = True
    result["note"]    = "Offline mode — VirusTotal check नहीं हुआ"
    return result


# ══════════════════════════════════════════════════════════
#  UI COMPONENTS
# ══════════════════════════════════════════════════════════

OFFLINE_BANNER_HTML = """
<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;
            padding:8px 14px;margin:6px 0;display:flex;align-items:center;gap:10px">
    <span style="font-size:1.2rem">📵</span>
    <div>
        <div style="font-weight:700;color:#856404;font-size:0.88rem">
            Offline Mode — इंटरनेट नहीं
        </div>
        <div style="font-size:0.78rem;color:#856404">
            ✅ Fraud Scan | ✅ Scam DB | ✅ PDF Report |
            ⚠️ VirusTotal off | ⚠️ AI Chatbot off | ⚠️ gTTS off
        </div>
    </div>
</div>
"""

ONLINE_BANNER_HTML = """
<div style="background:#d4edda;border:1px solid #28a745;border-radius:8px;
            padding:6px 14px;margin:6px 0;display:flex;align-items:center;gap:8px">
    <span style="font-size:1rem">🌐</span>
    <span style="font-weight:600;color:#155724;font-size:0.82rem">
        Online — सभी features उपलब्ध
    </span>
</div>
"""


def render_connectivity_badge():
    """Sidebar में connection status badge।"""
    online = check_internet()
    if online:
        st.markdown(ONLINE_BANNER_HTML, unsafe_allow_html=True)
    else:
        st.markdown(OFFLINE_BANNER_HTML, unsafe_allow_html=True)
    return online


def render_offline_warning(feature: str):
    """
    किसी specific feature के offline होने पर warning।
    feature: 'virustotal' | 'gtts' | 'ai' | 'general'
    """
    messages = {
        "virustotal": "⚠️ **VirusTotal URL Check** offline है। Heuristic check से काम चलेगा।",
        "gtts":       "⚠️ **आवाज़** offline है। Text पढ़कर काम चलाएं।",
        "ai":         "⚠️ **AI Chatbot** offline है। इंटरनेट कनेक्ट करें।",
        "general":    "📵 **Offline Mode** — Basic fraud scan काम करता है।",
    }
    st.warning(messages.get(feature, messages["general"]))


# ══════════════════════════════════════════════════════════
#  OFFLINE-AWARE SCAN
# ══════════════════════════════════════════════════════════

def run_scan_with_offline_support(text: str, advanced: bool = False) -> dict:
    """
    Internet हो या न हो — scan हमेशा काम करे।
    """
    from security_engine import check_security, check_security_advanced, get_risk_level
    from scam_database   import check_patterns

    online = check_internet()

    if advanced:
        # Advanced mode — online features conditional
        vt_key = os.getenv("VIRUSTOTAL_API_KEY", "")
        result = check_security_advanced(
            text,
            check_urls_online=(online and bool(vt_key))
        )
    else:
        findings, score = check_security(text)
        level, emoji    = get_risk_level(score)
        result = {
            "findings":   findings,
            "raw_score":  score,
            "risk_level": level,
            "risk_emoji": emoji,
            "ml": {"probability": min(score * 12, 100), "verdict": level},
        }

    # Scam DB check (always offline-safe)
    result["db_matches"] = check_patterns(text)
    result["offline"]    = not online

    return result
