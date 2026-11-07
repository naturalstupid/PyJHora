#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Chart menu: web equivalent of the PyQt desktop app's right-click menu on a chart.

The desktop app (horo_chart_tabs.py, ChartTabbed._get_menu_dicts) builds ONE nested dict, the chart's context
menu, and merges the dicts of every feature into it. This module rebuilds the same tree and offers it as
combo boxes beside the chart instead of a right-click menu (which has no touch equivalent):

  * Combo 1 lists the top-level entries, in the desktop's order, with the desktop's own labels. Every label is
    a resource string (res_str of the same key horo_chart_tabs.py uses) or, for the entries the library builds
    itself (Varnada Lagna, Chara Karakas, Special Lagnas, Special Planets, Sphutas, Sahams, Yogi), the key of
    the dict the library returned - already translated. No label is invented here.
  * An entry whose value is a nested dict is a sub-menu: its children appear in a further combo to the right
    (up to MAX_LEVELS combos) with the first child already selected and shown. Entries without children show no
    further combo.
  * A 12-element list is "show in chart cells": picking it writes it into the chart. Everything else opens a
    popup dialog. The combos always show what the chart shows: after a popup the selection returns to the item
    drawn in the chart (initially the "Planets" entry, which clears the overlay).

Node types of the tree built by build_menu_locked():
    {'t': 'reset'}                          clears the overlay                  (Chart.Action.ResetChartCells)
    {'t': 'overlay', 'data': [12 str]}      draws data in the cells             (Chart.Action.ShowInChartCells)
    {'t': 'menu', 'children': {label: node}}
    {'t': 'popup', 'title': str, 'html': str}   popup with ready content        (Chart.Action.PopupInfo / PopupWidget)
    {'t': 'lazy', 'key': str, 'title': str}     popup whose content is computed only when picked
                                                (the desktop also defers Rasi Entry; Drishti, Aspect and the planet
                                                speed table are costly and rarely looked at)

Entries the desktop leaves out when they have nothing to show (Paachakaadi, Brahma, Pushkara, Combustion, Graha
Yudh, Mrityu Bhaga, Marana Karaka Sthana) are left out here too, which is why the whole tree is computed in one go
after the chart (build_menu_locked) rather than on demand.

Prasna Lagna (horary) is the one entry that needs input: its node ({'t': 'prasna'}) opens PrasnaDialog - the web
version of the desktop's PrasnaDialog: a random-number check box, the method (Prasna Lagna-108, Prasna Lagna KP-249 or
Naadi-1800), the number (1..108 / 1..249 / 1..1800) and "keep" or "replace" the lagna. Its key is, as on the desktop,
res_str('prasna_lagna_str') + '(' + res_str('prasna_lagna_short_str') + ')'. On Accept the Prasna Lagna rasi is worked
out by utils.get_prasna_lagna_*_for_varga_chart() and either
  * "keep": the Prasna Lagna short label is drawn in that rasi's cell as an overlay (the chart is unchanged), or
  * "replace": the ascendant is moved there - chart_with_prasna() removes the ascendant from its own cell and writes
    "<ascendant_str>(<prasna_lagna_short_str>)" in the Prasna Lagna cell (the desktop's label), which also becomes
    the ascendant house.
Unlike the desktop, the chart is never edited in place: the page keeps the real chart and derives the replaced one when
it draws, so choosing any other menu entry (or Planets) simply stops deriving it and nothing has to be backed up.
"""
import asyncio
import contextlib
import contextvars
import html as html_lib
import random
import re
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope.chart import charts, house, strength
from components import calc_lock, res_str, safe_notify, DelayedBusyIndicator

drik = utils.hora_engine_proxy

MAX_LEVELS = 4  # number of cascading combos; deeper nesting is flattened into 'a > b' labels
OVERLAY_TABLE_MIN_LINES = 4   # any house with this many lines or more -> show as a table

def overlay_too_crowded(overlay):
    """True if any house of the 12-list overlay has OVERLAY_TABLE_MIN_LINES or more lines."""
    return any(len(str(x).split('\n')) >= OVERLAY_TABLE_MIN_LINES for x in (overlay or []) if str(x).strip())

def overlay_side_table_html(overlay, heading=None):
    """Rasi | Details table of a 12-list overlay, all 12 signs, Aries first; codes joined with commas."""
    th = 'border:1px solid #5c3a21;padding:3px 8px;background:#f0fdf4;text-align:left;'
    td = 'border:1px solid #d1d5db;padding:3px 8px;vertical-align:top;'
    out = ["<table style='border-collapse:collapse;font-size:12px;max-width:300px;'>",
           f"<tr><th style='{th}'>{_esc(res_str('raasi_str', 'Raasi'))}</th>"
           f"<th style='{th}'>{_esc(heading if heading is not None else res_str('details_str', 'Details'))}</th></tr>"]
    for i in range(12):
        text = ', '.join(p for p in str(overlay[i] or '').split('\n') if p.strip())
        out.append(f"<tr><td style='{td}white-space:nowrap;'>{_esc(utils.RAASI_LIST[i])}</td>"
                   f"<td style='{td}'>{_esc(text)}</td></tr>")
    out.append('</table>')
    return ''.join(out)

def _esc(text):
    """HTML-escapes any value for display."""
    return html_lib.escape(str(text))


def _lines_html(lines):
    """Joins already-escaped lines with <br>."""
    return '<br>'.join(lines)


def _table_html(headers, rows, header_bg='#f0fdf4', font_size='12px'):
    """Returns an HTML table (cell values are escaped here).

    Args:
        headers: list of column heading texts, or None for no heading row.
        rows: list of rows; each row is a list of cell values.
        header_bg: background color of the heading row.
        font_size: CSS font size.
    """
    th = f'border:1px solid #5c3a21;padding:4px 8px;background:{header_bg};text-align:left;white-space:nowrap;'
    td = 'border:1px solid #d1d5db;padding:4px 8px;white-space:nowrap;'
    out = [f"<table style='border-collapse:collapse;font-size:{font_size};'>"]
    if headers:
        out.append('<tr>' + ''.join(f"<th style='{th}'>{_esc(h)}</th>" for h in headers) + '</tr>')
    for row in rows:
        out.append('<tr>' + ''.join(f"<td style='{td}'>{_esc(c)}</td>" for c in row) + '</tr>')
    out.append('</table>')
    return ''.join(out)


def _none_found():
    """Returns the HTML shown when a popup has nothing to report for this chart."""
    return f"<i>{_esc(res_str('no_results_str', 'Nothing found for this chart.'))}</i>"


def _convert_chart_to_indices(chart_1d):
    """Replaces localized planet names (and the ascendant label) in a 12-house chart by planet indices and drops
    stationary/retrograde marks - the form house.raasi_drishti_from_chart() etc. expect. Same conversion as
    drishti_tab.py / horo_chart_tabs.py _convert_language_chart_to_indices().
    """
    out = list(chart_1d)
    local = utils.PLANET_NAMES + [res_str('ascendant_str', 'Ascendant')]
    english = ['Sun   ', 'Moon   ', 'Mars   ', 'Mercury   ', 'Jupiter   ', 'Venus   ', 'Saturn   ',
               'Raagu   ', 'Kethu   ', 'Uranus', 'Neptune', 'Pluto', 'Lagnam']
    values = [str(i) for i in range(12)] + [const._ascendant_symbol]
    for src, dst in zip(local, english):
        out = [x.replace(src, dst) for x in out]
    for src, dst in zip(english, values):
        out = [x.replace(src, dst).replace(const._stationary_symbol, '').replace(const._retrogade_symbol, '')
               for x in out]
    return out


def style_supports_menu(chart_style):
    """Returns False for the chart styles the chart menu is not offered for: Sudarsana Chakra (concentric rings, not
    the 12 house cells the overlays are written into) and Western (a wheel, drawn by a different renderer). A page
    hides the menu combos for them with ChartMenu.set_hidden().

    Args:
        chart_style: const.CHART_STYLE value of the displayed chart.
    """
    unsupported = {getattr(const.CHART_STYLE, name, None) for name in ('SUDARSANA_CHAKRA', 'WESTERN')}
    unsupported.discard(None)
    return chart_style not in unsupported


# ---------------------------------------------------------------------------------------------------------
# Tree nodes
# ---------------------------------------------------------------------------------------------------------
def _reset():
    return {'t': 'reset'}


def _overlay(data):
    return {'t': 'overlay', 'data': list(data)}


def _menu(children):
    return {'t': 'menu', 'children': children}


def _popup(title, html):
    return {'t': 'popup', 'title': title, 'html': html}


def _lazy(key, title):
    return {'t': 'lazy', 'key': key, 'title': title}


def _to_node(value):
    """Converts a value of a library menu dict into a node, as the desktop's _wrap_chart_cell_menu_actions() does:
    a dict is a sub-menu, a 12-element list is an overlay for the chart cells. Anything else is not a menu item
    (None when the result would be an empty sub-menu).
    """
    if isinstance(value, dict):
        children = _nodes_from(value)
        return _menu(children) if children else None
    if isinstance(value, (list, tuple)) and len(value) == 12 and not isinstance(value, str):
        return _overlay([str(x) if x is not None else '' for x in value])
    return None


def _nodes_from(menu_dict):
    """Returns {label: node} for every usable entry of a library menu dict (empty for anything else)."""
    nodes = {}
    if isinstance(menu_dict, dict):
        for label, value in menu_dict.items():
            node = _to_node(value)
            if node is not None:
                nodes[str(label)] = node
    return nodes


def _flatten_leaves(children, prefix):
    """Flattens nested sub-menus into {'prefix > a > b': leaf} (used only past MAX_LEVELS)."""
    flat = {}
    for label, node in children.items():
        name = f'{prefix} > {label}'
        if node['t'] == 'menu':
            flat.update(_flatten_leaves(node['children'], name))
        else:
            flat[name] = node
    return flat


def _cap_depth(children, depth):
    """Returns `children` (shown in combo number `depth`, 0-based) with sub-menus that would need more than
    MAX_LEVELS combos flattened into joined labels."""
    out = {}
    for label, node in children.items():
        if node['t'] == 'menu':
            if depth + 1 >= MAX_LEVELS:
                out.update(_flatten_leaves(node['children'], label))
            else:
                out[label] = _menu(_cap_depth(node['children'], depth + 1))
        else:
            out[label] = node
    return out


# ---------------------------------------------------------------------------------------------------------
# Prasna Lagna
# ---------------------------------------------------------------------------------------------------------
# method key -> (highest number, function of jhora.utils that returns the Prasna Lagna rasi index 0..11)
PRASNA_METHODS = {
    '108': (108, 'get_prasna_lagna_108_for_varga_chart'),
    'kp249': (249, 'get_prasna_lagna_KP_249_for_varga_chart'),
    'nadi1800': (1800, 'get_prasna_lagna_nadi_for_varga_chart'),
}


def prasna_key():
    """Returns the menu label of the Prasna Lagna entry: the desktop's res_str('prasna_lagna_str') + '(' +
    res_str('prasna_lagna_short_str') + ')'."""
    return res_str('prasna_lagna_str', 'Prasna Lagna') + '(' + res_str('prasna_lagna_short_str', 'PrL') + ')'


def prasna_marker_overlay(rasi):
    """Returns the 12-list overlay that shows the Prasna Lagna in the chart cells: the short Prasna Lagna label in
    the cell of absolute rasi index `rasi`, empty elsewhere."""
    overlay = [''] * 12
    overlay[rasi] = res_str('prasna_lagna_short_str', 'PrL')
    return overlay


def _ascendant_names():
    """Returns the language strings that stand for the ascendant in a chart cell, longest first: ascendant_str (e.g.
    "Ascendant" + its symbol) and ascendant_short_str. The desktop's replace_ascendant_with_prasna_lagna() removes
    ascendant_str from every cell by plain text replacement; both forms are accepted here because the web chart shows
    either, depending on how a cell was built."""
    names = {res_str('ascendant_str', 'Ascendant').strip(), res_str('ascendant_short_str', 'Asc').strip()}
    names.discard('')
    return sorted(names, key=len, reverse=True)


def _ascendant_glyph():
    """Returns the symbol that ends ascendant_str (e.g. the script L), or '' if it has none. Only a character from
    the symbol blocks (code point 0x2000 and above) counts: letters of the Indian scripts are below that, so a
    language whose ascendant_str ends in a letter never matches ordinary text by accident."""
    text = res_str('ascendant_str', 'Ascendant').strip()
    return text[-1] if text and ord(text[-1]) >= 0x2000 else ''


def _cell_tokens(raw):
    """Splits one chart cell into its tokens. Cells are '/'-joined, but the library also puts a line break between
    the planets of a house, so both separate tokens."""
    return [t.strip() for t in re.split(r'[/\n]', raw or '') if t.strip()]


def _without_ascendant(token, names, glyph):
    """Returns `token` with the ascendant taken out ('' if nothing else is left), and whether it had one.

    The ascendant is recognised (1) as the plain symbol const._ascendant_symbol (the token form some charts use),
    (2) as ascendant_str / ascendant_short_str - removed as text, like the desktop does, so any remainder stays - and,
    failing both, (3) as any token carrying the ascendant's own symbol, which no planet has."""
    if token == const._ascendant_symbol:
        return '', True
    for name in names:
        if len(name) >= 2 and name in token:
            return token.replace(name, '').strip(), True
        if token == name:
            return '', True
    if glyph and glyph in token:
        return '', True
    return token, False


def chart_with_prasna(chart_1d, asc_house, prasna_rasi):
    """Returns (chart_1d, asc_house) of the chart with its ascendant replaced by the Prasna Lagna.

    The ascendant is removed from every house, and the label ascendant_str + "(" + prasna_lagna_short_str + ")" (the
    desktop's new_lagna) is written first in the cell of `prasna_rasi`, followed by that cell's own planets. The Prasna
    Lagna rasi becomes the ascendant house. The arguments are not modified. If no ascendant can be found in any cell
    the chart is still drawn with the label in the Prasna cell, and the console shows the cells and what was looked for,
    so the format can be corrected.

    Args:
        chart_1d: 12 house strings indexed by absolute rasi; see _cell_tokens() for the separators.
        asc_house: absolute rasi index of the real ascendant, used only in the console message.
        prasna_rasi: absolute rasi index (0 = Aries) of the Prasna Lagna.
    """
    names, glyph = _ascendant_names(), _ascendant_glyph()
    label = (res_str('ascendant_str', 'Ascendant') + '(' + res_str('prasna_lagna_short_str', 'PrL') + ')').replace('/', '')
    cells, removed = [], 0
    for raw in chart_1d:
        tokens = []
        for token in _cell_tokens(raw):
            rest, was_ascendant = _without_ascendant(token, names, glyph)
            removed += was_ascendant
            if rest:
                tokens.append(rest)
        cells.append(tokens)
    if removed == 0:
        print('[chart_details] chart_with_prasna: no ascendant found in the chart cells, so the original ascendant is left '
              f'where it is. Looked for: the symbol {const._ascendant_symbol!r}, the names {names!r} and the glyph '
              f'{glyph!r}. The real ascendant house is {asc_house!r}; the cells are {list(chart_1d)!r}')
    cells[prasna_rasi].insert(0, label)
    return ['/'.join(tokens) for tokens in cells], prasna_rasi


def compute_prasna_locked(method, number, dcf):
    """Returns the Prasna Lagna rasi index (0 = Aries .. 11) for a method and a number. Blocking; takes calc_lock().

    Args:
        method: a key of PRASNA_METHODS ('108', 'kp249' or 'nadi1800').
        number: the Prasna number, 1 .. the method's highest number.
        dcf: divisional chart factor of the displayed chart (the rasi is given for that varga).

    Raises:
        ValueError: if the method or number is invalid, or the library does not return a rasi 0..11.
    """
    if method not in PRASNA_METHODS:
        raise ValueError(f'unknown Prasna Lagna method: {method}')
    highest, func_name = PRASNA_METHODS[method]
    number = int(number)
    if not 1 <= number <= highest:
        raise ValueError(f'the Prasna number must be 1..{highest}')
    with calc_lock():
        rasi = getattr(utils, func_name)(number, dcf)
    if not isinstance(rasi, int) or isinstance(rasi, bool) or not 0 <= rasi <= 11:
        raise ValueError(f'unexpected Prasna Lagna result: {rasi!r}')
    return rasi


# ---------------------------------------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------------------------------------
def make_context(horo, dob, tob, varga_idx, dcf, chart_method, chart_style, correction=0.0):
    """Returns the context dict that build_menu_locked() and compute_lazy_locked() work from.

    Args:
        horo: the horo_info.Horoscope object of the displayed chart.
        dob: (year, month, day) of the moment the chart is cast for.
        tob: (hour, minute, second) of the moment the chart is cast for.
        varga_idx: index of the displayed divisional chart in const.division_chart_factors.
        dcf: divisional chart factor of the displayed chart.
        chart_method: calculation method (1-based) of the displayed chart.
        chart_style: const.CHART_STYLE value of the displayed chart.
        correction: dhasa progression correction (degrees) added to all longitudes of the displayed chart
            (the Transit page's nakshathra dhasa progression); 0.0 for every other chart. The menu is built from
            the same corrected positions as the chart, as the desktop app's _get_menu_dicts() does.
    """
    return {'horo': horo, 'dob': tuple(dob), 'tob': tuple(tob), 'varga_idx': varga_idx, 'dcf': dcf,
            'chart_method': chart_method, 'chart_style': chart_style, 'correction': float(correction or 0.0)}


def _positions(ctx, jd, place):
    """Returns the planet positions of the displayed chart including the non-planets (ascendant, upagrahas...)."""
    return charts.divisional_chart(
        jd, place, divisional_chart_factor=ctx['dcf'], chart_method=ctx['chart_method'],
        base_rasi=None, count_from_end_of_sign=None, dhasa_progression_correction=ctx.get('correction', 0.0),
        exclude_non_planets=False)


def _pp_count():
    """Number of leading entries of the planet positions that are planets (Sun..Ketu, or ..Pluto)."""
    return const._pp_count_upto_pluto if const._INCLUDE_URANUS_TO_PLUTO else const._pp_count_upto_ketu


# ---------------------------------------------------------------------------------------------------------
# Menu entries. Each _e_* returns {label: node} (possibly empty) and mirrors the matching block of the desktop's
# _get_menu_dicts(); the labels are built from the same resource keys.
# ---------------------------------------------------------------------------------------------------------
def _e_planets(ctx, horo, jd, place, pp, pp_dict):
    return {res_str('planets_str', 'Planets'): _reset()}


def _e_arudhas(ctx, horo, jd, place, pp, pp_dict):
    menu = getattr(horo, '_arudha_menu_dict', None)
    if not menu:
        # The chart computation did not populate it; ask the horoscope object for it, as the desktop app's
        # compute_horoscope() does (Rasi chart arudha padhas).
        try:
            horo._get_arudha_padhas(horo.Date, horo.birth_time, place, divisional_chart_factor=1,
                                    years=1, months=1, sixty_hours=1,
                                    dhasa_progression_correction=ctx.get('correction', 0.0))
            menu = getattr(horo, '_arudha_menu_dict', None)
        except Exception as e:
            print(f'[chart_details] arudha padhas not available: {e}')
            menu = None
    children = _nodes_from(menu)
    return {res_str('arudhas_str', 'Arudhas'): _menu(children)} if children else {}


def _e_varnada(ctx, horo, jd, place, pp, pp_dict):
    return _nodes_from(horo.get_varnada_lagna_from_positions(pp_dict))


def _e_karakas(ctx, horo, jd, place, pp, pp_dict):
    return _nodes_from(horo.get_chara_karakas_for_chart(pp))


def _e_special_lagnas(ctx, horo, jd, place, pp, pp_dict):
    return _nodes_from(horo.get_special_lagnas_from_positions(pp_dict))


def _e_special_planets(ctx, horo, jd, place, pp, pp_dict):
    menu, _ = horo.get_special_planets_from_positions(pp_dict)
    return _nodes_from(menu)


def _e_sphutas(ctx, horo, jd, place, pp, pp_dict):
    return _nodes_from(horo.get_sphutas_from_positions(pp_dict))


def _e_prasna(ctx, horo, jd, place, pp, pp_dict):
    return {prasna_key(): {'t': 'prasna'}}


def _e_sahams(ctx, horo, jd, place, pp, pp_dict):
    menu, _ = horo.get_sahams(
        jd, place, divisional_chart_factor=ctx['dcf'], chart_method=ctx['chart_method'],
        base_rasi=None, count_from_end_of_sign=None,
        dhasa_progression_correction=ctx.get('correction', 0.0))
    return _nodes_from(menu)


def _e_paachakaadi(ctx, horo, jd, place, pp, pp_dict):
    data = charts.get_pachakadi_sambhandha(pp[:const._pp_count_upto_ketu])
    names = [res_str(pr + '_str', pr) for pr in const.paachaadi_relations]
    lines = []
    for planet1, (index, (planet2, h, enemy)) in data.items():
        enemy_str = res_str('inimical_str', 'Inimical') if enemy == 'E' else ''
        lines.append(' '.join(x for x in [
            _esc(utils.PLANET_NAMES[planet2]), _esc(enemy_str), _esc(names[index]),
            _esc(utils.PLANET_NAMES[planet1]), _esc(res_str('house_str', 'House') + '-' + str(h))] if x))
    if not lines:
        return {}
    key = res_str('paachakaadi_sambhandha_str', 'Paachakaadi Sambhandha')
    return {key: _popup(key, _lines_html(lines))}


def _e_brahma(ctx, horo, jd, place, pp, pp_dict):
    positions = pp[:_pp_count()]
    brahma = house.brahma(positions)
    rudra = house.rudra(positions)
    maheshwara = house.maheshwara_from_planet_positions(positions)
    if brahma is None or rudra is None or maheshwara is None:
        return {}
    key = res_str('brahma_str', 'Brahma') + ',' + res_str('rudra_str', 'Rudra') + ',' + \
        res_str('maheshwara_str', 'Maheshwara')
    raasi = res_str('raasi_str', 'Raasi')
    lines = [
        f"{_esc(res_str('brahma_str', 'Brahma'))}:{_esc(utils.PLANET_NAMES[brahma])}",
        f"{_esc(res_str('rudra_str', 'Rudra'))}:{_esc(utils.PLANET_NAMES[rudra[0]])} "
        f"{_esc(raasi)}:{_esc(utils.RAASI_LIST[rudra[1]])}",
        f"{_esc(res_str('trishoola_str', 'Trishoola'))} {_esc(raasi)}:"
        f"{_esc(','.join(utils.RAASI_LIST[r] for r in rudra[2]))}",
        f"{_esc(res_str('maheshwara_str', 'Maheshwara'))}:{_esc(utils.PLANET_NAMES[maheshwara])}",
    ]
    return {key: _popup(key, _lines_html(lines))}


def _e_drishti(ctx, horo, jd, place, pp, pp_dict):
    title = res_str('raasi_str', 'Raasi') + '-' + res_str('graha_str', 'Graha') + '-' + res_str('drishti_str', 'Drishti')
    return {res_str('drishti_str', 'Drishti'): _lazy('drishti', title)}


def _e_yogi(ctx, horo, jd, place, pp, pp_dict):
    info = horo.get_ava_saha_yoga_info_for_chart(pp_dict)
    if not info:
        return {}
    key, text = list(info.items())[0]
    text = re.sub(r'(?i)<br\s*/?>|&lt;br\s*/?&gt;', '\n', str(text))
    return {str(key): _popup(str(key), _esc(text).replace('\n', '<br>'))}


def _e_planet_info(ctx, horo, jd, place, pp, pp_dict):
    if not utils.astro_engine_is_drik():
        return {}
    key = (res_str('planets_str', 'Planets') + ' ' + res_str('speed_str', 'Speed') + ', ' +
           res_str('distance_str', 'Distance') + ' ' + res_str('information_str', 'Information'))
    return {key: _lazy('planet_info', key)}


def _e_pushkara(ctx, horo, jd, place, pp, pp_dict):
    pa, pb = charts.planets_in_pushkara_navamsa_bhaga(pp)
    lines = []
    if len(pa) > 0:
        lines.append(f"{_esc(res_str('pushkara_amsa_str', 'Pushkara Amsa'))} "
                     f"{_esc(res_str('planets_str', 'Planets'))}:")
        lines += [_esc(utils.PLANET_NAMES[p]) for p in pa]
    if len(pb) > 0:
        if lines:
            lines.append('')
        lines.append(f"{_esc(res_str('pushkara_bhaga_str', 'Pushkara Bhaga'))} "
                     f"{_esc(res_str('planets_str', 'Planets'))}:")
        lines += [_esc(utils.PLANET_NAMES[p]) for p in pb]
    if not lines:
        return {}
    key = res_str('pushkara_amsa_str', 'Pushkara Amsa') + ', ' + res_str('pushkara_bhaga_str', 'Pushkara Bhaga')
    return {key: _popup(key, _lines_html(lines))}


def _e_combustion(ctx, horo, jd, place, pp, pp_dict):
    planets = charts.planets_in_combustion(pp)
    if not planets:
        return {}
    key = res_str('combustion_str', 'Combustion') + ' ' + res_str('planets_str', 'Planets')
    return {key: _popup(key, _lines_html([_esc(key)] + [_esc(utils.PLANET_NAMES[p]) for p in planets]))}


def _e_graha_yudh(ctx, horo, jd, place, pp, pp_dict):
    if ctx['varga_idx'] != 0 or not utils.astro_engine_is_drik():
        return {}
    yudh = drik.planets_in_graha_yudh(jd, place)
    if not yudh:
        return {}
    types = [res_str(gy + '_str', gy) for gy in ('bhed_yuti', 'ullekh_yuti', 'apasavya_yuti', 'anshumardan_yuti')]
    lines = [_esc(res_str('graha_yudh_str', 'Graha Yudh') + ' ' + res_str('planets_str', 'Planets') + ' :')]
    lines += [f'{_esc(utils.PLANET_NAMES[p1])} {_esc(types[t])} {_esc(utils.PLANET_NAMES[p2])}' for p1, p2, t in yudh]
    key = res_str('graha_yudh_str', 'Graha Yudh')
    return {key: _popup(key, _lines_html(lines))}


def _e_mrityu(ctx, horo, jd, place, pp, pp_dict):
    y, m, d, fh = utils.jd_to_gregorian(jd)
    planets = charts.planets_in_mrityu_bhaga(drik.Date(y, m, d), (fh, 0, 0), place, pp)
    if not planets:
        return {}
    lines = [_esc(res_str('mrityu_bhaga_str', 'Mrityu Bhaga') + ' ' + res_str('planets_str', 'Planets') + ' :')]
    for p, r, l in planets:
        if isinstance(p, int):
            name = utils.PLANET_NAMES[p]
        else:
            name = res_str('ascendant_str', 'Ascendant') if p == 'L' else res_str('maandi_str', 'Maandi')
        lines.append(f"{_esc(name)} {_esc(utils.RAASI_LIST[r])} {_esc(res_str('balance_str', 'Balance'))} : "
                     f"{_esc(utils.to_dms(l, is_lat_long='plong'))}")
    key = res_str('mrityu_bhaga_str', 'Mrityu Bhaga')
    return {key: _popup(key, _lines_html(lines))}


def _e_aspect(ctx, horo, jd, place, pp, pp_dict):
    key = res_str('planet_aspects_relations_str', 'Planet Aspects / Relations')
    return {key: _lazy('aspect', key)}


def _e_mks(ctx, horo, jd, place, pp, pp_dict):
    planets = charts.get_planets_in_marana_karaka_sthana(pp, consider_ketu_4th_house=True)
    if not planets:
        return {}
    key = res_str('marana_karaka_sthana_str', 'Marana Karaka Sthana') + ' ' + res_str('planets_str', 'Planets')
    lines = [_esc(key)] + [f"{_esc(utils.PLANET_NAMES[p])} {_esc(res_str('house_str', 'House'))}-{h}" for p, h in planets]
    return {key: _popup(key, _lines_html(lines))}


def _e_rasi_entry(ctx, horo, jd, place, pp, pp_dict):
    key = res_str('raasi_str', 'Raasi') + ' ' + res_str('entry_str', 'Entry')
    return {key: _lazy('rasi_entry', key)}


def _e_lattha(ctx, horo, jd, place, pp, pp_dict):
    key = res_str('lattha_star_str', 'Lattha Star')
    stars = [utils.NAKSHATRA_LIST[s] for s in const.abhijit_order_of_stars]
    rows = []
    for p, (p_star, l_star) in enumerate(charts.lattha_stars_planets(pp)):
        rows.append([utils.PLANET_NAMES[p], utils.NAKSHATRA_LIST[p_star - 1], stars[l_star - 1]])
    return {key: _popup(key, _table_html([res_str('planet_str', 'Planet'), res_str('nakshatra_str', 'Nakshatra'), key],
                                         rows))}


def _lord_table(data):
    """Table of {planet -> (raasi index, lord index)} as used by the 22nd Drekkana / 64th Navamsa lords."""
    headers = [res_str('planet_str', 'Planet'), res_str('raasi_str', 'Raasi'), res_str('lord_str', 'Lord')]
    rows = []
    for p, (v1, v2) in data.items():
        name = res_str('ascendant_str', 'Ascendant') if p == const._ascendant_symbol else utils.PLANET_NAMES[p]
        rows.append([name, utils.RAASI_LIST[v1], utils.PLANET_NAMES[v2]])
    return _table_html(headers, rows)


def _e_ndl(ctx, horo, jd, place, pp, pp_dict):
    dcf = ctx['dcf']
    if dcf == 3:
        key = '22nd ' + res_str('drekkanam_str', 'Drekkana').replace(' (D3)', '')
        data = charts.get_22nd_drekkana(pp[:const._pp_count_upto_ketu])
    elif dcf == 9:
        key = '64th ' + res_str('navamsam_str', 'Navamsa').replace(' (D9)', '')
        data = charts.get_64th_navamsa(pp[:const._pp_count_upto_ketu])
    else:
        return {}
    method = res_str('d' + str(dcf) + '_option' + str(ctx['chart_method']) + '_str', '')
    body = _lord_table(data) + (f'<br><b>{_esc(method)}</b>' if method else '')
    return {key: _popup(key, body)}


def _e_graha_drekkana(ctx, horo, jd, place, pp, pp_dict):
    if ctx['varga_idx'] != 0:
        return {}
    key = res_str('planet_str', 'Planet') + ' ' + res_str('drekkanam_str', 'Drekkana').replace(' (D3)', '')
    rows = []
    for p, gpt in enumerate(drik.graha_drekkana(jd, place)):
        rows.append([utils.PLANET_NAMES[p], '' if gpt == 0 else res_str(const.graha_drekkana_types[gpt] + '_str',
                                                                          const.graha_drekkana_types[gpt])])
    return {key: _popup(key, _table_html([res_str('planet_str', 'Planet'), key], rows))}


def _e_nava_thaara(ctx, horo, jd, place, pp, pp_dict):
    key = res_str('nava_thaara_str', 'Nava Thaara')
    navas = ['janma_str', 'sampatha_str', 'vipatha_str', 'kshema_str', 'prathyaka_str', 'saadhana_str',
             'naidhana_str', 'mithra_str', 'paramithra_str']
    all_ntl = charts.nava_thaara_for_all_planets(pp)
    bases = [('L', res_str('ascendant_str', 'Ascendant'))] + [(p, utils.PLANET_NAMES[p]) for p in const.SUN_TO_KETU]
    children = {}
    for base, base_name in bases:
        rows = []
        for n, (lord, star_list) in enumerate(all_ntl[base]):
            rows.append([res_str(navas[n], navas[n]), utils.PLANET_NAMES[lord],
                         ', '.join(utils.NAKSHATRA_LIST[s] for s in star_list)])
        title = f'{key} ({base_name})'
        children[base_name] = _popup(title, _table_html(
            [key, res_str('lord_str', 'Lord'), res_str('nakshatra_str', 'Nakshatra')], rows))
    return {key: _menu(children)}


def _e_special_thaara(ctx, horo, jd, place, pp, pp_dict):
    key = res_str('special_thaara_str', 'Special Thaara')
    star_list = (utils.get_nakshathra_list_with_abhijith() if const.include_abhijith_in_special_thaara_calculation
                 else utils.NAKSHATRA_LIST)
    all_ntl = charts.special_thaara_for_all_planets(pp)
    bases = [('L', res_str('ascendant_str', 'Ascendant'))] + [(p, utils.PLANET_NAMES[p]) for p in range(9)]
    children = {}
    for base, base_name in bases:
        rows = []
        for s, (lord, star) in enumerate(all_ntl[base]):
            rows.append([res_str(const.special_thaara_names[s], const.special_thaara_names[s]),
                         utils.PLANET_NAMES[lord], star_list[star]])
        title = f'{key} ({base_name})'
        children[base_name] = _popup(title, _table_html(
            [key, res_str('lord_str', 'Lord'), res_str('nakshatra_str', 'Nakshatra')], rows))
    return {key: _menu(children)}


# The desktop's merge order (see _special_menu_dict_1d_chart). Later entries replace earlier ones of the same label.
_ENTRIES = [
    ('planets', _e_planets), ('arudhas', _e_arudhas), ('varnada', _e_varnada), ('karakas', _e_karakas),
    ('special_lagnas', _e_special_lagnas), ('special_planets', _e_special_planets), ('sphutas', _e_sphutas),
    ('prasna', _e_prasna), ('sahams', _e_sahams), ('paachakaadi', _e_paachakaadi), ('brahma', _e_brahma), ('drishti', _e_drishti),
    ('yogi', _e_yogi), ('planet_info', _e_planet_info), ('pushkara', _e_pushkara), ('combustion', _e_combustion),
    ('graha_yudh', _e_graha_yudh), ('mrityu', _e_mrityu), ('aspect', _e_aspect), ('mks', _e_mks),
    ('rasi_entry', _e_rasi_entry), ('lattha', _e_lattha), ('ndl', _e_ndl), ('graha_drekkana', _e_graha_drekkana),
    ('nava_thaara', _e_nava_thaara), ('special_thaara', _e_special_thaara),
]


def build_menu_locked(ctx):
    """Builds the chart menu tree {label: node} for the displayed chart (see the module docstring).

    Blocking; takes calc_lock() itself, so run it in a worker thread. Each entry is built on its own: one that
    fails is left out (and reported on the console) instead of losing the whole menu.
    """
    with calc_lock():
        horo = ctx['horo']
        place = horo.Place
        jd = utils.julian_day_number(drik.Date(*ctx['dob']), ctx['tob'])
        pp = _positions(ctx, jd, place)
        pp_dict = {p: (h, lg) for p, (h, lg) in pp}
        menu = {}
        for name, build in _ENTRIES:
            try:
                menu.update(build(ctx, horo, jd, place, pp, pp_dict))
            except Exception as e:
                print(f'[chart_details] menu entry {name} not available: {type(e).__name__}: {e}')
    return _cap_depth(menu, 0)


# ---------------------------------------------------------------------------------------------------------
# Content computed only when picked ('lazy' nodes). Each returns the popup's HTML.
# ---------------------------------------------------------------------------------------------------------
def _h_drishti(ctx, horo, jd, place, pp, pp_dict):
    _, chart_1d, _ = horo.get_horoscope_information_for_chart(
        ctx['varga_idx'], ctx['chart_method'], divisional_chart_factor=ctx['dcf'], base_rasi=None,
        count_from_end_of_sign=None, varnada_method=1,
        dhasa_progression_correction=ctx.get('correction', 0.0))
    chart_ind = _convert_chart_to_indices(chart_1d)
    r_arp, r_ahp, r_app = house.raasi_drishti_from_chart(chart_ind, '\n')
    g_arp, g_ahp, g_app = house.graha_drishti_from_chart(chart_ind, '\n')
    headers = [res_str('planet_str', 'Planet'), res_str('raasis_str', 'Raasis'), res_str('houses_str', 'Houses'),
               res_str('planets_str', 'Planets')]

    def rows_for(arp, ahp, app, count):
        rows = []
        for row in range(count):
            ras = ', '.join(utils.RAASI_LIST[x] for x in arp[row])
            hs = ', '.join(const.houses_str[x - 1] for x in ahp[row])
            pls = ', '.join(utils.PLANET_NAMES[int(x)] for x in app[row] if x != '' and x != const._ascendant_symbol)
            rows.append([utils.PLANET_NAMES[row], ras, hs, pls])
        return rows

    graha = _table_html(headers, rows_for(g_arp, g_ahp, g_app, 7))
    raasi = _table_html(headers, rows_for(r_arp, r_ahp, r_app, 9))
    return (f"<b>{_esc(res_str('graha_str', 'Graha'))} {_esc(res_str('drishti_str', 'Drishti'))}</b><br>{graha}<br><br>"
            f"<b>{_esc(res_str('raasi_str', 'Raasi'))} {_esc(res_str('drishti_str', 'Drishti'))}</b><br>{raasi}")


def _h_planet_info(ctx, horo, jd, place, pp, pp_dict):
    speeds = drik.planets_speed_info(jd, place)
    factors = const.planet_info_round_factors
    L, S = res_str('longitude_str', 'Longitude'), res_str('speed_str', 'Speed')
    headers = [res_str('planet_str', 'Planet'), L, L + ' ' + S, res_str('latitude_str', 'Latitude'),
               res_str('latitude_str', 'Latitude') + ' ' + S, res_str('distance_str', 'Distance'),
               res_str('distance_str', 'Distance') + ' ' + S]
    rows = []
    for p, v in speeds.items():
        v = [round(x, factors[i]) for i, x in enumerate(v)]
        # v = (longitude, latitude, distance, longitude speed, latitude speed, distance speed)
        rows.append([utils.PLANET_NAMES[p], f'{v[0]} deg', f'{v[3]} deg/day', f'{v[1]} deg', f'{v[4]} deg/day',
                     f'{v[2]} AU', f'{v[5]} AU/day'])
    return _table_html(headers, rows)


def _h_aspect(ctx, horo, jd, place, pp, pp_dict):
    """Planet aspect / relationship table (planets and houses vs planets), colored by relationship.
    Ported from horo_chart_tabs.py _get_menu_dicts()."""
    rows = 21  # 9 planets + 12 houses
    values = [[str(e) for e in row] for row in strength.planet_aspect_relationship_table_pvr(pp, include_houses=True)]
    names = [''] + utils.PLANET_SHORT_NAMES[:9] + ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
                                                    '10th', '11th', '12th']
    grid = [names] + [[names[i + 1]] + values[i] for i in range(len(values))]
    crp = const.compound_planet_relations[:]
    hsp = const.house_strengths_of_planets[:]
    header_colors = ['black'] * (rows + 1)
    planet_colors = ['black', 'red', 'orange', 'blue', 'lightgreen', 'darkgreen', 'black']
    rasi_colors = ['red', 'orange', 'cyan', 'blue', 'lightgreen', 'darkgreen']
    cell_colors = [[planet_colors[crp[p1][p2]] if p1 < 9 else rasi_colors[hsp[p2][p1 - 9]] for p1 in range(rows)]
                   for p2 in range(9)]
    colors = [header_colors] + [[header_colors[i + 1]] + cell_colors[i] for i in range(len(cell_colors))]
    grid_t = list(zip(*grid))
    colors_t = list(zip(*colors))
    td = 'border:1px solid #d1d5db;padding:3px 7px;text-align:center;font-weight:bold;'
    out = ["<table style='border-collapse:collapse;font-size:12px;'>"]
    for r in range(len(grid_t)):
        out.append('<tr>' + ''.join(
            f"<td style='{td}color:{colors_t[r][c]};'>{_esc(grid_t[r][c])}</td>" for c in range(len(grid_t[r]))) + '</tr>')
    out.append('</table>')
    legend = [
        [res_str('adhisathru_str', 'Adhisathru') + ' / ' + res_str('neecha_str', 'Neecha'), res_str('sathru_str', 'Sathru'),
         res_str('sama_str', 'Sama')],
        [res_str('sama_str', 'Sama'), res_str('mithra_str', 'Mithra') + ' / ' + res_str('uchcha_str', 'Uchcha'),
         res_str('adhimitra_str', 'Adhimitra') + ' / ' + res_str('swagraha_str', 'Swagraha')],
    ]
    legend_html = ''.join(
        "<div style='display:flex;flex-wrap:wrap;gap:4px 14px;'>" + ''.join(
            f"<span style='font-weight:bold;color:{rasi_colors[r * 3 + c]};'>"
            f"{_esc(rasi_colors[r * 3 + c])}: {_esc(legend[r][c])}</span>"
            for c in range(3)) + '</div>'
        for r in range(2))
    return ''.join(out) + f'<div style="margin-top:6px;">{legend_html}</div>'


def _h_rasi_entry(ctx, horo, jd, place, pp, pp_dict):
    """Next / previous raasi entry date of the ascendant in the displayed chart (the same entries the desktop
    app shows). This is the slow one: it searches for the date."""
    dcf, method = ctx['dcf'], ctx['chart_method']
    pstr = res_str('ascendant_str', 'Ascendant')
    lines = []
    ajd, al = charts.next_planet_entry_date_divisional_chart(
        jd, place, 'L', dcf, direction=1, chart_method=method, base_rasi=None, count_from_end_of_sign=None)
    ay, am, ad, ah = utils.jd_to_gregorian(ajd)
    lines.append(f"{_esc(pstr)} {_esc(res_str('next_str', 'Next'))} {_esc(res_str('raasi_str', 'Raasi'))} "
                 f"({_esc(utils.RAASI_LIST[int(round(al / 30, 0)) % 12])}) {_esc(res_str('entry_str', 'Entry'))} : "
                 f"({ay},{am},{ad}) {_esc(utils.to_dms(ah))}")
    ajd, al = charts.previous_planet_entry_date_divisional_chart(
        jd, place, 'L', dcf, chart_method=method, base_rasi=None, count_from_end_of_sign=None)
    ay, am, ad, ah = utils.jd_to_gregorian(ajd)
    lines.append(f"{_esc(pstr)} {_esc(res_str('previous_str', 'Previous'))} {_esc(res_str('raasi_str', 'Raasi'))} "
                 f"({_esc(utils.RAASI_LIST[int(round(al / 30, 0)) % 12])}) {_esc(res_str('entry_str', 'Entry'))} : "
                 f"({ay},{am},{ad}) {_esc(utils.to_dms(ah))}")
    return _lines_html(lines)


_LAZY = {'drishti': _h_drishti, 'planet_info': _h_planet_info, 'aspect': _h_aspect, 'rasi_entry': _h_rasi_entry}


def compute_lazy_locked(ctx, key):
    """Computes the HTML of a 'lazy' node (see the module docstring). Blocking; takes calc_lock() itself."""
    with calc_lock():
        horo = ctx['horo']
        place = horo.Place
        jd = utils.julian_day_number(drik.Date(*ctx['dob']), ctx['tob'])
        pp = _positions(ctx, jd, place)
        pp_dict = {p: (h, lg) for p, (h, lg) in pp}
        return _LAZY[key](ctx, horo, jd, place, pp, pp_dict)


def overlay_table_html(overlay):
    """Returns an HTML table of a 12-house overlay (rasi name, text), skipping empty houses; used to show what an
    overlay would put into the chart cells for a chart style that cannot draw it (e.g. Sudarsana Chakra)."""
    rows = [[utils.RAASI_LIST[i], overlay[i].replace('\n', ' / ')] for i in range(12) if overlay[i].strip()]
    if not rows:
        return _none_found()
    return _table_html([res_str('raasi_str', 'Raasi'), res_str('details_str', 'Details')], rows)


# ---------------------------------------------------------------------------------------------------------
# UI: the cascading combos and the popup dialog
# ---------------------------------------------------------------------------------------------------------
class PrasnaDialog:
    """The Prasna Lagna options dialog: the web version of the desktop's PrasnaDialog (chart_styles.py).

    Controls, with the desktop's resource keys: a "random number" check box (it fills the number box with a random
    number and locks it); the method - Prasna Lagna-108, Prasna Lagna KP-249 or Naadi-1800 - which sets the range of the
    number (1..108, 1..249, 1..1800; changing the method re-draws the random number if the check box is on); the number;
    and "keep the lagna" / "replace the lagna". Accept and Cancel close it. Defaults, on every opening: random off,
    method 108, number 1, keep the lagna.
    """

    def __init__(self):
        self._on_accept = None
        self._on_cancel = None
        self._done = False
        with ui.dialog() as self._dialog, ui.card().classes('gap-2 min-w-[380px] max-w-[96vw]'):
            self._title = ui.label(res_str('prasna_lagna_str', 'Prasna Lagna') + ' ' + res_str('options_str', 'Options')) \
                .classes('text-lg font-bold text-green-700')
            self._random = ui.checkbox(res_str('random_number_str', 'Random number'), value=False,
                                       on_change=lambda e: self._on_random())
            self._method = ui.radio(
                {'108': res_str('prasna_lagna_str', 'Prasna Lagna') + '-108',
                 'kp249': res_str('prasna_lagna_str', 'Prasna Lagna') + 'KP-249',
                 'nadi1800': res_str('naadi_str', 'Naadi') + '-1800'},
                value='108', on_change=lambda e: self._on_method()).props('inline')
            self._number = ui.number(label='', value=1, min=1, max=108, step=1, format='%.0f').props('outlined dense')
            self._replace = ui.radio(
                {0: res_str('prasna_replace_lagna_label1_str', 'Keep the Lagna'),
                 1: res_str('prasna_replace_lagna_label2_str', 'Replace the Lagna by the Prasna Lagna')}, value=0)
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button(res_str('cancel_str', 'Cancel'), on_click=lambda: self.cancel()).props('outlined dense')
                ui.button(res_str('accept_str', 'Accept'), on_click=lambda: self.accept()).classes('bg-green-600 text-white')
        self._dialog.on('hide', lambda e=None: self._on_hide())

    def _highest(self):
        return PRASNA_METHODS[self._method.value][0]

    def _label(self):
        return res_str('prasna_label_str', 'Prasna Number') + ' (1..' + str(self._highest()) + ')'

    def _refresh_number(self):
        highest = self._highest()
        # min / max must be set as NUMBERS. ui.number compares its value with them when the field loses focus
        # (sanitize()), so props('min=1 max=108') - which stores the STRINGS '1' and '108' - fails there with
        # "'>' not supported between instances of 'str' and 'float'". Use the attributes, never a props string.
        self._number.min = 1
        self._number.max = highest
        self._number._props['label'] = self._label()   # the label may contain any text, so it is not put in a props string
        self._number.update()
        if self._random.value:
            self._number.set_value(random.randint(1, highest))

    def _on_random(self):
        if self._random.value:
            self._number.set_value(random.randint(1, self._highest()))
            self._number.disable()
        else:
            self._number.enable()

    def _on_method(self):
        self._refresh_number()

    def open(self, on_accept, on_cancel):
        """Opens the dialog with its defaults.

        Args:
            on_accept: callable(method, number, replace) called on Accept with a valid number: method is a key of
                PRASNA_METHODS, number an int in range, replace True for "replace the lagna".
            on_cancel: callable() called when the dialog is closed without Accept (Cancel, Escape, click outside).
        """
        self._on_accept, self._on_cancel, self._done = on_accept, on_cancel, False
        self._random.set_value(False)
        self._method.set_value('108')
        self._number.enable()
        self._number.set_value(1)
        self._replace.set_value(0)
        self._refresh_number()
        self._dialog.open()

    def accept(self):
        """Accept: validates the number (a notice and the dialog stays open when it is out of range) and reports."""
        try:
            number = int(self._number.value)
        except (TypeError, ValueError):
            number = None
        if number is None or not 1 <= number <= self._highest():
            safe_notify(self._label(), type='warning')
            return
        self._done = True
        callback = self._on_accept
        self._dialog.close()
        if callback is not None:
            callback(self._method.value, number, bool(self._replace.value))

    def cancel(self):
        """Cancel: closes the dialog without reporting an Accept."""
        self._dialog.close()

    def _on_hide(self):
        """The dialog was closed (by anything): report a cancel unless it was an Accept."""
        if not self._done and self._on_cancel is not None:
            callback, self._on_cancel = self._on_cancel, None
            callback()


class ChartMenu:
    """The chart menu as cascading combo boxes plus a popup dialog.

    Create it inside the container that should hold the combos (a row): it draws MAX_LEVELS selects there, of
    which only the first is visible until a sub-menu entry is picked. Call schedule_rebuild(ctx) after each chart is
    drawn, clear() when the page has no chart, and set_hidden() for a chart style the menu is not offered for.
    """

    def __init__(self, apply_overlay, overlay_supported=lambda: True, apply_prasna=None):
        """
        Args:
            apply_overlay: callable(overlay_or_None) that draws a 12-list in the chart cells (None clears it). It must
                also drop a Prasna Lagna replacement, as every entry other than Prasna Lagna does on the desktop.
            overlay_supported: callable returning False for chart styles that cannot draw an overlay (the item is
                then shown in the popup instead).
            apply_prasna: callable(rasi, replace) that shows a Prasna Lagna: rasi is the absolute rasi index, replace
                True to move the ascendant there (the page then draws chart_with_prasna()), False to draw
                prasna_marker_overlay(rasi) in the cells. None: the page has no Prasna Lagna and the entry is left out.
        """
        self._apply_overlay = apply_overlay
        self._overlay_supported = overlay_supported
        self._apply_prasna = apply_prasna
        self._menu = {}
        self._ctx = None
        self._hidden = False   # True: the combos are not shown at all (see set_hidden())
        self._applied = None   # labels of the item whose overlay is in the chart; None = no overlay
        self._syncing = 0
        self._gen = 0
        self._tasks = set()
        self._levels = []
        for i in range(MAX_LEVELS):
            sel = ui.select({}, value=None, on_change=lambda e, i=i: self._on_level(i, e)) \
                .props('outlined dense').classes('w-52 shrink-0')
            # Picking an entry of the chart menu never needs the chart to be recalculated, so these combos must not
            # highlight the page's Compute button (see calc_highlight.py).
            sel._calc_no_dirty = True
            self._levels.append(sel)
        for sel in self._levels[1:]:
            sel.set_visibility(False)
        self._levels[0].disable()
        self._spinner = ui.spinner(size='sm')
        self._spinner.set_visibility(False)
        with ui.dialog() as self._dialog, ui.card().classes('max-h-[90vh] gap-2 overflow-auto').style(
                'width:max-content !important;max-width:96vw !important;min-width:0;'):
            with ui.row().classes('w-full items-center justify-between flex-nowrap'):
                self._title = ui.label('').classes('text-lg font-bold text-green-700')
                ui.button(icon='close', on_click=self._dialog.close).props('flat round dense')
            self._popup_busy = DelayedBusyIndicator(stop_label=res_str('stop_str', 'Stop'))
            self._body = ui.html('').classes('text-sm overflow-auto').style('width:max-content;max-width:100%;')
        self._prasna_dialog = PrasnaDialog() if apply_prasna is not None else None

    def applied_label(self):
        """Returns the translated text of the deepest combo entry applied to the chart, or an empty string."""
        return str(self._applied[-1]) if self._applied else ''

    def applied_path(self):
        """Returns a copy of the combo path (list of labels) of the entry currently applied to the
        chart's cells (e.g. ['Punya Saham']), or None if nothing is applied (the chart shows
        Planets). Used by a page that wants to re-resolve the same menu selection against a
        DIFFERENT chart (e.g. looping every varga for a multi-page report): the path is just
        labels, so the caller must rebuild that other chart's own menu tree (build_menu_locked())
        and walk the SAME labels through it - the overlay data at the end will differ per chart,
        which is the point.
        """
        return list(self._applied) if self._applied else None

    # -- state helpers ----------------------------------------------------------------------------------
    @contextlib.contextmanager
    def _sync(self):
        """While active, programmatic changes of the combos do not trigger the selection handler."""
        self._syncing += 1
        try:
            yield
        finally:
            self._syncing -= 1

    def _node_at(self, path):
        children = self._menu
        node = None
        for label in path:
            node = children.get(label)
            if node is None:
                return None
            children = node.get('children', {})
        return node

    def _reset_label(self):
        for label, node in self._menu.items():
            if node['t'] == 'reset':
                return label
        return None

    def _set_menu(self, menu):
        if self._apply_prasna is None:
            menu = {k: v for k, v in menu.items() if v.get('t') != 'prasna'}
        self._menu = menu
        self._applied = None
        with self._sync():
            first = self._levels[0]
            if menu:
                first.set_options({k: k for k in menu}, value=self._reset_label())
                first.enable()
            else:
                first.set_options({}, value=None)
                first.disable()
            for sel in self._levels[1:]:
                sel.set_visibility(False)

    def _restore(self):
        """Puts the combos back to the item the chart shows (the Planets entry when no overlay is drawn)."""
        path = self._applied
        with self._sync():
            if not path:
                reset = self._reset_label()
                self._levels[0].set_value(reset)
                for sel in self._levels[1:]:
                    sel.set_visibility(False)
                return
            children = self._menu
            for depth, label in enumerate(path):
                sel = self._levels[depth]
                sel.set_options({k: k for k in children}, value=label)
                sel.set_visibility(True)
                children = children[label].get('children', {})
            for sel in self._levels[len(path):]:
                sel.set_visibility(False)

    # -- building ---------------------------------------------------------------------------------------
    async def rebuild(self, ctx):
        """Rebuilds the menu for a newly drawn chart (see make_context()). The tree is computed in a worker thread;
        meanwhile the combos are empty and a spinner shows if it takes a moment. A newer rebuild() replaces an
        older one that is still running. Does nothing while the menu is hidden (see set_hidden())."""
        if self._hidden:
            return
        self._gen += 1
        gen = self._gen
        self._ctx = ctx
        self._set_menu({})
        reveal = asyncio.ensure_future(self._reveal_spinner(gen))
        menu = {}
        try:
            context = contextvars.copy_context()
            menu = await run.io_bound(context.run, build_menu_locked, ctx)
        except Exception as e:
            print(f'[chart_details] chart menu could not be built: {type(e).__name__}: {e}')
        finally:
            reveal.cancel()
            try:
                self._spinner.set_visibility(False)
            except RuntimeError:
                pass
        if gen != self._gen:
            return  # a newer chart superseded this one
        try:
            self._set_menu(menu)
        except RuntimeError:
            pass  # the page is gone

    def clear(self):
        """Empties the menu (combos blank and disabled) for a page that has no chart to show, and discards any rebuild
        still running, so a stale menu cannot appear afterwards."""
        self._gen += 1
        self._ctx = None
        try:
            self._spinner.set_visibility(False)
            self._set_menu({})
        except RuntimeError:
            pass  # the page is gone

    def set_hidden(self, hidden):
        """Hides all the combos (True) or shows the first one again (False), for a chart style the menu is not offered
        for (see style_supports_menu()). Hiding also empties the menu and discards a rebuild still running; showing
        it again leaves the menu empty until the next schedule_rebuild(), which the page makes when it redraws the
        chart. Calling it with the current state changes nothing.
        """
        hidden = bool(hidden)
        if hidden == self._hidden:
            return
        self._hidden = hidden
        self._gen += 1          # a rebuild that is still running must not fill the menu in afterwards
        self._ctx = None
        try:
            self._spinner.set_visibility(False)
            self._set_menu({})  # empty, first combo disabled, the others hidden
            self._levels[0].set_visibility(not hidden)
        except RuntimeError:
            pass  # the page is gone

    def schedule_rebuild(self, ctx):
        """Starts rebuild(ctx) in the background, so the caller (the page drawing the chart) is not held up. Does
        nothing while the menu is hidden (see set_hidden())."""
        if self._hidden:
            return
        task = asyncio.ensure_future(self.rebuild(ctx))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _reveal_spinner(self, gen):
        await asyncio.sleep(0.8)
        if gen == self._gen:
            self._spinner.set_visibility(True)

    # -- selection --------------------------------------------------------------------------------------
    def _on_level(self, i, e):
        """Handler of combo number i (a plain function: the sync guard must be checked at call time)."""
        if self._syncing or e.value is None:
            return
        path = [self._levels[j].value for j in range(i)] + [e.value]
        node = self._node_at(path)
        if node is None:
            return
        self._activate(i, path, node)

    def _activate(self, i, path, node):
        """Acts on the entry `node` that is now selected in combo i (path = the labels chosen in combos 0..i).

        A sub-menu entry shows its children in combo i + 1 with the FIRST child already selected, and acts on that
        child at once (draws it in the chart or opens its popup), so the second combo is never blank. The other
        entries: Planets clears the overlay, an overlay entry is drawn in the chart cells, anything else opens a
        popup.

        After a popup the combos go back to the item the chart shows - but only for an entry of combo 0. A popup
        chosen inside a sub-menu leaves the combos as they are, so another sibling (e.g. another Nava Thaara base)
        can be picked straight away.
        """
        for sel in self._levels[i + 1:]:
            sel.set_visibility(False)
        kind = node['t']
        back = (lambda: self._restore()) if i == 0 else (lambda: None)
        if kind == 'menu':
            first = next(iter(node['children']))
            nxt = self._levels[i + 1]
            with self._sync():
                nxt.set_options({k: k for k in node['children']}, value=first)
            nxt.set_visibility(True)
            self._activate(i + 1, path + [first], node['children'][first])
        elif kind == 'reset':
            self._applied = None
            self._apply_overlay(None)
        elif kind == 'overlay':
            if self._overlay_supported():
                self._applied = path
                self._apply_overlay(node['data'])
            else:
                self._show_popup(' > '.join(path), overlay_table_html(node['data']))
                back()
        elif kind == 'popup':
            self._show_popup(node['title'], node['html'])
            back()
        elif kind == 'prasna':
            # The combo stays on the Prasna Lagna entry while the dialog is open; a cancel puts it back (see _restore()).
            ctx = self._ctx
            self._prasna_dialog.open(
                on_accept=lambda method, number, replace: self._start_prasna(ctx, path, method, number, replace),
                on_cancel=self._restore)
        elif kind == 'lazy':
            self._show_popup(node['title'], '')  # opens at once; the content follows when it has been computed
            task = asyncio.ensure_future(self._fill_lazy(node, self._ctx))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            back()

    def _start_prasna(self, ctx, path, method, number, replace):
        task = asyncio.ensure_future(self._run_prasna(ctx, path, method, number, replace))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _run_prasna(self, ctx, path, method, number, replace):
        """Works out the Prasna Lagna in a worker thread and shows it; on any problem the combos go back to what the
        chart shows. The Prasna Lagna entry then stays selected, because the chart now shows it."""
        try:
            context = contextvars.copy_context()
            rasi = await run.io_bound(context.run, compute_prasna_locked, method, number, ctx['dcf'])
        except Exception as ex:
            safe_notify(f'Error computing the Prasna Lagna: {ex}', type='negative')
            self._restore()
            return
        if ctx is not self._ctx:
            return  # the chart changed meanwhile: the menu was rebuilt for the new chart
        self._applied = path
        self._apply_prasna(rasi, replace)
        self._restore()

    def _show_popup(self, title, body_html):
        self._title.set_text(title)
        self._body.set_content(body_html)
        self._dialog.open()

    async def _fill_lazy(self, node, ctx):
        """Fills the (already open) popup of a lazy node when its content has been computed in a worker thread."""
        if self._popup_busy.is_busy:
            self._body.set_content(f"<i>{_esc(res_str('chart_details_busy_str', 'Still working on the previous item. Please wait.'))}</i>")
            return
        try:
            body = await self._popup_busy.run(compute_lazy_locked, ctx, node['key'],
                                              wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing chart details: {ex}', type='negative')
            self._body.set_content(f'<span style="color:red">Error: {_esc(ex)}</span>')
            return
        if body is DelayedBusyIndicator.STOPPED:
            return
        if ctx is not self._ctx:
            self._dialog.close()  # the chart changed meanwhile: this result is for the old chart
            return
        self._body.set_content(body)
