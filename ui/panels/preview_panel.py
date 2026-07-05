from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

from ui.theme import Theme


class PreviewPanel(QWidget):
    prev_page = pyqtSignal()
    next_page = pyqtSignal()

    def __init__(self, t_func, parent=None):
        super().__init__(parent)
        self.t = t_func
        self._current_pixmap = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Preview mode label
        self.mode_label = QLabel("")
        self.mode_label.setProperty("cssClass", "muted")
        layout.addWidget(self.mode_label)

        # Stacked widget: placeholder vs image
        self.stack = QStackedWidget()

        # Placeholder
        self.placeholder = QLabel(self.t("preview_empty"))
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setWordWrap(True)
        self.placeholder.setStyleSheet(f"""
            color: {Theme.MUTED};
            padding: 40px;
            border: 2px dashed {Theme.CARD_BORDER};
            border-radius: 12px;
            background-color: {Theme.BG_SECONDARY};
        """)
        self.stack.addWidget(self.placeholder)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent;")
        self.stack.addWidget(self.image_label)

        self.stack.setCurrentIndex(0)
        layout.addWidget(self.stack, 1)

        # Navigation row
        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = QPushButton("\u25C0")
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.clicked.connect(self.prev_page)

        self.page_label = QLabel("")
        self.page_label.setProperty("cssClass", "muted")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QPushButton("\u25B6")
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.clicked.connect(self.next_page)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_btn)

        self.nav_widget = QWidget()
        self.nav_widget.setLayout(nav_layout)
        self.nav_widget.setVisible(False)
        layout.addWidget(self.nav_widget)

    def set_pixmap(self, pixmap):
        if pixmap:
            self._current_pixmap = pixmap
            scaled = pixmap.scaled(
                self.stack.currentWidget().size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled)
            self.stack.setCurrentIndex(1)
        else:
            self._current_pixmap = None
            self.stack.setCurrentIndex(0)

    def set_mode_label(self, text):
        self.mode_label.setText(text)

    def set_nav_visible(self, visible):
        self.nav_widget.setVisible(visible)

    def update_nav(self, current, total):
        self.page_label.setText(f"{current} / {total}")
        self.prev_btn.setEnabled(current > 1)
        self.next_btn.setEnabled(current < total)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_pixmap:
            scaled = self._current_pixmap.scaled(
                self.stack.currentWidget().size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled)
