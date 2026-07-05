import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor

from ui.theme import Theme


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._max_entries = 100

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.log_area = QScrollArea()
        self.log_area.setWidgetResizable(True)
        self.log_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Theme.LOG_BG};
                border: 1px solid {Theme.CARD_BORDER};
                border-radius: 10px;
                padding: 4px;
            }}
        """)

        self.log_container = QWidget()
        self.log_container.setStyleSheet(f"background-color: {Theme.LOG_BG};")
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setContentsMargins(8, 8, 8, 8)
        self.log_layout.setSpacing(4)
        self.log_layout.addStretch()

        self.log_area.setWidget(self.log_container)
        layout.addWidget(self.log_area)

    def _add_entry(self, message, level="info"):
        icons = {
            "info": "\u2139",
            "success": "\u2713",
            "error": "\u2717",
            "warning": "\u26A0",
        }
        colors = {
            "info": Theme.INFO,
            "success": Theme.SUCCESS,
            "error": Theme.DANGER,
            "warning": Theme.WARNING,
        }

        stamp = time.strftime("%H:%M:%S")
        icon = icons.get(level, "\u2139")
        color = colors.get(level, Theme.TEXT)

        entry = QHBoxLayout()
        entry.setSpacing(8)

        # Timestamp
        time_label = QLabel(stamp)
        time_label.setStyleSheet(f"color: {Theme.MUTED}; font-size: 11px; font-family: monospace; background: transparent;")
        time_label.setFixedWidth(58)
        entry.addWidget(time_label)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"color: {color}; font-size: 14px; background: transparent;")
        icon_label.setFixedWidth(18)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        entry.addWidget(icon_label)

        # Message
        msg_label = QLabel(message)
        msg_label.setStyleSheet(f"color: {color}; font-size: 12px; background: transparent;")
        msg_label.setWordWrap(True)
        entry.addWidget(msg_label, 1)

        # Container widget
        container = QWidget()
        container.setStyleSheet(f"""
            background-color: {Theme.LOG_ROW};
            border-radius: 8px;
        """)
        container.setLayout(entry)
        container.setMinimumHeight(32)

        # Insert before the stretch
        self.log_layout.insertWidget(self.log_layout.count() - 1, container)

        # Limit entries
        while self.log_layout.count() - 1 > self._max_entries:
            item = self.log_layout.itemAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        # Auto-scroll
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def log_info(self, message):
        self._add_entry(message, "info")

    def log_success(self, message):
        self._add_entry(message, "success")

    def log_error(self, message):
        self._add_entry(message, "error")

    def log_warning(self, message):
        self._add_entry(message, "warning")

    def clear(self):
        while self.log_layout.count() > 1:
            item = self.log_layout.itemAt(0)
            if item and item.widget():
                item.widget().deleteLater()
            elif item:
                self.log_layout.removeItem(item)
            else:
                break
