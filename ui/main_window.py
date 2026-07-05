import os
import sys
import tempfile
import threading
from io import BytesIO

from PIL import Image
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QFileDialog, QApplication,
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence, QDragEnterEvent, QDropEvent

from ui.theme import Theme
from ui.panels.preview_panel import PreviewPanel
from ui.panels.result_panel import ResultPanel
from ui.panels.settings_panel import SettingsPanel
from ui.panels.actions_panel import ActionsPanel
from ui.panels.log_panel import LogPanel
from ui.screenshot import RegionSelector
from ui.workers import OcrWorker, image_to_pixmap
from core.image_processor import preprocess_image, suggest_psm
from core.pdf_handler import pdf_to_images, get_pdf_page_count
from core.ocr_engine import build_tesseract_config, get_psm_reason_label, resolve_tesseract_path
from core.export_manager import save_export
from utils.i18n import TEXT, PSM_REASONS, APP_VERSION, APP_AUTHOR, APP_GITHUB, SUPPORTED_EXTENSIONS, EXPORT_EXTENSIONS
from settings import load_settings, save_settings
from tessdata_manager import ensure_model_store, trim_unused_tessdata, apply_ocr_mode


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "fa"
        self.file_path = None
        self.is_pdf = False
        self.pdf_page_count = 0
        self.preview_page = 1
        self.cancel_event = threading.Event()
        self.ocr_running = False
        self.batch_files = []
        self.ocr_worker = None
        self._pending_screenshot = None

        # Initialize tessdata
        ensure_model_store()
        trim_unused_tessdata()

        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._load_settings()
        self._apply_language()

    def t(self, key):
        return TEXT[self.language].get(key, key)

    def _setup_window(self):
        self.setWindowTitle(self.t("title"))
        self.setMinimumSize(900, 700)
        self.resize(1000, 850)
        self.setAcceptDrops(True)

        # Try to set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icon.ico")
        if os.path.isfile(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header
        main_layout.addWidget(self._build_header())

        # Actions panel
        self.actions_panel = ActionsPanel(self.t)
        self.actions_panel.file_selected.connect(self._pick_file)
        self.actions_panel.folder_selected.connect(self._pick_folder)
        self.actions_panel.screenshot_full.connect(self._screenshot_full)
        self.actions_panel.screenshot_region.connect(self._screenshot_region)
        self.actions_panel.ocr_requested.connect(self._run_ocr)
        self.actions_panel.ocr_stopped.connect(self._stop_ocr)
        self.actions_panel.save_requested.connect(self._save_output)
        main_layout.addWidget(self.actions_panel)

        # Content area: Preview + Result in splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)

        # Preview card
        preview_group = QGroupBox(self.t("preview"))
        preview_group.setProperty("i18n_key", "preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_panel = PreviewPanel(self.t)
        self.preview_panel.prev_page.connect(self._prev_preview_page)
        self.preview_panel.next_page.connect(self._next_preview_page)
        preview_layout.addWidget(self.preview_panel)
        splitter.addWidget(preview_group)

        # Result card
        result_group = QGroupBox(self.t("result"))
        result_group.setProperty("i18n_key", "result")
        result_layout = QVBoxLayout(result_group)
        self.result_panel = ResultPanel(self.t)
        self.result_panel.copy_requested.connect(self._copy_output)
        self.result_panel.clear_requested.connect(self._clear_output)
        result_layout.addWidget(self.result_panel)
        splitter.addWidget(result_group)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        # Settings panel
        settings_group = QGroupBox(self.t("settings"))
        settings_group.setProperty("i18n_key", "settings")
        settings_layout = QVBoxLayout(settings_group)
        self.settings_panel = SettingsPanel(self.t)
        self.settings_panel.settings_changed.connect(self._on_settings_changed)
        self.settings_panel.auto_psm_changed.connect(self._on_auto_psm_changed)
        self.settings_panel.ocr_mode_changed.connect(self._on_ocr_mode_changed)
        settings_layout.addWidget(self.settings_panel)
        splitter.addWidget(settings_group)

        main_layout.addWidget(splitter, 1)

        # Log panel
        log_group = QGroupBox(self.t("log"))
        log_group.setProperty("i18n_key", "log")
        log_layout = QVBoxLayout(log_group)
        self.log_panel = LogPanel()
        log_layout.addWidget(self.log_panel)
        log_group.setFixedHeight(200)
        main_layout.addWidget(log_group)

    def _build_header(self):
        header = QWidget()
        header.setStyleSheet(f"""
            background: {Theme.HEADER_BG};
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 12px;
            padding: 12px 18px;
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 12, 18, 12)

        # App icon
        icon_label = QLabel("\u2318")
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            color: {Theme.PRIMARY};
            background-color: {Theme.PRIMARY_SOFT};
            border-radius: 10px;
            padding: 8px;
        """)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        layout.addSpacing(12)

        # Title and version
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        title_label = QLabel(self.t("brand"))
        title_label.setProperty("cssClass", "header-title")
        text_layout.addWidget(title_label)
        version_label = QLabel(self.t("version"))
        version_label.setProperty("cssClass", "header-version")
        text_layout.addWidget(version_label)
        # Author
        author_layout = QHBoxLayout()
        author_layout.setSpacing(6)
        author_label = QLabel(self.t("author_by").format(name=APP_AUTHOR))
        author_label.setStyleSheet(f"color: {Theme.MUTED}; font-size: 11px; background: transparent;")
        author_layout.addWidget(author_label)
        self.github_btn = QPushButton(self.t("author_link"))
        self.github_btn.setStyleSheet(f"""
            color: {Theme.PRIMARY};
            font-size: 11px;
            background: transparent;
            border: none;
            padding: 0;
        """)
        self.github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_btn.clicked.connect(self._open_github)
        author_layout.addWidget(self.github_btn)
        author_layout.addStretch()
        text_layout.addLayout(author_layout)
        layout.addLayout(text_layout, 1)

        # Language toggle
        self.lang_btn = QPushButton(self.t("lang_switch"))
        self.lang_btn.setMinimumWidth(80)
        self.lang_btn.clicked.connect(self._toggle_language)
        layout.addWidget(self.lang_btn)

        return header

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self, self._pick_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_output)
        QShortcut(QKeySequence("Ctrl+C"), self, self._copy_output)
        QShortcut(QKeySequence("F5"), self, self._run_ocr)

    # --- Drag & Drop ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    ext = os.path.splitext(url.toLocalFile())[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        event.acceptProposedAction()
                        self.actions_panel.set_status(self.t("drop_files_here"), "info")
                        return

    def dragLeaveEvent(self, event):
        self.actions_panel.set_status(self.t("status_default"), "info")

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                ext = os.path.splitext(path)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    self.batch_files = []
                    self._load_file(path)
                    return

    # --- File operations ---
    def _pick_file(self):
        exts = " ".join(f"*{e}" for e in SUPPORTED_EXTENSIONS)
        path, _ = QFileDialog.getOpenFileName(
            self, self.t("select_file"), "",
            f"Supported Files ({exts});;All Files (*)",
        )
        if path:
            self.batch_files = []
            self._load_file(path)

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t("select_folder"))
        if not folder:
            return
        files = []
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS:
                files.append(path)
        if not files:
            self.log_panel.log_error(self.t("no_files_found"))
            return
        self.batch_files = files
        self.log_panel.log_info(self.t("folder_selected").format(count=len(files)))
        self._start_ocr(batch_files=files)

    def _load_file(self, file_path):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        self.is_pdf = ext == ".pdf"
        self.preview_page = 1
        name = os.path.basename(file_path)

        if self.is_pdf:
            self.pdf_page_count = get_pdf_page_count(file_path)
            self.settings_panel.set_page_range(1, self.pdf_page_count)
            self.preview_panel.set_nav_visible(True)
            self._update_preview_nav()
            self.actions_panel.set_status(self.t("pdf_selected").format(name=name), "info")
            self.log_panel.log_info(self.t("pdf_selected").format(name=name))
        else:
            self.pdf_page_count = 0
            self.preview_panel.set_nav_visible(False)
            self.actions_panel.set_status(self.t("image_selected").format(name=name), "info")
            self.log_panel.log_info(self.t("image_selected").format(name=name))

        self._suggest_psm_for_file()
        self._render_preview()
        self.actions_panel.set_run_enabled(True)
        self.result_panel.clear()
        self.actions_panel.hide_progress()

    # --- Preview ---
    def _get_source_image(self):
        if not self.file_path:
            return None
        if self.is_pdf:
            images = pdf_to_images(
                self.file_path, dpi=120,
                first_page=self.preview_page, last_page=self.preview_page,
            )
            return images[0] if images else None
        with Image.open(self.file_path) as img:
            return img.copy()

    def _render_preview(self):
        if not self.file_path:
            return
        try:
            if self.is_pdf:
                images = pdf_to_images(
                    self.file_path, dpi=120,
                    first_page=self.preview_page, last_page=self.preview_page,
                )
                image = images[0] if images else None
            else:
                with Image.open(self.file_path) as img:
                    image = img.copy()

            if not image:
                self.preview_panel.set_pixmap(None)
                return

            show_processed = (
                self.settings_panel.show_preprocessed_check.isChecked()
                and self.settings_panel.preprocess_check.isChecked()
            )
            if show_processed:
                image = preprocess_image(
                    image,
                    binarize=self.settings_panel.binarize_check.isChecked(),
                    upscale=True,
                )
                self.preview_panel.set_mode_label(self.t("preview_preprocessed"))
            else:
                self.preview_panel.set_mode_label(self.t("preview_original"))

            pixmap = image_to_pixmap(image)
            self.preview_panel.set_pixmap(pixmap)
        except Exception:
            self.preview_panel.set_pixmap(None)
            self.preview_panel.set_mode_label("")

    def _update_preview_nav(self):
        self.preview_panel.update_nav(self.preview_page, max(self.pdf_page_count, 1))

    def _prev_preview_page(self):
        if self.preview_page > 1:
            self.preview_page -= 1
            self._update_preview_nav()
            if self.settings_panel.auto_psm_check.isChecked():
                self._suggest_psm_for_file()
            self._render_preview()

    def _next_preview_page(self):
        if self.preview_page < self.pdf_page_count:
            self.preview_page += 1
            self._update_preview_nav()
            if self.settings_panel.auto_psm_check.isChecked():
                self._suggest_psm_for_file()
            self._render_preview()

    # --- PSM suggestion ---
    def _suggest_psm_for_file(self, log=True):
        if not self.settings_panel.auto_psm_check.isChecked() or not self.file_path:
            self.settings_panel.set_psm_hint("")
            return
        try:
            if self.is_pdf:
                images = pdf_to_images(
                    self.file_path, dpi=120,
                    first_page=self.preview_page, last_page=self.preview_page,
                )
                image = images[0] if images else None
            else:
                with Image.open(self.file_path) as img:
                    image = img.copy()

            if not image:
                return
            psm, reason = suggest_psm(image)
            self.settings_panel.set_psm_value(psm)
            reason_label = get_psm_reason_label(reason, self.language)
            hint = self.t("psm_suggested").format(psm=psm, reason=reason_label)
            self.settings_panel.set_psm_hint(hint)
            self._persist_settings()
            if log:
                self.log_panel.log_info(hint)
        except Exception:
            self.settings_panel.set_psm_hint("")

    # --- Settings ---
    def _load_settings(self):
        settings = load_settings()
        self.language = settings.get("ui_language", "fa")
        self.settings_panel.set_ocr_lang(settings.get("ocr_lang", "fas+eng"))
        self.settings_panel.set_psm_value(settings.get("psm", "3"))
        self.settings_panel.set_preprocess(settings.get("preprocess", True))
        self.settings_panel.set_binarize(settings.get("binarize", False))
        self.settings_panel.set_auto_psm(settings.get("auto_psm", True))
        self.settings_panel.set_show_preprocessed(settings.get("show_preprocessed", False))
        self.settings_panel.set_ocr_mode(settings.get("ocr_mode", "accurate"))
        apply_ocr_mode(settings.get("ocr_mode", "accurate"))

    def _persist_settings(self):
        page_from, page_to = self.settings_panel.get_page_range()
        save_settings({
            "ui_language": self.language,
            "ocr_lang": self.settings_panel.get_ocr_lang_key(),
            "psm": self.settings_panel.get_psm_value(),
            "preprocess": self.settings_panel.preprocess_check.isChecked(),
            "binarize": self.settings_panel.binarize_check.isChecked(),
            "auto_psm": self.settings_panel.auto_psm_check.isChecked(),
            "show_preprocessed": self.settings_panel.show_preprocessed_check.isChecked(),
            "export_format": "txt",
            "ocr_mode": self.settings_panel.get_ocr_mode(),
        })

    def _on_settings_changed(self):
        self._persist_settings()
        if self.file_path:
            self._render_preview()

    def _on_auto_psm_changed(self, checked):
        if checked:
            self._suggest_psm_for_file()
        else:
            self.settings_panel.set_psm_hint("")

    def _on_ocr_mode_changed(self, mode):
        apply_ocr_mode(mode)
        self._persist_settings()
        label = self.t("ocr_fast") if mode == "fast" else self.t("ocr_accurate")
        self.log_panel.log_info(label)

    # --- OCR ---
    def _run_ocr(self):
        if not self.file_path or self.ocr_running:
            return
        self._start_ocr()

    def _start_ocr(self, batch_files=None):
        if self.ocr_running:
            return

        resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tesseract_path = resolve_tesseract_path(resource_dir)

        if not tesseract_path:
            self.log_panel.log_error(self.t("tesseract_missing"))
            self.actions_panel.set_status(self.t("tesseract_missing_title"), "error")
            return

        options = {
            "lang": self.settings_panel.get_ocr_lang_key(),
            "tesseract_config": build_tesseract_config(psm=int(self.settings_panel.get_psm_value())),
            "preprocess": self.settings_panel.preprocess_check.isChecked(),
            "binarize": self.settings_panel.binarize_check.isChecked(),
            "auto_psm": self.settings_panel.auto_psm_check.isChecked(),
            "page_from": self.settings_panel.get_page_range()[0],
            "page_to": self.settings_panel.get_page_range()[1],
        }

        if batch_files:
            files = batch_files
        elif self.file_path:
            files = []
        else:
            return

        if not files and options["page_from"] > options["page_to"]:
            self.log_panel.log_error(self.t("invalid_page_range"))
            return

        self.ocr_running = True
        self.cancel_event.clear()
        self.actions_panel.set_ocr_buttons(True)
        self.result_panel.clear()
        self.actions_panel.set_progress(0, "")
        self.actions_panel.set_status(self.t("ocr_started"), "info")
        self.log_panel.log_info(self.t("ocr_started"))

        self.ocr_worker = OcrWorker(
            self.file_path, options, tesseract_path,
            self.cancel_event, batch_files=files,
        )
        self.ocr_worker.progress.connect(self._on_ocr_progress)
        self.ocr_worker.batch_progress.connect(self._on_batch_progress)
        self.ocr_worker.finished.connect(self._on_ocr_finished)
        self.ocr_worker.error.connect(self._on_ocr_error)
        self.ocr_worker.start()

    def _on_ocr_progress(self, value, current_page, total_pages):
        self.actions_panel.set_progress(
            value,
            self.t("ocr_page_progress").format(current=current_page, total=total_pages),
        )

    def _on_batch_progress(self, current, total, name):
        self.actions_panel.set_progress(
            current / max(total, 1),
            self.t("batch_progress").format(current=min(current + 1, total), total=total, name=name),
        )

    def _on_ocr_finished(self, text, elapsed, cancelled):
        self.ocr_running = False
        self.actions_panel.set_ocr_buttons(False)
        self.actions_panel.hide_progress()

        if cancelled:
            if text.strip():
                self.result_panel.set_text(text)
                self.actions_panel.set_status(self.t("ocr_cancelled_partial"), "warning")
                self.log_panel.log_warning(f"{self.t('ocr_cancelled')} ({elapsed:.1f}s)")
                self.actions_panel.set_save_enabled(True)
            else:
                self.actions_panel.set_status(self.t("ocr_cancelled"), "warning")
                self.log_panel.log_warning(self.t("ocr_cancelled"))
        else:
            self.result_panel.set_text(text)
            self.actions_panel.set_status(self.t("ocr_complete").format(elapsed=elapsed), "success")
            self.log_panel.log_success(self.t("ocr_complete").format(elapsed=elapsed))
            self.actions_panel.set_save_enabled(bool(text.strip()))

    def _on_ocr_error(self, message):
        self.ocr_running = False
        self.actions_panel.set_ocr_buttons(False)
        self.actions_panel.hide_progress()
        self.actions_panel.set_status(self.t("ocr_failed"), "error")
        self.log_panel.log_error(f"OCR failed: {message}")

    def _stop_ocr(self):
        if self.ocr_running:
            self.cancel_event.set()
            self.log_panel.log_info(self.t("stopping_ocr"))

    # --- Clipboard ---
    def _copy_output(self):
        text = self.result_panel.get_text().strip()
        if not text:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.log_panel.log_success(self.t("copied"))

    def _clear_output(self):
        self.result_panel.clear()
        self.log_panel.log_info(self.t("result_cleared"))

    # --- Save ---
    def _save_output(self):
        text = self.result_panel.get_text().strip()
        if not text:
            return

        # Show format selection dialog
        exts = " ".join(f"*.{e}" for e in ["txt", "docx", "pdf"])
        path, selected_filter = QFileDialog.getSaveFileName(
            self, self.t("save"), "output.txt",
            f"Text Files (*.txt);;Word Documents (*.docx);;PDF Files (*.pdf)",
        )
        if not path:
            return

        # Determine format from path
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if ext not in EXPORT_EXTENSIONS:
            ext = "txt"
            if not path.endswith(".txt"):
                path += ".txt"

        try:
            source_image = None
            if ext == "pdf" and self.file_path and not self.is_pdf:
                if self.file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    source_image = Image.open(self.file_path)
                    if self.settings_panel.preprocess_check.isChecked():
                        source_image = preprocess_image(
                            source_image,
                            binarize=self.settings_panel.binarize_check.isChecked(),
                            upscale=True,
                        )

            resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tesseract_path = resolve_tesseract_path(resource_dir)

            result_kind = save_export(
                path, text, ext,
                source_image=source_image,
                tesseract_path=tesseract_path,
                lang=self.settings_panel.get_ocr_lang_key(),
                tesseract_config=build_tesseract_config(psm=int(self.settings_panel.get_psm_value())),
            )

            if result_kind == "pdf_searchable":
                msg = self.t("saved_searchable_pdf").format(path=path)
            elif result_kind == "pdf_text":
                msg = self.t("saved_text_pdf").format(path=path)
            else:
                msg = f"Saved to: {path}" if self.language == "en" else f"خروجی ذخیره شد: {path}"
            self.log_panel.log_success(msg)
        except Exception as exc:
            self.log_panel.log_error(f"Save failed: {exc}")

    # --- Screenshots ---
    def _screenshot_full(self):
        self.actions_panel.close_screenshot_menu()
        self.actions_panel.set_status(self.t("screenshot_processing"), "info")
        self.log_panel.log_info(self.t("screenshot_processing"))

        # Minimize, wait, then screenshot
        self.showMinimized()

        import pyautogui
        def worker():
            import time
            time.sleep(0.4)  # Wait for minimize animation
            try:
                img = pyautogui.screenshot()
                # Restore on main thread
                QTimer.singleShot(0, self._restore_and_process_screenshot)
                self._pending_screenshot = img
            except Exception as exc:
                QTimer.singleShot(0, lambda: self._screenshot_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _screenshot_region(self):
        self.actions_panel.close_screenshot_menu()
        self.actions_panel.set_status(self.t("screenshot_processing"), "info")
        self.log_panel.log_info(self.t("screenshot_processing"))

        # Minimize, wait, then screenshot
        self.showMinimized()

        import pyautogui
        def worker():
            import time
            time.sleep(0.4)  # Wait for minimize animation
            try:
                img = pyautogui.screenshot()
                self._pending_screenshot = img
                QTimer.singleShot(0, self._restore_and_show_region)
            except Exception as exc:
                QTimer.singleShot(0, lambda: self._screenshot_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _restore_and_process_screenshot(self):
        """Restore window and process the captured screenshot."""
        self.showNormal()
        self.activateWindow()
        self.raise_()
        if hasattr(self, '_pending_screenshot') and self._pending_screenshot:
            self._process_screenshot(self._pending_screenshot)
            self._pending_screenshot = None

    def _restore_and_show_region(self):
        """Restore window and show region selector."""
        self.showNormal()
        self.activateWindow()
        self.raise_()
        if hasattr(self, '_pending_screenshot') and self._pending_screenshot:
            self._show_region_selector(self._pending_screenshot)
            self._pending_screenshot = None

    def _screenshot_error(self, message):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.actions_panel.set_status(self.t("screenshot_cancelled"), "error")
        self.log_panel.log_error(f"Screenshot failed: {message}")

    def _show_region_selector(self, pil_image):
        from PyQt6.QtGui import QImage, QPixmap
        from io import BytesIO

        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        data = buffer.getvalue()
        qimg = QImage()
        qimg.loadFromData(data)
        pixmap = QPixmap.fromImage(qimg)

        self.selector = RegionSelector(pixmap)
        self.selector.region_selected.connect(lambda pm: self._on_region_selected(pm, pil_image))
        self.selector.region_cancelled.connect(self._on_screenshot_cancelled)

    def _on_region_selected(self, cropped_pixmap, original_pil):
        if cropped_pixmap:
            self._process_screenshot_pixmap(cropped_pixmap)
        else:
            self._on_screenshot_cancelled()

    def _process_screenshot_pixmap(self, pixmap):
        from PyQt6.QtGui import QImage
        from PyQt6.QtCore import QBuffer, QByteArray
        from PIL import Image

        qimg = pixmap.toImage()
        buf = QByteArray()
        qbuffer = QBuffer(buf)
        qbuffer.open(QBuffer.OpenModeFlag.WriteOnly)
        qimg.save(qbuffer, "PNG")
        qbuffer.close()

        pil_image = Image.open(__import__('io').BytesIO(buf.data()))
        self._process_screenshot(pil_image)

    def _process_screenshot(self, pil_image):
        tmp_path = os.path.join(tempfile.gettempdir(), "persian_ocr_screenshot.png")
        pil_image.save(tmp_path)
        self.batch_files = []
        self._load_file(tmp_path)
        self.log_panel.log_success(self.t("screenshot_taken"))

    def _on_screenshot_cancelled(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.actions_panel.set_status(self.t("screenshot_cancelled"), "warning")
        self.log_panel.log_warning(self.t("screenshot_cancelled"))

    # --- Language ---
    def _toggle_language(self):
        self.language = "en" if self.language == "fa" else "fa"
        self._apply_language()
        self._persist_settings()

    def _apply_language(self):
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if self.language == "fa"
            else Qt.LayoutDirection.LeftToRight
        )
        self.setWindowTitle(self.t("title"))
        self.lang_btn.setText(self.t("lang_switch"))
        self.github_btn.setText(self.t("author_link"))

        # Update all panels
        self.actions_panel.update_texts(self.t)
        self.settings_panel.update_texts(self.t)
        self.result_panel.update_texts(self.t)

        # Update group box titles by storing keys
        for widget in self.findChildren(QGroupBox):
            key = widget.property("i18n_key")
            if key:
                widget.setTitle(self.t(key))

    def _open_github(self):
        import webbrowser
        webbrowser.open(APP_GITHUB)

    def closeEvent(self, event):
        if self.ocr_running:
            self.cancel_event.set()
        event.accept()
