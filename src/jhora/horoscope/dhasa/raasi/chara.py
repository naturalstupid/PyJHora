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
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

"""
    Chara Dasa
        1=> KN Rao method
        2=> Parasara/PVN Rao Method - from https://vedicastrologer.org/articles/pp_chara_dasa.pdf
        3=> Raghava Bhatta method from https://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html
        4=> Mind Sutra method from same Ref3.

    A rasi-based dasa with 5 selectable calculation methods, each with its
    own Mahadasa seed/progression, duration formula, and antardasa rule:
        KN_RAO, PVN_RAO: Parasara-style, seeded at Lagna.
        IRANGATTI_MALE1, IRANGATTI_MALE2, IRANGATTI_FEMALE: Sri Iranganti
            Rangacharya's method (Jaimini Sutramritam), per Shanmukha's
            reference summary ("Chara Dasa (Raghava Bhatta - Nrisimha
            Suri method)").
        MIND_SUTRA_MALE, MIND_SUTRA_FEMALE: the MindSutra.com software's
            own variant of the same Rangacharya-derived method, per the
            same reference summary.

    Rangacharya (Iranganti) method, common rules:
        - Chara Dasa always starts from Lagna.
        - For female charts, the starting dasa sign is the 4th sign from
          Lagna, zodiacally if Lagna is odd, or anti-zodiacally if Lagna
          is even (equivalently, the 10th sign zodiacally).
        - For both male and female charts, the Mahadasa sequence runs
          zodiacally or anti-zodiacally according to whether Lagna itself
          is odd or even, respectively -- not the oddity of the starting
          dasa sign.
        - Mahadasa signs follow Padakrama order, keyed off Lagna's own
          modality: movable signs step by 1, fixed signs step by 5 (every
          6th sign), dual signs step through trines (1st, 5th, 9th, 2nd,
          6th, 10th, ... from Lagna -- after the 9th, the next sign is the
          2nd from Lagna, not the 10th, unlike Narayana Dasa).
        - If a sign's lord occupies that sign itself, its Mahadasa
          duration is 12 years. Scorpio's lord is taken as Mars and
          Aquarius's as Saturn (Rahu/Ketu are not used as sign lords
          here); exaltation/debilitation of the lord is not considered.
        - Male duration: count from the lord's own occupied sign to the
          dasa sign, both signs inclusive, zodiacally if the lord's
          occupied sign is odd, anti-zodiacally if even.
        - Female duration: the same count, but the direction is instead
          keyed off the dasa sign's own oddity (zodiacal if the dasa sign
          is odd, anti-zodiacal if even), and if the lord is 7th from the
          dasa sign, the duration is 10 years.
        - Antardasa (both genders): computed by treating the Mahadasa
          sign as a fresh Lagna and applying the same Padakrama rule,
          keyed off that sign's own modality. There are always 12
          antardasas, each of duration (Mahadasa years / 12).

    IRANGATTI_MALE2 implements the Male rule above directly. IRANGATTI_
    FEMALE implements the Female rule above directly; both are confirmed
    matching real JHora output, including running-dasa lookups, and are
    left as-is.

    MindSutra method (per the same reference summary):
        - Duration: the same rule as Rangacharya's Male duration
          (direction from the lord's own occupied-sign oddity), but
          stated to apply identically for both male and female charts;
          the 7th-from-dasa-sign -> 10 years and own-sign -> 12 years
          special cases both apply.
        - Antardasa: starts from the sign occupied by the dasa lord
          (Paka), proceeding zodiacally or anti-zodiacally according to
          the oddity of that Paka sign, in plain sign order (Padakrama
          is explicitly NOT used here). The number of antardasas equals
          the Mahadasa's own duration in years (not always 12), and each
          antardasa is a fixed 1-year block; only Pratyantardasa and
          deeper levels revert to the common parent-duration/12 equal
          split.
    Release History:
        V5.0 - Refactored to match JHora for KN-Rao, PVN_RAO and Iranganti/Rangacharya Femaile chart
               Other methods not supported by JHora so not verified
"""
from jhora import const, utils
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik

_dhasa_cycles = 2
one_year_days = const.sidereal_year

# Sanity backstop (in days) against drik._get_dhasa_end_jd() returning a
# result far from the linear (duration * year_duration) estimate for a
# narrow band of small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# Threshold (in days) below which drik._get_dhasa_end_jd()'s solar-transit
# search is not reliable. This check is duration-triggered, re-evaluated
# fresh for every batch of children, regardless of level, chara_method, or
# which entry point is calling.
_SUB_DAY_DURATION_DAYS = 1.0


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, via
    drik._get_dhasa_end_jd(), falling back to plain linear
    (duration_years * one_year_days) arithmetic if that result is more
    than _SMALL_DURATION_BACKSTOP_DAYS away from the linear estimate.
    """
    end_jd = drik._get_dhasa_end_jd(
        start_jd=start_jd_local,
        place=place,
        total_dasa_years=duration_years,
    )

    expected_jd = start_jd_local + duration_years * one_year_days

    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd

    return end_jd


# Iranganti / Rangacharya sets and helpers, also used by MindSutra's
# antardasa rule. Source: Shanmukha's "Chara Dasa (Raghava Bhatta -
# Nrisimha Suri method)" reference summary.

OJAPADA_SIGNS = {
    const.ARIES, const.TAURUS, const.GEMINI, const.LIBRA, const.SCORPIO, const.SAGITTARIUS
}
SAMAPADA_SIGNS = {
    const.CANCER, const.LEO, const.VIRGO, const.CAPRICORN, const.AQUARIUS, const.PISCES
}


""" This _antardhasa() is added to ONLY  support yogardha dhasa but not used here """
def _antardhasa(dhasas, method=const.CHARA_TYPE.PVN_RAO):
    _antardhasas = dhasas[1:] + [dhasas[0]] if method == 1 else dhasas
    return _antardhasas


def _lord_of(sign, planet_positions):
    # Classical sign lords in these Chara rules (Sc=Mars, Aq=Saturn; nodes not used)
    if sign == const.SCORPIO:
        return const.MARS_ID
    if sign == const.AQUARIUS:
        return const.SATURN_ID
    return const.house_owners[sign]


def _dhasa_progression_iranganti_m1_male(planet_positions):
    """
    IRANGATTI_MALE1 Mahadasa progression: identical to IRANGATTI_MALE2 --
    the source describes a single Male progression rule (start at Lagna,
    Padakrama by Lagna's own modality, direction from Lagna's own
    oddity), not two variants. See module change log.
    """
    return _dhasa_progression_iranganti_m2_male(planet_positions)


def _dhasa_duration_iranganti_m1_male(planet_positions, sign):
    """
    IRANGATTI_MALE1 Mahadasa duration: identical to IRANGATTI_MALE2 --
    see _dhasa_progression_iranganti_m1_male() above.
    """
    return _dhasa_duration_iranganti_m2_male(planet_positions, sign)


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
    Rangacharya Antardasa padakrama with direction set by the PARENT
    SIGN's own oddity.
      - Movable: contiguous +/-1
      - Fixed  : every-6th +/-5 (0-based)
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


# Antardasa (Iranganti/Rangacharya): parent-sign padakrama; 12 parts; equal split
def _antardhasa_iranganti(parent_sign):
    return _padakrama_list_from_parent(parent_sign)


def _antardhasa_order_knrao(parent_sign):
    """
    KN Rao Method: Generates sub-periods ending at the parent sign.

    Forward (+1) starting at (parent + 1) for: Ar, Le, Li, Aq, Vi, Pi
    Backward (-1) starting at (parent - 1) for: Ta, Ge, Cn, Sc, Sg, Cp

    Assumes 0-indexed integers: 0=Aries, 1=Taurus, ..., 11=Pisces.
    """
    # Exact signs that progress forward in KN Rao's Antardasha system
    # Aries(0), Leo(4), Virgo(5), Libra(6), Aquarius(10), Pisces(11)
    forward_signs = {0, 4, 5, 6, 10, 11}

    if parent_sign in forward_signs:
        # Move forward from the next sign, landing on the parent sign last
        return [(parent_sign + 1 + h) % 12 for h in range(12)]
    else:
        # Move backward from the previous sign, landing on the parent sign last
        return [(parent_sign - 1 - h) % 12 for h in range(12)]


def _dhasa_progression_mindsutra(planet_positions, chara_method):
    """
    MindSutra Mahadasa progression: a single Padakrama pattern chosen
    once from the starting sign's own modality (movable/fixed/dual),
    applied uniformly for all 12 signs -- the same mechanism as
    _padakrama_list_from_parent(). The source describes no MindSutra-
    specific Mahadasa progression rule; this is a working assumption,
    not an explicit rule (see module change log).

    Starting sign: Lagna itself for Male; the 4th sign from Lagna
    (zodiacally if Lagna is odd, anti-zodiacally if even) for Female --
    the same starting-sign rule already used for IRANGATTI_FEMALE.
    """
    asc = planet_positions[0][1][0]
    odd = asc in const.odd_signs
    start = (
        asc if chara_method == const.CHARA_TYPE.MIND_SUTRA_MALE
        else ((asc + const.HOUSE_4) % 12 if odd else (asc - const.HOUSE_4) % 12)
    )
    forward = start in const.odd_signs

    if start in const.movable_signs:
        step = 1 if forward else -1
        return [(start + step * i) % 12 for i in range(12)]
    if start in const.fixed_signs:
        step = 5 if forward else -5
        return [(start + step * i) % 12 for i in range(12)]
    return _dual_block(start, forward=forward)


def _dhasa_duration_mindsutra(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]

    # Rule 4: If Lord is in the dasa sign itself -> 12 years
    if lord_house == sign:
        return 12

    # Rule 3: If Lord is 7th from dasa sign -> 10 years
    if lord_house == (sign + 6) % 12:  # Standardized 0-indexed 7th house step
        return 10

    # Rule 1 & 2: Odd/Even Sign direction tracking
    forward = lord_house in const.odd_signs

    # Count from Lord (Paka) to Dasha sign inclusive
    count = utils.count_rasis(lord_house, sign, direction=1 if forward else -1)

    years = count - 1
    if years <= 0:
        years = 12
    return years


def _antardhasa_order_mindsutra(parent_sign, planet_positions, dhasa_years):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(parent_sign, planet_positions)
    paka = p_to_h[lord]

    forward = paka in const.odd_signs

    # MindSutra Modification: The number of Antardashas MUST equal dhasa_years
    order = []
    for i in range(dhasa_years):
        if forward:
            next_sign = (paka + i) % 12
        else:
            next_sign = (paka - i) % 12
        order.append(next_sign)

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


def _lord_of_pvn(sign, planet_positions):
    """Get the stronger lord for a sign using built-in house methods."""
    if sign not in (const.SCORPIO, const.AQUARIUS):
        return const.house_owners[sign]

    if sign == const.SCORPIO:
        l1, l2 = const.MARS_ID, const.KETU_ID
    else:
        l1, l2 = const.SATURN_ID, const.RAHU_ID

    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    s1 = p_to_h.get(l1, -1)
    s2 = p_to_h.get(l2, -1)

    if s1 == sign and s2 != sign:
        return l2
    if s2 == sign and s1 != sign:
        return l1
    if s1 == sign and s2 == sign:
        return l1

    # Use the library's built-in stronger planet comparison
    stronger = house.stronger_planet_from_planet_positions(planet_positions, l1, l2)
    return l1 if stronger == l1 else l2


def _antardhasa_order_pvnrao(parent_sign, planet_positions):
    seventh_sign = (parent_sign + const.HOUSE_7) % 12

    # Use the library's built-in stronger rasi comparison
    stronger_rasi = house.stronger_rasi_from_planet_positions(planet_positions, parent_sign, seventh_sign)
    start_sign = parent_sign if stronger_rasi == parent_sign else seventh_sign

    ODD_SIGNS = {const.ARIES, const.GEMINI, const.LEO, const.LIBRA, const.SAGITTARIUS, const.AQUARIUS}
    forward = start_sign in ODD_SIGNS

    if start_sign in const.movable_signs:
        step = 1 if forward else -1
        return [(start_sign + step * i) % 12 for i in range(12)]
    elif start_sign in const.fixed_signs:
        step = 5 if forward else -5
        return [(start_sign + step * i) % 12 for i in range(12)]
    else:
        out = []
        step_kendra = 3 if forward else -3
        step_block = 4 if forward else -4
        for g in range(3):
            anchor = (start_sign + step_block * g) % 12
            out.extend([(anchor + step_kendra * i) % 12 for i in range(4)])
        return out


def _dhasa_duration_pvnrao_method(planet_positions, sign):
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


def _dhasa_progression_pvnrao_method(planet_positions):
    """
    Parasara PVR Method Mahadasa Order:
    Starts from Lagna (Ascendant) with direction determined by the 9th house.
    Only with this assumption dhasa progression matches with JHora V8.0 software
    Instead if we use PVR's paper: https://vedicastrologer.org/articles/pp_chara_dasa.pdf
    stronger lord calculation does not match with JHora V8.0 software.
    Hence we are using Lagna as the starting point.
    """
    asc_house = planet_positions[0][1][0]  # Lagna sign index (Capricorn for this chart)
    seed_house = asc_house

    ninth_house = (seed_house + const.HOUSE_9) % 12
    _dhasa_progression = [(h + seed_house) % 12 for h in range(12)]

    # If 9th house from seed is even-footed, reverse the progression
    if ninth_house in const.even_footed_signs:
        _dhasa_progression = [(seed_house + 12 - h) % 12 for h in range(12)]

    return _dhasa_progression


def _dhasa_duration(planet_positions, sign):
    return _dhasa_duration_knrao_method(planet_positions, sign)


def _dhasa_progression_knrao_method(planet_positions):
    asc_house = planet_positions[0][1][0]
    seed_house = asc_house
    ninth_house = (seed_house + const.HOUSE_9) % 12
    _dhasa_progression = [(h + seed_house) % 12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        _dhasa_progression = [(seed_house + 12 - h) % 12 for h in range(12)]
    return _dhasa_progression


def _resolve_method_functions(chara_method, planet_positions):
    """
    Single dispatch point returning (dhasa_progression, duration_func,
    antardhasa_function, num_cycles) for the given chara_method/gender.
    """
    if chara_method == const.CHARA_TYPE.PVN_RAO:
        dhasa_progression = _dhasa_progression_pvnrao_method(planet_positions)
        duration_func = _dhasa_duration_pvnrao_method
        cycles = 2
        antardhasa_function = lambda sign, years=None: _antardhasa_order_pvnrao(sign, planet_positions)

    elif chara_method == const.CHARA_TYPE.KN_RAO:
        dhasa_progression = _dhasa_progression_knrao_method(planet_positions)
        duration_func = _dhasa_duration_knrao_method
        cycles = 1
        antardhasa_function = lambda sign, years=None: _antardhasa_order_knrao(sign)

    elif chara_method  == const.CHARA_TYPE.IRANGATTI_MALE1:
        dhasa_progression = _dhasa_progression_iranganti_m1_male(planet_positions)
        duration_func = _dhasa_duration_iranganti_m1_male 
        cycles = 1
        antardhasa_function = lambda sign, years=None: _antardhasa_iranganti(sign)

    elif chara_method == const.CHARA_TYPE.IRANGATTI_MALE2:
        dhasa_progression = _dhasa_progression_iranganti_m2_male(planet_positions)
        duration_func = _dhasa_duration_iranganti_m2_male 
        cycles = 1
        antardhasa_function = lambda sign, years=None: _antardhasa_iranganti(sign)

    elif chara_method  == const.CHARA_TYPE.IRANGATTI_FEMALE:
        dhasa_progression = _dhasa_progression_iranganti_female(planet_positions)
        duration_func = _dhasa_duration_iranganti_female
        cycles = 1
        antardhasa_function = lambda sign, years=None: _antardhasa_iranganti(sign)

    elif chara_method in [const.CHARA_TYPE.MIND_SUTRA_MALE,const.CHARA_TYPE.MIND_SUTRA_FEMALE]:
        dhasa_progression = _dhasa_progression_mindsutra(planet_positions, chara_method)
        duration_func = _dhasa_duration_mindsutra
        cycles = 1
        antardhasa_function = lambda sign, years=12: _antardhasa_order_mindsutra(sign, planet_positions, years)

    else:
        raise ValueError("Unsupported chara_method.")

    return dhasa_progression, duration_func, antardhasa_function, cycles


def _generate_mahadasa_periods(
    place,
    planet_positions,
    chara_method,
    *,
    jd_start,
    stop_at_jd=None,
):
    """
    The single Mahadasa seed/root generator for Chara Dasa, covering all 5
    chara_method variants. This is the only place in the module that walks
    the method-specific dhasa_progression and applies PVN_RAO's 2-cycle
    complement rule (cycle-2 duration = 12 - cycle-1 duration, per sign).
    get_dhasa_antardhasa(), chara_immediate_children() (indirectly, via
    get_running_dhasa_for_given_date()'s own use of this generator), and
    get_running_dhasa_for_given_date() all rely on this same generator for
    the Mahadasa level.

    Yields:
        (sign, maha_start_jd, maha_duration_years, maha_end_jd)
    """
    dhasa_progression, duration_func, _antardhasa_function, cycles = _resolve_method_functions(
        chara_method, planet_positions,
    )

    start_jd = jd_start

    for cycle_ix in range(cycles):
        for lord in dhasa_progression:
            dd = float(duration_func(planet_positions, lord))

            if chara_method == const.CHARA_TYPE.PVN_RAO and cycle_ix == 1:
                dd = 12.0 - dd

            maha_start_jd = start_jd
            maha_end_jd = _bounded_end_jd(maha_start_jd, dd, place)

            yield lord, maha_start_jd, dd, maha_end_jd

            start_jd = maha_end_jd

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return


def _get_chara_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    chara_method,
    planet_positions,
    *,
    parent_end_jd=None,
):
    """
    Single children-engine for Chara Dasa (used at every level below
    Mahadasa, by all three entry points: get_dhasa_antardhasa()'s own
    recursion, chara_immediate_children(), and get_running_dhasa_for_
    given_date()).

    Rules:
        - Child order = the method-specific antardhasa_function's own
          output for parent_path[-1] (the parent sign).
        - MIND_SUTRA is structurally unique: at Antara level specifically
          (len(parent_path) == 1), the antardhasa_function itself returns
          exactly dhasa_years entries (not always 12), and each child's
          duration is a fixed 1.0 year (not parent_duration / 12). At
          every deeper level (len(parent_path) > 1) and for every other
          chara_method at every level, the rule is a simple equal split:
          child_duration = parent_duration / 12 (always exactly 12
          children).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's smallest child duration is under
          _SUB_DAY_DURATION_DAYS, all child boundaries (not just the
          last) are computed via proportional interpolation of the
          parent's own real [parent_start_jd, parent_end_jd] span,
          instead of calling _bounded_end_jd()/drik._get_dhasa_end_jd()
          per child.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    parent_sign = parent_path[-1]
    is_mindsutra_antara_level = (
        chara_method in [const.CHARA_TYPE.MIND_SUTRA_MALE, const.CHARA_TYPE.MIND_SUTRA_FEMALE ]
                         and len(parent_path) == 1
    )

    _, _duration_func, antardhasa_function, _cycles = _resolve_method_functions(
        chara_method, planet_positions,
    )
    # Gender only affects the Mahadasa PROGRESSION (handled by
    # _generate_mahadasa_periods()) -- antardhasa_function's own behavior
    # does not depend on gender for any of the 5 methods: only the
    # *_progression_* functions take a gender-dependent starting point;
    # antardhasa selection is always a pure function of the parent sign,
    # and for MIND_SUTRA, of dhasa_years.

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    if is_mindsutra_antara_level:
        years_int = int(round(parent_duration)) if parent_duration is not None else 12
        child_order = antardhasa_function(parent_sign, years=years_int)
        raw_child_durations = [1.0] * len(child_order)
    else:
        years_int = int(round(parent_duration)) if parent_duration is not None else 12
        child_order = antardhasa_function(parent_sign, years=years_int)
        raw_child_durations = [parent_duration / 12.0] * len(child_order)

    n = len(child_order)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = min(raw_child_durations)
    smallest_child_days = smallest_child_years * one_year_days
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(raw_child_durations)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, child_sign in enumerate(child_order):
        child_duration = raw_child_durations[i]
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
                child_start_jd,
                child_duration,
                child_end_jd,
            )
        )

        cursor = child_end_jd

    return children, parent_end_jd


def _find_child_containing_jd(children, target_jd):
    """
    Returns the single child tuple whose [start_jd, end_jd) contains
    target_jd. Falls back to the last child if target_jd is at/past the
    final boundary.
    """
    if not children:
        return None

    for child in children:
        _, s, _, e = child

        if s <= target_jd < e:
            return child

    return children[-1]


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    chara_method=None,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
    **kwargs,
):
    """
    Chara Dasa (sign-based), depth-enabled.

    Uses the same shared _generate_mahadasa_periods()/_get_chara_children_jd()
    engine as chara_immediate_children() and get_running_dhasa_for_given_date()
    -- every boundary, at every level, is computed via real solar-arc
    crossing unless the batch of children is sub-day, in which case
    proportional interpolation is used instead (see _SUB_DAY_DURATION_DAYS
    above).

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    """
    if chara_method is None:
        chara_method = const.CHARA_TYPE_DEFAULT
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

    rows = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            rows.append(
                (
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                )
            )
        else:
            start_str = utils.jd_to_gregorian(start_jd_local)
            dur_ret = round(duration_years, dhasa_level_index + 1) if round_duration else duration_years
            rows.append((lords_tuple, start_str, dur_ret))

    def _recurse(level, parent_path, parent_start_jd, parent_duration_years, parent_end_jd):
        children, _ = _get_chara_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            chara_method,
            planet_positions,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(level + 1, child_path, child_start_jd, child_duration, child_end_jd)
            else:
                _emit_row(child_path, child_start_jd, child_duration, child_end_jd)

    for lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        place,
        planet_positions,
        chara_method,
        jd_start=jd_at_dob,
    ):
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row((lord,), maha_start_jd, maha_dur, maha_end_jd)
        else:
            _recurse(
                const.MAHA_DHASA_DEPTH.ANTARA,
                (lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
            )

    return rows


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    chara_method=None,
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
    Chara -- return ONLY the immediate (p -> p+1) children inside the given parent span.

    A thin wrapper around the shared _get_chara_children_jd() engine.
    """
    if chara_method is None:
        chara_method = const.CHARA_TYPE_DEFAULT
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
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
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

    children, _ = _get_chara_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        chara_method,
        planet_positions,
        parent_end_jd=end_jd,
    )

    return [
        [
            child_path,
            _jd_to_tuple(child_start_jd),
            _jd_to_tuple(child_end_jd),
        ]
        for child_path, child_start_jd, _child_duration, child_end_jd in children
    ]


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    chara_method=None,
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
    Chara -- narrow Maha -> ... -> target depth and return the full running ladder.

    Uses the same shared _generate_mahadasa_periods()/_get_chara_children_jd()
    engine as get_dhasa_antardhasa() and chara_immediate_children(). The
    Mahadasa level is found via a single early-stopping walk of
    _generate_mahadasa_periods() (stop_at_jd=current_jd); every level
    below Mahadasa uses _get_chara_children_jd() then _find_child_
    containing_jd(), staying in JD-float space throughout (only the final
    returned rows are converted to Gregorian tuples).
    """
    if chara_method in [const.CHARA_TYPE.MIND_SUTRA_MALE, const.CHARA_TYPE.MIND_SUTRA_FEMALE]:
        raise ValueError("MindSutra method is not supported in get_running_dhasa_for_given_date. Use get_dhasa_antardhasa instead.")
    global one_year_days
    if chara_method is None:
        chara_method = const.CHARA_TYPE_DEFAULT
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

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None

    for lord, m_start_jd, m_dur, m_end_jd in _generate_mahadasa_periods(
        place,
        planet_positions,
        chara_method,
        jd_start=jd_at_dob,
        stop_at_jd=current_jd,
    ):
        maha_lord, maha_start_jd, maha_dur, maha_end_jd = lord, m_start_jd, m_dur, m_end_jd

    if maha_lord is None:
        return []

    running_all = [
        [
            (maha_lord,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    parent_path = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_chara_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            chara_method,
            planet_positions,
            parent_end_jd=parent_end_jd,
        )

        found = _find_child_containing_jd(children, current_jd)

        if found is None:
            running_all.append(
                [
                    parent_path + (parent_path[-1],),
                    utils.jd_to_gregorian(parent_start_jd),
                    utils.jd_to_gregorian(parent_end_jd),
                ]
            )
            break

        child_path, child_start_jd, child_duration_years, child_end_jd = found

        running_all.append(
            [
                child_path,
                utils.jd_to_gregorian(child_start_jd),
                utils.jd_to_gregorian(child_end_jd),
            ]
        )

        parent_path = child_path
        parent_start_jd = child_start_jd
        parent_end_jd = child_end_jd
        parent_duration_years = child_duration_years

    return running_all


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    dob = drik.Date(1995,1,11)
    tob = (15, 50, 37)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    chara_dhasa_method = const.CHARA_TYPE.IRANGATTI_MALE2
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    db = get_dhasa_antardhasa(dob, tob, place,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
    md_ad_seq = {}
    for lords, _, _ in db:
        lord, sub_lord = lords
        lord_name = utils.RAASI_SHORT_LIST[lord]
        if lord_name not in md_ad_seq:
            md_ad_seq[lord_name] = []
        md_ad_seq[lord_name].append(utils.RAASI_SHORT_LIST[sub_lord])
    md_ad_seq = {k: ','.join(v) for k, v in md_ad_seq.items()}
    for lord, sub_lord_seq in md_ad_seq.items():
        print(lord, " > ", md_ad_seq[lord])
    from datetime import datetime
    import random
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    print(check_date)
    import time
    if chara_dhasa_method in [const.CHARA_TYPE.MIND_SUTRA_MALE, const.CHARA_TYPE.MIND_SUTRA_FEMALE]:
        print("Skipping old method for MindSutra as it is not supported.")
        exit()  # MindSutra is not supported in the old method, skip it
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
        grd = get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=DLI,
                dhasa_duration_type=dd,
                chara_method=chara_dhasa_method,
            )
        grdn = [
                ['-'.join([utils.RAASI_SHORT_LIST[lord] for lord in lords]),
                 (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))]
                    for [lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2)] in grd]
        print("Dehā (new)  :", grdn)
        print('new method elapsed time', time.time() - start_time)
        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd,
            chara_method=chara_dhasa_method,
            return_exact_bounds=True,
        )
        deha_groups = utils._group_ancestors_from_leaves(ad, DLI)
        old_last_lords, old_start_jd, old_end_jd = utils._find_containing_group(deha_groups, current_jd)
        old_last_name = '-'.join([utils.RAASI_SHORT_LIST[lord] for lord in old_last_lords])
        y1, m1, d1, fh1 = utils.jd_to_gregorian(old_start_jd)
        y2, m2, d2, fh2 = utils.jd_to_gregorian(old_end_jd)
        print("Dehā (old)  :", [old_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('old method elapsed time', time.time() - start_time)

        new_last_lords = grdn[-1][0].split('-')
        lords_match = new_last_lords == old_last_lords if isinstance(old_last_lords, list) else None
        print("\n" + "-" * 80)
        print("DIFF (new - old), Deha level only:")
        print("  new lords:", grdn[-1][0], " old lords:", old_last_name)
        print("-" * 80)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chara_dhasa_test()
    exit()
