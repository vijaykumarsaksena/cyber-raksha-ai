"""
cyber_raksha_bot.py — Multilingual Edition v3.0
────────────────────────────────────────────────
✅ 6 भाषाएं: हिंदी, भोजपुरी, मैथिली, उर्दू, मगही, English
✅ Scam Database integration
✅ Language auto-detect + manual change
✅ SQLite sessions
"""

import os, re, json, random
import sqlite3
from flask           import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv          import load_dotenv
from security_engine import check_security, get_risk_level, format_findings_for_whatsapp
from database        import save_complaint, save_scan
from alert_system    import trigger_alert
from scam_database   import check_patterns, get_tip, get_helpline, get_db_stats

load_dotenv()
app = Flask(__name__)
_DB = os.path.join(os.path.dirname(__file__), "cyber_raksha.db")


# ══════════════════════════════════════════════════════════
#  SESSION MANAGEMENT
# ══════════════════════════════════════════════════════════

def _conn():
    c = sqlite3.connect(_DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS bot_sessions (
        phone TEXT PRIMARY KEY,
        state TEXT DEFAULT 'menu',
        lang  TEXT DEFAULT 'hi',
        data  TEXT DEFAULT '{}'
    )""")
    c.commit()
    return c

def get_session(phone):
    conn = _conn()
    row  = conn.execute(
        "SELECT state, lang, data FROM bot_sessions WHERE phone=?", (phone,)
    ).fetchone()
    conn.close()
    if row is None:
        return {"state": "menu", "lang": "hi", "data": {}}
    return {"state": row["state"], "lang": row["lang"],
            "data": json.loads(row["data"])}

def save_session(phone, session):
    conn = _conn()
    conn.execute("""INSERT INTO bot_sessions (phone, state, lang, data)
                    VALUES (?,?,?,?)
                    ON CONFLICT(phone) DO UPDATE SET
                    state=excluded.state, lang=excluded.lang, data=excluded.data""",
                 (phone, session["state"], session["lang"],
                  json.dumps(session["data"], ensure_ascii=False)))
    conn.commit(); conn.close()

def reset_session(phone, lang="hi"):
    conn = _conn()
    conn.execute("""INSERT INTO bot_sessions (phone, state, lang, data)
                    VALUES (?,?,?,?)
                    ON CONFLICT(phone) DO UPDATE SET
                    state='menu', lang=excluded.lang, data='{}'""",
                 (phone, "menu", lang, "{}"))
    conn.commit(); conn.close()


# ══════════════════════════════════════════════════════════
#  LANGUAGE AUTO-DETECT
# ══════════════════════════════════════════════════════════

LANG_TRIGGERS = {
    "bho": ["bhojpuri","भोजपुरी","bho","बोलीं","करीं","बानी","नइखे"],
    "mai": ["maithili","मैथिली","mai","करू","देलहुँ","जाउ","अछि"],
    "ur":  ["urdu","اردو","ur","کریں","ہے","نہیں","بتائیں"],
    "mag": ["magahi","मगही","mag","करो","गेलो","हेला","नञ"],
    "en":  ["english","en","hello","hi there","scan this","help me"],
}

def detect_lang(text):
    tl = text.lower()
    for lang, triggers in LANG_TRIGGERS.items():
        if any(tr in tl for tr in triggers):
            return lang
    return None


# ══════════════════════════════════════════════════════════
#  MULTILINGUAL STRINGS
# ══════════════════════════════════════════════════════════

MENU = {
    "hi":  "🛡️ *साइबर-रक्षा Bot* में आपका स्वागत है!\n_KDSP बिहार | V K SAKSENA_\n\n1️⃣ मैसेज की सुरक्षा जांच\n2️⃣ फ्रॉड की शिकायत दर्ज\n3️⃣ साइबर सुरक्षा टिप\n4️⃣ हेल्पलाइन नंबर\n5️⃣ भाषा बदलें\n\nनंबर टाइप करें (1-5)",
    "bho": "🛡️ *साइबर-रक्षा Bot* में रउआ के स्वागत बा!\n_KDSP बिहार | V K SAKSENA_\n\n1️⃣ मैसेज के जांच करीं\n2️⃣ ठगी के शिकायत करीं\n3️⃣ सुरक्षा टिप पाईं\n4️⃣ हेल्पलाइन नंबर\n5️⃣ भाषा बदलीं\n\nनंबर टाइप करीं (1-5)",
    "mai": "🛡️ *साइबर-रक्षा Bot* मे अहाँक स्वागत!\n_KDSP बिहार | V K SAKSENA_\n\n1️⃣ मैसेजक जाँच करू\n2️⃣ ठगीक शिकायत करू\n3️⃣ सुरक्षा टिप पाबू\n4️⃣ हेल्पलाइन नंबर\n5️⃣ भाषा बदलू\n\nनंबर टाइप करू (1-5)",
    "ur":  "🛡️ *سائبر-رکشا Bot* میں خوش آمدید!\n_KDSP بہار | V K SAKSENA_\n\n1️⃣ پیغام کی جانچ\n2️⃣ فراڈ کی شکایت\n3️⃣ سیکورٹی ٹپ\n4️⃣ ہیلپ لائن\n5️⃣ زبان بدلیں\n\nنمبر ٹائپ کریں (1-5)",
    "mag": "🛡️ *साइबर-रक्षा Bot* में अहाँ के स्वागत हे!\n_KDSP बिहार | V K SAKSENA_\n\n1️⃣ मैसेज के जाँच करो\n2️⃣ ठगी के शिकायत करो\n3️⃣ सुरक्षा टिप पाओ\n4️⃣ हेल्पलाइन नंबर\n5️⃣ भाषा बदलो\n\nनंबर टाइप करो (1-5)",
    "en":  "🛡️ Welcome to *Cyber-Raksha Bot*!\n_KDSP Bihar | V K SAKSENA_\n\n1️⃣ Scan message for fraud\n2️⃣ File a fraud complaint\n3️⃣ Get security tip\n4️⃣ Helpline numbers\n5️⃣ Change language\n\nType a number (1-5)",
}

SCAN_PROMPT = {
    "hi":  "🔍 संदिग्ध मैसेज यहाँ भेजें:\n_('0' = वापस)_",
    "bho": "🔍 शक वाला मैसेज यहाँ भेजीं:\n_('0' = वापस)_",
    "mai": "🔍 संदिग्ध मैसेज हिठाम पठाउ:\n_('0' = वापस)_",
    "ur":  "🔍 مشکوک پیغام یہاں بھیجیں:\n_('0' = واپس)_",
    "mag": "🔍 शक वाला मैसेज इहाँ भेजो:\n_('0' = वापस)_",
    "en":  "🔍 Send the suspicious message here:\n_('0' = back)_",
}

SAFE_MSG = {
    "hi":  "✅ *सुरक्षित!*\nकोई बड़ा खतरा नहीं मिला।\n\n_दूसरा मैसेज भेजें या '0'।_",
    "bho": "✅ *सुरक्षित बा!*\nकवनो खतरा नइखे।\n\n_दूसर मैसेज भेजीं या '0'।_",
    "mai": "✅ *सुरक्षित!*\nकोनो खतरा नहि भेटल।\n\n_दोसर मैसेज पठाउ या '0'।_",
    "ur":  "✅ *محفوظ!*\nکوئی بڑا خطرہ نہیں۔\n\n_دوسرا پیغام یا '0'۔_",
    "mag": "✅ *सुरक्षित हे!*\nकोय खतरा नञ मिलल।\n\n_दोसर मैसेज भेजो या '0'।_",
    "en":  "✅ *Safe!*\nNo major threat found.\n\n_Send another or type '0'._",
}

DANGER_SUFFIX = {
    "hi":  "⚠️ इस मैसेज पर भरोसा न करें। 1930 पर कॉल करें।",
    "bho": "⚠️ एह मैसेज पर भरोसा मत करीं। 1930 call करीं।",
    "mai": "⚠️ एहि मैसेज पर भरोसा नहि करू। 1930 call करू।",
    "ur":  "⚠️ اس پیغام پر بھروسہ نہ کریں۔ 1930 کال کریں۔",
    "mag": "⚠️ एकरा पर भरोसा मत करो। 1930 call करो।",
    "en":  "⚠️ Do not trust this message. Call 1930.",
}

SCAN_WORD = {
    "hi":"संदिग्ध संकेत","bho":"शक के चीज","mai":"संदिग्ध",
    "ur":"مشکوک","mag":"शक वाला","en":"suspicious signals",
}

NAME_PROMPT = {
    "hi":  "📝 अपना *पूरा नाम* बताएं:",
    "bho": "📝 आपन *पूरा नाम* बताईं:",
    "mai": "📝 अपना *पूरा नाम* कहू:",
    "ur":  "📝 اپنا *پورا نام* بتائیں:",
    "mag": "📝 आपन *पूरा नाम* बताओ:",
    "en":  "📝 Please enter your *full name*:",
}

GREET = {
    "hi":"नमस्ते","bho":"प्रणाम","mai":"प्रणाम",
    "ur":"السلام علیکم","mag":"नमस्कार","en":"Hello",
}

PHONE_PROMPT = {
    "hi":  "*मोबाइल नंबर* बताएं:",
    "bho": "*मोबाइल नंबर* बताईं:",
    "mai": "*मोबाइल नंबर* दिअ:",
    "ur":  "*موبائل نمبر* بتائیں:",
    "mag": "*मोबाइल नंबर* बताओ:",
    "en":  "Enter your *mobile number*:",
}

WRONG_PHONE = {
    "hi":"❌ सही 10 अंकों का नंबर डालें:",
    "bho":"❌ सही 10 अंक वाला नंबर डालीं:",
    "mai":"❌ सही 10 अंकक नंबर दिअ:",
    "ur":"❌ صحیح 10 ہندسوں کا نمبر:",
    "mag":"❌ सही 10 अंक वाला नंबर डालो:",
    "en":"❌ Enter a valid 10-digit number:",
}

DESC_PROMPT = {
    "hi":  "✅ नंबर सेव।\n\n*फ्रॉड का विवरण* बताएं:\n_(क्या हुआ, कब हुआ, कितना नुकसान)_",
    "bho": "✅ नंबर सेव।\n\n*ठगी के बारे में* बताईं:\n_(का भइल, कब, केतना नुकसान)_",
    "mai": "✅ नंबर सेव।\n\n*ठगीक विवरण* दिअ:\n_(की भेल, कखन, कतेक नुकसान)_",
    "ur":  "✅ نمبر محفوظ۔\n\n*فراڈ کی تفصیل* بتائیں:\n_(کیا ہوا، کب، کتنا نقصان)_",
    "mag": "✅ नंबर सेव।\n\n*ठगी के बारे में* बताओ:\n_(का भेल, कब, केतना नुकसान)_",
    "en":  "✅ Number saved.\n\nDescribe the *fraud*:\n_(what happened, when, how much lost)_",
}

DISTRICT_PROMPT = {
    "hi":  "✅ नंबर सेव।\n\n*जिला* बताएं (जैसे: पटना, गया, मुजफ्फरपुर):\n_(या 'skip' लिखें)_",
    "bho": "✅ नंबर सेव।\n\n*जिला* बताईं (जइसे: पटना, गया):\n_(या 'skip' लिखीं)_",
    "mai": "✅ नंबर सेव।\n\n*जिला* कहू (जेना: पटना, गया):\n_(वा 'skip' लिखू)_",
    "ur":  "✅ نمبر محفوظ۔\n\n*ضلع* بتائیں (مثلاً: پٹنہ، گیا):\n_('skip' لکھ سکتے ہیں)_",
    "mag": "✅ नंबर सेव।\n\n*जिला* बताओ (जइसे: पटना, गया):\n_(या 'skip' लिखो)_",
    "en":  "✅ Number saved.\n\n*District* (e.g. Patna, Gaya):\n_(or type 'skip')_",
}
    "hi":  "📋 *शिकायत दर्ज!*\n\n🆔 ID: CR-{cid}\n👤 {name} | 📱 {phone}\n\n*अगले कदम:*\n1️⃣ 1930 पर कॉल करें\n2️⃣ cybercrime.gov.in\n3️⃣ नजदीकी थाना\n\n_'0' = menu_",
    "bho": "📋 *शिकायत दर्ज भइल!*\n\n🆔 ID: CR-{cid}\n👤 {name} | 📱 {phone}\n\n*आगे करीं:*\n1️⃣ 1930 call करीं\n2️⃣ cybercrime.gov.in\n3️⃣ नजदीकी थाना\n\n_'0' = menu_",
    "mai": "📋 *शिकायत दर्ज भेल!*\n\n🆔 ID: CR-{cid}\n👤 {name} | 📱 {phone}\n\n*आगाँ:*\n1️⃣ 1930 call करू\n2️⃣ cybercrime.gov.in\n3️⃣ थाना\n\n_'0' = menu_",
    "ur":  "📋 *شکایت درج!*\n\n🆔 ID: CR-{cid}\n👤 {name} | 📱 {phone}\n\n*اگلے اقدام:*\n1️⃣ 1930 کال\n2️⃣ cybercrime.gov.in\n3️⃣ تھانہ\n\n_'0' = menu_",
    "mag": "📋 *शिकायत दर्ज!*\n\n🆔 ID: CR-{cid}\n👤 {name} | 📱 {phone}\n\n*आगे:*\n1️⃣ 1930 call करो\n2️⃣ cybercrime.gov.in\n3️⃣ थाना\n\n_'0' = menu_",
    "en":  "📋 *Complaint Filed!*\n\n🆔 ID: CR-{cid}\n👤 {name} | 📱 {phone}\n\n*Next steps:*\n1️⃣ Call 1930\n2️⃣ cybercrime.gov.in\n3️⃣ Police station\n\n_'0' = menu_",
}

LANG_MENU_TEXT = "🌐 *भाषा / Language:*\n\n1. हिंदी\n2. भोजपुरी\n3. मैथिली\n4. اردو\n5. मगही\n6. English\n\nनंबर टाइप करें:"
LANG_MAP = {"1":"hi","2":"bho","3":"mai","4":"ur","5":"mag","6":"en"}


# ══════════════════════════════════════════════════════════
#  WEBHOOK
# ══════════════════════════════════════════════════════════

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.form.get("Body", "").strip()
    sender   = request.form.get("From", "")
    session  = get_session(sender)
    state    = session["state"]
    lang     = session["lang"]

    resp = MessagingResponse()
    msg  = resp.message()

    # Language auto-detect
    detected = detect_lang(incoming)
    if detected and detected != lang:
        lang = detected
        session["lang"] = lang
        save_session(sender, session)

    # Reset / menu triggers
    if incoming.lower() in ["menu","मेनू","start","0","hi","hello",
                             "नमस्ते","प्रणाम","السلام","नमस्कार"]:
        reset_session(sender, lang)
        msg.body(MENU.get(lang, MENU["hi"]))
        return str(resp)

    # Language select state
    if state == "lang_select":
        new_lang = LANG_MAP.get(incoming)
        if new_lang:
            lang = new_lang
            session["lang"] = lang
            session["state"] = "menu"
            save_session(sender, session)
            msg.body(MENU.get(lang, MENU["hi"]))
        else:
            msg.body(LANG_MENU_TEXT)
        return str(resp)

    # Menu
    if state == "menu":
        if incoming == "1":
            session["state"] = "scan"; save_session(sender, session)
            msg.body(SCAN_PROMPT.get(lang, SCAN_PROMPT["hi"]))
        elif incoming == "2":
            session["state"] = "name"; save_session(sender, session)
            msg.body(NAME_PROMPT.get(lang, NAME_PROMPT["hi"]))
        elif incoming == "3":
            msg.body(f"💡 *Tip*\n\n{get_tip(lang)}")
        elif incoming == "4":
            msg.body(get_helpline(lang))
        elif incoming == "5":
            session["state"] = "lang_select"; save_session(sender, session)
            msg.body(LANG_MENU_TEXT)
        else:
            msg.body(MENU.get(lang, MENU["hi"]))

    # Scan
    elif state == "scan":
        findings, score = check_security(incoming)
        level, emoji    = get_risk_level(score)
        save_scan(incoming, score, level, "whatsapp")
        db_matches = check_patterns(incoming, lang)

        if score == 0 and not db_matches:
            msg.body(SAFE_MSG.get(lang, SAFE_MSG["hi"]))
        else:
            detail = format_findings_for_whatsapp(findings)
            db_warn = ""
            if db_matches:
                best = max(db_matches, key=lambda x: x["risk"])
                db_warn = f"\n\n🗄️ *{best['name']}*\n💡 {best['advice']}"
            reply = (f"{emoji} *{level}!* — {score} "
                     f"{SCAN_WORD.get(lang,'संदिग्ध')}:\n\n"
                     f"{detail}{db_warn}\n\n"
                     f"{DANGER_SUFFIX.get(lang,'')}\n\n"
                     f"_{'दूसरा मैसेज या 0' if lang=='hi' else 'Next msg or 0'}_")
            trigger_alert("scan", score, message=incoming, source="whatsapp")
            msg.body(reply)

    # Name
    elif state == "name":
        session["data"]["name"] = incoming
        session["state"] = "phone"; save_session(sender, session)
        greet = GREET.get(lang, "नमस्ते")
        msg.body(f"{greet} *{incoming}* 👋\n\n{PHONE_PROMPT.get(lang, PHONE_PROMPT['hi'])}")

    # Phone
    elif state == "phone":
        if not re.match(r'^[6-9]\d{9}$', incoming):
            msg.body(WRONG_PHONE.get(lang, WRONG_PHONE["hi"]))
        else:
            session["data"]["phone"] = incoming
            session["state"] = "district"; save_session(sender, session)
            msg.body(DISTRICT_PROMPT.get(lang, DISTRICT_PROMPT["hi"]))

    # District
    elif state == "district":
        district = "" if incoming.lower() in ["skip","छोड़ें","छोड़ो","چھوڑیں"] else incoming.strip()
        session["data"]["district"] = district
        session["state"] = "desc"; save_session(sender, session)
        msg.body(DESC_PROMPT.get(lang, DESC_PROMPT["hi"]))

    # Description → file complaint
    elif state == "desc":
        findings, score = check_security(incoming)
        data     = session["data"]
        district = data.get("district", "")
        cid      = save_complaint(data["name"], data["phone"], incoming,
                                  score, "whatsapp", district)
        trigger_alert("complaint", score, name=data["name"], phone=data["phone"],
                      message=incoming, complaint_id=cid, source="whatsapp")
        tmpl = COMPLAINT_DONE.get(lang, COMPLAINT_DONE["hi"])
        dist_line = f"\n📍 {district}" if district else ""
        msg.body(tmpl.format(cid=f"{cid:04d}", name=data["name"],
                             phone=data["phone"]) + dist_line)
        reset_session(sender, lang)

    return str(resp)


@app.route("/health")
def health():
    return {"status": "✅ चालू", "version": "3.0",
            "languages": 6, "scam_db": get_db_stats()}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🛡️ Bot v3.0 — Port {port} | 6 Languages")
    app.run(debug=False, host="0.0.0.0", port=port)
