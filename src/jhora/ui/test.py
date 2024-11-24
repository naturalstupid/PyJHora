from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtWidgets import QWidget, QApplication
import sys

class AlignmentTextWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 400, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont("Arial", 16)
        painter.setFont(font)

        # Align text to the left
        rect_left = self.rect().adjusted(10, 10, -300, -350)
        painter.drawText(rect_left, Qt.AlignmentFlag.AlignLeft, "Aligned to left")

        # Align text to the right
        rect_right = self.rect().adjusted(300, 10, -10, -350)
        painter.drawText(rect_right, Qt.AlignmentFlag.AlignRight, "Aligned to right")

        # Align text to the center
        rect_center = self.rect().adjusted(0, 50, 0, -300)
        painter.drawText(rect_center, Qt.AlignmentFlag.AlignCenter, "Centered text")

        # Align text to the top
        rect_top = self.rect().adjusted(0, 0, 0, -350)
        painter.drawText(rect_top, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, "Aligned to top")

        # Align text to the bottom
        rect_bottom = self.rect().adjusted(0, 300, 0, -50)
        painter.drawText(rect_bottom, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, "Aligned to bottom")

app = QApplication(sys.argv)
window = AlignmentTextWidget()
window.show()
sys.exit(app.exec())
