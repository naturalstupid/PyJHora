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
from jhora.panchanga import drik, pancha_paksha
_available_ayanamsa_modes = [k for k in list(const.available_ayanamsa_modes.keys()) if k not in ['SENTHIL','SIDM_USER','SUNDAR_SS']]
_KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'; _HEADER_COLOR='green'
_KEY_LENGTH=50; _VALUE_LENGTH=50; _HEADER_LENGTH=100
_HEADER_FORMAT_ = '<b><span style="color:'+_HEADER_COLOR+';">{:<'+str(_HEADER_LENGTH)+'}</span></b><br>'
_KEY_VALUE_FORMAT_ = '<span style="color:'+_KEY_COLOR+';">{:.'+str(_KEY_LENGTH)+'}</span><span style="color:'+\
        _VALUE_COLOR+';">{:.'+str(_VALUE_LENGTH)+'}</span><br>'
_images_path = const._IMAGES_PATH
_IMAGES_PER_PDF_PAGE = 2
_IMAGE_ICON_PATH=const._IMAGE_ICON_PATH
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
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
_info_label1_height = 600
_info_label1_width = 100
_info_label1_font_size = 5.6#8
_info_label2_height = _info_label1_height; _info_label3_height = _info_label1_height
_info_label2_width = 100
_info_label2_font_size = 5 if _SHOW_MUHURTHA_OR_SHUBHA_HORA==0 else 5.9
_info_label3_font_size =5.62#8
_row3_widget_width = 75
_chart_info_label_width = 230#350
_footer_label_font_height = 8
_footer_label_height = 30
_chart_size_factor = 1.35
_tab_names = ['panchangam_str','']
_tab_count = len(_tab_names)
_tabcount_before_chart_tab = 1

available_languages = const.available_languages
class PanchangaInfoDialog(QWidget):
    def __init__(self,language = 'English',jd=None,place:drik.Place=None,
                 info_label1_font_size=_info_label1_font_size, info_label2_font_size=_info_label2_font_size,
                 info_label3_font_size=_info_label3_font_size,
                 info_label_height=_info_label1_height):
        """
            @param jd: Julian Day Number
            @param place_of_birth: tuple in the format ('place_name',latitude_float,longitude_float,timezone_hrs_float)
                                    e.g. ('Chennai, India',13.0878,80.2785,5.5)
            @param language: One of 'English','Hindi','Tamil','Telugu','Kannada'; Default:English
        """
        super().__init__()
        self.start_jd = jd; self.place = place
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
        if place is None:
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
        self._info_label1 = QLabel("Information:")
        self._info_label1.setMinimumHeight(self._info_label1_height)
        self._info_label1.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label1.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label1_font_size)+'pt')
        _margin = int(_info_label1_font_size)
        self._info_label1.setContentsMargins(_margin,_margin,_margin,_margin)
        h_layout.addWidget(self._info_label1)
        self._info_label2 = QLabel("Information:")
        self._info_label2.setMinimumHeight(self._info_label2_height)
        self._info_label2.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label2.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label2_font_size)+'pt')
        _margin = int(_info_label2_font_size)
        self._info_label2.setContentsMargins(_margin,_margin,_margin,_margin)
        h_layout.addWidget(self._info_label2)
        self._info_label3 = QLabel("Information:")
        self._info_label3.setMinimumHeight(self._info_label3_height)
        self._info_label3.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label3.setStyleSheet("border: 1px solid black;"+' font-size:'+str(self._info_label3_font_size)+'pt')
        _margin = int(_info_label3_font_size)
        self._info_label3.setContentsMargins(_margin,_margin,_margin,_margin)
        h_layout.addWidget(self._info_label3)
        self.setLayout(h_layout)
        self.setWindowTitle(self.res['panchangam_str'])
        self.move(50,50)
    def update_panchangam_info(self,jd=None,place:drik.Place=None):
        try:
            if jd is not None: self.start_jd = jd
            if place is not None: self.place = place
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
    def _fill_information_label1(self,show_more_link=True,jd=None,place=None):
        try:
            jd = self.start_jd if jd is None else jd
            place = self.place if place is None else place
            info_str = ''; format_str = _KEY_VALUE_FORMAT_
            year, month, day,_ = utils.jd_to_gregorian(jd)
            date_in = drik.Date(year,month,day)
            if jd is None: return
            key = self.res['vaaram_str']
            value = utils.DAYS_LIST[drik.vaara(jd)]
            info_str += format_str.format(key,value)
            date_str1 = str(year)+','+str(month)+','+str(day)
            date_str2 = str(year)+' '+utils.MONTH_LIST_EN[month-1]+' '+str(day)
            key = self.res['date_of_birth_str']; value = date_str2
            info_str += format_str.format(key,value)
            key = self.res['tamil_month_str']
            tm,td = drik.tamil_solar_month_and_date(date_in, place)
            value = utils.MONTH_LIST[tm] +" "+self.res['date_str']+' '+str(td)
            info_str += format_str.format(key,value)
            key = self.res['lunar_year_month_str']
            maasam_no,adhik_maasa,nija_maasa = drik.lunar_month(jd,place)
            adhik_maasa_str = ''; 
            if adhik_maasa:
                adhik_maasa_str = self.res['adhika_maasa_str']
            _samvatsara = drik.samvatsara(date_in, place, zodiac=0)
            """ Check if current month is Nija Maasa """
            nija_month_str = ''
            if nija_maasa:
                nija_month_str = self.res['nija_month_str']
            value = utils.YEAR_LIST[_samvatsara-1]+' / '+utils.MONTH_LIST[maasam_no-1]+' '+adhik_maasa_str+nija_month_str
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
            key = self.res['nakshatra_str']
            nak = drik.nakshatra(jd,place)
            value = utils.NAKSHATRA_LIST[nak[0]-1]+' '+  \
                        ' ('+utils.PLANET_SHORT_NAMES[utils.nakshathra_lord(nak[0])]+') '+ self.res['paadham_str']+\
                        str(nak[1]) + ' '+ utils.to_dms(nak[3]) + ' ' + self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['raasi_str']
            rasi = drik.raasi(jd,place)
            frac_left = rasi[2]*100
            value = utils.RAASI_LIST[rasi[0]-1]+' '+rasi[1]+ ' ' + self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['tithi_str']; _tithi = drik.tithi(jd, place)
            _paksha = 0
            if _tithi[0] > 15: _paksha = 1 # V3.1.1
            value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi[0]-1]+ \
                            ' (' + utils.TITHI_DEITIES[_tithi[0]-1]+') '+ \
                            utils.to_dms(_tithi[2])+ ' ' + self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['yogam_str']
            yogam = drik.yogam(jd,place)
            yoga_lord = ' ('+utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[yogam[0]-1][0]]+'/'+\
                            utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[yogam[0]-1][1]]+') '
            value = utils.YOGAM_LIST[yogam[0]-1] + yoga_lord + '  '+ \
                                utils.to_dms(yogam[2])+ ' ' + self.res['ends_at_str']
            info_str += format_str.format(key,value)
            key = self.res['karanam_str']
            karanam = drik.karana(jd,place)
            karana_lord = utils.PLANET_SHORT_NAMES[utils.karana_lord(karanam[0])]
            value = utils.KARANA_LIST[karanam[0]-1]+' ('+ karana_lord +') '+utils.to_dms(karanam[1])+ ' ' +\
                            utils.to_dms(karanam[2])+ ' ' + self.res['ends_at_str']
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
            scd = drik.sahasra_chandrodayam(date_in, (7,0,0), place)
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
            value = utils.to_dms(drik.day_length(jd, place)).replace(' AM','').replace(' PM','')+' '+self.res['hours_str']
            info_str += format_str.format(key,value)
            key = self.res['night_length_str']
            value = utils.to_dms(drik.night_length(jd, place)).replace(' AM','').replace(' PM','')+' '+self.res['hours_str']
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
            info_str += format_str.format(key,value)
            paksha_index = _paksha+1
            bird_index = pancha_paksha._get_birth_bird_from_nakshathra(nak[0],paksha_index)
            key = self.res['pancha_pakshi_sastra_str']+' '+self.res['main_bird_str'].replace('\\n',' ')+' : '
            value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
            info_str += format_str.format(key,value)
            [kali_year, vikrama_year,saka_year] = drik.elapsed_year(jd,maasam_no)
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
            print(f"An error occurred: {e}")
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
            info_str += key_str+' '+value_str#format_str.format(key,value)
            return info_str
        except Exception as e:
            print(f"An error occurred: {e}")
if __name__ == "__main__":
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    lang = 'Tamil'
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob,tob)
    chart = PanchangaInfoDialog(language=lang)
    #chart.update_panchangam_info(jd, place)
    chart.show()
    sys.exit(App.exec())
