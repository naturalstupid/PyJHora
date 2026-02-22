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
from jhora.horoscope.chart import charts, house,arudhas
from jhora.horoscope.dhasa.raasi import narayana
""" TODO logic not fully implemented """
# --- Keep your duration and progression as-is (minor safety casts) -----------
# -*- coding: UTF-8 -*-
_round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

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
    Ref: IR write-ups (LOVA/Saptarishis). [1](https://phpbb.lightonvedicastrology.com/viewforum.php?f=30&start=200)
    """
    direction = 1 if dhasa_lord in const.odd_signs else -1

    if dhasa_lord in const.fixed_signs:
        return [(dhasa_lord + direction * h * const.HOUSE_6) % 12 for h in range(12)]
    if dhasa_lord in const.movable_signs:
        return [(dhasa_lord + direction * h) % 12 for h in range(12)]

    frame = [1,4,7,10, 5,8,11,2, 9,12,3,6]
    return [(dhasa_lord + direction * (h - 1)) % 12 for h in frame]


# -----------------------------------------------------------------------------
#   Common helpers
# -----------------------------------------------------------------------------
def _append_row(_rows, _labels, _start_jd, _dur_years, round_duration):
    _start_str = utils.julian_day_to_date_time_string(_start_jd)
    _durn = round(_dur_years, _round_ndigits) if round_duration else _dur_years
    _rows.append((*_labels, _start_str, float(_durn)))


def _expand_iranganti_levels(_rows, _level_target, _labels, _parent_sign,
                             _start_jd, _dur_years, _current_level,
                             planet_positions_ctx, round_duration):
    """
    Recursive builder for IR: order from _dhasa_progression(parent), equal-split 12,
    Σ(children) == parent, and JD advances exactly by child_years * sidereal_year.
    """
    if _current_level == _level_target:
        _append_row(_rows, _labels, _start_jd, _dur_years, round_duration)
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
            round_duration=round_duration
        )
        jd_ptr += child_years * getattr(const, "sidereal_year", 365.256363004)


# -----------------------------------------------------------------------------
#   Method 1: Iranganti Rangacharya (IR) – D-9 (KM/Nādi) ONLY
# -----------------------------------------------------------------------------
def _iranganti_rangacharya_method(dob, tob, place,
                                  years=1, months=1, sixty_hours=1,
                                  dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                                  round_duration=True):
    """
    IR Padanadhamsa: reckon in Jaimini/Krishna-Mishra (Nādi) Navamsa (D-9).
    Steps (per IR):
      1) AL in D1; 2) Seed in D9(KM): AL-lord's D9 sign vs its 7th (stronger);
      3) Order per IR progression (modality + odd/even sign);
      4) Durations in D9(KM): S->L inclusive; odd forward, even reverse; own=12, 7th=10;
      5) Sub-levels: equal-split (/12). [1](https://phpbb.lightonvedicastrology.com/viewforum.php?f=30&start=200)
    """
    if not (1 <= int(dhasa_level_index) <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")

    jd_at_dob = utils.julian_day_number(dob, tob)

    # D1 for AL
    d1_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=1,
                                           years=years, months=months, sixty_hours=sixty_hours)
    al = arudhas.bhava_arudhas_from_planet_positions(d1_positions)[0]

    # D9 (KM/Nādi) – both seed AND engine for IR
    d9_km_positions = charts.divisional_chart(jd_at_dob, place,
                                              divisional_chart_factor=9, chart_method=4)

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
            _append_row(rows, [md_sign], jd_ptr, md_years, round_duration)
        else:
            _expand_iranganti_levels(rows, int(dhasa_level_index), [md_sign], md_sign,
                                     jd_ptr, md_years, 1, d9_km_positions, round_duration)
        jd_ptr += md_years * getattr(const, "sidereal_year", 365.256363004)

    return rows


# -----------------------------------------------------------------------------
#   Method 2: Sanjay Rath (SR) – D-9 ONLY (Padanathamsa = Navamsa Narayana)
# -----------------------------------------------------------------------------
def _sanjay_rath_method(dob, tob, place,
                        years=1, months=1, sixty_hours=1,
                        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                        round_duration=True,
                        navamsa_chart_method_for_sr=1):
    """
    SR Padanadhamsa = Narayana Dasa of the Navamsa:
      - Seed in D9: AL-lord's D9 sign vs its 7th (stronger). For AL in Sc/Aq, pick stronger (Mars,Ketu)/(Saturn,Rahu) IN D9.
      - Engine: run Narayana Dasa on D9 (periods 'exactly similar to the Navamsa Narayana Dasa').
      - Sub-levels: as per your Narayana engine. [3](https://phpbb.lightonvedicastrology.com/viewtopic.php?t=20285)[4](https://phpbb.lightonvedicastrology.com/viewtopic.php?t=3946)
    """
    jd_at_dob = utils.julian_day_number(dob, tob)

    # D1 for AL
    d1_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=1,
                                           years=years, months=months, sixty_hours=sixty_hours)
    al = arudhas.bhava_arudhas_from_planet_positions(d1_positions)[0]

    # D9 (variant knob): Parāśara=1 (default) or KM/Nādi=4
    d9_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=9,
                                           chart_method=navamsa_chart_method_for_sr)

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
        round_duration=round_duration
    )


# -----------------------------------------------------------------------------
#   Method 3: PVR/JHora generalized – ANY varga (seed chart == engine chart)
# -----------------------------------------------------------------------------
def _pvr_generalized_method(dob, tob, place, divisional_chart_factor=1,
                            years=1, months=1, sixty_hours=1,
                            dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                            round_duration=True):
    """
    PVR/JHora-style 'Padanadhamsa':
      - Seed in TARGET varga (dcf): AL in D1 -> AL-lord (Sc/Aq: stronger co-lord IN target varga)
        -> lord's sign in target varga vs its 7th (stronger).
      - Engine: run Narayana Dasa on the SAME varga (dcf).
      Matches JHora when users switch dcf (D1 timelines for dcf=1, D9 for dcf=9, etc.). [5](https://archive.org/details/quintessenceofbrahmasutrashreebhashyamahamahopadhyayairangantirangacharya2002ocr)
    """
    jd_at_dob = utils.julian_day_number(dob, tob)

    # Engine/seed chart = requested varga
    varga_positions = charts.divisional_chart(jd_at_dob, place,
                                              divisional_chart_factor=divisional_chart_factor,
                                              years=years, months=months, sixty_hours=sixty_hours)

    # D1 for AL
    d1_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=1,
                                           years=years, months=months, sixty_hours=sixty_hours)
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
        round_duration=round_duration
    )


# -----------------------------------------------------------------------------
#   Public router
# -----------------------------------------------------------------------------
def get_dhasa_antardhasa(dob, tob, place,
                         divisional_chart_factor=9, years=1, months=1, sixty_hours=1,
                         dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                         round_duration=True, method=1,
                         # SR variant: choose D9 build (1=Parāśara, 4=KM/Nādi)
                         navamsa_chart_method_for_sr=1):
    """
    method=1 -> Iranganti Rangacharya (D-9 KM/Nādi ONLY; seed+engine in D9)  [1](https://phpbb.lightonvedicastrology.com/viewforum.php?f=30&start=200)
    method=2 -> Sanjay Rath (D-9 ONLY; Padanathamsa = Navamsa Narayana)       [3](https://phpbb.lightonvedicastrology.com/viewtopic.php?t=20285)
    method=3 -> PVR/JHora generalized (seed & engine in target varga 'dcf')    [5](https://archive.org/details/quintessenceofbrahmasutrashreebhashyamahamahopadhyayairangantirangacharya2002ocr)

    NOTE:
      - For methods 1 & 2, D-9 is used internally regardless of 'divisional_chart_factor'.
      - For method 3, 'divisional_chart_factor' drives both seed & engine.
    """
    if method == 1:
        return _iranganti_rangacharya_method(
            dob, tob, place,
            years=years, months=months, sixty_hours=sixty_hours,
            dhasa_level_index=dhasa_level_index,
            round_duration=round_duration
        )

    if method == 2:
        return _sanjay_rath_method(
            dob, tob, place,
            years=years, months=months, sixty_hours=sixty_hours,
            dhasa_level_index=dhasa_level_index,
            round_duration=round_duration,
            navamsa_chart_method_for_sr=navamsa_chart_method_for_sr
        )

    # method == 3 (PVR generalized)
    return _pvr_generalized_method(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration
    )


# -----------------------------------------------------------------------------
#   Quick local test
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    utils.set_language('en')
    from jhora.panchanga import drik
    dob = drik.Date(1917,11,19); tob=(23,22,0); place= drik.Place("Allahabad, India",25.4683,81.8546,5.5)
    dli = 2 # Dhasa Lavel Index 
    print('Date:',dob)
    # IR (D-9 KM/Nādi only)
    out_ir = get_dhasa_antardhasa(dob, tob, place, method=1, dhasa_level_index=dli)
    for row in out_ir:
        print("[IR]", [utils.RAASI_LIST[r] for r in row[:-2]], row[-2], row[-1], "Yrs")

    # Bill Clinton example (SR book): Aug 19, 1946 03:44, Hope AR
    dob = drik.Date(1946,8,19); tob=(3,44,0); place = drik.Place("Hope,AK,USA", 33+40/60, -93-35/60, -6.0)
    print('Date:',dob)
    # SR (D-9 only): default Parāśara D9; switch to 4 for KM/Nādi if desired
    out_sr = get_dhasa_antardhasa(dob, tob, place, method=2,
                                  navamsa_chart_method_for_sr=1,  # or 4
                                  dhasa_level_index=dli)
    for row in out_sr:
        print("[SR]", [utils.RAASI_LIST[r] for r in row[:-2]], row[-2], row[-1], "Yrs")

    print('Date:',dob)
    out_pvr_d9 = get_dhasa_antardhasa(dob, tob, place, method=3, divisional_chart_factor=9, dhasa_level_index=dli)
    for row in out_pvr_d9:
        print("[PVR D9]", [utils.RAASI_LIST[r] for r in row[:-2]], row[-2], row[-1], "Yrs")
    # PVR/JHora generalized: seed+engine on the chosen varga (try dcf=1 and dcf=9)
    out_pvr_d1 = get_dhasa_antardhasa(dob, tob, place, method=3, divisional_chart_factor=1, dhasa_level_index=1)
    for row in out_pvr_d1:
        print("[PVR D1]", [utils.RAASI_LIST[r] for r in row[:-2]], row[-2], row[-1], "Yrs")
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.padhanadhamsa_dhasa_test()