from hora import const, utils
from hora.horoscope.chart import charts, house
from hora.horoscope.dhasa.raasi import narayana
""" Also called Lagna Kendradi Raasi Dhasa """
""" This file also finds Karaka Kendraddi Rasi Dasa - See karaka_kendradhi_rasi_dhasa() """
def lagna_kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1):
    return kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
def kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
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
    dhasa_info = []
    start_jd = jd_at_dob
    for dhasa_lord in dhasa_progression:
        dhasa_duration = narayana._dhasa_duration(planet_positions,dhasa_lord)
        if include_antardhasa:
            bhukthis = _antardhasa(dhasa_lord,p_to_h)
            dd = dhasa_duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,dhasa_duration))
            start_jd += dhasa_duration * const.sidereal_year
    # Second cycle
    dhasa_start = start_jd
    total_dhasa_duration = sum([row[-1] for row in dhasa_info ])
    for c,dhasa_lord in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_info[c][-1]
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            continue
        if include_antardhasa:
            bhukthis = _antardhasa(dhasa_lord,p_to_h)
            dd = dhasa_duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,dhasa_duration))
            start_jd += dhasa_duration * const.sidereal_year
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_info
def karaka_kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1,karaka_index=1,include_antardhasa=True):
    if karaka_index not in range(1,9):
        print('Karaka Index should be in the range (1..8). Index 1 assumed')
        karaka_index = 1
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    ak = house.chara_karakas(planet_positions)[karaka_index-1]
    ak_house = p_to_h[ak]
    seventh_house = (ak_house+7-1)%12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, ak_house, seventh_house)
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
    dhasa_progression = [(dhasa_seed_sign+direction*(k-1))%12 for k in ks]
    dhasa_info = []
    start_jd = jd_at_dob
    for dhasa_lord in dhasa_progression:
        dhasa_duration = narayana._dhasa_duration(planet_positions,dhasa_lord)
        if include_antardhasa:
            bhukthis = _antardhasa(dhasa_lord,p_to_h)
            dd = dhasa_duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,dhasa_duration))
            start_jd += dhasa_duration * const.sidereal_year
    # Second cycle
    dhasa_start = start_jd
    total_dhasa_duration = sum([row[-1] for row in dhasa_info ])
    for c,dhasa_lord in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_info[c][-1]
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            continue
        if include_antardhasa:
            bhukthis = _antardhasa(dhasa_lord,p_to_h)
            dd = dhasa_duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,dhasa_duration))
            start_jd += dhasa_duration * const.sidereal_year
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_info
    
def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.kendradhi_rasi_test()