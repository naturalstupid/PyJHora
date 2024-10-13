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
import itertools
from jhora import const,utils
from jhora.horoscope.chart import house
from jhora.horoscope.transit import tajaka
""" Tajaka Yogas """
def ishkavala_yoga(planet_to_house_dict):
    """
         Ishkavala Yoga
            If planets occupy only kendras (1st, 4th, 7th and 10th houses) and panapharas (2nd, 5th,
            8th and 11th houses) and if apoklimas (3rd, 6th, 9th and 12th houses) are empty, then
            this yoga is present. This yoga gives wealth, happiness and good fortune.
        @param planet_to_house_dict: Example {0:1.1:2,2:0,..'L':1}
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether ishkaval yoga is present or not  
    """
    """ TODO Not Working """
    asc_house = planet_to_house_dict[const._ascendant_symbol]
    slq = list(set([(asc_house+h-1)%12 for h in [1,2,4,5,7,8,10,11]]))
    sph = list(set([house.get_relative_house_of_planet(asc_house,h)-1 for h in list(planet_to_house_dict.values())[:-1]]))
    yoga_present = all(el in slq for el in sph)
    return yoga_present
def induvara_yoga(planet_to_house_dict):
    """
        Induvara Yoga
            If planets occupy only apoklimas (3rd, 6th, 9th and 12th houses) and if kendras (1st, 4th,
            7th and 10th houses) and panapharas (2nd, 5th, 8th and 11th houses) are empty, then this
            yoga is present. This yoga gives disappointments, worries and illnesses.    
        @param planet_to_house_dict: Example {0:1.1:2,2:0,..'L':1}
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether induvara yoga is present or not  
    """
    asc_house = planet_to_house_dict[const._ascendant_symbol]
    slq = list(set([(asc_house+h-1)%12 for h in [3,6,9,12]]))
    sph = list(set([house.get_relative_house_of_planet(asc_house,h)-1 for h in list(planet_to_house_dict.values())[:-1]]))
    yoga_present = all(el in slq for el in sph)
    #print('sph',sph,'slq',slq)
    return yoga_present
def ithasala_yoga(planet_positions,planet1,planet2):
    """
        Ithasala Yoga
            If two planets have an aspect and if the faster moving planet83 is less advanced in its
            rasi than the slower moving planet, then we have an ithasala yoga between the two.        
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether yoga is present or not  
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print(house_planet_dict)
    chk1 = tajaka.planets_have_aspects(house_planet_dict, planet1, planet2)
    chk2,ithasala_type = tajaka.both_planets_within_their_deeptamsa(planet_positions,planet1, planet2)
    chk3 = tajaka.both_planets_approaching(planet_positions,planet1,planet2)
    yoga_present = chk1 and chk2 and chk3
    return yoga_present, ithasala_type
def eesarpha_yoga(planet_positions,planet1,planet2):
    """
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether yoga is present or not  
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print(house_planet_dict)
    chk1 = tajaka.planets_have_aspects(house_planet_dict, planet1, planet2)
    chk2,ithasala_type = tajaka.both_planets_within_their_deeptamsa(planet_positions,planet1, planet2)
    chk3 = tajaka.both_planets_approaching(planet_positions,planet1,planet2)
    yoga_present = chk1 and chk2 and (not chk3)
    return yoga_present
def _check_nakta_yoga_1(planet_positions,planet1,planet2):
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    excluded_planets = [const._ascendant_symbol,'7','8']
    yp = str(planet1) not in excluded_planets and str(planet2) not in excluded_planets
    yp = yp and not ithasala_yoga(planet_positions,int(planet1),int(planet2))[0]
    yp = yp and not eesarpha_yoga(planet_positions, int(planet1), int(planet2))
    yp = yp and int(planet1) not in tajaka.aspects_of_the_planet(house_planet_dict,int(planet2))
    return yp
def _check_nakta_yoga(planet_positions, planet, p1, p2):
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    yp1 = _check_nakta_yoga_1(planet_positions, p1, p2)
    if not yp1:
        return False
    yp2 = ithasala_yoga(planet_positions, int(planet), int(p1))[0]
    yp3 = ithasala_yoga(planet_positions, int(planet), int(p2))[0]
    yp = yp1 and yp2 and yp3
    #print('_check_nakta_yoga_1(planet_positions, p1, p2)',planet,p1,p2,yp1,yp2,yp3,yp)
    """
    if not yp:
        return False
    yp = yp and str(p2) in tajaka.benefic_aspects_of_the_planet(house_planet_dict, planet)
    if not yp:
        return False
    yp = yp and const.order_of_planets_by_speed.index(planet) > const.order_of_planets_by_speed.index(int(p1)) and \
            const.order_of_planets_by_speed.index(planet) > const.order_of_planets_by_speed.index(int(p2))
    if yp:
        p_long = planet_positions[planet+1][1][1]
        p1_long = planet_positions[int(p1)+1][1][1]
        p2_long = planet_positions[int(p2)+1][1][1]
        yp = yp and p_long < p1_long and p_long < p2_long
    """
    return yp
def _get_nakta_triples(ithasala_pairs):
    from collections import defaultdict
    iy_list = defaultdict(list)
    [iy_list[k].append(v) for k,v,_ in ithasala_pairs]
    iy_list = [(k,list(itertools.combinations(lst,2))) for k,lst in iy_list.items() if len(lst)>1]
    print('_get_nakta_triples iy_list',iy_list)
    iy_list1 = defaultdict(list)
    [iy_list1[v].append(k) for k,v,_ in ithasala_pairs]
    iy_list1 = [(k,list(itertools.combinations(lst,2))) for k,lst in iy_list1.items() if len(lst)>1]
    print('_get_nakta_triples iylist1',iy_list1)
    iy_list += iy_list1
    print('_get_nakta_triples iy_list',iy_list)
    _nakta_triples = iy_list # utils.flatten_list(iy_list)
    return _nakta_triples
def get_nakta_yoga_planet_triples(planet_positions):
    """
        nakta yoga between p2 and p3 if 
             p1 & p2 and p1 & p3 have ithasala yoga between them 
             but p2 and p3 have no aspects
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of natka yoga triples
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    iy_pairs = get_ithasala_yoga_planet_pairs(planet_positions)
    #print('ithasala_yoga_planet_pairs',iy_pairs)
    _nakta_triples = _get_nakta_triples(iy_pairs)
    #print(_nakta_triples)
    nt = []
    for planet,p_list in _nakta_triples:
        p_long = planet_positions[planet+1][1][1]
        for p1,p2 in p_list:
            p1_long = planet_positions[p1+1][1][1]
            p2_long = planet_positions[p2+1][1][1]
            #print('checking triples',planet,p_long,p1,p1_long,p2,p2,p_long)
            if not tajaka.planets_have_aspects(house_planet_dict, p1, p2) and \
                    p_long < p1_long and p_long < p2_long:
                nt.append([planet,(p1,p2)])
                #print('found natka triple',planet,p1,p2)
    _nakta_triples = utils.flatten_list(nt)
    #print('natka planet triples',_nakta_triples)
    return _nakta_triples
def check_yamaya_yoga(planet,planet1,planet2,planet_positions):
    planet_house_dict = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    #print(planet_house_dict)
    house_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print(house_planet_list)
    # Step-1: check planet1 and planet2 have no aspects
    chk1 = not tajaka.planets_have_aspects(house_planet_list, planet1, planet2)
    if not chk1:
        return False
    #Step-2: Check planet has aspect with planet1 and planet 2
    chk2_1 = tajaka.planets_have_aspects(house_planet_list,planet,planet1)
    chk2_2 = tajaka.planets_have_aspects(house_planet_list,planet,planet2)
    chk2 = chk2_1 and chk2_2 
    if not chk2:
        return False
    #Step-3: Planet forms ithasala pair with planet1 and planet2
    chk3_1 = ithasala_yoga(planet_positions,planet,planet1)
    chk3_2 = ithasala_yoga(planet_positions,planet,planet2)
    chk3 = chk3_1 and chk3_2
    if not chk3:
        return False
    # Step-4: check if planet has higher longitude than planet1/planet2
    p_long = planet_positions[planet+1][1][1]
    p1_long = planet_positions[planet1+1][1][1]
    p2_long = planet_positions[planet2+1][1][1]
    chk4 = p_long > p1_long and p_long > p2_long
    #print(p_long,p1_long,p2_long,chk3)
    return chk4
def get_yamaya_yoga_planet_triples(planet_positions):
    """
        yamaya yoga between p2 and p3 if 
             p1 & p2 and p1 & p3 have ithasala yoga between them 
             but p2 and p3 have no aspects
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of yamaya yoga triples
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    iy_pairs = get_ithasala_yoga_planet_pairs(planet_positions)
    print('ithasala_yoga_planet_pairs',iy_pairs)
    _yamaya_triples = _get_nakta_triples(iy_pairs)
    print('_yamaya_triples',_yamaya_triples)
    nt = []
    for planet,p_list in _yamaya_triples:
        p_long = planet_positions[planet+1][1][1]
        for p1,p2 in p_list:
            p1_long = planet_positions[p1+1][1][1]
            p2_long = planet_positions[p2+1][1][1]
            print('checking triples',planet,p_long,p1,p1_long,p2,p2,p_long)
            if not tajaka.planets_have_aspects(house_planet_dict, p1, p2) and \
                    p_long > p1_long and p_long > p2_long:
                nt.append([planet,(p1,p2)])
                #print('found yamaya triple',planet,p1,p2)
    _yamaya_triples = utils.flatten_list(nt)
    print('yamaya planet triples',_yamaya_triples)
    return _yamaya_triples
def get_eesarpha_yoga_planet_pairs(planet_positions):
    """
        Get eeasrpha yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of eesarpha yoga pairs        
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    com1=[]
    for p1,p2 in list(itertools.combinations([*range(7)],2)):
        iy = eesarpha_yoga(planet_positions, p1, p2)
        if iy:
           com1.append((p1,p2))
    return com1 
def get_ithasala_yoga_planet_pairs(planet_positions):
    """
        Get ithasala yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of ithasala yoga pairs        
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    print('house_planet_dict',house_planet_dict)
    com1=[]
    for p1,p2 in list(itertools.combinations([*range(7)],2)):
        iy,iyt = ithasala_yoga(planet_positions, p1, p2)
        if iy:
           com1.append((p1,p2,iyt))
    return com1 
def get_manahoo_yoga_planet_pairs(planet_positions):
    """
        Get manahoo yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of manahoo yoga pairs        
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    iy_pairs = get_ithasala_yoga_planet_pairs(planet_positions)
    my = []
    mars_or_saturn_houses = [planet_positions[3+1][1][0],planet_positions[6+1][1][0]]
    for p1,p2,_ in iy_pairs: # ithasala tuple is p1,p2,othasal_type
        p1_long = planet_positions[p1+1][1][1]
        p2_long = planet_positions[p2+1][1][1]
        faster_planet = p1
        faster_planet_long = p1_long
        if p2_long < p1_long:
            faster_planet = p2
            faster_planet_long = p2_long
        faster_planet_house = planet_positions[faster_planet+1][1][0]
        faster_planet_deeptaamsa_start,faster_planet_deeptaamsa_end = utils.deeptaamsa_range_of_planet(faster_planet, faster_planet_long)
        if faster_planet_house in mars_or_saturn_houses:
            m_s_index = mars_or_saturn_houses.index(faster_planet_house)
            m_s_long = planet_positions[m_s_index+1][1][1]
            if m_s_long > faster_planet_deeptaamsa_start and m_s_long < faster_planet_deeptaamsa_end:
                my.append([p1,p2,mars_or_saturn_houses[m_s_index]])
    return my
def get_kamboola_yoga_planet_pairs(planet_positions):
    """
        Get kamboola yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of kamboola yoga pairs        
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    iy_pairs = get_ithasala_yoga_planet_pairs(planet_positions)
    iy_pairs = [(x,y) for x,y,_ in iy_pairs]
    #print(iy_pairs)
    ky_pairs = [ (x,y) for x,y in iy_pairs if x==1 or x==1]
    ky_planets = [ y for x,y in iy_pairs if x==1]+[ x for x,y in iy_pairs if y==1]    
    #print(ky_pairs, ky_planets)
    iy_ky_pairs = [(x,y) for kyp in ky_planets for x,y in iy_pairs if kyp==x or kyp==y]
    ky_check =any([kyp == x or kyp ==y for kyp in ky_planets for x,y in iy_pairs])
    return (ky_check,ky_pairs,iy_ky_pairs)
def get_gairi_kamboola_yoga_planet_pairs(planet_positions):
    """ TODO: to be implemented """
    return None
def get_khallasara_yoga_planet_pairs(planet_positions):
    """ TODO: to be implemented """
    return None
def get_radda_yoga_planet_pairs(planet_positions):
    """
        Get radda yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of radda yoga pairs        
    """
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    iy_pairs = get_ithasala_yoga_planet_pairs(planet_positions)
    iy_pairs = [(x,y) for x,y,_ in iy_pairs]
    chk = []
    chk.append([x in charts.planets_in_combustion(planet_positions) or y in charts.planets_in_combustion(planet_positions) for x,y in iy_pairs])
    chk.append([x in charts.planets_in_retrograde(planet_positions) or y in charts.planets_in_retrograde(planet_positions) for x,y in iy_pairs])
    chk.append([const.house_strengths_of_planets[x][p_to_h[x]] < const._NEUTRAL_SAMAM or const.house_strengths_of_planets[y][p_to_h[y]]<2 for x,y in iy_pairs])
    import numpy as np
    ry_check= list(np.any(chk,axis=0))
    ry_pairs = [(x,y) for i,(x,y) in enumerate(iy_pairs) if ry_check[i]]
    return ry_pairs
def get_duhphali_kutta_yoga_planet_pairs(jd,place):
    """
        Get duhphali kutta yoga planet pairs
        @param jd: Julian Day Number
        @param place: drik.Place struct ('place name',latitude, longitude, timezone) 
        @return: List of duhphali kutta yoga pairs        
    """
    planet_positions = charts.divisional_chart(jd, place)
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    print('house planet chart',house_planet_dict)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    iy_pairs = get_ithasala_yoga_planet_pairs(planet_positions)
    iy_pairs = [(x,y) for x,y,_ in iy_pairs]
    dky_pairs = []
    for x,y in iy_pairs:
        faster_planet = x
        slower_planet = y
        if const.order_of_planets_by_speed.index(x) < const.order_of_planets_by_speed.index(y):
            faster_planet = y
            slower_planet = x
        print('ithasala pair',faster_planet,slower_planet)
        chk = const.house_strengths_of_planets[faster_planet][p_to_h[faster_planet]] > const._FRIEND
        print('chk1',chk,const.house_strengths_of_planets[faster_planet][p_to_h[faster_planet]])
        if not chk:
            continue
        from jhora.horoscope.chart import strength
        pvb = strength.pancha_vargeeya_bala(jd, place)
        print('pvb',pvb[faster_planet],pvb[slower_planet])
        chk = chk & (pvb[faster_planet]  > const.pancha_vargeeya_bala_strength_threshold)
        print('chk2',chk)
        if not chk:
            continue
        chk = chk & (const.house_strengths_of_planets[slower_planet][p_to_h[slower_planet]] < const._EXALTED_UCCHAM)
        print('chk3',chk)
        if not chk:
            continue
        chk = chk & (pvb[slower_planet]  < const.pancha_vargeeya_bala_strength_threshold)
        print('chk3',chk)
        if not chk:
            continue
        else:
            dky_pairs.append((x,y))
    print('duhphali_kutta_yoga_planet_pairs',dky_pairs)
    return dky_pairs
def nakta_yoga(planet_positions,planet):
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print(house_planet_dict)
    ah,ap = tajaka.aspects_of_the_planet(house_planet_dict, planet)
    com = list(itertools.combinations(ap,2))
    com1 = []
    for p1,p2 in com:
        if _check_nakta_yoga(planet_positions, planet, p1, p2):
            com1.append((int(p1),int(p2)))
    com = com1[:]
    #print(planet,'combinations',com)
    yoga_present = len(com)>0
    return yoga_present,com
"""
    Ithasala yoga
        If two planets have an aspect and if the faster moving planet83 is less advanced in its
        rasi than the slower moving planet, then we have an ithasala yoga between the two.
"""
if __name__ == "__main__":
    pp = [['L',(1,5)],[0,(0,25)],[1,(0,20)],[2,(7,15)],[3,(0,23)],[4,(3,16)],[5,(2,13)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
    planet1 = 2
    planet2 = 5
    planet3 = 4
    planet_house_dict = utils.get_planet_house_dictionary_from_planet_positions(pp)
    print(check_yamaya_yoga(planet3, planet1, planet2, pp))
    exit()
    from jhora.panchanga import drik
    from jhora.horoscope.chart import charts
    jd_at_years = utils.julian_day_number((1993,6,1),(13,30,4))
    place = drik.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    chart_67_rasi = charts.divisional_chart(jd_at_years, place, divisional_chart_factor=1)
    com = get_ithasala_yoga_planet_pairs(chart_67_rasi)
    print('ithasala combinations\n',com)
    com = get_eesarpha_yoga_planet_pairs(chart_67_rasi)
    print('eesarpha_yoga combinations\n',com)
    exit()
    chart_66 = ['0','','3','7','','4','8','','6','5/L','','2/1']
    chart_66 = ['3','4','','5','7','','8','6/2','','L/0','1','']
    print(chart_66)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    print('asc_house',asc_house)
    print(ishkavala_yoga(p_to_h,asc_house))
    exit()
    from jhora.panchanga import drik
    from jhora.horoscope.chart import charts
    jd_at_dob = utils.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = drik.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    jd_at_years = utils.julian_day_number((1993,6,1),(13,30,4))
    dky = get_duhphali_kutta_yoga_planet_pairs(jd_at_years,place)
    exit()
    chart_67_rasi = charts.divisional_chart(jd_at_years, place, ayanamsa_mode, divisional_chart_factor=1)
    print(chart_67_rasi)
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(chart_67_rasi)
    print(house_planet_dict)
    ry = get_radda_yoga_planet_pairs(chart_67_rasi)
    print(ry)
    exit()
    ky = get_kamboola_yoga_planet_pairs(chart_67_rasi)
    print('get_kamboola_yoga_planet_pairs',ky)
    exit()
    get_nakta_yoga_planet_triples(chart_67_rasi)
    get_yamaya_yoga_planet_triples(chart_67_rasi)
    com = get_manahoo_yoga_planet_pairs(chart_67_rasi)
    print('manahoo combinations\n',com)
    exit()
    com = get_eesarpha_yoga_planet_pairs(chart_67_rasi)
    print('eesarpha combinations\n',com)
    exit()
    com = []
    for planet in range(7):
        ty = nakta_yoga(chart_67_rasi,planet)
        if ty[0] and len(ty[1])>0:
            com.append([planet,ty[1]])
        print('nakta yoga',ty)
    print('nakta yoga',com)
    exit()
    chart_66 = ['0','','3','7','','4','8','','6','5/L','','2/1']
    print(chart_66)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    print('asc_house',asc_house)
    print(ishkavala_yoga(p_to_h,asc_house))
    chart_66 = ['','','3/0/5','','','4/7/8','','','6','L','','2/1']
    print(chart_66)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    print('asc_house',asc_house)
    print(induvara_yoga(p_to_h,asc_house))