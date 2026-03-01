"""
cyber_raksha_app.py  (पूरा अपडेट)
✅ हिंदी PDF — फॉन्ट अपने आप डाउनलोड
✅ SQLite Database — शिकायतें हमेशा सुरक्षित
✅ Admin Login — पासवर्ड से सुरक्षित
✅ Analytics Dashboard
"""

import streamlit as st
import re, json, os, tempfile, base64
import numpy as np
import pandas as pd
from PIL import Image
from datetime import datetime
# Heavy imports — lazy loaded for fast startup
# easyocr → load_ocr()
# gTTS → speak_with_fallback()
# anthropic → AI chatbot tab only

from font_setup      import HINDI_FONT_AVAILABLE, FONT_PATH
from fpdf            import FPDF
from database        import (verify_admin, change_password,
                             save_complaint, get_all_complaints, get_complaint_stats,
                             save_scan, get_scan_stats,
                             get_daily_complaints, get_daily_scans,
                             get_source_breakdown, get_risk_distribution,
                             save_feedback, get_feedback_stats, get_recent_feedback)
from security_engine import (check_security, get_risk_level,
                              check_security_advanced, detect_image_tampering,
                              check_url_heuristic, check_phone_reputation)
from alert_system    import trigger_alert, get_alert_settings, test_alert
from voice_assistant import (speak_simple, speak_advanced,
                              render_speech_to_text, render_voice_query,
                              render_voice_panel, text_to_speech)
from translations    import (t, LANGUAGES, get_language_selector_label,
                              get_all_fraud_keywords, get_gtts_lang, get_speech_lang)
from admin_dashboard import render_admin_dashboard
from offline_mode    import (render_connectivity_badge, render_offline_warning,
                              run_scan_with_offline_support, check_internet,
                              speak_with_fallback)

st.set_page_config(
    page_title="Cyber-Raksha AI",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://cybercrime.gov.in",
        "Report a bug": None,
        "About": "🛡️ Cyber-Raksha AI Pro v3.6 | KDSP Bihar | 📞 1930",
    }
)

MOBILE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans', sans-serif !important; }

/* ── Header ─────────────────────────────────────── */
.cr-header {
    background: linear-gradient(135deg,#1e3c78 0%,#2a5298 100%);
    color:white; padding:20px 16px 14px; border-radius:16px;
    text-align:center; margin-bottom:16px;
    box-shadow:0 4px 20px rgba(30,60,120,0.25);
}
.cr-header h1 { font-size:1.5rem; margin:0 0 4px; font-weight:700; letter-spacing:-0.3px; }
.cr-header p  { font-size:0.8rem; margin:0; opacity:0.85; }

/* ── Cards ──────────────────────────────────────── */
.cr-card {
    border-radius:12px; padding:12px 16px; margin:6px 0;
    font-size:0.88rem; line-height:1.55;
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
.cr-danger  { background:#fff5f5; border-left:4px solid #e74c3c; }
.cr-warning { background:#fffbf0; border-left:4px solid #f39c12; }
.cr-safe    { background:#f0fff4; border-left:4px solid #27ae60; }
.cr-info    { background:#edf5ff; border-left:4px solid #2980b9; }

/* ── Buttons ─────────────────────────────────────── */
.stButton > button {
    border-radius:10px !important; font-size:0.95rem !important;
    font-weight:600 !important; padding:11px 18px !important;
    width:100% !important;
    transition:all 0.15s ease !important;
    border:none !important;
}
.stButton > button:hover  { transform:translateY(-1px) !important; box-shadow:0 4px 12px rgba(0,0,0,0.15) !important; }
.stButton > button:active { transform:scale(0.97) !important; }
div[data-testid="stButton"] > button[kind="primary"] {
    background:linear-gradient(135deg,#1e3c78,#2a5298) !important;
    color:white !important;
}

/* ── Tabs ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap:3px; background:#f0f2f6; border-radius:12px;
    padding:4px; overflow-x:auto; flex-wrap:nowrap;
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px !important; font-size:0.78rem !important;
    padding:7px 9px !important; font-weight:600 !important;
    white-space:nowrap !important; flex-shrink:0 !important;
}
.stTabs [aria-selected="true"] {
    background:white !important;
    box-shadow:0 2px 8px rgba(0,0,0,0.12) !important;
    color:#1e3c78 !important;
}

/* ── Inputs ──────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    border-radius:10px !important; font-size:0.95rem !important;
    padding:10px 12px !important; border:1.5px solid #dde1e7 !important;
    transition:border-color 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color:#2a5298 !important;
    box-shadow:0 0 0 3px rgba(42,82,152,0.12) !important;
    outline:none !important;
}

/* ── Radio ───────────────────────────────────────── */
.stRadio > div { gap:6px !important; }
.stRadio label {
    border:1.5px solid #e0e4ea; border-radius:10px;
    padding:8px 14px !important; cursor:pointer;
    transition:all 0.15s; font-size:0.9rem !important;
}
.stRadio label:hover { border-color:#2a5298; background:#f0f4ff; }

/* ── Metrics ─────────────────────────────────────── */
[data-testid="metric-container"] {
    background:white; border-radius:12px; padding:14px !important;
    box-shadow:0 2px 10px rgba(0,0,0,0.07); text-align:center;
    border:1px solid #f0f2f6;
}
[data-testid="metric-container"] > div { justify-content:center !important; }

/* ── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#f8faff 0%,#eef2ff 100%) !important;
}
[data-testid="stSidebar"] .block-container { padding-top:1rem !important; }

/* ── Expander ────────────────────────────────────── */
.streamlit-expanderHeader {
    border-radius:10px !important; font-weight:600 !important;
    font-size:0.9rem !important;
}

/* ── Helpline badge ──────────────────────────────── */
.helpline-badge {
    display:inline-block; background:#e74c3c; color:white;
    font-weight:700; font-size:1.1rem; padding:6px 20px;
    border-radius:20px; letter-spacing:1px; margin:4px 0;
    box-shadow:0 2px 8px rgba(231,76,60,0.35);
}

/* ── Footer ──────────────────────────────────────── */
.cr-footer {
    text-align:center; font-size:0.76rem; color:#999;
    margin-top:24px; padding:16px; border-top:1px solid #eef0f4;
}

/* ── Scrollbar ───────────────────────────────────── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#f1f1f1; }
::-webkit-scrollbar-thumb { background:#bdc3c7; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#95a5a6; }

/* ── Mobile responsive ───────────────────────────── */
@media (max-width:768px) {
    .cr-header h1 { font-size:1.15rem; }
    .cr-header p  { font-size:0.72rem; }
    .stTabs [data-baseweb="tab"] { font-size:0.68rem !important; padding:6px 7px !important; }
    .stButton > button { font-size:0.88rem !important; padding:9px !important; }
    .cr-card { font-size:0.83rem !important; padding:10px 13px !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
    [data-testid="column"] { min-width:48% !important; }
    [data-testid="metric-container"] { padding:10px !important; }
}
@media (max-width:480px) {
    .cr-header { padding:14px 12px 10px; border-radius:12px; }
    .cr-header h1 { font-size:1rem; }
    [data-testid="column"] { min-width:100% !important; }
    .stTabs [data-baseweb="tab"] { font-size:0.62rem !important; padding:5px 5px !important; }
}
</style>
"""

# ── OCR — lazy load (startup slow नहीं होगा) ───────────
@st.cache_resource(show_spinner=False)
def load_ocr():
    import easyocr
    return easyocr.Reader(['hi', 'en'], gpu=False)

# ── Quiz ───────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_quiz():
    try:
        with open(os.path.join(os.path.dirname(__file__), "quiz_questions.json"), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"question":"बैंक OTP मांगे तो?","options":["दे देंगे","नहीं देंगे"],
                 "answer":"नहीं देंगे","explanation":"बैंक कभी OTP नहीं मांगता।","category":"OTP फ्रॉड"}]

@st.cache_data(ttl=300)
def cached_scan(text: str) -> tuple:
    """Same text को बार-बार scan न करें।"""
    from security_engine import check_security
    return check_security(text)

QUIZ = load_quiz()

# ── Voice ──────────────────────────────────────────────
def speak(text: str):
    """Smart TTS — online हो तो gTTS, offline हो तो fallback।"""
    speak_with_fallback(text)

# ── PDF ────────────────────────────────────────────────
class CyberPDF(FPDF):
    def __init__(self):
        super().__init__()
        self._h = False
        if HINDI_FONT_AVAILABLE:
            self.add_font("Noto","",FONT_PATH,uni=True); self._h = True
    def _f(self, bold=False, size=11):
        self.set_font("Noto" if self._h else "Arial","B" if (bold and not self._h) else "",size)
    def header(self):
        self._f(True,14); self.set_fill_color(30,60,120); self.set_text_color(255,255,255)
        self.cell(0,12,"साइबर-रक्षा जाँच रिपोर्ट" if self._h else "CYBER-RAKSHA REPORT",ln=True,align="C",fill=True)
        self.set_text_color(0,0,0); self.ln(4)
    def footer(self):
        self.set_y(-15); self._f(size=8); self.set_text_color(120,120,120)
        self.cell(0,10,f"साइबर हेल्पलाइन: 1930  |  पृष्ठ {self.page_no()}" if self._h
                  else f"Cyber Helpline: 1930  |  Page {self.page_no()}",align="C")

def _s(t,h): return t if h else t.encode("latin-1",errors="replace").decode("latin-1")

def create_pdf(name,phone,message,findings,cid=None):
    pdf=CyberPDF(); pdf.add_page(); h=pdf._h
    pdf._f(size=11); pdf.set_fill_color(240,240,240)
    pdf.cell(0,8,_s(f"दिनांक: {datetime.now().strftime('%d/%m/%Y %H:%M')}",h),ln=True,fill=True)
    if cid: pdf.cell(0,8,_s(f"शिकायत ID: CR-{cid:04d}",h),ln=True,fill=True)
    pdf.cell(0,8,_s(f"नाम: {name}  |  मोबाइल: {phone}",h),ln=True,fill=True); pdf.ln(4)
    pdf._f(True,11); pdf.cell(0,8,_s("विवरण:",h),ln=True)
    pdf._f(size=10); pdf.set_fill_color(255,245,245); pdf.multi_cell(0,7,_s(message,h),fill=True); pdf.ln(4)
    pdf._f(True,11); pdf.set_text_color(200,0,0)
    pdf.cell(0,8,_s(f"संदिग्ध संकेत: {len(findings)}",h),ln=True); pdf.set_text_color(0,0,0); pdf._f(size=10)
    for _,txt in findings: pdf.cell(0,7,_s(f"  • {re.sub(r'[*`]','',txt)}",h),ln=True)
    if not findings:
        pdf.set_text_color(0,150,0); pdf.cell(0,8,_s("कोई बड़ा खतरा नहीं मिला।",h),ln=True); pdf.set_text_color(0,0,0)
    pdf.ln(6); pdf._f(size=9); pdf.set_text_color(80,80,80)
    pdf.multi_cell(0,6,_s("अगले कदम: 1) 1930 पर कॉल करें  2) cybercrime.gov.in पर रिपोर्ट करें  3) नजदीकी थाने जाएं",h))
    raw=pdf.output(dest="S"); return raw if isinstance(raw,bytes) else raw.encode("latin-1")

# ══════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════
def show_login():
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="cr-header">
        <h1>🛡️ साइबर-रक्षा</h1>
        <p>Cyber-Raksha AI | KDSP बिहार</p>
    </div>""", unsafe_allow_html=True)

    with st.form("lf"):
        u = st.text_input("👤 Username", placeholder="kdsp_admin")
        p = st.text_input("🔒 Password", type="password", placeholder="••••••••")
        if st.form_submit_button("🔐 Login करें", use_container_width=True):
            if verify_admin(u, p):
                st.session_state.update({"logged_in":True,"username":u})
                st.rerun()
            else:
                st.error("❌ गलत Username या Password!")
    st.markdown("""
    <div class="cr-footer">
        पहली बार login करने पर KDSP Admin से संपर्क करें।<br>
        साइबर हेल्पलाइन: <span class="helpline-badge">1930</span>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════
def show_app():
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    # ── Language selector (session state) ──────────
    if "lang" not in st.session_state:
        st.session_state["lang"] = "hi"
    lang = st.session_state["lang"]

    with st.sidebar:
        st.markdown(f"👤 **{st.session_state['username']}**")
        if st.button(t("logout", lang), use_container_width=True):
            st.session_state.clear(); st.rerun()

        st.divider()
        # 🌐 Connectivity Status
        render_connectivity_badge()
        st.divider()

        # 🌐 Language Selector
        st.write("**🌐 भाषा / Language**")
        lang_options = list(LANGUAGES.keys())
        lang_labels  = [get_language_selector_label(l) for l in lang_options]
        selected_idx = lang_options.index(lang)
        new_idx = st.selectbox(
            "भाषा चुनें:", range(len(lang_labels)),
            index=selected_idx,
            format_func=lambda i: lang_labels[i],
            label_visibility="collapsed"
        )
        if lang_options[new_idx] != lang:
            st.session_state["lang"] = lang_options[new_idx]
            st.session_state.pop("greeted", None)
            st.rerun()

        st.divider()
        st.caption(f"{'✅ हिंदी PDF' if HINDI_FONT_AVAILABLE else '⚠️ अंग्रेज़ी PDF'}")
        st.caption("DB: cyber_raksha.db ✅")
        st.divider()
        st.write("**🔔 Alert Status**")
        cfg = get_alert_settings()
        st.caption(f"Email: {'✅' if cfg['email_ok'] else '❌'}")
        st.caption(f"SMS:   {'✅' if cfg['sms_ok']   else '❌'}")
        st.caption(f"Min Score: {cfg['min_score']}")
        if st.button("🧪 Test Alert", use_container_width=True):
            with st.spinner("भेज रहे हैं..."):
                results = test_alert()
            if results.get("email"): st.success("✅ Email पहुँचा!")
            else:                    st.error("❌ Email नहीं पहुँचा")
            if results.get("sms"):   st.success("✅ SMS पहुँचा!")
            else:                    st.warning("⚠️ SMS नहीं पहुँचा")
        st.divider()
        st.write("**🔑 पासवर्ड**")
        with st.form("pf"):
            p1 = st.text_input("नया पासवर्ड", type="password")
            p2 = st.text_input("दोबारा", type="password")
            if st.form_submit_button("बदलें"):
                if len(p1) < 8: st.error("कम से कम 8 अक्षर!")
                elif p1 != p2:  st.error("मेल नहीं खाते!")
                else: change_password(st.session_state["username"],p1); st.success("✅ बदल गया!")

    # ── Mobile Header ──────────────────────────────
    st.markdown(f"""
    <div class="cr-header">
        <h1>{t('app_title', lang)}</h1>
        <p>{t('tagline', lang)}</p>
    </div>""", unsafe_allow_html=True)

    if "greeted" not in st.session_state:
        speak(f"{t('welcome', lang)}! {t('tagline', lang)}")
        st.session_state["greeted"] = True

    tabs = st.tabs([
        t("tab_scan", lang), t("tab_report", lang), t("tab_quiz", lang),
        t("tab_analytics", lang), t("tab_ai", lang),
        "📄 Bulk Upload", "🔐 Admin"
    ])

    # ── TAB 1: स्कैन (Advanced Fraud Detection) ───────
    with tabs[0]:
        st.write(f"### {t('scan_title', lang)}")

        # Voice Assistant Panel
        render_voice_panel(
            show_stt=True, show_speed=True,
            key_prefix="scan", label=""
        )
        st.markdown("---")

        # Mode selector
        scan_col1, scan_col2 = st.columns([2,1])
        with scan_col1:
            mode = st.radio("माध्यम:", [t("scan_mode_text",lang), t("scan_mode_img",lang)], horizontal=True)
        with scan_col2:
            advanced_mode = st.toggle(t("advanced_mode",lang), value=False,
                                       help="ML Score + URL/Phone deep analysis")

        user_input = ""
        uploaded_img_path = None

        if mode == t("scan_mode_text", lang):
            user_input = st.text_area(t("scan_placeholder", lang), height=150)
        else:
            up = st.file_uploader("स्क्रीनशॉट", type=["jpg","png","jpeg"])
            if up:
                img = Image.open(up)
                st.image(img, width=320)
                # Save temp file for tampering analysis
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                    img.save(tf.name)
                    uploaded_img_path = tf.name
                with st.spinner("AI पढ़ रहा है..."):
                    with st.spinner("🔍 Image से text extract हो रहा है..."):
                        reader = load_ocr()
                        user_input = " ".join(reader.readtext(np.array(img), detail=0))
                st.info(f"**OCR टेक्स्ट:** {user_input[:200]}...")

                # Advanced: Image tampering check
                if advanced_mode and uploaded_img_path:
                    with st.spinner("🔬 Image analysis हो रही है..."):
                        ela = detect_image_tampering(uploaded_img_path)
                    if ela.get("tampered"):
                        st.markdown(
                            f'<div class="cr-card cr-danger">🖼️ <b>Image Tampering Detected!</b> '
                            f'Confidence: {ela["confidence"]}%<br>'
                            + "<br>".join(f"• {f}" for f in ela["flags"][:3]) +
                            f'<br><small>ELA Score: {ela["ela_score"]} | Size: {ela["size"]}</small></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="cr-card cr-safe">🖼️ Image authentic दिखती है '
                            f'(ELA: {ela.get("ela_score",0)}) '
                            + (f'| EXIF: ✅' if ela.get("has_exif") else '| EXIF: ❌') +
                            '</div>',
                            unsafe_allow_html=True
                        )

        if st.button(t("scan_btn", lang), use_container_width=True):
            if user_input.strip():
                if advanced_mode:
                    # ── ADVANCED ANALYSIS (offline-aware) ──
                    online = check_internet()
                    if not online:
                        render_offline_warning("virustotal")
                    with st.spinner("🔬 Advanced Analysis हो रही है..."):
                        vt_key = os.getenv("VIRUSTOTAL_API_KEY","")
                        result = check_security_advanced(
                            user_input,
                            check_urls_online=(online and bool(vt_key))
                        )
                    findings = result["findings"]
                    score    = result["raw_score"]
                    level    = result["risk_level"]
                    emoji_r  = result["risk_emoji"]
                    ml       = result["ml"]

                    save_scan(user_input, score, level, "streamlit")

                    # ML Verdict banner
                    prob = ml["probability"]
                    color = "#e74c3c" if prob>=65 else "#e67e22" if prob>=40 else "#27ae60"
                    st.markdown(f"""
                    <div style="background:{color};color:white;padding:14px 16px;
                    border-radius:10px;margin:8px 0">
                        <b>{emoji_r} {level}</b> &nbsp;|&nbsp;
                        🤖 ML Fraud Probability: <b>{prob}%</b><br>
                        <small>{ml['verdict']}</small>
                    </div>""", unsafe_allow_html=True)

                    # URL Results
                    if result["url_results"]:
                        st.write("**🔗 URL Analysis:**")
                        for i, ur in enumerate(result["url_results"]):
                            flags_txt = "; ".join(ur.get("flags",ur.get("error",[""])[:1]))[:80]
                            if not ur.get("safe"):
                                st.markdown(
                                    f'<div class="cr-card cr-danger">🚨 URL {i+1}: '
                                    f'{flags_txt}</div>',
                                    unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    f'<div class="cr-card cr-safe">✅ URL {i+1}: Safe</div>',
                                    unsafe_allow_html=True)

                    # Phone Reputation
                    if result["phone_results"]:
                        st.write("**📞 Phone Reputation:**")
                        for pr in result["phone_results"]:
                            if pr.get("is_scam"):
                                st.markdown(
                                    f'<div class="cr-card cr-danger">🚨 {pr["phone"]}: '
                                    f'{"; ".join(pr["flags"][:2])}</div>',
                                    unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    f'<div class="cr-card cr-safe">✅ {pr["phone"]}: Normal</div>',
                                    unsafe_allow_html=True)

                    # Bank SMS
                    br = result["bank_result"]
                    if br.get("bank"):
                        st.write("**🏦 Bank SMS Analysis:**")
                        if br.get("is_fake"):
                            st.markdown(
                                f'<div class="cr-card cr-danger">🚨 Fake {br["bank"]} SMS! '
                                f'{"; ".join(br["flags"][:2])}</div>',
                                unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f'<div class="cr-card cr-safe">✅ {br["bank"]} SMS — '
                                f'Suspicious pattern नहीं मिला</div>',
                                unsafe_allow_html=True)

                    # ML Breakdown
                    with st.expander("📊 ML Score Breakdown"):
                        bd = ml["breakdown"]
                        if bd:
                            bd_df = pd.DataFrame({
                                "Feature": list(bd.keys()),
                                "Score":   list(bd.values()),
                            })
                            st.bar_chart(bd_df.set_index("Feature")["Score"],
                                         color="#e74c3c")
                        if ml["evidence"]:
                            for ev in ml["evidence"]:
                                st.caption(f"• {ev}")
                        st.caption(f"Raw Total: {ml['raw_total']} → Probability: {prob}%")

                    # All findings
                    if findings:
                        with st.expander(f"🔍 सभी {len(findings)} Findings देखें"):
                            for _, txt in findings:
                                clean = re.sub(r'[*`]','',txt)
                                st.markdown(f'<div class="cr-card cr-warning">⚠️ {clean}</div>',
                                            unsafe_allow_html=True)

                    speak(f"सावधान! ML score {prob} percent fraud probability है।")
                    trigger_alert("scan", score, message=user_input, source="streamlit")

                else:
                    # ── STANDARD ANALYSIS ──────────────────
                    findings, score = check_security(user_input)
                    level, emoji_r  = get_risk_level(score)
                    save_scan(user_input, score, level, "streamlit")
                    if score > 0:
                        st.markdown(f"""
                        <div class="cr-card cr-danger">
                            <strong>{emoji_r} {level}!</strong> — {score} संदिग्ध संकेत मिले।
                        </div>""", unsafe_allow_html=True)
                        for _, txt in findings:
                            clean = re.sub(r'[*`]','',txt)
                            st.markdown(f'<div class="cr-card cr-warning">⚠️ {clean}</div>',
                                        unsafe_allow_html=True)
                        speak(f"सावधान! {score} संदिग्ध चीजें मिली हैं।")
                        trigger_alert("scan", score, message=user_input, source="streamlit")
                    else:
                        st.markdown(f"""
                        <div class="cr-card cr-safe">
                            {t('scan_safe', lang)}
                        </div>""", unsafe_allow_html=True)
                        speak(t('scan_safe', lang))

                # ── FEEDBACK WIDGET ─────────────────────
                st.markdown("---")
                fb_labels = {
                    "hi":  ("क्या यह जाँच सही थी?", "✅ हाँ, सही", "❌ नहीं, गलत", "🤔 पक्का नहीं"),
                    "bho": ("का ई जांच सही रहल?",   "✅ हाँ",       "❌ नाहीं",     "🤔 पता नइखे"),
                    "mai": ("की ई जाँच सही छल?",     "✅ हँ",        "❌ नहि",        "🤔 पक्का नहि"),
                    "ur":  ("کیا یہ جانچ صحیح تھی؟","✅ ہاں",       "❌ نہیں",       "🤔 یقین نہیں"),
                    "mag": ("का ई जाँच सही रहल?",   "✅ हाँ",       "❌ नञ",         "🤔 पक्का नञ"),
                    "en":  ("Was this scan accurate?","✅ Yes",       "❌ No",         "🤔 Unsure"),
                }.get(lang, ("क्या यह जाँच सही थी?","✅ हाँ, सही","❌ नहीं, गलत","🤔 पक्का नहीं"))

                st.caption(f"**{fb_labels[0]}**")
                fb_col1, fb_col2, fb_col3 = st.columns(3)
                fb_key = f"fb_{hash(user_input[:50])}"

                if fb_col1.button(fb_labels[1], key=f"{fb_key}_yes", use_container_width=True):
                    save_feedback("correct", user_input[:300], level if 'level' in dir() else "", source="streamlit")
                    st.success("👍 धन्यवाद!" if lang=="hi" else "👍 Thanks!")
                if fb_col2.button(fb_labels[2], key=f"{fb_key}_no", use_container_width=True):
                    save_feedback("wrong", user_input[:300], level if 'level' in dir() else "", source="streamlit")
                    st.info("📝 जानकारी के लिए शुक्रिया!" if lang=="hi" else "📝 Thanks for the feedback!")
                if fb_col3.button(fb_labels[3], key=f"{fb_key}_ns", use_container_width=True):
                    save_feedback("unsure", user_input[:300], level if 'level' in dir() else "", source="streamlit")
                    st.info("🤔 ठीक है!" if lang=="hi" else "🤔 OK!")
            else:
                st.warning(t("no_input", lang))

    # ── TAB 2: रिपोर्ट ────────────────────────────────
    with tabs[1]:
        st.write(f"### {t('report_title', lang)}")
        c1, c2 = st.columns(2)
        name  = c1.text_input(t("name_label", lang))
        phone = c2.text_input(t("phone_label", lang))

        # District dropdown
        from admin_dashboard import BIHAR_DISTRICTS
        district_label = {
            "hi": "📍 जिला चुनें *", "bho": "📍 जिला चुनीं *",
            "mai": "📍 जिला चुनू *",  "ur":  "📍 ضلع منتخب کریں *",
            "mag": "📍 जिला चुनो *",  "en":  "📍 Select District *",
        }.get(lang, "📍 जिला चुनें *")

        district_options = ["— जिला चुनें —"] + sorted(BIHAR_DISTRICTS)
        district = st.selectbox(district_label, district_options)
        if district == "— जिला चुनें —":
            district = ""

        msg = st.text_area(t("msg_label", lang), height=120)

        if st.button(t("pdf_btn", lang), use_container_width=True):
            if name.strip() and msg.strip():
                findings, score = check_security(msg)
                cid = save_complaint(
                    name.strip(), phone.strip(), msg.strip(),
                    score, "streamlit", district
                )
                pdf = create_pdf(name.strip(), phone.strip(), msg.strip(), findings, cid)
                dist_info = f" | 📍 {district}" if district else ""
                st.success(f"✅ {t('complaint_filed', lang)} **CR-{cid:04d}**{dist_info}")
                trigger_alert("complaint", score,
                              name=name.strip(), phone=phone.strip(),
                              message=msg.strip(), complaint_id=cid, source="streamlit")
                sn = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip())
                st.download_button(t("download_pdf", lang), pdf,
                                   f"{sn}_CR{cid:04d}.pdf",
                                   "application/pdf", use_container_width=True)
            else:
                st.warning(t("no_input", lang))

    # ── TAB 3: क्विज़ ──────────────────────────────────
    with tabs[2]:
        st.write("### 🎮 साइबर जागरूकता क्विज़")
        if "quiz_done" not in st.session_state: st.session_state["quiz_done"] = False
        if not st.session_state["quiz_done"]:
            with st.form("qf"):
                for i,q in enumerate(QUIZ):
                    st.markdown(f"**Q{i+1}. {q['question']}** `{q.get('category','')}`")
                    st.radio("",q["options"],key=f"q_{i}",label_visibility="collapsed")
                    st.divider()
                if st.form_submit_button("📊 रिजल्ट", use_container_width=True):
                    st.session_state["quiz_done"] = True; st.rerun()
        else:
            score = 0
            for i,q in enumerate(QUIZ):
                ok = st.session_state.get(f"q_{i}") == q["answer"]
                if ok: score += 1; st.success(f"✅ Q{i+1}: सही! — {q['explanation']}")
                else:  st.error(f"❌ Q{i+1}: गलत। सही: _{q['answer']}_ — {q['explanation']}")
            st.divider()
            pct = int(score/len(QUIZ)*100)
            c1,c2 = st.columns(2)
            c1.metric("स्कोर",f"{score}/{len(QUIZ)}"); c2.metric("प्रतिशत",f"{pct}%")
            if pct==100: st.balloons(); speak("बधाई हो! आप माहिर हैं।")
            elif pct>=60: speak("ठीक है, और सीखें।")
            else: speak("सावधान! और जानकारी लें।")
            if st.button("🔄 फिर खेलें", use_container_width=True):
                st.session_state["quiz_done"] = False
                [st.session_state.pop(f"q_{i}",None) for i in range(len(QUIZ))]
                st.rerun()

    # ── TAB 4: Analytics ──────────────────────────────
    with tabs[3]:
        st.write("### 📊 Analytics Dashboard")

        cs  = get_complaint_stats()
        ss  = get_scan_stats()
        days_opt = st.select_slider(
            "📅 अवधि चुनें", options=[7, 14, 30], value=7,
            format_func=lambda x: f"पिछले {x} दिन"
        )

        # ── Metric Cards ──────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🗂️ कुल शिकायतें",  cs["total"])
        c2.metric("📅 आज",            cs["today"])
        c3.metric("🚨 उच्च जोखिम",   cs["high_risk"])
        c4.metric("🔍 कुल स्कैन",     ss["total"])

        st.divider()

        # ── Row 1: Daily Complaints + Daily Scans ─
        col_l, col_r = st.columns(2)

        with col_l:
            st.write("#### 📈 दैनिक शिकायतें")
            daily = get_daily_complaints(days_opt)
            if daily:
                df_d = pd.DataFrame(daily)
                df_d["day"] = pd.to_datetime(df_d["day"]).dt.strftime("%d %b")
                st.bar_chart(df_d.set_index("day")["count"],
                             color="#2a5298", use_container_width=True)
            else:
                st.info("अभी डेटा नहीं है।")

        with col_r:
            st.write("#### 🔍 दैनिक स्कैन")
            scans = get_daily_scans(days_opt)
            if scans:
                df_s = pd.DataFrame(scans)
                df_s["day"] = pd.to_datetime(df_s["day"]).dt.strftime("%d %b")
                st.bar_chart(df_s.set_index("day")["count"],
                             color="#27ae60", use_container_width=True)
            else:
                st.info("अभी डेटा नहीं है।")

        # ── Row 2: Risk Distribution + Source Breakdown ─
        col_a, col_b = st.columns(2)

        with col_a:
            st.write("#### ⚠️ जोखिम वितरण")
            risk = get_risk_distribution()
            total_r = sum(risk.values())
            if total_r > 0:
                df_r = pd.DataFrame({
                    "स्तर":   list(risk.keys()),
                    "संख्या": list(risk.values()),
                })
                # colored progress bars
                colors_map = {
                    "सुरक्षित (0)":        ("#27ae60", "🟢"),
                    "संदिग्ध (1-3)":       ("#f39c12", "🟡"),
                    "खतरनाक (4-5)":        ("#e67e22", "🟠"),
                    "अत्यंत खतरनाक (6+)": ("#e74c3c", "🔴"),
                }
                for level, count in risk.items():
                    pct = int(count / total_r * 100) if total_r else 0
                    color, emoji = colors_map.get(level, ("#999","⚪"))
                    st.markdown(
                        f'<div style="margin:6px 0">'
                        f'<span style="font-size:0.85rem">{emoji} <b>{level}</b> — {count} ({pct}%)</span>'
                        f'<div style="background:#eee;border-radius:6px;height:10px;margin-top:3px">'
                        f'<div style="background:{color};width:{pct}%;height:10px;border-radius:6px"></div>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("अभी डेटा नहीं है।")

        with col_b:
            st.write("#### 📡 स्रोत विश्लेषण")
            src = get_source_breakdown()
            if src:
                # donut-style using st.bar_chart
                df_src = pd.DataFrame({
                    "स्रोत":   [k.replace("streamlit","🖥️ App").replace("whatsapp","📱 WhatsApp") for k in src.keys()],
                    "शिकायतें": list(src.values()),
                })
                st.bar_chart(df_src.set_index("स्रोत")["शिकायतें"],
                             color="#8e44ad", use_container_width=True)
                # numbers
                for k, v in src.items():
                    label = "🖥️ App" if k == "streamlit" else "📱 WhatsApp"
                    pct = int(v / sum(src.values()) * 100)
                    st.caption(f"{label}: **{v}** शिकायतें ({pct}%)")
            else:
                st.info("अभी डेटा नहीं है।")

        # ── Scan Safety Overview ───────────────────
        st.divider()
        st.write("#### 🛡️ स्कैन सुरक्षा सारांश")
        total_sc = ss["total"]
        if total_sc > 0:
            safe_pct   = int(ss["safe"] / total_sc * 100)
            danger_pct = int(ss["danger"] / total_sc * 100)
            mid_pct    = 100 - safe_pct - danger_pct
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("✅ सुरक्षित स्कैन",    f"{ss['safe']}",   f"{safe_pct}%")
            sc2.metric("⚠️ संदिग्ध स्कैन",     f"{total_sc - ss['safe'] - ss['danger']}", f"{mid_pct}%")
            sc3.metric("🚨 खतरनाक स्कैन",     f"{ss['danger']}", f"{danger_pct}%")

            # single-row stacked progress
            bar_html = (
                f'<div style="display:flex;height:16px;border-radius:8px;overflow:hidden;margin:8px 0">'
                f'<div style="background:#27ae60;width:{safe_pct}%" title="सुरक्षित"></div>'
                f'<div style="background:#f39c12;width:{mid_pct}%" title="संदिग्ध"></div>'
                f'<div style="background:#e74c3c;width:{danger_pct}%" title="खतरनाक"></div>'
                f'</div>'
                f'<div style="font-size:0.78rem;color:#888">🟢 सुरक्षित &nbsp; 🟡 संदिग्ध &nbsp; 🔴 खतरनाक</div>'
            )
            st.markdown(bar_html, unsafe_allow_html=True)

        # ── Complaints Table ───────────────────────
        st.divider()
        st.write("#### 📋 हाल की शिकायतें")
        data = get_all_complaints(50)
        if data:
            cols_available = ["id","name","phone","alert_count","district","source","created_at"]
            df_cols = [c for c in cols_available if c in pd.DataFrame(data).columns]
            df = pd.DataFrame(data)[df_cols]
            col_names = {"id":"ID","name":"नाम","phone":"मोबाइल",
                         "alert_count":"अलर्ट","district":"📍 जिला",
                         "source":"स्रोत","created_at":"दिनांक"}
            df.columns = [col_names.get(c,c) for c in df_cols]
            df["दिनांक"] = df["दिनांक"].str[:16].str.replace("T"," ")
            df["स्रोत"] = df["स्रोत"].replace({"streamlit":"🖥️ App","whatsapp":"📱 WhatsApp","bulk_upload":"📄 Bulk"})
            if "📍 जिला" in df.columns:
                df["📍 जिला"] = df["📍 जिला"].fillna("").replace("","—")
            # color alert_count
            def color_alert(val):
                if val == 0:   return "background-color:#f0fff4"
                elif val <= 3: return "background-color:#fff8e1"
                else:          return "background-color:#fff0f0"
            st.dataframe(
                df.style.applymap(color_alert, subset=["अलर्ट"]),
                use_container_width=True, hide_index=True
            )
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 CSV डाउनलोड", csv,
                               "complaints.csv","text/csv",use_container_width=True)
        else:
            st.info("अभी कोई शिकायत नहीं।")

        # ── Feedback Stats ─────────────────────────
        st.divider()
        st.write("#### 👍 User Feedback — Scan Accuracy")
        fb = get_feedback_stats()
        if fb["total"] > 0:
            fcol1, fcol2, fcol3, fcol4 = st.columns(4)
            fcol1.metric("📊 कुल Feedback", fb["total"])
            fcol2.metric("✅ सही",   fb["correct"],  f"{round(fb['correct']/fb['total']*100)}%")
            fcol3.metric("❌ गलत",   fb["wrong"],    f"{round(fb['wrong']/fb['total']*100)}%")
            fcol4.metric("🤔 अनिश्चित", fb["unsure"], f"{round(fb['unsure']/fb['total']*100)}%")

            # Accuracy meter
            acc = fb["accuracy"]
            color = "#27ae60" if acc >= 80 else "#e67e22" if acc >= 60 else "#e74c3c"
            st.markdown(f"""
            <div style="background:#f8f9fa;border-radius:10px;padding:12px 16px;margin:8px 0">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                    <span style="font-weight:700;color:#333">Model Accuracy</span>
                    <span style="font-weight:900;color:{color};font-size:1.2rem">{acc}%</span>
                </div>
                <div style="background:#e0e0e0;border-radius:4px;height:12px">
                    <div style="background:{color};width:{acc}%;height:12px;border-radius:4px"></div>
                </div>
                <div style="font-size:0.75rem;color:#888;margin-top:4px">
                    {fb['correct']} सही / {fb['total']} कुल feedback
                </div>
            </div>""", unsafe_allow_html=True)

            # Recent feedback table
            recent = get_recent_feedback(10)
            if recent:
                with st.expander("📋 हाल का Feedback देखें"):
                    fb_df = pd.DataFrame(recent)[["id","vote","risk_level","created_at"]]
                    fb_df.columns = ["ID","Vote","Risk Level","दिनांक"]
                    fb_df["दिनांक"] = fb_df["दिनांक"].str[:16].str.replace("T"," ")
                    fb_df["Vote"] = fb_df["Vote"].replace({
                        "correct":"✅ सही","wrong":"❌ गलत","unsure":"🤔 अनिश्चित"
                    })
                    st.dataframe(fb_df, use_container_width=True, hide_index=True)
        else:
            st.info("📊 अभी कोई feedback नहीं। Scan करने के बाद 👍/❌ बटन दबाएं।")

    # ── TAB 5: AI Chatbot ─────────────────────────────
    with tabs[4]:
        st.write("### 🤖 साइबर सुरक्षा AI सहायक")
        st.caption("Claude AI द्वारा संचालित — हिंदी में साइबर सुरक्षा के सवाल पूछें")

        # Offline check
        if not check_internet():
            render_offline_warning("ai")
            st.info("📵 Internet नहीं है। Scam Database से offline help देख सकते हैं।")
            from scam_database import get_tip
            st.write("**💡 Offline Tip:**")
            st.info(get_tip(lang))
            st.stop()

        # API Key — env से या input से
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            api_key = st.text_input(
                "🔑 Anthropic API Key",
                type="password",
                placeholder="sk-ant-...",
                help="console.anthropic.com से API Key लें"
            )

        if not api_key:
            st.markdown("""
            <div class="cr-card cr-info">
                <b>API Key कैसे लें?</b><br>
                1. <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a> पर जाएं<br>
                2. Account बनाएं → API Keys → New Key<br>
                3. Key ऊपर paste करें <b>या</b> .env में <code>ANTHROPIC_API_KEY=sk-ant-...</code> डालें
            </div>""", unsafe_allow_html=True)
        else:
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            SYSTEM_PROMPT = """आप Cyber-Raksha AI के हिंदी साइबर सुरक्षा सहायक हैं।
आपको KDSP बिहार के लिए आम नागरिकों की मदद करनी है।

नियम:
- हमेशा सरल हिंदी में जवाब दें
- साइबर फ्रॉड, ऑनलाइन सुरक्षा, डिजिटल जागरूकता के विषयों पर ही बात करें
- खतरनाक स्थिति में हमेशा 1930 हेल्पलाइन का उल्लेख करें
- जवाब 150-250 शब्दों में रखें
- असंबंधित विषयों पर विनम्रता से मना करें
- तकनीकी शब्दों को सरल भाषा में समझाएं"""

            # Quick questions
            st.write("**💬 जल्दी पूछें:**")
            quick_qs = [
                "OTP फ्रॉड से कैसे बचें?",
                "WhatsApp lottery सच्ची है?",
                "KYC मैसेज मिला — क्या करूं?",
                "UPI से पैसे गए — अब क्या?",
                "नकली ऐप कैसे पहचानें?",
            ]
            qcols = st.columns(3)
            for i, q in enumerate(quick_qs):
                if qcols[i % 3].button(q, key=f"qq_{i}", use_container_width=True):
                    st.session_state["chat_history"].append({"role": "user", "content": q})
                    st.session_state["pending_chat"] = True
                    st.rerun()

            st.divider()

            # Chat display
            if not st.session_state["chat_history"]:
                st.markdown("""
                <div class="cr-card cr-info" style="text-align:center;padding:20px">
                    🤖 नमस्ते! मैं आपका साइबर सुरक्षा AI सहायक हूँ।<br>
                    साइबर फ्रॉड से जुड़ा कोई भी सवाल पूछें — हिंदी में।
                </div>""", unsafe_allow_html=True)
            else:
                for msg in st.session_state["chat_history"]:
                    if msg["role"] == "user":
                        st.markdown(
                            f'<div style="background:#e8f0fe;border-radius:12px 12px 0 12px;'
                            f'padding:10px 14px;margin:6px 0;margin-left:15%">'
                            f'<b>🧑 आप:</b> {msg["content"]}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div style="background:#f0fff4;border-radius:12px 12px 12px 0;'
                            f'padding:10px 14px;margin:6px 0;border-left:3px solid #27ae60;'
                            f'margin-right:15%">🤖 {msg["content"]}</div>',
                            unsafe_allow_html=True
                        )

            # Pending quick question process
            if st.session_state.get("pending_chat"):
                st.session_state["pending_chat"] = False
                with st.spinner("🤔 सोच रहा हूँ..."):
                    try:
                        client = anthropic.Anthropic(api_key=api_key)
                        resp = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=600,
                            system=SYSTEM_PROMPT,
                            messages=st.session_state["chat_history"][-10:]
                        )
                        st.session_state["chat_history"].append(
                            {"role": "assistant", "content": resp.content[0].text}
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

            # User input form — text + voice
            tab_text, tab_voice = st.tabs(["⌨️ Type करें", "🎤 बोलकर पूछें"])

            with tab_text:
                with st.form("chat_form", clear_on_submit=True):
                    col_inp, col_btn = st.columns([5, 1])
                    user_q = col_inp.text_input(
                        "सवाल:", label_visibility="collapsed",
                        placeholder="जैसे: OTP किसे नहीं देनी चाहिए?"
                    )
                    send = col_btn.form_submit_button("📤", use_container_width=True)

                if send and user_q.strip():
                    st.session_state["chat_history"].append(
                        {"role": "user", "content": user_q.strip()}
                    )
                    with st.spinner("🤔 सोच रहा हूँ..."):
                        try:
                            client = anthropic.Anthropic(api_key=api_key)
                            resp = client.messages.create(
                                model="claude-sonnet-4-20250514",
                                max_tokens=600,
                                system=SYSTEM_PROMPT,
                                messages=st.session_state["chat_history"][-10:]
                            )
                            answer = resp.content[0].text
                            st.session_state["chat_history"].append(
                                {"role": "assistant", "content": answer}
                            )
                            # AI reply को voice में भी सुनाएं
                            speak_advanced(answer[:300], speed=1.0,
                                           key="chat_reply",
                                           label="AI का जवाब")
                            st.rerun()
                        except anthropic.AuthenticationError:
                            st.error("❌ API Key गलत है।")
                            st.session_state["chat_history"].pop()
                        except anthropic.RateLimitError:
                            st.warning("⏳ Rate limit — थोड़ी देर बाद कोशिश करें।")
                            st.session_state["chat_history"].pop()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            st.session_state["chat_history"].pop()

            with tab_voice:
                st.caption("🎤 बोलें → Text दिखेगा → 'Copy करें' → ऊपर Type box में paste करें")
                render_speech_to_text(key="chat_stt", lang="hi-IN")
                render_voice_query(key="chat_vq")
                st.caption("💡 Chrome browser में बेहतर काम करता है।")
                st.session_state["chat_history"].append(
                            {"role": "assistant", "content": resp.content[0].text}
                        )
            if st.session_state.get("chat_history"):
                if st.button("🗑️ चैट साफ करें", use_container_width=True):
                    st.session_state["chat_history"] = []
                    st.rerun()

    # ── TAB 6: CSV Bulk Upload ────────────────────────
    with tabs[5]:
        st.write("### 📄 Bulk Message Scan — CSV Upload")
        st.caption("एक साथ 100+ messages/numbers की जाँच करें")

        # ── Download Sample CSV ───────────────────────
        with st.expander("📥 Sample CSV Format देखें / Download करें"):
            sample_data = """message,type,name
आपका SBI खाता बंद होगा। KYC करें: http://sbi-kyc.tk,message,Sample 1
आप KBC लॉटरी के विजेता हैं! 25 लाख जीते। OTP बताएं।,message,Sample 2
+923001234567,phone,Sample 3
9304123456,phone,Sample 4
यह एक सामान्य मैसेज है। कोई फ्रॉड नहीं।,message,Sample 5
"""
            st.code(sample_data, language="")
            st.download_button(
                "📥 Sample CSV Download करें",
                sample_data.encode("utf-8"),
                "sample_bulk_scan.csv",
                "text/csv",
                use_container_width=True
            )

        st.markdown("---")

        # ── CSV Upload ────────────────────────────────
        uploaded_csv = st.file_uploader(
            "CSV file चुनें (columns: message, type, name)",
            type=["csv"],
            help="message: text to scan | type: 'message' या 'phone' | name: optional label"
        )

        # Manual text input भी
        st.caption("**या सीधे messages टाइप करें** (एक line = एक message):")
        bulk_text = st.text_area("Messages (एक line पर एक):", height=100,
                                  placeholder="OTP मत बताइए\n+923001234567\nआप KBC winner हैं")

        col_scan, col_clear = st.columns([3,1])
        run_bulk = col_scan.button("🔎 सभी Scan करें", use_container_width=True,
                                    type="primary")

        if run_bulk:
            rows = []

            # CSV से rows
            if uploaded_csv:
                try:
                    import io
                    df_in = pd.read_csv(io.StringIO(
                        uploaded_csv.read().decode("utf-8", errors="ignore")
                    ))
                    for _, row in df_in.iterrows():
                        msg  = str(row.get("message", row.iloc[0])).strip()
                        typ  = str(row.get("type", "message")).strip().lower()
                        name = str(row.get("name", "")).strip()
                        if msg:
                            rows.append({"text": msg, "type": typ, "name": name})
                except Exception as e:
                    st.error(f"CSV पढ़ने में error: {e}")

            # Manual text से rows
            if bulk_text.strip():
                for line in bulk_text.strip().split("\n"):
                    line = line.strip()
                    if line:
                        # Phone number detect
                        typ = "phone" if re.match(r'^\+?[\d\s\-]{10,15}$', line) else "message"
                        rows.append({"text": line, "type": typ, "name": ""})

            if not rows:
                st.warning("कृपया CSV upload करें या messages टाइप करें।")
            else:
                st.info(f"🔄 {len(rows)} items scan हो रहे हैं...")
                progress = st.progress(0)

                results = []
                for i, row in enumerate(rows):
                    text = row["text"]
                    findings, score = check_security(text)
                    level, emoji_r  = get_risk_level(score)
                    save_scan(text, score, level, "bulk_upload")

                    results.append({
                        "क्र.":     i + 1,
                        "नाम/Label": row["name"] or f"Item {i+1}",
                        "Message":   text[:60] + ("..." if len(text) > 60 else ""),
                        "Type":      "📱 Phone" if row["type"] == "phone" else "💬 Message",
                        "Score":     score,
                        "जोखिम":    f"{emoji_r} {level}",
                        "Status":   "🚨 संदिग्ध" if score >= 4 else
                                    "⚠️ ध्यान दें" if score >= 2 else
                                    "✅ सुरक्षित",
                    })
                    progress.progress((i + 1) / len(rows))

                progress.empty()

                # ── Summary ───────────────────────────
                total  = len(results)
                danger = sum(1 for r in results if r["Score"] >= 4)
                warn   = sum(1 for r in results if 2 <= r["Score"] < 4)
                safe   = sum(1 for r in results if r["Score"] < 2)

                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("📊 कुल", total)
                sc2.metric("🚨 खतरनाक", danger, f"{round(danger/total*100)}%")
                sc3.metric("⚠️ संदिग्ध", warn,   f"{round(warn/total*100)}%")
                sc4.metric("✅ सुरक्षित", safe,   f"{round(safe/total*100)}%")

                # ── Results Table ─────────────────────
                st.write("#### 📋 Scan Results")
                df_out = pd.DataFrame(results)

                def color_status(val):
                    if "🚨" in str(val): return "background-color:#fff0f0;color:#c0392b;font-weight:700"
                    if "⚠️" in str(val): return "background-color:#fff8e1;color:#d35400"
                    return "background-color:#f0fff4;color:#27ae60"

                st.dataframe(
                    df_out.style.applymap(color_status, subset=["Status","जोखिम"]),
                    use_container_width=True,
                    hide_index=True
                )

                # ── Download Results ──────────────────
                csv_out = df_out.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📥 Results CSV Download करें",
                    csv_out,
                    f"bulk_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )

                # ── Dangerous items detail ────────────
                danger_items = [r for r in results if r["Score"] >= 4]
                if danger_items:
                    with st.expander(f"🚨 {len(danger_items)} खतरनाक items की detail"):
                        for item in danger_items:
                            st.markdown(
                                f'<div class="cr-card cr-danger">'
                                f'<b>{item["नाम/Label"]}</b>: {item["Message"]}'
                                f'<br><small>Score: {item["Score"]} | {item["जोखिम"]}</small>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                st.success(f"✅ {total} items scan complete! {danger} खतरनाक मिले।")

        # ── Instructions ──────────────────────────────
        st.divider()
        with st.expander("📖 Bulk Upload कैसे करें?"):
            st.markdown("""
**CSV Format:**
```
message,type,name
<text या phone>,message/phone,<label>
```

**Tips:**
- `type=message` → text scan होगा
- `type=phone` → phone reputation check होगा
- `name` column optional है — पहचान के लिए
- एक बार में 500 rows तक support
- Results CSV में download करें
- सभी scans database में save होते हैं

**Manual Input:**
- Text box में एक line पर एक message
- Phone numbers अपने आप detect होते हैं
            """)


    # ── TAB 7: Admin Dashboard ────────────────────────
    with tabs[6]:
        render_admin_dashboard(current_user=st.session_state.get("username","admin"))

    st.markdown(f"""
    <div class="cr-footer">
        ⚠️ {t('helpline_msg', lang)}<br>
        <span class="helpline-badge">📞 1930</span><br><br>
        <a href="https://cybercrime.gov.in" target="_blank">cybercrime.gov.in</a><br><br>
        <strong>डेवलपर:</strong> V K SAKSENA | KDSP बिहार
    </div>""", unsafe_allow_html=True)

# ── Entry Point ────────────────────────────────────────
if not st.session_state.get("logged_in"):
    show_login()
else:
    show_app()
