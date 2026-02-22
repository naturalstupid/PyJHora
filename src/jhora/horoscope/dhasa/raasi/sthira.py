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
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year

def _dhasa_duration(lord):
    if lord in const.movable_signs:
        return 7
    elif lord in const.fixed_signs:
        return 8
    else:
        return 9
    

def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,   # 1..6; default L2 (Maha + Antara)
    round_duration=False   # round only in returned rows; progression uses full precision
):
    """
    Sthira Dasha with multi-level expansion (L1..L6).

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
    """
    # Chart & seed
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )
    brahma = house.brahma(planet_positions)
    brahma_sign = planet_positions[brahma + 1][1][0]  # seed rāśi
    md_lords = [(brahma_sign + h) % 12 for h in range(12)]  # forward sequence

    dhasa_info = []
    start_jd = jd_at_dob

    # ----- helpers -----
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row and advance by seg_duration_years.
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
        )
        dhasa_info.append(tuple(
            lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]
        ))
        return start_jd_val + seg_duration_years * year_duration  # keep your module's year_duration

    def _child_sequence(parent_lord):
        # Sthira: children go forward from parent_lord
        return [(parent_lord + h) % 12 for h in range(12)]

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a node to the requested depth.
        - If current_level == target_level: append one row covering the full segment.
        - Else: split parent duration equally among 12 children in forward order.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence(parent_lord)
        child_duration = parent_duration_years / 12.0  # equal split

        for child_lord in children:
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ----- generate rows (single cycle; durations via _dhasa_duration) -----
    for md_lord in md_lords:
        md_years = _dhasa_duration(md_lord)  # preserve your duration logic
        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    return dhasa_info

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.sthira_dhasa_test()