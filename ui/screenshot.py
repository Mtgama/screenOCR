from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPixmap, QPen, QFont, QCursor


class RegionSelector(QWidget):
    region_selected = pyqtSignal(object)  # QPixmap
    region_cancelled = pyqtSignal()

    def __init__(self, background_pixmap=None):
        super().__init__()
        self.background_pixmap = background_pixmap
        self.start_point = None
        self.current_rect = None
        self.is_selecting = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.setMouseTracking(True)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.showFullScreen()
        self.activateWindow()
        self.setFocus()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Draw screenshot background
        if self.background_pixmap:
            scaled = self.background_pixmap.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
            painter.drawPixmap(0, 0, scaled)

        # Semi-transparent overlay on everything
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 130))

        # Draw selection area
        if self.current_rect and self.current_rect.width() > 0 and self.current_rect.height() > 0:
            rect = self.current_rect.normalized()

            # Show original content inside selection (remove overlay from selected area)
            if self.background_pixmap:
                painter.setClipRect(rect)
                painter.setClipping(True)
                scaled = self.background_pixmap.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                painter.drawPixmap(0, 0, scaled)
                painter.setClipping(False)

            # Draw selection border
            pen = QPen(QColor(139, 92, 246), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            # Draw corner handles
            handle = 8
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(139, 92, 246))
            corners = [rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()]
            for corner in corners:
                painter.drawRect(QRect(corner.x() - handle//2, corner.y() - handle//2, handle, handle))

            # Draw dimension text
            dim_text = f"{int(rect.width())} x {int(rect.height())}"
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            text_rect = QRect(int(rect.center().x() - 40), int(rect.top() - 28), 80, 24)
            # Background for text
            painter.setBrush(QColor(0, 0, 0, 180))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(text_rect.adjusted(-4, -2, 4, 2), 4, 4)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, dim_text)

        # Draw instructions at bottom
        painter.setPen(QColor(255, 255, 255, 220))
        painter.setFont(QFont("Segoe UI", 11))
        instr_rect = QRect(0, h - 50, w, 40)
        painter.drawText(instr_rect, Qt.AlignmentFlag.AlignCenter, "Click and drag to select region  |  Press ESC to cancel")

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.current_rect = QRect(self.start_point, self.start_point)
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.start_point:
            self.current_rect = QRect(self.start_point, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            if self.current_rect and self.current_rect.width() > 10 and self.current_rect.height() > 10:
                rect = self.current_rect.normalized()
                # Crop the original pixmap to the selected region
                if self.background_pixmap:
                    # Map screen coordinates to original pixmap coordinates
                    sw = self.background_pixmap.width() / self.width()
                    sh = self.background_pixmap.height() / self.height()
                    orig_rect = QRect(
                        int(rect.x() * sw), int(rect.y() * sh),
                        int(rect.width() * sw), int(rect.height() * sh)
                    )
                    cropped = self.background_pixmap.copy(orig_rect)
                else:
                    cropped = None
                self.close()
                self.region_selected.emit(cropped)
            else:
                self.current_rect = None
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.region_cancelled.emit()

    def mouseDoubleClickEvent(self, event):
        self.close()
        self.region_cancelled.emit()
