from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house

sidereal_year = const.sidereal_year

def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    karakas = house.chara_karakas(planet_positions)
    #print('karakas',karakas)
    asc_house = planet_positions[0][1][0]
    dhasa_info = []
    start_jd = jd_at_dob
    human_life_span = sum([(planet_positions[k+1][1][0] - asc_house +12)%12 for k in karakas])
    for k in karakas:
        k_h = planet_positions[k+1][1][0]
        duration = (k_h - asc_house + 12)%12
        bhukthis = karakas
        if include_antardhasa:
            for bhukthi_lord in bhukthis:
                b_h = planet_positions[bhukthi_lord+1][1][0]
                dd = (b_h - asc_house + 12)%12
                factor = dd *  duration / human_life_span
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((k,bhukthi_lord,dhasa_start,dd))
                start_jd += factor * sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((k,dhasa_start,duration))
            start_jd += duration * sidereal_year
    return dhasa_info
        

if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.karaka_dhasa_test()
