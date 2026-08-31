"""
ui/settings_window.py
----------------------
Native replacement for settings.html's panel.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QLabel
)


class SettingsWindow(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowTitle("Settings")
        self.setFixedSize(320, 260)
        self.setStyleSheet("""
            QWidget { background-color: #0a0a0c; color: white; font-family: Segoe UI, Arial; }
            QLineEdit, QComboBox {
                background: #1a1a1e; border: 1px solid #333; border-radius: 6px;
                padding: 6px; color: white;
            }
            QPushButton {
                background-color: #4e97eb; border: none; border-radius: 8px;
                padding: 8px; color: white; font-weight: 600;
            }
            QPushButton:hover { background-color: #3d7fd1; }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Assistant Settings"))

        form = QFormLayout()

        self.name_input = QLineEdit(self.main_window.assistant_name)
        form.addRow("Assistant name", self.name_input)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["en-US", "en-GB", "hi-IN", "es-ES", "fr-FR"])
        idx = self.language_combo.findText(self.main_window.language)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)
        form.addRow("Language", self.language_combo)

        layout.addLayout(form)
        layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def save(self):
        self.main_window.assistant_name = self.name_input.text().strip() or "Assistant"
        self.main_window.title_label.setText(self.main_window.assistant_name)
        self.main_window.language = self.language_combo.currentText()
        self.main_window.append_message("Assistant", "Settings saved.")
        self.close()
