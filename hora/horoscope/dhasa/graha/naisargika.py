from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house

dhasa_adhipathi_dict = {1:1,2:2,3:9,5:20,4:18,0:20,6:50} #,'L':12} 
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    start_jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(start_jd, place, divisional_chart_factor=divisional_chart_factor, 
                                               years=years, months=months, sixty_hours=sixty_hours)
    asc_house = planet_positions[0][1][0]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    dhasa_lords = list(dhasa_adhipathi_dict.keys())
    dhasa_info = []
    for dhasa_lord in dhasa_lords:
        duration = dhasa_adhipathi_dict[dhasa_lord]
        lord_house = planet_positions[dhasa_lord+1][1][0]
        bhukthis = [h_to_p[(h+lord_house)%12].split('/') for h in [0,3,6,9,1,4,7,10,2,5,8,11] if h_to_p[(h+lord_house)%12] != '']
        #print('dhasa_lord',dhasa_lord,bhukthis)
        bhukthis = utils.flatten_list(bhukthis)
        bhukthis.remove('L'); bhukthis.remove('8'); bhukthis.remove('7');bhukthis.remove(str(dhasa_lord))            
        bhukthis = list(map(int,bhukthis))
        if include_antardhasa:
            dd = duration/len(bhukthis)
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,duration))
            start_jd += duration * const.sidereal_year
    return dhasa_info
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.naisargika_test()