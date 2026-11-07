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
from jhora.horoscope.chart import house, charts
from jhora.horoscope.dhasa.raasi import narayana
"""
Trikona Dasa

Mahadasa seed (shared by all 4 methods below): the strongest of the 1st,
5th and 9th houses from Lagna, resolved by a pairwise strength cascade
(house.stronger_rasi_from_planet_positions).

Four Mahadasa methods are supported, selected via const.TRIKONA_METHOD
(see trikona_const_patch.py) and const.trikona_dhasa_method_default:
  JHORA (default) - the dasa order runs forward from the seed if the seed
      is an odd sign, backward if even, one sign at a time. Duration for
      each Mahadasa uses narayana._dhasa_duration().
  Ref: https://saptarishisshop.com/trikona-dasa-a-critical-review-by-iranganti-rangacharya/
  RAMAN_DWIVEDI_ACHYUTANANDA_JHA ("Method 1" per Vinayak Bhatt's article,
      "Trikona Dasa - A Critical Review of Iranganti Rangacharya",
      saptarishisastrology.com, attributed to B.V. Raman, Dwivedi and
      Achyutananda Jha) - dasa order steps according to the seed sign's
      modality: movable signs step through consecutively, fixed signs
      step in samasaptaka (every 6th house) pairs, dual signs step in
      trinal (1st-5th-9th) groups. Direction is set by Neelakanta's
      Vishama Pada / Sama Pada classification: Vishama (direct) =
      {Ar,Ta,Ge,Li,Sc,Sg}, Sama (reverse) = {Cn,Le,Vi,Cp,Aq,Pi} - this
      differs from plain odd/even only for the four fixed signs
      (Ta/Sc are Vishama though naturally even; Le/Aq are Sama though
      naturally odd). Duration for each sign is the inclusive sign-count
      to its lord (direct/reverse by the same Vishama/Sama rule), minus
      one, with the own-sign exception giving 12 years and the usual
      exalted (+1) / debilitated (-1) adjustments.
  RAGHAVA_BHATTA_NRISIMHA_SURI ("Method 2" in the same article, also
      called Gochara Dasa) - same modality-based stepping as above, but
      direction is set by plain odd/even signs rather than Vishama/Sama.
      Duration is the inclusive sign-count to the lord (direct/reverse by
      plain odd/even), with NO further subtraction - the raw count is the
      duration - own-sign gives 12 years, with the usual exalted/
      debilitated adjustments. Per the article, Raghavabhatta does not
      resolve dual rulership of Scorpio/Aquarius by chart strength for
      this calculation; this module therefore uses const.house_owners
      (the fixed, traditional single-lord table: Mars for Scorpio, Saturn
      for Aquarius) rather than house.house_owner_from_planet_positions()
      (which performs a chart-dependent strength comparison between the
      two co-lords) when resolving a sign's lord for this method only.
  NEELAKANTA_VRIDDHAKARIKA ("Method 3", citing an old Vriddhakarika text
      quoted by Neelakanta) - the seed sign from the standard derivation
      may be replaced before use, depending on the native's gender: for a
      male horoscope, an even seed is replaced by its "sammukha" (facing)
      sign, guaranteeing an odd, direct-order seed; for a female
      horoscope, an odd seed is replaced by its sammukha, guaranteeing an
      even, reverse-order seed. Sammukha is the 8th house for a movable
      sign, the 6th house for a fixed sign, and the 4th house (direct if
      the sign is odd, reverse if even) for a dual sign. This
      substitution is defined only for male/female horoscopes; for
      const.GENDER.TRANSGENDER or const.GENDER.NO_PREFERENCE the seed
      candidate is used as-is, with no substitution. Order and duration
      otherwise follow the same rules as RAGHAVA_BHATTA_NRISIMHA_SURI.

Antardasa (level 2 and below) depends on the Mahadasa method:
  - JHORA: seed = stronger(dasa_rasi, 7th_from_dasa_rasi); direction by
    plain odd/even; steps by modality of that seed - movable: 1 sign at a
    time; fixed: every 5th sign; dual: kendra progression
    (1,4,7,10,2,5,8,11,3,6,9,12). Confirmed against 3 independent real
    JHora charts (36 Mahadasa->Antardasa pairs, all 6 modality x parity
    combinations, 0 exceptions). Saturn/Ketu occupying the antardasa seed
    has NOT been tested and may require an exception not yet accounted
    for here - treat this rule as confirmed for the common case only.
  - all other methods: P.S. Sastri's "Jaimini Astrology Insights" rule -
    each Mahadasa is divided into twelve equal antardasas, in the order
    1,5,9,2,6,10,3,7,11,4,8,12 from the dasa sign if that sign is odd, or
    1,9,5,12,8,4,11,7,3,10,6,2 if even. Verified against that book's own
    worked examples (Sagittarius, Cancer).
The same rule (per method) is applied recursively at each deeper level,
treating the current sign as the new starting point.

Real dasa-period boundaries (drik._get_dhasa_end_jd) are used throughout
in place of a fixed average year length, with a sanity backstop against
the average-year estimate and a proportional fallback for sub-day spans
where a fresh ephemeris lookup would be unreliable.
"""
year_duration = const.sidereal_year
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True
# Vishama Pada (direct) / Sama Pada (reverse) sign groups per Neelakanta -
# same as plain odd/even except the four fixed signs are inverted.
_VISHAMA_PADA = {const.ARIES, const.TAURUS, const.GEMINI, const.LIBRA, const.SCORPIO, const.SAGITTARIUS}
# Antardasa offsets (P.S. Sastri), 1-indexed house numbers from the dasa sign.
_ANTARDASA_OFFSETS_ODD = [1, 5, 9, 2, 6, 10, 3, 7, 11, 4, 8, 12]
_ANTARDASA_OFFSETS_EVEN = [1, 9, 5, 12, 8, 4, 11, 7, 3, 10, 6, 2]
# Antardasa step-lists for TRIKONA_METHOD.JHORA, by seed modality (0-indexed
# offsets from the seed; direction applied separately).
_JHORA_AD_STEPS_MOVABLE = list(range(12))
_JHORA_AD_STEPS_FIXED = [(5 * k) % 12 for k in range(12)]
_JHORA_AD_STEPS_DUAL = [0, 3, 6, 9, 4, 7, 10, 1, 8, 11, 2, 5]
# Mahadasa order offsets by modality (movable/fixed/dual), used by
# RAMAN_DWIVEDI_ACHYUTANANDA_JHA, RAGHAVA_BHATTA_NRISIMHA_SURI and
# NEELAKANTA_VRIDDHAKARIKA.
_MD_OFFSETS_MOVABLE = list(range(1, 13))
_MD_OFFSETS_FIXED = [1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12]
_MD_OFFSETS_DUAL = [1, 5, 9, 2, 6, 10, 3, 7, 11, 4, 8, 12]
def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration
def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """ Real dasa-period end JD, guarded by a naive average-year backstop. """
    naive_end = start_jd + duration_in_years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, duration_in_years)
    except Exception:
        return naive_end
    if real_end is None or real_end <= start_jd:
        return naive_end
    if _USE_SANITY_BACKSTOP and abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq):
    """ Splits a parent span into twelve equal children using real dasa-period boundaries. """
    child_years = parent_years / 12.0
    parent_real_days = parent_end_jd - parent_start_jd
    n = len(child_seq)
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        if is_last:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (child_years * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out
# ---------------------------------------------------------------------------
# Antardasa.
# ---------------------------------------------------------------------------
def _antardhasa_sastri(parent_sign):
    """ P.S. Sastri's antardasa rule (see module docstring) - used by all methods except JHORA. """
    offsets = _ANTARDASA_OFFSETS_ODD if parent_sign in const.odd_signs else _ANTARDASA_OFFSETS_EVEN
    return [(parent_sign + (o - 1)) % 12 for o in offsets]
def _antardhasa_jhora(planet_positions, parent_sign):
    """
    Antardasa order for TRIKONA_METHOD.JHORA (see module docstring).
    Seed = stronger(parent_sign, 7th); direction by plain odd/even of the
    seed; step-list by the seed's own modality.
    """
    seventh = (parent_sign + const.HOUSE_7) % 12
    seed = house.stronger_rasi_from_planet_positions(planet_positions, parent_sign, seventh)
    direction = 1 if seed in const.odd_signs else -1
    if seed in const.movable_signs:
        steps = _JHORA_AD_STEPS_MOVABLE
    elif seed in const.fixed_signs:
        steps = _JHORA_AD_STEPS_FIXED
    else:
        steps = _JHORA_AD_STEPS_DUAL
    return [(seed + direction * s) % 12 for s in steps]
def _antardhasa_order(planet_positions, parent_sign, method):
    """ Dispatches to the antardasa rule for the given Mahadasa method. """
    if method == const.TRIKONA_METHOD.JHORA:
        return _antardhasa_jhora(planet_positions, parent_sign)
    return _antardhasa_sastri(parent_sign)
# ---------------------------------------------------------------------------
# Mahadasa seed.
# ---------------------------------------------------------------------------
def _trikona_seed_candidate(planet_positions):
    """ Strongest of the 1st, 5th and 9th houses from Lagna. """
    asc_house = planet_positions[0][1][0]
    trikonas = [asc_house, (asc_house + 4) % 12, (asc_house + 8) % 12]
    sr = house.stronger_rasi_from_planet_positions(planet_positions, trikonas[0], trikonas[1])
    sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, trikonas[2])
    return sr
def _sammukha(sign):
    """ NEELAKANTA_VRIDDHAKARIKA's facing-sign substitution (see module docstring). """
    if sign in const.movable_signs:
        return (sign + 7) % 12
    elif sign in const.fixed_signs:
        return (sign + 5) % 12
    else:
        if sign in const.odd_signs:
            return (sign + 3) % 12
        else:
            return (sign - 3) % 12
def _neelakanta_final_seed(seed_candidate, gender):
    """
    Applies the gender-dependent sammukha substitution described in the
    module docstring for const.GENDER.MALE / FEMALE. For
    const.GENDER.TRANSGENDER and const.GENDER.NO_PREFERENCE, the
    substitution is not defined in the source and is not applied - the
    seed candidate is returned unchanged.
    """
    is_odd = seed_candidate in const.odd_signs
    if gender == const.GENDER.MALE:
        return seed_candidate if is_odd else _sammukha(seed_candidate)
    elif gender == const.GENDER.FEMALE:
        return seed_candidate if not is_odd else _sammukha(seed_candidate)
    else:
        return seed_candidate
# ---------------------------------------------------------------------------
# Mahadasa order.
# ---------------------------------------------------------------------------
def _md_order_jhora(seed):
    direction = 1 if seed in const.odd_signs else -1
    return [(seed + direction * h) % 12 for h in range(12)]
def _modality_offsets(sign):
    if sign in const.movable_signs:
        return _MD_OFFSETS_MOVABLE
    elif sign in const.fixed_signs:
        return _MD_OFFSETS_FIXED
    else:
        return _MD_OFFSETS_DUAL
def _md_order_modality_based(seed, method):
    """ Modality-based order for RAMAN_DWIVEDI_ACHYUTANANDA_JHA and RAGHAVA_BHATTA_NRISIMHA_SURI. """
    offsets = _modality_offsets(seed)
    if method == const.TRIKONA_METHOD.RAMAN_DWIVEDI_ACHYUTANANDA_JHA:
        direct_set = _VISHAMA_PADA
    else:
        direct_set = const.odd_signs
    direction = 1 if seed in direct_set else -1
    return [(seed + direction * (o - 1)) % 12 for o in offsets]
def _md_seed_and_order(planet_positions, method, gender):
    seed_candidate = _trikona_seed_candidate(planet_positions)
    if method == const.TRIKONA_METHOD.JHORA:
        seed = seed_candidate
        order = _md_order_jhora(seed)
    elif method == const.TRIKONA_METHOD.NEELAKANTA_VRIDDHAKARIKA:
        seed = _neelakanta_final_seed(seed_candidate, gender)
        order = _md_order_modality_based(seed, const.TRIKONA_METHOD.RAGHAVA_BHATTA_NRISIMHA_SURI)
    else:
        seed = seed_candidate
        order = _md_order_modality_based(seed, method)
    return seed, order
# ---------------------------------------------------------------------------
# Mahadasa duration.
# ---------------------------------------------------------------------------
def _lord_of_sign_for_trikona(planet_positions, sign, use_dynamic_dual_lord_resolution):
    """
    Resolves a sign's lord for the Mahadasa duration calculation.
    For Scorpio and Aquarius, two lord-resolution approaches are used
    depending on the method:
      - use_dynamic_dual_lord_resolution=True (RAMAN_DWIVEDI_ACHYUTANANDA_
        JHA, NEELAKANTA_VRIDDHAKARIKA): house.house_owner_from_planet_
        positions() performs its own chart-dependent strength comparison
        between the two traditional co-lords (Mars/Ketu for Scorpio,
        Saturn/Rahu for Aquarius) and returns whichever the chart favours.
      - use_dynamic_dual_lord_resolution=False (RAGHAVA_BHATTA_NRISIMHA_
        SURI): const.house_owners gives the fixed, traditional single
        lord for every sign, without any chart-dependent comparison -
        matching this method's own stated preference not to resolve dual
        rulership by strength for duration purposes.
    """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    if use_dynamic_dual_lord_resolution:
        lord = house.house_owner_from_planet_positions(planet_positions, sign)
    else:
        lord = const.house_owners[sign]
    return lord, p_to_h[lord]
def _count_to_lord_duration_with_offset(planet_positions, sign, direct_classification_signs,
                                         count_offset, use_dynamic_dual_lord_resolution):
    """
    Inclusive sign-count from `sign` to its lord (direct if `sign` is in
    `direct_classification_signs`, reverse otherwise), plus count_offset,
    with the own-sign exception giving 12 years and the usual exalted
    (+1) / debilitated (-1) adjustment.
    count_offset is -1 for RAMAN_DWIVEDI_ACHYUTANANDA_JHA and
    NEELAKANTA_VRIDDHAKARIKA, and 0 for RAGHAVA_BHATTA_NRISIMHA_SURI,
    whose duration is the raw inclusive count with no further reduction.
    The exalted/debilitated adjustment is not applied when the resolved
    lord is Rahu or Ketu - the dignity of the nodes is not used in this
    calculation regardless of how the lord was resolved.
    """
    lord, lord_house = _lord_of_sign_for_trikona(planet_positions, sign, use_dynamic_dual_lord_resolution)
    if sign in direct_classification_signs:
        count = ((lord_house - sign) % 12) + 1
    else:
        count = ((sign - lord_house) % 12) + 1
    if count == 1:
        period = 12
    else:
        period = count + count_offset
    if lord in (const.RAHU_ID, const.KETU_ID):
        pass
    elif const.house_strengths_of_planets[lord][lord_house] == const._EXALTED_UCCHAM:
        period += 1
    elif const.house_strengths_of_planets[lord][lord_house] == const._DEBILITATED_NEECHAM:
        period -= 1
    return period
def _md_duration(planet_positions, sign, method):
    if method == const.TRIKONA_METHOD.JHORA:
        return float(narayana._dhasa_duration(planet_positions, sign))
    elif method == const.TRIKONA_METHOD.RAMAN_DWIVEDI_ACHYUTANANDA_JHA:
        return float(_count_to_lord_duration_with_offset(
            planet_positions, sign, _VISHAMA_PADA, -1,
            use_dynamic_dual_lord_resolution=True))
    elif method == const.TRIKONA_METHOD.RAGHAVA_BHATTA_NRISIMHA_SURI:
        return float(_count_to_lord_duration_with_offset(
            planet_positions, sign, const.odd_signs, 0,
            use_dynamic_dual_lord_resolution=False))
    else:  # NEELAKANTA_VRIDDHAKARIKA
        return float(_count_to_lord_duration_with_offset(
            planet_positions, sign, _VISHAMA_PADA, -1,
            use_dynamic_dual_lord_resolution=True))
# ---------------------------------------------------------------------------
# Public entry points.
# ---------------------------------------------------------------------------
def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,
    method=None,
    gender=const.GENDER.MALE,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Trikona Dasha, computed to the requested depth (1 = Mahadasa only,
    up to 6 = Mahadasa through Deha-antardasa).
    @param method: a const.TRIKONA_METHOD member, or None to use
        const.trikona_dhasa_method_default.
    @param gender: a const.GENDER member. Used only by
        NEELAKANTA_VRIDDHAKARIKA, whose seed derivation depends on the
        native's gender (see module docstring); ignored by every other
        method.
    @return: list of rows, each (lords_tuple, start_tuple, duration_years)
    """
    if method is None:
        method = const.trikona_dhasa_method_default
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    seed, md_lords = _md_seed_and_order(planet_positions, method, gender)
    rows = []
    start_jd = jd_at_dob
    def _append_row(labels, start_jd_val, seg_years):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))
    def _recurse(level, parent_lord, pstart_jd, parent_years, parent_end_jd, prefix):
        child_seq = _antardhasa_order(planet_positions, parent_lord, method)
        child_years = parent_years / 12.0
        child_bounds = _split_into_children(place, pstart_jd, parent_end_jd, parent_years, child_seq)
        if level + 1 == lvl:
            for c, (child_start_jd, _child_end_jd) in zip(child_seq, child_bounds):
                _append_row(prefix + (c,), child_start_jd, child_years)
            return parent_end_jd
        for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
            _recurse(level + 1, c, child_start_jd, child_years, child_end_jd, prefix + (c,))
        return parent_end_jd
    for md_lord in md_lords:
        md_years = _md_duration(planet_positions, md_lord, method)
        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        if lvl == 1:
            _append_row((md_lord,), start_jd, md_years)
        else:
            _recurse(1, md_lord, start_jd, md_years, md_end_jd, (md_lord,))
        start_jd = md_end_jd
    return rows
def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    divisional_chart_factor: int = 1,
    method=None,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    jd_at_dob=None,
    place=None,
    **kwargs
):
    """
    Returns the twelve immediate antardasa children of a given parent
    span. `parent_lords`' last element is always a level-2-or-deeper
    sign. `method` selects the antardasa rule (see module docstring);
    None uses const.trikona_dhasa_method_default. TRIKONA_METHOD.JHORA's
    antardasa rule needs the chart, so jd_at_dob/place are required for
    that method.
    """
    if method is None:
        method = const.trikona_dhasa_method_default
    if place is not None and jd_at_dob is not None:
        _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, place, parent_years)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []
    planet_positions = None
    if method == const.TRIKONA_METHOD.JHORA:
        if jd_at_dob is None or place is None:
            raise ValueError("jd_at_dob and place are required for TRIKONA_METHOD.JHORA")
        planet_positions = charts.divisional_chart(
            jd_at_dob, place,
            divisional_chart_factor=divisional_chart_factor, **kwargs
        )[:const._pp_count_upto_ketu]
    child_seq = _antardhasa_order(planet_positions, parent_sign, method)
    child_bounds = _split_into_children(place, start_jd, end_jd, parent_years, child_seq)
    rows = []
    for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
        if child_end_jd > child_start_jd:
            rows.append((path + (c,), _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)))
    return rows
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    method=None,
    gender=const.GENDER.MALE,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Returns the running dasa/antardasa chain, from Mahadasa down to the
    requested depth, for `current_jd`.
    """
    if method is None:
        method = const.trikona_dhasa_method_default
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor, **kwargs
    )[:const._pp_count_upto_ketu]
    seed, md_lords = _md_seed_and_order(planet_positions, method, gender)
    md_entries = []
    cursor_jd = jd_at_dob
    for md_lord in md_lords:
        md_years = _md_duration(planet_positions, md_lord, method)
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        md_entries.append((md_lord, cursor_jd, md_end_jd, md_years))
        cursor_jd = md_end_jd
    located_entry = None
    for md, seg_start, seg_end, seg_years in md_entries:
        if seg_start <= current_jd < seg_end:
            located_entry = (md, seg_start, seg_end, seg_years)
            break
    if located_entry is None:
        located_entry = md_entries[-1]
    md_sign, md_start, md_end, md_years = located_entry
    ladder = [([md_sign], utils.julian_day_to_date_time_string(md_start),
               utils.julian_day_to_date_time_string(md_end))]
    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder
    parent_lords = [md_sign]
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_years
    parent_sign = md_sign
    for level in range(2, target + 1):
        child_seq = _antardhasa_order(planet_positions, parent_sign, method)
        child_bounds = _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq)
        child_years = parent_years / 12.0
        chosen = None
        for c, (c_start, c_end) in zip(child_seq, child_bounds):
            if c_start <= current_jd < c_end:
                chosen = (c, c_start, c_end)
                break
        if chosen is None:
            chosen = (child_seq[-1], child_bounds[-1][0], child_bounds[-1][1])
        child_sign, child_start_jd, child_end_jd = chosen
        parent_lords = parent_lords + [child_sign]
        ladder.append((parent_lords, utils.julian_day_to_date_time_string(child_start_jd),
                       utils.julian_day_to_date_time_string(child_end_jd)))
        parent_sign = child_sign
        parent_start_jd, parent_end_jd, parent_years = child_start_jd, child_end_jd, child_years
    return ladder
if __name__ == "__main__":
    utils.set_language('en')
    import time
    def _print_md_table(dob, tob, place, method, label):
        print("=" * 70)
        print(f"Method: {method.name}  ({label})")
        print("=" * 70)
        rows = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=1, method=method)
        for lords, start_tuple, dur_years in rows:
            lord_name = utils.RAASI_SHORT_LIST[lords[0]]
            y_, m_, d_, fh_ = start_tuple
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs")
        print()
    # Book examples - Methods 1, 2 and 3 each carry their own worked
    # example and date, per the source article; the JHora method is
    # exercised separately against the two charts used elsewhere in this
    # project's rasi-dasa work.
    book_dob = drik.Date(1927, 5, 21)
    book_tob = (18, 30, 0)
    book_place = drik.Place('Unknown', 0.0, 0.0, 0.0)
    for method in [const.TRIKONA_METHOD.RAMAN_DWIVEDI_ACHYUTANANDA_JHA,
                   const.TRIKONA_METHOD.RAGHAVA_BHATTA_NRISIMHA_SURI,
                   const.TRIKONA_METHOD.NEELAKANTA_VRIDDHAKARIKA]:
        _print_md_table(book_dob, book_tob, book_place, method, "book example, 1927-05-21")
    for chart_label, dob, tob in [
        ("1996-12-07", drik.Date(1996, 12, 7), (10, 34, 0)),
        ("2004-06-25", drik.Date(2004, 6, 25), (14, 47, 0)),
        ("1996-01-11", drik.Date(1995, 1, 11), (15, 50, 37)),
    ]:
        place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
        _print_md_table(dob, tob, place, const.TRIKONA_METHOD.JHORA, chart_label)
        jd_at_dob = utils.julian_day_number(dob, tob)
        y, m, d, hh, mm, ss = 2010, 11, 9, 15, 29, 45
        current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
        print(f"--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss}, {chart_label} ---")
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
        )
        for lords, start_str, end_str in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:15s} {start_str}  ->  {end_str}")
        print('elapsed time', time.time() - start_time)
        print()
