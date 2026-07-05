from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt


class Theme:
    # Colors - Modern purple-dark theme
    BG = "#0f1117"
    BG_SECONDARY = "#141722"
    CARD = "#1a1d2e"
    CARD_BORDER = "#2a2d3e"
    PRIMARY = "#8B5CF6"
    PRIMARY_HOVER = "#7C3AED"
    PRIMARY_SOFT = "#2d1f5e"
    SECONDARY = "#6366F1"
    ACCENT = "#A78BFA"
    DANGER = "#EF4444"
    DANGER_HOVER = "#DC2626"
    SUCCESS = "#34D399"
    INFO = "#818CF8"
    WARNING = "#FBBF24"
    TEXT = "#E8EDF4"
    TEXT_SECONDARY = "#94A3B8"
    MUTED = "#64748B"
    INPUT_BG = "#111425"
    INPUT_BORDER = "#2a2d3e"
    LOG_BG = "#111420"
    LOG_ROW = "#161929"
    HEADER_BG = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a1d2e, stop:1 #1e1433)"
    SHADOW = "rgba(0, 0, 0, 0.3)"

    @staticmethod
    def get_stylesheet():
        return f"""
        /* Global */
        QWidget {{
            background-color: {Theme.BG};
            color: {Theme.TEXT};
            font-family: 'Segoe UI', 'Vazirmatn', 'Tahoma', sans-serif;
            font-size: 13px;
        }}

        /* Main Window */
        QMainWindow {{
            background-color: {Theme.BG};
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background: {Theme.BG_SECONDARY};
            width: 8px;
            margin: 0;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {Theme.CARD_BORDER};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {Theme.MUTED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {Theme.BG_SECONDARY};
            height: 8px;
            margin: 0;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {Theme.CARD_BORDER};
            border-radius: 4px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {Theme.MUTED};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        /* Cards (QGroupBox) */
        QGroupBox {{
            background-color: {Theme.CARD};
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 12px;
            margin-top: 20px;
            padding: 16px 12px 12px 12px;
            font-weight: 600;
            font-size: 14px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 16px;
            top: 4px;
            padding: 0 8px;
            color: {Theme.ACCENT};
            background-color: {Theme.CARD};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {Theme.CARD};
            color: {Theme.TEXT};
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 500;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: {Theme.PRIMARY_SOFT};
            border-color: {Theme.PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {Theme.PRIMARY};
        }}
        QPushButton:disabled {{
            background-color: {Theme.BG_SECONDARY};
            color: {Theme.MUTED};
            border-color: {Theme.INPUT_BORDER};
        }}

        /* Primary Button */
        QPushButton[cssClass="primary"] {{
            background-color: {Theme.PRIMARY};
            color: white;
            border: none;
            font-weight: 600;
        }}
        QPushButton[cssClass="primary"]:hover {{
            background-color: {Theme.PRIMARY_HOVER};
        }}
        QPushButton[cssClass="primary"]:disabled {{
            background-color: {Theme.PRIMARY_SOFT};
            color: {Theme.MUTED};
        }}

        /* Danger Button */
        QPushButton[cssClass="danger"] {{
            background-color: {Theme.DANGER};
            color: white;
            border: none;
            font-weight: 600;
        }}
        QPushButton[cssClass="danger"]:hover {{
            background-color: {Theme.DANGER_HOVER};
        }}
        QPushButton[cssClass="danger"]:disabled {{
            background-color: #3d1515;
            color: {Theme.MUTED};
        }}

        /* Text Input */
        QTextEdit, QPlainTextEdit {{
            background-color: {Theme.INPUT_BG};
            color: {Theme.TEXT};
            border: 1px solid {Theme.INPUT_BORDER};
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            selection-background-color: {Theme.PRIMARY_SOFT};
        }}
        QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {Theme.PRIMARY};
        }}

        QLineEdit {{
            background-color: {Theme.INPUT_BG};
            color: {Theme.TEXT};
            border: 1px solid {Theme.INPUT_BORDER};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border-color: {Theme.PRIMARY};
        }}

        /* ComboBox (Dropdown) */
        QComboBox {{
            background-color: {Theme.INPUT_BG};
            color: {Theme.TEXT};
            border: 1px solid {Theme.INPUT_BORDER};
            border-radius: 6px;
            padding: 6px 10px;
            min-width: 140px;
        }}
        QComboBox:hover {{
            border-color: {Theme.PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {Theme.MUTED};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Theme.CARD};
            color: {Theme.TEXT};
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 6px;
            padding: 4px;
            selection-background-color: {Theme.PRIMARY_SOFT};
        }}

        /* CheckBox */
        QCheckBox {{
            spacing: 8px;
            color: {Theme.TEXT};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {Theme.CARD_BORDER};
            background-color: {Theme.INPUT_BG};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Theme.PRIMARY};
            border-color: {Theme.PRIMARY};
        }}
        QCheckBox::indicator:hover {{
            border-color: {Theme.PRIMARY};
        }}

        /* ProgressBar */
        QProgressBar {{
            background-color: {Theme.INPUT_BG};
            border: none;
            border-radius: 4px;
            height: 6px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {Theme.PRIMARY};
            border-radius: 4px;
        }}

        /* Label */
        QLabel {{
            color: {Theme.TEXT};
            background: transparent;
        }}
        QLabel[cssClass="muted"] {{
            color: {Theme.MUTED};
            font-size: 12px;
        }}
        QLabel[cssClass="accent"] {{
            color: {Theme.ACCENT};
            font-size: 12px;
        }}
        QLabel[cssClass="header-title"] {{
            font-size: 22px;
            font-weight: bold;
            color: {Theme.TEXT};
        }}
        QLabel[cssClass="header-version"] {{
            font-size: 12px;
            color: {Theme.MUTED};
        }}
        QLabel[cssClass="status"] {{
            font-size: 13px;
            font-weight: 500;
            padding: 4px 8px;
        }}
        QLabel[cssClass="stats"] {{
            color: {Theme.MUTED};
            font-size: 12px;
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {Theme.CARD_BORDER};
            width: 2px;
            margin: 4px 0;
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 8px;
            background-color: {Theme.CARD};
        }}
        QTabBar::tab {{
            background-color: {Theme.BG_SECONDARY};
            color: {Theme.MUTED};
            border: 1px solid {Theme.CARD_BORDER};
            border-bottom: none;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        QTabBar::tab:selected {{
            background-color: {Theme.CARD};
            color: {Theme.ACCENT};
        }}

        /* ToolTip */
        QToolTip {{
            background-color: {Theme.CARD};
            color: {Theme.TEXT};
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 6px;
            padding: 6px;
        }}

        /* Menu */
        QMenu {{
            background-color: {Theme.CARD};
            color: {Theme.TEXT};
            border: 1px solid {Theme.CARD_BORDER};
            border-radius: 8px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 20px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {Theme.PRIMARY_SOFT};
        }}

        /* Separator */
        QFrame[frameShape="4"] {{
            background-color: {Theme.CARD_BORDER};
            max-height: 1px;
        }}
        """

    @staticmethod
    def apply_to_app(app):
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(Theme.BG))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(Theme.TEXT))
        palette.setColor(QPalette.ColorRole.Base, QColor(Theme.INPUT_BG))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Theme.CARD))
        palette.setColor(QPalette.ColorRole.Text, QColor(Theme.TEXT))
        palette.setColor(QPalette.ColorRole.Button, QColor(Theme.CARD))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(Theme.TEXT))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(Theme.PRIMARY))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        app.setPalette(palette)
        app.setStyleSheet(Theme.get_stylesheet())

        font = QFont("Segoe UI", 10)
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        app.setFont(font)
