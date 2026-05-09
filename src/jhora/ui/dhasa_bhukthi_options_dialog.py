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
from PyQt6.QtWidgets import QLineEdit, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,\
                            QComboBox, QDialog, QCheckBox
from PyQt6.QtCore import Qt
from jhora import utils, const
from jhora.panchanga.drik import Date
_chart_names = const._chart_names
""" Below list should match horo_chart_tabs._graha_dhasa_dict and length should match const.graha_dhasa_default_options"""
#_graha_dhasa_list = const._graha_dhasa_dict.keys()
_tithi_list = ['janma_tithi_str','dhana_tithi_str','bhrartri_tithi_str','matri_tithi_str','putra_tithi_str',
               'satru_tithi_str','kalatra_tithi_str','mrutyu_tithi_str','bhagya_tithi_str','karma_tithi_str',
               'laabha_tithi_str','vyaya_tithi_str']
# seed_list_dhasas = {dhasa:seed_star}
seed_list_dhasas = {'vimsottari':3,'rasi_bhukthi_vimsottari':3,'ashtottari':6,'yogini':7,'shodasottari':8,'dwadasottari':27,
                    'dwisatpathi':19,'panchottari':17,'satabdika':27,'chaturaaseeti_sama':15,'shashtisama':1,'shattrimsa_sama':22}
dhasa_start_planet_dhasas = ['vimsottari','rasi_bhukthi_vimsottari','ashtottari','yogini','shodasottari','dwadasottari',
                             'dwisatpathi','panchottari','satabdika','chaturaaseeti_sama','shashtisama','shattrimsa_sama',
                             'saptharishi_nakshathra']
start_from_moon_dhasas = ['vimsottari','rasi_bhukthi_vimsottari','ashtottari','yogini','shodasottari','dwadasottari',
                             'dwisatpathi','panchottari','satabdika','chaturaaseeti_sama','shashtisama','shattrimsa_sama',
                             'saptharishi_nakshathra']
tribhagi_dhasas = ['vimsottari','yoga_vimsottari','rasi_bhukthi_vimsottari','ashtottari','tithi_ashtottari','yogini',
                   'tithi_yogini','shodasottari','dwadasottari','dwisatpathi','panchottari','satabdika','chaturaaseeti_sama',
                   'karana_chaturaaseethi_sama','shashtisama','shattrimsa_sama','saptharishi_nakshathra']
varga_dhasas = ['vimsottari','rasi_bhukthi_vimsottari','ashtottari','yogini','shodasottari','dwadasottari','dwisatpathi',
                'panchottari','satabdika','chaturaaseeti_sama','shashtisama','shattrimsa_sama','tara','karaka','buddhi_gathi',
                'saptharishi_nakshathra','rashmi','ashtaka_varga_planet','ashtaka_varga_pinda','narayana','lagna_kendraadhi','sudasa','drig',
                'niryaana', 'shoola','karaka_kendraadhi','chara','lagnamsaka','padhanadhamsa','mandooka','sthira','tara_lagna',
                'brahma','varnada','yogardha','navamsa','paryaaya','trikona','kalachakra','chakra','sandhya','pachaka',
                'raashiyanka','ashtaka_varga_sign','chathurvidha_lagna_utthara','chathurvidha_kendra_utthara',
                'chathurvidha_trikona_utthara','chathurvidha_dasha_utthara']
antardhasa_option_list = ['vimsottari','yoga_vimsottari','rasi_bhukthi_vimsottari','ashtottari','tithi_ashtottari','yogini',
                          'tithi_yogini','shodasottari','dwadasottari','dwisatpathi','panchottari','satabdika',
                          'chaturaaseeti_sama','karana_chaturaaseethi_sama','shashtisama','shattrimsa_sama',
                          'saptharishi_nakshathra']
tithi_dhasas = ['tithi_ashtottari','tithi_yogini']
_varga_option_dict = const.varga_option_dict
class DhasaBhukthiOptionDialog(QDialog):
    """
        Dhasa Bhukthi Options Dialog
    """
    def __init__(self, dhasa_name=None, dhasa_option_list=None):
        super().__init__()
        if dhasa_name is None or dhasa_name not in const.dhasa_default_options.keys():
            raise ValueError ("dhasa_name is a required argument and should be one of const.graha_dhasa_default_options.keys()")
        self._dhasa_name = dhasa_name.lower()
        self._dhasa_option_list = const.dhasa_default_options[dhasa_name] if dhasa_option_list==None else dhasa_option_list
        if len(self._dhasa_option_list) == 0: self._cancel_button_clicked() 
        self.res = utils.resource_strings
        #self._graha_dhasa_dict = [self.res[d+'_str'] for d in _graha_dhasa_list]
        #self._dhasa_name = self._graha_dhasa_dict[self._dhasa_index]
        self._tribhagi_visible = False
        self._aayu_visible = False
        self._seed_star_visible = False
        self._dhasa_start_visible = False
        self._moon_start_visible = False
        self._ant_option_visible = False
        self._varga_chart_visible = False
        self._varga_chart_method_visible = False
        self._naisargika_option_visible = False
        self._tithi_list_visible = False
        self._rbv_variation_visible = False
        self._tara_method_visible = False
        self._option_string = ''
        self.create_ui()
    def closeEvent(self, *args, **kwargs):
        self._option_string = ''
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)
    def create_ui(self):
        v_layout = QVBoxLayout()
        title = self.res[self._dhasa_name+"_str"]+' '+self.res['dhasa_str']+' '+self.res['options_str']
        self.setWindowTitle(title)
        _option_counter = 0
        if self._dhasa_name=='aayu': #'aayu':
            self._aayu_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['aayu_dhasa_option_str'])
            h_layout1.addWidget(_label)
            dhasa_type_list = [self.res['pindayu_str'],self.res['nisargayu_str'],self.res['amsayu_str'],'None']
            self._dhasa_type_combo = QComboBox()
            self._dhasa_type_combo.addItems(dhasa_type_list)
            self._dhasa_type_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._dhasa_type_combo)
            v_layout.addLayout(h_layout1)
            self.setLayout(v_layout)
        elif self._dhasa_name=='naisargika': # Naisargika
            self._naisargika_option_visible = True
            v_layout1 = QVBoxLayout()
            _label = QLabel(self.res['nisargika_dhasa_option1_str'])
            v_layout1.addWidget(_label)
            self._naisargika_option1 = QCheckBox(self.res['nisargika_dhasa_option2_str'])
            self._naisargika_option1.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            v_layout1.addWidget(self._naisargika_option1)
            self._naisargika_option2 = QCheckBox(self.res['nisargika_dhasa_option3_str'])
            self._naisargika_option2.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            v_layout1.addWidget(self._naisargika_option2)
            self._naisargika_option3 = QCheckBox(self.res['nisargika_dhasa_option4_str'])
            self._naisargika_option3.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            v_layout1.addWidget(self._naisargika_option3)
            v_layout.addLayout(v_layout1)
            self.setLayout(v_layout)
        elif self._dhasa_name=='tara': # Tara
            self._tara_method_visible = True
            _label = QLabel(self.res['tara_dhasa_option1_str'])
            v_layout.addWidget(_label)
            self._tara_method_combo = QComboBox()
            self._tara_method_combo.addItems([self.res['tara_dhasa_option2_str'],
                                              self.res['tara_dhasa_option3_str']])
            self._tara_method_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            v_layout.addWidget(self._tara_method_combo)
            self.setLayout(v_layout)
        elif self._dhasa_name=='rasi_bhukthi_vimsottari': # Raasi Bhukthi Variation
            self._rbv_variation_visible = True
            self._rbv_check = QCheckBox(self.res['rbv_dhasa_option_str'])
            self._rbv_check.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            self._rbv_check.setEnabled(False)
            v_layout.addWidget(self._rbv_check)
            self.setLayout(v_layout)
        if self._dhasa_name in tithi_dhasas:
            self._tithi_list_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['tithi_index_option_str'])
            h_layout1.addWidget(_label)
            self._tithi_combo = QComboBox()
            self._tithi_combo.addItems([self.res[t] for t in _tithi_list])
            self._tithi_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._tithi_combo)
            v_layout.addLayout(h_layout1)
        if self._dhasa_name in tribhagi_dhasas: # Tribhagi
            self._tribhagi_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['tribhagi_option_str'])
            h_layout1.addWidget(_label)
            self._tribhagi_check = QCheckBox()
            self._tribhagi_check.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._tribhagi_check)
            v_layout.addLayout(h_layout1)
        if self._dhasa_name in seed_list_dhasas.keys(): # Seed Star
            self._seed_star_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['seed_star_option_str'])
            h_layout1.addWidget(_label)
            self._seed_star_combo = QComboBox()
            seed_list = [utils.NAKSHATRA_LIST[n] for n in range(27)]
            self._seed_star_combo.addItems(seed_list)
            self._seed_star_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._seed_star_combo)
            v_layout.addLayout(h_layout1)
        if self._dhasa_name in dhasa_start_planet_dhasas: # dhasa start
            self._dhasa_start_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['dhasa_start_option_str'])
            h_layout1.addWidget(_label)
            self._dhasa_start_combo = QComboBox()
            dhasa_start_list = [utils.PLANET_NAMES[p]+'-'+self.res['sphuta_str'] for p in range(9)]+\
                    [self.res['ascendant_str']+'-'+self.res['sphuta_str'],self.res['maandi_str']+'-'+self.res['sphuta_str'],
                    self.res['gulika_str']+'-'+self.res['sphuta_str'],self.res['tri_sphuta_str']+'-'+self.res['sphuta_str'],
                    self.res['bhrigu_bindhu_lagna_str'],self.res['indu_lagna_str'],self.res['pranapada_lagna_str']]
            self._dhasa_start_combo.addItems(dhasa_start_list)
            self._dhasa_start_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._dhasa_start_combo)
            v_layout.addLayout(h_layout1)
        if self._dhasa_name in start_from_moon_dhasas: # start from moon
            self._moon_start_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['moon_start_option1_str'])
            h_layout1.addWidget(_label)
            self._moon_start_combo = QComboBox()
            moon_start_list = [self.res['moon_start_option2_str'],self.res['moon_start_option3_str'],
                                self.res['moon_start_option4_str'],self.res['moon_start_option5_str']]
            self._moon_start_combo.addItems(moon_start_list)
            self._moon_start_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._moon_start_combo)
            v_layout.addLayout(h_layout1)
        if self._dhasa_name in antardhasa_option_list: # Antardhasa Option
            self._ant_option_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['ant_dhasa_option_str'])
            h_layout1.addWidget(_label)
            self._ant_option_combo = QComboBox()
            ant_option_list = [self.res['ant_dhasa_option1_str'],self.res['ant_dhasa_option2_str'],
                               self.res['ant_dhasa_option3_str'],self.res['ant_dhasa_option4_str'],
                               self.res['ant_dhasa_option5_str'],self.res['ant_dhasa_option6_str']]
            self._ant_option_combo.addItems(ant_option_list)
            self._ant_option_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._ant_option_combo)
            v_layout.addLayout(h_layout1)
        if self._dhasa_name in varga_dhasas: # Varga Chart 
            self._varga_chart_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['varga_option_str'])
            h_layout1.addWidget(_label)
            self._star_chart_combo = QComboBox()
            varga_chart_list = [self.res[c] for c in _chart_names]
            self._star_chart_combo.addItems(varga_chart_list)
            self._star_chart_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            self._star_chart_combo.currentIndexChanged.connect(self._varga_chart_selection_changed)
            h_layout1.addWidget(self._star_chart_combo)
            v_layout.addLayout(h_layout1)
            if self._dhasa_option_list[_option_counter] != -1:
                h_layout1 = QHBoxLayout()
                self._varga_chart_method_label = QLabel(self.res['choose_varga_chart_method_str'])
                self._varga_chart_method_label.setVisible(True)
                h_layout1.addWidget(self._varga_chart_method_label)
                self._varga_chart_method_combo = QComboBox()
                self._varga_chart_method_combo.setVisible(True)
                _varga_chart_index = self._star_chart_combo.currentIndex()
                _varga_factor = const.division_chart_factors[_varga_chart_index]
                _method_count = _varga_option_dict[_varga_factor][0]
                for m in range(_method_count):
                    _varga_method = self.res['d'+str(_varga_factor)+'_option'+str(m+1)+'_str']
                    self._varga_chart_method_combo.addItem(_varga_method)
                self._varga_chart_method_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
                h_layout1.addWidget(self._varga_chart_method_combo)
                v_layout.addLayout(h_layout1)
            else:
                h_layout1 = QHBoxLayout()
                self._varga_chart_method_label = QLabel(self.res['choose_varga_chart_method_str'])
                self._varga_chart_method_label.setVisible(False)
                h_layout1.addWidget(self._varga_chart_method_label)
                self._varga_chart_method_combo = QComboBox()
                self._varga_chart_method_combo.setVisible(False)
                h_layout1.addWidget(self._varga_chart_method_combo)
                v_layout.addLayout(h_layout1)
        if all([self._tribhagi_visible, self._aayu_visible, self._ant_option_visible, self._dhasa_start_visible,
                self._moon_start_visible, self._seed_star_visible, self._varga_chart_visible,
                self._naisargika_option_visible, self._tithi_list_visible,self._rbv_variation_visible,
                self._tara_method_visible])==False:
            self._cancel_button_clicked()
        h_layout = QHBoxLayout()
        self._accept_button = QPushButton(self.res['accept_str'])
        self._accept_button.clicked.connect(self._accept_button_clicked)
        h_layout.addWidget(self._accept_button)
        self._cancel_button = QPushButton(self.res['cancel_str'])
        self._cancel_button.clicked.connect(self._cancel_button_clicked)
        h_layout.addWidget(self._cancel_button)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
    def _varga_chart_selection_changed(self):
        _varga_chart_index = self._star_chart_combo.currentIndex()
        _varga_factor = const.division_chart_factors[_varga_chart_index]
        if _varga_factor ==1:
            self._varga_chart_method_combo.setVisible(False)
            self._varga_chart_method_visible = False
            self._varga_chart_method_label.setVisible(False)
            return
        _method_count = _varga_option_dict[_varga_factor][0]
        _default_method = _varga_option_dict[_varga_factor][1]
        self._varga_chart_method_combo.clear()
        for m in range(_method_count):
            _varga_method = self.res['d'+str(_varga_factor)+'_option'+str(m+1)+'_str']
            self._varga_chart_method_combo.addItem(_varga_method)
        self._varga_chart_method_combo.setCurrentIndex(_default_method-1)
        self._varga_chart_method_combo.setVisible(True)
        self._varga_chart_method_label.setVisible(True)
        self._varga_chart_method_visible = True
    def _accept_button_clicked(self):
        option_str = []; option_list = []
        if self._aayu_visible:
            ind = self._dhasa_type_combo.currentIndex()
            opt = 'aayur_type='+str(ind) if ind in [0,1,2] else 'aayur_type=None'
            option_str.append(opt); option_list.append(ind)
        elif self._naisargika_option_visible:
            ind1 = self._naisargika_option1.isChecked()
            opt = 'mahadhasa_lord_has_no_antardhasa='+str(bool(ind1))
            option_str.append(opt); option_list.append(bool(ind1))
            ind2 = self._naisargika_option2.isChecked()
            opt = 'antardhasa_option1='+str(bool(ind2))
            option_str.append(opt); option_list.append(bool(ind2))
            ind3 = self._naisargika_option3.isChecked()
            opt = 'antardhasa_option2='+str(bool(ind3))
            option_str.append(opt); option_list.append(bool(ind3))
        if self._tara_method_visible:
            ind = self._tara_method_combo.currentIndex()
            opt = 'dhasa_method='+str(ind+1)
            option_str.append(opt); option_list.append(ind)
        if self._rbv_variation_visible: #RBV
            ind = self._rbv_check.isChecked()
            opt = 'use_rasi_bhukthi_variation='+str(bool(ind))
            option_str.append(opt);option_list.append(bool(ind))
        if self._tithi_list_visible:
            ind = self._tithi_combo.currentIndex()
            opt = 'tithi_index='+str(ind+1)
            option_str.append(opt); option_list.append(ind)
        if self._tribhagi_visible:
            ind = self._tribhagi_check.isChecked()
            opt = 'use_tribhagi_variation='+str(bool(ind))
            option_str.append(opt); option_list.append(bool(ind))
        if self._seed_star_visible:
            ind = self._seed_star_combo.currentIndex()
            opt = 'seed_star='+str(ind+1)
            option_str.append(opt); option_list.append(ind)
        if self._dhasa_start_visible:
            ind = self._dhasa_start_combo.currentIndex()
            ind_dict = {0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:"'L'",10:"'M'",11:"'G'",12:"'T'",13:"'B'",14:"'I'",15:"'P'"}
            opt = 'dhasa_starting_planet='+str(ind_dict[ind])
            option_str.append(opt); option_list.append(ind)
        if self._moon_start_visible:
            ind = self._moon_start_combo.currentIndex()
            ind_dict = {0:1,1:4,2:5,3:8}
            opt = 'star_position_from_moon='+str(ind_dict[ind])
            option_str.append(opt); option_list.append(ind)
        if self._ant_option_visible:
            ind = self._ant_option_combo.currentIndex()
            opt = 'antardhasa_option='+str(ind+1)
            option_str.append(opt); option_list.append(ind)
        if self._varga_chart_visible:
            ind = self._star_chart_combo.currentIndex()
            dcf = const.division_chart_factors[ind]
            opt = 'divisional_chart_factor='+str(dcf)
            option_str.append(opt); option_list.append(ind)
            if self._varga_chart_method_visible:
                ind = self._varga_chart_method_combo.currentIndex()
                opt = 'chart_method='+str(ind+1)
                option_str.append(opt); option_list.append(ind)
            else:
                option_list.append(-1)
        option_str = ','.join(option_str)
        self._accept_clicked = True
        self._option_string = option_str
        #print(option_str)
        self._option_list = option_list
        #print(option_list)
        self.accept()
    def _cancel_button_clicked(self):
        self._accept_clicked = False
        self._option_string = ''
        self.reject()
        return

class RunningDhasaDialog(QDialog):
    def __init__(self,dhasa_name,dhasa_type=None, db=None, dhasa_cycle_count=1, parent=None,
                 jd_at_dob=None,place=None,options_dict={}):
        super().__init__(parent)
        if dhasa_name is not None and dhasa_type is None:
            dhasa_type = (0 if dhasa_name in const._graha_dhasa_dict.keys()
                            else (1 if dhasa_name in const._rasi_dhasa_dict.keys() else 2) 
                           )
        self.dhasa_type = dhasa_type
        self.dhasa_name = dhasa_name
        self.jd_at_dob = jd_at_dob; self.place = place
        self.db = db
        self.options_dict = options_dict
        self.dhasa_cycle_count = dhasa_cycle_count
        self.resources = utils.resource_strings

        self.setWindowTitle(self.resources['show_running_dhasa_str'])
        #self.setMinimumWidth(600)

        v_layout = QVBoxLayout(self)

        # -------------------------------------------------------
        # Row for Date and Time Input
        # -------------------------------------------------------
        datetime_row = QHBoxLayout()

        # Default values (current system time)
        from datetime import datetime
        now = datetime.now()
        y, m, d = now.year, now.month, now.day
        hh, mm, ss = now.hour, now.minute, now.second

        self.date_edit = QLineEdit(f"{y},{m},{d}")
        self.time_edit = QLineEdit(f"{hh}:{mm}:{ss}")

        self.date_edit.setToolTip("YYYY,MM,DD")
        self.time_edit.setToolTip("HH:MM:SS")

        datetime_row.addWidget(QLabel(self.resources['current_date_str']))
        datetime_row.addWidget(self.date_edit)

        datetime_row.addWidget(QLabel(self.resources['time_of_birth_str']))
        datetime_row.addWidget(self.time_edit)

        v_layout.addLayout(datetime_row)

        # -------------------------------------------------------
        # Results Label (Multi-line output)
        # -------------------------------------------------------
        self.results_area = QLabel()
        #self.results_area.setReadOnly(True)
        #self.results_area.setMinimumHeight(250)
        v_layout.addWidget(self.results_area)

        # -------------------------------------------------------
        # Buttons Row
        # -------------------------------------------------------
        button_row = QHBoxLayout()

        compute_btn = QPushButton(self.resources['compute_str'])
        compute_btn.clicked.connect(self.compute_results)
        button_row.addWidget(compute_btn)

        cancel_btn = QPushButton(self.resources['cancel_str'])
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)

        v_layout.addLayout(button_row)

    # ------------------------------------------------------------------
    # COMPUTE RESULTS BASED ON USER INPUT
    # ------------------------------------------------------------------
    def compute_results(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            # ------------------ Parse Date ---------------------
            y, m, d = map(int, self.date_edit.text().split(','))

            # ------------------ Parse Time ---------------------
            hh, mm, ss = map(int, self.time_edit.text().split(':'))

        except Exception:
            self.results_area.setText("<b>Invalid date/time format</b>")
            return

        # Convert to JD
        current_jd = utils.julian_day_number(
            Date(y, m, d),
            (hh, mm, ss)
        )
        if self.db is None:
            module, defaults = utils._get_import_dhasa_module(self.dhasa_name)
            # 2) Locate callable
            func = getattr(module, "get_running_dhasa_for_given_date", None)
            if not callable(func):
                raise AttributeError(f"{module.__name__}.get_running_dhasa_for_given_date not found/callable")
            # 3) Build opts (defaults ⊕ user), user wins
            import ast
            def _val(x):
                x = x.strip()
                if x.lower() in ("true", "false", "none"):
                    return {"true": True, "false": False, "none": None}[x.lower()]
                try:
                    return ast.literal_eval(x)  # quoted strings, numbers, lists, etc.
                except Exception:
                    return x                    # unquoted token becomes a plain str
            opts = ({k.strip(): _val(v)
                     for k, v in (pair.split("=", 1) for pair in self.options_dict.split(",") if "=" in pair)}
                    if self.options_dict else {})
            opts = {**defaults, **opts}  # merge, user overrides
            # 4) Call
            rd = func(current_jd, self.jd_at_dob, self.place, **opts)
            """
            for row in rd:
                lords,ds,de = row
                print([utils.RAASI_LIST[lord] for lord in lords],ds,de)
            """
        else:
            #print(self.dhasa_name,'utils.get_running_dhasa_at_all_levels_for_given_date')
            rd = utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                self.db,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=self.dhasa_cycle_count
            )
        if rd is None:
            html = "<html><b>"+f"{self.dhasa_name} is not supported.</b></html>"
            self.results_area.setText(html)
            return
        _dhasa_type = (self.resources['graha_str'] if self.dhasa_type==0 else 
                       (self.resources['raasi_str'] if self.dhasa_type==1 else self.resources['annual_str']) ) 
        html = "<html><b>"+f"{self.resources[self.dhasa_name+'_str']} {_dhasa_type} {self.resources['dhasa_str']}"+":<br>"
        html += "<table border=1 cellspacing=0 cellpadding=4>"
        html += (
            f"<tr>"
            f"<th>{self.resources['dhasa_str']}</th>"
            f"<th>{self.resources['lord_str']}</th>"
            f"<th>{self.resources['starts_at_str']}</th>"
            f"<th>{self.resources['ends_at_str']}</th>"
            f"</tr>"
        )

        dli_lords = ['maha_str','antara_str','prathyanthara_str','sookshma_str','praana_str','deha_str']

        for dli, row in enumerate(rd):
            lord = row[0][dli]
            #if isinstance(lord, tuple):
            #    print('karaka lords',lord)
            #    lord = lord[1]

            start = row[1]
            end = row[2]
            if self.dhasa_name in const.nakshathra_dhasas:
                lord_str = utils.NAKSHATRA_LIST[lord]
            elif self.dhasa_name in const.special_dhasas:
                lord_str = self.resources[lord + "_str"]
            elif self.dhasa_type in [0,2] and self.dhasa_name in const.planet_dhasas:
                lord_str = utils.resource_strings['ascendant_str'] if lord==const._ascendant_symbol else utils.PLANET_NAMES[lord]
            elif self.dhasa_name in const.tuple_dhasas:
                if self.dhasa_name.lower() == 'karaka':
                    lord_str = utils.PLANET_NAMES[lord[1]]+' ('+self.resources[lord[0]+'_str']+')'
                elif self.dhasa_name.lower() == 'sudarsana_chakra':
                    lord_str = '/'.join([utils.RAASI_LIST[l] for l in lord ])
            elif self.dhasa_type==1 and self.dhasa_name in const.rasi_dhasas:
                lord_str = utils.RAASI_LIST[lord]
            else:
                lord_str = "?"

            # Format start/end
            s = f"{start[0]:04}-{start[1]:02}-{start[2]:02} {utils.to_dms(start[-1])}"
            e = f"{end[0]:04}-{end[1]:02}-{end[2]:02} {utils.to_dms(end[-1])}"

            html += (
                f"<tr>"
                f"<td>{self.resources[dli_lords[dli]]}</td>"
                f"<td>{lord_str}</td>"
                f"<td>{s}</td>"
                f"<td>{e}</td>"
                f"</tr>"
            )

        html += "</table></b></html>"
        QApplication.restoreOverrideCursor()
        self.results_area.setText(html)
        self.adjustSize()
        
if __name__ == "__main__":
    import sys
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    #"""
    from jhora.panchanga.drik import Date,Place
    dob = Date(1996,12,7); tob = (10,34,0)
    place = Place('Chennai,IN', 13.0389, 80.2619, +5.5)    
    jd_at_dob  = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y,m,d = map(int,current_date_str.split(','))
    hh,mm,ss = map(int,current_time_str.split(':')); fh = hh+mm/60+ss/3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(Date(y,m,d),(hh,mm,ss))
    _dhasa_name = 'karaka'
    import random
    _dhasa_name = random.choice(const.supported_dhasas)
    opts = ''#'divisional_chart_factor=9,chart_method=3'
    dlg = RunningDhasaDialog(dhasa_name=_dhasa_name,jd_at_dob=jd_at_dob,place=place,options_dict=opts)
    dlg.show()
    sys.exit(App.exec())
    exit()
    #"""
    """
    print('total graha dhasas',len(const.dhasa_default_options))
    import random
    _dhasa_name = random.choice(list(const.dhasa_default_options))
    _dhasa_name = 'narayana'
    print('Selected Dhasa',utils.resource_strings[_dhasa_name+"_str"])
    _graha_dhasa_options = const.dhasa_default_options[_dhasa_name]
    print(_graha_dhasa_options)
    chart = DhasaBhukthiOptionDialog(dhasa_name=_dhasa_name,dhasa_option_list=_graha_dhasa_options)
    #chart = DhasaBhukthiOptionDialog(2,[True,False,2,13,0,0,0,-1])
    chart.show()
    sys.exit(App.exec())
    """