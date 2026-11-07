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
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
"""
    Saham calculation
    saham has a formula that looks like A – B + C. What this means is that we take the
    longitudes of A, B and C and find (A – B + C). This is equivalent to finding how far
    A is from B and then taking the same distance from C. However, if C is not between
    B and A (i.e. we start from B and go zodiacally till we meet A and we do not find C
    on the way), then we add 30º to the value evaluated above.
    NOTE : For 30 degree correction rule "C" is always lagna longitude for the function
    _is_C_between_B_to_A(a_long, b_long, LAGNA_LONG) (donot use c_long)
    NOTE: Saham calculations use standard house owners - instead of strength based calculations from house module.
    (Using strength based owner calculations results in deviation from Jagannatha hora values)
    To use strength based owner calculations set const.use_default_house_owner_for_saham_calculation=False
    Along with this one can set - depending on choice
        const.scorpio_owner_for_dhasa_calculations = None # Or MARS_ID Or KETU_ID
        const.aquarius_owner_for_dhasa_calculations = None # Or SATURN_ID or Rahu_ID

"""
_saham_short = utils._sahams.keys()

saham_longitude = lambda pp,p:pp[p][1][0]*30+pp[p][1][1]
def lagna_longitude(jd_at_dob, place):
    asc = drik.ascendant(jd_at_dob, place)
    return asc[0] * 30 + asc[1]
def _ascendant_house(jd_at_dob, place):
    return drik.ascendant(jd_at_dob, place)[0]
sun_longitude = lambda pp: saham_longitude(pp,const.SUN_ID)
moon_longitude = lambda pp: saham_longitude(pp,const.MOON_ID)
mars_longitude = lambda pp: saham_longitude(pp,const.MARS_ID)
mercury_longitude = lambda pp: saham_longitude(pp,const.MERCURY_ID)
jupiter_longitude = lambda pp: saham_longitude(pp,const.JUPITER_ID)
venus_longitude = lambda pp: saham_longitude(pp,const.VENUS_ID)
saturn_longitude = lambda pp: saham_longitude(pp,const.SATURN_ID)

def is_night_time_birth(jd_at_dob,place):
    _,_,_,fh = utils.jd_to_gregorian(jd_at_dob)
    sunrise_hours = drik.sunrise(jd_at_dob,place)[0]
    sunset_hours = drik.sunset(jd_at_dob,place)[0]
    return fh < sunrise_hours or fh > sunset_hours
# Saham Meaning Formula
def punya_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 1 Punya Fortune/good deeds Moon – Sun + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    moon_long = moon_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    punya_sagam_long = moon_long - sun_long + lagna_long
    if not _is_C_between_B_to_A(moon_long,sun_long,lagna_long):
        punya_sagam_long += 30
    if night_time_birth:
        punya_sagam_long = sun_long - moon_long + lagna_long
        if not _is_C_between_B_to_A(sun_long,moon_long,lagna_long):
            punya_sagam_long += 30
    return utils.norm360(punya_sagam_long + dhasa_progression_correction)
    
def vidya_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 2 Vidya Education Sun – Moon + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    sun_long = sun_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    vidya_sagam_long = sun_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(sun_long,moon_long,lagna_long):
        vidya_sagam_long += 30
    if night_time_birth:
        vidya_sagam_long = moon_long - sun_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,sun_long,lagna_long):
            vidya_sagam_long += 30
    return utils.norm360(vidya_sagam_long + dhasa_progression_correction)
    
def yasas_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 3 Yasas Fame Jupiter – PunyaSaham + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    jupiter_long = jupiter_longitude(planet_positions)
    punya_long = punya_saham(jd_at_dob, place)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    yasas_sagam_long = jupiter_long - punya_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,punya_long,lagna_long):
        yasas_sagam_long += 30
    if night_time_birth:
        yasas_sagam_long = punya_long - jupiter_long + lagna_long
        if not _is_C_between_B_to_A(punya_long,jupiter_long,lagna_long):
            yasas_sagam_long += 30
    return utils.norm360(yasas_sagam_long + dhasa_progression_correction)
    
def mitra_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 4 Mitra Friend Jupiter – PunyaSaham + Venus
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    jupiter_long = jupiter_longitude(planet_positions)
    punya_long = punya_saham(jd_at_dob, place)
    venus_long = venus_longitude(planet_positions)
    " A - B + C "
    mitra_sagam_long = jupiter_long - punya_long + venus_long
    if not _is_C_between_B_to_A(jupiter_long,punya_long,venus_long):
        mitra_sagam_long += 30
    if night_time_birth:
        mitra_sagam_long = punya_long - jupiter_long + venus_long
        if not _is_C_between_B_to_A(punya_long,jupiter_long,venus_long):
            mitra_sagam_long += 30
    return utils.norm360(mitra_sagam_long + dhasa_progression_correction)
    
def mahatmaya_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 5 Mahatmya Greatness PunyaSaham – Mars + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    punya_long = punya_saham(jd_at_dob, place)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    mahatmaya_sagam_long = punya_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(punya_long,mars_long,lagna_long):
        mahatmaya_sagam_long += 30
    if night_time_birth:
        mahatmaya_sagam_long = mars_long - punya_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,punya_long,lagna_long):
            mahatmaya_sagam_long += 30
    return utils.norm360(mahatmaya_sagam_long + dhasa_progression_correction)
    
def asha_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 6 Asha Desires Saturn – Mars + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    saturn_long = saturn_longitude(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    asha_sagam_long = saturn_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,mars_long,lagna_long):
        asha_sagam_long += 30
    if night_time_birth:
        asha_sagam_long = mars_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,saturn_long,lagna_long):
            asha_sagam_long += 30
    return utils.norm360(asha_sagam_long + dhasa_progression_correction)
    
def samartha_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 7 Samartha Enterprise/ability    Mars – Lagna Lord + Lagna (Jupiter – Mars + Lagna, if Mars owns lagna)
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    mars_long = mars_longitude(planet_positions)
    lagna_house = _ascendant_house(jd_at_dob, place)
    lagna_lord = ( const.house_owners[lagna_house] if const.use_default_house_owner_for_saham_calculation 
                   else house.house_owner_from_planet_positions(planet_positions, lagna_house) )
    if lagna_lord == const.MARS_ID:
        #print('Lagna Lord is Mars. So Jupiter is used as Lagna Lord in saham equation')
        lagna_lord = const.JUPITER_ID # Jupiter
        " This is done to swap ABC equation "
        night_time_birth = not night_time_birth
    lagna_lord_long = saham_longitude(planet_positions,lagna_lord)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    samartha_sagam_long = mars_long - lagna_lord_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,lagna_lord_long,lagna_long):
        samartha_sagam_long += 30
    if night_time_birth:
        samartha_sagam_long = lagna_lord_long - mars_long + lagna_long
        if not _is_C_between_B_to_A(lagna_lord_long,mars_long,lagna_long):
            samartha_sagam_long += 30
    return utils.norm360(samartha_sagam_long + dhasa_progression_correction)
    
def bhratri_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 8 Bhratri Brothers Jupiter – Saturn + Lagna (same for day & night)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    jupiter_long = jupiter_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    bhratri_sagam_long = jupiter_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,saturn_long,lagna_long):
        bhratri_sagam_long += 30
    return utils.norm360(bhratri_sagam_long + dhasa_progression_correction)
    
def gaurava_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    """
    Calculates Gaurava Saham using the correct planet mappings to match JHora,
    ensuring parameters flow perfectly into the updated _is_C_between_B_to_A function.
    """
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    
    jupiter_long = jupiter_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    
    if not night_time_birth:
        # Day Formula: Sun - Moon + Jupiter
        # A = Sun, B = Moon, C = Jupiter
        a, b, c = sun_long, moon_long, jupiter_long
    else:
        # Night Formula: Moon - Sun + Jupiter
        # A = Moon, B = Sun, C = Jupiter
        a, b, c = moon_long, sun_long, jupiter_long

    # Execute standard Saham Math: A - B + C
    gaurava_sagam_long = a - b + c
    
    # Use your fixed _is_C_between_B_to_A function seamlessly
    if not _is_C_between_B_to_A(a, b, c):
        gaurava_sagam_long += 30.0
        
    return utils.norm360(gaurava_sagam_long + dhasa_progression_correction)

    
def pithri_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    """
        TODO: JHora book says jupiter-moon+sun
        Internet says: sun-moon+jupiter - which is right. We follow JHora book - but does not match with JHora s/w.
    """
    # 10 Pitri Father Saturn – Sun + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    saturn_long = saturn_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    pithri_sagam_long = saturn_long - sun_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,sun_long,lagna_long):
        pithri_sagam_long += 30
    if night_time_birth:
        pithri_sagam_long = sun_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(sun_long,saturn_long,lagna_long):
            pithri_sagam_long += 30
    return utils.norm360(pithri_sagam_long + dhasa_progression_correction)
    
def rajya_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    """
        TODO: JHora book says jupiter-moon+sun
        Internet says: sun-moon+jupiter - which is right. We follow JHora book - but does not match with JHora s/w.
    """
# 11 Rajya Kingdom Saturn – Sun + Lagna
    return pithri_saham(jd_at_dob, place, dhasa_progression_correction)
def maathri_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 12 Matri Mother Moon – Venus + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    moon_long = moon_longitude(planet_positions)
    venus_long = venus_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    maathri_sagam_long = moon_long - venus_long + lagna_long
    if not _is_C_between_B_to_A(moon_long,venus_long,lagna_long):
        maathri_sagam_long += 30
    if night_time_birth:
        maathri_sagam_long = venus_long - moon_long + lagna_long
        if not _is_C_between_B_to_A(venus_long,moon_long,lagna_long):
            maathri_sagam_long += 30
    return utils.norm360(maathri_sagam_long + dhasa_progression_correction)
    
def puthra_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 13 Putra Children Jupiter – Moon + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    jupiter_long = jupiter_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    puthra_sagam_long = jupiter_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,moon_long,lagna_long):
        puthra_sagam_long += 30
    if night_time_birth:
        puthra_sagam_long = moon_long - jupiter_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,jupiter_long,lagna_long):
            puthra_sagam_long += 30
    return utils.norm360(puthra_sagam_long + dhasa_progression_correction)
    
def jeeva_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 14 Jeeva Life Saturn – Jupiter + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    saturn_long = saturn_longitude(planet_positions)
    jupiter_long = jupiter_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    jeeva_sagam_long = saturn_long - jupiter_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,jupiter_long,lagna_long):
        jeeva_sagam_long += 30
    if night_time_birth:
        jeeva_sagam_long = jupiter_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(jupiter_long,saturn_long,lagna_long):
            jeeva_sagam_long += 30
    return utils.norm360(jeeva_sagam_long + dhasa_progression_correction)
    
def karma_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 15 Karma Action (work) Mars – Mercury + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    mars_long = mars_longitude(planet_positions)
    mercury_long = mercury_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    karma_sagam_long = mars_long - mercury_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,mercury_long,lagna_long):
        karma_sagam_long += 30
    if night_time_birth:
        karma_sagam_long = mercury_long - mars_long + lagna_long
        if not _is_C_between_B_to_A(mercury_long,mars_long,lagna_long):
            karma_sagam_long += 30
    return utils.norm360(karma_sagam_long + dhasa_progression_correction)
    
def roga_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 16 Roga Disease Lagna – Moon + Lagna (Same for night/day)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    roga_sagam_long = lagna_long - moon_long + lagna_long
    return utils.norm360(roga_sagam_long + dhasa_progression_correction)
    
def roga_saham_1(jd_at_dob, place, dhasa_progression_correction = 0.0):
# 16 Roga Disease - Another Version -  Saturn – Moon + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    saturn_long = saturn_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    roga_sagam_long = saturn_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,moon_long,lagna_long):
        roga_sagam_long += 30
    if night_time_birth:
        roga_sagam_long = moon_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,saturn_long,lagna_long):
            roga_sagam_long += 30
    return utils.norm360(roga_sagam_long + dhasa_progression_correction)
    
def kali_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 17 Kali Great misfortune Jupiter – Mars + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    jupiter_long = jupiter_longitude(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    kali_sagam_long = jupiter_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,mars_long,lagna_long):
        kali_sagam_long += 30
    if night_time_birth:
        kali_sagam_long = mars_long - jupiter_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,jupiter_long,lagna_long):
            kali_sagam_long += 30
    return utils.norm360(kali_sagam_long + dhasa_progression_correction)
    
def sastra_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    # 18 Sastra Sciences Jupiter - Saturn + Mercury
    # Correction check uses Lagna, not Mercury.

    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    jupiter_long = jupiter_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    mercury_long = mercury_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)

    if not night_time_birth:
        a, b, x = jupiter_long, saturn_long, mercury_long
    else:
        a, b, x = saturn_long, jupiter_long, mercury_long

    sastra_sagam_long = a - b + x

    # Tajaka correction: C is always Lagna longitude.
    if not _is_C_between_B_to_A(a, b, lagna_long):
        sastra_sagam_long += 30.0

    return utils.norm360(sastra_sagam_long + dhasa_progression_correction)
    
def bandhu_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 19 Bandhu Relatives Mercury – Moon + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    mercury_long = mercury_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    bandhu_sagam_long = mercury_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(mercury_long,moon_long,lagna_long):
        bandhu_sagam_long += 30
    if night_time_birth:
        bandhu_sagam_long = moon_long - mercury_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,mercury_long,lagna_long):
            bandhu_sagam_long += 30
    return utils.norm360(bandhu_sagam_long + dhasa_progression_correction)
    
def mrithyu_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 20 Mrityu Death 8th house – Moon + Lagna (same for day & night)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    lagna_long = lagna_longitude(jd_at_dob, place)
    eigth_house_long = lagna_long + const.HOUSE_8*30
    moon_long = moon_longitude(planet_positions)
    " A - B + C "
    mrithyu_sagam_long = eigth_house_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(eigth_house_long,moon_long,lagna_long):
        mrithyu_sagam_long += 30
    return utils.norm360(mrithyu_sagam_long + dhasa_progression_correction)
    
def paradesa_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 21 Paradesa Foreign countries 9th house – 9th lord + Lagna (same for day & night)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    asc_house = _ascendant_house(jd_at_dob, place)
    ninth_house = (asc_house+const.HOUSE_9)%12
    ninth_lord = ( const.house_owners[ninth_house] if const.use_default_house_owner_for_saham_calculation 
                   else house.house_owner_from_planet_positions(planet_positions, ninth_house) )
    long_asc_house = lagna_longitude(jd_at_dob, place)
    long_ninth_house = long_asc_house+const.HOUSE_9*30.0
    long_ninth_lord = saham_longitude(planet_positions,ninth_lord)
    " A - B + C "
    paradesa_saham_long = (long_ninth_house - long_ninth_lord + long_asc_house)
    if not _is_C_between_B_to_A(long_ninth_house,long_ninth_lord,long_asc_house):
        paradesa_saham_long += 30
    return utils.norm360(paradesa_saham_long + dhasa_progression_correction)
    
def artha_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 22 Artha Money 2nd house – 2nd lord + Lagna (same for day & night)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    asc_house = _ascendant_house(jd_at_dob, place)
    second_house = (asc_house+const.HOUSE_2)%12
    second_lord = ( const.house_owners[second_house] if const.use_default_house_owner_for_saham_calculation 
                   else house.house_owner_from_planet_positions(planet_positions, second_house) )
    long_asc_house = lagna_longitude(jd_at_dob, place)
    long_second_house = long_asc_house+30.0
    long_second_lord = planet_positions[second_lord][1][0]*30+planet_positions[second_lord][1][1]
    " A - B + C "
    artha_saham_long = (long_second_house - long_second_lord + long_asc_house)
    if not _is_C_between_B_to_A(long_second_house,long_second_lord,long_asc_house):
        artha_saham_long += 30
    return utils.norm360(artha_saham_long + dhasa_progression_correction)
    
def paradara_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 23 Paradara Adultery Venus – Sun + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    venus_long = venus_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    paradara_sagam_long = venus_long - sun_long + lagna_long
    if not _is_C_between_B_to_A(venus_long,sun_long,lagna_long):
        paradara_sagam_long += 30
    if night_time_birth:
        paradara_sagam_long = sun_long - venus_long + lagna_long
        if not _is_C_between_B_to_A(sun_long,venus_long,lagna_long):
            paradara_sagam_long += 30
    return utils.norm360(paradara_sagam_long + dhasa_progression_correction)
    
def vanika_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 24 Vanik Commerce Moon – Mercury + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    moon_long = moon_longitude(planet_positions) #345-14 11-15-14
    mercury_long = mercury_longitude(planet_positions) # 311-28 - 10-11-28
    lagna_long = lagna_longitude(jd_at_dob, place) # 280-50 - 9-10-50
    " A - B + C "
    vanika_sagam_long = moon_long - mercury_long + lagna_long
    if not _is_C_between_B_to_A(moon_long,mercury_long,lagna_long):
        vanika_sagam_long += 30
    if night_time_birth:
        vanika_sagam_long = mercury_long - moon_long + lagna_long
        if not _is_C_between_B_to_A(mercury_long,moon_long,lagna_long):
            vanika_sagam_long += 30
    return utils.norm360(vanika_sagam_long + dhasa_progression_correction)
    
def karyasiddhi_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    # 25 Karyasiddhi Success in endeavours
    #
    # Classical Tajaka:
    # Day:   Saturn - Sun  + Lord of Sun sign
    # Night: Saturn - Moon + Lord of Moon sign
    #
    # IMPORTANT:
    # Formula additive term X is the luminary sign lord.
    # But the +30 correction check uses Lagna longitude.

    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)

    if not night_time_birth:
        b_id = const.SUN_ID
        b_long = sun_longitude(planet_positions)
    else:
        b_id = const.MOON_ID
        b_long = moon_longitude(planet_positions)

    sign_of_b = planet_positions[b_id][1][0]
    lord_of_b_sign = ( const.house_owners[sign_of_b] if const.use_default_house_owner_for_saham_calculation 
                   else house.house_owner_from_planet_positions(planet_positions, sign_of_b) )
    sign_lord_long = saham_longitude(planet_positions, lord_of_b_sign)

    a, b, x = saturn_long, b_long, sign_lord_long

    karyasiddhi_sagam_long = a - b + x

    # Tajaka correction: C is always Lagna longitude.
    if not _is_C_between_B_to_A(a, b, lagna_long):
        karyasiddhi_sagam_long += 30.0

    return utils.norm360(karyasiddhi_sagam_long + dhasa_progression_correction)
    
def vivaha_saham_from_jd_place(jd_at_dob, place):
    return vivaha_saham(jd_at_dob, place)
def vivaha_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 26 Vivaha Marriage Venus – Saturn + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    venus_long = venus_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    vivaha_saham_long = venus_long - saturn_long + lagna_long 
    if not _is_C_between_B_to_A(venus_long,saturn_long,lagna_long):
        vivaha_saham_long += 30
    if night_time_birth:
        vivaha_saham_long = saturn_long - venus_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,venus_long,lagna_long):
            vivaha_saham_long += 30
    return utils.norm360(vivaha_saham_long + dhasa_progression_correction)
    
def santapa_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    # 27 Santapa Sadness Saturn - Moon + 6th house
    # Correction check uses Lagna, not 6th house.

    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)

    saturn_long = saturn_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    sixth_house_long = lagna_long + const.HOUSE_6 * 30.0

    if not night_time_birth:
        a, b, x = saturn_long, moon_long, sixth_house_long
    else:
        a, b, x = moon_long, saturn_long, sixth_house_long

    santapa_saham_long = a - b + x

    # Tajaka correction: C is always Lagna longitude.
    if not _is_C_between_B_to_A(a, b, lagna_long):
        santapa_saham_long += 30.0

    return utils.norm360(santapa_saham_long + dhasa_progression_correction)
    
def sraddha_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 28 Sraddha Devotion/sincerity Venus – Mars + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    venus_long = venus_longitude(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    sraddha_sagam_long = venus_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(venus_long,mars_long,lagna_long):
        sraddha_sagam_long += 30
    if night_time_birth:
        sraddha_sagam_long = mars_long - venus_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,venus_long,lagna_long):
            sraddha_sagam_long += 30
    return utils.norm360(sraddha_sagam_long + dhasa_progression_correction)
    
def preethi_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    # 29 Preeti Love / attachment
    # Formula: Sastra Saham - Punya Saham + Lagna
    # Here X is Lagna, so the correction point is also Lagna.

    night_time_birth = is_night_time_birth(jd_at_dob, place)

    sastra_long = sastra_saham(jd_at_dob, place)
    punya_long = punya_saham(jd_at_dob, place)
    lagna_long = lagna_longitude(jd_at_dob, place)

    if not night_time_birth:
        a, b, x = sastra_long, punya_long, lagna_long
    else:
        a, b, x = punya_long, sastra_long, lagna_long

    preethi_sagam_long = a - b + x

    # Tajaka correction: C is always Lagna longitude.
    if not _is_C_between_B_to_A(a, b, lagna_long):
        preethi_sagam_long += 30.0

    return utils.norm360(preethi_sagam_long + dhasa_progression_correction)
    
def jadya_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 30 Jadya Chronic disease Mars – Saturn + Mercury
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    mars_long = mars_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    mercury_long = mercury_longitude(planet_positions)
    " A - B + C "
    jadya_sagam_long = mars_long - saturn_long + mercury_long
    if not _is_C_between_B_to_A(mars_long,saturn_long,mercury_long):
        jadya_sagam_long += 30
    if night_time_birth:
        jadya_sagam_long = saturn_long - mars_long + mercury_long
        if not _is_C_between_B_to_A(saturn_long,mars_long,mercury_long):
            jadya_sagam_long += 30
        jadya_sagam_long %= 360
    return utils.norm360(jadya_sagam_long + dhasa_progression_correction)
    
def vyaapaara_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 31 Vyapara Business Mars – Saturn + Lagna (same for day & night)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    mars_long = mars_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    vyaapaara_sagam_long = mars_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,saturn_long,lagna_long):
        vyaapaara_sagam_long += 30
    return utils.norm360(vyaapaara_sagam_long + dhasa_progression_correction)
    
def sathru_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 32 Satru Enemy Mars – Saturn + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    mars_long = mars_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    sathru_sagam_long = mars_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,saturn_long,lagna_long):
        sathru_sagam_long += 30
    if night_time_birth:
        sathru_sagam_long = saturn_long - mars_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,mars_long,lagna_long):
            sathru_sagam_long += 30
    return utils.norm360(sathru_sagam_long + dhasa_progression_correction)
    
def jalapatna_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 33 Jalapatana Crossing an ocean Cancer 15º– Saturn + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    cancer_long = 105.0
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    jalapatna_sagam_long = cancer_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(cancer_long,saturn_long,lagna_long):
        jalapatna_sagam_long += 30
    if night_time_birth:
        jalapatna_sagam_long = saturn_long - cancer_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,cancer_long,lagna_long):
            jalapatna_sagam_long += 30
    return utils.norm360(jalapatna_sagam_long + dhasa_progression_correction)
    
def bandhana_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 34 Bandhana Imprisonment PunyaSaham – Saturn + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    punya_long = punya_saham(jd_at_dob, place)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    bandhana_sagam_long = punya_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(punya_long,saturn_long,lagna_long):
        bandhana_sagam_long += 30
    if night_time_birth:
        bandhana_sagam_long = saturn_long - punya_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,punya_long,lagna_long):
            bandhana_sagam_long += 30
    return utils.norm360(bandhana_sagam_long + dhasa_progression_correction)
    
def apamrithyu_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
# 35 Apamrityu Bad death 8th house – Mars + Lagna
    night_time_birth = is_night_time_birth(jd_at_dob, place)
    planet_positions = drik.dhasavarga(jd_at_dob, place)
    eigth_house_long = lagna_longitude(jd_at_dob, place)+210
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(jd_at_dob, place)
    " A - B + C "
    apamrithyu_sagam_long = eigth_house_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(eigth_house_long,mars_long,lagna_long):
        apamrithyu_sagam_long += 30
    if night_time_birth:
        apamrithyu_sagam_long = mars_long - eigth_house_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,eigth_house_long,lagna_long):
            apamrithyu_sagam_long += 30
    return utils.norm360(apamrithyu_sagam_long + dhasa_progression_correction)
    
def laabha_saham(jd_at_dob, place, dhasa_progression_correction=0.0):
    # 36 Labha Material gains
    #
    # Classical/common formula:
    # 11th cusp - 11th lord + Lagna
    #
    # Same for day and night.
    #
    # IMPORTANT:
    # Here X is Lagna, so formula additive and correction point are both Lagna.

    planet_positions = drik.dhasavarga(jd_at_dob, place)

    asc_house = _ascendant_house(jd_at_dob, place)
    eleventh_house = (asc_house + const.HOUSE_11) % 12
    eleventh_lord = ( const.house_owners[eleventh_house] if const.use_default_house_owner_for_saham_calculation 
                   else house.house_owner_from_planet_positions(planet_positions, eleventh_house) )
    lagna_long = lagna_longitude(jd_at_dob, place)
    eleventh_house_long = lagna_long + const.HOUSE_11 * 30.0
    eleventh_lord_long = saham_longitude(planet_positions, eleventh_lord)

    a, b, x = eleventh_house_long, eleventh_lord_long, lagna_long

    laabha_saham_long = a - b + x

    # Tajaka correction: C is always Lagna longitude.
    if not _is_C_between_B_to_A(a, b, lagna_long):
        laabha_saham_long += 30.0

    return utils.norm360(laabha_saham_long + dhasa_progression_correction)
    
def _is_C_between_B_to_A(a_long, b_long, c_long):
    # Shift the 360-degree circle so Planet B becomes the 0-degree baseline
    # This naturally handles 0-indexed Rasis (0 to 11) and wrap-arounds flawlessly
    target_a = (a_long - b_long) % 360
    target_c = (c_long - b_long) % 360
    
    # Returns True if C is between B and A. 
    # Returns False if C is outside, triggering your code's +30 degree addition.
    return target_c <= target_a

def __is_C_between_B_to_A(a_long,b_long,c_long):
    a_rasi = int(a_long/30)
    b_rasi = int(b_long/30)
    c_rasi = int(c_long/30)
    c_rasi_found = False
    for n in range(b_rasi,b_rasi+11):
        next_n = (n+1) % 12 
        if next_n == c_rasi:
            c_rasi_found = True
            break
        elif next_n == a_rasi:
            break
    return c_rasi_found
     
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests.saham_new_tests()
    exit()
