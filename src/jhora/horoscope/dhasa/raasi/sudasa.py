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
Sudasa Dasa.

Seed: Sree Lagna (SL) - Lagna advanced by Moon's nakshatra-fraction of 360d.
MD order: from SL, progress through quadrants, panapharas, apoklimas
(houses 1,4,7,10, 2,5,8,11, 3,6,9,12). MD duration: as in Narayana Dasa.
The first Mahadasa's TRUE start (before birth) is found via
drik._get_dhasa_start_jd(), using the fraction of that Mahadasa already
elapsed at birth (1 minus (30 - SL's degree in its own sign)/30). Its end
is then computed from that true start using the FULL duration - exactly
how Vimsottari handles a fractional first dasa: the first Mahadasa's
returned start is the true, pre-birth start_jd, not birth itself, and
every level (antardasa and below) is built from that same true start
forward with full durations throughout.

const.SUDASA_METHOD (default PVR_JHORA):
  - PVR_BOOK: Ch. 20, "Vedic Astrology: An Integrated Approach". Direction:
    forward if SL is an odd sign, backward if even (plain odd/even). No
    Saturn/Ketu exception. Antardasa is not covered by the book; uses
    const.SUDASA_ANTARDASA_OPTION (JHora's own dialog default: stronger of
    dasa-sign/7th).
  - PVR_BLOG: indiadivine.org, "Sudasa calculation and interpretation".
    Ref: https://www.indiadivine.org/content/topic/1503384-lesson-15-sudasa-calculation-and-interpretation/
    Same MD progression as the book, with an added direction exception:
    Saturn in the sign forces forward; Ketu in the sign reverses whatever
    odd/even gives. Antardasa: quadrant/panaphara/apoklima progression
    from the dasa sign, same exception rule.
  - PVR_JHORA (default): matches JHora's actual MD order. Each of the 3
    groups (Kendras/Panapharas/Apoklimas from SL) is seeded independently
    by cascading house.stronger_rasi_from_planet_positions() through its
    own 4 candidate signs, then walked through its own house-list (built
    in natural house-number order) starting at the winning seed, stepping
    by direction. Direction: SL odd -> forward; SL even -> backward; SL a
    dual sign -> forward, overriding the even/odd result.
    Antardasa (level 2+): seed = stronger(dhasa_lord, 7th_from_dhasa_lord),
    direction = plain odd/even of that seed, with the same Saturn-forces-
    forward/Ketu-reverses exception as PVR_BLOG.

Release History
----------------
V5.0 - Refactored to match JHora (PVR_JHORA, default) and added PVR_BOOK
and PVR_BLOG as selectable alternatives. Fixed the first-Mahadasa JD
calculation (see above) - the previous version computed the first MD's
end directly from a scaled-down fractional duration starting at birth,
which was off from real JHora by about a day, unchanged at every level
below it.
"""
year_duration = const.sidereal_year
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True
_SUDASA_MD_HOUSE_NUMBERS = [1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12]
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
def _bounded_start_jd(jd_birth, place, fraction_elapsed, total_dasa_years):
    """
    Return the TRUE (pre-birth) start JD of the first dasa, given the
    fraction of its full duration already elapsed at birth. Mirrors
    _bounded_end_jd()'s real-vs-naive-estimate safety pattern.
    """
    naive_start = jd_birth - fraction_elapsed * total_dasa_years * year_duration
    try:
        real_start = drik._get_dhasa_start_jd(jd_birth, place, fraction_elapsed=fraction_elapsed,
                                               total_dasa_years=total_dasa_years)
    except Exception:
        return naive_start
    if real_start is None or real_start >= jd_birth:
        return naive_start
    if _USE_SANITY_BACKSTOP and abs(real_start - naive_start) > _BACKSTOP_DAYS:
        return naive_start
    return real_start
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq):
    """Return the (start,end) JD pairs for each child in child_seq."""
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
def _direction_for_sign(planet_positions, sign, dhasa_method=None):
    """Return the odd/even direction for sign, per dhasa_method."""
    if dhasa_method is None:
        dhasa_method = const.sudasa_dhasa_method_default
    if dhasa_method in (const.SUDASA_METHOD.PVR_BLOG, const.SUDASA_METHOD.PVR_JHORA):
        if planet_positions[const.SATURN_ID + 1][1][0] == sign:
            return 1
        direction = 1 if sign in const.odd_signs else -1
        if planet_positions[const.KETU_ID + 1][1][0] == sign:
            direction *= -1
        return direction
    return 1 if sign in const.odd_signs else -1
def _sudasa_md_order(planet_positions, seed_sign, dhasa_method=None):
    """Return the 12 Mahadasa lords, starting from seed_sign."""
    direction = _direction_for_sign(planet_positions, seed_sign, dhasa_method)
    return [(seed_sign + direction * (k - 1)) % 12 for k in _SUDASA_MD_HOUSE_NUMBERS]
def _quadrant_progression_from_sign(planet_positions, s, dhasa_method=None):
    """Return the 12-sign quadrant/panaphara/apoklima progression from s."""
    direction = _direction_for_sign(planet_positions, s, dhasa_method)
    out = []
    anchor = s
    for _ in range(3):
        out.extend((anchor + direction * k) % 12 for k in (0, 3, 6, 9))
        anchor = (anchor + direction) % 12
    return out
# ---------------------------------------------------------------------------
# PVR_JHORA - group-independent MD seed selection + direction.
# ---------------------------------------------------------------------------
def _cascade_stronger(planet_positions, candidates):
    """Return the strongest of candidates, by repeated pairwise comparison."""
    winner = candidates[0]
    for c in candidates[1:]:
        winner = house.stronger_rasi_from_planet_positions(planet_positions, winner, c)
    return winner
def _jhora_direction(sl_sign):
    """Return the MD/group direction: SL odd->forward, even->backward,
    dual->forward (overrides even/odd), applied identically to all 3 groups."""
    if sl_sign in const.dual_signs:
        return 1
    return 1 if sl_sign in const.odd_signs else -1
def _jhora_md_seed_and_order(planet_positions, sl_sign):
    """Return the 12 Mahadasa lords. Each of the 3 groups (Kendra/Panaphara/
    Apoklima houses from SL) is seeded via _cascade_stronger(), then walked
    through its own house-list starting at that seed, per _jhora_direction()."""
    direction = _jhora_direction(sl_sign)
    kendras = [(sl_sign + h) % 12 for h in (0, 3, 6, 9)]
    panapharas = [(sl_sign + h) % 12 for h in (1, 4, 7, 10)]
    apoklimas = [(sl_sign + h) % 12 for h in (2, 5, 8, 11)]
    def _walk(group, seed):
        idx = group.index(seed)
        return [group[(idx + direction * k) % 4] for k in range(4)]
    g1 = _walk(kendras, _cascade_stronger(planet_positions, kendras))
    g2 = _walk(panapharas, _cascade_stronger(planet_positions, panapharas))
    g3 = _walk(apoklimas, _cascade_stronger(planet_positions, apoklimas))
    return g1 + g2 + g3
def _default_antardhasa_option(dhasa_method):
    """Return the default antardasa option for dhasa_method."""
    if dhasa_method == const.SUDASA_METHOD.PVR_BLOG:
        return const.SUDASA_ANTARDASA_OPTION.QUADRANTS_FROM_DHASA_SIGN_ODD_FORWARD_EVEN_REVERSE
    if dhasa_method == const.SUDASA_METHOD.PVR_JHORA:
        return const.SUDASA_ANTARDASA_OPTION.STRONGER_DHASA_7th_ODD_FORWARD_EVEN_REVERSE
    return const.sudasa_antardhasa_default_option
def _antardhasa(planet_positions, dhasa_lord, antardhasa_option=None, dhasa_method=None):
    """Return the antardasa order for dhasa_lord, per const.SUDASA_ANTARDASA_OPTION."""
    if dhasa_method is None:
        dhasa_method = const.sudasa_dhasa_method_default
    if antardhasa_option is None:
        antardhasa_option = _default_antardhasa_option(dhasa_method)
    opt = const.SUDASA_ANTARDASA_OPTION
    dhasa_lord_7th = (dhasa_lord + const.HOUSE_7) % 12
    if antardhasa_option == opt.DHASA_SIGN_ODD_FORWARD_EVEN_REVERSE:
        seed = dhasa_lord
        direction = _direction_for_sign(planet_positions, seed, dhasa_method)
        return [(seed + direction * h) % 12 for h in range(12)]
    elif antardhasa_option == opt.STRONGER_DHASA_7th_ODD_FORWARD_EVEN_REVERSE:
        seed = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_lord, dhasa_lord_7th)
        direction = _direction_for_sign(planet_positions, seed, dhasa_method)
        return [(seed + direction * h) % 12 for h in range(12)]
    elif antardhasa_option == opt.QUADRANTS_FROM_DHASA_SIGN_ODD_FORWARD_EVEN_REVERSE:
        return _quadrant_progression_from_sign(planet_positions, dhasa_lord, dhasa_method)
    elif antardhasa_option == opt.QUADRANTS_FROM_STRONGER_DHASA_7TH_SIGN_ODD_FORWARD_EVEN_REVERSE:
        seed = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_lord, dhasa_lord_7th)
        return _quadrant_progression_from_sign(planet_positions, seed, dhasa_method)
    elif antardhasa_option == opt.SAME_AS_NARAYANA_ANTARDASA:
        return narayana._narayana_antardhasa(planet_positions, dhasa_lord)
    else:
        raise ValueError(f"Unknown antardhasa_option: {antardhasa_option}")
def _md_duration_years(planet_positions, sign):
    """Return the Mahadasa duration (years) of sign."""
    return float(narayana._dhasa_duration(planet_positions, sign))
def _first_md_fraction(sl_longitude_in_sign):
    """Return the fraction of the first Mahadasa remaining at birth."""
    deg_in_sign = sl_longitude_in_sign % 30.0
    return (30.0 - deg_in_sign) / 30.0
def _md_order_for_method(planet_positions, sl_sign, dhasa_method):
    """Return the 12 Mahadasa lords, dispatched by dhasa_method."""
    if dhasa_method == const.SUDASA_METHOD.PVR_JHORA:
        return _jhora_md_seed_and_order(planet_positions, sl_sign)
    return _sudasa_md_order(planet_positions, sl_sign, dhasa_method)
def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,
    dhasa_method=None,
    antardhasa_option=None,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return dhasa/antardhasa periods. dhasa_method: const.SUDASA_METHOD.*"""
    if dhasa_method is None:
        dhasa_method = const.sudasa_dhasa_method_default
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
    sl_full = charts.get_chart_element_longitude(jd_at_dob,place,
                                            divisional_chart_factor=divisional_chart_factor,
                                            dhasa_starting_planet="SL")
    sl_sign, sl_long = drik.dasavarga_from_long(sl_full)
    md_lords = _md_order_for_method(planet_positions, sl_sign, dhasa_method)
    first_md_fraction = _first_md_fraction(sl_long)
    rows = []
    start_jd = jd_at_dob
    def _append_row(labels, start_jd_val, seg_years):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))
    def _recurse(level, parent_lord, pstart_jd, parent_years, parent_end_jd, prefix):
        child_seq = _antardhasa(planet_positions, parent_lord, antardhasa_option, dhasa_method)
        child_years = parent_years / 12.0
        child_bounds = _split_into_children(place, pstart_jd, parent_end_jd, parent_years, child_seq)
        if level + 1 == lvl:
            for c, (child_start_jd, _child_end_jd) in zip(child_seq, child_bounds):
                _append_row(prefix + (c,), child_start_jd, child_years)
            return parent_end_jd
        for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
            _recurse(level + 1, c, child_start_jd, child_years, child_end_jd, prefix + (c,))
        return parent_end_jd
    for idx, md_lord in enumerate(md_lords):
        md_years_full = _md_duration_years(planet_positions, md_lord)
        if idx == 0:
            fraction_elapsed = 1.0 - first_md_fraction
            start_jd = _bounded_start_jd(jd_at_dob, place, fraction_elapsed, md_years_full)
        md_years = md_years_full
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
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    dhasa_method=None,
    antardhasa_option=None,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return immediate child periods for a parent dasha."""
    if dhasa_method is None:
        dhasa_method = const.sudasa_dhasa_method_default
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
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor, **kwargs
    )[:const._pp_count_upto_ketu]
    child_seq = _antardhasa(planet_positions, parent_sign, antardhasa_option, dhasa_method)
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
    dhasa_method=None,
    antardhasa_option=None,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return the running dhasa sequence for a given date."""
    if dhasa_method is None:
        dhasa_method = const.sudasa_dhasa_method_default
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
    sl_sign, sl_long = drik.sree_lagna(jd_at_dob, place)
    md_lords = _md_order_for_method(planet_positions, sl_sign, dhasa_method)
    first_md_fraction = _first_md_fraction(sl_long)
    md_entries = []
    cursor_jd = jd_at_dob
    for idx, md_lord in enumerate(md_lords):
        md_years_full = _md_duration_years(planet_positions, md_lord)
        if idx == 0:
            fraction_elapsed = 1.0 - first_md_fraction
            cursor_jd = _bounded_start_jd(jd_at_dob, place, fraction_elapsed, md_years_full)
        md_years = md_years_full
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
    ladder = [([md_sign], utils.jd_to_gregorian(md_start), utils.jd_to_gregorian(md_end))]
    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder
    parent_lords = [md_sign]
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_years
    parent_sign = md_sign
    for level in range(2, target + 1):
        child_seq = _antardhasa(planet_positions, parent_sign, antardhasa_option, dhasa_method)
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
        ladder.append((parent_lords, utils.jd_to_gregorian(child_start_jd),
                       utils.jd_to_gregorian(child_end_jd)))
        parent_sign = child_sign
        parent_start_jd, parent_end_jd, parent_years = child_start_jd, child_end_jd, child_years
    return ladder
if __name__ == "__main__":
    utils.set_language('en')
    CHART = "2004-06-25"   # "1996-12-07" / "2004-06-25" / "1995-01-11"
    if CHART == "1996-12-07":
        dob = drik.Date(1996, 12, 7)
        tob = (10, 34, 0)
    elif CHART == "2004-06-25":
        dob = drik.Date(2004, 6, 25)
        tob = (14, 47, 0)
    else:
        dob = drik.Date(1995, 1, 11)
        tob = (15, 50, 37)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    dcf = 1
    for method_name, method in (("PVR_JHORA", const.SUDASA_METHOD.PVR_JHORA),):
        for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
            yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
            print("=" * 70)
            print(CHART, method_name, dd.name, dd.value, yd)
            sl_sign, sl_long = drik.sree_lagna(jd_at_dob, place)
            print(f"Sree Lagna: sign={utils.RAASI_SHORT_LIST[sl_sign]}  longitude_in_sign(mod 30)={sl_long % 30:.4f}")
            print(f"First-MD fraction: {_first_md_fraction(sl_long):.4f}")
            print(f"\n--- MD-only table ({CHART}, {method_name}) ---")
            md_only_rows = get_dhasa_antardhasa(
                dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd,
                divisional_chart_factor=dcf, dhasa_method=method,
            )
            for lords, start_tuple, dur_years in md_only_rows:
                lord_name = utils.RAASI_SHORT_LIST[lords[0]]
                y_, m_, d_, fh_ = start_tuple
                print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs")
            print(f"\n--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss} ({method_name}) ---")
            start_time = time.time()
            grd = get_running_dhasa_for_given_date(
                current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                divisional_chart_factor=dcf, dhasa_method=method,
            )
            for lords, start, end in grd:
                label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
                start_str = f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])}"
                end_str = f"{end[0]}-{end[1]}-{end[2]} {utils.to_dms(end[3])}"
                print(f"{label:15s} {start_str}  ->  {end_str}")
            print('elapsed time', time.time() - start_time)
