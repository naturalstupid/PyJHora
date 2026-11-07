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
Drig Dasa

Two selectable methods (const.DRIG_TYPE):

PVR_BOOK: Mahadasa seed signs are the 9th, 10th and 11th houses from
Lagna, each followed by its own aspected kendra signs (house.aspected_
kendras_of_raasi), giving a 12-sign Mahadasa sequence, single cycle.
Each Mahadasa's duration is computed the same way as Narayana dasa
(narayana._dhasa_duration). Antardasa order (and every level below
Mahadasa) uses narayana._narayana_antardhasa(parent_sign), applied
recursively, with an equal 12-way duration split at every level.
Ref: PVR's book, Ch. 21 ("Drig Dasa"). The book does not define its own
antardasa rule; Narayana Dasa's antardasa is used as a working
assumption for this method.

PVR_PAPER: Mahadasa seed signs are the 9th, 10th and 11th houses from
Lagna, each followed by the 3 signs it aspects (house.raasi_drishti_of_
the_raasi), ordered nearest-first in the direction determined by the
seed sign's classification (movable/fixed and Vishama/Sama Pada), with
ties broken toward the sign sharing the seed's lord. Each Mahadasa's
duration is fixed by modality: movable = 7 years, fixed = 8 years, dual
= 9 years, for a single 12-sign cycle (no second cycle). Antardasa
order (and every level below Mahadasa) is seeded from the stronger of
the parent sign and its 7th, rolling forward (odd parent sign) or
backward (even parent sign) -- movable signs step consecutively, fixed
signs step every 6th house, dual signs step in three trinal (1-5-9)
groups -- applied recursively, with an equal 12-way duration split at
every level.
Ref: "Drig Dasa of Parasara" - PVR.

drig_dhasa() / drig_dhasa_bhukthi() are legacy entry points, retained
for backward compatibility. Both delegate internally to
get_dhasa_antardhasa(). drig_dhasa()'s `place` argument is optional
(falls back to naive average-year JD arithmetic if omitted); its
`planet_positions` argument, if given, is used as-is rather than being
recomputed from dob/tob.

Release History:
    V5.0 - Refactored to match JHora/PVR_Paper and PVR_Book Examples
"""
from typing import List, Tuple, Sequence, Optional, Union

from jhora import const, utils
from jhora.horoscope.chart import house, charts
from jhora.horoscope.dhasa.raasi import narayana
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

_DAYS_IN_YEAR = float(const.sidereal_year)
_ROUND_NDIGITS = int(getattr(const, "DHASA_DURATION_ROUNDING_TO", 2))

_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30


def _set_year_duration(jd: float, place, dhasa_duration_type=None, savana_year_method=None) -> float:
    """
    Sets the module-level _DAYS_IN_YEAR used for the naive-fallback
    estimate and sub-day interpolation. If place is None, uses the
    sidereal year constant directly. If dhasa_duration_type is given,
    also sets const.dhasa_year_duration_default.
    """
    global _DAYS_IN_YEAR
    if place is None:
        _DAYS_IN_YEAR = float(const.sidereal_year)
        return _DAYS_IN_YEAR
    if dhasa_duration_type is not None:
        const.dhasa_year_duration_default = dhasa_duration_type
    _DAYS_IN_YEAR = float(drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    ))
    return _DAYS_IN_YEAR


def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """
    Real dasa-period end JD, guarded by a naive average-year backstop.
    If place is None, returns the naive average-year estimate directly.
    """
    naive_end = start_jd + duration_in_years * _DAYS_IN_YEAR
    if place is None:
        return naive_end
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, duration_in_years)
    except Exception:
        return naive_end
    if real_end is None or real_end <= start_jd:
        return naive_end
    if abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end


def drig_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    chart_method=1,
    **kwargs,
):
    """
    Legacy entry point (dob, tob, place). Computes planet_positions
    internally (D-1 by default) and delegates to get_dhasa_antardhasa().
    dhasa_method defaults to const.DRIG_TYPE.PVR_BOOK.
    """
    jd = utils.julian_day_number(dob, tob)
    if dhasa_method is None:
        dhasa_method = const.DRIG_TYPE.PVR_BOOK

    rows = get_dhasa_antardhasa(
        dob,tob,
        place,
        dhasa_method=dhasa_method,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_level_index=int(dhasa_level_index),
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )

    return [
        (tuple(lords), start_tuple, dur)
        for lords, start_tuple, dur in rows
    ]


def drig_dhasa(
    planet_positions,
    dob,
    tob,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    *,
    place=None,
    dhasa_method=None,
    **kwargs,
):
    """
    Legacy entry point, retained for backward compatibility. Delegates
    to get_dhasa_antardhasa(). Uses the given planet_positions as-is
    (never recomputed); dob/tob anchor the Mahadasa start JD only.

    `place` is optional; if omitted, JD boundaries use naive average-
    sidereal-year arithmetic. dhasa_method defaults to
    const.DRIG_TYPE.PVR_BOOK.

    Note: antardasa-and-below for dhasa_method=PVR_BOOK uses
    narayana._narayana_antardhasa() (an explicitly-flagged working
    assumption per this module's docstring, since the book defines no
    antardasa rule of its own). For the PVR_PAPER antardasa stepping
    rule instead, pass dhasa_method=const.DRIG_TYPE.PVR_PAPER.
    """
    if dhasa_method is None:
        dhasa_method = const.DRIG_TYPE.PVR_BOOK

    jd = utils.julian_day_number(dob, tob)

    rows = get_dhasa_antardhasa(
        dob,tob,
        place,
        dhasa_method=dhasa_method,
        dhasa_level_index=int(dhasa_level_index),
        round_duration=round_duration,
        planet_positions=planet_positions,
        **kwargs,
    )

    return [
        (tuple(lords), start_tuple, dur)
        for lords, start_tuple, dur in rows
    ]


def _antardhasa_from_planet_positions(planet_positions, dhasa_lord):
    """
    Antardhasa Ref: Drig Dasa of Parasara - PVR
    Retained for backward compatibility / cross-checking. Mathematically
    identical to _paper_antardhasa_order() below.
    """
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


def _md_years_book(pp, sign: int) -> float:
    """Book: MD years computed like Narayana dasha (single cycle)."""
    return float(narayana._dhasa_duration(pp, sign))


# -----------------------------------------------------------------------------
# Antardasa order
# -----------------------------------------------------------------------------
def _paper_antardhasa_order(parent_sign: int, pp) -> List[int]:
    """
    Seed = stronger of parent_sign / its 7th. Direction = forward (odd
    parent) or backward (even parent). Movable signs step consecutively;
    fixed signs step every 6th house; dual signs step in three trinal
    (1-5-9) groups of 4, with the group-starting offsets (+5th, +9th)
    also taken in the resolved direction.
    """
    opp = _mod12(parent_sign + const.HOUSE_7)
    seed = int(house.stronger_rasi_from_planet_positions(pp, parent_sign, opp)) % 12
    direction = 1 if _is_odd_sign(parent_sign) else -1

    if _is_movable(parent_sign):
        return [_mod12(seed + direction * i) for i in range(12)]

    if _is_fixed(parent_sign):
        step = 5 * direction
        return [_mod12(seed + step * i) for i in range(12)]

    step3 = 3 * direction
    bases = [seed, _mod12(seed + direction * const.HOUSE_5), _mod12(seed + direction * const.HOUSE_9)]
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
# Single shared children-boundary engine (levels below Mahadasa)
# -----------------------------------------------------------------------------
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, n=12):
    """ Splits a parent span into n equal children using real dasa-period
    boundaries; the last child is clamped exactly to parent_end_jd. """
    child_years = parent_years / n
    parent_real_days = parent_end_jd - parent_start_jd
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        if is_last:
            end_jd = parent_end_jd
        elif (child_years * _DAYS_IN_YEAR) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / n
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out


def _get_children_jds(path_so_far, parent_sign, parent_start_jd, parent_end_jd, parent_years,
                       place, pp, dhasa_method):
    """
    Returns the 12 children of parent_sign (one level below parent_sign,
    which may itself be a Mahadasa sign or any deeper antardasa sign):
        list of (child_path, child_sign, child_start_jd, child_end_jd, child_years)
    """
    order = _children_order(parent_sign, pp, dhasa_method)
    child_years = parent_years / 12.0
    bounds = _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, n=12)

    out = []
    for child_sign, (c_start, c_end) in zip(order, bounds):
        out.append((path_so_far + (child_sign,), child_sign, c_start, c_end, child_years))
    return out


# -----------------------------------------------------------------------------
# Mahadasa generator (shared by all three public entry points)
# -----------------------------------------------------------------------------
def _generate_md_periods(pp, jd_at_dob, place, dhasa_method, stop_at_jd=None):
    """
    Yields Mahadasa periods (md_sign, md_start_jd, md_end_jd, md_years) for
    the full md_seq, one single 12-sign cycle (both PVR_PAPER and
    PVR_BOOK). If stop_at_jd is given, generation stops once a Mahadasa
    containing stop_at_jd has been yielded.
    """
    chart = _chart_from_pp(pp)
    lagna = _lagna_sign_from_pp(pp)
    md_seq = _md_sequence(lagna, dhasa_method, chart, pp)

    jd_cursor = jd_at_dob

    for md_sign in md_seq:
        if dhasa_method == const.DRIG_TYPE.PVR_BOOK:
            md_years = _md_years_book(pp, md_sign)
        else:
            md_years = _md_years_paper(md_sign)

        md_start_jd = jd_cursor
        md_end_jd = _bounded_end_jd(md_start_jd, place, md_years)

        yield md_sign, md_start_jd, md_end_jd, md_years

        jd_cursor = md_end_jd
        if stop_at_jd is not None and md_start_jd <= stop_at_jd < md_end_jd:
            return


# =============================================================================
# PUBLIC 1: get_dhasa_antardhasa
# =============================================================================
def get_dhasa_antardhasa(dob,tob,
                         place=None,
                         dhasa_method=None,
                         divisional_chart_factor: int = 1,
                         chart_method: int = 1,
                         dhasa_duration_type=None,
                         savana_year_method=None,
                         planet_positions=None,
                         **kwargs) -> List[Tuple]:
    """
    Returns rows:
      (lords_tuple, start_tuple(Y,M,D,fh), duration_years)

    `place` is optional; if omitted, JD boundaries use naive average-
    sidereal-year arithmetic instead of real dasa-period boundaries.

    `planet_positions`, if given, is used as-is instead of being
    recomputed from (jd, place, divisional_chart_factor, chart_method).

    kwargs:
      dhasa_level_index: 1..6 (default const.MAHA_DHASA_DEPTH.ANTARA)
      round_duration: bool (default True)
      any remaining kwargs passed to charts.divisional_chart(...) (only
      used when planet_positions is not given)
    """
    jd = utils.julian_day_number(dob,tob)
    if dhasa_method is None: dhasa_method = const.DRIG_TYPE_DEFAULT
    _set_year_duration(jd, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    dhasa_level_index = int(kwargs.pop("dhasa_level_index", int(const.MAHA_DHASA_DEPTH.ANTARA)))
    round_duration = bool(kwargs.pop("round_duration", True))
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")

    if planet_positions is not None:
        pp = planet_positions
    else:
        pp = _pp_upto_ketu(jd, place, divisional_chart_factor, chart_method=chart_method, **kwargs)

    rows: List[Tuple] = []

    def _recurse(path_so_far, parent_sign, parent_start_jd, parent_end_jd, parent_years, current_depth):
        children = _get_children_jds(
            path_so_far, parent_sign, parent_start_jd, parent_end_jd, parent_years,
            place, pp, dhasa_method,
        )
        for child_path, child_sign, c_start, c_end, c_years in children:
            if current_depth == dhasa_level_index:
                _append_row(rows, child_path, c_start, c_years, round_duration)
            else:
                _recurse(child_path, child_sign, c_start, c_end, c_years, current_depth + 1)

    for md_sign, md_start_jd, md_end_jd, md_years in _generate_md_periods(pp, jd, place, dhasa_method):
        if dhasa_level_index == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
            _append_row(rows, [md_sign], md_start_jd, md_years, round_duration)
        else:
            _recurse((md_sign,), md_sign, md_start_jd, md_end_jd, md_years, current_depth=2)

    return rows


# =============================================================================
# PUBLIC 2: drig_immediate_children
# =============================================================================
def get_immediate_children(
    parent_lords: Union[int, Sequence[int]],
    parent_start: Tuple[int, int, int, float],
    parent_duration: Optional[float] = None,
    parent_end: Optional[Tuple[int, int, int, float]] = None,
    *,
    jd_at_dob: float,
    place,
    dhasa_method=None,
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
    if dhasa_method is None: dhasa_method = const.DRIG_TYPE_DEFAULT
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
        end_jd = _bounded_end_jd(start_jd, place, float(parent_duration))
    else:
        end_jd = _tuple_to_jd(parent_end)

    if end_jd <= start_jd:
        return []

    pp_birth = _pp_upto_ketu(jd_at_dob, place, divisional_chart_factor, chart_method=chart_method, **kwargs)
    parent_years = (end_jd - start_jd) / _DAYS_IN_YEAR

    children = _get_children_jds(path, parent_sign, start_jd, end_jd, parent_years, place, pp_birth, dhasa_method)

    return [
        [child_path, _jd_to_tuple(c_start), _jd_to_tuple(c_end)]
        for child_path, _child_sign, c_start, c_end, _c_years in children
    ]


# =============================================================================
# PUBLIC 3: get_running_dhasa_for_given_date
# =============================================================================
def get_running_dhasa_for_given_date(
    current_jd: float,
    jd_at_dob: float,
    place,
    dhasa_method=None,
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
    if dhasa_method is None: dhasa_method = const.DRIG_TYPE_DEFAULT
    _set_year_duration(jd_at_dob, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    target_depth = max(1, min(6, int(dhasa_level_index)))

    pp = _pp_upto_ketu(jd_at_dob, place, divisional_chart_factor, chart_method=chart_method, **kwargs)

    located = None
    last_seen = None
    for md_sign, md_start_jd, md_end_jd, md_years in _generate_md_periods(
        pp, jd_at_dob, place, dhasa_method, stop_at_jd=current_jd
    ):
        last_seen = (md_sign, md_start_jd, md_end_jd, md_years)
        if md_start_jd <= current_jd < md_end_jd:
            located = last_seen
    if located is None:
        located = last_seen
    if located is None:
        return []

    parent_sign, parent_start_jd, parent_end_jd, parent_years = located
    parent_path = (parent_sign,)
    ladder = [[list(parent_path), _jd_to_tuple(parent_start_jd), _jd_to_tuple(parent_end_jd)]]

    if target_depth == 1:
        return ladder

    for _depth in range(2, target_depth + 1):
        children = _get_children_jds(
            parent_path, parent_sign, parent_start_jd, parent_end_jd, parent_years,
            place, pp, dhasa_method,
        )
        chosen = None
        for child_path, child_sign, c_start, c_end, c_years in children:
            if c_start <= current_jd < c_end:
                chosen = (child_path, child_sign, c_start, c_end, c_years)
                break
        if chosen is None:
            chosen = children[-1]

        parent_path, parent_sign, parent_start_jd, parent_end_jd, parent_years = chosen
        ladder.append([list(parent_path), _jd_to_tuple(parent_start_jd), _jd_to_tuple(parent_end_jd)])

    return ladder


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (1998,11,9)
    hh, mm, ss = (15,29,45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    _dhasa_method = const.DRIG_TYPE.PVR_PAPER
    dcf = 1
    chart_method = 2
    print("Drig Dhasa Method", "PVR_BOOK" if _dhasa_method == const.DRIG_TYPE.PVR_BOOK else "PVR_PAPER", "div=", dcf, "cm=", chart_method)
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
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
            lords, (y1,m1,d1,fh1), (y2,m2,d2,fh2) = row
            print([utils.RAASI_SHORT_LIST[lord] for lord in lords], 
                f"{y1}-{m1}-{d1} {utils.to_dms(fh1)}", 
                f"{y2}-{m2}-{d2} {utils.to_dms(fh2)}")
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob,tob,
            place,
            dhasa_level_index=DLI,
            dhasa_method=_dhasa_method,
            divisional_chart_factor=dcf,
            chart_method=chart_method,
            dhasa_duration_type=dd,
        )
        if DLI <= const.MAHA_DHASA_DEPTH.ANTARA:
            for row in ad:
                lords, (y1,m1,d1,fh1), (y2,m2,d2,fh2) = row
                print([utils.RAASI_SHORT_LIST[lord] for lord in lords], 
                    f"{y1}-{m1}-{d1} {utils.to_dms(fh1)}", 
                    f"{y2}-{m2}-{d2} {utils.to_dms(fh2)}")
        rd2 = utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd,
            ad,
            DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=1,
        )
        for row in rd2:
            lords, (y1,m1,d1,fh1), (y2,m2,d2,fh2) = row
            print([utils.RAASI_SHORT_LIST[lord] for lord in lords], 
                  f"{y1}-{m1}-{d1} {utils.to_dms(fh1)}", 
                  f"{y2}-{m2}-{d2} {utils.to_dms(fh2)}")
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chapter_21_tests()
