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
Karaka–Kendrādhi Rāśi Daśā — public runner + immediate-children,
designed to work alongside your existing base generator.

Exports:
  • karaka_kendradhi_immediate_children(...)
  • get_running_dhasa_for_given_date(...)

Usage with importlib:
  - module: jhora.horoscope.dhasa.raasi.karaka_kendradhi_rasi
  - function: get_running_dhasa_for_given_date
"""

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house
from jhora.horoscope.dhasa.raasi.narayana import _dhasa_duration as narayana_dhasa_duration

# Default year basis; public entry points resolve this through drik.dhasa_year_duration(...)
year_duration = const.sidereal_year


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    """Resolve and cache the daśā year duration used by this module."""
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _antardhasa(antardhasa_seed_rasi, p_to_h):
    direction = -1
    if p_to_h[const.SATURN_ID] == antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs:
        direction = 1
    if p_to_h[const.KETU_ID] == antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi + direction * i) % 12 for i in range(12)]


def karaka_kendradhi_rasi_dhasa(
    dob,
    tob,
    place,
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
    Kāraka Kendraadhi Rāśi Daśā with multi-level depth.

    Same rules as Kendraadhi Rāśi Daśā, except:
      • Seed is stronger of (AK house) & (7th from AK house).
      • Direction uses the same Saturn/Ketu/odd-even logic.
      • Progression uses kendrasas above.

    Depth shapes and recursion are identical to kendradhi_rasi_dhasa.
    """
    if karaka_index not in range(1, 9):
        print('Karaka Index should be in the range (1..8). Index 1 assumed')
        karaka_index = 1

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(
        jd_at_dob,
        place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs,
    )

    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    ak = house.chara_karakas(planet_positions)[karaka_index - 1]
    ak_house = p_to_h[ak]
    seventh_house = (ak_house + const.HOUSE_7) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, ak_house, seventh_house)

    if p_to_h[const.SATURN_ID] == dhasa_seed_sign:
        direction = 1
    elif p_to_h[const.KETU_ID] == dhasa_seed_sign:
        direction = -1
    elif dhasa_seed_sign in const.odd_signs:
        direction = 1
    else:
        direction = -1

    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [(dhasa_seed_sign + direction * (k - 1)) % 12 for k in ks]

    def _children(parent_sign):
        return _antardhasa(parent_sign, p_to_h)

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        child_years = parent_years / 12.0
        jd_cursor = parent_start_jd
        for child_sign in _children(parent_sign):
            if level < dhasa_level_index:
                _recurse(level + 1, child_sign, jd_cursor, child_years, prefix + (child_sign,), out_rows)
            else:
                start_str = utils.jd_to_gregorian(jd_cursor)
                dur_ret = round(child_years, dhasa_level_index + 1) if round_duration else child_years
                out_rows.append((prefix + (child_sign,), start_str, dur_ret))
            jd_cursor += child_years * year_duration

    rows = []
    start_jd = jd_at_dob

    # ----- Cycle #1 ------------------------------------------------------------
    for dhasa_lord in dhasa_progression:
        dd = float(narayana_dhasa_duration(planet_positions, dhasa_lord))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(dd, dhasa_level_index + 1) if round_duration else dd,
            ))
            start_jd += dd * year_duration
        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                rows.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_b),
                    round(ddb, dhasa_level_index + 1) if round_duration else ddb,
                ))
                jd_b += ddb * year_duration
            start_jd += dd * year_duration
        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd, (dhasa_lord,), rows)
            start_jd += dd * year_duration

    # ----- Cycle #2 (12 − first) ----------------------------------------------
    for dhasa_lord in dhasa_progression:
        first_dd = float(narayana_dhasa_duration(planet_positions, dhasa_lord))
        dd2 = 12.0 - first_dd
        if dd2 <= 0:
            dd2 = 0.0

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(dd2, dhasa_level_index + 1) if round_duration else dd2,
            ))
            start_jd += dd2 * year_duration
        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd2 / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                rows.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_b),
                    round(ddb, dhasa_level_index + 1) if round_duration else ddb,
                ))
                jd_b += ddb * year_duration
            start_jd += dd2 * year_duration
        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd2, (dhasa_lord,), rows)
            start_jd += dd2 * year_duration

    return rows


def get_karaka_kendradhi_rasi_bhukthi(
    dob,
    tob,
    place,
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
        dob,
        tob,
        place,
        divisional_chart_factor,
        chart_method,
        karaka_index,
        dhasa_level_index,
        round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )


def karaka_kendradhi_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    karaka_index=1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Karaka–Kendrādhi Rāśi — return ONLY the immediate (p -> p+1) children under the given parent span.

    Strategy:
      1) PURE-TILER (fast): if optional `_children_order_karaka` is defined, compute child order (+weights)
         from birth-epoch positions; split equal/proportional; tile exact [start, end).
      2) BASE-FILTER (safe): call your base at depth (k+1) anchored at birth; filter subtree for this parent;
         clip to [parent_start, parent_end).
    """
    _set_year_duration(
        jd_at_dob,
        place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]
    k = len(path)

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

    order_func = globals().get("_children_order_karaka")
    if callable(order_func):
        planet_positions = charts.divisional_chart(
            jd_at_dob,
            place,
            divisional_chart_factor,
            chart_method=chart_method,
            **kwargs,
        )[:const._pp_count_upto_ketu]

        order, weights = None, None
        try:
            out = order_func(parent_sign, planet_positions, **kwargs)
            if isinstance(out, tuple) and len(out) == 2:
                order, weights = list(out[0]), list(out[1])
            else:
                order = list(out)
        except Exception:
            order = None

        if order:
            if weights is not None:
                W = float(sum(weights)) or 1.0
                child_years_list = [parent_years * (w / W) for w in weights[:len(order)]]
            else:
                child_years_list = [parent_years / float(len(order))] * len(order)

            out_rows, cursor = [], start_jd
            n = min(len(order), len(child_years_list))
            for i in range(n):
                cs = int(order[i])
                cy = float(child_years_list[i])
                child_end = end_jd if i == n - 1 else cursor + cy * year_duration
                out_rows.append([path + (cs,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
                cursor = child_end
                if cursor >= end_jd:
                    break
            if out_rows:
                out_rows[-1][2] = _jd_to_tuple(end_jd)
            return out_rows

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    base_rows = get_karaka_kendradhi_rasi_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        karaka_index=karaka_index,
        dhasa_level_index=k + 1,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )
    if not base_rows:
        return []

    children = []
    for row in base_rows:
        labels = tuple(row[0]) if isinstance(row[0], (tuple, list)) else (row[0],)
        if len(labels) != k + 1 or tuple(labels[:k]) != path:
            continue
        sjd = _tuple_to_jd(row[1])
        if sjd < start_jd:
            continue
        if sjd >= end_jd:
            break
        dur_y = float(row[2])
        ejd = sjd + dur_y * year_duration
        if ejd > end_jd:
            ejd = end_jd
        children.append([labels, _jd_to_tuple(sjd), _jd_to_tuple(ejd)])

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


# ============================================================
# PUBLIC: Runner (Mahā -> … -> target depth) for Karaka variant
# ============================================================
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
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
    Karaka–Kendrādhi Rāśi — running ladder at `current_jd`:
      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        ... up to requested depth ...
      ]

    Zero-duration safe:
      • L1 (Mahā) is taken from the base and any zero-duration Mahā is SKIPPED
        when building (lords, start) + sentinel for the selector.
    """
    _set_year_duration(
        jd_at_dob,
        place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

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

    def _is_zero_length_by_start_dur(start_tuple, dur_years, eps_seconds=1e-3):
        if dur_years <= 0.0:
            return True
        return (dur_years * year_duration * 86400.0) <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        if not children_rows:
            return []
        rows = []
        for lords, st, en in children_rows:
            if (_tuple_to_jd(en) - _tuple_to_jd(st)) * 86400.0 > eps_seconds:
                rows.append((lords, st))
        if not rows:
            return []
        rows.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st in rows:
            sj = _tuple_to_jd(st)
            if prev is None or sj > prev:
                proj.append((lords, st))
                prev = sj
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    def _lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    maha_rows = get_karaka_kendradhi_rasi_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        karaka_index=karaka_index,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    ) or []

    periods = []
    jd_cursor = jd_at_dob
    for labels, start_tuple, dur_years in maha_rows:
        dur = float(dur_years)
        if _is_zero_length_by_start_dur(start_tuple, dur):
            continue
        lords = _lords(labels)
        periods.append((lords, start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd_to_tuple(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd_to_tuple(jd_cursor)))

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [_lords(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    for _depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = karaka_kendradhi_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            karaka_index=karaka_index,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )
        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            ladder.append(running)
            break

        periods = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
            running = [_lords(rdk[0]), rdk[1], rdk[2]]

        ladder.append(running)

    return ladder


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y,m,d), (fh, 0, 0))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        print(
            "DLI=",
            DLI,
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=DLI,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = karaka_kendradhi_rasi_dhasa(
            dob,
            tob,
            place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
        )
        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                DLI,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=2,
            )
        )
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kendradhi_rasi_test()
