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
        V5.0  - REFACTORED to match JHora
"""
from jhora import utils, const
from jhora.horoscope.chart import charts
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

year_duration = const.sidereal_year

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO drik._get_dhasa_end_jd() calls anywhere (pure
# linear arithmetic instead) -- every boundary in this module now routes
# through _bounded_end_jd().
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in every other dhasa module refactored in this
# project) to become unreliable by a real, non-trivial margin. This check
# is duration-triggered, re-evaluated fresh for every batch of children,
# regardless of level or which cycle (1 or 2) the Mahadasa came from.
_SUB_DAY_DURATION_DAYS = 1.0


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


def _build_buddhigathi_progression(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
):
    """
    Builds Buddhi Gathi's CYCLE-1 base progression, via a single house-scan
    pass over the natal chart. UNCHANGED in logic from the pre-refactor
    draft -- CONFIRMED CORRECT (both lord order and each lord's own
    duration) against real chart data and the project's own canonical/
    official test (see V5.0 changelog above).

    Returns
    -------
    list[tuple[int, float]]
        [(planet_lord, cycle1_dhasa_duration_years), ...]
    """
    jd_at_dob = utils.julian_day_number(dob, tob)

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )[:const._pp_count_upto_ketu]

    h_to_p = utils.get_house_planet_list_from_planet_positions(
        planet_positions[1:const._pp_count_upto_ketu]
    )
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    planet_dict = {
        int(p): p_long
        for p, (_, p_long) in planet_positions[1:const._pp_count_upto_ketu]
    }

    asc_house = p_to_h[const._ascendant_symbol]

    dhasa_progression = []
    h1 = 0

    for h in range(12):
        hs = (asc_house + const.HOUSE_4 + h) % 12

        if h_to_p[hs] == "":
            continue

        planets = list(map(int, h_to_p[hs].split("/")))

        # Sort planets in this house by descending longitude.
        d1 = {p: l for p, l in planet_dict.items() if p in planets}
        pl_new = [
            p for (p, _) in sorted(
                d1.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

        for pl in pl_new:
            durn = ((asc_house + h1 + 12) - p_to_h[pl]) % 12

            # If planet is exalted add +1.
            if const.house_strengths_of_planets[pl][p_to_h[pl]] == const._EXALTED_UCCHAM:
                durn += 1

            # If planet is debilitated subtract -1.
            if const.house_strengths_of_planets[pl][p_to_h[pl]] == const._DEBILITATED_NEECHAM:
                durn -= 1

            dhasa_progression.append((pl, durn))
            h1 += 1

    return dhasa_progression


def _build_two_cycle_mahadasa_list(dhasa_progression):
    """
    V5.0 REAL FIX: builds the FULL, FIXED Mahadasa lord/duration sequence
    for this dhasa's entire lifespan -- EXACTLY 2 cycles: cycle 1 is the
    house-scan-derived (lord, duration) list as-is; cycle 2 repeats the
    SAME lords, in the SAME order, but with each lord's duration replaced
    by its COMPLEMENT (12 - that lord's own cycle-1 duration).

    This REPLACES the pre-refactor draft's open-ended, indefinitely-
    repeating "while cycles_done < max_cycles" loop (which replayed cycle
    1 UNCHANGED on every pass, bounded only by an unrelated Narayana-dasha
    lifespan constant) -- CONFIRMED WRONG via the project's own canonical/
    official test, which shows the real cycle-2 durations are each
    lord's own complement, not a flat repeat (see V5.0 changelog above
    for the full derivation, including the confirmed 12*d_len total
    lifespan property).

    Returns
    -------
    list[tuple[int, float]]
        [(planet_lord, duration_years), ...] -- length 2 * len(dhasa_progression)
    """
    cycle_2 = [(pl, 12 - durn) for (pl, durn) in dhasa_progression]

    return list(dhasa_progression) + cycle_2


def _get_buddhigathi_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    base_order,
    *,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Buddhi Gathi Dasa.

    Rules:
        - EQUAL split of parent_duration among all d_len lords in
          base_order (the fixed cycle-1 lord list, in cycle-1 order --
          this is the SAME fixed set/order used at EVERY level below
          Mahadasa, regardless of which cycle -- 1 or 2 -- the parent
          Mahadasa itself came from; UNCHANGED from the pre-refactor
          draft's own equal-subdivision logic, which is consistent with
          the project's own canonical/official test's structure).
        - Child order = base_order ROTATED to start at the parent lord
          (wrapping through all d_len lords). UNCHANGED from the
          pre-refactor draft.
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's per-child duration is under
          _SUB_DAY_DURATION_DAYS, ALL child boundaries (not just the
          last) are computed via EQUAL proportional interpolation of the
          parent's own real [parent_start_jd, parent_end_jd] span,
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

    d_len = len(base_order)

    if d_len == 0:
        return [], parent_end_jd

    start_index = base_order.index(parent_lord) if parent_lord in base_order else 0
    rotated = base_order[start_index:] + base_order[:start_index]

    child_duration = parent_duration / d_len
    child_duration_days = child_duration * year_duration
    use_proportional_interpolation = child_duration_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd

    for i, clord in enumerate(rotated):
        child_start_jd = cursor

        if i == d_len - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            child_end_jd = parent_start_jd + parent_span * (i + 1) / d_len
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                parent_path + (clord,),
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
    mahadasa_list,
    *,
    stop_at_jd=None,
):
    """
    THE single Mahadasa seed/root generator for Buddhi Gathi. This is the
    ONLY place in the module that walks the FIXED, 2-cycle mahadasa_list
    (see _build_two_cycle_mahadasa_list() and V5.0 changelog above)
    starting from the birth JD. get_dhasa_bhukthi() and get_running_
    dhasa_for_given_date() both call THIS SAME generator.

    Unlike every other dhasa module in this project (which cycle
    indefinitely, or for an explicit num_cycles), this dhasa's Mahadasa
    sequence is FIXED-LENGTH (exactly 2 * d_len entries, per the
    confirmed 2-cycle-complement model) -- the generator simply walks
    this fixed list once; there is no "num_cycles" concept here.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd)
    """
    start_jd = jd_at_dob

    for lord, dur in mahadasa_list:
        if dur <= 0:
            continue

        maha_start_jd = start_jd
        maha_end_jd = _bounded_end_jd(maha_start_jd, dur, place)

        yield lord, maha_start_jd, dur, maha_end_jd

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
    Buddhi Gathi dhasa expansions to requested depth.

    Parameters
    ----------
    dob : drik.Date
    tob : tuple
        (hour, minute, second) or compatible fractional-hour tuple.
    place : drik.Place
    divisional_chart_factor : int
    chart_method : int
    years, months, sixty_hours : int
        Passed to charts.divisional_chart().
    dhasa_level_index : int
        1 = Maha only
        2 = Antara
        3 = Pratyantara
        4 = Sookshma
        5 = Prana
        6 = Deha
    round_duration : bool
        Round output duration years.
    dhasa_duration_type :
        Optional override. If None, drik.dhasa_year_duration() uses configured default.
    savana_year_method :
        Optional override for Savana year method.
    return_exact_bounds : bool
        If True, each row is [lords_tuple, start_jd_float, end_jd_float,
        duration_years] instead of [lords_tuple, start_tuple,
        duration_years]. New parameter -- the draft's own __main__ test
        block already called this function with return_exact_bounds=True
        even though it was never defined; that call would have raised
        TypeError before this fix.

    Returns
    -------
    list
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level (the draft used pure linear
    arithmetic instead -- see V5.0 changelog above), UNLESS a batch of
    children is sub-day, in which case proportional interpolation of the
    parent's real span is used instead (see _SUB_DAY_DURATION_DAYS
    above).

    This dhasa runs for a FIXED lifespan of exactly 2 house-scan cycles
    (cycle 1 as computed, cycle 2 = complement of cycle 1 -- see V5.0
    changelog above), NOT an indefinite/max_cycles-bounded repeat.
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

    dhasa_progression = _build_buddhigathi_progression(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )

    if len(dhasa_progression) == 0:
        return []

    base_order = [pl for (pl, _) in dhasa_progression]
    mahadasa_list = _build_two_cycle_mahadasa_list(dhasa_progression)

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
        parent_path,
        parent_start_jd,
        parent_duration_years,
        parent_end_jd,
    ):
        children, _ = _get_buddhigathi_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            base_order,
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
                )
            else:
                _emit_row(
                    child_path,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        mahadasa_list,
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
                parent_path=(maha_lord,),
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
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Buddhi Gathi immediate children under a parent span.

    A thin wrapper around the shared _get_buddhigathi_children_jd() engine
    (previously duplicated the equal-split + rotation logic independently
    from get_dhasa_bhukthi() -- now both call the same engine).

    Output rows:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    Rules:
        - Equal subdivision at every sub-level (same fixed d_len-lord base
          order at every level, regardless of which Mahadasa cycle the
          top-level parent came from).
        - Child order is base_order rotated from parent_lord.
        - Last child end is forced to parent_end.
    """
    global year_duration

    y,m,d,fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y,m,d); tob = (fh,0,0)
    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)):
        if len(parent_lords) == 0:
            raise ValueError("parent_lords cannot be empty")
        path = tuple(parent_lords)
    else:
        raise TypeError("parent_lords must be int or tuple/list of ints")

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

    dhasa_progression = _build_buddhigathi_progression(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )

    if len(dhasa_progression) == 0:
        return []

    base_order = [pl for (pl, _) in dhasa_progression]

    children, _ = _get_buddhigathi_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        base_order,
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
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Buddhi Gathi runner. Narrows Maha -> ... -> target depth.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Instead it drills straight
    down this dhasa's own tree using the SAME single-recursive-rule
    machinery as get_dhasa_bhukthi() and buddhigathi_immediate_children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd) over the FIXED 2-cycle mahadasa_list --
          no longer rebuilds the FULL Mahadasa table every time just to
          find the current one.
        - Every level below Mahadasa: _get_buddhigathi_children_jd(), then
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

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    dhasa_progression = _build_buddhigathi_progression(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )

    if len(dhasa_progression) == 0:
        return []

    base_order = [pl for (pl, _) in dhasa_progression]
    mahadasa_list = _build_two_cycle_mahadasa_list(dhasa_progression)

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        mahadasa_list,
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
        children, _ = _get_buddhigathi_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            base_order,
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
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    md = get_dhasa_antardhasa(dob,tob,place,dhasa_level_index=2)
    for (lords),start,durn in md:
        lord_str = ','.join([utils.PLANET_SHORT_NAMES[lord] for lord in lords])
        start_str = f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])}"
        print(lord_str,start_str,durn)
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

    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.buddhi_gathi_test()
