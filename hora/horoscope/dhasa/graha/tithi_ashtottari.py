"""
Calculates Tithi Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana
"""

import swisseph as swe
from collections import OrderedDict as Dict
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house
sidereal_year = const.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = 108
""" 
    {ashtottari adhipati:[(tithis),dasa_length]} 
"""
ashtottari_adhipathi_list = [0,1,2,3,6,4,7,5]
ashtottari_adhipathi_dict = {0:[(1,9,16,24),6],1:[(2,10,17,25),15],2:[(3,11,18,26),8],3:[(4,12,19,27),17],
                             6:[(7,15,22),10],4:[(5,13,20,28),19],7:[(8,23,30),12],5:[(6,14,21,29),21]}
def ashtottari_adhipathi(tithi_index):
    for key,(tithi_list,durn) in ashtottari_adhipathi_dict.items():
        if tithi_index in tithi_list:
            return key,durn 
def ashtottari_dasha_start_date(jd,place):
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    tit = drik.tithi(jd, place)
    t_frac = utils.get_fraction(tit[1], tit[2], birth_time_hrs)
    #print('tithi',tit,'birth_time_hrs',birth_time_hrs,'tithi_fracion',t_frac)
    lord,res = ashtottari_adhipathi(tit[0])          # ruler of current nakshatra
    period_elapsed = (1-t_frac)*res*sidereal_year
    start_jd = jd - period_elapsed      # so many days before current day
    #print('lord,res,period_elapsed,start_date',lord,res,period_elapsed,utils.jd_to_gregorian(start_date))
    return [lord, start_jd]
def ashtottari_next_adhipati(lord):
    """Returns next lord after `lord` in the adhipati_list"""
    current = ashtottari_adhipathi_list.index(lord)
    #print(current)
    next_index = (current + 1) % len(ashtottari_adhipathi_list)
    #print(next_index)
    return list(ashtottari_adhipathi_dict.keys())[next_index]
def ashtottari_mahadasa(jd,place):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    lord, start_date = ashtottari_dasha_start_date(jd,place)
    retval = Dict()
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        #print('lord,lord_duration',lord,lord_duration)
        start_date += lord_duration * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def ashtottari_bhukthi(dhasa_lord, start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa and its start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = ashtottari_next_adhipati(dhasa_lord) # For Ashtottari first bhukkti starts from dhasa's next lord
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        start_date += factor * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def ashtottari_anthara(dhasa_lord, bhukthi_lord,bhukthi_lord_start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa, its bhukthi lord and bhukthi_lord's start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = ashtottari_next_adhipati(bhukthi_lord) # For Ashtottari first bhukkti starts from dhasa's next lord
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        bhukthi_lord_start_date += factor * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def get_ashtottari_dhasa_bhukthi(jd, place,use_tribhagi_variation=False):
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_ashtottari_dhasa
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_ashtottari_dhasa *= _tribhagi_factor
        for k,(v1,v2) in ashtottari_adhipathi_dict.items():
            ashtottari_adhipathi_dict[k] = [v1,round(v2*_tribhagi_factor,2)]
    city,lat,long,tz = place
    jdut1 = jd# - tz/24
    dashas = ashtottari_mahadasa(jdut1,place)
    #print('dasha lords',dashas)
    dhasa_bhukthi=[]
    for i in dashas:
        #print(i, dashas[i])
        bhukthis = ashtottari_bhukthi(i, dashas[i])
        #print(bhukthis)
        dhasa_lord = i
        for j in bhukthis:
            bhukthi_lord = j
            jd1 = bhukthis[j]+tz/24
            y, m, d, h = utils.jd_to_gregorian(jd1)#swe.revjul(round(jd1 + tz/24))
            """ TODO: Need to figure out passing date and time string to UI, main.py and pvr_tests.py """
            date_str = '%04d-%02d-%02d' %(y,m,d)+' '+utils.to_dms(h,as_string=True)
            bhukthi_start = date_str
            dhasa_bhukthi.append([dhasa_lord,bhukthi_lord,bhukthi_start]) 
            #dhasa_bhukthi[i][j] = [dhasa_lord,bhukthi_lord,bhukthi_start]
    return dhasa_bhukthi
'------ main -----------'
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.tithi_ashtottari_tests()