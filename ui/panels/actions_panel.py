from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QCursor

from ui.theme import Theme


class ActionsPanel(QWidget):
    file_selected = pyqtSignal()
    folder_selected = pyqtSignal()
    screenshot_full = pyqtSignal()
    screenshot_region = pyqtSignal()
    ocr_requested = pyqtSignal()
    ocr_stopped = pyqtSignal()
    save_requested = pyqtSignal()

    def __init__(self, t_func, parent=None):
        super().__init__(parent)
        self.t = t_func
        self._menu_visible = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Status text
        self.status_label = QLabel(self.t("status_default"))
        self.status_label.setProperty("cssClass", "status")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Shortcuts hint
        self.shortcuts_label = QLabel(self.t("shortcuts"))
        self.shortcuts_label.setProperty("cssClass", "muted")
        layout.addWidget(self.shortcuts_label)

        # Action buttons row 1
        btn_layout1 = QHBoxLayout()
        btn_layout1.setSpacing(8)

        self.select_file_btn = QPushButton(f"  {self.t('select_file')}")
        self.select_file_btn.setProperty("cssClass", "primary")
        self.select_file_btn.setMinimumHeight(40)
        self.select_file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.select_file_btn.clicked.connect(self.file_selected)
        btn_layout1.addWidget(self.select_file_btn)

        self.select_folder_btn = QPushButton(f"  {self.t('select_folder')}")
        self.select_folder_btn.setMinimumHeight(40)
        self.select_folder_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.select_folder_btn.clicked.connect(self.folder_selected)
        btn_layout1.addWidget(self.select_folder_btn)

        self.screenshot_btn = QPushButton(f"  {self.t('screenshot')}")
        self.screenshot_btn.setMinimumHeight(40)
        self.screenshot_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.screenshot_btn.setCheckable(True)
        self.screenshot_btn.toggled.connect(self._toggle_screenshot_menu)
        btn_layout1.addWidget(self.screenshot_btn)

        layout.addLayout(btn_layout1)

        # Floating screenshot popup (parented to the main window, not in layout)
        self._create_screenshot_popup()

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {Theme.CARD_BORDER}; max-height: 1px;")
        layout.addWidget(line)

        # Action buttons row 2
        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(8)

        self.run_btn = QPushButton(f"  {self.t('run')}")
        self.run_btn.setProperty("cssClass", "primary")
        self.run_btn.setMinimumHeight(42)
        self.run_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.ocr_requested)
        btn_layout2.addWidget(self.run_btn)

        self.stop_btn = QPushButton(f"  {self.t('stop')}")
        self.stop_btn.setProperty("cssClass", "danger")
        self.stop_btn.setMinimumHeight(42)
        self.stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.ocr_stopped)
        btn_layout2.addWidget(self.stop_btn)

        self.save_btn = QPushButton(f"  {self.t('save')}")
        self.save_btn.setMinimumHeight(42)
        self.save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_requested)
        btn_layout2.addWidget(self.save_btn)

        layout.addLayout(btn_layout2)

        # Progress bar
        from PyQt6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setProperty("cssClass", "muted")
        layout.addWidget(self.progress_label)

    def _create_screenshot_popup(self):
        """Create floating screenshot menu as a top-level popup widget."""
        self._screenshot_popup = QWidget(
            None,
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool,
        )
        self._screenshot_popup.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.CARD_BORDER};
                border-radius: 8px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 8px 20px;
                border-radius: 0px;
                color: {Theme.TEXT};
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_SOFT};
            }}
        """)

        popup_layout = QVBoxLayout(self._screenshot_popup)
        popup_layout.setContentsMargins(0, 4, 0, 4)
        popup_layout.setSpacing(0)

        self._popup_full_btn = QPushButton(f"  {self.t('screenshot_full')}")
        self._popup_full_btn.setMinimumHeight(36)
        self._popup_full_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._popup_full_btn.clicked.connect(self._on_full_clicked)
        popup_layout.addWidget(self._popup_full_btn)

        self._popup_region_btn = QPushButton(f"  {self.t('screenshot_region')}")
        self._popup_region_btn.setMinimumHeight(36)
        self._popup_region_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._popup_region_btn.clicked.connect(self._on_region_clicked)
        popup_layout.addWidget(self._popup_region_btn)

    def _toggle_screenshot_menu(self, checked):
        if checked:
            self._show_screenshot_popup()
        else:
            self._hide_screenshot_popup()

    def _show_screenshot_popup(self):
        # Position the popup below the screenshot button
        btn = self.screenshot_btn
        global_pos = btn.mapToGlobal(QPoint(0, btn.height()))
        self._screenshot_popup.move(global_pos)
        self._screenshot_popup.show()
        self._menu_visible = True

    def _hide_screenshot_popup(self):
        self._screenshot_popup.hide()
        self._menu_visible = False

    def _on_full_clicked(self):
        self._hide_screenshot_popup()
        self.screenshot_btn.setChecked(False)
        self.screenshot_full.emit()

    def _on_region_clicked(self):
        self._hide_screenshot_popup()
        self.screenshot_btn.setChecked(False)
        self.screenshot_region.emit()

    def close_screenshot_menu(self):
        self._hide_screenshot_popup()
        self.screenshot_btn.setChecked(False)

    def set_status(self, text, level="info"):
        colors = {
            "info": Theme.INFO,
            "success": Theme.SUCCESS,
            "error": Theme.DANGER,
            "warning": Theme.WARNING,
        }
        color = colors.get(level, Theme.TEXT)
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 500; padding: 4px 8px; background: transparent;")

    def set_progress(self, value, text=""):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(int(value * 100))
        self.progress_label.setText(text)

    def hide_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")

    def set_ocr_buttons(self, running):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.select_file_btn.setEnabled(not running)
        self.select_folder_btn.setEnabled(not running)
        self.screenshot_btn.setEnabled(not running)
        self.save_btn.setEnabled(False)

    def set_save_enabled(self, enabled):
        self.save_btn.setEnabled(enabled)

    def set_run_enabled(self, enabled):
        self.run_btn.setEnabled(enabled)

    def update_texts(self, t_func):
        self.t = t_func
        self.status_label.setText(self.t("status_default"))
        self.shortcuts_label.setText(self.t("shortcuts"))
        self.select_file_btn.setText(f"  {self.t('select_file')}")
        self.select_folder_btn.setText(f"  {self.t('select_folder')}")
        self.screenshot_btn.setText(f"  {self.t('screenshot')}")
        self._popup_full_btn.setText(f"  {self.t('screenshot_full')}")
        self._popup_region_btn.setText(f"  {self.t('screenshot_region')}")
        self.run_btn.setText(f"  {self.t('run')}")
        self.stop_btn.setText(f"  {self.t('stop')}")
        self.save_btn.setText(f"  {self.t('save')}")
