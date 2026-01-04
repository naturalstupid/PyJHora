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
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik
year_duration = const.sidereal_year
def _dhasa_duration(planet_positions,sign,varsha_narayana=False):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    dhasa_period = utils.count_rasis(house_of_lord,sign) if sign in const.even_footed_signs \
                            else utils.count_rasis(sign, house_of_lord) 
    dhasa_period -= 1 # Subtract one from the count
    if dhasa_period <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then.
        """
        dhasa_period = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM : # > const._FRIEND:
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        dhasa_period += 1
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEBILITATED_NEECHAM:
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
        dhasa_period -= 1
    if varsha_narayana:
        dhasa_period *= 3
    return dhasa_period
def _narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=1, months=1, sixty_hours=1,include_antardhasa=True,varsha_narayana=False):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    dhasa_factor = year_duration
    if varsha_narayana:
        dhasa_factor /= 360
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    if p_to_h[8]==dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h[6]==dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]
    dhasa_periods = []
    jd_at_dob = utils.julian_day_number(dob, tob)
    dhasa_start_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    for dhasa_lord in dhasa_progression:
        dhasa_duration = _dhasa_duration(planet_positions,dhasa_lord,varsha_narayana)
        bhukthis = _narayana_antardhasa(planet_positions,dhasa_lord)#_narayana_antardhasa(dhasa_lord,p_to_h)
        if include_antardhasa:
            dhasa_duration /= 12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(dhasa_start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_periods.append((dhasa_lord,bhukthi_lord,dhasa_start,dhasa_duration))
                dhasa_start_jd += dhasa_duration * dhasa_factor
        else:
            y,m,d,h = utils.jd_to_gregorian(dhasa_start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_periods.append((dhasa_lord,dhasa_start,dhasa_duration))
            dhasa_start_jd += dhasa_duration * dhasa_factor
    # Second cycle
    total_dhasa_duration = sum([row[-1] for row in dhasa_periods ])
    for c,dhasa_lord in enumerate(dhasa_progression):
        dhasa_duration = (12 - dhasa_periods[c][-1])
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            continue
        bhukthis = _narayana_antardhasa(planet_positions,dhasa_lord)#_narayana_antardhasa(dhasa_lord,p_to_h)
        if include_antardhasa:
            dhasa_duration /= 12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(dhasa_start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_periods.append((dhasa_lord,bhukthi_lord,dhasa_start,dhasa_duration))
                dhasa_start_jd += dhasa_duration * dhasa_factor
        else:
            y,m,d,h = utils.jd_to_gregorian(dhasa_start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_periods.append((dhasa_lord,dhasa_start,dhasa_duration))
            dhasa_start_jd += dhasa_duration * dhasa_factor
        if varsha_narayana:
            if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa*3:
                break
        else:
            if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
                break
    return dhasa_periods
def narayana_dhasa_for_divisional_chart(dob,tob,place,years=1, months=1, sixty_hours=1,divisional_chart_factor=1,include_antardhasa=True):
    if divisional_chart_factor==1:
        return narayana_dhasa_for_rasi_chart(dob, tob, place, years, months, sixty_hours, include_antardhasa)
    # Get Rasi Chart first
    jd_at_dob = utils.julian_day_number(dob,tob)
    planet_positions_rasi = charts.divisional_chart(jd_at_dob, place)
    h_to_p_rasi = utils.get_house_planet_list_from_planet_positions(planet_positions_rasi)
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    # For D-n planet_positions_rasi get the lord of nth house in rasi planet_positions_rasi
    seed_house = (p_to_h_rasi[const._ascendant_symbol]+divisional_chart_factor-1)%12
    lord_of_seed_house = house.house_owner_from_planet_positions(planet_positions_rasi, seed_house,check_during_dhasa=True)
    """ 
        Important:
        Take the rasi occupied by Lord of Seed House in the divisional planet_positions_rasi of interest as lagna of varga planet_positions_rasi
    """
    # Get Varga Chart
    varga_planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    lord_sign = p_to_h_varga[lord_of_seed_house]
    h_to_p_varga = utils.get_house_planet_list_from_planet_positions(varga_planet_positions)
    h_to_p_varga = utils.get_house_planet_list_from_planet_positions(varga_planet_positions)
    seventh_house = (lord_sign+7-1)%12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(varga_planet_positions, lord_sign, seventh_house)
    return _narayana_dhasa_calculation(varga_planet_positions,dhasa_seed_sign,dob,tob,place,years=years, months=months, sixty_hours=sixty_hours,include_antardhasa=include_antardhasa,varsha_narayana=False)
def narayana_dhasa_for_rasi_chart(dob,tob,place,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.rasi_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    return _narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,sixty_hours=sixty_hours,include_antardhasa=include_antardhasa,varsha_narayana=False)
def _narayana_antardhasa(planet_positions,dhasa_rasi):
    _DEBUG_ = False
    if _DEBUG_:print('dhasa_rasi',utils.RAASI_LIST[dhasa_rasi])
    lord_of_dhasa_rasi = house.house_owner_from_planet_positions(planet_positions, dhasa_rasi, check_during_dhasa=True)
    if _DEBUG_:print('lord_of_dhasa_rasi',utils.PLANET_NAMES[lord_of_dhasa_rasi])
    house_of_dhasa_rasi_lord = planet_positions[lord_of_dhasa_rasi+1][1][0]
    if _DEBUG_:print('house_of_dhasa_rasi_lord',utils.RAASI_LIST[house_of_dhasa_rasi_lord])
    lord_of_7thhouse_of_dhasa_rasi = house.house_owner_from_planet_positions(planet_positions, (dhasa_rasi+7)%12, check_during_dhasa=True)
    if _DEBUG_:print('lord_of_7thhouse_of_dhasa_rasi',utils.PLANET_NAMES[lord_of_7thhouse_of_dhasa_rasi])
    house_of_dhasa_rasi_lord_7thHouse = planet_positions[lord_of_7thhouse_of_dhasa_rasi+1][1][0]
    if _DEBUG_:print('house_of_dhasa_rasi_lord_7thHouse',utils.RAASI_LIST[house_of_dhasa_rasi_lord_7thHouse])
    antardhasa_seed_rasi = house.stronger_rasi_from_planet_positions(planet_positions, house_of_dhasa_rasi_lord, house_of_dhasa_rasi_lord_7thHouse)
    if _DEBUG_:print('stronger antardhasa_seed_rasi',utils.RAASI_LIST[antardhasa_seed_rasi])
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    return _narayana_antardhasa_old(antardhasa_seed_rasi,p_to_h)
def _narayana_antardhasa_old(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
def varsha_narayana_dhasa_bhukthi(dob,tob,place,years=1,months=1,sixty_hours=1,divisional_chart_factor=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years)
    rasi_planet_positions = charts.rasi_chart(jd_at_years, place)
    p_to_h_rasi = utils.get_planet_house_dictionary_from_planet_positions(rasi_planet_positions)
    varga_planet_positions = charts.divisional_chart(jd_at_years, place, divisional_chart_factor=divisional_chart_factor)
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    natal_lagna =  p_to_h_rasi[const._ascendant_symbol]
    annual_house = (natal_lagna+(years-1)+divisional_chart_factor-1)%12
    h_to_p_varga = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h_varga)
    annual_house_owner_in_varga = house.house_owner_from_planet_positions(varga_planet_positions,annual_house,check_during_dhasa=True)
    dhasa_seed_sign = p_to_h_varga[annual_house_owner_in_varga]
    nd = _narayana_dhasa_calculation(varga_planet_positions, dhasa_seed_sign, dob,tob,place,years=years,months=months,sixty_hours=sixty_hours,include_antardhasa=include_antardhasa,varsha_narayana=True)
    return nd
    
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.chapter_18_tests()
    pvr_tests.varsha_narayana_tests()
