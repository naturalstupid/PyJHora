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
    Naisargika Dhasa

    A "natural" (temperament-based) rasi dhasa in which the Mahadasa
    sequence and durations are fixed for every chart, independent of the
    birth details:

        Moon (1 yr) -> Mars (2) -> Mercury (9) -> Venus (20) -> Jupiter
        (18) -> Sun (20) -> Saturn (50) -> Lagna (12)

    (dhasa_adhipathi_dict). This order and the Lagna as an 8th Mahadasa
    (in addition to the seven planets) both match real JHora output.

    Antardasa (Sanjay Rath, citing Kalyan Varma's Saravali, Antardasa-
    phala-adhyaya, Ch.42):
        - Candidates are every planet other than the Mahadasa lord itself
          (the dasa lord does not receive its own antardasa).
        - Candidates are visited in three groups, relative to the
          Mahadasa lord's own sign: kendra (1st/4th/7th/10th houses),
          then panapara (2nd/5th/8th/11th houses), then apoklima
          (3rd/6th/9th/12th houses).
        - Within kendra and panapara, the visiting order is by
          descending house number (10th->7th->4th->1st for kendra;
          11th->8th->5th->2nd for panapara). Apoklima is visited in the
          order 9th->12th->6th->3rd.
        - When two or more candidates share the same house, all of them
          furnish their own antardasa (per Satyacharya, Saravali 42-4,
          rather than Kalyan Varma's alternative of only the strongest
          furnishing it), ordered by seniority in the fixed Naisargika
          Mahadasa sequence (Moon>Mars>Merc>Venus>Jupiter>Sun>Saturn>
          Lagna; later = more senior = listed first).
        - Each antardasa's duration is weighted by Kalyan Varma's
          aspect-strength table, keyed by the candidate's house offset
          from the Mahadasa lord's own sign:
              conjoining (same house):        weight 1/2
              2nd, 3rd, 6th, 10th, 11th, 12th: weight 1
              4th, 8th (chaturasra):          weight 1/4
              5th, 9th (trikona):             weight 1/3
              7th (full aspect):              weight 1/7
          A candidate's antardasa duration = its own weight, divided by
          the sum of all candidates' weights in that Mahadasa, multiplied
          by the Mahadasa's own duration.

        The same order and weight-table are applied recursively at every
        level below the antardasa (Pratyantardasa, Sookshma, Prana-
        antardasa, Deha), treating each level's own lord as the
        reference sign for its children.

        antardhasa_option1 (drop 3rd/10th house candidates) and
        antardhasa_option2 (drop 2nd/6th/11th/12th house candidates) are
        optional legacy exclusions retained for backward compatibility;
        both default to False.

        Every dasha boundary (Mahadasa and every level below it) is
        computed via drik._get_dhasa_end_jd(), through the _bounded_end_jd()
        wrapper, which falls back to plain linear (duration * year_duration)
        arithmetic if drik._get_dhasa_end_jd() returns a result more than
        _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate. When a
        batch of children's smallest duration drops below
        _SUB_DAY_DURATION_DAYS, that batch's boundaries are instead computed
        by proportional interpolation of the parent's own [start_jd, end_jd]
        span, since drik._get_dhasa_end_jd()'s underlying solar-transit
        search is not reliable at sub-day granularity.
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
# proportional interpolation of the parent's own real span instead (see
# _get_naisargika_children()).
_SUB_DAY_DURATION_DAYS = 1.0

dhasa_adhipathi_dict = {1: 1, 2: 2, 3: 9, 5: 20, 4: 18, 0: 20, 6: 50, 'L': 12}

# Naisargika Mahadasa sequence, in order. Used as the seniority reference
# when breaking ties between antardasa candidates that share the same
# house (see _bhukthis_and_weights_for()). Preserves dhasa_adhipathi_dict's
# own insertion order.
_MD_ORDER_SEQ = list(dhasa_adhipathi_dict.keys())


def _md_seniority(lord):
    """Position of `lord` in the fixed Naisargika Mahadasa sequence (0=Moon
    .. 7=Lagna). Higher = more senior; used only to break same-house
    antardasa ties."""
    return _MD_ORDER_SEQ.index(lord)


# Antardasa house-offset traversal order: kendra, then panapara, then
# apoklima.
#     kendra   (offsets 0,3,6,9  = houses  1st, 4th, 7th,10th): descending
#     panapara (offsets 1,4,7,10 = houses  2nd, 5th, 8th,11th): descending
#     apoklima (offsets 2,5,8,11 = houses  3rd, 6th, 9th,12th): visited in
#              the order 9th->12th->6th->3rd (offsets 8,11,5,2)
_OFFSET_TRAVERSAL_ORDER = [9, 6, 3, 0, 10, 7, 4, 1, 8, 11, 5, 2]

# Kalyan Varma's (Saravali, Ch.42) aspect-strength weight table, keyed by
# house-offset from the Mahadasa lord's own sign.
_WEIGHT_BY_OFFSET = {
    0: 1 / 2,   # conjoining (same house as the dasa lord)
    1: 1.0,     # 2nd house
    2: 1.0,     # 3rd house
    3: 1 / 4,   # 4th house (chaturasra)
    4: 1 / 3,   # 5th house (trikona)
    5: 1.0,     # 6th house
    6: 1 / 7,   # 7th house (full aspect)
    7: 1 / 4,   # 8th house (chaturasra)
    8: 1 / 3,   # 9th house (trikona)
    9: 1.0,     # 10th house
    10: 1.0,    # 11th house
    11: 1.0,    # 12th house
}

# Legacy antardasa exclusion options, retained for backward compatibility.
# Both default to False.
_bhukthi_exempt_list_1 = [2, 9]         # 3rd/10th house offsets
_bhukthi_exempt_list_2 = [1, 5, 10, 11]  # 2nd/6th/11th/12th house offsets


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


def _bhukthis_and_weights_for(
    parent_lord,
    planet_positions,
    h_to_p,
    *,
    mahadhasa_lord_has_no_antardhasa=True,
    antardhasa_option1=False,
    antardhasa_option2=False,
):
    """
    Returns the ordered list of (child_lord, weight) antardasa candidates
    for `parent_lord`, per Kalyan Varma's kendra->panapara->apoklima order
    and aspect-strength weight table.
    """
    lord_house = (
        planet_positions[parent_lord + 1][1][0]
        if parent_lord != const._ascendant_symbol
        else planet_positions[0][1][0]
    )

    offset_order = list(_OFFSET_TRAVERSAL_ORDER)
    if antardhasa_option1:
        offset_order = [o for o in offset_order if o not in _bhukthi_exempt_list_1]
    if antardhasa_option2:
        offset_order = [o for o in offset_order if o not in _bhukthi_exempt_list_2]

    ordered = []
    for offset in offset_order:
        house_index = (offset + lord_house) % 12
        occupants_str = h_to_p[house_index]
        if not occupants_str:
            continue

        pids = []
        for label in occupants_str.split('/'):
            if label in ('L', '7', '8'):
                continue
            try:
                pids.append(int(label))
            except ValueError:
                continue

        # Same-house ties: more senior (later) in the Naisargika Mahadasa
        # sequence goes first.
        pids.sort(key=_md_seniority, reverse=True)

        weight = _WEIGHT_BY_OFFSET[offset]
        for pid in pids:
            ordered.append((pid, weight))

    if mahadhasa_lord_has_no_antardhasa and parent_lord != const._ascendant_symbol:
        ordered = [(pid, w) for pid, w in ordered if pid != parent_lord]

    return ordered


def _get_naisargika_children(
    parent_path,
    parent_lord,
    parent_start_jd,
    parent_duration_years,
    place,
    planet_positions,
    h_to_p,
    *,
    parent_end_jd=None,
    mahadhasa_lord_has_no_antardhasa=True,
    antardhasa_option1=False,
    antardhasa_option2=False,
):
    """
    Single children-engine for Naisargika Dasa antardasa and every level
    below it, applying the same kendra/panapara/apoklima order and
    Kalyan Varma weight table recursively at each level.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD
    """
    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration_years, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    candidates = _bhukthis_and_weights_for(
        parent_lord,
        planet_positions,
        h_to_p,
        mahadhasa_lord_has_no_antardhasa=mahadhasa_lord_has_no_antardhasa,
        antardhasa_option1=antardhasa_option1,
        antardhasa_option2=antardhasa_option2,
    )

    if not candidates:
        return [], parent_end_jd

    total_weight = sum(w for _p, w in candidates)
    n = len(candidates)

    child_durations = [parent_duration_years * w / total_weight for _p, w in candidates]

    # Sub-day fallback: interpolate proportionally instead of calling
    # drik._get_dhasa_end_jd() per child (see _SUB_DAY_DURATION_DAYS above).
    smallest_child_days = min(child_durations) * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(child_durations)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, ((child_lord, _weight), child_duration) in enumerate(zip(candidates, child_durations)):
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


def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1, chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    mahadhasa_lord_has_no_antardhasa=True,
    antardhasa_option1=False, antardhasa_option2=False,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Provides Naisargika dhasa-bhukthi for a given date.

    @param antardhasa_option1 = True: 3rd/10th house has no antardhasa
        (legacy option, not part of the standard antardasa rule)
    @param antardhasa_option2 = True: 2nd/6th/11th/12th house has no
        antardhasa (legacy option, not part of the standard antardasa
        rule)

    Returns:
        dhasa_info rows:
            [ [lords_tuple, start_tuple, duration_years], ... ]
        If return_exact_bounds=True, each row is instead:
            [ lords_tuple, start_jd_float, end_jd_float, duration_years ]
    """
    global year_duration

    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    start_jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=start_jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        start_jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
    )[:const._pp_count_upto_saturn]  # Ignore Rahu onwards

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    dhasa_lords = list(dhasa_adhipathi_dict.keys())

    dhasa_info = []

    def _emit_row(lords_tuple, start_jd_local, duration_years_local, end_jd_local):
        if return_exact_bounds:
            dhasa_info.append(
                [lords_tuple, start_jd_local, end_jd_local, duration_years_local]
            )
        else:
            durn = (
                round(duration_years_local, dhasa_level_index + 1)
                if round_duration
                else duration_years_local
            )
            dhasa_info.append(
                [lords_tuple, utils.jd_to_gregorian(start_jd_local), durn]
            )

    def _recurse(level, parent_path, parent_lord, parent_start_jd, parent_duration_years, parent_end_jd):
        children, _ = _get_naisargika_children(
            parent_path, parent_lord, parent_start_jd, parent_duration_years,
            place, planet_positions, h_to_p,
            parent_end_jd=parent_end_jd,
            mahadhasa_lord_has_no_antardhasa=mahadhasa_lord_has_no_antardhasa,
            antardhasa_option1=antardhasa_option1,
            antardhasa_option2=antardhasa_option2,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            child_lord = child_path[-1]
            if level < dhasa_level_index:
                _recurse(level + 1, child_path, child_lord, child_start_jd, child_duration, child_end_jd)
            else:
                _emit_row(child_path, child_start_jd, child_duration, child_end_jd)

    cursor_jd = start_jd
    for dhasa_lord in dhasa_lords:
        maha_dur = dhasa_adhipathi_dict[dhasa_lord]
        maha_start_jd = cursor_jd
        maha_end_jd = _bounded_end_jd(maha_start_jd, maha_dur, place)

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row((dhasa_lord,), maha_start_jd, maha_dur, maha_end_jd)
        else:
            _recurse(
                const.MAHA_DHASA_DEPTH.ANTARA,
                (dhasa_lord,), dhasa_lord,
                maha_start_jd, maha_dur, maha_end_jd,
            )

        cursor_jd = maha_end_jd

    return dhasa_info


def get_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (optional)
    parent_end=None,             # (Y, M, D, fractional_hour) (optional)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    mahadhasa_lord_has_no_antardhasa: bool = True,
    antardhasa_option1: bool = False,
    antardhasa_option2: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Naisargika -- return ONLY the immediate (p -> p+1) children under the
    given parent span, via the shared _get_naisargika_children() engine.

    Returns:
        [ [lords_tuple_with_child, child_start_tuple, child_end_tuple], ... ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, (int, str)):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int/str or non-empty tuple/list")
    parent_lord = path[-1]

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
    )[:const._pp_count_upto_saturn]

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)

    children, _ = _get_naisargika_children(
        path, parent_lord, start_jd, parent_years,
        place, planet_positions, h_to_p,
        parent_end_jd=end_jd,
        mahadhasa_lord_has_no_antardhasa=mahadhasa_lord_has_no_antardhasa,
        antardhasa_option1=antardhasa_option1,
        antardhasa_option2=antardhasa_option2,
    )

    return [
        [child_path, _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)]
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
    mahadhasa_lord_has_no_antardhasa: bool = True,
    antardhasa_option1: bool = False,
    antardhasa_option2: bool = False,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Naisargika -- narrow Maha -> ... -> target depth and return the full
    running ladder:
        [
            [(l1,),               start1, end1],
            [(l1,l2),             start2, end2],
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

    maha_lord = None
    maha_start_jd = maha_end_jd = None
    cursor_jd = jd_at_dob
    for dhasa_lord in dhasa_adhipathi_dict.keys():
        maha_dur = dhasa_adhipathi_dict[dhasa_lord]
        s = cursor_jd
        e = _bounded_end_jd(s, maha_dur, place)
        if s <= current_jd < e:
            maha_lord, maha_start_jd, maha_end_jd, maha_years = dhasa_lord, s, e, maha_dur
            break
        cursor_jd = e
    else:
        # current_jd at/after the final Mahadasa's end -- clamp to the last one
        maha_lord = dhasa_lord
        maha_start_jd, maha_end_jd, maha_years = s, e, maha_dur

    running_all = [
        [(maha_lord,), utils.jd_to_gregorian(maha_start_jd), utils.jd_to_gregorian(maha_end_jd)]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
    )[:const._pp_count_upto_saturn]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)

    parent_path = (maha_lord,)
    parent_lord = maha_lord
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_years

    for _depth in range(2, target_depth + 1):
        children, _ = _get_naisargika_children(
            parent_path, parent_lord, parent_start_jd, parent_duration_years,
            place, planet_positions, h_to_p,
            parent_end_jd=parent_end_jd,
            mahadhasa_lord_has_no_antardhasa=mahadhasa_lord_has_no_antardhasa,
            antardhasa_option1=antardhasa_option1,
            antardhasa_option2=antardhasa_option2,
        )

        found = None
        for child in children:
            _, s, _, e = child
            if s <= current_jd < e:
                found = child
                break
        if found is None and children:
            found = children[-1]

        if found is None:
            running_all.append(
                [parent_path + (parent_path[-1],), utils.jd_to_gregorian(parent_start_jd),
                 utils.jd_to_gregorian(parent_end_jd)]
            )
            break

        child_path, child_start_jd, child_duration_years, child_end_jd = found
        running_all.append(
            [child_path, utils.jd_to_gregorian(child_start_jd), utils.jd_to_gregorian(child_end_jd)]
        )

        parent_path = child_path
        parent_lord = child_path[-1]
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
    import time
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600

    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    print(check_date)

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
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.naisargika_test()
