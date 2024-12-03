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
def tri_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=mixed_dvf)
    gulika_long = gulika[0]*30+gulika[1]
    _tri_sphuta = (moon_long+asc_long+gulika_long)%360
    return drik.dasavarga_from_long(_tri_sphuta, divisional_chart_factor=mixed_dvf)
    
def tri_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
               chart_method=1,years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _tri_sphuta = (moon_long+asc_long+gulika_long)%360
    return drik.dasavarga_from_long(_tri_sphuta, divisional_chart_factor=divisional_chart_factor)
def chatur_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tri_sphuta= tri_sphuta_mixed_chart(dob, tob, place,varga_factor_1,chart_method_1,varga_factor_2,chart_method_2)
    _chatur_sphuta = (sun_long+_tri_sphuta[0]*30+_tri_sphuta[1])%360
    return drik.dasavarga_from_long(_chatur_sphuta, divisional_chart_factor=mixed_dvf)
def chatur_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
               chart_method=1,years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tri_sphuta= tri_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, chart_method,
                            years, months, sixty_hours)
    _chatur_sphuta = (sun_long+_tri_sphuta[0]*30+_tri_sphuta[1])%360
    return drik.dasavarga_from_long(_chatur_sphuta, divisional_chart_factor=divisional_chart_factor)
def pancha_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    _chatur_sphuta= chatur_sphuta_mixed_chart(dob, tob, place,varga_factor_1,chart_method_1,varga_factor_2,chart_method_2)
    _pancha_sphuta = (rahu_long+_chatur_sphuta[0]*30+_chatur_sphuta[1])%360
    return drik.dasavarga_from_long(_pancha_sphuta, divisional_chart_factor=mixed_dvf)    
def pancha_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
               chart_method=1,years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    _chatur_sphuta= chatur_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, chart_method,
                                  years, months, sixty_hours)
    _pancha_sphuta = (rahu_long+_chatur_sphuta[0]*30+_chatur_sphuta[1])%360
    return drik.dasavarga_from_long(_pancha_sphuta, divisional_chart_factor=divisional_chart_factor)
def prana_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=mixed_dvf)
    gulika_long = gulika[0]*30+gulika[1]
    _prana_long = (asc_long*5 + gulika_long) %360
    return drik.dasavarga_from_long(_prana_long, divisional_chart_factor=mixed_dvf)
def prana_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                 years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours)
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _prana_long = (asc_long*5 + gulika_long) %360
    return drik.dasavarga_from_long(_prana_long, divisional_chart_factor=divisional_chart_factor)
def deha_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=mixed_dvf)
    gulika_long = gulika[0]*30+gulika[1]
    _deha_long = (moon_long*8 + gulika_long) %360
    return drik.dasavarga_from_long(_deha_long, divisional_chart_factor=mixed_dvf)
def deha_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _deha_long = (moon_long*8 + gulika_long) %360
    return drik.dasavarga_from_long(_deha_long, divisional_chart_factor=divisional_chart_factor)
def mrityu_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=mixed_dvf)
    gulika_long = gulika[0]*30+gulika[1]
    _mrityu_long = (gulika_long*7 + sun_long) %360
    return drik.dasavarga_from_long(_mrityu_long, divisional_chart_factor=mixed_dvf)
def mrityu_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                  years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _mrityu_long = (gulika_long*7 + sun_long) %360
    return drik.dasavarga_from_long(_mrityu_long, divisional_chart_factor=divisional_chart_factor)
def sookshma_tri_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    _prana_long = prana_sphuta_mixed_chart(dob, tob, place,varga_factor_1,chart_method_1,varga_factor_2,chart_method_2)
    _deha_long = deha_sphuta_mixed_chart(dob, tob, place,varga_factor_1,chart_method_1,varga_factor_2,chart_method_2)
    _mrityu_long = mrityu_sphuta_mixed_chart(dob, tob, place,varga_factor_1,chart_method_1,varga_factor_2,chart_method_2)
    _sookshma_long = (_prana_long[0]*30+_prana_long[1] + _deha_long[0]*30+_deha_long[1] + _mrityu_long[0]*30+_mrityu_long[1]) %360
    return drik.dasavarga_from_long(_sookshma_long, divisional_chart_factor=mixed_dvf)
def sookshma_tri_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                        chart_method=1,years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    _prana_long = prana_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, chart_method,years, months, sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    _deha_long = deha_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor,chart_method, years, months, sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    _mrityu_long = mrityu_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, chart_method,years, months, sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    _sookshma_long = (_prana_long[0]*30+_prana_long[1] + _deha_long[0]*30+_deha_long[1] + _mrityu_long[0]*30+_mrityu_long[1]) %360
    return drik.dasavarga_from_long(_sookshma_long, divisional_chart_factor=divisional_chart_factor)
def beeja_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    venus_long = planet_positions[6][1][0]*30+planet_positions[6][1][1]
    _beeja_long = (sun_long + jupiter_long + venus_long)%360
    return drik.dasavarga_from_long(_beeja_long, divisional_chart_factor=mixed_dvf)
def beeja_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                 years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    venus_long = planet_positions[6][1][0]*30+planet_positions[6][1][1]
    _beeja_long = (sun_long + jupiter_long + venus_long)%360
    return drik.dasavarga_from_long(_beeja_long, divisional_chart_factor=divisional_chart_factor)
def kshetra_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    mars_long = planet_positions[3][1][0]*30+planet_positions[3][1][1]
    _kshetra_long = (moon_long + jupiter_long + mars_long)%360
    return drik.dasavarga_from_long(_kshetra_long, divisional_chart_factor=mixed_dvf)
def kshetra_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                   years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    mars_long = planet_positions[3][1][0]*30+planet_positions[3][1][1]
    _kshetra_long = (moon_long + jupiter_long + mars_long)%360
    return drik.dasavarga_from_long(_kshetra_long, divisional_chart_factor=divisional_chart_factor)
def tithi_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (moon_long - sun_long) %360
    return drik.dasavarga_from_long(_tithi_long, divisional_chart_factor=mixed_dvf)
def tithi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                 years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (moon_long - sun_long) %360
    return drik.dasavarga_from_long(_tithi_long, divisional_chart_factor=divisional_chart_factor)
def yoga_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                            add_yogi_longitude=False):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    yogi_long = 93+20/60 if add_yogi_longitude else 0
    _yoga_long = (moon_long + sun_long + yogi_long) %360
    return drik.dasavarga_from_long(_yoga_long, divisional_chart_factor=mixed_dvf)
def yoga_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                years=1,months=1,sixty_hours=1,add_yogi_longitude=False,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    yogi_long = 93+20/60 if add_yogi_longitude else 0
    _yoga_long = (moon_long + sun_long + yogi_long) %360
    return drik.dasavarga_from_long(_yoga_long, divisional_chart_factor=divisional_chart_factor)
def yogi_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    return yoga_sphuta_mixed_chart(dob, tob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2, 
                                   add_yogi_longitude=True)
def yogi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    return yoga_sphuta(dob,tob,place,ayanamsa_mode,divisional_chart_factor,chart_method,
                       years,months,sixty_hours,add_yogi_longitude=True,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
def avayogi_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    mixed_dvf = varga_factor_1*varga_factor_2
    yl = yogi_sphuta_mixed_chart(dob, tob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    ayl = (yl[0]*30+yl[1]+186+40/60)%360
    return drik.dasavarga_from_long(ayl, mixed_dvf)
def avayogi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                   years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    yl = yogi_sphuta(dob,tob,place,ayanamsa_mode,divisional_chart_factor,chart_method,years,months,sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    ayl = (yl[0]*30+yl[1]+186+40/60)%360
    return drik.dasavarga_from_long(ayl, divisional_chart_factor)
def rahu_tithi_sphuta_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    mixed_dvf = varga_factor_1*varga_factor_2
    planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (rahu_long - sun_long) %360
    return drik.dasavarga_from_long(_tithi_long, divisional_chart_factor=mixed_dvf)
def rahu_tithi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                      years=1,months=1,sixty_hours=1,base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        years=years,months=months, sixty_hours=sixty_hours,
                                        base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (rahu_long - sun_long) %360
    return drik.dasavarga_from_long(_tithi_long, divisional_chart_factor=divisional_chart_factor)
    #return _tithi_long
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    line_sep = '\n'
    yh,yl = yogi_sphuta(dob, tob, place)
    ystr = utils.resource_strings['yogi_sphuta_str']+' '+utils.resource_strings['raasi_str']+':'+\
            utils.RAASI_LIST[yh]+' '+utils.resource_strings['longitude_str']+':'+utils.to_dms(yl,is_lat_long='plong')
    ynak = drik.nakshatra_pada(yh*30+yl)
    ystr += line_sep+utils.resource_strings['yogi_sphuta_str']+' '+utils.resource_strings['nakshatra_str']+':'+ \
            utils.NAKSHATRA_LIST[ynak[0]-1]
    yogi_planet = [l for l,naks in const.nakshathra_lords.items() if ynak[0]-1 in naks][0]
    ystr += line_sep+utils.resource_strings['yogi_sphuta_str']+' '+utils.resource_strings['planet_str']+':'+ \
            utils.PLANET_NAMES[yogi_planet]
    sahayogi_planet = const._house_owners_list[yh]
    ystr += line_sep+utils.resource_strings['sahayogi_str']+' '+utils.resource_strings['planet_str']+':'+ \
            utils.PLANET_NAMES[sahayogi_planet]
    yh,yl = avayogi_sphuta(dob, tob, place)
    ynak = drik.nakshatra_pada(yh*30+yl)
    ystr += line_sep+utils.resource_strings['avayogi_sphuta_str']+' '+utils.resource_strings['raasi_str']+':'+\
            utils.RAASI_LIST[yh]+' '+utils.resource_strings['longitude_str']+':'+utils.to_dms(yl,is_lat_long='plong')
    ynak = drik.nakshatra_pada(yh*30+yl)
    ystr += line_sep+utils.resource_strings['avayogi_sphuta_str']+' '+utils.resource_strings['nakshatra_str']+':'+ \
            utils.NAKSHATRA_LIST[ynak[0]-1]
    yogi_planet = [l for l,naks in const.nakshathra_lords.items() if ynak[0]-1 in naks][0]
    ystr += line_sep+utils.resource_strings['avayogi_sphuta_str']+' '+utils.resource_strings['planet_str']+':'+ \
            utils.PLANET_NAMES[yogi_planet]
    print(ystr)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests.sphuta_tests()
