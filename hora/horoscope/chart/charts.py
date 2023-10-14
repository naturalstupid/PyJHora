from hora.panchanga import drik
from hora import const,utils
divisional_chart_functions = {2:'hora_chart',3:'drekkana_chart',4:'chaturthamsa_chart',5:'panchamsa_chart',
                              6:'shashthamsa_chart',7:'saptamsa_chart',8:'ashtamsa_chart',9:'navamsa_chart',
                              10:'dasamsa_chart',11:'rudramsa_chart',12:'dwadasamsa_chart',16:'shodasamsa_chart',
                              20:'vimsamsa_chart',24:'chaturvimsamsa_chart',27:'nakshatramsa_chart',30:'trimsamsa_chart',
                              40:'khavedamsa_chart',45:'akshavedamsa_chart',60:'shashtyamsa_chart',
                              81:'nava_navamsa_chart',108:'ashtotharamsa_chart',144:'dwadas_dwadasamsa_chart'}
def rasi_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,years=1,months=1,sixty_hours=1):
    """
        Get Rasi chart - D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    #print('rasi chart','years',years,'months',months,'60hrs',sixty_hours)
    jd_years = drik.next_solar_date(jd_at_dob, place_as_tuple, years, months,sixty_hours)
    ascendant_index = const._ascendant_symbol
    drik.set_ayanamsa_mode(ayanamsa_mode)
    " Get Ascendant information"
    ascendant_constellation, ascendant_longitude, _, _ = drik.ascendant(jd_years,place_as_tuple)
    """ FIXED in V2.3.1 - asc long re-calculated to get full longitude value """
    #ascendant_longitude += ascendant_longitude + ascendant_constellation*30 
    #ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor=1)
    #print('ascendant dhasa varga',ascendant_divisional_chart_constellation,ascendant_divisional_chart_longitude)
    " Get planet information "
    " planet_positions lost: [planet_id, planet_constellation, planet_longitude] "
    planet_positions = drik.dhasavarga(jd_years,place_as_tuple,divisional_chart_factor=1)
    #print('planet_positions\n',planet_positions)
    planet_positions = [[ascendant_index,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    #print('planet_positions\n',planet_positions)
    return planet_positions
def hora_chart(planet_positions_in_rasi):
    """ Hora Chart - D2 Chart """
    # Sun's Hora is Leo and Moon's Hora is Cancer
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // 15.0)
        r = 3 # Moon's hora
        if (sign in const.odd_signs and l==0) or (sign in const.even_signs and l==1):
            r = 4 # Sun's Hora
        dp.append([planet,[r,long]])
    return dp
def drekkana_chart(planet_positions_in_rasi):
    """ Drekkana Chart - D3 Chart """
    dp = []
    f1 = 10
    f2 = 4 
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,long]]) # lth position from rasi
    return dp
def chaturthamsa_chart(planet_positions_in_rasi):
    dp = []
    f1 = 7.5
    f2 = 3
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,long]]) # lth position from rasi
    return dp
def panchamsa_chart(planet_positions_in_rasi):
    odd = [0,10,8,2,6]
    even = [1,5,11,9,7]
    f1 = 6
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = even[l]%12
        if sign in const.odd_signs:
            r = odd[l]
        dp.append([planet,[r,long]]) # lth position from rasi
    return dp
def shashthamsa_chart(planet_positions_in_rasi):
    f1 = 5
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12
        if sign in const.even_signs:
            r = (l+6)%12
        dp.append([planet,[r,long]])
    return dp
def saptamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/7
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+l+6)%12
        dp.append([planet,[r,long]])
    return dp
def ashtamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/8
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+4)%12
        elif sign in const.fixed_signs:
            r = (l+8)%12
        dp.append([planet,[r,long]])
    return dp
def navamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/9
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 # fiery sign
        if sign in const.water_signs:
            r = (l+3)%12
        elif sign in const.air_signs:
            r = (l+6)%12
        elif sign in const.earth_signs:
            r = (l+9)%12
        dp.append([planet,[r,long]])
    return dp
def dasamsa_chart(planet_positions_in_rasi):
    f1 = 3.0
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+l+9)%12
        dp.append([planet,[r,long]])
    return dp
def rudramsa_chart(planet_positions_in_rasi):
    f1 = 30.0/11
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = (12+l-sign-1)%12
        dp.append([planet,[r,long]])
    return dp
def dwadasamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/12
    return [[planet,[(int(long//f1)+sign)%12,long]] for planet,[sign,long] in planet_positions_in_rasi]
def shodasamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/16
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+4)%12
        elif sign in const.dual_signs:
            r = (l+8)%12
        dp.append([planet,[r,long]])
    return dp
def vimsamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/20
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+4)%12
        elif sign in const.fixed_signs:
            r = (l+8)%12
        dp.append([planet,[r,long]])
    return dp
def chaturvimsamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/24
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = (l+4)%12 #part from Leo
        if sign in const.even_signs:
            r = (l+3)%12 # Part from Cancer
        dp.append([planet,[r,long]])
    return dp
def nakshatramsa_chart(planet_positions_in_rasi):
    f1 = 30.0/27
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 # fiery sign
        if sign in const.earth_signs:
            r = (l+3)%12 # part from Cancer
        elif sign in const.air_signs:
            r = (l+6)%12
        elif sign in const.water_signs:
            r = (l+9)%12
        dp.append([planet,[r,long]])
    return dp
def trimsamsa_chart(planet_positions_in_rasi):
    odd = [(0,5,0),(5,10,10),(10,18,8),(18,25,2),(25,30,6)]
    even = [(0,5,1),(5,12,5),(12,20,11),(20,25,9),(25,30,7)]
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        if sign in const.odd_signs:
            r = [ rasi%12 for (l_min,l_max,rasi) in odd if (long >= l_min and long <= l_max) ]
        else:
            r = [ rasi%12 for (l_min,l_max,rasi) in even if (long >= l_min and long <= l_max) ]
        dp.append([planet,[r[0],long]]) # lth position from rasi
    return dp
def khavedamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/40
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 #part from Aries
        if sign in const.even_signs:
            r = (l+5)%12 # Part from Libra
        dp.append([planet,[r,long]])
    return dp
def akshavedamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/45
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+4)%12
        elif sign in const.dual_signs:
            r = (l+8)%12
        dp.append([planet,[r,long]])
    return dp
def shashtyamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/60
    return [[planet,[(int(long//f1)+sign)%12,long]] for planet,[sign,long] in planet_positions_in_rasi]
def nava_navamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/81
    return [[planet,[(int(long//f1)+sign)%12,long]] for planet,[sign,long] in planet_positions_in_rasi]
def ashtotharamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/108
    return [[planet,[(int(long//f1)+sign)%12,long]] for planet,[sign,long] in planet_positions_in_rasi]
def dwadas_dwadasamsa_chart(planet_positions_in_rasi):
    f1 = 30.0/144
    return [[planet,[(int(long//f1)+sign)%12,long]] for planet,[sign,long] in planet_positions_in_rasi]
def divisional_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    """
        Get division chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
    """
    planet_positions = rasi_chart(jd_at_dob, place_as_tuple, ayanamsa_mode,years,months,sixty_hours)
    #print('divisional chart','years',years,'months',months,'60hrs',sixty_hours)
    if divisional_chart_factor==1:
        return planet_positions
    else:
        if divisional_chart_factor in divisional_chart_functions.keys():
            return eval(divisional_chart_functions[divisional_chart_factor]+'(planet_positions)')
        else:
            print('Chart division factor',divisional_chart_factor,'not supported')
            return None
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
def dhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
    planet_dhasamsa = [0 for p in range(9)]
    for di, _world_city_db_df in enumerate(const.dhasavarga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=_world_city_db_df)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_dhasamsa[p] += 1
    return planet_dhasamsa
def shadvarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
    planet_shadamsa = [0 for p in range(9)]
    for di, _world_city_db_df in enumerate(const.shadvarga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=_world_city_db_df)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_shadamsa[p] += 1
    return planet_shadamsa
def sapthavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
    planet_sapthamsa = [0 for p in range(9)]
    for di, _world_city_db_df in enumerate(const.sapthavarga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=_world_city_db_df)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                planet_sapthamsa[p] += 1
    return planet_sapthamsa
def shodhasavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    planet_shodhasamsa = [0 for p in range(9)]
    for di, _world_city_db_df in enumerate(const.shodhasa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=_world_city_db_df)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(_world_city_db_df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_shodhasamsa[p] += 1
    return planet_shodhasamsa
def vimsamsavarga_of_planets(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    """
        Get the count - in how many vimsamsa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
    planet_vimsamsa = [0 for p in range(9)]
    for di, _world_city_db_df in enumerate(const.vimsamsa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=_world_city_db_df)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(_world_city_db_df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_vimsamsa[p] += 1
    return planet_vimsamsa
if __name__ == "__main__":
    dob = drik.Date(1967,3,8)
    tob = (17,40,0)
    lat=26+18.0/60
    lon=73+4/60.0
    tz = 5.5
    place = drik.Place('unknown',lat,lon,tz)
    jd = utils.julian_day_number(dob,tob)
    pr = rasi_chart(jd, place)
    pp = divisional_chart(jd, place, divisional_chart_factor=1)
    jdy = jd + 10*const.sidereal_year
    py = divisional_chart(jdy, place, divisional_chart_factor=1)
    jdy = jd + 10*const.average_gregorian_year
    py1 = divisional_chart(jdy, place, divisional_chart_factor=1)
    print(pr)
    print(pp)
    print(py)
    print(py1)
    exit()
    for d in const.division_chart_factors:
        pp = divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=d)
        if pp==None:
            break
        if d==1:
            print('D-'+str(d),'rasi chart',pp)
        else:
            print('D-'+str(d),divisional_chart_functions[d],pp)
    exit()
    pr = rasi_chart(jd, place)
    print('rasi',pr)
    pd = drekkana_chart(pr)
    print('drekkana',pd)
    pd = chaturthamsa_chart(pr)
    print('chaturthamsa',pd)
    pd = panchamsa_chart(pr)
    print('panchamsa_chart',pd)
    pd = shashthamsa_chart(pr)
    print('shashthamsa_chart',pd)
    pd = saptamsa_chart(pr)
    print('saptamsa_chart',pd)
    pd = ashtamsa_chart(pr)
    print('ashtamsa_chart',pd)
    pd = navamsa_chart(pr)
    print('navamsa_chart',pd)
    pd = dasamsa_chart(pr)
    print('dasamsa_chart',pd)
    pd = rudramsa_chart(pr)
    print('rudramsa_chart',pd)
    pd = dwadasamsa_chart(pr)
    print('dwadasammsa_chart',pd)
    pd = shodasamsa_chart(pr)
    print('shodasamsa_chart',pd)
    pd = vimsamsa_chart(pr)
    print('vimsasamsa_chart',pd)
    pd = chaturvimsamsa_chart(pr)
    print('chaturvimsamsa_chart',pd)
    pd = nakshatramsa_chart(pr)
    print('nakshatramsa_chart',pd)
    pd = trimsamsa_chart(pr)
    print('trimsamsa_chart',pd)
    pd = khavedamsa_chart(pr)
    print('khavedamsa_chart',pd)
    pd = akshavedamsa_chart(pr)
    print('akshavedamsa_chart',pd)
    pd = shashtyamsa_chart(pr)
    print('shashtyamsa_chart',pd)
    exit()
    " Rajiv Gandhi"
    dob = (1944,8,20)
    tob = (7,11,40)
    lat = 18.0+59.0/60
    lon = 72.0+49.0/60
    tz = 5.5
    tob_in_hours = tob[0]+tob[1]/60.0+tob[2]/3600.0
    place = drik.Place('unknown',lat,lon,tz)
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
