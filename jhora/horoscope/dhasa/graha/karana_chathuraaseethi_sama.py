from hora import const, utils
from hora.panchanga import drik
sidereal_year = const.sidereal_year
""" Karana Based Chathuraaseethi Sama Dasa """

seed_star = 15 # Swaathi
seed_lord = 0
dhasa_adhipathi_list = {k:12 for k in range(7)} # duration 12 years Total 84 years
dhasa_adhipathi_dict = const.karana_lords
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def _dhasa_adhipathi(karana_index):
    for key,(karana_list,durn) in dhasa_adhipathi_dict.items():
        if karana_index in karana_list:
            return key,durn 
def _next_adhipati(lord):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + 1) % len(dhasa_adhipathi_list))]
    return next_lord
def _maha_dhasa(nak):
    return [(_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord]) for _dhasa_lord,_star_list in dhasa_adhipathi_dict.items() if nak in _star_list][0]
def _antardhasa(lord):
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord)
    return _bhukthis
def _dhasa_start(jd,place):
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    _kar = drik.karana(jd, place)
    k_frac = utils.get_fraction(_kar[1], _kar[2], birth_time_hrs)
    #print('tithi',tit,'birth_time_hrs',birth_time_hrs,'tithi_fracion',t_frac)
    lord,res = _dhasa_adhipathi(_kar[0])          # ruler of current nakshatra
    period_elapsed = (1-k_frac)*res*sidereal_year
    start_date = jd - period_elapsed      # so many days before current day
    #print('lord,res,period_elapsed,start_date',lord,res,period_elapsed,utils.jd_to_gregorian(start_date))
    return [lord, start_date,res]
def get_dhasa_bhukthi(dob,tob,place,include_antardhasa=True,use_tribhagi_variation=False):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    _tribhagi_factor = 1.
    _dhasa_cycles = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.; _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
    jd = utils.julian_day_number(dob, tob)
    timezone = place.timezone
    """ Dhasa start jd changed to UTC based to almost match JHora V2.8.9 """
    jd_utc = jd - place.timezone / 24.
    dhasa_lord, start_jd,_ = _dhasa_start(jd_utc,place)
    retval = []
    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            _dhasa_duration = round(dhasa_adhipathi_list[dhasa_lord]*_tribhagi_factor,2)
            if include_antardhasa:
                bhukthis = _antardhasa(dhasa_lord)
                _dhasa_duration /= len(bhukthis)
                for bhukthi_lord in bhukthis:
                    y,m,d,h = utils.jd_to_gregorian(start_jd+timezone/24)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    #dhasa_start = (y,m,d,h)
                    retval.append((dhasa_lord,bhukthi_lord,dhasa_start,_dhasa_duration))
                    start_jd += _dhasa_duration * sidereal_year
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd+timezone/24)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                #dhasa_start = (y,m,d,h)
                retval.append((dhasa_lord,dhasa_start,_dhasa_duration))
                lord_duration = round(dhasa_adhipathi_list[dhasa_lord]*_tribhagi_factor,2)
                start_jd += lord_duration * sidereal_year
            dhasa_lord = _next_adhipati(dhasa_lord)
    return retval
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.karana_chathuraseethi_sama_test()
