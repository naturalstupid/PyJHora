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
from jhora.horoscope.chart import charts
from jhora.horoscope.dhasa.raasi import narayana
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,
                         dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA, round_duration=True):
    """
    Lagnamsaka Daśā (depth-enabled; equal-split at each deeper level)

    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> (l1,               start_str, dur_units)
      2 = ANTARA               -> (l1, l2,           start_str, dur_units)    [DEFAULT]
      3 = PRATYANTARA          -> (l1, l2, l3,       start_str, dur_units)
      4 = SOOKSHMA             -> (l1, l2, l3, l4,   start_str, dur_units)
      5 = PRANA                -> (l1, l2, l3, l4, l5,   start_str, dur_units)
      6 = DEHA                 -> (l1, l2, l3, l4, l5, l6, start_str, dur_units)

    Units:
      • `_dhasa_duration(...)` returns daśā length in “years”.
      • We advance JD with `dhasa_factor`, where:
           dhasa_factor = year_duration
           if varsha_narayana: dhasa_factor /= 360
        (kept exactly as in your original function)
      • Returned `dur_units` are in the same “years” units you use today.

    Notes:
      • Mahā progression chosen by const.narayana_dhasa_*_progression with Ketu/Saturn exceptions.
      • Antar order at all depths comes from `_narayana_antardhasa(planet_positions, parent_rasi)`.
      • Deeper levels (>= L3) split the *immediate* parent evenly into 12 parts; Σ(children)=parent.
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    navamsa_planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=9)
    dhasa_seed_sign = navamsa_planet_positions[0][1][0]
    planet_positions = charts.divisional_chart(jd_at_dob, place,
                                        divisional_chart_factor=divisional_chart_factor)[:const._pp_count_upto_ketu]
    return narayana._narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,
                                                sixty_hours=sixty_hours,dhasa_level_index=dhasa_level_index,
                                                varsha_narayana=False,round_duration=round_duration)
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.lagnamsaka_dhasa_test()
    