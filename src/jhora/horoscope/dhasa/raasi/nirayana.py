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
""" Called Nirayana or Nirayana Shoola Dhasa """
from jhora import const, utils
from jhora.horoscope.chart import house,charts

def nirayana_shoola_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True
):
    jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd, place, divisional_chart_factor=divisional_chart_factor
    )[:const._pp_count_upto_ketu]
    return nirayana_shoola_dhasa(
        planet_positions,
        dob,
        tob,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration
    )


def nirayana_shoola_dhasa(
    planet_positions,
    dob,
    tob,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True
):
    """
    Calculate Nirayana Shoola Dasha up to the requested depth.

    Output (variable arity by level):
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
    """
    def _antardhasa(seed_rasi, p_to_h):
        direction = -1
        # Forward if AK (Saturn index '6' in your mapping?) is in seed, OR if seed is an odd sign
        if p_to_h[6] == seed_rasi or seed_rasi in const.odd_signs:
            direction = 1
        if p_to_h[8] == seed_rasi:  # flip direction if Mangal (index '8' here) occupies seed
            direction *= -1
        return [(seed_rasi + direction * i) % 12 for i in range(12)]

    def _append_row(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single row at the current depth with start time string and (optionally rounded) duration.
        Enforce lifespan cutoff AFTER appending (as per your rule).
        """
        # Compute returned duration (rounded only for display/output)
        disp_dur = seg_duration_years
        if round_duration:
            # If your codebase defines common rounding precision through const
            _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
            disp_dur = round(disp_dur, _round_ndigits)

        dhasa_info.append(tuple(lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]))

        # Lifespan cutoff (stop after row if exceeded)
        # Birth JD
        birth_jd = utils.julian_day_number(dob, tob)
        age_years = (start_jd_val - birth_jd) / const.sidereal_year
        if age_years >= getattr(const, 'human_life_span_for_narayana_dhasa', 108):
            return True  # signal to stop
        return False

    def _expand_children(
        start_jd_val,
        parent_duration_years,
        parent_lords_stack,
        parent_seed_rasi,
        p_to_h,
        current_level,
        target_level
    ):
        """
        Recursive, level-by-level expansion:
          • For Nirayana Shoola, each parent splits into 12 equal children.
          • Children order uses the same antara seed logic applied to the parent's seed.
          • We DO NOT round during progression; only in the returned rows.
          • Returns updated start_jd after expanding this branch.
        """
        nonlocal stop_due_to_lifespan

        if current_level == target_level:
            # Leaf node: just append a row for the whole segment
            # (This is the finest granularity requested.)
            if _append_row(parent_lords_stack, start_jd_val, parent_duration_years):
                stop_due_to_lifespan = True
            # Advance time by the entire leaf duration
            return start_jd_val + parent_duration_years * const.sidereal_year

        # Otherwise, split into 12 equal children at next level
        child_duration = parent_duration_years / 12.0
        child_sequence = _antardhasa(parent_seed_rasi, p_to_h)

        for child_lord in child_sequence:
            if stop_due_to_lifespan:
                break

            # Append or recurse:
            new_lords_stack = parent_lords_stack + [child_lord]
            # At every non-leaf boundary, we DO NOT append a row—only at leaf level
            next_seed = child_lord  # child's seed = its own rasi (preserves antara seed rule)
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                new_lords_stack,
                next_seed,
                p_to_h,
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ------------------------
    # Build chart basics
    # ------------------------
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    asc_house = p_to_h[const._ascendant_symbol]
    second_house = (asc_house + 2 - 1) % 12
    eighth_house = (asc_house + 8 - 1) % 12

    # Seed sign: stronger of 2H and 8H
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(
        planet_positions, second_house, eighth_house
    )

    # Direction (odd signs forward, even backward)
    direction = 1
    if dhasa_seed_sign in const.even_signs:
        direction = -1

    md_progression = [(dhasa_seed_sign + direction * k) % 12 for k in range(12)]

    # ------------------------
    # Generate rows
    # ------------------------
    dhasa_info = []
    start_jd = utils.julian_day_number(dob, tob)
    stop_due_to_lifespan = False

    # We also replicate the original basis used in the old code's second cycle:
    # If level == 1: basis = MD years; else basis = MD years / 12
    first_cycle_basis_for_second = []

    # ---------- First cycle ----------
    for md_rasi in md_progression:
        if stop_due_to_lifespan:
            break

        # Maha duration: 7/8/9 years by sign modality
        if md_rasi in const.fixed_signs:
            md_years = 8
        elif md_rasi in const.dual_signs:
            md_years = 9
        else:
            md_years = 7  # movable

        # Record basis for second cycle (preserving original behavior)
        basis = md_years if dhasa_level_index == 1 else (md_years / 12.0)
        first_cycle_basis_for_second.append(basis)

        # Expand to target depth
        # L1 row(s) → MD only
        # L2..L6 → recursively split by 12 at each deeper level
        start_jd = _expand_children(
            start_jd,
            md_years,
            parent_lords_stack=[md_rasi],
            parent_seed_rasi=md_rasi,
            p_to_h=p_to_h,
            current_level=1,
            target_level=dhasa_level_index
        )

    # Early stop if lifespan exceeded during first cycle
    if stop_due_to_lifespan:
        return dhasa_info

    # ---------- Second cycle ----------
    # Original code: for each of the 12 positions, compute
    #   dhasa_duration = round(12 - dhasa_info[c][-1], 2)
    # which depends on whether Antara was generated (bug-prone). To preserve
    # behavior without rewriting other logic, we emulate exactly:
    #   if L1 → basis was MD years
    #   else  → basis was (MD years)/12
    # so that MD2 = round(12 - basis, 2).
    for idx, md_rasi in enumerate(md_progression):
        if stop_due_to_lifespan:
            break

        md2_years = round(12 - first_cycle_basis_for_second[idx], 2)
        if md2_years <= 0:
            continue

        # Expand this second-cycle Maha to requested depth
        start_jd = _expand_children(
            start_jd,
            md2_years,
            parent_lords_stack=[md_rasi],
            parent_seed_rasi=md_rasi,
            p_to_h=p_to_h,
            current_level=1,
            target_level=dhasa_level_index
        )

        # After every parent (and all of its leaf rows), check lifespan again
        birth_jd = utils.julian_day_number(dob, tob)
        age_years = (start_jd - birth_jd) / const.sidereal_year
        if age_years >= getattr(const, 'human_life_span_for_narayana_dhasa', 108):
            break

    return dhasa_info
def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.nirayana_shoola_dhasa_tests()