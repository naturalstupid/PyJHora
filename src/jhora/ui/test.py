import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import Qt

# Define your constants
_CENTER_X = 100
_CENTER_Y = 100
_INNER_CIRCLE_RADIUS = 50
_OUTER_CIRCLE_RADIUS = 100
_SUNRISE_LABEL_DEGREES = 45
_sunset_degrees = 90

class AnnularShadingWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the outer circle
        painter.setBrush(QColor(211, 211, 211))  # very light grey
        painter.drawEllipse(_CENTER_X - _OUTER_CIRCLE_RADIUS, _CENTER_Y - _OUTER_CIRCLE_RADIUS, 
                            2 * _OUTER_CIRCLE_RADIUS, 2 * _OUTER_CIRCLE_RADIUS)

        # Draw the annular region
        painter.setBrush(QColor(255, 255, 224))  # light yellow
        start_angle = _SUNRISE_LABEL_DEGREES * 16
        sweep_length = -_sunset_degrees * 16
        painter.drawPie(_CENTER_X - _OUTER_CIRCLE_RADIUS, _CENTER_Y - _OUTER_CIRCLE_RADIUS,
                        2 * _OUTER_CIRCLE_RADIUS, 2 * _OUTER_CIRCLE_RADIUS, start_angle, sweep_length)

        # Draw the inner circle
        painter.setBrush(self.palette().window().color())  # fill with the widget's background color
        painter.drawEllipse(_CENTER_X - _INNER_CIRCLE_RADIUS, _CENTER_Y - _INNER_CIRCLE_RADIUS, 
                            2 * _INNER_CIRCLE_RADIUS, 2 * _INNER_CIRCLE_RADIUS)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = AnnularShadingWidget()
    widget.resize(300, 300)
    widget.show()
    sys.exit(app.exec())
