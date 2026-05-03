# ⚡ J.A.R.V.I.S. — AI Virtual Assistant

J.A.R.V.I.S. (Just A Rather Very Intelligent System) is a futuristic AI assistant inspired by the Stark Industries HUD. It leverages the **Gemini 2.5 Flash** model to provide concise, professional, and context-aware responses via text or voice.

## 🚀 Features
*   **Marvel Cinematic HUD**: A custom Streamlit UI with animated scanlines, radial glows, and a pulsing Arc Reactor.
*   **Dual-Input Mode**: Interact via text input or real-time voice recognition using `speech_recognition`.
*   **Voice Matrix**: Integrated Text-to-Speech (TTS) using Windows PowerShell or `pyttsx3` fallbacks.
*   **System Metrics**: Real-time tracking of query counts, system uptime, and API connection status.
*   **Neural Shortcuts**: Quick-action buttons for common commands like diagnostics, weather, and time[cite: 6].

## 🛠️ Tech Stack
*   **Frontend**: Streamlit (Python) with custom CSS injection.
*   **Brain**: Google Generative AI (Gemini 2.5 Flash).
*   **Audio**: SpeechRecognition (Input) & pyttsx3 / PowerShell (Output).
*   **Multithreading**: Background TTS processing for a non-blocking UI experience.

## 📋 Prerequisites
Before running the system, ensure you have:
1.  Python 3.9+
2.  A Google Gemini API Key.
3.  Microphone access (for voice commands).

## 🔧 Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone [https://github.com/gowthamoffll/jarvis-mark-80](https://github.com/gowthamoffll/jarvis-mark-80)
   cd jarvis-ai
