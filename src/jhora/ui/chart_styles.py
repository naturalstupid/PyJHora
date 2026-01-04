#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import math
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont, QPainter, QAction, QColor, QPen
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication, QMenu, QDialog, QLabel, QCheckBox, \
                            QRadioButton, QSpinBox, QHBoxLayout, QVBoxLayout, QButtonGroup, QPushButton
from PyQt6.QtCore import Qt

from jhora import const,utils
from jhora.panchanga import drik #V2.3.0

color_label = lambda label,color: '<span style=color:'+color+';>'+label+'</span>'
_rasi_color = 'Red'; _planet_color = 'Brown'; _text_color='Green'; _arudha_color = 'Blue'
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
_lagnam_line_factor = 0.3
_lagnam_line_thickness = 3
_image_path = os.path.abspath(const._IMAGES_PATH)
_zodiac_icons = ['mesham.jpg','rishabham.jpg','mithunam.jpg','katakam.jpg','simmam.jpg','kanni.jpg','thulam.jpg','vrichigam.jpg','dhanusu.jpg','makaram.jpg','kumbam.jpg','meenam.jpg']
def _fit_table_widgets_to_contents(tableWidgets):
    for table in tableWidgets:
        for row in range(table.rowCount()):
            table.resizeRowToContents(row)
            for col in range(table.columnCount()):
                table.resizeColumnToContents(col)
def replace_ascendant_with_prasna_lagna(planet_list,prasna_list,chart_type='south indian'):
    #print(chart_type,'before planet/prasna list', planet_list,prasna_list)
    plag = utils.resource_strings['prasna_lagna_short_str']
    lagna = utils.resource_strings['ascendant_str']
    new_lagna = lagna+'('+plag+')'
    if 'south' in chart_type.lower() or 'east' in chart_type.lower():
        prasna_2d = utils._convert_1d_house_data_to_2d(prasna_list, chart_type=chart_type)
        #print('prasna_2d',prasna_2d)
        (rp,cp) = utils.get_2d_list_index(prasna_2d,plag,contains_in_element=True)
        # Remove from prasna list
        prasna_list = [ele.replace(plag,'') for ele in prasna_list]
        # Remove Lagna from planet_list
        planet_list = [[ele.replace(lagna,"") for ele in row] for row in planet_list]
        planet_list[rp][cp] = new_lagna +'\n'+planet_list[rp][cp] if planet_list[rp][cp] !='' else new_lagna
        asc_house = (rp,cp)
        #print(chart_type,'after planet/prasna list', planet_list,prasna_list)
        return planet_list,prasna_list, asc_house
    elif 'north' in chart_type.lower():
        rp = utils.get_1d_list_index(prasna_list,plag,contains_in_element=True)
        planet_list = [ele.replace(lagna,'') for ele in planet_list]
        prasna_list = [ele.replace(plag,'') for ele in prasna_list]
        planet_list[rp] = new_lagna +'\n'+planet_list[rp] if planet_list[rp] !='' else new_lagna
        asc_house = rp
        #print(chart_type,'after planet/prasna list', planet_list,prasna_list)
        return planet_list,prasna_list, asc_house
class PrasnaDialog(QDialog):
    def __init__(self, parent=None,varga_factor=1):
        super().__init__(parent)
        self._varga_factor = varga_factor
        self.setWindowTitle(utils.resource_strings['prasna_lagna_str']+' '+utils.resource_strings['options_str'])

        # Layouts
        main_layout = QVBoxLayout()
        radio_layout = QHBoxLayout()
        spin_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # CheckBox
        self.random_checkbox = QCheckBox(utils.resource_strings['random_number_str'])
        main_layout.addWidget(self.random_checkbox)
        self.random_checkbox.clicked.connect(self.on_random_selection_changed)

        # Radio Buttons
        self.radio_prasna108 = QRadioButton(utils.resource_strings['prasna_lagna_str']+'-108')
        self.radio_prasnakp249 = QRadioButton(utils.resource_strings['prasna_lagna_str']+'KP-249')
        self.radio_prasna_nadi = QRadioButton(utils.resource_strings['naadi_str']+'-1800')
        self.radio_prasna108.setChecked(True)
        
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_prasna108)
        self.radio_group.addButton(self.radio_prasnakp249)
        self.radio_group.addButton(self.radio_prasna_nadi)
        
        radio_layout.addWidget(self.radio_prasna108)
        radio_layout.addWidget(self.radio_prasnakp249)
        radio_layout.addWidget(self.radio_prasna_nadi)
        main_layout.addLayout(radio_layout)

        # SpinBox
        self.spin_box = QSpinBox()
        self._spin_max = 108
        self.spin_box.setRange(1, self._spin_max)
        self._spin_label = QLabel((utils.resource_strings['prasna_label_str']+' (1..'+str(self._spin_max)+')'))
        spin_layout.addWidget(self._spin_label)
        spin_layout.addWidget(self.spin_box)
        main_layout.addLayout(spin_layout)
        # Radio Button change event
        self.radio_group.buttonClicked.connect(self.on_radio_button_changed)
        
        # add lagnam replacement choices
        radio_group1 = QButtonGroup()
        self.keep_lagna_radio_button = QRadioButton(utils.resource_strings['prasna_replace_lagna_label1_str'])
        self.keep_lagna_radio_button.setChecked(True)
        radio_group1.addButton(self.keep_lagna_radio_button)
        main_layout.addWidget(self.keep_lagna_radio_button)
        self.replace_lagna_radio_button = QRadioButton(utils.resource_strings['prasna_replace_lagna_label2_str'])
        radio_group1.addButton(self.replace_lagna_radio_button)
        main_layout.addWidget(self.replace_lagna_radio_button)
        # Individual Accept and Cancel buttons
        self.accept_button = QPushButton(utils.resource_strings['accept_str'])
        self.cancel_button = QPushButton(utils.resource_strings['cancel_str'])

        self.accept_button.clicked.connect(self.accept_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
    def on_random_selection_changed(self):
        import random
        if self.random_checkbox.isChecked():
            r = random.randint(1,self._spin_max)
            self.spin_box.setEnabled(False); self.spin_box.setValue(r)
        else:
            self.spin_box.setEnabled(True)
    def on_radio_button_changed(self):
        import random
        if self.radio_prasna108.isChecked():
            self._spin_max = 108
        elif self.radio_prasnakp249.isChecked():
            self._spin_max = 249
        elif self.radio_prasna_nadi.isChecked():
            self._spin_max = 1800
        self.spin_box.setRange(1,self._spin_max)
        self._spin_label.setText((utils.resource_strings['prasna_label_str']+' (1..'+str(self._spin_max)+')'))
        if self.random_checkbox.isChecked(): self.spin_box.setValue(random.randint(1,self._spin_max))
    def accept_clicked(self):
        kp_no = int(self.spin_box.value())
        if self.radio_prasna108.isChecked():
            plag = utils.get_prasna_lagna_108_for_varga_chart(kp_no,self._varga_factor)
        elif self.radio_prasnakp249.isChecked():
            plag = utils.get_prasna_lagna_KP_249_for_varga_chart(kp_no,self._varga_factor)
        elif self.radio_prasna_nadi.isChecked():
            plag = utils.get_prasna_lagna_nadi_for_varga_chart(kp_no,self._varga_factor)
        self.prasna_lagna = plag
        self.replace_lagna = self.replace_lagna_radio_button.isChecked()
        self.accept()
    def cancel_clicked(self):
        self.reject()
        self.close()
def show_prasna_dialog(varga_factor=1):
    dialog = PrasnaDialog(varga_factor=varga_factor)
    data = ['' for _ in range(12)]
    if dialog.exec() == QDialog.DialogCode.Accepted:
        data [dialog.prasna_lagna]=utils.resource_strings['prasna_lagna_short_str']
    else:
        return []
    return data, dialog.replace_lagna
class SudarsanaChakraChart(QWidget):
    """
        Sudarsana Chakra Chart 
    """
    def __init__(self,data=None,chart_center_pos:tuple=(175,175),chart_radii:tuple=(75,125,175),
                 chart_inner_square:tuple=(30,30),label_font_size:int=8,chart_label_radius_factor:float=0.15,
                 chart_size_factor:float=1.0,chart_title_font_size=9, chart_title = ''):
        QWidget.__init__(self)
        self._chart_title = chart_title
        self._data_counter = 0
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
    def setData(self,data,chart_title='',chart_title_font_size=9):
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
        if self.chart_title_font_size  is not None:
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
        font = QFont()
        font.setPixelSize(self.sc_label_font_size)
        painter.setFont(font)
        painter.setPen(QColor(_rasi_color))
        self.drawNode(painter,pt,pr,const._zodiac_symbols[z])
        painter.setPen(QPen())
        if p_len == 0:
            return
        painter.setPen(QColor(_planet_color))
        for p in planets:
            pt -= tinc
            tx = int(cx+pr*math.cos(pt))
            ty = int(cy - pr*math.sin(pt))
            trect = QtCore.QRect(tx,ty,tw,th)
            self.drawNode(painter,pt,pr,p)
        painter.setPen(QPen())
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
                 chart_size_factor:float=1.0,chart_title_font_size=_west_chart_title_font_size,
                 chart_title = ''):
        QWidget.__init__(self)
        self._chart_title = chart_title
        self._data_counter = 0
        self._chart_center_pos = tuple([int(x*chart_size_factor) for x in chart_center_pos])
        self._chart_radii = tuple([int(x*chart_size_factor) for x in chart_radii])
        self._label_font_size = label_font_size
        self._label_pos_radial_increment = label_pos_radial_increment*chart_size_factor
        self._chart_size_factor = chart_size_factor
        self.chart_title_font_size = chart_title_font_size
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
        painter.setPen(QColor(_planet_color))
        for i in range(len(self.data)):
            self._write_planets_inside_houses(painter,r2,self.data[i],i)
        painter.setPen(QPen())
        painter.setPen(QColor(_rasi_color))
        for i_z in range(12):
            z_i = (self._asc_house+i_z+12)%12
            zodiac_symbol = _zodiac_symbols[z_i]
            house_mid_angle = (i_z*30+self._asc_longitude+155)#*math.pi/180.0
            rect = QtCore.QRect(int(cx+r34*math.cos(house_mid_angle*math.pi/180.0)),int(cy-r34*math.sin(house_mid_angle*math.pi/180.0)),10,10)
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,zodiac_symbol.strip())
        painter.setPen(QPen())
        rect = QtCore.QRect(cx-r1,cy-r1,r1*2,2*r1)
        title_x = cx - r3
        title_y = cy + r3
        title_height = 20
        title_width = 2*r3
        title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
        #print('chart style north indian chart title',self._chart_title)
        self._chart_title.replace('\n',' ')
        #print('chart style north indian chart title',self._chart_title)
        if self.chart_title_font_size  is not None:
            font = QFont()
            font.setPixelSize(self.chart_title_font_size)
            painter.setFont(font)                    
        painter.setPen(QColor(_text_color))
        _chart_title = self._chart_title.strip().split()[0] if self._chart_title.strip() != '' else ''
        painter.drawText(title_rect,Qt.AlignmentFlag.AlignCenter,_chart_title)
        """ reset painter """
        painter.setPen(QPen())
        painter.setFont(QFont())                    
    def _write_planets_inside_houses(self,painter,radius,data,i_z):
        tmp_arr = data.strip().split()
        planet = tmp_arr[0][-2:].strip() if const._retrogade_symbol in tmp_arr[0] else tmp_arr[0][-1:].strip() 
        zodiac = tmp_arr[1][0].strip()
        deg = int(tmp_arr[-3][:-1].strip())
        mins = int(tmp_arr[-2][:-1].strip())
        sec = int(tmp_arr[-1][:-1].strip())
        #deg = int(tmp_arr[2][:-1].strip())
        #mins = int(tmp_arr[3][:-1].strip())
        #sec = int(tmp_arr[4][:-1].strip())
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
        self.data = data; 
        tmp_arr = data[0].strip().split()
        deg = int(tmp_arr[-3][:-1].strip())
        mins = int(tmp_arr[-2][:-1].strip())
        sec = int(tmp_arr[-1][:-1].strip())
        #deg = int(tmp_arr[2][:-1].strip())
        #mins = int(tmp_arr[3][:-1].strip())
        #sec = int(tmp_arr[4][:-1].strip())
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
                 arudha_lagna_data=None,chart_title=''):
        QWidget.__init__(self)
        self._chart_title = chart_title
        self._data_counter = 0
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
        self._drishti_dialog = None
        self._aspect_dialog = None
        self._planet_info_dialog = None
        self._ndl_22_dialog=None; self._ndl_64_dialog = None
        self._graha_drekkana_dialog = None
        self._nava_thaara_dialog = None; self._spl_thaara_dialog = None
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def showContextMenu(self,pos):
        self.menu = QMenu(self)
        self._display_info_dict = {}
        self.build_menu(self.menu, self._menu_dict)
        self.menu.exec(self.mapToGlobal(pos))
    def build_menu(self, menu, data):
        for key, value in data.items():
            if isinstance(value,dict):
                submenu = QMenu(key, self)
                self.build_menu(submenu, value)
                menu.addMenu(submenu)
            else:
                action = QAction(key, self)
                action.setData(value)
                action.triggered.connect(lambda checked,key=key : self.set_menu_data(key))
                menu.addAction(action)
    def set_menu_data(self,key):
        self.menu.close()
        action = self.sender(); alt_data = action.data()
        if isinstance(alt_data,str):
            self._display_info_dict[key] = alt_data
            alt_data = ['' for _ in range(12)]
        if key == utils.resource_strings['prasna_lagna_str']+'('+utils.resource_strings['prasna_lagna_short_str']+')':
            ret = show_prasna_dialog(self._varga_factor)
            if len(ret)==0: return
            alt_data,_replace_lagna = ret
            if _replace_lagna:
                self._data_counter += 1
                if self._data_counter == 1: 
                    self._data_original = self.data # Keep a backup for Prasna
                    self._asc_house_original = self._asc_house
                self.data,alt_data,self._asc_house = replace_ascendant_with_prasna_lagna(self._data_original, alt_data, 'east indian')
            else:
                # replace 'lagna(plag) with lagna
                lagna = utils.resource_strings['ascendant_str']; plag = utils.resource_strings['prasna_lagna_short_str']
                self.data = utils.search_replace(self.data, lagna+'('+plag+')', lagna)
            if len(alt_data)>0:
                action = self.sender()
                action.setData(alt_data)
        elif key in [utils.resource_strings['pushkara_amsa_str']+', '+utils.resource_strings['pushkara_bhaga_str'],
                   utils.resource_strings['yogi_sphuta_str']+', '+utils.resource_strings['avayogi_sphuta_str']+', '+utils.resource_strings['sahayogi_str'],
                   utils.resource_strings['paachakaadi_sambhandha_str'],
                   utils.resource_strings['brahma_str']+','+utils.resource_strings['rudra_str']+','+utils.resource_strings['maheshwara_str'],
                   utils.resource_strings['combustion_str']+' '+utils.resource_strings['planets_str'],
                   utils.resource_strings['graha_yudh_str'],
                   utils.resource_strings['marana_karaka_sthana_str']+' '+utils.resource_strings['planets_str'],
                   utils.resource_strings['mrityu_bhaga_str'],
                   utils.resource_strings['raasi_str']+' '+utils.resource_strings['entry_str'],
                   utils.resource_strings['lattha_star_str'],
                   ]:
            from jhora.ui.options_dialog import InfoDialog
            info_dialog = InfoDialog(title=key,
                                     info_text=self._display_info_dict[key],
                                     button_texts=[utils.resource_strings['accept_str']])
            info_dialog.exec()
        elif key==utils.resource_strings['drishti_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = utils.resource_strings['raasi_str']+'-'+utils.resource_strings['graha_str']+'-'+utils.resource_strings['drishti_str']
            if self._drishti_dialog is None and self._drishti_table_widgets is not None:
                self._drishti_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._drishti_table_widgets)
            _fit_table_widgets_to_contents(self._drishti_table_widgets)
            self._drishti_dialog.exec()
        elif key == utils.resource_strings['nava_thaara_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._nava_thaara_dialog is None and self._nava_thaara_widgets is not None:
                self._nava_thaara_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._nava_thaara_widgets,fit_to_widget_contents=True)
            self._nava_thaara_dialog.exec()            
        elif key == utils.resource_strings['special_thaara_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._spl_thaara_dialog is None and self._spl_thaara_widgets is not None:
                self._spl_thaara_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._spl_thaara_widgets,fit_to_widget_contents=True)
            self._spl_thaara_dialog.exec()            
        elif utils.resource_strings['planet_str']+' '+utils.resource_strings['drekkanam_str'].replace(' (D3)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._graha_drekkana_dialog is None and self._graha_drekkana_widgets is not None:
                self._graha_drekkana_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._graha_drekkana_widgets,fit_to_widget_contents=True)
            self._graha_drekkana_dialog.exec()
        elif '22nd '+utils.resource_strings['drekkanam_str'].replace(' (D3)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._ndl_22_dialog is None and self._ndl_22_widgets is not None:
                self._ndl_22_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._ndl_22_widgets,fit_to_widget_contents=True)
            self._ndl_22_dialog.exec()
        elif '64th '+utils.resource_strings['navamsam_str'].replace(' (D9)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._ndl_64_dialog is None and self._ndl_64_widgets is not None:
                self._ndl_64_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._ndl_64_widgets,fit_to_widget_contents=True)
            self._ndl_64_dialog.exec()
        elif key==utils.resource_strings['planet_aspects_relations_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._aspect_dialog is None and self._aspect_widgets is not None:
                self._aspect_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._aspect_widgets,fit_to_widget_contents=True)
            self._aspect_dialog.exec()
        elif key == utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                    utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._planet_info_dialog is None and self._planet_info_widgets is not None:
                self._planet_info_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._planet_info_widgets)
            _fit_table_widgets_to_contents(self._planet_info_widgets)
            self._planet_info_dialog.exec()
        elif key==utils.resource_strings['planets_str']:
            try:
                self.data = self._data_original
                self._asc_house = self._asc_house_original
            except:
                pass
        alt_data_2d = utils._convert_1d_house_data_to_2d(alt_data,'east indian')
        self.setData(data=self.data, arudha_lagna_data=alt_data_2d,
                     chart_title=self._chart_title,chart_title_font_size=self._chart_title_font_size)
        self.update()
    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def paintEvent(self, event):
        self.event = event
        self.set_east_indian_chart_data()#event)
    def setData(self,data,chart_title='',chart_title_font_size=None,arudha_lagna_data=None,menu_dict=None,
                varga_factor=None,drishti_table_widgets=None,planet_info_widgets=None,aspect_widgets=None,
                ndl_22_widgets=None,ndl_64_widgets=None,graha_drekkana_widgets=None,nava_thaara_widgets=None,
                spl_thaara_widgets=None):
        if menu_dict !=None:
            self._menu_dict = menu_dict
            self._varga_factor = varga_factor
            self._drishti_table_widgets = drishti_table_widgets
            self._aspect_widgets = aspect_widgets
            self._planet_info_widgets = planet_info_widgets
            self._ndl_22_widgets = ndl_22_widgets;self._ndl_64_widgets = ndl_64_widgets
            self._graha_drekkana_widgets = graha_drekkana_widgets
            self._nava_thaara_widgets = nava_thaara_widgets; self._spl_thaara_widgets = spl_thaara_widgets
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.showContextMenu)
        from jhora.ui.options_dialog import WidgetDialog
        _title = utils.resource_strings['nava_thaara_str']
        if self._nava_thaara_dialog is not None and self._nava_thaara_widgets is not None:
            self._nava_thaara_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._nava_thaara_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['special_thaara_str']
        if self._spl_thaara_dialog is not None and self._spl_thaara_widgets is not None:
            self._spl_thaara_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._spl_thaara_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['planet_str']+' '+utils.resource_strings['drekkanam_str'].replace(' (D3)','')
        if self._graha_drekkana_dialog is not None and self._graha_drekkana_widgets is not None:
            self._graha_drekkana_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._graha_drekkana_widgets,fit_to_widget_contents=True)
        _title = '22nd '+utils.resource_strings['drekkanam_str'].replace(' (D3)','')
        if self._ndl_22_dialog is not None and self._ndl_22_widgets is not None:
            self._ndl_22_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._ndl_22_widgets,fit_to_widget_contents=True)
        _title = '64th '+utils.resource_strings['navamsam_str'].replace(' (D9)','')
        if self._ndl_64_dialog is not None and self._ndl_64_widgets is not None:
            self._ndl_64_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._ndl_64_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['raasi_str']+'-'+utils.resource_strings['graha_str']+'-'+utils.resource_strings['drishti_str']
        if self._drishti_dialog is not None and self._drishti_table_widgets is not None:
            self._drishti_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._drishti_table_widgets)
        _title = utils.resource_strings['planet_aspects_relations_str']
        if self._aspect_dialog is not None and self._aspect_widgets is not None:
            self._aspect_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._aspect_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']
        if self._planet_info_dialog is not None and self._planet_info_widgets is not None:
            self._planet_info_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._planet_info_widgets)
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
                font = QFont(); painter.setPen(QPen())
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
                painter.setPen(QPen())
                painter.drawRect(rect)
                if left_top_cell:
                    painter.setPen(QPen())
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha,top_cell_arudha = arudha.split("/")
                    # House 3
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_cell_text.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_arudha.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,'\n'+top_zodiac.strip())
                    # House 2
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_text.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_zodiac.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,'\n'+bottom_cell_arudha.strip())
                    painter.setPen(QPen())
                    # Draw cross line
                    diag_start_x = self.x
                    diag_start_y = self.y
                    diag_end_x = self.x + cell_width
                    diag_end_y = self.y + cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                    painter.setPen(QPen())
                elif right_top_cell:
                    painter.setPen(QPen())
                    top_cell_text,bottom_cell_text = cell.split("/") # Fixed in 1.1.0
                    top_zodiac,bottom_zodiac = zodiac_symbol.split("/")
                    top_cell_arudha,bottom_cell_arudha = arudha.split("/") # Fixed in 1.1.0
                    # House 11
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,top_cell_text.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,top_cell_arudha.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,'\n'+top_zodiac.strip())
                    # House 12
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,bottom_cell_text.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,bottom_zodiac.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,'\n'+bottom_cell_arudha.strip())
                    # Draw cross line
                    diag_start_x = self.x + chart_width
                    diag_start_y = self.y
                    diag_end_x = self.x + chart_width - cell_width
                    diag_end_y = self.y + cell_height
                    painter.setPen(QPen())
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                    painter.setPen(QPen())
                elif right_bottom_cell:
                    painter.setPen(QPen())
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha,top_cell_arudha = arudha.split("/")
                    # House 8
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_text.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_zodiac.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,'\n'+bottom_cell_arudha.strip())
                    # House 9
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_cell_text.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_arudha.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,'\n'+top_zodiac.strip())
                    # Draw cross line
                    diag_start_x = self.x + chart_width - cell_width
                    diag_start_y = self.y + chart_height - cell_height
                    diag_end_x = self.x + chart_width
                    diag_end_y = self.y + chart_height
                    painter.setPen(QPen())
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                    painter.setPen(QPen())
                elif left_bottom_cell:
                    painter.setPen(QPen())
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha,top_cell_arudha = arudha.split("/")
                    # House 5
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_cell_text.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_arudha.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,'\n'+bottom_zodiac.strip())
                    # House 6
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_text.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_zodiac.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,'\n'+top_cell_arudha.strip())
                    # Draw cross line
                    diag_start_x = self.x
                    diag_start_y = self.y + chart_height
                    diag_end_x = self.x + cell_width
                    diag_end_y = self.y + chart_height - cell_height
                    painter.setPen(QPen())
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                    painter.setPen(QPen())
                # write chart title in center of the chart
                elif center_cell and chart_title:
                    painter.setPen(QColor(_text_color))
                    title_x = self.x #round(self.x + chart_width/3)
                    title_y = self.y + chart_height + self.y
                    title_height = 20
                    title_width = chart_width
                    title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
                    chart_title.replace('\n',' ')
                    if self._chart_title_font_size  is not None:
                        font = QFont()
                        font.setPixelSize(self._chart_title_font_size)
                        painter.setFont(font)          
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,chart_title.strip())
                    painter.setPen(QPen())
                    """ reset painter """
                    font = QFont()
                    painter.setFont(font)                    
                    rect_image = QtCore.QRect(round(cell_x+cell_width/2),round(cell_y),round(cell_width/2),round(cell_height/2))
                    icon = QPixmap(_image_path+'//lord_ganesha1.jpg')
                    painter.drawPixmap(rect_image, icon)
                    painter.setPen(QPen())
                else:
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,cell.strip())
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,zodiac_symbol.strip())
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,arudha.strip())
                    painter.setPen(QPen())
                painter.setPen(QPen())
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
    _south_chart_title_font_size = 9
    def __init__(self,data=None,chart_house_size:tuple=(_south_chart_house_x,_south_chart_house_y,_south_chart_house_width,_south_chart_house_height),
                 label_font_size:int=_south_label_font_size,chart_size_factor:float = 1.0,
                 chart_title_font_size=_south_chart_title_font_size, arudha_lagna_data=None,
                 chart_title=''):
        QWidget.__init__(self)
        self._chart_house_size = chart_house_size
        self._data_counter = 0
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
        self._drishti_dialog = None; self._planet_info_dialog = None; self._aspect_dialog=None
        self._ndl_22_dialog=None; self._ndl_64_dialog = None
        self._graha_drekkana_dialog = None
        self._nava_thaara_dialog = None; self._spl_thaara_dialog = None
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        self._chart_title = chart_title
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def showContextMenu(self,pos):
        self.menu = QMenu(self)
        self._display_info_dict = {}
        self.build_menu(self.menu, self._menu_dict)
        self.menu.exec(self.mapToGlobal(pos))
    def build_menu(self, menu, data):
        for key, value in data.items():
            if isinstance(value,dict):
                submenu = QMenu(key, self)
                self.build_menu(submenu, value)
                menu.addMenu(submenu)
            else:
                action = QAction(key, self)
                action.setData(value)
                action.triggered.connect(lambda checked,key=key : self.set_menu_data(key))
                menu.addAction(action)
    def set_menu_data(self,key):
        self.menu.close()
        action = self.sender(); alt_data = action.data()
        if isinstance(alt_data,str):
            self._display_info_dict[key] = alt_data
            alt_data = ['' for _ in range(12)]
        if key == utils.resource_strings['prasna_lagna_str']+'('+utils.resource_strings['prasna_lagna_short_str']+')':
            ret = show_prasna_dialog(self._varga_factor)
            if len(ret)==0: return
            alt_data,_replace_lagna = ret
            if _replace_lagna:
                self._data_counter += 1
                if self._data_counter == 1: 
                    self._data_original = self.data # Keep a backup for Prasna
                    self._asc_house_original = self._asc_house
                self.data,alt_data,self._asc_house = replace_ascendant_with_prasna_lagna(self._data_original, alt_data, 'south indian')
            else:
                # replace 'lagna(plag) with lagna
                lagna = utils.resource_strings['ascendant_str']; plag = utils.resource_strings['prasna_lagna_short_str']
                self.data = utils.search_replace(self.data, lagna+'('+plag+')', lagna)
            if len(alt_data)>0:
                action = self.sender()
                action.setData(alt_data)
        elif key in [utils.resource_strings['pushkara_amsa_str']+', '+utils.resource_strings['pushkara_bhaga_str'],
                   utils.resource_strings['yogi_sphuta_str']+', '+utils.resource_strings['avayogi_sphuta_str']+', '+utils.resource_strings['sahayogi_str'],
                   utils.resource_strings['paachakaadi_sambhandha_str'],
                   utils.resource_strings['brahma_str']+','+utils.resource_strings['rudra_str']+','+utils.resource_strings['maheshwara_str'],
                   utils.resource_strings['combustion_str']+' '+utils.resource_strings['planets_str'],
                   utils.resource_strings['graha_yudh_str'],
                   utils.resource_strings['marana_karaka_sthana_str']+' '+utils.resource_strings['planets_str'],
                   utils.resource_strings['mrityu_bhaga_str'],
                   utils.resource_strings['raasi_str']+' '+utils.resource_strings['entry_str'],
                   utils.resource_strings['lattha_star_str'],
                   ]:
            from jhora.ui.options_dialog import InfoDialog
            info_dialog = InfoDialog(title=key,
                                     info_text=self._display_info_dict[key],
                                     button_texts=[utils.resource_strings['accept_str']])
            info_dialog.exec()
        elif key == utils.resource_strings['nava_thaara_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._nava_thaara_dialog is None and self._nava_thaara_widgets is not None:
                self._nava_thaara_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._nava_thaara_widgets,fit_to_widget_contents=True)
            self._nava_thaara_dialog.exec()            
        elif key == utils.resource_strings['special_thaara_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._spl_thaara_dialog is None and self._spl_thaara_widgets is not None:
                self._spl_thaara_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._spl_thaara_widgets,fit_to_widget_contents=True)
            self._spl_thaara_dialog.exec()            
        elif utils.resource_strings['planet_str']+' '+utils.resource_strings['drekkanam_str'].replace(' (D3)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._graha_drekkana_dialog is None and self._graha_drekkana_widgets is not None:
                self._graha_drekkana_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._graha_drekkana_widgets,fit_to_widget_contents=True)
            self._graha_drekkana_dialog.exec()
        elif '22nd '+utils.resource_strings['drekkanam_str'].replace(' (D3)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._ndl_22_dialog is None and self._ndl_22_widgets is not None:
                self._ndl_22_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._ndl_22_widgets,fit_to_widget_contents=True)
            self._ndl_22_dialog.exec()
        elif '64th '+utils.resource_strings['navamsam_str'].replace(' (D9)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._ndl_64_dialog is None and self._ndl_64_widgets is not None:
                self._ndl_64_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._ndl_64_widgets,fit_to_widget_contents=True)
            self._ndl_64_dialog.exec()
        elif key==utils.resource_strings['drishti_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = utils.resource_strings['raasi_str']+'-'+utils.resource_strings['graha_str']+'-'+utils.resource_strings['drishti_str']
            if self._drishti_dialog is None and self._drishti_table_widgets is not None:
                self._drishti_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._drishti_table_widgets)
            _fit_table_widgets_to_contents(self._drishti_table_widgets)
            self._drishti_dialog.exec()
        elif key==utils.resource_strings['planet_aspects_relations_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._aspect_dialog is None and self._aspect_widgets is not None:
                self._aspect_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._aspect_widgets,fit_to_widget_contents=True)
            self._aspect_dialog.exec()
        elif key == utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                    utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._planet_info_dialog is None and self._planet_info_widgets is not None:
                self._planet_info_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._planet_info_widgets)
            _fit_table_widgets_to_contents(self._planet_info_widgets)
            self._planet_info_dialog.exec()
        elif key==utils.resource_strings['planets_str']:
            try:
                self.data = self._data_original
                self._asc_house = self._asc_house_original
            except:
                pass
        alt_data_2d = utils._convert_1d_house_data_to_2d(alt_data,'south indian')
        self.setData(data=self.data, arudha_lagna_data=alt_data_2d,
                     chart_title=self._chart_title,chart_title_font_size=self._chart_title_font_size)
        self.update()
    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def paintEvent(self, event):
        self.event = event
        self.set_south_indian_chart_data()
    def setData(self,data,chart_title='',chart_title_font_size=None,arudha_lagna_data=None,menu_dict=None,
                varga_factor=None,drishti_table_widgets=None,planet_info_widgets=None,aspect_widgets=None,
                ndl_22_widgets=None,ndl_64_widgets=None,graha_drekkana_widgets=None,nava_thaara_widgets=None,
                spl_thaara_widgets=None):
        #import inspect; print('called by',inspect.stack()[1].function)
        if menu_dict !=None:
            self._menu_dict = menu_dict
            self._varga_factor = varga_factor
            self._drishti_table_widgets = drishti_table_widgets
            self._aspect_widgets = aspect_widgets
            self._planet_info_widgets=planet_info_widgets
            self._ndl_22_widgets = ndl_22_widgets;self._ndl_64_widgets = ndl_64_widgets
            self._graha_drekkana_widgets = graha_drekkana_widgets
            self._nava_thaara_widgets = nava_thaara_widgets; self._spl_thaara_widgets = spl_thaara_widgets
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.showContextMenu)
        from jhora.ui.options_dialog import WidgetDialog
        _title = utils.resource_strings['nava_thaara_str']
        if self._nava_thaara_dialog is not None and self._nava_thaara_widgets is not None:
            self._nava_thaara_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._nava_thaara_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['special_thaara_str']
        if self._spl_thaara_dialog is not None and self._spl_thaara_widgets is not None:
            self._spl_thaara_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._spl_thaara_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['planet_str']+' '+utils.resource_strings['drekkanam_str'].replace(' (D3)','')
        if self._graha_drekkana_dialog is not None and self._graha_drekkana_widgets is not None:
            self._graha_drekkana_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._graha_drekkana_widgets,fit_to_widget_contents=True)
        _title = '22nd '+utils.resource_strings['drekkanam_str'].replace(' (D3)','')
        if self._ndl_22_dialog is not None and self._ndl_22_widgets is not None:
            self._ndl_22_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._ndl_22_widgets,fit_to_widget_contents=True)
        _title = '64th '+utils.resource_strings['navamsam_str'].replace(' (D9)','')
        if self._ndl_64_dialog is not None and self._ndl_64_widgets is not None:
            self._ndl_64_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._ndl_64_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['raasi_str']+'-'+utils.resource_strings['graha_str']+'-'+utils.resource_strings['drishti_str']
        if self._drishti_dialog is not None and self._drishti_table_widgets is not None:
            self._drishti_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._drishti_table_widgets)
        _title = utils.resource_strings['planet_aspects_relations_str']
        if self._aspect_dialog is not None and self._aspect_widgets is not None:
            self._aspect_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._aspect_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']
        if self._planet_info_dialog is not None and self._planet_info_widgets is not None:
            self._planet_info_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._planet_info_widgets)
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        
        self.arudha_lagna_data = arudha_lagna_data
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
                font = QFont(); painter.setPen(QPen())
                font.setPixelSize(self._label_font_size)
                painter.setFont(font)                    
                cell_text = data[row][col]
                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)
                cell_rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                if row==0 or row==row_count-1 or col==0 or col==col_count-1:
                    if self.arudha_lagna_data:
                        painter.setPen(QColor(_arudha_color))
                        painter.drawText(cell_rect,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom,self.arudha_lagna_data[row][col].strip())
                    painter.setPen(QPen())
                    painter.drawRect(cell_rect)
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignCenter,cell_text.strip())
                    painter.setPen(QColor(_rasi_color))
                    # Write zodiac symbol
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop,self._zodiac_symbols[row][col].strip())
                    painter.setPen(QPen())
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
                    if self._chart_title_font_size  is not None:
                        font = QFont()
                        font.setPixelSize(self._chart_title_font_size)
                        painter.setFont(font)                    
                    painter.setPen(QColor(_text_color))
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignTop+Qt.AlignmentFlag.AlignLeft,chart_title.strip())
                    """ reset painter """
                    font = QFont()
                    painter.setFont(font); painter.setPen(QPen())              
                if row == (row_count/2) and col==(col_count/2) and chart_title:
                    cell_x = round(self.x + col*cell_width)
                    cell_y = round(self.y + (row)*cell_height)
                    cell_rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                    icon = QPixmap(_image_path+'//lord_ganesha1.jpg')
                    painter.drawPixmap(cell_rect, icon)
                painter.setPen(QPen())
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
    _north_chart_title_font_size = 9
    def __init__(self,data=None,chart_house_size:tuple=(_north_chart_house_x,_north_chart_house_y,_north_chart_house_width,_north_chart_house_height),
                 label_font_size:int=_north_label_font_size,chart_size_factor:float=1.0,arudha_lagna_data=None,
                 chart_title_font_size=_north_chart_title_font_size,chart_title=''):
        drik._TROPICAL_MODE = False #V2.3.0
        drik.set_sideral_planets() #V2.3.0
        QWidget.__init__(self)
        self._chart_house_size = chart_house_size
        self._data_counter = 0
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self._chart_title_font_size = chart_title_font_size
        self.row_count = 4
        self.col_count = 4
        self._asc_house = 0
        self.data = data
        self._drishti_dialog = None
        self._aspect_dialog = None
        self._planet_info_dialog = None
        self._ndl_22_dialog=None; self._ndl_64_dialog = None
        self._graha_drekkana_dialog = None
        self._nava_thaara_dialog = None; self._spl_thaara_dialog = None
        self.arudha_lagna_data = arudha_lagna_data
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2]*self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3]*self._chart_size_factor)
        self.resources=[]
        self._chart_title = chart_title
        self._grid_labels = []
        self.label_positions = NorthIndianChart._north_label_positions
        self.zodiac_label_positions = NorthIndianChart._north_zodiac_label_positions
        self.north_arudha_positions = NorthIndianChart._north_arudha_positions
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def showContextMenu(self,pos):
        self.menu = QMenu(self)
        self._display_info_dict = {}
        self.build_menu(self.menu, self._menu_dict)
        self.menu.exec(self.mapToGlobal(pos))
    def build_menu(self, menu, data):
        for key, value in data.items():
            if isinstance(value,dict):
                submenu = QMenu(key, self)
                self.build_menu(submenu, value)
                menu.addMenu(submenu)
            else:
                action = QAction(key, self)
                action.setData(value)
                action.triggered.connect(lambda checked,key=key : self.set_menu_data(key))
                menu.addAction(action)
    def set_menu_data(self,key):
        self.menu.close()
        action = self.sender(); alt_data = action.data()
        if isinstance(alt_data,str):
            self._display_info_dict[key] = alt_data
            alt_data = ['' for _ in range(12)]
        if key == utils.resource_strings['prasna_lagna_str']+'('+utils.resource_strings['prasna_lagna_short_str']+')':
            ret = show_prasna_dialog(self._varga_factor)
            if len(ret)==0: return
            alt_data,_replace_lagna = ret
            if _replace_lagna:
                self._data_counter += 1
                if self._data_counter == 1: 
                    self._data_original = self.data # Keep a backup for Prasna
                    self._asc_house_original = self._asc_house
                self.data,alt_data,self._asc_house = replace_ascendant_with_prasna_lagna(self._data_original, alt_data, 'north indian')
            else:
                # replace 'lagna(plag) with lagna
                lagna = utils.resource_strings['ascendant_str']; plag = utils.resource_strings['prasna_lagna_short_str']
                self.data = utils.search_replace(self.data, lagna+'('+plag+')', lagna)
            if len(alt_data)>0:
                action = self.sender()
                action.setData(alt_data)
        elif key in [utils.resource_strings['pushkara_amsa_str']+', '+utils.resource_strings['pushkara_bhaga_str'],
                   utils.resource_strings['yogi_sphuta_str']+', '+utils.resource_strings['avayogi_sphuta_str']+', '+utils.resource_strings['sahayogi_str'],
                   utils.resource_strings['paachakaadi_sambhandha_str'],
                   utils.resource_strings['brahma_str']+','+utils.resource_strings['rudra_str']+','+utils.resource_strings['maheshwara_str'],
                   utils.resource_strings['combustion_str']+' '+utils.resource_strings['planets_str'],
                   utils.resource_strings['graha_yudh_str'],
                   utils.resource_strings['marana_karaka_sthana_str']+' '+utils.resource_strings['planets_str'],
                   utils.resource_strings['mrityu_bhaga_str'],
                   utils.resource_strings['raasi_str']+' '+utils.resource_strings['entry_str'],
                   utils.resource_strings['lattha_star_str'],
                   ]:
            from jhora.ui.options_dialog import InfoDialog
            info_dialog = InfoDialog(title=key,
                                     info_text=self._display_info_dict[key],
                                     button_texts=[utils.resource_strings['accept_str']])
            info_dialog.exec()
        elif key == utils.resource_strings['nava_thaara_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._nava_thaara_dialog is None and self._nava_thaara_widgets is not None:
                self._nava_thaara_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._nava_thaara_widgets,fit_to_widget_contents=True)
            self._nava_thaara_dialog.exec()            
        elif key == utils.resource_strings['special_thaara_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._spl_thaara_dialog is None and self._spl_thaara_widgets is not None:
                self._spl_thaara_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._spl_thaara_widgets,fit_to_widget_contents=True)
            self._spl_thaara_dialog.exec()            
        elif utils.resource_strings['planet_str']+' '+utils.resource_strings['drekkanam_str'].replace(' (D3)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._graha_drekkana_dialog is None and self._graha_drekkana_widgets is not None:
                self._graha_drekkana_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._graha_drekkana_widgets,fit_to_widget_contents=True)
            self._graha_drekkana_dialog.exec()
        elif '22nd '+utils.resource_strings['drekkanam_str'].replace(' (D3)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._ndl_22_dialog is None and self._ndl_22_widgets is not None:
                self._ndl_22_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._ndl_22_widgets,fit_to_widget_contents=True)
            self._ndl_22_dialog.exec()
        elif '64th '+utils.resource_strings['navamsam_str'].replace(' (D9)','') in key:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._ndl_64_dialog is None and self._ndl_64_widgets is not None:
                self._ndl_64_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._ndl_64_widgets,fit_to_widget_contents=True)
            self._ndl_64_dialog.exec()
        elif key==utils.resource_strings['drishti_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = utils.resource_strings['raasi_str']+'-'+utils.resource_strings['graha_str']+'-'+utils.resource_strings['drishti_str']
            if self._drishti_dialog is None and self._drishti_table_widgets is not None:
                self._drishti_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._drishti_table_widgets)
            _fit_table_widgets_to_contents(self._drishti_table_widgets)
            self._drishti_dialog.exec()
        elif key==utils.resource_strings['planet_aspects_relations_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._aspect_dialog is None and self._aspect_widgets is not None:
                self._aspect_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._aspect_widgets,fit_to_widget_contents=True)
            self._aspect_dialog.exec()
        elif key == utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                    utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']:
            from jhora.ui.options_dialog import WidgetDialog
            _title = key
            if self._planet_info_dialog is None and self._planet_info_widgets is not None:
                self._planet_info_dialog = WidgetDialog(title=_title,
                                         h_widgets=self._planet_info_widgets)
            _fit_table_widgets_to_contents(self._planet_info_widgets)
            self._planet_info_dialog.exec()
        elif key==utils.resource_strings['planets_str']:
            try:
                self.data = self._data_original
                self._asc_house = self._asc_house_original
            except:
                pass
        self.setData(data=self.data, arudha_lagna_data=alt_data,
                     chart_title=self._chart_title,chart_title_font_size=self._chart_title_font_size)
        self.update()
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
    def setData(self,data,chart_title='',chart_title_font_size=None,arudha_lagna_data=None,menu_dict=None,
                varga_factor=None,drishti_table_widgets=None,planet_info_widgets=None,aspect_widgets=None,
                ndl_22_widgets=None,ndl_64_widgets=None,graha_drekkana_widgets=None,nava_thaara_widgets=None,
                spl_thaara_widgets=None):
        if menu_dict !=None:
            self._menu_dict = menu_dict
            self._varga_factor = varga_factor
            self._drishti_table_widgets = drishti_table_widgets
            self._aspect_widgets = aspect_widgets
            self._planet_info_widgets = planet_info_widgets
            self._ndl_22_widgets = ndl_22_widgets;self._ndl_64_widgets = ndl_64_widgets
            self._graha_drekkana_widgets = graha_drekkana_widgets
            self._nava_thaara_widgets = nava_thaara_widgets; self._spl_thaara_widgets = spl_thaara_widgets
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.showContextMenu)
        from jhora.ui.options_dialog import WidgetDialog
        _title = utils.resource_strings['nava_thaara_str']
        if self._nava_thaara_dialog is not None and self._nava_thaara_widgets is not None:
            self._nava_thaara_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._nava_thaara_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['special_thaara_str']
        if self._spl_thaara_dialog is not None and self._spl_thaara_widgets is not None:
            self._spl_thaara_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._spl_thaara_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['planet_str']+' '+utils.resource_strings['drekkanam_str'].replace(' (D3)','')
        if self._graha_drekkana_dialog is not None and self._graha_drekkana_widgets is not None:
            self._graha_drekkana_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._graha_drekkana_widgets,fit_to_widget_contents=True)
        _title = '22nd '+utils.resource_strings['drekkanam_str'].replace(' (D3)','')
        if self._ndl_22_dialog is not None and self._ndl_22_widgets is not None:
            self._ndl_22_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._ndl_22_widgets,fit_to_widget_contents=True)
        _title = '64th '+utils.resource_strings['navamsam_str'].replace(' (D9)','')
        if self._ndl_64_dialog is not None and self._ndl_64_widgets is not None:
            self._ndl_64_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._ndl_64_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['raasi_str']+'-'+utils.resource_strings['graha_str']+'-'+utils.resource_strings['drishti_str']
        if self._drishti_dialog is not None and self._drishti_table_widgets is not None:
            self._drishti_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._drishti_table_widgets)
        _title = utils.resource_strings['planet_aspects_relations_str']
        if self._aspect_dialog is not None and self._aspect_widgets is not None:
            self._aspect_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._aspect_widgets,fit_to_widget_contents=True)
        _title = utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']
        if self._planet_info_dialog is not None and self._planet_info_widgets is not None:
            self._planet_info_dialog = WidgetDialog(title=_title,
                                     h_widgets=self._planet_info_widgets)
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        self._chart_title_font_size = NorthIndianChart._north_chart_title_font_size if chart_title_font_size==None else chart_title_font_size
        self._chart_title = chart_title
    def _draw_north_indian_chart(self):#,event):
        painter = QPainter(self)
        chart_width = self.house_width
        chart_height = self.house_height
        cell_width = round(chart_width / self.col_count)
        cell_height = round(chart_height / self.row_count)
        painter.setPen(QPen())
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
        if self._chart_title_font_size  is not None:
            font = QFont()
            font.setPixelSize(self._chart_title_font_size)
            painter.setFont(font)                    
        painter.setPen(QColor(_text_color))
        painter.drawText(title_rect,Qt.AlignmentFlag.AlignCenter,self._chart_title.strip())
        """ reset painter """
        font = QFont(); painter.setPen(QPen())
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
            print(l,pos,label_x,label_y,label_text)
            cell_height = round(chart_height / self.row_count)
            cell_width = round(chart_width / self.col_count)
            cell_rect = QtCore.QRect(label_x,label_y,cell_width,cell_height)
            painter.setPen(QColor(_planet_color))
            painter.drawText(cell_rect,0,label_text.strip())
            zodiac_label_text = _zodiac_symbols[zl]
            zodiac_label_x = round(self.x + zx*chart_width)
            zodiac_label_y = round(self.y + zy*chart_height)
            zodiac_cell_rect = QtCore.QRect(zodiac_label_x,zodiac_label_y,cell_width,cell_height)
            painter.setPen(QColor(_rasi_color))
            painter.drawText(zodiac_cell_rect,0,zodiac_label_text.strip())
            if self.arudha_lagna_data:
                arudha_label_text = self.arudha_lagna_data[l]
                arudha_label_x = round(self.x + ax*chart_width)
                arudha_label_y = round(self.y + ay*chart_height)
                arudha_cell_rect = QtCore.QRect(arudha_label_x,arudha_label_y,cell_width,cell_height)
                painter.setPen(QColor(_arudha_color))
                painter.drawText(arudha_cell_rect,0,arudha_label_text.strip())
            _label_counter += 1
            painter.setPen(QPen())
        painter.end()
def _convert_1d_chart_with_planet_names(chart_1d_list): #To be used for Sudarsana Chakra data as input
    from jhora.horoscope.chart import house
    result = []
    retrograde_planets = chart_1d_list[-1]
    for chart_1d in chart_1d_list[:-1]:
        res = []
        for z,pls in chart_1d:
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
                        ret_str = const._retrogade_symbol
                    pl_str += house.planet_list[int(p)]+ret_str+'/'#const._planet_symbols[int(p)]+'/'
            pl_str = pl_str[:-1]
            res.append((z,pl_str))
        result.append(res)
    return result
if __name__ == "__main__":
    from jhora.panchanga import drik
    from jhora import utils
    utils.set_language('ta'); _resources = utils.resource_strings
    south_data = [['சனி♄\nகேது☋', '', '', ''],['', '', '', ''],['லக்னம்ℒ\nஅருணா⛢\nவருணா♆', '', '', 'செவ்வாய்♂'],['புதன்☿\nகுரு♃\nமாந்தி', 'சூரியன்☉\nகுறுகோள்♇', 'சந்திரன்☾\nசுக்ரன்♀', 'ராகு☊']]
    north_data = ['புதன்☿\nகுரு♃\nமாந்தி', 'லக்னம்ℒ\nஅருணா⛢\nவருணா♆', '', 'சனி♄\nகேது☋', '', '', '', '', 'செவ்வாய்♂', 'ராகு☊', 'சந்திரன்☾\nசுக்ரன்♀', 'சூரியன்☉\nகுறுகோள்♇']
    east_data = [['/', '', 'சனி♄\nகேது☋/'],['', '', 'லக்னம்ℒ\nஅருணா⛢\nவருணா♆'],['செவ்வாய்♂/ராகு☊', 'சந்திரன்☾\nசுக்ரன்♀', 'சூரியன்☉\nகுறுகோள்♇/புதன்☿\nகுரு♃\nமாந்தி']]
    prasna_data = ['', '', '', '', '', '', '', '', '', 'பிர.ல', '', '']
    """
    chart_type = 'south indian'
    print('south data',south_data); print('prasna data',prasna_data)
    south_data,prasna_data = replace_ascendant_with_prasna_lagna(south_data, prasna_data, chart_type)
    print('south data',south_data); print('prasna data',prasna_data)
    """
    """
    chart_type = 'north indian'
    north_data,prasna_data = replace_ascendant_with_prasna_lagna(north_data, prasna_data, chart_type)
    print('north data',north_data); print('prasna data',prasna_data)
    """
    """
    chart_type = 'east indian'
    east_data,prasna_data = replace_ascendant_with_prasna_lagna(east_data, prasna_data, chart_type)
    print('east data',east_data); print('prasna data',prasna_data)
    """
    """
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5) 
    jd = utils.julian_day_number(dob, tob); dcf = 1; arudha_base = 1;
    special_menu_list = [_resources['ascendant_short_str']]+ utils.PLANET_SHORT_NAMES[:const._planets_upto_ketu]
    special_menu_dict = {_resources[r]:[] for r in const._bhava_arudha_list}
    from jhora.horoscope.chart import charts, arudhas
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=dcf)
    for ab,(key,_) in enumerate(special_menu_dict.items()):
        ba = arudhas.bhava_arudhas_from_planet_positions(planet_positions,arudha_base=ab)
        ba_chart = ['' for _ in range(12)]
        astr = special_menu_list[ab]
        for p,r in enumerate(ba):
            ba_chart[r] += _resources['bhava_arudha_a'+str(p+1)+'_short_str']+'\n' if ab==0 else astr+str(p+1)+'\n'
        for b in range(len(ba_chart)):
            if ba_chart[b] != '' and ba_chart[b][-1]=='\n': ba_chart[b] = ba_chart[b][:-1]
        special_menu_dict[key] = ba_chart
    ga = arudhas.graha_arudhas_from_planet_positions(planet_positions)
    ga_chart = ['' for _ in range(12)]
    for p,r in enumerate(ga):
        ga_chart[r] += _resources['ascendant_str']+'\n' if p==0 else utils.PLANET_NAMES[p-1]+'\n'
    for b in range(len(ga_chart)):
        if ga_chart[b] != '' and ga_chart[b][-1]=='\n': ga_chart[b] = ga_chart[b][:-1]
    chart_title = ''
    chart_data_1d = ga_chart
    special_menu_data = special_menu_dict[_resources['ascendant_str']]
    #print('arudha data',arudha_data)
    chart_data_1d = [x[:-1] for x in chart_data_1d] # remove ]n from end of each element
    #print(chart_data_1d)
    _western_data = ['லக்னம் ♑︎மகரம் 22° 26’ 37"','சூரியன்☉ ♏︎விருச்சிகம் 21° 33’ 34"','சந்திரன்☾ ♎︎துலாம் 6° 57’ 33"',
                         'செவ்வாய்♂ ♌︎சிம்மம் 25° 32’ 10"','புதன்☿ ♐︎தனுசு 9° 55’ 36"','குரு♃ ♐︎தனுசு 25° 49’ 14"',
                         'சுக்ரன்♀ ♎︎துலாம் 23° 42’ 24"','சனி♄ ♓︎மீனம் 6° 48’ 25"','ராகு☊ ♍︎கன்னி 10° 33’ 13"',
                         'கேது☋ ♓︎மீனம் 10° 33’ 13"']
    """
    def _index_containing_substring(the_list, substring):
        for i, s in enumerate(the_list):
            if substring in s:
                return i
        return -1
    def _convert_1d_chart_with_planet_names(chart_1d_list): #To be used for Sudarsana Chakra data as input
        from jhora.horoscope.chart import house
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
    def __convert_1d_house_data_to_2d(rasi_1d,chart_type='south indian'):
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
        #print('set data called')
        if 'north' in chart_type.lower():
            chart_data_1d = ["House-1","House-2","House-3","House-4","House-5","House-6","House-7","House-8","House-9","House-10","House-11","House-12"] #north_data[:]
            asc_house = 2
            chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
            Chart.setData(chart_data_north,chart_title=_chart_title,chart_title_font_size=8)#,menu_dict=special_menu_dict)
        elif 'east' in chart_type.lower():
            chart_data_2d = east_data#utils._convert_1d_house_data_to_2d(chart_data_1d,chart_type)
            row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,_resources['ascendant_str'])
            Chart._asc_house = row*Chart.row_count+col
            Chart.setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=10)#,menu_dict=special_menu_dict)
        elif 'west' in chart_type.lower():
            Chart.setData(_western_data,chart_title=_chart_title,chart_title_font_size=8)
            Chart.update()                
        elif 'sudar' in chart_type.lower():
            from jhora.horoscope.dhasa import sudharsana_chakra
            chart_1d = sudharsana_chakra.sudharshana_chakra_chart(jd, place,dob,years_from_dob=0, divisional_chart_factor=dcf)
            #print('chart_1d',chart_1d)
            data_1d = _convert_1d_chart_with_planet_names(chart_1d)
            Chart.setData(data_1d,chart_title=_chart_title,chart_title_font_size=8)
            Chart.update()                
        else: # south indian
            chart_data_2d = south_data#utils._convert_1d_house_data_to_2d(chart_data_1d)
            #print('arudha_data_2d',arudha_data_2d)
            row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,_resources['ascendant_str'])
            Chart._asc_house = (row,col)
            print('chart asc house',Chart._asc_house)
            Chart.setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=12)#,menu_dict=special_menu_dict)
        Chart.update()
#    print(data_1d)
    import sys
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
    _set_chart_data(Chart, chart_type, '')
    Chart.show()
    sys.exit(App.exec())
    