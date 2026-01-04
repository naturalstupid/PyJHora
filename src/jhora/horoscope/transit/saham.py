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
    Saham calculation
    saham has a formula that looks like A – B + C. What this means is that we take the
    longitudes of A, B and C and find (A – B + C). This is equivalent to finding how far
    A is from B and then taking the same distance from C. However, if C is not between
    B and A (i.e. we start from B and go zodiacally till we meet A and we do not find C
    on the way), then we add 30º to the value evaluated above.    
"""
saham_longitude = lambda pp,p:pp[p][1][0]*30+pp[p][1][1]
lagna_longitude = lambda pp: saham_longitude(pp,0)
sun_longitude = lambda pp: saham_longitude(pp,1)
moon_longitude = lambda pp: saham_longitude(pp,2)
mars_longitude = lambda pp: saham_longitude(pp,3)
mercury_longitude = lambda pp: saham_longitude(pp,4)
jupiter_longitude = lambda pp: saham_longitude(pp,5)
venus_longitude = lambda pp: saham_longitude(pp,6)
saturn_longitude = lambda pp: saham_longitude(pp,7)

# Saham Meaning Formula
def punya_saham(planet_positions,night_time_birth=False):
# 1 Punya Fortune/good deeds Moon – Sun + Lagna
    moon_long = moon_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    punya_sagam_long = moon_long - sun_long + lagna_long
    if not _is_C_between_B_to_A(moon_long,sun_long,lagna_long):
        punya_sagam_long += 30
    if night_time_birth:
        punya_sagam_long = sun_long - moon_long + lagna_long
        if not _is_C_between_B_to_A(sun_long,moon_long,lagna_long):
            punya_sagam_long += 30
    punya_sagam_long %= 360
    return punya_sagam_long
    
def vidya_saham(planet_positions,night_time_birth=False):
# 2 Vidya Education Sun – Moon + Lagna
    sun_long = sun_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    vidya_sagam_long = sun_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(sun_long,moon_long,lagna_long):
        vidya_sagam_long += 30
    if night_time_birth:
        vidya_sagam_long = moon_long - sun_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,sun_long,lagna_long):
            vidya_sagam_long += 30
    vidya_sagam_long %= 360
    return vidya_sagam_long
def yasas_saham(planet_positions,night_time_birth=False):
# 3 Yasas Fame Jupiter – PunyaSaham + Lagna
    jupiter_long = jupiter_longitude(planet_positions)
    punya_long = punya_saham(planet_positions, night_time_birth)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    yasas_sagam_long = jupiter_long - punya_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,punya_long,lagna_long):
        yasas_sagam_long += 30
    if night_time_birth:
        yasas_sagam_long = punya_long - jupiter_long + lagna_long
        if not _is_C_between_B_to_A(punya_long,jupiter_long,lagna_long):
            yasas_sagam_long += 30
    yasas_sagam_long %= 360
    return yasas_sagam_long
def mitra_saham(planet_positions,night_time_birth=False):
# 4 Mitra Friend Jupiter – PunyaSaham + Venus
    jupiter_long = jupiter_longitude(planet_positions)
    punya_long = punya_saham(planet_positions, night_time_birth)
    venus_long = venus_longitude(planet_positions)
    " A - B + C "
    mitra_sagam_long = jupiter_long - punya_long + venus_long
    if not _is_C_between_B_to_A(jupiter_long,punya_long,venus_long):
        mitra_sagam_long += 30
    if night_time_birth:
        mitra_sagam_long = punya_long - jupiter_long + venus_long
        if not _is_C_between_B_to_A(punya_long,jupiter_long,venus_long):
            mitra_sagam_long += 30
    mitra_sagam_long %= 360
    return mitra_sagam_long
def mahatmaya_saham(planet_positions,night_time_birth=False):
# 5 Mahatmya Greatness PunyaSaham – Mars + Lagna
    punya_long = punya_saham(planet_positions, night_time_birth)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    mahatmaya_sagam_long = punya_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(punya_long,mars_long,lagna_long):
        mahatmaya_sagam_long += 30
    if night_time_birth:
        mahatmaya_sagam_long = mars_long - punya_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,punya_long,lagna_long):
            mahatmaya_sagam_long += 30
    mahatmaya_sagam_long %= 360
    return mahatmaya_sagam_long
def asha_saham(planet_positions,night_time_birth=False):
# 6 Asha Desires Saturn – Mars + Lagna
    saturn_long = saturn_longitude(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    asha_sagam_long = saturn_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,mars_long,lagna_long):
        asha_sagam_long += 30
    if night_time_birth:
        asha_sagam_long = mars_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,saturn_long,lagna_long):
            asha_sagam_long += 30
    asha_sagam_long %= 360
    return asha_sagam_long
def samartha_saham(planet_positions,night_time_birth=False):
# 7 Samartha Enterprise/ability    Mars – Lagna Lord + Lagna (Jupiter – Mars + Lagna, if Mars owns lagna)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_house = planet_positions[0][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,lagna_house)
    if lagna_lord == 2:
        #print('Lagna Lord is Mars. So Jupiter is used as Lagna Lord in saham equation')
        lagna_lord = 4 # Jupiter
        " This is done to swap ABC equation "
        night_time_birth = not night_time_birth
    lagna_lord_long = saham_longitude(planet_positions,lagna_lord+1)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    samartha_sagam_long = mars_long - lagna_lord_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,lagna_lord_long,lagna_long):
        samartha_sagam_long += 30
    if night_time_birth:
        samartha_sagam_long = lagna_lord_long - mars_long + lagna_long
        if not _is_C_between_B_to_A(lagna_lord_long,mars_long,lagna_long):
            samartha_sagam_long += 30
    samartha_sagam_long %= 360
    return samartha_sagam_long
def bhratri_saham(planet_positions):
# 8 Bhratri Brothers Jupiter – Saturn + Lagna (same for day & night)
    jupiter_long = jupiter_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    bhratri_sagam_long = jupiter_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,saturn_long,lagna_long):
        bhratri_sagam_long += 30
    bhratri_sagam_long %= 360
    return bhratri_sagam_long
def gaurava_saham(planet_positions,night_time_birth=False):
    """
        TODO: JHora book says jupiter-moon+sun
        Internet says: sun-moon+jupiter - which is right. We follow JHora book - but does not match with JHora s/w.
    """
# 9 Gaurava Respect/regard Jupiter – Moon + Sun
    jupiter_long = jupiter_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    " A - B + C "
    gaurava_sagam_long = jupiter_long - moon_long + sun_long
    if not _is_C_between_B_to_A(jupiter_long,moon_long,sun_long):
        gaurava_sagam_long += 30
    if night_time_birth:
        gaurava_sagam_long = moon_long - jupiter_long + sun_long
        if not _is_C_between_B_to_A(moon_long,jupiter_long,sun_long):
            gaurava_sagam_long += 30
    gaurava_sagam_long %= 360
    return gaurava_sagam_long
def pithri_saham(planet_positions,night_time_birth=False):
    # 10 Pitri Father Saturn – Sun + Lagna
    saturn_long = saturn_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    pithri_sagam_long = saturn_long - sun_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,sun_long,lagna_long):
        pithri_sagam_long += 30
    if night_time_birth:
        pithri_sagam_long = sun_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(sun_long,saturn_long,lagna_long):
            pithri_sagam_long += 30
    pithri_sagam_long %= 360
    return pithri_sagam_long
def rajya_saham(planet_positions,night_time_birth=False):
# 11 Rajya Kingdom Saturn – Sun + Lagna
    return pithri_saham(planet_positions,night_time_birth)

def maathri_saham(planet_positions,night_time_birth=False):
# 12 Matri Mother Moon – Venus + Lagna
    moon_long = moon_longitude(planet_positions)
    venus_long = venus_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    maathri_sagam_long = moon_long - venus_long + lagna_long
    if not _is_C_between_B_to_A(moon_long,venus_long,lagna_long):
        maathri_sagam_long += 30
    if night_time_birth:
        maathri_sagam_long = venus_long - moon_long + lagna_long
        if not _is_C_between_B_to_A(venus_long,moon_long,lagna_long):
            maathri_sagam_long += 30
    maathri_sagam_long %= 360
    return maathri_sagam_long
def puthra_saham(planet_positions,night_time_birth=False):
# 13 Putra Children Jupiter – Moon + Lagna
    jupiter_long = jupiter_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    puthra_sagam_long = jupiter_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,moon_long,lagna_long):
        puthra_sagam_long += 30
    if night_time_birth:
        puthra_sagam_long = moon_long - jupiter_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,jupiter_long,lagna_long):
            puthra_sagam_long += 30
    puthra_sagam_long %= 360
    return puthra_sagam_long
def jeeva_saham(planet_positions,night_time_birth=False):
# 14 Jeeva Life Saturn – Jupiter + Lagna
    saturn_long = saturn_longitude(planet_positions)
    jupiter_long = jupiter_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    jeeva_sagam_long = saturn_long - jupiter_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,jupiter_long,lagna_long):
        jeeva_sagam_long += 30
    if night_time_birth:
        jeeva_sagam_long = jupiter_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(jupiter_long,saturn_long,lagna_long):
            jeeva_sagam_long += 30
    jeeva_sagam_long %= 360
    return jeeva_sagam_long
def karma_saham(planet_positions,night_time_birth=False):
# 15 Karma Action (work) Mars – Mercury + Lagna
    mars_long = mars_longitude(planet_positions)
    mercury_long = mercury_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    karma_sagam_long = mars_long - mercury_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,mercury_long,lagna_long):
        karma_sagam_long += 30
    if night_time_birth:
        karma_sagam_long = mercury_long - mars_long + lagna_long
        if not _is_C_between_B_to_A(mercury_long,mars_long,lagna_long):
            karma_sagam_long += 30
    karma_sagam_long %= 360
    return karma_sagam_long
def roga_saham(planet_positions,night_time_birth=False):
# 16 Roga Disease Lagna – Moon + Lagna (Same for night/day)
    lagna_long = lagna_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    roga_sagam_long = lagna_long - moon_long + lagna_long
    roga_sagam_long %= 360
    return roga_sagam_long
def roga_sagam_1(planet_positions,night_time_birth=False):
# 16 Roga Disease - Another Version -  Saturn – Moon + Lagna
    saturn_long = saturn_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    roga_sagam_long = saturn_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(saturn_long,moon_long,lagna_long):
        roga_sagam_long += 30
    if night_time_birth:
        roga_sagam_long = moon_long - saturn_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,saturn_long,lagna_long):
            roga_sagam_long += 30
    roga_sagam_long %= 360
    return roga_sagam_long
def kali_saham(planet_positions,night_time_birth=False):
# 17 Kali Great misfortune Jupiter – Mars + Lagna
    jupiter_long = jupiter_longitude(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    kali_sagam_long = jupiter_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(jupiter_long,mars_long,lagna_long):
        kali_sagam_long += 30
    if night_time_birth:
        kali_sagam_long = mars_long - jupiter_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,jupiter_long,lagna_long):
            kali_sagam_long += 30
    kali_sagam_long %= 360
    return kali_sagam_long
def sastra_saham(planet_positions,night_time_birth=False):
# 18 Sastra Sciences Jupiter – Saturn + Mercury
    jupiter_long = jupiter_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    mercury_long = mercury_longitude(planet_positions)
    " A - B + C "
    sastra_sagam_long = jupiter_long - saturn_long + mercury_long
    if not _is_C_between_B_to_A(jupiter_long,saturn_long,mercury_long):
        sastra_sagam_long += 30
    if night_time_birth:
        sastra_sagam_long = saturn_long - jupiter_long + mercury_long
        if not _is_C_between_B_to_A(saturn_long,jupiter_long,mercury_long):
            sastra_sagam_long += 30
    sastra_sagam_long %= 360
    return sastra_sagam_long
def bandhu_saham(planet_positions,night_time_birth=False):
# 19 Bandhu Relatives Mercury – Moon + Lagna
    mercury_long = mercury_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    bandhu_sagam_long = mercury_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(mercury_long,moon_long,lagna_long):
        bandhu_sagam_long += 30
    if night_time_birth:
        bandhu_sagam_long = moon_long - mercury_long + lagna_long
        if not _is_C_between_B_to_A(moon_long,mercury_long,lagna_long):
            bandhu_sagam_long += 30
    bandhu_sagam_long %= 360
    return bandhu_sagam_long
def mrithyu_saham(planet_positions):
# 20 Mrityu Death 8th house – Moon + Lagna (same for day & night)
    lagna_long = lagna_longitude(planet_positions)
    eigth_house_long = lagna_long + (8-1)*30
    moon_long = moon_longitude(planet_positions)
    " A - B + C "
    mrithyu_sagam_long = eigth_house_long - moon_long + lagna_long
    if not _is_C_between_B_to_A(eigth_house_long,moon_long,lagna_long):
        mrithyu_sagam_long += 30
    mrithyu_sagam_long %= 360
    return mrithyu_sagam_long
def paradesa_saham(planet_positions,night_time_birth=False):
# 21 Paradesa Foreign countries 9th house – 9th lord + Lagna (same for day & night)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]
    ninth_house = (asc_house+9-1)%12
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,ninth_house)
    long_asc_house = lagna_longitude(planet_positions)
    long_ninth_house = long_asc_house+(9-1)*30.0
    long_ninth_lord = saham_longitude(planet_positions,ninth_lord+1)
    " A - B + C "
    paradesa_saham_long = (long_ninth_house - long_ninth_lord + long_asc_house)
    if not _is_C_between_B_to_A(long_ninth_house,long_ninth_lord,long_asc_house):
        paradesa_saham_long += 30
    paradesa_saham_long %= 360
    return paradesa_saham_long
def artha_saham(planet_positions,night_time_birth=False):
# 22 Artha Money 2nd house – 2nd lord + Lagna (same for day & night)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]
    second_house = (asc_house+2-1)%12
    second_lord = house.house_owner_from_planet_positions(planet_positions,second_house)
    #print('asc_house',asc_house,'second_house',second_house,'second_lord',second_lord)
    long_asc_house = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    long_second_house = long_asc_house+30.0
    long_second_lord = planet_positions[second_lord+1][1][0]*30+planet_positions[second_lord+1][1][1]
    " A - B + C "
    artha_saham_long = (long_second_house - long_second_lord + long_asc_house)
    if not _is_C_between_B_to_A(long_second_house,long_second_lord,long_asc_house):
        artha_saham_long += 30
    artha_saham_long %= 360
    return artha_saham_long
def paradara_saham(planet_positions,night_time_birth=False):
# 23 Paradara Adultery Venus – Sun + Lagna
    venus_long = venus_longitude(planet_positions)
    sun_long = sun_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    paradara_sagam_long = venus_long - sun_long + lagna_long
    if not _is_C_between_B_to_A(venus_long,sun_long,lagna_long):
        paradara_sagam_long += 30
    if night_time_birth:
        paradara_sagam_long = sun_long - venus_long + lagna_long
        if not _is_C_between_B_to_A(sun_long,venus_long,lagna_long):
            paradara_sagam_long += 30
    paradara_sagam_long %= 360
    return paradara_sagam_long
def vanika_saham(planet_positions,night_time_birth=False):
# 24 Vanik Commerce Moon – Mercury + Lagna
    moon_long = moon_longitude(planet_positions) #345-14 11-15-14
    mercury_long = mercury_longitude(planet_positions) # 311-28 - 10-11-28
    lagna_long = lagna_longitude(planet_positions) # 280-50 - 9-10-50
    " A - B + C "
    vanika_sagam_long = moon_long - mercury_long + lagna_long
    if not _is_C_between_B_to_A(moon_long,mercury_long,lagna_long):
        vanika_sagam_long += 30
    if night_time_birth:
        vanika_sagam_long = mercury_long - moon_long + lagna_long
        if not _is_C_between_B_to_A(mercury_long,moon_long,lagna_long):
            vanika_sagam_long += 30
    vanika_sagam_long %= 360
    return vanika_sagam_long
def karyasiddhi_saham(planet_positions,night_time_birth=False):
# 25 Karyasiddhi Success in endeavours Saturn – Sun + Lord of sunsign (Night: Saturn – Moon + Lord of Moonsign)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    B_long = sun_longitude(planet_positions)
    lord_of_sun_sign = house.house_owner_from_planet_positions(planet_positions,planet_positions[1][1][0])
    sign_long = saham_longitude(planet_positions,lord_of_sun_sign+1)
    " A - B + C "
    karyasiddhi_sagam_long = saturn_long - B_long + sign_long
    if not _is_C_between_B_to_A(saturn_long,B_long,sign_long):
        karyasiddhi_sagam_long += 30
    if night_time_birth:
        B_long = moon_longitude(planet_positions)
        lord_of_moon_sign = house.house_owner_from_planet_positions(planet_positions,planet_positions[2][1][0])
        sign_long = saham_longitude(planet_positions,lord_of_moon_sign+1)
        karyasiddhi_sagam_long = saturn_long - B_long + sign_long
        if not _is_C_between_B_to_A(saturn_long,B_long,sign_long):
            karyasiddhi_sagam_long += 30
    karyasiddhi_sagam_long %= 360
    return karyasiddhi_sagam_long
    
def vivaha_saham(planet_positions,night_time_birth=False):
# 26 Vivaha Marriage Venus – Saturn + Lagna
    venus_long = venus_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    vivaha_saham_long = venus_long - saturn_long + lagna_long 
    if not _is_C_between_B_to_A(venus_long,saturn_long,lagna_long):
        vivaha_saham_long += 30
    if night_time_birth:
        vivaha_saham_long = saturn_long - venus_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,venus_long,lagna_long):
            vivaha_saham_long += 30
    vivaha_saham_long %= 360
    return vivaha_saham_long
def santapa_saham(planet_positions,night_time_birth=False):
# 27 Santapa Sadness Saturn – Moon + 6th house
    saturn_long = saturn_longitude(planet_positions)
    moon_long = moon_longitude(planet_positions)
    sixth_house_long = lagna_longitude(planet_positions) + (6-1)*30
    " A - B + C "
    santapa_saham_long = saturn_long - moon_long + sixth_house_long 
    if not _is_C_between_B_to_A(saturn_long,moon_long,sixth_house_long):
        santapa_saham_long += 30
    if night_time_birth:
        santapa_saham_long = moon_long - saturn_long + sixth_house_long
        if not _is_C_between_B_to_A(moon_long,saturn_long,sixth_house_long):
            santapa_saham_long += 30
    santapa_saham_long %= 360
    return santapa_saham_long
def sraddha_saham(planet_positions,night_time_birth=False):
# 28 Sraddha Devotion/sincerity Venus – Mars + Lagna
    venus_long = venus_longitude(planet_positions)
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    sraddha_sagam_long = venus_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(venus_long,mars_long,lagna_long):
        sraddha_sagam_long += 30
    if night_time_birth:
        sraddha_sagam_long = mars_long - venus_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,venus_long,lagna_long):
            sraddha_sagam_long += 30
    sraddha_sagam_long %= 360
    return sraddha_sagam_long
def preethi_saham(planet_positions,night_time_birth=False):
# 29 Preeti Love/attachment SastraSaham – PunyaSaham + Lagna
    sastra_long = sastra_saham(planet_positions, night_time_birth)
    punya_long = punya_saham(planet_positions, night_time_birth)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    preethi_sagam_long = sastra_long - punya_long + lagna_long
    if not _is_C_between_B_to_A(sastra_long,punya_long,lagna_long):
        preethi_sagam_long += 30
    if night_time_birth:
        preethi_sagam_long = punya_long - sastra_long + lagna_long
        if not _is_C_between_B_to_A(punya_long,sastra_long,lagna_long):
            preethi_sagam_long += 30
    preethi_sagam_long %= 360
    return preethi_sagam_long
def jadya_saham(planet_positions,night_time_birth=False):
# 30 Jadya Chronic disease Mars – Saturn + Mercury
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
    return jadya_sagam_long
def vyaapaara_saham(planet_positions):
# 31 Vyapara Business Mars – Saturn + Lagna (same for day & night)
    mars_long = mars_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    vyaapaara_sagam_long = mars_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,saturn_long,lagna_long):
        vyaapaara_sagam_long += 30
    vyaapaara_sagam_long %= 360
    return vyaapaara_sagam_long
def sathru_saham(planet_positions,night_time_birth=False):
# 32 Satru Enemy Mars – Saturn + Lagna
    mars_long = mars_longitude(planet_positions)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    sathru_sagam_long = mars_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(mars_long,saturn_long,lagna_long):
        sathru_sagam_long += 30
    if night_time_birth:
        sathru_sagam_long = saturn_long - mars_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,mars_long,lagna_long):
            sathru_sagam_long += 30
    sathru_sagam_long %= 360
    return sathru_sagam_long
def jalapatna_saham(planet_positions,night_time_birth=False):
# 33 Jalapatana Crossing an ocean Cancer 15º– Saturn + Lagna
    cancer_long = 105.0
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    jalapatna_sagam_long = cancer_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(cancer_long,saturn_long,lagna_long):
        jalapatna_sagam_long += 30
    if night_time_birth:
        jalapatna_sagam_long = saturn_long - cancer_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,cancer_long,lagna_long):
            jalapatna_sagam_long += 30
    jalapatna_sagam_long %= 360
    return jalapatna_sagam_long
def bandhana_saham(planet_positions,night_time_birth=False):
# 34 Bandhana Imprisonment PunyaSaham – Saturn + Lagna
    punya_long = punya_saham(planet_positions, night_time_birth)
    saturn_long = saturn_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    bandhana_sagam_long = punya_long - saturn_long + lagna_long
    if not _is_C_between_B_to_A(punya_long,saturn_long,lagna_long):
        bandhana_sagam_long += 30
    if night_time_birth:
        bandhana_sagam_long = saturn_long - punya_long + lagna_long
        if not _is_C_between_B_to_A(saturn_long,punya_long,lagna_long):
            bandhana_sagam_long += 30
    bandhana_sagam_long %= 360
    return bandhana_sagam_long
def apamrithyu_saham(planet_positions,night_time_birth=False):
# 35 Apamrityu Bad death 8th house – Mars + Lagna
    eigth_house_long = lagna_longitude(planet_positions)+210
    mars_long = mars_longitude(planet_positions)
    lagna_long = lagna_longitude(planet_positions)
    " A - B + C "
    apamrithyu_sagam_long = eigth_house_long - mars_long + lagna_long
    if not _is_C_between_B_to_A(eigth_house_long,mars_long,lagna_long):
        apamrithyu_sagam_long += 30
    if night_time_birth:
        apamrithyu_sagam_long = mars_long - eigth_house_long + lagna_long
        if not _is_C_between_B_to_A(mars_long,eigth_house_long,lagna_long):
            apamrithyu_sagam_long += 30
    apamrithyu_sagam_long %= 360
    return apamrithyu_sagam_long
def laabha_saham(planet_positions,night_time_birth=False):
# 36 Labha Material gains 11th house – 11th lord + Lagna (same for day & night)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]
    eleventh_house = (asc_house+11-1)%12
    eleventh_lord = house.house_owner_from_planet_positions(planet_positions,eleventh_house)
    long_asc_house = lagna_longitude(planet_positions)
    long_eleventh_house = long_asc_house+(11-1)*30.0
    long_eleventh_lord = saham_longitude(planet_positions,eleventh_lord+1)
    " A - B + C "
    laabha_saham_long = (long_eleventh_house - long_eleventh_lord + long_asc_house)
    if not _is_C_between_B_to_A(long_eleventh_house,long_eleventh_lord,long_asc_house):
        laabha_saham_long += 30
    if night_time_birth:
        laabha_saham_long = (long_eleventh_lord - long_eleventh_house + long_asc_house)
        if not _is_C_between_B_to_A(long_eleventh_lord,long_eleventh_house,long_asc_house):
            laabha_saham_long += 30
    laabha_saham_long %= 360
    return laabha_saham_long
def _is_C_between_B_to_A(a_long,b_long,c_long):
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
    pvr_tests.saham_tests()
    exit()
