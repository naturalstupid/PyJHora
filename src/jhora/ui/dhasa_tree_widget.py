#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Standalone, embeddable, lazy accordion-style Dhasa tree widget.
Behavior:
    - Level 1 (Maha Dasa) starts as a flat list of all top-level dhasa lords.
    - Expanding any row:
        1. HIDES all its sibling rows (only one branch visible on screen at
           any time) - accordion behavior.
        2. LAZILY fetches its children (ONE level down only, never more)
           via dhasa_selector.get_dhasa_children(...) and displays them
           indented one level further. Already-loaded children are never
           re-fetched.
    - Collapsing a row restores its hidden siblings; its own children stay
      cached (Qt keeps them attached, just hidden by the collapse) so
      re-expanding is instant, no recompute.
    - Repeats down to `max_levels` (default 6: Maha/Antara/Prathyanthara/
      Sookshma/Praana/Deha).
    - NO internal banner - the host app already displays the dhasa
      calculation options used (e.g. use_tribhagi_variation=..., seed_star=...)
      above this widget, so no separate header/banner label lives here.
    - Column widths auto-resize after every expand/collapse.
    - Columns: [Label, Level, Starts At, Ends At]. The "Level" column shows
      Maha/Antara/Prathyanthara/Sookshma/Praana/Deha as its OWN column
      (header left blank - no single settled NLS term exists for "which
      dasha-level is this row", only the individual level names themselves).
    - NOT editable, via THREE independent, redundant layers.
    - GRACEFUL UNAVAILABLE-DHASA HANDLING: if a selected dhasa has no
      _root_nodes/_immediate_children wrapper pair registered yet in
      dhasa_selector.py, this widget shows a single, friendly, non-crashing
      message row instead of an error/traceback - both when first showing a
      dhasa (show_dhasa) and when expanding into an unsupported deeper level
      (_load_children, e.g. a dhasa whose root works but whose children
      wrapper isn't written yet).
    - ZERO-DURATION ROW HANDLING (see _make_item / _load_children):
        A dhasa level whose own start == end (a legitimate outcome for some
        dhasas, e.g. Narayana Dasa's second 12-year cycle, where a rasi
        whose first-cycle allotment already used the full per-rasi total
        legitimately gets a zero-length second-cycle period) is, by design,
        simply NOT given an expand arrow in the first place (_make_item) --
        there is nothing further to distinguish by expanding a zero-width
        span, so this is both the cleanest UX and avoids needlessly
        cascading identical timestamps down every remaining level.
        As a defense-in-depth safety net (belt-and-suspenders, in case a
        row's own start/end do NOT indicate zero duration but its
        dhasa-specific get_dhasa_children() call still legitimately returns
        no rows for some other reason), _load_children ALSO handles an
        empty, exception-free `rows` result gracefully: it immediately
        restores any hidden sibling rows (exactly as a collapse would) and
        adds a small explanatory leaf, instead of leaving the tree "stuck"
        with its siblings permanently hidden and no expand arrow left on
        the current row to trigger a collapse. Previously, this combination
        (siblings hidden on expand + zero children loaded + no arrow left
        to collapse with) left the tree UI unrecoverable except by
        re-calling show_dhasa() from outside the widget.
    - NOT editable, via THREE independent, redundant layers.
    - ALL EXCEPTIONS (not just the graceful "not available yet" case) are
      ALWAYS printed to the console with a full traceback, unconditionally -
      NOT gated behind the _DEBUG_ flag. _DEBUG_ only controls the extra
      verbose step-by-step tracing prints (tree population counts, click/
      expand/collapse events) used earlier for diagnosing the duplicate-MD-
      row bug; it does NOT gate error visibility. This means any future
      error can always be copy-pasted from the console regardless of
      whether _DEBUG_ is on.
This widget is 100% dhasa-agnostic: it only ever consumes
    (lords, label, start, end)
rows from dhasa_selector.get_dhasa_root_nodes(...) / get_dhasa_children(...).
All dhasa-specific lord -> NLS-label conversion lives in the corresponding
per-dhasa wrapper functions in dhasa_selector.py - never here.
"""
import sys
import traceback
from PyQt6.QtWidgets import (QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                              QWidget, QAbstractItemView, QStyledItemDelegate)
from PyQt6.QtCore import Qt
from jhora import utils
from jhora.horoscope.dhasa import dhasa_selector
_DEBUG_ = False
_DUMMY_CHILD_TAG = '__dhasa_lazy_placeholder__'
_DEFAULT_MAX_LEVELS = 6
# Resource-string keys for each of the 6 levels, in order
# (Maha, Antara, Prathyanthara, Sookshma, Praana, Deha).
_LEVEL_NAME_KEYS = ['maha_str', 'antara_str', 'prathyanthara_str',
                    'sookshma_str', 'praana_str', 'deha_str']
# Friendly, non-crashing message shown when a dhasa (or one of its deeper
# levels) has no wrapper functions registered yet in dhasa_selector.py.
# Kept as a single, easily-editable format string so wording/localization
# can be adjusted in one place.
_UNAVAILABLE_MESSAGE_TEMPLATE = "{dhasa_label} dhasa is not available yet"
# Shown (as a small non-expandable leaf) on the rare defense-in-depth path
# where get_dhasa_children() returns zero rows without raising an exception,
# even though the parent row's own start/end did not already indicate a
# zero-duration span (see class docstring, "ZERO-DURATION ROW HANDLING").
_NO_FURTHER_BREAKDOWN_MESSAGE = "(no further sub-periods)"
# Two date/time tuples (Y, M, D, fractional_hour) are treated as denoting the
# SAME instant - i.e. a zero-duration dhasa period - if they agree on
# calendar date and their fractional-hour values differ by less than this
# many hours (a generous 1-second tolerance), guarding only against
# insignificant floating-point noise, never against a genuinely different
# (even if very short) real period.
_ZERO_DURATION_TOLERANCE_HOURS = 1.0 / 3600.0
def _is_zero_duration(start_tuple, end_tuple):
    """
    True if `start_tuple` and `end_tuple` (each (Y, M, D, fractional_hour))
    denote the same instant, within a small floating-point tolerance - i.e.
    this dhasa period's own span is (for all practical purposes) zero.
    """
    if not start_tuple or not end_tuple:
        return False
    y1, m1, d1, fh1 = start_tuple
    y2, m2, d2, fh2 = end_tuple
    if (y1, m1, d1) != (y2, m2, d2):
        return False
    return abs(fh1 - fh2) < _ZERO_DURATION_TOLERANCE_HOURS
def _print_exception(context_label, exc):
    """
    Always prints a full traceback for exc to the console, prefixed with
    context_label (e.g. 'DhasaTreeWidget.show_dhasa'), UNCONDITIONALLY -
    never gated behind _DEBUG_. This is the single place that guarantees
    any error encountered anywhere in this widget is visible in the
    console and can be copy-pasted for troubleshooting, regardless of the
    _DEBUG_ setting.
    """
    print(f"[DhasaTreeWidget] {context_label} error: {exc}")
    traceback.print_exc()
class _NoEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None
def _set_treewidget_font_size(tree, font_size):
    font = tree.font()
    font.setPointSizeF(font_size)
    tree.setFont(font)
    tree.header().setFont(font)
class DhasaTreeWidget(QWidget):
    """
    Call show_dhasa(...) to (re)populate the tree's root (Maha Dasa) level
    for a specific dhasa type/name/date-of-birth selection.
    """
    def __init__(self, level_name_keys=None, max_levels=_DEFAULT_MAX_LEVELS,
                 tree_font_size=9, level_column_header='', show_borders=False, parent=None):
        super().__init__(parent)
        if _DEBUG_: print(f"[DEBUG] DhasaTreeWidget.__init__ CALLED - id(self)={id(self)}")
        self._max_levels = max_levels
        self._level_name_keys = level_name_keys or _LEVEL_NAME_KEYS
        v_layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels([
            utils.resource_strings['dhasa_str'],
            level_column_header,
            utils.resource_strings['starts_at_str'],
            utils.resource_strings['ends_at_str'],
        ])
        _set_treewidget_font_size(self.tree, tree_font_size)
        # --- Not editable: 3 independent, redundant guards -------------------
        # 1. Disable every built-in edit-start gesture at the view level.
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 2. Strip the editable flag per-item too (see _make_item).
        # 3. Custom delegate whose createEditor() always returns None - makes
        #    editor creation structurally impossible regardless of trigger/flag.
        self._no_edit_delegate = _NoEditDelegate(self.tree)
        self.tree.setItemDelegate(self._no_edit_delegate)
        # ---------------------------------------------------------------------
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemCollapsed.connect(self._on_item_collapsed)
        self.tree.itemClicked.connect(self._on_item_clicked)
        v_layout.addWidget(self.tree)
        self.setLayout(v_layout)
        self.set_show_borders(show_borders)
    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------
    def set_show_borders(self, show_borders: bool):
        self._show_borders = show_borders
        selection_rule = (
            "QTreeView::item:selected { background: #cce5ff; color: #000000; }"
        )
        if show_borders:
            self.tree.setStyleSheet(
                "QTreeView::item { border: 1px solid palette(mid); padding: 2px; }"
                + selection_rule
            )
            header_font = self.tree.header().font()
            header_font.setBold(True)
            self.tree.header().setFont(header_font)
            self.tree.header().setStyleSheet(
                "QHeaderView::section { font-weight: bold; border: 2px solid palette(dark); padding: 4px; }"
            )
        else:
            self.tree.setStyleSheet(selection_rule)
            header_font = self.tree.header().font()
            header_font.setBold(False)
            self.tree.header().setFont(header_font)
            self.tree.header().setStyleSheet("")
    def show_dhasa(self, dhasa_type_index, dhasa_name, dob, tob, place,
                    divisional_chart_factor=1, **kwargs):
        """ (Re)populate the tree's root (Maha Dasa) level for a dhasa selection. """
        if _DEBUG_: print(f"[DEBUG] show_dhasa() CALLED - tree id={id(self.tree)}, "
              f"dhasa_name={dhasa_name}, top_level_count_BEFORE_clear={self.tree.topLevelItemCount()}")
        self.tree.clear()
        if _DEBUG_: print(f"[DEBUG] show_dhasa() after clear() - top_level_count={self.tree.topLevelItemCount()}")
        try:
            md_rows = dhasa_selector.get_dhasa_root_nodes(
                dhasa_type_index, dhasa_name, dob, tob, place,
                divisional_chart_factor=divisional_chart_factor, **kwargs)
        except AttributeError as e:
            # Graceful path: dhasa not registered yet. Still print to console
            # (unconditionally) so it's clear in the log WHY the friendly
            # message is showing, even though the UI itself stays clean.
            _print_exception(f"show_dhasa('{dhasa_name}') - not yet supported", e)
            self._show_unavailable_message(dhasa_name)
            return
        except Exception as e:
            _print_exception(f"show_dhasa('{dhasa_name}')", e)
            self.tree.addTopLevelItem(QTreeWidgetItem([f"(error computing root dhasa: {e})"]))
            return
        if _DEBUG_: print(f"[DEBUG] show_dhasa() got {len(md_rows)} raw md_rows from dhasa_selector: "
              f"{[r[0] for r in md_rows]}")   # prints just the lords tuples for brevity
        base_kwargs = {'jd_at_dob': utils.julian_day_number(dob, tob), 'place': place,
                       'divisional_chart_factor': divisional_chart_factor, **kwargs}
        for lords, label, start, end in md_rows:
            meta = {'dhasa_name': dhasa_name, 'dhasa_type_index': dhasa_type_index,
                     'lords': lords, 'label': label, 'start': start, 'end': end,
                     'level': 1, 'kwargs': base_kwargs}
            self.tree.addTopLevelItem(self._make_item(meta))
        self._autosize_columns()
        if _DEBUG_: print(f"[DEBUG] show_dhasa() FINISHED - top_level_count_AFTER={self.tree.topLevelItemCount()}")
    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------
    def _show_unavailable_message(self, dhasa_label):
        """
        Shows a single, friendly, non-technical message row instead of
        crashing or showing a raw exception, when a dhasa has no wrapper
        functions registered yet in dhasa_selector.py.
        """
        message = _UNAVAILABLE_MESSAGE_TEMPLATE.format(dhasa_label=dhasa_label)
        item = QTreeWidgetItem([message, '', '', ''])
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.tree.addTopLevelItem(item)
        self._autosize_columns()
    def _autosize_columns(self):
        for col in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(col)
    def _level_name(self, level):
        idx = min(level - 1, len(self._level_name_keys) - 1)
        key = self._level_name_keys[idx]
        return utils.resource_strings[key]
    def _date_text(self, date_tuple):
        if not date_tuple:
            return ''
        y, m, d, fh = date_tuple
        return f"{y:04d}-{m:02d}-{d:02d} " + utils.to_dms(fh)
    def _make_item(self, meta):
        level_name = self._level_name(meta['level'])
        item = QTreeWidgetItem([
            meta['label'],
            level_name,
            self._date_text(meta['start']),
            self._date_text(meta['end']),
        ])
        item.setData(0, Qt.ItemDataRole.UserRole, meta)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        # A zero-duration period (this row's own start == end) has nothing
        # further to distinguish by expanding it: every one of its would-be
        # children (at every remaining level, all the way to Deha) would
        # simply repeat that same identical instant. Rather than let the
        # user open such a row (which, before this fix, could also leave
        # the tree UI permanently stuck if the underlying dhasa's children
        # function then legitimately returned nothing - see class
        # docstring, "ZERO-DURATION ROW HANDLING"), such rows are simply
        # given no expand placeholder at all: no arrow is shown, and
        # clicking them does nothing (matching _on_item_clicked's existing
        # "only toggle expand if childCount() > 0" rule, unchanged below).
        if meta['level'] < self._max_levels and not _is_zero_duration(meta['start'], meta['end']):
            item.addChild(QTreeWidgetItem([_DUMMY_CHILD_TAG]))
        return item
    def _siblings_of(self, item):
        parent = item.parent()
        if parent is None:
            return [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())
                    if self.tree.topLevelItem(i) is not item]
        return [parent.child(i) for i in range(parent.childCount()) if parent.child(i) is not item]
    def _restore_siblings(self, item):
        """
        Un-hides every sibling of `item` (the same effect _on_item_collapsed
        has). Used both by the normal collapse path and, defensively, by
        _load_children when zero children are loaded for a row that was
        already expanded (see class docstring, "ZERO-DURATION ROW HANDLING")
        - so the tree can never end up with permanently hidden siblings and
        no remaining way (via the UI) to bring them back.
        """
        for sib in self._siblings_of(item):
            sib.setHidden(False)
    def _on_item_clicked(self, item, column):
        """ Single click anywhere on a row toggles expand/collapse. """
        if item is None:
            return
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        lords = meta['lords'] if meta else '?'
        if _DEBUG_: print(f"[DEBUG] _on_item_clicked - lords={lords}, was_expanded={item.isExpanded()}, "
              f"childCount={item.childCount()}, top_level_count={self.tree.topLevelItemCount()}")
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
    def _on_item_expanded(self, item):
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        lords = meta['lords'] if meta else '?'
        if _DEBUG_: print(f"[DEBUG] _on_item_expanded FIRED - lords={lords}, "
              f"top_level_count={self.tree.topLevelItemCount()}, "
              f"childCount_before_load={item.childCount()}")
        for sib in self._siblings_of(item):
            sib.setHidden(True)
        if item.childCount() == 1 and item.child(0).text(0) == _DUMMY_CHILD_TAG:
            placeholder = item.child(0)
            meta = item.data(0, Qt.ItemDataRole.UserRole)
            item.removeChild(placeholder)
            if meta is not None:
                self._load_children(item, meta)
        self._autosize_columns()
        if _DEBUG_: print(f"[DEBUG] _on_item_expanded DONE - top_level_count_after={self.tree.topLevelItemCount()}, "
              f"childCount_after={item.childCount()}")
    def _load_children(self, item, meta):
        try:
            rows = dhasa_selector.get_dhasa_children(
                meta['dhasa_name'], meta['lords'], meta['start'],
                parent_end=meta['end'], **meta['kwargs'])
        except AttributeError as e:
            # Graceful path: not yet supported at this level. Still print to
            # console (unconditionally) so it's clear WHY the friendly
            # message is showing, even though the UI itself stays clean.
            _print_exception(
                f"_load_children('{meta['dhasa_name']}', lords={meta['lords']}) - not yet supported", e)
            message = _UNAVAILABLE_MESSAGE_TEMPLATE.format(dhasa_label=meta['dhasa_name'])
            leaf = QTreeWidgetItem([message])
            leaf.setFlags(leaf.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.addChild(leaf)
            return
        except Exception as e:
            # THIS is the fix: previously this branch only printed when
            # _DEBUG_ was True. Now it ALWAYS prints a full traceback to the
            # console, unconditionally, so any future error here can be
            # copy-pasted straight from the console regardless of _DEBUG_.
            _print_exception(
                f"_load_children('{meta['dhasa_name']}', lords={meta['lords']})", e)
            leaf = QTreeWidgetItem([f"(error: {e})"])
            leaf.setFlags(leaf.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.addChild(leaf)
            return
        if not rows:
            # Defense-in-depth safety net (see class docstring, "ZERO-DURATION
            # ROW HANDLING"): this row's own start/end did not already flag
            # it as zero-duration in _make_item (otherwise no expand
            # placeholder would have been added, and we would never get
            # here), yet its dhasa-specific children function still
            # legitimately returned zero rows without raising. Rather than
            # leave this row expanded-but-childless (which would permanently
            # hide its siblings with no remaining UI action able to restore
            # them - no expand arrow survives once childCount stays 0, so
            # neither a click nor a manual collapse attempt can fire
            # _on_item_collapsed), explicitly restore sibling visibility
            # right now, exactly as a normal collapse would, and add a
            # single explanatory leaf so the row still shows why nothing
            # expanded further.
            _print_exception_note = (
                f"[DhasaTreeWidget] _load_children('{meta['dhasa_name']}', lords={meta['lords']}) "
                f"returned no rows without raising - restoring sibling visibility."
            )
            if _DEBUG_: print(_print_exception_note)
            leaf = QTreeWidgetItem([_NO_FURTHER_BREAKDOWN_MESSAGE])
            leaf.setFlags(leaf.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.addChild(leaf)
            self._restore_siblings(item)
            return
        for lords, label, start, end in rows:
            child_meta = {'dhasa_name': meta['dhasa_name'],
                           'dhasa_type_index': meta['dhasa_type_index'],
                           'lords': lords, 'label': label, 'start': start, 'end': end,
                           'level': meta['level'] + 1, 'kwargs': meta['kwargs']}
            item.addChild(self._make_item(child_meta))
    def _on_item_collapsed(self, item):
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        lords = meta['lords'] if meta else '?'
        if _DEBUG_: print(f"[DEBUG] _on_item_collapsed FIRED - lords={lords}, "
              f"top_level_count={self.tree.topLevelItemCount()}")
        self._restore_siblings(item)
        self._autosize_columns()
if __name__ == "__main__":
    from jhora.panchanga.drik import Date, Place
    horoscope_language = 'ta'
    utils.set_language(horoscope_language)
    dob = Date(1996, 12, 7); tob = (10, 34, 0)
    place = Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    app = QApplication(sys.argv)
    w = DhasaTreeWidget(show_borders=True)
    import random
    from jhora import const
    dhasa_name = random.choice(const.supported_dhasas)
    dhasa_name = "varsha_vimsottari"
    print("Random Dhasa Picked", dhasa_name)
    w.show_dhasa(0, dhasa_name, dob, tob, place, divisional_chart_factor=1)
    # Try an unregistered dhasa to see the graceful message instead:
    # w.show_dhasa(0, 'ashtottari', dob, tob, place, divisional_chart_factor=1)
    w.resize(700, 400)
    w.show()
    sys.exit(app.exec())
    error_dasas = ['rashmi','ashtaka_varga_planet']
