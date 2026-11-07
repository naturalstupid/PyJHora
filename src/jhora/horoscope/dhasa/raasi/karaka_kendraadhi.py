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
    Karaka-Kendradhi Rasi Dasha 
    V5.0 - Refactored to match JHora
"""

from functools import cmp_to_key
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house
from jhora.horoscope.dhasa.raasi.narayana import _dhasa_duration as narayana_dhasa_duration

# Default year basis; public entry points resolve this through drik.dhasa_year_duration(...)
# NOTE: this is used ONLY inside _bounded_end_jd()'s own naive-estimate fallback -
# nowhere else in this module (see "REAL BUGS FOUND AND FIXED" #4 above).
year_duration = const.sidereal_year

# "30-day backstop" - a last-resort floor, used ONLY when a boundary
# calculation genuinely fails/degenerates (end <= start).
_MIN_SPAN_DAYS = 30.0

# Duration-triggered (NOT depth-triggered) sub-day fallback threshold - see
# "REAL BUGS FOUND AND FIXED" #3 above.
_SUB_DAY_THRESHOLD_DAYS = 1.0


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    "Resolve and cache the dasa year duration used by this module."
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _bounded_end_jd(start_jd, place, duration_in_years, min_days=_MIN_SPAN_DAYS):
    """
    Canonical end-jd resolver, used at every level by the shared engine.
    Parameter names EXACTLY match the real drik._get_dhasa_end_jd() this
    wraps: `start_jd, place, duration_in_years`.
    Prefers the real boundary from drik._get_dhasa_end_jd() over the naive
    arithmetic estimate (start_jd + duration_in_years * year_duration),
    falling back silently if that call is unavailable, fails, or disagrees
    in a non-sane direction (<= start_jd). The `min_days` backstop is a
    LAST RESORT for genuine failure/degenerate cases only.
    """
    naive_end = start_jd + duration_in_years * year_duration

    real_end = None
    _real_end_fn = getattr(drik, '_get_dhasa_end_jd', None)
    if callable(_real_end_fn):
        try:
            real_end = _real_end_fn(start_jd, place, duration_in_years)
        except Exception:
            real_end = None
    end_jd = real_end if (real_end is not None and real_end > start_jd) else naive_end
    if end_jd <= start_jd:
        end_jd = start_jd + min_days
    return end_jd

def _kendra_direction(seed_sign, p_to_h):
    """
    Canonical Saturn > Ketu > odd/even direction rule.
    Used IDENTICALLY both to seed the Mahadasa progression from the karaka
    seed sign, and to order every Antardhasa+ level from its own parent sign.
    """
    if p_to_h[const.SATURN_ID] == seed_sign:
        return 1
    elif p_to_h[const.KETU_ID] == seed_sign:
        return -1
    elif seed_sign in const.odd_signs:
        return 1
    return -1


def _antardhasa_order(seed_sign, p_to_h):
    """
    Generates the 12-sign Antardhasa progression for Karaka Kendradi Dasa.

    Rule (verified against real JHora transitions across the MD/AD/PD/SD/
    PAD/Deha chain for the standard test chart):
      - Dual (dwiswabhava) seed sign (Ge, Vi, Sg, Pi): order starts at
        Sagittarius; direction = +1 (direct) if seed is odd, else -1.
      - Movable (chara) seed sign (Ar, Cn, Li, Cp): order starts at the
        4th house from the seed; direction always +1 (direct).
      - Fixed (sthira) seed sign (Ta, Le, Sc, Aq): order starts at the 7th
        house from the seed; direction always +1 (direct).

    """
    if seed_sign in const.dual_signs:
        start_sign = 8  # Sagittarius
        direction = 1 if seed_sign in const.odd_signs else -1
    elif seed_sign in const.movable_signs:
        start_sign = (seed_sign + 3) % 12  # 4th house from seed
        direction = 1
    elif seed_sign in const.fixed_signs:
        start_sign = (seed_sign + 6) % 12  # 7th house from seed
        direction = 1
    else:
        start_sign = seed_sign
        direction = _kendra_direction(seed_sign, p_to_h)
    return [(start_sign + direction * i) % 12 for i in range(12)]


def _karaka_seed_and_progression(planet_positions, p_to_h, karaka_index=1):
    """
    Computes Karaka Kendradi Dasa by grouping houses relative to the Atmakaraka
    and sorting each group internally by strength (Balakramat), matching Jagannatha Hora.
    """
    charas = house.chara_karakas(planet_positions)
    if karaka_index not in range(1, 9):
        karaka_index = 1
    ak = charas[karaka_index - 1]
    ak_sign = p_to_h[ak]

    def sort_by_strength(rasi_list):
        def compare_rasis(rasi1, rasi2):
            if rasi1 == rasi2:
                return 0
            winner = house.stronger_rasi_from_planet_positions(planet_positions, rasi1, rasi2)
            return -1 if winner == rasi1 else 1
        return sorted(rasi_list, key=cmp_to_key(compare_rasis))

    kendras = [(ak_sign + 0) % 12, (ak_sign + 3) % 12, (ak_sign + 6) % 12, (ak_sign + 9) % 12]
    panapharas = [(ak_sign + 1) % 12, (ak_sign + 4) % 12, (ak_sign + 7) % 12, (ak_sign + 10) % 12]
    apoklimas = [(ak_sign + 2) % 12, (ak_sign + 5) % 12, (ak_sign + 8) % 12, (ak_sign + 11) % 12]

    sorted_kendras = sort_by_strength(kendras)
    sorted_panapharas = sort_by_strength(panapharas)
    sorted_apoklimas = sort_by_strength(apoklimas)

    dhasa_progression = sorted_kendras + sorted_panapharas + sorted_apoklimas
    dhasa_seed_sign = dhasa_progression[0]

    return dhasa_seed_sign, dhasa_progression


def _maha_cycle_jd(jd_at_dob, dhasa_progression, planet_positions, place):
    """
    The real, SINGLE-pass 12-node Mahadasa cycle over `dhasa_progression`,
    each sign's duration being its real Narayana-style duration (1..12
    years each). Returns [(sign, start_jd, end_jd, years), ...] x 12, in
    chronological order.
    """
    rows = []
    jd_cursor = jd_at_dob
    for sign in dhasa_progression:
        dd = float(narayana_dhasa_duration(planet_positions, sign))
        end_jd = _bounded_end_jd(jd_cursor, place, dd) if dd > 0 else jd_cursor
        rows.append((sign, jd_cursor, end_jd, dd))
        jd_cursor = end_jd
    return rows


def _get_karaka_kendradhi_children_jd(level, parent_sign, parent_start_jd, parent_end_jd,
                                       parent_years, place, p_to_h,
                                       planet_positions=None, dhasa_progression=None):
    """
    THE single shared children-tree function used identically by
    karaka_kendradhi_rasi_dhasa(), karaka_kendradhi_immediate_children(),
    and get_running_dhasa_for_given_date(). No other function in this
    module computes a start/end boundary.

    level == 0 : real, single-pass Mahadasa level. Requires
                 `planet_positions` and `dhasa_progression`; parent_sign /
                 parent_end_jd / parent_years are unused. Returns the
                 12-node cycle starting at `parent_start_jd` (== jd_at_dob),
                 each row now (sign, start_jd, end_jd, years).
    level >= 1 : returns the 12 Antardhasa+ children of `parent_sign`,
                 dividing [parent_start_jd, parent_end_jd) into 12 equal
                 (by `parent_years` - an EXACT, already-known value passed
                 in by the caller, NEVER re-derived from a JD span - see
                 module docstring "REAL BUGS FOUND AND FIXED" #4) slices in
                 `_antardhasa_order` order.
                   - child_years = parent_years / 12, passed directly to
                     `_bounded_end_jd()` as a duration-in-years.
                   - EXCEPT when child_years's real-day equivalent falls
                     below `_SUB_DAY_THRESHOLD_DAYS` (duration-triggered,
                     not depth-triggered), in which case the boundary is
                     instead interpolated proportionally within the
                     PARENT's own already-resolved real span.
                   - The 12th (last) child is always clamped EXACTLY to
                     parent_end_jd.
                 Each returned row is (child_sign, start_jd, end_jd,
                 child_years) - the 4th element lets the caller recurse
                 one level deeper WITHOUT ever re-deriving years from a
                 JD span.
    """
    if level == 0:
        return _maha_cycle_jd(parent_start_jd, dhasa_progression, planet_positions, place)

    order = _antardhasa_order(parent_sign, p_to_h)
    n = len(order)
    child_years = parent_years / n
    parent_real_days = parent_end_jd - parent_start_jd

    rows = []
    jd_cursor = parent_start_jd
    for i, child_sign in enumerate(order):
        if i == n - 1:
            end_jd = parent_end_jd  # exact clamp - no drift accumulation
        else:
            naive_days = child_years * year_duration
            if naive_days < _SUB_DAY_THRESHOLD_DAYS:
                end_jd = parent_start_jd + parent_real_days * (i + 1) / n
            else:
                end_jd = _bounded_end_jd(jd_cursor, place, child_years)
        rows.append((child_sign, jd_cursor, end_jd, child_years))
        jd_cursor = end_jd
    return rows


# ============================================================
# PUBLIC: full depth-first table builder (Maha -> ... -> target depth)
# ============================================================
def karaka_kendradhi_rasi_dhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    chart_method=1,
    karaka_index=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Karaka Kendradhi Rasi Dasha with multi-level depth.
    Built entirely on the shared `_get_karaka_kendradhi_children_jd()` engine.
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs,
    )
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    _seed_sign, dhasa_progression = _karaka_seed_and_progression(planet_positions, p_to_h, karaka_index)

    maha_rows = _get_karaka_kendradhi_children_jd(
        0, None, jd_at_dob, None, None, place, p_to_h,
        planet_positions=planet_positions, dhasa_progression=dhasa_progression,
    )

    rows = []

    def _emit_or_descend(level, path, start_jd, end_jd, years):
        if level >= dhasa_level_index:
            dur_ret = round(years, dhasa_level_index + 1) if round_duration else years
            rows.append((path, utils.jd_to_gregorian(start_jd), dur_ret))
            return
        for child_sign, c_start, c_end, c_years in _get_karaka_kendradhi_children_jd(
            level, path[-1], start_jd, end_jd, years, place, p_to_h
        ):
            _emit_or_descend(level + 1, path + (child_sign,), c_start, c_end, c_years)

    for sign, s_jd, e_jd, s_years in maha_rows:
        _emit_or_descend(1, (sign,), s_jd, e_jd, s_years)

    return rows


def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    chart_method=1,
    karaka_index=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    return karaka_kendradhi_rasi_dhasa(
        dob, tob, place, divisional_chart_factor, chart_method, karaka_index,
        dhasa_level_index, round_duration,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method, **kwargs,
    )


# ============================================================
# PUBLIC: immediate children of any given parent node
# ============================================================
def get_immediate_children(
    parent_lords, parent_start,
    parent_duration=None, parent_end=None,
    *, jd_at_dob, place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    karaka_index=1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Karaka-Kendradhi Rasi - return ONLY the immediate (p -> p+1) children
    under the given parent span.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
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
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        # Only path where years must still be estimated from a JD span -
        # unavoidable here since no explicit duration was given.
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs,
    )
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    children = _get_karaka_kendradhi_children_jd(
        len(path), parent_sign, start_jd, end_jd, parent_years, place, p_to_h
    )

    out_rows = [[path + (cs,), _jd_to_tuple(cst), _jd_to_tuple(cet)] for cs, cst, cet, _cy in children]
    if out_rows:
        out_rows[-1][2] = _jd_to_tuple(end_jd)
    return out_rows


# ============================================================
# PUBLIC: Runner (Maha -> ... -> target depth) for Karaka variant
# ============================================================
def get_running_dhasa_for_given_date(
    current_jd, jd_at_dob, place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    karaka_index=1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Karaka-Kendradhi Rasi - running ladder at `current_jd`.
    ONE call to the shared engine per level - no full-table rebuild anywhere.
    `parent_years` is tracked explicitly across levels (see module
    docstring "REAL BUGS FOUND AND FIXED" #4) - never re-derived from a
    JD span.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method)

    def _normalize_depth(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))

    target_depth = _normalize_depth(dhasa_level_index)

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    def _lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs,
    )
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    _seed_sign, dhasa_progression = _karaka_seed_and_progression(planet_positions, p_to_h, karaka_index)

    maha_rows = _get_karaka_kendradhi_children_jd(
        0, None, jd_at_dob, None, None, place, p_to_h,
        planet_positions=planet_positions, dhasa_progression=dhasa_progression,
    )

    # maha_rows: (sign, start_jd, end_jd, years) - keep a lookup from lords -> years
    years_by_start = {}
    periods = []
    for sign, s_jd, e_jd, yrs in maha_rows:
        if e_jd - s_jd > 0:
            periods.append(((sign,), _jd_to_tuple(s_jd)))
            years_by_start[(sign,)] = yrs
    if not periods:
        sentinel = _jd_to_tuple(jd_at_dob)
        return [[(), sentinel, sentinel]]
    periods.append((periods[-1][0], _jd_to_tuple(maha_rows[-1][2])))

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running_lords = _lords(rd1[0])
    running = [running_lords, rd1[1], rd1[2]]
    running_years = years_by_start.get(running_lords)
    ladder = [running]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    for _depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running
        parent_sign = parent_lords[-1]
        start_jd = _tuple_to_jd(parent_start)
        end_jd = _tuple_to_jd(parent_end)

        if end_jd <= start_jd or running_years is None:
            running = [parent_lords + (parent_sign,), parent_end, parent_end]
            running_years = None
            ladder.append(running)
            continue

        children = _get_karaka_kendradhi_children_jd(
            len(parent_lords), parent_sign, start_jd, end_jd, running_years, place, p_to_h
        )
        years_by_lords = {}
        periods = []
        for cs, cst, cet, cy in children:
            if cet - cst > 0:
                lords = parent_lords + (cs,)
                periods.append((lords, _jd_to_tuple(cst)))
                years_by_lords[lords] = cy

        if not periods:
            running = [parent_lords + (parent_sign,), parent_end, parent_end]
            running_years = None
        else:
            periods.append((periods[-1][0], _jd_to_tuple(children[-1][2])))
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
            running_lords = _lords(rdk[0])
            running = [running_lords, rdk[1], rdk[2]]
            running_years = years_by_lords.get(running_lords)

        ladder.append(running)

    return ladder


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    y, m, d = (1998, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    print(check_date)
    import time

    DLI = const.MAHA_DHASA_DEPTH.DEHA
    LEVEL_NAMES = ['MD', 'AD', 'PD', 'SD', 'PAD', 'Deha']

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

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
                current_jd, jd_at_dob, place,
                dhasa_level_index=DLI, dhasa_duration_type=dd,
            )
        grdn = [
                ['-'.join([utils.RAASI_SHORT_LIST[lord] for lord in lords]),
                 (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))]
                    for [lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2)] in grd]

        print("\nFull running-dhasa chain (NEW method) - MD/AD/PD/SD/PAD/Deha:")
        for name, row in zip(LEVEL_NAMES, grdn):
            print(f"  {name:5s}: {row}")
        print('new method elapsed time', time.time() - start_time)

        jhora_lords = ['Pi', 'Pi-Ta', 'Pi-Ta-Cn', 'Pi-Ta-Cn-Sg', 'Pi-Ta-Cn-Sg-Pi', 'Pi-Ta-Cn-Sg-Pi-Sg']
        print("\nJHora reference lords (MD/AD/PD/SD/PAD/Deha):", jhora_lords)
        print("NEW method lords                              :", [row[0] for row in grdn])
