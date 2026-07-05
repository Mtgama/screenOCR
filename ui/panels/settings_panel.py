from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QLineEdit, QGridLayout, QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui.theme import Theme


class SettingsPanel(QWidget):
    settings_changed = pyqtSignal()
    auto_psm_changed = pyqtSignal(bool)
    ocr_mode_changed = pyqtSignal(str)

    def __init__(self, t_func, parent=None):
        super().__init__(parent)
        self.t = t_func
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Grid layout for settings
        grid = QGridLayout()
        grid.setSpacing(10)

        # OCR Language
        lang_label = QLabel(self.t("ocr_lang"))
        lang_label.setProperty("cssClass", "muted")
        grid.addWidget(lang_label, 0, 0)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([self.t("lang_fas_eng"), self.t("lang_fas")])
        self.lang_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(self.lang_combo, 0, 1)

        # OCR Mode
        mode_label = QLabel(self.t("ocr_mode"))
        mode_label.setProperty("cssClass", "muted")
        grid.addWidget(mode_label, 1, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([self.t("ocr_accurate"), self.t("ocr_fast")])
        self.mode_combo.currentIndexChanged.connect(self._on_ocr_mode_changed)
        grid.addWidget(self.mode_combo, 1, 1)

        # Page Layout
        psm_label = QLabel(self.t("page_layout"))
        psm_label.setProperty("cssClass", "muted")
        grid.addWidget(psm_label, 2, 0)
        self.psm_combo = QComboBox()
        self.psm_combo.addItems([
            self.t("psm_3"), self.t("psm_6"),
            self.t("psm_7"), self.t("psm_11"),
        ])
        self.psm_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(self.psm_combo, 2, 1)

        # Page Range
        range_label = QLabel(self.t("page_range"))
        range_label.setProperty("cssClass", "muted")
        grid.addWidget(range_label, 3, 0)
        range_layout = QHBoxLayout()
        range_layout.setSpacing(6)
        self.page_from_label = QLabel(self.t("from_page"))
        self.page_from_label.setProperty("cssClass", "muted")
        range_layout.addWidget(self.page_from_label)
        self.page_from = QLineEdit("1")
        self.page_from.setFixedWidth(60)
        self.page_from.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_from.textChanged.connect(self._on_changed)
        range_layout.addWidget(self.page_from)
        self.page_to_label = QLabel(self.t("to_page"))
        self.page_to_label.setProperty("cssClass", "muted")
        range_layout.addWidget(self.page_to_label)
        self.page_to = QLineEdit("1")
        self.page_to.setFixedWidth(60)
        self.page_to.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_to.textChanged.connect(self._on_changed)
        range_layout.addWidget(self.page_to)
        range_layout.addStretch()
        grid.addLayout(range_layout, 3, 1)

        layout.addLayout(grid)

        # Checkboxes
        self.preprocess_check = QCheckBox(self.t("preprocess"))
        self.preprocess_check.setChecked(True)
        self.preprocess_check.stateChanged.connect(self._on_changed)
        layout.addWidget(self.preprocess_check)

        self.binarize_check = QCheckBox(self.t("binarize"))
        self.binarize_check.stateChanged.connect(self._on_changed)
        layout.addWidget(self.binarize_check)

        self.auto_psm_check = QCheckBox(self.t("auto_psm"))
        self.auto_psm_check.setChecked(True)
        self.auto_psm_check.stateChanged.connect(self._on_auto_psm)
        layout.addWidget(self.auto_psm_check)

        self.show_preprocessed_check = QCheckBox(self.t("show_preprocessed"))
        self.show_preprocessed_check.stateChanged.connect(self._on_changed)
        layout.addWidget(self.show_preprocessed_check)

        # PSM hint
        self.psm_hint = QLabel("")
        self.psm_hint.setProperty("cssClass", "accent")
        layout.addWidget(self.psm_hint)

    def _on_changed(self):
        self.settings_changed.emit()

    def _on_auto_psm(self, state):
        checked = (state == 2)  # Qt.CheckState.Checked
        self.auto_psm_changed.emit(checked)
        self.settings_changed.emit()

    def _on_ocr_mode_changed(self):
        self.ocr_mode_changed.emit(self.get_ocr_mode())
        self.settings_changed.emit()

    def get_ocr_lang_key(self):
        idx = self.lang_combo.currentIndex()
        return "fas+eng" if idx == 0 else "fas"

    def get_psm_value(self):
        idx = self.psm_combo.currentIndex()
        values = ["3", "6", "7", "11"]
        return values[idx] if idx < len(values) else "3"

    def get_ocr_mode(self):
        idx = self.mode_combo.currentIndex()
        return "accurate" if idx == 0 else "fast"

    def get_page_range(self):
        try:
            page_from = int(self.page_from.text() or "1")
        except ValueError:
            page_from = 1
        try:
            page_to = int(self.page_to.text() or "1")
        except ValueError:
            page_to = 1
        return page_from, page_to

    def set_page_range(self, page_from, page_to):
        self.page_from.setText(str(page_from))
        self.page_to.setText(str(page_to))

    def set_psm_hint(self, text):
        self.psm_hint.setText(text)

    def set_psm_value(self, value):
        values = ["3", "6", "7", "11"]
        try:
            idx = values.index(str(value))
            self.psm_combo.setCurrentIndex(idx)
        except ValueError:
            pass

    def set_ocr_lang(self, key):
        self.lang_combo.setCurrentIndex(0 if key == "fas+eng" else 1)

    def set_ocr_mode(self, mode):
        self.mode_combo.setCurrentIndex(0 if mode == "accurate" else 1)

    def set_preprocess(self, value):
        self.preprocess_check.setChecked(value)

    def set_binarize(self, value):
        self.binarize_check.setChecked(value)

    def set_auto_psm(self, value):
        self.auto_psm_check.setChecked(value)

    def set_show_preprocessed(self, value):
        self.show_preprocessed_check.setChecked(value)

    def update_texts(self, t_func):
        self.t = t_func
        # Update combo items
        self.lang_combo.clear()
        self.lang_combo.addItems([self.t("lang_fas_eng"), self.t("lang_fas")])
        self.mode_combo.clear()
        self.mode_combo.addItems([self.t("ocr_accurate"), self.t("ocr_fast")])
        self.psm_combo.clear()
        self.psm_combo.addItems([
            self.t("psm_3"), self.t("psm_6"),
            self.t("psm_7"), self.t("psm_11"),
        ])
        # Update labels
        for widget in self.findChildren(QLabel):
            if widget == self.psm_hint:
                continue
            text = widget.text()
            for key in ["ocr_lang", "ocr_mode", "page_layout", "page_range", "from_page", "to_page"]:
                if text == self.t(key):
                    pass  # Already correct
        self.preprocess_check.setText(self.t("preprocess"))
        self.binarize_check.setText(self.t("binarize"))
        self.auto_psm_check.setText(self.t("auto_psm"))
        self.show_preprocessed_check.setText(self.t("show_preprocessed"))
