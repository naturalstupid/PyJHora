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

# Module-level year basis. Public entry points refresh this via drik.dhasa_year_duration().
year_duration = const.sidereal_year


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _dhasa_duration(lord):
    if lord in const.movable_signs:
        return 7
    elif lord in const.fixed_signs:
        return 8
    else:
        return 9


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,   # 1..6; default L2 (Maha + Antara)
    round_duration=False,  # round only in returned rows; progression uses full precision
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sthira Dasha with multi-level expansion (L1..L6).

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
    """
    # Chart & seed
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    brahma = house.brahma(planet_positions)
    brahma_sign = planet_positions[brahma + 1][1][0]  # seed rāśi
    md_lords = [(brahma_sign + h) % 12 for h in range(12)]  # forward sequence

    dhasa_info = []
    start_jd = jd_at_dob

    # ----- helpers -----
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row and advance by seg_duration_years.
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, dhasa_level_index + 1
        )
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))
        return start_jd_val + seg_duration_years * year_duration

    def _child_sequence(parent_lord):
        # Sthira: children go forward from parent_lord
        return [(parent_lord + h) % 12 for h in range(12)]

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a node to the requested depth.
        - If current_level == target_level: append one row covering the full segment.
        - Else: split parent duration equally among 12 children in forward order.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence(parent_lord)
        child_duration = parent_duration_years / 12.0  # equal split

        for child_lord in children:
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ----- generate rows (single cycle; durations via _dhasa_duration) -----
    for md_lord in md_lords:
        md_years = _dhasa_duration(md_lord)  # preserve your duration logic
        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )
    return dhasa_info


def sthira_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years  (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,           # tiler returns exact spans; no rounding here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sthira Daśā — return ONLY the immediate (parent -> children) splits.

    Output rows:
      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Rules aligned to your base:
      • Children sequence: 12 signs *forward* from the parent sign.
      • Children durations: *equal split* of the parent (/12).
      • Exact tiling on [parent_start, parent_end); zero-span parent -> [].
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- parent span (use selected module-level year_duration)
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    # zero-span parent → no children
    if end_jd <= start_jd:
        return []

    # ---- Sthira children order: forward from parent
    child_signs = [(parent_sign + h) % 12 for h in range(12)]

    # ---- equal split and exact tiling
    child_years = parent_years / 12.0
    incr_days = child_years * year_duration

    rows, cursor = [], start_jd
    for i, sgn in enumerate(child_signs):
        child_end = end_jd if i == 11 else cursor + incr_days
        if child_end > cursor:  # skip degenerate zero-length child
            rows.append((path + (sgn,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)))
        cursor = child_end
        if cursor >= end_jd:
            break

    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd_to_tuple(end_jd))
    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,   # 1..6
    *,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,                    # runner uses exact start/end; no rounding here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sthira Daśā — running ladder at `current_jd`:
      [
        [(L1,),                  start1, end1],
        [(L1,L2),                start2, end2],
        ...
        [(L1,..,L_d),            startd, endd]
      ]

    Zero-duration safe:
      • Uses base (depth=1) to build (lords,start)+sentinel and *skips* any 0-year Mahā
        before calling the selector.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- depth normalization
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- zero-length checks
    def _is_zero_by_start_dur(start_tuple, dur_years, eps_seconds=1e-3):
        if dur_years <= 0.0:
            return True
        return (dur_years * year_duration * 86400.0) <= eps_seconds

    def _to_selector_periods_zero_safe(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ (lords_tuple, start_tuple, end_tuple), ... ]
        -> strictly increasing [(lords, start), ..., sentinel(parent_end)]
        """
        if not children_rows:
            return []
        rows = []
        for lt, st, en in children_rows:
            if (_tuple_to_jd(en) - _tuple_to_jd(st)) * 86400.0 > eps_seconds:
                rows.append((lt, st))
        if not rows:
            return []
        rows.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lt, st in rows:
            sj = _tuple_to_jd(st)
            if prev is None or sj > prev:
                proj.append((lt, st))
                prev = sj
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel
        return proj

    # ---- Step 1: Mahā via base (depth=1, unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # Build (lords, start) + sentinel — skip zero-year Mahās (defensive)
    periods = []
    jd_cursor = jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        dur = float(dur_years)
        if _is_zero_by_start_dur(start_tuple, dur):
            continue
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd_to_tuple(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd_to_tuple(jd_cursor)))  # sentinel

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Step 2..target: expand only the running parent each time
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = sthira_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years, months=months, sixty_hours=sixty_hours,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_selector_periods_zero_safe(kids, parent_end_tuple=parent_end)
        if not periods:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
        running = [tuple(rdk[0]), rdk[1], rdk[2]]
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
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    _dhasa_cycle_count = 1
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Maha        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob, tob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        )
        """
        for row in ad:
            lords, ds, dur = row
            print([utils.RAASI_LIST[lord] for lord in lords], ds, dur)
        """
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=_dhasa_cycle_count
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.sthira_dhasa_test()
