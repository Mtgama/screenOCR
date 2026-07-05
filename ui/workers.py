import os
import time
import threading
from io import BytesIO

from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PIL import Image
import pyautogui

from core.image_processor import preprocess_image, suggest_psm
from core.pdf_handler import pdf_to_images
from core.ocr_engine import (
    build_tesseract_config,
    ocr_single_file,
    get_psm_reason_label,
)
from core.export_manager import save_export


class OcrWorker(QThread):
    progress = pyqtSignal(float, int, int)  # value, current_page, total_pages
    batch_progress = pyqtSignal(int, int, str)  # current, total, name
    finished = pyqtSignal(str, float, bool)  # text, elapsed, cancelled
    error = pyqtSignal(str)

    def __init__(self, file_path, options, tesseract_path, cancel_event, batch_files=None):
        super().__init__()
        self.file_path = file_path
        self.options = options
        self.tesseract_path = tesseract_path
        self.cancel_event = cancel_event
        self.batch_files = batch_files or []

    def run(self):
        try:
            start = time.time()
            options = self.options.copy()
            options["tesseract_path"] = self.tesseract_path

            if self.batch_files:
                all_text = []
                total = len(self.batch_files)
                for idx, file_path in enumerate(self.batch_files):
                    if self.cancel_event.is_set():
                        break
                    name = os.path.basename(file_path)
                    self.batch_progress.emit(idx, total, name)
                    file_text = ocr_single_file(file_path, options, self.cancel_event)
                    all_text.append(f"\n=== {name} ===\n{file_text}")
                    self.batch_progress.emit(idx + 1, total, name)
                result = "\n".join(all_text)
                elapsed = time.time() - start
                self.finished.emit(result, elapsed, self.cancel_event.is_set())
                return

            # Single file
            if self.cancel_event.is_set():
                self.finished.emit("", time.time() - start, True)
                return

            result = ocr_single_file(
                self.file_path, options, self.cancel_event,
                progress_callback=lambda v, c, t: self.progress.emit(v, c, t),
            )
            elapsed = time.time() - start
            self.finished.emit(result, elapsed, False)
        except Exception as exc:
            self.error.emit(str(exc))


class ScreenshotWorker(QThread):
    finished = pyqtSignal(object)  # PIL Image
    error = pyqtSignal(str)

    def __init__(self, mode="full"):
        super().__init__()
        self.mode = mode

    def run(self):
        try:
            img = pyautogui.screenshot()
            if self.mode == "region":
                # For region, we need to pass the full screenshot to the selector
                self.finished.emit(("region", img))
            else:
                self.finished.emit(("full", img))
        except Exception as exc:
            self.error.emit(str(exc))


def image_to_pixmap(pil_image, max_size=(520, 300)):
    """Convert PIL Image to QPixmap."""
    from PyQt6.QtGui import QImage, QPixmap

    img = pil_image.copy()
    img.thumbnail(max_size)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    data = buffer.getvalue()

    qimg = QImage()
    qimg.loadFromData(data)
    return QPixmap.fromImage(qimg)
