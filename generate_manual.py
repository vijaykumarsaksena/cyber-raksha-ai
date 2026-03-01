"""
generate_manual.py
────────────────────────────────────────────
Cyber-Raksha AI — हिंदी User Manual PDF
चलाएं: python3 generate_manual.py
"""

from reportlab.pdfbase        import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus        import (SimpleDocTemplate, Paragraph, Spacer,
                                       Table, TableStyle, PageBreak, HRFlowable,
                                       KeepTogether)
from reportlab.lib.pagesizes   import A4
from reportlab.lib.styles      import ParagraphStyle
from reportlab.lib.units        import cm
from reportlab.lib              import colors
from reportlab.lib.enums        import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime                  import datetime
import os

# ── Fonts ──────────────────────────────────────────────
FONT_REG  = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV',  FONT_REG))
pdfmetrics.registerFont(TTFont('DVB', FONT_BOLD))

# ── Colors ─────────────────────────────────────────────
NAVY   = colors.HexColor('#1e3c78')
BLUE   = colors.HexColor('#2a5298')
RED    = colors.HexColor('#e74c3c')
GREEN  = colors.HexColor('#27ae60')
ORANGE = colors.HexColor('#e67e22')
LGRAY  = colors.HexColor('#f4f6fb')
MGRAY  = colors.HexColor('#dde1e7')
DGRAY  = colors.HexColor('#555555')

W, H = A4

# ── Styles ─────────────────────────────────────────────
def S(name, **kw):
    defaults = dict(fontName='DV', fontSize=11, leading=16,
                    textColor=colors.black, spaceAfter=4)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

sTitle    = S('Title',   fontName='DVB', fontSize=26, leading=32,
              textColor=colors.white,    alignment=TA_CENTER, spaceAfter=6)
sSubtitle = S('Sub',     fontName='DV',  fontSize=13, leading=18,
              textColor=colors.HexColor('#c8d8ff'), alignment=TA_CENTER)
sH1       = S('H1',      fontName='DVB', fontSize=17, leading=22,
              textColor=NAVY, spaceBefore=14, spaceAfter=6)
sH2       = S('H2',      fontName='DVB', fontSize=13, leading=18,
              textColor=BLUE, spaceBefore=10, spaceAfter=4)
sH3       = S('H3',      fontName='DVB', fontSize=11, leading=15,
              textColor=DGRAY, spaceBefore=6, spaceAfter=3)
sBody     = S('Body',    fontSize=10.5,  leading=17, spaceAfter=5)
sNote     = S('Note',    fontSize=10,    leading=15, textColor=DGRAY,
              spaceAfter=4)
sBold     = S('Bold',    fontName='DVB', fontSize=10.5, leading=15)
sWarn     = S('Warn',    fontSize=10,    leading=15, textColor=RED)
sCenter   = S('Center',  fontSize=10.5,  leading=15, alignment=TA_CENTER)
sRight    = S('Right',   fontSize=9,     leading=13,
              textColor=DGRAY, alignment=TA_RIGHT)
sStep     = S('Step',    fontName='DVB', fontSize=11, leading=16,
              textColor=BLUE, spaceAfter=3)
sTOC      = S('TOC',     fontSize=11,    leading=18, spaceAfter=2)
sTOCsub   = S('TOCsub',  fontSize=10,    leading=16, leftIndent=16,
              textColor=DGRAY, spaceAfter=1)

# ── Helpers ────────────────────────────────────────────
def P(text, style=None):
    return Paragraph(text, style or sBody)

def HR(color=MGRAY, thickness=0.8):
    return HRFlowable(width='100%', thickness=thickness,
                      color=color, spaceAfter=6, spaceBefore=6)

def SP(h=0.3):
    return Spacer(1, h * cm)

def section_header(title, icon=''):
    """नीला section header box"""
    data = [[Paragraph(f'{icon}  {title}', S('SH', fontName='DVB',
             fontSize=14, leading=18, textColor=colors.white))]]
    t = Table(data, colWidths=[W - 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('PADDING',    (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return t

def info_box(text, bg=LGRAY, border=BLUE):
    data = [[P(text, S('IB', fontSize=10, leading=15))]]
    t = Table(data, colWidths=[W - 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), bg),
        ('LEFTPADDING',  (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('LINEAFTER',    (0,0), (0,-1),  3, border),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return t

def warn_box(text):
    return info_box(f'⚠️  {text}',
                    bg=colors.HexColor('#fff8e1'),
                    border=ORANGE)

def tip_box(text):
    return info_box(f'💡  {text}',
                    bg=colors.HexColor('#f0fff4'),
                    border=GREEN)

def step_table(steps):
    """numbered step list"""
    data = []
    for i, (title, desc) in enumerate(steps, 1):
        data.append([
            Paragraph(f'<b>{i}</b>', S('Num', fontName='DVB', fontSize=13,
                       textColor=BLUE, alignment=TA_CENTER)),
            Paragraph(f'<b>{title}</b><br/>{desc}',
                      S('SD', fontSize=10, leading=15)),
        ])
    t = Table(data, colWidths=[1.2*cm, W - 5.2*cm])
    t.setStyle(TableStyle([
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (1,0), (1,-1),  8),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
    ]))
    return t

def two_col(left_items, right_items, header_left='', header_right=''):
    """दो-स्तंभ table"""
    rows = []
    if header_left:
        rows.append([
            Paragraph(header_left, sBold),
            Paragraph(header_right, sBold),
        ])
    max_len = max(len(left_items), len(right_items))
    for i in range(max_len):
        l = P(left_items[i] if i < len(left_items) else '', sNote)
        r = P(right_items[i] if i < len(right_items) else '', sNote)
        rows.append([l, r])
    t = Table(rows, colWidths=[(W-4*cm)/2]*2)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  LGRAY) if header_left else ('',),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    return t

# ══════════════════════════════════════════════════════
#  PAGE TEMPLATES
# ══════════════════════════════════════════════════════
def cover_page(canvas, doc):
    canvas.saveState()
    # background gradient (navy → blue)
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)

    # decorative circle
    canvas.setFillColor(colors.HexColor('#ffffff10'))
    canvas.circle(W - 60, H - 60, 180, fill=1, stroke=0)
    canvas.circle(60, 80, 100, fill=1, stroke=0)

    # top strip
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 12, W, 12, fill=1, stroke=0)

    # bottom strip + helpline
    canvas.setFillColor(RED)
    canvas.rect(0, 0, W, 42, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont('DVB', 14)
    canvas.drawCentredString(W/2, 14, 'साइबर हेल्पलाइन: 1930  |  cybercrime.gov.in')

    canvas.restoreState()


def normal_page(canvas, doc):
    canvas.saveState()
    # header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 36, W, 36, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont('DVB', 10)
    canvas.drawString(2*cm, H - 24, '🛡️  Cyber-Raksha AI — उपयोगकर्ता मार्गदर्शिका')
    canvas.setFont('DV', 9)
    canvas.drawRightString(W - 2*cm, H - 24, f'पृष्ठ {doc.page}')

    # footer
    canvas.setFillColor(MGRAY)
    canvas.rect(0, 0, W, 28, fill=1, stroke=0)
    canvas.setFillColor(DGRAY)
    canvas.setFont('DV', 8)
    canvas.drawCentredString(W/2, 10,
        'KDSP बिहार | डेवलपर: V K SAKSENA | साइबर हेल्पलाइन: 1930')
    canvas.restoreState()


# ══════════════════════════════════════════════════════
#  CONTENT
# ══════════════════════════════════════════════════════
def build_manual(output_path: str):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
    )

    story = []

    # ── COVER PAGE ────────────────────────────────────
    story.append(Spacer(1, 3.5*cm))
    story.append(P('🛡️', S('Icon', fontSize=52, alignment=TA_CENTER,
                             textColor=colors.white)))
    story.append(SP(0.3))
    story.append(P('साइबर-रक्षा AI', sTitle))
    story.append(P('Cyber-Raksha Artificial Intelligence', sSubtitle))
    story.append(SP(0.5))
    story.append(P('उपयोगकर्ता मार्गदर्शिका', S('ManSub', fontName='DVB',
                    fontSize=16, leading=22, textColor=colors.HexColor('#a8c4ff'),
                    alignment=TA_CENTER)))
    story.append(SP(0.3))
    story.append(P('User Manual v2.4', S('Ver', fontSize=11,
                    textColor=colors.HexColor('#7aa8ff'), alignment=TA_CENTER)))
    story.append(SP(2.5))
    # info table on cover
    cov_data = [
        ['संस्था:', 'Kashyap Digital Service Point (KDSP) बिहार'],
        ['डेवलपर:', 'V K SAKSENA'],
        ['संस्करण:', f'v2.4 — {datetime.now().strftime("%B %Y")}'],
        ['हेल्पलाइन:', '1930 (24×7 उपलब्ध)'],
    ]
    ct = Table(cov_data, colWidths=[3.5*cm, 9*cm])
    ct.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'DVB'),
        ('FONTNAME',     (1,0), (1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 11),
        ('TEXTCOLOR',    (0,0), (0,-1),  colors.HexColor('#a8c4ff')),
        ('TEXTCOLOR',    (1,0), (1,-1),  colors.white),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, colors.HexColor('#ffffff30')),
        ('ALIGN',        (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(ct)
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ─────────────────────────────
    story.append(SP(0.5))
    story.append(P('📋 विषय-सूची', sH1))
    story.append(HR(NAVY, 1.5))
    story.append(SP(0.2))

    toc_items = [
        ('1.', 'परिचय — Cyber-Raksha क्या है?', False),
        ('2.', 'Login कैसे करें', False),
        ('3.', 'मैसेज की सुरक्षा जाँच', False),
        ('  3.1', 'टेक्स्ट मैसेज जाँचना', True),
        ('  3.2', 'स्क्रीनशॉट से जाँचना', True),
        ('  3.3', 'जोखिम स्तर समझें', True),
        ('4.', 'पुलिस शिकायत PDF बनाएं', False),
        ('5.', 'WhatsApp Bot उपयोग करें', False),
        ('6.', 'साइबर जागरूकता क्विज़', False),
        ('7.', 'Analytics Dashboard', False),
        ('8.', 'Alert System सेटअप', False),
        ('9.', 'Admin सेटिंग', False),
        ('10.', 'सामान्य समस्याएं और समाधान', False),
        ('11.', 'ज़रूरी हेल्पलाइन नंबर', False),
    ]
    for num, title, sub in toc_items:
        style = sTOCsub if sub else sTOC
        story.append(P(f'<b>{num}</b>   {title}', style))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 1. परिचय
    # ══════════════════════════════════════════════════
    story.append(section_header('1. परिचय — Cyber-Raksha क्या है?', '🛡️'))
    story.append(SP(0.3))
    story.append(P(
        'Cyber-Raksha AI एक हिंदी भाषा में बना साइबर सुरक्षा उपकरण है जो '
        'आम नागरिकों को ऑनलाइन फ्रॉड से बचाने के लिए बनाया गया है। '
        'यह ऐप KDSP बिहार द्वारा विकसित किया गया है।'
    ))
    story.append(SP(0.2))

    feat_data = [
        ['🔍 सुरक्षा जाँच',   'फ्रॉड मैसेज और स्क्रीनशॉट की तुरंत जाँच'],
        ['📄 PDF रिपोर्ट',    'पुलिस शिकायत के लिए हिंदी PDF बनाएं'],
        ['📱 WhatsApp Bot',   'WhatsApp पर सीधे मैसेज भेजकर जाँच करें'],
        ['🔔 Alert System',   'खतरनाक मैसेज मिलने पर Email/SMS तुरंत आए'],
        ['📊 Analytics',      'सभी शिकायतें और स्कैन का विश्लेषण देखें'],
        ['🎮 क्विज़',          '6 सवालों से अपनी जागरूकता जाँचें'],
    ]
    ft = Table(feat_data, colWidths=[4.5*cm, W-8.5*cm])
    ft.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'DVB'),
        ('FONTNAME',     (1,0), (1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 10.5),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('BACKGROUND',   (0,0), (-1,0),  LGRAY),
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [colors.white, LGRAY]),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(ft)
    story.append(SP(0.3))
    story.append(warn_box(
        'यह ऐप जागरूकता के लिए है। किसी भी फ्रॉड में तुरंत 1930 डायल करें।'
    ))

    # ══════════════════════════════════════════════════
    # 2. Login
    # ══════════════════════════════════════════════════
    story.append(SP(0.5))
    story.append(section_header('2. Login कैसे करें', '🔐'))
    story.append(SP(0.3))
    story.append(P(
        'ऐप खोलते ही Login पेज दिखेगा। Admin username और password डालें।'
    ))
    story.append(SP(0.2))
    story.append(step_table([
        ('Username डालें', 'Admin ने जो username दिया हो वो टाइप करें।'),
        ('Password डालें', 'Password टाइप करें (अक्षर नहीं दिखेंगे — सुरक्षित है)।'),
        ('"Login करें" दबाएं', 'सही होने पर मुख्य ऐप खुल जाएगा।'),
        ('पहली बार?', 'KDSP Admin से username/password लें। Default password login के बाद बदलें।'),
    ]))
    story.append(SP(0.2))
    story.append(tip_box(
        'पासवर्ड भूल गए? KDSP Admin से संपर्क करें। वे database से reset कर सकते हैं।'
    ))

    # ══════════════════════════════════════════════════
    # 3. सुरक्षा जाँच
    # ══════════════════════════════════════════════════
    story.append(SP(0.5))
    story.append(section_header('3. मैसेज की सुरक्षा जाँच', '🔍'))
    story.append(SP(0.3))
    story.append(P(
        '"🔍 स्कैन" tab खोलें। दो तरीकों से जाँच कर सकते हैं:'
    ))

    # 3.1 टेक्स्ट
    story.append(SP(0.2))
    story.append(P('3.1  टेक्स्ट मैसेज जाँचना', sH2))
    story.append(step_table([
        ('"✍️ टेक्स्ट" चुनें', 'Radio button पर क्लिक करें।'),
        ('मैसेज paste करें',  'संदिग्ध WhatsApp/SMS मैसेज copy करके बड़े box में paste करें।'),
        ('"🔎 जांच शुरू करें" दबाएं', 'AI कुछ ही सेकंड में जाँच करेगा।'),
        ('रिजल्ट देखें', 'हरा = सुरक्षित। लाल/नारंगी card = खतरा। हर संदिग्ध बात अलग दिखेगी।'),
    ]))

    # 3.2 स्क्रीनशॉट
    story.append(SP(0.2))
    story.append(P('3.2  स्क्रीनशॉट से जाँचना (OCR)', sH2))
    story.append(step_table([
        ('"🖼️ स्क्रीनशॉट" चुनें', 'Radio button पर क्लिक करें।'),
        ('फोटो अपलोड करें', '"Browse files" दबाएं और स्क्रीनशॉट चुनें (JPG/PNG)।'),
        ('AI पढ़ेगा', '"AI पढ़ रहा है..." दिखेगा — 5-15 सेकंड प्रतीक्षा करें।'),
        ('टेक्स्ट और रिजल्ट', 'निकाला गया टेक्स्ट और जाँच रिजल्ट दोनों दिखेंगे।'),
    ]))
    story.append(SP(0.2))
    story.append(tip_box(
        'बेहतर OCR के लिए — स्क्रीनशॉट साफ और अच्छी रोशनी में हो। '
        'धुंधली या काटी हुई इमेज में गलती हो सकती है।'
    ))

    # 3.3 जोखिम स्तर
    story.append(SP(0.2))
    story.append(P('3.3  जोखिम स्तर समझें', sH2))
    risk_data = [
        ['स्तर', 'रंग', 'Score', 'क्या करें'],
        ['✅ सुरक्षित',        'हरा',    '0',   'सामान्यतः ठीक है — फिर भी सतर्क रहें'],
        ['⚠️ संदिग्ध',        'नारंगी', '1-3', 'सावधानी से पढ़ें — किसी से confirm करें'],
        ['🚨 खतरनाक',         'लाल',    '4-5', 'जवाब न दें — 1930 पर सूचित करें'],
        ['🔴 अत्यंत खतरनाक', 'गहरा लाल','6+', 'तुरंत 1930 डायल करें — Admin को बताएं'],
    ]
    rt = Table(risk_data, colWidths=[4*cm, 2.5*cm, 2*cm, W-12.5*cm])
    rt.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'DVB'),
        ('FONTNAME',     (0,1), (-1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('BACKGROUND',   (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',    (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),
         [colors.HexColor('#f0fff4'), colors.HexColor('#fff8e1'),
          colors.HexColor('#fff0f0'), colors.HexColor('#ffe5e5')]),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
        ('ALIGN',        (2,0), (2,-1),  'CENTER'),
    ]))
    story.append(rt)

    # ══════════════════════════════════════════════════
    # 4. PDF रिपोर्ट
    # ══════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header('4. पुलिस शिकायत PDF बनाएं', '📄'))
    story.append(SP(0.3))
    story.append(P(
        '"📝 रिपोर्ट" tab खोलें। यह feature पुलिस FIR के लिए तैयार '
        'हिंदी PDF बनाता है जिसमें शिकायत ID, अलर्ट और अगले कदम होते हैं।'
    ))
    story.append(SP(0.2))
    story.append(step_table([
        ('नाम भरें',       'पीड़ित व्यक्ति का पूरा नाम लिखें।'),
        ('मोबाइल नंबर',   '10 अंकों का नंबर डालें।'),
        ('विवरण लिखें',   'क्या हुआ, कब हुआ, कितना नुकसान — सब विस्तार से लिखें।'),
        ('PDF तैयार करें', '"📄 PDF तैयार करें" दबाएं। CR-XXXX ID मिलेगी।'),
        ('Download करें',  '"📥 PDF डाउनलोड" दबाकर अपने device में save करें।'),
        ('थाने जाएं',      'PDF का printout लेकर नजदीकी थाने में जाएं।'),
    ]))
    story.append(SP(0.2))
    story.append(info_box(
        '📌  शिकायत ID (CR-XXXX) नोट करें। यही नंबर आपकी शिकायत की पहचान है। '
        'Admin Dashboard में इसी से खोजा जा सकता है।'
    ))

    # ══════════════════════════════════════════════════
    # 5. WhatsApp Bot
    # ══════════════════════════════════════════════════
    story.append(SP(0.5))
    story.append(section_header('5. WhatsApp Bot उपयोग करें', '📱'))
    story.append(SP(0.3))
    story.append(P(
        'WhatsApp Bot से घर बैठे, बिना computer के, '
        'सुरक्षा जाँच और शिकायत दर्ज कर सकते हैं।'
    ))
    story.append(SP(0.2))

    bot_data = [
        ['आप टाइप करें', 'Bot का जवाब'],
        ['hi / नमस्ते / menu', 'मुख्य मेनू दिखेगा (1/2/3/4)'],
        ['1',  'सुरक्षा जाँच mode शुरू'],
        ['[संदिग्ध मैसेज]', 'तुरंत जाँच रिजल्ट मिलेगा'],
        ['2',  'शिकायत दर्ज करने का flow शुरू'],
        ['3',  'एक साइबर सुरक्षा टिप मिलेगी'],
        ['4',  'सभी हेल्पलाइन नंबर दिखेंगे'],
        ['0 / menu', 'कभी भी मुख्य मेनू पर वापस'],
    ]
    bt = Table(bot_data, colWidths=[5*cm, W - 9*cm])
    bt.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'DVB'),
        ('FONTNAME',     (0,1), (-1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('BACKGROUND',   (0,0), (-1,0),  BLUE),
        ('TEXTCOLOR',    (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, LGRAY]),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
    ]))
    story.append(bt)
    story.append(SP(0.2))
    story.append(tip_box(
        'Bot 24×7 उपलब्ध है — रात को भी मैसेज भेज सकते हैं। '
        'हर शिकायत को CR-XXXX ID मिलती है।'
    ))

    # ══════════════════════════════════════════════════
    # 6. क्विज़
    # ══════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header('6. साइबर जागरूकता क्विज़', '🎮'))
    story.append(SP(0.3))
    story.append(P(
        '"🎮 क्विज़" tab में 6 सवाल हैं जो आपकी साइबर जागरूकता जाँचते हैं। '
        'हर सवाल के बाद सही जवाब और समझाइश मिलती है।'
    ))
    story.append(SP(0.2))
    story.append(step_table([
        ('सवाल पढ़ें',       'हर सवाल के नीचे 2 विकल्प हैं।'),
        ('जवाब चुनें',       'सही लगने वाला विकल्प click करें।'),
        ('"रिजल्ट" दबाएं',  'सभी 6 जवाब देने के बाद button दबाएं।'),
        ('Score देखें',      'कितने सही — और क्यों सही/गलत — समझाया जाएगा।'),
        ('फिर खेलें',        '"🔄 फिर खेलें" से दोबारा practice करें।'),
    ]))
    story.append(SP(0.2))

    quiz_topics = [
        'OTP फ्रॉड', 'KBC लॉटरी स्कैम',
        'Sextortion', 'नकली ऐप',
        'Aadhaar फ्रॉड', 'Online शॉपिंग फ्रॉड',
    ]
    qt_data = [[P(f'• {t}', sNote)] for t in quiz_topics]
    story.append(P('क्विज़ में ये विषय हैं:', sBold))
    story.append(SP(0.1))
    qt = Table(qt_data, colWidths=[W - 4*cm])
    qt.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), LGRAY),
        ('TOPPADDING',   (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ('LEFTPADDING',  (0,0), (-1,-1), 16),
        ('LINEBELOW',    (0,0), (-1,-2), 0.3, MGRAY),
    ]))
    story.append(qt)

    # ══════════════════════════════════════════════════
    # 7. Analytics
    # ══════════════════════════════════════════════════
    story.append(SP(0.5))
    story.append(section_header('7. Analytics Dashboard', '📊'))
    story.append(SP(0.3))
    story.append(P(
        '"📊 Analytics" tab में सभी शिकायतों और स्कैन का सारांश दिखता है। '
        'यह सिर्फ Admin को दिखता है।'
    ))
    story.append(SP(0.2))

    an_data = [
        ['कुल शिकायतें',  'अब तक दर्ज सभी शिकायतें'],
        ['आज',            'आज दर्ज शिकायतों की संख्या'],
        ['उच्च जोखिम',   'Score 4+ वाली गंभीर शिकायतें'],
        ['कुल स्कैन',     'App और WhatsApp दोनों से हुए स्कैन'],
    ]
    at = Table(an_data, colWidths=[4*cm, W - 8*cm])
    at.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'DVB'),
        ('FONTNAME',     (1,0), (1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 10.5),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [colors.white, LGRAY]),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
    ]))
    story.append(at)
    story.append(SP(0.2))
    story.append(P(
        'नीचे शिकायतों की पूरी list है जिसे CSV में download भी कर सकते हैं — '
        'Excel में खोलें और रिपोर्ट बनाएं।', sNote
    ))

    # ══════════════════════════════════════════════════
    # 8. Alert System
    # ══════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header('8. Alert System सेटअप', '🔔'))
    story.append(SP(0.3))
    story.append(P(
        'जब कोई खतरनाक मैसेज आए तो Admin को Email और SMS '
        'अपने आप मिल जाए — इसके लिए .env file में ये जानकारी डालें:'
    ))
    story.append(SP(0.2))

    env_data = [
        ['.env Variable', 'क्या डालें', 'कहाँ से मिलेगा'],
        ['ALERT_EMAIL', 'आपका Gmail address', 'Gmail account'],
        ['ALERT_EMAIL_PASS', '16-digit App Password', 'Gmail → Security → App Passwords'],
        ['ALERT_PHONE', 'Admin मोबाइल नंबर', 'अपना नंबर'],
        ['FAST2SMS_API_KEY', 'API Key', 'fast2sms.com → Dashboard'],
        ['ALERT_MIN_SCORE', 'जैसे: 3', 'कितने score पर alert चाहिए'],
    ]
    et = Table(env_data, colWidths=[4.5*cm, 4*cm, W - 12.5*cm])
    et.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'DVB'),
        ('FONTNAME',     (0,1), (-1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 9.5),
        ('BACKGROUND',   (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',    (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, LGRAY]),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
    ]))
    story.append(et)
    story.append(SP(0.2))
    story.append(step_table([
        ('Gmail App Password बनाएं',
         'Gmail → Settings → Security → 2-Step Verification → App Passwords → "Mail" चुनें → 16-digit password मिलेगा।'),
        ('Fast2SMS account बनाएं',
         'fast2sms.com पर free account बनाएं → Dev API → Key copy करें।'),
        ('.env file में save करें',
         'सभी values भरकर save करें।'),
        ('Test Alert भेजें',
         'Sidebar में "🧪 Test Alert भेजें" button दबाएं — Email और SMS आना चाहिए।'),
    ]))

    # ══════════════════════════════════════════════════
    # 9. Admin सेटिंग
    # ══════════════════════════════════════════════════
    story.append(SP(0.5))
    story.append(section_header('9. Admin सेटिंग', '⚙️'))
    story.append(SP(0.3))
    story.append(P('Sidebar (बाईं तरफ ☰ menu) में ये सेटिंग मिलती हैं:'))
    story.append(SP(0.2))

    adm_data = [
        ['🔑 पासवर्ड बदलें',   'नया पासवर्ड (8+ अक्षर) डालें और confirm करें।'],
        ['🔔 Alert Status',    'Email ✅/❌ और SMS ✅/❌ की स्थिति दिखती है।'],
        ['🧪 Test Alert',      'Setup सही है या नहीं — तुरंत जाँचें।'],
        ['✅/⚠️ PDF Status',   'हिंदी font है या नहीं — यहाँ दिखेगा।'],
        ['🚪 Logout',          'काम खत्म होने पर logout जरूर करें।'],
    ]
    adt = Table(adm_data, colWidths=[4.5*cm, W - 8.5*cm])
    adt.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'DVB'),
        ('FONTNAME',     (1,0), (1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [colors.white, LGRAY]),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
    ]))
    story.append(adt)
    story.append(SP(0.2))
    story.append(warn_box(
        'Logout करना न भूलें — खासकर shared computer पर। '
        'Session खुला रहने पर कोई भी Admin panel देख सकता है।'
    ))

    # ══════════════════════════════════════════════════
    # 10. समस्याएं और समाधान
    # ══════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header('10. सामान्य समस्याएं और समाधान', '🔧'))
    story.append(SP(0.3))

    trouble_data = [
        ['समस्या', 'संभावित कारण', 'समाधान'],
        ['Login नहीं हो रहा',
         'गलत password',
         'KDSP Admin से reset करवाएं।'],
        ['OCR में गलत टेक्स्ट',
         'धुंधली इमेज',
         'साफ स्क्रीनशॉट लें। टेक्स्ट manually भी paste कर सकते हैं।'],
        ['PDF में ? ? ? दिख रहा',
         'Hindi font नहीं है',
         'NotoSans-Regular.ttf को ऐप folder में रखें।'],
        ['Email alert नहीं आया',
         'Gmail credentials गलत',
         'App Password दोबारा generate करें और .env update करें।'],
        ['WhatsApp Bot offline',
         'Server बंद है',
         'Railway dashboard में service restart करें।'],
        ['वॉयस नहीं आई',
         'Internet नहीं है',
         'gTTS को internet चाहिए। बिना internet silent रहेगी।'],
        ['स्कैन में गलत alert',
         'Common शब्द जैसे "urgent"',
         'Context पढ़ें — हर alert 100% सही नहीं होता, human judgment ज़रूरी है।'],
    ]
    trt = Table(trouble_data, colWidths=[4*cm, 4*cm, W - 12*cm])
    trt.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'DVB'),
        ('FONTNAME',     (0,1), (-1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 9.5),
        ('BACKGROUND',   (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',    (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, LGRAY]),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(trt)

    # ══════════════════════════════════════════════════
    # 11. हेल्पलाइन
    # ══════════════════════════════════════════════════
    story.append(SP(0.5))
    story.append(section_header('11. ज़रूरी हेल्पलाइन नंबर', '📞'))
    story.append(SP(0.3))

    hl_data = [
        ['📞 1930',              'राष्ट्रीय साइबर क्राइम हेल्पलाइन',  '24×7 उपलब्ध'],
        ['🌐 cybercrime.gov.in', 'ऑनलाइन शिकायत portal',             'कभी भी'],
        ['👮 100',               'पुलिस इमरजेंसी',                    '24×7'],
        ['🏦 बैंक टोल-फ्री',    'तुरंत card block करने के लिए',       'बैंक के पीछे लिखा है'],
        ['📱 UIDAI: 1947',       'Aadhaar संबंधी शिकायत',             'सोम-शनि 9-6'],
    ]
    hlt = Table(hl_data, colWidths=[5.5*cm, W-11.5*cm, 2.5*cm])
    hlt.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'DVB'),
        ('FONTNAME',     (1,0), (-1,-1),'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 11),
        ('TEXTCOLOR',    (0,0), (0,-1),  RED),
        ('TOPPADDING',   (0,0), (-1,-1), 9),
        ('BOTTOMPADDING',(0,0), (-1,-1), 9),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [colors.white, LGRAY]),
        ('LINEBELOW',    (0,0), (-1,-2), 0.6, MGRAY),
        ('ALIGN',        (2,0), (2,-1),  'RIGHT'),
        ('TEXTCOLOR',    (2,0), (2,-1),  DGRAY),
        ('FONTSIZE',     (2,0), (2,-1),  9),
    ]))
    story.append(hlt)
    story.append(SP(0.4))

    # big helpline badge
    badge_data = [[
        P('फ्रॉड होने पर तुरंत डायल करें:', S('BL', fontSize=12, fontName='DVB',
           textColor=colors.white, alignment=TA_CENTER)),
        P('📞  1930', S('BN', fontSize=22, fontName='DVB',
           textColor=colors.white, alignment=TA_CENTER)),
    ]]
    bt2 = Table(badge_data, colWidths=[(W-4*cm)/2]*2)
    bt2.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), RED),
        ('PADDING',      (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [8]),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(bt2)

    # ── LAST PAGE: Quick Reference ─────────────────────
    story.append(PageBreak())
    story.append(P('⚡ Quick Reference Card', sH1))
    story.append(HR(NAVY, 1.5))
    story.append(SP(0.2))

    qr_data = [
        ['कार्य', 'कैसे करें'],
        ['फ्रॉड मैसेज जाँचें',   'स्कैन tab → paste → जांच शुरू करें'],
        ['स्क्रीनशॉट जाँचें',   'स्कैन tab → स्क्रीनशॉट → upload → जांच'],
        ['PDF बनाएं',            'रिपोर्ट tab → नाम/नंबर/विवरण → PDF तैयार'],
        ['WhatsApp जाँच',        'Bot को "1" → मैसेज भेजें'],
        ['शिकायत (WhatsApp)',    'Bot को "2" → नाम → नंबर → विवरण'],
        ['Tips पाएं (WA)',       'Bot को "3"'],
        ['Helpline (WA)',         'Bot को "4"'],
        ['Quiz खेलें',           'क्विज़ tab → सवाल → रिजल्ट'],
        ['CSV export',            'Analytics tab → CSV डाउनलोड'],
        ['Alert test करें',      'Sidebar → Test Alert भेजें'],
        ['Logout',                'Sidebar → 🚪 Logout'],
    ]
    qrt = Table(qr_data, colWidths=[5.5*cm, W - 9.5*cm])
    qrt.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'DVB'),
        ('FONTNAME',     (0,1), (-1,-1), 'DV'),
        ('FONTSIZE',     (0,0), (-1,-1), 10.5),
        ('BACKGROUND',   (0,0), (-1,0),  BLUE),
        ('TEXTCOLOR',    (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, LGRAY]),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 10),
        ('LINEBELOW',    (0,0), (-1,-2), 0.4, MGRAY),
    ]))
    story.append(qrt)
    story.append(SP(0.4))
    story.append(HR(NAVY))
    story.append(SP(0.2))
    story.append(P(
        f'Cyber-Raksha AI v2.4  |  KDSP बिहार  |  '
        f'डेवलपर: V K SAKSENA  |  {datetime.now().strftime("%B %Y")}',
        sCenter
    ))
    story.append(P(
        '⚠️  यह ऐप केवल जागरूकता के लिए है। कानूनी कार्यवाही के लिए '
        'नजदीकी थाने जाएं या 1930 पर कॉल करें।',
        S('Disc', fontSize=9, textColor=DGRAY, alignment=TA_CENTER)
    ))

    # ── Build ──────────────────────────────────────────
    def on_page(canvas, doc):
        if doc.page == 1:
            cover_page(canvas, doc)
        else:
            normal_page(canvas, doc)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"✅ Manual बन गया: {output_path}")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "Cyber_Raksha_User_Manual.pdf")
    build_manual(out)
