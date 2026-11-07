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
import math
import time
from datetime import datetime
from enum import IntEnum

# PyJHora module imports
from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    """ Resolves this module's local year_duration (naive-fallback estimate).
    An explicitly passed dhasa_duration_type also becomes
    const.dhasa_year_duration_default, so that drik._get_dhasa_start_jd()
    and drik._get_dhasa_end_jd() (which read only that global) honor the
    caller's argument. When dhasa_duration_type is None, the global is
    left untouched and used as-is. """
    global year_duration
    if dhasa_duration_type is not None:
        const.dhasa_year_duration_default = dhasa_duration_type
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration

def _get_svara_id(nak_index: int) -> int:
    """nak_index is 0-indexed (0=Ashwini to 26=Revati)."""
    return nak_index % 5


def _get_svara_id_pada(nak_index: int, pada_index: int) -> int:
    """nak_index (0..26), pada_index (0..3). Total padas span 0..107."""
    total_pada = (nak_index * 4) + pada_index
    return total_pada % 5


def _panchasvara_start_info(start_lon: float, method: str = None):
    if method is None:
        method = const.panchasvara_method_default

    config = const.PANCHASVARA_CONFIG[method]
    nak_count = int(config["nak_count"])
    nak_span = 360.0 / nak_count

    nak_val = start_lon / nak_span
    nak_index = int(nak_val) % nak_count  # 0..26

    if config["is_pada"]:
        pada_span = nak_span / 4.0
        pada_index = int((start_lon % nak_span) / pada_span) % 4  # 0..3
        root_svara_id = _get_svara_id_pada(nak_index, pada_index)
        fraction_traversed = (start_lon % pada_span) / pada_span
    else:
        root_svara_id = _get_svara_id(nak_index)
        fraction_traversed = (start_lon % nak_span) / nak_span

    return root_svara_id, fraction_traversed


def _get_children_jds(
    parent_start_jd,
    parent_years,
    root_svara_id,
    parent_lords,
    method,
    place,
    dhasa_duration_type,
    savana_year_method,
    use_pancha_elements_for_svaras,
    antardhasa_option,
):
    config = const.PANCHASVARA_CONFIG[method]
    total_cycle = config["total_years"]

    if (
        not parent_lords
        or antardhasa_option
        == const.PANCHASVARA_ANTARDHASA_OPTION.START_WITH_JANMA_SVARA
    ):
        start_sid = root_svara_id
    else:
        last_lord = parent_lords[-1]
        start_sid = const.PANCHASVARA_LABEL_TO_ID.get(last_lord, root_svara_id)

    order_ids = [(start_sid + offset) % 5 for offset in range(5)]

    children = []
    cursor_jd = parent_start_jd

    for sid in order_ids:
        svara_weight = config["durations"][sid]
        child_years = parent_years * (svara_weight / total_cycle)
        
        # Calculate precise calendar end date using PyJHora's canonical method
        child_end_jd = drik._get_dhasa_end_jd(
            cursor_jd,
            place,
            child_years,
        )

        svara_label = (
            const.PANCHASVARA_LABELS[sid][1]
            if use_pancha_elements_for_svaras
            else const.PANCHASVARA_LABELS[sid][0]
        )
        new_lords = tuple(list(parent_lords) + [svara_label])
        children.append((new_lords, cursor_jd, child_end_jd, child_years))

        cursor_jd = child_end_jd

    return children


# =========================================================================
# 1. FULL DHASA BHUKTHI TREE
# =========================================================================
def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
    chart_method=1,
    round_duration=True,
    use_pancha_elements_for_svaras=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    antardhasa_option=None,
    dhasa_method=None,
    **kwargs
):
    if dhasa_method is None:
        dhasa_method = const.panchasvara_method_default
    if antardhasa_option is None:
        antardhasa_option = getattr(
            const, "panchasvara_antardhasa_option_default", None
        )

    jd_at_dob = utils.julian_day_number(dob, tob)

    start_lon = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    root_svara_id, fraction_traversed = _panchasvara_start_info(
        start_lon, dhasa_method
    )
    first_lord_years = const.PANCHASVARA_CONFIG[dhasa_method]["durations"][
        root_svara_id
    ]

    # Calculate precise initial start date
    initial_dasa_start_jd = drik._get_dhasa_start_jd(
        jd_at_dob,
        place,
        fraction_traversed,
        first_lord_years,
    )
    
    total_cycle = const.PANCHASVARA_CONFIG[dhasa_method]["total_years"]
    results = []

    def recurse_tree(current_depth, parent_start_jd, parent_years, current_lords):
        children = _get_children_jds(
            parent_start_jd,
            parent_years,
            root_svara_id,
            current_lords,
            dhasa_method,
            place,
            dhasa_duration_type,
            savana_year_method,
            use_pancha_elements_for_svaras,
            antardhasa_option,
        )

        for child_lords, c_start_jd, c_end_jd, c_years in children:
            if current_depth == dhasa_level_index:
                durn = (
                    round(c_years, dhasa_level_index)
                    if round_duration
                    else c_years
                )
                results.append(
                    [
                        list(child_lords),
                        utils.jd_to_gregorian(c_start_jd),
                        durn,
                    ]
                )
            else:
                recurse_tree(
                    current_depth + 1, c_start_jd, c_years, child_lords
                )

    cursor_jd = initial_dasa_start_jd
    for _ in range(2):
        recurse_tree(1, cursor_jd, total_cycle, ())
        
        # Advance cycle precisely
        cursor_jd = drik._get_dhasa_end_jd(
            cursor_jd,
            place,
            total_cycle,
        )

    return results


# =========================================================================
# 2. IMMEDIATE CHILDREN
# =========================================================================
def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    antardhasa_option=None,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_starting_planet=1,
    use_tribhagi_variation=False,
    round_duration: bool = False,
    use_pancha_elements_for_svaras: bool = True,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    if dhasa_method is None:
        dhasa_method = const.panchasvara_method_default
    if antardhasa_option is None:
        antardhasa_option = getattr(
            const, "panchasvara_antardhasa_option_default", None
        )

    start_jd = utils.julian_day_number(
        drik.Date(*parent_start[:3]), (parent_start[3], 0, 0)
    )

    if (parent_duration is None) == (parent_end is None):
        raise ValueError(
            "Provide exactly one of parent_duration (years) or parent_end (tuple)"
        )

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = drik._get_dhasa_end_jd(
            start_jd,
            place,
            parent_years,
        )
    else:
        end_jd = utils.julian_day_number(
            drik.Date(*parent_end[:3]), (parent_end[3], 0, 0)
        )
        # Approximate parent years linearly just to derive exact child fractions
        year_duration = _set_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    start_lon = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    root_svara_id, _ = _panchasvara_start_info(start_lon, dhasa_method)
    path = (
        tuple(parent_lords)
        if isinstance(parent_lords, (list, tuple))
        else (parent_lords,)
    )

    children = _get_children_jds(
        start_jd,
        parent_years,
        root_svara_id,
        path,
        dhasa_method,
        place,
        dhasa_duration_type,
        savana_year_method,
        use_pancha_elements_for_svaras,
        antardhasa_option,
    )

    return [
        (c_lords, utils.jd_to_gregorian(s_jd), utils.jd_to_gregorian(e_jd))
        for c_lords, s_jd, e_jd, _ in children
    ]


# =========================================================================
# 3. RUNNING DASHA FOR GIVEN DATE (Tree Traversal)
# =========================================================================
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    use_tribhagi_variation: bool = False,
    star_position_from_moon: int = 1,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_starting_planet: int = 1,
    antardhasa_option=None,
    use_pancha_elements_for_svaras: bool = True,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    if dhasa_method is None:
        dhasa_method = const.panchasvara_method_default
    if antardhasa_option is None:
        antardhasa_option = getattr(
            const, "panchasvara_antardhasa_option_default", None
        )

    start_lon = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    root_svara_id, fraction_traversed = _panchasvara_start_info(
        start_lon, dhasa_method
    )
    first_lord_years = const.PANCHASVARA_CONFIG[dhasa_method]["durations"][
        root_svara_id
    ]

    initial_dasa_start_jd = drik._get_dhasa_start_jd(
        jd_at_dob,
        place,
        fraction_traversed,
        first_lord_years,
    )
    
    total_cycle = const.PANCHASVARA_CONFIG[dhasa_method]["total_years"]

    cycle_start_jd = initial_dasa_start_jd
    
    # Traverse forward until we find the active macro cycle
    while True:
        next_cycle_jd = drik._get_dhasa_end_jd(
            cycle_start_jd,
            place,
            total_cycle,
        )
        if current_jd < next_cycle_jd:
            break
        cycle_start_jd = next_cycle_jd

    ladder = []
    current_start_jd = cycle_start_jd
    current_years = total_cycle
    current_lords = ()

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = int(const.MAHA_DHASA_DEPTH.DEHA)

    for depth in range(1, target_depth + 1):
        children = _get_children_jds(
            current_start_jd,
            current_years,
            root_svara_id,
            current_lords,
            dhasa_method,
            place,
            dhasa_duration_type,
            savana_year_method,
            use_pancha_elements_for_svaras,
            antardhasa_option,
        )

        active_child = None
        for c_lords, c_start_jd, c_end_jd, c_years in children:
            if c_start_jd <= current_jd < c_end_jd:
                active_child = (c_lords, c_start_jd, c_end_jd, c_years)
                break

        if not active_child and children:
            active_child = children[-1]

        if not active_child:
            break

        c_lords, c_start_jd, c_end_jd, c_years = active_child
        ladder.append(
            [
                c_lords,
                utils.jd_to_gregorian(c_start_jd),
                utils.jd_to_gregorian(c_end_jd),
            ]
        )

        current_start_jd = c_start_jd
        current_years = c_years
        current_lords = c_lords

    return ladder

# =========================================================================
# USER EXECUTION BLOCK
# =========================================================================
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in const.DHASA_YEAR_DURATION:
        const.dhasa_year_duration_default = dd
        yd = _set_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob, tob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=2
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()