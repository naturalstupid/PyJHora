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
    AK Kendradhi Graha Dasa

    A graha (planet) dasa per Parasara (BPHS), seeded from the Atmakaraka
    (AK) -- the planet with the highest degree within its own sign among
    the 8 chara karakas (Sun through Rahu; Ketu is excluded as a dasa
    lord, per Parasara's use of the word "karaka" for the dasa lord in
    this verse).

    Seed sign: whichever of AK's own sign or the 7th from it is
    stronger (by rasi-strength comparison) becomes the reference sign
    for the whole Mahadasa sequence.

    Mahadasa order: from the reference sign, the 8 karaka planets are
    grouped by house-relationship to that sign -- kendra (1st, 4th,
    7th, 10th), panaphara (2nd, 5th, 8th, 11th), apoklima (3rd, 6th,
    9th, 12th), reckoned zodiacally. Within each group, planets are
    ordered by the strength of the sign they occupy (ties among
    planets sharing a sign are broken by planet-strength).

    Mahadasa duration: for each planet, count from its occupied sign to
    its own sign (to both signs if a dual-sign owner, taking the larger
    count), zodiacally if the occupied sign is odd-footed, anti-
    zodiacally if even-footed, minus 1 year; +1 year if the planet is
    exalted in its occupied sign, -1 year if debilitated; a planet
    occupying its own sign always gets the maximum of 12 years
    regardless of exaltation.

    Antardasa: the same 8-planet order established for the Mahadasas,
    rotated to start at the current Mahadasa's own lord (wrapping
    through all 8), with each Antardasa's duration proportional to that
    lord's own computed Mahadasa-years, divided by the sum of all 8
    planets' Mahadasa-years. The same rule is applied recursively at
    every level below Antardasa (Pratyantara, Sookshma, Prana, Deha).

    Sign-strength and planet-strength comparisons use
    house.stronger_rasi_from_planet_positions()/house.order_of_raasis_
    by_strength() and house.stronger_planet_from_planet_positions(),
    with use_dignity_tier_for_rule3=True: Rule-3 of the sign-strength
    ladder (normally a binary "contains an exalted planet, yes/no"
    check) is instead the fuller dignity comparison of the best-placed
    resident planet in each sign (exalted > moolatrikona > own > friend
    > neutral > enemy > debilitated) -- needed to correctly resolve
    ties where one sign's resident planet is in its own sign but not
    exalted (e.g. Jupiter in Pisces) against another sign's resident
    planet that is in neither its own nor an exalted sign.

    Every dasha boundary (Mahadasa and every level below it) is computed
    via drik._get_dhasa_end_jd(), through the _bounded_end_jd() wrapper,
    which falls back to plain linear (duration * year_duration)
    arithmetic if drik._get_dhasa_end_jd() returns a result more than
    _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate. When a
    batch of children's smallest duration drops below
    _SUB_DAY_DURATION_DAYS, that batch's boundaries are instead computed
    by proportional-by-own-mahadasa-years interpolation of the parent's
    own [start_jd, end_jd] span, since drik._get_dhasa_end_jd()'s
    underlying solar-transit search is not reliable at sub-day
    granularity.
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year

# Sanity backstop (in days) against drik._get_dhasa_end_jd() returning a
# result far from the linear (duration * year_duration) estimate for a
# narrow band of small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# Threshold (in days) below which drik._get_dhasa_end_jd()'s solar-transit
# search is not reliable. When a batch of children's smallest duration
# drops below this threshold, that batch's boundaries are computed via
# proportional-by-own-mahadasa-years interpolation of the parent's own
# real span instead (see _get_children_jd()). This is a duration-
# triggered check, re-evaluated fresh for each batch of children at
# whatever level they occur.
_SUB_DAY_DURATION_DAYS = 1.0

# The 8 chara karakas that receive a dasa (Ketu is excluded).
_KARAKA_PLANET_COUNT = 8

# Each planet's own sign(s) (0=Aries..11=Pisces). Scorpio/Aquarius are
# dual-lorded (Mars/Ketu and Saturn/Rahu respectively); Rahu and Ketu
# each only carry the one sign relevant to their own dasa computation.
_OWN_SIGNS = {
    const.SUN_ID: [4],                    # Leo
    const.MOON_ID: [3],                   # Cancer
    const.MARS_ID: [0, 7],                # Aries, Scorpio
    const.MERCURY_ID: [2, 5],             # Gemini, Virgo
    const.JUPITER_ID: [8, 11],            # Sagittarius, Pisces
    const.VENUS_ID: [1, 6],               # Taurus, Libra
    const.SATURN_ID: [9, 10],             # Capricorn, Aquarius
    const.RAHU_ID: [10],                  # Aquarius (dual lord of Aquarius)
    const.KETU_ID: [7],                   # Scorpio (dual lord of Scorpio)
}


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


def _mahadasa_duration_for_planet(planet_positions, planet, occupied_house):
    """
    Counts from the occupied sign to the planet's own sign (both signs
    if a dual-sign owner, taking the larger count), zodiacally if the
    occupied sign is odd-footed, anti-zodiacally if even-footed, minus
    1 year. +1 year if the planet is exalted in the occupied sign, -1
    year if debilitated. A planet occupying its own sign always gets
    the maximum of 12 years, regardless of exaltation/debilitation.
    """
    own_signs = _OWN_SIGNS[planet]

    def _count_to_sign(own_sign):
        if occupied_house in const.even_footed_signs:
            if own_sign < occupied_house:
                count = occupied_house - own_sign + 1
            else:
                count = occupied_house + 13 - own_sign
        else:
            if own_sign > occupied_house:
                count = own_sign - occupied_house + 1
            else:
                count = own_sign + 13 - occupied_house
        count -= 1

        strength = const.house_strengths_of_planets[planet][occupied_house]
        if strength == const._EXALTED_UCCHAM:
            count += 1
        elif strength == const._DEBILITATED_NEECHAM:
            count -= 1

        if occupied_house == own_sign:
            count = 12

        if count <= 0:
            count = 12

        return count

    return max(_count_to_sign(s) for s in own_signs)


def _mahadasa_lords_and_years(planet_positions):
    """
    Determines the fixed 8-lord Mahadasa sequence and each lord's own
    Mahadasa duration (in years), for this chart.

    Returns:
        (lords, years) -- both length 8, in Mahadasa order.
    """
    karakas = house.chara_karakas(planet_positions)
    ak_planet = karakas[0]

    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    ak_house = p_to_h[ak_planet]
    seventh_from_ak = (ak_house + 6) % 12

    reference_sign = house.stronger_rasi_from_planet_positions(
        planet_positions, ak_house, seventh_from_ak,
        use_dignity_tier_for_rule3=True,
    )

    kendra = [(reference_sign + i) % 12 for i in (0, 3, 6, 9)]
    panaphara = [(reference_sign + i) % 12 for i in (1, 4, 7, 10)]
    apoklima = [(reference_sign + i) % 12 for i in (2, 5, 8, 11)]

    full_strength_order = house.order_of_raasis_by_strength(
        planet_positions, use_dignity_tier_for_rule3=True,
    )

    def _signs_in_strength_order(group_signs):
        return [s for s in full_strength_order if s in group_signs]

    def _planets_in_group(group_signs):
        result = []
        for sign in _signs_in_strength_order(group_signs):
            occupants = [
                p for p in range(const.KETU_ID + 1)
                if planet_positions[p + 1][1][0] == sign
            ]
            if len(occupants) > 1:
                from functools import cmp_to_key

                def _compare(planet1, planet2):
                    stronger = house.stronger_planet_from_planet_positions(
                        planet_positions, planet1, planet2,
                    )
                    return -1 if stronger == planet1 else 1

                occupants = sorted(occupants, key=cmp_to_key(_compare))
            result.extend(occupants)
        return result

    lords = (
        _planets_in_group(kendra)
        + _planets_in_group(panaphara)
        + _planets_in_group(apoklima)
    )

    # Ketu occupies a slot in the strength ordering above (it can
    # determine which planets are grouped/ordered alongside it), but
    # does not itself receive a Mahadasa -- only the 8 chara karakas do.
    lords = [p for p in lords if p != const.KETU_ID]

    years = [
        _mahadasa_duration_for_planet(planet_positions, p, p_to_h[p])
        for p in lords
    ]

    return lords, years


def _get_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    lords,
    years,
    *,
    parent_end_jd=None,
):
    """
    Single children-engine for AK Kendradhi Graha Dasa (used at every
    level below Mahadasa).

    Rules:
        - Child order: the same fixed 8-lord Mahadasa sequence, rotated
          to start at the parent's own lord (wrapping through all 8).
        - Proportional-by-own-mahadasa-years split: each child's share
          of parent_duration is that lord's own Mahadasa-years, divided
          by the sum of all 8 lords' own Mahadasa-years.
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd
          when not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's smallest child duration is under
          _SUB_DAY_DURATION_DAYS, all child boundaries (not just the
          last) are computed via proportional-by-own-mahadasa-years
          interpolation of the parent's own real span, instead of
          calling drik._get_dhasa_end_jd() per child.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    parent_lord = parent_path[-1]

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    child_lords = lords ### All Children Follow Same Maha Lord Sequence

    total_years = sum(years)
    child_own_years = [years[lords.index(cl)] for cl in child_lords]
    child_durations = [parent_duration * y / total_years for y in child_own_years]

    smallest_child_days = min(child_durations) * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(child_durations)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, (child_lord, child_duration) in enumerate(zip(child_lords, child_durations)):
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_duration += child_duration
            child_end_jd = parent_start_jd + parent_span * cumulative_duration / total_child_duration
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                parent_path + (child_lord,),
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
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    num_cycles=1,
    stop_at_jd=None,
    max_cycles_safety=50,
):
    """
    The single Mahadasa seed/root generator for AK Kendradhi Graha Dasa.
    Computes the chart once, determines the fixed 8-lord sequence and
    each lord's own Mahadasa duration, then cycles through them starting
    from the birth JD. get_dhasa_antardhasa() and get_running_dhasa_for_
    given_date() both call this same generator.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd, lords, years)
        (lords, years) are the full fixed 8-lord sequence/duration table
        for this chart, threaded down so deeper levels never need to
        recompute the chart.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
    )

    lords, md_years = _mahadasa_lords_and_years(planet_positions)

    total_lords = len(lords)
    effective_cycles = max_cycles_safety if stop_at_jd is not None else num_cycles

    start_jd = jd_at_dob

    for _cycle in range(effective_cycles):
        for i in range(total_lords):
            dhasa_lord = lords[i]
            maha_dur = md_years[i]
            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd, lords, md_years

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return


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
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Returns AK Kendradhi Graha dhasa segments at the selected depth
    level.

    Return format:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]

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
        lords,
        md_years,
    ):
        children, _ = _get_children_jd(
            parent_lords_tuple,
            parent_start_jd,
            parent_duration_years,
            place,
            lords,
            md_years,
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
                    lords,
                    md_years,
                )
            else:
                _emit_row(
                    child_lords,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd, lords, md_years in _generate_mahadasa_periods(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        num_cycles=1,
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
                const.MAHA_DHASA_DEPTH.ANTARA,
                (maha_lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
                lords,
                md_years,
            )

    return retval


def karaka_kendradhi_graha_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    AK Kendradhi Graha Dasa -- return ONLY the immediate (p -> p+1)
    children under the given parent span.

    A thin wrapper around the shared _get_children_jd() engine, which
    also backs get_dhasa_antardhasa() and get_running_dhasa_for_given_
    date().

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
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end.")

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
    )
    lords, md_years = _mahadasa_lords_and_years(planet_positions)

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    children, _ = _get_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        lords,
        md_years,
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
    AK Kendradhi Graha Dasa runner. Narrows Maha to requested depth.

    Drills down this dasa's own tree using the same recursive machinery
    as get_dhasa_antardhasa() and karaka_kendradhi_graha_immediate_
    children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd).
        - Every level below Mahadasa: _get_children_jd(), then
          _find_child_containing_jd().
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
    lords = md_years = None

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd, lords, md_years in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        stop_at_jd=current_jd,
    ):
        pass  # generator itself stops once the covering period is yielded

    if maha_lord is None:
        return []

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
        children, _ = _get_children_jd(
            parent_lords,
            parent_start_jd,
            parent_duration_years,
            place,
            lords,
            md_years,
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
            break

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


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1963, 8, 7)
    dob = drik.Date(1996,12,7)
    tob = (21, 15, 0)
    tob = (10,34,0)
    place = drik.Place('Sambalpur,IN', 21.45, 83.9667, +5.5)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    # ---- Print Mahadasa list ----
    _md = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    print("=== Mahadasas ===")
    for row in _md:
        lords, (y, m, d, fh), dur = row
        print(f"{utils.PLANET_SHORT_NAMES[lords[0]]} {y}-{m:02d}-{d:02d} {utils.to_dms(fh)}  dur={dur:.4f}")

    # ---- Print Antardasas for Saturn's MD ----
    _ad = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
    print("\n=== Antardasas (grouped by MD) ===")
    import itertools
    for md_lord, group in itertools.groupby(_ad, key=lambda r: r[0][0]):
        group = list(group)
        md_name = utils.PLANET_SHORT_NAMES[md_lord]
        print(f"\n{md_name} MD:")
        for lords, (y, m, d, fh), dur in group:
            ad_lord = lords[1]
            ad_name = utils.PLANET_SHORT_NAMES[ad_lord]
            print(f"  {ad_name:5s} {y}-{m:02d}-{d:02d} {utils.to_dms(fh)}  dur={dur:.4f}")
    y,m,d=(1998,11,9)
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
        new_last_lords, new_last_start, new_last_end = grd[-1]
        new_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord] for lord in new_last_lords])
        y1, m1, d1, fh1 = new_last_start
        y2, m2, d2, fh2 = new_last_end
        print("Dehā (new)  :", check_date,
              [new_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('new method elapsed time', time.time() - start_time)

        # ---- OLD method: full tree, extract only the last (Deha) row,
        #      via the SELF-CONTAINED groupby (NOT jhora.utils) -----------
        start_time = time.time()
        full_tree = get_dhasa_antardhasa(
            dob, tob,
            place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
            return_exact_bounds=True,
        )
        deha_groups = utils._group_ancestors_from_leaves(full_tree, DLI)
        old_last_lords, old_start_jd, old_end_jd = utils._find_containing_group(deha_groups, current_jd)
        old_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord] for lord in old_last_lords])
        y1, m1, d1, fh1 = utils._jd_to_tuple(old_start_jd)
        y2, m2, d2, fh2 = utils._jd_to_tuple(old_end_jd)
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
