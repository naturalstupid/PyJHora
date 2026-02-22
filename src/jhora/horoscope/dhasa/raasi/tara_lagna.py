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
    Tara Lagna Dasha with multi-level expansion (L1..L6).

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Key rules:
      • L1 (Maha) duration is fixed: 9 years for each MD.
      • Seed/MD order from your original code (Ascendant + Moon star fraction; even seed reverses).
      • L2..L6: child order ALWAYS follows Atma Karaka (AK) sign & its direction rule.
      • Lx duration = L(x-1) / 12 (equal split at every deeper level).
      • Σ(children) == parent (no double-advance of JD).
      • Timestamps via utils.julian_day_to_date_time_string; no jd_to_gregorian/ to_dms.
      • No rounding in progression; `round_duration` only rounds the returned duration.
    """
    # ---- Seed & chart basics (unchanged logic) ----
    start_jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        start_jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    asc_house = planet_positions[0][1][0]

    # Moon longitude in absolute degrees within zodiac
    moon_longitude = planet_positions[2][1][0] * 30 + planet_positions[2][1][1]

    one_star = 360.0 / 27.0
    nak_frac = one_star / 12.0
    nak, _, _ = drik.nakshatra_pada(moon_longitude)

    # Daśā seed: based on Asc and the intra-nakshatra "tithi-like" twelfth
    dhasa_seed = (asc_house + int((moon_longitude - (nak - 1) * one_star) // nak_frac)) % 12

    # L1 MD sequence: forward from seed; reverse if seed is even sign
    md_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        md_lords = [(dhasa_seed - h) % 12 for h in range(12)]

    # Atma Karaka (AK) and its house (akh)
    ak = house.chara_karakas(planet_positions)[0]
    akh = planet_positions[ak + 1][1][0]

    # ---- Local helpers (no formatting wrappers; use utils.* directly) ----
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row and advance time by seg_duration_years.
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
        )
        dhasa_info.append(tuple(
            lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]
        ))
        return start_jd_val + seg_duration_years * const.sidereal_year

    def _ak_child_sequence():
        """
        Child order at ALL deeper levels (L2..L6) is driven by AK sign and its direction rule.
        """
        seq = [(akh + h) % 12 for h in range(12)]
        # Reverse for akh in [1,5,7,10] (your rule)
        if akh in [1, 5, 7, 10]:
            seq = [(akh - h) % 12 for h in range(12)]
        return seq

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a node down to the requested depth.
          • If current_level == target_level: append one row for the entire segment.
          • Else: split into 12 children using AK-based order and equal durations = parent/12.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        children = _ak_child_sequence()      # Always AK-driven at deeper levels
        child_duration = parent_duration_years / 12.0

        for child_lord in children:
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ---- Generate rows (single cycle; all MDs are 9 years) ----
    dhasa_info = []
    for md_lord in md_lords:
        md_years = 9.0  # fixed MD duration
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
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.tara_lagna_dhasa_test()