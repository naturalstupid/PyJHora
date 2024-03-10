from hora import const, utils
from hora.horoscope.chart import charts, house
from hora.horoscope.dhasa import narayana
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    navamsa_planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=9)
    dhasa_seed_sign = navamsa_planet_positions[0][1][0]
    planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
    return narayana._narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,sixty_hours=sixty_hours,include_antardasa=include_antardasa,varsha_narayana=False)
if __name__ == "__main__":
    from hora.panchanga import drik
    dob = (1996,12,7)
    tob = (10,34,0)
    tobh = (tob[0]+tob[1]/60+tob[2]/3600)/24
    place =drik.Place('Chennai',13.0878,80.2785,5.5)
    ld = get_dhasa_antardhasa(dob, tob, place,include_antardasa=False)
    for l,b,d,t in ld:
        print(house.rasi_names_en[l],d)
    #print(ld)