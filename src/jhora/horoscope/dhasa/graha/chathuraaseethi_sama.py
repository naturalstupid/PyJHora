#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora
#
# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
Calculates Chathuraaseethi Sama (=84) Dasha-bhukthi-antara-sukshma-prana
"""
"""
Release History:
    V4.8.9 - minor argument call fixes.
    V4.9.0 - dhasa start date calculation now uses drik._get_dhasa_star_jd()
             to calculate dhasa start date using how much Sun has tranversed.
    V5.0   - REFACTOR (matches JHora results)
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts


year_duration = const.sidereal_year

"""Applicability: The 10th lord in 10th."""

# seed_star = 15  # Swaathi
seed_lord = 0

# Duration 12 years each; total 84 years.
dhasa_adhipathi_list = {k: 12 for k in const.SUN_TO_SATURN}

# count_direction:
#   1  -> base star to birth star zodiac
#  -1  -> base star to birth star anti-zodiac
count_direction = 1

# Total lifespan (years) for this dhasa system: 7 lords * 12 years = 84.
human_life_span_for_chathuraaseethi_sama_dhasa = sum(dhasa_adhipathi_list.values())

# Defensive backstop threshold (days). Mirrors vimsottari.py's
# _END_JD_SANITY_SLACK_DAYS / ashtottari.py's same constant. If
# drik._get_dhasa_end_jd() is ever called fresh (no known parent_end_jd)
# with a small duration and the returned span differs from the naive
# proportional estimate by more than this many days, we distrust the
# primitive's result and fall back to the proportional estimate instead of
# propagating a corrupted boundary.
_END_JD_SANITY_SLACK_DAYS = 30.0


def applicability_check(planet_positions):
    """10th Lord in 10th House."""
    from jhora.horoscope.chart import house

    asc_house = planet_positions[0][1][0]
    tenth_house = (asc_house + 9) % 12
    tenth_lord = house.house_owner_from_planet_positions(planet_positions, tenth_house)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    return p_to_h[tenth_lord] == tenth_house


def _next_adhipati(lord, dirn=1):
    """Returns next lord after lord in the adhipati list."""
    keys = list(dhasa_adhipathi_list.keys())
    current = keys.index(lord)
    next_lord = keys[(current + dirn) % len(keys)]
    return next_lord


def _get_dhasa_dict(seed_star=15):
    dhasa_dict = {k: [] for k in dhasa_adhipathi_list.keys()}

    nak = seed_star - 1
    lord = seed_lord
    lord_index = list(dhasa_adhipathi_list.keys()).index(lord)

    for _ in range(27):
        dhasa_dict[lord].append(nak + 1)
        nak = (nak + 1 * count_direction) % 27
        lord_index = (lord_index + 1) % len(dhasa_adhipathi_list)
        lord = list(dhasa_adhipathi_list.keys())[lord_index]

    return dhasa_dict


def _maha_dhasa(nak, seed_star=15):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)

    return [
        (_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord])
        for _dhasa_lord, _star_list in dhasa_adhipathi_dict.items()
        if nak in _star_list
    ][0]


def _antardhasa(lord, antardhasa_option=None):
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
    if antardhasa_option in [const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
                             const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_BACKWARD]:
        lord = _next_adhipati(lord, dirn=1)
    elif antardhasa_option in [const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD,
                               const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_BACKWARD]:
        lord = _next_adhipati(lord, dirn=-1)

    dirn = (1 if antardhasa_option in [const.ANTARDHASA_OPTION.START_FROM_DHASA_LORD_GO_FORWARD,
                                       const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
                                       const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD] 
                        else -1)
    bhukthis = []

    for _ in range(len(dhasa_adhipathi_list)):
        bhukthis.append(lord)
        lord = _next_adhipati(lord, dirn)

    return bhukthis


def _dhasa_start(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    seed_star=15,
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


### --- SINGLE CHILD-GENERATION ENGINE ---------------------------------------
def _get_chathuraaseethi_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    antardhasa_option=None,
    parent_end_jd=None,
):
    """
    THE authoritative Chathuraaseethi Sama child-generation engine (JD-based).

    Every level (MD->AD, AD->PD, PD->SD, SD->PrD, PrD->DD) is generated by
    this ONE function, called recursively. There is no other place in this
    module (post-refactor) that computes a child dhasa boundary.

    Note (specific to this dhasa): children are split EQUALLY among the 7
    lords (parent_duration / 7 each), per the original _antardhasa()/
    _recurse() logic -- unlike Vimsottari/Ashtottari, which split
    proportionally by each child lord's own individual years. This equal
    split is preserved exactly (not generalized away), since it reflects
    this dhasa's genuinely different rule.

    parent_duration MUST be the clean cascaded symbolic duration
    (parent_of_parent_duration / 7), NEVER a value back-derived from an
    already-materialized calendar span.

    parent_end_jd : float, optional
        If the CALLER already knows this parent's exact end JD (true for
        every level below the first), pass it here. It is then used AS-IS
        and drik._get_dhasa_end_jd is never called for it -- avoiding
        re-derivation of an already-known boundary (the pattern confirmed
        necessary in vimsottari.py to sidestep a drik._get_dhasa_end_jd
        defect for very small durations).

    Returns
    -------
    (children, parent_end_jd)
        children: list of (child_lords_tuple, child_start_jd, child_end_jd,
                            child_duration_years) -- all raw JD/float.
        parent_end_jd: float, the parent's end (either the value passed in,
                       or freshly computed -- see sanity guard below).
    """
    global year_duration
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
    parent_lord = parent_lords[-1]

    if parent_end_jd is None:
        # Only reached when the caller does NOT already know this boundary.
        # Safe for Maha-scale (12-year) durations; guarded here in case this
        # is ever invoked with a small duration from some other caller.
        candidate_end_jd = drik._get_dhasa_end_jd(
            start_jd=parent_start_jd,
            place=place,
            total_dasa_years=float(parent_duration),
        )
        expected_span_days = float(parent_duration) * year_duration
        actual_span_days = candidate_end_jd - parent_start_jd
        if abs(actual_span_days - expected_span_days) > _END_JD_SANITY_SLACK_DAYS:
            parent_end_jd = parent_start_jd + expected_span_days
        else:
            parent_end_jd = candidate_end_jd

    child_lords = _antardhasa(parent_lord, antardhasa_option)
    if not child_lords:
        return [], parent_end_jd

    n_children = len(child_lords)
    child_duration = float(parent_duration) / n_children
    span = parent_end_jd - parent_start_jd
    min_child_days = child_duration * year_duration

    children = []

    if min_child_days >= 1.0:
        # Large enough: real per-child solar-arc crossing (chained). The
        # very last child is always clamped to parent_end_jd for exact
        # closure.
        #
        # MONOTONE GUARD: if a crossing is backward or overshoots the
        # parent end, fall back to a proportional split of the REMAINING
        # span for that child only (guaranteed forward, non-overshooting).
        jd_cursor = parent_start_jd
        remaining_children = n_children
        for idx, clord in enumerate(child_lords):
            if idx == n_children - 1:
                child_end_jd = parent_end_jd
            else:
                child_end_jd = drik._get_dhasa_end_jd(
                    start_jd=jd_cursor, place=place, total_dasa_years=child_duration,
                )
                if not (jd_cursor < child_end_jd < parent_end_jd):
                    frac = 1.0 / remaining_children if remaining_children > 0 else 0.0
                    child_end_jd = jd_cursor + (parent_end_jd - jd_cursor) * frac
            children.append((parent_lords + (clord,), jd_cursor, child_end_jd, child_duration))
            jd_cursor = child_end_jd
            remaining_children -= 1
    else:
        # Sub-day (or otherwise below the safe per-child arc threshold):
        # equal proportional division within the ALREADY-KNOWN parent span.
        # Never calls drik._get_dhasa_end_jd per child, so it can never hit
        # the confirmed small-duration bug regardless of how small the
        # children are.
        for idx, clord in enumerate(child_lords):
            cstart = parent_start_jd + span * (idx / n_children)
            cend = parent_end_jd if idx == n_children - 1 else parent_start_jd + span * ((idx + 1) / n_children)
            children.append((parent_lords + (clord,), cstart, cend, child_duration))

    if children:
        last = children[-1]
        children[-1] = (last[0], last[1], parent_end_jd, last[3])

    return children, parent_end_jd


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    antardhasa_option=None,
    place=None,
    **kwargs,
):
    """
    Public one-level child API (tuple-date in / tuple-date out wrapper
    around the single _get_chathuraaseethi_children_jd() engine).

    Output:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    If `parent_end` is supplied, it is passed straight through to
    _get_chathuraaseethi_children_jd() as `parent_end_jd` -- used AS-IS,
    never re-derived via drik._get_dhasa_end_jd. `parent_duration`
    (back-derived from the given span in that case) is still used to
    compute the children's equal-split SHAPE.
    """
    global year_duration
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
    if place is None:
        raise ValueError("place is required for exact child boundary calculation.")

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)):
        if len(parent_lords) == 0:
            raise ValueError("parent_lords cannot be empty")
        path = tuple(parent_lords)
    else:
        raise TypeError("parent_lords must be int or tuple/list of ints")

    start_jd = utils._tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end.")

    known_end_jd = None
    if parent_end is None:
        clean_duration = float(parent_duration)
    else:
        known_end_jd = utils._tuple_to_jd(parent_end)
        if known_end_jd <= start_jd:
            return []
        clean_duration = (known_end_jd - start_jd) / year_duration

    children, _parent_end_jd = _get_chathuraaseethi_children_jd(
        parent_lords=path,
        parent_start_jd=start_jd,
        parent_duration=clean_duration,
        place=place,
        antardhasa_option=antardhasa_option,
        parent_end_jd=known_end_jd,
    )

    return [
        [lords, utils.jd_to_gregorian(start_jd_c), utils.jd_to_gregorian(end_jd_c)]
        for (lords, start_jd_c, end_jd_c, _dur) in children
    ]


def _expand_all_levels(
    parent_lords,
    parent_start_jd,
    parent_end_jd,
    parent_duration,
    target_depth,
    place,
    *,
    antardhasa_option,
    emit_row,
):
    """
    Recursively walk down from `parent_lords` to `target_depth`, emitting
    only the LEAF rows at target_depth.

    `parent_end_jd` (already known from the level above) is passed straight
    into _get_chathuraaseethi_children_jd() so it is reused, never
    recomputed via drik._get_dhasa_end_jd.

    emit_row signature: emit_row(lords_tuple, start_jd, end_jd, duration_years)
    """
    depth = len(parent_lords)

    if depth == target_depth:
        emit_row(parent_lords, parent_start_jd, parent_end_jd, parent_duration)
        return

    children, _parent_end_jd_confirmed = _get_chathuraaseethi_children_jd(
        parent_lords=parent_lords,
        parent_start_jd=parent_start_jd,
        parent_duration=parent_duration,
        place=place,
        antardhasa_option=antardhasa_option,
        parent_end_jd=parent_end_jd,
    )

    for (child_lords, child_start_jd, child_end_jd, child_duration) in children:
        _expand_all_levels(
            child_lords,
            child_start_jd,
            child_end_jd,
            child_duration,
            target_depth,
            place,
            antardhasa_option=antardhasa_option,
            emit_row=emit_row,
        )


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    seed_star=15,
    dhasa_starting_planet=1,
    antardhasa_option=None,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Returns a list of dhasa rows at selected depth L1..L6.

    RETURNS (default, return_exact_bounds=False -- BACKWARD COMPATIBLE,
    same shape as before the refactor):
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    RETURNS (return_exact_bounds=True -- NEW, opt-in, for validation/
    precision use only; has NO effect unless explicitly requested):
        [
            [lords_tuple, start_jd_float, end_jd_float, duration_years],
            ...
        ]
        Here start_jd/end_jd are the EXACT raw Julian Day values produced by
        _get_chathuraaseethi_children_jd() during the recursive build -- no
        reconstruction, no duration*year_duration approximation, no tuple
        round-trip. When True, `round_duration` is ignored (exact duration
        is always returned) since rounding is only meaningful for display.

    dhasa_level_index:
        1 = Maha only
        2 = Antara
        3 = Pratyantara
        4 = Sookshma
        5 = Prana
        6 = Deha

    REFACTOR NOTE: every level from 2 (Antara) through 6 (Deha) is now
    generated by the same recursive walk (_expand_all_levels) over the
    same single engine (_get_chathuraaseethi_children_jd), cascading the
    CLEAN (equally-split, per this dhasa's own rule) duration top-down AND
    threading each level's already-known end JD down to the next level, so
    the confirmed small-duration drik._get_dhasa_end_jd defect (see
    vimsottari.py V7.2 notes) is never triggered in this cascade.
    """
    utils.validate_star_index(seed_star)
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
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

    tribhagi_factor = 1.0
    dhasa_cycles = 1

    if use_tribhagi_variation:
        tribhagi_factor = 1.0 / 3.0
        dhasa_cycles = int(dhasa_cycles / tribhagi_factor)

    dhasa_lord, start_jd, _ = _dhasa_start(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    retval = []

    def _emit_row(lords_tuple, start_jd_local, end_jd_local, duration_years):
        if return_exact_bounds:
            retval.append([lords_tuple, start_jd_local, end_jd_local, float(duration_years)])
        else:
            durn = round(duration_years, dhasa_level_index) if round_duration else duration_years
            retval.append([lords_tuple, utils.jd_to_gregorian(start_jd_local), durn])

    for _ in range(dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            maha_dur = dhasa_adhipathi_list[dhasa_lord] * tribhagi_factor
            maha_start_jd = start_jd
            maha_end_jd = drik._get_dhasa_end_jd(
                start_jd=maha_start_jd, place=place, total_dasa_years=maha_dur,
            )

            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                _emit_row((dhasa_lord,), maha_start_jd, maha_end_jd, maha_dur)
            else:
                _expand_all_levels(
                    (dhasa_lord,),
                    maha_start_jd,
                    maha_end_jd,
                    maha_dur,
                    dhasa_level_index,
                    place,
                    antardhasa_option=antardhasa_option,
                    emit_row=_emit_row,
                )

            start_jd = maha_end_jd
            dhasa_lord = _next_adhipati(dhasa_lord)

    return retval


def _generate_mahadasas_covering(current_jd, jd, place, *, divisional_chart_factor=1,
                                  chart_method=1, star_position_from_moon=1,
                                  seed_star=15, dhasa_starting_planet=1,
                                  use_tribhagi_variation=False, max_cycles=20):
    """
    Generate (lord, start_jd, end_jd, duration_years) rows for consecutive
    Mahadasas, starting from the seed Mahadasa, looping the 7-lord/84-year
    cycle as many times as needed (capped at max_cycles) until current_jd is
    covered. Avoids any dependency on jhora.utils for this.
    """
    tribhagi_factor = (1.0 / 3.0) if use_tribhagi_variation else 1.0

    dhasa_lord, start_jd, _res = _dhasa_start(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    rows = []
    n_lords = len(dhasa_adhipathi_list)
    for _cycle in range(max_cycles):
        for _ in range(n_lords):
            maha_dur = dhasa_adhipathi_list[dhasa_lord] * tribhagi_factor
            maha_start_jd = start_jd
            maha_end_jd = drik._get_dhasa_end_jd(
                start_jd=maha_start_jd, place=place, total_dasa_years=maha_dur,
            )
            rows.append((dhasa_lord, maha_start_jd, maha_end_jd, maha_dur))
            start_jd = maha_end_jd
            dhasa_lord = _next_adhipati(dhasa_lord)
        if rows[-1][2] > current_jd:
            break
    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Narrow Maha -> ... -> target depth and return the full running ladder:

        [
            [(l1,),                start1, end1],
            [(l1,l2),              start2, end2],
            ...
            [(l1,l2,l3,l4,l5,l6),  start6, end6],
        ]

    Walks down using the SAME _get_chathuraaseethi_children_jd() engine
    that get_dhasa_bhukthi() uses for the full tree, threading each level's
    already-known end JD into the NEXT level's call as parent_end_jd --
    exactly mirroring vimsottari.py's V7.2 fix.

    NOTE: no longer depends on jhora.utils.get_running_dhasa_for_given_date()
    (confirmed, during the vimsottari refactor, to have its own independent
    bisect/stride reconstruction bug) -- Mahadasa containment is found via
    _generate_mahadasas_covering() (this module's own arithmetic), and deeper
    levels via a plain linear scan over this module's own exact child
    boundaries.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = const.MAHA_DHASA_DEPTH.DEHA
    target_depth = max(
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        min(const.MAHA_DHASA_DEPTH.DEHA, target_depth),
    )

    divisional_chart_factor = kwargs.get("divisional_chart_factor", 1)
    chart_method = kwargs.get("chart_method", 1)
    star_position_from_moon = kwargs.get("star_position_from_moon", 1)
    use_tribhagi_variation = kwargs.get("use_tribhagi_variation", False)
    seed_star = kwargs.get("seed_star", 15)
    dhasa_starting_planet = kwargs.get("dhasa_starting_planet", 1)
    antardhasa_option = kwargs.get("antardhasa_option", const.antardhasa_option_default)

    maha_rows = _generate_mahadasas_covering(
        current_jd, jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        use_tribhagi_variation=use_tribhagi_variation,
    )

    md_lord, md_start_jd, md_end_jd, md_dur = maha_rows[-1]
    for (lord, s, e, dur) in maha_rows:
        if s <= current_jd < e:
            md_lord, md_start_jd, md_end_jd, md_dur = lord, s, e, dur
            break

    running_all = [[(md_lord,), md_start_jd, md_end_jd]]

    if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        return [
            [lords, utils.jd_to_gregorian(s), utils.jd_to_gregorian(e)]
            for (lords, s, e) in running_all
        ]

    parent_lords = (md_lord,)
    parent_start_jd = md_start_jd
    parent_duration = md_dur
    parent_end_jd = md_end_jd

    for depth in range(2, target_depth + 1):
        children, parent_end_jd = _get_chathuraaseethi_children_jd(
            parent_lords=parent_lords,
            parent_start_jd=parent_start_jd,
            parent_duration=parent_duration,
            place=place,
            antardhasa_option=antardhasa_option,
            parent_end_jd=parent_end_jd,
        )
        running_all[-1][2] = parent_end_jd

        if not children:
            raise ValueError("No children generated; check parent span or child generator options.")

        chosen = children[-1]
        for child in children:
            _, cstart, cend, _cdur = child
            if cstart <= current_jd < cend:
                chosen = child
                break

        child_lords, child_start_jd, child_end_jd, child_duration = chosen
        running_all.append([child_lords, child_start_jd, child_end_jd])

        parent_lords = child_lords
        parent_start_jd = child_start_jd
        parent_duration = child_duration
        parent_end_jd = child_end_jd

    return [
        [lords, utils.jd_to_gregorian(s), utils.jd_to_gregorian(e)]
        for (lords, s, e) in running_all
    ]


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=15,
    antardhasa_option=None,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Nakshathra dhasa progression.

    For divisional charts:
        First calculate progression for rasi, then apply varga division to
        progressed rasi longitudes.
    """
    utils.validate_star_index(seed_star)
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
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
        antardhasa_option=antardhasa_option,
        dhasa_starting_planet=dhasa_starting_planet,
        dhasa_level_index=DLI,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    vdc = None

    if get_running_dhasa:
        vdc = get_running_dhasa_for_given_date(
            jd_current,
            jd_at_dob,
            place,
            dhasa_level_index=DLI,
            star_position_from_moon=star_position_from_moon,
            use_tribhagi_variation=use_tribhagi_variation,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            seed_star=seed_star,
            antardhasa_option=antardhasa_option,
            dhasa_starting_planet=dhasa_starting_planet,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
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

# ---------------------------------------------------------------------
# Example usage / duration-method test
# ---------------------------------------------------------------------
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    from datetime import datetime
    import random
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y,m,d=(2010,11,9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh,mm,ss = (13,29,45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    _antardhasa_option = 1
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
                antardhasa_option = _antardhasa_option,
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
            antardhasa_option = _antardhasa_option,
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
    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chathuraseethi_sama_tests()