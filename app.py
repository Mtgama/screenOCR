import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.theme import Theme
from ui.main_window import MainWindow


def get_resource_dir():
    if getattr(sys, "frozen", False):
        for base in (getattr(sys, "_MEIPASS", ""), os.path.dirname(sys.executable)):
            if base and os.path.isdir(os.path.join(base, "Tesseract")):
                return base
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    # High DPI support
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Persian OCR")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Hamed Gharghi")

    # Apply theme
    Theme.apply_to_app(app)

    # Create main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
