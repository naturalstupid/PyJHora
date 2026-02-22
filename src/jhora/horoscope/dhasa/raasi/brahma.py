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

def _dhasa_duration(planet_positions, sign):
    lord_of_6th = house.house_owner_from_planet_positions(planet_positions, (sign+5)%12)
    lord_house = planet_positions[lord_of_6th+1][1][0]
    _dd = (lord_house+13-sign)%12
    if sign in const.even_signs:
        _dd = (sign+13-lord_house)%12
    _dd -= 1
    if lord_house == sign:
        _dd = 0
    elif const.house_strengths_of_planets[lord_of_6th][lord_house] == const._DEBILITATED_NEECHAM:
        _dd -= 1
    elif const.house_strengths_of_planets[lord_of_6th][lord_house] == const._EXALTED_UCCHAM:
        _dd += 1
    return _dd

def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True                               # round only the returned durations; JD math stays full precision
):
    """
        Compute Brahma-based sign daśā with depth control (Maha → Antara → …)

        This function generalizes your original `get_dhasa_antardhasa`:
        - Depth is controlled by `dhasa_level_index` instead of include_antardhasa.
        - Default depth = 2 (Antara) preserves your legacy output shape and values.

        Depth levels (output tuples):
          1 = MAHA_DHASA_ONLY     -> (l1,               start_str, dur_years)
          2 = ANTARA              -> (l1, l2,           start_str, dur_years)        [DEFAULT]
          3 = PRATYANTARA         -> (l1, l2, l3,       start_str, dur_years)
          4 = SOOKSHMA            -> (l1, l2, l3, l4,   start_str, dur_years)
          5 = PRANA               -> (l1, l2, l3, l4, l5, start_str, dur_years)
          6 = DEHA                -> (l1, l2, l3, l4, l5, l6, start_str, dur_years)

        Duration policy:
          - Maha duration (years) comes from _dhasa_duration(...) exactly as before.
          - At every deeper level, the IMMEDIATE parent is split into 12 equal parts
            (same logic you used for Antara). This guarantees Σ(children) = parent at each level.

        Ordering:
          - Maha sequence is 12 signs starting from dhasa_seed, or reverse if seed is even.
          - At each node, children are the 12 signs in cyclic order starting from the parent sign
            (identical to your `bn = d` wraparound).

        Rounding:
          - Only the returned 'dur_years' is rounded (when `round_duration=True`, using
            const.DHASA_DURATION_ROUNDING_TO if available). All JD math uses unrounded values.

        How to match old behavior:
          - Old "include_antardhasa=False"  -> set dhasa_level_index = const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
          - Old "include_antardhasa=True"   -> (default) dhasa_level_index = const.MAHA_DHASA_DEPTH.ANTARA
    """
    # --- Safety: ensure depth is valid ---------------------------------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # --- Build the base chart once (unchanged) ------------------------------------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    # Brahma seed sign / daśā seed (unchanged)
    brahma = house.brahma(planet_positions)
    dhasa_seed = planet_positions[brahma + 1][1][0]

    # Maha sequence (12 signs), forward when odd, reverse when even (unchanged)
    dhasa_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [(dhasa_seed + 6 - h + 12) % 12 for h in range(12)]

    # Control rounding precision (fallback to 2 if constant is absent)
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    # --- Helpers ------------------------------------------------------------------------------

    def _children_signs(parent_sign):
        """
        Children order for a given parent:
          12 signs in cyclic order starting from the *parent* sign itself,
          i.e., [parent, parent+1, ..., wrap].
        """
        return [(parent_sign + k) % 12 for k in range(12)]

    def _equal_split(parent_years):
        """
        Antara / deeper split: 12 equal parts of the immediate parent duration (years).
        """
        return parent_years / 12.0

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        """
        Recursive builder for depth >= 3. At each node:
          - Child duration = parent_years / 12
          - Children order = cyclic from `parent_sign`
          - Σ(children) = parent (by construction)
        """
        bhuktis = _children_signs(parent_sign)
        child_unrounded = _equal_split(parent_years)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for child_sign in bhuktis:
                _recurse(level + 1, child_sign, jd_cursor, child_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_unrounded * year_duration
        else:
            for child_sign in bhuktis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret = round(child_unrounded, _round_ndigits) if round_duration else child_unrounded
                out_rows.append(prefix + (child_sign, start_str, dur_ret))
                jd_cursor += child_unrounded * year_duration

    # --- Main loop: build rows at requested depth ---------------------------------------------

    dhasa_info = []
    start_jd = jd_at_dob

    for d, dhasa_lord in enumerate(dhasa_lords):
        # 1) Maha duration in YEARS (kept exactly as before)
        duration_years = float(_dhasa_duration(planet_positions, dhasa_lord))

        # Guard against negative/zero (rare, but keep math safe)
        # (If you prefer strict original behavior, remove the max(); I’m leaving the clamp commented)
        # duration_years = max(duration_years, 0.0)

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # ---- L1: Maha only ----
            dhasa_info.append((
                dhasa_lord,
                utils.julian_day_to_date_time_string(start_jd),
                round(duration_years, _round_ndigits) if round_duration else duration_years
            ))
            start_jd += duration_years * year_duration
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # ---- L2: Antara (legacy equal-split into 12) ----
            bhukthis = _children_signs(dhasa_lord)     # identical ordering to your original (bn=d logic)
            dd = duration_years / 12.0                  # equal split (years)
            jd_cursor = start_jd

            for bhukthi_lord in bhukthis:
                dhasa_info.append((
                    dhasa_lord,
                    bhukthi_lord,
                    utils.julian_day_to_date_time_string(jd_cursor),
                    round(dd, _round_ndigits) if round_duration else dd
                ))
                jd_cursor += dd * year_duration

            # Advance Maha cursor by full Maha duration
            start_jd += duration_years * year_duration
            continue

        # ---- L3..L6: recursive equal-split under immediate parent ----
        _recurse(
            level=const.MAHA_DHASA_DEPTH.ANTARA,   # = 2; children built at 3..N
            parent_sign=dhasa_lord,
            parent_start_jd=start_jd,
            parent_years=duration_years,
            prefix=(dhasa_lord,),
            out_rows=dhasa_info
        )
        start_jd += duration_years * year_duration

    return dhasa_info

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.brahma_dhasa_test()