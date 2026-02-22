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
from jhora import const,utils
from jhora.panchanga import drik
from jhora.horoscope.chart import house
from jhora.horoscope.dhasa.raasi import narayana
from jhora.horoscope.chart import charts
year_duration = const.sidereal_year
"""
    
    TODO: Book examples matches what is stated in PVR's book
    But same example data in JHora give different dhasa/bhukthi values
    Not Clear what JHora's algorithm is
"""

def sudasa_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=2,   # 1..6 (default: L2 = Maha + Antara)
    round_duration=True
):
    """
    Entry point for Sudasa Dasha using dhasa_level_index.
    """
    jd = utils.julian_day_number(dob, tob)
    sl = drik.sree_lagna(jd, place, divisional_chart_factor=divisional_chart_factor)
    sree_lagna_house = sl[0]
    sree_lagna_longitude = sl[1]

    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)

    return sudasa_dhasa_from_planet_positions(
        planet_positions=planet_positions,
        sree_lagna_house=sree_lagna_house,
        sree_lagna_longitude=sree_lagna_longitude,
        dob=dob,
        tob=tob,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration
    )


def sudasa_dhasa_from_planet_positions(
    planet_positions,
    sree_lagna_house,
    sree_lagna_longitude,
    dob,
    tob,
    dhasa_level_index=2,   # 1..6; default L2 (Maha + Antara)
    round_duration=False
):
    """
    Calculate Sudasa Dasha up to the requested depth.

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
    """
    # --- Setup ---
    sl_frac_left = (30.0 - sree_lagna_longitude) / 30.0
    start_jd = utils.julian_day_number(dob, tob)

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    # Direction: odd → forward; even → backward
    direction = 1 if (sree_lagna_house in const.odd_signs) else -1
    # Exceptions
    if p_to_h[const.SATURN_ID] == sree_lagna_house:
        direction = 1
    elif p_to_h[const.KETU_ID] == sree_lagna_house:
        direction *= -1

    # Kendra-based MD sequence (as in your code)
    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [ (sree_lagna_house + direction * (k - 1)) % 12 for k in ks ]

    dhasa_info = []
    md_years_cycle1 = []  # store first-cycle MD years (unrounded), after SL fraction for c==0

    # --- Helpers ---
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append one leaf row and advance time by seg_duration_years.
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
        )
        dhasa_info.append(tuple(
            lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]
        ))
        return start_jd_val + seg_duration_years * year_duration  # keep module's year_duration

    def _child_sequence(parent_lord):
        """
        L2 direction/order (and deeper) determined by parent's placement,
        via your existing _antardhasa logic.
        """
        return _antardhasa(parent_lord, p_to_h)

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a node:
          • If current_level == target_level: append one leaf for the entire segment.
          • Else: split evenly among 12 children ordered by _child_sequence.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence(parent_lord)
        child_duration = parent_duration_years / 12.0  # Lx = L(x-1)/12 equal split

        for child_lord in children:
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # --- First cycle ---
    for idx, md_lord in enumerate(dhasa_progression):
        md_years = narayana._dhasa_duration(planet_positions, md_lord)  # L1 only
        if idx == 0:
            md_years *= sl_frac_left  # fraction left in SL at birth

        md_years_cycle1.append(md_years)

        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    # --- Second cycle (preserve your basis rules & depth dependency) ---
    # Start with the total from the first cycle (as your original code did)
    total_dhasa_duration = sum(row[-1] for row in dhasa_info)

    # Depth factor:
    #   L1 → div = 1
    #   L2 → div = 12
    #   L3 → div = 12^2
    #   ...
    depth_divisor = (12 ** (dhasa_level_index - 1))

    for c, md_lord in enumerate(dhasa_progression):
        if dhasa_level_index == 1:
            # L1 basis: c==0 ignores SL fraction; c>0 uses MD from cycle-1
            basis = narayana._dhasa_duration(planet_positions, md_lord) if c == 0 else md_years_cycle1[c]
        else:
            # L2+ basis: depth-adjusted
            if c == 0:
                # ignore SL fraction: use raw MD years, but scaled down to current depth
                basis = narayana._dhasa_duration(planet_positions, md_lord) / depth_divisor
            else:
                # use the cycle-1 MD for this lord (which already includes any SL fraction effect if applicable),
                # then scale down to current depth
                basis = md_years_cycle1[c] / depth_divisor

        md2_years = 12.0 - basis
        if md2_years <= 0:
            continue

        total_dhasa_duration += md2_years

        start_jd = _expand_children(
            start_jd,
            md2_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

        # Keep your original break condition location/semantics
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break

    return dhasa_info
def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[const.SATURN_ID]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[const.KETU_ID]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.sudasa_tests()