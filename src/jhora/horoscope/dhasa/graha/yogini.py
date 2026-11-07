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
    Yogini Dasha (nakshatra-based, 8 lords, 36-year cycle x 3 = 108 years)

    Release History:
        V4.8.9 - minor argument call fixes.
        V4.9.0 - dhasa start date calculation now uses drik._get_dhasa_star_jd()
                to calculate dhasa start date using how much Sun has traversed.
        V5.0   - REFACTORED  to match JHora.
"""
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, sphuta


year_duration = const.sidereal_year

"""dhasa_adhipathi_dict = {planet: [star list]}"""

seed_lord = 0
_seed_star = 1

# Total 36 years.
dhasa_adhipathi_list = {
    1: 1,
    0: 2,
    4: 3,
    2: 4,
    3: 5,
    6: 6,
    5: 7,
    7: 8,
}

dhasa_adhipathi_dict = {
    1: [6, 14, 22],
    0: [7, 15, 23],
    4: [8, 16, 24],
    2: [1, 9, 17, 25],
    3: [2, 10, 18, 26],
    6: [3, 11, 19, 27],
    5: [4, 12, 20],
    7: [5, 13, 21],
}

count_direction = 1

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3) -- same mechanism already used in every other refactored dhasa module
# in this project.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in every other dhasa module refactored in this
# project) to become unreliable by a real, non-trivial margin. For THIS
# dhasa (8-way equal splits cascading from a 1-8 year Mahadasa), worst-
# case duration reaches sub-day starting around PAD level for an average-
# sized Mahadasa (~0.401 days), sooner for the smallest (1-year) Mahadasa.
# This check is duration-triggered, re-evaluated fresh for every batch of
# children, regardless of level.
_SUB_DAY_DURATION_DAYS = 1.0


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, guarding
    against drik._get_dhasa_end_jd()'s known unreliability for small
    durations. Every ANTARA-level-and-below boundary in this module now
    routes through this wrapper, per the project's standing direction to
    apply real end_jd at every level (the Mahadasa level itself already
    correctly used drik._get_dhasa_end_jd() in the pre-refactor draft, via
    _next_jd_by_dhasa_years() -- see module docstring above).
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


def _next_adhipati(lord, dirn=1):
    """Returns next lord after lord in the adhipati list. UNCHANGED."""
    keys = list(dhasa_adhipathi_list.keys())
    current = keys.index(lord)
    next_lord = keys[(current + dirn) % len(keys)]

    return next_lord


def _maha_dhasa(nak, seed_star=_seed_star):
    """UNCHANGED from the pre-refactor draft."""
    return [
        (_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord])
        for _dhasa_lord, _star_list in dhasa_adhipathi_dict.items()
        if ((nak - seed_star) % 27) + 1 in _star_list
    ][0]


def _antardhasa(lord, antardhasa_option=1):
    """
    UNCHANGED from the pre-refactor draft. 6 variant modes controlling
    which lord starts the antara sequence and the stepping direction
    through the fixed 8-lord cycle.
    """
    if antardhasa_option in [3, 4]:
        lord = _next_adhipati(lord, dirn=1)
    elif antardhasa_option in [5, 6]:
        lord = _next_adhipati(lord, dirn=-1)

    dirn = 1 if antardhasa_option in [1, 3, 5] else -1

    bhukthis = []

    for _ in range(len(dhasa_adhipathi_list)):
        bhukthis.append(lord)
        lord = _next_adhipati(lord, dirn=dirn)

    return bhukthis


def _dhasa_start(
    jd_at_dob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    seed_star=_seed_star,
    dhasa_starting_planet=1,
):
    """
    UNCHANGED from the pre-refactor draft. Already uses real
    drik._get_dhasa_start_jd() (fraction-elapsed correction) for the
    Mahadasa's own start -- see module docstring above.
    """
    one_star = 360 / 27.0

    planet_long = charts.get_chart_element_longitude(
        jd=jd_at_dob,
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
        jd_at_dob,
        place,
        fraction_elapsed=fraction_elapsed,
        total_dasa_years=res,
    )

    return [lord, start_jd, res]


def _get_yogini_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    antardhasa_option,
    *,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Yogini Dasha (used at every level below
    Mahadasa, by ALL THREE entry points: get_dhasa_bhukthi()'s own
    recursion, yogini_immediate_children(), and get_running_dhasa_for_
    given_date()).

    Rules:
        - Child order = _antardhasa(parent_lord, antardhasa_option) --
          the SAME 6-variant antardhasa rule at every level below
          Mahadasa. UNCHANGED from the pre-refactor draft -- CONFIRMED
          correct against real JHora data (the antara order for every
          parent lord tested matched JHora's own real "Antardasas in
          this MD/PAD" tables exactly).
        - V5.1 REAL BUG FIX: each child's share of parent_duration is
          WEIGHTED by that child's OWN Mahadasa-year weight (dhasa_
          adhipathi_list[child_lord]), out of the fixed total of 36 (the
          sum of all 8 lords' own weights) -- child_duration =
          parent_duration * (dhasa_adhipathi_list[child_lord] / 36) --
          NOT an equal 1/8 split as the pre-refactor draft computed
          (child_duration = parent_duration / len(children)). This
          mirrors the same well-known classical rule already used for
          Vimshottari-family antardhasas (each bhukti lord's share is
          proportional to its OWN total dasha-year weight, not divided
          equally) -- CONFIRMED against real JHora data: the pre-refactor
          draft's equal-split AD duration for Jupiter (under a 3-year
          Jupiter Mahadasa) came out to ~137 days, while JHora's real
          Jupiter Antardasha is ~90 days -- exactly matching the
          weighted formula (3 years * 3/36 = 0.25 years = ~91.3 days).
          Verified further at PD/SD/PAD/Deha levels (Venus PD ~17.4
          days, Rahu SD ~3.9 days) using JHora's own real screenshot
          boundaries -- all reproduce the real JHora durations closely
          (within normal real-vs-mean-year drift, consistent with every
          other correctly-implemented dhasa in this project).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's smallest child duration is under
          _SUB_DAY_DURATION_DAYS, ALL child boundaries (not just the
          last) are computed via weighted proportional interpolation of
          the parent's own real [parent_start_jd, parent_end_jd] span,
          instead of calling _bounded_end_jd()/drik._get_dhasa_end_jd()
          per child.

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

    child_lords = list(_antardhasa(parent_lord, antardhasa_option=antardhasa_option))
    n = len(child_lords)

    if n == 0:
        return [], parent_end_jd

    total_weight = float(sum(dhasa_adhipathi_list.values()))  # always 36 (fixed 8-lord permutation)
    child_durations = [
        parent_duration * (dhasa_adhipathi_list[child_lord] / total_weight)
        for child_lord in child_lords
    ]

    smallest_child_years = min(child_durations)
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(child_durations)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, child_lord in enumerate(child_lords):
        child_duration = child_durations[i]
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
    star_position_from_moon=1,
    seed_star=_seed_star,
    dhasa_starting_planet=1,
    use_tribhagi_variation=False,
    stop_at_jd=None,
):
    """
    THE single Mahadasa seed/root generator for Yogini Dasha. This is the
    ONLY place in the module that computes the seed lord (via
    _dhasa_start()) and walks the fixed 8-lord cycle for 3 full cycles
    (or 9, under tribhagi -- keeping the total at 108 years either way).
    get_dhasa_bhukthi(), yogini_immediate_children() (indirectly, via
    get_running_dhasa_for_given_date()'s own use of this generator), and
    get_running_dhasa_for_given_date() all rely on THIS SAME generator
    for the Mahadasa level.

    UNCHANGED in logic from the pre-refactor draft -- the Mahadasa level
    already correctly used real drik._get_dhasa_start_jd()/_get_dhasa_
    end_jd() boundaries (see module docstring above).

    Yields:
        (lord, maha_start_jd, maha_duration_years, maha_end_jd)
    """
    tribhagi_factor = 1.0
    dhasa_cycles = 3

    if use_tribhagi_variation:
        tribhagi_factor = 1.0 / 3.0
        dhasa_cycles = int(dhasa_cycles / tribhagi_factor)

    dhasa_lord, start_jd, _ = _dhasa_start(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    for _cycle in range(dhasa_cycles):
        for _lord_ix in range(len(dhasa_adhipathi_list)):
            maha_years = float(dhasa_adhipathi_list[dhasa_lord]) * tribhagi_factor

            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_years, place)

            yield dhasa_lord, maha_start_jd, maha_years, maha_end_jd

            start_jd = maha_end_jd
            dhasa_lord = _next_adhipati(dhasa_lord)

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
    use_tribhagi_variation=False,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=_seed_star,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Provides Yogini dhasa-bhukthi for a given birth date and time.

    Uses the SAME shared _generate_mahadasa_periods()/_get_yogini_children_jd()
    engine as yogini_immediate_children() and get_running_dhasa_for_given_date().

    Return format:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    (new parameter, matching the project-wide convention already present
    in every other refactored dhasa module).

    dhasa_level_index:
        1 = Maha only
        2 = Antara
        3 = Pratyantara
        4 = Sookshma
        5 = Prana
        6 = Deha
    """
    utils.validate_star_index(seed_star)

    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6.")

    jd_at_dob = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    rows = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            rows.append(
                [
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                ]
            )
        else:
            start_tuple = utils.jd_to_gregorian(start_jd_local)
            dur_out = round(duration_years, dhasa_level_index) if round_duration else duration_years
            rows.append([lords_tuple, start_tuple, dur_out])

    def _recurse(level, parent_path, parent_start_jd, parent_duration_years, parent_end_jd):
        children, _ = _get_yogini_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            antardhasa_option,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(level + 1, child_path, child_start_jd, child_duration, child_end_jd)
            else:
                _emit_row(child_path, child_start_jd, child_duration, child_end_jd)

    for dhasa_lord, maha_start_jd, maha_years, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        use_tribhagi_variation=use_tribhagi_variation,
    ):
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row((dhasa_lord,), maha_start_jd, maha_years, maha_end_jd)
        else:
            _recurse(
                const.MAHA_DHASA_DEPTH.ANTARA,
                (dhasa_lord,),
                maha_start_jd,
                maha_years,
                maha_end_jd,
            )

    return rows


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=_seed_star,
    antardhasa_option=1,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    UNCHANGED from the pre-refactor draft. A distinct, higher-level
    utility (progressed longitude computation), not a dhasa-tree
    traversal -- not part of the single-engine consolidation.
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
        use_tribhagi_variation=use_tribhagi_variation,
        star_position_from_moon=star_position_from_moon,
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
        vd_for_utils = [(row[0], row[1]) for row in vd]

        vdc = utils.get_running_dhasa_for_given_date(
            jd_current,
            vd_for_utils,
        )

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
    jd_at_dob=None,
    place=None,
    antardhasa_option=1,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=_seed_star,
    dhasa_starting_planet=1,
    use_tribhagi_variation=False,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Yogini immediate children under the given parent span.

    A thin wrapper around the shared _get_yogini_children_jd() engine
    (previously duplicated the antara-order/equal-split logic
    independently from get_dhasa_bhukthi() -- now both call the same
    engine).

    Returns:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]
    """
    utils.validate_star_index(seed_star)

    global year_duration

    if jd_at_dob is not None and place is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

    if place is None:
        raise ValueError("place is required for exact Yogini child boundary calculation.")

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
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    children, _ = _get_yogini_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        antardhasa_option,
        parent_end_jd=end_jd,
    )

    return [
        [
            child_path,
            _jd_to_tuple(child_start_jd),
            _jd_to_tuple(child_end_jd),
        ]
        for child_path, child_start_jd, _child_duration, child_end_jd in children
    ]


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    use_tribhagi_variation=False,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=_seed_star,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Yogini runner. Narrows Maha to requested depth.

    Uses the SAME shared _generate_mahadasa_periods()/_get_yogini_children_jd()
    engine as get_dhasa_bhukthi() and yogini_immediate_children(). The
    Mahadasa level is found via a single early-stopping walk of
    _generate_mahadasa_periods() (stop_at_jd=current_jd) rather than
    rebuilding the FULL Mahadasa-only row list (all 3 -- or 9, under
    tribhagi -- cycles) and handing it to jhora.utils.get_running_dhasa_
    for_given_date() for lookup -- a pure architectural/performance
    consolidation (that utility itself is not being treated as buggy; see
    module docstring above). Every level below Mahadasa uses
    _get_yogini_children_jd() then _find_child_containing_jd(), staying
    in JD-float space throughout (only the final returned rows are
    converted to Gregorian tuples).

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
    utils.validate_star_index(seed_star)

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

    for lord, m_start_jd, m_dur, m_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        use_tribhagi_variation=use_tribhagi_variation,
        stop_at_jd=current_jd,
    ):
        maha_lord, maha_start_jd, maha_dur, maha_end_jd = lord, m_start_jd, m_dur, m_end_jd

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

    parent_path = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_yogini_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            antardhasa_option,
            parent_end_jd=parent_end_jd,
        )

        found = _find_child_containing_jd(children, current_jd)

        if found is None:
            running_all.append(
                [
                    parent_path + (parent_path[-1],),
                    utils.jd_to_gregorian(parent_start_jd),
                    utils.jd_to_gregorian(parent_end_jd),
                ]
            )
            break

        child_path, child_start_jd, child_duration_years, child_end_jd = found

        running_all.append(
            [
                child_path,
                utils.jd_to_gregorian(child_start_jd),
                utils.jd_to_gregorian(child_end_jd),
            ]
        )

        parent_path = child_path
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
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.yogini_test()
