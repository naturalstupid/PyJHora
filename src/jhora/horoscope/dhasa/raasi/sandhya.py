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
    Sandhya is another Ayurdasa system. Concept: Sandhya is the Dvadashāńśa Ayurdaya of the Param Ayurdaya.
    In this dasa system, the parama-ayush is spread among the 12 Rāśis, making the dasa span of each Rāśi as 1/12th of the Paramaayush.
    For humans the Paramayush have been agreed by savants as 120 years. Hence the span of each Sandhya Dasa is 10 years.

    Also includes Pachaka Dasa Variation - wherein 10 years are divided into 3 compartments:
    NOTE: Some Authors call pachaka as PANCHAKA
    For Panchaka/Pachaka - set use_pachaka_variation to True
    1 rasi - 61/30, 3 rasis-61/60 and 8 rasis - 61/90  - each fraction of 10 years
"""
from jhora import utils, const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

_sandhya_duration = [10 for _ in range(12)]
_pachaka_duration = [60 / 31, 30 / 31, 30 / 31, 30 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31, 20 / 31]

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
    use_pachaka_variation=False,  # if True, use _pachaka_duration as weights for children at every level
    round_duration=True,          # only affects returned rows; progression uses full precision
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sandhya Dasha with multi-level expansion (L1..L6).

    Output (variable arity by level):
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Rules:
      • Replaces include_antardhasa with dhasa_level_index (1..6).
      • Each deeper level is computed from its immediate parent.
      • Equal split ×12 by default; if use_pachaka_variation=True, use _pachaka_duration as weights (normalized).
      • Σ(children) == parent. No rounding in progression; rounding only in returned rows if round_duration=True.
      • Timestamps via utils.jd_to_gregorian(jd).
      • Preserves Sandhya MD order from _sandhya_duration.
    """
    # ------------------------
    # Prepare chart & MD progression
    # ------------------------
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

    _dhasa_seed = pp[0][1][0]  # asc house index
    # MD progression: 12 signs starting from seed; durations from module-level _sandhya_duration
    _dhasa_progression = [((_dhasa_seed + h) % 12, _durn) for h, _durn in enumerate(_sandhya_duration)]

    dhasa_info = []
    start_jd = jd_at_dob

    # ------------------------
    # Local helpers (no timestamp wrapper; use utils.* directly)
    # ------------------------
    def _child_sequence(parent_lord):
        """Ordered list of 12 child lords for Sandhya: forward from parent_lord."""
        return [(parent_lord + h) % 12 for h in range(12)]

    def _child_durations(parent_duration_years):
        """
        Child durations for the next level.
        - If use_pachaka_variation: use _pachaka_duration as weights (normalized to sum=1).
        - Else: equal split among 12 (each 1/12).
        Returns list of 12 absolute durations whose sum equals parent_duration_years.
        """
        if use_pachaka_variation:
            total_w = float(sum(_pachaka_duration))
            if total_w <= 0:
                return [parent_duration_years / 12.0] * 12
            return [parent_duration_years * (w / total_w) for w in _pachaka_duration]
        else:
            return [parent_duration_years / 12.0] * 12

    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row with start time string and (optionally rounded) duration.
        Produces: ((lords...), start_tuple, dur)
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, dhasa_level_index + 1
        )
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))
        # Advance time by the leaf duration
        return start_jd_val + seg_duration_years * year_duration

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand segments down to target_level.
        - If current_level == target_level: append a single row for the entire segment.
        - Else: split into 12 children using order from _child_sequence and durations from _child_durations.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence(parent_lord)
        child_durs = _child_durations(parent_duration_years)

        for i, child_lord in enumerate(children):
            start_jd_val = _expand_children(
                start_jd_val,
                child_durs[i],
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ------------------------
    # Generate rows (single cycle; Sandhya has MD durations from _sandhya_duration)
    # ------------------------
    for md_lord, md_years in _dhasa_progression:
        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    return dhasa_info


def sandhya_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years  (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    use_pachaka_variation: bool = False,       # if True, use _pachaka_duration weights
    round_duration: bool = False,              # tiler returns exact spans; do not round here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Sandhyā Daśā — return ONLY the immediate (parent -> children) splits.

    Output rows:
        [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Rules:
      • Child order: 12 signs forward from the parent.
      • Child durations:
          - equal split (/12), OR
          - Pāchaka variation: normalized _pachaka_duration[] weights × parent_years.
      • Exact tiling on [parent_start, parent_end).
      • Zero-span parent -> [].
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")

    parent_lord = path[-1]

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- resolve parent span (use selected module-level year_duration)
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

    # ---- child order: forward from parent (12 signs)
    children = [(parent_lord + h) % 12 for h in range(12)]

    # ---- child durations
    if use_pachaka_variation:
        total_w = float(sum(_pachaka_duration))
        if total_w <= 0:
            child_years_list = [parent_years / 12.0] * 12
        else:
            child_years_list = [parent_years * (w / total_w) for w in _pachaka_duration]
    else:
        child_years_list = [parent_years / 12.0] * 12

    # ---- tile exactly within [start, end)
    rows, cursor = [], start_jd
    for i, (child_lord, yrs) in enumerate(zip(children, child_years_list)):
        child_end = end_jd if i == 11 else cursor + yrs * year_duration
        # skip degenerate zero-length child (robustness at boundaries)
        if child_end > cursor:
            rows.append((path + (child_lord,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)))
        cursor = child_end
        if cursor >= end_jd:
            break

    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd_to_tuple(end_jd))  # clamp final child to parent end
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
    """
    Sandhyā Daśā — running ladder at `current_jd`:
      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        ...
        [(l1,..,l_d),        startd, endd]
      ]

    Zero-duration safe:
      • Mahā ladder is taken from the base (depth=1) and any 0-year Mahā is SKIPPED
        when building selector periods (strictly increasing starts + sentinel).
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

    # ---- zero-length tests & converter
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
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    # ---- L1 Mahā via base (depth=1, unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        use_pachaka_variation=use_pachaka_variation,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # Build (lords, start) + sentinel — SKIP zero-year Mahās
    periods = []
    jd_cursor = jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        dur = float(dur_years)
        if _is_zero_by_start_dur(start_tuple, dur):
            continue  # skip 0-year MD
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd_to_tuple(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd_to_tuple(jd_cursor)))  # sentinel end

    # ---- Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Step-down using immediate-children (exact tiling; zero-safe)
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = sandhya_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years, months=months, sixty_hours=sixty_hours,
            use_pachaka_variation=use_pachaka_variation,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            # zero-span parent (or no children) → represent boundary
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        child_periods = _to_selector_periods_zero_safe(kids, parent_end_tuple=parent_end)
        if not child_periods:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        rdk = utils.get_running_dhasa_for_given_date(current_jd, child_periods)
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
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=_dhasa_cycle_count
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.sandhya_test()
