from hora import const, utils
from hora.horoscope.chart import charts, house
from hora.horoscope.dhasa.raasi import narayana
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    navamsa_planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=9)
    dhasa_seed_sign = navamsa_planet_positions[0][1][0]
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    return narayana._narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,sixty_hours=sixty_hours,include_antardhasa=include_antardhasa,varsha_narayana=False)
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.lagnamsaka_dhasa_test()
    