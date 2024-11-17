from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt6.QtGui import QPainter, QColor,QFont, QPen
from PyQt6.QtCore import Qt, QRectF, QPoint, QPointF, QSize
import sys, math
from jhora import utils,const

class ChandraKalanala(QWidget):
    def __init__(self,base_star=18,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 8; self.y_dim = 9; self.x_gap = 65; self.y_gap=60
        self.setGeometry(10, 10, 500, 500)
        self.setWindowTitle(utils.resource_strings['chandra_kalanala_str']+' '+utils.resource_strings['chakra_str'])
        self.lines = [((4,8),(4,7)),((4,7),(6,7)),((6,7),(6,8)),((5,8),(5,2)),((4,2),(4,3)),((4,3),(6,3)),((6,3),(6,2)),
                      ((2,4),(3,4)),((3,4),(3,6)),((3,6),(2,6)),((2,5),(8,5)),((8,4),(7,4)),((7,4),(7,6)),((7,6),(8,6))]
        self.rasi_labels = {
            1: (5,1), 2: (4,1), 3: (4,3), 6: (3,4), 7: (2,4),
            8: (2,5), 9: (2,6), 10: (3, 6), 13: (4,7), 14: (4,8),
            15: (5,8), 16: (6,8), 17: (6,7), 20: (7,6),
            21: (8,6), 22: (8,5), 23: (8,4), 24: (7,4),
            27: (6,3), 28: (6,2), 4:(4,4),5:(4,5),11:(4,6),12:(5,6),18:(6,6),19:(6,5),25:(6,4),26:(5,4),
        }
        self._label_font_size = label_font_size
        self._base_star = base_star
        self._update_with_star_labels()
        self._rasi_color = 'Red'; self._planet_color = 'Brown'; self._text_color='Green';
        self._star_color = 'Blue'
        self._planet_positions = planet_positions
        self._planets_in_retrograde=planets_in_retrograde
    def _update_with_star_labels(self):
        _star_list = utils.NAKSHATRA_SHORT_LIST
        _abhijit_list = [_star_list[i] for i in const.abhijit_order_of_stars]
        _star_labels = {}
        for k,(x,y) in self.rasi_labels.items():
            nak = ((self._base_star-1)+(k-1))%28
            #self.rasi_labels[k] = (x,y,_abhijit_list[nak])
            _star_labels[nak+1] = (x,y,_abhijit_list[nak])
        self.rasi_labels = _star_labels.copy()
    def _update_with_planet_labels(self):
        for p,(h,long) in self._planet_positions:
            p_long = h*30+long
            from jhora.panchanga import drik
            nak = drik.nakshatra_pada(p_long)
            p_star = nak[0]
            if p_star >= 21: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[p_star]
            self.rasi_labels[p_star] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],base_star=None,label_font_size=None):
        if base_star != None: self._base_star = base_star
        if label_font_size != None: self._label_font_size = label_font_size
        self._planet_positions = planet_positions
        self._planets_in_retrograde = planets_in_retrograde
        self._update_with_planet_labels()
        self.createUI()
    def createUI(self):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
        x_gap = self.x_gap; y_gap = self.y_gap
        # Draw lines
        for line in self.lines:
            start, end = line
            painter.drawLine(start[0] * x_gap, (start[1]) * y_gap, end[0] * x_gap, (end[1]) * y_gap)

        # Draw text
        font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold); painter.setFont(font)
        for _, (x, y,star_planets) in self.rasi_labels.items():
            color = self._planet_color if '\n' in star_planets else self._star_color
            painter.setPen(QColor(color))
            painter.drawText(QRectF(int(x * x_gap), int((y) * y_gap),300,300), str(star_planets))
            painter.setPen(QPen())
    def paintEvent(self, event):
        self.createUI()
if __name__ == "__main__":
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    planet_positions = [['L', (9, 22.44575902738461)], [0, (7, 21.565282200247736)], [1, (6, 6.959489445251251)], [2, (4, 25.539747317445176)], [3, (8, 9.936449034377262)], [4, (8, 25.82805158497206)], [5, (6, 23.71713310535756)], [6, (11, 6.807276353388318)], [7, (5, 10.553787374448945)], [8, (11, 10.553787374448916)]]
    chart = ChandraKalanala()
    chart.setData(planet_positions, planets_in_retrograde=[3,4])
    chart.show()
    sys.exit(App.exec())
    