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
"""
from collections import OrderedDict as Dict

from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import house


year_duration = const.sidereal_year
human_life_span_for_ashtottari_dhasa = 108

"""
    {ashtottari adhipati:[(tithis),dasa_length]}
"""

ashtottari_adhipathi_list = [0, 1, 2, 3, 6, 4, 7, 5]

ashtottari_adhipathi_dict = {
    0: [(1, 9, 16, 24), 6],
    1: [(2, 10, 17, 25), 15],
    2: [(3, 11, 18, 26), 8],
    3: [(4, 12, 19, 27), 17],
    6: [(7, 15, 22), 10],
    4: [(5, 13, 20, 28), 19],
    7: [(8, 23, 30), 12],
    5: [(6, 14, 21, 29), 21],
}

_TOTAL_DHASA_YEARS = float(human_life_span_for_ashtottari_dhasa)  # 108

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO protection against this anywhere.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in karana_chathuraaseethi_sama.py, panchottari.py,
# saptharishi_nakshathra.py, sataatbika.py, shastihayani.py,
# shattrimsa_sama.py, shodasottari.py) to become unreliable by a real,
# non-trivial margin. For THIS dhasa (6-21 year Mahadasa spread), worst-
# case duration reaches sub-day starting at SD level (~0.376 days worst
# case). This check is duration-triggered, re-evaluated fresh per batch
# of children, never hardcoded to a specific level.
_SUB_DAY_DURATION_DAYS = 1.0


def _ashtottari_adhipathi(tithi_index):
    for key, value in ashtottari_adhipathi_dict.items():
        tithi_list, durn = value

        if tithi_index in tithi_list:
            return key, durn

    raise ValueError("No Ashtottari adhipathi found for tithi_index={}".format(tithi_index))


def _ashtottari_dasha_start_date(jd, place, tithi_index=1):
    _, _, _, birth_time_hrs = utils.jd_to_gregorian(jd)

    tit = drik.tithi(
        jd,
        place,
        tithi_index=tithi_index,
    )

    t_frac = utils.get_fraction(
        tit[1],
        tit[2],
        birth_time_hrs,
    )

    lord, res = _ashtottari_adhipathi(tit[0])

    start_jd = drik._get_dhasa_start_jd(
        jd,
        place,
        fraction_elapsed=(1.0 - t_frac),
        total_dasa_years=res,
    )

    return [lord, start_jd]


def _ashtottari_next_adhipati(lord, dirn=1):
    """Returns next lord after lord in the adhipati list."""
    current = ashtottari_adhipathi_list.index(lord)
    next_index = (current + dirn) % len(ashtottari_adhipathi_list)

    return ashtottari_adhipathi_list[next_index]


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, guarding
    against drik._get_dhasa_end_jd()'s known ~365-day-too-large defect for a
    narrow band of small durations. The pre-refactor draft had NO protection
    against this anywhere -- every drik._get_dhasa_end_jd() call in this
    module now routes through this wrapper.
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


def _child_start_and_dir(parent_lord, antardhasa_option=3):
    """
    Determines the starting antardhasa lord and cycling direction for a
    given parent (mahadasa or deeper) lord.

    antardhasa_option semantics (matches every other refactored dhasa
    module's raw-int convention, for backward compatibility -- integers
    1-6 map the same way everywhere in this project):
        1: start at self,          forward
        2: start at self,          backward
        3: start at NEXT lord,     forward   (DEFAULT -- "Ketu's way",
                                               confirmed correct for this
                                               dhasa per project reference
                                               documentation)
        4: start at NEXT lord,     backward
        5: start at PREVIOUS lord, forward
        6: start at PREVIOUS lord, backward
    """
    lord = parent_lord

    if antardhasa_option in [3, 4]:
        lord = _ashtottari_next_adhipati(parent_lord, dirn=1)
    elif antardhasa_option in [5, 6]:
        lord = _ashtottari_next_adhipati(parent_lord, dirn=-1)

    dirn = 1 if antardhasa_option in [1, 3, 5] else -1

    return lord, dirn


def _get_tithi_ashtottari_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    antardhasa_option=3,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Tithi Ashtottari Dasa.

    Signature matches the project-wide pattern:
        (parent_lords, parent_start_jd, parent_duration, place, *,
         antardhasa_option=None, parent_end_jd=None) -> (children, parent_end_jd)

    Rules:
        - Child order via _child_start_and_dir(parent_lord,
          antardhasa_option) -- defaults to option 3 ("Ketu's way": start
          at the NEXT lord, go forward), confirmed correct for this dhasa
          per the project's own PVR reference documentation.
        - PROPORTIONAL-BY-LORD-YEARS split: each child's share of
          parent_duration is that lord's own entry in
          ashtottari_adhipathi_dict, divided by _TOTAL_DHASA_YEARS (108).
          This was ALREADY correctly implemented in the pre-refactor
          draft (across three independent, now-consolidated copies) --
          not a split-rule bug found in this module, unlike several
          other dhasas in this project.
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's SMALLEST child's own computed duration is under
          _SUB_DAY_DURATION_DAYS, ALL of that batch's boundaries (not
          just the last) are computed via proportional-by-lord-years
          interpolation of the parent's own real span, instead of calling
          drik._get_dhasa_end_jd() per child.

    Note: the split ratio always uses the ORIGINAL, constant
    ashtottari_adhipathi_dict/_TOTAL_DHASA_YEARS (108) -- never a
    tribhagi-mutated copy -- since the ratio lord_years/108 is
    mathematically invariant under uniform tribhagi scaling; the caller
    is responsible for supplying an already-correctly-scaled
    parent_duration (see _generate_mahadasa_periods()).

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

    start_lord, dirn = _child_start_and_dir(parent_lord, antardhasa_option)

    child_lords = []
    lord = start_lord

    for _ in range(len(ashtottari_adhipathi_list)):
        child_lords.append(lord)
        lord = _ashtottari_next_adhipati(lord, dirn)

    n = len(child_lords)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = parent_duration * min(
        ashtottari_adhipathi_dict[cl][1] for cl in child_lords
    ) / _TOTAL_DHASA_YEARS
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd
    cumulative_years = 0.0

    for i, clord in enumerate(child_lords):
        child_duration = parent_duration * ashtottari_adhipathi_dict[clord][1] / _TOTAL_DHASA_YEARS

        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_years += ashtottari_adhipathi_dict[clord][1]
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
    tithi_index=1,
    use_tribhagi_variation=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    num_cycles=1,
    stop_at_jd=None,
    max_cycles_safety=50,
):
    """
    THE single Mahadasa seed/root generator for Tithi Ashtottari. This is
    the ONLY place in the module that cycles ashtottari_adhipathi_list
    starting from the birth lord/start_jd. get_dhasa_bhukthi() and
    get_running_dhasa_for_given_date() both call THIS SAME generator.

    Yields already-tribhagi-scaled durations (each maha_dur is the real,
    correctly-scaled Mahadasa length in years) -- the split ratio used by
    _get_tithi_ashtottari_children_jd() is always computed against the
    ORIGINAL, constant ashtottari_adhipathi_dict/_TOTAL_DHASA_YEARS (see
    that function's docstring for why this is safe under tribhagi
    scaling).

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

    dhasa_lord, start_jd = _ashtottari_dasha_start_date(
        jd_at_dob,
        place,
        tithi_index=tithi_index,
    )

    total_lords = len(ashtottari_adhipathi_list)
    effective_cycles = max_cycles_safety if stop_at_jd is not None else num_cycles

    for _cycle in range(effective_cycles):
        for _ in range(total_lords):
            maha_dur = ashtottari_adhipathi_dict[dhasa_lord][1] * tribhagi_factor
            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return

            dhasa_lord = _ashtottari_next_adhipati(dhasa_lord)


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


def ashtottari_mahadasa(jd, place, tithi_index):
    """
    Returns a dictionary of all mahadashas and their start JDs.

    PRESERVED as a public legacy function (in case other code depends on
    this exact signature/OrderedDict shape). Now uses _bounded_end_jd()
    internally (30-day backstop) instead of a raw drik._get_dhasa_end_jd()
    call.

    Returns:
        OrderedDict:
            {mahadhasa_lord_index: start_jd}
    """
    lord, start_date = _ashtottari_dasha_start_date(
        jd,
        place,
        tithi_index,
    )

    retval = Dict()

    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date

        lord_duration = ashtottari_adhipathi_dict[lord][1]

        start_date = _bounded_end_jd(start_date, lord_duration, place)

        lord = _ashtottari_next_adhipati(lord)

    return retval


def ashtottari_bhukthi(dhasa_lord, start_date, place, antardhasa_option=3):
    """
    Compute all bhukthis (AD-level only) of given Mahadasa lord and its
    start date.

    PRESERVED as a public legacy function (in case other code depends on
    this exact signature/OrderedDict shape). Now a thin wrapper around
    the shared _get_tithi_ashtottari_children_jd() engine instead of an
    independent reimplementation of the same proportional-split math.
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]

    children, _ = _get_tithi_ashtottari_children_jd(
        (dhasa_lord,),
        start_date,
        dhasa_lord_duration,
        place,
        antardhasa_option=antardhasa_option,
    )

    retval = Dict()

    for lords_tuple, child_start_jd, _child_duration, _child_end_jd in children:
        retval[lords_tuple[-1]] = child_start_jd

    return retval


def ashtottari_anthara(dhasa_lord, bhukthi_lord, bhukthi_lord_start_date, place):
    """
    Compute all antharas (PD-level only) for given Mahadasa lord, Bhukthi
    lord and Bhukthi start date.

    PRESERVED as a public legacy function (in case other code depends on
    this exact signature/OrderedDict shape). Now a thin wrapper around
    the shared _get_tithi_ashtottari_children_jd() engine instead of an
    independent reimplementation of the same proportional-split math.

    NOTE: this legacy function's own antardhasa cycling always starts at
    the NEXT lord after bhukthi_lord (dirn=+1 implied) -- preserved
    exactly as in the draft (antardhasa_option is not exposed as a
    parameter here, matching the original signature).
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    bhukthi_lord_duration = ashtottari_adhipathi_dict[bhukthi_lord][1]

    bhukthi_years = dhasa_lord_duration * bhukthi_lord_duration / _TOTAL_DHASA_YEARS

    children, _ = _get_tithi_ashtottari_children_jd(
        (dhasa_lord, bhukthi_lord),
        bhukthi_lord_start_date,
        bhukthi_years,
        place,
        antardhasa_option=3,
    )

    retval = Dict()

    for lords_tuple, child_start_jd, _child_duration, _child_end_jd in children:
        retval[lords_tuple[-1]] = child_start_jd

    return retval


def get_dhasa_antardhasa(
    dob, tob,
    place,
    use_tribhagi_variation=False,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    tithi_index=1,
    antardhasa_option=3,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Provides Tithi Ashtottari dhasa-bhukthi for a given Julian day.

    This is Ashtottari Dhasa based on tithi instead of nakshatra.

    Return format:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    (new parameter -- the draft's own __main__ test block already called
    this function with return_exact_bounds=True even though it was never
    defined; that call would have raised TypeError before this fix).

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level, UNLESS a batch of children is
    sub-day, in which case proportional interpolation of the parent's
    real span is used instead (see _SUB_DAY_DURATION_DAYS above).
    """
    global year_duration

    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")
    jd = utils.julian_day_number(dob,tob)
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
            retval.append(
                [
                    lords_tuple,
                    utils.jd_to_gregorian(start_jd_local),
                    float(duration_years),
                ]
            )

    def _recurse(
        level,
        parent_lords_tuple,
        parent_start_jd,
        parent_duration_years,
        parent_end_jd,
    ):
        children, _ = _get_tithi_ashtottari_children_jd(
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
        tithi_index=tithi_index,
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
    jd_at_dob=None,
    place=None,
    antardhasa_option=3,
    use_tribhagi_variation=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Tithi Ashtottari immediate children under the given parent span.

    A thin wrapper around the shared _get_tithi_ashtottari_children_jd()
    engine (previously duplicated the proportional-split logic
    independently from get_dhasa_bhukthi() and ashtottari_bhukthi()/
    ashtottari_anthara() -- now all four call the same engine).

    Returns:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]
    """
    global year_duration

    if jd_at_dob is not None and place is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

    if place is None:
        raise ValueError("place is required for exact Tithi Ashtottari child boundary calculation.")

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

    children, _ = _get_tithi_ashtottari_children_jd(
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
    tithi_index=1,
    antardhasa_option=3,
    use_tribhagi_variation=False,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Tithi Ashtottari runner. Narrows Maha to requested depth.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Instead it drills straight
    down this dhasa's own tree using the SAME single-recursive-rule
    machinery as get_dhasa_bhukthi() and tithi_ashtottari_immediate_
    children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd).
        - Every level below Mahadasa: _get_tithi_ashtottari_children_jd(),
          then _find_child_containing_jd().
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
        tithi_index=tithi_index,
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
        children, _ = _get_tithi_ashtottari_children_jd(
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
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.tithi_ashtottari_tests()
