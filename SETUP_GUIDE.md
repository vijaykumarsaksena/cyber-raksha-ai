# 🛡️ Cyber-Raksha WhatsApp Bot — सेटअप गाइड

## फाइलें (एक ही फोल्डर में रखें)
```
cyber_raksha/
├── cyber_raksha_bot.py      ← WhatsApp Bot (Flask)
├── cyber_raksha_app.py      ← Streamlit ऐप
├── security_engine.py       ← साझा सुरक्षा इंजन
├── quiz_questions.json      ← क्विज़ के सवाल
├── .env                     ← Twilio credentials
└── NotoSans-Regular.ttf     ← हिंदी PDF फॉन्ट (वैकल्पिक)
```

---

## चरण 1 — लाइब्रेरी इंस्टॉल करें
```bash
pip install flask twilio python-dotenv streamlit easyocr gtts fpdf2 pillow
```

---

## चरण 2 — Twilio सेटअप

1. **Twilio Account बनाएं** → https://www.twilio.com/try-twilio
   _(Free trial में ₹0 खर्च होता है)_

2. **WhatsApp Sandbox Activate करें:**
   - Twilio Console → Messaging → Try it out → Send a WhatsApp message
   - दिए गए नंबर पर WhatsApp से **"join [sandbox-word]"** भेजें

3. **Credentials कॉपी करें:**
   - Account SID और Auth Token → Dashboard पर मिलेंगे
   - `.env.example` को `.env` नाम से सेव करें और credentials भरें

---

## चरण 3 — ngrok से Public URL बनाएं

```bash
# ngrok इंस्टॉल करें (एक बार)
# Windows: https://ngrok.com/download
# Linux/Mac:
brew install ngrok   # या
snap install ngrok

# चलाएं
ngrok http 5000
```

ngrok आपको ऐसा URL देगा:
```
https://abc123.ngrok.io  ←  यह आपका public URL है
```

---

## चरण 4 — Twilio Webhook सेट करें

1. Twilio Console → Messaging → Settings → WhatsApp Sandbox Settings
2. **"When a message comes in"** में यह URL डालें:
   ```
   https://abc123.ngrok.io/webhook
   ```
3. Method: **HTTP POST** → Save करें

---

## चरण 5 — Bot चालू करें

```bash
# Terminal 1 — Bot चलाएं
python cyber_raksha_bot.py

# Terminal 2 — Streamlit ऐप चलाएं (वैकल्पिक)
streamlit run cyber_raksha_app.py
```

---

## Bot का Flow (Test करें)

WhatsApp खोलें → Twilio Sandbox नंबर पर मैसेज भेजें:

```
आप लिखें:  hi
Bot देगा:   मुख्य मेनू (1/2/3/4)

आप लिखें:  1
Bot देगा:   "मैसेज भेजें जांच के लिए"

आप लिखें:  "आपने KBC lottery जीती है! OTP दें"
Bot देगा:   🚨 खतरा! 3 संदिग्ध संकेत मिले...
```

---

## Production के लिए (बाद में)

| सेवा | उपयोग | लागत |
|------|--------|------|
| **Railway / Render** | Server होस्टिंग | Free tier उपलब्ध |
| **Twilio WhatsApp Business** | Official नंबर | ~$5/माह |
| **MongoDB Atlas** | Database | Free tier उपलब्ध |

---

## हेल्पलाइन
- साइबर क्राइम: **1930**
- ऑनलाइन शिकायत: **cybercrime.gov.in**
- डेवलपर: **V K SAKSENA | KDSP बिहार**
