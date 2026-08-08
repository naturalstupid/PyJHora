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
"""
"""
Calculates Yoga Vimsottari
"""
from collections import OrderedDict as Dict

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts


year_duration = const.sidereal_year

vimsottari_dict = {
    8: [(3, 12, 21), 7],
    5: [(4, 13, 22), 20],
    0: [(5, 14, 23), 6],
    1: [(6, 15, 24), 10],
    2: [(7, 16, 25), 7],
    7: [(8, 17, 26), 18],
    4: [(9, 18, 27), 16],
    6: [(1, 10, 19), 19],
    3: [(2, 11, 20), 17],
}

human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa


def _extract_years(val):
    """Allow both numeric or [yoga_list, years]/(yoga_list, years)."""
    if isinstance(val, (list, tuple)) and len(val) >= 2 and isinstance(val[1], (int, float)):
        return float(val[1])

    return float(val)


def _scale_entry(val, factor):
    """Scale only the years while preserving the original container type."""
    if isinstance(val, (list, tuple)) and len(val) >= 2 and isinstance(val[1], (int, float)):
        y = round(float(val[1]) * factor, 6)

        if isinstance(val, tuple):
            return (val[0], y)

        return [val[0], y]

    if isinstance(val, (int, float)):
        return round(float(val) * factor, 6)

    return val


def vimsottari_adhipathi(yoga_index):
    for key, value in vimsottari_dict.items():
        yoga_list, durn = value

        if yoga_index in yoga_list:
            return key, durn

    raise ValueError("No Yoga Vimshottari adhipathi found for yoga_index={}".format(yoga_index))


def vimsottari_next_adhipati(lord, direction=1):
    """Returns next lord after lord in the Vimsottari adhipati list."""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + direction) % len(const.vimsottari_adhipati_list)

    return const.vimsottari_adhipati_list[next_index]


def vimsottari_dasha_start_date(jd, place):
    """Returns the start JD of the Mahadasha occurring on or before jd."""
    _, _, _, birth_time_hrs = utils.jd_to_gregorian(jd)

    yoga_info = drik.yogam(jd, place)

    y_frac = utils.get_fraction(
        yoga_info[1],
        yoga_info[2],
        birth_time_hrs,
    )

    lord, res = vimsottari_adhipathi(yoga_info[0])

    start_jd = drik._get_dhasa_start_jd(
        jd,
        place,
        fraction_elapsed=(1.0 - y_frac),
        total_dasa_years=res,
    )

    return [lord, start_jd]


def vimsottari_mahadasa(jdut1, place):
    """List all Mahadashas and their start JDs."""
    lord, start_date = vimsottari_dasha_start_date(jdut1, place)

    retval = Dict()

    for _ in range(len(const.vimsottari_adhipati_list)):
        retval[lord] = start_date

        lord_duration = _extract_years(vimsottari_dict[lord])

        start_date = drik._get_dhasa_end_jd(
            start_jd=start_date,
            place=place,
            total_dasa_years=lord_duration,
        )

        lord = vimsottari_next_adhipati(lord)

    return retval


def _vimsottari_bhukti(maha_lord, start_date, place, antardhasa_option=1):
    """Compute all Bhuktis of a given Mahadasha lord and its start date."""
    lord = maha_lord

    if antardhasa_option in [3, 4]:
        lord = vimsottari_next_adhipati(lord, direction=1)
    elif antardhasa_option in [5, 6]:
        lord = vimsottari_next_adhipati(lord, direction=-1)

    dirn = 1 if antardhasa_option in [1, 3, 5] else -1

    dhasa_lord_duration = _extract_years(vimsottari_dict[maha_lord])

    retval = Dict()

    for _ in range(len(vimsottari_dict)):
        retval[lord] = start_date

        bhukthi_duration = _extract_years(vimsottari_dict[lord])

        factor = (
            bhukthi_duration
            * dhasa_lord_duration
            / human_life_span_for_vimsottari_dhasa
        )

        start_date = drik._get_dhasa_end_jd(
            start_jd=start_date,
            place=place,
            total_dasa_years=factor,
        )

        lord = vimsottari_next_adhipati(lord, dirn)

    return retval


def _vimsottari_antara(maha_lord, bhukti_lord, start_date, place):
    """Compute all Antaradasas from a given Bhukti start date."""
    lord = bhukti_lord

    retval = Dict()

    for _ in range(len(const.vimsottari_adhipati_list)):
        retval[lord] = start_date

        factor = _extract_years(vimsottari_dict[lord])
        factor = factor * (
            _extract_years(vimsottari_dict[maha_lord])
            / human_life_span_for_vimsottari_dhasa
        )
        factor = factor * (
            _extract_years(vimsottari_dict[bhukti_lord])
            / human_life_span_for_vimsottari_dhasa
        )

        start_date = drik._get_dhasa_end_jd(
            start_jd=start_date,
            place=place,
            total_dasa_years=factor,
        )

        lord = vimsottari_next_adhipati(lord)

    return retval


def _where_occurs(jd, some_dict):
    """Returns last key such that some_dict[key] < jd."""
    for key in reversed(list(some_dict.keys())):
        if some_dict[key] < jd:
            return key

    return next(iter(some_dict.keys()))


def compute_vimsottari_antara_from(jd, mahadashas, place):
    """Returns Antaradasha within which given jd falls."""
    i = _where_occurs(jd, mahadashas)

    bhuktis = _vimsottari_bhukti(
        i,
        mahadashas[i],
        place,
    )

    j = _where_occurs(jd, bhuktis)

    antara = _vimsottari_antara(
        i,
        j,
        bhuktis[j],
        place,
    )

    return i, j, antara


def get_dhasa_bhukthi(
    jd,
    place,
    use_tribhagi_variation=False,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Yoga-based Vimshottari dasha.

    This is Vimshottari keyed by Yogam instead of Nakshatra.

    Return format:
        vim_bal, [
            [lords_tuple, start_tuple, duration_years],
            ...
        ]

    End JD is used internally only to calculate the next start JD.
    """
    global human_life_span_for_vimsottari_dhasa
    global vimsottari_dict
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6.")

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    orig_H = human_life_span_for_vimsottari_dhasa
    orig_dict = vimsottari_dict.copy()

    try:
        dhasa_cycles = 1

        if use_tribhagi_variation:
            trib = 1.0 / 3.0
            human_life_span_for_vimsottari_dhasa = orig_H * trib
            vimsottari_dict = {
                k: _scale_entry(v, trib)
                for k, v in orig_dict.items()
            }
            dhasa_cycles = int(dhasa_cycles / trib)

        H = float(human_life_span_for_vimsottari_dhasa)

        dashas = vimsottari_mahadasa(jd, place)

        dl = list(dashas.values())
        de = dl[1] if len(dl) >= 2 else dl[0]

        y, m, d, _ = utils.jd_to_gregorian(jd)
        p_date1 = drik.Date(y, m, d)

        y, m, d, _ = utils.jd_to_gregorian(de)
        p_date2 = drik.Date(y, m, d)

        vim_bal = utils.panchanga_date_diff(p_date1, p_date2)

        dhasa_bhukthi = []

        def _next_jd_by_dhasa_years(start_jd_local, duration_years):
            return drik._get_dhasa_end_jd(
                start_jd=start_jd_local,
                place=place,
                total_dasa_years=duration_years,
            )

        def _emit_row(lords_tuple, start_jd_local, duration_years):
            dhasa_bhukthi.append(
                [
                    lords_tuple,
                    utils.jd_to_gregorian(start_jd_local),
                    float(duration_years),
                ]
            )

        def _start_and_dir(parent_lord):
            lord = parent_lord

            if antardhasa_option in [3, 4]:
                lord = vimsottari_next_adhipati(lord, direction=1)
            elif antardhasa_option in [5, 6]:
                lord = vimsottari_next_adhipati(lord, direction=-1)

            dirn = 1 if antardhasa_option in [1, 3, 5] else -1

            return lord, dirn

        def _children_planetary(parent_lord, parent_start_jd, parent_end_jd, parent_years):
            """
            Yields:
                child_lord, child_start_jd, child_end_jd, child_duration_years

            End JD is used internally only to calculate next start.
            """
            start_lord, dirn = _start_and_dir(parent_lord)

            jd_cursor = parent_start_jd
            lord = start_lord

            for idx in range(len(const.vimsottari_adhipati_list)):
                Y = _extract_years(vimsottari_dict[lord])
                dur_yrs = parent_years * (Y / H)

                child_start_jd = jd_cursor

                if idx == len(const.vimsottari_adhipati_list) - 1:
                    child_end_jd = parent_end_jd
                else:
                    child_end_jd = _next_jd_by_dhasa_years(
                        child_start_jd,
                        dur_yrs,
                    )

                yield lord, child_start_jd, child_end_jd, dur_yrs

                jd_cursor = child_end_jd

                if jd_cursor >= parent_end_jd:
                    break

                lord = vimsottari_next_adhipati(lord, direction=dirn)

        def _current_cycle_items(md_items_base, cycle_start_jd):
            """
            Builds one cycle of Mahadasha start JDs using _get_dhasa_end_jd.
            """
            items = []
            cursor = cycle_start_jd

            for lord, _old_start in md_items_base:
                items.append((lord, cursor))

                cursor = _next_jd_by_dhasa_years(
                    cursor,
                    _extract_years(vimsottari_dict[lord]),
                )

            return items, cursor

        md_items_base = list(dashas.items())
        cycle_start_jd = md_items_base[0][1]

        for _ in range(dhasa_cycles):
            md_items, next_cycle_start_jd = _current_cycle_items(
                md_items_base,
                cycle_start_jd,
            )

            for idx, (md_lord, md_start_jd) in enumerate(md_items):
                if idx < len(md_items) - 1:
                    md_end_jd = md_items[idx + 1][1]
                else:
                    md_end_jd = next_cycle_start_jd

                md_years = (md_end_jd - md_start_jd) / year_duration

                if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                    _emit_row(
                        (md_lord,),
                        md_start_jd,
                        md_years,
                    )
                    continue

                if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                    for blord, bstart, bend, byears in _children_planetary(
                        md_lord,
                        md_start_jd,
                        md_end_jd,
                        md_years,
                    ):
                        _emit_row(
                            (md_lord, blord),
                            bstart,
                            byears,
                        )
                    continue

                if dhasa_level_index == const.MAHA_DHASA_DEPTH.PRATYANTARA:
                    for blord, bstart, bend, byears in _children_planetary(
                        md_lord,
                        md_start_jd,
                        md_end_jd,
                        md_years,
                    ):
                        for alord, astart, aend, ayears in _children_planetary(
                            blord,
                            bstart,
                            bend,
                            byears,
                        ):
                            _emit_row(
                                (md_lord, blord, alord),
                                astart,
                                ayears,
                            )
                    continue

                def _recurse(
                    level,
                    parent_lord,
                    parent_start_jd,
                    parent_end_jd,
                    parent_years,
                    prefix,
                ):
                    if level == dhasa_level_index:
                        _emit_row(
                            prefix,
                            parent_start_jd,
                            parent_years,
                        )
                        return

                    for clord, cstart, cend, cyears in _children_planetary(
                        parent_lord,
                        parent_start_jd,
                        parent_end_jd,
                        parent_years,
                    ):
                        _recurse(
                            level + 1,
                            clord,
                            cstart,
                            cend,
                            cyears,
                            prefix + (clord,),
                        )

                _recurse(
                    level=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
                    parent_lord=md_lord,
                    parent_start_jd=md_start_jd,
                    parent_end_jd=md_end_jd,
                    parent_years=md_years,
                    prefix=(md_lord,),
                )

            cycle_start_jd = next_cycle_start_jd

        return vim_bal, dhasa_bhukthi

    finally:
        human_life_span_for_vimsottari_dhasa = orig_H
        vimsottari_dict = orig_dict


def _tuple_to_jd(t):
    y, m, d, fh = t
    return utils.julian_day_number(
        drik.Date(y, m, d),
        (fh, 0, 0),
    )


def _jd_to_tuple(jd_val):
    return utils.jd_to_gregorian(jd_val)


def yoga_vimsottari_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    jd_at_dob=None,
    place=None,
    antardhasa_option=1,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Yoga Vimshottari immediate children under the given parent span.

    Returns:
        [
            [lords_tuple_with_child, child_start_tuple, child_end_tuple],
            ...
        ]

    This function intentionally returns start and end tuples because
    the running-dhasa navigator needs parent-child boundaries.
    """
    global year_duration

    if jd_at_dob is not None and place is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

    if place is None:
        raise ValueError("place is required for exact Yoga Vimshottari child boundary calculation.")

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")

    parent_lord = path[-1]

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end.")

    if parent_end is None:
        parent_years = float(parent_duration)

        end_jd = drik._get_dhasa_end_jd(
            start_jd=start_jd,
            place=place,
            total_dasa_years=parent_years,
        )
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    def _start_and_dir(parent_lord_local):
        lord = parent_lord_local

        if antardhasa_option in [3, 4]:
            lord = vimsottari_next_adhipati(lord, direction=1)
        elif antardhasa_option in [5, 6]:
            lord = vimsottari_next_adhipati(lord, direction=-1)

        dirn = 1 if antardhasa_option in [1, 3, 5] else -1

        return lord, dirn

    start_lord, dirn = _start_and_dir(parent_lord)

    lord = start_lord
    H = float(human_life_span_for_vimsottari_dhasa)
    jd_cursor = start_jd
    children = []

    for idx in range(len(const.vimsottari_adhipati_list)):
        Y = _extract_years(vimsottari_dict[lord])
        child_years = parent_years * (Y / H)

        child_start = jd_cursor

        if idx == len(const.vimsottari_adhipati_list) - 1:
            child_end = end_jd
        else:
            child_end = drik._get_dhasa_end_jd(
                start_jd=child_start,
                place=place,
                total_dasa_years=child_years,
            )

        children.append(
            [
                path + (lord,),
                _jd_to_tuple(child_start),
                _jd_to_tuple(child_end),
            ]
        )

        jd_cursor = child_end

        if jd_cursor >= end_jd:
            break

        lord = vimsottari_next_adhipati(lord, direction=dirn)

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)

    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    antardhasa_option=1,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Yoga Vimshottari runner.

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

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        filtered = [
            r
            for r in children_rows
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

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    target_depth = _normalize_depth(dhasa_level_index)

    vim_bal, maha_rows = get_dhasa_bhukthi(
        jd=jd_at_dob,
        place=place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        antardhasa_option=antardhasa_option,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )

    maha_for_utils = [
        (_as_tuple_lords(row[0]), row[1])
        for row in maha_rows
    ]

    rd1 = utils.get_running_dhasa_for_given_date(
        current_jd,
        maha_for_utils,
    )

    running = [
        _as_tuple_lords(rd1[0]),
        rd1[1],
        rd1[2],
    ]

    running_all = [running]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = yoga_vimsottari_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            antardhasa_option=antardhasa_option,
            use_rasi_bhukthi_variation=use_rasi_bhukthi_variation and depth == 2,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )

        if not children:
            running = [
                parent_lords + (parent_lords[-1],),
                parent_end,
                parent_end,
            ]
            running_all.append(running)
            break

        periods_for_utils = _to_utils_periods(
            children,
            parent_end_tuple=parent_end,
        )

        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(
                current_jd,
                periods_for_utils,
            )

            running = [
                _as_tuple_lords(rdk[0]),
                rdk[1],
                rdk[2],
            ]

        running_all.append(running)

    return running_all

'------ main -----------'
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    for dd in const.DHASA_YEAR_DURATION:
        const.dhasa_year_duration_default = dd
        print(dd.name,get_dhasa_bhukthi(jd_at_dob, place, dhasa_level_index=1))
    exit()
    from datetime import datetime
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        print(
            "Dehā        :",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        _vim_bal, ad = get_dhasa_bhukthi(
            jd_at_dob,
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
            )
        )
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.yoga_vimsottari_tests()
