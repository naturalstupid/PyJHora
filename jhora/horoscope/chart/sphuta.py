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
from jhora.panchanga import drik
from jhora import const,utils
from jhora.horoscope.chart import house, charts

def tri_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _tri_sphuta = (moon_long+asc_long+gulika_long)%360
    return drik.dasavarga_from_long(_tri_sphuta, divisional_chart_factor=divisional_chart_factor)
    #return _tri_sphuta
def chatur_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tri_sphuta= tri_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _chatur_sphuta = (sun_long+_tri_sphuta[0]*30+_tri_sphuta[1])%360
    return drik.dasavarga_from_long(_chatur_sphuta, divisional_chart_factor=divisional_chart_factor)
    #return _chatur_sphuta
def pancha_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    _chatur_sphuta= chatur_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _pancha_sphuta = (rahu_long+_chatur_sphuta[0]*30+_chatur_sphuta[1])%360
    return drik.dasavarga_from_long(_pancha_sphuta, divisional_chart_factor=divisional_chart_factor)
    #return _pancha_sphuta
def prana_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _prana_long = (asc_long*5 + gulika_long) %360
    return drik.dasavarga_from_long(_prana_long, divisional_chart_factor=divisional_chart_factor)
    #return _prana_long
def deha_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _deha_long = (moon_long*8 + gulika_long) %360
    return drik.dasavarga_from_long(_deha_long, divisional_chart_factor=divisional_chart_factor)
    #return _deha_long
def mrityu_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _mrityu_long = (gulika_long*7 + sun_long) %360
    return drik.dasavarga_from_long(_mrityu_long, divisional_chart_factor=divisional_chart_factor)
    #return _mrityu_long
def sookshma_tri_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    _prana_long = prana_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _deha_long = deha_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _mrityu_long = mrityu_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _sookshma_long = (_prana_long[0]*30+_prana_long[1] + _deha_long[0]*30+_deha_long[1] + _mrityu_long[0]*30+_mrityu_long[1]) %360
    return drik.dasavarga_from_long(_sookshma_long, divisional_chart_factor=divisional_chart_factor)
    #return _sookshma_long
def beeja_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    venus_long = planet_positions[6][1][0]*30+planet_positions[6][1][1]
    _beeja_long = (sun_long + jupiter_long + venus_long)%360
    return drik.dasavarga_from_long(_beeja_long, divisional_chart_factor=divisional_chart_factor)
    #return _beeja_long
def kshetra_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    mars_long = planet_positions[3][1][0]*30+planet_positions[3][1][1]
    _kshetra_long = (moon_long + jupiter_long + mars_long)%360
    return drik.dasavarga_from_long(_kshetra_long, divisional_chart_factor=divisional_chart_factor)
    #return _kshetra_long
def tithi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (moon_long - sun_long) %360
    return drik.dasavarga_from_long(_tithi_long, divisional_chart_factor=divisional_chart_factor)
    #return _tithi_long
def yoga_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                years=1,months=1,sixty_hours=1,add_yogi_longitude=False):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    yogi_long = 93+20/60 if add_yogi_longitude else 0
    _yoga_long = (moon_long + sun_long + yogi_long) %360
    return drik.dasavarga_from_long(_yoga_long, divisional_chart_factor=divisional_chart_factor)
def yogi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                years=1,months=1,sixty_hours=1):
    return yoga_sphuta(dob,tob,place,ayanamsa_mode,divisional_chart_factor,years,months,sixty_hours,add_yogi_longitude=True)
def avayogi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    yl = yogi_sphuta(dob,tob,place,ayanamsa_mode,divisional_chart_factor,years,months,sixty_hours)
    ayl = (yl[0]*30+yl[1]+186+40/60)%360
    return drik.dasavarga_from_long(ayl, divisional_chart_factor)
def rahu_tithi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (rahu_long - sun_long) %360
    return drik.dasavarga_from_long(_tithi_long, divisional_chart_factor=divisional_chart_factor)
    #return _tithi_long
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    print(tri_sphuta(dob, tob, place))
    exit()
    from jhora.tests import pvr_tests
    pvr_tests.sphuta_tests()
