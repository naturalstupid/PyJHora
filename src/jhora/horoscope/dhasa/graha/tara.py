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
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house


dhasa_adhipathi_dict_sanjay_rath = {
    5: 20,
    1: 10,
    8: 7,
    6: 19,
    4: 16,
    3: 17,
    7: 18,
    2: 7,
    0: 6,
}

dhasa_adhipathi_dict_parasara = {
    5: 20,
    0: 6,
    1: 10,
    2: 7,
    7: 18,
    4: 16,
    6: 19,
    3: 17,
    8: 7,
}

# V5.0: preserved for backward compatibility with any external code that
# might import this constant, but NO LONGER used internally for real
# duration calculations -- see V5.0 changelog above. Both tables actually
# sum to the same 120 (same multiset of values, different key mapping),
# but _TOTAL_DHASA_YEARS is now always computed fresh from whichever
# adhipathi dict is actually in effect, guaranteeing self-consistency.
human_life_span = sum(dhasa_adhipathi_dict_parasara.values())

year_duration = const.sidereal_year

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO protection against this anywhere.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in karana_chathuraaseethi_sama.py, panchottari.py,
# saptharishi_nakshathra.py, sataatbika.py, shastihayani.py,
# shattrimsa_sama.py, shodasottari.py, tithi_ashtottari.py,
# tithi_yogini.py, yoga_vimsottari.py, yogini.py) to become unreliable by
# a real, non-trivial margin. For THIS dhasa (6-20 year Mahadasa spread,
# total 120 years), worst-case duration reaches sub-day starting at SD
# level (~0.274 days worst case). This check is duration-triggered,
# re-evaluated fresh per batch of children, never hardcoded to a
# specific level.
_SUB_DAY_DURATION_DAYS = 1.0


def _get_adhipathi_dict(dhasa_method):
    if dhasa_method == const.TARA_TYPE.SANJAY_RATH:
        return dhasa_adhipathi_dict_sanjay_rath

    return dhasa_adhipathi_dict_parasara


def _next_adhipati(lord, dirn=1, dhasa_method=None):
    """Returns next lord after lord in the adhipati list."""
    if dhasa_method is None: dhasa_method = const.TARA_TYPE_DEFAULT
    dhasa_adhipathi_dict = _get_adhipathi_dict(dhasa_method)

    keys = list(dhasa_adhipathi_dict.keys())
    current = keys.index(lord)
    next_lord = keys[(current + dirn) % len(keys)]

    return next_lord


def _antardhasa(lord, dhasa_method=None):
    if dhasa_method is None: dhasa_method = const.TARA_TYPE_DEFAULT
    dhasa_adhipathi_dict = _get_adhipathi_dict(dhasa_method)

    bhukthis = []

    for _ in range(len(dhasa_adhipathi_dict)):
        bhukthis.append(lord)
        lord = _next_adhipati(
            lord,
            dhasa_method=dhasa_method,
        )

    return bhukthis


def _dhasa_start(
    jd,
    place,
    period,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_method=None,
):
    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

    one_star = 360 / 27.0

    planet_positions = charts.divisional_chart(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )[:const._pp_count_upto_ketu]

    moon = (
        planet_positions[2][1][0] * 30
        + planet_positions[2][1][1]
        + (star_position_from_moon - 1) * one_star
    )

    nak = int(moon / one_star)
    rem = moon - nak * one_star

    fraction_elapsed = rem / one_star

    start_jd = drik._get_dhasa_start_jd(
        jd,
        place,
        fraction_elapsed=fraction_elapsed,
        total_dasa_years=period,
    )

    return start_jd


def _tara_seed_lord_and_duration(
    jd_at_dob,
    place,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_method=None,
):
    """
    Determines the Mahadasa seed lord and its own duration, via the
    kendra (quadrant: 1st/4th/7th/10th from lagna) occupancy + "stronger
    planet" comparison logic. This is a NEW shared function (V5.0) --
    the pre-refactor draft had this logic embedded directly and only
    inside get_dhasa_bhukthi(), not reusable elsewhere (see V5.0
    changelog above). UNCHANGED in actual logic from the draft; only
    extracted into its own function so both get_dhasa_bhukthi() and the
    new _generate_mahadasa_periods() can share it, instead of the draft's
    approach where get_running_dhasa_for_given_date() had to call the
    ENTIRE get_dhasa_bhukthi(..., MAHA_DHASA_ONLY) function just to
    re-derive this same seed.

    Returns:
        (dhasa_lord, dhasa_adhipathi_dict, dhasa_duration) or
        (None, dhasa_adhipathi_dict, None) if no quadrant is occupied
        (mirrors the draft's own "return [] " early-exit behavior, now
        surfaced as a None sentinel for the caller to handle).
    """
    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

    dhasa_adhipathi_dict = _get_adhipathi_dict(dhasa_method)

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
        [
            h_to_p[(h + asc_house) % 12].split("/")
            for h in [0, 3, 6, 9]
            if h_to_p[(h + asc_house) % 12] != ""
        ],
        key=len,
        reverse=True,
    )

    ds = utils.flatten_list(ds)

    if len(ds) == 0:
        return None, dhasa_adhipathi_dict, None

    if "L" in ds:
        ds.remove("L")

    if len(ds) == 0:
        return None, dhasa_adhipathi_dict, None

    if len(ds) >= 2:
        ds1 = ds
        sp = int(ds1[0])

        for p in range(1, len(ds1)):
            sp = house.stronger_planet_from_planet_positions(
                planet_positions,
                int(ds1[p]),
                int(sp),
            )

        dhasa_lord = sp
    else:
        dhasa_lord = int(ds[0])

    dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]

    return dhasa_lord, dhasa_adhipathi_dict, dhasa_duration


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


def _get_tara_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    dhasa_method=None,
    dhasa_adhipathi_dict=None,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Tara Dasa.

    Rules:
        - Child order via _antardhasa(parent_lord, dhasa_method) -- this
          dhasa cycles ONLY forward from the parent lord itself (no
          6-option antardhasa_option support -- see V5.0 changelog
          above; preserved exactly as the draft's own convention).
        - PROPORTIONAL-BY-LORD-YEARS split: each child's share of
          parent_duration is that lord's own entry in the CURRENTLY-
          ACTIVE adhipathi dict (Sanjay Rath or Parasara, per
          dhasa_method), divided by that dict's own total. This was
          ALREADY correctly implemented in the pre-refactor draft (in
          two independent, now-consolidated copies) -- not a split-rule
          bug found in this module.
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's SMALLEST child's own computed duration is under
          _SUB_DAY_DURATION_DAYS, ALL of that batch's boundaries (not
          just the last) are computed via proportional-by-lord-years
          interpolation of the parent's own real span, instead of calling
          drik._get_dhasa_end_jd() per child.

    Returns:
        children: list of
            (child_lords_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

    if dhasa_adhipathi_dict is None:
        dhasa_adhipathi_dict = _get_adhipathi_dict(dhasa_method)

    total_years = float(sum(dhasa_adhipathi_dict.values())) or 1.0

    path = tuple(parent_lords) if isinstance(parent_lords, (list, tuple)) else (parent_lords,)
    parent_lord = path[-1]

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    child_lords = list(
        _antardhasa(
            parent_lord,
            dhasa_method=dhasa_method,
        )
    )

    n = len(child_lords)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = parent_duration * min(
        dhasa_adhipathi_dict[cl] for cl in child_lords
    ) / total_years
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd
    cumulative_years = 0.0

    for i, clord in enumerate(child_lords):
        child_duration = parent_duration * dhasa_adhipathi_dict[clord] / total_years

        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_years += dhasa_adhipathi_dict[clord]
            child_end_jd = parent_start_jd + parent_span * cumulative_years / total_years
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
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_method=None,
    num_cycles=1,
    stop_at_jd=None,
    max_cycles_safety=50,
):
    """
    THE single Mahadasa seed/root generator for Tara. This is the ONLY
    place in the module that determines the seed lord (via
    _tara_seed_lord_and_duration()) and cycles the adhipathi dict
    starting from it. get_dhasa_bhukthi() and get_running_dhasa_for_
    given_date() both call THIS SAME generator.

    Yields nothing (returns immediately) if no quadrant is occupied --
    mirrors the draft's own "return []" early-exit behavior for this
    case.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd)
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
    )

    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

    dhasa_lord, dhasa_adhipathi_dict, dhasa_duration = _tara_seed_lord_and_duration(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_method=dhasa_method,
    )

    if dhasa_lord is None:
        return

    start_jd = _dhasa_start(
        jd_at_dob,
        place,
        dhasa_duration,
        star_position_from_moon=1,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_method=dhasa_method,
    )

    total_lords = len(dhasa_adhipathi_dict)
    effective_cycles = max_cycles_safety if stop_at_jd is not None else num_cycles

    for _cycle in range(effective_cycles):
        for _ in range(total_lords):
            maha_dur = dhasa_adhipathi_dict[dhasa_lord]
            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return

            dhasa_lord = _next_adhipati(dhasa_lord, dhasa_method=dhasa_method)


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
    dhasa_method=None,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Provides Tara dhasa-bhukthi for a given birth date and time.

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

    dhasa_level_index:
        1 = Maha only
        2 = Antara
        3 = Pratyantara
        4 = Sookshma
        5 = Prana
        6 = Deha
    """
    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

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

    dhasa_adhipathi_dict = _get_adhipathi_dict(dhasa_method)

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
        children, _ = _get_tara_children_jd(
            parent_lords_tuple,
            parent_start_jd,
            parent_duration_years,
            place,
            dhasa_method=dhasa_method,
            dhasa_adhipathi_dict=dhasa_adhipathi_dict,
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
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_method=dhasa_method,
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
    dhasa_method=None,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Tara Dhasa immediate children under the given parent span.

    A thin wrapper around the shared _get_tara_children_jd() engine
    (previously duplicated the proportional-split logic independently
    from get_dhasa_bhukthi() -- now both call the same engine).

    Returns:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    Child duration is weighted by the child lord's dhasa years.
    """
    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

    global year_duration

    if jd_at_dob is not None and place is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

    if place is None:
        raise ValueError("place is required for exact Tara child boundary calculation.")

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or a non-empty tuple/list of ints")

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

    children, _ = _get_tara_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        dhasa_method=dhasa_method,
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
    dhasa_method=None,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Tara Dhasa runner. Narrows Maha to requested depth.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Instead it drills straight
    down this dhasa's own tree using the SAME single-recursive-rule
    machinery as get_dhasa_bhukthi() and tara_immediate_children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd) -- also no longer rebuilds the FULL
          Mahadasa cycle table just to find the current one (previous
          draft called the entire get_dhasa_bhukthi(...,
          MAHA_DHASA_ONLY) every time).
        - Every level below Mahadasa: _get_tara_children_jd(), then
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
    if dhasa_method is None:
        dhasa_method = const.TARA_TYPE_DEFAULT

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
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_method=dhasa_method,
        stop_at_jd=current_jd,
    ):
        pass

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
        children, _ = _get_tara_children_jd(
            parent_lords,
            parent_start_jd,
            parent_duration_years,
            place,
            dhasa_method=dhasa_method,
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
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.tara_dhasa_test()
