from hora import const,utils
from hora.horoscope.chart import charts, house
import swisseph as swe
from hora.panchanga import drik
rasi_names_en = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
def _dhasa_duration(p_to_h,sign):
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    lord_of_sign = house.house_owner(h_to_p,sign)
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_years = 0
    #print('start woth dhasa years 0 - sign lord of sign house of lord dhasa years',sign,lord_of_sign,house_of_lord,dhasa_years)
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        #print(sign,house.rasi_names_en[sign],'even footed counting backward - Step 1',dhasa_years)
        """ Counting is backward if dasa rasi is even-footed."""
        if house_of_lord < sign:
            dhasa_years = sign+1-house_of_lord
            #print('house_of_lord',house_of_lord,'< sign',sign,'dhasa years',dhasa_years)
        else:
            dhasa_years = sign+13-house_of_lord
            #print('house_of_lord',house_of_lord,'> sign',sign,'dhasa years',dhasa_years)
    else:
        #print(sign,house.rasi_names_en[sign],'odd footed counting forward - Step -1',dhasa_years)
        """ Counting is forward if dasa rasi is odd-footed."""
        if house_of_lord < sign:
            dhasa_years = house_of_lord+13-sign
            #print('house_of_lord',house_of_lord,'< sign',sign,'dhasa years',dhasa_years)
        else:
            dhasa_years = house_of_lord+1-sign
            #print('house_of_lord',house_of_lord,'> sign',sign,'dhasa years',dhasa_years)
    dhasa_years -= 1 # Subtract one from the count
    #print('Step-2 subtract 1 from Step-1', dhasa_years)
    if dhasa_years <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then.
        """
        dhasa_years = 12
        #print('Step-3.1 dhasa_years = 0 set to 12',dhasa_years)
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM : # > const._FRIEND:
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        #print(planet_list[lord_of_sign],'is exhalted in',rasi_names_en[house_of_lord])
        dhasa_years += 1
        #print('Step-3.2 lord exalted add 1',dhasa_years)
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEFIBILATED_NEECHAM:
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
        dhasa_years -= 1
        #print('Step-3.2 lord defibilated minus 1',dhasa_years)
    #print(rasi_names_en[sign],planet_list[lord_of_sign],rasi_names_en[house_of_lord],rasi_names_en[sign],dhasa_years)
    return dhasa_years
def narayana_dhasa_for_divisional_chart_old(jd_at_dob,place,dob,years_from_dob=0,divisional_chart_factor=1):
    """
        calculate narayana dhasa for divisional charts / annual charts
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param jd_at_dob: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @param years_from_dob: # years of from year of birth
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    " Natal Chart using jd_at_dob without years_from_dob"
    rasi_planet_positions = charts.divisional_chart(jd_at_dob,place,divisional_chart_factor=1)
    h_to_p = utils.get_house_planet_list_from_planet_positions(rasi_planet_positions)
    #print('h_to_p_rasi',h_to_p)
    lagna_house = rasi_planet_positions[0][1][0]
    #print('lagna house natal chart',lagna_house)
    lagna_house = (lagna_house+(years_from_dob+1)-1) % 12
    #print('lagna house on annual natal chart',lagna_house)
    lagna_seventh_house = (lagna_house+7-1) % 12
    jd_at_years = jd_at_dob + years_from_dob * const.sidereal_year
    dob = drik.jd_to_gregorian(jd_at_years)
    varga_planet_positions = charts.divisional_chart(jd_at_years,place,divisional_chart_factor=divisional_chart_factor)
    #print('varga_planet_positions',varga_planet_positions)
    h_to_p = utils.get_house_planet_list_from_planet_positions(varga_planet_positions)
    dhasa_seed_sign = house.stronger_rasi(h_to_p,lagna_house,lagna_seventh_house)
    #print(rasi_names_en[dhasa_seed_sign],'is stronger of ',rasi_names_en[lagna_house],'and',rasi_names_en[lagna_seventh_house])
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    return _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob)
def _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob,include_antardasa=True):
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    if p_to_h[8]==dhasa_seed_sign:
        #print('ketu exception')
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h[6]==dhasa_seed_sign:
        #print('saturn exception')
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]
    #print('narayana dhasa progression',dhasa_progression)
    dhasa_periods = []
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_duration = _dhasa_duration(p_to_h,sign)
        dhasa_end = dhasa_start+dhasa_duration
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        if include_antardasa:
            andtardhasa = _narayana_antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
            dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        else:
            dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,dhasa_duration])
        dhasa_start = dhasa_end
    # Second cycle
    dhasa_start = dhasa_end
    total_dhasa_duration = sum([row[-1] for row in dhasa_periods ])
    for c,sign in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_periods[c][-1]
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            #dhasa_duration = 12
            continue
        dhasa_end = dhasa_start+dhasa_duration
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        if include_antardasa:
            andtardhasa = _narayana_antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
            dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        else:
            dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,dhasa_duration])
        dhasa_start = dhasa_end
        #print('total_dhasa_duration',total_dhasa_duration,dhasa_end)
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_periods
def narayana_dhasa_for_divisional_chart(dob,tob,place,divisional_chart_factor=1):
    # Get Rasi Chart first
    jd_at_dob = utils.julian_day_number(dob,tob)
    chart = charts.divisional_chart(jd_at_dob, place)
    h_to_p_rasi = utils.get_house_planet_list_from_planet_positions(chart)
    #print('h_to_p_rasi',h_to_p_rasi)
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    #print('p_to_h_rasi',p_to_h_rasi)
    # For D-n chart get the lord of nth house in rasi chart
    seed_house = p_to_h_rasi[const._ascendant_symbol]+divisional_chart_factor-1
    lord_of_seed_house = house.house_owner(h_to_p_rasi,seed_house)
    #print('seed house',seed_house,'lord_of_seed_house',lord_of_seed_house)
    """ 
        Important:
        Take the rasi occupied by Lord of Seed House in the divisional chart of interest as lagna of varga chart
    """
    # Get Varga Cahrt
    varga_planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    lord_sign = p_to_h_varga[lord_of_seed_house]
    #print('lord_of_seed_house',lord_of_seed_house,'lord_sign',lord_sign,'\nvarga_planet_positions',varga_planet_positions)
    h_to_p_varga = utils.get_house_planet_list_from_planet_positions(varga_planet_positions)
    #print('h_to_p_varga',h_to_p_varga)
    #exit()
    h_to_p_varga = utils.get_house_planet_list_from_planet_positions(varga_planet_positions)
    seventh_house = (lord_sign+7-1)%12
    #print("Finding which house",lord_sign,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi(h_to_p_varga,lord_sign,seventh_house)
    #print('dhasa_seed_sign',dhasa_seed_sign)
    return _narayana_dhasa_calculation(p_to_h_varga,dhasa_seed_sign,dob)
def narayana_dhasa_for_divisional_chart_old2(dob,tob,place,h_to_p_varga,divisional_chart_factor=1):
    # Get Rasi Chart first
    jd_at_dob = utils.julian_day_number(dob,tob)
    chart = charts.divisional_chart(jd_at_dob, place)
    h_to_p_rasi = utils.get_house_planet_list_from_planet_positions(chart)
    #print('h_to_p_rasi',h_to_p_rasi)
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    #print('p_to_h_rasi',p_to_h_rasi)
    # For D-n chart get the lord of nth house in rasi chart
    seed_house = p_to_h_rasi[const._ascendant_symbol]+divisional_chart_factor-1
    lord_of_seed_house = house.house_owner(h_to_p_rasi,seed_house)
    #print('seed house',seed_house,'lord_of_seed_house',lord_of_seed_house)
    p_to_h_varga = utils.get_planet_to_house_dict_from_chart(h_to_p_varga)
    lord_sign = p_to_h_varga[lord_of_seed_house]
    seventh_house = (lord_sign+7-1)%12
    #print("Finding which house",lord_sign,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi(h_to_p_varga,lord_sign,seventh_house)
    #print('dhasa_seed_sign',dhasa_seed_sign)
    return _narayana_dhasa_calculation(p_to_h_varga,dhasa_seed_sign,dob)
def narayana_dhasa_for_rasi_chart(dob,tob,place):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.rasi_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    #print("Finding which house",asc_house,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi(h_to_p,asc_house,seventh_house)
    #print('stronger_rasi of ',house.rasi_names_en[asc_house],house.rasi_names_en[seventh_house],'is',house.rasi_names_en[dhasa_seed_sign])
    return _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob)
def narayana_dhasa_for_rasi_chart_old(h_to_p,dob):
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    #print("Finding which house",asc_house,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi(h_to_p,asc_house,seventh_house)
    #print('stronger_rasi of ',house.rasi_names_en[asc_house],house.rasi_names_en[seventh_house],'is',house.rasi_names_en[dhasa_seed_sign])
    return _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob)
def _narayana_antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
def varsha_narayana_dhasa_bhukthi(dob,tob,place,years=1,divisional_chart_factor=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    #jd_at_years = jd_at_dob + years * const.sidereal_year
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years)
    rasi_chart = charts.rasi_chart(jd_at_years, place)
    p_to_h_rasi = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    #print('p_to_h_rasi',p_to_h_rasi)
    varga_chart = charts.divisional_chart(jd_at_years, place, divisional_chart_factor=divisional_chart_factor)
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_chart)
    #print('p_to_h_varga',p_to_h_varga)
    natal_lagna =  p_to_h_rasi[const._ascendant_symbol]
    #print('natal lagna',natal_lagna)
    annual_house = (natal_lagna+(years-1)+divisional_chart_factor-1)%12
    #print('annual_house',annual_house)
    h_to_p_varga = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h_varga)
    annual_house_owner_in_varga = house.house_owner(h_to_p_varga,annual_house)
    #print('annual_house_owner_in_varga',annual_house_owner_in_varga)
    dhasa_seed_sign = p_to_h_varga[annual_house_owner_in_varga]
    #print('dhasa_seed_sign',dhasa_seed_sign)
    include_antardasa = True
    nd = _narayana_dhasa_calculation(p_to_h_varga, dhasa_seed_sign, dob,include_antardasa=include_antardasa)
    print('narayana dasa',nd)
    if include_antardasa:
        nd = [ [p,ys,ye,bhukthis,d*3] for p,ys,ye,bhukthis,d in nd]
    else:
        nd = [ [p,ys,ye,d*3] for p,ys,ye,d in nd] # Varsha Progression 120 years Mapped to 360 days. So d*3
    print('varsha narayana dasa',nd)
    return nd
    
if __name__ == "__main__":
    from hora.tests.pvr_tests import test_example
    """
    chapter = 'Chapter 18.2 '
    exercise = 'Example 66 / Chart 23 Narayana Dhasa Tests ' 
    dob = (1912,8,8)
    tob = (19,38,0)
    lat = 13.0+0.0/60
    long = 77.+35.0/60
    place = drik.Place('unknown',lat, long, +5.5)
    divisional_chart_factor = 1
    h_to_p = ['','6/1','','0','3/2/5','8','','4','','','L','7']
    #nd = narayana.narayana_dhasa_for_divisional_chart(dob,tob,place,divisional_chart_factor)
    nd = narayana_dhasa_for_rasi_chart(dob,tob,place)
    expected_result= [(4,1),(9,8),(2,2),(7,9),(0,4),(5,1),(10,9),(3,3),(8,11),(1,3),(6,10),(11,4),(4,11),(9,4),(2,10),(7,3),(0,8),(5,11),(10,3),(3,9)]
    for pe,p in enumerate(nd):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
    """
    """
    chapter = 'Chapter 18.5 '
    exercise = 'Example 71 / Chart 27 Narayana Dhasa Divisional Chart Tests ' 
    dob = (1970,4,4)
    tob = (17,50,0)
    jd_at_dob = utils.julian_day_number(dob, tob)
    lat = 16.0+15.0/60
    long = 81.+12.0/60
    place = drik.Place('unknown',lat, long, 5.5)
    divisional_chart_factor = 4
    h_to_p_varga = ['3','','','5','7/L','0','6','','','4/2','8','1']
    nd = narayana_dhasa_for_divisional_chart(dob, tob, place, divisional_chart_factor)
    expected_result= [(9,4),(8,0),(7,3),(6,9),(5,5),(4,11),(3,7),(2,10),(1,2),(0,10),(11,1),(10,6)]
    for pe,p in enumerate(nd[:len(expected_result)]):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
    """
    #"""
    chapter = 'Chapter 30.4 '
    exercise = 'Example in 30.4 '
    dob = (1972,6,1)
    tob = (4,16,0)
    jd_at_dob = utils.julian_day_number(dob,tob)
    years = 22
    place = drik.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 9
    vd = varsha_narayana_dhasa_bhukthi(dob,tob,place,years=years,divisional_chart_factor=divisional_chart_factor)
    print(vd)
    expected_result = [(7,21),(8,12),(9,6),(10,9),(11,33)]
    for i,[p,_,_,_,d] in enumerate(vd[:len(expected_result)]):
        test_example(chapter+exercise,expected_result[i],(p,d),'days')
    #"""
    