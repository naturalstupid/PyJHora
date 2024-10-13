""" Chakra Dhasa """
"""
    Antardasa/Bhukthi Lords do not match with JHora - as it is not clear how it is implemented there
    So we start with mahadasa lord as the bhukthi lord.
"""
from hora.panchanga import drik
from hora import utils, const
_dhasa_duration = 10.0; _bhukthi_duration = _dhasa_duration/12.0
def _dhasa_seed(jd,place,lagna_house,lagna_lord_house):
    previous_day_sunset_time = drik.sunset(jd-1, place)[0]
    today_sunset_time = drik.sunset(jd, place)[0]
    today_sunrise_time = drik.sunrise(jd, place)[0]
    tomorrow_sunrise_time = 24.0+drik.sunrise(jd+1, place)[0]
    _,_,_,birth_time = utils.jd_to_gregorian(jd)
    df = abs(today_sunset_time - today_sunrise_time)/6.0
    nf1 = abs(today_sunrise_time-previous_day_sunset_time)/6.0
    nf2 = abs(tomorrow_sunrise_time-today_sunset_time)/6.0
    #print('df',df,'nf1',nf1,'nf2',nf2)
    dawn_start = today_sunrise_time-nf1; dawn_end=today_sunrise_time+nf1
    #print('dawn',dawn_start,dawn_end)
    day_start = dawn_end; day_end = today_sunset_time-nf1
    #print('day',day_start,day_end)
    dusk_start = day_end ; dusk_end = today_sunset_time+nf2
    #print('dusk',dusk_start,dusk_end)
    yday_night_start = -(previous_day_sunset_time+nf1); yday_night_end = today_sunrise_time-nf1
    tonight_start = today_sunset_time+nf2; tonight_end = tomorrow_sunrise_time-nf2
    #print('Night-Yday',yday_night_start,yday_night_end,'Night-today',tonight_start,tonight_end)
    # Night is before dawn_start and after dusk_end
    if birth_time > dawn_start and birth_time < dawn_end: # dawn
        kaala_period = 'Dawn'
        _dhasa_seed = (lagna_house+1)%12
    elif birth_time > dusk_start and birth_time < dusk_end: # dusk
        kaala_period = 'Dusk'
        _dhasa_seed = (lagna_house+1)%12
    elif birth_time > day_start and birth_time < day_end: # Day
        kaala_period = 'Day'
        _dhasa_seed = lagna_lord_house
    elif birth_time > yday_night_start and birth_time < yday_night_end: # yday-night
        kaala_period = 'YDay-Night'
        _dhasa_seed = lagna_house
    elif birth_time > tonight_start and birth_time < tonight_end: # yday-night
        kaala_period = 'ToNight'
        _dhasa_seed = lagna_house    
    return _dhasa_seed
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=False):
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months,sixty_hours=months)
    from hora.horoscope.chart import charts, house
    pp = charts.divisional_chart(jd_years, place, divisional_chart_factor=divisional_chart_factor)
    lagna_house = pp[0][1][0];lagna_lord = house.house_owner_from_planet_positions(pp, lagna_house)
    lagna_lord_house = pp[lagna_lord+1][1][0]
    dhasa_seed = _dhasa_seed(jd_years, place,lagna_house,lagna_lord_house)
    dhasa_info = []
    start_jd = jd_years
    for dhasa_lord in [(dhasa_seed+h)%12 for h in range(12)]:
        if include_antardhasa:
            for bhukthi_lord in [(dhasa_lord+h)%12 for h in range(12)]:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                start_jd += _bhukthi_duration * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,round(_dhasa_duration,2)))
            start_jd += _dhasa_duration * const.sidereal_year
    return dhasa_info
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.chakra_test()