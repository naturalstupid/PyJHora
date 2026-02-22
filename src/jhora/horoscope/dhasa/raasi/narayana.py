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
"""
    Note: Some Astrologers like PVR Force Scoprio/Aquarius to Mars/Kethu or Saturn/Rahu
    instead of finding the strongest.
    You can force, the owner using const.scorpio_owner_for_dhasa_calculations= and 
    const.aquarius_owner_for_dhasa_calculations=
"""
from jhora import const,utils
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik
year_duration = const.sidereal_year
def _dhasa_duration(planet_positions,sign,varsha_narayana=False):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    dhasa_period = utils.count_rasis(house_of_lord,sign) if sign in const.even_footed_signs \
                            else utils.count_rasis(sign, house_of_lord) 
    dhasa_period -= 1 # Subtract one from the count
    if dhasa_period <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then./
        """
        dhasa_period = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM : # > const._FRIEND:
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        dhasa_period += 1
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEBILITATED_NEECHAM:
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
        dhasa_period -= 1
    if varsha_narayana:
        dhasa_period *= 3
    return dhasa_period


def _narayana_dhasa_calculation(
    planet_positions,
    dhasa_seed_sign,
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    varsha_narayana=False,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6  (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True
):
    """
    Narayana Daśā (depth-enabled) with lifespan cutoff enforced after EVERY innermost append.

    ─────────────────────────────────────────────────────────────────────────────
    Depth control (replaces include_antardhasa):
        1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_units)
        2 = ANTARA               -> rows: (l1, l2,           start_str, dur_units)      [DEFAULT]
        3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_units)
        4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_units)
        5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_units)
        6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_units)

    Units & time advancement:
        • _dhasa_duration(...) returns **years** (same as your original).
        • We advance JD with `dhasa_factor`:
              dhasa_factor = year_duration
              if varsha_narayana: dhasa_factor /= 360.0
          (kept exactly as in your original code)
        • Returned duration field (dur_units) remains in **years**.
        • Only the **returned** duration is rounded (when round_duration=True).
          All JD math uses full precision.

    Progression & exceptions (unchanged):
        • Base progression from `const.narayana_dhasa_normal_progression[dhasa_seed_sign]`.
        • Ketu-in-seed → `const.narayana_dhasa_ketu_exception_progression`.
        • Saturn-in-seed → `const.narayana_dhasa_saturn_exception_progression`.

    Antar order & deeper levels:
        • Antar order at every level uses your `_narayana_antardhasa(planet_positions, parent_rasi)`.
        • L2 and deeper: Each parent period is split into **12 equal parts** (Σ children = parent),
          emitted in the antar order returned by your helper.
          (If you later want a **weighted** split rule here, we can swap it in without changing the interface.)

    Lifespan cutoff (critical fix):
        • We increment `total_years` and check the cutoff **immediately after each append**:
            – L1: after adding each Maha row,
            – L2: after each Antara row,
            – L3+: after each leaf row in recursion.
        • Cutoff is:
              limit = const.human_life_span_for_narayana_dhasa * (3.0 if varsha_narayana else 1.0)
          (exactly your earlier semantics).

    Returns:
        A flat list of tuples with depth-dependent shapes shown above.

    Notes:
        • This function does **not** change your _dhasa_duration or _narayana_antardhasa logic;
          it only adds depth recursion & corrects where lifespan cutoff is enforced.
        • No “double-advance” at L2: since Σ(12 Antara) = Maha, we DON’T add the Maha duration again.
    """
    # ── Safety guard for depth argument ────────────────────────────────────────
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ── Prepare progression with exception handling (unchanged) ───────────────
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    dhasa_factor = year_duration
    if varsha_narayana:
        dhasa_factor /= 360.0

    # Base progression from seed
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    # Ketu and Saturn exceptions
    if p_to_h.get(const.KETU_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h.get(const.SATURN_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]

    # ── Epoch selection (unchanged) ───────────────────────────────────────────
    jd_at_dob    = utils.julian_day_number(dob, tob)
    dhasa_start_jd = drik.next_solar_date(
        jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours
    )

    # ── Output rows & running totals ──────────────────────────────────────────
    rows         = []
    total_years  = 0.0                                      # in **years**
    limit        = const.human_life_span_for_narayana_dhasa * (3.0 if varsha_narayana else 1.0)
    stop         = False                                    # early-termination switch
    _round_nd    = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    # ── Recursive builder for L3+ (equal split into 12; antar order from helper) ─
    def _recurse(level, parent_rasi, parent_start_jd, parent_years, prefix, out_rows):
        """
        Build rows for levels >= 3 using the same antar order at each node.
        Equal split: child_years = parent_years / 12.0 → Σ children = parent.
        Lifespan is checked after every row append.
        """
        nonlocal total_years, stop
        if stop:
            return

        child_years = parent_years / 12.0
        jd_cursor   = parent_start_jd
        bhuktis     = _narayana_antardhasa(planet_positions, parent_rasi)  # your order

        if level < dhasa_level_index:
            # Go deeper one level for each child
            for child_rasi in bhuktis:
                if stop:
                    break
                _recurse(level + 1, child_rasi, jd_cursor, child_years, prefix + (child_rasi,), out_rows)
                jd_cursor += child_years * dhasa_factor
        else:
            for child_rasi in bhuktis:
                if stop:
                    break
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret   = round(child_years, _round_nd) if round_duration else child_years
                out_rows.append(prefix + (child_rasi, start_str, dur_ret))

                # Lifespan increment & cutoff at the innermost emission
                total_years += child_years
                if total_years >= limit:
                    stop = True
                    break

                jd_cursor += child_years * dhasa_factor

    # ─────────────────────────────
    # Cycle #1
    # ─────────────────────────────
    for dhasa_lord in dhasa_progression:
        if stop:
            break

        # Maha duration (years) via your helper
        dd = float(_dhasa_duration(planet_positions, dhasa_lord, varsha_narayana))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1 (Maha only)
            start_str = utils.julian_day_to_date_time_string(dhasa_start_jd)
            dur_ret   = round(dd, _round_nd) if round_duration else dd
            rows.append((dhasa_lord, start_str, dur_ret))

            # Lifespan increment & cutoff (after each MD append)
            total_years += dd
            if total_years >= limit:
                stop = True
                break

            dhasa_start_jd += dd * dhasa_factor

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2 (Antara): equal split into 12, order from your antar helper
            ddb   = dd / 12.0
            jd_b  = dhasa_start_jd
            order = _narayana_antardhasa(planet_positions, dhasa_lord)

            for bhukthi_lord in order:
                if stop:
                    break
                start_str = utils.julian_day_to_date_time_string(jd_b)
                dur_ret   = round(ddb, _round_nd) if round_duration else ddb
                rows.append((dhasa_lord, bhukthi_lord, start_str, dur_ret))

                # Lifespan increment & cutoff (after each AD append)
                total_years += ddb
                if total_years >= limit:
                    stop = True
                    break

                jd_b += ddb * dhasa_factor

            # IMPORTANT: Do NOT "double-advance" MD at L2; Σ(12 AD) == MD
            dhasa_start_jd = jd_b

        else:
            # L3..L6 (recursive equal split under MD)
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,     # 2 → build 3..N
                parent_rasi=dhasa_lord,
                parent_start_jd=dhasa_start_jd,
                parent_years=dd,
                prefix=(dhasa_lord,),
                out_rows=rows
            )

            # Honor early termination
            if stop:
                break

            # Advance Maha cursor by full MD length; recursion advanced internally for leaves
            dhasa_start_jd += dd * dhasa_factor

    # Early return if cutoff hit mid-cycle
    if stop:
        return rows

    # ─────────────────────────────
    # Cycle #2 (12 − first)    (identical structure; skip if 2nd duration <= 0)
    # ─────────────────────────────
    for idx, dhasa_lord in enumerate(dhasa_progression):
        if stop:
            break

        first_dd = float(_dhasa_duration(planet_positions, dhasa_lord, varsha_narayana))
        dd2 = 12.0 - first_dd
        if dd2 <= 0:
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1 (Maha only)
            start_str = utils.julian_day_to_date_time_string(dhasa_start_jd)
            dur_ret   = round(dd2, _round_nd) if round_duration else dd2
            rows.append((dhasa_lord, start_str, dur_ret))

            total_years += dd2
            if total_years >= limit:
                break

            dhasa_start_jd += dd2 * dhasa_factor

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2 (Antara)
            ddb   = dd2 / 12.0
            jd_b  = dhasa_start_jd
            order = _narayana_antardhasa(planet_positions, dhasa_lord)

            for bhukthi_lord in order:
                if stop:
                    break
                start_str = utils.julian_day_to_date_time_string(jd_b)
                dur_ret   = round(ddb, _round_nd) if round_duration else ddb
                rows.append((dhasa_lord, bhukthi_lord, start_str, dur_ret))

                total_years += ddb
                if total_years >= limit:
                    stop = True
                    break

                jd_b += ddb * dhasa_factor

            # again: no double-advance at L2
            dhasa_start_jd = jd_b

        else:
            # L3..L6 (recursive equal split under MD)
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_rasi=dhasa_lord,
                parent_start_jd=dhasa_start_jd,
                parent_years=dd2,
                prefix=(dhasa_lord,),
                out_rows=rows
            )
            if stop:
                break
            dhasa_start_jd += dd2 * dhasa_factor

    return rows


def narayana_dhasa_for_divisional_chart(dob,tob,place,years=1, months=1, sixty_hours=1,divisional_chart_factor=1,
                                        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,round_duration=True):
    """
    Narayana Daśā (depth-enabled; equal-split at each deeper level)

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
    if divisional_chart_factor==1:
        return narayana_dhasa_for_rasi_chart(dob, tob, place, years, months, sixty_hours, dhasa_level_index,
                                             round_duration)
    # Get Rasi Chart first
    jd_at_dob = utils.julian_day_number(dob,tob)
    planet_positions_rasi = charts.divisional_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    h_to_p_rasi = utils.get_house_planet_list_from_planet_positions(planet_positions_rasi)
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    # For D-n planet_positions_rasi get the lord of nth house in rasi planet_positions_rasi
    seed_house = (p_to_h_rasi[const._ascendant_symbol]+divisional_chart_factor-1)%12
    lord_of_seed_house = house.house_owner_from_planet_positions(planet_positions_rasi, seed_house,check_during_dhasa=True)
    """ 
        Important:
        Take the rasi occupied by Lord of Seed House in the divisional planet_positions_rasi of interest as lagna of varga planet_positions_rasi
    """
    # Get Varga Chart
    varga_planet_positions = charts.divisional_chart(jd_at_dob, place,
                                        divisional_chart_factor=divisional_chart_factor)[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    lord_sign = p_to_h_varga[lord_of_seed_house]
    seventh_house = (lord_sign+const.HOUSE_7)%12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(varga_planet_positions, lord_sign, seventh_house)
    return _narayana_dhasa_calculation(varga_planet_positions,dhasa_seed_sign,dob,tob,place,years=years, months=months, 
                                       sixty_hours=sixty_hours,dhasa_level_index=dhasa_level_index,varsha_narayana=False,
                                       round_duration=round_duration)
def narayana_dhasa_for_rasi_chart(dob,tob,place,years=1,months=1,sixty_hours=1,
                                  dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,round_duration=True):
    """
    Narayana Daśā (depth-enabled; equal-split at each deeper level)

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
    planet_positions = charts.rasi_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house+7-1)%12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    return _narayana_dhasa_calculation(planet_positions,dhasa_seed_sign,dob,tob,place,years=years,months=months,
                                       sixty_hours=sixty_hours,dhasa_level_index=dhasa_level_index,varsha_narayana=False,
                                       round_duration=round_duration)
def _narayana_antardhasa(planet_positions,dhasa_rasi):
    lord_of_dhasa_rasi = house.house_owner_from_planet_positions(planet_positions, dhasa_rasi, check_during_dhasa=True)
    house_of_dhasa_rasi_lord = planet_positions[lord_of_dhasa_rasi+1][1][0]
    lord_of_7thhouse_of_dhasa_rasi = house.house_owner_from_planet_positions(planet_positions, (dhasa_rasi+7)%12, check_during_dhasa=True)
    house_of_dhasa_rasi_lord_7thHouse = planet_positions[lord_of_7thhouse_of_dhasa_rasi+1][1][0]
    antardhasa_seed_rasi = house.stronger_rasi_from_planet_positions(planet_positions, house_of_dhasa_rasi_lord, house_of_dhasa_rasi_lord_7thHouse)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    return _narayana_antardhasa_old(antardhasa_seed_rasi,p_to_h)
def _narayana_antardhasa_old(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
def varsha_narayana_dhasa_bhukthi(dob,tob,place,years=1,months=1,sixty_hours=1,divisional_chart_factor=1,
                                  dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,round_duration=True):
    """
    Varsha Narayana Daśā (depth-enabled; equal-split at each deeper level)

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
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years)
    rasi_planet_positions = charts.rasi_chart(jd_at_years, place)[:const._pp_count_upto_ketu]
    p_to_h_rasi = utils.get_planet_house_dictionary_from_planet_positions(rasi_planet_positions)
    varga_planet_positions = charts.divisional_chart(jd_at_years, place,
                                        divisional_chart_factor=divisional_chart_factor)[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    natal_lagna =  p_to_h_rasi[const._ascendant_symbol]
    annual_house = (natal_lagna+(years-1)+divisional_chart_factor-1)%12
    h_to_p_varga = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h_varga)
    annual_house_owner_in_varga = house.house_owner_from_planet_positions(varga_planet_positions,annual_house,check_during_dhasa=True)
    dhasa_seed_sign = p_to_h_varga[annual_house_owner_in_varga]
    nd = _narayana_dhasa_calculation(varga_planet_positions, dhasa_seed_sign, dob,tob,place,years=years,months=months,
                                     sixty_hours=sixty_hours,dhasa_level_index=dhasa_level_index,varsha_narayana=True,
                                     round_duration=round_duration)
    return nd
    
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    utils.set_language('en')
    pvr_tests._narayana_test_5()
    exit()
    pvr_tests.chapter_18_tests()
    pvr_tests.varsha_narayana_tests()
