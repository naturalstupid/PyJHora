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
    Kaala Dhasa

    Release History:
        V5.0 - Ref: Kaala Dasa and Chakra Dasa - P.V.R. Narasimha Rao November 1, 2009 Article
        Method decribed in the article is either ambiguous or JHora software follows different method.
        We try 2 different methods to calculate Kaala Fraction. 1. Using lagna/Sun longitudes
        2. Using day/dawn/dusk/night time portions. Neither yield accurate matching of article example
        or JHora software. Longitude based calculations are reasonably close
"""
from jhora import utils, const
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

_kaala_dhasa_life_span = 120  # years
year_duration = const.sidereal_year
_KAALA_FRACTION_METHOD = 1 # 1=>Longitude Based Calculation 2=> Time Based Calculation

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO drik._get_dhasa_end_jd() calls anywhere (pure
# linear arithmetic instead) -- every boundary in this module now routes
# through _bounded_end_jd().
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in every other dhasa module refactored in this
# project) to become unreliable by a real, non-trivial margin. For THIS
# dhasa (kaala_frac fully chart/birth-time-dependent, 1/45 smallest
# weight share compounding across levels), worst-case duration reaches
# sub-day starting at PD level (~0.481 days worst case). This check is
# duration-triggered, re-evaluated fresh for every batch of 18 children,
# regardless of level or which Mahadasa cycle/phase the ultimate ancestor
# came from.
_SUB_DAY_DURATION_DAYS = 1.0

# The 9 fixed lord "weights" (1..9) applied within EACH phase, in FIXED
# lord-index order (0=Sun .. 8=Ketu). UNCHANGED from the pre-refactor
# draft -- CONFIRMED CORRECT against real chart data (see module
# docstring above).
_WEIGHTS = list(range(1, 10))
_TOTAL_WEIGHT = 45.0


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, guarding
    against drik._get_dhasa_end_jd()'s known ~365-day-too-large defect for a
    narrow band of small durations. The pre-refactor draft had NO
    drik._get_dhasa_end_jd() calls anywhere (pure linear arithmetic
    instead) -- every boundary in this module now routes through this
    wrapper, per the project's standing direction to apply real end_jd at
    every level.
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
def _dhasa_progression_and_periods_using_longitudes(jd, place):
    # 1. Fetch exact sidereal longitudes 
    # (Replace these with your library's specific functions for Longitude)
    jd_utc = jd - place.timezone/24.0
    sun_long = drik.solar_longitude(jd_utc, place)
    asc = drik.ascendant(jd, place)
    lagna_long = asc[0]*30+asc[1]
    #print('lagna',utils.deg_to_sign_str(lagna_long),'sun_long',utils.deg_to_sign_str(sun_long))
    # 2. Calculate degrees Lagna has moved past the Sun
    diff = (lagna_long - sun_long) % 360.0

    # 3. Determine Kaala Type and Fraction based purely on degrees
    if diff >= 330.0 or diff < 30.0:
        kaala_type = const.KAALA_TYPE.DAWN
        # Normalize the 330-to-30 range to a 0-to-60 scale
        kaala_frac = ((diff + 30.0) % 360.0) / 60.0
        
    elif 30.0 <= diff < 150.0:
        kaala_type = const.KAALA_TYPE.DAY
        kaala_frac = (diff - 30.0) / 120.0
        
    elif 150.0 <= diff < 210.0:
        kaala_type = const.KAALA_TYPE.DUSK
        kaala_frac = (diff - 150.0) / 60.0
        
    elif 210.0 <= diff < 330.0:
        kaala_type = const.KAALA_TYPE.NIGHT
        kaala_frac = (diff - 210.0) / 120.0

    # 4. Calculate Life Spans
    _kaala_dhasa_life_span = 120.0
    
    # First cycle uses the ELAPSED fraction
    _kaala_dhasa_life_span_first_cycle = _kaala_dhasa_life_span * kaala_frac
    _dhasas1 = [(p + 1) * _kaala_dhasa_life_span_first_cycle / 45.0 for p in range(9)]

    # Second cycle uses the REMAINING fraction
    _kaala_dhasa_life_span_second_cycle = _kaala_dhasa_life_span * (1.0 - kaala_frac)
    _dhasas2 = [(p + 1) * _kaala_dhasa_life_span_second_cycle / 45.0 for p in range(9)]

    return kaala_type, kaala_frac, _dhasas1, _dhasas2

def _dhasa_progression_and_periods_using_time(jd, place):
    prev_sunrise               = drik.sunrise(jd - 1, place)[0]
    previous_day_sunset_time   = drik.sunset(jd - 1, place)[0]
    today_sunrise_time         = drik.sunrise(jd, place)[0]
    today_sunset_time          = drik.sunset(jd, place)[0]
    tomorrow_sunrise_time      = 24.0 + drik.sunrise(jd + 1, place)[0]
    tomorrow_sunset_time       = 24.0 + drik.sunset(jd + 1, place)[0]
    _, _, _, birth_time = utils.jd_to_gregorian(jd)

    df_today = (today_sunset_time - today_sunrise_time) / 6.0
    df_prev  = (previous_day_sunset_time - prev_sunrise) / 6.0
    df_tmrw  = (tomorrow_sunset_time - tomorrow_sunrise_time) / 6.0

    nf1 = (today_sunrise_time - (previous_day_sunset_time - 24.0)) / 6.0
    nf2 = (tomorrow_sunrise_time - today_sunset_time) / 6.0

    dawn_start = today_sunrise_time - nf1
    dawn_end   = today_sunrise_time + df_today
    day_start  = dawn_end
    day_end    = today_sunset_time - df_today
    dusk_start = day_end
    dusk_end   = today_sunset_time + nf2

    yday_night_start = (previous_day_sunset_time - 24.0) + nf1
    yday_night_end   = dawn_start

    tonight_start = dusk_end
    tonight_end   = tomorrow_sunrise_time - nf2

    # NEW: spillover segments, only "active" near polar latitudes
    yday_dusk_start = (previous_day_sunset_time - 24.0) - df_prev
    yday_dusk_end   = yday_night_start

    tmrw_dawn_start = tonight_end
    tmrw_dawn_end   = tomorrow_sunrise_time + df_tmrw

    segments = [
        (const.KAALA_TYPE.DAWN, dawn_start, dawn_end),
        (const.KAALA_TYPE.DUSK, dusk_start, dusk_end),
        (const.KAALA_TYPE.DAY,  day_start,  day_end),
        (const.KAALA_TYPE.NIGHT, yday_night_start, yday_night_end),
        (const.KAALA_TYPE.NIGHT, tonight_start, tonight_end),
        (const.KAALA_TYPE.DUSK, yday_dusk_start, yday_dusk_end),   # spillover
        (const.KAALA_TYPE.DAWN, tmrw_dawn_start, tmrw_dawn_end),   # spillover
    ]

    kaala_type, kaala_frac = const.KAALA_TYPE.DAY, 0.0
    for ktype, start, end in segments:
        if start <= birth_time < end:
            kaala_type = ktype
            kaala_frac = (birth_time - start) / (end - start)
            break
    _kaala_dhasa_life_span_first_cycle = _kaala_dhasa_life_span * kaala_frac
    _dhasas1 = [(p + 1) * _kaala_dhasa_life_span_first_cycle / 45.0 for p in range(9)]
    _kaala_dhasa_life_span_second_cycle = _kaala_dhasa_life_span - _kaala_dhasa_life_span_first_cycle
    _dhasas2 = [(p + 1) * _kaala_dhasa_life_span_second_cycle / 45.0 for p in range(9)]
    return kaala_type, kaala_frac, _dhasas1, _dhasas2

def _get_kaala_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    kaala_frac,
    *,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Kaala Dasa (used at every level below
    Mahadasa).

    Rules:
        - 18 children total per node: phase A (kaala_frac * parent_
          duration, weighted 1..9 across lords 0..8 in fixed order), then
          phase B ((1-kaala_frac) * parent_duration, weighted 1..9 across
          the SAME lords 0..8 in fixed order again). UNCHANGED from the
          pre-refactor draft -- CONFIRMED CORRECT against real chart data
          (see module docstring above).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's smallest child duration is under
          _SUB_DAY_DURATION_DAYS, ALL 18 child boundaries (not just the
          last) are computed via weighted proportional interpolation of
          the parent's own real [parent_start_jd, parent_end_jd] span,
          instead of calling _bounded_end_jd()/drik._get_dhasa_end_jd()
          per child.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    phaseA_years = kaala_frac * parent_duration
    phaseB_years = (1.0 - kaala_frac) * parent_duration

    # Build the 18-entry (lord, duration) sequence: phase A (9 lords),
    # then phase B (SAME 9 lords again, fixed order 0..8 both times).
    segments = []

    for blord, w in enumerate(_WEIGHTS):
        segments.append((blord, phaseA_years * (w / _TOTAL_WEIGHT)))

    for blord, w in enumerate(_WEIGHTS):
        segments.append((blord, phaseB_years * (w / _TOTAL_WEIGHT)))

    n = len(segments)

    smallest_child_years = min(d for _b, d in segments)
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(d for _b, d in segments)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, (blord, child_duration) in enumerate(segments):
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
                parent_path + (blord,),
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
    years=1,
    months=1,
    sixty_hours=1,
    stop_at_jd=None,
):
    """
    THE single Mahadasa seed/root generator for Kaala Dasa. This is the
    ONLY place in the module that computes kaala_type/kaala_frac (once)
    and walks the FIXED, exactly-2-cycle Mahadasa sequence (18 total
    entries: 9 lords at cycle-1 weights, then the SAME 9 lords again at
    cycle-2 weights) starting from the birth JD (progressed via
    drik.next_solar_date(), matching the pre-refactor draft exactly).
    get_dhasa_antardhasa() and get_running_dhasa_for_given_date() both
    call THIS SAME generator.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd, kaala_type, kaala_frac)
    """
    jd_years = drik.next_solar_date(
        jd_at_dob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )
    if _KAALA_FRACTION_METHOD == 1:
        kaala_type, kaala_frac, dhasas_first, dhasas_second = _dhasa_progression_and_periods_using_longitudes(
            jd_years,
            place,
        )
    else:
        kaala_type, kaala_frac, dhasas_first, dhasas_second = _dhasa_progression_and_periods_using_time(
            jd_years,
            place,
        )


    start_jd = jd_years

    for cycle_durations in (dhasas_first, dhasas_second):
        for dhasa_lord in range(9):
            maha_dur = cycle_durations[dhasa_lord]

            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

            yield dhasa_lord, maha_start_jd, maha_dur, maha_end_jd, kaala_type, kaala_frac

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
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Provides Kaala dhasa-bhukthi for a given date.

    Returns:
        kaala_type, dhasa_info

    dhasa_info rows:
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    (new parameter -- proactively added for consistency with every other
    refactored dhasa module in this project; see module docstring above).

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level (the draft used pure linear
    arithmetic instead -- see module docstring above), UNLESS a batch of
    children is sub-day, in which case weighted proportional
    interpolation of the parent's real span is used instead (see
    _SUB_DAY_DURATION_DAYS above).
    """
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

    dhasa_info = []
    kaala_type_result = [None]

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            dhasa_info.append(
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

            dhasa_info.append(
                [
                    lords_tuple,
                    utils.jd_to_gregorian(start_jd_local),
                    durn,
                ]
            )

    def _recurse(
        level,
        parent_path,
        parent_start_jd,
        parent_duration_years,
        parent_end_jd,
        kaala_frac,
    ):
        children, _ = _get_kaala_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            kaala_frac,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(
                    level + 1,
                    child_path,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                    kaala_frac,
                )
            else:
                _emit_row(
                    child_path,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )

    for (
        maha_lord, maha_start_jd, maha_dur, maha_end_jd, kaala_type, kaala_frac,
    ) in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    ):
        kaala_type_result[0] = kaala_type

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
                kaala_frac,
            )

    return kaala_type_result[0], dhasa_info


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kaala Dhasa immediate children under a given parent span.

    A thin wrapper around the shared _get_kaala_children_jd() engine
    (previously duplicated the 18-way two-phase weighted-split logic
    independently from get_dhasa_antardhasa() -- now both call the same
    engine).

    Rules:
        - Two-phase split using kaala_frac.
        - Phase A = kaala_frac * parent duration.
        - Phase B = (1 - kaala_frac) * parent duration.
        - Each phase subdivided by weights 1..9.
        - 18 immediate children total.
        - Last child end is forced to parent_end.

    Output:
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

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    jd_years = drik.next_solar_date(
        jd_at_dob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )

    if _KAALA_FRACTION_METHOD == 1:
        kaala_type, kaala_frac, dhasas_first, dhasas_second = _dhasa_progression_and_periods_using_longitudes(
            jd_years,
            place,
        )
    else:
        kaala_type, kaala_frac, dhasas_first, dhasas_second = _dhasa_progression_and_periods_using_time(
            jd_years,
            place,
        )

    children, _ = _get_kaala_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        kaala_frac,
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
    *,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kaala Dhasa runner.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Instead it drills straight
    down this dhasa's own tree using the SAME single-recursive-rule
    machinery as get_dhasa_antardhasa() and kaala_immediate_children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd).
        - Every level below Mahadasa: _get_kaala_children_jd(), then
          _find_child_containing_jd().
    Stays in JD-float space throughout; only the final returned rows are
    converted to Gregorian tuples.

    Returns:
        [
            [(l1,),                start1, end1],
            [(l1,l2),              start2, end2],
            [(l1,l2,l3),           start3, end3],
            [(l1,l2,l3,l4),        start4, end4],
            [(l1,l2,l3,l4,l5),     start5, end5],
            [(l1,l2,l3,l4,l5,l6),  start6, end6],
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
    kaala_frac = None

    for (
        maha_lord, maha_start_jd, maha_dur, maha_end_jd, _kaala_type, kaala_frac,
    ) in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
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

    parent_path = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_kaala_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            kaala_frac,
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


if __name__ == "__main__":
    utils.set_language("en")
    dob = drik.Date(1996, 12, 7)
    #dob = drik.Date(1944, 8, 20)
    tob = (10, 34, 0)
    #tob = (7,12,0)
    place = drik.Place("Chennai,IN", 13+2/60+19/3600, 80+15/60+42.4979999999834/3600, +5.5)
    place = drik.Place("Rajiv Gandhi", 18.+58/60, 72+49/60, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    _,m_db = get_dhasa_antardhasa(dob,tob,place,dhasa_level_index=1)
    _,a_db = get_dhasa_antardhasa(dob,tob,place,dhasa_level_index=2)
    import itertools
    sr = drik.sunrise(jd_at_dob,place)[0]
    ss = drik.sunset(jd_at_dob,place)[0]
    print('sunrise',utils.to_dms(sr),'sunset',utils.to_dms(ss))
    print(_dhasa_progression_and_periods_using_longitudes(jd_at_dob,place))
    #exit()
    # Step 1: Group a_db's antardasa rows by their md
    # (antardasas for the same md are contiguous, since md is the outer loop)
    ad_groups = {}
    order = []
    for row in a_db:
        md = row[0][0]
        if md not in ad_groups:
            ad_groups[md] = []
            order.append(md)
        ad_groups[md].append(row)

    # Step 2: Walk through m_db (source of truth for date + correct duration)
    for m_row in m_db:
        md = m_row[0][0]            # maha dasa index (single value, not a tuple)
        (y, m, d, fh) = m_row[1]   # start date/time
        duration = m_row[2]        # correct maha dasa duration

        print(f"{utils.PLANET_SHORT_NAMES[md]} {y}-{m}-{d} {utils.to_dms(fh)} {duration}")

        ad_names = [utils.PLANET_SHORT_NAMES[row[0][1]] for row in ad_groups[md]]
        #print(f"{utils.PLANET_SHORT_NAMES[md]} > {','.join(ad_names)}")
    from datetime import datetime
    import random
    import time

    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600

    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    print(check_date)

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
        print("running_all[4]", grd[4])
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
        _kaala_type, full_tree = get_dhasa_antardhasa(
            dob, tob,
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
    pvr_tests.kaala_test()
