"""
font_setup.py
─────────────────────────────────────────────
हिंदी PDF के लिए NotoSans फॉन्ट अपने आप डाउनलोड करें।
Internet न हो तो fallback (Arial) इस्तेमाल होगा।
"""

import os
import urllib.request

FONT_PATH = os.path.join(os.path.dirname(__file__), "NotoSans-Regular.ttf")

FONT_URL = (
    "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans-Regular.ttf"
)


def ensure_hindi_font() -> bool:
    """
    फॉन्ट फाइल मौजूद है? → True
    नहीं है → डाउनलोड करें → True
    डाउनलोड फेल? → False (fallback Arial)
    """
    if os.path.isfile(FONT_PATH):
        return True

    print("⬇️  NotoSans फॉन्ट डाउनलोड हो रहा है...")
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        print("✅ फॉन्ट डाउनलोड हो गया!")
        return True
    except Exception as e:
        print(f"⚠️  फॉन्ट डाउनलोड नहीं हुआ: {e}")
        print("   PDF अंग्रेज़ी (Arial) में बनेगी।")
        return False


HINDI_FONT_AVAILABLE = ensure_hindi_font()
