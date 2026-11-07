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
import os
import math
from enum import Enum
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont, QPainter, QAction, QColor, QPen
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication, QMenu, QDialog, QLabel, QCheckBox, \
                            QRadioButton, QSpinBox, QHBoxLayout, QVBoxLayout, QButtonGroup, QPushButton
from PyQt6.QtCore import Qt

from jhora import const,utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

color_label = lambda label,color: '<span style=color:'+color+';>'+label+'</span>'
_rasi_color = 'Red'; _planet_color = 'Brown'; _text_color='Green'; _arudha_color = 'Blue'
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
_lagnam_line_factor = 0.3
_lagnam_line_thickness = 3
_image_path = os.path.abspath(const._IMAGES_PATH)
_zodiac_icons = ['mesham.jpg','rishabham.jpg','mithunam.jpg','katakam.jpg','simmam.jpg','kanni.jpg','thulam.jpg','vrichigam.jpg','dhanusu.jpg','makaram.jpg','kumbam.jpg','meenam.jpg']

""" Helper Functions """

def _clone_chart_data(data):
    import copy
    """
    Safely clone chart data so backup data is not modified later by reference.
    """
    return copy.deepcopy(data)
def _fit_table_widgets_to_contents(tableWidgets):
    for table in tableWidgets:
        for row in range(table.rowCount()):
            table.resizeRowToContents(row)
            for col in range(table.columnCount()):
                table.resizeColumnToContents(col)
def _restore_original_chart_after_prasna_if_needed(chart_widget):
    """
    Restore original chart data and ascendant after Prasna Lagna replacement.

    This removes Ascendant(PrL), restores original Ascendant text,
    and restores the original ascendant marker position.
    """
    if getattr(chart_widget, '_data_counter', 0) <= 0:
        return False

    if not hasattr(chart_widget, '_data_original'):
        return False

    if not hasattr(chart_widget, '_asc_house_original'):
        return False

    restored_data = _clone_chart_data(chart_widget._data_original)

    chart_widget.data = restored_data
    chart_widget._asc_house = chart_widget._asc_house_original

    chart_widget._data_counter = 0

    return True

def replace_ascendant_with_prasna_lagna(planet_list, prasna_list, chart_type=None):
    if chart_type is None:
        chart_type = const.default_chart_type

    plag = utils.resource_strings['prasna_lagna_short_str']
    lagna = utils.resource_strings['ascendant_str']
    new_lagna = lagna + '(' + plag + ')'

    if chart_type in const._SOUTH_EAST_TYPES:
        prasna_2d = utils._convert_1d_house_data_to_2d(
            prasna_list,
            chart_type=chart_type
        )

        rp, cp = utils.get_2d_list_index(
            prasna_2d,
            plag,
            contains_in_element=True
        )

        # Remove Prasna Lagna marker from overlay list.
        prasna_list = [ele.replace(plag, '') for ele in prasna_list]

        # Work on a copy, not the original list reference.
        planet_list = [
            [ele.replace(lagna, '') for ele in row]
            for row in planet_list
        ]

        if planet_list[rp][cp] != '':
            planet_list[rp][cp] = new_lagna + '\n' + planet_list[rp][cp]
        else:
            planet_list[rp][cp] = new_lagna

        asc_house = (rp, cp)

        return planet_list, prasna_list, asc_house

    elif chart_type in const.CHART_STYLE.NORTH_INDIAN:

        rp = utils.get_1d_list_index(
            prasna_list,
            plag,
            contains_in_element=True
        )

        planet_list = [
            ele.replace(lagna, '')
            for ele in planet_list
        ]

        prasna_list = [
            ele.replace(plag, '')
            for ele in prasna_list
        ]

        if planet_list[rp] != '':
            planet_list[rp] = new_lagna + '\n' + planet_list[rp]
        else:
            planet_list[rp] = new_lagna

        asc_house = rp

        return planet_list, prasna_list, asc_house
    
def _build_popup_widget_registry_from_legacy_arguments(
         drishti_table_widgets=None,
         planet_info_widgets=None,
         aspect_widgets=None,
         ndl_22_widgets=None,
         ndl_64_widgets=None,
         graha_drekkana_widgets=None,
         nava_thaara_widgets=None,
         spl_thaara_widgets=None):
     """
     Build one generic popup-widget registry from the existing legacy widget arguments.
 
     This is Patch-1 only:
     - keeps existing setData(...) signature stable
     - allows popup widget features to be driven generically
     """
     return {
         'drishti': drishti_table_widgets,
         'planet_info': planet_info_widgets,
         'aspect': aspect_widgets,
         'ndl_22': ndl_22_widgets,
         'ndl_64': ndl_64_widgets,
         'graha_drekkana': graha_drekkana_widgets,
         'nava_thaara': nava_thaara_widgets,
         'special_thaara': spl_thaara_widgets,
     }

def _invoke_popup_widget_menu(chart_widget, action_data):
    """
    Generic popup-widget dispatcher.

    Expected tuple format:
        (
            Chart.Action.PopupWidget,
            popup_id,
            widget_index,              # int or None
            title,
            fit_to_widget_contents,    # bool
            resize_table_to_contents   # bool
        )

    Notes:
    - widget_index = None means show the full widget list for that popup_id
    - widget_index = int means show only that indexed widget
    """
    if not isinstance(action_data, tuple):
        return False

    if len(action_data) < 6:
        return False

    if action_data[0] != Chart.Action.PopupWidget:
        return False

    popup_id = action_data[1]
    widget_index = action_data[2]
    title = action_data[3]
    fit_to_widget_contents = action_data[4]
    resize_table_to_contents = action_data[5]

    if not hasattr(chart_widget, '_popup_widget_registry') or chart_widget._popup_widget_registry is None:
        return False

    widget_list = chart_widget._popup_widget_registry.get(popup_id)
    if widget_list is None:
        return False

    if widget_index is None:
        h_widgets = widget_list
        cache_key = (Chart.Action.PopupWidget, popup_id, 'all')
    else:
        if widget_index < 0 or widget_index >= len(widget_list):
            return False
        h_widgets = [widget_list[widget_index]]
        cache_key = (Chart.Action.PopupWidget, popup_id, widget_index)

    if resize_table_to_contents:
        _fit_table_widgets_to_contents(widget_list)

    if not hasattr(chart_widget, '_popup_widget_dialog_cache') or chart_widget._popup_widget_dialog_cache is None:
        chart_widget._popup_widget_dialog_cache = {}

    from jhora.ui.options_dialog import WidgetDialog

    if cache_key not in chart_widget._popup_widget_dialog_cache:
        chart_widget._popup_widget_dialog_cache[cache_key] = WidgetDialog(
            title=title,
            h_widgets=h_widgets,
            fit_to_widget_contents=fit_to_widget_contents
        )

    chart_widget._popup_widget_dialog_cache[cache_key].exec()
    return True

def _invoke_popup_info_menu(chart_widget, action_data):
    """
    Generic popup-info dispatcher.

    Expected tuple format:
        (
            Chart.Action.PopupInfo,
            title,
            info_text
        )
    """
    if not isinstance(action_data, tuple):
        return False

    if len(action_data) < 3:
        return False

    if action_data[0] != Chart.Action.PopupInfo:
        return False

    title = action_data[1]
    info_text = action_data[2]

    from jhora.ui.options_dialog import InfoDialog

    info_dialog = InfoDialog(
        title=title,
        info_text=info_text,
        button_texts=[utils.resource_strings['accept_str']]
    )
    info_dialog.exec()
    return True

def _invoke_show_in_chart_cells_menu(chart_widget, action_data, chart_type):
    """
    Generic in-chart-cell overlay dispatcher.

    Expected tuple format:
        (
            Chart.Action.ShowInChartCells,
            overlay_data_1d
        )
    """
    if not isinstance(action_data, tuple):
        return False

    if len(action_data) < 2:
        return False

    if action_data[0] != Chart.Action.ShowInChartCells:
        return False
    overlay_data_1d = action_data[1]
    if chart_type in const._SOUTH_EAST_TYPES:
        overlay_data = utils._convert_1d_house_data_to_2d(
            overlay_data_1d,
            chart_type
        )
    else:
        overlay_data = overlay_data_1d
    _restore_original_chart_after_prasna_if_needed(chart_widget)
    chart_widget.setData(
        data=chart_widget.data,
        arudha_lagna_data=overlay_data,
        chart_title=chart_widget._chart_title,
        chart_title_font_size=chart_widget._chart_title_font_size
    )
    chart_widget.update()
    return True

def _invoke_reset_chart_cells_menu(chart_widget, action_data, chart_type):
    """
    Generic reset/default-chart dispatcher.
    """
    if not isinstance(action_data, tuple):
        return False

    if len(action_data) < 1:
        return False

    if action_data[0] != Chart.Action.ResetChartCells:
        return False
    try:
        restored_data = _clone_chart_data(chart_widget._data_original)
    
        chart_widget.data = restored_data
        chart_widget._asc_house = chart_widget._asc_house_original
    
        chart_widget._data_counter = 0
    except Exception:
        pass
    blank_overlay_1d = ['' for _ in range(12)]

    if chart_type in const._SOUTH_EAST_TYPES:
        overlay_data = utils._convert_1d_house_data_to_2d(
            blank_overlay_1d,
            chart_type
        )
    else:
        overlay_data = blank_overlay_1d

    chart_widget.setData(
        data=chart_widget.data,
        arudha_lagna_data=overlay_data,
        chart_title=chart_widget._chart_title,
        chart_title_font_size=chart_widget._chart_title_font_size
    )

    chart_widget.update()
    return True

def _build_chart_menu(chart_widget, menu, data):
    """
    Shared recursive menu builder for South/East/North Indian chart widgets.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            submenu = QMenu(key, chart_widget)
            _build_chart_menu(chart_widget, submenu, value)
            menu.addMenu(submenu)
        else:
            action = QAction(key, chart_widget)
            action.setData(value)
            action.triggered.connect(lambda checked, key=key: chart_widget.set_menu_data(key))
            menu.addAction(action)

def _show_chart_context_menu(chart_widget, pos):
    """
    Shared context-menu launcher for South/East/North Indian chart widgets.
    """
    chart_widget.menu = QMenu(chart_widget)
    _build_chart_menu(chart_widget, chart_widget.menu, chart_widget._menu_dict)
    chart_widget.menu.exec(chart_widget.mapToGlobal(pos))

def _convert_overlay_data_for_chart_type(overlay_data_1d, chart_type):
    """
    Convert 1D overlay data to chart-style-specific format.

    South/East -> 2D
    North      -> 1D
    """
    if chart_type in const._SOUTH_EAST_TYPES:
        return utils._convert_1d_house_data_to_2d(overlay_data_1d, chart_type)
    return overlay_data_1d

def _apply_overlay_to_chart_widget(chart_widget, overlay_data_1d, chart_type):
    """
        Apply overlay data to the chart widget and refresh it.
        
        chart_widget.data is already in the correct display-ready layout.
        Menu overlay data remains 1-D and is converted here using chart_type.
    """
    overlay_data = _convert_overlay_data_for_chart_type(overlay_data_1d, chart_type)

    chart_widget.setData(
        data=chart_widget.data,
        arudha_lagna_data=overlay_data,
        chart_title=chart_widget._chart_title,
        chart_title_font_size=chart_widget._chart_title_font_size
    )
    chart_widget.update()

def _handle_prasna_menu_action(chart_widget, key, chart_type):
    """
    Shared Prasna Lagna handler for South/East/North Indian chart widgets.

    Returns:
        True  -> action handled
        False -> not a Prasna action
    """
    prasna_key = utils.resource_strings['prasna_lagna_str'] + '(' + utils.resource_strings['prasna_lagna_short_str'] + ')'
    if key != prasna_key:
        return False

    ret = show_prasna_dialog(chart_widget._varga_factor)
    if len(ret) == 0:
        return True

    alt_data, replace_lagna = ret

    if replace_lagna:
        chart_widget._data_counter += 1
    
        if chart_widget._data_counter == 1:
            chart_widget._data_original = _clone_chart_data(chart_widget.data)
            chart_widget._asc_house_original = chart_widget._asc_house
    
        new_data, alt_data, new_asc_house = replace_ascendant_with_prasna_lagna(
            _clone_chart_data(chart_widget._data_original),
            alt_data,
            chart_type
        )
    
        chart_widget.data = new_data
        chart_widget._asc_house = new_asc_house
    else:
        lagna = utils.resource_strings['ascendant_str']
        plag = utils.resource_strings['prasna_lagna_short_str']
        chart_widget.data = utils.search_replace(
            chart_widget.data,
            lagna + '(' + plag + ')',
            lagna
        )

    if len(alt_data) > 0:
        action = chart_widget.sender()
        action.setData(alt_data)

    _apply_overlay_to_chart_widget(chart_widget, alt_data, chart_type)
    return True

def _handle_chart_menu_action(chart_widget, key, chart_type):
    """
    Shared menu action dispatcher for South/East/North Indian chart widgets.

    Handles:
    - popup_widget
    - popup_info
    - show_in_chart_cells
    - reset_chart_cells
    - custom Prasna Lagna
    - backward-compatible legacy raw 1D overlay lists
    """
    chart_widget.menu.close()
    action = chart_widget.sender()
    alt_data = action.data()

    if _invoke_popup_widget_menu(chart_widget, alt_data):
        return

    if _invoke_popup_info_menu(chart_widget, alt_data):
        return

    if _invoke_show_in_chart_cells_menu(chart_widget, alt_data, chart_type):
        return

    if _invoke_reset_chart_cells_menu(chart_widget, alt_data, chart_type):
        return

    if isinstance(alt_data, tuple):
        return

    if _handle_prasna_menu_action(chart_widget, key, chart_type):
        return
    
    # If user clicks another menu item after Prasna Lagna replacement,
    # restore original Lagna/chart before applying that menu overlay.
    _restore_original_chart_after_prasna_if_needed(chart_widget)
    
    # Backward-compatible fallback for old raw overlay-list leaves
    _apply_overlay_to_chart_widget(chart_widget, alt_data, chart_type)
    
def _configure_chart_menu_context(chart_widget, menu_dict=None, varga_factor=None,
                                  drishti_table_widgets=None, planet_info_widgets=None, aspect_widgets=None,
                                  ndl_22_widgets=None, ndl_64_widgets=None, graha_drekkana_widgets=None,
                                  nava_thaara_widgets=None, spl_thaara_widgets=None):
    """
    Shared menu/popup context setup for South/East/North Indian chart widgets.

    This keeps the current setData(...) call signature intact while centralizing:
    - menu dict assignment
    - popup registry assignment
    - popup dialog cache reset
    - context-menu signal wiring
    """
    if menu_dict is None:
        return

    chart_widget._menu_dict = menu_dict
    chart_widget._varga_factor = varga_factor

    chart_widget._popup_widget_registry = _build_popup_widget_registry_from_legacy_arguments(
        drishti_table_widgets=drishti_table_widgets,
        planet_info_widgets=planet_info_widgets,
        aspect_widgets=aspect_widgets,
        ndl_22_widgets=ndl_22_widgets,
        ndl_64_widgets=ndl_64_widgets,
        graha_drekkana_widgets=graha_drekkana_widgets,
        nava_thaara_widgets=nava_thaara_widgets,
        spl_thaara_widgets=spl_thaara_widgets
    )

    chart_widget._popup_widget_dialog_cache = {}

    chart_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    try:
        chart_widget.customContextMenuRequested.disconnect(chart_widget.showContextMenu)
    except Exception:
        pass
    chart_widget.customContextMenuRequested.connect(chart_widget.showContextMenu)
    
class PrasnaDialog(QDialog):
    def __init__(self, parent=None,varga_factor=1):
        super().__init__(parent)
        self._varga_factor = varga_factor
        self.setWindowTitle(utils.resource_strings['prasna_lagna_str']+' '+utils.resource_strings['options_str'])

        # Layouts
        main_layout = QVBoxLayout()
        radio_layout = QHBoxLayout()
        spin_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # CheckBox
        self.random_checkbox = QCheckBox(utils.resource_strings['random_number_str'])
        main_layout.addWidget(self.random_checkbox)
        self.random_checkbox.clicked.connect(self.on_random_selection_changed)

        # Radio Buttons
        self.radio_prasna108 = QRadioButton(utils.resource_strings['prasna_lagna_str']+'-108')
        self.radio_prasnakp249 = QRadioButton(utils.resource_strings['prasna_lagna_str']+'KP-249')
        self.radio_prasna_nadi = QRadioButton(utils.resource_strings['naadi_str']+'-1800')
        self.radio_prasna108.setChecked(True)
        
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_prasna108)
        self.radio_group.addButton(self.radio_prasnakp249)
        self.radio_group.addButton(self.radio_prasna_nadi)
        
        radio_layout.addWidget(self.radio_prasna108)
        radio_layout.addWidget(self.radio_prasnakp249)
        radio_layout.addWidget(self.radio_prasna_nadi)
        main_layout.addLayout(radio_layout)

        # SpinBox
        self.spin_box = QSpinBox()
        self._spin_max = 108
        self.spin_box.setRange(1, self._spin_max)
        self._spin_label = QLabel((utils.resource_strings['prasna_label_str']+' (1..'+str(self._spin_max)+')'))
        spin_layout.addWidget(self._spin_label)
        spin_layout.addWidget(self.spin_box)
        main_layout.addLayout(spin_layout)
        # Radio Button change event
        self.radio_group.buttonClicked.connect(self.on_radio_button_changed)
        
        # add lagnam replacement choices
        radio_group1 = QButtonGroup()
        self.keep_lagna_radio_button = QRadioButton(utils.resource_strings['prasna_replace_lagna_label1_str'])
        self.keep_lagna_radio_button.setChecked(True)
        radio_group1.addButton(self.keep_lagna_radio_button)
        main_layout.addWidget(self.keep_lagna_radio_button)
        self.replace_lagna_radio_button = QRadioButton(utils.resource_strings['prasna_replace_lagna_label2_str'])
        radio_group1.addButton(self.replace_lagna_radio_button)
        main_layout.addWidget(self.replace_lagna_radio_button)
        # Individual Accept and Cancel buttons
        self.accept_button = QPushButton(utils.resource_strings['accept_str'])
        self.cancel_button = QPushButton(utils.resource_strings['cancel_str'])

        self.accept_button.clicked.connect(self.accept_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
    def on_random_selection_changed(self):
        import random
        if self.random_checkbox.isChecked():
            r = random.randint(1,self._spin_max)
            self.spin_box.setEnabled(False); self.spin_box.setValue(r)
        else:
            self.spin_box.setEnabled(True)
    def on_radio_button_changed(self):
        import random
        if self.radio_prasna108.isChecked():
            self._spin_max = 108
        elif self.radio_prasnakp249.isChecked():
            self._spin_max = 249
        elif self.radio_prasna_nadi.isChecked():
            self._spin_max = 1800
        self.spin_box.setRange(1,self._spin_max)
        self._spin_label.setText((utils.resource_strings['prasna_label_str']+' (1..'+str(self._spin_max)+')'))
        if self.random_checkbox.isChecked(): self.spin_box.setValue(random.randint(1,self._spin_max))
    def accept_clicked(self):
        kp_no = int(self.spin_box.value())
        if self.radio_prasna108.isChecked():
            plag = utils.get_prasna_lagna_108_for_varga_chart(kp_no,self._varga_factor)
        elif self.radio_prasnakp249.isChecked():
            plag = utils.get_prasna_lagna_KP_249_for_varga_chart(kp_no,self._varga_factor)
        elif self.radio_prasna_nadi.isChecked():
            plag = utils.get_prasna_lagna_nadi_for_varga_chart(kp_no,self._varga_factor)
        self.prasna_lagna = plag
        self.replace_lagna = self.replace_lagna_radio_button.isChecked()
        self.accept()
    def cancel_clicked(self):
        self.reject()
        self.close()
def show_prasna_dialog(varga_factor=1):
    dialog = PrasnaDialog(varga_factor=varga_factor)
    data = ['' for _ in range(12)]
    if dialog.exec() == QDialog.DialogCode.Accepted:
        data [dialog.prasna_lagna]=utils.resource_strings['prasna_lagna_short_str']
    else:
        return []
    return data, dialog.replace_lagna

class Chart(QWidget):
    """
    Common base class for all chart widgets.

    This includes:
    - South Indian chart
    - East Indian chart
    - North Indian chart
    - Western chart
    - Sudarsana Chakra chart
    """
    
    class Style(Enum):
        SouthIndian = const.CHART_STYLE.SOUTH_INDIAN_REGULAR
        NorthIndian = const.CHART_STYLE.NORTH_INDIAN
        EastIndian = const.CHART_STYLE.EAST_INDIAN_WITH_FRAME
        Western = const.CHART_STYLE.WESTERN
        SudarsanaChakra = const.CHART_STYLE.SUDARSANA_CHAKRA

    @classmethod
    def parse_style(cls, value):
        if isinstance(value, cls.Style):
            return value

        if value is None:
            raise ValueError("Chart style cannot be None")

        v = value

        if v in const._SOUTH_CHART_TYPES:
            return cls.Style.SouthIndian
        elif v in const.CHART_STYLE.NORTH_INDIAN:
            return cls.Style.NorthIndian
        elif v in const._EAST_CHART_TYPES:
            return cls.Style.EastIndian
        elif v in const.CHART_STYLE.WESTERN:
            return cls.Style.Western
        elif v in const.CHART_STYLE.SUDARSANA_CHAKRA:
            return cls.Style.SudarsanaChakra

        raise ValueError(f"Not a valid chart style: {value}")

    class Action(Enum):
        PopupWidget = 'popup_widget'
        PopupInfo = 'popup_info'
        ShowInChartCells = 'show_in_chart_cells'
        ResetChartCells = 'reset_chart_cells'

    def __init__(self, style, parent=None):
        super().__init__(parent)
        self.style = self.parse_style(style)
        self.data = None
        self._chart_title = ''
        self._chart_title_font_size = None
        self._data_counter = 0

    def chart_type_name(self):
        return self.style.value

    def _get_chart_rect(self):
        """
        Return chart bounding rectangle as:
            chart_left, chart_top, chart_width, chart_height
    
        Subclasses should override this.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _get_chart_rect()"
        )
    
    
    def _draw_chart_title_below(
            self,
            painter,
            title=None,
            font_size=None,
            title_height=20,
            title_margin=None,
            color=None):
        """
        Draw chart title centered below the chart bounding rectangle.
        """
    
        chart_left, chart_top, chart_width, chart_height = self._get_chart_rect()
    
        if title is None:
            title = getattr(self, '_chart_title', '')
    
        if title is None:
            title = ''
    
        title = str(title).replace('\n', ' ').strip()
    
        if title == '':
            return
    
        if font_size is None:
            font_size = getattr(
                self,
                '_chart_title_font_size',
                getattr(self, 'chart_title_font_size', None)
            )
    
        if title_margin is None:
            title_margin = chart_top
    
        title_rect = QtCore.QRect(
            round(chart_left),
            round(chart_top + chart_height + title_margin),
            round(chart_width),
            round(title_height)
        )
    
        painter.save()
    
        if font_size is not None:
            font = QFont()
            font.setPixelSize(font_size)
            painter.setFont(font)
    
        if color is None:
            color = _text_color
    
        painter.setPen(QColor(color))
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignCenter,
            title
        )
    
        painter.restore()

class KundaliChart(Chart):
    """
    Shared base class for Vedic/Indian kundali chart widgets:

    - SouthIndianChart
    - EastIndianChart
    - NorthIndianChart

    Shared responsibilities:
    - context menu handling
    - recursive menu building
    - generic action dispatch
    - popup widget registry setup
    - shared setData support
    """

    def __init__(self, style, parent=None):
        super().__init__(style, parent)

        self._menu_dict = {}
        self._popup_widget_registry = {}
        self._popup_widget_dialog_cache = {}
        self._varga_factor = 1

        self.arudha_lagna_data = None

    def showContextMenu(self, pos):
        _show_chart_context_menu(self, pos)

    def build_menu(self, menu, data):
        _build_chart_menu(self, menu, data)

    def set_menu_data(self, key):
        _handle_chart_menu_action(self, key, self.chart_type_name())

    def _draw_center_icon(
            self,
            painter,
            icon_file='lord_ganesha1.jpg',
            icon_size_factor=0.18,
            min_icon_size=32,
            max_icon_size=None):
        """
        Draw deity/icon centered in the chart bounding rectangle.
    
        This is useful now that chart titles are drawn below the chart.
        Works for South/East/North Indian chart widgets that implement
        _get_chart_rect().
        """
    
        chart_left, chart_top, chart_width, chart_height = self._get_chart_rect()
    
        icon_size = round(min(chart_width, chart_height) * icon_size_factor)
    
        if max_icon_size is not None:
            icon_size = min(icon_size, max_icon_size)
    
        icon_size = max(icon_size, min_icon_size)
    
        icon_x = round(chart_left + (chart_width - icon_size) / 2)
        icon_y = round(chart_top + (chart_height - icon_size) / 2)
    
        icon_rect = QtCore.QRect(
            icon_x,
            icon_y,
            icon_size,
            icon_size
        )
    
        icon = QPixmap(_image_path + '//' + icon_file)
    
        if not icon.isNull():
            painter.drawPixmap(icon_rect, icon)

    def _get_chart_rect(self):
        return (
            self.x,
            self.y,
            self.house_width,
            self.house_height
        )

    def _draw_kundali_chart_title_below(
            self,
            painter,
            chart_width,
            chart_height,
            title_height=20):
        """
        Draw title below a South/East/North Indian chart.
        """
        self._draw_chart_title_below(
            painter=painter,
            chart_left=self.x,
            chart_top=self.y,
            chart_width=chart_width,
            chart_height=chart_height,
            title_height=title_height
        )

    def _set_kundali_data(self, data, chart_title='', chart_title_font_size=None, arudha_lagna_data=None,
                          menu_dict=None, varga_factor=None, drishti_table_widgets=None,
                          planet_info_widgets=None, aspect_widgets=None,
                          ndl_22_widgets=None, ndl_64_widgets=None,
                          graha_drekkana_widgets=None, nava_thaara_widgets=None,
                          spl_thaara_widgets=None, default_chart_title_font_size=None):
        """
        Shared setData implementation for Indian kundali chart widgets.
        """
        _configure_chart_menu_context(
            self,
            menu_dict=menu_dict,
            varga_factor=varga_factor,
            drishti_table_widgets=drishti_table_widgets,
            planet_info_widgets=planet_info_widgets,
            aspect_widgets=aspect_widgets,
            ndl_22_widgets=ndl_22_widgets,
            ndl_64_widgets=ndl_64_widgets,
            graha_drekkana_widgets=graha_drekkana_widgets,
            nava_thaara_widgets=nava_thaara_widgets,
            spl_thaara_widgets=spl_thaara_widgets
        )

        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
        self._chart_title = chart_title

        if default_chart_title_font_size is None:
            self._chart_title_font_size = chart_title_font_size
        else:
            self._chart_title_font_size = default_chart_title_font_size if chart_title_font_size is None else chart_title_font_size
        
class SudarsanaChakraChart(Chart):
    """
        Sudarsana Chakra Chart 
    """
    def __init__(self, data=None, chart_center_pos: tuple = (175, 175), chart_radii: tuple = (75, 125, 175),
                 chart_inner_square: tuple = (30, 30), label_font_size: int = 8, chart_label_radius_factor: float = 0.15,
                 chart_size_factor: float = 1.0, chart_title_font_size=9, chart_title=''):
        Chart.__init__(self, Chart.Style.SudarsanaChakra)
    
        self._chart_title = chart_title
        self.sc_chart_radius_1 = int(chart_radii[0] * chart_size_factor)
        self.sc_chart_radius_2 = int(chart_radii[1] * chart_size_factor)
        self.sc_chart_radius_3 = int(chart_radii[2] * chart_size_factor)
        self.sc_inner_square_width = int(chart_inner_square[0] * chart_size_factor)
        self.sc_inner_square_height = int(chart_inner_square[1] * chart_size_factor)
        self.sc_chart_center_x = int(chart_center_pos[0] * chart_size_factor)
        self.sc_chart_center_y = int(chart_center_pos[1] * chart_size_factor)
        self.sc_label_font_size = label_font_size
        self._sc_label_radius_factor = chart_label_radius_factor
        self.chart_title_font_size = chart_title_font_size
    
        if data is None:
            data = [
                ['L', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Mandhi', ''],
                ['L', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Mandhi', ''],
                ['L', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Mandhi', '']
            ]
        self.data = data

    def paintEvent(self, event):
        self._draw_sudarsana_chakra_chart()

    def _get_chart_rect(self):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        r = self.sc_chart_radius_3
    
        return (
            cx - r,
            cy - r,
            2 * r,
            2 * r
        )
        
    def setData(self,data,chart_title='',chart_title_font_size=9):
        self.data = data
        self._chart_title = chart_title
        self.chart_title_font_size = chart_title_font_size

    def _draw_sc_basic_chart(self, painter):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        center = QtCore.QPoint(cx, cy)
    
        painter.drawEllipse(center, self.sc_chart_radius_1, self.sc_chart_radius_1)
        painter.drawEllipse(center, self.sc_chart_radius_2, self.sc_chart_radius_2)
        painter.drawEllipse(center, self.sc_chart_radius_3, self.sc_chart_radius_3)
    
        sw = self.sc_inner_square_width
        sh = self.sc_inner_square_height
        r = self.sc_chart_radius_3
    
        a = int(math.sqrt(r * r - 0.25 * sh * sh))
        b = int(math.sqrt(r * r - 0.25 * sw * sw))
    
        painter.drawLine(QtCore.QLine(cx + int(0.5 * sw), cy - b, cx + int(0.5 * sw), cy + b))
        painter.drawLine(QtCore.QLine(cx - int(0.5 * sw), cy - b, cx - int(0.5 * sw), cy + b))
        painter.drawLine(QtCore.QLine(cx - a, cy - int(0.5 * sh), cx + a, cy - int(0.5 * sh)))
        painter.drawLine(QtCore.QLine(cx - a, cy + int(0.5 * sh), cx + a, cy + int(0.5 * sh)))
    
        r2 = int(r / math.sqrt(2))
    
        painter.drawLine(QtCore.QLine(cx - int(0.5 * sw), cy - int(0.5 * sh), cx - r2, cy - r2))
        painter.drawLine(QtCore.QLine(cx + int(0.5 * sw), cy - int(0.5 * sh), cx + r2, cy - r2))
        painter.drawLine(QtCore.QLine(cx + int(0.5 * sw), cy + int(0.5 * sh), cx + r2, cy + r2))
        painter.drawLine(QtCore.QLine(cx - int(0.5 * sw), cy + int(0.5 * sh), cx - r2, cy + r2))
    
        ix = cx - int(0.5 * sw)
        iy = cy - int(0.5 * sh)
        icon = QPixmap(_image_path + '//aum_small.jpg')
        image_rect = QtCore.QRect(ix, iy, sw, sh)
        painter.drawPixmap(image_rect, icon)
    
        pi_value = 180.0
        t = math.asin(0.5 * sh / self.sc_chart_radius_3) * pi_value / math.pi
    
        t_list = [
            -t, t,
            0.25 * pi_value,
            0.5 * pi_value - t,
            0.5 * pi_value + t,
            0.75 * pi_value,
            pi_value - t,
            pi_value + t,
            1.25 * pi_value,
            1.5 * pi_value - t,
            1.5 * pi_value + t,
            1.75 * pi_value,
            2 * pi_value - t,
            2 * pi_value + t
        ]
    
        font = QFont()
        font.setPixelSize(12)
        painter.setFont(font)
    
        painter.save()
        painter.translate(cx, cy)
    
        for z in range(12):
            angle = 0.5 * (t_list[z] + t_list[z + 1])
            rad = self.sc_chart_radius_3
            self.drawNode(painter, angle, rad, str(z + 1))
    
        painter.restore()
        painter.setFont(QFont())

    def _draw_sudarsana_chakra_chart(self):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        sw = self.sc_inner_square_width
        sh = self.sc_inner_square_height
    
        painter = QPainter(self)
    
        self._draw_sc_basic_chart(painter)
    
        r_sq = math.sqrt(sw * sw + sh * sh)
        pi_value = 180.0
    
        r_list = [
            r_sq,
            self.sc_chart_radius_1,
            self.sc_chart_radius_2,
            self.sc_chart_radius_3
        ]
    
        painter.save()
        painter.translate(cx, cy)
    
        for i, r in enumerate(r_list[:-1]):
            data_1d = self.data[i]
            r1 = r_list[i]
            r2 = r_list[i + 1]
    
            pr = r1 + self._sc_label_radius_factor * (r2 - r1)
    
            t = math.asin(0.5 * sh / r2) * pi_value / math.pi
    
            t_list = [
                -t, t,
                0.25 * pi_value,
                0.5 * pi_value - t,
                0.5 * pi_value + t,
                0.75 * pi_value,
                pi_value - t,
                pi_value + t,
                1.25 * pi_value,
                1.5 * pi_value - t,
                1.5 * pi_value + t,
                1.75 * pi_value,
                2 * pi_value - t,
                2 * pi_value + t
            ]
    
            for i_z in range(12):
                t1 = t_list[i_z]
                t2 = t_list[i_z + 1]
                self._write_planets_inside_houses(
                    painter,
                    pr,
                    t1,
                    t2,
                    data_1d[i_z],
                    i_z
                )
    
        painter.restore()
    
        self._draw_chart_title_below(
            painter=painter,
            font_size=self.chart_title_font_size
        )
    
        painter.end()
    
    def drawNode(self,painter, angle, radius, text):
        #print('angle, radius, text',angle, radius, text)
        size = 32767.0
        painter.save()
        painter.rotate(-angle)
        painter.translate(radius, 0)
        painter.drawText(QtCore.QRectF(0, -size/2.0, size, size), Qt.AlignmentFlag.AlignVCenter, text.strip())
        painter.restore()
    def _write_planets_inside_houses(self,painter,pr,t1,t2,data,i_z):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        z,pls = data
        planets = pls.split('/')
        p_len = len(planets)
        if planets[0] == '':
            p_len = 0
        pc = p_len+1
        tinc = (t2-t1)/(pc+1)
        th = 40
        tw = 40
        # First write zodiac symbol
        pt = t2-tinc
        tx = int(cx+pr*math.cos(pt))
        ty = int(cy - pr*math.sin(pt))
        trect = QtCore.QRect(tx,ty,tw,th)
        font = QFont()
        font.setPixelSize(self.sc_label_font_size)
        painter.setFont(font)
        painter.setPen(QColor(_rasi_color))
        self.drawNode(painter,pt,pr,const._zodiac_symbols[z])
        painter.setPen(QPen())
        if p_len == 0:
            return
        painter.setPen(QColor(_planet_color))
        for p in planets:
            pt -= tinc
            tx = int(cx+pr*math.cos(pt))
            ty = int(cy - pr*math.sin(pt))
            trect = QtCore.QRect(tx,ty,tw,th)
            self.drawNode(painter,pt,pr,p)
        painter.setPen(QPen())
        painter.setFont(QFont())
    def _write_planets_inside_houses_1(self,painter,radius,data,i_z):
        cx = self.sc_chart_center_x
        cy = self.sc_chart_center_y
        z,pls = data
        data_text = const._zodiac_symbols[z]+'\n'+pls
        ri = 0.7
        font = QFont()
        font.setPixelSize(self.sc_label_font_size)
        painter.setFont(font)
        a = ((i_z*30.0)+0)*math.pi/180.0             
        rect = QtCore.QRect(int(cx+radius*ri*math.cos(a)),int(cy-radius*ri*math.sin(a)),40,40)
        painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,data_text.strip())
        painter.setFont(QFont()) # reset font
               
        
class WesternChart(Chart):
    """
        Western Chart
        @param data=one-dimensional array of longitudes of planets in houses
        Example: [Sun_Long/Moon_long, '',Mars_long,'', ...'Lagnam_long',...,'']
        @param chart_center_pos = (x,y) tuple coordinates of chart center
        @param chart_radii: list of radius lengths of four circles of the chart 
        @param label_font_size: font size of labels: default: _west_label_font_size
        @param label_pos_radial_increment: position of labels in radial increment: default: _west_radial_increment
        
    """
    _west_chart_radius_1 = 30
    _west_chart_radius_2 = 110
    _west_chart_radius_3 = 130
    _west_chart_radius_4 = 150
    _west_radial_increment = 15
    _west_chart_center_x = 150
    _west_chart_center_y = 150
    _west_label_font_size = 8
    _west_chart_title_font_size = 9
    def __init__(self, data=None, chart_center_pos: tuple = (_west_chart_center_x, _west_chart_center_y),
                 chart_radii: tuple = (_west_chart_radius_1, _west_chart_radius_2, _west_chart_radius_3, _west_chart_radius_4),
                 label_font_size=_west_label_font_size, label_pos_radial_increment=_west_radial_increment,
                 chart_size_factor: float = 1.0, chart_title_font_size=_west_chart_title_font_size,
                 chart_title=''):
        Chart.__init__(self, Chart.Style.Western)
    
        self._chart_title = chart_title
        self._chart_center_pos = tuple([int(x * chart_size_factor) for x in chart_center_pos])
        self._chart_radii = tuple([int(x * chart_size_factor) for x in chart_radii])
        self._label_font_size = label_font_size
        self._label_pos_radial_increment = label_pos_radial_increment * chart_size_factor
        self._chart_size_factor = chart_size_factor
        self.chart_title_font_size = chart_title_font_size
        self.data = data
        self._asc_longitude = 10.0
        self._asc_house = 0
    
        if self.data is None:
            self.data = [
                'லக்னம் ♑︎மகரம் 22° 26’ 37"',
                'சூரியன்☉ ♏︎விருச்சிகம் 21° 33’ 34"',
                'சந்திரன்☾ ♎︎துலாம் 6° 57’ 33"',
                'செவ்வாய்♂ ♌︎சிம்மம் 25° 32’ 10"',
                'புதன்☿ ♐︎தனுசு 9° 55’ 36"',
                'குரு♃ ♐︎தனுசு 25° 49’ 14"',
                'சுக்ரன்♀ ♎︎துலாம் 23° 42’ 24"',
                'சனி♄ ♓︎மீனம் 6° 48’ 25"',
                'ராகு☊ ♍︎கன்னி 10° 33’ 13"',
                'கேது☋ ♓︎மீனம் 10° 33’ 13"'
            ]

    def set_label_font_size(self,label_font_size:int):
        """
            Set Label Font Size
            @param label_font_size: int - default: _west_label_font_size
        """
        self._label_font_size = label_font_size
    def set_chart_center_coordinates(self,chart_center_pos:tuple):
        """
            set chart center coordinates (x,y)
            @param chart_center_pos: tuple (x,y) 
        """
        self._chart_center_pos = chart_center_pos
    def set_chart_radii_dimensions(self,chart_radii:tuple):
        """
            set radius of four cicles that form a western chart (r1,r2,r3,r4)
            @param chart_center_pos: tuple (r1,r2,r3,r4) 
        """
        self._chart_radii = chart_radii
    def paintEvent(self, event):
        self._draw_western_chart()

    def _get_chart_rect(self):
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        r = self._chart_radii[-1]
    
        return (
            cx - r,
            cy - r,
            2 * r,
            2 * r
        )

    def _draw_western_chart(self):
        painter = QPainter(self)
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        center = QtCore.QPoint(cx,cy)
        r1 = self._chart_radii[0]
        r2 = self._chart_radii[1]
        r3 = self._chart_radii[2]
        r23 = r3-0.5*(r3-r2)
        r23b = r3-0.75*(r3-r2)
        r4 = self._chart_radii[3]
        r34 = r4 -0.5*(r4-r3)
        painter.drawEllipse(center,r1,r1)
        painter.drawEllipse(center,r2,r2)
        painter.drawEllipse(center,r3,r3)
        painter.drawEllipse(center,r4,r4)
        asc_long = self._asc_longitude
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        icon_x = int(cx - 0.65 * r1)
        icon_y = int(cy - 0.65 * r1)
        icon_height = int(r1*1.4)
        icon_width = int(r1*1.4)
        icon = QPixmap(_image_path+"//lord_ganesha1.jpg")
        painter.drawPixmap(QtCore.QRect(icon_x,icon_y,icon_width,icon_height),icon)
        for i in range(180,540,30):
            a = i*math.pi/180.0
            ip = QtCore.QPoint(int(cx+r1*math.cos(a)),int(cy+r1*math.sin(a)))
            op = QtCore.QPoint(int(cx+r2*math.cos(a)),int(cy+r2*math.sin(a)))
            painter.drawLine(ip,op)
        for i in range(0,360,5):
            a = i*math.pi/180.0
            ri = r23
            if i%10==0:
                ri = r23b
            ip = QtCore.QPoint(int(cx+ri*math.cos(a)),int(cy+ri*math.sin(a)))
            op = QtCore.QPoint(int(cx+r3*math.cos(a)),int(cy+r3*math.sin(a)))
            painter.drawLine(ip,op)
        for i in range(12):
            a = (i*30+asc_long+150)*math.pi/180.0
            ip = QtCore.QPoint(int(cx+r3*math.cos(a)),int(cy+r3*math.sin(a)))
            op = QtCore.QPoint(int(cx+r4*math.cos(a)),int(cy+r4*math.sin(a)))
            painter.drawLine(ip,op)
        painter.setPen(QColor(_planet_color))
        for i in range(len(self.data)):
            self._write_planets_inside_houses(painter,r2,self.data[i],i)
        painter.setPen(QPen())
        painter.setPen(QColor(_rasi_color))
        for i_z in range(12):
            z_i = (self._asc_house+i_z+12)%12
            zodiac_symbol = _zodiac_symbols[z_i]
            house_mid_angle = (i_z*30+self._asc_longitude+155)#*math.pi/180.0
            rect = QtCore.QRect(int(cx+r34*math.cos(house_mid_angle*math.pi/180.0)),int(cy-r34*math.sin(house_mid_angle*math.pi/180.0)),10,10)
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,zodiac_symbol.strip())
        painter.setPen(QPen())
        rect = QtCore.QRect(cx-r1,cy-r1,r1*2,2*r1)
        
        self._draw_chart_title_below(painter=painter,title=self._chart_title,
                                     font_size=getattr(self, 'chart_title_font_size', None)
                                     )

        """ reset painter """
        painter.setPen(QPen())
        painter.setFont(QFont())                    
    def _write_planets_inside_houses(self,painter,radius,data,i_z):
        tmp_arr = data.strip().split()
        planet = tmp_arr[0][-2:].strip() if const._retrogade_symbol in tmp_arr[0] else tmp_arr[0][-1:].strip() 
        zodiac = tmp_arr[1][0].strip()
        deg = int(tmp_arr[-3][:-1].strip())
        mins = int(tmp_arr[-2][:-1].strip())
        sec = int(tmp_arr[-1][:-1].strip())
        #deg = int(tmp_arr[2][:-1].strip())
        #mins = int(tmp_arr[3][:-1].strip())
        #sec = int(tmp_arr[4][:-1].strip())
        zodiac_index = _zodiac_symbols.index(zodiac)
        if i_z==0:
            planet = 'ℒ'
            self._asc_longitude = deg+mins/60.0
            self._asc_house = zodiac_index
        min_new = round(mins+sec/60.0)
        text_new = planet+' '+tmp_arr[2]+' '+zodiac+' '+ str(min_new)+tmp_arr[-3][-1]
        house_index = (zodiac_index - self._asc_house + 12+5) % 12 #+5 to account for 150 degrees for ASC house start
        house_start_angle = house_index*30
        angle = round(house_start_angle+(deg+(mins/60.0+sec/3600.0)))
        a = angle*math.pi/180.0
        cx = self._chart_center_pos[0]
        cy = self._chart_center_pos[1]
        ri = self._label_pos_radial_increment
        font = QFont()
        font.setPixelSize(self._label_font_size)
        painter.setFont(font)                    
        for i,c in enumerate(text_new.split()):
            rect = QtCore.QRect(int(cx+(radius-(i+1)*ri)*math.cos(a)),int(cy-(radius-(i+1)*ri)*math.sin(a)),20,12)
            painter.drawText(rect,Qt.AlignmentFlag.AlignLeft,c.strip())
        painter.setFont(QFont()) # reset font
               
    def setData(self,data,chart_title='',chart_title_font_size=None):#,event=None):
        self._chart_title = chart_title
        self._chart_title_font_size = chart_title_font_size
        self.data = data; 
        tmp_arr = data[0].strip().split()
        deg = int(tmp_arr[-3][:-1].strip())
        mins = int(tmp_arr[-2][:-1].strip())
        sec = int(tmp_arr[-1][:-1].strip())
        #deg = int(tmp_arr[2][:-1].strip())
        #mins = int(tmp_arr[3][:-1].strip())
        #sec = int(tmp_arr[4][:-1].strip())
        self._asc_longitude = deg+mins/60.0+sec/3600.0
        self.update()

class EastIndianChart(KundaliChart):
    """
        Draws East Indian Natal Chart and labels the planets
        East Indian chart is 3x3 goes anti-clockwise from top-middle
        @param data: 2-D List of planet names in native language
            NOTE: For East Indian Chart - inner cells of 2-D list should have empty labels
            Example: [ ['Saturn/Moon',     'Neptune',       'Mars'/'Sun'],
                       ['Lagnam',          ''   ,     'Ragu'],
                       ['Ketu/Venus',    'Pluto',  'Mercury/Jupiter']
                    ]
        @param chart_house_size: chart size tuple(x,y,width,height)
        @param label_font_size: font size of labels: Default: _east_label_font_size  
    """
    _east_label_font_size = 9
    _east_chart_house_x = 1
    _east_chart_house_y = _east_chart_house_x
    _east_chart_house_width = 120 #100
    _east_chart_house_height = _east_chart_house_width
    _east_chart_title_font_size = 9
    def __init__(self, data=None,
                 chart_house_size: tuple = (_east_chart_house_x, _east_chart_house_y, _east_chart_house_width, _east_chart_house_height),
                 label_font_size: int = _east_label_font_size,
                 chart_size_factor: float = 1.0,
                 chart_title_font_size=_east_chart_title_font_size,
                 arudha_lagna_data=None,
                 chart_title='',
                 draw_frames=False,
                 ):
        KundaliChart.__init__(self, Chart.Style.EastIndian)
        self._draw_frames = draw_frames
        self._chart_title = chart_title
        self._chart_house_size = chart_house_size
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self._chart_title_font_size = chart_title_font_size
    
        drik._TROPICAL_MODE = False
        drik.set_sideral_planets()
    
        self._zodiac_symbols = [
            ['\n\u264A/\u2649\n', '\u2648', '\u2653\n/\n\u2652'],
            ['\u264B', '', '\u2651'],
            ['\u264C\n/\n\u264D', '\u264E', '\n\u264F/\u2650\n'],
        ]
    
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        self._grid_labels = []
        self.row_count = 3
        self.col_count = 3
        self._asc_house = 0
    
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2] * self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3] * self._chart_size_factor)
    
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
    
        if self.data is None:
            self.data = ['' for _ in range(12)]
        
    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def paintEvent(self, event):
        self.set_east_indian_chart_data()
    def setData(self, data, chart_title='', chart_title_font_size=None, arudha_lagna_data=None, menu_dict=None,
                varga_factor=None, drishti_table_widgets=None, planet_info_widgets=None, aspect_widgets=None,
                ndl_22_widgets=None, ndl_64_widgets=None, graha_drekkana_widgets=None, nava_thaara_widgets=None,
                spl_thaara_widgets=None):
        self._set_kundali_data(
            data=data,
            chart_title=chart_title,
            chart_title_font_size=chart_title_font_size,
            arudha_lagna_data=arudha_lagna_data,
            menu_dict=menu_dict,
            varga_factor=varga_factor,
            drishti_table_widgets=drishti_table_widgets,
            planet_info_widgets=planet_info_widgets,
            aspect_widgets=aspect_widgets,
            ndl_22_widgets=ndl_22_widgets,
            ndl_64_widgets=ndl_64_widgets,
            graha_drekkana_widgets=graha_drekkana_widgets,
            nava_thaara_widgets=nava_thaara_widgets,
            spl_thaara_widgets=spl_thaara_widgets
        )

    def _get_chart_rect(self):
        return (
            self.x,
            self.y,
            self.col_count * self.house_width,
            self.row_count * self.house_height
        )

    def _draw_east_indian_chart_grid(self, painter, row_count, col_count, cell_width, cell_height):
        """
        Draw East Indian chart grid.
    
        self._draw_frames = True:
            Draw outer border plus internal grid lines.
    
        self._draw_frames = False:
            Do not draw outer border.
            Still draw internal vertical/horizontal lines.
        """
        painter.setPen(QPen())
    
        chart_width = round(col_count * cell_width)
        chart_height = round(row_count * cell_height)

        self._draw_chart_title_below(painter)

        left = round(self.x)
        top = round(self.y)
        right = round(self.x + chart_width)
        bottom = round(self.y + chart_height)
    
        # Draw outer border only if requested
        if self._draw_frames:
            painter.drawRect(
                QtCore.QRect(
                    left,
                    top,
                    chart_width,
                    chart_height
                )
            )
    
        # Always draw internal vertical lines
        for c in range(1, col_count):
            x = round(self.x + c * cell_width)
            painter.drawLine(
                x,
                top,
                x,
                bottom
            )
    
        # Always draw internal horizontal lines
        for r in range(1, row_count):
            y = round(self.y + r * cell_height)
            painter.drawLine(
                left,
                y,
                right,
                y
            )

    def set_east_indian_chart_data(self):
        """
        Sets the planet labels on to the East Indian natal chart.
    
        NOTE:
        For East Indian Chart:
            - Inner cells of 2-D list should have empty labels.
            - Corner cells should be divided by a separator "/".
    
        Example:
            [
                ['Saturn/',      'Moon',       'Mars/Sun'],
                ['Lagnam',       '',           'Rahu'],
                ['Ketu/Venus',   'Jupiter',    '/Jupiter']
            ]
    
        Frame behavior:
            self._draw_frames = True:
                Draw outer border plus internal grid lines.
    
            self._draw_frames = False:
                Do not draw outer border.
                Still draw internal grid lines and diagonals.
        """
        painter = QPainter(self)
    
        data = self.data
        chart_title = self._chart_title
    
        row_count = len(data)
        col_count = len(data[0])
    
        cell_width = self.house_width
        cell_height = self.house_height
    
        chart_width = round(col_count * cell_width)
        chart_height = round(row_count * cell_height)
    
        # Draw chart grid once.
        self._draw_east_indian_chart_grid(
            painter,
            row_count,
            col_count,
            cell_width,
            cell_height
        )

        painter.setPen(QPen())
    
        font = QFont()
        painter.setFont(font)
    
        self._draw_center_icon(
            painter,
            icon_file='lord_ganesha1.jpg',
            icon_size_factor=0.18,
            min_icon_size=36
        )
    
        painter.setPen(QPen())
        
        for row in range(row_count):
            for col in range(col_count):
                font = QFont()
                font.setPixelSize(self._label_font_size)
                painter.setFont(font)
                painter.setPen(QPen())
    
                left_top_cell = (row == 0 and col == 0)
                right_bottom_cell = (row == row_count - 1 and col == col_count - 1)
                right_top_cell = (row == 0 and col == col_count - 1)
                left_bottom_cell = (row == row_count - 1 and col == 0)
                center_cell = (row == 1 and col == 1)
    
                cell = data[row][col]
    
                arudha = '/'
                if self.arudha_lagna_data and self.arudha_lagna_data[row][col].strip() != '':
                    arudha = self.arudha_lagna_data[row][col]
    
                if arudha.strip() == '':
                    arudha = '/'
    
                zodiac_symbol = self._zodiac_symbols[row][col]
    
                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)
    
                rect = QtCore.QRect(
                    cell_x,
                    cell_y,
                    round(cell_width),
                    round(cell_height)
                )
    
                # Do not draw painter.drawRect(rect) here.
                # Grid/frame is already drawn once above.
    
                if left_top_cell:
                    painter.setPen(QPen())
    
                    bottom_cell_text, top_cell_text = cell.split("/")
                    bottom_zodiac, top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha, top_cell_arudha = arudha.split("/")
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        top_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        top_cell_arudha.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        '\n' + top_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        bottom_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        bottom_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        '\n' + bottom_cell_arudha.strip()
                    )
    
                    painter.setPen(QPen())
                    painter.drawLine(
                        round(self.x),
                        round(self.y),
                        round(self.x + cell_width),
                        round(self.y + cell_height)
                    )
    
                elif right_top_cell:
                    painter.setPen(QPen())
    
                    top_cell_text, bottom_cell_text = cell.split("/")
                    top_zodiac, bottom_zodiac = zodiac_symbol.split("/")
                    top_cell_arudha, bottom_cell_arudha = arudha.split("/")
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        top_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        top_cell_arudha.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        '\n' + top_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        bottom_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        bottom_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        '\n' + bottom_cell_arudha.strip()
                    )
    
                    painter.setPen(QPen())
                    painter.drawLine(
                        round(self.x + chart_width),
                        round(self.y),
                        round(self.x + chart_width - cell_width),
                        round(self.y + cell_height)
                    )
    
                elif right_bottom_cell:
                    painter.setPen(QPen())
    
                    bottom_cell_text, top_cell_text = cell.split("/")
                    bottom_zodiac, top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha, top_cell_arudha = arudha.split("/")
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        bottom_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        bottom_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        '\n' + bottom_cell_arudha.strip()
                    )
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        top_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        top_cell_arudha.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        '\n' + top_zodiac.strip()
                    )
    
                    painter.setPen(QPen())
                    painter.drawLine(
                        round(self.x + chart_width - cell_width),
                        round(self.y + chart_height - cell_height),
                        round(self.x + chart_width),
                        round(self.y + chart_height)
                    )
    
                elif left_bottom_cell:
                    painter.setPen(QPen())
    
                    bottom_cell_text, top_cell_text = cell.split("/")
                    bottom_zodiac, top_zodiac = zodiac_symbol.split("/")
                    bottom_cell_arudha, top_cell_arudha = arudha.split("/")
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        bottom_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        bottom_cell_arudha.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        '\n' + bottom_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        top_cell_text.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        top_zodiac.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        '\n' + top_cell_arudha.strip()
                    )
    
                    painter.setPen(QPen())
                    painter.drawLine(
                        round(self.x),
                        round(self.y + chart_height),
                        round(self.x + cell_width),
                        round(self.y + chart_height - cell_height)
                    )
    
                else:
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignCenter,
                        cell.strip()
                    )
    
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        zodiac_symbol.strip()
                    )
    
                    painter.setPen(QColor(_arudha_color))
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        arudha.strip()
                    )
    
                    painter.setPen(QPen())
    
                painter.setPen(QPen())
    
        painter.end()
    
class SouthIndianChart(KundaliChart):
    """
        Draws South Indian Natal Chart and labels the planets

        @param data: 2-D List of planet names in native language

        NOTE:
        For South Indian Chart - inner cells of 2-D list should have empty labels.

        Example:
            [
                ['Saturn','Moon','Sun', 'Mars'],
                ['Lagnam', ''   , ''  , 'Ragu'],
                ['Ketu'  , ''   , ''  , 'Mercury'],
                [''      , 'Jupiter','','']
            ]

        @param chart_house_size: chart size tuple(x,y,width,height)
        @param label_font_size: font size of labels
    """

    _south_label_font_size = 9
    _south_chart_house_x = 1
    _south_chart_house_y = _south_chart_house_x
    _south_chart_house_width = 350
    _south_chart_house_height = _south_chart_house_width
    _south_chart_title_font_size = 9

    def __init__(
            self,
            data=None,
            chart_house_size: tuple = (
                _south_chart_house_x,
                _south_chart_house_y,
                _south_chart_house_width,
                _south_chart_house_height
            ),
            label_font_size: int = _south_label_font_size,
            chart_size_factor: float = 1.0,
            chart_title_font_size=_south_chart_title_font_size,
            arudha_lagna_data=None,
            chart_title='',
            chart_style_irregular=False,
    ):
        KundaliChart.__init__(self, Chart.Style.SouthIndian)

        self.chart_style_irregular = chart_style_irregular
        self._chart_house_size = chart_house_size
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self._chart_title_font_size = chart_title_font_size

        const._TROPICAL_MODE = False
        drik.set_sideral_planets()

        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)

        if self.chart_style_irregular:
            self._zodiac_symbols = const.south_irregular_zodiac_symbol_map
        else:
            self._zodiac_symbols = const.south_regular_zodiac_symbol_map
        self.row_count = 4
        self.col_count = 4

        self._asc_house = (-1, -1)
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2] * self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3] * self._chart_size_factor)

        self.data = data
        self.arudha_lagna_data = arudha_lagna_data

        self._chart_title = chart_title

        if self.data is None:
            self.data = [['' for _ in range(4)] for _ in range(4)]

    def chart_type_name(self):
        if self.chart_style_irregular:
            return const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR
        return const.CHART_STYLE.SOUTH_INDIAN_REGULAR

    def set_chart_size(self, chart_size: tuple):
        self._chart_house_size = chart_size

    def set_label_font_size(self, label_font_size):
        self._label_font_size = label_font_size

    def paintEvent(self, event):
        self.set_south_indian_chart_data()

    def setData(
            self,
            data,
            chart_title='',
            chart_title_font_size=None,
            arudha_lagna_data=None,
            menu_dict=None,
            varga_factor=None,
            drishti_table_widgets=None,
            planet_info_widgets=None,
            aspect_widgets=None,
            ndl_22_widgets=None,
            ndl_64_widgets=None,
            graha_drekkana_widgets=None,
            nava_thaara_widgets=None,
            spl_thaara_widgets=None
    ):
        """
        Set South Indian chart data.
    
        Data is expected to already be in the correct 2-D South Indian layout:
            - regular chart   -> regular South Indian 2-D data
            - irregular chart -> irregular South Indian 2-D data
    
        This class only draws the data. It does not reverse or remap it.
        """
    
        self._set_kundali_data(
            data=data,
            chart_title=chart_title,
            chart_title_font_size=chart_title_font_size,
            arudha_lagna_data=arudha_lagna_data,
            menu_dict=menu_dict,
            varga_factor=varga_factor,
            drishti_table_widgets=drishti_table_widgets,
            planet_info_widgets=planet_info_widgets,
            aspect_widgets=aspect_widgets,
            ndl_22_widgets=ndl_22_widgets,
            ndl_64_widgets=ndl_64_widgets,
            graha_drekkana_widgets=graha_drekkana_widgets,
            nava_thaara_widgets=nava_thaara_widgets,
            spl_thaara_widgets=spl_thaara_widgets
        )

    def set_south_indian_chart_data(self):
        """
        Draw South Indian chart cells, planets, arudha/overlay labels,
        zodiac symbols, and ascendant indicator.
        """
        painter = QPainter(self)

        data = self.data

        row_count = len(data)
        col_count = len(data[0])

        chart_width = self.house_width
        chart_height = self.house_height

        cell_width = round(chart_width / self.col_count)
        cell_height = round(chart_height / self.row_count)

        self._draw_chart_title_below(painter)

        # Draw center icon.
        self._draw_center_icon(
            painter,
            icon_file='lord_ganesha1.jpg',
            icon_size_factor=0.18,
            min_icon_size=36
        )

        asc_house = self._asc_house

        for row in range(row_count):
            for col in range(col_count):
                font = QFont()
                painter.setPen(QPen())
                font.setPixelSize(self._label_font_size)
                painter.setFont(font)

                cell_text = data[row][col]

                cell_x = round(self.x + col * cell_width)
                cell_y = round(self.y + row * cell_height)

                cell_rect = QtCore.QRect(
                    cell_x,
                    cell_y,
                    cell_width,
                    cell_height
                )

                # South Indian chart uses only outer cells.
                if row == 0 or row == row_count - 1 or col == 0 or col == col_count - 1:

                    # Draw arudha / overlay text.
                    if (
                            self.arudha_lagna_data
                            and self.arudha_lagna_data[row][col].strip() != ''
                    ):
                        arudha_text = self.arudha_lagna_data[row][col].strip()
                        painter.setPen(QColor(_arudha_color))
                        painter.drawText(
                            cell_rect,
                            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                            arudha_text
                        )

                    # Draw cell border.
                    painter.setPen(QPen())
                    painter.drawRect(cell_rect)

                    # Draw planet text.
                    painter.setPen(QColor(_planet_color))
                    painter.drawText(
                        cell_rect,
                        Qt.AlignmentFlag.AlignCenter,
                        cell_text.strip()
                    )

                    # Draw zodiac symbol.
                    painter.setPen(QColor(_rasi_color))
                    painter.drawText(
                        cell_rect,
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
                        self._zodiac_symbols[row][col].strip()
                    )

                    painter.setPen(QPen())

                    # Draw ascendant marker.
                    asc_row, asc_col = asc_house
                    
                    if row == asc_row and col == asc_col:
                        line_start_x = cell_x
                        line_start_y = round(cell_y + _lagnam_line_factor * cell_height)
                        line_end_x = round(cell_x + _lagnam_line_factor * cell_width)
                        line_end_y = cell_y
                    
                        painter.drawLine(
                            line_start_x,
                            line_start_y,
                            line_end_x,
                            line_end_y
                        )
                painter.setPen(QPen())

        painter.end()

class NorthIndianChart(KundaliChart):
    _north_label_font_size = 9
    _north_chart_house_x = 1
    _north_chart_house_y = _north_chart_house_x
    _north_chart_house_width = 350 #300
    _north_chart_house_height = _north_chart_house_width
    _north_label_positions = [(4/10,1.0/10),(1.5/10,0.5/10),(0.1/10,2.0/10),(1.5/10,4/10), 
                     (0.1/10,7/10), (1.75/10,8.5/10), (3.5/10,7/10), (6.75/10,8.5/10),
                     (8.5/10,7/10),(6.5/10,4/10),(8.35/10,2.0/10),(6.5/10,0.5/10)]
    _north_arudha_positions = [(5/10,3.75/10),(3.25/10,0.1/10),(0.1/10,3.75/10),(2.25/10,6.5/10), 
                     (0.1/10,8.75/10), (0.5/10,9.5/10), (4.5/10,8.25/10), (8.75/10,9.5/10),
                     (9.25/10,8.75/10),(7.25/10,6.5/10),(9.25/10,3.75/10),(8.75/10,0.25/10)]
    _north_zodiac_label_positions = [(4.75/10,0.25/10),(2.25/10,1.75/10),(0.05/10,0.25/10),(2.25/10,2.75/10), 
                     (0.1/10,5.25/10), (2.25/10,7.75/10), (4.75/10,5.5/10), (7.25/10,7.75/10),
                     (9.5/10,5.5/10),(7.25/10,2.75/10),(9.5/10,0.5/10),(7.25/10,1.75/10)]
    _north_chart_icon_x = int((_north_chart_house_width/2)*0.85)
    _north_chart_icon_y = int((_north_chart_house_height/2)*0.85)
    _north_chart_icon_width = 50
    _north_chart_icon_height = _north_chart_icon_width
    _north_chart_title_font_size = 9
    def __init__(self, data=None,
                 chart_house_size: tuple = (_north_chart_house_x, _north_chart_house_y, _north_chart_house_width, _north_chart_house_height),
                 label_font_size: int = _north_label_font_size,
                 chart_size_factor: float = 1.0,
                 arudha_lagna_data=None,
                 chart_title_font_size=_north_chart_title_font_size,
                 chart_title=''):
        KundaliChart.__init__(self, Chart.Style.NorthIndian)
    
        drik._TROPICAL_MODE = False
        drik.set_sideral_planets()
    
        self._chart_house_size = chart_house_size
        self._label_font_size = label_font_size
        self._chart_size_factor = chart_size_factor
        self._chart_title_font_size = chart_title_font_size
    
        self.row_count = 4
        self.col_count = 4
        self._asc_house = 0
        self.data = data
        self.arudha_lagna_data = arudha_lagna_data
    
        self.x = self._chart_house_size[0]
        self.y = self._chart_house_size[1]
        self.house_width = round(self._chart_house_size[2] * self._chart_size_factor)
        self.house_height = round(self._chart_house_size[3] * self._chart_size_factor)
    
        self.resources = []
        self._chart_title = chart_title
        self._grid_labels = []
        self.label_positions = NorthIndianChart._north_label_positions
        self.zodiac_label_positions = NorthIndianChart._north_zodiac_label_positions
        self.north_arudha_positions = NorthIndianChart._north_arudha_positions
    
        if self.data is None:
            self.data = ['' for _ in range(12)]

    def set_chart_size(self,chart_size:tuple):
        self._chart_house_size = chart_size
    def set_label_font_size(self,label_font_size):
        self._label_font_size = label_font_size
    def set_chart_label_positions(self,chart_label_positions):
        self.label_positions = chart_label_positions
    def set_chart_zodiac_label_positions(self,zodiac_label_positions):
        self.zodiac_label_positions = zodiac_label_positions
    def paintEvent(self, event):
        self._draw_north_indian_chart()#event)
    def setData(self, data, chart_title='', chart_title_font_size=None, arudha_lagna_data=None, menu_dict=None,
                varga_factor=None, drishti_table_widgets=None, planet_info_widgets=None, aspect_widgets=None,
                ndl_22_widgets=None, ndl_64_widgets=None, graha_drekkana_widgets=None, nava_thaara_widgets=None,
                spl_thaara_widgets=None):
        self._set_kundali_data(
            data=data,
            chart_title=chart_title,
            chart_title_font_size=chart_title_font_size,
            arudha_lagna_data=arudha_lagna_data,
            menu_dict=menu_dict,
            varga_factor=varga_factor,
            drishti_table_widgets=drishti_table_widgets,
            planet_info_widgets=planet_info_widgets,
            aspect_widgets=aspect_widgets,
            ndl_22_widgets=ndl_22_widgets,
            ndl_64_widgets=ndl_64_widgets,
            graha_drekkana_widgets=graha_drekkana_widgets,
            nava_thaara_widgets=nava_thaara_widgets,
            spl_thaara_widgets=spl_thaara_widgets,
            default_chart_title_font_size=NorthIndianChart._north_chart_title_font_size
        )
    
    def _draw_north_indian_chart(self):
        painter = QPainter(self)
        chart_width = self.house_width
        chart_height = self.house_height
        cell_width = round(chart_width / self.col_count)
        cell_height = round(chart_height / self.row_count)
        painter.setPen(QPen())
    
        rect = QtCore.QRect(self.x, self.y, chart_width, chart_height)
        painter.drawRect(rect)
    
        icon_x = int(NorthIndianChart._north_chart_icon_x * self._chart_size_factor)
        icon_y = int(NorthIndianChart._north_chart_icon_y * self._chart_size_factor)
        icon_width = int(NorthIndianChart._north_chart_icon_width * self._chart_size_factor)
        icon_height = int(NorthIndianChart._north_chart_icon_height * self._chart_size_factor)
        icon_rect = QtCore.QRect(icon_x, icon_y, icon_width, icon_height)
        icon = QPixmap(_image_path + "//lord_ganesha1.jpg")
        painter.drawPixmap(icon_rect, icon)
    
        diag_start_x = self.x
        diag_start_y = self.y
        diag_end_x = round(diag_start_x + chart_width)
        diag_end_y = round(diag_start_y + chart_height)
        painter.drawLine(diag_start_x, diag_start_y, diag_end_x, diag_end_y)
    
        diag_start_x = self.x
        diag_start_y = round(self.y + chart_height)
        diag_end_x = round(self.x + chart_width)
        diag_end_y = self.y
        painter.drawLine(diag_start_x, diag_start_y, diag_end_x, diag_end_y)
    
        start_x = self.x
        start_y = round(self.y + chart_height / 2)
        end_x = round(self.x + chart_width / 2)
        end_y = self.y
        painter.drawLine(start_x, start_y, end_x, end_y)
    
        start_x = end_x
        start_y = end_y
        end_x = round(self.x + chart_width)
        end_y = round(self.y + chart_height / 2)
        painter.drawLine(start_x, start_y, end_x, end_y)
    
        start_x = end_x
        start_y = end_y
        end_x = round(self.x + chart_width / 2)
        end_y = round(self.y + chart_height)
        painter.drawLine(start_x, start_y, end_x, end_y)
    
        start_x = end_x
        start_y = end_y
        end_x = self.x
        end_y = round(self.y + chart_height / 2)
        painter.drawLine(start_x, start_y, end_x, end_y)
    
        self._draw_chart_title_below(painter)
    
        font = QFont()
        painter.setPen(QPen())
        painter.setFont(font)
    
        font = QFont()
        font.setPixelSize(self._label_font_size)
        painter.setFont(font)
    
        for l, pos in enumerate(self.label_positions):
            zl = (l + self._asc_house - 1) % 12
            x = pos[0]
            zx = self.zodiac_label_positions[l][0]
            ax = self.north_arudha_positions[l][0]
            y = pos[1]
            zy = self.zodiac_label_positions[l][1]
            ay = self.north_arudha_positions[l][1]
    
            label_text = str(self.data[l])
            label_x = round(self.x + x * chart_width)
            label_y = round(self.y + y * chart_height)
    
            cell_height = round(chart_height / self.row_count)
            cell_width = round(chart_width / self.col_count)
            cell_rect = QtCore.QRect(label_x, label_y, cell_width, cell_height)
    
            painter.setPen(QColor(_planet_color))
            painter.drawText(cell_rect, 0, label_text.strip())
    
            zodiac_label_text = _zodiac_symbols[zl]
            zodiac_label_x = round(self.x + zx * chart_width)
            zodiac_label_y = round(self.y + zy * chart_height)
            zodiac_cell_rect = QtCore.QRect(zodiac_label_x, zodiac_label_y, cell_width, cell_height)
    
            painter.setPen(QColor(_rasi_color))
            painter.drawText(zodiac_cell_rect, 0, zodiac_label_text.strip())
    
            if self.arudha_lagna_data:
                arudha_label_text = self.arudha_lagna_data[l]
                arudha_label_x = round(self.x + ax * chart_width)
                arudha_label_y = round(self.y + ay * chart_height)
                arudha_cell_rect = QtCore.QRect(arudha_label_x, arudha_label_y, cell_width, cell_height)
    
                painter.setPen(QColor(_arudha_color))
                painter.drawText(arudha_cell_rect, 0, arudha_label_text.strip())
    
            painter.setPen(QPen())
    
        painter.end()
    
def _convert_1d_chart_with_planet_names(chart_1d_list): #To be used for Sudarsana Chakra data as input
    from jhora.horoscope.chart import house
    result = []
    retrograde_planets = chart_1d_list[-1]
    for chart_1d in chart_1d_list[:-1]:
        res = []
        for z,pls in chart_1d:
            pl_str = ''
            tmp = pls.split('/')
            if len(tmp) == 1 and tmp[0] =='':
                pl_str = ''
                res.append((z,pl_str))
                continue
            for p in tmp:
                if p == const._ascendant_symbol:
                    pl_str += 'Lagnam'+'/'#const._ascendant_symbol+"/"
                else:
                    ret_str = ''
                    if int(p) in retrograde_planets:
                        ret_str = const._retrogade_symbol
                    pl_str += house.planet_list[int(p)]+ret_str+'/'#const._planet_symbols[int(p)]+'/'
            pl_str = pl_str[:-1]
            res.append((z,pl_str))
        result.append(res)
    return result
if __name__ == "__main__":
    from jhora.panchanga import drik
    from jhora import utils
    utils.set_language('ta'); _resources = utils.resource_strings
    south_data = [['சனி♄\nகேது☋', '', '', ''],['', '', '', ''],['லக்னம்ℒ\nஅருணா⛢\nவருணா♆', '', '', 'செவ்வாய்♂'],['புதன்☿\nகுரு♃\nமாந்தி', 'சூரியன்☉\nகுறுகோள்♇', 'சந்திரன்☾\nசுக்ரன்♀', 'ராகு☊']]
    north_data = ['புதன்☿\nகுரு♃\nமாந்தி', 'லக்னம்ℒ\nஅருணா⛢\nவருணா♆', '', 'சனி♄\nகேது☋', '', '', '', '', 'செவ்வாய்♂', 'ராகு☊', 'சந்திரன்☾\nசுக்ரன்♀', 'சூரியன்☉\nகுறுகோள்♇']
    east_data = [['/', '', 'சனி♄\nகேது☋/'],['', '', 'லக்னம்ℒ\nஅருணா⛢\nவருணா♆'],['செவ்வாய்♂/ராகு☊', 'சந்திரன்☾\nசுக்ரன்♀', 'சூரியன்☉\nகுறுகோள்♇/புதன்☿\nகுரு♃\nமாந்தி']]
    sudarsana_data = [[(6, 'L/7'), (7, '0/3/4'), (8, '2/5'), (9, ''), (10, '6'), (11, ''), (0, '8'), (1, ''), (2, '1'), (3, ''), (4, ''), (5, '')], [(2, '1'), (3, ''), (4, ''), (5, ''), (6, 'L/7'), (7, '0/3/4'), (8, '2/5'), (9, ''), (10, '6'), (11, ''), (0, '8'), (1, '')], [(7, '0/3/4'), (8, '2/5'), (9, ''), (10, '6'), (11, ''), (0, '8'), (1, ''), (2, '1'), (3, ''), (4, ''), (5, ''), (6, 'L/7')], [7, 8]]
    prasna_data = ['', '', '', '', '', '', '', '', '', 'பிர.ல', '', '']
    import sys
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    kundali = SouthIndianChart()
    #_set_chart_data(kundali, chart_type, '')
    kundali.setData(data=south_data, chart_title=" South Chart", chart_title_font_size=12)
    kundali.resize(600,600)
    kundali.show()
    sys.exit(App.exec())
    