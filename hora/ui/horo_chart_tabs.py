""" Get Package Version from _package_info.py """
from hora import _package_info
_APP_VERSION=_package_info.version
#----------
import re, sys, os
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QStyledItemDelegate, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, \
                            QListWidget, QTextEdit, QAbstractItemView, QAbstractScrollArea, QTableWidgetItem, \
                            QGridLayout, QLayout, QLabel, QSizePolicy, QLineEdit, QCompleter, QComboBox, \
                            QPushButton, QSpinBox, QCheckBox, QApplication, QDoubleSpinBox, QHeaderView, \
                            QListWidgetItem,QMessageBox, QFileDialog
from PyQt6.QtGui import QFont, QFontMetrics, QPixmap
from PyQt6.QtCore import Qt
from _datetime import datetime, timedelta, timezone
import img2pdf
from PIL import Image
import numpy as np
from hora import const, utils
from hora.panchanga import drik
from hora.horoscope import main
from hora.horoscope.prediction import general
from hora.horoscope.match import compatibility
from hora.horoscope.chart import ashtakavarga
from hora.horoscope.chart import yoga, raja_yoga, dosha
from hora.horoscope.chart import house
from hora.ui.chart_styles import EastIndianChart, WesternChart, SouthIndianChart, NorthIndianChart, SudarsanaChakraChart
from hora.horoscope.dhasa import sudharsana_chakra
_images_path = const._IMAGES_PATH
_IMAGES_PER_PDF_PAGE = 2
_IMAGE_ICON_PATH=const._IMAGE_ICON_PATH
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
_world_city_csv_file = const._world_city_csv_file
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
""" UI Constants """
_main_window_width = 1000#750 #725
_main_window_height = 725#630 #580 #
_comp_table_font_size = 8
_comp_results_per_list_item = 3
_yoga_text_font_size = 10#8.5
_dosha_text_font_size = 10#9
_prediction_text_font_size = 5
_raja_yogas_per_list_item = 1 # Do not change this from 1 yet
_yogas_per_list_item = 3
_doshas_per_list_item = 1
_predictions_per_list_item = 1
_compatability_list_width = 175#145
_yoga_list_box_width = 125
_dosha_list_box_width = 150#125
_prediction_list_box_width = 150
_shodhaya_table_font_size = 9#6.3
_drishti_table_font_size = 8#6.3
_chart_info_label_font_size = 6.37#7# # if uranus/neptune/pluto included
south_chart_title_font_size = 12; north_chart_title_font_size=12; east_chart_title_font_size=12
west_chart_title_font_size = 10; sudarsana_chakra_chart_title_font_size = 8
_main_ui_label_button_font_size = 10#8
#_main_ui_comp_label_font_size = 7
_info_label1_height = 200
_info_label1_width = 100
_info_label1_font_size = 9#8
_info_label2_height = _info_label1_height
_info_label2_width = 100
_info_label2_font_size = 9#8
_row3_widget_width = 75
_chart_info_label_width = 350#150
_ashtaka_chart_size_factor = 0.475
_footer_label_font_height = 8
_footer_label_height = 30
_chart_size_factor = 1.5
_chart_label_font_size = 12
_margin_between_chart_and_info = 1
_arudha_lagnas_included_in_chart = const._arudha_lagnas_included_in_chart
_chart_names = ['raasi_str','hora_str','drekkanam_str','chaturthamsa_str','panchamsa_str',
              'shashthamsa_str','saptamsam_str','ashtamsa_str','navamsam_str','dhasamsam_str','rudramsa_str',
              'dhwadamsam_str','shodamsa_str','vimsamsa_str','chaturvimsamsa_str','nakshatramsa_str','thrisamsam_str',
              'khavedamsa_str','akshavedamsa_str','sashtiamsam_str',
              'nava_navamsa_str','ashtotharamsa_str','dwadas_dwadasamsa_str']
_bala_names = ['sphuta_str','drishti_str','bhava_graha_arudha_str','amsa_bala_str','harsha_pancha_dwadhasa_vargeeya_bala_str',
               'shad_bala_str','bhava_bala_str']
""" dhasa dictionary {"dhasa":[tab_count,table_font_size,tables_per_tab,rows_per_table,cols_per_table] """
_graha_dhasa_dict = {'vimsottari':[3,10,3,9,1,0,[],[]],'yoga_vimsottari':[3,10,3,9,1,0,[],[]],'rasi_bhukthi_vimsottari':[3,10,3,12,1,0,[],[]],
                     'ashtottari':[3,11,3,8,1,0,[],[]],'tithi_ashtottari':[3,11,3,8,1,0,[],[]],'yogini':[6,8,4,8,1,0,[],[]],
                     'tithi_yogini':[6,8,4,8,1,0,[],[]],'shodasottari':[2,8,4,8,1,0,[],[]],'dwadasottari':[2,8,4,8,1,0,[],[]],
                     'dwisatpathi':[4,8,4,8,1,0,[],[]],'panchottari':[2,8,4,7,1,0,[],[]],'satabdika':[2,8,4,7,1,0,[],[]],
                     'chaturaaseeti_sama':[2,8,4,7,1,0,[],[]],'karana_chaturaaseeti_sama':[2,8,4,7,1,0,[],[]],
                     'shashtisama':[2,8,4,8,1,0,[],[]],'shattrimsa_sama':[6,8,4,8,1,0,[],[]],'naisargika':[2,8,4,6,1,0,[],[]],
                     'tara':[3,10,3,9,1,0,[],[]],'karaka':[3,8.5,3,8,1,0,[],[]],'buddhi_gathi':[5,8,4,9,1,0,[],[]],
                     'kaala':[3,10,3,18,1,0,[],[]]}
_graha_dhasa_names = list(_graha_dhasa_dict.keys())
_graha_dhasa_tab_count = sum(v[0] for k,v in _graha_dhasa_dict.items())
_rasi_dhasa_dict = {'narayana':[3,7.5,4,12,1,0,[],[]],'kendraadhi_rasi':[3,7.5,4,12,1,0,[],[]],'sudasa':[3,7.5,4,12,1,0,[],[]],'drig':[3,8,4,12,1,0,[],[]],
                'nirayana':[3,7.5,4,12,1,0,[],[]], 'shoola':[3,7.5,4,12,1,0,[],[]],'kendraadhi_karaka':[3,7.5,4,12,1,0,[],[]],
                'chara':[3,7.5,4,12,1,0,[],[]],'lagnamsaka':[4,7.5,4,12,1,0,[],[]],'padhanadhamsa':[4,7.5,4,12,1,0,[],[]],
                'mandooka':[3,7.5,4,12,1,0,[],[]],'sthira':[3,7.5,4,12,1,0,[],[]],'tara_lagna':[3,7.5,4,12,1,0,[],[]],
                'brahma':[3,7.5,4,12,1,0,[],[]],'varnada':[3,7.5,4,12,1,0,[],[]],'yogardha':[3,7.5,4,12,1,0,[],[]],
                'navamsa':[3,7.5,4,12,1,0,[],[]],'paryaaya':[3,7.5,4,12,1,0,[],[]],'trikona':[3,7.5,4,12,1,0,[],[]],
                'kalachakra':[1,11,2,9,1,0,[],[]], 'chakra':[3,7.5,4,12,1,0,[],[]]}
### 'paryaaya':[1,10,2,12,1,0,[],[]],'trikona':[1,10,2,12,1,0,[],[]],
_rasi_dhasa_names = list(_rasi_dhasa_dict.keys())
_rasi_dhasa_tab_count = sum(v[0] for k,v in _rasi_dhasa_dict.items())
_annual_dhasa_dict ={'patyayini':[2,7.5,4,8,1,0,[],[]],'varsha_vimsottari':[3,9,3,9,1,0,[],[]],'varsha_narayana':[5,7.5,4,12,1,0,[],[]],}
_annual_dhasa_names = list(_annual_dhasa_dict.keys())
_annual_dhasa_tab_count = sum(v[0] for k,v in _annual_dhasa_dict.items())
_other_names = ['ashtaka_varga_str','argala_str','shodhaya_pinda_str','yoga_str','dosha_str','compatibility_str','prediction_str']
_tab_names = ['panchangam_str'] + _chart_names + _bala_names + _graha_dhasa_names + _rasi_dhasa_names + \
            _annual_dhasa_names + _other_names
_chart_tab_end = len(_chart_names)+1
_sphuta_tab_start = _chart_tab_end#len(_chart_names)+1
_sphuta_tab_count = 6
_sphuta_tab_end = _sphuta_tab_start + _sphuta_tab_count - 1
_sphuta_table_font_size= 9#7

_drishti_tab_start = _sphuta_tab_end + 1
_drishti_tab_count = 1
_drishti_tab_end = _drishti_tab_start + _drishti_tab_count - 1

_graha_arudha_tab_start = _drishti_tab_start+1
_graha_arudha_tab_count = 6
_graha_arudha_tab_end = _graha_arudha_tab_start + _graha_arudha_tab_count - 1
_arudha_table_font_size= 10#8

_amsa_bala_tab_start = _graha_arudha_tab_end + 1 
_amsa_bala_tab_count = 1
_amsa_bala_tab_end = _amsa_bala_tab_start + _amsa_bala_tab_count - 1
_amsa_bala_table_font_size = 8#6

_other_bala_tab_start = _amsa_bala_tab_end + 1 
_other_bala_tab_count = 1
_other_bala_tab_end = _other_bala_tab_start + _other_bala_tab_count - 1
_other_bala_table_font_size = 12#8

_shad_bala_tab_start = _other_bala_tab_end + 1 
_shad_bala_tab_count = 1
_shad_bala_tab_end = _shad_bala_tab_start + _shad_bala_tab_count - 1
_shad_bala_table_font_size = 12

_bhava_bala_tab_start = _shad_bala_tab_end + 1 
_bhava_bala_tab_count = 1
_bhava_bala_tab_end = _bhava_bala_tab_start + _bhava_bala_tab_count - 1
_bhava_bala_table_font_size = 12

_ashtaka_varga_tab_start = _bhava_bala_tab_end  + _graha_dhasa_tab_count + _rasi_dhasa_tab_count+ _annual_dhasa_tab_count + 1
""" 8 BAV/PAV-Raasi for each planet and Asc. One SAV-D1/SAV-D9. 8 BAV/PAV-D9 for each planet"""
_ashtaka_varga_tab_count = len(_tab_names[1:_chart_tab_end])#_vimsottari_dhasa_tab_start]) #+1 # +1 for shodhaya tables
_ashtaka_varga_tab_end = _ashtaka_varga_tab_start + _ashtaka_varga_tab_count - 1

_argala_tab_start = _ashtaka_varga_tab_end + 1
_argala_tab_count = 1
_argala_tab_end = _argala_tab_start + _argala_tab_count - 1
_argala_table_font_size = 10#6.5

_shodhaya_tab_start  = _argala_tab_end + 1
_shodhaya_tab_count = 2 # one for Raasi and another for Navamsam
_shodhaya_dict = {0:'raasi_str',7:'navamsam_str'} #2 and 7 are horoscope chart counters
_shodhaya_tab_end = _shodhaya_tab_start + _shodhaya_tab_count - 1

_yoga_tab_start = _shodhaya_tab_end + 1
_yoga_tab_count = 1
_yoga_tab_end = _yoga_tab_start + _yoga_tab_count - 1

_dosha_tab_start = _yoga_tab_end + 1
_dosha_tab_count = 1
_dosha_tab_end = _dosha_tab_start + _dosha_tab_count - 1

_compatibility_tab_start = _dosha_tab_end + 1 
_prediction_tab_start = _compatibility_tab_start + 1 
_tab_count = len(_tab_names)

available_chart_types = {'south_indian':SouthIndianChart,'north_indian':NorthIndianChart,'east_indian':EastIndianChart,
                         'western':WesternChart,'sudarsana_chakra':SudarsanaChakraChart}
available_languages = const.available_languages
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignHCenter
class GrowingTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)  
        self.document().contentsChanged.connect(self.sizeChange)

        self.heightMin = 0
        self.heightMax = 65000

    def sizeChange(self):
        docHeight = int(self.document().size().height())
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)
class ChartTabbed(QWidget):
    def __init__(self,chart_type='south_indian',show_marriage_compatibility=True, calculation_type:str='drik'):
        super().__init__()
        self._chart_type = chart_type
        self._calculation_type = calculation_type
        self._show_compatibility = show_marriage_compatibility
        ' read world cities'
        self._df = utils._world_city_db_df
        self._world_cities_db = utils.world_cities_db
        self._conjunction_dialog_accepted = False; self._conj_planet1=''; self._conj_planet2=''; self._raasi=''
        self._separation_angle_list = []
        self._separation_angle_index = 0              
        self._init_main_window()
        self._v_layout = QVBoxLayout()
        self._create_row1_ui()
        self._create_row_2_and_3_ui()
        if self._show_compatibility:
            self._create_comp_ui()
        self._init_tab_widget_ui()
        year,month,day = self._dob_text.text().split(",")
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        self._birth_julian_day = utils.julian_day_number(dob, tob)
        self.compute_horoscope(calculation_type=self._calculation_type)    
    def _hide_2nd_row_widgets(self,show=True):
            self._dob_label.setVisible(show)
            self._dob_text.setVisible(show)
            self._tob_label.setVisible(show)
            self._tob_text.setVisible(show)
            self._chart_type_combo.setVisible(show)
            self._ayanamsa_combo.setVisible(show)
    def _process_tab_changed(self):
        _current_tab_index = self.tabWidget.currentIndex()
        if _current_tab_index == _compatibility_tab_start :
            self._show_hide_marriage_checkboxes(True)
        elif _current_tab_index >= 32 and _current_tab_index <= 64:  #_vimsottari_dhasa_tab_start and _current_tab_index <= _shoola_dhasa_tab_end:
            self._hide_2nd_row_widgets(False)
        else:
            self._hide_2nd_row_widgets(True)
            self._show_hide_marriage_checkboxes(False)
    def _init_tab_widget_ui(self):
        self._western_chart = False
        if 'west' in self._chart_type.lower():
            self._western_chart = True
            self.tabNames = _tab_names[:_chart_tab_end]
        elif self._show_compatibility:
            self.tabNames = _tab_names
        else:
            self.tabNames = _tab_names[:-1]
        self.tabWidget = QTabWidget()
        self.tabWidget.currentChanged.connect(self._process_tab_changed)
        self._v_layout.addWidget(self.tabWidget)
        self.tabCount = len(self.tabNames)
        self.horo_tabs = []
        self._charts = []
        self._ashtaka_charts = []
        self._drishti_table1 = []
        self._drishti_table2 = []
        self._argala_table1 = []
        self._argala_table2 = []
        self._shad_bala_table = []
        self._bhava_bala_table = []
        self._shodhaya_table1 = []
        self._shodhaya_table_label1=[]
        self._shodhaya_table2 = []
        self._shodhaya_table_label2=[]
        self._chart_info_labels= []
        self.match_tables = [[ QTableWidget(13,4) for _ in range(2)] for _ in range(10)]
        self.vimsottari_db_tables =  []
        self._matching_star_list = QListWidget()
        self._yoga_list = QListWidget()
        self._yoga_text = QTextEdit()
        self._yoga_text.setReadOnly(True)# setDisabled(True)
        self._dosha_list = QListWidget()
        self._dosha_text = QTextEdit()
        self._dosha_text.setReadOnly(True)# setDisabled(True)
        self._prediction_list = QListWidget()
        self._prediction_text = QTextEdit()#GrowingTextEdit()
        self._prediction_text.setReadOnly(True)# setDisabled(True)
        t = 0
        self._init_panchanga_tab_widgets(t)
        t+=1
        self._init_chart_tab_widgets(t)
        t += len(_chart_names)
        if not self._western_chart or 'west' not in self._chart_type.lower():
            self._init_sphuta_tab_widgets(t)
            t += _sphuta_tab_count
            self._init_drishti_tab_widgets(t)
            t += _drishti_tab_count
            self._init_graha_arudha_tab_widgets(t)
            t += _graha_arudha_tab_count
            self._init_amsa_bala_tab_widgets(t)
            t += _amsa_bala_tab_count
            self._init_other_bala_tab_widgets(t)
            t += _other_bala_tab_count
            self._init_shad_bala_tab_widgets(t)
            t += _shad_bala_tab_count
            self._init_bhava_bala_tab_widgets(t)
            t += _bhava_bala_tab_count
            t_i = self._init_tab_widgets(t)
            _added_tab_count = sum(v[0] for _,v in _graha_dhasa_dict.items())
            t += _added_tab_count
            _added_tab_count = sum(v[0] for _,v in _rasi_dhasa_dict.items())
            t += _added_tab_count
            _added_tab_count = sum(v[0] for _,v in _annual_dhasa_dict.items())
            t += _added_tab_count
            self._init_ashtaka_tab_widgets(t)
            t += _ashtaka_varga_tab_count
            self._init_argala_tab_widgets(t)
            t += _argala_tab_count
            self._init_shodhaya_tab_widgets(t)
            t += _shodhaya_tab_count
            self._init_yoga_tab_widgets(t)
            t += _yoga_tab_count
            self._init_dosha_tab_widgets(t)
            t += _dosha_tab_count
            if self._show_compatibility and t==_compatibility_tab_start:
                self._init_compatibility_tab_widgets(t)
                t += 1
            self._init_prediction_tab_widgets(t); t += 1
        self.tabCount = self.tabWidget.count()
        self._add_footer_to_chart()
        self.setLayout(self._v_layout)        
        self._show_hide_marriage_checkboxes(False)
    def _init_prediction_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        h_layout = QHBoxLayout()
        self._prediction_list =QListWidget()
        self._prediction_list.currentRowChanged.connect(self._update_prediction_table)
        self._prediction_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._prediction_list.setMaximumWidth(_prediction_list_box_width)
        h_layout.addWidget(self._prediction_list)
        self._prediction_text = QTextEdit()#GrowingTextEdit()
        self._prediction_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._prediction_text.setStyleSheet('font-size:'+str(_prediction_text_font_size)+'pt')
        h_layout.addWidget(self._prediction_text)
        self.horo_tabs[_prediction_tab_start].setLayout(h_layout)
    def _init_dosha_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        h_layout = QHBoxLayout()
        self._dosha_list =QListWidget()
        self._dosha_list.currentRowChanged.connect(self._update_dosha_table)
        self._dosha_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._dosha_list.setMaximumWidth(_dosha_list_box_width)
        h_layout.addWidget(self._dosha_list)
        self._dosha_text = QTextEdit()
        self._dosha_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._dosha_text.setStyleSheet('font-size:'+str(_dosha_text_font_size)+'pt')
        h_layout.addWidget(self._dosha_text)
        self.horo_tabs[_dosha_tab_start].setLayout(h_layout)
    def _init_yoga_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
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
        self.horo_tabs[_yoga_tab_start].setLayout(h_layout)
    def _init_compatibility_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
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
    def _init_sphuta_tab_widgets(self,tab_index):
        self._sphuta_rows_per_table = len(const.sphuta_list)
        self._sphuta_cols_per_table = 1
        self._sphuta_tables_per_tab = 4
        tab_start = _sphuta_tab_start
        tab_count = _sphuta_tab_count
        tab_str = 'sphuta_str'
        self.sphuta_db_tables = self._init_dhasa_tab_widgets(tab_index, self._sphuta_tables_per_tab, self._sphuta_rows_per_table, 
                                            self._sphuta_cols_per_table, _sphuta_tab_start, _sphuta_tab_count, 
                                            'sphuta_str', _sphuta_table_font_size)
        return
    def _init_graha_arudha_tab_widgets(self,tab_index):
        self._arudha_rows_per_table = 9
        self._arudha_cols_per_table = 1
        self._arudha_tables_per_tab = 4
        tab_start = _graha_arudha_tab_start
        tab_count = _graha_arudha_tab_count
        tab_str = 'graha_arudham_str'
        self.arudha_db_tables = self._init_dhasa_tab_widgets(tab_index, self._arudha_tables_per_tab, self._arudha_rows_per_table, 
                                            self._arudha_cols_per_table, _graha_arudha_tab_start, _graha_arudha_tab_count, 
                                            'graha_arudham_str', _arudha_table_font_size)
        return
    def _init_amsa_bala_tab_widgets(self,tab_index):
        self._amsa_bala_rows_per_table = 9
        self._amsa_bala_cols_per_table = 1
        self._amsa_bala_tables_per_tab = 4
        self.amsa_bala_db_tables = self._init_dhasa_tab_widgets(tab_index, self._amsa_bala_tables_per_tab, self._amsa_bala_rows_per_table, 
                                            self._amsa_bala_cols_per_table, _amsa_bala_tab_start, _amsa_bala_tab_count, 
                                            'amsa_bala_str', _amsa_bala_table_font_size)
        return
    def _init_other_bala_tab_widgets(self,tab_index):
        self._other_bala_rows_per_table = 7
        self._other_bala_cols_per_table = 1
        self._other_bala_tables_per_tab = 3
        self.other_bala_db_tables = self._init_dhasa_tab_widgets(tab_index, self._other_bala_tables_per_tab, self._other_bala_rows_per_table, 
                                            self._other_bala_cols_per_table, _other_bala_tab_start, _other_bala_tab_count, 
                                            'harsha_pancha_dwadhasa_vargeeya_bala_str', _other_bala_table_font_size)
        return
    def _init_tab_widgets(self, tab_index):
        tab_start = tab_index
        for t, (tab_str,tab_values) in enumerate(_graha_dhasa_dict.items()):
            _graha_dhasa_dict[tab_str][5]=tab_start
            _db_tables = self._init_dhasa_tab_widgets(tab_index, tab_values[2], tab_values[3], 
                                            tab_values[4], tab_start, tab_values[0], 
                                            tab_str, tab_values[1])
            _graha_dhasa_dict[tab_str][6] = _db_tables
            tab_start += tab_values[0]
            tab_index = tab_start
        for t, (tab_str,tab_values) in enumerate(_rasi_dhasa_dict.items()):
            _rasi_dhasa_dict[tab_str][5]=tab_start
            _db_tables = self._init_dhasa_tab_widgets(tab_index, tab_values[2], tab_values[3], 
                                            tab_values[4], tab_start, tab_values[0], 
                                            tab_str, tab_values[1])
            _rasi_dhasa_dict[tab_str][6] = _db_tables
            tab_start += tab_values[0]
            tab_index = tab_start
        for t, (tab_str,tab_values) in enumerate(_annual_dhasa_dict.items()):
            _annual_dhasa_dict[tab_str][5]=tab_start
            _db_tables = self._init_dhasa_tab_widgets(tab_index, tab_values[2], tab_values[3], 
                                            tab_values[4], tab_start, tab_values[0], 
                                            tab_str, tab_values[1])
            _annual_dhasa_dict[tab_str][6] = _db_tables
            tab_start += tab_values[0]
            tab_index = tab_start
        return tab_start
    def _init_dhasa_tab_widgets(self,tab_index,tables_per_tab,rows_per_table,cols_per_table,
                                tab_start,tab_count,tab_str,table_font_size):
        """ Add more tabs for narayna dhasa  """
        for t in range(tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self.tabCount += tab_count#-1
        _db_tables = [[ QTableWidget(rows_per_table,cols_per_table) for _ in range(tables_per_tab)] for _ in range(tab_count)]
        for db_tab in range(tab_count):
            grid_layout = QGridLayout()
            for col in range(tables_per_tab):
                delegate = AlignDelegate(_db_tables[db_tab][col])
                _db_tables[db_tab][col].setItemDelegate(delegate)
                _db_tables[db_tab][col].setStyleSheet('font-size:'+str(table_font_size)+'pt')
                _db_tables[db_tab][col].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                _db_tables[db_tab][col].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                grid_layout.addWidget(_db_tables[db_tab][col],1,col)
            self.horo_tabs[tab_start+db_tab].setLayout(grid_layout)
            _tabname = tab_str+str(db_tab+1)
            self.tabWidget.setTabText(tab_start+db_tab,_tabname)
        return _db_tables
    def _init_panchanga_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        h_layout = QHBoxLayout()
        h_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self._info_label1 = QLabel("Information:")
        self._info_label1.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label1.setStyleSheet("border: 1px solid black;"+' font-size:'+str(_info_label1_font_size)+'pt')
        self._info_label1.setMinimumHeight(_info_label1_height)
        self._info_label1.setMinimumWidth(_info_label1_width)
        h_layout.addWidget(self._info_label1)
        self._info_label2 = QLabel("Information:")
        self._info_label2.setStyleSheet("border: 1px solid black;"+' font-size:'+str(_info_label2_font_size)+'pt')
        self._info_label1.setMinimumHeight(_info_label1_height)
        self._info_label2.setMinimumWidth(_info_label2_width)
        h_layout.addWidget(self._info_label2)
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_chart_tab_widgets(self,tab_index):
        for c in range(len(_chart_names)):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+c],self.tabNames[tab_index+c])
            h_layout = QHBoxLayout()
            self._charts.append(available_chart_types[self._chart_type](chart_size_factor=_chart_size_factor, label_font_size=_chart_label_font_size))
            h_layout.addWidget(self._charts[tab_index+c-1])
            self._chart_info_labels.append(QLabel('Chart Information'))
            h_layout.addWidget(self._chart_info_labels[tab_index+c-1])
            self._chart_info_labels[tab_index+c-1].setStyleSheet('font-size:'+str(_chart_info_label_font_size)+'pt')
            h_layout.setSpacing(_margin_between_chart_and_info)
            h_layout.setContentsMargins(0,0,0,0)
            self._charts[tab_index+c-1].update()
            self.horo_tabs[tab_index+c].setLayout(h_layout)
    def _init_drishti_tab_widgets(self,tab_index):
        # create extra tabs depending on the count
        for t in range(_drishti_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._drishti_table1 = [ QTableWidget(7,3) for _ in range(_drishti_tab_count)] 
        self._drishti_table2 = [ QTableWidget(9,3) for _ in range(_drishti_tab_count)] 
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
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
                table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(''))
                table.update()
            self.horo_tabs[tab_index+t].setLayout(h_layout)            
    def _init_shad_bala_tab_widgets(self, tab_index):
        for t in range(_shad_bala_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._shad_bala_table = [ QTableWidget(9,7) for _ in range(_shad_bala_tab_count)] 
        for t in range(_shad_bala_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._shad_bala_table[t])
            self._shad_bala_table[t].setItemDelegate(delegate)
            h_layout.addWidget(self._shad_bala_table[t])
            for table in [self._shad_bala_table[t]]:
                table.setStyleSheet('font-size:'+str(_shad_bala_table_font_size)+'pt')
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
    def _init_bhava_bala_tab_widgets(self, tab_index):
        for t in range(_bhava_bala_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._bhava_bala_table = [ QTableWidget(12,3) for _ in range(_bhava_bala_tab_count)] 
        for t in range(_bhava_bala_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._bhava_bala_table[t])
            self._bhava_bala_table[t].setItemDelegate(delegate)
            h_layout.addWidget(self._bhava_bala_table[t])
            for table in [self._bhava_bala_table[t]]:
                table.setStyleSheet('font-size:'+str(_bhava_bala_table_font_size)+'pt')
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
    def _init_argala_tab_widgets(self,tab_index):
        for t in range(_argala_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._argala_table1 = [ QTableWidget(12,4) for _ in range(_argala_tab_count)] 
        self._argala_table2 = [ QTableWidget(12,4) for _ in range(_argala_tab_count)] 
        for t in range(_argala_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._argala_table1[t])
            self._argala_table1[t].setItemDelegate(delegate)
            delegate = AlignDelegate(self._argala_table2[t])
            self._argala_table2[t].setItemDelegate(delegate)
            h_layout.addWidget(self._argala_table1[t])
            h_layout.addWidget(self._argala_table2[t])
            for table in [self._argala_table1[t], self._argala_table2[t]]:
                table.setStyleSheet('font-size:'+str(_argala_table_font_size)+'pt')
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
        for t in range(_shodhaya_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._shodhaya_table1 = [ QTableWidget(9,12) for _ in range(_shodhaya_tab_count)] 
        self._shodhaya_table_label1 = [ QLabel() for _ in range(_shodhaya_tab_count)] 
        self._shodhaya_table2 = [ QTableWidget(3,7) for _ in range(_shodhaya_tab_count)] 
        self._shodhaya_table_label2 = [ QLabel() for _ in range(_shodhaya_tab_count)] 
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
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(str(0)))
                    
            self.horo_tabs[tab_index+t].setLayout(v_layout)            
    def _init_ashtaka_tab_widgets(self, tab_index):
        # create extra tabs depending on the count
        for t in range(_ashtaka_varga_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        """ create 9x9 chart grid. 1st one SAV and others are 8 planet BAV """
        for t in range(_ashtaka_varga_tab_count):
            self._ashtaka_grid_layout = QGridLayout()
            """ Sudarsana Chakra Chart does not Asktaka Varga Chart - So Force North Indian """
            __chart_type = available_chart_types[self._chart_type]
            if 'sudar' in self._chart_type.lower():
                __chart_type = available_chart_types['north_indian']
            self._ashtaka_charts.append([(__chart_type(chart_size_factor=_ashtaka_chart_size_factor)) for i in range(9)])
            ac = 0
            for i in range(3):
                for j in range(3):
                    self._ashtaka_grid_layout.addWidget(self._ashtaka_charts[t][ac],i,j)
                    ac+=1
            self._ashtaka_grid_layout.setSpacing(0)
            self.horo_tabs[tab_index+t].setLayout(self._ashtaka_grid_layout)        
    def _init_main_window(self):
        self._footer_title = ''
        self.setWindowIcon(QtGui.QIcon(_IMAGE_ICON_PATH))
        self._language = list(available_languages.keys())[0]#list(available_languages.keys())[0]
        ci = _index_containing_substring(available_chart_types.keys(),self._chart_type.lower())
        if ci >=0:
            self._chart_type = list(available_chart_types.keys())[ci]
        self.setFixedSize(_main_window_width,_main_window_height)
        self.showMaximized()
        #self.setMinimumSize(_main_window_width,_main_window_height)        
    def _create_row1_ui(self):
        self._row1_h_layout = QHBoxLayout()
        self._name_label = QLabel("Name:")
        self._row1_h_layout.addWidget(self._name_label)
        self._name_text = QLineEdit("Today")
        self._name = self._name_text.text()
        self._name_text.setToolTip('Enter your name')
        self._row1_h_layout.addWidget(self._name_text)
        self._gender_combo = QComboBox()
        self._gender_combo.addItems(['Female','Male','Transgender','No preference'])
        self._gender_combo.setCurrentText('No preference')
        self._gender_combo.currentIndexChanged.connect(self._gender_changed)
        #self._gender_index = self._gender_combo.currentIndex()
        self._row1_h_layout.addWidget(self._gender_combo)
        self._place_label = QLabel("Place:")
        self._row1_h_layout.addWidget(self._place_label)
        self._place_name = ''
        self._place_text = QLineEdit(self._place_name)
        self._world_cities_list = utils.world_cities_list
        completer = QCompleter(self._world_cities_list)
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
        " Initialize with default place based on IP"
        loc = utils.get_place_from_user_ip_address()
        if loc:
            self.place(loc[0])
        self._v_layout.addLayout(self._row1_h_layout)
    def _gender_changed(self):
        self._gender_index = self._gender_combo.currentIndex()
        self._show_compatibility = False
        if self._gender_index in [0,1]:
            self._show_compatibility = True
    def _create_row_3_ui(self):
        self._row3_h_layout = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.activated.connect(self._update_main_window_label_and_tooltips)
        self._row3_h_layout.addWidget(self._lang_combo)
        self._pravesha_combo = QComboBox()
        self._pravesha_combo.addItems(const._PRAVESHA_LIST)
        self._pravesha_combo.setCurrentIndex(0)
        self._pravesha_combo.setToolTip('Choose type of Pravesha (Janma, annual, tithi, present)')
        #self._pravesha_combo.currentIndexChanged.connect(self._enable_disable_annual_ui)
        self._pravesha_combo.activated.connect(self._enable_disable_annual_ui)
        self._row3_h_layout.addWidget(self._pravesha_combo)
        self._compute_button = QPushButton("Show Chart")
        self._compute_button.setFont(QtGui.QFont("Arial Bold",9))
        self._compute_button.clicked.connect(lambda: self.compute_horoscope(calculation_type=self._calculation_type))
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
    def _create_row_2_and_3_ui(self):
        v_layout = QVBoxLayout()
        self._row2_h_layout = QHBoxLayout()
        self._dob_label = QLabel("Date of Birth:")
        self._row2_h_layout.addWidget(self._dob_label)
        self._date_of_birth = ''
        self._dob_text = QLineEdit(self._date_of_birth)
        self._dob_text.setToolTip('Date of birth in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        self._dob_label.setMaximumWidth(_row3_widget_width)
        self._dob_text.setMaximumWidth(_row3_widget_width)
        self._row2_h_layout.addWidget(self._dob_text)
        self._tob_label = QLabel("Time of Birth:")
        self._row2_h_layout.addWidget(self._tob_label)
        self._time_of_birth = ''
        self._tob_text = QLineEdit(self._time_of_birth)
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        self._tob_label.setMaximumWidth(_row3_widget_width)
        self._tob_text.setMaximumWidth(_row3_widget_width)
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self.date_of_birth(current_date_str)
        self.time_of_birth(current_time_str)
        self._row2_h_layout.addWidget(self._tob_text)
        #"""
        self._years_label=QLabel('Years')
        self._row2_h_layout.addWidget(self._years_label)
        self._years_combo = QSpinBox()
        self._years_combo.setRange(1,100)
        self._years_combo.setSingleStep(1)
        self._years_combo.setValue(1)
        self._row2_h_layout.addWidget(self._years_combo)
        self._months_label=QLabel('Months')
        self._row2_h_layout.addWidget(self._months_label)
        self._months_combo = QSpinBox()
        self._months_combo.setRange(1,12)
        self._months_combo.setSingleStep(1)
        self._months_combo.setValue(1)
        self._row2_h_layout.addWidget(self._months_combo)
        self._60hrs_label=QLabel('60 Hrs')
        self._row2_h_layout.addWidget(self._60hrs_label)
        self._60hrs_combo = QSpinBox()
        self._60hrs_combo.setRange(1,12)
        self._60hrs_combo.setSingleStep(1)
        self._60hrs_combo.setValue(1)
        self._row2_h_layout.addWidget(self._60hrs_combo)
        #"""
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
        self._create_row_3_ui()
        v_layout.addLayout(self._row3_h_layout)
        self._v_layout.addLayout(v_layout)
    def _create_comp_ui(self):
        self._comp_h_layout = QHBoxLayout()
        self._show_marriage_checkboxes = True # V2.6.1
        self._mahendra_porutham_checkbox = QCheckBox()
        self._mahendra_porutham_checkbox.setChecked(False)
        self._mahendra_porutham = self._mahendra_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._mahendra_porutham_checkbox)
        self._vedha_porutham_checkbox = QCheckBox()
        self._vedha_porutham_checkbox.setChecked(False)
        self._vedha_porutham = self._vedha_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._vedha_porutham_checkbox)
        self._rajju_porutham_checkbox = QCheckBox()
        self._rajju_porutham_checkbox.setChecked(False)
        self._rajju_porutham = self._rajju_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._rajju_porutham_checkbox)
        self._sthree_dheerga_porutham_checkbox = QCheckBox()
        self._sthree_dheerga_porutham_checkbox.setChecked(False)
        self._sthree_dheerga_porutham = self._sthree_dheerga_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._sthree_dheerga_porutham_checkbox)
        self._min_score_label = QLabel('')
        self._comp_h_layout.addWidget(self._min_score_label)
        self._min_score_combo = QDoubleSpinBox()
        if 'south' in self._chart_type.lower():
            self._min_score_combo.setValue(const.compatibility_minimum_score_south)
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_south)
            self._min_score_combo.setSingleStep(1.0)
        else:
            self._min_score_combo.setValue(const.compatibility_minimum_score_north)
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_north)
            self._min_score_combo.setSingleStep(0.5)
        self._comp_h_layout.addWidget(self._min_score_combo)
        self._v_layout.addLayout(self._comp_h_layout)
        self._comp_h_layout = QHBoxLayout()
        #self._dhasa_bhukthi_combo = QComboBox()
        #self._dhasa_bhukthi_combo.addItems([db.replace('_str','') for db in _dhasa_bhukthi_combo_list])
        #self._comp_h_layout.addWidget(self._dhasa_bhukthi_combo)
        self._show_hide_marriage_checkboxes(True)
        self._v_layout.addLayout(self._comp_h_layout)
    def _show_vratha_finder_dialog(self):
        year,month,day = self._date_of_birth.split(","); dob = (int(year),int(month),int(day))
        #tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        tob = tuple([int(x) for x in self._time_of_birth.split(':')])
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        from hora.ui import vratha_finder
        jd_at_dob = utils.julian_day_number(dob, tob)
        dlg = vratha_finder.VrathaFinderDialog(jd_at_dob,place)
        self._conjunction_dialog_accepted = False
        if dlg.exec()==1:
            self._conjunction_dialog_accepted = dlg._accept_clicked
            vrath_jd = dlg._selection_date_jd
            y,m,d,fh = utils.jd_to_gregorian(vrath_jd)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
            #print(self._date_of_birth,self._time_of_birth)
        else:
            # Reset   pravesha_combo selection to 0
            self._pravesha_combo.setCurrentIndex(0)
            self.compute_horoscope(self._calculation_type)           
    def _show_conjunction_dialog(self,entry_type=0):
        #year,month,day = self._dob_text.text().split(","); dob = (int(year),int(month),int(day))
        year,month,day = self._date_of_birth.split(","); dob = (int(year),int(month),int(day))
        #tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        tob = tuple([int(x) for x in self._time_of_birth.split(':')])
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        from hora.ui import conjunction_dialog
        jd_at_dob = utils.julian_day_number(dob, tob)
        dlg = conjunction_dialog.ConjunctionDialog(jd_at_dob,place,entry_type=entry_type)
        self._conjunction_dialog_accepted = False
        if dlg.exec()==1:
            self._conjunction_dialog_accepted = dlg._accept_clicked
            conj_jd = dlg._conjunction_date_jd
            y,m,d,fh = utils.jd_to_gregorian(conj_jd)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
            self._conj_planet1 = dlg._planet1
            if entry_type==0:
                self._conj_planet2 = dlg._planet2
                self._separation_angle_list = dlg._sep_angle_list
                self._separation_angle_index = dlg._separation_angle_index
            elif entry_type==1:
                self._conj_raasi = None if dlg._raasi==None else dlg._raasi-1
        else:
            # Reset   pravesha_combo selection to 0
            self._pravesha_combo.setCurrentIndex(0)
            #self.compute_horoscope(self._calculation_type)           
    def _enable_disable_annual_ui(self):
        year,month,day = self._dob_text.text().split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        user_age = min(datetime.now().year - birth_date.year, const.annual_maximum_age) + 1
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        self._birth_julian_day = utils.julian_day_number(dob, tob)
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        self._years_combo.setValue(1); self._60hrs_combo.setValue(1); self._months_combo.setValue(1)
        self._years_combo.setEnabled(False); self._months_combo.setEnabled(False); self._60hrs_combo.setEnabled(False)
        if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('birth_str'):
            self._years = 1; self._60hrs = 1; self._months = 1
            self._years_combo.setEnabled(False); self._months_combo.setEnabled(False); self._60hrs_combo.setEnabled(False)
            self._date_of_birth = self._dob_text.text()
            self._time_of_birth = self._tob_text.text()
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('annual_str'): 
            jd_at_dob = utils.julian_day_number(dob, tob)
            jd_years = drik.next_solar_date(jd_at_dob, place, user_age, self._months, self._60hrs)
            y,m,d,fh = utils.jd_to_gregorian(jd_years)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('tithi_pravesha_str'):
            from hora.panchanga import vratha
            tp = vratha.tithi_pravesha(birth_date, tob, place, user_age)
            tp_date = tp[0][0]; tp_time = tp[0][1]; tithi_time = tuple(utils.to_dms(tp_time,as_string=False))
            tp_date_new = drik.Date(tp_date[0],tp_date[1],tp_date[2])
            jd_years = utils.julian_day_number(tp_date_new, tithi_time)
            y,m,d,fh = utils.jd_to_gregorian(jd_years)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('present_str'):
            timezone_offset = self._time_zone
            tzinfo = timezone(timedelta(hours=timezone_offset))
            today = datetime.now(tzinfo)
            self._date_of_birth = today.strftime("%Y,%m,%d"); self._time_of_birth = today.strftime("%H:%M:%S")
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str') \
                or self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planet_transit_str') \
                or self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vakra_gathi_change_str'):
            pass
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('prenatal_time_str'):
            jd_at_dob = utils.julian_day_number(dob, tob)
            jd_prenatal = drik._nisheka_time(jd_at_dob, place)
            y,m,d,fh = utils.jd_to_gregorian(jd_prenatal)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])            
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vrathas_str'):
            timezone_offset = self._time_zone
            tzinfo = timezone(timedelta(hours=timezone_offset))
            today = datetime.now(tzinfo)
            self._date_of_birth = today.strftime("%Y,%m,%d"); self._time_of_birth = today.strftime("%H:%M:%S")
        else:
            self._years_combo.setValue(1); self._60hrs_combo.setValue(1); self._months_combo.setValue(1)
            self._years_combo.setEnabled(True); self._months_combo.setEnabled(True); self._60hrs_combo.setEnabled(True)
            self._date_of_birth = self._dob_text.text()
            self._time_of_birth = self._tob_text.text()
            
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
    def ayanamsa_mode(self, ayanamsa_mode, ayanamsa=None):
        """
            Set Ayanamsa mode
            @param ayanamsa_mode - Default - Lahiri
            See 'drik.available_ayanamsa_modes' for the list of available models
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
        result = utils.get_location(place_name)
        if result == None:
            return
        [self._place_name,self._latitude,self._longitude,self._time_zone] = result
        self._lat_text.setText(str(self._latitude))
        self._long_text.setText(str(self._longitude))
        self._tz_text.setText(str(self._time_zone))
    def name(self,name):
        """
            Set name of the person whose horoscope is sought
            @param - Name of person
        """
        self._name = name
        self._name_text.setText(name)
    def gender(self,gender_index):
        """
            set gender of the person whose horoscope is sought
            @param gender_index: range 0..3 0=>Male, 1=>Female, 2=> Transgender 3=>No option 
        """
        if gender_index in [0,1,2,3]:
            self._gender_combo.setCurrentIndex(gender_index)
            self._gender = self._gender_combo.currentText()
        if gender_index >= 2:
            """ Disable compatibility ui if no male/femal selected """
            self._show_compatibility = False

    def chart_type(self,chart_type):
        """
            Set chart type of the horoscope
            @param - chart_type:
                options: 'south_indian'. 'north_indian', 'west_indian', 'western', 'sudarsana_chakra'
                Default: south_indian
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
        if 'south' in self._chart_type.lower():
            if self._show_compatibility and  minm_comp_score>0 and minm_comp_score <= const.compatibility_maximum_score_south:
                self._minimum_score = minm_comp_score
                self._min_score_combo.setValue(minm_comp_score)
        else:
            if self._show_compatibility and  minm_comp_score>0.0 and minm_comp_score <= const.compatibility_maximum_score_north:
                self._minimum_score = minm_comp_score
                self._min_score_combo.setValue(minm_comp_score)
    def _validate_ui(self):
        all_data_ok = self._place_text.text().strip() != '' and \
                         self._name_text.text().strip() != '' and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._lat_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._long_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d{1,5}\,\d{1,2}\,\d{1,2}", self._dob_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"\d{1,2}:\d{1,2}:\d{1,2}", self._tob_text.text().strip(),re.IGNORECASE)
        return all_data_ok
    def _update_main_window_label_and_tooltips(self):
        try:
            if self.resources:
                msgs = self.resources
                self._name_label.setText(msgs['name_str'])
                self._name_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._name_label.setToolTip(msgs['name_tooltip_str'])
                _gender_index = self._gender_combo.currentIndex()
                self._gender_combo.clear()
                self._gender_combo.addItems([msgs['gender_male_str'],msgs['gender_female_str'],msgs['gender_transgender_str'],msgs['gender_no_preference_str']])
                self._gender_combo.setCurrentIndex(_gender_index)
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
                _pravesha_index = self._pravesha_combo.currentIndex()
                _years_prev = self._years; _months_prev = self._months; _60hrs_prev=self._60hrs
                self._pravesha_combo.clear()
                self._pravesha_combo.addItems([msgs[p] for p in const._PRAVESHA_LIST])
                self._pravesha_combo.setCurrentIndex(_pravesha_index)
                self._years = _years_prev; self._months = _months_prev; self._60hrs = _60hrs_prev
                self._years_label.setText(msgs['years_str'])
                self._months_label.setText(msgs['months_str'])
                self._60hrs_label.setText(msgs['60hrs_str'])
                _chart_type_index = self._chart_type_combo.currentIndex()
                self._chart_type_combo.clear()
                self._chart_type_combo.addItems([msgs[c+'_str'] for c in available_chart_types.keys()])
                _language_index = self._lang_combo.currentIndex()
                self._lang_combo.clear()
                self._lang_combo.addItems([msgs[l.lower()+'_str'] for l in const.available_languages.keys()])
                self._lang_combo.setCurrentIndex(_language_index)
                self._chart_type_combo.setCurrentIndex(_chart_type_index)
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
                self._mahendra_porutham_checkbox.setText(msgs['mahendra_match_str'])#.split()[0])
                self._mahendra_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._mahendra_porutham_checkbox.setToolTip(msgs['mahendra_tooltip_str'])
                self._vedha_porutham_checkbox.setText(msgs['vedha_match_str'])#.split()[0])
                self._vedha_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._vedha_porutham_checkbox.setToolTip(msgs['vedha_tooltip_str'])
                self._rajju_porutham_checkbox.setText(msgs['rajju_match_str'])#.split()[0])
                self._rajju_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._rajju_porutham_checkbox.setToolTip(msgs['rajju_tooltip_str'])
                self._sthree_dheerga_porutham_checkbox.setText(msgs['sthree_dheerga_match_str'])#.split()[0])
                self._sthree_dheerga_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._sthree_dheerga_porutham_checkbox.setToolTip(msgs['sthree_dheerga_tooltip_str'])
                self._min_score_label.setText(msgs['min_score_label_str'])
                self._min_score_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._min_score_label.setToolTip(msgs['min_score_tooltip_str'])
                self._footer_label.setText(msgs['window_footer_title'])
                self.setWindowTitle(msgs['window_title']+'-'+_APP_VERSION)
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
        self._gender = self._gender_combo.currentText()
        self._place_name = self._place_text.text()
        self._latitude = float(self._lat_text.text())
        self._longitude = float(self._long_text.text())
        self._time_zone = float(self._tz_text.text())
        self._language = list(const.available_languages.keys())[self._lang_combo.currentIndex()]
        year,month,day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        self._years = self._years_combo.value()
        self._months = self._months_combo.value()
        self._60hrs = self._60hrs_combo.value()
        if self._place_name.strip() == "":
            print("Please enter a place of birth")
            return
        self._ayanamsa_mode =  self._ayanamsa_combo.currentText()
        if self._place_name.strip() == '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0: 
            [self._place_name,self._latitude,self._longitude,self._time_zone] = \
                utils.get_location_using_nominatim(self._place_name)
            self._lat_text.setText((self._latitude))
            self._long_text.setText((self._longitude))
            self._tz_text.setText((self._time_zone))
        self._enable_disable_annual_ui()
        if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str'):
            self._show_conjunction_dialog(entry_type=0)
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planet_transit_str'):
            self._show_conjunction_dialog(entry_type=1)
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vakra_gathi_change_str'):
            self._show_conjunction_dialog(entry_type=2)
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vrathas_str'):
            self._show_vratha_finder_dialog()
            year,month,day = self._date_of_birth.split(",")
            birth_date = drik.Date(int(year),int(month),int(day))
            """ TODO: For vrathas Show only Panchangam page updated and return """
            if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
                self._horo= main.Horoscope(latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,
                                           date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,
                                           ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                           years=self._years,months=self._months,sixty_hours=self._60hrs,
                                           pravesha_type=self._pravesha_combo.currentIndex(),language=available_languages[self._language])
            else:
                self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,
                                           ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                           years=self._years,months=self._months,sixty_hours=self._60hrs,
                                           pravesha_type=self._pravesha_combo.currentIndex(),language=available_languages[self._language])
            self._calendar_info = self._horo.calendar_info
            self.resources = self._horo.cal_key_list
            info_str = ''
            format_str = '%-20s%-40s\n'
            self._fill_information_label1(info_str, format_str)
            self._fill_information_label2(info_str, format_str)
            return
        """ reset birth_date again based on self._date_of_birth and self._time_of_birth from pravesha functions """
        year,month,day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        self._chart_type = list(available_chart_types)[self._chart_type_combo.currentIndex()]
        ' set the chart type and reset widgets'
        self._recreate_chart_tab_widgets()
        self._western_chart = False
        if 'west' in self._chart_type.lower():
            self._western_chart = True
            self.tabNames = _tab_names[:_chart_tab_end]
        if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
            self._horo= main.Horoscope(latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,
                                       date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,
                                       ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       years=self._years,months=self._months,sixty_hours=self._60hrs,
                                       pravesha_type=self._pravesha_combo.currentIndex(),language=available_languages[self._language])
        else:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,
                                       ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       years=self._years,months=self._months,sixty_hours=self._60hrs,
                                       pravesha_type=self._pravesha_combo.currentIndex(),language=available_languages[self._language])
        """
        self._calendar_info = self._horo.get_calendar_information(language=available_languages[self._language])
        self.resources= self._horo._get_calendar_resource_strings(language=available_languages[self._language])
        self._horoscope_info, self._horoscope_charts = self._horo.get_horoscope_information(language=available_languages[self._language])
        """
        self._calendar_info = self._horo.calendar_info
        self.resources = self._horo.cal_key_list
        self._horoscope_info = self._horo.horoscope_info; self._horoscope_charts = self._horo.horoscope_charts
        if not self._western_chart:
            """ TODO: Should we change dob,tob to birth date/time here """
            dob = self._horo.Date
            tob = self._horo.birth_time
            #dob = self._dob_text.text().split(','); dob = drik.Date(dob[0],dob[1],dob[2])
            #tob = self._tob_text.text().split(':')
            place = self._horo.Place
            for tab_str,tab_values in _graha_dhasa_dict.items():
                retval = eval('self._horo._get_'+tab_str+'_dhasa_bhukthi(dob, tob, place)')
                tab_values[7] = retval
            r = 0
            for tab_str,tab_values in _rasi_dhasa_dict.items():
                retval = eval('self._horo._get_'+tab_str+'_dhasa(dob, tob, place)')
                tab_values[7] = retval
            _db_info = self._horo._get_annual_dhasa_bhukthi()
            r = 0
            for tab_str,tab_values in _annual_dhasa_dict.items():
                tab_values[7] = _db_info[r]
                r+=1
            self._horo._get_arudha_padhas(dob, tob, place, divisional_chart_factor=1,
                                          years=self._years,months=self._months,sixty_hours=self._60hrs)
            self._amsa_bala_info = self._horo._get_amsa_bala(dob, tob, place)
            self._other_bala_info = self._horo._get_other_bala(dob, tob, place)
            self._shad_bala_info = self._horo._get_shad_bala(dob, tob, place)
            self._bhava_bala_info = self._horo._get_bhava_bala(dob, tob, place)
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
        jd = self._horo.julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        bt=self._horo.birth_time
        tob = bt[0]+bt[1]/60.0+bt[2]/3600.0
        self._years_combo.setValue(self._years)
        self._months_combo.setValue(self._months)
        self._60hrs_combo.setValue(self._60hrs)
        jd_years = drik.next_solar_date(jd, place, self._years, self._months, self._60hrs)
        yb, mb, db, hfb = utils.jd_to_gregorian(jd)
        yy, my, dy, hfy = utils.jd_to_gregorian(jd_years)
        self._date_text_dob =  '%04d-%02d-%02d' %(yb,mb,db)
        self._time_text_dob = utils.to_dms(hfb,as_string=True)
        self._date_text_years =  '%04d-%02d-%02d' %(yy,my,dy)
        self._time_text_years = utils.to_dms(hfy,as_string=True)
        self._lat_chart_text = utils.to_dms(self._latitude,is_lat_long='lat')
        self._long_chart_text = utils.to_dms(self._longitude,is_lat_long='long')
        if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('tithi_pravesha_str'):
            year_number = yb + self._years - 1
            from hora.panchanga import vratha
            birth_date = self._horo.Date
            birth_time = self._horo.birth_time
            place = self._horo.Place
            tp = vratha.tithi_pravesha(birth_date, birth_time, place, year_number)
            tp_date = tp[0][0]; hfy = tp[0][1];
            yy=tp_date[0]; my=tp_date[1]; dy = tp_date[2]
            self._date_text_years =  '%04d-%02d-%02d' %(yy,my,dy)
            self._time_text_years = utils.to_dms(hfy,as_string=True)
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str'):
            self._date_text_dob =  '%04d-%02d-%02d' %(yy,my,dy)
            self._time_text_dob = utils.to_dms(hfy,as_string=True)
            #jd = jd_years
        self._timezone_text = '(GMT '+str(self._tz_text.text())+')'
        key = 'date_of_birth_str'
        info_str += format_str % (self.resources[key],self._date_text_dob)
        key = 'time_of_birth_str'
        info_str += format_str % (self.resources[key],self._time_text_dob)
        info_str += format_str % (self.resources['udhayathi_str'], utils.udhayadhi_nazhikai(jd,place)[0])
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
        jd = self._horo.julian_day#V3.2.0
        key = self.resources['bhava_lagna_str']
        value = drik.bhava_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['hora_lagna_str']
        value = drik.hora_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['ghati_lagna_str']
        value = drik.ghati_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['vighati_lagna_str']
        value = drik.vighati_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['pranapada_lagna_str']
        value = drik.pranapada_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['indu_lagna_str']
        value = drik.indu_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['bhrigu_bindhu_lagna_str']
        value = drik.bhrigu_bindhu(jd,place,divisional_chart_factor=1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['sree_lagna_str']
        value = drik.sree_lagna(jd,place,divisional_chart_factor=1)
        jd = self._horo.julian_day # V3.1.9
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        #key = self.resources['raasi_str']+'-'+self.resources['ascendant_str']
        #value = self._horoscope_info[key]
        value = drik.ascendant(jd, place)
        info_str += format_str % (self.resources['ascendant_str'],utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong'))
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
        """ TODO: This part of code assumes vimsottari dhasa date is in string format "y-m-d" and not "y-m-d H:M:S" 
            Need to figure out alternate means of calculating _dhasa balance"""
        _vimsottari_dhasa_bhukti_info = _graha_dhasa_dict['vimsottari'][-1]
        _vim_balance = ':'.join(map(str,self._horo._vimsottari_balance))
        dhasa = [k for k,_ in _vimsottari_dhasa_bhukti_info][8].split('-')[0]
        value = _vim_balance
        key = dhasa + ' '+self.resources['balance_str']
        info_str += format_str % (key,value)
        dhasa = ''
        dhasa_end_date = ''
        di = 9
        for p,(k,v) in enumerate(_vimsottari_dhasa_bhukti_info):
            # get dhasa
            if (p+1) == di:
                dhasa = k.split("-")[0]
            # Get dhasa end Date
            elif (p+1) == di+1:
                """ to account for BC Dates negative sign is introduced"""
                if len(v.split('-')) == 4:
                    _,year,month,day = v.split('-')
                    year = '-'+year
                else:
                    year,month,day = v.split('-')
                dd = day.split(' ')[0] # REMOVE TIME STRING FROM VIMSOTTARI DATES
                dhasa_end_date = year+'-'+month+'-'+str(int(dd)-1)+ ' '+self.resources['ends_at_str']
                info_str += format_str % (dhasa, dhasa_end_date)
                di += 9
        #key = self.resources['maasa_str']
        key = self.resources['tamil_month_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['ayanamsam_str']+' ('+self._ayanamsa_mode+') '
        value = drik.get_ayanamsa_value(self._horo.julian_day)
        self._ayanamsa_value = value
        value = utils.to_dms(value,as_string=True,is_lat_long='lat').replace('N','').replace('S','')
        print("horo_chart: Ayanamsa mode",key,'set to value',value)
        info_str += format_str % (key,value)
        #key = self.resources['samvatsara_str']
        key = self.resources['lunar_year_month_str']
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
        key = self.resources['calculation_type_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        self._info_label2.setText(info_str)
    def _convert_1d_chart_with_planet_names(self,chart_1d_list): #To be used for Sudarsana Chakra data as input
        from hora.horoscope.chart import house
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
                        pl_str += self.resources['ascendant_short_str']+'/'#' 'Lagnam'+'/'#const._ascendant_symbol+"/"
                    else:
                        ret_str = ''
                        if int(p) in retrograde_planets:
                            ret_str = const._retrogade_symbol
                        pl_str += utils.PLANET_SHORT_NAMES[int(p)]+ret_str+'/'# house.planet_list[int(p)]+'/'#const._planet_symbols[int(p)]+'/'
                pl_str = pl_str[:-1]
                res.append((z,pl_str))
            result.append(res)
        return result
    def _update_tabs_with_divisional_charts(self,jd,place):
        i_end = 0
        format_str = '%-18s%-20s\n'
        _chart_title_separator = ' '; tab_str=''
        if 'south' in self._chart_type.lower() or 'east' in self._chart_type.lower():
            _chart_title_separator = '\n'
        if int(self._months_combo.text()) > 1:
            tab_str = self.resources['monthly_str']+_chart_title_separator
        elif int(self._60hrs_combo.text()) > 1:
            tab_str = self.resources['60hourly_str']+_chart_title_separator
        elif self._conjunction_dialog_accepted:
            _pravesha_index = const._PRAVESHA_LIST[self._pravesha_combo.currentIndex()]
            pstr = ''
            if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str'):
                pstr = utils.PLANET_NAMES[self._conj_planet1]+'/'+utils.PLANET_NAMES[self._conj_planet2]
                pstr += '-'+self._separation_angle_list[self._separation_angle_index]
            elif (self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planet_transit_str')):
                if self._conj_raasi == None:
                    pstr = utils.PLANET_NAMES[self._conj_planet1]
                else:
                    pstr = utils.RAASI_LIST[self._conj_raasi] + '-'+utils.PLANET_NAMES[self._conj_planet1]
            elif (self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vakra_gathi_change_str')):
                pstr = utils.PLANET_NAMES[self._conj_planet1]
            tab_str = pstr+_chart_title_separator
        elif int(self._years_combo.text()) > 1:
            tab_str = self.resources['annual_str']+_chart_title_separator
        else:
            _pravesha_index = const._PRAVESHA_LIST[self._pravesha_combo.currentIndex()]
            tab_str = self.resources[_pravesha_index]+_chart_title_separator
            
        self.tabWidget.setTabText(0,self.resources[self.tabNames[0]])
        _arudha_lagnas_count = len(_arudha_lagnas_included_in_chart.keys())
        planet_count = len(drik.planet_list) + 1 # Inlcuding Lagnam
        upagraha_count = len(const._solar_upagraha_list) + len(const._other_upagraha_list)# + 1 # +1 for upajethu title row
        special_lagna_count = len(const._special_lagna_list)
        total_row_count = _arudha_lagnas_count + planet_count + upagraha_count + special_lagna_count
        for t,tab in enumerate(self.tabNames[1:_chart_tab_end]): #_vimsottari_dhasa_tab_start]):
            dcf = const.division_chart_factors[t]
            """ update the chart from horoscope charts """
            tab_name = tab_str + self.resources[tab]
            _chart_title = tab_name + _chart_title_separator+self._date_text_years + \
                            _chart_title_separator+self._time_text_years +_chart_title_separator + \
                            self._timezone_text + _chart_title_separator + self._place_name + _chart_title_separator + \
                            self._lat_chart_text + " , " + self._long_chart_text
            self.tabWidget.setTabText(t+1,tab_name.replace('\n','-'))
            i_start = i_end # (t-1)*10
            # 26 #29 # 4 for special lagnas, 10 from lagnam and planets, 12 rows for upagraha details
            i_end = i_start + total_row_count
            chart_info = ''
            western_data = []
            if self._western_chart:
                i_start = i_start + special_lagna_count + _arudha_lagnas_count #  Skip Arudha Lagna count and  special lagna rows
                i_end = i_start + planet_count #10 # 13 # count of planets + lagnam
            i_i = -1
            for (k,v) in list(self._horoscope_info.items())[i_start:i_end]:
                i_i += 1
                k1 = k.split('-')[-1]
                v1 = v.split('-')[0]
                chart_info += format_str % (k1,v1)
                western_data.append(k1+' '+v1)
            if self._western_chart:
                i_end += upagraha_count#12
            self._chart_info_labels[t].setText(chart_info) # Fixed defect here in 1.0.2
            self._chart_info_labels[t].setMaximumWidth(_chart_info_label_width)  # Fixed defect here in 1.0.2
            chart_data_1d = self._horoscope_charts[t]
            chart_data_1d = [x[:-1] for x in chart_data_1d] # remove ]n from end of each element
            # combine hora and ghati lagna
            hl = self._horo._hora_lagna_data[dcf]; gl = self._horo._ghati_lagna_data[dcf]; vl = self._horo._vighati_lagna_data[dcf]
            bl = self._horo._bhava_lagna_data[dcf]; sl = self._horo._sree_lagna_data[dcf] # V3.1.9
            if const.include_maandhi_in_charts: ml = self._horo._maandhi_data[dcf]
            adc = []
            if const.include_special_and_arudha_lagna_in_charts:
                for k,v in enumerate(self._horo._arudha_lagna_data[dcf]):
                    v1 = v
                    if k== bl:
                        v1 += '\n' + self.resources['bhava_lagna_short_str'] # V3.1.9
                    if k== sl:
                        v1 += '\n' + self.resources['sree_lagna_short_str'] # V3.1.9
                    if k== hl:
                        v1 += '\n' + self.resources['hora_lagna_short_str']
                    if k== gl:
                        v1 += '\n' + self.resources['ghati_lagna_short_str']
                    if k== vl:
                        v1 += '\n' + self.resources['vighati_lagna_short_str']
                    if const.include_maandhi_in_charts and k== ml:
                        v1 += '\n' + self.resources['maandi_str']
                    adc.append(v1.strip())            
            self._horo._arudha_lagna_data[dcf] = adc
            self._western_chart = False
            if 'north' in self._chart_type.lower():
                _ascendant = drik.ascendant(jd,place)
                asc_house = _ascendant[0]+1
                self._charts[t]._asc_house = asc_house
                chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
                ald_north = self._horo._arudha_lagna_data[dcf][:]
                ald_north = ald_north[asc_house-1:]+ald_north[0:asc_house-1]
                self._charts[t].setData(chart_data_north,chart_title=_chart_title,chart_title_font_size=north_chart_title_font_size,
                                        arudha_lagna_data=ald_north)
            elif 'east' in self._chart_type.lower():
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
                arudha_lagna_data_2d = _convert_1d_house_data_to_2d(self._horo._arudha_lagna_data[dcf],self._chart_type)
                self._charts[t]._asc_house = row*self._charts[t].row_count+col
                self._charts[t].setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=east_chart_title_font_size,arudha_lagna_data=arudha_lagna_data_2d)
            elif 'west' in self._chart_type.lower():
                self._western_chart = True
                self._charts[t].setData(western_data,chart_title=_chart_title,chart_title_font_size=west_chart_title_font_size)
                self._charts[t].update()                
            elif 'sudar' in self._chart_type.lower():
                dcf = const.division_chart_factors[t]
                chart_1d = sudharsana_chakra.sudharshana_chakra_chart(jd, place,self._date_of_birth,years_from_dob=0, divisional_chart_factor=dcf)
                data_1d = self._convert_1d_chart_with_planet_names(chart_1d)
                self._charts[t].setData(data_1d,chart_title=_chart_title,chart_title_font_size=sudarsana_chakra_chart_title_font_size)
                self._charts[t].update()                
            else: # south indian'
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
                arudha_lagna_data_2d = _convert_1d_house_data_to_2d(self._horo._arudha_lagna_data[dcf])
                self._charts[t]._asc_house = (row,col)
                self._charts[t].setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=south_chart_title_font_size,arudha_lagna_data=arudha_lagna_data_2d)
            self._charts[t].update()
    def _update_tab_chart_information(self):
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._update_tabs_with_divisional_charts(jd,place)
    def _update_table_tab_information(self,tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=True):#,app_check=True):
        self._show_hide_marriage_checkboxes(False)
        tab_title = tab_title_str
        if dhasa_bhukti:
            tab_title = tab_title_str+'-'+self.resources['dhasa_bhukthi_str']
        table_index = 0
        for db_tab in range(tab_count):
            p = db_tab*(rows_per_table)*tables_per_tab
            for col in range(tables_per_tab):
                i_start = p
                i_end = i_start + rows_per_table
                db_list = table_info[i_start:i_end]
                if not db_list:
                    continue
                if dhasa_bhukti:
                    db_str = db_list[0][0].split('-')[0]+' '+self.resources['dhasa_str']
                    db_tables[db_tab][col].setHorizontalHeaderItem(0,QTableWidgetItem(db_str+'\n'+self.resources['starts_at_str']))
                else:
                    db_tables[db_tab][col].setHorizontalHeaderItem(0,QTableWidgetItem(table_titles[table_index]))
                t_row = 0
                for k,v in db_list:
                    k1 = k
                    if dhasa_bhukti:
                        k1 = k.split('-')[-1]+' '+self.resources['bhukthi_str']
                    db_tables[db_tab][col].setVerticalHeaderItem(t_row,QTableWidgetItem(str(k1)))
                    db_tables[db_tab][col].setItem(t_row,0,QTableWidgetItem(str(v)))
                    t_row += 1
                p = i_end
                table_index += 1
                db_tables[db_tab][col].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
                db_tables[db_tab][col].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
                db_tables[db_tab][col].verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                db_tables[db_tab][col].horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.tabWidget.setTabText(tab_start+db_tab,tab_title+'-'+str(db_tab+1))            
    def _update_sphuta_tab_information(self):
        tab_title_str = self.resources['sphuta_str']
        tab_start = _sphuta_tab_start
        tab_count = _sphuta_tab_count
        tables_per_tab = self._sphuta_tables_per_tab
        rows_per_table = self._sphuta_rows_per_table
        table_info = []
        for k,v in list(self._horo._sphuta_data.items()):
            k1 = re.sub(r"^(D\d+\-)*","",k)
            table_info.append((k1,v))
        db_tables = self.sphuta_db_tables
        table_titles = ['D'+str(dcf)+'\n'+self.resources['sphuta_str'] for dcf in const.division_chart_factors ]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_graha_arudha_tab_information(self):
        tab_title_str = self.resources['graha_arudha_str']
        tab_start = _graha_arudha_tab_start
        tab_count = _graha_arudha_tab_count
        tables_per_tab = self._arudha_tables_per_tab
        rows_per_table = self._arudha_rows_per_table
        table_info = []
        for k,v in list(self._horo._graha_lagna_data.items()):
            k1 = re.sub(r"^(D\d+\-)*","",k)
            table_info.append((k1,v))
        db_tables = self.arudha_db_tables
        table_titles = ['D'+str(dcf)+'\n'+self.resources['graha_arudha_str'] for dcf in const.division_chart_factors ]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_amsa_bala_tab_information(self):
        #"""
        tab_title_str = self.resources['amsa_bala_str']
        tab_start = _amsa_bala_tab_start
        tab_count = _amsa_bala_tab_count
        tables_per_tab = self._amsa_bala_tables_per_tab
        rows_per_table = self._amsa_bala_rows_per_table
        table_info = [(k,v) for dbl in self._amsa_bala_info for k,v in dbl.items() ]
        db_tables = self.amsa_bala_db_tables
        table_titles = [self.resources[t]+'\n'+self.resources['vimsopaka_score_str'] for t in ['shadvarga_bala_str','sapthavarga_bala_str','dhasavarga_bala_str','shodhasavarga_bala_str']]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_other_bala_tab_information(self):
        tab_title_str = self.resources['harsha_pancha_dwadhasa_vargeeya_bala_str']
        tab_start = _other_bala_tab_start
        tab_count = _other_bala_tab_count
        tables_per_tab = self._other_bala_tables_per_tab
        rows_per_table = self._other_bala_rows_per_table
        table_info = [(k,v) for dbl in self._other_bala_info for k,v in dbl.items() ]
        db_tables = self.other_bala_db_tables
        table_titles = [self.resources[t] for t in ['harsha_bala_str','pancha_vargeeya_bala_str','dwadhasa_vargeeya_bala_str']]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_dhasa_bhukthi_tab_information(self):
        for tab_str,tab_values in _graha_dhasa_dict.items():
            tab_title_str = self.resources['graha_str']+'-'+self.resources[tab_str+'_str']
            tab_start = tab_values[5]
            tab_count = tab_values[0]
            rows_per_table= tab_values[3]
            tables_per_tab = tab_values[2]
            table_info = tab_values[7]
            db_tables=tab_values[6]
            table_titles=''
            dhasa_bhukti=True
            self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=True)                       
        for tab_str,tab_values in _rasi_dhasa_dict.items():
            tab_title_str = self.resources['raasi_str']+'-'+self.resources[tab_str+'_str']
            tab_start = tab_values[5]
            tab_count = tab_values[0]
            rows_per_table= tab_values[3]
            tables_per_tab = tab_values[2]
            table_info = tab_values[7]
            db_tables=tab_values[6]
            table_titles=''
            dhasa_bhukti=True
            self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=True)                       
        _pravesha_index = const._PRAVESHA_LIST[self._pravesha_combo.currentIndex()]
        _pravesha_str = self.resources[_pravesha_index]
        for tab_str,tab_values in _annual_dhasa_dict.items():
            tab_title_str = _pravesha_str+'-'+self.resources[tab_str+'_str']
            tab_start = tab_values[5]
            tab_count = tab_values[0]
            rows_per_table= tab_values[3]
            tables_per_tab = tab_values[2]
            table_info = tab_values[7]
            db_tables=tab_values[6]
            table_titles=''
            dhasa_bhukti=True
            self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=True)                       
        return            
    def _show_hide_marriage_checkboxes(self,_show = True):
        self._mahendra_porutham_checkbox.setVisible(_show)
        self._vedha_porutham_checkbox.setVisible(_show)
        self._rajju_porutham_checkbox.setVisible(_show)
        self._sthree_dheerga_porutham_checkbox.setVisible(_show)
        self._min_score_label.setVisible(_show)
        self._min_score_combo.setVisible(_show)
    def _update_shad_bala_table_information(self):
        tab_name = self.resources['shad_bala_str']
        self.tabWidget.setTabText(_shad_bala_tab_start,tab_name)
        column_names = utils.PLANET_NAMES[:7]
        row_names = ['sthaana_bala_str','kaala_bala_str','dig_bala_str','chesta_bala_str','naisargika_bala_str',
                     'drik_bala_str','shad_bala_str','shad_bala_rupas_str','shad_bala_strength_str']
        row_count = self._shad_bala_table[0].rowCount()
        col_count = self._shad_bala_table[0].columnCount()
        _sb_info = self._shad_bala_info
        for row in range(row_count):
            for col in range(col_count):
                cell_value = str(_sb_info[row][col])
                self._shad_bala_table[0].setItem(row,col,QTableWidgetItem(cell_value))
        for row in range(row_count):
            shad_str = self.resources[row_names[row]]
            self._shad_bala_table[0].setVerticalHeaderItem(row,QTableWidgetItem(shad_str))
            self._shad_bala_table[0].resizeRowToContents(row)
        for col in range(col_count):
            header = column_names[col]
            self._shad_bala_table[0].setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._shad_bala_table[0].resizeColumnToContents(col)
        self._shad_bala_table[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._shad_bala_table[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_bhava_bala_table_information(self):
        tab_name = self.resources['bhava_bala_str']
        self.tabWidget.setTabText(_bhava_bala_tab_start,tab_name)
        row_names = [self.resources['house_str']+'-'+str(h+1) for h in range(12)]
        column_names = ['bhava_bala_str','bhava_bala_rupas_str','bhava_bala_strength_str']
        row_count = self._bhava_bala_table[0].rowCount()
        col_count = self._bhava_bala_table[0].columnCount()
        _sb_info = self._bhava_bala_info
        for row in range(row_count):
            for col in range(col_count):
                cell_value = str(_sb_info[row][col])
                self._bhava_bala_table[0].setItem(row,col,QTableWidgetItem(cell_value))
        for row in range(row_count):
            bhava_str = row_names[row]
            self._bhava_bala_table[0].setVerticalHeaderItem(row,QTableWidgetItem(bhava_str))
            self._bhava_bala_table[0].resizeRowToContents(row)
        for col in range(col_count):
            header = self.resources[column_names[col]]
            self._bhava_bala_table[0].setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._bhava_bala_table[0].resizeColumnToContents(col)
        self._bhava_bala_table[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._bhava_bala_table[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_argala_table_information(self):
        tab_name = self.resources['argala_str']+'-'+self.resources['virodhargala_str']
        self.tabWidget.setTabText(_argala_tab_start,tab_name)
        planet_names = utils.PLANET_NAMES
        rasi_names_en = utils.RAASI_LIST
        chart_1d = self._horoscope_charts[0]
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        row_count_1 = self._argala_table1[0].rowCount()
        col_count = self._argala_table1[0].columnCount()
        argala,virodhargala = house.get_argala(chart_1d_ind)
        for row in range(row_count_1):
            for col in range(col_count):
                a_planets = argala[row][col].split('/')
                a_planets = '\n'.join(planet_names[int(p)] for p in a_planets if p.strip() !='' and p.strip() !=const._ascendant_symbol)
                self._argala_table1[0].setItem(row,col,QTableWidgetItem(a_planets))
                v_planets = virodhargala[row][col].split('/')
                v_planets = '\n'.join(planet_names[int(p)] for p in v_planets if p.strip() !='' and p.strip() !=const._ascendant_symbol)
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
        planet_names = utils.PLANET_NAMES
        rasi_names_en = utils.RAASI_LIST
        chart_1d = self._horoscope_charts[0]
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        r_arp,r_ahp,r_app = house.raasi_drishti_from_chart(chart_1d_ind,'\n')
        g_arp,g_ahp,g_app = house.graha_drishti_from_chart(chart_1d_ind,'\n')
        row_count_1 = self._drishti_table1[0].rowCount()
        row_count_2 = self._drishti_table2[0].rowCount()
        col_count = self._drishti_table1[0].columnCount()
        join_str = '\n'
        for row in range(row_count_2):
            col1 = join_str.join([rasi_names_en[arp] for arp in r_arp[row]])
            self._drishti_table2[0].setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp-1] for arp in r_ahp[row]])
            self._drishti_table2[0].setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in r_app[row] if pl != '' and pl!=const._ascendant_symbol])
            self._drishti_table2[0].setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            col1 = join_str.join([rasi_names_en[arp] for arp in g_arp[row]])
            self._drishti_table1[0].setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp-1] for arp in g_ahp[row]])
            self._drishti_table1[0].setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in g_app[row] if pl != '' and pl!=const._ascendant_symbol])
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
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        tab_names = [self.resources[tab] for tab in self.tabNames[1:_chart_tab_end]]#_vimsottari_dhasa_tab_start]]
        for t in range(_ashtaka_varga_tab_count):
            tab_name = self.resources['ashtaka_varga_str']+'-'+tab_names[t]
            self.tabWidget.setTabText(_ashtaka_varga_tab_start+t,tab_name)
            chart_1d = self._horoscope_charts[t] #charts[t]
            chart_1d = self._convert_language_chart_to_indices(chart_1d)
            bav,sav, _ = ashtakavarga.get_ashtaka_varga(chart_1d)#_en)
            ac = 0
            for _ in range(3):
                for _ in range(3):
                    if ac ==0:
                        chart_data_1d = sav
                        chart_title = 'SAV'
                    else:
                        chart_data_1d = bav[ac-1]
                        chart_title = self._horo._get_planet_list()[0][ac-1]
                    if 'north' in self._chart_type.lower() or 'sudar' in self._chart_type.lower():
                        _ascendant = drik.ascendant(jd,place)
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
    def _update_prediction_table(self):
        cur_row = self._prediction_list.currentRow()
        if cur_row == -1:
            cur_row = 0
            self._prediction_list.setCurrentRow(cur_row)
        cur_item = self._prediction_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected dosha information in the dosha edit box """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        prediction_results_text = ''
        list_count = _predictions_per_list_item
        list_len = self._prediction_count-1
        if cur_row < self._prediction_count:
            list_count = _predictions_per_list_item
            list_len = 0
        prediction_keys = list(self._prediction_results.keys())
        for k in range(list_count):
            if sy_len > k:
                yk = prediction_keys[(cur_row-list_len) * list_count + k] 
                #prediction_results_text += "<b><u>"+yk+"</u></b><br>"
                prediction_results_text += self._prediction_results[yk]+"<br>"
        prediction_results_text = prediction_results_text[:-len("<br>")]
        self._prediction_text.setHtml(prediction_results_text)
        self._prediction_text.setReadOnly(True) #setDisabled(True)
        
    def _update_prediction_tab_information(self):
        self.tabWidget.setTabText(_prediction_tab_start,self.resources['general_prediction_str'])
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._prediction_results = general.get_prediction_details(jd,place,language=available_languages[self._language])
        self._prediction_list.clear()
        self._prediction_count = len(self._prediction_results)
        for k in range(0,self._prediction_count,_predictions_per_list_item):
            key = ''
            for kk in range(_predictions_per_list_item):
                if k+kk<=self._prediction_count-kk:
                    key = key+'\n'+''.join(list(self._prediction_results.keys())[k+kk])
            key = key[1:]
            self._prediction_list.addItem(QListWidgetItem(key))
        self._prediction_list.setCurrentRow(0)
        return 
    def _update_dosha_table(self):
        cur_row = self._dosha_list.currentRow()
        if cur_row == -1:
            cur_row = 0
            self._dosha_list.setCurrentRow(cur_row)
        cur_item = self._dosha_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected dosha information in the dosha edit box """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        dosha_results_text = ''
        list_count = _doshas_per_list_item
        list_len = self._dosha_count-1
        if cur_row < self._dosha_count:
            list_count = _doshas_per_list_item
            list_len = 0
        dosha_keys = list(self._dosha_results.keys())
        for k in range(list_count):
            if sy_len > k:
                yk = dosha_keys[(cur_row-list_len) * list_count + k] 
                dosha_results_text += "<b><u>"+yk+"</u></b><br>"
                dosha_results_text += self._dosha_results[yk]+"<br>"
        dosha_results_text = dosha_results_text[:-len("<br>")]
        self._dosha_text.setHtml(dosha_results_text)
        self._dosha_text.setReadOnly(True) #setDisabled(True)
        
    def _update_dosha_tab_information(self):
        self.tabWidget.setTabText(_dosha_tab_start,self.resources['dosha_str'])
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._dosha_results = dosha.get_dosha_details(jd,place,language=available_languages[self._language])
        self._dosha_list.clear()
        self._dosha_count = len(self._dosha_results)
        for k in range(0,self._dosha_count,_doshas_per_list_item):
            key = ''
            for kk in range(_doshas_per_list_item):
                if k+kk<=self._dosha_count-kk:
                    key = key+'\n'+''.join(list(self._dosha_results.keys())[k+kk])
            key = key[1:]
            self._dosha_list.addItem(QListWidgetItem(key))
        self._dosha_list.setCurrentRow(0)
        return 
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
        list_count = _yogas_per_list_item
        list_len = self._raja_yoga_count-1
        if cur_row < self._raja_yoga_count:
            list_count = _raja_yogas_per_list_item
            list_len = 0
        yoga_keys = list(self._yoga_results.keys())
        for k in range(list_count):
            if sy_len > k:
                yk = yoga_keys[(cur_row-list_len) * list_count + k] 
                yoga_chart,yoga_name, yoga_description, yoga_predictions = self._yoga_results[yk]
                yoga_results_text += "<b><u>"+yoga_name+" ("+yoga_chart+")</u></b><br>"
                yoga_results_text += "<b>"+self.resources['description_str']+"</b> "+yoga_description+"<br>"
                yoga_results_text += "<b>"+self.resources['prediction_str']+"</b> " +yoga_predictions+"<br><br>"
        yoga_results_text = yoga_results_text[:-len("<br>")]
        self._yoga_text.setHtml(yoga_results_text)
        self._yoga_text.setReadOnly(True) #setDisabled(True)
        
    def _update_yoga_tab_information(self):
        self.tabWidget.setTabText(_yoga_tab_start,self.resources['yoga_str'])
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._raja_yoga_results,_,_ = raja_yoga.get_raja_yoga_details_for_all_charts(jd,place,language=available_languages[self._language])
        self._yoga_results,_,_ = yoga.get_yoga_details_for_all_charts(jd,place,language=available_languages[self._language])
        self._yoga_list.clear()
        self._raja_yoga_count = len(self._raja_yoga_results)
        if self._raja_yoga_results:
            yoga_count = len(self._raja_yoga_results)
            for k in range(0,yoga_count,_raja_yogas_per_list_item):
                key = ''
                for kk in range(_raja_yogas_per_list_item):
                    if k+kk<=yoga_count-kk:
                        key = key+'\n'+''.join(list(self._raja_yoga_results.values())[k+kk][1].split()[0:-1])
                key = key[1:]
                self._yoga_list.addItem(QListWidgetItem(key))
            #self._yoga_list.setCurrentRow(0)
        yoga_count = len(self._yoga_results)
        for k in range(0,yoga_count,_yogas_per_list_item):
            key = ''
            for kk in range(_yogas_per_list_item):
                if k+kk<=yoga_count-kk:
                    key = key+'\n'+''.join(list(self._yoga_results.values())[k+kk][1].split()[0:-1])
            key = key[1:]
            self._yoga_list.addItem(QListWidgetItem(key))
        self._yoga_results = {**self._raja_yoga_results, **self._yoga_results}
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
        if 'south' in self._chart_type.lower():
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_south)
            self._min_score_combo.setSingleStep(1.0)
            self._min_score_combo.setValue(const.compatibility_minimum_score_south)
        else:
            """ NOTE: setValue works only when used after setting range """ 
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_north)
            self._min_score_combo.setSingleStep(0.5)
            self._min_score_combo.setValue(const.compatibility_minimum_score_north)
        self._minimum_score = float(self._min_score_combo.text())
        nak = drik.nakshatra(self._birth_julian_day, self._horo.Place)
        _nakshatra_number = nak[0]; _paadha_number = nak[1]
        if self._gender_combo.currentIndex()==0: # self._gender.lower() == 'male':
            bn = _nakshatra_number # self._horo._nakshatra_number
            bp = _paadha_number# self._horo._paadha_number
        else:
            gn = _nakshatra_number # self._horo._nakshatra_number
            gp = _paadha_number # self._horo._paadha_number
        comp = compatibility.Match(boy_nakshatra_number=bn,boy_paadham_number=bp,girl_nakshatra_number=gn,girl_paadham_number=gp,\
                   check_for_mahendra_porutham=self._mahendra_porutham,check_for_vedha_porutham=self._vedha_porutham,\
                   check_for_rajju_porutham=self._rajju_porutham,check_for_shreedheerga_porutham=self._sthree_dheerga_porutham,\
                   minimum_score=self._minimum_score,method=self._chart_type)
        self._matching_stars_tuple = utils.sort_tuple(comp.get_matching_partners(),3,reverse=True)
        matching_stars_count = len(self._matching_stars_tuple)
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
                        paadham = str(m_s_tup[1])
                        key += '\n'+nakshatra+'-'+paadham
                key = key[1:]
                matching_stars.append(key)
            self._matching_star_list.addItems(matching_stars)
            self._matching_star_list.setCurrentRow(0)
    def _update_compatibility_table(self):
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
        ettu_poruthham_list = [self.resources[p] for p in compatibility.compatibility_list_north]
        if 'south' in self._chart_type.lower():
            ettu_poruthham_list = [self.resources[p] for p in compatibility.compatibility_list_south]            
        ettu_porutham_max_score = [compatibility.varna_max_score,compatibility.vasiya_max_score,compatibility.gana_max_score,\
                                    compatibility.nakshathra_max_score,compatibility.yoni_max_score,compatibility.raasi_adhipathi_max_score, \
                                    compatibility.raasi_max_score, compatibility.naadi_max_score]
        naalu_porutham_list = [self.resources[p] for p in compatibility.naalu_porutham_list]
        ettu_porutham_results = selected_matching_star_tuple[2]
        compatibility_score = selected_matching_star_tuple[3]
        naalu_porutham_results = selected_matching_star_tuple[4]
        minimum_tamil_porutham = naalu_porutham_results[-1]
        if 'south' in self._chart_type.lower():
            ettu_porutham_results = ettu_porutham_results[1:-1]
            #minimum_tamil_porutham = all([ettu_porutham_results[t] for t in const.mandatory_compatibility_south_list]) and naalu_porutham_results[2]          
        nakshatra = utils.NAKSHATRA_LIST[selected_matching_star_tuple[0]-1]
        paadham = self.resources['paadham_str']+' '+str(selected_matching_star_tuple[1])
        results_table.setHorizontalHeaderItem(0,QTableWidgetItem(nakshatra+'-'+paadham))
        results_table.setHorizontalHeaderItem(1,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(2,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(3,QTableWidgetItem(''))
        row = 0
        for p,porutham in enumerate(ettu_poruthham_list):
            if 'south' in self._chart_type.lower():
                results_table.setItem(row,0,QTableWidgetItem(porutham))
                results_table.setItem(row,1,QTableWidgetItem(str(ettu_porutham_results[p])))
                results_table.setItem(row,2,QTableWidgetItem('True'))
                if ettu_porutham_results[p]:
                    results_table.setItem(row,3,QTableWidgetItem(str(const._GREEN_CHECK)))
                else:
                    results_table.setItem(row,3,QTableWidgetItem(str(const._RED_CROSS)))                
            else:
                results_table.setItem(row,0,QTableWidgetItem(porutham))
                results_table.setItem(row,1,QTableWidgetItem(str(ettu_porutham_results[p])))
                results_table.setItem(row,2,QTableWidgetItem(str(ettu_porutham_max_score[p])))
                perc = '{:3.0f}%'.format(ettu_porutham_results[p]/ettu_porutham_max_score[p]*100)
                results_table.setItem(row,3,QTableWidgetItem(str(perc)))
            row += 1
        for p,porutham in enumerate(naalu_porutham_list):
            results_table.setItem(row,0,QTableWidgetItem(porutham))
            results_table.setItem(row,1,QTableWidgetItem(str(naalu_porutham_results[p])))
            results_table.setItem(row,2,QTableWidgetItem('True'))
            if naalu_porutham_results[p]:
                results_table.setItem(row,3,QTableWidgetItem(str(const._GREEN_CHECK)))
            else:
                results_table.setItem(row,3,QTableWidgetItem(str(const._RED_CROSS)))
            row += 1
        results_table.setItem(row,0,QTableWidgetItem(self.resources['overall_match_str']))
        results_table.setItem(row,1,QTableWidgetItem(str(compatibility_score)))
        if 'south' in self._chart_type.lower():
            results_table.setItem(row,2,QTableWidgetItem(str(compatibility.max_compatibility_score_south)))
            if minimum_tamil_porutham:
                results_table.setItem(row,3,QTableWidgetItem(str(const._GREEN_CHECK)))
            else:
                results_table.setItem(row,3,QTableWidgetItem(str(const._RED_CROSS)))
        else:
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
            self._update_sphuta_tab_information()
            self._update_drishti_table_information()
            self._update_graha_arudha_tab_information()
            self._update_amsa_bala_tab_information()
            self._update_other_bala_tab_information()
            self._update_shad_bala_table_information()
            self._update_bhava_bala_table_information()
            self._update_dhasa_bhukthi_tab_information()
            self._update_ashtaka_varga_tab_information()
            self._update_argala_table_information()
            self._update_shodhaya_table_information()
            self._update_yoga_tab_information()
            self._update_dosha_tab_information()
            self._show_compatibility = self._gender_combo.currentIndex() in [0,1]
            if  self._show_compatibility:
                self._update_compatibility_tab_information()
            self._update_prediction_tab_information()
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
            print(self._place_name,self._latitude,self._longitude,self._time_zone)
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
        def __save_scrollable_list_widget_as_image(widget:QWidget,image_id, image_files,_row_steps=1):
            scroll_tab_count = 0
            for row in range(0,widget.count(),_row_steps):
                self._hide_show_even_odd_pages(image_id)
                widget.setCurrentRow(row)
                image_file = _images_path+image_prefix+str(image_id)+image_ext
                im = self.grab()
                im.save(image_file) 
                image_files.append(image_file)
                image_id +=1
                scroll_tab_count += 1
            return image_id
        if not self._western_chart:
            self._matching_star_list.setVisible(False)
            self._matching_star_list.setMaximumWidth(0)
            self._yoga_list.setVisible(False)
            self._yoga_list.setMaximumWidth(0)
            self._dosha_list.setVisible(False)
            self._dosha_list.setMaximumWidth(0)
            for c in range(_comp_results_per_list_item):
                self._comp_results_table[c].update()
            self._prediction_list.setVisible(False)
            self._prediction_list.setMaximumWidth(0)
            self._yoga_text.update()
            self._dosha_text.update()
            self._prediction_text.update()
        if pdf_file_name:
            self._hide_show_layout_widgets(self._row3_h_layout, False)
            for t in range(self.tabCount):
                self._hide_show_even_odd_pages(image_id)
                self.tabWidget.setCurrentIndex(t)
                self._show_only_tab(t)
                #"""
                if t==_yoga_tab_start: image_id = __save_scrollable_list_widget_as_image(self._yoga_list,image_id, image_files)
                elif t==_dosha_tab_start:image_id = __save_scrollable_list_widget_as_image(self._dosha_list,image_id, image_files)
                elif t==_compatibility_tab_start:image_id = __save_scrollable_list_widget_as_image(self._matching_star_list,image_id, image_files,_comp_results_per_list_item)
                elif t==_prediction_tab_start:image_id = __save_scrollable_list_widget_as_image(self._prediction_list,image_id, image_files)
                else:
                    image_file = _images_path+image_prefix+str(image_id)+image_ext
                    image_files.append(image_file)
                    im = self.grab()
                    im.save(image_file) 
                    image_id +=1
                #"""
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
        self._hide_show_layout_widgets(self._row3_h_layout, True)
        self._hide_show_layout_widgets(self._comp_h_layout, True)
        self._footer_label.show()
        if not self._western_chart:
            self._matching_star_list.setVisible(True)
            self._matching_star_list.setMaximumWidth(_compatability_list_width)
            self._yoga_list.setVisible(True)
            self._yoga_list.setMaximumWidth(_yoga_list_box_width)
            self._dosha_list.setVisible(True)
            self._dosha_list.setMaximumWidth(_dosha_list_box_width)
            self._prediction_list.setVisible(True)
            self._prediction_list.setMaximumWidth(_prediction_list_box_width)
            for c in range(_comp_results_per_list_item):
                self._comp_results_table[c].update()
            self._yoga_text.update()
            self._dosha_text.update()
            self._prediction_text.update()
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
        utils.PLANET_NAMES = self.resources['PLANET_NAMES'].split(',')
        utils.RAASI_LIST = self.resources['RAASI_LIST'].split(',')
        #planet_list_lang = self._horo._get_planet_list()[0]+[self.resources['ascendant_str']]
        planet_list_lang = utils.PLANET_NAMES+[self.resources['ascendant_str']]
        planet_list_en = ['Sun☉','Moon☾','Mars♂','Mercury☿','Jupiter♃','Venus♀','Saturn♄','Raagu☊','Kethu☋','Uranus','Neptune','Pluto','Lagnam']
        planet_lang_dict = {planet_list_lang[i]:planet_list_en[i] for i in range(len(planet_list_en))}
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v)
        return rasi_1d_en
    def _convert_language_chart_to_indices(self,rasi_1d_lang):
        rasi_1d_en = self._convert_language_chart_to_english(rasi_1d_lang)
        planet_list_en = ['Sun☉','Moon☾','Mars♂','Mercury☿','Jupiter♃','Venus♀','Saturn♄','Raagu☊','Kethu☋','Uranus','Neptune','Pluto']+['Lagnam']
        planet_lang_dict = {planet_list_en[i]:str(i) for i in range(len(planet_list_en))}
        last_key = list(planet_lang_dict)[-1]
        planet_lang_dict[last_key] = const._ascendant_symbol
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v).replace(const._retrogade_symbol,'')
        return rasi_1d_en
def show_horoscope(data):
    """
        Same as class method show() to display the horoscope
        @param data - last chance to pass the data to the class
    """
    app=QApplication(sys.argv)
    window=ChartTabbed(data)
    window.show()
    app.exec_()
def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1
def _convert_1d_house_data_to_2d(rasi_1d,chart_type='south_indian'):
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
def _get_date_difference(then, now = datetime.now(), interval = "default"):
    from dateutil import relativedelta
    diff = relativedelta.relativedelta(now,then)
    years = abs(diff.years)
    months = abs(diff.months)
    days = abs(diff.days)
    return [years,months,days]
def _dhasa_balance(date_of_birth,dhasa_end_date):
    return utils.panchanga_date_diff(date_of_birth,dhasa_end_date)
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
    chart_type = 'south_indian'
    chart = ChartTabbed(chart_type=chart_type,show_marriage_compatibility=True)
    chart.language('Tamil')
    chart.name('XXX')#'('Rama')
    chart.gender(1) #(0)
    """
    loc = utils.get_place_from_user_ip_address()
    print('loc from IP address',loc)
    if loc:
        chart.place(loc[0])
    """
    chart.place('Chennai, India') #('Ayodhya, India')
    chart.latitude(13.0878)#('26.79909')
    chart.longitude(80.2785)#('82.2047')
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    chart.date_of_birth(current_date_str)
    chart.date_of_birth('1996,12,7')#('-5114,1,9')
    #chart.time_of_birth(current_time_str)
    chart.time_of_birth('10:34:00')#('12:10:00')
    chart.chart_type(chart_type)
    chart.compute_horoscope(calculation_type='drik')
    chart.show()
    #chart.save_as_pdf('./output.pdf')
    sys.exit(App.exec())
