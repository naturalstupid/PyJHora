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
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, QStringListModel, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QCompleter

from jhora import const, utils

_SIZE_SAMPLE_TEXT = 'Chennai'

# --------------------------------------------------------------------------
# Shared, app-independent helpers.
#
# These were previously copy-pasted (with small, silent behavioral drift)
# into horo_chart.py, horo_chart_tabs.py, panchangam.py and vedic_calendar.py
# as private methods named _resize_place_text_size / _reset_place_text_size /
# _get_location / _on_location_resolved. Centralizing them here means every
# consuming app gets the same (fixed) behavior automatically, instead of
# needing the same bug fixed N times.
# --------------------------------------------------------------------------
def parse_location_record(rec):
    """
    Normalize a resolved location record (as emitted by PlaceWidget's
    locationResolved(dict) signal, i.e. utils.get_location_record()'s return
    value) into a plain (place_name, latitude, longitude, timezone,
    elevation) tuple of the right types.
    Returns None if `rec` is falsy (e.g. empty dict / None).
    This replaces the identical parsing block that used to be duplicated
    verbatim inside every app's _on_location_resolved(self, rec) handler.
    """
    if not rec:
        return None
    place_name = rec.get('name') or rec.get('canonical_name', '')
    latitude = float(rec['latitude'])
    longitude = float(rec['longitude'])
    timezone_hrs = float(rec['timezone'])
    elevation = float(rec.get('elevation', 0.0))
    return place_name, latitude, longitude, timezone_hrs, elevation

def parse_location_tuple(result):
    """
    Normalize the OLD-style tuple returned by utils.get_location(place_name)
    into the same (place_name, latitude, longitude, timezone, elevation)
    shape as parse_location_record(), tolerating either a 4-tuple (no
    elevation) or 5-tuple (with elevation) result.
    Returns None if `result` is falsy.
    NOTE: one duplicated copy of this logic (in horo_chart_tabs.py) used to
    unpack `result` directly assuming exactly 5 values, e.g.:
        self._place_name, self._latitude, ... , self._elevation = result
    That silently raises ValueError if utils.get_location() ever returns a
    4-tuple. This helper is defensive against that on behalf of every
    caller, in one place.
    """
    if not result:
        return None
    place_name = result[0]
    latitude = result[1]
    longitude = result[2]
    timezone_hrs = result[3]
    elevation = float(result[4]) if len(result) >= 5 else 0.0
    return place_name, latitude, longitude, timezone_hrs, elevation

class PlaceWidget(QWidget):
    """
    Reusable place input widget with:
      - QLineEdit
      - dynamic QCompleter
      - debounced search via utils.search_places_contains()
      - place resolution via utils.get_location_record()

    Signals:
      placeSelected(str)        -> emitted with the selected / resolved display label
      locationResolved(dict)    -> emitted with resolved location record
      locationLookupFailed(str) -> emitted when place could not be resolved
      textEditedSignal(str)     -> emitted when user edits text
    """

    placeSelected = pyqtSignal(str)
    locationResolved = pyqtSignal(dict)
    locationLookupFailed = pyqtSignal(str)
    textEditedSignal = pyqtSignal(str)

    def __init__(
        self,
        parent=None,
        initial_text="",
        placeholder_text="Enter place of birth, country name",
        tooltip_text="Enter place of birth, country name",
        min_chars=2,
        debounce_ms=150,
        max_visible_items=None,
        max_search_items = None,
        auto_load_database=False,
    ):
        super().__init__(parent)
        if max_visible_items is None: max_visible_items = const.maximum_visible_search_places_in_UI
        if max_search_items is None: max_search_items = const.maximum_queried_search_places
        self.max_search_items = max_search_items
        self._min_chars = min_chars
        self._debounce_ms = debounce_ms
        self._selection_in_progress = False
        self._popup_mouse_down = False
        self._ignore_next_editing_finished = False
        # Text the USER typed that has not been resolved yet (None = nothing pending).
        # QLineEdit.editingFinished fires on focus-out whenever the contents changed since the last emission -- and a
        # programmatic setText() (ChartTabbed.place(), the IP-geolocation name, a resolved record) counts as a change.
        # So focus-out alone must NOT be treated as "the user entered a place"; only text the user actually typed
        # (textEdited is emitted for user edits only) is resolved.
        self._pending_user_text = None
        if auto_load_database:
            utils.use_database_for_world_cities(True)

        self._line_edit = QLineEdit(initial_text, self)
        self._line_edit.setPlaceholderText(placeholder_text)
        self._line_edit.setToolTip(tooltip_text)

        self._completer_model = QStringListModel()
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(max_visible_items)

        self._line_edit.setCompleter(self._completer)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._update_completions)

        # Signals
        self._line_edit.textEdited.connect(self._on_text_edited)

        # IMPORTANT:
        # Use returnPressed for manual commit
        self._line_edit.returnPressed.connect(self._on_return_pressed)

        # Keep editingFinished, but guard it carefully
        self._line_edit.editingFinished.connect(self._on_editing_finished)

        # Completer selection
        self._completer.activated.connect(self._on_place_selected)

        # Track mouse press on popup so editingFinished doesn't hijack selection
        popup = self._completer.popup()
        popup.pressed.connect(self._on_popup_pressed)
        popup.clicked.connect(self._on_popup_pressed)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._line_edit)

    # --------------------------------------------------------
    # Public helpers
    # --------------------------------------------------------
    def lineEdit(self):
        return self._line_edit

    def text(self):
        return self._line_edit.text()

    def setText(self, text):
        self._line_edit.setText(text)

    def setPlaceholderText(self, text):
        self._line_edit.setPlaceholderText(text)

    def setToolTip(self, text):
        self._line_edit.setToolTip(text)

    def setMinChars(self, value: int):
        self._min_chars = max(1, int(value))

    def setDebounceMs(self, value: int):
        self._debounce_ms = max(0, int(value))

    def resize_to_text(self):
        """
        Resize the internal line edit to fit its CURRENT text.
        Consolidates the 4x-duplicated _resize_place_text_size() method that
        used to live separately in horo_chart.py, horo_chart_tabs.py,
        panchangam.py and vedic_calendar.py. Two of those four copies
        (panchangam.py, vedic_calendar.py) had independently patched in a
        guard for empty text falling back to a sample width; the other two
        (horo_chart.py, horo_chart_tabs.py) never got that fix. This single
        implementation always has the guard, so every caller gets it for
        free.
        """
        pt = self._line_edit.text()
        if not pt:
            pt = _SIZE_SAMPLE_TEXT
        f = QFont("", 0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._line_edit.setFixedSize(pw, ph)
        self._line_edit.adjustSize()

    def reset_size(self):
        """
        Resize the internal line edit back to a fixed sample-text width
        (used after a location lookup succeeds/fails, so the field settles
        to a consistent width rather than whatever the last typed text was).
        Consolidates the 4x-duplicated _reset_place_text_size() method.
        """
        pt = _SIZE_SAMPLE_TEXT
        f = QFont("", 0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._line_edit.setFixedSize(pw, ph)
        self._line_edit.adjustSize()
        self._line_edit.selectionStart()
        self._line_edit.setCursorPosition(0)

    # --------------------------------------------------------
    # Internal UI handlers
    # --------------------------------------------------------
    def _on_text_edited(self, text):
        self._pending_user_text = text
        self.textEditedSignal.emit(text)
        self._search_timer.start(self._debounce_ms)

    def _has_uncommitted_user_text(self):
        """ True only if the current text is what the user typed and it has not been resolved yet.
            Text set by the program (setText) is never 'uncommitted': it differs from the last typed text, or no text
            was typed at all.  """
        pending = self._pending_user_text
        return pending is not None and self._line_edit.text().strip() == pending.strip()

    def _update_completions(self):
        text = self._line_edit.text().strip()

        if len(text) < self._min_chars:
            self._completer_model.setStringList([])
            self._completer.popup().hide()
            return

        suggestions = utils.search_places_contains(text, limit=self.max_search_items)
        self._completer_model.setStringList(suggestions)

        popup = self._completer.popup()
        popup.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)

        if suggestions and self._line_edit.hasFocus():
            # IMPORTANT:
            # We already filtered suggestions in Python.
            # Prevent QCompleter from re-filtering against the typed text.
            self._completer.setCompletionPrefix("")

            fm = popup.fontMetrics()
            widest = max(fm.horizontalAdvance(s) for s in suggestions)
            padding = 40
            popup_width = max(self._line_edit.width(), widest + padding)

            popup.setMinimumWidth(popup_width)
            popup.resize(popup_width, popup.sizeHint().height())

            self._completer.complete()
        else:
            popup.hide()

    def _on_popup_pressed(self, *_):
        # Mouse click on popup is starting a real selection
        self._popup_mouse_down = True
        self._selection_in_progress = True

    def _on_place_selected(self, text):
        selected_text = str(text).strip()
        if not selected_text:
            self._popup_mouse_down = False
            self._selection_in_progress = False
            self._ignore_next_editing_finished = False
            return
    
        # A real popup selection is happening now.
        # editingFinished often fires immediately afterward due to focus change.
        # We must ignore that one extra editingFinished event.
        self._selection_in_progress = True
        self._ignore_next_editing_finished = True
    
        self._resolve_and_emit(selected_text)
    
        # clear selection flags after current event loop cycle
        QtCore.QTimer.singleShot(0, self._clear_selection_guard)

    def _clear_selection_guard(self):
        self._selection_in_progress = False
        self._popup_mouse_down = False

    def _on_return_pressed(self):
        """
        Manual commit by pressing Enter in the line edit.
        If popup is open and has suggestions, let user choose;
        don't prematurely resolve ambiguous partial text.
        """
        text = self._line_edit.text().strip()
        if not text:
            return
        if not self._has_uncommitted_user_text():
            return          # nothing new was typed: do not re-resolve (also stops Enter resolving twice)

        popup = self._completer.popup()

        # If popup is visible, user is in the middle of choosing.
        # Don't force resolution here.
        if popup.isVisible():
            return

        self._resolve_or_disambiguate(text)

    def _on_editing_finished(self):
        """
        Guard against focus-loss firing when clicking/selecting from the popup.
    
        Important:
        After a real completer selection, Qt may still emit editingFinished.
        In that case we must ignore exactly one editingFinished event,
        otherwise the same selection gets resolved twice.
        """
        popup = self._completer.popup()
    
        # Ignore the first editingFinished immediately after popup selection
        if self._ignore_next_editing_finished:
            self._ignore_next_editing_finished = False
            return
    
        # If popup selection is in progress or popup is visible, do nothing
        if self._selection_in_progress or self._popup_mouse_down or popup.isVisible():
            return
    
        text = self._line_edit.text().strip()
        if not text:
            return
        if not self._has_uncommitted_user_text():
            return          # focus left the box but the user typed nothing new (text may have been set by the program)
    
        self._resolve_or_disambiguate(text)

    def _resolve_or_disambiguate(self, text):
        """
        If exact alias is ambiguous (e.g. 'Pune'), show exact choices.
        Otherwise emit/place-resolve normally.
        """
        exact_labels = utils.get_exact_alias_labels(text, limit=30)
        if len(exact_labels) > 1:
            self._completer_model.setStringList(exact_labels)

            popup = self._completer.popup()
            popup.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)

            if self._line_edit.hasFocus():
                self._completer.setCompletionPrefix("")

                fm = popup.fontMetrics()
                widest = max(fm.horizontalAdvance(s) for s in exact_labels)
                padding = 40
                popup_width = max(self._line_edit.width(), widest + padding)

                popup.setMinimumWidth(popup_width)
                popup.resize(popup_width, popup.sizeHint().height())
                self._completer.complete()

            return

        # No ambiguity -> resolve directly
        self._resolve_and_emit(text)

    def _resolve_and_emit(self, text):
        selected_text = str(text).strip()
        self._pending_user_text = None      # this text is being resolved now, whatever the outcome
    
        # Let utils parse alias — canonical if present
        rec = utils.get_location_record(selected_text)
    
        if not rec:
            self.locationLookupFailed.emit(selected_text)
            return
    
        # IMPORTANT: keep exactly what the user selected visible
        self._line_edit.setText(selected_text)
    
        # Emit selected text AS SHOWN
        self.placeSelected.emit(selected_text)
        self.locationResolved.emit(rec)
    
        