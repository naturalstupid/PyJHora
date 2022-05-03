""" Computes Drig Dhasa from the chart """
from hora import const,utils
from hora.panchanga import panchanga
from hora.horoscope.chart import house
from hora.horoscope.dhasa import narayana
import swisseph as swe
import datetime
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
    print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)  
    print(p_to_h)
    asc_house = p_to_h['L']
    ninth_house = (asc_house+9-1)%12
    dhasa_progression= []
    for s in range(ninth_house,ninth_house+3):
        dp = [s]+ house.aspected_kendras_of_raasi(s,s in const.even_footed_signs)
        #print(s,dp)
        dhasa_progression.append(dp)
    dhasa_progression = sum(dhasa_progression,[])
    print(dhasa_progression)
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
    drig_dhasa_tests()