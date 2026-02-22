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
""" TODO: Paryaaya Dasa NOT IMPLEMENTED FULLY YET
    Dhasas are ok. Antardasa and periods are not matching JHora
    Try: https://sutramritam.blogspot.com/2010/03/chara-paryaya-dasa-introduction.html
"""
sidereal_year = const.sidereal_year
dhasa_adhipati_list = [0,4,6,10,0,4,6,10,0,4,6,10]
antardhasa_list = [6,0,8,10,4,8,6,0,8,10,4,8]
chara_paryaaya_list = [1,5,9,2,6,10,3,7,11,4,8,12]
ubhaya_paryaaya_list = [1,4,7,10,2,5,8,11,3,6,9,12]
sthira_paryaaya_list = [1,7,2,8,3,9,4,10,5,11,6,12]

def applicability(planet_positions):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lagna = p_to_h[const._ascendant_symbol]
    trines = house.trines_of_the_raasi(lagna)
    # Jupiter in either of Trines
    jupiter_in_trines = p_to_h[const.JUPITER_ID] in trines
    if jupiter_in_trines: return True
    # Mercury in either of trines
    mercury_in_trines = p_to_h[const.MERCURY_ID] in trines
    if mercury_in_trines: return True
    # Placement of atma karaka in trines
    ak_in_trines = house.chara_karakas(planet_positions)[0] in trines
    if ak_in_trines: return True
    # Placement of own lord in trines
    own_lord_in_trines = any([p_to_h[const.house_owners[h]]==h in trines for _,(h,_) in planet_positions])
    return own_lord_in_trines
    
def _dhasa_duration_iranganti(planet_positions,dhasa_lord):
    ak_planet = house.chara_karakas(planet_positions)[0]
    ak_rasi = planet_positions[ak_planet+1][1][0]
    target_houses = {ak_rasi}
    kendra_rasis    = set(house.quadrants_of_the_raasi(ak_rasi))
    panapara_rasis  = set(house.panapharas_of_the_raasi(ak_rasi))
    apoklima_rasis  = set(house.apoklimas_of_the_raasi(ak_rasi))
    kpa_rasis = kendra_rasis | panapara_rasis | apoklima_rasis
    rasis_with_planets = set([r for p,(r,_) in planet_positions if r in kpa_rasis and p!=const._ascendant_symbol ])
    target_houses |= rasis_with_planets
    dirn = 1 if dhasa_lord in const.odd_signs else -1
    count = 1
    for h in range(12):
        if (dhasa_lord+dirn*h)%12 in target_houses:
            return count
        count += 1
    return None
def _dhasa_duration_indiadivine(planet_positions,dhasa_lord):
    lord_owner = house.house_owner_from_planet_positions(planet_positions, dhasa_lord)
    house_of_lord = planet_positions[lord_owner+1][1][0]
    dhasa_period = (house_of_lord+13-dhasa_lord)%12
    if dhasa_lord in const.even_signs:
        dhasa_period = (dhasa_lord+13-house_of_lord)%12
    return dhasa_period
def _dhasa_lords(planet_positions,dhasa_seed, chara_seed_method=1):
    if dhasa_seed in const.dual_signs: # Dual and Chara Paryaaya
        dhasa_type = 1 # Chara
        if chara_seed_method==1: #Chara method = 1 - Iranganti / Raghava Bhatta - stronger of 1,5,9
            ts = house.trines_of_the_raasi(dhasa_seed)
            sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
            sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        else: # chara method = 2 - Krishna Mishra - stronger of Lagna and 7th
            sr = house.stronger_rasi_from_planet_positions(planet_positions,dhasa_seed,(dhasa_seed+const.HOUSE_7)%12)
        dhasa_lords = [(sr+h-1)%12 for h in chara_paryaaya_list]
        if sr in const.even_footed_signs:
            dhasa_lords = [(sr-h+13)%12 for h in chara_paryaaya_list]
    elif dhasa_seed in const.movable_signs: # Movable and Ubhaya Paryaaya
        dhasa_type = 2 # Ubhaya
        ts = house.quadrants_of_the_raasi(dhasa_seed)
        sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[3])
        dhasa_lords = [(sr+h-1)%12 for h in ubhaya_paryaaya_list]
        if sr in const.even_footed_signs: # Fixed and Sthira Paryaaya
            dhasa_lords = [(sr-h+13)%12 for h in ubhaya_paryaaya_list]
    else: #Fixed = Sthira Paryaaya
        dhasa_type = 3 # Sthira
        sr = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_seed, (dhasa_seed+6)%12)
        dhasa_lords = [(sr+h-1)%12 for h in sthira_paryaaya_list]
        if sr in const.even_footed_signs:
            dhasa_lords = [(sr-h+13)%12 for h in sthira_paryaaya_list]
    return dhasa_type, dhasa_lords

def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=6,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,     # 1..6; default L2 (Maha + Antara)
    use_tribhagi_variation=False,
    round_duration=False,
    chara_seed_method = 1
):
    """
    Calculate Paryaaya Dasha up to the requested depth.

    Output (variable arity by level):
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
      Note: Ref: https://www.indiadivine.org/content/topic/1209053-varnada-and-paryaaya-dasa/
        Chara method = 1 - Iranganti / Raghava Bhatta - stronger of 1,5,9
        chara method = 2 - Krishna Mishra - stronger of Lagna and 7th
    """

    # ------------------------
    # Tribhagi settings
    # ------------------------
    _dhasa_cycles = 2
    _tribhagi_factor = 1.0
    if use_tribhagi_variation:
        _tribhagi_factor = 1.0 / 3.0
        _dhasa_cycles = int(_dhasa_cycles / _tribhagi_factor)  # e.g., 2 / (1/3) => 6 cycles

    # ------------------------
    # Prepare chart & seed
    # ------------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]
    asc_house = planet_positions[0][1][0]
    dhasa_seed = (asc_house + divisional_chart_factor - 1) % 12  # per your original logic
    dhasa_type, md_lords = _dhasa_lords(planet_positions, dhasa_seed,chara_seed_method=chara_seed_method)
    dhasa_info = []
    start_jd = jd_at_dob
    stop_due_to_lifespan = False

    def _append_row(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row with (optionally rounded) duration and enforce lifespan cutoff.
        """
        # Display duration (rounded only for output)
        disp_dur = seg_duration_years
        if round_duration:
            _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
            disp_dur = round(disp_dur, _round_ndigits)

        dhasa_info.append(tuple(lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]))

        # Lifespan cutoff right after appending the row
        birth_jd = jd_at_dob
        age_years = (start_jd_val - birth_jd) / const.sidereal_year
        if age_years >= getattr(const, 'human_life_span_for_narayana_dhasa', 108):
            return True
        return False

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a node:
          • Leaf if current_level == target_level → append one row for entire segment.
          • Otherwise split into 12 equal children ordered by _dhasa_lords with
            seed = immediate parent lord.
        Returns updated start_jd after consuming this segment.
        """
        nonlocal stop_due_to_lifespan

        if current_level == target_level:
            # Leaf node: append one row for the full segment
            if _append_row(parent_lords_stack, start_jd_val, parent_duration_years):
                stop_due_to_lifespan = True
            # Advance by the leaf duration
            return start_jd_val + parent_duration_years * const.sidereal_year

        # Otherwise split into 12 children at the next level
        parent_lord = parent_lords_stack[-1]
        _,child_sequence = _dhasa_lords(planet_positions, parent_lord)
        child_duration = parent_duration_years / 12.0  # equal split

        for child_lord in child_sequence:
            if stop_due_to_lifespan:
                break
            # Recurse down one level
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )

        return start_jd_val

    # ------------------------
    # Generate rows across cycles
    # ------------------------
    for _ in range(_dhasa_cycles):
        for md_lord in md_lords:
            if stop_due_to_lifespan:
                break

            # Base MD duration (scaled for tribhagi if enabled); DO NOT ROUND here
            #md_years = _dhasa_duration_iranganti(planet_positions, md_lord) * _tribhagi_factor
            md_years = _dhasa_duration_indiadivine(planet_positions, md_lord) * _tribhagi_factor
            # Expand to requested depth; do not advance JD again afterward
            start_jd = _expand_children(
                start_jd,
                md_years,
                [md_lord],
                current_level=1,
                target_level=dhasa_level_index
            )

        if stop_due_to_lifespan:
            break

    return dhasa_type,dhasa_info
if __name__ == "__main__":
    utils.set_language('en')
    """
    dob = drik.Date(1982,4,10); tob = (20,30,0); place=drik.Place('',20+2/60,75+13/60,5.5)
    jd = utils.julian_day_number(dob,tob); dcf = 1
    pp = charts.divisional_chart(jd,place,divisional_chart_factor=dcf)
    chart_rasi = utils.get_house_planet_list_from_planet_positions(pp)
    print(chart_rasi)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    print(p_to_h)
    dhasa_type,pd = get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=dcf,dhasa_level_index=1)
    print(dhasa_type,pd)
    exit()
    """
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.paryaaya_dhasa_test()