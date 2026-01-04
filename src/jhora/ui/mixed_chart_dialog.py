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
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QRadioButton,QDialog, QHBoxLayout,\
                            QPushButton,QSpinBox, QComboBox, QCheckBox, QFrame, QButtonGroup
from jhora import utils, const

_chart_names = ['raasi_str', 'hora_str', 'drekkanam_str', 'chaturthamsa_str', 'panchamsa_str', 
    'shashthamsa_str', 'saptamsam_str', 'ashtamsa_str', 'navamsam_str', 'dhasamsam_str', 'rudramsa_str', 
    'dhwadamsam_str', 'shodamsa_str', 'vimsamsa_str', 'chaturvimsamsa_str', 'nakshatramsa_str', 'thrisamsam_str', 
    'khavedamsa_str', 'akshavedamsa_str', 'sashtiamsam_str', 
    'nava_navamsa_str', 'ashtotharamsa_str', 'dwadas_dwadasamsa_str']
_custom_varga_factor = const.DEFAULT_CUSTOM_VARGA_FACTOR
def get_varga_option_dict():
    """ dict: {dcf:(method_count,method_index,base_rasi_index,count_from_end_of_sign)}"""
    _varga_option_dict = {}; _res = utils.resource_strings
    _varga_option_dict[1] = (None,None)
    for dcf in const.division_chart_factors[1:]:
        _opt_count = len([k for k in _res.keys() if 'd'+str(dcf)+'_option' in k ])
        _varga_option_dict[dcf] = (_opt_count,1)
    return _varga_option_dict
class MixedChartOptionsDialog(QDialog):
    """
        Varga Chart Options Dialog
        @param chart_index 1 for Hora, 2 for drekkana. 
            set chart_index=None if you custom divisional chart and set varga_factor to custom value
        @param varga_factor: None for standard charts and 1..300 for custom chart
        @param chart_method: chart method index (depending number of options available in each chart type)
        @param base_rasi: None for standard charts and custom cyclic charts. 
                For Non-cyclic custom charts - 0 for Aries and 1 for sign itself
        @param count_from_end_of_sign: None standard charts. Trur/False for custom charts 
        @return: 
                _option_string
                _method_index
                _varga_factor
                _base_rasi_index
                _count_from_end_of_sign
    """
    def __init__(self, chart_index_1=1,chart_method_1=1,chart_index_2=1,chart_method_2=1):
        super().__init__()
        self._varga_option_dict = get_varga_option_dict()
        self.res = utils.resource_strings
        self._chart_index_1 = chart_index_1
        self._varga_factor_1 = const.division_chart_factors[chart_index_1]
        self._method_count_1 = self._varga_option_dict[self._varga_factor_1][0]
        self._method_index_1 = chart_method_1
        self._chart_index_2 = chart_index_2
        self._varga_factor_2 = const.division_chart_factors[chart_index_2]
        self._method_count_2 = self._varga_option_dict[self._varga_factor_2][0]
        self._method_index_2 = chart_method_2
        self._option_string_1 = ''; self._option_string_2 = ''
        self.create_ui()
    def create_ui(self):
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        self._label_1= QLabel(self.res['varga_option_str']+'<br>'+self.res[_chart_names[self._chart_index_1]])
        h_layout.addWidget(self._label_1)
        self._varga_combo_1 = QComboBox()
        _dvf_list = [self.res[c] for c in _chart_names]
        self._varga_combo_1.addItems(_dvf_list)
        self._varga_combo_1.setCurrentIndex(self._chart_index_1)
        self._varga_combo_1.currentIndexChanged.connect(self._vargo_combo_1_changed)
        h_layout.addWidget(self._varga_combo_1)
        v_layout.addLayout(h_layout)
        label = QLabel(self.res['mixed_varga_str1'])
        v_layout.addWidget(label)
        self._radGroup1 = QButtonGroup(self)
        self._method_rbs_1 = [QRadioButton('') for _ in range(1,self._method_count_1+1)]
        for mc in range(1,self._method_count_1+1):
            self._method_rbs_1[mc-1].setText(self.res['d'+str(self._varga_factor_1)+'_option'+str(mc)+'_str'])
            if self._method_index_1==mc: self._method_rbs_1[mc-1].setChecked(True)
            self._radGroup1.addButton(self._method_rbs_1[mc-1])
            v_layout.addWidget(self._method_rbs_1[mc-1])
        # Create a horizontal separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        v_layout.addWidget(separator)
        label = QLabel(self.res['mixed_varga_str2'])
        v_layout.addWidget(label)
        h_layout = QHBoxLayout()
        self._label_2= QLabel(self.res['varga_option_str']+'<br>'+self.res[_chart_names[self._chart_index_2]])
        h_layout.addWidget(self._label_2)
        self._varga_combo_2 = QComboBox()
        self._varga_combo_2.addItems(_dvf_list)
        self._varga_combo_2.setCurrentIndex(self._chart_index_2)
        self._varga_combo_2.currentIndexChanged.connect(self._vargo_combo_2_changed)
        h_layout.addWidget(self._varga_combo_2)
        v_layout.addLayout(h_layout)
        self._radGroup2 = QButtonGroup(self)
        self._method_rbs_2 = [QRadioButton('') for _ in range(1,self._method_count_2+1)]
        for mc in range(1,self._method_count_2+1):
            self._method_rbs_2[mc-1].setText(self.res['d'+str(self._varga_factor_2)+'_option'+str(mc)+'_str'])
            if self._method_index_2==mc: self._method_rbs_2[mc-1].setChecked(True)
            self._radGroup2.addButton(self._method_rbs_2[mc-1])
            v_layout.addWidget(self._method_rbs_2[mc-1])

        h_layout = QHBoxLayout()
        self._accept_button = QPushButton(self.res['accept_str'])
        self._accept_button.setFlat(False)
        self._accept_button.clicked.connect(self._accept_button_clicked)
        h_layout.addWidget(self._accept_button)
        self._cancel_button = QPushButton(self.res['cancel_str'])
        self._cancel_button.setFlat(False)
        self._cancel_button.clicked.connect(self._cancel_button_clicked)
        h_layout.addWidget(self._cancel_button)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        self.setWindowTitle(self.res['mixed_varga_kundali_str']+' '+self.res['options_str'])
    def _vargo_combo_1_changed(self):
        self._chart_index_1 = self._varga_combo_1.currentIndex()
        self._varga_factor_1 = const.division_chart_factors[self._chart_index_1]
        self._method_count_1 = self._varga_option_dict[self._varga_factor_1][0]
        self._label_1.setText(self.res['varga_option_str']+'<br>'+self.res[_chart_names[self._chart_index_1]])
        self._method_index_1 = self._varga_option_dict[self._varga_factor_1][1]
        if self._varga_factor_1==1:
            self._method_count_1 = None; self._method_index_1 = None
            for rb in self._radGroup1.buttons():
                rb.setVisible(False)
            self.adjustSize()
            return
        for mc in range(1,self._method_count_1+1):
            self._method_rbs_1[mc-1].setVisible(True)
            self._method_rbs_1[mc-1].setText(self.res['d'+str(self._varga_factor_1)+'_option'+str(mc)+'_str'])
            if self._method_index_1==mc: self._method_rbs_1[mc-1].setChecked(True)
        self.adjustSize()
    def _vargo_combo_2_changed(self):
        self._chart_index_2 = self._varga_combo_2.currentIndex()
        self._varga_factor_2 = const.division_chart_factors[self._chart_index_2]
        self._method_count_2 = self._varga_option_dict[self._varga_factor_2][0]
        self._label_2.setText(self.res['varga_option_str']+'<br>'+self.res[_chart_names[self._chart_index_2]])
        self._method_index_1 = self._varga_option_dict[self._varga_factor_1][1]
        if self._varga_factor_2==1:
            self._method_count_2 = None; self._method_index_2 = None
            for rb in self._radGroup2.buttons():
                rb.setVisible(False)
            self.adjustSize()
            return
        for mc in range(1,self._method_count_2+1):
            self._method_rbs_2[mc-1].setVisible(True)
            self._method_rbs_2[mc-1].setText(self.res['d'+str(self._varga_factor_2)+'_option'+str(mc)+'_str'])
            if self._method_index_2==mc: self._method_rbs_2[mc-1].setChecked(True)
        self.adjustSize()
        
    def _accept_button_clicked(self):
        self._accept_clicked = True
        if self._method_count_1==None:
            self._option_string_1 = ''
        else:
            for mc in range(1,self._method_count_1+1):
                rb = self._method_rbs_1[mc-1]
                if rb.isChecked():
                    self._option_string_1 = rb.text()
                    self._method_index_1 = mc
        if self._method_count_2==None:
            self._option_string_2 = ''
        else:
            for mc in range(1,self._method_count_2+1):
                rb = self._method_rbs_2[mc-1]
                if rb.isChecked():
                    self._option_string_2 = rb.text()
                    self._method_index_2 = mc
        #print(self._varga_factor_1,self._method_index_1,self._option_string_1)
        #print(self._varga_factor_2,self._method_index_2,self._option_string_2)
        #self.get_mixed_chart()
        self.accept()
    def _cancel_button_clicked(self):
        self._accept_clicked = False
        self._option_string_1 = self.res['d'+str(self._varga_factor_1)+'_option'+str(self._method_index_1)+'_str']
        self._option_string_2 = self.res['d'+str(self._varga_factor_2)+'_option'+str(self._method_index_2)+'_str']
        self.reject()
    def get_mixed_chart(self):
        from jhora.horoscope.chart import charts
        from jhora.panchanga import drik
        dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,IN',13.0389, 80.2619, +5.5)
        jd = utils.julian_day_number(dob, tob)
        pp = charts.mixed_chart(jd, place, self._varga_factor_1, self._method_index_1, self._varga_factor_2, self._method_index_2)
        mixed_dvf = 'D'+str(self._varga_factor_1)+'xD'+str(self._varga_factor_2)
        print(mixed_dvf,utils.get_house_planet_list_from_planet_positions(pp))
if __name__ == "__main__":
    import sys
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = MixedChartOptionsDialog(chart_index_1=8,chart_method_1=1,chart_index_2=12,chart_method_2=1)
    chart.show()
    sys.exit(App.exec())
