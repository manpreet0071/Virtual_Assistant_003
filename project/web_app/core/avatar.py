"""
core/avatar.py
---------------
Plays and loops the avatar video using OpenCV instead of PyQt5's
QMediaPlayer/QtMultimedia. QMediaPlayer relies on Windows DirectShow
under the hood, which frequently fails on ordinary .mp4 files with
errors like:

    DirectShowPlayerService::doRender: Unresolved error code 0x80040266

OpenCV's VideoCapture doesn't have that problem, and it's the same
library core/camera.py already uses successfully for the webcam — so
this keeps both video sources consistent and reliable.

Frames are resized/cropped to exactly fill the target box (like CSS
`background-size: cover`), so the video fills the whole widget with no
letterboxing.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

try:
    import cv2
except ImportError:
    cv2 = None


def cover_resize(frame, target_w: int, target_h: int):
    """Resize + center-crop a BGR frame to exactly (target_w, target_h),
    filling the whole area without distorting the aspect ratio."""
    h, w = frame.shape[:2]
    if w == 0 or h == 0:
        return frame
    scale = max(target_w / w, target_h / h)
    new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    x0 = max(0, (new_w - target_w) // 2)
    y0 = max(0, (new_h - target_h) // 2)
    return resized[y0:y0 + target_h, x0:x0 + target_w]


class AvatarThread(QThread):
    frame_ready = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, path: str, target_size: tuple[int, int], parent=None):
        super().__init__(parent)
        self.path = path
        self.target_w, self.target_h = target_size
        self._running = False

    def run(self):
        if cv2 is None:
            self.error.emit("opencv-python is not installed. Run: pip install opencv-python")
            return

        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            self.error.emit(f"Could not open avatar video: {self.path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        delay_ms = max(int(1000 / fps), 16)

        self._running = True
        while self._running:
            ok, frame = cap.read()
            if not ok:
                # End of clip (or a decode hiccup) -> loop back to the start
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cover_resize(frame, self.target_w, self.target_h)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(qimg.copy())
            self.msleep(delay_ms)

        cap.release()

    def stop(self):
        self._running = False