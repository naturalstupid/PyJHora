#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Dhasa / Bhukthi page (/dhasa).
Computes the dhasa of the chosen type (Graha, Raasi or Annual) and name and shows it as a drill-down
list: Maha -> Antara -> Prathyanthara -> Sookshma -> Praana -> Deha (6 levels). The children of a row
are computed when it is first opened.
Only one path is open at a time. The open chain is shown as breadcrumb rows with the deepest row
highlighted and its children listed below it. Clicking a child opens it; clicking the deepest row
collapses one level; clicking another breadcrumb row jumps back to that level.
Controls: Dhasa Type, Dhasa, Varga (Annual dhasas only), Dhasa Options (a dialog whose fields depend
on the dhasa) and Running Dhasa (a dialog that shows the running dhasa chain for a given date and
year-duration type). The option lists below (seed_list_dhasas, tribhagi_dhasas, ...) are the same as
in jhora's dhasa_bhukthi_options_dialog.
Dhasa Options are PERSISTED PER DHASA in app.storage.user (via `state`, under
_DHASA_OPTIONS_KEY, one entry per (dhasa_type_index, dhasa_name) - see _get_dhasa_options() /
_set_dhasa_options()) - NOT in a plain local dict. This matters: a plain local dict (used by an
earlier version of this page) is recreated empty every time dhasa_page() itself re-runs, and this
was confirmed to happen around window.print() in at least one browser/printer-driver combination -
the symptom was a customized dhasa's options (e.g. Tribhagi for Yoga Vimsottari) surviving an
ordinary same-session dhasa switch perfectly well, but being silently lost specifically right after
printing. Storing the options in app.storage.user instead (the same mechanism birth_store.py's own
docstring explains is used for exactly this reason - it is keyed by a persistent browser identity,
not tied to the specific live connection) fixes this, matching how every other per-browser setting
on this page (and the rest of the app) already survives a reconnect.
The CURRENTLY SELECTED Dhasa Type / Dhasa / Varga are ALSO persisted the same way (_DHASA_SELECTION_
KEY, see _get_selection()/_set_selection()) - NOT just hardcoded to index 0 on every page build. This
was a second instance of the exact same reconnect bug: a page reconnect (confirmed around printing)
rebuilds the Dhasa Type/Dhasa/Varga selectors from scratch with their literal default value=0, which
looked like "the combo reverts to the first dhasa after printing" even though nothing about the
visitor's own choice actually changed - it is the WIDGET that is new, not the selection being reset.
Fixed the same way as the options bug: read the persisted selection when building the selectors
(instead of hardcoding value=0), and write it back on every real selection change. Switching the
Dhasa Type itself still resets the Dhasa name to the first one in the new type's list (that part IS
a real, correct reset, since the old dhasa name belongs to the old type) - see
_on_dhasa_type_changed() vs. the initial-build code for how the two cases are told apart.
"Print / Save as PDF" prints only the Maha Dasa (root) level as a plain table - NOT the full,
interactive drill-down tree (which has icons, breadcrumbs and click handlers that do not belong in
a printout), and NOT the Running Dhasa dialog's result. This is a deliberate scope decision: a deep,
fully-expanded 6-level tree for most dhasas would be an unreasonably long printout, and only the
current selection (not "every dhasa") is meant to be printable here. See components.py's '.print-only'
utility for how the two views (interactive tree vs. plain print table) stay independent. The single
print table reuses the SAME '.dhasa-report-item' / '.dhasa-report-header' print-pagination classes as
"Print Multiple Dhasas" below (see that feature's own note for what these fix and why), since a single
dhasa's own Maha Dasa table can be just as tall as any one dhasa in the multi-dhasa report.
"Print Multiple Dhasas" additionally offers printing every dhasa in one or more categories (Graha /
Annual / Raasi), one page per dhasa, Maha Dasa level only, in a hidden multi-page report (see
components.py's '.dhasa-report-item' / '.dhasa-report-header' for the print-pagination rules this
needs - a dhasa's own header is kept attached to the start of its table, while a long table can still
span further pages on its own). "Selected dhasa only" mode in this dialog uses the current dhasa's
OWN persisted options (_get_dhasa_options()) and, for an Annual dhasa, its own Varga selection.
"By category" mode uses D1 (Rasi) varga for every dhasa regardless of any dhasa's own persisted
varga choice (looping every varga for every annual dhasa in the category would be too slow - see
that mode's own tooltip), but DOES still apply each dhasa's own persisted non-varga options (e.g. a
Tribhagi choice for Vimsottari) if this browser customized it earlier - confirmed from an actual
printed PDF that an earlier version of this mode ignored that customization and always printed
every dhasa's bare defaults instead, which is not what was wanted.
IMPORTANT (print): the lone `ui.separator()` between the control bar and the tree/print-table area
is explicitly marked 'no-print' - this was a genuine bug, found after a LATER printed PDF still
showed a BLANK first page for the single-dhasa print despite '.dhasa-report-item' already carrying
`page-break-before: avoid`. Root cause: that rule only suppresses an OPTIONAL page break, it cannot
override an element genuinely NOT FITTING the remaining vertical space on a page - and this
separator (previously un-marked, so still visible during print) occupied a sliver of page 1 above
the print table. Since the table's own header ('.dhasa-report-header') is explicitly atomic (kept
whole and attached to the start of the table via `break-inside: avoid` / `break-after: avoid`), if
that atomic unit did not fit in whatever space remained on page 1 after the separator, the ENTIRE
unit had to move to page 2 regardless of the `avoid` rule - leaving page 1 showing only the (mostly
invisible, whitespace-only) separator. Marking the separator 'no-print' removes it from the printed
flow entirely, so the print table is now the FIRST thing on the page with the full page available
to it.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), defaulting to the first Graha dhasa (Vimsottari in the standard dhasa
dict) at D1 (Rasi), with no customized options - since the registry calls this function HEADLESSLY
(no live Dhasa Type/Dhasa/Varga selectors or persisted-options state exist for a page the visitor
is not currently on; app.storage.user IS still reachable, but reading "whichever dhasa a visitor
once customized" would make the registry's OWN simple default behavior unpredictable across
visitors, so this intentionally always uses the plain, uncustomized default instead). Reuses
_dhasa_root_locked() and _root_rows_table_html(), the SAME functions this page's own
compute_dhasa()/_render_print_table() call.
"""
import time
from datetime import date, datetime
from nicegui import ui, run
from jhora import const, utils, config
from jhora.horoscope.dhasa import dhasa_selector
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
    render_footer, run_io_bound_ctx, 
)
# print_button / trigger_print_js imports REMOVED - this page no longer has its own print button at
# all (see the button-row removal note inside dhasa_page() below for the full reasoning).
import print_registry
_DHASA_OPTIONS_KEY = "dhasa_options_store_v1"
_DHASA_SELECTION_KEY = "dhasa_selection_v1"
def _dhasa_root_locked(dhasa_type_index, dhasa_name, dob, tob, place, dcf, option_kwargs):
    """Computes the root (Maha Dasa level) rows under calc_lock(); the slow part of compute_dhasa(),
    run in a worker thread via components.DelayedBusyIndicator.run(). Deeper levels stay lazily
    computed on demand when a row is expanded (see _ensure_children_loaded()), unaffected by this.
    """
    with calc_lock():
        return dhasa_selector.get_dhasa_root_nodes(
            dhasa_type_index, dhasa_name, dob, tob, place,
            divisional_chart_factor=dcf, **option_kwargs,
        )
def _root_rows_table_html(rows):
    """Returns the Lord / Starts At / Ends At table (as an HTML string) of a dhasa's root (Maha Dasa)
    rows.
    Args:
        rows: list of (lords, label, start, end) tuples - e.g. straight from
            dhasa_selector.get_dhasa_root_nodes(), or the (lords, label, start, end) view of this
            page's own node dicts (see _render_print_table(), which converts its node dicts into
            this exact shape before calling this function - passing the node dicts directly here
            instead raises ValueError: too many values to unpack, since a dict has far more than 4
            keys to iterate over).
    """
    _th_style = 'border:1px solid #5c3a21; padding:4px 8px; background:#f0fdf4; text-align:left; white-space:nowrap;'
    _td_style = 'border:1px solid #d1d5db; padding:4px 8px; white-space:nowrap;'
    html = "<table style='border-collapse:collapse;'>"
    html += (f"<tr><th style='{_th_style}'>{res_str('lord_str', 'Lord')}</th>"
             f"<th style='{_th_style}'>{res_str('starts_at_str', 'Starts At')}</th>"
             f"<th style='{_th_style}'>{res_str('ends_at_str', 'Ends At')}</th></tr>")
    for lords, label, start, end in rows:
        html += (f"<tr><td style='{_td_style}'>{label}</td>"
                 f"<td style='{_td_style}'>{_date_text(start)}</td>"
                 f"<td style='{_td_style}'>{_date_text(end)}</td></tr>")
    html += "</table>"
    return html
def _build_dhasa_report_locked(dob, tob, place_val, lat_val, lon_val, tz_val, dhasa_specs):
    """Computes the Maha Dasa (root) rows for every (dhasa_type_index, dhasa_name, dcf,
    option_kwargs) tuple in `dhasa_specs`, under calc_lock() (one dhasa at a time). Blocking; run in
    a worker thread. A dhasa whose computation fails (e.g. not yet supported - see the AttributeError
    handling elsewhere on this page) is skipped and reported on the console, rather than aborting the
    whole report, same policy as kundali_chart.py's/chart_render.py's all-vargas report.
    Args:
        dhasa_specs: list of (dhasa_type_index, dhasa_name, dcf, option_kwargs) tuples - see
            _build_dhasa_report()'s docstring for how these are assembled from the print dialog.
    Returns:
        List of per-dhasa page dicts: title, rows_html (the table built by _root_rows_table_html()).
    """
    place = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
    pages = []
    for dhasa_type_index, dhasa_name, dcf, option_kwargs in dhasa_specs:
        try:
            with calc_lock():
                rows = dhasa_selector.get_dhasa_root_nodes(
                    dhasa_type_index, dhasa_name, dob, tob, place,
                    divisional_chart_factor=dcf, **(option_kwargs or {}),
                )
        except Exception as e:
            print(f"[dhasa_page] multi-dhasa report: computation failed for "
                  f"dhasa_name={dhasa_name!r} (type={dhasa_type_index}, dcf={dcf}): {type(e).__name__}: {e}")
            continue
        dhasa_type_label = (res_str('graha_str', 'Graha') if dhasa_type_index == 0 else
                            (res_str('raasi_str', 'Raasi') if dhasa_type_index == 1 else res_str('annual_str', 'Annual')))
        dhasa_label = res_str(dhasa_name + '_str', dhasa_name.replace('_', ' ').title())
        title = f"{dhasa_label} {dhasa_type_label} {res_str('dhasa_str', 'Dhasa')} ({res_str('maha_str', 'Maha')} {res_str('dhasa_str', 'Dhasa')})"
        pages.append({'title': title, 'rows_html': _root_rows_table_html(rows)})
    return pages
_MAX_LEVELS = 6  # Maha, Antara, Prathyanthara, Sookshma, Praana, Deha
_LEVEL_NAME_KEYS = ['maha_str', 'antara_str', 'prathyanthara_str', 'sookshma_str', 'praana_str', 'deha_str']
_UNAVAILABLE_MESSAGE_TEMPLATE = "{dhasa_label} dhasa is not available yet"
_NO_FURTHER_BREAKDOWN_MESSAGE = "(no further sub-periods)"
_ZERO_DURATION_TOLERANCE_HOURS = 1.0 / 3600.0
_chart_names = const._chart_names
_division_chart_factors = const.division_chart_factors  # the 24 standard divisional charts (no custom / mixed)
# Option lists: which option fields each dhasa shows (same as jhora's DhasaBhukthiOptionDialog).
# seed_list_dhasas holds the dhasas that offer a seed star.
_tithi_list = ['janma_tithi_str', 'dhana_tithi_str', 'bhrartri_tithi_str', 'matri_tithi_str', 'putra_tithi_str',
             'satru_tithi_str', 'kalatra_tithi_str', 'mrutyu_tithi_str', 'bhagya_tithi_str', 'karma_tithi_str',
             'laabha_tithi_str', 'vyaya_tithi_str']
seed_list_dhasas = {'vimsottari': 3, 'rasi_bhukthi_vimsottari': 3, 'ashtottari': 6, 'yogini': 7, 'shodasottari': 8,
                   'dwadasottari': 27, 'dwisatpathi': 19, 'panchottari': 17, 'satabdika': 27,
                   'chaturaaseeti_sama': 15, 'shashtisama': 1, 'shattrimsa_sama': 22}
dhasa_start_planet_dhasas = ['vimsottari', 'rasi_bhukthi_vimsottari', 'ashtottari', 'yogini', 'shodasottari',
                            'dwadasottari', 'dwisatpathi', 'panchottari', 'satabdika', 'chaturaaseeti_sama',
                            'shashtisama', 'shattrimsa_sama', 'saptharishi_nakshathra']
start_from_moon_dhasas = ['vimsottari', 'rasi_bhukthi_vimsottari', 'ashtottari', 'yogini', 'shodasottari',
                         'dwadasottari', 'dwisatpathi', 'panchottari', 'satabdika', 'chaturaaseeti_sama',
                         'shashtisama', 'shattrimsa_sama', 'saptharishi_nakshathra']
tribhagi_dhasas = ['vimsottari', 'yoga_vimsottari', 'rasi_bhukthi_vimsottari', 'ashtottari', 'tithi_ashtottari',
                  'yogini', 'tithi_yogini', 'shodasottari', 'dwadasottari', 'dwisatpathi', 'panchottari',
                  'satabdika', 'chaturaaseeti_sama', 'karana_chaturaaseethi_sama', 'shashtisama',
                  'shattrimsa_sama', 'saptharishi_nakshathra']
varga_dhasas = ['vimsottari', 'rasi_bhukthi_vimsottari', 'ashtottari', 'yogini', 'shodasottari', 'dwadasottari',
              'dwisatpathi', 'panchottari', 'satabdika', 'chaturaaseeti_sama', 'shashtisama', 'shattrimsa_sama',
              'tara', 'karaka', 'buddhi_gathi', 'saptharishi_nakshathra', 'rashmi', 'ashtaka_varga_planet',
              'ashtaka_varga_pinda', 'narayana', 'lagna_kendraadhi', 'sudasa', 'drig', 'niryaana', 'shoola',
              'karaka_kendraadhi', 'chara', 'lagnamsaka', 'padhanadhamsa', 'mandooka', 'sthira', 'tara_lagna',
              'brahma', 'varnada', 'yogardha', 'navamsa', 'paryaaya', 'trikona', 'kalachakra', 'chakra',
              'sandhya', 'pachaka', 'raashiyanka', 'ashtaka_varga_sign', 'chathurvidha_lagna_utthara',
              'chathurvidha_kendra_utthara', 'chathurvidha_trikona_utthara', 'chathurvidha_dasha_utthara']
antardhasa_option_list = ['vimsottari', 'yoga_vimsottari', 'rasi_bhukthi_vimsottari', 'ashtottari',
                         'tithi_ashtottari', 'yogini', 'tithi_yogini', 'shodasottari', 'dwadasottari',
                         'dwisatpathi', 'panchottari', 'satabdika', 'chaturaaseeti_sama',
                         'karana_chaturaaseethi_sama', 'shashtisama', 'shattrimsa_sama', 'saptharishi_nakshathra']
tithi_dhasas = ['tithi_ashtottari', 'tithi_yogini']
# Running Dhasa dialog: resource keys of the 8 year-duration types, in selector order
# (index = const.dhasa_year_duration_default - 1).
_YEAR_DURATION_KEYS = [
    'mean_sidereal_year_str', 'true_sidereal_year_str', 'mean_tropical_year_str',
    'true_tropical_year_str', 'savana_year_str', 'mean_lunar_year_str',
    'true_lunar_year_str', 'gregorean_year_str',
]
_DLI_LEVEL_KEYS = ['maha_str', 'antara_str', 'prathyanthara_str', 'sookshma_str', 'praana_str', 'deha_str']
def _varga_label(i):
    """Returns the localized name of the divisional chart at index `i` of const.division_chart_factors."""
    return res_str(_chart_names[i], _chart_names[i].replace('_str', '').replace('_', ' ').title())
def _is_zero_duration(start_tuple, end_tuple):
    """Returns True if two (year, month, day, fractional_hours) tuples fall on the same date and are less
    than one second apart.
    """
    if not start_tuple or not end_tuple:
        return False
    y1, m1, d1, fh1 = start_tuple
    y2, m2, d2, fh2 = end_tuple
    if (y1, m1, d1) != (y2, m2, d2):
        return False
    return abs(fh1 - fh2) < _ZERO_DURATION_TOLERANCE_HOURS
def _date_text(date_tuple):
    """Returns 'YYYY-MM-DD HH:MM:SS' for a (year, month, day, fractional_hours) tuple ('' if empty)."""
    if not date_tuple:
        return ''
    y, m, d, fh = date_tuple
    return f"{y:04d}-{m:02d}-{d:02d} " + utils.to_dms(fh)
def _level_name(level):
    """Returns the localized name of dhasa level `level` (1 = Maha .. 6 = Deha)."""
    idx = min(level - 1, len(_LEVEL_NAME_KEYS) - 1)
    return res_str(_LEVEL_NAME_KEYS[idx], _LEVEL_NAME_KEYS[idx].replace('_str', '').title())
def _parse_tob(tob_str, fallback=(12, 0, 0)):
    """Parses a time string 'H:M' or 'H:M:S'.
    Args:
        tob_str: time text.
        fallback: value returned when the text cannot be parsed (default noon).
    Returns:
        (hour, minute, second) tuple.
    """
    try:
        parts = [int(x) for x in str(tob_str).strip().split(':')]
        if len(parts) == 2:
            parts.append(0)
        if len(parts) != 3:
            raise ValueError
        return tuple(parts)
    except Exception:
        return fallback
def _make_node(dhasa_name, dhasa_type_index, lords, label, start, end, level, base_kwargs):
    """Returns the dict describing one tree row.
    Args:
        dhasa_name: dhasa name.
        dhasa_type_index: 0 Graha, 1 Raasi, 2 Annual.
        lords: lords of the row's chain (as returned by dhasa_selector).
        label: row label.
        start, end: (year, month, day, fractional_hours) tuples.
        level: 1 (Maha) .. 6 (Deha).
        base_kwargs: keyword arguments passed on when the children are computed.
    Returns:
        dict with these values plus 'can_expand' (level below the maximum and not a zero-length
        period) and 'children' (None until first opened).
    """
    return {
        'dhasa_name': dhasa_name, 'dhasa_type_index': dhasa_type_index,
        'lords': lords, 'label': label, 'start': start, 'end': end,
        'level': level, 'kwargs': base_kwargs,
        'can_expand': (level < _MAX_LEVELS and not _is_zero_duration(start, end)),
        'children': None,
    }
@ui.page('/dhasa')
def dhasa_page():
    """Dhasa page: control bar, dhasa selectors, option dialogs and the drill-down tree."""
    navigation_header()
    state = ensure_default_state()
    tree_state = {"roots": None, "root_error_message": None, "active_path": [],
                 "print_dob": "", "print_tob": "", "print_place": "",
                 "print_dhasa_name": "", "print_dhasa_type_index": 0}
    def _options_store():
        """Returns this browser's PERSISTED dhasa-options store (a dict, read from `state` i.e.
        app.storage.user) - never a plain local variable. See the module docstring for why: a plain
        local dict is recreated empty every time dhasa_page() itself re-runs, which was confirmed to
        happen around window.print() in at least one browser/printer-driver combination, silently
        losing every dhasa's customization right after printing even though it survived an ordinary
        same-session dhasa switch perfectly well. Returns {} if nothing has been stored yet (or if
        whatever is stored under this key is not a dict, e.g. after a format change).
        """
        store = state.get(_DHASA_OPTIONS_KEY)
        return store if isinstance(store, dict) else {}
    def _options_store_key(key):
        """Returns the persisted-store key for one dhasa, as a PLAIN STRING (not the (type, name)
        tuple used elsewhere on this page) - app.storage.user's underlying storage needs to be able
        to serialize its keys/values, and a bare tuple is not guaranteed to round-trip through that
        the way it does in an ordinary in-memory dict.
        Args:
            key: (dhasa_type_index, dhasa_name) tuple, e.g. from _selected_dhasa_key().
        """
        dhasa_type_index, dhasa_name = key
        return f"{dhasa_type_index}:{dhasa_name}"
    def _get_dhasa_options(key):
        """Returns a COPY of this browser's persisted options for one dhasa, or {} if none are stored.
        Args:
            key: (dhasa_type_index, dhasa_name) tuple.
        """
        return dict(_options_store().get(_options_store_key(key), {}))
    def _set_dhasa_options(key, options):
        """Persists `options` for one dhasa under its own key, in app.storage.user (via `state`) - does
        NOT disturb any other dhasa's stored options, and (unlike a plain local dict) SURVIVES a page
        reconnect (see the module docstring).
        Args:
            key: (dhasa_type_index, dhasa_name) tuple.
            options: keyword-argument dict to store for this dhasa.
        """
        updated_store = _options_store()
        updated_store[_options_store_key(key)] = dict(options)
        state[_DHASA_OPTIONS_KEY] = updated_store
    def _get_selection():
        """Returns this browser's PERSISTED Dhasa Type / Dhasa / Varga selection (a dict), read from
        `state` i.e. app.storage.user - same reconnect-survival reasoning as _get_dhasa_options()
        (see the module docstring). Returns {} if nothing has been stored yet.
        Keys: 'dhasa_type_index' (0/1/2), 'dhasa_name' (string - a NAME, not an index, so a later
        reordering of the dhasa dict for one type cannot silently point this at the wrong dhasa),
        'varga_index' (int, only meaningful for Annual dhasas but harmless to keep for any type).
        """
        sel = state.get(_DHASA_SELECTION_KEY)
        return sel if isinstance(sel, dict) else {}
    def _set_selection(**kwargs):
        """Updates one or more fields of the persisted selection (any field not passed here keeps its
        previous value) and writes the result back to app.storage.user.
        """
        sel = _get_selection()
        sel.update(kwargs)
        state[_DHASA_SELECTION_KEY] = sel
    _db_str = res_str('dhasa_str',"Dhasa")+" / "+res_str('bhukthi_str',"Bhukthi")
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(_db_str).classes('text-xl font-bold text-green-700')
            # Both print_button() AND the former "Print Multiple Dhasas" button/dialog are REMOVED -
            # printing is now exclusively via the ONE global "Save as PDF" button
            # (print_registry.py). This page remains registered there, WITH its own real
            # sub_option_ui (Selected dhasa / By category checkboxes - see
            # _dhasa_sub_option_ui()/_build_print_section() below) replicating exactly what the
            # removed "Print Multiple Dhasas" dialog used to offer, now INSIDE the central dialog
            # instead of this page's own separate one.
        _graha_names = list(const._graha_dhasa_dict.keys())
        _rasi_names = list(const._rasi_dhasa_dict.keys())
        _annual_names = list(const._annual_dhasa_dict.keys())
        _dhasa_type_options = {
            0: res_str('graha_str', 'Graha') + ' ' + res_str('dhasa_str', 'Dhasa'),
            1: res_str('raasi_str', 'Raasi') + ' ' + res_str('dhasa_str', 'Dhasa'),
            2: res_str('annual_str', 'Annual') + ' ' + res_str('dhasa_str', 'Dhasa'),
        }
        _varga_options = {i: _varga_label(i) for i in range(len(_division_chart_factors))}
        def _names_for_type(idx):
            """Returns the dhasa names of the Dhasa Type `idx` (0 Graha, 1 Raasi, 2 Annual)."""
            return _graha_names if idx == 0 else (_rasi_names if idx == 1 else _annual_names)
        # Read the persisted Dhasa Type / Dhasa / Varga selection (if any) so the selectors below
        # are built with the visitor's own LAST choice instead of always defaulting to index 0 - see
        # the module docstring for the reconnect bug this replaces (confirmed around printing).
        _persisted_selection = _get_selection()
        _initial_dhasa_type_index = _persisted_selection.get('dhasa_type_index', 0)
        if not isinstance(_initial_dhasa_type_index, int) or not (0 <= _initial_dhasa_type_index <= 2):
            _initial_dhasa_type_index = 0
        _initial_dhasa_names = _names_for_type(_initial_dhasa_type_index)
        _persisted_dhasa_name = _persisted_selection.get('dhasa_name')
        try:
            _initial_dhasa_name_index = (
                _initial_dhasa_names.index(_persisted_dhasa_name)
                if _persisted_dhasa_name in _initial_dhasa_names else 0
            )
        except Exception:
            _initial_dhasa_name_index = 0
        _initial_varga_index = _persisted_selection.get('varga_index', 0)
        if not isinstance(_initial_varga_index, int) or not (0 <= _initial_varga_index < len(_division_chart_factors)):
            _initial_varga_index = 0
        def _selected_dhasa_name():
            """Returns the name of the dhasa selected in the Dhasa Type and Dhasa selectors."""
            idx = dhasa_type_select.value if isinstance(dhasa_type_select.value, int) else 0
            names = _names_for_type(idx)
            name_idx = dhasa_name_select.value if isinstance(dhasa_name_select.value, int) else 0
            if not (0 <= name_idx < len(names)):
                name_idx = 0
            return names[name_idx]
        def _selected_dhasa_key():
            """Returns (dhasa_type_index, dhasa_name) of the currently selected dhasa - the key used
            to look up/store its options via _get_dhasa_options()/_set_dhasa_options()."""
            idx = dhasa_type_select.value if isinstance(dhasa_type_select.value, int) else 0
            return (idx, _selected_dhasa_name())
        def _dhasa_option_field_specs(dhasa_name):
            """Returns the fields of the Dhasa Options dialog for a dhasa, in display order, following
            const.dhasa_default_options entry by entry.
            Args:
                dhasa_name: dhasa name.
            Returns:
                List of field dicts ('kind': 'combo', 'checkbox' or 'varga', plus kwarg, label, items and
                default); [] if the dhasa has no options.
            """
            defaults = list(const.dhasa_default_options.get(dhasa_name, []))
            if not defaults:
                return []
            counter = 0
            def _next_default(fallback=0):
                nonlocal counter
                val = defaults[counter] if counter < len(defaults) else fallback
                counter += 1
                return val
            specs = []
            # Dhasa-specific fields (mutually exclusive).
            if dhasa_name == 'aayu':
                specs.append({'kind': 'combo', 'kwarg': 'aayur_type',
                               'label': res_str('aayu_dhasa_option_str', 'Aayu Dhasa Type'),
                               'items': [res_str('pindayu_str', 'Pindayu'), res_str('nisargayu_str', 'Nisargayu'),
                                         res_str('amsayu_str', 'Amsayu'), 'None'],
                               'default': _next_default(3), 'special': 'aayur_type'})
            elif dhasa_name == 'naisargika':
                specs.append({'kind': 'checkbox', 'kwarg': 'mahadhasa_lord_has_no_antardhasa',
                               'label': res_str('nisargika_dhasa_option2_str', 'Mahadhasa lord has no antardhasa'),
                               'default': bool(_next_default(False))})
                specs.append({'kind': 'checkbox', 'kwarg': 'antardhasa_option1',
                               'label': res_str('nisargika_dhasa_option3_str', 'Antardhasa option 1'),
                               'default': bool(_next_default(False))})
                specs.append({'kind': 'checkbox', 'kwarg': 'antardhasa_option2',
                               'label': res_str('nisargika_dhasa_option4_str', 'Antardhasa option 2'),
                               'default': bool(_next_default(False))})
            elif dhasa_name == 'tara':
                specs.append({'kind': 'combo', 'kwarg': 'dhasa_method',
                               'label': res_str('tara_dhasa_option1_str', 'Tara Dhasa Method'),
                               'items': [res_str('tara_dhasa_option2_str', 'Method 1'),
                                         res_str('tara_dhasa_option3_str', 'Method 2')],
                               'default': _next_default(0), 'value_offset': 1})
            elif dhasa_name == 'rasi_bhukthi_vimsottari':
                specs.append({'kind': 'checkbox', 'kwarg': 'use_rasi_bhukthi_variation',
                               'label': res_str('rbv_dhasa_option_str', 'Use Rasi Bhukthi Variation'),
                               'default': bool(_next_default(False)), 'disabled': True})
            # Fields that can be combined.
            if dhasa_name in tithi_dhasas:
                specs.append({'kind': 'combo', 'kwarg': 'tithi_index',
                               'label': res_str('tithi_index_option_str', 'Tithi Index'),
                               'items': [res_str(t, t.replace('_str', '').replace('_', ' ').title()) for t in _tithi_list],
                               'default': _next_default(0), 'value_offset': 1})
            if dhasa_name in tribhagi_dhasas:
                specs.append({'kind': 'checkbox', 'kwarg': 'use_tribhagi_variation',
                               'label': res_str('tribhagi_option_str', 'Use Tribhagi Variation'),
                               'default': bool(_next_default(False))})
            if dhasa_name in seed_list_dhasas.keys():
                specs.append({'kind': 'combo', 'kwarg': 'seed_star',
                               'label': res_str('seed_star_option_str', 'Seed Star'),
                               'items': [utils.NAKSHATRA_LIST[n] for n in range(27)],
                               'default': _next_default(0), 'value_offset': 1})
            if dhasa_name in dhasa_start_planet_dhasas:
                _ind_dict = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
                             9: 'L', 10: 'M', 11: 'G', 12: 'T', 13: 'B', 14: 'I', 15: 'P'}
                _items = [utils.PLANET_NAMES[p] + '-' + res_str('sphuta_str', 'Sphuta') for p in range(9)] + [
                    res_str('ascendant_str', 'Ascendant') + '-' + res_str('sphuta_str', 'Sphuta'),
                    res_str('maandi_str', 'Maandi') + '-' + res_str('sphuta_str', 'Sphuta'),
                    res_str('gulika_str', 'Gulika') + '-' + res_str('sphuta_str', 'Sphuta'),
                    res_str('tri_sphuta_str', 'Tri-Sphuta') + '-' + res_str('sphuta_str', 'Sphuta'),
                    res_str('bhrigu_bindhu_lagna_str', 'Bhrigu Bindhu Lagna'),
                    res_str('indu_lagna_str', 'Indu Lagna'),
                    res_str('pranapada_lagna_str', 'Pranapada Lagna'),
                ]
                specs.append({'kind': 'combo', 'kwarg': 'dhasa_starting_planet',
                               'label': res_str('dhasa_start_option_str', 'Dhasa Starting Planet'),
                               'items': _items, 'default': _next_default(0), 'index_map': _ind_dict})
            if dhasa_name in start_from_moon_dhasas:
                _moon_ind_dict = {0: 1, 1: 4, 2: 5, 3: 8}
                specs.append({'kind': 'combo', 'kwarg': 'star_position_from_moon',
                               'label': res_str('moon_start_option1_str', 'Star Position From Moon'),
                               'items': [res_str('moon_start_option2_str', 'Option 1'), res_str('moon_start_option3_str', 'Option 2'),
                                         res_str('moon_start_option4_str', 'Option 3'), res_str('moon_start_option5_str', 'Option 4')],
                               'default': _next_default(0), 'index_map': _moon_ind_dict})
            if dhasa_name in antardhasa_option_list:
                specs.append({'kind': 'combo', 'kwarg': 'antardhasa_option',
                               'label': res_str('ant_dhasa_option_str', 'Antardhasa Option'),
                               'items': [res_str(f'ant_dhasa_option{i}_str', f'Option {i}') for i in range(1, 7)],
                               'default': _next_default(0), 'value_offset': 1})
            if dhasa_name in varga_dhasas:
                varga_default = _next_default(0)
                method_default = defaults[counter] if counter < len(defaults) else -1
                if method_default != -1:
                    counter += 1  # the method default is consumed only when present
                specs.append({'kind': 'varga', 'default': varga_default, 'method_default': method_default})
            return specs
        def _initial_value_for_spec(spec, stored):
            """Returns the initial widget value to show for `spec` when (re)opening the Dhasa Options
            dialog: the value this browser previously chose for the CURRENT dhasa (from `stored`, the
            persisted entry for its (type, name) key - see _get_dhasa_options()), if present, otherwise
            spec['default'] (from const.dhasa_default_options). This is the inverse of the mapping
            _on_accept() below applies when turning widget values into keyword arguments.
            Args:
                spec: field dict from _dhasa_option_field_specs().
                stored: _get_dhasa_options(key) for the dhasa `spec` belongs to.
            Returns:
                For 'combo'/'varga': a widget-select index. For 'checkbox': a bool.
            """
            kind = spec['kind']
            if kind == 'checkbox':
                if spec['kwarg'] in stored:
                    return bool(stored[spec['kwarg']])
                return spec['default']
            if kind == 'combo':
                if spec['kwarg'] not in stored:
                    return spec['default']
                stored_val = stored[spec['kwarg']]
                if spec.get('special') == 'aayur_type':
                    return 3 if stored_val is None else stored_val
                if 'index_map' in spec:
                    inverse = {v: k for k, v in spec['index_map'].items()}
                    return inverse.get(stored_val, spec['default'])
                return stored_val - spec.get('value_offset', 0)
            if kind == 'varga':
                dcf = stored.get('divisional_chart_factor')
                if dcf is None:
                    return spec['default']
                try:
                    return _division_chart_factors.index(dcf)
                except ValueError:
                    return spec['default']
            return spec['default']
        def _initial_method_idx_for_spec(spec, stored):
            """Returns the initial value of a 'varga' field's own method combo: this dhasa's
            previously-chosen chart_method (from `stored`) if present, otherwise spec['method_default']
            (None if that dhasa/varga combination has no configurable method - see
            _rebuild_method_combo()'s own varga_factor==1 / single-method short-circuit).
            """
            if 'chart_method' in stored:
                return stored['chart_method'] - 1
            return (spec['method_default'] - 1) if spec['method_default'] != -1 else None
        def _refresh_dhasa_options_button():
            """Enables the Dhasa Options button, with a tooltip, when the selected dhasa has option
            fields; otherwise disables it. Does NOT touch any dhasa's persisted options - each dhasa's
            own stored options persist across switching to a different dhasa and back, AND across a
            page reconnect (see the module docstring).
            """
            dhasa_name = _selected_dhasa_name()
            if _dhasa_option_field_specs(dhasa_name):
                dhasa_options_button.enable()
                dhasa_options_button.classes(remove='text-gray-400')
                dhasa_options_tooltip.set_text('Configure extra options (e.g. seed star, tribhagi variation) for this dhasa.')
            else:
                dhasa_options_button.disable()
                dhasa_options_button.classes(add='text-gray-400')
                dhasa_options_tooltip.set_text('This dhasa has no extra options to configure.')
        def _open_dhasa_options_dialog():
            """Opens the Dhasa Options dialog for the selected dhasa, pre-filled with whatever this
            browser last chose for it (_get_dhasa_options()), or the dhasa's defaults if nothing was
            chosen yet. Accept persists the chosen keyword arguments under this dhasa's own (type, name)
            key via _set_dhasa_options() - so a later switch to a different dhasa and back, OR a page
            reconnect (e.g. around printing), still finds them - and recomputes the tree.
            """
            dhasa_name = _selected_dhasa_name()
            key = _selected_dhasa_key()
            stored = _get_dhasa_options(key)
            specs = _dhasa_option_field_specs(dhasa_name)
            if not specs:
                safe_notify('This dhasa has no extra options to configure.', type='warning')
                return
            widget_refs = []
            with ui.dialog() as dialog, ui.card().classes('gap-3'):
                ui.label(
                    res_str(dhasa_name + '_str', dhasa_name.replace('_', ' ').title()) + ' ' +
                    res_str('dhasa_str', 'Dhasa') + ' ' + res_str('options_str', 'Options')
                ).classes('text-lg font-bold text-green-700')
                for spec in specs:
                    if spec['kind'] == 'combo':
                        el = ui.select(options={i: lbl for i, lbl in enumerate(spec['items'])},
                                        value=_initial_value_for_spec(spec, stored), label=spec['label']) \
                            .props('outlined dense').classes('w-72')
                        widget_refs.append((spec, el))
                    elif spec['kind'] == 'checkbox':
                        el = ui.checkbox(spec['label'], value=_initial_value_for_spec(spec, stored))
                        if spec.get('disabled'):
                            el.disable()
                        widget_refs.append((spec, el))
                    elif spec['kind'] == 'varga':
                        varga_combo = ui.select(options={i: _varga_label(i) for i in range(len(_division_chart_factors))},
                                                 value=_initial_value_for_spec(spec, stored), label=res_str('varga_option_str', 'Varga Chart')) \
                            .props('outlined dense').classes('w-72')
                        method_container = ui.column().classes('gap-1 w-72')
                        method_combo_ref = {'el': None}
                        def _rebuild_method_combo(default_method_idx=None, _varga_combo=varga_combo,
                                                   _method_container=method_container, _ref=method_combo_ref):
                            _method_container.clear()
                            varga_factor = _division_chart_factors[_varga_combo.value]
                            if varga_factor == 1:
                                _ref['el'] = None
                                return
                            # get_varga_option_dict() follows the visitor's d{n}_chart_method_default settings (const.varga_option_dict does not).
                            method_count, default_method, _b, _e = utils.get_varga_option_dict()[varga_factor]
                            method_count = method_count or 1
                            default_method = default_method or 1
                            items = [res_str(f'd{varga_factor}_option{m + 1}_str', f'Method {m + 1}') for m in range(method_count)]
                            idx = default_method_idx if default_method_idx is not None else (default_method - 1)
                            with _method_container:
                                el = ui.select(options={i: lbl for i, lbl in enumerate(items)}, value=idx,
                                                label=res_str('choose_varga_chart_method_str', 'Choose Varga Chart Method')) \
                                    .props('outlined dense').classes('w-72')
                            _ref['el'] = el
                        _rebuild_method_combo(_initial_method_idx_for_spec(spec, stored))
                        varga_combo.on_value_change(lambda e, _r=_rebuild_method_combo: _r())
                        widget_refs.append((spec, (varga_combo, method_combo_ref)))
                async def _on_accept():
                    kwargs = {}
                    for spec, el in widget_refs:
                        kind = spec['kind']
                        if kind == 'combo':
                            ind = el.value if isinstance(el.value, int) else 0
                            if spec.get('special') == 'aayur_type':
                                val = ind if ind in (0, 1, 2) else None
                            elif 'index_map' in spec:
                                val = spec['index_map'].get(ind, ind)
                            else:
                                val = ind + spec.get('value_offset', 0)
                            kwargs[spec['kwarg']] = val
                        elif kind == 'checkbox':
                            kwargs[spec['kwarg']] = bool(el.value)
                        elif kind == 'varga':
                            varga_combo, method_combo_ref = el
                            ind = varga_combo.value if isinstance(varga_combo.value, int) else 0
                            kwargs['divisional_chart_factor'] = _division_chart_factors[ind]
                            if method_combo_ref['el'] is not None:
                                m_ind = method_combo_ref['el'].value if isinstance(method_combo_ref['el'].value, int) else 0
                                kwargs['chart_method'] = m_ind + 1
                    # Persisted under this dhasa's OWN key, in app.storage.user - does not disturb any
                    # other dhasa's stored options, and survives switching away from this dhasa and
                    # back, AND a page reconnect (see the module docstring).
                    _set_dhasa_options(key, kwargs)
                    dialog.close()
                    safe_notify('Dhasa options applied - recomputing.', type='positive')
                    await compute_dhasa()
                with ui.row().classes('gap-2 justify-end w-full'):
                    ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                    ui.button(res_str('accept_str', 'Accept'), on_click=_on_accept).classes('bg-green-600 text-white')
            dialog.open()
        def _parse_birth_inputs():
            """Reads the birth details from the control bar.
            Returns:
                (jd_at_dob, place): Julian day of the birth and its drik.Place.
            Raises:
                An exception if an input is invalid.
            """
            dob_val = w['dob_input'].value.strip()
            tob_val = w['tob_input'].value.strip()
            place_val = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat_val = float(w['lat_input'].value.strip())
            lon_val = float(w['lon_input'].value.strip())
            tz_val = float(w['tz_input'].value.strip())
            year, month, day = dob_val.split(",")
            dob = drik.Date(int(year), int(month), int(day))
            tob = _parse_tob(tob_val)
            place = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
            jd_at_dob = utils.julian_day_number(dob, tob)
            return jd_at_dob, place
        def _open_running_dhasa_dialog():
            """Opens the Running Dhasa dialog for the selected dhasa.
            Inputs: current date ('Y,M,D'), current time ('H:M:S') and the year-duration type. Compute shows a
            table (level, lord, starts at, ends at) from get_running_dhasa_for_given_date(), using this
            dhasa's own persisted options (_get_dhasa_options()). const.dhasa_year_duration_default is set
            for the calculation only and restored afterwards, inside the lock.
            """
            dhasa_name = _selected_dhasa_name()
            dhasa_type_index = dhasa_type_select.value if isinstance(dhasa_type_select.value, int) else 0
            key = _selected_dhasa_key()
            with calc_lock():  # read inside calc_lock() so the visitor's year-duration setting applies
                original_duration = int(const.dhasa_year_duration_default)
            now = datetime.now()
            with ui.dialog() as dialog, ui.card().classes('gap-3'):
                ui.label(
                    res_str('show_running_dhasa_str', 'Show Running Dhasa') + ' (' +
                    res_str(dhasa_name + '_str', dhasa_name.replace('_', ' ').title()) + ')'
                ).classes('text-lg font-bold text-green-700')
                with ui.row().classes('items-center gap-2'):
                    date_input = ui.input(
                        label=res_str('current_date_str', 'Current Date'),
                        value=f"{now.year},{now.month},{now.day}",
                    ).props('outlined dense').classes('w-40')
                    time_input = ui.input(
                        label=res_str('time_of_birth_str', 'Time'),
                        value=f"{now.hour}:{now.minute}:{now.second}",
                    ).props('outlined dense').classes('w-32')
                duration_options = {i: res_str(k, k.replace('_str', '').replace('_', ' ').title()) for i, k in enumerate(_YEAR_DURATION_KEYS)}
                duration_select = ui.select(
                    options=duration_options, value=original_duration - 1,
                    label=res_str('year_duration_type_str', 'Year Duration Type'),
                ).props('outlined dense').classes('w-64')
                results_html = ui.html('')
                def _on_compute():
                    try:
                        y, m, d = map(int, date_input.value.strip().split(','))
                        hh, mm, ss = map(int, time_input.value.strip().split(':'))
                    except Exception:
                        results_html.set_content('<b style="color:red">Invalid date/time format (expected YYYY,MM,DD and HH:MM:SS)</b>')
                        return
                    try:
                        current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
                        chosen_duration = (duration_select.value if isinstance(duration_select.value, int) else 0) + 1
                        jd_at_dob, place = _parse_birth_inputs()
                        with calc_lock():
                            # The year-duration constant is set, used and restored inside the lock, so no other visitor sees the temporary value.
                            previous_duration = const.dhasa_year_duration_default
                            try:
                                const.dhasa_year_duration_default = chosen_duration
                                module, defaults = utils._get_import_dhasa_module(dhasa_name)
                                func = getattr(module, "get_running_dhasa_for_given_date", None)
                                if not callable(func):
                                    raise AttributeError(f"{module.__name__}.get_running_dhasa_for_given_date not found/callable")
                                opts = {**defaults, **_get_dhasa_options(key)}
                                rd = func(current_jd, jd_at_dob, place, **opts)
                            finally:
                                const.dhasa_year_duration_default = previous_duration
                    except AttributeError as e:
                        print(f"[dhasa_page] _open_running_dhasa_dialog('{dhasa_name}') - not yet supported: {e}")
                        results_html.set_content(f'<b>{dhasa_name} {res_str("dhasa_str", "dhasa")} is not supported.</b>')
                        return
                    except Exception as e:
                        results_html.set_content(f'<b style="color:red">Error: {e}</b>')
                        return
                    if rd is None:
                        results_html.set_content(f'<b>{dhasa_name} {res_str("dhasa_str", "dhasa")} is not supported.</b>')
                        return
                    dhasa_type_label = (res_str('graha_str', 'Graha') if dhasa_type_index == 0 else
                                        (res_str('raasi_str', 'Raasi') if dhasa_type_index == 1 else res_str('annual_str', 'Annual')))
                    html = (f"<b>{res_str(dhasa_name + '_str', dhasa_name.replace('_', ' ').title())} {dhasa_type_label} "
                            f"{res_str('dhasa_str', 'Dhasa')}:</b><br>")
                    # Explicit inline CSS: the page's CSS reset removes default table borders and padding.
                    _th_style = 'border:1px solid #5c3a21; padding:6px 10px; background:#f0fdf4; text-align:left; white-space:nowrap;'
                    _td_style = 'border:1px solid #d1d5db; padding:6px 10px; white-space:nowrap;'
                    html += "<table style='border-collapse:collapse;'>"
                    html += (f"<tr><th style='{_th_style}'>{res_str('dhasa_str', 'Dhasa')}</th>"
                             f"<th style='{_th_style}'>{res_str('lord_str', 'Lord')}</th>"
                             f"<th style='{_th_style}'>{res_str('starts_at_str', 'Starts At')}</th>"
                             f"<th style='{_th_style}'>{res_str('ends_at_str', 'Ends At')}</th></tr>")
                    for dli, row in enumerate(rd):
                        lord = row[0][dli]
                        start = row[1]
                        end = row[2]
                        lord_str = utils.get_dhasa_lord_resource_name(dhasa_type=dhasa_type_index, dhasa_name=dhasa_name, lord=lord)
                        s = f"{start[0]:04d}-{start[1]:02d}-{start[2]:02d} {utils.to_dms(start[3])}"
                        e = f"{end[0]:04d}-{end[1]:02d}-{end[2]:02d} {utils.to_dms(end[3])}"
                        level_label = res_str(_DLI_LEVEL_KEYS[dli], _DLI_LEVEL_KEYS[dli].replace('_str', '').title())
                        html += (f"<tr><td style='{_td_style}'>{level_label}</td>"
                                 f"<td style='{_td_style}'>{lord_str}</td>"
                                 f"<td style='{_td_style}'>{s}</td>"
                                 f"<td style='{_td_style}'>{e}</td></tr>")
                    html += "</table>"
                    results_html.set_content(html)
                with ui.row().classes('gap-2 justify-end w-full'):
                    ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                    ui.button(res_str('compute_str', 'Compute'), on_click=_on_compute).classes('bg-green-600 text-white')
            dialog.open()
        # _open_multi_dhasa_dialog() and _build_dhasa_report() (the former "Print Multiple Dhasas"
        # button's own dialog + its report builder) are REMOVED entirely - see the button-row
        # removal note above for why. The SAME "Selected dhasa only" / "By category" choice is now
        # offered by this page's own print_registry.py sub_option_ui (see _dhasa_sub_option_ui() /
        # _build_print_section() below), inside the ONE central dialog instead of a separate one
        # here. "Selected dhasa only" there reads the PERSISTED selection (_DHASA_SELECTION_KEY /
        # _DHASA_OPTIONS_KEY, both in app.storage.user) rather than this page's own live widgets -
        # those persisted values ARE reachable headlessly (unlike a live widget), so this still
        # reflects whatever this browser last had selected/customized on this page, exactly as
        # before.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute_dhasa(),
                                on_calculate=lambda: compute_dhasa())
        busy = DelayedBusyIndicator(buttons=[w.get('calculate_button')], stop_label=res_str('stop_str', 'Stop'))
        _dhasa_option_str = res_str('dhasa_str','Dasha')+' '+res_str('options_str','Options')
        with w['row2']:
            # value= below uses the PERSISTED selection computed earlier (_initial_dhasa_type_index/
            # _initial_dhasa_name_index/_initial_varga_index), NOT a hardcoded 0 - see the module
            # docstring for the reconnect bug this replaces.
            dhasa_type_select = ui.select(options=_dhasa_type_options, value=_initial_dhasa_type_index, label='Dhasa Type') \
                .props('outlined dense').classes('w-40')
            dhasa_name_options = {i: res_str(n + '_str', n.replace('_', ' ').title()) for i, n in enumerate(_initial_dhasa_names)}
            dhasa_name_select = ui.select(options=dhasa_name_options, value=_initial_dhasa_name_index, label='Dhasa') \
                .props('outlined dense').classes('w-56')
            varga_select = ui.select(options=_varga_options, value=_initial_varga_index, label='Varga').props('outlined dense').classes('w-56')
            varga_select.set_visibility(_initial_dhasa_type_index == 2)
            dhasa_options_button = ui.button(_dhasa_option_str, on_click=lambda: _open_dhasa_options_dialog()).props('outlined dense')
            dhasa_options_tooltip = None
            with dhasa_options_button:
                dhasa_options_tooltip = ui.tooltip('')
            ui.button(res_str('show_running_dhasa_str', 'Running Dhasa'), on_click=lambda: _open_running_dhasa_dialog()).props('outlined dense')
        # Marked 'no-print' - see the module docstring's "IMPORTANT (print)" note for the real bug
        # this was found to cause: left un-marked, this separator was still visible during print,
        # occupying a sliver of page 1 above the print table - and since the print table's own
        # header is explicitly atomic (kept whole + attached to the table start), it had to move
        # ENTIRELY to page 2 when it did not fit whatever page-1 space the separator left behind,
        # leaving page 1 blank. '.dhasa-report-item's own `page-break-before: avoid` rule could not
        # prevent this, since that rule only suppresses an OPTIONAL break - it cannot stop a break
        # that is physically REQUIRED because the content genuinely does not fit.
        ui.separator().classes('my-1 no-print')
        # Interactive drill-down tree: icons, breadcrumbs and click handlers do not belong in a
        # printout, so this is marked 'no-print' - see dhasa_print_container below for the plain,
        # Maha-Dasa-only table that prints instead (components.py's '.print-only' utility).
        tree_container = ui.column().classes('w-full gap-0 no-print')
        # 'print-only' makes this show up during a NORMAL print_button() print (the single, currently
        # selected dhasa). It is ALSO marked 'single-chart-print-block' so that, during the multi-dhasa
        # report below (which sets body.printing-all), the existing rule that hides
        # '.single-chart-print-block' under that class suppresses this single-dhasa table too -
        # otherwise it would appear ALONGSIDE the multi-dhasa report in the same print job, since
        # '.print-only's own CSS rule is unconditional and does not know about 'printing-all' by itself.
        # ALSO marked 'dhasa-report-item' (the SAME class "Print Multiple Dhasas" uses) - a single
        # dhasa's own Maha Dasa table can be just as tall as any one dhasa in that report, and this is
        # what lets its header (below, marked 'dhasa-report-header') stay attached to the start of its
        # table instead of being stranded alone on a page with the table starting fresh on the NEXT
        # page - this was confirmed from an actual printed PDF before this fix.
        dhasa_print_container = ui.column().classes('w-full gap-0 print-only single-chart-print-block dhasa-report-item')
        # Hidden multi-dhasa report, built only when "Print Multiple Dhasas" is used - see
        # components.py's _PRINT_CSS: '.all-charts-report' stays invisible both on screen and during
        # a normal print_button() print; shown only while body carries 'printing-all' (see above).
        all_dhasa_report_container = ui.column().classes('all-charts-report w-full gap-0')
        def _refresh_dhasa_name_options():
            """Fills the Dhasa selector for the chosen Dhasa Type, RESETTING the Dhasa to the first
            name in the new type's list (and persisting that reset). Call this ONLY in response to
            the Dhasa Type selector's own change event (_on_dhasa_type_changed()) - resetting the
            dhasa name IS the correct behavior there, since the old name belongs to the old type.
            Do NOT call this when simply re-displaying a previously persisted selection on page
            build - that path builds dhasa_name_select directly with the persisted index instead
            (see the `with w['row2']:` block above), so a page reconnect does not look like this
            same "type changed" reset.
            Also shows the Varga selector only for Annual dhasas and hides the Dhasa Options button
            for them.
            """
            idx = dhasa_type_select.value if isinstance(dhasa_type_select.value, int) else 0
            names = _names_for_type(idx)
            dhasa_name_select.set_options({i: res_str(n + '_str', n.replace('_', ' ').title()) for i, n in enumerate(names)})
            dhasa_name_select.set_value(0)
            varga_select.set_visibility(idx == 2)
            dhasa_options_button.set_visibility(idx != 2)
            _refresh_dhasa_options_button()
        async def _on_dhasa_type_changed(e):
            _refresh_dhasa_name_options()
            # Persist the new type AND the dhasa name _refresh_dhasa_name_options() just reset to
            # (the first name of the new type's list) - see that function's own docstring for why
            # this reset (unlike a reconnect) is the intended behavior here.
            new_type_idx = dhasa_type_select.value if isinstance(dhasa_type_select.value, int) else 0
            new_names = _names_for_type(new_type_idx)
            _set_selection(dhasa_type_index=new_type_idx, dhasa_name=(new_names[0] if new_names else None))
            await compute_dhasa()
        async def _on_dhasa_name_changed(e):
            _refresh_dhasa_options_button()
            _set_selection(dhasa_name=_selected_dhasa_name())
            await compute_dhasa()
        dhasa_type_select.on_value_change(_on_dhasa_type_changed)
        dhasa_name_select.on_value_change(_on_dhasa_name_changed)
        async def _on_varga_changed(e):
            idx = varga_select.value if isinstance(varga_select.value, int) else 0
            _set_selection(varga_index=idx)
            await compute_dhasa()
        varga_select.on_value_change(_on_varga_changed)
        def _ensure_children_loaded(node):
            """Computes node['children'] on first use. Afterwards it is always a list; a placeholder entry
            ('leaf_text') stands for an unsupported dhasa, an error or no sub-periods.
            Args:
                node: tree row dict from _make_node().
            """
            if node.get('children') is not None:
                return
            try:
                with calc_lock():
                    rows = dhasa_selector.get_dhasa_children(
                        node['dhasa_name'], node['lords'], node['start'],
                        parent_end=node['end'], **node['kwargs']
                    )
            except AttributeError as e:
                print(f"[dhasa_page] get_dhasa_children('{node['dhasa_name']}') - not yet supported: {e}")
                node['children'] = [{'leaf_text': _UNAVAILABLE_MESSAGE_TEMPLATE.format(dhasa_label=node['dhasa_name']), 'level': node['level'] + 1}]
                return
            except Exception as e:
                print(f"[dhasa_page] get_dhasa_children('{node['dhasa_name']}') error: {e}")
                node['children'] = [{'leaf_text': f"(error: {e})", 'level': node['level'] + 1}]
                return
            if not rows:
                # No children came back for a row that can be expanded: show a placeholder row.
                node['children'] = [{'leaf_text': _NO_FURTHER_BREAKDOWN_MESSAGE, 'level': node['level'] + 1}]
            else:
                node['children'] = [
                    _make_node(node['dhasa_name'], node['dhasa_type_index'], lords, label, start, end,
                               node['level'] + 1, node['kwargs'])
                    for (lords, label, start, end) in rows
                ]
        # Header + every row share ONE CSS Grid container (built in _render_tree()) instead of each
        # row being its own independent flex container - this is what lets the Dhasa label column's
        # width be computed from the WIDEST label currently shown ACROSS ALL ROWS (max-content), so a
        # long label (e.g. Sudarsana Chakra's multi-planet "Sagittarius/Pisces/Libra" style labels)
        # is shown on one line instead of wrapping inside a fixed-width box - a real layout problem
        # the user reported from an actual screenshot. Columns 2-4 (level/start/end) are short,
        # fixed-format text and simply use max-content too (effectively their natural width).
        _TREE_GRID_STYLE = (
            'display:grid; grid-template-columns: minmax(96px, max-content) max-content max-content max-content; '
            'column-gap:16px; row-gap:2px; align-items:center;'
        )
        def _render_row(node, indent_level, *, highlighted=False, expanded=False, clickable_handler=None):
            """Draws one row, either a breadcrumb row or a child row, as cells of the shared CSS Grid
            built by _render_tree() (see _TREE_GRID_STYLE above) - NOT as its own independent flex
            row (an earlier version of this function did that, which is why the Dhasa label column
            used to wrap long labels inside a fixed width instead of fitting them on one line - see
            _TREE_GRID_STYLE's own comment).
            The logical "row" is a `display:contents` wrapper: it generates no box of its own (its 4
            children become direct grid items instead), so indentation/highlight background/cursor
            must be applied to each of those 4 cells individually rather than to this wrapper -
            children's click events still bubble through it completely normally, so the click
            handler can still be attached here exactly as before. One visual trade-off worth knowing:
            a highlighted row now shows as 4 separate light-blue cells with small gaps between them
            (from column-gap) rather than one seamless rounded bar - simpler to implement correctly
            than a seamless highlight across a CSS Grid's row, and not the focus of the request this
            fixes; revisit if that gap looks wrong in practice.
            Args:
                node: row dict from _make_node(), or a placeholder dict with 'leaf_text'.
                indent_level: indentation in steps of 24 px, applied as padding-left on the label
                    cell ONLY - the level/start/end columns stay aligned across every row regardless
                    of that row's own nesting depth (unlike the old margin-left-on-the-whole-row
                    approach, which moved every column together).
                highlighted: blue background (the deepest open row) - applied to all 4 cells.
                expanded: show the 'v' icon instead of '>' (every row of the open chain).
                clickable_handler: click callback, or None.
            """
            indent = indent_level * 24
            cell_bg = 'bg-blue-50' if highlighted else ''
            cell_interactive = 'cursor-pointer hover:bg-gray-50' if clickable_handler else ''
            cell_extra = f'{cell_bg} {cell_interactive}'.strip()
            if 'leaf_text' in node:
                with ui.element('div').classes(f'text-xs text-gray-500 py-0.5 {cell_extra}'.strip()) \
                        .style(f'grid-column: 1 / -1; padding-left:{indent}px;'):
                    ui.label(node['leaf_text'])
                return
            with ui.element('div').style('display:contents') as row:
                with ui.element('div').classes(f'flex items-center gap-2 py-0.5 {cell_extra}'.strip()) \
                        .style(f'padding-left:{indent}px; white-space:nowrap;'):
                    if node['can_expand']:
                        # Icon: 'v' for every row of the open chain, '>' for a row that is not open.
                        icon_name = 'expand_more' if expanded else 'chevron_right'
                        ui.icon(icon_name).classes('text-gray-500')
                    else:
                        ui.element('div').classes('w-6 shrink-0')
                    ui.label(node['label']).classes('font-bold text-brown-800')
                ui.label(_level_name(node['level'])).classes(f'text-gray-500 text-xs py-0.5 {cell_extra}'.strip())
                ui.label(_date_text(node['start'])).classes(f'text-blue-700 text-xs py-0.5 whitespace-nowrap {cell_extra}'.strip())
                ui.label(_date_text(node['end'])).classes(f'text-blue-700 text-xs py-0.5 whitespace-nowrap {cell_extra}'.strip())
                if clickable_handler:
                    row.on('click', clickable_handler)
        def _render_tree():
            """Redraws the whole tree: header, breadcrumb rows of the open chain and the list below
            them, all inside ONE shared CSS Grid (_TREE_GRID_STYLE) - see _render_row()'s own
            docstring for why this (rather than each row being its own flex container) is what makes
            the Dhasa label column fit its contents instead of wrapping.
            """
            # Header, breadcrumb rows and child list are all built inside tree_container, so clear() removes the previous drawing.
            tree_container.clear()
            with tree_container:
                if tree_state["root_error_message"]:
                    ui.label(tree_state["root_error_message"]).classes('text-red-600')
                    return
                if not tree_state["roots"]:
                    ui.label('Click "Show Dhasa" to compute the dhasa/bhukthi tree.').classes('text-gray-500')
                    return
                with ui.element('div').classes('w-full').style(_TREE_GRID_STYLE):
                    ui.label(res_str('dhasa_str', 'Dhasa')).classes('font-bold text-green-700 py-1')
                    ui.label('').classes('py-1')
                    ui.label(res_str('starts_at_str', 'Starts At')).classes('font-bold text-green-700 py-1')
                    ui.label(res_str('ends_at_str', 'Ends At')).classes('font-bold text-green-700 py-1')
                    # One grid item spanning all 4 columns, standing in for the header's old
                    # border-b-2 (a single continuous rule under the whole header row).
                    ui.element('div').style('grid-column: 1 / -1; border-bottom: 2px solid #15803d; margin-bottom: 2px;')
                    path = tree_state["active_path"]
                    # 1) Breadcrumb rows of the open chain: every row shows the 'v' icon, only the deepest is highlighted.
                    #    Clicking the deepest row collapses it; clicking an earlier row jumps back to that level.
                    for i, node in enumerate(path):
                        is_last = (i == len(path) - 1)
                        if is_last:
                            handler = (lambda n=node: _on_deepest_clicked(n))
                        else:
                            handler = (lambda idx=i: _on_breadcrumb_ancestor_clicked(idx))
                        _render_row(node, i, highlighted=is_last, expanded=True, clickable_handler=handler)
                    # 2) List below: the root rows when nothing is open, otherwise the children of the deepest open row (shown with '>').
                    current_list = tree_state["roots"] if not path else (path[-1].get('children') or [])
                    flat_indent = len(path)
                    for child in current_list:
                        if 'leaf_text' in child:
                            _render_row(child, flat_indent)
                        elif child['can_expand']:
                            _render_row(child, flat_indent, highlighted=False, expanded=False, clickable_handler=lambda n=child: _on_child_clicked(n))
                        else:
                            _render_row(child, flat_indent, highlighted=False, expanded=False, clickable_handler=None)
        def _render_print_table():
            """Draws the print-only Maha Dasa level table (dhasa_print_container) from tree_state. Per the
            user's explicit scope decision, this mirrors ONLY the root (Maha Dasa) rows as a clean table -
            no drill-down icons/breadcrumbs/click handlers, and no deeper levels - since printing the full,
            potentially 6-level-deep interactive tree was judged unnecessary and keeping the printout to
            just this level is what makes it practical for more than one dhasa to eventually share a page.
            The header (place/date + title) is marked 'dhasa-report-header' (same class the multi-dhasa
            report uses) so it stays attached to the start of the table below it, instead of being
            stranded alone on a page with the table starting fresh on the next one.
            tree_state["roots"] holds NODE DICTS (from _make_node()), NOT the raw (lords, label,
            start, end) tuples _root_rows_table_html() expects - they are converted below.
            """
            dhasa_print_container.clear()
            with dhasa_print_container:
                if tree_state.get("root_error_message"):
                    ui.label(tree_state["root_error_message"]).classes('text-red-600')
                    return
                roots = tree_state.get("roots")
                if not roots:
                    return
                dhasa_name = tree_state.get("print_dhasa_name", "")
                dhasa_type_index = tree_state.get("print_dhasa_type_index", 0)
                dhasa_type_label = (res_str('graha_str', 'Graha') if dhasa_type_index == 0 else
                                    (res_str('raasi_str', 'Raasi') if dhasa_type_index == 1 else res_str('annual_str', 'Annual')))
                dhasa_label = res_str(dhasa_name + '_str', dhasa_name.replace('_', ' ').title()) if dhasa_name else ''
                header_html = (
                    f"<div style='margin-bottom:4px;'><b>{tree_state.get('print_place', '')}</b> "
                    f"&mdash; {tree_state.get('print_dob', '')} {tree_state.get('print_tob', '')}</div>"
                    f"<div style='margin-bottom:6px;'><b>{dhasa_label} {dhasa_type_label} "
                    f"{res_str('dhasa_str', 'Dhasa')} ({res_str('maha_str', 'Maha')} "
                    f"{res_str('dhasa_str', 'Dhasa')})</b></div>"
                )
                ui.html(header_html).classes('dhasa-report-header')
                root_row_tuples = [(node['lords'], node['label'], node['start'], node['end']) for node in roots]
                ui.html(_root_rows_table_html(root_row_tuples))
        @ignore_disconnected_client
        def _on_child_clicked(node):
            """Opens a child row: loads its children if needed, adds it to the open chain and redraws."""
            _ensure_children_loaded(node)
            tree_state["active_path"].append(node)
            _render_tree()
        @ignore_disconnected_client
        def _on_deepest_clicked(node):
            """Collapses the deepest open row (goes up one level) and redraws."""
            if tree_state["active_path"]:
                tree_state["active_path"].pop()
            _render_tree()
        @ignore_disconnected_client
        def _on_breadcrumb_ancestor_clicked(index):
            """Jumps back to the breadcrumb row at `index` (closing the rows below it) and redraws."""
            tree_state["active_path"] = tree_state["active_path"][:index + 1]
            _render_tree()
        @ignore_disconnected_client
        async def compute_dhasa():
            """Reads the control bar and the dhasa selectors, computes the root rows in a worker thread
            (showing a "please wait" message via DelayedBusyIndicator if it takes more than a moment) and
            draws the tree (and the print-only Maha Dasa table - see _render_print_table()). This dhasa's
            OWN persisted options (_get_dhasa_options()) are included.
            """
            if busy.is_busy:
                safe_notify('Already computing. Please wait.', type='warning')
                return
            dhasa_name = None
            try:
                dob_val = w['dob_input'].value.strip()
                tob_val = w['tob_input'].value.strip()
                place_val = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
                lat_val = float(w['lat_input'].value.strip())
                lon_val = float(w['lon_input'].value.strip())
                tz_val = float(w['tz_input'].value.strip())
                year, month, day = dob_val.split(",")
                dob = drik.Date(int(year), int(month), int(day))
                tob = _parse_tob(tob_val)
                dhasa_type_index = dhasa_type_select.value if isinstance(dhasa_type_select.value, int) else 0
                names = _names_for_type(dhasa_type_index)
                name_idx = dhasa_name_select.value if isinstance(dhasa_name_select.value, int) else 0
                if not (0 <= name_idx < len(names)):
                    name_idx = 0
                dhasa_name = names[name_idx]
                if dhasa_type_index == 2:
                    varga_idx = varga_select.value if isinstance(varga_select.value, int) else 0
                    dcf = _division_chart_factors[varga_idx]
                else:
                    dcf = 1
                # This dhasa's own persisted options (_get_dhasa_options()); its divisional_chart_factor,
                # if any, overrides the Varga selector.
                option_kwargs = _get_dhasa_options((dhasa_type_index, dhasa_name))
                dcf = option_kwargs.pop('divisional_chart_factor', dcf)
                place = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
                # Context for the print-only table (see _render_print_table()); stored here (rather than
                # only on success) so a later computation failure still has something sensible to show.
                tree_state["print_dob"] = dob_val
                tree_state["print_tob"] = tob_val
                tree_state["print_place"] = place_val
                tree_state["print_dhasa_name"] = dhasa_name
                tree_state["print_dhasa_type_index"] = dhasa_type_index
            except Exception as e:
                tree_state["roots"] = None
                tree_state["active_path"] = []
                tree_state["root_error_message"] = f"(error computing root dhasa: {e})"
                _render_tree()
                _render_print_table()
                safe_notify(f'Error computing dhasa: {str(e)}', type='negative')
                return
            try:
                md_rows = await busy.run(_dhasa_root_locked, dhasa_type_index, dhasa_name, dob, tob, place, dcf,
                                         option_kwargs, wait_text=res_str('computing_str', 'Computing... please wait.'))
            except AttributeError as e:
                label_for_message = dhasa_name if dhasa_name is not None else dhasa_name_select.props.get('label') or 'This'
                print(f"[dhasa_page] compute_dhasa('{label_for_message}') - not yet supported: {e}")
                tree_state["roots"] = None
                tree_state["active_path"] = []
                tree_state["root_error_message"] = _UNAVAILABLE_MESSAGE_TEMPLATE.format(dhasa_label=label_for_message)
                _render_tree()
                _render_print_table()
                safe_notify('This dhasa is not available yet.', type='warning')
                return
            except Exception as e:
                tree_state["roots"] = None
                tree_state["active_path"] = []
                tree_state["root_error_message"] = f"(error computing root dhasa: {e})"
                _render_tree()
                _render_print_table()
                safe_notify(f'Error computing dhasa: {str(e)}', type='negative')
                return
            if md_rows is DelayedBusyIndicator.STOPPED:
                return
            base_kwargs = {'jd_at_dob': utils.julian_day_number(dob, tob), 'place': place,
                           'divisional_chart_factor': dcf, **option_kwargs}
            tree_state["roots"] = [
                _make_node(dhasa_name, dhasa_type_index, lords, label, start, end, 1, base_kwargs)
                for (lords, label, start, end) in md_rows
            ]
            tree_state["root_error_message"] = None
            tree_state["active_path"] = []  # close the drill-down on every new computation
            _render_tree()
            _render_print_table()
        _refresh_dhasa_options_button()
        ui.timer(0.1, compute_dhasa, once=True)
    render_footer()
_dhasa_graha_names = list(const._graha_dhasa_dict.keys())
_dhasa_rasi_names = list(const._rasi_dhasa_dict.keys())
_dhasa_annual_names = list(const._annual_dhasa_dict.keys())
def _dhasa_sub_option_ui():
    """Draws this entry's OWN custom widgets inside print_registry.py's dialog - replicates EXACTLY
    what the (now-removed) "Print Multiple Dhasas" dialog used to offer: "Selected dhasa only" vs.
    "By category" with Graha/Annual/Raasi checkboxes (any combination), the category checkboxes only
    visible once "By category" is picked (see this function's own on_value_change handler). Returned
    as a plain {name: widget} dict - print_registry.py's own _collect_sub_option_values() reads each
    widget's `.value` generically.
    """
    mode_radio = ui.radio(
        {0: res_str('selected_dhasa_only_str', 'Selected dhasa only'),
         1: res_str('by_category_str', 'By category')},
        value=0,
    ).props('inline')
    with ui.column().classes('gap-1 pl-4') as category_box:
        graha_cb = ui.checkbox(res_str('graha_str', 'Graha') + ' ' + res_str('dhasa_str', 'Dhasa'), value=True)
        annual_cb = ui.checkbox(res_str('annual_str', 'Annual') + ' ' + res_str('dhasa_str', 'Dhasa'), value=False)
        raasi_cb = ui.checkbox(res_str('raasi_str', 'Raasi') + ' ' + res_str('dhasa_str', 'Dhasa'), value=False)
        with annual_cb:
            ui.tooltip('Annual dhasas will use the Rasi (D1) varga, regardless of any dhasa\'s own '
                      'persisted varga choice - looping every varga for every annual dhasa would be '
                      'too slow to compute in one report.')
    category_box.set_visibility(False)
    mode_radio.on_value_change(lambda e: category_box.set_visibility(e.value == 1))
    return {'mode': mode_radio, 'graha': graha_cb, 'annual': annual_cb, 'raasi': raasi_cb}
def _dhasa_own_options(dhasa_type_index, dhasa_name):
    """Returns this dhasa's OWN persisted options (app.storage.user, via the module-level
    _DHASA_OPTIONS_KEY - the SAME storage key _get_dhasa_options() inside dhasa_page() reads/writes),
    read HEADLESSLY (no live widgets needed - app.storage.user is reachable from anywhere, unlike a
    live widget's own .value). divisional_chart_factor/chart_method are stripped - "By category"
    mode always forces D1 for every dhasa regardless of any dhasa's own persisted varga choice (see
    _dhasa_sub_option_ui()'s own tooltip for why).
    """
    state = ensure_default_state()
    store = state.get(_DHASA_OPTIONS_KEY)
    store = store if isinstance(store, dict) else {}
    opts = dict(store.get(f"{dhasa_type_index}:{dhasa_name}", {}))
    opts.pop('divisional_chart_factor', None)
    opts.pop('chart_method', None)
    return opts
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_values):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract, and _dhasa_sub_option_ui() above for where
    sub_option_values comes from. Reuses _build_dhasa_report_locked() and _dhasa_root_locked() /
    _root_rows_table_html(), the SAME functions this page's own (now-removed) multi-dhasa report
    builder and single-dhasa print table used.
    "Selected dhasa only" reads the PERSISTED Dhasa Type/Name/Varga selection
    (_DHASA_SELECTION_KEY, in app.storage.user - the SAME key _get_selection() inside dhasa_page()
    reads/writes) HEADLESSLY, rather than any live widget - this still reflects whatever this
    browser last had selected on the Dhasa page itself, exactly as the removed dialog's own
    "Selected dhasa only" mode did.
    """
    mode = sub_option_values.get('mode')
    mode = mode if isinstance(mode, int) else 0
    dhasa_specs = []
    if mode == 0:
        state = ensure_default_state()
        sel = state.get(_DHASA_SELECTION_KEY)
        sel = sel if isinstance(sel, dict) else {}
        dhasa_type_index = sel.get('dhasa_type_index', 0)
        if not isinstance(dhasa_type_index, int) or not (0 <= dhasa_type_index <= 2):
            dhasa_type_index = 0
        names = [_dhasa_graha_names, _dhasa_rasi_names, _dhasa_annual_names][dhasa_type_index]
        dhasa_name = sel.get('dhasa_name')
        if dhasa_name not in names:
            dhasa_name = names[0] if names else None
        if dhasa_name is None:
            with container:
                ui.html("<i>No dhasa available.</i>")
            return
        if dhasa_type_index == 2:
            varga_idx = sel.get('varga_index', 0)
            if not isinstance(varga_idx, int) or not (0 <= varga_idx < len(_division_chart_factors)):
                varga_idx = 0
            dcf = _division_chart_factors[varga_idx]
        else:
            dcf = 1
        option_kwargs = dict(ensure_default_state().get(_DHASA_OPTIONS_KEY) or {})
        option_kwargs = dict(option_kwargs.get(f"{dhasa_type_index}:{dhasa_name}", {}))
        dcf = option_kwargs.pop('divisional_chart_factor', dcf)
        dhasa_specs.append((dhasa_type_index, dhasa_name, dcf, option_kwargs))
    else:
        if sub_option_values.get('graha'):
            dhasa_specs += [(0, name, 1, _dhasa_own_options(0, name)) for name in _dhasa_graha_names]
        if sub_option_values.get('raasi'):
            dhasa_specs += [(1, name, 1, _dhasa_own_options(1, name)) for name in _dhasa_rasi_names]
        if sub_option_values.get('annual'):
            dhasa_specs += [(2, name, 1, _dhasa_own_options(2, name)) for name in _dhasa_annual_names]
        if not dhasa_specs:
            with container:
                ui.html("<i>No category selected - nothing to print for Dhasa.</i>")
            return
    try:
        pages = await run_io_bound_ctx(_build_dhasa_report_locked, dob, tob, place_val, lat_val, lon_val, tz_val, dhasa_specs)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Dhasa: {e}</i>")
        return
    if not pages:
        with container:
            ui.html("<i>Could not compute any dhasa (see the server console).</i>")
        return
    with container:
        for page in pages:
            with ui.column().classes('w-full dhasa-report-item'):
                ui.html(
                    f"<div style='margin-bottom:4px;'><b>{place_val}</b> &mdash; "
                    f"{dob[0]},{dob[1]},{dob[2]} {tob[0]:02d}:{tob[1]:02d}:{tob[2]:02d}</div>"
                    f"<div style='margin-bottom:4px;'><b>{page['title']}</b></div>"
                ).classes('dhasa-report-header')
                ui.html(page['rows_html'])
print_registry.register('dhasa', res_str('dhasa_str', 'Dhasa') + '/' + res_str('bhukthi_str', 'Bhukthi'), 'Dhasa',
                        _build_print_section, sub_option_ui=_dhasa_sub_option_ui)
