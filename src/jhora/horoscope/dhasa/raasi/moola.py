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
from jhora.horoscope.chart import house, charts
from jhora.horoscope.dhasa.raasi import narayana
""" Also called Lagna Kendradi Rasi Dhasa """

def moola_dhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6  (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True
):
    """
    Lagna Kendraadhi Daśā (a.k.a. Moola Daśā) — depth-enabled (Maha → Antara → …)

    Depth (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)  [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

      • Seed = stronger of Asc vs 7th (house.stronger_rasi_from_planet_positions).
      • Direction: Saturn in seed ⇒ forward; Ketu in seed ⇒ backward; else odd fwd / even back.
      • Progression: first three kendras (house.kendras()[:3]) from the seed, mapped with direction.
      • Maha duration: narayana._dhasa_duration(planet_positions, sign)  [in years].
      • Two cycles: cycle‑2 duration = 12 − first; skip if ≤ 0.
      • Lifespan stop: break when cumulated years ≥ const.human_life_span_for_narayana_dhasa.
      • Antar order: your `_antardhasa(sign, p_to_h)` at every level.

    Rounding:
      • Only the returned duration is rounded (to const.DHASA_DURATION_ROUNDING_TO if present; else 2).
      • JD/time accumulation uses unrounded durations.
    """
    # ---- Safety guard on depth argument ---------------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- Build the base chart at the annualized epoch (your original call) ----
    start_jd = utils.julian_day_number(dob, tob)
    pp = charts.divisional_chart(
        start_jd, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    # ---- Seed (stronger of Asc & 7th) and direction ---------------------------
    p_to_h      = utils.get_planet_house_dictionary_from_planet_positions(pp)
    asc_house   = p_to_h[const._ascendant_symbol]
    seventh     = (asc_house + 7 - 1) % 12
    seed_sign   = house.stronger_rasi_from_planet_positions(pp, asc_house, seventh)

    # Direction rules: Saturn in seed → fwd; Ketu in seed → back; else odd→fwd, even→back
    if p_to_h.get(const.SATURN_ID, -1) == seed_sign:
        direction = 1
    elif p_to_h.get(const.KETU_ID, -1) == seed_sign:
        direction = -1
    elif seed_sign in const.odd_signs:
        direction = 1
    else:
        direction = -1

    # Kendra list and progression from the seed (your original)
    ks = sum(house.kendras()[:3], [])  # first three kendras
    dhasa_progression = [ (seed_sign + direction * (k - 1)) % 12 for k in ks ]  # 12-sign IDs

    # ---- Helpers ---------------------------------------------------------------
    # Mahā duration (years) via Narayana helper
    def _maha_duration(rasi):
        return float(narayana._dhasa_duration(pp, rasi))

    # Antara order for any parent sign: uses your _antardhasa(sign, p_to_h)
    def _antara_order(parent_sign):
        return _antardhasa(parent_sign, p_to_h)

    # Rounding precision (configurable from const; safe default=2)
    _round_ndigits = max(0, int(getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)))

    # Recursive expansion for depth ≥ 3: equal-split the immediate parent into 12 parts
    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows, totals):
        """
        L3+ recursion:
          • child_years = parent_years / 12.0
          • child order = _antara_order(parent_sign)
          • Σ children = parent
          • Lifespan check after each innermost append (to mirror your second-cycle stop)
        """
        child_years = parent_years / 12.0
        jd_cursor   = parent_start_jd
        for child_sign in _antara_order(parent_sign):
            if level < dhasa_level_index:
                _recurse(level + 1, child_sign, jd_cursor, child_years, prefix + (child_sign,), out_rows, totals)
            else:
                # Leaf row at requested depth
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_out   = round(child_years, _round_ndigits) if round_duration else child_years
                out_rows.append(prefix + (child_sign, start_str, dur_out))
                # lifespan accumulation in YEARS (same units as _maha_duration)
                totals['years'] += child_years
                if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                    totals['stop'] = True
                    return
            jd_cursor += child_years * const.sidereal_year
            if totals.get('stop'):
                return

    # ---- Emit rows per requested depth (two cycles) ---------------------------
    rows        = []
    jd_cursor   = start_jd
    totals      = {'years': 0.0, 'stop': False}  # accumulate durations in YEARS

    # Cycle #1
    for md_sign in dhasa_progression:
        if totals['stop']:
            break
        md_years = _maha_duration(md_sign)

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Mahā only
            rows.append((
                md_sign,
                utils.julian_day_to_date_time_string(jd_cursor),
                round(md_years, _round_ndigits) if round_duration else md_years
            ))
            totals['years'] += md_years
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break
            jd_cursor += md_years * const.sidereal_year

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antara — equal split into 12, order from _antardhasa(seed, p_to_h)
            ad_years = md_years / 12.0
            jd_b     = jd_cursor
            for ad_sign in _antara_order(md_sign):
                rows.append((
                    md_sign, ad_sign,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(ad_years, _round_ndigits) if round_duration else ad_years
                ))
                totals['years'] += ad_years
                if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                    jd_cursor = jd_b + ad_years * const.sidereal_year
                    break
                jd_b += ad_years * const.sidereal_year
            # Use end of Antara chain as next Mahā start (Σ Antara == Mahā)
            jd_cursor = jd_b
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break

        else:
            # L3..L6: recursive equal-split under the immediate parent
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,  # 2 → build 3..N
                parent_sign=md_sign,
                parent_start_jd=jd_cursor,
                parent_years=md_years,
                prefix=(md_sign,),
                out_rows=rows,
                totals=totals
            )
            if totals['stop']:
                break
            jd_cursor += md_years * const.sidereal_year

    if totals['years'] >= const.human_life_span_for_narayana_dhasa:
        return rows

    # Cycle #2: duration = 12 − first; skip if ≤ 0
    for _, md_sign in enumerate(dhasa_progression):
        if totals['stop']:
            break
        first_md = _maha_duration(md_sign)
        md2_years = 12.0 - first_md
        if md2_years <= 0:
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                md_sign,
                utils.julian_day_to_date_time_string(jd_cursor),
                round(md2_years, _round_ndigits) if round_duration else md2_years
            ))
            totals['years'] += md2_years
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break
            jd_cursor += md2_years * const.sidereal_year

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ad_years = md2_years / 12.0
            jd_b     = jd_cursor
            for ad_sign in _antara_order(md_sign):
                rows.append((
                    md_sign, ad_sign,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(ad_years, _round_ndigits) if round_duration else ad_years
                ))
                totals['years'] += ad_years
                if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                    jd_cursor = jd_b + ad_years * const.sidereal_year
                    break
                jd_b += ad_years * const.sidereal_year
            jd_cursor = jd_b
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break

        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=md_sign,
                parent_start_jd=jd_cursor,
                parent_years=md2_years,
                prefix=(md_sign,),
                out_rows=rows,
                totals=totals
            )
            if totals['stop']:
                break
            jd_cursor += md2_years * const.sidereal_year

    return rows

def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[const.SATURN_ID]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[const.KETU_ID]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.moola_dhasa_test()