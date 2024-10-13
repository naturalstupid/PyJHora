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
from jhora.horoscope.chart import charts, house,arudhas
from jhora.horoscope.dhasa.raasi import narayana
""" TODO logic not fully implemented """
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    arudha_sign = arudhas.bhava_arudhas_from_planet_positions(planet_positions)[0]
    lord_of_arudha_sign = house.house_owner_from_planet_positions(planet_positions, arudha_sign)
    navamsa_planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=9)
    navamsa_arudha_sign = navamsa_planet_positions[lord_of_arudha_sign+1][1][0]
    arudha_seventh_house = (navamsa_arudha_sign+6)%12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(navamsa_planet_positions, navamsa_arudha_sign, arudha_seventh_house)
    #return narayana._narayana_dhasa_calculation(navamsa_planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,sixty_hours=sixty_hours,include_antardhasa=include_antardhasa,varsha_narayana=False)
    return narayana._narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,sixty_hours=sixty_hours,include_antardhasa=include_antardhasa,varsha_narayana=False)
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests.padhanadhamsa_dhasa_test()