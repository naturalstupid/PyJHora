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
    'nava_navamsa_str', 'ashtotharamsa_str', 'dwadas_dwadasamsa_str','custom_varga_kundali_str']
_custom_varga_factor = const.DEFAULT_CUSTOM_VARGA_FACTOR
class VargaChartOptionsDialog(QDialog):
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
    def __init__(self, chart_index=None,chart_method=0,varga_factor=None,base_rasi=None,count_from_end_of_sign=None):
        super().__init__()
        _varga_option_dict = utils.get_varga_option_dict()
        self._custom_chart_index = len(_chart_names)-1
        self.res = utils.resource_strings
        self._base_rasi_index = base_rasi
        if varga_factor==None and (chart_index==None or chart_index < self._custom_chart_index):
            self._varga_factor = const.division_chart_factors[chart_index]
            self._method_count = _varga_option_dict[self._varga_factor][0]
        elif varga_factor  is not None:
            if varga_factor in const.division_chart_factors:
                self._varga_factor = varga_factor
                self._method_count = _varga_option_dict[self._varga_factor][0]
            else:
                self._varga_factor = varga_factor
                self._method_count = _varga_option_dict[self._varga_factor][0]
        else:
            self._varga_factor = -1
            self._method_count = _varga_option_dict[_custom_varga_factor][0]
        #print(_varga_option_dict[self._varga_factor])
        self._count_from_end_of_sign = count_from_end_of_sign
        self._method_index = chart_method#_varga_option_dict[self._varga_factor][1]
        self._option_string = ''
        self.create_ui()
    def create_ui(self):
        v_layout = QVBoxLayout()
        self._method_rbs = [QRadioButton('') for _ in range(self._method_count)]
        self._varga_option_label = QLabel('')
        radGroup = QButtonGroup(self)
        self._custom_cycle_option = QRadioButton(self.res['dn_custom_cyclic_str'])
        radGroup.addButton(self._custom_cycle_option)
        self._custom_non_cycle_option = QRadioButton(self.res['dn_custom_non_cyclic_str'])
        radGroup.addButton(self._custom_non_cycle_option)
        self._custom_base_combo = QComboBox()
        self._custom_base_combo.addItems(['Aries Always','The rasi itself'])
        self._base_label = QLabel('Select Base Rasi Option:')
        self._custom_count_from_end_of_sign_check = QCheckBox(self.res['dn_custom_count_from_end_of_sign_str'])
        if self._count_from_end_of_sign  is not None:
            self._custom_count_from_end_of_sign_check.setChecked(self._count_from_end_of_sign)
        if self._varga_factor not in const.division_chart_factors:
            h_layout = QHBoxLayout()
            _cust_label = QLabel(self.res['dn_custom_varga_number_str'])
            h_layout.addWidget(_cust_label)
            self._custom_dvf_combo = QComboBox()#QSpinBox()
            _dvf_list = [str(d) for d in range(2,const.MAX_DHASAVARGA_FACTOR+1) if d not in const.division_chart_factors]
            if const.TREAT_STANDARD_CHART_AS_CUSTOM:
                _dvf_list = [str(d) for d in range(2,const.MAX_DHASAVARGA_FACTOR+1)]
            self._custom_dvf_combo.addItems(_dvf_list)#setRange(2,const.MAX_DHASAVARGA_FACTOR+1)
            #self._custom_dvf_combo.setSingleStep(1)
            if str(self._varga_factor) in _dvf_list:#range(2,const.MAX_DHASAVARGA_FACTOR+1):
                self._custom_dvf_combo.setCurrentText(str(self._varga_factor))
            else:
                self._custom_dvf_combo.setCurrentText(str(const.DEFAULT_CUSTOM_VARGA_FACTOR))
            h_layout.addWidget(self._custom_dvf_combo)
            v_layout.addLayout(h_layout)
            h_layout = QHBoxLayout()
            self._custom_cycle_option.toggled.connect(self._custom_cyclic_changed)
            self._custom_cycle_option.setChecked(self._method_index==0 and self._base_rasi_index==None)
            h_layout.addWidget(self._custom_cycle_option)
            self._custom_non_cycle_option.toggled.connect(self._custom_cyclic_changed)
            h_layout.addWidget(self._custom_non_cycle_option)
            v_layout.addLayout(h_layout)
            h_layout = QHBoxLayout()
            h_layout.addWidget(self._base_label)
            h_layout.addWidget(self._custom_base_combo)
            self._custom_base_combo.setCurrentIndex(0)
            if self._base_rasi_index  is not None: self._custom_base_combo.setCurrentIndex(self._base_rasi_index)
            v_layout.addLayout(h_layout)
        if self._varga_factor in const.division_chart_factors:
            varga_chart_index = const.division_chart_factors.index(self._varga_factor)
            self._varga_option_label.setText(self.res['varga_option_str']+' '+self.res[_chart_names[varga_chart_index]])
        else:
            self._varga_option_label.setText(self.res['varga_option_str']+' '+self.res[_chart_names[-1]])
        v_layout.addWidget(self._varga_option_label)
        for mc in range(self._method_count):
            if self._varga_factor in const.division_chart_factors:
                rb_caption = self.res['d'+str(self._varga_factor)+'_option'+str(mc+1)+'_str']
            else:
                rb_caption = self.res['dn_custom_option'+str(mc)+'_str']
            self._method_rbs[mc].setText(rb_caption) #.append(QRadioButton(rb_caption))
            if self._varga_factor in const.division_chart_factors and self._method_index==(mc+1): 
                self._method_rbs[mc].setChecked(True)
            if self._varga_factor not in const.division_chart_factors and self._method_index==(mc): 
                self._method_rbs[mc].setChecked(True)
            v_layout.addWidget(self._method_rbs[mc])
        self._option_string = rb_caption
        self._custom_non_cycle_option.setChecked(not self._custom_cycle_option.isChecked())
        self._custom_count_from_end_of_sign_check.setChecked(False)
        if self._count_from_end_of_sign==True: self._custom_count_from_end_of_sign_check.setChecked(True)
        if self._varga_factor not in const.division_chart_factors:
            # Create a horizontal separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            v_layout.addWidget(separator)
            v_layout.addWidget(self._custom_count_from_end_of_sign_check)
            #self._custom_count_from_end_of_sign_check.setEnabled(False)
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
        self.setWindowTitle(self.res['choose_varga_chart_method_str'])
    def _custom_cyclic_changed(self):
        if self._custom_cycle_option.isChecked():
            self._base_label.setVisible(False)
            self._custom_base_combo.setVisible(False)
            self._varga_option_label.setVisible(False)
            self._custom_count_from_end_of_sign_check.setVisible(False)
            for mc in range(self._method_count):
                self._method_rbs[mc].setVisible(False)
        else:
            self._base_label.setVisible(True)
            self._custom_base_combo.setVisible(True)
            self._varga_option_label.setVisible(True)
            self._custom_count_from_end_of_sign_check.setVisible(True)
            for mc in range(self._method_count):
                self._method_rbs[mc].setVisible(True)
        self.adjustSize()
    def _accept_button_clicked(self):
        self._accept_clicked = True
        for mc,rb in enumerate(self._method_rbs):
            if rb.isChecked():
                self._option_string = rb.text()
                self._method_index = mc+1
                if self._custom_cycle_option.isVisible() and self._custom_cycle_option.isChecked():
                    self._method_index = 0
                elif self._custom_non_cycle_option.isVisible() and self._custom_non_cycle_option.isChecked():
                    self._method_index = mc
        #self._base_rasi_index = None if not self._custom_base_combo.isVisible() else self._custom_base_combo.currentIndex()
        if not self._custom_base_combo.isVisible():
            self._base_rasi_index = None
            bstr = '<br>(Standard) base_rasi=None' if self._varga_factor in const.division_chart_factors else '<br>(Custom-Cyclic) base_rasi=None'
        else:
            self._base_rasi_index = self._custom_base_combo.currentIndex()
            bstr = '<br>Custom Non-Cyclic base_rasi='+ utils.RAASI_LIST[0] if self._base_rasi_index==0 else 'base is the sign'
        self._option_string += bstr# + str(self._base_rasi_index)
        cstr = ' count_from_end_of_sign='
        #self._count_from_end_of_sign = None if not self._custom_count_from_end_of_sign_check.isVisible() else self._custom_count_from_end_of_sign_check.isChecked()
        if not self._custom_count_from_end_of_sign_check.isVisible():
            self._count_from_end_of_sign = None
            cstr += 'None'
        else:
            self._count_from_end_of_sign = self._custom_count_from_end_of_sign_check.isChecked()
            cstr += str(self._count_from_end_of_sign)
        self._option_string += cstr# + str(self._count_from_end_of_sign)
        self._varga_factor = int(self._custom_dvf_combo.currentText()) if self._varga_factor not in const.division_chart_factors else None
        self.accept()
        """
        print('self._method_count',self._method_count,'self._method_index',self._method_index,
              'self._varga_factor',self._varga_factor,'self._option_string',self._option_string,
              '\nself._base_rasi_index',self._base_rasi_index,'self._count_from_end_of_sign',self._count_from_end_of_sign)
        """
    def _cancel_button_clicked(self):
        self._accept_clicked = False
        if self._varga_factor in const.division_chart_factors:
            rb_caption = self.res['d'+str(self._varga_factor)+'_option'+str(self._method_index)+'_str']
        else:
            rb_caption = self.res['dn_custom_option'+str(self._method_index)+'_str']
        self._option_string = rb_caption#self.res['d'+str(self._varga_factor)+'_option'+str(self._method_index)+'_str']
        self.reject()
    
if __name__ == "__main__":
    import sys
    utils.set_language('en')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    #chart = VargaChartOptionsDialog(chart_index=23,chart_method=None)
    #chart = VargaChartOptionsDialog(chart_index=23,chart_method=0)
    #chart = VargaChartOptionsDialog(chart_index=23,varga_factor=63,base_rasi=1,chart_method=5,count_from_end_of_sign=True)
    #chart = VargaChartOptionsDialog(varga_factor=57,chart_method=0,base_rasi=0,count_from_end_of_sign=True)
    chart = VargaChartOptionsDialog(varga_factor=9,chart_method=1)
    #chart = VargaChartOptionsDialog(chart_index=8,chart_method=3)
    chart.show()
    sys.exit(App.exec())
