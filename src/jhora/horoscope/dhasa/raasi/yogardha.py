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
from jhora.horoscope.dhasa.raasi import chara, sthira
""" Mahadasa match with JHora. Antardasa does not match with JHora """
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
    round_duration=False   # only affects returned rows; progression uses full precision
):
    """
    Yogardha Dasha with multi-level expansion (L1..L6).

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Rules:
      • L1 lords: stronger of Lagna vs 7th as seed; forward from seed, reverse if seed is even.
      • L1 duration (years): 0.5 * (chara._dhasa_duration(md) + sthira._dhasa_duration(md)).
      • Lx+1 lords: chara._antardhasa(Lx_lords)  (global transformation per level).
      • Lx duration: L(x-1) / 12 (equal split at each deeper level).
      • Σ(children) == parent; no double-advancing JD.
      • Timestamps via utils.julian_day_to_date_time_string(jd).
      • No rounding in progression; optional rounding in returned durations via round_duration.
    """
    # --- Chart & seed ---
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    asc_house = planet_positions[0][1][0]
    seventh_house = (asc_house + 6) % 12  # your original uses (asc+6)%12
    dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)

    # L1 (Maha) sequence: forward from seed; reverse if seed is even
    l1_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        l1_lords = [(dhasa_seed - h + 12) % 12 for h in range(12)]

    # Precompute lords sequence per level using chara._antardhasa(Lx) → Lx+1
    # Level 1 sequence is l1_lords; for k>=2, level_k_lords = chara._antardhasa(level_{k-1}_lords)
    levels_lords = {1: l1_lords}
    for lvl in range(2, dhasa_level_index + 1):
        # Delegate to chara._antardhasa on the entire previous level’s list (global transform).
        levels_lords[lvl] = chara._antardhasa(levels_lords[lvl - 1])

    dhasa_info = []
    start_jd = jd_at_dob

    # --- Helpers ---
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
        return start_jd_val + seg_duration_years * year_duration  # keep module's year_duration symbol

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a segment down to target_level.
          • If current_level == target_level → append one row for the entire segment.
          • Else → split evenly among 12 children (order from precomputed levels_lords[current_level+1]).
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        # Children at next level are the global sequence for that level (from chara._antardhasa)
        children = levels_lords[current_level + 1]
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

    # --- Generate rows (single cycle; L1 durations via chara/sthira average) ---
    for md_lord in l1_lords:
        md_years = 0.5 * (
            chara._dhasa_duration(planet_positions, md_lord) +  # expects (planet_positions, rasi)
            sthira._dhasa_duration(md_lord)                      # expects (rasi)
        )

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
    pvr_tests.yogardha_dhasa_test()