from hora import const,utils
from hora.horoscope.chart import charts, house
from hora.panchanga import drik
chara_method = 1 # 1=> KN Rao method 2=> Parasara Method 3>Rangacharya Method
def _dhasa_duration(planet_positions,sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    #print('dhasa_lord',sign,'lord_of_sign',lord_of_sign,'house_of_lord',house_of_lord,'strength',const.house_strengths_of_planets[lord_of_sign][house_of_lord])
    dhasa_period = 0
    #print('start woth dhasa years 0 - sign lord of sign house of lord dhasa years',sign,lord_of_sign,house_of_lord,dhasa_period)
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        #print(sign,house.rasi_names_en[sign],'even footed counting backward - Step 1',dhasa_period)
        """ Counting is backward if dasa rasi is even-footed."""
        if house_of_lord < sign:
            dhasa_period = sign+1-house_of_lord
            #print('house_of_lord',house_of_lord,'< sign',sign,'dhasa_period',dhasa_period)
        else:
            dhasa_period = sign+13-house_of_lord
            #print('house_of_lord',house_of_lord,'> sign',sign,'dhasa_period',dhasa_period)
    else:
        #print(sign,house.rasi_names_en[sign],'odd footed counting forward - Step -1',dhasa_period)
        """ Counting is forward if dasa rasi is odd-footed."""
        if house_of_lord < sign:
            dhasa_period = house_of_lord+13-sign
            #print('house_of_lord',house_of_lord,'< sign',sign,'dhasa_period',dhasa_period)
        else:
            dhasa_period = house_of_lord+1-sign
            #print('house_of_lord',house_of_lord,'> sign',sign,'dhasa_period',dhasa_period)
    dhasa_period -= 1 # Subtract one from the count
    #print('Step-2 subtract 1 from Step-1', dhasa_period)
    if dhasa_period <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then.
        """
        dhasa_period = 12
        #print('Step-3.1 dhasa_period = 0 set to 12',dhasa_period)
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM : # > const._FRIEND:
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        #print(planet_list[lord_of_sign],'is exhalted in',rasi_names_en[house_of_lord])
        dhasa_period += 1
        #print('Step-3.2 lord exalted add 1',dhasa_period)
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEFIBILATED_NEECHAM:
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
        dhasa_period -= 1
        #print('Step-3.2 lord defibilated minus 1',dhasa_period)
    return dhasa_period
def _antardhasa(dhasas): # KN Rao Method
    return dhasas[1:]+[dhasas[0]]
    
""" CHARA METHODS 2 and 3  - Logic not yet implemented """
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True,
                         chara_method=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    asc_house = planet_positions[0][1][0]
    if chara_method==1:
        seed_house = asc_house
    elif chara_method==3:
        sun_house = planet_positions[1][1][0]
        sh = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, sun_house)
        moon_house = planet_positions[2][1][0]
        seed_house = house.stronger_rasi_from_planet_positions(planet_positions, sh, moon_house)
    ninth_house = (seed_house+8)%12
    dhasa_progression = [(h+seed_house)%12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        dhasa_progression = [(seed_house+12-h)%12 for h in range(12)]
    #print('dhasa_progression',dhasa_progression)
    start_jd = jd_at_dob
    dhasas = []
    for lord in dhasa_progression:
        dd = _dhasa_duration(planet_positions, lord)        
        bhukthis = _antardhasa(dhasa_progression)
        if include_antardhasa:
            ddb = dd/12
            for bhukthi in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasas.append((lord,bhukthi,dhasa_start,ddb))
                start_jd += ddb * const.sidereal_year
                #print(house.rasi_names_en[lord],house.rasi_names_en[bhukthi],dhasa_start)
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasas.append((lord,dhasa_start,dd))
            start_jd += dd * const.sidereal_year
        #print(house.rasi_names_en[lord],dhasa_start)
        start_jd += dd * const.sidereal_year
    return dhasas
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.chara_dhasa_test()