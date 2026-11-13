#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""General Prediction page (/prediction).
Lists the general predictions for the chart on the left; selecting one shows its text on the
right.
"Print / Save as PDF" prints ALL predictions found (not just the one currently selected in the
detail pane) - each with its own heading, flowing continuously across as many pages as needed. The
interactive list+detail view (icons/click handlers) is marked 'no-print' and never printed; a
separate, plain '.print-only' container (components.py's utility for exactly this "different,
cleaner view for print" need) shows every prediction's full text instead.

The list also ends with a "Vimsottari Dhasa Bhukthi" heading followed by ONE entry per Maha Dasa lord
(with its dates). Selecting a lord fills the right side with that lord's caution note, Maha Dasa text and
its nine Bhukthis; Save as PDF always prints the WHOLE sequence (see _vimsottari_report_locked() and
_vimsottari_blocks() below):
  * the Maha Dasa lords, Bhukthi lords and all dates come from PyJHora (dhasa_selector - the SAME
    engine the /dhasa page uses, default Vimsottari options, so both pages always agree);
  * the texts come from dasha_predictions_<lang>.json (B.V. Raman, 'How to Judge a Horoscope'):
      - JSON key = the Maha Dasa lord's PyJHora planet number as text (Sun "0", Moon "1", Mars "2",
        Mercury "3", Jupiter "4", Venus "5", Saturn "6", Rahu "7", Ketu "8");
      - ["predictions"][n] = Maha Dasa text, n = natal Rasi (0 Aries .. 11 Pisces) of the Maha lord;
      - ["bhuktis"][i]     = text of the i-th Bhukthi of that Maha Dasa, in PyJHora's returned order
        (i = 0 is the Maha lord's own Bhukthi, then the Vimsottari sequence continues).
"""
import html as _html
import json
import os
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope.prediction import general
from jhora.horoscope.dhasa import dhasa_selector
from jhora.horoscope.chart import charts
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        render_footer, print_button, run_io_bound_ctx, )
import print_registry
drik = utils.hora_engine_proxy

# ---------------------------------------------------------------------------------------------------
# Vimsottari Dhasa / Bhukthi predictions (B.V. Raman)
# ---------------------------------------------------------------------------------------------------
# Planet numbers (PyJHora): Sun 0, Moon 1, Mars 2, Mercury 3, Jupiter 4, Venus 5, Saturn 6, Rahu 7, Ketu 8.
# dasha_predictions_<lang>.json is keyed by that same planet number (as text). Each planet's "bhuktis"
# list starts with the planet itself and then follows the Vimsottari sequence, as in the book (and
# as PyJHora returns the Bhukthis). _VIM_SEQ is only used as a fallback for the Bhukthi position.
_VIM_SEQ = [0, 1, 2, 7, 4, 6, 3, 8, 5]
_VIM_JSON_KEY = {planet: str(planet) for planet in range(9)}
_DASHA_JSON_PATTERN = 'dasha_predictions_{lang}.json'
_DASHA_JSON_CACHE = {}
_DEFAULT_CAUTION = ("Please note that these predictions are excerpts from the book 'How to judge Horoscope' of "
                    "B.V. Raman. These are general in nature. The exact nature of the results should be "
                    "interpreted by taking into account, the various dignities and strengths of planets and houses.")
_ENGLISH_RAASI = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius',
                  'Capricorn', 'Aquarius', 'Pisces']
def _vimsottari_title():
    """Left-menu entry / right-side heading: 'Vimsottari Dhasa Bhukthi' (localized)."""
    return (res_str('vimsottari_str', 'Vimsottari') + ' ' + res_str('dhasa_str', 'Dhasa') + ' ' +
            res_str('bhukthi_str', 'Bhukthi'))
_DASHA_JSON_SEARCHED = []     # paths tried by the last _load_dasha_predictions() call (shown if nothing is found)
def _dasha_json_dirs():
    """Folders searched for dasha_predictions_<lang>.json, in order (duplicates removed): const._LANGUAGE_PATH
    (where the app's other language/NLS files live) first, then the folder of this file as a fallback."""
    dirs = []
    lang_path = getattr(const, '_LANGUAGE_PATH', None)
    if isinstance(lang_path, str) and lang_path:
        dirs.append(lang_path)
    here = os.path.dirname(os.path.abspath(__file__))
    dirs += [here, os.path.join(here, 'lang')]
    seen, out = set(), []
    for d in dirs:
        d = os.path.normpath(d)
        if d not in seen:
            seen.add(d); out.append(d)
    return out
def _load_dasha_predictions():
    """Returns the Dasha prediction JSON (dict) for the visitor's language - falling back to English when
    there is no file for that language yet - cached per file. Returns {} when no file can be read; the paths
    tried are then in _DASHA_JSON_SEARCHED (and printed on the console)."""
    try:
        import components
        lang = components._visitor_language()
    except Exception:
        lang = str(getattr(const, '_DEFAULT_LANGUAGE', 'en') or 'en').strip().lower()
    _DASHA_JSON_SEARCHED.clear()
    for code in dict.fromkeys((lang, 'en')):
        for folder in _dasha_json_dirs():
            path = os.path.join(folder, _DASHA_JSON_PATTERN.format(lang=code))
            if path in _DASHA_JSON_CACHE:
                return _DASHA_JSON_CACHE[path]
            _DASHA_JSON_SEARCHED.append(path)
            if os.path.isfile(path):
                try:
                    with open(path, encoding='utf-8-sig') as f:
                        _DASHA_JSON_CACHE[path] = json.load(f)
                    print(f"[prediction_page] Dasha predictions loaded from {path}")
                    return _DASHA_JSON_CACHE[path]
                except Exception as ex:
                    print(f"[prediction_page] cannot read {path}: {type(ex).__name__}: {ex}")
    print("[prediction_page] dasha_predictions_<lang>.json NOT FOUND. Looked for:\n  " + "\n  ".join(_DASHA_JSON_SEARCHED))
    return {}
def _missing_json_note():
    """HTML warning shown on the Vimsottari report when no prediction file could be loaded ('' otherwise)."""
    if _load_dasha_predictions():
        return ''
    tried = '<br>'.join(_html.escape(x) for x in _DASHA_JSON_SEARCHED[:6])
    return ("<div style='color:#b91c1c; margin:6px 0;'><b>Prediction texts not found:</b> "
            f"{_html.escape(_DASHA_JSON_PATTERN.format(lang='en'))} must be placed in the language folder (const._LANGUAGE_PATH). Looked in:"
            f"<br>{tried}</div>")
def _lord_ints(lords):
    """Normalizes the `lords` part of a dhasa_selector row (an int, or a list/tuple of ints) to a list of ints."""
    if isinstance(lords, (list, tuple)):
        out = []
        for x in lords:
            try:
                if not isinstance(x, bool):
                    out.append(int(x))
            except (TypeError, ValueError):
                pass
        return out
    try:
        return [int(lords)]
    except (TypeError, ValueError):
        return []
def _fmt_date(t):
    """'YYYY-MM-DD' for a (year, month, day, fractional_hours) tuple ('' if empty)."""
    if not t:
        return ''
    return f"{int(t[0]):04d}-{int(t[1]):02d}-{int(t[2]):02d}"
def _sign_name(sign_index):
    try:
        return utils.RAASI_LIST[sign_index]
    except Exception:
        return _ENGLISH_RAASI[sign_index % 12]
def _vimsottari_report_locked(y, m, d, t, pv, lat, lon, tz):
    """Computes the person's Vimsottari Maha Dasa / Bhukthi periods and the natal Rasi of each Maha lord, under
    calc_lock(); blocking - run in a worker thread (busy.run() / run_io_bound_ctx()).
    Returns a list (one dict per Maha Dasa, in time order):
        {'lord': planet number, 'label': Maha lord name, 'sign': natal Rasi 0..11, 'start': t, 'end': t,
         'bhuktis': [{'label': 'Sun-Moon'-style label, 'start': t, 'end': t}, ... in PyJHora's order]}
    Raises ValueError when a Maha lord cannot be identified in dhasa_selector's output.
    """
    with calc_lock():
        dob = drik.Date(y, m, d)
        jd = utils.julian_day_number(dob, t)
        place = drik.Place(pv, lat, lon, tz, 0.0)
        # Natal Rasi of every planet: planet_positions = [['L', (rasi, long)], [0, (rasi, long)], ...]
        rasi_of = {}
        for entry in charts.rasi_chart(jd, place):
            if isinstance(entry[0], int) and not isinstance(entry[0], bool):
                rasi_of[entry[0]] = int(entry[1][0])
        roots = dhasa_selector.get_dhasa_root_nodes(0, 'vimsottari', dob, t, place, divisional_chart_factor=1)
        child_kwargs = {'jd_at_dob': jd, 'place': place, 'divisional_chart_factor': 1}
        report = []
        for lords, label, start, end in roots:
            ids = _lord_ints(lords)
            if not ids or ids[0] not in _VIM_JSON_KEY:
                raise ValueError(f"Cannot identify the Vimsottari Maha lord from {lords!r}")
            maha = ids[0]
            rows = dhasa_selector.get_dhasa_children('vimsottari', lords, start, parent_end=end, **child_kwargs) or []
            bhuktis = []
            for i, (b_lords, b_label, b_start, b_end) in enumerate(rows):
                idx = i
                if len(rows) != len(_VIM_SEQ):
                    # Unexpected row count: take the position from the Bhukthi lord instead.
                    b_ids = _lord_ints(b_lords)
                    if b_ids and b_ids[-1] in _VIM_SEQ:
                        idx = (_VIM_SEQ.index(b_ids[-1]) - _VIM_SEQ.index(maha)) % len(_VIM_SEQ)
                bhuktis.append({'label': b_label, 'start': b_start, 'end': b_end, 'index': idx})
            report.append({'lord': maha, 'label': label, 'sign': rasi_of.get(maha, 0), 'start': start,
                           'end': end, 'bhuktis': bhuktis})
        return report
def _vimsottari_blocks(report):
    """Turns _vimsottari_report_locked()'s result into display blocks: a list of (kind, heading_html, text) where
    kind is 'maha' or 'bhukthi' and text is plain (un-escaped) prediction text. One list drives both the
    on-screen detail pane and the print view."""
    data = _load_dasha_predictions()
    blocks = []
    for maha in report:
        entry = data.get(_VIM_JSON_KEY[maha['lord']]) or {}
        preds, bhuks = entry.get('predictions') or [], entry.get('bhuktis') or []
        sign = maha['sign']
        maha_text = preds[sign] if 0 <= sign < len(preds) else ''
        blocks.append(('maha',
                       f"{_html.escape(str(maha['label']))} {res_str('dhasa_str', 'Dhasa')} "
                       f"({_fmt_date(maha['start'])} &ndash; {_fmt_date(maha['end'])}) &mdash; "
                       f"{_html.escape(str(maha['label']))} / {_html.escape(str(_sign_name(sign)))}",
                       maha_text))
        for b in maha['bhuktis']:
            i = b['index']
            blocks.append(('bhukthi',
                           f"{_html.escape(str(b['label']))} ({_fmt_date(b['start'])} &ndash; {_fmt_date(b['end'])})",
                           bhuks[i] if 0 <= i < len(bhuks) else ''))
    return blocks
def _vimsottari_html(report):
    """Vimsottari report as ONE html string (the on-screen right-side pane). `report` is normally a list with
    ONE Maha Dasa entry (the lord selected in the left menu); the print view draws the whole list instead."""
    caution = res_str('general_prediction_caution', _DEFAULT_CAUTION)
    if not report:
        return f"<i>{res_str('no_results_str', 'No predictions found.')}</i>"
    parts = [f"<b><u>{_html.escape(_vimsottari_title())}</u></b><br>",
             f"<i>{_html.escape(caution)}</i><br>", _missing_json_note(), "<br>"]
    for kind, heading, text in _vimsottari_blocks(report):
        if kind == 'maha':
            parts.append(f"<div style='margin-top:14px; padding:2px 6px; background:#f0fdf4; border-left:4px solid "
                         f"#15803d;'><b>{heading}</b></div>")
            parts.append(f"<div style='margin:4px 0 6px 0;'>{_html.escape(text)}</div>")
        else:
            parts.append(f"<div style='margin:8px 0 0 14px;'><b><u>{heading}</u></b></div>")
            parts.append(f"<div style='margin:2px 0 4px 14px;'>{_html.escape(text)}</div>")
    return ''.join(parts)
def _draw_vimsottari_print(report):
    """Draws the Vimsottari report into the CURRENT ui container, one element per heading / text so the
    browser can break pages between them (headings stay attached to their own text via 'print-attach-next')."""
    ui.label(_vimsottari_title()).classes('text-base font-bold text-green-700 print-attach-next')
    ui.html(f"<i>{_html.escape(res_str('general_prediction_caution', _DEFAULT_CAUTION))}</i>").classes('text-sm')
    _note = _missing_json_note()
    if _note:
        ui.html(_note).classes('text-sm')
    for kind, heading, text in _vimsottari_blocks(report):
        with ui.column().classes('gap-1' + (' ml-4' if kind == 'bhukthi' else '')):
            ui.html(f"<b><u>{heading}</u></b>").classes('print-attach-next')
            ui.html(_html.escape(text)).classes('text-sm')
def _prediction_locked(y, m, d, t, pv, lat, lon, tz):
    """Computes the general predictions under calc_lock(); the slow part of compute(), run in a worker
    thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        jd = utils.julian_day_number(drik.Date(y, m, d), t)
        place = drik.Place(pv, lat, lon, tz, 0.0)
        return general.get_prediction_details(jd, place, language=const._DEFAULT_LANGUAGE)
@ui.page('/prediction')
def prediction_page():
    navigation_header(); ensure_default_state()
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('general_prediction_str', 'General Prediction')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute(), on_calculate=lambda: compute())
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        with ui.row().classes('w-full gap-6 items-start flex-nowrap no-print'):
            with ui.column().classes('w-80 shrink-0 gap-1'):
                ui.label(res_str('general_prediction_str', 'General Prediction') + ' ' + res_str('list_str', 'List')).classes('font-bold text-green-700')
                pred_list = ui.column().classes('max-h-[640px] overflow-y-auto gap-1 border rounded p-2 bg-gray-50')
            with ui.column().classes('flex-1') as detail_col:
                detail_html = ui.html('').classes('text-sm')
        # 'print-only' (components.py's utility): hidden on screen, shown ONLY for print - lists
        # EVERY prediction's full text, not just the one currently selected in detail_html above.
        # 'single-chart-print-block' (added): 'print-only' alone shows this during ANY print, but
        # does not hide it during the global combined "Save as PDF" print (body.printing-all - see
        # components.py's _PRINT_CSS) - without this class, this page's own live print_container
        # stayed visible on whatever page a visitor happened to be sitting on AND
        # print_registry.py's own _build_print_section() built a SECOND, independent copy into the
        # hidden '.all-charts-report' container, duplicating General Prediction - the same bug
        # confirmed and fixed for amsa_ruler_tab.py's and 12 other pages' identical pattern.
        print_container = ui.column().classes('w-full gap-3 print-only single-chart-print-block')
    state = {'results': {}, 'vimsottari': []}
    def show_detail(name, text):
        detail_html.set_content(f"<b><u>{name}</u></b><br>{text}<br>")
        # Scroll the detail panel into view.
        ui.run_javascript(
            f'getElement({detail_col.id}).scrollIntoView({{behavior: "smooth", block: "start"}});'
        )
    def show_vimsottari(maha):
        """Right side = the selected Maha lord's report: caution, its Maha Dasa text and its nine Bhukthis."""
        detail_html.set_content(_vimsottari_html([maha]))
        ui.run_javascript(
            f'getElement({detail_col.id}).scrollIntoView({{behavior: "smooth", block: "start"}});'
        )
    def render_list():
        pred_list.clear()
        with pred_list:
            for name, text in state['results'].items():
                ui.label(name).classes('cursor-pointer hover:bg-green-100 rounded px-1').on(
                    'click', lambda n=name, t=text: show_detail(n, t)
                )
            # Vimsottari Dhasa Bhukthi: a heading, then ONE entry per Maha lord (in Dasa order, with its dates).
            if state['vimsottari']:
                ui.label(_vimsottari_title()).classes(
                    'font-semibold text-green-800 border-t border-gray-300 mt-1 pt-1 px-1')
                for maha in state['vimsottari']:
                    ui.label(f"{maha['label']} ({_fmt_date(maha['start'])} \u2013 {_fmt_date(maha['end'])})").classes(
                        'cursor-pointer hover:bg-green-100 rounded px-1 ml-2 text-sm').on(
                        'click', lambda m=maha: show_vimsottari(m))
    def render_print_content():
        """Fills print_container with EVERY prediction's own heading + full text - see the module
        docstring for why this is a separate, print-only view rather than just printing whatever
        happens to be selected in the on-screen detail pane.
        """
        print_container.clear()
        with print_container:
            if not state['results'] and not state['vimsottari']:
                ui.html(f"<i>{res_str('no_results_str', 'No predictions found.')}</i>")
                return
            for name, text in state['results'].items():
                with ui.column().classes('gap-1'):
                    # 'print-attach-next': keeps this prediction's own heading attached to the start
                    # of its own text below (see components.py's module docstring for the general
                    # "heading separated from its own content" bug class this class fixes).
                    ui.html(f"<b><u>{name}</u></b>").classes('print-attach-next')
                    ui.html(text).classes('text-sm')
            if state['vimsottari']:
                _draw_vimsottari_print(state['vimsottari'])
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.', type='warning'); return
        try:
            dv = w['dob_input'].value.strip(); tv = w['tob_input'].value.strip()
            pv = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat = float(w['lat_input'].value); lon = float(w['lon_input'].value); tz = float(w['tz_input'].value)
            y, m, d = map(int, dv.split(',')); tp = [int(x) for x in tv.split(':')]; t = tuple((tp + [0])[:3])
        except Exception as ex:
            safe_notify(f'Error computing Predictions: {ex}', type='negative'); return
        try:
            results = await busy.run(_prediction_locked, y, m, d, t, pv, lat, lon, tz,
                                     wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing Predictions: {ex}', type='negative'); return
        if results is DelayedBusyIndicator.STOPPED:
            return
        state['results'] = results
        # Vimsottari report: a failure here must not take the general predictions down with it.
        try:
            vim = await busy.run(_vimsottari_report_locked, y, m, d, t, pv, lat, lon, tz,
                                 wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as ex:
            print(f"[prediction_page] Vimsottari report failed: {type(ex).__name__}: {ex}")
            safe_notify(f'Error computing Vimsottari Dhasa Bhukthi: {ex}', type='negative')
            vim = []
        if vim is DelayedBusyIndicator.STOPPED:
            return
        state['vimsottari'] = vim
        render_list()
        render_print_content()
        if results:
            first_name = next(iter(results))
            show_detail(first_name, results[first_name])
        else:
            detail_html.set_content(f"<i>{res_str('no_results_str', 'No predictions found.')}</i>")
    ui.timer(0.1, compute, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Reuses _prediction_locked() (the SAME calculation
    function this page's own compute() calls), draws EVERY prediction found directly into
    `container` (no live widgets of this page are read).
    """
    try:
        results = await run_io_bound_ctx(_prediction_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Predictions: {e}</i>")
        return
    # Vimsottari report: a failure here must not lose the general predictions.
    try:
        vim = await run_io_bound_ctx(_vimsottari_report_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val)
    except Exception as e:
        print(f"[prediction_page] Vimsottari print section failed: {type(e).__name__}: {e}")
        vim = []
    with container:
        ui.label(res_str('general_prediction_str', 'General Prediction')).classes('text-base font-bold text-green-700 print-attach-next')
        if not results and not vim:
            ui.html(f"<i>{res_str('no_results_str', 'No predictions found.')}</i>")
            return
        for name, text in (results or {}).items():
            with ui.column().classes('gap-1'):
                ui.html(f"<b><u>{name}</u></b>").classes('print-attach-next')
                ui.html(text).classes('text-sm')
        if vim:
            _draw_vimsottari_print(vim)
print_registry.register('prediction', 'General Prediction', 'Yoga / Dosha / Prediction', _build_print_section)
