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
from jhora.horoscope.chart import house, charts
from jhora import utils, const
from jhora.panchanga import drik
one_year_days = const.sidereal_year
jcd_year_factor = 324/one_year_days
turns_of_moon = 27.32
nakshathra_year = const.nakshathra_year
"""
    DO NOT USE THIS YET. UNDER TESTING...
    Based on Book: Hindu Predictive Astrology - by BV Raman
"""
def _baladrishta_checks(jd,place,divisional_chart_factor=1):
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    print(h_to_p)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    print(p_to_h)
    asc_house = p_to_h['L']
    _relative_house = lambda sign: house.get_relative_house_of_planet(asc_house,sign)
    bd_checks = []
    """ malefics in last navamsa """
    """ Moon in kendra with malefics """
    bc = any([p_to_h[1] in q for q in [house.quadrants_of_the_raasi(p_to_h[m]) for m in const.natural_malefics]])
    bd_checks.append(bc)
    """ Moon in 7/8/12th house with malefics and without benefic aspects"""
    bc = (_relative_house(p_to_h[1]) in [7,8,12]) and \
            any([p_to_h[1]==p_to_h[m] for m in const.natural_malefics]) and \
            any([1 in q for q in [house.aspected_planets_of_the_planet(h_to_p, b) for b in const.natural_benefics]])
    bd_checks.append(bc)
    """ Malefics in 2,6,8,12 house """
    bc = all([mh in [2,6,8,12] for mh in [_relative_house(p_to_h[m]) for m in charts.malefics(jd, place)]])
    bd_checks.append(bc)
    """ Weak moon in ascendant or 8th and Malefics in quadrants """
    bc = const.house_strengths_of_planets[1][p_to_h[1]] < const._FRIEND and \
                ( (p_to_h[1] == asc_house) or (_relative_house(p_to_h[1])==8) ) and \
                any([m in house.quadrants_of_the_raasi(p_to_h[1]) for m in const.natural_malefics])
    
    bd_checks.append(bc)
    """ Moon in ascendant, Mars in 8th, Sun in 9th, and Saturn in 12th """
    bc = (asc_house==p_to_h[1]) and (_relative_house(p_to_h[0])==9) and \
         (_relative_house(p_to_h[2])==8) and \
         (_relative_house(p_to_h[6])==12)
    bd_checks.append(bc)
    """ Moon in 8th, Mars in 7th, Rahu in 9th, and Jupiter in 3rd """
    bc = (_relative_house(p_to_h[1])==8) and \
         (_relative_house(p_to_h[2])==7) and \
         (_relative_house(p_to_h[7])==9) and \
         (_relative_house(p_to_h[4])==3)
    bd_checks.append(bc)
    return bd_checks
def _alpayu_checks(jd,place,divisional_chart_factor=1):
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    print(h_to_p)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    print(p_to_h)
    asc_house = p_to_h['L']
    _relative_house = lambda sign: house.get_relative_house_of_planet(asc_house,sign)
    _house_owner = lambda sign:house.house_owner_from_planet_positions(planet_positions,sign)
    """ Saturn in 8th, Mars in 5th and Kethu with Ascendant/1st """
    ad_checks = []
    ac = (_relative_house(p_to_h[6])==8) and \
         (_relative_house(p_to_h[2])==5) and \
         (asc_house==p_to_h[8])
    ad_checks.append(ac)
    ac = all([mh in [6,8,12] for mh in [_relative_house(p_to_h[m]) for m in charts.malefics(jd, place)]])
    ad_checks.append(ac)
    """ Saturn in Lagna and the Sun, Moon and Mars in 7th """
    ac = (p_to_h[1]==p_to_h[2]) and (p_to_h[0]==p_to_h[1])\
         (_relative_house(p_to_h[2])==7) and \
         (asc_house==p_to_h[6])
    ad_checks.append(ac)
    """ Lord of 8th in Ascendant with Kethu"""
    eighth_lord = _house_owner((asc_house+7)%12)
    ac = asc_house==p_to_h[eighth_lord] and asc_house==p_to_h[8]
    ad_checks.append(ac)
    """ Malefics with Ascendant and moon is in conjunction """
    """ TODO: Any malefic or All Malefics??? """
    ac = any([p_to_h[1] == p_to_h[m] and asc_house == p_to_h[m] for m in const.natural_malefics])
    ad_checks.append(ac)
    """ Lord of 8th in Ascendant and Lagna Lord is powerless """
    eighth_lord = _house_owner((asc_house+7)%12)
    lagna_lord = _house_owner(asc_house)
    #print(eighth_lord,lagna_lord,const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]])
    ac = (p_to_h[eighth_lord]==asc_house) and (const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] < const._FRIEND)
    ad_checks.append(ac)
    """ Lagna in Scorpio/Vrichigam with Sun and Jupiter, 8th lord in quardrants """
    ac = (asc_house==p_to_h[0]) and (asc_house==p_to_h[4] and (asc_house==7))
    eighth_lord = _house_owner((asc_house+7)%12)
    ac = ac and any([p_to_h[eighth_lord] in house.quadrants_of_the_raasi(asc_house)])
    #print(eighth_lord,p_to_h[eighth_lord],house.quadrants_of_the_raasi(asc_house))
    ad_checks.append(ac)
    """ Rahu/7th and Moon/8th and Jupiter/Ascendant""" 
    ac = _relative_house(p_to_h[7])==7 and \
         _relative_house(p_to_h[1])==8 and \
         (asc_house == p_to_h[4])
    ad_checks.append(ac)
    """ Saturn/Ascendant owned by malefic and benefics in [3,6,9,12] """
    ac = asc_house==p_to_h[6] and \
         any([m == lagna_lord for m in charts.malefics(jd, place)]) and \
         all([_relative_house(p_to_h[b]) in [3,6,9,12]  for b in charts.benefics(jd, place)])    
    ad_checks.append(ac)
    """ Lords of Asc and 8th conjoin in 8th with malefics and without beneficial aspect """
    ac = p_to_h[lagna_lord]==p_to_h[eighth_lord] and \
         p_to_h[lagna_lord]==(asc_house+7)%12 and \
         any([p_to_h[m] == p_to_h[lagna_lord] for m in charts.malefics(jd, place)]) and \
         any([lagna_lord in q for q in [house.aspected_planets_of_the_planet(h_to_p, b) for b in const.natural_benefics]])
    ad_checks.append(ac)
    return ad_checks
def _madhyayu_checks(jd,place,divisional_chart_factor=1):
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    print(h_to_p)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    print(p_to_h)
    asc_house = p_to_h['L']
    _relative_house = lambda sign: house.get_relative_house_of_planet(asc_house,sign)
    _house_owner = lambda sign:house.house_owner_from_planet_positions(planet_positions,sign)
    """ Lord of 3rd or 6th in kendra/quadrant """
    md_checks = []
    mc = p_to_h[_house_owner((asc_house+2)%12)] in house.kendra_aspects_of_the_raasi(asc_house) or \
         p_to_h[_house_owner((asc_house+5)%12)] in house.kendra_aspects_of_the_raasi(asc_house)
    md_checks.append(mc)
    """ Two of: lord of 8th, 10th 11th - are powerful """
    eighth_lord = _house_owner((asc_house+7)%12)
    tenth_lord = _house_owner((asc_house+9)%12)
    eleventh_lord = _house_owner((asc_house+10)%12)
    mc = sum([const.house_strengths_of_planets[p][p_to_h[p]] > const._FRIEND for p in [eighth_lord,tenth_lord,eleventh_lord]]) >=2
    md_checks.append(mc)
    """ Mercury, Venus, Jupiter in 2nd/3rd/11th house """
    mc = all([ _relative_house(p_to_h[p]) in [2,3,11] for p in [3,4,5]])
    """ All planets in middle four houses from lagna """
    mc = all([ _relative_house(p_to_h[p]) in [5,6,7,8] for p in const.SUN_TO_SATURN ])
    md_checks.append(mc)
    return md_checks
def life_span_range(jd,place):
    """
        Alpayu = 0; Madhyayu = 1; Poornayu = 2
    """
    def _get_aayu(sign1, sign2):
        if sign1 in const.fixed_signs and sign2 in const.fixed_signs:
            return 0
        elif sign1 in const.movable_signs and sign2 in const.movable_signs:
            return 2
        elif sign1 in const.dual_signs and sign2 in const.dual_signs:
            return 1
        elif (sign1 in const.fixed_signs and sign2 in const.movable_signs) or \
             (sign1 in const.movable_signs and sign2 in const.fixed_signs):
            return 1
        elif (sign1 in const.dual_signs and sign2 in const.movable_signs) or \
             (sign1 in const.movable_signs and sign2 in const.dual_signs):
            return 0
        elif (sign1 in const.fixed_signs and sign2 in const.dual_signs) or \
             (sign1 in const.dual_signs and sign2 in const.fixed_signs):
            return 2
    planet_positions = charts.rasi_chart(jd, place)
    asc_house = planet_positions[0][1][0]; eigth_house = (asc_house+7)%12
    moon_house = planet_positions[2][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    lagna_lord_house = planet_positions[lagna_lord+1][1][0]
    eighth_lord = house.house_owner_from_planet_positions(planet_positions, eigth_house)
    eighth_lord_house = planet_positions[eighth_lord+1][1][0]
    hora_lagna = drik.hora_lagna(jd,place)[0]
    _aayu_group = []
    _aayu_group.append(_get_aayu(lagna_lord_house, eighth_lord_house))
    _aayu_group.append(_get_aayu(asc_house, moon_house))
    _aayu_group.append(_get_aayu(asc_house, hora_lagna))
    import collections
    counter = collections.Counter(_aayu_group)
    #print(counter)
    if len(counter)==1: # All three same
        return counter.keys()[0]
    elif len(counter)==2:# two are same
        return max(counter,key=counter.get)
    else: # all 3 are different
        ret = _aayu_group[-1]
        if moon_house==asc_house or moon_house == (asc_house+6)%12:
            ret = _aayu_group[1]
        return ret
def _jaimini_dhasa_corrections(jd, place, divisional_chart_factor=1):
    """
        NOTE: DO NOT USE. NOT YET IMPLEMENTED
        TODO: Does not consider "hastening effects"
    """
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    print('chart',utils.get_house_planet_list_from_planet_positions(planet_positions))
    year_of_birth,_,_,_ = utils.jd_to_gregorian(jd)
    from math import log
    def _get_reckoning_point():
        reckoning_point = (planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1] + 
                           planet_positions[const.MOON_ID+1][1][0]*30+planet_positions[const.MOON_ID+1][1][1] +
                           22.5)%360
        rec_sign = int(reckoning_point // 30)
        return rec_sign
    def _get_dhasa_lords(parent_sign):
        if parent_sign in const.movable_signs:
            return [(parent_sign + i) % 12 for i in range(12)] # Regular
        if parent_sign in const.fixed_signs:
            return [(parent_sign + const.HOUSE_6 * i) % 12 for i in range(12)] # Every 6th
        out = []
        for g in range(4):
            a = (parent_sign - g) % 12
            out.extend([a, (a + 4) % 12, (a - 4) % 12])
        return out
    def _lord_of(sign, planet_positions):
        # Classical sign lords in these Chara rules (Sc=Mars, Aq=Saturn; nodes not used)
        if sign == const.SCORPIO:  return const.MARS_ID
        if sign == const.AQUARIUS: return const.SATURN_ID
        return const.house_owners[sign]

    def dksen_years_for_sign(sign, use_plain_count=True,            # True = matches 'Analysis' table rows
                             apply_neelakantha_exceptions=True, # Leo/Aq reverse; Ta/Sc direct
                             classical_lords=True):              # Saturn for Aq; Mars for Sc
        """
        Return the DK Sen 'Years' for one period sign.
        Assumes: signs 0..11 = Ar..Pi; const.HOUSE_7 = 6; const.odd_signs={0,2,4,6,8,10}.
        """
        p_to_rasi = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
        lord = _lord_of(sign, planet_positions)  # ensure Saturn for Aq; Mars for Sc
        lh   = p_to_rasi[lord]  # <-- must be a rasi index (0..11), not house-from-Lagna
    
        # Overrides
        if lh == sign:
            return 12
        if lh == (sign + const.HOUSE_7) % 12:
            return 10
    
        # Direction from LORD’s sign parity (odd=>forward, even=>reverse)
        forward = (lh in const.odd_signs)
    
        # Neelakantha / Iranganti exceptions on the LORD's sign (optional)
        if apply_neelakantha_exceptions:
            if lh in {const.LEO, const.AQUARIUS}:    # reverse irrespective of parity
                forward = False
            elif lh in {const.TAURUS, const.SCORPIO}:# direct irrespective of parity
                forward = True
    
        # Distance from LORD -> SIGN in that direction
        steps = (sign - lh) % 12 if forward else (lh - sign) % 12
    
        # Sen's worked table rows use plain count.
        years = steps if use_plain_count else (steps - 1)
    
        # Guard if someone forces minus-one where steps==0
        if years <= 0:
            years = 12
    
        return years
    def _dhasa_duration_dksen(sign, minus_one=True):
        """
        D.K. Sen 'worked example' rule:
          • Direction is decided by the LORD’s sign parity:
                lord in odd  -> forward (zodiacal)
                lord in even -> reverse
          • Count FROM the lord’s sign TO the period sign in that direction.
          • Years = count (Sen’s table), unless minus_one=True (use text variant).
          • Overrides: own -> 12; 7th -> 10.
        """
        # map planets -> houses/signs 0..11
        p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
        lord = _lord_of(sign, planet_positions)      # your existing helper
        lh   = p_to_h[lord]                          # lord’s sign index
        # Overrides first
        if lh == sign:
            return 12
        if lh == (sign + const.HOUSE_7) % 12:
            return 10
        # Direction from LORD’s sign parity (odd={0,2,4,6,8,10} if 0-based Aries..Pisces)
        forward = (lh in const.odd_signs)
        # Count from LORD -> SIGN in that direction
        steps = (sign - lh) % 12 if forward else (lh - sign) % 12
        # Sen’s printed table uses the plain count; the 'text variant' uses count-1
        years = (steps - 1) if minus_one else steps
        # Practical floor/guard: wrap 0 to 12 (should only happen with minus_one=True & adjacency)
        if years <= 0:
            years = 12
        return years
    def _dhasa_duration_jcd_correction(sign):
        p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
        lord = _lord_of(sign, planet_positions)
        lord_house = p_to_h[lord]
        if lord_house == sign: return 12
        if lord_house == (sign + const.HOUSE_7) % 12: return 10
        forward = (sign in const.odd_signs)
        steps = ((lord_house - sign) % 12) if forward else ((sign - lord_house) % 12)
        years = steps if steps != 0 else 12
        return years
    def _dhasa_duration_sum_from_every_8th(dhasa_lords, dhasa_periods):
        dp_sum = {dhasa_lords[0]: dhasa_periods[0]}
        next_house = dhasa_lords[0]
        for h in range(12):
            next_house = (next_house+const.HOUSE_8)%12
            if next_house in dp_sum.keys(): break
            dp_sum[next_house] = dhasa_sum_dict[next_house]
        print('dp_sum',dp_sum)
        dhasa_duration_sum = sum(dp_sum.values())
        return dhasa_duration_sum
    def _get_jcf_correction_years():
        """
        D.K. Sen corrections (Hart page):
          Lagna-side (units = 1.0):
            +1 each if Jupiter or Venus is in {Lagna, 8th, trines from Lagna, trines from 8th}.
            +1 additional if that benefic is also in OWN SIGN (e.g., 'Venus in Asc in own' => +2).
            -1 each if Saturn or Ketu is in the same Lagna-side region.
          Moon-side (units = 0.5):
            Same regions measured from Moon and 8th from Moon; ±0.5 per hit.
          Notes:
            • Pair 3-year special cases exist in Sen’s prose, but Hart’s worked line shows simple linear adds,
              including the own-sign bonus; we follow that precisely.
            • Trines = 5th and 9th from a base.
        Reference: https://saptarishisastrology.com/assassination-or-murder-by-d-k-sen/
        Corrections: Venus in Ascdt. in own-sign(+2y),
                    Jupiter in 8th (+1y), 
                    Ketu in trine from 8th from Ascdt (-1y), 
                    Saturn in trine from Moon(-0.5) -     
                    Total correction = + 1.5
        """
        # --- helpers --------------------------------------------------------------
        def trine_pair(r):
            return {(r + const.HOUSE_5) % 12, (r + const.HOUSE_9) % 12}  # 5th & 9th (0-based)
    
        def region_from(base):
            """ Asc OR 8th OR trines from Asc OR trines from 8th (set of sign indices). """
            h8 = (base + const.HOUSE_8) % 12
            return {base, h8} | trine_pair(base) | trine_pair(h8)
    
        def is_own(planet_id, sign_idx):
            """ True if the planet rules that sign (classical lords only). """
            lord = _lord_of(sign_idx, planet_positions)  # Saturn for Aq; Mars for Sc
            return lord == planet_id
    
        # --- positions & regions --------------------------------------------------
        p_to_rasi = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
        lagna = p_to_rasi[const._ascendant_symbol]
        moon  = p_to_rasi[const.MOON_ID]
    
        lagna_region = region_from(lagna)
        moon_region  = region_from(moon)
    
        # --- Lagna-side (units = 1.0) --------------------------------------------
        jcf = 0.0
        # Benefics: Jupiter, Venus
        if p_to_rasi[const.JUPITER_ID] in lagna_region:
            jcf += 1.0  # +1 for presence
            print("Jupiter in Lagna Region",lagna_region,jcf)
    
        if p_to_rasi[const.VENUS_ID] in lagna_region:
            jcf += 1.0  # +1 for presence
            print('Venus in Lagna Region',lagna_region,jcf)
            if is_own(const.VENUS_ID, p_to_rasi[const.VENUS_ID]):  # “in own-sign (+2)”
                jcf += 1.0
                print('Venus in own sign',jcf)
    
        # Malefics: Saturn, Ketu
        if p_to_rasi[const.SATURN_ID] in lagna_region:
            jcf -= 1.0
            print('Saturn in Lagna Region',lagna_region,jcf)
        if p_to_rasi[const.KETU_ID] in lagna_region:
            jcf -= 1.0
            print('Ketu in Lagna Region',lagna_region,jcf)
    
        # --- Moon-side (units = 0.5) ---------------------------------------------
        if p_to_rasi[const.JUPITER_ID] in moon_region:
            jcf += 0.5
            print("Jupiter in Moon Region",moon_region,jcf)
        if p_to_rasi[const.VENUS_ID] in moon_region:
            jcf += 0.5
            print("Venus in Moon Region",moon_region,jcf)
        if p_to_rasi[const.SATURN_ID] in moon_region:
            jcf -= 0.5  # e.g., “Saturn in trine from Moon (−0.5)”
            print("Saturn in Moon Region",moon_region,jcf)
        if p_to_rasi[const.KETU_ID] in moon_region:
            jcf -= 0.5
            print("Ketu in Moon Region",moon_region,jcf)
    
        return jcf
    
        # --- lagna side (units = 1.0 year) ---------------------------------------
        lagna = p_to_h[const._ascendant_symbol]
        lagna_net = side_units(lagna, 1.0)
    
        # --- moon side (units = 0.5 year) ----------------------------------------
        moon = p_to_h[const.MOON_ID]
        moon_net = side_units(moon, 0.5)
    
        jcf_total = lagna_net + moon_net
        # Optional: verbose debug prints
        # print(f"JCF: lagna={lagna_net:+.1f} yrs, moon={moon_net:+.1f} yrs, total={jcf_total:+.1f} yrs")
        return jcf_total

    rec_sign = _get_reckoning_point()
    dhasa_lords = _get_dhasa_lords(rec_sign)
    print('dhasa_lords',dhasa_lords,[utils.RAASI_LIST[dl] for dl in dhasa_lords])
    """ Dhasa periods should be [9,11,5,7,12,2,1,10,8,1,10,11] """
    #dhasa_periods = [_dhasa_duration_jcd_correction(sign) for sign in dhasa_lords]
    #dhasa_periods = [_dhasa_duration_dksen(sign) for sign in dhasa_lords]
    dhasa_periods = [dksen_years_for_sign(sign) for sign in dhasa_lords]
    dhasa_sum_dict = {dhasa_lords[k]:dhasa_periods[k] for k in range(12)}
    print('dhasa_periods',dhasa_periods,'sum',sum(dhasa_periods)) 
    dhasa_duration = _dhasa_duration_sum_from_every_8th(dhasa_lords,dhasa_periods)
    print('dhasa_duration',dhasa_duration)
    jcf = _get_jcf_correction_years()
    print('jcf',jcf)
    # add corrections to jcd maha dhasa duration
    jcd_corrected_duration = dhasa_duration + jcf
    jcd_corrected_duration_int = int(jcd_corrected_duration)
    print('jcd_corrected_duration',jcd_corrected_duration,'jcd_corrected_duration_int',jcd_corrected_duration_int)
    event_year_1 = int(jcd_corrected_duration_int*nakshathra_year/one_year_days)
    print('event_year_1',event_year_1)
    # Add to year of birth
    event_year_approx = event_year_1 + year_of_birth
    print('event_year_approx',event_year_approx)
    # convert to turns of moon
    jcd_moon_turns =  (event_year_1 * one_year_days / turns_of_moon)
    print('jcd_moon_turns',jcd_moon_turns)
    # Take natural log and add 6 months due to fraction
    jcd_correction_months = round(log(jcd_moon_turns)) + 6
    print('jcd_correction_months',jcd_correction_months)
    yc,mc = divmod(jcd_correction_months,12)
    print('yc,mc',yc,mc)
    event_year, event_month = event_year_approx+yc, mc
    print('event_year, event_month',event_year, event_month)
    event_age = event_year-year_of_birth
    print('event_age',event_age)
    return event_year,event_month

if __name__ == "__main__":
    horoscope_language = 'en' # """ Matplotlib charts available only English"""
    utils.set_language(horoscope_language)
    from jhora.panchanga import drik
    dob = drik.Date(1869,10,2); tob = (8,36,19); place = drik.Place("gandhi",21.64,69.36,5.5)
    #dob = drik.Date(1809,2,12); tob = (6,45,0); place = drik.Place("lincoln",37+34/60+26/3600,-85-44/60-24/3600,-5.0)
    #dob = drik.Date(1917,5,29); tob = (15,0,0); place = drik.Place("lincoln",42+19/60,-71-7/60,-4.0)#Death:1963,11,22
    jd = utils.julian_day_number(dob,tob)
    print(_jaimini_dhasa_corrections(jd,place))
    exit()
