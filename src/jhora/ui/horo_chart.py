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

import re
import sys
import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCompleter,
    QMessageBox, QComboBox, QPushButton, QApplication, QFileDialog
)
from PyQt6.QtCore import Qt

from _datetime import datetime
import img2pdf

from jhora import utils, const
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope import info
from jhora.ui.chart_styles import (
    EastIndianChart,
    WesternChart,
    SouthIndianChart,
    NorthIndianChart,
    SudarsanaChakraChart
)
from jhora.ui.place_widget import PlaceWidget, parse_location_record, parse_location_tuple
from jhora.horoscope.dhasa import sudharsana_chakra


_IMAGES_PATH = '../images/'
_IMAGE_ICON_PATH = _IMAGES_PATH + "lord_ganesha2.jpg"
_DATA_PATH = '../data/'


""" UI Constants """
_main_window_width = 650
_main_window_height = 630
_info_label1_height = 200
_info_label2_height = 200
_info_label1_font_size = 7
_info_label2_font_size = 7
_footer_label_font_height = 8
_footer_label_height = 30
_chart_size_factor = 0.875

AVAILABLE_CHART_STYLES = utils.get_available_chart_styles()

_CHART_STYLE_KEYS = list(AVAILABLE_CHART_STYLES.keys())
_DEFAULT_UI_CHART_TYPE = const.default_chart_type

_SOUTH_INDIAN_STYLES = {
    const.CHART_STYLE.SOUTH_INDIAN_REGULAR,
    const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR,
}

_EAST_INDIAN_STYLES = {
    const.CHART_STYLE.EAST_INDIAN_WITH_FRAME,
    const.CHART_STYLE.EAST_INDIAN_NO_FRAME,
}


available_languages = const.available_languages 

def _resource_text(resources, key, fallback_key=None, default_text=None):
    """
    Return translated resource text with fallback support.
    """
    if resources is None:
        return default_text or key

    if key in resources:
        return resources[key]

    if fallback_key is not None and fallback_key in resources:
        return resources[fallback_key]

    return default_text or key


def _chart_style_display_name(resources, chart_style):
    """
    Return localized chart style name for combo box.
    """
    cfg = AVAILABLE_CHART_STYLES[chart_style]
    return _resource_text(
        resources,
        cfg["resource"],
        cfg.get("fallback_resource"),
        cfg.get("default_text", cfg["resource"])
    )


def _normalize_chart_type(chart_type):
    """
    Accept old string chart type or new const.CHART_STYLE value.
    Return const.CHART_STYLE value.

    Supported old-style examples:
        'south indian'
        'south indian irregular'
        'south indian anticlockwise'
        'north indian'
        'east indian'
        'east indian noframe'
        'east indian no frame'
        'western'
        'sudarsana_chakra'
    """
    if chart_type in AVAILABLE_CHART_STYLES:
        return chart_type

    if chart_type is None:
        return _DEFAULT_UI_CHART_TYPE

    s = str(chart_type).strip().lower()

    if "south" in s and (
        "irregular" in s
        or "alternate" in s
        or "anti" in s
        or "anticlock" in s
        or "anti-clock" in s
        or "counter" in s
    ):
        return const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR

    if "south" in s:
        return const.CHART_STYLE.SOUTH_INDIAN_REGULAR

    if "east" in s and (
        "noframe" in s
        or "no frame" in s
        or "no outer" in s
        or "alternate" in s
    ):
        return const.CHART_STYLE.EAST_INDIAN_NO_FRAME

    if "east" in s:
        return const.CHART_STYLE.EAST_INDIAN_WITH_FRAME

    if "north" in s:
        return const.CHART_STYLE.NORTH_INDIAN

    if "west" in s:
        return const.CHART_STYLE.WESTERN

    if "sudar" in s:
        return const.CHART_STYLE.SUDARSANA_CHAKRA

    return _DEFAULT_UI_CHART_TYPE

class WidePopupComboBox(QComboBox):
    def showPopup(self):
        fm = self.fontMetrics()

        max_width = 0
        for i in range(self.count()):
            max_width = max(
                max_width,
                fm.horizontalAdvance(self.itemText(i))
            )

        # margins + scrollbar + padding
        max_width += 40

        self.view().setMinimumWidth(
            max(self.width(), max_width)
        )

        super().showPopup()
class ChartSimple(QWidget):
    def __init__(self, chart_type='south indian', calculation_type: str = 'drik'):
        super().__init__()

        self._footer_title = ''
        self._image_icon_path = _IMAGE_ICON_PATH
        self.setWindowIcon(QtGui.QIcon(self._image_icon_path))
        utils.use_database_for_world_cities(enable_database=True)
        self._language = list(available_languages.keys())[0]
        utils.set_language(available_languages[self._language])
        self.resources = utils.resource_strings

        self._chart_type = _normalize_chart_type(chart_type)
        self._calculation_type = calculation_type.lower()
        self._ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE

        self.setFixedSize(_main_window_width, _main_window_height)
        self.setWindowTitle('')

        # ----------------------------
        # changed/dirty tracking flags
        # ----------------------------
        self._inputs_changed = False
        self._suspend_input_change_tracking = True

        self._v_layout = QVBoxLayout()

        self._create_row1_ui()
        self._create_row_2_and_3_ui()
        self._create_info_ui()
        self._create_chart_ui()

        self.compute_horoscope()

        # end init -> enable change tracking and ensure clean button state
        self._suspend_input_change_tracking = False
        self._clear_inputs_changed()

    # =========================================================
    # CHANGED / DIRTY FLAG HELPERS
    # =========================================================
    def _mark_inputs_changed(self, reason: str = ""):
        """
        Mark UI inputs as changed, so the currently displayed chart is stale.
        This does NOT change the button text.
        It only bolds the Show Chart button.
        """
        if getattr(self, "_suspend_input_change_tracking", False):
            return
        self._inputs_changed = True
        self._update_compute_button_changed_state()

    def _clear_inputs_changed(self):
        """
        Clear changed flag after a successful compute.
        """
        self._inputs_changed = False
        self._update_compute_button_changed_state()

    def _update_compute_button_changed_state(self):
        """
        Visual cue on the Show Chart button when inputs have changed.
        Keep the button text unchanged. Only toggle button font bold/normal.
        """
        if not hasattr(self, "_compute_button"):
            return
        font = self._compute_button.font()
        font.setBold(bool(getattr(self, "_inputs_changed", False)))
        self._compute_button.setFont(font)

    def _compute_and_clear_changed(self):
        """
        Wrapper used by the Show Chart button.
        Runs compute_horoscope(), then clears the changed flag only if compute succeeds.
        """
        ok = self.compute_horoscope()
        if ok:
            self._clear_inputs_changed()

    # -----------------------------------------------------------------
    # Chart widget helpers
    # -----------------------------------------------------------------

    def _create_chart_widget(self, chart_type):
        chart_type = _normalize_chart_type(chart_type)

        chart_config = AVAILABLE_CHART_STYLES[chart_type]
        ChartClass = chart_config["class"]

        kwargs = {
            "chart_size_factor": _chart_size_factor
        }
        kwargs.update(chart_config["args"])

        return ChartClass(**kwargs)

    def _clear_layout_widgets(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _selected_chart_type_from_combo(self):
        index = self._chart_type_combo.currentIndex()
        if index < 0 or index >= len(_CHART_STYLE_KEYS):
            return _DEFAULT_UI_CHART_TYPE
        return _CHART_STYLE_KEYS[index]

    def _set_chart_type_combo_to_current_chart_type(self):
        try:
            index = _CHART_STYLE_KEYS.index(self._chart_type)
        except ValueError:
            index = 0
            self._chart_type = _CHART_STYLE_KEYS[0]

        self._chart_type_combo.setCurrentIndex(index)

    def _create_chart_ui(self):
        """
        Create or recreate the chart widgets.

        This version avoids repeatedly adding new chart layouts/footer labels
        whenever Show Chart is clicked.
        """
        if not hasattr(self, "_chart_h_layout"):
            self._chart_h_layout = QHBoxLayout()
            self._v_layout.addLayout(self._chart_h_layout)
        else:
            self._clear_layout_widgets(self._chart_h_layout)

        self._table1 = self._create_chart_widget(self._chart_type)
        self._table2 = self._create_chart_widget(self._chart_type)

        self._chart_h_layout.addWidget(self._table1)
        self._chart_h_layout.addWidget(self._table2)

        if not hasattr(self, "_footer_label"):
            self._add_footer_to_chart()
            self._v_layout.addWidget(self._footer_label)

        self.setLayout(self._v_layout)

        self._table1.update()
        self._table2.update()

    # -----------------------------------------------------------------
    # UI creation
    # -----------------------------------------------------------------

    def _create_row1_ui(self):
        h_layout = QHBoxLayout()

        name_label = QLabel("Name:")
        h_layout.addWidget(name_label)

        self._name_text = QLineEdit("Today")
        self._name = self._name_text.text()
        self._name_text.setToolTip('Enter your name')
        self._name_text.textChanged.connect(lambda _t: self._mark_inputs_changed("name changed"))
        h_layout.addWidget(self._name_text)

        self._place_label = QLabel("Place:")
        h_layout.addWidget(self._place_label)
        
        self._place_name = ''
        self._elevation = 0.0
        
        self._place_widget = PlaceWidget(
            self,
            initial_text=self._place_name,
            placeholder_text="Enter place of birth, country name",
            tooltip_text="Enter place of birth, country name",
        )
        
        self._place_text = self._place_widget.lineEdit()
        
        self._place_widget.textEditedSignal.connect(self._resize_place_text_size)
        self._place_widget.locationResolved.connect(self._on_location_resolved)
        self._place_widget.locationLookupFailed.connect(self._on_location_lookup_failed)
        self._place_widget.textEditedSignal.connect(lambda _t: self._mark_inputs_changed("place edited"))
        
        self._place_text.setToolTip('Enter place of birth, country name')
        
        h_layout.addWidget(self._place_widget)
        lat_label = QLabel("Latidude:")
        h_layout.addWidget(lat_label)

        self._lat_text = QLineEdit('')
        self._latitude = 0.0
        self._lat_text.setToolTip('Enter Latitude preferably exact at place of birth: Format: +/- xx.xxx')
        self._lat_text.textChanged.connect(lambda _t: self._mark_inputs_changed("latitude changed"))
        h_layout.addWidget(self._lat_text)

        long_label = QLabel("Longitude:")
        h_layout.addWidget(long_label)

        self._long_text = QLineEdit('')
        self._longitude = 0.0
        self._long_text.setToolTip('Enter Longitude preferably exact at place of birth. Format +/- xx.xxx')
        self._long_text.textChanged.connect(lambda _t: self._mark_inputs_changed("longitude changed"))
        h_layout.addWidget(self._long_text)

        tz_label = QLabel("Time Zone:")
        h_layout.addWidget(tz_label)

        self._tz_text = QLineEdit('')
        self._time_zone = 0.0
        self._tz_text.setToolTip('Enter Time offset from GMT e.g. -5.5 or 4.5')
        self._tz_text.textChanged.connect(lambda _t: self._mark_inputs_changed("timezone changed"))

        """
        Initialize with default place based on IP.
        """
        loc = utils.get_place_from_user_ip_address()
        print('loc from IP address', loc)
        
        if loc and len(loc) >= 4:
            print('setting values from loc')
            elev = float(loc[4]) if len(loc) >= 5 else 0.0
            self.place(loc[0], loc[1], loc[2], loc[3], elev)
        h_layout.addWidget(self._tz_text)
        self._v_layout.addLayout(h_layout)

    def _reset_place_text_size(self):
        # Delegates to PlaceWidget (see place_widget.py: PlaceWidget.reset_size()).
        # Consolidated here from what used to be 4 independent, drifting
        # copies of this exact method across horo_chart.py, horo_chart_tabs.py,
        # panchangam.py and vedic_calendar.py.
        self._place_widget.reset_size()

    def _resize_place_text_size(self):
        # Delegates to PlaceWidget.resize_to_text(), which also fixes a bug
        # this file's old copy had: no guard for empty text (see
        # place_widget.py docstring for details).
        self._place_widget.resize_to_text()

    def _on_location_resolved(self, rec):
        """
        Consumes the location record PlaceWidget itself already resolved
        (via utils.get_location_record()) -- this does NOT call
        utils.get_location() a second time for the same query text.
        FIX: The previous _get_location(place_name) handler (wired to the
        placeSelected(str) signal) re-ran the ENTIRE lookup chain --
        including any live network geocode call -- a second time immediately
        after PlaceWidget had already run it once internally to validate the
        selection. panchangam.py and vedic_calendar.py already carried this
        fix; this file did not until now.
        """
        parsed = parse_location_record(rec)
        if parsed is None:
            return
        self._place_name, self._latitude, self._longitude, self._time_zone, self._elevation = parsed
        self._place_text.setText(self._place_name)
        self._lat_text.setText(str(self._latitude))
        self._long_text.setText(str(self._longitude))
        self._tz_text.setText(str(self._time_zone))
        self._reset_place_text_size()

    def _on_location_lookup_failed(self, place_name):
        msg = (
            place_name +
            " could not be found in OpenStreetMap.\n"
            "Try entering latitude and longitude manually.\n"
            "Or try entering nearest big city"
        )
        print(msg)
        self._lat_text.setText('')
        self._long_text.setText('')
        self._reset_place_text_size()

    def _create_row_2_and_3_ui(self):
        h_layout = QHBoxLayout()

        dob_label = QLabel("Date of Birth:")
        h_layout.addWidget(dob_label)

        self._date_of_birth = ''
        self._dob_text = QLineEdit(self._date_of_birth)
        self._dob_text.setToolTip(
            'Date of birth in the format YYYY,MM,DD\n'
            'For BC enter negative years.\n'
            'Allowed Year Range: -13000 (BC) to 16800 (AD)'
        )
        self._dob_text.textChanged.connect(lambda _t: self._mark_inputs_changed("date changed"))
        h_layout.addWidget(self._dob_text)

        tob_label = QLabel("Time of Birth:")
        h_layout.addWidget(tob_label)

        self._time_of_birth = ''
        self._tob_text = QLineEdit(self._time_of_birth)
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        self._tob_text.textChanged.connect(lambda _t: self._mark_inputs_changed("time changed"))

        current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self.date_of_birth(current_date_str)
        self.time_of_birth(current_time_str)

        h_layout.addWidget(self._tob_text)

        self._chart_type_combo = WidePopupComboBox()
        self._chart_type_combo.addItems([
            _chart_style_display_name(self.resources, cs)
            for cs in _CHART_STYLE_KEYS
        ])
        self._chart_type_combo.setToolTip('Choose birth chart style north, south, east, western, etc.')
        self._set_chart_type_combo_to_current_chart_type()
        self._chart_type_combo.currentIndexChanged.connect(lambda _i: self._mark_inputs_changed("chart type changed"))
        h_layout.addWidget(self._chart_type_combo)
        if utils.astro_engine_is_drik():
            available_ayanamsa_modes = list(const.available_ayanamsa_modes.keys())
            self._ayanamsa_combo = WidePopupComboBox()
            self._ayanamsa_combo.addItems(available_ayanamsa_modes)
            self._ayanamsa_combo.setToolTip('Choose Ayanamsa mode from the list')
            self._ayanamsa_value = None
            self._ayanamsa_combo.setCurrentText(self._ayanamsa_mode)
            self._ayanamsa_combo.currentIndexChanged.connect(lambda _i: self._mark_inputs_changed("ayanamsa changed"))
            h_layout.addWidget(self._ayanamsa_combo)
        self._lang_combo = WidePopupComboBox()
        self._lang_combo.addItems(list(available_languages.keys()))
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.currentIndexChanged.connect(lambda _i: self._mark_inputs_changed("language changed"))
        h_layout.addWidget(self._lang_combo)

        self._compute_button = QPushButton("Show Chart")
        self._compute_button.setFont(QtGui.QFont("Arial Bold", 9))
        self._compute_button.clicked.connect(self._compute_and_clear_changed)
        self._compute_button.setToolTip('Click to update the chart information based on selections made')
        h_layout.addWidget(self._compute_button)

        save_image_button = QPushButton("Save as PDF")
        save_image_button.setFont(QtGui.QFont("Arial Bold", 8))
        save_image_button.clicked.connect(self.save_as_pdf)
        save_image_button.setToolTip('Click to save horoscope as a PDF')
        h_layout.addWidget(save_image_button)

        self._v_layout.addLayout(h_layout)

    def _create_info_ui(self):
        h_layout = QHBoxLayout()

        self._info_label1 = QLabel("Information:")
        self._info_label1.setStyleSheet(
            "border: 1px solid black;" +
            ' font-size:' + str(_info_label1_font_size) + 'pt'
        )
        self._info_label1.setFixedHeight(_info_label1_height)
        h_layout.addWidget(self._info_label1)

        self._info_label2 = QLabel("Information:")
        self._info_label2.setStyleSheet(
            "border: 1px solid black;" +
            ' font-size:' + str(_info_label2_font_size) + 'pt'
        )
        self._info_label2.setFixedHeight(_info_label2_height)
        h_layout.addWidget(self._info_label2)

        self._v_layout.addLayout(h_layout)

    def _add_footer_to_chart(self):
        self._footer_label = QLabel('')
        self._footer_label.setTextFormat(Qt.TextFormat.RichText)
        self._footer_label.setText(self._footer_title)
        self._footer_label.setStyleSheet("border: 1px solid black;")
        self._footer_label.setFont(QtGui.QFont("Arial Bold", _footer_label_font_height))
        self._footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer_label.setFixedHeight(_footer_label_height)
        self._footer_label.setFixedWidth(self.width())
        self._footer_label.setWordWrap(True)

    # -----------------------------------------------------------------
    # Public setters
    # -----------------------------------------------------------------

    def _on_application_exit(self):
        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)

        sys.excepthook = except_hook
        QApplication.quit()

    def ayanamsa_mode(self, ayanamsa_mode, ayanamsa=None):
        """
        Set Ayanamsa mode.

        @param ayanamsa_mode:
            Default - Lahiri.
            See drik.available_ayanamsa_modes for list of available models.
        """
        self._ayanamsa_mode = ayanamsa_mode
        self._ayanamsa_value = ayanamsa

        if utils.astro_engine_is_drik() and hasattr(self, "_ayanamsa_combo"):
            self._ayanamsa_combo.setCurrentText(ayanamsa_mode)

    def place(self, place_name, latitude, longitude, timezone_hrs, elevation=0.0):
        """
        Set the place of birth.
        NOTE: latitude/longitude/timezone_hrs/elevation are coerced to float
        here (previously they were stored as-is, so a caller passing e.g.
        a numeric string would silently propagate it downstream, unlike
        panchangam.py's equivalent set_place_fields(), which already cast).
        """
        self._place_name = place_name
        self._latitude = float(latitude)
        self._longitude = float(longitude)
        self._time_zone = float(timezone_hrs)
        self._elevation = float(elevation)
    
        self._place_text.setText(self._place_name)
        self._lat_text.setText(str(self._latitude))
        self._long_text.setText(str(self._longitude))
        self._tz_text.setText(str(self._time_zone))
    def name(self, name):
        """
        Set name of the person whose horoscope is sought.
        """
        self._name = name
        self._name_text.setText(name)

    def chart_type(self, chart_type):
        """
        Set chart type of the horoscope.

        Accepts either:
            - old string names such as 'south indian', 'north indian', 'east indian'
            - new const.CHART_STYLE enum values
        """
        self._chart_type = _normalize_chart_type(chart_type)

        if hasattr(self, "_chart_type_combo"):
            blocker = QtCore.QSignalBlocker(self._chart_type_combo)
            self._set_chart_type_combo_to_current_chart_type()
            del blocker

    def latitude(self, latitude):
        """
        Sets the latitude manually.
        """
        self._latitude = float(latitude)
        self._lat_text.setText(str(latitude))

    def longitude(self, longitude):
        """
        Sets the longitude manually.
        """
        self._longitude = float(longitude)
        self._long_text.setText(str(longitude))

    def time_zone(self, time_zone):
        """
        Sets the time zone offset manually.
        """
        self._time_zone = float(time_zone)
        self._tz_text.setText(str(time_zone))

    def date_of_birth(self, date_of_birth):
        """
        Sets the date of birth.
        Format: YYYY,MM,DD
        """
        self._date_of_birth = date_of_birth
        self._dob_text.setText(self._date_of_birth)

    def time_of_birth(self, time_of_birth):
        """
        Sets the time of birth.
        Format: HH:MM:SS
        """
        self._time_of_birth = time_of_birth
        self._tob_text.setText(self._time_of_birth)

    def language(self, language):
        """
        Sets the language for display.
        """
        if language in available_languages:
            self._language = language
            self._lang_combo.setCurrentText(language)

    # -----------------------------------------------------------------
    # Validation and compute
    # -----------------------------------------------------------------

    def _validate_ui(self):
        all_data_ok = (
            self._place_text.text().strip() != '' and
            self._name_text.text().strip() != '' and
            re.match(r"[\+|\-]?\d+\.\d+\s?", self._lat_text.text().strip(), re.IGNORECASE) and
            re.match(r"[\+|\-]?\d+\.\d+\s?", self._long_text.text().strip(), re.IGNORECASE) and
            re.match(r"[\+|\-]?\d{1,4}\,\d{1,2}\,\d{1,2}", self._dob_text.text().strip(), re.IGNORECASE) and
            re.match(r"\d{1,2}:\d{1,2}:\d{1,2}", self._tob_text.text().strip(), re.IGNORECASE)
        )
        return all_data_ok

    def compute_horoscope(self):
        """
        Compute the horoscope based on details entered.
        If details are missing, error is displayed/printed.
        """
        if not self._validate_ui():
            print('values are not filled properly')
            return False

        self._place_name = self._place_text.text()
        self._latitude = float(self._lat_text.text())
        self._longitude = float(self._long_text.text())
        self._time_zone = float(self._tz_text.text())

        self._language = list(available_languages.keys())[self._lang_combo.currentIndex()]
        self._date_of_birth = self._dob_text.text()
        self._time_of_birth = self._tob_text.text()

        if self._place_name.strip() == "":
            print("Please enter a place of birth")
            return False

        if utils.astro_engine_is_drik(): self._ayanamsa_mode = self._ayanamsa_combo.currentText()
        year, month, day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year), int(month), int(day))

        # Store selected chart type as enum/key.
        self._chart_type = self._selected_chart_type_from_combo()

        # Recreate chart widgets using selected chart class/options.
        self._create_chart_ui()

        if (
            self._place_name.strip() != '' and
            abs(self._latitude) > 0.0 and
            abs(self._longitude) > 0.0 and
            abs(self._time_zone) > 0.0
        ):
            self._horo = info.Horoscope(
                latitude=self._latitude,
                longitude=self._longitude,
                timezone_offset=self._time_zone,
                date_in=birth_date,
                birth_time=self._time_of_birth,
                calculation_type=self._calculation_type,
                language=available_languages[self._language]
            )
        else:
            self._horo = info.Horoscope(
                place_with_country_code=self._place_name,
                date_in=birth_date,
                birth_time=self._time_of_birth,
                calculation_type=self._calculation_type,
                language=available_languages[self._language]
            )

        self._calendar_info = self._horo.calendar_info
        self._calendar_key_list = self._horo._get_calendar_resource_strings()

        self._horoscope_info = []
        self._horoscope_charts = []
        self._vimsottari_dhasa_bhukti_info = []

        self._horoscope_info, self._horoscope_charts, self._ascendant_houses = self._horo.get_horoscope_information()
        _dob = self._horo.Date
        _tob = self._horo.birth_time
        _place = self._horo.Place
        self._vimsottari_dhasa_bhukthi_info = self._horo._get_vimsottari_dhasa_bhukthi(
            _dob,
            _tob,
            _place
        )

        self._update_chart_ui_with_info()
        return True

    # -----------------------------------------------------------------
    # Information labels
    # -----------------------------------------------------------------

    def _fill_information_label1(self, format_str):
        info_str = ''

        key = self._calendar_key_list['udhayathi_str']
        value = utils.udhayadhi_nazhikai(self._horo.julian_day, self._horo.Place)[0]
        info_str += format_str % (key, value)

        key = 'sunrise_str'
        sunrise_time = self._calendar_info[self._calendar_key_list[key]]
        info_str += format_str % (self._calendar_key_list[key], sunrise_time)

        key = 'sunset_str'
        info_str += format_str % (
            self._calendar_key_list[key],
            self._calendar_info[self._calendar_key_list[key]]
        )

        key = 'nakshatra_str'
        info_str += format_str % (
            self._calendar_key_list[key],
            self._calendar_info[self._calendar_key_list[key]]
        )

        key = 'raasi_str'
        info_str += format_str % (
            self._calendar_key_list[key],
            self._calendar_info[self._calendar_key_list[key]]
        )

        key = 'tithi_str'
        info_str += format_str % (
            self._calendar_key_list[key],
            self._calendar_info[self._calendar_key_list[key]]
        )

        key = 'yogam_str'
        info_str += format_str % (
            self._calendar_key_list[key],
            self._calendar_info[self._calendar_key_list[key]]
        )

        key = 'karanam_str'
        info_str += format_str % (
            self._calendar_key_list[key],
            self._calendar_info[self._calendar_key_list[key]]
        )

        key = self._calendar_key_list['raasi_str'] + '-' + self._calendar_key_list['ascendant_str']
        value = self._horoscope_info[key]
        info_str += format_str % (self._calendar_key_list['ascendant_str'], value)

        key = self._calendar_key_list['kali_year_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)

        key = self._calendar_key_list['vikrama_year_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)

        key = self._calendar_key_list['saka_year_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)

        self._info_label1.setText(info_str)

    def _fill_information_label2(self, format_str):
        info_str = ''

        dob = self._horo.Date
        tob = self._horo.birth_time
        place = self._horo.Place

        _vimsottari_dhasa_bhukti_info = self._horo._get_vimsottari_dhasa_bhukthi(
            dob,
            tob,
            place
        )

        _vim_balance = ':'.join(map(str, self._horo._vimsottari_balance))
        dhasa = [k for k, _ in _vimsottari_dhasa_bhukti_info][8].split('-')[0]

        value = _vim_balance
        db_list = []

        key = '&nbsp;&nbsp;' + dhasa + ' ' + self._calendar_key_list['balance_str'] + ' :'
        db_list.append(key + ' ' + value)

        dhasa = ''
        dhasa_end_date = ''
        di = 9

        for p, (k, v) in enumerate(_vimsottari_dhasa_bhukti_info):
            if (p + 1) == di:
                dhasa = '&nbsp;&nbsp;' + k.split("-")[0]
            elif (p + 1) == di + 1:
                """
                To account for BC dates, negative sign is introduced.
                """
                if len(v.split('-')) == 4:
                    _, year, month, day = v.split('-')
                    year = '-' + year
                else:
                    year, month, day = v.split('-')

                dd = day.split(' ')[0]
                dhasa_end_date = (
                    year + '-' +
                    month + '-' +
                    str(int(dd) - 1) +
                    ' ' +
                    self._calendar_key_list['ends_at_str']
                )
                db_list.append(dhasa + ' ' + dhasa_end_date)
                di += 9

        key = self._calendar_key_list['tamil_month_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)
        if utils.astro_engine_is_drik():
            key = self._calendar_key_list['ayanamsam_str'] + ' (' + self._ayanamsa_mode + ') '
            value = drik.get_ayanamsa_value(self._horo.julian_day, place)
            self._ayanamsa_value = value
            value = utils.to_dms(
                value,
                as_string=True,
                is_lat_long='lat'
            ).replace('N', '').replace('S', '')

            info_str += format_str % (key, value)
        key = self._calendar_key_list['lunar_year_month_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)

        key = self._calendar_key_list['vaaram_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)

        key = self._calendar_key_list['calculation_type_str']
        value = self._calendar_info[key]
        info_str += format_str % (key, value)

        self._info_label2.setText(info_str)

    # -----------------------------------------------------------------
    # Chart update
    # -----------------------------------------------------------------

    def _update_chart_ui_with_info(self):
        model = "Surya Sidhantha" if const.astrology_model_default == const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA else "DRIK"
        self._footer_label.setText(self._calendar_key_list['window_footer_title'])
        self.setWindowTitle(self._calendar_key_list['window_title'])

        format_str = '%-20s%-40s\n'
        self._fill_information_label1(format_str)
        self._fill_information_label2(format_str)

        rasi_1d = self._horoscope_charts[0]
        rasi_1d = [x[:-1] for x in rasi_1d]
        asc_house = self._ascendant_houses[0]
        #print('model',model,'rasi chart 1d',rasi_1d,'asc_house',asc_house)
        jd = self._horo.julian_day
        place = drik.Place(
            self._place_name,
            float(self._latitude),
            float(self._longitude),
            float(self._time_zone)
        )

        planet_count = len(drik.planet_list) + 1
        upagraha_count = len(const._solar_upagraha_list) + len(const._other_upagraha_list)
        special_lagna_count = len(const._special_lagna_list)
        total_row_count = planet_count + upagraha_count + special_lagna_count

        _chart_title = (
            self._calendar_key_list['raasi_str'] + '\n' +
            self._date_of_birth + '\n' +
            self._time_of_birth + '\n' +
            self._place_name + '\nGMT ' + str(self._time_zone)
        )
        # ---------------------
        # Rasi chart
        # ---------------------
        asc_house = self._ascendant_houses[0]
        if self._chart_type == const.CHART_STYLE.NORTH_INDIAN:
            rasi_north = rasi_1d[asc_house:] + rasi_1d[0:asc_house]
            self._table1.setData(rasi_north)
            self._table1.update()

        elif self._chart_type in _EAST_INDIAN_STYLES:
            rasi_2d = _convert_1d_house_data_to_2d(rasi_1d, self._chart_type)
            row,col = const.south_indian_regular_chart_2d_map[asc_house]
            self._table1._asc_house = asc_house
            self._table1.setData(rasi_2d, chart_title=_chart_title)
            self._table1.update()

        elif self._chart_type == const.CHART_STYLE.WESTERN:
            i_start = special_lagna_count
            i_end = i_start + planet_count

            data = []
            for k, v in list(self._horoscope_info.items())[i_start:i_end]:
                k1 = k.split('-')[-1]
                v1 = v.split('-')[0]
                data.append(k1 + ' ' + v1)

            self._table1.setData(data, chart_title=_chart_title)
            self._table1.update()

        elif self._chart_type == const.CHART_STYLE.SUDARSANA_CHAKRA:
            chart_1d = sudharsana_chakra.sudharshana_chakra_chart(
                jd,
                place,
                self._date_of_birth
            )
            data_1d = self._convert_1d_chart_with_planet_names(chart_1d)
            self._table1.setData(data_1d)
            self._table1.update()
        else: # south indian regular / irregular
            if self._chart_type == const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR:
                south_chart_type = const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR
                south_chart_map = const.south_indian_irregular_chart_2d_map
            else:
                south_chart_type = const.CHART_STYLE.SOUTH_INDIAN_REGULAR
                south_chart_map = const.south_indian_regular_chart_2d_map
        
            rasi_2d = utils._convert_1d_house_data_to_2d(
                rasi_1d,
                chart_type=south_chart_type
            )
            row, col = south_chart_map[asc_house]
            self._table1._asc_house = (row, col)
            self._table1.setData(rasi_2d, chart_title=_chart_title)
            self._table1.update()
        # ---------------------
        # Navamsa chart
        # ---------------------
        nava_1d = self._horoscope_charts[1]
        nava_1d = [x[:-1] for x in nava_1d]
        asc_house = self._ascendant_houses[1]
        #print('model',model,'navamsa chart 1d',nava_1d,'asc_house',asc_house)
        
        _chart_title = (
            self._calendar_key_list['navamsam_str'] + '\n' +
            self._date_of_birth + '\n' +
            self._time_of_birth + '\n' +
            self._place_name + '\nGMT ' + str(self._time_zone)
        )

        if self._chart_type == const.CHART_STYLE.NORTH_INDIAN:
            nava_north = nava_1d[asc_house:] + nava_1d[0:asc_house]
            self._table2.setData(nava_north)
            self._table2.update()

        elif self._chart_type in _EAST_INDIAN_STYLES:
            nava_2d = _convert_1d_house_data_to_2d(nava_1d, self._chart_type)
            row,col = const.south_indian_regular_chart_2d_map[asc_house]
            self._table2._asc_house = asc_house
            self._table2.setData(nava_2d, chart_title=_chart_title)
            self._table2.update()

        elif self._chart_type == const.CHART_STYLE.WESTERN:
            chart_counter = 8
            i_start = chart_counter * total_row_count + special_lagna_count
            i_end = i_start + planet_count

            data = []
            for k, v in list(self._horoscope_info.items())[i_start:i_end]:
                k1 = k.split('-')[-1]
                v1 = v.split('-')[0]
                data.append(k1 + ' ' + v1)

            self._table2.setData(data, chart_title=_chart_title)
            self._table2.update()

        elif self._chart_type == const.CHART_STYLE.SUDARSANA_CHAKRA:
            chart_1d = sudharsana_chakra.sudharshana_chakra_chart(
                jd,
                place,
                self._date_of_birth,
                years_from_dob=0,
                divisional_chart_factor=9
            )
            data_1d = self._convert_1d_chart_with_planet_names(chart_1d)
            self._table2.setData(data_1d)
            self._table2.update()

        else: # south indian regular / irregular
            if self._chart_type == const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR:
                south_chart_type = const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR
                south_chart_map = const.south_indian_irregular_chart_2d_map
            else:
                south_chart_type = const.CHART_STYLE.SOUTH_INDIAN_REGULAR
                south_chart_map = const.south_indian_regular_chart_2d_map

        
            nava_2d = utils._convert_1d_house_data_to_2d(
                nava_1d,
                chart_type=south_chart_type
            )
            row, col = south_chart_map[asc_house]
            self._table2._asc_house = (row, col)
            self._table2.setData(nava_2d, chart_title=_chart_title)
            self._table2.update()
    # -----------------------------------------------------------------
    # Save PDF
    # -----------------------------------------------------------------

    def save_as_pdf(self):
        """
        Save the displayed chart as a PDF.
        Choose a file from file save dialog displayed.
        """
        path = QFileDialog.getSaveFileName(
            self,
            'Choose folder and file to save as PDF file',
            './output',
            'PDF files (*.pdf)'
        )
        pdf_file = path[0]
        image_file = "./main_window.png"

        if pdf_file:
            im = self.grab()
            im.save(image_file)

            with open(pdf_file, "wb") as f:
                f.write(img2pdf.convert(image_file))

        if os.path.exists(image_file):
            os.remove(image_file)

    def _convert_1d_chart_with_planet_names(self, chart_1d_list):
        """
        To be used for Sudarsana Chakra data as input.
        """
        result = []
        retrograde_planets = chart_1d_list[-1]

        for chart_1d in chart_1d_list[:-1]:
            res = []

            for z, pls in chart_1d:
                pl_str = ''
                tmp = pls.split('/')

                if len(tmp) == 1 and tmp[0] == '':
                    pl_str = ''
                    res.append((z, pl_str))
                    continue

                for p in tmp:
                    if p == const._ascendant_symbol:
                        pl_str += self._calendar_key_list['ascendant_short_str'] + '/'
                    else:
                        ret_str = ''
                        if int(p) in retrograde_planets:
                            ret_str = const._retrogade_symbol

                        pl_str += utils.PLANET_SHORT_NAMES[int(p)] + ret_str + '/'

                pl_str = pl_str[:-1]
                res.append((z, pl_str))

            result.append(res)

        return result


def show_horoscope(data):
    """
    Same as class method show() to display the horoscope.

    @param data:
        Last chance to pass the data to the class.
    """
    app = QApplication(sys.argv)
    window = ChartSimple(data)
    window.show()
    app.exec()


def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1


def _convert_1d_house_data_to_2d(rasi_1d, chart_type=const.CHART_STYLE.SOUTH_INDIAN_REGULAR):
    separator = '/'
    chart_type = _normalize_chart_type(chart_type)

    if chart_type in _SOUTH_INDIAN_STYLES:
        row_count = 4
        col_count = 4

        # Same data mapping for both South Indian visual variants.
        # SouthIndianChart(chart_style_irregular=True/False) handles drawing.
        map_to_2d = [
            [11, 0, 1, 2],
            [10, "", "", 3],
            [9, "", "", 4],
            [8, 7, 6, 5]
        ]

    elif chart_type in _EAST_INDIAN_STYLES:
        row_count = 3
        col_count = 3

        # Same data mapping for East Indian with frame and no-frame.
        # EastIndianChart(draw_frames=True/False) handles border drawing.
        map_to_2d = [
            ['2' + separator + '1', '0', '11' + separator + '10'],
            ['3', "", '9'],
            ['4' + separator + '5', '6', '7' + separator + '8']
        ]

    else:
        row_count = 4
        col_count = 4
        map_to_2d = [
            [11, 0, 1, 2],
            [10, "", "", 3],
            [9, "", "", 4],
            [8, 7, 6, 5]
        ]

    rasi_2d = [['X'] * col_count for _ in range(row_count)]

    for p, val in enumerate(rasi_1d):
        for index, row in enumerate(map_to_2d):
            if chart_type in _SOUTH_INDIAN_STYLES:
                if p in row:
                    i, j = [
                        (index, row.index(p))
                        for index, row in enumerate(map_to_2d)
                        if p in row
                    ][0]
                    rasi_2d[i][j] = val

            elif chart_type in _EAST_INDIAN_STYLES:
                p_index = _index_containing_substring(row, str(p))

                if p_index != -1:
                    i, j = index, p_index

                    if rasi_2d[i][j] != 'X':
                        if index > 0:
                            rasi_2d[i][j] += separator + val
                        else:
                            rasi_2d[i][j] = val + separator + rasi_2d[i][j]
                    else:
                        rasi_2d[i][j] = val

    for i in range(row_count):
        for j in range(col_count):
            if rasi_2d[i][j] == 'X':
                rasi_2d[i][j] = ''

    return rasi_2d


def _get_date_difference(then, now=datetime.now(), interval="default"):
    from dateutil import relativedelta

    diff = relativedelta.relativedelta(now, then)
    years = abs(diff.years)
    months = abs(diff.months)
    days = abs(diff.days)

    return [years, months, days]


def _dhasa_balance(date_of_birth, dhasa_end_date):
    d_arr = date_of_birth.split('-')

    if len(d_arr) == 4:
        _, year, month, day = d_arr
    else:
        year, month, day = d_arr

    dob = datetime(abs(int(year)), int(month), int(day))

    d_arr = dhasa_end_date.split('-')

    if len(d_arr) == 4:
        _, year, month, day = d_arr
    else:
        year, month, day = d_arr

    ded = datetime(abs(int(year)), int(month), int(day))
    duration = _get_date_difference(dob, ded)

    return duration


if __name__ == "__main__":
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)

    sys.excepthook = except_hook

    App = QApplication(sys.argv)

    # Examples:
    #
    # chart_type = const.CHART_STYLE.SOUTH_INDIAN_REGULAR
    # chart_type = const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR
    # chart_type = const.CHART_STYLE.NORTH_INDIAN
    # chart_type = const.CHART_STYLE.EAST_INDIAN_WITH_FRAME
    # chart_type = const.CHART_STYLE.EAST_INDIAN_NO_FRAME
    # chart_type = const.CHART_STYLE.WESTERN
    # chart_type = const.CHART_STYLE.SUDARSANA_CHAKRA
    #
    # Old string values also still work:
    # chart_type = 'South Indian'
    # chart_type = 'South Indian Anti-clockwise'
    # chart_type = 'East Indian No Frame'

    const.astrology_model_default = const.ASTROLOGY_MODELS.KHANDA_KHAADYAKA
    chart_type = const.CHART_STYLE.SOUTH_INDIAN_REGULAR

    chart = ChartSimple(chart_type=chart_type)
    chart.language('English')
    chart.name('Today')

    #"""
    chart.place('Chennai, India', 13.0878, 80.2785, 5.5)
    chart.date_of_birth('1996,12,7')
    chart.time_of_birth('10:34:00')
    #"""
    chart.chart_type(chart_type)
    chart.compute_horoscope()
    chart.show()

    sys.exit(App.exec())