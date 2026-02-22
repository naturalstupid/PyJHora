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
""" Computes Drig Dhasa from the chart """
from jhora import const, utils
from jhora.horoscope.chart import house, charts
from jhora.horoscope.dhasa.raasi import narayana
_round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
# -*- coding: utf-8 -*-
"""
Drig Dhasa (sign-aspect based) with multi-level expansion (L1..L6).

Signature:
    get_dhasa_antardhasa(jd, place, divisional_chart_factor=1, dhasa_level_index=2)

Returns:
  Depending on dhasa_level_index:
    1 (MAHA_DHASA_ONLY): rows = (l1,                             start_str, dur_years)
    2 (ANTARA)          : rows = (l1, l2,                        start_str, dur_years)   [DEFAULT]
    3 (PRATYANTARA)     : rows = (l1, l2, l3,                    start_str, dur_years)
    4 (SOOKSHMA)        : rows = (l1, l2, l3, l4,                start_str, dur_years)
    5 (PRANA)           : rows = (l1, l2, l3, l4, l5,            start_str, dur_years)
    6 (DEHA)            : rows = (l1, l2, l3, l4, l5, l6,        start_str, dur_years)

Notes:
  - All labels l1..l6 are integers (0..11), i.e., rasi indices (Aries=0 ... Pisces=11).
  - MD order: 9th → its 3 aspected (ordered) → 10th → its 3 → 11th → its 3 (total 12).
  - Durations: movable=7y, fixed=8y, dual=9y.
  - Antara & deeper:
      * Seed = stronger of parent sign vs its 7th (house.stronger_rasi_from_planet_positions).
      * Direction: zodiacal if parent sign is odd (1-based), else anti-zodiacal.
      * Progression:
          Movable → regular step by ±1.
          Fixed   → alternate seed and its 6th.
          Dual    → kantakas from 1st, then 5th, then 9th; within each quartet apply direction.
  - Deeper levels split equally (1/12 each); Σ(children)=parent. No lifespan cap.
  - Dates via utils.julian_day_to_date_time_string(jd).
"""

from typing import List, Tuple

# Prefer const.sidereal_year if present; else fallback.
_DAYS_IN_YEAR = getattr(const, "sidereal_year", 365.256363004)

# Modality sets (lists of rasis 0..11) from const
_MOVABLE = set(getattr(const, "movables_signs", [0, 3, 6, 9]))
_FIXED   = set(getattr(const, "fixed_signs",    [1, 4, 7, 10]))
_DUAL    = set(getattr(const, "dual_signs",     [2, 5, 8, 11]))

def drig_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                       round_duration=True):
    """
    Drig Daśā (two-cycle) with depth control.

    Depth (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)       [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

    Returned tuple shapes follow the depth setting (see above).
    """
    jd = utils.julian_day_number(dob,tob)
    planet_positions = charts.divisional_chart(jd, place,
                                        divisional_chart_factor=divisional_chart_factor)[:const._pp_count_upto_ketu]
    return drig_dhasa(planet_positions, dob,tob,dhasa_level_index=dhasa_level_index,round_duration=round_duration)

def drig_dhasa(
    planet_positions, dob, tob,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6: 1=Maha only, 2=+Antara (default), 3..6 deeper
    round_duration=True
):
    """
    Drig Daśā (two-cycle) with depth control.

    Depth (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)       [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)
    Returned tuple shapes follow the depth setting (see above).
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # Start epoch = birth epoch
    start_jd = utils.julian_day_number(dob, tob)

    # Build house/planet maps (you already use these)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    # Asc and 9th from asc (your original)
    asc_house = p_to_h[const._ascendant_symbol]
    ninth_house = (asc_house + 9 - 1) % 12

    # Drig Mahā progression: 9th house and its aspected kendras for three consecutive signs
    dhasa_progression = []
    for s in range(ninth_house, (ninth_house + 3)):
        s_mod = s % 12
        aspected_k = house.aspected_kendras_of_raasi(s_mod, s_mod in const.even_footed_signs)
        dhasa_progression.append([s_mod] + aspected_k)
    dhasa_progression = sum(dhasa_progression, [])  # flatten

    # Helper: rounding precision (fallback 2)
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    # Helper: recursive deeper levels (>= L3) for a given parent sign
    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        """
        For Drig deeper levels:
          - Split parent_years equally into 12 parts.
          - Child order and direction come from your _antardhasa(parent_sign, p_to_h).
          - Advance JD with full precision; round only the *returned* duration if requested.
        """
        child_years_unrounded = parent_years / 12.0
        jd_cursor = parent_start_jd
        child_order = _antardhasa_from_planet_positions(planet_positions, parent_sign)  # depends on Saturn/Ketu and seed rasi

        if level < dhasa_level_index:
            for child_sign in child_order:
                _recurse(level + 1, child_sign, jd_cursor, child_years_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_years_unrounded * const.sidereal_year
        else:
            for child_sign in child_order:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret   = round(child_years_unrounded, _round_ndigits) if round_duration else child_years_unrounded
                out_rows.append(prefix + (child_sign, start_str, dur_ret))
                jd_cursor += child_years_unrounded * const.sidereal_year

    rows = []
    total_years = 0.0

    # --- First cycle ------------------------------------------------------------
    for dhasa_lord in dhasa_progression:
        # Mahā duration (years) via Narayana helper (unchanged)
        dhasa_duration = float(narayana._dhasa_duration(planet_positions, dhasa_lord))
        total_years += dhasa_duration

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Mahā only
            rows.append((
                dhasa_lord,
                utils.julian_day_to_date_time_string(start_jd),
                round(dhasa_duration, _round_ndigits) if round_duration else dhasa_duration
            ))
            start_jd += dhasa_duration * const.sidereal_year

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antarā — equal split; order from your _antardhasa(parent_sign, p_to_h)
            dd = dhasa_duration / 12.0
            jd_b = start_jd
            bhukthis = _antardhasa_from_planet_positions(planet_positions, dhasa_lord)
            for bhukthi_lord in bhukthis:
                rows.append((
                    dhasa_lord, bhukthi_lord,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(dd, _round_ndigits) if round_duration else dd
                ))
                jd_b += dd * const.sidereal_year
            start_jd += dhasa_duration * const.sidereal_year

        else:
            # L3..L6: recursive expansion under the immediate parent
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,  # start at 2 → build 3..N
                parent_sign=dhasa_lord,
                parent_start_jd=start_jd,
                parent_years=dhasa_duration,
                prefix=(dhasa_lord,),
                out_rows=rows
            )
            start_jd += dhasa_duration * const.sidereal_year

    # Early stop if life-span limit already reached
    if total_years >= const.human_life_span_for_narayana_dhasa:
        return rows

    # --- Second cycle: (12 − first duration) per sign, skip if <= 0 -------------
    for idx, dhasa_lord in enumerate(dhasa_progression):
        # First cycle duration for this index is the sum of the last field we added for that mahā.
        # But shapes differ by depth; simpler to recompute:
        first_dd = float(narayana._dhasa_duration(planet_positions, dhasa_lord))
        dhasa_duration2 = round(12.0 - first_dd, 2)
        if dhasa_duration2 <= 0:
            continue

        total_years += dhasa_duration2
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                dhasa_lord,
                utils.julian_day_to_date_time_string(start_jd),
                round(dhasa_duration2, _round_ndigits) if round_duration else dhasa_duration2
            ))
            start_jd += dhasa_duration2 * const.sidereal_year

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            dd = dhasa_duration2 / 12.0
            jd_b = start_jd
            bhukthis = _antardhasa_from_planet_positions(planet_positions, dhasa_lord)
            for bhukthi_lord in bhukthis:
                rows.append((
                    dhasa_lord, bhukthi_lord,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(dd, _round_ndigits) if round_duration else dd
                ))
                jd_b += dd * const.sidereal_year
            start_jd += dhasa_duration2 * const.sidereal_year

        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=dhasa_lord,
                parent_start_jd=start_jd,
                parent_years=dhasa_duration2,
                prefix=(dhasa_lord,),
                out_rows=rows
            )
            start_jd += dhasa_duration2 * const.sidereal_year

        if total_years >= const.human_life_span_for_narayana_dhasa:
            break

    return rows
def _antardhasa_from_planet_positions(planet_positions,dhasa_lord):
    """ V4.6.5 Antardhasa Ref: Drig Dasa of Parasara - PVR """
    # starting sign: stronger of dhasa sign and 7th from it
    dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_lord, 
                                                                (dhasa_lord+const.HOUSE_7)%12)
    # direction: zodiacal for odd signs otherwise anti-zodiacal
    direction = 1 if dhasa_lord in const.odd_signs else -1
    # progression: Movable signs: regularly, fixed every 6th, 
    # for dual: 3 kendras [1,4,7,10,5,8,11,2,9,12,3,6] from lagna
    if dhasa_lord in const.fixed_signs: # Every 6th
        _dhasa_progression = [(dhasa_seed+direction*h*const.HOUSE_6)%12 for h in range(12)]
    elif dhasa_lord in const.movable_signs:
        _dhasa_progression = [(dhasa_seed+direction*h)%12 for h in range(12)] # Regular
    else:
        _dhasa_progression = [(dhasa_seed+direction*(h-1))%12 for h in [1,4,7,10,5,8,11,2,9,12,3,6]]
    return _dhasa_progression

# --- Small helpers -----------------------------------------------------------

def _mod12(x: int) -> int:
    return x % 12

def _is_odd_sign_1based(s: int) -> bool:
    """Odd signs: 1,3,5,7,9,11 (1-based) => indices 0,2,4,6,8,10."""
    return (s % 2) == 0

def _dist_forward(s: int, t: int) -> int:
    """Zodiacal distance (1..11)."""
    d = (t - s) % 12
    return 12 if d == 0 else d

def _dist_backward(s: int, t: int) -> int:
    """Anti-zodiacal distance (1..11)."""
    d = (s - t) % 12
    return 12 if d == 0 else d

def _is_movable(s: int) -> bool: return s in _MOVABLE
def _is_fixed(s: int)   -> bool: return s in _FIXED
def _is_dual(s: int)    -> bool: return s in _DUAL

def _md_years_for_sign(s: int) -> int:
    if _is_movable(s): return 7
    if _is_fixed(s):   return 8
    return 9  # dual


# --- MD order: aspects via house API, then Drig-Dasa ordering ----------------

def _ordered_aspected_three(chart: List[str], anchor: int) -> List[int]:
    """
    Use house.aspected_raasis_of_the_raasi(chart, anchor) to get the 3 aspected rasis,
    then sort them per Drig Dhasa rule:
      - Go zodiacally for fixed signs and odd dual signs
      - Go anti-zodiacally for movable signs and even dual signs
      - Prefer nearest. (If a rare tie occurs, stable order is kept.)
    """
    candidates = list(house.raasi_drishti_of_the_raasi(chart, anchor) or [])
    if len(candidates) != 3:
        # Defensive: ensure exactly three. If the API returns extras, keep only unique.
        uniq = []
        for c in candidates:
            if c not in uniq:
                uniq.append(c)
        candidates = uniq
        if len(candidates) != 3:
            # As per Parāśara this must be 3; raise if not.
            raise ValueError(f"Aspected rasis for {anchor} not equal to 3: {candidates}")

    # Decide sorting mode
    zodiacal = (_is_fixed(anchor) or (_is_dual(anchor) and _is_odd_sign_1based(anchor)))

    if zodiacal:
        key_fn = lambda t: (_dist_forward(anchor, t), )
    else:
        key_fn = lambda t: (_dist_backward(anchor, t), )

    candidates.sort(key=key_fn)
    return candidates


def _md_order(lagna_sign: int, chart: List[str]) -> List[int]:
    """
    12 mahadashas: 9th + its 3 aspected (ordered), then 10th + its 3, then 11th + its 3.
    """
    seq: List[int] = []
    for offset in (const.HOUSE_9, const.HOUSE_10, const.HOUSE_11):  # 9th, 10th, 11th from Lagna (0-based)
        anchor = _mod12(lagna_sign + offset)
        seq.append(anchor)
        seq.extend(_ordered_aspected_three(chart, anchor))
    # Expect a permutation of the 12 signs
    if len(set(seq)) != 12:
        raise ValueError(f"Drig Dhasa MD sequence not unique: {seq}")
    return seq


# --- Antara seed and per-modality progression --------------------------------

def _antara_seed(parent_sign: int, planet_positions) -> int:
    """
    Starting sign is the stronger of parent sign and 7th from it.
    Uses house.stronger_rasi_from_planet_positions.
    """
    opp = _mod12(parent_sign + const.HOUSE_7)
    stronger = house.stronger_rasi_from_planet_positions(planet_positions, parent_sign, opp)
    return stronger if stronger in (parent_sign, opp) else parent_sign


def _antara_order_for_parent_sign(parent_sign: int, planet_positions) -> List[int]:
    """
    Produce the 12-subperiod sign order for the given parent sign:
      - Seed: stronger of parent sign vs its 7th.
      - Direction: zodiacal if parent_sign is odd (1-based), else anti-zodiacal.
      - Progression:
          Movable: seed, next, next, ... (±1) for 12 entries.
          Fixed  : alternate seed and its 6th for 12 entries.
          Dual   : kantakas (1st, 4th, 7th, 10th) taken from:
                     * zodiacal   -> seeds: [1st, 5th, 9th]
                     * anti-zodiacal -> seeds: [1st, 9th, 5th]
                   Within each quartet, **seed must be first**, then step by ±3.
    """
    start = _antara_seed(parent_sign, planet_positions)
    zodiacal = _is_odd_sign_1based(parent_sign)  # odd => zodiacal; even => anti-zodiacal

    # Movable: regular neighbors in chosen direction
    if _is_movable(parent_sign):
        step = 1 if zodiacal else -1
        return [_mod12(start + i * step) for i in range(12)]

    # Fixed: alternate seed and its 6th
    if _is_fixed(parent_sign):
        a = start
        b = _mod12(start + const.HOUSE_7)
        seq = []
        for i in range(12):
            seq.append(a if (i % 2 == 0) else b)
        return seq

    # Dual: kantakas
    # Step is +3 (zodiacal) or -3 (anti-zodiacal).
    step = 3 if zodiacal else -3

    # Seeds per direction:
    #   zodiacal:     1st, 5th, 9th
    #   anti-zodiacal:1st, 9th, 5th   (this matches your expected Virgo example)
    seeds = [start, _mod12(start + const.HOUSE_5), _mod12(start + const.HOUSE_9)]
    if not zodiacal:
        seeds = [start, _mod12(start + const.HOUSE_9), _mod12(start + const.HOUSE_5)]

    seq: List[int] = []
    for seed in seeds:
        # Ensure seed is **first**, then progress by ±3
        for i in range(4):
            seq.append(_mod12(seed + i * step))
    return seq

# --- Output plumbing ----------------------------------------------------------

def _append_row(rows: List[Tuple], labels: List[int], start_jd: float, dur_years: float,
                round_duration:bool):
    start_str = utils.julian_day_to_date_time_string(start_jd)
    _durn = round(dur_years, _round_ndigits) if round_duration else dur_years
    rows.append((*labels, start_str, float(_durn)))


def _expand_level(rows: List[Tuple],
                  level_target: int,
                  labels: List[int],
                  parent_sign: int,
                  start_jd: float,
                  dur_years: float,
                  current_level: int,
                  planet_positions, round_duration:bool):
    """
    Recursively expand children equally splitting duration, preserving antara order.
    - rows: output sink
    - level_target: Lx requested by user
    - labels: current label stack (sign indices up to current_level)
    - parent_sign: sign index of the current parent block
    - start_jd: start JD of the current parent block
    - dur_years: duration (years) of the current parent block
    - current_level: depth reached so far (1..6)
    """
    if current_level == level_target:
        _append_row(rows, labels, start_jd, dur_years,round_duration)
        return

    order = _antara_order_for_parent_sign(parent_sign, planet_positions)
    child_years = dur_years / 12.0

    jd_ptr = start_jd
    for child_sign in order:
        _expand_level(
            rows=rows,
            level_target=level_target,
            labels=labels + [child_sign],
            parent_sign=child_sign,
            start_jd=jd_ptr,
            dur_years=child_years,
            current_level=current_level + 1,
            planet_positions=planet_positions, round_duration=round_duration
        )
        jd_ptr += child_years * _DAYS_IN_YEAR  # exact 1/12 advancement


# --- Public API ---------------------------------------------------------------

def get_dhasa_antardhasa(jd, place, divisional_chart_factor: int = 1, 
                         dhasa_level_index: int = const.MAHA_DHASA_DEPTH.ANTARA, round_duration=True,
                         method=1) -> List[Tuple]:
    """
    Drig Dhasa main entry.

    Parameters
    ----------
    jd : float
        Julian day at which dhasa timeline begins.
    place : Place
        Observer's location, used for computing Lagna and divisions.
    divisional_chart_factor : int, default=1
        Varga factor (D1, D9, etc.).
    dhasa_level_index : int, default=2
        1..6 (MD only .. Deha).
    method   1=> PVR's 2007 Article - Drig Dasa of Parashara (Default)
             2=> PVR's Book Chapter 21 Drig Dasa
    Returns
    -------
    list of tuples:
        Conforms to the requested level:
            L1: (l1,                                   start_str, dur_years)
            L2: (l1, l2,                                start_str, dur_years)
            L3: (l1, l2, l3,                            start_str, dur_years)
            L4: (l1, l2, l3, l4,                        start_str, dur_years)
            L5: (l1, l2, l3, l4, l5,                    start_str, dur_years)
            L6: (l1, l2, l3, l4, l5, l6,                start_str, dur_years)
        All l* are integers 0..11 (rasi indices).
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")
    if method==2:
        return drig_dhasa_bhukthi(dob, tob, place, divisional_chart_factor, dhasa_level_index, round_duration)
    # Get varga positions and chart (singular function name per your note)
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor)
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    if 'L' not in p_to_h:
        raise ValueError("Lagna sign ('L') not found in planet-house dictionary.")
    lagna_sign = int(p_to_h['L']) % 12

    # Build MD sequence
    md_seq = _md_order(lagna_sign, chart)

    rows: List[Tuple] = []
    jd_ptr = float(jd)

    for md_sign in md_seq:
        md_years = float(_md_years_for_sign(md_sign))

        if dhasa_level_index == 1:
            _append_row(rows, [md_sign], jd_ptr, md_years,round_duration)
        else:
            _expand_level(
                rows=rows,
                level_target=dhasa_level_index,
                labels=[md_sign],
                parent_sign=md_sign,
                start_jd=jd_ptr,
                dur_years=md_years,
                current_level=1,
                planet_positions=planet_positions, round_duration=round_duration
            )

        jd_ptr += md_years * _DAYS_IN_YEAR

    return rows
if __name__ == "__main__":
    utils.set_language('en')
    from jhora.panchanga import drik
    dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob); dcf = 1
    dd = get_dhasa_antardhasa(jd, place, divisional_chart_factor=dcf,dhasa_level_index=1,method=2)
    print(dd)
    dd = get_dhasa_antardhasa(jd, place, divisional_chart_factor=dcf,dhasa_level_index=2,method=1)
    print(dd)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chapter_21_tests()
