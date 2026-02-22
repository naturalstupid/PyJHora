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
from PyQt6.QtWidgets import (
    QLineEdit, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,
    QComboBox, QDialog, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from jhora import utils, const
from jhora.panchanga import drik
from jhora.panchanga import eclipse


solar_eclipse_types = {
    "any":     eclipse.SolarEclipseType.ANY,
    "total":   eclipse.SolarEclipseType.TOTAL,
    "partial": eclipse.SolarEclipseType.PARTIAL,
    "hybrid":  eclipse.SolarEclipseType.HYBRID,
    "annular": eclipse.SolarEclipseType.ANNULAR,
}
lunar_eclipse_types = {
    "any":     eclipse.LunarEclipseType.ANY,
    "total":   eclipse.LunarEclipseType.TOTAL,
    "partial": eclipse.LunarEclipseType.PARTIAL,
    "penumbral": eclipse.LunarEclipseType.PENUMBRAL,
}

_main_window_width = 550
_main_window_height = 150
_CALCULATE_WAIT_MSG = '<b>Calculating... Results will be updated here. Please wait...</b>'
class GeneralConjunctionDialog(QDialog):
    """
        Planetary Conjunction Dialog
    """
    def __init__(self,current_date_jd,place:drik.Place,planet1=const.SATURN_ID, chart_title='Planetary Conjunctions',
                 entry_type=0,planet2=const.JUPITER_ID,raasi=None,show_other_conjunction_options=False):
        """
            Entry Type: 0=> Planetary Conjunctions; 1=> Planet Entry/Transit 2=> Planet Vakra Gathi Change
                        3=> Eclipse
        """
        super().__init__()
        self.show_other_conjunction_options = show_other_conjunction_options
        self._current_date_jd = current_date_jd
        self._conjunction_date_jd = current_date_jd
        self.Place = place
        self._planet1 = planet1
        self._chart_title = chart_title
        self._entry_type = entry_type
        self._accept_clicked = False

        # Existing tracking
        self._separation_angle_index = 0
        if entry_type==0:
            self._planet2 = planet2
        elif entry_type==1:
            self._raasi = raasi

        # New: Remember last selections per mode (UI-only caches)
        self._last_p1 = {0: None, 1: None, 2: None}     # planet1 by mode
        self._last_p2 = None                             # planet2 for conjunction mode
        self._last_raasi_index = 0                       # raasi index for transit mode

        self.res = utils.resource_strings
        self._create_ui()

    def _create_ui(self):
        v_layout = QVBoxLayout()

        # -----------------------------
        # (0) Entry option row (NEW)
        # -----------------------------
        entry_row = QHBoxLayout()
        self._rb_conj = QRadioButton(self.res['planetary_conjunctions_str'])
        self._rb_transit = QRadioButton(self.res['planet_transit_str'])
        self._rb_vakra = QRadioButton(self.res['vakra_gathi_change_str'])
        self._rb_eclipse = QRadioButton(self.res['eclipse_str'])
        entry_row.addWidget(self._rb_conj)
        entry_row.addWidget(self._rb_transit)
        entry_row.addWidget(self._rb_vakra)
        entry_row.addWidget(self._rb_eclipse)
        entry_row.addStretch()

        self._entry_group = QButtonGroup(self)
        self._entry_group.addButton(self._rb_conj, 0)
        self._entry_group.addButton(self._rb_transit, 1)
        self._entry_group.addButton(self._rb_vakra, 2)
        self._entry_group.addButton(self._rb_eclipse, 3)

        # select initial based on self._entry_type
        if self._entry_type == 0:
            self._rb_conj.setChecked(True)
        elif self._entry_type == 1:
            self._rb_transit.setChecked(True)
        elif self._entry_type == 2:
            self._rb_vakra.setChecked(True)
        else:
            self._rb_eclipse.setChecked(True)

        self._entry_group.idClicked.connect(self._on_mode_changed)
        v_layout.addLayout(entry_row)
        for rb in self._entry_group.buttons():
            rb.setVisible(self.show_other_conjunction_options)
        # ------------------------------------
        # (1) Parameter row (FIRST after top)
        # ------------------------------------
        param_row = QHBoxLayout()
        # Conjunction-only UI
        self._sep_angle_combo = QComboBox()
        self._sep_angle_list = self.res['planet_separation_angle_list'].split(',')
        self._sep_angle_combo.addItems(self._sep_angle_list)
        self._sep_angle_combo.setCurrentIndex(0)
        self._separation_angle = self._sep_angle_combo.currentIndex()*30.
        param_row.addWidget(self._sep_angle_combo)
        # Common planet1 combo (contents depend on mode)
        self._planet1_combo = QComboBox()
        param_row.addWidget(self._planet1_combo)
        # Conjunction's planet2
        self._planet2_combo = QComboBox()
        param_row.addWidget(self._planet2_combo)
        # Transit-only raasi
        self._raasi_combo = QComboBox()
        param_row.addWidget(self._raasi_combo)
        # Connections that are safe even when hidden
        self._planet1_combo.currentIndexChanged.connect(self._update_planet2_list)
        self._eclipse_combo = QComboBox()
        self._eclipse_list = [self.res['solar_str']+' '+ self.res['eclipse_str'],
                                      self.res['lunar_str']+' '+self.res['eclipse_str']]
        self._eclipse_combo.addItems(self._eclipse_list)
        self._eclipse = 0 # Solar 1=>Linar
        param_row.addWidget(self._eclipse_combo)
        self._eclipse_type_combo = QComboBox()
        if self._eclipse_combo.currentIndex()==0:
            self._ect_dict = {self.res[k+'_str']:v for k,v in solar_eclipse_types.items()}
        else:
            self._ect_dict = {self.res[k+'_str']:v for k,v in lunar_eclipse_types.items()}
        for key,mask in self._ect_dict.items():
            self._eclipse_type_combo.addItem(key,mask)
        self._eclipse_type = 0 #Any, 1=total,2=partial,3=hybrid/penumbral
        param_row.addWidget(self._eclipse_type_combo)
        self._eclipse_loc_combo = QComboBox()
        self._eclipse_loc_combo.addItems([self.res['global_str'],self.res['local_str']])
        self._eclipse_loc = 0 # Global, 1=Local
        param_row.addWidget(self._eclipse_loc_combo)
        self._eclipse_combo.currentIndexChanged.connect(self._eclipse_item_changed)
            
        v_layout.addLayout(param_row)

        # ------------------------------------
        # (2) Date/Time row (UNCHANGED order)
        # ------------------------------------
        self._current_date_label = QLabel(self.res['current_date_str'])
        cy,cm,cd,cfh = utils.jd_to_gregorian(self._current_date_jd)
        hh,mm,ss = utils.to_dms(cfh,as_string=False)

        datetime_row = QHBoxLayout()
        datetime_row.addWidget(self._current_date_label)
        self._dob_text = QLineEdit(f"{cy},{cm},{cd}")
        self._dob_text.setToolTip('Date in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        datetime_row.addWidget(self._dob_text)

        self._tob_label = QLabel(self.res['time_of_birth_str'])
        datetime_row.addWidget(self._tob_label)
        self._tob_text = QLineEdit(f"{hh}:{mm}:{ss}")
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        datetime_row.addWidget(self._tob_text)

        self._after_before_combo = QComboBox(); datetime_row.addWidget(self._after_before_combo)
        self._after_before_combo.addItems([self.res['next_str'],self.res['previous_str']])

        v_layout.addLayout(datetime_row)

        # ------------------------------------
        # (3) Results label
        # ------------------------------------
        self._results_text = QLabel(self._after_before_combo.currentText()+'occurs at:')
        self._results_text.setEnabled(False)
        v_layout.addWidget(self._results_text)

        # ------------------------------------
        # (4) Buttons row
        # ------------------------------------
        buttons_row = QHBoxLayout()
        self._find_button = QPushButton(self.res['compute_str']); buttons_row.addWidget(self._find_button)
        self._find_button.clicked.connect(self._calculate_clicked)
        self._accept_button = QPushButton(self.res['accept_str']); buttons_row.addWidget(self._accept_button)
        self._accept_button.clicked.connect(self._accept_and_close)
        self._close_button = QPushButton(self.res['cancel_str']); buttons_row.addWidget(self._close_button)
        self._close_button.clicked.connect(self._close_dialog)
        v_layout.addLayout(buttons_row)

        self.setLayout(v_layout)

        # -----------------------------
        # SIZING: replace fixed size
        # -----------------------------
        # ORIGINAL (commented per your request):
        # self.setFixedSize(_main_window_width,_main_window_height)

        # NEW (auto-size to content, keep width reasonable, then fix to size hint)
        self.setMinimumWidth(_main_window_width)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

        # Window title and initial state
        self.setWindowTitle(self._chart_title)
        self._results_text.setText('')
        self._accept_button.setEnabled(False)

        # Populate controls and set initial visibility/selection for current mode
        self._apply_entry_type(self._entry_type, first_time=True)
    def _eclipse_item_changed(self):
        self._eclipse = self._eclipse_combo.currentIndex()
        self._eclipse_type = self._eclipse_type_combo.currentIndex()
        self._eclipse_loc = self._eclipse_loc_combo.currentIndex()
        if self._eclipse_combo.currentIndex()==0:
            self._ect_dict = {self.res[k+'_str']:v for k,v in solar_eclipse_types.items()}
        else:
            self._ect_dict = {self.res[k+'_str']:v for k,v in lunar_eclipse_types.items()}
        self._eclipse_type_combo.clear()
        for key,mask in self._ect_dict.items():
            self._eclipse_type_combo.addItem(key,mask)
        self._apply_entry_type(self._entry_type)
    def closeEvent(self, *args, **kwargs):
        self._conjunction_date_jd = self._current_date_jd
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)

    # -------------------------
    # NEW: mode switching glue
    # -------------------------
    def _on_mode_changed(self, entry_type: int):
        self._entry_type = self._entry_group.checkedId()
        # Remember current selections into caches before switching
        # planet1
        if self._planet1_combo.count() > 0:
            self._last_p1[self._entry_type] = self._planet1_combo.currentText()
        # planet2 (only meaningful in conjunction)
        if self._entry_type == 0 and self._planet2_combo.count() > 0:
            self._last_p2 = self._planet2_combo.currentText()
        # raasi (only meaningful in transit)
        if self._entry_type == 1 and self._raasi_combo.count() > 0:
            self._last_raasi_index = self._raasi_combo.currentIndex()
        # sep angle
        if self._sep_angle_combo.isVisible():
            self._separation_angle_index = self._sep_angle_combo.currentIndex()

        self._apply_entry_type(self._entry_type)
        # Clear results and wait for explicit compute, as requested
        self._results_text.setText('')
        self._accept_button.setEnabled(False)

    def _apply_entry_type(self, entry_type: int, first_time: bool=False):
        self._entry_type = entry_type
        self.setWindowTitle(self._entry_group.checkedButton().text())
        # ---------- Populate planet1 list based on mode ----------
        self._planet1_combo.blockSignals(True)
        self._planet1_combo.clear()
        if entry_type == 2:  # Vakra Gathi Change
            p1_list = utils.PLANET_NAMES[const.MARS_ID:const.SATURN_ID+1]
        else:
            p1_list = [self.res['ascendant_str']] + utils.PLANET_NAMES[:9]
        self._planet1_combo.addItems(p1_list)
        self._planet1_combo.blockSignals(False)

        # ---------- Conjunction-only planet2 handling ----------
        self._planet2_combo.clear()
        if entry_type == 0:
            pass

        # ---------- Transit-only raasi ----------
        self._raasi_combo.clear()
        if entry_type == 1:
            self._raasi_combo.addItems([self.res['raasi_str']] + utils.RAASI_LIST)

        # ---------- Restore selections or set from constructor on first_time ----------
        # planet1
        restored_p1 = False
        if self._last_p1.get(entry_type):
            txt = self._last_p1[entry_type]
            idx = self._planet1_combo.findText(txt)
            if idx >= 0:
                self._planet1_combo.setCurrentIndex(idx)
                restored_p1 = True

        if not restored_p1 and first_time:
            # Derive from constructor arguments
            try:
                if entry_type in (0,1):
                    # ascendant or named planet
                    if self._planet1 == const._ascendant_symbol:
                        self._planet1_combo.setCurrentText(self.res['ascendant_str'])
                    else:
                        ptxt = utils.PLANET_NAMES[self._planet1]
                        if ptxt in p1_list:
                            self._planet1_combo.setCurrentText(ptxt)
                else:
                    # vakra: only utils.PLANET_NAMES[2:7] allowed
                    ptxt = utils.PLANET_NAMES[self._planet1] if 0 <= self._planet1 < len(utils.PLANET_NAMES) else None
                    if ptxt in p1_list:
                        self._planet1_combo.setCurrentText(ptxt)
                    else:
                        self._planet1_combo.setCurrentIndex(0)
            except Exception:
                self._planet1_combo.setCurrentIndex(0)
        elif not restored_p1:
            # safe default
            self._planet1_combo.setCurrentIndex(0)

        # planet2 for conjunction
        if entry_type == 0:
            self._update_planet2_list()  # repopulate based on current planet1
            restored_p2 = False
            if self._last_p2:
                idx2 = self._planet2_combo.findText(self._last_p2)
                if idx2 >= 0:
                    self._planet2_combo.setCurrentIndex(idx2)
                    restored_p2 = True
            if not restored_p2 and first_time:
                try:
                    # From constructor if valid
                    p2txt = self.res['ascendant_str'] if getattr(const, '_ascendant_symbol', None) == self._planet2 else utils.PLANET_NAMES[self._planet2]
                    idx2 = self._planet2_combo.findText(p2txt)
                    if idx2 >= 0:
                        self._planet2_combo.setCurrentIndex(idx2)
                except Exception:
                    pass

        # raasi for transit
        if entry_type == 1:
            if first_time and self._raasi is not None:
                # _raasi is 1..12; index 0 in combo is the label
                idxr = int(self._raasi) if isinstance(self._raasi, int) else 0
                if 0 <= idxr <= len(utils.RAASI_LIST):
                    self._raasi_combo.setCurrentIndex(idxr)
                else:
                    self._raasi_combo.setCurrentIndex(0)
            else:
                self._raasi_combo.setCurrentIndex(self._last_raasi_index if self._last_raasi_index is not None else 0)

        # sep angle
        if entry_type == 0:
            self._sep_angle_combo.setCurrentIndex(self._separation_angle_index if self._separation_angle_index is not None else 0)
            self._separation_angle = self._sep_angle_combo.currentIndex() * 30.0

        # ---------- Visibility matrix ----------
        is_conj = (entry_type == 0)
        is_transit = (entry_type == 1)
        is_vakra = (entry_type == 2)
        is_eclipse = (entry_type ==3)

        self._planet1_combo.setVisible(not is_eclipse)
        self._sep_angle_combo.setVisible(is_conj)
        self._planet2_combo.setVisible(is_conj)
        self._raasi_combo.setVisible(is_transit)
        self._eclipse_combo.setVisible(is_eclipse)
        self._eclipse_loc_combo.setVisible(is_eclipse)
        self._eclipse_type_combo.setVisible(is_eclipse)
    # (UNCHANGED) your original helper
    def _update_planet2_list(self):
        self._planet2_combo.clear()
        _planet2_list = [self.res['ascendant_str']]+ utils.PLANET_NAMES[:9]
        _planet2_list.remove(self._planet1_combo.currentText())
        if self._planet1_combo.currentIndex()==8 or self._planet1_combo.currentIndex()==9:
            _planet2_list = _planet2_list[:7]
        self._planet2_combo.addItems(_planet2_list)
        self._planet2_combo.setCurrentIndex(0)
        if hasattr(self, "_planet2") and utils.PLANET_NAMES[self._planet2] in _planet2_list:
            self._planet2_combo.setCurrentText(utils.PLANET_NAMES[self._planet2])

    # (UNCHANGED) compute dispatch
    def _calculate_clicked(self):
        self._accept_button.setEnabled(False)
        if self._entry_type==0:
            self.setWindowTitle(self.res['planetary_conjunctions_str'])
            self._find_conjunction_date()
            print('conjunction',self._conjunction_date_jd)
        elif self._entry_type==1:
            self.setWindowTitle(self.res['planet_transit_str'])
            self._find_transit_date()
            print('transit',self._conjunction_date_jd)
        elif self._entry_type==2:
            self.setWindowTitle(self.res['vakra_gathi_change_str'])
            self._find_retrogression_change_date()
            print('vakra gathi',self._conjunction_date_jd)
        else:
            self.setWindowTitle(self.res['eclipse_str'])
            self._find_eclipse_date()
            print('eclipse',"solar" if self._eclipse==0 else "lunar",self._eclipse_type_str,self._conjunction_date_jd)
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
    def _find_eclipse_date(self):
        from datetime import datetime
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        place = self.Place
        y,m,d = map(int,self._dob_text.text().split(",")); dob=drik.Date(y,m,d)
        hh,mm,ss = map(int,self._tob_text.text().split(":")); tob=(hh,mm,ss)
        self._current_date_jd = utils.julian_day_number(dob,tob)
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        jd_local = self._current_date_jd + direction # Add one day
        _eclipse_location_type = eclipse.EclipseLocation.GLOBAL if self._eclipse_loc==0 else eclipse.EclipseLocation.LOCAL
        _search_backward = self._after_before_combo.currentIndex()==1 
        _eclipse_type = int(self._eclipse_type_combo.currentData())
        if self._eclipse==0:
            _ecl = eclipse.next_solar_eclipse(jd_local, place, _eclipse_location_type, _eclipse_type, _search_backward)
            _ecl1_str=utils.resource_strings['solar_str']+' '+ utils.resource_strings['eclipse_str']
        else:
            _ecl = eclipse.next_lunar_eclipse(jd_local, place, _eclipse_location_type, _eclipse_type, _search_backward)
            _ecl1_str=utils.resource_strings['lunar_str']+' '+ utils.resource_strings['eclipse_str']
        _ecl_jd_str = "[" + ",".join(f"({y},{m},{d},{int(h):02d}:{int(mi):02d}:{int(round(s)):02d})"
                                     for y,m,d,fh in _ecl[1] for h,mi,s in (utils.to_dms(fh, as_string=False),)) + "]"
        self._eclipse_type_str = _ecl[0]
        _ecl_results = (f"{utils.resource_strings[_ecl[0] + '_str']} "f"{_ecl1_str} "f"{_ecl_jd_str}")
        self._results_text.setText(_ecl_results)
        y,m,d,fh = _ecl[1][0]; hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._current_date_jd = utils.julian_day_number(drik.Date(y,m,d),(hh,mm,ss))
        self._dob_text.setText(f"{y},{m:02d},{d:02d}")
        self._tob_text.setText(f"{hh:02d}:{mm:02d}:{ss:02d}")
        self._conjunction_date_jd = self._current_date_jd
        QApplication.restoreOverrideCursor()        
    def _find_transit_date(self):
        #from datetime import datetime
        #start_time = datetime.now()
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
        #end_time = datetime.now()
        #print("Elapsed", (end_time - start_time).total_seconds(),'seconds')
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
def show(current_date_jd,place:drik.Place,planet1=6,planet2=4, chart_title='Planetary Conjunctions',entry_type=0,
         show_other_conjunction_options=False):
    import sys
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    dlg = GeneralConjunctionDialog(current_date_jd,place,planet1,chart_title,entry_type,planet2,
                                   show_other_conjunction_options=show_other_conjunction_options)
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
    _chart_title = 'Conjunctions'
    entry_type = 3
    show(jd, place,entry_type=entry_type,chart_title=_chart_title,show_other_conjunction_options=True)
    exit()

