from hora import const, utils
from hora.horoscope.chart.house import *
from hora.horoscope.dhasa import narayana

def nirayana_shoola_dhasa(chart,dob):
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    print(p_to_h)
    asc_house = p_to_h['L']
    print('asc_house',asc_house)
    second_house = (asc_house+2-1)%12
    eighth_house = (asc_house+8-1)%12
    print("Finding which house",second_house,eighth_house,'is stronger')
    dhasa_seed_sign = stronger_rasi(h_to_p,second_house,eighth_house)
    if dhasa_seed_sign != asc_house:
        dhasa_seed_sign = (dhasa_seed_sign+asc_house - 1)%12
    print('dhasa_seed_sign',dhasa_seed_sign)
    direction = 1
    if dhasa_seed_sign in const.even_signs:
        direction = -1
    dhasa_progression = [(dhasa_seed_sign+direction*k)%12 for k in range(12)]
    print(dhasa_progression)
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
    pass