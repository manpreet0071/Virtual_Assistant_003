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

        if (
            isinstance(result, dict)
            and result.get("action", {}).get("type") == "none"
        ):

            print(
                "[Assistant] Normal AI conversation"
            )

            answer = AnswerModifier(
                ChatBotAI(query)
            )

            print(
                "Assistant:",
                answer
            )

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
        # SAVE CHAT LOG
        # ====================================================

        try:

            with open(
                ChatLogPath,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(

                    [
                        {
                            "role": "user",
                            "content": query
                        },

                        {
                            "role": "assistant",
                            "content": response
                        }
                    ],

                    f,

                    indent=4,

                    ensure_ascii=False
                )

        except Exception as e:

            print(
                "⚠️ ChatLog Error:",
                e
            )


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