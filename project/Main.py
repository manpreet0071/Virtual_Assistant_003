import os
import sys
import json
import threading
import asyncio
import base64
from random import choice
from threading import Lock

# # --------------------------------------------------
# # PATH SETUP (CRITICAL)
# # --------------------------------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# sys.path.insert(0, BASE_DIR)
# sys.path.insert(0, BACKEND_DIR)

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------
from backend.Automation_engine import Run as AutomationEngine
from backend.chatbot import ChatBotAI, AnswerModifier
from backend.llm import ask_llm as Model
from backend.TTS import TTS
from backend.pc_control_new import perform_action as SystemAutomation
from backend.whatsapp_controller import WhatsAppController
from web_app.ui.main_window import MainWindow

import pyautogui
import mtranslate as mt
import eel
import speech_recognition as sr
from dotenv import load_dotenv, set_key

# --------------------------------------------------
# ENV & GLOBAL STATE
# --------------------------------------------------
# load_dotenv(os.path.join(BACKEND_DIR, ".env"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(ENV_PATH, override=True)

state = "Available..."
WEBCAM = False
lock = Lock()
working: list[threading.Thread] = []

InputLanguage = os.getenv("InputLanguage", "en")
Assistantname = os.getenv("AssistantName", "Assistant")
Username = os.getenv("NickName", "User")

ChatLogPath = os.path.join(BACKEND_DIR, "Data", "ChatLog.json")
os.makedirs(os.path.dirname(ChatLogPath), exist_ok=True)

professional_responses = [
    "Task completed successfully.",
    "I’ve executed your command.",
    "Automation finished.",
    "Your request has been processed."
]

# --------------------------------------------------
# UTILITIES
# --------------------------------------------------
def UniversalTranslator(text: str) -> str:
    if "en" in InputLanguage.lower():
        return text.capitalize()
    return mt.translate(text, "en", "auto").capitalize()

def QueryModifier(text: str) -> str:
    return text.strip()

# --------------------------------------------------
# CORE EXECUTION
# --------------------------------------------------
def MainExecution(query: str):
    global state

    if state != "Available...":
        return

    query = QueryModifier(UniversalTranslator(query))

    # ---------------- WHATSAPP FAST PATH ----------------
    if "whatsapp" in query.lower():
        try:
            state = "Automation..."
            result = WhatsAppController(query)

            response = (
                "Message sent successfully."
                if result.get("success")
                else "Failed to send WhatsApp message."
            )

            state = "Answering..."
            TTS(response)

        except Exception as e:
            print("❌ WhatsApp Error:", e)
            TTS("WhatsApp action failed.")

        finally:
            state = "Available..."
        return

    # ---------------- NORMAL FLOW ----------------
    state = "Thinking..."

    try:
        result = Model(query)
        print("LLM Result:", result)

        # ---------- AI ONLY ----------
        if isinstance(result, dict) and result.get("action", {}).get("type") == "none":
            answer = AnswerModifier(ChatBotAI(query))
            state = "Answering..."
            TTS(answer)
            return

        # ---------- AUTOMATION ----------
        state = "Automation..."
        command = result.get("action", {}).get("command", "")

        automation_prefixes = (
            "open ", "close ", "play ", "system ",
            "write ", "code ", "make ", "google search ", "search ",
            "youtube search ", "search on youtube ",
        )

        if command.lower().startswith(automation_prefixes):
            # 1️⃣ High-level automation (open/close/play/system/content/search)
            AutomationEngine(command)
        else:
            # 2️⃣ Everything else falls back to the general system command router
            # (whatsapp, calls, email, urls, free-form search, etc.) — this is a
            # synchronous function, so it's called directly, not via asyncio.run.
            SystemAutomation(command, raw_text=query, model_output=str(result))

        response = choice(professional_responses)

        with open(ChatLogPath, "w", encoding="utf-8") as f:
            json.dump(
                [{"role": "assistant", "content": response}],
                f,
                indent=4,
                ensure_ascii=False,
            )

        state = "Answering..."
        TTS(response)

    except Exception as e:
        print("❌ ERROR in MainExecution:", e)

    finally:
        state = "Available..."

# --------------------------------------------------
# VOICE LISTENER
# --------------------------------------------------
def voice_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    # Recognition settings
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("🎤 Voice listener started")

        while True:
            try:
                print("🎧 Listening...")

                audio = recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=10
                )

                text = recognizer.recognize_google(audio)

                if not text.strip():
                    continue

                print("You:", text)

                # ------------------------------------------
                # ALWAYS accept the next recognized command
                # ------------------------------------------
                t = threading.Thread(
                    target=MainExecution,
                    args=(text,),
                    daemon=True
                )

                t.start()
                working.append(t)

                # Remove finished threads
                working[:] = [
                    thread for thread in working
                    if thread.is_alive()
                ]

            except sr.UnknownValueError:
                # Speech was detected but not understood
                continue

            except sr.RequestError as e:
                print("❌ Speech Recognition Error:", e)

            except Exception as e:
                print("❌ Voice Error:", e)

# --------------------------------------------------
# EEL EXPOSED FUNCTIONS
# --------------------------------------------------
@eel.expose
def js_mic(text):
    t = threading.Thread(target=MainExecution, args=(text,), daemon=True)
    t.start()
    working.append(t)

@eel.expose
def js_state():
    return state

@eel.expose
def js_language():
    return InputLanguage

@eel.expose
def js_assistantname():
    return Assistantname

@eel.expose
def js_setvalues(GroqApi, AssistantName, Username):
    env_path = os.path.join(BACKEND_DIR, ".env")

    if GroqApi:
        set_key(env_path, "GROQ_API_KEY", GroqApi)
    if AssistantName:
        set_key(env_path, "AssistantName", AssistantName)
    if Username:
        set_key(env_path, "NickName", Username)

# --------------------------------------------------
# IMAGE CAPTURE
# --------------------------------------------------
@eel.expose
def js_capture(image_data):
    image_bytes = base64.b64decode(image_data.split(",")[1])
    with open(os.path.join(BASE_DIR, "capture.png"), "wb") as f:
        f.write(image_bytes)

# --------------------------------------------------
# APP START
# --------------------------------------------------
if __name__ == "__main__":
    eel.init("web")
    threading.Thread(target=voice_listener, daemon=True).start()
    eel.start("spider.html", port=8000)
