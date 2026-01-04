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
"""
    1=> KN Rao method 
    2=> Parasara/PVN Rao Method - from https://vedicastrologer.org/articles/pp_chara_dasa.pdf
    3=> Raghava Bhatta method from https://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html
"""
chara_method = 1
_dhasa_cycles = 2; one_year_days = const.sidereal_year

def _dhasa_duration_knrao_method(planet_positions,sign):
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
    return dhasa_period
def _dhasa_duration_pvnrao_method(planet_positions,sign):
    """ Not fully implemented yet """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    """ Additionally PVN Rao has following condition
            Stronger Co-lord of Sc and Aq for dasa years
            For Sc and Aq, there are 2 co-lords – Mars/Ketu and Saturn/Rahu. Find dasa years from the stronger co-lord
            using the following rules until there is a resolution:
            (1) If both lords are in the sign, dasa is of 12 years.
            (2) If one of them is in the sign, take dasa years from the other co-lord.
            (3) If both are outside the sign, take the stronger planet.    
            (4) One conjoining more planets is stronger.
            (5) A planet in a movable sign (Ar, Cn, Li, Cp) is stronger than a planet in a fixed sign (Ta, Le, Sc, Aq)
                and a planet in a fixed sign is stronger than a planet in a dual sign (Ge, Vi, Sg, Pi).
            (6) A planet giving more dasa years is stronger.
    """
    if sign==7: # sign is scorpio Mars/Ketu are co-lords
        if p_to_h[2]==sign and p_to_h[8]==sign: # Both in Scorpio
            dhasa_period = 12; return dhasa_period
        elif (p_to_h[2]==sign and p_to_h[8]!=sign): # only one of them in scorpio
            house_of_lord = p_to_h[8]
        elif (p_to_h[8]==sign and p_to_h[2]!=sign):
            house_of_lord = p_to_h[2]
        else:
            lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
            house_of_lord = p_to_h[lord_of_sign]
    elif sign==10: # sign is aquarius Sat/Rahu are co-lords
        if p_to_h[6]==sign and p_to_h[7]==sign: # Both in Aquarius
            dhasa_period = 12; return dhasa_period
        elif (p_to_h[6]==sign and p_to_h[7]!=sign): # only one of them in scorpio
            house_of_lord = p_to_h[7]
        elif (p_to_h[7]==sign and p_to_h[6]!=sign):
            house_of_lord = p_to_h[6]
        else:
            lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
            house_of_lord = p_to_h[lord_of_sign]
    else:
        lord_of_sign = const.house_owners[sign]
        house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        """ Counting is backward if dasa rasi is even-footed."""
        if house_of_lord < sign:
            dhasa_period = sign+1-house_of_lord
        else:
            dhasa_period = sign+13-house_of_lord
    else:
        """ Counting is forward if dasa rasi is odd-footed."""
        if house_of_lord < sign:
            dhasa_period = house_of_lord+13-sign
        else:
            dhasa_period = house_of_lord+1-sign
    dhasa_period -= 1 # Subtract one from the count
    if dhasa_period <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then.
        """
        dhasa_period = 12
        """ Following exceptions are not applicable for PVN Rao method """
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
    return dhasa_period
def _dhasa_duration_raghava_bhatta_method(planet_positions,sign):
    """ Not fully implemented yet """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    """ 
        The lord of Scorpio is Mars and lord of Aquarius is Saturn. Not necessary to consider Rahu, Ketu.
    """
    if sign==7: 
        house_of_lord = 2
    elif sign==10: # sign is aquarius Sat/Rahu are co-lords
        house_of_lord = 6
    else:
        lord_of_sign = const.house_owners[sign]
        house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        """ Counting is backward if dasa rasi is even-footed."""
        dhasa_period = (13+sign-house_of_lord)%12
        if dhasa_period ==0: dhasa_period = 12
    else:
        """ Counting is forward if dasa rasi is odd-footed."""
        dhasa_period = (13+house_of_lord-sign)%12
        if dhasa_period ==0: dhasa_period = 12
    dhasa_period -= 1 # Subtract one from the count
    if dhasa_period <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then.
        """
        dhasa_period = 12
    return dhasa_period
def _dhasa_duration_rangacharya_method(planet_positions,sign,gender):
    """ Not fully implemented yet """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    """ 
        The lord of Scorpio is Mars and lord of Aquarius is Saturn. Not necessary to consider Rahu, Ketu.
    """
    if sign==7: 
        house_of_lord = 2
    elif sign==10: # sign is aquarius Sat/Rahu are co-lords
        house_of_lord = 6
    else:
        lord_of_sign = const.house_owners[sign]
        house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    if gender==0:
        if house_of_lord in const.even_signs: # count back from sign to house_of_lord
            dhasa_period = (13+sign-house_of_lord)%12
        else:
            dhasa_period = (13+house_of_lord-sign)%12
    else:
        if house_of_lord in const.even_signs: # count back from sign to house_of_lord
            dhasa_period = (12+sign-house_of_lord)%12
        else:
            dhasa_period = (12+house_of_lord-sign)%12
    if dhasa_period ==0: dhasa_period = 12
    return dhasa_period
def _dhasa_duration(planet_positions,sign):
    return _dhasa_duration_knrao_method(planet_positions, sign)    
""" CHARA METHODS 2 and 3  - Logic not yet implemented """
def _antardhasa(dhasas,method=1): # KN Rao Method
    _antardhasas = dhasas[1:]+[dhasas[0]] if method==1 else dhasas
    return _antardhasas
def _dhasa_progression_pvnrao_method(planet_positions):
    """
        (1) Take the signs occupied by lagna, Moon and Sun. Take the one with the strongest lord. Strengths of
        lords are judged based on rules to be mentioned in another section.
    """
    sun_house = planet_positions[1][1][0]; sun_house_lord = house.house_owner_from_planet_positions(planet_positions, sun_house)
    asc_house = planet_positions[0][1][0]; asc_house_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    sh = house.stronger_planet_from_planet_positions(planet_positions, sun_house_lord, asc_house_lord)
    seed_house = asc_house if sh==asc_house_lord else sun_house
    moon_house = planet_positions[2][1][0]; moon_house_lord = house.house_owner_from_planet_positions(planet_positions, moon_house)
    stronger_lord = house.stronger_planet_from_planet_positions(planet_positions,sh, moon_house_lord)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)#; print(h_to_p)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)#; print(p_to_h)
    if moon_house_lord==stronger_lord:seed_house = moon_house 
    #print(asc_house_lord,sun_house_lord,moon_house_lord,'stronger lord of lagna, sun, moon houses',stronger_lord)
    #print(asc_house,sun_house,moon_house,'stronger of lagna, sun, moon houses',seed_house)
    ninth_house = (seed_house+8)%12
    _dhasa_progression = [(h+seed_house)%12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        #print('ninth house is even footed')
        _dhasa_progression = [(seed_house+12-h)%12 for h in range(12)]
    return _dhasa_progression
def _dhasa_progression_knrao_method(planet_positions):
    asc_house = planet_positions[0][1][0]
    seed_house = asc_house
    ninth_house = (seed_house+8)%12
    _dhasa_progression = [(h+seed_house)%12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        _dhasa_progression = [(seed_house+12-h)%12 for h in range(12)]
    return _dhasa_progression
def _dhasa_progression_raghava_bhatta_method(planet_positions,gender=1):
    asc_house = planet_positions[0][1][0]
    dhasa_seed = asc_house if gender==0 else (asc_house+3)%12
    #print('gender',gender,'dhasa seed',dhasa_seed)
    _dhasa_progression = [(dhasa_seed+h)%12 for h in range(12)] if asc_house in const.odd_signs else [(12+dhasa_seed-h)%12 for h in range(12)]
    if dhasa_seed in const.fixed_signs :
        _dhasa_progression = [(dhasa_seed+h*5)%12 for h in range(12)]
    elif dhasa_seed in const.dual_signs:
        _dhasa_progression = [(dhasa_seed+h+4)%12 for h in range(12)]
    return _dhasa_progression
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True,
                         chara_method=1,gender=0):
    """
        chara_method = 1 => Parasara/PVN Rao Method of two cycles. 2nd cycle duration 12-1st duration
        chara_methos = 2 => KN Rao Single Cycle
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    dhasa_progression = _dhasa_progression_pvnrao_method(planet_positions)
    start_jd = jd_at_dob
    dhasas = []
    _dhasa_cycles = 1 if chara_method==2 else 2
    for dc in range(_dhasa_cycles):
        for lord in dhasa_progression:
            dd = _dhasa_duration_knrao_method(planet_positions, lord) if chara_method==1 else _dhasa_duration_pvnrao_method(planet_positions, lord)
            if dc==1: # 2nd cycle for chara_method=1
                dd = 12.0-dd
            bhukthis = _antardhasa(dhasa_progression)
            if include_antardhasa:
                ddb = dd/12
                for bhukthi in bhukthis:
                    y,m,d,h = utils.jd_to_gregorian(start_jd)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    dhasas.append((lord,bhukthi,dhasa_start,ddb))
                    start_jd += ddb * one_year_days
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasas.append((lord,dhasa_start,dd))
                start_jd += dd * one_year_days
    return dhasas
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.chara_dhasa_test()
    