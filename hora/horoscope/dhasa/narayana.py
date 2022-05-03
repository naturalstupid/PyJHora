from hora import const,utils
from hora.horoscope.chart import charts
from hora.horoscope.chart.house import *
import swisseph as swe
from hora.panchanga import panchanga
rasi_names_en = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
def _dhasa_duration(p_to_h,sign):
    lord_of_sign = const.house_owners[sign]
    #print('sign',sign,'lord of sign',lord_of_sign)
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_years = 0
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        #print('backward')
        if house_of_lord < sign:
            dhasa_years = sign+1-house_of_lord
        else:
            dhasa_years = sign+13-house_of_lord
    else:
        #print('forward')
        if house_of_lord < sign:
            dhasa_years = house_of_lord+13-sign
        else:
            dhasa_years = house_of_lord+1-sign
    dhasa_years -= 1
    if dhasa_years <=0:
        dhasa_years = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] > const._FRIEND:
        #print(planet_list[lord_of_sign],'is exhalted in',rasi_names_en[house_of_lord])
        dhasa_years += 1
    #print(rasi_names_en[sign],planet_list[lord_of_sign],rasi_names_en[house_of_lord],rasi_names_en[sign],dhasa_years)
    return dhasa_years
def narayana_dhasa_for_divisional_chart(jd_at_dob,place,dob,years_from_dob=0,divisional_chart_factor=1):
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
    print('h_to_p_rasi',h_to_p)
    lagna_house = rasi_planet_positions[0][1][0]
    print('lagna house natal chart',lagna_house)
    lagna_house = (lagna_house+(years_from_dob+1)-1) % 12
    print('lagna house on annual natal chart',lagna_house)
    dv_house = (lagna_house+divisional_chart_factor-1)%12
    lord_of_dv_house = const.house_owners[dv_house]
    print('dv_house,lord_of_dv_house',dv_house,lord_of_dv_house)
    jd_at_years = jd_at_dob + years_from_dob * const.sidereal_year
    dob = panchanga.jd_to_gregorian(jd_at_years)
    varga_planet_positions = charts.divisional_chart(jd_at_years,place,divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(varga_planet_positions)
    print('h_to_p_D'+str(divisional_chart_factor),h_to_p)
    varga_lagna_house = varga_planet_positions[lord_of_dv_house+1][1][0]
    varga_seventh_house = varga_planet_positions[(varga_lagna_house+7-1)%12][1][0]
    print('varga_lagna_house',varga_lagna_house,'varga_seventh_house',varga_seventh_house)
    dhasa_seed_sign = stronger_rasi(h_to_p,varga_lagna_house,varga_seventh_house)
    print('stronger',dhasa_seed_sign)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    return _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob)
def _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob,years_from_dob=0):
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
    dhasa_periods = []
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_duration = _dhasa_duration(p_to_h,sign)
        dhasa_end = dhasa_start+dhasa_duration
        andtardhasa = _narayana_antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
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
        #print(sign,_narayana_antardhasa(sign))
        andtardhasa = _narayana_antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        dhasa_start = dhasa_end
        #print('total_dhasa_duration',total_dhasa_duration,dhasa_end)
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_periods
def narayana_dhasa(h_to_p,dob):
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    asc_house = p_to_h['L']
    seventh_house = (asc_house+7-1)%12
    #print("Finding which house",asc_house,seventh_house,'is stronger')
    dhasa_seed_sign = stronger_rasi(h_to_p,asc_house,seventh_house)
    print('dhasa_seed_sign',dhasa_seed_sign)
    return _narayana_dhasa_calculation(p_to_h,dhasa_seed_sign,dob)
def _narayana_antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
def varsha_narayana_dhasa_bhukthi(jd,place,years,divisional_chart_factor=1):
    pass
if __name__ == "__main__":
    # Chart 24 - Bill Gates
    """
    dob = (1955,10,28)
    tob = (21,18,0)
    place = panchanga.Place('unknown',47+36.0/60, -122.33, -8.0)
    divisional_chart_factor = 1
    """
    """
    # Chart 25 - India's indepdendence
    dob = (1947,8,15)
    tob = (0,0,0)
    place = panchanga.Place('unknown',27.0, 78.5, +5.5)
    divisional_chart_factor = 1
    """
    #"""
    # Chart 27
    dob = (1972,6,1)
    tob = (4,16,0)
    years = 21
    place = panchanga.Place('unknown',16+15.0/60, 81+12.0/60, +5.5)
    divisional_chart_factor = 9
    #"""
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd_at_dob = swe.julday(dob[0],dob[1],dob[2], time_of_birth_in_hours)
    jd_at_years = jd_at_dob + years * const.sidereal_year
    nd = narayana_dhasa_for_divisional_chart(jd_at_dob,place,dob,years,divisional_chart_factor)
    for p in nd:
        print(p)
    exit()
    ascendant_index = 'L'
    planet_positions = panchanga.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = panchanga.ascendant(jd,place,as_string=False)[1]
    asc_house,asc_long = panchanga.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[ascendant_index,(asc_house,asc_long)]]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions) 
    print('h_to_p\n',h_to_p)
    nd = narayana_dhasa(h_to_p,dob)
    for p in nd:
        print(p)
    