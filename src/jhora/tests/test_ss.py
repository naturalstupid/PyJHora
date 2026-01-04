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
    unit tests for examples from the book
    Ancient Indian Astronomy - Planetary Positions and Eclipses
    By S. Balachandra Rao, Prof. Dept. of Mathematics, National College, Bangalore
"""
import swisseph as swe
from jhora import utils, const
from jhora.panchanga import drik, surya_sidhantha

place = drik.Place('Ujjain',23.1765, 75.7885,5.5)
dt = drik.Date(1997,3,21)
jd = swe.julday(dt[0],dt[1],dt[2],12.00)
def ss_mean_position_tests():
    chapter = 'Chapter 6.3.1 Examples '
    ka = surya_sidhantha.kali_ahargana(jd)
    print(chapter + 'Kali Ahargana',ka)
    _,sun_mean_long = surya_sidhantha._mean_solar_longitude(jd)
    sun_mean_long1 = surya_sidhantha._planet_mean_longitude(jd, place, const._SUN)
    print(chapter + 'Sun mean longitude - Expected: 334° 14’ 9" - Actual:',sun_mean_long,utils.to_dms(sun_mean_long1,is_lat_long='plong'))
    _,moon_mean_long = surya_sidhantha._mean_lunar_longitude(jd)
    moon_mean_long1 = surya_sidhantha._planet_mean_longitude(jd, place, const._MOON)
    print(chapter + 'Moon mean longitude - Expected: 117° 48’ 25" - Actual:',moon_mean_long,utils.to_dms(moon_mean_long1,is_lat_long='plong'))
    _,moon_apogee_mean_long = surya_sidhantha._mean_lunar_apogee_longitude(jd)
    print(chapter + 'Moon Apogee mean longitude - Expected: 131° 59’ 46" - Actual:',moon_apogee_mean_long)
    _,rahu_mean_long = surya_sidhantha._mean_rahu_longitude(jd)
    print(chapter + 'Rahu mean longitude - Expected: 158° 56’ 29" - Actual:',rahu_mean_long)
    _,ketu_mean_long = surya_sidhantha._mean_ketu_longitude(jd)
    print(chapter + 'Ketu mean longitude - Expected: 338° 56’ 29" - Actual:',ketu_mean_long)
def desantara_correction_tests():
    chapter = 'Chapter 6.3.1 Examples '
    bangalore = drik.Place('Bangalore',12.9716, 77.+35./60.,5.5)
    dc_sun = surya_sidhantha._desantara_correction(bangalore, const._SUN)
    sun_mean_long = surya_sidhantha._planet_mean_longitude(jd, place, const._SUN)
    sun_mean_long_after_dc = sun_mean_long + dc_sun
    print(chapter + 'desantara correction for Sun - Expected 0° 0’ 17.7" - Actual:',utils.to_dms(dc_sun,is_lat_long='plong',round_seconds_to_digits=1))    
    print(chapter + 'sun mean longitude after desantara correction - Expected:334° 13’ 51.3" - Actual:',utils.to_dms(sun_mean_long_after_dc,is_lat_long='plong',round_seconds_to_digits=1))

    dc_moon = surya_sidhantha._desantara_correction(bangalore, const._MOON)
    moon_mean_long = surya_sidhantha._planet_mean_longitude(jd, place, const._MOON)
    moon_mean_long_after_dc = moon_mean_long + dc_moon
    print(chapter + 'desantara correction for Moon - Expected 0° 3’ 57.0" - Actual:',utils.to_dms(dc_moon,is_lat_long='plong',round_seconds_to_digits=1))    
    print(chapter + 'Moon mean longitude after desantara correction - Expected:117° 44’ 28.0" - Actual:',utils.to_dms(moon_mean_long_after_dc,is_lat_long='plong',round_seconds_to_digits=1))

    dc_rahu = surya_sidhantha._desantara_correction(bangalore, const._RAHU)
    rahu_mean_long = surya_sidhantha._planet_mean_longitude(jd, place, const._RAHU)
    rahu_mean_long_after_dc = rahu_mean_long + dc_rahu
    print(chapter + 'desantara correction for Rahu - Expected 0° 0’ 1" - Actual:',utils.to_dms(dc_rahu,is_lat_long='plong'))    
    print(chapter + 'Rahu mean longitude after desantara correction - Expected:158° 56’ 30" - Actual:',utils.to_dms(rahu_mean_long_after_dc,is_lat_long='plong'))
def tamil_date_test():
    dt = drik.Date(2001,7,10)
    jd = swe.julday(dt[0],dt[1],dt[2],23.43)
    place = drik.Place('Ujjain',23.1765, 75.7885,5.5)
    tm,td = drik.tamil_solar_month_and_date(dt, place)
    tithi = drik.tithi(jd, place)
    print('tamil month',tm,'tamil day',td,'tithi',tithi[0])
def ss_true_position_sun_tests():
    chapter = 'Chapter 6.3.1 Examples '
    bangalore = drik.Place('Bangalore',12.9716, 77.+35./60.,5.5)
    dc_sun = surya_sidhantha._desantara_correction(bangalore, const._SUN)
    sun_mean_long = surya_sidhantha._planet_mean_longitude(jd, place, const._SUN)
    sun_mean_long_after_dc = sun_mean_long + dc_sun
    sun_mandaphala = surya_sidhantha._mandaphala_planet(jd, const._SUN, sun_mean_long_after_dc)
    print('Sun Mandaphala Expected:2° 7’ 13" - Actual: ',utils.to_dms(sun_mandaphala,is_lat_long='plong'))
    sun_long_before_bhujantara = sun_mean_long_after_dc+sun_mandaphala
    print('Sun longitude before Bhujantara Expected:336° 21’ 4" - Actual:',utils.to_dms(sun_long_before_bhujantara, is_lat_long='plong'))
    sun_bujantara = surya_sidhantha.bhujantara_correction(const._SUN, sun_mandaphala)
    print('Sun Bhujantara Expected:0° 0’ 21" - Actual: ',utils.to_dms(sun_bujantara,is_lat_long='plong'))
    sun_true_long = surya_sidhantha._planet_true_longitude(jd, place,const._SUN, sun_mean_long_after_dc)
    print('Sun True Longitude after Bhujantara Expected:336° 21’ 04" - Actual:',utils.to_dms(sun_true_long, is_lat_long='plong', round_seconds_to_digits=None))
def ss_true_position_moon_tests():
    chapter = 'Chapter 6.3.1 (ii) Examples '
    bangalore = drik.Place('Bangalore',12.9716, 77.+35./60.,5.5)
    dc_moon = surya_sidhantha._desantara_correction(bangalore, const._MOON)
    moon_mean_long = surya_sidhantha._planet_mean_longitude(jd, bangalore, const._MOON)
    moon_mean_long_after_dc = moon_mean_long + dc_moon
    moon_mandaphala = surya_sidhantha._mandaphala_planet(jd, const._MOON, moon_mean_long_after_dc)
    print('Moon Mandaphala Expected:1° 15’ 3" - Actual: ',utils.to_dms(moon_mandaphala,is_lat_long='plong'))
    moon_long_before_bhujantara = moon_mean_long_after_dc+moon_mandaphala
    print('Moon longitude before Bhujantara Expected:118° 59’ 31" - Actual:',utils.to_dms(moon_long_before_bhujantara, is_lat_long='plong'))
    moon_bujantara = surya_sidhantha.bhujantara_correction(const._MOON, moon_mandaphala)
    print('Moon Bhujantara Expected:0° 5’ 3" - Actual: ',utils.to_dms(moon_bujantara,is_lat_long='plong'))
    moon_true_long = surya_sidhantha._planet_true_longitude(jd,bangalore, const._MOON, moon_mean_long_after_dc)
    print('Moon True Longitude after Bhujantara Expected:119° 4’ 34" - Actual:',utils.to_dms(moon_true_long, is_lat_long='plong', round_seconds_to_digits=None))
def ss_true_position_planet_tests(planet,planet_expected_mean_longitude,planet_expected_true_longitude):
    dt = drik.Date(1991,3,22)
    jd = swe.julday(dt[0],dt[1],dt[2],12.00)
    chapter = 'Chapter 12 Examples '
    bangalore = drik.Place('Bangalore',12.9716, 77.+35./60.,5.5)
    planet_mean_longitude = surya_sidhantha._planet_mean_longitude(jd, place, planet)
    print('Planet:',planet,' Mean Longitude Expected:',planet_expected_mean_longitude,' - Actual:',utils.to_dms(planet_mean_longitude, is_lat_long='plong'))
    planet_true_longitude = surya_sidhantha._planet_true_longitude(jd, place,planet, planet_mean_longitude)
    print('Planet:',planet,' True Longitude Expected:',planet_expected_true_longitude,' - Actual:',utils.to_dms(planet_true_longitude, is_lat_long='plong'))
def ss_planet_mandaphala_tests(planet,planet_mandaphala_expected):
    dt = drik.Date(1991,3,22)
    jd = swe.julday(dt[0],dt[1],dt[2],12.00)
    chapter = 'Chapter 12 Examples '
    bangalore = drik.Place('Bangalore',12.9716, 77.+35./60.,5.5)
    planet_mean_longitude = surya_sidhantha._planet_mean_longitude(jd, place, planet)
    planet_mandaphala = surya_sidhantha._mandaphala_planet(jd, planet, planet_mean_longitude)
    print('Planet:',planet,' Mandaphala Expected:',planet_mandaphala_expected,' - Actual: ',utils.to_dms(planet_mandaphala,is_lat_long='plong'))
        
if __name__ == "__main__":
    ss_mean_position_tests()
    desantara_correction_tests()
    ss_true_position_sun_tests()
    ss_true_position_moon_tests()
    ss_true_position_planet_tests(const._SATURN,'272° 49’ 4"','273° 47’ 45"')
    ss_planet_mandaphala_tests(const._JUPITER,'4° 32’ 59"')