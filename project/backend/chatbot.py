# # =============================================
# # Chatbot.py - FINAL (WITH MODAL + REALTIME)
# # =============================================

# # ---------------- EXISTING IMPORTS ----------------
# import asyncio
# from TTS import TTS
# from llm import ask_llm
# from text_processing import prepare_speech

# from Automation_engine import Automation, Content
# from pc_control_new import perform_action
# from groq import Groq
# import json
# import datetime
# from dotenv import load_dotenv
# from os import environ
# import os
# import re

# from whatsapp_controller import WhatsAppController

# # ---------------- NEW IMPORTS ----------------
# from Modal import FirstLayerDMM
# from RealtimeSearchEngine import RealtimeSearchEngine


# # -----------------------------
# # Load environment variables
# # -----------------------------
# load_dotenv()
# NickName = environ.get('NickName', 'User')
# AssistantName = environ.get('AssistantName', 'Yui')

# # -----------------------------
# # DATA DIRECTORY
# # -----------------------------
# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
# os.makedirs(DATA_DIR, exist_ok=True)
# CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# # -----------------------------
# # Initialize Groq client (safe)
# # -----------------------------
# _groq_key = os.getenv('GroqAPI') or os.getenv('GROQ_API_KEY') or os.getenv('GroqAPIKey')
# if _groq_key:
#     client = Groq(api_key=_groq_key)
# else:
#     client = None
#     print('[Warning] Groq API key not found. LLM/Realtime features will be disabled. Set GroqAPI or GROQ_API_KEY in your environment.')

# # -----------------------------
# # Custom Instructions
# # -----------------------------
# CustomInstructions = (
#     f"You are {AssistantName}, a cute, sweet, and caring 18-year-old anime girl. "
#     f"Always address the user as {NickName} in a playful and affectionate way. "
#     "Reply in short, lively sentences so TTS can stream them quickly. "
#     "Each sentence should be self-contained, and mischievous, with kawaii-style charm. "
#     "Mix English and Hinglish naturally, add expressive sounds, emojis, and playful phrases. "
#     "Avoid long paragraphs, avoid sounding professional or robotic. "
#     "Always keep responses short and TTS-friendly."
#     "Donot use the emojis."

# )

# SystemTemplate = (
#     f"Hello, I am {NickName}. You are {AssistantName}, a professional AI chatbot.\n"
#     + CustomInstructions
# )

# SystemChatBot = [
#     {'role': 'system', 'content': SystemTemplate},
#     {'role': 'user', 'content': 'Hi'},
#     {'role': 'assistant', 'content': f'Hello {NickName}, how can I help you today?'}
# ]

# DefaultMessage = [
#     {'role': 'user', 'content': f"Hello {AssistantName}, how are you?"},
#     {'role': 'assistant', 'content': f"Welcome back {NickName}, I am doing well. How may I assist you today?"}
# ]

# # -----------------------------
# # Safe JSON Loader
# # -----------------------------
# def load_json_safe(file_path, default=None):
#     if default is None:
#         default = []
#     try:
#         with open(file_path, 'r') as f:
#             return json.load(f)
#     except:
#         with open(file_path, 'w') as f:
#             json.dump(default, f, indent=4)
#         return default

# # -----------------------------
# # Real-time Info
# # -----------------------------
# def Information():
#     now = datetime.datetime.now()
#     return (
#         f"Day: {now.strftime('%A')}\n"
#         f"Date: {now.strftime('%d')}\n"
#         f"Month: {now.strftime('%B')}\n"
#         f"Year: {now.strftime('%Y')}\n"
#         f"Time: {now.strftime('%H:%M:%S')}\n"
#     )

# # -----------------------------
# # Answer Modifier
# # -----------------------------
# def AnswerModifier(answer):
#     lines = answer.split('\n')
#     return '\n'.join(line.strip() for line in lines if line.strip())

# # -----------------------------
# # Language Detection
# # -----------------------------
# def detect_language(text):
#     if not text.strip():
#         return 'Unsupported'
#     if re.search(r'[A-Za-z]', text):
#         return 'English/Hinglish'
#     return 'Unsupported'


# # =========================================================
# # 🔥 NEW CORE INTELLIGENCE ROUTER (MODAL + REALTIME)
# # =========================================================
# def SmartRouter(prompt):
#     try:
#         decisions = FirstLayerDMM(prompt)

#         if not decisions:
#             return "⚠️ No decision made."

#         final_responses = []

#         for decision in decisions:

#             # ---------------- REALTIME ----------------
#             if decision.startswith("realtime"):
#                 query = decision.replace("realtime", "").strip()
#                 result = RealtimeSearchEngine(query)
#                 final_responses.append(result)

#             # ---------------- GENERAL (LLM) ----------------
#             elif decision.startswith("general"):
#                 query = decision.replace("general", "").strip()
#                 result = ChatBotAI(query)   # your existing brain
#                 final_responses.append(result)

#             # ---------------- AUTOMATION ----------------
#             else:
#                 # send directly to automation system
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 result = loop.run_until_complete(Automation([decision]))
#                 final_responses.append(str(result))

#         return "\n".join(final_responses)

#     except Exception as e:
#         print("Router Error:", e)
#         return "Something went wrong in SmartRouter."


# # =========================================================
# # 🔥 YOUR ORIGINAL ChatBotAI (UNCHANGED)
# # =========================================================
# def is_whatsapp_command(prompt: str) -> bool:
#     lower = prompt.lower()
#     triggers = ["send ", "message ", "call ", "video call "]
#     return any(lower.startswith(word) for word in triggers)

# def ChatBotAI(prompt):
#     try:
#         lower = prompt.lower()

#         # WHATSAPP
#         if is_whatsapp_command(prompt):
#             print("OPENING WHATSAPP")
#             result = WhatsAppController(prompt)
#             if result.get("success"):
#                 msg = f"✅ WhatsApp action performed via {result.get('method')}"
#             else:
#                 msg = f"❌ WhatsApp action failed: {result.get('error', 'Unknown error')}"
#             TTS(msg)
#             return msg

#         # AUTOMATION
#         elif lower.startswith(("open ", "search ", "play ")):
#             action_result = perform_action(prompt, raw_text=prompt)
#             if not action_result.startswith("❌"):
#                 TTS(action_result)
#             return action_result

#         # NORMAL CHAT
#         if detect_language(prompt) == 'Unsupported':
#             return "Sorry, I can only understand English or Hinglish."

#         messages = load_json_safe(CHATLOG_PATH, DefaultMessage)
#         system_msg = {
#             'role': 'system',
#             'content': f"{CustomInstructions}\nAlways reply in English/Hinglish.\n{Information()}"
#         }

#         if client is None:
#             return "LLM client not configured. Set GroqAPI or GROQ_API_KEY in your environment to enable normal chat."

#         completion = client.chat.completions.create(
#             # model='llama-3.1-8b-instant',
#             model="openai/gpt-oss-120b",
#             messages=SystemChatBot + [system_msg] + messages + [
#                 {'role': 'user', 'content': prompt}
#             ],
#             stream=True
#         )

#         answer = ''
#         for chunk in completion:
#             if getattr(chunk.choices[0].delta, 'content', None):
#                 answer += chunk.choices[0].delta.content

#         messages.append({'role': 'user', 'content': prompt})
#         messages.append({'role': 'assistant', 'content': answer})

#         with open(CHATLOG_PATH, 'w') as f:
#             json.dump(messages, f, indent=4)

#         final_answer = AnswerModifier(answer)
#         if TTS:
#             TTS(final_answer)
#         return final_answer

#     except Exception as e:
#         print(f"Error: {e}")
#         return "An error occurred."


# # =========================================================
# # 🔥 MAIN LOOP (UPDATED TO USE SMART ROUTER)
# # =========================================================
# if __name__ == '__main__':
#     print(f"=== {AssistantName} Started ===\nType 'exit' to quit.\n")

#     while True:
#         user_input = input('Enter Your Question: ').strip()

#         if user_input.lower() in ('exit', 'quit'):
#             print(f"Exiting {AssistantName}...")
#             break

#         # 🔥 USE NEW BRAIN
#         response = SmartRouter(user_input)

#         print("\n🤖:", response)


# --------------------------------------------------------------------------------------------------------
# gpt
# =============================================
# Chatbot.py - FIXED GROQ + MODAL + REALTIME
# =============================================

# ---------------- EXISTING IMPORTS ----------------
import asyncio
import json
import datetime
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from TTS import TTS
from text_processing import prepare_speech

from Automation_engine import Automation, Content
from pc_control_new import perform_action

from whatsapp_controller import WhatsAppController

# ---------------- NEW IMPORTS ----------------
from Modal import FirstLayerDMM
from RealtimeSearchEngine import RealtimeSearchEngine


# =========================================================
# PROJECT PATH
# =========================================================

# Current file:
# project_yui/project/backend/chatbot.py
#
# parents[0] = backend
# parents[1] = project
# parents[2] = project_yui

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

DATA_DIR = PROJECT_ROOT / "project" / "backend" / "Data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

CHATLOG_PATH = DATA_DIR / "ChatLog.json"


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(ENV_FILE, override=True)

print(f"[llm] Loading environment from: {ENV_FILE}")


# =========================================================
# USER / ASSISTANT SETTINGS
# =========================================================

NickName = os.getenv("NickName", "User")
AssistantName = os.getenv("AssistantName", "Yui")


# =========================================================
# GROQ CONFIGURATION
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("[llm] ERROR: GROQ_API_KEY was not found.")
    print(f"[llm] Expected .env file: {ENV_FILE}")
    client = None

else:
    GROQ_API_KEY = GROQ_API_KEY.strip()

    print("[llm] Groq API key detected.")
    print(f"[llm] API key length: {len(GROQ_API_KEY)}")

    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("[llm] Groq client initialized successfully.")

    except Exception as e:
        print(f"[llm] Failed to initialize Groq client: {e}")
        client = None


# =========================================================
# CUSTOM INSTRUCTIONS
# =========================================================

CustomInstructions = (
    f"You are {AssistantName}, a cute, sweet, and caring anime assistant. "
    f"Always address the user as {NickName}. "
    "Reply in short, lively sentences so TTS can stream them quickly. "
    "Each sentence should be self-contained. "
    "Use a playful and friendly style. "
    "Mix English and Hinglish naturally when appropriate. "
    "Do not use emojis. "
    "Avoid long paragraphs. "
    "Avoid sounding professional or robotic. "
    "Always keep responses short and TTS-friendly."
)


SystemTemplate = (
    f"Hello, I am {NickName}. "
    f"You are {AssistantName}, a professional AI chatbot.\n"
    + CustomInstructions
)


SystemChatBot = [
    {
        "role": "system",
        "content": SystemTemplate
    },
    {
        "role": "user",
        "content": "Hi"
    },
    {
        "role": "assistant",
        "content": f"Hello {NickName}, how can I help you today?"
    }
]


DefaultMessage = [
    {
        "role": "user",
        "content": f"Hello {AssistantName}, how are you?"
    },
    {
        "role": "assistant",
        "content": (
            f"Welcome back {NickName}, "
            "I am doing well. How may I assist you today?"
        )
    }
]


# =========================================================
# SAFE JSON LOADER
# =========================================================

def load_json_safe(file_path, default=None):

    if default is None:
        default = []

    file_path = Path(file_path)

    try:

        if not file_path.exists():

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)

            return default

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:

        print(f"[JSON] Error loading {file_path}: {e}")

        try:

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)

        except Exception as write_error:

            print(f"[JSON] Error creating file: {write_error}")

        return default


# =========================================================
# REAL-TIME INFORMATION
# =========================================================

def Information():

    now = datetime.datetime.now()

    return (
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )


# =========================================================
# ANSWER MODIFIER
# =========================================================

def AnswerModifier(answer):

    if not answer:
        return ""

    lines = answer.split("\n")

    return "\n".join(
        line.strip()
        for line in lines
        if line.strip()
    )


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text):

    if not text or not text.strip():
        return "Unsupported"

    if re.search(r"[A-Za-z]", text):
        return "English/Hinglish"

    return "Unsupported"


# =========================================================
# WHATSAPP COMMAND DETECTION
# =========================================================

def is_whatsapp_command(prompt: str) -> bool:

    lower = prompt.lower().strip()

    triggers = [
        "send ",
        "message ",
        "call ",
        "video call "
    ]

    return any(
        lower.startswith(word)
        for word in triggers
    )


# =========================================================
# SMART ROUTER
# =========================================================

def SmartRouter(prompt):

    try:

        decisions = FirstLayerDMM(prompt)

        if not decisions:

            return "No decision was made."

        final_responses = []

        for decision in decisions:

            decision = str(decision).strip()

            # ---------------- REALTIME ----------------

            if decision.lower().startswith("realtime"):

                query = decision[len("realtime"):].strip()

                if not query:
                    final_responses.append(
                        "I need a search query."
                    )
                    continue

                try:

                    result = RealtimeSearchEngine(query)

                    final_responses.append(
                        str(result)
                    )

                except Exception as e:

                    print(f"[Realtime] Error: {e}")

                    final_responses.append(
                        "I could not get the real-time information."
                    )


            # ---------------- GENERAL LLM ----------------

            elif decision.lower().startswith("general"):

                query = decision[len("general"):].strip()

                if not query:
                    query = prompt

                result = ChatBotAI(query)

                final_responses.append(
                    str(result)
                )


            # ---------------- AUTOMATION ----------------

            else:

                try:

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(
                        Automation([decision])
                    )

                    final_responses.append(
                        str(result)
                    )

                except Exception as e:

                    print(f"[Automation] Error: {e}")

                    final_responses.append(
                        "Automation failed."
                    )

                finally:

                    try:
                        loop.close()
                    except Exception:
                        pass

        return "\n".join(final_responses)

    except Exception as e:

        print(f"[Router] Error: {e}")

        return "Something went wrong in SmartRouter."


# =========================================================
# MAIN CHATBOT AI
# =========================================================

def ChatBotAI(prompt):

    try:

        prompt = str(prompt).strip()

        if not prompt:
            return "Please say something."


        # =================================================
        # WHATSAPP
        # =================================================

        if is_whatsapp_command(prompt):

            print("OPENING WHATSAPP")

            try:

                result = WhatsAppController(prompt)

                if result.get("success"):

                    msg = (
                        f"WhatsApp action performed "
                        f"via {result.get('method', 'unknown method')}."
                    )

                else:

                    msg = (
                        "WhatsApp action failed: "
                        f"{result.get('error', 'Unknown error')}."
                    )

                TTS(msg)

                return msg

            except Exception as e:

                print(f"[WhatsApp] Error: {e}")

                return "I could not complete the WhatsApp action."


        # =================================================
        # AUTOMATION
        # =================================================

        elif prompt.lower().startswith(
            ("open ", "search ", "play ")
        ):

            try:

                action_result = perform_action(
                    prompt,
                    raw_text=prompt
                )

                if not action_result.startswith("❌"):

                    TTS(action_result)

                return action_result

            except Exception as e:

                print(f"[Automation] Error: {e}")

                return "I could not perform that action."


        # =================================================
        # LANGUAGE CHECK
        # =================================================

        if detect_language(prompt) == "Unsupported":

            return (
                "Sorry, I can only understand "
                "English or Hinglish."
            )


        # =================================================
        # GROQ CLIENT CHECK
        # =================================================

        if client is None:

            print(
                "[llm] Groq client is not available."
            )

            return (
                "Groq is not configured. "
                "Please check your GROQ_API_KEY."
            )


        # =================================================
        # LOAD CHAT HISTORY
        # =================================================

        messages = load_json_safe(
            CHATLOG_PATH,
            DefaultMessage
        )


        # =================================================
        # SYSTEM MESSAGE
        # =================================================

        system_msg = {
            "role": "system",
            "content": (
                f"{CustomInstructions}\n"
                "Always reply in English/Hinglish.\n"
                f"{Information()}"
            )
        }


        # =================================================
        # GROQ REQUEST
        # =================================================

        print(f"[llm] Sending request to Groq...")

        completion = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=(
                SystemChatBot
                + [system_msg]
                + messages
                + [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ),

            stream=True
        )


        # =================================================
        # READ STREAM
        # =================================================

        answer = ""

        for chunk in completion:

            try:

                content = chunk.choices[0].delta.content

                if content:

                    answer += content

            except Exception:
                continue


        # =================================================
        # CHECK EMPTY RESPONSE
        # =================================================

        if not answer.strip():

            print("[llm] Groq returned an empty response.")

            return "I did not receive a response from Groq."


        # =================================================
        # SAVE CHAT HISTORY
        # =================================================

        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        try:

            with open(
                CHATLOG_PATH,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    messages,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            print(f"[ChatLog] Could not save chat history: {e}")


        # =================================================
        # FINAL ANSWER
        # =================================================

        final_answer = AnswerModifier(answer)


        # =================================================
        # TTS
        # =================================================

        if final_answer:

            try:

                TTS(final_answer)

            except Exception as e:

                print(f"[TTS] Error: {e}")


        return final_answer


    # =====================================================
    # GROQ/API ERROR
    # =====================================================

    except Exception as e:

        error_text = str(e)

        print(f"[llm] Groq/API Error: {error_text}")


        if "401" in error_text or "invalid api key" in error_text.lower():

            print(
                "[llm] Your GROQ_API_KEY was rejected by Groq."
            )

            return (
                "My Groq API key was rejected. "
                "Please check the GROQ_API_KEY in your .env file."
            )


        if "429" in error_text:

            return (
                "Groq rate limit reached. "
                "Please try again in a moment."
            )


        return "An error occurred while processing your request."


# =========================================================
# MAIN LOOP
# =========================================================

if __name__ == "__main__":

    print(
        f"=== {AssistantName} Started ==="
    )

    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Environment file: {ENV_FILE}"
    )

    print(
        "Type 'exit' to quit.\n"
    )


    while True:

        try:

            user_input = input(
                "Enter Your Question: "
            ).strip()

        except KeyboardInterrupt:

            print(
                f"\nExiting {AssistantName}..."
            )

            break

        except EOFError:

            print(
                f"\nExiting {AssistantName}..."
            )

            break


        if user_input.lower() in (
            "exit",
            "quit"
        ):

            print(
                f"Exiting {AssistantName}..."
            )

            break


        if not user_input:

            continue


        response = SmartRouter(
            user_input
        )


        print(
            f"\n{AssistantName}: {response}\n"
        )