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
from jhora import const,utils
from jhora.horoscope.chart import charts, house
"""
    1=> KN Rao method 
    2=> Parasara/PVN Rao Method - from https://vedicastrologer.org/articles/pp_chara_dasa.pdf
    3=> Raghava Bhatta method from https://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html
"""
chara_method = 1
_dhasa_cycles = 2; one_year_days = const.sidereal_year
# ─────────────────────────────────────────────────────────────────────────────
# NEW: Iranganti / RB–NS sets & helpers (used by Method=3,4) and MindSutra (5)
# Sources: Iranganti's booklet (Phalita Daśās → Chara Daśā); RB–NS note (Shanmukha)
# ─────────────────────────────────────────────────────────────────────────────

# Oja/Sama groups (Iranganti, Method‑1 male rules)
OJAPADA_SIGNS = {
    const.ARIES, const.TAURUS, const.GEMINI, const.LIBRA, const.SCORPIO, const.SAGITTARIUS
}
SAMAPADA_SIGNS = {
    const.CANCER, const.LEO, const.VIRGO, const.CAPRICORN, const.AQUARIUS, const.PISCES
}

def _lord_of(sign, planet_positions):
    # Classical sign lords in these Chara rules (Sc=Mars, Aq=Saturn; nodes not used)
    if sign == const.SCORPIO:  return const.MARS_ID
    if sign == const.AQUARIUS: return const.SATURN_ID
    return const.house_owners[sign]

# ─────────────────────────────────────────────────────────────────────────────
# Iranganti – MALE Method‑1 (Method=3, male)
# Start: Lagna. Direction: contiguous ±1 based on 9th in Oja or Sama.
# Years: if own=12; else count SIGN→LORD forward (if SIGN∈Oja) or backward (if SIGN∈Sama);
#        years = count-1; apply exalt/neecha ±1.
# Antara: start at parent; 12 by padakrama; equal split.
# ─────────────────────────────────────────────────────────────────────────────
def _dhasa_progression_iranganti_m1_male(planet_positions):
    asc = planet_positions[0][1][0]
    ninth = (asc + const.HOUSE_9) % 12
    is_forward = (ninth in OJAPADA_SIGNS)  # else Sama → reverse
    return [(asc + (i if is_forward else -i)) % 12 for i in range(12)]

def _dhasa_duration_iranganti_m1_male(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    # count SIGN → LORD by SIGN's Oja/Sama group
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

# ─────────────────────────────────────────────────────────────────────────────
# Iranganti – MALE Method‑2 (Method=4, male)
# Start: Lagna. Pattern by (odd/even × modality) → contiguous / ±6 / trinal.
# Years: own=12; else lord‑parity determines direction counting LORD→SIGN; years=count‑1 (no ex/neecha).
# Antara: start at parent; 12 by padakrama; equal split.
# ─────────────────────────────────────────────────────────────────────────────
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

    # dual
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
    # dual
    return _dual_block(asc, forward=odd)

def _dhasa_duration_iranganti_m2_male(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    forward = (lord_house in const.odd_signs)
    count = ((sign - lord_house) % 12) + 1 if forward else ((lord_house - sign) % 12) + 1
    years = count - 1
    if years <= 0:
        years = 12
    return years

# ─────────────────────────────────────────────────────────────────────────────
# Iranganti – FEMALE (single method; used with Method=3 and Method=4)
# Start: 4th from Lagna by PRAKṚTI (odd → forward; even → backward).
# Progression: VIKṚTI padakrama keyed to FEMALE Lagna: contiguous / ±6 / trinal (even&dual=reverse trinal).
# Years: own=12; 7th=10; else LORD→SIGN by PRAKṚTI of RUNNING SIGN (odd→forward; even→backward), years=count‑1.
# Antara: start at parent; 12 by padakrama; equal split.
# ─────────────────────────────────────────────────────────────────────────────
def _dhasa_progression_iranganti_female(planet_positions):
    asc = planet_positions[0][1][0]
    odd = asc in const.odd_signs
    start = (asc + 3) % 12 if odd else (asc - 3) % 12  # 4th by prakṛti
    if asc in const.movable_signs:
        step = 1 if odd else -1
        return [(start + step * i) % 12 for i in range(12)]
    if asc in const.fixed_signs:
        step = 5 if odd else -5
        return [(start + step * i) % 12 for i in range(12)]
    # dual
    return _dual_block(start, forward=odd)

def _dhasa_duration_iranganti_female(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(sign, planet_positions)
    lord_house = p_to_h[lord]
    if lord_house == sign:
        return 12
    if lord_house == (sign + const.HOUSE_7) % 12:
        return 10
    forward = (sign in const.odd_signs)  # prakṛti of RUNNING SIGN
    count = ((sign - lord_house) % 12) + 1 if forward else ((lord_house - sign) % 12) + 1
    years = count - 1
    if years <= 0:
        years = 12
    return years

# Antardaśā (Iranganti/RB–NS): parent‑sign padakrama; 12 parts; equal split
def _antardhasa_iranganti(parent_sign):
    return _padakrama_list_from_parent(parent_sign)

# ─────────────────────────────────────────────────────────────────────────────
# MindSutra (Method=5) — software variant per Shanmukha’s page
# Years: both sexes → if lord in odd sign count LORD→SIGN forward else backward; years=count‑1; own=12; 7th=10; no ex/neecha.
# Antar: starts from PĀKA sign; direction by PĀKA parity; #antars = mahā‑years (≈1 year each); contiguous (no padakrama).
# Progression: padakrama‑based, global direction by Lagna odd/even (RB–NS wording).
# ─────────────────────────────────────────────────────────────────────────────
def _dhasa_progression_mindsutra(planet_positions, gender):
    # choose start as in RB–NS: male→Lagna; female→4th by prakṛti
    asc = planet_positions[0][1][0]
    odd = asc in const.odd_signs
    start = asc if gender == 0 else ((asc + 3) % 12 if odd else (asc - 3) % 12)

    # Build forward padakrama chain by stepping with current sign’s nature
    seq = [start]
    seen = {start}
    # master for dual rotation
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
            # fall through if user customized sets; ensure we fill 12 unique
            i = 0
            while nxt in seen and i < 12:
                nxt = (nxt + 1) % 12
                i += 1
        seq.append(nxt); seen.add(nxt)

    # Reverse the order for even Lagna (as per “sequence by Lagna odd/even”)
    if not odd:
        # keep start first, then reverse the remainder
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
    forward = (lord_house in const.odd_signs)
    count = ((sign - lord_house) % 12) + 1 if forward else ((lord_house - sign) % 12) + 1
    count = utils.count_rasis(lord_house,sign,1) if forward else utils.count_rasis(lord_house,sign,-1)
    years = count - 1
    if years <= 0:
        years = 12
    return years

def _antardhasa_order_mindsutra(parent_sign, planet_positions):
    # Antar starts from PĀKA (lord’s sign); direction by PĀKA parity; contiguous; count decided in L2
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord = _lord_of(parent_sign, planet_positions)
    paka = p_to_h[lord]
    forward = (paka in const.odd_signs)
    order = [(paka + (i if forward else -i)) % 12 for i in range(12)]
    return order
def _antardhasa_rangacharya(parent_sign):
    """
    Parent-specific padakrama (matches JHora "Rangacharya"):
      Movable P -> contiguous forward 12
      Fixed   P -> every 6th (0-based +5)
      Dual    P -> four trinal triplets:
                   [P, P-4, P+4], then anchors P-1, P-2, P-3 (mod 12)
    """
    P = parent_sign % 12
    if P in const.movable_signs:
        return [(P + i) % 12 for i in range(12)]
    if P in const.fixed_signs:
        return [(P + 5*i) % 12 for i in range(12)]
    out = []
    for g in range(4):
        a = (P - g) % 12
        out.extend([a, (a - 4) % 12, (a + 4) % 12])
    return out

def _dhasa_duration_knrao_method(planet_positions,sign):
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
            However, dasa length becomes 12 years then.
        """
        dhasa_period = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM : # > const._FRIEND:
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        dhasa_period += 1
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEBILITATED_NEECHAM:
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
        dhasa_period -= 1
    return dhasa_period
def _dhasa_duration_pvnrao_method(planet_positions,sign):
    """ Not fully implemented yet """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    """ Additionally PVN Rao has following condition
            Stronger Co-lord of Sc and Aq for dasa years
            For Sc and Aq, there are 2 co-lords – Mars/Ketu and Saturn/Rahu. Find dasa years from the stronger co-lord
            using the following rules until there is a resolution:
            (1) If both lords are in the sign, dasa is of 12 years.
            (2) If one of them is in the sign, take dasa years from the other co-lord.
            (3) If both are outside the sign, take the stronger planet.    
            (4) One conjoining more planets is stronger.
            (5) A planet in a movable sign (Ar, Cn, Li, Cp) is stronger than a planet in a fixed sign (Ta, Le, Sc, Aq)
                and a planet in a fixed sign is stronger than a planet in a dual sign (Ge, Vi, Sg, Pi).
            (6) A planet giving more dasa years is stronger.
    """
    if sign==const.SCORPIO: # sign is scorpio Mars/Ketu are co-lords
        if p_to_h[const.MARS_ID]==sign and p_to_h[const.KETU_ID]==sign: # Both in Scorpio
            dhasa_period = 12; return dhasa_period
        elif (p_to_h[const.MARS_ID]==sign and p_to_h[const.KETU_ID]!=sign): # only one of them in scorpio
            house_of_lord = p_to_h[const.KETU_ID]
        elif (p_to_h[const.KETU_ID]==sign and p_to_h[const.MARS_ID]!=sign):
            house_of_lord = p_to_h[const.MARS_ID]
        else:
            lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
            house_of_lord = p_to_h[lord_of_sign]
    elif sign==const.AQUARIUS: # sign is aquarius Sat/Rahu are co-lords
        if p_to_h[const.SATURN_ID]==sign and p_to_h[const.RAHU_ID]==sign: # Both in Aquarius
            dhasa_period = 12; return dhasa_period
        elif (p_to_h[const.SATURN_ID]==sign and p_to_h[const.RAHU_ID]!=sign): # only one of them in scorpio
            house_of_lord = p_to_h[const.RAHU_ID]
        elif (p_to_h[const.RAHU_ID]==sign and p_to_h[const.SATURN_ID]!=sign):
            house_of_lord = p_to_h[const.SATURN_ID]
        else:
            lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
            house_of_lord = p_to_h[lord_of_sign]
    else:
        lord_of_sign = const.house_owners[sign]
        house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        """ Counting is backward if dasa rasi is even-footed."""
        if house_of_lord < sign:
            dhasa_period = sign+1-house_of_lord
        else:
            dhasa_period = sign+13-house_of_lord
    else:
        """ Counting is forward if dasa rasi is odd-footed."""
        if house_of_lord < sign:
            dhasa_period = house_of_lord+13-sign
        else:
            dhasa_period = house_of_lord+1-sign
    dhasa_period -= 1 # Subtract one from the count
    if dhasa_period <=0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one, 
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one. 
            However, dasa length becomes 12 years then.
        """
        dhasa_period = 12
        """ Following exceptions are not applicable for PVN Rao method """
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
    return dhasa_period
def _dhasa_duration(planet_positions,sign):
    return _dhasa_duration_knrao_method(planet_positions, sign)    
""" CHARA METHODS 2 and 3  - Logic not yet implemented """
def _antardhasa(dhasas,method=1): # KN Rao Method
    _antardhasas = dhasas[1:]+[dhasas[0]] if method==1 else dhasas
    return _antardhasas
def _dhasa_progression_pvnrao_method(planet_positions):
    """
        (1) Take the signs occupied by lagna, Moon and Sun. Take the one with the strongest lord. Strengths of
        lords are judged based on rules to be mentioned in another section.
    """
    sun_house = planet_positions[1][1][0]; sun_house_lord = house.house_owner_from_planet_positions(planet_positions, sun_house)
    asc_house = planet_positions[0][1][0]; asc_house_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    sh = house.stronger_planet_from_planet_positions(planet_positions, sun_house_lord, asc_house_lord)
    seed_house = asc_house if sh==asc_house_lord else sun_house
    moon_house = planet_positions[2][1][0]; moon_house_lord = house.house_owner_from_planet_positions(planet_positions, moon_house)
    stronger_lord = house.stronger_planet_from_planet_positions(planet_positions,sh, moon_house_lord)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)#; print(h_to_p)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)#; print(p_to_h)
    if moon_house_lord==stronger_lord:seed_house = moon_house 
    #print(asc_house_lord,sun_house_lord,moon_house_lord,'stronger lord of lagna, sun, moon houses',stronger_lord)
    #print(asc_house,sun_house,moon_house,'stronger of lagna, sun, moon houses',seed_house)
    ninth_house = (seed_house+8)%12
    _dhasa_progression = [(h+seed_house)%12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        #print('ninth house is even footed')
        _dhasa_progression = [(seed_house+12-h)%12 for h in range(12)]
    return _dhasa_progression
def _dhasa_progression_knrao_method(planet_positions):
    asc_house = planet_positions[0][1][0]
    seed_house = asc_house
    ninth_house = (seed_house+const.HOUSE_9)%12
    _dhasa_progression = [(h+seed_house)%12 for h in range(12)]
    if ninth_house in const.even_footed_signs:
        _dhasa_progression = [(seed_house+12-h)%12 for h in range(12)]
    return _dhasa_progression
def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1, years=1, months=1, sixty_hours=1,
    chara_method=1,              # 1 = Parāśara/PVN Rao (two cycles, 2nd = 12 - first)
                                 # 2 = K.N. Rao (single cycle)
                                 # 3 = Rāghava Bhaṭṭa/Rangacharya - Method-1
                                 # 4 = Rāghava Bhaṭṭa/Rangacharya - Method-2
    gender=0,                    # 5 = Mind Sutra Method
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara [default], 3..6 deeper)
    round_duration=True
):
    """
    Chara Daśā (sign-based), depth-enabled.
    chara_method=1,              
        # 1 = Parāśara/PVN Rao (two cycles, 2nd = 12 - first)
        # 2 = K.N. Rao (single cycle)
        # 3 = Rāghava Bhaṭṭa/Rangacharya - Method-1. Ref: Jyotish Manual of Jaimini Astrology - Iranganti Rangacharya
        # 4 = Rāghava Bhaṭṭa/Rangacharya - Method-2. Ref: Jyotish Manual of Jaimini Astrology - Iranganti Rangacharya
        # 5 = Mind Sutra Method (Ref:https://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html) 
            (Method 3/4 are also called Raghava Bhatta - Nrisimha Suri method)
            And method=5 is given by Ref: https://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html
    gender=0, 0=Male, 1 = Female
    Depth control (replaces include_antardhasa):
      1 = MAHA_DHASA_ONLY      -> rows: (l1,               start_str, dur_years)
      2 = ANTARA               -> rows: (l1, l2,           start_str, dur_years)       [DEFAULT]
      3 = PRATYANTARA          -> rows: (l1, l2, l3,       start_str, dur_years)
      4 = SOOKSHMA             -> rows: (l1, l2, l3, l4,   start_str, dur_years)
      5 = PRANA                -> rows: (l1, l2, l3, l4, l5,   start_str, dur_years)
      6 = DEHA                 -> rows: (l1, l2, l3, l4, l5, l6, start_str, dur_years)

    IMPORTANT: We do NOT re-implement any Chara logic. We only:
      - pick progression, durations, and cycles via your existing helpers based on `chara_method`;
      - split immediate parent into 12 equal parts at deeper levels;
      - keep antardasha order exactly as `_antardhasa(dhasa_progression, method=...)` returns (global sequence).
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # --- Chart at birth epoch (as your current function does) -------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, 
                                    divisional_chart_factor=divisional_chart_factor)[:const._pp_count_upto_ketu]
    # --- Choose progression, duration function and cycles based on method -------
    if chara_method == 1:
        # Parāśara/PVN Rao: progression via PVN helper, durations via PVN helper, two cycles
        dhasa_progression = _dhasa_progression_pvnrao_method(planet_positions)
        duration_func     = _dhasa_duration_pvnrao_method
        cycles            = 2
        antardhasa_method     = 1
        antardhasa_function = None
    elif chara_method == 2:
        # K.N. Rao: progression via KN Rao helper, durations via KN Rao helper, single cycle
        dhasa_progression = _dhasa_progression_knrao_method(planet_positions)
        duration_func     = _dhasa_duration_knrao_method
        cycles            = 1
        antardhasa_method     = 2   # no rotation
        antardhasa_function = None
    elif chara_method == 3:
        # Iranganti – Method‑1 (Male-1); Female = book’s single method
        if gender == 0:
            dhasa_progression = _dhasa_progression_iranganti_m1_male(planet_positions)
            duration_func     = _dhasa_duration_iranganti_m1_male
        else:
            dhasa_progression = _dhasa_progression_iranganti_female(planet_positions)
            duration_func     = _dhasa_duration_iranganti_female
        cycles                = 1
        antardhasa_method     = None   # not used; we drive via function below
        antardhasa_function   = _antardhasa_iranganti

    elif chara_method == 4:
        # Iranganti – Method‑2 (Male-2); Female = book’s single method
        if gender == 0:
            dhasa_progression = _dhasa_progression_iranganti_m2_male(planet_positions)
            duration_func     = _dhasa_duration_iranganti_m2_male
        else:
            dhasa_progression = _dhasa_progression_iranganti_female(planet_positions)
            duration_func     = _dhasa_duration_iranganti_female
        cycles                = 1
        antardhasa_method     = None
        antardhasa_function   = _antardhasa_iranganti

    elif chara_method == 5:
        # MindSutra variant (documented by Shanmukha; Jaimini Light)
        dhasa_progression = _dhasa_progression_mindsutra(planet_positions, gender)
        duration_func     = _dhasa_duration_mindsutra
        cycles            = 1
        antardhasa_method   = None   # special handling in L2 for method 5
        antardhasa_function = None
    else:
        raise ValueError("Unsupported chara_method. Use 1 (PVN), 2 (KNRao), or 3 (Raghava Bhatta).")

    # --- Global antardasha sequence (exactly how your code does it) -------------
    # NOTE: This is *not* rotated per-parent. We keep your global sequence at every level.
    bhukthis_global = _antardhasa(dhasa_progression, method=antardhasa_method)
    if antardhasa_method is not None:
        bhukthis_global = _antardhasa(dhasa_progression, method=antardhasa_method)

    # --- Helpers ----------------------------------------------------------------
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    def _append(out, tpl):
        out.append(tpl)

    def _recurse(level, parent_start_jd, parent_years, prefix, out_rows):
        """
        Depth >= 3:
          - child order: the same global `bhukthis_global`
          - child duration: equal split of immediate parent into 12
        """
        child_unrounded = parent_years / 12.0
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for child_sign in bhukthis_global:
                _recurse(level + 1, jd_cursor, child_unrounded, prefix + (child_sign,), out_rows)
                jd_cursor += child_unrounded * one_year_days
        else:
            for child_sign in bhukthis_global:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_ret   = round(child_unrounded, _round_ndigits) if round_duration else child_unrounded
                _append(out_rows, prefix + (child_sign, start_str, dur_ret))
                jd_cursor += child_unrounded * one_year_days

    # --- Build rows --------------------------------------------------------------
    rows   = []
    jd_cur = jd_at_dob

    for cycle_ix in range(cycles):
        for lord in dhasa_progression:
            # years for this maha sign
            dd = float(duration_func(planet_positions, lord))
            if chara_method == 1 and cycle_ix == 1:
                # 2nd cycle (PVN): 12 - first cycle duration
                dd = 12.0 - dd

            # L1: Maha only
            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                start_str = utils.julian_day_to_date_time_string(jd_cur)
                dur_ret   = round(dd, _round_ndigits) if round_duration else dd
                _append(rows, (lord, start_str, dur_ret))
                jd_cur += dd * one_year_days
                continue

            # L2: Antara (equal split into 12; global antardasha sequence)
            if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                ddb      = dd / 12.0
                jd_b_ini = jd_cur
                # --- Only change: pick Antardaśā order per method ---
                if antardhasa_function is not None:
                    bhuktis_order = antardhasa_function(lord)           # method 3/4: parent-specific padakrama
                else:
                    bhuktis_order = bhukthis_global                 # method 1/2: your existing global sequence
                for bhukthi in bhuktis_order:
                    start_str = utils.julian_day_to_date_time_string(jd_b_ini)
                    dur_ret   = round(ddb, _round_ndigits) if round_duration else ddb
                    _append(rows, (lord, bhukthi, start_str, dur_ret))
                    jd_b_ini += ddb * one_year_days
                jd_cur += dd * one_year_days
                continue

            # L3..L6: recursive, equal split of immediate parent using global bhukthis order
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,  # = 2 → build 3..N
                parent_start_jd=jd_cur,
                parent_years=dd,
                prefix=(lord,),
                out_rows=rows
            )
            jd_cur += dd * one_year_days

    return rows

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.chara_dhasa_test()
    exit()
    