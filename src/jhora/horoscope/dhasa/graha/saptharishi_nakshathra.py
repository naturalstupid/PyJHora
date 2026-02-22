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
from collections import OrderedDict as Dict
from jhora import const, utils
from jhora.panchanga import drik


_dhasa_duration = 10; _dhasa_count = 10
year_duration = const.sidereal_year
human_life_span_for_dhasa = 100
dhasa_adhipathi_list = lambda lord: {(lord-i)%27:_dhasa_duration for i in range(_dhasa_count)}
def _next_adhipati(lord,dhasa_lords,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = dhasa_lords.index(lord)
    next_lord = dhasa_lords[(current + dirn) % len(dhasa_lords)]
    #print(dirn,lord,next_lord,dhasa_lords)
    return next_lord
def _antardhasa(dhasa_lord,antardhasa_option=1):
    dhasa_lords = [(dhasa_lord-i)%27 for i in range(_dhasa_count)]
    lord = dhasa_lord
    if antardhasa_option in [3,4]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords,dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_lords)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord,dhasa_lords,dirn)
    return _bhukthis
    
def _dhasa_progression(jd,place,divisional_chart_factor=1,chart_method=1,star_position_from_moon=1,
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
    nak = int(planet_long / one_star)
    _dp = [(nak-i)%27 for i in range(_dhasa_count)]
    return _dp

def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True               # NEW: round only returned durations; internal calcs use full precision
):
    """
        returns a list of dasha segments at the selected depth level

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1
        @param chart_method: Default=1
        @param star_position_from_moon: 1=Moon(default), 4=Kshema, 5=Utpanna, 8=Adhana
        @param use_tribhagi_variation: False (default), True => durations scaled to 1/3 with 3 cycles
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna, M/G/T/B/I/P as supported
        @param antardhasa_option: ordering rule passed to _antardhasa(...)
        @param dhasa_level_index: Depth 1..6 (1=Maha only, 2=+Antara, 3=+Pratyantara, 4=+Sookshma, 5=+Prana, 6=+Deha)
        @param round_duration: If True, round only the returned duration values to const.DHASA_DURATION_ROUNDING_TO

        @return:
            if dhasa_level_index == 1:
                [ (l1, start_str, dur_years), ... ]
            else:
                [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
            (tuple grows by one lord per requested level)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # --- original cycles/tribhagi behavior preserved ---
    global human_life_span_for_dhasa
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_dhasa *= _tribhagi_factor  # preserves original behavior

    jd = utils.julian_day_number(dob, tob)

    # Original progression (unchanged)
    dhasa_progression = _dhasa_progression(
        jd, place,
        divisional_chart_factor, chart_method,
        star_position_from_moon,
        dhasa_starting_planet
    )

    # Existing antara ordering reused at every depth
    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option))

    retval = []
    start_jd = jd

    # Nested expansion: equal split of the IMMEDIATE PARENT (∑children = parent)
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        children = _children_of(parent_lord)
        if not children:
            return

        n = len(children)
        if n <= 0:
            return

        child_dur_unrounded = parent_duration_years / n  # equal split (same as your Antara branch)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper
            for blord in children:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            # leaf: round ONLY returned value; keep full precision for time accumulation
            for blord in children:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                durn = round(child_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else child_dur_unrounded
                retval.append(prefix + (blord, start_str, durn))
                jd_cursor += child_dur_unrounded * year_duration

    # Main loop (original order & cycles preserved)
    for _ in range(_dhasa_cycles):
        for dhasa_lord in dhasa_progression:
            # Original maha duration logic preserved: _dhasa_duration is your module's base unit
            maha_dur_unrounded = _dhasa_duration * _tribhagi_factor

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

    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.saptharishi_nakshathra_test()
