from hora.horoscope.chart import charts
from hora import const, utils
from hora.panchanga import panchanga
def sudharsana_chakra_dhasa_for_divisional_chart(jd_at_dob,place,dob,years_from_dob=0,divisional_chart_factor=1):
    """
        calculate sudharsana chakra dhasa for divisional charts / annual charts
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param jd_at_dob: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @param years_from_dob: # years of from year of birth
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @return: [lagna_periods,moon_periods,sun_periods]
          Each dhasa period will have the following format:
          [planet index,(dhasa_start_year, month, date,longitude),dhasa duration],...
          [0, (1987, 10, 31, 15.388383474200964), 2.5], [1, (1987, 11, 3, 4.348383475095034), 2.5],....
          
    """
    jd_at_years = jd_at_dob + (years_from_dob * const.sidereal_year)
    rasi_planet_positions = charts.divisional_chart(jd_at_years,place,divisional_chart_factor=divisional_chart_factor)
    lagna_house = rasi_planet_positions[0][1][0]
    moon_house = rasi_planet_positions[2][1][0]
    sun_house = rasi_planet_positions[1][1][0]
    print('lagna house natal chart',lagna_house)
    lagna_sign = (lagna_house+years_from_dob-1) % 12
    moon_sign = (moon_house+years_from_dob-1) % 12
    sun_sign = (sun_house+years_from_dob-1) % 12
    print('lagna/Moon/Sun house on annual natal chart',lagna_sign,moon_sign,sun_sign)
    lagna_periods = _sudharsana_dhasa_calculation(jd_at_years,lagna_sign)
    moon_periods = _sudharsana_dhasa_calculation(jd_at_years,moon_sign)
    sun_periods = _sudharsana_dhasa_calculation(jd_at_years,sun_sign)
    return lagna_periods,moon_periods,sun_periods
def _sudharsana_dhasa_calculation(jd_at_years,dhasa_seed_sign):
    dhasa_periods = []
    dhasa_start = jd_at_years
    dhasa_progression = [(dhasa_seed_sign+h)%12 for h in range(12)]
    dhasa_duration = const.sidereal_year
    antardhasa_duration = round(const.sidereal_year / 12.0,2)
    for sign in dhasa_progression:
        dhasa_end = dhasa_start+dhasa_duration
        antardhasa = [[(sign+h)%12,panchanga.jd_to_gregorian(dhasa_start+h*antardhasa_duration),1.0] for h in range(12)]
        dhasa_end_date = panchanga.jd_to_gregorian(dhasa_end)
        dhasa_periods.append([sign,antardhasa,dhasa_end_date,1.0])
        dhasa_start = dhasa_end
    return dhasa_periods
def sudharsana_pratyantardasas(antardhasa_start,antardhasa_seed_sign):
    dhasa_periods = []
    dhasa_start = antardhasa_start
    dhasa_progression = [(antardhasa_seed_sign+h)%12 for h in range(12)]
    dhasa_duration = round(const.sidereal_year/144.0,2)
    for sign in dhasa_progression:
        dhasa_end = dhasa_start+dhasa_duration
        dhasa_end_date = panchanga.jd_to_gregorian(dhasa_end)
        dhasa_periods.append([sign,dhasa_end_date,2.5])
        dhasa_start = dhasa_end
    return dhasa_periods
    