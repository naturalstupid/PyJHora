# -*- coding: UTF-8 -*-

# vimsottari.py -- routines for computing time periods of vimsottari dhasa bhukthi
#
# Copyright by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Calculates Vimshottari (=120) Dasha-bhukthi-antara-sukshma-prana
"""
import datetime
from collections import OrderedDict as Dict
import swisseph as swe
from hora import const,utils
from hora.panchanga import drik
sidereal_year = const.sidereal_year #const.savana_year #  # some say 360 days, others 365.25 or 365.2563 etc
vimsottari_adhipati = lambda nak: const.vimsottari_adhipati_list[nak % (len(const.vimsottari_adhipati_list))]
vimsottari_dict = const.vimsottari_dict
human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa
### --- Vimoshatari functions
def vimsottari_next_adhipati(lord):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + 1) % len(const.vimsottari_adhipati_list)
    return const.vimsottari_adhipati_list[next_index]

def vimsottari_dasha_start_date(jd,star_position_from_moon=1):
    """Returns the start date of the mahadasa which occured on or before `jd`"""
    nak, rem = drik.nakshatra_position(jd,star_position_from_moon)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    lord = vimsottari_adhipati(nak)          # ruler of current nakshatra
    period = vimsottari_dict[lord]       # total years of nakshatra lord
    period_elapsed = rem / one_star * period # years
    period_elapsed *= sidereal_year        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date]

def vimsottari_mahadasa(jdut1,star_position_from_moon=1):
    """List all mahadashas and their start dates"""
    lord, start_date = vimsottari_dasha_start_date(jdut1,star_position_from_moon)
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        start_date += vimsottari_dict[lord] * sidereal_year
        lord = vimsottari_next_adhipati(lord)

    return retval
def _vimsottari_rasi_bhukthi(maha_lord,maha_lord_rasi,start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa using rasi bhukthi variation
    and its start date"""
    retval = Dict()
    bhukthi_duration = vimsottari_dict[maha_lord]/12
    for bhukthi_rasi in [(maha_lord_rasi+h)%12 for h in range(12)]:
        retval[bhukthi_rasi] = start_date
        start_date += bhukthi_duration * sidereal_year
    return retval
    
def _vimsottari_bhukti(maha_lord, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa
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

def get_vimsottari_dhasa_bhukthi(jd,place,star_position_from_moon=1,use_tribhagi_variation=False,
                                 use_rasi_bhukthi_variation=False):
    """
        provides Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_vimsottari_dhasa
    # jd is julian date with birth time included
    if use_rasi_bhukthi_variation:
        from hora.horoscope.chart import charts
        planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=1)
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
    dashas = vimsottari_mahadasa(jdut1,star_position_from_moon)
    dl = list(dashas.values()); de = dl[1]
    y,m,h,_ = utils.jd_to_gregorian(jd); p_date1 = drik.Date(y,m,h)
    y,m,h,_ = utils.jd_to_gregorian(de); p_date2 = drik.Date(y,m,h)
    vim_bal = utils.panchanga_date_diff(p_date1, p_date2)
    #print('dasha lords',dashas)
    dhasa_bukthi=[]
    for _ in range(_dhasa_cycles):
        for i in dashas:
            #print(' ---------- ' + get_dhasa_name(i) + ' ---------- ')
            if use_rasi_bhukthi_variation:
                maha_lord_rasi= planet_positions[i+1][1][0]
                bhuktis = _vimsottari_rasi_bhukthi(i, maha_lord_rasi, dashas[i])
            else:
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
    vim_bal,db = get_vimsottari_dhasa_bhukthi(jd, place,use_tribhagi_variation=False,use_rasi_bhukthi_variation=True)
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
