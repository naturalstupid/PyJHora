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
""" This is also called Shashti Sama Dasa """
""" Applicability: Sun in lagna """

#seed_star = 1 # Ashvini
mahadasa_seed_star = 1
dhasa_adhipathi_star_count = {4:3,0:4,2:3,1:4,3:3,5:4,6:3,7:4}
dhasa_adhipathi_list = {4:10,0:10,2:10,1:6,3:6,5:6,6:6,7:6} #  Total 60 years
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def applicability_check(planet_positions):
    """ Sun in lagna """
    return planet_positions[0][1][0]==planet_positions[1][1][0]
def _next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dirn) % len(dhasa_adhipathi_list))]
    return next_lord
""" get_dhasa_dict - start with Ashwini nakshatra, and take them in groups of 3 & 4, alternately.  """
def _get_dhasa_dict(seed_star=mahadasa_seed_star):
    dhasa_dict = {k:[] for k in dhasa_adhipathi_star_count.keys()}
    nak = seed_star
    for lord,nak_count in dhasa_adhipathi_star_count.items():
        for _ in range(nak_count):
            dhasa_dict[lord].append(nak)
            nak = (nak+1)%28
    return dhasa_dict
#dhasa_adhipathi_dict = _get_dhasa_dict()

def _maha_dhasa(nak,seed_star=mahadasa_seed_star):
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
def _dhasa_start(jd,place,star_position_from_moon=1,divisional_chart_factor=1,chart_method=1,
                 seed_star=mahadasa_seed_star,dhasa_starting_planet=1):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob=drik.Date(y,m,d); tob=(fh,0,0)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method)
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
    #print('period_elapsed',period_elapsed,rem/one_star)
    period_elapsed *= year_duration        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date,res]

def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    seed_star=mahadasa_seed_star,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_cycles = 2
):
    """
        returns a list of dasha segments at the selected depth level

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place(name, lat, lon, tz)
        @param divisional_chart_factor: Default=1 (1=Rasi, 9=Navamsa, ...)
        @param chart_method: Default=1
        @param star_position_from_moon: 1=Moon (default), 4=Kshema, 5=Utpanna, 8=Adhana
        @param use_tribhagi_variation: False (default); True => durations scaled to 1/3 with 3 cycles
        @param seed_star: 1..27 (default=1)
        @param dhasa_starting_planet: 0..8 or 'L', 'M','G','T','B','I','P'
        @param antardhasa_option: ordering rule for _antardhasa(...)
        @param dhasa_level_index: Depth 1..6 (1=Maha only, 2=+Antara, 3=+Pratyantara, 4=+Sookshma, 5=+Prana, 6=+Deha)
        @param round_duration: If True, round only the returned durations to const.DHASA_DURATION_ROUNDING_TO

        @return:
          if dhasa_level_index == 1:
              [ (l1, start_str, dur_years), ... ]
          else:
              [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
          (tuple grows by one lord per requested level)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    _tribhagi_factor = 1.
    _dhasa_cycles = dhasa_cycles
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)

    jd = utils.julian_day_number(dob, tob)
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

    # Nested expansion: equal split of IMMEDIATE PARENT (∑children = parent)
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return
        n = len(bhukthis)
        child_dur_unrounded = parent_duration_years / n  # equal split (matches your Antara rule)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            # leaf rows: round only the returned duration; internal math stays full precision
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

            dhasa_lord = _next_adhipati(dhasa_lord)  # maintain your sequence

    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.shastihayani_test()
    