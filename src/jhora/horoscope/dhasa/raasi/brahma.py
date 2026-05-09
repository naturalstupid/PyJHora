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
""" Also called Brahma Grahashrita Dasa """
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year


def _dhasa_duration(planet_positions, sign):
    lord_of_6th = house.house_owner_from_planet_positions(planet_positions, (sign + const.HOUSE_6) % 12)
    lord_house = planet_positions[lord_of_6th + 1][1][0]
    _dd = (lord_house + 13 - sign) % 12
    if sign in const.even_signs:
        _dd = (sign + 13 - lord_house) % 12
    _dd -= 1
    if lord_house == sign:
        _dd = 0
    elif const.house_strengths_of_planets[lord_of_6th][lord_house] == const._DEBILITATED_NEECHAM:
        _dd -= 1
    elif const.house_strengths_of_planets[lord_of_6th][lord_house] == const._EXALTED_UCCHAM:
        _dd += 1
    return _dd


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
        Compute Brahma-based sign daśā with depth control (Maha → Antara → …).
    """
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    brahma = house.brahma(planet_positions)
    dhasa_seed = planet_positions[brahma + 1][1][0]

    dhasa_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [(dhasa_seed + 6 - h + 12) % 12 for h in range(12)]

    def _children_signs(parent_sign):
        return [(parent_sign + k) % 12 for k in range(12)]

    def _equal_split(parent_years):
        return parent_years / 12.0

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        bhukthis = _children_signs(parent_sign)
        child_unrounded = _equal_split(parent_years)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for child_sign in bhukthis:
                _recurse(level + 1, child_sign, jd_cursor, child_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_unrounded * year_duration
        else:
            for child_sign in bhukthis:
                start_str = utils.jd_to_gregorian(jd_cursor)
                dur_ret = round(child_unrounded, dhasa_level_index + 1) if round_duration else child_unrounded
                out_rows.append((prefix + (child_sign,), start_str, dur_ret))
                jd_cursor += child_unrounded * year_duration

    dhasa_info = []
    start_jd = jd_at_dob

    for d, dhasa_lord in enumerate(dhasa_lords):
        duration_years = float(_dhasa_duration(planet_positions, dhasa_lord))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            dhasa_info.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(duration_years, dhasa_level_index + 1) if round_duration else duration_years,
            ))
            start_jd += duration_years * year_duration
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            bhukthis = _children_signs(dhasa_lord)
            dd = duration_years / 12.0
            jd_cursor = start_jd

            for bhukthi_lord in bhukthis:
                dhasa_info.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_cursor),
                    round(dd, dhasa_level_index + 1) if round_duration else dd,
                ))
                jd_cursor += dd * year_duration

            start_jd += duration_years * year_duration
            continue

        _recurse(
            level=const.MAHA_DHASA_DEPTH.ANTARA,
            parent_sign=dhasa_lord,
            parent_start_jd=start_jd,
            parent_years=duration_years,
            prefix=(dhasa_lord,),
            out_rows=dhasa_info,
        )
        start_jd += duration_years * year_duration

    return dhasa_info


def brahma_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Brahma Daśā — return ONLY the immediate (p -> p+1) children under the given parent span.
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
        raise ValueError("parent_lords must be int or non-empty tuple/list")
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

    children_signs = [(parent_sign + k) % 12 for k in range(12)]
    child_years = parent_years / 12.0

    children = []
    cursor = start_jd
    for i, sgn in enumerate(children_signs):
        if i == len(children_signs) - 1:
            child_end = end_jd
        else:
            child_end = cursor + child_years * year_duration
        children.append([
            path + (sgn,),
            _jd_to_tuple(cursor),
            _jd_to_tuple(child_end),
        ])
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
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Brahma Daśā — narrow Mahā -> … -> target depth and return the full running ladder.
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
        for lords, st, _ in filtered:
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
        **kwargs,
    )
    maha_for_utils = [(_as_tuple_lords(row[0]), row[1]) for row in maha_rows]

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_as_tuple_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = brahma_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years,
            months=months,
            sixty_hours=sixty_hours,
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
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.brahma_dhasa_test()
