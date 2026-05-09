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
from jhora.horoscope.chart import charts, house, arudhas
from jhora.horoscope.dhasa.raasi import narayana
from jhora.panchanga import drik

""" TODO logic not fully implemented """

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


# -----------------------------------------------------------------------------
#   IR local rules (order + duration) – chart passed in defines the context
# -----------------------------------------------------------------------------
def _dhasa_duration(planet_positions, dhasa_sign):
    """
    Duration in the SAME chart passed in:
      - Count inclusive from dhasa_sign (S) to its lord L in this chart.
      - Direction decided by S (odd -> forward, even -> reverse).
      - Overrides: own=12, 7th=10.
    NOTE: For IR we pass D9(KM/Nādi), for generalized/PVR we pass target varga, etc.
    """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    # If you expose user-owner knobs (e.g., Scorpio->Mars vs Ketu), resolve here before mapping.
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, dhasa_sign)
    house_of_lord = int(p_to_h[lord_of_sign]) % 12

    if house_of_lord == dhasa_sign:
        return 12
    if house_of_lord == (dhasa_sign + const.HOUSE_7) % 12:
        return 10

    direction = +1 if dhasa_sign in const.odd_signs else -1
    return utils.count_rasis(dhasa_sign, house_of_lord, dir=direction, total=12)


def _dhasa_progression(dhasa_lord):
    """
    Iranganti progression per rasi-modality with odd/even direction:
      - Movable: step ±1
      - Fixed  : every 6th (0-based '6th-from' step == 5) => ±5
      - Dual   : 1,4,7,10 ; 5,8,11,2 ; 9,12,3,6  (apply direction)
    """
    direction = 1 if dhasa_lord in const.odd_signs else -1

    if dhasa_lord in const.fixed_signs:
        return [(dhasa_lord + direction * h * const.HOUSE_6) % 12 for h in range(12)]
    if dhasa_lord in const.movable_signs:
        return [(dhasa_lord + direction * h) % 12 for h in range(12)]

    frame = [1, 4, 7, 10, 5, 8, 11, 2, 9, 12, 3, 6]
    return [(dhasa_lord + direction * (h - 1)) % 12 for h in frame]


# -----------------------------------------------------------------------------
#   Common helpers
# -----------------------------------------------------------------------------
def _append_row(_rows, _labels, _start_jd, _dur_years, round_duration, dhasa_level_index):
    _start_str = utils.jd_to_gregorian(_start_jd)
    _durn = round(_dur_years, dhasa_level_index + 1) if round_duration else _dur_years
    _rows.append((tuple(_labels), _start_str, float(_durn)))


def _expand_iranganti_levels(_rows, _level_target, _labels, _parent_sign,
                             _start_jd, _dur_years, _current_level,
                             planet_positions_ctx, round_duration, dhasa_level_index):
    """
    Recursive builder for IR: order from _dhasa_progression(parent), equal-split 12,
    Σ(children) == parent, and JD advances exactly by child_years * year_duration.
    """
    if _current_level == _level_target:
        _append_row(_rows, _labels, _start_jd, _dur_years, round_duration, dhasa_level_index)
        return

    next_order = _dhasa_progression(_parent_sign)
    child_years = _dur_years / 12.0

    jd_ptr = _start_jd
    for _child_sign in next_order:
        _expand_iranganti_levels(
            _rows=_rows,
            _level_target=_level_target,
            _labels=_labels + [_child_sign],
            _parent_sign=_child_sign,
            _start_jd=jd_ptr,
            _dur_years=child_years,
            _current_level=_current_level + 1,
            planet_positions_ctx=planet_positions_ctx,
            round_duration=round_duration,
            dhasa_level_index=dhasa_level_index
        )
        jd_ptr += child_years * year_duration


# -----------------------------------------------------------------------------
#   Method 1: Iranganti Rangacharya (IR) – D-9 (KM/Nādi) ONLY
# -----------------------------------------------------------------------------
def _iranganti_rangacharya_method(dob, tob, place,
                                  years=1, months=1, sixty_hours=1,
                                  dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                                  round_duration=True,
                                  dhasa_duration_type=None,
                                  savana_year_method=None,
                                  **kwargs):
    """
    IR Padanadhamsa: reckon in Jaimini/Krishna-Mishra (Nādi) Navamsa (D-9).
    """
    if not (1 <= int(dhasa_level_index) <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # D1 for AL
    d1_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=1,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    al = arudhas.bhava_arudhas_from_planet_positions(d1_positions)[0]

    # D9 (KM/Nādi) – both seed AND engine for IR
    d9_km_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=9,
        chart_method=4
    )[:const._pp_count_upto_ketu]

    # If AL is Scorpio/Aquarius, pick stronger co-lord in D9(KM) before taking the D9 sign
    if al == const.SCORPIO:
        al_lord = house.stronger_planet_from_planet_positions(d9_km_positions,
                                                              const.MARS_ID, const.KETU_ID)
    elif al == const.AQUARIUS:
        al_lord = house.stronger_planet_from_planet_positions(d9_km_positions,
                                                              const.SATURN_ID, const.RAHU_ID)
    else:
        al_lord = house.house_owner_from_planet_positions(d1_positions, al)

    p2h_d9km = utils.get_planet_house_dictionary_from_planet_positions(d9_km_positions)
    lord_sign_d9 = int(p2h_d9km[al_lord]) % 12
    seed = house.stronger_rasi_from_planet_positions(
        d9_km_positions, lord_sign_d9, (lord_sign_d9 + const.HOUSE_7) % 12
    )

    # Build timeline in D9(KM) using IR rules
    md_order = _dhasa_progression(seed)
    rows, jd_ptr = [], float(jd_at_dob)

    for md_sign in md_order:
        md_years = float(_dhasa_duration(d9_km_positions, md_sign))
        if int(dhasa_level_index) == 1:
            _append_row(rows, [md_sign], jd_ptr, md_years, round_duration, dhasa_level_index)
        else:
            _expand_iranganti_levels(rows, int(dhasa_level_index), [md_sign], md_sign,
                                     jd_ptr, md_years, 1, d9_km_positions, round_duration, dhasa_level_index)
        jd_ptr += md_years * year_duration

    return rows


# -----------------------------------------------------------------------------
#   Method 2: Sanjay Rath (SR) – D-9 ONLY (Padanathamsa = Navamsa Narayana)
# -----------------------------------------------------------------------------
def _sanjay_rath_method(dob, tob, place,
                        years=1, months=1, sixty_hours=1,
                        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                        round_duration=True,
                        navamsa_chart_method_for_sr=1,
                        dhasa_duration_type=None,
                        savana_year_method=None,
                        **kwargs):
    """
    SR Padanadhamsa = Narayana Dasa of the Navamsa.
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # D1 for AL
    d1_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=1,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    al = arudhas.bhava_arudhas_from_planet_positions(d1_positions)[0]

    # D9 (variant knob): Parāśara=1 (default) or KM/Nādi=4
    d9_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=9,
        chart_method=navamsa_chart_method_for_sr
    )[:const._pp_count_upto_ketu]

    # Dual-lord AL strength in D9
    if al == const.SCORPIO:
        al_lord = house.stronger_planet_from_planet_positions(d9_positions,
                                                              const.MARS_ID, const.KETU_ID)
    elif al == const.AQUARIUS:
        al_lord = house.stronger_planet_from_planet_positions(d9_positions,
                                                              const.SATURN_ID, const.RAHU_ID)
    else:
        al_lord = house.house_owner_from_planet_positions(d1_positions, al)

    p2h_d9 = utils.get_planet_house_dictionary_from_planet_positions(d9_positions)
    lord_sign_d9 = int(p2h_d9[al_lord]) % 12
    seed = house.stronger_rasi_from_planet_positions(
        d9_positions, lord_sign_d9, (lord_sign_d9 + const.HOUSE_7) % 12
    )

    # Run Narayana Dasa ON D9 from this seed (your Narayana module governs order/durations)
    return narayana._narayana_dhasa_calculation(
        d9_positions, seed, dob, tob, place,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=dhasa_level_index,
        varsha_narayana=False,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


# -----------------------------------------------------------------------------
#   Method 3: PVR/JHora generalized – ANY varga (seed chart == engine chart)
# -----------------------------------------------------------------------------
def _pvr_generalized_method(dob, tob, place, divisional_chart_factor=1,
                            years=1, months=1, sixty_hours=1,
                            dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                            round_duration=True,
                            dhasa_duration_type=None,
                            savana_year_method=None,
                            **kwargs):
    """
    PVR/JHora-style 'Padanadhamsa':
      - Seed in TARGET varga (dcf): AL in D1 -> AL-lord (Sc/Aq: stronger co-lord IN target varga)
        -> lord's sign in target varga vs its 7th (stronger).
      - Engine: run Narayana Dasa on the SAME varga (dcf).
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # Engine/seed chart = requested varga
    varga_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    # D1 for AL
    d1_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=1,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    al = arudhas.bhava_arudhas_from_planet_positions(d1_positions)[0]

    # AL-lord resolution; for Sc/Aq AL, pick stronger co-lord in TARGET varga
    if al == const.SCORPIO:
        al_lord = house.stronger_planet_from_planet_positions(varga_positions,
                                                              const.MARS_ID, const.KETU_ID)
    elif al == const.AQUARIUS:
        al_lord = house.stronger_planet_from_planet_positions(varga_positions,
                                                              const.SATURN_ID, const.RAHU_ID)
    else:
        al_lord = house.house_owner_from_planet_positions(d1_positions, al)

    p2h_v = utils.get_planet_house_dictionary_from_planet_positions(varga_positions)
    lord_sign_v = int(p2h_v[al_lord]) % 12
    seed = house.stronger_rasi_from_planet_positions(
        varga_positions, lord_sign_v, (lord_sign_v + const.HOUSE_7) % 12
    )

    return narayana._narayana_dhasa_calculation(
        varga_positions, seed, dob, tob, place,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=dhasa_level_index,
        varsha_narayana=False,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


# -----------------------------------------------------------------------------
#   Public router
# -----------------------------------------------------------------------------
def get_dhasa_antardhasa(dob, tob, place,
                         divisional_chart_factor=9, years=1, months=1, sixty_hours=1,
                         dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                         round_duration=True, method=const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA,
                         # SR variant: choose D9 build (1=Parāśara, 4=KM/Nādi)
                         navamsa_chart_method_for_sr=1,
                         dhasa_duration_type=None,
                         savana_year_method=None,
                         **kwargs):
    """
    method=1 -> Iranganti Rangacharya (D-9 KM/Nādi ONLY; seed+engine in D9)
    method=2 -> Sanjay Rath (D-9 ONLY; Padanathamsa = Navamsa Narayana)
    method=3 -> PVR/JHora generalized (seed & engine in target varga 'dcf')

    NOTE:
      - For methods 1 & 2, D-9 is used internally regardless of 'divisional_chart_factor'.
      - For method 3, 'divisional_chart_factor' drives both seed & engine.
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    if method == const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA:
        return _iranganti_rangacharya_method(
            dob, tob, place,
            years=years, months=months, sixty_hours=sixty_hours,
            dhasa_level_index=dhasa_level_index,
            round_duration=round_duration,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )

    if method == const.PADHANADHAMSA_TYPE.SANJAY_RATH:
        return _sanjay_rath_method(
            dob, tob, place,
            years=years, months=months, sixty_hours=sixty_hours,
            dhasa_level_index=dhasa_level_index,
            round_duration=round_duration,
            navamsa_chart_method_for_sr=navamsa_chart_method_for_sr,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )

    # method == 3 (PVR generalized)
    return _pvr_generalized_method(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


def padanadhamsa_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    # Engine/router knobs (match your base)
    divisional_chart_factor: int = 9,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_method: int = const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA,
    navamsa_chart_method_for_sr: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Padanādhamsa — return ONLY the immediate (parent -> children) splits.

    Output rows:
        [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Behavior by method:
      • Method 1 (IR – D9 KM/Nādi): children built directly (no base call).
        - Order: _dhasa_progression(parent_sign)
        - Durations: equal split (/12) of parent duration

      • Method 2 (SR – D9 Narayana) & Method 3 (PVR generalized):
        - Use base router get_dhasa_antardhasa(...depth=k+1) and filter rows under parent.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")

    parent_sign = path[-1]
    k = len(path)  # parent depth

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- resolve parent span (use selected module-level year_duration)
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    # =========================
    #  Method 1: IR — DIRECT
    # =========================
    if int(dhasa_method) == const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA:
        # Children order from the IR progression (no chart rebuild needed here)
        order = _dhasa_progression(parent_sign)
        child_years = parent_years / 12.0
        incr_days = child_years * year_duration

        out, cursor = [], start_jd
        for i, sgn in enumerate(order):
            child_end = end_jd if i == 11 else cursor + incr_days
            if child_end > end_jd:
                child_end = end_jd
            if child_end > cursor:
                out.append((path + (sgn,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)))
            cursor = child_end
            if cursor >= end_jd:
                break
        if out:
            out[-1] = (out[-1][0], out[-1][1], _jd_to_tuple(end_jd))
        return out

    # ==========================================
    #  Methods 2 & 3: SR/PVR — BASE-FILTER
    # ==========================================
    # Build a depth-(k+1) table and filter the subtree under `path`
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=k + 1,
        round_duration=False,
        method=int(dhasa_method),
        navamsa_chart_method_for_sr=navamsa_chart_method_for_sr,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    children = []
    for (lords_tuple, start_tuple, dur_years) in rows:
        if len(lords_tuple) != k + 1:
            continue
        if tuple(lords_tuple[:k]) != path:
            continue
        sjd = _tuple_to_jd(start_tuple)
        ejd = sjd + float(dur_years) * year_duration
        if ejd <= start_jd or sjd >= end_jd:
            continue
        # clip to parent span
        cs = max(sjd, start_jd)
        ce = min(ejd, end_jd)
        if ce > cs:
            children.append((tuple(lords_tuple), _jd_to_tuple(cs), _jd_to_tuple(ce)))

    # exact closure
    if children:
        children[-1] = (children[-1][0], children[-1][1], _jd_to_tuple(end_jd))
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 9,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_method: int = const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA,
    navamsa_chart_method_for_sr: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Padanādhamsa — running ladder at `current_jd`:
      [
        [(s1,),              start1, end1],
        [(s1,s2),            start2, end2],
        ...
        [(s1,..,s_d),        startd, endd]
      ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- depth normalization
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _to_periods(children_rows, parent_end_tuple):
        """
        children_rows: [ (lords_tuple, start_tuple, end_tuple), ... ]
        Return strictly increasing [(lords_tuple, start_tuple), ... , sentinel]
        """
        if not children_rows:
            return []
        rows = sorted(children_rows, key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, en in rows:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel end
        return proj

    # ---- Step 1: Mahā via base router (depth=1, unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        method=int(dhasa_method),
        navamsa_chart_method_for_sr=navamsa_chart_method_for_sr,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    if not maha_rows:
        return []

    # Build Mahā periods + sentinel
    periods = []
    jd_cursor = jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        lords = tuple(lords_tuple) if isinstance(lords_tuple, (tuple, list)) else (lords_tuple,)
        periods.append((lords, start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + float(dur_years) * year_duration
    periods.append((periods[-1][0], utils.jd_to_gregorian(jd_cursor)))

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Step 2..target: expand only the running parent each time
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = padanadhamsa_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years, months=months, sixty_hours=sixty_hours,
            dhasa_method=int(dhasa_method),
            navamsa_chart_method_for_sr=navamsa_chart_method_for_sr,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            # Represent “no deeper split” as a boundary
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_periods(kids, parent_end_tuple=parent_end)
        rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
        running = [tuple(rdk[0]), rdk[1], rdk[2]]
        ladder.append(running)

    return ladder


# -----------------------------------------------------------------------------
#   Quick local test
# -----------------------------------------------------------------------------
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
    _dhasa_method = 3
    _dhasa_cycle_count = 1 if _dhasa_method == 1 else 2
    import time

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=_dhasa_method,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob, tob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            method=_dhasa_method,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=_dhasa_cycle_count
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.padhanadhamsa_dhasa_test()
