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

from jhora import utils, const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik


year_duration = const.sidereal_year


def validate_av_dasha_options(
    dhasa_method: str,
    start_rule: str,
    sequence_rule: str,
    user_defined_first: int | None = None
) -> None:
    """
    Enforces the dhasa_method/start/sequence compatibility matrix and checks user_defined_first.
    Raises ValueError with a clear message if invalid.
    """

    # 1) Method membership
    if dhasa_method not in (
        const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
        const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN,
        const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET,
    ):
        raise ValueError(f"Unsupported dhasa_method: {dhasa_method}")

    # 2) Start-rule compatibility
    allowed_starts = const.ASHTAKAVARGA_DHASA_ALLOWED_START_RULES[dhasa_method]
    if start_rule not in allowed_starts:
        raise ValueError(
            f"Invalid start_rule={start_rule} for dhasa_method={dhasa_method}. "
            f"Allowed: {sorted(allowed_starts)}"
        )

    # 3) Sequence-rule compatibility
    allowed_sequences = const.ASHTAKAVARGA_DHASA_ALLOWED_SEQUENCE_RULES[dhasa_method]
    if sequence_rule not in allowed_sequences:
        raise ValueError(
            f"Invalid sequence_rule={sequence_rule} for dhasa_method={dhasa_method}. "
            f"Allowed: {sorted(allowed_sequences)}"
        )

    # 4) User-defined starts
    if start_rule == const.ASHTAKAVARGA_DHASA_START_RULE.USER_DEFINED_PLANET:
        if dhasa_method not in (
            const.ASHTAKAVARGA_DHASA_METHOD.BAV_PLANET,
            const.ASHTAKAVARGA_DHASA_METHOD.PINDA_PLANET,
        ):
            raise ValueError("USER_DEFINED_PLANET is valid only for graha methods.")
        if user_defined_first is None or user_defined_first not in const.SUN_TO_SATURN:
            raise ValueError("USER_DEFINED_PLANET requires user_defined_first in const.SUN_TO_SATURN (0..6).")

    if start_rule == const.ASHTAKAVARGA_DHASA_START_RULE.USER_DEFINED_SIGN:
        if dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN:
            raise ValueError("USER_DEFINED_SIGN is valid only for SAV_SIGN.")
        if user_defined_first is None or user_defined_first not in range(12):
            raise ValueError("USER_DEFINED_SIGN requires user_defined_first in 0..11 (Ar..Pi).")

    # 5) Method-specific starts
    if (
        start_rule in (
            const.ASHTAKAVARGA_DHASA_START_RULE.LAGNA_SIGN,
            const.ASHTAKAVARGA_DHASA_START_RULE.JANMA_RASI,
        )
        and dhasa_method != const.ASHTAKAVARGA_DHASA_METHOD.SAV_SIGN
    ):
        raise ValueError(f"{start_rule} is only valid with SAV_SIGN.")

    # 6) Method-specific sequences
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
    Builds Buddhi Gathi base progression exactly as used by get_dhasa_bhukthi().

    Returns
    -------
    list[tuple[int, float]]
        [(planet_lord, dhasa_duration_years), ...]
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


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    max_cycles=2,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
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
    max_cycles : int
        Number of base progression cycles to iterate.
    round_duration : bool
        Round output duration years.
    dhasa_duration_type :
        Optional override. If None, drik.dhasa_year_duration() uses configured default.
    savana_year_method :
        Optional override for Savana year method.

    Returns
    -------
    list
        [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]
    """
    global year_duration

    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    max_level = dhasa_level_index

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

    d_len = len(dhasa_progression)

    if d_len == 0:
        return []

    base_order = [pl for (pl, _) in dhasa_progression]
    index_of = {pl: i for i, pl in enumerate(base_order)}
    lifespan_years = const.human_life_span_for_narayana_dhasa

    def _recurse(level, start_index, start_jd_local, duration_years, prefix, rows_out):
        """
        Recursive equal subdivision engine.

        level:
            Current tree level.
        start_index:
            Rotation start index in base_order for this node.
        prefix:
            Existing lord tuple.
        """
        sub_len = d_len

        if sub_len == 0:
            return

        sub_duration = duration_years / sub_len
        durn = round(sub_duration, dhasa_level_index + 1) if round_duration else sub_duration

        if level < max_level:
            jd_cursor = start_jd_local

            for k in range(sub_len):
                lord = base_order[(start_index + k) % sub_len]
                next_start_index = index_of[lord]

                _recurse(
                    level + 1,
                    next_start_index,
                    jd_cursor,
                    sub_duration,
                    prefix + (lord,),
                    rows_out,
                )

                jd_cursor += sub_duration * year_duration

        else:
            jd_cursor = start_jd_local

            for k in range(sub_len):
                lord = base_order[(start_index + k) % sub_len]
                row_start = utils.jd_to_gregorian(jd_cursor)
                row = [prefix + (lord,), row_start, durn]
                rows_out.append(row)
                jd_cursor += sub_duration * year_duration

    dhasa_bhukthi_info = []
    start_jd = jd_at_dob
    total_dhasa_duration = 0

    cycles_done = 0
    outer_break = False

    while cycles_done < max_cycles and not outer_break:
        for dhasa_idx in range(d_len):
            dhasa_lord, dhasa_duration = dhasa_progression[dhasa_idx]
            durn = round(dhasa_duration, dhasa_level_index + 1) if round_duration else dhasa_duration

            if dhasa_duration <= 0:
                continue

            if max_level == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                dhasa_start = utils.jd_to_gregorian(start_jd)
                row = [(dhasa_lord,), dhasa_start, durn]
                dhasa_bhukthi_info.append(row)

            else:
                rows_out = []
                start_index = index_of[dhasa_lord]

                _recurse(
                    level=2,
                    start_index=start_index,
                    start_jd_local=start_jd,
                    duration_years=dhasa_duration,
                    prefix=(dhasa_lord,),
                    rows_out=rows_out,
                )

                dhasa_bhukthi_info.extend(rows_out)

            start_jd += dhasa_duration * year_duration
            total_dhasa_duration += dhasa_duration

            if total_dhasa_duration >= lifespan_years:
                outer_break = True
                break

        cycles_done += 1

    return dhasa_bhukthi_info


def buddhigathi_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Buddhi Gathi immediate children under a parent span.

    Output rows:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    Rules:
        - Equal subdivision at every sub-level.
        - Child order is base_order rotated from parent_lord.
        - Last child end is forced to parent_end.
    """
    global year_duration

    jd_at_dob = utils.julian_day_number(dob, tob)

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

    parent_lord = path[-1]

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
        end_jd = start_jd + parent_years * year_duration
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

    d_len = len(dhasa_progression)

    if d_len == 0:
        return []

    base_order = [pl for (pl, _) in dhasa_progression]
    index_of = {pl: i for i, pl in enumerate(base_order)}

    sub_len = d_len
    sub_years = parent_years / sub_len

    start_index = index_of.get(parent_lord, 0)
    rotated = base_order[start_index:] + base_order[:start_index]

    children = []
    cursor = start_jd

    for i, child_lord in enumerate(rotated):
        if i == sub_len - 1:
            child_end = end_jd
        else:
            child_end = cursor + sub_years * year_duration

        children.append(
            [
                path + (child_lord,),
                _jd_to_tuple(cursor),
                _jd_to_tuple(child_end),
            ]
        )

        cursor = child_end

        if cursor >= end_jd:
            break

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)

    return children


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
    Buddhi Gathi runner. Narrows Mahā → ... → target depth.

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

    maha_rows = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        max_cycles=2,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )

    maha_for_utils = []

    for row in maha_rows:
        lords_any, start_t = row[0], row[1]
        maha_for_utils.append((_as_tuple_lords(lords_any), start_t))

    running_all = []

    rd = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    lords = _as_tuple_lords(rd[0])
    running = [lords, rd[1], rd[2]]
    running_all.append(running)

    if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        return running_all

    for depth in range(const.MAHA_DHASA_DEPTH.ANTARA, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = buddhigathi_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            dob=dob,
            tob=tob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years,
            months=months,
            sixty_hours=sixty_hours,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            continue

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
                dhasa_duration_type=dd,
            ),
        )

        print("new method elapsed time", time.time() - start_time)

        start_time = time.time()

        ad = get_dhasa_bhukthi(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd,
        )

        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=2,
            )
        )

        print("old method elapsed time", time.time() - start_time)

    exit()

    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.buddhi_gathi_test()