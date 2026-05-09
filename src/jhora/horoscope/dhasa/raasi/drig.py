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
from typing import List, Tuple, Sequence, Optional, Union

from jhora import const, utils
from jhora.horoscope.chart import house, charts
from jhora.horoscope.dhasa.raasi import narayana
from jhora.panchanga import drik

# Use library sidereal year as default; overwritten per-call by drik.dhasa_year_duration(...)
_DAYS_IN_YEAR = float(const.sidereal_year)
_ROUND_NDIGITS = int(getattr(const, "DHASA_DURATION_ROUNDING_TO", 2))


def _set_year_duration(jd: float, place, dhasa_duration_type=None, savana_year_method=None) -> float:
    """Resolve and cache the dasa year duration used by this module."""
    global _DAYS_IN_YEAR
    _DAYS_IN_YEAR = float(drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    ))
    return _DAYS_IN_YEAR


""" OLD CODE TO SUPPORT PVR_BOOK TEST EXAMPLES """
def drig_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Drig Daśā (two-cycle) with depth control.
    """
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)
    planet_positions = charts.divisional_chart(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs,
    )[:const._pp_count_upto_ketu]
    return drig_dhasa(
        planet_positions,
        dob,
        tob,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
    )


def drig_dhasa(
    planet_positions,
    dob,
    tob,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
):
    """
    Drig Daśā (two-cycle) with depth control.
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    start_jd = utils.julian_day_number(dob, tob)

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    asc_house = p_to_h[const._ascendant_symbol]
    ninth_house = (asc_house + 9 - 1) % 12

    dhasa_progression = []
    for s in range(ninth_house, ninth_house + 3):
        s_mod = s % 12
        aspected_k = house.aspected_kendras_of_raasi(s_mod, s_mod in const.even_footed_signs)
        dhasa_progression.append([s_mod] + aspected_k)
    dhasa_progression = sum(dhasa_progression, [])

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        child_years_unrounded = parent_years / 12.0
        jd_cursor = parent_start_jd
        child_order = _antardhasa_from_planet_positions(planet_positions, parent_sign)

        if level < dhasa_level_index:
            for child_sign in child_order:
                _recurse(level + 1, child_sign, jd_cursor, child_years_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_years_unrounded * _DAYS_IN_YEAR
        else:
            for child_sign in child_order:
                start_str = utils.jd_to_gregorian(jd_cursor)
                dur_ret = round(child_years_unrounded, dhasa_level_index + 1) if round_duration else child_years_unrounded
                out_rows.append((prefix + (child_sign,), start_str, dur_ret))
                jd_cursor += child_years_unrounded * _DAYS_IN_YEAR

    rows = []

    for dhasa_lord in dhasa_progression:
        dhasa_duration = float(narayana._dhasa_duration(planet_positions, dhasa_lord))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(dhasa_duration, dhasa_level_index + 1) if round_duration else dhasa_duration,
            ))
            start_jd += dhasa_duration * _DAYS_IN_YEAR

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            dd = dhasa_duration / 12.0
            jd_b = start_jd
            bhukthis = _antardhasa_from_planet_positions(planet_positions, dhasa_lord)
            for bhukthi_lord in bhukthis:
                rows.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_b),
                    round(dd, dhasa_level_index + 1) if round_duration else dd,
                ))
                jd_b += dd * _DAYS_IN_YEAR
            start_jd += dhasa_duration * _DAYS_IN_YEAR

        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=dhasa_lord,
                parent_start_jd=start_jd,
                parent_years=dhasa_duration,
                prefix=(dhasa_lord,),
                out_rows=rows,
            )
            start_jd += dhasa_duration * _DAYS_IN_YEAR

    for dhasa_lord in dhasa_progression:
        first_dd = float(narayana._dhasa_duration(planet_positions, dhasa_lord))
        dhasa_duration2 = 12.0 - first_dd
        if dhasa_duration2 <= 0:
            dhasa_duration2 = 0.0

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(dhasa_duration2, dhasa_level_index + 1) if round_duration else dhasa_duration2,
            ))
            start_jd += dhasa_duration2 * _DAYS_IN_YEAR

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            dd = dhasa_duration2 / 12.0
            jd_b = start_jd
            bhukthis = _antardhasa_from_planet_positions(planet_positions, dhasa_lord)
            for bhukthi_lord in bhukthis:
                rows.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_b),
                    round(dd, dhasa_level_index + 1) if round_duration else dd,
                ))
                jd_b += dd * _DAYS_IN_YEAR
            start_jd += dhasa_duration2 * _DAYS_IN_YEAR

        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=dhasa_lord,
                parent_start_jd=start_jd,
                parent_years=dhasa_duration2,
                prefix=(dhasa_lord,),
                out_rows=rows,
            )
            start_jd += dhasa_duration2 * _DAYS_IN_YEAR
    return rows


def _antardhasa_from_planet_positions(planet_positions, dhasa_lord):
    """ V4.6.5 Antardhasa Ref: Drig Dasa of Parasara - PVR """
    dhasa_seed = house.stronger_rasi_from_planet_positions(
        planet_positions,
        dhasa_lord,
        (dhasa_lord + const.HOUSE_7) % 12,
    )
    direction = 1 if dhasa_lord in const.odd_signs else -1
    if dhasa_lord in const.fixed_signs:
        _dhasa_progression = [(dhasa_seed + direction * h * const.HOUSE_6) % 12 for h in range(12)]
    elif dhasa_lord in const.movable_signs:
        _dhasa_progression = [(dhasa_seed + direction * h) % 12 for h in range(12)]
    else:
        _dhasa_progression = [(dhasa_seed + direction * (h - 1)) % 12 for h in [1, 4, 7, 10, 5, 8, 11, 2, 9, 12, 3, 6]]
    return _dhasa_progression


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _mod12(x: int) -> int:
    return x % 12


def _pp_upto_ketu(jd: float, place, dcf: int, chart_method: int = 1, **kwargs):
    """Compute varga planet positions and slice to L..Ketu (exclude outers)."""
    pp = charts.divisional_chart(
        jd,
        place,
        divisional_chart_factor=dcf,
        chart_method=chart_method,
        **kwargs,
    )
    return pp[:const._pp_count_upto_ketu]


def _chart_from_pp(pp):
    """Chart list ['1/L', '', ...] Aries..Pisces."""
    return utils.get_house_planet_list_from_planet_positions(pp)


def _p_to_h_from_pp(pp):
    """Planet-to-house dict from planet_positions."""
    return utils.get_planet_house_dictionary_from_planet_positions(pp)


def _lagna_sign_from_pp(pp) -> int:
    """Lagna sign index 0..11 from planet_positions."""
    pth = _p_to_h_from_pp(pp)
    if 'L' in pth:
        return int(pth['L']) % 12
    asc_sym = getattr(const, "_ascendant_symbol", "L")
    if asc_sym in pth:
        return int(pth[asc_sym]) % 12
    raise ValueError("Lagna not found in planet-house dictionary (expected 'L').")


def _jd_to_tuple(jd_val: float) -> Tuple[int, int, int, float]:
    return utils.jd_to_gregorian(jd_val)


def _tuple_to_jd(t: Tuple[int, int, int, float]) -> float:
    y, m, d, fh = t
    return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))


def _append_row(rows: List[Tuple], lords: Sequence[int], start_jd: float, dur_years: float, round_duration: bool):
    start_t = _jd_to_tuple(start_jd)
    d = round(float(dur_years), _ROUND_NDIGITS) if round_duration else float(dur_years)
    rows.append((tuple(int(x) % 12 for x in lords), start_t, float(d)))


def _dist_forward(a: int, b: int) -> int:
    d = (b - a) % 12
    return 12 if d == 0 else d


def _dist_backward(a: int, b: int) -> int:
    d = (a - b) % 12
    return 12 if d == 0 else d


def _is_odd_sign(sign: int) -> bool:
    return sign in const.odd_signs


def _is_movable(sign: int) -> bool:
    return sign in const.movable_signs


def _is_fixed(sign: int) -> bool:
    return sign in const.fixed_signs


def _is_dual(sign: int) -> bool:
    return sign in const.dual_signs


# -----------------------------------------------------------------------------
# PVR_PAPER: MD ordering of 3 aspected signs (nearest-first in direction)
# -----------------------------------------------------------------------------
def _paper_order_aspected_three(chart, anchor: int, pp) -> List[int]:
    cand = list(house.raasi_drishti_of_the_raasi(chart, anchor) or [])
    uniq: List[int] = []
    for x in cand:
        x = int(x) % 12
        if x not in uniq:
            uniq.append(x)
    if len(uniq) != 3:
        raise ValueError(f"PAPER: expected 3 aspected signs for anchor={anchor}, got {uniq}")

    zodiacal = _is_fixed(anchor) or (_is_dual(anchor) and _is_odd_sign(anchor))
    dist = (lambda t: _dist_forward(anchor, t)) if zodiacal else (lambda t: _dist_backward(anchor, t))

    uniq.sort(key=lambda t: dist(t))
    anchor_lord = house.house_owner_from_planet_positions(pp, anchor, check_during_dhasa=True)

    out: List[int] = []
    i = 0
    while i < len(uniq):
        d0 = dist(uniq[i])
        group = [uniq[i]]
        j = i + 1
        while j < len(uniq) and dist(uniq[j]) == d0:
            group.append(uniq[j])
            j += 1

        if len(group) == 1:
            out.extend(group)
        else:
            prev_lord = None
            if out:
                prev_lord = house.house_owner_from_planet_positions(pp, out[-1], check_during_dhasa=True)

            pref = None
            if prev_lord is not None:
                for g in group:
                    if house.house_owner_from_planet_positions(pp, g, check_during_dhasa=True) == prev_lord:
                        pref = g
                        break
            if pref is None:
                for g in group:
                    if house.house_owner_from_planet_positions(pp, g, check_during_dhasa=True) == anchor_lord:
                        pref = g
                        break

            if pref is None:
                out.extend(group)
            else:
                out.append(pref)
                out.extend([g for g in group if g != pref])

        i = j

    return out


# -----------------------------------------------------------------------------
# MD sequence (both methods share the same 9th/10th/11th block skeleton)
# -----------------------------------------------------------------------------
def _md_sequence(lagna_sign: int, dhasa_method: int, chart, pp) -> List[int]:
    seq: List[int] = []
    for offset in (const.HOUSE_9, const.HOUSE_10, const.HOUSE_11):
        anchor = _mod12(lagna_sign + offset)
        seq.append(anchor)

        if dhasa_method == const.DRIG_TYPE.PVR_BOOK:
            even_footed = anchor in const.even_footed_signs
            aspects = list(house.aspected_kendras_of_raasi(anchor, even_footed) or [])
            uniq: List[int] = []
            for x in aspects:
                x = int(x) % 12
                if x not in uniq:
                    uniq.append(x)
            if len(uniq) != 3:
                raise ValueError(f"BOOK: expected 3 aspected kendras for anchor={anchor}, got {uniq}")
            seq.extend(uniq)
        else:
            seq.extend(_paper_order_aspected_three(chart, anchor, pp))

    if len(seq) != 12:
        raise ValueError(f"Invalid MD sequence length {len(seq)}: {seq}")
    return seq


# -----------------------------------------------------------------------------
# Durations
# -----------------------------------------------------------------------------
def _md_years_paper(sign: int) -> float:
    """Paper: movable=7, fixed=8, dual=9 (sthira years)."""
    if _is_movable(sign):
        return 7.0
    if _is_fixed(sign):
        return 8.0
    return 9.0


def _md_years_book_cycle1(pp, sign: int) -> float:
    """Book: MD years computed like Narayana dasha."""
    return float(narayana._dhasa_duration(pp, sign))


def _book_cycle_years(cycle_idx: int, cycle1_years: float) -> float:
    """Book: 2 cycles; cycle2 = 12 - cycle1 (clamp)."""
    if cycle_idx == 1:
        return float(cycle1_years)
    y2 = 12.0 - float(cycle1_years)
    return 0.0 if y2 <= 0 else float(y2)


# -----------------------------------------------------------------------------
# Antardasa order
# -----------------------------------------------------------------------------
def _paper_antardhasa_order(parent_sign: int, pp) -> List[int]:
    opp = _mod12(parent_sign + const.HOUSE_7)
    seed = int(house.stronger_rasi_from_planet_positions(pp, parent_sign, opp)) % 12
    direction = 1 if _is_odd_sign(parent_sign) else -1

    if _is_movable(parent_sign):
        return [_mod12(seed + direction * i) for i in range(12)]

    if _is_fixed(parent_sign):
        step = 5 * direction
        return [_mod12(seed + step * i) for i in range(12)]

    step3 = 3 * direction
    bases = [seed, _mod12(seed + const.HOUSE_5), _mod12(seed + const.HOUSE_9)]
    seq: List[int] = []
    for base in bases:
        for i in range(4):
            seq.append(_mod12(base + step3 * i))
    return seq


def _children_order(parent_sign: int, pp, dhasa_method: int) -> List[int]:
    if dhasa_method == const.DRIG_TYPE.PVR_BOOK:
        return list(narayana._narayana_antardhasa(pp, int(parent_sign) % 12))
    return _paper_antardhasa_order(int(parent_sign) % 12, pp)


# -----------------------------------------------------------------------------
# Equal split recursion (L2..L6)
# -----------------------------------------------------------------------------
def _expand_equal_12(rows: List[Tuple],
                     target_depth: int,
                     current_depth: int,
                     lords_prefix: List[int],
                     parent_sign: int,
                     start_jd: float,
                     dur_years: float,
                     pp,
                     dhasa_method: int,
                     round_duration: bool):
    if current_depth == target_depth:
        _append_row(rows, lords_prefix, start_jd, dur_years, round_duration)
        return

    order = _children_order(parent_sign, pp, dhasa_method)
    child_years = float(dur_years) / 12.0
    jd_ptr = float(start_jd)

    for child_sign in order:
        child_sign = int(child_sign) % 12
        _expand_equal_12(
            rows=rows,
            target_depth=target_depth,
            current_depth=current_depth + 1,
            lords_prefix=lords_prefix + [child_sign],
            parent_sign=child_sign,
            start_jd=jd_ptr,
            dur_years=child_years,
            pp=pp,
            dhasa_method=dhasa_method,
            round_duration=round_duration,
        )
        jd_ptr += child_years * _DAYS_IN_YEAR


# =============================================================================
# PUBLIC 1: get_dhasa_antardhasa
# =============================================================================
def get_dhasa_antardhasa(jd: float,
                         place,
                         dhasa_method=const.DRIG_TYPE.PVR_PAPER,
                         divisional_chart_factor: int = 1,
                         chart_method: int = 1,
                         dhasa_duration_type=None,
                         savana_year_method=None,
                         **kwargs) -> List[Tuple]:
    """
    Returns rows:
      (lords_tuple, start_tuple(Y,M,D,fh), duration_years)

    kwargs:
      dhasa_level_index: 1..6 (default const.MAHA_DHASA_DEPTH.ANTARA)
      round_duration: bool (default True)
      any kwargs passed to charts.divisional_chart(...)
    """
    _set_year_duration(jd, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    dhasa_level_index = int(kwargs.pop("dhasa_level_index", int(const.MAHA_DHASA_DEPTH.ANTARA)))
    round_duration = bool(kwargs.pop("round_duration", True))
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")

    pp = _pp_upto_ketu(jd, place, divisional_chart_factor, chart_method=chart_method, **kwargs)
    chart = _chart_from_pp(pp)
    lagna = _lagna_sign_from_pp(pp)

    md_seq = _md_sequence(lagna, dhasa_method, chart, pp)

    rows: List[Tuple] = []
    jd_ptr = float(jd)

    if dhasa_method == const.DRIG_TYPE.PVR_BOOK:
        for cycle in (1, 2):
            for md_sign in md_seq:
                c1 = _md_years_book_cycle1(pp, md_sign)
                md_years = _book_cycle_years(cycle, c1)
                if md_years <= 0:
                    md_years = 0

                if dhasa_level_index == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
                    _append_row(rows, [md_sign], jd_ptr, md_years, round_duration)
                else:
                    _expand_equal_12(
                        rows=rows,
                        target_depth=dhasa_level_index,
                        current_depth=1,
                        lords_prefix=[md_sign],
                        parent_sign=md_sign,
                        start_jd=jd_ptr,
                        dur_years=md_years,
                        pp=pp,
                        dhasa_method=dhasa_method,
                        round_duration=round_duration,
                    )

                jd_ptr += md_years * _DAYS_IN_YEAR
    else:
        for md_sign in md_seq:
            md_years = _md_years_paper(md_sign)

            if dhasa_level_index == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
                _append_row(rows, [md_sign], jd_ptr, md_years, round_duration)
            else:
                _expand_equal_12(
                    rows=rows,
                    target_depth=dhasa_level_index,
                    current_depth=1,
                    lords_prefix=[md_sign],
                    parent_sign=md_sign,
                    start_jd=jd_ptr,
                    dur_years=md_years,
                    pp=pp,
                    dhasa_method=dhasa_method,
                    round_duration=round_duration,
                )

            jd_ptr += md_years * _DAYS_IN_YEAR

    return rows


# =============================================================================
# PUBLIC 2: drig_immediate_children
# =============================================================================
def drig_immediate_children(
    parent_lords: Union[int, Sequence[int]],
    parent_start: Tuple[int, int, int, float],
    parent_duration: Optional[float] = None,
    parent_end: Optional[Tuple[int, int, int, float]] = None,
    *,
    jd_at_dob: float,
    place,
    dhasa_method=const.DRIG_TYPE.PVR_PAPER,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Return immediate 12 children under a given parent span:
      [ [lords_tuple, start_tuple, end_tuple], ... ]

    Uses birth-epoch positions (jd_at_dob) for ordering.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    if isinstance(parent_lords, int):
        path = (int(parent_lords) % 12,)
    else:
        path = tuple(int(x) % 12 for x in parent_lords)
    parent_sign = int(path[-1]) % 12

    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end.")
    if parent_end is None:
        end_jd = start_jd + float(parent_duration) * _DAYS_IN_YEAR
    else:
        end_jd = _tuple_to_jd(parent_end)

    if end_jd <= start_jd:
        return []

    pp_birth = _pp_upto_ketu(jd_at_dob, place, divisional_chart_factor, chart_method=chart_method, **kwargs)
    order = _children_order(parent_sign, pp_birth, dhasa_method)

    parent_years = (end_jd - start_jd) / _DAYS_IN_YEAR
    child_years = parent_years / 12.0

    out = []
    cursor = start_jd
    for i, child_sign in enumerate(order):
        child_end = end_jd if i == 11 else cursor + child_years * _DAYS_IN_YEAR
        out.append([path + (int(child_sign) % 12,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break

    if out:
        out[-1][2] = _jd_to_tuple(end_jd)
    return out


# =============================================================================
# PUBLIC 3: get_running_dhasa_for_given_date
# =============================================================================
def get_running_dhasa_for_given_date(
    current_jd: float,
    jd_at_dob: float,
    place,
    dhasa_method=const.DRIG_TYPE.PVR_PAPER,
    dhasa_level_index: int = const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns running ladder up to requested depth:
      [
        [lords_L1, start1, end1],
        [lords_L2, start2, end2],
        ...
      ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    target_depth = max(1, min(6, int(dhasa_level_index)))

    md_rows = get_dhasa_antardhasa(
        jd=jd_at_dob,
        place=place,
        dhasa_method=dhasa_method,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_level_index=int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY),
        round_duration=False,
        **kwargs,
    )
    if not md_rows:
        return []

    spans = []
    for lords, start_t, dur in md_rows:
        sjd = _tuple_to_jd(start_t)
        ejd = sjd + float(dur) * _DAYS_IN_YEAR
        spans.append((sjd, ejd, tuple(lords)))
    spans.sort(key=lambda x: x[0])

    cur = float(current_jd)
    running = None
    for sjd, ejd, lords in spans:
        if sjd <= cur < ejd:
            running = [lords, _jd_to_tuple(sjd), _jd_to_tuple(ejd)]
            break
    if running is None:
        sjd, ejd, lords = spans[-1]
        running = [lords, _jd_to_tuple(sjd), _jd_to_tuple(ejd)]

    ladder = [running]
    if target_depth == 1:
        return ladder

    for _depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running
        children = drig_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            dhasa_method=dhasa_method,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )
        if not children:
            break

        found = None
        for lords, st, en in children:
            sjd = _tuple_to_jd(st)
            ejd = _tuple_to_jd(en)
            if sjd <= cur < ejd:
                found = (tuple(lords), st, en)
                break
        if found is None:
            lords, st, en = children[-1]
            found = (tuple(lords), st, en)

        running = [found[0], found[1], found[2]]
        ladder.append(running)

    return ladder


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
    _dhasa_method = const.DRIG_TYPE.PVR_BOOK
    dcf = 1
    chart_method = 1
    print("Drig Dhasa Method", "PVR_BOOK" if _dhasa_method == const.DRIG_TYPE.PVR_BOOK else "PVR_PAPER", "div=", dcf, "cm=", chart_method)
    DLI = const.MAHA_DHASA_DEPTH.DEHA

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
        rd1 = get_running_dhasa_for_given_date(
            current_jd,
            jd_at_dob,
            place,
            dhasa_level_index=DLI,
            dhasa_method=_dhasa_method,
            divisional_chart_factor=dcf,
            chart_method=chart_method,
            dhasa_duration_type=dd,
        )
        for row in rd1:
            lords, ds, de = row
            print([utils.RAASI_LIST[lord] for lord in lords], ds, de)
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        _dhasa_cycles = 1 if _dhasa_method == const.DRIG_TYPE.PVR_PAPER else 2
        ad = get_dhasa_antardhasa(
            jd_at_dob,
            place,
            dhasa_level_index=DLI,
            dhasa_method=_dhasa_method,
            divisional_chart_factor=dcf,
            chart_method=chart_method,
            dhasa_duration_type=dd,
        )
        if DLI <= const.MAHA_DHASA_DEPTH.ANTARA:
            for row in ad:
                lords, ds, dur = row
                print([utils.RAASI_LIST[lord] for lord in lords], ds, dur)
            exit()
        rd2 = utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd,
            ad,
            DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=_dhasa_cycles,
        )
        for row in rd2:
            lords, ds, de = row
            print([utils.RAASI_LIST[lord] for lord in lords], ds, de)
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chapter_21_tests()
