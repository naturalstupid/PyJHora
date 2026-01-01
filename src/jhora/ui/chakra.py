from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt6.QtGui import QPainter, QColor,QFont, QPen
from PyQt6.QtCore import Qt, QRectF, QPoint, QPointF, QSize
import sys, math
from jhora import utils,const

star_list = ["Asw","Bha","Kri","Roh","Mrig","Ardr","Puna","Push","Asre","Magh","PPha","UPha","Hast","Chit","Swat",
             "Visa","Anu","Jye","Mool","PSha","USha","Srav","Dhan","Sat","PBha","UBha","Rev","Abhi"]
get_2d_list_index = utils.get_2d_list_index
color_label = lambda label,color: '<span style=color:'+color+';>'+label+'</span>'
def drawRotatedText(painter, degrees, x, y, text):
    painter.save()
    painter.translate(x, y)
    painter.rotate(degrees)
    painter.drawText(0, 0, text)
    painter.restore()
class SapthaNaadi(QWidget):
    def __init__(self, planet_positions=[],planets_in_retrograde=[]):
        QWidget.__init__(self)
        self._xdim = 5; self._ydim = 7
        self._grid_label_values = [
            ['prachanda_str','pawan_str', 'dahan_str', 'soumya_str', 'neera_str', 'jala_str', 'amrit_str'],
            [3,4,5,6,7,8,9],[16,15,14,13,12,11,10],[17,18,19,20,21,22,23],[2,1,28,27,26,25,24,23]
        ]
        self._star_indices = {self._grid_label_values[i][j]:(i,j) for i in range(self._xdim) for j in range(self._ydim) if isinstance(self._grid_label_values[i][j],int)}
        self._rasi_color = 'Red'; self._planet_color = 'Brown'; self._text_color='Green';
        self._star_color = 'Blue'
        self._planet_positions = planet_positions
        self._planets_in_retrograde=planets_in_retrograde
        self.createUI()
    def createUI(self):
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        self._grid_labels = [[QLabel('') for j in range(self._ydim)] for i in range(self._xdim)]
        for i in range(self._xdim):
            for j in range(self._ydim):
                #self._grid_labels[i][j].setText(self._grid_label_values[i][j])
                self._grid_labels[i][j].setStyleSheet("border: 1px solid black;")  # Optional: Add a border to each cell
                self.gridLayout.addWidget(self._grid_labels[i][j], i, j)
        self.layout.addLayout(self.gridLayout)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self._update_labels_with_stars_and_rasis()
        if len(self._planet_positions) > 0:
            self._update_with_planet_labels()
    def _update_with_planet_labels(self):
        for p,(h,long) in self._planet_positions:
            p_long = h*30+long
            from jhora.panchanga import drik
            nak = drik.nakshatra_pada(p_long)
            p_star = nak[0]
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            r,c = self._star_indices[p_star]
            cell_value = self._grid_labels[r][c].text()+'<br>'+color_label(pstr+rstr,self._planet_color)
            self._grid_labels[r][c].setText(cell_value)
        self.update()
    def setData(self,planet_positions=[],planets_in_retrograde=[],label_font_size=8):
        if len(planet_positions) > 0:
            self._planet_positions = planet_positions
            self._update_with_planet_labels()
    def _update_labels_with_stars_and_rasis(self):
        for i in range(self._xdim):
            for j in range(self._ydim):
                cell_value = self._grid_label_values[i][j]
                star_cell = isinstance(cell_value,int)
                if star_cell:
                    cell_value = color_label(utils.NAKSHATRA_SHORT_LIST[cell_value-1],self._star_color)
                    self._grid_labels[i][j].setText(cell_value)
                    self._grid_labels[i][j].setAlignment(Qt.AlignmentFlag.AlignTop)
                else:
                    cell_value = color_label(utils.resource_strings[cell_value],self._text_color)
                    self._grid_labels[i][j].setText(cell_value)
                    self._grid_labels[i][j].setAlignment(Qt.AlignmentFlag.AlignCenter)
class PanchaShalaka(QWidget):
    def __init__(self,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 7; self.y_dim = 7; self.x_gap = 60; self.y_gap=60
        self.setGeometry(10, 10, 600, 600)
        self.setWindowTitle(utils.resource_strings['saptha_shalaka_str']+' '+utils.resource_strings['chakra_str'])
        self.lines = [((2,1),(2,7)),((3,1),(3,7)),((4,1),(4,7)),((5,1),(5,7)),((6,1),(6,7)),
                      ((1,2),(7,2)),((1,3),(7,3)),((1,4),(7,4)),((1,5),(7,5)),((1,6),(7,6)),
                      ((1,6.5),(6.5,1)),((1.5,7),(7,1.5)),((1.5,1),(7,6.5)),((1,1.5),(6.5,7))
                      ]
        self.rasi_labels = {
            1: (1,2), 2: (1, 1.5), 3: (1.5, 1), 4: (2,1), 5: (3,1),6:(4,1),7:(5,1), 8: (6,1), 9: (6.5,1),
            10: (7,1.5), 11: (7,2), 12: (7,3), 13:(7,4),14:(7,5), 15: (7, 6), 16: (7, 6.5), 17: (6.5,7), 18: (6,7),
            19: (5,7), 20:(4,7), 21:(3,7), 22: (2,7), 23: (1.5, 7),
            24: (1, 6.5), 25: (1, 6), 26: (1,5), 27: (1, 4), 28: (1, 3)
        }
        self._label_font_size = label_font_size
        self._base_star = 1
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
            if p_star > const._ABHIJITH_STAR_INDEX: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[p_star]
            self.rasi_labels[p_star] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],label_font_size=None):
        if label_font_size  is not None: self._label_font_size = label_font_size
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
            painter.drawLine(int(start[0] * x_gap), int((start[1]) * y_gap), int(end[0] * x_gap), int((end[1]) * y_gap))

        # Draw text
        font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold); painter.setFont(font)
        for _, (x, y,star_planets) in self.rasi_labels.items():
            color = self._planet_color if '\n' in star_planets else self._star_color
            painter.setPen(QColor(color))
            painter.drawText(QRectF(int(x * x_gap), int((y) * y_gap),300,300), str(star_planets))
            painter.setPen(QPen())
    def paintEvent(self, event):
        self.createUI()
class SapthaShalaka(QWidget):
    def __init__(self,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 9; self.y_dim = 9; self.x_gap = 50; self.y_gap=50
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle(utils.resource_strings['saptha_shalaka_str']+' '+utils.resource_strings['chakra_str'])
        self.lines = [((2,1),(2,9)),((3,1),(3,9)),((4,1),(4,9)),
                      ((5,1),(5,9)),((6,1),(6,9)),((7,1),(7,9)),
                      ((8,1),(8,9)),((1,2),(9,2)),((1,3),(9,3)),((1,4),(9,4)),
                      ((1,5),(9,5)),((1,6),(9,6)),((1,7),(9,7)),((1,8),(9,8))
                      ]
        self.rasi_labels = {
            1: (7, 1), 2: (8, 1), 3: (9, 2), 4: (9, 3), 5: (9, 4), 6: (9, 5), 7: (9, 6),
            8: (9, 7), 9: (9, 8), 10: (8, 9), 11: (7, 9), 12: (6, 9), 13: (5, 9), 14: (4, 9),
            15: (3, 9), 16: (2, 9), 17: (1, 8), 18: (1, 7), 19: (1, 6), 20: (1, 5),
            21: (1, 4), 22: (1, 3), 23: (1,2), 24: (2, 1), 25: (3, 1), 26: (4, 1),
            27: (5, 1), 28: (6, 1)
        }
        self._label_font_size = label_font_size
        self._base_star = 1
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
            if p_star > const._ABHIJITH_STAR_INDEX: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[p_star]
            self.rasi_labels[p_star] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],label_font_size=None):
        if label_font_size  is not None: self._label_font_size = label_font_size
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
RahuKalanala = SapthaShalaka
class ChandraKalanala(QWidget):
    def __init__(self,base_star=18,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 8; self.y_dim = 9; self.x_gap = 60; self.y_gap=55
        self.setGeometry(0, 0, 500, 500)
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
            if p_star > const._ABHIJITH_STAR_INDEX: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[p_star]
            self.rasi_labels[p_star] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],base_star=None,label_font_size=None):
        if base_star  is not None: self._base_star = base_star
        if label_font_size  is not None: self._label_font_size = label_font_size
        self._planet_positions = planet_positions
        self._planets_in_retrograde = planets_in_retrograde
        self._update_with_planet_labels()
        self.createUI()
    def createUI(self):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
        x_gap = self.x_gap; y_gap = self.y_gap
        # draw cicrle
        p1 = (1,1); p2 = (2,1)
        rad = 1.5*x_gap
        center = QPointF(5*x_gap,5*y_gap)
        painter.drawEllipse(center, rad, rad)
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
class Tripataki(QWidget):
    def __init__(self,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 5; self.y_dim = 5; self.x_gap = 80; self.y_gap=80
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle(utils.resource_strings['tripataki_str']+' '+utils.resource_strings['chakra_str'])
        self.lines = {(2,5):[(1,4),(2,1),(5,2)],(3,5):[(1,3),(3,1),(5,3)],(4,5):[(1,2),(4,1),(5,4)],
                      (2,1):[(1,2),(5,4)],(3,1):[(1,3),(5,3)],(4,1):[(1,4),(5,2)],
                      (1,2):[(5,2)],(1,3):[(5,3)],(1,4):[(5,4)]
                       }
        self.rasi_labels = [(1,3),(1,4),(2,5),(3,5),(4,5),(5,4),(5,3),(5,2),(4,1),(3,1),(2,1),(1,2)]
        self._label_font_size = label_font_size
        self._rasi_color = 'Red'; self._planet_color = 'Brown'; self._text_color='Green';
        self._star_color = 'Blue'
        self._planet_positions = planet_positions
        self._planets_in_retrograde=planets_in_retrograde
    def _update_with_planet_labels(self):
        self.rasi_labels = [(x,y,utils.RAASI_SHORT_LIST[h]) for h,(x,y) in enumerate(self.rasi_labels)]
        for p,(h,_) in self._planet_positions:
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[h]
            self.rasi_labels[h] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],base_star=None,label_font_size=None):
        if base_star  is not None: self._base_star = base_star
        if label_font_size  is not None: self._label_font_size = label_font_size
        self._planet_positions = planet_positions
        self._planets_in_retrograde = planets_in_retrograde
        self._update_with_planet_labels()
        self.createUI()
    def createUI(self):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
        x_gap = self.x_gap; y_gap = self.y_gap
        # Draw lines
        for start,ends in self.lines.items():
            for end in ends:
                painter.drawLine(start[0] * x_gap, (start[1]) * y_gap, end[0] * x_gap, (end[1]) * y_gap)

        # Draw text
        font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold); painter.setFont(font)
        for x, y,rasi_planets in self.rasi_labels:
            color = self._planet_color if '\n' in rasi_planets else self._rasi_color
            painter.setPen(QColor(color))
            painter.drawText(QRectF(int(x * x_gap), int((y) * y_gap),300,300), str(rasi_planets))
            painter.setPen(QPen())
    def paintEvent(self, event):
        self.createUI()
class SuryaKalanala(QWidget):
    def __init__(self,base_star=18,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 15; self.y_dim = 15; self.x_gap = 30; self.y_gap=30
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle(utils.resource_strings['surya_kalanala_str']+' '+utils.resource_strings['chakra_str'])
        self.lines = [((1,6),(15,6)),((1,8),(15,8)),((1,10),(15,10)),
                      ((5,1),(5,15)),((8,1),(8,15)),((11,1),(11,15)),
                      ((4,6),(2,3)),((5,6),(2,2)),((5,5),(3,2)),((5,4),(4,2)),
                      ((12,6),(14,3)),((11,6),(14,2)),((11,5),(13,2)),((11,4),(12,2)),
                      ((5,12),(3,14)),((3,10),(2,12)),((11,12),(13,14)),((13,10),(14,12)),
                      ((5,4),(6,2)),((8,4),(7,2)),((8,4),(9,2)),((11,4),(12,2)),((11,4),(10,2))
                      ]
        self.rasi_labels = {
            1: (8, 15), 2: (5, 15), 3: (3, 15), 4: (1, 14), 5: (1, 10), 6: (1, 8), 7: (1, 6),
            8: (1, 4), 9: (1, 1), 10: (3, 1), 11: (4, 1), 12: (5, 1), 13: (6, 1), 14: (7, 1),
            15: (8, 1), 16: (9, 1), 17: (10, 1), 18: (11, 1), 19: (12, 1), 20: (13, 1),
            21: (15, 1), 22: (15, 4), 23: (15,6), 24: (15, 8), 25: (15, 10), 26: (15, 14),
            27: (13, 15), 28: (11, 15)
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
            if p_star > const._ABHIJITH_STAR_INDEX: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[p_star]
            self.rasi_labels[p_star] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],base_star=None,label_font_size=None):
        if base_star  is not None: self._base_star = base_star
        if label_font_size  is not None: self._label_font_size = label_font_size
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
class Shoola(QWidget):
    def __init__(self,base_star=18,planet_positions=[],planets_in_retrograde=[],label_font_size=6):
        super().__init__()
        self.x_dim = 11; self.y_dim = 11; self.x_gap = 30; self.y_gap=40
        self.setGeometry(100, 100, 400, 600)
        self.setWindowTitle(utils.resource_strings['shoola_str']+' '+utils.resource_strings['chakra_str'])
        self.lines = [
            ((5, 1), (5, 10)),
            ((2, 7), (8, 7)),
            ((2, 7), (2, 10)),
            ((8, 7), (8, 10))
        ]
        self.rasi_labels = {
            1: (5, 1), 2: (4, 2), 3: (4, 3), 4: (4, 4), 5: (4, 5), 6: (4, 6), 7: (4, 7),
            8: (3, 10), 9: (2, 11), 10: (1, 10), 11: (1, 9), 12: (1, 8), 13: (2, 7),
            14: (4, 10), 15: (5, 11), 16: (6, 10), 17: (6, 9), 18: (6, 8.5), 19: (6, 8),
            20: (7, 10), 21: (8, 11), 22: (9, 10), 23: (9, 9), 24: (9, 8), 25: (8, 7),
            26: (6, 4), 27: (6, 3), 28: (6, 2)
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
            if p_star > const._ABHIJITH_STAR_INDEX: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            x,y,pl = self.rasi_labels[p_star]
            self.rasi_labels[p_star] = [x,y,pl+'\n'+pstr+rstr]        
    def setData(self,planet_positions,planets_in_retrograde=[],base_star=None,label_font_size=None):
        if base_star  is not None: self._base_star = base_star
        if label_font_size  is not None: self._label_font_size = label_font_size
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
            painter.drawLine(start[0] * x_gap, (self.y_dim+1 - start[1]) * y_gap, end[0] * x_gap, (self.y_dim+1 - end[1]) * y_gap)

        # Draw text
        font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold); painter.setFont(font)
        for _, (x, y,star_planets) in self.rasi_labels.items():
            color = self._planet_color if '\n' in star_planets else self._star_color
            painter.setPen(QColor(color))
            painter.drawText(QRectF(int(x * x_gap), int((self.y_dim+1 - y) * y_gap),300,300), str(star_planets))
            painter.setPen(QPen())
    def paintEvent(self, event):
        self.createUI()
class Sarvatobadra(QWidget):
    def __init__(self, planet_positions=[],planets_in_retrograde=[]):
        QWidget.__init__(self)
        self._grid_label_values = [
            ['ii',  23, 24, 25, 26, 27, 1, 2, 'a'],
            [22, 'rii', 'g', 's', 'd', 'ch', 'l', 'u', 3],
            [28, 'kh', 'ai', 11, 12, 1, 'lu', 'a', 4],
            [21, 'j', 10, 'ah', 'Rikita<br>Fri', 'o', 2, 'v', 5],
            [20, 'bh', 9, 'Jaya<br>Thu', 'Pooma<br>Sat', 'Nanda<br>Sun<br>Tue', 3, 'k', 6],
            [19, 'y', 8, 'am', 'Bhadra<br>Mon<br>Wed', 'au', 4, 'h', 7],
            [18, 'n', 'e', 7, 6, 5, 'luu', 'd', 8],
            [17, 'ri', 't', 'r', 'p', 't~', 'm', 'uu', 9],
            ['i', 16, 15, 14, 13, 12, 11, 10, 'aa']
        ]
        self._star_indices = {self._grid_label_values[i][j]:(i,j) for i in range(9) for j in range(9) if ((i==8) or (j==8) or (i==0) or (j==0)) and isinstance(self._grid_label_values[i][j],int)}
        self._rasi_color = 'Red'; self._planet_color = 'Brown'; self._text_color='Green';
        self._star_color = 'Blue'
        self._planet_positions = planet_positions
        self._planets_in_retrograde=planets_in_retrograde
        self.createUI()
    def createUI(self):
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        self._grid_labels = [[QLabel('') for j in range(9)] for i in range(9)]
        for i in range(9):
            for j in range(9):
                #self._grid_labels[i][j].setText(self._grid_label_values[i][j])
                self._grid_labels[i][j].setStyleSheet("border: 1px solid black;")  # Optional: Add a border to each cell
                self.gridLayout.addWidget(self._grid_labels[i][j], i, j)
        self.layout.addLayout(self.gridLayout)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self._update_labels_with_stars_and_rasis()
        if len(self._planet_positions) > 0:
            self._update_with_planet_labels()
    def _update_with_planet_labels(self):
        for p,(h,long) in self._planet_positions:
            p_long = h*30+long
            from jhora.panchanga import drik
            nak = drik.nakshatra_pada(p_long)
            p_star = nak[0]
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            r,c = self._star_indices[p_star]
            cell_value = self._grid_labels[r][c].text()+'<br>'+color_label(pstr+rstr,self._planet_color)
            self._grid_labels[r][c].setText(cell_value)
        self.update()
    def setData(self,planet_positions=[],planets_in_retrograde=[],label_font_size=8):
        if len(planet_positions) > 0:
            self._planet_positions = planet_positions
            self._update_with_planet_labels()
    def _update_labels_with_stars_and_rasis(self):
        for i in range(9):
            for j in range(9):
                cell_value = self._grid_label_values[i][j]
                border_cell = ((i==8) or (j==8)) or (i==0) or (j==0)
                if border_cell and isinstance(cell_value,int):
                    cell_value = color_label(utils.NAKSHATRA_SHORT_LIST[cell_value-1],self._star_color)
                    self._grid_labels[i][j].setText(cell_value)
                    self._grid_labels[i][j].setAlignment(Qt.AlignmentFlag.AlignTop)
                elif not border_cell and isinstance(cell_value,int):
                    cell_value = color_label(utils.RAASI_SHORT_LIST[cell_value-1],self._rasi_color)
                    self._grid_labels[i][j].setText(cell_value)
                    self._grid_labels[i][j].setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    cell_value = color_label(cell_value,self._text_color)
                    self._grid_labels[i][j].setText(cell_value)
                    self._grid_labels[i][j].setAlignment(Qt.AlignmentFlag.AlignCenter)
class KaalaChakra(QWidget):
    def __init__(self, planet_positions=[],planets_in_retrograde=[],base_star=None,
                 title_font_size=8,label_font_size=8):
        """
            If birth chart Rasi - sun_star = star of Sun's longitude
            For all other chars - use star of Lagna longitude
        """
        QWidget.__init__(self)
        self._rasi_color = 'Red'; self._planet_color = 'Brown'; self._text_color='Green';
        self._star_color = 'Blue'
        self._planet_positions=[]
        self._label_font_size = label_font_size
        if len(planet_positions)>0:
            self.createUI()
    def get_kaala_chakra_star_labels(self):
        _star_list = utils.NAKSHATRA_SHORT_LIST
        _abhijit_list = [_star_list[i] for i in const.abhijit_order_of_stars]
        self.stars_inner = [((self._base_star-1)+(ele-1))%28 for ele in self.stars_inner]
        self.labels_inner = [_abhijit_list[i] for i in self.stars_inner]
        self.stars_outer_divisions = [[((self._base_star-1)+(ele-1))%28  for ele in row] for row in self.stars_outer_divisions]
        self.labels_outer_divisions = [[_abhijit_list[i]  for i in row] for row in self.stars_outer_divisions]
    def createUI(self):
        qp = QPainter(self)
        qp.begin(self)
        try:
            self.drawCircle(qp)
        except Exception as e:
            print(f"Error in drawCircle: {e}")
        qp.end()
    def setData(self,planet_positions=[],planets_in_retrograde=[],base_star=18,
                 title_font_size=8,label_font_size=8):
        self._label_font_size = label_font_size
        self._base_star = base_star
        self._planet_positions = planet_positions
        self._planets_in_retrograde = planets_in_retrograde
        self.labels_custom = [utils.resource_strings[r] for r in ['kaala_chakra_southeast_str','kaala_chakra_east_str','kaala_chakra_northeast_str',
                                'kaala_chakra_north_str','kaala_chakra_northwest_str','kaala_chakra_west_str',
                                'kaala_chakra_southwest_str','kaala_chakra_south_str']]
        self.stars_inner = [4, 25, 18, 11]
        self.stars_outer_divisions = [[5, 6, 7],[3, 2, 1],[26, 27, 28],[24, 23, 22],[19, 20, 21],
                                      [17, 16, 15],[12, 13, 14],[10, 9, 8]]
        self.get_kaala_chakra_star_labels()
        self.add_planet_labels()
        self.inner_angles = [45, 135, 225, 315]
        self.outer_angles = [45, 90, 135, 180, 225, 270, 315, 360]
        self.createUI()
    def add_planet_labels(self):
        for p,(h,long) in self._planet_positions:
            p_long = h*30+long
            from jhora.panchanga import drik
            nak = drik.nakshatra_pada(p_long)
            p_star = nak[0]
            if p_star > const._ABHIJITH_STAR_INDEX: p_star += 1
            rstr = const._retrogade_symbol if p in self._planets_in_retrograde else ''
            pstr = utils.resource_strings['ascendant_short_str'] if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
            if p_star-1 in self.stars_inner:
                self.labels_inner[self.stars_inner.index(p_star-1)] += '\n'+pstr+rstr
            else:
                r,c = get_2d_list_index(self.stars_outer_divisions,p_star-1)
                self.labels_outer_divisions[r][c] += '\n'+pstr+rstr
    def paintEvent(self, event):
        if len(self._planet_positions) > 0:
            self.createUI()
    def drawCircle(self, qp):
        try:
            # Set up pen and font
            pen = QPen(Qt.GlobalColor.black, 2)
            qp.setPen(pen)
            font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold)
            qp.setFont(font)

            # Draw circle
            center = QPointF(self.width() / 2, self.height() / 2)
            radius = min(self.width(), self.height()) / 8
            qp.drawEllipse(center, radius, radius)

            # Draw labels inside the circle
            angles_inner = self.inner_angles
            for angle, label in zip(angles_inner, self.labels_inner):
                rad = math.radians(angle)
                x = int(center.x() + radius * 0.5 * math.cos(rad))
                y = int(center.y() - radius * 0.5 * math.sin(rad))
                color = self._planet_color if '\n' in label else self._star_color
                qp.setPen(QColor(color))
                qp.drawText(QRectF(x,y, 300, 300),Qt.AlignmentFlag.AlignLeft, label)
                qp.setPen(QPen())
            # Draw lines and labels outside the circle
            angles_outer = self.outer_angles
            for i, angle in enumerate(angles_outer):
                rad = math.radians(angle)
                x_start = int(center.x() + radius * math.cos(rad))
                y_start = int(center.y() - radius * math.sin(rad))
                x_outer = int(center.x() + (radius + 200) * math.cos(rad))
                y_outer = int(center.y() - (radius + 200) * math.sin(rad))
                qp.drawLine(QPointF(x_start, y_start), QPointF(x_outer, y_outer))

                # Draw labels at each division of the lines
                for j in range(1, 4):
                    x_div = int(center.x() + (radius + 200 / 4 * j) * math.cos(rad))
                    y_div = int(center.y() - (radius + 200 / 4 * j) * math.sin(rad))
                    color = self._planet_color if '\n' in self.labels_outer_divisions[i][j-1] else self._star_color
                    qp.setPen(QColor(color))
                    qp.drawText(QRectF(x_div,y_div, 300, 300),Qt.AlignmentFlag.AlignLeft, self.labels_outer_divisions[i][j-1])
                    qp.setPen(QPen())
                # Draw the final custom label at the end of each line
                x_label = int(center.x() + (radius + 220) * math.cos(rad))
                y_label = int(center.y() - (radius + 220) * math.sin(rad))
                if angle == 180 or angle==360:
                    y_label -= 20
                elif angle == 90:
                    x_label += 40; y_label += 60
                elif angle == 270:
                    x_label += 40; y_label -= 60
                qp.setPen(QColor(self._text_color))
                qp.drawText(QRectF(x_label,y_label, 300, 300),Qt.AlignmentFlag.AlignLeft, self.labels_custom[i])
                qp.setPen(QPen())
        except Exception as e:
            print(f"Error in drawCircle: {e}")

    def closeEvent(self, event):
        event.accept()
            
class KotaChakra(QWidget):
    def __init__(self, planet_positions=[], birth_star=15,birth_star_padha=1,planets_in_retrograde=[],
                 title_font_size=12,label_font_size=12,
                 square_color_rgbs=[(255, 128, 128),(128, 255, 128), (128, 128, 255), (255, 255, 128)],
                 square_captions=[]):
        QWidget.__init__(self)
        self._star_list = utils.NAKSHATRA_SHORT_LIST
        self._planet_positions = planet_positions
        self._planets_in_retrograde = planets_in_retrograde
        self._birth_star = birth_star
        self._birth_star_padha = birth_star_padha
        self.labels = self.get_planet_star_labels(planet_positions, birth_star,planets_in_retrograde)
        self._title_font_size = title_font_size
        self._label_font_size = label_font_size
        self._square_color_rgbs = square_color_rgbs
        if len(square_captions)==0:
            self._square_captions = [utils.resource_strings[r] for r in ['baahya_str','praakaara_str','durgantara_str','sthamba_str']]
        else:
            self._square_captions = square_captions
        self._space_between_squares = 65
        self.setGeometry(0,0,550,550)
        self.setWindowTitle(utils.resource_strings['kota_str']+' '+utils.resource_strings['chakra_str'])
        if len(self._planet_positions)>0:
            moon_house = self._planet_positions[2][1][0]
            from jhora.horoscope.chart import house
            self._kota_lord = utils.PLANET_NAMES[house.house_owner_from_planet_positions(planet_positions, moon_house)]
            self._kota_paala = utils.PLANET_NAMES[const.kota_paala_lord_for_star_paadha[birth_star-1][birth_star_padha-1]]
            #print('kota lord',self._kota_lord,'kota paala',self._kota_paala)
    def createUI(self):
        self._star_list = utils.NAKSHATRA_SHORT_LIST
        painter = QPainter(self)
        rect = self.rect().adjusted(0, 0, -1, -1)
        colors = [QColor(x[0],x[1],x[2]) for x in self._square_color_rgbs ]
        # Draw 4 concentric squares
        num_squares = 4
        for i in range(num_squares):
            inset = i * self._space_between_squares  # Space between squares
            square_rect = rect.adjusted(inset, inset, -inset, -inset)
            painter.fillRect(square_rect, colors[i])
            self.drawLabels(painter, square_rect, i, num_squares)
            self.drawCaptions(painter, square_rect, i, num_squares)
    def setData(self,planet_positions=[], birth_star=15,birth_star_padha=1,planets_in_retrograde=[],
                 title_font_size=12,label_font_size=8,
                 square_color_rgbs=[(255, 128, 128),(128, 255, 128), (128, 128, 255), (255, 255, 128)],
                 square_captions=[]):
        self._planet_positions = planet_positions
        self._planets_in_retrograde = planets_in_retrograde
        self._birth_star = birth_star
        self.labels = self.get_planet_star_labels(planet_positions, birth_star,planets_in_retrograde)
        self._title_font_size = title_font_size
        self._label_font_size = label_font_size
        self._square_color_rgbs = square_color_rgbs
        if len(square_captions)==0:
            self._square_captions = [utils.resource_strings[r] for r in ['baahya_str','praakaara_str','durgantara_str','sthamba_str']]
        else:
            self._square_captions = square_captions
        moon_house = self._planet_positions[2][1][0]
        from jhora.horoscope.chart import house
        self._kota_lord = utils.PLANET_NAMES[house.house_owner_from_planet_positions(planet_positions, moon_house)]
        self._kota_paala = utils.PLANET_NAMES[const.kota_paala_lord_for_star_paadha[birth_star-1][birth_star_padha-1]]
        #print('kota lord',self._kota_lord,'kota paala',self._kota_paala)
        self.createUI()
    def paintEvent(self, event):
        self.createUI()
    def drawLabels(self, painter, rect, index, num_squares):
        painter.setPen(Qt.GlobalColor.black)
        # Retrieve labels from the list
        square_labels = self.labels[index]
        xadj = int(0.02*rect.width()); yadj = int(0.03*rect.height())
        if index == num_squares - 1:  # Innermost square
            label_positions = [
                (QPoint(rect.center().x()+xadj, rect.top()+yadj), square_labels[0]), #Inner Top Middle
                (QPoint(rect.right()-xadj, rect.center().y()), square_labels[1]), # Inner Right
                (QPoint(rect.center().x()+xadj, rect.bottom()-3*yadj), square_labels[2]), # Inner Bottom
                (QPoint(rect.left()+3*xadj, rect.center().y()), square_labels[3]) # Inner Left
            ]
        else:
            label_positions = [
                (rect.topLeft()+QPoint(4*xadj,yadj), square_labels[0]), # Top Left
                (QPoint(rect.center().x()+xadj, rect.top()+yadj), square_labels[1]), # Top Middle
                (rect.topRight()+QPoint(-xadj,yadj), square_labels[2]), # Top Right
                (QPoint(rect.right()-xadj, rect.center().y()), square_labels[3]), # Center Right
                (rect.bottomRight()+QPoint(-xadj,-3*yadj), square_labels[4]), # Bottom Right
                (QPoint(rect.center().x()+xadj, rect.bottom()-3*yadj), square_labels[5]), # Bottom Middle
                (rect.bottomLeft()+QPoint(4*xadj,-3*yadj), square_labels[6]), # Bottom Left
                (QPoint(rect.left()+4*xadj, rect.center().y()), square_labels[7]) # Center Left
            ]
        font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        for pos, text in label_positions:
            painter.drawText(QRectF(pos.x() - 30, pos.y() - 10, 60, 200), Qt.AlignmentFlag.AlignLeft, text)
        self.update()
    def drawCaptions(self, painter, rect, index, num_squares):
        painter.setPen(Qt.GlobalColor.black)
        _caption = self._square_captions[index]
        xadj = 10; yadj = 15
        if index == num_squares - 1:  # Innermost square
            pos = (QPoint(rect.bottomRight().x()-xadj, rect.bottomRight().y()-int(yadj/2)))
        else:
            pos = (QPoint(rect.bottomRight().x()-10*xadj, rect.bottom()-int(yadj/2)))
        font = QFont(); font.setPointSize(self._label_font_size); font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(pos.x() - 30, pos.y() - 10, 300, 300), Qt.AlignmentFlag.AlignLeft, _caption)
    def get_kota_chakra_star_list(self,birth_star=15):
        star_list_1 = [self._star_list[i] for i in const.abhijit_order_of_stars]
        return [[star_list_1[((birth_star-1)+(ele-1))%28]  for ele in row] for row in const.kota_chakra_star_placement_from_birth_star]
         
    def get_labels_from_birth_star(self,birth_star=15):
        star_list_1 = [self._star_list[i] for i in const.abhijit_order_of_stars]
        #star_list_1 = [i for i in const.abhijit_order_of_stars]
        labels = []
        for row in const.kota_chakra_star_placement_from_birth_star:
            lbl = []
            for ele in row:
                star = star_list_1[((birth_star-1)+(ele-1))%28]
                lbl.append(str(star))
            labels.append(lbl)
        return labels
    def get_planet_star_labels(self,planet_positions,birth_star=15,planets_in_retrograde=[]):
        from jhora.panchanga import drik
        kcs_list = self.get_kota_chakra_star_list(birth_star)
        labels = self.get_labels_from_birth_star(birth_star)
        for planet, (sign,long) in planet_positions:
            rStr = const._retrogade_symbol if planet in planets_in_retrograde else ''
            p_long = sign*30+long
            nak,_,_ = drik.nakshatra_pada(p_long)
            p_i,p_j = get_2d_list_index(kcs_list,self._star_list[nak-1])
            if  planet==const._ascendant_symbol:
                labels[p_i][p_j] += '\n'+utils.resource_strings['ascendant_short_str']
            else:
                labels[p_i][p_j] += '\n' + utils.PLANET_SHORT_NAMES[planet]+rStr
        return labels
    def resizeEvent(self, event):
        side = min(self.width(), self.height())
        self.setFixedSize(side, side)

if __name__ == "__main__":
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    planet_positions = [['L', (9, 22.44575902738461)], [0, (7, 21.565282200247736)], [1, (6, 6.959489445251251)], 
                        [2, (4, 25.539747317445176)], [3, (8, 9.936449034377262)], [4, (8, 25.82805158497206)], 
                        [5, (6, 23.71713310535756)], [6, (11, 6.807276353388318)], [7, (5, 10.553787374448945)], 
                        [8, (11, 10.553787374448916)],[9,(9,8.2)],[10,(9,2.2)],[11,(7,9.7)]]
    chart = SapthaNaadi()
    chart.setData(planet_positions, planets_in_retrograde=[3,4])
    #chart = PanchaShalaka()#RahuKalanala()
    #chart.setData(planet_positions=planet_positions,planets_in_retrograde=[3,4])
    #chart = SapthaShalaka()#RahuKalanala()
    #chart.setData(planet_positions=planet_positions,planets_in_retrograde=[3,4])
    #chart = ChandraKalanala(base_star=18)
    #chart.setData(planet_positions=planet_positions,planets_in_retrograde=[3,4])
    #chart = Tripataki()
    #chart.setData(planet_positions=planet_positions,planets_in_retrograde=[3,4])
    #chart = SuryaKalanala(base_star=18)
    #chart.setData(planet_positions=planet_positions,planets_in_retrograde=[3,4])
    #chart = Shoola(base_star=18)
    #chart.setData(planet_positions=planet_positions,planets_in_retrograde=[3,4])
    #chart = KotaChakra()
    #chart.setData(planet_positions=planet_positions,birth_star=15,planets_in_retrograde=[3,5],label_font_size=6)
    #chart = KaalaChakra()
    #chart.setData(planet_positions=planet_positions,base_star=18,planets_in_retrograde=[3,5],label_font_size=6)
    #chart = Sarvatobadra()
    #chart.setData(planet_positions, planets_in_retrograde=[3,4])
    chart.show()
    sys.exit(App.exec())
