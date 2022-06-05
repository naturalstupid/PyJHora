import re, sys, os
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from _datetime import datetime,timedelta,time,date
import time as time_sleep
import img2pdf
from PIL import Image
import numpy as np
import pandas as pd
from hora import const
from hora import utils
from hora.panchanga import panchanga
from hora.horoscope import main
from hora.horoscope.match import compatibility
from hora.horoscope.chart import ashtakavarga
from hora.horoscope.chart import yoga
from hora.horoscope.chart import house
import math
import requests
import json

sort_tuple = lambda tup,tup_index,reverse=False: sorted(tup,key = lambda x: x[tup_index],reverse=reverse)

_images_path = const._IMAGES_PATH
_IMAGE_ICON_PATH=const._IMAGE_ICON_PATH
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
_world_city_csv_file = const._world_city_csv_file
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
""" UI Constants """
_main_window_width = 650
_main_window_height = 560 #630
_comp_table_font_size = 8
_comp_results_per_list_item = 2
_yoga_text_font_size = 8.5
_yogas_per_list_item = 3
_compatability_list_width = 145
_yoga_list_box_width = 125
_shodhaya_table_font_size = 5.6
_drishti_table_font_size = 6.3
_info_label_font_size = 7.2 # 6.3  if uranus/neptune/pluto included
_main_ui_label_button_font_size = 6
#_main_ui_comp_label_font_size = 7
_info_label1_height = 200
_info_label2_height = _info_label1_height
_row3_widget_width = 75
_chart_info_label_width = 250
_chart_size_factor = 0.31
_east_chart_house_x = 1
_east_chart_house_y = _east_chart_house_x
_east_chart_house_width = 110
_east_chart_house_height = _east_chart_house_width
_south_chart_house_x = 1
_south_chart_house_y = _south_chart_house_x
_south_chart_house_width = 340
_south_chart_house_height = _south_chart_house_width
_north_chart_house_x = 1
_north_chart_house_y = _north_chart_house_x
_north_chart_house_width = 320
_north_chart_house_height = _north_chart_house_width
_north_label_positions = [(4/10,2/10),(1.5/10,0.5/10),(0.1/10,2/10),(1.5/10,4/10), 
                 (0.1/10,7/10), (1.75/10,8.5/10), (3.5/10,7/10), (6.75/10,8.5/10),
                 (8.5/10,7/10),(6.5/10,4/10),(8.35/10,2.0/10),(6.5/10,0.5/10)]
_north_zodiac_label_positions = [(4.75/10,0.25/10),(2.25/10,1.75/10),(0.05/10,0.25/10),(2.25/10,2.75/10), 
                 (0.1/10,5.25/10), (2.25/10,7.75/10), (4.75/10,5.5/10), (7.25/10,7.75/10),
                 (9.5/10,5.5/10),(7.25/10,2.75/10),(9.5/10,0.5/10),(7.25/10,1.75/10)]
_west_chart_radius_1 = 30
_west_chart_radius_2 = 110
_west_chart_radius_3 = 130
_west_chart_radius_4 = 150
_west_radial_increment = 10
_west_chart_center_x = 150
_west_chart_center_y = 150
_west_label_font_size = 8
_footer_label_font_height = 8
_footer_label_height = 26
_lagnam_line_factor = 0.3
_lagnam_line_thickness = 3
_tab_names = ['panchangam_str','raasi_str','hora_str','drekkanam_str','chaturthamsa_str','panchamsa_str',
              'shashthamsa_str','saptamsam_str','ashtamsa_str','navamsam_str','dhasamsam_str','rudramsa_str',
              'dhwadamsam_str','shodamsa_str','vimsamsa_str','chaturvimsamsa_str','nakshatramsa_str','thrisamsam_str',
              'khavedamsa_str','akshavedamsa_str','sashtiamsam_str',
              'dhasa_bhukthi_str','ashtaka_varga_str','drishti_str','argala_str','shodhaya_pinda_str','yoga_str','compatibility_str']
_dhasa_bhukthi_tab_start = 21
_dhasa_bhukthi_tab_count = 3
_dhasa_bhukthi_tab_end = _dhasa_bhukthi_tab_start + _dhasa_bhukthi_tab_count - 1
_ashtaka_varga_tab_start = _dhasa_bhukthi_tab_end + 1
""" 8 BAV/PAV-Raasi for each planet and Asc. One SAV-D1/SAV-D9. 8 BAV/PAV-D9 for each planet"""
_ashtaka_varga_tab_count = len(_tab_names[1:_dhasa_bhukthi_tab_start]) #+1 # +1 for shodhaya tables
_ashtaka_varga_tab_end = _ashtaka_varga_tab_start + _ashtaka_varga_tab_count - 1
_drishti_tab_start = _ashtaka_varga_tab_end + 1
_drishti_tab_count = 1
_drishti_tab_end = _drishti_tab_start + _drishti_tab_count - 1
_argala_tab_start = _drishti_tab_end + 1
_argala_tab_count = 1
_argala_tab_end = _argala_tab_start + _argala_tab_count - 1
_shodhaya_tab_start  = _argala_tab_end + 1
_shodhaya_tab_count = 2 # one for Raasi and another for Navamsam
_shodhaya_dict = {0:'raasi_str',7:'navamsam_str'} #2 and 7 are horoscope chart counters
_shodhaya_tab_end = _shodhaya_tab_start + _shodhaya_tab_count - 1
_yoga_tab_start = _shodhaya_tab_end + 1
_yoga_tab_count = 1
_yoga_tab_end = _yoga_tab_start + _yoga_tab_count - 1
_compatibility_tab_start = _yoga_tab_end + 1 
 
_tab_count = len(_tab_names)

available_chart_types = {'south':"SouthIndianChart",'north':'NorthIndianChart','east':'EastIndianChart','west':'WesternChart'}
available_languages = const.available_languages
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignHCenter
class WesternChart(QWidget):
    """
        Western Chart
        @param data=one-day array of longitudes of planets in houses
        Example: [Sun_Long/Moon_long, '',Mars_long,'', ...'Lagnam_long',...,'']
        
    """
    def __init__(self,data=None,chart_size_factor = 1.0,*args):
        QWidget.__init__(self, *args)
        panchanga._TROPICAL_MODE = True
        panchanga.set_tropical_planets()
        self._chart_title = ''
        self.data = data
        self._asc_longitude = 10.0
        self._asc_house = 0
        if self.data==None:
            self.data = ['லக்னம் ♑︎மகரம் 22° 26’ 37"','சூரியன்☉ ♏︎விருச்சிகம் 21° 33’ 34"','சந்திரன்☾ ♎︎துலாம் 6° 57’ 33"',
                         'செவ்வாய்♂ ♌︎சிம்மம் 25° 32’ 10"','புதன்☿ ♐︎தனுசு 9° 55’ 36"','குரு♃ ♐︎தனுசு 25° 49’ 14"',
                         'சுக்ரன்♀ ♎︎துலாம் 23° 42’ 24"','சனி♄ ♓︎மீனம் 6° 48’ 25"','ராகு☊ ♍︎கன்னி 10° 33’ 13"',
                         'கேது☋ ♓︎மீனம் 10° 33’ 13"']
    def paintEvent(self, event):
        self.event = event
        self._draw_western_chart()#event)
    def _draw_western_chart(self):
        painter = QPainter(self)
        #print('calling western _draw_circle')
        cx = _west_chart_center_x
        cy = _west_chart_center_y
        center = QtCore.QPoint(cx,cy)
        r1 = _west_chart_radius_1
        r2 = _west_chart_radius_2
        r3 = _west_chart_radius_3
        r23 = r3-0.5*(r3-r2)
        r23b = r3-0.75*(r3-r2)
        r4 = _west_chart_radius_4
        r34 = _west_chart_radius_4 -0.5*(_west_chart_radius_4-_west_chart_radius_3) # 0.5*(_west_chart_radius_4+_west_chart_radius_3)
        painter.drawEllipse(center,r1,r1)
        painter.drawEllipse(center,r2,r2)
        painter.drawEllipse(center,r3,r3)
        painter.drawEllipse(center,r4,r4)
        asc_long = self._asc_longitude
        cx = _west_chart_center_x
        cy = _west_chart_center_y
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
        asc_house_start = 165
        for i_z in range(12):
            z_i = (self._asc_house+i_z+12)%12
            zodiac_symbol = _zodiac_symbols[z_i]
            #house_mid_angle = i_z*30+asc_house_start
            house_mid_angle = (i_z*30+self._asc_longitude+155)#*math.pi/180.0
            #print('writing',zodiac_symbol,'z_i',z_i,'angle',house_mid_angle,i_z)
            rect = QtCore.QRect(int(cx+r34*math.cos(house_mid_angle*math.pi/180.0)),int(cy-r34*math.sin(house_mid_angle*math.pi/180.0)),10,10)
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,zodiac_symbol)
        rect = QtCore.QRect(cx-_west_chart_radius_1,cy-_west_chart_radius_1,_west_chart_radius_1*2,2*_west_chart_radius_1)
        if self._chart_title_font_size != None:
            font = QFont()
            font.setPixelSize(self._chart_title_font_size)
            painter.setFont(font)                    
        painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,self._chart_title.split()[0])
        """ reset painter """
        painter.setFont(QFont())                    
    def _write_planets_inside_houses(self,painter,radius,data,i_z):
        tmp_arr = data.strip().split()
        #print(data,tmp_arr)
        planet = tmp_arr[0][-1].strip()
        zodiac = tmp_arr[1][0].strip()
        deg = int(tmp_arr[2][:-1].strip())
        min = int(tmp_arr[3][:-1].strip())
        sec = int(tmp_arr[4][:-1].strip())
        zodiac_index = _zodiac_symbols.index(zodiac)
        if i_z==0:
            planet = 'ℒ'
            self._asc_longitude = deg+min/60.0
            self._asc_house = zodiac_index
        min_new = round(min+sec/60.0)
        #print(planet,deg,min,sec,zodiac,min_new)
        text_new = planet+' '+tmp_arr[2]+' '+zodiac+' '+ str(min_new)+tmp_arr[-3][-1]
        house_index = (zodiac_index - self._asc_house + 12+5) % 12 #+5 to account for 150 degrees for ASC house start
        house_start_angle = house_index*30
        angle = round(house_start_angle+(deg+(min/60.0+sec/3600.0)))
        a = angle*math.pi/180.0#+self._asc_longitude
        #print('data',data,'text_new',text_new,'angle',angle,'angle in rads',a,'zodiac_index',zodiac_index,'house index',house_index)
        cx = _west_chart_center_x
        cy = _west_chart_center_y
        ri = 15 #_west_radial_increment
        #print(text_new)
        for i,c in enumerate(text_new.split()):
            font = QFont()
            font.setPixelSize(_west_label_font_size)
            painter.setFont(font)                    
            rect = QtCore.QRect(int(cx+(radius-(i+1)*ri)*math.cos(a)),int(cy-(radius-(i+1)*ri)*math.sin(a)),20,12)
            painter.drawText(rect,Qt.AlignmentFlag.AlignLeft,c)
            painter.setFont(QFont()) # reset font
               
    def setData(self,data,chart_title='',chart_title_font_size=None):#,event=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        tmp_arr = data[0].strip().split()
        #print(data,tmp_arr)
        planet = tmp_arr[0][-1].strip()
        zodiac = tmp_arr[1][0].strip()
        deg = int(tmp_arr[2][:-1].strip())
        min = int(tmp_arr[3][:-1].strip())
        sec = int(tmp_arr[4][:-1].strip())
        self._asc_longitude = deg+min/60.0+sec/3600.0
        self.update()
        event = self.event
class EastIndianChart(QWidget):
    """
        Draws East Indian Natal Chart and labels the planets
        East Indian chart is 3x3 goes anti-clockwise from top-middle
        @param data: 2-D List of planet names in native language
        NOTE: For East Indian Chart - inner cells of 2-D list should have empty labels
        [ [3/2  1  12/11],
          [ 4   ""  10  ],
          [ 5/6 7  8/9]  
        Example: [ ['Saturn/Moon',     'Neptune',       'Mars'/'Sun'],
                   ['Lagnam',          ''   ,     'Ragu'],
                   ['Ketu/Venus',    'Pluto',  'Mercury/Jupiter']
                ]
    """
    def __init__(self,data=None,chart_size_factor = 1.0,*args):
        QWidget.__init__(self, *args)
        panchanga._TROPICAL_MODE = False
        panchanga.set_sideral_planets()
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
        self.x = _east_chart_house_x
        self.y = _east_chart_house_y
        self.house_width = round(_east_chart_house_width * chart_size_factor)
        self.house_height = round(_east_chart_house_height * chart_size_factor)
        self.data = data
        self._chart_title = ''
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def paintEvent(self, event):
        self.event = event
        self.set_east_indian_chart_data()#event)
    def setData(self,data,chart_title='',chart_title_font_size=None):#,event=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        event = self.event
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
                left_top_cell = (row==0 and col==0) 
                right_bottom_cell = (row==row_count-1 and col==col_count-1)
                right_top_cell = (row==0 and col==col_count-1) 
                left_bottom_cell = (row==row_count-1 and col==0)
                center_cell = row==1 and col==1
                cell = data[row][col]
                zodiac_symbol = self._zodiac_symbols[row][col]
                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)
                rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                painter.drawRect(rect)
                if left_top_cell:
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    # House 3
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_zodiac)
                    # House 2
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_zodiac)
                    # Draw cross line
                    diag_start_x = self.x
                    diag_start_y = self.y
                    diag_end_x = self.x + cell_width
                    diag_end_y = self.y + cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                elif right_top_cell:
                    top_cell_text,bottom_cell_text = cell.split("/") # Fixed in 1.1.0
                    top_zodiac,bottom_zodiac = zodiac_symbol.split("/")
                    # House 11
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,top_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,top_zodiac)
                    # House 12
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,bottom_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,bottom_zodiac)
                    # Draw cross line
                    diag_start_x = self.x + chart_width
                    diag_start_y = self.y
                    diag_end_x = self.x + chart_width - cell_width
                    diag_end_y = self.y + cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                elif right_bottom_cell:
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    # House 8
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_zodiac)
                    # House 9
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_zodiac)
                    # Draw cross line
                    diag_start_x = self.x + chart_width - cell_width
                    diag_start_y = self.y + chart_height - cell_height
                    diag_end_x = self.x + chart_width
                    diag_end_y = self.y + chart_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                elif left_bottom_cell:
                    bottom_cell_text,top_cell_text = cell.split("/")
                    bottom_zodiac,top_zodiac = zodiac_symbol.split("/")
                    # House 5
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,bottom_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,bottom_zodiac)
                    # House 6
                    painter.drawText(rect,Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight,top_cell_text)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,top_zodiac)
                    # Draw cross line
                    diag_start_x = self.x
                    diag_start_y = self.y + chart_height
                    diag_end_x = self.x + cell_width
                    diag_end_y = self.y + chart_height - cell_height
                    painter.drawLine(diag_start_x,diag_start_y,diag_end_x,diag_end_y)
                # write chart title in center of the chart
                elif center_cell and chart_title:
                    #painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,chart_title)
                    if self._chart_title_font_size != None:
                        font = QFont()
                        font.setPixelSize(self._chart_title_font_size)
                        painter.setFont(font)                    
                    painter.drawText(rect,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom,chart_title)
                    """ reset painter """
                    font = QFont()
                    painter.setFont(font)                    
                    rect_image = QtCore.QRect(round(cell_x+cell_width/2),round(cell_y),round(cell_width/2),round(cell_height/2))
                    icon = QPixmap('./images/lord_ganesha2.jpg')
                    painter.drawPixmap(rect_image, icon)
                else:
                    painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,cell)
                    painter.drawText(rect,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight,zodiac_symbol)
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
    """
    def __init__(self,data=None,chart_size_factor = 1.0,*args):
        QWidget.__init__(self, *args)
        panchanga._TROPICAL_MODE = False
        panchanga.set_sideral_planets()
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        self._zodiac_symbols = [ ['\u2653','\u2648','\u2649', '\u264A'],
                   ['\u2652', ''   , ''  , '\u264B'],
                   ['\u2651'  , ''   , ''  , '\u264C'],
                   ['\u2650'      , '\u264F','\u264E','\u264D']]
        self.row_count = 4
        self.col_count = 4
        self._asc_house = (-1,-1)
        self.x = _south_chart_house_x
        self.y = _south_chart_house_y
        self.house_width = round(_south_chart_house_width * chart_size_factor)
        self.house_height = round(_south_chart_house_height * chart_size_factor)
        self.data = data
        self._chart_title = ''
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def paintEvent(self, event):
        self.event = event
        self.set_south_indian_chart_data()#event)
    def setData(self,data,chart_title='',chart_title_font_size=None):#,event=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data
        event = self.event
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
        row_count = len(data)
        col_count = len(data[0])
        chart_width = self.house_width
        chart_height = self.house_height
        cell_width =  round(chart_width/self.col_count)
        cell_height = round(chart_height/self.row_count)
        _label_counter = 0
        for row in range(row_count):
            for col in range(col_count):
                cell_text = data[row][col]
                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)
                cell_rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                if row==0 or row==row_count-1 or col==0 or col==col_count-1:
                    painter.drawRect(cell_rect)
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignCenter,cell_text)
                    # Write zodiac symbol
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop,self._zodiac_symbols[row][col])
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
                    painter.drawText(cell_rect,Qt.AlignmentFlag.AlignCenter,chart_title)
                    """ reset painter """
                    font = QFont()
                    painter.setFont(font)                    
                if row == (row_count/2) and col==(col_count/2) and chart_title:
                    cell_x = round(self.x + col*cell_width)
                    cell_y = round(self.y + (row)*cell_height)
                    cell_rect = QtCore.QRect(cell_x,cell_y,cell_width,cell_height)
                    icon = QPixmap('./images/lord_ganesha2.jpg')
                    painter.drawPixmap(cell_rect, icon)
                _label_counter += 1
class NorthIndianChart(QWidget):
    def __init__(self,data=None,chart_size_factor = 1.0):
        panchanga._TROPICAL_MODE = False
        panchanga.set_sideral_planets()
        QWidget.__init__(self)
        self.row_count = 4
        self.col_count = 4
        self._asc_house = 0
        self.data = data
        self.x = _north_chart_house_x
        self.y = _north_chart_house_y
        self.house_width = round(_north_chart_house_width * chart_size_factor)
        self.house_height = round(_north_chart_house_height * chart_size_factor)
        self.resources=[]
        self._chart_title = ''
        self._grid_labels = []
        self.label_positions = _north_label_positions
        self.zodiac_label_positions = _north_zodiac_label_positions
        if self.data==None:
            self.data = ['','','','','','','','','','','','']
    def paintEvent(self, event):
        self.event = event
        self._draw_north_indian_chart()#event)
    def setData(self,data,chart_title='',chart_title_font_size=None):#,event=None):
        self.data = data
        self._chart_title_font_size = chart_title_font_size
        self._chart_title = chart_title
        event = self.event
    def _draw_north_indian_chart(self):#,event):
        painter = QPainter(self)
        chart_width = self.house_width
        chart_height = self.house_height
        cell_width = round(chart_width / self.col_count)
        cell_height = round(chart_height / self.row_count)
        # first draw a square 
        rect = QtCore.QRect(self.x,self.y,chart_width,chart_height)
        painter.drawRect(rect)
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
        title_x = round(self.x + chart_width/3)
        title_y = self.y + chart_height + self.y
        title_height = 20
        title_width = chart_width
        title_rect = QtCore.QRect(title_x,title_y,title_width,title_height)
        if self._chart_title_font_size != None:
            font = QFont()
            font.setPixelSize(self._chart_title_font_size)
            painter.setFont(font)                    
        painter.drawText(title_rect,0,self._chart_title)
        """ reset painter """
        font = QFont()
        painter.setFont(font)                    
        _label_counter = 0
        for l, pos in enumerate(self.label_positions):
            zl = (l+self._asc_house-1) % 12
            x = pos[0]
            zx = self.zodiac_label_positions[l][0]
            y = pos[1]
            zy = self.zodiac_label_positions[l][1]
            label_text = str(self.data[l])
            label_x = round(self.x + x*chart_width)
            label_y = round(self.y + y*chart_height)
            cell_height = round(chart_height / self.row_count)
            cell_width = round(chart_width / self.col_count)
            cell_rect = QtCore.QRect(label_x,label_y,cell_width,cell_height)
            painter.drawText(cell_rect,0,label_text)
            zodiac_label_text = _zodiac_symbols[zl]
            zodiac_label_x = round(self.x + zx*chart_width)
            zodiac_label_y = round(self.y + zy*chart_height)
            zodiac_cell_rect = QtCore.QRect(zodiac_label_x,zodiac_label_y,cell_width,cell_height)
            #print(self._asc_house,l,zodiac_label_x,zodiac_label_y,zodiac_label_text)
            painter.drawText(zodiac_cell_rect,0,zodiac_label_text)
            _label_counter += 1
        painter.end()
class ChartWindow(QWidget):
    def __init__(self,chart_type='south indian',show_marriage_compatibility=True):
        super().__init__()
        self._chart_type = chart_type
        self._show_compatibility = show_marriage_compatibility
        ' read world cities'
        self._df = pd.read_csv(_world_city_csv_file,header=None)
        self._world_cities_db = np.array(self._df.loc[:].values.tolist())
        self._init_main_window()
        self._v_layout = QVBoxLayout()
        self._create_row1_ui()
        self._create_row_2_and_3_ui()
        if self._show_compatibility:
            self._create_comp_ui()
        self._init_tab_widget_ui()    
    def _init_tab_widget_ui(self):
        self._western_chart = False
        if 'west' in self._chart_type.lower():
            self._western_chart = True
            self.tabNames = _tab_names[:_dhasa_bhukthi_tab_start]
        elif self._show_compatibility:
            self.tabNames = _tab_names
        else:
            self.tabNames = _tab_names[:-1]
        self.tabWidget = QTabWidget()
        self._v_layout.addWidget(self.tabWidget)
        self.tabCount = len(self.tabNames)
        self.horo_tabs = []
        self._charts = []
        self._ashtaka_charts = []
        self._drishti_table1 = []
        self._drishti_table2 = []
        self._argala_table1 = []
        self._argala_table2 = []
        self._shodhaya_table1 = []
        self._shodhaya_table_label1=[]
        self._shodhaya_table2 = []
        self._shodhaya_table_label2=[]
        self._chart_info_labels= []
        self.match_tables = [[ QTableWidget(13,4) for i in range(2)] for j in range(10)]
        self.db_tables =  []
        self._matching_star_list = QListWidget()
        self._yoga_list = QListWidget()
        self._yoga_text = QTextEdit()
        t = 0
        #print('tabs',self.tabNames)
        for tabName in self.tabNames:
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[t],tabName)
            if t==0:
                self._init_panchanga_tab_widgets(t)
                t+=1
            elif t==_dhasa_bhukthi_tab_start:
                self._init_dhasa_bhukthi_tab_widgets(t)
                t += _dhasa_bhukthi_tab_count
            elif t==_ashtaka_varga_tab_start:
                self._init_ashtaka_tab_widgets(t)
                t += _ashtaka_varga_tab_count
            elif t==_drishti_tab_start:
                self._init_drishti_tab_widgets(t)
                t += _drishti_tab_count
            elif t==_argala_tab_start:
                self._init_argala_tab_widgets(t)
                t += _argala_tab_count
            elif t==_shodhaya_tab_start:
                self._init_shodhaya_tab_widgets(t)
                t += _shodhaya_tab_count
            elif t==_yoga_tab_start:
                self._init_yoga_tab_widgets(t)
                t += _yoga_tab_count
            elif self._show_compatibility and t==_compatibility_tab_start:
                self._init_compatibility_tab_widgets(t)
                t += 1
            else:
                self._init_chart_tab_widgets(t)
                t +=1
        self.tabCount = self.tabWidget.count()
        self._add_footer_to_chart()
        self.setLayout(self._v_layout)        
    def _init_yoga_tab_widgets(self, tab_index):
        h_layout = QHBoxLayout()
        self._yoga_list =QListWidget()
        self._yoga_list.currentRowChanged.connect(self._update_yoga_table)
        self._yoga_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._yoga_list.setMaximumWidth(_yoga_list_box_width)
        h_layout.addWidget(self._yoga_list)
        self._yoga_text = QTextEdit()
        self._yoga_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._yoga_text.setStyleSheet('font-size:'+str(_yoga_text_font_size)+'pt')
        h_layout.addWidget(self._yoga_text)
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_compatibility_tab_widgets(self,tab_index):
        h_layout = QHBoxLayout()
        self._matching_star_list = QListWidget()
        self._matching_star_list.currentRowChanged.connect(self._update_compatibility_table)
        self._matching_star_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._matching_star_list.setMaximumWidth(_compatability_list_width)
        h_layout.addWidget(self._matching_star_list)
        self._comp_results_table = []
        for c in range(_comp_results_per_list_item):
            self._comp_results_table.append(QTableWidget(13,4))
            self._comp_results_table[c].setStyleSheet('font-size:'+str(_comp_table_font_size)+'pt')
            self._comp_results_table[c].verticalHeader().hide()
            self._comp_results_table[c].setHorizontalHeaderItem(0,QTableWidgetItem('Porutham/Koota'))
            self._comp_results_table[c].setHorizontalHeaderItem(1,QTableWidgetItem('Score'))
            self._comp_results_table[c].setHorizontalHeaderItem(2,QTableWidgetItem('Max Score'))
            self._comp_results_table[c].setHorizontalHeaderItem(3,QTableWidgetItem('%'))
            self._comp_results_table[c].setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._comp_results_table[c].setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            h_layout.addWidget(self._comp_results_table[c])
        self._matching_star_list.setMaximumHeight(self._comp_results_table[0].height())
        self.horo_tabs[_compatibility_tab_start].setLayout(h_layout)     
    def _init_dhasa_bhukthi_tab_widgets(self,tab_index):
        """ Add more tabs for dhasa-bhukthi """
        for t in range(1,_dhasa_bhukthi_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        #self.horo_tabs.append(QWidget())
        #self.tabWidget.addTab(self.horo_tabs[tab_index+2],'')
        self.tabCount += _dhasa_bhukthi_tab_count-1
        self.db_tables = [[ QTableWidget(10,2) for i in range(_dhasa_bhukthi_tab_count)] for j in range(3)] 
        for db_tab in range(_dhasa_bhukthi_tab_count):
            grid_layout = QGridLayout()
            for col in range(3):
                self.db_tables[db_tab][col].horizontalHeader().hide()
                self.db_tables[db_tab][col].verticalHeader().hide()
                self.db_tables[db_tab][col].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.db_tables[db_tab][col].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                grid_layout.addWidget(self.db_tables[db_tab][col],1,col)
            self.horo_tabs[_dhasa_bhukthi_tab_start+db_tab].setLayout(grid_layout)
            self.tabWidget.setTabText(_dhasa_bhukthi_tab_start+db_tab,'dhasa_bhukthi_str-'+str(db_tab+1))
    def _init_panchanga_tab_widgets(self,tab_index):
        h_layout = QHBoxLayout()
        self._info_label1 = QLabel("Information:")
        self._info_label1.setStyleSheet("border: 1px solid black;")
        #self._info_label1.setFixedHeight(_info_label1_height)
        h_layout.addWidget(self._info_label1)
        self._info_label2 = QLabel("Information:")
        self._info_label2.setStyleSheet("border: 1px solid black;")
        #self._info_label2.setFixedHeight(_info_label2_height)
        h_layout.addWidget(self._info_label2)
        #self._v_layout.addLayout(h_layout)
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_chart_tab_widgets(self,tab_index):
        h_layout = QHBoxLayout()
#        print('created chart of type ',self._chart_type)
        self._charts.append(eval(available_chart_types[self._chart_type])())
        h_layout.addWidget(self._charts[tab_index-1])
        self._chart_info_labels.append(QLabel('Chart Information'))
        h_layout.addWidget(self._chart_info_labels[tab_index-1])
        self._chart_info_labels[tab_index-1].setStyleSheet('font-size:'+str(_info_label_font_size)+'pt')
        h_layout.setSpacing(0)
        #self._add_footer_to_chart()
        self._charts[tab_index-1].update()
        #self._chart2.update()
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_drishti_tab_widgets(self,tab_index):
        # create extra tabs depending on the count
        for t in range(1,_drishti_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._drishti_table1 = [ QTableWidget(7,3) for i in range(_drishti_tab_count)] 
        self._drishti_table2 = [ QTableWidget(9,3) for i in range(_drishti_tab_count)] 
        for t in range(_drishti_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._drishti_table1[t])
            self._drishti_table1[t].setItemDelegate(delegate)
            delegate = AlignDelegate(self._drishti_table2[t])
            self._drishti_table2[t].setItemDelegate(delegate)
            h_layout.addWidget(self._drishti_table1[t])
            h_layout.addWidget(self._drishti_table2[t])
            self._drishti_table2[t].setStyleSheet('font-size:'+str(_drishti_table_font_size)+'pt')
            for table in [self._drishti_table1[t], self._drishti_table2[t]]:
                #table.setStyleSheet('font-size:'+str(_drishti_table_font_size)+'pt')
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
                #table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(''))
                table.update()
            self.horo_tabs[tab_index+t].setLayout(h_layout)            
    def _init_argala_tab_widgets(self,tab_index):
        # create extra tabs depending on the count
        for t in range(1,_argala_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._argala_table1 = [ QTableWidget(12,4) for i in range(_argala_tab_count)] 
        self._argala_table2 = [ QTableWidget(12,4) for i in range(_argala_tab_count)] 
        for t in range(_argala_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._argala_table1[t])
            self._argala_table1[t].setItemDelegate(delegate)
            delegate = AlignDelegate(self._argala_table2[t])
            self._argala_table2[t].setItemDelegate(delegate)
            h_layout.addWidget(self._argala_table1[t])
            h_layout.addWidget(self._argala_table2[t])
            for table in [self._argala_table1[t], self._argala_table2[t]]:
                table.setStyleSheet('font-size:'+str(_drishti_table_font_size)+'pt')
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
                table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(''))
                table.update()
            self.horo_tabs[tab_index+t].setLayout(h_layout)            
    def _init_shodhaya_tab_widgets(self,tab_index):
        # create extra tabs depending on the count
        for t in range(1,_shodhaya_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._shodhaya_table1 = [ QTableWidget(9,12) for i in range(_shodhaya_tab_count)] 
        self._shodhaya_table_label1 = [ QLabel() for i in range(_shodhaya_tab_count)] 
        self._shodhaya_table2 = [ QTableWidget(3,7) for i in range(_shodhaya_tab_count)] 
        self._shodhaya_table_label2 = [ QLabel() for i in range(_shodhaya_tab_count)] 
        """ create tables in shodhaya tab """
        for t in range(_shodhaya_tab_count):
            v_layout = QVBoxLayout()
            self._shodhaya_table_label1[t].setText('Ashtaka Varga (After reduction)')
            delegate = AlignDelegate(self._shodhaya_table1[t])
            self._shodhaya_table1[t].setItemDelegate(delegate)
            self._shodhaya_table_label2[t].setText('Ashtaka Varga (Shodhaya Pinda)')
            delegate = AlignDelegate(self._shodhaya_table2[t])
            self._shodhaya_table2[t].setItemDelegate(delegate)
            v_layout.addWidget(self._shodhaya_table_label1[t])
            v_layout.addWidget(self._shodhaya_table1[t])
            v_layout.addWidget(self._shodhaya_table_label2[t])
            v_layout.addWidget(self._shodhaya_table2[t])
            for table in [self._shodhaya_table1[t], self._shodhaya_table2[t]]:
                table.setStyleSheet('font-size:'+str(_shodhaya_table_font_size)+'pt')
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
                table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                #table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(str(0)))
                    
            self.horo_tabs[tab_index+t].setLayout(v_layout)            
    def _init_ashtaka_tab_widgets(self, tab_index):
        # create extra tabs depending on the count
        for t in range(1,_ashtaka_varga_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        #print('_init_ashtaka_tab_widgets',tab_index)
        """ create 9x9 chart grid. 1st one SAV and others are 8 planet BAV """
        for t in range(_ashtaka_varga_tab_count):
            self._ashtaka_grid_layout = QGridLayout()
            self._ashtaka_charts.append([(eval(available_chart_types[self._chart_type])(chart_size_factor=_chart_size_factor)) for i in range(9)])
            ac = 0
            for i in range(3):
                for j in range(3):
                    self._ashtaka_grid_layout.addWidget(self._ashtaka_charts[t][ac],i,j)
                    ac+=1
            self._ashtaka_grid_layout.setSpacing(0)
            self.horo_tabs[tab_index+t].setLayout(self._ashtaka_grid_layout)        
    def _init_main_window(self):
        fp = open(_INPUT_DATA_FILE, encoding='utf-8', mode='r')
        window_title = fp.readline().split('=',1)[1]
        self._footer_title = fp.readline().split('=',1)[1]
        self._image_icon_path = fp.readline().split('=',1)[1]
        fp.close()
        self.setWindowIcon(QtGui.QIcon(_IMAGE_ICON_PATH))
        self._language = list(available_languages.keys())[0]
        #self._chart_type = 'south'
        ci = _index_containing_substring(available_chart_types.keys(),chart_type.lower())
        if ci >=0:
            self._chart_type = list(available_chart_types.keys())[ci]
        self.setFixedSize(_main_window_width,_main_window_height)        
    def _create_row1_ui(self):
        self._row1_h_layout = QHBoxLayout()
        self._name_label = QLabel("Name:")
        self._row1_h_layout.addWidget(self._name_label)
        self._name_text = QLineEdit("")
        self._name = self._name_text.text()
        self._name_text.setToolTip('Enter your name')
        self._row1_h_layout.addWidget(self._name_text)
        self._gender_combo = QComboBox()
        self._gender_combo.addItems(['Male','Female'])
        self._row1_h_layout.addWidget(self._gender_combo)
        self._place_label = QLabel("Place:")
        self._row1_h_layout.addWidget(self._place_label)
        self._place_name = '' # 'Chennai, IN'
        self._place_text = QLineEdit(self._place_name)#"Chennai, IN")
        self._world_cities_list = self._df[1].tolist()
        completer = QCompleter(self._world_cities_list)#self._world_cities_db[:,1])
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
        self._place_text.editingFinished.connect(lambda : self._get_place_latitude_longitude(self._place_text.text()))
        self._place_text.setToolTip('Enter place of birth, country name')
        self._row1_h_layout.addWidget(self._place_text)
        self._lat_label = QLabel("Latidude:")
        self._row1_h_layout.addWidget(self._lat_label)
        self._lat_text = QLineEdit('')
        self._latitude = 0.0
        self._lat_text.setToolTip('Enter Latitude preferably exact at place of birth: Format: +/- xx.xxx')
        self._row1_h_layout.addWidget(self._lat_text)
        self._long_label = QLabel("Longitude:")
        self._row1_h_layout.addWidget(self._long_label)
        self._long_text = QLineEdit('')#'xx.xxxx')#"80.2619")
        self._longitude = 0.0
        self._long_text.setToolTip('Enter Longitude preferably exact at place of birth. Format +/- xx.xxx')
        self._row1_h_layout.addWidget(self._long_text)
        self._tz_label = QLabel("Time Zone:")
        self._row1_h_layout.addWidget(self._tz_label)
        self._tz_text = QLineEdit('')#'x.x')#"+5.5")
        self._time_zone = 0.0
        self._tz_text.setToolTip('Enter Time offset from GMT e.g. -5.5 or 4.5')
        self._row1_h_layout.addWidget(self._tz_text)
        self._v_layout.addLayout(self._row1_h_layout)
    def _create_row_2_and_3_ui(self):
        v_layout = QVBoxLayout()
        self._row2_h_layout = QHBoxLayout()
        self._dob_label = QLabel("Date of Birth:")
        self._row2_h_layout.addWidget(self._dob_label)
        self._date_of_birth = ''# '1996,12,7'
        self._dob_text = QLineEdit(self._date_of_birth)#'yyyy,mm,dd')#"1996,12,7")
        self._dob_text.setToolTip('Date of birth in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        self._dob_label.setMaximumWidth(_row3_widget_width)
        self._dob_text.setMaximumWidth(_row3_widget_width)
        self._row2_h_layout.addWidget(self._dob_text)
        self._tob_label = QLabel("Time of Birth:")
        self._row2_h_layout.addWidget(self._tob_label)
        self._time_of_birth = '' # '10:34:00'
        self._tob_text = QLineEdit(self._time_of_birth)#'hh:mm:ss')#"10:34:00")
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        self._tob_label.setMaximumWidth(_row3_widget_width)
        self._tob_text.setMaximumWidth(_row3_widget_width)
        self._row2_h_layout.addWidget(self._tob_text)
        self._chart_type_combo = QComboBox()
        self._chart_type_combo.addItems(available_chart_types.keys())
        self._chart_type_combo.setToolTip('Choose birth chart style north, south or east indian')
        self._chart_type_combo.setCurrentText(self._chart_type)
        self._chart_type_combo.setMaximumWidth(_row3_widget_width)
        self._row2_h_layout.addWidget(self._chart_type_combo)
        available_ayanamsa_modes = list(const.available_ayanamsa_modes.keys())#[:-1]
        self._ayanamsa_combo = QComboBox()
        self._ayanamsa_combo.addItems(available_ayanamsa_modes)
        self._ayanamsa_combo.setToolTip('Choose Ayanamsa mode from the list')
        self._ayanamsa_mode = "LAHIRI"
        self._ayanamsa_value = None
        self._ayanamsa_combo.setCurrentText(self._ayanamsa_mode)
        self._row2_h_layout.addWidget(self._ayanamsa_combo)
        v_layout.addLayout(self._row2_h_layout)
        self._row3_h_layout = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.currentIndexChanged.connect(self._update_main_window_label_and_tooltips)
        self._row3_h_layout.addWidget(self._lang_combo)
        self._compute_button = QPushButton("Show Chart")
        self._compute_button.setFont(QtGui.QFont("Arial Bold",9))
        self._compute_button.clicked.connect(self.compute_horoscope)
        self._compute_button.setToolTip('Click to update the chart information based on selections made')
        self._row3_h_layout.addWidget(self._compute_button)
        self._save_image_button = QPushButton("Save as PDF")
        self._save_image_button.setFont(QtGui.QFont("Arial Bold",8))
        self._save_image_button.clicked.connect(lambda : self.save_as_pdf(pdf_file_name=None))
        self._save_image_button.setToolTip('Click to save horoscope as a PDF')
        self._row3_h_layout.addWidget(self._save_image_button)
        self._save_city_button = QPushButton("Save City")
        self._save_city_button.clicked.connect(self._save_city_to_database)
        self._save_city_button.setToolTip('Click to save the city information in csv database')
        self._row3_h_layout.addWidget(self._save_city_button)
        v_layout.addLayout(self._row3_h_layout)
        self._v_layout.addLayout(v_layout)
    def _create_comp_ui(self):
        self._comp_h_layout = QHBoxLayout()
        self._mahendra_porutham_checkbox = QCheckBox()
        self._mahendra_porutham_checkbox.setChecked(True)
        self._mahendra_porutham = self._mahendra_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._mahendra_porutham_checkbox)
        self._vedha_porutham_checkbox = QCheckBox()
        self._vedha_porutham_checkbox.setChecked(True)
        self._vedha_porutham = self._vedha_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._vedha_porutham_checkbox)
        self._rajju_porutham_checkbox = QCheckBox()
        self._rajju_porutham_checkbox.setChecked(True)
        self._rajju_porutham = self._rajju_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._rajju_porutham_checkbox)
        self._sthree_dheerga_porutham_checkbox = QCheckBox()
        self._sthree_dheerga_porutham_checkbox.setChecked(True)
        self._sthree_dheerga_porutham = self._sthree_dheerga_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._sthree_dheerga_porutham_checkbox)
        self._min_score_label = QLabel('')
        self._comp_h_layout.addWidget(self._min_score_label)
        self._min_score_combo = QDoubleSpinBox()
        self._min_score_combo.setRange(0.0,36.0)
        self._min_score_combo.setSingleStep(0.5)
        self._min_score_combo.setValue(18.0)
        self._comp_h_layout.addWidget(self._min_score_combo)
        self._v_layout.addLayout(self._comp_h_layout)
    def _add_footer_to_chart(self):
        self._footer_label = QLabel('')
        self._footer_label.setTextFormat(Qt.TextFormat.RichText)
        self._footer_label.setText(self._footer_title)#"Copyright © Dr. Sundar Sundaresan, Open Astro Technologies, USA.")
        self._footer_label.setStyleSheet("border: 1px solid black;")
        self._footer_label.setFont(QtGui.QFont("Arial Bold",_footer_label_font_height))
        self._footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer_label.setFixedHeight(_footer_label_height)
        self._footer_label.setFixedWidth(self.width())
        self._footer_label.setWordWrap(True)
        self._footer_label.setOpenExternalLinks(True)
        self._v_layout.addWidget(self._footer_label)
    def _on_application_exit(self):
        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)
        sys.excepthook = except_hook
        QApplication.quit()
    def ayanamsa_mode(self, ayanamsa_mode, ayanamsa=None):
        """
            Set Ayanamsa mode
            @param ayanamsa_mode - Default - Lahiri
            See 'panchanga.available_ayanamsa_modes' for the list of available models
        """
        self._ayanamsa_mode = ayanamsa_mode
        self._ayanamsa_value = ayanamsa
        self._ayanamsa_combo.setCurrentText(ayanamsa_mode)
    def place(self,place_name):
        """
            Set the place of birth
            @param - place_name - Specify with country code. e.g. Chennai, IN
            NOTE: Uses Nominatim to get the latitude and longitude
            An error message displayed if lat/long could not be found in which case enter lat/long manually.
            Also NOTE: calling latitude() or longitude() will replace the lat/long values added already
        """
        self._place_name = place_name
        self._place_text.setText(place_name)
        result = self._get_place_latitude_longitude(place_name)
        if result == None:
            return
        [self._place_name,self._latitude,self._longitude,self._time_zone] = result
    def name(self,name):
        """
            Set name of the person whose horoscope is sought
            @param - Name of person
        """
        self._name = name
        self._name_text.setText(name)
    def gender(self,gender):
        """
            set gender of the person whose horoscope is sought
            @param gender: gender of the person
        """
        if gender.lower()=='male' or gender.lower()=='female':
            self._gender = gender
            self._gender_combo.setCurrentText(gender)
    def chart_type(self,chart_type):
        """
            Set chart type of the horoscope
            @param - chart_type:
                options: 'south indian'. 'north indian'
                Default: south indian
        """
        ci = _index_containing_substring(available_chart_types.keys(),chart_type.lower())
        if ci >=0:
            self._chart_type = list(available_chart_types.keys())[ci]
            self._chart_type_combo.setCurrentText(chart_type.lower())
    def latitude(self,latitude):
        """
            Sets the latitude manually
            @param - latitude
        """
        self._latitude = float(latitude)
        self._lat_text.setText(latitude)
    def longitude(self,longitude):
        """
            Sets the longitude manually
            @param - longitude
        """
        self._longitude = float(longitude)
        self._long_text.setText(longitude)
    def time_zone(self,time_zone):
        """
            Sets the time zone offset manually
            @param - time_zone - time zone offset
        """
        self._time_zone = float(time_zone)
        self._tz_text.setText(time_zone)
    def date_of_birth(self, date_of_birth):
        """
            Sets the date of birth (Format:YYYY,MM,DD)
            @param - date_of_birth
        """
        self._date_of_birth = date_of_birth
        self._dob_text.setText(self._date_of_birth)
    def time_of_birth(self, time_of_birth):
        """
            Sets the time of birth (Format:HH:MM:SS)
            @param - time_of_birth
        """
        self._time_of_birth = time_of_birth
        self._tob_text.setText(self._time_of_birth)
    def language(self,language):
        """
            Sets the language for display
            @param - language
        """
        if language in available_languages:
            self._language = language
            self._lang_combo.setCurrentText(language)
    def mahendra_porutham(self, bool_value:bool=True):
        """
            Set whether mahendra porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._mahendra_porutham = bool_value
            self._mahendra_porutham_checkbox.setChecked(bool_value)
    def vedha_porutham(self, bool_value:bool=True):
        """
            Set whether vedha porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._vedha_porutham = bool_value
            self._vedha_porutham_checkbox.setChecked(bool_value)
    def rajju_porutham(self, bool_value:bool=True):
        """
            Set whether rajju porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._rajju_porutham = bool_value
            self._rajju_porutham_checkbox.setChecked(bool_value)
    def sthree_dheerga_porutham(self, bool_value:bool=True):
        """
            Set whether sthree dheerga porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._sthree_dheerga_porutham = bool_value
            self._sthree_dheerga_porutham_checkbox.setChecked(bool_value)
    def minimum_compatibility_score(self,minm_comp_score:float=18.0):
        """
            Set minimum score required for marriage compatibility
            @param minm_comp_score: float in range(0.0,35.0,0.5) 
        """
        if self._show_compatibility and  minm_comp_score>0.0 and minm_comp_score < 36.5:
            self._minimum_score = minm_comp_score
            self._min_score_combo.setValue(minm_comp_score)
    def _validate_ui(self):
        all_data_ok = False
        all_data_ok = self._place_text.text().strip() != '' and \
                         self._name_text.text().strip() != '' and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._lat_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._long_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d{1,4}\,\d{1,2}\,\d{1,2}", self._dob_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"\d{1,2}:\d{1,2}:\d{1,2}", self._tob_text.text().strip(),re.IGNORECASE)
        return all_data_ok
    def _update_main_window_label_and_tooltips(self):
        try:
            if self.resources:
                msgs = self.resources
                self._name_label.setText(msgs['name_str'])
                self._name_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._name_label.setToolTip(msgs['name_tooltip_str'])
                self._place_label.setText(msgs['place_str'])
                self._place_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._place_label.setToolTip(msgs['place_tooltip_str'])
                self._lat_label.setText(msgs['latitude_str'])
                self._lat_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._lat_label.setToolTip(msgs['latitude_tooltip_str'])
                self._long_label.setText(msgs['longitude_str'])
                self._long_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._long_label.setToolTip(msgs['longitude_tooltip_str'])
                self._tz_label.setText(msgs['timezone_offset_str'])
                self._tz_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._tz_label.setToolTip(msgs['timezone_tooltip_str'])
                self._dob_label.setText(msgs['date_of_birth_str'])
                self._dob_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._dob_label.setToolTip(msgs['dob_tooltip_str'])
                self._tob_label.setText(msgs['time_of_birth_str'])
                self._tob_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._tob_label.setToolTip(msgs['tob_tooltip_str'])
                self._ayanamsa_combo.setToolTip(msgs['ayanamsa_tooltip_str'])
                self._lang_combo.setToolTip(msgs['language_tooltip_str'])
                self._compute_button.setText(msgs['show_chart_str'])
                self._compute_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._compute_button.setToolTip(msgs['compute_tooltip_str'])
                self._save_image_button.setText(msgs['save_pdf_str'])
                self._save_image_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._save_image_button.setToolTip(msgs['savepdf_tooltip_str'])
                self._save_city_button.setText(msgs['save_city_str'])
                self._save_city_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._save_city_button.setToolTip(msgs['savecity_tooltip_str'])
                self._mahendra_porutham_checkbox.setText(msgs['mahendra_str'])#.split()[0])
                self._mahendra_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._mahendra_porutham_checkbox.setToolTip(msgs['mahendra_tooltip_str'])
                self._vedha_porutham_checkbox.setText(msgs['vedha_str'])#.split()[0])
                self._vedha_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._vedha_porutham_checkbox.setToolTip(msgs['vedha_tooltip_str'])
                self._rajju_porutham_checkbox.setText(msgs['rajju_str'])#.split()[0])
                self._rajju_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._rajju_porutham_checkbox.setToolTip(msgs['rajju_tooltip_str'])
                self._sthree_dheerga_porutham_checkbox.setText(msgs['sthree_dheerga_str'])#.split()[0])
                self._sthree_dheerga_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._sthree_dheerga_porutham_checkbox.setToolTip(msgs['sthree_dheerga_tooltip_str'])
                self._min_score_label.setText(msgs['min_score_label_str'])
                self._min_score_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._min_score_label.setToolTip(msgs['min_score_tooltip_str'])
                self.update()
        except:
            pass
    def compute_horoscope(self):
        """
            Compute the horoscope based on details entered
            if details missing - error is displayed            
        """
        if not self._validate_ui():
            print('values are not filled properly')
            return
        self._gender = self._gender_combo.currentText()
        self._place_name = self._place_text.text()
        self._latitude = float(self._lat_text.text())
        self._longitude = float(self._long_text.text())
        self._time_zone = float(self._tz_text.text())
        self._language = self._lang_combo.currentText()
        self._date_of_birth = self._dob_text.text()
        self._time_of_birth = self._tob_text.text()
        if self._place_name.strip() == "":
            print("Please enter a place of birth")
            return
        horoscope_language = available_languages[self._language]
        self._ayanamsa_mode =  self._ayanamsa_combo.currentText()
        as_string = True
        if self._place_name.strip() == '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0: 
            [self._place_name,self._latitude,self._longitude,self._time_zone] = utils.get_latitude_longitude_from_place_name(place_name)
            self._lat_text.setText((self._latitude))
            self._long_text.setText((self._longitude))
            self._tz_text.setText((self._time_zone))
        year,month,day = self._date_of_birth.split(",")
        birth_date = panchanga.Date(int(year),int(month),int(day))
        self._chart_type = self._chart_type_combo.currentText()
        ' set the chart type and reset widgets'
        self._recreate_chart_tab_widgets()
        if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
            self._horo= main.Horoscope(latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value)
        else:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value)
        self._calendar_info = self._horo.get_calendar_information(language=available_languages[self._language])
        self.resources= self._horo._get_calendar_resource_strings(language=available_languages[self._language])
        self._horoscope_info, self._horoscope_charts, self._dhasa_bhukti_info = [],[],[]
        self._horoscope_info, self._horoscope_charts,self._dhasa_bhukti_info = self._horo.get_horoscope_information(language=available_languages[self._language])
        self._update_main_window_label_and_tooltips()
        self._update_chart_ui_with_info()
        self.resize(self.minimumSizeHint())
        self.tabWidget.setFocus()
    def _recreate_chart_tab_widgets(self):
        self._v_layout.removeWidget(self.tabWidget)
        current_tab = self.tabWidget.currentIndex()
        self.tabWidget.deleteLater()
        self._footer_label.deleteLater()
        self.tabWidget = None
        self._init_tab_widget_ui()
        self.tabWidget.setCurrentIndex(current_tab)
    def _fill_information_label1(self,info_str,format_str):
        key = 'sunrise_str'
        sunrise_time = self._calendar_info[self.resources[key]]
        info_str += format_str % (self.resources[key],sunrise_time)
        key = 'sunset_str'
        info_str += format_str % (self.resources[key],self._calendar_info[self.resources[key]])
        key = 'nakshatra_str'
        info_str += format_str % (self.resources[key],self._calendar_info[self.resources[key]])
        key = 'raasi_str'
        info_str += format_str % (self.resources[key],self._calendar_info[self.resources[key]])
        key = 'tithi_str'
        info_str += format_str % (self.resources[key],self._calendar_info[self.resources[key]])
        key = 'yogam_str'
        info_str += format_str % (self.resources[key],self._calendar_info[self.resources[key]])
        key = 'karanam_str'
        info_str += format_str % (self.resources[key],self._calendar_info[self.resources[key]])
        jd = self._horo.julian_day
        place = panchanga.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        bt=self._horo.birth_time
        tob = bt[0]+bt[1]/60.0+bt[2]/3600.0
        key = self.resources['bhava_lagna_str']
        value = panchanga.bhava_lagna(jd,place,tob,1)
        info_str += format_str %(key,value)
        key = self.resources['hora_lagna_str']
        value = panchanga.hora_lagna(jd,place,tob,1)
        info_str += format_str %(key,value)
        key = self.resources['ghati_lagna_str']
        value = panchanga.ghati_lagna(jd,place,tob,1)
        info_str += format_str %(key,value)
        key = self.resources['sree_lagna_str']
        value = panchanga.sree_lagna(jd,place,1)
        info_str += format_str %(key,value)
        key = self.resources['raasi_str']+'-'+self.resources['ascendant_str']
        value = self._horoscope_info[key]#.split()[:1]
        info_str += format_str % (self.resources['ascendant_str'],value)
        birth_time = self._time_of_birth
        info_str += format_str % (self.resources['udhayathi_str'], _udhayadhi_nazhikai(birth_time,sunrise_time))
        key = self.resources['raahu_kaalam_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['kuligai_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['yamagandam_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['dhurmuhurtham_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['abhijit_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['moonrise_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['moonset_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)        
        self._info_label1.setText(info_str)
    def _fill_information_label2(self,info_str,format_str):
        info_str = ''
        dhasa = list(self._dhasa_bhukti_info.keys())[8].split('-')[0]
        deb = list(self._dhasa_bhukti_info.values())[8]
        dob = self._dob_text.text().replace(',','-')
        years,months,days = _dhasa_balance(dob, deb)
        value = str(years)+':'+ str(months)+':'+ str(days)
        key = dhasa + ' '+self.resources['balance_str']
        info_str += format_str % (key,value)
        dhasa = ''
        dhasa_end_date = ''
        di = 9
        for p,(k,v) in enumerate(self._dhasa_bhukti_info.items()):
            # get dhasa
            if (p+1) == di:
                dhasa = k.split("-")[0]#+ ' '+self.resources['ends_at_str']
            # Get dhasa end date
            elif (p+1) == di+1:
                """ to account for BC Dates negative sign is introduced"""
                if len(v.split('-')) == 4:
                    _,year,month,day = v.split('-')
                    year = '-'+year
                else:
                    year,month,day = v.split('-')
                dhasa_end_date = year+'-'+month+'-'+str(int(day)-1)+ ' '+self.resources['ends_at_str']
                info_str += format_str % (dhasa, dhasa_end_date)
                di += 9
        key = self.resources['maasa_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['ayanamsam_str']+' ('+self._ayanamsa_mode+') '
        value = panchanga.get_ayanamsa_value(self._horo.julian_day)
        self._ayanamsa_value = value
        value = utils.to_dms(value,as_string=True,is_lat_long='lat').replace('N','').replace('S','')
        print("horo_chart: Ayanamsa mode",key,'set to value',value)
        info_str += format_str % (key,value)
        key = self.resources['samvatsara_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['kali_year_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['vikrama_year_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['saka_year_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['vaaram_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        self._info_label2.setText(info_str)
    def _update_tabs_with_divisional_charts(self,jd,place):
        i_end = 0
        division_chart_factors = const.division_chart_factors
        bt=self._horo.birth_time
        tob = bt[0]+bt[1]/60.0+bt[2]/3600.0
        format_str = '%-18s%-20s\n'
        tab_name = self.resources[self.tabNames[0]]
        self.tabWidget.setTabText(0,tab_name)
        chara_karaka_names = [x+'_str' for x in house.chara_karaka_names]
        chara_karaka_dict = house.chara_karakas(jd,place)
        planet_count = len(panchanga.planet_list) + 1 # Inlcuding :agnam
        upagraha_count = len(const._solar_upagraha_list) + len(const._other_upagraha_list)# + 1 # +1 for upajethu title row
        special_lagna_count = len(const._special_lagna_list)
        total_row_count = planet_count + upagraha_count + special_lagna_count
        print('planet_count',planet_count,'upagraha_count',upagraha_count,'special_lagna_count',special_lagna_count,'total_row_count',total_row_count)
        for t,tab in enumerate(self.tabNames[1:_dhasa_bhukthi_tab_start]):
            """ update the chart from horoscope charts """
            tab_name = self.resources[tab]
            self.tabWidget.setTabText(t+1,tab_name)
            #divisional_chart_factor = division_chart_factors[t]
            i_start = i_end # (t-1)*10
            i_end = i_start + total_row_count# 26 #29 # 4 for special lagnas, 10 from lagnam and planets, 12 rows for upagraha details
            chart_info = ''
            western_data = []
            if self._western_chart:
                i_start = i_start + special_lagna_count #4 # Skip special lagna rows
                i_end = i_start + planet_count #10 # 13 # count of planets + lagnam
            i_i = -1
            #print('western_chart',self._western_chart,i_start,i_end)
            for (k,v) in list(self._horoscope_info.items())[i_start:i_end]:
                i_i += 1
                k1 = k.split('-')[-1]
                v1 = v.split('-')[0]
                if i_i >=5 and i_i <=12 and not self._western_chart:
                    p_i = i_i-5
                    v1 += ' (' + self.resources[chara_karaka_names[chara_karaka_dict[p_i]]] +')'
                #print(tab_name,i_start,i_end,k1,v1,i_i,i_start,i_end)
                chart_info += format_str % (k1,v1)
                western_data.append(k1+' '+v1)
            if self._western_chart:
                i_end += upagraha_count#12
            #print('western',tab_name,i_start,i_end,western_data)
            self._chart_info_labels[t].setText(chart_info) # Fixed defect here in 1.0.2
            self._chart_info_labels[t].setMaximumWidth(_chart_info_label_width)  # Fixed defect here in 1.0.2
            chart_data_1d = self._horoscope_charts[t]
            chart_data_1d = [x[:-1] for x in chart_data_1d] # remove ]n from end of each element
            self._western_chart = False
            if 'north' in self._chart_type.lower():
                _ascendant = panchanga.ascendant(jd,place,False)
                asc_house = _ascendant[0]+1
                self._charts[t]._asc_house = asc_house
                chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
                self._charts[t].setData(chart_data_north,chart_title=tab_name)
                #self._charts[t].update()
            elif 'east' in self._chart_type.lower():
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
                self._charts[t]._asc_house = row*self._charts[t].row_count+col
                self._charts[t].setData(chart_data_2d,chart_title=tab_name)
                #self._charts[t].update()
            elif 'west' in self._chart_type.lower():
                self._western_chart = True
                #print(tab_name,western_data)
                self._charts[t].setData(western_data,chart_title=tab_name,chart_title_font_size=8)
                self._charts[t].update()                
            else: # south indian
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
                self._charts[t]._asc_house = (row,col) #row*self._charts[t].row_count+col
                self._charts[t].setData(chart_data_2d,chart_title=tab_name)
                #self._charts[t].set_south_indian_chart_data(chart_data_2d,chart_title=tab_name,image_icon_path=self._image_icon_path)
            #self._charts[t].parent().layout().setSpacing(0)
            self._charts[t].update()
    def _update_tab_chart_information(self):
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa buthi - use birth time
        place = panchanga.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._update_tabs_with_divisional_charts(jd,place)
    def _update_dhasa_bhukthi_tab_information(self):
        format_str = '%-20s%-30s\n'
        tab_title = self.resources['dhasa_bhukthi_str']
        for db_tab in range(_dhasa_bhukthi_tab_count):
            p = db_tab*27
            row = 1
            for col in range(3):
                i_start = p
                i_end = i_start + 9
                db_list = list(self._dhasa_bhukti_info.items())[i_start:i_end]
                #print(i_start,i_end,db_list)
                db_str = db_list[0][0].split('-')[0]#+'\n'
                self.db_tables[db_tab][col].setItem(0,0,QTableWidgetItem(db_str))
                self.db_tables[db_tab][col].setItem(0,1,QTableWidgetItem(self.resources['ends_at_str']))
                t_row = 1
                for k,v in db_list:
                    k1 = k.split('-')[-1]
                    #db_str += format_str % (k1,v)
                    self.db_tables[db_tab][col].setItem(t_row,0,QTableWidgetItem(k1))
                    self.db_tables[db_tab][col].setItem(t_row,1,QTableWidgetItem(v))
                    t_row += 1
                p = i_end
                self.db_tables[db_tab][col].resizeColumnToContents(0)
                self.db_tables[db_tab][col].resizeColumnToContents(1)
            self.tabWidget.setTabText(_dhasa_bhukthi_tab_start+db_tab,tab_title+'-'+str(db_tab+1))
    def _update_argala_table_information(self):
        tab_name = self.resources['argala_str']+'-'+self.resources['virodhargala_str']
        self.tabWidget.setTabText(_argala_tab_start,tab_name)
        planet_names = panchanga.PLANET_NAMES
        rasi_names_en = panchanga.RAASI_LIST
        chart_1d = self._horoscope_charts[0]
        #print('chart_1d',chart_1d)
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        #print('chart_1d_ind',chart_1d_ind)
        row_count_1 = self._argala_table1[0].rowCount()
        row_count_2 = self._argala_table2[0].rowCount()
        col_count = self._argala_table1[0].columnCount()
        argala,virodhargala = house.get_argala(chart_1d_ind)
        #print('argala',argala)
        #print('virodhargala',virodhargala)
        for row in range(row_count_1):
            for col in range(col_count):
                a_planets = argala[row][col].split('/')
                #print('argala',row,col,a_planets)
                a_planets = '\n'.join(planet_names[int(p)] for p in a_planets if p.strip() !='' and p.strip() !='L')
                #print('argala',row,col,a_planets)
                self._argala_table1[0].setItem(row,col,QTableWidgetItem(a_planets))
                v_planets = virodhargala[row][col].split('/')
                v_planets = '\n'.join(planet_names[int(p)] for p in v_planets if p.strip() !='' and p.strip() !='L')
                self._argala_table2[0].setItem(row,col,QTableWidgetItem(v_planets))
        for row in range(row_count_1):
            raasi = rasi_names_en[row]
            self._argala_table1[0].setVerticalHeaderItem(row,QTableWidgetItem(raasi))
            self._argala_table1[0].resizeRowToContents(row)
            self._argala_table2[0].setVerticalHeaderItem(row,QTableWidgetItem(raasi))
            self._argala_table2[0].resizeRowToContents(row)
        for col in range(col_count):
            header = const.argala_houses_str[col]
            self._argala_table1[0].setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._argala_table1[0].resizeColumnToContents(col)
            header = const.virodhargala_houses_str[col]
            self._argala_table2[0].setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._argala_table2[0].resizeColumnToContents(col)
        self._argala_table1[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._argala_table2[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._argala_table1[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._argala_table2[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_drishti_table_information(self):
        tab_name = self.resources['raasi_str']+'-'+self.resources['graha_str']+'-'+self.resources['drishti_str']
        self.tabWidget.setTabText(_drishti_tab_start,tab_name)
        planet_names = panchanga.PLANET_NAMES
        rasi_names_en = panchanga.RAASI_LIST
        chart_1d = self._horoscope_charts[0]
        #print(chart_1d)
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        #print(chart_1d_ind)
        r_arp,r_ahp,r_app = house.raasi_drishti_from_chart(chart_1d_ind,'\n')
        #print('rasi drishti',r_arp,'\n',r_ahp,'\n',r_app)
        g_arp,g_ahp,g_app = house.graha_drishti_from_chart(chart_1d_ind,'\n')
        #print('graha drishti',g_arp,'\n',g_ahp,'\n',g_app)
        row_count_1 = self._drishti_table1[0].rowCount()
        row_count_2 = self._drishti_table2[0].rowCount()
        col_count = self._drishti_table1[0].columnCount()
        join_str = '\n'
        for row in range(row_count_2):
            col1 = join_str.join([rasi_names_en[arp] for arp in r_arp[row]])
            #print('rasi col1',row,col1)
            self._drishti_table2[0].setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp] for arp in r_ahp[row]])
            #print('rasi col2',row,col2)
            self._drishti_table2[0].setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in r_app[row] if pl != '' and pl!='L'])
            #print('rasi col3',row,col3)
            self._drishti_table2[0].setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            col1 = join_str.join([rasi_names_en[arp] for arp in g_arp[row]])
            #print('graha col1',row,col1)
            self._drishti_table1[0].setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp] for arp in g_ahp[row]])
            #print('graha col2',row,col2)
            self._drishti_table1[0].setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in g_app[row] if pl != '' and pl!='L'])
            #print('graha col3',row,col3)
            self._drishti_table1[0].setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            planet = planet_names[row]
            self._drishti_table1[0].setVerticalHeaderItem(row,QTableWidgetItem(planet))
            self._drishti_table1[0].resizeRowToContents(row)
        for row in range(row_count_2):
            planet = planet_names[row]
            self._drishti_table2[0].setVerticalHeaderItem(row,QTableWidgetItem(planet))
            self._drishti_table2[0].resizeRowToContents(row)
        headers = [self.resources['raasis_str'],self.resources['houses_str'],self.resources['planets_str']]
        #headers = [self.resources['drishti_str']+' '+ele for ele in headers]
        for col in range(col_count):
            self._drishti_table1[0].setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            self._drishti_table2[0].setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            self._drishti_table1[0].resizeColumnToContents(col)
            self._drishti_table2[0].resizeColumnToContents(col)
        self._drishti_table1[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._drishti_table2[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._drishti_table1[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._drishti_table2[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_shodhaya_table_information(self):
        """ Following List should match _shodhaya_tab_count """
        tab_names = [self.resources[st_res] for st_res in _shodhaya_dict.values()]
        chart_counters = [index for index in _shodhaya_dict.keys()]
        for t in range(_shodhaya_tab_count):
            tab_name = self.resources['shodhaya_pinda_str']+'-'+tab_names[t]
            self.tabWidget.setTabText(_shodhaya_tab_start+t,tab_name)
            label_title = self.resources['ashtaka_varga_str']+' ('+self.resources['trikona_str']+'-'+self.resources['ekadhipathya_str']+' )'
            self._shodhaya_table_label1[t].setText(label_title)
            self._shodhaya_table_label1[t].setStyleSheet("font-weight: bold")
            label_title = self.resources['shodhaya_pinda_str']
            self._shodhaya_table_label2[t].setText(label_title)
            self._shodhaya_table_label2[t].setStyleSheet("font-weight: bold")
            chart_1d = self._horoscope_charts[chart_counters[t]] #charts[t]
            #chart_1d_en = self._convert_language_chart_to_english(chart_1d)
            chart_1d = self._convert_language_chart_to_indices(chart_1d)
            bav,sav,_ = ashtakavarga.get_ashtaka_varga(chart_1d)#_en)
            tri = ashtakavarga._trikona_sodhana(bav)
            eka = ashtakavarga._ekadhipatya_sodhana(tri,chart_1d)#_en)
            sav = np.asarray(eka).sum(axis=0).tolist()
            raasi_pindas,graha_pindas,shodya_pindas = ashtakavarga._sodhya_pindas(eka,chart_1d)#_en)
            row_count = self._shodhaya_table1[t].rowCount()
            col_count = self._shodhaya_table1[t].columnCount()
            for r in range(col_count):
                for p in range(row_count-1):
                    self._shodhaya_table1[t].setItem(p,r,QTableWidgetItem(str(eka[p][r])))
                self._shodhaya_table1[t].setItem(row_count-1,r,QTableWidgetItem(str(sav[r])))
            for p in range(row_count):
                if p==row_count-1:
                    header = "SAV"
                elif p==row_count-2:
                    header = self.resources['ascendant_str']
                else:
                    header = self._horo._get_planet_list()[0][p]
                self._shodhaya_table1[t].setVerticalHeaderItem(p,QTableWidgetItem(header))
                self._shodhaya_table1[t].resizeRowToContents(p)
            for r in range(col_count):
                header = self._horo._get_raasi_list()[0][r]
                self._shodhaya_table1[t].setHorizontalHeaderItem(r,QTableWidgetItem(header))
                self._shodhaya_table1[t].resizeColumnToContents(r)                
            self._shodhaya_table1[t].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
            self._shodhaya_table1[t].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
            self._shodhaya_table1[t].update()
            row_count = self._shodhaya_table2[t].rowCount()
            col_count = self._shodhaya_table2[t].columnCount()
            row_names = [self.resources['graha_pinda_str'],self.resources['raasi_pinda_str'],self.resources['shodhaya_pinda_str']]
            for p in range(col_count):
                self._shodhaya_table2[t].setItem(0,p,QTableWidgetItem(str(raasi_pindas[p])))
                self._shodhaya_table2[t].setItem(1,p,QTableWidgetItem(str(graha_pindas[p])))
                self._shodhaya_table2[t].setItem(2,p,QTableWidgetItem(str(shodya_pindas[p])))
            for row in range(row_count):
                self._shodhaya_table2[t].setVerticalHeaderItem(row,QTableWidgetItem(row_names[row]))
                self._shodhaya_table2[t].resizeRowToContents(row)
            for p in range(col_count):
                self._shodhaya_table2[t].setHorizontalHeaderItem(p,QTableWidgetItem(self._horo._get_planet_list()[0][p]))
                self._shodhaya_table2[t].resizeColumnToContents(p)
            self._shodhaya_table2[t].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
            self._shodhaya_table2[t].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
            self._shodhaya_table2[t].update()
    def _update_ashtaka_varga_tab_information(self):
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa buthi - use birth time
        place = panchanga.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        tab_names = [self.resources[tab] for tab in self.tabNames[1:_dhasa_bhukthi_tab_start]]
        for t in range(_ashtaka_varga_tab_count):
            tab_name = self.resources['ashtaka_varga_str']+'-'+tab_names[t]
            self.tabWidget.setTabText(_ashtaka_varga_tab_start+t,tab_name)
            chart_1d = self._horoscope_charts[t] #charts[t]
            #chart_1d_en = self._convert_language_chart_to_english(chart_1d)
            chart_1d = self._convert_language_chart_to_indices(chart_1d)
            #print('chart_1d',chart_1d)
            bav,sav, pav = ashtakavarga.get_ashtaka_varga(chart_1d)#_en)
            ac = 0
            for i in range(3):
                for j in range(3):
                    if ac ==0:
                        chart_data_1d = sav
                        chart_title = 'SAV'
                    else:
                        chart_data_1d = bav[ac-1]
                        chart_title = self._horo._get_planet_list()[0][ac-1]
                    if 'north' in self._chart_type.lower():
                        _ascendant = panchanga.ascendant(jd,place,False)
                        asc_house = _ascendant[0]+1
                        chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
                        self._ashtaka_charts[t][ac].setData(chart_data_north,chart_title=chart_title)
                    elif 'east' in self._chart_type.lower():
                        chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
                        self._ashtaka_charts[t][ac]._asc_house = self._charts[t]._asc_house
                        self._ashtaka_charts[t][ac].setData(chart_data_2d,chart_title=chart_title,chart_title_font_size=8)
                    else: # south indian
                        chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d)
                        self._ashtaka_charts[t][ac]._asc_house = self._charts[t]._asc_house
                        self._ashtaka_charts[t][ac].setData(chart_data_2d,chart_title=chart_title,chart_title_font_size=7)
                    self._ashtaka_charts[t][ac].parent().layout().setSpacing(0)
                    self._ashtaka_charts[t][ac].update()
                    ac += 1        
    def _update_yoga_table(self):
        cur_row = self._yoga_list.currentRow()
        if cur_row == -1:
            cur_row = 0
            self._yoga_list.setCurrentRow(cur_row)
        cur_item = self._yoga_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected yoga information in the yoga edit box """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        yoga_results_text = ''
        yoga_keys = list(self._yoga_results.keys())
        for k in range(_yogas_per_list_item):
            if sy_len > k:
                yk = yoga_keys[cur_row * _yogas_per_list_item + k] 
                yoga_chart,yoga_name, yoga_description, yoga_predictions = self._yoga_results[yk]
                yoga_results_text += "<b><u>"+yoga_name+" ("+yoga_chart+")</u></b><br>"
                yoga_results_text += "<b>"+self.resources['description_str']+"</b> "+yoga_description+"<br>"
                yoga_results_text += "<b>"+self.resources['prediction_str']+"</b> " +yoga_predictions+"<br><br>"
        yoga_results_text = yoga_results_text[:-len("<br>")]
        self._yoga_text.setHtml(yoga_results_text)
        
    def _update_yoga_tab_information(self):
        self.tabWidget.setTabText(_yoga_tab_start,self.resources['yoga_str'])
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa buthi - use birth time
        place = panchanga.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        #yoga_results = yoga.get_yoga_details(jd,place,divisional_chart_factor=1,language=available_languages[self._language])
        self._yoga_results,_,_ = yoga.get_yoga_details_for_all_charts(jd,place,language=available_languages[self._language])
        self._yoga_list.clear()
        yoga_count = len(self._yoga_results)
        #print(yoga_count,'yogas found')
        for k in range(0,yoga_count,_yogas_per_list_item):
            key = ''
            for kk in range(_yogas_per_list_item):
                if k+kk<=yoga_count-kk:
                    key = key+'\n'+''.join(list(self._yoga_results.values())[k+kk][1].split()[0:-1])
            key = key[1:]
            self._yoga_list.addItem(QListWidgetItem(key))
        #self._yoga_list.addItems(self._yoga_results.keys())
        self._yoga_list.setCurrentRow(0)
        return 
    def _update_compatibility_tab_information(self):
        self.tabWidget.setTabText(_compatibility_tab_start,self.resources['compatibility_str'])
        bn=None
        bp=None
        gn=None
        gp=None
        self._mahendra_porutham = self._mahendra_porutham_checkbox.isChecked()
        self._vedha_porutham = self._vedha_porutham_checkbox.isChecked()
        self._rajju_porutham = self._rajju_porutham_checkbox.isChecked()
        self._sthree_dheerga_porutham = self._sthree_dheerga_porutham_checkbox.isChecked()
        self._minimum_score = float(self._min_score_combo.text())
        if self._gender.lower() == 'male':
            bn = self._horo._nakshatra_number
            bp = self._horo._paadha_number
        else:
            gn = self._horo._nakshatra_number
            gp = self._horo._paadha_number
        comp = compatibility.Match(boy_nakshatra_number=bn,boy_paadham_number=bp,girl_nakshatra_number=gn,girl_paadham_number=gp,\
                   check_for_mahendra_porutham=self._mahendra_porutham,check_for_vedha_porutham=self._vedha_porutham,\
                   check_for_rajju_porutham=self._rajju_porutham,check_for_shreedheerga_porutham=self._sthree_dheerga_porutham,\
                   minimum_score=self._minimum_score)
        self._matching_stars_tuple = sort_tuple(comp.get_matching_partners(),4,reverse=True)
        matching_stars_count = len(self._matching_stars_tuple)
        #print(matching_stars_count,' matching stars found for',bn,bp,gn,gp,self._mahendra_porutham,self._vedha_porutham,self._rajju_porutham,self._sthree_dheerga_porutham)
        if not self._matching_stars_tuple:
            self._matching_star_list.clear()
            self._matching_star_list.addItems(['No matching found'])
        else:
            self._matching_star_list.clear()
            matching_stars = []
            for k in range(0,matching_stars_count,_comp_results_per_list_item):
                key = ''
                for kk in range(_comp_results_per_list_item):
                    if k+kk<=matching_stars_count-kk:
                        m_s_tup = self._matching_stars_tuple[k+kk]
                        nakshatra = utils.NAKSHATRA_LIST[m_s_tup[0]-1]
                        paadham = str(m_s_tup[1])+'-'+str(m_s_tup[2])
                        key += '\n'+nakshatra+'-'+paadham
                key = key[1:]
                matching_stars.append(key)
            self._matching_star_list.addItems(matching_stars)
            self._matching_star_list.setCurrentRow(0)
            
    def _update_compatibility_table(self):
        cur_row = self._matching_star_list.currentRow()
        cur_item = self._matching_star_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected item in the results table """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        selected_list_index = self._matching_star_list.currentRow()
        for k in range(_comp_results_per_list_item):
            if sy_len > k:
                self._comp_results_table[k].setVisible(True)
                results_table = self._comp_results_table[k]
                sel_index = selected_list_index*_comp_results_per_list_item+k
                self._update_compatibility_table_tmp(results_table,sel_index)
            else:
                self._comp_results_table[k].setVisible(False)
    def _update_compatibility_table_tmp(self,results_table,selected_list_index):
        selected_matching_star_tuple = self._matching_stars_tuple[selected_list_index]
        ettu_poruthham_list = [self.resources['varna_str'], self.resources['vasiya_str'], self.resources['gana_str'], 
                               self.resources['tara_str'], self.resources['yoni_str'], self.resources['adhipathi_str'],\
                               self.resources['raasi_str1'], self.resources['naadi_str']]
        ettu_porutham_max_score = [compatibility.varna_max_score,compatibility.vasiya_max_score,compatibility.gana_max_score,\
                                    compatibility.nakshathra_max_score,compatibility.yoni_max_score,compatibility.raasi_adhipathi_max_score, \
                                    compatibility.raasi_max_score, compatibility.naadi_max_score]
        naalu_porutham_list = [self.resources['mahendra_str'],self.resources['vedha_str'],self.resources['rajju_str'],self.resources['sthree_dheerga_str']]
        ettu_porutham_results = selected_matching_star_tuple[3]
        compatibility_score = selected_matching_star_tuple[4]
        naalu_porutham_results = selected_matching_star_tuple[5]
        nakshatra = utils.NAKSHATRA_LIST[selected_matching_star_tuple[0]-1]
        paadham = self.resources['paadham_str']+' '+str(selected_matching_star_tuple[1])+'-'+str(selected_matching_star_tuple[2])
        #print('updating comp table',_compatibility_tab_start + tab_index,col,self.resources['compatibility_str']+'-'+str(tab_index+1),nakshatra+'-'+paadham)
        result = ''
        results_table.setHorizontalHeaderItem(0,QTableWidgetItem(nakshatra+'-'+paadham))
        results_table.setHorizontalHeaderItem(1,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(2,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(3,QTableWidgetItem(''))
        row = 0
        for p,porutham in enumerate(ettu_poruthham_list):
            #result += format_str % (porutham,str(ettu_porutham_results[p][0]),str(ettu_porutham_results[p][1]))
            results_table.setItem(row,0,QTableWidgetItem(porutham))
            results_table.setItem(row,1,QTableWidgetItem(str(ettu_porutham_results[p])))
            results_table.setItem(row,2,QTableWidgetItem(str(ettu_porutham_max_score[p])))
            perc = '{:3.0f}%'.format(ettu_porutham_results[p]/ettu_porutham_max_score[p]*100)
            results_table.setItem(row,3,QTableWidgetItem(str(perc)))
            row += 1
        for p,porutham in enumerate(naalu_porutham_list):
            #result += format_str % (porutham,str(naalu_porutham_results[p]),'')
            results_table.setItem(row,0,QTableWidgetItem(porutham))
            results_table.setItem(row,1,QTableWidgetItem(str(naalu_porutham_results[p])))
            results_table.setItem(row,2,QTableWidgetItem('True'))
            if naalu_porutham_results[p]:
                results_table.setItem(row,3,QTableWidgetItem(str('\u2705')))
            else:
                results_table.setItem(row,3,QTableWidgetItem(str('\u274C')))
            row += 1
        #result += format_str % ('Overall Compatibility Score:', str(compatibility_score) +' out of '+ str(compatibility.max_compatibility_score),'')
        results_table.setItem(row,0,QTableWidgetItem(self.resources['overall_str']))
        results_table.setItem(row,1,QTableWidgetItem(str(compatibility_score)))
        results_table.setItem(row,2,QTableWidgetItem(str(compatibility.max_compatibility_score)))
        perc = '{:3.0f}%'.format(compatibility_score/compatibility.max_compatibility_score*100)
        results_table.setItem(row,3,QTableWidgetItem(str(perc)))
        results_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        results_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for c in range(4):
            results_table.resizeColumnToContents(c)
        for r in range(14):
            results_table.resizeRowToContents(r)
        
    def _update_chart_ui_with_info(self):
        info_str = ''
        format_str = '%-20s%-40s\n'
        self._fill_information_label1(info_str, format_str)
        self._fill_information_label2(info_str, format_str)
        self._update_tab_chart_information()
        if not self._western_chart:
            self._update_dhasa_bhukthi_tab_information()
            self._update_ashtaka_varga_tab_information()
            self._update_drishti_table_information()
            self._update_argala_table_information()
            self._update_shodhaya_table_information()
            self._update_yoga_tab_information()
            if  self._show_compatibility:
                self._update_compatibility_tab_information()
        self.update()
    def _get_place_latitude_longitude(self,place_name):
        result = None
        place_found = False
        ' first check if lat/long in world cities db'
        place_index = -1
        place_name_1 = place_name.replace(',',' ')
        place_index = [row for row,city in enumerate(self._world_cities_list) if place_name_1.split()[0].lower() in city.lower()]
        if len(place_index)>0:
            place_found = True
            print(place_name,'in the database')
            place_index = int(place_index[0])
            self._latitude = round(float(self._world_cities_db[place_index,2]),4)
            self._longitude = round(float(self._world_cities_db[place_index,3]),4)
            self._time_zone = round(float(self._world_cities_db[place_index,5]),2)
        else:
            print(place_name,'not in the world cities csv database.Trying to get from Google')
            result = _scrap_google_map_for_latlongtz_from_city_with_country(place_name)
            if result != None and len(result)==3:
                place_found = True
                print(place_name,' found from google maps')
                self._place_name = place_name
                self._latitude = round(result[0],4)
                self._longitude = round(result[1],4)
                self._time_zone = round(result[2],2)
            else:
                print('Could not get',place_name,'from google.Trying to get from OpenStreetMaps')
                place_found = False
                result = panchanga.get_latitude_longitude_from_place_name(place_name)
                if result:
                    place_found = True
                    print(place_name,'found in OpenStreetMap')
                    [self._place_name,self._latitude,self._longitude,self._time_zone] = result
        if place_found:
            self._place_text.setText(self._place_name)
            self._lat_text.setText(str(self._latitude))
            self._long_text.setText(str(self._longitude))
            self._tz_text.setText(str(self._time_zone))
            print(self._place_name,self._latitude,self._longitude,self._time_zone)
        else:
            msg = place_name+" could not be found in OpenStreetMap.\nTry entering latitude and longitude manually.\nOr try entering nearest big city"
            print(msg)
            QMessageBox.about(self,"City not found",msg)
            self._lat_text.setText('')
            self._long_text.setText('')
            
    def _save_city_to_database(self):
        if self._validate_ui():
            " add this data to csv file "
            tmp_arr = self._place_name.split(',')
            country = 'N/A'
            city = tmp_arr[0]
            if len(tmp_arr) > 1:
                country = tmp_arr[1:]
            last_row = [city,city,self._latitude,self._longitude,country,self._time_zone]
            print('writing ',last_row,' to ',_world_city_csv_file)
            self._df.loc[len(self._df.index)] = last_row
            self._df.to_csv(_world_city_csv_file,mode='w',header=None,index=False)#,quoting=None)
        return          
    def save_as_pdf(self,pdf_file_name=None):
        """
            Save the displayed chart as a pdf
            Choose a file from file save dialog displayed
        """
        image_prefix = 'pdf_grb_'
        image_ext = '.png'
        if pdf_file_name==None:
            path = QFileDialog.getSaveFileName(self, 'Choose folder and file to save as PDF file', './output', 'PDF files (*.pdf)')#)
            pdf_file_name = path[0]
        image_files = []
        combined_image_files = []
        image_id = 1
        if not self._western_chart:
            self._matching_star_list.setVisible(False)
            self._matching_star_list.setMaximumWidth(0)
            self._yoga_list.setVisible(False)
            self._yoga_list.setMaximumWidth(0)
            for c in range(_comp_results_per_list_item):
                self._comp_results_table[c].update()
            self._yoga_text.update()
        if pdf_file_name:
            for t in range(self.tabCount):
                self._hide_show_even_odd_pages(image_id)
                self.tabWidget.setCurrentIndex(t)
                self._show_only_tab(t)
                if t==_yoga_tab_start:# self.tabCount-1:
                    for row in range(self._yoga_list.count()):
                        self._hide_show_even_odd_pages(image_id)
                        self._yoga_list.setCurrentRow(row)
                        image_file = _images_path+image_prefix+str(image_id)+image_ext
                        im = self.grab()
                        im.save(image_file) 
                        image_files.append(image_file)
                        image_id +=1
                elif t==_compatibility_tab_start:
                    for row in range(0,self._matching_star_list.count(),_comp_results_per_list_item):
                        self._hide_show_even_odd_pages(image_id)
                        self._matching_star_list.setCurrentRow(row)
                        image_file = _images_path+image_prefix+str(image_id)+image_ext
                        im = self.grab()
                        im.save(image_file) 
                        image_files.append(image_file)
                        image_id +=1
                else:
                    image_file = _images_path+image_prefix+str(image_id)+image_ext
                    image_files.append(image_file)
                    im = self.grab()
                    im.save(image_file) 
                    image_id +=1
            self._reset_all_ui()
            ci = 1
            for i in range(0,len(image_files),2):
                combined_image_file = _images_path+'combined_'+str(ci)+image_ext
                _combine_multiple_images(image_files[i:i+2],combined_image_file)
                combined_image_files.append(combined_image_file)
                ci += 1
            image_count = len(image_files)
            combined_image_count = len(combined_image_files)
            with open(pdf_file_name,"wb") as f:
                f.write(img2pdf.convert(combined_image_files))
            f.close()
        for image_file in image_files+combined_image_files:
            if os.path.exists(image_file):
                os.remove(image_file)
    def _reset_all_ui(self):
        self._hide_show_layout_widgets(self._row1_h_layout, True)
        self._hide_show_layout_widgets(self._row2_h_layout, True)
        self._hide_show_layout_widgets(self._comp_h_layout, True)
        self._footer_label.show()
        if not self._western_chart:
            self._matching_star_list.setVisible(True)
            self._matching_star_list.setMaximumWidth(_compatability_list_width)
            self._yoga_list.setVisible(True)
            self._yoga_list.setMaximumWidth(_yoga_list_box_width)
            for c in range(_comp_results_per_list_item):
                self._comp_results_table[c].update()
            self._yoga_text.update()
        for t in range(self.tabCount): # reset all tabs to visible
            self.tabWidget.setTabVisible(t,True)
        
    def _hide_show_even_odd_pages(self,image_id):
        if image_id % 2 == 0: # Even Page
            self._hide_show_layout_widgets(self._row1_h_layout, False)
            self._hide_show_layout_widgets(self._row2_h_layout, False)
            self._hide_show_layout_widgets(self._comp_h_layout, False)
            self._footer_label.show()
        else:
            self._hide_show_layout_widgets(self._row1_h_layout, True)
            if image_id==1:
                self._hide_show_layout_widgets(self._row2_h_layout, True)
                self._hide_show_layout_widgets(self._comp_h_layout, True)
            self._footer_label.hide()        
    def _hide_show_layout_widgets(self,layout,show):
        for index in range(layout.count()):
            myWidget = layout.itemAt(index).widget()
            if show:
                myWidget.show()
            else:
                myWidget.hide()
            index -=1            
    def exit(self):
        self.close()
        QApplication.quit()
        print('Application Closed')
    def _show_only_tab(self,t): #set onlt tab t to be visible
        for ti in range(self.tabCount):
            self.tabWidget.setTabVisible(ti,False)
            if t==ti:
                self.tabWidget.setTabVisible(ti,True)
    def _convert_language_chart_to_english(self,rasi_1d_lang):
        rasi_1d_en = rasi_1d_lang[:]
        planet_list_lang = self._horo._get_planet_list()[0]+[self.resources['ascendant_str']]
        #print(planet_list_lang)
        planet_list_en = ['Sun ☉','Moon ☾','Mars ♂','Mercury ☿','Jupiter ♃','Venus ♀','Saturn ♄','Raagu ☊','Kethu ☋','Uranus','Neptune','Pluto','Lagnam']
        planet_lang_dict = {planet_list_lang[i]:planet_list_en[i] for i in range(len(planet_list_en))}
        #print('planet_lang_dict',planet_lang_dict)
        #rasi_1d_lang =['','சூரியன்/சந்திரன்','','செவ்வாய்','லக்னம்/புதன்','குரு','','சுக்ரன்','','சனி','ராகு','கேது']
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v)
        return rasi_1d_en
    def _convert_language_chart_to_indices(self,rasi_1d_lang):
        #print('_convert_language_chart_to_indices before english',rasi_1d_lang)
        rasi_1d_en = self._convert_language_chart_to_english(rasi_1d_lang)
        #print('_convert_language_chart_to_indices after english',rasi_1d_lang)
        planet_list_en = ['Sun ☉','Moon ☾','Mars ♂','Mercury ☿','Jupiter ♃','Venus ♀','Saturn ♄','Raagu ☊','Kethu ☋','Uranus','Neptune','Pluto']+['Lagnam']
        #print('planet_list_en',planet_list_en)
        #planet_list_en = ['சூரியன்☉','சந்திரன்☾','செவ்வாய்♂','புதன்☿','குரு♃','சுக்ரன்♀','சனி♄','ராகு☊','கேது☋','அருணா(யுரேனஸ்)','வருணா (நெப்டியூன்)','குறுகோள் (புளூட்டோ)','லக்னம்']
        #planet_list_en = ['Sun ☉','Moon ☾','Mars ♂','Mercury ☿','Jupiter ♃','Venus ♀','Saturn ♄','Raagu ☊','Kethu ☋','Uranus','Neptune','Pluto','Lagnam']
        planet_lang_dict = {planet_list_en[i]:str(i) for i in range(len(planet_list_en))}
        #print('planet_lang_dict',planet_lang_dict)
        last_key = list(planet_lang_dict)[-1]
        planet_lang_dict[last_key] = 'L'
        #print('planet_lang_dict',planet_lang_dict)
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v)
        #print('rasi_1d_lang',rasi_1d_lang)
        return rasi_1d_en
def _scrap_google_map_for_latlongtz_from_city_with_country(city_with_country):
    url = "https://www.google.cl/maps/place/"+city_with_country#+' time zone'
    resp=requests.request(method="GET",url=url)
    r = requests.get(url)
    txt = r.text
    
    find1 = "window.APP_INITIALIZATION_STATE="
    find2 = ";window.APP"
    
    i1 = txt.find(find1)
    i2 = txt.find(find2, i1+1 )
    js = txt[i1+len(find1):i2]
    data = json.loads(js)[0][0][1:3]
    latitude = data[1]
    longitude = data[0]
    timezone_offset = panchanga.get_place_timezone_offset(latitude, longitude)
    print('city',city_with_country,'lat=',latitude,'long=',longitude,'timezone offset',timezone_offset)
    return latitude,longitude,timezone_offset
def show_horoscope(data):
    """
        Same as class method show() to display the horoscope
        @param data - last chance to pass the data to the class
    """
    app=QApplication(sys.argv)
    window=ChartWindow(data)
    window.show()
    app.exec_()
def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1
def _convert_1d_list_to_2d_list(list_1d,map_1d_to_2d=None):
    if map_1d_to_2d==None:
        rasi_2d = [['X']*row_count for _ in range(col_count)]
        map_1d_to_2d=[ [1,2,3], [4,5,6], [7,8,9]]
        for index, row in enumerate(map_1d_to_2d):
            i,j = [(index, row.index(p)) for index, row in enumerate(map_1d_to_2d) if p in row][0]
            list_2d[i][j] = val
        return list_2d
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
    result =(-1,-1)
    for row in range(len(list_2d)):
        for col in range(len(list_2d[0])):
            if match_string in list_2d[row][col]:
                return (row,col)
def _udhayadhi_nazhikai(birth_time,sunrise_time):
    """ TODO: this will not for work for BC dates due to datetime """
    def _convert_str_to_time(str_time):
        arr = str_time.split(':')
        arr[-1] = arr[-1].replace('AM','').replace('PM','')
        return time(int(arr[0]),int(arr[1]),int(arr[2]))
    birth_time = _convert_str_to_time(birth_time)
    sunrise_time =_convert_str_to_time(sunrise_time)
    import math
    days = 0
    duration = str(datetime.combine(date.min, birth_time) - datetime.combine(date.min, sunrise_time))
    hour_sign = ''
    if " day" in duration:
        duration = str(datetime.combine(date.min, sunrise_time) - datetime.combine(date.min, birth_time))
        hour_sign = '-'
    hours,minutes,seconds = duration.split(":")
    tharparai = (int(hours)+days)*9000+int(minutes)*150+int(seconds)
    naazhigai = math.floor(tharparai/3600)
    vinadigal = math.floor( (tharparai-(naazhigai*3600))/60 )
    tharparai = math.floor(tharparai - naazhigai*3600 - vinadigal*60)
    return hour_sign+str(naazhigai)+':'+str(vinadigal)+':'+str(tharparai)
def _get_date_difference(then, now = datetime.now(), interval = "default"):
    from dateutil import relativedelta
    diff = relativedelta.relativedelta(now,then)
    years = abs(diff.years)
    months = abs(diff.months)
    days = abs(diff.days)
    return [years,months,days]
def _dhasa_balance(date_of_birth,dhasa_end_date):
    d_arr = date_of_birth.split('-')
    if len(d_arr) == 4:
        _,year,month,day = d_arr
    else:
        year,month,day = d_arr
    dob = datetime(abs(int(year)),int(month),int(day))
    d_arr = dhasa_end_date.split('-')
    if len(d_arr) == 4:
        _,year,month,day = d_arr
    else:
        year,month,day = d_arr
    ded = datetime(abs(int(year)),int(month),int(day))
    duration = _get_date_difference(dob,ded)#,starting_text="Dhasa Balance:")
    return duration
def _combine_multiple_images(image_list,output_image,combine_mode='vertical',image_quality_in_pixels=100):
    total_width = 0
    total_height = 0
    max_width = 0
    max_height = 0
    ix =[]
    for img in image_list:
        im = Image.open(img)
        size = im.size
        w = size[0]
        h = size[1]
        total_width += w 
        total_height += h
        
        if h > max_height:
            max_height = h
        if w > max_width:
            max_width = w
        ix.append(im) 
    #print((total_width, total_height, max_width, max_height))
    if combine_mode.lower()=='vertical':
        target = Image.new('RGB', (max_width, total_height))
    else:
        target = Image.new('RGB', (total_width, max_height))
    pre_w = 0
    pre_h = 0
    for img in ix:
        if combine_mode.lower()=='vertical':
            target.paste(img, (pre_w, pre_h, pre_w+max_width, pre_h + img.size[1]))
            pre_h += img.size[1]
        else:
            target.paste(img, (pre_w, pre_h, pre_w+img.size[0], pre_h + img.size[1]))
            pre_w += img.size[0]            
    #print(image_list,'combined to',output_image)
    target.save(output_image, quality=image_quality_in_pixels)
if __name__ == "__main__":
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart_type = 'South'
    chart = ChartWindow(chart_type=chart_type,show_marriage_compatibility=True)
    chart.language('Tamil')
    chart.name('Bhuvana')#'Krishna') #Rama
    chart.gender('Female')#'Male')
    chart.place('Chennai')#'Mathura,IN') #Ayodhya,IN
    chart.latitude('13.0389')#'27.4955539')
    chart.longitude('80.2619')#'77.6855554')
    chart.time_zone('5.5')
    chart.date_of_birth('1996,12,7')#-3229,6,1')#'-5114,1,10')
    chart.time_of_birth('10:34:00')#'22:34:00')#'12:30:00')
    chart.chart_type(chart_type)
    chart.compute_horoscope()
    chart.show()
    #chart.save_as_pdf('./output.pdf')
    sys.exit(App.exec())
