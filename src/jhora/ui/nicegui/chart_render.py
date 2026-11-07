#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Shared chart-drawing code for every chart-style page (Kundali today; any future page - e.g. a
Panchangam "followed by these charts" PDF - that needs the same South/North/East Indian or
Sudarsana Chakra chart box).
Extracted from kundali_chart.py so a second page can reuse the exact same rendering, instead of a
second hand-copied version drifting out of sync with the first over time. kundali_chart.py now
imports from here instead of defining its own copies.
Every render_*() function draws into a caller-supplied NiceGUI container element and takes a plain
`overlay_lookup(rasi_idx) -> str` callable instead of reaching into any page's own state directly,
so this module has no dependency on any one page's widgets, chart-menu instance, or busy indicator -
a caller decides what (if anything) is overlaid on the chart cells, and whether crowded cells route
in a given chart style.
Every chart's planet-label text, rasi badges and Chart Details overlay text carry the CSS classes
'chart-cell-text' / 'chart-rasi-badge' / 'chart-overlay-text' (and the surface itself carries
'chart-surface', with 'chart-cell' added by a style whose cells use a fixed-height Tailwind utility,
e.g. South Indian's 'h-24'), so a page's print stylesheet (see components.py's _PRINT_CSS) can
control their font size for the printed/PDF version centrally, regardless of what Tailwind class or
inline style is used for the on-screen look.

Varga-chart computation + "every varga, one page per varga" report (added when Panchangam's own
"+ include charts" PDF option needed the same capability kundali_chart.py already had - moved here,
generalized, so it is written once instead of copy-pasted per page):
  compute_varga_chart_locked()   one varga's chart + info + Vimsottari balance, under calc_lock()
  resolve_menu_path_locked()     re-resolves a chart_details.ChartMenu.applied_path() against one
                                 chart's own menu tree (so a Saham etc. shown on one varga's chart
                                 can be re-applied, correctly, to every other varga)
  build_chart_info_html()        the Chart Information / Vimsottari text, as plain HTML strings
                                 (no UI widgets touched - safe to call from a worker thread)
  method_count_and_default_for() how many calculation methods a varga has, and its default
  build_all_vargas_pages()       loops every varga (D1..D150), returns one dict per page (title,
                                 chart data, info HTML) - the slow part, meant to run in a worker
                                 thread via components.DelayedBusyIndicator.run()
A caller (a page) still owns: its own UI widgets, its own busy indicator, and actually drawing the
returned pages into a hidden '.all-charts-report' container with '.print-report-page' /
'.print-report-page-break' before calling components.trigger_print_js() - see kundali_chart.py's
_build_all_vargas_report() for the pattern, and SAVE_AS_PDF_CENTRAL_DESIGN.md for why page-agnostic
headless rendering is the chosen architecture for Save as PDF generally.
"""
import math
from nicegui import ui
from jhora import const, utils
from jhora.horoscope import info as horo_info
from components import res_str, calc_lock
import chart_details
drik = utils.hora_engine_proxy
# Chart size in pixels (on-screen default; print CSS overrides this via the 'chart-surface' class -
# see components.py's _PRINT_CSS).
CHART_SIZE_PX = 560
# South Indian regular chart: absolute rasi index (0=Aries .. 11=Pisces) -> (row, col) in a 4x4 grid.
# Aries is at (0, 1) and the rasis run clockwise around the border; the centre 2x2 is not used.
SOUTH_MAP_TO_2D = [[11, 0, 1, 2], [10, None, None, 3], [9, None, None, 4], [8, 7, 6, 5]]
def south_cell_for_rasi(rasi_idx):
    """Returns the (row, col) of an absolute rasi index (0=Aries .. 11=Pisces) in SOUTH_MAP_TO_2D."""
    for r, row in enumerate(SOUTH_MAP_TO_2D):
        for c, cell_rasi in enumerate(row):
            if cell_rasi == rasi_idx:
                return r, c
    return None, None
# South Indian irregular chart: Aries is at (0, 2) and the rasis run anticlockwise around the border.
SOUTH_IRREGULAR_MAP_TO_2D = [[2, 1, 0, 11], [3, None, None, 10], [4, None, None, 9], [5, 6, 7, 8]]
def south_irregular_cell_for_rasi(rasi_idx):
    """Same as south_cell_for_rasi() for SOUTH_IRREGULAR_MAP_TO_2D."""
    for r, row in enumerate(SOUTH_IRREGULAR_MAP_TO_2D):
        for c, cell_rasi in enumerate(row):
            if cell_rasi == rasi_idx:
                return r, c
    return None, None
# North Indian chart: label position (x %, y %) of each house. Index 0 is the house containing the
# ascendant; the data is rotated by the ascendant house before drawing.
NORTH_LABEL_POSITIONS = [
    (40, 10), (15, 5), (1, 20), (15, 40), (1, 70), (17.5, 85), (35, 70), (67.5, 85),
    (85, 70), (65, 40), (83.5, 20), (65, 5),
]
# North Indian chart: position of the rasi badge of each house as (vertex_x, vertex_y, nudge_dx, nudge_dy),
# in % of the chart size: the nearest frame vertex (square corner or diamond tip) plus a small offset.
NORTH_BADGE_ANCHORS = [
    (50, 0, -6, 2), (0, 0, 5, 1), (0, 0, 1, 5), (0, 50, 1, -6),
    (0, 50, 1, 6), (0, 100, 3, -3), (50, 100, -6, -2), (50, 100, 6, -2),
    (100, 50, -2, 6), (100, 50, -2, -6), (100, 0, -3, 3), (50, 0, 6, 2),
]
# North Indian chart: top-left position (x %, y %) of the Chart Details overlay text of each house.
NORTH_OVERLAY_POSITIONS = [
    (50, 37.5), (32.5, 1), (1, 37.5), (22.5, 65), (1, 87.5), (5, 95),
    (45, 82.5), (87.5, 95), (92.5, 87.5), (72.5, 65), (92.5, 37.5), (87.5, 2.5),
]
# East Indian chart: Aries is the top-middle cell and the rasis run anticlockwise. Each of the four
# corner cells holds two rasis (split diagonally); the four edge-middle cells hold one each.
EAST_EDGE_CELLS = {'top': 0, 'left': 3, 'bottom': 6, 'right': 9}
EAST_CORNER_CELLS = {
    'top_left': (1, 2), 'bottom_left': (4, 5), 'bottom_right': (7, 8), 'top_right': (10, 11),
}
# Zodiac glyphs (Aries U+2648 .. Pisces U+2653), one per rasi.
RASI_SHORT = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D', '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653']
# Sudarsana Chakra: (inner radius %, outer radius %) of each of the three concentric bhava rings.
SC_RING_RADII_PCT = [(8, 20), (20, 33), (33, 46)]
_chart_names = const._chart_names
_division_chart_factors = const.division_chart_factors
def planet_label(token):
    """Returns the short display label of one token of a house's planet string: the ascendant label for
    the ascendant symbol, utils.PLANET_SHORT_NAMES[int(token)] for a planet index, otherwise the token.
    """
    token = token.strip()
    if not token:
        return ''
    if token == const._ascendant_symbol:
        return res_str('ascendant_short_str', 'Asc')
    try:
        return utils.PLANET_SHORT_NAMES[int(token)]
    except Exception:
        return token
def cell_text(raw_cell):
    """Returns the display text of one house: short planet labels, one per line ('' for an empty house).
    Args:
        raw_cell: '/'-joined planet tokens of the house (e.g. 'L/0/7'), or ''.
    """
    if not raw_cell or not raw_cell.strip():
        return ''
    return '\n'.join(planet_label(t) for t in raw_cell.split('/') if t.strip() != '')
def planet_text_classes(raw_cell):
    """Returns the font-size class of a house's planet text: smaller when 4 or more planets share the house."""
    count = len([t for t in (raw_cell or '').split('/') if t.strip() != ''])
    return 'text-[10px]' if count >= 4 else 'text-xs'
def varga_label(i):
    """Returns the localized name of the divisional chart at index `i` of const.division_chart_factors."""
    return res_str(_chart_names[i], _chart_names[i].replace('_str', '').replace('_', ' ').title())
def chart_style_label(style):
    """Returns the localized label of a chart style key of const.AVAILABLE_CHART_STYLES."""
    cfg = const.AVAILABLE_CHART_STYLES[style]
    return res_str(cfg["resource"], cfg["resource"].replace('_str', '').replace('_', ' ').title())
def method_count_and_default_for(varga_idx):
    """Returns (method_count, default_method) of the divisional chart at index `varga_idx`; the
    default method is 1-based. D1 (index 0) and a failed lookup give (1, 1).
    """
    if varga_idx == 0:
        return 1, 1
    varga_factor = _division_chart_factors[varga_idx]
    try:
        method_count, default_method, _base_rasi_idx, _count_from_end = utils.get_varga_option_dict()[varga_factor]
    except (KeyError, TypeError, ValueError) as e:
        print(f"[chart_render] get_varga_option_dict() lookup/unpack failed for varga_factor={varga_factor} (varga_idx={varga_idx}): {e}")
        return 1, 1
    if method_count is None:
        return 1, 1
    return method_count, (default_method if default_method is not None else 1)
def _place_center_icon():
    """Draws the decorative centre icon of a chart (South Indian's unused 2x2 centre cell): the
    configured image (const._IMAGE_ICON_PATH) if set, otherwise a generic temple icon. Call inside a
    container that already centres its content.
    """
    icon_path = getattr(const, '_IMAGE_ICON_PATH', None)
    if icon_path:
        ui.image(icon_path).classes('w-16 h-16 object-contain')
    else:
        ui.icon('temple_hindu', size='2rem').classes('text-amber-700')
def _place_center_icon_absolute(left_pct, top_pct, size_pct):
    """Draws the decorative centre icon at an absolute position, for chart styles (North, East Indian,
    Sudarsana Chakra) whose unused centre is not a single grid cell.
    """
    icon_path = getattr(const, '_IMAGE_ICON_PATH', None)
    with ui.element('div').style(
        f'position:absolute; left:{left_pct}%; top:{top_pct}%; width:{size_pct}%; height:{size_pct}%;'
    ):
        if icon_path:
            ui.image(icon_path).classes('w-full h-full object-contain')
        else:
            ui.icon('temple_hindu', size='1.2rem').classes('text-amber-700')
def render_south_indian_generic(container, chart_1d, asc_house, cell_lookup_fn, overlay_lookup):
    """Draws a South Indian chart (4x4 border grid, empty 2x2 centre); regular and irregular differ
    only in the rasi-to-cell map.
    Args:
        container: NiceGUI container to draw into (cleared first).
        chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
        asc_house: rasi index of the ascendant (its cell is highlighted).
        cell_lookup_fn: south_cell_for_rasi or south_irregular_cell_for_rasi.
        overlay_lookup: callable(rasi_idx) -> overlay text for that rasi, or ''.
    """
    chart_2d = [[''] * 4 for _ in range(4)]
    rasi_2d = [[None] * 4 for _ in range(4)]
    for rasi_idx in range(12):
        r, c = cell_lookup_fn(rasi_idx)
        if r is not None:
            chart_2d[r][c] = cell_text(chart_1d[rasi_idx])
            rasi_2d[r][c] = rasi_idx
    asc_r, asc_c = cell_lookup_fn(asc_house)
    container.clear()
    with container:
        with ui.grid(columns=4).classes('gap-1 bg-white p-2 border-2 border-brown-700 rounded chart-surface') \
                .style(f'width:{CHART_SIZE_PX}px; grid-template-rows: repeat(4, minmax(0, 1fr));'):
            with ui.card().classes('flex items-center justify-center bg-yellow-50 border border-brown-300') \
                    .style('grid-column: 2 / span 2; grid-row: 2 / span 2;'):
                _place_center_icon()
            for r in range(4):
                for c in range(4):
                    is_center = (1 <= r <= 2 and 1 <= c <= 2)
                    if is_center:
                        continue
                    is_asc = (r == asc_r and c == asc_c)
                    bg = 'bg-emerald-100 border-2 border-green-600' if is_asc else 'bg-yellow-50 border border-brown-300'
                    with ui.card().classes(f'h-24 chart-cell {bg} p-1 flex items-center justify-center text-center relative'):
                        if rasi_2d[r][c] is not None:
                            ui.label(RASI_SHORT[rasi_2d[r][c]]).classes(
                                'absolute top-0.5 left-1 text-[10px] text-gray-400 font-normal leading-none chart-rasi-badge'
                            )
                        ui.label(chart_2d[r][c]).classes(
                            f'{planet_text_classes(chart_1d[(rasi_2d[r][c] if rasi_2d[r][c] is not None else 0)])} '
                            'font-bold text-brown-800 whitespace-pre-line chart-cell-text'
                        )
                        _ov = overlay_lookup(rasi_2d[r][c])
                        if _ov:
                            ui.label(_ov).classes(
                                'absolute bottom-0.5 left-1 text-[9px] text-blue-700 font-bold '
                                'whitespace-pre-line leading-tight text-left chart-overlay-text'
                            )
def render_south_indian(container, chart_1d, asc_house, overlay_lookup):
    """Draws the South Indian regular chart."""
    render_south_indian_generic(container, chart_1d, asc_house, south_cell_for_rasi, overlay_lookup)
def render_south_indian_irregular(container, chart_1d, asc_house, overlay_lookup):
    """Draws the South Indian irregular chart."""
    render_south_indian_generic(container, chart_1d, asc_house, south_irregular_cell_for_rasi, overlay_lookup)
def render_east_indian(container, chart_1d, asc_house, draw_frame, overlay_lookup):
    """Draws an East Indian chart (3x3 layout, see the East Indian maps above).
    Args:
        container: NiceGUI container to draw into (cleared first).
        chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
        asc_house: rasi index of the ascendant (its planet text is highlighted).
        draw_frame: draw the outer square frame.
        overlay_lookup: callable(rasi_idx) -> overlay text for that rasi, or ''.
    """
    container.clear()
    frame_stroke = 'stroke="#5c3a21" stroke-width="1"' if draw_frame else 'stroke="none"'
    with container:
        with ui.element('div').classes('chart-surface').style(f'position:relative; width:{CHART_SIZE_PX}px; height:{CHART_SIZE_PX}px;'):
            ui.html(f'''
                <svg viewBox="0 0 99 99" style="position:absolute;top:0;left:0;width:100%;height:100%;">
                  <rect x="0.5" y="0.5" width="98" height="98" fill="none" {frame_stroke}/>
                  <line x1="33" y1="0" x2="33" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="66" y1="0" x2="66" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="33" y1="66" x2="33" y2="99" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="66" y1="66" x2="66" y2="99" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="0" y1="33" x2="33" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="0" y1="66" x2="33" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="66" y1="33" x2="99" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="66" y1="66" x2="99" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="33" y1="33" x2="66" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="33" y1="66" x2="66" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="33" y1="33" x2="33" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="66" y1="33" x2="66" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="0" y1="0" x2="33" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="99" y1="0" x2="66" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="0" y1="99" x2="33" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="99" y1="99" x2="66" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                </svg>
            ''')
            _place_center_icon_absolute(40, 40, 20)
            def _place_text(px, py, rasi_idx, width=15, align='center'):
                text = cell_text(chart_1d[rasi_idx])
                is_asc = (rasi_idx == asc_house)
                color = 'color:#15803d; font-weight:bold;' if is_asc else 'color:#5c3a21; font-weight:bold;'
                font_size = '9px' if len([t for t in chart_1d[rasi_idx].split('/') if t.strip()]) >= 4 else '10px'
                with ui.element('div').classes('chart-cell-text').style(
                    f'position:absolute; left:{px}%; top:{py}%; width:{width}%; '
                    f'font-size:{font_size}; text-align:{align}; white-space:pre-line; {color}; line-height:1.25;'
                ):
                    ui.label(text)
                _ov = overlay_lookup(rasi_idx)
                if _ov:
                    with ui.element('div').classes('chart-overlay-text').style(
                        f'position:absolute; left:{px}%; top:{py + 10}%; width:{width}%; '
                        f'font-size:9px; text-align:{align}; white-space:pre-line; color:#1d4ed8; '
                        f'font-weight:bold; line-height:1.15;'
                    ):
                        ui.label(_ov)
            def _place_badge(px, py, rasi_idx):
                with ui.element('div').classes('chart-rasi-badge').style(
                    f'position:absolute; left:{px}%; top:{py}%; '
                    f'font-size:11px; color:#9ca3af; line-height:1;'
                ):
                    ui.label(RASI_SHORT[rasi_idx])
            _place_badge(41, 1, EAST_EDGE_CELLS['top']); _place_text(42, 8, EAST_EDGE_CELLS['top'])
            _place_badge(41, 95, EAST_EDGE_CELLS['bottom']); _place_text(42, 78, EAST_EDGE_CELLS['bottom'])
            _place_badge(1, 46, EAST_EDGE_CELLS['left']); _place_text(9, 42, EAST_EDGE_CELLS['left'])
            _place_badge(95, 46, EAST_EDGE_CELLS['right']); _place_text(75, 42, EAST_EDGE_CELLS['right'])
            tl_top, tl_left = EAST_CORNER_CELLS['top_left']
            _place_badge(14, 2, tl_top); _place_text(14, 6, tl_top, width=17, align='right')
            _place_badge(2, 14, tl_left); _place_text(3, 23, tl_left, width=17, align='left')
            tr_right, tr_top = EAST_CORNER_CELLS['top_right']
            _place_badge(85, 2, tr_top); _place_text(68, 6, tr_top, width=17, align='left')
            _place_badge(95, 14, tr_right); _place_text(80, 23, tr_right, width=17, align='right')
            bl_left, bl_bottom = EAST_CORNER_CELLS['bottom_left']
            _place_badge(2, 84, bl_left); _place_text(3, 57, bl_left, width=17, align='left')
            _place_badge(14, 95, bl_bottom); _place_text(14, 80, bl_bottom, width=17, align='right')
            br_bottom, br_right = EAST_CORNER_CELLS['bottom_right']
            _place_badge(85, 95, br_bottom); _place_text(68, 80, br_bottom, width=17, align='left')
            _place_badge(95, 84, br_right); _place_text(80, 57, br_right, width=17, align='right')
def render_north_indian(container, chart_1d, asc_house, overlay_lookup):
    """Draws the North Indian chart (diamond layout).
    Args:
        container: NiceGUI container to draw into (cleared first).
        chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
        asc_house: rasi index of the ascendant; house 0 of the drawing.
        overlay_lookup: callable(absolute_rasi_idx) -> overlay text for that rasi, or ''.
    """
    rotated = chart_1d[asc_house:] + chart_1d[0:asc_house]
    container.clear()
    with container:
        with ui.element('div').classes('chart-surface').style(f'position:relative; width:{CHART_SIZE_PX}px; height:{CHART_SIZE_PX}px;'):
            ui.html('''
                <svg viewBox="0 0 100 100" style="position:absolute;top:0;left:0;width:100%;height:100%;">
                  <rect x="0" y="0" width="100" height="100" fill="none" stroke="#5c3a21" stroke-width="1"/>
                  <line x1="0" y1="0" x2="100" y2="100" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="100" y1="0" x2="0" y2="100" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="0" y1="50" x2="50" y2="0" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="50" y1="0" x2="100" y2="50" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="100" y1="50" x2="50" y2="100" stroke="#5c3a21" stroke-width="0.6"/>
                  <line x1="50" y1="100" x2="0" y2="50" stroke="#5c3a21" stroke-width="0.6"/>
                </svg>
            ''')
            _place_center_icon_absolute(42, 42, 16)
            for l, (px, py) in enumerate(NORTH_LABEL_POSITIONS):
                text = cell_text(rotated[l])
                is_asc = (l == 0)
                color = 'color:#15803d; font-weight:bold;' if is_asc else 'color:#5c3a21; font-weight:bold;'
                font_size = '9px' if len([t for t in rotated[l].split('/') if t.strip()]) >= 4 else '10px'
                if px < 45:
                    align = 'left'
                elif px > 55:
                    align = 'right'
                else:
                    align = 'center'
                with ui.element('div').classes('chart-cell-text').style(
                    f'position:absolute; left:{px}%; top:{py}%; width:15%; '
                    f'font-size:{font_size}; text-align:{align}; white-space:pre-line; {color}; line-height:1.25;'
                ):
                    ui.label(text)
                _ov = overlay_lookup((asc_house + l) % 12)
                if _ov:
                    ox, oy = NORTH_OVERLAY_POSITIONS[l]
                    side = f'right:{100 - ox}%; text-align:right;' if ox >= 80 else f'left:{ox}%; text-align:left;'
                    with ui.element('div').classes('chart-overlay-text').style(
                        f'position:absolute; {side} top:{oy}%; width:15%; font-size:9px; '
                        f'white-space:pre-line; color:#1d4ed8; font-weight:bold; line-height:1.15;'
                    ):
                        ui.label(_ov)
                vx, vy, ndx, ndy = NORTH_BADGE_ANCHORS[l]
                abs_rasi = (asc_house + l) % 12
                with ui.element('div').classes('chart-rasi-badge').style(
                    f'position:absolute; left:{vx + ndx}%; top:{vy + ndy}%; '
                    f'font-size:10px; color:#9ca3af; line-height:1;'
                ):
                    ui.label(RASI_SHORT[abs_rasi])
# Western chart: (r1, r2, r3, r4) radii of the four concentric circles, in % of chart size — same
# proportions as the desktop WesternChart (icon hole, planet ring, degree-tick ring, zodiac/house-cusp ring).
_WESTERN_RING_RADII_PCT = (9, 28, 44, 49)
def render_western(container, chart_1d, asc_house, overlay_lookup):
    """Draws the Western chart: 4 concentric circles, 12 house-cusp spokes starting at the ascendant
    (9 o'clock, going anticlockwise), zodiac glyphs in the outer ring, planet text in the middle ring.
    Ported from the desktop app's WesternChart (chart_styles.py), using the web's sign-indexed chart_1d
    (whole-sign houses) in place of the desktop version's exact per-planet degree strings.
    Args:
        container: NiceGUI container to draw into (cleared first).
        chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
        asc_house: rasi index of the ascendant; house 0 of the drawing.
        overlay_lookup: callable(absolute_rasi_idx) -> overlay text for that rasi, or ''.
    """
    r1, r2, r3, r4 = _WESTERN_RING_RADII_PCT
    container.clear()
    with container:
        with ui.element('div').classes('chart-surface').style(
                f'position:relative; width:{CHART_SIZE_PX}px; height:{CHART_SIZE_PX}px;'):
            circles = ''.join(
                f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="#5c3a21" stroke-width="0.4"/>'
                for r in (r1, r2, r3, r4)
            )
            spokes = ''.join(
                f'<line x1="{50 + r3*math.cos(math.radians(180-h*30)):.2f}" '
                f'y1="{50 - r3*math.sin(math.radians(180-h*30)):.2f}" '
                f'x2="{50 + r4*math.cos(math.radians(180-h*30)):.2f}" '
                f'y2="{50 - r4*math.sin(math.radians(180-h*30)):.2f}" '
                f'stroke="#5c3a21" stroke-width="0.5"/>' for h in range(12)
            )
            ticks = ''.join(
                f'<line x1="{50 + r2*math.cos(math.radians(d)):.2f}" '
                f'y1="{50 - r2*math.sin(math.radians(d)):.2f}" '
                f'x2="{50 + r3*math.cos(math.radians(d)):.2f}" '
                f'y2="{50 - r3*math.sin(math.radians(d)):.2f}" '
                f'stroke="#5c3a21" stroke-width="0.2"/>' for d in range(0, 360, 10)
            )
            ui.html(
                f'<svg viewBox="0 0 100 100" style="position:absolute;top:0;left:0;width:100%;height:100%;">'
                f'{circles}{ticks}{spokes}</svg>'
            )
            _place_center_icon_absolute(42, 42, 2 * r1 * 0.9)
            for h in range(12):
                abs_rasi = (asc_house + h) % 12
                mid = 180 - (h * 30 + 15)
                px = 50 + ((r2 + r3) / 2) * math.cos(math.radians(mid))
                py = 50 - ((r2 + r3) / 2) * math.sin(math.radians(mid))
                color = 'color:#15803d; font-weight:bold;' if h == 0 else 'color:#5c3a21; font-weight:bold;'
                with ui.element('div').classes('chart-cell-text').style(
                        f'position:absolute; left:{px:.2f}%; top:{py:.2f}%; width:14%; '
                        f'transform:translate(-50%,-50%); font-size:9px; text-align:center; '
                        f'white-space:pre-line; {color} line-height:1.1;'):
                    ui.label(cell_text(chart_1d[abs_rasi]))
                zx = 50 + ((r3 + r4) / 2) * math.cos(math.radians(mid))
                zy = 50 - ((r3 + r4) / 2) * math.sin(math.radians(mid))
                with ui.element('div').classes('chart-rasi-badge').style(
                        f'position:absolute; left:{zx:.2f}%; top:{zy:.2f}%; '
                        f'transform:translate(-50%,-50%); font-size:11px; color:#9ca3af; line-height:1;'):
                    ui.label(RASI_SHORT[abs_rasi])
                _ov = overlay_lookup(abs_rasi)
                if _ov:
                    with ui.element('div').classes('chart-overlay-text').style(
                            f'position:absolute; left:{px:.2f}%; top:{py+6:.2f}%; width:14%; '
                            f'transform:translate(-50%,0); font-size:8px; text-align:center; '
                            f'white-space:pre-line; color:#1d4ed8; font-weight:bold; line-height:1.1;'):
                        ui.label(_ov)
def render_sudarsana_chakra(container, sc_rings):
    """Draws the Sudarsana Chakra chart: three concentric bhava rings (Lagna, Moon and Sun, from the
    centre outward), each divided into its 12 houses.
    Args:
        container: NiceGUI container to draw into (cleared first).
        sc_rings: [lagna_chart, moon_chart, sun_chart, retrograde_planets] from
            sudharsana_chakra.sudharshana_chakra_chart(); each of the first three is 12
            (absolute rasi index, '/'-joined planet tokens) tuples, indexed by house from that
            reference point (index 0 is the reference point's own house, highlighted).
    """
    lagna_chart, moon_chart, sun_chart, _retrograde = sc_rings
    ring_defs = [
        (lagna_chart, res_str('ascendant_str', 'Lagna'), SC_RING_RADII_PCT[0]),
        (moon_chart, utils.PLANET_NAMES[const.MOON_ID], SC_RING_RADII_PCT[1]),
        (sun_chart, utils.PLANET_NAMES[const.SUN_ID], SC_RING_RADII_PCT[2]),
    ]
    hole_r = ring_defs[0][2][0]
    outer_r = ring_defs[-1][2][1]
    container.clear()
    with container:
        with ui.element('div').classes('chart-surface').style(f'position:relative; width:{CHART_SIZE_PX}px; height:{CHART_SIZE_PX}px;'):
            circles = f'<circle cx="50" cy="50" r="{hole_r}" fill="none" stroke="#5c3a21" stroke-width="0.4"/>'
            circles += ''.join(
                f'<circle cx="50" cy="50" r="{r_out}" fill="none" stroke="#5c3a21" stroke-width="0.4"/>'
                for _, _, (_, r_out) in ring_defs
            )
            spokes = ''.join(
                f'<line x1="{50 + hole_r * math.cos(math.radians(-90 + h * 30 - 15)):.2f}" '
                f'y1="{50 + hole_r * math.sin(math.radians(-90 + h * 30 - 15)):.2f}" '
                f'x2="{50 + outer_r * math.cos(math.radians(-90 + h * 30 - 15)):.2f}" '
                f'y2="{50 + outer_r * math.sin(math.radians(-90 + h * 30 - 15)):.2f}" '
                f'stroke="#5c3a21" stroke-width="0.3"/>'
                for h in range(12)
            )
            ui.html(f'''
                <svg viewBox="0 0 100 100" style="position:absolute;top:0;left:0;width:100%;height:100%;">
                  {circles}
                  {spokes}
                </svg>
            ''')
            _place_center_icon_absolute(42, 42, 2 * hole_r * 0.9)
            for ring_data, _ring_label, (r_in, r_out) in ring_defs:
                r_label = (r_in + r_out) / 2
                for h in range(12):
                    abs_rasi, raw_cell = ring_data[h]
                    angle = math.radians(-90 + h * 30)
                    cx = 50 + r_label * math.cos(angle)
                    cy = 50 + r_label * math.sin(angle)
                    is_ref_house = (h == 0)
                    color = 'color:#15803d; font-weight:bold;' if is_ref_house else 'color:#5c3a21; font-weight:bold;'
                    with ui.element('div').classes('chart-cell-text').style(
                        f'position:absolute; left:{cx:.2f}%; top:{cy:.2f}%; width:12%; '
                        f'transform:translate(-50%,-40%); font-size:8px; text-align:center; '
                        f'white-space:pre-line; {color} line-height:1.1;'
                    ):
                        ui.label(cell_text(raw_cell))
                    with ui.element('div').classes('chart-rasi-badge').style(
                        f'position:absolute; left:{cx:.2f}%; top:{cy - (r_out - r_in) * 0.32:.2f}%; '
                        f'font-size:7px; color:#9ca3af; line-height:1; transform:translate(-50%,-100%);'
                    ):
                        ui.label(RASI_SHORT[abs_rasi])
            with ui.element('div').style(
                'position:absolute; left:2%; top:2%; font-size:9px; color:#5c3a21; white-space:nowrap;'
            ):
                ui.label(
                    f"{res_str('inner_str', 'Inner')}: {ring_defs[0][1]}  |  "
                    f"{res_str('middle_str', 'Middle')}: {ring_defs[1][1]}  |  "
                    f"{res_str('outer_str', 'Outer')}: {ring_defs[2][1]}"
                )
def render_not_yet_implemented(container, style_label):
    """Shows a placeholder for a chart style that cannot be drawn yet (e.g. Western)."""
    container.clear()
    with container:
        with ui.card().classes('w-full max-w-md p-8 bg-gray-50 border-2 border-dashed border-gray-300 text-center'):
            ui.icon('construction', size='2rem').classes('text-gray-400')
            ui.label(f'{style_label} chart rendering is not yet implemented.').classes('text-gray-500 mt-2')
            ui.label('Switch to South Indian, East Indian, North Indian, or Sudarsana Chakra for now.').classes('text-gray-400 text-sm')
def render_chart_into(chart_container_el, overlay_table_el, chart_style, chart_1d, asc_house, sc_rings,
                       overlay, overlay_too_crowded_fn, overlay_side_table_html_fn, applied_label):
    """Dispatches to the right render_*() function for ONE chart (reusable for a single live chart or
    one page of a multi-page report).
    Args:
        chart_container_el: NiceGUI container the chart itself is drawn into.
        overlay_table_el: NiceGUI html element for the crowded-overlay side table, or None to skip
            that handling entirely (e.g. a caller that never shows a table-style overlay).
        chart_style: const.CHART_STYLE value.
        chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi (already adjusted for
            a Prasna Lagna replacement, if any - this function does not know about Prasna Lagna).
        asc_house: rasi index of the ascendant.
        sc_rings: Sudarsana Chakra ring data (see render_sudarsana_chakra()); ignored for other styles.
        overlay: 12-list of overlay text indexed by absolute rasi, or None/[] for "show Planets".
        overlay_too_crowded_fn: chart_details.overlay_too_crowded (passed in, not imported here, to
            avoid this module depending on chart_details for this specific call path - the varga-
            report functions further below DO import chart_details directly, since they need its
            make_context()/build_menu_locked() regardless).
        overlay_side_table_html_fn: chart_details.overlay_side_table_html (same reasoning).
        applied_label: the label of the currently-applied menu entry (chart_details.ChartMenu's
            applied_label()), used only for the side-table caption when the overlay is shown that way.
    """
    as_table = bool(overlay) and overlay_too_crowded_fn(overlay)
    if overlay_table_el is not None:
        overlay_table_el.set_content(overlay_side_table_html_fn(overlay, applied_label) if as_table else '')
        overlay_table_el.set_visibility(as_table)
    if as_table:
        overlay_lookup = lambda rasi_idx: ''
    else:
        overlay_lookup = lambda rasi_idx: (overlay[rasi_idx] if overlay and rasi_idx is not None else '')
    if chart_style == const.CHART_STYLE.SOUTH_INDIAN_REGULAR:
        render_south_indian(chart_container_el, chart_1d, asc_house, overlay_lookup)
    elif chart_style == const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR:
        render_south_indian_irregular(chart_container_el, chart_1d, asc_house, overlay_lookup)
    elif chart_style == const.CHART_STYLE.NORTH_INDIAN:
        render_north_indian(chart_container_el, chart_1d, asc_house, overlay_lookup)
    elif chart_style == const.CHART_STYLE.EAST_INDIAN_WITH_FRAME:
        render_east_indian(chart_container_el, chart_1d, asc_house, True, overlay_lookup)
    elif chart_style == const.CHART_STYLE.EAST_INDIAN_NO_FRAME:
        render_east_indian(chart_container_el, chart_1d, asc_house, False, overlay_lookup)
    elif chart_style == const.CHART_STYLE.SUDARSANA_CHAKRA:
        render_sudarsana_chakra(chart_container_el, sc_rings)
    elif chart_style == const.CHART_STYLE.WESTERN:
        render_western(chart_container_el, chart_1d, asc_house, overlay_lookup)
    else:
        render_not_yet_implemented(chart_container_el, chart_style_label_fallback(chart_style))
def chart_style_label_fallback(style):
    """Returns a readable label for a chart style, for the "not yet implemented" placeholder only
    (callers that need the real localized label elsewhere already have their own chart_style_label()
    using const.AVAILABLE_CHART_STYLES - this is just a plain fallback so this module does not need
    that dict's exact shape to render a placeholder message).
    """
    return getattr(style, 'name', str(style)).replace('_', ' ').title()
# ---------------------------------------------------------------------------------------------------------
# Varga-chart computation + "every varga, one page per varga" report (see the module docstring above).
# ---------------------------------------------------------------------------------------------------------
def compute_varga_chart_locked(dob, tob, place_val, lat_val, lon_val, tz_val, varga_idx, dcf, chart_method, chart_style):
    """Computes one varga's chart, its information panel and Vimsottari dhasa balance under calc_lock().
    Blocking; run in a worker thread.
    Returns:
        (horo, chart_info, chart_1d, asc_house, vim_db, vim_balance, sc_rings).
    """
    sc_rings = None
    with calc_lock():
        horo = horo_info.Horoscope(
            latitude=lat_val, longitude=lon_val, timezone_offset=tz_val,
            date_in=drik.Date(*dob), birth_time=f"{tob[0]:02d}:{tob[1]:02d}:{tob[2]:02d}",
            calculation_type='drik', language=const._DEFAULT_LANGUAGE,
        )
        chart_info, chart_1d_raw, asc_house = horo.get_horoscope_information_for_chart(
            chart_index=varga_idx, chart_method=chart_method, divisional_chart_factor=dcf,
        )
        chart_1d = [x.rstrip('/') for x in chart_1d_raw]
        vim_db = horo._get_vimsottari_dhasa_bhukthi(horo.Date, horo.birth_time, horo.Place)
        vim_balance = getattr(horo, '_vimsottari_balance', None)
        if chart_style == const.CHART_STYLE.SUDARSANA_CHAKRA:
            from jhora.horoscope.dhasa import sudharsana_chakra
            place_obj = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
            jd_at_dob = utils.julian_day_number(drik.Date(*dob), tob)
            sc_rings = sudharsana_chakra.sudharshana_chakra_chart(
                jd_at_dob, place_obj, dob, years_from_dob=1,
                divisional_chart_factor=dcf, chart_method=chart_method,
            )
    return horo, chart_info, chart_1d, asc_house, vim_db, vim_balance, sc_rings
def resolve_menu_path_locked(horo, dob, tob, varga_idx, dcf, chart_method, chart_style, path):
    """Rebuilds the chart-menu tree for ONE chart and walks `path` (a list of labels, as returned by
    chart_details.ChartMenu.applied_path()) through it.
    Returns:
        The 12-list overlay data if `path` resolves to an overlay node in THIS chart's own menu tree,
        otherwise None - either because this chart's menu does not have an entry with these exact
        labels, or because the entry it resolves to is not a chart-cell overlay for this chart.
    """
    ctx = chart_details.make_context(horo, dob, tob, varga_idx, dcf, chart_method, chart_style)
    menu = chart_details.build_menu_locked(ctx)
    children = menu
    node = None
    for label in path:
        node = children.get(label) if isinstance(children, dict) else None
        if node is None:
            return None
        children = node.get('children', {})
    if node is not None and node.get('t') == 'overlay':
        return node.get('data')
    return None
def build_chart_info_html(dob_val, tob_val, place_val, chart_info, vim_balance, vim_db):
    """Returns (info_html_1, info_html_2): the Chart Information / Vimsottari text split into two
    roughly even HTML strings, as plain text (no UI widgets touched) - reusable from a worker thread.
    """
    lines_col1 = []
    lines_col2 = []
    lines_col1.append(f"<b>{res_str('date_of_birth_str','Date of Birth')}:</b> {dob_val}")
    lines_col1.append(f"<b>{res_str('time_of_birth_str','Time of Birth')}:</b> {tob_val}")
    lines_col1.append(f"<b>{res_str('place_str','Place')}:</b> {place_val}")
    lines_col1.append('')
    lines_col1.append(f"<b>{res_str('chart_information_str','Chart Information')}</b>")
    items = list(chart_info.items())
    mid = len(items) // 2
    for k, v in items[:mid]:
        k1 = str(k).split('-')[-1]
        v1 = str(v).split('-')[0]
        lines_col1.append(f"<span style='color:brown'>{k1}</span>: <span style='color:blue'>{v1}</span>")
    for k, v in items[mid:]:
        k1 = str(k).split('-')[-1]
        v1 = str(v).split('-')[0]
        lines_col2.append(f"<span style='color:brown'>{k1}</span>: <span style='color:blue'>{v1}</span>")
    lines_col2.append('')
    lines_col2.append(f"<b>{res_str('vimsottari_str','Vimsottari')} {res_str('dhasa_str','Dhasa')} {res_str('balance_str','Balance')} ({res_str('birth_str','At Birth')}):</b> "
                    + (':'.join(map(str, vim_balance)) if vim_balance is not None else 'N/A'))
    if vim_db:
        lines_col2.append(f"<b>{res_str('dhasa_str','Dhasa')}-{res_str('bhukthi_str','Bhukthi')} ({res_str('birth_str','At Birth')}):</b>")
        for k, v in vim_db[:9]:
            lines_col2.append(f"<span style='color:brown'>{k}</span>: <span style='color:blue'>{v}</span>")
    sep = '<br>'
    return sep.join(lines_col1), sep.join(lines_col2)
def build_all_vargas_pages(dob, tob, place_val, lat_val, lon_val, tz_val, chart_style, chart_options_state, applied_path):
    """Computes every varga's chart, information text and (if `applied_path` is given) that varga's
    own version of a currently-applied chart-menu overlay, under calc_lock() (one varga at a time).
    Blocking; run in a worker thread - this is up to 24 full chart computations plus, if a menu
    overlay is applied, 24 menu-tree rebuilds (costly - computes arudhas, sphutas, sahams, etc.), so
    this can take a while. A varga whose own chart computation fails is skipped (reported on the
    console) rather than aborting the whole report.
    Args:
        dob, tob, place_val, lat_val, lon_val, tz_val: birth/event details, as read from a page's
            own control bar.
        chart_style: const.CHART_STYLE value to draw every varga in.
        chart_options_state: {varga_idx: chart_method} of the visitor's own Chart Options choices (a
            page without this concept - e.g. Panchangam - can pass {} to use every varga's default
            method).
        applied_path: list of labels (chart_details.ChartMenu.applied_path()), or None/[] for
            "Planets" on every page (a page with no ChartMenu of its own - e.g. Panchangam - always
            passes None).
    Returns:
        List of per-varga page dicts: title, chart_style, chart_1d, asc_house, sc_rings, overlay,
        info_html_1, info_html_2 - everything a caller's own render_chart_into() + two ui.html() calls
        need, with no UI widgets touched (safe to build in a worker thread).
    """
    pages = []
    for varga_idx in range(len(_division_chart_factors)):
        dcf = _division_chart_factors[varga_idx]
        _, default_method = method_count_and_default_for(varga_idx)
        chart_method = chart_options_state.get(varga_idx, default_method)
        try:
            horo, chart_info, chart_1d, asc_house, vim_db, vim_balance, sc_rings = compute_varga_chart_locked(
                dob, tob, place_val, lat_val, lon_val, tz_val, varga_idx, dcf, chart_method, chart_style)
        except Exception as e:
            print(f"[chart_render] all-vargas report: chart computation failed for "
                  f"varga_idx={varga_idx} ({varga_label(varga_idx)}): {type(e).__name__}: {e}")
            continue
        overlay = None
        if applied_path:
            try:
                overlay = resolve_menu_path_locked(horo, dob, tob, varga_idx, dcf, chart_method, chart_style, applied_path)
            except Exception as e:
                print(f"[chart_render] all-vargas report: could not resolve the chart-menu selection "
                      f"{applied_path!r} for varga_idx={varga_idx} ({varga_label(varga_idx)}): "
                      f"{type(e).__name__}: {e}")
        dob_val = f"{dob[0]},{dob[1]},{dob[2]}"
        tob_val = f"{tob[0]:02d}:{tob[1]:02d}:{tob[2]:02d}"
        info_html_1, info_html_2 = build_chart_info_html(dob_val, tob_val, place_val, chart_info, vim_balance, vim_db)
        title = f"{varga_label(varga_idx)} ({chart_style_label(chart_style)}) \u2014 {place_val}"
        pages.append({'title': title, 'chart_style': chart_style, 'chart_1d': chart_1d, 'asc_house': asc_house,
                      'sc_rings': sc_rings, 'overlay': overlay, 'info_html_1': info_html_1, 'info_html_2': info_html_2})
    return pages
