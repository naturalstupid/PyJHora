"""
Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
"""
import datetime
from collections import OrderedDict as Dict
import swisseph as swe
from hora import const
from hora.panchanga import panchanga
from hora.horoscope.chart import charts
from hora.horoscope.dhasa import vimsottari
sidereal_year = const.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
varsha_vimsottari_adhipati = lambda nak: const.varsha_vimsottari_adhipati_list[nak % (len(const.varsha_vimsottari_adhipati_list))]

### --- Vimoshatari functions
def varsha_vimsottari_next_adhipati(lord):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.varsha_vimsottari_adhipati_list.index(lord)
    next_index = (current + 1) % len(const.varsha_vimsottari_adhipati_list)
    next_lord = const.varsha_vimsottari_adhipati_list[next_index]
    return next_lord

def varsha_vimsottari_dasha_start_date(jd,years):
    """Returns the start date of the mahadasa which occured on or before `jd`"""
    nak, rem = panchanga.nakshatra_position(jd)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    lord = vimsottari.vimsottari_dasha_start_date(jd)[0]
    lord = (lord+years) % 9
    lord = const.varsha_vimsottari_adhipati_list[lord]
    period = const.varsha_vimsottari_days[lord]       # total years of nakshatra lord
    period_elapsed = (rem / one_star) * period # yet to be traversed in days
    start_date = jd +years*sidereal_year - period_elapsed      # so many days before current day
    return [lord, start_date]

def varsha_vimsottari_mahadasa(jdut1,years):
    """List all mahadashas and their start dates"""
    lord, start_date = varsha_vimsottari_dasha_start_date(jdut1,years)
    retval = []
    for i in range(9):
        duration = const.varsha_vimsottari_days[lord] * sidereal_year / 360.0
        retval.append((lord,start_date,duration))
        start_date += duration
        lord = varsha_vimsottari_next_adhipati(lord)
    return retval

def varsha_vimsottari_bhukti(maha_lord, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    retval = []
    for i in range(9):
        factor = const.varsha_vimsottari_days[lord] * const.varsha_vimsottari_days[maha_lord] / const.human_life_span_for_varsha_vimsottari_dhasa
        duration = factor * sidereal_year / 360.0
        start_date += duration
        retval.append((lord,start_date,round(duration,2)))
        lord = varsha_vimsottari_next_adhipati(lord)
    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def varsha_vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = []
    for i in range(9):
        factor = const.varsha_vimsottari_days[lord] * (const.varsha_vimsottari_days[maha_lord] / const.human_life_span_for_varsha_vimsottari_dhasa)
        duration = factor * (const.varsha_vimsottari_days[bhukti_lord] / const.human_life_span_for_varsha_vimsottari_dhasa)
        retval.append((lord,start_date,round(duration,2)))
        start_date += duration
        lord = varsha_vimsottari_next_adhipati(lord)
    return retval


def where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


def compute_varsha_vimsottari_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = varsha_vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = varsha_vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)

# ---------------------- ALL TESTS ------------------------------
def varsha_vimsottari_dhasa_bhukthi(jd,place,years):
    # jd is julian date with birth time included
    city,lat,long,tz = place
    jdut1 = jd - tz/24
    dashas = varsha_vimsottari_mahadasa(jdut1,years)
    print(dashas)
    dhasa_bukthi=[]
    for l,j,d in dashas:
        bhuktis = varsha_vimsottari_bhukti(l, j)
        dhasa_lord = l
        for lj,jj,dj in bhuktis:
            bhukthi_lord = lj
            jd1 = jj #bhuktis[j]
            y, m, d, h = swe.revjul(round(jd1 + tz))
            date_str = '%04d-%02d-%02d' %(y,m,d)
            bhukthi_start = date_str
            dhasa_bukthi.append((dhasa_lord,bhukthi_lord,bhukthi_start,dj)) 
    return dhasa_bukthi
def mudda_dhasa_bhukthi():
    return varsha_vimsottari_dhasa_bhukthi(jd,place,years)
'------ main -----------'
if __name__ == "__main__":
    pass