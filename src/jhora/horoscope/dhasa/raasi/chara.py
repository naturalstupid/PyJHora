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

"""
    1=> KN Rao method
    2=> Parasara/PVN Rao Method - from https://vedicastrologer.org/articles/pp_chara_dasa.pdf
    3=> Raghava Bhatta method from https://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html
"""
chara_method = 1
_dhasa_cycles = 2
one_year_days = const.sidereal_year

# ─────────────────────────────────────────────────────────────────────────────
# NEW: Iranganti / RB–NS sets & helpers (used by Method=3,4) and MindSutra (5)
# Sources: Iranganti's booklet (Phalita Daśās → Chara Daśā); RB–NS note (Shanmukha)
# ─────────────────────────────────────────────────────────────────────────────

OJAPADA_SIGNS = {
    const.ARIES, const.TAURUS, const.GEMINI, const.LIBRA, const.SCORPIO, const.SAGITTARIUS
}
SAMAPADA_SIGNS = {
    const.CANCER, const.LEO, const.VIRGO, const.CAPRICORN, const.AQUARIUS, const.PISCES
}


def _lord_of(sign, planet_positions):
    # Classical sign lords in these Chara rules (Sc=Mars, Aq=Saturn; nodes not used)
    if sign == const.SCORPIO:
        return const.MARS_ID
    if sign == const.AQUARIUS:
        return const.SATURN_ID
    return const.house_owners[sign]


def _dhasa_progression_iranganti_m1_male(planet_positions):
    asc = planet_positions[0][1][0]
    ninth = (asc + const.HOUSE_9) % 12
    is_forward = ninth in OJAPADA_SIGNS
    return [(asc + (i if is_forward else -i)) % 12 for i in range(12)]


def _dhasa_duration_iranganti_m1_male(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    if sign in OJAPADA_SIGNS:
        count = ((lord_house - sign) % 12) + 1
    else:
        count = ((sign - lord_house) % 12) + 1
    years = count - 1
    st = const.house_strengths_of_planets[lord][lord_house]
    if st == const._EXALTED_UCCHAM:
        years += 1
    elif st == const._DEBILITATED_NEECHAM:
        years -= 1
    if years <= 0:
        years = 12
    return years


def _dual_block(start, forward=True):
    """
    Dual trinal blocks:
      forward : [a, a+4, a-4] and anchor a := a+1  (odd parent)
      reverse : [a, a-4, a+4] and anchor a := a-1  (even parent)
    """
    out = []
    a = start % 12
    if forward:
        for _ in range(4):
            out.extend([a, (a + 4) % 12, (a - 4) % 12])
            a = (a + 1) % 12
    else:
        for _ in range(4):
            out.extend([a, (a - 4) % 12, (a + 4) % 12])
            a = (a - 1) % 12
    return out


def _padakrama_list_from_parent(parent_sign):
    """
    Rangacharya / RB–NS Antardaśā padakrama with direction set by the PARENT SIGN's parity.
      - Movable: contiguous ±1
      - Fixed  : every‑6th ±5 (0‑based)
      - Dual   : trinal blocks (forward/reverse)
    """
    P = parent_sign % 12
    odd = P in const.odd_signs

    if P in const.movable_signs:
        step = 1 if odd else -1
        return [(P + step * i) % 12 for i in range(12)]

    if P in const.fixed_signs:
        step = 5 if odd else -5
        return [(P + step * i) % 12 for i in range(12)]

    return _dual_block(P, forward=odd)


def _dhasa_progression_iranganti_m2_male(planet_positions):
    asc = planet_positions[0][1][0]
    odd = asc in const.odd_signs
    if asc in const.movable_signs:
        step = 1 if odd else -1
        return [(asc + step * i) % 12 for i in range(12)]
    if asc in const.fixed_signs:
        step = 5 if odd else -5
        return [(asc + step * i) % 12 for i in range(12)]
    return _dual_block(asc, forward=odd)


def _dhasa_duration_iranganti_m2_male(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    forward = lord_house in const.odd_signs
    count = ((sign - lord_house) % 12) + 1 if forward else ((lord_house - sign) % 12) + 1
    years = count - 1
    if years <= 0:
        years = 12
    return years


def _dhasa_progression_iranganti_female(planet_positions):
    asc = planet_positions[0][1][0]
    odd = asc in const.odd_signs
    start = (asc + 3) % 12 if odd else (asc - 3) % 12
    if asc in const.movable_signs:
        step = 1 if odd else -1
        return [(start + step * i) % 12 for i in range(12)]
    if asc in const.fixed_signs:
        step = 5 if odd else -5
        return [(start + step * i) % 12 for i in range(12)]
    return _dual_block(start, forward=odd)


def _dhasa_duration_iranganti_female(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    if lord_house == (sign + const.HOUSE_7) % 12:
        return 10
    forward = sign in const.odd_signs
    count = ((sign - lord_house) % 12) + 1 if forward else ((lord_house - sign) % 12) + 1
    years = count - 1
    if years <= 0:
        years = 12
    return years


# Antardaśā (Iranganti/RB–NS): parent-sign padakrama; 12 parts; equal split
def _antardhasa_iranganti(parent_sign):
    return _padakrama_list_from_parent(parent_sign)


def _dhasa_progression_mindsutra(planet_positions, gender):
    asc = planet_positions[0][1][0]
    odd = asc in const.odd_signs
    start = asc if gender == 0 else ((asc + 3) % 12 if odd else (asc - 3) % 12)

    seq = [start]
    seen = {start}
    trinal_master = [0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11]

    def _next_dual(cur):
        k = trinal_master.index(cur)
        return trinal_master[(k + 1) % 12]

    while len(seq) < 12:
        cur = seq[-1]
        if cur in const.movable_signs:
            nxt = (cur + 1) % 12
        elif cur in const.fixed_signs:
            nxt = (cur + 5) % 12
        else:
            nxt = _next_dual(cur)
        if nxt in seen:
            i = 0
            while nxt in seen and i < 12:
                nxt = (nxt + 1) % 12
                i += 1
        seq.append(nxt)
        seen.add(nxt)

    if not odd:
        tail = seq[1:]
        tail.reverse()
        seq = [start] + tail
    return seq


def _dhasa_duration_mindsutra(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    if lord_house == (sign + const.HOUSE_7) % 12:
        return 10
    forward = lord_house in const.odd_signs
    count = utils.count_rasis(lord_house, sign, 1) if forward else utils.count_rasis(lord_house, sign, -1)
    years = count - 1
    if years <= 0:
        years = 12
    return years


def _antardhasa_order_mindsutra(parent_sign, planet_positions):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(parent_sign, planet_positions)
    paka = p_to_h[lord]
    forward = paka in const.odd_signs
    order = [(paka + (i if forward else -i)) % 12 for i in range(12)]
    return order


def _antardhasa_rangacharya(parent_sign):
    """
    Parent-specific padakrama (matches JHora "Rangacharya").
    """
    P = parent_sign % 12
    if P in const.movable_signs:
        return [(P + i) % 12 for i in range(12)]
    if P in const.fixed_signs:
        return [(P + 5 * i) % 12 for i in range(12)]
    out = []
    for g in range(4):
        a = (P - g) % 12
        out.extend([a, (a - 4) % 12, (a + 4) % 12])
    return out


def _dhasa_duration_knrao_method(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = utils.count_rasis(house_of_lord, sign) if sign in const.even_footed_signs else utils.count_rasis(sign, house_of_lord)
    dhasa_period -= 1
    if dhasa_period <= 0:
        dhasa_period = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM:
        dhasa_period += 1
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEBILITATED_NEECHAM:
        dhasa_period -= 1
    return dhasa_period


def _dhasa_duration_pvnrao_method(planet_positions, sign):
    """Not fully implemented yet."""
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)

    if sign == const.SCORPIO:
        if p_to_h[const.MARS_ID] == sign and p_to_h[const.KETU_ID] == sign:
            dhasa_period = 12
            return dhasa_period
        elif p_to_h[const.MARS_ID] == sign and p_to_h[const.KETU_ID] != sign:
            house_of_lord = p_to_h[const.KETU_ID]
        elif p_to_h[const.KETU_ID] == sign and p_to_h[const.MARS_ID] != sign:
            house_of_lord = p_to_h[const.MARS_ID]
        else:
            lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
            house_of_lord = p_to_h[lord_of_sign]
    elif sign == const.AQUARIUS:
        if p_to_h[const.SATURN_ID] == sign and p_to_h[const.RAHU_ID] == sign:
            dhasa_period = 12
            return dhasa_period
        elif p_to_h[const.SATURN_ID] == sign and p_to_h[const.RAHU_ID] != sign:
            house_of_lord = p_to_h[const.RAHU_ID]
        elif p_to_h[const.RAHU_ID] == sign and p_to_h[const.SATURN_ID] != sign:
            house_of_lord = p_to_h[const.SATURN_ID]
        else:
            lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
            house_of_lord = p_to_h[lord_of_sign]
    else:
        lord_of_sign = const.house_owners[sign]
        house_of_lord = p_to_h[lord_of_sign]

    dhasa_period = 0
    if sign in const.even_footed_signs:
        if house_of_lord < sign:
            dhasa_period = sign + 1 - house_of_lord
        else:
            dhasa_period = sign + 13 - house_of_lord
    else:
        if house_of_lord < sign:
            dhasa_period = house_of_lord + 13 - sign
        else:
            dhasa_period = house_of_lord + 1 - sign
    dhasa_period -= 1
    if dhasa_period <= 0:
        dhasa_period = 12
    return dhasa_period


def _dhasa_duration(planet_positions, sign):
    return _dhasa_duration_knrao_method(planet_positions, sign)


""" CHARA METHODS 2 and 3  - Logic not yet implemented """
def _antardhasa(dhasas, method=1):
    _antardhasas = dhasas[1:] + [dhasas[0]] if method == 1 else dhasas
    return _antardhasas


def _dhasa_progression_pvnrao_method(planet_positions):
    sun_house = planet_positions[1][1][0]
    sun_house_lord = house.house_owner_from_planet_positions(planet_positions, sun_house)
    asc_house = planet_positions[0][1][0]
    asc_house_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    sh = house.stronger_planet_from_planet_positions(planet_positions, sun_house_lord, asc_house_lord)
    seed_house = asc_house if sh == asc_house_lord else sun_house
    moon_house = planet_positions[2][1][0]
    moon_house_lord = house.house_owner_from_planet_positions(planet_positions, moon_house)
    stronger_lord = house.stronger_planet_from_planet_positions(planet_positions, sh, moon_house_lord)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    if moon_house_lord == stronger_lord:
        seed_house = moon_house
    ninth_house = (seed_house + 8) % 12
    _dhasa_progression = [(h + seed_house) % 12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        _dhasa_progression = [(seed_house + 12 - h) % 12 for h in range(12)]
    return _dhasa_progression


def _dhasa_progression_knrao_method(planet_positions):
    asc_house = planet_positions[0][1][0]
    seed_house = asc_house
    ninth_house = (seed_house + const.HOUSE_9) % 12
    _dhasa_progression = [(h + seed_house) % 12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        _dhasa_progression = [(seed_house + 12 - h) % 12 for h in range(12)]
    return _dhasa_progression


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    chara_method=2,
    gender=0,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Chara Daśā (sign-based), depth-enabled.
    """
    global one_year_days

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)

    one_year_days = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    if chara_method == const.CHARA_TYPE.PVN_RAO:
        dhasa_progression = _dhasa_progression_pvnrao_method(planet_positions)
        duration_func = _dhasa_duration_pvnrao_method
        cycles = 2
        antardhasa_method = 1
        antardhasa_function = None
    elif chara_method == const.CHARA_TYPE.KN_RAO:
        dhasa_progression = _dhasa_progression_knrao_method(planet_positions)
        duration_func = _dhasa_duration_knrao_method
        cycles = 1
        antardhasa_method = 2
        antardhasa_function = None
    elif chara_method == const.CHARA_TYPE.IRANGATTI_MALE1:
        if gender == 0:
            dhasa_progression = _dhasa_progression_iranganti_m1_male(planet_positions)
            duration_func = _dhasa_duration_iranganti_m1_male
        else:
            dhasa_progression = _dhasa_progression_iranganti_female(planet_positions)
            duration_func = _dhasa_duration_iranganti_female
        cycles = 1
        antardhasa_method = None
        antardhasa_function = _antardhasa_iranganti
    elif chara_method == const.CHARA_TYPE.IRANGATTI_MALE2:
        if gender == 0:
            dhasa_progression = _dhasa_progression_iranganti_m2_male(planet_positions)
            duration_func = _dhasa_duration_iranganti_m2_male
        else:
            dhasa_progression = _dhasa_progression_iranganti_female(planet_positions)
            duration_func = _dhasa_duration_iranganti_female
        cycles = 1
        antardhasa_method = None
        antardhasa_function = _antardhasa_iranganti
    elif chara_method == const.CHARA_TYPE.MIND_SUTRA:
        dhasa_progression = _dhasa_progression_mindsutra(planet_positions, gender)
        duration_func = _dhasa_duration_mindsutra
        cycles = 1
        antardhasa_method = None
        antardhasa_function = None
    else:
        raise ValueError("Unsupported chara_method. Use 1 (PVN), 2 (KNRao), 3/4 (Iranganti), or 5 (MindSutra).")

    bhukthis_global = _antardhasa(dhasa_progression, method=antardhasa_method) if antardhasa_method is not None else None

    def _append(out, tpl):
        out.append(tpl)

    def _child_order(parent_sign, parent_depth):
        if antardhasa_function is not None and parent_depth == 1:
            return antardhasa_function(parent_sign)
        if chara_method == const.CHARA_TYPE.MIND_SUTRA and parent_depth == 1:
            return _antardhasa_order_mindsutra(parent_sign, planet_positions)
        if bhukthis_global is not None:
            return bhukthis_global
        return _antardhasa(dhasa_progression, method=2)

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        child_order = _child_order(parent_sign, len(prefix))
        child_unrounded = parent_years / 12.0
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for child_sign in child_order:
                _recurse(level + 1, child_sign, jd_cursor, child_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_unrounded * one_year_days
        else:
            for child_sign in child_order:
                start_str = utils.jd_to_gregorian(jd_cursor)
                dur_ret = round(child_unrounded, dhasa_level_index + 1) if round_duration else child_unrounded
                _append(out_rows, (prefix + (child_sign,), start_str, dur_ret))
                jd_cursor += child_unrounded * one_year_days

    rows = []
    jd_cur = jd_at_dob

    for cycle_ix in range(cycles):
        for lord in dhasa_progression:
            dd = float(duration_func(planet_positions, lord))
            if chara_method == const.CHARA_TYPE.PVN_RAO and cycle_ix == 1:
                dd = 12.0 - dd

            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                start_str = utils.jd_to_gregorian(jd_cur)
                dur_ret = round(dd, dhasa_level_index + 1) if round_duration else dd
                _append(rows, ((lord,), start_str, dur_ret))
                jd_cur += dd * one_year_days
                continue

            child_order = _child_order(lord, 1)

            if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                ddb = dd / 12.0
                jd_b_ini = jd_cur
                for bhukthi in child_order:
                    start_str = utils.jd_to_gregorian(jd_b_ini)
                    dur_ret = round(ddb, dhasa_level_index + 1) if round_duration else ddb
                    _append(rows, ((lord, bhukthi), start_str, dur_ret))
                    jd_b_ini += ddb * one_year_days
                jd_cur += dd * one_year_days
                continue

            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=lord,
                parent_start_jd=jd_cur,
                parent_years=dd,
                prefix=(lord,),
                out_rows=rows,
            )
            jd_cur += dd * one_year_days

    return rows


def chara_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    chara_method: int = const.CHARA_TYPE.KN_RAO,
    gender: int = 0,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Chara — return ONLY the immediate (p -> p+1) children inside the given parent span.
    """
    global one_year_days

    one_year_days = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")
    parent_sign = path[-1]
    parent_depth = len(path)

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
        end_jd = start_jd + parent_years * one_year_days
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / one_year_days

    if end_jd <= start_jd:
        return []

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    if chara_method == const.CHARA_TYPE.PVN_RAO:
        dhasa_progression = _dhasa_progression_pvnrao_method(planet_positions)
        antardhasa_method = 1
        antardhasa_function = None
    elif chara_method == const.CHARA_TYPE.KN_RAO:
        dhasa_progression = _dhasa_progression_knrao_method(planet_positions)
        antardhasa_method = 2
        antardhasa_function = None
    elif chara_method == const.CHARA_TYPE.IRANGATTI_MALE1:
        dhasa_progression = _dhasa_progression_iranganti_m1_male(planet_positions) if gender == 0 else _dhasa_progression_iranganti_female(planet_positions)
        antardhasa_method = None
        antardhasa_function = _antardhasa_iranganti
    elif chara_method == const.CHARA_TYPE.IRANGATTI_MALE2:
        dhasa_progression = _dhasa_progression_iranganti_m2_male(planet_positions) if gender == 0 else _dhasa_progression_iranganti_female(planet_positions)
        antardhasa_method = None
        antardhasa_function = _antardhasa_iranganti
    elif chara_method == const.CHARA_TYPE.MIND_SUTRA:
        dhasa_progression = _dhasa_progression_mindsutra(planet_positions, gender)
        antardhasa_method = None
        antardhasa_function = None
    else:
        raise ValueError("Unsupported chara_method (use 1..5).")

    bhukthis_global = None
    if antardhasa_method is not None:
        bhukthis_global = _antardhasa(dhasa_progression, method=antardhasa_method)

    if antardhasa_function is not None and parent_depth == 1:
        bhukthis_order = antardhasa_function(parent_sign)
    elif chara_method == const.CHARA_TYPE.MIND_SUTRA and parent_depth == 1:
        bhukthis_order = _antardhasa_order_mindsutra(parent_sign, planet_positions)
    else:
        if bhukthis_global is None:
            bhukthis_global = _antardhasa(dhasa_progression, method=2)
        bhukthis_order = bhukthis_global

    child_years = parent_years / 12.0
    children = []
    cursor = start_jd
    for idx, child_sign in enumerate(bhukthis_order):
        if idx == 11:
            child_end = end_jd
        else:
            child_end = cursor + child_years * one_year_days
        children.append([
            path + (child_sign,),
            _jd_to_tuple(cursor),
            _jd_to_tuple(child_end),
        ])
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
    chara_method: int = const.CHARA_TYPE.KN_RAO,
    gender: int = 0,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Chara — narrow Mahā -> … -> target depth and return the full running ladder.
    """
    global one_year_days

    one_year_days = drik.dhasa_year_duration(
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
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds)]
        if not filtered:
            return []
        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _ in filtered:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    running_all = []

    maha_rows = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        chara_method=chara_method,
        gender=gender,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )
    maha_for_utils = [(_as_tuple_lords(row[0]), row[1]) for row in maha_rows]

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_as_tuple_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = chara_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            chara_method=chara_method,
            gender=gender,
            divisional_chart_factor=divisional_chart_factor,
            years=years,
            months=months,
            sixty_hours=sixty_hours,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )
        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            break

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            running = [_as_tuple_lords(rdk[0]), rdk[1], rdk[2]]

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
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
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
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chara_dhasa_test()
    exit()
