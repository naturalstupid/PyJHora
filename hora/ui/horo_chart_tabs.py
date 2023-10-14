import math
import re, sys, os
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from _datetime import datetime,time,date
import img2pdf
from PIL import Image
import numpy as np
from hora import const
from hora import utils
from hora.panchanga import drik, surya_sidhantha
from hora.horoscope import main
from hora.horoscope.match import compatibility
from hora.horoscope.chart import ashtakavarga
from hora.horoscope.chart import yoga
from hora.horoscope.chart import house
from hora.ui.chart_styles import EastIndianChart, WesternChart, SouthIndianChart, NorthIndianChart, SudarsanaChakraChart
from hora.horoscope.dhasa import sudharsana_chakra

sort_tuple = lambda tup,tup_index,reverse=False: sorted(tup,key = lambda x: x[tup_index],reverse=reverse)

_images_path = const._IMAGES_PATH
_IMAGE_ICON_PATH=const._IMAGE_ICON_PATH
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
_world_city_csv_file = const._world_city_csv_file
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
""" UI Constants """
_main_window_width = 750 #725
_main_window_height = 580 #630
_comp_table_font_size = 8
_comp_results_per_list_item = 2
_yoga_text_font_size = 8.5
_yogas_per_list_item = 3
_compatability_list_width = 145
_yoga_list_box_width = 125
_shodhaya_table_font_size = 5.6
_drishti_table_font_size = 6.3
_info_label_font_size = 7.2 # 6.3  if uranus/neptune/pluto included
_main_ui_label_button_font_size = 8
#_main_ui_comp_label_font_size = 7
_info_label1_height = 200
_info_label2_height = _info_label1_height
_row3_widget_width = 75
_chart_info_label_width = 250
_chart_size_factor = 0.31
_footer_label_font_height = 8
_footer_label_height = 30
#_dhasa_bhukthi_combo_list = ['vimsottari_str','ashtothari_str','narayana_str','kendraadhi_rasi_str','sudasa_str','drig_str','nirayana_str','shoola_str','kalachakra_str']
_chart_names = ['raasi_str','hora_str','drekkanam_str','chaturthamsa_str','panchamsa_str',
              'shashthamsa_str','saptamsam_str','ashtamsa_str','navamsam_str','dhasamsam_str','rudramsa_str',
              'dhwadamsam_str','shodamsa_str','vimsamsa_str','chaturvimsamsa_str','nakshatramsa_str','thrisamsam_str',
              'khavedamsa_str','akshavedamsa_str','sashtiamsam_str',
              'nava_navamsa_str','ashtotharamsa_str','dwadas_dwadasamsa_str']
_tab_names = ['panchangam_str'] + _chart_names + ['vimsottari_dhasa_bhukthi_str','ashtottari_dhasa_bhukthi_str',
                                                  'narayana_dhasa_str','Kendraadhi_rasi_dhasa_str','sudasa_str','drig_str',
                                                  'nirayana_str', 'shoola_str','patyayini_str','varsha_vimsottari_str','varsha_narayana_str',
                                                  'ashtaka_varga_str','drishti_str','argala_str','shodhaya_pinda_str','yoga_str','compatibility_str']
_vimsottari_dhasa_tab_start = len(_chart_names)+1 #21 #24
_vimsottari_dhasa_tab_count = 3
_vimsottari_dhasa_tab_end = _vimsottari_dhasa_tab_start + _vimsottari_dhasa_tab_count - 1
_vimsottari_table_font_size = 10

_ashtottari_dhasa_tab_start = _vimsottari_dhasa_tab_end+1 #21 #24
_ashtottari_dhasa_tab_count = 3
_ashtottari_dhasa_tab_end = _ashtottari_dhasa_tab_start + _ashtottari_dhasa_tab_count - 1
_ashtottari_table_font_size = 10

_narayana_dhasa_tab_start = _ashtottari_dhasa_tab_end + 1
_narayana_dhasa_tab_count = 3
_narayana_dhasa_tab_end = _narayana_dhasa_tab_start + _narayana_dhasa_tab_count - 1
_narayana_table_font_size = 7

_kendraadhi_dhasa_tab_start = _narayana_dhasa_tab_end + 1
_kendraadhi_dhasa_tab_count = 3
_kendraadhi_dhasa_tab_end = _kendraadhi_dhasa_tab_start + _kendraadhi_dhasa_tab_count - 1
_kendraadhi_table_font_size = 7

_sudasa_dhasa_tab_start = _kendraadhi_dhasa_tab_end + 1
_sudasa_dhasa_tab_count = 3
_sudasa_dhasa_tab_end = _sudasa_dhasa_tab_start + _sudasa_dhasa_tab_count - 1
_sudasa_table_font_size = 7

_drig_dhasa_tab_start = _sudasa_dhasa_tab_end + 1
_drig_dhasa_tab_count = 3
_drig_dhasa_tab_end = _drig_dhasa_tab_start + _drig_dhasa_tab_count - 1
_drig_table_font_size = 7

_nirayana_dhasa_tab_start = _drig_dhasa_tab_end + 1
_nirayana_dhasa_tab_count = 3
_nirayana_dhasa_tab_end = _nirayana_dhasa_tab_start + _nirayana_dhasa_tab_count - 1
_nirayana_table_font_size = 7

_shoola_dhasa_tab_start = _nirayana_dhasa_tab_end + 1
_shoola_dhasa_tab_count = 3
_shoola_dhasa_tab_end = _shoola_dhasa_tab_start + _shoola_dhasa_tab_count - 1
_shoola_table_font_size = 7

_patyayini_dhasa_tab_start = _shoola_dhasa_tab_end + 1
_patyayini_dhasa_tab_count = 2
_patyayini_dhasa_tab_end = _patyayini_dhasa_tab_start + _patyayini_dhasa_tab_count - 1
_patyayini_table_font_size = 7

_mudda_dhasa_tab_start = _patyayini_dhasa_tab_end + 1
_mudda_dhasa_tab_count = 3
_mudda_dhasa_tab_end = _mudda_dhasa_tab_start + _mudda_dhasa_tab_count - 1
_mudda_table_font_size = 7

_varsha_narayana_dhasa_tab_start = _mudda_dhasa_tab_end + 1
_varsha_narayana_dhasa_tab_count = 3
_varsha_narayana_dhasa_tab_end = _varsha_narayana_dhasa_tab_start + _varsha_narayana_dhasa_tab_count - 1
_varsha_narayana_table_font_size = 7

_ashtaka_varga_tab_start = _varsha_narayana_dhasa_tab_end + 1
""" 8 BAV/PAV-Raasi for each planet and Asc. One SAV-D1/SAV-D9. 8 BAV/PAV-D9 for each planet"""
_ashtaka_varga_tab_count = len(_tab_names[1:_vimsottari_dhasa_tab_start]) #+1 # +1 for shodhaya tables
_ashtaka_varga_tab_end = _ashtaka_varga_tab_start + _ashtaka_varga_tab_count - 1
#print('_ashtaka_varga_tab',_ashtaka_varga_tab_start,_ashtaka_varga_tab_count,_ashtaka_varga_tab_end)
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
#print('_tab_names',_tab_names,len(_tab_names))
available_chart_types = {'south indian':SouthIndianChart,'north indian':NorthIndianChart,'east indian':EastIndianChart,
                         'western':WesternChart,'sudarsana chakra':SudarsanaChakraChart}
available_languages = const.available_languages
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignHCenter
class ChartTabbed(QWidget):
    def __init__(self,chart_type='south indian',show_marriage_compatibility=True, calculation_type:str='drik'):
        super().__init__()
        self._chart_type = chart_type
        self._calculation_type = calculation_type
        self._show_compatibility = show_marriage_compatibility
        ' read world cities'
        self._df = utils._world_city_db_df
        self._world_cities_db = utils.world_cities_db
        self._init_main_window()
        self._v_layout = QVBoxLayout()
        self._create_row1_ui()
        self._create_row_2_and_3_ui()
        if self._show_compatibility:
            self._create_comp_ui()
        self._init_tab_widget_ui()
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
        elif _current_tab_index >= _vimsottari_dhasa_tab_start and _current_tab_index <= _shoola_dhasa_tab_end:
            self._hide_2nd_row_widgets(False)
        else:
            self._hide_2nd_row_widgets(True)
            self._show_hide_marriage_checkboxes(False)
    def _init_tab_widget_ui(self):
        self._western_chart = False
        if 'west' in self._chart_type.lower():
            self._western_chart = True
            self.tabNames = _tab_names[:_vimsottari_dhasa_tab_start]
        elif self._show_compatibility:
            self.tabNames = _tab_names
        else:
            self.tabNames = _tab_names[:-1]
        #print('Tab Names',self.tabNames)
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
        t = 0
        for tabName in self.tabNames:
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[t],tabName)
            if t==0:
                self._init_panchanga_tab_widgets(t)
                t+=1
            elif t==_vimsottari_dhasa_tab_start:
                self._init_vimsottari_dhasa_bhukthi_tab_widgets(t)
                t += _vimsottari_dhasa_tab_count
            elif t==_ashtottari_dhasa_tab_start:
                self._init_ashtottari_dhasa_bhukthi_tab_widgets(t)
                t += _ashtottari_dhasa_tab_count
            elif t==_narayana_dhasa_tab_start:
                self._init_narayana_dhasa_tab_widgets(t)
                t += _narayana_dhasa_tab_count
            elif t==_kendraadhi_dhasa_tab_start:
                self._init_kendraadhi_dhasa_tab_widgets(t)
                t += _kendraadhi_dhasa_tab_count
            elif t==_sudasa_dhasa_tab_start:
                self._init_sudasa_dhasa_tab_widgets(t)
                t += _sudasa_dhasa_tab_count
            elif t==_drig_dhasa_tab_start:
                self._init_drig_dhasa_tab_widgets(t)
                t += _drig_dhasa_tab_count
            elif t==_nirayana_dhasa_tab_start:
                self._init_nirayana_dhasa_tab_widgets(t)
                t += _nirayana_dhasa_tab_count
            elif t==_shoola_dhasa_tab_start:
                self._init_shoola_dhasa_tab_widgets(t)
                t += _shoola_dhasa_tab_count
            elif t==_patyayini_dhasa_tab_start:
                self._init_patyayini_dhasa_bhukthi_tab_widgets(t)
                t += _patyayini_dhasa_tab_count
            elif t==_mudda_dhasa_tab_start:
                self._init_mudda_dhasa_bhukthi_tab_widgets(t)
                t += _mudda_dhasa_tab_count
            elif t==_varsha_narayana_dhasa_tab_start:
                self._init_varsha_narayana_dhasa_bhukthi_tab_widgets(t)
                t += _varsha_narayana_dhasa_tab_count
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
            #print('Added uptp tab#',t-1,tabName)
        self.tabCount = self.tabWidget.count()
        self._add_footer_to_chart()
        self.setLayout(self._v_layout)        
        #self._dhasa_bhukthi_combo.setVisible(False)
        self._show_hide_marriage_checkboxes(False)
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
    def _init_vimsottari_dhasa_bhukthi_tab_widgets(self,tab_index):
        self._vimsottari_tables_per_tab = 3
        self._vimsottari_rows_per_table = 10 # One row for Header
        self._vimsottari_cols_per_table = 2
        self.vimsottari_db_tables = self._init_dhasa_tab_widgets(tab_index, self._vimsottari_tables_per_tab, self._vimsottari_rows_per_table, 
                                            self._vimsottari_cols_per_table, _vimsottari_dhasa_tab_start, _vimsottari_dhasa_tab_count, 
                                            'vimsottari_str', _vimsottari_table_font_size)
        return
    def _init_ashtottari_dhasa_bhukthi_tab_widgets(self,tab_index):
        self._ashtottari_tables_per_tab = 3
        self._ashtottari_rows_per_table = 9 # One row for Header
        self._ashtottari_cols_per_table = 2
        self.ashtottari_db_tables = self._init_dhasa_tab_widgets(tab_index, self._ashtottari_tables_per_tab, self._ashtottari_rows_per_table, 
                                            self._ashtottari_cols_per_table, _ashtottari_dhasa_tab_start, _ashtottari_dhasa_tab_count, 
                                            'ashtottari_str', _ashtottari_table_font_size)
        return
    def _init_narayana_dhasa_tab_widgets(self,tab_index):
        self._narayana_tables_per_tab = 4
        self._narayana_rows_per_table = 13 # One row for Header
        self._narayana_cols_per_table = 2
        self.narayana_db_tables = self._init_dhasa_tab_widgets(tab_index, self._narayana_tables_per_tab, self._narayana_rows_per_table, 
                                            self._narayana_cols_per_table, _narayana_dhasa_tab_start, _narayana_dhasa_tab_count, 
                                            'narayana_str', _narayana_table_font_size)
        return
    def _init_kendraadhi_dhasa_tab_widgets(self,tab_index):
        self._kendraadhi_tables_per_tab = 4
        self._kendraadhi_rows_per_table = 13 # One row for Header
        self._kendraadhi_cols_per_table = 2
        self.kendraadhi_db_tables = self._init_dhasa_tab_widgets(tab_index, self._kendraadhi_tables_per_tab, self._kendraadhi_rows_per_table, 
                                            self._kendraadhi_cols_per_table, _kendraadhi_dhasa_tab_start, _kendraadhi_dhasa_tab_count, 
                                            'kendraadhi_rasi_str', _kendraadhi_table_font_size)
        return
    def _init_sudasa_dhasa_tab_widgets(self,tab_index):
        self._sudasa_tables_per_tab = 4
        self._sudasa_rows_per_table = 13 # One row for Header
        self._sudasa_cols_per_table = 2
        self.sudasa_db_tables = self._init_dhasa_tab_widgets(tab_index, self._sudasa_tables_per_tab, self._sudasa_rows_per_table, 
                                            self._sudasa_cols_per_table, _sudasa_dhasa_tab_start, _sudasa_dhasa_tab_count, 
                                            'sudasa_str', _sudasa_table_font_size)
        return
    def _init_drig_dhasa_tab_widgets(self,tab_index):
        self._drig_tables_per_tab = 4
        self._drig_rows_per_table = 13 # One row for Header
        self._drig_cols_per_table = 2
        self.drig_db_tables = self._init_dhasa_tab_widgets(tab_index, self._drig_tables_per_tab, self._drig_rows_per_table, 
                                            self._drig_cols_per_table, _drig_dhasa_tab_start, _drig_dhasa_tab_count, 
                                            'drig_str', _drig_table_font_size)
        return
    def _init_nirayana_dhasa_tab_widgets(self,tab_index):
        self._nirayana_tables_per_tab = 4
        self._nirayana_rows_per_table = 13 # One row for Header
        self._nirayana_cols_per_table = 2
        self.nirayana_db_tables = self._init_dhasa_tab_widgets(tab_index, self._nirayana_tables_per_tab, self._nirayana_rows_per_table, 
                                            self._nirayana_cols_per_table, _nirayana_dhasa_tab_start, _nirayana_dhasa_tab_count, 
                                            'nirayana_str', _nirayana_table_font_size)
        return
    def _init_shoola_dhasa_tab_widgets(self,tab_index):
        self._shoola_tables_per_tab = 4
        self._shoola_rows_per_table = 13 # One row for Header
        self._shoola_cols_per_table = 2
        self.shoola_db_tables = self._init_dhasa_tab_widgets(tab_index, self._shoola_tables_per_tab, self._shoola_rows_per_table, 
                                            self._shoola_cols_per_table, _shoola_dhasa_tab_start, _shoola_dhasa_tab_count, 
                                            'shoola_str', _shoola_table_font_size)
        return
    def _init_patyayini_dhasa_bhukthi_tab_widgets(self,tab_index):
        self._patyayini_tables_per_tab = 4
        self._patyayini_rows_per_table = 9 # One row for Header
        self._patyayini_cols_per_table = 2
        self.patyayini_db_tables = self._init_dhasa_tab_widgets(tab_index, self._patyayini_tables_per_tab, self._patyayini_rows_per_table, 
                                            self._patyayini_cols_per_table, _patyayini_dhasa_tab_start, _patyayini_dhasa_tab_count, 
                                            'patyayini_str', _patyayini_table_font_size)
        return
    def _init_mudda_dhasa_bhukthi_tab_widgets(self,tab_index):
        self._mudda_tables_per_tab = 3
        self._mudda_rows_per_table = 10 # One row for Header
        self._mudda_cols_per_table = 2
        self.mudda_db_tables = self._init_dhasa_tab_widgets(tab_index, self._mudda_tables_per_tab, self._mudda_rows_per_table, 
                                            self._mudda_cols_per_table, _mudda_dhasa_tab_start, _mudda_dhasa_tab_count, 
                                            'varsha_vimsottari_str', _mudda_table_font_size)
        return
    def _init_varsha_narayana_dhasa_bhukthi_tab_widgets(self,tab_index):
        self._varsha_narayana_tables_per_tab = 4
        self._varsha_narayana_rows_per_table = 13 # One row for Header
        self._varsha_narayana_cols_per_table = 2
        self.varsha_narayana_db_tables = self._init_dhasa_tab_widgets(tab_index, self._varsha_narayana_tables_per_tab, self._varsha_narayana_rows_per_table, 
                                            self._varsha_narayana_cols_per_table, _varsha_narayana_dhasa_tab_start, _varsha_narayana_dhasa_tab_count, 
                                            'varsha_narayana_str', _varsha_narayana_table_font_size)
        return
    def _init_dhasa_tab_widgets(self,tab_index,tables_per_tab,rows_per_table,cols_per_table,
                                tab_start,tab_count,tab_str,table_font_size):
        """ Add more tabs for narayna dhasa  """
        for t in range(1,tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self.tabCount += tab_count-1
        _db_tables = [[ QTableWidget(rows_per_table,cols_per_table) for _ in range(tables_per_tab)] for _ in range(tab_count)]
        #print('self.drig_db_tables',self.drig_db_tables) 
        for db_tab in range(tab_count):
            grid_layout = QGridLayout()
            for col in range(tables_per_tab):
                _db_tables[db_tab][col].setStyleSheet('font-size:'+str(table_font_size)+'pt')
                _db_tables[db_tab][col].horizontalHeader().hide()
                _db_tables[db_tab][col].verticalHeader().hide()
                _db_tables[db_tab][col].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                _db_tables[db_tab][col].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                grid_layout.addWidget(_db_tables[db_tab][col],1,col)
            self.horo_tabs[tab_start+db_tab].setLayout(grid_layout)
            _tabname = tab_str+str(db_tab+1)
            self.tabWidget.setTabText(tab_start+db_tab,_tabname)
        return _db_tables
    def _init_panchanga_tab_widgets(self,tab_index):
        h_layout = QHBoxLayout()
        h_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self._info_label1 = QLabel("Information:")
        self._info_label1.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label1.setStyleSheet("border: 1px solid black;")
        h_layout.addWidget(self._info_label1)
        self._info_label2 = QLabel("Information:")
        self._info_label2.setStyleSheet("border: 1px solid black;")
        h_layout.addWidget(self._info_label2)
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_chart_tab_widgets(self,tab_index):
        h_layout = QHBoxLayout()
        self._charts.append(available_chart_types[self._chart_type]())
        h_layout.addWidget(self._charts[tab_index-1])
        self._chart_info_labels.append(QLabel('Chart Information'))
        h_layout.addWidget(self._chart_info_labels[tab_index-1])
        self._chart_info_labels[tab_index-1].setStyleSheet('font-size:'+str(_info_label_font_size)+'pt')
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0,0,0,0)
        self._charts[tab_index-1].update()
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_drishti_tab_widgets(self,tab_index):
        # create extra tabs depending on the count
        for t in range(1,_drishti_tab_count):
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
    def _init_argala_tab_widgets(self,tab_index):
        # create extra tabs depending on the count
        for t in range(1,_argala_tab_count):
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
        for t in range(1,_ashtaka_varga_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        #print('_init_ashtaka_tab_widgets',tab_index)
        """ create 9x9 chart grid. 1st one SAV and others are 8 planet BAV """
        for t in range(_ashtaka_varga_tab_count):
            self._ashtaka_grid_layout = QGridLayout()
            """ Sudarsana Chakra Chart does not Asktaka Varga Chart - So Force North Indian """
            __chart_type = available_chart_types[self._chart_type]
            if 'sudar' in self._chart_type.lower():
                __chart_type = available_chart_types['north indian']
                #print('For SC - using SI Ashtaka Chart...',__chart_type)
            self._ashtaka_charts.append([(__chart_type(chart_size_factor=_chart_size_factor)) for i in range(9)])
            #self._ashtaka_charts.append([(available_chart_types[self._chart_type](chart_size_factor=_chart_size_factor)) for i in range(9)])
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
        self._language = list(available_languages.keys())[0]
        ci = _index_containing_substring(available_chart_types.keys(),self._chart_type.lower())
        if ci >=0:
            self._chart_type = list(available_chart_types.keys())[ci]
        self.setFixedSize(_main_window_width,_main_window_height)        
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
        self._row1_h_layout.addWidget(self._gender_combo)
        self._place_label = QLabel("Place:")
        self._row1_h_layout.addWidget(self._place_label)
        self._place_name = ''
        self._place_text = QLineEdit(self._place_name)
        self._world_cities_list = utils.world_cities_list
        completer = QCompleter(self._world_cities_list)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
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
    def _create_row_3_ui(self):
        self._row3_h_layout = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.currentIndexChanged.connect(self._update_main_window_label_and_tooltips)
        self._row3_h_layout.addWidget(self._lang_combo)
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
        self._comp_h_layout = QHBoxLayout()
        #self._dhasa_bhukthi_combo = QComboBox()
        #self._dhasa_bhukthi_combo.addItems([db.replace('_str','') for db in _dhasa_bhukthi_combo_list])
        #self._comp_h_layout.addWidget(self._dhasa_bhukthi_combo)
        self._show_hide_marriage_checkboxes(True)
        self._v_layout.addLayout(self._comp_h_layout)
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
                #"""
                self._years_label.setText(msgs['years_str'])
                self._months_label.setText(msgs['months_str'])
                self._60hrs_label.setText(msgs['60hrs_str'])
                #"""
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
                self._footer_label.setText(msgs['window_footer_title'])
                self.setWindowTitle(msgs['window_title'])
                self.update()
        except:
            pass
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
        self._language = self._lang_combo.currentText()
        self._date_of_birth = self._dob_text.text()
        self._time_of_birth = self._tob_text.text()
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
        year,month,day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        self._chart_type = self._chart_type_combo.currentText()
        ' set the chart type and reset widgets'
        self._recreate_chart_tab_widgets()
        if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
            self._horo= main.Horoscope(latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,
                                       date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,
                                       ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       years=self._years,months=self._months,sixty_hours=self._60hrs)
        else:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,
                                       ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       years=self._years,months=self._months,sixty_hours=self._60hrs)
        self._calendar_info = self._horo.get_calendar_information(language=available_languages[self._language])
        self.resources= self._horo._get_calendar_resource_strings(language=available_languages[self._language])
        #self._horoscope_info, self._horoscope_charts, self._vimsottari_dhasa_bhukti_info, self._ashtottari_dhasa_bhukti_info = [],[],[],[]
        self._horoscope_info, self._horoscope_charts = self._horo.get_horoscope_information(language=available_languages[self._language])
        dob = self._horo.Date
        tob = self._horo.birth_time
        place = self._horo.Place
        self._vimsottari_dhasa_bhukti_info,self._ashtottari_dhasa_bhukti_info = self._horo._get_graha_dhasa_bhukthi(dob, tob, place)
        self._narayana_dhasa_info, self._kendraadhi_dhasa_info, self._sudasa_dhasa_info, \
            self._drig_dhasa_info, self._nirayana_dhasa_info,self._shoola_dhasa_info \
                = self._horo._get_rasi_dhasa_bhukthi(dob, tob, place)
        self._patyayini_dhasa_info,self._mudda_dhasa_info,self._varsha_narayana_dhasa_info = self._horo._get_annual_dhasa_bhukthi()
        #print('self._patyayini_dhasa_info',self._patyayini_dhasa_info)
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
        _years = int(self._years_combo.text())
        _months = int(self._months_combo.text())
        _60hrs = int(self._60hrs_combo.text())
        jd_years = drik.next_solar_date(jd, place, _years, _months, _60hrs)
        yb, mb, db, hfb = utils.jd_to_gregorian(jd)
        yy, my, dy, hfy = utils.jd_to_gregorian(jd_years)
        #print('jd,_years,_months,_60hrs,jd_years,y,m,d,hf',jd,_years,_months,_60hrs,jd_years,y,m,d,hf)
        self._date_text_dob =  '%04d-%02d-%02d' %(yb,mb,db)
        self._time_text_dob = utils.to_dms(hfb,as_string=True)
        self._date_text_years =  '%04d-%02d-%02d' %(yy,my,dy)
        self._time_text_years = utils.to_dms(hfy,as_string=True)
        self._timezone_text = '(GMT '+str(self._tz_text.text())+')'
        key = 'date_of_birth_str'
        info_str += format_str % (self.resources[key],self._date_text_dob)
        key = 'time_of_birth_str'
        info_str += format_str % (self.resources[key],self._time_text_dob)
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
        key = self.resources['bhava_lagna_str']
        value = drik.bhava_lagna(jd,place,tob,1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['hora_lagna_str']
        value = drik.hora_lagna(jd,place,tob,1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['ghati_lagna_str']
        value = drik.ghati_lagna(jd,place,tob,1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['sree_lagna_str']
        value = drik.sree_lagna(jd,place,1)
        info_str += format_str %(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        #key = self.resources['raasi_str']+'-'+self.resources['ascendant_str']
        #value = self._horoscope_info[key]
        value = drik.ascendant(jd, place)
        info_str += format_str % (self.resources['ascendant_str'],utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong'))
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
        dhasa = list(self._vimsottari_dhasa_bhukti_info.keys())[8].split('-')[0]
        deb = list(self._vimsottari_dhasa_bhukti_info.values())[8]
        dob = self._dob_text.text().replace(',','-')
        years,months,days = _dhasa_balance(dob, deb)
        value = str(years)+':'+ str(months)+':'+ str(days)
        key = dhasa + ' '+self.resources['balance_str']
        info_str += format_str % (key,value)
        dhasa = ''
        dhasa_end_date = ''
        di = 9
        for p,(k,v) in enumerate(self._vimsottari_dhasa_bhukti_info.items()):
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
                dhasa_end_date = year+'-'+month+'-'+str(int(day)-1)+ ' '+self.resources['ends_at_str']
                info_str += format_str % (dhasa, dhasa_end_date)
                di += 9
        key = self.resources['maasa_str']
        value = self._calendar_info[key]
        info_str += format_str % (key,value)
        key = self.resources['ayanamsam_str']+' ('+self._ayanamsa_mode+') '
        value = drik.get_ayanamsa_value(self._horo.julian_day)
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
    def _convert_1d_chart_with_planet_names(self,chart_1d_list): #To be used for Sudarsana Chakra data as input
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
                        pl_str += self.resources['ascendant_short_str']+'/'#' 'Lagnam'+'/'#const._ascendant_symbol+"/"
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
    def _update_tabs_with_divisional_charts(self,jd,place):
        i_end = 0
        format_str = '%-18s%-20s\n'
        _chart_title_separator = ' '
        if 'south' in self._chart_type.lower() or 'east' in self._chart_type.lower():
            _chart_title_separator = '\n'
        if int(self._years_combo.text()) > 1:
            tab_str = self.resources['annual_str']+_chart_title_separator
        elif int(self._months_combo.text()) > 1:
            tab_str = self.resources['monthly_str']+_chart_title_separator
        elif int(self._60hrs_combo.text()) > 1:
            tab_str = self.resources['60hourly_str']+_chart_title_separator
        else:
            tab_str = ''
        self.tabWidget.setTabText(0,self.resources[self.tabNames[0]])
        chara_karaka_names = [x+'_str' for x in house.chara_karaka_names]
        chara_karaka_dict = house.chara_karakas(jd,place)
        planet_count = len(drik.planet_list) + 1 # Inlcuding Lagnam
        upagraha_count = len(const._solar_upagraha_list) + len(const._other_upagraha_list)# + 1 # +1 for upajethu title row
        special_lagna_count = len(const._special_lagna_list)
        total_row_count = planet_count + upagraha_count + special_lagna_count
        print('planet_count',planet_count,'upagraha_count',upagraha_count,'special_lagna_count',special_lagna_count,'total_row_count',total_row_count)
        for t,tab in enumerate(self.tabNames[1:_vimsottari_dhasa_tab_start]):
            dcf = const.division_chart_factors[t]
            """ update the chart from horoscope charts """
            tab_name = tab_str + self.resources[tab]
            _chart_title = tab_name + _chart_title_separator+self._date_text_years + \
                            _chart_title_separator+self._time_text_years +_chart_title_separator+ self._timezone_text
            self.tabWidget.setTabText(t+1,tab_name.replace('\n','-'))
            i_start = i_end # (t-1)*10
            # 26 #29 # 4 for special lagnas, 10 from lagnam and planets, 12 rows for upagraha details
            i_end = i_start + total_row_count
            chart_info = ''
            western_data = []
            if self._western_chart:
                i_start = i_start + special_lagna_count #4 # Skip special lagna rows
                i_end = i_start + planet_count #10 # 13 # count of planets + lagnam
            i_i = -1
            for (k,v) in list(self._horoscope_info.items())[i_start:i_end]:
                i_i += 1
                k1 = k.split('-')[-1]
                v1 = v.split('-')[0]
                if i_i >=5 and i_i <=12 and not self._western_chart:
                    p_i = i_i-5
                    v1 += ' (' + self.resources[chara_karaka_names[chara_karaka_dict[p_i]]] +')'
                chart_info += format_str % (k1,v1)
                western_data.append(k1+' '+v1)
            if self._western_chart:
                i_end += upagraha_count#12
            self._chart_info_labels[t].setText(chart_info) # Fixed defect here in 1.0.2
            self._chart_info_labels[t].setMinimumWidth(_chart_info_label_width)  # Fixed defect here in 1.0.2
            chart_data_1d = self._horoscope_charts[t]
            chart_data_1d = [x[:-1] for x in chart_data_1d] # remove ]n from end of each element
            self._western_chart = False
            if 'north' in self._chart_type.lower():
                _ascendant = drik.ascendant(jd,place)
                asc_house = _ascendant[0]+1
                self._charts[t]._asc_house = asc_house
                chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
                self._charts[t].setData(chart_data_north,chart_title=_chart_title,chart_title_font_size=8)
            elif 'east' in self._chart_type.lower():
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
                self._charts[t]._asc_house = row*self._charts[t].row_count+col
                self._charts[t].setData(chart_data_2d,chart_title=_chart_title)
            elif 'west' in self._chart_type.lower():
                self._western_chart = True
                self._charts[t].setData(western_data,chart_title=_chart_title,chart_title_font_size=8)
                self._charts[t].update()                
            elif 'sudar' in self._chart_type.lower():
                dcf = const.division_chart_factors[t]
                chart_1d = sudharsana_chakra.sudharshana_chakra_chart(jd, place,self._date_of_birth,years_from_dob=0, divisional_chart_factor=dcf)
                #print('chart_1d',chart_1d)
                data_1d = self._convert_1d_chart_with_planet_names(chart_1d)
                self._charts[t].setData(data_1d,chart_title=_chart_title,chart_title_font_size=8)
                self._charts[t].update()                
            else: # south indian
                chart_data_2d = _convert_1d_house_data_to_2d(chart_data_1d)
                row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
                self._charts[t]._asc_house = (row,col)
                self._charts[t].setData(chart_data_2d,chart_title=_chart_title)
            self._charts[t].update()
    def _update_tab_chart_information(self):
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._update_tabs_with_divisional_charts(jd,place)
    def _update_dhasa_bhukthi_tab_information(self,tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              dhasa_info,db_tables):
        self._show_hide_marriage_checkboxes(False)
        tab_title = self.resources[tab_title_str]+'-'+self.resources['dhasa_bhukthi_str']
        for db_tab in range(tab_count):
            p = db_tab*(rows_per_table-1)*tables_per_tab
            for col in range(tables_per_tab):
                i_start = p
                i_end = i_start + rows_per_table-1
                db_list = list(dhasa_info.items())[i_start:i_end]
                if not db_list:
                    continue
                db_str = db_list[0][0].split('-')[0]+' '+self.resources['dhasa_str']
                db_tables[db_tab][col].setItem(0,0,QTableWidgetItem(db_str))
                db_tables[db_tab][col].setItem(0,1,QTableWidgetItem(self.resources['starts_at_str'])) #V2.3.1 Changed to starts_at_str
                t_row = 1
                for k,v in db_list:
                    k1 = k.split('-')[-1]+' '+self.resources['bhukthi_str']
                    #print('db_tab',db_tab,'col',col,k,v,k1)
                    db_tables[db_tab][col].setItem(t_row,0,QTableWidgetItem(k1))
                    db_tables[db_tab][col].setItem(t_row,1,QTableWidgetItem(v))
                    t_row += 1
                p = i_end
                db_tables[db_tab][col].resizeColumnToContents(0)
                db_tables[db_tab][col].resizeColumnToContents(1)
            self.tabWidget.setTabText(tab_start+db_tab,tab_title+'-'+str(db_tab+1))            
    def _update_vimsottari_dhasa_bhukthi_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('vimsottari_str',_vimsottari_dhasa_tab_start,_vimsottari_dhasa_tab_count,
                                                   self._vimsottari_rows_per_table,self._vimsottari_tables_per_tab,
                                              self._vimsottari_dhasa_bhukti_info,self.vimsottari_db_tables)
        return
    def _update_ashtottari_dhasa_bhukthi_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('ashtottari_str',_ashtottari_dhasa_tab_start,_ashtottari_dhasa_tab_count,
                                                   self._ashtottari_rows_per_table,self._ashtottari_tables_per_tab,
                                              self._ashtottari_dhasa_bhukti_info,self.ashtottari_db_tables)
        return
    def _update_narayana_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('narayana_str',_narayana_dhasa_tab_start,_narayana_dhasa_tab_count,
                                                   self._narayana_rows_per_table,self._narayana_tables_per_tab,
                                              self._narayana_dhasa_info,self.narayana_db_tables)
        return
    def _update_kendraadhi_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('kendraadhi_rasi_str',_kendraadhi_dhasa_tab_start,_kendraadhi_dhasa_tab_count,
                                                   self._kendraadhi_rows_per_table,self._kendraadhi_tables_per_tab,
                                              self._kendraadhi_dhasa_info,self.kendraadhi_db_tables)
        return
    def _update_sudasa_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('sudasa_str',_sudasa_dhasa_tab_start,_sudasa_dhasa_tab_count,
                                                   self._sudasa_rows_per_table,self._sudasa_tables_per_tab,
                                              self._sudasa_dhasa_info,self.sudasa_db_tables)
        return
    def _update_drig_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('drig_str',_drig_dhasa_tab_start,_drig_dhasa_tab_count,
                                                   self._drig_rows_per_table,self._drig_tables_per_tab,
                                              self._drig_dhasa_info,self.drig_db_tables)
        return
    def _update_nirayana_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('nirayana_str',_nirayana_dhasa_tab_start,_nirayana_dhasa_tab_count,
                                                   self._nirayana_rows_per_table,self._nirayana_tables_per_tab,
                                              self._nirayana_dhasa_info,self.nirayana_db_tables)
        return
    def _update_shoola_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('shoola_str',_shoola_dhasa_tab_start,_shoola_dhasa_tab_count,
                                                   self._shoola_rows_per_table,self._shoola_tables_per_tab,
                                              self._shoola_dhasa_info,self.shoola_db_tables)
        return
    def _update_patyayini_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('patyayini_str',_patyayini_dhasa_tab_start,_patyayini_dhasa_tab_count,
                                                   self._patyayini_rows_per_table,self._patyayini_tables_per_tab,
                                              self._patyayini_dhasa_info,self.patyayini_db_tables)
        return
    def _update_mudda_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('varsha_vimsottari_str',_mudda_dhasa_tab_start,_mudda_dhasa_tab_count,
                                 self._mudda_rows_per_table,self._mudda_tables_per_tab,
                                              self._mudda_dhasa_info,self.mudda_db_tables)
        return
    def _update_varsha_narayana_dhasa_tab_information(self):
        self._update_dhasa_bhukthi_tab_information('varsha_narayana_str',_varsha_narayana_dhasa_tab_start,_varsha_narayana_dhasa_tab_count,
                                 self._varsha_narayana_rows_per_table,self._varsha_narayana_tables_per_tab,
                                              self._varsha_narayana_dhasa_info,self.varsha_narayana_db_tables)
        return
    def _show_hide_marriage_checkboxes(self,_show = True):
        self._mahendra_porutham_checkbox.setVisible(_show)
        self._vedha_porutham_checkbox.setVisible(_show)
        self._rajju_porutham_checkbox.setVisible(_show)
        self._sthree_dheerga_porutham_checkbox.setVisible(_show)
        self._min_score_label.setVisible(_show)
        self._min_score_combo.setVisible(_show)
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
            col2 = join_str.join([const.houses_str[arp] for arp in r_ahp[row]])
            self._drishti_table2[0].setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in r_app[row] if pl != '' and pl!=const._ascendant_symbol])
            self._drishti_table2[0].setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            col1 = join_str.join([rasi_names_en[arp] for arp in g_arp[row]])
            self._drishti_table1[0].setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp] for arp in g_ahp[row]])
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
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        tab_names = [self.resources[tab] for tab in self.tabNames[1:_vimsottari_dhasa_tab_start]]
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
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._yoga_results,_,_ = yoga.get_yoga_details_for_all_charts(jd,place,language=available_languages[self._language])
        self._yoga_list.clear()
        yoga_count = len(self._yoga_results)
        for k in range(0,yoga_count,_yogas_per_list_item):
            key = ''
            for kk in range(_yogas_per_list_item):
                if k+kk<=yoga_count-kk:
                    key = key+'\n'+''.join(list(self._yoga_results.values())[k+kk][1].split()[0:-1])
            key = key[1:]
            self._yoga_list.addItem(QListWidgetItem(key))
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
        results_table.setHorizontalHeaderItem(0,QTableWidgetItem(nakshatra+'-'+paadham))
        results_table.setHorizontalHeaderItem(1,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(2,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(3,QTableWidgetItem(''))
        row = 0
        for p,porutham in enumerate(ettu_poruthham_list):
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
                results_table.setItem(row,3,QTableWidgetItem(str('\u2705')))
            else:
                results_table.setItem(row,3,QTableWidgetItem(str('\u274C')))
            row += 1
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
            self._update_vimsottari_dhasa_bhukthi_tab_information()
            self._update_ashtottari_dhasa_bhukthi_tab_information()
            self._update_narayana_dhasa_tab_information()
            self._update_kendraadhi_dhasa_tab_information()
            self._update_sudasa_dhasa_tab_information()
            self._update_drig_dhasa_tab_information()
            self._update_nirayana_dhasa_tab_information()
            self._update_shoola_dhasa_tab_information()
            self._update_patyayini_dhasa_tab_information()
            self._update_mudda_dhasa_tab_information()
            self._update_varsha_narayana_dhasa_tab_information()
            self._update_ashtaka_varga_tab_information()
            self._update_drishti_table_information()
            self._update_argala_table_information()
            self._update_shodhaya_table_information()
            self._update_yoga_tab_information()
            if  self._show_compatibility:
                self._update_compatibility_tab_information()
        self.update()
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
        if not self._western_chart:
            self._matching_star_list.setVisible(False)
            self._matching_star_list.setMaximumWidth(0)
            self._yoga_list.setVisible(False)
            self._yoga_list.setMaximumWidth(0)
            for c in range(_comp_results_per_list_item):
                self._comp_results_table[c].update()
            self._yoga_text.update()
        if pdf_file_name:
            self._hide_show_layout_widgets(self._row3_h_layout, False)
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
        planet_list_en = ['Sun ☉','Moon ☾','Mars ♂','Mercury ☿','Jupiter ♃','Venus ♀','Saturn ♄','Raagu ☊','Kethu ☋','Uranus','Neptune','Pluto','Lagnam']
        planet_lang_dict = {planet_list_lang[i]:planet_list_en[i] for i in range(len(planet_list_en))}
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v)
        return rasi_1d_en
    def _convert_language_chart_to_indices(self,rasi_1d_lang):
        rasi_1d_en = self._convert_language_chart_to_english(rasi_1d_lang)
        planet_list_en = ['Sun ☉','Moon ☾','Mars ♂','Mercury ☿','Jupiter ♃','Venus ♀','Saturn ♄','Raagu ☊','Kethu ☋','Uranus','Neptune','Pluto']+['Lagnam']
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
def _udhayadhi_nazhikai(birth_time,sunrise_time):
    """ TODO: this will not for work for BC dates due to datetime """
    def _convert_str_to_time(str_time):
        arr = str_time.split(':')
        arr[-1] = arr[-1].replace('AM','').replace('PM','')
        return time(int(arr[0]),int(arr[1]),int(arr[2]))
    birth_time = _convert_str_to_time(birth_time)
    sunrise_time =_convert_str_to_time(sunrise_time)
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
    chart_type = 'South Indian'
    chart = ChartTabbed(chart_type=chart_type,show_marriage_compatibility=True)
    chart.language('Tamil')
    chart.name('Today')
    loc = utils.get_place_from_user_ip_address()
    print('loc from IP address',loc)
    if loc:
        chart.place(loc[0])
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    chart.date_of_birth(current_date_str)
    chart.time_of_birth(current_time_str)
    chart.chart_type(chart_type)
    chart.compute_horoscope(calculation_type='drik')
    chart.show()
    #chart.save_as_pdf('./output.pdf')
    sys.exit(App.exec())
