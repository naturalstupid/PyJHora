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
from jhora.horoscope.chart import house
_hora_chart_by_pvr_method = const.hora_chart_by_pvr_method
_lang_path = const._LANGUAGE_PATH
divisional_chart_functions = {2:'hora_chart',3:'drekkana_chart',4:'chaturthamsa_chart',5:'panchamsa_chart',
                              6:'shashthamsa_chart',7:'saptamsa_chart',8:'ashtamsa_chart',9:'navamsa_chart',
                              10:'dasamsa_chart',11:'rudramsa_chart',12:'dwadasamsa_chart',16:'shodasamsa_chart',
                              20:'vimsamsa_chart',24:'chaturvimsamsa_chart',27:'nakshatramsa_chart',30:'trimsamsa_chart',
                              40:'khavedamsa_chart',45:'akshavedamsa_chart',60:'shashtyamsa_chart',
                              81:'nava_navamsa_chart',108:'ashtotharamsa_chart',144:'dwadas_dwadasamsa_chart'}
def get_amsa_resources(language='en'):
    """
        get raja yoga names from raja_yoga_msgs_<lang>.txt
        @param language: Two letter language code. en, hi, ka, ta, te
        Note: this argument is not required it language was already set using utils.set_language
        @return json strings from the resource file as dictionary 
    """
    import json
    json_file = _lang_path + "amsa_rulers_"+language+'.json'
    #print('opening json file',json_file)
    f = open(json_file,"r",encoding="utf-8")
    msgs = json.load(f)
    return msgs
def rasi_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,years=1,months=1,sixty_hours=1
               ,calculation_type='drik',pravesha_type=0):
    """
        Get Rasi chart - D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    #print('rasi chart',jd_at_dob,place_as_tuple,'years',years,'months',months,'60hrs',sixty_hours)
    jd_years = drik.next_solar_date(jd_at_dob, place_as_tuple, years, months,sixty_hours)
    if pravesha_type==2:
        from jhora.panchanga import vratha
        bt_year,bt_month,bt_day,bt_hours = utils.jd_to_gregorian(jd_at_dob)
        #print('bt_year,bt_month,bt_day,bt_hours',bt_year,bt_month,bt_day,bt_hours)
        birth_date = drik.Date(bt_year,bt_month,bt_day); birth_time = tuple(utils.to_dms(bt_hours,as_string=False))
        year_number = bt_year + years - 1
        tp = vratha.tithi_pravesha(birth_date, birth_time, place_as_tuple, year_number)
        #print('tithi pravesha',tp)
        tp_date = tp[0][0]; tp_time = tp[0][1]; birth_time = tuple(utils.to_dms(tp_time,as_string=False))
        tp_date_new = drik.Date(tp_date[0],tp_date[1],tp_date[2])
        jd_years = utils.julian_day_number(tp_date_new, birth_time)
    if calculation_type.lower()=='ss':
        from jhora.panchanga import surya_sidhantha
        return surya_sidhantha.planet_positions(jd_years, place_as_tuple)
    ascendant_index = const._ascendant_symbol
    drik.set_ayanamsa_mode(ayanamsa_mode)
    " Get Ascendant information"
    ascendant_constellation, ascendant_longitude, _, _ = drik.ascendant(jd_years,place_as_tuple)
    """ FIXED in V2.3.1 - asc long re-calculated to get full longitude value """
    #ascendant_longitude += ascendant_longitude + ascendant_constellation*30 
    #ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor=1)
    #print('ascendant dhasa varga',ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude)
    " Get planet information "
    " planet_positions lost: [planet_id, planet_constellation, planet_longitude] "
    planet_positions = drik.dhasavarga(jd_years,place_as_tuple,divisional_chart_factor=1)
    #print('planet_positions\n',planet_positions)
    planet_positions = [[ascendant_index,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    return planet_positions
def bhava_houses(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,bhava_starts_with_ascendant=False):
    bp = bhava_chart_houses(jd, place, ayanamsa_mode,bhava_starts_with_ascendant=bhava_starts_with_ascendant)
    bp = {p:house.get_relative_house_of_planet(bp[const._ascendant_symbol][0],h) for p,(h,_) in bp.items()}
    return bp
def bhava_chart(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,bhava_madhya_method=const.bhaava_madhya_method):
    """
        @return: [[house1_rasi,(house1_start,house1_cusp,house1_end),[planets_in_house1]],(...),
                [house12_rasi,(house12_start,house12_cusp,house12_end,[planets_in_house12])]]
    """
    drik.set_ayanamsa_mode(ayanamsa_mode)
    return drik._bhaava_madhya_new(jd, place, bhava_madhya_method)
def bhava_chart_houses(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,years=1,months=1,sixty_hours=1
                ,calculation_type='drik',bhava_starts_with_ascendant=False):
    """
        Get Bhava chart from Rasi / D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    planet_positions = rasi_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, years, months, sixty_hours,
                                  calculation_type=calculation_type)
    #print('rasi planet positions',planet_positions)
    asc_house = planet_positions[0][1][0]
    asc_long = planet_positions[0][1][1]
    asc_start = asc_long if bhava_starts_with_ascendant else asc_long - 15.0
    asc_end = asc_long + 30.0 if bhava_starts_with_ascendant else asc_long + 15.0
    pp_bhava = {}
    if asc_start < 0:
        pp_bhava[const._ascendant_symbol]=(asc_house-1,asc_long)
        for p,(h,p_long) in planet_positions[1:]:
            pp_bhava[p]=(h,p_long)
            if p_long > asc_end:
                pp_bhava[p]=((h + 1)%12,p_long)
    else:
        pp_bhava[const._ascendant_symbol]=(asc_house,asc_long)
        for p,(h,p_long) in planet_positions[1:]:
            pp_bhava[p]=(h,p_long)
            if p_long < asc_start:
                pp_bhava[p]=((h - 1)%12,p_long)
    return pp_bhava
def _hora_chart_pvr_method(planet_positions_in_rasi):
    """ Hora Chart - D2 Chart PV Narasimha Rao Method"""
    dvf = 2
    _hora_list = const.hora_list
    hora_sign = lambda r,h: [s1 for r1,h1,s1 in _hora_list if r1==r and h1==h][0]
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // 15.0)
        dp.append([planet,[hora_sign(rasi_sign,hora),d_long]])
    return dp
def hora_chart(planet_positions_in_rasi,pvn_rao_method=const.hora_chart_by_pvr_method):
    """ 
        Hora Chart - D2 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 2
    if pvn_rao_method:
        return _hora_chart_pvr_method(planet_positions_in_rasi)
    # Sun's Hora is Leo and Moon's Hora is Cancer
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // 15.0)
        r = 3 # Moon's hora
        if (sign in const.odd_signs and l==0) or (sign in const.even_signs and l==1):
            r = 4 # Sun's Hora
        dp.append([planet,[r,d_long]])
    return dp
def drekkana_chart(planet_positions_in_rasi):
    """ 
        Drekkana Chart - D3 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 3
    dp = []
    f1 = 10
    f2 = 4 
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,d_long]]) # lth position from rasi
    return dp
def chaturthamsa_chart(planet_positions_in_rasi):
    """ 
        Chaturthamsa Chart - D4 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 4
    dp = []
    f1 = 7.5
    f2 = 3
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,d_long]]) # lth position from rasi
    return dp
def panchamsa_chart(planet_positions_in_rasi):
    """ 
        Panchamsa Chart - D5 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 5
    odd = [0,10,8,2,6]
    even = [1,5,11,9,7]
    f1 = 6
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = even[l]%12
        if sign in const.odd_signs:
            r = odd[l]
        dp.append([planet,[r,d_long]]) # lth position from rasi
    return dp
def shashthamsa_chart(planet_positions_in_rasi):
    """ 
        Shashthamsa Chart - D6 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 6
    f1 = 5
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12
        if sign in const.even_signs:
            r = (l+6)%12
        dp.append([planet,[r,d_long]])
    return dp
def saptamsa_chart(planet_positions_in_rasi):
    """ 
        Saptamsa Chart - D7 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 7
    f1 = 30.0/7
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+l+6)%12
        dp.append([planet,[r,d_long]])
    return dp
def ashtamsa_chart(planet_positions_in_rasi):
    """ 
        Ashtamsa Chart - D8 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 8
    f1 = 30.0/8
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+4)%12
        elif sign in const.fixed_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def navamsa_chart(planet_positions_in_rasi):
    """ 
        Navamsa Chart - D9 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 9
    f1 = 30.0/9
    navamsa_dict = {0:const.fire_signs,3:const.water_signs,6:const.air_signs,9:const.earth_signs}
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = [(l+key)%12 for key,sign_list in navamsa_dict.items() if sign in sign_list][0]
        dp.append([planet,[r,d_long]])
    return dp
def dasamsa_chart(planet_positions_in_rasi):
    """ 
        Dasamsa Chart - D10 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 10
    f1 = 3.0
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+l+9)%12
        dp.append([planet,[r,d_long]])
    return dp
def rudramsa_chart(planet_positions_in_rasi):
    """ 
        Rudramsa Chart - D11 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 11
    f1 = 30.0/11
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (12+l-sign-1)%12
        dp.append([planet,[r,d_long]])
    return dp
def dwadasamsa_chart(planet_positions_in_rasi):
    """ 
        Dwadasamsa Chart - D12 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 12
    f1 = 30.0/12
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def shodasamsa_chart(planet_positions_in_rasi):
    """ 
        Shodasamsa Chart - D16 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 16
    f1 = 30.0/16
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+4)%12
        elif sign in const.dual_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def vimsamsa_chart(planet_positions_in_rasi):
    """ 
        Vimsamsa Chart - D20 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 20
    f1 = 30.0/20
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+4)%12
        elif sign in const.fixed_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def chaturvimsamsa_chart(planet_positions_in_rasi):
    """ 
        Chathur Vimsamsa Chart - D24 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 24
    f1 = 30.0/24
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (l+4)%12 #part from Leo
        if sign in const.even_signs:
            r = (l+3)%12 # Part from Cancer
        dp.append([planet,[r,d_long]])
    return dp
def nakshatramsa_chart(planet_positions_in_rasi):
    """ 
        Nakshatramsa Chart - D27 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 27
    f1 = 30.0/27
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # fiery sign
        if sign in const.earth_signs:
            r = (l+3)%12 # part from Cancer
        elif sign in const.air_signs:
            r = (l+6)%12
        elif sign in const.water_signs:
            r = (l+9)%12
        dp.append([planet,[r,d_long]])
    return dp
def trimsamsa_chart(planet_positions_in_rasi):
    """ 
        Trimsamsa Chart - D30 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 30
    odd = [(0,5,0),(5,10,10),(10,18,8),(18,25,2),(25,30,6)]
    even = [(0,5,1),(5,12,5),(12,20,11),(20,25,9),(25,30,7)]
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        if sign in const.odd_signs:
            r = [ rasi%12 for (l_min,l_max,rasi) in odd if (long >= l_min and long <= l_max) ]
        else:
            r = [ rasi%12 for (l_min,l_max,rasi) in even if (long >= l_min and long <= l_max) ]
        dp.append([planet,[r[0],d_long]]) # lth position from rasi
    return dp
def khavedamsa_chart(planet_positions_in_rasi):
    """ 
        Khavedamsa Chart - D40 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 40
    f1 = 30.0/40
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 #part from Aries
        if sign in const.even_signs:
            r = (l+5)%12 # Part from Libra
        dp.append([planet,[r,d_long]])
    return dp
def akshavedamsa_chart(planet_positions_in_rasi):
    """ 
        Akshavedamsa Chart - D45 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 45
    f1 = 30.0/45
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+4)%12
        elif sign in const.dual_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def shashtyamsa_chart(planet_positions_in_rasi):
    """ 
        Shashtyamsa Chart - D60 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 60
    f1 = 30.0/60
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def nava_navamsa_chart(planet_positions_in_rasi):
    """ 
        Nava Navamsa Chart - D81 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 81
    f1 = 30.0/81
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def ashtotharamsa_chart(planet_positions_in_rasi):
    """ 
        Ashtotharamsa Chart - D108 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 108
    f1 = 30.0/108
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def dwadas_dwadasamsa_chart(planet_positions_in_rasi):
    """ 
        Dwadas Dwadasamsa Chart - D144 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 144
    f1 = 30.0/144
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def divisional_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                     years=1,months=1,sixty_hours=1,calculation_type='drik',pravesha_type=0):
    """
        Get divisional/varga chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
    """
    #print('divisional chart',divisional_chart_factor,'years',years,'months',months,'60hrs',sixty_hours)
    planet_positions = rasi_chart(jd_at_dob, place_as_tuple, ayanamsa_mode,years,months,sixty_hours,
                                  calculation_type=calculation_type,pravesha_type=pravesha_type)
    if divisional_chart_factor==1:
        return planet_positions
    else:
        if divisional_chart_factor in divisional_chart_functions.keys():
            return eval(divisional_chart_functions[divisional_chart_factor]+'(planet_positions)')
        else:
            print('Chart division factor',divisional_chart_factor,'not supported')
            return None
    return planet_positions
def _planets_in_retrograde_old(planet_positions):
    """ TODO: CHECK IF this algorithm is correct 
        Retired from V3.0.0 """
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
    """
    retrograde_planets = []
    sun_house = planet_positions[1][1][0]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    for p,(h,p_long) in planet_positions[3:8]: # Exclude Lagna, Sun,Moon,, Rahu and Ketu
        planet_house = planet_positions[p+1][1][0]
        planet_long = h*30+p_long
        if p == 2:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(6,9)]]: # 6 to 8th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(6,9)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'6-8')
                retrograde_planets.append(p)            
        elif p == 3:
            if planet_long > sun_long-20 and planet_long < sun_long+20:
                #print('planet',p,'planet_long',planet_long,sun_long-20,sun_long+20)
                retrograde_planets.append(p)
        elif p == 4:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(5,10)]]: # 5 to 9th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(5,10)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'5-9')
                retrograde_planets.append(p)            
        elif p == 5:
            if planet_long > sun_long-30 and planet_long < sun_long+30:
                #print('planet',p,'planet_long',planet_long,sun_long-30,sun_long+30)
                retrograde_planets.append(p)
        elif p == 6:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(4,11)]]: # 4 to 10th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(4,11)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'4-10')
                retrograde_planets.append(p)
    return retrograde_planets
def planets_in_retrograde(planet_positions):
    """ TODO: This is New Attempt from V3.0.0 onwards 
        based on vakragathi - wikipedia ranges
    """
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
    """
    if const.planet_retrogression_calculation_method == 1:
        return _planets_in_retrograde_old(planet_positions)
    retrograde_planets = []
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    for p,(h,p_long) in planet_positions[3:8]: # Exclude Lagna, Sun,Moon,, Rahu and Ketu
        planet_long = h*30+p_long
        p_long_from_sun_1 = (sun_long+360+const.planets_retrograde_limits_from_sun[p][0])%360
        p_long_from_sun_2 = (sun_long+360+const.planets_retrograde_limits_from_sun[p][1])%360
        if p_long_from_sun_2 < p_long_from_sun_1:
            p_long_from_sun_2 += 360.
        if planet_long > p_long_from_sun_1 and planet_long < p_long_from_sun_2:
            retrograde_planets.append(p)
    return retrograde_planets
def planets_in_combustion(planet_positions,use_absolute_longitude=True):
    """
        Get the list of planets that are in combustion - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in combustion 
    """
    retrograde_planets = planets_in_retrograde(planet_positions) 
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1] if use_absolute_longitude else planet_positions[1][1][1]
    combustion_planets = []
    for p,(h,h_long) in planet_positions[2:8]: # Exclude Lagna, Sun, Rahu and Ketu
        p_long = h*30+h_long if use_absolute_longitude else h_long
        combustion_range = const.combustion_range_of_planets_from_sun
        if p in retrograde_planets: 
            combustion_range = const.combustion_range_of_planets_from_sun_while_in_retrogade
        if p_long >= sun_long-combustion_range[p-2] and p_long <= sun_long+combustion_range[p-2]:
            combustion_planets.append(p)
    return combustion_planets
def vaiseshikamsa_dhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.dhasavarga_amsa_vaiseshikamsa)
def vaiseshikamsa_shadvarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.shadvarga_amsa_vaiseshikamsa)
def vaiseshikamsa_sapthavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.sapthavarga_amsa_vaiseshikamsa)
def vaiseshikamsa_shodhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.shodhasa_varga_amsa_vaiseshikamsa)
def _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,amsa_vaiseshikamsa):
    p_d = [0 for _ in range(9)]
    p_d_s = [0 for _ in range(9)]
    p_d_c = ['' for _ in range(9)]
    for dcf in amsa_vaiseshikamsa.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,divisional_chart_factor=dcf)[:const._upto_ketu]
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                p_d[p] += 1
                p_d_c[p] += 'D'+str(dcf)+'/'
                p_d_s[p] += amsa_vaiseshikamsa[dcf]#*vv
    pdc = {}
    for p in range(9):
        p_d_c[p] = p_d_c[p][:-1]
        pdc[p] = [p_d[p],p_d_c[p],p_d_s[p]]
    return pdc
def _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,amsa_vimsopaka):
    p_d = [0 for _ in range(9)]
    p_d_s = [0 for _ in range(9)]
    p_d_c = ['' for _ in range(9)]
    scores = [5,7,10,15,18]
    for dcf in amsa_vimsopaka.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,divisional_chart_factor=dcf)[:const._upto_ketu]
        h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
        if dcf == 1:
            cr = house._get_compound_relationships_of_planets(h_to_p)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                p_d[p] += 1
                p_d_c[p] += 'D'+str(dcf)+'/'
            if const.house_strengths_of_planets[p][h]==const._OWNER_RULER:
                vv = 20
            else:
                d = const.house_owners[h]
                vv = scores[cr[p][d]]
            p_d_s[p] += amsa_vimsopaka[dcf]*vv/20
    pdc = {}
    for p in range(9):
        p_d_c[p] = p_d_c[p][:-1]
        pdc[p] = [p_d[p],p_d_c[p],p_d_s[p]]
        #print(house.planet_list[p],pdc[p])
    return pdc
    
def vimsopaka_dhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.dhasavarga_amsa_vimsopaka)
def vimsopaka_shadvarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.shadvarga_amsa_vimsopaka)
def vimsopaka_sapthavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.sapthavarga_amsa_vimsopaka)
def vimsopaka_shodhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.shodhasa_varga_amsa_vimsopaka)
def vimsamsavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many vimsamsa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    planet_vimsamsa = [0 for p in range(9)]
    for di, dcf in enumerate(const.vimsamsa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=dcf)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(_world_city_db_df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_vimsamsa[p] += 1
    return planet_vimsamsa
def _varnada_lagna_sanjay_rath(dob,tob, place,house_index=1,divisional_chart_factor=1):
    """ TO DO : Still experimenting """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob, place,divisional_chart_factor=divisional_chart_factor)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    asc_sign = (asc_sign+house_index-1)%12
    asc_long = asc_sign*30+asc_long
    hora_sign,hora_long = drik.hora_lagna(jd_at_dob,place); hora_sign = (hora_sign+house_index-1)%12
    hora_long = hora_sign*30+hora_long
    _debug_ = False
    asc_is_odd = asc_sign in const.odd_signs
    if not asc_is_odd: asc_long = 360.-asc_long
    if _debug_: print(asc_sign,utils.RAASI_LIST[asc_sign],asc_is_odd,asc_long)
    hora_is_odd = hora_sign in const.odd_signs
    if not hora_is_odd: hora_long = 360.-hora_long
    if _debug_: print(hora_sign,utils.RAASI_LIST[hora_sign],hora_is_odd,hora_long)
    if hora_is_odd == asc_is_odd:
        vl = (asc_long + hora_long)%360
        if _debug_: print('adding',asc_long,hora_long,vl)
    else:
        vl = (max(asc_long,hora_long) - min (asc_long,hora_long))%360
        if _debug_: print('subtracting',asc_long,hora_long,vl)
    if _debug_: print('asc_sign',asc_sign,'asc_long',asc_long,'asc_is_odd',const.odd_signs,asc_is_odd)
    if _debug_: print('hora_sign',hora_sign,'hora_long',hora_long,'hora_is_odd',const.odd_signs,hora_is_odd)
    if _debug_: print('vl before',vl)
    if not asc_is_odd: vl = 360 - vl
    if _debug_: print('vl after',vl)
    dl = drik.dasavarga_from_long(vl, divisional_chart_factor=1)
    if _debug_: print('return drik dasavarg',dl)
    return dl
def _varnada_lagna_jha_pandey(dob,tob, place,house_index=1,divisional_chart_factor=1):
    """ TO DO : Still experimenting """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob, place,divisional_chart_factor=divisional_chart_factor)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    lagna = (asc_sign+house_index-1)%12
    asc_long = lagna*30+asc_long
    lagna_is_odd = lagna in const.odd_signs
    if not lagna_is_odd: asc_long = 360.-asc_long
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_sign,hora_long = drik.hora_lagna(jd_at_dob,place)
    hora_lagna = (hora_sign+house_index-1)%12
    hora_long = hora_lagna*30+hora_long
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    if not lagna_is_odd: hora_long = 360.-hora_long
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if count1%2 == count2%2 else (max(count1,count2) - min (count1,count2))%12
    count_is_odd = count%2 != 0
    #print(lagna,lagna_is_odd,count1,hora_lagna,hora_lagna_is_odd,count2,count1%2!=0,count2%2!=0,count)
    vl = (asc_long + hora_long)%360 if count_is_odd else (max(asc_long,hora_long) - min (asc_long,hora_long))%360
    #print(asc_long,hora_long,count_is_odd,vl)
    dl = drik.dasavarga_from_long(vl, divisional_chart_factor=1)
    return dl
def varnada_lagna(dob,tob,place,divisional_chart_factor=1,house_index=1,varnada_method=1):
    """
        Get Varnada Lagna
            Ref: https://saptarishisshop.com/a-look-at-the-calculation-of-varnada-lagna-by-abhishekha/
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @param divisional_chart_factor: D-Chart index
        @param house_index: 1..12 1=Lagna, 2=2nd house etc
        Methods are based on combination of two factors:
             (1) last direction decided by odd/even of Lagna/hora or 
                     odd/even of the count values
             (2) count is decided by just count between lagna & hora lagna or 
                 count based on sum/diff of longitudes of lagna & hora lagna 
        @param varnada_method: 1=BV Raman - Lagna decides last step direction / count based on lagnas
                               2=Sharma/Santhanam - count decides last step direction / count based on lagnas
                               3=Sanjay Rath - Lagna decides last step direction / count based on longitudes of lagnas
                               4=Sitaram Jha/Prof. Ramachandra Pandey - last count decides last step direction / cound on longitudes
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    if varnada_method==1:
        return _varnada_lagna_bv_raman(dob, tob, place, house_index, divisional_chart_factor)
    elif varnada_method==2:
        return _varnada_lagna_sharma(dob, tob, place, house_index, divisional_chart_factor)
    elif varnada_method==3:
        return _varnada_lagna_sanjay_rath(dob, tob, place, house_index, divisional_chart_factor)
    elif varnada_method==4:
        return _varnada_lagna_jha_pandey(dob, tob, place, house_index, divisional_chart_factor)
def _varnada_lagna_bv_raman(dob,tob,place,house_index=1,divisional_chart_factor=1):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob, place,divisional_chart_factor=divisional_chart_factor)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place) # V3.1.9
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if hora_lagna_is_odd == lagna_is_odd else (max(count1,count2) - min (count1,count2))%12
    _varnada_lagna = utils.count_rasis(1,count,dir=1) if lagna_is_odd else utils.count_rasis(12,count,dir=-1)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return _varnada_lagna, asc_long #hl
def _varnada_lagna_santhanam(dob,tob,place,house_index=1,divisional_chart_factor=1):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    return _varnada_lagna_sharma(dob, tob, place, house_index, divisional_chart_factor)
def _varnada_lagna_sharma(dob,tob,place,house_index=1,divisional_chart_factor=1):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    _debug_ = False
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob, place,divisional_chart_factor=divisional_chart_factor)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place) # V3.1.9
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if count1%2 == count2%2 else (max(count1,count2) - min (count1,count2))%12
    count_is_odd = count%2 != 0
    _varnada_lagna = utils.count_rasis(1,count,dir=1) if count_is_odd else utils.count_rasis(12,count,dir=-1)
    #print(count1,count2,count,count_is_odd,_varnada_lagna)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return _varnada_lagna, asc_long #hl
def benefics_and_malefics(jd,place,divisional_chart_factor=1,method=2):
    """
        From BV Raman - Hindu Predictive Astrology - METHOD=1
        Jupiter. Venus. Full Moon and well-associated Mercury are benefics. 
        New Moon, badly associated Mercury. the Sun, Saturn, Mars, Rahu and Ketu are malefics
        From the eighth day of the bright half of the lunar month the Moon is full and strong.
        She is weak from the eighth day of the dark half.
        From PVR Narasimha Rao - Intergrated Vedic Astrology - METHOD=2
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
            Mercury becomes a natural benefic when he is alone or with more natural
            benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
            Mercury becomes a natural malefic when he is joined by more natural malefics.
            Waning Moon of Krishna paksha is a natural malefic.
    """
    benefics = const.natural_benefics[:] ; malefics = const.natural_malefics[:]
    _tithi = drik.tithi(jd, place)[0]
    if method == 2:
        if _tithi > 15:
            malefics.append(1)
        else:
            benefics.append(1)
    else:
        if _tithi >= 8 and _tithi <=15: benefics.append(1)
        if _tithi >= 23 and _tithi <=30: malefics.append(1) 
    planet_positions = divisional_chart(jd, place,divisional_chart_factor=divisional_chart_factor)
    malefics += [3 for p in malefics if planet_positions[p+1][1][0]==planet_positions[4][1][0]]
    benefics += [3 for p in benefics if planet_positions[p+1][1][0]==planet_positions[4][1][0]]
    benefics = sorted(set(benefics)) ; malefics = sorted(set(malefics))
    return benefics, malefics
def benefics(jd,place,method=2):
    """
        From BV Raman - Hindu Predictive Astrology - METHOD=1
        Jupiter. Venus. Full Moon and well-associated Mercury are benefics. 
        New Moon, badly associated Mercury. the Sun, Saturn, Mars, Rahu and Ketu are malefics
        From the eighth day of the bright half of the lunar month the Moon is full and strong.
        She is weak from the eighth day of the dark half.
        From PVR Narasimha Rao - Intergrated Vedic Astrology - METHOD=2
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
            Mercury becomes a natural benefic when he is alone or with more natural
            benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
            Mercury becomes a natural malefic when he is joined by more natural malefics.
            Waning Moon of Krishna paksha is a natural malefic.
    """
    return benefics_and_malefics(jd, place, method=method)[0]
def malefics(jd,place,method=2):
    """
        From BV Raman - Hindu Predictive Astrology - METHOD=1
        Jupiter. Venus. Full Moon and well-associated Mercury are benefics. 
        New Moon, badly associated Mercury. the Sun, Saturn, Mars, Rahu and Ketu are malefics
        From the eighth day of the bright half of the lunar month the Moon is full and strong.
        She is weak from the eighth day of the dark half.
        From PVR Narasimha Rao - Intergrated Vedic Astrology - METHOD=2
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
            Mercury becomes a natural benefic when he is alone or with more natural
            benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
            Mercury becomes a natural malefic when he is joined by more natural malefics.
            Waning Moon of Krishna paksha is a natural malefic.
    """
    return benefics_and_malefics(jd, place, method=method)[1]
def order_planets_from_kendras_of_raasi(planet_positions,raasi=None,include_lagna=False):
    base_house = raasi
    if raasi==None: base_house = planet_positions[0][1][0]
    ks = sum(house.kendras()[:3],[])
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    hp1 = [h_to_p[(base_house+h-1)%12] for h in ks]
    kps = []
    for pl in hp1:
        if not include_lagna and pl=='L': continue
        if pl=='' : continue
        pl2 = sorted([(p,long) for p,(_,long) in planet_positions if str(p) in pl ],key=lambda x:x[1],reverse=True)
        #print(pl2)
        pl3 = [p for p,_ in pl2]
        kps += pl3
    return kps
def _stronger_planet_from_the_list(planet_positions,planet_list):
    def _compare(planet1,planet2):
        return 1 if house.stronger_planet_from_planet_positions(planet_positions, planet1, planet2)==planet1 else -1 
    from functools import cmp_to_key
    planet_list.sort(key=cmp_to_key(_compare))
    return planet_list[0]
    
def _order_stronger_planets(planet_positions,reverse=False):
    """ Still under testing """
    def _compare(planet1,planet2):
        return 1 if house.stronger_planet_from_planet_positions(planet_positions, planet1, planet2)==planet1 else -1 
    planet_list = [*range(9)]
    from functools import cmp_to_key
    planet_list.sort(key=cmp_to_key(_compare))
    if reverse: planet_list = list(reversed(planet_list))
    return planet_list
def _amsa(jd,place, divisional_chart_factor,include_upagrahas=False,
          include_special_lagnas=False,include_sphutas=False):
    "Still under testing - Exact algorithm not clear"
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob = (fh,0,0)
    rasi_planet_positions = rasi_chart(jd, place)
    div_planet_positions = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    def _get_amsa_index_from_longitude(p_long):
        df = 30.0/divisional_chart_factor
        return int(p_long/df)
    __amsa_planets = {}; __amsa_special = {}; __amsa_upagraha = {}; __amsa_sphuta = {}
    for p,(_,long) in rasi_planet_positions:
        __amsa_planets[p] = _get_amsa_index_from_longitude(long)
    if include_special_lagnas:
        special_lagna_dict = {'bhava_lagna_str':0.25,'hora_lagna_str':0.5,'ghati_lagna_str':1.25,'pranapada_lagna_str':5.0,
                                 'vighati_lagna_str':15.0} #Bhava,hora,ghati,pranapada,vighati
        for sl,lf in special_lagna_dict.items():
            sf = drik.special_ascendant(jd, place, lagna_rate_factor=lf, divisional_chart_factor=divisional_chart_factor)
            __amsa_special[sl] = _get_amsa_index_from_longitude(sf[1])
        il = drik.indu_lagna(jd, place, divisional_chart_factor)
        __amsa_special['indu_lagna_str'] = _get_amsa_index_from_longitude(il[1])
        bl = drik.bhrigu_bindhu(jd, place, divisional_chart_factor)
        __amsa_special['bhrigu_bindhu_lagna_str'] = _get_amsa_index_from_longitude(bl[1])
        sl = drik.sree_lagna(jd, place, divisional_chart_factor)
        __amsa_special['sree_lagna_str'] = _get_amsa_index_from_longitude(sl[1])
        vl = varnada_lagna(dob, tob, place, divisional_chart_factor,house_index=1)
        __amsa_special['varnada_lagna_str'] = _get_amsa_index_from_longitude(vl[1])
    if include_upagrahas:
        sub_planet_list_1 = {'kaala_str':'kaala_longitude','mrityu_str':'mrityu_longitude','artha_str':'artha_praharaka_longitude','yama_str':'yama_ghantaka_longitude',
                           'gulika_str':'gulika_longitude','maandi_str':'maandi_longitude'}
        sub_planet_list_2 = ['dhuma','vyatipaata','parivesha','indrachaapa','upaketu']
        sun_long = div_planet_positions[1][1][0]*30+div_planet_positions[1][1][1]
        #print('solar longitude for D-'+str(divisional_chart_factor),sun_long)
        for sp,sp_func in sub_planet_list_1.items():
            v = eval('drik.'+sp_func+'(dob,tob,place,divisional_chart_factor=1)')
            __amsa_upagraha[sp] = _get_amsa_index_from_longitude(v[1])
        for sp in sub_planet_list_2:
            v = eval('drik.'+'solar_upagraha_longitudes(sun_long,sp,divisional_chart_factor)')
            __amsa_upagraha[sp+'_str'] = _get_amsa_index_from_longitude(v[1])
    if include_sphutas:
        from jhora.horoscope.chart import sphuta
        for s in const.sphuta_list:
            fn = 'sphuta.'+s+'_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor)'
            sp = eval(fn)
            __amsa_sphuta[s+'_sphuta_str'] = _get_amsa_index_from_longitude(sp[1])

    return __amsa_planets, __amsa_special, __amsa_upagraha,__amsa_sphuta
if __name__ == "__main__":
    lang = 'en'
    utils.set_language(lang)
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5) 
    jd = utils.julian_day_number(dob, tob); varnada_method=4
    dcf = 3; house_index = 1
    """
    for house_index in range(1,13):
        vl = varnada_lagna(dob, tob, place, dcf, house_index, varnada_method)
        print(house_index,utils.RAASI_LIST[vl[0]],utils.to_dms(vl[1],is_lat_long='plong'))
    exit()
    """
    planet_positions = rasi_chart(jd, place)
    a = _amsa(jd,place,divisional_chart_factor=dcf,include_special_lagnas=True,include_upagrahas=True)
    #print(dcf,a)
    print(dcf,{p:const.amsa_rulers[dcf][a[p]] for p in a[0].keys()})
    exit()
    print(benefics_and_malefics(jd,place,method=1))
    print(benefics_and_malefics(jd,place,method=2))
    exit()
    pp = rasi_chart(jd, place); p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    print('strength order',_order_stronger_planets(pp))
    pl = [3,1,7,8,0,2,5,6,4]
    sp = _stronger_planet_from_the_list(pp,pl)
    print('stronger planet of ',pl,' is',sp)
    kps = order_planets_from_kendras_of_raasi(pp)        
    print('Kendra Order of Planets',kps)
    exit()
    for h in range(1,13):
        vl = _varnada_lagna_bv_raman(dob, tob, place,house_index=h)
        str_bv = "Raman V"+str(h)+' '+utils.RAASI_LIST[vl[0]]+' '+utils.to_dms(vl[1],is_lat_long='plong')
        vl = _varnada_lagna_santhanam(dob, tob, place,house_index=h)
        str_s= "Santhanam V"+str(h)+' '+utils.RAASI_LIST[vl[0]]+' '+utils.to_dms(vl[1],is_lat_long='plong')
        vl = _varnada_lagna_sanjay_rath(jd, place,house_index=h)
        str_sr = "SanjayRath V"+str(h)+' '+utils.RAASI_LIST[vl[0]]+' '+utils.to_dms(vl[1],is_lat_long='plong')
        print(str_bv,str_s,str_sr)
    exit()
    jd_utc = jd - place.timezone/24.
    dcf =1 ; years=1
    print(rasi_chart(jd, place, years=years))
    pp = [[drik.planet_list.index(planet),drik.dasavarga_from_long(drik.sidereal_longitude(jd_utc, planet),dcf)] for planet in drik.planet_list[:-1]]
    print(pp)
    print(bhava_chart(jd, place))
    print(divisional_chart(jd, place,divisional_chart_factor=dcf,years=years))
    exit()
    print(benefics_and_malefics(jd, place))
    exit()
    pp = rasi_chart(jd, place)
    const.planet_retrogression_calculation_method = 1
    print(planets_in_retrograde(pp))
    const.planet_retrogression_calculation_method = 2
    print(planets_in_retrograde(pp))
    exit()
    print(bhava_chart(jd, place))
    exit()
    vl = varnada_lagna(dob, tob, place)
    print(house.rasi_names_en[vl[0]],utils.to_dms(vl[1],is_lat_long='plong'))
    exit()
