# """
# core/speech.py
# --------------
# Background threads for speech-to-text (listening) and text-to-speech
# (speaking), so the GUI thread never blocks.

# This replaces the old browser-side `webkitSpeechRecognition` +
# `eel.js_mic(...)` bridge from home.html.
# """

# from PyQt5.QtCore import QThread, pyqtSignal

# try:
#     import speech_recognition as sr
# except ImportError:
#     sr = None

# try:
#     import pyttsx3
# except ImportError:
#     pyttsx3 = None


# class ListenThread(QThread):
#     """Continuously listens on the default microphone until stopped,
#     emitting `result_ready` with each final transcript (mirrors the
#     old recognition.onresult -> eel.js_mic() call)."""

#     result_ready = pyqtSignal(str)
#     error = pyqtSignal(str)
#     state_changed = pyqtSignal(str)

#     def __init__(self, language: str = "en-US", parent=None):
#         super().__init__(parent)
#         self.language = language
#         self._running = False

#     def run(self):
#         if sr is None:
#             self.error.emit(
#                 "SpeechRecognition is not installed. Run: pip install SpeechRecognition PyAudio"
#             )
#             return

#         recognizer = sr.Recognizer()
#         self._running = True

#         try:
#             with sr.Microphone() as source:
#                 recognizer.adjust_for_ambient_noise(source, duration=0.5)
#                 self.state_changed.emit("Listening...")

#                 while self._running:
#                     try:
#                         audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
#                     except sr.WaitTimeoutError:
#                         continue

#                     if not self._running:
#                         break

#                     try:
#                         text = recognizer.recognize_google(audio, language=self.language)
#                         if text:
#                             self.result_ready.emit(text)
#                     except sr.UnknownValueError:
#                         continue
#                     except sr.RequestError as exc:
#                         self.error.emit(f"Speech service error: {exc}")
#                         break
#         except OSError as exc:
#             self.error.emit(f"Microphone error: {exc}")
#         finally:
#             self.state_changed.emit("Available...")

#     def stop(self):
#         self._running = False


# class SpeakThread(QThread):
#     """Speaks a single piece of text via pyttsx3 without blocking the GUI."""

#     finished_speaking = pyqtSignal()

#     def __init__(self, text: str, parent=None):
#         super().__init__(parent)
#         self.text = text

#     def run(self):
#         if pyttsx3 is None:
#             self.finished_speaking.emit()
#             return
#         engine = pyttsx3.init()
#         engine.say(self.text)
#         engine.runAndWait()
#         self.finished_speaking.emit()



"""
core/speech.py
--------------
Background threads for speech-to-text (listening) and text-to-speech
(speaking), so the GUI thread never blocks.

This replaces the old browser-side `webkitSpeechRecognition` +
`eel.js_mic(...)` bridge from home.html.
"""

from PyQt5.QtCore import QThread, pyqtSignal

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class ListenThread(QThread):
    """Continuously listens on the default microphone until stopped,
    emitting `result_ready` with each final transcript (mirrors the
    old recognition.onresult -> eel.js_mic() call)."""

    result_ready = pyqtSignal(str)
    error = pyqtSignal(str)
    state_changed = pyqtSignal(str)

    def __init__(self, language: str = "en-US", parent=None):
        super().__init__(parent)
        self.language = language
        self._running = False

    def run(self):
        if sr is None:
            self.error.emit(
                "SpeechRecognition is not installed. Run: pip install SpeechRecognition PyAudio"
            )
            return

        recognizer = sr.Recognizer()
        self._running = True

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.state_changed.emit("Listening...")

                while self._running:
                    try:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    except sr.WaitTimeoutError:
                        continue

                    if not self._running:
                        break

                    try:
                        text = recognizer.recognize_google(audio, language=self.language)
                        if text:
                            self.result_ready.emit(text)
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as exc:
                        self.error.emit(f"Speech service error: {exc}")
                        break
        except OSError as exc:
            self.error.emit(f"Microphone error: {exc}")
        finally:
            self.state_changed.emit("Available...")

    def stop(self):
        self._running = False


class SpeakThread(QThread):
    """Speaks a single piece of text via pyttsx3 without blocking the GUI."""

    finished_speaking = pyqtSignal()

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self):
        if pyttsx3 is None:
            self.finished_speaking.emit()
            return
        engine = pyttsx3.init()
        engine.say(self.text)
        engine.runAndWait()
        self.finished_speaking.emit()