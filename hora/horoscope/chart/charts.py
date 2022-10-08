from hora.panchanga import panchanga
from hora import const,utils

def divisional_chart(jd_at_dob,place_as_tuple,ayanamsa_mode='Lahiri',divisional_chart_factor=1):
    """
        Get division chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
    """
    ascendant_index = 'L'
    panchanga.set_ayanamsa_mode(ayanamsa_mode)
    " Get Ascendant information"
    _, ascendant_longitude, _, _ = panchanga.ascendant(jd_at_dob,place_as_tuple)
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
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
    """
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
    """
        Get the list of planets that are in combustion - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in combustion 
    """
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
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
    planet_dhasamsa = [0 for p in range(9)]
    for di, df in enumerate(const.dhasavarga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=df)
        for p,(h,_) in planet_positions:
            if p == 'L':
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_dhasamsa[p] += 1
    return planet_dhasamsa
def shadvarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri'):
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
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
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
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
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
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
        Get the count - in how many vimsamsa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
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
    jd = utils.julian_day_number(dob,tob)
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
