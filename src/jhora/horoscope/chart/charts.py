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
    Release History:
    V4.8.6 - utils.count_rasis dir argument changed to direction
    V4.8.7 - planet retrogression method removed.
    V4.8.9 - 
        chara_karakas with 4 methods as specified in jaganath hora. This will replace hourse.chara_karakas
        divisional_chart has exclude_non_planets=True argument to include all non-planet chart elements
        separate functions added to get non-planet longitudes e.g. saham_longitudes, arudha_lagna_longitudes
        NOTE: NadiAmsa (D150 Default in JHora V8.0 is non-uniform method. But chart and amsa rulers are opposite -
        in the sense chart is non-uniform, but amsa ruler is for uniform or vice-versa.
"""
import math
from collections import defaultdict
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
                              150:'nadiamsa_chart'
                              }

def _get_rasi_positions(jd_at_dob,place,star_position_from_moon=1,dhasa_progression_correction=0.0):
    return chart_element_rasi_positions(jd_at_dob, place, star_position_from_moon)

def _get_non_planet_varga_position(non_planet_key,non_planet_long,divisional_chart_factor,chart_method,base_rasi,
                                   count_from_end_of_sign):
    _rasi, _longitude = drik.dasavarga_from_long(non_planet_long)
    div_positions = divisional_positions_from_rasi_positions(
                    [[non_planet_key,(_rasi, _longitude)]],
                    divisional_chart_factor=divisional_chart_factor, 
                    chart_method=chart_method, base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign,
                    )
    non_planet_result = div_positions[0]
    non_planet_rasi, non_planet_long = non_planet_result[1]
    non_planet_full_long = non_planet_rasi * 30 + non_planet_long
    return non_planet_full_long

def _get_non_planet_mixed_varga_position(non_planet_key,non_planet_long,varga_factor_1, chart_method_1,varga_factor_2,
                                         chart_method_2):
    _rasi, _longitude = drik.dasavarga_from_long(non_planet_long)
    mixed_positions = mixed_chart_from_rasi_positions([[non_planet_key,(_rasi, _longitude)]],
                                                      varga_factor_1, chart_method_1,
                                                      varga_factor_2,chart_method_2)
    non_planet_result = mixed_positions[0]
    non_planet_rasi, non_planet_long = non_planet_result[1]
    non_planet_full_long = non_planet_rasi * 30 + non_planet_long
    return non_planet_full_long

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
    f.close()
    return msgs
def rasi_chart(jd_at_dob,place_as_tuple,years=1,months=1,sixty_hours=1
               ,calculation_type='drik',pravesha_type=0,dhasa_progression_correction=0.0):
    """
        Get Rasi chart - D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
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
    " Get Ascendant information"
    ascendant_constellation, ascendant_longitude, _, _ = drik.ascendant(jd_years,place_as_tuple,
                                                                dhasa_progression_correction=dhasa_progression_correction)
    planet_positions = drik.dhasavarga(jd_years,place_as_tuple,divisional_chart_factor=1,
                                       dhasa_progression_correction=dhasa_progression_correction)
    planet_positions = [[ascendant_index,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    return planet_positions
def bhava_houses(jd,place,bhava_starts_with_ascendant=False):
    bp = bhava_chart_houses(jd, place, bhava_starts_with_ascendant=bhava_starts_with_ascendant)
    bp = {p:house.get_relative_house_of_planet(bp[const._ascendant_symbol][0],h) for p,(h,_) in bp.items()}
    return bp
def bhava_chart(jd,place,bhava_madhya_method=None):
    """
        @return: [[house1_rasi,(house1_start,house1_cusp,house1_end),[planets_in_house1]],(...),
                [house12_rasi,(house12_start,house12_cusp,house12_end,[planets_in_house12])]]
    """
    if bhava_madhya_method is None: bhava_madhya_method = const.bhaava_madhya_method
    return _bhaava_madhya_new(jd,place,bhava_madhya_method=bhava_madhya_method)
def _bhaava_madhya_new(
    jd=None,
    place=None,
    divisional_chart_factor=1,
    bhava_madhya_method=None,
    ayanamsa_mode=None,
    reference_planet_for_ascendant=None,
    ascendant_is_middle_of_house=True,
    chart_method=None, base_rasi=None, count_from_end_of_sign=None, # Other divisional chart arguments
    dhasa_progression_correction=0.0,
    **kwargs
):
    """
    returns house longitudes (start, cusp, end)

    @param jd: Julian Day number
    @param place: Place('name',latitude,longitude,timezone_hours)
    @param bhava_madhya_method:
        Indian House Systems (Use numbers as below)
         1 => KN Rao method (Parashari - Bhava Chalita - cusp-15,cusp,cusp+15)
         2 => Parashari - (Whole Sign - Houses 0-30, cusps as calculated from Swiss Ephimeris)
         3 => KP Method (houses start from cusp and end at cusp)
         4 => BV Raman (get 1,4,6,10 cusps, equally divided houses. Sandhi/edges 1/2 of adjacent cusps.
         5 => Equal Houses based on nakshathra padas (9 padhas each)
         Note: Use
         'O' => Sripathi/Porphyrius - To match Jagannatha Hora,
         'S' => Sripathi/Astrodienst - to match Sripati padhati - book by  V. Subramanya Sastri
        For Western House Systems (use 'alphabets' as below)
        Note: Western House Systems are included only if const.include_western_house_systems=True
         'A':'Equal (cusp 1 is Ascendant)', 'B':'Alcabitus','C':'Campanus', 
         'E':'Equal (cusp 1 is Ascendant)', 
         'H':'azimuthal or horizontal system','K':'Koch','M':'Morinus',
         'O' : Sripathi/Porphyrius - To match Jagannatha Hora,
         'P':'Placidus','R':'Regiomontanus', 
         'S' : Sripathi/Astrodienst - to match Sripati padhati - book by  V. Subramanya Sastri,
         'V':'Vehlow equal (Asc. in middle of house 1)', 
         'X':'axial rotation system',
         'W':'Whole Sign - (0,15,30),(30,45,60) - Same as Rasi Chart',
         'T':'Polich/Page (topocentric system)'

    @param reference_planet_for_ascendant: None (Default=Ascendant) or use const.SUN_ID to const.KETU_ID
    @param ascendant_is_middle_of_house: (True=Default); False=Start of house
    @return: [[house1_rasi,(house1_start,house1_cusp,house1_end)],(...),[house12_rasi,(house12_start,house12_cusp,house12_end)]]
    """
    if bhava_madhya_method is None: bhava_madhya_method = const.bhaava_madhya_method
    # --- Get the divisional chart planetary positions (unchanged) ---
    varga_factor_1 = kwargs.get("varga_factor_1"); chart_method_1 = kwargs.get("chart_method_1",1)
    varga_factor_2 = kwargs.get("varga_factor_2"); chart_method_2 = kwargs.get("chart_method_2",1)
    if varga_factor_1 is not None and varga_factor_2 is not None:
        planet_positions = mixed_chart(jd, place, varga_factor_1=varga_factor_1, chart_method_1=chart_method_1,
                                       varga_factor_2=varga_factor_2,chart_method_2=chart_method_2)#,**kwargs)
    else:
        planet_positions = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                        chart_method=chart_method, base_rasi=base_rasi,
                                        count_from_end_of_sign=count_from_end_of_sign,
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True,
                                        **kwargs)
    if bhava_madhya_method is None: bhava_madhya_method = const.bhaava_madhya_method
    def mid_point(a, b):
        # midpoint along the forward arc a -> b (mod 360)
        return (a + ((b - a) % 360.0) / 2.0) % 360.0
    def add_deg(a, d):
        return (a + d) % 360.0
    def mids_to_boundaries(mids):
        """
        Given 12 madhyas m[h], derive 12 sandhi/cusps as boundaries:
          boundary[h] = mid_point(mids[h], mids[(h+1)%12])
        Then House h: start = boundary[h-1], end = boundary[h]
        """
        return [mid_point(mids[h], mids[(h+1) % 12]) for h in range(12)]
    # --- Ayanamsa override handling ---
    if ayanamsa_mode is not None:
        previous_default_ayanamsa = const._DEFAULT_AYANAMSA_MODE
        drik.set_ayanamsa_mode(ayanamsa_mode)
    # --- Validate chosen method ---
    if not utils.is_valid_option(bhava_madhya_method,const.available_house_systems()):
        warn_msg = "bhava_madhya_method should be one of const.available_house_systems keys\n Value 1 assumed"
        print(warn_msg)
        bhava_madhya_method = const.BHAVA_METHODS.KN_RAO_JHORA_DEFAULT
    # --- Ascendant (or reference planet) ---
    if reference_planet_for_ascendant in const.SUN_TO_KETU:
        asc_rasi = planet_positions[reference_planet_for_ascendant + 1][1][0]
        asc_long = planet_positions[reference_planet_for_ascendant + 1][1][1]
        asc_full = (asc_rasi * 30.0 + asc_long) % 360.0
    else:
        asc_rasi, asc_long = planet_positions[0][1][0], planet_positions[0][1][1]
        asc_full = (asc_rasi * 30.0 + asc_long) % 360.0
    bhava_houses = []
    # 1 => KN Rao method (Parashari - Bhava Chalita - cusp-15,cusp,cusp+15)
    if bhava_madhya_method == 1:
        for h in range(12):
            cusp = utils.norm360(asc_full + 30.0 * h)
            if ascendant_is_middle_of_house:
                # True  => (cusp-15, cusp, cusp+15)
                start = add_deg(cusp, -15.0)
                mid   = cusp
                end   = add_deg(cusp,  15.0)
            else:
                # False => (cusp, cusp+15, cusp+30)
                start = cusp
                mid   = add_deg(cusp, 15.0)
                end   = add_deg(cusp, 30.0)
            bhava_houses.append((start, mid, end))
        results = drik._assign_planets_to_houses(
            planet_positions, bhava_houses, bhava_madhya_method=bhava_madhya_method
        )
    # 2 => Parashari - (Whole Sign - Houses 0-30, cusps as calculated from Swiss Ephimeris)
    elif bhava_madhya_method == 2:
        for h in range(12):
            _bhava_start = utils.norm360((asc_rasi + h) * 30.0)
            _bhava_end   = utils.norm360((asc_rasi + h + 1) * 30.0)
            _bhava_mid   = utils.norm360(asc_full + h * 30.0)  # asc degree carried into each sign
            # For True/False, the triple is the same; semantics differ, not the geometry.
            bhava_houses.append((_bhava_start, _bhava_mid, _bhava_end))
        results = drik._assign_planets_to_houses(
            planet_positions, bhava_houses, bhava_madhya_method=bhava_madhya_method
        )
    # 3 => KP Method (houses start from cusp and end at cusp)
    elif bhava_madhya_method == 3:
        # Treat these as the *house cusps* (Placidus), ordered 1..12.
        cusps = drik.bhaava_madhya_kp(jd, place)
        cusps = [x % 360.0 for x in cusps]
        # Sandhis (house edges) are midpoints between adjacent cusps
        # sandhi[h] = midpoint(cusp[h-1], cusp[h])
        sandhi = [mid_point(cusps[(h - 1) % 12], cusps[h]) for h in range(12)]
        bhava_houses = []
        for h in range(12):
            if ascendant_is_middle_of_house:
                # True: Start = sandhi-left, Mid = cusp, End = sandhi-right (JHora style)
                start = sandhi[h]
                mid   = cusps[h]
                end   = sandhi[(h + 1) % 12]
            else:
                # False: House starts at cusp, ends at next cusp; middle is midpoint of the arc.
                start = cusps[h]
                end   = cusps[(h + 1) % 12]
                mid   = mid_point(start, end)
            bhava_houses.append((start % 360.0, mid % 360.0, end % 360.0))
        results = drik._assign_planets_to_houses(
            planet_positions, bhava_houses, bhava_madhya_method=bhava_madhya_method
        )
    # 4 => BV Raman (get 1,4,6,10 cusps, equally divided houses. Sandhi/edges 1/2 of adjacent cusps.
    elif bhava_madhya_method == 4:
        m = drik.bhaava_madhya_swe(jd, place, house_code='S')  # assume mids
        m = [utils.norm360(x) for x in m]
        if ascendant_is_middle_of_house:
            for h in range(12):
                s = mid_point(m[(h - 1) % 12], m[h])
                e = mid_point(m[h], m[(h + 1) % 12])
                bhava_houses.append((s, m[h], e))
        else:
            # “House starts at cusp”; cusps are the sandhis between adjacent middles
            c = mids_to_boundaries(m)
            for h in range(12):
                start = c[(h - 1) % 12]
                end   = c[h]
                mid   = mid_point(start, end)
                bhava_houses.append((start, mid, end))
        results = drik._assign_planets_to_houses(
            planet_positions, bhava_houses, bhava_madhya_method=4  # keep 'S' for Raman/Sripati
        )
    # 5 => Equal Houses based on nakshathra padas (9 padhas each)
    elif bhava_madhya_method == 5:
        one_padha = (3 + 20 / 60.0)  # 3°20' = 3.333...°
        # Centers aligned to pada centers; keep existing approach & add False branch
        centers = [((math.floor(((asc_full % 360.0) / one_padha)) * one_padha) + one_padha / 2.0 + i * 30.0) % 360.0
                   for i in range(12)]
        if ascendant_is_middle_of_house:
            for c in centers:
                bhava_houses.append((add_deg(c, -15.0), c, add_deg(c, 15.0)))
        else:
            for c in centers:
                start = c
                mid   = add_deg(c, 15.0)
                end   = add_deg(c, 30.0)
                bhava_houses.append((start, mid, end))
        results = drik._assign_planets_to_houses(
            planet_positions, bhava_houses, bhava_madhya_method=bhava_madhya_method
        )
    else:
        # --------------------------
        # WESTERN SYSTEMS (alphabet codes)
        # --------------------------
        house_code = bhava_madhya_method
    
        # --- Special-case Vehlow equal ('V'): Asc in the MIDDLE of House 1 ---
        if house_code == 'V':
            bhava_houses = []
            if ascendant_is_middle_of_house:
                # House 1 centered on Asc
                start1 = add_deg(asc_full, -15.0)
                mid1   = asc_full
                end1   = add_deg(asc_full,  15.0)
            else:
                # "house starts with cusp"; for Vehlow, cusp(1) = Asc - 15°
                start1 = add_deg(asc_full, -15.0)
                mid1   = add_deg(start1, 15.0)  # geometric mid of the 30° span
                end1   = add_deg(start1, 30.0)
    
            # Build all 12 houses by marching 30° ahead
            for h in range(12):
                start = add_deg(start1, 30.0 * h)
                mid   = add_deg(mid1,   30.0 * h)
                end   = add_deg(end1,   30.0 * h)
                bhava_houses.append((start, mid, end))
    
            results = drik._assign_planets_to_houses(
                planet_positions, bhava_houses, bhava_madhya_method=house_code
            )
            # Important: return here so the generic flow below doesn't run for 'V'
            return results
    
        # --- All other Western codes proceed as usual ---
        m = drik.bhaava_madhya_swe(jd, place, house_code=house_code)  # often returns mids
        m = [utils.norm360(x) for x in m]
    
        # Equal-span systems where cusp 1 is Ascendant ('A' and 'E')
        if house_code in ('A', 'E'):
            bhava_houses = []
            if ascendant_is_middle_of_house:
                for h in range(12):
                    s = add_deg(m[h], -15.0)
                    e = add_deg(m[h],  15.0)
                    bhava_houses.append((s, m[h], e))
            else:
                for h in range(12):
                    start = m[h]
                    mid   = add_deg(m[h], 15.0)
                    end   = add_deg(m[h], 30.0)
                    bhava_houses.append((start, mid, end))
    
            results = drik._assign_planets_to_houses(
                planet_positions, bhava_houses, bhava_madhya_method=house_code
            )
            return results
    
        # Variable-span systems (P,K,O,R,C,X,H,T,B,M, etc.)
        # Convert mids to boundaries (cusps) and then build (start, mid, end)
        c = [mid_point(m[h], m[(h+1) % 12]) for h in range(12)]
    
        bhava_houses = []
        if ascendant_is_middle_of_house:
            for h in range(12):
                start = c[(h - 1) % 12]
                end   = c[h]
                mid   = m[h]
                bhava_houses.append((start, mid, end))
        else:
            for h in range(12):
                start = c[(h - 1) % 12]
                end   = c[h]
                mid   = mid_point(start, end)
                bhava_houses.append((start, mid, end))
    
        results = drik._assign_planets_to_houses(
            planet_positions, bhava_houses, bhava_madhya_method=house_code
        )
    # --- Restore ayanamsa if overridden ---
    if ayanamsa_mode is not None:
        drik.set_ayanamsa_mode(previous_default_ayanamsa)
    return results

def bhava_chart_houses(jd_at_dob,place_as_tuple,years=1,months=1,sixty_hours=1
                ,calculation_type='drik',bhava_starts_with_ascendant=False):
    """
        Get Bhava chart from Rasi / D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    planet_positions = rasi_chart(jd_at_dob, place_as_tuple, years, months, sixty_hours,
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
def __parivritti_even_reverse(planet_positions_in_rasi, dvf, dirn=1):
    f1 = 30.0 / dvf
    _hora_list = utils.parivritti_even_reverse(dvf, dirn)
    hora_sign = lambda r, h: [s1 for r1, h1, s1 in _hora_list if r1 == r and h1 == h][0]
    dp = []
    
    for planet, [rasi_sign, long] in planet_positions_in_rasi:
        # 1. Calculate standard forward-projected longitude
        d_long = (long * dvf) % 30.0
        
        # 2. APPLY REVERSAL FOR EVEN SIGNS
        # Since the amsas are mapped in reverse order, the longitude 
        # within the amsa is reckoned backward from the end of the sign.
        if rasi_sign in const.even_signs:
            d_long = 30.0 - d_long
            # Edge case safety: prevent exactly 30.0 from bypassing 0.0
            if d_long >= 30.0:
                d_long -= 30.0
                
        hora = int(long // f1)
        dp.append([planet, [hora_sign(rasi_sign, hora), d_long]])
        
    return dp
def _hora_chart_raman_method(planet_positions_in_rasi):
    """ Hora Chart - D2 Chart Raman Method
        Ref: https://jyotish-blog.blogspot.com/2005/08/
    """
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
    planet_hora = const.planet_hora_dict_for_odd_even_signs
    planet_count = const._pp_count_upto_pluto if const._INCLUDE_URANUS_TO_PLUTO else const._pp_count_upto_ketu
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi[:planet_count]:
        d_long = (long*dvf)%30
        hora = int(long // 15.0)
        lord_of_rasi = house.house_owner_from_planet_positions(planet_positions_in_rasi, rasi_sign)
        if rasi_sign in const.odd_signs:
            hora_sign = planet_hora[lord_of_rasi][0] if hora==0 else planet_hora[lord_of_rasi][1] 
        else:
            hora_sign = planet_hora[lord_of_rasi][1] if hora==0 else planet_hora[lord_of_rasi][0] 
        dp.append([planet,[hora_sign,d_long]])
    return dp
    
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
def hora_chart_all_chart_elements(
        jd,
        place,
        chart_method=1,
        star_position_from_moon=1,
        exclude_non_planets=False,
    ):
    """
    Hora/D2 chart for planets and optionally non-planet chart elements.

    This follows the required flow:
        1. Calculate D1/Rasi longitude of each element.
        2. Apply D2/Hora transformation using chart_method.

    @param exclude_non_planets:
        True  => only Lagna + planets
        False => Lagna + planets + non-planets
    """

    pp_rasi = chart_element_rasi_positions(
        jd,
        place,
        star_position_from_moon=star_position_from_moon,
        exclude_non_planets=exclude_non_planets,
    )

    return hora_chart(pp_rasi, chart_method=chart_method)
    
def hora_chart(planet_positions_in_rasi,chart_method=None):
    """ 
        Hora Chart - D2 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=> Parasara hora with parivritti & even side reversal (Uma Shambu) here it is PVR method
            2=> Traditional Parasara (Only Le & Cn)
            3=> Raman Method (1st/11th, day/night)
            4=> Parivritti Dwaya (Bicyclical Hora)
            5=> Kashinatha Hora (ownership day/night)
            6=> Somanatha method (parivritti alternate)
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    try:
        chart_method = const.D2_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d2_chart_method_default
    if chart_method==const.D2_CHART_METHOD.PARASARA_UMA_SHAMBU_VARIATION:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf=2)
    elif chart_method==const.D2_CHART_METHOD.TRADITIONA_PARASARA_WITH_Le_Cn_ONLY:
        return _hora_traditional_parasara_chart(planet_positions_in_rasi)
    elif chart_method==const.D2_CHART_METHOD.RAMAN_1st_11th_DAY_NIGHT:
        return _hora_chart_raman_method(planet_positions_in_rasi)
    elif chart_method==const.D2_CHART_METHOD.PARIVRITTI_DWAYA_BICYCLICAL_HORA:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf=2)
    elif chart_method==const.D2_CHART_METHOD.KASHINATHA_HORA_OWNERSHIP_DAY_NIGHT:
        return _hora_chart_kashinath(planet_positions_in_rasi)
    elif chart_method==const.D2_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf=2)
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
def drekkana_chart(planet_positions_in_rasi,chart_method=None):
    """ 
        Drekkana Chart - D3 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Parasara with parivritti and even sign reversal (Uma Shambu)
            2=>Parivritti Traya
            3=>Somanatha method (parivritti alternate)
            4=>Jaganatha
            5=>Parasara Parivritti and Even sign reverse
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    try:
        chart_method = const.D3_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d3_chart_method_default
    dvf = 3
    if chart_method==const.D3_CHART_METHOD.PARASARA_UMA_SHAMBU:
        return _drekkana_chart_parasara(planet_positions_in_rasi)
    elif chart_method==const.D3_CHART_METHOD.PARIVRITTI_TRAYA:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D3_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    elif chart_method==const.D3_CHART_METHOD.JAGANAATHA:
        return _drekkana_chart_jagannatha(planet_positions_in_rasi)
    elif chart_method==const.D3_CHART_METHOD.PARASARA_PARIVRITTI_EVEN_REVERSE:
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
def chaturthamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D4_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d4_chart_method_default
    if chart_method==const.D4_CHART_METHOD.PARASARA_TRADITIONAL:
        return _chaturthamsa_parasara(planet_positions_in_rasi)
    elif chart_method==const.D4_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf=4)
    elif chart_method==const.D4_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf=4)
    elif chart_method==const.D4_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf=4)
def panchamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D5_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d5_chart_method_default
    dvf = 5; f1 = 30.0/dvf
    if chart_method==2:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==3:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==4:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    odd = const.panchamsa_odd_signs
    even = const.panchamsa_even_signs
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = even[l]%12
        if sign in const.odd_signs:
            r = odd[l]
        dp.append([planet,[r,d_long]]) # lth position from rasi
    return dp
def shashthamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D6_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d6_chart_method_default
    dvf = 6; f1 = 30.0/dvf
    if chart_method==const.D6_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D6_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D6_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
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
def saptamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D7_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d7_chart_method_default
    dvf = 7; f1 = 30.0/dvf
    if chart_method==const.D7_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D7_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D7_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    dirn = -1 if chart_method in [
                                    const.D7_CHART_METHOD.PARASARA_EVEN_START_7TH_GO_BACKWARD,
                                    const.D7_CHART_METHOD.PARASARA_EVEN_REVERSE_END_7TH] else 1
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+dirn*(l+const.HOUSE_7))%12
            if chart_method==const.D7_CHART_METHOD.PARASARA_EVEN_REVERSE_END_7TH:
                r = (r-const.HOUSE_7)%12
        dp.append([planet,[r,d_long]])
    return dp
def ashtamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D8_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d8_chart_method_default
    dvf = 8; f1 = 30.0/dvf
    if chart_method==const.D8_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D8_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D8_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
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
def navamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D9_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d9_chart_method_default
    dvf = 9; f1 = 30.0/dvf
    if chart_method==const.D9_CHART_METHOD.PARIVRITTI_CYCLIC: # This also same as traditional UKM
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D9_CHART_METHOD.PARASARA_EVEN_REVERSAL_UNIFORM_KRISHNA_MISRA: # Uniform Krishna Navamsa Method
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D9_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    elif chart_method==const.D9_CHART_METHOD.KALACHAKRA_NAVAMSA: # Kalachakra Navamsa
        return _navamsa_kalachakra(planet_positions_in_rasi)
    # Traditional Parasara Method
    navamsa_dict = {0:(1,const.fire_signs),3:(1,const.water_signs),6:(1,const.air_signs),9:(1,const.earth_signs)}
    if chart_method==const.D9_CHART_METHOD.RANGACHARYA_KRISHNA_MISRA_SANJAY_RATH_NADI_NAVAMSA:
        navamsa_dict = {0:(1,const.fire_signs),3:(-1,const.water_signs),6:(1,const.air_signs),9:(-1,const.earth_signs)}
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = [(seed+dirn*l)%12 for seed,(dirn,sign_list) in navamsa_dict.items() if sign in sign_list][0]
        dp.append([planet,[r,d_long]])
    return dp
def dasamsa_chart(planet_positions_in_rasi,chart_method=None):
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
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries. 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    try:
        chart_method = const.D10_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d10_chart_method_default
    dvf = 10; f1 = 30.0/dvf
    if chart_method==const.D10_CHART_METHOD.PARIVRITTI_CYCLIC_OJHA:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D10_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D10_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    dirn = -1 if chart_method in [const.D10_CHART_METHOD.PARASARA_EVEN_START_9TH_BACKWARD,
                                  const.D10_CHART_METHOD.PARASARA_EVEN_START_REVERSE_9TH_BACKWARD] else 1
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+dirn*(l+const.HOUSE_9))%12
            if chart_method==const.D10_CHART_METHOD.PARASARA_EVEN_START_9TH_BACKWARD:
                r = (r-const.HOUSE_9)%12
        dp.append([planet,[r,d_long]])
    return dp
def rudramsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D11_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d11_chart_method_default
    dvf = 11; f1 = 30.0/dvf
    if chart_method==const.D11_CHART_METHOD.PARIVRITTI_CYCLIC_OJHA:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D11_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D11_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (12-sign+l)%12
        if chart_method==const.D11_CHART_METHOD.BVRAMAN_EKADASAMSA_ANTI_ZODIACAL: r = (11-r)%12
        dp.append([planet,[r,d_long]])
    return dp
def dwadasamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D12_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d12_chart_method_default
    dvf = 12; f1 = 30.0/dvf
    if chart_method==const.D12_CHART_METHOD.PARIVRITTI_CYCLIC_OJHA:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D12_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D12_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        dirn = -1 if ( sign in const.even_signs and 
                       chart_method==const.D12_CHART_METHOD.TRADITIONAL_PARASARA_EVEN_REVERSAL ) else 1
        l = (int(long//f1))
        dp.append([planet,[(sign+dirn*l)%12,(long*dvf)%30]])
    return dp
def kalamsa_chart(planet_positions_in_rasi,chart_method=1):
    return shodasamsa_chart(planet_positions_in_rasi, chart_method)
def shodasamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D16_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d16_chart_method_default
    dvf = 16; f1 = 30.0/dvf
    if chart_method==const.D16_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D16_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D16_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+const.HOUSE_5)%12
        elif sign in const.dual_signs:
            r = (l+const.HOUSE_9)%12
        dp.append([planet,[r,d_long]])
    return dp
def vimsamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D20_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d20_chart_method_default
    dvf = 20; f1 = 30.0/dvf
    if chart_method==const.D20_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D20_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D20_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+const.HOUSE_5)%12
        elif sign in const.fixed_signs:
            r = (l+const.HOUSE_9)%12
        dp.append([planet,[r,d_long]])
    return dp
def siddhamsa_chart(planet_positions_in_rasi,chart_method=None):
    return chaturvimsamsa_chart(planet_positions_in_rasi,chart_method=chart_method)
def chaturvimsamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D24_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d24_chart_method_default
    dvf = 24; f1 = 30.0/dvf; dp = []
    even_dirn = -1 if chart_method==const.D24_CHART_METHOD.PARASARA_EVEN_REVERSE else 1
    odd_base = 4
    even_base = 4 if chart_method == const.D24_CHART_METHOD.PARASARA_EVEN_DOUBLE_REVERSE else 3
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (odd_base+l)%12 #4 = Leo
        if sign in const.even_signs:
            r = (even_base+even_dirn*l)%12 # 3 = Cancer
        dp.append([planet,[r,d_long]])
    return dp
def nakshatramsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D27_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d27_chart_method_default
    dvf = 27; f1 = 30.0/dvf
    if chart_method==const.D27_CHART_METHOD.PARASARA_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D27_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # fiery sign
        if sign in const.earth_signs:
            r = (l+const.HOUSE_4)%12 # part from Cancer
        elif sign in const.air_signs:
            r = (l+const.HOUSE_7)%12
        elif sign in const.water_signs:
            r = (l+const.HOUSE_10)%12
        dp.append([planet,[r,d_long]])
    return dp
def trimsamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D30_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d30_chart_method_default
    dvf = 30; f1 = 30.0/dvf
    if chart_method==const.D30_CHART_METHOD.PARIVRITTI_CYCLIC_TRIMSAMSA:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D30_CHART_METHOD.PARASARA_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D30_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    elif chart_method==const.D30_CHART_METHOD.SASHTYAMSA_LIKE_TRIMSAMSA:
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
def khavedamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D40_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d40_chart_method_default
    dvf = 40; f1 = 30.0/dvf
    if chart_method==const.D40_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D40_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D40_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 #part from Aries
        if sign in const.even_signs:
            r = (l+const.HOUSE_7)%12 # Part from Libra
        dp.append([planet,[r,d_long]])
    return dp
def akshavedamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D45_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d45_chart_method_default
    dvf = 45; f1 = 30.0/dvf
    if chart_method==const.D45_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D45_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D45_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+const.HOUSE_5)%12
        elif sign in const.dual_signs:
            r = (l+const.HOUSE_9)%12
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
    try:
        chart_method = const.D60_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d60_chart_method_default
    dvf = 60; f1 = 30.0/dvf
    if chart_method==const.D60_CHART_METHOD.PARASARA_EVEN_REVERSE_FROM_ARIES: #Parasara (from Aries even reverse)
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dirn = -1 if (sign in const.even_signs and 
                      chart_method == const.D60_CHART_METHOD.PARASARA_EVEN_REVERSE_FROM_SIGN) else 1
        seed = 0 if chart_method == const.D60_CHART_METHOD.PARASARA_CYCLIC_FROM_ARIES else sign
        dp.append([planet,[(seed+dirn*l)%12,d_long]])
    return dp
def nava_navamsa_chart(planet_positions_in_rasi,chart_method=None):
    """ 
        Nava Navamsa Chart - D81 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @param chart_method:
            1=>Traditional Parasara (Parivritti Cyclic)
            2=>Parivritti Even Reverse
            3=>Parivritti Alternate (aka Somanatha)
            4=>Kalachakra nava navamsa
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    try:
        chart_method = const.D81_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d81_chart_method_default
    dvf = 81; f1 = 30.0/dvf
    if chart_method==const.D81_CHART_METHOD.PARASARA_TRADITIONAL_PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D81_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D81_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    pp1 = _navamsa_kalachakra(planet_positions_in_rasi,dvf=9)
    pp2 = _navamsa_kalachakra(pp1,dvf=9)
    return pp2
def ashtotharamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D108_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d108_chart_method_default
    dvf = 108; f1 = 30.0/dvf
    if chart_method==const.D108_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D108_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D108_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dvf_1 = 9; chart_method_1=1; dvf_2=12; chart_method_2=1
    pp = mixed_chart_from_rasi_positions(planet_positions_in_rasi, varga_factor_1=dvf_1, chart_method_1=chart_method_1, 
                      varga_factor_2=dvf_2, chart_method_2=chart_method_2)
    return pp
def dwadas_dwadasamsa_chart(planet_positions_in_rasi,chart_method=None):
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
    try:
        chart_method = const.D144_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d144_chart_method_default
    dvf = 144; f1 = 30.0/dvf
    if chart_method==const.D144_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf)
    elif chart_method==const.D144_CHART_METHOD.PARIVRITTI_EVEN_REVERSE:
        return __parivritti_even_reverse(planet_positions_in_rasi, dvf)
    elif chart_method==const.D144_CHART_METHOD.SOMANATHA_PARIVRITTI_ALTERNATE:
        return __parivritti_alternate(planet_positions_in_rasi, dvf)
    # Traditional Parasara Method
    dvf_1 = 12; chart_method_1=1; dvf_2=12; chart_method_2=1
    pp = mixed_chart_from_rasi_positions(planet_positions_in_rasi,varga_factor_1=dvf_1,chart_method_1=chart_method_1,
                      varga_factor_2=dvf_2, chart_method_2=chart_method_2)
    return pp

def _chandra_kala_nadi_boundaries():
    """
    Generate 150 non-uniform Chandra Kala Nadi intervals
    from Parashara's shodasa varga boundaries.

    The principle:
        - Mark the internal boundaries of the Parashara vargas inside one sign.
        - These distinct boundaries divide 30 degrees into 150 non-uniform parts.

    D1/Rasi contributes no internal boundary, so the useful divisions are:
        D2, D3, D4, D7, D9, D10, D12, D16, D20, D24,
        D27, D30, D40, D45, D60

    Returns:
        List of 151 boundary points:
            0 degree + 149 internal boundaries + 30 degrees
    """
    from fractions import Fraction

    varga_divisions = [2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]

    points = {Fraction(0, 1), Fraction(30, 1)}

    for d in varga_divisions:
        for k in range(1, d):
            points.add(Fraction(30 * k, d))

    points = sorted(points)
    # Should produce 151 points: 0 + 149 internal boundaries + 30
    assert len(points) == 151
    result = [float(p) for p in points]
    return result


# Compute once at module load, not once per planet.
_CKN_POINTS = _chandra_kala_nadi_boundaries()


def _non_uniform_d150_index_and_longitude(lon):
    """
    lon: longitude within sign, 0 <= lon < 30

    Returns:
        index: 0-based nadi index, 0..149
        d_long: proportional longitude inside that nadi, scaled to 0..30
    """
    from bisect import bisect_right

    lon = lon % 30.0

    index = bisect_right(_CKN_POINTS, lon) - 1

    if index >= 150:
        index = 149

    start = _CKN_POINTS[index]
    end = _CKN_POINTS[index + 1]

    # Scale variable-width segment to 0..30 for divisional-chart longitude.
    d_long = ((lon - start) / (end - start)) * 30.0

    return index, d_long


def _uniform_d150_index_and_longitude(lon, dvf=150):
    """
    Uniform D150 division.

    Divides each sign into 150 equal parts of 12' arc, i.e. 0.2 degrees each.

    Returns:
        index: 0-based division index, 0..149
        d_long: longitude inside resulting D150 sign, 0..30
    """
    f1 = 30.0 / dvf  # 12 minutes of arc (0.2 degrees)

    lon = lon % 30.0

    l = int(lon // f1)

    if l >= dvf:
        l = dvf - 1

    d_long = (lon * dvf) % 30.0

    return l, d_long



def nadiamsa_chart(planet_positions_in_rasi, chart_method=None):
    """
    Nadiamsa Chart - D150 Chart

    Method 1:
        PVR/JHora matching method.
        Uniform D150, own sign as base, forward counting for all signs.

    Method 2:
        Uses non-uniform Chandra Kala Nadi division.
        Each sign is divided into 150 unequal parts generated from
        Parashara's shodasa varga boundaries.

    Other non-cyclic methods:
        Divide each sign into 150 parts of 12' (0.2 degrees) each.

    @param planet_positions_in_rasi: Rasi chart planet positions
        Format: [[planet, (rasi, planet_longitude)], ...]

    @param chart_method: Base sign configuration (1 to 8)
        1 => PVR_JHORA_METHOD_OWN_SIGN_UNIFORM_DIRECT
             Uniform D150, own sign as base, forward for all signs

        2 => DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM
             Non-uniform Chandra Kala Nadi - Movable: Aries, Fixed: Taurus [Rev], Dual: Gemini

        3 => DEVA_KERALAM_CHANDRA_KALA_NADI_UNIFORM_DIRECT
             Uniform D150 - Movable: Aries, Fixed: Taurus [Fwd], Dual: Gemini

        4 => PARIVRITTI_CYCLIC
             Continuous Parivritti cyclic projection

        5 => MOVABLE_ARIES_FWD_FIXED_TAURUS_BACK_DUAL_GEMINI_FWD

        6 => MOVABLE_ARIES_FWD_FIXED_SCORPIO_BACK_DUAL_SAGITARIUS_FWD

        7 => MOVABLE_ARIES_FWD_FIXED_LEO_BACK_DUAL_SAGITARIUS_FWD

        8 => MOVABLE_SIGN_FWD_FIXED_SIGN_BACK_DUAL_SIGN_FWD

    @return: D-150 planet positions list
    """
    try:
        chart_method = const.D150_CHART_METHOD(chart_method)
    except (ValueError, TypeError):
        chart_method = const.d150_chart_method_default

    dvf = 150

    # Handle Cyclic Parivritti Method
    if chart_method == const.D150_CHART_METHOD.PARIVRITTI_CYCLIC:
        return __parivritti_cyclic(planet_positions_in_rasi, dvf, dirn=1)

    dp = []

    for planet, [sign, lon] in planet_positions_in_rasi:
        lon = lon % 30.0

        # 1. Calculate division index and segment longitude
        if chart_method == const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM:
            l, d_long = _non_uniform_d150_index_and_longitude(lon)
        else:
            l, d_long = _uniform_d150_index_and_longitude(lon)

        direction = 1  # Default to forward/direct

        # PVR/JHora matching method:
        # Uniform D150, own sign as base, forward counting for all signs.
        if chart_method == const.D150_CHART_METHOD.PVR_JHORA_METHOD_OWN_SIGN_UNIFORM_DIRECT:
            base = sign
            direction = 1

        else:
            # 2. Determine base sign and counting direction
            if sign in const.movable_signs:  # Movable Signs
                if chart_method in [
                    const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM,
                    const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_UNIFORM_DIRECT,
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_TAURUS_BACK_DUAL_GEMINI_FWD,
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_SCORPIO_BACK_DUAL_SAGITARIUS_FWD,
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_LEO_BACK_DUAL_SAGITARIUS_FWD,
                ]:
                    base = 0  # Aries
                else:  # MOVABLE_SIGN_FWD_FIXED_SIGN_BACK_DUAL_SIGN_FWD
                    base = sign

            elif sign in const.fixed_signs:  # Fixed Signs
                # All fixed sign structures run backwards (-1) EXCEPT Uniform Direct
                if chart_method != const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_UNIFORM_DIRECT:
                    direction = -1

                if chart_method in [
                    const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM,
                    const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_UNIFORM_DIRECT,
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_TAURUS_BACK_DUAL_GEMINI_FWD,
                ]:
                    base = 1  # Taurus
                elif chart_method == const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_SCORPIO_BACK_DUAL_SAGITARIUS_FWD:
                    base = 7  # Scorpio
                elif chart_method == const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_LEO_BACK_DUAL_SAGITARIUS_FWD:
                    base = 4  # Leo
                else:  # MOVABLE_SIGN_FWD_FIXED_SIGN_BACK_DUAL_SIGN_FWD
                    base = sign

            else:  # Dual Signs
                if chart_method in [
                    const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM,
                    const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_UNIFORM_DIRECT,
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_TAURUS_BACK_DUAL_GEMINI_FWD,
                ]:
                    base = 2  # Gemini
                elif chart_method in [
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_SCORPIO_BACK_DUAL_SAGITARIUS_FWD,
                    const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_LEO_BACK_DUAL_SAGITARIUS_FWD,
                ]:
                    base = 8  # Sagittarius
                else:  # MOVABLE_SIGN_FWD_FIXED_SIGN_BACK_DUAL_SIGN_FWD
                    base = sign

        # 3. Determine the final D-150 Sign
        r = (base + direction * l) % 12

        # 4. Handle longitude reversal for reverse-direction calculations
        if direction == -1:
            d_long = 30.0 - d_long
            if d_long >= 30.0:
                d_long -= 30.0

        dp.append([planet, [r, d_long]])

    return dp

def custom_divisional_chart(planet_positions_in_rasi,divisional_chart_factor,chart_method=0,
                            base_rasi=1,count_from_end_of_sign=False):
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
def mixed_chart(jd,place,varga_factor_1=None,chart_method_1=1,varga_factor_2=None,chart_method_2=1,
                dhasa_progression_correction=0.0,star_position_from_moon=1,exclude_non_planets=True):
    if exclude_non_planets:
        planet_positions_in_rasi = rasi_chart(jd,place,dhasa_progression_correction=dhasa_progression_correction)
    else:
        planet_positions_in_rasi = chart_element_rasi_positions(jd, place, star_position_from_moon=star_position_from_moon)
    if varga_factor_1==1 and varga_factor_2==1: return planet_positions_in_rasi
    return mixed_chart_from_rasi_positions(planet_positions_in_rasi=planet_positions_in_rasi,
                                           varga_factor_1=varga_factor_1, chart_method_1=chart_method_1,
                                           varga_factor_2=varga_factor_2, chart_method_2=chart_method_2)
def mixed_chart_from_rasi_positions(
        planet_positions_in_rasi,
        varga_factor_1=1,
        chart_method_1=1,
        varga_factor_2=1,
        chart_method_2=1):

    if varga_factor_1 == 1:
        pp1 = planet_positions_in_rasi
    else:
        func1_name = divisional_chart_functions[varga_factor_1]
        func1 = globals()[func1_name]
        pp1 = func1(planet_positions_in_rasi, chart_method=chart_method_1)

    if varga_factor_2 == 1:
        pp2 = pp1
    else:
        func2_name = divisional_chart_functions[varga_factor_2]
        func2 = globals()[func2_name]
        pp2 = func2(pp1, chart_method=chart_method_2)

    return pp2

def divisional_positions_from_rasi_positions(planet_positions_in_rasi,divisional_chart_factor=1,
                     chart_method=None,base_rasi=None,count_from_end_of_sign=None):
    if divisional_chart_factor==1 or divisional_chart_factor is None:
        return planet_positions_in_rasi
    else:
        if (not const.TREAT_STANDARD_CHART_AS_CUSTOM) and (divisional_chart_factor in divisional_chart_functions.keys()\
                and (base_rasi==None and (chart_method is None or chart_method >0) )):
            func_name = divisional_chart_functions[divisional_chart_factor]
            func = globals()[func_name]
            return func(
                planet_positions_in_rasi,
                chart_method=chart_method,
            )
        elif divisional_chart_factor in range(1,const.MAX_DHASAVARGA_FACTOR+1):
            return custom_divisional_chart(planet_positions_in_rasi, divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        else:
            return planet_positions_in_rasi
    
def divisional_chart(jd_at_dob,place_as_tuple,divisional_chart_factor=1,
                     chart_method=None,years=1,months=1,sixty_hours=1,calculation_type='drik',pravesha_type=0,
                     base_rasi=None,count_from_end_of_sign=None,dhasa_progression_correction=0.0,
                     exclude_non_planets=None,star_position_from_moon=1):
    """
        Get divisional/varga chart.

        @param exclude_non_planets:
            True  => old behavior. Only Lagna + planets.
            False => Lagna + planets + non-planet chart elements.

        If exclude_non_planets=False:
            D1/Rasi longitudes are first obtained using chart_element_rasi_positions().
            Then the requested varga is calculated from those Rasi longitudes using
            existing varga functions such as hora_chart(), drekkana_chart(), etc.
    """
    if exclude_non_planets is None: exclude_non_planets = const.exclude_non_planets_in_varga_chart_calculations
    if exclude_non_planets:
        planet_positions_in_rasi = rasi_chart(
            jd_at_dob,
            place_as_tuple,
            years,
            months,
            sixty_hours,
            calculation_type=calculation_type,
            pravesha_type=pravesha_type,
            dhasa_progression_correction=dhasa_progression_correction
        )
    else:
        jd_for_chart = jd_at_dob

        if not (years == 1 and months == 1 and sixty_hours == 1):
            jd_for_chart = drik.next_solar_date(
                jd_at_dob,
                place_as_tuple,
                years,
                months,
                sixty_hours
            )

        if pravesha_type == 2:
            from jhora.panchanga import vratha

            bt_year, bt_month, bt_day, bt_hours = utils.jd_to_gregorian(jd_at_dob)
            birth_date = drik.Date(bt_year, bt_month, bt_day)
            birth_time = tuple(utils.to_dms(bt_hours, as_string=False))
            year_number = bt_year + years - 1

            tp = vratha.tithi_pravesha(
                birth_date,
                birth_time,
                place_as_tuple,
                year_number
            )

            tp_date = tp[0][0]
            tp_time = tp[0][1]
            tp_time_tuple = tuple(utils.to_dms(tp_time, as_string=False))
            tp_date_new = drik.Date(tp_date[0], tp_date[1], tp_date[2])
            jd_for_chart = utils.julian_day_number(tp_date_new, tp_time_tuple)

        planet_positions_in_rasi = chart_element_rasi_positions(
            jd_for_chart,
            place_as_tuple,
            star_position_from_moon=star_position_from_moon
        )

    return divisional_positions_from_rasi_positions(
        planet_positions_in_rasi,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        base_rasi=base_rasi,
        count_from_end_of_sign=count_from_end_of_sign
    )
    
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
        if p == const.MARS_ID:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(6,9)]]: # 6 to 8th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(6,9)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'6-8')
                retrograde_planets.append(p)            
        elif p == const.MERCURY_ID:
            if planet_long > sun_long-20 and planet_long < sun_long+20:
                #print('planet',p,'planet_long',planet_long,sun_long-20,sun_long+20)
                retrograde_planets.append(p)
        elif p == const.JUPITER_ID:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(5,10)]]: # 5 to 9th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(5,10)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'5-9')
                retrograde_planets.append(p)            
        elif p == const.VENUS_ID:
            if planet_long > sun_long-30 and planet_long < sun_long+30:
                #print('planet',p,'planet_long',planet_long,sun_long-30,sun_long+30)
                retrograde_planets.append(p)
        elif p == const.SATURN_ID:
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
    retrograde_planets = []
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    for p,(h,p_long) in planet_positions[const.MARS_ID+1:const.RAHU_ID+1]: # Exclude Lagna, Sun,Moon,, Rahu and Ketu
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
    for p,(h,h_long) in planet_positions[const.MOON_ID+1:const._pp_count_upto_saturn]: # Exclude Lagna, Sun, Rahu and Ketu
        p_long = h*30+h_long if use_absolute_longitude else h_long
        combustion_range = const.combustion_range_of_planets_from_sun
        if p in retrograde_planets: 
            combustion_range = const.combustion_range_of_planets_from_sun_while_in_retrogade
        if p_long >= sun_long-combustion_range[p-2] and p_long <= sun_long+combustion_range[p-2]:
            combustion_planets.append(p)
    return combustion_planets
def vaiseshikamsa_dhasavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.dhasavarga_amsa_vaiseshikamsa)
def vaiseshikamsa_shadvarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.shadvarga_amsa_vaiseshikamsa)
def vaiseshikamsa_sapthavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.sapthavarga_amsa_vaiseshikamsa)
def vaiseshikamsa_shodhasavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    return _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,const.shodhasa_varga_amsa_vaiseshikamsa)
def _vaiseshikamsa_bala_of_planets(jd_at_dob, place_as_tuple,amsa_vaiseshikamsa=None):
    p_d = [0 for _ in const.SUN_TO_KETU]
    p_d_s = [0 for _ in const.SUN_TO_KETU]
    p_d_c = ['' for _ in const.SUN_TO_KETU]
    for dcf in amsa_vaiseshikamsa.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,divisional_chart_factor=dcf)[:const._pp_count_upto_ketu]
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
def _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,amsa_vimsopaka=None):
    p_d = [0 for _ in const.SUN_TO_KETU]
    p_d_s = [0 for _ in const.SUN_TO_KETU]
    p_d_c = ['' for _ in const.SUN_TO_KETU]
    scores = const.vimsopaka_bala_scores
    for dcf in amsa_vimsopaka.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,divisional_chart_factor=dcf)[:const._pp_count_upto_ketu]
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
                d = house.house_owner_from_planet_positions(planet_positions, h) # V4.6.0
                vv = scores[cr[p][d]]
            p_d_s[p] += amsa_vimsopaka[dcf]*vv/20
    pdc = {}
    for p in const.SUN_TO_KETU:
        p_d_c[p] = p_d_c[p][:-1]
        pdc[p] = [p_d[p],p_d_c[p],p_d_s[p]]
        #print(house.planet_list[p],pdc[p])
    return pdc
    
def vimsopaka_dhasavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.dhasavarga_amsa_vimsopaka)
def vimsopaka_shadvarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.shadvarga_amsa_vimsopaka)
def vimsopaka_sapthavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.sapthavarga_amsa_vimsopaka)
def vimsopaka_shodhasavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    return _vimsopaka_bala_of_planets(jd_at_dob, place_as_tuple,const.shodhasa_varga_amsa_vimsopaka)
def vimsamsavarga_of_planets(jd_at_dob, place_as_tuple):
    """
        Get the count - in how many vimsamsa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    planet_vimsamsa = [0 for p in const.SUN_TO_KETU]
    for _, dcf in enumerate(const.vimsamsa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, divisional_chart_factor=dcf)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(_world_city_db_df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_vimsamsa[p] += 1
    return planet_vimsamsa
def _varnada_lagna_sanjay_rath_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1,
                                           dhasa_progression_correction=0.0):
    non_planet_long = _varnada_lagna_sanjay_rath(dob, tob, place, house_index,
                                                 dhasa_progression_correction=dhasa_progression_correction)
    non_planet_key = "V"+str(house_index)
    return _get_non_planet_mixed_varga_position(non_planet_key, non_planet_long, varga_factor_1, chart_method_1,
                                                varga_factor_2, chart_method_2)
def _varnada_lagna_sanjay_rath(dob,tob, place,house_index=1,dhasa_progression_correction=0.0):
    """ TO DO : Still experimenting """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = rasi_chart(jd_at_dob, place,dhasa_progression_correction=dhasa_progression_correction)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    asc_sign = (asc_sign+house_index-1)%12
    asc_long = asc_sign*30+asc_long
    hora_full_long = get_chart_element_longitude(jd_at_dob,place,dhasa_progression_correction=dhasa_progression_correction,
                                dhasa_starting_planet='HL')
    hora_sign,hora_long_z = drik.dasavarga_from_long(hora_full_long)
    hora_sign = (hora_sign+house_index-1)%12
    hora_long = hora_sign*30+hora_long_z
    asc_is_odd = asc_sign in const.odd_signs
    if not asc_is_odd: asc_long = 360.-asc_long
    hora_is_odd = hora_sign in const.odd_signs
    if not hora_is_odd: hora_long = 360.-hora_long
    if hora_is_odd == asc_is_odd:
        vl = (asc_long + hora_long)%360
    else:
        vl = (max(asc_long,hora_long) - min (asc_long,hora_long))%360
    if not asc_is_odd: vl = 360 - vl
    return utils.norm360(vl)
def _varnada_lagna_jha_pandey_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1,
                                           dhasa_progression_correction=0.0):
    non_planet_long = _varnada_lagna_jha_pandey(dob, tob, place, house_index,
                                                 dhasa_progression_correction=dhasa_progression_correction)
    non_planet_key = "V"+str(house_index)
    return _get_non_planet_mixed_varga_position(non_planet_key, non_planet_long, varga_factor_1, chart_method_1,
                                                varga_factor_2, chart_method_2)
def _varnada_lagna_jha_pandey(dob,tob, place,house_index=1,dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = rasi_chart(jd_at_dob, place,dhasa_progression_correction=dhasa_progression_correction)
    asc_sign = planet_positions[0][1][0];asc_long = planet_positions[0][1][1]
    lagna = (asc_sign+house_index-1)%12
    asc_long = lagna*30+asc_long
    lagna_is_odd = lagna in const.odd_signs
    if not lagna_is_odd: asc_long = 360.-asc_long
    count1 = utils.count_rasis(0,lagna,direction=1) if lagna_is_odd else utils.count_rasis(11,lagna,direction=-1)
    hora_sign,hora_long = drik.hora_lagna(jd_at_dob,place, dhasa_progression_correction=dhasa_progression_correction) # V3.1.9
    hora_lagna = (hora_sign+house_index-1)%12
    hora_long = hora_lagna*30+hora_long
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    if not lagna_is_odd: hora_long = 360.-hora_long
    count2 = utils.count_rasis(0,hora_lagna,direction=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,direction=-1)
    count = (count1 + count2)%12 if count1%2 == count2%2 else (max(count1,count2) - min (count1,count2))%12
    count_is_odd = count%2 != 0
    vl = (asc_long + hora_long)%360 if count_is_odd else (max(asc_long,hora_long) - min (asc_long,hora_long))%360
    return utils.norm360(vl)
def _varnada_lagna_bv_raman_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1,
                                           dhasa_progression_correction=0.0):
    non_planet_long = _varnada_lagna_bv_raman(dob, tob, place, house_index,
                                                 dhasa_progression_correction=dhasa_progression_correction)
    non_planet_key = "V"+str(house_index)
    return _get_non_planet_mixed_varga_position(non_planet_key, non_planet_long, varga_factor_1, chart_method_1,
                                                varga_factor_2, chart_method_2)
def _varnada_lagna_sharma_mixed_chart(dob,tob, place,house_index=1,varga_factor_1=1,chart_method_1=1,
                                           varga_factor_2=1,chart_method_2=1,
                                           dhasa_progression_correction=0.0):
    non_planet_long = _varnada_lagna_sharma(dob, tob, place, house_index,
                                                 dhasa_progression_correction=dhasa_progression_correction)
    non_planet_key = "V"+str(house_index)
    return _get_non_planet_mixed_varga_position(non_planet_key, non_planet_long, varga_factor_1, chart_method_1,
                                                varga_factor_2, chart_method_2)
def varnada_lagna_mixed_chart(dob,tob,place,house_index=1,varga_factor_1=1,
                              chart_method_1=1,varga_factor_2=1,chart_method_2=1,varnada_method=None,
                              dhasa_progression_correction=0.0):
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
    if varnada_method is None: varnada_method = const.varnada_method_default
    if varnada_method==const.VARNADA_METHOD.BV_RAMAN:
        vl = _varnada_lagna_bv_raman_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2,dhasa_progression_correction=dhasa_progression_correction)
    elif varnada_method==const.VARNADA_METHOD.SHARMA_SANTHANAM:
        vl = _varnada_lagna_sharma_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2,dhasa_progression_correction=dhasa_progression_correction)
    elif varnada_method==const.VARNADA_METHOD.SANJAY_RATH:
        vl = _varnada_lagna_sanjay_rath_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2,dhasa_progression_correction=dhasa_progression_correction)
    elif varnada_method==const.VARNADA_METHOD.JHA_PANDEY:
        vl = _varnada_lagna_jha_pandey_mixed_chart(dob, tob, place, house_index=house_index,
                        varga_factor_1=varga_factor_1, chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                        chart_method_2=chart_method_2,dhasa_progression_correction=dhasa_progression_correction)
    return drik.dasavarga_from_long(vl)
def varnada_lagna(dob,tob,place,house_index=1,varnada_method=None,dhasa_progression_correction=0.0):
    """
        Get Varnada Lagna
            Ref: https://saptarishisshop.com/a-look-at-the-calculation-of-varnada-lagna-by-abhishekha/
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
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
    if varnada_method is None: varnada_method = const.varnada_method_default
    if varnada_method==const.VARNADA_METHOD.BV_RAMAN:
        vl =_varnada_lagna_bv_raman(dob, tob, place, house_index,
                                       dhasa_progression_correction=dhasa_progression_correction)
    elif varnada_method==const.VARNADA_METHOD.SHARMA_SANTHANAM:
        vl = _varnada_lagna_sharma(dob, tob, place, house_index, 
                                       dhasa_progression_correction=dhasa_progression_correction)
    elif varnada_method==const.VARNADA_METHOD.SANJAY_RATH:
        vl = _varnada_lagna_sanjay_rath(dob, tob, place, house_index,
                                       dhasa_progression_correction=dhasa_progression_correction)
    elif varnada_method==const.VARNADA_METHOD.JHA_PANDEY:
        vl = _varnada_lagna_jha_pandey(dob, tob, place, house_index,
                                       dhasa_progression_correction=dhasa_progression_correction)
    return drik.dasavarga_from_long(vl)

def _varnada_lagna_bv_raman(dob,tob,place,house_index=1, dhasa_progression_correction=0.0):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varnada_lagna_rasi, varnada_lagna_longitude 
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = rasi_chart(jd_at_dob,place,dhasa_progression_correction=dhasa_progression_correction)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,direction=1) if lagna_is_odd else utils.count_rasis(11,lagna,direction=-1)
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place, dhasa_progression_correction=dhasa_progression_correction) # V3.1.9
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,direction=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,direction=-1)
    count = (count1 + count2)%12 if hora_lagna_is_odd == lagna_is_odd else (max(count1,count2) - min (count1,count2))%12
    _varnada_lagna = utils.count_rasis(1,count,direction=1) if lagna_is_odd else utils.count_rasis(12,count,direction=-1)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return utils.norm360(_varnada_lagna*30+asc_long)
def _varnada_lagna_santhanam(dob,tob,place,house_index=1,dhasa_progression_correction=0.0):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varnada_lagna_rasi, varnada_lagna_longitude 
    """
    return _varnada_lagna_sharma(dob, tob, place, house_index,dhasa_progression_correction=dhasa_progression_correction)
def _varnada_lagna_sharma(dob,tob,place,house_index=1,dhasa_progression_correction=0.0):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varnada_lagna_rasi, varnada_lagna_longitude 
    """
    _debug_ = False
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = rasi_chart(jd_at_dob,place,dhasa_progression_correction=dhasa_progression_correction)
    lagna = (planet_positions[0][1][0]+house_index-1)%12; asc_long = planet_positions[0][1][1]
    lagna_is_odd = lagna in const.odd_signs
    count1 = utils.count_rasis(0,lagna,direction=1) if lagna_is_odd else utils.count_rasis(11,lagna,direction=-1)
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place,dhasa_progression_correction=dhasa_progression_correction) # V3.1.9
    hora_lagna = (hora_lagna+house_index-1)%12
    hora_lagna_is_odd = hora_lagna in const.odd_signs
    count2 = utils.count_rasis(0,hora_lagna,direction=1) if hora_lagna_is_odd else utils.count_rasis(11,hora_lagna,direction=-1)
    count = (count1 + count2)%12 if count1%2 == count2%2 else (max(count1,count2) - min (count1,count2))%12
    count_is_odd = count%2 != 0
    _varnada_lagna = utils.count_rasis(1,count,direction=1) if count_is_odd else utils.count_rasis(12,count,direction=-1)
    _varnada_lagna -= 1 ## Keep in 0..11 range instead of 1..12
    return utils.norm360(_varnada_lagna*30+asc_long)
def benefics_and_malefics(jd,place,divisional_chart_factor=1,method=2,exclude_rahu_ketu=False):
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
        if _tithi >= 8 and _tithi <=15: benefics.append(1) # Waxing moon benefic
        if _tithi >= 23 and _tithi <=30: malefics.append(1) # Waning moon malefic
    planet_positions = divisional_chart(jd, place,divisional_chart_factor=divisional_chart_factor)
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
def benefics(jd,place,divisional_chart_factor=1,method=2,exclude_rahu_ketu=False):
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
    return benefics_and_malefics(jd, place, method=method,divisional_chart_factor=divisional_chart_factor,
                                 exclude_rahu_ketu=exclude_rahu_ketu)[0]
def malefics(jd,place,divisional_chart_factor=1,method=2,exclude_rahu_ketu=False):
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
    return benefics_and_malefics(jd, place, method=method,divisional_chart_factor=divisional_chart_factor,
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
def _stronger_planet_from_the_planet_positions(planet_positions,planet_list):
    def _compare(planet1,planet2):
        return 1 if house.stronger_planet_from_planet_positions(planet_positions, planet1, planet2)==planet1 else -1 
    from functools import cmp_to_key
    planet_list.sort(key=cmp_to_key(_compare))
    return planet_list[0]    
def _order_stronger_planets(planet_positions,reverse=False):
    """ Still under testing """
    def _compare(planet1,planet2):
        return 1 if house.stronger_planet_from_planet_positions(planet_positions, planet1, planet2)==planet1 else -1 
    planet_list = const.SUN_TO_KETU
    from functools import cmp_to_key
    planet_list.sort(key=cmp_to_key(_compare))
    if reverse: planet_list = list(reversed(planet_list))
    return planet_list
def special_planet_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                          dhasa_progression_correction=0.0):
    spl_planet_positions_in_rasi = special_planet_longitudes(dob, tob, place)
    if varga_factor_1==1 and varga_factor_2==1: return spl_planet_positions_in_rasi
    pp1 = spl_planet_positions_in_rasi if varga_factor_1==1 else \
            eval(divisional_chart_functions[varga_factor_1]+'(spl_planet_positions_in_rasi,chart_method=chart_method_1)')
    pp2 = pp1 if varga_factor_2==2 else eval(divisional_chart_functions[varga_factor_2]+'(pp1,chart_method=chart_method_2)')
    return pp2
def special_planet_longitudes(dob, tob, place, divisional_chart_factor=1, chart_method=None,
                              base_rasi=None, count_from_end_of_sign=None,
                              dhasa_progression_correction=0.0):

    jd_at_dob = utils.julian_day_number(dob, tob)

    spl_rasi_positions = []

    for sp, sp_func in utils._drik_upagrahas.items():
        if not sp_func.endswith('_longitude'):
            sp_func += '_longitude'

        v = getattr(drik, sp_func)(dob, tob, place, dhasa_progression_correction)
        spl_rasi_positions.append([sp, [v[0], v[1]]])

    sun_long = rasi_chart(jd_at_dob, place)[1][1]
    sun_long = sun_long[0] * 30 + sun_long[1]

    for sp, sp_func in utils._chart_upagrahas.items():
        v = drik.solar_upagraha_longitudes(
            sun_long,
            upagraha=sp_func,
            dhasa_progression_correction=dhasa_progression_correction
        )

        spl_rasi_positions.append([sp, [v[0], v[1]]])

    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)
def special_lagna_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1,
                             base_rasi=None,count_from_end_of_sign=None,dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    spl_rasi_positions = []
    for sp,sp_func in utils._special_lagnas.items():
        func = getattr(drik, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.panchanga.drik' has no callable '{sp_func}'")
        v = func(
            jd_at_dob,
            place,
            dhasa_progression_correction=dhasa_progression_correction,
        )
        spl_rasi_positions.append([sp,[v[0],v[1]]])
    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)
def special_lagna_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                          dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    spl_rasi_positions = []
    for sp,sp_func in utils._special_lagnas.items():
        func = getattr(drik, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.panchanga.drik' has no callable '{sp_func}'")
        v = func(
            jd_at_dob,
            place,
            dhasa_progression_correction=dhasa_progression_correction,
        )
        spl_rasi_positions.append([sp,[v[0],v[1]]])
    return mixed_chart_from_rasi_positions(planet_positions_in_rasi=spl_rasi_positions, varga_factor_1=varga_factor_1,
                                           chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                                           chart_method_2=chart_method_2)
def sphuta_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1,base_rasi=None,count_from_end_of_sign=None,
                      dhasa_progression_correction=0.0):
    from jhora.horoscope.chart import sphuta
    spl_rasi_positions = []
    for dsp in utils._sphutas.keys():
        _house_index = int(dsp[1:])
        sp_func = utils._sphutas[dsp] + "_sphuta"
        func = getattr(sphuta, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.horoscope.chart.sphuta' has no callable '{sp_func}'")

        v = func(
            dob,
            tob,
            place,
        )
        spl_rasi_positions.append([dsp,[v[0],v[1]]])
    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)
def sphuta_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,
                                         varga_factor_2=1,chart_method_2=1,varnada_method=None,
                              dhasa_progression_correction=0.0):
    from jhora.horoscope.chart import sphuta
    spl_rasi_positions = []
    for dsp in utils._sphutas.keys():
        _house_index = int(dsp[1:])
        sp_func = utils._sphutas[dsp] + "_sphuta"
        func = getattr(sphuta, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.horoscope.chart.sphuta' has no callable '{sp_func}'")

        v = func(
            dob,
            tob,
            place,
        )
        spl_rasi_positions.append([dsp,[v[0],v[1]]])
    """ This is where you should call varga_1, varga_2 chart methods to call """
    return mixed_chart_from_rasi_positions(planet_positions_in_rasi=spl_rasi_positions, varga_factor_1=varga_factor_1,
                                           chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                                           chart_method_2=chart_method_2)
def varnada_lagna_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1, varnada_method=None,
                             base_rasi=None,count_from_end_of_sign=None,dhasa_progression_correction=0.0,
                             jhora_compatible=False):
    if jhora_compatible:
        return _jhora_varnada_lagna_longitudes(
            dob,tob,place,divisional_chart_factor,chart_method,varnada_method,
            base_rasi,count_from_end_of_sign,dhasa_progression_correction)
    spl_rasi_positions = []
    for dsp in utils._varnada_lagnas.keys():
        _house_index = int(dsp[1:])
        """ Calculate Rasi Positions here so no divisional_chart_Factor argument """
        v = varnada_lagna(
            dob,
            tob,
            place,
            house_index=_house_index,
            varnada_method=varnada_method,
        )
        spl_rasi_positions.append([dsp,[v[0],v[1]]])
    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)
def varnada_lagna_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,
                                         varga_factor_2=1,chart_method_2=1,varnada_method=None,
                              dhasa_progression_correction=0.0,jhora_compatible=False):
    if jhora_compatible:
        first = _jhora_varnada_lagna_longitudes(
            dob,tob,place,varga_factor_1,chart_method_1,varnada_method,
            dhasa_progression_correction=dhasa_progression_correction)
        return divisional_positions_from_rasi_positions(first,varga_factor_2,chart_method_2)
    spl_rasi_positions = []
    for dsp in utils._varnada_lagnas.keys():
        _house_index = int(dsp[1:])
        """ Calculate Rasi Positions here so no varga_1 varga_2 arguments """
        v = varnada_lagna_mixed_chart(
            dob,
            tob,
            place,
            house_index=_house_index,
            varnada_method=varnada_method,
            dhasa_progression_correction=dhasa_progression_correction,
        )
        spl_rasi_positions.append([dsp,[v[0],v[1]]])
    """ This is where you should call varga_1, varga_2 chart methods to call """
    return mixed_chart_from_rasi_positions(planet_positions_in_rasi=spl_rasi_positions, varga_factor_1=varga_factor_1,
                                           chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                                           chart_method_2=chart_method_2)
def _jhora_varnada_lagna_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1,varnada_method=None,
                                   base_rasi=None,count_from_end_of_sign=None,dhasa_progression_correction=0.0):
    """Opt-in compatibility with the verified JHora BV Raman chart convention.

    Signs use each chart's Lagna and Hora Lagna. Degrees retain the ordinary
    transformation of natal Varnada. D0 is a zero-degree display placeholder.
    Mixed charts transform the recomputed first-chart Varnada in chart two.
    """
    if varnada_method is None:
        varnada_method = const.varnada_method_default
    if varnada_method != const.VARNADA_METHOD.BV_RAMAN:
        raise ValueError('JHora compatibility is verified only for BV Raman Varnada')
    jd = utils.julian_day_number(dob,tob)
    asc = rasi_chart(jd,place,dhasa_progression_correction=dhasa_progression_correction)[0][1]
    hora = drik.hora_lagna(jd,place,dhasa_progression_correction=dhasa_progression_correction)
    natal = []
    for key in utils._varnada_lagnas:
        position = varnada_lagna(dob,tob,place,house_index=int(key[1:]),varnada_method=varnada_method,
                                 dhasa_progression_correction=dhasa_progression_correction)
        natal.append([key,list(position)])
    if divisional_chart_factor == 0:
        context = [['L',[0,0.0]],['HL',[0,0.0]]]
        projected = [[key,[0,0.0]] for key,_ in natal]
    else:
        context = divisional_positions_from_rasi_positions(
            [['L',list(asc)],['HL',list(hora)]],divisional_chart_factor,chart_method,
            base_rasi,count_from_end_of_sign)
        projected = divisional_positions_from_rasi_positions(
            natal,divisional_chart_factor,chart_method,base_rasi,count_from_end_of_sign)
    result = []
    for key,(_,longitude) in projected:
        shift = int(key[1:])-1
        lagna = (context[0][1][0]+shift)%12
        hora_lagna = (context[1][1][0]+shift)%12
        odd_lagna = lagna in const.odd_signs
        odd_hora = hora_lagna in const.odd_signs
        count1 = utils.count_rasis(0,lagna,1) if odd_lagna else utils.count_rasis(11,lagna,-1)
        count2 = utils.count_rasis(0,hora_lagna,1) if odd_hora else utils.count_rasis(11,hora_lagna,-1)
        count = (count1+count2)%12 if odd_lagna==odd_hora else abs(count1-count2)%12
        sign = (count-1)%12 if odd_lagna else (12-count)%12
        result.append([key,[sign,longitude]])
    return result
def arudha_lagna_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1, arudha_base=0,
                            bhava_madhya_method=None, base_rasi=None,count_from_end_of_sign=None,
                            dhasa_progression_correction=0.0):
    from jhora.horoscope.chart import arudhas
    jd_at_dob = utils.julian_day_number(dob, tob)
    arudha_base_str = "A" #arudhas._bhava_arudha_prefix_list[arudha_base]
    spl_rasi_positions = []
    a_longs = arudhas.bhava_arudha_longitudes(
        jd_at_dob,
        place,
        divisional_chart_factor=1, # First get Rasi Longitudes
        arudha_base=arudha_base,
        bhava_madhya_method=bhava_madhya_method,
    )
    for ai,a_long in enumerate(a_longs):
        sp = arudha_base_str+str(ai+1)
        p_rasi, p_long = drik.dasavarga_from_long(a_long)
        spl_rasi_positions.append([sp,(p_rasi,p_long)])
    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)

def arudha_lagna_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                        arudha_base=0,bhava_madhya_method=None,dhasa_progression_correction=0.0):
    from jhora.horoscope.chart import arudhas
    jd_at_dob = utils.julian_day_number(dob, tob)
    _bhava_arudha_prefix_list = ["A","Su","Mo","Ma","Ju","ve","Sa","Ra","Ke"]
    arudha_base_str = arudhas._bhava_arudha_prefix_list[arudha_base]
    spl_rasi_positions = []
    a_longs = arudhas.bhava_arudha_longitudes(
        jd_at_dob,
        place,
        divisional_chart_factor=1, # First get Rasi Longitudes
        arudha_base=arudha_base,
        bhava_madhya_method=bhava_madhya_method,
    )
    for ai,a_long in enumerate(a_longs):
        sp = arudha_base_str+str(ai+1)
        p_rasi, p_long = drik.dasavarga_from_long(a_long)
        spl_rasi_positions.append([sp,(p_rasi,p_long)])
    return mixed_chart_from_rasi_positions(planet_positions_in_rasi=spl_rasi_positions, varga_factor_1=varga_factor_1,
                                           chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                                           chart_method_2=chart_method_2)

def solar_upagraha_longitudes(planet_positions,upagraha,divisional_chart_factor=1, chart_method=1, base_rasi=None,
                              count_from_end_of_sign=None):
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
    jd_at_dob = utils.julian_day_number(dob, tob)
    spl_rasi_positions = []
    sub_planet_list_2 = {'Dm':'dhuma','Vp':'vyatipaata','Pv':'parivesha','Ic':'indrachaapa','Uk':'upaketu'}
    sun_long = rasi_chart(jd_at_dob, place)[1][1]; sun_long = sun_long[0]*30+sun_long[1]
    for sp,sp_func in sub_planet_list_2.items():
        eval_str = "drik.solar_upagraha_longitudes(sun_long,upagraha='"+str(sp_func)+"')"
        v = eval(eval_str)
        spl_rasi_positions.append([sp,[v[0],v[1]]]) 
    #"""
    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)
def _amsa_old(jd, place, divisional_chart_factor=1, include_upagrahas=False, include_special_lagnas=False, include_sphutas=False,
          chart_method=1, base_rasi=None, count_from_end_of_sign=None):
    
    y, m, d, fh = utils.jd_to_gregorian(jd); dob = drik.Date(y, m, d); tob = (fh, 0, 0)
    __amsa_planets = {}; __amsa_special = {}; __amsa_upagraha = {}; __amsa_sphuta = {}
    rasi_dict = {}
    if divisional_chart_factor == 150:
        rasi_chart = divisional_chart(jd, place, divisional_chart_factor=1, exclude_non_planets=False)
        rasi_dict = {p: (h, long) for p, (h, long) in rasi_chart}
    def _get_amsa_index_from_longitude(p_key, varga_long):
        if divisional_chart_factor == 150:
            rasi_sign_num, rasi_long = rasi_dict[p_key]  # Expects 0..11 based sign
            if chart_method == const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM:
                raw_idx = _non_uniform_d150_index_and_longitude(rasi_long)[0]
            else:
                raw_idx = _uniform_d150_index_and_longitude(rasi_long, dvf=150)[0]
            if chart_method in [const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM,
                                const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_TAURUS_BACK_DUAL_GEMINI_FWD, 
                                const.D150_CHART_METHOD.MOVABLE_SIGN_FWD_FIXED_SIGN_BACK_DUAL_SIGN_FWD]:
                if rasi_sign_num in const.movable_signs:
                    final_idx = raw_idx
                elif rasi_sign_num in const.fixed_signs:
                    final_idx = 149 - raw_idx  # 0-based pure reverse mapping
                elif rasi_sign_num in const.dual_signs:
                    final_idx = (raw_idx + 75) % 150  # 76th Nadi 0-based offset
            elif chart_method in [const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_SCORPIO_BACK_DUAL_SAGITARIUS_FWD, 
                                  const.D150_CHART_METHOD.MOVABLE_ARIES_FWD_FIXED_LEO_BACK_DUAL_SAGITARIUS_FWD]:
                final_idx = 149 - raw_idx if rasi_sign_num in const.fixed_signs else raw_idx
            elif chart_method == const.D150_CHART_METHOD.PARIVRITTI_CYCLIC:
                final_idx = ((rasi_sign_num * 150) + raw_idx) % 150
            else:  # Uniform Direct methods -> Forward counting always
                final_idx = raw_idx
            return max(0, min(final_idx, 149))
        # Fallback loop behavior for standard charts (D-9, D-10, etc.)
        df = 30.0 / divisional_chart_factor
        return int(varga_long / df)
    div_planet_positions = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                            chart_method=chart_method, base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign,
                                            exclude_non_planets=False)
    planet_positions_dict = {p: (h, long) for p, (h, long) in div_planet_positions}
    for p, (h, long) in planet_positions_dict.items():
        try:
            planet_id = int(p)
        except:
            planet_id = None
        if p == const._ascendant_symbol or planet_id in const.SUN_TO_PLUTO:
            __amsa_planets[p] = _get_amsa_index_from_longitude(p, long)
        elif p in utils._special_lagnas.keys():
            p_str = utils._special_lagnas[p] + '_str'
            __amsa_special[p_str] = _get_amsa_index_from_longitude(p, long)
        elif p in utils._chart_upagrahas.keys():
            p_str = utils._chart_upagrahas[p] + '_str'
            __amsa_upagraha[p_str] = _get_amsa_index_from_longitude(p, long)
        elif p in utils._drik_upagrahas.keys():
            p_str = utils._drik_upagrahas[p] + '_str'
            __amsa_upagraha[p_str] = _get_amsa_index_from_longitude(p, long)
        elif p in utils._sphutas.keys():
            p_str = utils._sphutas[p] + '_sphuta_str'
            __amsa_sphuta[p_str] = _get_amsa_index_from_longitude(p, long)
    return __amsa_planets, __amsa_special, __amsa_upagraha, __amsa_sphuta

def _get_KP_lords_from_planet_longitude(planet,rasi,rasi_longitude):
    lords = const.vimsottari_adhipati_list
    lord_fractions = const.KP_lord_fractions
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
    if const.use_kp_dictionary_for_lords_calculation:
        kp_info = {}
        for p,(h,long) in planet_positions:
            kp_info_planet = _get_KP_lords_from_planet_longitude(p,h,long)
            kp_info = {**kp_info, **kp_info_planet}
        return kp_info
    else:
        kp_info = {}
        for p,(h,long) in planet_positions:
            kp_info_planet = utils.kp_lords_for_longitude(p,h*30+long)
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
    pb = [planet for planet, (sign,long) in planet_positions[1:const._pp_count_upto_ketu] if long >= const.pushkara_bhagas[sign]-1 and long < const.pushkara_bhagas[sign]]
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

def _planets_in_mrityu_bhaga_new(dob, tob, place, planet_positions, 
                             mrityu_bhaga_source=None,
                             mrityu_bhaga_method=None):
    """
        TODO: UNDER TESTING DO NOT USE YET
    """
    """
    Returns the list of planets in the mrityu bhaga matching the JHora configuration options.
    
    @param mrityu_bhaga_source:
        0 = Use Jataka Parijata degrees (Default)
        1 = Use Brihat Prajapatyam degrees
    @param mrityu_bhaga_method: 
        0 = Exact degree / planet-specific custom orb (e.g., abs(long - base) <= tolerance)
        1 = The entire 1 degree of the sign (e.g., base - 1 <= longitude <= base)
        2 = An orb of 1 degree around the exact point (e.g., abs(long - base) <= 1.0)
    
    @return: [(planet, rasi, diff in long from mrityu longitude), ...]
    """
    from jhora import utils
    
    # Fallback to global config constants if arguments are omitted
    if mrityu_bhaga_source is None:
        mrityu_bhaga_source = getattr(const, 'mrityu_bhaga_source_default', 0)
        
    if mrityu_bhaga_method is None:
        mrityu_bhaga_method = getattr(const, 'mrityu_bhaga_method_default', 0)

    # Core planetary bodies (integers 0 through 8)
    working_positions = planet_positions[:const._pp_count_upto_ketu]
    
    # Mandi position calculation
    mandi_rasi, mandi_rel_long = drik.maandi_longitude(dob, tob, place)
    working_positions = working_positions + [('Md', (mandi_rasi, mandi_rel_long))]
        
    # Lagna position calculation
    jd = utils.julian_day_number(dob, tob)
    asc = drik.ascendant(jd, place)
    lagna_rasi = asc[0]
    lagna_rel_long = asc[1]
    working_positions = working_positions + [('L', (lagna_rasi, lagna_rel_long))]

    # Display mappings matching your integer rules (0-8 are ints, 'Md' and 'L' are keys)
    planet_names = [*range(const._planets_upto_ketu)] + ['Md', 'L']

    result = []
    for planet, (rasi, longitude) in working_positions:
        if planet == 'Md':
            planet_index = 9
        elif planet == 'L':
            planet_index = 10
        else:
            planet_index = planet  
        
        # 1. Source Logic (Jataka Parijata vs. Brihat Prajapatyam)
        if mrityu_bhaga_source == 1:  # Brihat Prajapatyam
            if planet_index == 1:  # Moon gets its own distinct sign degrees
                bp_moon_degrees = [26, 12, 13, 14, 25, 11, 26, 14, 13, 25, 5, 12]
                base_longitude = bp_moon_degrees[rasi]
            else:
                # All other points inherit the sign's base degree (Lagna column index 10)
                base_longitude = const.mrityu_bhaga_base_longitudes[rasi][10]
        else:  # 0 = Jataka Parijata (Default multi-planet matrix)
            base_longitude = const.mrityu_bhaga_base_longitudes[rasi][planet_index]
        
        is_in_mrityu_bhaga = False
        long_diff = abs(longitude - base_longitude)
        
        # 2. Mathematical Definition Logic
        if mrityu_bhaga_method == 0:
            # Method 0: Exact point / planet-specific customized orb
            tolerance = const.mrityu_bhaga_tolerances[planet]
            if long_diff <= tolerance:
                is_in_mrityu_bhaga = True
                
        elif mrityu_bhaga_method == 1:
            # Method 1: The entire 1 degree of the sign (e.g., between 19° and 20°)
            if (base_longitude - 1.0) <= longitude <= base_longitude:
                is_in_mrityu_bhaga = True
                
        elif mrityu_bhaga_method == 2:
            # Method 2: An orb of 1 degree around the exact point (+/- 1.0°)
            if long_diff <= 1.0:
                is_in_mrityu_bhaga = True
        
        if is_in_mrityu_bhaga:
            result.append((planet_names[planet_index], rasi, long_diff))
            
    return result

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
    if (p1==const.RAHU_ID and p2==const.KETU_ID) or (p1==const.KETU_ID and p2==const.RAHU_ID):
        warnings.warn("Rahu and Ketu do not conjoin ever. Program returns error")
        return None
    pi1 = 0 if p1==const._ascendant_symbol else p1+1; pi2 = 0 if p2==const._ascendant_symbol else p2+1
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
            """ For separation Angle > 180 Lagrange may not work """
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
def _amsa_d150(jd,place,divisional_chart_factor=1,include_upagrahas=False,
          include_special_lagnas=False,include_sphutas=False,chart_method=1,base_rasi=None,count_from_end_of_sign=None):
    #msgs = get_amsa_resources()
    planet_positions = divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                            chart_method=chart_method,base_rasi=base_rasi, count_from_end_of_sign=count_from_end_of_sign)
    f1 = 30.0/divisional_chart_factor
    _ap = []
    for p,(h,long) in planet_positions:
        pstr = utils.resource_strings['ascendant_str'] if p==const._ascendant_symbol else utils.PLANET_NAMES[p]
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
def get_chart_element_longitude(
    jd,
    place,
    divisional_chart_factor=1,
    base_rasi=None,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
    count_from_end_of_sign=None,
    arudha_base = 0,
    varnada_method=None,
    house_index = 1,
    dhasa_progression_correction = 0.0,
    ):
    """
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param star_position_from_moon: 1=Moon (default), 4=Kshema, 5=Utpanna, 8=Adhana
        @param divisional_chart_factor: Default=1 (1=Raasi, 9=Navamsa)
        @param chart_method: various chart methods (see charts module)
        @param dhasa_starting_planet: 'L', 0=Sun ... 8=Ketu,9=Uranus,10=Neptune,11=Pluto
            Upagrahas: 'Kl':'kaala','Mr':'mrityu','Ap':'artha','Yg':'yama','Gk':'gulika','Md':'maandi',
                      'Dm':'dhuma','Vp':'vyatipaata','Pv':'parivesha','Ic':'indrachaapa','Uk':'upaketu'
            Special Lagnas: BL':'bhava_lagna','HL':'hora_lagna','GL':'ghati_lagna','PL':'pranapada_lagna',
                            'VL':'vighati_lagna','KL':'kunda_lagna','BBL':'bhrigu_bindhu_lagna',
                            'SL':'sree_lagna'
            Arudha Lagnas: A1,A2,...A12
            Varnada Lagnas: V1,V2,...V12
            Sphutas: 'S1': 'Tri Sphuta', 'S2': 'Chatur Sphuta', 'S3': 'Pancha Sphuta', 'S4': 'Prana Sphuta', 
                    'S5': 'Deha Sphuta', 'S6': 'Mrityu Sphuta', 'S7': 'Sookshma Tri Sphuta', 'S8': 'Beeja Sphuta', 
                    'S9': 'Kshetra Sphuta', 'S10': 'Tithi Sphuta', 'S11': 'Yoga Sphuta', 'S12': 'Rahu Tithi Sphuta', 
                    'S13': 'Yogi Sphuta', 'S14': 'Avayogi Sphuta'
                      
        @param dhasa_level_index: depth 1..6
        @return: planet_longitude (0..360)

        NOTE:
        For deriving varga charts for non-planets, call this with
        divisional_chart_factor=1 first, then apply the varga transformation
        from the D1/Rasi longitude.
    """
    if star_position_from_moon is None or star_position_from_moon not in const.SUN_TO_KETU:
        star_position_from_moon = 1
    try:
        planet_id = int(dhasa_starting_planet)
    except:
        planet_id = None

    y, m, d, fh = utils.jd_to_gregorian(jd)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    one_star = 360.0 / 27.0

    if divisional_chart_factor == 1:
        planet_positions = rasi_chart(jd, place)[:const._pp_count_upto_pluto]
    else:
        planet_positions = divisional_chart(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            exclude_non_planets=True,
            dhasa_progression_correction = dhasa_progression_correction,
        )[:const._pp_count_upto_pluto]

    if dhasa_starting_planet == const._ascendant_symbol:
        planet_long = planet_positions[0][1][0] * 30 + planet_positions[0][1][1]

    elif planet_id is not None and planet_id in const.SUN_TO_PLUTO:
        planet_long = (
            planet_positions[planet_id + 1][1][0] * 30
            + planet_positions[planet_id + 1][1][1]
        )

    elif dhasa_starting_planet in utils._drik_upagrahas.keys():
        sp_func = utils._drik_upagrahas[dhasa_starting_planet] + "_longitude"
        func = getattr(drik, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'drik' has no callable '{sp_func}'")

        v = func(
            dob,
            tob,
            place,
        )
        planet_long = v[0] * 30 + v[1]

    elif dhasa_starting_planet in utils._special_lagnas.keys():
        sp_func = utils._special_lagnas[dhasa_starting_planet]
        func = getattr(drik, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.panchanga.drik' has no callable '{sp_func}'")

        v = func(
            jd,
            place,
        )
        planet_long = v[0] * 30 + v[1]

    elif dhasa_starting_planet in utils._chart_upagrahas.keys():
        sun_long_tuple = planet_positions[const.SUN_ID+1][1]
        sun_long = sun_long_tuple[0]*30+sun_long_tuple[1]
        v = drik.solar_upagraha_longitudes(
            solar_longitude=sun_long,
            upagraha=utils._chart_upagrahas[dhasa_starting_planet],
            ) # dhasa_progression_correction already applied to Sun Longitude
        planet_long = v[0] * 30 + v[1]

    elif dhasa_starting_planet in utils._varnada_lagnas.keys():
        _house_index = int(dhasa_starting_planet[1:])

        v = varnada_lagna(
            dob,
            tob,
            place,
            house_index=_house_index,
            varnada_method=varnada_method,
        )
        planet_long = v[0] * 30 + v[1]

    elif dhasa_starting_planet in utils._sphutas.keys():
        from jhora.horoscope.chart import sphuta
        sp_func = utils._sphutas[dhasa_starting_planet] + "_sphuta"
        func = getattr(sphuta, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.horoscope.chart.sphuta' has no callable '{sp_func}'")

        v = func(
            dob,
            tob,
            place,
        )
        planet_long = v[0] * 30 + v[1]

    elif dhasa_starting_planet in utils._arudha_lagnas.keys():
        _arudha_index = int(dhasa_starting_planet[1:])
        from jhora.horoscope.chart import arudhas

        planet_long = arudhas.bhava_arudha_longitudes(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            arudha_base=arudha_base,
        )[_arudha_index - 1]
    elif dhasa_starting_planet in utils._sahams.keys():
        from jhora.horoscope.transit import saham
        sp_func = utils._sahams[dhasa_starting_planet] + "_saham"
        func = getattr(saham, sp_func, None)
        if not callable(func):
            raise AttributeError(f"'jhora.horoscope.transit' has no callable '{sp_func}'")
        vl = func(jd, place, dhasa_progression_correction=dhasa_progression_correction)
        planet_long = vl
    else:
        raise ValueError(
            "dhasa_starting_planet ("
            + str(dhasa_starting_planet)
            + ") is not one of utils.chart_planets.keys()"
        )

    if dhasa_starting_planet == 1:
        planet_long += (star_position_from_moon - 1) * one_star
    
    return utils.norm360(planet_long)
def get_nakshathra_dhasa_progression_longitudes(
        jd_at_dob, place,
        planet_progression_correction, # Progressed Longitude of Moon
        divisional_chart_factor=1,
        chart_method=1,
        star_position_from_moon=1,
        dhasa_starting_planet=1,
        include_non_planets = False,
        ):
    #pp_rasi = divisional_chart(jd_at_dob, place, divisional_chart_factor=1, chart_method=chart_method)
    main_planet_list = (list(utils._main_planets.keys())[:const._pp_count_upto_pluto-1] if const._INCLUDE_URANUS_TO_PLUTO 
                        else list(utils._main_planets.keys())[:const._pp_count_upto_ketu-1])
    planet_list = list(utils._ascendant.keys())+ main_planet_list
    pp_rasi_progressed = []
    if include_non_planets:
        planet_list += (list(utils._drik_upagrahas.keys())+
                       list(utils._chart_upagrahas.keys())+list(utils._special_lagnas.keys())+
                       list(utils._varnada_lagnas.keys())+list(utils._sphutas.keys())+
                       list(utils._arudha_lagnas.keys()))
    """ Note: First we rasi positions and then find varga division so for rasi we pass divisional_chart_factor=1"""
    for p in planet_list:
        p_long = get_chart_element_longitude(jd_at_dob, place, divisional_chart_factor=1, chart_method=chart_method,
                                           star_position_from_moon=star_position_from_moon, dhasa_starting_planet=p)
        p_long_progressed = utils.norm360(p_long+planet_progression_correction)
        pz,pl = drik.dasavarga_from_long(p_long_progressed)
        pp_rasi_progressed.append([p,(pz,pl)])
    if divisional_chart_factor > 1:
        pp_dcf_progressed = divisional_positions_from_rasi_positions(pp_rasi_progressed, divisional_chart_factor=divisional_chart_factor,
                                                       chart_method=chart_method)
        return pp_dcf_progressed
    return pp_rasi_progressed

def nava_thaara_for_all_planets(planet_positions):
    pp = planet_positions[:const._pp_count_upto_ketu]
    _nava_thaara = {}
    for planet_id,(_h,_long) in pp:
        p_long = _h * 30 + _long
        _nava_thaara[planet_id] = drik._nava_thaara_from_planet_longitude(p_long)
    return _nava_thaara
    
def special_thaara_for_all_planets(planet_positions):
    pp = planet_positions[:const._pp_count_upto_ketu]
    _nava_thaara = {}
    for planet,(_h,_long) in pp:
        p_long = _h * 30 + _long
        _nava_thaara[planet] = drik._special_thaara_from_planet_longitude(planet,p_long)
    return _nava_thaara

def nava_thaara_for_chart_element(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
    ):
    planet_longitude = get_chart_element_longitude(jd, place, divisional_chart_factor, chart_method, 
                                                   star_position_from_moon, dhasa_starting_planet)
    return drik._nava_thaara_from_planet_longitude(planet_longitude)

def special_thaara_for_chart_element(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
    ):
    planet_longitude = get_chart_element_longitude(jd, place, divisional_chart_factor, chart_method, 
                                                   star_position_from_moon, dhasa_starting_planet)
    return drik._special_thaara_from_planet_longitude(dhasa_starting_planet,planet_longitude)

def chara_karakas(planet_positions, chara_karaka_method=None):
    """
    Get chara karakas for a dasa varga chart.
    
    @param planet_positions: list of [planet_id, (zodiac, longitude_in_rasi)]
    @param chara_karaka_method: const.CHARA_KARAKA_METHOD value or None
    @return: A dictionary mapping Planet ID -> List of Karaka Names from const.chara_karaka_names
    """
    # Handle default assignment if None is explicitly passed
    if chara_karaka_method is None: chara_karaka_method = const.chara_karaka_default_method
    # Create a quick mapping of planet_id -> longitude_in_rasi
    pos_map = {row[0]: row[-1][1] for row in planet_positions}
    one_rasi = 30.0  # 360.0 / 12 degrees
    
    # Pre-sort the core 7 planets (Sun to Saturn)
    pp_7 = [[p_id, pos_map[p_id]] for p_id in const.SUN_TO_SATURN if p_id in pos_map]
    pp_7_sorted = sorted(pp_7, key=lambda x: x[1], reverse=True)
    p_ids_7 = [p[0] for p in pp_7_sorted]
    
    p_ids = []

    # =========================================================================
    # METHOD 1: EIGHT_KARAKA_PARASHARI
    # =========================================================================
    if chara_karaka_method == const.CHARA_KARAKA_METHOD.EIGHT_KARAKA_PARASHARI:
        pp_8 = list(pp_7)
        if const.RAHU_ID in pos_map:
            pp_8.append([const.RAHU_ID, one_rasi - pos_map[const.RAHU_ID]])
        pp_8_sorted = sorted(pp_8, key=lambda x: x[1], reverse=True)
        p_ids = [p[0] for p in pp_8_sorted]

    # =========================================================================
    # METHOD 2: SEVEN_KARAKA_KNRAO_NOPiK
    # =========================================================================
    elif chara_karaka_method == const.CHARA_KARAKA_METHOD.SEVEN_KARAKA_KNRAO_NOPiK:
        p_ids = p_ids_7[:4] + [None] + p_ids_7[4:]

    # =========================================================================
    # METHOD 3: SEVEN_KARAKA_PK_MERGED_WITH_MK
    # =========================================================================
    elif chara_karaka_method == const.CHARA_KARAKA_METHOD.SEVEN_KARAKA_PK_MERGED_WITH_MK:
        p_ids = p_ids_7[:5] + [p_ids_7[3]] + p_ids_7[5:]

    # =========================================================================
    # METHOD 4: MIXED_SEVEN_EIGHT_KARAKA_PARASHARA
    # =========================================================================
    elif chara_karaka_method == const.CHARA_KARAKA_METHOD.MIXED_SEVEN_EIGHT_KARAKA_PARASHARA:
        degrees = [int(pos_map[p_id]) for p_id in const.SUN_TO_SATURN if p_id in pos_map]
        has_degree_tie = len(degrees) != len(set(degrees))
        
        if has_degree_tie:
            # Fallback to Method 1 logic
            pp_8 = list(pp_7)
            if const.RAHU_ID in pos_map:
                pp_8.append([const.RAHU_ID, one_rasi - pos_map[const.RAHU_ID]])
            pp_8_sorted = sorted(pp_8, key=lambda x: x[1], reverse=True)
            p_ids = [p[0] for p in pp_8_sorted]
        else:
            # Fallback to Method 3 logic
            p_ids = p_ids_7[:5] + [p_ids_7[3]] + p_ids_7[5:]

    # =========================================================================
    # BUILD OPTION 2 RETURN MAP: Planet ID -> [List of Karaka Names]
    # =========================================================================
    planet_to_karakas = defaultdict(list)
    
    for karaka_name, p_id in zip(const.chara_karaka_names, p_ids):
        if p_id is not None:
            planet_to_karakas[p_id].append(karaka_name)
            
    return dict(planet_to_karakas)
def chart_element_rasi_positions(
        jd,
        place,
        star_position_from_moon=1,
    ):
    """
    Get D1/Rasi source positions for all chart elements.

    Returns:
        [[element_id, [rasi, longitude_in_rasi]], ...]

    This function intentionally calls get_chart_element_longitude()
    with divisional_chart_factor=1 only.

    Then divisional_chart() can transform these D1 positions into D2/D3/etc.
    using existing hora_chart(), drekkana_chart(), etc.
    """

    main_planet_list = (
        list(utils._main_planets.keys())[:const._pp_count_upto_pluto - 1]
        if const._INCLUDE_URANUS_TO_PLUTO
        else list(utils._main_planets.keys())[:const._pp_count_upto_ketu - 1]
    )

    element_list = (
        list(utils._ascendant.keys())
        + main_planet_list
        + list(utils._drik_upagrahas.keys())
        + list(utils._chart_upagrahas.keys())
        + list(utils._special_lagnas.keys())
        + list(utils._varnada_lagnas.keys())
        + list(utils._sphutas.keys())
        + list(utils._arudha_lagnas.keys())
        + list(utils._sahams.keys())
    )

    seen = set()
    clean_element_list = []
    for element in element_list:
        if element not in seen:
            clean_element_list.append(element)
            seen.add(element)

    pp_rasi = []

    for element in clean_element_list:
        abs_long = get_chart_element_longitude(
            jd,
            place,
            divisional_chart_factor=1,
            chart_method=1,
            star_position_from_moon=star_position_from_moon,
            dhasa_starting_planet=element,
        )

        rasi, longitude_in_rasi = drik.dasavarga_from_long(
            abs_long,
            divisional_chart_factor=1
        )

        pp_rasi.append([element, [rasi, longitude_in_rasi]])

    return pp_rasi
def saham_longitudes(dob,tob,place,divisional_chart_factor=1,chart_method=1,
                             base_rasi=None,count_from_end_of_sign=None,dhasa_progression_correction=0.0):
    from jhora.horoscope.transit import saham
    jd_at_dob = utils.julian_day_number(dob, tob)
    spl_rasi_positions = []
    for sp,sp_func in utils._sahams.items():
        func = getattr(saham, sp_func+'_saham', None)
        if not callable(func):
            raise AttributeError(f"'jhora.horoscope.transit' has no callable '{sp_func}'")
        vl = func(
            jd_at_dob,
            place,
            dhasa_progression_correction=dhasa_progression_correction,
        )
        v = drik.dasavarga_from_long(vl)
        spl_rasi_positions.append([sp,[v[0],v[1]]])
    return divisional_positions_from_rasi_positions(spl_rasi_positions, divisional_chart_factor, chart_method, base_rasi, 
                                              count_from_end_of_sign)
def saham_longitudes_mixed_chart(dob,tob,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                          dhasa_progression_correction=0.0):
    from jhora.horoscope.transit import saham
    jd_at_dob = utils.julian_day_number(dob, tob)
    spl_rasi_positions = []
    for sp,sp_func in utils._sahams.items():
        func = getattr(saham, sp_func+'_saham', None)
        if not callable(func):
            raise AttributeError(f"'jhora.horoscope.transit' has no callable '{sp_func}'")
        vl = func(
            jd_at_dob,
            place,
            dhasa_progression_correction=dhasa_progression_correction,
        )
        v = drik.dasavarga_from_long(vl)
        spl_rasi_positions.append([sp,[v[0],v[1]]])
    return mixed_chart_from_rasi_positions(planet_positions_in_rasi=spl_rasi_positions, varga_factor_1=varga_factor_1,
                                           chart_method_1=chart_method_1, varga_factor_2=varga_factor_2,
                                           chart_method_2=chart_method_2)
def _d2_ruler_index(sign, l):
    # Odd signs (0, 2, 4, 6, 8, 10): 1st half (l=0) -> 1, 2nd half (l=1) -> 2
    # Even signs (1, 3, 5, 7, 9, 11): 1st half (l=0) -> 2, 2nd half (l=1) -> 1
    if sign in const.odd_signs:
        return l + 1
    else:
        return 2 - l

def _d3_ruler_index(sign, l):
    # Jagannatha Drekkana Logic
    if sign in const.movable_signs: return (l % 3) + 1
    if sign in const.fixed_signs:   return ((l + 1) % 3) + 1
    return ((l + 2) % 3) + 1        # Dual

def _d4_ruler_index(sign, l):
    return l + 1

def _d7_ruler_index(sign, l):
    return (l + 1) if sign in const.odd_signs else (7 - l)
def _d9_ruler_index(sign, long):
    navamsa_index = int(long // (30.0 / 9.0))
    if navamsa_index >= 9:
        navamsa_index = 8
    ruler = (navamsa_index + (sign % 3)) % 3 + 1
    return ruler
def _d10_ruler_index(sign, l):
    if sign in const.odd_signs: 
        return l + 1
    return 10 - l
def _d12_ruler_index(sign, l):
    return l + 1

def _d16_ruler_index(sign, l):
    # Forward for odd, reverse for even
    return (l + 1) if sign in const.odd_signs else (16 - l)

def _d20_ruler_index(sign, l):
    return l + 1

def _d24_ruler_index(sign, l):
    return (l + 1) if sign in const.odd_signs else (24 - l)

def _d27_ruler_index(sign, l):
    return l + 1

def _d30_ruler_index(sign, longitude):
    # D30 uses custom segments based on Odd/Even parity
    if sign in const.odd_signs:
        if longitude < 5: return 1
        if longitude < 10: return 2
        if longitude < 18: return 3
        if longitude < 25: return 4
        return 5
    else:
        if longitude < 5: return 5
        if longitude < 12: return 4
        if longitude < 20: return 3
        if longitude < 25: return 2
        return 1

def _d40_ruler_index(sign, l):
    return (l % 12) + 1
def _d45_ruler_index(sign_index, l):
    nature = sign_index % 3
    if sign_index not in const.even_signs:
        return ((l + nature) % 3) + 1
    else:
        return ((nature + 2 - l) % 3) + 1
def _d60_ruler_index(sign, l):
    return (l + 1) if sign in const.odd_signs else (60 - l)

def _d150_ruler_index(rasi_sign, longitude):
    use_non_uniform = const.d150_chart_method_default == const.D150_CHART_METHOD.DEVA_KERALAM_CHANDRA_KALA_NADI_NON_UNIFORM
    if use_non_uniform:
        raw_idx, _ = _non_uniform_d150_index_and_longitude(longitude)
    else:
        raw_idx, _ = _uniform_d150_index_and_longitude(longitude)

    # 2. Map the 0-149 index to the 1-150 Nadi Amsa Ruler ID
    # sign_type: 0 = Movable (Chara), 1 = Fixed (Sthira), 2 = Dual (Dvisvabhava)
    sign_type = rasi_sign % 3

    if rasi_sign in const.movable_signs: # sign_type == 0:
        # Movable signs: Sequence is 1 to 150
        return raw_idx + 1
        
    elif rasi_sign in const.fixed_signs: # sign_type == 1:
        # Fixed signs: Sequence is 150 down to 1
        return 150 - raw_idx
        
    else:
        # Dual signs: Sequence is 76-150, then 1-75
        if raw_idx < 75:
            return raw_idx + 76
        else:
            return raw_idx - 74

def amsa_rulers(planet_positions_in_rasi, dcf):
    """
    planet_positions_in_rasi: List of [planet_id, [sign_index (0-11), longitude]]
    dcf: Divisional Chart Factor
    """
    helpers = {
        v: globals()[f"_d{v}_ruler_index"]
        for v in const.amsa_supported_vargas
    }
    longitude_vargas = [9, 30, 150]
    
    amsa_rulers = {}
    f1 = 30.0 / dcf 
    
    for planet_id, [sign, longitude] in planet_positions_in_rasi:
        # Calculate 0-based division index 'l'
        l = min(int(longitude // f1), dcf - 1) 
        
        if dcf in longitude_vargas:
            amsa_rulers[planet_id] = helpers[dcf](sign, longitude)
        elif dcf in helpers:
            amsa_rulers[planet_id] = helpers[dcf](sign, l)
        else:
            # Fallback for unexpected DCFs
            amsa_rulers[planet_id] = l + 1
    return amsa_rulers
        
if __name__ == "__main__":
    lang = 'en'
    _ayanamsa = "TRUE_PUSHYA"
    drik.set_ayanamsa_mode(_ayanamsa)
    utils.set_language(lang)
    drik.set_planet_list(set_rahu_ketu_as_true_nodes=True, include_western_planets=True)
    #from jhora.tests import pvr_tests
    #pvr_tests.amsa_deity_tests()
    #exit()
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.03862,80.261818,5.5)
    jd = utils.julian_day_number(dob, tob); dcf = 3
    dcf_1 = 9; dcf_2 = 12 ; vm = 1; cm = 1; cm1 = 1; cm2 = 1
    pp_rasi = divisional_chart(jd,place,divisional_chart_factor=1,exclude_non_planets=True)
    chart_1d = utils.get_house_planet_list_from_planet_positions(pp_rasi)
    print(chart_1d)
    chart_data_2d = utils._convert_1d_house_data_to_2d(chart_1d,'south_indian')
    chart_1d_south_irregular = [row[::-1] for row in chart_data_2d]
    print(chart_1d_south_irregular)
    exit()
    pp_div = divisional_chart(jd,place,divisional_chart_factor=dcf,exclude_non_planets=False)
    pl = amsa_rulers(pp_rasi, dcf)
    _amsa_res = get_amsa_resources(lang)
    for pi,(k,v) in enumerate(pl.items()):
        p_long = pp_rasi[pi][1][0]*30 + pp_rasi[pi][1][1]
        p_div_long = pp_div[pi][1][0]*30 + pp_div[pi][1][1]
        print("D-"+str(dcf),"Rasi Long:",utils.deg_to_sign_str(p_long),"Varga Long:",utils.deg_to_sign_str(p_div_long),
              k,v,_amsa_res[str(dcf)][v-1])
    exit()
    """
    #spls = varnada_lagna_longitudes(dob, tob, place, divisional_chart_factor=dcf, chart_method=cm, varnada_method=vm)
    #spls = varnada_lagna_longitudes_mixed_chart(dob, tob, place, varga_factor_1=dcf_1, chart_method_1=cm1,
    #                                 varga_factor_2=dcf_2, chart_method_2=cm2, varnada_method=vm)
    spls = arudha_lagna_longitudes(dob, tob, place)
    dcf_str = "D-"+str(dcf)
    for sp,(h,long) in spls:
        print(dcf_str,sp,utils.deg_to_sign_str(h*30+long))
    exit()
    from jhora.tests import pvr_tests
    drik.set_ayanamsa_mode("LAHIRI")
    pvr_tests.saham_new_tests()
    exit()
    spls = saham_longitudes_mixed_chart(dob, tob, place, varga_factor_1=dcf_1,chart_method_1=cm1,
                                        varga_factor_2=dcf_2,chart_method_2=cm2)
    dcf_str = "D-"+str(dcf_1)+" X D-"+str(dcf_2)
    for sp,(h,long) in spls:
        print(dcf_str,sp,utils.resource_strings[utils._sahams[sp]+'_saham_str']+utils.resource_strings['saham_str']
              ,utils.deg_to_sign_str(h*30+long))
    exit()
    """
    """
    dcf_str = "D-"+str(dcf)
    spls = divisional_chart(jd, place, divisional_chart_factor=dcf, exclude_non_planets=True,
                            chart_method=const.D150_CHART_METHOD.PVR_JHORA_METHOD_OWN_SIGN_UNIFORM_DIRECT)
    chart_1d = utils.get_house_planet_list_from_planet_positions(spls[:const._pp_count_upto_ketu])
    print(chart_1d)
    pp_rasi = rasi_chart(jd,place)
    print('rasi positions',pp_rasi)
    for sp,(h,long) in spls:
        print(dcf_str,sp,utils.deg_to_sign_str(h*30+long))
    exit()
    """
    #"""
    from jhora.tests import pvr_tests
    pvr_tests.chart_element_longitude_d150_test()
    #pvr_tests.chart_element_longitude_custom_d57_non_cyclic_tests()
    #pvr_tests.chart_element_longitude_d2_tests()
    #pvr_tests.chart_element_longitude_d9_tests()
    exit()
    #"""
    for ckm in const.CHARA_KARAKA_METHOD:
        c_karakas = chara_karakas(pp, ckm)
        print("=========================")
        print(f"Method = {ckm}")
        print("=========================")
        for p,(h,long) in pp:
            p_str = utils.resource_strings['ascendant_str'] if p == const._ascendant_symbol else utils.PLANET_NAMES[p]
            p_long_str = utils.deg_to_sign_str(h*30+long)
            if p in c_karakas:
                k_str = [utils.resource_strings[f"{k}_str"] for k in c_karakas[p]]
                k_str = '/'.join(k_str)
            else:
                k_str = ''
            print(p_str, ':', p_long_str+' '+k_str)
    exit()
