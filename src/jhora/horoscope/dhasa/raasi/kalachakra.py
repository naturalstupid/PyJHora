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
import numpy as np
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import house, charts
""" TODO: Dhasa Progression does not seem to match with JHora """
def _get_dhasa_progression(planet_longitude):
    nakshatra,paadham,_ = drik.nakshatra_pada(planet_longitude)
    nakshatra -= 1
    paadham -= 1
    kalachakra_index = 0
    if nakshatra in const.savya_stars_1:
        kalachakra_index = 0
    elif nakshatra in const.savya_stars_2:
        kalachakra_index = 1
    elif nakshatra in const.apasavya_stars_1:
        kalachakra_index = 2
    else:
        kalachakra_index = 3
    dhasa_progression = const.kalachakra_rasis[kalachakra_index][paadham]
    dhasa_paramayush = const.kalachakra_paramayush[kalachakra_index][paadham]
    dhasa_duration = [const.kalachakra_dhasa_duration[r] for r in dhasa_progression]
    one_star = (360.0/27)
    one_paadha = (360.0 / 108)
    nak_start_long = nakshatra*one_star + paadham * one_paadha
    nak_travel_fraction = (planet_longitude-nak_start_long)/one_paadha
    dhasa_duration_cumulative = np.cumsum(dhasa_duration)
    paramayush_completed = nak_travel_fraction * dhasa_paramayush
    dhasa_index_at_birth = next(x[0] for x in enumerate(dhasa_duration_cumulative) if x[1] > paramayush_completed)
    dhasa_remaining_at_birth = dhasa_duration_cumulative[dhasa_index_at_birth]-paramayush_completed
    kalachakra_index_next = kalachakra_index
    paadham_next = (paadham+1)%4
    if paadham==3:
        if kalachakra_index == 0:
            kalachakra_index_next = 1
        elif kalachakra_index == 1:
            kalachakra_index_next = 0
        elif kalachakra_index == 2:
            kalachakra_index_next = 3
        elif kalachakra_index == 3:
            kalachakra_index_next = 2
    dhasa_progression = dhasa_progression[dhasa_index_at_birth:]+const.kalachakra_rasis[kalachakra_index_next][paadham_next][:dhasa_index_at_birth]
    dhasa_duration = [const.kalachakra_dhasa_duration[r] for r in dhasa_progression]
    dhasa_duration[0] = dhasa_remaining_at_birth
    dhasa_periods = []
    for i,dp in enumerate(dhasa_progression):
        ad = antardhasa(dhasa_index_at_birth,i, dhasa_paramayush, kalachakra_index_next, paadham)
        """
            Temporary Fix if ad = empty list
        """
        if len(ad)==0: ad=[dhasa_progression,[const.kalachakra_dhasa_duration[r] for r in dhasa_progression]]
        dhasa_periods.append([dp,ad,dhasa_duration[i]])
    return dhasa_periods
def antardhasa(dhasa_index_at_birth,dp_index,paramayush,kc_index,paadham):
    dp_begin = kc_index*9*4+paadham*9+dhasa_index_at_birth+dp_index
    antardhasa_progression=const.kalachakra_rasis_list[dp_begin:dp_begin+9]
    antardhasa_duration = [const.kalachakra_dhasa_duration[r] for r in antardhasa_progression]
    """ TODO: handle if above is empty list [] """
    if len(antardhasa_duration)==0:
        return []
    dhasa_duration = antardhasa_duration[0]
    antardhasa_fraction = dhasa_duration/sum(antardhasa_duration)
    antardhasa_duration = [(ad * antardhasa_fraction) for ad in antardhasa_duration]
    return [antardhasa_progression,antardhasa_duration]
def kalachakra_dhasa(planet_longitude,jd,include_antardhasa=True):
    """
        Kalachara Dhasa calculation
        @param planet_longitude: Longitude of planet (default=moon) at the time of Date/time of birth as float
        @param dob: Date of birth as tuple (year,month,day)
        @return: list of [dhasa_rasi,dhasa_rasi_start_date, dhasa_rasi_end_date,[abtadhasa_rasis],dhasa_rasi_duration]
        Example: [[7, '1946-12-2', '1955-12-2', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 9], [8, '1955-12-2', '1964-12-2', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 9], ...]
    """
    dhasa_periods = _get_dhasa_progression(planet_longitude)
    if len(dhasa_periods)==0:
        return []
    dhasa_start_jd = jd
    dp_new = []
    for dp in dhasa_periods:
        ds,ad,dd = dp
        #print('kalachakra dhasa values ds,ad,dd',ds,ad,dd)
        if include_antardhasa:
            for b in range(len(ad[0])):
                bhukthi_lord = ad[0][b]; bhukthi_duration = ad[1][b] 
                y,m,d,h = utils.jd_to_gregorian(dhasa_start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dp_new.append([ds,bhukthi_lord,dhasa_start,round(bhukthi_duration,2)])
                dhasa_start_jd += bhukthi_duration*const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(dhasa_start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dp_new.append([ds,dhasa_start,round(dd,2)])
        dhasa_duration_in_days = dd*const.sidereal_year
        dhasa_start_jd += dhasa_duration_in_days
    dhasa_periods = dp_new[:]
    return dhasa_periods
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,dhasa_starting_planet=1,
                      include_antardhasa=True,star_position_from_moon=1):
    """
        returns kalachakra dhasa bhukthi
        @param dob = Date of Birth as drik.Date tuple
        @param tob = Time of birth as tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
        
    """
    jd = utils.julian_day_number(dob, tob)
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=divisional_chart_factor)
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
        gl = drik.bhrigu_bindhu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='I':
        gl = drik.indu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='P':
        gl = drik.pranapada_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='T':
        sp = sphuta.tri_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = sp[0]*30+sp[1]
    else:
        planet_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    if dhasa_starting_planet==1:
        one_star = (360 / 27.)        # 27 nakshatras span 360°
        planet_long += (star_position_from_moon-1)*one_star
    return kalachakra_dhasa(planet_long, jd,include_antardhasa=include_antardhasa)
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.kalachakra_dhasa_tests()
