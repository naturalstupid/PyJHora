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
"""
Lagna–Kendrādhi Rāśi Daśā — public runner + immediate-children,
designed to work alongside your existing base generator.

Exports:
  • lagna_kendradhi_immediate_children(...)
  • get_running_dhasa_for_given_date(...)

Usage with importlib:
  - module: jhora.horoscope.dhasa.raasi.lagna_kendradhi_rasi
  - function: get_running_dhasa_for_given_date
"""

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house
from jhora.horoscope.dhasa.raasi.narayana import _dhasa_duration as narayana_dhasa_duration

# Module-level year basis. Public entry points refresh this via drik.dhasa_year_duration().
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


def _antardhasa(antardhasa_seed_rasi, p_to_h):
    direction = -1
    if p_to_h[const.SATURN_ID] == antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs:  # Forward
        direction = 1
    if p_to_h[const.KETU_ID] == antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi + direction * i) % 12 for i in range(12)]


def lagna_kendradhi_rasi_dhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    return kendradhi_rasi_dhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


def kendradhi_rasi_dhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Kendraadhi Rāśi Daśā with multi-level depth (Maha → Antara → …)

    Depth control:
      1 = MAHA_DHASA_ONLY          -> (l1,                 start_str, dur_years)
      2 = ANTARA                   -> (l1, l2,             start_str, dur_years)  [DEFAULT]
      3 = PRATYANTARA              -> (l1, l2, l3,         start_str, dur_years)
      4 = SOOKSHMA                 -> (l1, l2, l3, l4,     start_str, dur_years)
      5 = PRANA                    -> (l1, l2, l3, l4, l5, start_str, dur_years)
      6 = DEHA                     -> (l1, l2, l3, l4, l5, l6, start_str, dur_years)

    Seed & Direction (unchanged):
      • Seed: stronger of Asc & 7th (house.stronger_rasi_from_planet_positions).
      • Direction: Saturn in seed ⇒ forward; Ketu in seed ⇒ backward; else odd forward / even backward.
      • Progression: by first 3 kendras (house.kendras()[:3]) mapped from seed in the chosen direction.

    Durations:
      • Mahā duration (cycle 1): narayana._dhasa_duration(planet_positions, rasi).
      • Two cycles always:
          – Cycle 1: use first duration.
          – Cycle 2: duration = max(12.0 − first_duration, 0.0).
      • No life-span cutoff; do not stop early.
      • If duration is 0.0 at any level, still include the period in the output with:
          (lords_tuple, dhasa_start, 0.0). Start date does not advance for zero periods.

    Antara ordering:
      • At any node: _antardhasa(parent_sign, p_to_h).
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
    )[:const._pp_count_upto_ketu]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house + const.HOUSE_7) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(
        planet_positions, asc_house, seventh_house
    )

    # Direction
    if p_to_h[const.SATURN_ID] == dhasa_seed_sign:
        direction = 1
    elif p_to_h[const.KETU_ID] == dhasa_seed_sign:
        direction = -1
    elif dhasa_seed_sign in const.odd_signs:
        direction = 1
    else:
        direction = -1

    # Progression from first 3 kendras (1,4,7), mapped from seed
    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [(dhasa_seed_sign + direction * (k - 1)) % 12 for k in ks]

    # Helpers
    def _children(parent_sign):
        """12 children from parent sign using antar ordering."""
        return _antardhasa(parent_sign, p_to_h)

    def _emit_period(lords_tuple, start_jd, dur_years, out_rows):
        """Append output row and advance cursor by duration (even if 0)."""
        start_str = utils.jd_to_gregorian(start_jd)
        dur_out = round(dur_years, dhasa_level_index + 1) if round_duration else dur_years
        out_rows.append((lords_tuple, start_str, dur_out))
        return start_jd + dur_years * year_duration  # advances 0 for zero durations

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        child_years = parent_years / 12.0
        jd_cursor = parent_start_jd
        for child_sign in _children(parent_sign):
            if level < dhasa_level_index:
                _recurse(level + 1, child_sign, jd_cursor, child_years, prefix + (child_sign,), out_rows)
                jd_cursor += child_years * year_duration
            else:
                jd_cursor = _emit_period(prefix + (child_sign,), jd_cursor, child_years, out_rows)
        # jd_cursor implicitly advanced (or not) by child_years each step

    rows = []
    start_jd = jd_at_dob

    # ---------------------- Cycle #1 ----------------------
    for dhasa_lord in dhasa_progression:
        dd = float(narayana_dhasa_duration(planet_positions, dhasa_lord))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            start_jd = _emit_period((dhasa_lord,), start_jd, dd, rows)

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                jd_b = _emit_period((dhasa_lord, bhukthi_lord), jd_b, ddb, rows)
            start_jd = jd_b

        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd, (dhasa_lord,), rows)
            start_jd += dd * year_duration

    # ---------------------- Cycle #2 ----------------------
    for dhasa_lord in dhasa_progression:
        first_dd = float(narayana_dhasa_duration(planet_positions, dhasa_lord))
        dd2 = 12.0 - first_dd
        if dd2 < 0.0:
            dd2 = 0.0  # include as zero-duration; do not skip

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            start_jd = _emit_period((dhasa_lord,), start_jd, dd2, rows)

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd2 / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                jd_b = _emit_period((dhasa_lord, bhukthi_lord), jd_b, ddb, rows)
            start_jd = jd_b

        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd2, (dhasa_lord,), rows)
            start_jd += dd2 * year_duration

    return rows


def get_lagna_kendradhi_rasi_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    return lagna_kendradhi_rasi_dhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


# ============================================================
# PUBLIC: immediate children (p -> p+1) for Lagna variant
# ============================================================
def lagna_kendradhi_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    round_duration: bool = False,    # tiler returns exact spans; do not round here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Lagna–Kendrādhi Rāśi — return ONLY the immediate (p -> p+1) children under the given parent span.

    Strategy:
      1) PURE-TILER (fast): if optional `_children_order_lagna` is defined, compute child order (+weights)
         from birth-epoch positions; split equal/proportional; tile exact [start, end).
      2) BASE-FILTER (safe): call your base at depth (k+1) anchored at birth; filter subtree for this parent;
         clip to [parent_start, parent_end).
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]
    k = len(path)  # depth of parent

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- parent span
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    # ---- PURE-TILER attempt (if helper exists)
    order_func = globals().get("_children_order_lagna")
    if callable(order_func):
        # birth-epoch positions
        planet_positions = charts.divisional_chart(
            jd_at_dob, place, divisional_chart_factor, chart_method=chart_method, **kwargs
        )[:const._pp_count_upto_ketu]

        order, weights = None, None
        try:
            out = order_func(parent_sign, planet_positions, **kwargs)
            if isinstance(out, tuple) and len(out) == 2:
                order, weights = list(out[0]), list(out[1])
            else:
                order = list(out)
        except Exception:
            order = None

        if order:
            if weights is not None:
                W = float(sum(weights)) or 1.0
                child_years_list = [parent_years * (w / W) for w in weights[:len(order)]]
            else:
                child_years_list = [parent_years / float(len(order))] * len(order)

            out_rows, cursor = [], start_jd
            n = min(len(order), len(child_years_list))
            for i in range(n):
                cs = int(order[i])
                cy = float(child_years_list[i])
                child_end = end_jd if i == n - 1 else cursor + cy * year_duration
                out_rows.append([path + (cs,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
                cursor = child_end
                if cursor >= end_jd:
                    break
            if out_rows:
                out_rows[-1][2] = _jd_to_tuple(end_jd)
            return out_rows

    # ---- BASE-FILTER fallback: call base at depth k+1, anchored at birth JD
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    base_rows = get_lagna_kendradhi_rasi_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=k + 1,
        round_duration=False,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    if not base_rows:
        return []

    children = []
    for row in base_rows:
        labels = tuple(row[0]) if isinstance(row[0], (tuple, list)) else (row[0],)
        if len(labels) != k + 1 or tuple(labels[:k]) != path:
            continue
        sjd = _tuple_to_jd(row[1])
        if sjd < start_jd:
            continue
        if sjd >= end_jd:
            break
        dur_y = float(row[2])
        ejd = sjd + dur_y * year_duration
        if ejd > end_jd:
            ejd = end_jd
        children.append([labels, _jd_to_tuple(sjd), _jd_to_tuple(ejd)])

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


# ============================================================
# PUBLIC: Runner (Mahā -> … -> target depth) for Lagna variant
# ============================================================
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    star_position_from_moon: int = 1,
    dhasa_starting_planet: int = 1,
    round_duration: bool = False,  # runner operates on exact (start,end)
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Lagna–Kendrādhi Rāśi — narrow Mahā -> … -> target depth and return the full running ladder:

      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        [(l1,l2,l3),         start3, end3],
        [(l1,l2,l3,l4),      start4, end4],
        [(l1,l2,l3,l4,l5),   start5, end5],
        [(l1,l2,l3,l4,l5,l6),start6, end6],
      ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize depth
    def _normalize_depth(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target_depth = _normalize_depth(dhasa_level_index)

    # helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps

    def _to_utils_periods(children_rows, parent_end_tuple, eps=1.0):
        flt = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps)]
        if not flt:
            return []
        flt.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _ in flt:
            sj = _tuple_to_jd(st)
            if prev is None or sj > prev:
                proj.append((lords, st))
                prev = sj
        # sentinel to bound the last interval
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    def _lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    running_all = []

    # L1 via your base (anchored at birth JD, unrounded)
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    maha_rows = get_lagna_kendradhi_rasi_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    maha_for_utils = [(_lords(row[0]), row[1]) for row in maha_rows]

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    # Levels 2..target: expand only the running parent each step
    for _depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = lagna_kendradhi_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            break

        periods = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
            running = [_lords(rdk[0]), rdk[1], rdk[2]]

        running_all.append(running)

    return running_all


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
        ad = lagna_kendradhi_rasi_dhasa(
            dob, tob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=2
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kendradhi_rasi_test()
