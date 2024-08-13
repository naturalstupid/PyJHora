from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house
""" Maha dasa and antardasa are OK but dhasa periods do not match with JHora """
sidereal_year = const.sidereal_year

def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    lagna = planet_positions[0][1][0]
    hora_lagna,_ = drik.hora_lagna(jd_at_dob,place,divisional_chart_factor=divisional_chart_factor) # V3.1.9
    varnada_lagna,_ = charts.varnada_lagna(dob, tob, place,divisional_chart_factor=divisional_chart_factor)
    dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, lagna, hora_lagna)
    dhasa_lords = [(dhasa_seed+h)%12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [(dhasa_seed-h+12)%12 for h in range(12)]
    #print('lagna',lagna,'hora_lagna',hora_lagna,'varnada_lagna',varnada_lagna,dhasa_seed,dhasa_lords)
    dhasa_info = []
    start_jd = jd_at_dob
    for dhasa_lord in dhasa_lords:
        duration = (dhasa_lord - varnada_lagna)%12
        bhukthis = [(dhasa_lord+h)%12 for h in range(12)]
        if include_antardhasa:
            dd = duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,duration))
            start_jd += duration * sidereal_year
    return dhasa_info
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.varnada_dhasa_test()