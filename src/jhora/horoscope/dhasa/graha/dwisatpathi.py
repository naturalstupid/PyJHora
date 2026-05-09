#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA of# Copyright (C) Open Astro Technologies, USA.
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option any later version.
#
# This program is distributed in the hope that it will be useful,

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, sphuta


year_duration = const.sidereal_year

"""Applicability: Lagna lord in 7th or 7th lord in Lagna."""

# seed_star = 19  # Moola
seed_lord = 0

# Duration: 9 years each. Total: 72 years.
dhasa_adhipathi_list = {k: 9 for k in range(8)}

# dhasa_adhipathi_dict = {
#     0: [19, 27, 8, 16],
#     1: [20, 1, 9, 17],
#     2: [21, 2, 10, 18],
#     3: [22, 3, 11],
#     4: [23, 4, 12],
#     5: [24, 5, 13],
#     6: [25, 6, 14],
#     7: [26, 7, 15],
# }

# count_direction:
#   1  -> base star to birth star zodiac
#  -1  -> base star to birth star anti-zodiac
count_direction = 1


def applicability_check(planet_positions):
    """Lagna lord in 7th or 7th lord in Lagna."""
    from jhora.horoscope.chart import house

    lagna = planet_positions[0][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions, lagna)

    seventh_house = (lagna + 6) % 12
    seventh_lord = house.house_owner_from_planet_positions(planet_positions, seventh_house)

    return (
        planet_positions[seventh_lord + 1][1][0] == lagna
        or planet_positions[lagna_lord + 1][1][0] == seventh_house
    )


def _next_adhipati(lord, dirn=1):
    """Returns next lord after lord in the adhipati list."""
    keys = list(dhasa_adhipathi_list.keys())
    current = keys.index(lord)
    next_lord = keys[(current + dirn) % len(keys)]
    return next_lord


def _get_dhasa_dict(seed_star=19):
    dhasa_dict = {k: [] for k in dhasa_adhipathi_list.keys()}

    nak = seed_star - 1
    lord = seed_lord
    lord_index = list(dhasa_adhipathi_list.keys()).index(lord)

    for _ in range(27):
        dhasa_dict[lord].append(nak + 1)
        nak = (nak + 1 * count_direction) % 27
        lord_index = (lord_index + 1) % len(dhasa_adhipathi_list)
        lord = list(dhasa_adhipathi_list.keys())[lord_index]

    return dhasa_dict


def _maha_dhasa(nak, seed_star=19):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)

    return [
        (_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord])
        for _dhasa_lord, _star_list in dhasa_adhipathi_dict.items()
        if nak in _star_list
    ][0]


def _antardhasa(dhasa_lord, antardhasa_option=1):
    lord = dhasa_lord

    if antardhasa_option in [3, 4]:
        lord = _next_adhipati(dhasa_lord, dirn=1)
    elif antardhasa_option in [5, 6]:
        lord = _next_adhipati(dhasa_lord, dirn=-1)

    dirn = 1 if antardhasa_option in [1, 3, 5] else -1

    _bhukthis = []

    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord, dirn)

    return _bhukthis


def _dhasa_start(
    jd,
    place,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=19,
    dhasa_starting_planet=1,
):
    one_star = 360 / 27.0

    planet_long = charts.get_chart_element_longitude(
        jd,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )

    nak = int(planet_long / one_star)
    rem = planet_long - nak * one_star

    lord, res = _maha_dhasa(nak + 1, seed_star)

    period = res
    period_elapsed = rem / one_star * period  # years
    period_elapsed *= year_duration           # days

    start_date = jd - period_elapsed

    return [lord, start_date, res]


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=19,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Returns dhasa segments at the selected depth level L1..L6.

    Returns:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    dhasa_level_index:
        1 = Maha only
        2 = Antara
        3 = Pratyantara
        4 = Sookshma
        5 = Prana
        6 = Deha
    """
    global year_duration

    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # Original logic preserved.
    _tribhagi_factor = 1.0
    _dhasa_cycles = 2

    if use_tribhagi_variation:
        _tribhagi_factor = 1.0 / 3.0
        _dhasa_cycles = int(_dhasa_cycles / _tribhagi_factor)

    dhasa_lord, start_jd, _ = _dhasa_start(
        jd,
        place,
        star_position_from_moon=star_position_from_moon,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    retval = []

    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option=antardhasa_option))

    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        """
        Nested equal split of the immediate parent.
        Internal calculations use full precision.
        """
        bhukthis = _children_of(parent_lord)

        if not bhukthis:
            return

        child_dur_unrounded = parent_duration_years / len(bhukthis)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for blord in bhukthis:
                _recurse(
                    level + 1,
                    blord,
                    jd_cursor,
                    child_dur_unrounded,
                    prefix + (blord,),
                )
                jd_cursor += child_dur_unrounded * year_duration
        else:
            for blord in bhukthis:
                start_tuple = utils.jd_to_gregorian(jd_cursor)
                durn = (
                    round(child_dur_unrounded, dhasa_level_index)
                    if round_duration
                    else child_dur_unrounded
                )
                retval.append([prefix + (blord,), start_tuple, durn])
                jd_cursor += child_dur_unrounded * year_duration

    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            maha_dur_unrounded = dhasa_adhipathi_list[dhasa_lord] * _tribhagi_factor

            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                start_tuple = utils.jd_to_gregorian(start_jd)
                durn = (
                    round(maha_dur_unrounded, dhasa_level_index)
                    if round_duration
                    else maha_dur_unrounded
                )
                retval.append([(dhasa_lord,), start_tuple, durn])
                start_jd += maha_dur_unrounded * year_duration
            else:
                _recurse(
                    level=const.MAHA_DHASA_DEPTH.ANTARA,
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_duration_years=maha_dur_unrounded,
                    prefix=(dhasa_lord,),
                )
                start_jd += maha_dur_unrounded * year_duration

            dhasa_lord = _next_adhipati(dhasa_lord)

    return retval


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=19,
    antardhasa_option=1,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Nakshathra dhasa progression.

    For divisional charts:
        First calculate progression for rasi, then apply varga division to
        progressed rasi longitudes.
    """
    DLI = dhasa_level_index

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    vd = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        antardhasa_option=antardhasa_option,
        dhasa_level_index=DLI,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    vdc = None

    if get_running_dhasa:
        vdc = utils.get_running_dhasa_for_given_date(jd_current, vd)
        print(vdc)

    jds = [
        utils.julian_day_number(drik.Date(y1, m1, d1), (fh1, 0, 0))
        for _, (y1, m1, d1, fh1), *_ in vd
    ]

    planet_long = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=1,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    birth_star_index = drik.nakshatra_pada(planet_long)[0] - 1

    prog_long = utils.progressed_abs_long_general(
        jds,
        jd_current,
        birth_star_index,
        dhasa_level_index=DLI,
        total_lords_in_dhasa=len(dhasa_adhipathi_list),
    )

    progression_correction = utils.norm360(prog_long - planet_long)

    if get_running_dhasa:
        return progression_correction, vdc

    return progression_correction


def dwisatpathi_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    antardhasa_option: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Dwisatpathi immediate children under the given parent span.

    Rules:
        - Child order from _antardhasa(parent_lord, antardhasa_option)
        - Equal split at this level
        - Last child end forced to parent_end

    Output:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]
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

    parent_lord = path[-1]

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end.")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    child_lords = list(_antardhasa(parent_lord, antardhasa_option=antardhasa_option))

    if not child_lords:
        return []

    n = len(child_lords)
    child_years = parent_years / n

    children = []
    cursor = start_jd

    for i, cl in enumerate(child_lords):
        if i == n - 1:
            child_end = end_jd
        else:
            child_end = cursor + child_years * year_duration

        children.append(
            [
                path + (cl,),
                _jd_to_tuple(cursor),
                _jd_to_tuple(child_end),
            ]
        )

        cursor = child_end

        if cursor >= end_jd:
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
    antardhasa_option: int = 1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=19,
    dhasa_starting_planet=1,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Dwisatpathi runner. Narrows Maha -> ... -> target level.

    Returns:
        [
            [(l1,),                start1, end1],
            [(l1,l2),              start2, end2],
            [(l1,l2,l3),           start3, end3],
            [(l1,l2,l3,l4),        start4, end4],
            [(l1,l2,l3,l4,l5),     start5, end5],
            [(l1,l2,l3,l4,l5,l6),  start6, end6],
        ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        filtered = [
            r
            for r in children_rows
            if not _is_zero_length(r[1], r[2], eps_seconds=eps_seconds)
        ]

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

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = const.MAHA_DHASA_DEPTH.DEHA

    target_depth = max(
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        min(const.MAHA_DHASA_DEPTH.DEHA, target_depth),
    )

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    maha_rows = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        antardhasa_option=antardhasa_option,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    maha_for_utils = []

    for row in maha_rows:
        lords_any, start_t = row[0], row[1]
        maha_for_utils.append((_as_tuple_lords(lords_any), start_t))

    running_all = []

    rd = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)

    lords = _as_tuple_lords(rd[0])
    running = [lords, rd[1], rd[2]]
    running_all.append(running)

    if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        return running_all

    for depth in range(const.MAHA_DHASA_DEPTH.ANTARA, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = dwisatpathi_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            antardhasa_option=antardhasa_option,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
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
            lords_k = _as_tuple_lords(rd_k[0])
            running = [lords_k, rd_k[1], rd_k[2]]

        running_all.append(running)

    return running_all


# ---------------------------------------------------------------------
# Example usage / duration-method test
# ---------------------------------------------------------------------
if __name__ == "__main__":
    utils.set_language("en")

    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)

    place = drik.Place("Chennai,IN", 13.0389, 80.2619, +5.5)

    jd_at_dob = utils.julian_day_number(dob, tob)

    from datetime import datetime
    import time

    current_date_str, current_time_str = datetime.now().strftime("%Y,%m,%d;%H:%M:%S").split(";")

    y, m, d = map(int, current_date_str.split(","))
    hh, mm, ss = map(int, current_time_str.split(":"))
    fh = hh + mm / 60 + ss / 3600

    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))

    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

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
            "Deha:",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_duration_type=dd,
            ),
        )

        print("new method elapsed time", time.time() - start_time)

        start_time = time.time()

        ad = get_dhasa_bhukthi(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd,
        )

        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=2,
            )
        )

        print("old method elapsed time", time.time() - start_time)

    exit()

    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.dwisatpathi_test()
