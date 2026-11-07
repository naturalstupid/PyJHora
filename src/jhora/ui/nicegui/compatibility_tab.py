#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility (Porutham) page (/compatibility).
Finds, for a birth star (nakshatra) and paadham and a gender, the partner nakshatra / paadham
combinations ranked by compatibility score (jhora.horoscope.match.compatibility.Match).
Matching combinations are listed on the left; the selected one is shown on the right as a table
of the individual poruthams, their results and the overall match.
The Birth Star and Paadham selectors are set to the star and paadham of the entered birth details
(drik.nakshatra) whenever those details change; they can then be changed to try other star /
gender combinations. Gender is the shared, top-level field (components.render_control_bar()'s
gender_select widget, mirroring the PyQt desktop app's main-window Gender combo box) - the same
field the Yoga page reads - rather than a selector local to this page, so the chart owner's gender
stays consistent across every page that depends on it. Gender index 0 (Male) treats the entered
star/paadham as the "boy" side of the match; any other value treats it as the "girl" side. The
selectors and options of the second control row stay on one row; on a narrow window the row
scrolls sideways.
The scoring rules follow the chart style stored by the Kundali page: South Indian styles use the
Tamil-style poruthams (True / False checks), other styles use percentage scoring. The minimum
score defaults follow that choice (const.compatibility_minimum_score_south / _north).
"Print / Save as PDF" prints EVERY matching partner found (state['matches'], not just the one
currently selected in the detail pane on the right) - per explicit scope decision, since the match
list is open-ended and the user wants the full result set on paper, not only whichever one row
happens to be selected on screen. Each partner gets its own compatibility table, with its own
heading attached to the start of its own table. The interactive list+detail view is marked
'no-print' and never printed; a separate, plain '.print-only' container (components.py's utility
for exactly this "different, cleaner view for print" need) rebuilds every partner's own table using
the SAME table-building logic the on-screen detail pane uses (_match_title_html() /
_match_table_only_html() - two SEPARATE functions/elements, not one combined blob, specifically so
'print-attach-next' can be applied to just the heading - see _match_title_html()'s own docstring for
the page-break bug this split fixes), so the two views cannot silently drift out of sync with each
other over time.
"""
from nicegui import ui, app, run
from jhora import const, utils
from jhora.horoscope.match import compatibility
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        render_footer, print_button, run_io_bound_ctx, )
import print_registry
drik = utils.hora_engine_proxy
_STAR_COUNT = 27
_PAADHAM_COUNT = 4
# How many matches' own compatibility tables are grouped into one '.print-side-by-side' row for
# print - see render_print_content()'s own docstring for the full reasoning. 3 was chosen per the
# user's own explicit request ("there is enough space for 3 tables") - if a FUTURE change to this
# table's own layout (e.g. more columns, longer porutham names) makes 3 tables too cramped to read
# comfortably side by side, lowering this constant to 2 is the simplest fix; this is the ONLY place
# that number needs to change (both the live print view and the central-dialog headless view read
# this same constant, so they cannot drift out of sync with each other on this).
_MATCHES_PER_PRINT_ROW = 3
def _south_style():
    """Returns True if the chart style stored by the Kundali page is a South Indian style, False
    otherwise. Selects the South (Tamil-style) or North (percentage) compatibility rules.
    """
    state = app.storage.user
    raw = state.get('kundali_chart_style', state.get('chart_style', None))
    if raw is None:
        try:
            idx = int(state.get('kundali_chart_style_index', 0))
            raw = list(const.AVAILABLE_CHART_STYLES.keys())[idx]
        except Exception:
            raw = 'south_indian_regular'
    text = (getattr(raw, 'name', None) or str(raw)).lower()
    return ('south' in text) or ('irregular' in text and 'south' in text) or text in ('south_indian_regular', 'south_indian_irregular')
def _compatibility_match_locked(bn, bp, gn, gp, mahendra_val, vedha_val, rajju_val, sthree_val, min_score_val, style_key):
    """Computes the matching partner list under calc_lock(); the slow part of compute() - checks every
    nakshatra/paadham combination - run in a worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        comp = compatibility.Match(
            boy_nakshatra_number=bn, boy_paadham_number=bp,
            girl_nakshatra_number=gn, girl_paadham_number=gp,
            check_for_mahendra_porutham=mahendra_val, check_for_vedha_porutham=vedha_val,
            check_for_rajju_porutham=rajju_val, check_for_shreedheerga_porutham=sthree_val,
            minimum_score=min_score_val, method=style_key,
        )
        return utils.sort_tuple(comp.get_matching_partners(), 3, reverse=True)
def _match_title_html(m_tuple):
    """Returns ONLY the heading HTML (nakshatra - paadham) of one match - split out from the table
    itself (see _match_table_only_html()) specifically so the two can be placed as TWO SEPARATE
    sibling elements for print, with 'print-attach-next' applied to JUST this heading element - see
    the module docstring's own note on why this split is necessary (a single combined HTML blob
    containing both the heading and the table gave the browser's print engine no element boundary
    to anchor a "keep together" rule to, so a page break could land INSIDE that blob, between the
    heading and its own table, even with 'print-attach-next' applied to the blob's own OUTER
    wrapper - that class only has break-before/break-after:avoid, nothing stops an INTERNAL split;
    confirmed from an actual printed PDF where match N's table ended one page and match N+1's own
    heading started that same page, with match N+1's table only starting on the NEXT page).
    """
    nak_num, paadha_num, _ettu_results, _score, _naalu_results = m_tuple
    nakshatra_name = utils.NAKSHATRA_LIST[nak_num - 1]
    return f"<b>{nakshatra_name} - {res_str('paadham_str', 'Paadham')} {paadha_num}</b>"
def _match_table_only_html(m_tuple, south):
    """Returns ONLY the <table>...</table> HTML of one match's compatibility table (the individual
    poruthams, their results and the overall match) - see _match_title_html() for why this is now
    split from the heading into its own, separate function/element.
    Args:
        m_tuple: one (nakshatra_number, paadham_number, ettu_results, score, naalu_results) tuple,
            e.g. from state['matches'].
        south: this page's own state['south'] (True for South Indian / Tamil-style poruthams, False
            for North / percentage scoring) - NOT re-derived here, so a print pass stays consistent
            with whatever rule set was actually used to compute state['matches'] in the first place.
    """
    nak_num, paadha_num, ettu_results, score, naalu_results = m_tuple
    if south:
        ettu_list = [res_str(p, p.replace('_str', '').replace('_', ' ').title()) for p in compatibility.compatibility_list_south]
        ettu_results = ettu_results[1:-1]
    else:
        ettu_list = [res_str(p, p.replace('_str', '').replace('_', ' ').title()) for p in compatibility.compatibility_list_north]
    ettu_max = [compatibility.varna_max_score, compatibility.vasiya_max_score, compatibility.gana_max_score,
                compatibility.nakshathra_max_score, compatibility.yoni_max_score, compatibility.raasi_adhipathi_max_score,
                compatibility.raasi_max_score, compatibility.naadi_max_score]
    naalu_list = [res_str(p, p.replace('_str', '').replace('_', ' ').title()) for p in compatibility.naalu_porutham_list]
    minimum_tamil_porutham = naalu_results[-1]
    _th = 'border:1px solid #5c3a21;padding:4px 8px;background:#f0fdf4;text-align:left;'
    _td = 'border:1px solid #d1d5db;padding:4px 8px;text-align:center;'
    _td_label = 'border:1px solid #d1d5db;padding:4px 8px;font-weight:bold;text-align:left;'
    html = ["<table style='border-collapse:collapse;width:100%;'>"]
    headers = ('', res_str('result_str', 'Result'), res_str('max_score_str', 'Max/Basis'), res_str('status_str', 'Status'))
    html.append('<tr>' + ''.join(f"<th style='{_th}'>{h}</th>" for h in headers) + '</tr>')
    for p, name in enumerate(ettu_list):
        val = ettu_results[p] if p < len(ettu_results) else ''
        if south:
            max_col, status_col = 'True', (str(const._GREEN_CHECK) if val else str(const._RED_CROSS))
        else:
            max_val = ettu_max[p] if p < len(ettu_max) else ''
            max_col = str(max_val)
            status_col = '{:3.0f}%'.format(val / max_val * 100) if max_val else ''
        html.append(f"<tr><td style='{_td_label}'>{name}</td><td style='{_td}'>{val}</td>"
                    f"<td style='{_td}'>{max_col}</td><td style='{_td}'>{status_col}</td></tr>")
    for p, name in enumerate(naalu_list):
        val = naalu_results[p] if p < len(naalu_results) else ''
        status_col = str(const._GREEN_CHECK) if val else str(const._RED_CROSS)
        html.append(f"<tr><td style='{_td_label}'>{name}</td><td style='{_td}'>{val}</td>"
                    f"<td style='{_td}'>True</td><td style='{_td}'>{status_col}</td></tr>")
    if south:
        max_col = str(compatibility.max_compatibility_score_south)
        status_col = str(const._GREEN_CHECK) if minimum_tamil_porutham else str(const._RED_CROSS)
    else:
        max_col = str(compatibility.max_compatibility_score)
        status_col = '{:3.0f}%'.format(score / compatibility.max_compatibility_score * 100)
    html.append(f"<tr><td style='{_td_label};background:#f0fdf4;'>{res_str('overall_match_str', 'Overall Match')}</td>"
                f"<td style='{_td};font-weight:bold;'>{score}</td><td style='{_td}'>{max_col}</td><td style='{_td}'>{status_col}</td></tr>")
    html.append('</table>')
    return ''.join(html)
@ui.page('/compatibility')
def compatibility_page():
    navigation_header(); ensure_default_state()
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('compatibility_str', 'Compatibility')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute(), on_calculate=lambda: compute(),
                                calculate_label=res_str('compute_str', 'Find Matches'))
        # Gender is the shared, top-level field drawn by render_control_bar() (row 1) - not a selector
        # local to this page; see the module docstring.
        gender_select = w['gender_select']
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        # Row 2 never wraps: its widgets keep their width and the row scrolls sideways on a narrow window.
        w['row2'].classes(add='flex-nowrap overflow-x-auto', remove='flex-wrap')
        with w['row2']:
            star = ui.select({i + 1: utils.NAKSHATRA_LIST[i] for i in range(_STAR_COUNT)}, value=1,
                             label=res_str('birth_star_str', 'Birth Star')).props('outlined dense').classes('w-44 shrink-0')
            paadham = ui.select({i: str(i) for i in range(1, _PAADHAM_COUNT + 1)}, value=1,
                                label=res_str('paadham_str', 'Paadham')).props('outlined dense').classes('w-24 shrink-0')
            mahendra = ui.checkbox(res_str('mahendra_match_str', 'Mahendra Porutham'), value=False) \
                .props('dense').classes('text-xs shrink-0 whitespace-nowrap')
            vedha = ui.checkbox(res_str('vedha_match_str', 'Vedha Porutham'), value=False) \
                .props('dense').classes('text-xs shrink-0 whitespace-nowrap')
            rajju = ui.checkbox(res_str('rajju_match_str', 'Rajju Porutham'), value=False) \
                .props('dense').classes('text-xs shrink-0 whitespace-nowrap')
            sthree = ui.checkbox(res_str('sthree_dheerga_match_str', 'Sthree Dheerga Porutham'), value=False) \
                .props('dense').classes('text-xs shrink-0 whitespace-nowrap')
            min_score = ui.number(label=res_str('minimum_score_str', 'Minimum Score'), value=0.0, step=1.0) \
                .props('outlined dense').classes('w-32 shrink-0')
        with ui.row().classes('w-full gap-6 items-start flex-nowrap no-print'):
            with ui.column().classes('w-80 shrink-0 gap-1'):
                ui.label(res_str('matching_stars_str', 'Matching Nakshatras')).classes('font-bold text-green-700')
                match_list = ui.column().classes('max-h-[640px] overflow-y-auto gap-1 border rounded p-2 bg-gray-50')
            with ui.column().classes('flex-1') as detail_col:
                detail_table = ui.column().classes('w-full')
        # 'print-only' (components.py's utility): hidden on screen, shown ONLY for print - lists
        # EVERY matching partner found (all of state['matches']), not just the one currently
        # selected in detail_table above - see the module docstring for the explicit scope decision
        # behind this (the match list can be long and open-ended).
        # 'single-chart-print-block' (added): 'print-only' alone shows this during ANY print, but
        # does not hide it during the global combined "Save as PDF" print (body.printing-all - see
        # components.py's _PRINT_CSS) - without this class, this page's own live print_container
        # stayed visible on whatever page a visitor happened to be sitting on AND
        # print_registry.py's own _build_print_section() built a SECOND, independent copy into the
        # hidden '.all-charts-report' container, duplicating Compatibility - the same bug confirmed
        # and fixed for amsa_ruler_tab.py's and 12 other pages' identical pattern.
        print_container = ui.column().classes('w-full gap-4 print-only single-chart-print-block')
    state = {'matches': [], 'south': True, 'birth_key': None, 'setting_star': False}
    def refresh_score_defaults():
        south = _south_style()
        state['south'] = south
        with calc_lock():  # read inside calc_lock() so the visitor's own settings apply
            mins, maxs = const.compatibility_minimum_score_south, const.compatibility_maximum_score_south
            minn, maxn = const.compatibility_minimum_score_north, const.compatibility_maximum_score_north
        if south:
            min_score.value = mins
            min_score.props(f'step=1.0 max={maxs} min=0')
        else:
            min_score.value = minn
            min_score.props(f'step=0.5 max={maxn} min=0')
    def show_match(m_tuple):
        detail_table.clear()
        with detail_table:
            ui.html(_match_title_html(m_tuple))
            ui.html(_match_table_only_html(m_tuple, state['south']))
        # Scroll the detail panel into view.
        ui.run_javascript(
            f'getElement({detail_col.id}).scrollIntoView({{behavior: "smooth", block: "start"}});'
        )
    def render_list():
        match_list.clear()
        with match_list:
            if not state['matches']:
                ui.label(res_str('no_matching_found_str', 'No matching found')).classes('text-gray-500')
                return
            for m in state['matches']:
                nak_num, paadha_num, _ettu, score, _naalu = m
                label = f"{utils.NAKSHATRA_LIST[nak_num - 1]} - {paadha_num} ({score})"
                ui.label(label).classes('cursor-pointer hover:bg-green-100 rounded px-1').on(
                    'click', lambda mm=m: show_match(mm)
                )
    def render_print_content():
        """Fills print_container with EVERY matching partner's own full compatibility table (not
        just the one currently selected in detail_table above) - see the module docstring for the
        explicit scope decision behind this. Reuses _match_title_html()/_match_table_only_html(),
        the SAME functions show_match() itself calls, so a printed table can never silently differ
        from what that same match's own on-screen detail table shows.
        Heading and table are TWO SEPARATE elements (ui.html() calls) within each match's own
        ui.column(), with 'print-attach-next' on ONLY the heading - see _match_title_html()'s own
        docstring for why a single combined heading+table HTML blob (an earlier version of this
        function) let a page break land INSIDE that blob, between a match's own heading and its own
        table.
        Matches are grouped 3-PER-ROW (see _MATCHES_PER_PRINT_ROW), each group wrapped in its own
        '.print-side-by-side' row (the SAME class already proven working for Amsa Ruler's/Saham's/
        Drishti's/Argala's multi-table layouts - reused here rather than inventing a second,
        parallel mechanism) - this is what lets 3 individually-compact compatibility tables actually
        SIT NEXT TO EACH OTHER on one landscape page, instead of each one being printed on its own
        separate page (the user's own explicit request: "there is enough space for 3 tables").
        """
        print_container.clear()
        with print_container:
            if not state['matches']:
                ui.html(f"<i>{res_str('no_matching_found_str', 'No matching found')}</i>")
                return
            matches = state['matches']
            for row_start in range(0, len(matches), _MATCHES_PER_PRINT_ROW):
                row_matches = matches[row_start:row_start + _MATCHES_PER_PRINT_ROW]
                with ui.row().classes('w-full gap-3 items-start flex-wrap print-side-by-side'):
                    for m in row_matches:
                        with ui.column().classes('gap-1 min-w-72'):
                            ui.html(_match_title_html(m)).classes('print-attach-next')
                            ui.html(_match_table_only_html(m, state['south']))
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.', type='warning')
            return
        try:
            refresh_score_defaults()
            dv = w['dob_input'].value.strip(); tv = w['tob_input'].value.strip()
            pv = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat = float(w['lat_input'].value); lon = float(w['lon_input'].value); tz = float(w['tz_input'].value)
            y, m, d = map(int, dv.split(',')); tp = [int(x) for x in tv.split(':')]; t = tuple((tp + [0])[:3])
            south = _south_style()
            style_key = list(const.AVAILABLE_CHART_STYLES.keys())[0]
            try:
                raw = app.storage.user.get('kundali_chart_style')
                if raw:
                    style_key = getattr(const.CHART_STYLE, raw, style_key)
            except Exception:
                pass
            # Quick astronomical lookup (just the birth nakshatra/paadham) stays inline, under
            # calc_lock(), since it is fast and its result is used to update the star/paadham
            # selectors (a UI change, which must happen on the main thread, not in a worker thread).
            with calc_lock():
                jd = utils.julian_day_number(drik.Date(y, m, d), t)
                place = drik.Place(pv, lat, lon, tz, 0.0)
                nak = drik.nakshatra(jd, place)
            birth_key = (dv, tv, pv, lat, lon, tz)
            if state['birth_key'] != birth_key:
                # New birth details: the selectors show the star and paadham of the birth.
                state['birth_key'] = birth_key
                state['setting_star'] = True
                try:
                    star.value, paadham.value = int(nak[0]), int(nak[1])
                finally:
                    state['setting_star'] = False
            nakshatra_number, paadha_number = int(star.value), int(paadham.value)
            # Gender comes from the shared control-bar field (0=Male, 1=Female); see module docstring.
            gender_value = gender_select.value if isinstance(gender_select.value, int) else int(const.GENDER.FEMALE)
            bn = bp = gn = gp = None
            if gender_value == 0:
                bn, bp = nakshatra_number, paadha_number
            else:
                gn, gp = nakshatra_number, paadha_number
        except Exception as ex:
            safe_notify(f'Error computing Compatibility: {ex}', type='negative')
            return
        try:
            # The actual partner search - checks every nakshatra/paadham combination - is the slow
            # part, so it alone runs in a worker thread.
            matches = await busy.run(_compatibility_match_locked, bn, bp, gn, gp, mahendra.value, vedha.value,
                                     rajju.value, sthree.value, float(min_score.value or 0), style_key,
                                     wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing Compatibility: {ex}', type='negative')
            return
        if matches is DelayedBusyIndicator.STOPPED:
            return
        state['matches'] = matches
        render_list()
        render_print_content()
        if matches:
            show_match(matches[0])
        else:
            detail_table.clear()
    gender_select.on_value_change(lambda e: compute())
    star.on_value_change(lambda e: None if state['setting_star'] else compute())
    paadham.on_value_change(lambda e: None if state['setting_star'] else compute())
    refresh_score_defaults()
    ui.timer(0.1, compute, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Reuses _compatibility_match_locked(),
    _match_title_html() and _match_table_only_html() (the SAME functions this page's own
    show_match()/compute() call),
    draws EVERY matching partner found directly into `container` (no live widgets of this page are
    read).
    This has NO sub_options for v1 (sub_option_value is unused) - it reproduces exactly the live
    page's OWN default behavior: the entered birth details' own nakshatra/paadham (computed here via
    drik.nakshatra(), same as the live page's compute() does on a birth-detail change) as the star
    side matching Gender's own value (read from the SAME shared state print_registry.py's dialog
    already used for birth details - NOT a selector local to this page, mirroring how the live page
    itself treats Gender as a shared, top-level field). The default minimum-score/porutham-checkbox
    settings (mahendra/vedha/rajju/sthree all False, score default per chart style) are also used,
    same as what a visitor sees on first loading this page before touching any control.
    """
    try:
        south = _south_style()
        with calc_lock():
            mins = const.compatibility_minimum_score_south if south else const.compatibility_minimum_score_north
            jd = utils.julian_day_number(drik.Date(*dob), tob)
            place = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
            nak = drik.nakshatra(jd, place)
        state = ensure_default_state()
        gender_value = state.get('gender', int(const.GENDER.FEMALE))
        if not isinstance(gender_value, int):
            gender_value = int(const.GENDER.FEMALE)
        style_key = list(const.AVAILABLE_CHART_STYLES.keys())[0]
        try:
            raw = state.get('kundali_chart_style')
            if raw:
                style_key = getattr(const.CHART_STYLE, raw, style_key)
        except Exception:
            pass
        nakshatra_number, paadha_number = int(nak[0]), int(nak[1])
        bn = bp = gn = gp = None
        if gender_value == 0:
            bn, bp = nakshatra_number, paadha_number
        else:
            gn, gp = nakshatra_number, paadha_number
        matches = await run_io_bound_ctx(_compatibility_match_locked, bn, bp, gn, gp, False, False, False, False,
                                     float(mins), style_key)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Compatibility: {e}</i>")
        return
    with container:
        ui.label(res_str('compatibility_str', 'Compatibility')).classes('text-base font-bold text-green-700 print-attach-next')
        if not matches:
            ui.html(f"<i>{res_str('no_matching_found_str', 'No matching found')}</i>")
            return
        # Grouped 3-per-row, same as render_print_content()'s own live-page print view - see that
        # function's own docstring for the full reasoning (reuses '.print-side-by-side', the same
        # class already proven working for other multi-table pages).
        for row_start in range(0, len(matches), _MATCHES_PER_PRINT_ROW):
            row_matches = matches[row_start:row_start + _MATCHES_PER_PRINT_ROW]
            with ui.row().classes('w-full gap-3 items-start flex-wrap print-side-by-side'):
                for m in row_matches:
                    with ui.column().classes('gap-1 min-w-72'):
                        ui.html(_match_title_html(m)).classes('print-attach-next')
                        ui.html(_match_table_only_html(m, south))
print_registry.register('compatibility', 'Compatibility', 'Compatibility', _build_print_section)
