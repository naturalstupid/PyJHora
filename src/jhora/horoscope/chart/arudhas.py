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
        V4.8.9
            - bhava_arudha_longitudes_from_planet_positions removed. Use charts.arudha_lagna_longitudes instead.
            - this module calculates only for rasi chart level. Use charts.arudha_lagna_longitudes for vargas.
            - graha_arudhas_from_planet_positions - now return [ (graha_arudha_rasi, planet_longitude), ...]
"""
from jhora import const, utils
from jhora.horoscope.chart import house, charts
_bhava_arudha_prefix_list = ["A","Su","Mo","Ma","Ju","ve","Sa","Ra","Ke"]

def bhava_arudhas_from_planet_positions(planet_positions,arudha_base=0):
    """
        gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna)
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @param arudha_base: (0=Lagna, 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn, 8=Rahu, 9=Ketu)
            0 = Lagna - will return A1, A2, ... A12
            1 = Sun - will return Surya Arudhas S1, S2,... S12
            2 = Moon - will return Chandra Arudhas M1, M2, .. M12
        @return bhava arudhas of houses. first element is rasi for the first house from arudha base and so on
    """
    """ V3.6.4 Below line is crucial. If Uranus/Netp/Pluto included wrong A1..A12 results
        So planet_positions restricted [:const._pp_count_upto_ketu] """
    planet_positions = planet_positions[:const._pp_count_upto_ketu]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    base_house = planet_positions[arudha_base][1][0]
    houses = [(h+base_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for h in houses:
        lord_of_the_house = house.house_owner_from_planet_positions(planet_positions, h, check_during_dhasa=False)
        house_of_the_lord = p_to_h[lord_of_the_house]
        signs_between_house_and_lord = utils.count_rasis(h,house_of_the_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = utils.count_rasis(h,bhava_arudha_of_house)-1#((bhava_arudha_of_house+1+12-h)%12)
        if signs_from_the_house in [const.HOUSE_1, const.HOUSE_7]: #[1,7]:
            bhava_arudha_of_house = (bhava_arudha_of_house+const.HOUSE_10)%12
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def bhava_arudha_longitudes(
    jd,
    place,
    arudha_base=0,
    bhava_madhya_method=None,
    ascendant_is_middle_of_house=True,
    **kwargs
):
    """
    Ref: https://www.vedicastrologer.org/articles/padamsa_transit.pdf
         https://www.youtube.com/shorts/YguEbXWGCBw
    Returns full longitudes (0..360) for bhava arudhas from base:
      arudha_base=0 -> A1..A12
      arudha_base=1 -> Su1..Su12
      arudha_base=2 -> Mo1..Mo12
      etc.

    Uses bhava madhya (cusp) longitudes from charts._bhaava_madhya_new.
    """
    if bhava_madhya_method is None: bhava_madhya_method = const.bhaava_madhya_method
    if "divisional_chart_factor" in kwargs:
        planet_positions = charts.divisional_chart(jd, place, exclude_non_planets=True,**kwargs)[:const._pp_count_upto_ketu]
    elif "varga_factor_1" in kwargs and "varga_factor_2" in kwargs:
        planet_positions = charts.mixed_chart(jd, place,exclude_non_planets=True,**kwargs)
    else:
        planet_positions = charts.rasi_chart(jd, place)

    # planet full longitude map
    p_to_full_lon = {}
    for p, (r, lon_in_sign) in planet_positions:
        p_to_full_lon[p] = (int(r) % 12) * 30.0 + float(lon_in_sign)
    # Use reference_planet_for_ascendant to anchor the "1st house" at base (A/Su/Mo/...)
    # For Lagna base use None. For others, use the corresponding planet id.
    reference_planet_for_ascendant = None
    if arudha_base != 0:
        # planet_positions[arudha_base][0] is the planet-id for Sun/Moon/... in your structure
        reference_planet_for_ascendant = planet_positions[arudha_base][0]
    # Get bhava madhyas: [[house_rasi,(start,cusp,end)], ...] with cusp as full longitude
    bhavas = charts._bhaava_madhya_new(
        jd=jd,
        place=place,
        bhava_madhya_method=bhava_madhya_method,
        reference_planet_for_ascendant=reference_planet_for_ascendant,
        ascendant_is_middle_of_house=ascendant_is_middle_of_house,
        **kwargs
    )
    # For equal houses, bhavas should be 12 entries; cusp is B_h
    out = []
    for i in range(12):
        # mid/cusp longitude (what JHora displays as cusp)
        B = float(bhavas[i][1][1])
        # sign where this cusp lies (lord is based on this sign)
        house_sign = int(B // 30.0) % 12
        lord = house.house_owner_from_planet_positions(
            planet_positions, house_sign, check_during_dhasa=False
        )
        L = float(p_to_full_lon[lord])
        # reflect using MID cusp
        A = (2.0 * L - B) % 360.0
        ### Apply Exceptions if Applicable
        # ---- PVR padamsa_transit correction, but test over the HOUSE SPAN ----
        # Use the HOUSE START boundary as reference for the 0–30 and 180–210 windows.
        S = float(bhavas[i][1][0])           # house start longitude
        delta = (A - S) % 360.0              # <-- changed from (A - B)
        # If A falls in the same 30° house span [0,30) from start,
        # or in the 7th house span [180,210) from start, shift by -90°.
        if (0.0 <= delta < 30.0) or (180.0 <= delta < 210.0):
            A = (A - 90.0) % 360.0 # subtract 90° as stated by PVR [2]
        out.append(A)
    return out

def bhava_arudhas_from_chart(chart_1d,arudha_base=0):
    """
        gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna)
        @param chart_1d: chart in the format ["1","2/3",..."L/5"]
        @param arudha_base: (0=Lagna, 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn, 8=Rahu, 9=Ketu)
            0 = Lagna - will return A1, A2, ... A12
            1 = Sun - will return Surya Arudhas S1, S2,... S12
            2 = Moon - will return Chandra Arudhas M1, M2, .. M12
        @return bhava arudhas of houses. first element is rasi for the first house from arudha base and so on
    """
    """ V3.6.4 Below line is crucial. If Uranus/Netp/Pluto included wrong A1..A12 results
        So planet_positions restricted [:const._pp_count_upto_ketu] """
    h_to_p = chart_1d[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    base_house = p_to_h[const._ascendant_symbol] if arudha_base==0 else p_to_h[arudha_base-1]
    houses = [(h+base_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for h in houses:
        lord_of_the_house = house.house_owner(h_to_p, h)
        house_of_the_lord = p_to_h[lord_of_the_house]
        signs_between_house_and_lord = utils.count_rasis(h,house_of_the_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = utils.count_rasis(h,bhava_arudha_of_house)-1#((bhava_arudha_of_house+1+12-h)%12)
        if signs_from_the_house in [const.ARIES, const.LIBRA]: #[1,7]:
            bhava_arudha_of_house = (bhava_arudha_of_house+const.HOUSE_10)%12
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def surya_arudhas_from_planet_positions(planet_positions):
    return bhava_arudhas_from_planet_positions(planet_positions, arudha_base=1)
def chandra_arudhas_from_planet_positions(planet_positions):
    return bhava_arudhas_from_planet_positions(planet_positions, arudha_base=2)
def bhava_arudhas(chart):
    """
        gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna)
        @param chart: Enter chart information in the following format. 
            For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    houses = [(h+asc_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for h in houses:
        lord_of_the_house = house.house_owner(h_to_p, h) # V2.3.1
        house_of_the_lord = p_to_h[lord_of_the_house]
        signs_between_house_and_lord = utils.count_rasis(h,house_of_the_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = ((bhava_arudha_of_house+12-h)%12)
        if signs_from_the_house in [const.ARIES, const.LIBRA]: #[1,7]:
            bhava_arudha_of_house = (bhava_arudha_of_house+const.HOUSE_10)%12
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def graha_arudhas_from_planet_positions(planet_positions):
    """
        gives Graha Arudhas for each planet from the planet positions
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return [(graha arudhas of planet,planet_longitude)...]. 
            first element is for Lagnam, then Sun,Moon.. last element is for Ketu
    """
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_long = planet_positions[0][1][1]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    graha_arudhas_of_planets = [(p_to_h[const._ascendant_symbol],asc_long)]
    for p in range(const._planets_upto_ketu):
        _,(h,long) = planet_positions[p+1]
        house_of_the_planet = p_to_h[p]
        sign_owned_by_planet = const.house_lords_dict[p]
        if len(sign_owned_by_planet)>1:
            sign_owned_by_planet = house.stronger_rasi_from_planet_positions(planet_positions,sign_owned_by_planet[0],sign_owned_by_planet[1])
        else:
            sign_owned_by_planet = sign_owned_by_planet[0]
        count_to_strong = (sign_owned_by_planet+1+12-house_of_the_planet)%12
        count_to_arudha = (house_of_the_planet+2*(count_to_strong-1))%12
        count_from_house = (house_of_the_planet+12-count_to_arudha)%12
        if count_from_house in [const.ARIES, const.LIBRA]: #[0,6]:
            count_to_arudha = (count_to_arudha+const.HOUSE_10)%12
        graha_padha_of_planet = count_to_arudha
        graha_arudhas_of_planets.append((graha_padha_of_planet,long))
    return graha_arudhas_of_planets
def graha_arudhas(chart):
    """
        gives Graha Arudhas for each planet from the chart
        @param chart: Enter chart information in the following format. For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    graha_arudhas_of_planets = [p_to_h[const._ascendant_symbol]]
    for p in range(const._planets_upto_ketu):
        house_of_the_planet = p_to_h[p]
        sign_owned_by_planet = const.house_lords_dict[p]
        if len(sign_owned_by_planet)>1:
            sign_owned_by_planet = house.stronger_rasi(h_to_p,sign_owned_by_planet[0],sign_owned_by_planet[1])
        else:
            sign_owned_by_planet = sign_owned_by_planet[0]
        count_to_strong = (sign_owned_by_planet+1+12-house_of_the_planet)%12
        count_to_arudha = (house_of_the_planet+2*(count_to_strong-1))%12
        count_from_house = (house_of_the_planet+12-count_to_arudha)%12
        if count_from_house in [const.ARIES, const.LIBRA]: #[0,6]:
            count_to_arudha = (count_to_arudha+const.HOUSE_10)%12
        graha_padha_of_planet = count_to_arudha
        graha_arudhas_of_planets.append(graha_padha_of_planet)
    return graha_arudhas_of_planets
    
if __name__ == "__main__":
    #"""
    """ 
        drik here is generic model name can be surya_sidhantha or drik depending on value 
        of const.astrology_model_default value
    """
    drik = utils.hora_engine_proxy
    utils.set_language('en')
    drik.set_ayanamsa_mode("TRUE_PUSHYA")
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5) 
    jd = utils.julian_day_number(dob, tob); dcf = 1; arudha_base = 0;
    arudha_base_list = ['A','Su','Mo','Ma','Me','Ju','Ve','Sa','Ra','Ke']
    from jhora.horoscope.chart import charts
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=dcf)
    print(utils.get_house_planet_list_from_planet_positions(planet_positions))
    ba1 = bhava_arudhas_from_planet_positions(planet_positions,arudha_base=arudha_base)
    ba = bhava_arudha_longitudes(jd,place,arudha_base=arudha_base)
    exp_jhora = ["22Ar18'.12.79","22Pi18'20.95","0Cn20'50.53","29Sg46'14.74","26Pi07'31.91","28Ta33'50.99","22Sg36'36.88",
                 "21Sc49'18.59","28Aq33'50.99","26Cn07'31.91","2Cn05'43.65","0Li20'50.53"]
    for b in range(12):
        print("A"+str(b+1),
              utils.RAASI_LIST[ba1[b]],
              utils.deg_to_sign_str(ba[b]),"Expected",exp_jhora[b])
    exit()
    ga = graha_arudhas_from_planet_positions(planet_positions)
    print(ga)
    ga_chart = ['' for _ in range(12)]
    for p,r in enumerate(ga):
        ga_chart[r] += 'L/' if p==0 else str(p-1)+'/'
    for b in range(len(ga_chart)):
        if ga_chart[b] != '' and ga_chart[b][-1]=='/': ga_chart[b] = ga_chart[b][:-1]
    print(ga_chart)
    exit()
    #"""
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.chapter_9_tests()
