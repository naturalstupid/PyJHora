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
from jhora import const, utils
from jhora.panchanga import drik
year_duration = const.sidereal_year
""" Karana Based Chathuraaseethi Sama Dasa """

seed_lord = 0
dhasa_adhipathi_dict = {key: const.karana_lords[key] for key in list(const.karana_lords.keys())[:-2]} # Exclude Rahu and Ketu V4.2.7
dhasa_adhipathi_list = {k:12 for k in range(len(dhasa_adhipathi_dict))} # duration 12 years Total 84 years
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def _dhasa_adhipathi(karana_index):
    for key,(karana_list,durn) in dhasa_adhipathi_dict.items():
        if karana_index in karana_list:
            return key,durn 
def _next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dirn) % len(dhasa_adhipathi_list))]
    return next_lord
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
def _dhasa_start(jd,place):
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    _kar = drik.karana(jd, place)
    k_frac = utils.get_fraction(_kar[1], _kar[2], birth_time_hrs)
    lord,res = _dhasa_adhipathi(_kar[0])# V4.2.6
    period_elapsed = (1-k_frac)*res*year_duration
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date,res]

def get_dhasa_bhukthi(
    dob, tob, place,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True      # NEW: round only returned durations; internal calcs use full precision
):
    """
        provides karana chathuraaseethi sama dhasa bhukthi for a given date in julian day (includes birth time)

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param divisional_chart_factor: Default=1
        @param chart_method: Default=1
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_level_index: Depth (1..6)
            1 = Maha only (no Antara)
            2 = + Antara (Bhukthi)
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara
        @param round_duration: If True, round only the returned duration values to const.DHASA_DURATION_ROUNDING_TO

        @return:
            if dhasa_level_index == 1:
                [ (l1, start_str, dur_years), ... ]
            else:
                [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
            (the tuple grows by one lord per requested level)
    """
    # --- original setup preserved ---
    _tribhagi_factor = 1.
    _dhasa_cycles = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd = utils.julian_day_number(dob, tob)
    dhasa_lord, start_jd, _ = _dhasa_start(jd, place)

    retval = []

    # Use your existing antara ordering at every level
    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option))

    # Nested partition of the immediate parent; internal calcs use full precision
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return

        child_dur_unrounded = parent_duration_years / len(bhukthis)  # equal split (your antara logic)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper: each child becomes the parent for next level
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            # leaf rows: round only the returned duration if requested
            for blord in bhukthis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                durn = round(child_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else child_dur_unrounded
                retval.append(prefix + (blord, start_str, durn))
                jd_cursor += child_dur_unrounded * year_duration

    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            # Maha duration — full precision internally; round only when returning
            maha_dur_unrounded = dhasa_adhipathi_list[dhasa_lord] * _tribhagi_factor

            if dhasa_level_index == 1:
                start_str = utils.julian_day_to_date_time_string(start_jd)
                durn = round(maha_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur_unrounded
                retval.append((dhasa_lord, start_str, durn))
                start_jd += maha_dur_unrounded * year_duration
            else:
                _recurse(
                    level=2,
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_duration_years=maha_dur_unrounded,
                    prefix=(dhasa_lord,)
                )
                start_jd += maha_dur_unrounded * year_duration

            dhasa_lord = _next_adhipati(dhasa_lord)  # dirn=1 for dhasa sequence

    return retval
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.karana_chathuraseethi_sama_test()
