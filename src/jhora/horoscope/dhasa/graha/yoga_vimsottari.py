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
        V5.0   - REFACTORED to match JHora.
"""
from collections import OrderedDict as Dict

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts


year_duration = const.sidereal_year

vimsottari_dict = {
    8: [(3, 12, 21), 7],
    5: [(4, 13, 22), 20],
    0: [(5, 14, 23), 6],
    1: [(6, 15, 24), 10],
    2: [(7, 16, 25), 7],
    7: [(8, 17, 26), 18],
    4: [(9, 18, 27), 16],
    6: [(1, 10, 19), 19],
    3: [(2, 11, 20), 17],
}

human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa

# V5.0: computed directly from vimsottari_dict's own entries (120), rather
# than solely trusting const.human_life_span_for_vimsottari_dhasa to
# necessarily agree -- confirmed they do agree, but self-consistency with
# the actual table used for the split ratio is more robust.
_TOTAL_DHASA_YEARS = sum(v[1] for v in vimsottari_dict.values())  # 120

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO protection against this anywhere.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in karana_chathuraaseethi_sama.py, panchottari.py,
# saptharishi_nakshathra.py, sataatbika.py, shastihayani.py,
# shattrimsa_sama.py, shodasottari.py, tithi_ashtottari.py,
# tithi_yogini.py) to become unreliable by a real, non-trivial margin.
# For THIS dhasa (6-20 year Mahadasa spread, identical to standard
# Vimsottari's own spread), worst-case duration reaches sub-day starting
# at SD level (~0.274 days worst case). This check is duration-triggered,
# re-evaluated fresh per batch of children, never hardcoded to a specific
# level.
_SUB_DAY_DURATION_DAYS = 1.0


def _extract_years(val):
    """Allow both numeric or [yoga_list, years]/(yoga_list, years)."""
    if isinstance(val, (list, tuple)) and len(val) >= 2 and isinstance(val[1], (int, float)):
        return float(val[1])

    return float(val)


def vimsottari_adhipathi(yoga_index):
    for key, value in vimsottari_dict.items():
        yoga_list, durn = value

        if yoga_index in yoga_list:
            return key, durn

    raise ValueError("No Yoga Vimshottari adhipathi found for yoga_index={}".format(yoga_index))


def vimsottari_next_adhipati(lord, direction=None):
    """Returns next lord after lord in the Vimsottari adhipati list.

    direction defaults to +1 (forward/zodiacal) when not explicitly
    overridden by the caller -- matches every other dhasa module's
    count_direction convention (this module has no separate
    count_direction constant since const.vimsottari_adhipati_list's own
    cyclic order already encodes the standard Vimsottari lord sequence).
    """
    if direction is None:
        direction = 1

    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + direction) % len(const.vimsottari_adhipati_list)

    return const.vimsottari_adhipati_list[next_index]


def vimsottari_dasha_start_date(jd, place):
    """Returns the start JD of the Mahadasha occurring on or before jd."""
    _, _, _, birth_time_hrs = utils.jd_to_gregorian(jd)

    yoga_info = drik.yogam(jd, place)
    y_frac = utils.get_fraction(
        yoga_info[1],
        yoga_info[2],
        birth_time_hrs,
    )
    lord, res = vimsottari_adhipathi(yoga_info[0])

    start_jd = drik._get_dhasa_start_jd(
        jd,
        place,
        fraction_elapsed=(1.0 - y_frac),
        total_dasa_years=res,
    )

    return [lord, start_jd]


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


def _child_start_and_dir(parent_lord, antardhasa_option=1):
    """
    Determines the starting antardhasa lord and cycling direction for a
    given parent (mahadasa or deeper) lord.

    antardhasa_option semantics (matches every other refactored dhasa
    module's raw-int convention):
        1: start at self,          forward   (DEFAULT -- "Jupiter's way",
                                               matches standard Vimsottari)
        2: start at self,          backward
        3: start at NEXT lord,     forward
        4: start at NEXT lord,     backward
        5: start at PREVIOUS lord, forward
        6: start at PREVIOUS lord, backward
    """
    lord = parent_lord

    if antardhasa_option in [3, 4]:
        lord = vimsottari_next_adhipati(parent_lord, direction=1)
    elif antardhasa_option in [5, 6]:
        lord = vimsottari_next_adhipati(parent_lord, direction=-1)

    dirn = 1 if antardhasa_option in [1, 3, 5] else -1

    return lord, dirn


def _get_yoga_vimsottari_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    antardhasa_option=1,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Yoga Vimsottari Dasa.

    Signature matches the project-wide pattern:
        (parent_lords, parent_start_jd, parent_duration, place, *,
         antardhasa_option=None, parent_end_jd=None) -> (children, parent_end_jd)

    Rules:
        - Child order via _child_start_and_dir(parent_lord,
          antardhasa_option) -- defaults to option 1 ("Jupiter's way":
          start at self, go forward), matching standard Vimsottari's own
          convention and the draft's own explicit default.
        - PROPORTIONAL-BY-LORD-YEARS split: each child's share of
          parent_duration is that lord's own entry in vimsottari_dict,
          divided by _TOTAL_DHASA_YEARS (120). This was ALREADY correctly
          implemented in the pre-refactor draft (across three
          independent, now-consolidated copies) -- not a split-rule bug
          found in this module.
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
    vimsottari_dict/_TOTAL_DHASA_YEARS -- never a tribhagi-mutated copy --
    since the ratio lord_years/120 is mathematically invariant under
    uniform tribhagi scaling; the caller is responsible for supplying an
    already-correctly-scaled parent_duration (see
    _generate_mahadasa_periods()).

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

    for _ in range(len(const.vimsottari_adhipati_list)):
        child_lords.append(lord)
        lord = vimsottari_next_adhipati(lord, dirn)

    n = len(child_lords)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = parent_duration * min(
        _extract_years(vimsottari_dict[cl]) for cl in child_lords
    ) / _TOTAL_DHASA_YEARS
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd
    cumulative_years = 0.0

    for i, clord in enumerate(child_lords):
        clord_years = _extract_years(vimsottari_dict[clord])
        child_duration = parent_duration * clord_years / _TOTAL_DHASA_YEARS

        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_years += clord_years
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
    use_tribhagi_variation=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    num_cycles=1,
    stop_at_jd=None,
    max_cycles_safety=50,
):
    """
    THE single Mahadasa seed/root generator for Yoga Vimsottari. This is
    the ONLY place in the module that cycles const.vimsottari_adhipati_
    list starting from the birth lord/start_jd. get_dhasa_bhukthi() and
    get_running_dhasa_for_given_date() both call THIS SAME generator.

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

    dhasa_lord, start_jd = vimsottari_dasha_start_date(jd_at_dob, place)

    total_lords = len(const.vimsottari_adhipati_list)
    effective_cycles = max_cycles_safety if stop_at_jd is not None else num_cycles

    for _cycle in range(effective_cycles):
        for _ in range(total_lords):
            maha_dur = _extract_years(vimsottari_dict[dhasa_lord]) * tribhagi_factor
            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return

            dhasa_lord = vimsottari_next_adhipati(dhasa_lord)


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


def vimsottari_mahadasa(jdut1, place):
    """
    List all Mahadashas and their start JDs.

    PRESERVED as a public legacy function (in case other code depends on
    this exact signature/OrderedDict shape). Now uses _bounded_end_jd()
    internally (30-day backstop) instead of a raw drik._get_dhasa_end_jd()
    call.

    Returns:
        OrderedDict: {mahadhasa_lord_index: start_jd}
    """
    lord, start_date = vimsottari_dasha_start_date(jdut1, place)

    retval = Dict()

    for _ in range(len(const.vimsottari_adhipati_list)):
        retval[lord] = start_date

        lord_duration = _extract_years(vimsottari_dict[lord])

        start_date = _bounded_end_jd(start_date, lord_duration, place)

        lord = vimsottari_next_adhipati(lord)

    return retval


def _vimsottari_bhukti(maha_lord, start_date, place, antardhasa_option=1):
    """
    Compute all Bhuktis (AD-level only) of a given Mahadasha lord and its
    start date.

    PRESERVED as a public legacy function (in case other code depends on
    this exact signature/OrderedDict shape). Now a thin wrapper around
    the shared _get_yoga_vimsottari_children_jd() engine instead of an
    independent reimplementation of the same proportional-split math.
    """
    dhasa_lord_duration = _extract_years(vimsottari_dict[maha_lord])

    children, _ = _get_yoga_vimsottari_children_jd(
        (maha_lord,),
        start_date,
        dhasa_lord_duration,
        place,
        antardhasa_option=antardhasa_option,
    )

    retval = Dict()

    for lords_tuple, child_start_jd, _child_duration, _child_end_jd in children:
        retval[lords_tuple[-1]] = child_start_jd

    return retval


def _vimsottari_antara(maha_lord, bhukti_lord, start_date, place):
    """
    Compute all Antaradasas (PD-level only) from a given Bhukti start
    date.

    PRESERVED as a public legacy function (in case other code depends on
    this exact signature/OrderedDict shape). Now a thin wrapper around
    the shared _get_yoga_vimsottari_children_jd() engine instead of an
    independent reimplementation of the same proportional-split math.

    NOTE: this legacy function's own antardhasa cycling always starts at
    the SAME lord (bhukti_lord itself, forward) -- preserved exactly as
    in the draft (antardhasa_option is not exposed as a parameter here,
    matching the original signature).
    """
    maha_lord_duration = _extract_years(vimsottari_dict[maha_lord])
    bhukti_lord_duration = _extract_years(vimsottari_dict[bhukti_lord])

    bhukti_years = maha_lord_duration * bhukti_lord_duration / _TOTAL_DHASA_YEARS

    children, _ = _get_yoga_vimsottari_children_jd(
        (maha_lord, bhukti_lord),
        start_date,
        bhukti_years,
        place,
        antardhasa_option=1,
    )

    retval = Dict()

    for lords_tuple, child_start_jd, _child_duration, _child_end_jd in children:
        retval[lords_tuple[-1]] = child_start_jd

    return retval


def _where_occurs(jd, some_dict):
    """Returns last key such that some_dict[key] < jd."""
    for key in reversed(list(some_dict.keys())):
        if some_dict[key] < jd:
            return key

    return next(iter(some_dict.keys()))


def compute_vimsottari_antara_from(jd, mahadashas, place):
    """
    Returns Antaradasha within which given jd falls.

    PRESERVED as a public legacy function, UNCHANGED in logic (still
    calls the now-refactored _vimsottari_bhukti()/_vimsottari_antara()
    legacy wrappers, which themselves now route through the shared
    engine).
    """
    i = _where_occurs(jd, mahadashas)

    bhuktis = _vimsottari_bhukti(
        i,
        mahadashas[i],
        place,
    )

    j = _where_occurs(jd, bhuktis)

    antara = _vimsottari_antara(
        i,
        j,
        bhuktis[j],
        place,
    )

    return i, j, antara


def get_dhasa_antardhasa(
    dob, tob,
    place,
    use_tribhagi_variation=False,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Yoga-based Vimshottari dasha.

    This is Vimshottari keyed by Yogam instead of Nakshatra.

    Return format:
        vim_bal, [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    If return_exact_bounds=True, each row in the second tuple element is
    instead:
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
    jd = utils.julian_day_number(dob,tob)
    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    dhasa_cycles = 3 if use_tribhagi_variation else 1

    # --- vim_bal: preserved exactly as in the draft, computed from the
    # first two Mahadasas' start dates (via the shared generator) rather
    # than a separately-mutated vimsottari_mahadasa() call.
    md_preview = []
    for maha_lord, maha_start_jd, _maha_dur, _maha_end_jd in _generate_mahadasa_periods(
        jd,
        place,
        use_tribhagi_variation=use_tribhagi_variation,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        num_cycles=1,
    ):
        md_preview.append(maha_start_jd)
        if len(md_preview) >= 2:
            break

    de = md_preview[1] if len(md_preview) >= 2 else md_preview[0]

    y, m, d, _ = utils.jd_to_gregorian(jd)
    p_date1 = drik.Date(y, m, d)

    y, m, d, _ = utils.jd_to_gregorian(de)
    p_date2 = drik.Date(y, m, d)

    vim_bal = utils.panchanga_date_diff(p_date1, p_date2)

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
        children, _ = _get_yoga_vimsottari_children_jd(
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

    return vim_bal, retval


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob=None,
    place=None,
    antardhasa_option=1,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Yoga Vimshottari immediate children under the given parent span.

    A thin wrapper around the shared _get_yoga_vimsottari_children_jd()
    engine (previously duplicated the proportional-split logic
    independently from get_dhasa_bhukthi() and _vimsottari_bhukti()/
    _vimsottari_antara() -- now all four call the same engine).

    NOTE: use_rasi_bhukthi_variation, divisional_chart_factor, and
    chart_method are accepted for interface compatibility (matching the
    draft's own signature) but are NOT currently used anywhere in this
    function's body -- this was already true in the pre-refactor draft
    (a pre-existing no-op parameter, not something this refactor removed
    or newly broke). See V5.0 changelog above.

    Returns:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    This function intentionally returns start and end tuples because
    the running-dhasa navigator needs parent-child boundaries.
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
        raise ValueError("place is required for exact Yoga Vimshottari child boundary calculation.")

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

    children, _ = _get_yoga_vimsottari_children_jd(
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
    antardhasa_option=1,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Yoga Vimshottari runner. Narrows Maha to requested depth.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Instead it drills straight
    down this dhasa's own tree using the SAME single-recursive-rule
    machinery as get_dhasa_bhukthi() and yoga_vimsottari_immediate_
    children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd).
        - Every level below Mahadasa: _get_yoga_vimsottari_children_jd(),
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
        children, _ = _get_yoga_vimsottari_children_jd(
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
    _,_md = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    print("=== Mahadasas ===")
    for row in _md:
        lords, (y, m, d, fh), dur = row
        print(f"{utils.PLANET_SHORT_NAMES[lords[0]] if lords[0] != 'L' else 'Asc'} "
              f"{y}-{m:02d}-{d:02d} {utils.to_dms(fh)}  dur={dur:.4f}")

    # ---- Print Antardasas for the first 4 Mahadasas ----
    _,_ad = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
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
        _,full_tree = get_dhasa_antardhasa(
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
    pvr_tests.yoga_vimsottari_tests()
