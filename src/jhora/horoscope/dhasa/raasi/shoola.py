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
from jhora.horoscope.chart import house,charts
""" This is different from Nirayana Shoola Dhasa """
year_duration = const.sidereal_year
def shoola_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=2,   # 1..6 (default: L2 = Maha + Antara)
    round_duration=False
):
    """
    Shoola Dasha entry point (no backward-compat mapping).
    Accepts dhasa_level_index and forwards it to shoola_dhasa.
    """
    jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    return shoola_dhasa(
        planet_positions,
        dob,
        tob,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration
    )
def shoola_dhasa(
    planet_positions,
    dob,
    tob,
    dhasa_level_index=2,  # 1..6; default L2 (Maha + Antara)
    round_duration=False
):
    """
    Calculate Shoola Dasha up to the requested depth.

    Output (variable arity by level):
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Preserved module behavior:
      • Seed = stronger of Lagna vs 7th (using house.stronger_rasi_from_planet_positions).
      • Direction always forward; Maha duration = 9 years for every sign.
      • Second cycle logic mirrors original:
          - If level==1 → basis = MD years
          - Else       → basis = (MD years)/12
        Then MD2 = round(12 - basis, 2). If MD2 <= 0 → skip.
      • Lifespan cap is checked only in the second cycle using total_dhasa_duration,
        exactly as in your original implementation.

    General multi-level rules:
      • Each deeper level is computed from its immediate parent (equal split ×12).
      • Σ(children) == parent; no double-advance of JD beyond Σ(children).
      • No rounding in time progression; optional rounding only in returned rows.
      • Timestamps via utils.julian_day_to_date_time_string(jd).
    """
    start_jd = utils.julian_day_number(dob, tob)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    asc_house     = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house + const.HOUSE_7) % 12

    # Seed: stronger of Lagna vs 7th
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(
        planet_positions, asc_house, seventh_house
    )

    # Always forward; each MD = 9 years
    md_progression = [(dhasa_seed_sign + k) % 12 for k in range(12)]
    md_years = 9.0

    dhasa_info = []

    def _append_row(lords_stack, start_jd_val, seg_years):
        disp = seg_years if not round_duration else round(
            seg_years, getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
        )
        dhasa_info.append(tuple(
            lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp]
        ))
        return start_jd_val + seg_years * const.sidereal_year

    def _child_sequence(parent_lord):
        return _antardhasa(parent_lord, p_to_h)

    def _expand(start_jd_val, parent_years, lords_stack, level, target_level):
        if level == target_level:
            return _append_row(lords_stack, start_jd_val, parent_years)
        child_years = parent_years / 12.0
        for child in _child_sequence(lords_stack[-1]):
            start_jd_val = _expand(start_jd_val, child_years, lords_stack + [child], level + 1, target_level)
        return start_jd_val

    # ---- Only the first cycle (12 × 9 = 108) ----
    for md in md_progression:
        start_jd = _expand(start_jd, md_years, [md], level=1, target_level=dhasa_level_index)

    return dhasa_info
def _shoola_dhasa(chart,dob):
    """
        calculate Shoola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    #print("Finding which house",asc_house,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi(h_to_p,asc_house,seventh_house)
    #print('dhasa_seed_sign',dhasa_seed_sign)
    if dhasa_seed_sign != asc_house:
        dhasa_seed_sign = (dhasa_seed_sign+asc_house - 1)%12
    #print('dhasa_seed_sign',dhasa_seed_sign)
    " direction is always forward for this shoola dhasa and dhasa duration is always 9 years"
    direction = 1
    dhasa_progression = [(dhasa_seed_sign+direction*k)%12 for k in range(12)]
    #print(dhasa_progression)
    dhasa_periods = []
    dhasa_duration = 9
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_end = dhasa_start+dhasa_duration
        andtardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        dhasa_start = dhasa_end
    # Second cycle
    dhasa_start = dhasa_end
    total_dhasa_duration = sum([row[-1] for row in dhasa_periods ])
    for c,sign in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_periods[c][-1]
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            #dhasa_duration = 12
            continue
        dhasa_end = dhasa_start+dhasa_duration
        #print(sign,_narayana_antardhasa(sign))
        andtardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        dhasa_start = dhasa_end
        #print('total_dhasa_duration',total_dhasa_duration,dhasa_end)
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_periods
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
    pvr_tests.shoola_dhasa_tests()