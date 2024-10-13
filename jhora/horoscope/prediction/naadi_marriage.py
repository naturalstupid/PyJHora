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
from jhora.horoscope.chart import house
from jhora import utils
"""
    DO NOT USE THIS YET. UNDER TESTING...
    Based on Book: Prediction Secrets Naadi Astrology - A research work based on Rao's system - by Sri Satyanarayana Naik
"""
def _check_yoga_1(planet_positions:list=None,gender:int=0):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Yoga-1 / Yoga-7 - check if marriage planet of gender aspecting Jupiter or Saturn """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    planet = 5 # Venus
    if gender==1: planet = 2 # Mars
    aspected_planets = house.aspected_planets_of_the_planet(house_to_planet_list, planet)
    y1 = any([p1 in aspected_planets for p1 in [4,6]])
    y1msg = "Obstacles in marriage, if married, disputes with spouse"
    if y1: y1msg = "Marriage will happen"
    print('4/6 in aspected planets graha drishti of planet',planet,aspected_planets,y1,y1msg)
    return (y1,y1msg)
def _check_yoga_2(planet_positions:list=None,gender:int=0):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ yoga-2 / yoga - 8 / Yoga-3/Yoga-9  Early/late marriage"""
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    planet = 5 # Venus
    if gender==1: planet = 2 # Mars
    aspected_planets = house.aspected_planets_of_the_planet(house_to_planet_list, planet)
    y2 = 4 in aspected_planets
    if y2:
        y2msg = "Early Marriage"
        print('yoga 2/8 Is Jupiter Aspecting',planet,aspected_planets,y2,y2msg)
    else:
        y2 = 6 in aspected_planets
        y2msg = "Late Marriage" if y2 else "Neither Early/Late Marriage"
        print('yoga 2/8 Is Saturn Aspecting',planet,aspected_planets,y2,y2msg)
    return (y2,y2msg)
def _check_yoga_3(planet_positions:list=None,gender:int=0):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Yoga-4 / obstacles in marriage, If married disputes with spouse """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    planet = 5 # Venus
    if gender==1: planet = 2 # Mars
    aspected_planets = house.aspected_planets_of_the_planet(house_to_planet_list, 8)
    y3msg = ""; y3 = planet in aspected_planets
    if y3: y3msg = "Obstacles in marriage, If married disputes with spouse."
    print('yoga 4/10 Is Kethu Aspecting',planet,aspected_planets,y3,y3msg)
    return (y3,y3msg)
    
def _check_yoga_4(planet_positions:list=None,gender:int=0):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Yoga-5 / Marriage delayed or if married, will not like the spouse. """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    planet = 5 # Venus
    if gender==1: planet = 2 # Mars
    aspected_planets = house.aspected_planets_of_the_planet(house_to_planet_list, 7)
    y4msg = ""; y4 = planet in aspected_planets
    if y4: y4msg = "Marriage delayed or if married, will not like the spouse."
    print('yoga 6/16 Is Rahu Aspecting',planet,aspected_planets,y4,y4msg)
    return (y4,y4msg)
def _check_marriage_yogas(planet_positions:list=None,gender:int=0):
    mc = []
    mc.append(_check_yoga_1(planet_positions, gender))
    mc.append(_check_yoga_2(planet_positions, gender))
    mc.append(_check_yoga_3(planet_positions, gender))
    mc.append(_check_yoga_4(planet_positions, gender))
    return mc

if __name__ == "__main__":
    horoscope_language = 'en' # """ Matplotlib charts available only English"""
    utils.set_language(horoscope_language)
    gender = 1 # Female
    #"""
    from jhora.horoscope.chart import charts
    from jhora.panchanga import drik
    dcf = 1
    pp = charts.divisional_chart(utils.julian_day_number((1996,12,7), (10,34,0)), drik.Place('Chennai,India',13.0878,80.2785,5.5),divisional_chart_factor=dcf)
    h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
    print(h_to_p)
    """
    h_to_p_1 = ['5/2/3/0','','','L/4','6/7','','','1','','','8','']
    h_to_p_2 = ['','','8','L/4','','1','','','7','6','2/3/5','0']
    #gender = 0
    h_to_p_3 = ['L/2','1','3','0/5','7','','','','4/6','','8','']
    """
    print(_check_marriage_yogas(pp,gender))
    