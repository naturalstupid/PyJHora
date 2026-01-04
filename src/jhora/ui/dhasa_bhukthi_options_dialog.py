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
_chart_names = ['raasi_str', 'hora_str', 'drekkanam_str', 'chaturthamsa_str', 'panchamsa_str', 
    'shashthamsa_str', 'saptamsam_str', 'ashtamsa_str', 'navamsam_str', 'dhasamsam_str', 'rudramsa_str', 
    'dhwadamsam_str', 'shodamsa_str', 'vimsamsa_str', 'chaturvimsamsa_str', 'nakshatramsa_str', 'thrisamsam_str', 
    'khavedamsa_str', 'akshavedamsa_str', 'sashtiamsam_str', 
    'nava_navamsa_str', 'ashtotharamsa_str', 'dwadas_dwadasamsa_str']
_graha_dhasa_list = ['vimsottari','yoga_vimsottari','rasi_bhukthi_vimsottari','ashtottari','tithi_ashtottari',
                     'yogini','tithi_yogini','shodasottari','dwadasottari','dwisatpathi','panchottari','satabdika',
                     'chaturaaseeti_sama','karana_chaturaaseeti_sama','shashtisama','shattrimsa_sama','naisargika',
                     'tara','karaka','buddhi_gathi','kaala','aayu','saptharishi_nakshathra']
_tithi_list = ['janma_tithi_str','dhana_tithi_str','bhrartri_tithi_str','matri_tithi_str','putra_tithi_str',
               'satru_tithi_str','kalatra_tithi_str','mrutyu_tithi_str','bhagya_tithi_str','karma_tithi_str',
               'laabha_tithi_str','vyaya_tithi_str']
seed_list_dhasas = {0:3,2:3,3:6,5:7,7:8,8:27,9:19,10:17,11:27,12:15,14:1,15:22}
dhasa_start_planet_dhasas = [0,2,3,5,7,8,9,10,11,12,14,15,22]
start_from_moon_dhasas = [0,2,3,5,7,8,9,10,11,12,14,15,22]
tribhagi_dhasas = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,22]
varga_dhasas = [0,2,3,5,7,8,9,10,11,12,14,15,17,19,22]
antardhasa_option_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,22]
tithi_dhasas = [4,6]
_varga_option_dict = const.varga_option_dict
class DhasaBhukthiOptionDialog(QDialog):
    """
        Dhasa Bhukthi Options Dialog
    """
    def __init__(self, dhasa_index=0, dhasa_option_list=None):
        super().__init__()
        #utils.set_language(const._DEFAULT_LANGUAGE)
        self._dhasa_index = dhasa_index
        self._dhasa_option_list = const.dhasa_default_options[dhasa_index] if dhasa_option_list==None else dhasa_option_list
        self.res = utils.resource_strings
        self._graha_dhasa_dict = [self.res[d+'_str'] for d in _graha_dhasa_list]
        self._dhasa_name = self._graha_dhasa_dict[self._dhasa_index]
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
        title = self._dhasa_name+' '+self.res['dhasa_str']+' '+self.res['options_str']
        self.setWindowTitle(title)
        _option_counter = 0
        if self._dhasa_index==21: #'aayu':
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
        elif self._dhasa_index==16: # Naisargika
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
        elif self._dhasa_index==17: # Tara
            self._tara_method_visible = True
            _label = QLabel(self.res['tara_dhasa_option1_str'])
            v_layout.addWidget(_label)
            self._tara_method_combo = QComboBox()
            self._tara_method_combo.addItems([self.res['tara_dhasa_option2_str'],
                                              self.res['tara_dhasa_option3_str']])
            self._tara_method_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            v_layout.addWidget(self._tara_method_combo)
            self.setLayout(v_layout)
        elif self._dhasa_index==2: # Raasi Bhukthi Variation
            self._rbv_variation_visible = True
            self._rbv_check = QCheckBox(self.res['rbv_dhasa_option_str'])
            self._rbv_check.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            self._rbv_check.setEnabled(False)
            v_layout.addWidget(self._rbv_check)
            self.setLayout(v_layout)
        if self._dhasa_index in tithi_dhasas:
            self._tithi_list_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['tithi_index_option_str'])
            h_layout1.addWidget(_label)
            self._tithi_combo = QComboBox()
            self._tithi_combo.addItems([self.res[t] for t in _tithi_list])
            self._tithi_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._tithi_combo)
            v_layout.addLayout(h_layout1)
        if self._dhasa_index in tribhagi_dhasas: # Tribhagi
            self._tribhagi_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['tribhagi_option_str'])
            h_layout1.addWidget(_label)
            self._tribhagi_check = QCheckBox()
            self._tribhagi_check.setChecked(self._dhasa_option_list[_option_counter]); _option_counter+=1
            h_layout1.addWidget(self._tribhagi_check)
            v_layout.addLayout(h_layout1)
        if self._dhasa_index in seed_list_dhasas.keys(): # Seed Star
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
        if self._dhasa_index in dhasa_start_planet_dhasas: # dhasa start
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
        if self._dhasa_index in start_from_moon_dhasas: # start from moon
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
        if self._dhasa_index in antardhasa_option_list: # Antardhasa Option
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
        if self._dhasa_index in varga_dhasas: # Varga Chart 
            self._varga_chart_visible = True
            h_layout1 = QHBoxLayout()
            _label = QLabel(self.res['varga_option_str'])
            h_layout1.addWidget(_label)
            self._varga_chart_combo = QComboBox()
            varga_chart_list = [self.res[c] for c in _chart_names]
            self._varga_chart_combo.addItems(varga_chart_list)
            self._varga_chart_combo.setCurrentIndex(self._dhasa_option_list[_option_counter]); _option_counter+=1
            self._varga_chart_combo.currentIndexChanged.connect(self._varga_chart_selection_changed)
            h_layout1.addWidget(self._varga_chart_combo)
            v_layout.addLayout(h_layout1)
            if self._dhasa_option_list[_option_counter] != -1:
                h_layout1 = QHBoxLayout()
                self._varga_chart_method_label = QLabel(self.res['choose_varga_chart_method_str'])
                self._varga_chart_method_label.setVisible(True)
                h_layout1.addWidget(self._varga_chart_method_label)
                self._varga_chart_method_combo = QComboBox()
                self._varga_chart_method_combo.setVisible(True)
                _varga_chart_index = self._varga_chart_combo.currentIndex()
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
        _varga_chart_index = self._varga_chart_combo.currentIndex()
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
            ind = self._varga_chart_combo.currentIndex()
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
if __name__ == "__main__":
    import sys
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = DhasaBhukthiOptionDialog(2,[True,False,2,13,0,0,0,-1])
    chart.show()
    sys.exit(App.exec())

