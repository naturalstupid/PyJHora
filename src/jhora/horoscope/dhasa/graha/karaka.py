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
    Karaka Dasa

    A dhasa whose lords are the 7 or 8 "chara karakas" (Atmakaraka,
    Amatyakaraka, etc. -- planets ranked by degree within sign, per
    charts.chara_karakas()), under either of two selectable methods
    (chara_karaka_method, const.CHARA_KARAKA_METHOD):
        EIGHT_KARAKA_PARASHARI
        SEVEN_KARAKA_KNRAO_NOPiK

    Each lord's own Mahadasa duration, dd(planet) = sign-distance (0-11)
    from Lagna to that planet's own sign, is chart-dependent: the total
    span (human_life_span = sum of dd() over all karakas) varies from
    chart to chart, unlike dhasas with a fixed lord-year table. dd() can
    legitimately be 0 if a karaka planet sits in Lagna's own sign, in
    which case that lord's Mahadasa has zero duration and is skipped
    entirely at the Mahadasa level (no zero-width row is produced);
    deeper levels do not skip zero-duration children and emit them as
    legitimate zero-width rows.

    Antardasa order (_antardhasa_planet_order()) rotates starting at the
    next karaka after the parent (wrapping through all karakas), ending
    at the parent lord itself last.

    Every level below Mahadasa splits its parent's duration
    proportionally by dd(): each child's share of the parent's duration
    equals dd(child) / human_life_span.

    show_karaka_as_pair controls how lords are labeled in the returned
    tuples: None returns a plain planet-id int, 1 returns
    (karaka_index, planet_id), and 2 (default) returns
    (karaka_name, planet_id).

    Every dasha boundary (Mahadasa and every level below it) is computed
    via drik._get_dhasa_end_jd(), through the _bounded_end_jd() wrapper,
    which falls back to plain linear (duration * year_duration)
    arithmetic if drik._get_dhasa_end_jd() returns a result more than
    _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate. When a
    batch of children's smallest duration drops below
    _SUB_DAY_DURATION_DAYS, that batch's boundaries are instead computed
    by dd()-weighted proportional interpolation of the parent's own
    [start_jd, end_jd] span, since drik._get_dhasa_end_jd()'s underlying
    solar-transit search is not reliable at sub-day granularity.
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year

supported_chara_karaka_methods = [
    const.CHARA_KARAKA_METHOD.EIGHT_KARAKA_PARASHARI,
    const.CHARA_KARAKA_METHOD.SEVEN_KARAKA_KNRAO_NOPiK,
]

# Sanity backstop (in days) against drik._get_dhasa_end_jd() returning a
# result far from the linear (duration * year_duration) estimate for a
# narrow band of small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# Threshold (in days) below which drik._get_dhasa_end_jd()'s solar-transit
# search is not reliable. When a batch of children's smallest duration
# drops below this threshold, that batch's boundaries are computed via
# dd()-weighted proportional interpolation of the parent's own real span
# instead (see _get_karaka_children_jd()). This is a duration-triggered
# check, re-evaluated fresh for each batch of children at whatever level
# they occur, regardless of child count or individual dd()-derived
# weights (including weight=0 for a Lagna-conjunct karaka).
_SUB_DAY_DURATION_DAYS = 1.0


def _validate_supported_chara_karaka_method(chara_karaka_method):
    # Handle default assignment if None is explicitly passed
    if chara_karaka_method is None:
        chara_karaka_method = const.chara_karaka_default_method

    if chara_karaka_method not in supported_chara_karaka_methods:
        print(f"chara_karaka_method argument {chara_karaka_method} is not supported.\n"
              "Karaka Dasha calculations require a strict 1:1 mapping of planets to karakas "
              "to prevent loop tracking errors.\n"
              "Default: EIGHT_KARAKA_PARASHARI (1) assumed to calculate the karaka dhasa.")
        chara_karaka_method = const.CHARA_KARAKA_METHOD.EIGHT_KARAKA_PARASHARI

    return chara_karaka_method


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


def _extract_planet_id(label):
    """
    The last label in a lords_tuple may be a plain planet-id int, or an
    (index_or_name, planet_id) pair (per show_karaka_as_pair) -- this
    extracts the underlying planet id either way.
    """
    if isinstance(label, tuple) and len(label) == 2 and isinstance(label[1], int):
        return label[1]

    if isinstance(label, int):
        return label

    raise ValueError(f"Unsupported lord label for Karaka dasha: {label}")


def _compute_karakas(planet_positions, chara_karaka_method):
    """
    Computes the ordered list of karaka planet ids (None entries --
    missing karaka assignments -- already excluded) for the given chart,
    plus lookup maps for karaka name/index by planet id.

    Returns: (karakas, karaka_name_by_planet, karaka_index_by_planet)
    """
    karaka_dict = charts.chara_karakas(planet_positions, chara_karaka_method=chara_karaka_method)

    if chara_karaka_method == const.CHARA_KARAKA_METHOD.SEVEN_KARAKA_KNRAO_NOPiK:
        local_karaka_list = [k for k in const.chara_karaka_names if 'pitri' not in k.lower()]
    else:
        local_karaka_list = const.chara_karaka_names

    karakas_raw = []

    for k_name in local_karaka_list:
        matched_planet = None

        for p_id, names in karaka_dict.items():
            if k_name in names:
                matched_planet = p_id
                break

        karakas_raw.append(matched_planet)

    karaka_name_by_planet = {}
    karaka_index_by_planet = {}
    karakas = []

    for idx, pl in enumerate(karakas_raw):
        if pl is not None:
            karakas.append(pl)
            karaka_name_by_planet[pl] = local_karaka_list[idx]
            karaka_index_by_planet[pl] = idx

    return karakas, karaka_name_by_planet, karaka_index_by_planet


def _dd(pl, planet_positions, asc_house):
    """
    Sign-distance (0-11) from Lagna to planet pl's own sign -- this is the
    lord's own Mahadasa/antara-share duration weight (in years, at
    Mahadasa level; proportionally at every level below). Can
    legitimately be 0 if pl sits in Lagna's own sign.
    """
    return (planet_positions[pl + 1][1][0] - asc_house + 12) % 12


def _antardhasa_planet_order(parent_planet, karakas):
    """
    Returns the antara-level child planet ids (not yet labeled) for a
    given parent_planet, in rotation order: starting at the next karaka
    after parent_planet (wrapping through all karakas), ending at
    parent_planet itself last.
    """
    ki = karakas.index(parent_planet)

    return karakas[ki + 1:] + karakas[:ki + 1]


def _label(pl, show_karaka_as_pair, karaka_name_by_planet, karaka_index_by_planet):
    """
    Applies the show_karaka_as_pair display convention to a raw planet id.
    """
    if pl is None:
        return ("None", None)

    if show_karaka_as_pair is None:
        return pl

    if show_karaka_as_pair == 2:
        return (karaka_name_by_planet[pl], pl)

    return (karaka_index_by_planet[pl], pl)


def _get_karaka_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    karakas,
    planet_positions,
    asc_house,
    human_life_span,
    *,
    show_karaka_as_pair=2,
    karaka_name_by_planet=None,
    karaka_index_by_planet=None,
    parent_end_jd=None,
):
    """
    Single children-engine for Karaka Dasa.

    Rules:
        - Child order via _antardhasa_planet_order(parent_planet, karakas)
          -- rotate starting at next karaka after parent, wrapping, ending
          at parent itself last.
        - Proportional-by-dd() split: each child's share of parent_
          duration is dd(child) / human_life_span. dd(child) can
          legitimately be 0 (a zero-width child).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's per-child duration is under
          _SUB_DAY_DURATION_DAYS, all child boundaries (not just the
          last) are computed via dd()-weighted proportional interpolation
          of the parent's own real [parent_start_jd, parent_end_jd] span,
          instead of calling _bounded_end_jd()/drik._get_dhasa_end_jd()
          per child.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
            (child_path_tuple elements are already display-labeled per
            show_karaka_as_pair)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    parent_planet = _extract_planet_id(parent_path[-1])

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    child_planets = _antardhasa_planet_order(parent_planet, karakas)

    n = len(child_planets)

    if n == 0:
        return [], parent_end_jd

    child_dds = [_dd(cp, planet_positions, asc_house) for cp in child_planets]

    smallest_child_years = parent_duration * min(child_dds) / human_life_span
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd
    cumulative_dd = 0.0

    for i, cp in enumerate(child_planets):
        dd_child = child_dds[i]
        child_duration = parent_duration * dd_child / human_life_span

        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_dd += dd_child
            child_end_jd = parent_start_jd + parent_span * cumulative_dd / human_life_span
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        clabel = _label(cp, show_karaka_as_pair, karaka_name_by_planet, karaka_index_by_planet)

        children.append(
            (
                parent_path + (clabel,),
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
    karakas,
    planet_positions,
    asc_house,
    human_life_span,
    *,
    show_karaka_as_pair=2,
    karaka_name_by_planet=None,
    karaka_index_by_planet=None,
    stop_at_jd=None,
):
    """
    The single Mahadasa seed/root generator for Karaka Dasa. Cycles
    through the karakas list starting from the birth JD.
    get_dhasa_antardhasa() and get_running_dhasa_for_given_date() both
    call this same generator.

    Karaka lords whose dd()=0 (planet sits in Lagna's own sign) are
    skipped entirely at this (Mahadasa) level -- no zero-width Mahadasa
    row is ever produced. Deeper levels do not skip zero-duration
    children.

    Yields:
        (maha_label, maha_start_jd, maha_dur, maha_end_jd)
        (maha_label is already display-labeled per show_karaka_as_pair)
    """
    start_jd = jd_at_dob

    for k in karakas:
        maha_dur = _dd(k, planet_positions, asc_house)

        if maha_dur == 0:
            continue

        maha_start_jd = start_jd
        maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

        maha_label = _label(k, show_karaka_as_pair, karaka_name_by_planet, karaka_index_by_planet)

        yield maha_label, maha_start_jd, maha_dur, maha_end_jd

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
    chart_method=1,  # Kept strictly for divisional_chart configuration
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    show_karaka_as_pair=2,   # None=>Don't show pair, 1=>Index pair, 2=>Name pair
    dhasa_duration_type=None,
    savana_year_method=None,
    chara_karaka_method=None,  # Dedicated explicit argument for the 2 supported methods
    return_exact_bounds=False,
):
    """
    Provides Karaka dhasa-bhukthi for a given date in julian day.

    Parameters
    ----------
    show_karaka_as_pair :
        None => Don't show as pair
                return format: (dhasa_lord, start_str, duration)
        1    => Show karaka index (NLS support)
                return format: ((karaka_index, dhasa_lord), start_str, duration)
        2    => Show karaka name
                return format: ((karaka_name, dhasa_lord), start_str, duration)

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]

    Returns
    -------
    list
        if dhasa_level_index == 1:
            [ [ (l1,), start_str, dur_years ], ... ]
        else:
            [ [ (l1, l2, ...), start_str, leaf_dur_years ], ... ]

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level, unless a batch of children is
    sub-day, in which case dd()-weighted proportional interpolation of
    the parent's real span is used instead (see
    _SUB_DAY_DURATION_DAYS above).
    """
    global year_duration

    chara_karaka_method = _validate_supported_chara_karaka_method(chara_karaka_method)

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

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )[:const._pp_count_upto_ketu]

    karakas, karaka_name_by_planet, karaka_index_by_planet = _compute_karakas(
        planet_positions, chara_karaka_method,
    )

    asc_house = planet_positions[0][1][0]

    human_life_span = sum(_dd(k, planet_positions, asc_house) for k in karakas)

    if human_life_span == 0:
        human_life_span = 1.0  # Prevent division by zero

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
        children, _ = _get_karaka_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            karakas,
            planet_positions,
            asc_house,
            human_life_span,
            show_karaka_as_pair=show_karaka_as_pair,
            karaka_name_by_planet=karaka_name_by_planet,
            karaka_index_by_planet=karaka_index_by_planet,
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

    for maha_label, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        karakas,
        planet_positions,
        asc_house,
        human_life_span,
        show_karaka_as_pair=show_karaka_as_pair,
        karaka_name_by_planet=karaka_name_by_planet,
        karaka_index_by_planet=karaka_index_by_planet,
    ):
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row(
                (maha_label,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
            )
        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_path=(maha_label,),
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
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    show_karaka_as_pair: int | None = 2,
    dhasa_duration_type=None,
    savana_year_method=None,
    chara_karaka_method=None,  # Added to properly carry down calculation rule selections
    **kwargs,
):
    """
    Karaka Dasa -- return ONLY the immediate (p -> p+1) children for the
    given parent span.

    A thin wrapper around the shared _get_karaka_children_jd() engine,
    which also backs get_dhasa_antardhasa() and
    get_running_dhasa_for_given_date().

    Matches the base logic:
      - Karakas: charts.chara_karakas(planet_positions)
      - dd(pl) = distance (signs) from Lagna to planet sign
      - human_life_span = sum(dd(k) for k in karakas)
      - children order = rotation of karakas starting AFTER parent_lord
        and wrapping, ending at parent_lord itself
      - child_years = parent_years * dd(child) / human_life_span

    Output rows:
        [ [lords_tuple_with_child, child_start_tuple, child_end_tuple], ... ]
    """
    global year_duration

    chara_karaka_method = _validate_supported_chara_karaka_method(chara_karaka_method)

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
        raise ValueError("parent_lords must be int or non-empty tuple/list")

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

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )[:const._pp_count_upto_ketu]

    karakas, karaka_name_by_planet, karaka_index_by_planet = _compute_karakas(
        planet_positions, chara_karaka_method,
    )

    asc_house = planet_positions[0][1][0]

    human_life_span = sum(_dd(k, planet_positions, asc_house) for k in karakas)

    if human_life_span == 0:
        human_life_span = 1.0

    children, _ = _get_karaka_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        karakas,
        planet_positions,
        asc_house,
        human_life_span,
        show_karaka_as_pair=show_karaka_as_pair,
        karaka_name_by_planet=karaka_name_by_planet,
        karaka_index_by_planet=karaka_index_by_planet,
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
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    show_karaka_as_pair: int | None = 2,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    chara_karaka_method=None,
    **kwargs,
):
    """
    Karaka Dasa -- narrow Maha -> ... -> target level and return the full
    running ladder.

    Drills down this dhasa's own tree using the same recursive machinery
    as get_dhasa_antardhasa() and karaka_immediate_children():
        - Mahadasa (seed/root) level: _generate_mahadasa_periods(...,
          stop_at_jd=current_jd).
        - Every level below Mahadasa: _get_karaka_children_jd(), then
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

    chara_karaka_method = _validate_supported_chara_karaka_method(chara_karaka_method)

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

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )[:const._pp_count_upto_ketu]

    karakas, karaka_name_by_planet, karaka_index_by_planet = _compute_karakas(
        planet_positions, chara_karaka_method,
    )

    asc_house = planet_positions[0][1][0]

    human_life_span = sum(_dd(k, planet_positions, asc_house) for k in karakas)

    if human_life_span == 0:
        human_life_span = 1.0

    maha_label = maha_start_jd = maha_end_jd = maha_dur = None

    for maha_label, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        karakas,
        planet_positions,
        asc_house,
        human_life_span,
        show_karaka_as_pair=show_karaka_as_pair,
        karaka_name_by_planet=karaka_name_by_planet,
        karaka_index_by_planet=karaka_index_by_planet,
        stop_at_jd=current_jd,
    ):
        pass

    if maha_label is None:
        return []

    running_all = [
        [
            (maha_label,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    parent_path = (maha_label,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_karaka_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            karakas,
            planet_positions,
            asc_house,
            human_life_span,
            show_karaka_as_pair=show_karaka_as_pair,
            karaka_name_by_planet=karaka_name_by_planet,
            karaka_index_by_planet=karaka_index_by_planet,
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

    from datetime import datetime
    import random
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh, mm, ss = (15, 29, 45)
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
        print("running_all[4]", grd[4])
        new_last_lords, new_last_start, new_last_end = grd[-1]
        new_last_name = (
                '-'.join(
                utils.resource_strings[karaka + '_short_str'] + '/' + utils.PLANET_SHORT_NAMES[lord]
                          for karaka, lord in new_last_lords)
        )
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
        old_last_name = (
                '-'.join(
                utils.resource_strings[karaka + '_short_str'] + '/' + utils.PLANET_SHORT_NAMES[lord]
                          for karaka, lord in old_last_lords)
        )
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
    pvr_tests.karaka_dhasa_test()

    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place("Chennai", 13.0878, 80.2785, 5.5)

    for dli in range(
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        const.MAHA_DHASA_DEPTH.DEHA + 1,
    ):
        gd = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=dli,
            round_duration=False,
        )
        gd_sum = [sum([row[-1] for row in gd])]
        if dli == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            expected_list = gd_sum
            continue
        else:
            pvr_tests.compare_lists_within_tolerance(
                "karaka_dhasa Level Duration Test ",
                expected_list,
                gd_sum,
                pvr_tests._tolerance,
                "Level",
                dli,
            )
                