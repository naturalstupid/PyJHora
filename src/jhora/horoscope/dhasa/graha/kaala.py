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
""" Kaala Dhasa """
from jhora.panchanga import drik
from jhora import utils, const

_kaala_dhasa_life_span = 120  # years
year_duration = const.sidereal_year


def _dhasa_progression_and_periods(jd, place):
    previous_day_sunset_time = drik.sunset(jd - 1, place)[0]
    today_sunset_time = drik.sunset(jd, place)[0]
    today_sunrise_time = drik.sunrise(jd, place)[0]
    tomorrow_sunrise_time = 24.0 + drik.sunrise(jd + 1, place)[0]

    _, _, _, birth_time = utils.jd_to_gregorian(jd)

    df = abs(today_sunset_time - today_sunrise_time) / 6.0
    nf1 = abs(today_sunrise_time - previous_day_sunset_time) / 6.0
    nf2 = abs(tomorrow_sunrise_time - today_sunset_time) / 6.0

    dawn_start = today_sunrise_time - nf1
    dawn_end = today_sunrise_time + nf1

    day_start = dawn_end
    day_end = today_sunset_time - nf1

    dusk_start = day_end
    dusk_end = today_sunset_time + nf2

    yday_night_start = -(previous_day_sunset_time + nf1)
    yday_night_end = today_sunrise_time - nf1

    tonight_start = today_sunset_time + nf2
    tonight_end = tomorrow_sunrise_time - nf2

    # Night is before dawn_start and after dusk_end.
    if birth_time > dawn_start and birth_time < dawn_end:
        kaala_type = const.KAALA_TYPE.DAWN
        kaala_frac = (birth_time - dawn_start) / (dawn_end - dawn_start)

    elif birth_time > dusk_start and birth_time < dusk_end:
        kaala_type = const.KAALA_TYPE.DUSK
        kaala_frac = (birth_time - dusk_start) / (dusk_end - dusk_start)

    elif birth_time > day_start and birth_time < day_end:
        kaala_type = const.KAALA_TYPE.DAY
        kaala_frac = (birth_time - day_start) / (day_end - day_start)

    elif birth_time > yday_night_start and birth_time < yday_night_end:
        kaala_type = const.KAALA_TYPE.NIGHT
        kaala_frac = (birth_time - yday_night_start) / (yday_night_end - yday_night_start)

    elif birth_time > tonight_start and birth_time < tonight_end:
        kaala_type = const.KAALA_TYPE.NIGHT
        kaala_frac = (birth_time - tonight_start) / (tonight_end - tonight_start)

    else:
        # Boundary fallback.
        kaala_type = const.KAALA_TYPE.DAY
        kaala_frac = 0.0

    _kaala_dhasa_life_span_first_cycle = _kaala_dhasa_life_span * kaala_frac
    _dhasas1 = [(p + 1) * _kaala_dhasa_life_span_first_cycle / 45.0 for p in range(9)]

    # Second Cycle.
    _kaala_dhasa_life_span_second_cycle = (
        _kaala_dhasa_life_span - _kaala_dhasa_life_span_first_cycle
    )
    _dhasas2 = [(p + 1) * _kaala_dhasa_life_span_second_cycle / 45.0 for p in range(9)]

    return kaala_type, kaala_frac, _dhasas1, _dhasas2


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Provides Kaala dhasa-bhukthi for a given date.

    Returns:
        kaala_type, dhasa_info

    dhasa_info rows:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]
    """
    global year_duration

    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    jd_years = drik.next_solar_date(
        jd_at_dob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )

    kaala_type, kaala_frac, dhasas_first, dhasas_second = _dhasa_progression_and_periods(
        jd_years,
        place,
    )

    dhasa_info = []
    start_jd = jd_years

    def _children_two_phase(parent_start_jd, parent_duration_years):
        """
        Yields children using the Kaala two-phase rule.

        Phase A:
            kaala_frac * parent_duration, subdivided by weights 1..9.
        Phase B:
            (1 - kaala_frac) * parent_duration, subdivided by weights 1..9.

        Yields:
            (bhukthi_lord, child_start_jd, child_duration_years)
        """
        weights = list(range(1, 10))
        W = 45.0

        # Phase A.
        phaseA = kaala_frac * parent_duration_years
        jd_cursor = parent_start_jd

        for blord, w in enumerate(weights):
            dur = phaseA * (w / W)
            yield blord, jd_cursor, dur
            jd_cursor += dur * year_duration

        # Phase B.
        phaseB = (1.0 - kaala_frac) * parent_duration_years

        for blord, w in enumerate(weights):
            dur = phaseB * (w / W)
            yield blord, jd_cursor, dur
            jd_cursor += dur * year_duration

    def _recurse(level, parent_start_jd, parent_duration_years, prefix):
        """
        Recursive expander. Applies Kaala two-phase rule at every depth.
        """
        children = list(_children_two_phase(parent_start_jd, parent_duration_years))

        if not children:
            return

        if level < dhasa_level_index:
            for blord, child_start_jd, child_dur in children:
                _recurse(
                    level + 1,
                    child_start_jd,
                    child_dur,
                    prefix + (blord,),
                )
        else:
            for blord, child_start_jd, child_dur in children:
                durn = (
                    round(child_dur, dhasa_level_index + 1)
                    if round_duration
                    else child_dur
                )
                dhasa_info.append(
                    [
                        prefix + (blord,),
                        utils.jd_to_gregorian(child_start_jd),
                        durn,
                    ]
                )

    # First Cycle.
    for dhasa_lord in range(9):
        maha_dur_unrounded = dhasas_first[dhasa_lord]

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            durn = (
                round(maha_dur_unrounded, dhasa_level_index + 1)
                if round_duration
                else maha_dur_unrounded
            )
            dhasa_info.append([(dhasa_lord,), utils.jd_to_gregorian(start_jd), durn])
            start_jd += maha_dur_unrounded * year_duration
        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_start_jd=start_jd,
                parent_duration_years=maha_dur_unrounded,
                prefix=(dhasa_lord,),
            )
            start_jd += maha_dur_unrounded * year_duration

    # Second Cycle.
    for dhasa_lord in range(9):
        maha_dur_unrounded = dhasas_second[dhasa_lord]

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            durn = (
                round(maha_dur_unrounded, dhasa_level_index + 1)
                if round_duration
                else maha_dur_unrounded
            )
            dhasa_info.append([(dhasa_lord,), utils.jd_to_gregorian(start_jd), durn])
            start_jd += maha_dur_unrounded * year_duration
        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_start_jd=start_jd,
                parent_duration_years=maha_dur_unrounded,
                prefix=(dhasa_lord,),
            )
            start_jd += maha_dur_unrounded * year_duration

    return kaala_type, dhasa_info


def kaala_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kaala Dhasa immediate children under a given parent span.

    Rules:
        - Two-phase split using kaala_frac.
        - Phase A = kaala_frac * parent duration.
        - Phase B = (1 - kaala_frac) * parent duration.
        - Each phase subdivided by weights 1..9.
        - 18 immediate children total.
        - Last child end is forced to parent_end.

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

    jd_years = drik.next_solar_date(
        jd_at_dob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )

    _kaala_type, kaala_frac, _dhasas_first, _dhasas_second = _dhasa_progression_and_periods(
        jd_years,
        place,
    )

    weights = list(range(1, 10))
    W = 45.0

    phaseA_years = kaala_frac * parent_years
    phaseB_years = (1.0 - kaala_frac) * parent_years

    segments = []

    for blord, w in enumerate(weights):
        segments.append((blord, phaseA_years * (w / W)))

    for blord, w in enumerate(weights):
        segments.append((blord, phaseB_years * (w / W)))

    children = []
    cursor = start_jd

    for idx, (blord, dur_y) in enumerate(segments):
        if idx == len(segments) - 1:
            child_end = end_jd
        else:
            child_end = cursor + dur_y * year_duration

        children.append(
            [
                path + (blord,),
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
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kaala Dhasa runner.

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
        filtered = [
            r for r in children_rows
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

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    running_all = []

    _kaala_type, maha_rows = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    maha_for_utils = []

    for row in maha_rows:
        lords_any, start_t = row[0], row[1]
        maha_for_utils.append((_as_tuple_lords(lords_any), start_t))

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)

    lords1 = _as_tuple_lords(rd1[0])
    running = [lords1, rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = kaala_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            years=years,
            months=months,
            sixty_hours=sixty_hours,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
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
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            lords_k = _as_tuple_lords(rdk[0])
            running = [lords_k, rdk[1], rdk[2]]

        running_all.append(running)

    return running_all


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

        _, ad = get_dhasa_antardhasa(
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
            )
        )

        print("old method elapsed time", time.time() - start_time)

    exit()

    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kaala_test()
