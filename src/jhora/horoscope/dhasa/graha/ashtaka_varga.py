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

from jhora import const, utils
from jhora.panchanga import drik
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
    Proportional duration splitter with sum conservation.
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


def get_ashtaka_varga_dhasa_bhukthi(
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

    results = []
    jd_tracker = jd_birth
    lifespan_years = float(const.human_life_span_for_vimsottari_dhasa)

    def _round_for_output(val: float) -> float:
        if not round_duration:
            return val

        if rounding_mode == "decimals":
            return round(val, dhasa_level_index)

        return val

    def _recurse(depth: int, parent_duration: float, lords_stack: tuple[int, ...]):
        nonlocal jd_tracker

        child_durs = _split_durations_by_weights(parent_duration, order, weights)

        for c, dur in zip(order, child_durs):
            if dur <= 0:
                continue

            next_stack = lords_stack + (c,)

            if depth == dhasa_level_index:
                y, m, d, fh = utils.jd_to_gregorian(jd_tracker)
                results.append([next_stack, (y, m, d, fh), _round_for_output(dur)])

                # Advance by unrounded duration to preserve continuity.
                jd_tracker += dur * year_length_days
            else:
                _recurse(depth + 1, dur, next_stack)

    _recurse(1, lifespan_years, tuple())

    return results


def ashtakavarga_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    dob,
    tob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_method: str = const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
    start_rule: str = const.ASHTAKAVARGA_DHASA_START_RULE.MAX_STRENGTH,
    sequence_rule: str = const.ASHTAKAVARGA_DHASA_SEQUENCE_RULE.STRENGTH_ORDER,
    user_defined_first: int | None = None,
):
    """
    Returns only the immediate children under a given Ashtakavarga parent span.

    Output rows:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    Notes:
        Uses module-level year_length_days. Public callers should set it first.
    """

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
        raise ValueError("Provide exactly one of parent_duration or parent_end")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_length_days
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

    child_years_list = _split_durations_by_weights(parent_years, order, weights)

    children = []
    jd_cursor = start_jd

    for idx, (c, dur_y) in enumerate(zip(order, child_years_list)):
        if idx == len(order) - 1:
            child_end_jd = end_jd
        else:
            child_end_jd = jd_cursor + dur_y * year_length_days

        children.append(
            [
                path + (c,),
                _jd_to_tuple(jd_cursor),
                _jd_to_tuple(child_end_jd),
            ]
        )

        jd_cursor = child_end_jd

        if jd_cursor >= end_jd:
            break

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)

    return children


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

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    def _tuple_to_jd(t):
        y1, m1, d1, fh1 = t
        return utils.julian_day_number(drik.Date(y1, m1, d1), (fh1, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        filtered = [
            r for r in children_rows
            if not _is_zero_length(r[1], r[2], eps_seconds=eps_seconds)
        ]

        if not filtered:
            return []

        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))

        proj = []
        prev = None

        for lords, st, _en in filtered:
            sjd = _tuple_to_jd(st)

            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd

        proj.append((proj[-1][0], parent_end_tuple))

        return proj

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = const.MAHA_DHASA_DEPTH.DEHA

    target_depth = max(
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        min(const.MAHA_DHASA_DEPTH.DEHA, target_depth),
    )

    maha_rows = get_ashtaka_varga_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_method=dhasa_method,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        start_rule=start_rule,
        sequence_rule=sequence_rule,
        user_defined_first=user_defined_first,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )

    maha_for_utils = []

    for row in maha_rows:
        lords_any, start_t, *_ = row
        maha_for_utils.append((_as_tuple_lords(lords_any), start_t))

    rd = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)

    lords = _as_tuple_lords(rd[0])
    running = [lords, rd[1], rd[2]]
    running_all = [running]

    if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        return running_all

    for depth in range(const.MAHA_DHASA_DEPTH.ANTARA, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = ashtakavarga_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            dob=dob,
            tob=tob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_method=dhasa_method,
            start_rule=start_rule,
            sequence_rule=sequence_rule,
            user_defined_first=user_defined_first,
        )

        if not children:
            raise ValueError("No children generated for the Ashtakavarga parent period.")

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)

        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rd_k = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            lords_k = _as_tuple_lords(rd_k[0])
            running = [lords_k, rd_k[1], rd_k[2]]

        running_all.append(running)

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

    from datetime import datetime
    import time

    current_date_str, current_time_str = datetime.now().strftime("%Y,%m,%d;%H:%M:%S").split(";")

    y, m, d = map(int, current_date_str.split(","))
    hh, mm, ss = map(int, current_time_str.split(":"))
    fh = hh + mm / 60 + ss / 3600

    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))

    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    _method = const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET

    for dd in const.DHASA_YEAR_DURATION:
        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("-" * 80)

        start_time = time.time()

        print(
            "Deha:",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_method=_method,
                dhasa_duration_type=dd,
            ),
        )

        print("new method elapsed time", time.time() - start_time)

        start_time = time.time()

        ad = get_ashtaka_varga_dhasa_bhukthi(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=_method,
            dhasa_duration_type=dd,
        )

        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
            )
        )

        print("old method elapsed time", time.time() - start_time)

    exit()