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
from jhora.panchanga import drik
from jhora.horoscope.chart import house
from jhora.horoscope.dhasa.raasi import narayana
from jhora.horoscope.chart import charts

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


"""
    TODO: Book examples matches what is stated in PVR's book
    But same example data in JHora give different dhasa/bhukthi values
    Not Clear what JHora's algorithm is
"""


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    antardhasa_option=2,  # Sign or 7th
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,   # 1..6 (default: L2 = Maha + Antara)
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Entry point for Sudasa Dasha using dhasa_level_index.
    """
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type, savana_year_method)

    sl = drik.sree_lagna(jd, place, divisional_chart_factor=divisional_chart_factor)
    sree_lagna_house = sl[0]
    sree_lagna_longitude = sl[1]

    planet_positions = charts.divisional_chart(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs
    )[:const._pp_count_upto_ketu]
    return sudasa_dhasa_from_planet_positions(
        planet_positions=planet_positions,
        sree_lagna_house=sree_lagna_house,
        sree_lagna_longitude=sree_lagna_longitude,
        dob=dob,
        tob=tob,
        antardhasa_option=antardhasa_option,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration
    )


def sudasa_dhasa_from_planet_positions(
    planet_positions,
    sree_lagna_house,
    sree_lagna_longitude,
    dob,
    tob,
    antardhasa_option=2,  # Sign of 7th
    dhasa_level_index=2,  # 1..6; default L2 (Maha + Antara)
    round_duration=False
):
    """
    Calculate Sudasa Dasha up to the requested depth.

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
    """
    # --- Setup ---
    sl_frac_left = (30.0 - sree_lagna_longitude) / 30.0
    start_jd = utils.julian_day_number(dob, tob)

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    # Direction: odd → forward; even → backward
    direction = 1 if (sree_lagna_house in const.odd_signs) else -1
    # Exceptions
    if p_to_h[const.SATURN_ID] == sree_lagna_house:
        direction = 1
    elif p_to_h[const.KETU_ID] == sree_lagna_house:
        direction *= -1

    # Kendra-based MD sequence (as in your code)
    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [(sree_lagna_house + direction * (k - 1)) % 12 for k in ks]

    dhasa_info = []
    md_years_cycle1 = []  # store first-cycle MD years (unrounded), after SL fraction for c==0

    # --- Helpers ---
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append one leaf row and advance time by seg_duration_years.
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, dhasa_level_index + 1
        )
        dhasa_info.append((
            tuple(lords_stack),
            utils.jd_to_gregorian(start_jd_val),
            disp_dur
        ))
        return start_jd_val + seg_duration_years * year_duration

    def _child_sequence(planet_positions, parent_lord, antardhasa_option=1):
        """
        L2 direction/order (and deeper) determined by parent's placement,
        via your existing _antardhasa logic.
        """
        return _antardhasa(planet_positions, parent_lord, antardhasa_option=antardhasa_option)

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a node:
          • If current_level == target_level: append one leaf for the entire segment.
          • Else: split evenly among 12 children ordered by _child_sequence.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence(planet_positions, parent_lord, antardhasa_option=antardhasa_option)
        child_duration = parent_duration_years / 12.0  # Lx = L(x-1)/12 equal split

        for child_lord in children:
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # --- First cycle ---
    for idx, md_lord in enumerate(dhasa_progression):
        md_years = narayana._dhasa_duration(planet_positions, md_lord)  # L1 only
        if idx == 0:
            md_years *= sl_frac_left  # fraction left in SL at birth

        md_years_cycle1.append(md_years)

        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    # --- Second cycle (preserve your basis rules & depth dependency) ---
    # Start with the total from the first cycle (as your original code did)
    total_dhasa_duration = sum(row[-1] for row in dhasa_info)

    depth_divisor = (12 ** (dhasa_level_index - 1))

    for c, md_lord in enumerate(dhasa_progression):
        if dhasa_level_index == 1:
            basis = narayana._dhasa_duration(planet_positions, md_lord) if c == 0 else md_years_cycle1[c]
        else:
            if c == 0:
                basis = narayana._dhasa_duration(planet_positions, md_lord) / depth_divisor
            else:
                basis = md_years_cycle1[c] / depth_divisor

        md2_years = 12.0 - basis
        if md2_years <= 0:
            continue

        total_dhasa_duration += md2_years

        start_jd = _expand_children(
            start_jd,
            md2_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    return dhasa_info


def _antardhasa(planet_positions, dhasa_lord, antardhasa_option=1):
    """
        antardhasa_option
            1 =>    Regular from dhasa sign  (odd=>Backward, Even=>Forward)
            2 =>    Regular from stronger of dhasa sign or 7th (odd=>Backward, Even=>Forward)
            3 =>    Quadrants from dhasa sign  (odd=>Backward, Even=>Forward)
            4 =>    Quadrants from stronger of dhasa or 7th  (odd=>Backward, Even=>Forward)
            5 =>    Like Narayana dhasa
        NOTE: JHora V8.0 options dialog says opposite but s/w shows Odd>Backward Even>Forward
    """
    dhasa_lord_7th = (dhasa_lord + const.HOUSE_7) % 12
    seed = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_lord, dhasa_lord_7th)
    if antardhasa_option == 1:
        dirn = 1 if dhasa_lord in const.even_signs else -1
        return [(dhasa_lord + dirn * h) % 12 for h in range(12)]
    elif antardhasa_option == 2:
        dirn = 1 if seed in const.even_signs else -1
        return [(seed + dirn * h) % 12 for h in range(12)]
    elif antardhasa_option == 3:
        q, s = house.quadrants_of_the_raasi, dhasa_lord % 12
        order_fwd = q(s) + sorted(q((s + 1) % 12)) + sorted(q((s + 2) % 12))
        order = order_fwd if s in const.even_signs else [s] + list(reversed(order_fwd[1:]))
        return order
    elif antardhasa_option == 4:
        q, s = house.quadrants_of_the_raasi, seed % 12
        order_fwd = q(s) + sorted(q((s + 1) % 12)) + sorted(q((s + 2) % 12))
        order = order_fwd if s in const.even_signs else [s] + list(reversed(order_fwd[1:]))
        return order
    else:
        try:
            from jhora.horoscope.dhasa.raasi.narayana import _narayana_antardhasa
        except Exception:
            raise ImportError("jhora.horoscope.dhasa.raasi.narayana._narayana_antardhasa not found")
        return _narayana_antardhasa(planet_positions, dhasa_lord)


def __antardhasa(antardhasa_seed_rasi, p_to_h):
    direction = -1
    if p_to_h[const.SATURN_ID] == antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs:  # Forward
        direction = 1
    if p_to_h[const.KETU_ID] == antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi + direction * i) % 12 for i in range(12)]


def sudasa_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    antardhasa_option: int = 2,  # Sign or 7th
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sudāśā — return ONLY the immediate (parent -> 12 children) splits for the given parent span.

    Output rows:
      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

    # resolve parent span
    start_jd = _t2jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _t2jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    # zero-span parent → no children
    if end_jd <= start_jd:
        return []

    # positions @ birth
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # child order via your optioned _antardhasa
    order = _antardhasa(planet_positions, parent_sign, antardhasa_option=antardhasa_option)

    # equal split & exact tiling
    child_years = parent_years / 12.0
    rows, cursor = [], start_jd
    for i, sgn in enumerate(order):
        child_end = end_jd if i == 11 else cursor + child_years * year_duration
        if child_end > cursor:  # skip degenerate zero-length
            rows.append((path + (sgn,), _jd2t(cursor), _jd2t(child_end)))
        cursor = child_end
        if cursor >= end_jd:
            break

    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd2t(end_jd))
    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,   # 1..6
    *,
    divisional_chart_factor: int = 1,
    antardhasa_option: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sudāśā — running ladder at `current_jd`:

      [
        [(L1,),                  start1, end1],
        [(L1,L2),                start2, end2],
        ...
        [(L1,..,L_d),            startd, endd]
      ]

    Notes:
      • L1 is sourced from your base `get_dhasa_bhukthi(..., dhasa_level_index=MAHA_DHASA_ONLY)`.
      • Children are expanded via `sudasa_immediate_children(...)`.
      • Zero-duration intervals are skipped in selector period-lists.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # depth normalize
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

    # zero-length checks
    def _is_zero_by_start_dur(start_tuple, dur_years, eps_seconds=1e-3):
        if dur_years <= 0.0:
            return True
        return (dur_years * year_duration * 86400.0) <= eps_seconds

    def _to_selector_periods_zero_safe(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ (lords_tuple, start_tuple, end_tuple), ... ]
        -> strictly increasing [(lords, start), ..., sentinel(parent_end)]
        """
        if not children_rows:
            return []
        rows = []
        for lt, st, en in children_rows:
            if (_t2jd(en) - _t2jd(st)) * 86400.0 > eps_seconds:
                rows.append((lt, st))
        if not rows:
            return []
        rows.sort(key=lambda r: _t2jd(r[1]))
        proj, prev = [], None
        for lt, st in rows:
            sj = _t2jd(st)
            if prev is None or sj > prev:
                proj.append((lt, st))
                prev = sj
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel
        return proj

    # 1) L1 MD via your base (unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    l1_rows = get_dhasa_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        antardhasa_option=antardhasa_option,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # build (lords,start)+sentinel for selector — skip 0-year MDs
    periods, jd_cursor = [], jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in l1_rows:
        dur = float(dur_years)
        if _is_zero_by_start_dur(start_tuple, dur):
            continue
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _t2jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd2t(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd2t(jd_cursor)))  # sentinel end

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # 2) Expand only the running parent at each deeper level
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = sudasa_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            antardhasa_option=antardhasa_option,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        child_periods = _to_selector_periods_zero_safe(kids, parent_end_tuple=parent_end)
        if not child_periods:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        rdk = utils.get_running_dhasa_for_given_date(current_jd, child_periods)
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
    _dhasa_cycle_count = 2
    _ant_option = 2
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Maha        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            antardhasa_option=_ant_option,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            dob, tob, place,
            dhasa_level_index=DLI,
            antardhasa_option=_ant_option,
            dhasa_duration_type=dd
        )
        """
        for row in ad:
            lords, ds, dur = row
            print([utils.RAASI_LIST[lord] for lord in lords], ds, dur)
        exit()
        """
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=_dhasa_cycle_count
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.sudasa_tests()
