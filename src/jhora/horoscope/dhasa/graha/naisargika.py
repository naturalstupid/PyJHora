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
_bhukthi_house_list = [0,3,6,9,1,4,7,10,2,5,8,11]
_bhukthi_exempt_list_1 = [2,9]
_bhukthi_exempt_list_2 = [1,5,10,11] 
dhasa_adhipathi_dict = {1:1,2:2,3:9,5:20,4:18,0:20,6:50,'L':12} 

def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1, chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    mahadhasa_lord_has_no_antardhasa=True,
    antardhasa_option1=False, antardhasa_option2=False,
    round_duration=True                          # NEW: round only returned duration; internals use full precision
):
    """
        provides Naisargika dhasa bhukthi for a given date in julian day (includes birth time)
        @param antardhasa_option1 = True 3rd/10th house has no antardhasa
        @param antardhasa_option2 = True 2/6/11/12 house has no antardhasa
        @return:
          if dhasa_level_index == 1:
            [ (dhasa_lord, start_str, duration_years), ... ]
          else:
            [ (l1, l2, ..., start_str, leaf_duration_years), ... ]  # equal-split of immediate parent
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # Build base chart once
    start_jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        start_jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_saturn]  # Ignore Rahu onwards (as you did)

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    dhasa_lords = list(dhasa_adhipathi_dict.keys())  # preserve existing order

    # --- Build bhukthi house list (with requested exclusions) ---
    bhukthi_house_list = _bhukthi_house_list
    if antardhasa_option1:
        bhukthi_house_list = [p for p in bhukthi_house_list if p not in _bhukthi_exempt_list_1]
    if antardhasa_option2:
        bhukthi_house_list = [p for p in bhukthi_house_list if p not in _bhukthi_exempt_list_2]

    def _bhukthis_for(parent_lord):
        """
        SAME antara selection as your original code, applied to `parent_lord`.
        - Houses are picked relative to `parent_lord`'s sign
        - Flattens h_to_p lists, removes 'L','7','8'
        - Optionally removes parent lord itself (if flag is set and not Lagna)
        Returns: list[int] of child lords in order
        """
        lord_house = planet_positions[parent_lord+1][1][0] if parent_lord != const._ascendant_symbol \
                     else planet_positions[0][1][0]
        # Collect planet labels from targeted houses
        raw_lists = [h_to_p[(h + lord_house) % 12] for h in bhukthi_house_list]
        raw_lists = [s for s in raw_lists if s != '']
        bhukthis = utils.flatten_list([s.split('/') for s in raw_lists])

        # Remove these labels if present (mirror original)
        for p in ['L', '7', '8']:
            if p in bhukthis:
                bhukthis.remove(p)

        # “Maha lord has no antara” option
        if mahadhasa_lord_has_no_antardhasa and parent_lord != const._ascendant_symbol:
            if str(parent_lord) in bhukthis:
                bhukthis.remove(str(parent_lord))

        return list(map(int, bhukthis))

    retval = []

    # --- Recursive expansion: equal split of the immediate parent at every level ---
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        children = _bhukthis_for(parent_lord)
        if not children:
            return

        n = len(children)
        child_dur_unrounded = parent_duration_years / n  # equal split (as in your Antara today)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # Go deeper (each child becomes parent for next level)
            for blord in children:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * const.sidereal_year
        else:
            # Leaf rows: round ONLY the returned duration; advance with full precision
            for blord in children:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                durn = round(child_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else child_dur_unrounded
                retval.append(prefix + (blord, start_str, durn))
                jd_cursor += child_dur_unrounded * const.sidereal_year

    # --- Top-level (Maha) progression using your dhasa_adhipathi_dict ---
    for dhasa_lord in dhasa_lords:
        maha_dur_unrounded = dhasa_adhipathi_dict[dhasa_lord]  # full precision internally

        if dhasa_level_index == 1:
            start_str = utils.julian_day_to_date_time_string(start_jd)
            durn = round(maha_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur_unrounded
            retval.append((dhasa_lord, start_str, durn))
            start_jd += maha_dur_unrounded * const.sidereal_year
        else:
            _recurse(
                level=2,
                parent_lord=dhasa_lord,
                parent_start_jd=start_jd,
                parent_duration_years=maha_dur_unrounded,
                prefix=(dhasa_lord,)
            )
            start_jd += maha_dur_unrounded * const.sidereal_year

    return retval

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.naisargika_test()