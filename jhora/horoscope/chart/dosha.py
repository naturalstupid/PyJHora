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
import json
from jhora.horoscope.chart import charts, house
from jhora import utils, const
from jhora.panchanga import drik
_lang_path = const._LANGUAGE_PATH

def get_dosha_resources(language='en'):
    """
        get yoga names from yoga_msgs_<lang>.txt
        @param language: Two letter language code. en, hi, ka, ta, te
        @return json strings from the resource file as dictionary 
    """
    json_file = _lang_path + const._DEFAULT_DOSHA_JSON_FILE_PREFIX+language+'.json'
    f = open(json_file,"r",encoding="utf-8")
    msgs = json.load(f)
    return msgs
def kala_sarpa(house_to_planet_list):
    """ Returns kala Sarpa Dosha True or False 
        If True type kala sarpa dosha can be obtained from the Rahu's house number (1..12)
        as the index of the array from dosha_msgs_<lang> file
    """
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    rahu_house = p_to_h[7]
    kpdc1 = all([any([p_to_h[ph]==(rahu_house+rkh)%12 for rkh in [*range(7)]]) for ph in [*range(7)]])
    ketu_house = p_to_h[8]
    kpdc2 = all([any([p_to_h[ph]==(ketu_house+rkh)%12 for rkh in [*range(7)]]) for ph in [*range(7)]])
    #print('rahu_house',rahu_house,'ketu_house',ketu_house)
    return kpdc1 or kpdc2
def manglik(planet_positions,manglik_reference_planet='L',include_lagna_house=False,
            include_2nd_house=True,apply_exceptions=True):
    """ Sanjay Rath (https://srath.com/jyoti%E1%B9%A3a/amateur/ma%E1%B9%85galika-do%E1%B9%A3a/)
        says lagna house not in ancient text. So default include_lagna_house set to False
        Similarly some astrolgers use reference planet as manglik_reference_planet=1 (moon) or 
        manglik_reference_planet=5 (venus) instead of lagna
        include_2nd_house => South India considers also 2nd house (Default = True)
        apply_exceptions => BV Raman has suggested exemptions for manglik rule. (Default - True)
        @return: [Manglik=True/False,Exceptions-True/False,[Exception Indices or -1]]
                Exception index = 0 => No Exceptions
                Exception index >1 => Exception indices can be mapped to dosha_msgs_<lang>.json file strings.
    """
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #house_to_planet_list = ['L','7','0/1','5/6','2','3','4','8','','','','']
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    manglik_houses = [4,7,8,12]
    if include_2nd_house:
        manglik_houses = [2]+manglik_houses
    if include_lagna_house:
        manglik_houses = [1]+manglik_houses
    from_house = p_to_h[manglik_reference_planet] ; mars_house = p_to_h[2]
    mars_house_from_ref = house.get_relative_house_of_planet(from_house,mars_house)
    _manglik = mars_house_from_ref in manglik_houses
    if apply_exceptions and _manglik:
        _me = _manglik_exceptions(planet_positions)
        return [_manglik,_me[0],_me[1]]
    else:
        return [_manglik,False,[]]
def _manglik_exceptions(planet_positions):
    """
        BV Raman Exceptions:
        1. Mars in Leo/Simmam or Aquarious (Kumbam)
        2. Mars in 2nd house and in signs of Gemini/Mithuna or Virgo/Kanni
        3. Mars in 4th house and in signs of Aries/Mesham or Scorpio/Vrichigam
        4. Mars in 7th house and in signs of Cancer/Kataka or Capricorn/Makaram
        5. Mars in 8th house and in signs of Sagitarius/Dhanusu or Pisces/Meenam
        6. Mars in 12th house and in signs of Taurus/Rishabam or Libra/Thulam
        7. Mars is in association or aspected by Jupiter or Saturn
        8. Retrograde Mars
        9. Mars is weak (combust, Rasi Sandhi etc)
        10. Mars is lagna lord.
        11. Dispositor of Mars is neecha or associated with strong benefic
        12. Mars in own house, exalted or in friend' house - reduced effects
        13. Mars in movable - reduced effects
        14. Dispositor of Mars is in Quad or Trine
        15. If Lagnam is in Cancer/Kataka or Leo, then Mars is yoga karaka causes no dosha.
        16. Since Mars cojoins with Jupiter or moon, it reduces the dosha
        17. When Jupiter or Venus is in Lagna it reduces dosha
    """
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    mars_house = p_to_h[2] ; lagna_house = p_to_h['L']; mars_long = planet_positions[3][1][1]
    mars_from_lagna = house.get_relative_house_of_planet(lagna_house,mars_house)
    _me = [] ; _me_details = []
    c1 = mars_house in [4,10] ; _me.append(c1)
    c2 = mars_from_lagna ==2 and mars_house in [2,5] ; _me.append(c2)
    c3 = mars_from_lagna ==4 and mars_house in [0,7] ; _me.append(c3)
    c4 = mars_from_lagna ==7 and mars_house in [3,9] ; _me.append(c4)
    c5 = mars_from_lagna ==8 and mars_house in [8,11] ; _me.append(c5)
    c6 = mars_from_lagna ==12 and mars_house in [1,6] ; _me.append(c6)
    c7 = len(house.associations_of_the_planet(planet_positions, 2))>0 ; _me.append(c7)
    c8 = 2 in charts.planets_in_retrograde(planet_positions) ; _me.append(c8)
    c9_1 = 2 in charts.planets_in_combustion(planet_positions)
    c9_2 = mars_long < const.rasi_sandhi_duration or mars_long > (30.0-const.rasi_sandhi_duration)
    c9 = c9_1 or c9_2 ; _me.append(c9)
    c10 = house.house_owner_from_planet_positions(planet_positions, lagna_house)==2; _me.append(c10)
    c11 = False ; _me.append(c11)
    c12 = const.house_strengths_of_planets[2][mars_house] >= const._FRIEND; _me.append(c12)
    c13 = mars_house in const.movable_signs; _me.append(c13)
    c14 = False ; _me.append(c14)
    c15 = lagna_house in [3,4] ; _me.append(c15)
    c16 = mars_house in [p_to_h[4], p_to_h[5]]; _me.append(c16)
    c17 = lagna_house in [p_to_h[4], p_to_h[5]]; _me.append(c17)
    _me_i = []
    have_exceptions = any(_me)
    if have_exceptions:
        _me_i = [i+1 for i,m in enumerate(_me) if m]
    return [have_exceptions,_me_i]
def pitru_dosha(planet_positions):
    """
        returns True/False if pitru/pitra dosha
        From timesofindia:
            Sun, moon or Rahu in 9th house
            Ketu in 4th house
            sun, moon, rahu or ketu afflicted by malefic planets like Mars or Saturn
            Venus, Mercury, Rahu or any of these two in 2nd, 5th, 9th or 12th    
        Sun or Moon is in conjunction with Rahu or Ketu
    """
    house_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    planet_house_dict = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    ninth_house = (planet_house_dict['L']+8)%12
    pd = []
    pd1 = planet_house_dict[0] == ninth_house or planet_house_dict[1] == ninth_house or planet_house_dict[7] == ninth_house
    pd.append(pd1)
    pd2 = planet_house_dict[7] == (planet_house_dict['L']+3)%12
    pd.append(pd2)
    pd3 = any([2 in house.associations_of_the_planet(planet_positions, p1) or 6 in house.associations_of_the_planet(planet_positions, p1) for p1 in [0,1,7,8]])
    pd.append(pd3)
    pd4 = any([sum([planet_house_dict[p1]==(planet_house_dict['L']+h-1)%12 for p1 in [3,5,7]])>1 for h in [2,5,9,12] ])
    pd.append(pd4)
    pd5 = any([any([planet_house_dict[p1]==planet_house_dict[p2] for p2 in [7,8]]) for p1 in [0,1] ])
    pd.append(pd5)
    pdc = any(pd)
    if pdc:
        return [pdc, [i+1 for i,m in enumerate(pd) if m]]
    else:
        return [False,[]]
def guru_chandala_dosha(planet_positions):
    """ returns True/False if guru chandal dosha presents in the chart
        if Rahu/Keti conjoins Jupiter - this dosha exists
        @return True/False if chandala dosha, True/False if Jupiter stronger, Rahu/Ketu whicever conjoins Jupiter
    """
    rahu_house = planet_positions[8][1][0] ; ketu_house = planet_positions[9][1][0]
    jupiter_house = planet_positions[5][1][0]
    jupiter_is_strong = False
    if jupiter_house == rahu_house :
        jupiter_is_strong = house.stronger_planet_from_planet_positions(planet_positions, 4, 7)==4
        return True, jupiter_is_strong
    elif jupiter_house == ketu_house :
        jupiter_is_strong = house.stronger_planet_from_planet_positions(planet_positions, 4, 8)==4
        return True, jupiter_is_strong
    else:
        return False,False
def kalathra(planet_positions,reference_planet='L'):
    """
        The placement of malefic planets Mars, Saturn, Sun, Rahu, and Ketu in the 
        1st, 2nd, 4th, 7th, 8th, or 12th house from the Ascendant (Lagna) signifies Kalathra Dosha.
        @param planet_positions:
        @param reference planet - default = 'L' for lagnam. For chandran/moon use the value 1 :  
        @return: True/False if kalathra dosha exists of not
    """
    reference_house = (planet_positions[0][1][0]+6)%12
    if reference_planet==1:
        reference_house = (planet_positions[2][1][0]+6)%12
    kc = all([any([planet_positions[p+1][1][0]==(reference_house+h-1)%12 for h in [1,2,4,7,8,12] ]) for p in const.natural_malefics ])
    #print(kc)
    return kc
def _get_kalathra_results(planet_positions,dosha_msgs,key_str, reference_planet='L'):
    ks_results = {}
    """ get kalathra dosha """
    next_line = "<br><br>"
    ks = 'kalathra'
    ks_key = key_str
    ks_msgs = dosha_msgs[ks]
    kpd = kalathra(planet_positions, reference_planet=reference_planet)
    ks_results[ks_key] = "<html>"+ks_msgs[0]+next_line
    if kpd:
        ks_results[ks_key] = "<html>"+ks_msgs[-1]+next_line
    ks_results[ks_key] += "</html>"
    return ks_results
def ganda_moola(moon_star):
    return moon_star in const.ganda_moola_stars
def _get_ganda_moola_results(jd_at_dob,place,dosha_msgs,key_str):
    m_results = {}
    next_line = "<br><br>"
    m = "ganda_moola"
    m_key = key_str
    m_msgs = dosha_msgs[m]
    moon_star = drik.nakshatra(jd_at_dob, place)
    _gm = ganda_moola(moon_star)
    #print('_gc',_gc)
    m_results[m_key] = "<html>"+m_msgs[0]+next_line
    if _gm:
        m_results[m_key] = m_msgs[-1]+next_line
        m_results[m_key] += m_msgs[const.ganda_moola_stars.index(moon_star)+1]
    return m_results 
def _get_guru_chandala_results(planet_positions,dosha_msgs,key_str):
    m_results = {}
    next_line = "<br><br>"
    m = "guru_chandal"
    m_key = key_str
    m_msgs = dosha_msgs[m]
    rahu_house = planet_positions[8][1][0] ; ketu_house = planet_positions[9][1][0]
    jupiter_house = planet_positions[5][1][0]
    _gc = guru_chandala_dosha(planet_positions)
    #print('_gc',_gc)
    m_results[m_key] = "<html>"+m_msgs[0]+next_line
    if _gc[0]:
        m_results[m_key] = "<html>"+m_msgs[-1]+next_line
        if _gc[1]:
            if jupiter_house==rahu_house:
                m_results[m_key] += utils.resource_strings['guru_stronger_than_rahu']+next_line
            elif jupiter_house==ketu_house:
                m_results[m_key] += utils.resource_strings['guru_stronger_than_ketu']+next_line
            m_results[m_key] += m_msgs[planet_positions[5][1][0]+1] + next_line
    m_results[m_key] += "</html>"
    return m_results
def _get_kala_sarpa_results(planet_positions,dosha_msgs,key_str):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    ks_results = {}
    """ get kala sarpa dosha """
    next_line = "<br><br>"
    ks = 'kala_sarpa'
    ks_key = key_str
    ks_msgs = dosha_msgs[ks]
    kpd = kala_sarpa(house_to_planet_list)
    ks_results[ks_key] = "<html>"+ks_msgs[0]+next_line
    if kpd:
        ks_results[ks_key] = "<html>"+ks_msgs[-1]+next_line
        rahu_house = house.get_relative_house_of_planet(planet_positions[0][1][0],planet_positions[8][1][0])
        #print('rahu house',rahu_house,ks_msgs[rahu_house])
        ks_results[ks_key] += ks_msgs[rahu_house]+next_line
    ks_results[ks_key] += "</html>"
    return ks_results
def ghata(planet_positions):
    """
        Mars/Saturn conjunction results in ghata dosha
        @return: True/False
    """
    return planet_positions[3][1][0]==planet_positions[7][1][0]
def shrapit(planet_positions):
    """
        Rahu/Saturn conjunction results in Shrapit dosha
        @return: True/False
    """
    return planet_positions[8][1][0]==planet_positions[7][1][0]
def _get_ghata_results(planet_positions,dosha_msgs,key_str):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    ks_results = {}
    """ get ghata dosha """
    next_line = "<br><br>"
    ks = 'ghata'
    ks_key = key_str
    ks_msgs = dosha_msgs[ks]
    kpd = ghata(planet_positions)
    ks_results[ks_key] = "<html>"+ks_msgs[0]+next_line
    if kpd:
        ks_results[ks_key] = "<html>"+ks_msgs[-1]+next_line
        mars_house = house.get_relative_house_of_planet(planet_positions[0][1][0], planet_positions[3][1][0])
        ks_results[ks_key] += ks_msgs[mars_house]+next_line
    ks_results[ks_key] += "</html>"
    return ks_results
def _get_shrapit_results(planet_positions,dosha_msgs,key_str):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    ks_results = {}
    """ get shrapt dosha """
    next_line = "<br><br>"
    ks = 'shrapit'
    ks_key = key_str
    ks_msgs = dosha_msgs[ks]
    kpd = shrapit(planet_positions)
    ks_results[ks_key] = "<html>"+ks_msgs[0]+next_line
    if kpd:
        ks_results[ks_key] = "<html>"+ks_msgs[-1]+next_line
        saturn_house = house.get_relative_house_of_planet(planet_positions[0][1][0], planet_positions[7][1][0])
        ks_results[ks_key] += ks_msgs[saturn_house]+next_line
    ks_results[ks_key] += "</html>"
    return ks_results
def _get_manglik_results(planet_positions, dosha_msgs,key_str):
    m_results = {}
    next_line = "<br><br>"
    m = "manglik"
    m_key = key_str
    m_msgs = dosha_msgs[m]
    _manglik = manglik(planet_positions)
    m_results[m_key] = "<html>"+m_msgs[0]+next_line
    if _manglik[0]:
        m_results[m_key] = "<html>"+m_msgs[-1]+next_line
        mars_house = house.get_relative_house_of_planet(planet_positions[0][1][0],planet_positions[3][1][0])
        #print('mars_house',mars_house)
        m_results[m_key] += m_msgs[mars_house]+next_line
        """ Check exceptions """
        e_msgs = dosha_msgs['manglik_exceptions']
        exp = e_msgs[0]
        if _manglik[1]:
            exp = e_msgs[-1]+next_line
            for _me in _manglik[2]:
                exp += "\t"+e_msgs[_me]+next_line
        m_results[m_key] += exp
    m_results[m_key] += "</html>"
    return m_results
def _get_pitru_results(planet_positions,dosha_msgs,key_str):
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    ks_results = {}
    next_line = "<br><br>"
    ks = 'pitru'
    ks_key = key_str
    ks_msgs = dosha_msgs[ks]
    kpd = pitru_dosha(planet_positions)
    ks_results[ks_key] = "<html>"+ks_msgs[0]+next_line
    if kpd[0]:
        ks_results[ks_key] = "<html>"+ks_msgs[-1]+next_line
        for m in kpd[1]:
            ks_results[ks_key] += ks_msgs[m]+next_line
    ks_results[ks_key] += "</html>"
    return ks_results
def get_dosha_details(jd_at_dob,place_as_tuple,language=const._DEFAULT_LANGUAGE):
    dosha_msgs = get_dosha_resources(language)
    #print(dosha_msgs)
    planet_positions = charts.rasi_chart(jd_at_dob, place_as_tuple)
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    dosha_results = {}
    """ get kala sarpa dosha """
    key_str = utils.resource_strings['kala_sarpa_dosha_str']
    ks_results = _get_kala_sarpa_results(planet_positions, dosha_msgs,key_str)
    dosha_results.update(ks_results)
    """ get manglik """
    key_str = utils.resource_strings['manglik_dosha_str']
    m_results = _get_manglik_results(planet_positions, dosha_msgs,key_str)
    dosha_results.update(m_results)
    """ get pitru """
    key_str = utils.resource_strings['pitru_dosha_str']
    m_results = _get_pitru_results(planet_positions,dosha_msgs,key_str)
    dosha_results.update(m_results)
    """ get guru chandala """
    key_str = utils.resource_strings['guru_chandala_dosha_str']
    m_results = _get_guru_chandala_results(planet_positions,dosha_msgs,key_str)
    dosha_results.update(m_results)
    """ get ganda moola """
    key_str = utils.resource_strings['ganda_moola_dosha_str']
    m_results = _get_ganda_moola_results(jd_at_dob,place_as_tuple,dosha_msgs,key_str)
    dosha_results.update(m_results)
    """ get kalathra """
    key_str = utils.resource_strings['kalathra_dosha_str']
    m_results = _get_kalathra_results(planet_positions, dosha_msgs, key_str, reference_planet='L')
    dosha_results.update(m_results)
    """ get ghata """
    key_str = utils.resource_strings['ghata_dosha_str']
    m_results = _get_ghata_results(planet_positions, dosha_msgs, key_str)
    dosha_results.update(m_results)
    """ get shrapit """
    key_str = utils.resource_strings['shrapit_dosha_str']
    m_results = _get_shrapit_results(planet_positions, dosha_msgs, key_str)
    dosha_results.update(m_results)
    return dosha_results
if __name__ == "__main__":
    lang = 'ta'
    utils.set_language(lang)
    res = utils.resource_strings
    from jhora.horoscope.chart import charts
    from jhora.panchanga import drik
    dob = (1996,12,7); tob = (10,34,0); jd_at_dob = utils.julian_day_number(dob, tob)
    place_as_tuple = drik.Place('Chennai, India',13.0878,80.2785,5.5)
    pp = charts.rasi_chart(jd_at_dob, place_as_tuple)
    h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
    print(h_to_p)
    tob_hrs = 10+34/60.0
    sunrise_hrs = drik.sunrise(jd_at_dob, place_as_tuple)[0]
    print(tob_hrs,sunrise_hrs,utils.udhayadhi_nazhikai(tob, sunrise_hrs))
    exit()
    #pp = [['L',(1,0)],[0,(2,0)],[1,(3,0)],[2,(3,0)],[3,(4,0)],[4,(5,2.0)],[5,(6,0)],[6,(7,0)],[7,(5,0)],[8,(0,0)]]
    #dosha_msgs = get_dosha_resources(lang)
    #key_str = utils.resource_strings['guru_chandala_dosha_str']
    ks = get_dosha_details(jd_at_dob, place_as_tuple, language=lang)
    print(ks)
    exit()
    #pp = [['L',(9,0.0)],[0,(7,0.0)],[1,(6,0.0)],[2,(4,0.0)],[3,(8,0.0)],[4,(8,0.0)],[5,(6,0.0)],[6,(11,0.0)],[7,(5,0.0)],[8,(11,0.0)]]
    h_to_p = ['','','','','2','7','1/5','0','3/4','L','','6/8']
    #pp = [['L',(0,0.0)],[0,(9,0.0)],[1,(9,0.0)],[2,(0,0.0)],[3,(10,0.0)],[4,(11,0.0)],[5,(1,0.0)],[6,(10,0.0)],[7,(8,0.0)],[8,(2,0.0)]]
    #h_to_p = ['L/2','5','8','','','','','','7','0/1','6/3','4']
    print('kala_sarpa',kala_sarpa(h_to_p))
    mng = manglik(pp,manglik_reference_planet='L')
    print('manglik dosha',mng)
    exit()
    #pp = [['L',(1,0.0)],[0,(1,0.0)],[0,(7,0.0)],[2,(6,0.0)],[3,(5,0.0)],[4,(4,0.0)],[5,(3,0.0)],[6,(2,0.0)],[7,(1,0.0)],[8,(7,0.0)]]
    h_to_p = ['L','7','0/1','5/6','2','3','4','8','','','','']
    print('kala_sarpa',kala_sarpa(h_to_p))
    h_to_p = ['L','8','0/1','5/6','2','3','4','7','','','','']
    print('kala_sarpa',kala_sarpa(h_to_p))
    h_to_p = ['L','7/0','1','5','2','3','4','6/8','','','','']
    print('kala_sarpa',kala_sarpa(h_to_p))
    h_to_p = ['L','8/0','1','5','2','3','4','6/7','','','','']
    print('kala_sarpa',kala_sarpa(h_to_p))
    h_to_p = ['L','7','0/1','5','2','3','4','8','6','','','']
    print('kala_sarpa',kala_sarpa(h_to_p))
    h_to_p = ['L/0','7','1','5/6','2','3','4','8','','','','']
    print('kala_sarpa',kala_sarpa(h_to_p))
    h_to_p = ['L/6','5','8','','','','','','7','0/1','2/3','4']
    print('kala_sarpa',kala_sarpa(h_to_p))
    mrp = 'L'
    h_to_p = ['L/2','5','8','','','','','','7','0/1','6/3','4']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    h_to_p = ['L','5/2','8','','','','','','7','0/1','6/3','4']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    h_to_p = ['L','5','8','2','','','','','7','0/1','6/3','4']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    h_to_p = ['L','5','8','','','','2','','7','0/1','6/3','4']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    h_to_p = ['L','5','8','','','','','2','0/1','','6/3','4']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    h_to_p = ['L','5','8','','','','','','0/1','','6/3','4/2']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    print('Manglik Exception cases')
    h_to_p = ['5','L','8','','2','','','','0/1','','6/3','4']
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    h_to_p = ['','5','8','','L','','','','0/1','6/3','2','4']
    mng = manglik(h_to_p,manglik_reference_planet=mrp)
    print(h_to_p,'manglik',manglik(h_to_p,manglik_reference_planet=mrp))
    