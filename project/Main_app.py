"""
main.py
-------
Entry point for the native Python assistant UI (replaces spider.html +
eel as the app shell).

Run with:
    pip install -r requirements.txt
    python main.py

Drop your avatar video into ./assets/ — any .mp4/.mov/.avi is picked up
automatically and looped.

The window opens docked to the BOTTOM-RIGHT corner of your screen, on
top of everything else, like a desktop widget.

Project layout this expects:
    main.py
    ui/main_window.py      <- the window itself
    core/camera.py         <- webcam thread
    core/speech.py         <- listen (STT) + speak (TTS) threads
    backend/                <- OPTIONAL: put llm.py, Automation_engine.py,
                               TTS.py, pc_control_new.py, whatsapp_controller.py,
                               chatbot.py, prompts.py, etc. here if you want
                               the mic to actually trigger your AI backend.
                               The app runs fine without this folder too —
                               it'll just echo back what you said.
    assets/                 <- your avatar video goes here
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Make sure ui/, core/, and backend/ are all importable regardless of
# where this script is launched from.
for sub in ("", "backend"):
    path = os.path.join(BASE_DIR, sub) if sub else BASE_DIR
    if path not in sys.path:
        sys.path.insert(0, path)

from PyQt5.QtWidgets import QApplication

# from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # window = MainWindow(
    #     assistant_name=os.getenv("AssistantName", "J4E"),
    #     language=os.getenv("InputLanguage", "en-US"),
    # )
    # window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()