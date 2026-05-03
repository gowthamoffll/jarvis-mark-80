import streamlit as st
import google.generativeai as genai
from datetime import datetime
import re
import time
import threading
import platform
import os
import math
import tempfile
import shutil

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="J.A.R.V.I.S.",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

IS_WINDOWS = platform.system() == "Windows"

# ── Custom CSS – Tony Stark Marvel HUD ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #00050f !important;
    color: #c8e8ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 400;
}

/* ── Deep space background with subtle radial glow ── */
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,100,255,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,40,120,0.1) 0%, transparent 60%),
        #00050f !important;
}

/* ── Animated scanlines ── */
.stApp::before {
    content: "";
    pointer-events: none;
    position: fixed; inset: 0; z-index: 9998;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 3px,
        rgba(0,160,255,0.012) 3px, rgba(0,160,255,0.012) 4px
    );
    animation: scanline-drift 12s linear infinite;
}
@keyframes scanline-drift {
    0% { background-position: 0 0; }
    100% { background-position: 0 100px; }
}

/* ── Moving HUD corner brackets overlay ── */
.stApp::after {
    content: "";
    pointer-events: none;
    position: fixed; inset: 0; z-index: 9997;
    background:
        linear-gradient(90deg, rgba(0,150,255,0.07) 1px, transparent 1px),
        linear-gradient(0deg, rgba(0,150,255,0.07) 1px, transparent 1px);
    background-size: 80px 80px;
    animation: grid-move 20s linear infinite;
}
@keyframes grid-move {
    0% { background-position: 0 0; }
    100% { background-position: 80px 80px; }
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.2rem 2rem 2rem !important; max-width: 1200px !important; }

/* ══════════════════════════════════════════════
   HUD HEADER
══════════════════════════════════════════════ */
.hud-header {
    position: relative;
    display: flex; align-items: center; gap: 1.5rem;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.2rem;
    background: linear-gradient(135deg, rgba(0,20,60,0.95) 0%, rgba(0,10,30,0.98) 100%);
    border: 1px solid rgba(0,160,255,0.2);
    border-top: 2px solid rgba(0,200,255,0.6);
    clip-path: polygon(0 0, calc(100% - 30px) 0, 100% 30px, 100% 100%, 30px 100%, 0 calc(100% - 0px));
    overflow: hidden;
}

/* Animated shimmer across header */
.hud-header::before {
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(105deg, transparent 30%, rgba(0,180,255,0.04) 50%, transparent 70%);
    animation: shimmer 4s ease-in-out infinite;
}
@keyframes shimmer {
    0%,100% { transform: translateX(-100%); }
    50% { transform: translateX(100%); }
}

/* Bottom scan line on header */
.hud-header::after {
    content: "";
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #00c8ff 30%, #00eaff 50%, #00c8ff 70%, transparent);
    animation: scan-h 3s ease-in-out infinite;
}
@keyframes scan-h {
    0%,100% { opacity: 0.3; } 50% { opacity: 1; }
}

/* ── Arc Reactor ── */
.arc-reactor-wrap {
    position: relative; flex-shrink: 0;
    width: 70px; height: 70px;
    display: flex; align-items: center; justify-content: center;
}
.arc-reactor {
    width: 56px; height: 56px; border-radius: 50%;
    background:
        radial-gradient(circle at 35% 35%, #fff 0%, #80e8ff 15%, #00aaff 35%, #0044cc 60%, #001040 85%);
    box-shadow:
        0 0 0 2px rgba(0,180,255,0.4),
        0 0 0 6px rgba(0,100,255,0.15),
        0 0 20px #00aaff,
        0 0 50px rgba(0,150,255,0.5),
        0 0 100px rgba(0,100,255,0.2),
        inset 0 0 20px rgba(255,255,255,0.1);
    animation: reactor-core 3s ease-in-out infinite;
    position: relative; z-index: 2;
}
@keyframes reactor-core {
    0%,100% {
        box-shadow: 0 0 0 2px rgba(0,180,255,0.4), 0 0 0 6px rgba(0,100,255,0.15),
                    0 0 20px #00aaff, 0 0 50px rgba(0,150,255,0.5), 0 0 100px rgba(0,100,255,0.2);
    }
    50% {
        box-shadow: 0 0 0 3px rgba(0,220,255,0.7), 0 0 0 10px rgba(0,150,255,0.2),
                    0 0 35px #00ddff, 0 0 80px rgba(0,200,255,0.7), 0 0 140px rgba(0,150,255,0.35);
    }
}
/* Rotating ring around reactor */
.arc-ring {
    position: absolute; inset: -8px;
    border-radius: 50%;
    border: 1px solid transparent;
    border-top-color: rgba(0,200,255,0.7);
    border-right-color: rgba(0,200,255,0.3);
    animation: ring-spin 2s linear infinite;
}
.arc-ring-2 {
    position: absolute; inset: -14px;
    border-radius: 50%;
    border: 1px solid transparent;
    border-bottom-color: rgba(0,160,255,0.5);
    border-left-color: rgba(0,160,255,0.2);
    animation: ring-spin 3.5s linear infinite reverse;
}
@keyframes ring-spin { to { transform: rotate(360deg); } }

/* ── Title ── */
.title-block { flex: 1; }
.title-block h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.4rem; font-weight: 900;
    letter-spacing: 0.28em; line-height: 1;
    background: linear-gradient(135deg, #ffffff 0%, #80e8ff 40%, #00aaff 70%, #0066cc 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 20px rgba(0,180,255,0.6));
}
.title-block .subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem; font-weight: 500;
    letter-spacing: 0.35em; text-transform: uppercase;
    color: rgba(0,200,255,0.5); margin-top: 6px;
}
.title-block .version {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem; color: rgba(0,160,255,0.35);
    letter-spacing: 0.15em; margin-top: 2px;
}

/* ── Status badge ── */
.status-group { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.status-badge {
    padding: 5px 18px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #00ffcc;
    border: 1px solid rgba(0,255,180,0.4);
    background: linear-gradient(135deg, rgba(0,255,180,0.06), rgba(0,180,120,0.04));
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    box-shadow: 0 0 20px rgba(0,255,150,0.15), inset 0 0 10px rgba(0,255,150,0.05);
    animation: status-pulse 2.5s ease-in-out infinite;
}
@keyframes status-pulse {
    0%,100% { box-shadow: 0 0 20px rgba(0,255,150,0.15); }
    50% { box-shadow: 0 0 35px rgba(0,255,150,0.4), 0 0 60px rgba(0,255,150,0.1); }
}
.uptime-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem; color: rgba(0,160,255,0.4);
    letter-spacing: 0.12em;
}

/* ══════════════════════════════════════════════
   METRICS ROW
══════════════════════════════════════════════ */
.metrics-row { display: flex; gap: 0.6rem; margin-bottom: 1.2rem; }
.metric-card {
    flex: 1; padding: 0.8rem 1rem;
    background: linear-gradient(145deg, rgba(0,15,45,0.95), rgba(0,8,25,0.98));
    border: 1px solid rgba(0,140,255,0.15);
    border-top: none;
    position: relative; overflow: hidden;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 0px));
    transition: border-color 0.3s;
}
.metric-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00aaff, #00eeff, #00aaff, transparent);
    opacity: 0.7;
}
.metric-card::after {
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(0,150,255,0.03) 0%, transparent 60%);
}
.metric-card .label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.58rem; font-weight: 600;
    letter-spacing: 0.25em; text-transform: uppercase;
    color: rgba(0,180,255,0.45); margin-bottom: 5px;
}
.metric-card .value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem; font-weight: 700;
    color: #00ddff;
    text-shadow: 0 0 15px rgba(0,200,255,0.6), 0 0 30px rgba(0,150,255,0.3);
}
.metric-card .value.green { color: #00ffaa; text-shadow: 0 0 15px rgba(0,255,150,0.6); }
.metric-card .value.orange { color: #ff8c00; text-shadow: 0 0 15px rgba(255,140,0,0.5); }

/* ══════════════════════════════════════════════
   CHAT VIEWPORT
══════════════════════════════════════════════ */
.chat-outer {
    position: relative;
    background: linear-gradient(160deg, rgba(0,12,35,0.97), rgba(0,5,18,0.99));
    border: 1px solid rgba(0,140,255,0.18);
    margin-bottom: 0.8rem;
    clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 0px));
    overflow: hidden;
}
.chat-outer::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 5%, #0088ff 30%, #00ddff 50%, #0088ff 70%, transparent 95%);
}
.chat-outer::after {
    content: "";
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 5%, rgba(0,100,200,0.4) 50%, transparent 95%);
}
.chat-viewport {
    padding: 1.2rem 1.4rem;
    min-height: 360px; max-height: 420px; overflow-y: auto;
    scrollbar-width: thin; scrollbar-color: rgba(0,160,255,0.4) transparent;
}
.chat-viewport::-webkit-scrollbar { width: 3px; }
.chat-viewport::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00aaff, #0044cc);
    border-radius: 2px;
}

/* ── Messages ── */
.msg { display: flex; gap: 0.9rem; margin-bottom: 1.2rem; animation: msg-in 0.4s cubic-bezier(0.16,1,0.3,1); }
@keyframes msg-in {
    from { opacity: 0; transform: translateY(12px) scale(0.98); }
    to   { opacity: 1; transform: none; }
}

.msg-avatar {
    width: 36px; height: 36px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.6rem; font-weight: 700;
    clip-path: polygon(15% 0%, 85% 0%, 100% 15%, 100% 85%, 85% 100%, 15% 100%, 0% 85%, 0% 15%);
}
.msg-avatar.user {
    background: linear-gradient(135deg, rgba(255,120,0,0.25), rgba(255,80,0,0.1));
    border: 1px solid rgba(255,140,0,0.5); color: #ffaa00;
    box-shadow: 0 0 12px rgba(255,120,0,0.2);
}
.msg-avatar.jarvis {
    background: linear-gradient(135deg, rgba(0,150,255,0.2), rgba(0,80,200,0.1));
    border: 1px solid rgba(0,180,255,0.5); color: #00ddff;
    box-shadow: 0 0 12px rgba(0,150,255,0.25);
}

.msg-body { flex: 1; }
.msg-meta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem; letter-spacing: 0.12em;
    color: rgba(0,180,255,0.3); margin-bottom: 4px;
}
.msg-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem; font-weight: 500; line-height: 1.6;
    padding: 0.65rem 1rem; display: inline-block; max-width: 95%;
    position: relative;
}
.msg-text.user {
    background: linear-gradient(135deg, rgba(255,100,0,0.08), rgba(200,60,0,0.04));
    border: 1px solid rgba(255,120,0,0.22);
    border-left: 3px solid #ff8800;
    color: #ffd080;
    clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
    box-shadow: inset 0 0 20px rgba(255,100,0,0.04), 0 0 10px rgba(255,100,0,0.06);
}
.msg-text.jarvis {
    background: linear-gradient(135deg, rgba(0,120,255,0.08), rgba(0,60,180,0.04));
    border: 1px solid rgba(0,160,255,0.22);
    border-left: 3px solid #0099ff;
    color: #b8e0ff;
    clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
    box-shadow: inset 0 0 20px rgba(0,120,255,0.04), 0 0 10px rgba(0,120,255,0.06);
}

.empty-state {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 300px; gap: 1rem;
    color: rgba(0,160,255,0.25); text-transform: uppercase; letter-spacing: 0.2em;
}
.empty-icon {
    font-size: 3.5rem; opacity: 0.15;
    animation: empty-pulse 3s ease-in-out infinite;
}
@keyframes empty-pulse { 0%,100% { opacity:0.1; } 50% { opacity:0.22; } }
.empty-state .e-title { font-family: 'Orbitron', sans-serif; font-size: 0.75rem; }
.empty-state .e-sub { font-size: 0.6rem; opacity: 0.5; }

/* ── Voice listening bar ── */
.voice-listening {
    display: flex; align-items: center; gap: 0.8rem;
    padding: 0.65rem 1.2rem; margin-bottom: 0.7rem;
    background: linear-gradient(135deg, rgba(0,255,100,0.06), rgba(0,180,70,0.03));
    border: 1px solid rgba(0,255,100,0.3);
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 0px));
    color: #00ff88; font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem; letter-spacing: 0.2em;
    animation: listen-glow 1s ease-in-out infinite;
}
@keyframes listen-glow {
    0%,100% { box-shadow: 0 0 10px rgba(0,255,100,0.15); }
    50%      { box-shadow: 0 0 25px rgba(0,255,100,0.4), inset 0 0 20px rgba(0,255,100,0.05); }
}
/* Sound wave bars */
.wave-bars { display: flex; align-items: center; gap: 2px; }
.wave-bar {
    width: 3px; border-radius: 2px; background: #00ff88;
    animation: wave-anim 0.6s ease-in-out infinite;
}
.wave-bar:nth-child(1) { height: 8px;  animation-delay: 0s; }
.wave-bar:nth-child(2) { height: 16px; animation-delay: 0.1s; }
.wave-bar:nth-child(3) { height: 22px; animation-delay: 0.2s; }
.wave-bar:nth-child(4) { height: 14px; animation-delay: 0.15s; }
.wave-bar:nth-child(5) { height: 8px;  animation-delay: 0.05s; }
@keyframes wave-anim {
    0%,100% { transform: scaleY(0.4); opacity: 0.5; }
    50%      { transform: scaleY(1);   opacity: 1; }
}

/* ══════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════ */
.stTextInput > div > div > input {
    background: linear-gradient(135deg, rgba(0,15,40,0.95), rgba(0,8,25,0.98)) !important;
    border: 1px solid rgba(0,160,255,0.3) !important;
    border-bottom: 2px solid rgba(0,160,255,0.5) !important;
    border-radius: 0 !important;
    color: #c8e8ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important; font-weight: 500 !important;
    padding: 0.7rem 1rem !important;
    caret-color: #00ddff;
    letter-spacing: 0.05em;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 0 100%);
}
.stTextInput > div > div > input:focus {
    border-color: rgba(0,200,255,0.6) !important;
    border-bottom-color: #00ddff !important;
    box-shadow: 0 0 0 1px rgba(0,180,255,0.15), 0 4px 20px rgba(0,160,255,0.1) !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(0,160,255,0.25) !important; font-style: italic;
}

/* ══════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(145deg, rgba(0,20,55,0.95), rgba(0,10,30,0.98)) !important;
    border: 1px solid rgba(0,160,255,0.35) !important;
    border-top: 1px solid rgba(0,200,255,0.5) !important;
    border-radius: 0 !important;
    color: #00ccff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.62rem !important; font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    padding: 0.65rem 0.8rem !important;
    text-transform: uppercase !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    clip-path: polygon(6px 0%, 100% 0%, calc(100% - 6px) 100%, 0% 100%) !important;
    position: relative; overflow: hidden;
}
.stButton > button::before {
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(0,180,255,0.08), transparent);
    opacity: 0; transition: opacity 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(145deg, rgba(0,50,120,0.9), rgba(0,30,80,0.95)) !important;
    border-color: rgba(0,220,255,0.7) !important;
    border-top-color: #00eeff !important;
    box-shadow: 0 0 20px rgba(0,180,255,0.3), 0 0 40px rgba(0,120,255,0.1),
                inset 0 0 15px rgba(0,180,255,0.08) !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Checkbox ── */
.stCheckbox > label {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: rgba(0,200,255,0.65) !important;
    font-size: 0.82rem !important; letter-spacing: 0.12em !important;
    text-transform: uppercase;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem; letter-spacing: 0.3em; text-transform: uppercase;
    color: rgba(0,160,255,0.35); margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.section-label::after {
    content: ""; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(0,140,255,0.25), transparent);
}

/* ── Divider ── */
hr { border-color: rgba(0,120,255,0.1) !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #00aaff !important; }

/* ── Right panel card ── */
.panel-card {
    background: linear-gradient(160deg, rgba(0,15,45,0.96), rgba(0,8,22,0.98));
    border: 1px solid rgba(0,120,255,0.15);
    padding: 0.8rem;
    position: relative; overflow: hidden;
    margin-bottom: 0.5rem;
}
.panel-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,160,255,0.5), transparent);
}

/* ── Tip bar ── */
.tip-bar {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.1em;
    color: rgba(0,160,255,0.3); margin-top: 0.6rem;
    padding: 0.4rem 0.6rem;
    border-left: 2px solid rgba(0,140,255,0.2);
    background: rgba(0,100,255,0.03);
}
</style>
""", unsafe_allow_html=True)

# ── API KEY — paste your Gemini key here ─────────────────────────────────────
GEMINI_API_KEY = ""   # 👈 Replace this with your actual key

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "messages":      [],
    "jarvis_active": False,
    "query_count":   0,
    "api_key":       GEMINI_API_KEY,           # key is loaded from above constant
    "voice_output":  True,
    "is_listening":  False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Always keep the key in sync (survives reruns)
st.session_state.api_key = GEMINI_API_KEY

# ═══════════════════════════════════════════════════════════════════════════════
# ── TTS — copied and adapted from original Jarvis.py ─────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\n+', ' ', text)
    return text.strip()

def speak_windows(text: str) -> bool:
    """Windows PowerShell TTS — from original Jarvis.py"""
    try:
        import subprocess
        pwsh = shutil.which("powershell") or shutil.which("pwsh")
        if not pwsh:
            return False
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as tf:
            tfname = tf.name
            tf.write(text)
        words = len(text.split())
        timeout = int(math.ceil(max(10.0, (words / 150.0) * 60.0 * 1.6 + 4.0)))
        ps_command = (
            f"$txt = Get-Content -Raw -Encoding UTF8 '{tfname}';"
            "Add-Type -AssemblyName System.Speech;"
            "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "$synth.Rate = 1; $synth.Volume = 100;"
            "$synth.Speak($txt);"
        )
        subprocess.run([pwsh, "-NoProfile", "-Command", ps_command],
                       capture_output=True, text=True, timeout=timeout)
        try:
            os.remove(tfname)
        except Exception:
            pass
        return True
    except Exception:
        return False

def speak_pyttsx3(text: str) -> bool:
    """pyttsx3 TTS fallback — from original Jarvis.py"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
        return True
    except Exception:
        return False

def speak(text: str):
    """
    Speak in a background thread so the Streamlit UI stays responsive.
    Only fires when voice output is enabled in session state.
    """
    if not st.session_state.get("voice_output", True):
        return

    def _run():
        if IS_WINDOWS:
            if speak_windows(text):
                return
        speak_pyttsx3(text)

    threading.Thread(target=_run, daemon=True).start()

# ═══════════════════════════════════════════════════════════════════════════════
# ── VOICE INPUT — speech_recognition (from original Jarvis.py) ───────────────
# ═══════════════════════════════════════════════════════════════════════════════

def listen_once() -> str:
    """
    Opens the microphone, listens for one spoken phrase, and returns the
    recognised text. Returns an empty string on any error.
    Uses the same settings as the original Jarvis.py.
    """
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 4000
        r.dynamic_energy_threshold = True
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=8, phrase_time_limit=8)
        return r.recognize_google(audio)
    except Exception:
        return ""

# ═══════════════════════════════════════════════════════════════════════════════
# ── GEMINI AI ─────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def ask_jarvis(user_text: str, api_key: str) -> str:
    if not api_key:
        return "API key not configured, sir. Please enter your Gemini API key."
    try:
        if "time" in user_text.lower():
            return f"The current time is {datetime.now().strftime('%I:%M %p')}, sir."
        if "date" in user_text.lower():
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}, sir."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        prompt = (
            "You are J.A.R.V.I.S. — Just A Rather Very Intelligent System — from Iron Man. "
            "Reply in 1-3 short sentences. Be confident, precise, and helpful. "
            "Occasionally address the user as 'sir'. No markdown, no asterisks, no special characters.\n"
            f"User: {user_text}"
        )
        response = model.generate_content(prompt)
        reply = clean_text(response.text)
        if len(reply) > 280:
            reply = reply[:280].rsplit('.', 1)[0] + '.'
        return reply
    except Exception as e:
        return f"I encountered an error processing that request, sir. ({str(e)[:80]})"

def process_command(command: str):
    """Add user message, get Jarvis reply, speak it, update state."""
    ts = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": command, "time": ts})
    reply = ask_jarvis(command, st.session_state.api_key)
    st.session_state.messages.append({"role": "jarvis", "content": reply, "time": ts})
    st.session_state.query_count += 1
    speak(reply)   # ← Jarvis speaks the reply aloud

# ═══════════════════════════════════════════════════════════════════════════════
# ── RENDER CHAT ───────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def render_messages():
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-outer"><div class="chat-viewport">
        <div class="empty-state">
            <div class="empty-icon">⬡</div>
            <div class="e-title">Neural interface standing by</div>
            <div class="e-sub">Initialize system · then speak or type your command</div>
        </div>
        </div></div>""", unsafe_allow_html=True)
        return

    html = ""
    for msg in st.session_state.messages:
        role, content, ts = msg["role"], msg["content"], msg.get("time", "")
        if role == "user":
            html += f"""
            <div class="msg">
                <div class="msg-avatar user">YOU</div>
                <div class="msg-body">
                    <div class="msg-meta">OPERATOR · {ts}</div>
                    <div class="msg-text user">{content}</div>
                </div>
            </div>"""
        else:
            html += f"""
            <div class="msg">
                <div class="msg-avatar jarvis">JVS</div>
                <div class="msg-body">
                    <div class="msg-meta">J.A.R.V.I.S. · {ts}</div>
                    <div class="msg-text jarvis">{content}</div>
                </div>
            </div>"""
    st.markdown(f'<div class="chat-outer"><div class="chat-viewport">{html}</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ── PAGE LAYOUT ───────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

# Header
now = datetime.now()
status_text = "SYSTEMS ONLINE" if st.session_state.jarvis_active else "STANDBY MODE"
st.markdown(f"""
<div class="hud-header">
    <div class="arc-reactor-wrap">
        <div class="arc-ring-2"></div>
        <div class="arc-ring"></div>
        <div class="arc-reactor"></div>
    </div>
    <div class="title-block">
        <h1>J.A.R.V.I.S.</h1>
        <div class="subtitle">Just A Rather Very Intelligent System</div>
        <div class="version">MARK VII &nbsp;·&nbsp; STARK INDUSTRIES &nbsp;·&nbsp; BUILD 3.14.1</div>
    </div>
    <div class="status-group">
        <div class="status-badge">{status_text}</div>
        <div class="uptime-text">SYS/{now.strftime("%Y.%m.%d")} &nbsp;·&nbsp; NODE:ACTIVE</div>
    </div>
</div>""", unsafe_allow_html=True)

# Metrics
voice_color = "#00ffaa" if st.session_state.voice_output else "#ff6b35"
voice_label = "ENABLED" if st.session_state.voice_output else "DISABLED"
st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card">
        <div class="label">◈ System Time</div>
        <div class="value">{now.strftime("%H:%M:%S")}</div>
    </div>
    <div class="metric-card">
        <div class="label">◈ Stardate</div>
        <div class="value">{now.strftime("%d %b %Y")}</div>
    </div>
    <div class="metric-card">
        <div class="label">◈ Queries Processed</div>
        <div class="value">{st.session_state.query_count:04d}</div>
    </div>
    <div class="metric-card">
        <div class="label">◈ Voice Matrix</div>
        <div class="value" style="color:{voice_color}">{voice_label}</div>
    </div>
</div>""", unsafe_allow_html=True)

# Two-column layout
col_main, col_panel = st.columns([3, 1], gap="medium")

# ── RIGHT PANEL ───────────────────────────────────────────────────────────────
with col_panel:

    st.markdown('<div class="section-label">◈ System Config</div>', unsafe_allow_html=True)

    # API key status
    if st.session_state.api_key and st.session_state.api_key != "paste-your-api-key-here":
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;color:#00ffaa;font-size:0.65rem;
             letter-spacing:0.12em;padding:6px 10px;margin-bottom:8px;
             border:1px solid rgba(0,255,150,0.25);
             background:linear-gradient(135deg,rgba(0,255,150,0.05),rgba(0,180,100,0.02));
             clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 0px));">
            ◉ GEMINI LINK ESTABLISHED
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;color:#ff5533;font-size:0.62rem;
             letter-spacing:0.1em;padding:6px 10px;margin-bottom:8px;
             border:1px solid rgba(255,80,50,0.3);
             background:rgba(255,60,30,0.05);
             clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 0px));">
            ◎ NO API KEY DETECTED<br>
            <span style="opacity:0.6">Edit GEMINI_API_KEY in file</span>
        </div>""", unsafe_allow_html=True)

    # Voice toggle
    st.session_state.voice_output = st.checkbox(
        "🔊  VOICE MATRIX", value=st.session_state.voice_output
    )

    st.markdown('<div style="height:0.3rem"></div>', unsafe_allow_html=True)

    if st.button("⚡  INITIALIZE", use_container_width=True):
        st.session_state.jarvis_active = True
        ts = datetime.now().strftime("%H:%M")
        msg = "J.A.R.V.I.S. systems online. All modules nominal. How may I assist you, sir?"
        st.session_state.messages.append({"role": "jarvis", "content": msg, "time": ts})
        speak(msg)
        st.rerun()

    if st.button("⏻  POWER DOWN", use_container_width=True):
        st.session_state.jarvis_active = False
        ts = datetime.now().strftime("%H:%M")
        msg = "Initiating shutdown sequence. Goodbye, sir."
        st.session_state.messages.append({"role": "jarvis", "content": msg, "time": ts})
        speak(msg)
        st.rerun()

    if st.button("◫  PURGE LOG", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<hr style="margin:0.7rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">◈ Neural Shortcuts</div>', unsafe_allow_html=True)

    for cmd in ["What time is it?", "Tell me a joke", "Run diagnostics",
                "Weather update", "System status", "Tell me something interesting"]:
        if st.button(cmd, key=f"qc_{cmd}", use_container_width=True):
            if st.session_state.jarvis_active:
                with st.spinner("Processing..."):
                    process_command(cmd)
                st.rerun()
            else:
                st.warning("Initialize J.A.R.V.I.S. first.")

# ── MAIN CHAT PANEL ───────────────────────────────────────────────────────────
with col_main:
    st.markdown('<div class="section-label">◈ Neural Interface · Command Log</div>', unsafe_allow_html=True)

    # Animated listening bar
    if st.session_state.is_listening:
        st.markdown("""
        <div class="voice-listening">
            <div class="wave-bars">
                <div class="wave-bar"></div><div class="wave-bar"></div>
                <div class="wave-bar"></div><div class="wave-bar"></div>
                <div class="wave-bar"></div>
            </div>
            &nbsp; AUDIO INPUT ACTIVE — AWAITING COMMAND, SIR
        </div>""", unsafe_allow_html=True)

    render_messages()

    # Input row
    inp_col, send_col, mic_col = st.columns([5, 1, 1], gap="small")

    with inp_col:
        user_input = st.text_input(
            "input", placeholder="// Enter command, sir...",
            key="user_input", label_visibility="collapsed",
        )
    with send_col:
        send_clicked = st.button("► SEND", use_container_width=True)
    with mic_col:
        mic_clicked = st.button("🎤 MIC", use_container_width=True)

    # Text SEND
    if send_clicked and user_input.strip():
        if not st.session_state.jarvis_active:
            st.warning("J.A.R.V.I.S. is offline. Click INITIALIZE first.")
        else:
            with st.spinner("J.A.R.V.I.S. processing..."):
                process_command(user_input.strip())
            st.rerun()

    # MIC button
    if mic_clicked:
        if not st.session_state.jarvis_active:
            st.warning("Initialize J.A.R.V.I.S. first before using voice input.")
        else:
            st.session_state.is_listening = True
            st.rerun()

    # Actually listen
    if st.session_state.is_listening:
        with st.spinner("🎤 Audio capture active... speak now, sir"):
            recognised = listen_once()
        st.session_state.is_listening = False

        if recognised:
            with st.spinner("J.A.R.V.I.S. processing neural input..."):
                process_command(recognised)
        else:
            ts = datetime.now().strftime("%H:%M")
            err_msg = "Audio signal unclear, sir. Please repeat your command."
            st.session_state.messages.append({"role": "jarvis", "content": err_msg, "time": ts})
            speak(err_msg)
        st.rerun()

    st.markdown("""
    <div class="tip-bar">
        🎤 MIC — voice input &nbsp;·&nbsp; ► SEND — text input &nbsp;·&nbsp;
        VOICE MATRIX — toggle audio response
    </div>""", unsafe_allow_html=True)
