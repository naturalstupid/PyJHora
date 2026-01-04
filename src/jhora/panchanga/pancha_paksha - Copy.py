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
"""
    Module for Pancha Paksha Sastra
"""

import sys
from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, \
                QLineEdit, QHBoxLayout,QLabel, QCompleter, QMessageBox, QPushButton, QComboBox
import pandas as pd
import datetime
from jhora import utils, const
from jhora.panchanga import drik

PP_DB_FILE = const.ROOT_DIR+ '/data/pancha_pakshi_db.csv'
IMAGE_PATH = const._IMAGES_PATH + const._sep
_NAK_BIRD_INDEX = 0; _WEEK_DAY_INDEX = 1; _PAKSHA_INDEX = 2; _DAYNIGHT_INDEX = 3
_MAIN_BIRD_INDEX = 4; _MAIN_ACTIVITY_INDEX = 5; _SUB_BIRD_INDEX = 6; _SUB_ACTIVITY_INDEX = 7
_DURATION_FACTOR = 8
# Define the data types for each column
dtype_dict = {
    _NAK_BIRD_INDEX: 'int32',  # Column 0 as integer
    _WEEK_DAY_INDEX: 'int32',  # Column 1 as integer
    _PAKSHA_INDEX: 'int32',  # Column 2 as integer
    _DAYNIGHT_INDEX: 'int32',  # Column 3 as integer
    _MAIN_BIRD_INDEX: 'int32',  # Column 4 as integer
    _MAIN_ACTIVITY_INDEX: 'int32',  # Column 5 as integer
    _SUB_BIRD_INDEX: 'int32',  # Column 6 as integer
    _SUB_ACTIVITY_INDEX: 'int32',  # Column 7 as integer
    _DURATION_FACTOR: 'float64'  # Column 8 as float
}
#Pancha Pakshi for each star (birth if sukla paksha, birth if in krishna paksha)
#1:Vulture 2:Owl, 3:Crow, 4:Cock, 5:Peacock
pancha_pakshi_birds = ['vulture','owl','crow','cock','peacock']
pancha_pakshi_images = ['vulture.png','owl.png','crow.png','cock.png','peacock.png']
pancha_pakshi_activities = ['ruling','eating','walking','sleeping','dying']
pancha_pakshi_activity_images = [p+'.png' for p in pancha_pakshi_activities]
bird_list = [0,1,2,3,4];activity_list = [1,2,3,4,5] 
pancha_pakshi_stars_birds_paksha = [(1,5),(1,5),(1,5),(1,5),(1,5),(2,4),(2,4),(2,4),(2,4),(2,4),(2,4),
                                    (3,3),(3,3),(3,3),(3,3),(3,3),(4,2),(4,2),(4,2),(4,2),(4,2),
                                    (5,1),(5,1),(5,1),(5,1),(5,1),(5,1)]
#1:Sunday, 2:Mon, 3:Tue, 4:Wed, 5:Thu, 6:Fri, 7:Sat
#1st element Vulture... last element Peacock
#1st tuple sukla paksha 2nd tuple krishna paksha
pancha_pakshi_death_days = [[(5,7),(3)],[(1,6),(2)],[(2),(1)],[(3),(5,7)],[(4),(4,6)] ]
pancha_pakshi_ruling_days = [[(1,3),(6)],[(2,4),(5)],[(5),(4)],[(6),(1,3)],[(7),(2,7)] ]
pancha_pakshi_ruling_nights = [[(6),(1,3)],[(7),(4)],[(1,3),(5)],[(2,4),(2,7)],[(5),(6)] ]
# Duration List: First list is for day time and 2nd list for night time
# Each duration is respectively for activities: Rule, Eat, Walk, Sleep, Death
_pancha_pakshi_duration_list = [[48,30,36,18,12],[24,30,30,24,36]]
pancha_pakshi_duration_list = [[ele/144 for ele in row] for row in _pancha_pakshi_duration_list ]

"""
    elements 1-5 are daytime (sunrise to sunset equal durations = day_length/5)
        Each of this will need to be divided by durations depend on activity but totals day_length),
    6-10 are night time (sunset to sunrise equal durations = night_length/5)
        Each of this will need to be divided by durations depend on activity but totals night_length),
    (1-10 are Sukla Paksha)
    elements 11-15 are daytime, 16-20 night time (11-20 are Krishna Paksha)
    element values: 1:Rule, 2:Eat, 3:Walk, 4:Sleep, 5:Death
    Each column starts with main bird and continues cyclically to other birds
    
"""
pancha_paksha_activity_list = [
[ #Vulture
    [2,3,1,4,5,5,3,4,2,1,3,2,5,4,1,2,4,3,5,1],
    [5,2,3,1,4,3,4,2,1,5,4,1,3,2,5,5,1,2,4,3],
    [2,3,1,4,5,5,3,4,2,1,3,2,5,4,1,2,4,3,5,1],
    [5,2,3,1,4,3,4,2,1,5,5,4,1,3,2,4,3,5,1,2],
    [4,5,2,3,1,4,2,1,5,3,1,3,2,5,4,3,5,1,2,4],
    [1,4,5,2,3,2,1,5,3,4,2,5,4,1,3,1,2,4,3,5],
    [3,1,4,5,2,1,5,3,4,2,4,1,3,2,5,5,1,2,4,3],
],
[ #Owl
    [3,1,4,5,2,1,5,3,4,2,5,4,1,3,2,1,2,4,3,5],
    [2,3,1,4,5,5,3,4,2,1,3,2,5,4,1,3,5,1,2,4],
    [3,1,4,5,2,1,5,3,4,2,5,4,1,3,2,1,2,4,3,5],
    [2,3,1,4,5,5,3,4,2,1,1,3,2,5,4,2,4,3,5,1],
    [5,2,3,1,4,3,4,2,1,5,2,5,4,1,3,4,3,5,1,2],
    [4,5,2,3,1,4,2,1,5,3,4,1,3,2,5,5,1,2,4,3],
    [1,4,5,2,3,2,1,5,3,4,3,2,5,4,1,3,5,1,2,4],
],
[ #Crow
    [1,4,5,2,3,2,1,5,3,4,1,3,2,5,4,5,1,2,4,3],
    [3,1,4,5,2,1,5,3,4,2,5,4,1,3,2,4,3,5,1,2],
    [1,4,5,2,3,2,1,5,3,4,1,3,2,5,4,5,1,2,4,3],
    [3,1,4,5,2,1,5,3,4,2,2,5,4,1,3,1,2,4,3,5],
    [2,3,1,4,5,5,3,4,2,1,4,1,3,2,5,2,4,3,5,1],
    [5,2,3,1,4,3,4,2,1,5,3,2,5,4,1,3,5,1,2,4],
    [4,5,2,3,1,4,2,1,5,3,5,4,1,3,2,4,3,5,1,2],
],
[ #Cock
    [4,5,2,3,1,4,2,1,5,3,2,5,4,1,3,3,5,1,2,4],
    [1,4,5,2,3,2,1,5,3,4,1,3,2,5,4,2,4,3,5,1],
    [4,5,2,3,1,4,2,1,5,3,2,5,4,1,3,3,5,1,2,4],
    [1,4,5,2,3,2,1,5,3,4,4,1,3,2,5,5,1,2,4,3],
    [3,1,4,5,2,1,5,3,4,2,3,2,5,4,1,1,2,4,3,5],
    [2,3,1,4,5,5,3,4,2,1,5,4,1,3,2,4,3,5,1,2],
    [5,2,3,1,4,3,4,2,1,5,1,3,2,5,4,2,4,3,5,1],
],
[ #Peacock
    [5,2,3,1,4,3,4,2,1,5,4,1,3,2,5,4,3,5,1,2],
    [4,5,2,3,1,4,2,1,5,3,2,5,4,1,3,1,2,4,3,5],
    [5,2,3,1,4,3,4,2,1,5,4,1,3,2,5,4,3,5,1,2],
    [4,5,2,3,1,4,2,1,5,3,3,2,5,4,1,3,5,1,2,4],
    [1,4,5,2,3,2,1,5,3,4,5,4,1,3,2,5,1,2,4,3],
    [3,1,4,5,2,1,5,3,4,2,1,3,2,5,4,2,4,3,5,1],
    [2,3,1,4,5,5,3,4,2,1,2,5,4,1,3,1,2,4,3,5],
]
]
_next_list_item = lambda _list,_current,dir=1,step=1: _list[(_list.index(_current)+dir*step)%len(_list)]

class PanchaPakshiSastraWidget(QWidget):
    def __init__(self, birth_bird_index, headers=None, parent_level_list=None, child_level_list=None, hide_headers=True):
        super().__init__()
        self.setWindowTitle("TreeWidget Demo")
        self.setGeometry(50, 50, 800, 600)
        # Determine the maximum number of columns
        if parent_level_list:
            column_count = max(len(row) for row in parent_level_list + [item for sublist in child_level_list for item in sublist])
        else:
            column_count = 0  # If the parent level list is empty

        # Layout
        v_layout = QVBoxLayout()

        h_layout = QHBoxLayout()
        _dob_label = QLabel("Date:")
        h_layout.addWidget(_dob_label)
        self._dob_text = QLineEdit('')
        self._dob_text.setToolTip('Date in the format YYYY,MM,DD')
        _dob_label.setMaximumWidth(75)
        self._dob_text.setMaximumWidth(75)
        h_layout.addWidget(self._dob_text)
        _tob_label = QLabel("Time:")
        h_layout.addWidget(_tob_label)
        self._tob_text = QLineEdit('')
        self._tob_text.setToolTip('Enter time in the format HH:MM:SS if afternoon use 12+ hours')
        _tob_label.setMaximumWidth(75)
        self._tob_text.setMaximumWidth(75)
        current_date_str,current_time_str = datetime.datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self._dob_text.setText(current_date_str)
        self._tob_text.setText(current_time_str)
        h_layout.addWidget(self._tob_text)

        self._place_name = ''
        self._place_text = QLineEdit(self._place_name)
        _world_cities_list = utils.world_cities_list
        completer = QCompleter(_world_cities_list)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
        self._place_text.textChanged.connect(self._resize_place_text_size)
        self._place_text.editingFinished.connect(lambda : self._get_location(self._place_text.text()))
        self._place_text.setToolTip('Enter place of birth, country name')
        h_layout.addWidget(self._place_text)
        self._lat_label = QLabel("Latidude:")
        h_layout.addWidget(self._lat_label)
        self._lat_text = QLineEdit('')
        self._latitude = 0.0
        self._lat_text.setToolTip('Enter Latitude preferably exact at place of birth: Format: +/- xx.xxx')
        h_layout.addWidget(self._lat_text)
        self._long_label = QLabel("Longitude:")
        h_layout.addWidget(self._long_label)
        self._long_text = QLineEdit('')
        self._longitude = 0.0
        self._long_text.setToolTip('Enter Longitude preferably exact at place of birth. Format +/- xx.xxx')
        h_layout.addWidget(self._long_text)
        self._tz_label = QLabel("Time Zone:")
        h_layout.addWidget(self._tz_label)
        self._tz_text = QLineEdit('')
        self._time_zone = 0.0
        self._tz_text.setToolTip('Enter Time offset from GMT e.g. -5.5 or 4.5')
        h_layout.addWidget(self._tz_text)
        " Initialize with default place based on IP"
        loc = utils.get_place_from_user_ip_address()
        if len(loc)==4:
            self.place(loc[0],loc[1],loc[2],loc[3])
        _show_button = QPushButton('Show')
        _show_button.clicked.connect(self._calculate_results)
        h_layout.addWidget(_show_button)
        self.bird_combo = QComboBox()
        self.bird_combo.addItems([utils.resource_strings[b+'_str'] for b in pancha_pakshi_birds])
        self.bird_combo.setCurrentIndex(birth_bird_index-1)
        h_layout.addWidget(self.bird_combo)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        # Tree Widget
        self.tree = QTreeWidget()
        """
        if headers is not None:
            self.tree.setColumnCount(len(headers))
            self.tree.setHeaderLabels(headers)
        else:
            self.tree.setColumnCount(len(parent_level_list[0]))
        self.tree.setHeaderHidden(hide_headers)
        """
        v_layout.addWidget(self.tree)
        
        # Populate TreeWidget with data
        self.populate_tree(headers,parent_level_list, child_level_list, hide_headers)
        # Connect the itemExpanded signal to the resize_all_columns slot
        #self.tree.itemExpanded.connect(self.resize_all_columns)
        
        # Initial resize to fit columns based on initial content
        #self.resize_all_columns()
    def place(self,place_name,latitude,longitude,timezone_hrs):
        """
            Set the place of birth
            @param - place_name - Specify with country code. e.g. Chennai, IN
            NOTE: Uses Nominatim to get the latitude and longitude
            An error message displayed if lat/long could not be found in which case enter lat/long manually.
            Also NOTE: calling latitude() or longitude() will replace the lat/long values added already
        """
        self._place_name = place_name
        self._latitude = latitude; self._longitude = longitude
        self._time_zone = timezone_hrs
        self._place_text.setText(self._place_name)
        self._lat_text.setText(str(self._latitude))
        self._long_text.setText(str(self._longitude))
        self._tz_text.setText(str(self._time_zone))
    def _resize_place_text_size(self):
        pt = self._place_text.text()
        f = QFont("",0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw,ph)
        self._place_text.adjustSize()
    def _get_location(self,place_name):
        result = utils.get_location(place_name)
        #print('RESULT',result)
        if result:
            self._place_name,self._latitude,self._longitude,self._time_zone = result
            self._place_text.setText(self._place_name)
            self._lat_text.setText(str(self._latitude))
            self._long_text.setText(str(self._longitude))
            self._tz_text.setText(str(self._time_zone))
            #print(self._place_name,self._latitude,self._longitude,self._time_zone)
        else:
            msg = place_name+" could not be found in OpenStreetMap.\nTry entering latitude and longitude manually.\nOr try entering nearest big city"
            print(msg)
            QMessageBox.about(self,"City not found",msg)
            self._lat_text.setText('')
            self._long_text.setText('')
        self._resize_place_text_size()
        #print('leaving _get_location')
        
    def populate_tree(self, headers, parent_level_list, child_level_list,hide_headers):
        self.tree.clear()
        if headers is not None:
            self.tree.setColumnCount(len(headers))
            self.tree.setHeaderLabels(headers)
        else:
            self.tree.setColumnCount(len(parent_level_list[0]))
        self.tree.setHeaderHidden(hide_headers)
        for parent_index, parent_row in enumerate(parent_level_list):
            #parent_item = QTreeWidgetItem([str(cell) for cell in parent_row] + [''] * (self.tree.columnCount() - len(parent_row)))
            parent_item = QTreeWidgetItem()
            self.set_item_icon_and_text(parent_item, parent_row)
            self.tree.addTopLevelItem(parent_item)
            for child_row in child_level_list[parent_index]:
                #child_item = QTreeWidgetItem([str(cell) for cell in child_row] + [''] * (self.tree.columnCount() - len(child_row)))
                child_item = QTreeWidgetItem()
                self.set_item_icon_and_text(child_item, child_row)
                parent_item.addChild(child_item)
        # Connect the itemExpanded signal to the resize_all_columns slot
        self.tree.itemExpanded.connect(self.resize_all_columns)
        
        # Initial resize to fit columns based on initial content
        self.resize_all_columns()
        
    def set_item_icon_and_text(self, item, row):
        for column, cell_value in enumerate(row):
            if isinstance(cell_value,tuple):
                icon_path,text = cell_value
                if icon_path:
                    item.setIcon(column, QIcon(IMAGE_PATH+icon_path))
            else:
                text = cell_value
            item.setText(column, str(text))
    def resize_all_columns(self):
        """Resize columns of the tree widget to fit contents."""
        for column in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(column)
    def _calculate_results(self):
        year,month,day = self._dob_text.text().split(",")
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        jd = utils.julian_day_number(dob, tob)
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        bird_index = self.bird_combo.currentIndex()+1
        headers,top_level_list,child_level_list = _construct_pancha_pakshi_information(dob, tob, place, nakshathra_bird_index=bird_index)
        self.populate_tree(headers, top_level_list, child_level_list,hide_headers=False)


def _get_birth_nakshathra(jd,place):
    return drik.nakshatra(jd, place)[0]
def _get_paksha(jd,place):
    _tithi = drik.tithi(jd, place)[0]
    return 1 if _tithi <= 15 else 2
def _get_birth_bird_from_nakshathra(birth_star,_paksha):
    return pancha_pakshi_stars_birds_paksha[birth_star-1][_paksha-1]
def _get_pancha_paksha_db_row_from_list(bird_index,day_index,paksha_index):
    _p_start = 0 if paksha_index==1 else 10
    _p_end = _p_start + 10
    return pancha_paksha_activity_list[bird_index-1][day_index-1][_p_start:_p_end]
def _create_pancha_paksha_db():
    _pp_db = []
    print('nak_bird_index,week_day_index,paksha_index,daynight_index,main_bird_index,main_activity_index,sub_bird_index,sub_activity_index,duration_factor')
    for nak_bird_index,_day_list in enumerate(pancha_paksha_activity_list):
        for week_day_index,week_day_list in enumerate(_day_list):
            _sp_day_acts = week_day_list[:5]; _sp_night_acts = week_day_list[5:10]
            _kp_day_acts = week_day_list[10:15]; _kp_night_acts = week_day_list[15:20]
            main_bird_index = nak_bird_index
            paksha_index = 0
            daynight_index = 0
            for timestep1_index,main_activity_index in enumerate(_sp_day_acts):
                sub_acts = _sp_day_acts[timestep1_index:]+_sp_day_acts[:timestep1_index]
                sub_bird_index = main_bird_index
                for sub_activity_index in sub_acts:
                    duration_factor = pancha_pakshi_duration_list[daynight_index-1][sub_activity_index-1]
                    print(nak_bird_index,week_day_index,paksha_index,daynight_index,main_bird_index,
                          main_activity_index-1,sub_bird_index,sub_activity_index-1,duration_factor)
                    sub_bird_index = _next_list_item(bird_list,sub_bird_index,dir=1,step=1)
            daynight_index = 1
            for timestep1_index,main_activity_index in enumerate(_sp_night_acts):
                sub_acts = _sp_night_acts[timestep1_index:]+_sp_night_acts[:timestep1_index]
                sub_bird_index = main_bird_index
                for sub_activity_index in sub_acts:
                    duration_factor = pancha_pakshi_duration_list[daynight_index-1][sub_activity_index-1]
                    print(nak_bird_index,week_day_index,paksha_index,daynight_index,main_bird_index,
                          main_activity_index-1,sub_bird_index,sub_activity_index-1,duration_factor)
                    sub_bird_index = _next_list_item(bird_list,sub_bird_index,dir=-1,step=1)
            paksha_index = 1
            daynight_index = 0
            for timestep1_index,main_activity_index in enumerate(_kp_day_acts):
                sub_acts = _kp_day_acts[timestep1_index:]+_kp_day_acts[:timestep1_index]
                sub_bird_index = main_bird_index
                for sub_activity_index in sub_acts:
                    duration_factor = pancha_pakshi_duration_list[daynight_index-1][sub_activity_index-1]
                    print(nak_bird_index,week_day_index,paksha_index,daynight_index,main_bird_index,
                          main_activity_index-1,sub_bird_index,sub_activity_index-1,duration_factor)
                    sub_bird_index = _next_list_item(bird_list,sub_bird_index,dir=1,step=3)
            daynight_index = 1
            for timestep1_index,main_activity_index in enumerate(_kp_night_acts):
                sub_acts = _kp_night_acts[timestep1_index:]+_kp_night_acts[:timestep1_index]
                sub_bird_index = main_bird_index
                for sub_activity_index in sub_acts:
                    duration_factor = pancha_pakshi_duration_list[daynight_index-1][sub_activity_index-1]
                    print(nak_bird_index,week_day_index,paksha_index,daynight_index,main_bird_index,
                          main_activity_index-1,sub_bird_index,sub_activity_index-1,duration_factor)
                    sub_bird_index = _next_list_item(bird_list,sub_bird_index,dir=-1,step=1)
def get_matching_pancha_pakshi_data_from_db(bird_index,weekday_index,paksha_index):
    print('bird_index,weekday_index,paksha_index',bird_index-1,weekday_index-1,paksha_index-1)
    # Open db
    pp_db = pd.read_csv(PP_DB_FILE,header=None,index_col=None, encoding='utf-8',dtype=dtype_dict)
    # Print unique values in columns
    #print("Unique values in NAK_BIRD_INDEX column:", pp_db[_NAK_BIRD_INDEX].unique())
    #print("Unique values in WEEK_DAY_INDEX column:", pp_db[_WEEK_DAY_INDEX].unique())
    #print("Unique values in PAKSHA_INDEX column:", pp_db[_PAKSHA_INDEX].unique())
    # Define the search criteria
    search_criteria = (
        (pp_db[_NAK_BIRD_INDEX] == bird_index - 1) &
        (pp_db[_WEEK_DAY_INDEX] == weekday_index - 1) &
        (pp_db[_PAKSHA_INDEX] == paksha_index - 1)
    )
    # Get the matching rows
    search_results = pp_db[search_criteria]
    # Convert the matching rows to a list of lists and print it
    result_list = search_results.values.tolist()
    #print("Search Results:", result_list)
    return result_list
def _construct_pancha_pakshi_information(dob=None,tob=None,place=None,nakshathra_bird_index=None):
    _DEBUG_ = False
    jd = utils.julian_day_number(dob,tob)
    weekday_index = drik.vaara(jd)+1
    paksha_index = _get_paksha(jd, place)
    sunrise_jd = drik.sunrise(jd, place)[-1]
    day_length = drik.day_length(jd, place)
    night_length = drik.night_length(jd, place)
    day_inc = day_length/5.0; night_inc = night_length/5.0
    if _DEBUG_: print('nakshathra_bird_index',nakshathra_bird_index,'weekday_index',weekday_index,'paksha_index',paksha_index)
    print(utils.resource_strings[pancha_pakshi_birds[nakshathra_bird_index-1]+'_str'],utils.DAYS_LIST[weekday_index-1],utils.PAKSHA_LIST[paksha_index-1])
    if _DEBUG_: print('day_length',day_length,'night_length',night_length,day_inc,night_inc)
    result_list = get_matching_pancha_pakshi_data_from_db(nakshathra_bird_index,weekday_index,paksha_index)
    headers = ['From_Time','To_Time','Duration','Main_Bird','Main_Act','Sub_Bird','Sub_Act','Power_Factor','Effect','Rating']
    top_level_list = []; child_level_list = []
    time_from_jd = sunrise_jd
    for row in range(0,len(result_list),5):
        nbi,wdi,pi,dni,mbi,mai,sbi,sai,df = result_list[row]
        if _DEBUG_: print('row=',row,nbi,wdi,pi,dni,mbi,mai,sbi,sai,df)
        time_inc = day_inc/24 if dni==0 else night_inc/24
        time_to_jd = time_from_jd + time_inc
        by,bm,bd,bfh = utils.jd_to_gregorian(time_from_jd)
        time_from = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh)
        by,bm,bd,bfh = utils.jd_to_gregorian(time_to_jd)
        time_to = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh)
        time_from1 = ('day_sun.png',time_from) if dni==0 else ('moon_with_star.png',time_from)
        duration = str(round(time_inc*24,2))+' '+utils.resource_strings['hours_str']
        main_bird = utils.resource_strings[pancha_pakshi_birds[int(mbi)]+'_str']
        main_bird_image = pancha_pakshi_images[int(mbi)]
        main_act = utils.resource_strings[pancha_pakshi_activities[int(mai)]+'_str']
        main_act_image = pancha_pakshi_activity_images[int(mai)]
        sub_bird = ''; sub_act = ''
        power_factor = ''; effect = ''; rating = ''
        tlist = [time_from1,time_to,duration,(main_bird_image,main_bird),(main_act_image,main_act),sub_bird,sub_act,power_factor,effect,rating]
        if _DEBUG_: print('row',row,tlist)
        top_level_list.append(tlist)
        clist = []
        for irow in range(row,row+5):
            nbi,wdi,pi,dni,mbi,mai,sbi,sai,df = result_list[irow]
            if _DEBUG_: print('c-row=',irow,nbi,wdi,pi,dni,mbi,mai,sbi,sai,df)
            time_inc = day_inc/24 if dni==0 else night_inc/24
            time_to_jd = time_from_jd + time_inc*df
            by,bm,bd,bfh = utils.jd_to_gregorian(time_from_jd)
            time_from = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh)
            by,bm,bd,bfh = utils.jd_to_gregorian(time_to_jd)
            time_to = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh)
            time_from1 = ('day_sun.png',time_from) if dni==0 else ('moon_with_star.png',time_from)
            duration = str(round(df*time_inc*24*60))+' '+utils.resource_strings['minutes_str']
            sub_bird = utils.resource_strings[pancha_pakshi_birds[int(sbi)]+'_str']
            sub_bird_image = pancha_pakshi_images[int(sbi)]
            sub_act = utils.resource_strings[pancha_pakshi_activities[int(sai)]+'_str']
            sub_act_image = pancha_pakshi_activity_images[int(sai)]
            power_factor = ''; effect = ''; rating = ''
            cll = [time_from1,time_to,duration,(main_bird_image,main_bird),(main_act_image,main_act),
                   (sub_bird_image,sub_bird),(sub_act_image,sub_act),power_factor,effect,rating]
            if _DEBUG_: print('c-row',irow,cll)
            clist.append(cll)
            time_from_jd = time_to_jd
        time_from_jd = time_to_jd
        child_level_list.append(clist)
    if _DEBUG_: print(headers)
    if _DEBUG_: print(top_level_list)
    if _DEBUG_: print(child_level_list)
    return headers,top_level_list,child_level_list
if __name__ == "__main__":
    utils.set_language('ta')
    #_create_pancha_paksha_db(); exit()
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    bs = _get_birth_nakshathra(jd, place)
    paksha_index = _get_paksha(jd, place)
    bird_index = _get_birth_bird_from_nakshathra(bs,paksha_index)
    weekday_index = drik.vaara(jd)+1
    print('bird',bird_index,utils.resource_strings[pancha_pakshi_birds[bird_index-1]+'_str'])
    dt = datetime.datetime.now().timetuple()
    dob = dt[0:3]; tob=dt[3:6]
    headers,top_level_list,child_level_list = _construct_pancha_pakshi_information(dob, tob, place, nakshathra_bird_index=bird_index)
    app = QApplication(sys.argv)
    demo = PanchaPakshiSastraWidget(birth_bird_index=bird_index,headers=headers,parent_level_list=top_level_list,child_level_list=child_level_list,
                          hide_headers=False)
    demo.show()
    sys.exit(app.exec())
