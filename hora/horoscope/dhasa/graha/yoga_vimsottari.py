"""
Calculates Yoga Vimsottari
"""
from collections import OrderedDict as Dict
from hora import const,utils
from hora.panchanga import drik
sidereal_year = const.sidereal_year #const.savana_year #  # some say 360 days, others 365.25 or 365.2563 etc
vimsottari_dict = { 8:[(3,12,21), 7], 5: [(4,13,22),20], 0:[(5,14,23), 6], 1:[(6,15,24), 10], 2:[(7,16,25), 7], 
                   7:[(8,17,26), 18], 4:[(9,18,27), 16], 6:[(1,10,19), 19], 3:[(2,11,20), 17] }
human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa
### --- Vimoshatari functions
def vimsottari_adhipathi(yoga_index):
    for key,(yoga_list,durn) in vimsottari_dict.items():
        if yoga_index in yoga_list:
            return key,durn 
def vimsottari_next_adhipati(lord):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + 1) % len(const.vimsottari_adhipati_list)
    return const.vimsottari_adhipati_list[next_index]

def vimsottari_dasha_start_date(jd,place):
    """Returns the start date of the mahadasa which occured on or before `jd`"""
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    _yoga = drik.yogam(jd, place)
    y_frac = utils.get_fraction(_yoga[1], _yoga[2], birth_time_hrs)
    #print('yoga',_yoga,'birth_time_hrs',birth_time_hrs,'yoga_fracion',y_frac)
    lord,res = vimsottari_adhipathi(_yoga[0])          # ruler of current nakshatra
    period_elapsed = (1-y_frac)*res*sidereal_year
    start_jd = jd - period_elapsed      # so many days before current day
    #print('lord,res,period_elapsed,start_date',lord,res,period_elapsed,utils.jd_to_gregorian(start_date))
    return [lord, start_jd]

def vimsottari_mahadasa(jdut1,place):
    """List all mahadashas and their start dates"""
    lord, start_date = vimsottari_dasha_start_date(jdut1,place)
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date; lord_duration = vimsottari_dict[lord][1]
        start_date += lord_duration * sidereal_year
        lord = vimsottari_next_adhipati(lord)
    return retval

def _vimsottari_bhukti(maha_lord, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord; dhasa_lord_duration = vimsottari_dict[maha_lord][1]
    retval = Dict()
    for i in range(len(vimsottari_dict)):
        retval[lord] = start_date; bhukthi_duration = vimsottari_dict[lord][1]
        factor = bhukthi_duration * dhasa_lord_duration / human_life_span_for_vimsottari_dhasa
        start_date += factor * sidereal_year
        lord = vimsottari_next_adhipati(lord)

    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def _vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * (vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa)
        factor *= (vimsottari_dict[bhukti_lord] / human_life_span_for_vimsottari_dhasa)
        start_date += factor * sidereal_year
        lord = vimsottari_next_adhipati(lord)

    return retval


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


def compute_vimsottari_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = _where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = _vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = _where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = _vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)

def get_dhasa_bhukthi(jd,place,use_tribhagi_variation=False):
    """
        provides Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_vimsottari_dhasa
    # jd is julian date with birth time included
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_vimsottari_dhasa *= _tribhagi_factor
        for k,v in vimsottari_dict.items():
            vimsottari_dict[k] = round(v*_tribhagi_factor,2)
    city,lat,long,tz = place
    jdut1 = jd - tz/24
    dashas = vimsottari_mahadasa(jdut1,place)
    dl = list(dashas.values()); de = dl[1]
    y,m,h,_ = utils.jd_to_gregorian(jd); p_date1 = drik.Date(y,m,h)
    y,m,h,_ = utils.jd_to_gregorian(de); p_date2 = drik.Date(y,m,h)
    vim_bal = utils.panchanga_date_diff(p_date1, p_date2)
    #print('dasha lords',dashas)
    dhasa_bukthi=[]
    for _ in range(_dhasa_cycles):
        for i in dashas:
            #print(' ---------- ' + get_dhasa_name(i) + ' ---------- ')
            bhuktis = _vimsottari_bhukti(i, dashas[i])
            dhasa_lord = i
            for j in bhuktis:
                bhukthi_lord = j
                jd1 = bhuktis[j]+tz/24
                y, m, d, h = utils.jd_to_gregorian(jd1)#swe.revjul(round(jd1 + tz/24))
                """ TODO: Need to figure out passing date and time string to UI, main.py and pvr_tests.py """
                date_str = '%04d-%02d-%02d' %(y,m,d)+' '+utils.to_dms(h,as_string=True)
                bhukthi_start = date_str
                dhasa_bukthi.append([dhasa_lord,bhukthi_lord,bhukthi_start]) 
                #dhasa_bukthi[i][j] = [dhasa_lord,bhukthi_lord,bhukthi_start]
    return vim_bal,dhasa_bukthi

'------ main -----------'
if __name__ == "__main__":
    from hora import utils
    from hora.horoscope.chart import charts
    drik.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
    dob = drik.Date(1996,12,7)
    tob = (10,34,0)
    place = drik.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    jd = utils.julian_day_number(dob,tob)
    pp = charts.rasi_chart(jd, place)
    vim_bal,db = get_dhasa_bhukthi(jd, place,use_tribhagi_variation=False)
    print('yoga vimsottari balance',vim_bal)
    for d,b,s in db:
        print(d,b,s)
    exit()
    from hora.tests import pvr_tests
    pvr_tests._vimsottari_test_1()
    pvr_tests._vimsottari_test_2()
    pvr_tests._vimsottari_test_3()
    pvr_tests._vimsottari_test_4()
    pvr_tests._vimsottari_test_5()
    exit()

