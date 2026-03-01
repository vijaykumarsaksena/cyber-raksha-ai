"""
translations.py — Multi-language Support v1.0
──────────────────────────────────────────────
Cyber-Raksha AI — 6 भाषाएं:
  hi  : हिंदी (default)
  bho : भोजपुरी
  mai : मैथिली
  ur  : उर्दू
  mag : मगही
  en  : English
"""

# ══════════════════════════════════════════════════════════
#  LANGUAGE META
# ══════════════════════════════════════════════════════════

LANGUAGES = {
    "hi":  {"name": "हिंदी",     "flag": "🇮🇳", "gtts": "hi", "speech": "hi-IN"},
    "bho": {"name": "भोजपुरी",   "flag": "🇮🇳", "gtts": "hi", "speech": "hi-IN"},
    "mai": {"name": "मैथिली",    "flag": "🇮🇳", "gtts": "hi", "speech": "hi-IN"},
    "ur":  {"name": "اردو",      "flag": "🇮🇳", "gtts": "ur", "speech": "ur-IN"},
    "mag": {"name": "मगही",      "flag": "🇮🇳", "gtts": "hi", "speech": "hi-IN"},
    "en":  {"name": "English",   "flag": "🇬🇧", "gtts": "en", "speech": "en-IN"},
}

# ══════════════════════════════════════════════════════════
#  TRANSLATIONS
# ══════════════════════════════════════════════════════════

T = {

    # ── App title & tagline ────────────────────────────
    "app_title": {
        "hi":  "🛡️ Cyber-Raksha AI",
        "bho": "🛡️ Cyber-Raksha AI",
        "mai": "🛡️ Cyber-Raksha AI",
        "ur":  "🛡️ Cyber-Raksha AI",
        "mag": "🛡️ Cyber-Raksha AI",
        "en":  "🛡️ Cyber-Raksha AI",
    },
    "tagline": {
        "hi":  "साइबर फ्रॉड से बचाव | KDSP बिहार",
        "bho": "साइबर फ्रॉड से बचाव | KDSP बिहार",
        "mai": "साइबर धोखाधड़ीसँ बचाव | KDSP बिहार",
        "ur":  "سائبر فراڈ سے بچاؤ | KDSP بہار",
        "mag": "साइबर ठगी से बचाव | KDSP बिहार",
        "en":  "Cyber Fraud Protection | KDSP Bihar",
    },

    # ── Login ──────────────────────────────────────────
    "login_title": {
        "hi":  "🔐 Admin Login",
        "bho": "🔐 Admin Login",
        "mai": "🔐 Admin Login",
        "ur":  "🔐 ایڈمن لاگ ان",
        "mag": "🔐 Admin Login",
        "en":  "🔐 Admin Login",
    },
    "username": {
        "hi":  "यूज़रनेम",
        "bho": "यूज़रनेम",
        "mai": "यूज़रनेम",
        "ur":  "یوزرنیم",
        "mag": "यूज़रनेम",
        "en":  "Username",
    },
    "password": {
        "hi":  "पासवर्ड",
        "bho": "पासवर्ड",
        "mai": "पासवर्ड",
        "ur":  "پاسورڈ",
        "mag": "पासवर्ड",
        "en":  "Password",
    },
    "login_btn": {
        "hi":  "🔓 Login करें",
        "bho": "🔓 Login करीं",
        "mai": "🔓 Login करू",
        "ur":  "🔓 لاگ ان کریں",
        "mag": "🔓 Login करो",
        "en":  "🔓 Login",
    },
    "login_success": {
        "hi":  "✅ Login सफल!",
        "bho": "✅ Login हो गइल!",
        "mai": "✅ Login भेल!",
        "ur":  "✅ لاگ ان کامیاب!",
        "mag": "✅ Login हो गेल!",
        "en":  "✅ Login Successful!",
    },
    "login_fail": {
        "hi":  "❌ गलत यूज़रनेम या पासवर्ड",
        "bho": "❌ गलत यूज़रनेम या पासवर्ड बा",
        "mai": "❌ गलत यूज़रनेम वा पासवर्ड",
        "ur":  "❌ غلط یوزرنیم یا پاسورڈ",
        "mag": "❌ गलत यूज़रनेम या पासवर्ड हे",
        "en":  "❌ Wrong username or password",
    },

    # ── Tab names ──────────────────────────────────────
    "tab_scan": {
        "hi":  "🔍 स्कैन",
        "bho": "🔍 जांच",
        "mai": "🔍 जाँच",
        "ur":  "🔍 اسکین",
        "mag": "🔍 जाँच",
        "en":  "🔍 Scan",
    },
    "tab_report": {
        "hi":  "📝 रिपोर्ट",
        "bho": "📝 रिपोर्ट",
        "mai": "📝 रिपोर्ट",
        "ur":  "📝 رپورٹ",
        "mag": "📝 रिपोर्ट",
        "en":  "📝 Report",
    },
    "tab_quiz": {
        "hi":  "🎮 क्विज़",
        "bho": "🎮 क्विज़",
        "mai": "🎮 क्विज़",
        "ur":  "🎮 کوئز",
        "mag": "🎮 क्विज़",
        "en":  "🎮 Quiz",
    },
    "tab_analytics": {
        "hi":  "📊 Analytics",
        "bho": "📊 Analytics",
        "mai": "📊 Analytics",
        "ur":  "📊 تجزیہ",
        "mag": "📊 Analytics",
        "en":  "📊 Analytics",
    },
    "tab_ai": {
        "hi":  "🤖 AI सहायक",
        "bho": "🤖 AI मदद",
        "mai": "🤖 AI सहायक",
        "ur":  "🤖 AI مددگار",
        "mag": "🤖 AI सहायक",
        "en":  "🤖 AI Assistant",
    },

    # ── Scan tab ───────────────────────────────────────
    "scan_title": {
        "hi":  "मैसेज या स्क्रीनशॉट की जांच",
        "bho": "मैसेज या फोटो के जांच करीं",
        "mai": "मैसेज या स्क्रीनशॉटक जाँच",
        "ur":  "پیغام یا اسکرین شاٹ کی جانچ",
        "mag": "मैसेज या फोटो के जाँच",
        "en":  "Check Message or Screenshot",
    },
    "scan_mode_text": {
        "hi":  "✍️ टेक्स्ट",
        "bho": "✍️ लिखल",
        "mai": "✍️ टेक्स्ट",
        "ur":  "✍️ متن",
        "mag": "✍️ लिखल",
        "en":  "✍️ Text",
    },
    "scan_mode_img": {
        "hi":  "🖼️ स्क्रीनशॉट",
        "bho": "🖼️ फोटो",
        "mai": "🖼️ स्क्रीनशॉट",
        "ur":  "🖼️ اسکرین شاٹ",
        "mag": "🖼️ फोटो",
        "en":  "🖼️ Screenshot",
    },
    "scan_placeholder": {
        "hi":  "मैसेज पेस्ट करें:",
        "bho": "मैसेज लिखीं या paste करीं:",
        "mai": "मैसेज पेस्ट करू:",
        "ur":  "پیغام یہاں پیسٹ کریں:",
        "mag": "मैसेज paste करो:",
        "en":  "Paste your message here:",
    },
    "scan_btn": {
        "hi":  "🔎 जांच शुरू करें",
        "bho": "🔎 जांच शुरू करीं",
        "mai": "🔎 जाँच शुरू करू",
        "ur":  "🔎 جانچ شروع کریں",
        "mag": "🔎 जाँच शुरू करो",
        "en":  "🔎 Start Scan",
    },
    "scan_safe": {
        "hi":  "✅ सुरक्षित! — कोई बड़ा खतरा नहीं मिला।",
        "bho": "✅ सुरक्षित बा! — कवनो खतरा नइखे।",
        "mai": "✅ सुरक्षित! — कोनो खतरा नहि भेटल।",
        "ur":  "✅ محفوظ! — کوئی بڑا خطرہ نہیں ملا۔",
        "mag": "✅ सुरक्षित हे! — कोय खतरा नञ मिलल।",
        "en":  "✅ Safe! — No major threat found.",
    },
    "scan_danger": {
        "hi":  "संदिग्ध संकेत मिले",
        "bho": "संदिग्ध चीज मिलल",
        "mai": "संदिग्ध संकेत भेटल",
        "ur":  "مشکوک اشارے ملے",
        "mag": "संदिग्ध चीज मिलल",
        "en":  "Suspicious signs found",
    },

    # ── Report tab ─────────────────────────────────────
    "report_title": {
        "hi":  "📄 पुलिस शिकायत ड्राफ्ट",
        "bho": "📄 पुलिस शिकायत बनावल",
        "mai": "📄 पुलिस शिकायत ड्राफ्ट",
        "ur":  "📄 پولیس شکایت ڈرافٹ",
        "mag": "📄 पुलिस शिकायत बनाओ",
        "en":  "📄 Police Complaint Draft",
    },
    "name_label": {
        "hi":  "ग्राहक का नाम *",
        "bho": "आपन नाम *",
        "mai": "आपनाक नाम *",
        "ur":  "آپ کا نام *",
        "mag": "आपन नाम *",
        "en":  "Your Name *",
    },
    "phone_label": {
        "hi":  "मोबाइल नंबर",
        "bho": "मोबाइल नंबर",
        "mai": "मोबाइल नंबर",
        "ur":  "موبائل نمبر",
        "mag": "मोबाइल नंबर",
        "en":  "Mobile Number",
    },
    "msg_label": {
        "hi":  "फ्रॉड संदेश / विवरण *",
        "bho": "ठगी के मैसेज / बात *",
        "mai": "ठगीक संदेश / विवरण *",
        "ur":  "فراڈ پیغام / تفصیل *",
        "mag": "ठगी के मैसेज / बात *",
        "en":  "Fraud Message / Description *",
    },
    "pdf_btn": {
        "hi":  "📄 PDF तैयार करें",
        "bho": "📄 PDF बनाईं",
        "mai": "📄 PDF बनाबू",
        "ur":  "📄 PDF بنائیں",
        "mag": "📄 PDF बनाओ",
        "en":  "📄 Generate PDF",
    },

    # ── Results ────────────────────────────────────────
    "risk_safe": {
        "hi":  "सुरक्षित",
        "bho": "सुरक्षित",
        "mai": "सुरक्षित",
        "ur":  "محفوظ",
        "mag": "सुरक्षित",
        "en":  "Safe",
    },
    "risk_suspicious": {
        "hi":  "संदिग्ध",
        "bho": "शक वाला",
        "mai": "संदिग्ध",
        "ur":  "مشکوک",
        "mag": "शक वाला",
        "en":  "Suspicious",
    },
    "risk_dangerous": {
        "hi":  "खतरनाक",
        "bho": "खतरनाक",
        "mai": "खतरनाक",
        "ur":  "خطرناک",
        "mag": "खतरनाक",
        "en":  "Dangerous",
    },
    "risk_very_dangerous": {
        "hi":  "अत्यंत खतरनाक",
        "bho": "बहुत खतरनाक",
        "mai": "अत्यंत खतरनाक",
        "ur":  "انتہائی خطرناک",
        "mag": "बहुत खतरनाक",
        "en":  "Very Dangerous",
    },

    # ── Helpline ───────────────────────────────────────
    "helpline_msg": {
        "hi":  "फ्रॉड होने पर तुरंत डायल करें",
        "bho": "ठगी होखे त फौरन डायल करीं",
        "mai": "ठगी भेलापर तुरंत डायल करू",
        "ur":  "فراڈ ہونے پر فوری ڈائل کریں",
        "mag": "ठगी होय त तुरंत डायल करो",
        "en":  "Dial immediately if fraud occurs",
    },

    # ── Fraud keywords (extended per language) ────────
    "fraud_keywords_extra": {
        "bho": [
            "लॉटरी", "इनाम बा", "ओटीपी बताईं", "पईसा डबल",
            "केवाईसी करीं", "खाता बंद होई", "तुरंते", "फ्री रिचार्ज",
            "जीत गइल बानी", "क्लिक करीं",
        ],
        "mai": [
            "लॉटरी", "इनाम अछि", "ओटीपी दिअ", "पैसा दोगुना",
            "केवाईसी करू", "खाता बंद होयत", "तुरंत", "फ्री रिचार्ज",
            "जीत गेलहुँ", "क्लिक करू",
        ],
        "ur": [
            "لاٹری", "انعام", "او ٹی پی", "پیسے دوگنے",
            "کے وائی سی", "اکاؤنٹ بند", "فوری", "مفت ری چارج",
            "جیت گئے", "کلک کریں", "یقینی منافع",
        ],
        "mag": [
            "लॉटरी", "इनाम हे", "ओटीपी बताओ", "पईसा दोगुना",
            "केवाईसी करो", "खाता बंद होतो", "तुरंत", "फ्री रिचार्ज",
            "जीत गेलो", "क्लिक करो",
        ],
        "en": [
            "lottery", "prize", "otp", "double money", "kyc",
            "account blocked", "urgent", "free recharge", "you won",
            "click here", "guaranteed profit", "work from home",
        ],
    },

    # ── Misc UI ────────────────────────────────────────
    "logout": {
        "hi":  "🚪 Logout",
        "bho": "🚪 बाहर जाईं",
        "mai": "🚪 Logout",
        "ur":  "🚪 لاگ آؤٹ",
        "mag": "🚪 Logout",
        "en":  "🚪 Logout",
    },
    "welcome": {
        "hi":  "नमस्ते",
        "bho": "प्रणाम",
        "mai": "प्रणाम",
        "ur":  "السلام علیکم",
        "mag": "नमस्कार",
        "en":  "Welcome",
    },
    "no_input": {
        "hi":  "कृपया कुछ इनपुट दें।",
        "bho": "कुछ लिखीं या बोलीं।",
        "mai": "किछु input दिअ।",
        "ur":  "براہ کرم کچھ درج کریں۔",
        "mag": "कुछ लिखो।",
        "en":  "Please enter some input.",
    },
    "advanced_mode": {
        "hi":  "🔬 Advanced Mode",
        "bho": "🔬 गहिरा जांच",
        "mai": "🔬 Advanced Mode",
        "ur":  "🔬 جدید موڈ",
        "mag": "🔬 गहरा जाँच",
        "en":  "🔬 Advanced Mode",
    },
    "voice_assistant": {
        "hi":  "🔊 Voice Assistant",
        "bho": "🔊 आवाज़ वाला",
        "mai": "🔊 आवाज़ सहायक",
        "ur":  "🔊 آواز مددگار",
        "mag": "🔊 आवाज़ वाला",
        "en":  "🔊 Voice Assistant",
    },
    "speak_slow": {
        "hi":  "धीरे बोलें",
        "bho": "धीरे बोलीं",
        "mai": "धीरे बाजू",
        "ur":  "آہستہ بولیں",
        "mag": "धीरे बोलो",
        "en":  "Speak slowly",
    },
    "complaint_filed": {
        "hi":  "शिकायत दर्ज! ID:",
        "bho": "शिकायत दर्ज हो गइल! ID:",
        "mai": "शिकायत दर्ज भेल! ID:",
        "ur":  "شکایت درج! ID:",
        "mag": "शिकायत दर्ज हो गेल! ID:",
        "en":  "Complaint Filed! ID:",
    },
    "download_pdf": {
        "hi":  "📥 PDF डाउनलोड",
        "bho": "📥 PDF डाउनलोड करीं",
        "mai": "📥 PDF डाउनलोड करू",
        "ur":  "📥 PDF ڈاؤنلوڈ",
        "mag": "📥 PDF डाउनलोड",
        "en":  "📥 Download PDF",
    },
}


# ══════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════

def t(key: str, lang: str = "hi") -> str:
    """
    Translation lookup।
    t("scan_btn", "bho") → "🔎 जांच शुरू करीं"
    """
    entry = T.get(key, {})
    return entry.get(lang) or entry.get("hi") or key


def get_language_selector_label(lang: str) -> str:
    """Language selector के लिए label।"""
    meta = LANGUAGES.get(lang, {})
    return f"{meta.get('flag','')} {meta.get('name','')}"


def get_all_fraud_keywords(lang: str, base_keywords: list) -> list:
    """Base keywords + language-specific keywords combine करें।"""
    extra = T.get("fraud_keywords_extra", {}).get(lang, [])
    return list(set(base_keywords + extra))


def get_gtts_lang(lang: str) -> str:
    """gTTS language code।"""
    return LANGUAGES.get(lang, {}).get("gtts", "hi")


def get_speech_lang(lang: str) -> str:
    """Web Speech API language code।"""
    return LANGUAGES.get(lang, {}).get("speech", "hi-IN")
