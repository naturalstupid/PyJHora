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
""" dhasa_adhipathi_dict = {planet:[(star list), dhasa duration] } """
#dhasa_adhipathi_list = [1,0,4,2,3,6,5,7]
#dhasa_adhipathi_dict = {0:[(7,15,23),2], 1:[(6,14,22),1], 2:[(1,9,17,25),4], 3:[(2,10,18,26),5], 4:[(8,16,24),3], 5:[(4,12,20),7], 6:[(3,11,19,27),6], 7:[(5,13,21),8]}
#seed_star = 7
seed_lord = 0
dhasa_adhipathi_list = {1:1,0:2,4:3,2:4,3:5,6:6,5:7,7:8} # Total 36 years
#dhasa_adhipathi_dict = {1: [14, 22, 3], 0: [7, 15, 23, 4], 4: [8, 16, 24, 5], 2: [9, 17, 25, 6], 3: [10, 18, 26], 6: [11, 19, 27], 5: [12, 20, 1], 7: [13, 21, 2]}
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def _next_adhipati(lord,dir=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dir) % len(dhasa_adhipathi_list))]
    return next_lord

def _get_dhasa_dict(seed_star=7):
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
def _maha_dhasa(nak,seed_star=7):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)
    return [(_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord]) for _dhasa_lord,_star_list in dhasa_adhipathi_dict.items() if nak in _star_list][0]
def _antardhasa(lord,antardhasa_option=1):
    if antardhasa_option in [3,4]:
        lord = _next_adhipati(lord, dir=1) 
    elif antardhasa_option in [5,6]:
        lord = _next_adhipati(lord, dir=-1) 
    dir = 1 if antardhasa_option in [1,3,5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord,dir)
    return _bhukthis
def _dhasa_start(jd,place,divisional_chart_factor=1,star_position_from_moon=1,seed_star=7,dhasa_starting_planet=1):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob=drik.Date(y,m,d); tob=(fh,0,0)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place,
                                divisional_chart_factor=divisional_chart_factor)[:const._pp_count_upto_ketu]
    if dhasa_starting_planet in const.SUN_TO_KETU:
        planet_long = planet_positions[dhasa_starting_planet+1][1][0]*30+planet_positions[dhasa_starting_planet+1][1][1]
    elif dhasa_starting_planet==const._ascendant_symbol:
        planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    elif dhasa_starting_planet.upper()=='M':
        mn = drik.maandi_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0]*30+mn[1]
    elif dhasa_starting_planet.upper()=='G':
        gl = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='B':
        gl = drik.bhrigu_bindhu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='I':
        gl = drik.indu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='P':
        gl = drik.pranapada_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='T':
        sp = sphuta.tri_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = sp[0]*30+sp[1]
    else:
        planet_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    if dhasa_starting_planet==1:
        planet_long += (star_position_from_moon-1)*one_star
    nak = int(planet_long / one_star); rem = (planet_long - nak * one_star)
    lord,res = _maha_dhasa(nak+1,seed_star)          # ruler of current nakshatra
    period = res
    period_elapsed = rem / one_star * period # years
    period_elapsed *= year_duration        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date,res]

def get_dhasa_bhukthi(
    dob, tob, place,
    use_tribhagi_variation=False,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    seed_star=7,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara, 3..6 deeper)
    round_duration=True
):
    """
        Multi-level version (L1..L6) of your Yoga-based dhasa:
          L1 -> (l1, start, dur)
          L2 -> (l1, l2, start, dur)        [DEFAULT: preserves your legacy]
          L3 -> (l1, l2, l3, start, dur)
          L4 -> (l1, l2, l3, l4, start, dur)
          L5 -> (l1, l2, l3, l4, l5, start, dur)
          L6 -> (l1, l2, l3, l4, l5, l6, start, dur)

        - Durations at lower levels equal-split the IMMEDIATE parent (your current logic).
        - Only returned durations are rounded when round_duration=True; JD math uses full precision.
        - Tribhagi cycles behavior untouched.
        - Same timestamp formatting as your original (to keep tests byte-identical).
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- Legacy tribhagi handling (unchanged) ----------------------------------
    _tribhagi_factor = 1.
    _dhasa_cycles   = 3
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles    = int(_dhasa_cycles / _tribhagi_factor)

    # ---- Start JD using your existing function ---------------------------------
    jd = utils.julian_day_number(dob, tob)
    dhasa_lord, start_jd, _ = _dhasa_start(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet
    )

    # ---- Helpers ----------------------------------------------------------------
    def _children_of(parent_lord):
        return _antardhasa(parent_lord, antardhasa_option)

    # pick the rounding places safely even if const.DHASA_DURATION_ROUNDING_TO is absent
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    def _recurse(level, parent_lord, parent_start_jd, parent_years, prefix):
        """Generic equal-split recursion for levels >= 3."""
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return
        n = len(bhukthis)
        child_unrounded = parent_years / n
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_unrounded, prefix + (blord,))
                jd_cursor += child_unrounded * year_duration
        else:
            # leaf rows
            for blord in bhukthis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret   = round(child_unrounded, _round_ndigits) if round_duration else child_unrounded
                rows.append(prefix + (blord, start_str, dur_ret))
                jd_cursor += child_unrounded * year_duration

    rows = []

    # ---- Main expansion over cycles & maha sequence -----------------------------
    for _ in range(_dhasa_cycles):  # legacy: 3 cycles (or 9 when tribhagi=True)
        for _ in range(len(dhasa_adhipathi_list)):
            maha_years_unrounded = float(dhasa_adhipathi_list[dhasa_lord])

            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                # L1: Maha only (keep your timestamp style)
                rows.append((dhasa_lord, utils.julian_day_to_date_time_string(start_jd),
                             round(maha_years_unrounded, _round_ndigits) if round_duration else maha_years_unrounded))
                start_jd += maha_years_unrounded * year_duration

            elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                # L2: your legacy logic (equal split among bhukthis)
                bhukthis = _children_of(dhasa_lord)
                n = len(bhukthis)
                child_unrounded = maha_years_unrounded / n
                jd_cursor = start_jd
                for blord in bhukthis:
                    start_str = utils.julian_day_to_date_time_string(jd_cursor)
                    dur_ret   = round(child_unrounded, _round_ndigits) if round_duration else child_unrounded
                    rows.append((dhasa_lord, blord, start_str, dur_ret))
                    jd_cursor += child_unrounded * year_duration
                start_jd += maha_years_unrounded * year_duration

            else:
                # L3..L6: recursive equal-split under the immediate parent
                _recurse(
                    level=const.MAHA_DHASA_DEPTH.ANTARA,  # = 2; we’re about to build level 3 and below
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_years=maha_years_unrounded,
                    prefix=(dhasa_lord,)
                )
                start_jd += maha_years_unrounded * year_duration

            # next maha lord in your custom cycle
            dhasa_lord = _next_adhipati(dhasa_lord)

    return rows
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.yogini_test()
    