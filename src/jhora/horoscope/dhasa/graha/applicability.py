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
from jhora import utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik
_conditional_dhasas = ['ashtottari','chaturaaseeti_sama','dwadasottari','dwisatpathi','panchottari','satabdika',
                    'shashtisama','shattrimsa_sama','shodasottari']
def applicability_check(dob,tob,place,divisional_chart_factor=1):
    jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=divisional_chart_factor)
    """ First check ashtottari dhasa applicability """
    applicable_dhasas = []
    from jhora.horoscope.dhasa.graha import ashtottari
    if ashtottari.applicability_check(planet_positions): applicable_dhasas.append('ashtottari')
    from jhora.horoscope.dhasa.graha import chathuraaseethi_sama
    if chathuraaseethi_sama.applicability_check(planet_positions): applicable_dhasas.append('chaturaaseeti_sama')
    from jhora.horoscope.dhasa.graha import dwadasottari
    navamsa_planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=9)
    if dwadasottari.applicability_check(navamsa_planet_positions): applicable_dhasas.append('dwadasottari')
    from jhora.horoscope.dhasa.graha import dwisatpathi
    if dwisatpathi.applicability_check(planet_positions): applicable_dhasas.append('dwisatpathi')
    dwadasamsa_planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=12)
    from jhora.horoscope.dhasa.graha import panchottari
    if panchottari.applicability_check(dwadasamsa_planet_positions): applicable_dhasas.append('panchottari')
    from jhora.horoscope.dhasa.graha import sataatbika
    if sataatbika.applicability_check(dob, tob, place): applicable_dhasas.append('satabdika')
    from jhora.horoscope.dhasa.graha import shastihayani
    if shastihayani.applicability_check(planet_positions): applicable_dhasas.append('shashtisama')
    """ TODO: To implement applicability for Shattrimsa Sama and Shodasottari dhasas
        Both involve understanding deva/pitri hora day/nigh time etc
    """
    return applicable_dhasas

'------ main -----------'
if __name__ == "__main__":
    dcf = 1; dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    print(applicability_check(dob, tob, place, divisional_chart_factor=dcf))
    