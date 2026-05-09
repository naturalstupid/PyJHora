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
from functools import lru_cache

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

# Module-level year basis. Public entry points refresh this using either:
#   - drik.dhasa_year_duration(...), when a duration type is explicitly requested, OR
#   - the Sudharshana tropical/sidereal selector when use_sidereal is used.
year_duration = const.sidereal_year
_SIDEREAL_YEAR = year_duration
_TROPICAL_YEAR = getattr(const, "tropical_year", 365.24219052)


def _set_year_duration(jd, place, *, use_sidereal=False, dhasa_duration_type=None, savana_year_method=None):
    """Set module-level year_duration consistently for all JD math in this module."""
    global year_duration

    if dhasa_duration_type is not None or savana_year_method is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )
    else:
        year_duration = _SIDEREAL_YEAR if use_sidereal else _TROPICAL_YEAR
    return year_duration


def sudharshana_chakra_chart(jd_at_dob, place, dob, years_from_dob=1, divisional_chart_factor=1,
                             chart_method=1, use_sidereal=False, dhasa_duration_type=None,
                             savana_year_method=None, **kwargs):
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    jd_at_years = drik.next_solar_date(
        jd_at_dob, place, years=years_from_dob, use_sidereal=use_sidereal
    )
    planet_positions = charts.divisional_chart(
        jd_at_years, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )
    retrograde_planets = drik.planets_in_retrograde(jd_at_years, place)
    natal_chart = utils.get_house_planet_list_from_planet_positions(planet_positions)

    lagna_house = planet_positions[0][1][0]
    moon_house = planet_positions[2][1][0]
    sun_house = planet_positions[1][1][0]

    lagna_chart = [((p + lagna_house) % 12, natal_chart[(p + lagna_house) % 12]) for p in range(12)]
    moon_chart = [((p + moon_house) % 12, natal_chart[(p + moon_house) % 12]) for p in range(12)]
    sun_chart = [((p + sun_house) % 12, natal_chart[(p + sun_house) % 12]) for p in range(12)]

    return [lagna_chart, moon_chart, sun_chart, retrograde_planets]


def _sudharsana_antardhasa_seeds(dhasa_triple, planet_positions=None, antardhasa_from_lord_of_dhasa_sign=False):
    dl1, dl2, dl3 = dhasa_triple
    if not antardhasa_from_lord_of_dhasa_sign:
        return [[(dl1 + h) % 12, (dl2 + h) % 12, (dl3 + h) % 12] for h in range(12)]

    antardhasa_lords = [const._house_owners_list[ds] for ds in dhasa_triple]
    antardhasa_triple = [planet_positions[al + 1][1][0] for al in antardhasa_lords]
    dl1, dl2, dl3 = antardhasa_triple
    return [[(dl1 + h) % 12, (dl2 + h) % 12, (dl3 + h) % 12] for h in range(12)]


def get_dhasa_bhukthi(
    jd_at_dob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6
    antardhasa_from_lord_of_dhasa_sign=False,
    years_from_dob=1,
    chart_method=1,
    use_sidereal=False,
    dhasa_cycles=9,                 # repeat 12-year wheel dhasa_cycles times (9 => 108 years)
    max_rows=None,                  # optional safety guard
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Returns rows shaped as:
      [ [triple_lvl1, triple_lvl2, ..., triple_lvlN], (Y, M, D, fractional_hours), duration_in_years ]

    Where each triple is a tuple: (lagna_house, moon_house, sun_house) for that level.

    Notes
    -----
    - Sudharsana Chakra is a 12-year cyclic progression; dhasa_cycles repeats the same 12-year wheel.
    - Be careful with very deep levels:
        total_rows = dhasa_cycles * (12 ** depth)
      depth=6 and dhasa_cycles=9 => ~26.9M rows (huge). Prefer the runner for deep queries.
    """
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # --- Depth clamp 1..6
    try:
        depth = int(dhasa_level_index)
    except Exception:
        depth = const.MAHA_DHASA_DEPTH.ANTARA
    depth = max(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, min(depth, const.MAHA_DHASA_DEPTH.DEHA))

    # --- cycles clamp
    try:
        dhasa_cycles = int(dhasa_cycles)
    except Exception:
        dhasa_cycles = 9
    dhasa_cycles = max(1, dhasa_cycles)

    # --- guard against accidental huge generations
    total_rows = dhasa_cycles * (12 ** depth)
    if max_rows is not None and total_rows > int(max_rows):
        raise ValueError(
            f"Requested {total_rows} rows (dhasa_cycles={dhasa_cycles}, depth={depth}) "
            f"exceeds max_rows={max_rows}. Use the runner for deep levels."
        )

    # --- Base chart roots (Lagna, Moon, Sun)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )
    lagna_house = planet_positions[0][1][0]
    moon_house = planet_positions[const.MOON_ID + 1][1][0]
    sun_house = planet_positions[const.SUN_ID + 1][1][0]
    base_triple = (lagna_house, moon_house, sun_house)

    # --- Anchor (kept as in your code)
    jd0 = drik.next_solar_date(
        jd_at_dob, place, years=years_from_dob, use_sidereal=use_sidereal
    )

    # leaf period size in JD
    step_jd = year_duration / (12 ** (depth - 1))
    duration_years = 1.0 / (12 ** (depth - 1))

    def _roll_triple(tri, k):
        return ((tri[0] + k) % 12, (tri[1] + k) % 12, (tri[2] + k) % 12)

    @lru_cache(maxsize=None)
    def _seeds_for(tri):
        seed_list = _sudharsana_antardhasa_seeds(
            list(tri),
            planet_positions=planet_positions,
            antardhasa_from_lord_of_dhasa_sign=antardhasa_from_lord_of_dhasa_sign
        )
        return tuple(tuple(s) for s in seed_list)

    def _weight(level_1_based):
        return 12 ** (depth - level_1_based)

    results = []

    def _recurse(level, parent_triple, path_triples, k_so_far):
        if level == 1:
            w = _weight(level)
            for i1 in range(12):
                triple1 = _roll_triple(parent_triple, i1)
                k1 = k_so_far + i1 * w
                if depth == 1:
                    start_jd = jd0 + k1 * step_jd
                    results.append([[triple1], utils.jd_to_gregorian(start_jd), duration_years])
                else:
                    _recurse(level + 1, triple1, [triple1], k1)
            return

        seeds = _seeds_for(parent_triple)
        w = _weight(level)
        for i in range(12):
            triple_i = seeds[i]
            k_i = k_so_far + i * w
            new_path = path_triples + [triple_i]
            if level == depth:
                start_jd = jd0 + k_i * step_jd
                results.append([new_path, utils.jd_to_gregorian(start_jd), duration_years])
            else:
                _recurse(level + 1, triple_i, new_path, k_i)

    # loop cycles; each cycle adds a flat-index offset of (12**depth)
    cycle_span_k = 12 ** depth
    for c in range(dhasa_cycles):
        cycle_offset_k = c * cycle_span_k
        _recurse(level=1, parent_triple=base_triple, path_triples=[], k_so_far=cycle_offset_k)

    return results


def sudharsana_chakra_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fh)
    parent_duration_years=None,  # float years (optional)
    parent_end=None,             # (Y, M, D, fh) (optional)
    antardhasa_option=1,         # kept for signature compatibility
    *,
    jd_at_dob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    use_sidereal=False,
    antardhasa_from_lord_of_dhasa_sign=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sudharshana Chakra – return ONLY the immediate (p->p+1) children under a given parent span.

    Output rows:
        [ (lords_tuple_with_child), child_start_tuple, child_end_tuple ]

    Notes:
      • Children count is always 12.
      • Child triples come from _sudharsana_antardhasa_seeds(parent_triple, ...).
      • Duration split is equal: parent_span / 12.
      • Last child end is forced to parent_end (tiling closure).
    """
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- normalize lords path
    if isinstance(parent_lords, tuple):
        path = parent_lords
    elif isinstance(parent_lords, list):
        path = tuple(parent_lords)
    else:
        raise TypeError("parent_lords must be tuple/list (path of triples).")

    if len(path) == 0:
        raise ValueError("parent_lords cannot be empty")

    parent_triple = path[-1]  # (lagna_house, moon_house, sun_house)

    # ---- tuple <-> JD helpers (your canonical form)
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- parent start/end in JD
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration_years is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration_years or parent_end.")

    if parent_end is None:
        end_jd = start_jd + float(parent_duration_years) * year_duration
        parent_end = _jd_to_tuple(end_jd)
    else:
        end_jd = _tuple_to_jd(parent_end)

    if end_jd <= start_jd:
        return []

    # ---- planet_positions needed only if antardhasa_from_lord_of_dhasa_sign=True
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )

    child_triples = _sudharsana_antardhasa_seeds(
        list(parent_triple),
        planet_positions=planet_positions,
        antardhasa_from_lord_of_dhasa_sign=antardhasa_from_lord_of_dhasa_sign
    )
    child_triples = [tuple(ct) for ct in child_triples]

    # ---- equal split into 12 children inside parent span
    step = (end_jd - start_jd) / 12.0
    children = []
    cursor = start_jd

    for i, child_triple in enumerate(child_triples):
        child_end_jd = end_jd if i == 11 else cursor + step
        children.append([
            path + (child_triple,),
            _jd_to_tuple(cursor),
            _jd_to_tuple(child_end_jd),
        ])
        cursor = child_end_jd
        if cursor >= end_jd:
            break

    # force closure
    if children:
        children[-1][2] = _jd_to_tuple(end_jd)

    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    years_from_dob=1,
    use_sidereal=False,
    antardhasa_from_lord_of_dhasa_sign=False,
    dhasa_cycles=9,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sudharshana Chakra – narrow Mahā → … → target depth and return the full ladder:

        [
          [((t1,),)           start1, end1],
          [((t1,t2),)         start2, end2],
          ...
        ]
    """
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- clamp depth
    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = const.MAHA_DHASA_DEPTH.DEHA
    target_depth = max(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, min(const.MAHA_DHASA_DEPTH.DEHA, target_depth))

    # ---- tuple<->JD (your canonical conversion)
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ [lords_tuple, start_tuple, end_tuple], ... ]
        Returns: list of (lords_tuple, start_tuple) + sentinel, filtering zero-length,
        enforcing strictly increasing starts.
        """
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds)]
        if not filtered:
            return []

        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))

        proj = []
        prev = None
        for lords, st, _en in filtered:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd

        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    running_all = []

    # ---- Level 1: Mahā starts from the SCD generator (depth=1) over dhasa_cycles
    maha_rows = get_dhasa_bhukthi(
        jd_at_dob=jd_at_dob,
        place=place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        antardhasa_from_lord_of_dhasa_sign=antardhasa_from_lord_of_dhasa_sign,
        years_from_dob=years_from_dob,
        chart_method=chart_method,
        use_sidereal=use_sidereal,
        dhasa_cycles=dhasa_cycles,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )

    if not maha_rows:
        sentinel = utils.jd_to_gregorian(jd_at_dob)
        return [[(), sentinel, sentinel]]

    maha_for_utils = [((row[0][0],), row[1]) for row in maha_rows]

    # Running Mahā
    rd = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [tuple(rd[0]), rd[1], rd[2]]
    running_all.append(running)

    if target_depth == 1:
        return running_all

    # ---- Levels 2..target
    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = sudharsana_chakra_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            use_sidereal=use_sidereal,
            antardhasa_from_lord_of_dhasa_sign=antardhasa_from_lord_of_dhasa_sign,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )

        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            continue

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rd_k = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            running = [tuple(rd_k[0]), rd_k[1], rd_k[2]]

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
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    import time

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            jd_at_dob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        )
        if DLI <= const.MAHA_DHASA_DEPTH.ANTARA:
            for row in ad:
                print(row)
            continue
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=9
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    utils.set_language('en')
    chart_72 = ['', '', '7', '5/0', '3', '2', '', '', '8', '6', '1', '4/L']
    print('chart_72', chart_72)
    chart_72_lagna = []
    dob = (1963, 8, 7)
    tob = (21, 14, 0)
    place = drik.Place('unknown', 21 + 27.0 / 60, 83 + 58.0 / 60, +5.5)
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.03862, 80.261818, 5.5)
    jd = utils.julian_day_number(dob, tob)
    jd_utc = jd - place.timezone / 24.0
    years_from_dob = 1
    divisional_chart_factor = 1
    jd_at_dob = utils.julian_day_number(dob, tob)
    pp = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor)
    jd_at_years = jd_at_dob + years_from_dob * year_duration
    lsd, msd, ssd, _ = sudharshana_chakra_chart(
        jd_at_dob, place, dob, years_from_dob, divisional_chart_factor
    )
    print(lsd, '\n', msd, '\n', ssd)
    scd = get_dhasa_bhukthi(
        jd_at_dob, place, divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
        antardhasa_from_lord_of_dhasa_sign=True
    )
    for row in scd:
        print(row)
