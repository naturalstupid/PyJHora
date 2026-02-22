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
        Calculates Tithi Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana
        Ref: https://www.indiadivine.org/content/topic/1488164-vedavyasa-tithi-ashtottari-dasa-tutorial/

"""

import swisseph as swe
from collections import OrderedDict as Dict
from jhora import const,utils
from jhora.panchanga import drik
from jhora.horoscope.chart import house
year_duration = const.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = 108
""" 
    {ashtottari adhipati:[(tithis),dasa_length]} 
"""
ashtottari_adhipathi_list = [0,1,2,3,6,4,7,5]
ashtottari_adhipathi_dict = {0:[(1,9,16,24),6],1:[(2,10,17,25),15],2:[(3,11,18,26),8],3:[(4,12,19,27),17],
                             6:[(7,15,22),10],4:[(5,13,20,28),19],7:[(8,23,30),12],5:[(6,14,21,29),21]}
def _ashtottari_adhipathi(tithi_index):
    for key,(tithi_list,durn) in ashtottari_adhipathi_dict.items():
        if tithi_index in tithi_list:
            return key,durn 
def _ashtottari_dasha_start_date(jd,place,tithi_index=1):
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    tit = drik.tithi(jd, place,tithi_index=tithi_index)
    t_frac = utils.get_fraction(tit[1], tit[2], birth_time_hrs)
    lord,res = _ashtottari_adhipathi(tit[0])          # ruler of current nakshatra
    period_elapsed = (1-t_frac)*res*year_duration
    start_jd = jd - period_elapsed      # so many days before current day
    return [lord, start_jd]
def _ashtottari_next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = ashtottari_adhipathi_list.index(lord)
    next_index = (current + dirn) % len(ashtottari_adhipathi_list)
    return list(ashtottari_adhipathi_dict.keys())[next_index]
def ashtottari_mahadasa(jd,place,tithi_index):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    lord, start_date = _ashtottari_dasha_start_date(jd,place,tithi_index)
    retval = Dict()
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        start_date += lord_duration * year_duration
        lord = _ashtottari_next_adhipati(lord)
    return retval
def ashtottari_bhukthi(dhasa_lord, start_date,antardhasa_option=3):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa and its start date
    """
    lord = dhasa_lord
    if antardhasa_option in [3,4]:
        lord = _ashtottari_next_adhipati(lord, dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = _ashtottari_next_adhipati(lord, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    #lord = _ashtottari_next_adhipati(dhasa_lord,dirn) # For Ashtottari first bhukkti starts from dhasa's next lord
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        start_date += factor * year_duration
        lord = _ashtottari_next_adhipati(lord,dirn)
    return retval
def ashtottari_anthara(dhasa_lord, bhukthi_lord,bhukthi_lord_start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa, its bhukthi lord and bhukthi_lord's start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = _ashtottari_next_adhipati(bhukthi_lord) # For Ashtottari first bhukkti starts from dhasa's next lord
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        bhukthi_lord_start_date += factor * year_duration
        lord = _ashtottari_next_adhipati(lord)
    return retval

def get_ashtottari_dhasa_bhukthi(
    jd, place,
    use_tribhagi_variation=False,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara, 3..6 deeper)
    tithi_index=1,
    antardhasa_option=3
):
    """
        provides Tithi Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        This is Ashtottari Dhasa based on tithi instead of nakshathra

        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param dhasa_level_index: Depth level (1..6)
            1 = Maha only (no Antardasha)
            2 = + Antardasha (Bhukthi)    [Default]
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara
        @param tithi_index: 1=>Janma, 2=>Dhana, 3=>Bhratri, 4=>Matri, 5=>Putra, 6=>Satru, 7=>Kalatra, 8=>Mrutyu,
                           9=>Bhagya, 10=>Karma, 11=>Laabha, 12=>Vyaya
        @param antardhasa_option:
            1 => dhasa lord - forward
            2 => dhasa lord - backward
            3 => next dhasa lord - forward (Default)
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward

        @return:
          If dhasa_level_index==1: [ [dhasa_lord, start_str], ... ]
          If dhasa_level_index==2: [ [dhasa_lord, bhukthi_lord, start_str], ... ]
          If dhasa_level_index>=3: [ [l1, l2, l3, ..., start_str], ... ]  (variable-length lists)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    global human_life_span_for_ashtottari_dhasa
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        # Preserve your original behavior: mutate global H and scale each adhipati year
        human_life_span_for_ashtottari_dhasa *= _tribhagi_factor
        for k, (v1, v2) in ashtottari_adhipathi_dict.items():
            ashtottari_adhipathi_dict[k] = [v1, round(v2 * _tribhagi_factor, 2)]

    # Tithi-based maha start dates (unchanged helper)
    dashas = ashtottari_mahadasa(jd, place, tithi_index)

    dhasa_bhukthi = []
    H = human_life_span_for_ashtottari_dhasa  # 108 (or scaled by tribhāgī)
    # We will need the year length; this module defines `year_duration = const.sidereal_year`
    # and we retain it.

    # -- Child ordering: same antara start & direction as regular Ashtottari --
    def _child_start_and_dir(parent_lord):
        lord = parent_lord
        if antardhasa_option in [3, 4]:
            lord = _ashtottari_next_adhipati(parent_lord, dirn=1)
        elif antardhasa_option in [5, 6]:
            lord = _ashtottari_next_adhipati(parent_lord, dirn=-1)
        dirn = 1 if antardhasa_option in [1, 3, 5] else -1
        return lord, dirn

    def _children_of(parent_lord, parent_start_jd, parent_years):
        """
        One full child cycle under `parent_lord`, nested partition:
          child_years = parent_years * (Y(child)/H),
        marching from the start child and direction defined by antardhasa_option.
        Y(child) is taken from ashtottari_adhipathi_dict[child][1].
        """
        start_lord, dirn = _child_start_and_dir(parent_lord)
        jd_cursor = parent_start_jd
        lord = start_lord
        for _ in range(len(ashtottari_adhipathi_list)):
            Y = ashtottari_adhipathi_dict[lord][1]
            dur_yrs = parent_years * (Y / H)
            yield (lord, jd_cursor, dur_yrs)
            jd_cursor += dur_yrs * year_duration
            lord = _ashtottari_next_adhipati(lord, dirn)

    # -- Depth handling --
    for _ in range(_dhasa_cycles):
        # L1 (Maha only)
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            for lord in dashas:
                jd1 = dashas[lord]
                dhasa_bhukthi.append([lord, utils.julian_day_to_date_time_string(jd1)])
            continue

        # L2 (Maha + Antara): reuse your existing antara helper for exact legacy starts
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            for lord in dashas:
                bhukthis = ashtottari_bhukthi(lord, dashas[lord], antardhasa_option)
                for blord in bhukthis:
                    jd1 = bhukthis[blord]
                    dhasa_bhukthi.append([lord, blord, utils.julian_day_to_date_time_string(jd1)])
            continue

        # L3..L6: nested expansion using the same antara rule at each level
        def _recurse(level, parent_lord, parent_start_jd, parent_years, prefix, out_rows):
            if level < dhasa_level_index:
                # produce one child cycle and recurse deeper
                for clord, cstart, cyears in _children_of(parent_lord, parent_start_jd, parent_years):
                    _recurse(level + 1, clord, cstart, cyears, prefix + [clord], out_rows)
            else:
                # leaf: emit lords... + start string
                for clord, cstart, _cyears in _children_of(parent_lord, parent_start_jd, parent_years):
                    out_rows.append(prefix + [clord, utils.julian_day_to_date_time_string(cstart)])

        for lord in dashas:
            maha_start = dashas[lord]
            maha_years = ashtottari_adhipathi_dict[lord][1]  # in years (already tribhāgī-scaled above if used)
            if dhasa_level_index == const.MAHA_DHASA_DEPTH.PRATYANTARA:
                # Fast path for L3: expand one level beyond antara
                for blord, bstart, byears in _children_of(lord, maha_start, maha_years):
                    for plord, pstart, _py in _children_of(blord, bstart, byears):
                        dhasa_bhukthi.append([lord, blord, plord, utils.julian_day_to_date_time_string(pstart)])
            else:
                # Generic recursion for L4..L6
                _recurse(
                    level=const.MAHA_DHASA_DEPTH.PRATYANTARA,
                    parent_lord=lord,
                    parent_start_jd=maha_start,
                    parent_years=maha_years,
                    prefix=[lord],
                    out_rows=dhasa_bhukthi
                )

    return dhasa_bhukthi

'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.tithi_ashtottari_tests()
    