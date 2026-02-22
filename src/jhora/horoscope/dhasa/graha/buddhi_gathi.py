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
from jhora import utils, const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,   # 1..6 (default=2 to include Antara like before)
    max_cycles=2,
    round_duration=True
):
    """
    Buddhi Gathi dasha expansions to the requested depth, controlled solely by `dhasa_level_index`.

    Parameters
    ----------
    dob : (year, month, day)
    tob : (hour, minute, second)
    place : Place
    divisional_chart_factor : int, default=1
        1=Rasi, 9=Navamsa, ...
    chart_method : int, default=1
    years, months, sixty_hours : int
        Passed to charts.divisional_chart().
    dhasa_level_index : int, default=2
        Tree depth (L1..L6):
          1 = Maha only (no Antara)
          2 = + Antara (Bhukthi)
          3 = + Pratyantara
          4 = + Sookshma
          5 = + Prana
          6 = + Deha-antara
        NOTE: Caller must pass a valid value in 1..6.
    max_cycles : int, default=2
        Iterate base progression cycles.

    Returns
    -------
    list of tuples
        Tuple shape depends on depth:
          L1: (l1, start, duration_years)
          L2: (l1, l2, start, duration_years)
          L3: (l1, l2, l3, start, duration_years)
          L4: (l1, l2, l3, l4, start, duration_years)
          L5: (l1, l2, l3, l4, l5, start, duration_years)
          L6: (l1, l2, l3, l4, l5, l6, start, duration_years)

    Notes
    -----
    * Equal subdivision at each depth: sub_duration = parent_duration / d_len
    * Rotation at every depth from the current lord’s index in the base sequence
    * Life-span guard using const.human_life_span_for_narayana_dhasa
    """

    # --- Validate depth (no normalization/clamping) -------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha-antara).")

    max_level = dhasa_level_index  # L1=Maha ... L6=Deha-antara

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
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions[1:const._pp_count_upto_ketu])
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    planet_dict = {int(p): p_long for p, (_, p_long) in planet_positions[1:const._pp_count_upto_ketu]}
    asc_house = p_to_h[const._ascendant_symbol]

    dhasa_progression = []
    h1 = 0
    for h in range(12):
        hs = (asc_house + const.HOUSE_4 + h) % 12
        if h_to_p[hs] == '':
            continue
        planets = list(map(int, h_to_p[hs].split('/')))
        # Sort planets in this house by descending longitude
        d1 = {p: l for p, l in planet_dict.items() if p in planets}
        pl_new = [p for (p, _) in sorted(d1.items(), key=lambda item: item[1], reverse=True)]
        for pl in pl_new:
            durn = ((asc_house + h1 + 12) - p_to_h[pl]) % 12
            # If planet is exalted add +1  V4.6.3
            if const.house_strengths_of_planets[pl][p_to_h[pl]]==const._EXALTED_UCCHAM: durn += 1 
            # If planet is denilitated minus -1  V4.6.3
            if const.house_strengths_of_planets[pl][p_to_h[pl]]==const._DEBILITATED_NEECHAM: durn -= 1 
            dhasa_progression.append((pl, durn))
            h1 += 1

    d_len = len(dhasa_progression)
    if d_len == 0:
        return []

    base_order = [pl for (pl, _) in dhasa_progression]
    index_of = {pl: i for i, pl in enumerate(base_order)}
    lifespan_years = const.human_life_span_for_narayana_dhasa

    # --- Recursive subdivision engine --------------------------------------------
    def _recurse(level, start_index, start_jd_local, duration_years, prefix, rows_out):
        """
        level: current tree level (2..max_level). prefix holds L1..(level-1) lords.
        start_index: rotation start index in base_order for this node
        """
        sub_len = d_len
        if sub_len == 0:
            return

        sub_duration = duration_years / sub_len
        durn = round(sub_duration,const.DHASA_DURATION_ROUNDING_TO) if round_duration else sub_duration
        if level < max_level:
            jd_cursor = start_jd_local
            for k in range(sub_len):
                lord = base_order[(start_index + k) % sub_len]
                next_start_index = index_of[lord]
                _recurse(level + 1, next_start_index, jd_cursor, sub_duration, prefix + (lord,), rows_out)
                jd_cursor += sub_duration * const.sidereal_year
        else:
            # Leaf: emit rows at the deepest requested level
            jd_cursor = start_jd_local
            for k in range(sub_len):
                lord = base_order[(start_index + k) % sub_len]
                row_start = utils.julian_day_to_date_time_string(jd_cursor)
                row = prefix + (lord, row_start, durn)
                rows_out.append(row)
                jd_cursor += sub_duration * const.sidereal_year

    # --- Iterate Maha-dashas & expand to requested depth --------------------------
    dhasa_bhukthi_info = []
    start_jd = jd_at_dob
    total_dhasa_duration = 0

    cycles_done = 0
    outer_break = False
    while cycles_done < max_cycles and not outer_break:
        for dhasa_idx in range(d_len):
            dhasa_lord, dhasa_duration = dhasa_progression[dhasa_idx]
            durn = round(dhasa_duration, const.DHASA_DURATION_ROUNDING_TO) if round_duration else dhasa_duration
            if dhasa_duration <= 0:
                continue

            if max_level == 1:
                # Maha only (keep original tuple & duration type)
                dhasa_start = utils.julian_day_to_date_time_string(start_jd)
                row = (dhasa_lord, dhasa_start, durn)
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
                    rows_out=rows_out
                )
                dhasa_bhukthi_info.extend(rows_out)

            # advance to next maha
            start_jd += dhasa_duration * const.sidereal_year
            total_dhasa_duration += dhasa_duration

            if total_dhasa_duration >= lifespan_years:
                outer_break = True
                break
        cycles_done += 1

    return dhasa_bhukthi_info

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.buddhi_gathi_test()