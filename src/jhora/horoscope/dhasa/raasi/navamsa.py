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
""" Navamsa Dasa """
year_duration = const.sidereal_year
"""
Birth in Sign    Ar    Ta    Ge    Cn    Le    Vi    Li    Sc    Sg    Cp    Aq    Pi
9 Years          Ar    Le    Li    Aq    Ar    Le    Li    Aq    Ar    Le    Li    Aq
                 0     4     6     10    0     4     6     10    0     4     6     10
                 Li    Ar    Sg    Aq    Le    Sg    Li    Ar    Sg    Aq    Le    Sg
                 6     0     8     10    4     8     6     0     8     10    4     8
"""
dhasa_adhipati_list = [0,4,6,10,0,4,6,10,0,4,6,10]
antardhasa_list = [6,0,8,10,4,8,6,0,8,10,4,8]
dhasa_duration = 9

def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=9,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 → 1=Maha only, 2=+Antara [default], 3..6 deeper
    round_duration=True
):
    """
    Navāṁśa Daśā (depth-enabled)

    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)  [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

      • Seed daśā rāśi = dhasa_adhipati_list[Navāṁśa lagna sign].
      • Mahā sequence = 12 signs from seed forward; if seed is even, use the reversed style
      • Antara rule (L2): child seed = `antardhasa_list[maha_rasi]`, then 12 rāśis forward from there.
      • JD advancement uses your `year_duration`.

    Depth ≥ 3:
      • At every node, **equal‑split the immediate parent** into 12 parts (Σchildren = parent),
        and use **the same Antara rule** but applied to the **current parent**:
           child order = 12 signs starting from `antardhasa_list[parent_rasi]`.

    Rounding:
      • Only the returned duration is rounded (to `const.DHASA_DURATION_ROUNDING_TO` if defined, else 2).
      • All JD/time math uses unrounded values (full precision).

    Returns:
      A flat list of tuples shaped per `dhasa_level_index`.
    """
    # ---- Safety guard on depth argument ---------------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- Chart and seed computation (unchanged logic) -------------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    # Navāṁśa lagna sign is at planet_positions[0][1][0]
    navamsa_lagna_sign = planet_positions[0][1][0]

    # Your original seed mapping: seed = dhasa_adhipati_list[lagna_sign]
    dhasa_seed = dhasa_adhipati_list[navamsa_lagna_sign]

    # Mahā sequence: default forward, but flip to your reversed construction if seed is even
    dhasa_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [ (dhasa_seed + 6 - h + 12) % 12 for h in range(12) ]

    # Helper: build 12-child order for ANY parent using antardhasa_list[parent]
    def _children_from(parent_rasi):
        bukthi_seed = antardhasa_list[parent_rasi]
        return [ (bukthi_seed + h) % 12 for h in range(12) ]

    # Rounding precision (configurable; safe fallback=2)
    _round_ndigits = max(0, int(getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)))

    # Recursion for depth ≥ 3: equal split of immediate parent into 12 Antara,
    # order from _children_from(parent)
    def _recurse(level, parent_rasi, parent_start_jd, parent_years, prefix, out_rows):
        child_years = parent_years / 12.0
        jd_cursor   = parent_start_jd
        for child_rasi in _children_from(parent_rasi):
            if level < dhasa_level_index:
                _recurse(level + 1, child_rasi, jd_cursor, child_years, prefix + (child_rasi,), out_rows)
            else:
                # Leaf row at requested depth
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_out   = round(child_years, _round_ndigits) if round_duration else child_years
                out_rows.append(prefix + (child_rasi, start_str, dur_out))
            jd_cursor += child_years * year_duration

    # ---- Emit per requested depth --------------------------------------------
    rows     = []
    start_jd = jd_at_dob

    for maha_rasi in dhasa_lords:
        md_years = float(dhasa_duration)  # your module constant (in years)

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Maha only
            rows.append((
                maha_rasi,
                utils.julian_day_to_date_time_string(start_jd),
                round(md_years, _round_ndigits) if round_duration else md_years
            ))
            start_jd += md_years * year_duration

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antara — equal split of fixed Mahā duration; order from antardhasa_list[maha]
            ad_years = md_years / 12.0
            jd_b     = start_jd
            for antara_rasi in _children_from(maha_rasi):
                rows.append((
                    maha_rasi, antara_rasi,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(ad_years, _round_ndigits) if round_duration else ad_years
                ))
                jd_b += ad_years * year_duration
            # ΣAntara == Mahā → use end of Antara chain as next Mahā start
            start_jd = jd_b

        else:
            # L3..L6: recursive equal-split under the immediate parent
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,  # 2 → build 3..N
                parent_rasi=maha_rasi,
                parent_start_jd=start_jd,
                parent_years=md_years,
                prefix=(maha_rasi,),
                out_rows=rows
            )
            start_jd += md_years * year_duration

    return rows
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.navamsa_dhasa_test()