from hora.panchanga import panchanga
from hora import const,utils

def divisional_chart(jd_at_dob,place_as_tuple,ayanamsa_mode='Lahiri',divisional_chart_factor=1):
    ascendant_index = 'L'
    panchanga.set_ayanamsa_mode(ayanamsa_mode)
    " Get Ascendant information"
    ascendant_constellation, ascendant_longitude, asc_nak_no, asc_paadha_no = panchanga.ascendant(jd_at_dob,place_as_tuple)
    #print('ascendant rasi',ascendant_constellation,ascendant_longitude)
    ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude = panchanga.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    #print('ascendant dhasa varga',ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude)
    " Get planet information "
    " planet_positions lost: [planet_id, planet_constellation, planet_longitude] "
    planet_positions = panchanga.dhasavarga(jd_at_dob,place_as_tuple,divisional_chart_factor)
    #print('planet_positions\n',planet_positions)
    planet_positions = [[ascendant_index,(ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude)]] + planet_positions
    #print('planet_positions\n',planet_positions)
    return planet_positions
def planets_in_retrograde(planet_positions):
    retrograde_planets = []
    sun_house = planet_positions[1][1][0]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    for p,(h,p_long) in planet_positions[3:8]: # Exclude Lagna, Sun,Moon,, Rahu and Ketu
        planet_house = planet_positions[p+1][1][0]
        planet_long = h*30+p_long
        if p == 2:
            if planet_house in [(sun_house+h-1)%12 for h in [*range(6,9)]]: # 6 to 8th house of sun
                retrograde_planets.append(p)            
        elif p == 3:
            if planet_long > sun_long-20 and planet_long < sun_long+20:
                retrograde_planets.append(p)
        elif p == 4:
            if planet_house in [(sun_house+h-1)%12 for h in [*range(5,10)]]: # 5 to 9th house of sun
                retrograde_planets.append(p)            
        elif p == 5:
            if planet_long > sun_long-30 and planet_long < sun_long+30:
                retrograde_planets.append(p)
        elif p == 6:
            if planet_house in [(sun_house+h-1)%12 for h in [*range(4,11)]]: # 4 to 10th house of sun
                retrograde_planets.append(p)
    return retrograde_planets
def planets_in_combustion(planet_positions):
    retrograde_planets = planets_in_retrograde(planet_positions) 
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    combustion_planets = []
    for p,(_,p_long) in planet_positions[2:8]: # Exclude Lagna, Sun, Rahu and Ketu
        combustion_range = const.combustion_range_of_planets_from_sun
        if p in retrograde_planets: 
            combustion_range = const.combustion_range_of_planets_from_sun_while_in_retrogade
        if p_long >= sun_long-combustion_range[p-2] and p_long <= sun_long+combustion_range[p-2]:
            combustion_planets.append(p)
    return combustion_planets
def dhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri'):
    """
    Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
    Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
    Sreedhaamaamsa – 10.
    """
    planet_dhasamsa = [0 for p in range(9)]
    for di, df in enumerate(const.dhasa_varga_amasa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=df)
        for p,(h,_) in planet_positions:
            if p == 'L':
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_dhasamsa[p] += 1
    return planet_dhasamsa
def shadvarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri'):
    """
    Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
    planet_shadamsa = [0 for p in range(9)]
    for di, df in enumerate(const.shadvarga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=df)
        for p,(h,_) in planet_positions:
            if p == 'L':
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_shadamsa[p] += 1
    return planet_shadamsa
def sapthavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri'):
    """
    Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
    planet_sapthamsa = [0 for p in range(9)]
    for di, df in enumerate(const.sapthavarga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=df)
        for p,(h,_) in planet_positions:
            if p == 'L':
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_sapthamsa[p] += 1
    return planet_sapthamsa
def shodhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri'):
    """
    Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
    Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
    Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
    Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    planet_shodhasamsa = [0 for p in range(9)]
    for di, df in enumerate(const.shodhasa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=df)
        for p,(h,_) in planet_positions:
            if p == 'L':
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_shodhasamsa[p] += 1
    return planet_shodhasamsa
def vimsamsavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri'):
    """
    Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
    Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
    Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
    Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    planet_vimsamsa = [0 for p in range(9)]
    for di, df in enumerate(const.vimsamsa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=df)
        for p,(h,_) in planet_positions:
            if p == 'L':
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_vimsamsa[p] += 1
    return planet_vimsamsa
if __name__ == "__main__":
    dob = panchanga.Date(1967,3,8)
    tob = (17,40,0)
    lat=73+4/60.0
    lon=26+18.0/60
    tz = 5.5
    " Rajiv Gandhi"
    dob = (1944,8,20)
    tob = (7,11,40)
    lat = 18.0+59.0/60
    lon = 72.0+49.0/60
    tz = 5.5
    tob_in_hours = tob[0]+tob[1]/60.0+tob[2]/3600.0
    place = panchanga.Place('unknown',lat,lon,tz)
    jd = panchanga.julian_day_number(dob,tob)
    planet_dhasamsa = vimsamsavarga_of_planets(jd, place)
    print(planet_dhasamsa)
    exit()
    pp = divisional_chart(jd,place, divisional_chart_factor=60)
    for p,(h,_) in pp[1:]:
        print(p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h])
    exit()
    print(pp)
    print(planets_in_retrograde(pp))
    h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
    print(h_to_p)
