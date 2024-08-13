from hora import const, utils
from hora.horoscope.chart import house, charts
from hora.horoscope.dhasa.raasi import narayana
""" Also called Lagna Kendradi Rasi Dhasa """
def moola_dhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    """
        calculate Lagna Kendraadhi dhasa aka Moola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    start_jd = utils.julian_day_number(dob,tob)
    pp = charts.divisional_chart(start_jd, place, divisional_chart_factor=divisional_chart_factor, years=years, months=months, 
                                 sixty_hours=sixty_hours)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)    
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    #print("Finding which house",asc_house,seventh_house,'is stronger')
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(pp, asc_house,seventh_house)
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
    #print(dhasa_progression)
    dhasa_periods = []
    dhasa_start = start_jd
    for sign in dhasa_progression:
        dhasa_duration = narayana._dhasa_duration(pp,sign)
        dhasa_end = dhasa_start+dhasa_duration*const.sidereal_year
        y,m,d,h = utils.jd_to_gregorian(dhasa_start)
        dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
        if include_antardhasa:
            antardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
            dhasa_periods.append((sign,dhasa_start,antardhasa,dhasa_duration))
        else:
            dhasa_periods.append((sign,dhasa_start,dhasa_duration))
        #dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        #dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,antardhasa,dhasa_duration])
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
        dhasa_end = dhasa_start+dhasa_duration*const.sidereal_year
        y,m,d,h = utils.jd_to_gregorian(dhasa_start)
        dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
        if include_antardhasa:
            antardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
            dhasa_periods.append((sign,dhasa_start,antardhasa,dhasa_duration))
        else:
            dhasa_periods.append((sign,dhasa_start,dhasa_duration))
        #dhasa_period_suffix = '-'+str(dob_month)+'-'+str(dob_day)
        #dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
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
    pvr_tests.moola_dhasa_test()