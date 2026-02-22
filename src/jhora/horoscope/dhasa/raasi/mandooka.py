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
from jhora.horoscope.chart import charts, house
""" method = 2 KN Rao Method - Working. Method 1=> Sanjay Rath - yet to be implemented """
year_duration = const.sidereal_year
dhasa_order = {0:([0,3,6,9, 2,5,8,11, 1,4,7,10],[0,9,6,3, 2,11,8,5, 1,10,7,4]),
               3:([3,6,9,0, 2,5,8,11, 1,4,7,10],[3,0,9,6, 2,11,8,5, 1,10,7,4]),
               6:([6,9,0,3, 2,5,8,11, 1,4,7,10],[6,3,0,9, 2,11,8,5, 1,10,7,4]),
               9:([9,0,3,6, 2,5,8,11, 1,4,7,10],[9,6,3,0, 2,11,8,5, 1,10,7,4]),
               2:([2,5,8,11, 1,4,7,10, 0,3,6,9],[2,11,8,5, 1,10,7,4,0,9,6,3]),
               5:([5,8,11,2, 1,4,7,10,0,3,6,9],  [5,2,11,8, 1,10,7,4,0,9,6,3]),
               8:([8,11,2,5, 1,4,7,10,0,3,6,9 ],[8,5,2,11, 1,10,7,4,0,9,6,3]),
               11:([11,2,5,8, 1,4,7,10, 0,3,6,9],[11,8,5,2, 1,10,7,4,0,9,6,3]),
               1:([1,4,7,10, 0,3,6,9, 2,5,8,11],[1,10,7,4, 0,9,6,3, 2,11,8,5]),
               4:([4,7,10,1, 0,3,6,9, 2,5,8,11],[4,1,10,7, 0,9,6,3, 2,11,8,5]),
               7:([7,10,1,4, 0,3,6,9, 2,5,8,11],[7,4,1,10, 0,9,6,3, 2,11,8,5]),
               10:([10,1,4,7, 0,3,6,9, 2,5,8,11],[10,7,4,1, 0,9,6,3, 2,11,8,5])
               }
               
def _dhasa_duration_kn_rao(planet_positions,sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        dhasa_period = (sign-house_of_lord+1)%12
            #print('house_of_lord',house_of_lord,'> sign',sign,'dhasa_period',dhasa_period)
    else:
        dhasa_period = (house_of_lord-sign+1)%12
    if dhasa_period <=0 or const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._OWNER_RULER:# or \
            #house_of_lord==(sign+11)%12:
        dhasa_period = 12
    if house_of_lord==(sign+6)%12:
        dhasa_period = 10
    return dhasa_period
def _dhasa_duration(lord):
    if lord in const.movable_signs:
        return 7
    elif lord in const.fixed_signs:
        return 8
    else:
        return 9

def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True
):
    """
    Mandooka Daśā (depth-enabled)

    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)    [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

    Preserved from your original:
      • method = 2 (K.N. Rao) by default. (method = 1 = Sanjay Rath – TODO)
      • Seed: stronger of Asc & 7th (KNRao), or SRath mapping when method==1.
      • Direction: by your `dhasa_order[dhasa_seed][dirn]` where dirn = 1 if seed is even, else 0.
      • Mahā duration: _dhasa_duration_kn_rao(planet_positions, rasi) [or _dhasa_duration(rasi) if method==1].
      • Antar order: rotation of `dhasa_lords` starting at the *current Mahā’s index* (global order).
      • JD advancement uses `sidereal_year` (module alias), unchanged.

    Durations & rounding:
      • Returned durations are rounded to const.DHASA_DURATION_ROUNDING_TO (fallback = 2) when `round_duration=True`.
      • JD/time accumulation always uses the unrounded value.

    """
    # ── Safety guard for depth argument ────────────────────────────────────────
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ── Method selection (K.N. Rao by default) ────────────────────────────────
    method = 2  # 2 = K.N. Rao (working); 1 = Sanjay Rath (TODO in your code)

    # ── Build the annual chart epoch (your original call kept these params) ───
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    # ── Seed determination ─────────────────────────────────────────────────────
    asc_house     = planet_positions[0][1][0]
    seventh_house = (asc_house + 6) % 12    # (Asc + 7 − 1) % 12  == (Asc+6)%12

    if method == 1 and asc_house in const.even_signs:
        # Sanjay Rath mapping (your TODO branch left intact)
        dhasa_seed = const.SAGITTARIUS
        if asc_house in const.fixed_signs:
            dhasa_seed = const.LIBRA
        elif asc_house in const.dual_signs:
            dhasa_seed = const.SCORPIO
    else:
        # K.N. Rao: stronger of Asc & 7th
        dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)

    # ── Direction & full 12‑sign global order for this seed ───────────────────
    # dirn picks which of the 2 sequences under this seed to use from your `dhasa_order`
    dirn = 1 if dhasa_seed in const.even_signs else 0
    dhasa_lords = dhasa_order[dhasa_seed][dirn]  # length 12

    # Helper: “Antara order” for any parent is the rotation of dhasa_lords starting at the parent's index
    def _bhukthis_from(parent_rasi):
        idx = dhasa_lords.index(parent_rasi)
        return [dhasa_lords[(idx + h) % 12] for h in range(12)]

    # Helper: chosen Mahā duration function (KNRao / SRath)
    def _maha_duration(rasi):
        if method == 1:
            return float(_dhasa_duration(rasi))  # your SRath stub
        return float(_dhasa_duration_kn_rao(planet_positions, rasi))  # KNRao

    # Rounding precision
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    # ── Recursive builder for L3+ (equal split into 12 using the same global rotation rule) ──
    def _recurse(level, parent_rasi, parent_start_jd, parent_years, prefix, out_rows):
        """
        Depth >= 3:
          • child_years = parent_years / 12.0  (Σ children = parent)
          • child order = rotation of dhasa_lords, starting at parent_rasi’s index
        """
        child_years = parent_years / 12.0
        jd_cursor   = parent_start_jd
        for child_rasi in _bhukthis_from(parent_rasi):
            if level < dhasa_level_index:
                _recurse(level + 1, child_rasi, jd_cursor, child_years, prefix + (child_rasi,), out_rows)
            else:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret   = round(child_years, _round_ndigits) if round_duration else child_years
                out_rows.append(prefix + (child_rasi, start_str, dur_ret))
            jd_cursor += child_years * year_duration

    # ── Main build loop over the 12‑sign global order ─────────────────────────
    rows    = []
    start_jd = jd_at_dob

    for dhasa_lord in dhasa_lords:
        md_years = _maha_duration(dhasa_lord)  # Mahā duration in years

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Maha only
            rows.append((
                dhasa_lord,
                utils.julian_day_to_date_time_string(start_jd),
                round(md_years, _round_ndigits) if round_duration else md_years
            ))
            start_jd += md_years * year_duration

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antara — equal split into 12, using the rotation from the current Mahā index
            ad_years = md_years / 12.0
            jd_b     = start_jd
            for bhukthi_lord in _bhukthis_from(dhasa_lord):
                rows.append((
                    dhasa_lord, bhukthi_lord,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(ad_years, _round_ndigits) if round_duration else ad_years
                ))
                jd_b += ad_years * year_duration
            # Use end of Antara as next Mahā start (Σ 12 Antara == Mahā)
            start_jd = jd_b

        else:
            # L3..L6: recursive equal split under the immediate parent
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,  # 2 → build 3..N
                parent_rasi=dhasa_lord,
                parent_start_jd=start_jd,
                parent_years=md_years,
                prefix=(dhasa_lord,),
                out_rows=rows
            )
            start_jd += md_years * year_duration

    return rows
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.mandooka_dhasa_test()