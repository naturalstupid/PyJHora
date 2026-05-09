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
from jhora.horoscope.chart import charts
""" TODO: Dhasa Progression does not seem to match with JHora """
# -*- coding: utf-8 -*-
"""
Kalachakra Daśā (L1..L6) with method switch:
  1 = PVR/book table logic (Moon-pāda KCD wheel) + proportional split at L2+
  2 = Sanjay Rath style cycle rotation (same as 1 here; hook for future gati nuances)
  3 = Rāghavācārya (JHora): L1 by navāṁśa progression; L2 by 9 pādas (via KCD tables)
"""

year_duration = const.sidereal_year


# -----------------------------
# Small internal helpers only
# -----------------------------
def _cycle_for(kc_index, paadham):
    """Return the 9-sign cycle (list of sign indices) for a given (group, pāda)."""
    return list(const.kalachakra_rasis[kc_index][paadham])


def _rotate(lst, k):
    n = len(lst)
    if n == 0:
        return lst
    k %= n
    return lst[k:] + lst[:k]


def _rotate_cycle_from_sign(cycle, start_sign):
    return _rotate(cycle, cycle.index(start_sign)) if start_sign in cycle else cycle[:]


def _sign_year_weights(signs):
    return [float(const.kalachakra_dhasa_duration[s]) for s in signs]


def _scaled_child_years_proportional(parent_years, weights):
    total = sum(weights) or 1.0
    return [parent_years * (w / total) for w in weights]


# ---------- method-specific L2 (re-used for deeper levels) ----------
def _antardhasa_pvr(parent_sign, kc_index, paadham, parent_years):
    cyc = _rotate_cycle_from_sign(_cycle_for(kc_index, paadham), parent_sign)
    yrs = _scaled_child_years_proportional(parent_years, _sign_year_weights(cyc))
    return cyc, yrs


def _antardhasa_rath(parent_sign, kc_index, paadham, parent_years):
    cyc = _rotate_cycle_from_sign(_cycle_for(kc_index, paadham), parent_sign)
    yrs = _scaled_child_years_proportional(parent_years, _sign_year_weights(cyc))
    return cyc, yrs


# --- NAVĀṂŚA helpers for method=3 (Rāghavācārya) ---
_NAVAMSA_SPAN = 360.0 / 108.0


def _navamsa_rasi_from_longitude(lon_deg):
    lon = float(lon_deg) % 360.0
    rasi = int(lon // 30.0)
    off = lon - (rasi * 30.0)
    n = int(off // (30.0 / 9.0))

    if rasi in (0, 3, 6, 9):
        start = rasi
    elif rasi in (1, 4, 7, 10):
        start = (rasi + 8) % 12
    else:
        start = (rasi + 4) % 12

    return (start + n) % 12


def _fraction_left_in_current_navamsa(lon_deg):
    lon = float(lon_deg) % 360.0
    x = lon % 30.0
    span = 30.0 / 9.0
    i = int(x // span)
    end = (i + 1) * span
    left = end - x
    return max(0.0, min(1.0, left / span))


# --- method=3 AD builder (corrected) ---
def _padas_in_sign_desc(sign_idx):
    start = sign_idx * 30.0
    mids = [start + (8 - i + 0.5) * _NAVAMSA_SPAN for i in range(9)]
    out = []
    for L in mids:
        nak, paa, _ = drik.nakshatra_pada(L)
        out.append((nak - 1, paa - 1))
    return out


# --- helper: find kc-group for a nakshatra index (0..26) ---
def _kc_group_for_nak(nak_index):
    if nak_index in const.savya_stars_1:
        return 0
    elif nak_index in const.savya_stars_2:
        return 1
    elif nak_index in const.apasavya_stars_1:
        return 2
    else:
        return 3


# --- method=3 AD builder (correct JHora/Rāghavācārya logic) ---
def _antardhasa_raghavacharya_for_md_navamsa(md_nav_start_lon, md_years):
    nak, paa, _ = drik.nakshatra_pada(md_nav_start_lon + 1e-9)
    nak_i, paa_i = nak - 1, paa - 1
    kc = _kc_group_for_nak(nak_i)

    ad_signs = list(const.kalachakra_rasis[kc][paa_i])
    weights = _sign_year_weights(ad_signs)
    ad_years = _scaled_child_years_proportional(md_years, weights)
    return ad_signs, ad_years


# --- ascending pādas inside a sign (0°→30°) ---
def _padas_in_sign_asc(sign_idx):
    start = sign_idx * 30.0
    mids = [start + (i + 0.5) * _NAVAMSA_SPAN for i in range(9)]
    out = []
    for L in mids:
        nak, paa, _ = drik.nakshatra_pada(L)
        out.append((nak - 1, paa - 1))
    return out


def _antardhasa_raghavacharya_by_padas(md_sign, md_years):
    ad_signs = []
    for nak_i, paa_i in _padas_in_sign_asc(md_sign):
        kc = _kc_group_for_nak(nak_i)
        cycle = const.kalachakra_rasis[kc][paa_i]
        ad_signs.append(int(cycle[0]))

    weights = _sign_year_weights(ad_signs)
    ad_years = _scaled_child_years_proportional(md_years, weights)
    return ad_signs, ad_years


# ---------------------------------------------------------------
# L1 progression builder with birth balance and method hooks
# ---------------------------------------------------------------
def _get_dhasa_progression(planet_longitude, dhasa_method=const.KALACHAKRA_TYPE.PVR_BOOK):
    """
    Build the Mahā sequence and, for each Mahā, attach L2 payload according to method.
    Returns: list of [md_sign, (bhut_rasis, bhut_years, kc_i, pa_i), md_years]
    """
    if dhasa_method == const.KALACHAKRA_TYPE.RAGHAVACHARYA:
        lon0 = float(planet_longitude) % 360.0
        frac_left = _fraction_left_in_current_navamsa(lon0)

        rasi = int(lon0 // 30.0)
        off = lon0 - (rasi * 30.0)
        span = 30.0 / 9.0
        i0 = int(off // span)
        start_of_nav = (rasi * 30.0) + i0 * span

        md_nav_starts = [start_of_nav + k * _NAVAMSA_SPAN for k in range(9)]
        md_signs = [_navamsa_rasi_from_longitude(L + 1e-9) for L in md_nav_starts]
        md_durs = [float(const.kalachakra_dhasa_duration[s]) for s in md_signs]
        if md_durs:
            md_durs[0] = md_durs[0] * frac_left

        nak_b, paa_b, _ = drik.nakshatra_pada(planet_longitude)
        nak_b -= 1
        paa_b -= 1
        kc_birth = _kc_group_for_nak(nak_b)

        dhasa_periods = []
        for md_sign, md_start, md_years in zip(md_signs, md_nav_starts, md_durs):
            ad_signs, ad_years = _antardhasa_raghavacharya_for_md_navamsa(md_start, md_years)
            dhasa_periods.append([md_sign, (ad_signs, ad_years, kc_birth, paa_b), md_years])
        return dhasa_periods

    nakshatra, paadham, _ = drik.nakshatra_pada(planet_longitude)
    nakshatra -= 1
    paadham -= 1

    kalachakra_index = _kc_group_for_nak(nakshatra)

    cycle0 = _cycle_for(kalachakra_index, paadham)
    param0 = float(const.kalachakra_paramayush[kalachakra_index][paadham])
    dur0 = _sign_year_weights(cycle0)

    one_star = 360.0 / 27.0
    one_paadha = 360.0 / 108.0
    nak_start_long = nakshatra * one_star + paadham * one_paadha
    nak_frac = (planet_longitude - nak_start_long) / one_paadha

    dur0_cum, acc = [], 0.0
    for v in dur0:
        acc += v
        dur0_cum.append(acc)

    completed = nak_frac * param0
    idx_at_birth = next(i for i, s in enumerate(dur0_cum) if s > completed)
    md_remaining = float(dur0_cum[idx_at_birth] - completed)

    kc_next = kalachakra_index
    pa_next = (paadham + 1) % 4
    if paadham == 3:
        kc_next = {0: 1, 1: 0, 2: 3, 3: 2}[kalachakra_index]

    cycle1 = _cycle_for(kc_next, pa_next)

    md_progression = cycle0[idx_at_birth:] + cycle1[:idx_at_birth]
    md_durations = _sign_year_weights(md_progression)
    md_durations[0] = md_remaining

    split_at = len(cycle0) - idx_at_birth

    if dhasa_method == const.KALACHAKRA_TYPE.PVR_BOOK:
        _children = _antardhasa_pvr
    else:
        _children = _antardhasa_rath

    dhasa_periods = []
    for i, md_sign in enumerate(md_progression):
        md_years = md_durations[i]
        if i < split_at:
            kc_i, pa_i = kalachakra_index, paadham
        else:
            kc_i, pa_i = kc_next, pa_next

        bhut_rasis, bhut_years = _children(md_sign, kc_i, pa_i, md_years)
        dhasa_periods.append([md_sign, (bhut_rasis, bhut_years, kc_i, pa_i), md_years])

    return dhasa_periods


# ---------------------------------------------------------
# Public KCD function with depth (L1..L6) & method switch
# ---------------------------------------------------------
def kalachakra_dhasa(
    planet_longitude,
    jd,
    dhasa_level_index=2,
    round_duration=True,
    dhasa_method=const.KALACHAKRA_TYPE.PVR_BOOK,
    dhasa_duration_type=None,
    savana_year_method=None,
    place=None,
    **kwargs,
):
    """
    Returns rows shaped as: [ ((lords...), start_str, dur_years), ... ]
    """
    global year_duration

    if place is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

    depth = int(dhasa_level_index)
    if not (1 <= depth <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")

    dhasa_periods = _get_dhasa_progression(planet_longitude, dhasa_method=dhasa_method)
    if not dhasa_periods:
        return []

    rows = []
    jd_ptr_md = float(jd)

    if dhasa_method == const.KALACHAKRA_TYPE.PVR_BOOK:
        _children = _antardhasa_pvr
    elif dhasa_method == const.KALACHAKRA_TYPE.SANJAY_RATH:
        _children = _antardhasa_rath
    elif dhasa_method == const.KALACHAKRA_TYPE.RAGHAVACHARYA:
        _children = _antardhasa_pvr
    else:
        _children = _antardhasa_pvr

    for md_sign, l2_payload, md_years in dhasa_periods:
        bhut_rasis, bhut_years, kc_i, pa_i = l2_payload

        if depth == 1:
            start_str = utils.jd_to_gregorian(jd_ptr_md)
            dur_ret = round(md_years, depth + 1) if round_duration else md_years
            rows.append(((md_sign,), start_str, float(dur_ret)))
            jd_ptr_md += md_years * year_duration
            continue

        jd_ptr_l2 = jd_ptr_md
        if depth == 2:
            for blord, byears in zip(bhut_rasis, bhut_years):
                start_str = utils.jd_to_gregorian(jd_ptr_l2)
                dur_ret = round(byears, depth + 1) if round_duration else byears
                rows.append(((md_sign, blord), start_str, float(dur_ret)))
                jd_ptr_l2 += byears * year_duration
            jd_ptr_md = jd_ptr_l2
            continue

        def _recurse(prefix_lords, start_jd, parent_years, kc_for_node, pa_for_node):
            current_level = len(prefix_lords)
            if current_level == depth:
                start_str = utils.jd_to_gregorian(start_jd)
                dur_ret = round(parent_years, depth + 1) if round_duration else parent_years
                rows.append((tuple(prefix_lords), start_str, float(dur_ret)))
                return start_jd + parent_years * year_duration

            child_signs, child_years = _children(prefix_lords[-1], kc_for_node, pa_for_node, parent_years)

            jd_ptr = start_jd
            for cs, cy in zip(child_signs, child_years):
                jd_ptr = _recurse(prefix_lords + [cs], jd_ptr, cy, kc_for_node, pa_for_node)
            return jd_ptr

        jd_ptr_after_md = jd_ptr_l2
        for blord, byears in zip(bhut_rasis, bhut_years):
            jd_ptr_after_md = _recurse([md_sign, blord], jd_ptr_after_md, byears, kc_i, pa_i)

        jd_ptr_md = jd_ptr_after_md

    return rows


# ---------------------------------------------------------
# Public router (seed selection + dasha call)
# ---------------------------------------------------------
def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_starting_planet=1,
    star_position_from_moon=1,
    dhasa_level_index=2,
    round_duration=True,
    dhasa_method=const.KALACHAKRA_TYPE.RAGHAVACHARYA,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Wrapper: computes JD & seed longitude and returns KCD rows.
    """
    global year_duration

    jd = utils.julian_day_number(dob, tob)
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_long = charts.get_chart_element_longitude(
        jd,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )
    return kalachakra_dhasa(
        planet_longitude=planet_long,
        jd=jd,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        dhasa_method=dhasa_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        place=place,
        **kwargs,
    )


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_starting_planet=1,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)
    vd = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor,
        chart_method,
        dhasa_starting_planet,
        star_position_from_moon,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    jds = [utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0)) for _, (y, m, d, fh), _ in vd]
    mpl = utils.degrees_between_jds(jds, jd_at_dob, jd_current)
    ppl = charts.get_nakshathra_dhasa_progression_longitudes(
        jd_at_dob,
        place,
        planet_progression_correction=mpl,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )
    return ppl


def kalachakra_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    dhasa_method: int = const.KALACHAKRA_TYPE.PVR_BOOK,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_starting_planet: int = 1,
    star_position_from_moon: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kalachakra — return ONLY the immediate (p -> p+1) children inside the given parent span.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or a non-empty tuple/list")
    parent_sign = path[-1]
    k = len(path)

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

    planet_long = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )
    dhasa_periods = _get_dhasa_progression(planet_longitude=planet_long, dhasa_method=dhasa_method)
    if not dhasa_periods:
        return []

    md_sign = path[0]
    md_entry = next((e for e in dhasa_periods if int(e[0]) == int(md_sign)), None)
    if md_entry is None:
        return []
    bhut_rasis, bhut_years, kc_i, pa_i = md_entry[1]

    def _children_method1(parent_sign_local, parent_years_local):
        cyc = _rotate_cycle_from_sign(_cycle_for(kc_i, pa_i), parent_sign_local)
        yrs = _scaled_child_years_proportional(parent_years_local, _sign_year_weights(cyc))
        return cyc, yrs

    def _children_method2(parent_sign_local, parent_years_local):
        cyc = _rotate_cycle_from_sign(_cycle_for(kc_i, pa_i), parent_sign_local)
        yrs = _scaled_child_years_proportional(parent_years_local, _sign_year_weights(cyc))
        return cyc, yrs

    def _children_method3(parent_sign_local, parent_years_local):
        if k == 1:
            total = float(sum(bhut_years)) or 1.0
            scale = parent_years_local / total
            cyc = list(bhut_rasis)
            yrs = [float(by) * scale for by in bhut_years]
            return cyc, yrs
        return _children_method1(parent_sign_local, parent_years_local)

    if dhasa_method == const.KALACHAKRA_TYPE.PVR_BOOK:
        child_builder = _children_method1
    elif dhasa_method == const.KALACHAKRA_TYPE.SANJAY_RATH:
        child_builder = _children_method2
    else:
        child_builder = _children_method3

    child_signs, child_years = child_builder(parent_sign, parent_years)
    n = min(len(child_signs), len(child_years))
    child_signs, child_years = child_signs[:n], child_years[:n]
    if n == 0:
        return []

    out = []
    cursor = start_jd
    for i, (cs, cy) in enumerate(zip(child_signs, child_years)):
        child_end = end_jd if i == n - 1 else cursor + cy * year_duration
        out.append([path + (int(cs),), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break

    out[-1][2] = _jd_to_tuple(end_jd)
    return out


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    dhasa_method: int = const.KALACHAKRA_TYPE.PVR_BOOK,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_starting_planet: int = 1,
    star_position_from_moon: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kalachakra — narrow Mahā -> … -> target depth; return full running ladder.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        flt = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds)]
        if not flt:
            return []
        flt.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _ in flt:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    def _lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    running_all = []

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    maha_rows = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_starting_planet=dhasa_starting_planet,
        star_position_from_moon=star_position_from_moon,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_method=dhasa_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )
    maha_for_utils = [(_lords(row[0]), row[1]) for row in maha_rows]

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = kalachakra_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            dhasa_method=dhasa_method,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_starting_planet=dhasa_starting_planet,
            star_position_from_moon=star_position_from_moon,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )

        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            break

        periods = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
            running = [_lords(rdk[0]), rdk[1], rdk[2]]

        running_all.append(running)

    return running_all


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
    _dhasa_method = const.KALACHAKRA_TYPE.RAGHAVACHARYA
    import time
    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        print(
            "Dehā        :",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_method=_dhasa_method,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=_dhasa_method,
            dhasa_duration_type=dd,
        )
        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
            )
        )
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kalachakra_dhasa_tests()
