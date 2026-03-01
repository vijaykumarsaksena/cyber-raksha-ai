"""
security_engine.py  — Advanced Edition v3.0
─────────────────────────────────────────────────────────────
Cyber-Raksha का उन्नत सुरक्षा इंजन।

✅ Feature 1 — URL Safety Check (VirusTotal API)
✅ Feature 2 — Phone Number Reputation
✅ Feature 3 — Fake Bank SMS Detection
✅ Feature 4 — Deepfake / Tampered Image Detection (ELA)
✅ Feature 5 — ML-based Weighted Scoring Model
"""

import re, os, math, json
import urllib.request, urllib.parse
from typing import Optional

# ══════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

FRAUD_KEYWORDS = [
    # ── English — Financial scams ──────────────────────────
    "lottery","prize","otp","kbc","gift","lucky draw","luckydraw",
    "account block","account suspended","account deactivated",
    "kyc","kyc update","kyc expired","kyc pending","verify now",
    "claim your prize","free recharge","click here","winner",
    "congratulations you won","you are selected","reward points",
    "cashback offer","investment opportunity","double your money",
    "guaranteed return","guaranteed profit","100% profit",
    "act now","limited time offer","offer expires","link expires",
    "refund pending","tax refund","income tax notice","it department",
    "courier held","custom duty pending","parcel held",
    "job offer","work from home","earn daily","part time job",
    "data entry job","earn 500 daily","500 per day",
    "crypto","bitcoin","nft","trading signal","forex trading",
    "sextortion","obscene video","intimate video","leak your video",
    "aadhaar link","pan link","sim upgrade","sim block","sim swap",
    "screen share","anydesk","teamviewer","remote access",
    "loan approved","pre-approved loan","zero interest loan",
    "insurance claim","policy lapse","policy expired",
    # ── English — Impersonation ────────────────────────────
    "rbi notice","sebi alert","cyber crime police","cbi inquiry",
    "microsoft support","apple helpdesk","google security",
    "amazon lucky winner","flipkart winner",
    "pm kisan","pm awas yojana","government scheme",
    # ── हिंदी — Financial ─────────────────────────────────
    "जीतो","इनाम","ओटीपी","पैसे","शेयर करें","तुरंत","अभी क्लिक",
    "लॉटरी","मुफ्त","इनामी","खाता बंद","केवाईसी","सत्यापन","दोगुना",
    "निवेश करें","घर बैठे कमाएं","क्रिप्टो","वीडियो वायरल",
    "अश्लील वीडियो","ब्लैकमेल","स्क्रीन शेयर करें",
    "लिंक क्लिक करें","ऑफर खत्म होगा","अंतिम मौका",
    "लोन मंजूर","बीमा दावा","पॉलिसी बंद",
    # ── भोजपुरी / मगही patterns ──────────────────────────
    "ओटीपी बताईं","पईसा डबल","इनाम मिलल","खाता बंद होई",
    "केवाईसी करीं","जीत गइल बानी","ओटीपी बताओ","जीत गेलो",
    # ── उर्दू patterns ────────────────────────────────────
    "او ٹی پی","یقینی منافع","اکاؤنٹ بند","کے وائی سی",
]

RISK_LEVELS = [
    (0,  "सुरक्षित",       "✅"),
    (2,  "संदिग्ध",        "⚠️"),
    (4,  "खतरनाक",        "🚨"),
    (7,  "अत्यंत खतरनाक", "🔴"),
]

WEIGHTS = {
    "keyword":          1.0,
    "url":              1.5,
    "phone":            0.8,
    "upi":              1.2,
    "amount":           0.6,
    "bank_pattern":     2.5,   # ↑ raised
    "url_malicious":    3.5,   # ↑ raised
    "phone_scam":       2.8,   # ↑ raised
    "urgency":          1.4,   # ↑ raised
    "impersonation":    2.5,   # ↑ raised
    "remote_access":    3.0,   # NEW — AnyDesk/TeamViewer
    "sextortion":       4.0,   # NEW — highest threat
    "db_match":         2.0,   # NEW — scam DB hit
}

BANK_NAMES = [
    "sbi","hdfc","icici","axis","kotak","pnb","bob","canara",
    "union bank","yes bank","idfc","rbl","स्टेट बैंक","एचडीएफसी","आईसीआईसीआई",
]

FAKE_BANK_PATTERNS = [
    r'otp\s+(?:share|dena|send|do\s+not\s+share)',
    r'(?:account|card)\s+(?:block|suspend|deactivat)',
    r'(?:खाता|कार्ड)\s+(?:बंद|ब्लॉक|निष्क्रिय)',
    r'refund\s+of\s+(?:rs|₹|inr)\.?\s*[\d,]+\s+(?:pending|process)',
    r'kyc\s+(?:update|expire|pending|complete)',
    r'(?:केवाईसी|kyc)\s+(?:अपडेट|पूरा|समाप्त)',
    r'neft\s+(?:transfer|txn)\s+(?:failed|on\s+hold|pending)',
]

URGENCY_PHRASES = [
    r'\b(?:within\s+24\s+hours?|within\s+\d+\s+hours?)\b',
    r'\b(?:last\s+chance|final\s+notice|immediate(?:ly)?|asap)\b',
    r'\b(?:expire[sd]?\s+(?:today|tomorrow|soon))\b',
    r'(?:24\s+घंटे|अंतिम\s+मौका|तुरंत\s+कार्रवाई)',
    r'\b(?:act\s+now|respond\s+immediately|do\s+not\s+ignore)\b',
]

IMPERSONATION_PATTERNS = [
    r'\b(?:rbi|reserve\s+bank|sebi|income\s+tax|it\s+department)\b',
    r'\b(?:cbi|police|cyber\s+crime|court|judge)\b',
    r'\b(?:pm\s+(?:kisan|awas|modi)|government\s+scheme)\b',
    r'(?:आरबीआई|सेबी|आयकर\s+विभाग|साइबर\s+पुलिस)',
    r'\b(?:microsoft|apple|google|amazon|flipkart)\s+(?:support|team|helpdesk)\b',
]


# ══════════════════════════════════════════════════════════
#  FEATURE 1 — URL Safety Check
# ══════════════════════════════════════════════════════════

def check_url_virustotal(url: str) -> dict:
    """VirusTotal API से URL जाँचें।"""
    if not VIRUSTOTAL_API_KEY:
        return {"status": "no_key", "safe": True, "vendors_flagged": 0}
    try:
        data = urllib.parse.urlencode({"url": url}).encode()
        req  = urllib.request.Request(
            "https://www.virustotal.com/api/v3/urls", data=data,
            headers={"x-apikey": VIRUSTOTAL_API_KEY,
                     "Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            resp = json.loads(r.read())
        analysis_id = resp["data"]["id"]
        import time; time.sleep(2)
        req2 = urllib.request.Request(
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
            headers={"x-apikey": VIRUSTOTAL_API_KEY}
        )
        with urllib.request.urlopen(req2, timeout=8) as r2:
            result = json.loads(r2.read())
        stats = result["data"]["attributes"]["stats"]
        mal = stats.get("malicious", 0)
        sus = stats.get("suspicious", 0)
        return {
            "status": "checked", "safe": mal == 0 and sus == 0,
            "malicious": mal, "suspicious": sus,
            "vendors_flagged": mal + sus,
            "permalink": f"https://www.virustotal.com/gui/url/{analysis_id}",
        }
    except Exception as e:
        return {"status": "error", "safe": True, "vendors_flagged": 0, "error": str(e)}


def check_url_heuristic(url: str) -> dict:
    """Internet के बिना URL की heuristic जाँच।"""
    risk_score = 0
    flags = []

    bad_tlds = ['.tk','.ml','.cf','.ga','.gq','.xyz','.top','.loan','.click','.online','.site']
    if any(url.lower().endswith(t) or f'{t}/' in url.lower() for t in bad_tlds):
        risk_score += 2; flags.append("संदिग्ध domain extension")

    if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        risk_score += 3; flags.append("IP address as domain")

    shorteners = ['bit.ly','tinyurl','goo.gl','t.co','ow.ly','short.io','rb.gy','cutt.ly']
    if any(s in url.lower() for s in shorteners):
        risk_score += 1; flags.append("URL shortener")

    lookalikes = {
        'sbi':['sb1','sbl','s-bi'],'hdfc':['hdfcc','hdfcbank.net'],
        'icici':['icicl','icicii'],'paytm':['paytmm','pay-tm'],
    }
    for brand, fakes in lookalikes.items():
        if any(f in url.lower() for f in fakes):
            risk_score += 3; flags.append(f"Lookalike domain ({brand})")

    domain = re.sub(r'https?://', '', url).split('/')[0]
    if domain.count('.') > 3:
        risk_score += 1; flags.append("Excessive subdomains")

    bad_words = ['login','verify','secure','update','confirm','otp','kyc','reward']
    found = [w for w in bad_words if w in url.lower()]
    if found:
        risk_score += len(found); flags.append(f"Suspicious keywords: {', '.join(found)}")

    if url.startswith('http://'):
        risk_score += 1; flags.append("HTTP (not encrypted)")

    return {"status":"heuristic","safe":risk_score==0,"risk_score":risk_score,
            "flags":flags,"vendors_flagged":risk_score}


# ══════════════════════════════════════════════════════════
#  FEATURE 2 — Phone Number Reputation
# ══════════════════════════════════════════════════════════

def check_phone_reputation(phone: str) -> dict:
    """Phone number reputation check करें।"""
    p = re.sub(r'[\s\-\(\)\+]', '', phone)
    flags = []; risk_score = 0

    if p.startswith('92') and len(p) == 12:
        risk_score += 3; flags.append("Pakistan number — KBC fraud में आम")
    elif p.startswith('1') and len(p) == 11:
        risk_score += 2; flags.append("US number — lottery fraud में उपयोग")
    elif p.startswith('44') and len(p) == 12:
        risk_score += 2; flags.append("UK number — romance fraud में उपयोग")

    for pattern in [r'^140\d{7}$', r'^160\d{7}$', r'^1800\d{6,7}$']:
        if re.match(pattern, p):
            risk_score += 3; flags.append("TRAI-reported spam range"); break

    if re.search(r'(\d)\1{5,}', p):
        risk_score += 2; flags.append("Repeated digits — fake number")
    if re.search(r'(?:0123456789|9876543210)', p):
        risk_score += 2; flags.append("Sequential digits — fake")

    return {"phone":p, "risk_score":risk_score,
            "is_scam":risk_score>=3, "flags":flags, "safe":risk_score==0}


# ══════════════════════════════════════════════════════════
#  FEATURE 3 — Fake Bank SMS Detection
# ══════════════════════════════════════════════════════════

def detect_fake_bank_sms(text: str) -> dict:
    """Fake Bank SMS detect करें।"""
    tl = text.lower()
    flags = []; risk_score = 0
    bank_found = next((b.upper() for b in BANK_NAMES if b in tl), None)

    if not bank_found:
        return {"is_fake":False,"risk_score":0,"flags":[],"bank":None,"safe":True}

    for pattern in FAKE_BANK_PATTERNS:
        if re.search(pattern, tl):
            risk_score += 2; flags.append(f"Suspicious pattern detected")

    spoofing = [
        (r'(?:dear|dearest)\s+(?:customer|user)', "Generic salutation — असली bank आपका नाम जानता है"),
        (r'click\s+(?:here|link|below)\s+to\s+(?:verify|update|login)', "Phishing link instruction"),
        (r'call\s+(?:us|now)\s+(?:at|on)\s+[6-9]\d{9}', "Private mobile number दिया"),
        (r'(?:your\s+)?net\s*banking\s+(?:will\s+be\s+)?(?:block|suspend)', "Fake blocking threat"),
    ]
    for pat, desc in spoofing:
        if re.search(pat, tl):
            risk_score += 2; flags.append(desc)

    if re.search(r'(?:share|provide|send|बताएं)\s+(?:your\s+)?otp', tl):
        risk_score += 4
        flags.append("🚨 OTP माँगना — 100% FRAUD! असली बैंक कभी OTP नहीं माँगता")

    urls = re.findall(r'https?://[^\s]+', text)
    official = ['sbi.co.in','hdfcbank.com','icicibank.com','axisbank.com','kotakbank.com']
    for url in urls:
        if not any(o in url.lower() for o in official):
            risk_score += 3; flags.append(f"Non-official bank link: {url[:50]}")

    return {"bank":bank_found,"is_fake":risk_score>=3,
            "risk_score":risk_score,"flags":flags,"safe":risk_score==0}


# ══════════════════════════════════════════════════════════
#  FEATURE 4 — Image Tampering / Deepfake Detection
# ══════════════════════════════════════════════════════════

def detect_image_tampering(image_path: str) -> dict:
    """ELA + Metadata से image tampering detect करें।"""
    try:
        from PIL import Image as PILImage
        from PIL.ExifTags import TAGS
        import numpy as np, io

        flags = []; risk_score = 0
        img = PILImage.open(image_path).convert('RGB')
        w, h = img.size

        # ELA Analysis
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=95)
        buf.seek(0)
        img2 = PILImage.open(buf).convert('RGB')
        arr1 = np.array(img,  dtype=np.float32)
        arr2 = np.array(img2, dtype=np.float32)
        diff = np.abs(arr1 - arr2)
        ela_mean = float(diff.mean())
        ela_std  = float(diff.std())
        ela_score = min(10, ela_mean * 2)

        if ela_mean > 8:
            risk_score += 3; flags.append(f"High ELA ({ela_mean:.1f}) — edited image")
        elif ela_mean > 4:
            risk_score += 1; flags.append(f"Moderate ELA ({ela_mean:.1f})")
        if ela_std > 15:
            risk_score += 2; flags.append("Inconsistent noise — AI-generated/spliced")

        # EXIF Metadata
        exif_data = {}
        try:
            raw = img._getexif()
            if raw:
                exif_data = {TAGS.get(k,k): v for k,v in raw.items()}
        except Exception:
            pass

        if not exif_data:
            risk_score += 1; flags.append("No EXIF metadata — screenshot या edited")

        sw = str(exif_data.get('Software','')).lower()
        if any(t in sw for t in ['photoshop','gimp','lightroom','facetune','snapseed']):
            risk_score += 2; flags.append(f"Editing tool: {sw}")

        date_o = exif_data.get('DateTimeOriginal','')
        date_m = exif_data.get('DateTime','')
        if date_o and date_m and date_o != date_m:
            risk_score += 1; flags.append(f"Date mismatch: {date_o} vs {date_m}")

        # Resolution check (GAN typical sizes)
        if w % 256 == 0 and h % 256 == 0 and w >= 512:
            risk_score += 1; flags.append(f"AI-typical resolution ({w}x{h})")

        return {
            "tampered":   risk_score >= 3,
            "ela_score":  round(ela_score, 2),
            "ela_mean":   round(ela_mean, 2),
            "risk_score": risk_score,
            "confidence": min(99, risk_score * 15),
            "flags":      flags,
            "size":       f"{w}x{h}",
            "has_exif":   bool(exif_data),
        }
    except ImportError:
        return {"tampered":False,"flags":["PIL/numpy नहीं है"],"risk_score":0,
                "ela_score":0,"confidence":0}
    except Exception as e:
        return {"tampered":False,"flags":[f"Error: {e}"],"risk_score":0,
                "ela_score":0,"confidence":0}


# ══════════════════════════════════════════════════════════
#  FEATURE 5 — ML-based Weighted Scoring
# ══════════════════════════════════════════════════════════

def compute_ml_score(raw_findings: list,
                     url_results: list   = None,
                     phone_results: list = None,
                     bank_result: dict   = None) -> dict:
    """Weighted ensemble scoring model।"""
    weighted_sum = 0.0
    breakdown = {}
    evidence = []

    # Base findings
    type_counts = {}
    for ftype, _ in raw_findings:
        type_counts[ftype] = type_counts.get(ftype, 0) + 1

    for ftype, count in type_counts.items():
        w = WEIGHTS.get(ftype, 1.0)
        contrib = w * (1 + math.log(count) if count > 1 else 1)
        weighted_sum += contrib
        breakdown[ftype] = round(contrib, 2)

    # URL results
    if url_results:
        for ur in url_results:
            vf = ur.get("vendors_flagged", 0)
            if vf > 0:
                c = WEIGHTS["url_malicious"] * min(vf / 5, 3)
                weighted_sum += c
                breakdown["url_malicious"] = round(c, 2)
                evidence.append(f"Malicious URL ({vf} vendors)")
            elif ur.get("risk_score", 0) > 0:
                c = ur["risk_score"] * 0.5
                weighted_sum += c

    # Phone results
    if phone_results:
        for pr in phone_results:
            if pr.get("is_scam"):
                c = WEIGHTS["phone_scam"]
                weighted_sum += c
                breakdown["phone_scam"] = round(c, 2)
                evidence.append(f"Scam phone: {pr['phone']}")

    # Bank SMS
    if bank_result and bank_result.get("is_fake"):
        c = WEIGHTS["bank_pattern"] * max(bank_result["risk_score"] / 3, 1)
        weighted_sum += c
        breakdown["bank_sms"] = round(c, 2)
        evidence.append(f"Fake bank SMS ({bank_result.get('bank','')})")

    # Urgency + Impersonation combo multiplier
    if breakdown.get("urgency") and breakdown.get("impersonation"):
        weighted_sum *= 1.3
        evidence.append("Urgency + Impersonation combo (×1.3)")

    # Sigmoid → probability
    probability = round(1 / (1 + math.exp(-0.4 * (weighted_sum - 5))) * 100, 1)
    ml_score    = round(min(weighted_sum, 10), 2)

    if probability >= 85:   verdict = "🔴 FRAUD — अत्यंत उच्च संभावना"
    elif probability >= 65: verdict = "🚨 संभावित FRAUD"
    elif probability >= 40: verdict = "⚠️ संदिग्ध — सावधान रहें"
    elif probability >= 20: verdict = "🟡 थोड़ा संदिग्ध"
    else:                   verdict = "✅ सुरक्षित प्रतीत होता है"

    return {"ml_score":ml_score,"probability":probability,"verdict":verdict,
            "breakdown":breakdown,"evidence":evidence,"raw_total":round(weighted_sum,2)}


# ══════════════════════════════════════════════════════════
#  URGENCY & IMPERSONATION
# ══════════════════════════════════════════════════════════

def detect_urgency(text: str) -> list:
    findings = []
    for p in URGENCY_PHRASES:
        if re.search(p, text, re.IGNORECASE):
            findings.append(("urgency", f"⏰ Urgency tactic मिली"))
    return findings[:2]  # max 2


def detect_impersonation(text: str) -> list:
    findings = []
    for p in IMPERSONATION_PATTERNS:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            findings.append(("impersonation",
                              f"🎭 Impersonation: **{m.group(0)}**"))
    return findings[:2]


def detect_remote_access(text: str) -> list:
    """AnyDesk, TeamViewer, Screen share scam detect करें।"""
    patterns = [
        r'\b(anydesk|teamviewer|ultraviewer|airdroid|rustdesk)\b',
        r'\b(screen\s+share|remote\s+access|remote\s+control)\b',
        r'(?:स्क्रीन\s+शेयर|रिमोट\s+एक्सेस)',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return [("remote_access",
                     "⚠️ Remote Access Tool — स्क्रीन शेयर करने को मत कहें!")]
    return []


def detect_sextortion(text: str) -> list:
    """Sextortion / blackmail detect करें।"""
    patterns = [
        r'\b(sextortion|blackmail|ब्लैकमेल)\b',
        r'(obscene|intimate|adult)\s+(video|photo|image)',
        r'(video|photo)\s+(viral|leak|share\s+kar)',
        r'(वीडियो|फोटो)\s+(वायरल|लीक)',
        r'pay\s+(?:or|otherwise|else)\s+(?:i\s+will|we\s+will)',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return [("sextortion",
                     "🚨 Sextortion/Blackmail — घबराएं नहीं, 1930 पर call करें!")]
    return []


# ══════════════════════════════════════════════════════════
#  MAIN FUNCTIONS
# ══════════════════════════════════════════════════════════

def check_security(text: str, check_urls_online: bool = False) -> tuple[list, int]:
    """Standard check — backward compatible।"""
    tl = text.lower()
    findings = []
    matched_kw = set()

    # 1. Keywords
    for word in FRAUD_KEYWORDS:
        w = word.lower()
        if w in tl and w not in matched_kw:
            matched_kw.add(w)
            findings.append(("keyword", f"संदिग्ध शब्द: **{word}**"))

    # 2. URLs
    for url in re.findall(r'(https?://[^\s]+)', text):
        if check_urls_online and VIRUSTOTAL_API_KEY:
            vt = check_url_virustotal(url)
            label = "🚨 Malicious" if not vt.get("safe") else "✅ Safe"
            findings.append(("url", f"{label} URL: `{url[:60]}`"))
        else:
            h = check_url_heuristic(url)
            if not h.get("safe"):
                findings.append(("url",
                    f"संदिग्ध URL [{'; '.join(h['flags'][:2])}]: `{url[:50]}`"))
            else:
                findings.append(("url", f"Link: `{url[:60]}`"))

    UPI_HANDLES = r'(?:okaxis|oksbi|okicici|okhdfcbank|ybl|upi|paytm|gpay|ibl|axl|APB|aubank)'
    for ph in re.findall(r'\b[6-9]\d{9}\b', text):
        rep = check_phone_reputation(ph)
        label = "🚨 Scam" if rep["is_scam"] else "📱"
        findings.append(("phone", f"{label} नंबर: `{ph}`"))
    for ph in re.findall(r'\+(?:92|1|44)\d{9,11}', text):
        rep = check_phone_reputation(ph)
        findings.append(("phone", f"{'🚨' if rep['is_scam'] else '⚠️'} Int'l: `{ph}`"))
    for upi in re.findall(rf'[\w.\-]{{3,}}@{UPI_HANDLES}\b', text, re.IGNORECASE):
        findings.append(("upi", f"UPI ID: `{upi}`"))
    for amt in re.findall(r'(?:₹|rs\.?|रुपय[ेे]?)\s*[\d,]+', text, re.IGNORECASE):
        findings.append(("amount", f"राशि: `{amt.strip()}`"))

    findings.extend(detect_urgency(text))
    findings.extend(detect_impersonation(text))
    findings.extend(detect_remote_access(text))
    findings.extend(detect_sextortion(text))

    bank = detect_fake_bank_sms(text)
    if bank.get("is_fake"):
        for flag in bank["flags"][:3]:
            findings.append(("bank_pattern", f"🏦 {flag}"))
    elif bank.get("bank"):
        findings.append(("bank_pattern", f"Bank name: {bank['bank']}"))

    return findings, len(findings)


def check_security_advanced(text: str, check_urls_online: bool = False) -> dict:
    """Full advanced analysis — ML score + all features।"""
    findings, raw_score = check_security(text, check_urls_online)

    urls   = re.findall(r'(https?://[^\s]+)', text)
    phones = re.findall(r'\b(?:[6-9]\d{9}|\+(?:92|1|44)\d{9,11})\b', text)

    url_results   = [check_url_virustotal(u) if (check_urls_online and VIRUSTOTAL_API_KEY)
                     else check_url_heuristic(u) for u in urls]
    phone_results = [check_phone_reputation(p) for p in phones]
    bank_result   = detect_fake_bank_sms(text)
    ml_result     = compute_ml_score(findings, url_results, phone_results, bank_result)
    level, emoji  = get_risk_level(raw_score)

    return {
        "findings": findings, "raw_score": raw_score,
        "risk_level": level, "risk_emoji": emoji,
        "ml": ml_result,
        "url_results": url_results, "phone_results": phone_results,
        "bank_result": bank_result,
        "urls_checked": len(urls), "phones_checked": len(phones),
    }


def get_risk_level(score: int) -> tuple[str, str]:
    level_name, emoji = RISK_LEVELS[0][1], RISK_LEVELS[0][2]
    for threshold, name, em in RISK_LEVELS:
        if score >= threshold:
            level_name, emoji = name, em
    return level_name, emoji


def format_findings_for_whatsapp(findings: list) -> str:
    if not findings:
        return "कोई संदिग्ध संकेत नहीं मिला।"
    groups = {
        "keyword":       ("🔴 संदिग्ध शब्द",   []),
        "url":           ("🔗 Links",           []),
        "phone":         ("📱 नंबर",           []),
        "upi":           ("💳 UPI",            []),
        "amount":        ("💰 राशि",           []),
        "bank_pattern":  ("🏦 Bank SMS",       []),
        "urgency":       ("⏰ Urgency",        []),
        "impersonation": ("🎭 Impersonation",  []),
    }
    for ftype, txt in findings:
        clean = re.sub(r'[*`]', '', txt)
        if ftype in groups:
            groups[ftype][1].append(clean)
    lines = []
    for _, (label, items) in groups.items():
        if items:
            lines.append(f"*{label}:*")
            for item in items[:3]:
                lines.append(f"  • {item[:80]}")
    return "\n".join(lines)
