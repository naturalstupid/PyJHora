""" Computes Drig Dhasa from the chart """
from hora import const,utils
from hora.horoscope.chart import house,charts
from hora.horoscope.dhasa import narayana
import swisseph as swe
import datetime
def drig_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1):
    jd = utils.julian_day_number(dob,tob)
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    return drig_dhasa(chart, dob)
def drig_dhasa(chart,dob):
    """
        computes drig dhasa from the chart
        @param chart: chart list 1-D. Format ['1/2','3/L',...,'',5/6/7','9','0'] # 12 houses with planets and Lagnam
        @param dob: tuple of date of birth format: (year,month,day)
        @return: list of drig dhasa from date of birth 
          Format: [ [dhasa_lord, dhasa_start_date, dhasa_end_date, [bhukthi_lord1, bhukthi_lord2...], dhasa_duration],...]
          Example: [[2, '1912-1-1', '1916-1-1', [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1], 4], 
                    [5, '1916-1-1', '1927-1-1', [5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6], 11], ...]]
    """
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)  
    #print(p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    ninth_house = (asc_house+9-1)%12
    dhasa_progression= []
    for s in range(ninth_house,(ninth_house+3)):
        s %= 12
        aspected_kendras = house.aspected_kendras_of_raasi(s,s in const.even_footed_signs)
        dp = [s]+ aspected_kendras
        #print(s,dp)
        dhasa_progression.append(dp)
    dhasa_progression = sum(dhasa_progression,[])
    #print(dhasa_progression)
    dhasa_periods = []
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_duration = narayana._dhasa_duration(p_to_h,sign)
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
    chapter = 'Chapter 21 / Drig Dhasa Tests '
    exercise = 'Example 80 / Chart 36'
    chart_36 = ['','8','6','','5','2/0','3/L','7','','1','4','']
    dd = drig_dhasa(chart_36,(1912,1,1))
    print(dd)
    expected_result = [(2,4),(5,11),(8,2),(11,1),(3,6),(1,3),(10,8),(7,10),(4,11),(0,5),(9,7),(6,10)]
    # Ans: Ge, Vi, Sg, Pi, Cn, Ta, Aq, Sc, Le, Ar, Cp, Li.
    # Ans: 2,5,8,11,3,1,10,7,4,0,9,6
    for pe,p in enumerate(dd[:len(expected_result)]):
        pvr_tests.test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
