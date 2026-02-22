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
""" Tithi Yogini Dasa """
""" TODO: To implement in jhora.panchanga.drik general tithi based on any 2 planets and call here """
from jhora import const, utils
from jhora.panchanga import drik
year_duration = const.sidereal_year
""" dhasa_adhipathi_dict = {planet:[(tithi list), dhasa duration] } """
seed_star = 7
seed_lord = 0
dhasa_adhipathi_list = {1:1,0:2,4:3,2:4,3:5,6:6,5:7,7:8} # Total 36 years
dhasa_adhipathi_dict = {0:[(1,9,16,24),2],1:[(2,10,17,25),1],2:[(3,11,18,26),4],3:[(4,12,19,27),5],
                             6:[(7,15,22),6],4:[(5,13,20,28),3],7:[(8,23,30),8],5:[(6,14,21,29),7]}
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def yogini_adhipathi(tithi_index):
    for key,(tithi_list,durn) in dhasa_adhipathi_dict.items():
        if tithi_index in tithi_list:
            return key,durn 
def _next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dirn) % len(dhasa_adhipathi_list))]
    return next_lord

def _get_dhasa_dict():
    dhasa_dict = {k:[] for k in dhasa_adhipathi_list.keys()}
    nak = seed_star-1
    lord = seed_lord
    lord_index = list(dhasa_adhipathi_list.keys()).index(lord)
    for _ in range(27):
        dhasa_dict[lord].append(nak+1)
        nak = (nak+1*count_direction)%27
        lord_index = (lord_index+1) % len(dhasa_adhipathi_list)
        lord = list(dhasa_adhipathi_list.keys())[lord_index]
    return dhasa_dict
#dhasa_adhipathi_dict = _get_dhasa_dict()
def _maha_dhasa(nak):
    return [(_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord]) for _dhasa_lord,_star_list in dhasa_adhipathi_dict.items() if nak in _star_list][0]
def _antardhasa(dhasa_lord,antardhasa_option=1):
    lord = dhasa_lord
    if antardhasa_option in [3,4]:
        lord = _next_adhipati(dhasa_lord, dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = _next_adhipati(dhasa_lord, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord,dirn)
    return _bhukthis
def _dhasa_start(jd,place,tithi_index=1):
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    tit = drik.tithi(jd, place,tithi_index)
    t_frac = utils.get_fraction(tit[1], tit[2], birth_time_hrs)
    lord,res = yogini_adhipathi(tit[0])          # ruler of current nakshatra
    period_elapsed = (1-t_frac)*res*year_duration
    start_jd = jd - period_elapsed      # so many days before current day
    return [lord, start_jd,res]

def get_dhasa_bhukthi(
    dob, tob, place,
    use_tribhagi_variation=False,
    tithi_index=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara, ..., 6=+Deha)
    round_duration=True                               # Round only returned durations; internal calcs full precision
):
    """
        provides Tithi Yogini dhasa bhukthi for a given date in julian day (includes birth time)
        This is Ashtottari Dhasa based on tithi instead of nakshatra.

        @param dob: date of birth (Y, M, D)
        @param tob: time of birth (h, m, s)
        @param place: Place(name, latitude, longitude, timezone)
        @param use_tribhagi_variation: False (default). True => same behavior as your legacy:
                                       increase cycle count; do NOT scale segment years.
        @param tithi_index:  1=Janma 2=Dhana 3=Bhratri 4=Matri 5=Putra 6=Satru
                             7=Kalatra 8=Mrutyu 9=Bhagya 10=Karma 11=Laabha 12=Vyaya
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_level_index: depth (1..6)
            1 = Maha only (no Antardasha)
            2 = + Antardasha (Bhukthi)
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara
        @param round_duration: if True, round only the returned durations to
                               const.DHASA_DURATION_ROUNDING_TO

        @return:
          if dhasa_level_index == 1:
            [ (l1, start_str, dur_years), ... ]
          else:
            [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
          (tuple grows by one lord per requested level)
    """
    # --- original cycle logic preserved (no other behavior changed) ---
    _tribhagi_factor = 1.0
    _dhasa_cycles = 3
    if use_tribhagi_variation:
        _tribhagi_factor = 1.0 / 3.0
        _dhasa_cycles = int(_dhasa_cycles / _tribhagi_factor)  # legacy behavior: more cycles, same per-segment years

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd = utils.julian_day_number(dob, tob)
    dhasa_lord, start_jd, _ = _dhasa_start(jd, place, tithi_index)

    retval = []

    # --- Children ordering reused at every depth (your antara rule) ---
    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option=antardhasa_option))

    # --- Nested partition of IMMEDIATE PARENT (equal split, matching your legacy antara logic) ---
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return

        n = len(bhukthis)
        child_dur_unrounded = parent_duration_years / n
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            # leaf rows: round only the returned duration; advance with full precision
            for blord in bhukthis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                durn = round(child_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else child_dur_unrounded
                retval.append(prefix + (blord, start_str, durn))
                jd_cursor += child_dur_unrounded * year_duration

    # --- Main loop (cycles preserved; per-lord years preserved) ---
    for _ in range(_dhasa_cycles):  # legacy: 3 cycles (or 9 when tribhagi=True)
        for _ in range(len(dhasa_adhipathi_list)):
            maha_dur_unrounded = dhasa_adhipathi_list[dhasa_lord]  # legacy: no tribhagi scaling here

            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                start_str = utils.julian_day_to_date_time_string(start_jd)
                durn = round(maha_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur_unrounded
                retval.append((dhasa_lord, start_str, durn))
                start_jd += maha_dur_unrounded * year_duration
            else:
                _recurse(
                    level=const.MAHA_DHASA_DEPTH.ANTARA,  # 2
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_duration_years=maha_dur_unrounded,
                    prefix=(dhasa_lord,)
                )
                start_jd += maha_dur_unrounded * year_duration

            dhasa_lord = _next_adhipati(dhasa_lord)

    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.tithi_yogini_test()
    