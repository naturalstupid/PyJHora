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
from datetime import datetime
import importlib
from PyQt6.QtWidgets import (
    QLineEdit, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,
    QComboBox, QDialog, QRadioButton, QButtonGroup, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from jhora import utils, const
from jhora.panchanga import drik
from jhora.panchanga import eclipse
from enum import IntEnum, unique

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
dhasa_levels = {
    "maha": const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
    "antara": const.MAHA_DHASA_DEPTH.ANTARA,
    "prathyanthara": const.MAHA_DHASA_DEPTH.PRATYANTARA,
    "sookshma" : const.MAHA_DHASA_DEPTH.SOOKSHMA,
    "praana": const.MAHA_DHASA_DEPTH.PRANA,
    "deha": const.MAHA_DHASA_DEPTH.DEHA
    }

@unique
class DialogEntryType(IntEnum):
    CONJUNCTION = 0
    ENTRY_TRANSIT = 1
    VAKRA_GATHI = 2
    ECLIPSE = 3
    NAKSHATHRA_DHASA_PROGRESSION = 4

ALLOWED_STAR_DHASAS = ["vimsottari","yogini","ashtottari","chaturaaseeti_sama","dwadasottari","dwisatpathi",
                       "panchottari","satabdika","shodasottari","shastihayani","shattrimsa_sama"] 
_main_window_width = 550
_main_window_height = 150
_CALCULATE_WAIT_MSG = '<b>Calculating... Results will be updated here. Please wait...</b>'
GRAHA_DHASA_PKG = "jhora.horoscope.dhasa.graha"
PROGRESSION_FUNCTION = "nakshathra_dhasa_progression"    

class GeneralConjunctionDialog(QDialog):
    """
        Planetary Conjunction Dialog
    """
    def __init__(self,current_date_jd=None,place:drik.Place=None,planet1=const.SATURN_ID, chart_title='Planetary Conjunctions',
                 entry_type=DialogEntryType.CONJUNCTION,planet2=const.JUPITER_ID,raasi=None,
                 show_other_conjunction_options=False):
        """
            Entry Type: 0=> Planetary Conjunctions; 1=> Planet Entry/Transit 2=> Planet Vakra Gathi Change
                        3=> Eclipse, 4=> Nakshathra Dhasa Progression
        """
        super().__init__()
        if not isinstance(entry_type, DialogEntryType):
            raise ValueError(entry_type,"should be one of ",", ".join(f"{m.name}({m.value})" for m in DialogEntryType))
        if ( entry_type == DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION and
             (current_date_jd is None or place is None)
             ):
            raise AttributeError("For nashathra dhasa progression argument current_date_jd is treated as jd for date of birth. So jd and place are required.")
        self.show_other_conjunction_options = show_other_conjunction_options
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        y,m,d = map(int,current_date_str.split(','))
        hh,mm,ss = map(int,current_time_str.split(':'))
        if current_date_jd is None:
            current_date_jd = utils.julian_day_number(drik.Date(y,m,d),(hh,mm,ss))
        self._current_date_jd = current_date_jd
        if entry_type==DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION:
            self._jd_at_dob = current_date_jd
            self.dhasa_progression_correction = 0.0
            self._current_date_jd = utils.julian_day_number(drik.Date(y,m,d),(hh,mm,ss))
        self._conjunction_date_jd = current_date_jd
        self.Place = place
        self._planet1 = planet1 if entry_type != DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION else const.MOON_ID
        self._chart_title = chart_title
        self._entry_type = entry_type
        self._accept_clicked = False

        # Existing tracking
        self._separation_angle_index = 0
        if entry_type==DialogEntryType.CONJUNCTION:
            self._planet2 = planet2
        elif entry_type==DialogEntryType.ENTRY_TRANSIT:
            self._raasi = raasi

        # Remember last selections per mode (UI-only caches)
        # (Fix 3 – preserve per-mode planet1 on mode change)
        self._last_p1 = {m: None for m in DialogEntryType}  # for ALL modes
        self._last_p2 = None
        self._last_raasi_index = 0

        self.res = utils.resource_strings
        self._create_ui()

    def _create_ui(self):
        v_layout = QVBoxLayout()

        # -----------------------------
        # (0) Entry option row
        # -----------------------------
        entry_row = QHBoxLayout()
        self._rb_conj = QRadioButton(self.res['planetary_conjunctions_str'])
        self._rb_transit = QRadioButton(self.res['planet_transit_str'])
        self._rb_vakra = QRadioButton(self.res['vakra_gathi_change_str'])
        self._rb_eclipse = QRadioButton(self.res['eclipse_str'])
        self._rb_nak_dhasa_prog = QRadioButton(self.res["nakshathra_dhasa_progression_str"])
        entry_row.addWidget(self._rb_conj)
        entry_row.addWidget(self._rb_transit)
        entry_row.addWidget(self._rb_vakra)
        entry_row.addWidget(self._rb_eclipse)
        entry_row.addWidget(self._rb_nak_dhasa_prog)
        entry_row.addStretch()

        self._entry_group = QButtonGroup(self)
        self._entry_group.addButton(self._rb_conj, DialogEntryType.CONJUNCTION)
        self._entry_group.addButton(self._rb_transit, DialogEntryType.ENTRY_TRANSIT)
        self._entry_group.addButton(self._rb_vakra, DialogEntryType.VAKRA_GATHI)
        self._entry_group.addButton(self._rb_eclipse, DialogEntryType.ECLIPSE)
        self._entry_group.addButton(self._rb_nak_dhasa_prog, DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION)

        # select initial based on self._entry_type
        if self._entry_type == DialogEntryType.CONJUNCTION:
            self._rb_conj.setChecked(True)
        elif self._entry_type == DialogEntryType.ENTRY_TRANSIT:
            self._rb_transit.setChecked(True)
        elif self._entry_type == DialogEntryType.VAKRA_GATHI:
            self._rb_vakra.setChecked(True)
        elif self._entry_type == DialogEntryType.ECLIPSE:
            self._rb_eclipse.setChecked(True)
        elif self._entry_type == DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION:
            self._rb_nak_dhasa_prog.setChecked(True)
        else:
            raise ValueError(self._entry_type,"should be one of ",", ".join(f"{m.name}({m.value})" for m in DialogEntryType))

        self._entry_group.idClicked.connect(self._on_mode_changed)
        v_layout.addLayout(entry_row)
        for rb in self._entry_group.buttons():
            rb.setVisible(self.show_other_conjunction_options)

        # ------------------------------------
        # (1) Parameter row
        # ------------------------------------
        param_row = QHBoxLayout()
        # Conjunction-only UI
        self._sep_angle_combo = QComboBox()
        self._sep_angle_list = self.res['planet_separation_angle_list'].split(',')
        self._sep_angle_combo.addItems(self._sep_angle_list)
        self._sep_angle_combo.setCurrentIndex(0)
        self._separation_angle = self._sep_angle_combo.currentIndex()*30.
        param_row.addWidget(self._sep_angle_combo)

        self._start_planet_label = QLabel(self.res['dhasa_start_option_str'])
        param_row.addWidget(self._start_planet_label)
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

        # Eclipse controls
        self._eclipse_combo = QComboBox()
        self._eclipse_list = [self.res['solar_str']+' '+ self.res['eclipse_str'],
                              self.res['lunar_str']+' '+ self.res['eclipse_str']]
        self._eclipse_combo.addItems(self._eclipse_list)
        self._eclipse = 0 # Solar 1=>Lunar
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

        self._show_eclipse_location = QCheckBox(self.res['show_max_eclipse_location_str'])
        v_layout.addWidget(self._show_eclipse_location)
        # --- Controls for Nakshathra Dhasa Progression ---
        self._star_dhasa_combo = QComboBox()
        self._star_dhasa_combo.addItems(self.res[d+'_str'] for d in ALLOWED_STAR_DHASAS)
        param_row.addWidget(self._star_dhasa_combo)

        self._dhasa_level_combo = QComboBox()
        self._dhasa_level_combo.addItems([self.res[dl+'_str'] for dl in dhasa_levels.keys()])
        # Prevent signals while setting defaults (Fix 1 – part A)
        self._star_dhasa_combo.blockSignals(True)
        self._dhasa_level_combo.blockSignals(True)
        self._star_dhasa_combo.setCurrentIndex(0)
        self._dhasa_level_combo.setCurrentIndex(const.MAHA_DHASA_DEPTH.ANTARA-1)
        self._star_dhasa_combo.blockSignals(False)
        self._dhasa_level_combo.blockSignals(False)

        self._star_dhasa_index = 0
        self._dhasa_level_index = const.MAHA_DHASA_DEPTH.ANTARA
        param_row.addWidget(self._dhasa_level_combo)

        v_layout.addLayout(param_row)
        self._show_all_dhasa_level_check = QCheckBox("Show all dhasa levels")
        self._show_all_dhasa_level_check.setChecked(False)
        v_layout.addWidget(self._show_all_dhasa_level_check)
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

        self._after_before_combo = QComboBox()
        datetime_row.addWidget(self._after_before_combo)
        self._after_before_combo.addItems([self.res['next_str'],self.res['previous_str']])

        v_layout.addLayout(datetime_row)

        # ✅ Now safe: hook these signals AFTER _after_before_combo exists (Fix 1 – part B)
        self._star_dhasa_combo.currentIndexChanged.connect(self._star_dhasa_changed)
        self._dhasa_level_combo.currentIndexChanged.connect(self._dhasa_level_changed)

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

        # Window title and initial state
        self.setWindowTitle(self._chart_title)
        self._results_text.setText('')
        self._accept_button.setEnabled(False)

        # Populate controls and set initial visibility/selection for current mode
        self._apply_entry_type(self._entry_type, first_time=True, from_mode_change=False)

    def _star_dhasa_changed(self):
        self._star_dhasa_index = self._star_dhasa_combo.currentIndex()
        self._dhasa_level_index = self._dhasa_level_combo.currentIndex()+1
        # Same mode refresh (not a mode change)
        self._apply_entry_type(self._entry_type, first_time=False, from_mode_change=False)

    def _dhasa_level_changed(self):
        self._star_dhasa_index = self._star_dhasa_combo.currentIndex()
        self._dhasa_level_index = self._dhasa_level_combo.currentIndex()+1
        # Same mode refresh (not a mode change)
        self._apply_entry_type(self._entry_type, first_time=False, from_mode_change=False)

    def _eclipse_item_changed(self):
        self._eclipse = self._eclipse_combo.currentIndex()
        self._eclipse_type = self._eclipse_type_combo.currentIndex()
        self._eclipse_loc = self._eclipse_loc_combo.currentIndex()
        self._show_eclipse_location.setVisible(self._eclipse_loc==0)
        if self._eclipse_combo.currentIndex()==0:
            self._ect_dict = {self.res[k+'_str']:v for k,v in solar_eclipse_types.items()}
        else:
            self._ect_dict = {self.res[k+'_str']:v for k,v in lunar_eclipse_types.items()}
        self._eclipse_type_combo.clear()
        for key,mask in self._ect_dict.items():
            self._eclipse_type_combo.addItem(key,mask)
        # Same mode refresh (not a mode change)
        self._apply_entry_type(self._entry_type, first_time=False, from_mode_change=False)

    def closeEvent(self, *args, **kwargs):
        self._conjunction_date_jd = self._current_date_jd
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)

    # -------------------------
    # Mode switching glue (Fix the cache bug + preserve per-mode planet1)
    # -------------------------
    def _on_mode_changed(self, entry_type: int):
        prev_type = self._entry_type  # remember current mode BEFORE switching

        # Remember current selections into caches for the prev mode
        if self._planet1_combo.count() > 0:
            self._last_p1[prev_type] = self._planet1_combo.currentText()
        if prev_type == DialogEntryType.CONJUNCTION and self._planet2_combo.count() > 0:
            self._last_p2 = self._planet2_combo.currentText()
        if prev_type == DialogEntryType.ENTRY_TRANSIT and self._raasi_combo.count() > 0:
            self._last_raasi_index = self._raasi_combo.currentIndex()
        if self._sep_angle_combo.isVisible():
            self._separation_angle_index = self._sep_angle_combo.currentIndex()

        # Now switch the mode
        self._entry_type = self._entry_group.checkedId()

        # Indicate this is a mode change so we restore from per-mode cache
        self._apply_entry_type(self._entry_type, first_time=False, from_mode_change=True)

        # Clear results and wait for explicit compute, as requested
        self._results_text.setText('')
        self._accept_button.setEnabled(False)

    def _apply_entry_type(self, entry_type: int, first_time: bool=False, from_mode_change: bool=False):
        self._entry_type = entry_type
        self.setWindowTitle(self._entry_group.checkedButton().text())

        # --- Remember current selections (to keep during SAME-MODE refresh) ---
        prev_p1_text = self._planet1_combo.currentText() if self._planet1_combo.count() > 0 else None
        prev_p2_text = self._planet2_combo.currentText() if self._planet2_combo.count() > 0 else None
        prev_raasi_index = self._raasi_combo.currentIndex() if self._raasi_combo.count() > 0 else None

        # ---------- Populate planet1 list based on mode ----------
        self._planet1_combo.blockSignals(True)
        self._planet1_combo.clear()
        if entry_type == DialogEntryType.VAKRA_GATHI:  # Vakra Gathi Change
            p1_list = utils.PLANET_NAMES[const.MARS_ID:const.SATURN_ID+1]
        else:
            p1_list = [self.res['ascendant_str']] + utils.PLANET_NAMES[:9]
        self._planet1_combo.addItems(p1_list)

        # ---------- Restore planet1 ----------
        restored_p1 = False

        # (Fix 3) If this call came from a MODE CHANGE, ignore prev_p1_text and use per-mode cache
        if from_mode_change:
            cached = self._last_p1.get(entry_type)
            if cached:
                idx = self._planet1_combo.findText(cached)
                if idx >= 0:
                    self._planet1_combo.setCurrentIndex(idx)
                    restored_p1 = True
        else:
            # Same-mode UI refresh: try to keep the current text
            if prev_p1_text:
                idx_prev = self._planet1_combo.findText(prev_p1_text)
                if idx_prev >= 0:
                    self._planet1_combo.setCurrentIndex(idx_prev)
                    restored_p1 = True
            # If not restored, try cached per-mode selection
            if not restored_p1:
                cached = self._last_p1.get(entry_type)
                if cached:
                    idx = self._planet1_combo.findText(cached)
                    if idx >= 0:
                        self._planet1_combo.setCurrentIndex(idx)
                        restored_p1 = True

        self._planet1_combo.blockSignals(False)

        # ---------- Conjunction-only planet2 handling ----------
        self._planet2_combo.clear()
        if entry_type == DialogEntryType.CONJUNCTION:
            self._update_planet2_list()  # repopulate based on current planet1
            restored_p2 = False
            if not from_mode_change and prev_p2_text:
                idx2 = self._planet2_combo.findText(prev_p2_text)
                if idx2 >= 0:
                    self._planet2_combo.setCurrentIndex(idx2)
                    restored_p2 = True
            if not restored_p2 and self._last_p2:
                idx2 = self._planet2_combo.findText(self._last_p2)
                if idx2 >= 0:
                    self._planet2_combo.setCurrentIndex(idx2)

        # ---------- Transit-only raasi ----------
        self._raasi_combo.clear()
        if entry_type == DialogEntryType.ENTRY_TRANSIT:
            self._raasi_combo.addItems([self.res['raasi_str']] + utils.RAASI_LIST)
            if not from_mode_change and prev_raasi_index is not None and 0 <= prev_raasi_index < self._raasi_combo.count():
                self._raasi_combo.setCurrentIndex(prev_raasi_index)
            else:
                # restore cached raasi for transit mode
                if 0 <= self._last_raasi_index < self._raasi_combo.count():
                    self._raasi_combo.setCurrentIndex(self._last_raasi_index)

        # ---------- Constructor-time defaults if still not restored ----------
        if not restored_p1 and first_time:
            try:
                if entry_type in (DialogEntryType.CONJUNCTION, DialogEntryType.ENTRY_TRANSIT, DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION):
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
        elif not restored_p1 and not from_mode_change:
            # final fallback (same-mode refresh)
            self._planet1_combo.setCurrentIndex(0)

        # raasi for transit on first time using _raasi
        if entry_type == DialogEntryType.ENTRY_TRANSIT:
            if first_time and getattr(self, "_raasi", None) is not None:
                idxr = int(self._raasi) if isinstance(self._raasi, int) else 0
                if 0 <= idxr <= len(utils.RAASI_LIST):
                    self._raasi_combo.setCurrentIndex(idxr)
                else:
                    self._raasi_combo.setCurrentIndex(0)

        # sep angle
        if entry_type == DialogEntryType.CONJUNCTION:
            self._sep_angle_combo.setCurrentIndex(self._separation_angle_index if self._separation_angle_index is not None else 0)
            self._separation_angle = self._sep_angle_combo.currentIndex() * 30.0

        # ---------- Visibility matrix ----------
        is_conj = (entry_type == DialogEntryType.CONJUNCTION)
        is_transit = (entry_type == DialogEntryType.ENTRY_TRANSIT)
        is_vakra = (entry_type == DialogEntryType.VAKRA_GATHI)
        is_eclipse = (entry_type == DialogEntryType.ECLIPSE)
        is_star_dhasa = (entry_type == DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION)
        self._planet1_combo.setVisible(not is_eclipse)
        self._sep_angle_combo.setVisible(is_conj)
        self._planet2_combo.setVisible(is_conj)
        self._raasi_combo.setVisible(is_transit)
        self._eclipse_combo.setVisible(is_eclipse)
        self._eclipse_loc_combo.setVisible(is_eclipse)
        self._show_eclipse_location.setVisible(is_eclipse and self._eclipse_loc==0)
        self._eclipse_type_combo.setVisible(is_eclipse)
        self._start_planet_label.setVisible(is_star_dhasa)
        self._star_dhasa_combo.setVisible(is_star_dhasa)
        self._dhasa_level_combo.setVisible(is_star_dhasa)
        if hasattr(self, "_after_before_combo"):  # guard (Fix 1 – safety)
            self._after_before_combo.setVisible(not is_star_dhasa)

    # (UNCHANGED) your original helper
    def _update_planet2_list(self):
        if self._entry_type != DialogEntryType.CONJUNCTION: return
        self._planet2_combo.clear()
        _planet2_list = [self.res['ascendant_str']]+ utils.PLANET_NAMES[:9]
        # remove the currently selected planet1
        if self._planet1_combo.currentText() in _planet2_list:
            _planet2_list.remove(self._planet1_combo.currentText())
        # if Rahu or Ketu chosen for planet1, restrict to 7
        if self._planet1_combo.currentIndex()==8 or self._planet1_combo.currentIndex()==9:
            _planet2_list = _planet2_list[:7]
        self._planet2_combo.addItems(_planet2_list)
        self._planet2_combo.setCurrentIndex(0)
        if hasattr(self, "_planet2") and utils.PLANET_NAMES[self._planet2] in _planet2_list:
            self._planet2_combo.setCurrentText(utils.PLANET_NAMES[self._planet2])

    # (UNCHANGED) compute dispatch
    def _calculate_clicked(self):
        self._accept_button.setEnabled(False)
        if self._entry_type==DialogEntryType.CONJUNCTION:
            self.setWindowTitle(self.res['planetary_conjunctions_str'])
            self._find_conjunction_date()
            print('conjunction',self._conjunction_date_jd)
        elif self._entry_type==DialogEntryType.ENTRY_TRANSIT:
            self.setWindowTitle(self.res['planet_transit_str'])
            self._find_transit_date()
            print('transit',self._conjunction_date_jd)
        elif self._entry_type==DialogEntryType.VAKRA_GATHI:
            self.setWindowTitle(self.res['vakra_gathi_change_str'])
            self._find_retrogression_change_date()
            print('vakra gathi',self._conjunction_date_jd)
        elif self._entry_type==DialogEntryType.ECLIPSE:
            self.setWindowTitle(self.res['eclipse_str'])
            self._find_eclipse_date()
            print('eclipse',"solar" if self._eclipse==0 else "lunar",self._eclipse_type_str,self._conjunction_date_jd)
        elif self._entry_type==DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION:
            self.setWindowTitle(self.res["nakshathra_dhasa_progression_str"])
            self._find_progression_correction()
        self._accept_button.setEnabled(True)
        self.adjustSize()
    def _find_retrogression_change_date(self):
        from jhora import const
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        panchanga_place = self.Place
        year,month,day = map(int,self._dob_text.text().split(","))
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        panchanga_start_date = drik.Date(year,month,day+1*direction)
        cur_jd,ret_sign = drik.next_planet_retrograde_change_date(self._planet1,panchanga_start_date,panchanga_place,direction=direction)
        retStr=''  if ret_sign == 1 else const._retrogade_symbol
        self._conjunction_date_jd = cur_jd
        results = self._planet1_combo.currentText()+' '
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+utils.PLANET_NAMES[self._planet1]+retStr
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._dob_text.setText(str(y)+','+str(m)+','+str(d));self._tob_text.setText(str(hh)+':'+str(mm)+':'+str(ss))
        QApplication.restoreOverrideCursor()        
        
    def _find_conjunction_date(self):
        self._separation_angle = self._sep_angle_combo.currentIndex()*30.
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
        if ret is None:
            self._results_text.setText('Could not find planetary conjunctions for sep angle '+str(self._separation_angle)+'  Try increasing search range')
            QApplication.restoreOverrideCursor()
            return
        else:
            cur_jd,p1_long,p2_long = ret
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
        _show_where_eclipse = self._show_eclipse_location.isChecked()
        if self._eclipse==0:
            _ecl_ret = eclipse.next_solar_eclipse(jd_local, place, _eclipse_location_type, _eclipse_type, _search_backward,
                                              show_maximum_eclipse_global_location=_show_where_eclipse)
            _ecl1_str=utils.resource_strings['solar_str']+' '+ utils.resource_strings['eclipse_str']
        else:
            _ecl_ret = eclipse.next_lunar_eclipse(jd_local, place, _eclipse_location_type, _eclipse_type, _search_backward,
                                              show_maximum_eclipse_global_location=_show_where_eclipse)
            _ecl1_str=utils.resource_strings['lunar_str']+' '+ utils.resource_strings['eclipse_str']
        _ecl_loc = None
        if _show_where_eclipse:
            _ecl,_ecl_loc = _ecl_ret
        else:
            _ecl = _ecl_ret
        _ecl_jd_str = "[" + ",".join(
            f"({y},{m},{d},{int(h):02d}:{int(mi):02d}:{int(round(s)):02d})"
            for y,m,d,fh in _ecl[1] for h,mi,s in (utils.to_dms(fh, as_string=False),)
        ) + "]"
        self._eclipse_type_str = _ecl[0]
        _ecl_results = (f"{utils.resource_strings[_ecl[0] + '_str']} "f"{_ecl1_str} "f"{_ecl_jd_str}")
        self._results_text.setText(_ecl_results)
        y,m,d,fh = _ecl[1][0]; hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._current_date_jd = utils.julian_day_number(drik.Date(y,m,d),(hh,mm,ss))
        self._dob_text.setText(f"{y},{m:02d},{d:02d}")
        self._tob_text.setText(f"{hh:02d}:{mm:02d}:{ss:02d}")
        self._conjunction_date_jd = self._current_date_jd
        if self._show_eclipse_location.isChecked() and _ecl_loc:
            import reverse_geocode
            loc_results = reverse_geocode.get((_ecl_loc[0],_ecl_loc[1]))
            keys = ["country", "state", "city", "latitude", "longitude"]
            loc_str = "\n".join(f"{self.res[k+'_str']}: {loc_results[k]}" for k in keys if k in loc_results)
            QMessageBox.about(self,self.res['eclipse_maximum_location_str'],loc_str)
        QApplication.restoreOverrideCursor()        

    def _find_transit_date(self):
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = const._ascendant_symbol if self._planet1_combo.currentIndex()==0 else utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        panchanga_place = self.Place
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        start_jd = self._current_date_jd + direction* (1/(24*60*60))
        self._raasi = None if self._raasi_combo.currentIndex()==0 else self._raasi_combo.currentIndex()
        (y,m,d,fh),p1_long = drik.next_planet_entry_date(self._planet1,start_jd,panchanga_place,
                                                     direction=direction,raasi=self._raasi)
        cur_jd = utils.julian_day_number(drik.Date(y,m,d),(fh,0,0))
        self._conjunction_date_jd = cur_jd; self._current_date_jd = cur_jd
        results = self._planet1_combo.currentText()+' '
        p1_rasi,p1_long = drik.dasavarga_from_long(p1_long, divisional_chart_factor=1)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+self.res['longitude_str']+' :'+ utils.RAASI_LIST[p1_rasi]+' ' + utils.to_dms(p1_long,is_lat_long='plong')+' '
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        hh,mm,ss = utils.to_dms(fh,as_string=False)
        self._dob_text.setText(str(y)+','+str(m)+','+str(d));self._tob_text.setText(str(hh)+':'+str(mm)+':'+str(ss))
        QApplication.restoreOverrideCursor()        

    def _accept_and_close(self):
        self._accept_clicked = True
        self.accept()

    def _close_dialog(self):
        self._accept_clicked = False
        self.reject()

    def _get_dhasa_progression_correction(self):
        self._star_dhasa_index = self._star_dhasa_combo.currentIndex()
        dhasa_name = ALLOWED_STAR_DHASAS[self._star_dhasa_index]
        """
        Dynamically import the selected dhasa module and call its get_dhasa_bhukthi().
        """
        if dhasa_name not in ALLOWED_STAR_DHASAS:
            raise ValueError(f"Unsupported dhasa: {dhasa_name!r}")
    
        try:
            module = importlib.import_module(f"{GRAHA_DHASA_PKG}.{dhasa_name}")
        except ModuleNotFoundError as e:
            raise ImportError(f"Could not import module for dhasa {dhasa_name!r}: {e}") from e
    
        func = getattr(module, PROGRESSION_FUNCTION, None)
        if not callable(func):
            raise AttributeError(
                f"Module {module.__name__} does not expose a callable {PROGRESSION_FUNCTION}"
            )
        # Call it with your args
        jd_at_dob = self._jd_at_dob; place = self.Place; jd_current = self._current_date_jd
        dsp = self._dhasa_planet
        DLI = self._dhasa_level_index
        dsp_str = const._ascendant_symbol if dsp=='L' else utils.PLANET_NAMES[dsp]
        print(utils.jd_to_gregorian(jd_at_dob),utils.jd_to_gregorian(jd_current),dsp_str,
              "DhasaLevel",self._dhasa_level_index)
        self.dhasa_progression_correction, self._running_dhasa = func(jd_at_dob, place,jd_current,
                                                 dhasa_starting_planet=dsp,dhasa_level_index=DLI)

    def _find_progression_correction(self):
        show_all_levels_of_running_dhasa = self._show_all_dhasa_level_check.isChecked()
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        place = self.Place
        y,m,d = map(int,self._dob_text.text().split(",")); dob=drik.Date(y,m,d)
        hh,mm,ss = map(int,self._tob_text.text().split(":")); tob=(hh,mm,ss)
        self._current_date_jd = utils.julian_day_number(dob,tob)
        self._dhasa_planet = const._ascendant_symbol if self._planet1_combo.currentIndex()==0 else self._planet1_combo.currentIndex()-1
        print(self._dhasa_planet,self._planet1_combo.currentIndex(),self._planet1_combo.currentText())
        dhasa_str = self._star_dhasa_combo.currentText()
        results = "<html><b>"+f"{dhasa_str} {self.res['dhasa_str']}:<br>"
        dli_lords = ['maha_str','antara_str','prathyanthara_str','sookshma_str','praana_str','deha_str']
        if show_all_levels_of_running_dhasa:
            results += "<style>table{border: 1px solid black}</style>"
            results += f"<table><tr><th>{self.res['dhasa_str']}</th><th>{self.res['lord_str']}</th>"
            results += f"<th>{self.res['starts_at_str']}</th><th>{self.res['ends_at_str']}</th></tr>"
            for dli in range(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,const.MAHA_DHASA_DEPTH.DEHA+1):
                self._dhasa_level_combo.setCurrentIndex(dli-1)
                self._get_dhasa_progression_correction()
                lords,dhasa_start,dhasa_end = self._running_dhasa
                if not isinstance(lords,tuple): lords = [lords]
                rd_lord_str = f"<td>{self.res[dli_lords[dli-1]]}</td><td>{utils.PLANET_NAMES[lords[dli-1]]}</td>"
                dhasa_start_str = f"<td>{dhasa_start[0]:04d}-{dhasa_start[1]:02d}-{dhasa_start[2]:02d} {utils.to_dms(dhasa_start[-1])}</td>"
                dhasa_end_str = f"<td>{dhasa_end[0]:04d}-{dhasa_end[1]:02d}-{dhasa_end[2]:02d} {utils.to_dms(dhasa_end[-1])}</td>"
                results += f"<tr>{rd_lord_str} {dhasa_start_str} {dhasa_end_str}</tr>"
            results +="</table>"
        else:
            dli = self._dhasa_level_index
            self._get_dhasa_progression_correction()
            lords,dhasa_start,dhasa_end = self._running_dhasa
            if not isinstance(lords,tuple): lords = [lords]
            rd_lord_str = '/'.join(utils.PLANET_NAMES[p] for p in lords)
            dhasa_start_str = f"{dhasa_start[0]:04d}-{dhasa_start[1]:02d}-{dhasa_start[2]:02d} {utils.to_dms(dhasa_start[-1])} " + self.res['starts_at_str']
            dhasa_end_str = f"{dhasa_end[0]:04d}-{dhasa_end[1]:02d}-{dhasa_end[2]:02d} {utils.to_dms(dhasa_end[-1])} " + self.res['ends_at_str']
            dhasa_str = self._star_dhasa_combo.currentText()
            results += f"{dhasa_str} {self.res['dhasa_str']}:"+f"{rd_lord_str}<br>{dhasa_start_str} {dhasa_end_str}<br>"
            
        results += "Dhasa Progression Correction="+utils.to_dms(self.dhasa_progression_correction,is_lat_long='plong')+'<br>'
        results += "Add this to all planet longitudes to get nakshathra dhasa progression chart.<br>"
        results += "</b></html>"
        #self._conjunction_date_jd = self._current_date_jd
        self._results_text.setText(results)
        QApplication.restoreOverrideCursor()        

def show(current_date_jd=None,place:drik.Place=None,planet1=6,planet2=4, chart_title='Planetary Conjunctions',entry_type=0,
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
    entry_type = DialogEntryType.NAKSHATHRA_DHASA_PROGRESSION
    #show(jd, place,entry_type=entry_type,chart_title=_chart_title,show_other_conjunction_options=True)
    show(jd,place,entry_type=entry_type)
    exit()

