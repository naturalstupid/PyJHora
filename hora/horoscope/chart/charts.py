from hora.panchanga import drik
from hora import const,utils
from hora.horoscope.chart import house
_hora_chart_by_pvr_method = True
divisional_chart_functions = {2:'hora_chart',3:'drekkana_chart',4:'chaturthamsa_chart',5:'panchamsa_chart',
                              6:'shashthamsa_chart',7:'saptamsa_chart',8:'ashtamsa_chart',9:'navamsa_chart',
                              10:'dasamsa_chart',11:'rudramsa_chart',12:'dwadasamsa_chart',16:'shodasamsa_chart',
                              20:'vimsamsa_chart',24:'chaturvimsamsa_chart',27:'nakshatramsa_chart',30:'trimsamsa_chart',
                              40:'khavedamsa_chart',45:'akshavedamsa_chart',60:'shashtyamsa_chart',
                              81:'nava_navamsa_chart',108:'ashtotharamsa_chart',144:'dwadas_dwadasamsa_chart'}
def rasi_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,years=1,months=1,sixty_hours=1
               ,calculation_type='drik'):
    """
        Get Rasi chart - D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    #print('rasi chart','years',years,'months',months,'60hrs',sixty_hours)
    jd_years = drik.next_solar_date(jd_at_dob, place_as_tuple, years, months,sixty_hours)
    if calculation_type.lower()=='ss':
        from hora.panchanga import surya_sidhantha
        return surya_sidhantha.planet_positions(jd_years, place_as_tuple)
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
def bhava_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,years=1,months=1,sixty_hours=1
                ,calculation_type='drik'):
    """
        Get Bhava chart from Rasi / D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    planet_positions = rasi_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, years, months, sixty_hours,
                                  calculation_type=calculation_type)
    #print('rasi planet positions',planet_positions)
    asc_house = planet_positions[0][1][0]
    asc_long = planet_positions[0][1][1]
    asc_start = asc_long - 15.0
    asc_end = asc_long + 15.0
    pp_bhava = {}
    if asc_start < 0:
        pp_bhava['L']=asc_house-1
        for p,(h,long) in planet_positions[1:]:
            pp_bhava[p]=h
            if long > asc_end:
                pp_bhava[p]=(h + 1)%12
    else:
        pp_bhava['L']=asc_house
        for p,(h,long) in planet_positions[1:]:
            pp_bhava[p]=h
            if long < asc_start:
                pp_bhava[p]=(h - 1)%12
    return pp_bhava
def _hora_chart_pvr_method(planet_positions_in_rasi):
    """ Hora Chart - D2 Chart PV Narasimha Rao Method"""
    dvf = 2
    hora_list = [(0,0,0),(0,1,1),(1,1,2),(1,0,3),(2,0,4),(2,1,5),(3,1,6),(3,0,7),(4,0,8),(4,1,9),(5,1,10),(5,0,11),
                 (6,0,0),(6,1,1),(7,1,2),(7,0,3),(8,0,4),(8,1,5),(9,1,6),(9,0,7),(10,0,8),(10,1,0),(11,1,10),(11,0,11)]
    hora_sign = lambda r,h: [s1 for r1,h1,s1 in hora_list if r1==r and h1==h][0]
    dp = []
    for planet,[rasi_sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        hora = int(long // 15.0)
        dp.append([planet,[hora_sign(rasi_sign,hora),d_long]])
    return dp
def hora_chart(planet_positions_in_rasi,pvn_rao_method=_hora_chart_by_pvr_method):
    """ 
        Hora Chart - D2 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 2
    if pvn_rao_method:
        return _hora_chart_pvr_method(planet_positions_in_rasi)
    # Sun's Hora is Leo and Moon's Hora is Cancer
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // 15.0)
        r = 3 # Moon's hora
        if (sign in const.odd_signs and l==0) or (sign in const.even_signs and l==1):
            r = 4 # Sun's Hora
        dp.append([planet,[r,d_long]])
    return dp
def drekkana_chart(planet_positions_in_rasi):
    """ 
        Drekkana Chart - D3 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 3
    dp = []
    f1 = 10
    f2 = 4 
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,d_long]]) # lth position from rasi
    return dp
def chaturthamsa_chart(planet_positions_in_rasi):
    """ 
        Chaturthamsa Chart - D4 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 4
    dp = []
    f1 = 7.5
    f2 = 3
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        dp.append([planet,[(sign+l*f2)%12,d_long]]) # lth position from rasi
    return dp
def panchamsa_chart(planet_positions_in_rasi):
    """ 
        Panchamsa Chart - D5 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 5
    odd = [0,10,8,2,6]
    even = [1,5,11,9,7]
    f1 = 6
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = even[l]%12
        if sign in const.odd_signs:
            r = odd[l]
        dp.append([planet,[r,d_long]]) # lth position from rasi
    return dp
def shashthamsa_chart(planet_positions_in_rasi):
    """ 
        Shashthamsa Chart - D6 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 6
    f1 = 5
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12
        if sign in const.even_signs:
            r = (l+6)%12
        dp.append([planet,[r,d_long]])
    return dp
def saptamsa_chart(planet_positions_in_rasi):
    """ 
        Saptamsa Chart - D7 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 7
    f1 = 30.0/7
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+l+6)%12
        dp.append([planet,[r,d_long]])
    return dp
def ashtamsa_chart(planet_positions_in_rasi):
    """ 
        Ashtamsa Chart - D8 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 8
    f1 = 30.0/8
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+4)%12
        elif sign in const.fixed_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def navamsa_chart(planet_positions_in_rasi):
    """ 
        Navamsa Chart - D9 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 9
    f1 = 30.0/9
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # fiery sign
        if sign in const.water_signs:
            r = (l+3)%12
        elif sign in const.air_signs:
            r = (l+6)%12
        elif sign in const.earth_signs:
            r = (l+9)%12
        dp.append([planet,[r,d_long]])
    return dp
def dasamsa_chart(planet_positions_in_rasi):
    """ 
        Dasamsa Chart - D10 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 10
    f1 = 3.0
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (sign+l)%12
        if sign in const.even_signs:
            r = (sign+l+9)%12
        dp.append([planet,[r,d_long]])
    return dp
def rudramsa_chart(planet_positions_in_rasi):
    """ 
        Rudramsa Chart - D11 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 11
    f1 = 30.0/11
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (12+l-sign-1)%12
        dp.append([planet,[r,d_long]])
    return dp
def dwadasamsa_chart(planet_positions_in_rasi):
    """ 
        Dwadasamsa Chart - D12 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 12
    f1 = 30.0/12
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def shodasamsa_chart(planet_positions_in_rasi):
    """ 
        Shodasamsa Chart - D16 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 16
    f1 = 30.0/16
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+4)%12
        elif sign in const.dual_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def vimsamsa_chart(planet_positions_in_rasi):
    """ 
        Vimsamsa Chart - D20 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 20
    f1 = 30.0/20
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.dual_signs:
            r = (l+4)%12
        elif sign in const.fixed_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def chaturvimsamsa_chart(planet_positions_in_rasi):
    """ 
        Chathur Vimsamsa Chart - D24 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 24
    f1 = 30.0/24
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = (l+4)%12 #part from Leo
        if sign in const.even_signs:
            r = (l+3)%12 # Part from Cancer
        dp.append([planet,[r,d_long]])
    return dp
def nakshatramsa_chart(planet_positions_in_rasi):
    """ 
        Nakshatramsa Chart - D27 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 27
    f1 = 30.0/27
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # fiery sign
        if sign in const.earth_signs:
            r = (l+3)%12 # part from Cancer
        elif sign in const.air_signs:
            r = (l+6)%12
        elif sign in const.water_signs:
            r = (l+9)%12
        dp.append([planet,[r,d_long]])
    return dp
def trimsamsa_chart(planet_positions_in_rasi):
    """ 
        Trimsamsa Chart - D30 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 30
    odd = [(0,5,0),(5,10,10),(10,18,8),(18,25,2),(25,30,6)]
    even = [(0,5,1),(5,12,5),(12,20,11),(20,25,9),(25,30,7)]
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        if sign in const.odd_signs:
            r = [ rasi%12 for (l_min,l_max,rasi) in odd if (long >= l_min and long <= l_max) ]
        else:
            r = [ rasi%12 for (l_min,l_max,rasi) in even if (long >= l_min and long <= l_max) ]
        dp.append([planet,[r[0],d_long]]) # lth position from rasi
    return dp
def khavedamsa_chart(planet_positions_in_rasi):
    """ 
        Khavedamsa Chart - D40 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 40
    f1 = 30.0/40
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 #part from Aries
        if sign in const.even_signs:
            r = (l+5)%12 # Part from Libra
        dp.append([planet,[r,d_long]])
    return dp
def akshavedamsa_chart(planet_positions_in_rasi):
    """ 
        Akshavedamsa Chart - D45 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 45
    f1 = 30.0/45
    dp = []
    for planet,[sign,long] in planet_positions_in_rasi:
        d_long = (long*dvf)%30
        l = int(long // f1)
        r = l%12 # movable sign
        if sign in const.fixed_signs:
            r = (l+4)%12
        elif sign in const.dual_signs:
            r = (l+8)%12
        dp.append([planet,[r,d_long]])
    return dp
def shashtyamsa_chart(planet_positions_in_rasi):
    """ 
        Shashtyamsa Chart - D60 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 60
    f1 = 30.0/60
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def nava_navamsa_chart(planet_positions_in_rasi):
    """ 
        Nava Navamsa Chart - D81 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 81
    f1 = 30.0/81
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def ashtotharamsa_chart(planet_positions_in_rasi):
    """ 
        Ashtotharamsa Chart - D108 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 108
    f1 = 30.0/108
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def dwadas_dwadasamsa_chart(planet_positions_in_rasi):
    """ 
        Dwadas Dwadasamsa Chart - D144 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
    dvf = 144
    f1 = 30.0/144
    return [[planet,[(int(long//f1)+sign)%12,(long*dvf)%30]] for planet,[sign,long] in planet_positions_in_rasi]
def divisional_chart(jd_at_dob,place_as_tuple,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,
                     years=1,months=1,sixty_hours=1,calculation_type='drik'):
    """
        Get divisional/varga chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
    """
    planet_positions = rasi_chart(jd_at_dob, place_as_tuple, ayanamsa_mode,years,months,sixty_hours,calculation_type=calculation_type)
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
def _planets_in_retrograde_old(planet_positions):
    """ TODO: CHECK IF this algorithm is correct 
        Retired from V3.0.0 """
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
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(6,9)]]: # 6 to 8th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(6,9)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'6-8')
                retrograde_planets.append(p)            
        elif p == 3:
            if planet_long > sun_long-20 and planet_long < sun_long+20:
                #print('planet',p,'planet_long',planet_long,sun_long-20,sun_long+20)
                retrograde_planets.append(p)
        elif p == 4:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(5,10)]]: # 5 to 9th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(5,10)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'5-9')
                retrograde_planets.append(p)            
        elif p == 5:
            if planet_long > sun_long-30 and planet_long < sun_long+30:
                #print('planet',p,'planet_long',planet_long,sun_long-30,sun_long+30)
                retrograde_planets.append(p)
        elif p == 6:
            #if planet_house in [(sun_house+h-1)%12 for h in [*range(4,11)]]: # 4 to 10th house of sun
            if house.get_relative_house_of_planet(sun_house,planet_house) in [*range(4,11)]:
                #print('planet',p,'planet_house',planet_house,'sun_house',sun_house,'relative house from sun',house.get_relative_house_of_planet(sun_house,planet_house),'4-10')
                retrograde_planets.append(p)
    return retrograde_planets
def planets_in_retrograde(planet_positions):
    """ TODO: This is New Attempt from V3.0.0 onwards 
        based on vakragathi - wikipedia ranges
    """
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
    """
    if const.planet_retrogression_calculation_method == 1:
        return _planets_in_retrograde_old(planet_positions)
    retrograde_planets = []
    sun_house = planet_positions[1][1][0]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    for p,(h,p_long) in planet_positions[3:8]: # Exclude Lagna, Sun,Moon,, Rahu and Ketu
        planet_house = h
        planet_long = h*30+p_long
        p_long_from_sun_1 = (sun_long+360+const.planets_retrograde_limits_from_sun[p][0])%360
        p_long_from_sun_2 = (sun_long+360+const.planets_retrograde_limits_from_sun[p][1])%360
        if p_long_from_sun_2 < p_long_from_sun_1:
            p_long_from_sun_2 += 360.
        if planet_long > p_long_from_sun_1 and planet_long < p_long_from_sun_2:
            #print(p,'sun_long',sun_long,'planet_long',planet_long,'is in range?',p_long_from_sun_1,p_long_from_sun_2)
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
def _amsa_bala_of_planets(jd_at_dob, place_as_tuple,amsa_vimsopaka):
    p_d = [0 for _ in range(9)]
    p_d_s = [0 for _ in range(9)]
    p_d_c = ['' for _ in range(9)]
    scores = [5,7,10,15,18]
    for dcf in amsa_vimsopaka.keys():
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple,divisional_chart_factor=dcf)
        h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
        if dcf == 1:
            cr = house._get_compound_relationships_of_planets(h_to_p)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                p_d[p] += 1
                p_d_c[p] += 'D'+str(dcf)+'/'
            if const.house_strengths_of_planets[p][h]==const._OWNER_RULER:
                vv = 20
            else:
                d = const.house_owners[h]
                vv = scores[cr[p][d]]
            p_d_s[p] += amsa_vimsopaka[dcf]*vv/20
    pdc = {}
    for p in range(9):
        p_d_c[p] = p_d_c[p][:-1]
        pdc[p] = [p_d[p],p_d_c[p],p_d_s[p]]
        #print(house.planet_list[p],pdc[p])
    return pdc
    
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
    return _amsa_bala_of_planets(jd_at_dob, place_as_tuple,const.dhasavarga_amsa_vimsopaka)
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
    return _amsa_bala_of_planets(jd_at_dob, place_as_tuple,const.shadvarga_amsa_vimsopaka)
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
    return _amsa_bala_of_planets(jd_at_dob, place_as_tuple,const.sapthavarga_amsa_vimsopaka)
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
    return _amsa_bala_of_planets(jd_at_dob, place_as_tuple,const.shodhasa_varga_amsa_vimsopaka)
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
    for di, dcf in enumerate(const.vimsamsa_varga_amsa_factors):
        planet_positions = divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode, divisional_chart_factor=dcf)
        for p,(h,_) in planet_positions:
            if p == const._ascendant_symbol:
                continue
            elif h==const.moola_trikona_of_planets[p] or const.house_strengths_of_planets[p][h] > const._FRIEND:
                #print('D'+str(_world_city_db_df),p,h,const.moola_trikona_of_planets[p],const.house_strengths_of_planets[p][h],di+1)
                planet_vimsamsa[p] += 1
    return planet_vimsamsa
def varnada_lagna(dob,tob,place):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = rasi_chart(jd_at_dob, place)
    lagna = planet_positions[0][1][0]
    count1 = (12-lagna)
    lagna_is_odd = False
    if lagna in const.odd_signs:
        count1 = lagna + 1 # Count from Mesha/Pisces to Lagna
        lagna_is_odd = True
    hora_lagna,hl = drik.hora_lagna(jd_at_dob,place,utils.from_dms(dob[0],dob[1],dob[2]))
    count2 = (12-hora_lagna)
    hora_lagna_is_odd = False
    if hora_lagna in const.odd_signs:
        count2 = hora_lagna + 1 # Count from Mesha/Pisces to Lagna
        hora_lagna_is_odd = True
    if (hora_lagna_is_odd and lagna_is_odd) or (not hora_lagna_is_odd and not lagna_is_odd):
        count = count1 + count2
    else:
        count = max(count1,count2) - min (count1,count2)
    _varnada_lagna = (12-count)
    if lagna in const.odd_signs:
        _varnada_lagna = count
    return _varnada_lagna, hl
def benefics_and_malefics(jd,place,method=2):
    """
        From BV Raman - Hindu Predictive Astrology - METHOD=1
        Jupiter. Venus. Full Moon and well-associated Mercury are benefics. 
        New Moon, badly associated Mercury. the Sun, Saturn, Mars, Rabu and Ketu are malefics
        From the eighth day of the bright half of the lunar month the Moon is full and strong.
        She is weak from the eighth day of the dark half.
        From PVR Narasimha Rao - Intergrated Vedic Astrology - METHOD=2
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
            Mercury becomes a natural benefic when he is alone or with more natural
            benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
            Mercury becomes a natural malefic when he is joined by more natural malefics.
            Waning Moon of Krishna paksha is a natural malefic.
    """
    benefics = const.natural_benefics[:] ; malefics = const.natural_malefics[:]
    _tithi = drik.tithi(jd, place)[0]
    if _tithi > 15:
        malefics.append(1)
    else:
        benefics.append(1)
    from hora.horoscope.chart import house, charts
    planet_positions = charts.rasi_chart(jd, place)
    m_assn = any([planet_positions[4][1][0]==planet_positions[m+1][1][0] for m in const.natural_malefics])
    if m_assn: malefics.append(3)
    b_assn = any([planet_positions[4][1][0]==planet_positions[b+1][1][0] for b in const.natural_benefics])
    if b_assn: benefics.append(3)
    benefics = sorted(benefics) ; malefics = sorted(malefics)
    return benefics, malefics
def benefics(jd,place,method=2):
    """
        From BV Raman - Hindu Predictive Astrology - METHOD=1
        Jupiter. Venus. Full Moon and well-associated Mercury are benefics. 
        New Moon, badly associated Mercury. the Sun, Saturn, Mars, Rabu and Ketu are malefics
        From the eighth day of the bright half of the lunar month the Moon is full and strong.
        She is weak from the eighth day of the dark half.
        From PVR Narasimha Rao - Intergrated Vedic Astrology - METHOD=2
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
            Mercury becomes a natural benefic when he is alone or with more natural
            benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
            Mercury becomes a natural malefic when he is joined by more natural malefics.
            Waning Moon of Krishna paksha is a natural malefic.
    """
    return benefics_and_malefics(jd, place, method=method)[0]
def malefics(jd,place,method=2):
    """
        From BV Raman - Hindu Predictive Astrology - METHOD=1
        Jupiter. Venus. Full Moon and well-associated Mercury are benefics. 
        New Moon, badly associated Mercury. the Sun, Saturn, Mars, Rabu and Ketu are malefics
        From the eighth day of the bright half of the lunar month the Moon is full and strong.
        She is weak from the eighth day of the dark half.
        From PVR Narasimha Rao - Intergrated Vedic Astrology - METHOD=2
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
            Mercury becomes a natural benefic when he is alone or with more natural
            benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
            Mercury becomes a natural malefic when he is joined by more natural malefics.
            Waning Moon of Krishna paksha is a natural malefic.
    """
    return benefics_and_malefics(jd, place, method=method)[1]
if __name__ == "__main__":
    utils.set_language('en')
    dob = (1996,12,7)
    #dob = (1995,1,11)
    #dob = (1996,11,5)
    #dob = (2023,9,5)
    tob = (10,34,0)
    #tob = (15,50,37)
    #tob = (11,45,0)
    place = drik.Place('Chennai',13.0878,80.2785,5.5)
    #place = drik.Place('Royapuram',13+6/60,80+17/60,5.5)
    #place = drik.Place('New Brunswick,NJ,USA',40+29/60,-74-27/60,-5.0)
    jd = utils.julian_day_number(dob, tob)
    print(benefics_and_malefics(jd, place))
    exit()
    pp = rasi_chart(jd, place)
    const.planet_retrogression_calculation_method = 1
    print(planets_in_retrograde(pp))
    const.planet_retrogression_calculation_method = 2
    print(planets_in_retrograde(pp))
    exit()
    print(bhava_chart(jd, place))
    exit()
    vl = varnada_lagna(dob, tob, place)
    print(house.rasi_names_en[vl[0]],utils.to_dms(vl[1],is_lat_long='plong'))
    exit()
    from hora.tests.pvr_tests import test_example
    def amsa_bala_test_1():
        exercise = 'Example from Internet '
        dob = drik.Date(1769,8,15)
        tob = (11,30,0)
        lat=41.9192
        lon=8.7386
        tz = 2.0
        place = drik.Place('Chandigarh',lat,lon,tz)
        jd_at_dob = utils.julian_day_number(dob, tob)
        pp = rasi_chart(jd_at_dob, place)
        h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
        sv1 = shadvarga_of_planets(jd_at_dob, place)
        for p in range(9):
            if sv1[p][0] > 1:
                test_example(exercise+' Shad varga of '+house.planet_list[p],sv1[p][0],sv1[p][0],utils.SHADVARGAMSA_NAMES[sv1[p][0]],sv1[p][1],'Score',sv1[p][2])
    def amsa_bala_test_2():
        exercise = 'Chandigarh Example from Internet '
        dob = drik.Date(1981,9,18)
        tob = (16,12,27)
        lat=30.7333
        lon=76.7794
        tz = 5.5
        place = drik.Place('Chandigarh',lat,lon,tz)
        jd_at_dob = utils.julian_day_number(dob, tob)
        pp = rasi_chart(jd_at_dob, place)
        h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
        sv1 = shadvarga_of_planets(jd_at_dob, place)
        for p in range(9):
            if sv1[p][0] > 1:
                test_example(exercise+' Shad varga of '+house.planet_list[p],sv1[p][0],sv1[p][0],utils.SHADVARGAMSA_NAMES[sv1[p][0]],sv1[p][1],'Score',sv1[p][2])
    utils.set_language('ta')
    amsa_bala_test_1()
    amsa_bala_test_2()
    exit()
