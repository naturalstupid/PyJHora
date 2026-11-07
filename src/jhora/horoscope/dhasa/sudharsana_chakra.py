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
Sudharshana Chakra Dasa

Source: P.V.R. Narasimha Rao, "Vedic Astrology: An Integrated Approach",
Ch. 31 "Sudarsana Chakra Dasa".

Three reference points -- Lagna, Moon, Sun -- each give a house count.
Sudarsana Chakra (SC) draws the bhava chakra with respect to all three
as concentric circles. This module tracks all three simultaneously as
one (lagna_house, moon_house, sun_house) triple per level.

Mahadasa: dasas of the 12 houses run in cycles throughout a native's
life, one house per year; after 12 years, dasa of the 1st house
returns. The running house for a given year is found by: (years
completed + 1), divided by 12, remainder taken (a remainder of 0 means
house 12). At birth (0 years completed), this gives house 1, i.e. the
native's own natal triple. One year stands for a solar year.

Antardasa: each dasa divides into 12 antardasas; the dasa sign is taken
as lagna, and the 1st, 2nd, 3rd etc. houses from it are given to the
antardasas in order. The same rule applies recursively at every deeper
level. This is antardhasa_from_lord_of_dhasa_sign=False, the default.

antardhasa_from_lord_of_dhasa_sign=True: each of the triple's three
signs is replaced by the natal house of that sign's lord
(const._house_owners_list), and the antardasa roll proceeds from there.

Level 1 (Mahadasha) always uses the plain forward roll from the natal
triple; antardhasa_from_lord_of_dhasa_sign only governs level 2 and
deeper.
"""
from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

year_duration = const.sidereal_year
_SIDEREAL_YEAR = year_duration
_TROPICAL_YEAR = getattr(const, "tropical_year", 365.24219052)

_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True

_MAX_CYCLE_SEARCH = 200


def _set_year_duration(jd, place, *, use_sidereal=False, dhasa_duration_type=None, savana_year_method=None):
    """
    Sets the module-level year_duration used by _bounded_end_jd() and
    sub-day interpolation. If dhasa_duration_type is given, it also sets
    const.dhasa_year_duration_default; otherwise the existing global is
    left unchanged.
    """
    global year_duration

    if dhasa_duration_type is not None:
        const.dhasa_year_duration_default = dhasa_duration_type

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


def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """ Real dasa-period end JD, guarded by a naive average-year backstop. """
    naive_end = start_jd + duration_in_years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, duration_in_years)
    except Exception:
        return naive_end
    if real_end is None or real_end <= start_jd:
        return naive_end
    if _USE_SANITY_BACKSTOP and abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end


def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, n=12):
    """ Splits a parent span into n equal children using real dasa-period
    boundaries; the last child is clamped exactly to parent_end_jd. """
    child_years = parent_years / n
    parent_real_days = parent_end_jd - parent_start_jd
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        if is_last:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (child_years * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / n
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out


def _roll_triple(tri, k):
    return ((tri[0] + k) % 12, (tri[1] + k) % 12, (tri[2] + k) % 12)


def _sudharsana_antardhasa_seeds(dhasa_triple, planet_positions, antardhasa_from_lord_of_dhasa_sign):
    """ The 12 ordered antardasa (or deeper) child triples for a given
    parent triple. See module docstring for the source citation
    (antardhasa_from_lord_of_dhasa_sign=False) and the "from lord of
    dasa sign" rule (antardhasa_from_lord_of_dhasa_sign=True), which
    uses const._house_owners_list. """
    dl1, dl2, dl3 = dhasa_triple
    if not antardhasa_from_lord_of_dhasa_sign:
        return [((dl1 + h) % 12, (dl2 + h) % 12, (dl3 + h) % 12) for h in range(12)]

    antardhasa_lords = [const._house_owners_list[ds] for ds in dhasa_triple]
    antardhasa_triple = [planet_positions[al + 1][1][0] for al in antardhasa_lords]
    al1, al2, al3 = antardhasa_triple
    return [((al1 + h) % 12, (al2 + h) % 12, (al3 + h) % 12) for h in range(12)]


def _get_children_triples(parent_triple, child_level, planet_positions, antardhasa_from_lord_of_dhasa_sign):
    """
    The ordered list of 12 child triples belonging to `child_level`
    (1 = Mahadasha, 2 = Antardasha, ...). Level 1 always uses the plain
    forward roll from the natal triple; antardhasa_from_lord_of_dhasa_
    sign only affects level 2 and deeper.
    """
    if child_level == 1:
        return [_roll_triple(parent_triple, i) for i in range(12)]
    return list(_sudharsana_antardhasa_seeds(
        parent_triple,
        planet_positions,
        antardhasa_from_lord_of_dhasa_sign,
    ))


def _get_children_jds(
    path_so_far, parent_triple, parent_start_jd, parent_end_jd, parent_years,
    place, child_level, planet_positions, antardhasa_from_lord_of_dhasa_sign,
):
    """
    Returns a list of (child_path, child_triple, child_start_jd,
    child_end_jd, child_years) for the 12 children of parent_triple at
    child_level.
    """
    child_triples = _get_children_triples(
        parent_triple, child_level, planet_positions, antardhasa_from_lord_of_dhasa_sign
    )
    child_years = parent_years / 12.0
    bounds = _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, n=12)

    out = []
    for triple, (c_start, c_end) in zip(child_triples, bounds):
        out.append((path_so_far + (triple,), triple, c_start, c_end, child_years))
    return out


def sudharshana_chakra_chart(jd_at_dob, place, dob, years_from_dob=1, divisional_chart_factor=1,
                             chart_method=1, use_sidereal=False, dhasa_duration_type=None,
                             savana_year_method=None, **kwargs):
    """ Casts the Sudarsana Chakra chart (Lagna/Moon/Sun concentric bhava
    charts) at a given year of life, using a Tajaka (solar-return) annual
    chart -- separate from the dasha-boundary machinery below. """
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


def get_dhasa_antardhasa(
    dob,tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    antardhasa_from_lord_of_dhasa_sign=False,
    chart_method=1,
    use_sidereal=False,
    dhasa_cycles=9,
    max_rows=None,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Full Sudharshana Chakra table, to the requested depth, across
    dhasa_cycles repeating 12-year wheels, anchored at the birth Julian
    day.

    Returns rows shaped as:
      [ [triple_lvl1, ..., triple_lvlN], (Y, M, D, fractional_hours), duration_in_years ]
    """
    jd_at_dob = utils.julian_day_number(dob,tob)
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    try:
        depth = int(dhasa_level_index)
    except Exception:
        depth = const.MAHA_DHASA_DEPTH.ANTARA
    depth = max(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, min(depth, const.MAHA_DHASA_DEPTH.DEHA))

    try:
        dhasa_cycles = int(dhasa_cycles)
    except Exception:
        dhasa_cycles = 9
    dhasa_cycles = max(1, dhasa_cycles)

    total_rows = dhasa_cycles * (12 ** depth)
    if max_rows is not None and total_rows > int(max_rows):
        raise ValueError(
            f"Requested {total_rows} rows (dhasa_cycles={dhasa_cycles}, depth={depth}) "
            f"exceeds max_rows={max_rows}. Use the runner for deep levels."
        )

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

    results = []

    def _append_leaf(path, start_jd_val, years_val):
        disp_dur = round(years_val, depth + 1) if round_duration else years_val
        results.append([list(path), utils.jd_to_gregorian(start_jd_val), disp_dur])

    def _recurse(path_so_far, parent_triple, start_jd_val, end_jd_val, years_val, child_level):
        children = _get_children_jds(
            path_so_far, parent_triple, start_jd_val, end_jd_val, years_val,
            place, child_level, planet_positions, antardhasa_from_lord_of_dhasa_sign,
        )
        for child_path, child_triple, c_start, c_end, c_years in children:
            if child_level == depth:
                _append_leaf(child_path, c_start, c_years)
            else:
                _recurse(child_path, child_triple, c_start, c_end, c_years, child_level + 1)

    cursor_jd = jd_at_dob
    for _c in range(dhasa_cycles):
        cycle_end_jd = _bounded_end_jd(cursor_jd, place, 12.0)
        _recurse((), base_triple, cursor_jd, cycle_end_jd, 12.0, child_level=1)
        cursor_jd = cycle_end_jd

    return results


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    antardhasa_option=1,
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
    Returns the immediate 12 children under a given parent triple/span.

    Output rows: [ [lords_tuple_with_child], child_start_tuple, child_end_tuple ]
    """
    y,m,d,fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y,m,d); tob = (fh,0,0)
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, tuple):
        path = parent_lords
    elif isinstance(parent_lords, list):
        path = tuple(parent_lords)
    else:
        raise TypeError("parent_lords must be tuple/list (path of triples).")

    if len(path) == 0:
        raise ValueError("parent_lords cannot be empty")

    parent_triple = path[-1]

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration_years or parent_end.")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, place, parent_years)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )

    child_level = len(path) + 1
    children = _get_children_jds(
        path, parent_triple, start_jd, end_jd, parent_years,
        place, child_level, planet_positions, antardhasa_from_lord_of_dhasa_sign,
    )

    rows = []
    for child_path, _child_triple, c_start, c_end, _c_years in children:
        if c_end > c_start:
            rows.append([list(child_path), _jd_to_tuple(c_start), _jd_to_tuple(c_end)])

    if rows:
        rows[-1][2] = _jd_to_tuple(end_jd)

    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    use_sidereal=False,
    antardhasa_from_lord_of_dhasa_sign=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Returns the running dasa/antardasa/... chain, from Mahadasha down to
    the requested depth, for current_jd.

        [ [[triple1], start1, end1], [[triple1, triple2], start2, end2], ... ]

    If current_jd falls before jd_at_dob, it is clamped to jd_at_dob.
    """
    _set_year_duration(
        jd_at_dob, place,
        use_sidereal=use_sidereal,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = const.MAHA_DHASA_DEPTH.DEHA
    target_depth = max(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, min(const.MAHA_DHASA_DEPTH.DEHA, target_depth))

    if current_jd < jd_at_dob:
        current_jd = jd_at_dob

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

    cursor_jd = jd_at_dob
    chosen = None
    for _cycle in range(_MAX_CYCLE_SEARCH):
        cycle_end_jd = _bounded_end_jd(cursor_jd, place, 12.0)
        md_children = _get_children_jds(
            (), base_triple, cursor_jd, cycle_end_jd, 12.0,
            place, 1, planet_positions, antardhasa_from_lord_of_dhasa_sign,
        )
        for child_path, child_triple, c_start, c_end, c_years in md_children:
            if c_start <= current_jd < c_end:
                chosen = (child_path, child_triple, c_start, c_end, c_years)
                break
        if chosen is not None:
            break
        cursor_jd = cycle_end_jd

    if chosen is None:
        chosen = (child_path, child_triple, c_start, c_end, c_years)

    parent_path, parent_triple, parent_start, parent_end, parent_years = chosen
    ladder = [[list(parent_path), utils.jd_to_gregorian(parent_start), utils.jd_to_gregorian(parent_end)]]

    if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        return ladder

    for level in range(2, target_depth + 1):
        children = _get_children_jds(
            parent_path, parent_triple, parent_start, parent_end, parent_years,
            place, level, planet_positions, antardhasa_from_lord_of_dhasa_sign,
        )
        chosen_child = None
        for child_path, child_triple, c_start, c_end, c_years in children:
            if c_start <= current_jd < c_end:
                chosen_child = (child_path, child_triple, c_start, c_end, c_years)
                break
        if chosen_child is None:
            chosen_child = children[-1]

        parent_path, parent_triple, parent_start, parent_end, parent_years = chosen_child
        ladder.append([list(parent_path), utils.jd_to_gregorian(parent_start), utils.jd_to_gregorian(parent_end)])

    return ladder


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    import time

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        for flag in [False, True]:
            print(f"\n--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss}, antardhasa_from_lord_of_dhasa_sign={flag} ---")
            start_time = time.time()
            grd = get_running_dhasa_for_given_date(
                current_jd, jd_at_dob, place,
                dhasa_level_index=DLI,
                dhasa_duration_type=dd,
                antardhasa_from_lord_of_dhasa_sign=flag,
            )
            for row in grd:
                raasi_tuples, start, end = row
                lord_str = ",".join(
                    "(" + "-".join(utils.RAASI_SHORT_LIST[i] for i in t) + ")"
                    for t in raasi_tuples
                )
                start_str = f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])}"
                end_str = f"{end[0]}-{end[1]}-{end[2]} {utils.to_dms(end[3])}"
                print("New:", lord_str, start_str, "To:", end_str)
            print('elapsed time', time.time() - start_time)

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
    scd = get_dhasa_antardhasa(
        jd_at_dob, place, divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
        antardhasa_from_lord_of_dhasa_sign=True
    )
    for row in scd:
        print(row)
