import os
import sys
import json
from random import choice


# ============================================================
# PATH SETUP
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND_DIR = os.path.join(
    BASE_DIR,
    "backend"
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend.Automation_engine import Run as AutomationEngine
from backend.chatbot import ChatBotAI, AnswerModifier
from backend.llm import ask_llm as Model
from backend.pc_control_new import perform_action as SystemAutomation
from backend.whatsapp_controller import WhatsAppController


# ============================================================
# CHAT LOG
# ============================================================

ChatLogPath = os.path.join(
    BACKEND_DIR,
    "Data",
    "ChatLog.json"
)

os.makedirs(
    os.path.dirname(ChatLogPath),
    exist_ok=True
)

# Keep only the most recent N turns (user+assistant pairs) in the log.
# This also matters for speed: chatbot.py / RealtimeSearchEngine.py send
# this whole log to the model as conversation history on every request,
# so an ever-growing file makes every future reply slower and slower.
MAX_CHAT_LOG_MESSAGES = 20


def _append_chat_log(user_text: str, assistant_text: str) -> None:
    """Append one exchange to ChatLog.json instead of overwriting it.

    BUG FIX: the previous version of this function replaced the whole
    file with just the latest exchange on every automation command,
    silently deleting all prior conversation history that chatbot.py
    relies on for context.
    """

    try:
        if os.path.exists(ChatLogPath):
            with open(ChatLogPath, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
                except Exception:
                    history = []
        else:
            history = []

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": assistant_text})

        if len(history) > MAX_CHAT_LOG_MESSAGES:
            history = history[-MAX_CHAT_LOG_MESSAGES:]

        with open(ChatLogPath, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print("⚠️ ChatLog Error:", e)


# ============================================================
# PROFESSIONAL AUTOMATION RESPONSES
# ============================================================

professional_responses = [
    "Task completed successfully.",
    "I've executed your command.",
    "Automation finished.",
    "Your request has been processed."
]


# ============================================================
# MAIN ASSISTANT EXECUTION
# ============================================================

def MainExecution(query: str):

    query = query.strip()

    if not query:
        return None

    print()
    print("=" * 60)
    print("You:", query)
    print("=" * 60)


    # ========================================================
    # WHATSAPP FAST PATH
    # ========================================================

    if "whatsapp" in query.lower():

        try:

            print("[Assistant] Processing WhatsApp command...")

            result = WhatsAppController(query)

            if (
                isinstance(result, dict)
                and result.get("success")
            ):
                response = "Message sent successfully."

            else:
                response = "Failed to send WhatsApp message."

            print("Assistant:", response)

            return response

        except Exception as e:

            print(
                "❌ WhatsApp Error:",
                e
            )

            return "WhatsApp action failed."


    # ========================================================
    # NORMAL LLM FLOW
    # ========================================================

    try:

        print("[Assistant] Asking LLM...")

        result = Model(query)

        print(
            "LLM Result:",
            result
        )


        # ====================================================
        # AI ONLY
        # ====================================================
        # PERF FIX: ask_llm() already generated a full "speak"/"display"
        # answer as part of the SAME Groq call that decided the action
        # type. The old code discarded that answer and made a SECOND,
        # completely separate Groq call to ChatBotAI() just to answer
        # the exact same question again. That means every plain message
        # (e.g. "hello") paid for two full model round-trips back to
        # back. We now reuse the first call's answer directly, which
        # roughly halves latency for normal conversation. ChatBotAI()
        # is kept only as a fallback for the rare case where ask_llm()
        # returned an empty/unusable answer (e.g. Groq client not
        # configured).
        # ====================================================

        if (
            isinstance(result, dict)
            and result.get("action", {}).get("type") == "none"
        ):

            print(
                "[Assistant] Normal AI conversation"
            )

            direct_answer = (
                result.get("speak")
                or result.get("display")
                or ""
            ).strip()

            if direct_answer:
                answer = AnswerModifier(direct_answer)
            else:
                # Fallback path only — kept for safety, not the hot path.
                answer = AnswerModifier(
                    ChatBotAI(query)
                )

            print(
                "Assistant:",
                answer
            )

            _append_chat_log(query, answer)

            return answer


        # ====================================================
        # AUTOMATION
        # ====================================================

        command = ""

        if isinstance(result, dict):

            command = result.get(
                "action",
                {}
            ).get(
                "command",
                ""
            )


        if not command:

            print(
                "⚠️ LLM returned no command."
            )

            return "I couldn't determine the command."


        print(
            "[Assistant] Command:",
            command
        )


        # ====================================================
        # HIGH LEVEL AUTOMATION
        # ====================================================

        automation_prefixes = (

            "open ",
            "close ",
            "play ",
            "system ",
            "write ",
            "code ",
            "make ",
            "google search ",
            "search ",
            "youtube search ",
            "search on youtube ",

        )


        if command.lower().startswith(
            automation_prefixes
        ):

            print(
                "[Assistant] Running AutomationEngine..."
            )

            AutomationEngine(
                command
            )


        # ====================================================
        # GENERAL SYSTEM AUTOMATION
        # ====================================================

        else:

            print(
                "[Assistant] Running SystemAutomation..."
            )

            SystemAutomation(
                command,
                raw_text=query,
                model_output=str(result)
            )


        # ====================================================
        # AUTOMATION RESPONSE
        # ====================================================

        response = choice(
            professional_responses
        )

        print(
            "Assistant:",
            response
        )


        # ====================================================
        # SAVE CHAT LOG (append, don't overwrite — see fix above)
        # ====================================================

        _append_chat_log(query, response)

        return response


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print()
        print(
            "❌ MainExecution Error:",
            e
        )

        return (
            "Sorry, something went wrong "
            "while processing your request."
        )