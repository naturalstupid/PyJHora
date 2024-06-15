import os
import math
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont, QPainter
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt6.QtCore import Qt

from hora import const
from hora.panchanga import drik #V2.3.0

_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
_lagnam_line_factor = 0.3
_lagnam_line_thickness = 3
_image_path = os.path.abspath(const._IMAGES_PATH)
_zodiac_icons = ['mesham.jpg','rishabham.jpg','mithunam.jpg','katakam.jpg','simmam.jpg','kanni.jpg','thulam.jpg','vrichigam.jpg','dhanusu.jpg','makaram.jpg','kumbam.jpg','meenam.jpg']
class SudarsanaChakraChart(QWidget):
    """
        Sudarsana Chakra Chart 
    """
    def __init__(self,data=None,chart_center_pos:tuple=(175,175),chart_radii:tuple=(75,125,175),
                 chart_inner_square:tuple=(30,30),label_font_size:int=8,chart_label_radius_factor:float=0.15,
                 chart_size_factor:float=1.0,chart_title_font_size=9):
        QWidget.__init__(self)
        self.sc_chart_radius_1 = int(chart_radii[0]*chart_size_factor)
        self.sc_chart_radius_2 = int(chart_radii[1]*chart_size_factor)
        self.sc_chart_radius_3 = int(chart_radii[2]*chart_size_factor)
        self.sc_inner_square_width = int(chart_inner_square[0]*chart_size_factor)
        self.sc_inner_square_height = int(chart_inner_square[1]*chart_size_factor)
        self.sc_chart_center_x = int(chart_center_pos[0]*chart_size_factor)
        self.sc_chart_center_y = int(chart_center_pos[1]*chart_size_factor)
        self.sc_label_font_size = label_font_size
        self._sc_label_radius_factor = chart_label_radius_factor
        self.chart_title_font_size = chart_title_font_size
        if data is None:
            data = [['L','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu','Mandhi',''],
                    ['L','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu','Mandhi',''],
                    ['L','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu','Mandhi','']]
        self.data = data
        #self.setGeometry(0,0,500,500)
    def paintEvent(self, event):
        self.event = event
        self._draw_sudarsana_chakra_chart()#event)
    def setData(self,data,chart_title=None,chart_title_font_size=None):
        self.data = data
        self._chart_title = chart_title
        self.chart_title_font_size = chart_title_font_size
    def _draw_sc_basic_chart(self,painter):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        center = QtCore.QPoint(cx,cy)
        painter.drawEllipse(center,self.sc_chart_radius_1,self.sc_chart_radius_1)
        painter.drawEllipse(center,self.sc_chart_radius_2,self.sc_chart_radius_2)
        painter.drawEllipse(center,self.sc_chart_radius_3,self.sc_chart_radius_3)
        sw = self.sc_inner_square_width
        sh = self.sc_inner_square_height
        r = self.sc_chart_radius_3
        a = int(math.sqrt(r*r-0.25*sh*sh))
        b = int(math.sqrt(r*r-0.25*sw*sw))
        l12 = QtCore.QLine(cx+int(0.5*sw),cy-b,cx+int(0.5*sw),cy+b)
        painter.drawLine(l12)
        l34 = QtCore.QLine(cx-int(0.5*sw),cy-b,cx-int(0.5*sw),cy+b)
        painter.drawLine(l34)
        l56 = QtCore.QLine(cx-a,cy-int(0.5*sh),cx+a,cy-int(0.5*sh))
        painter.drawLine(l56)
        l78 = QtCore.QLine(cx-a,cy+int(0.5*sh),cx+a,cy+int(0.5*sh))
        painter.drawLine(l78)
        r2= int(r/math.sqrt(2))
        l12 = QtCore.QLine(cx-int(0.5*sw),cy-int(0.5*sh),cx-r2,cy-r2)
        painter.drawLine(l12)
        l34 = QtCore.QLine(cx+int(0.5*sw),cy-int(0.5*sh),cx+r2,cy-r2)
        painter.drawLine(l34)
        l56 = QtCore.QLine(cx+int(0.5*sw),cy+int(0.5*sh),cx+r2,cy+r2)
        painter.drawLine(l56)
        l78 = QtCore.QLine(cx-int(0.5*sw),cy+int(0.5*sh),cx-r2,cy+r2)
        painter.drawLine(l78)
        ix = cx - int(0.5*sw)
        iy = cy - int(0.5*sh)
        icon = QPixmap(_image_path+'//aum_small.jpg')
        image_rect = QtCore.QRect(ix,iy,sw,sh)
        painter.drawPixmap(image_rect, icon)
        pi_value = 180.0
        t = math.asin(0.5*sh/self.sc_chart_radius_3)*pi_value/math.pi
        t_list=[-t,t,0.25*pi_value,0.5*pi_value-t,0.5*pi_value+t,0.75*pi_value,pi_value-t,pi_value+t,1.25*pi_value,1.5*pi_value-t,1.5*pi_value+t,1.75*pi_value,2*pi_value-t,2*pi_value+t]
        font = QFont()
        font.setPixelSize(12)
        painter.setFont(font)
        painter.translate(cx,cy)
        for z in range(12):
            angle = 0.5*(t_list[z]+t_list[(z+1)])
            rad = self.sc_chart_radius_3#+10
            self.drawNode(painter,angle,rad,str(z+1))
        painter.setFont(QFont())
    def _draw_sudarsana_chakra_chart(self):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        sw = self.sc_inner_square_width
        sh = self.sc_inner_square_height
        painter = QPainter(self)
        self._draw_sc_basic_chart(painter)
        #painter.translate(cx,cy)
        r_sq = math.sqrt(sw*sw+sh*sh)
        pi_value = 180.0#/math.pi ##
        r_list = [r_sq,self.sc_chart_radius_1,self.sc_chart_radius_2,self.sc_chart_radius_3]
        title_x = cx
        r3 = r_list[-1]
        title_y = cy + r3
        title_height = 20
        title_width = 2*r3
        title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
        self._chart_title.replace('\n',' ')
        if self.chart_title_font_size != None:
            font = QFont()
            font.setPixelSize(self.chart_title_font_size)
            painter.setFont(font)                    
        painter.drawText(title_rect,Qt.AlignmentFlag.AlignCenter,self._chart_title.strip())
        for i,r in enumerate(r_list[:-1]):
            data_1d = self.data[i]
            r1 = r_list[i]
            r2 = r_list[(i+1)]
            pr = r1 + self._sc_label_radius_factor*(r2-r1)#r2-self._sc_label_radius_factor*(r2-r1)
            t = math.asin(0.5*sh/r2)*pi_value/math.pi
            t_list=[-t,t,0.25*pi_value,0.5*pi_value-t,0.5*pi_value+t,0.75*pi_value,pi_value-t,pi_value+t,1.25*pi_value,1.5*pi_value-t,1.5*pi_value+t,1.75*pi_value,2*pi_value-t,2*pi_value+t]
            for i_z in range(12):
                t1 = t_list[i_z]
                t2 = t_list[(i_z+1)]
                self._write_planets_inside_houses(painter,pr,t1,t2,data_1d[i_z],i_z)
    def drawNode(self,painter, angle, radius, text):
        #print('angle, radius, text',angle, radius, text)
        size = 32767.0
        painter.save()
        painter.rotate(-angle)
        painter.translate(radius, 0)
        painter.drawText(QtCore.QRectF(0, -size/2.0, size, size), Qt.AlignmentFlag.AlignVCenter, text.strip())
        painter.restore()
    def _write_planets_inside_houses(self,painter,pr,t1,t2,data,i_z):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        z,pls = data
        planets = pls.split('/')
        p_len = len(planets)
        if planets[0] == '':
            p_len = 0
        pc = p_len+1
        tinc = (t2-t1)/(pc+1)
        th = 40
        tw = 40
        # First write zodiac symbol
        pt = t2-tinc
        tx = int(cx+pr*math.cos(pt))
        ty = int(cy - pr*math.sin(pt))
        trect = QtCore.QRect(tx,ty,tw,th)
        #print(int(tx),int(ty),int(tw),int(th),pr,pt*180.0/math.pi,const.rasi_names_en[z])
        font = QFont()
        font.setPixelSize(self.sc_label_font_size)
        painter.setFont(font)
        self.drawNode(painter,pt,pr,const._zodiac_symbols[z])
        if p_len == 0:
            return
        for p in planets:
            pt -= tinc
            tx = int(cx+pr*math.cos(pt))
            ty = int(cy - pr*math.sin(pt))
            trect = QtCore.QRect(tx,ty,tw,th)
            self.drawNode(painter,pt,pr,p)
        painter.setFont(QFont())
    def _write_planets_inside_houses_1(self,painter,radius,data,i_z):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        z,pls = data
        data_text = const._zodiac_symbols[z]+'\n'+pls
        ri = 0.7
        font = QFont()
        font.setPixelSize(self.sc_label_font_size)
        painter.setFont(font)
        a = ((i_z*30.0)+0)*math.pi/180.0             
        rect = QtCore.QRect(int(cx+radius*ri*math.cos(a)),int(cy-radius*ri*math.sin(a)),40,40)
        painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,data_text.strip())
        painter.setFont(QFont()) # reset font
               
        
class WesternChart(QWidget):
    """
        Western Chart
        @param data=one-dimensional array of longitudes of planets in houses
        Example: [Sun_Long/Moon_long, '',Mars_long,'', ...'Lagnam_long',...,'']
        @param chart_center_pos = (x,y) tuple coordinates of chart center
        @param chart_radii: list of radius lengths of four circles of the chart 
        @param label_font_size: font size of labels: default: _west_label_font_size
        @param label_pos_radial_increment: position of labels in radial increment: default: _west_radial_increment
        
    """
    _west_chart_radius_1 = 30
    _west_chart_radius_2 = 110
    _west_chart_radius_3 = 130
    _west_chart_radius_4 = 150
    _west_radial_increment = 15
    _west_chart_center_x = 150
    _west_chart_center_y = 150
    _west_label_font_size = 8
    _west_chart_title_font_size = 9
    def __init__(self,data=None,chart_center_pos:tuple=(_west_chart_center_x,_west_chart_center_y),
                 chart_radii:tuple=(_west_chart_radius_1,_west_chart_radius_2,_west_chart_radius_3,_west_chart_radius_4),
                 label_font_size=_west_label_font_size,label_pos_radial_increment=_west_radial_increment,
                 chart_size_factor:float=1.0,chart_title_font_size=_west_chart_title_font_size):
        QWidget.__init__(self)
        self._chart_center_pos = tuple([int(x*chart_size_factor) for x in chart_center_pos])
        self._chart_radii = tuple([int(x*chart_size_factor) for x in chart_radii])
        self._label_font_size = label_font_size
        self._label_pos_radial_increment = label_pos_radial_increment*chart_size_factor
        self._chart_size_factor = chart_size_factor
        self.chart_title_font_size = chart_title_font_size
        drik._TROPICAL_MODE = True #V2.3.0
        drik.set_tropical_planets() #V2.3.0
        self._chart_title = ''
        self.data = data
        self._asc_longitude = 10.0
        self._asc_house = 0
        if self.data==None:
            self.data = ['லக்னம் ♑︎மகரம் 22° 26’ 37"','சூரியன்☉ ♏︎விருச்சிகம் 21° 33’ 34"','சந்திரன்☾ ♎︎துலாம் 6° 57’ 33"',
                         'செவ்வாய்♂ ♌︎சிம்மம் 25° 32’ 10"','புதன்☿ ♐︎தனுசு 9° 55’ 36"','குரு♃ ♐︎தனுசு 25° 49’ 14"',
                         'சுக்ரன்♀ ♎︎துலாம் 23° 42’ 24"','சனி♄ ♓︎மீனம் 6° 48’ 25"','ராகு☊ ♍︎கன்னி 10° 33’ 13"',
                         'கேது☋ ♓︎மீனம் 10° 33’ 13"']
    def set_label_font_size(self,label_font_size:int):
        """
            Set Label Font Size
            @param label_font_size: int - default: _west_label_font_size
        """
        self._label_font_size = label_font_size
    def set_chart_center_coordinates(self,chart_center_pos:tuple):
        """
            set chart center coordinates (x,y)
            @param chart_center_pos: tuple (x,y) 
        """
        self._chart_center_pos = chart_center_pos
    def set_chart_radii_dimensions(self,chart_radii:tuple):
        """
            set radius of four cicles that form a western chart (r1,r2,r3,r4)
            @param chart_center_pos: tuple (r1,r2,r3,r4) 
        """
        self._chart_radii = chart_radii
    def paintEvent(self, event):
        self.event = event
        self._draw_western_chart()#event)
    def _draw_western_chart(self):
        painter = QPainter(self)
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        center = QtCore.QPoint(cx,cy)
        r1 = self._chart_radii[0]
        r2 = self._chart_radii[1]
        r3 = self._chart_radii[2]
        r23 = r3-0.5*(r3-r2)
        r23b = r3-0.75*(r3-r2)
        r4 = self._chart_radii[3]
        r34 = r4 -0.5*(r4-r3)
        painter.drawEllipse(center,r1,r1)
        painter.drawEllipse(center,r2,r2)
        painter.drawEllipse(center,r3,r3)
        painter.drawEllipse(center,r4,r4)
        asc_long = self._asc_longitude
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        icon_x = int(cx - 0.65 * r1)
        icon_y = int(cy - 0.65 * r1)
        icon_height = int(r1*1.4)
        icon_width = int(r1*1.4)
        icon = QPixmap(_image_path+"//lord_ganesha1.jpg")
        painter.drawPixmap(QtCore.QRect(icon_x,icon_y,icon_width,icon_height),icon)
        for i in range(180,540,30):
            a = i*math.pi/180.0
            ip = QtCore.QPoint(int(cx+r1*math.cos(a)),int(cy+r1*math.sin(a)))
            op = QtCore.QPoint(int(cx+r2*math.cos(a)),int(cy+r2*math.sin(a)))
            painter.drawLine(ip,op)
        for i in range(0,360,5):
            a = i*math.pi/180.0
            ri = r23
            if i%10==0:
                ri = r23b
            ip = QtCore.QPoint(int(cx+ri*math.cos(a)),int(cy+ri*math.sin(a)))
            op = QtCore.QPoint(int(cx+r3*math.cos(a)),int(cy+r3*math.sin(a)))
            painter.drawLine(ip,op)
        for i in range(12):
            a = (i*30+asc_long+150)*math.pi/180.0
            ip = QtCore.QPoint(int(cx+r3*math.cos(a)),int(cy+r3*math.sin(a)))
            op = QtCore.QPoint(int(cx+r4*math.cos(a)),int(cy+r4*math.sin(a)))
            painter.drawLine(ip,op)
        for i in range(len(self.data)):
            self._write_planets_inside_houses(painter,r2,self.data[i],i)
        for i_z in range(12):
            z_i = (self._asc_house+i_z+12)%12
            zodiac_symbol = _zodiac_symbols[z_i]
            house_mid_angle = (i_z*30+self._asc_longitude+155)#*math.pi/180.0
            rect = QtCore.QRect(int(cx+r34*math.cos(house_mid_angle*math.pi/180.0)),int(cy-r34*math.sin(house_mid_angle*math.pi/180.0)),10,10)
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,zodiac_symbol.strip())
        rect = QtCore.QRect(cx-r1,cy-r1,r1*2,2*r1)
        title_x = cx - r3
        title_y = cy + r3
        title_height = 20
        title_width = 2*r3
        title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
        self._chart_title.replace('\n',' ')
        if self.chart_title_font_size != None:
            font = QFont()
            font.setPixelSize(self.chart_title_font_size)
            painter.setFont(font)                    
        painter.drawText(title_rect,Qt.AlignmentFlag.AlignCenter,self._chart_title.strip().split()[0])
        """ reset painter """
        painter.setFont(QFont())                    
    def _write_planets_inside_houses(self,painter,radius,data,i_z):
        tmp_arr = data.strip().split()
        planet = tmp_arr[0][-1].strip()
        zodiac = tmp_arr[1][0].strip()
        deg = int(tmp_arr[2][:-1].strip())
        mins = int(tmp_arr[3][:-1].strip())
        sec = int(tmp_arr[4][:-1].strip())
        zodiac_index = _zodiac_symbols.index(zodiac)
        if i_z==0:
            planet = 'ℒ'
            self._asc_longitude = deg+mins/60.0
            self._asc_house = zodiac_index
        min_new = round(mins+sec/60.0)
        text_new = planet+' '+tmp_arr[2]+' '+zodiac+' '+ str(min_new)+tmp_arr[-3][-1]
        house_index = (zodiac_index - self._asc_house + 12+5) % 12 #+5 to account for 150 degrees for ASC house start
        house_start_angle = house_index*30
        angle = round(house_start_angle+(deg+(mins/60.0+sec/3600.0)))
        a = angle*math.pi/180.0
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        ri = self._label_pos_radial_increment
        font = QFont()
        font.setPixelSize(self._label_font_size)
        painter.setFont(font)                    
        for i,c in enumerate(text_new.split()):
            rect = QtCore.QRect(int(cx+(radius-(i+1)*ri)*math.cos(a)),int(cy-(radius-(i+1)*ri)*math.sin(a)),20,12)
            painter.drawText(rect,Qt.AlignmentFlag.AlignLeft,c.strip())
        painter.setFont(QFont()) # reset font
               
    def setData(self,data,chart_title='',chart_title_font_size=None):#,event=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        tmp_arr = data[0].strip().split()
        deg = int(tmp_arr[2][:-1].strip())
        mins = int(tmp_arr[3][:-1].strip())
        sec = int(tmp_arr[4][:-1].strip())
        self._asc_longitude = deg+mins/60.0+sec/3600.0
        self.update()
class EastIndianChart(QWidget):
    """
        Draws East Indian Natal Chart and labels the planets
        East Indian chart is 3x3 goes anti-clockwise from top-middle
        @param data: 2-D List of planet names in native language
            NOTE: For East Indian Chart - inner cells of 2-D list should have empty labels
            Example: [ ['Saturn/Moon',     'Neptune',       'Mars'/'Sun'],
                       ['Lagnam',          ''   ,     'Ragu'],
                       ['Ketu/Venus',    'Pluto',  'Mercury/Jupiter']
                    ]
        @param chart_house_size: chart size tuple(x,y,width,height)
        @param label_font_size: font size of labels: Default: _east_label_font_size  
    """
    _east_label_font_size = 9
    _east_chart_house_x = 1
    _east_chart_house_y = _east_chart_house_x
    _east_chart_house_width = 120 #100
    _east_chart_house_height = _east_chart_house_width
    _east_chart_title_font_size = 9
    def __init__(self,data=None,chart_house_size:tuple=(_east_chart_house_x,_east_chart_house_y,_east_chart_house_width,_east_chart_house_height),
                 label_font_size:int=_east_label_font_size,chart_size_factor:float=1.0,chart_title_font_size=_east_chart_title_font_size,
                 arudha_lagna_data=None):
        QWidget.__init__(self)
        self._chart_house_size = chart_house_size
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self._chart_title_font_size = chart_title_font_size
        drik._TROPICAL_MODE = False #V2.3.0
        drik.set_sideral_planets() #V2.3.0
        self._zodiac_symbols = [['\n\u264A/\u2649\n','\u2648','\u2653\n/\n\u2652'],
                                ['\u264B','','\u2651'],
                                ['\u264C\n/\n\u264D','\u264E','\n\u264F/\u2650\n'],
                               ]
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        self._grid_labels = []
        self.row_count = 3
        self.col_count = 3
        self._asc_house = 0
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2]*self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3]*self._chart_size_factor)
        self.data = data
        self.arudha_lagna_data=arudha_lagna_data
        self._chart_title = ''
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def paintEvent(self, event):
        self.event = event
        self.set_east_indian_chart_data()#event)
    def setData(self,data,chart_title='',chart_title_font_size=None,arudha_lagna_data=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
    def set_east_indian_chart_data(self):
        """
        Sets the planet labels on to the east indian natal chart
        NOTE: For East Indian Chart - inner cells of 2-D list should have empty labels
                And corner cells should be divided by a separator /
        Example: [ ['Saturn/""',     'Moon',       'Mars'/'Sun'],
                   ['Lagnam',          ''   ,     'Ragu'],
                   ['Ketu/Venus',    'Jupiter',  '""/Jupiter']
                ]
        """
        painter = QPainter(self)
        data = self.data
        chart_title = self._chart_title
        row_count = len(data)
        col_count = len(data[0])
        cell_width = self.house_width
        cell_height = self.house_height
        chart_width = round(self.col_count * cell_width)
        chart_height = round(self.row_count * cell_height)
        _label_counter = 0
        for row in range(row_count):
            for col in range(col_count):
                font = QFont()
                font.setPixelSize(self._label_font_size)
                painter.setFont(font)                    
                left_top_cell = (row==0 and col==0) 
                right_bottom_cell = (row==row_count-1 and col==col_count-1)
                right_top_cell = (row==0 and col==col_count-1) 
                left_bottom_cell = (row==row_count-1 and col==0)
                center_cell = row==1 and col==1
                cell = data[row][col]
                arudha = '/'
                if self.arudha_lagna_data:
                    arudha = self.arudha_lagna_data[row][col]
                zodiac_symbol = self._zodiac_symbols[row][col]
                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)
                rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                painter.drawRect(rect)
                if left_top_cell:
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha,top_cell_arudha = arudha.split("/")
                    # House 3
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_arudha.strip()+'\n'+top_zodiac.strip())
                    # House 2
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_zodiac.strip()+'\n'+bottom_cell_arudha.strip())
                    # Draw cross line
                    diag_start_x = self.x
                    diag_start_y = self.y
                    diag_end_x = self.x + cell_width
                    diag_end_y = self.y + cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                elif right_top_cell:
                    top_cell_text,bottom_cell_text = cell.split("/") # Fixed in 1.1.0
                    top_zodiac,bottom_zodiac = zodiac_symbol.split("/")
                    top_cell_arudha,bottom_cell_arudha = arudha.split("/") # Fixed in 1.1.0
                    # House 11
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,top_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,top_cell_arudha.strip()+'\n'+top_zodiac.strip())
                    # House 12
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,bottom_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,bottom_zodiac.strip()+'\n'+bottom_cell_arudha.strip())
                    # Draw cross line
                    diag_start_x = self.x + chart_width
                    diag_start_y = self.y
                    diag_end_x = self.x + chart_width - cell_width
                    diag_end_y = self.y + cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                elif right_bottom_cell:
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha,top_cell_arudha = arudha.split("/")
                    # House 8
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_zodiac.strip()+'\n'+bottom_cell_arudha.strip())
                    # House 9
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_arudha.strip()+'\n'+top_zodiac.strip())
                    # Draw cross line
                    diag_start_x = self.x + chart_width - cell_width
                    diag_start_y = self.y + chart_height - cell_height
                    diag_end_x = self.x + chart_width
                    diag_end_y = self.y + chart_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                elif left_bottom_cell:
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha,top_cell_arudha = arudha.split("/")
                    # House 5
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_arudha.strip()+'\n'+bottom_zodiac.strip())
                    # House 6
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_text.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_zodiac.strip()+'\n'+top_cell_arudha.strip())
                    # Draw cross line
                    diag_start_x = self.x
                    diag_start_y = self.y + chart_height
                    diag_end_x = self.x + cell_width
                    diag_end_y = self.y + chart_height - cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                # write chart title in center of the chart
                elif center_cell and chart_title:
                    title_x = self.x #round(self.x + chart_width/3)
                    title_y = self.y + chart_height + self.y
                    title_height = 20
                    title_width = chart_width
                    title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
                    chart_title.replace('\n',' ')
                    if self._chart_title_font_size != None:
                        font = QFont()
                        font.setPixelSize(self._chart_title_font_size)
                        painter.setFont(font)                    
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,chart_title.strip())
                    """ reset painter """
                    font = QFont()
                    painter.setFont(font)                    
                    rect_image = QtCore.QRect(round(cell_x+cell_width/2),round(cell_y),round(cell_width/2),round(cell_height/2))
                    icon = QPixmap(_image_path+'//lord_ganesha1.jpg')
                    painter.drawPixmap(rect_image, icon)
                else:
                    painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,cell.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,zodiac_symbol.strip())
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,arudha.strip())
            _label_counter += 1
        painter.end()
class SouthIndianChart(QWidget):
    """
        Draws South Indian Natal Chart and labels the planets
        @param data: 2-D List of planet names in native language
        NOTE: For South Indian Chart - inner cells of 2-D list should have empty labels
        Example: [ ['Saturn','Moon','Sun', 'Mars'],
                   ['Lagnam', ''   , ''  , 'Ragu'],
                   ['Ketu'  , ''   , ''  , 'Mercury'],
                   [''      , 'Jupiter','','']]
        @param chart_house_size: chart size tuple(x,y,width,height)
        @param label_font_size: font size of labels: Default: _east_label_font_size  
    """
    _south_label_font_size = 9
    _south_chart_house_x = 1
    _south_chart_house_y = _south_chart_house_x
    _south_chart_house_width = 350 #300
    _south_chart_house_height = _south_chart_house_width
    def __init__(self,data=None,chart_house_size:tuple=(_south_chart_house_x,_south_chart_house_y,_south_chart_house_width,_south_chart_house_height),
                 label_font_size:int=_south_label_font_size,chart_size_factor:float = 1.0,chart_title_font_size=9, arudha_lagna_data=None):
        QWidget.__init__(self)
        self._chart_house_size = chart_house_size
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self._chart_title_font_size = chart_title_font_size
        drik._TROPICAL_MODE = False #V2.3.0
        drik.set_sideral_planets() #V2.3.0
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        self._zodiac_symbols = [ ['\u2653','\u2648','\u2649', '\u264A'],
                   ['\u2652', ''   , ''  , '\u264B'],
                   ['\u2651'  , ''   , ''  , '\u264C'],
                   ['\u2650'      , '\u264F','\u264E','\u264D']]
        self.row_count = 4
        self.col_count = 4
        self._asc_house = (-1,-1)
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2]*self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3]*self._chart_size_factor)
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        self._chart_title = ''
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def paintEvent(self, event):
        self.event = event
        self.set_south_indian_chart_data()
    def setData(self,data,chart_title='',chart_title_font_size=None,arudha_lagna_data=None):#,event=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        #print('chart style arudha lagna data',self.arudha_lagna_data)
    def set_south_indian_chart_data(self):#, data,chart_title=''):
        """
        Sets the planet labels on to the south indian natal chart
        @param data: 2-D List of planet names in native language
        @chart_title - title of chart (e.g. Raasi, Navamsam) to be displayed in the center of chart
        NOTE: For South Indian Chart - inner cells of 2-D list should have empty labels
        Example: [ ['Saturn','Moon','Sun', 'Mars'],
                   ['Lagnam', ''   , ''  , 'Ragu'],
                   ['Ketu'  , ''   , ''  , 'Mercury'],
                   [''      , 'Jupiter','','']]
        """
        painter = QPainter(self)
        data = self.data
        chart_title = self._chart_title        
        row_count = len(data)
        col_count = len(data[0])
        chart_width = self.house_width
        chart_height = self.house_height
        cell_width =  round(chart_width/self.col_count)
        cell_height = round(chart_height/self.row_count)
        for row in range(row_count):
            for col in range(col_count):
                font = QFont()
                font.setPixelSize(self._label_font_size)
                painter.setFont(font)                    
                cell_text = data[row][col]
                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)
                cell_rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                if row==0 or row==row_count-1 or col==0 or col==col_count-1:
                    if self.arudha_lagna_data:
                        painter.drawText(cell_rect,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom,self.arudha_lagna_data[row][col].strip())
                    painter.drawRect(cell_rect)
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignCenter,cell_text.strip())
                    # Write zodiac symbol
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop,self._zodiac_symbols[row][col].strip())
                    if row == self._asc_house[0] and col == self._asc_house[1]:
                        line_start_x = cell_x
                        line_start_y = round(cell_y + _lagnam_line_factor * cell_height)
                        line_end_x = round(cell_x + _lagnam_line_factor * cell_width)
                        line_end_y = cell_y
                        #painter.setPen(QPen(Qt.GlobalColor.black,_lagnam_line_thickness))
                        painter.drawLine(line_start_x,line_start_y,line_end_x,line_end_y)
                # draw chart title  and icon in center of the chart
                if row == (row_count/2)-1 and col==(col_count/2)-1 and chart_title:
                    cell_x = round(self.x + col * cell_width)
                    cell_y = round(self.y + (row)*cell_height)
                    cell_rect = QtCore.QRect(cell_x,cell_y,2*cell_width,cell_height)
                    if self._chart_title_font_size != None:
                        font = QFont()
                        font.setPixelSize(self._chart_title_font_size)
                        painter.setFont(font)                    
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignTop+Qt.AlignmentFlag.AlignLeft,chart_title.strip())
                    """ reset painter """
                    font = QFont()
                    painter.setFont(font)                    
                if row == (row_count/2) and col==(col_count/2) and chart_title:
                    cell_x = round(self.x + col*cell_width)
                    cell_y = round(self.y + (row)*cell_height)
                    cell_rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                    icon = QPixmap(_image_path+'//lord_ganesha1.jpg')
                    painter.drawPixmap(cell_rect, icon)
class NorthIndianChart(QWidget):
    _north_label_font_size = 9
    _north_chart_house_x = 1
    _north_chart_house_y = _north_chart_house_x
    _north_chart_house_width = 350 #300
    _north_chart_house_height = _north_chart_house_width
    _north_label_positions = [(4/10,1.0/10),(1.5/10,0.5/10),(0.1/10,2.0/10),(1.5/10,4/10), 
                     (0.1/10,7/10), (1.75/10,8.5/10), (3.5/10,7/10), (6.75/10,8.5/10),
                     (8.5/10,7/10),(6.5/10,4/10),(8.35/10,2.0/10),(6.5/10,0.5/10)]
    _north_arudha_positions = [(5/10,3.75/10),(3.25/10,0.1/10),(0.1/10,3.75/10),(2.25/10,6.5/10), 
                     (0.1/10,8.75/10), (0.5/10,9.5/10), (4.5/10,8.25/10), (8.75/10,9.5/10),
                     (9.25/10,8.75/10),(7.25/10,6.5/10),(9.25/10,3.75/10),(8.75/10,0.25/10)]
    _north_zodiac_label_positions = [(4.75/10,0.25/10),(2.25/10,1.75/10),(0.05/10,0.25/10),(2.25/10,2.75/10), 
                     (0.1/10,5.25/10), (2.25/10,7.75/10), (4.75/10,5.5/10), (7.25/10,7.75/10),
                     (9.5/10,5.5/10),(7.25/10,2.75/10),(9.5/10,0.5/10),(7.25/10,1.75/10)]
    _north_chart_icon_x = int((_north_chart_house_width/2)*0.85)
    _north_chart_icon_y = int((_north_chart_house_height/2)*0.85)
    _north_chart_icon_width = 50
    _north_chart_icon_height = _north_chart_icon_width
    def __init__(self,data=None,chart_house_size:tuple=(_north_chart_house_x,_north_chart_house_y,_north_chart_house_width,_north_chart_house_height),
                 label_font_size:int=_north_label_font_size,chart_size_factor:float=1.0,arudha_lagna_data=None):
        drik._TROPICAL_MODE = False #V2.3.0
        drik.set_sideral_planets() #V2.3.0
        QWidget.__init__(self)
        self._chart_house_size = chart_house_size
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self.row_count = 4
        self.col_count = 4
        self._asc_house = 0
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2]*self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3]*self._chart_size_factor)
        self.resources=[]
        self._chart_title = ''
        self._grid_labels = []
        self.label_positions = NorthIndianChart._north_label_positions
        self.zodiac_label_positions = NorthIndianChart._north_zodiac_label_positions
        self.north_arudha_positions = NorthIndianChart._north_arudha_positions
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def set_chart_label_positions(self,chart_label_positions):
        self.label_positions = chart_label_positions
    def set_chart_zodiac_label_positions(self,zodiac_label_positions):
        self.zodiac_label_positions = zodiac_label_positions
    def paintEvent(self, event):
        self.event = event
        self._draw_north_indian_chart()#event)
    def setData(self,data,chart_title='',chart_title_font_size=None,arudha_lagna_data=None):
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        self._chart_title_font_size = chart_title_font_size
        self._chart_title = chart_title
    def _draw_north_indian_chart(self):#,event):
        painter = QPainter(self)
        chart_width = self.house_width
        chart_height = self.house_height
        cell_width = round(chart_width / self.col_count)
        cell_height = round(chart_height / self.row_count)
        # first draw a square 
        rect = QtCore.QRect(self.x,self.y,chart_width,chart_height)
        painter.drawRect(rect)
        # Draw icon
        icon_x = int(NorthIndianChart._north_chart_icon_x * self._chart_size_factor)
        icon_y = int(NorthIndianChart._north_chart_icon_y * self._chart_size_factor)
        icon_width = int(NorthIndianChart._north_chart_icon_width * self._chart_size_factor)
        icon_height = int(NorthIndianChart._north_chart_icon_height * self._chart_size_factor)
        icon_rect = QtCore.QRect(icon_x,icon_y,icon_width,icon_height)
        icon = QPixmap(_image_path+"//lord_ganesha1.jpg")
        painter.drawPixmap(icon_rect,icon)
        # draw diagonals
        diag_start_x = self.x
        diag_start_y = self.y
        diag_end_x = round(diag_start_x + chart_width)
        diag_end_y = round(diag_start_y + chart_height)
        painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
        diag_start_x = self.x
        diag_start_y = round(self.y + chart_height)
        diag_end_x = round(self.x + chart_width)
        diag_end_y = self.y
        painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
        # Draw internal square
        start_x = self.x
        start_y = round(self.y + chart_height / 2)
        end_x = round(self.x + chart_width / 2)
        end_y = self.y
        painter.drawLine(start_x,start_y,end_x,end_y) 
        start_x = end_x
        start_y = end_y
        end_x = round(self.x + chart_width)
        end_y = round(self.y + chart_height / 2)
        painter.drawLine(start_x,start_y,end_x,end_y) 
        start_x = end_x
        start_y = end_y
        end_x = round(self.x + chart_width / 2)
        end_y = round(self.y + chart_height)
        painter.drawLine(start_x,start_y,end_x,end_y) 
        start_x = end_x
        start_y = end_y
        end_x = self.x
        end_y = round(self.y + chart_height / 2)
        painter.drawLine(start_x,start_y,end_x,end_y) 
        title_x = self.x #round(self.x + chart_width/3)
        title_y = self.y + chart_height + self.y
        title_height = 20
        title_width = chart_width
        self._chart_title.replace('\n',' ')
        title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
        if self._chart_title_font_size != None:
            font = QFont()
            font.setPixelSize(self._chart_title_font_size)
            painter.setFont(font)                    
        painter.drawText(title_rect,Qt.AlignmentFlag.AlignCenter,self._chart_title.strip())
        """ reset painter """
        font = QFont()
        painter.setFont(font)                    
        _label_counter = 0
        font = QFont()
        font.setPixelSize(self._label_font_size)
        painter.setFont(font)                    
        for l, pos in enumerate(self.label_positions):
            zl = (l+self._asc_house-1) % 12
            x = pos[0]
            zx = self.zodiac_label_positions[l][0]
            ax = self.north_arudha_positions[l][0]
            y = pos[1]
            zy = self.zodiac_label_positions[l][1]
            ay = self.north_arudha_positions[l][1]
            label_text = str(self.data[l])
            label_x = round(self.x + x*chart_width)
            label_y = round(self.y + y*chart_height)
            cell_height = round(chart_height / self.row_count)
            cell_width = round(chart_width / self.col_count)
            cell_rect = QtCore.QRect(label_x,label_y,cell_width,cell_height)
            painter.drawText(cell_rect,0,label_text.strip())
            zodiac_label_text = _zodiac_symbols[zl]
            zodiac_label_x = round(self.x + zx*chart_width)
            zodiac_label_y = round(self.y + zy*chart_height)
            zodiac_cell_rect = QtCore.QRect(zodiac_label_x,zodiac_label_y,cell_width,cell_height)
            painter.drawText(zodiac_cell_rect,0,zodiac_label_text.strip())
            if self.arudha_lagna_data:
                arudha_label_text = self.arudha_lagna_data[l]
                arudha_label_x = round(self.x + ax*chart_width)
                arudha_label_y = round(self.y + ay*chart_height)
                arudha_cell_rect = QtCore.QRect(arudha_label_x,arudha_label_y,cell_width,cell_height)
                painter.drawText(arudha_cell_rect,0,arudha_label_text.strip())
            _label_counter += 1
        painter.end()
def _convert_1d_chart_with_planet_names(chart_1d_list): #To be used for Sudarsana Chakra data as input
    from hora.horoscope.chart import house
    result = []
    retrograde_planets = chart_1d_list[-1]
    #print('_convert_1d_chart_with_planet_names - retrograde_planets',retrograde_planets)
    for chart_1d in chart_1d_list[:-1]:
        #print('chart_1d',chart_1d)
        res = []
        for z,pls in chart_1d:
            #print('z',z,'pls',pls)
            pl_str = ''
            tmp = pls.split('/')
            if len(tmp) == 1 and tmp[0] =='':
                pl_str = ''
                res.append((z,pl_str))
                continue
            for p in tmp:
                if p == const._ascendant_symbol:
                    pl_str += 'Lagnam'+'/'#const._ascendant_symbol+"/"
                else:
                    ret_str = ''
                    if int(p) in retrograde_planets:
                        #print('planet ',utils.PLANET_SHORT_NAMES[int(p)],'is retrograde',const._retrogade_symbol)
                        ret_str = const._retrogade_symbol
                    pl_str += house.planet_list[int(p)]+ret_str+'/'#const._planet_symbols[int(p)]+'/'
            pl_str = pl_str[:-1]
            #print('tmp',tmp,(z,pl_str))
            res.append((z,pl_str))
        result.append(res)
    return result
if __name__ == "__main__":
    import sys
    #"""
    from hora.horoscope.dhasa import sudharsana_chakra
    from hora import utils
    from hora.panchanga import drik
    from hora.horoscope.chart import house, charts
    from hora.horoscope import main
    _chart_names = ['raasi_str','hora_str','drekkanam_str','chaturthamsa_str','panchamsa_str',
                  'shashthamsa_str','saptamsam_str','ashtamsa_str','navamsam_str','dhasamsam_str','rudramsa_str',
                  'dhwadamsam_str','shodamsa_str','vimsamsa_str','chaturvimsamsa_str','nakshatramsa_str','thrisamsam_str',
                  'khavedamsa_str','akshavedamsa_str','sashtiamsam_str']
    dob = drik.Date(1997,12,7)
    tob_str = '10:34:00 AM'
    tob = tuple(map(int,tob_str.replace(' AM','').replace(' PM','').split(':')))
    print(tob)
    jd = utils.julian_day_number(dob, tob)
    language ='ta'
    place = drik.Place('Chennai',13.5,81.5,5.5)
    horo = main.Horoscope(latitude=place.latitude,longitude=place.longitude,timezone_offset=place.timezone,
                                       date_in=dob,birth_time=tob_str)
    _calendar_info = horo.get_calendar_information(language=language)
    _resources= horo._get_calendar_resource_strings(language=language)
    _,horo_charts = horo.get_horoscope_information(language=language)
    dcf = 9
    chart_index = const.division_chart_factors.index(dcf)
    chart_title = _resources[_chart_names[chart_index]]
    chart_data_1d = horo_charts[chart_index]
    chart_data_1d = [x[:-1] for x in chart_data_1d] # remove ]n from end of each element
    print(chart_data_1d)
    _western_data = ['லக்னம் ♑︎மகரம் 22° 26’ 37"','சூரியன்☉ ♏︎விருச்சிகம் 21° 33’ 34"','சந்திரன்☾ ♎︎துலாம் 6° 57’ 33"',
                         'செவ்வாய்♂ ♌︎சிம்மம் 25° 32’ 10"','புதன்☿ ♐︎தனுசு 9° 55’ 36"','குரு♃ ♐︎தனுசு 25° 49’ 14"',
                         'சுக்ரன்♀ ♎︎துலாம் 23° 42’ 24"','சனி♄ ♓︎மீனம் 6° 48’ 25"','ராகு☊ ♍︎கன்னி 10° 33’ 13"',
                         'கேது☋ ♓︎மீனம் 10° 33’ 13"']
    def _index_containing_substring(the_list, substring):
        for i, s in enumerate(the_list):
            if substring in s:
                return i
        return -1
    def _convert_1d_chart_with_planet_names(chart_1d_list): #To be used for Sudarsana Chakra data as input
        from hora.horoscope.chart import house
        result = []
        retrograde_planets = chart_1d_list[-1]
        #print('_convert_1d_chart_with_planet_names - retrograde_planets',retrograde_planets)
        for chart_1d in chart_1d_list[:-1]:
            #print('chart_1d',chart_1d)
            res = []
            for z,pls in chart_1d:
                #print('z',z,'pls',pls)
                pl_str = ''
                tmp = pls.split('/')
                if len(tmp) == 1 and tmp[0] =='':
                    pl_str = ''
                    res.append((z,pl_str))
                    continue
                for p in tmp:
                    if p == const._ascendant_symbol:
                        pl_str += _resources['ascendant_short_str']+'/'#' 'Lagnam'+'/'#const._ascendant_symbol+"/"
                    else:
                        ret_str = ''
                        if int(p) in retrograde_planets:
                            #print('planet ',utils.PLANET_SHORT_NAMES[int(p)],'is retrograde',const._retrogade_symbol)
                            ret_str = const._retrogade_symbol
                        pl_str += utils.PLANET_SHORT_NAMES[int(p)]+ret_str+'/'# house.planet_list[int(p)]+'/'#const._planet_symbols[int(p)]+'/'
                pl_str = pl_str[:-1]
                #print('tmp',tmp,(z,pl_str))
                res.append((z,pl_str))
            result.append(res)
        return result
    def _convert_1d_house_data_to_2d(rasi_1d,chart_type='south indian'):
        separator = '/'
        if 'south' in chart_type.lower():
            row_count = 4
            col_count = 4
            map_to_2d = [ [11,0,1,2], [10,"","",3], [9,"","",4], [8,7,6,5] ]
        elif 'east' in chart_type.lower():
            row_count = 3
            col_count = 3
            map_to_2d = [['2'+separator+'1','0','11'+separator+'10'], ['3', "",'9' ], ['4'+separator+'5','6','7'+separator+'8']]
        rasi_2d = [['X']*row_count for _ in range(col_count)]
        for p,val in enumerate(rasi_1d):
            for index, row in enumerate(map_to_2d):
                if 'south' in chart_type.lower():
                    i,j = [(index, row.index(p)) for index, row in enumerate(map_to_2d) if p in row][0]
                    rasi_2d[i][j] = str(val)
                elif 'east' in chart_type.lower():
                    p_index = _index_containing_substring(row,str(p))
                    if p_index != -1:
                        i,j = (index, p_index)
                        if rasi_2d[i][j] != 'X':
                            if index > 0:
                                rasi_2d[i][j] += separator + str(val)
                            else:
                                rasi_2d[i][j] = str(val) + separator + rasi_2d[i][j]
                        else:
                            rasi_2d[i][j] = str(val)
        for i in range(row_count):
            for j in range(col_count):
                if rasi_2d[i][j] == 'X':
                    rasi_2d[i][j] = ''
        return rasi_2d
    def _get_row_col_string_match_from_2d_list(list_2d,match_string):
        for row in range(len(list_2d)):
            for col in range(len(list_2d[0])):
                if match_string in list_2d[row][col]:
                    return (row,col)
    def _set_chart_data(Chart,chart_type,_chart_title):
            arudha_data = ['AL'+str(i+1) for i in range(12)]
            if 'north' in chart_type.lower():
                _ascendant = drik.ascendant(jd,place)
                asc_house = _ascendant[0]+1
                chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
                Chart.setData(chart_data_north,chart_title=_chart_title,chart_title_font_size=8,arudha_lagna_data=arudha_data)
            elif 'east' in chart_type.lower():
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d,chart_type)
                arudha_data_2d = _convert_1d_house_data_to_2d(arudha_data,chart_type)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,_resources['ascendant_str'])
                Chart._asc_house = row*Chart.row_count+col
                Chart.setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=10,arudha_lagna_data=arudha_data_2d)
            elif 'west' in chart_type.lower():
                Chart.setData(_western_data,chart_title=_chart_title,chart_title_font_size=8)
                Chart.update()                
            elif 'sudar' in chart_type.lower():
                chart_1d = sudharsana_chakra.sudharshana_chakra_chart(jd, place,dob,years_from_dob=0, divisional_chart_factor=dcf)
                #print('chart_1d',chart_1d)
                data_1d = _convert_1d_chart_with_planet_names(chart_1d)
                Chart.setData(data_1d,chart_title=_chart_title,chart_title_font_size=8)
                Chart.update()                
            else: # south indian
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d)
                arudha_data_2d = _convert_1d_house_data_to_2d(arudha_data,chart_type)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,_resources['ascendant_str'])
                Chart._asc_house = (row,col)
                Chart.setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=12,arudha_lagna_data=arudha_data_2d)
            Chart.update()
#    print(data_1d)
    #exit()
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart_type = 'North Indian'
    if 'south' in chart_type.lower():
        Chart = SouthIndianChart()
    elif 'north' in chart_type.lower():
        Chart = NorthIndianChart(chart_size_factor=1.5)
    elif 'east' in chart_type.lower():
        Chart = EastIndianChart()
    elif 'west' in chart_type.lower():
        Chart = WesternChart()
    elif 'sudar' in chart_type.lower():
        Chart = SudarsanaChakraChart()
    else:
        Chart = SouthIndianChart()
    _set_chart_data(Chart, chart_type, chart_title)
    Chart.show()
    sys.exit(App.exec())
    