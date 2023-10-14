from hora import const, utils
from hora.horoscope.chart import house,charts
def nirayana_shoola_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1):
    jd = utils.julian_day_number(dob,tob)
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    return nirayana_shoola_dhasa(chart,dob)
def nirayana_shoola_dhasa(chart,dob):
    """
        calculate Nirayana Shoola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    #print('asc_house',asc_house)
    second_house = (asc_house+2-1)%12 # 2nd house
    eighth_house = (asc_house+8-1)%12 # 8th house
    #print("Finding which house",second_house,eighth_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi(h_to_p,second_house,eighth_house)
    #if dhasa_seed_sign != asc_house:
    #    dhasa_seed_sign = (dhasa_seed_sign+asc_house - 1)%12
    #print('dhasa_seed_sign',dhasa_seed_sign)
    direction = 1
    if dhasa_seed_sign in const.even_signs:
        direction = -1
    dhasa_progression = [(dhasa_seed_sign+direction*k)%12 for k in range(12)]
    #print(dhasa_progression)
    dhasa_periods = []
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_duration = 7 # movable sign
        if sign in const.fixed_signs:
            dhasa_duration = 8
        elif sign in const.dual_signs:
            dhasa_duration = 9
        dhasa_end = dhasa_start+dhasa_duration
        andtardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
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
        andtardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        dhasa_start = dhasa_end
        #print('total_dhasa_duration',total_dhasa_duration,dhasa_end)
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_periods
def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from hora.tests import pvr_tests
    chapter = 'Chapter 22 / Nirayana Shoola Dhasa Tests '
    exercise = 'Example 84 / Chart 8'
    chart_8 = ['','7','','6','','','4/3/5','0/L/8/2','','','1','']
    #print('nirayana shoola dhasa test\n',chart_8)
    #print('nirayana shoola dhasa\n',sd)
    #Ans: Sg (9), Cp(7), Aq(8), Pi(9), Ar(7), Ta(8), Ge(9) etc
    sd = nirayana_shoola_dhasa(chart_8, (1946,12,2))
    #print(sd)
    expected_result = [(2,9),(3,7),(4,8),(5,9),(6,7),(7,8),(8,9)]
    print('Starting Rasi in book as Sg may be wrong. Both Sg and Ge have same oddity per Rule-4. By Rule-5 Ge is stronger')
    for pe,p in enumerate(sd[:len(expected_result)]):
        pvr_tests.test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
