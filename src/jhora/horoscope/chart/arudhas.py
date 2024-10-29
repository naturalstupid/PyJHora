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
from jhora.horoscope.chart import house
def bhava_arudhas_from_planet_positions(planet_positions):
    """
        gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna)
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
    """ V3.6.4 Below line is crucial. If Uranus/Netp/Pluto included wrong A1..A12 results
        So planet_positions restricted [:const._pp_count_upto_ketu] """
    planet_positions = planet_positions[:const._pp_count_upto_ketu]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    houses = [(h+asc_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for h in houses:
        lord_of_the_house = house.house_owner_from_planet_positions(planet_positions, h, check_during_dhasa=False)
        house_of_the_lord = p_to_h[lord_of_the_house]
        signs_between_house_and_lord = utils.count_rasis(h,house_of_the_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = utils.count_rasis(h,bhava_arudha_of_house)#((bhava_arudha_of_house+1+12-h)%12)
        if signs_from_the_house in [1,7]:
            bhava_arudha_of_house = (bhava_arudha_of_house+10-1)%12
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def bhava_arudhas(chart):
    """
        gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna)
        @param chart: Enter chart information in the following format. 
            For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    houses = [(h+asc_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for h in houses:
        lord_of_the_house = house.house_owner(h_to_p, h) # V2.3.1
        house_of_the_lord = p_to_h[lord_of_the_house]
        signs_between_house_and_lord = utils.count_rasis(h,house_of_the_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = ((bhava_arudha_of_house+1+12-h)%12)
        if signs_from_the_house in [1,7]:
            bhava_arudha_of_house = (bhava_arudha_of_house+10-1)%12
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def graha_arudhas_from_planet_positions(planet_positions):
    """
        gives Graha Arudhas for each planet from the planet positions
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    graha_arudhas_of_planets = []
    for p in range(const._planets_upto_ketu):
        house_of_the_planet = p_to_h[p]
        sign_owned_by_planet = const.house_lords_dict[p]
        if len(sign_owned_by_planet)>1:
            sign_owned_by_planet = house.stronger_rasi_from_planet_positions(planet_positions,sign_owned_by_planet[0],sign_owned_by_planet[1])
        else:
            sign_owned_by_planet = sign_owned_by_planet[0]
        count_to_strong = (sign_owned_by_planet+1+12-house_of_the_planet)%12
        count_to_arudha = (house_of_the_planet+2*(count_to_strong-1))%12
        count_from_house = (house_of_the_planet+12-count_to_arudha)%12
        if count_from_house in [0,6]:
            count_to_arudha = (count_to_arudha+9)%12
        graha_padha_of_planet = count_to_arudha
        graha_arudhas_of_planets.append(graha_padha_of_planet)
    return graha_arudhas_of_planets
def graha_arudhas(chart):
    """
        gives Graha Arudhas for each planet from the chart
        @param chart: Enter chart information in the following format. For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    graha_arudhas_of_planets = []
    for p in range(const._planets_upto_ketu):
        house_of_the_planet = p_to_h[p]
        sign_owned_by_planet = const.house_lords_dict[p]
        if len(sign_owned_by_planet)>1:
            sign_owned_by_planet = house.stronger_rasi(h_to_p,sign_owned_by_planet[0],sign_owned_by_planet[1])
        else:
            sign_owned_by_planet = sign_owned_by_planet[0]
        count_to_strong = (sign_owned_by_planet+1+12-house_of_the_planet)%12
        count_to_arudha = (house_of_the_planet+2*(count_to_strong-1))%12
        count_from_house = (house_of_the_planet+12-count_to_arudha)%12
        if count_from_house in [0,6]:
            count_to_arudha = (count_to_arudha+9)%12
        graha_padha_of_planet = count_to_arudha
        graha_arudhas_of_planets.append(graha_padha_of_planet)
    return graha_arudhas_of_planets
    
if __name__ == "__main__":
    """
    from jhora.panchanga import drik
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5) 
    jd = utils.julian_day_number(dob, tob); dcf = 1
    from jhora.horoscope.chart import charts
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=dcf)
    ba = bhava_arudhas_from_planet_positions(planet_positions)
    print(ba); exit()
    """
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.chapter_9_tests()
