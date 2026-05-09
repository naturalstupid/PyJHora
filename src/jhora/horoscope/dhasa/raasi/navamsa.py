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
from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

""" Navamsa Dasa """

year_duration = const.sidereal_year


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


"""
Birth in Sign    Ar    Ta    Ge    Cn    Le    Vi    Li    Sc    Sg    Cp    Aq    Pi
9 Years          Ar    Le    Li    Aq    Ar    Le    Li    Aq    Ar    Le    Li    Aq
                 0     4     6     10    0     4     6     10    0     4     6     10
                 Li    Ar    Sg    Aq    Le    Sg    Li    Ar    Sg    Aq    Le    Sg
                 6     0     8     10    4     8     6     0     8     10    4     8
"""
dhasa_adhipati_list = [0, 4, 6, 10, 0, 4, 6, 10, 0, 4, 6, 10]
antardhasa_list = [6, 0, 8, 10, 4, 8, 6, 0, 8, 10, 4, 8]
dhasa_duration = 9


def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=9,
    chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 → 1=Maha only, 2=+Antara [default], 3..6 deeper
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Navāṁśa Daśā (depth-enabled)

    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)  [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

      • Seed daśā rāśi = dhasa_adhipati_list[Navāṁśa lagna sign].
      • Mahā sequence = 12 signs from seed forward; if seed is even, use the reversed style.
      • Antara rule (L2): child seed = `antardhasa_list[maha_rasi]`, then 12 rāśis forward from there.
      • JD advancement uses module-level `year_duration`, set by drik.dhasa_year_duration().

    Depth ≥ 3:
      • At every node, equal-split the immediate parent into 12 parts (Σchildren = parent),
        and use the same Antara rule but applied to the current parent:
           child order = 12 signs starting from `antardhasa_list[parent_rasi]`.

    Rounding:
      • Only the returned duration is rounded.
      • All JD/time math uses unrounded values (full precision).

    Returns:
      A flat list of tuples shaped per `dhasa_level_index`.
    """
    # ---- Safety guard on depth argument ---------------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- Chart and seed computation (unchanged logic) -------------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, chart_method=chart_method,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    # Navāṁśa lagna sign is at planet_positions[0][1][0]
    navamsa_lagna_sign = planet_positions[0][1][0]

    # Your original seed mapping: seed = dhasa_adhipati_list[lagna_sign]
    dhasa_seed = dhasa_adhipati_list[navamsa_lagna_sign]

    # Mahā sequence: default forward, but flip to your reversed construction if seed is even
    dhasa_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [(dhasa_seed + 6 - h + 12) % 12 for h in range(12)]

    # Helper: build 12-child order for ANY parent using antardhasa_list[parent]
    def _children_from(parent_rasi):
        bukthi_seed = antardhasa_list[parent_rasi]
        return [(bukthi_seed + h) % 12 for h in range(12)]

    # Recursion for depth ≥ 3: equal split of immediate parent into 12 Antara,
    # order from _children_from(parent)
    def _recurse(level, parent_rasi, parent_start_jd, parent_years, prefix, out_rows):
        child_years = parent_years / 12.0
        jd_cursor = parent_start_jd
        for child_rasi in _children_from(parent_rasi):
            if level < dhasa_level_index:
                _recurse(level + 1, child_rasi, jd_cursor, child_years, prefix + (child_rasi,), out_rows)
            else:
                # Leaf row at requested depth
                start_str = utils.jd_to_gregorian(jd_cursor)
                dur_out = round(child_years, dhasa_level_index + 1) if round_duration else child_years
                out_rows.append((prefix + (child_rasi,), start_str, dur_out))
            jd_cursor += child_years * year_duration

    # ---- Emit per requested depth --------------------------------------------
    rows = []
    start_jd = jd_at_dob

    for maha_rasi in dhasa_lords:
        md_years = float(dhasa_duration)  # your module constant (in years)

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Maha only
            rows.append((
                (maha_rasi,),
                utils.jd_to_gregorian(start_jd),
                round(md_years, dhasa_level_index + 1) if round_duration else md_years
            ))
            start_jd += md_years * year_duration

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antara — equal split of fixed Mahā duration; order from antardhasa_list[maha]
            ad_years = md_years / 12.0
            jd_b = start_jd
            for antara_rasi in _children_from(maha_rasi):
                rows.append((
                    (maha_rasi, antara_rasi),
                    utils.jd_to_gregorian(jd_b),
                    round(ad_years, dhasa_level_index + 1) if round_duration else ad_years
                ))
                jd_b += ad_years * year_duration
            # ΣAntara == Mahā → use end of Antara chain as next Mahā start
            start_jd = jd_b

        else:
            # L3..L6: recursive equal-split under the immediate parent
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,  # 2 → build 3..N
                parent_rasi=maha_rasi,
                parent_start_jd=start_jd,
                parent_years=md_years,
                prefix=(maha_rasi,),
                out_rows=rows
            )
            start_jd += md_years * year_duration

    return rows


def navamsa_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years  (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 9,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    FAST: Navāṁśa Daśā — return ONLY the immediate (parent -> children) splits,
    computed directly (no call to the base).

    Rules (your base logic):
      • L2 seed = antardhasa_list[parent_rasi]
      • Children = 12 rāśis forward from that seed
      • Sama split: child_years = parent_years / 12
      • Exact tiling on [parent_start, parent_end)
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")

    parent_rasi = path[-1]

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- resolve parent span (use selected module-level year_duration)
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    # ---- child order (no base call): antardhasa_list[parent] → 12 forward
    bukthi_seed = antardhasa_list[parent_rasi]
    children_signs = [(bukthi_seed + h) % 12 for h in range(12)]

    # ---- equal split & tiling
    child_years = parent_years / 12.0
    children = []
    cursor = start_jd

    # For speed, precompute increment in days
    incr_days = child_years * year_duration

    for i, sgn in enumerate(children_signs):
        child_end = end_jd if i == len(children_signs) - 1 else cursor + incr_days
        # Clip (robust if parent spans were fractional)
        if child_end > end_jd:
            child_end = end_jd
        if child_end > cursor:  # positive span only
            children.append([path + (sgn,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break

    # exact closure
    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 9,
    chart_method=1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Navāṁśa Daśā — running ladder at current_jd:
      [
        [(r1,),              start1, end1],
        [(r1,r2),            start2, end2],
        ...
        [(r1,..,r_d),        startd, endd]
      ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- depth normalization
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # ---- helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _to_periods(children_rows, parent_end_tuple):
        # children_rows: [[lords_tuple, start_tuple, end_tuple], ...]
        if not children_rows:
            return []
        rows = sorted(children_rows, key=lambda r: _tuple_to_jd(r[1]))
        proj = []
        for lords, st, en in rows:
            if (not proj) or (_tuple_to_jd(st) > _tuple_to_jd(proj[-1][1])):
                proj.append((lords, st))
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel end
        return proj

    # ---- Step 1: running Mahā via base (depth=1, unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    # Build periods + sentinel for selector
    periods = []
    jd_cursor = jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        periods.append((tuple(lords_tuple), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + float(dur_years) * year_duration
    periods.append((periods[-1][0], utils.jd_to_gregorian(jd_cursor)))  # sentinel

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Step 2+: deeper levels via immediate-children on the running parent
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = navamsa_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years, months=months, sixty_hours=sixty_hours,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            # represent “no deeper split” as zero-length at the boundary
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_periods(kids, parent_end)
        rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
        running = [tuple(rdk[0]), rdk[1], rdk[2]]
        ladder.append(running)

    return ladder


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)

    from datetime import datetime
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    import time
    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob, tob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.navamsa_dhasa_test()
