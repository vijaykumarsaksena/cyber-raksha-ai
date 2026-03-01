# 🛡️ Cyber-Raksha AI — Final Project Report
**KDSP बिहार | डेवलपर: V K SAKSENA**

---

## 📁 प्रोजेक्ट फाइलें

| फाइल | काम | Lines |
|------|-----|-------|
| `cyber_raksha_app.py` | Streamlit Web App (UI) | 385 |
| `cyber_raksha_bot.py` | WhatsApp Bot (Flask) | 180 |
| `alert_system.py` | Email + SMS Alerts | 222 |
| `database.py` | SQLite Database | 176 |
| `security_engine.py` | फ्रॉड जाँच इंजन | 106 |
| `font_setup.py` | हिंदी PDF Font | 38 |
| `quiz_questions.json` | 6 जागरूकता सवाल | — |
| `requirements.txt` | Python dependencies | — |
| `Procfile` | Railway deployment | — |
| **कुल** | | **~1,107 lines** |

---

## ✅ सभी Features

### 🔍 सुरक्षा जाँच
- 35+ fraud keywords (हिंदी + अंग्रेज़ी)
- संदिग्ध URL, मोबाइल नंबर, UPI ID, ₹ राशि
- 4-स्तरीय जोखिम: सुरक्षित → संदिग्ध → खतरनाक → अत्यंत खतरनाक
- OCR से स्क्रीनशॉट पढ़ना

### 📄 PDF रिपोर्ट
- हिंदी PDF (NotoSans फॉन्ट अपने आप download)
- शिकायत ID (CR-XXXX)
- पुलिस शिकायत के लिए तैयार format

### 📱 WhatsApp Bot
- Twilio + Flask
- State machine: menu → scan → complaint
- Sessions SQLite में (restart-proof)
- Railway पर 24/7 deploy

### 🔔 Alert System
- Gmail SMTP से Email
- Fast2SMS से SMS
- Background thread (UI slow नहीं)
- DB-backed deduplication (restart-proof)

### 🔐 Admin Panel
- SHA-256 password hashing
- पासवर्ड बदलने की सुविधा
- Sidebar में alert status + test button

### 📊 Analytics
- कुल शिकायतें, आज की, उच्च जोखिम
- शिकायत table + CSV export

### 🎮 क्विज़
- 6 सवाल JSON से (बिना code बदले नए जोड़ें)
- Score + explanation

### 📱 Mobile UI
- Centered layout, sidebar collapsed
- Card-style results
- Touch-friendly buttons
- 1930 helpline badge

---

## 🔒 Security Checklist

| पहलू | स्थिति |
|------|--------|
| SQL Injection | ✅ Parameterized queries |
| Password Storage | ✅ SHA-256 hash |
| Sensitive Data in Logs | ✅ MD5 hash + 60 chars preview |
| Thread Safety | ✅ check_same_thread=False |
| UPI False Positives | ✅ Specific handles only |
| Duplicate Alerts | ✅ DB-backed deduplication |
| Default Password visible | ✅ Login से हटाया |
| Bare except | ✅ Proper error handling |

---

## 🚀 Deploy करें

### Streamlit App (Streamlit Cloud — मुफ्त)
```bash
# 1. GitHub पर push करें
git add . && git commit -m "Cyber-Raksha v1.0" && git push

# 2. share.streamlit.io पर जाएं
# 3. अपना repo connect करें
# 4. Main file: cyber_raksha_app.py
```

### WhatsApp Bot (Railway — मुफ्त tier)
```bash
# railway.app → New Project → GitHub repo
# Environment Variables में .env values डालें
# Twilio Webhook: https://your-app.railway.app/webhook
```

---

## 📞 ज़रूरी Links

| सेवा | Link |
|------|------|
| साइबर हेल्पलाइन | **1930** |
| ऑनलाइन शिकायत | [cybercrime.gov.in](https://cybercrime.gov.in) |
| Twilio WhatsApp | [twilio.com](https://twilio.com) |
| Fast2SMS | [fast2sms.com](https://fast2sms.com) |
| Railway Deploy | [railway.app](https://railway.app) |
| Streamlit Cloud | [share.streamlit.io](https://share.streamlit.io) |

---

## 🗓️ Version History

| Version | क्या जोड़ा |
|---------|-----------|
| v1.0 | Basic scan + OCR + PDF |
| v1.1 | Quiz, Voice, Screenshot |
| v2.0 | SQLite DB, Admin Login, Analytics |
| v2.1 | WhatsApp Bot + Twilio |
| v2.2 | Email + SMS Alert System |
| v2.3 | Mobile-friendly UI + CSS |
| **v2.4** | **Final Review + Bug fixes** |

---

*⚠️ यह ऐप केवल जागरूकता के लिए है। किसी भी फ्रॉड में तुरंत 1930 डायल करें।*
