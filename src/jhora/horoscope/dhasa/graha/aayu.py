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
    Computation of pindayu, Nisargayu, Amsayu dasa
    Ref: https://medium.com/thoughts-on-jyotish/thoughts-on-the-mathematical-ayur-models-and-their-usage-in-the-dasas-such-as-moola-and-naisargika-517dee1396ae
    NOTE: !!! DO NOT USE THIS YET - NOT FULLY IMPLEMENTED YET !!!
    
"""
from jhora import const, utils
from jhora.horoscope.chart import charts,house
from jhora.panchanga import drik
one_year_days = const.sidereal_year
_TOTAL_PINDAYU = sum(const.pindayu_full_longevity_of_planets)
_TOTAL_NISARGAYU = sum(const.nisargayu_full_longevity_of_planets)
_TOTAL_AMSAYU = 120
_DEBUG = False
"""
    Method = 1 => Santhanam (Ref: Santhanam, Brihat Parasara Hora Shastra)
    Method = 2 => Varahamihira (Ref: https://medium.com/thoughts-on-jyotish/thoughts-on-the-mathematical-ayur-models-and-their-usage-in-the-dasas-such-as-moola-and-naisargika-517dee1396ae)
"""
def _astangata_harana(planet_positions):
    """
    •    When a graha is located near to Surya, this Harana is applied.
    •    This does not apply to Śukra and Śani
    •    1/2 is reduced. This is equivalent to multiplying 1/2 to the Base figure.    
    """
    ignore_planets = [5,6]
    planets_in_combustion = charts.planets_in_combustion(planet_positions)
    if _DEBUG: print('planets_in_combustion',planets_in_combustion)
    planets_in_retrograde = charts.planets_in_retrograde(planet_positions)
    """
    # The superior planets (Mars, Jupiter and Shani) are far from Surya during their retrogression
    #    Add 2,4 to ignore planets if retrograde
    [planets_in_retrograde.remove(sp) for sp in [2,4] if sp in planets_in_retrograde]
    """
    if _DEBUG: print('planets_in_retrograde',planets_in_retrograde)
    _harana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    if _DEBUG: print('ignore_planets',ignore_planets)
    temp_dict = {p:0.5 for p in planets_in_combustion if p not in ignore_planets}
    temp_dict1 = {p:0.5 for p in planets_in_retrograde if p not in ignore_planets}
    temp_dict.update(temp_dict1)
    _harana_factors.update(temp_dict)
    return _harana_factors
def _shatru_kshetra_harana(planet_positions,treat_mars_as_strong_in_enemy_sign=True,method=2):
    """
    •    When a Graha occupies its enemy sign, this Harana is applied.
    •    This is not applicable to Vakra graha, which can be interpreted as Retrograde planet or Mangal. 
         It is said that Mangal is strong even in its enemy sign, as it is the god of war.
    •    Retrograde grahas are akin to Exaltation, hence, this weakness does not apply to them.
    •    1/3rd is reduced. This is equivalent to multiplying 2/3 to the Base figure.
    """
    if method==1: treat_mars_as_strong_in_enemy_sign = False
    planets_in_enemy_sign = [p for p,(h,_) in planet_positions[:8] if p!=const._ascendant_symbol and const.house_strengths_of_planets[p][h]==const._ENEMY]
    if treat_mars_as_strong_in_enemy_sign and 2 in planets_in_enemy_sign: planets_in_enemy_sign.remove(2)
    if _DEBUG: print('planets_in_enemy_sign',planets_in_enemy_sign)
    planets_in_retrograde = charts.planets_in_retrograde(planet_positions[:8])
    """
    # The superior planets (Mars, Jupiter and Shani) are far from Surya during their retrogression
    #    Add 2,4 to ignore planets if retrograde
    [planets_in_retrograde.remove(sp) for sp in [2,4] if sp in planets_in_retrograde]
    """
    if _DEBUG: print('planets_in_retrograde',planets_in_retrograde)
    _harana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    temp_dict = {p:2/3 for p in planets_in_enemy_sign if p not in planets_in_retrograde}
    _harana_factors.update(temp_dict)
    return _harana_factors
def _shatru_kshetra_harana_santhanam(planet_positions,treat_mars_as_strong_in_enemy_sign=False):
    """
        2. Satru Kshetra Haraoa: If a planet is in its enemy's sign, reduce one third of the basic years and take only two third. 
        An exception is that a retrograde planet, although placed in inimical sign, does not incur this liability. 
        'Vakrachara' is the expression made by Maharishi Parāśara and hence it accepts a retrograde planet. 
        Mars also does lose in an enemy's sign. => treat_mars_as_strong_in_enemy_sign = FALSE
        (This is the main difference between Santhanam(method=1) and Varahamihira (method=2)
        Needless to mention, a planet in neutral’s Sign (or in friend's sign)is not subjected to this reduction.
    """
    return _shatru_kshetra_harana(planet_positions, treat_mars_as_strong_in_enemy_sign=False, method=1)
def _chakrapata_harana(planet_positions,method=2):
    """
    •    When a Graha is located above the horizon (visible hemisphere), this Harana is applied.
    •    The visible Hemisphere is mapped to houses 12,11,10,9,8,7.
    •    Higher reduction is applied when the Graha is closer to the Lagna and lesser reduction is applied 
         when the graha occupies closer to 7th.
    •    The reduction of Shubha graha is 1/2 of that of Krura Grahas. 
         Only Surya, Mangal and Shani are considered Krura here. Kshina Chandra and Budha (ill conjoined)
         Budha are considered Shubha here.
    """
    """
        TODO: Following rules are to be used to determine malefic/benefic planets
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
        Mercury becomes a natural benefic when he is alone or with more natural
        benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
        Mercury becomes a natural malefic when he is joined by more natural malefics.
        Waning Moon of Krishna paksha is a natural malefic.        
    """
    asc_house = planet_positions[0][1][0]
    subha_asubha_factors = {12:(0,0.5),11:(0.5,0.75),10:(2/3,5/6),9:(3/4,7/8),8:(4/5,9/10),7:(5/6,11/12)}
    _harana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    if _DEBUG: print('subha_grahas',subha_grahas,const.natural_benefics,'asubha_grahas',asubha_grahas,const.natural_malefics)
    subha_dict = {p:subha_asubha_factors[(house.get_relative_house_of_planet(asc_house,h))][0] for p,(h,_) in planet_positions if p in subha_grahas and (house.get_relative_house_of_planet(asc_house,h))>6}
    asubha_dict = {p:subha_asubha_factors[((house.get_relative_house_of_planet(asc_house,h)))][1] for p,(h,_) in planet_positions if p in asubha_grahas and (house.get_relative_house_of_planet(asc_house,h))>6}
    _harana_factors.update(subha_dict); _harana_factors.update(asubha_dict)
    return _harana_factors
def _chakrapata_harana_santhanam(planet_positions,bhava_starts_with_ascendant=False): #jd,place,bhava_starts_with_ascendant=False):
    """
    3. Vyayadi Harana: Planets entail reduction if placed anywhere between the 12th and 7th (reckoned in descending order).
        This need not be mistaken to be Drisyardha Hani. Drisyardha means that half of the zodiac which is visible. 
        Hence it is J 8'0° behind the ascendantal cusp, i.e. up to descendant via meridian. 
        Vyayadi Harana figures are: full, half, 1/3, 1/4, 1/5 and l /6th according to the planet being 
        in 12th, 11th, 10th, 9th, 8th and 7th. 
        These are for malefic planets while a benefice in this connection 
        loses only half of what is noted for a malefic. 
        The Moon is ever a benefice for longevity calculations, 
        as per Maharishi Parāśara. 
        Mercury although joining a malefic be treated as a benefice only, for all longevity calculations.)
        
        'C' ÷ ((14 - House) – (DP ÷ BL)) = Loss of Years
            C = Base Aayu
            (DP=Distance of planet from Bhava start; 
            BL=Bhava length and 'House' is the Bhava occupied by the planet under rectification.
    """
    global bhava_houses
    asc_long = planet_positions[0][1][1]
    _harana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    #bhava_houses = charts.bhava_houses(jd, place)
    bhava_length = 30.0
    if _DEBUG: print('bhava houses',bhava_houses,bhava_length)
    bhava_start = (asc_long - 15)%30; bhava_end = (asc_long + 15)%30
    if bhava_starts_with_ascendant:
        bhava_start = asc_long; bhava_end = (asc_long + 30)%30
    if _DEBUG: print('bhava start',bhava_start,'bhava end',bhava_end)
    vh = {}
    for p,(h,p_long) in planet_positions[:8]:
        bh = bhava_houses[p]
        if bh > 6:
            dp = (p_long-bhava_start)%30 if p_long > bhava_start else (30-bhava_start+p_long)%30
            if _DEBUG: print('dp',dp)
            vh[p] = 1.0 - (1.0/((14-bh)-(dp/bhava_length)))
    _harana_factors.update(vh)
    return _harana_factors
def _krurodaya_harana_santhanam(planet_positions):
    """
        4. Kroorodaya Harana: Only malefic (i.e. Saturn, the Sm and Mars) entail this check if in the ascendant. Mercury, 
        though joining a natural malefic will not be liable to this reduction. Here the ascendant means the area between 
        the starting and ending points of the sign rising. To find out this reduction, the ascendantal cusp in 
        degrees, minutes and seconds be multiplied by the number of basic years donated by the malefic concerned and 
        divided by 21600. The divider is 21600 as these are the total minutes of arc in the zodiac. 
        The figure so arrived should be reduced from the said malefics basic contribution. 
        However, if a benefice aspects the said malefic, reduce only half of the figure so suggested.
        
        NOTE: In above text from Santhanam, no instructions if multiple malefics in lagna
              Nor it mentions if benefic is closer than malefic ignore reduction
    """
    _malefics = [0,2,6]; _benefics = const.natural_benefics
    _harana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    kh_fraction = 1.0 - (planet_positions[0][1][0]*30+planet_positions[0][1][1])/360.0
    kh1 = {m:kh_fraction for m in _malefics if p_to_h[m]==p_to_h[const._ascendant_symbol]}
    mps = {p:planet_positions[p+1][1][1] for p in asubha_grahas if p_to_h[p]==p_to_h[const._ascendant_symbol]}
    mps = sorted(mps.items(),key=lambda x:x[1]-planet_positions[0][1][1]) # sort by ascending close to lagna
    if len(mps)==0: return _harana_factors
    mp = mps[0][0] # consider the closest one to lagna
    aps = [sp for sp in subha_grahas if p_to_h[sp]==p_to_h[mp] and planet_positions[sp][1][1] < planet_positions[mp][1][1] ]
    if len(aps) > 0: return _harana_factors
    if any([p in _benefics for p in house.aspected_planets_of_the_planet(h_to_p, mp)]):
        kh1.update({mp:0.5*kh_fraction})
    _harana_factors.update(kh1)
    return _harana_factors
def _krurodaya_harana(planet_positions,method=2):
    """
        Reduce by Sum of Graha Aayu of all the Grahas arrived at previous steps * Lagna Longitude in the Rasi / 360º
        For Krurodaya Harana, firstly the Lagna fraction needs to be found, which is to be applied to the sum of all 
            the Graha Aayus to determine the reduction that needs to be applied.
    •    This Harana is applied only when a Krura Graha viz., Surya, Shani and Shukra is rising with the Lagna.
    •    If more than one Krura Graha rises in the Lagna, then the one occupying closer to the Lagna degree is considered 
        for this Harana. The remaining are ignored.
    •    If a Shubha graha viz., Guru, Shukra, Budha and Chandra occupy or aspect the Lagna, then the Harana is halved.
    •    If a Shubha Graha also rises with the Krura Graha in the Lagna, then the Harana is ignore, provided the Shubha Graha is closer to the Lagna degree.
         
    """
    """ TODO: To implement above bullet points """
    if method==1: return _krurodaya_harana_santhanam(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    _harana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    kh_fraction = 1.0 - (planet_positions[0][1][0]*30+planet_positions[0][1][1])/360.0
    kh1 = {p:kh_fraction for p in asubha_grahas if p_to_h[p]==p_to_h[const._ascendant_symbol]}
    #print('kh1',kh1)
    """ If more than one Krura Graha rises in the Lagna, then the one occupying closer to the Lagna degree is considered 
        for this Harana. The remaining are ignored."""
    mps = {p:planet_positions[p+1][1][1] for p in asubha_grahas if p_to_h[p]==p_to_h[const._ascendant_symbol]}
    #print('mps',mps,planet_positions[0][1][1])
    mps = sorted(mps.items(),key=lambda x:x[1]-planet_positions[0][1][1]) # sort by ascending close to lagna
    #print('mps',mps)
    if len(mps)==0: return _harana_factors
    mp = mps[0][0] # consider the closest one to lagna
    aps = [sp for sp in subha_grahas if p_to_h[sp]==p_to_h[mp] and planet_positions[sp][1][1] < planet_positions[mp][1][1] ]
    """If a Shubha Graha also rises with the Krura Graha in the Lagna, then the Harana is ignore, 
        provided the Shubha Graha is closer to the Lagna degree. """
    if len(aps) > 0: return _harana_factors
    """ If a Shubha graha viz., Guru, Shukra, Budha and Chandra occupy or aspect the Lagna, then the Harana is halved."""
    if any([p in subha_grahas for p in house.aspected_planets_of_the_planet(h_to_p, mp)]):
        kh1.update({mp:0.5*kh_fraction})
    _harana_factors.update(kh1)
    #print('_krurodaya_harana',_harana_factors)
    return _harana_factors
def _bharana(planet_positions):
    """ This is only needed for Amsayu """
    """
    The Bharanas (Increase in the Base Longevity)
        1.    When the Graha is Retrograde, Exalted or in Svakshetra, then multiply by 3.
        2.    When the Graha is in Sva-Navamsa, Sva-Drekkana or in Vargottama Navamsa, then multiply by 2.
        3.    If a multiplication by both 3 and 2 is applicable to a graha, the higher multiplication factor is applied.
    """
    _bharana_factors = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
    retrograde_planets = charts.planets_in_retrograde(planet_positions)
    pp_3 = charts.drekkana_chart(planet_positions); pp_9 = charts.navamsa_chart(planet_positions)
    chk1 = lambda p:p in retrograde_planets or const.house_strengths_of_planets[p][planet_positions[p+1][1][0]] in [const._EXALTED_UCCHAM, const._OWNER_RULER]
    ph = {p:3.0 for p in range(7) if chk1(p)}; _bharana_factors.update(ph)
    chk23 = lambda p: planet_positions[p+1][1][0]==pp_9[p+1][1][0]
    chk21 = lambda p: const.house_strengths_of_planets[p][pp_9[p+1][1][0]]==const._OWNER_RULER
    chk22 = lambda p: const.house_strengths_of_planets[p][pp_3[p+1][1][0]]==const._OWNER_RULER
    ph1 = {p:2.0 for p in range(7) if chk21(p) or chk22(p) or chk23(p) and _bharana_factors[p]!=2.0}
    _bharana_factors.update(ph1)
    if _DEBUG: print('bharana factors',_bharana_factors)
    return _bharana_factors
def _apply_harana(planet_positions,base_aayu,is_amsayu=False,method=2):
        """ TODO: For AMSAYU there are following special rules
            The base aayu arrived at the previous step needs to increased (Bharana) based on occupation in exaltation, 
            retrogression, Svakshetra, Vargottamamsa, Sva-navamsa, Sva-Drekkana.
            Apply Bharana on base aayu and then haranas
            The Bharanas (Increase in the Base Longevity)
                1.    When the Graha is Retrograde, Exalted or in Svakshetra, then multiply by 3.
                2.    When the Graha is in Sva-Navamsa, Sva-Drekkana or in Vargottama Navamsa, then multiply by 2.
                3.    If a multiplication by both 3 and 2 is applicable to a graha, the higher multiplication factor is applied.
            The Haranas (Decrease in the Base Longevity)
                1.    The same Haranas as the Pindayu and Nisargayu Methods are also applied here. Only Krurodaya Harana is not applied.
                2.    If more than two Haranas between Shatrukshetra and Astangata Harana is applicable to the graha, then the only the higher reduction is applied. The Chakrapata Harana is not affected by this and need to be carried out independently.
        """
        """ Astangata Harana - combusion factor """
        """ Santhanam Book says only one of the harana which is max to be applied for each planet """
        final_harana = {}
        ah = _astangata_harana(planet_positions) # does not depend on the method
        if _DEBUG: print('_astangata_harana',ah,final_harana)
        """ Shatru Kshetra Harana """
        skh = _shatru_kshetra_harana(planet_positions)
        final_harana.update({p:min(v1,skh[p]) for p,v1 in ah.items()})
        if _DEBUG: print('_shatru_kshetra_harana',skh,final_harana)
        """ Chakrapata Harana """
        ch = _chakrapata_harana(planet_positions) if method==2 else _chakrapata_harana_santhanam(planet_positions)#jd, place)
        final_harana.update({p:min(v1,ch[p]) for p,v1 in final_harana.items()})
        if _DEBUG: print('_chakrapata_harana',ch,final_harana)
        """ Krurodaya Harana Not applicable for Amsayu """
        kh = {p:1.0 for p in [const._ascendant_symbol]+[*range(7)]}
        if not is_amsayu: kh = _krurodaya_harana(planet_positions)
        final_harana.update({p:min(v1,kh[p]) for p,v1 in final_harana.items()})
        if _DEBUG: print('_krurodaya_harana',kh,final_harana)
        """ Graha Aayu = Base Aayu * (1 — Shatrukshetra Harana) * (1 — Astangata Harana) * (1 — Chakrapata Harana) """
        #graha_aayu = {p:base_aayu[p]*ah[p]*skh[p]*ch[p]*kh[p] for p in base_aayu.keys()}
        graha_aayu = {p:base_aayu[p]*final_harana[p] for p in base_aayu.keys()}
        if _DEBUG: print(base_aayu,'graha_ayu after harana',graha_aayu)
        return graha_aayu
def _pindayu_santhanam(planet_positions,apply_haranas=True,method=1):
    planet_base_longevity = {}
    for planet in range(7):
        planet_long = planet_positions[planet+1][1][0]*30+planet_positions[planet+1][1][1]
        if _DEBUG: print('planet',planet,'planet_long',planet_long)
        arc_of_longevity = utils.norm360(360+planet_long - const.planet_deep_exaltation_longitudes[planet])
        if _DEBUG: print('planet',planet,'arc_of_longevity',arc_of_longevity)
        if arc_of_longevity > 180.0:
            planet_base_longevity[planet] = const.pindayu_full_longevity_of_planets[planet]*arc_of_longevity/360.0
        else:
            planet_base_longevity[planet] = const.pindayu_full_longevity_of_planets[planet] - const.pindayu_full_longevity_of_planets[planet]*arc_of_longevity/360.0
        if _DEBUG: print('planet',planet,'planet_base_longevity santhanam',planet_base_longevity[planet])
    if apply_haranas:
        return _apply_harana(planet_positions,planet_base_longevity,method=method)
    else:
        return planet_base_longevity
    
def _pindayu(planet_positions,apply_haranas=True,method=2):
    return _pindayu_santhanam(planet_positions, apply_haranas, method)
    planet_base_longevity = {}
    for planet in range(7):
        planet_long = planet_positions[planet+1][1][0]*30+planet_positions[planet+1][1][1]
        arc_of_longevity = utils.norm360(360+planet_long - const.planet_deep_exaltation_longitudes[planet])
        effective_arc = arc_of_longevity - 180 if arc_of_longevity > 180 else arc_of_longevity
        planet_base_longevity[planet] = const.pindayu_full_longevity_of_planets[planet]*effective_arc/360.0
    if _DEBUG: print('planet_base_longevity',planet_base_longevity)
    if apply_haranas:
        return _apply_harana(planet_positions,planet_base_longevity,method=method)
    else:
        return planet_base_longevity
def _nisargayu_santhanam(planet_positions,apply_haranas=True,method=1):
    planet_base_longevity = {}
    for planet in range(7):
        planet_long = planet_positions[planet+1][1][0]*30+planet_positions[planet+1][1][1]
        if _DEBUG: print('_nisargayu_santhanam','planet_long',planet_long)
        arc_of_longevity = utils.norm360(360+planet_long - const.planet_deep_exaltation_longitudes[planet])
        if _DEBUG: print('_nisargayu_santhanam','arc_of_longevity',arc_of_longevity)
        if arc_of_longevity > 180.0:
            planet_base_longevity[planet] = const.nisargayu_full_longevity_of_planets[planet]*arc_of_longevity/360.0
        else:
            planet_base_longevity[planet] = const.nisargayu_full_longevity_of_planets[planet] - const.nisargayu_full_longevity_of_planets[planet]*arc_of_longevity/360.0
        if _DEBUG: print(planet,'planet_base_longevity santhanam',planet_base_longevity[planet])
    if _DEBUG: print('planet_base_longevity santhanam',planet_base_longevity)
    if apply_haranas:
        return _apply_harana(planet_positions,planet_base_longevity,method=method)
    else:
        return planet_base_longevity
def _nisargayu(planet_positions,apply_haranas=True,method=2):
    return _nisargayu_santhanam(planet_positions, apply_haranas, method)
    if method==1: return _nisargayu_santhanam(planet_positions, apply_haranas, method)
    planet_base_longevity = {}
    for planet in range(7):
        planet_long = planet_positions[planet+1][1][0]*30+planet_positions[planet+1][1][1]
        if _DEBUG: print('_nisargayu','planet_long',planet_long)
        arc_of_longevity = utils.norm360(planet_long - const.planet_deep_exaltation_longitudes[planet])
        if _DEBUG: print('_nisargayu','arc_of_longevity',arc_of_longevity,const.planet_deep_exaltation_longitudes[planet])
        effective_arc = arc_of_longevity - 180 if arc_of_longevity > 180 else arc_of_longevity
        if _DEBUG: print('_nisargayu','effective_arc',effective_arc)
        planet_base_longevity[planet] = const.nisargayu_full_longevity_of_planets[planet]*effective_arc/360.0
        if _DEBUG: print(planet,'planet_base_longevity',planet_base_longevity[planet])
    if _DEBUG: print('planet_base_longevity',planet_base_longevity)
    if apply_haranas:
        return _apply_harana(planet_positions,planet_base_longevity)
    else:
        return planet_base_longevity
    
def _amsayu(planet_positions,apply_haranas=True,method=1):
    planet_base_longevity = {}
    for planet,(h,p_long) in planet_positions[1:8]: #range(7):
        planet_long = h*30+p_long
        planet_base_longevity[planet] = (planet_long*108) % 12
        if method==2:planet_base_longevity[planet] = (planet_long*60/200) %12 # Varhamihira
    if _DEBUG: print('planet_base_longevity',planet_base_longevity)
    if apply_haranas:
        bh = _bharana(planet_positions)
        ah =  _apply_harana(planet_positions,planet_base_longevity,is_amsayu=True)
        graha_aayu = {p:ah[p]*bh[p] for p in ah.keys()}
        return graha_aayu
    else:
        return planet_base_longevity
def _stronger_of_lagna_sun_moon(planet_positions):
    sp = house.stronger_planet_from_planet_positions(planet_positions, 0, 1)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    asc_house = p_to_h[const._ascendant_symbol]; sp_house = p_to_h[sp]
    sr = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, sp_house)
    if sr == asc_house: 
        return const._ascendant_symbol
    else:
        return sp
def _lagna_longevity_santhanam(jd,place):
    pp_rasi = charts.rasi_chart(jd, place)
    asc_rasi = pp_rasi[0][1][0]; asc_rasi_lord = house.house_owner_from_planet_positions(pp_rasi, asc_rasi)
    asc_rasi_long = asc_rasi*30+pp_rasi[0][1][1]
    if _DEBUG: print(asc_rasi,'asc rasi long',asc_rasi_long)
    asc_nava = (asc_rasi+8)%12; asc_navamsa_lord = house.house_owner_from_planet_positions(pp_rasi, asc_nava)
    asc_nava_long = asc_nava*30+(asc_rasi_long//30)
    if _DEBUG: print(asc_nava,'asc nava long',asc_nava_long)
    sp = house.stronger_planet_from_planet_positions(pp_rasi, asc_rasi_lord, asc_navamsa_lord)
    if _DEBUG: print(asc_rasi_lord,asc_navamsa_lord,'stronger is',sp)
    _lagna_aayu = asc_rasi_long/30.0;
    if sp==asc_navamsa_lord:
        _lagna_aayu = asc_nava_long/30.0;
    return _lagna_aayu
def _lagna_longevity(jd,place,divisional_chart_factor=9,chart_method=1):
    pp_chart = charts.rasi_chart(jd, place)
    asc_chart = pp_chart[0][1][0]; asc_chart_lord = house.house_owner_from_planet_positions(pp_chart, asc_chart)
    asc_chart_long = asc_chart*30+pp_chart[0][1][1]
    pp_navamsa = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
    asc_nava = pp_navamsa[0][1][0]; asc_navamsa_lord = house.house_owner_from_planet_positions(pp_navamsa, asc_nava)
    asc_nava_long = asc_nava*30+pp_navamsa[0][1][1]
    _lagna_aayu = asc_chart_long/30.0;
    if const.house_strengths_of_planets[asc_navamsa_lord][asc_nava] > const.house_strengths_of_planets[asc_chart_lord][asc_chart]:
        _lagna_aayu = asc_nava_long/30.0;
    return _lagna_aayu
def _get_aayur_type(planet_positions):
    return _stronger_of_lagna_sun_moon(planet_positions)
def _get_global_constants(jd,place):
    global subha_grahas, asubha_grahas, bhava_houses
    subha_grahas, asubha_grahas = charts.benefics_and_malefics(jd, place, method=1)#BV Raman's method
    bhava_houses = charts.bhava_houses(jd, place)#; bhava_length = 30.0
    """
    bm1 = drik.bhaava_madhya(jd, place,bhava_method=const.bhaava_madhya_method); bhava_madhya = bm1[:]+[bm1[0]]
    if _DEBUG: print('bhava madhya',[utils.to_dms(bm,is_lat_long='plong') for bm in bhava_madhya])
    bhava_lengths = [(bhava_madhya[i+1]-bhava_madhya[i])%60 for i in range(len(bhava_madhya)-1)]
    bhava_starts = [(bhava_madhya[i]-0.5*bhava_lengths[i])%30 for i in range(12) ]
    """
    return
def get_dhasa_antardhasa(jd,place,aayur_type=None,include_antardhasa=True,apply_haranas=True,dhasa_method=2,
                         divisional_chart_factor=9,chart_method=1):
    """
        provides Aayu dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param aayur_type (0=Pindayu, 1=Nisargayu, 2=Amsayu, None=Automatically determine whichever is applicable)
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param apply_haranas: (True/False) whether to or not to apply haranas (Default=True)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    planet_positions = charts.rasi_chart(jd, place)
    if _DEBUG: print('planet_positions',planet_positions)
    global subha_grahas, asubha_grahas, bhava_houses
    bhava_houses = charts.bhava_houses(jd, place)
    subha_grahas, asubha_grahas = charts.benefics_and_malefics(jd, place, method=1)#BV Raman's method
    bm1 = drik.bhaava_madhya(jd, place,const.bhaava_madhya_method); bhava_madhya = bm1[:]+[bm1[0]]
    if _DEBUG: print('bhava madhya',[utils.to_dms(bm,is_lat_long='plong') for bm in bhava_madhya])
    bhava_lengths = [(bhava_madhya[i+1]-bhava_madhya[i])%60 for i in range(len(bhava_madhya)-1)]
    bhava_starts = [bhava_madhya[i]-0.5*bhava_lengths[i] for i in range(12) ]
    if _DEBUG: print('bhava length',[utils.to_dms(bm,is_lat_long='plong') for bm in bhava_lengths])
    if _DEBUG: print('bhava start',[utils.to_dms(bs%30,is_lat_long='plong') for bs in bhava_starts])
    _lagna_duration = _lagna_longevity(jd,place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
    sp = aayur_type if aayur_type!=None else _get_aayur_type(planet_positions)
    if _DEBUG: print('stronger of lagna/Sun/Moon',sp)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    _dhasa_seed = p_to_h[sp]
    if _DEBUG: print('dhasa seed',_dhasa_seed)
    dhasa_progression = charts.order_planets_from_kendras_of_raasi(planet_positions[:8], _dhasa_seed,include_lagna=True)
    if sp in [0,1,const._ascendant_symbol]:
        dhasa_progression = [sp] + [p for p in dhasa_progression if p!=sp]
    if _DEBUG: print('dhasa progression',dhasa_progression)
    start_jd = jd
    dhasas = []
    
    if sp == 0:
        if _DEBUG: print('Aayu type Pindayu')
        _dhasa_duration = _pindayu(planet_positions,apply_haranas,method=dhasa_method)
        _total_duration = _TOTAL_PINDAYU
        _dhasa_type = 0 # Pindyayu = Sun is the lord
    elif sp == 1:
        if _DEBUG: print('aayu type nisargayu')
        _dhasa_duration = _nisargayu(planet_positions,apply_haranas,method=dhasa_method)
        _total_duration = _TOTAL_NISARGAYU
        _dhasa_type = 1 # Nisargayu Moon is the lord
    else: # sp == const._ascendant_symbol:
        if _DEBUG: print('aayu type amsayu')
        _dhasa_duration = _amsayu(planet_positions,apply_haranas,method=dhasa_method)
        _total_duration = _TOTAL_AMSAYU
        _dhasa_type = 2 # Amsayu - Lagna is the lord
    _dhasa_duration[const._ascendant_symbol] = _lagna_longevity(jd, place)
    if _DEBUG: print('dhasa duration',_dhasa_duration)
    for lord in dhasa_progression:
        dd = _dhasa_duration[lord]
        bhukthis = dhasa_progression # Antardhasa follows same dhasa progression
        if include_antardhasa:
            ddb = dd/(len(dhasa_progression))
            for bhukthi in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasas.append((lord,bhukthi,dhasa_start,round(ddb,2)))
                start_jd += ddb * one_year_days
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasas.append((lord,dhasa_start,round(dd,2)))
            start_jd += dd * one_year_days
    return _dhasa_type, dhasas
def pindayu_dhasa_bhukthi(jd,place,include_antardhasa=True,apply_haranas=True,dhasa_method=2,
                          divisional_chart_factor=9,chart_method=1):
    return get_dhasa_antardhasa(jd, place, aayur_type=0, include_antardhasa=include_antardhasa, 
                                apply_haranas=apply_haranas, dhasa_method=dhasa_method,
                                divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)[1]
def nisargayu_dhasa_bhukthi(jd,place,include_antardhasa=True,apply_haranas=True,dhasa_method=2,
                          divisional_chart_factor=9,chart_method=1):
    return get_dhasa_antardhasa(jd, place, aayur_type=1, include_antardhasa=include_antardhasa, 
                                apply_haranas=apply_haranas, dhasa_method=dhasa_method,
                                divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)[1]
def amsayu_dhasa_bhukthi(jd,place,include_antardhasa=True,apply_haranas=True,dhasa_method=2,
                          divisional_chart_factor=9,chart_method=1):
    return get_dhasa_antardhasa(jd, place, aayur_type=2, include_antardhasa=include_antardhasa, 
                                apply_haranas=apply_haranas, dhasa_method=dhasa_method,
                                divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)[1]
def longevity(jd,place,aayu_type=None,dhasa_method=2):
    _at,_adb = get_dhasa_antardhasa(jd, place, aayur_type=aayu_type, include_antardhasa=False, apply_haranas=True, dhasa_method=dhasa_method)
    _longevity = sum(d for _,_,d in _adb)
    return _longevity,_at
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.aayu_test()
