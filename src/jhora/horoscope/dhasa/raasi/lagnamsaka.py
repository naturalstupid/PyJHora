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
from jhora.horoscope.dhasa.raasi import narayana
from jhora.panchanga import drik

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


def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Lagnamsaka Daśā (depth-enabled; equal-split at each deeper level)

    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> (l1,               start_str, dur_units)
      2 = ANTARA               -> (l1, l2,           start_str, dur_units)    [DEFAULT]
      3 = PRATYANTARA          -> (l1, l2, l3,       start_str, dur_units)
      4 = SOOKSHMA             -> (l1, l2, l3, l4,   start_str, dur_units)
      5 = PRANA                -> (l1, l2, l3, l4, l5,   start_str, dur_units)
      6 = DEHA                 -> (l1, l2, l3, l4, l5, l6, start_str, dur_units)

    Units:
      • `_dhasa_duration(...)` returns daśā length in “years”.
      • JD math in this module uses `year_duration`, set by drik.dhasa_year_duration().
      • Narayana base calculation receives dhasa_duration_type/savana_year_method and handles its own JD math.
      • Returned `dur_units` are in the same “years” units you use today.

    Notes:
      • Mahā progression chosen by const.narayana_dhasa_*_progression with Ketu/Saturn exceptions.
      • Antar order at all depths comes from `_narayana_antardhasa(planet_positions, parent_rasi)`.
      • Deeper levels (>= L3) split the *immediate* parent evenly into 12 parts; Σ(children)=parent.
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    navamsa_planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=9)
    dhasa_seed_sign = navamsa_planet_positions[0][1][0]
    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs
    )[:const._pp_count_upto_ketu]
    return narayana._narayana_dhasa_calculation(
        planet_positions,
        dhasa_seed_sign,
        dob,
        tob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_level_index=dhasa_level_index,
        varsha_narayana=False,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


"""
Lagnāṁśaka Daśā — two helpers:
  • lagnamsaka_immediate_children(...)     # (p -> p+1) tiler
  • get_running_dhasa_for_given_date(...)  # step-down runner

Assumptions:
  • Your existing base Lagnāṁśaka entry is present:
      get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=1, years=1, months=1, sixty_hours=1,
                            dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA, round_duration=True)
    which computes the seed from Navāṁśa Lagna and delegates to Narayana.
  • Narayana module exports: _narayana_antardhasa(planet_positions, parent_rasi)
"""


def lagnamsaka_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (one of duration or end must be provided)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    # Keep knobs explicit for parity with your base:
    divisional_chart_factor: int = 1,
    chart_method: int = 1,       # not used by tiler (L1 only), kept for parity
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,        # L1-only knobs — ignored here
    round_duration: bool = False,   # tiler tiles exact spans; no rounding here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Lagnāṁśaka — return ONLY the immediate (p -> p+1) children inside the given parent span.

    Rules (identical to Narayana beyond the seed):
      • Child order at every level via Narayana antar: narayana._narayana_antardhasa(planet_positions, parent_sign)
      • Split rule: equal (parent_years / 12)  → Σ(children) = parent
      • Exact tiling: first child starts at parent_start; last child ends at parent_end
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")
    parent_sign = int(path[-1])

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- resolve parent span (years) and convert to [start_jd, end_jd]
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

    # ---- birth-epoch D1 positions for Narayana antar order
    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # child order from Narayana antar
    order = list(narayana._narayana_antardhasa(planet_positions, parent_sign))
    if not order:
        return []

    # ---- equal split & tiling within parent [start, end)
    child_years = parent_years / 12.0
    children = []
    cursor = start_jd
    for i, child_sign in enumerate(order):
        child_sign = int(child_sign)
        child_end = end_jd if i == 11 else cursor + child_years * year_duration
        children.append([path + (child_sign,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break

    # exact closure
    children[-1][2] = _jd_to_tuple(end_jd)
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    chart_method: int = 1,     # kept for signature parity
    round_duration: bool = False,   # runner operates on exact starts/ends
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Lagnāṁśaka — narrow Mahā -> … -> target depth and return the full running ladder:

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

    # ---- depth normalization
    def _normalize_depth(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target_depth = _normalize_depth(dhasa_level_index)

    # ---- helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ [lords_tuple, start_tuple, end_tuple], ... ]
        Returns: list of (lords_tuple, start_tuple) + sentinel(parent_end_tuple),
        filtering zero-length rows and enforcing strictly increasing starts.
        """
        flt = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds)]
        if not flt:
            return []
        flt.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _ in flt:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel
        return proj

    def _lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    running_all = []

    # ---- derive dob,tob for base L1 call
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    # ---- L1: Mahā via YOUR base (seeded from Navāṁśa Lagna)
    maha_rows = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    # normalize to (lords_tuple, start_tuple)
    maha_for_utils = [(_lords(row[0]), row[1]) for row in maha_rows]

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    # ---- L2..target: expand only the running parent via Narayana antar + equal split
    for depth in range(const.MAHA_DHASA_DEPTH.ANTARA, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = lagnamsaka_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years,
            months=months,
            sixty_hours=sixty_hours,
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
            current_jd,
            jd_at_dob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd,
            ad,
            const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=2
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.lagnamsaka_dhasa_test()
