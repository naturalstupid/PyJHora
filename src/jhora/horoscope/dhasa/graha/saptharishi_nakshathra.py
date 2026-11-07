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
    Saptharishi Nakshathra Dasa

    A nakshatra-based dhasa ("Sama" = equal) using 10 consecutive
    nakshatra-lords, each with a fixed, equal 10-year Mahadasa (100 years
    total). The 10 lords are determined by counting backward, in
    27-nakshatra order, from the nakshatra occupied by the chart element
    specified via dhasa_starting_planet (default: Lagna) at birth.

    The first Mahadasa starts exactly at the birth JD with its full,
    unreduced 10-year duration -- no birth-fraction-elapsed adjustment is
    applied (unlike Vimshottari/Ashtottari/Panchottari-style nakshatra
    dhasas).

    Antardasa order (_antardhasa()) is controlled by
    const.ANTARDHASA_OPTION, selecting the starting lord (the dhasa lord
    itself, or the next/previous lord in the cycle) and direction
    (forward/backward through the same 10-lord cycle).

    Every level below Mahadasa (Antara, Pratyantara, Sookshma, Prana,
    Deha) splits its parent's duration EQUALLY across all 10 lords in
    the antardasa sequence.

    Every dasha boundary (Mahadasa and every level below it) is computed
    via drik._get_dhasa_end_jd(), through the _bounded_end_jd() wrapper,
    which falls back to plain linear (duration * year_duration)
    arithmetic if drik._get_dhasa_end_jd() returns a result more than
    _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate. Because
    this dhasa splits 10-way at every level, durations shrink faster per
    level than in dhasas with fewer lords; when a batch of children's
    smallest duration drops below _SUB_DAY_DURATION_DAYS (which for this
    dhasa can occur as early as Prana/PAD level), that batch's boundaries
    are instead computed by equal proportional interpolation of the
    parent's own [start_jd, end_jd] span, since drik._get_dhasa_end_jd()'s
    underlying solar-transit search is not reliable at sub-day
    granularity.
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts


_dhasa_duration = 10  # years per lord, fixed (equal split at Mahadasa level)
_dhasa_count = 10     # number of nakshatra-lords used in the cycle (of 27)
year_duration = const.sidereal_year

# Documentary constant only (10 lords * 10 years); not used in any
# calculation elsewhere in this module.
human_life_span_for_dhasa = 100

# Sanity backstop (in days) against drik._get_dhasa_end_jd() returning a
# result far from the linear (duration * year_duration) estimate for a
# narrow band of small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# Threshold (in days) below which drik._get_dhasa_end_jd()'s solar-transit
# search is not reliable. When a batch of children's smallest duration
# drops below this threshold, that batch's boundaries are computed via
# equal proportional interpolation of the parent's own real span instead
# (see _get_saptharishi_nakshathra_children_jd()). This is a duration-
# triggered check, re-evaluated fresh for each batch of children at
# whatever level they occur -- for this dhasa's 10-way equal split, this
# is expected to trigger starting at Prana (PAD) level, not just Deha.
_SUB_DAY_DURATION_DAYS = 1.0


def _dhasa_adhipathi_list(lord):
    """Returns the dict of {nakshatra_lord: duration_years} for the cycle
    of _dhasa_count nakshatras counting backward from `lord`."""
    return {(lord - i) % 27: _dhasa_duration for i in range(_dhasa_count)}


def _next_adhipati(lord, dhasa_lords, dirn=1):
    """Returns next lord after `lord` in dhasa_lords (a list, not a dict)."""
    current = dhasa_lords.index(lord)
    next_lord = dhasa_lords[(current + dirn) % len(dhasa_lords)]

    return next_lord


def _antardhasa(dhasa_lord, antardhasa_option=None):
    """
    Returns the bhukthi (antardhasa) lord sequence for a given dhasa_lord.

    antardhasa_option should be a const.ANTARDHASA_OPTION enum member (raw
    ints 1-6 are still accepted for backward compatibility since the enum
    is an IntEnum, but new code should always pass the enum member).
    """
    if antardhasa_option is None:
        antardhasa_option = const.antardhasa_option_default

    dhasa_lords = [(dhasa_lord - i) % 27 for i in range(_dhasa_count)]
    lord = dhasa_lord

    if antardhasa_option in [
        const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_BACKWARD,
    ]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords, dirn=1)
    elif antardhasa_option in [
        const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_BACKWARD,
    ]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords, dirn=-1)

    dirn = 1 if antardhasa_option in [
        const.ANTARDHASA_OPTION.START_FROM_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
        const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD,
    ] else -1

    bhukthis = []

    for _ in range(len(dhasa_lords)):
        bhukthis.append(lord)
        lord = _next_adhipati(lord, dhasa_lords, dirn)

    return bhukthis


def _dhasa_progression(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=const._ascendant_symbol,
):
    """
    Determines the 10 nakshatra-lords used for this chart (counting
    backward from the birth nakshatra) and their cyclic order. Only the
    whole-nakshatra index is needed -- this dhasa does not apply a
    birth-fraction-elapsed adjustment.
    """
    from jhora.horoscope.chart import charts as _charts

    planet_long = _charts.get_chart_element_longitude(
        jd=jd,
        place=place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    one_star = 360 / 27.0  # 27 nakshatras span 360 degrees
    nak = int(planet_long / one_star)

    dhasa_progression = [(nak - i) % 27 for i in range(_dhasa_count)]

    return dhasa_progression


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


def _get_saptharishi_nakshathra_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    antardhasa_option=None,
    parent_end_jd=None,
):
    """
    Single children-engine for Saptharishi Nakshathra Dasa.

    Signature:
        (parent_lords, parent_start_jd, parent_duration, place, *,
         antardhasa_option=None, parent_end_jd=None) -> (children, parent_end_jd)

    Rules:
        - Child order via _antardhasa(parent_lord, antardhasa_option).
        - Equal split (dhasa name contains "Sama"): parent_duration
          divided evenly across all children.
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's per-child duration is under
          _SUB_DAY_DURATION_DAYS, all child boundaries (not just the
          last) are computed via equal proportional interpolation of the
          parent's own real [parent_start_jd, parent_end_jd] span,
          instead of calling _bounded_end_jd()/drik._get_dhasa_end_jd()
          per child.

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

    child_duration = parent_duration / n  # EQUAL split (Sama)

    child_duration_days = child_duration * year_duration
    use_proportional_interpolation = child_duration_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd

    for i, clord in enumerate(child_lords):
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            # Equal proportional interpolation within the parent's own
            # real span.
            child_end_jd = parent_start_jd + parent_span * (i + 1) / n
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
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=const._ascendant_symbol,
    use_tribhagi_variation=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    num_cycles=1,
    stop_at_jd=None,
    max_cycles_safety=50,
):
    """
    The single Mahadasa seed/root generator for Saptharishi Nakshathra.
    Cycles the 10 nakshatra-lord progression starting from the birth JD
    (no fraction-elapsed adjustment). get_dhasa_bhukthi() and
    get_running_dhasa_for_given_date() both call this same generator.

    Two mutually exclusive usage modes:
        - num_cycles=N, stop_at_jd=None: yields all Mahadasas across N full
          passes through the lord list.
        - stop_at_jd=<jd>, num_cycles ignored: yields Mahadasas one at a
          time and stops as soon as the yielded period covers stop_at_jd.
          Bounded defensively by max_cycles_safety.

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

    dhasa_progression = _dhasa_progression(
        jd_at_dob,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )

    # No birth-fraction-elapsed adjustment: the first Mahadasa starts
    # exactly at the birth JD with the full, unreduced duration.
    start_jd = jd_at_dob

    total_lords = len(dhasa_progression)
    effective_cycles = max_cycles_safety if stop_at_jd is not None else num_cycles

    for _cycle in range(effective_cycles):
        for dhasa_lord in dhasa_progression:
            maha_dur = _dhasa_duration * tribhagi_factor
            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return


def _find_child_containing_jd(children, target_jd):
    """
    children: list of (lords_tuple, start_jd, duration_years, end_jd) as
    returned by _get_saptharishi_nakshathra_children_jd().

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
    dhasa_starting_planet=const._ascendant_symbol,
    antardhasa_option=None,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Returns a list of dasha segments at the selected depth level for
    Saptharishi Nakshathra Dasa.

    @param dob: Date Struct (year,month,day)
    @param tob: time tuple (h,m,s)
    @param place: Place as tuple (place name, latitude, longitude, timezone)
    @param divisional_chart_factor Default=1
    @param chart_method: Default=1
    @param star_position_from_moon: 1=Moon(default), 4=Kshema, 5=Utpanna, 8=Adhana
    @param use_tribhagi_variation: False (default), True => durations scaled to 1/3 with 3 cycles
    @param dhasa_starting_planet 0=Sun 1=Moon...8=Ketu, 'L'=Lagna(default),
        "Md" for Maandi, "BL" for Bhava Lagna "S1" Tri-sphuta etc
    @param antardhasa_option: const.ANTARDHASA_OPTION enum member (defaults
        to const.antardhasa_option_default when None)
    @param dhasa_level_index: Depth 1..6 (1=Maha only, 2=+Antara, 3=+Pratyantara, 4=+Sookshma, 5=+Prana, 6=+Deha)
    @param round_duration: If True, round only the returned duration values to dhasa_level_index

    Return format:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level, including Deha, unless a batch of
    children is sub-day, in which case proportional interpolation of the
    parent's real span is used instead (see _SUB_DAY_DURATION_DAYS above).
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
        children, _ = _get_saptharishi_nakshathra_children_jd(
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
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
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
    Saptharishi Nakshathra immediate children under the given parent span.

    A thin wrapper around the shared
    _get_saptharishi_nakshathra_children_jd() engine.

    Returns:
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

    children, _ = _get_saptharishi_nakshathra_children_jd(
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
    dhasa_starting_planet=const._ascendant_symbol,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Saptharishi Nakshathra runner. Narrows Maha to requested depth.

    Drills down this dhasa's own tree using the same recursive machinery
    as get_dhasa_bhukthi() and saptharishi_nakshathra_immediate_children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd).
        - Every level below Mahadasa: _get_saptharishi_nakshathra_
          children_jd(), then _find_child_containing_jd().
    Stays in JD-float space throughout; only the final returned rows are
    converted to Gregorian tuples.

    Returns:
        [
            [(l1,),              start1, end1],
            [(l1,l2),            start2, end2],
            [(l1,l2,l3),         start3, end3],
            [(l1,l2,l3,l4),      start4, end4],
            [(l1,l2,l3,l4,l5),   start5, end5],
            [(l1,l2,l3,l4,l5,l6),start6, end6],
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

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
        use_tribhagi_variation=use_tribhagi_variation,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        stop_at_jd=current_jd,
    ):
        pass  # generator itself stops once the covering period is yielded

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
        children, _ = _get_saptharishi_nakshathra_children_jd(
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

    y,m,d = (1998,11,9)
    hh,mm,ss = (15,29,45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in [const.DHASA_YEAR_DURATION.TRUE_SIDEREAL_YEAR,
               const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
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
        new_last_name = '-'.join([utils.NAKSHATRA_SHORT_LIST[lord] for lord in new_last_lords])
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
        old_last_name = '-'.join([utils.NAKSHATRA_SHORT_LIST[lord] for lord in old_last_lords])
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
    pvr_tests.saptharishi_nakshathra_test()
