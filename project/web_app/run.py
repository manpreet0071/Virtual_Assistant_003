# """
# main.py
# -------
# Entry point for the native Python assistant UI (replaces spider.html +
# eel as the app shell).

# Run with:
#     pip install -r requirements.txt
#     python main.py

# Drop your avatar video into ./assets/ — any .mp4/.mov/.avi is picked up
# automatically and looped.

# The window opens docked to the BOTTOM-RIGHT corner of your screen, on
# top of everything else, like a desktop widget.

# Project layout this expects:
#     main.py
#     ui/main_window.py      <- the window itself
#     core/camera.py         <- webcam thread
#     core/speech.py         <- listen (STT) + speak (TTS) threads
#     backend/                <- OPTIONAL: put llm.py, Automation_engine.py,
#                                TTS.py, pc_control_new.py, whatsapp_controller.py,
#                                chatbot.py, prompts.py, etc. here if you want
#                                the mic to actually trigger your AI backend.
#                                The app runs fine without this folder too —
#                                it'll just echo back what you said.
#     assets/                 <- your avatar video goes here
# """

# import os
# import sys

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # backend/ was NOT moved into web_app — it's still one level up, as a
# # sibling folder (project/backend, while this file lives in
# # project/web_app). Point sys.path at its real location instead of
# # requiring it to be moved.
# BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "backend"))

# for path in (BASE_DIR, BACKEND_DIR):
#     if os.path.isdir(path) and path not in sys.path:
#         sys.path.insert(0, path)

# from PyQt5.QtWidgets import QApplication

# from ui.main_window import MainWindow


# def main():
#     app = QApplication(sys.argv)
#     app.setQuitOnLastWindowClosed(True)

#     window = MainWindow(
#         assistant_name=os.getenv("AssistantName", "J4E"),
#         language=os.getenv("InputLanguage", "en-US"),
#     )
#     window.show()

#     sys.exit(app.exec_())


# if __name__ == "__main__":
#     main()





import os
import sys


# ============================================================
# PATH SETUP
# ============================================================

# This file is:
#
# project/
#     web_app/
#         main.py
#
# Therefore BASE_DIR = project/web_app
# PROJECT_ROOT       = project
# BACKEND_DIR        = project/backend

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    BASE_DIR
)

BACKEND_DIR = os.path.join(
    PROJECT_ROOT,
    "backend"
)

CORE_DIR = os.path.join(
    PROJECT_ROOT,
    "core"
)


# ============================================================
# ADD PROJECT PATHS
# ============================================================

for path in (
    PROJECT_ROOT,
    BACKEND_DIR,
    CORE_DIR,
    BASE_DIR
):

    if (
        os.path.isdir(path)
        and path not in sys.path
    ):

        sys.path.insert(
            0,
            path
        )


# ============================================================
# DEBUG PATHS
# ============================================================

print("=" * 60)
print("[Emily] Starting...")
print("[Emily] BASE_DIR    :", BASE_DIR)
print("[Emily] PROJECT_ROOT:", PROJECT_ROOT)
print("[Emily] BACKEND_DIR :", BACKEND_DIR)
print("[Emily] CORE_DIR    :", CORE_DIR)
print("=" * 60)


# ============================================================
# CHECK BACKEND
# ============================================================

if not os.path.isdir(BACKEND_DIR):

    raise FileNotFoundError(
        f"""
Backend folder was not found.

Expected:
{BACKEND_DIR}

Create/move your backend folder there.
"""
    )


# ============================================================
# IMPORT PYQT5
# ============================================================

from PyQt5.QtWidgets import QApplication


# ============================================================
# IMPORT UI
# ============================================================

from ui.main_window import MainWindow


# ============================================================
# IMPORT ASSISTANT BACKEND
# ============================================================

from backend.assistant_controller import MainExecution


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setQuitOnLastWindowClosed(
        True
    )


    # --------------------------------------------------------
    # ENVIRONMENT VARIABLES
    # --------------------------------------------------------

    assistant_name = os.getenv(
        "AssistantName",
        "Emily"
    )

    language = os.getenv(
        "InputLanguage",
        "en-US"
    )


    # --------------------------------------------------------
    # CREATE WINDOW
    # --------------------------------------------------------

    window = MainWindow(

        assistant_name=assistant_name,

        language=language,

        on_query=MainExecution

    )


    # --------------------------------------------------------
    # SHOW WINDOW
    # --------------------------------------------------------

    window.show()


    # --------------------------------------------------------
    # START QT
    # --------------------------------------------------------

    sys.exit(
        app.exec_()
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()