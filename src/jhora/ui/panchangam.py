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
import re, sys, os
sys.path.append('../')
""" Get Package Version from _package_info.py """
#import importlib.metadata
#_APP_VERSION = importlib.metadata.version('PyJHora')
#----------
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QStyledItemDelegate, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, \
                            QTextEdit, QLayout, QLabel, QSizePolicy, QLineEdit, QCompleter, QComboBox, \
                            QPushButton, QApplication, QMessageBox, QFileDialog
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTimeZone
from _datetime import datetime
import img2pdf
from PIL import Image
from jhora import const, utils
from jhora.panchanga import drik, pancha_paksha, vratha
vratha.load_festival_data(const._FESTIVAL_FILE)
_available_ayanamsa_modes = [k for k in list(const.available_ayanamsa_modes.keys()) if k not in ['SENTHIL','SIDM_USER']]
_KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'; _HEADER_COLOR='green'
_KEY_LENGTH=100; _VALUE_LENGTH=100; _HEADER_LENGTH=100
_HEADER_FORMAT_ = '<b><span style="color:'+_HEADER_COLOR+';">{:<'+str(_HEADER_LENGTH)+'}</span></b><br>'
_KEY_VALUE_FORMAT_ = '<span style="color:'+_KEY_COLOR+';">{:.'+str(_KEY_LENGTH)+'}'+'  '+'</span><span style="color:'+\
        _VALUE_COLOR+';">{:.'+str(_VALUE_LENGTH)+'}</span><br>'
_images_path = const._IMAGES_PATH
_IMAGES_PER_PDF_PAGE = 2
_IMAGE_ICON_PATH=const._IMAGE_ICON_PATH
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
_SHOW_SPECIAL_TITHIS = True
_SHOW_MUHURTHA_OR_SHUBHA_HORA = 0 # 0=Muhurtha 1=Shubha Hora
_VEDIC_HOURS_PER_DAY = 60 #30 for Mhurthas and 60 for Ghati
_world_city_csv_file = const._world_city_csv_file
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
""" UI Constants """
_main_window_width = 1000#750 #725
_main_window_height = 725#630 #580 #
_main_ui_label_button_font_size = 10#8
#_main_ui_comp_label_font_size = 7
_info_label1_height = 250
_INFO_LABEL_HAS_SCROLL = True
_info_label1_width = 100
_info_label1_font_size = 4.87 if not _INFO_LABEL_HAS_SCROLL else 6#4.87#8
_info_label2_height = _info_label1_height; _info_label3_height = _info_label1_height
_info_label2_width = 100
_info_label2_font_size = 4.87 if not _INFO_LABEL_HAS_SCROLL else 6#4.87# if _SHOW_MUHURTHA_OR_SHUBHA_HORA==0 else 5.9
_info_label3_font_size = 4.87 if not _INFO_LABEL_HAS_SCROLL else 6#4.87#8
_row3_widget_width = 75
_chart_info_label_width = 230#350
_footer_label_font_height = 8
_footer_label_height = 30
_chart_size_factor = 1.35
_tab_names = ['panchangam_str','']
_tab_count = len(_tab_names)
_tabcount_before_chart_tab = 1

available_languages = const.available_languages
_scrollbar_border_size = "1px"; _scrollbar_border_color = "#999999"
# Constants
SCROLLBAR_BORDER_SIZE = "1px"
SCROLLBAR_BORDER_COLOR = "#999999"
SCROLLBAR_BACKGROUND = "#f0f0f0"
SCROLLBAR_WIDTH = "15px"
SCROLLBAR_MARGIN = "0px 0px 0px 0px"

HANDLE_BACKGROUND = "#55aaff"
HANDLE_MIN_HEIGHT = "20px"
HANDLE_BORDER_RADIUS = "5px"

def set_scrollbar_stylesheet(scroll_widget):
    scroll_widget.verticalScrollBar().setStyleSheet(f"""
        QScrollBar:vertical {{
            border: {SCROLLBAR_BORDER_SIZE} solid {SCROLLBAR_BORDER_COLOR}; /* Border around the scrollbar */
            background: {SCROLLBAR_BACKGROUND}; /* Background color of the scrollbar track */
            width: {SCROLLBAR_WIDTH}; /* Width of the scrollbar */
            margin: {SCROLLBAR_MARGIN}; /* Margins around the scrollbar */
        }}

        QScrollBar::handle:vertical {{
            background: {HANDLE_BACKGROUND}; /* Color of the scrollbar thumb (handle) */
            min-height: {HANDLE_MIN_HEIGHT}; /* Minimum height of the thumb */
            border-radius: {HANDLE_BORDER_RADIUS}; /* Rounded corners for the thumb */
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """)
    
class PanchangaInfoDialog(QWidget):
    def __init__(self,language = 'English',jd=None,place:drik.Place=None,ayanamsa_mode=None,
                 info_label1_font_size=_info_label1_font_size, info_label2_font_size=_info_label2_font_size,
                 info_label3_font_size=_info_label3_font_size,
                 info_label_height=_info_label1_height, info_labels_have_scroll=_INFO_LABEL_HAS_SCROLL):
        """
            @param jd: Julian Day Number
            @param place_of_birth: tuple in the format ('place_name',latitude_float,longitude_float,timezone_hrs_float)
                                    e.g. ('Chennai, India',13.0878,80.2785,5.5)
            @param language: One of 'English','Hindi','Tamil','Telugu','Kannada'; Default:English
        """
        super().__init__()
        self.start_jd = jd; self.place = place
        self.info_labels_have_scroll = info_labels_have_scroll
        self._ayanamsa_mode = ayanamsa_mode if ayanamsa_mode is not None else const._DEFAULT_AYANAMSA_MODE
        self._info_label1_font_size=info_label1_font_size; self._info_label2_font_size=info_label2_font_size
        self._info_label3_font_size=info_label3_font_size
        self._info_label1_height = info_label_height; self._info_label2_height = info_label_height
        self._info_label3_height = info_label_height
        self.set_language(language)
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        if self.start_jd is None:
            year,month,day = current_date_str.split(','); dob = drik.Date(int(year),int(month),int(day))
            tob = current_time_str.split(':')
            self.start_jd = utils.julian_day_number(dob, (int(tob[0]),int(tob[1]),int(tob[2])))
        if place == None and const.use_internet_for_location_check:
            loc = utils.get_place_from_user_ip_address()
            print('loc from IP address',loc)
            if len(loc)==4:
                print('setting values from loc')
                self.place= drik.Place(loc[0],loc[1],loc[2],loc[3])
        self.initUI()
        self.update_panchangam_info()
    def set_language(self,language):
        self._language = language; utils.set_language(available_languages[language])
        self.res = utils.resource_strings
    def initUI(self):
        h_layout = QHBoxLayout()
        h_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self._info_label1 = QTextEdit("Information:") if self.info_labels_have_scroll else QLabel("Information:")
        if self.info_labels_have_scroll:
            self._info_label1.setReadOnly(True)        
            self._info_label1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._info_label1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            set_scrollbar_stylesheet(self._info_label1)
        self._info_label1.setMinimumHeight(self._info_label1_height)
        self._info_label1.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label1.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label1_font_size)+'pt')
        _margin = int(_info_label1_font_size)
        self._info_label1.setContentsMargins(_margin,_margin,_margin,_margin)
        h_layout.addWidget(self._info_label1)
        self._info_label2 = QTextEdit("Information:") if self.info_labels_have_scroll else QLabel("Information:")
        if self.info_labels_have_scroll:
            self._info_label2.setReadOnly(True)        
            self._info_label2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._info_label2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            set_scrollbar_stylesheet(self._info_label2)
        self._info_label2.setMinimumHeight(self._info_label2_height)
        self._info_label2.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label2.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label2_font_size)+'pt')
        _margin = int(_info_label2_font_size)
        self._info_label2.setContentsMargins(_margin,_margin,_margin,_margin)
        h_layout.addWidget(self._info_label2)
        self._info_label3 = QTextEdit("Information:") if self.info_labels_have_scroll else QLabel("Information:")
        if self.info_labels_have_scroll:
            self._info_label3.setReadOnly(True)        
            self._info_label3.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._info_label3.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            set_scrollbar_stylesheet(self._info_label3)
        self._info_label3.setMinimumHeight(self._info_label3_height)
        self._info_label3.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label3.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label3_font_size)+'pt')
        _margin = int(_info_label3_font_size)
        self._info_label3.setContentsMargins(_margin,_margin,_margin,_margin)
        h_layout.addWidget(self._info_label3)
        self.setLayout(h_layout)
        self.setWindowTitle(self.res['panchangam_str'])
        self.move(50,50)
    def update_panchangam_info(self,jd=None,place:drik.Place=None,ayanamsa_mode=None):
        try:
            if jd is not None: self.start_jd = jd
            if place is not None: self.place = place
            self._ayanamsa_mode = ayanamsa_mode if ayanamsa_mode is not None else self._ayanamsa_mode
            self._info_label1.clear()
            self._info_label1.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label1_font_size)+'pt')
            self._info_label2.clear()
            self._info_label2.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label2_font_size)+'pt')
            self._info_label3.clear()
            self._info_label3.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label3_font_size)+'pt')
            sep_str = '<br>'
            
            info_list = self._fill_information_label1(show_more_link=False).split(sep_str)
            info_list += self._fill_information_label2().split(sep_str)
            info_list += self._fill_information_label3().split(sep_str)
            info_list = [ele for ele in info_list if ele.strip() != '']
            info_len = int(len(info_list)/3)
            self._info_label1.setText(sep_str.join(info_list[:info_len]))
            self._info_label2.setText(sep_str.join(info_list[info_len:2*info_len]))
            self._info_label3.setText(sep_str.join(info_list[2*info_len:]))
            self.adjustSize()
        except Exception as e:
            print(f"An error occurred: {e}")
    def _fill_information_label1(self,show_more_link=True,jd=None,place=None,ayanamsa_mode=None):
        try:
            jd = self.start_jd if jd is None else jd
            place = self.place if place is None else place
            self._ayanamsa_mode = ayanamsa_mode if ayanamsa_mode is not None else self._ayanamsa_mode
            info_str = ''; format_str = _KEY_VALUE_FORMAT_
            year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
            date_in = drik.Date(year,month,day)
            if jd is None: return
            key = self.res['place_str']+': '; value = place.Place
            _lat = utils.to_dms(float(place.latitude),is_lat_long='lat')
            _long = utils.to_dms(float(place.longitude),is_lat_long='long')
            value += ' ('+_lat+', '+_long+')'
            info_str += format_str.format(key,value)
            key = self.res['vaaram_str']+': '
            value = utils.DAYS_LIST[drik.vaara(jd)]
            info_str += format_str.format(key,value)
            date_str1 = str(year)+','+str(month)+','+str(day)
            date_str2 = str(year)+' '+utils.MONTH_LIST_EN[month-1]+' '+str(day)
            key = self.res['date_of_birth_str']; value = date_str2+'  '+self.res['time_of_birth_str']+' '+utils.to_dms(birth_time_hrs)
            info_str += format_str.format(key,value)
            keys = [self.res['solar_str']+' '+self.res['year_str']+'/'+self.res['month_str'],self.res['lunar_year_month_str'],self.res['lunar_year_month_str']]
            _calendar_type_str = ['',' ('+self.res['amantha_str']+')',' ('+self.res['purnimantha_str']+')']
            for _calendar_type in range(3):
                _month,_day,_year,adhik_maasa,nija_maasa = drik.vedic_date(jd, place, calendar_type=_calendar_type)
                adhik_maasa_str = ''; nija_month_str = ''
                if adhik_maasa: adhik_maasa_str = self.res['adhika_maasa_str']
                if nija_maasa: nija_month_str = self.res['nija_month_str']
                spl_month_text = utils.MONTH_LIST[_month-1]+' '+ adhik_maasa_str+nija_month_str+' '+str(_day)
                year_str = utils.YEAR_LIST[_year]
                key = keys[_calendar_type]
                value = utils.YEAR_LIST[_year]+' / '+utils.MONTH_LIST[_month-1]+' '+ \
                                adhik_maasa_str+nija_month_str+' '+str(_day)
                value += _calendar_type_str[_calendar_type]
                info_str += format_str.format(key,value)
            key = self.res['sunrise_str']
            value = drik.sunrise(jd,place)[1]
            info_str += format_str.format(key,value)
            key = self.res['sunset_str']
            value = drik.sunset(jd,place)[1]
            info_str += format_str.format(key,value)
            key = self.res['moonrise_str']
            value = drik.moonrise(jd, place)[1]
            info_str += format_str.format(key,value)
            key = self.res['moonset_str']
            value = drik.moonset(jd, place)[1]
            info_str += format_str.format(key,value)        
            #"""
            _festival_list = vratha.get_festivals_of_the_day(jd,place)
            if len(_festival_list)>0:
                info_str += format_str.format(self.res['todays_festivals_str'],'')
                for row in _festival_list:
                    info_str += format_str.format('\t',row['Festival_'+const.available_languages[self._language]])
            #"""
            key = self.res['nakshatra_str']
            nak = drik.nakshatra(jd,place)
            frac_left = 100*utils.get_fraction(nak[2], nak[3], birth_time_hrs)
            frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + self.res['balance_str']+' )'
            value = utils.NAKSHATRA_LIST[nak[0]-1]+' '+  \
                        ' ('+utils.PLANET_SHORT_NAMES[utils.nakshathra_lord(nak[0])]+') '+ self.res['paadham_str']+\
                        str(nak[1]) + ' '+ utils.to_dms(nak[3]) + ' ' + self.res['ends_at_str']+frac_str
            info_str += format_str.format(key,value)
            if nak[3] < 24:
                _next_nak = (nak[0])%27+1
                value = utils.NAKSHATRA_LIST[_next_nak-1]+' '+  \
                            ' ('+utils.PLANET_SHORT_NAMES[utils.nakshathra_lord(_next_nak)]+') '+ \
                            ' '+ utils.to_dms(nak[3]) + ' ' + self.res['starts_at_str']
                info_str += format_str.format(key,value)
            key = self.res['raasi_str']
            rasi = drik.raasi(jd,place)
            frac_left = rasi[2]*100
            frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + self.res['balance_str']+' )'
            value = utils.RAASI_LIST[rasi[0]-1]+' '+utils.to_dms(rasi[1])+ ' ' + self.res['ends_at_str']+frac_str
            info_str += format_str.format(key,value)
            if rasi[1] < 24:
                _next_rasi = (rasi[0])%12+1
                value = utils.RAASI_LIST[_next_rasi-1]+' '+utils.to_dms(rasi[1])+ ' ' + self.res['starts_at_str']
                info_str += format_str.format(key,value)
            st = drik.special_tithis(jd,place)[:12]
            if _SHOW_SPECIAL_TITHIS:
                for t in range(1,13):
                    _tithi_returned = st[0][t-1]
                    frac_left = 100*utils.get_fraction(_tithi_returned[1], _tithi_returned[2], birth_time_hrs)
                    frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + self.res['balance_str']+' )'
                    _paksha = 0 if _tithi_returned[0]<=15 else 1
                    key = self.res[const.special_tithis[t-1]+'_tithi_str']
                    _deity_str= ' (' + utils.TITHI_DEITIES[_tithi_returned[0]-1]+') '
                    from_str = utils.to_dms(_tithi_returned[1])+' '+self.res['starts_at_str']
                    end_str = utils.to_dms(_tithi_returned[2])+' '+self.res['ends_at_str']
                    value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi_returned[0]-1]
                    value += _deity_str+from_str+' '+end_str+' '+frac_str
                    info_str += format_str.format(key,value)
                    #"""
                    if _tithi_returned[2] < 24:
                        _paksha = 0
                        if (_tithi_returned[0])%30+1 > 15: _paksha = 1 # V3.1.1
                        value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[(_tithi_returned[0])%30]+ \
                                        ' (' + utils.TITHI_DEITIES[(_tithi_returned[0])%30]+') '+ \
                                        utils.to_dms(_tithi_returned[2])+ ' ' + self.res['starts_at_str']
                        info_str += format_str.format(key,value)
                    #"""
            else:
                key = self.res['tithi_str']; _tithi = drik.tithi(jd, place)
                frac_left = 100*utils.get_fraction(_tithi[1], _tithi[2], birth_time_hrs)
                frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + self.res['balance_str']+' )'
                _paksha = 0
                if _tithi[0] > 15: _paksha = 1 # V3.1.1
                value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi[0]-1]+ \
                                ' (' + utils.TITHI_DEITIES[_tithi[0]-1]+') '+ \
                                utils.to_dms(_tithi[2])+ ' ' + self.res['ends_at_str']+frac_str
                info_str += format_str.format(key,value)
                if _tithi[2] < 24:
                    key = self.res['tithi_str']
                    _paksha = 0
                    if (_tithi[0])%30+1 > 15: _paksha = 1 # V3.1.1
                    value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[(_tithi[0])%30]+ \
                                    ' (' + utils.TITHI_DEITIES[(_tithi[0])%30]+') '+ \
                                    utils.to_dms(_tithi[2])+ ' ' + self.res['starts_at_str']
                    info_str += format_str.format(key,value)
            key = self.res['yogam_str']
            yogam = drik.yogam(jd,place)
            frac_left = 100*utils.get_fraction(yogam[1], yogam[2], birth_time_hrs)
            frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + self.res['balance_str']+' )'
            yoga_lord = ' ('+utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[yogam[0]-1][0]]+'/'+\
                            utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[yogam[0]-1][1]]+') '
            value = utils.YOGAM_LIST[yogam[0]-1] + yoga_lord + '  '+ \
                                utils.to_dms(yogam[2])+ ' ' + self.res['ends_at_str']+frac_str
            info_str += format_str.format(key,value)
            if yogam[2] < 24:
                yoga_lord = ' ('+utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[(yogam[0])%27][0]]+'/'+\
                                utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[(yogam[0])%27][1]]+') '
                value = utils.YOGAM_LIST[(yogam[0])%27] + yoga_lord + '  '+ \
                                    utils.to_dms(yogam[2])+ ' ' + self.res['starts_at_str']
                info_str += format_str.format(key,value)
            key = self.res['karanam_str']
            karanam = drik.karana(jd,place)
            karana_lord = utils.PLANET_SHORT_NAMES[utils.karana_lord(karanam[0])]
            frac_left = 100*utils.get_fraction(karanam[1], karanam[2], birth_time_hrs)
            frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + self.res['balance_str']+' )'
            value = utils.KARANA_LIST[karanam[0]-1]+' ('+ karana_lord +') '+utils.to_dms(karanam[1])+' '+ \
                    self.res['starts_at_str']+ ' ' +utils.to_dms(karanam[2])+ ' ' + self.res['ends_at_str']+frac_str
            info_str += format_str.format(key,value)
            if karanam[2] < 24:
                _next_karana = karanam[0]%60+1
                karana_lord = utils.PLANET_SHORT_NAMES[utils.karana_lord(_next_karana)]
                value = utils.KARANA_LIST[_next_karana-1]+' ('+ karana_lord +') '+\
                                utils.to_dms(karanam[2])+ ' ' + self.res['starts_at_str']
                info_str += format_str.format(key,value)
            key = self.res['raahu_kaalam_str']
            _raahu_kaalam = drik.raahu_kaalam(jd,place)
            value = _raahu_kaalam[0] + ' '+ self.res['starts_at_str']+' '+ _raahu_kaalam[1]+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            kuligai = drik.gulikai_kaalam(jd,place)
            key = self.res['kuligai_str']
            value = kuligai[0] + ' '+ self.res['starts_at_str']+' '+ kuligai[1]+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            yamagandam = drik.yamaganda_kaalam(jd,place)
            key = self.res['yamagandam_str'] 
            value = yamagandam[0] + ' '+ self.res['starts_at_str']+' '+ yamagandam[1]+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            abhijit = drik.abhijit_muhurta(jd,place)
            key = self.res['abhijit_str']
            value = abhijit[0] + ' '+ self.res['starts_at_str']+' '+ abhijit[1]+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            _dhurmuhurtham = drik.durmuhurtam(jd,place)
            key = self.res['dhurmuhurtham_str']
            value = _dhurmuhurtham[0] + ' '+ self.res['starts_at_str']+' '+ _dhurmuhurtham[1]+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            nm = drik.nishita_muhurtha(jd, place)
            key = self.res['nishitha_muhurtha_str']+' : '
            value = utils.to_dms(nm[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob=utils.to_dms(fh,as_string=False)
            scd = drik.sahasra_chandrodayam(jd, place)
            if scd is not None:
                key = self.res['sahasra_chandrodhayam_str']+' '+self.res['day_str']
                value = str(scd[0])+'-'+'{:02d}'.format(scd[1])+'-'+'{:02d}'.format(scd[2])\
                        #+' '+'{:02d}'.format(scd[3])+':'+'{:02d}'.format(scd[4])+':'+'{:02d}'.format(scd[5])
                info_str += format_str.format(key,value) #'%-40s%-40s\n' % (key,value)        
            ag = drik.amrita_gadiya(jd, place)
            key = self.res['amritha_gadiya_str']
            value = utils.to_dms(ag[0])+' '+self.res['starts_at_str']+' '+utils.to_dms(ag[1])+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)        
            ag = drik.varjyam(jd, place)
            key = self.res['varjyam_str']
            value = utils.to_dms(ag[0])+' '+self.res['starts_at_str']+' '+utils.to_dms(ag[1])+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)        
            if len(ag)>2:
                value += '&nbsp;&nbsp;'+utils.to_dms(ag[2])+' '+self.res['starts_at_str']+' '+utils.to_dms(ag[3])+' '+self.res['ends_at_str']
            ay = drik.anandhaadhi_yoga(jd, place)
            key = self.res['anandhaadhi_yoga_str']
            value = self.res['ay_'+const.anandhaadhi_yoga_names[ay[0]]+'_str']+' '+utils.to_dms(ay[1])+' '+self.res['starts_at_str']
            info_str += format_str.format(key,value)
            key = self.res['day_length_str']
            _day_length = drik.day_length(jd, place)
            value = utils.to_dms(_day_length).replace(' AM','').replace(' PM','')+' '+self.res['hours_str']
            info_str += format_str.format(key,value)
            key = self.res['night_length_str']
            _night_length = drik.night_length(jd, place)
            value = utils.to_dms(_night_length).replace(' AM','').replace(' PM','')+' '+self.res['hours_str']
            info_str += format_str.format(key,value)
            key = self.res['present_str']+' '+self.res['triguna_str']
            tg = drik.triguna(jd, place)
            value = self.res[const.triguna_names[tg[0]]+'_str']
            value += '&nbsp;&nbsp;'+utils.to_dms(tg[1])+' '+self.res['starts_at_str']+' '+utils.to_dms(tg[2])+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['present_str']+' '+self.res['vivaha_chakra_palan']+' :'
            value = drik.vivaha_chakra_palan(jd, place)
            value = self.res['vivaha_chakra_palan_'+str(value)]
            info_str += format_str.format(key,value)
            key = self.res['tamil_yogam_str']+' : '
            tg = drik.tamil_yogam(jd, place)
            value = self.res[const.tamil_yoga_names[tg[0]]+'_yogam_str']
            value += ' ('+self.res[const.tamil_yoga_names[tg[3]]+'_yogam_str']+')' if len(tg)>3 and tg[0] != tg[3] else '' 
            value += '&nbsp;&nbsp;'+utils.to_dms(tg[1])+' '+self.res['starts_at_str']+' '+utils.to_dms(tg[2])+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            value = drik.pushkara_yoga(jd, place)
            if len(value)>0:
                key = self.res['dwi_pushkara_yoga_str'] if value[0]==1 else self.res['tri_pushkara_yoga_str']
                value = utils.to_dms(value[1])+' '+self.res['starts_at_str']
                info_str += format_str.format(key,value)
            value = drik.aadal_yoga(jd, place)
            if len(value)>0:
                key = self.res['aadal_yoga_str']
                value = utils.to_dms(value[0])+' '+self.res['starts_at_str']+' '+utils.to_dms(value[1])+' '+self.res['ends_at_str']
                info_str += format_str.format(key,value)
            value = drik.vidaal_yoga(jd, place)
            if len(value)>0:
                key = self.res['vidaal_yoga_str']
                value = utils.to_dms(value[0])+' '+self.res['starts_at_str']+' '+utils.to_dms(value[1])+' '+self.res['ends_at_str']
                info_str += format_str.format(key,value)
            key = self.res['shiva_vaasa_str']
            sv = drik.shiva_vaasa(jd, place)
            value = self.res['shiva_vaasa_str'+str(sv[0])]+' '+utils.to_dms(sv[1])+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['agni_vaasa_str']
            av = drik.agni_vaasa(jd, place)
            value = self.res['agni_vaasa_str'+str(av[0])]+' '+utils.to_dms(av[1])+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            directions = ['east','south','west','north','south_west','north_west','north_east','south_east']
            yv = drik.yogini_vaasa(jd, place)
            key = self.res['yogini_vaasa_str']; value = self.res[directions[yv]+'_str']
            info_str += format_str.format(key,value)
            ds = drik.disha_shool(jd)
            key = self.res['disha_shool_str']; value = self.res[directions[ds]+'_str']
            info_str += format_str.format(key,value)
            car,ca_jd = drik.chandrashtama(jd, place); key = self.res['chandrashtamam_str']
            value = utils.RAASI_LIST[car-1]+' '+utils.julian_day_to_date_time_string(ca_jd)+' '+self.res['ends_at_str']
            #"""
            key = self.res['ayanamsam_str']+' ('+self._ayanamsa_mode+') '
            value = drik.get_ayanamsa_value(jd)
            value = utils.to_dms(value,as_string=True,is_lat_long='lat').replace('N','').replace('S','')
            info_str += format_str.format(key,value)
            #"""
            paksha_index = _paksha+1
            bird_index = pancha_paksha._get_birth_bird_from_nakshathra(nak[0],paksha_index)
            key = self.res['pancha_pakshi_sastra_str']+' '+self.res['main_bird_str'].replace('\\n',' ')+' : '
            value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
            info_str += format_str.format(key,value)
            [kali_year, vikrama_year,saka_year] = drik.elapsed_year(jd,_month)
            key = self.res['kali_year_str']
            key_str = '<span style="color:'+_KEY_COLOR+';">'+key+'</span>'+' '
            value = '<span style="color:'+_VALUE_COLOR+';">'+str(kali_year)+'</span>'+ ' '
            info_str += key_str+value
            key = self.res['vikrama_year_str']
            key_str = '<span style="color:'+_KEY_COLOR+';">'+key+'</span>'+' '
            value = '<span style="color:'+_VALUE_COLOR+';">'+str(vikrama_year)+'</span>'+ ' '
            info_str += key_str+value
            key = self.res['saka_year_str']; value = str(saka_year)
            info_str += format_str.format(key,value)
            key = self.res['kali_ahargana_str']
            value = str(drik.kali_ahargana_days(jd))+' '+self.res['days_str']
            info_str += format_str.format(key,value)
            if show_more_link:
                info_str += format_str.format('<a href="show_more">Show more</a>','')
                self._info_label1.linkActivated.connect(lambda link: self._on_show_more_link_clicked(link, jd, place))
            return info_str
        except Exception as e:
            tb = sys.exc_info()[2]
            print(f"PanchangaInfoDialog - An error occurred: {e}",'line number',tb.tb_lineno)
    def _fill_information_label2(self):
        try:
            jd = self.start_jd; place = self.place
            format_str = _KEY_VALUE_FORMAT_
            header = _HEADER_FORMAT_
            info_str = ''
            car,ca_jd = drik.chandrashtama(jd, place); key = self.res['chandrashtamam_str']
            value = utils.RAASI_LIST[car-1]+' '+utils.julian_day_to_date_time_string(ca_jd)+' '+self.res['ends_at_str']
            info_str += format_str.format(key,value)
            info_str += header.format(self.res['daytime_str']+' '+self.res['gauri_choghadiya_str']+':')
            gc = drik.gauri_choghadiya(jd, place)
            _gc_types = ['gc_udvega_str','gc_chara_str','gc_laabha_str','gc_amrit_str','gc_kaala_str','gc_shubha_str','gc_roga_str']
            for g,(gt,st,et) in enumerate(gc):
                if g==8: # V4.3.6
                    info_str += header.format(self.res['nighttime_str']+' '+self.res['gauri_choghadiya_str']+':')
                key = '&nbsp;&nbsp;'+self.res[_gc_types[gt]]
                value = st +' '+self.res['starts_at_str']+ ' '+ et + ' '+ self.res['ends_at_str']
                info_str += format_str.format(key,value)
            #if _SHOW_MUHURTHA_OR_SHUBHA_HORA==0:
            info_str += header.format(self.res['daytime_str']+' '+self.res['muhurtha_str']+':')
            mh = drik.muhurthas(jd, place)
            for mi,(mn,ma,(ms,me)) in enumerate(mh):
                if mi==15: info_str += header.format(self.res['nighttime_str']+' '+self.res['muhurtha_str']+':')
                key = '&nbsp;&nbsp;'+utils.resource_strings['muhurtha_'+mn+'_str']+ ' ('
                key += utils.resource_strings['auspicious_str'] if ma==1 else utils.resource_strings["inauspicious_str"]
                key += ') '
                value = utils.to_dms(ms)+' '+self.res['starts_at_str']+ ' '+ utils.to_dms(me) + ' '+ self.res['ends_at_str']
                info_str += format_str.format(key,value)
            #else:
            info_str += header.format(self.res['daytime_str']+' '+self.res['shubha_hora_str']+':')
            gc = drik.shubha_hora(jd, place)
            for g,(gt,st,et) in enumerate(gc):
                #if g == 12: break
                if g==12: info_str += header.format(self.res['nighttime_str']+' '+self.res['shubha_hora_str']+':')
                key = '&nbsp;&nbsp;'+utils.PLANET_NAMES[gt]+' '+self.res['shubha_hora_'+str(gt)]
                value = st +' '+self.res['starts_at_str']+ ' '+ et + ' '+ self.res['ends_at_str']
                info_str += format_str.format(key,value)
            bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
            self.panchaka_rahitha = drik.panchaka_rahitha(jd, place)
            info_str += header.format(self.res['panchaka_rahitha_str']+' :')
            for prc,pr_beg,pr_end in self.panchaka_rahitha[:1]:
                key=self.res['muhurtha_str']+' ('+self.res['good_str']+') ' if prc==0 \
                        else self.res[bad_panchakas[prc]+'_panchaka_str']
                value1 = utils.to_dms(pr_beg)+' '+utils.resource_strings['starts_at_str']
                value2 = utils.to_dms(pr_end)+' '+utils.resource_strings['ends_at_str']
                info_str += format_str.format(key,value1+' '+value2)
            return info_str
        except Exception as e:
            print(f"An error occurred: {e}")
    def _fill_information_label3(self):
        try:
            jd = self.start_jd; place = self.place
            header = _HEADER_FORMAT_
            format_str = _KEY_VALUE_FORMAT_
            info_str = ''
            bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
            for prc,pr_beg,pr_end in self.panchaka_rahitha[1:]:
                key=self.res['muhurtha_str']+' ('+self.res['good_str']+') ' if prc==0 \
                        else self.res[bad_panchakas[prc]+'_panchaka_str']
                value1 = utils.to_dms(pr_beg)+' '+utils.resource_strings['starts_at_str']
                value2 = utils.to_dms(pr_end)+' '+utils.resource_strings['ends_at_str']
                info_str += format_str.format(key,value1+' '+value2)
            tb = drik.thaaraabalam(jd, place, return_only_good_stars=True)
            info_str += header.format(self.res['thaaraabalam_str']+' :')
            star_list = [utils.NAKSHATRA_LIST[t-1] for t in tb]; knt=6
            star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
            for sl in star_list:
                info_str += format_str.format('',sl)
            cb = drik.chandrabalam(jd, place)
            info_str += header.format(self.res['chandrabalam_str']+' :')
            star_list = [utils.RAASI_LIST[t-1] for t in cb]; knt=5
            star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
            for sl in star_list:
                info_str += format_str.format('',sl)
            bm = drik.brahma_muhurtha(jd, place)
            key = self.res['brahma_str']+' '+self.res['muhurtha_str']+' : '
            value = utils.to_dms(bm[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(bm[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            bm = drik.godhuli_muhurtha(jd, place)
            key = self.res['godhuli_muhurtha_str']+' : '
            value = utils.to_dms(bm[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(bm[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            ps,ms,ss = drik.sandhya_periods(jd, place)
            key = self.res['pratah_sandhya_kaalam_str']+' : '
            value = utils.to_dms(ps[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(ps[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['madhyaahna_sandhya_kaalam_str']+' : '
            value = utils.to_dms(ms[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(ms[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['saayam_sandhya_kaalam_str']+' : '
            value = utils.to_dms(ss[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(ss[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            nm = drik.nishita_kaala(jd, place)
            key = self.res['nishitha_kaala_str']+' : '
            value = utils.to_dms(nm[0]) +' '+self.res['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ self.res['ends_at_str']
            info_str += format_str.format(key,value)
            ulm = drik.udhaya_lagna_muhurtha(jd, place)
            info_str += header.format(self.res['udhaya_lagna_str']+':')
            for ulr,ulb,ule in ulm:
                key = '&nbsp;&nbsp;'+utils.RAASI_LIST[ulr]+' : '
                ulb_str = utils.to_dms(ulb); ule_str=utils.to_dms(ule)
                value = ulb_str +' '+self.res['starts_at_str']+ ' '+ ule_str + ' '+ self.res['ends_at_str']
                info_str += format_str.format(key,value)
            bs = pancha_paksha._get_birth_nakshathra(jd, place)
            paksha_index = pancha_paksha._get_paksha(jd, place)
            bird_index = pancha_paksha._get_birth_bird_from_nakshathra(bs,paksha_index)
            key = self.res['pancha_pakshi_sastra_str']+' '+self.res['main_bird_str'].replace('\\n',' ')+' : '
            value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
            info_str += format_str.format(key,value)
            key = self.res['karaka_str']+' '+self.res['tithi_str']
            kt = drik.karaka_tithi(jd, place)
            key_str = '<span style="color:'+_KEY_COLOR+';">'+key+'</span>'+' '
            _paksha = utils.PAKSHA_LIST[0] if kt[0]-1 <15 else utils.PAKSHA_LIST[1]
            value = _paksha +' '+utils.TITHI_LIST[kt[0]-1]; _t_deity = utils.TITHI_DEITIES[kt[0]-1]
            value_str='<span style="color:'+_VALUE_COLOR+';">'+str(value)+'</span>'+ ' '
            info_str += key_str+' '+value_str#format_str.format(key,value)
            key = self.res['karaka_str']+' '+self.res['yogam_str']
            key_str = '<span style="color:'+_KEY_COLOR+';">'+key+'</span>'+' '
            ky = drik.karaka_yogam(jd, place)
            value = utils.YOGAM_LIST[ky[0]-1]
            value_str='<span style="color:'+_VALUE_COLOR+';">'+str(value)+'</span>'+ ' '
            info_str += key_str+' '+value_str
            return info_str
        except Exception as e:
            print(f"An error occurred: {e}")

class PanchangaWidget(QWidget):
    def __init__(self,calculation_type:str='drik',language = 'English',date_of_birth=None,time_of_birth=None,
                 place_of_birth=None,show_vedic_digital_clock=False,show_local_clock=False,
                 show_vedic_analog_clock=False,use_world_city_database=const.check_database_for_world_cities,
                 use_internet_for_location_check=const.use_internet_for_location_check):
        """
            @param date_of_birth: string in the format 'yyyy,m,d' e.g. '2024,1,1'  or '2024,01,01'
            @param place_of_birth: tuple in the format ('place_name',latitude_float,longitude_float,timezone_hrs_float)
                                    e.g. ('Chennai, India',13.0878,80.2785,5.5)
            @param language: One of 'English','Hindi','Tamil','Telugu','Kannada'; Default:English
        """
        super().__init__()
        self.show_vedic_digital_clock = show_vedic_digital_clock
        self.show_vedic_analog_clock = show_vedic_analog_clock and show_vedic_digital_clock
        self.show_local_clock = show_local_clock
        self._horo = None
        self._language = language; utils.set_language(available_languages[language])
        self.use_world_city_database = use_world_city_database
        utils.use_database_for_world_cities(self.use_world_city_database)
        self.use_internet_for_location_check = use_internet_for_location_check
        self.resources = utils.resource_strings
        self._calculation_type = calculation_type
        ' read world cities'
        #self._df = utils._world_city_db_df
        #self._world_cities_db = utils.world_cities_db
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self._init_main_window()
        self._v_layout = QVBoxLayout()
        self._create_row1_ui()
        self._create_row_2_ui()
        self._init_tab_widget_ui()
        if date_of_birth == None:
            self.date_of_birth(current_date_str)
        if time_of_birth == None:
            self.time_of_birth(current_time_str)
        #"""
        if place_of_birth == None and self.use_internet_for_location_check:
            loc = utils.get_place_from_user_ip_address()
            print('loc from IP address',loc)
            if len(loc)==4:
                print('setting values from loc')
                self.place(loc[0],loc[1],loc[2],loc[3])
        #"""
        year,month,day = self._dob_text.text().split(",")
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        self._birth_julian_day = utils.julian_day_number(dob, tob)
        """ Commented in V4.0.4 to force explicit calling """
        #self.compute_horoscope(calculation_type=self._calculation_type)    
    def _hide_2nd_row_widgets(self,show=True):
            self._dob_label.setVisible(show)
            self._dob_text.setVisible(show)
            self._tob_label.setVisible(show)
            self._tob_text.setVisible(show)
            self._ayanamsa_combo.setVisible(show)
    def _init_tab_widget_ui(self):
        self.tabNames = _tab_names
        self.tabWidget = QTabWidget()
        self.horo_tabs = []
        self._v_layout.addWidget(self.tabWidget)
        self.tabCount = len(self.tabNames)
        t = 0
        self._init_panchanga_tab_widgets(t)
        if self.show_vedic_digital_clock or self.show_local_clock:
            t+=1; self._init_clock_tab(t)
        self.tabCount = self.tabWidget.count()
        self._add_footer_to_chart()
        self.setLayout(self._v_layout)        
    def _init_clock_tab(self,tab_index):
        #self.horo_tabs.append(QWidget())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_clock_tab_text)
        self.timer.start(1000)
        if self.show_vedic_analog_clock:
            from jhora.ui.vedic_clock import VedicAnalogClock
            self._vedic_analog_clock = VedicAnalogClock()
            self.horo_tabs.append(self._vedic_analog_clock)
            self.tabWidget.addTab(self.horo_tabs[tab_index],'Clock')
            self.tabWidget.tabBar().setTabEnabled(1, True)
        else:
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index],'Clock')
            # Ensure the second tab cannot be selected
            self.tabWidget.tabBar().setTabEnabled(1, False)
    def _update_clock_tab_text(self):
        jd = self.julian_day; place = self.place
        current_datetime = QDateTime.currentDateTime()
        local_time_zone_hours = place.timezone
        time_zone = QTimeZone(int(local_time_zone_hours * 3600))
        current_datetime = current_datetime.toTimeZone(time_zone)
        current_time = current_datetime.time().hour() + current_datetime.time().minute() / 60 + current_datetime.time().second() / 3600
        local_time = ''
        if self.show_local_clock:
            lc = self.resources['present_str']+' '+ f"{self.resources['time_of_birth_str']} "
            local_time = lc + current_datetime.time().toString("HH:mm:ss")+' / '
        vedic_time = drik.float_hours_to_vedic_time(jd, place, current_time,vedic_hours_per_day=_VEDIC_HOURS_PER_DAY)
        vc1 = self.resources['vedic_clock_str']+' '
        vc = vc1+f"{self.resources['ghati_str']}:{self.resources['pala_str']}:{self.resources['vighati_str']} "
        vedic_time_str = local_time + vc + f"{vedic_time[0]:02}:{vedic_time[1]:02}:{vedic_time[2]:02}"
        self.tabWidget.setTabText(1, vedic_time_str)
        self.tabWidget.tabBar().setStyleSheet("QTabBar::tab { color: green; font-weight: bold; }")
    def _init_panchanga_tab_widgets(self,tab_index):
        self.panchanga_info_dialog = PanchangaInfoDialog(language=self._language,ayanamsa_mode=self._ayanamsa_mode,
                                                         info_label1_font_size=_info_label1_font_size,
                                                         info_label2_font_size=_info_label2_font_size,
                                                         info_label3_font_size=_info_label3_font_size,
                                                         info_label_height=_info_label1_height)
        self.horo_tabs.append(self.panchanga_info_dialog)
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        return
    def _init_main_window(self):
        self._footer_title = ''
        self.setWindowIcon(QtGui.QIcon(_IMAGE_ICON_PATH))
        self._language = list(available_languages.keys())[0]#list(available_languages.keys())[0]
        self.setFixedSize(_main_window_width,_main_window_height)
        self.showMaximized()
        #self.setMinimumSize(_main_window_width,_main_window_height)        
    def _create_row1_ui(self):
        self._row1_h_layout = QHBoxLayout()
        self._dob_label = QLabel("Date of Birth:")
        self._row1_h_layout.addWidget(self._dob_label)
        self._date_of_birth = ''
        self._dob_text = QLineEdit(self._date_of_birth)
        self._dob_text.setToolTip('Date of birth in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        self._dob_label.setMaximumWidth(_row3_widget_width)
        self._dob_text.setMaximumWidth(_row3_widget_width)
        self._row1_h_layout.addWidget(self._dob_text)
        self._tob_label = QLabel("Time of Birth:")
        self._row1_h_layout.addWidget(self._tob_label)
        self._time_of_birth = ''
        self._tob_text = QLineEdit(self._time_of_birth)
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        self._tob_label.setMaximumWidth(_row3_widget_width)
        self._tob_text.setMaximumWidth(_row3_widget_width)
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self.date_of_birth(current_date_str)
        self.time_of_birth(current_time_str)
        self._row1_h_layout.addWidget(self._tob_text)
        self._place_label = QLabel("Place:")
        self._row1_h_layout.addWidget(self._place_label)
        self._place_name = ''
        self._place_text = QLineEdit(self._place_name)
        completer = QCompleter(utils.world_cities_dict.keys())
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
        self._place_text.textChanged.connect(self._resize_place_text_size)
        self._place_text.editingFinished.connect(lambda : self._get_location(self._place_text.text()))
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
        self._long_text = QLineEdit('')
        self._longitude = 0.0
        self._long_text.setToolTip('Enter Longitude preferably exact at place of birth. Format +/- xx.xxx')
        self._row1_h_layout.addWidget(self._long_text)
        self._tz_label = QLabel("Time Zone:")
        self._row1_h_layout.addWidget(self._tz_label)
        self._tz_text = QLineEdit('')
        self._time_zone = 0.0
        self._tz_text.setToolTip('Enter Time offset from GMT e.g. -5.5 or 4.5')
        self._row1_h_layout.addWidget(self._tz_text)
        self._v_layout.addLayout(self._row1_h_layout)
    def _create_row_2_ui(self):
        self._row2_h_layout = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.activated.connect(self._update_main_window_label_and_tooltips)
        self._row2_h_layout.addWidget(self._lang_combo)
        self._ayanamsa_combo = QComboBox()
        self._ayanamsa_combo.addItems(_available_ayanamsa_modes)
        self._ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        self._ayanamsa_combo.setCurrentText(self._ayanamsa_mode)
        self._ayanamsa_combo.activated.connect(self._ayanamsa_selection_changed)
        self._ayanamsa_combo.setToolTip('Choose Ayanamsa mode from the list')
        self._ayanamsa_value = None
        self._row2_h_layout.addWidget(self._ayanamsa_combo)
        self._compute_button = QPushButton("Show Chart")
        self._compute_button.setFont(QtGui.QFont("Arial Bold",9))
        self._compute_button.clicked.connect(lambda: self.compute_horoscope(calculation_type=self._calculation_type))
        self._compute_button.setToolTip('Click to update the chart information based on selections made')
        self._row2_h_layout.addWidget(self._compute_button)
        self._save_image_button = QPushButton("Save as PDF")
        self._save_image_button.setFont(QtGui.QFont("Arial Bold",8))
        self._save_image_button.clicked.connect(lambda : self.save_as_pdf(pdf_file_name=None))
        self._save_image_button.setToolTip('Click to save horoscope as a PDF')
        self._row2_h_layout.addWidget(self._save_image_button)
        self._save_city_button = QPushButton("Save City")
        self._save_city_button.clicked.connect(self._save_city_to_database)
        self._save_city_button.setToolTip('Click to save the city information in csv database')
        self._row2_h_layout.addWidget(self._save_city_button)
        self._v_layout.addLayout(self._row2_h_layout)
    def _add_footer_to_chart(self):
        self._footer_label = QLabel('')
        self._footer_label.setTextFormat(Qt.TextFormat.RichText)
        self._footer_label.setText(self._footer_title)
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
    def _ayanamsa_selection_changed(self):
        self._ayanamsa_mode = self._ayanamsa_combo.currentText().upper()
        drik.set_ayanamsa_mode(self._ayanamsa_mode,jd=self.julian_day) if self._ayanamsa_mode.upper()=='SUNDAR_SS' else drik.set_ayanamsa_mode(self._ayanamsa_mode)
        const._DEFAULT_AYANAMSA_MODE = self._ayanamsa_mode
    def ayanamsa_mode(self, ayanamsa_mode, ayanamsa=None):
        """
            Set Ayanamsa mode
            @param ayanamsa_mode - Default - Lahiri
            See 'drik.available_ayanamsa_modes' for the list of available models
        """
        if ayanamsa_mode.upper() in const.available_ayanamsa_modes.keys():
            self._ayanamsa_mode = ayanamsa_mode
            self._ayanamsa_value = ayanamsa
            self._ayanamsa_combo.setCurrentText(ayanamsa_mode)
            const._DEFAULT_AYANAMSA_MODE = self._ayanamsa_mode
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
    def latitude(self,latitude):
        """
            Sets the latitude manually
            @param - latitude
        """
        self._latitude = float(latitude)
        self._lat_text.setText(str(latitude))
    def longitude(self,longitude):
        """
            Sets the longitude manually
            @param - longitude
        """
        self._longitude = float(longitude)
        self._long_text.setText(str(longitude))
    def time_zone(self,time_zone):
        """
            Sets the time zone offset manually
            @param - time_zone - time zone offset
        """
        self._time_zone = float(time_zone)
        self._tz_text.setText(str(time_zone))
    def date_of_birth(self, date_of_birth):
        """
            Sets the Date of birth (Format:YYYY,MM,DD)
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
        if language in available_languages.keys():
            self._language = language
            self._lang_combo.setCurrentText(language)
    def _validate_ui(self):
        all_data_ok = self._place_text.text().strip() != '' and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._lat_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._long_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d{1,5}\,\d{1,2}\,\d{1,2}", self._dob_text.text().strip(),re.IGNORECASE)
        return all_data_ok
    def _update_main_window_label_and_tooltips(self):
        try:
            if self.resources:
                msgs = self.resources
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
                _language_index = self._lang_combo.currentIndex()
                self._lang_combo.clear()
                #self._lang_combo.addItems([msgs[l.lower()+'_str'] for l in const.available_languages.keys()])
                self._lang_combo.addItems(const.available_languages.keys())
                self._lang_combo.setCurrentIndex(_language_index)
                self._ayanamsa_combo.setToolTip(msgs['ayanamsa_tooltip_str'])
                self._ayanamsa_combo.setMaximumWidth(300)
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
                self._footer_label.setText(msgs['window_footer_title'])
                self.setWindowTitle(msgs['window_title']+'-'+const._APP_VERSION)
                self.update()
                print('UI Language change to',self._language,'completed')
        except:
            print('Some error happened during changing to',self._language,' language and displaying UI in that language.\n'+\
            'Please Check resources file:',const._DEFAULT_LANGUAGE_MSG_STR+available_languages[self._language]+'.txt')
            print(sys.exc_info())
    def compute_horoscope(self, calculation_type='drik'):
        """
            Compute the horoscope based on details entered
            if details missing - error is displayed            
        """
        if not self._validate_ui():
            print('values are not filled properly')
            return
        self._place_name = self._place_text.text()
        self._latitude = float(self._lat_text.text())
        self._longitude = float(self._long_text.text())
        self._time_zone = float(self._tz_text.text())
        self._language = list(const.available_languages.keys())[self._lang_combo.currentIndex()]
        utils.set_language(available_languages[self._language])
        self.resources = utils.resource_strings
        year,month,day = self._dob_text.text().split(",")
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        self.julian_day = utils.julian_day_number(dob, tob)
        self.place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._ayanamsa_mode =  self._ayanamsa_combo.currentText()
        drik.set_ayanamsa_mode(self._ayanamsa_mode,jd=self.julian_day) if self._ayanamsa_mode.upper()=='SUNDAR_SS' else drik.set_ayanamsa_mode(self._ayanamsa_mode) 
        ' set the chart type and reset widgets'
        info_str = ''
        format_str = _KEY_VALUE_FORMAT_
        self._fill_panchangam_info(info_str, format_str)
        self._update_clock_tab_text()
        if self.show_vedic_analog_clock:
            self._vedic_analog_clock.jd = self.julian_day; self._vedic_analog_clock.place = self.place
            self._vedic_analog_clock._get_drik_info()
        self.tabWidget.setCurrentIndex(0) # Switch First / Panchanga Tab
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
    def _fill_panchangam_info(self, info_str,format_str):
        jd = self.julian_day; place = self.place
        self.panchanga_info_dialog.set_language(self._language)
        self.panchanga_info_dialog.update_panchangam_info(jd, place,ayanamsa_mode=self._ayanamsa_mode)
        return
    def _update_chart_ui_with_info(self):
        # Update Panchanga and Bhava tab names here
        for t in range(_tabcount_before_chart_tab):
            self.tabWidget.setTabText(t,self.resources[_tab_names[t]])
        self.update()
    def _reset_place_text_size(self):
        pt = 'Chennai'#self._place_text.text().split(',')[0]
        f = QFont("",0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw,ph)
        self._place_text.adjustSize()
        self._place_text.selectionStart()
        self._place_text.setCursorPosition(0)
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
        print('RESULT',result)
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
        self._reset_place_text_size()
            
    def _save_city_to_database(self):
        if self._validate_ui():
            " add this data to csv file "
            tmp_arr = self._place_name.split(',')
            country = 'N/A'
            city = tmp_arr[0]
            if len(tmp_arr) > 1:
                country = tmp_arr[1:]
            location_data = [country,city,self._latitude,self._longitude,country,self._time_zone]
            utils.save_location_to_database(location_data)
        return          
    def _save_info_labels_by_click_scroll(self, image_id, image_files):
        labels = [
            self.panchanga_info_dialog._info_label1,
            self.panchanga_info_dialog._info_label2,
            self.panchanga_info_dialog._info_label3
        ]
    
        scrollbars = [label.verticalScrollBar() for label in labels]
        finished = [False, False, False]
    
        # Capture initial state before any scroll
        QApplication.processEvents()
        image_file = _images_path + f'pdf_info_label_{image_id}.png'
        image = self.grab()
        image.save(image_file)
        image_files.append(image_file)
        image_id += 1
    
        while not all(finished):
            for i, sb in enumerate(scrollbars):
                if not finished[i]:
                    current = sb.value()
                    step = sb.pageStep()
                    max_val = sb.maximum()
                    new_val = current + step
                    sb.setValue(min(new_val, max_val))
                    finished[i] = new_val >= max_val
    
            QApplication.processEvents()
    
            image_file = _images_path + f'pdf_info_label_{image_id}.png'
            image = self.grab()
            image.save(image_file)
            image_files.append(image_file)
            image_id += 1
    
        return image_id
    def _save_info_labels_as_images(self, image_id, image_files):
        label1 = self.panchanga_info_dialog._info_label1
        label2 = self.panchanga_info_dialog._info_label2
        label3 = self.panchanga_info_dialog._info_label3
    
        def get_scrollable_pages(text_edit: QTextEdit) -> int:
            scroll_bar = text_edit.verticalScrollBar()
            step = scroll_bar.pageStep()
            max_val = scroll_bar.maximum()
            return max(1, int(max_val // step + 1))
    
        pages_label1 = get_scrollable_pages(label1)
        pages_label2 = get_scrollable_pages(label2)
        pages_label3 = get_scrollable_pages(label3)
    
        max_pages = max(pages_label1, pages_label2, pages_label3)
        print(pages_label1, pages_label2, pages_label3,max_pages)
        for page in range(max_pages):
            label1.verticalScrollBar().setValue(int(min(page, pages_label1 - 1) * label1.verticalScrollBar().maximum() / (pages_label1 - 1)))
            label2.verticalScrollBar().setValue(int(min(page, pages_label2 - 1) * label2.verticalScrollBar().maximum() / (pages_label2 - 1)))
            label3.verticalScrollBar().setValue(int(min(page, pages_label3 - 1) * label3.verticalScrollBar().maximum() / (pages_label3 - 1)))
    
            QApplication.processEvents()
    
            image_file = _images_path + f'pdf_info_label_{image_id}.png'
            image = self.grab()
            image.save(image_file)
            image_files.append(image_file)
            image_id += 1
    
        return image_id
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
        def __save_scrollable_list_widget_as_image(widget:QWidget,image_id, image_files,_row_steps=1,widget_is_combo=False,row_count_size=None):
            """ TODO: Annual Dhasa count is not coming correct. Annual Dhasa is repeatedly printed by rasi/graha dhasa count times """
            _sleep_time = 0.01
            scroll_tab_count = 0
            import time; 
            row_count = widget.count() if row_count_size==None else row_count_size
            for row in range(0,row_count,_row_steps):
                self._hide_show_even_odd_pages(image_id)
                if widget_is_combo:
                    widget.setCurrentIndex(row)
                    if widget == self._dhasa_combo:
                        self._dhasa_type_selection_changed()                 
                else:
                    widget.setCurrentRow(row)
                image_file = _images_path+image_prefix+str(image_id)+image_ext
                time.sleep(_sleep_time)
                im = self.grab()
                im.save(image_file) 
                image_files.append(image_file)
                image_id +=1
                scroll_tab_count += 1
            return image_id
        if pdf_file_name:
            self._hide_show_layout_widgets(self._row2_h_layout, False)
            """
            for t in [0]:#range(self.tabCount):
                self._hide_show_even_odd_pages(image_id)
                self.tabWidget.setCurrentIndex(t)
                self._show_only_tab(t)
                image_file = _images_path+image_prefix+str(image_id)+image_ext
                image_files.append(image_file)
                im = self.grab()
                im.save(image_file) 
                image_id +=1
            """
            image_id = self._save_info_labels_by_click_scroll(image_id, image_files)
            self._reset_all_ui()
            ci = 1
            for i in range(0,len(image_files),_IMAGES_PER_PDF_PAGE):
                combined_image_file = _images_path+'combined_'+str(ci)+image_ext
                _combine_multiple_images(image_files[i:i+2],combined_image_file)
                combined_image_files.append(combined_image_file)
                ci += 1
            with open(pdf_file_name,"wb") as f:
                f.write(img2pdf.convert(combined_image_files))
            f.close()
        for image_file in image_files+combined_image_files:
            if os.path.exists(image_file):
                os.remove(image_file)
    def _reset_all_ui(self):
        self._hide_show_layout_widgets(self._row1_h_layout, True)
        self._hide_show_layout_widgets(self._row2_h_layout, True)
        self._footer_label.show()
        for t in range(self.tabCount): # reset all tabs to visible
            self.tabWidget.setTabVisible(t,True)
        
    def _hide_show_even_odd_pages(self,image_id):
        if image_id % 2 == 0: # Even Page
            self._hide_show_layout_widgets(self._row1_h_layout, False)
            self._hide_show_layout_widgets(self._row2_h_layout, False)
            self._footer_label.show()
        else:
            self._hide_show_layout_widgets(self._row1_h_layout, True)
            if image_id==1:
                self._hide_show_layout_widgets(self._row2_h_layout, True)
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
def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1
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
    target.save(output_image, quality=image_quality_in_pixels)
if __name__ == "__main__":
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = PanchangaWidget(show_vedic_digital_clock=True,show_vedic_analog_clock=True,show_local_clock=True)
    chart.language('Tamil')
    """
    chart.date_of_birth('1996,12,7')#('-5114,1,9')
    chart.time_of_birth('10:34:00')#('12:10:00')
    chart.place('Chennai, India',13.0878,80.2785,5.5)
    """
    chart.compute_horoscope()
    chart.show()
    sys.exit(App.exec())
