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
    Kalachakra Dasha -- 5 selectable methods:
        SANTHANAM, BV_RAMAN, PVR_SANJAY_RATH, RAGHAVACHARYA, SM_SINGH

    A nakshatra-pada-based dasha with 5 selectable calculation methods,
    each with its own Mahadasa seed/progression and Antardasa rule:

        SANTHANAM / SM_SINGH:
            Mahadasa seeded from the dhasa_starting_planet's own nakshatra
            pada (via the standard Kalachakra group/pada lookup). Antardasa
            for SANTHANAM rotates the MD's own Kalachakra row starting from
            the MD sign; for SM_SINGH each Antardasa steps one pada forward
            through the Kalachakra pada sequence.

        BV_RAMAN / PVR_SANJAY_RATH:
            Mahadasa seeded from the navamsa of the dhasa_starting_planet's
            D-1 longitude. BV_RAMAN's Antardasa rotates the MD's own
            Kalachakra row from the MD sign (same rule as SANTHANAM);
            PVR_SANJAY_RATH's Antardasa is a fixed progressive Kalachakra
            pada row assigned per Mahadasa.

        RAGHAVACHARYA:
            Mahadasa signs are consecutive navamsa padas starting from the
            dhasa_starting_planet's own pada, each Mahadasa sign being that
            pada's Kalachakra-navamsa sign. Antardasa uses the nine child
            padas of the Mahadasa's own pada.

    Levels 3 and deeper (Pratyantara, Sookshma, Praana, Deha) are generated
    for all 5 methods by recursively applying the same children engine,
    _get_kalachakra_children_jd(), used by get_dhasa_antardhasa(),
    get_immediate_children() and get_running_dhasa_for_given_date().
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts
_MAHA_COUNT = 9
year_duration = const.sidereal_year
# Sanity backstop (days) against drik._get_dhasa_end_jd() returning a result
# far from the linear (duration * year_duration) estimate for a narrow band
# of small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0
# Threshold (days) below which drik._get_dhasa_end_jd()'s solar-transit
# search is not reliable; below this, boundaries are interpolated instead.
_SUB_DAY_DURATION_DAYS = 1.0
_PADAS_IN_ZODIAC = 108
_PADAS_IN_BLOCK = 9


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    End JD for a given start JD and duration in years, with a sanity
    backstop around drik._get_dhasa_end_jd().
    """
    end_jd = drik._get_dhasa_end_jd(
        start_jd=start_jd_local,
        place=place,
        total_dasa_years=duration_years,
    )
    expected_jd = start_jd_local + duration_years * year_duration
    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd
    return end_jd


def _tuple_to_jd(date_tuple):
    y, m, d, fh = date_tuple
    return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))


def _jd_to_tuple(jd_value):
    return utils.jd_to_gregorian(jd_value)


# =============================================================================
# Basic helpers
# =============================================================================
def _get_dhasa_starting_planet_longitude(jd, place, divisional_chart_factor=1, chart_method=1,
                                         dhasa_starting_planet=const.MOON_ID):
    """ Returns dhasa_starting_planet's D-1 longitude as 0..360 degrees. """
    planet_longitude = charts.get_chart_element_longitude(jd, place,
                                        divisional_chart_factor=divisional_chart_factor,
                                        chart_method=chart_method,
                                        dhasa_starting_planet=dhasa_starting_planet)
    return planet_longitude
def _kc_group_for_nak(nak0):
    """ nak0 is 0-based nakshatra index. Returns Kalachakra group index 0..3. """
    if nak0 in const.savya_stars_1:
        return 0
    if nak0 in const.savya_stars_2:
        return 1
    if nak0 in const.apasavya_stars_1:
        return 2
    if nak0 in const.apasavya_stars_2:
        return 3
    raise ValueError(f"Nakshatra index {nak0} not found in Kalachakra groups")
def _rotate_from(seq, item):
    seq = list(seq)
    if item not in seq:
        return seq
    index = seq.index(item)
    return seq[index:] + seq[:index]
def _sign_years(signs):
    return [float(const.kalachakra_dhasa_duration[int(rasi)]) for rasi in signs]
def _proportional_split(parent_years, child_signs):
    weights = _sign_years(child_signs)
    total = sum(weights)
    if total == 0:
        raise ValueError("Invalid Kalachakra duration weights")
    return [float(parent_years) * weight / total for weight in weights]
def _dhasa_starting_planet_pada_details_from_remainder(dhasa_starting_planet_longitude):
    """
    Uses utils.nakshatra_pada(longitude), where:
        nak       = 1..27
        pada      = 1..4
        reminder  = degrees elapsed inside nakshatra
    Returns:
        nak0, pada0, pada_fraction, reminder
    """
    nak, pada, reminder = utils.nakshatra_pada(dhasa_starting_planet_longitude)
    one_pada = 360.0 / 108.0
    nak0 = nak - 1
    pada0 = pada - 1
    pada_elapsed = reminder - pada0 * one_pada
    pada_fraction = pada_elapsed / one_pada
    pada_fraction = max(0.0, min(1.0, pada_fraction))
    return nak0, pada0, pada_fraction, reminder
def _nak_pada_from_longitude(lon):
    """ Direct longitude-based nakshatra-pada helper. Returns: nak0, pada0 """
    lon = lon % 360.0
    one_nak = 360.0 / 27.0
    one_pada = 360.0 / 108.0
    nak0 = int(lon // one_nak)
    rem = lon % one_nak
    pada0 = int(rem // one_pada)
    return min(nak0, 26), min(pada0, 3)
def _navamsa_rasi_from_longitude(lon):
    """
    Standard navamsa sign mapping. Movable signs start from themselves,
    fixed signs start from the 9th from themselves, dual signs start from
    the 5th from themselves.
    """
    lon = lon % 360.0
    rasi = int(lon // 30.0)
    offset = lon - rasi * 30.0
    nav_index = int(offset // (30.0 / 9.0))
    if rasi in (0, 3, 6, 9):
        start = rasi
    elif rasi in (1, 4, 7, 10):
        start = (rasi + 8) % 12
    else:
        start = (rasi + 4) % 12
    return (start + nav_index) % 12
def _navamsa_start_info_from_longitude(lon):
    """
    Used by BV Raman and PVR/Sanjay Rath. From a D-1 longitude, returns:
        navamsa_rasi, nav_start_d1_longitude, nav_fraction, navamsa_seed_longitude
    Seed = start of dhasa_starting_planet's current navamsa rasi.
    """
    lon = lon % 360.0
    one_nav = 30.0 / 9.0
    d1_rasi = int(lon // 30.0)
    offset = lon - d1_rasi * 30.0
    nav_index = int(offset // one_nav)
    nav_start_d1_longitude = d1_rasi * 30.0 + nav_index * one_nav
    elapsed_in_nav = lon - nav_start_d1_longitude
    nav_fraction = elapsed_in_nav / one_nav
    nav_fraction = max(0.0, min(1.0, nav_fraction))
    navamsa_rasi = _navamsa_rasi_from_longitude(lon)
    navamsa_seed_longitude = navamsa_rasi * 30.0
    return (
        navamsa_rasi,
        nav_start_d1_longitude,
        nav_fraction,
        navamsa_seed_longitude,
    )


# =============================================================================
# Kalachakra sequence helpers
# =============================================================================
def _next_kc_pada(kc_index, pada0):
    """
    Move to the next Kalachakra pada cycle. pada0 is 0..3. When crossing
    pada 4 to pada 1: savya 1 <-> savya 2, apasavya 1 <-> apasavya 2.
    """
    if pada0 < 3:
        return kc_index, pada0 + 1
    next_pada0 = 0
    if kc_index == 0:
        next_kc = 1
    elif kc_index == 1:
        next_kc = 0
    elif kc_index == 2:
        next_kc = 3
    else:
        next_kc = 2
    return next_kc, next_pada0
def _kc_pada_after_steps(start_kc, start_pada, steps):
    cur_kc = start_kc
    cur_pada = start_pada
    for _ in range(steps):
        cur_kc, cur_pada = _next_kc_pada(cur_kc, cur_pada)
    return cur_kc, cur_pada
def _build_progressive_kc_pada_list(start_kc, start_pada):
    """ Used by PVR/Sanjay Rath: each MD's AD uses a progressive Kalachakra pada row. """
    out = []
    cur_kc = start_kc
    cur_pada = start_pada
    for _ in range(_MAHA_COUNT):
        out.append((cur_kc, cur_pada))
        cur_kc, cur_pada = _next_kc_pada(cur_kc, cur_pada)
    return out
def _extend_md_sequence_from_running(
    cycle,
    full_md_years,
    running_md_index,
    kc_index,
    pada0,
):
    """
    Returns _MAHA_COUNT MDs starting from running_md_index. If the current
    pada cycle ends, continues into subsequent pada cycles. Used by
    Santhanam, Raman, and PVR/Sanjay Rath.
    """
    md_signs = []
    md_years = []
    md_kc_pada = []
    for i in range(running_md_index, len(cycle)):
        md_signs.append(int(cycle[i]))
        md_years.append(float(full_md_years[i]))
        md_kc_pada.append((kc_index, pada0))
        if len(md_signs) >= _MAHA_COUNT:
            return md_signs, md_years, md_kc_pada
    cur_kc = kc_index
    cur_pada = pada0
    while len(md_signs) < _MAHA_COUNT:
        cur_kc, cur_pada = _next_kc_pada(cur_kc, cur_pada)
        next_cycle = list(const.kalachakra_rasis[cur_kc][cur_pada])
        next_years = _sign_years(next_cycle)
        for sign, years in zip(next_cycle, next_years):
            md_signs.append(int(sign))
            md_years.append(float(years))
            md_kc_pada.append((cur_kc, cur_pada))
            if len(md_signs) >= _MAHA_COUNT:
                break
    return md_signs, md_years, md_kc_pada
def _find_running_md_index_from_elapsed(full_md_years, elapsed_years):
    cumulative = []
    total = 0.0
    for years in full_md_years:
        total += years
        cumulative.append(total)
    running_md_index = 0
    for i, cum_years in enumerate(cumulative):
        if elapsed_years < cum_years:
            running_md_index = i
            break
    elapsed_before_md = 0.0
    if running_md_index > 0:
        elapsed_before_md = cumulative[running_md_index - 1]
    elapsed_in_running_md = elapsed_years - elapsed_before_md
    return running_md_index, elapsed_in_running_md
def _deha_rasi_from_nak_pada(nak0, pada0):
    """
    Raghavacharya MD lord mapping.
    Savya block rows:    row0 Ar,Ta,Ge,Cn  row1 Le,Vi,Li,Sc  row2 Sg,Cp,Aq,Pi
    Apasavya block rows: row0 Sc,Li,Vi,Cn  row1 Le,Ge,Ta,Ar  row2 Pi,Aq,Cp,Sg
    """
    savya_deha_rows = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [8, 9, 10, 11],
    ]
    apasavya_deha_rows = [
        [7, 6, 5, 3],
        [4, 2, 1, 0],
        [11, 10, 9, 8],
    ]
    block_index = nak0 // 3
    row_index = nak0 % 3
    if block_index % 2 == 0:
        return savya_deha_rows[row_index][pada0]
    return apasavya_deha_rows[row_index][pada0]


# =============================================================================
# Pada-run context table, used by PVR_SANJAY_RATH.
# =============================================================================
def _kc_navamsa_of_pada(nak0, pada0):
    """ Kalachakra navamsa sign of a nakshatra pada, from const.kalachakra_navamsa. """
    return int(const.kalachakra_navamsa[nak0][pada0])
def _build_kc_child_context_table():
    """
    Maps each parent (kc_index, pada0) to the nine child (kc_index, pada0)
    contexts, one per entry of const.kalachakra_rasis[kc_index][pada0]. Every
    such row of nine rasis is the Kalachakra-navamsa image of nine
    consecutive nakshatra padas; child i's own context is the group and pada
    of the i-th pada in that run. The run is solved for here rather than
    hard-coded so the table stays in step with const.

    A run recurs every 24 padas and each copy yields identical child
    contexts, except where a copy overlaps the Revati/U.Bhadra tail
    (const.savya_stars_1 holds 9 nakshatras against savya_stars_2's 6, so
    the periodicity breaks there). Those 4 of 16 keys take the majority
    across copies.
    """
    table = {}
    for kc_index in range(4):
        for pada0 in range(4):
            target = list(const.kalachakra_rasis[kc_index][pada0])
            votes = {}
            for start in range(_PADAS_IN_ZODIAC):
                for step in (1, -1):
                    padas = [
                        (start + step * i) % _PADAS_IN_ZODIAC
                        for i in range(_PADAS_IN_BLOCK)
                    ]
                    signs = [_kc_navamsa_of_pada(p // 4, p % 4) for p in padas]
                    if signs == target:
                        key = tuple(
                            (_kc_group_for_nak(p // 4), p % 4) for p in padas
                        )
                        votes[key] = votes.get(key, 0) + 1
            if not votes:
                raise ValueError(
                    f"No Kalachakra pada run for (kc_index={kc_index}, "
                    f"pada0={pada0}); const.kalachakra_rasis and "
                    "const.kalachakra_navamsa are inconsistent."
                )
            best_key = max(votes.items(), key=lambda kv: kv[1])[0]
            table[(kc_index, pada0)] = [tuple(x) for x in best_key]
    return table
_KC_CHILD_CONTEXTS = _build_kc_child_context_table()


# =============================================================================
# Pada-walk helpers, used by RAGHAVACHARYA only.
# =============================================================================
def _sign_of_pada(pada):
    pada = int(pada) % _PADAS_IN_ZODIAC
    return _kc_navamsa_of_pada(pada // 4, pada % 4)
def _kc_child_padas(pada):
    """
    The nine child padas of a pada, as nine consecutive nakshatra padas.
    Block b means padas 9b..9b+8:
        savya    : b = pada % 12,       taken ascending
        apasavya : b = (7 - pada) % 12, taken descending when
                   (nakshatra // 6) is even, otherwise ascending
    The Kalachakra navamsas of the returned run are always exactly one
    const.kalachakra_rasis row.
    """
    pada = int(pada) % _PADAS_IN_ZODIAC
    nak0 = pada // 4
    if (nak0 // 3) % 2 == 0:
        block = pada % 12
        return [_PADAS_IN_BLOCK * block + i for i in range(_PADAS_IN_BLOCK)]
    block = (7 - pada) % 12
    if (nak0 // 6) % 2 == 0:
        return [_PADAS_IN_BLOCK * block + 8 - i for i in range(_PADAS_IN_BLOCK)]
    return [_PADAS_IN_BLOCK * block + i for i in range(_PADAS_IN_BLOCK)]
def _kc_child_padas_and_signs(pada):
    child_padas = _kc_child_padas(pada)
    return child_padas, [_sign_of_pada(p) for p in child_padas]
def _first_partial_ad_index(ad_years_full, elapsed_in_first_md):
    """
    Index of the AD running at birth. Mirrors the index selection inside
    _trim_first_partial_ads(), so the two stay aligned.
    """
    cumulative = []
    total = 0.0
    for years in ad_years_full:
        total += years
        cumulative.append(total)
    for i, cum_years in enumerate(cumulative):
        if elapsed_in_first_md < cum_years:
            return i
    return 0


# =============================================================================
# Mahadhasa builders. They receive an already-resolved
# dhasa_starting_planet_longitude, so divisional_chart_factor / chart_method /
# dhasa_starting_planet are handled once, in _build_md_data().
# =============================================================================
def _build_santhanam_md_sequence(
    jd,
    place,
    dhasa_starting_planet_longitude,
    from_birth,
    method,
):
    nak0, pada0, pada_fraction, reminder = _dhasa_starting_planet_pada_details_from_remainder(
        dhasa_starting_planet_longitude
    )
    kc_index = _kc_group_for_nak(nak0)
    cycle = list(const.kalachakra_rasis[kc_index][pada0])
    paramayush = float(const.kalachakra_paramayush[kc_index][pada0])
    full_md_years = _sign_years(cycle)
    elapsed_years = pada_fraction * paramayush
    running_md_index, elapsed_in_running_md = _find_running_md_index_from_elapsed(
        full_md_years,
        elapsed_years,
    )
    md_signs, md_years, md_kc_pada = _extend_md_sequence_from_running(
        cycle=cycle,
        full_md_years=full_md_years,
        running_md_index=running_md_index,
        kc_index=kc_index,
        pada0=pada0,
    )
    full_running_md_duration = full_md_years[running_md_index]
    if from_birth:
        if md_years:
            md_years[0] = md_years[0] - elapsed_in_running_md
        start_jd = float(jd)
        elapsed_in_first_md = elapsed_in_running_md
        first_md_is_partial = True
    else:
        fraction_elapsed = elapsed_in_running_md / full_running_md_duration
        fraction_elapsed = max(0.0, min(1.0, fraction_elapsed))
        start_jd = drik._get_dhasa_start_jd(
            jd_birth=float(jd),
            place=place,
            fraction_elapsed=fraction_elapsed,
            total_dasa_years=full_running_md_duration,
        )
        elapsed_in_first_md = 0.0
        first_md_is_partial = False
    return {
        "md_signs": md_signs,
        "md_years": md_years,
        "md_kc_pada": md_kc_pada,
        "start_jd": start_jd,
        "elapsed_in_first_md": elapsed_in_first_md,
        "first_md_is_partial": first_md_is_partial,
    }
def _build_navamsa_seed_md_sequence(
    jd,
    place,
    dhasa_starting_planet_longitude,
    from_birth,
    method,
):
    """ Used by BV_RAMAN and PVR_SANJAY_RATH. """
    (
        navamsa_rasi,
        nav_start_d1_longitude,
        nav_fraction,
        seed_longitude,
    ) = _navamsa_start_info_from_longitude(dhasa_starting_planet_longitude)
    seed_nak0, seed_pada0 = _nak_pada_from_longitude(dhasa_starting_planet_longitude)
    seed_kc_index = _kc_group_for_nak(seed_nak0)
    cycle = list(const.kalachakra_rasis[seed_kc_index][seed_pada0])
    full_md_years = _sign_years(cycle)
    running_md_index = 0
    first_md_duration = full_md_years[0]
    elapsed_in_running_md = nav_fraction * first_md_duration
    md_signs, md_years, md_kc_pada = _extend_md_sequence_from_running(
        cycle=cycle,
        full_md_years=full_md_years,
        running_md_index=running_md_index,
        kc_index=seed_kc_index,
        pada0=seed_pada0,
    )
    md_sr_ad_kc_pada = _build_progressive_kc_pada_list(
        seed_kc_index,
        seed_pada0,
    )
    if from_birth:
        if md_years:
            md_years[0] = md_years[0] - elapsed_in_running_md
        start_jd = float(jd)
        elapsed_in_first_md = elapsed_in_running_md
        first_md_is_partial = True
    else:
        fraction_elapsed = elapsed_in_running_md / first_md_duration
        fraction_elapsed = max(0.0, min(1.0, fraction_elapsed))
        start_jd = drik._get_dhasa_start_jd(
            jd_birth=float(jd),
            place=place,
            fraction_elapsed=fraction_elapsed,
            total_dasa_years=first_md_duration,
        )
        elapsed_in_first_md = 0.0
        first_md_is_partial = False
    return {
        "md_signs": md_signs,
        "md_years": md_years,
        "md_kc_pada": md_kc_pada,
        "md_sr_ad_kc_pada": md_sr_ad_kc_pada,
        "start_jd": start_jd,
        "elapsed_in_first_md": elapsed_in_first_md,
        "first_md_is_partial": first_md_is_partial,
    }
def _build_raghavacharya_md_sequence(
    jd,
    place,
    dhasa_starting_planet_longitude,
    from_birth,
    method,
):
    """
    Navamsa progression: the mahadasas are consecutive padas from
    dhasa_starting_planet's own pada, each mahadasa sign being that pada's
    Kalachakra navamsa. md_padas is used to descend below AD.
    """
    lon = dhasa_starting_planet_longitude % 360.0
    one_nav = 30.0 / 9.0
    rasi = int(lon // 30.0)
    offset = lon - rasi * 30.0
    nav_index = int(offset // one_nav)
    nav_start = rasi * 30.0 + nav_index * one_nav
    elapsed_in_nav = lon - nav_start
    frac_left = (one_nav - elapsed_in_nav) / one_nav
    frac_left = max(0.0, min(1.0, frac_left))
    md_nav_starts = [nav_start + i * one_nav for i in range(_MAHA_COUNT)]
    md_nak_pada = []
    md_signs = []
    md_kc_pada = []
    md_padas = []
    for nav_start_lon in md_nav_starts:
        nak0, pada0 = _nak_pada_from_longitude(nav_start_lon + 1e-9)
        kc_index = _kc_group_for_nak(nak0)
        md_nak_pada.append((nak0, pada0))
        md_kc_pada.append((kc_index, pada0))
        md_padas.append((nak0 * 4 + pada0) % _PADAS_IN_ZODIAC)
        md_signs.append(_deha_rasi_from_nak_pada(nak0, pada0))
    md_years = _sign_years(md_signs)
    first_full_md = md_years[0] if md_years else 0.0
    elapsed_in_running_md = first_full_md * (1.0 - frac_left)
    if from_birth:
        if md_years:
            md_years[0] = md_years[0] * frac_left
        start_jd = float(jd)
        elapsed_in_first_md = elapsed_in_running_md
        first_md_is_partial = True
    else:
        fraction_elapsed = elapsed_in_running_md / first_full_md
        fraction_elapsed = max(0.0, min(1.0, fraction_elapsed))
        start_jd = drik._get_dhasa_start_jd(
            jd_birth=float(jd),
            place=place,
            fraction_elapsed=fraction_elapsed,
            total_dasa_years=first_full_md,
        )
        elapsed_in_first_md = 0.0
        first_md_is_partial = False
    return {
        "md_signs": md_signs,
        "md_years": md_years,
        "md_nav_starts": md_nav_starts,
        "md_nak_pada": md_nak_pada,
        "md_kc_pada": md_kc_pada,
        "md_padas": md_padas,
        "start_jd": start_jd,
        "elapsed_in_first_md": elapsed_in_first_md,
        "first_md_is_partial": first_md_is_partial,
    }
def _build_sm_singh_md_sequence(
    jd,
    place,
    dhasa_starting_planet_longitude,
    from_birth,
    method,
):
    nak0, pada0, pada_fraction, reminder = _dhasa_starting_planet_pada_details_from_remainder(
        dhasa_starting_planet_longitude
    )
    kc_index = _kc_group_for_nak(nak0)
    cycle = list(const.kalachakra_rasis[kc_index][pada0])
    paramayush = float(const.kalachakra_paramayush[kc_index][pada0])
    full_md_years = _sign_years(cycle)
    elapsed_years = pada_fraction * paramayush
    running_md_index, elapsed_in_running_md = _find_running_md_index_from_elapsed(
        full_md_years,
        elapsed_years,
    )
    md_signs = []
    md_years = []
    md_cycle_indices = []
    md_sm_ad_kc_pada = []
    for j in range(_MAHA_COUNT):
        cycle_index = (running_md_index + j) % len(cycle)
        md_signs.append(int(cycle[cycle_index]))
        md_years.append(float(full_md_years[cycle_index]))
        md_cycle_indices.append(cycle_index)
        ad_kc, ad_pada = _kc_pada_after_steps(
            start_kc=kc_index,
            start_pada=pada0,
            steps=cycle_index,
        )
        md_sm_ad_kc_pada.append((ad_kc, ad_pada))
    full_running_md_duration = full_md_years[running_md_index]
    if from_birth:
        if md_years:
            md_years[0] = md_years[0] - elapsed_in_running_md
        start_jd = float(jd)
        elapsed_in_first_md = elapsed_in_running_md
        first_md_is_partial = True
    else:
        fraction_elapsed = elapsed_in_running_md / full_running_md_duration
        fraction_elapsed = max(0.0, min(1.0, fraction_elapsed))
        start_jd = drik._get_dhasa_start_jd(
            jd_birth=float(jd),
            place=place,
            fraction_elapsed=fraction_elapsed,
            total_dasa_years=full_running_md_duration,
        )
        elapsed_in_first_md = 0.0
        first_md_is_partial = False
    return {
        "md_signs": md_signs,
        "md_years": md_years,
        "md_cycle_indices": md_cycle_indices,
        "md_sm_ad_kc_pada": md_sm_ad_kc_pada,
        "start_jd": start_jd,
        "elapsed_in_first_md": elapsed_in_first_md,
        "first_md_is_partial": first_md_is_partial,
    }


# =============================================================================
# Antardhasa helpers.
# =============================================================================
def _ad_cycle_for_md_standard(md_sign, kc_index, pada0):
    base = list(const.kalachakra_rasis[kc_index][pada0])
    return _rotate_from(base, md_sign)
def _ad_cycle_for_md_raghavacharya(md_nav_start):
    """
    Retained for compatibility with callers still using the older lookup;
    the tree itself now uses _kc_child_padas() so each antardasa carries its
    own pada, returning the same nine signs.
    """
    nak0, pada0 = _nak_pada_from_longitude(md_nav_start + 1e-9)
    kc_index = _kc_group_for_nak(nak0)
    return list(const.kalachakra_rasis[kc_index][pada0])
def _trim_first_partial_ads(
    ad_signs,
    ad_years_full,
    elapsed_in_first_md,
    remaining_md,
):
    cumulative = []
    total = 0.0
    for years in ad_years_full:
        total += years
        cumulative.append(total)
    running_ad_index = 0
    for i, cum_years in enumerate(cumulative):
        if elapsed_in_first_md < cum_years:
            running_ad_index = i
            break
    elapsed_before_ad = 0.0
    if running_ad_index > 0:
        elapsed_before_ad = cumulative[running_ad_index - 1]
    elapsed_in_ad = elapsed_in_first_md - elapsed_before_ad
    ad_signs_use = ad_signs[running_ad_index:]
    ad_years_use = list(ad_years_full[running_ad_index:])
    if ad_years_use:
        ad_years_use[0] = ad_years_use[0] - elapsed_in_ad
    trimmed_signs = []
    trimmed_years = []
    acc = 0.0
    for ad_sign, ad_years in zip(ad_signs_use, ad_years_use):
        if acc >= remaining_md:
            break
        duration = min(ad_years, remaining_md - acc)
        if duration > 1e-10:
            trimmed_signs.append(ad_sign)
            trimmed_years.append(duration)
            acc += duration
    return trimmed_signs, trimmed_years
def _append_ad_rows_for_standard_md_data(place, md_data):
    """ Santhanam and BV Raman. AD rule: the MD's Kalachakra row, rotated from the MD sign. """
    rows = []
    md_signs = md_data["md_signs"]
    md_years = md_data["md_years"]
    md_kc_pada = md_data["md_kc_pada"]
    cursor_jd = md_data["start_jd"]
    elapsed_in_first_md = md_data["elapsed_in_first_md"]
    first_md_is_partial = md_data["first_md_is_partial"]
    for md_i, (md_sign, md_duration) in enumerate(zip(md_signs, md_years)):
        if md_duration <= 1e-10:
            continue
        kc_for_md, pada_for_md = md_kc_pada[md_i]
        ad_signs = _ad_cycle_for_md_standard(md_sign, kc_for_md, pada_for_md)
        full_md_duration = float(const.kalachakra_dhasa_duration[md_sign])
        ad_years_full = _proportional_split(full_md_duration, ad_signs)
        if md_i == 0 and first_md_is_partial and elapsed_in_first_md > 1e-10:
            ad_signs_use, ad_years_use = _trim_first_partial_ads(
                ad_signs,
                ad_years_full,
                elapsed_in_first_md,
                md_duration,
            )
        else:
            ad_signs_use = ad_signs
            ad_years_use = _proportional_split(md_duration, ad_signs_use)
        for ad_sign, ad_duration in zip(ad_signs_use, ad_years_use):
            if ad_duration <= 1e-10:
                continue
            rows.append(
                (
                    (int(md_sign), int(ad_sign)),
                    utils.jd_to_gregorian(cursor_jd),
                    float(ad_duration),
                )
            )
            cursor_jd = drik._get_dhasa_end_jd(
                start_jd=cursor_jd,
                place=place,
                total_dasa_years=ad_duration,
            )
    return rows
def _append_ad_rows_for_pvr_sanjay_rath_md_data(place, md_data):
    """ PVR/Sanjay Rath AD: progressive Kalachakra pada row for each MD. """
    rows = []
    md_signs = md_data["md_signs"]
    md_years = md_data["md_years"]
    md_sr_ad_kc_pada = md_data["md_sr_ad_kc_pada"]
    cursor_jd = md_data["start_jd"]
    elapsed_in_first_md = md_data["elapsed_in_first_md"]
    first_md_is_partial = md_data["first_md_is_partial"]
    for md_i, (md_sign, md_duration) in enumerate(zip(md_signs, md_years)):
        if md_duration <= 1e-10:
            continue
        kc_for_ad, pada_for_ad = md_sr_ad_kc_pada[md_i]
        ad_signs = list(const.kalachakra_rasis[kc_for_ad][pada_for_ad])
        full_md_duration = float(const.kalachakra_dhasa_duration[md_sign])
        ad_years_full = _proportional_split(full_md_duration, ad_signs)
        if md_i == 0 and first_md_is_partial and elapsed_in_first_md > 1e-10:
            ad_signs_use, ad_years_use = _trim_first_partial_ads(
                ad_signs,
                ad_years_full,
                elapsed_in_first_md,
                md_duration,
            )
        else:
            ad_signs_use = ad_signs
            ad_years_use = _proportional_split(md_duration, ad_signs_use)
        for ad_sign, ad_duration in zip(ad_signs_use, ad_years_use):
            if ad_duration <= 1e-10:
                continue
            rows.append(
                (
                    (int(md_sign), int(ad_sign)),
                    utils.jd_to_gregorian(cursor_jd),
                    float(ad_duration),
                )
            )
            cursor_jd = drik._get_dhasa_end_jd(
                start_jd=cursor_jd,
                place=place,
                total_dasa_years=ad_duration,
            )
    return rows
def _append_ad_rows_for_raghavacharya_md_data(place, md_data):
    """
    Raghavacharya AD: the Kalachakra navamsas of the MD pada's nine child
    padas -- the same nine signs and dates as the earlier
    _ad_cycle_for_md_raghavacharya() lookup. The child padas are recorded in
    md_data["ad_row_padas"], one per emitted row, so levels 3-6 can descend.
    """
    rows = []
    ad_row_padas = []
    md_signs = md_data["md_signs"]
    md_years = md_data["md_years"]
    md_padas = md_data["md_padas"]
    cursor_jd = md_data["start_jd"]
    elapsed_in_first_md = md_data["elapsed_in_first_md"]
    first_md_is_partial = md_data["first_md_is_partial"]
    for md_i, (md_sign, md_duration) in enumerate(zip(md_signs, md_years)):
        if md_duration <= 1e-10:
            continue
        child_padas, ad_signs = _kc_child_padas_and_signs(md_padas[md_i])
        full_md_duration = float(const.kalachakra_dhasa_duration[md_sign])
        ad_years_full = _proportional_split(full_md_duration, ad_signs)
        if md_i == 0 and first_md_is_partial and elapsed_in_first_md > 1e-10:
            ad_signs_use, ad_years_use = _trim_first_partial_ads(
                ad_signs,
                ad_years_full,
                elapsed_in_first_md,
                md_duration,
            )
            first_index = _first_partial_ad_index(ad_years_full, elapsed_in_first_md)
            ad_padas_use = child_padas[first_index: first_index + len(ad_signs_use)]
        else:
            ad_signs_use = ad_signs
            ad_years_use = _proportional_split(md_duration, ad_signs_use)
            ad_padas_use = list(child_padas)
        for ad_sign, ad_duration, ad_pada in zip(ad_signs_use, ad_years_use, ad_padas_use):
            if ad_duration <= 1e-10:
                continue
            rows.append(
                (
                    (int(md_sign), int(ad_sign)),
                    utils.jd_to_gregorian(cursor_jd),
                    float(ad_duration),
                )
            )
            ad_row_padas.append(int(ad_pada))
            cursor_jd = drik._get_dhasa_end_jd(
                start_jd=cursor_jd,
                place=place,
                total_dasa_years=ad_duration,
            )
    md_data["ad_row_padas"] = ad_row_padas
    return rows
def _append_ad_rows_for_sm_singh_md_data(place, md_data):
    rows = []
    md_signs = md_data["md_signs"]
    md_years = md_data["md_years"]
    md_sm_ad_kc_pada = md_data["md_sm_ad_kc_pada"]
    cursor_jd = md_data["start_jd"]
    elapsed_in_first_md = md_data["elapsed_in_first_md"]
    first_md_is_partial = md_data["first_md_is_partial"]
    for md_i, (md_sign, md_duration) in enumerate(zip(md_signs, md_years)):
        if md_duration <= 1e-10:
            continue
        kc_for_ad, pada_for_ad = md_sm_ad_kc_pada[md_i]
        ad_signs = list(const.kalachakra_rasis[kc_for_ad][pada_for_ad])
        full_md_duration = float(const.kalachakra_dhasa_duration[md_sign])
        ad_years_full = _proportional_split(full_md_duration, ad_signs)
        if md_i == 0 and first_md_is_partial and elapsed_in_first_md > 1e-10:
            ad_signs_use, ad_years_use = _trim_first_partial_ads(
                ad_signs,
                ad_years_full,
                elapsed_in_first_md,
                md_duration,
            )
        else:
            ad_signs_use = ad_signs
            ad_years_use = _proportional_split(md_duration, ad_signs_use)
        for ad_sign, ad_duration in zip(ad_signs_use, ad_years_use):
            if ad_duration <= 1e-10:
                continue
            rows.append(
                (
                    (int(md_sign), int(ad_sign)),
                    utils.jd_to_gregorian(cursor_jd),
                    float(ad_duration),
                )
            )
            cursor_jd = drik._get_dhasa_end_jd(
                start_jd=cursor_jd,
                place=place,
                total_dasa_years=ad_duration,
            )
    return rows


# =============================================================================
# Build MD/AD (levels 1-2) using the per-method (builder, appender) pair.
# =============================================================================
def _build_md_data(jd, place, method, from_birth,
                   divisional_chart_factor=1,
                   chart_method=1,
                   dhasa_starting_planet=const.MOON_ID,
                   ):
    dhasa_starting_planet_longitude = _get_dhasa_starting_planet_longitude(jd, place,
                    divisional_chart_factor=divisional_chart_factor,
                    chart_method=chart_method,
                    dhasa_starting_planet=dhasa_starting_planet,
                    )
    if method == const.KALACHAKRA_TYPE.SANTHANAM:
        return _build_santhanam_md_sequence(
            jd=jd, place=place, dhasa_starting_planet_longitude=dhasa_starting_planet_longitude,
            from_birth=from_birth, method=method,
        ), _append_ad_rows_for_standard_md_data
    if method == const.KALACHAKRA_TYPE.BV_RAMAN:
        return _build_navamsa_seed_md_sequence(
            jd=jd, place=place, dhasa_starting_planet_longitude=dhasa_starting_planet_longitude,
            from_birth=from_birth, method=method,
        ), _append_ad_rows_for_standard_md_data
    if method == const.KALACHAKRA_TYPE.PVR_SANJAY_RATH:
        return _build_navamsa_seed_md_sequence(
            jd=jd, place=place, dhasa_starting_planet_longitude=dhasa_starting_planet_longitude,
            from_birth=from_birth, method=method,
        ), _append_ad_rows_for_pvr_sanjay_rath_md_data
    if method == const.KALACHAKRA_TYPE.RAGHAVACHARYA:
        return _build_raghavacharya_md_sequence(
            jd=jd, place=place, dhasa_starting_planet_longitude=dhasa_starting_planet_longitude,
            from_birth=from_birth, method=method,
        ), _append_ad_rows_for_raghavacharya_md_data
    if method == const.KALACHAKRA_TYPE.SM_SINGH:
        return _build_sm_singh_md_sequence(
            jd=jd, place=place, dhasa_starting_planet_longitude=dhasa_starting_planet_longitude,
            from_birth=from_birth, method=method,
        ), _append_ad_rows_for_sm_singh_md_data
    raise ValueError(f"Unsupported Kalachakra method: {method}")


def _group_ad_rows_by_md(ad_rows):
    """
    Returns a list mapping each row in ad_rows to its md_i (index into the
    Mahadasa block sequence), by grouping consecutive rows that share the
    same MD sign -- the same grouping rule used by get_maha_from_antardhasa().
    """
    md_i_by_row = []
    current_md_i = -1
    last_md_sign = None
    for lords, _start_t, _dur in ad_rows:
        if lords[0] != last_md_sign:
            current_md_i += 1
            last_md_sign = lords[0]
        md_i_by_row.append(current_md_i)
    return md_i_by_row


def _get_kalachakra_children_jd(
    method,
    parent_path,
    parent_context,
    parent_start_jd,
    parent_duration,
    place,
    *,
    parent_end_jd=None,
    elapsed_in_parent=0.0,
):
    """
    Children-engine for levels 3+, all 5 methods.
    parent_context is the parent's own context:
        {"kc_index": ..., "pada0": ...}  SANTHANAM / BV_RAMAN /
                                         PVR_SANJAY_RATH / SM_SINGH
        {"pada": ...}                    RAGHAVACHARYA

    Child order and context per method:
        SANTHANAM/BV_RAMAN : order = _ad_cycle_for_md_standard() (rotate from
            the parent sign); context inherited unchanged.
        PVR_SANJAY_RATH    : order = const.kalachakra_rasis[kc][pada0]; child
            i's context = _KC_CHILD_CONTEXTS[(kc,pada0)][i].
        RAGHAVACHARYA      : order and contexts = _kc_child_padas(parent pada);
            child i's context is the i-th child pada.
        SM_SINGH           : order = const.kalachakra_rasis[kc][pada0]; child i's
            context = parent context advanced i _next_kc_pada() steps.

    Durations use _proportional_split(); a partial parent trims via
    _trim_first_partial_ads(). The last child's end is forced to parent_end_jd.
    If the smallest child duration is under _SUB_DAY_DURATION_DAYS, all
    boundaries are interpolated across the parent's real span instead of
    calling _bounded_end_jd() per child.

    Returns:
        children: list of (child_path, child_context, child_start_jd,
                           child_duration_years, child_end_jd)
        parent_end_jd: float JD
    """
    parent_sign = parent_path[-1]
    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)
    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd
    if method in (const.KALACHAKRA_TYPE.SANTHANAM, const.KALACHAKRA_TYPE.BV_RAMAN):
        kc_index = parent_context["kc_index"]
        pada0 = parent_context["pada0"]
        child_signs = _ad_cycle_for_md_standard(parent_sign, kc_index, pada0)
        child_contexts = [{"kc_index": kc_index, "pada0": pada0} for _ in child_signs]
    elif method == const.KALACHAKRA_TYPE.PVR_SANJAY_RATH:
        kc_index = parent_context["kc_index"]
        pada0 = parent_context["pada0"]
        child_signs = list(const.kalachakra_rasis[kc_index][pada0])
        child_contexts = [
            {"kc_index": g, "pada0": p}
            for (g, p) in _KC_CHILD_CONTEXTS[(kc_index, pada0)]
        ]
    elif method == const.KALACHAKRA_TYPE.RAGHAVACHARYA:
        parent_pada = int(parent_context["pada"])
        child_padas, child_signs = _kc_child_padas_and_signs(parent_pada)
        child_contexts = [{"pada": int(p)} for p in child_padas]
    elif method == const.KALACHAKRA_TYPE.SM_SINGH:
        kc_index = parent_context["kc_index"]
        pada0 = parent_context["pada0"]
        child_signs = list(const.kalachakra_rasis[kc_index][pada0])
        child_contexts = []
        cur_kc, cur_pada = kc_index, pada0
        for _ in child_signs:
            child_contexts.append({"kc_index": cur_kc, "pada0": cur_pada})
            cur_kc, cur_pada = _next_kc_pada(cur_kc, cur_pada)
    else:
        raise ValueError(f"Unsupported Kalachakra method: {method}")
    if not child_signs:
        return [], parent_end_jd
    full_parent_duration = float(const.kalachakra_dhasa_duration[parent_sign])
    raw_child_years = _proportional_split(full_parent_duration, child_signs)
    if elapsed_in_parent > 1e-10:
        signs_use, years_use = _trim_first_partial_ads(
            child_signs,
            raw_child_years,
            elapsed_in_parent,
            parent_duration,
        )
        first_index = _first_partial_ad_index(raw_child_years, elapsed_in_parent)
        contexts_use = child_contexts[first_index: first_index + len(signs_use)]
    else:
        signs_use = child_signs
        contexts_use = child_contexts
        years_use = _proportional_split(parent_duration, signs_use)
    n = len(signs_use)
    if n == 0:
        return [], parent_end_jd
    smallest_child_years = min(years_use)
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(years_use)
    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0
    for i, (child_sign, child_context) in enumerate(zip(signs_use, contexts_use)):
        child_duration = years_use[i]
        child_start_jd = cursor
        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_duration += child_duration
            child_end_jd = parent_start_jd + parent_span * cumulative_duration / total_child_duration
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)
        children.append(
            (
                parent_path + (child_sign,),
                child_context,
                child_start_jd,
                child_duration,
                child_end_jd,
            )
        )
        cursor = child_end_jd
    return children, parent_end_jd
def _find_child_containing_jd(children, target_jd):
    if not children:
        return None
    for child in children:
        _, _, s, _, e = child
        if s <= target_jd < e:
            return child
    return children[-1]
def _ad_context_for_row(method, md_data, md_sign, ad_sign, md_i, row_index=None):
    """
    The AD's own context, used to start the level 3+ recursion.
    SANTHANAM/BV_RAMAN : inherited unchanged from the parent MD.
    PVR_SANJAY_RATH    : the AD sign is an entry in the MD's own antara row, so
        its context is _KC_CHILD_CONTEXTS[MD context][position of ad_sign].
    RAGHAVACHARYA      : the AD's own pada, recorded per row by
        _append_ad_rows_for_raghavacharya_md_data().
    SM_SINGH           : the MD's context stepped by the AD sign's position in
        the MD's own row.
    """
    if method in (const.KALACHAKRA_TYPE.SANTHANAM, const.KALACHAKRA_TYPE.BV_RAMAN):
        kc_index, pada0 = md_data["md_kc_pada"][md_i]
        return {"kc_index": kc_index, "pada0": pada0}
    if method == const.KALACHAKRA_TYPE.PVR_SANJAY_RATH:
        md_kc_index, md_pada0 = md_data["md_sr_ad_kc_pada"][md_i]
        md_own_row = list(const.kalachakra_rasis[md_kc_index][md_pada0])
        ad_position = md_own_row.index(int(ad_sign)) if int(ad_sign) in md_own_row else 0
        ad_kc_index, ad_pada0 = _KC_CHILD_CONTEXTS[(md_kc_index, md_pada0)][ad_position]
        return {"kc_index": ad_kc_index, "pada0": ad_pada0}
    if method == const.KALACHAKRA_TYPE.RAGHAVACHARYA:
        ad_row_padas = md_data.get("ad_row_padas") or []
        if row_index is not None and 0 <= row_index < len(ad_row_padas):
            return {"pada": int(ad_row_padas[row_index])}
        md_pada = md_data["md_padas"][md_i]
        child_padas, child_signs = _kc_child_padas_and_signs(md_pada)
        if int(ad_sign) in child_signs:
            return {"pada": int(child_padas[child_signs.index(int(ad_sign))])}
        return {"pada": int(md_pada)}
    if method == const.KALACHAKRA_TYPE.SM_SINGH:
        md_kc_index, md_pada0 = md_data["md_sm_ad_kc_pada"][md_i]
        md_own_row = list(const.kalachakra_rasis[md_kc_index][md_pada0])
        ad_position = md_own_row.index(int(ad_sign)) if int(ad_sign) in md_own_row else 0
        ad_kc_index, ad_pada0 = _kc_pada_after_steps(md_kc_index, md_pada0, ad_position)
        return {"kc_index": ad_kc_index, "pada0": ad_pada0}
    raise ValueError(f"Unsupported Kalachakra method: {method}")


# =============================================================================
# Public API
# =============================================================================
def get_dhasa_antardhasa(
    dob, tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_starting_planet=const.MOON_ID,
    dhasa_method=None,
    from_birth=False,
    round_duration=True,
    return_exact_bounds=False,
):
    """
    Kalachakra Dasha, depth-enabled.

    Returns rows at the requested depth:
        [ (lords_tuple, start_date_tuple, duration_years), ... ]
    If return_exact_bounds=True, rows are instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]

    dhasa_level_index selects how deep to compute: 1=Maha, 2=Antara
    (default), 3=Pratyantara, 4=Sookshma, 5=Praana, 6=Deha. Levels 1-2 come
    directly from the method's own (builder, appender) pair; levels 3+ are
    generated by recursively applying _get_kalachakra_children_jd(), the
    same engine used by get_immediate_children() and
    get_running_dhasa_for_given_date().

    dhasa_method:
        const.KALACHAKRA_TYPE.SANTHANAM
        const.KALACHAKRA_TYPE.BV_RAMAN
        const.KALACHAKRA_TYPE.PVR_SANJAY_RATH
        const.KALACHAKRA_TYPE.RAGHAVACHARYA
        const.KALACHAKRA_TYPE.SM_SINGH
    If dhasa_method is None or invalid, const.KALACHAKRA_TYPE_DEFAULT is used.
    """
    if isinstance(dhasa_method, const.KALACHAKRA_TYPE):
        method = dhasa_method
    else:
        method = const.KALACHAKRA_TYPE_DEFAULT
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    md_data, appender = _build_md_data(
        jd_at_dob, place, method, from_birth,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        maha_rows = get_maha_from_antardhasa(appender(place, md_data))
        if return_exact_bounds:
            rows = []
            for md, start_t, duration in maha_rows:
                start_jd = _tuple_to_jd(start_t)
                end_jd = _bounded_end_jd(start_jd, duration, place)
                rows.append(((md,), start_jd, end_jd, duration))
            return rows
        return [((md,), start_t, duration) for md, start_t, duration in maha_rows]

    ad_rows = appender(place, md_data)

    if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
        if return_exact_bounds:
            rows = []
            for lords, start_t, duration in ad_rows:
                start_jd = _tuple_to_jd(start_t)
                end_jd = _bounded_end_jd(start_jd, duration, place)
                rows.append((lords, start_jd, end_jd, duration))
            return rows
        return ad_rows

    md_i_by_row = _group_ad_rows_by_md(ad_rows)
    rows = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            rows.append((lords_tuple, start_jd_local, end_jd_local, duration_years))
        else:
            start_str = utils.jd_to_gregorian(start_jd_local)
            dur_ret = round(duration_years, dhasa_level_index + 1) if round_duration else duration_years
            rows.append((lords_tuple, start_str, dur_ret))

    def _recurse(level, parent_path, parent_context, parent_start_jd, parent_duration, parent_end_jd):
        children, _ = _get_kalachakra_children_jd(
            method, parent_path, parent_context, parent_start_jd, parent_duration, place,
            parent_end_jd=parent_end_jd,
        )
        if not children:
            return
        for child_path, child_context, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(level + 1, child_path, child_context, child_start_jd, child_duration, child_end_jd)
            else:
                _emit_row(child_path, child_start_jd, child_duration, child_end_jd)

    pratyantara_level = const.MAHA_DHASA_DEPTH.ANTARA + 1
    for row_index, (lords, start_t, duration) in enumerate(ad_rows):
        md_sign, ad_sign = lords
        md_i = md_i_by_row[row_index]
        ad_start_jd = _tuple_to_jd(start_t)
        parent_context = _ad_context_for_row(method, md_data, md_sign, ad_sign, md_i, row_index=row_index)
        _recurse(pratyantara_level, lords, parent_context, ad_start_jd, duration, None)

    return rows


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_starting_planet=const.MOON_ID,
    dhasa_method=None,
    from_birth=False,
    elapsed_in_parent=0.0,
    **kwargs,
):
    """
    Kalachakra -- returns the immediate children of ANY node, at any depth.

    parent_lords length 1 (a Maha Dasa sign): returns that Maha Dasa's own
    Antardasa rows, read directly from the same (builder, appender) pair
    get_dhasa_antardhasa() itself uses -- there is no restriction here; no
    separate call to get_dhasa_antardhasa() is required by the caller.

    parent_lords length >= 2 (Antara or deeper): the node's own context
    (which nakshatra-pada group/pada, or Raghavacharya pada, it belongs to)
    is reconstructed internally from parent_lords -- the Maha/Antara table
    is rebuilt to locate the Antara this path starts from and that Antara's
    own context, then, if parent_lords goes deeper than Antara, each further
    sign in parent_lords is walked one step at a time via
    _get_kalachakra_children_jd(), since the exact child sign at each step
    is already known from parent_lords itself.
    """
    if isinstance(dhasa_method, const.KALACHAKRA_TYPE):
        method = dhasa_method
    else:
        method = const.KALACHAKRA_TYPE_DEFAULT
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")

    md_data, appender = _build_md_data(
        jd_at_dob, place, method, from_birth,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_starting_planet=dhasa_starting_planet,
    )
    ad_rows = appender(place, md_data)

    if len(path) == 1:
        md_sign = path[0]
        matched = [row for row in ad_rows if row[0][0] == md_sign]
        result = []
        for i, (lords, start_t, duration) in enumerate(matched):
            start_jd_local = _tuple_to_jd(start_t)
            if i + 1 < len(matched):
                end_jd_local = _tuple_to_jd(matched[i + 1][1])
            else:
                end_jd_local = _bounded_end_jd(start_jd_local, duration, place)
            result.append([lords, start_t, utils.jd_to_gregorian(end_jd_local)])
        return result

    md_i_by_row = _group_ad_rows_by_md(ad_rows)
    ad_row_index = next((i for i, (lords, _s, _d) in enumerate(ad_rows) if lords == path[:2]), None)
    if ad_row_index is None:
        raise ValueError(f"Could not locate Antara row for path {path[:2]}")
    md_i = md_i_by_row[ad_row_index]
    parent_context = _ad_context_for_row(method, md_data, path[0], path[1], md_i, row_index=ad_row_index)

    walked_path = path[:2]
    for level in range(2, len(path)):
        children, _ = _get_kalachakra_children_jd(
            method, walked_path, parent_context, jd_at_dob, 1.0, place, parent_end_jd=None,
        )
        target_sign = path[level]
        match = next((c for c in children if c[0][-1] == target_sign), None)
        if match is None:
            raise ValueError(f"Could not resolve child sign {target_sign} at level {level + 1} for path {path}")
        _child_path, parent_context, _s, _d, _e = match
        walked_path = walked_path + (target_sign,)

    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    children, _ = _get_kalachakra_children_jd(
        method, path, parent_context, start_jd, parent_years, place,
        parent_end_jd=end_jd, elapsed_in_parent=elapsed_in_parent,
    )
    return [
        [child_path, _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)]
        for child_path, _child_context, child_start_jd, _child_duration, child_end_jd in children
    ]


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_starting_planet=const.MOON_ID,
    dhasa_method=None,
    from_birth=False,
    **kwargs,
):
    """
    Kalachakra -- narrows Maha -> ... -> target depth and returns the full
    running ladder.

    Levels 1-2 scan the AD rows from the per-method (builder, appender)
    pair. Levels 3-6 use _get_kalachakra_children_jd(), bootstrapped via
    _ad_context_for_row().

    divisional_chart_factor, chart_method and dhasa_starting_planet are
    keyword-only so that existing positional calls passing dhasa_level_index
    as the 4th argument keep working.

    Returns:
        [
            [(l1,),              start1, end1],
            [(l1,l2),            start2, end2],
            [(l1,l2,l3),         start3, end3],
            [(l1,l2,l3,l4),      start4, end4],
            [(l1,l2,l3,l4,l5),   start5, end5],
            [(l1,l2,l3,l4,l5,l6),start6, end6],
        ]
    """
    global year_duration
    if isinstance(dhasa_method, const.KALACHAKRA_TYPE):
        method = dhasa_method
    else:
        method = const.KALACHAKRA_TYPE_DEFAULT
    year_duration = drik.dhasa_year_duration(jd=jd_at_dob, place=place)

    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))
    target_depth = _normalize_depth(dhasa_level_index)

    md_data, appender = _build_md_data(jd_at_dob, place, method, from_birth,
                divisional_chart_factor=divisional_chart_factor,
                chart_method=chart_method,
                dhasa_starting_planet=dhasa_starting_planet,
                                       )
    ad_rows = appender(place, md_data)
    found_ad = None
    for row_index, (lords, start_t, duration) in enumerate(ad_rows):
        start_jd_local = _tuple_to_jd(start_t)
        end_jd_local = _bounded_end_jd(start_jd_local, duration, place)
        if start_jd_local <= current_jd < end_jd_local:
            found_ad = (lords, start_jd_local, duration, end_jd_local, row_index)
            break
    if found_ad is None and ad_rows:
        row_index = len(ad_rows) - 1
        lords, start_t, duration = ad_rows[row_index]
        start_jd_local = _tuple_to_jd(start_t)
        end_jd_local = _bounded_end_jd(start_jd_local, duration, place)
        found_ad = (lords, start_jd_local, duration, end_jd_local, row_index)
    if found_ad is None:
        return []
    (md_sign, ad_sign), ad_start_jd, ad_duration, ad_end_jd, ad_row_index = found_ad
    maha_rows = get_maha_from_antardhasa(ad_rows)
    md_start_jd = md_end_jd = None
    for md, start_t, duration in maha_rows:
        if md == md_sign:
            s_jd = _tuple_to_jd(start_t)
            e_jd = _bounded_end_jd(s_jd, duration, place)
            if s_jd <= ad_start_jd < e_jd or (md_start_jd is None):
                md_start_jd, md_end_jd = s_jd, e_jd
                if s_jd <= ad_start_jd < e_jd:
                    break
    running_all = [[(md_sign,), utils.jd_to_gregorian(md_start_jd), utils.jd_to_gregorian(md_end_jd)]]
    if target_depth == 1:
        return running_all
    running_all.append([(md_sign, ad_sign), utils.jd_to_gregorian(ad_start_jd), utils.jd_to_gregorian(ad_end_jd)])
    if target_depth == 2:
        return running_all
    md_signs = md_data["md_signs"]
    md_i = 0
    for k, s in enumerate(md_signs):
        if s == md_sign:
            md_i = k
            break
    parent_context = _ad_context_for_row(
        method, md_data, md_sign, ad_sign, md_i, row_index=ad_row_index
    )
    parent_path = (md_sign, ad_sign)
    parent_start_jd = ad_start_jd
    parent_end_jd = ad_end_jd
    parent_duration_years = ad_duration
    for _depth in range(3, target_depth + 1):
        children, _ = _get_kalachakra_children_jd(
            method, parent_path, parent_context, parent_start_jd, parent_duration_years,
            place, parent_end_jd=parent_end_jd,
        )
        found = _find_child_containing_jd(children, current_jd)
        if found is None:
            running_all.append(
                [parent_path + (parent_path[-1],), utils.jd_to_gregorian(parent_start_jd), utils.jd_to_gregorian(parent_end_jd)]
            )
            break
        child_path, child_context, child_start_jd, child_duration_years, child_end_jd = found
        running_all.append([child_path, utils.jd_to_gregorian(child_start_jd), utils.jd_to_gregorian(child_end_jd)])
        parent_path = child_path
        parent_context = child_context
        parent_start_jd = child_start_jd
        parent_end_jd = child_end_jd
        parent_duration_years = child_duration_years
    return running_all


def get_maha_from_antardhasa(ad_rows):
    maha_rows = []
    current_md = None
    current_start = None
    current_duration = 0.0
    for lords, start, duration in ad_rows:
        md, ad = lords
        if current_md is None:
            current_md = md
            current_start = start
            current_duration = duration
            continue
        if md == current_md:
            current_duration += duration
        else:
            maha_rows.append(
                (
                    int(current_md),
                    current_start,
                    float(current_duration),
                )
            )
            current_md = md
            current_start = start
            current_duration = duration
    if current_md is not None:
        maha_rows.append(
            (
                int(current_md),
                current_start,
                float(current_duration),
            )
        )
    return maha_rows
def print_maha_from_antardhasa(ad_rows):
    maha_rows = get_maha_from_antardhasa(ad_rows)
    for md, start, duration in maha_rows:
        y, m, d, fh = start
        print(utils.RAASI_SHORT_LIST[md], (y, m, d), utils.to_dms(fh), duration)


if __name__ == "__main__":
    utils.set_language("en")
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place(
        "Chennai,India",
        13.03862,
        80.261818,
        5.5,
    )
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    dcf = 1
    dsp = const.MOON_ID
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    for method in [
        const.KALACHAKRA_TYPE.SANTHANAM,
        const.KALACHAKRA_TYPE.BV_RAMAN,
        const.KALACHAKRA_TYPE.PVR_SANJAY_RATH,
        const.KALACHAKRA_TYPE.RAGHAVACHARYA,
        const.KALACHAKRA_TYPE.SM_SINGH,
    ]:
        print("\n" + "=" * 80)
        print("METHOD:", method.name, method.value)
        print("=" * 80)

        ad = get_dhasa_antardhasa(dob, tob, place, dhasa_method=method, from_birth=False,
                                   divisional_chart_factor=dcf,
                                   dhasa_starting_planet=dsp)
        print("\nMaha Dasas:")
        print_maha_from_antardhasa(ad)

        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=method, divisional_chart_factor=dcf, dhasa_starting_planet=dsp,
        )
        print("\nRunning ladder (all 6 levels), via get_running_dhasa_for_given_date:")
        for lords, start, end in grd:
            lord_str = [utils.RAASI_SHORT_LIST[lord] for lord in lords]
            start_str = f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])}"
            end_str = f"{end[0]}-{end[1]}-{end[2]} {utils.to_dms(end[3])}"
            print(lord_str, start_str, end_str)

        deep = get_dhasa_antardhasa(dob, tob, place, dhasa_method=method, from_birth=False,
                                     divisional_chart_factor=dcf,
                                     dhasa_starting_planet=dsp,
                                     dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                                     return_exact_bounds=True)
        deha_row = None
        for lords, start_jd, end_jd, duration in deep:
            if start_jd <= current_jd < end_jd:
                deha_row = (lords, start_jd, end_jd)
                break
        if deha_row is None and deep:
            deha_row = deep[-1][0], deep[-1][1], deep[-1][2]
        print("\nDeha row containing the check date, via get_dhasa_antardhasa(dhasa_level_index=DEHA):")
        if deha_row:
            lords, start_jd, end_jd = deha_row
            lord_str = [utils.RAASI_SHORT_LIST[lord] for lord in lords]
            y1, m1, d1, fh1 = utils.jd_to_gregorian(start_jd)
            y2, m2, d2, fh2 = utils.jd_to_gregorian(end_jd)
            print(lord_str, f"{y1}-{m1}-{d1} {utils.to_dms(fh1)}", f"{y2}-{m2}-{d2} {utils.to_dms(fh2)}")

        immediate_from_md = get_immediate_children(
            grd[0][0], grd[0][1], parent_end=grd[0][2],
            jd_at_dob=jd_at_dob, place=place, dhasa_method=method,
            divisional_chart_factor=dcf, dhasa_starting_planet=dsp,
        )
        print("\nImmediate children of the running Maha Dasa (length-1 parent_lords), via get_immediate_children:")
        for lords, start, end in immediate_from_md:
            lord_str = [utils.RAASI_SHORT_LIST[lord] for lord in lords]
            print(lord_str, start, end)

        immediate = get_immediate_children(
            grd[-2][0], grd[-2][1], parent_end=grd[-2][2],
            jd_at_dob=jd_at_dob, place=place, dhasa_method=method,
            divisional_chart_factor=dcf, dhasa_starting_planet=dsp,
        )
        print("\nImmediate children of the second-to-last running level, via get_immediate_children:")
        for lords, start, end in immediate:
            lord_str = [utils.RAASI_SHORT_LIST[lord] for lord in lords]
            print(lord_str, start, end)
    exit()
