from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house

dhasa_adhipathi_dict = {5:20,1:10,8:7,6:19,4:16,3:17,7:18,2:7,0:6}
human_life_span = sum(dhasa_adhipathi_dict.values())

def _next_adhipati(lord):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_dict.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_dict.keys())[((current + 1) % len(dhasa_adhipathi_dict))]
    return next_lord
def _antardhasa(lord):
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord)
    return _bhukthis
def _dhasa_start(jd_utc,period,star_position_from_moon=1):
    nak, rem = drik.nakshatra_position(jd_utc,star_position_from_moon=star_position_from_moon)
    #print('nak,rem',nak,rem) # returns 0..26
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    period_elapsed = rem / one_star * period # years
    #print('period_elapsed',period_elapsed,rem/one_star)
    period_elapsed *= const.sidereal_year        # days
    start_date = jd_utc - period_elapsed      # so many days before current day
    return start_date
        
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]
    ds = sorted([h_to_p[(h+asc_house)%12].split('/') for h in [0,3,6,9] if h_to_p[(h+asc_house)%12] != ''],key=len,reverse=True)
    ds = utils.flatten_list(ds)
    """ TODO If ds is empty list - what to do? """
    if len(ds)==0:
        print('tara dhasa ds list is empty, returning empty list')
        return []
    if 'L' in ds:
        ds.remove('L')
    if len(ds)==0:
        print('tara dhasa ds list is empty, returning empty list')
        return []
    if len(ds) >= 2:
        ds1 = ds; sp = int(ds1[0])
        for p in range(1,len(ds1)):
            sp = house.stronger_planet_from_planet_positions(planet_positions, int(ds1[p]), int(sp))
        dhasa_lord = sp
    else:#if len(ds)==1:
        dhasa_lord = int(ds[0])#int(ds[0][0])
    _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]
    jd_utc = jd_at_dob - place.timezone / 24.
    start_jd = _dhasa_start(jd_utc, _dhasa_duration, star_position_from_moon=1)
    dhasa_info = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _dhasa_lord_duration = dhasa_adhipathi_dict[dhasa_lord]
        bhukthis = _antardhasa(dhasa_lord)
        if include_antardasa:
            for bhukthi_lord in bhukthis:
                _bhukthi_duration = dhasa_adhipathi_dict[bhukthi_lord]
                factor = _bhukthi_duration *  _dhasa_lord_duration / human_life_span
                y,m,d,h = utils.jd_to_gregorian(start_jd+place.timezone/24)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,_dhasa_duration))
                start_jd += factor * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd+place.timezone/24)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,_dhasa_duration))
            lord_duration = dhasa_adhipathi_dict[dhasa_lord]
            start_jd += lord_duration * const.sidereal_year
        dhasa_lord = _next_adhipati(dhasa_lord)
        _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]
    return dhasa_info
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.tara_dhasa_test()