""" Kaala Dhasa """
from hora.panchanga import drik
from hora import utils, const
_kaala_dhasa_life_span = 120 # years
def _dhasa_progression_and_periods(jd,place):
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
        kaala_frac = (birth_time-dawn_start)/(dawn_end-dawn_start)
    elif birth_time > dusk_start and birth_time < dusk_end: # dusk
        kaala_period = 'Dusk'
        kaala_frac = (birth_time-dusk_start)/(dusk_end-dusk_start)
    elif birth_time > day_start and birth_time < day_end: # Day
        kaala_period = 'Day'
        kaala_frac = (birth_time-day_start)/(day_end-day_start)
    elif birth_time > yday_night_start and birth_time < yday_night_end: # yday-night
        kaala_period = 'YDay-Night'
        kaala_frac = (birth_time-yday_night_start)/(yday_night_end-yday_night_start)
    elif birth_time > tonight_start and birth_time < tonight_end: # yday-night
        kaala_period = 'ToNight'
        kaala_frac = (birth_time-tonight_start)/(tonight_end-tonight_start)
    #print(birth_time,'kaala period',kaala_period,'kaala fraction',kaala_frac)
    _kaala_dhasa_life_span_first_cycle = _kaala_dhasa_life_span*kaala_frac
    _dhasas1 = [(p+1)*_kaala_dhasa_life_span_first_cycle/45.0 for p in range(9)]
    # Second Cycle
    _kaala_dhasa_life_span_second_cycle = _kaala_dhasa_life_span - _kaala_dhasa_life_span_first_cycle
    _dhasas2 = [(p+1)*_kaala_dhasa_life_span_second_cycle/45.0 for p in range(9)]
    
    return _dhasas1,_dhasas2
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=False):
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months,sixty_hours=months)
    dhasas_first, dhasas_second = _dhasa_progression_and_periods(jd_years, place)
    dhasa_info = []
    start_jd = jd_years
    for dhasa_lord in range(9):
        _dhasa_duration = dhasas_first[dhasa_lord]
        if include_antardhasa:
            for bhukthi_lord in range(9):
                _bhukthi_duration = (bhukthi_lord+1)*_dhasa_duration/45.0
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                start_jd += _bhukthi_duration * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,round(_dhasa_duration,2)))
            start_jd += _dhasa_duration * const.sidereal_year
    # Second Cycle
    for dhasa_lord in range(9):
        _dhasa_duration = dhasas_second[dhasa_lord]
        if include_antardhasa:
            for bhukthi_lord in range(9):
                _bhukthi_duration = (bhukthi_lord+1)*_dhasa_duration/45.0
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
    pvr_tests.kaala_test()