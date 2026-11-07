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
from jhora.horoscope.chart import charts, house
"""
Sthira Dasa.

Seed: Brahma's sign. MD: from the seed over 12 signs, duration by modality
(movable=7yr, fixed=8yr, dual=9yr).

const.STHIRA_METHOD selects how Brahma is derived and which direction the
dasa signs run.

  PVR_BOOK   Brahma via house.brahma(). Antardasa seed = stronger of the
             parent sign and its 7th, always forward. Does not match JHora
             antardasas - kept available, not the default.

  PVR_JHORA  Brahma via house.brahma(). Antardasa via the narayana rule.
             Matches JHora. Default.

  PVR_PAPER  Brahma via house.brahma_new(), per P.V.R. Narasimha Rao,
             "Sthira Dasa of Parasara - An Independent Interpretation"
             (2009). Corrects three gaps in house.brahma(): the
             Maheswara/Saturn exclusion and weekday-order substitution,
             multi-way tie handling, and the invisible-half window (6 houses
             from the reference inclusive, not 7). The article covers Brahma
             only; the rest of the reckoning is as PVR_JHORA.

  SANTHANAM  Brahma via house.brahma(). Dasa signs run zodiacally when the
             Brahma planet is in an odd sign and anti-zodiacally when it is
             in an even sign, per Santhanam's translation of BPHS. PVR
             reports this reading and rejects it, holding that Parasara gave
             specific guidelines wherever required and that in their absence
             the order is always zodiacal. Both readings are offered.
             Antardasa via the narayana rule.

  RANGACHARYA
             Brahma per Iranganti Rangacharya, "Sthira Dasa - Exposition"
             (Saptarishis Astrology, 2009), from his Jaimini Sutramritam.
             Takes the stronger of the janma lagna and its 7th, then among
             that sign's 6th, 8th and 12th lords keeps those standing in the
             1st, 3rd or 5th from it, and makes the strongest of those
             Brahma. Saturn is a valid candidate: he rejects Neelakanta's
             exclusion of Saturn from Brahmahood, since Saturn is eligible
             to be Rudra and Maheswara. Dasa signs always run in direct
             order, whether the Brahma sign is odd or even. Antardasa via
             the narayana rule.

             His placement test can leave no candidate, and he holds Sthira
             dasa applicable only where Brahma is present. Neelakanta method
             is used as fallback.

  KN_RAO     Takes the stronger of the lagna and the 7th, then the strongest
             of the 6th, 8th and 12th lords counted from it. If that is
             Saturn it is passed over and the next strongest taken. Strength
             is the sum of graha bala, chara bala, sthira bala and drishti
             bala - see _kn_rao_planet_balas(). Dasa signs run in direct
             order. Antardasa follows the same direct order from the
             Mahadasa sign, each one twelfth of the Mahadasa.

V5.0 - Refactored to match JHora. Added Santhanam, Rangacharya, KN Rao methods
"""
year_duration = const.sidereal_year
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True

_ZODIACAL = 1
_REVERSE = -1

# Houses from the reference sign in which Brahma may stand: the 1st, 3rd
# and 5th. Where the reference is the 7th, these are the same houses as the
# 7th, 9th and 11th counted from the lagna.
_RANGACHARYA_PLACEMENTS = (0, 2, 4)

# KN Rao's four terms then map onto strength.shad_bala() as:
#
#   graha bala   -> sb_sum, the shadbala total          index 6
#   chara bala   -> cheshta bala, motional strength     index 3
#   sthira bala  -> sthana bala, positional strength    index 0
#   drishti bala -> drik bala, aspectual strength       index 5
#
# Sthana, cheshta and drik are themselves components of shadbala, so this
# sum weights those three twice over. That is what the four named terms
# add up to, taken literally. Set KN_RAO_GRAHA_BALA_AS_SHADBALA = False to
# read graha bala as naisargika bala instead, which leaves the four terms
# disjoint and equal to four of the six shadbala parts, omitting kaala and
# dig.
KN_RAO_GRAHA_BALA_AS_SHADBALA = True

_SHAD_BALA_STHANA = 0
_SHAD_BALA_CHESHTA = 3
_SHAD_BALA_NAISARGIKA = 4
_SHAD_BALA_DRIK = 5
_SHAD_BALA_TOTAL = 6

_kn_rao_bala_cache = {}


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd, place=place, dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _dhasa_duration(lord):
    """Return the Mahadasa duration (years) of lord's sign, by modality."""
    if lord in const.movable_signs:
        return 7
    elif lord in const.fixed_signs:
        return 8
    else:
        return 9


def _planet_sign(planet_positions, planet):
    return planet_positions[planet + 1][1][0]


def _dusthana_lords(planet_positions, reference_sign):
    """Return the 6th, 8th and 12th lords counted from reference_sign."""
    lords = []
    for h in (const.HOUSE_6, const.HOUSE_8, const.HOUSE_12):
        lord = house.house_owner_from_planet_positions(
            planet_positions, (reference_sign + h) % 12)
        if lord not in lords:
            lords.append(lord)
    return lords


def _stronger_of_lagna_and_seventh(planet_positions):
    """Return the stronger of the lagna and its 7th."""
    lagna = planet_positions[0][1][0]
    seventh = (lagna + const.HOUSE_7) % 12
    return house.stronger_rasi_from_planet_positions(planet_positions, lagna, seventh)


def _strongest_planet(planet_positions, planets):
    """Return the strongest of planets, compared pairwise."""
    best = planets[0]
    for p in planets[1:]:
        best = house.stronger_planet_from_planet_positions(planet_positions, best, p)
    return best


def kn_rao_planet_balas(jd, place):
    """Return the KN Rao strength of each planet, Sun to Saturn.

    Graha bala + chara bala + sthira bala + drishti bala, all drawn from a
    single strength.shad_bala() call. Returns Neelakantha Brahma if strength.py cannot
    supply them.
    """
    key = (jd, place)
    if key in _kn_rao_bala_cache:
        return _kn_rao_bala_cache[key]
    from jhora.horoscope.chart import strength
    sb = strength.shad_bala(jd, place)
    graha = sb[_SHAD_BALA_TOTAL]
    totals = [round(float(graha[p]), 2) for p in const.SUN_TO_SATURN]
    _kn_rao_bala_cache[key] = totals
    return totals


def _kn_rao_brahma(planet_positions, jd=None, place=None):
    """Return the Brahma planet per KN Rao.

    The strongest of the 6th, 8th and 12th lords from the stronger of the
    lagna and the 7th becomes Brahma; if that is Saturn it is passed over
    and the next strongest taken.

    """
    reference = _stronger_of_lagna_and_seventh(planet_positions)
    candidates = _dusthana_lords(planet_positions, reference)
    balas = kn_rao_planet_balas(jd, place)
    ordered = sorted(candidates, key=lambda p: balas[p], reverse=True)
    for p in ordered:
        if p != const.SATURN_ID:
            return p
    return ordered[0]


def kn_rao_brahma_workings(planet_positions, jd=None, place=None):
    """Return the reasoning behind the KN Rao Brahma for a chart.

    Gives the reference sign, each of the 6th/8th/12th lords with its bala,
    and the Brahma finally chosen.
    """
    reference = _stronger_of_lagna_and_seventh(planet_positions)
    candidates = _dusthana_lords(planet_positions, reference)
    balas = kn_rao_planet_balas(jd, place) if (jd is not None and place is not None) else None
    rows = [{'planet': p, 'sign': _planet_sign(planet_positions, p),
             'bala': None if balas is None else balas[p],
             'saturn_passed_over': p == const.SATURN_ID} for p in candidates]
    return {'lagna': planet_positions[0][1][0], 'reference_sign': reference,
            'bala_source': 'strength.shad_bala' if balas is not None else 'house pairwise',
            'lords': rows,
            'brahma': _kn_rao_brahma(planet_positions, jd, place)}


def _rangacharya_brahma(planet_positions):
    """Return the Brahma planet per Rangacharya, or None if Brahma is absent.

    Of the 6th, 8th and 12th lords, only those standing in the 1st, 3rd or
    5th from the reference sign are considered, and the strongest of those
    becomes Brahma. Lords placed elsewhere are set aside before strength is
    weighed: in one of his charts two of the three lords are dropped as
    "being on the other side, 12th", and in another the Brahma is named on
    placement alone with no comparison of strength.
    """
    reference = _stronger_of_lagna_and_seventh(planet_positions)
    candidates = [
        p for p in _dusthana_lords(planet_positions, reference)
        if ((_planet_sign(planet_positions, p) - reference) % 12)
        in _RANGACHARYA_PLACEMENTS
    ]
    if candidates:
        return _strongest_planet(planet_positions, candidates)
    return house.brahma(planet_positions)


def rangacharya_brahma_workings(planet_positions):
    """Return the reasoning behind the Rangacharya Brahma for a chart.

    Gives the reference sign, each of the 6th/8th/12th lords with the house
    it occupies from that reference, whether it is eligible, and the Brahma
    finally chosen. Intended for checking a chart by hand against the worked
    examples in the article.
    """
    reference = _stronger_of_lagna_and_seventh(planet_positions)
    rows = []
    for p in _dusthana_lords(planet_positions, reference):
        sign = _planet_sign(planet_positions, p)
        houses_away = (sign - reference) % 12
        rows.append({'planet': p, 'sign': sign, 'house_from_reference': houses_away + 1,
                     'eligible': houses_away in _RANGACHARYA_PLACEMENTS})
    return {'lagna': planet_positions[0][1][0], 'reference_sign': reference,
            'lords': rows,
            'brahma': _rangacharya_brahma(planet_positions),
            'neelakanta_brahma': house.brahma(planet_positions)}


def _brahma_planet(planet_positions, dhasa_method=None, jd=None, place=None):
    """Return the Brahma planet, or None if absent."""
    if dhasa_method is None:
        dhasa_method = const.sthira_dhasa_default_method
    if dhasa_method == const.STHIRA_METHOD.PVR_PAPER:
        return house.brahma_new(planet_positions)
    if dhasa_method == const.STHIRA_METHOD.RANGACHARYA:
        return _rangacharya_brahma(planet_positions)
    if dhasa_method == const.STHIRA_METHOD.KN_RAO:
        return _kn_rao_brahma(planet_positions, jd, place)
    return house.brahma(planet_positions)


def _brahma_sign(planet_positions, dhasa_method=None, jd=None, place=None):
    """Return the Brahma seed sign, or None if Brahma is absent."""
    bp = _brahma_planet(planet_positions, dhasa_method, jd, place)
    return None if bp is None else _planet_sign(planet_positions, bp)


def _md_direction(seed, dhasa_method):
    """Return the direction of the Mahadasa walk from the seed sign."""
    if dhasa_method == const.STHIRA_METHOD.SANTHANAM:
        return _ZODIACAL if seed in const.odd_signs else _REVERSE
    return _ZODIACAL


def _maha_dhasa_lords(planet_positions, dhasa_method=None, jd=None, place=None):
    """Return the 12 Mahadasa signs in order, or [] if Brahma is absent."""
    seed = _brahma_sign(planet_positions, dhasa_method, jd, place)
    if seed is None:
        return []
    direction = _md_direction(seed, dhasa_method)
    return [(seed + direction * i) % 12 for i in range(12)]


def _pvr_book_antardhasa(planet_positions, parent_sign):
    """Return the antardasa order per const.STHIRA_METHOD.PVR_BOOK."""
    seventh = (parent_sign + const.HOUSE_7) % 12
    seed = house.stronger_rasi_from_planet_positions(planet_positions, parent_sign, seventh)
    return [(seed + i) % 12 for i in range(12)]


def _antardhasa_order(planet_positions, parent_sign, dhasa_method=None):
    """Return the antardasa order for parent_sign.

    KN Rao runs the antardasas in the same direct order as the Mahadasas,
    beginning from the Mahadasa sign. The Santhanam direction rule applies
    to the Mahadasa signs only.
    """
    from jhora.horoscope.dhasa.raasi.narayana import _narayana_antardhasa
    if dhasa_method is None:
        dhasa_method = const.sthira_dhasa_default_method
    if dhasa_method == const.STHIRA_METHOD.PVR_BOOK:
        return _pvr_book_antardhasa(planet_positions, parent_sign)
    if dhasa_method == const.STHIRA_METHOD.KN_RAO:
        return [(parent_sign + i) % 12 for i in range(12)]
    return _narayana_antardhasa(planet_positions, parent_sign)


def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """Return the real (transit-based) end JD, with a naive-estimate backstop."""
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
    """Return the (start,end) JD pairs for each of the 12 children."""
    child_years = parent_years / 12.0
    parent_real_days = parent_end_jd - parent_start_jd
    n = len(child_seq)
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        if idx == n - 1:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (child_years * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out


def get_dhasa_antardhasa(
    dob, tob, place, divisional_chart_factor=1, years=1, months=1,
    sixty_hours=1, dhasa_level_index=2, round_duration=False,
    dhasa_duration_type=None, savana_year_method=None, dhasa_method=None,
    **kwargs
):
    """Return dhasa/antardhasa periods, depth-enabled.

    dhasa_method: any const.STHIRA_METHOD member. Returns [] when the chart
    has no Brahma under the chosen method.
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    md_lords = _maha_dhasa_lords(planet_positions, dhasa_method, jd_at_dob, place)
    if not md_lords:
        return []
    dhasa_info = []
    start_jd = jd_at_dob

    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, dhasa_level_index + 1)
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))

    def _expand_children(start_jd_val, end_jd_val, parent_duration_years,
                         parent_lords_stack, current_level, target_level):
        if current_level == target_level:
            _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)
            return end_jd_val
        children = _antardhasa_order(planet_positions, parent_lords_stack[-1],
                                     dhasa_method=dhasa_method)
        child_duration = parent_duration_years / 12.0
        child_bounds = _split_into_children(place, start_jd_val, end_jd_val,
                                            parent_duration_years, children)
        for child_lord, (c_start, c_end) in zip(children, child_bounds):
            _expand_children(c_start, c_end, child_duration,
                             parent_lords_stack + [child_lord],
                             current_level + 1, target_level)
        return end_jd_val

    for md_lord in md_lords:
        md_years = _dhasa_duration(md_lord)
        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        _expand_children(start_jd, md_end_jd, md_years, [md_lord],
                         current_level=1, target_level=dhasa_level_index)
        start_jd = md_end_jd
    return dhasa_info


def get_immediate_children(
    parent_lords, parent_start, parent_duration=None, parent_end=None, *,
    jd_at_dob, place, divisional_chart_factor: int = 1, years: int = 1,
    months: int = 1, sixty_hours: int = 1, round_duration: bool = False,
    dhasa_duration_type=None, savana_year_method=None, dhasa_method=None,
    **kwargs
):
    """Return immediate child periods for a parent dasha."""
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
    pp = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    child_signs = _antardhasa_order(pp, parent_sign, dhasa_method=dhasa_method)
    child_bounds = _split_into_children(place, start_jd, end_jd, parent_years, child_signs)
    return [(path + (sgn,), utils.jd_to_gregorian(cs), utils.jd_to_gregorian(ce))
            for sgn, (cs, ce) in zip(child_signs, child_bounds) if ce > cs]


def get_running_dhasa_for_given_date(
    current_jd, jd_at_dob, place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA, *,
    divisional_chart_factor: int = 1, years: int = 1, months: int = 1,
    sixty_hours: int = 1, round_duration: bool = False,
    dhasa_duration_type=None, savana_year_method=None, dhasa_method=None,
    **kwargs
):
    """Return the running dhasa sequence for a given date."""
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(int(const.MAHA_DHASA_DEPTH.DEHA),
                   max(int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), d))

    target = _norm(dhasa_level_index)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    md_lords = _maha_dhasa_lords(planet_positions, dhasa_method, jd_at_dob, place)
    if not md_lords:
        return []
    md_entries = []
    cursor_jd = jd_at_dob
    for md in md_lords:
        md_years = _dhasa_duration(md)
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        md_entries.append((md, cursor_jd, md_end_jd, md_years))
        cursor_jd = md_end_jd
    located_entry = None
    for entry in md_entries:
        if entry[1] <= current_jd < entry[2]:
            located_entry = entry
            break
    if located_entry is None:
        located_entry = md_entries[-1]
    md_sign, md_start, md_end, md_yrs = located_entry
    ladder = [([md_sign], utils.julian_day_to_date_time_string(md_start),
               utils.julian_day_to_date_time_string(md_end))]
    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder
    parent_lords = [md_sign]
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_yrs
    parent_sign = md_sign
    for _level in range(2, target + 1):
        child_seq = _antardhasa_order(planet_positions, parent_sign, dhasa_method=dhasa_method)
        child_bounds = _split_into_children(place, parent_start_jd, parent_end_jd,
                                            parent_years, child_seq)
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
        ladder.append((parent_lords,
                       utils.julian_day_to_date_time_string(child_start_jd),
                       utils.julian_day_to_date_time_string(child_end_jd)))
        parent_sign = child_sign
        parent_start_jd, parent_end_jd, parent_years = child_start_jd, child_end_jd, child_years
    return ladder


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    dob = drik.Date(2004, 6, 25)
    tob = (14, 47, 0)
    dob = drik.Date(1995, 1, 11)
    tob = (15, 50,37)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    dcf = 1
    _METHODS = [const.STHIRA_METHOD.PVR_BOOK, const.STHIRA_METHOD.PVR_JHORA,
                const.STHIRA_METHOD.PVR_PAPER, const.STHIRA_METHOD.SANTHANAM,
                const.STHIRA_METHOD.RANGACHARYA, const.STHIRA_METHOD.KN_RAO]
    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)
        print("\n--- MD-only table (single pass, 12 signs, real JD boundaries) ---", dob)
        md_only_rows = get_dhasa_antardhasa(
            dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd,
            divisional_chart_factor=dcf
        )
        for lords, start_tuple, dur_years in md_only_rows:
            lord_name = utils.RAASI_SHORT_LIST[lords[0]]
            y_, m_, d_, fh_ = start_tuple
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs")
        pp = charts.divisional_chart(jd_at_dob, place,
                                     divisional_chart_factor=dcf)[:const._pp_count_upto_ketu]
        print("\n--- Brahma by method ---")
        for _method in _METHODS:
            bp = _brahma_planet(pp, _method, jd_at_dob, place)
            print(f"{_method.name:12s} " + ("absent" if bp is None else
                  f"planet {bp} in {utils.RAASI_SHORT_LIST[_planet_sign(pp, bp)]}"))
        w = rangacharya_brahma_workings(pp)
        print("\n--- Rangacharya Brahma workings ---")
        print(f"lagna={utils.RAASI_SHORT_LIST[w['lagna']]} "
              f"reference={utils.RAASI_SHORT_LIST[w['reference_sign']]}")
        for r in w['lords']:
            print(f"  planet {r['planet']} in {utils.RAASI_SHORT_LIST[r['sign']]}, "
                  f"{r['house_from_reference']}th from reference, "
                  f"eligible={r['eligible']}")
        print(f"  rangacharya brahma={w['brahma']}  neelakanta brahma={w['neelakanta_brahma']}")
        k = kn_rao_brahma_workings(pp, jd_at_dob, place)
        print("\n--- KN Rao Brahma workings ---")
        print(f"lagna={utils.RAASI_SHORT_LIST[k['lagna']]} "
              f"reference={utils.RAASI_SHORT_LIST[k['reference_sign']]} "
              f"balas from {k['bala_source']}")
        for r in k['lords']:
            print(f"  planet {r['planet']} in {utils.RAASI_SHORT_LIST[r['sign']]}, "
                  f"bala={r['bala']}"
                  + ("  (Saturn - passed over)" if r['saturn_passed_over'] else ""))
        print(f"  brahma={k['brahma']}")
        for _method in _METHODS:
            print(f"\n--- MD table (method={_method.name}) ---")
            rows = get_dhasa_antardhasa(
                dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd,
                divisional_chart_factor=dcf, dhasa_method=_method)
            if not rows:
                print("no Brahma - Sthira dasa not applicable")
                continue
            print(','.join(utils.RAASI_SHORT_LIST[r[0][0]] for r in rows))
        for _method in _METHODS:
            print(f"\n--- MD -> AD table (level 2, method={_method.name}) ---")
            md_ad_rows = get_dhasa_antardhasa(
                dob, tob, place, dhasa_level_index=2, dhasa_duration_type=dd,
                divisional_chart_factor=dcf, dhasa_method=_method
            )
            if not md_ad_rows:
                print("no Brahma - Sthira dasa not applicable")
                continue
            md_ad_seq = {}
            for lords, start_tuple, dur_years in md_ad_rows:
                md_name = utils.RAASI_SHORT_LIST[lords[0]]
                ad_name = utils.RAASI_SHORT_LIST[lords[1]]
                md_ad_seq.setdefault(md_name, []).append(ad_name)
            for md_name, ad_list in md_ad_seq.items():
                print(md_name, "->", ','.join(ad_list))
        print(f"\n--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss} [default method] ---")
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            divisional_chart_factor=dcf,
        )
        for lords, start_str, end_str in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:15s} {start_str}  ->  {end_str}")
        print('elapsed time', time.time() - start_time)
