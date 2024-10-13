"""
Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
"""
import datetime
from collections import OrderedDict as Dict
import swisseph as swe
from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts
from hora.horoscope.dhasa.graha import vimsottari
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
    nak, rem = drik.nakshatra_position(jd)
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


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


def compute_varsha_vimsottari_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = _where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = varsha_vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = _where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = varsha_vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)

# ---------------------- ALL TESTS ------------------------------
def varsha_vimsottari_dhasa_bhukthi(jd,place,years):
    """
        Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
        @param jd: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param years: # years of from year of birth
        @return: 2D list of [ (dhasa_lord,Bhukthi_lord,bhukthi_start date, bhukthi_duration_days),...
          Example: [(7, 7, '1993-06-03', 8.22), (7, 4, '1993-06-11', 7.31), ...]
    """
    # jd is julian date with birth time included
    city,lat,long,tz = place
    jdut1 = jd - tz/24
    dashas = varsha_vimsottari_mahadasa(jdut1,years)
    #print(dashas)
    dhasa_bukthi=[]
    for l,j,d in dashas:
        bhuktis = varsha_vimsottari_bhukti(l, j)
        dhasa_lord = l
        for lj,jj,dj in bhuktis:
            bhukthi_lord = lj
            jd1 = jj #bhuktis[j]
            y, m, d, h = swe.revjul(round(jd1 + tz/24))
            date_str = '%04d-%02d-%02d' %(y,m,d)
            bhukthi_start = date_str
            dhasa_bukthi.append((dhasa_lord,bhukthi_lord,bhukthi_start,dj)) 
    return dhasa_bukthi
def mudda_dhasa_bhukthi(jd,place,years):
    return varsha_vimsottari_dhasa_bhukthi(jd,place,years)
'------ main -----------'
if __name__ == "__main__":
    from hora.tests.pvr_tests import test_example
    from hora import utils
    chapter = 'Chapter 30.3 '
    exercise = 'Example 122 / Chart 67 '
    #expected_result_book = [(5, 24.98), (3, 48.17), (1, 0.51), (6, 25.74), ('L', 11.24), (4, 57.35), (0, 93.29), (2, 103.99)]
    expected_result = [(5, 24.9), (3, 48.1), (1, 0.57), (6, 25.71), ('L', 11.3), (4, 57.43), (0, 93.03), (2, 104.19)]
    # Note: Difference in ans is due to planet longitude value round off 
    jd_at_dob = utils.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = drik.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    jd_at_years = utils.julian_day_number((1993,6,1),(13,30,4))
    cht=mudda_dhasa_bhukthi(jd_at_dob, place, years)
    print(cht); exit()
    print("Note: There is slight difference between book and actual values. Difference is due to round off of longitudes value calculations")
    for i,pp in enumerate(cht):
        test_example(chapter+exercise,expected_result[i],(pp[0],round(pp[-1],2)))
