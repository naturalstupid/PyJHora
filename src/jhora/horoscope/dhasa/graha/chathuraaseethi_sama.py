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
""" Applicability: The 10th lord in 10th """

#seed_star = 15 # Swaathi
seed_lord = 0
dhasa_adhipathi_list = {k:12 for k in const.SUN_TO_SATURN} # duration 12 years Total 84 years
#dhasa_adhipathi_dict = {0: [15, 22, 2, 9], 1: [16, 23, 3, 10], 2: [17, 24, 4, 11], 3: [18, 25, 5, 12], 4: [19, 26, 6, 13], 5: [20, 27, 7, 14], 6: [21, 1, 8]}
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def applicability_check(planet_positions):
    """ 10th Lord in 10th House """
    from jhora.horoscope.chart import house
    asc_house = planet_positions[0][1][0]
    #print('asc_house',asc_house)
    tenth_house = (asc_house+9)%12; tenth_lord = house.house_owner_from_planet_positions(planet_positions, tenth_house)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    #print('tenth_house',tenth_house,'tenth_lord',tenth_lord,p_to_h[tenth_lord])
    return p_to_h[tenth_lord]==tenth_house
def _next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dirn) % len(dhasa_adhipathi_list))]
    return next_lord
def _get_dhasa_dict(seed_star=15):
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

def _maha_dhasa(nak,seed_star=15):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)
    return [(_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord]) for _dhasa_lord,_star_list in dhasa_adhipathi_dict.items() if nak in _star_list][0]
def _antardhasa(lord,antardhasa_option=1):
    if antardhasa_option in [3,4]:
        lord = _next_adhipati(lord, dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = _next_adhipati(lord, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord,dirn)
    return _bhukthis
def _dhasa_start(jd,place,divisional_chart_factor=1,chart_method=1,star_position_from_moon=1,
                 seed_star=15,dhasa_starting_planet=1):
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
    period_elapsed *= sidereal_year        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date,res]

def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    chart_method=1,
    # include_antardhasa=True,     # REMOVED
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    seed_star=15,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration = True
):
    """
        returns a list of dasha at selected depth (L1..L6)

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param dhasa_level_index: Depth (1..6) — 1=Maha only (no Antara),
                                  2=+Antara (Bhukthi), 3=+Pratyantara, 4=+Sookshma, 5=+Prana, 6=+Deha
        @param star_position_from_moon:
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases
        @param seed_star 1..27. Default = 15
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada

        @return:
            if dhasa_level_index == 1:
                [ (l1, start_str, dur_years), ... ]
            else:
                [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
            (leaf tuple includes duration; structure grows by one lord per requested level)
    """
    # --- keep original variables/logic intact ---
    _tribhagi_factor = 1.
    _dhasa_cycles = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.; _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)

    # Validate depth
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd = utils.julian_day_number(dob, tob)
    dhasa_lord, start_jd, _ = _dhasa_start(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet
    )

    retval = []

    # Helper: children sequence at any level — order/direction from your existing antara logic
    def _children_of(parent_lord):
        """
        Returns the list of child lords under 'parent_lord' using the SAME order rule as your current Antara:
        _antardhasa(parent_lord, antardhasa_option)
        """
        return list(_antardhasa(parent_lord, antardhasa_option))

    # Recursive expander: equal split of IMMEDIATE PARENT (so sum(children)=parent)
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        """
        level: current level to build (>=2). prefix already contains lords up to previous level.
        """
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return
        child_dur = parent_duration_years / len(bhukthis)  # equal split (same as your Antara logic)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper: each child becomes the parent for next level
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_dur, prefix + (blord,))
                jd_cursor += child_dur * sidereal_year
        else:
            # leaf rows: emit tuples with (lords..., start_str, leaf_dur)
            for blord in bhukthis:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                retval.append(prefix + (blord, start_str, child_dur))
                jd_cursor += child_dur * sidereal_year

    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            # Maha duration (keep your rounding behavior at Maha)
            maha_dur = dhasa_adhipathi_list[dhasa_lord] * _tribhagi_factor
            durn = round(maha_dur,const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur
            if dhasa_level_index == 1:
                # Maha only (unchanged, just use centralized formatter)
                start_str = utils.julian_day_to_date_time_string(start_jd)
                retval.append((dhasa_lord, start_str, durn))
                start_jd += maha_dur * sidereal_year
            else:
                # Depth >= 2: expand down using the same antara ordering rule at EACH level (equal split)
                _recurse(level=2, parent_lord=dhasa_lord, parent_start_jd=start_jd,
                         parent_duration_years=maha_dur, prefix=(dhasa_lord,))
                # advance master clock by Maha
                start_jd += maha_dur * sidereal_year

            dhasa_lord = _next_adhipati(dhasa_lord)

    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chathuraseethi_sama_tests()
