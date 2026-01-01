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
    TODO: Custom Divisional Chart with following options:
    Cyclic or not (Cyclic/Parivritti) => First N parts in Ar and 2nd N to Ta etc
    For Non-cyclic - add following options:
        Base/Seed: Starts from sign or Aries
        Mapping of division starts from 
            Base/Seed
            1st/3rd from base (if odd/even)
            1st/5th from base (if odd/even)
            1st/7th from base (if odd/even)
            1st/9th from base (if odd/even)
            1st/11th from base (if odd/even)
            1st/5th/9th from base (movable/fixed/dual)
            1st/9th/5th from base (movable/fixed/dual)
            1st/4th/7th/10th from base (fire,earth,air/water)
            1st/10th/7th/4th from base (fire,earth,air/water)
          count N divisions from end of the sign if sign is even
"""
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
                              81:'nava_navamsa_chart',108:'ashtotharamsa_chart',144:'dwadas_dwadasamsa_chart',
                              #150:'nadiamsa_chart'
                              }
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
    jd_years = jd_at_dob if (years==1 and months==1 and sixty_hours==1) else drik.next_solar_date(jd_at_dob, place_as_tuple, years, months,sixty_hours)
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
def _bhaava_madhya_new(jd,place,planet_positions,bhava_madhya_method=const.bhaava_madhya_method):
    """
        returns house longitudes (start, cusp, end)
        @param jd: Julian Day number
        @param place: Place('name',latitude,longitude,timezone_hours)
        @param bhava_madhya_method:   
            1=> Equal Housing - Lagna in the middle start = lagna-15, end lagna+15; asc same for all houses
            2=> Equal Housing - Lagna as start
            3=> Sripati method.
            4=> KP Method (aka Placidus Houses method)
            5=> Each Rasi is the house (rasi is the house, 0 is start and 30 is end, asc is asc+rasi*30)
            'P':'Placidus','K':'Koch','O':'Porphyrius','R':'Regiomontanus','C':'Campanus','A':'Equal (cusp 1 is Ascendant)',
            'V':'Vehlow equal (Asc. in middle of house 1)','X':'axial rotation system','H':'azimuthal or horizontal system',
            'T':'Polich/Page (topocentric system)','B':'Alcabitus','M':'Morinus'        
        
        @return: [[house1_rasi,(house1_start,house1_cusp,house1_end)],(...),[house12_rasi,(house12_start,house12_cusp,house12_end)]]
    """
    import warnings
    if bhava_madhya_method not in const.available_house_systems.keys():
        warn_msg = "bhava_madhya_method should be one of const.available_house_systems keys\n Value 1 assumed"
        warnings.warn(warn_msg)
        bhava_madhya_method = 1
    ascendant_constellation, ascendant_longitude = planet_positions[0][1][0],planet_positions[0][1][1]
    ascendant_full_longitude = (ascendant_constellation*30+ascendant_longitude)%360
    bhava_houses = []
    if bhava_madhya_method ==1: #Equal Housing - Lagna in the middle
        _bhava_mid = ascendant_full_longitude; 
        for h in range(12):
            _bhava_start = (_bhava_mid-15.0)%360; _bhava_end = (_bhava_mid+15.0)%360 
            bhava_houses.append((_bhava_start,_bhava_mid,_bhava_end))
            _bhava_mid = utils.norm360(_bhava_mid + 30)
        return drik._assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==2: #Equal Housing - Lagna as start
        _bhava_mid = ascendant_full_longitude; 
        for h in range(12):
            _bhava_start = _bhava_mid; _bhava_mid=(_bhava_start+15.0)%360; _bhava_end = (_bhava_mid+15.0)%360 
            bhava_houses.append((_bhava_start,_bhava_mid,_bhava_end))
            _bhava_mid = utils.norm360(_bhava_start + 30)
        return drik._assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==3: #Sripati method
        bm = drik.bhaava_madhya_sripathi(jd, place); bm = bm[:]+[bm[0]]
        for h in range(12):
            _bhava_start = bm[h]; _bhava_mid = 0.5*(bm[h]+bm[h+1]); _bhava_end = bm[h+1] 
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return drik._assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==4 or bhava_madhya_method in const.western_house_systems.keys(): #KP Method (aka swiss ephemeris method) or western house systems
        bm = drik.bhaava_madhya_kp(jd, place) if bhava_madhya_method ==4 else drik.bhaava_madhya_swe(jd, place, house_code=bhava_madhya_method)
        bm = bm[:]+[bm[0]]
        for h in range(12):
            bmh = bm[h]; bmh1 = bm[h+1]
            if bmh1 < bmh: bmh1+=360
            _bhava_start = bmh; _bhava_mid = 0.5*(bmh+bmh1); _bhava_end = bmh1 
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return drik._assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==5: #Each Rasi is the house
        for h in range(12):
            h1 = (h+ascendant_constellation)%12
            _bhava_start = h1*30; _bhava_mid = _bhava_start + ascendant_longitude; _bhava_end = ((h1+1)%12)*30
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return drik._assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
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
def __parivritti_even_reverse(planet_positions_in_rasi,dvf,dirn=1):
    f1 = 30.0/dvf
    _hora_list = utils.parivritti_even_reverse(dvf,dirn)
    hora_sign = lambda r,h: [s1 for r1,h1,s1 in _hora_list if r1==r and h1==h][0]
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // f1)
        dp.append([planet,[hora_sign(rasi_sign,hora),d_long]])
    return dp
def _hora_chart_raman_method(planet_positions_in_rasi):
    """ Hora Chart - D2 Chart Raman Method"""
    dvf = 2
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // 15.0)
        hora_sign = const.hora_list_raman[rasi_sign][hora]
        dp.append([planet,[hora_sign,d_long]])
    return dp
def __parivritti_cyclic(planet_positions_in_rasi,dvf,dirn=1):
    f1 = 30.0/dvf
    _hora_list = utils.parivritti_cyclic(dvf,dirn)
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // f1)
        hora_sign = _hora_list[rasi_sign][hora]
        dp.append([planet,[hora_sign,d_long]])
    return dp
def _hora_chart_kashinath(planet_positions_in_rasi):
    dvf = 2
    planet_hora = {0:(4,4),1:(3,3),2:(7,0),3:(5,2),4:(11,8),5:(6,1),6:(10,9),7:(10,10),8:(4,4)}
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // 15.0)
        lord_of_rasi = house.house_owner_from_planet_positions(planet_positions_in_rasi, rasi_sign)
        if rasi_sign in const.odd_signs:
            hora_sign = planet_hora[lord_of_rasi][0] if hora==0 else planet_hora[lord_of_rasi][1] 
        else:
            hora_sign = planet_hora[lord_of_rasi][1] if hora==0 else planet_hora[lord_of_rasi][0] 
        dp.append([planet,[hora_sign,d_long]])
    return dp
    
""" 
TODO: Another Hora Chart Method from https://jyotish-blog.blogspot.com/2005/08/
    
"""    
def _hora_traditional_parasara_chart(planet_positions_in_rasi):
    # Sun's Hora is Leo and Moon's Hora is Cancer - Traditional Parasara
    dvf = 2
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // 15.0)
        r = 3 # Moon's hora
        if (sign in const.odd_signs and l==0) or (sign in const.even_signs and l==1):
            r = 4 # Sun's Hora
        dp.append([planet,[r,d_long]])
    return dp
def hora_chart(planet_positions_in_rasi,chart_method=2):
    """ 
        Hora Chart - D2 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=> Parasara hora with parivritti & even side reversal (Uma Shambu) here it is PVR method
            2=> Traditional Parasara (Only Le & Cn)
            3=> Raman Method (1st/11th, day/night)
            4=> Parivritti Dwaya (Bicyclical Hora)
            5=> Kashinatha Hora
            6=> Somanatha method (parivritti alternate)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    #print('hora chart method',chart_method)
    if chart_method==1:
        return __parivritti_even_reverse(planet_positions_in_rasi, 2)
    elif chart_method==2:
        return _hora_traditional_parasara_chart(planet_positions_in_rasi)
    elif chart_method==3:
        return _hora_chart_raman_method(planet_positions_in_rasi)
    elif chart_method==4:
        return __parivritti_cyclic(planet_positions_in_rasi, 2)
    elif chart_method==5:
        return _hora_chart_kashinath(planet_positions_in_rasi)
    elif chart_method==6:
        return __parivritti_alternate(planet_positions_in_rasi, 2)
def _drekkana_chart_jagannatha(planet_positions_in_rasi):
    """ Drekkana Chart - D3 Chart Jagannatha Method"""
    dvf = 3; f1 = 30.0/dvf
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // f1)
        hora_sign = const.drekkana_jagannatha[rasi_sign][hora]
        dp.append([planet,[hora_sign,d_long]])
    return dp
def __parivritti_alternate(planet_positions_in_rasi,dvf,dirn=1):
    f1 = 30.0/dvf; _hora_list = utils.parivritti_alternate(dvf,dirn)
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // f1)
        hora_sign = _hora_list[rasi_sign][hora]
        dp.append([planet,[hora_sign,d_long]])
    return dp
def _drekkana_chart_parasara(planet_positions_in_rasi):
    """ Drekkana Chart - PVR/Traditional Parasara Method """
    dvf = 3; f1 = 30.0/dvf
    dp = []
    f2 = 4 
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,d_long]]) # lth position from rasi
    return dp
def drekkana_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Drekkana Chart - D3 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara with parivritti and even sign reversal (Uma Shambu)
            2=>Parivritti Traya
            3=>Somanatha method (parivritti alternate)
            4=>Jaganatha
            5=>Parasara Parivritti and Even sign reverse
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 3
    if chart_method==1:
        return _drekkana_chart_parasara(planet_positions_in_rasi)
    elif chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return _drekkana_chart_jagannatha(planet_positions_in_rasi)
    elif chart_method==5:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
def _chaturthamsa_parasara(planet_positions_in_rasi):
    dvf = 4; f1 = 30.0/dvf
    dp = []
    f2 = 3
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,d_long]]) # lth position from rasi
    return dp
def chaturthamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Chaturthamsa Chart - D4 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti Cyclic
            3=>Parivritti Even Reverse
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    if chart_method==1:
        return _chaturthamsa_parasara(planet_positions_in_rasi)
    elif chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, 4)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, 4)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, 4)
def panchamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Panchamsa Chart - D5 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti Cyclic
            3=>Parivritti Even Reverse
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 5; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    odd = [0,10,8,2,6]
    even = [1,5,11,9,7]
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = even[l]%12
        if sign in const.odd_signs:
            r = odd[l]
        dp.append([planet,[r,d_long]]) # lth position from rasi
    return dp
def shashthamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Shashthamsa Chart - D6 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti Cyclic
            3=>Parivritti Even Reverse
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 6; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12
        if sign in const.even_signs:
            r = (l+6)%12
        dp.append([planet,[r,d_long]])
    return dp
def saptamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Saptamsa Chart - D7 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara (even start from 7th and go forward)
            2=>Traditional Parasara (even start from 7th and go backward)
            3=>Traditional Parasara (even reverse but end in 7th)
            4=>Parivritti Cyclic
            5=>Parivritti Even Reverse
            6=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 7; f1 = 30.0/dvf
    if chart_method==4:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==5:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==6:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    dirn = -1 if chart_method in [2,3] else 1
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+dirn*(l+6))%12
            if chart_method==3:
                r = (r-6)%12
        dp.append([planet,[r,d_long]])
    return dp
def ashtamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Ashtamsa Chart - D8 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti Cyclic
            3=>Parivritti Even Reverse
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 8; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
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
def _navamsa_kalachakra(planet_positions_in_rasi, dvf=9):
    dp =[]
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        nak,padha,_ = drik.nakshatra_pada(long+sign*30)
        r = const.kalachakra_navamsa[nak-1][padha-1]
        dp.append([planet,[r,d_long]])
    return dp
def navamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Navamsa Chart - D9 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parasara navamsa with even sign reversal (Uniform Krishna Mishra Navamsa)
            3=>Kalachakra Navamsa
            4=>Rangacharya Krishna Mishra Navamsa / Sanjay Rath Nadi Navamsa
            5=>Parivritti Cyclic
            6=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 9; f1 = 30.0/dvf
    if chart_method==5: # This also same as traditional UKM
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==2: # Uniform Krishna Navamsa Method
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==6:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    elif chart_method==3: # Kalachakra Navamsa
        return _navamsa_kalachakra(planet_positions_in_rasi)
    # Traditional Parasara Method
    navamsa_dict = {0:(1,const.fire_signs),3:(1,const.water_signs),6:(1,const.air_signs),9:(1,const.earth_signs)}
    if chart_method==4:
        navamsa_dict = {0:(1,const.fire_signs),3:(-1,const.water_signs),6:(1,const.air_signs),9:(-1,const.earth_signs)}
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = [(seed+dirn*l)%12 for seed,(dirn,sign_list) in navamsa_dict.items() if sign in sign_list][0]
        dp.append([planet,[r,d_long]])
    return dp
def dasamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Dasamsa Chart - D10 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara (start from 9th and go forward)
            2=>Parasara even signs (start from 9th and go backward)
            3=>Parasara even signs (start from reverse 9th and go backward)
            4=>Parivritti Cyclic (Ojha)
            5=>Parivritti Even Reverse
            6=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 10; f1 = 30.0/dvf
    if chart_method==4:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==5:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==6:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    dirn = -1 if chart_method in [2,3] else 1
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+dirn*(l+8))%12
            if chart_method==2:
                r = (r-8)%12
        dp.append([planet,[r,d_long]])
    return dp
def rudramsa_chart(planet_positions_in_rasi,chart_method=11):
    """ 
        Rudramsa Chart - D11 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara (Sanjay Rath)
            2=>BV Raman (Ekadasamsa - Anti-zodiacal)
            3=>Parivritti Cyclic
            4=>Parivritti Even Reverse
            5=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    """
        Check calculation against PVR book
    """
    dvf = 11; f1 = 30.0/dvf
    if chart_method==3:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==5:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (12-sign+l)%12
        if chart_method==2: r = (11-r)%12
        dp.append([planet,[r,d_long]])
    return dp
def dwadasamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Dwadasamsa Chart - D12 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Traditional Parasara with even sign reversal
            3=>Parivritti Cyclic
            4=>Parivritti Even Reverse
            5=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 12; f1 = 30.0/dvf
    if chart_method==3:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==5:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        dirn = -1 if sign in const.even_signs and chart_method==2 else 1
        l = (int(long//f1))
        dp.append([planet,[(sign+dirn*l)%12,(long*dvf)%30]])
    return dp
def kalamsa_chart(planet_positions_in_rasi,chart_method=1):
    return shodasamsa_chart(planet_positions_in_rasi, chart_method)
def shodasamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Shodasamsa Chart - D16 Chart Also called Kalamsa
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Traditional Parasara with even sign reversal
            3=>Parivritti Cyclic
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 16; f1 = 30.0/dvf
    if chart_method==3:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==2:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
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
def vimsamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Vimsamsa Chart - D20 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Traditional Parasara with even sign reversal
            3=>Parivritti Cyclic
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 20; f1 = 30.0/dvf
    if chart_method==3:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==2:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
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
def siddhamsa_chart(planet_positions_in_rasi,chart_method=1):
    return chaturvimsamsa_chart(planet_positions_in_rasi,chart_method=chart_method)
def chaturvimsamsa_chart(planet_positions_in_rasi,chart_method=3):
    """ 
        Chathur Vimsamsa Chart - D24 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method
            1=> Traditional Parasara Siddhamsa (Odd Le->Cn, Even Cn->Ge) -  Default
            2=> Parasara with even sign reversal (Odd Le-> Cn, Even Cn->Le)
            3=> Parasara Siddhamsa with even sign double reversal (Odd Le->Cn, Even Le->Cn) 
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 24; f1 = 30.0/dvf; dp = []
    even_dirn = -1 if chart_method==2 else 1
    odd_base = 4
    even_base = 4 if chart_method == 3 else 3
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (odd_base+l)%12 #4 = Leo
        if sign in const.even_signs:
            r = (even_base+even_dirn*l)%12 # 3 = Cancer
        dp.append([planet,[r,d_long]])
    return dp
def nakshatramsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Nakshatramsa Chart - D27 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Traditional Parasara with even sign reversal
            3=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 27; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
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
def trimsamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Trimsamsa Chart - D30 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti cyclical trimsamsa
            3=>Shastyamsa like trimsamsa
            4=>Parivritti Even Reverse
            5=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 30; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==5:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
    # Traditional Parasara Method
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
def khavedamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Khavedamsa Chart - D40 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti cyclical khavedamsa
            3=>Parivritti khavedamsa even reversal
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 40; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 #part from Aries
        if sign in const.even_signs:
            r = (l+6)%12 # Part from Libra
        dp.append([planet,[r,d_long]])
    return dp
def akshavedamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Akshavedamsa Chart - D45 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti cyclical akshavedamsa
            3=>Parivritti akshavedamsa even Reversal
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 45; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
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
def shashtyamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Shashtyamsa Chart - D60 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara shashtyamsa (from sign)
            2=>Parasara Shastyamsa (from Aries) - Same as Parvritti Cyclic
            3=>Parasara shashtyamsa even reversal (from Aries)
            4=>Parasara shashtyamsa even reversal (from sign)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 60; f1 = 30.0/dvf
    if chart_method==3: #Parasara (from Aries even reverse)
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dirn = -1 if (sign in const.even_signs and chart_method in [4]) else 1
        seed = 0 if chart_method in [2] else sign
        dp.append([planet,[(seed+dirn*l)%12,d_long]])
    return dp
def nava_navamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Nava Navamsa Chart - D81 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara (Parivritti Cyclic)
            2=>Parivritti Even Reverse
            3=>Parivritti Alternate (aka Somanatha)
            4=>Kalachakra nava navamsa (NOT IMPLEMENTED YET)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 81; f1 = 30.0/dvf
    if chart_method==1:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==2:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    pp1 = _navamsa_kalachakra(planet_positions_in_rasi,9)
    pp2 = _navamsa_kalachakra(pp1,9)
    return pp2
def ashtotharamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Ashtotharamsa Chart - D108 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti Cyclic
            3=>Parivritti Even Reverse
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 108; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dvf_1 = 9; chart_method_1=1; dvf_2=12; chart_method_2=1
    pp = mixed_chart_from_rasi_positions(planet_positions_in_rasi, varga_factor_1=dvf_1, chart_method_1=chart_method_1, 
                      varga_factor_2=dvf_2, chart_method_2=chart_method_2)
    return pp
def dwadas_dwadasamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Dwadas Dwadasamsa Chart - D144 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara
            2=>Parivritti Cyclic
            3=>Parivritti Even Reverse
            4=>Parivritti Alternate (aka Somanatha)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 144; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dvf_1 = 12; chart_method_1=1; dvf_2=12; chart_method_2=1
    pp = mixed_chart_from_rasi_positions(planet_positions_in_rasi,varga_factor_1=dvf_1,chart_method_1=chart_method_1,
                      varga_factor_2=dvf_2, chart_method_2=chart_method_2)
    return pp
def nadiamsa_chart(planet_positions_in_rasi,chart_method=1):
    """ 
        Nadiamsa Chart - D150 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara shashtyamsa (from sign)
            2=>Parasara Shastyamsa (from Aries) - Same as Parvritti Cyclic
            3=>Parasara shashtyamsa even reversal (from Aries)
            4=>Parasara shashtyamsa even reversal (from sign)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    return divisional_positions_from_rasi_positions(planet_positions_in_rasi, divisional_chart_factor=150,
                                                    chart_method=chart_method)
def custom_divisional_chart(planet_positions_in_rasi,divisional_chart_factor,chart_method=0,
                            base_rasi=None,count_from_end_of_sign=False):
    """ 
        Generates D-N chart (cyclic or non cyclic)
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param divisional_chart_factor: 1.. 300
        @param chart_method:
            0=>Cyclic Parivritti variation (base_rasi=None for cyclic and base_rasi=Aries/sign for non-cyclic)
            For Non-cyclic following parameters apply
            0=>From base for all signs
            1=>1st/7th from base if sign is odd/even
            2=>1st/9th from base if sign is odd/even
            3=>1st/5th from base if sign is odd/even
            4=>1st/11th from base if sign is odd/even
            5=>1st/3rd from base if sign is odd/even
            6=>1st/5th/9th from base if sign is movable/fixed/dual
            7=>1st/9th/5th from base if sign is movable/fixed/dual
            8=>1st/4th/7th/10th from base if sign is fire/earth/air/water
            9=>1st/10th/7th/4th from base if sign is fire/earth/air/water
        @param base_rasi: 
            None for cyclic variation 
            And for non-cyclic variation:0=>Base is Aries 1=>base is the sign
        @param count_from_end_of_sign=False. 
            If True = Count N divisions from end of the sign if sign is even
            And go anti-zodiac from there by N signs
            TODO: THIS PARAMETER IS NOT MATCHING WITH JHORA - STILL UNDER EXPERIMENT
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = divisional_chart_factor; f1 = 30.0/dvf
    if base_rasi==None:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf,dirn=1)
    _hora_list = utils.__varga_non_cyclic(dvf, base_rasi=base_rasi, start_sign_variation=chart_method,
                                             count_from_end_of_sign=count_from_end_of_sign)
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // f1)
        hora_sign = _hora_list[rasi_sign][hora]
        dp.append([planet,[hora_sign,d_long]])
    return dp
def mixed_chart(jd,place,varga_factor_1=None,chart_method_1=1,varga_factor_2=None,chart_method_2=1):
    planet_positions_in_rasi = rasi_chart(jd,place)
    if varga_factor_1==1 and varga_factor_2==1: return planet_positions_in_rasi
    pp1 = planet_positions_in_rasi if varga_factor_1==1 else \
            eval(divisional_chart_functions[varga_factor_1]+'(planet_positions_in_rasi,chart_method=chart_method_1)')
    pp2 = pp1 if varga_factor_2==2 else eval(divisional_chart_functions[varga_factor_2]+'(pp1,chart_method=chart_method_2)')
    return pp2
def mixed_chart_from_rasi_positions(planet_positions_in_rasi,varga_factor_1=None,chart_method_1=1,varga_factor_2=None,chart_method_2=1):
    pp1 = eval(divisional_chart_functions[varga_factor_1]+'(planet_positions_in_rasi,chart_method=chart_method_1)')
    pp2 = eval(divisional_chart_functions[varga_factor_2]+'(pp1,chart_method=chart_method_2)')
    return pp2
def divisional_positions_from_rasi_positions(planet_positions_in_rasi,divisional_chart_factor=1,
                     chart_method=1,base_rasi=None,count_from_end_of_sign=None):
    if divisional_chart_factor==1:
        return planet_positions_in_rasi
    else:
        if (not const.TREAT_STANDARD_CHART_AS_CUSTOM) and (divisional_chart_factor in divisional_chart_functions.keys()\
                and (base_rasi==None and (chart_method !=None and chart_method >0) )):
            return eval(divisional_chart_functions[divisional_chart_factor]+'(planet_positions_in_rasi,chart_method)')
        elif divisional_chart_factor in range(1,const.MAX_DHASAVARGA_FACTOR+1):
            return custom_divisional_chart(planet_positions_in_rasi, divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        else:
            print('Chart division factor',divisional_chart_factor,'not supported')
            return None
    
def divisional_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                     chart_method=1,years=1,months=1,sixty_hours=1,calculation_type='drik',pravesha_type=0,
                     base_rasi=None,count_from_end_of_sign=None):
    """
        Get divisional/varga chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.divisional_chart_factors for options
        @param chart_method: See individual chart function for available chart methods 
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param treat_standard_chart_as_custom: 
            False (default) => Standard chart calculations will be followed for standard vargas
            True => Custom chart calculations will be followed for even standard vargas
            Note: Even if custom_chart=False but divisional_chart_factor is not a standard one, 
            it will be processed as custom. This can be changed by setting const.TREAT_STANDARD_CHART_AS_CUSTOM=True
        @param base_rasi:
            None: Cyclic Variation for custom chart calculation. chart_method,count_from_end_of_sign will be ignored.
            0   : Non-Cyclic Variation - Aries to be used as the base
            1   : Non-Cyclic Variation - The sign to be used as the base
        @param chart_method: 0,1,2,3 etc
            For standard charts (treat_standard_chart_as_custom=False) - available standard chart methods will be used.
                Refer to individual chart function for methods available 
                values start from 1
            For Custom charts (treat_standard_chart_as_custom=True) - See custom_divisional_chart for details
        @param count_from_end_of_sign: Applicable only for non-cyclic variation
            False (default)
            True = Count N divisions from end of the sign if sign is even
            And go anti-zodiac from there by N signs
            TODO: THIS PARAMETER IS NOT MATCHING WITH JHORA - STILL UNDER EXPERIMENT
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
    """
    planet_positions_in_rasi = rasi_chart(jd_at_dob, place_as_tuple, ayanamsa_mode,years,months,sixty_hours,
                                  calculation_type=calculation_type,pravesha_type=pravesha_type)
    return divisional_positions_from_rasi_positions(planet_positions_in_rasi, divisional_chart_factor=divisional_chart_factor,
                    chart_method=chart_method, base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)
def _planets_in_retrograde_old(planet_positions):
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
        NOTE: DO NOT USE THIS. THIS IS NOT ACCURATE AND WILL BE REMOVED IN FUTURE VERSIONS
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
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
        NOTE: USE THIS FUNCTION ONLY IF YOU HAVE TO PASS planet_positions as argument
        OTHERWISE FOR ACCURATE RESULTS use drik.planets_in_retrograde(jd, place)
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
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.dhasavarga_amsa_vaiseshikamsa)
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
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.shadvarga_amsa_vaiseshikamsa)
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
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.sapthavarga_amsa_vaiseshikamsa)
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
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.shodhasa_varga_amsa_vaiseshikamsa)
def _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                                   amsa_vaiseshikamsa=None):
    p_d = [0 for _ in range(9)]
    p_d_s = [0 for _ in range(9)]
    p_d_c = ['' for _ in range(9)]
    for dcf in amsa_vaiseshikamsa.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,ayanamsa_mode,
                                            divisional_chart_factor=dcf)[:const._pp_count_upto_ketu]
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
def _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,amsa_vimsopaka=None):
    p_d = [0 for _ in range(9)]
    p_d_s = [0 for _ in range(9)]
    p_d_c = ['' for _ in range(9)]
    scores = [5,7,10,15,18]
    for dcf in amsa_vimsopaka.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,ayanamsa_mode,divisional_chart_factor=dcf)[:const._pp_count_upto_ketu]
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
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.dhasavarga_amsa_vimsopaka)
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
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.shadvarga_amsa_vimsopaka)
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
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.sapthavarga_amsa_vimsopaka)
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
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,ayanamsa_mode,const.shodhasa_varga_amsa_vimsopaka)
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
    for _, dcf in enumerate(const.vimsamsa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=dcf)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(_world_city_db_df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_vimsamsa[p] += 1
    return planet_vimsamsa
def _varnada_lagna_sanjay_rath_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    asc_sign = (asc_sign+house_index-1)%12
    asc_long = asc_sign*30+asc_long
    hora_sign,hora_long = drik.hora_lagna_mixed_chart(jd_at_dob,place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    hora_sign = (hora_sign+house_index-1)%12
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
def _varnada_lagna_sanjay_rath(dob,tob, place,house_index=1, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                               divisional_chart_factor=1,chart_method=1,
                                       base_rasi=None,count_from_end_of_sign=None):
    """ TO DO : Still experimenting """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                        chart_method=chart_method,base_rasi=base_rasi,
                                        count_from_end_of_sign=count_from_end_of_sign)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    asc_sign = (asc_sign+house_index-1)%12
    asc_long = asc_sign*30+asc_long
    hora_sign,hora_long = drik.hora_lagna(jd_at_dob,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                          chart_method=chart_method)
    hora_sign = (hora_sign+house_index-1)%12
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
def _varnada_lagna_jha_pandey_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    lagna = (asc_sign+house_index-1)%12
    asc_long = lagna*30+asc_long
    lagna_is_odd = lagna in const.odd_signs
    if not lagna_is_odd: asc_long = 360.-asc_long
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_sign,hora_long = drik.hora_lagna_mixed_chart(jd_at_dob,place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
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
def _varnada_lagna_jha_pandey(dob,tob, place,house_index=1,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                              divisional_chart_factor=1,chart_method=1,base_rasi=None,
                              count_from_end_of_sign=None):
    """ TO DO : Still experimenting """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                        chart_method=chart_method,base_rasi=base_rasi,
                                        count_from_end_of_sign=count_from_end_of_sign)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    lagna = (asc_sign+house_index-1)%12
    asc_long = lagna*30+asc_long
    lagna_is_odd = lagna in const.odd_signs
    if not lagna_is_odd: asc_long = 360.-asc_long
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_sign,hora_long = drik.hora_lagna(jd_at_dob,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                          chart_method=chart_method)
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
def varnada_lagna_mixed_chart(dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,house_index=1,varga_factor_1=1,
                              chart_method_1=1,varga_factor_2=1,chart_method_2=1,varnada_method=1):
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
                               4=Sitaram Jha/Prof. Ramachandra Pandey - last count decides last step direction / count on longitudes
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    if varnada_method==1:
        return _varnada_lagna_bv_raman_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_2, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2)
    elif varnada_method==2:
        return _varnada_lagna_sharma_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_2, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2)
    elif varnada_method==3:
        return _varnada_lagna_sanjay_rath_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_2, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2)
    elif varnada_method==4:
        return _varnada_lagna_jha_pandey_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_2, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2)
def varnada_lagna(dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                  chart_method=1,house_index=1,varnada_method=1,base_rasi=None,count_from_end_of_sign=None):
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
                               4=Sitaram Jha/Prof. Ramachandra Pandey - last count decides last step direction / count on longitudes
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    if varnada_method==1:
        return _varnada_lagna_bv_raman(dob, tob, place, house_index, ayanamsa_mode=ayanamsa_mode,
                                       divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    elif varnada_method==2:
        return _varnada_lagna_sharma(dob, tob, place, house_index, ayanamsa_mode=ayanamsa_mode,
                                     divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    elif varnada_method==3:
        return _varnada_lagna_sanjay_rath(dob, tob, place, house_index, ayanamsa_mode=ayanamsa_mode,
                                          divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    elif varnada_method==4:
        return _varnada_lagna_jha_pandey(dob, tob, place, house_index, ayanamsa_mode=ayanamsa_mode,
                                         divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
def _varnada_lagna_bv_raman_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_lagna,_ = drik.hora_lagna_mixed_chart(jd_at_dob,place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if hora_lagna_is_odd == lagna_is_odd else (max(count1,count2) - min (count1,count2))%12
    _varnada_lagna = utils.count_rasis(1,count,dir=1) if lagna_is_odd else utils.count_rasis(12,count,dir=-1)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return _varnada_lagna, asc_long #hl
def _varnada_lagna_bv_raman(dob,tob,place,house_index=1,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                            divisional_chart_factor=1,chart_method=1,base_rasi=None,count_from_end_of_sign=None):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varnada_lagna_rasi, varnada_lagna_longitude 
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob,place,ayanamsa_mode=ayanamsa_mode,
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                          chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign) # V3.1.9
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if hora_lagna_is_odd == lagna_is_odd else (max(count1,count2) - min (count1,count2))%12
    _varnada_lagna = utils.count_rasis(1,count,dir=1) if lagna_is_odd else utils.count_rasis(12,count,dir=-1)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return _varnada_lagna, asc_long #hl
def _varnada_lagna_santhanam_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1):
    return _varnada_lagna_sharma_mixed_chart(dob, tob, place, house_index, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
def _varnada_lagna_santhanam(dob,tob,place,house_index=1,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                             divisional_chart_factor=1,chart_method=1,
                                       base_rasi=None,count_from_end_of_sign=None):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varnada_lagna_rasi, varnada_lagna_longitude 
    """
    return _varnada_lagna_sharma(dob, tob, place, house_index,ayanamsa_mode=ayanamsa_mode,
                                 divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
def _varnada_lagna_sharma_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = mixed_chart(jd_at_dob, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_lagna,_ = drik.hora_lagna_mixed_chart(jd_at_dob,place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if count1%2 == count2%2 else (max(count1,count2) - min (count1,count2))%12
    count_is_odd = count%2 != 0
    _varnada_lagna = utils.count_rasis(1,count,dir=1) if count_is_odd else utils.count_rasis(12,count,dir=-1)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return _varnada_lagna, asc_long #hl
def _varnada_lagna_sharma(dob,tob,place,house_index=1,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                          divisional_chart_factor=1,chart_method=1,
                                       base_rasi=None,count_from_end_of_sign=None):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varnada_lagna_rasi, varnada_lagna_longitude 
    """
    _debug_ = False
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = divisional_chart(jd_at_dob,place,ayanamsa_mode=ayanamsa_mode,
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,dir=1) if lagna_is_odd else utils.count_rasis(11,lagna,dir=-1)
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place,ayanamsa_mode=ayanamsa_mode,
                                   divisional_chart_factor=divisional_chart_factor,
                                          chart_method=chart_method,
                                       base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign) # V3.1.9
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,dir=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,dir=-1)
    count = (count1 + count2)%12 if count1%2 == count2%2 else (max(count1,count2) - min (count1,count2))%12
    count_is_odd = count%2 != 0
    _varnada_lagna = utils.count_rasis(1,count,dir=1) if count_is_odd else utils.count_rasis(12,count,dir=-1)
    #print(count1,count2,count,count_is_odd,_varnada_lagna)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return _varnada_lagna, asc_long #hl
def benefics_and_malefics(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,method=2,
                          exclude_rahu_ketu=False):
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
        From VP Jain - Shadbala and Bhavabala:
        In addition If Mars is associated with both malefics and benefics
            (i) count of malefics/benefics decide
            (ii) if count is same one nearer to Mars in longitude decides
    """
    benefics = const.natural_benefics[:]
    malefics = const.natural_malefics[:-2] if exclude_rahu_ketu else const.natural_malefics[:]
    _tithi = drik.tithi(jd, place)[0]
    if method == 2:
        if _tithi > 15:
            malefics.append(1)
        else:
            benefics.append(1)
    else:
        if _tithi >= 8 and _tithi <=15: benefics.append(1)
        if _tithi >= 23 and _tithi <=30: malefics.append(1) 
    planet_positions = divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor)
    #malefics += [3 for p in malefics if planet_positions[p+1][1][0]==planet_positions[4][1][0]]
    #benefics += [3 for p in benefics if planet_positions[p+1][1][0]==planet_positions[4][1][0]]
    mars_malefics = [p for p in malefics if planet_positions[p+1][1][0]==planet_positions[4][1][0] ]
    mars_malefics_count = len(mars_malefics)
    mars_benefics = [p for p in benefics if planet_positions[p+1][1][0]==planet_positions[4][1][0] ]
    mars_benefics_count = len(mars_benefics)
    #if 3 not in benefics + malefics: benefics +=[3] # Merc benefic if alone
    if mars_benefics_count==0 and mars_malefics_count==0 or mars_benefics_count > mars_malefics_count:
        benefics +=[3] # Merc benefic if alone or with more benefics than malefics
    elif mars_malefics_count > mars_benefics_count :
        malefics +=[3] # Merc with more malefics than benefics
    elif mars_benefics_count == mars_malefics_count:
        mercury_house, mercury_long = next((h, l) for p, (h, l) in planet_positions if p == 3)
        planet_closest_to_mars = min(
            [p for p, (h, l) in planet_positions if h == mercury_house and p != 3],
            key=lambda p: abs(next(l for x, (h, l) in planet_positions if x == p) - mercury_long),
            default=None
        )
        #print(mars_benefics,mars_malefics,'planet_closest_to_mars',planet_closest_to_mars,planet_positions[planet_closest_to_mars+1][1][1],planet_positions[4][1][1])
        if planet_closest_to_mars in benefics:
            benefics += [3]
        else:
            malefics += [3] 
    benefics = sorted(set(benefics)) ; malefics = sorted(set(malefics))
    return benefics, malefics
def benefics(jd,place,divisional_chart_factor=1,method=2,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,exclude_rahu_ketu=False):
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
        From VP Jain - Shadbala and Bhavabala:
        In addition If Mars is associated with both malefics and benefics
            (i) count of malefics/benefics decide
            (ii) if count is same one nearer to Mars in longitude decides
    """
    return benefics_and_malefics(jd, place, method=method,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                 exclude_rahu_ketu=exclude_rahu_ketu)[0]
def malefics(jd,place,divisional_chart_factor=1,method=2,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,exclude_rahu_ketu=False):
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
        From VP Jain - Shadbala and Bhavabala:
        In addition If Mars is associated with both malefics and benefics
            (i) count of malefics/benefics decide
            (ii) if count is same one nearer to Mars in longitude decides
    """
    return benefics_and_malefics(jd, place, method=method,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                 exclude_rahu_ketu=exclude_rahu_ketu)[1]
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
def _stronger_planet_from_the_chart(chart_1d,planet_list):
    def _compare(planet1,planet2):
        return 1 if house.stronger_planet(chart_1d, planet1, planet2)==planet1 else -1 
    from functools import cmp_to_key
    planet_list.sort(key=cmp_to_key(_compare))
    return planet_list[0]    
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
def special_planet_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    spl_planet_positions_in_rasi = special_planet_longitudes(dob, tob, place)
    if varga_factor_1==1 and varga_factor_2==1: return spl_planet_positions_in_rasi
    pp1 = spl_planet_positions_in_rasi if varga_factor_1==1 else \
            eval(divisional_chart_functions[varga_factor_1]+'(spl_planet_positions_in_rasi,chart_method=chart_method_1)')
    pp2 = pp1 if varga_factor_2==2 else eval(divisional_chart_functions[varga_factor_2]+'(pp1,chart_method=chart_method_2)')
    return pp2
def special_planet_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=None,
                              base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    sub_planet_list_1 = {'Kl':'kaala_longitude','Mr':'mrityu_longitude','Ap':'artha_praharaka_longitude','Yg':'yama_ghantaka_longitude',
                       'Gk':'gulika_longitude','Md':'maandi_longitude'}
    spl_rasi_positions = []
    for sp,sp_func in sub_planet_list_1.items():
        v = eval('drik.'+sp_func+'(dob,tob,place)')
        spl_rasi_positions.append([sp,[v[0],v[1]]]) 
    #"""
    sub_planet_list_2 = {'Dm':'dhuma','Vp':'vyatipaata','Pv':'parivesha','Ic':'indrachaapa','Uk':'upaketu'}
    sun_long = rasi_chart(jd_at_dob, place)[1][1]; sun_long = sun_long[0]*30+sun_long[1]
    for sp,sp_func in sub_planet_list_2.items():
        eval_str = "drik.solar_upagraha_longitudes(sun_long,upagraha='"+str(sp_func)+"')"
        v = eval(eval_str)
        spl_rasi_positions.append([sp,[v[0],v[1]]]) 
    #"""
    if divisional_chart_factor==1: return spl_rasi_positions
    if (not const.TREAT_STANDARD_CHART_AS_CUSTOM) and (divisional_chart_factor in divisional_chart_functions.keys()\
            and (base_rasi==None and (chart_method !=None and chart_method >0) )):
        return eval(divisional_chart_functions[divisional_chart_factor]+'(spl_rasi_positions,chart_method)')
    elif divisional_chart_factor in range(1,const.MAX_DHASAVARGA_FACTOR+1):
        return custom_divisional_chart(spl_rasi_positions, divisional_chart_factor=divisional_chart_factor,
                    chart_method=chart_method,base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
    else:
        print('Chart division factor',divisional_chart_factor,'not supported')
        return None
def special_lagna_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1,
                             base_rasi=None,count_from_end_of_sign=None):
    jd_at_dob = utils.julian_day_number(dob, tob)
    """ For now let us comment this here as there is no longitude for arudha lagna
    _sp_lagna_list = ['AL']+['A'+str(l) for l in range(2,12)]+['UL']
    spl_rasi_positions = []
    from jhora.horoscope.chart import arudhas
    if divisional_chart_factor==1: spl_rasi_positions=arudhas.bhava_arudhas_from_planet_positions(spl_rasi_positions)
    """
def solar_upagraha_longitudes(planet_positions,upagraha,divisional_chart_factor=1):
    """
        Get logitudes of solar based upagrahas
        ['dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu']
        @param planet_positions: Planet Positions (return value of rasi_chart or divisional_chart functions)
        @param upagraha: one of the values from ['dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu']
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [constellation,longitude]
    """
    solar_longitude = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    return drik.solar_upagraha_longitudes(solar_longitude, upagraha, divisional_chart_factor=divisional_chart_factor)
def _amsa(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,include_upagrahas=False,
          include_special_lagnas=False,include_sphutas=False,chart_method=1,base_rasi=None,count_from_end_of_sign=None):
    "TODO: Still under testing - Exact algorithm not clear"
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob = (fh,0,0)
    div_planet_positions = divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                                            chart_method=chart_method,base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign)
    def _get_amsa_index_from_longitude(p_long):
        df = 30.0/divisional_chart_factor
        return int(p_long/df)
    __amsa_planets = {}; __amsa_special = {}; __amsa_upagraha = {}; __amsa_sphuta = {}
    for p,(_,long) in div_planet_positions:
        __amsa_planets[p] = _get_amsa_index_from_longitude(long)
    if include_special_lagnas:
        special_lagna_dict = {'bhava_lagna_str':0.25,'hora_lagna_str':0.5,'ghati_lagna_str':1.25,'pranapada_lagna_str':5.0,
                                 'vighati_lagna_str':15.0} #Bhava,hora,ghati,pranapada,vighati
        for sl,lf in special_lagna_dict.items():
            sf = drik.special_ascendant(jd, place,ayanamsa_mode=ayanamsa_mode,
                                        divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                        lagna_rate_factor=lf,base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
            __amsa_special[sl] = _get_amsa_index_from_longitude(sf[1])
        il = drik.indu_lagna(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                             chart_method=chart_method,base_rasi=base_rasi,
                             count_from_end_of_sign=count_from_end_of_sign)
        __amsa_special['indu_lagna_str'] = _get_amsa_index_from_longitude(il[1])
        bl = drik.bhrigu_bindhu_lagna(jd, place,ayanamsa_mode=ayanamsa_mode, divisional_chart_factor=divisional_chart_factor,
                                chart_method=chart_method,base_rasi=base_rasi,
                                count_from_end_of_sign=count_from_end_of_sign)
        __amsa_special['bhrigu_bindhu_lagna_str'] = _get_amsa_index_from_longitude(bl[1])
        kl = drik.kunda_lagna(jd, place,ayanamsa_mode=ayanamsa_mode, divisional_chart_factor=divisional_chart_factor,
                                chart_method=chart_method,base_rasi=base_rasi,
                                count_from_end_of_sign=count_from_end_of_sign)
        __amsa_special['kunda_lagna_str'] = _get_amsa_index_from_longitude(kl[1])
        sl = drik.sree_lagna(jd, place,ayanamsa_mode=ayanamsa_mode, divisional_chart_factor=divisional_chart_factor,
                             base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        __amsa_special['sree_lagna_str'] = _get_amsa_index_from_longitude(sl[1])
        vl = varnada_lagna(dob, tob, place,ayanamsa_mode=ayanamsa_mode, divisional_chart_factor=divisional_chart_factor,
                           chart_method=chart_method,house_index=1,base_rasi=base_rasi,
                           count_from_end_of_sign=count_from_end_of_sign)
        __amsa_special['varnada_lagna_str'] = _get_amsa_index_from_longitude(vl[1])
    if include_upagrahas:
        sub_planet_list_1 = {'kaala_str':'kaala_longitude','mrityu_str':'mrityu_longitude','artha_str':'artha_praharaka_longitude','yama_str':'yama_ghantaka_longitude',
                           'gulika_str':'gulika_longitude','maandi_str':'maandi_longitude'}
        sub_planet_list_2 = ['dhuma','vyatipaata','parivesha','indrachaapa','upaketu']
        sun_long = div_planet_positions[1][1][0]*30+div_planet_positions[1][1][1]
        for sp,sp_func in sub_planet_list_1.items():
            v = eval('drik.'+sp_func+'(dob,tob,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor)')
            __amsa_upagraha[sp] = _get_amsa_index_from_longitude(v[1])
        for sp in sub_planet_list_2:
            v = eval('solar_upagraha_longitudes(div_planet_positions,sp,divisional_chart_factor=divisional_chart_factor)')
            __amsa_upagraha[sp+'_str'] = _get_amsa_index_from_longitude(v[1])
    if include_sphutas:
        from jhora.horoscope.chart import sphuta
        for s in const.sphuta_list:
            fn = 'sphuta.'+s+'_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor)'
            sp = eval(fn)
            __amsa_sphuta[s+'_sphuta_str'] = _get_amsa_index_from_longitude(sp[1])
    return __amsa_planets, __amsa_special, __amsa_upagraha,__amsa_sphuta
def _get_KP_lords_from_planet_longitude(planet,rasi,rasi_longitude):
    lords = const.vimsottari_adhipati_list
    lord_fractions = [7/120, 20/120,6/120,10/120,7/120,18/120,16/120,19/120,17/120]
    next_lord = lambda lord,dirn=1: lords[(lords.index(lord) + dirn) % len(lords)]
    p = planet; h = rasi; long = rasi_longitude
    kp_info = {}
    p_long = h*30+long
    kp_details = utils.get_KP_details_from_planet_longitude(p_long)
    kp_no, details = list(kp_details.items())[0]
    rasi,nak,sd,ed,sign_lord,star_lord,star_sub_lord = details
    kp_info[p] = [kp_no,star_lord,star_sub_lord]
    sub_lord = star_sub_lord
    for _ in range(4):
        # get Sub Sub Lords
        sub_sub_lord = sub_lord
        count = 1; durn = (ed-sd)
        while True:
            ed = sd + lord_fractions[sub_sub_lord]*durn
            #print('sub-level=',sub,'count',count,sd, p,long,ed)
            if (long > sd and long < ed) or count > 9: 
                #if count > 9:
                #    print(p,' not converging check')
                break
            sub_sub_lord = next_lord(sub_sub_lord)
            count += 1; sd = ed
        kp_info[p] += [sub_sub_lord]
        sub_lord = sub_sub_lord
    return kp_info
def get_KP_lords_from_planet_positions(planet_positions):
    kp_info = {}
    for p,(h,long) in planet_positions:
        kp_info_planet = _get_KP_lords_from_planet_longitude(p, h, long)
        kp_info = {**kp_info, **kp_info_planet}
    return kp_info
def get_pachakadi_sambhandha(planet_positions):
    prd = {planet:[(planet_positions[_pre[0]+1][1][0]==(planet_positions[planet+1][1][0]+_pre[1]-1)%12,_pre[2]) for _pre in _pr] for planet,_pr in const.paachakaadi_sambhandha.items()}
    #pachakadi_relation_dict = {key: (index, char) for key, value in prd.items() for index, (flag, char) in enumerate(value) if flag}
    #"""
    pachakadi_relation_dict = {
        key: [index,const.paachakaadi_sambhandha[key][index]]
        for key, value in prd.items()
        for index, (flag, char) in enumerate(value) if flag
    }
    #"""
    return pachakadi_relation_dict
def planets_in_pushkara_navamsa_bhaga(planet_positions):
    pna = [planet for planet, (sign,long) in planet_positions[1:const._pp_count_upto_ketu] \
           if (long >= const.pushkara_navamsa[sign] and long < const.pushkara_navamsa[sign]+(30/9)) or \
           (long >= const.pushkara_navamsa[sign]+60/9 and long < const.pushkara_navamsa[sign]+10) \
           ]
    #for planet, (sign,long) in planet_positions:
    #    print('pushkara navamsa',planet,sign,const.pushkara_navamsa[sign],long,const.pushkara_navamsa[sign]+(30/9))
    #    print('pushkara navamsa',planet,sign,const.pushkara_navamsa[sign]+60/9,long,const.pushkara_navamsa[sign]+10)
    pb = [planet for planet, (sign,long) in planet_positions[1:const._pp_count_upto_ketu] if long >= const.pushkara_bhagas[sign]-1 and long < const.pushkara_bhagas[sign]]
    #for planet, (sign,long) in planet_positions:
    #    print('pushkara bhaga',planet,sign,const.pushkara_bhagas[sign]-1,long,const.pushkara_bhagas[sign])
    return pna,pb
def planets_in_mrityu_bhaga(dob,tob,place,planet_positions):
    """
        returns the list of planets in the mrityu bhaga
        @return: [(planet,rasi,diff in long from mrityu longitude),...()...]
    """
    # Add Mandi planet positions list
    planet_positions = planet_positions[:const._pp_count_upto_ketu]+[['Md',drik.maandi_longitude(dob,tob,place)]]
    def compare_planet_positions(planet_positions):
        result = []
        planet_names = [*range(const._planets_upto_ketu)]+['Md', 'L']
        planet_indices = {name: idx for idx, name in enumerate(planet_names)}
    
        for planet, (rasi, longitude) in planet_positions:
            if planet in planet_indices:
                planet_index = planet_indices[planet]
            else:
                planet_index = int(planet)
            
            tolerance = const.mrityu_bhaga_tolerances[planet] if planet in ['Md', 'L'] else const.mrityu_bhaga_tolerances[planet_index]
            
            base_longitude = const.mrityu_bhaga_base_longitudes[rasi][planet_index]
            long_diff = abs(longitude - base_longitude)
            if long_diff <= tolerance:
                result.append((planet_names[planet_index], rasi, long_diff))
        
        return result
    return compare_planet_positions(planet_positions)
def get_planets_in_marana_karaka_sthana(planet_positions,consider_ketu_4th_house=True):
    mks_planets = []; asc_house = planet_positions[0][1][0]
    p_end = const._pp_count_upto_ketu if consider_ketu_4th_house else const._pp_count_upto_rahu
    for planet,(rasi,_) in planet_positions[1:p_end]:
        planet_house = house.get_relative_house_of_planet(asc_house,rasi)
        if planet_house == const.marana_karaka_sthana_of_planets[planet]:
            mks_planets.append((planet,planet_house))
    return mks_planets
def previous_planet_entry_date_divisional_chart(jd,place,planet,divisional_chart_factor=1,chart_method=1,base_rasi=None,
                              count_from_end_of_sign=None,increment_days=1,precision=0.1,raasi=None):
    return next_planet_entry_date_divisional_chart(jd,place,planet,divisional_chart_factor=divisional_chart_factor,direction=-1,
                                  chart_method=chart_method,base_rasi=base_rasi,
                                  count_from_end_of_sign=count_from_end_of_sign,increment_days=increment_days,
                                  precision=precision,raasi=raasi)
def next_planet_entry_date_divisional_chart(jd,place,planet,divisional_chart_factor=1,direction=1,chart_method=1,base_rasi=None,
                              count_from_end_of_sign=None,increment_days=1,precision=0.1,raasi=None):
    """
        get the date when the ascendant enters a zodiac
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param direction: 1= next entry, -1 previous entry
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param precision: precision in degrees within which longitude entry whould be (default: 0.1 degrees)
        @param raasi: raasi at which planet should enter. 
            If raasi==None: gives entry to next constellation
            If raasi is specified [1..12] gives entry to specified constellation/raasi
        @return Julian day number of planet entry into zodiac
    """
    if planet==8:
        raghu_raasi = (raasi-1+6)%12+1 if raasi!=None else raasi
        ret = next_planet_entry_date_divisional_chart(jd, place,7,divisional_chart_factor=divisional_chart_factor,
                                                      direction=direction,raasi=raghu_raasi)
        p_long = (ret[1]+180)%360
        return ret[0],p_long
    increment_days=1.0/24.0/60.0/divisional_chart_factor if planet in ['L',1] else 0.1/divisional_chart_factor
    planet_index = 0 if planet=='L' else planet+1
    sla = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor, 
                chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[planet_index][1]
    sl = sla[0]*30+sla[1]
    if raasi==None:
        multiple = (((sl//30)+1)%12)*30
        if direction==-1: multiple = (sl//30)%12*30
        if planet == 7:
            multiple = ((sl//30)%12 * 30)%360
            if direction==-1:
                multiple = ((sl//30+1)%12*30)%360
    else: 
        multiple = (raasi-1)*30
    #print(sla,multiple)
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        jd += increment_days*direction
        sla = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor, 
                    chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[planet_index][1]
        sl = sla[0]*30+sla[1]
    #print(sla,utils.jd_to_gregorian(jd))
    offsets = [t*0.25 for t in range(-5,5)] if planet !='L' else [t*increment_days for t in range(-5,5)]
    planet_longs = []
    for t in offsets:
        sla = divisional_chart(jd+t, place, divisional_chart_factor=divisional_chart_factor, 
                    chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[planet_index][1]
        sl = sla[0]*30+sla[1]
        planet_longs.append(sl)
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    jd += planet_hour
    sla = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor, 
                chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[planet_index][1]
    planet_long = sla[0]*30+sla[1]
    return jd,planet_long

def previous_planet_entry_date_mixed_chart(jd,place,planet,varga_factor_1=None,chart_method_1=None,
                                       varga_factor_2=None,chart_method_2=None,
                                       direction=1,precision=0.1,raasi=None):
    return next_planet_entry_date_mixed_chart(jd,place,planet,varga_factor_1=varga_factor_1,
                            chart_method_1=chart_method_1,varga_factor_2=varga_factor_2,chart_method_2=chart_method_2,
                                       direction=1,precision=0.1,raasi=None)
def next_planet_entry_date_mixed_chart(jd,place,planet,varga_factor_1=None,chart_method_1=None,
                                       varga_factor_2=None,chart_method_2=None,
                                       direction=1,precision=0.1,raasi=None):
    """
        get the date when the ascendant enters a zodiac
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param direction: 1= next entry, -1 previous entry
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param precision: precision in degrees within which longitude entry whould be (default: 0.1 degrees)
        @param raasi: raasi at which planet should enter. 
            If raasi==None: gives entry to next constellation
            If raasi is specified [1..12] gives entry to specified constellation/raasi
        @return Julian day number of planet entry into zodiac
    """
    increment_days=1.0/24.0/60.0 if planet in ['L'] else 0.1
    planet_index = 0 if planet=='L' else planet+1
    sla = mixed_chart(jd, place, varga_factor_1=varga_factor_1, chart_method_1=chart_method_1,
                      varga_factor_2=varga_factor_2, chart_method_2=chart_method_2)[planet_index][1]
    sl = sla[0]*30+sla[1]
    if raasi==None:
        multiple = (((sl//30)+1)%12)*30
        if direction==-1: multiple = (sl//30)%12*30
    else: 
        multiple = (raasi-1)*30
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        jd += increment_days*direction
        sla = mixed_chart(jd, place, varga_factor_1=varga_factor_1, chart_method_1=chart_method_1,
                      varga_factor_2=varga_factor_2, chart_method_2=chart_method_2)[planet_index][1]
        sl = sla[0]*30+sla[1]
    offsets = [t*0.25 for t in range(-5,5)] if planet !='L' else [t*increment_days for t in range(-5,5)]
    planet_longs = []
    for t in offsets:
        sla = mixed_chart(jd, place, varga_factor_1=varga_factor_1, chart_method_1=chart_method_1,
                      varga_factor_2=varga_factor_2, chart_method_2=chart_method_2)[planet_index][1]
        sl = sla[0]*30+sla[1]
        planet_longs.append(sl)
    print(offsets,'\n',planet_longs)
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    jd += planet_hour
    sla = mixed_chart(jd, place, varga_factor_1=varga_factor_1, chart_method_1=chart_method_1,
                      varga_factor_2=varga_factor_2, chart_method_2=chart_method_2)[planet_index][1]
    planet_long = sla[0]*30+sla[1]
    return jd,planet_long
def next_conjunction_of_planet_pair_divisional_chart(jd,place:drik.Place,p1,p2,divisional_chart_factor=1,chart_method=1,
                            base_rasi=None,count_from_end_of_sign=None,direction=1,separation_angle=0,
                            increment_speed_factor=0.25):
    """
        get the date when conjunction of given two planets occur
        @param p1: planet1 index (0=Sun..8=Kethu)
        @param p2: planet2 index (0=Sun..8=Kethu)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param panchanga_start_date: Date struct (y,m,d)
        @param direction: 1= next conjunction -1 previous conjunction
        @param separation_angle - angle by which the planets to each other
        @return: Julian day of conjunction   
    """
    import warnings
    _planet_speeds = [361]+[abs(psi[3]) for p,psi in drik.planets_speed_info(jd, place).items()]
    p1_speed = _planet_speeds[0] if p1=='L' else _planet_speeds[p1+1]
    p2_speed = _planet_speeds[0] if p2=='L' else _planet_speeds[p2+1]
    increment_days = increment_speed_factor/p1_speed if p1_speed > p2_speed else increment_speed_factor/p2_speed
    _DEBUG_ = False
    if (p1==7 and p2==8) or (p1==8 and p2==7):
        warnings.warn("Rahu and Ketu do not conjoin ever. Program returns error")
        return None
    pi1 = 0 if p1=='L' else p1+1; pi2 = 0 if p2=='L' else p2+1
    long_diff_check = 0.5# if p1 in ['L'] or p2 in ['L'] else 1.0
    max_days_to_search = 1000000
    cur_jd = jd# utils.julian_day_number(panchanga_start_date, (0,0,0))
    search_counter = 1
    while search_counter < max_days_to_search:
        cur_jd += increment_days
        sla = divisional_chart(cur_jd, place, divisional_chart_factor=divisional_chart_factor, 
                    chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi1][1]
        p1_long = sla[0]*30+sla[1]
        sla = divisional_chart(cur_jd, place, divisional_chart_factor=divisional_chart_factor, 
                    chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi2][1]
        p2_long = sla[0]*30+sla[1]
        long_diff = (360+p1_long - p2_long - separation_angle)%360
        if _DEBUG_: print(search_counter,p1,p1_long,p2,p2_long,long_diff,long_diff_check,utils.jd_to_gregorian(cur_jd))
        if long_diff<long_diff_check:
            if _DEBUG_: print(long_diff,'<',long_diff_check)
            #ret = __next_conjunction_of_planet_pair(p1,p2,panchanga_place,cur_jd,direction,separation_angle)
            jd_list = [cur_jd+t*increment_days for t in range(-10,10)]
            long_diff_list = []
            for jdt in jd_list:
                sla = divisional_chart(jdt, place, divisional_chart_factor=divisional_chart_factor, 
                            chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi1][1]
                p1_long = sla[0]*30+sla[1]
                sla = divisional_chart(jdt, place, divisional_chart_factor=divisional_chart_factor, 
                            chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi2][1]
                p2_long = sla[0]*30+sla[1]
                long_diff = (360+p1_long-p2_long-separation_angle)%360
                long_diff_list.append(long_diff)
            """ TODO: For separation Angle > 180 Lagrange may not work """
            try:
                if _DEBUG_: print('Lagrange method of fine tuning')
                if _DEBUG_: print(jd_list,'\n',long_diff_list)
                conj_jd = utils.inverse_lagrange(jd_list, long_diff_list, 0.0)
                sla = divisional_chart(conj_jd, place, divisional_chart_factor=divisional_chart_factor, 
                            chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi1][1]
                p1_long = sla[0]*30+sla[1]
                sla = divisional_chart(conj_jd, place, divisional_chart_factor=divisional_chart_factor, 
                            chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi2][1]
                p2_long = sla[0]*30+sla[1]
                if conj_jd is not None:
                    if _DEBUG_: print(p1,p2,utils.jd_to_gregorian(conj_jd),p1_long,p2_long)
                    return conj_jd, p1_long, p2_long
            except:
                if _DEBUG_: print('Normal method of fine tuning - since Lagrange failed')
                if _DEBUG_: print(search_counter,p1,p1_long,p2,p2_long,long_diff,long_diff_check,utils.jd_to_gregorian(cur_jd))
                conj_jd = drik.__next_conjunction_of_planet_pair(cur_jd,place,p1,p2,direction,separation_angle)
                if conj_jd is not None:
                    sla = divisional_chart(conj_jd, place, divisional_chart_factor=divisional_chart_factor, 
                                chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi1][1]
                    p1_long = sla[0]*30+sla[1]
                    sla = divisional_chart(conj_jd, place, divisional_chart_factor=divisional_chart_factor, 
                                chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)[pi2][1]
                    p2_long = sla[0]*30+sla[1]
                    return conj_jd, p1_long, p2_long
        search_counter += 1
    print('Could not find planetary conjunctions for sep angle',separation_angle,' Try increasing search range')
    return None
def lattha_stars_planets(planet_positions,include_abhijith=True):
    """
        returns latta star of the planet based on its positions
        Star numbers are returned as 1..28 (21st star is Abhijit and 28 is Revathi)
        @return: [sun_latta_star, moon_latta_star,...,ketu_latta_star]
    """
    star_count = 28 if include_abhijith else 27
    _latta_stars = []
    for p,(h,long) in planet_positions[1:const._pp_count_upto_ketu]:
        p_long = h*30+long
        p_star = drik.nakshatra_pada(p_long)[0]
        #print(p,p_star,h*30,long,p_long)
        _latta_star = utils.cyclic_count_of_stars_with_abhijit(p_star,const.latta_stars_of_planets[p][0],const.latta_stars_of_planets[p][1],star_count)
        #_latta_star = (p_star + const.latta_stars_of_planets[p][1]*const.latta_stars_of_planets[p][0]-1)%star_count
        #print(p,p_long,p_star,const.latta_stars_of_planets[p],_latta_star)
        _latta_stars.append((p_star,_latta_star))
    return _latta_stars
def _amsa_d150(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,include_upagrahas=False,
          include_special_lagnas=False,include_sphutas=False,chart_method=1,base_rasi=None,count_from_end_of_sign=None):
    #msgs = get_amsa_resources()
    planet_positions = divisional_chart(jd, place, ayanamsa_mode=ayanamsa_mode, divisional_chart_factor=divisional_chart_factor,
                            chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)
    print(planet_positions)
    f1 = 30.0/divisional_chart_factor
    _ap = []
    for p,(h,long) in planet_positions:
        pstr = utils.resource_strings['ascendant_str'] if p=='L' else utils.PLANET_NAMES[p]
        _hora = int(long//f1)+1
        if h in const.movable_signs:
            _amsa = _hora
        elif h in const.fixed_signs:
            _amsa = (151-_hora)
        else:
            _amsa = (75+_hora)%151
        #print(pstr,msgs[str(150)][_amsa])
        _ap.append(_amsa)
    return _ap
def get_64th_navamsa(navamsa_planet_positions):
    d64 = {}
    for p,(h,long) in navamsa_planet_positions:
        _64th_navamsa = (h+3)%12
        _64th_navamsa_lord = const._house_owners_list[_64th_navamsa]
        d64[p] = (_64th_navamsa,_64th_navamsa_lord)
    return d64
def get_22nd_drekkana(drekkana_planet_positions):
    d22 = {}
    for p,(h,long) in drekkana_planet_positions:
        _22nd_drekkana = (h+7)%12
        _22nd_drekkana_lord = const._house_owners_list[_22nd_drekkana]
        d22[p] = (_22nd_drekkana,_22nd_drekkana_lord)
    return d22
if __name__ == "__main__":
    from math import ceil
    import time
    lang = 'en'
    utils.set_language(lang)
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    dcf = 1; chart_method = 1; base_rasi=None; count_from_end_of_sign=None
    chart_1d = ['','1/6','','0','5/2/3','8','','4','','','L','7']
    print(_stronger_planet_from_the_chart(chart_1d, const.SUN_TO_SATURN))
    exit()
    """
    exp_results = []
    total_cpu = 0
    for planet in ['L']+[*range(9)]:
        start_time = time.time()
        nae = next_planet_entry_date_divisional_chart(jd, place, planet, divisional_chart_factor=dcf)
        cy,cm,cd,fhn = utils.jd_to_gregorian(nae[0])
        act_results = [(cy,cm,cd),utils.to_dms(fhn),utils.to_dms(nae[1],is_lat_long='plong')]
        print(planet,act_results)
        exp_results.append(act_results)
        end_time = time.time()
        cpu_time = end_time - start_time; total_cpu += cpu_time
        print(planet,'cpu time',cpu_time,'seconds','total cpu',total_cpu)
    print(exp_results)
    exit()
    """
    """
    total_cpu = 0
    p1 = 0; p2 = 1; speed_fac = 0.25
    exp_results = [['' for _ in range(10)] for _ in range(10)]
    for r,p1 in enumerate(['L']+[*range(9)]):
        for c,p2 in enumerate(['L']+[*range(9)]):
            start_time = time.time()
            if p1==p2 or (p1==7 and p2==8) or (p1==8 and p2==7): continue
            nae = drik.next_conjunction_of_planet_pair(jd, place, p1, p2, increment_speed_factor=speed_fac)
            cy,cm,cd,fhn = utils.jd_to_gregorian(nae[0])
            print(p1,p2,utils.jd_to_gregorian(nae[0]),ceil(nae[1]/30),utils.to_dms(nae[1],is_lat_long='plong'),utils.to_dms(fhn)
                  ,utils.to_dms(nae[2],is_lat_long='plong'))
            exp_results[r][c] = [(cy,cm,cd),utils.to_dms(fhn),utils.to_dms(nae[1],is_lat_long='plong')]
            end_time = time.time()
            cpu_time = end_time - start_time; total_cpu += cpu_time
            print('cpu time',cpu_time,'seconds','total cpu',total_cpu)
    print(exp_results)
    exit()
    """
    include_abhijith = True
    planet_positions = divisional_chart(jd, place, divisional_chart_factor=dcf, chart_method=chart_method,
                                        base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)
    print(dcf,planet_positions)
    lp = lattha_stars_planets(planet_positions,include_abhijith=include_abhijith)
    print(lp)
    _star_list = [utils.NAKSHATRA_LIST[s] for s in const.abhijit_order_of_stars] if include_abhijith else utils.NAKSHATRA_LIST
    for p,(p_star,l_star) in enumerate(lp):
        print(utils.PLANET_NAMES[p],p_star,utils.NAKSHATRA_LIST[p_star-1],l_star,_star_list[l_star-1])
    exit()
    p1_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    p2_long = planet_positions[p2+1][1][0]*30+planet_positions[p2+1][1][1]
    print(p1,p1_speed,p1_long,p2,p2_speed,p2_long)
    dt = (360+p2_long-p1_long)/(p1_speed-p2_speed) if p1_speed > p2_speed else (360+p1_long-p2_long)/(p2_speed-p1_speed)
    print(dt,utils.jd_to_gregorian(jd+dt*speed_fac))
    planet_positions = divisional_chart(jd+dt, place, divisional_chart_factor=dcf, chart_method=chart_method,
                                        base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)
    p1_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    p2_long = planet_positions[p2+1][1][0]*30+planet_positions[p2+1][1][1]
    print('estimate',p1,p1_speed,p1_long,p2,p2_speed,p2_long)
    nae = drik.next_conjunction_of_planet_pair(jd, place, p1, p2)
    print(p1,p2,utils.jd_to_gregorian(nae[0]),utils.to_dms(nae[1],is_lat_long='plong'),utils.to_dms(nae[2],is_lat_long='plong'))
    exit()
    #"""
    #"""
    varga_factor_1=9; chart_method_1=1;varga_factor_2 = 12; chart_method_2=1
    from math import ceil
    planet = 'L'
    import time
    total_cpu = 0
    for planet in ['L']+[*range(9)]:
        start_time = time.time()
        nae = next_planet_entry_date_divisional_chart(jd, place, planet, dcf, 1, chart_method, base_rasi, count_from_end_of_sign)
        _,_,_,fhn = utils.jd_to_gregorian(nae[0])
        print(utils.jd_to_gregorian(nae[0]),ceil(nae[1]/30),utils.to_dms(nae[1],is_lat_long='plong'),utils.to_dms(fhn))
        end_time = time.time()
        total_cpu += end_time-start_time
        print(planet,'cpu time',end_time-start_time,'seconds',total_cpu)
        nae = previous_planet_entry_date_divisional_chart(jd, place, planet, dcf, chart_method, base_rasi, count_from_end_of_sign)
        _,_,_,fhn = utils.jd_to_gregorian(nae[0])
        print(utils.jd_to_gregorian(nae[0]),ceil(nae[1]/30),utils.to_dms(nae[1],is_lat_long='plong'),utils.to_dms(fhn))
        total_cpu += time.time()-end_time
        print(planet,'cpu time',time.time()-end_time,'seconds',total_cpu)
    exit()
    #"""