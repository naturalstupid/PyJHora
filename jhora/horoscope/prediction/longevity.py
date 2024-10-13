from hora.horoscope.chart import house, charts
from hora import utils, const
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
    mc = all([ _relative_house(p_to_h[p]) in [5,6,7,8] for p in range(7) ])
    md_checks.append(mc)
    return md_checks
if __name__ == "__main__":
    horoscope_language = 'en' # """ Matplotlib charts available only English"""
    utils.set_language(horoscope_language)
    from hora.horoscope.chart import charts
    from hora.panchanga import drik
    dcf = 1; dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    #dcf = 1; dob = (1964,11,16); tob = (4,30,0); place = drik.Place('Karamadi,India',11.2406,76.9601,5.5)
    #dcf = 1; dob = (1995,1,11); tob = (15,50,37); place = drik.Place('Royapuram,Tamil Nadu,India',13+6/50,80+17/60,5.5)
    jd = utils.julian_day_number(dob, tob)
    print(drik._birthtime_rectification_nakshathra_suddhi(jd, place))
    print('_baladrishta_checks',_baladrishta_checks(jd,place))
    print('_alpayu_checks',_alpayu_checks(jd, place))
    print('_madhyayu_checks',_madhyayu_checks(jd, place))