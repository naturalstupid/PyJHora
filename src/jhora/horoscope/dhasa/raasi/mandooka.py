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
Mandooka Dasa.

Reference: K.N. Rao's "Mandook Dasha" write-up, quoting Sanjay Rath's
Jaimini Upadesa Sutra commentary (Adhyaya 2, Ch.4, verse 15).

Two selectable methods (const.MANDOOKA_TYPE):
  KN_RAO       - D-1. Seed = Ascendant (odd) or 7th-from-Ascendant (even).
                 "Frog jump" Mahadasa order, reused recursively at every
                 antardasa level. Confirmed matching JHora at all levels.
  SANJAY_RATH  - D-11. Seed = 11th from chart Ascendant. Two-block Mahadasa
                 order. Confirmed matching JHora at all levels.

Both methods share one children-split engine for every level below Mahadasa.
"""
from jhora import const, utils
from jhora.horoscope.chart import charts, house, arudhas
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

year_duration = const.sidereal_year

def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd, place=place,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
    )
    return year_duration

_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
def _bounded_end_jd(start_jd, place, years, backstop_days=_BACKSTOP_DAYS):
    """Real (transit-based) dasha-period end JD, with naive-average-year fallback."""
    naive_end = start_jd + years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, years)
    except Exception:
        return naive_end
    if real_end is None or abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end

# =============================================================================
#   Shared constants
# =============================================================================
_ODD_SIGNS = set(getattr(const, "odd_signs", (0, 2, 4, 6, 8, 10)))
_MOVABLE_SIGNS = set(getattr(const, "movable_signs", (0, 3, 6, 9)))
_FIXED_SIGNS = set(getattr(const, "fixed_signs", (1, 4, 7, 10)))
_DUAL_SIGNS = set(getattr(const, "dual_signs", (2, 5, 8, 11)))

# =============================================================================
#   K.N. Rao method
# =============================================================================
def _knr_seed_and_direction(planet_positions):
    """Seed = Ascendant (direct) if odd, else 7th-from-Ascendant (reverse)."""
    asc = planet_positions[0][1][0]
    if asc in _ODD_SIGNS:
        return asc, 1
    seventh = (asc + const.HOUSE_7) % 12
    return seventh, -1

def _frog_jump_md_order(seed, direction):
    """K.N. Rao's "frog jump" Mahadasa order."""
    order = []
    anchor = seed
    for _group in range(3):
        for step in range(4):
            order.append((anchor + direction * 3 * step) % 12)
        anchor = (anchor + direction) % 12
    return order

def _dhasa_duration_kn_rao(planet_positions, sign):
    """K.N. Rao Mahadasa duration, from dasa-rasi lord's position relative to dasa-rasi."""
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = const._house_owners_list[sign]
    house_of_lord = p_to_h[lord_of_sign]
    if sign in const.even_signs:
        dhasa_period = (sign - house_of_lord + 1) % 12
    else:
        dhasa_period = (house_of_lord - sign + 1) % 12
    if house_of_lord == sign:
        dhasa_period = 12
    if house_of_lord == (sign + const.HOUSE_7) % 12:
        dhasa_period = 10
    return dhasa_period

def _knr_antardasa_order(parent_rasi, direction):
    """Antardasa order at every level: fresh frog-jump recompute using the
    current parent sign as seed, with the fixed direction from the original
    Ascendant's parity reused unchanged at every deeper level."""
    return _frog_jump_md_order(parent_rasi, direction)

# =============================================================================
#   Sanjay Rath method
# =============================================================================
def _sr_seed_and_direction(varga_positions, divisional_chart_factor=11):
    """Seed = 11th sign from the chart's own Ascendant. Direction from seed
    parity, adjusted when Saturn and/or Ketu occupy the seed sign."""
    asc = varga_positions[0][1][0]
    seed = (asc + divisional_chart_factor - 1) % 12
    saturn_in_seed = varga_positions[const.SATURN_ID + 1][1][0] == seed
    ketu_in_seed = varga_positions[const.KETU_ID + 1][1][0] == seed
    direction = 1 if seed in const.odd_signs else -1
    if saturn_in_seed and ketu_in_seed:
        sp = house.stronger_planet_from_planet_positions(varga_positions, const.SATURN_ID, const.KETU_ID)
        if sp == const.SATURN_ID:
            direction = 1
        else:
            direction *= 1
    elif saturn_in_seed:
        direction = 1
    elif ketu_in_seed:
        direction *= -1
    return seed, direction

def _sr_md_order(seed, direction):
    """Sanjay Rath Mahadasa order: two contiguous 6-sign blocks, step of
    direction*2, second block anchored one sign before the seed."""
    step = direction * 2
    first6 = [(seed + step * k) % 12 for k in range(6)]
    second6 = [((seed - 1) + step * k) % 12 for k in range(6)]
    return first6 + second6

def _sr_md_years(rasi):
    """Sanjay Rath Mahadasa duration by dasa-rasi modality: movable=7, fixed=8, dual=9."""
    if rasi in _MOVABLE_SIGNS:
        return 7.0
    if rasi in _FIXED_SIGNS:
        return 8.0
    return 9.0

def _sr_antardasa_order(parent_rasi):
    """Alternate antardasa order rule (anchor + direction by parent's
    modality/parity). Currently unused by get_dhasa_antardhasa()."""
    R = int(parent_rasi)
    if R in _MOVABLE_SIGNS:
        anchor = const.SAGITTARIUS if (R in const.even_signs) else const.CANCER
        dir_fwd = (R in const.even_signs)
    elif R in _FIXED_SIGNS:
        anchor = const.CANCER
        dir_fwd = False
    else:
        anchor = const.TAURUS if (R in _ODD_SIGNS) else const.SAGITTARIUS
        dir_fwd = False
    step = 1 if dir_fwd else -1
    seq, s = [], anchor
    for _ in range(12):
        seq.append(s)
        s = (s + step) % 12
    return seq

# =============================================================================
#   Single shared "children" engine (AD level and deeper, both methods)
# =============================================================================
def _split_parent_into_children_jd(parent_rasi, parent_start_jd, parent_end_jd, parent_years,
                                    order_fn, place):
    """Shared 12-way equal-time split, used by all entry points for both
    methods, for every level from Antardasa downward."""
    order = order_fn(parent_rasi)
    parent_real_days = parent_end_jd - parent_start_jd
    base_years = parent_years / 12.0
    out = []
    jd_cursor = parent_start_jd
    for idx in range(12):
        child_rasi = order[idx]
        child_years = (parent_years - base_years * 11.0) if idx == 11 else base_years
        if idx == 11:
            child_end_jd = parent_end_jd
        else:
            naive_days = child_years * year_duration
            if naive_days < _SUB_DAY_THRESHOLD_DAYS:
                child_end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
            else:
                child_end_jd = _bounded_end_jd(jd_cursor, place, child_years)
        out.append((child_rasi, jd_cursor, child_end_jd, child_years))
        jd_cursor = child_end_jd
    return out

def _get_planet_positions_and_seed(jd_at_dob, place, divisional_chart_factor, chart_method,
                                    dhasa_method, years=1, months=1, sixty_hours=1, **kwargs):
    """Shared setup: builds planet positions and derives (seed, direction,
    md_order, md_duration_fn, ad_order_fn) for the requested method."""
    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    if dhasa_method == const.MANDOOKA_TYPE.SANJAY_RATH:
        seed, direction = _sr_seed_and_direction(planet_positions,
                                                 divisional_chart_factor=divisional_chart_factor)
        md_order = _sr_md_order(seed, direction)
        md_duration_fn = _sr_md_years
        ad_order_fn = lambda parent_rasi: _sr_antardasa_order(parent_rasi=parent_rasi)
    else:
        seed, direction = _knr_seed_and_direction(planet_positions)
        md_order = _frog_jump_md_order(seed, direction)
        md_duration_fn = lambda rasi: float(_dhasa_duration_kn_rao(planet_positions, rasi))
        ad_order_fn = lambda parent_rasi: _knr_antardasa_order(parent_rasi, direction)
    return planet_positions, seed, direction, md_order, md_duration_fn, ad_order_fn

# =============================================================================
#   get_dhasa_antardhasa - whole-table build
# =============================================================================
def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_method=None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return Mahadasa/Antardasa table. dhasa_method: const.MANDOOKA_TYPE.KN_RAO
    or .SANJAY_RATH."""
    if dhasa_method is None:
        dhasa_method = const.MANDOOKA_TYPE_DEFAULT
    if not (const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY <= dhasa_level_index <= const.MAHA_DHASA_DEPTH.DEHA):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    _planet_positions, _seed, _direction, md_order, md_duration_fn, ad_order_fn = \
        _get_planet_positions_and_seed(jd_at_dob, place, divisional_chart_factor, chart_method,
                                        dhasa_method, years=years, months=months, sixty_hours=sixty_hours, **kwargs)
    prec = dhasa_level_index + 1
    do_round = round if round_duration else (lambda x, _: x)
    rows = []
    def _append_row(level_key, start_jd, years_len):
        start_str = utils.jd_to_gregorian(start_jd)
        rows.append((tuple(level_key), start_str, float(do_round(years_len, prec))))
    def _recurse(level, parent_rasi, parent_start_jd, parent_end_jd, parent_years, prefix_list):
        children = _split_parent_into_children_jd(
            parent_rasi, parent_start_jd, parent_end_jd, parent_years, ad_order_fn, place
        )
        if level < dhasa_level_index:
            for child_rasi, child_start_jd, child_end_jd, child_years in children:
                prefix_list.append(child_rasi)
                _recurse(level + 1, child_rasi, child_start_jd, child_end_jd, child_years, prefix_list)
                prefix_list.pop()
        else:
            for child_rasi, child_start_jd, child_end_jd, child_years in children:
                _append_row(prefix_list + [child_rasi], child_start_jd, child_years)
    dhasa_start_jd = utils.julian_day_number(dob, tob)
    md_start_jd = dhasa_start_jd
    for md_rasi in md_order:
        md_years = float(md_duration_fn(md_rasi))
        md_end_jd = _bounded_end_jd(md_start_jd, place, md_years)
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _append_row([md_rasi], md_start_jd, md_years)
        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            children = _split_parent_into_children_jd(md_rasi, md_start_jd, md_end_jd, md_years, ad_order_fn, place)
            for ad_rasi, child_start_jd, child_end_jd, child_years in children:
                _append_row([md_rasi, ad_rasi], child_start_jd, child_years)
        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, md_rasi, md_start_jd, md_end_jd, md_years, [md_rasi])
        md_start_jd = md_end_jd
    return rows

# =============================================================================
#   mandooka_immediate_children
# =============================================================================
def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_method=None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return immediate (p -> p+1) child periods for a parent dasha."""
    if dhasa_method is None:
        dhasa_method = const.MANDOOKA_TYPE_DEFAULT
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")
    parent_rasi = int(path[-1])
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
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []
    _pp, _seed, _direction, _md_order, _md_dur_fn, ad_order_fn = \
        _get_planet_positions_and_seed(jd_at_dob, place, divisional_chart_factor, chart_method,
                                        dhasa_method, years=years, months=months, sixty_hours=sixty_hours, **kwargs)
    children = _split_parent_into_children_jd(parent_rasi, start_jd, end_jd, parent_years, ad_order_fn, place)
    return [
        [path + (child_rasi,), _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)]
        for child_rasi, child_start_jd, child_end_jd, _child_years in children
    ]

# =============================================================================
#   get_running_dhasa_for_given_date
# =============================================================================
def get_running_dhasa_for_given_date(
    jd_given, jd_at_dob, place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    dhasa_method=None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return running lords and (start, end) at each level for a single given moment."""
    if dhasa_method is None:
        dhasa_method = const.MANDOOKA_TYPE_DEFAULT
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    _pp, _seed, _direction, md_order, md_duration_fn, ad_order_fn = \
        _get_planet_positions_and_seed(jd_at_dob, place, divisional_chart_factor, chart_method,
                                        dhasa_method, years=years, months=months, sixty_hours=sixty_hours, **kwargs)
    jd_to_gregorian = utils.jd_to_gregorian
    epoch_jd = jd_at_dob
    md_years_list = [float(md_duration_fn(s)) for s in md_order]
    md_starts_jd = [epoch_jd]
    for y in md_years_list:
        md_starts_jd.append(_bounded_end_jd(md_starts_jd[-1], place, y))
    from bisect import bisect_right
    i = bisect_right(md_starts_jd, jd_given) - 1
    i = max(0, min(i, len(md_order) - 1))
    md_rasi = md_order[i]
    md_start, md_end, md_years = md_starts_jd[i], md_starts_jd[i + 1], md_years_list[i]
    out = [((md_rasi,), jd_to_gregorian(md_start), jd_to_gregorian(md_end))]
    parent_rasi, parent_start, parent_end, parent_years = md_rasi, md_start, md_end, md_years
    for _level in range(2, int(dhasa_level_index) + 1):
        children = _split_parent_into_children_jd(parent_rasi, parent_start, parent_end, parent_years, ad_order_fn, place)
        chosen = children[-1]
        for child_rasi, child_start_jd, child_end_jd, child_years in children:
            if jd_given < child_end_jd:
                chosen = (child_rasi, child_start_jd, child_end_jd, child_years)
                break
        child_rasi, child_start_jd, child_end_jd, child_years = chosen
        out.append((out[-1][0] + (child_rasi,), jd_to_gregorian(child_start_jd), jd_to_gregorian(child_end_jd)))
        parent_rasi, parent_start, parent_end, parent_years = child_rasi, child_start_jd, child_end_jd, child_years
    return out

if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    for method_name, method, dcf in (
        ("KN_RAO (D-1)", const.MANDOOKA_TYPE.KN_RAO, 1),
        ("SANJAY_RATH (D-11)", const.MANDOOKA_TYPE.SANJAY_RATH, 11),
    ):
        print("=" * 70)
        print(method_name, "- Maha Dasas")
        print("=" * 70)
        db_maha = get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=dcf,
                        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, dhasa_method=method)
        for lords, start_date, durn in db_maha:
            y, m, d, fh = start_date
            print(utils.RAASI_SHORT_LIST[lords[0]], f"{y}-{m:02d}-{d:02d}", utils.to_dms(fh), durn)

        print("\n", method_name, "- MD>AD sequence (first MD)")
        db_ad = get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=dcf,
                        dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA, dhasa_method=method)
        first_md = db_ad[0][0][0]
        for lords, start_date, durn in db_ad:
            if lords[0] != first_md:
                break
            y, m, d, fh = start_date
            print(" ", utils.RAASI_SHORT_LIST[lords[1]], f"{y}-{m:02d}-{d:02d}", utils.to_dms(fh), durn)

        y, m, d = (2010, 11, 9)
        hh, mm, ss = (15, 29, 45)
        print(f"\n {method_name} - running dasha chain for {y}-{m}-{d} {hh}:{mm}:{ss}")
        current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, divisional_chart_factor=dcf,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR,
            dhasa_method=method,
        )
        for lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2) in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:20s} {y1}-{m1:02d}-{d1:02d} {utils.to_dms(fh1)}  ->  {y2}-{m2:02d}-{d2:02d} {utils.to_dms(fh2)}")
        print()
