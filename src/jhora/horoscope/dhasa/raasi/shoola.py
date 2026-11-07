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
from jhora.horoscope.chart import house, charts
from jhora.panchanga import drik
"""
Shoola Dasa.

Ref: P.V.R. Narasimha Rao, "Vedic Astrology: An Integrated Approach", Ch. 23.

Seed (every level): stronger of the sign and its 7th house. MD: seed from
Lagna, forward zodiacal order, 9 years each, single 108-year cycle (no
2nd cycle - the book gives none here, unlike Narayana/Paryaaya). Every
level below MD: same seed rule applied to the current dasa-rasi, 12
equal children, duration = parent/12.

Confirmed matching JHora on 2 test charts.

Release History
----------------
V5.0 - Refactored.
"""
year_duration = const.sidereal_year
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True
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
def _seed(planet_positions, sign):
    """Return the stronger of sign and its 7th house."""
    seventh = (sign + const.HOUSE_7) % 12
    return house.stronger_rasi_from_planet_positions(planet_positions, sign, seventh)
def _children(planet_positions, parent_sign):
    """Return the 12 children of parent_sign, forward from the seed."""
    start_sign = _seed(planet_positions, parent_sign)
    return [(start_sign + i) % 12 for i in range(12)]
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq):
    """Return the (start,end) JD pairs for each of the 12 children."""
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
def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=2,
    round_duration=False,
    *,
    house_index: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return dhasa/bhukthi periods, depth-enabled.
    house_index: 1-based house from Lagna used as the MD-seed anchor
    (1 = Lagna itself, per the book; other values are a generalization)."""
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")
    if not (1 <= int(house_index) <= 12):
        raise ValueError("house_index must be in 1..12")
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type, savana_year_method)
    pp = charts.divisional_chart(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    asc_house = p_to_h[const._ascendant_symbol]
    base_sign = (asc_house + (int(house_index) - 1)) % 12
    md_seed_sign = _seed(pp, base_sign)
    md_progression = [(md_seed_sign + k) % 12 for k in range(12)]
    md_years = 9.0
    rows = []
    start_jd = jd
    def _append_row(labels, start_jd_val, seg_years):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))
    def _recurse(level, parent_sign, pstart_jd, parent_years, parent_end_jd, prefix):
        child_seq = _children(pp, parent_sign)
        child_years = parent_years / 12.0
        child_bounds = _split_into_children(place, pstart_jd, parent_end_jd, parent_years, child_seq)
        if level + 1 == lvl:
            for c, (child_start_jd, _child_end_jd) in zip(child_seq, child_bounds):
                _append_row(prefix + (c,), child_start_jd, child_years)
            return parent_end_jd
        for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
            _recurse(level + 1, c, child_start_jd, child_years, child_end_jd, prefix + (c,))
        return parent_end_jd
    for md in md_progression:
        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        if lvl == 1:
            _append_row((md,), start_jd, md_years)
        else:
            _recurse(1, md, start_jd, md_years, md_end_jd, (md,))
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
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
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
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    child_seq = _children(pp, parent_sign)
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
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    house_index: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return the running dhasa sequence for a given date."""
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
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    asc_house = p_to_h[const._ascendant_symbol]
    base_sign = (asc_house + (int(house_index) - 1)) % 12
    md_seed_sign = _seed(pp, base_sign)
    md_progression = [(md_seed_sign + k) % 12 for k in range(12)]
    md_years = 9.0
    md_entries = []
    cursor_jd = jd_at_dob
    for md in md_progression:
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        md_entries.append((md, cursor_jd, md_end_jd, md_years))
        cursor_jd = md_end_jd
    located_entry = None
    for md, seg_start, seg_end, seg_years in md_entries:
        if seg_start <= current_jd < seg_end:
            located_entry = (md, seg_start, seg_end, seg_years)
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
    for level in range(2, target + 1):
        child_seq = _children(pp, parent_sign)
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
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
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
    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)
        print("\n--- MD-only table (single pass, 12 signs x 9 years) ---", dob)
        md_only_rows = get_dhasa_antardhasa(
            dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd,
            divisional_chart_factor=dcf
        )
        for lords, start_tuple, dur_years in md_only_rows:
            lord_name = utils.RAASI_SHORT_LIST[lords[0]]
            y_, m_, d_, fh_ = start_tuple
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs")
        print(f"\n--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss} ---")
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            divisional_chart_factor=dcf,
        )
        for lords, start_str, end_str in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:15s} {start_str}  ->  {end_str}")
        print('elapsed time', time.time() - start_time)
