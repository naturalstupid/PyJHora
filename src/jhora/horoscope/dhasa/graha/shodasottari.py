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
    Release History:
        V4.8.9 - minor argument call fixes.
        V4.9.0 - dhasa start date calculation now uses drik._get_dhasa_star_jd()
                to calculate dhasa start date using how much Sun has tranversed.
        V5.0   - REFACTORED to match JHora
    
    Shodasottari Dasa

    A nakshatra-based dhasa applicable when Lagna is in Sun's hora during
    Sukla Paksha, or in Moon's hora during Krishna Paksha.

    The 27 nakshatras are cycled starting from mahadasa_seed_star
    (default 8, Poosam), assigning each lord's own Mahadasa duration
    (Sun=11, Mars=12, Jupiter=13, Saturn=14, Rahu=15, Moon=16,
    Mercury=17, Venus=18, total 116 years).

    Antardasa order (_antardhasa()) is controlled by
    const.ANTARDHASA_OPTION, selecting the starting lord (the dhasa lord
    itself, or the next/previous lord in the cycle) and direction
    (forward/backward through dhasa_adhipathi_list). The default is
    "Jupiter's way" (start at the Mahadasa lord itself, go forward),
    matching real JHora output for this dhasa.

    Every level below Mahadasa (Antara, Pratyantara, Sookshma, Prana,
    Deha) splits its parent's duration proportionally by lord-years:
    each child's share of the parent's duration equals that lord's own
    entry in dhasa_adhipathi_list, divided by the sum of all 8 lords'
    entries (116).

    Every dasha boundary (Mahadasa and every level below it) is computed
    via drik._get_dhasa_end_jd(), through the _bounded_end_jd() wrapper,
    which falls back to plain linear (duration * year_duration)
    arithmetic if drik._get_dhasa_end_jd() returns a result more than
    _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate. Because
    of this dhasa's 11-18 year Mahadasa spread, the smallest-lord worst
    case can reach sub-day duration starting at Prana (PAD) level; when a
    batch of children's smallest duration drops below
    _SUB_DAY_DURATION_DAYS, that batch's boundaries are instead computed
    by proportional-by-lord-years interpolation of the parent's own
    [start_jd, end_jd] span, since drik._get_dhasa_end_jd()'s underlying
    solar-transit search is not reliable at sub-day granularity.
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts


year_duration = const.sidereal_year

"""Applicability: Lagna in Sun's hora in Sukla paksha or Lagna in Moon's hora in Krishna paksha."""

mahadasa_seed_star = 8  # Poosam
seed_lord = 0

# Total 116 years. This same per-lord years value is also used as the
# proportion for every level below Mahadasa (see
# _get_shodasottari_children_jd).
dhasa_adhipathi_list = {
    0: 11,  # Sun
    2: 12,  # Mars
    4: 13,  # Jupiter
    6: 14,  # Saturn
    8: 15,  # Rahu
    1: 16,  # Moon
    3: 17,  # Mercury
    5: 18,  # Venus
}

_TOTAL_DHASA_YEARS = sum(dhasa_adhipathi_list.values())  # 116

# count_direction:
#   1  => zodiac (forward)
#  -1  => anti-zodiac (backward)
count_direction = 1

# Sanity backstop (in days) against drik._get_dhasa_end_jd() returning a
# result far from the linear (duration * year_duration) estimate for a
# narrow band of small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# Threshold (in days) below which drik._get_dhasa_end_jd()'s solar-transit
# search is not reliable. For this dhasa (11-18 year Mahadasa spread),
# worst-case duration reaches sub-day starting at Prana (PAD) level. This
# check is duration-triggered, re-evaluated fresh per batch of children,
# never hardcoded to a specific level.
_SUB_DAY_DURATION_DAYS = 1.0


def _next_adhipati(lord, dirn=None):
    """Returns next lord after lord in the adhipati list.

    dirn defaults to the module-level count_direction when not explicitly
    overridden by the caller.
    """
    if dirn is None:
        dirn = count_direction

    keys = list(dhasa_adhipathi_list.keys())
    current = keys.index(lord)
    next_lord = keys[(current + dirn) % len(keys)]

    return next_lord


def _get_dhasa_dict(seed_star=mahadasa_seed_star):
    dhasa_dict = {k: [] for k in dhasa_adhipathi_list.keys()}

    nak = seed_star - 1
    lord = seed_lord
    lord_index = list(dhasa_adhipathi_list.keys()).index(lord)

    for _ in range(27):
        dhasa_dict[lord].append(nak + 1)
        nak = (nak + count_direction) % 27
        lord_index = (lord_index + 1) % len(dhasa_adhipathi_list)
        lord = list(dhasa_adhipathi_list.keys())[lord_index]

    return dhasa_dict


def _maha_dhasa(nak, seed_star=mahadasa_seed_star):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)

    return [
        (_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord])
        for _dhasa_lord, _star_list in dhasa_adhipathi_dict.items()
        if nak in _star_list
    ][0]


def _antardhasa(dhasa_lord, antardhasa_option=None):
    """
    Returns the bhukthi (antardhasa) lord sequence for a given dhasa_lord.

    Defaults to const.antardhasa_option_default -- start at the Mahadasa
    lord itself, go forward ("Jupiter's way") -- matching real JHora
    output for this dhasa (see module docstring, V5.1).
    """
    if antardhasa_option is None:
        antardhasa_option = const.antardhasa_option_default

    lord = dhasa_lord

    if antardhasa_option in [
        const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_BACKWARD,
    ]:
        lord = _next_adhipati(dhasa_lord, dirn=1)
    elif antardhasa_option in [
        const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_BACKWARD,
    ]:
        lord = _next_adhipati(dhasa_lord, dirn=-1)

    dirn = 1 if antardhasa_option in [
        const.ANTARDHASA_OPTION.START_FROM_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD,
    ] else -1

    bhukthis = []

    for _ in range(len(dhasa_adhipathi_list)):
        bhukthis.append(lord)
        lord = _next_adhipati(lord, dirn)

    return bhukthis


def _dhasa_start(
    jd,
    place,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=mahadasa_seed_star,
    dhasa_starting_planet=1,
):
    one_star = 360 / 27.0

    planet_long = charts.get_chart_element_longitude(
        jd=jd,
        place=place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    nak = int(planet_long / one_star)
    rem = planet_long - nak * one_star

    lord, res = _maha_dhasa(nak + 1, seed_star)
    fraction_elapsed = rem / one_star

    start_jd = drik._get_dhasa_start_jd(
        jd,
        place,
        fraction_elapsed=fraction_elapsed,
        total_dasa_years=res,
    )

    return [lord, start_jd, res]


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, via
    drik._get_dhasa_end_jd(), falling back to plain linear
    (duration_years * year_duration) arithmetic if that result is more
    than _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate.
    """
    end_jd = drik._get_dhasa_end_jd(
        start_jd=start_jd_local,
        place=place,
        total_dasa_years=duration_years,
    )

    expected_jd = start_jd_local + duration_years * year_duration

    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd

    return end_jd


def _get_shodasottari_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    antardhasa_option=None,
    parent_end_jd=None,
):
    """
    Single children-engine for Shodasottari Dasa.

    Rules:
        - Child order via _antardhasa(parent_lord, antardhasa_option) --
          defaults to the project-wide convention ("Jupiter's way",
          start at self, forward).
        - Proportional-by-lord-years split: each child's share of
          parent_duration is that lord's own entry in
          dhasa_adhipathi_list, divided by _TOTAL_DHASA_YEARS (116).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's smallest child's own computed duration is under
          _SUB_DAY_DURATION_DAYS, all of that batch's boundaries (not
          just the last) are computed via proportional-by-lord-years
          interpolation of the parent's own real span, instead of calling
          drik._get_dhasa_end_jd() per child.

    Returns:
        children: list of
            (child_lords_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    path = tuple(parent_lords) if isinstance(parent_lords, (list, tuple)) else (parent_lords,)
    parent_lord = path[-1]

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    child_lords = list(
        _antardhasa(
            parent_lord,
            antardhasa_option=antardhasa_option,
        )
    )

    n = len(child_lords)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = parent_duration * min(
        dhasa_adhipathi_list[cl] for cl in child_lords
    ) / _TOTAL_DHASA_YEARS
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd
    cumulative_years = 0.0

    for i, clord in enumerate(child_lords):
        child_duration = parent_duration * dhasa_adhipathi_list[clord] / _TOTAL_DHASA_YEARS

        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_years += dhasa_adhipathi_list[clord]
            child_end_jd = parent_start_jd + parent_span * cumulative_years / _TOTAL_DHASA_YEARS
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                path + (clord,),
                child_start_jd,
                child_duration,
                child_end_jd,
            )
        )

        cursor = child_end_jd

    return children, parent_end_jd


def _generate_mahadasa_periods(
    jd_at_dob,
    place,
    *,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=mahadasa_seed_star,
    dhasa_starting_planet=1,
    use_tribhagi_variation=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    num_cycles=1,
    stop_at_jd=None,
    max_cycles_safety=50,
):
    """
    The single Mahadasa seed/root generator for Shodasottari. Cycles
    dhasa_adhipathi_list starting from the birth lord/start_jd.
    get_dhasa_antardhasa() and get_running_dhasa_for_given_date() both
    call this same generator.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd)
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    tribhagi_factor = (1.0 / 3.0) if use_tribhagi_variation else 1.0

    dhasa_lord, start_jd, _ = _dhasa_start(
        jd_at_dob,
        place,
        star_position_from_moon=star_position_from_moon,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    total_lords = len(dhasa_adhipathi_list)
    effective_cycles = max_cycles_safety if stop_at_jd is not None else num_cycles

    for _cycle in range(effective_cycles):
        for _ in range(total_lords):
            maha_dur = dhasa_adhipathi_list[dhasa_lord] * tribhagi_factor
            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return

            dhasa_lord = _next_adhipati(dhasa_lord)


def _find_child_containing_jd(children, target_jd):
    """
    Returns the single child tuple whose [start_jd, end_jd) contains
    target_jd. Falls back to the last child if target_jd is at/past the
    final boundary.
    """
    if not children:
        return None

    for child in children:
        _, s, _, e = child

        if s <= target_jd < e:
            return child

    return children[-1]


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    seed_star=mahadasa_seed_star,
    dhasa_starting_planet=1,
    antardhasa_option=None,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Returns Shodasottari dhasa segments at the selected depth level.

    antardhasa_option: defaults to None, which resolves to the same
    project-wide convention used everywhere else in this project
    ("Jupiter's way" -- start at self, go forward). See module
    docstring (V5.1) and _antardhasa() docstring above.
    """
    global year_duration

    utils.validate_star_index(seed_star)

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

    dhasa_cycles = 3 if use_tribhagi_variation else 1

    retval = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            retval.append(
                [
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                ]
            )
        else:
            durn = (
                round(duration_years, dhasa_level_index + 1)
                if round_duration
                else duration_years
            )

            retval.append(
                [
                    lords_tuple,
                    utils.jd_to_gregorian(start_jd_local),
                    durn,
                ]
            )

    def _recurse(
        level,
        parent_lords_tuple,
        parent_start_jd,
        parent_duration_years,
        parent_end_jd,
    ):
        children, _ = _get_shodasottari_children_jd(
            parent_lords_tuple,
            parent_start_jd,
            parent_duration_years,
            place,
            antardhasa_option=antardhasa_option,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_lords, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(
                    level + 1,
                    child_lords,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )
            else:
                _emit_row(
                    child_lords,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd,
        place,
        star_position_from_moon=star_position_from_moon,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        use_tribhagi_variation=use_tribhagi_variation,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        num_cycles=dhasa_cycles,
    ):
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row(
                (maha_lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
            )
        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_lords_tuple=(maha_lord,),
                parent_start_jd=maha_start_jd,
                parent_duration_years=maha_dur,
                parent_end_jd=maha_end_jd,
            )

    return retval


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=mahadasa_seed_star,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Nakshathra dhasa progression.
    """
    utils.validate_star_index(seed_star)

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    DLI = dhasa_level_index

    vd = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        dhasa_level_index=DLI,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    vdc = None

    if get_running_dhasa:
        vd_for_utils = [(row[0], row[1]) for row in vd]

        vdc = utils.get_running_dhasa_for_given_date(
            jd_current,
            vd_for_utils,
        )

        print(vdc)

    jds = [
        utils.julian_day_number(
            drik.Date(row[1][0], row[1][1], row[1][2]),
            (row[1][3], 0, 0),
        )
        for row in vd
    ]

    planet_long = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=1,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    birth_star_index = int((planet_long % 360.0) // utils.ONE_NAK)

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


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    antardhasa_option=None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Shodasottari immediate children under the given parent span.
    Thin wrapper around the shared _get_shodasottari_children_jd() engine.
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
        return utils.julian_day_number(
            drik.Date(y, m, d),
            (fh, 0, 0),
        )

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end.")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    children, _ = _get_shodasottari_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        antardhasa_option=antardhasa_option,
        parent_end_jd=end_jd,
    )

    return [
        [
            child_lords,
            _jd_to_tuple(child_start_jd),
            _jd_to_tuple(child_end_jd),
        ]
        for child_lords, child_start_jd, _child_duration, child_end_jd in children
    ]


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    antardhasa_option=None,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    seed_star=mahadasa_seed_star,
    dhasa_starting_planet=1,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Shodasottari runner. Narrows Maha to requested depth.

    Drills down this dhasa's own tree using the same recursive machinery
    as get_dhasa_antardhasa() and shodasottari_immediate_children().
    """
    global year_duration

    utils.validate_star_index(seed_star)

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

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        star_position_from_moon=star_position_from_moon,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        use_tribhagi_variation=use_tribhagi_variation,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        stop_at_jd=current_jd,
    ):
        pass

    running_all = [
        [
            (maha_lord,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    parent_lords = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_shodasottari_children_jd(
            parent_lords,
            parent_start_jd,
            parent_duration_years,
            place,
            antardhasa_option=antardhasa_option,
            parent_end_jd=parent_end_jd,
        )

        found = _find_child_containing_jd(children, current_jd)

        if found is None:
            running_all.append(
                [
                    parent_lords + (parent_lords[-1],),
                    utils.jd_to_gregorian(parent_start_jd),
                    utils.jd_to_gregorian(parent_end_jd),
                ]
            )
            continue

        child_lords, child_start_jd, child_duration_years, child_end_jd = found

        running_all.append(
            [
                child_lords,
                utils.jd_to_gregorian(child_start_jd),
                utils.jd_to_gregorian(child_end_jd),
            ]
        )

        parent_lords = child_lords
        parent_start_jd = child_start_jd
        parent_end_jd = child_end_jd
        parent_duration_years = child_duration_years

    return running_all

'------ main -----------'
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    # ---- Print Mahadasa list ----
    _md = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    print("=== Mahadasas ===")
    for row in _md:
        lords, (y, m, d, fh), dur = row
        print(f"{utils.PLANET_SHORT_NAMES[lords[0]] if lords[0] != 'L' else 'Asc'} "
              f"{y}-{m:02d}-{d:02d} {utils.to_dms(fh)}  dur={dur:.4f}")

    # ---- Print Antardasas for the first 4 Mahadasas ----
    _ad = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
    print("\n=== Antardasas (grouped by MD) ===")
    import itertools
    for md_lord, group in itertools.groupby(_ad, key=lambda r: r[0][0]):
        group = list(group)
        md_name = utils.PLANET_SHORT_NAMES[md_lord] if md_lord != 'L' else 'Asc'
        print(f"\n{md_name} MD:")
        for lords, (y, m, d, fh), dur in group:
            ad_lord = lords[1]
            ad_name = utils.PLANET_SHORT_NAMES[ad_lord] if ad_lord != 'L' else 'Asc'
            print(f"  {ad_name:5s} {y}-{m:02d}-{d:02d} {utils.to_dms(fh)}  dur={dur:.4f}")

    from datetime import datetime
    import random
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y,m,d = (1998,11,9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh,mm,ss = (15,29,45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        # ---- NEW method: only the last (Deha) row -------------------------
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=DLI,
                dhasa_duration_type=dd,
            )
        print("running_all[4]",grd[4])
        new_last_lords, new_last_start, new_last_end = grd[-1]
        new_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord] for lord in new_last_lords])
        y1, m1, d1, fh1 = new_last_start
        y2, m2, d2, fh2 = new_last_end
        print("Dehā (new)  :", check_date,
              [new_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('new method elapsed time', time.time() - start_time)

        # ---- OLD method: full tree, extract only the last (Deha) row,
        #      via utils' self-contained groupby (shared helpers) ---------
        start_time = time.time()
        full_tree = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
            return_exact_bounds=True,
        )
        deha_groups = utils._group_ancestors_from_leaves(full_tree, DLI)
        old_last_lords, old_start_jd, old_end_jd = utils._find_containing_group(deha_groups, current_jd)
        old_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord] for lord in old_last_lords])
        y1, m1, d1, fh1 = utils.jd_to_gregorian(old_start_jd)
        y2, m2, d2, fh2 = utils.jd_to_gregorian(old_end_jd)
        print("Dehā (old)  :", check_date,
              [old_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('old method elapsed time', time.time() - start_time)

        # ---- Diff between OLD and NEW (last/Deha row only) ----------------
        lords_match = tuple(new_last_lords) == tuple(old_last_lords)
        start_diff_seconds = (utils._tuple_to_jd(new_last_start) - old_start_jd) * 86400.0
        end_diff_seconds = (utils._tuple_to_jd(new_last_end) - old_end_jd) * 86400.0

        print("\n" + "-" * 80)
        print("DIFF (new - old), Deha level only:")
        print("  lords match      :", lords_match, f"({new_last_name}  vs  {old_last_name})")
        print(f"  start diff (sec) : {start_diff_seconds:+.3f}")
        print(f"  end   diff (sec) : {end_diff_seconds:+.3f}")
        print("-" * 80)
    exit()
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.shodasottari_test()
