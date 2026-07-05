from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor

from ui.theme import Theme


class ResultPanel(QWidget):
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, t_func, parent=None):
        super().__init__(parent)
        self.t = t_func
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header row
        header_layout = QHBoxLayout()

        self.stats_label = QLabel("")
        self.stats_label.setProperty("cssClass", "stats")
        header_layout.addWidget(self.stats_label)

        header_layout.addStretch()

        self.copy_btn = QPushButton(self.t("copy"))
        self.copy_btn.setProperty("cssClass", "primary")
        self.copy_btn.setFixedWidth(80)
        self.copy_btn.clicked.connect(self.copy_requested)
        self.copy_btn.setEnabled(False)
        header_layout.addWidget(self.copy_btn)

        self.clear_btn = QPushButton(self.t("clear"))
        self.clear_btn.setFixedWidth(80)
        self.clear_btn.clicked.connect(self.clear_requested)
        self.clear_btn.setEnabled(False)
        header_layout.addWidget(self.clear_btn)

        layout.addLayout(header_layout)

        # Result text area
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText(self.t("result_empty"))
        self.result_text.setReadOnly(False)
        self.result_text.textChanged.connect(self._update_stats)
        layout.addWidget(self.result_text, 1)

    def _update_stats(self):
        text = self.result_text.toPlainText()
        stripped = text.strip()
        if not stripped:
            self.stats_label.setText("")
            return
        self.stats_label.setText(
            self.t("result_stats").format(
                words=len(stripped.split()),
                chars=len(text),
                lines=text.count("\n") + 1,
            )
        )

    def set_text(self, text):
        self.result_text.setPlainText(text)
        has_text = bool(text.strip())
        self.copy_btn.setEnabled(has_text)
        self.clear_btn.setEnabled(has_text)

    def get_text(self):
        return self.result_text.toPlainText()

    def clear(self):
        self.result_text.clear()
        self.copy_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)

    def set_buttons_enabled(self, enabled):
        self.copy_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)

    def update_texts(self, t_func):
        self.t = t_func
        self.result_text.setPlaceholderText(self.t("result_empty"))
        self.copy_btn.setText(self.t("copy"))
        self.clear_btn.setText(self.t("clear"))
