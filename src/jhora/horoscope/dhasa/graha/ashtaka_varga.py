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
    Ashtakavarga-based Dasha (documented variants only)

    Methods:
      - BAV_PLANET    -> Graha Dasha; Sun..Saturn carriers; weights = BAV totals
      - SAV_SIGN      -> Rasi Dasha; 12-sign carriers; weights = SAV per sign
      - PINDA_PLANET  -> Graha Dasha; Sun..Saturn carriers; weights = Sodhya Pinda
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, ashtakavarga


# -----------------------------------------------------------------------------
# Ashtakavarga-based Dasha documented variants only
#
# Methods:
#   - BAV_PLANET    -> Graha Dasha; Sun..Saturn carriers; weights = BAV totals
#   - SAV_SIGN      -> Rasi Dasha; 12-sign carriers; weights = SAV per sign
#   - PINDA_PLANET  -> Graha Dasha; Sun..Saturn carriers; weights = Sodhya Pinda
#
# Time conversion:
#   Period durations are internally in years.
#   Conversion years -> days uses module-level year_length_days.
#   Public entry functions update year_length_days using drik.dhasa_year_duration().
# -----------------------------------------------------------------------------

year_length_days: float = const.sidereal_year

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO drik._get_dhasa_end_jd() calls anywhere (pure
# linear arithmetic instead) -- every boundary in this module now routes
# through _bounded_end_jd().
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in every other dhasa module refactored in this
# project) to become unreliable by a real, non-trivial margin. For THIS
# dhasa (fully chart-dependent BAV/SAV/Pinda weights), worst-case
# duration reaches sub-day starting around PAD level using typical real-
# world weight ranges (~0.343 days worst case). This check is duration-
# triggered, re-evaluated fresh for every batch of children, regardless
# of level, carrier count, or individual weight values.
_SUB_DAY_DURATION_DAYS = 1.0


def validate_av_dasha_options(
    dhasa_method: str,
    start_rule: str,
    sequence_rule: str,
    user_defined_first: int | None = None,
) -> None:
    """
    Enforces the dhasa_method/start/sequence compatibility matrix and checks
    user_defined_first.

    Raises:
        ValueError:
            If any option combination is invalid.
    """

    if dhasa_method not in (
        const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
        const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN,
        const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET,
    ):
        raise ValueError(f"Unsupported dhasa_method: {dhasa_method}")

    allowed_starts = const.ASHTAKAVARGA_DHASA_ALLOWED_START_RULES[dhasa_method]
    if start_rule not in allowed_starts:
        raise ValueError(
            f"Invalid start_rule={start_rule} for dhasa_method={dhasa_method}. "
            f"Allowed: {sorted(allowed_starts)}"
        )

    allowed_sequences = const.ASHTAKAVARGA_DHASA_ALLOWED_SEQUENCE_RULES[dhasa_method]
    if sequence_rule not in allowed_sequences:
        raise ValueError(
            f"Invalid sequence_rule={sequence_rule} for dhasa_method={dhasa_method}. "
            f"Allowed: {sorted(allowed_sequences)}"
        )

    if start_rule == const.ASHTAKAVARGA_DHASA_START_RULE.USER_DEFINED_PLANET:
        if dhasa_method not in (
            const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
            const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET,
        ):
            raise ValueError("USER_DEFINED_PLANET is valid only for graha methods.")

        if user_defined_first is None or user_defined_first not in const.SUN_TO_SATURN:
            raise ValueError(
                "USER_DEFINED_PLANET requires user_defined_first in const.SUN_TO_SATURN (0..6)."
            )

    if start_rule == const.ASHTAKAVARGA_DHASA_START_RULE.USER_DEFINED_SIGN:
        if dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN:
            raise ValueError("USER_DEFINED_SIGN is valid only for SAV_SIGN.")

        if user_defined_first is None or user_defined_first not in range(12):
            raise ValueError("USER_DEFINED_SIGN requires user_defined_first in 0..11.")

    if (
        start_rule
        in (
            const.ASHTAKAVARGA_DHASA_START_RULE.LAGNA_SIGN,
            const.ASHTAKAVARGA_DHASA_START_RULE.JANMA_RASI,
        )
        and dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN
    ):
        raise ValueError(f"{start_rule} is only valid with SAV_SIGN.")

    if (
        sequence_rule == const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.FIXED_SUN_SATURN
        and dhasa_method == const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN
    ):
        raise ValueError("FIXED_SUN_SATURN is only valid for graha planet methods.")

    if (
        sequence_rule == const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.ZODIACAL_ORDER
        and dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN
    ):
        raise ValueError("ZODIACAL_ORDER is only valid for SAV_SIGN dhasa_method.")


def _house_to_planet_chart_from_planet_to_sign(planet_to_sign: dict) -> list[str]:
    """
    Builds house_to_planet_chart as 12 strings:
        ["0/1/L", "", "3", ...]
    """
    house_bins = {s: [] for s in range(12)}

    for p, s in planet_to_sign.items():
        if s is None or not (0 <= int(s) < 12):
            continue

        if isinstance(p, int) or p == "L":
            house_bins[int(s)].append(p)

    chart = []

    for s in range(12):
        ints = sorted([x for x in house_bins[s] if isinstance(x, int)])
        lagna = [x for x in house_bins[s] if x == "L"]
        tokens = [str(x) for x in ints] + lagna
        chart.append("/".join(tokens))

    return chart


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

    expected_jd = start_jd_local + duration_years * year_length_days

    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd

    return end_jd


def _build_av_carriers_weights_order(
    dob,
    tob,
    place,
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_method: str = const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
    start_rule: str = const.ASHTAKAVARGA_DHASA_START_RULE.MAX_STRENGTH,
    sequence_rule: str = const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.STRENGTH_ORDER,
    user_defined_first: int | None = None,
):
    """
    Shared builder used by both:
        - get_ashtaka_varga_dhasa_bhukthi()
        - ashtakavarga_immediate_children()

    UNCHANGED from the pre-refactor draft -- already a single, correctly-
    shared builder (see module docstring above); no bug found here.

    Returns:
        jd_birth, carriers, weights, order, planet_to_sign
    """
    validate_av_dasha_options(
        dhasa_method,
        start_rule,
        sequence_rule,
        user_defined_first,
    )

    jd_birth = utils.julian_day_number(dob, tob)

    pp = charts.divisional_chart(
        jd_birth,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )[: const._pp_count_upto_ketu]

    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(pp)
    planet_to_sign = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)

    bav, sav, pav = ashtakavarga.get_ashtaka_varga(house_to_planet_list)

    house_to_planet_chart = _house_to_planet_chart_from_planet_to_sign(planet_to_sign)

    if dhasa_method == const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET:
        carriers = list(range(7))
        weights = {p: float(sum(bav[p])) for p in carriers}

    elif dhasa_method == const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN:
        carriers = list(range(12))
        weights = {i: float(sav[i]) for i in carriers}

    elif dhasa_method == const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET:
        carriers = list(const.SUN_TO_SATURN)
        _rp, _gp, sodhya_pindas = ashtakavarga.sodhaya_pindas(
            bav,
            house_to_planet_chart,
        )
        weights = {p: float(sodhya_pindas[p]) for p in carriers}

    else:
        raise ValueError(f"Unsupported dhasa_method: {dhasa_method}")

    def _base_order(seq_rule: str, method_local: str):
        if seq_rule == const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.STRENGTH_ORDER:
            return sorted(
                carriers,
                key=lambda c: (weights.get(c, 0.0), -c),
                reverse=True,
            )

        if seq_rule == const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.ZODIACAL_ORDER:
            return sorted(carriers)

        if seq_rule == const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.FIXED_SUN_SATURN:
            if method_local not in (
                const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
                const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET,
            ):
                raise ValueError("FIXED_SUN_SATURN sequence is valid only for planet methods.")
            return [0, 1, 2, 3, 4, 5, 6]

        raise ValueError(f"Unsupported sequence_rule: {seq_rule}")

    order = _base_order(sequence_rule, dhasa_method)

    def _choose_start(s_rule: str):
        if s_rule == const.ASHTAKAVARGA_DHASA_START_RULE.MAX_STRENGTH:
            return max(order, key=lambda c: (weights.get(c, 0.0), -c))

        if s_rule == const.ASHTAKAVARGA_DHASA_START_RULE.LAGNA_SIGN:
            if dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN:
                raise ValueError("LAGNA_SIGN start is valid only for SAV_SIGN.")
            lag_sign = planet_to_sign.get("L", None)
            return lag_sign if lag_sign in order else order[0]

        if s_rule == const.ASHTAKAVARGA_DHASA_START_RULE.JANMA_RASI:
            if dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN:
                raise ValueError("JANMA_RASI start is valid only for SAV_SIGN.")
            moon_sign = planet_to_sign.get(1, None)
            return moon_sign if moon_sign in order else order[0]

        if s_rule == const.ASHTAKAVARGA_DHASA_START_RULE.USER_DEFINED_SIGN:
            if dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN:
                raise ValueError("USER_DEFINED_SIGN start is valid only for SAV_SIGN.")
            return user_defined_first if user_defined_first in order else order[0]

        if s_rule == const.ASHTAKAVARGA_DHASA_START_RULE.USER_DEFINED_PLANET:
            if dhasa_method not in (
                const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
                const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET,
            ):
                raise ValueError("USER_DEFINED_PLANET start is valid only for graha methods.")
            return user_defined_first if user_defined_first in order else order[0]

        raise ValueError(f"Unsupported start_rule: {s_rule}")

    start_item = _choose_start(start_rule)

    if start_item in order:
        idx = order.index(start_item)
        order = order[idx:] + order[:idx]

    return jd_birth, carriers, weights, order, planet_to_sign


def _split_durations_by_weights(
    parent_duration: float,
    order_local: list[int],
    weights: dict,
) -> list[float]:
    """
    Proportional duration splitter with sum conservation. UNCHANGED from
    the pre-refactor draft -- already correctly implemented (see module
    docstring above); no bug found here.
    """
    total_w = sum(max(weights.get(c, 0.0), 0.0) for c in order_local)

    if total_w <= 0:
        n = len(order_local)
        raw = [parent_duration / n for _ in range(n)]
    else:
        raw = [
            (max(weights.get(c, 0.0), 0.0) / total_w) * parent_duration
            for c in order_local
        ]

    drift = parent_duration - sum(raw)

    if raw:
        raw[-1] += drift

    return raw


def _get_av_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    order,
    weights,
    *,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Ashtakavarga Dasha (used at EVERY level,
    INCLUDING Mahadasa itself, since this dhasa has no separate cycling
    root generator -- see module docstring above).

    Rules:
        - Child order = order (the SAME fixed carrier order, computed
          ONCE by _build_av_carriers_weights_order(), reused at every
          recursion depth regardless of level).
        - PROPORTIONAL-BY-WEIGHT split via _split_durations_by_weights()
          (UNCHANGED, already correct -- see module docstring above).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - Children with zero or negative duration are SKIPPED entirely
          (no zero-width row emitted) -- matches the draft's own
          `if dur <= 0: continue` behavior exactly.
        - If the batch's smallest non-zero child duration is under
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
    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    child_durs = _split_durations_by_weights(parent_duration, order, weights)

    raw_children = [
        (c, dur) for c, dur in zip(order, child_durs) if dur > 0
    ]

    n = len(raw_children)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = min(d for _c, d in raw_children)
    smallest_child_days = smallest_child_years * year_length_days
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_included_duration = sum(d for _c, d in raw_children)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, (c, child_duration) in enumerate(raw_children):
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_duration += child_duration
            child_end_jd = parent_start_jd + parent_span * cumulative_duration / total_included_duration
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                parent_path + (c,),
                child_start_jd,
                child_duration,
                child_end_jd,
            )
        )

        cursor = child_end_jd

    return children, parent_end_jd


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
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_method: str = const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
    dhasa_level_index: int = const.MAHA_DHASA_DEPTH.ANTARA,
    start_rule: str = const.ASHTAKAVARGA_DHASA_START_RULE.MAX_STRENGTH,
    sequence_rule: str = const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.STRENGTH_ORDER,
    user_defined_first: int | None = None,
    round_duration: bool = True,
    rounding_mode: str = "decimals",
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds: bool = False,
    **kwargs,
):
    """
    Returns a flat list of rows:
        [
            [lords_tuple, (year, month, day, fractional_hour), duration_years],
            ...
        ]

    lords_tuple length = dhasa_level_index:
        level=1 -> (M,)
        level=2 -> (M, A)
        level=3 -> (M, A, P)

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    (new parameter, matching the project-wide convention already present
    in every other refactored dhasa module).

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level (the draft used pure linear
    arithmetic instead -- see module docstring above), UNLESS a batch of
    children is sub-day, in which case weighted proportional
    interpolation of the parent's real span is used instead (see
    _SUB_DAY_DURATION_DAYS above).
    """
    global year_length_days

    jd_birth = utils.julian_day_number(dob, tob)

    year_length_days = drik.dhasa_year_duration(
        jd=jd_birth,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    jd_birth, carriers, weights, order, planet_to_sign = _build_av_carriers_weights_order(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_method=dhasa_method,
        start_rule=start_rule,
        sequence_rule=sequence_rule,
        user_defined_first=user_defined_first,
    )

    lifespan_years = float(const.human_life_span_for_vimsottari_dhasa)

    results = []

    def _round_for_output(val: float) -> float:
        if not round_duration:
            return val

        if rounding_mode == "decimals":
            return round(val, dhasa_level_index)

        return val

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            results.append(
                [
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                ]
            )
        else:
            y, m, d, fh = utils.jd_to_gregorian(start_jd_local)
            results.append([lords_tuple, (y, m, d, fh), _round_for_output(duration_years)])

    def _recurse(
        depth: int,
        parent_path: tuple[int, ...],
        parent_start_jd: float,
        parent_duration_years: float,
        parent_end_jd: float,
    ):
        children, _ = _get_av_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            order,
            weights,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if depth < dhasa_level_index:
                _recurse(
                    depth + 1,
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

    if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        children, _ = _get_av_children_jd(
            tuple(),
            jd_birth,
            lifespan_years,
            place,
            order,
            weights,
        )

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            _emit_row(child_path, child_start_jd, child_duration, child_end_jd)
    else:
        _recurse(1, tuple(), jd_birth, lifespan_years, None)

    return results


def get_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_method: str = const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
    start_rule: str = const.ASHTAKAVARGA_DHASA_START_RULE.MAX_STRENGTH,
    sequence_rule: str = const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.STRENGTH_ORDER,
    user_defined_first: int | None = None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns only the immediate children under a given Ashtakavarga parent
    span.

    A thin wrapper around the shared _get_av_children_jd() engine
    (previously duplicated the boundary-walking/tiling logic independently
    from get_ashtaka_varga_dhasa_bhukthi() -- now both call the same
    engine; the underlying proportional-split math itself was already
    correctly shared via _split_durations_by_weights() in the pre-
    refactor draft).

    Output rows:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]
    """
    global year_length_days
    y,m,d,fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y,m,d); tob = (fh,0,0)
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

    jd_birth_for_year_duration = utils.julian_day_number(dob, tob)

    year_length_days = drik.dhasa_year_duration(
        jd=jd_birth_for_year_duration,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_length_days

    if end_jd <= start_jd:
        return []

    _, carriers, weights, order, planet_to_sign = _build_av_carriers_weights_order(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_method=dhasa_method,
        start_rule=start_rule,
        sequence_rule=sequence_rule,
        user_defined_first=user_defined_first,
    )

    children, _ = _get_av_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        order,
        weights,
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
    dhasa_level_index: int = const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_method: str = const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
    dhasa_level_for_base: int = 1,
    start_rule: str = const.ASHTAKAVARGA_DHASA_START_RULE.MAX_STRENGTH,
    sequence_rule: str = const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.STRENGTH_ORDER,
    user_defined_first: int | None = None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Ashtakavarga runner.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Instead it drills straight
    down this dhasa's own tree using the SAME single-recursive-rule
    machinery as get_ashtaka_varga_dhasa_bhukthi() and ashtakavarga_
    immediate_children(): _get_av_children_jd(), then _find_child_
    containing_jd(), at EVERY level INCLUDING Mahadasa itself (there is no
    separate Mahadasa-cycling generator needed here, since this dhasa has
    no cycling at all -- a single call to _get_av_children_jd() over the
    full [jd_birth, jd_birth + 120y) span covers the entire Mahadasa
    level in one shot). Stays in JD-float space throughout; only the
    final returned rows are converted to Gregorian tuples.

    NOTE: dhasa_level_for_base is accepted for backward compatibility but
    is NOT used anywhere in this function -- it was already a dead
    parameter in the pre-refactor draft (see module docstring above).

    Returns:
        [
            [(l1,),       start1, end1],
            [(l1,l2),     start2, end2],
            ...
            [(l1,...,lN), startN, endN],
        ]
    """
    global year_length_days

    year_length_days = drik.dhasa_year_duration(
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

    jd_birth, carriers, weights, order, planet_to_sign = _build_av_carriers_weights_order(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_method=dhasa_method,
        start_rule=start_rule,
        sequence_rule=sequence_rule,
        user_defined_first=user_defined_first,
    )

    lifespan_years = float(const.human_life_span_for_vimsottari_dhasa)

    maha_children, _ = _get_av_children_jd(
        tuple(),
        jd_birth,
        lifespan_years,
        place,
        order,
        weights,
    )

    found = _find_child_containing_jd(maha_children, current_jd)

    if found is None:
        return []

    parent_path, parent_start_jd, parent_duration_years, parent_end_jd = found

    running_all = [
        [
            parent_path,
            utils.jd_to_gregorian(parent_start_jd),
            utils.jd_to_gregorian(parent_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for _depth in range(2, target_depth + 1):
        children, _ = _get_av_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            order,
            weights,
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


# ---------------------------------------------------------------------
# Example usage / duration-method test
# ---------------------------------------------------------------------
if __name__ == "__main__":
    utils.set_language("en")

    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)

    place = drik.Place("Chennai,IN", 13.0389, 80.2619, +5.5)

    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

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

    _method = const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("-" * 80)

        # ---- NEW method: only the last (Deha) row -------------------------
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=DLI,
                dhasa_method=_method,
                dhasa_duration_type=dd,
            )
        print("running_all[4]", grd[4] if len(grd) > 4 else grd[-1])
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
            dhasa_method=_method,
            dhasa_duration_type=dd,
            return_exact_bounds=True,
        )
        deha_groups = utils._group_ancestors_from_leaves(full_tree, DLI)
        old_last_lords, old_start_jd, old_end_jd = utils._find_containing_group(deha_groups, current_jd)
        old_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord]  for lord in old_last_lords])
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
