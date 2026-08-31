# """
# core/camera.py
# --------------
# Optional webcam feed, replacing the old getUserMedia()/startVideo()/
# stopVideo()/capture() functions in home.html.
# """

# from PyQt5.QtCore import QThread, pyqtSignal
# from PyQt5.QtGui import QImage

# try:
#     import cv2
# except ImportError:
#     cv2 = None


# class CameraThread(QThread):
#     frame_ready = pyqtSignal(QImage)
#     error = pyqtSignal(str)

#     def __init__(self, camera_index: int = 0, parent=None):
#         super().__init__(parent)
#         self.camera_index = camera_index
#         self._running = False
#         self._last_frame = None  # BGR numpy array, for capture()

#     def run(self):
#         if cv2 is None:
#             self.error.emit("opencv-python is not installed. Run: pip install opencv-python")
#             return

#         cap = cv2.VideoCapture(self.camera_index)
#         if not cap.isOpened():
#             self.error.emit("Could not open webcam.")
#             return

#         self._running = True
#         while self._running:
#             ok, frame = cap.read()
#             if not ok:
#                 continue
#             self._last_frame = frame
#             rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             h, w, ch = rgb.shape
#             qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
#             self.frame_ready.emit(qimg.copy())
#             self.msleep(30)  # ~30 fps cap

#         cap.release()

#     def stop(self):
#         self._running = False

#     def capture_still(self, path: str) -> bool:
#         """Save the most recent frame to disk. Returns True on success."""
#         if self._last_frame is None or cv2 is None:
#             return False
#         return cv2.imwrite(path, self._last_frame)


"""
core/camera.py
--------------
Optional webcam feed, replacing the old getUserMedia()/startVideo()/
stopVideo()/capture() functions in home.html.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

try:
    import cv2
except ImportError:
    cv2 = None


class CameraThread(QThread):
    frame_ready = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, camera_index: int = 0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._running = False
        self._last_frame = None  # BGR numpy array, for capture()

    def run(self):
        if cv2 is None:
            self.error.emit("opencv-python is not installed. Run: pip install opencv-python")
            return

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.error.emit("Could not open webcam.")
            return

        self._running = True
        while self._running:
            ok, frame = cap.read()
            if not ok:
                continue
            self._last_frame = frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(qimg.copy())
            self.msleep(30)  # ~30 fps cap

        cap.release()

    def stop(self):
        self._running = False

    def capture_still(self, path: str) -> bool:
        """Save the most recent frame to disk. Returns True on success."""
        if self._last_frame is None or cv2 is None:
            return False
        return cv2.imwrite(path, self._last_frame)