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
Yogardha Dasha

Mahadasa seed sign is the stronger of Lagna and its 7th house. The
12-sign Mahadasa progression runs forward from the seed, or reverse if
the seed is an even sign. Each Mahadasa's duration is the average of
Chara Dasa's duration (chara._dhasa_duration) and Sthira Dasa's duration
(sthira._dhasa_duration) for that sign.

Antardasa (and every level below Mahadasa) uses the same seed/order rule
as raasi Narayana Dasa's own antardhasa (narayana._narayana_antardhasa),
applied per parent sign recursively, with an equal 12-way duration split
at every level.
V5.0 Refactored to match JHora
"""
from jhora import const, utils
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik

year_duration = const.sidereal_year

_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    """
    Sets the module-level year_duration used by _bounded_end_jd() and
    sub-day interpolation. If dhasa_duration_type is given, it also sets
    const.dhasa_year_duration_default; otherwise the existing global is
    left unchanged.
    """
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


def _md_seed_and_order(planet_positions):
    """ Mahadasa seed (stronger of Lagna and its 7th) and 12-sign
    progression, forward from the seed or reverse if the seed is even. """
    asc_house = planet_positions[0][1][0]
    seventh_house = (asc_house + 6) % 12
    dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    direction = 1 if dhasa_seed not in const.even_signs else -1
    order = [(dhasa_seed + direction * h) % 12 for h in range(12)]
    return dhasa_seed, order


def _md_years(planet_positions, md_sign):
    """ Mahadasa duration: average of Chara Dasa's and Sthira Dasa's
    duration for this sign. """
    from jhora.horoscope.dhasa.raasi.chara import _dhasa_duration as chara_dhasa_duration
    from jhora.horoscope.dhasa.raasi.sthira import _dhasa_duration as sthira_dhasa_duration
    return 0.5 * (
        chara_dhasa_duration(planet_positions, md_sign) +
        sthira_dhasa_duration(md_sign)
    )


def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, n=12):
    """ Splits a parent span into n equal children using real dasa-period
    boundaries; the last child is clamped exactly to parent_end_jd. """
    child_years = parent_years / n
    parent_real_days = parent_end_jd - parent_start_jd
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        if is_last:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (child_years * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / n
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out


def _get_children_jds(path_so_far, parent_sign, parent_start_jd, parent_end_jd, parent_years,
                       place, planet_positions):
    """
    Returns the 12 children of parent_sign (one level below parent_sign,
    which may be a Mahadasa sign or any deeper antardasa sign), using
    narayana._narayana_antardhasa(planet_positions, parent_sign) for the
    child order:
        list of (child_path, child_sign, child_start_jd, child_end_jd, child_years)
    """
    from jhora.horoscope.dhasa.raasi.narayana import _narayana_antardhasa
    order = _narayana_antardhasa(planet_positions, parent_sign)
    child_years = parent_years / 12.0
    bounds = _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, n=12)

    out = []
    for child_sign, (c_start, c_end) in zip(order, bounds):
        out.append((path_so_far + (child_sign,), child_sign, c_start, c_end, child_years))
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
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Full Yogardha Dasha table, from MD down to the requested depth
    (1..6).

    Returns rows: [ (lords_tuple, (Y, M, D, fractional_hour), duration_years), ... ]
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    _dhasa_seed, md_order = _md_seed_and_order(planet_positions)

    dhasa_info = []

    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        disp_dur = seg_duration_years if not round_duration else round(seg_duration_years, dhasa_level_index + 1)
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))

    def _recurse(path_so_far, parent_sign, start_jd_val, end_jd_val, parent_years, current_level, target_level):
        if current_level == target_level:
            _append_leaf(path_so_far, start_jd_val, parent_years)
            return

        children = _get_children_jds(path_so_far, parent_sign, start_jd_val, end_jd_val, parent_years,
                                      place, planet_positions)
        for child_path, child_sign, c_start, c_end, c_years in children:
            _recurse(child_path, child_sign, c_start, c_end, c_years, current_level + 1, target_level)

    start_jd = jd_at_dob
    for md_sign in md_order:
        md_years = _md_years(planet_positions, md_sign)
        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        if dhasa_level_index == 1:
            _append_leaf((md_sign,), start_jd, md_years)
        else:
            _recurse((md_sign,), md_sign, start_jd, md_end_jd, md_years, current_level=1, target_level=dhasa_level_index)
        start_jd = md_end_jd

    return dhasa_info


def get_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method=1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Returns the immediate 12 children under a given parent span, via
    narayana._narayana_antardhasa(planet_positions, parent_sign).

    Output rows: [ (child_lords_tuple, start_tuple, end_tuple), ... ]
    """
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
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    children = _get_children_jds(path, parent_sign, start_jd, end_jd, parent_years, place, planet_positions)

    rows = []
    for child_path, _child_sign, c_start, c_end, _c_years in children:
        if c_end > c_start:
            rows.append((child_path, _jd_to_tuple(c_start), _jd_to_tuple(c_end)))

    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd_to_tuple(end_jd))

    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    divisional_chart_factor: int = 1,
    chart_method=1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Returns the running dasa/antardasa/... chain, from Mahadasha down to
    the requested depth, for current_jd. Descends only the single branch
    containing current_jd at each level.

    Returns: [ [lords_tuple, start_tuple, end_tuple], ... ]
    """
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
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    _dhasa_seed, md_order = _md_seed_and_order(planet_positions)

    cursor_jd = jd_at_dob
    located = None
    last_computed = None
    for md_sign in md_order:
        md_years = _md_years(planet_positions, md_sign)
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        last_computed = (md_sign, cursor_jd, md_end_jd, md_years)
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

    parent_path = (md_sign,)
    parent_sign = md_sign
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_years

    for level in range(2, target + 1):
        children = _get_children_jds(parent_path, parent_sign, parent_start_jd, parent_end_jd, parent_years,
                                      place, planet_positions)
        chosen = None
        for child_path, child_sign, c_start, c_end, c_years in children:
            if c_start <= current_jd < c_end:
                chosen = (child_path, child_sign, c_start, c_end, c_years)
                break
        if chosen is None:
            chosen = children[-1]

        parent_path, parent_sign, parent_start_jd, parent_end_jd, parent_years = chosen
        ladder.append([list(parent_path), utils.jd_to_gregorian(parent_start_jd), utils.jd_to_gregorian(parent_end_jd)])

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
        print(f"\n--- MD-only table, {CHART} ---")
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
