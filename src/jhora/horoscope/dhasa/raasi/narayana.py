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
from jhora import const, utils
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik

year_duration = const.sidereal_year


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _dhasa_duration(planet_positions, sign, varsha_narayana=False):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    dhasa_period = utils.count_rasis(house_of_lord, sign) if sign in const.even_footed_signs \
        else utils.count_rasis(sign, house_of_lord)
    dhasa_period -= 1  # Subtract one from the count
    if dhasa_period <= 0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one,
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one.
            However, dasa length becomes 12 years then./
        """
        dhasa_period = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM:
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
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Narayana Daśā (depth-enabled), optimized:
      • No lifespan cutoff
      • Always emits 12 MDs in both cycles (zero-duration included)
      • Memoized antar orders per rāśi
      • On-the-fly child split (no list allocations)
      • Mutable prefix to avoid tuple-concat in recursion

    Output shape unchanged:
      L1: (l1, start_str, dur_years)
      L2: ((l1,l2), start_str, dur_years)
      L3+: ((l1,...,lk), start_str, dur_years)
    """
    # ── Validate depth ────────────────────────────────────────────────────────
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ── Locals & constants (bind hot-path refs) ──────────────────────────────
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    dhasa_factor = year_duration
    if varsha_narayana:
        dhasa_factor /= 360.0

    jd_to_gregorian = utils.jd_to_gregorian
    _dur = _dhasa_duration
    _antar = _narayana_antardhasa
    MAHA_ONLY = const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
    ANTARA = const.MAHA_DHASA_DEPTH.ANTARA
    prec = dhasa_level_index + 1

    # Base progression with exceptions
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    if p_to_h.get(const.KETU_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h.get(const.SATURN_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]

    # Epoch selection
    dhasa_start_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)

    # ── Precompute antar order per rāśi (12 keys) to avoid repeated calls ────
    # NOTE: Because `planet_positions` are fixed for this run, antar order depends only on `parent_rasi`.
    antar_order_cache = {}
    for r in range(12):
        antar_order_cache[r] = tuple(_antar(planet_positions, r))

    # ── Precompute Cycle-1 MD durations and reuse for Cycle-2 complements ────
    md_durations_cycle1 = [float(_dur(planet_positions, lord, varsha_narayana)) for lord in dhasa_progression]

    # ── Helper: append one row (bound locals for speed) ──────────────────────
    rows = []
    rows_append = rows.append
    do_round = round if round_duration else (lambda x, _: x)

    def _append_row(level_key, start_jd, years_len):
        start_str = jd_to_gregorian(start_jd)
        dur_out = do_round(years_len, prec)
        rows_append((level_key, start_str, dur_out))

    # ── Helper: iterate 12 equal splits with last-child remainder ────────────
    # Avoids list allocation; yields base for first 11 and remainder for last.
    def _children(parent_years):
        base = parent_years / 12.0
        for i in range(11):
            yield i, base
        yield 11, parent_years - base * 11.0

    # ── Recursive builder for levels >= 3 (uses mutable prefix list) ─────────
    # Avoid tuple concatenation at each step; only build the final tuple at emit time.
    def _recurse(level, parent_rasi, parent_start_jd, parent_years, prefix_list):
        order = antar_order_cache[parent_rasi]
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # Go deeper
            for idx, child_years in _children(parent_years):
                child_rasi = order[idx]
                prefix_list.append(child_rasi)
                _recurse(level + 1, child_rasi, jd_cursor, child_years, prefix_list)
                prefix_list.pop()
                jd_cursor += child_years * dhasa_factor
        else:
            # Leaf emit (12 children at this level)
            for idx, child_years in _children(parent_years):
                child_rasi = order[idx]
                # Build final tuple ONCE here
                level_key = tuple(prefix_list + [child_rasi])
                _append_row(level_key, jd_cursor, child_years)
                jd_cursor += child_years * dhasa_factor

    # ─────────────────────────────
    # Cycle #1
    # ─────────────────────────────
    for lord_idx, dhasa_lord in enumerate(dhasa_progression):
        dd = md_durations_cycle1[lord_idx]

        if dhasa_level_index == MAHA_ONLY:
            _append_row(dhasa_lord, dhasa_start_jd, dd)
            dhasa_start_jd += dd * dhasa_factor

        elif dhasa_level_index == ANTARA:
            order = antar_order_cache[dhasa_lord]
            jd_b = dhasa_start_jd
            for idx, child_years in _children(dd):
                bhukthi_lord = order[idx]
                _append_row((dhasa_lord, bhukthi_lord), jd_b, child_years)
                jd_b += child_years * dhasa_factor
            dhasa_start_jd = jd_b  # Σ(12 children) == MD

        else:
            # L3..L6
            _recurse(
                level=ANTARA,                   # 2 → build 3..N
                parent_rasi=dhasa_lord,
                parent_start_jd=dhasa_start_jd,
                parent_years=dd,
                prefix_list=[dhasa_lord],       # mutable prefix
            )
            dhasa_start_jd += dd * dhasa_factor

    # ─────────────────────────────
    # Cycle #2 (12 − first), including zeros
    # ─────────────────────────────
    for lord_idx, dhasa_lord in enumerate(dhasa_progression):
        dd2 = 12.0 - md_durations_cycle1[lord_idx]
        if dd2 < 0.0:
            dd2 = 0.0

        if dhasa_level_index == MAHA_ONLY:
            _append_row(dhasa_lord, dhasa_start_jd, dd2)
            dhasa_start_jd += dd2 * dhasa_factor

        elif dhasa_level_index == ANTARA:
            order = antar_order_cache[dhasa_lord]
            jd_b = dhasa_start_jd
            for idx, child_years in _children(dd2):
                bhukthi_lord = order[idx]
                _append_row((dhasa_lord, bhukthi_lord), jd_b, child_years)
                jd_b += child_years * dhasa_factor
            dhasa_start_jd = jd_b

        else:
            _recurse(
                level=ANTARA,
                parent_rasi=dhasa_lord,
                parent_start_jd=dhasa_start_jd,
                parent_years=dd2,
                prefix_list=[dhasa_lord],
            )
            dhasa_start_jd += dd2 * dhasa_factor

    return rows


def _narayana_dhasa_seed_for_divisional_chart(jd_at_dob, place, divisional_chart_factor=1, chart_method=1, **kwargs):
    if divisional_chart_factor == 1:
        return _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place)
    planet_positions_rasi = charts.divisional_chart(jd_at_dob, place, **kwargs)[:const._pp_count_upto_ketu]
    h_to_p_rasi = utils.get_house_planet_list_from_planet_positions(planet_positions_rasi)
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    # For D-n planet_positions_rasi get the lord of nth house in rasi planet_positions_rasi
    seed_house = (p_to_h_rasi[const._ascendant_symbol] + divisional_chart_factor - 1) % 12
    lord_of_seed_house = house.house_owner_from_planet_positions(planet_positions_rasi, seed_house, check_during_dhasa=True)
    """
        Important:
        Take the rasi occupied by Lord of Seed House in the divisional planet_positions_rasi of interest as lagna of varga planet_positions_rasi
    """
    # Get Varga Chart
    varga_planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    lord_sign = p_to_h_varga[lord_of_seed_house]
    seventh_house = (lord_sign + const.HOUSE_7) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(varga_planet_positions, lord_sign, seventh_house)
    return dhasa_seed_sign


def narayana_dhasa_for_divisional_chart(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Narayana Daśā (depth-enabled; equal-split at each deeper level)
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    if divisional_chart_factor == 1:
        return narayana_dhasa_for_rasi_chart(
            dob, tob, place, years, months, sixty_hours, dhasa_level_index,
            round_duration, varsha_narayana,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
    varga_planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _narayana_dhasa_seed_for_divisional_chart(jd_at_dob, place, divisional_chart_factor)
    return _narayana_dhasa_calculation(
        varga_planet_positions, dhasa_seed_sign, dob, tob, place,
        years=years, months=months,
        sixty_hours=sixty_hours, dhasa_level_index=dhasa_level_index,
        varsha_narayana=varsha_narayana, round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


def _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place, **kwargs):
    planet_positions = charts.rasi_chart(jd_at_dob, place, **kwargs)[:const._pp_count_upto_ketu]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house + 7 - 1) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    return dhasa_seed_sign


def narayana_dhasa_for_rasi_chart(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Narayana Daśā (depth-enabled; equal-split at each deeper level)
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.rasi_chart(jd_at_dob, place, **kwargs)[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place, **kwargs)
    return _narayana_dhasa_calculation(
        planet_positions, dhasa_seed_sign, dob, tob, place,
        years=years, months=months,
        sixty_hours=sixty_hours, dhasa_level_index=dhasa_level_index, varsha_narayana=varsha_narayana,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


def _narayana_antardhasa(planet_positions, dhasa_rasi):
    """
    Antardaśā order for a given MAHĀ-daśā sign (dhasa_rasi), matching JHora/Parāśari usage.
    """
    # 1) Antardaśā seed
    lord_of_dhasa_rasi = house.house_owner_from_planet_positions(
        planet_positions, dhasa_rasi, check_during_dhasa=True
    )
    house_of_dhasa_rasi_lord = planet_positions[lord_of_dhasa_rasi + 1][1][0]

    lord_of_7th = house.house_owner_from_planet_positions(
        planet_positions, (dhasa_rasi + const.HOUSE_7) % 12, check_during_dhasa=True
    )
    house_of_dhasa_rasi_lord_7th = planet_positions[lord_of_7th + 1][1][0]

    seed = house.stronger_rasi_from_planet_positions(
        planet_positions, house_of_dhasa_rasi_lord, house_of_dhasa_rasi_lord_7th
    )

    # 2) Direction with exceptions
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    # base rule
    direction = 1 if (seed in const.odd_signs) else -1

    # Saturn in antardaśā SEED → force forward
    if p_to_h.get(const.SATURN_ID, -1) == seed:
        direction = 1

    # Ketu in the MAHĀ-DAŚĀ sign (dhasa_rasi) → flip antardaśā direction
    if p_to_h.get(const.KETU_ID, -1) == dhasa_rasi:
        direction *= -1

    # 3) Twelve antardaśās from seed in final direction
    return [(seed + direction * i) % 12 for i in range(12)]


def _varsha_naryana_seed(dob, tob, place, years=1, months=1, sixty_hours=1, divisional_chart_factor=1, chart_method=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    rasi_planet_positions = charts.rasi_chart(jd_at_years, place)[:const._pp_count_upto_ketu]
    p_to_h_rasi = utils.get_planet_house_dictionary_from_planet_positions(rasi_planet_positions)
    varga_planet_positions = charts.divisional_chart(
        jd_at_years, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method
    )[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    natal_lagna = p_to_h_rasi[const._ascendant_symbol]
    annual_house = (natal_lagna + (years - 1) + divisional_chart_factor - 1) % 12
    annual_house_owner_in_varga = house.house_owner_from_planet_positions(
        varga_planet_positions, annual_house, check_during_dhasa=True
    )
    dhasa_seed_sign = p_to_h_varga[annual_house_owner_in_varga]
    return dhasa_seed_sign


def varsha_narayana_dhasa_bhukthi(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Varsha Narayana Daśā (depth-enabled; equal-split at each deeper level)
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    varga_planet_positions = charts.divisional_chart(
        jd_at_years, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _varsha_naryana_seed(dob, tob, place, years, months, sixty_hours, divisional_chart_factor)
    nd = _narayana_dhasa_calculation(
        varga_planet_positions, dhasa_seed_sign, dob, tob, place,
        years=years, months=months,
        sixty_hours=sixty_hours, dhasa_level_index=dhasa_level_index, varsha_narayana=True,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    return nd


def get_running_dhasa_for_given_date(
    jd_given, jd_at_dob, place,
    divisional_chart_factor=1, chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,  # 6
    years=1, months=1, sixty_hours=1,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Instant path finder: return running lords and (start, end) at each level k=1..d.
    No full list is materialized. O(d) time.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- derive dob,tob once (no need to recompute jd_at_dob)
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    # ---- base positions & seed (D1 unless varga requested)
    planet_positions = charts.rasi_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place, **kwargs)

    if divisional_chart_factor > 1:
        varga_planet_positions = charts.divisional_chart(
            jd_at_dob, place,
            divisional_chart_factor=divisional_chart_factor, chart_method=chart_method, **kwargs
        )[:const._pp_count_upto_ketu]
        planet_positions = varga_planet_positions[:]
        dhasa_seed_sign = _narayana_dhasa_seed_for_divisional_chart(
            jd_at_dob, place, divisional_chart_factor, chart_method, **kwargs
        )

    # ---- duration scale: days per "dasha-year"
    dhasa_factor = year_duration
    if varsha_narayana:
        dhasa_factor /= 360.0

    # ---- bind locals
    jd_to_gregorian = utils.jd_to_gregorian
    _dur = _dhasa_duration
    _antar = _narayana_antardhasa

    # ---- progression with exceptions (same as generator)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    if p_to_h.get(const.KETU_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h.get(const.SATURN_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]

    # ---- epoch (identical to your generator)
    epoch_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)

    # ---- cache antar order per rāśi (12 entries)
    antar_order_cache = {r: tuple(_antar(planet_positions, r)) for r in range(12)}

    # ---- MD durations (cycle 1) and complements (cycle 2)
    md1_years = [float(_dur(planet_positions, lord, varsha_narayana)) for lord in dhasa_progression]
    md2_years = [max(0.0, 12.0 - y) for y in md1_years]

    md_lords = list(dhasa_progression) + list(dhasa_progression)
    md_years = md1_years + md2_years

    # ---- exact MD start JDs (length 24)
    md_starts_jd = [epoch_jd]
    for i in range(1, len(md_years)):
        md_starts_jd.append(md_starts_jd[-1] + md_years[i - 1] * dhasa_factor)

    # ---- select MD by JD (jd in [start_i, start_{i+1}); last open-ended)
    from bisect import bisect_right
    i = bisect_right(md_starts_jd, jd_given) - 1
    if i < 0:
        i = 0
    if i >= len(md_lords):
        i = len(md_lords) - 1

    md_lord = int(md_lords[i])
    md_year = float(md_years[i])
    md_start = md_starts_jd[i]
    md_end = (md_starts_jd[i + 1] if i + 1 < len(md_starts_jd) else md_start + md_year * dhasa_factor)

    # ---- output accumulator (now START & END tuples)
    out = []
    out.append(((md_lord,), jd_to_gregorian(md_start), jd_to_gregorian(md_end)))

    # ---- descend levels 2..d
    parent_lord = md_lord
    parent_start_jd = md_start
    parent_years = md_year

    for level in range(2, int(dhasa_level_index) + 1):
        # equal split (years) and JD boundaries
        base_years = parent_years / 12.0
        base_jd = base_years * dhasa_factor

        # select child index by JD boundaries inside THIS parent
        idx = None
        for k in range(11):  # children 0..10
            boundary_jd = parent_start_jd + (k + 1) * base_jd  # end of child k
            if jd_given < boundary_jd:
                idx = k
                break
        if idx is None:
            idx = 11  # last child

        # child rāśi from antar order of the parent
        order = antar_order_cache[parent_lord]
        child_rasi = int(order[idx])

        # child's start JD and end JD (remainder in last child)
        child_start_jd = parent_start_jd + idx * base_jd
        if idx < 11:
            child_end_jd = child_start_jd + base_jd
            child_years = base_years
        else:
            child_end_jd = parent_start_jd + parent_years * dhasa_factor
            child_years = parent_years - base_years * 11.0

        # append and prepare next level (prefix consistently extended)
        prefix = out[-1][0] + (child_rasi,)
        out.append((prefix, jd_to_gregorian(child_start_jd), jd_to_gregorian(child_end_jd)))

        parent_lord = child_rasi
        parent_start_jd = child_start_jd
        parent_years = child_years

    return out


def narayana_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method=1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Narayana — return ONLY the immediate (p -> p+1) children inside the given parent span:
      • Child order via narayana._narayana_antardhasa(planet_positions, parent_sign)
      • Equal split: parent_years / 12
      • Exact tiling with last child clamped to parent_end
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = int(path[-1])

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor, **kwargs
    )[:const._pp_count_upto_ketu]
    order = list(_narayana_antardhasa(planet_positions, parent_sign))
    if not order:
        return []

    child_years = parent_years / 12.0
    out, cursor = [], start_jd
    for i, cs in enumerate(order):
        cs = int(cs)
        child_end = end_jd if i == 11 else cursor + child_years * year_duration
        out.append([path + (cs,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break
    out[-1][2] = _jd_to_tuple(end_jd)
    return out


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    dcf = 9
    varsha_narayana = True
    years = 31

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            divisional_chart_factor=dcf,
            varsha_narayana=varsha_narayana,
            years=years,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = narayana_dhasa_for_divisional_chart(
            dob, tob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            divisional_chart_factor=dcf,
            varsha_narayana=varsha_narayana,
            years=years,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=2
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chapter_18_tests()
    pvr_tests.varsha_narayana_tests()
