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

"""
    This file contains definitions of raja yoga (245-263) from BV Raman's book
    245 - Three or more planets shculd be in exaltation or own house occupying kendras.
    246 - When a planet is in debilitation but with bright rays, or retrograde, and occupies 
       favourable positions, Raja yoga will be caused. 
    247 - Two, there or four planets should possess Dig bala.
    248 - The Lagna must be Kumbha with Sukra in it and four planets should be exalted without 
        occupying evil navamsas or shastiamsa
    249 - The Moon must be in Lagna, Jupiter in the 4th, Venus in the 10th and Saturn exalted or in his own house
    250 - The lord of the sign, a planet is debilitated in, or the planet, who would be exalted there, should be in 
        a kendra from the Moon or Lagna.
    251 - The Moon mustbe in a kendra other than Lagna and aspected by Jupiter, and otherwise powerful.
    252 - Planets in debilitated Rasis should occupy exalted Navamsas
    
"""
from jhora import const, utils
from jhora.horoscope.chart import house, charts

def _raja_yoga_245_calculation(jd=None, place=None, divisional_chart_factor=1, planet_positions=None, chart_1d=None):
    """ 245 - Three or more planets should be in exaltation or own house occupying kendras."""
    _minimum_required_planets = 3
    # Check if jd, place is supplied
    if jd is not None and place is not None:
        planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor)
    # Check else planet positions supplied and can compute with pp alone
    if planet_positions is not None:
        chart_1d = utils.get_house_planet_list_from_planet_positions(planet_positions)
    # Check last if chart is supplied and can compute raja yoga with chart alone
    if chart_1d is None: return False
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_1d)
    raja_yoga_planets = []
    for p,h in p_to_h.items():
        if p != const._ascendant_symbol and const.house_strengths_of_planets[p][h] == const._EXALTED_UCCHAM:
            raja_yoga_planets.append(p)
    condition_1 = len(raja_yoga_planets) >= _minimum_required_planets
    if condition_1: return condition_1, raja_yoga_planets
    # Condition 2 - own house occupying kendras
    _kendras = house.quadrants_of_the_raasi(p_to_h[const._ascendant_symbol])
    raja_yoga_planets = []
    for p,h in p_to_h.items():
        if p != const._ascendant_symbol and const.house_strengths_of_planets[p][h] == const._OWNER_RULER:
            if p_to_h[p] in _kendras:
                raja_yoga_planets.append(p)
    condition_2 = len(raja_yoga_planets) >= _minimum_required_planets
    return condition_2, raja_yoga_planets
