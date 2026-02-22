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
from jhora.horoscope.chart import charts, house
from jhora.horoscope.dhasa.raasi import narayana
""" Mahadhasa lord and period matches with JHora. Antardasa does not match """
year_duration = const.sidereal_year


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,   # 1..6; default L2 (Maha + Antara)
    round_duration=False   # only affects returned durations; progression uses full precision
):
    """
    Trikona Dasha with multi-level expansion (L1..L6).

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Rules:
      • Seed: pick strongest among the trines to Lagna:
          1) stronger of (1st, 5th), then stronger of (that, 9th).
      • L1 (Maha) order: forward if seed is odd sign, backward if seed is even sign.
      • L1 durations: narayana._dhasa_duration(planet_positions, md_lord).
      • L2..L6: child order depends on *parent lord* odd/even (forward/backward).
      • Lx durations: L(x-1) / 12 (equal split at each deeper level).
      • Σ(children) == parent; no double-advance of time.
      • Timestamps via utils.julian_day_to_date_time_string(jd).
      • No rounding in progression; optional rounding only for returned duration.
    """
    # -------- Chart & seed --------
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )

    # Trikona seed: strongest of (1st vs 5th), then vs 9th
    asc = planet_positions[0][1][0]
    trikonas = house.trines_of_the_raasi(asc)  # returns [1st, 5th, 9th] houses (indices)
    ds1 = house.stronger_rasi_from_planet_positions(planet_positions, trikonas[0], trikonas[1])
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, ds1, trikonas[2])

    # L1 (Maha) sequence: forward from seed if seed is odd, else backward
    md_lords = [(dhasa_seed_sign + h) % 12 for h in range(12)]
    if dhasa_seed_sign in const.even_signs:
        md_lords = [(dhasa_seed_sign - h) % 12 for h in range(12)]

    dhasa_info = []
    start_jd = jd_at_dob

    # -------- Local helpers --------
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row and advance by seg_duration_years (years).
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
        )
        dhasa_info.append(tuple(
            lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]
        ))
        return start_jd_val + seg_duration_years * year_duration  # use module's year_duration, as in your code

    def _child_sequence_from_parent(parent_lord):
        """
        L(x+1) order from Lx lord:
          • forward if parent_lord is odd sign
          • backward if parent_lord is even sign
        """
        if parent_lord in const.even_signs:
            return [(parent_lord - h) % 12 for h in range(12)]
        else:
            return [(parent_lord + h) % 12 for h in range(12)]

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand segments down to the target depth.
          • If current_level == target_level → append one row for the full segment.
          • Else → split evenly among 12 children ordered by parent's odd/even rule.
        Returns updated start_jd after this segment is fully consumed.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence_from_parent(parent_lord)
        child_duration = parent_duration_years / 12.0  # equal split at each deeper level

        for child_lord in children:
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # -------- Generate rows (single cycle) --------
    for md_lord in md_lords:
        md_years = narayana._dhasa_duration(planet_positions, md_lord)  # L1 only
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
    pvr_tests.trikona_dhasa_test()