from hora import const, utils
from hora.horoscope.chart import charts, house
from hora.horoscope.dhasa import narayana
""" Also called Lagna Kendradi Rasi Dhasa """
def kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    #print("Finding which house",asc_house,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    #print('dhasa_seed_sign',dhasa_seed_sign)
    direction = 0
    if p_to_h[6]==dhasa_seed_sign:
        direction = 1
    elif p_to_h[8]==dhasa_seed_sign:
        direction = -1
    elif dhasa_seed_sign in const.odd_signs:  # Forward
        direction = 1
    elif dhasa_seed_sign in const.even_signs:  # backward
        direction = -1
    ks = sum(house.kendras()[:3],[])
    #print('ks',ks)
    dhasa_progression = [(dhasa_seed_sign+direction*(k-1))%12 for k in ks]
    #print('kedraadhi dhasa progression',dhasa_progression)
    dhasa_periods = []
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_duration = narayana._dhasa_duration(planet_positions,sign)
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
def lagna_kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1):
    return kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
def karaka_kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1,karaka_index=1):
    if karaka_index not in range(1,9):
        print('Karaka Index should be in the range (1..8). Index 1 assumed')
        karaka_index = 1
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    ak = house.chara_karakas(planet_positions)[karaka_index-1]
    ak_house = p_to_h[ak]
    seventh_house = (ak_house+7-1)%12
    #print("Finding which house",house.rasi_names_en[ak_house],house.rasi_names_en[seventh_house],'is stronger')
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, ak_house, seventh_house)
    #print('dhasa_seed_sign',dhasa_seed_sign)
    direction = 0
    if p_to_h[6]==dhasa_seed_sign:
        direction = 1
    elif p_to_h[8]==dhasa_seed_sign:
        direction = -1
    elif dhasa_seed_sign in const.odd_signs:  # Forward
        direction = 1
    elif dhasa_seed_sign in const.even_signs:  # backward
        direction = -1
    ks = sum(house.kendras()[:3],[])
    #print('ks',ks)
    dhasa_progression = [(dhasa_seed_sign+direction*(k-1))%12 for k in ks]
    #print('kedraadhi dhasa progression',dhasa_progression)
    dhasa_periods = []
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_duration = narayana._dhasa_duration(planet_positions,sign)
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
    from hora.panchanga import drik
    dob = (1996,12,7)
    #dob = (1963,8,7)
    tob = (10,34,0)
    #tob = (21,15,0)
    tobh = (tob[0]+tob[1]/60+tob[2]/3600)/24
    place =drik.Place('Chennai',13.0878,80.2785,5.5)
    #place = drik.Place('sambalpur',21+27/60,83+58/60,5.5)
    #ld = karaka_kendradhi_rasi_dhasa(dob, tob, place)
    ld = lagna_kendradhi_rasi_dhasa(dob, tob, place)
    for l,s,e,_,_ in ld:
        print(house.rasi_names_en[l],s,e)
    exit()
    from hora.tests import pvr_tests
    chapter = 'Chapter 19.3 Kendradhi Rasi Dhasa tests '
    exercise = 'Example 76 / Chart 34'
    dob = (1911,2,6)
    tob = (2,4,0)
    place = drik.Place('unknwon',41+38/60,-89-47/60,-6.00)
    chart_34 = ['6/1/7','','','','','','8/4','L','2/3','0','5','']
    # Ans:           Ta Aq Sc Le Ar Cp Li Cn Pi Sg Vi Ge    
    # Ans: Dasa years 9 10 11 7  8  8  4  3  5  10  9  6
    expected_result = [(1,9),(10,10),(7,11),(4,7),(0,8),(9,8),(6,4),(3,3),(11,5),(8,10),(5,9),(2,6)]
    #print(chart_34)
    #kd = kendradhi_rasi_dhasa(chart_34,dob)
    kd = kendradhi_rasi_dhasa(dob, tob, place, divisional_chart_factor=1)
    print(kd)  
    for pe,p in enumerate(kd[:len(expected_result)]):
        pvr_tests.test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
