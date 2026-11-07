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
Calculates Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana
"""
"""
Release History:
    V4.8.6 - dhasa start state for Rahu lord fixed
    V4.8.9 - minor argument call fixes.
    V4.9.0 - dhasa start date calculation now uses drik._get_dhasa_star_jd()
             to calculate dhasa start date using how much Sun has tranversed.
    V5.0   - REFACTOR (matches JHora results)
"""

from collections import OrderedDict as Dict
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import house, charts


year_duration = const.sidereal_year
human_life_span_for_ashtottari_dhasa = const.human_life_span_for_ashtottari_dhasa
one_star = 360 / 27.0

# Defensive backstop threshold (days). Mirrors vimsottari.py's
# _END_JD_SANITY_SLACK_DAYS. If drik._get_dhasa_end_jd() is ever called
# fresh (no known parent_end_jd) with a small duration and the returned span
# differs from the naive proportional estimate by more than this many days,
# we distrust the primitive's result and fall back to the proportional
# estimate instead of propagating a corrupted boundary.
_END_JD_SANITY_SLACK_DAYS = 30.0


def _norm27(x):
    """Normalize any integer to the 1..27 range; treat 0 as 27."""
    x = x % 27
    return 27 if x == 0 else x


def ashtottari_md_segment_angles(md_lords, seed_star=6, one_nak=one_star, get_mapping_fn=None):
    """
    Build per-Mahadasa angle spans in degrees for Ashtottari, honoring seed_star.

    Args:
        md_lords:
            Iterable of lord IDs in the same order as Mahadasa JD boundaries.
        seed_star:
            int in 0..26, with 0 treated as 27.
        one_nak:
            Angle of one nakshatra; defaults to 360/27.
        get_mapping_fn:
            Function compatible with _get_dhasa_dict(seed_star), returning:
                {lord: [(start_star, end_star), duration_years]}

    Returns:
        List of angle spans in degrees, one per Mahadasa.
    """
    if get_mapping_fn is None:
        try:
            get_mapping_fn = _get_dhasa_dict
        except NameError:
            raise ValueError("Provide get_mapping_fn or ensure _get_dhasa_dict is in scope.")

    seed = _norm27(seed_star)
    mapping = get_mapping_fn(seed)

    angles = []

    for lord in md_lords:
        (sb, se), _ = mapping[lord]

        sb = _norm27(sb)
        se = _norm27(se)

        if se < sb:
            count = (se + 27) - sb + 1
        else:
            count = se - sb + 1

        angles.append(count * one_nak)

    return angles


"""
{ashtottari adhipati:[(starting_star_number,ending_star_number),dasa_length]}

Ashtottari longitude range:
    (starting_star_number - 1) * 360/27 TO ending_star_number * 360/27

Example:
    66.67 to 120.00 = 53 deg 20 min range
"""

ashtottari_adhipathi_list = [0, 1, 2, 3, 6, 4, 7, 5]

ashtottari_adhipathi_dict_seed = {
    0: [(6, 9), 6],
    1: [(10, 12), 15],
    2: [(13, 16), 8],
    3: [(17, 19), 17],
    6: [(20, 22), 10],
    4: [(23, 25), 19],
    7: [(26, 2), 12],
    5: [(3, 5), 21],
}


def applicability_check(planet_positions):
    asc_house = planet_positions[0][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    house_of_lagna_lord = planet_positions[lagna_lord + 1][1][0]
    rahu_house = planet_positions[const.RAHU_ID + 1][1][0]

    chk1 = rahu_house in house.trines_of_the_raasi(house_of_lagna_lord) and rahu_house != asc_house
    chk2 = rahu_house in house.quadrants_of_the_raasi(house_of_lagna_lord) and rahu_house != asc_house

    return chk1 or chk2


def _get_dhasa_dict(seed_star=6):
    if seed_star == 6:
        return ashtottari_adhipathi_dict_seed

    ashtottari_adhipathi_dict = {}
    nak = seed_star

    for p, [(nb, ne), durn] in ashtottari_adhipathi_dict_seed.items():
        nak_diff = ne - nb
        nsb = nak
        nse = (nsb + nak_diff) % 28

        ashtottari_adhipathi_dict[p] = [(nsb, nse), durn]

        nak = (nse + 1) % 28

    return ashtottari_adhipathi_dict


ashtottari_adhipathi_dict = _get_dhasa_dict(seed_star=6)


def ashtottari_adhipathi(nak):
    global ashtottari_adhipathi_dict

    for key, value in ashtottari_adhipathi_dict.items():
        starting_star = value[0][0]
        ending_star = value[0][1]
        nak1 = nak

        if ending_star < starting_star:
            ending_star += 27

            if nak1 < starting_star:
                nak1 += 27

        if starting_star <= nak1 <= ending_star:
            return key, value

    return None, None


def ashtottari_dasha_start_date(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=const.MOON_ID,
):
    planet_long = charts.get_chart_element_longitude(
        jd=jd,
        place=place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    nak = int(planet_long / one_star)

    lord, res = ashtottari_adhipathi(nak + 1)

    if lord is None or res is None:
        raise ValueError(
            "Unable to determine Ashtottari adhipathi for nakshatra {}".format(nak + 1)
        )

    period = res[1]
    start_nak = res[0][0]
    end_nak = res[0][1]

    start_deg = (start_nak - 1) * one_star
    pl = planet_long

    if end_nak < start_nak and pl < start_deg:
        pl += 360

    span_stars = utils.count_stars(start_nak, end_nak, direction=1, total=27)
    total_span = span_stars * one_star
    elapsed_span = pl - start_deg

    fraction_elapsed = elapsed_span / total_span

    start_jd = drik._get_dhasa_start_jd(
        jd,
        place,
        fraction_elapsed=fraction_elapsed,
        total_dasa_years=period,
    )

    return [lord, start_jd]


def ashtottari_next_adhipati(lord, dirn=1):
    """Returns next lord after lord in the adhipati list."""
    current = ashtottari_adhipathi_list.index(lord)
    next_index = (current + dirn) % len(ashtottari_adhipathi_list)

    return ashtottari_adhipathi_list[next_index]


def ashtottari_mahadasa(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
):
    """
    Returns dictionary of all Mahadasas and their start JDs.

    Maha durations (6-21 years) are far outside the confirmed small-duration
    bug band, so calling drik._get_dhasa_end_jd directly here (as the
    original code did) remains safe -- this seed/root generator is
    unchanged.

    Returns:
        OrderedDict: {mahadhasa_lord_index: start_jd}
    """
    lord, start_date = ashtottari_dasha_start_date(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    retval = Dict()

    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date

        lord_duration = ashtottari_adhipathi_dict[lord][1]

        start_date = drik._get_dhasa_end_jd(
            start_jd=start_date,
            place=place,
            total_dasa_years=lord_duration,
        )

        lord = ashtottari_next_adhipati(lord)

    return retval


def ashtottari_bhukthi(dhasa_lord, start_date, place, antardhasa_option=None):
    """
    LEGACY (kept for backward compatibility / external callers): compute all
    bhukthis of a given Mahadasa lord and its start date, using a single
    unconditional drik._get_dhasa_end_jd chain.

    NOT used internally by get_dhasa_bhukthi()/get_running_dhasa_for_given_date()
    anymore (see _get_ashtottari_children_jd below). Left untouched.
    """
    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict

    lord, dirn = _start_lord_and_dir(dhasa_lord,antardhasa_option)

    retval = Dict()

    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]

    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date

        lord_duration = ashtottari_adhipathi_dict[lord][1]

        factor = (
            lord_duration
            * dhasa_lord_duration
            / human_life_span_for_ashtottari_dhasa
        )

        start_date = drik._get_dhasa_end_jd(
            start_jd=start_date,
            place=place,
            total_dasa_years=factor,
        )

        lord = ashtottari_next_adhipati(lord, dirn)

    return retval


def ashtottari_anthara(dhasa_lord, bhukthi_lord, bhukthi_lord_start_date, place):
    """
    LEGACY (kept for backward compatibility): compute all antharas for a
    given Mahadasa lord, Bhukthi lord, and Bhukthi start date. NOT used
    internally anymore. Left untouched.
    """
    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict

    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    bhukthi_lord_duration = ashtottari_adhipathi_dict[bhukthi_lord][1]

    retval = Dict()
    lord = bhukthi_lord

    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date

        lord_duration = ashtottari_adhipathi_dict[lord][1]

        factor = (
            lord_duration
            * dhasa_lord_duration
            * bhukthi_lord_duration
            / human_life_span_for_ashtottari_dhasa
            / human_life_span_for_ashtottari_dhasa
        )

        bhukthi_lord_start_date = drik._get_dhasa_end_jd(
            start_jd=bhukthi_lord_start_date,
            place=place,
            total_dasa_years=factor,
        )

        lord = ashtottari_next_adhipati(lord)

    return retval


### --- NEW: shared cascade helpers (mirror vimsottari.py's shape) ----------
def _start_lord_and_dir(parent_lord, antardhasa_option):
    """Single definition of the antardhasa_option -> (start_lord, direction)
    rule -- same option semantics as the original ashtottari_bhukthi()."""
    lord = parent_lord
    if antardhasa_option in [const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
                             const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_BACKWARD]:
        lord = ashtottari_next_adhipati(lord, dirn=1)
    elif antardhasa_option in [const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD,
                               const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_BACKWARD]:
        lord = ashtottari_next_adhipati(lord, dirn=-1)
    dirn = (1 if antardhasa_option in [const.ANTARDHASA_OPTION.START_FROM_DHASA_LORD_GO_FORWARD,
                                       const.ANTARDHASA_OPTION.START_FROM_NEXT_DHASA_LORD_GO_FORWARD,
                                       const.ANTARDHASA_OPTION.START_FROM_PREVIOUS_DHASA_LORD_GO_FORWARD] 
                        else -1)
    return lord, dirn

def _child_sequence(parent_lord, antardhasa_option):
    """Ordered list of the 8 child lords for a given parent lord."""
    lord, dirn = _start_lord_and_dir(parent_lord, antardhasa_option)
    seq = []
    l = lord
    for _ in range(len(ashtottari_adhipathi_list)):
        seq.append(l)
        l = ashtottari_next_adhipati(l, dirn)
    return seq


### --- SINGLE CHILD-GENERATION ENGINE ---------------------------------------
def _get_ashtottari_children_jd(
    parent_lords,
    parent_start_jd,
    parent_duration,
    place,
    *,
    antardhasa_option=None,
    parent_end_jd=None,
):
    """
    THE authoritative Ashtottari child-generation engine (JD-based).

    Every level (MD->AD, AD->PD, PD->SD, SD->PrD, PrD->DD) is generated by
    this ONE function, called recursively. There is no other place in this
    module (post-refactor) that computes a child dhasa boundary.

    parent_duration MUST be the clean cascaded symbolic duration
    (parent_of_parent_duration * V[parent_lord] / H), NEVER a value
    back-derived from an already-materialized calendar span.

    parent_end_jd : float, optional
        If the CALLER already knows this parent's exact end JD (true for
        every level below the first), pass it here. It is then used AS-IS
        and drik._get_dhasa_end_jd is never called for it -- avoiding any
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
    global year_duration, human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
    parent_lord = parent_lords[-1]
    H = float(human_life_span_for_ashtottari_dhasa)

    if parent_end_jd is None:
        # Only reached when the caller does NOT already know this boundary.
        # Safe for Maha/Antara-scale durations; guarded here in case this is
        # ever invoked with a small duration from some other caller.
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

    sequence = _child_sequence(parent_lord, antardhasa_option)
    child_durations = [
        float(parent_duration) * float(ashtottari_adhipathi_dict[l][1]) / H
        for l in sequence
    ]
    total_child_years = sum(child_durations) or 1.0
    span = parent_end_jd - parent_start_jd
    min_child_days = min(child_durations) * year_duration

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
        remaining_years = total_child_years
        for idx, (clord, cdur) in enumerate(zip(sequence, child_durations)):
            if idx == len(sequence) - 1:
                child_end_jd = parent_end_jd
            else:
                child_end_jd = drik._get_dhasa_end_jd(
                    start_jd=jd_cursor, place=place, total_dasa_years=cdur,
                )
                if not (jd_cursor < child_end_jd < parent_end_jd):
                    frac = cdur / remaining_years if remaining_years > 0 else 0.0
                    child_end_jd = jd_cursor + (parent_end_jd - jd_cursor) * frac
            children.append((parent_lords + (clord,), jd_cursor, child_end_jd, cdur))
            jd_cursor = child_end_jd
            remaining_years -= cdur
    else:
        # Sub-day (or otherwise below the safe per-child arc threshold):
        # proportional division within the ALREADY-KNOWN parent span. This
        # branch never calls drik._get_dhasa_end_jd per child, so it can
        # never hit the confirmed small-duration bug regardless of how
        # small the children are.
        cum = 0.0
        for idx, (clord, cdur) in enumerate(zip(sequence, child_durations)):
            cstart = parent_start_jd + span * (cum / total_child_years)
            cum += cdur
            cend = parent_end_jd if idx == len(sequence) - 1 else parent_start_jd + span * (cum / total_child_years)
            children.append((parent_lords + (clord,), cstart, cend, cdur))

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
):
    """
    Public one-level child API (tuple-date in / tuple-date out wrapper
    around the single _get_ashtottari_children_jd() engine).

    Output:
        [
            [(l1, ..., parent, child), child_start_tuple, child_end_tuple],
            ...
        ]

    If `parent_end` is supplied, it is passed straight through to
    _get_ashtottari_children_jd() as `parent_end_jd` -- used AS-IS, never
    re-derived via drik._get_dhasa_end_jd. `parent_duration_years`
    (back-derived from the given span in that case) is still used to
    compute the children's proportional SHAPE.
    """
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
    if place is None:
        raise ValueError("place is required for exact Ashtottari child boundary calculation.")

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)):
        if len(parent_lords) == 0:
            raise ValueError("parent_lords cannot be empty")
        path = tuple(parent_lords)
    else:
        raise TypeError("parent_lords must be int or tuple/list of ints")

    parent_lord = path[-1]

    if parent_lord not in ashtottari_adhipathi_list:
        raise ValueError(
            "Parent lord {} not in Ashtottari sequence {}".format(
                parent_lord, ashtottari_adhipathi_list,
            )
        )

    start_jd = utils._tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration_years or parent_end")

    known_end_jd = None
    if parent_end is None:
        clean_duration = float(parent_duration)
    else:
        known_end_jd = utils._tuple_to_jd(parent_end)
        if known_end_jd <= start_jd:
            return []
        clean_duration = (known_end_jd - start_jd) / year_duration

    children, _parent_end_jd = _get_ashtottari_children_jd(
        parent_lords=path,
        parent_start_jd=start_jd,
        parent_duration=clean_duration,
        place=place,
        antardhasa_option=antardhasa_option,
        parent_end_jd=known_end_jd,
    )

    return [
        [lords, utils._jd_to_tuple(start_jd_c), utils._jd_to_tuple(end_jd_c)]
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
    into _get_ashtottari_children_jd() so it is reused, never recomputed via
    drik._get_dhasa_end_jd.

    emit_row signature: emit_row(lords_tuple, start_jd, end_jd, duration_years)
    """
    depth = len(parent_lords)

    if depth == target_depth:
        emit_row(parent_lords, parent_start_jd, parent_end_jd, parent_duration)
        return

    children, _parent_end_jd_confirmed = _get_ashtottari_children_jd(
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
    dob, tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    antardhasa_option=None,
    dhasa_starting_planet=1,
    seed_star=6,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
    **kwargs,
):
    """
    Provides Ashtottari dhasa at selected depth for a given birth Julian day.

    RETURNS (default, return_exact_bounds=False -- BACKWARD COMPATIBLE with
    the original module, which returns ONLY the flat row list, no balance
    tuple):
        [ [lords_tuple, (Y, M, D, fractional_hour), duration_years_float], ... ]

    RETURNS (return_exact_bounds=True -- for validation/precision use):
        [ [lords_tuple, start_jd_float, end_jd_float, duration_years_float], ... ]

    Every level from 2 (Antara) through 6 (Deha) is generated by the same
    recursive walk (_expand_all_levels) over the same single engine
    (_get_ashtottari_children_jd), cascading the CLEAN symbolic duration
    top-down AND threading each level's already-known end JD down to the
    next level, exactly mirroring vimsottari.py's V7.2 fix.
    """
    jd = utils.julian_day_number(dob,tob)
    utils.validate_star_index(seed_star)
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default

    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    orig_H = human_life_span_for_ashtottari_dhasa
    orig_dict = ashtottari_adhipathi_dict.copy()

    try:
        working_dict = _get_dhasa_dict(seed_star)

        if use_tribhagi_variation:
            trib = 1.0 / 3.0
            H = orig_H * trib
            working_dict = {
                k: [v[0], v[1] * trib]
                for k, v in working_dict.items()
            }
            dhasa_cycles = int(1 / trib)
        else:
            H = orig_H
            dhasa_cycles = 1

        human_life_span_for_ashtottari_dhasa = H
        ashtottari_adhipathi_dict = working_dict

        dashas = ashtottari_mahadasa(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            star_position_from_moon=star_position_from_moon,
            dhasa_starting_planet=dhasa_starting_planet,
        )

        dhasa_bhukthi = []

        def _emit_row(lords_tuple, start_jd, end_jd, duration_years):
            if return_exact_bounds:
                dhasa_bhukthi.append(
                    [lords_tuple, start_jd, end_jd, float(duration_years)]
                )
            else:
                dhasa_bhukthi.append(
                    [lords_tuple, utils.jd_to_gregorian(start_jd), float(duration_years)]
                )

        md_items = list(dashas.items())

        for _ in range(dhasa_cycles):
            for idx, (md_lord, md_start_jd) in enumerate(md_items):
                md_years = float(ashtottari_adhipathi_dict[md_lord][1])
                # md_end_jd: reuse next MD's own recorded start when
                # available (exact, zero extra computation); only the very
                # last MD in the sequence needs a fresh primitive call, and
                # Maha-scale durations (6-21 years) are safely outside the
                # confirmed bug band.
                if idx < len(md_items) - 1:
                    md_end_jd = md_items[idx + 1][1]
                else:
                    md_end_jd = drik._get_dhasa_end_jd(
                        start_jd=md_start_jd, place=place, total_dasa_years=md_years,
                    )

                if (dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
                        or dhasa_level_index == 1):
                    _emit_row((md_lord,), md_start_jd, md_end_jd, md_years)
                    continue

                _expand_all_levels(
                    (md_lord,),
                    md_start_jd,
                    md_end_jd,
                    md_years,
                    dhasa_level_index,
                    place,
                    antardhasa_option=antardhasa_option,
                    emit_row=_emit_row,
                )

        return dhasa_bhukthi

    finally:
        human_life_span_for_ashtottari_dhasa = orig_H
        ashtottari_adhipathi_dict = orig_dict


def get_running_dhasa_for_given_date(
    current_jd,
    jd,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Ashtottari-specific runner that finds the running dhasa at the requested
    depth. Returns the full running ladder:
        [ [lords_tuple, start_tuple, end_tuple], ... ]  (one row per level)

    Walks down using the SAME _get_ashtottari_children_jd() engine that
    get_dhasa_bhukthi() uses for the full tree, threading each level's
    already-known end JD (child_end_jd) into the NEXT level's call as
    parent_end_jd -- exactly mirroring vimsottari.py's V7.2 fix, so the
    confirmed small-duration drik._get_dhasa_end_jd defect pattern is never
    triggered here either, and OLD (full tree) / NEW (this function) cannot
    structurally diverge.

    NOTE: unlike the pre-refactor version, this no longer calls
    jhora.utils.get_running_dhasa_for_given_date()/
    get_running_dhasa_at_all_levels_for_given_date() at all -- that utility
    was found (during the vimsottari refactor) to have its own independent
    bisect/stride reconstruction bug. Containment is now a plain linear scan
    over this module's own exact child boundaries.
    """
    global year_duration, human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = const.MAHA_DHASA_DEPTH.DEHA
    target_depth = max(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, min(const.MAHA_DHASA_DEPTH.DEHA, target_depth))

    antardhasa_option = kwargs.get("antardhasa_option", const.antardhasa_option_default)
    seed_star = kwargs.get("seed_star", 6)
    dhasa_starting_planet = kwargs.get("dhasa_starting_planet", 1)

    orig_H = human_life_span_for_ashtottari_dhasa
    orig_dict = ashtottari_adhipathi_dict.copy()

    try:
        # Honor seed_star the same way get_dhasa_bhukthi() does, so the
        # running lookup uses the same lord-boundary table as the full tree.
        ashtottari_adhipathi_dict = _get_dhasa_dict(seed_star)

        # --- Level 1: find running Mahadasa ---------------------------------
        dashas = ashtottari_mahadasa(
            jd,
            place,
            star_position_from_moon=kwargs.get("star_position_from_moon", 1),
            dhasa_starting_planet=dhasa_starting_planet,
        )
        md_items = list(dashas.items())

        md_lord, md_start_jd = md_items[0]
        md_end_jd_known = None
        for idx, (lord, start_jd) in enumerate(md_items):
            next_start_jd = md_items[idx + 1][1] if idx < len(md_items) - 1 else None
            if start_jd <= current_jd and (next_start_jd is None or current_jd < next_start_jd):
                md_lord, md_start_jd = lord, start_jd
                md_end_jd_known = next_start_jd
                break

        md_years = float(ashtottari_adhipathi_dict[md_lord][1])

        running_all = []
        _, md_end_jd = _get_ashtottari_children_jd(
            (md_lord,), md_start_jd, md_years, place,
            antardhasa_option=antardhasa_option,
            parent_end_jd=md_end_jd_known,
        )
        running_all.append([(md_lord,), md_start_jd, md_end_jd])

        if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            return [
                [lords, utils._jd_to_tuple(s), utils._jd_to_tuple(e)] for (lords, s, e) in running_all
            ]

        # --- Levels 2..target_depth: descend via the SAME engine -----------
        parent_lords = (md_lord,)
        parent_start_jd = md_start_jd
        parent_duration = md_years
        parent_end_jd = md_end_jd

        for depth in range(2, target_depth + 1):
            children, parent_end_jd = _get_ashtottari_children_jd(
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
            [lords, utils._jd_to_tuple(s), utils._jd_to_tuple(e)] for (lords, s, e) in running_all
        ]

    finally:
        human_life_span_for_ashtottari_dhasa = orig_H
        ashtottari_adhipathi_dict = orig_dict


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=6,
    antardhasa_option=None,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    utils.validate_star_index(seed_star)
    if antardhasa_option is None: antardhasa_option = const.antardhasa_option_default
    DLI = dhasa_level_index
    y,m,d,fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y,m,d); tob = (fh,0,0)
    vd = get_dhasa_antardhasa(
        dob,tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        antardhasa_option=antardhasa_option,
        dhasa_starting_planet=dhasa_starting_planet,
        seed_star=seed_star,
        dhasa_level_index=DLI,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )

    vdc = None

    if get_running_dhasa:
        vd_for_utils = [(row[0], row[1]) for row in vd]
        vdc = utils.get_running_dhasa_for_given_date(jd_current, vd_for_utils)
        print(vdc)

    jds = [
        utils.julian_day_number(drik.Date(row[1][0], row[1][1], row[1][2]), (row[1][3], 0, 0))
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
        total_lords_in_dhasa=len(ashtottari_adhipathi_list),
    )

    progression_correction = (prog_long - planet_long) % 360

    if get_running_dhasa:
        return progression_correction, vdc

    return progression_correction

def validate_old_new_consistency(
    jd_at_dob,
    place,
    num_random_dates=200,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    dhasa_duration_type=None,
    year_range=(1997, 2050),
    tol_seconds=1e-3,
    verbose=True,
):
    """
    Randomized OLD-vs-NEW self-consistency check -- FULLY SELF-CONTAINED
    (mirrors vimsottari.py's validator).

    OLD = full tree via get_dhasa_bhukthi(..., return_exact_bounds=True),
          then ancestor levels reconstructed by utils._group_ancestors_from_leaves()
          (a plain contiguous groupby over the tree's OWN exact leaf bounds).
    NEW = get_running_dhasa_for_given_date(...)

    Both sides use ONLY this module's _get_ashtottari_children_jd()
    arithmetic -- no dependency on jhora.utils' bisect/stride reconstruction.
    """
    import random
    y,m,d,fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y,m,d); tob = (fh,0,0)
    full_tree = get_dhasa_antardhasa(
        dob,tob,
        place,
        dhasa_level_index=dhasa_level_index,
        dhasa_duration_type=dhasa_duration_type,
        return_exact_bounds=True,
    )

    level_groups = {
        level: utils._group_ancestors_from_leaves(full_tree, level)
        for level in range(1, dhasa_level_index + 1)
    }

    tol_days = tol_seconds / 86400.0
    mismatches = []

    for _ in range(num_random_dates):
        y = random.randrange(year_range[0], year_range[1])
        m = random.randrange(1, 12)
        d = random.randrange(1, 26)
        hh = random.randrange(0, 23)
        mm = random.randrange(0, 59)
        ss = random.randrange(0, 59)
        current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

        old_path = [
            utils._find_containing_group(level_groups[level], current_jd)
            for level in range(1, dhasa_level_index + 1)
        ]

        new_path_tuples = get_running_dhasa_for_given_date(
            current_jd,
            jd_at_dob,
            place,
            dhasa_level_index=dhasa_level_index,
            dhasa_duration_type=dhasa_duration_type,
        )
        new_path = [
            (tuple(lords), utils._tuple_to_jd(s), utils._tuple_to_jd(e))
            for (lords, s, e) in new_path_tuples
        ]

        reason = None
        if len(old_path) != len(new_path):
            reason = f"length mismatch: {len(old_path)} vs {len(new_path)}"
        else:
            for level, ((lo, so, eo), (ln, sn, en)) in enumerate(zip(old_path, new_path), start=1):
                if lo != ln:
                    reason = f"level {level}: lord mismatch {lo} vs {ln}"
                    break
                if abs(so - sn) > tol_days:
                    reason = f"level {level}: start mismatch (Δ={abs(so - sn) * 86400:.3f}s)"
                    break
                if abs(eo - en) > tol_days:
                    reason = f"level {level}: end mismatch (Δ={abs(eo - en) * 86400:.3f}s)"
                    break

        if reason:
            mismatches.append({"date": (y, m, d, hh, mm, ss), "reason": reason,
                                "old": old_path, "new": new_path})
            if verbose:
                print(f"MISMATCH at {(y, m, d, hh, mm, ss)}: {reason}")

    if verbose:
        print(f"\n{num_random_dates - len(mismatches)}/{num_random_dates} random dates matched "
              f"(tol={tol_seconds*1000:.1f} ms).")

    return mismatches


# ---------------------------------------------------------------------
# Example usage / duration-method test
# ---------------------------------------------------------------------
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    current_jd = utils.julian_day_number(drik.Date(2010,9,10),(15,29,45))
    print(nakshathra_dhasa_progression(jd_at_dob, place, current_jd))
    exit()
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    from datetime import datetime
    import random
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y,m,d = (2010,11,9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh,mm,ss = (13,29,45)
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
            dob,tob,
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
        continue ### Skip below random validation
        # ---- Broader randomized self-consistency check ---------------------
        print("\nRunning validate_old_new_consistency() over 200 random dates...")
        validate_old_new_consistency(
            jd_at_dob,
            place,
            num_random_dates=200,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
        )
    exit()
    """
    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.ashtottari_tests()
    exit()
    """
