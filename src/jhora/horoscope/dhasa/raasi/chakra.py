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
""" Chakra Dhasa """
"""
    Antardasa/Bhukthi Lords do not match with JHora - as it is not clear how it is implemented there
    So we start with mahadasa lord as the bhukthi lord.
"""
from jhora.panchanga import drik
from jhora import utils, const
_dhasa_duration = 10.0; _bhukthi_duration = _dhasa_duration/12.0
year_duration = const.sidereal_year

def _dhasa_seed(jd,place,lagna_house,lagna_lord_house):
    previous_day_sunset_time = drik.sunset(jd-1, place)[0]
    today_sunset_time = drik.sunset(jd, place)[0]
    today_sunrise_time = drik.sunrise(jd, place)[0]
    tomorrow_sunrise_time = 24.0+drik.sunrise(jd+1, place)[0]
    _,_,_,birth_time = utils.jd_to_gregorian(jd)
    df = abs(today_sunset_time - today_sunrise_time)/6.0
    nf1 = abs(today_sunrise_time-previous_day_sunset_time)/6.0
    nf2 = abs(tomorrow_sunrise_time-today_sunset_time)/6.0
    #print('df',df,'nf1',nf1,'nf2',nf2)
    dawn_start = today_sunrise_time-nf1; dawn_end=today_sunrise_time+nf1
    #print('dawn',dawn_start,dawn_end)
    day_start = dawn_end; day_end = today_sunset_time-nf1
    #print('day',day_start,day_end)
    dusk_start = day_end ; dusk_end = today_sunset_time+nf2
    #print('dusk',dusk_start,dusk_end)
    yday_night_start = -(previous_day_sunset_time+nf1); yday_night_end = today_sunrise_time-nf1
    tonight_start = today_sunset_time+nf2; tonight_end = tomorrow_sunrise_time-nf2
    #print('Night-Yday',yday_night_start,yday_night_end,'Night-today',tonight_start,tonight_end)
    # Night is before dawn_start and after dusk_end
    if birth_time > dawn_start and birth_time < dawn_end: # dawn
        kaala_period = 'Dawn'
        _dhasa_seed = (lagna_house+1)%12
    elif birth_time > dusk_start and birth_time < dusk_end: # dusk
        kaala_period = 'Dusk'
        _dhasa_seed = (lagna_house+1)%12
    elif birth_time > day_start and birth_time < day_end: # Day
        kaala_period = 'Day'
        _dhasa_seed = lagna_lord_house
    elif birth_time > yday_night_start and birth_time < yday_night_end: # yday-night
        kaala_period = 'YDay-Night'
        _dhasa_seed = lagna_house
    elif birth_time > tonight_start and birth_time < tonight_end: # yday-night
        kaala_period = 'ToNight'
        _dhasa_seed = lagna_house    
    return _dhasa_seed

def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1, years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6: 1=Maha only, 2=+Antara (default), 3..6 deeper
    round_duration=True                               # round only returned durations; JD math stays full precision
):
    """
    Chakra daśā with multi-level depth (Maha → Antara → Pratyantara → …)

    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)       [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

    Duration policy:
      - Maha duration (years) = _dhasa_duration(planet_positions, sign)  [your original helper].
      - At every deeper level, the IMMEDIATE parent is split into 12 equal parts (Σchildren = parent).
    Ordering:
      - Maha sequence: 12 signs starting from dhasa_seed (or your reversed cycle if seed is even).
      - At each node, children = 12 signs in cyclic order starting from the *parent* sign.
    """
    # ---- safety ----------------------------------------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- annual epoch (bugfix: pass the correct sixty_hours) -------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_years  = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)

    # ---- base chart (unchanged seed machinery) --------------------------------
    from jhora.horoscope.chart import charts, house
    pp = charts.divisional_chart(jd_years, place, divisional_chart_factor=divisional_chart_factor)
    lagna_house      = pp[0][1][0]
    lagna_lord       = house.house_owner_from_planet_positions(pp, lagna_house)
    lagna_lord_house = pp[lagna_lord + 1][1][0]

    # seed is for MAHA only—do not recompute it at deeper levels
    dhasa_seed = _dhasa_seed(jd_years, place, lagna_house, lagna_lord_house)

    # maha sequence (12 signs) starting from seed
    maha_signs = [(dhasa_seed + h) % 12 for h in range(12)]

    # children at any node: 12 signs starting from parent sign
    def _children_from(parent_sign):
        return [(parent_sign + k) % 12 for k in range(12)]

    # choose rounding precision; default to 2 if constant absent
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        """
        Depth >= 3:
          - child order: cyclic from parent_sign
          - child duration: parent_years / 12
        """
        bhuktis = _children_from(parent_sign)
        child_unrounded = parent_years / 12.0
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for child_sign in bhuktis:
                _recurse(level + 1, child_sign, jd_cursor, child_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_unrounded * year_duration
        else:
            for child_sign in bhuktis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret   = round(child_unrounded, _round_ndigits) if round_duration else child_unrounded
                out_rows.append(prefix + (child_sign, start_str, dur_ret))
                jd_cursor += child_unrounded * year_duration

    # ---- build rows per requested depth ---------------------------------------
    rows   = []
    jd_cur = jd_years

    for maha_sign in maha_signs:
        maha_years = _dhasa_duration
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Maha only
            start_str = utils.julian_day_to_date_time_string(jd_cur)
            dur_ret   = round(maha_years, _round_ndigits) if round_duration else maha_years
            rows.append((maha_sign, start_str, dur_ret))
            jd_cur += maha_years * year_duration
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antara — equal split of Maha into 12, children ordered from maha_sign
            child_unrounded = maha_years / 12.0
            jd_b = jd_cur
            for antara_sign in _children_from(maha_sign):
                start_str = utils.julian_day_to_date_time_string(jd_b)
                dur_ret   = round(child_unrounded, _round_ndigits) if round_duration else child_unrounded
                rows.append((maha_sign, antara_sign, start_str, dur_ret))
                jd_b += child_unrounded * year_duration
            jd_cur += maha_years * year_duration
            continue

        # L3..L6: recursive equal-split below immediate parent
        _recurse(
            level=const.MAHA_DHASA_DEPTH.ANTARA,   # = 2; build 3..N
            parent_sign=maha_sign,
            parent_start_jd=jd_cur,
            parent_years=maha_years,
            prefix=(maha_sign,),
            out_rows=rows
        )
        jd_cur += maha_years * year_duration

    return rows

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chakra_test()