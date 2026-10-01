# """
# ui/main_window.py
# ------------------
# The single window for the assistant. This is what main.py opens.

# Layout:
#     The avatar video (or, when toggled, the live webcam) fills the
#     ENTIRE window edge-to-edge, like a picture-in-picture widget. The
#     title bar, status text, and mic/camera buttons float on top of the
#     video as semi-transparent overlays rather than living in their own
#     boxed-off section.

# Playback:
#     Both the avatar clip and the webcam feed are decoded with OpenCV
#     (core/avatar.py, core/camera.py) rather than PyQt5's QMediaPlayer.
#     QMediaPlayer depends on Windows DirectShow, which frequently fails
#     on ordinary .mp4 files (DirectShowPlayerService::doRender errors).
#     OpenCV sidesteps that entirely.

# Positioning:
#     The window is frameless, always-on-top, and docks itself to the
#     BOTTOM-RIGHT corner of the primary screen, like a desktop widget.

# Wiring to the backend:
#     When speech is recognized, MainWindow calls `self.handle_query(text)`.
#     That method tries (in order):
#       1. `on_query` callback passed in at construction, if you supplied one
#       2. backend.llm.ask_llm(text)              -> dict with "speak"/"display"
#       3. a plain echo, if no backend is wired up yet

#     Put your backend/*.py files (llm.py, Automation_engine.py, TTS.py,
#     pc_control_new.py, whatsapp_controller.py, chatbot.py, prompts.py, ...)
#     into a folder named `backend/` and this will pick them up
#     automatically. Nothing crashes if backend/ is missing or a module
#     fails to import — it just falls back gracefully.
# """

# import glob
# import os
# import sys
# import importlib

# from PyQt5.QtCore import Qt, QUrl
# from PyQt5.QtGui import QPixmap, QImage, QRegion, QPainterPath
# from PyQt5.QtWidgets import (
#     QWidget, QLabel, QPushButton, QHBoxLayout, QApplication
# )

# from core.speech import ListenThread, SpeakThread
# from core.camera import CameraThread
# from core.avatar import AvatarThread, cover_resize

# try:
#     import cv2  # only used to convert raw webcam frames back to BGR for cover_resize
#     import numpy as np
# except ImportError:
#     cv2 = None
#     np = None

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# if BACKEND_DIR not in sys.path:
#     sys.path.insert(0, BACKEND_DIR)

# WINDOW_W, WINDOW_H = 320, 460
# MARGIN = 24        # gap from the screen edge
# CORNER_RADIUS = 18
# TOP_BAR_H = 40
# BOTTOM_BAR_H = 78


# def _find_avatar_video() -> str | None:
#     for ext in ("*.mp4", "*.mov", "*.avi", "*.mkv"):
#         matches = glob.glob(os.path.join(ASSETS_DIR, ext))
#         if matches:
#             return matches[0]
#     return None


# def _lazy_backend(module_name: str, attr: str = None):
#     """Import a backend module (or a single attribute from it) without
#     blowing up the whole app if it's missing or fails to import."""
#     try:
#         mod = importlib.import_module(module_name)
#     except Exception as exc:
#         print(f"[main_window] backend.{module_name} unavailable: {exc}")
#         return None
#     if attr is None:
#         return mod
#     return getattr(mod, attr, None)


# class MainWindow(QWidget):
#     def __init__(self, assistant_name: str = "Assistant", language: str = "en-US",
#                  on_query=None, parent=None):
#         super().__init__(parent)
#         self.assistant_name = assistant_name
#         self.language = language
#         self.on_query = on_query  # optional external callback(text) -> str | dict | None

#         self._avatar_thread: AvatarThread | None = None
#         self._listen_thread: ListenThread | None = None
#         self._speak_thread: SpeakThread | None = None
#         self._camera_thread: CameraThread | None = None
#         self._camera_active = False
#         self._drag_pos = None

#         self._build_ui()
#         self._dock_bottom_right()
#         self._start_avatar_video()

#     # ------------------------------------------------------------------
#     # UI construction — video fills the whole window; everything else
#     # is an overlay widget stacked on top of it.
#     # ------------------------------------------------------------------
#     def _build_ui(self):
#         self.setWindowTitle(self.assistant_name)
#         self.setFixedSize(WINDOW_W, WINDOW_H)
#         self.setWindowFlags(
#             Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
#         )

#         # ---- full-window video/camera background ----
#         self.video_label = QLabel(self)
#         self.video_label.setGeometry(0, 0, WINDOW_W, WINDOW_H)
#         self.video_label.setStyleSheet("background-color: #000;")
#         self.video_label.setScaledContents(False)
#         self.video_label.setAlignment(Qt.AlignCenter)

#         # ---- top bar overlay: name + close ----
#         self.top_bar = QWidget(self)
#         self.top_bar.setGeometry(0, 0, WINDOW_W, TOP_BAR_H)
#         self.top_bar.setStyleSheet("background-color: rgba(0, 0, 0, 130);")
#         top_layout = QHBoxLayout(self.top_bar)
#         top_layout.setContentsMargins(14, 6, 8, 6)

#         self.name_label = QLabel(self.assistant_name)
#         self.name_label.setStyleSheet("color: #f2f2f2; font-size: 14px; font-weight: 600; background: transparent;")
#         top_layout.addWidget(self.name_label)
#         top_layout.addStretch()

#         close_btn = QPushButton("✕")
#         close_btn.setFixedSize(24, 24)
#         close_btn.setStyleSheet("""
#             QPushButton { color: #ccc; background: transparent; border: none; border-radius: 12px; }
#             QPushButton:hover { background-color: rgba(255,255,255,40); }
#         """)
#         close_btn.clicked.connect(self.close)
#         top_layout.addWidget(close_btn)

#         # ---- bottom bar overlay: status text + mic/camera buttons ----
#         self.bottom_bar = QWidget(self)
#         self.bottom_bar.setGeometry(0, WINDOW_H - BOTTOM_BAR_H, WINDOW_W, BOTTOM_BAR_H)
#         self.bottom_bar.setStyleSheet("background-color: rgba(0, 0, 0, 130);")

#         bottom_layout = QHBoxLayout(self.bottom_bar)
#         bottom_layout.setContentsMargins(0, 8, 0, 10)

#         btn_style = """
#             QPushButton { border: none; border-radius: 22px; background-color: rgba(35, 37, 48, 200); color: white; font-size: 16px; }
#             QPushButton:hover { background-color: rgba(46, 49, 64, 230); }
#             QPushButton[active="true"] { background-color: rgba(214, 72, 63, 220); }
#         """

#         self.camera_btn = QPushButton("📷")
#         self.camera_btn.setFixedSize(40, 40)
#         self.camera_btn.setStyleSheet(btn_style)
#         self.camera_btn.clicked.connect(self.toggle_camera)

#         self.mic_btn = QPushButton("🎤")
#         self.mic_btn.setFixedSize(44, 44)
#         self.mic_btn.setStyleSheet(btn_style)
#         self.mic_btn.clicked.connect(self.toggle_listening)

#         bottom_layout.addStretch()
#         bottom_layout.addWidget(self.camera_btn)
#         bottom_layout.addSpacing(16)
#         bottom_layout.addWidget(self.mic_btn)
#         bottom_layout.addStretch()

#         self.status_label = QLabel("Available...", self.bottom_bar)
#         self.status_label.setGeometry(0, BOTTOM_BAR_H - 20, WINDOW_W, 18)
#         self.status_label.setAlignment(Qt.AlignCenter)
#         self.status_label.setStyleSheet("color: #cfcfcf; font-size: 11px; background: transparent;")

#         # stacking order: video at the bottom, bars on top
#         self.top_bar.raise_()
#         self.bottom_bar.raise_()

#         self._apply_rounded_mask()

#     def _apply_rounded_mask(self):
#         path = QPainterPath()
#         path.addRoundedRect(0, 0, self.width(), self.height(), CORNER_RADIUS, CORNER_RADIUS)
#         self.setMask(QRegion(path.toFillPolygon().toPolygon()))

#     def _dock_bottom_right(self):
#         screen = QApplication.primaryScreen().availableGeometry()
#         x = screen.right() - WINDOW_W - MARGIN
#         y = screen.bottom() - WINDOW_H - MARGIN
#         self.move(x, y)

#     # allow dragging the frameless window by clicking anywhere on it
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
#             event.accept()

#     def mouseMoveEvent(self, event):
#         if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
#             self.move(event.globalPos() - self._drag_pos)
#             event.accept()

#     def mouseReleaseEvent(self, event):
#         self._drag_pos = None

#     # ------------------------------------------------------------------
#     # Avatar video (core/avatar.py, OpenCV-based — fills the whole window)
#     # ------------------------------------------------------------------
#     def _start_avatar_video(self):
#         path = _find_avatar_video()
#         if not path:
#             self.status_label.setText("Drop an .mp4 into /assets")
#             return
#         self._avatar_thread = AvatarThread(path, target_size=(WINDOW_W, WINDOW_H))
#         self._avatar_thread.frame_ready.connect(self._on_avatar_frame)
#         self._avatar_thread.error.connect(self._on_error)
#         self._avatar_thread.start()

#     def _stop_avatar_video(self):
#         if self._avatar_thread is not None:
#             self._avatar_thread.stop()
#             self._avatar_thread.wait(500)
#             self._avatar_thread = None

#     def _on_avatar_frame(self, qimg: QImage):
#         if self._camera_active:
#             return  # camera feed currently owns the display
#         self.video_label.setPixmap(QPixmap.fromImage(qimg))

#     def _on_error(self, message: str):
#         self.set_status("Available...")
#         print(f"[main_window] {message}")

#     # ------------------------------------------------------------------
#     # Microphone (core/speech.py)
#     # ------------------------------------------------------------------
#     def toggle_listening(self):
#         if self._listen_thread is not None and self._listen_thread.isRunning():
#             self._listen_thread.stop()
#             self._listen_thread = None
#             self.mic_btn.setProperty("active", "false")
#             self.mic_btn.setStyle(self.mic_btn.style())
#             self.set_status("Available...")
#             return

#         self._listen_thread = ListenThread(language=self.language)
#         self._listen_thread.result_ready.connect(self._on_speech_result)
#         self._listen_thread.state_changed.connect(self.set_status)
#         self._listen_thread.error.connect(self._on_error)
#         self._listen_thread.start()

#         self.mic_btn.setProperty("active", "true")
#         self.mic_btn.setStyle(self.mic_btn.style())

#     def _on_speech_result(self, text: str):
#         self.set_status("Thinking...")
#         self.handle_query(text)

#     # ------------------------------------------------------------------
#     # Camera (core/camera.py) — only ever starts when the button is
#     # pressed, and takes over the same full-window display the avatar
#     # video uses. Pressing it again stops the camera and hands the
#     # display back to the avatar loop.
#     # ------------------------------------------------------------------
#     def toggle_camera(self):
#         if self._camera_thread is not None:
#             self._camera_thread.stop()
#             self._camera_thread.wait(500)
#             self._camera_thread = None
#             self._camera_active = False
#             self.camera_btn.setProperty("active", "false")
#             self.camera_btn.setStyle(self.camera_btn.style())
#             return

#         self._camera_active = True
#         self._camera_thread = CameraThread()
#         self._camera_thread.frame_ready.connect(self._on_camera_frame)
#         self._camera_thread.error.connect(self._on_error)
#         self._camera_thread.start()
#         self.camera_btn.setProperty("active", "true")
#         self.camera_btn.setStyle(self.camera_btn.style())

#     def _on_camera_frame(self, qimg: QImage):
#         if not self._camera_active:
#             return
#         # core/camera.py emits frames at the webcam's native resolution;
#         # crop/scale them to fill the window the same way the avatar does.
#         if cv2 is not None and np is not None:
#             w, h = qimg.width(), qimg.height()
#             ptr = qimg.bits()
#             ptr.setsize(h * w * 3)
#             rgb = np.frombuffer(ptr, dtype="uint8").reshape((h, w, 3))
#             bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
#             fitted = cover_resize(bgr, WINDOW_W, WINDOW_H)
#             fitted_rgb = cv2.cvtColor(fitted, cv2.COLOR_BGR2RGB)
#             out = QImage(fitted_rgb.data, WINDOW_W, WINDOW_H, 3 * WINDOW_W, QImage.Format_RGB888)
#             self.video_label.setPixmap(QPixmap.fromImage(out.copy()))
#         else:
#             pixmap = QPixmap.fromImage(qimg).scaled(
#                 WINDOW_W, WINDOW_H, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
#             )
#             self.video_label.setPixmap(pixmap)

#     # ------------------------------------------------------------------
#     # Query handling -> backend -> speech output
#     # ------------------------------------------------------------------
#     def handle_query(self, text: str):
#         """Route recognized speech (or typed text) to a response.

#         Priority: caller-supplied on_query callback > backend.llm.ask_llm
#         > a simple echo fallback. Whatever text comes back is spoken via
#         SpeakThread and shown as status."""
#         response_text = None

#         try:
#             if self.on_query is not None:
#                 result = self.on_query(text)
#                 response_text = self._extract_speak_text(result)

#             if response_text is None:
#                 ask_llm = _lazy_backend("llm", "ask_llm")
#                 if ask_llm is not None:
#                     result = ask_llm(text)
#                     response_text = self._extract_speak_text(result)

#             if response_text is None:
#                 response_text = f"You said: {text}"

#         except Exception as exc:
#             print(f"[main_window] handle_query error: {exc}")
#             response_text = "Sorry, something went wrong processing that."

#         self.set_status("Answering...")
#         self.speak(response_text)

#     @staticmethod
#     def _extract_speak_text(result):
#         if result is None:
#             return None
#         if isinstance(result, str):
#             return result
#         if isinstance(result, dict):
#             return result.get("speak") or result.get("display")
#         return str(result)

#     def speak(self, text: str):
#         self._speak_thread = SpeakThread(text)
#         self._speak_thread.finished_speaking.connect(lambda: self.set_status("Available..."))
#         self._speak_thread.start()

#     # ------------------------------------------------------------------
#     def set_status(self, text: str):
#         self.status_label.setText(text)

#     def closeEvent(self, event):
#         if self._listen_thread is not None:
#             self._listen_thread.stop()
#         if self._camera_thread is not None:
#             self._camera_thread.stop()
#         self._stop_avatar_video()
#         super().closeEvent(event)


#___________________________________________________________________________________________________________________________
"""
ui/main_window.py

PyQt5 frontend for Emily AI Assistant.

Responsibilities:
    - Display avatar video
    - Display webcam
    - Microphone input
    - Send queries to backend
    - Display status
    - Speak backend response
"""


# ============================================================
# IMPORTS
# ============================================================

import glob
import os
import sys
import importlib
import threading


from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QPixmap,
    QImage,
    QRegion,
    QPainterPath
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QApplication
)


# ============================================================
# CORE IMPORTS
# ============================================================

from core.speech import (
    ListenThread,
    SpeakThread
)

from core.camera import (
    CameraThread
)

from core.avatar import (
    AvatarThread,
    cover_resize
)


# ============================================================
# OPTIONAL OPENCV
# ============================================================

try:

    import cv2
    import numpy as np

except ImportError:

    cv2 = None
    np = None


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)

BACKEND_DIR = os.path.join(
    BASE_DIR,
    "backend"
)


if BACKEND_DIR not in sys.path:

    sys.path.insert(
        0,
        BACKEND_DIR
    )


# ============================================================
# WINDOW SETTINGS
# ============================================================

WINDOW_W = 320
WINDOW_H = 460

MARGIN = 24

CORNER_RADIUS = 18

TOP_BAR_H = 40

BOTTOM_BAR_H = 78


# ============================================================
# FIND AVATAR VIDEO
# ============================================================

def _find_avatar_video():

    for ext in (
        "*.mp4",
        "*.mov",
        "*.avi",
        "*.mkv"
    ):

        matches = glob.glob(
            os.path.join(
                ASSETS_DIR,
                ext
            )
        )

        if matches:

            return matches[0]

    return None


# ============================================================
# OPTIONAL BACKEND IMPORT
# ============================================================

def _lazy_backend(
    module_name: str,
    attr: str = None
):

    try:

        mod = importlib.import_module(
            module_name
        )

    except Exception as exc:

        print(
            "[main_window] backend.",
            module_name,
            "unavailable:",
            exc
        )

        return None


    if attr is None:

        return mod


    return getattr(
        mod,
        attr,
        None
    )


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QWidget):


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        assistant_name: str = "Emily",
        language: str = "en-US",
        on_query=None,
        parent=None
    ):

        super().__init__(
            parent
        )


        self.assistant_name = (
            assistant_name
        )

        self.language = (
            language
        )

        self.on_query = (
            on_query
        )


        # ----------------------------------------------------
        # THREADS
        # ----------------------------------------------------

        self._avatar_thread = None

        self._listen_thread = None

        self._speak_thread = None

        self._camera_thread = None


        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self._camera_active = False

        self._drag_pos = None


        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        self._build_ui()

        self._dock_bottom_right()

        self._start_avatar_video()


    # ========================================================
    # BUILD UI
    # ========================================================

    def _build_ui(self):

        self.setWindowTitle(
            self.assistant_name
        )

        self.setFixedSize(
            WINDOW_W,
            WINDOW_H
        )


        # ----------------------------------------------------
        # WINDOW FLAGS
        # ----------------------------------------------------

        self.setWindowFlags(

            Qt.FramelessWindowHint
            |
            Qt.WindowStaysOnTopHint
            |
            Qt.Tool

        )


        # ----------------------------------------------------
        # VIDEO BACKGROUND
        # ----------------------------------------------------

        self.video_label = QLabel(
            self
        )

        self.video_label.setGeometry(
            0,
            0,
            WINDOW_W,
            WINDOW_H
        )

        self.video_label.setStyleSheet(
            "background-color: #000;"
        )

        self.video_label.setScaledContents(
            False
        )

        self.video_label.setAlignment(
            Qt.AlignCenter
        )


        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        self.top_bar = QWidget(
            self
        )

        self.top_bar.setGeometry(
            0,
            0,
            WINDOW_W,
            TOP_BAR_H
        )

        self.top_bar.setStyleSheet(
            "background-color: rgba(0,0,0,130);"
        )


        top_layout = QHBoxLayout(
            self.top_bar
        )

        top_layout.setContentsMargins(
            14,
            6,
            8,
            6
        )


        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        self.name_label = QLabel(
            self.assistant_name
        )

        self.name_label.setStyleSheet(
            """
            color: #f2f2f2;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            """
        )


        top_layout.addWidget(
            self.name_label
        )

        top_layout.addStretch()


        # ----------------------------------------------------
        # CLOSE
        # ----------------------------------------------------

        close_btn = QPushButton(
            "✕"
        )

        close_btn.setFixedSize(
            24,
            24
        )

        close_btn.setStyleSheet(
            """
            QPushButton {
                color: #ccc;
                background: transparent;
                border: none;
                border-radius: 12px;
            }

            QPushButton:hover {
                background-color: rgba(255,255,255,40);
            }
            """
        )

        close_btn.clicked.connect(
            self.close
        )

        top_layout.addWidget(
            close_btn
        )


        # ----------------------------------------------------
        # BOTTOM BAR
        # ----------------------------------------------------

        self.bottom_bar = QWidget(
            self
        )

        self.bottom_bar.setGeometry(
            0,
            WINDOW_H - BOTTOM_BAR_H,
            WINDOW_W,
            BOTTOM_BAR_H
        )

        self.bottom_bar.setStyleSheet(
            "background-color: rgba(0,0,0,130);"
        )


        bottom_layout = QHBoxLayout(
            self.bottom_bar
        )

        bottom_layout.setContentsMargins(
            0,
            8,
            0,
            10
        )


        # ----------------------------------------------------
        # BUTTON STYLE
        # ----------------------------------------------------

        btn_style = """
        QPushButton {
            border: none;
            border-radius: 22px;
            background-color: rgba(35,37,48,200);
            color: white;
            font-size: 16px;
        }

        QPushButton:hover {
            background-color: rgba(46,49,64,230);
        }

        QPushButton[active="true"] {
            background-color: rgba(214,72,63,220);
        }
        """


        # ----------------------------------------------------
        # CAMERA BUTTON
        # ----------------------------------------------------

        self.camera_btn = QPushButton(
            "📷"
        )

        self.camera_btn.setFixedSize(
            40,
            40
        )

        self.camera_btn.setStyleSheet(
            btn_style
        )

        self.camera_btn.clicked.connect(
            self.toggle_camera
        )


        # ----------------------------------------------------
        # MICROPHONE BUTTON
        # ----------------------------------------------------

        self.mic_btn = QPushButton(
            "🎤"
        )

        self.mic_btn.setFixedSize(
            44,
            44
        )

        self.mic_btn.setStyleSheet(
            btn_style
        )

        self.mic_btn.clicked.connect(
            self.toggle_listening
        )


        bottom_layout.addStretch()

        bottom_layout.addWidget(
            self.camera_btn
        )

        bottom_layout.addSpacing(
            16
        )

        bottom_layout.addWidget(
            self.mic_btn
        )

        bottom_layout.addStretch()


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_label = QLabel(
            "Available...",
            self.bottom_bar
        )

        self.status_label.setGeometry(
            0,
            BOTTOM_BAR_H - 20,
            WINDOW_W,
            18
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        self.status_label.setStyleSheet(
            """
            color: #cfcfcf;
            font-size: 11px;
            background: transparent;
            """
        )


        # ----------------------------------------------------
        # STACKING
        # ----------------------------------------------------

        self.top_bar.raise_()

        self.bottom_bar.raise_()

        self._apply_rounded_mask()


    # ========================================================
    # ROUNDED WINDOW
    # ========================================================

    def _apply_rounded_mask(self):

        path = QPainterPath()

        path.addRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            CORNER_RADIUS,
            CORNER_RADIUS
        )

        self.setMask(
            QRegion(
                path.toFillPolygon().toPolygon()
            )
        )


    # ========================================================
    # DOCK BOTTOM RIGHT
    # ========================================================

    def _dock_bottom_right(self):

        screen = (
            QApplication
            .primaryScreen()
            .availableGeometry()
        )

        x = (
            screen.right()
            - WINDOW_W
            - MARGIN
        )

        y = (
            screen.bottom()
            - WINDOW_H
            - MARGIN
        )

        self.move(
            x,
            y
        )


    # ========================================================
    # DRAG WINDOW
    # ========================================================

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.LeftButton:

            self._drag_pos = (
                event.globalPos()
                -
                self.frameGeometry().topLeft()
            )

            event.accept()


    def mouseMoveEvent(
        self,
        event
    ):

        if (
            self._drag_pos is not None
            and event.buttons() == Qt.LeftButton
        ):

            self.move(
                event.globalPos()
                -
                self._drag_pos
            )

            event.accept()


    def mouseReleaseEvent(
        self,
        event
    ):

        self._drag_pos = None


    # ========================================================
    # AVATAR VIDEO
    # ========================================================

    def _start_avatar_video(self):

        path = _find_avatar_video()


        if not path:

            self.status_label.setText(
                "Drop an .mp4 into /assets"
            )

            return


        print(
            "[Avatar] Video:",
            path
        )


        self._avatar_thread = AvatarThread(

            path,

            target_size=(
                WINDOW_W,
                WINDOW_H
            )

        )


        self._avatar_thread.frame_ready.connect(
            self._on_avatar_frame
        )

        self._avatar_thread.error.connect(
            self._on_error
        )

        self._avatar_thread.start()


    def _stop_avatar_video(self):

        if self._avatar_thread is not None:

            self._avatar_thread.stop()

            self._avatar_thread.wait(
                500
            )

            self._avatar_thread = None


    def _on_avatar_frame(
        self,
        qimg: QImage
    ):

        if self._camera_active:

            return


        self.video_label.setPixmap(
            QPixmap.fromImage(
                qimg
            )
        )


    # ========================================================
    # ERROR
    # ========================================================

    def _on_error(
        self,
        message: str
    ):

        self.set_status(
            "Available..."
        )

        print(
            "[main_window]",
            message
        )


    # ========================================================
    # MICROPHONE
    # ========================================================

    def toggle_listening(self):

        # ----------------------------------------------------
        # STOP LISTENING
        # ----------------------------------------------------

        if (
            self._listen_thread is not None
            and self._listen_thread.isRunning()
        ):

            self._listen_thread.stop()

            self._listen_thread = None

            self.mic_btn.setProperty(
                "active",
                "false"
            )

            self.mic_btn.setStyle(
                self.mic_btn.style()
            )

            self.set_status(
                "Available..."
            )

            return


        # ----------------------------------------------------
        # START LISTENING
        # ----------------------------------------------------

        self._listen_thread = ListenThread(
            language=self.language
        )


        self._listen_thread.result_ready.connect(
            self._on_speech_result
        )

        self._listen_thread.state_changed.connect(
            self.set_status
        )

        self._listen_thread.error.connect(
            self._on_error
        )


        self._listen_thread.start()


        self.mic_btn.setProperty(
            "active",
            "true"
        )

        self.mic_btn.setStyle(
            self.mic_btn.style()
        )


    # ========================================================
    # SPEECH RESULT
    # ========================================================

    def _on_speech_result(
        self,
        text: str
    ):

        print(
            "[Speech]",
            text
        )

        self.set_status(
            "Thinking..."
        )

        self.handle_query(
            text
        )


    # ========================================================
    # CAMERA
    # ========================================================

    def toggle_camera(self):

        # ----------------------------------------------------
        # STOP CAMERA
        # ----------------------------------------------------

        if self._camera_thread is not None:

            self._camera_thread.stop()

            self._camera_thread.wait(
                500
            )

            self._camera_thread = None

            self._camera_active = False


            self.camera_btn.setProperty(
                "active",
                "false"
            )

            self.camera_btn.setStyle(
                self.camera_btn.style()
            )

            return


        # ----------------------------------------------------
        # START CAMERA
        # ----------------------------------------------------

        self._camera_active = True

        self._camera_thread = CameraThread()


        self._camera_thread.frame_ready.connect(
            self._on_camera_frame
        )

        self._camera_thread.error.connect(
            self._on_error
        )


        self._camera_thread.start()


        self.camera_btn.setProperty(
            "active",
            "true"
        )

        self.camera_btn.setStyle(
            self.camera_btn.style()
        )


    # ========================================================
    # CAMERA FRAME
    # ========================================================

    def _on_camera_frame(
        self,
        qimg: QImage
    ):

        if not self._camera_active:

            return


        if (
            cv2 is not None
            and np is not None
        ):

            w = qimg.width()

            h = qimg.height()

            ptr = qimg.bits()

            ptr.setsize(
                h * w * 3
            )


            rgb = np.frombuffer(
                ptr,
                dtype="uint8"
            ).reshape(
                (h, w, 3)
            )


            bgr = cv2.cvtColor(
                rgb,
                cv2.COLOR_RGB2BGR
            )


            fitted = cover_resize(
                bgr,
                WINDOW_W,
                WINDOW_H
            )


            fitted_rgb = cv2.cvtColor(
                fitted,
                cv2.COLOR_BGR2RGB
            )


            out = QImage(

                fitted_rgb.data,

                WINDOW_W,

                WINDOW_H,

                3 * WINDOW_W,

                QImage.Format_RGB888

            )


            self.video_label.setPixmap(
                QPixmap.fromImage(
                    out.copy()
                )
            )


        else:

            pixmap = (
                QPixmap
                .fromImage(qimg)
                .scaled(
                    WINDOW_W,
                    WINDOW_H,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

            self.video_label.setPixmap(
                pixmap
            )


    # ========================================================
    # QUERY HANDLING
    # ========================================================

    def handle_query(
        self,
        text: str
    ):

        """
        Send the query to the backend
        without freezing the PyQt5 UI.
        """

        self.set_status(
            "Thinking..."
        )


        thread = threading.Thread(

            target=self._process_query,

            args=(text,),

            daemon=True

        )


        thread.start()


    # ========================================================
    # BACKGROUND QUERY PROCESSING
    # ========================================================

    def _process_query(
        self,
        text: str
    ):

        response_text = None


        try:

            # ------------------------------------------------
            # CONNECTED BACKEND
            # ------------------------------------------------

            if self.on_query is not None:

                result = self.on_query(
                    text
                )

                response_text = (
                    self._extract_speak_text(
                        result
                    )
                )


            # ------------------------------------------------
            # FALLBACK LLM
            # ------------------------------------------------

            if response_text is None:

                ask_llm = _lazy_backend(
                    "llm",
                    "ask_llm"
                )


                if ask_llm is not None:

                    result = ask_llm(
                        text
                    )

                    response_text = (
                        self._extract_speak_text(
                            result
                        )
                    )


            # ------------------------------------------------
            # FINAL FALLBACK
            # ------------------------------------------------

            if response_text is None:

                response_text = (
                    f"You said: {text}"
                )


        except Exception as exc:

            print(
                "[main_window] Query error:",
                exc
            )


            response_text = (
                "Sorry, something went wrong "
                "processing that."
            )


        # ----------------------------------------------------
        # SPEAK RESPONSE
        # ----------------------------------------------------

        self._start_speaking(
            response_text
        )


    # ========================================================
    # START SPEAKING
    # ========================================================

    def _start_speaking(
        self,
        text: str
    ):

        self.set_status(
            "Answering..."
        )

        self.speak(
            text
        )


    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    @staticmethod
    def _extract_speak_text(
        result
    ):

        if result is None:

            return None


        if isinstance(
            result,
            str
        ):

            return result


        if isinstance(
            result,
            dict
        ):

            return (
                result.get("speak")
                or
                result.get("display")
                or
                result.get("response")
                or
                result.get("answer")
            )


        return str(
            result
        )


    # ========================================================
    # SPEAK
    # ========================================================

    # NOTE (perf/correctness): this is the single place that should
    # speak a reply for the GUI. backend.assistant_controller.MainExecution
    # (the normal on_query callback) now returns text WITHOUT speaking
    # it itself, so this is the only voice you'll hear in the common
    # case — previously the backend spoke the answer via edge_tts AND
    # this method spoke the same text again via pyttsx3, so replies
    # were effectively said twice back-to-back. If you wire in a
    # different backend function that does its own TTS internally,
    # don't also call self.speak() on its result, or you'll reintroduce
    # that double-speaking delay.
    def speak(
        self,
        text: str
    ):

        if not text:

            return


        print(
            "[TTS]",
            text
        )


        self._speak_thread = SpeakThread(
            text
        )


        self._speak_thread.finished_speaking.connect(

            lambda:
            self.set_status(
                "Available..."
            )

        )


        self._speak_thread.start()


    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text: str
    ):

        self.status_label.setText(
            text
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        print(
            "[MainWindow] Closing..."
        )


        if self._listen_thread is not None:

            self._listen_thread.stop()


        if self._camera_thread is not None:

            self._camera_thread.stop()


        self._stop_avatar_video()


        super().closeEvent(
            event
        )