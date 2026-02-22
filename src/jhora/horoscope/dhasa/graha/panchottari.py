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
sidereal_year = const.sidereal_year
""" Applicability: Lagna in Cancer dwadasamsa """

#seed_star = 17 # Anusham / Anuradha
seed_lord = 0
dhasa_adhipathi_list = {0:12,3:13,6:14,2:15,5:16,1:17,4:18} #  Total 105 years
#dhasa_adhipathi_dict = {0: [17, 24, 4, 11], 3: [18, 25, 5, 12], 6: [19, 26, 6, 13], 2: [20, 27, 7, 14], 5: [21, 1, 8, 15], 1: [22, 2, 9, 16], 4: [23, 3, 10]}
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def applicability_check(dwadasamsa_planet_positions):
    """ Lagna in Cancer dwadasamsa """
    return dwadasamsa_planet_positions[0][1][0]==3
    
def _next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dirn) % len(dhasa_adhipathi_list))]
    return next_lord
def _get_dhasa_dict(seed_star=17):
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

def _maha_dhasa(nak,seed_star=17):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)
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
def _dhasa_start(jd,place,star_position_from_moon=1,divisional_chart_factor=1,chart_method=1,seed_star=17,
                 dhasa_starting_planet=1):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob=drik.Date(y,m,d); tob=(fh,0,0)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method)[:const._pp_count_upto_ketu]
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
        gl = drik.bhrigu_bindhu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='I':
        gl = drik.indu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='P':
        gl = drik.pranapada_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='T':
        sp = sphuta.tri_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = sp[0]*30+sp[1]
    else:
        planet_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    if dhasa_starting_planet==1:
        planet_long += (star_position_from_moon-1)*one_star
    nak = int(planet_long / one_star); rem = (planet_long - nak * one_star)
    lord,res = _maha_dhasa(nak+1,seed_star)          # ruler of current nakshatra
    period = res
    period_elapsed = rem / one_star * period # years
    period_elapsed *= sidereal_year        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date,res]

def get_dhasa_bhukthi(
    dob, tob, place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=17,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    round_duration=True                 # NEW: round only returned durations; internals use full precision
):
    """
        provides karana chathuraaseethi sama dhasa bhukthi for a given date in julian day (includes birth time)

        @return:
          if dhasa_level_index == 1:
              [ (l1, start_str, dur_years), ... ]
          else:
              [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
          (tuple grows by one lord per requested level)
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
    # Keep the original start helper & inputs as-is
    dhasa_lord, start_jd, _ = _dhasa_start(
        jd, place,
        star_position_from_moon=star_position_from_moon,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet
    )

    retval = []

    # Use your existing antara ordering at every level
    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option))

    # Nested partition of the immediate parent; internal calcs use full precision
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return

        n = len(bhukthis)
        child_dur_unrounded = parent_duration_years / n  # equal split (your Antara logic)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper: each child becomes the parent for next level
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * sidereal_year
        else:
            # leaf rows: round only the returned duration if requested
            for blord in bhukthis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                durn = round(child_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else child_dur_unrounded
                retval.append(prefix + (blord, start_str, durn))
                jd_cursor += child_dur_unrounded * sidereal_year

    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            # Maha duration — full precision internally; round only when returning
            maha_dur_unrounded = dhasa_adhipathi_list[dhasa_lord] * _tribhagi_factor

            if dhasa_level_index == 1:
                start_str = utils.julian_day_to_date_time_string(start_jd)
                durn = round(maha_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur_unrounded
                retval.append((dhasa_lord, start_str, durn))
                start_jd += maha_dur_unrounded * sidereal_year
            else:
                _recurse(
                    level=2,
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_duration_years=maha_dur_unrounded,
                    prefix=(dhasa_lord,)
                )
                start_jd += maha_dur_unrounded * sidereal_year

            dhasa_lord = _next_adhipati(dhasa_lord)  # dirn=1 for dhasa sequence

    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.panchottari_test()
    