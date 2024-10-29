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
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QRadioButton,QDialog, QHBoxLayout, QPushButton
from jhora import utils, const
_chart_names = ['raasi_str', 'hora_str', 'drekkanam_str', 'chaturthamsa_str', 'panchamsa_str', 
    'shashthamsa_str', 'saptamsam_str', 'ashtamsa_str', 'navamsam_str', 'dhasamsam_str', 'rudramsa_str', 
    'dhwadamsam_str', 'shodamsa_str', 'vimsamsa_str', 'chaturvimsamsa_str', 'nakshatramsa_str', 'thrisamsam_str', 
    'khavedamsa_str', 'akshavedamsa_str', 'sashtiamsam_str', 
    'nava_navamsa_str', 'ashtotharamsa_str', 'dwadas_dwadasamsa_str']
#_varga_option_dict = const.varga_option_dict
def get_varga_option_dict():
    _varga_option_dict = {}; _res = utils.resource_strings
    for dcf in const.division_chart_factors[1:]:
        _opt_count = len([k for k in _res.keys() if 'd'+str(dcf)+'_option' in k ])
        _varga_option_dict[dcf] = (_opt_count,1)
    return _varga_option_dict
class VargaChartOptionsDialog(QDialog):
    """
        Varga Chart Options Dialog
    """
    def __init__(self, planet_positions_in_rasi,varga_factor,method_index=1):
        super().__init__()
        _varga_option_dict = get_varga_option_dict()
        self.res = utils.resource_strings
        self._planet_positions_in_rasi = planet_positions_in_rasi
        self._varga_factor = varga_factor
        self._varga_planet_positions=[]
        self._method_index = method_index#_varga_option_dict[self._varga_factor][1]
        self._method_count = _varga_option_dict[self._varga_factor][0]
        self._option_string = ''
        self.create_ui()
    def create_ui(self):
        v_layout = QVBoxLayout()
        varga_chart_index = const.division_chart_factors.index(self._varga_factor)
        _label = QLabel(self.res['varga_option_str']+' '+self.res[_chart_names[varga_chart_index]])
        v_layout.addWidget(_label)
        self._method_rbs = []
        for mc in range(self._method_count):
            rb_caption = self.res['d'+str(self._varga_factor)+'_option'+str(mc+1)+'_str']
            self._method_rbs.append(QRadioButton(rb_caption))
            if self._method_index==(mc+1): self._method_rbs[mc].setChecked(True)
            v_layout.addWidget(self._method_rbs[mc])
        self._option_string = self.res['d'+str(self._varga_factor)+'_option'+str(self._method_index)+'_str']
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
    def _accept_button_clicked(self):
        self._accept_clicked = True
        for mc,rb in enumerate(self._method_rbs):
            if rb.isChecked():
                self._option_string = rb.text()
                self._method_index = mc+1
        self.accept()
    def _cancel_button_clicked(self):
        self._accept_clicked = False
        self._option_string = self.res['d'+str(self._varga_factor)+'_option'+str(self._method_index)+'_str']
        self.reject()
    
if __name__ == "__main__":
    import sys
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = VargaChartOptionsDialog([],9)
    chart.show()
    sys.exit(App.exec())
