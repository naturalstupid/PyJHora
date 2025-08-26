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
                            QComboBox, QDialog, QListWidget, QAbstractScrollArea, QToolTip, QButtonGroup, QRadioButton
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFontMetrics, QCursor
from jhora import utils
from jhora.panchanga import drik, vratha
import datetime
_main_window_width = 750
_main_window_height = 550
_CALCULATE_WAIT_MSG = '<b>Calculating... Results will be updated here. Please wait...</b>'
class VrathaFinderDialog(QDialog):
    """
        Search Vratha Dialog
    """
    def __init__(self,current_date_jd,place:drik.Place,chart_title=''):
        super().__init__()
        self._current_date_jd = current_date_jd
        self._selection_date_jd = current_date_jd
        self.Place = place
        self._accept_clicked = False
        self.res = utils.resource_strings
        self._chart_title = self.res['search_festival_str'] if chart_title=='' else chart_title
        self._vratha_result_dates = []
        self._tithi_list = [self.res['tithi_str']]+ [utils.PAKSHA_LIST[0]+'-'+t for t in utils.TITHI_LIST[0:14]]+ \
                      [utils.TITHI_LIST[14]]+[utils.PAKSHA_LIST[1]+'-'+t for t in utils.TITHI_LIST[0:14]]+ \
                                   [utils.TITHI_LIST[29]]
        self._nakshathra_list = [self.res['nakshatra_str']]+utils.NAKSHATRA_LIST
        self._yogam_list = [self.res['yogam_str']]+utils.YOGAM_LIST
        self._tm_list = [self.res['tamil_month_str']]+utils.MONTH_LIST
        self._create_ui()
    def _create_ui(self):
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        self._special_combo = QComboBox()
        self._special_combo.addItems([self.res[k+'_str'] for k in list(vratha.special_vratha_map.keys())+['customized']])
        self._special_combo.currentIndexChanged.connect(self._enable_combos)
        # Calculate the required width for the longest item
        font_metrics = QFontMetrics(self._special_combo.font())
        max_width = max(font_metrics.horizontalAdvance(self._special_combo.itemText(i)) for i in range(self._special_combo.count()))
        # Set the minimum width of the combo box to fit the longest item
        self._special_combo.setMinimumWidth(max_width + 50)  # Add some padding
        h_layout.addWidget(self._special_combo)
        self._from_date_label = QLabel(self.res['starts_at_str']); h_layout.addWidget(self._from_date_label)
        y,m,d,_ = utils.jd_to_gregorian(self._current_date_jd)
        self._from_date_text = QLineEdit(str(y)+','+str(m)+','+str(d));h_layout.addWidget(self._from_date_text)
        self._to_date_label = QLabel(self.res['ends_at_str']); h_layout.addWidget(self._to_date_label)
        y,m,d,_ = utils.jd_to_gregorian(self._current_date_jd+365)
        self._to_date_text = QLineEdit(str(y)+','+str(m)+','+str(d));h_layout.addWidget(self._to_date_text)
        v_layout.addLayout(h_layout)
        h_layout = QHBoxLayout()
        self._search_group = QButtonGroup()
        btn = QRadioButton(self.res['show_all_festivals_str'])
        self._search_group.addButton(btn, 0)
        self._search_group.button(0).setChecked(True)
        h_layout.addWidget(btn)
        btn = QRadioButton(self.res['search_festival_by_combination_str'])
        self._search_group.addButton(btn, 1)
        h_layout.addWidget(btn)
        btn = QRadioButton(self.res['search_festival_str'])
        self._search_group.addButton(btn, 2)
        h_layout.addWidget(btn)
        self._search_group.buttonClicked.connect(self._enable_combos)
        self._search_festival_edit = QLineEdit()
        h_layout.addWidget(self._search_festival_edit)
        v_layout.addLayout(h_layout)
        h_layout = QHBoxLayout()
        self._tithi_combo = QComboBox()
        self._tithi_combo.addItems(self._tithi_list)
        h_layout.addWidget(self._tithi_combo)
        self._nakshatra_combo = QComboBox()
        self._nakshatra_combo.addItems(self._nakshathra_list)
        h_layout.addWidget(self._nakshatra_combo)
        self._yogam_combo = QComboBox()
        self._yogam_combo.addItems(self._yogam_list)
        h_layout.addWidget(self._yogam_combo)
        self._tm_combo = QComboBox()
        self._tm_combo.addItems(self._tm_list)
        h_layout.addWidget(self._tm_combo)
        v_layout.addLayout(h_layout)
        self._search_group.button(0).setVisible(False)
        self._search_group.button(1).setVisible(False)
        self._search_group.button(2).setVisible(False)
        self._tithi_combo.setVisible(False); self._nakshatra_combo.setVisible(False)
        self._yogam_combo.setVisible(False); self._tm_combo.setVisible(False)
        self._tithi_combo.setEnabled(False); self._nakshatra_combo.setEnabled(False)
        self._yogam_combo.setEnabled(False); self._tm_combo.setEnabled(False)
        self._tithi_combo.currentIndexChanged.connect(self._enable_combos)
        self._nakshatra_combo.currentIndexChanged.connect(self._enable_combos)
        self._yogam_combo.currentIndexChanged.connect(self._enable_combos)
        self._tm_combo.currentIndexChanged.connect(self._enable_combos)
        self._results_list = QListWidget()
        #self._results_list.setEnabled(False)
        self._results_list.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        v_layout.addWidget(self._results_list)
        self._stats_label = QLabel('')
        v_layout.addWidget(self._stats_label)
        h_layout = QHBoxLayout()
        self._find_button = QPushButton(self.res['compute_str']); h_layout.addWidget(self._find_button)
        self._find_button.clicked.connect(self._calculate_clicked_1)
        self._accept_button = QPushButton(self.res['accept_str']); h_layout.addWidget(self._accept_button)
        self._accept_button.clicked.connect(self._accept_and_close)
        self._close_button = QPushButton(self.res['cancel_str']); h_layout.addWidget(self._close_button)
        self._close_button.clicked.connect(self._close_dialog)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        self.setMinimumSize(_main_window_width,_main_window_height)
        self.setWindowTitle(self._chart_title)
        self._accept_button.setEnabled(False)
        self._calculate_clicked_1()
    def closeEvent(self, *args, **kwargs):
        self._selection_date_jd = self._current_date_jd
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)
    def _enable_combos(self):
        _width = self._special_combo.minimumSizeHint().width()
        self._special_combo.view().setMinimumWidth(_width+100)
        vrata_index = self._special_combo.currentIndex()
        self._results_list.clear();self._accept_button.setEnabled(False)
        self._stats_label.setText('')
        self._search_festival_edit.setVisible(self._search_group.checkedId()==2)
        self._search_festival_edit.setEnabled(self._search_group.checkedId()==2)
        if vrata_index == len(vratha.special_vratha_map.keys()):#vratha_type in ['tithi','nakshatra','yogam']:
            self._search_group.button(0).setVisible(True)
            self._search_group.button(1).setVisible(True)
            self._search_group.button(2).setVisible(True)
            if self._search_group.checkedId()==1:
                self._tithi_combo.setVisible(True); self._nakshatra_combo.setVisible(True)
                self._yogam_combo.setVisible(True); self._tm_combo.setVisible(True)
                self._tithi_combo.setEnabled(True); self._nakshatra_combo.setEnabled(True)
                self._yogam_combo.setEnabled(True); self._tm_combo.setEnabled(True)
            else:
                self._tithi_combo.setVisible(False); self._nakshatra_combo.setVisible(False)
                self._yogam_combo.setVisible(False); self._tm_combo.setVisible(False)
                self._tithi_combo.setEnabled(False); self._nakshatra_combo.setEnabled(False)
                self._yogam_combo.setEnabled(False); self._tm_combo.setEnabled(False)
        else:
            self._search_group.button(0).setVisible(False)
            self._search_group.button(1).setVisible(False)
            self._search_group.button(2).setVisible(False)
            self._tithi_combo.setVisible(False); self._nakshatra_combo.setVisible(False)
            self._yogam_combo.setVisible(False); self._tm_combo.setVisible(False)
            self._tithi_combo.setEnabled(False); self._nakshatra_combo.setEnabled(False)
            self._yogam_combo.setEnabled(False); self._tm_combo.setEnabled(False)
        self._stats_label.setText('')
    def _calculate_clicked_1(self):
        QToolTip.showText(self._accept_button.mapToGlobal(self._accept_button.rect().bottomLeft()), 
                          self.res['please_wait_calculations_done_str'])
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QTimer.singleShot(100,self._calculate_clicked)
    def _calculate_clicked(self):
        self._accept_button.setEnabled(False)
        _start_date = self._from_date_text.text().split(','); _start_date=drik.Date(int(_start_date[0]),int(_start_date[1]),int(_start_date[2]))
        _end_date = self._to_date_text.text().split(','); _end_date=drik.Date(int(_end_date[0]),int(_end_date[1]),int(_end_date[2]))
        vrata_index = self._special_combo.currentIndex()
        vdates = []
        if vrata_index == len(vratha.special_vratha_map.keys()):
            festival_selected = None if self._search_group.checkedId() !=2 else self._search_festival_edit.text()
            _tithi_index = None if self._search_group.checkedId() in [0,2] or self._tithi_combo.currentIndex()==0 else self._tithi_combo.currentIndex()
            _nakshatra_index = None if self._search_group.checkedId() in [0,2] or self._nakshatra_combo.currentIndex()==0 else self._nakshatra_combo.currentIndex()
            _yogam_index = None if self._search_group.checkedId() in [0,2] or self._yogam_combo.currentIndex()==0 else self._yogam_combo.currentIndex()
            _tm_index = None if self._search_group.checkedId() in [0,2] or self._tm_combo.currentIndex()==0 else self._tm_combo.currentIndex()
            #print(_tithi_index,_nakshatra_index,_yogam_index,_tm_index,festival_selected)
            vdates = vratha.search(self.Place,_start_date, _end_date, _tithi_index, _nakshatra_index, 
                                   _yogam_index, _tm_index,festival_name_contains=festival_selected)
        else:
            vratha_type = list(vratha.special_vratha_map.keys())[vrata_index]
            vdates = vratha.special_vratha_dates(self.Place, _start_date, _end_date, vratha_type)
        if vdates is not None and len(vdates)>0:
            unique_first_items = len(set(item[0] for item in vdates))
            self._stats_label.setText(str(unique_first_items)+' '+self.res['matching_dates_found_str'])
            self._vratha_result_dates = vdates
            self._results_list.clear()
            for values in vdates:
                res = ''
                res += '-'.join(map(str,values[0]))
                if len(values)>1 and values[1]!='' : res += ' / '+str(utils.to_dms(values[1]))
                if len(values)>2: res += ' / '+str(values[-1])
                self._results_list.addItem(res)
            self._results_list.setCurrentRow(0)
            self._accept_button.setEnabled(True)
        else:
            self._stats_label.setText(self.res['no_matching_dates_found_str'])
            self._results_list.clear()
        QApplication.restoreOverrideCursor()
    def _accept_and_close(self):
        selected_date_index = self._results_list.currentRow()
        #print('selected date index',selected_date_index)
        if selected_date_index !=-1:
            selected_item = self._vratha_result_dates[selected_date_index]
            #print('selected vdate',selected_item)
            selected_date = self._vratha_result_dates[selected_date_index][0]
            selected_time = self._vratha_result_dates[selected_date_index][1]
            self._selection_date_jd = utils.julian_day_number(selected_date, (0,0,0))
            #selected_time = drik.sunrise(self._selection_date_jd, self.Place)[0]
            self._selection_date_jd = utils.julian_day_number(selected_date, (selected_time,0,0))
            #print('select JD',self._selection_date_jd,selected_date,utils.to_dms(selected_time))
            y,m,d,fh = utils.jd_to_gregorian(self._selection_date_jd)
            #print(y,m,d,utils.to_dms(fh))
        self._accept_clicked = True
        self.accept()
    def _close_dialog(self):
        self._accept_clicked = False
        self.reject()
def show(current_date_jd,place:drik.Place,chart_title=''):
    import sys
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    dlg = VrathaFinderDialog(current_date_jd,place,chart_title)
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
    jd = utils.julian_day_number((2025,1,1), (8,34,0))
    place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    entry_type = 0
    show(jd, place)
    exit()
    chart = VrathaFinderDialog(jd,place)
    chart.show()
    sys.exit(App.exec())

