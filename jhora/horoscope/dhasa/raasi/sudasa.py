from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house
from hora.horoscope.dhasa.raasi import narayana
from hora.horoscope.chart import charts
def sudasa_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,include_antardhasa=True):
    jd = utils.julian_day_number(dob, tob)
    sl = drik.sree_lagna(jd, place, divisional_chart_factor)
    sree_lagna_house = sl[0]
    sree_lagna_longitude = sl[0]*30+sl[1]
    #print('sree_lagna_house',sree_lagna_house,'sree_lagna_longitude',sree_lagna_longitude)
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    return sudasa_dhasa_from_planet_positions(planet_positions,sree_lagna_house,sree_lagna_longitude,dob,tob,include_antardhasa=include_antardhasa)
def sudasa_dhasa_from_planet_positions(planet_positions,sree_lagna_house,sree_lagna_longitude,dob,tob,include_antardhasa=True):
    """
        calculate Sudasa Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param sree_lagna_house:Raasi index where sree lagna is
        @param sree_lagna_longitude: Longitude of Sree Lagna 
            Note: one can get sree lagna information from drik.sree_lagna()
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    start_jd = utils.julian_day_number(dob, tob)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    direction = 1
    if sree_lagna_house in const.even_signs:
        direction = -1
    ks = sum(house.kendras()[:3],[])
    """  
        Exceptions: There are exceptions for Saturn or Ketu. If Saturn occupies
                    SL, the counting is forward (no matter odd/even sign). If Ketu occupies
                    SL, the direction of counting houses is reversed from whatever we get based
                    on odd/even sign.
    """
    if p_to_h[6]==sree_lagna_house:
        direction = 1
    elif p_to_h[8]==sree_lagna_house:
        direction *= -1
    dhasa_progression = [(sree_lagna_house+direction*(k-1))%12 for k in ks]
    dhasa_info = []
    for s,dhasa_lord in enumerate(dhasa_progression):
        dhasa_duration = round(narayana._dhasa_duration(planet_positions,dhasa_lord),2)
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
        dhasa_duration = round(dhasa_duration,2)
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
    pvr_tests.sudasa_tests()