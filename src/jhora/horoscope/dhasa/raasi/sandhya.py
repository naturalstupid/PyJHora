#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora
#
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
from jhora import utils, const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik
"""
Sandhya Dasa (Rasi Dasa).

Ref: https://medium.com/thoughts-on-jyotish/in-search-of-maharishi-parasharas-42-dasa-systems-56f7604b5138

Seed: Lagna's own Rasi. MD order: forward sign by sign, 10 years each
(Paramayush 120yr / 12 signs), one 120-year cycle.

Pachaka variation (use_pachaka_variation=True): splits any parent span
into 12 unequal compartments instead of 12 equal ones - compartment 1 =
(parent years x 6)/31, compartments 2-4 = half of compartment 1,
compartments 5-12 = one third of compartment 1 - applied recursively at
every level. The source gives compartment sizes but not which sign gets
which; this module assigns them in forward order starting from the
parent sign, so the parent's own position carries the largest share.

No antardasa rule is given beyond recursive application of the same
forward-order/weighting scheme at each level.

Note: There is another Sandhya Graha Dasa (planet-based, not rasi-based)
- see jhora.horoscope.dhasa.graha.sandhya. To be implemented separately.
    Seed: sign occupied by the lord of Lagna.
    Sequence: weekday order (Sun/Moon/Mars/Merc/Jup/Ven/Sat/Rahu/Ketu).
    Duration: 12 years each.
    Children: same sequence/proportional duration, recursively.
    Ref: https://horoanalysis.wordpress.com/2020/06/02/predictive-usefulness-of-sandhya-dasha/

Release History
----------------
V5.0 - Refactored.
"""
_sandhya_duration = [10 for _ in range(12)]
_pachaka_duration = [60 / 31, 30 / 31, 30 / 31, 30 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31]
year_duration = const.sidereal_year
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True
def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    if dhasa_duration_type is not None:
        const.dhasa_year_duration_default = dhasa_duration_type
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
def _child_weights(use_pachaka_variation):
    """Return normalized weights for the 12 children of any parent span."""
    if use_pachaka_variation:
        total_w = float(sum(_pachaka_duration))
        if total_w <= 0:
            return [1.0 / 12.0] * 12
        return [w / total_w for w in _pachaka_duration]
    else:
        return [1.0 / 12.0] * 12
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq, use_pachaka_variation):
    """Return the (start,end,years) tuples for each of the 12 children."""
    weights = _child_weights(use_pachaka_variation)
    child_years_list = [parent_years * w for w in weights]
    parent_real_days = parent_end_jd - parent_start_jd
    cum_years = 0.0
    n = len(child_seq)
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        cyears = child_years_list[idx]
        cum_years += cyears
        if is_last:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (cyears * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (cum_years / parent_years) if parent_years > 0 else cursor
        else:
            end_jd = _bounded_end_jd(cursor, place, cyears)
        out.append((cursor, end_jd, cyears))
        cursor = end_jd
    return out
def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    use_pachaka_variation=False,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return dhasa/antardhasa periods, depth-enabled (L1..L6)."""
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    pp = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    _dhasa_seed = pp[0][1][0]
    _dhasa_progression = [((_dhasa_seed + h) % 12, _durn) for h, _durn in enumerate(_sandhya_duration)]
    dhasa_info = []
    start_jd = jd_at_dob
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, dhasa_level_index + 1
        )
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))
    def _expand_children(start_jd_val, end_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        if current_level == target_level:
            _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)
            return end_jd_val
        parent_lord = parent_lords_stack[-1]
        child_seq = [(parent_lord + h) % 12 for h in range(12)]
        child_bounds = _split_into_children(
            place, start_jd_val, end_jd_val, parent_duration_years, child_seq, use_pachaka_variation
        )
        for child_lord, (c_start, c_end, c_years) in zip(child_seq, child_bounds):
            _expand_children(
                c_start, c_end, c_years,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return end_jd_val
    for md_lord, md_years in _dhasa_progression:
        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        if dhasa_level_index == 1:
            _append_leaf([md_lord], start_jd, md_years)
        else:
            _expand_children(start_jd, md_end_jd, md_years, [md_lord], current_level=1, target_level=dhasa_level_index)
        start_jd = md_end_jd
    return dhasa_info
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
    use_pachaka_variation: bool = False,
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
    parent_lord = path[-1]
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
    child_seq = [(parent_lord + h) % 12 for h in range(12)]
    child_bounds = _split_into_children(place, start_jd, end_jd, parent_years, child_seq, use_pachaka_variation)
    rows = []
    for child_lord, (c_start, c_end, _c_years) in zip(child_seq, child_bounds):
        if c_end > c_start:
            rows.append((path + (child_lord,), _jd_to_tuple(c_start), _jd_to_tuple(c_end)))
    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd_to_tuple(end_jd))
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
    use_pachaka_variation: bool = False,
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
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    dhasa_seed = pp[0][1][0]
    cursor_jd = jd_at_dob
    located = None
    last_computed = None
    for h in range(12):
        lord = (dhasa_seed + h) % 12
        md_years = _sandhya_duration[lord]
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        last_computed = (lord, cursor_jd, md_end_jd, md_years)
        if cursor_jd <= current_jd < md_end_jd:
            located = last_computed
            break
        cursor_jd = md_end_jd
    if located is None:
        located = last_computed
    md_sign, md_start, md_end, md_years = located
    ladder = [[(md_sign,), utils.jd_to_gregorian(md_start), utils.jd_to_gregorian(md_end)]]
    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder
    parent_lords = (md_sign,)
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_years
    parent_sign = md_sign
    for level in range(2, target + 1):
        child_seq = [(parent_sign + h) % 12 for h in range(12)]
        child_bounds = _split_into_children(
            place, parent_start_jd, parent_end_jd, parent_years, child_seq, use_pachaka_variation
        )
        chosen = None
        for c_lord, (c_start, c_end, c_years) in zip(child_seq, child_bounds):
            if c_start <= current_jd < c_end:
                chosen = (c_lord, c_start, c_end, c_years)
                break
        if chosen is None:
            c_lord, (c_start, c_end, c_years) = child_seq[-1], child_bounds[-1]
            chosen = (c_lord, c_start, c_end, c_years)
        child_sign, child_start_jd, child_end_jd, child_years = chosen
        parent_lords = parent_lords + (child_sign,)
        ladder.append([parent_lords, utils.jd_to_gregorian(child_start_jd), utils.jd_to_gregorian(child_end_jd)])
        parent_sign = child_sign
        parent_start_jd, parent_end_jd, parent_years = child_start_jd, child_end_jd, child_years
    return ladder
if __name__ == "__main__":
    utils.set_language('en')
    CHART = "1996-12-07"   # or "2004-06-25"
    if CHART == "1996-12-07":
        dob = drik.Date(1996, 12, 7)
        tob = (10, 34, 0)
    else:
        dob = drik.Date(2004, 6, 25)
        tob = (14, 47, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    dcf = 1
    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)
        print(f"\n--- MD-only table  ---")
        md_only_rows = get_dhasa_antardhasa(
            dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd, divisional_chart_factor=dcf,
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
        for lords, start, end in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            start_str = f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])}"
            end_str = f"{end[0]}-{end[1]}-{end[2]} {utils.to_dms(end[3])}"
            print(f"{label:15s} {start_str}  ->  {end_str}")
        print('elapsed time', time.time() - start_time)
    exit()
