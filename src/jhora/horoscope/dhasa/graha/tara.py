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

""" Tara Dasa - applicable if all the four quadrants are occupied """
"""
    TODO: To implement following options for sanjay rath method:
        1. No dhasa sesham OR 2. Dasa sesham from moon as per vimsottari
        OR 3. Dhasa sesham from moon but in reverse for apasavya nakshatras
"""

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house


dhasa_adhipathi_dict_sanjay_rath = {5: 20, 1: 10, 8: 7, 6: 19, 4: 16, 3: 17, 7: 18, 2: 7, 0: 6}
dhasa_adhipathi_dict_parasara = {5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17, 8: 7}
human_life_span = sum(dhasa_adhipathi_dict_parasara.values())
year_duration = const.sidereal_year


def _next_adhipati(lord, dirn=1, dhasa_method=1):
    dhasa_adhipathi_dict = dhasa_adhipathi_dict_sanjay_rath if dhasa_method == 1 else dhasa_adhipathi_dict_parasara
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_dict.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_dict.keys())[((current + dirn) % len(dhasa_adhipathi_dict))]
    return next_lord


def _antardhasa(lord, dhasa_method=1):
    dhasa_adhipathi_dict = dhasa_adhipathi_dict_sanjay_rath if dhasa_method == 1 else dhasa_adhipathi_dict_parasara
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord, dhasa_method=dhasa_method)
    return _bhukthis


def _dhasa_start(jd, place, period, star_position_from_moon=1, divisional_chart_factor=1, chart_method=1):
    one_star = 360 / 27.0
    planet_positions = charts.divisional_chart(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )[:const._pp_count_upto_ketu]
    moon = planet_positions[2][1][0] * 30 + planet_positions[2][1][1] + (star_position_from_moon - 1) * one_star
    nak = int(moon / one_star)
    rem = moon - nak * one_star
    period_elapsed = rem / one_star * period  # years
    period_elapsed *= year_duration  # days
    start_date = jd - period_elapsed  # so many days before current day
    return start_date


def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1, chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_method=const.TARA_TYPE.SANJAY_RATH,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
        provides Tara dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth

        @param dhasa_level_index: Depth level (1..6)
            1 = Mahadasha only (no Antardasha)
            2 = + Antardasha (Bhukthi)
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara

        @param dhasa_method:
            1=>Sanjay Rath method dhasa order 5,1,8,6,4,3,7,2,0  (Default)
            2=>Parasara method dhasa order   5,0,1,2,7,4,6,3,8

        @param round_duration: If True, round only the returned duration values to dhasa_level_index.
                               Internal time accumulation and deeper splits always use full precision.

        @return:
          if dhasa_level_index==1:
            [ (dhasa_lord, dhasa_start, duration_years), ... ]
          else:
            [ (dhasa_lord, bhukthi_lord, [further sub-lords...], dhasa_start, leaf_duration_years), ... ]
    """
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    dhasa_adhipathi_dict = (
        dhasa_adhipathi_dict_sanjay_rath
        if dhasa_method == const.TARA_TYPE.SANJAY_RATH
        else dhasa_adhipathi_dict_parasara
    )

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
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )[:const._pp_count_upto_ketu]

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]

    ds = sorted(
        [h_to_p[(h + asc_house) % 12].split('/') for h in [0, 3, 6, 9] if h_to_p[(h + asc_house) % 12] != ''],
        key=len,
        reverse=True,
    )
    ds = utils.flatten_list(ds)
    if len(ds) == 0:
        print('tara dhasa ds list is empty, returning empty list')
        return []
    if 'L' in ds:
        ds.remove('L')
    if len(ds) == 0:
        print('tara dhasa ds list is empty, returning empty list')
        return []

    if len(ds) >= 2:
        ds1 = ds
        sp = int(ds1[0])
        for p in range(1, len(ds1)):
            sp = house.stronger_planet_from_planet_positions(planet_positions, int(ds1[p]), int(sp))
        dhasa_lord = sp
    else:
        dhasa_lord = int(ds[0])

    _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]

    start_jd = _dhasa_start(
        jd_at_dob,
        place,
        _dhasa_duration,
        star_position_from_moon=1,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )

    dhasa_info = []

    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, dhasa_method=dhasa_method))

    def _child_years_list(parent_years, children):
        return [
            parent_years * (dhasa_adhipathi_dict[bl] / float(human_life_span))
            for bl in children
        ]

    def _recurse(level, parent_lord, parent_start_jd, parent_years, prefix):
        children = _children_of(parent_lord)
        if not children:
            return

        child_years_list = _child_years_list(parent_years, children)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for blord, child_years_unrounded in zip(children, child_years_list):
                _recurse(level + 1, blord, jd_cursor, child_years_unrounded, prefix + (blord,))
                jd_cursor += child_years_unrounded * year_duration
        else:
            for blord, child_years_unrounded in zip(children, child_years_list):
                start_str = utils.jd_to_gregorian(jd_cursor)
                durn = round(child_years_unrounded, dhasa_level_index + 1) if round_duration else child_years_unrounded
                dhasa_info.append((prefix + (blord,), start_str, durn))
                jd_cursor += child_years_unrounded * year_duration

    for _ in range(len(dhasa_adhipathi_dict)):
        maha_years_unrounded = dhasa_adhipathi_dict[dhasa_lord]

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            start_str = utils.jd_to_gregorian(start_jd)
            durn = round(maha_years_unrounded, dhasa_level_index + 1) if round_duration else maha_years_unrounded
            dhasa_info.append(((dhasa_lord,), start_str, durn))
            start_jd += maha_years_unrounded * year_duration
        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_lord=dhasa_lord,
                parent_start_jd=start_jd,
                parent_years=maha_years_unrounded,
                prefix=(dhasa_lord,),
            )
            start_jd += maha_years_unrounded * year_duration

        dhasa_lord = _next_adhipati(dhasa_lord, dhasa_method=dhasa_method)
        _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]

    return dhasa_info


def tara_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (one of duration or end must be provided)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    dhasa_method: int = const.TARA_TYPE.SANJAY_RATH,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Tara Daśā — return ONLY the immediate (p->p+1) children within a given parent span.

    Rules (mirror your base get_dhasa_bhukthi):
      • Child order at every level: _antardhasa(parent_lord, dhasa_method=...)
      • Child duration weights == adhipati years for the method; normalized to parent span:
            child_years = parent_years * (Y_child / ΣY)
      • Exact tiling: first child starts at parent_start; last child ends at parent_end.

    Returns:
      [ (lords_tuple_with_child), child_start_tuple, child_end_tuple ]
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
        raise ValueError("parent_lords must be int or a non-empty tuple/list of ints")
    parent_lord = path[-1]

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

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

    adhi = (
        dhasa_adhipathi_dict_sanjay_rath
        if dhasa_method == const.TARA_TYPE.SANJAY_RATH
        else dhasa_adhipathi_dict_parasara
    )
    total_years = float(sum(adhi.values())) or 1.0

    def _children_of(pl):
        return list(_antardhasa(pl, dhasa_method=dhasa_method))

    children = _children_of(parent_lord)
    if not children:
        return []

    out = []
    jd_cursor = start_jd
    for idx, bl in enumerate(children):
        share = float(adhi.get(bl, 0.0)) / total_years
        child_years = parent_years * share
        if idx == len(children) - 1:
            child_end = end_jd
        else:
            child_end = jd_cursor + child_years * year_duration
        out.append([
            path + (bl,),
            _jd_to_tuple(jd_cursor),
            _jd_to_tuple(child_end),
        ])
        jd_cursor = child_end
        if jd_cursor >= end_jd:
            break

    if out:
        out[-1][2] = _jd_to_tuple(end_jd)

    return out


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    dhasa_method: int = const.TARA_TYPE.SANJAY_RATH,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Tara Daśā — narrow Mahā -> … -> target depth and return the full running ladder.
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
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds=eps_seconds)]
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

    maha_rows = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        dhasa_method=dhasa_method,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    maha_for_utils = [(_as_tuple_lords(row[0]), row[1]) for row in maha_rows]

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_as_tuple_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = tara_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            dhasa_method=dhasa_method,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
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
            continue

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
            )
        )
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.tara_dhasa_test()
