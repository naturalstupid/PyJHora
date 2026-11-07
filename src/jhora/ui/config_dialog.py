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
"""Dynamic configuration dialog for the unified PyJHora settings model.

This dialog reads all UI metadata from jhora.config and builds the UI dynamically.
It no longer hardcodes USER_FIELDS / ADVANCED_FIELDS / BOOL_KEYS, etc.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jhora import config
_UNSUPPORTED_UI_LANGUAGES = {"sat", "mai", "doi", "mni", "santali", "maithili", "dogri", "Manipuri/Meitei"}

def _is_unsupported_language(value: Any) -> bool:
    return str(value).strip().lower() in _UNSUPPORTED_UI_LANGUAGES

# ============================================================
# HELPERS
# ============================================================
def _safe_find_combo_index(combo: QComboBox, value: Any) -> int:
    """Find a combo row by userData first, then by visible text, including str fallback."""
    idx = combo.findData(value)
    if idx >= 0:
        return idx

    idx = combo.findText(str(value))
    if idx >= 0:
        return idx

    # final fallback: compare stringified current data
    for i in range(combo.count()):
        data = combo.itemData(i)
        if str(data) == str(value):
            return i

    return -1


def _populate_combo(combo: QComboBox, choices: List[Any]) -> None:
    """Populate combo box from either values or (stored, label) pairs."""
    combo.clear()

    for item in choices:
        if isinstance(item, (tuple, list)) and len(item) == 2:
            stored, label = item
            combo.addItem(str(label), stored)
        else:
            combo.addItem(str(item), item)


def _list_to_text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(str(x) for x in value)
    if value is None:
        return ""
    return str(value)


def _text_to_list(text: str, subtype: str) -> List[Any]:
    raw_items = [x.strip() for x in str(text).split(",") if x.strip() != ""]

    if subtype == "int_list":
        result: List[int] = []
        for item in raw_items:
            try:
                result.append(int(item))
            except Exception:
                pass
        return result

    if subtype == "float_list":
        result: List[float] = []
        for item in raw_items:
            try:
                result.append(float(item))
            except Exception:
                pass
        return result

    return raw_items


# ============================================================
# WIDGET FACTORY
# ============================================================
class SettingWidgetFactory:
    @staticmethod
    def create(meta: Dict[str, Any]) -> QWidget:
        type_ = str(meta.get("type", "string")).strip().lower()
        value = meta.get("value", meta.get("default"))

        if type_ == "bool":
            widget = QCheckBox()
            widget.setChecked(bool(value))
            return widget

        if type_ == "int":
            widget = QSpinBox()
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            widget.setMinimum(int(meta.get("min", -2147483647)))
            widget.setMaximum(int(meta.get("max", 2147483647)))
            try:
                widget.setValue(int(value))
            except Exception:
                widget.setValue(int(meta.get("default", 0)))
            return widget

        if type_ == "float":
            widget = QDoubleSpinBox()
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            widget.setDecimals(int(meta.get("decimals", 6)))
            widget.setMinimum(float(meta.get("min", -1e12)))
            widget.setMaximum(float(meta.get("max", 1e12)))
            try:
                widget.setValue(float(value))
            except Exception:
                widget.setValue(float(meta.get("default", 0.0)))
            return widget

        if type_ == "choice":
            widget = QComboBox()
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            _populate_combo(widget, meta.get("choices", []))

            idx = _safe_find_combo_index(widget, value)
            if idx < 0:
                idx = _safe_find_combo_index(widget, meta.get("default"))
            if idx >= 0:
                widget.setCurrentIndex(idx)
            elif widget.count() > 0:
                widget.setCurrentIndex(0)

            return widget

        if type_ in ("int_list", "float_list", "string_list"):
            widget = QLineEdit()
            widget.setText(_list_to_text(value))
            widget.setPlaceholderText("Comma-separated values")
            return widget

        # default -> string
        widget = QLineEdit()
        widget.setText("" if value is None else str(value))
        return widget

    @staticmethod
    def read(widget: QWidget, meta: Dict[str, Any]) -> Any:
        type_ = str(meta.get("type", "string")).strip().lower()

        if isinstance(widget, QCheckBox):
            return widget.isChecked()

        if isinstance(widget, QSpinBox):
            return widget.value()

        if isinstance(widget, QDoubleSpinBox):
            return widget.value()

        if isinstance(widget, QComboBox):
            return widget.currentData()
            #if data is None:
            #    return widget.currentText()
            #return data

        if isinstance(widget, QLineEdit):
            text = widget.text()
            if type_ in ("int_list", "float_list", "string_list"):
                return _text_to_list(text, type_)
            return text

        return None


# ============================================================
# TAB PAGE
# ============================================================
class ConfigTabPage(QWidget):
    def __init__(self, tab_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tab_name = tab_name
        self._widgets: Dict[str, QWidget] = {}
        self._meta_by_key: Dict[str, Dict[str, Any]] = {}

        self._build_ui()
        self._wire_dynamic_behavior()
        self._apply_dynamic_behavior()
    def _wire_dynamic_behavior(self) -> None:
        """
        Wire UI dependencies between settings.
        """
        pos_type_widget = self._widgets.get("planet_position_type")
        if isinstance(pos_type_widget, QComboBox):
            pos_type_widget.currentIndexChanged.connect(self._apply_dynamic_behavior)

    def _apply_dynamic_behavior(self) -> None:
        """
        Apply enable/disable rules based on current selections.
        """
        # True / Apparent dependency:
        # If Position Type == True (i.e. "True"), aberration and deflection are not applicable.
        pos_type_widget = self._widgets.get("planet_position_type")
        use_aberr_widget = self._widgets.get("use_aberration_of_light")
        use_defl_widget = self._widgets.get("use_gravitational_deflection")

        is_true_position = False
        if isinstance(pos_type_widget, QComboBox):
            current_data = pos_type_widget.currentData()
            is_true_position = bool(current_data)

        enabled_for_apparent = not is_true_position

        if use_aberr_widget is not None:
            use_aberr_widget.setEnabled(enabled_for_apparent)
            if not enabled_for_apparent:
                use_aberr_widget.setToolTip("Used only for apparent positions.")
            else:
                meta = self._meta_by_key.get("use_aberration_of_light", {})
                use_aberr_widget.setToolTip(str(meta.get("description", "")))

        if use_defl_widget is not None:
            use_defl_widget.setEnabled(enabled_for_apparent)
            if not enabled_for_apparent:
                use_defl_widget.setToolTip("Used only for apparent positions.")
            else:
                meta = self._meta_by_key.get("use_gravitational_deflection", {})
                use_defl_widget.setToolTip(str(meta.get("description", "")))

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)

        sections = config.get_ui_sections(tab=self.tab_name, visible_only=True)

        for section_name, items in sections.items():
            box = QGroupBox(str(section_name).replace("_", " ").title())
            box_layout = QFormLayout(box)
            box_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

            for item in items:
                key = item["key"]
                self._meta_by_key[key] = item

                widget = SettingWidgetFactory.create(item)
                if item.get("description"):
                    widget.setToolTip(str(item["description"]))

                label = QLabel(str(item.get("label", key)))
                if item.get("description"):
                    label.setToolTip(str(item["description"]))

                box_layout.addRow(label, widget)
                self._widgets[key] = widget

            layout.addWidget(box)

        layout.addStretch(1)

    def set_all_defaults(self) -> None:
        for key, widget in self._widgets.items():
            meta = self._meta_by_key[key]
            default_meta = dict(meta)
            default_meta["value"] = meta.get("default")

            parent_layout = widget.parentWidget().layout() if widget.parentWidget() else None
            new_widget = SettingWidgetFactory.create(default_meta)
            if meta.get("description"):
                new_widget.setToolTip(str(meta["description"]))

            # Replace widget in layout cleanly
            if parent_layout is not None:
                for row in range(parent_layout.rowCount()):
                    item_field = parent_layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
                    if item_field and item_field.widget() is widget:
                        parent_layout.removeWidget(widget)
                        widget.deleteLater()
                        parent_layout.setWidget(row, QFormLayout.ItemRole.FieldRole, new_widget)
                        self._widgets[key] = new_widget
                        break
            else:
                # Fallback: just update internal map if no layout found
                self._widgets[key] = new_widget

    def collect_values(self) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        for key, widget in self._widgets.items():
            meta = self._meta_by_key[key]
            values[key] = SettingWidgetFactory.read(widget, meta)
        return values


# ============================================================
# MAIN DIALOG
# ============================================================
class ConfigDialog(QDialog):
    """Dynamic configuration dialog.

    mode:
        "user"      -> only User tab
        "advanced"  -> only Advanced tab
        "both"      -> both tabs
    """

    def __init__(self, mode: str = "both", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.mode = str(mode).strip().lower()
        if self.mode not in ("user", "advanced", "both"):
            self.mode = "both"

        # Ensure config is loaded
        if not config.get_all_setting_defs():
            try:
                config.load_all_settings(create_if_missing=True, apply=False)
            except Exception:
                # Let the dialog still try to open; save will show any real error.
                pass

        self.setWindowTitle("Configuration")
        self._tab_pages: Dict[str, ConfigTabPage] = {}
        self._build_ui()
        self.setMinimumSize(800, 625)
        self.adjustSize()

    def _find_language_combo(self):
        """Return (page, key, combo) for the language setting, or None."""
        for page in self._tab_pages.values():
            for key, widget in page._widgets.items():
                if isinstance(widget, QComboBox) and any(
                        _is_unsupported_language(widget.itemData(i)) for i in range(widget.count())):
                    return page, key, widget
        return None
    def _first_supported_index(self, combo: QComboBox) -> int:
        for pref in ("en", "English"):
            i = _safe_find_combo_index(combo, pref)
            if i >= 0 and not _is_unsupported_language(combo.itemData(i)):
                return i
        return next((i for i in range(combo.count())
                    if not _is_unsupported_language(combo.itemData(i))), 0)

    def _wire_language_guard(self) -> None:
        found = self._find_language_combo()
        if not found:
            return
        _page, _key, combo = found
        if getattr(self, "_lang_combo", None) is combo:       # already wired
            return
        self._lang_combo = combo
        cur = combo.currentIndex()
        if _is_unsupported_language(combo.itemData(cur)):     # file already holds one
            cur = self._first_supported_index(combo)
            combo.blockSignals(True)
            combo.setCurrentIndex(cur)
            combo.blockSignals(False)
        self._last_ok_index = cur
        combo.currentIndexChanged.connect(self._on_language_changed)

    def _on_language_changed(self, idx: int) -> None:
        combo = self._lang_combo
        if not _is_unsupported_language(combo.itemData(idx)):
            self._last_ok_index = idx                          # remember last good choice
            return
        chosen = combo.itemText(idx)
        combo.blockSignals(True)                               # revert without re-triggering
        combo.setCurrentIndex(self._last_ok_index)
        combo.blockSignals(False)
        QTimer.singleShot(0, lambda: QMessageBox.warning(
            self, "Language not supported",
            f"{chosen} is not supported in this version yet.\n"
            f"Reverting to {combo.currentText()}."))
    
    def _revert_unsupported_language(self) -> None:
        found = self._find_language_combo()
        if not found:
            return
        page, key, combo = found
        if not _is_unsupported_language(combo.currentData()):
            return
        chosen = combo.currentText()
        meta = page._meta_by_key.get(key, {})
        candidates = [meta.get("value"), meta.get("default"), "en", "English"]   # value = as stored when the dialog opened
        idx = -1
        for cand in candidates:
            if cand is not None and not _is_unsupported_language(cand):
                idx = _safe_find_combo_index(combo, cand)
                if idx >= 0:
                    break
        if idx < 0:
            idx = next((i for i in range(combo.count())
                        if not _is_unsupported_language(combo.itemData(i))), 0)
        combo.setCurrentIndex(idx)
        QMessageBox.warning(
            self, "Language not supported",
            f"{chosen} is not supported in this version yet.\n"
            f"Reverting to {combo.currentText()}.")
    
    def _selected_tabs(self) -> List[str]:
        all_tabs = config.get_ui_tabs()
        if self.mode == "both":
            return all_tabs
        requested = self.mode.capitalize()
        return [tab for tab in all_tabs if str(tab).lower() == requested.lower()]

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._tabs = QTabWidget(self)
        layout.addWidget(self._tabs)

        for tab_name in self._selected_tabs():
            page = ConfigTabPage(tab_name, self)
            self._tab_pages[tab_name] = page
            self._tabs.addTab(page, tab_name)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )

        self._restore_button = QPushButton("Restore Defaults", self)
        buttons.addButton(self._restore_button, QDialogButtonBox.ButtonRole.ResetRole)

        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        self._restore_button.clicked.connect(self._on_restore_defaults)

        layout.addWidget(buttons)
        self._wire_language_guard()

    def _on_restore_defaults(self) -> None:
        page = self._tabs.currentWidget()
        if isinstance(page, ConfigTabPage):
            page.set_all_defaults()
            self._wire_language_guard() 

    def _collect_all_values(self) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        for page in self._tab_pages.values():
            values.update(page.collect_values())
        return values

    def _on_save(self) -> None:
        try:
            self._revert_unsupported_language()
            values = self._collect_all_values()
            config.set_values(values, apply=True, save=False)
            config.save_all_settings()
            self.accept()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save configuration.\n\n{exc}",
            )


# ============================================================
# OPTIONAL TEST
# ============================================================
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    try:
        config.load_all_settings(create_if_missing=True, apply=False)
    except Exception:
        pass

    dlg = ConfigDialog(mode="both")
    dlg.exec()
    #config.debug_dump_runtime_bindings()
    sys.exit(0)
