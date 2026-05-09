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
    Chaturvidha Uttara Dasha
        Lagna Uttara Dasha  -> Start from Lagna (Ascendant Rashi) - Dhasa Method = 1
        Kendra Uttara Dasha -> Start from strongest Kendra (1st, 4th, 7th, 10th house Rashi) - Dhasa Method = 2
        Trikona Uttara Dasha -> Start from strongest Trikona (1st, 5th, 9th house Rashi) - Dhasa Method = 3
        Dasha Uttara Dasha -> Start from Rashi with the strongest planetary influence - Dhasa Method = 4
"""
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year


def valid_methods_available_for_planet_positions(planet_positions):
    """
        It is possible the seed may be same for some/all of these methods.
        This function returns unique method numbers in such cases.
    """
    asc_house = planet_positions[0][1][0]
    _seeds = {}
    _seeds[1] = asc_house
    raasi_list = house.quadrants_of_the_raasi(asc_house)
    _seeds[2] = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    raasi_list = house.trines_of_the_raasi(asc_house)
    _seeds[3] = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    raasi_list = [(asc_house + h) % 12 for h in range(12)]
    _seeds[4] = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    unique_methods = list(set({v: k for k, v in _seeds.items()}.values()))
    return unique_methods


def _dhasa_progression_and_duration(planet_positions, dhasa_method=1):
    """
    Returns a dict {raasi: duration_weight} for the chosen Uttara Dasha method.
    """
    asc_house = planet_positions[0][1][0]
    if dhasa_method == 1:
        _seed = asc_house
    elif dhasa_method == 2:
        raasi_list = house.quadrants_of_the_raasi(asc_house)
        _seed = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    elif dhasa_method == 3:
        raasi_list = house.trines_of_the_raasi(asc_house)
        _seed = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    else:
        raasi_list = [(asc_house + h) % 12 for h in range(12)]
        _seed = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    return {(_seed + h) % 12: h + 1 for h in range(12)}


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    method=1,
    chart_method=1,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns a flat list of the lowest-level entries:
      [ [raasi_path], (y, m, d, fh), duration_years ], ...
    where raasi_path contains raasi indices (0..11) per level.
    """
    global year_duration

    SUM_W = 78.0

    def _sanitize_depth(depth):
        try:
            d = int(depth)
        except Exception:
            d = 2
        return max(1, min(6, d))

    def _progression_from_seed(seed):
        return [(seed + h) % 12 for h in range(12)]

    def _weights_for_progression(prog):
        return {r: (i + 1) for i, r in enumerate(prog)}

    def _build_level(prog, weights, parent_days):
        return [(r, parent_days * weights[r] / SUM_W) for r in prog]

    def _seed_for_method(planet_positions, asc_house, method):
        if method == 1:
            return asc_house
        elif method == 2:
            return house.stronger_raasi_from_list_of_raasis(
                planet_positions, house.quadrants_of_the_raasi(asc_house)
            )
        elif method == 3:
            return house.stronger_raasi_from_list_of_raasis(
                planet_positions, house.trines_of_the_raasi(asc_house)
            )
        elif method == 4:
            return house.stronger_raasi_from_list_of_raasis(
                planet_positions, [(asc_house + h) % 12 for h in range(12)]
            )
        else:
            raise ValueError(f"Unknown method: {method}")

    jd_at_dob = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    top_total_days = 78.0 * year_duration

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs,
    )

    asc_house = planet_positions[0][1][0]
    seed = _seed_for_method(planet_positions, asc_house, method)

    depth = _sanitize_depth(dhasa_level_index)
    rows = []

    def _recurse(current_seed, start_jd, parent_days, level, path):
        prog = _progression_from_seed(current_seed)
        weights = _weights_for_progression(prog)
        items = _build_level(prog, weights, parent_days)

        rolling_jd = start_jd
        for r, d_days in items:
            seg_start_jd = rolling_jd
            rolling_jd += d_days
            if level == 1:
                rows.append((path + [r], seg_start_jd, d_days))
            else:
                _recurse(r, seg_start_jd, d_days, level - 1, path + [r])

    _recurse(seed, jd_at_dob, top_total_days, depth, [])

    results = []
    for raasi_path, start_jd, d_days in rows:
        y, m, d, fh = utils.jd_to_gregorian(start_jd)
        dur_years = d_days / year_duration
        rd = round(dur_years, dhasa_level_index + 1) if round_duration else dur_years
        results.append([raasi_path, (y, m, d, fh), rd])

    return results


def chathurvidha_utthara_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    dhasa_method: int = 1,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Chathurvidha Utthara — return ONLY the immediate (p -> p+1) children under the given parent span.

    Rules:
      • At each level, RESEED from the parent sign: progression = [parent, parent+1, ..., wrap].
      • Weights 1..12 map to the progression order; split parent by weights proportional to (1..12)/78.
      • Exact tiling: first child starts at parent_start; last child ends at parent_end.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")

    parent_sign = path[-1]

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

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

    sum_w = 78.0
    progression = [(parent_sign + h) % 12 for h in range(12)]
    weights = {r: (i + 1) for i, r in enumerate(progression)}

    children = []
    jd_cursor = start_jd
    for i, r in enumerate(progression):
        share_years = parent_years * (weights[r] / sum_w)
        if i == len(progression) - 1:
            child_end = end_jd
        else:
            child_end = jd_cursor + share_years * year_duration

        children.append([
            path + (r,),
            _jd_to_tuple(jd_cursor),
            _jd_to_tuple(child_end),
        ])
        jd_cursor = child_end
        if jd_cursor >= end_jd:
            break

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    dhasa_method: int = 1,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Chathurvidha Utthara — narrow Mahā -> … -> target depth and return the full running ladder.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds)]
        if not filtered:
            return []
        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _en in filtered:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    running_all = []

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    maha_rows = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        method=dhasa_method,
        chart_method=chart_method,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )

    maha_for_utils = []
    for raasi_path, start_t, _dur_years in maha_rows:
        lords_tuple = tuple(raasi_path) if isinstance(raasi_path, list) else _as_tuple_lords(raasi_path)
        maha_for_utils.append((lords_tuple, start_t))

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_as_tuple_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = chathurvidha_utthara_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            dhasa_method=dhasa_method,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )

        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            break

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            running = [_as_tuple_lords(rdk[0]), rdk[1], rdk[2]]

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
    _dhasa_method = 4
    import time
    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        print(
            "Dehā        :",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_method=_dhasa_method,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            method=_dhasa_method,
            dhasa_duration_type=dd,
        )
        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
            )
        )
        print('old method elapsed time', time.time() - start_time)
    exit()
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.03862, 80.261818, 5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    dcf = 1
    pp = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=dcf)
    print(valid_methods_available_for_planet_positions(pp))
    cd = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        divisional_chart_factor=dcf,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
        method=4,
    )
    for row in cd:
        print(row)
