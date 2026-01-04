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
from collections import OrderedDict as Dict
from jhora import const, utils
from jhora.panchanga import drik


_dhasa_duration = 10; _dhasa_count = 10
year_duration = const.sidereal_year
human_life_span_for_dhasa = 100
dhasa_adhipathi_list = lambda lord: {(lord-i)%27:_dhasa_duration for i in range(_dhasa_count)}
def _next_adhipati(lord,dhasa_lords,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = dhasa_lords.index(lord)
    next_lord = dhasa_lords[(current + dirn) % len(dhasa_lords)]
    #print(dirn,lord,next_lord,dhasa_lords)
    return next_lord
def _antardhasa(dhasa_lord,antardhasa_option=1):
    dhasa_lords = [(dhasa_lord-i)%27 for i in range(_dhasa_count)]
    lord = dhasa_lord
    if antardhasa_option in [3,4]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords,dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_lords)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord,dhasa_lords,dirn)
    return _bhukthis
    
def _dhasa_progression(jd,place,divisional_chart_factor=1,chart_method=1,star_position_from_moon=1,
                       dhasa_starting_planet=1):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob=drik.Date(y,m,d); tob=(fh,0,0)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method)
    if dhasa_starting_planet in [*range(9)]:
        planet_long = planet_positions[dhasa_starting_planet+1][1][0]*30+planet_positions[dhasa_starting_planet+1][1][1]
    elif dhasa_starting_planet==const._ascendant_symbol:
        planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    elif dhasa_starting_planet.upper()=='M':
        mn = drik.maandi_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0]*30+mn[1]
    elif dhasa_starting_planet.upper()=='G':
        gl = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='B':
        gl = drik.bhrigu_bindhu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='I':
        gl = drik.indu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='P':
        gl = drik.pranapada_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='T':
        sp = sphuta.tri_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = sp[0]*30+sp[1]
    else:
        planet_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    if dhasa_starting_planet==1:
        planet_long += (star_position_from_moon-1)*one_star
    nak = int(planet_long / one_star)
    _dp = [(nak-i)%27 for i in range(_dhasa_count)]
    return _dp
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,chart_method=1,include_antardhasa=True,
                      star_position_from_moon=1,use_tribhagi_variation=False,
                      dhasa_starting_planet=1,antardhasa_option=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        NOTE: In JHora this option is disabled. JHora has seed_star option enabled, but shows no effect omn dhasa/bhukthi
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_dhasa
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_dhasa *= _tribhagi_factor
    jd = utils.julian_day_number(dob, tob)
    retval = []
    dhasa_progression = _dhasa_progression(jd, place, divisional_chart_factor,chart_method,star_position_from_moon, 
                                           dhasa_starting_planet)
    start_jd = jd
    for _ in range(_dhasa_cycles):
        for dhasa_lord in dhasa_progression:
            dhasa_duration = _dhasa_duration*_tribhagi_factor
            if include_antardhasa:
                bhukthis = _antardhasa(dhasa_lord, antardhasa_option)#[(dhasa_lord-i)%27 for i in range(_dhasa_count)]
                _bhukthi_duration = _dhasa_duration/len(bhukthis)
                for bhukthi_lord in bhukthis:
                    y,m,d,h = utils.jd_to_gregorian(start_jd)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    retval.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                    start_jd += _bhukthi_duration * year_duration
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                retval.append((dhasa_lord,dhasa_start,dhasa_duration))
                start_jd += dhasa_duration * year_duration
    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.saptharishi_nakshathra_test()
