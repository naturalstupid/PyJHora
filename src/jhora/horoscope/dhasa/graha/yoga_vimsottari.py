#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
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
Calculates Yoga Vimsottari
"""
from collections import OrderedDict as Dict
from jhora import const,utils
from jhora.panchanga import drik
sidereal_year = const.sidereal_year #const.savana_year #  # some say 360 days, others 365.25 or 365.2563 etc
vimsottari_dict = { 8:[(3,12,21), 7], 5: [(4,13,22),20], 0:[(5,14,23), 6], 1:[(6,15,24), 10], 2:[(7,16,25), 7], 
                   7:[(8,17,26), 18], 4:[(9,18,27), 16], 6:[(1,10,19), 19], 3:[(2,11,20), 17] }
human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa
### --- Vimoshatari functions
def vimsottari_adhipathi(yoga_index):
    for key,(yoga_list,durn) in vimsottari_dict.items():
        if yoga_index in yoga_list:
            return key,durn 
def vimsottari_next_adhipati(lord,dirn=1):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + dirn) % len(const.vimsottari_adhipati_list)
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

def _vimsottari_bhukti(maha_lord, start_date,antardhasa_option=1):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    if antardhasa_option in [3,4]:
        lord = vimsottari_next_adhipati(lord, dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = vimsottari_next_adhipati(lord, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    dhasa_lord_duration = vimsottari_dict[maha_lord][1]
    retval = Dict()
    for _ in range(len(vimsottari_dict)):
        retval[lord] = start_date; bhukthi_duration = vimsottari_dict[lord][1]
        factor = bhukthi_duration * dhasa_lord_duration / human_life_span_for_vimsottari_dhasa
        start_date += factor * sidereal_year
        lord = vimsottari_next_adhipati(lord,dirn)

    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def _vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = Dict()
    for _ in range(9):
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

def get_dhasa_bhukthi(jd,place,use_tribhagi_variation=False,antardhasa_option=1):
    """
        provides Yoga Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        This is vimsottari but based on yogam instead of nakshathra
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param antardhasa_option:
            1 => dhasa lord - forward
            2 => dhasa lord - backward
            3 => next dhasa lord - forward (Default)
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_vimsottari_dhasa
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_vimsottari_dhasa *= _tribhagi_factor
        for k,v in vimsottari_dict.items():
            vimsottari_dict[k] = round(v*_tribhagi_factor,2)
    _,_,_,tz = place
    dashas = vimsottari_mahadasa(jd,place)#V4.2.9
    dl = list(dashas.values()); de = dl[1]
    y,m,h,_ = utils.jd_to_gregorian(jd); p_date1 = drik.Date(y,m,h)
    y,m,h,_ = utils.jd_to_gregorian(de); p_date2 = drik.Date(y,m,h)
    vim_bal = utils.panchanga_date_diff(p_date1, p_date2)
    dhasa_bukthi=[]
    for _ in range(_dhasa_cycles):
        for i in dashas:
            bhuktis = _vimsottari_bhukti(i, dashas[i],antardhasa_option=antardhasa_option)
            dhasa_lord = i
            for j in bhuktis:
                bhukthi_lord = j
                jd1 = bhuktis[j]
                y, m, d, h = utils.jd_to_gregorian(jd1)
                """ TODO: Need to figure out passing date and time string to UI, main.py and pvr_tests.py """
                date_str = '%04d-%02d-%02d' %(y,m,d)+' '+utils.to_dms(h,as_string=True)
                bhukthi_start = date_str
                dhasa_bukthi.append([dhasa_lord,bhukthi_lord,bhukthi_start]) 
    return vim_bal,dhasa_bukthi

'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.yoga_vimsottari_tests()

