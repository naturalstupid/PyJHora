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
                            QComboBox, QDialog
from PyQt6.QtCore import Qt
from jhora import utils, const
from jhora.panchanga import drik
import datetime
_main_window_width = 550
_main_window_height = 150
_CALCULATE_WAIT_MSG = '<b>Calculating... Results will be updated here. Please wait...</b>'
class ConjunctionDialog(QDialog):
    """
        Planetary Conjunction Dialog
    """
    def __init__(self,current_date_jd,place:drik.Place,planet1=6, chart_title='Planetary Conjunctions',
                 entry_type=0,planet2=4,raasi=None):
        """
            Entry Type: 0=> Planetary Conjunctions; 1=> Planet Entry/Transit 2=> Planet Vakra Gathi Change
        """
        super().__init__()
        self._current_date_jd = current_date_jd
        self._conjunction_date_jd = current_date_jd
        self.Place = place
        self._planet1 = planet1
        self._chart_title = chart_title
        self._entry_type = entry_type
        self._accept_clicked = False
        self._separation_angle_index = 0
        if entry_type==0:
            self._planet2 = planet2
        elif entry_type==1:
            self._raasi = raasi
        self.res = utils.resource_strings
        self._create_ui()
    def _create_ui(self):
        v_layout = QVBoxLayout()
        self._current_date_label = QLabel(self.res['current_date_str'])
        cy,cm,cd,cfh = utils.jd_to_gregorian(self._current_date_jd)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self._current_date_label)
        hh,mm,ss = utils.to_dms(cfh,as_string=False)
        self._dob_text = QLineEdit(str(cy)+','+str(cm)+','+str(cd))
        self._dob_text.setToolTip('Date in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        h_layout.addWidget(self._dob_text)
        self._tob_label = QLabel(self.res['time_of_birth_str'])
        h_layout.addWidget(self._tob_label)
        hh,mm,ss = utils.to_dms(cfh,as_string=False)
        self._tob_text = QLineEdit(str(hh)+':'+str(mm)+':'+str(ss))
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        h_layout.addWidget(self._tob_text)
        self._after_before_combo = QComboBox(); h_layout.addWidget(self._after_before_combo)
        self._after_before_combo.addItems([self.res['next_str'],self.res['previous_str']])
        v_layout.addLayout(h_layout)
        h_layout = QHBoxLayout()
        if self._entry_type==0:
            self._sep_angle_combo = QComboBox()
            self._sep_angle_list = self.res['planet_separation_angle_list'].split(',')
            self._sep_angle_combo.addItems(self._sep_angle_list)
            self._sep_angle_combo.setCurrentIndex(0)
            self._separation_angle = self._sep_angle_combo.currentIndex()*30.
            h_layout.addWidget(self._sep_angle_combo)
        self._planet1_combo = QComboBox()
        if self._entry_type==2:
            self._planet1_list = utils.PLANET_NAMES[2:7]
        else:
            self._planet1_list = [self.res['ascendant_str']]+utils.PLANET_NAMES[:9]
        self._planet1_combo.addItems(self._planet1_list)
        self._planet1_combo.setCurrentIndex(0)
        if self._planet1==const._ascendant_symbol or utils.PLANET_NAMES[self._planet1] in self._planet1_list:
            self._planet1_combo.setCurrentText(utils.PLANET_NAMES[self._planet1])
        h_layout.addWidget(self._planet1_combo)
        if self._entry_type==0:
            self._planet2_combo = QComboBox()
            self._planet1_combo.currentIndexChanged.connect(self._update_planet2_list)
            self._update_planet2_list()
            h_layout.addWidget(self._planet2_combo)
        elif self._entry_type==1:
            self._raasi_combo = QComboBox()
            self._raasi_combo.addItems([self.res['raasi_str']]+utils.RAASI_LIST)
            h_layout.addWidget(self._raasi_combo)
        v_layout.addLayout(h_layout)
        self._results_text = QLabel(self._after_before_combo.currentText()+'occurs at:')
        self._results_text.setEnabled(False)
        v_layout.addWidget(self._results_text)
        h_layout = QHBoxLayout()
        self._find_button = QPushButton(self.res['compute_str']); h_layout.addWidget(self._find_button)
        self._find_button.clicked.connect(self._calculate_clicked)
        self._accept_button = QPushButton(self.res['accept_str']); h_layout.addWidget(self._accept_button)
        self._accept_button.clicked.connect(self._accept_and_close)
        self._close_button = QPushButton(self.res['cancel_str']); h_layout.addWidget(self._close_button)
        self._close_button.clicked.connect(self._close_dialog)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        self.setFixedSize(_main_window_width,_main_window_height)
        self.setWindowTitle(self._chart_title)
        self._results_text.setText('')
        self._accept_button.setEnabled(False)
        #self._calculate_clicked()
    def closeEvent(self, *args, **kwargs):
        self._conjunction_date_jd = self._current_date_jd
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)
    def _update_planet2_list(self):
        self._planet2_combo.clear()
        _planet2_list = [self.res['ascendant_str']]+ utils.PLANET_NAMES[:9]
        _planet2_list.remove(self._planet1_combo.currentText())
        if self._planet1_combo.currentIndex()==8 or self._planet1_combo.currentIndex()==9:
            _planet2_list = _planet2_list[:7]
        self._planet2_combo.addItems(_planet2_list)
        self._planet2_combo.setCurrentIndex(0)
        if utils.PLANET_NAMES[self._planet2] in _planet2_list:
            self._planet2_combo.setCurrentText(utils.PLANET_NAMES[self._planet2])
    def _calculate_clicked(self):
        self._accept_button.setEnabled(False)
        if self._entry_type==0:
            self.setWindowTitle(self.res['planetary_conjunctions_str'])
            self._find_conjunction_date()
        elif self._entry_type==1:
            self.setWindowTitle(self.res['planet_transit_str'])
            self._find_transit_date()
        else:
            self.setWindowTitle(self.res['vakra_gathi_change_str'])
            self._find_retrogression_change_date()
        self._accept_button.setEnabled(True)
    def _find_retrogression_change_date(self):
        from jhora import const
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        panchanga_place = self.Place
        #year = int(self._year_text.text()); month = int(self._month_text.text()); day=int(self._day_text.text())
        year,month,day = map(int,self._dob_text.text().split(","));# dob = (int(year),int(month),int(day))
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        panchanga_start_date = drik.Date(year,month,day+1*direction)
        cur_jd,ret_sign = drik.next_planet_retrograde_change_date(self._planet1,panchanga_start_date,panchanga_place,direction=direction)
        retStr=''  if ret_sign == 1 else const._retrogade_symbol
        self._conjunction_date_jd = cur_jd
        results = self._planet1_combo.currentText()+' '
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+utils.PLANET_NAMES[self._planet1]+retStr
        #print(results)
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._dob_text.setText(str(y)+','+str(m)+','+str(d));self._tob_text.setText(str(hh)+':'+str(mm)+':'+str(ss))
        QApplication.restoreOverrideCursor()        
        
    def _find_conjunction_date(self):
        #from datetime import datetime
        self._separation_angle = self._sep_angle_combo.currentIndex()*30.
        #start_time = datetime.now()
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = const._ascendant_symbol if self._planet1_combo.currentIndex()==0 else utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        self._planet2 = const._ascendant_symbol if self._planet2_combo.currentIndex()==0 else utils.PLANET_NAMES.index(self._planet2_combo.currentText())
        panchanga_place = self.Place
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        start_jd = self._current_date_jd + direction* (1/(24*60*60))
        ret = drik.next_conjunction_of_planet_pair(self._current_date_jd,panchanga_place, self._planet1, self._planet2, direction=direction,separation_angle=self._separation_angle)
        self._separation_angle_index = self._sep_angle_combo.currentIndex()
        if ret==None: #Error text fixec in V3.8.1
            self._results_text.setText('Could not find planetary conjunctions for sep angle '+str(self._separation_angle)+'  Try increasing search range')
            QApplication.restoreOverrideCursor()
            return
        else:
            cur_jd,p1_long,p2_long = ret
        #end_time = datetime.now()
        #print("Elapsed", (end_time - start_time).total_seconds(),'seconds')
        self._conjunction_date_jd = cur_jd; self._current_date_jd = cur_jd
        results = self._planet1_combo.currentText()+'/'+self._planet2_combo.currentText()+' '
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        pstr1 = self.res['ascendant_str'] if self._planet1 == const._ascendant_symbol else utils.PLANET_NAMES[self._planet1]
        pstr2 = self.res['ascendant_str'] if self._planet2 == const._ascendant_symbol else utils.PLANET_NAMES[self._planet2]
        results += ' '+self.res['longitude_str']+' '+\
                    pstr1+':'+utils.to_dms(p1_long,is_lat_long='plong')+' ' + \
                    pstr2+':'+utils.to_dms(p2_long,is_lat_long='plong')
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._dob_text.setText(str(y)+','+str(m)+','+str(d));self._tob_text.setText(str(hh)+':'+str(mm)+':'+str(ss))
        QApplication.restoreOverrideCursor()
        return
    def _find_transit_date(self):
        from datetime import datetime
        start_time = datetime.now()
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = const._ascendant_symbol if self._planet1_combo.currentIndex()==0 else utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        panchanga_place = self.Place
        #year = int(self._year_text.text()); month = int(self._month_text.text()); day=int(self._day_text.text())  
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        #panchanga_start_date = drik.Date(year,month,day)
        start_jd = self._current_date_jd + direction* (1/(24*60*60))
        #print(year,month,day,'panchanga_start_date',panchanga_start_date,utils.jd_to_gregorian(start_jd))
        self._raasi = None if self._raasi_combo.currentIndex()==0 else self._raasi_combo.currentIndex()
        cur_jd,p1_long = drik.next_planet_entry_date(self._planet1,start_jd,panchanga_place,
                                                     direction=direction,raasi=self._raasi)
        end_time = datetime.now()
        print("Elapsed", (end_time - start_time).total_seconds(),'seconds')
        self._conjunction_date_jd = cur_jd; self._current_date_jd = cur_jd
        results = self._planet1_combo.currentText()+' '
        #print(results)
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        p1_rasi,p1_long = drik.dasavarga_from_long(p1_long, divisional_chart_factor=1)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+self.res['longitude_str']+' :'+ utils.RAASI_LIST[p1_rasi]+' ' + utils.to_dms(p1_long,is_lat_long='plong')+' '
        #print(results)
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._dob_text.setText(str(y)+','+str(m)+','+str(d));self._tob_text.setText(str(hh)+':'+str(mm)+':'+str(ss))
        QApplication.restoreOverrideCursor()        
    def _accept_and_close(self):
        self._accept_clicked = True
        #y,m,d,fh = utils.jd_to_gregorian(self._conjunction_date_jd)
        #print(y,m,d,utils.to_dms(fh))
        self.accept()
    def _close_dialog(self):
        self._accept_clicked = False
        self.reject()
def show(current_date_jd,place:drik.Place,planet1=6,planet2=4, chart_title='Planetary Conjunctions',entry_type=0):
    import sys
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    dlg = ConjunctionDialog(current_date_jd,place,planet1,chart_title,entry_type,planet2)
    ret = dlg.exec()
    print('exec return value',ret)
    return ret
if __name__ == "__main__":
    import sys
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    lang = 'ta'; utils.set_language(lang)
    App = QApplication(sys.argv)
    jd = utils.julian_day_number((1996,12,7), (10,34,0))
    place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    _chart_title = 'Planet entry'
    entry_type = 2
    show(jd, place,entry_type=entry_type,chart_title=_chart_title)
    exit()
    chart = ConjunctionDialog(jd,place,entry_type=entry_type,planet1=const._ascendant_symbol)
    chart.show()
    sys.exit(App.exec())

