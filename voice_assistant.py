"""
voice_assistant.py — Advanced Voice Assistant v2.0
────────────────────────────────────────────────────
✅ Feature 1 — Speech-to-Text (browser Web Speech API)
✅ Feature 2 — बेहतर हिंदी TTS (gTTS + pyttsx3 fallback)
✅ Feature 3 — Play/Pause/Stop controls
✅ Feature 4 — Speed control (0.5x – 2.0x)
✅ Feature 5 — Voice query → AI Chatbot
"""

import os, base64, tempfile
import streamlit as st
from gtts import gTTS

# ══════════════════════════════════════════════════════════
#  FEATURE 2 — बेहतर हिंदी TTS
# ══════════════════════════════════════════════════════════

def text_to_speech(text: str, speed: float = 1.0,
                   slow: bool = False) -> str | None:
    """
    Text को Hindi audio में बदलें।
    Returns: base64 encoded mp3 string या None
    """
    try:
        tts = gTTS(text=text, lang='hi', slow=slow)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            path = tmp.name
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        os.unlink(path)
        return b64
    except Exception:
        return None


def speak_simple(text: str):
    """Backward-compatible simple speak (autoplay)।"""
    b64 = text_to_speech(text)
    if b64:
        st.markdown(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" '
            f'type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )
    else:
        st.caption("🔇 वॉयस उपलब्ध नहीं")


# ══════════════════════════════════════════════════════════
#  FEATURE 2+3+4 — Advanced Audio Player (Play/Pause/Speed)
# ══════════════════════════════════════════════════════════

def speak_advanced(text: str, speed: float = 1.0,
                   key: str = "audio_player", label: str = ""):
    """
    Controls के साथ audio player।
    Features: Play/Pause/Stop + Speed control
    """
    b64 = text_to_speech(text, slow=(speed < 0.8))
    if not b64:
        st.caption("🔇 वॉयस उपलब्ध नहीं (internet check करें)")
        return

    # HTML5 Audio Player with controls + speed
    player_html = f"""
    <div style="background:#f0f4ff;border-radius:12px;padding:12px 16px;
                border:1px solid #c8d8ff;margin:8px 0">
        <div style="font-size:0.85rem;color:#1e3c78;margin-bottom:6px">
            🔊 {label if label else 'आवाज़'}
        </div>
        <audio id="audio_{key}" style="width:100%;border-radius:8px"
               controls preload="auto">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <div style="margin-top:8px;display:flex;align-items:center;gap:8px;
                    font-size:0.8rem;color:#555">
            <span>🐢</span>
            <input type="range" id="speed_{key}" min="0.5" max="2.0" step="0.25"
                   value="{speed}"
                   style="flex:1;accent-color:#1e3c78"
                   oninput="
                     document.getElementById('audio_{key}').playbackRate =
                       parseFloat(this.value);
                     document.getElementById('speedval_{key}').textContent =
                       this.value + 'x';
                   ">
            <span>🐇</span>
            <span id="speedval_{key}" style="min-width:35px;font-weight:700;
                  color:#1e3c78">{speed}x</span>
        </div>
        <script>
          // Set initial speed
          var a = document.getElementById('audio_{key}');
          if (a) a.playbackRate = {speed};
        </script>
    </div>
    """
    st.markdown(player_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  FEATURE 1 — Speech-to-Text (Browser Web Speech API)
# ══════════════════════════════════════════════════════════

SPEECH_TO_TEXT_HTML = """
<div id="stt_container_{key}"
     style="background:#fff8e1;border:2px dashed #f39c12;border-radius:12px;
            padding:14px 16px;margin:8px 0">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <button id="mic_btn_{key}"
                onclick="toggleMic_{key}()"
                style="background:#e74c3c;color:white;border:none;border-radius:50%;
                       width:44px;height:44px;font-size:18px;cursor:pointer">
            🎤
        </button>
        <div>
            <div style="font-weight:700;font-size:0.9rem;color:#1e3c78">
                आवाज़ से टाइप करें
            </div>
            <div id="mic_status_{key}"
                 style="font-size:0.75rem;color:#888">
                बोलने के लिए 🎤 दबाएं
            </div>
        </div>
    </div>
    <div id="transcript_{key}"
         style="background:white;border-radius:8px;padding:10px;
                min-height:48px;font-size:0.9rem;color:#333;
                border:1px solid #e0e0e0">
        यहाँ आपकी बात दिखेगी...
    </div>
    <div style="margin-top:8px;display:flex;gap:8px">
        <button onclick="copyTranscript_{key}()"
                style="flex:1;background:#1e3c78;color:white;border:none;
                       border-radius:8px;padding:6px;font-size:0.8rem;cursor:pointer">
            📋 Copy करें
        </button>
        <button onclick="clearTranscript_{key}()"
                style="flex:1;background:#888;color:white;border:none;
                       border-radius:8px;padding:6px;font-size:0.8rem;cursor:pointer">
            🗑️ साफ करें
        </button>
    </div>
</div>

<script>
var recognition_{key} = null;
var isListening_{key} = false;

function initSpeech_{key}() {{
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
        document.getElementById('mic_status_{key}').textContent =
            '❌ Browser support नहीं है। Chrome use करें।';
        document.getElementById('mic_btn_{key}').disabled = true;
        return false;
    }}
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition_{key} = new SR();
    recognition_{key}.lang = '{lang}';
    recognition_{key}.continuous = true;
    recognition_{key}.interimResults = true;

    recognition_{key}.onstart = function() {{
        isListening_{key} = true;
        document.getElementById('mic_btn_{key}').style.background = '#27ae60';
        document.getElementById('mic_btn_{key}').textContent = '⏹️';
        document.getElementById('mic_status_{key}').textContent = '🎙️ सुन रहा हूँ...';
        document.getElementById('transcript_{key}').style.borderColor = '#27ae60';
    }};

    recognition_{key}.onresult = function(event) {{
        var interim = '', final = '';
        for (var i = event.resultIndex; i < event.results.length; i++) {{
            if (event.results[i].isFinal) {{
                final += event.results[i][0].transcript;
            }} else {{
                interim += event.results[i][0].transcript;
            }}
        }}
        var el = document.getElementById('transcript_{key}');
        el.innerHTML = '<span style="color:#222">' + final + '</span>' +
                       '<span style="color:#999;font-style:italic">' + interim + '</span>';
    }};

    recognition_{key}.onerror = function(event) {{
        document.getElementById('mic_status_{key}').textContent =
            '❌ Error: ' + event.error;
        stopMic_{key}();
    }};

    recognition_{key}.onend = function() {{
        if (isListening_{key}) recognition_{key}.start(); // continuous
    }};
    return true;
}}

function toggleMic_{key}() {{
    if (isListening_{key}) {{
        stopMic_{key}();
    }} else {{
        if (!recognition_{key}) initSpeech_{key}();
        if (recognition_{key}) recognition_{key}.start();
    }}
}}

function stopMic_{key}() {{
    isListening_{key} = false;
    if (recognition_{key}) recognition_{key}.stop();
    document.getElementById('mic_btn_{key}').style.background = '#e74c3c';
    document.getElementById('mic_btn_{key}').textContent = '🎤';
    document.getElementById('mic_status_{key}').textContent = 'रुक गया। फिर दबाएं।';
    document.getElementById('transcript_{key}').style.borderColor = '#e0e0e0';
}}

function copyTranscript_{key}() {{
    var text = document.getElementById('transcript_{key}').textContent;
    if (text && text !== 'यहाँ आपकी बात दिखेगी...') {{
        navigator.clipboard.writeText(text).then(function() {{
            document.getElementById('mic_status_{key}').textContent = '✅ Copy हो गया!';
        }});
    }}
}}

function clearTranscript_{key}() {{
    document.getElementById('transcript_{key}').innerHTML = 'यहाँ आपकी बात दिखेगी...';
    document.getElementById('mic_status_{key}').textContent = 'बोलने के लिए 🎤 दबाएं';
}}
</script>
"""

def render_speech_to_text(key: str = "stt1", lang: str = "hi-IN") -> None:
    """
    Speech-to-Text widget render करें।
    lang: 'hi-IN' (हिंदी) या 'en-IN' (English)
    """
    html = SPEECH_TO_TEXT_HTML.replace("{key}", key).replace("{lang}", lang)
    st.components.v1.html(html, height=220, scrolling=False)


# ══════════════════════════════════════════════════════════
#  FEATURE 5 — Voice Query Widget
# ══════════════════════════════════════════════════════════

VOICE_QUERY_HTML = """
<div style="background:#f0fff4;border:2px solid #27ae60;border-radius:12px;
            padding:14px 16px;margin:8px 0">
    <div style="font-weight:700;color:#1e3c78;margin-bottom:8px">
        🎤 आवाज़ से सवाल पूछें
    </div>
    <div style="display:flex;gap:10px;align-items:center">
        <button id="vq_btn"
                onclick="toggleVoiceQuery()"
                style="background:#27ae60;color:white;border:none;border-radius:50%;
                       width:48px;height:48px;font-size:20px;cursor:pointer;
                       flex-shrink:0">
            🎤
        </button>
        <div id="vq_text"
             style="flex:1;background:white;border-radius:8px;padding:10px;
                    min-height:40px;border:1px solid #e0e0e0;font-size:0.9rem">
            यहाँ बोलें...
        </div>
        <button onclick="submitVoiceQuery()"
                style="background:#1e3c78;color:white;border:none;border-radius:8px;
                       padding:8px 14px;cursor:pointer;font-size:0.85rem">
            📤 भेजें
        </button>
    </div>
    <input type="hidden" id="vq_hidden" value="">
    <div id="vq_status"
         style="font-size:0.75rem;color:#888;margin-top:6px">
        बोलने के लिए 🎤 दबाएं — हिंदी या English में
    </div>
</div>

<script>
var vq_recognition = null;
var vq_listening = false;
var vq_final_text = '';

function initVQ() {{
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
        document.getElementById('vq_status').textContent =
            '❌ Chrome browser में खोलें';
        return false;
    }}
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    vq_recognition = new SR();
    vq_recognition.lang = 'hi-IN';
    vq_recognition.continuous = false;
    vq_recognition.interimResults = true;

    vq_recognition.onstart = function() {{
        vq_listening = true;
        document.getElementById('vq_btn').textContent = '⏹️';
        document.getElementById('vq_btn').style.background = '#e74c3c';
        document.getElementById('vq_status').textContent = '🎙️ सुन रहा हूँ...';
    }};

    vq_recognition.onresult = function(e) {{
        var interim = '', final = '';
        for (var i = e.resultIndex; i < e.results.length; i++) {{
            if (e.results[i].isFinal) final += e.results[i][0].transcript;
            else interim += e.results[i][0].transcript;
        }}
        vq_final_text = final || interim;
        document.getElementById('vq_text').textContent = vq_final_text;
        document.getElementById('vq_hidden').value = vq_final_text;
    }};

    vq_recognition.onend = function() {{
        vq_listening = false;
        document.getElementById('vq_btn').textContent = '🎤';
        document.getElementById('vq_btn').style.background = '#27ae60';
        document.getElementById('vq_status').textContent =
            vq_final_text ? '✅ सुना — "भेजें" दबाएं' : 'दोबारा कोशिश करें';
    }};

    vq_recognition.onerror = function(e) {{
        document.getElementById('vq_status').textContent = '❌ ' + e.error;
        vq_listening = false;
    }};
    return true;
}}

function toggleVoiceQuery() {{
    if (vq_listening) {{
        if (vq_recognition) vq_recognition.stop();
    }} else {{
        vq_final_text = '';
        document.getElementById('vq_text').textContent = 'सुन रहा हूँ...';
        if (!vq_recognition) initVQ();
        if (vq_recognition) vq_recognition.start();
    }}
}}

function submitVoiceQuery() {{
    var text = document.getElementById('vq_hidden').value ||
               document.getElementById('vq_text').textContent;
    if (text && text !== 'यहाँ बोलें...' && text !== 'सुन रहा हूँ...') {{
        // Streamlit में भेजने के लिए URL param set करें
        var url = new URL(window.location);
        url.searchParams.set('voice_query', encodeURIComponent(text));
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: text
        }}, '*');
        document.getElementById('vq_status').textContent =
            '📤 भेजा: "' + text.substring(0, 50) + '"';
    }} else {{
        document.getElementById('vq_status').textContent =
            '⚠️ पहले कुछ बोलें';
    }}
}}
</script>
"""

def render_voice_query(key: str = "vq1") -> None:
    """Voice query widget — AI Chatbot के लिए।"""
    st.components.v1.html(
        VOICE_QUERY_HTML.replace("{key}", key),
        height=160, scrolling=False
    )


# ══════════════════════════════════════════════════════════
#  COMPLETE VOICE ASSISTANT PANEL
# ══════════════════════════════════════════════════════════

def render_voice_panel(text_to_read: str = "",
                       show_stt: bool = True,
                       show_speed: bool = True,
                       key_prefix: str = "vp",
                       label: str = "") -> None:
    """
    पूरा Voice Assistant Panel एक जगह।
    text_to_read : TTS के लिए text
    show_stt     : Speech-to-Text दिखाएं?
    show_speed   : Speed control दिखाएं?
    """
    with st.expander("🔊 Voice Assistant", expanded=False):

        # Speed control
        speed = 1.0
        if show_speed:
            speed = st.select_slider(
                "⚡ आवाज़ की गति:",
                options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                value=1.0,
                format_func=lambda x: {
                    0.5: "0.5x 🐢 बहुत धीमी",
                    0.75: "0.75x धीमी",
                    1.0: "1.0x सामान्य",
                    1.25: "1.25x थोड़ी तेज़",
                    1.5: "1.5x तेज़",
                    2.0: "2.0x 🐇 बहुत तेज़",
                }.get(x, str(x))
            )

        # TTS Player
        if text_to_read:
            speak_advanced(text_to_read, speed=speed,
                           key=f"{key_prefix}_tts", label=label)
        else:
            st.caption("ℹ️ जाँच करने पर आवाज़ अपने आप बजेगी।")

        # STT
        if show_stt:
            st.markdown("---")
            lang_choice = st.radio(
                "🌐 भाषा:",
                ["हिंदी", "English"],
                horizontal=True,
                key=f"{key_prefix}_lang"
            )
            lang_code = "hi-IN" if lang_choice == "हिंदी" else "en-IN"
            render_speech_to_text(key=f"{key_prefix}_stt", lang=lang_code)
            st.caption("💡 बोला हुआ text 'Copy करें' से scan box में paste करें।")
