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
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year
_KARAKA_LIST = ['Ak','AmK','BK','Mk','PiK','PuK','GK','DK']

def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1, chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,show_karaka_as_pair=2 #None=>Dont Show as pair, 1=>Show only karaka index 1,2,3 for NLS Support, 
):
    """
        provides karaka dhasa bhukthi for a given date in julian day (includes birth time)
        @param: show_karaka_as_pair
            None=>Dont Show as pair - return format: (dhasa_lord(s),start_str,duration)
            1=>Show karaka index 1,2,3 for NLS Support - return format: ((karaka_index,dhasa_lord),start_str,duration)
            2=>Show karaka Name Ak,Amk etc  - return format: ((karaka_name,dhasa_lord),start_str,duration)
        @return:
          if dhasa_level_index==1:
            [ (dhasa_lord, start_str, duration_years), ... ]
          else:
            [ (l1, l2, [...], start_str, dd_at_leaf), ... ]
          (leaf still returns `dd` exactly like your original antara output)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    karakas = house.chara_karakas(planet_positions)
    karaka_name_by_planet = {pl: _KARAKA_LIST[i] for i, pl in enumerate(karakas)}
    karaka_index_by_planet = {pl: i for i, pl in enumerate(karakas)}
    _karaka_pair = lambda lord, show_karaka_as_pair: (lord if show_karaka_as_pair is None else
                    (karaka_name_by_planet[lord],lord) if show_karaka_as_pair==2 else
                    (karaka_index_by_planet[lord],lord) )
    asc_house = planet_positions[0][1][0]

    def _dd(pl):
        # distance (in signs) from Lagna to the planet’s sign (0..11)
        return (planet_positions[pl+1][1][0] - asc_house + 12) % 12

    human_life_span = sum(_dd(k) for k in karakas)

    def _bhukthis_for(parent_lord):
        ki = karakas.index(parent_lord)
        kl = len(karakas)
        return karakas[ki+1:kl] + karakas[0:ki+1]

    dhasa_info = []
    start_jd = jd_at_dob

    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        """
        Nested partition at each level using the same antara rule:
        child_years = parent_years * dd(child) / human_life_span
        """
        bhukthis = _bhukthis_for(parent_lord)
        if not bhukthis:
            return

        jd_cursor = parent_start_jd
        for blord in bhukthis:
            dd_child = _dd(blord)
            blord_pair = _karaka_pair(blord,show_karaka_as_pair)
            child_years_unrounded = parent_duration_years * (dd_child / float(human_life_span))

            if level < dhasa_level_index:
                _recurse(level + 1, blord, jd_cursor, child_years_unrounded, prefix + (blord_pair,))
            else:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_out = (round(child_years_unrounded, const.DHASA_DURATION_ROUNDING_TO)
                           if round_duration else child_years_unrounded)
                dhasa_info.append(prefix + (blord_pair, start_str, dur_out))

            jd_cursor += child_years_unrounded * year_duration  # year_duration == const.sidereal_year

    # Top-level traversal (Maha)
    for k in karakas:
        lord_pair = _karaka_pair(k,show_karaka_as_pair)
        maha_years_unrounded = _dd(k)  # same as your original 'duration = (k_h - asc + 12) % 12'
        if dhasa_level_index == 1:
            start_str = utils.julian_day_to_date_time_string(start_jd)
            durn = round(maha_years_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_years_unrounded
            dhasa_info.append((lord_pair, start_str, durn))
            start_jd += maha_years_unrounded * year_duration
        else:
            _recurse(level=2, parent_lord=k, parent_start_jd=start_jd, parent_duration_years=maha_years_unrounded, prefix=(lord_pair,))
            start_jd += maha_years_unrounded * year_duration

    return dhasa_info
        

if __name__ == "__main__":
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5)
    gd = get_dhasa_antardhasa(dob, tob, place,dhasa_level_index=2,round_duration=False,
                              show_karaka_as_pair=1)
    print(gd); exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.karaka_dhasa_test()
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    for dli in range(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, const.MAHA_DHASA_DEPTH.DEHA+1):
        gd = get_dhasa_antardhasa(dob, tob, place,dhasa_level_index=dli,round_duration=False)
        gd_sum = [sum([row[-1] for row in gd])]
        if dli == 1:
            expected_list = gd_sum
            continue
        else:
            pvr_tests.compare_lists_within_tolerance("karaka_dhasa Level Duration Test ", 
                                       expected_list, gd_sum, pvr_tests._tolerance,"Level",dli)    
