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
from jhora.panchanga import drik

""" method = 2 KN Rao Method - Working. Method 1=> Sanjay Rath - yet to be implemented """

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


dhasa_order = {0: ([0, 3, 6, 9, 2, 5, 8, 11, 1, 4, 7, 10], [0, 9, 6, 3, 2, 11, 8, 5, 1, 10, 7, 4]),
               3: ([3, 6, 9, 0, 2, 5, 8, 11, 1, 4, 7, 10], [3, 0, 9, 6, 2, 11, 8, 5, 1, 10, 7, 4]),
               6: ([6, 9, 0, 3, 2, 5, 8, 11, 1, 4, 7, 10], [6, 3, 0, 9, 2, 11, 8, 5, 1, 10, 7, 4]),
               9: ([9, 0, 3, 6, 2, 5, 8, 11, 1, 4, 7, 10], [9, 6, 3, 0, 2, 11, 8, 5, 1, 10, 7, 4]),
               2: ([2, 5, 8, 11, 1, 4, 7, 10, 0, 3, 6, 9], [2, 11, 8, 5, 1, 10, 7, 4, 0, 9, 6, 3]),
               5: ([5, 8, 11, 2, 1, 4, 7, 10, 0, 3, 6, 9], [5, 2, 11, 8, 1, 10, 7, 4, 0, 9, 6, 3]),
               8: ([8, 11, 2, 5, 1, 4, 7, 10, 0, 3, 6, 9], [8, 5, 2, 11, 1, 10, 7, 4, 0, 9, 6, 3]),
               11: ([11, 2, 5, 8, 1, 4, 7, 10, 0, 3, 6, 9], [11, 8, 5, 2, 1, 10, 7, 4, 0, 9, 6, 3]),
               1: ([1, 4, 7, 10, 0, 3, 6, 9, 2, 5, 8, 11], [1, 10, 7, 4, 0, 9, 6, 3, 2, 11, 8, 5]),
               4: ([4, 7, 10, 1, 0, 3, 6, 9, 2, 5, 8, 11], [4, 1, 10, 7, 0, 9, 6, 3, 2, 11, 8, 5]),
               7: ([7, 10, 1, 4, 0, 3, 6, 9, 2, 5, 8, 11], [7, 4, 1, 10, 0, 9, 6, 3, 2, 11, 8, 5]),
               10: ([10, 1, 4, 7, 0, 3, 6, 9, 2, 5, 8, 11], [10, 7, 4, 1, 0, 9, 6, 3, 2, 11, 8, 5])
               }


def _dhasa_duration_kn_rao(planet_positions, sign):
    """ Use standard lord in case dual lord signs """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = const._house_owners_list[sign]  # Use standard lord in case dual lord signs
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_signs:  # count back from sign to house_of_lord
        dhasa_period = (sign - house_of_lord + 1) % 12
    else:
        dhasa_period = (house_of_lord - sign + 1) % 12
    if house_of_lord == sign:
        dhasa_period = 12
    if house_of_lord == (sign + 6) % 12:
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
    round_duration=True,
    dhasa_method=const.MANDOOKA_TYPE.KN_RAO,                    # <-- 2 = K.N. Rao (as before), 1 = Sanjay Rath (added)
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Mandooka Daśā (depth-enabled)

    Depth control:
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_tuple, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_tuple, dur_years)
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_tuple, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_tuple, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_tuple, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_tuple, dur_years)

    Methods:
      • dhasa_method = 2 (K.N. Rao) — (seed = stronger(Asc, 7th); global order from dhasa_order[seed][dirn]; Antara = rotation starting at parent index).
      • dhasa_method = 1 (Sanjay Rath) — seed from Lagna or 7th (whichever odd; fallback Lagna if both even/odd), MD "frog" leap to cover all 12; durations 7/8/9 by modality;
        Antardaśā order = parent-conditioned contiguous 12-sign sequence (anchor in {Sg,Cn,Ta} with direction per parent’s modality/parity), AD durations = MD/12.

    Rounding:
      • Returned durations rounded to `dhasa_level_index` digits when `round_duration=True`; JD math uses full precision.
    """
    # ---- Safety ---------------------------------------------------------------
    if not (const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY <= dhasa_level_index <= const.MAHA_DHASA_DEPTH.DEHA):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- Annual chart epoch (kept) -------------------------------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    # ---- Helpers (shared) -----------------------------------------------------
    _round_ndigits = getattr(const, "DHASA_DURATION_ROUNDING_TO", 2)

    def _emit(rows, labels, start_jd, dur_years):
        start_tuple = utils.jd_to_gregorian(start_jd)
        dur_out = round(dur_years, dhasa_level_index + 1) if round_duration else dur_years
        rows.append((tuple(labels), start_tuple, float(dur_out)))

    # -- SR durations (7/8/9) by modality
    def _sr_md_years(rasi: int) -> float:
        if rasi in getattr(const, "movable_signs", (0, 3, 6, 9)):  # Ar,Cn,Li,Cp
            return 7.0
        if rasi in getattr(const, "fixed_signs", (1, 4, 7, 10)):   # Ta,Le,Sc,Aq
            return 8.0
        return 9.0                                             # dual: Ge,Vi,Sg,Pi

    # -- SR seed: Lagna or 7th whichever odd; if both same parity, fallback Lagna
    def _sr_seed(asc: int) -> int:
        seventh = (asc + 6) % 12
        odd = set((0, 2, 4, 6, 8, 10))   # Ar,Ge,Le,Li,Sg,Aq (0-based)
        if asc in odd and seventh not in odd:
            return asc
        if seventh in odd and asc not in odd:
            return seventh
        # if both odd (always true for odd asc) or both even → fallback Lagna
        return asc

    # -- SR MD order: cover all 12 via two 6-sign passes with ±2 leap
    #    (matches observed JHora SR rings; here we use anti-zodiacal step -2,
    #     which reproduces Cp→Sc→Vi→... example you validated)
    def _sr_md_order(seed: int) -> list:
        step = -2
        first6 = [(seed + step * k) % 12 for k in range(6)]
        second6 = [((seed - 1) + step * k) % 12 for k in range(6)]
        return first6 + second6

    # -- SR Antardaśā order: anchor & direction by parent’s modality/parity
    def _sr_ad_order(parent_rasi: int) -> list:
        movable = set(getattr(const, "movable_signs", (0, 3, 6, 9)))
        fixed = set(getattr(const, "fixed_signs", (1, 4, 7, 10)))
        dual = set(getattr(const, "dual_signs", (2, 5, 8, 11)))
        odd = set((0, 2, 4, 6, 8, 10))
        even = set((1, 3, 5, 7, 9, 11))

        R = int(parent_rasi)
        if R in movable:
            anchor = const.SAGITTARIUS if (R in even) else const.CANCER
            dir_fwd = True if (R in even) else False
        elif R in fixed:
            anchor = const.CANCER
            dir_fwd = False
        else:  # dual
            anchor = const.TAURUS if (R in odd) else const.SAGITTARIUS
            dir_fwd = False

        seq = []
        step = +1 if dir_fwd else -1
        s = anchor
        for _ in range(12):
            seq.append(s)
            s = (s + step) % 12
        return seq

    # -- KNR Antardaśā order (your original): rotation of global order from parent index
    def _knr_bhukthis_from(global_order, parent_rasi):
        idx = global_order.index(parent_rasi)
        return [global_order[(idx + h) % 12] for h in range(12)]

    # =============================================================================
    # Seed & Global Order per method
    # =============================================================================
    asc_house = planet_positions[0][1][0]
    seventh_house = (asc_house + 6) % 12

    if dhasa_method == const.MANDOOKA_TYPE.SANJAY_RATH:
        # --- Sanjay Rath -------------------------------------------------------
        dhasa_seed = _sr_seed(asc_house)
        dhasa_lords = _sr_md_order(dhasa_seed)

        def _maha_duration(rasi): return _sr_md_years(rasi)
        def _antara_order(parent_rasi): return _sr_ad_order(parent_rasi)

    else:
        # --- K.N. Rao (existing) ----------------------------------------------
        dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
        dirn = 1 if dhasa_seed in const.even_signs else 0
        dhasa_lords = dhasa_order[dhasa_seed][dirn]

        def _maha_duration(rasi): return float(_dhasa_duration_kn_rao(planet_positions, rasi))
        def _antara_order(parent_rasi): return _knr_bhukthis_from(dhasa_lords, parent_rasi)

    # =============================================================================
    # Build rows per requested depth
    # =============================================================================
    rows = []
    jd_cursor = jd_at_dob

    for md_rasi in dhasa_lords:
        md_years = float(_maha_duration(md_rasi))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit(rows, [md_rasi], jd_cursor, md_years)
            jd_cursor += md_years * year_duration
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ad_years = md_years / 12.0
            jd_b = jd_cursor
            for ad_rasi in _antara_order(md_rasi):
                _emit(rows, [md_rasi, ad_rasi], jd_b, ad_years)
                jd_b += ad_years * year_duration
            jd_cursor = jd_b
            continue

        # L3..L6: recursive equal split using the same antara order rule
        def _recurse(level, parent_rasi, p_start_jd, p_years, prefix):
            child_years = p_years / 12.0
            jd_here = p_start_jd
            for ch in _antara_order(parent_rasi):
                if level < dhasa_level_index:
                    jd_here = _recurse(level + 1, ch, jd_here, child_years, prefix + (ch,))
                else:
                    _emit(rows, prefix + (ch,), jd_here, child_years)
                    jd_here += child_years * year_duration
            return jd_here

        jd_cursor = _recurse(level=const.MAHA_DHASA_DEPTH.ANTARA,  # 2 → build 3..N
                             parent_rasi=md_rasi,
                             p_start_jd=jd_cursor,
                             p_years=md_years,
                             prefix=(md_rasi,))

    return rows


def mandooka_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (one of duration or end must be provided)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    # epoching knobs (match your base)
    divisional_chart_factor: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    chart_method: int = 1,       # kept for parity (not used by charts.divisional_chart here)
    round_duration: bool = False,   # tiler returns exact spans; no rounding here
    dhasa_method: int = const.MANDOOKA_TYPE.KN_RAO,             # 2 = KNRao (current); 1 = Sanjay Rath (reserved for later)
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Mandooka — return ONLY the immediate (p -> p+1) children inside the given parent span.

    Rules (K.N. Rao dhasa_method, matching your base):
      • Global 12-sign order = dhasa_order[seed][dirn], where
          seed = stronger(Asc, 7th)  [or SR mapping when dhasa_method==1]
          dirn = 1 if seed is EVEN else 0
      • Child order under any parent = rotate(global order) so it starts at `parent_rasi`.
      • Split rule: equal (parent_years / 12)  → Σ(children) = parent.
      • Exact tiling of [parent_start, parent_end); last child clamped to parent_end.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")
    parent_rasi = int(path[-1])

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- parent span
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

    # ---- epoch chart (match your base: annual varga chart at birth JD)
    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    # ---- seed & global order (KNRao; SR mapping reserved for dhasa_method==1)
    asc_house = planet_positions[0][1][0]
    seventh = (asc_house + 6) % 12
    if dhasa_method == const.MANDOOKA_TYPE.SANJAY_RATH and asc_house in const.even_signs:
        # SR mapping placeholder (matches your base branch)
        if asc_house in const.fixed_signs:
            dhasa_seed = const.LIBRA
        elif asc_house in const.dual_signs:
            dhasa_seed = const.SCORPIO
        else:
            dhasa_seed = const.SAGITTARIUS
    else:
        dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh)

    dirn = 1 if dhasa_seed in const.even_signs else 0
    global_order = list(dhasa_order[dhasa_seed][dirn])  # length 12

    # ---- rotation: start at parent_rasi index
    try:
        j = global_order.index(parent_rasi)
    except ValueError:
        # If parent_rasi is not in the global list (shouldn't happen), do nothing
        return []
    child_order = [global_order[(j + h) % 12] for h in range(12)]

    # ---- equal split & tiling
    child_years = parent_years / 12.0
    children, cursor = [], start_jd
    for i, cr in enumerate(child_order):
        cr = int(cr)
        child_end = end_jd if i == 11 else cursor + child_years * year_duration
        children.append([path + (cr,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    chart_method: int = 1,        # kept for parity
    round_duration: bool = False, # runner uses exact (start,end)
    dhasa_method: int = const.MANDOOKA_TYPE.KN_RAO,              # 2 = KNRao (current); 1 = SR (reserved)
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Mandooka — narrow Mahā -> … -> target depth and return the full running ladder:

      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        [(l1,l2,l3),         start3, end3],
        [(l1,l2,l3,l4),      start4, end4],
        [(l1,l2,l3,l4,l5),   start5, end5],
        [(l1,l2,l3,l4,l5,l6),start6, end6],
      ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- depth normalization
    def _normalize_depth(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target_depth = _normalize_depth(dhasa_level_index)

    # ---- helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps

    def _to_utils_periods(children_rows, parent_end_tuple, eps=1.0):
        """
        children_rows: [ [lords_tuple, start_tuple, end_tuple], ... ]
        Returns: [(lords_tuple, start_tuple), ...] + sentinel(parent_end_tuple),
        after filtering zero-length rows and enforcing strictly increasing starts.
        """
        flt = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps)]
        if not flt:
            return []
        flt.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _ in flt:
            sj = _tuple_to_jd(st)
            if prev is None or sj > prev:
                proj.append((lords, st))
                prev = sj
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel bounds the last child
        return proj

    def _lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    running_all = []

    # ---- derive (dob,tob) once (birth epoch)
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    # ---- L1: Mahā via YOUR base (depth=1, unrounded)
    maha_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        dhasa_method=dhasa_method,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    maha_for_utils = [(_lords(row[0]), row[1]) for row in maha_rows]

    # pick running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    # ---- L2..target: expand only the running parent each step
    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = mandooka_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years, months=months, sixty_hours=sixty_hours,
            chart_method=chart_method,
            round_duration=False,
            dhasa_method=dhasa_method,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not children:
            # represent as zero-length at boundary when no deeper split
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
    import time
    _dhasa_method = 1
    dcf = 11

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=_dhasa_method,
            divisional_chart_factor=dcf,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob, tob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=_dhasa_method,
            divisional_chart_factor=dcf,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.mandooka_dhasa_test()
