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
from jhora.horoscope.chart import charts

avg_year_days = const.average_gregorian_year

def get_dhasa_bhukthi(
    jd_years, place,
    divisional_chart_factor=1, chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,   # 1..6
    round_duration=True,                               # kept for backward compat; ignored (raw float years)
    compress_dhasa_to_annual=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Patyayini Dhasa (Tajaka annual charts).

    ✅ RETURNS (canonical, raw float years always):
        [ (lords_tuple, start_tuple(y,m,d,fh), dur_years_float), ... ]

    Where:
      • If compress_dhasa_to_annual=True  -> total cycle ≈ 1 year
      • If compress_dhasa_to_annual=False -> total cycle ≈ const.human_life_span_for_vimsottari_dhasa (typically 120 years)

    Notes:
      • round_duration is ignored by design (raw float years only).
      • JD stepping uses dur_years * avg_year_days (full precision).
      • Child order at each level is cyclic starting at the parent’s index (your bn=d logic).
      • Sub-period weights are always normalized arc weights (sum=1) so recursion is consistent.
    """
    global avg_year_days
    avg_year_days = drik.dhasa_year_duration(
        jd=jd_years,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # depth check
    try:
        lvl = int(dhasa_level_index)
    except Exception:
        lvl = int(const.MAHA_DHASA_DEPTH.ANTARA)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # chart
    cht = charts.divisional_chart(
        jd_years, place,
        divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # Exclude Rahu and Ketu (preserving your original intent)
    krisamsas = cht[:-2]
    krisamsas.sort(key=lambda x: x[1][1])  # sort by longitude-in-sign (as in your code)

    # successive arc lengths (keep your original behavior:
    # first "arc" is the absolute longitude value of the first item)
    patyamsas = [[p, (h, long - krisamsas[i-1][1][1])]
                 for i, (p, (h, long)) in enumerate(krisamsas) if i > 0]
    patyamsas = [krisamsas[0]] + patyamsas

    patyamsa_sum = sum(long for _, (_, long) in patyamsas)
    if patyamsa_sum <= 0:
        raise ValueError("Invalid Patyayini setup: sum of arcs is non-positive.")

    # normalized weights (sum to 1.0) — use for *all* levels
    w = {p: (long / patyamsa_sum) for p, (_, long) in patyamsas}

    # total years for one full cycle (annual vs uncompressed)
    TOTAL_YEARS = 1.0 if compress_dhasa_to_annual else float(const.human_life_span_for_vimsottari_dhasa)

    # cycle order
    lords = [p for p, _ in patyamsas]
    n = len(lords)

    # build L1 blocks as (lord, start_jd, dur_years)
    maha_blocks = []
    jd_cursor = jd_years
    for p in lords:
        dur_years = w[p] * TOTAL_YEARS
        maha_blocks.append((p, jd_cursor, dur_years))
        jd_cursor += dur_years * avg_year_days

    # --- emitters / recursion -------------------------------------------------

    def _emit(prefix, start_jd, dur_years, out_rows):
        out_rows.append((tuple(prefix), utils.jd_to_gregorian(start_jd), float(dur_years)))

    def _recurse(level, parent_index, parent_start_jd, parent_dur_years, prefix, out_rows):
        """
        Recursively emit leaf rows at requested depth.
        Child order: cyclic starting at parent_index (your bn=d logic).
        Child duration: parent_dur_years * w[child]  (weights always normalized).
        """
        if level == lvl:
            _emit(prefix, parent_start_jd, parent_dur_years, out_rows)
            return

        jd_child = parent_start_jd
        for k in range(n):
            idx = (parent_index + k) % n
            child = lords[idx]
            cdur_years = parent_dur_years * w[child]
            _recurse(level + 1, idx, jd_child, cdur_years, prefix + (child,), out_rows)
            jd_child += cdur_years * avg_year_days

    # --- dispatch by depth ----------------------------------------------------

    rows = []
    if lvl == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        for p, start_jd, dur_years in maha_blocks:
            _emit((p,), start_jd, dur_years, rows)
        return rows

    if lvl == int(const.MAHA_DHASA_DEPTH.ANTARA):
        # L2 flat leaf rows: ((p, pa), start, dur_years)
        for d, (p, start_jd, md_years) in enumerate(maha_blocks):
            jd_b = start_jd
            bn = d
            for _ in range(n):
                pa = lords[bn]
                cdur_years = md_years * w[pa]
                _emit((p, pa), jd_b, cdur_years, rows)
                jd_b += cdur_years * avg_year_days
                bn = (bn + 1) % n
        return rows

    # L3..L6
    for d, (p, start_jd, md_years) in enumerate(maha_blocks):
        _recurse(
            level=int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY),  # start at 1
            parent_index=d,
            parent_start_jd=start_jd,
            parent_dur_years=md_years,
            prefix=(p,),
            out_rows=rows
        )
    return rows
def patyayini_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float YEARS (one of duration or end must be provided)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    compress_dhasa_to_annual=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Patyayini immediate children (Option A):
      returns [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Notes:
      • Base durations are YEARS always.
      • Zero durations are kept as end==start.
      • Only the last *positive-span* child is clamped to parent_end (so tiling stays exact
        without stretching a zero-duration child).
    """
    # normalize parent path
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    k = len(path)

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

    # parent span (duration is YEARS)
    start_jd = _t2jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    end_jd = _t2jd(parent_end) if parent_end is not None else start_jd + float(parent_duration) * avg_year_days
    if end_jd <= start_jd:
        return []

    # ask base for k+1 depth (unrounded; years-only)
    rows = get_dhasa_bhukthi(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_level_index=k + 1,
        round_duration=False,                 # ignored in your years-only base
        compress_dhasa_to_annual=compress_dhasa_to_annual,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # collect children under this parent path (keep zeros)
    kids = []
    for (lords_tuple, st_tup, dur_years) in rows:
        lords_tuple = tuple(lords_tuple)
        if lords_tuple[:k] != path:
            continue
        sjd = _t2jd(st_tup)
        dur = float(dur_years)
        ejd = sjd + dur * avg_year_days
        # keep if it intersects parent span OR is a zero exactly on boundary
        if ejd > start_jd and sjd < end_jd:
            kids.append([lords_tuple, sjd, ejd])
        elif dur == 0.0 and (sjd == start_jd or sjd == end_jd):
            kids.append([lords_tuple, sjd, ejd])

    if not kids:
        return []

    # sort by start
    kids.sort(key=lambda r: r[1])

    # clamp only the last positive-span child to parent_end (do NOT stretch a zero-span child)
    last_pos = None
    for i, (_, sjd, ejd) in enumerate(kids):
        if ejd > sjd:
            last_pos = i
    if last_pos is not None:
        kids[last_pos][2] = end_jd

    # output (clip to parent bounds; keep zeros as end==start)
    out = []
    for lt, sjd, ejd in kids:
        cs = max(sjd, start_jd)
        ce = min(ejd, end_jd)
        # keep zero rows too (ce==cs)
        out.append((lt, _jd2t(cs), _jd2t(ce)))

    return out
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    compress_dhasa_to_annual=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Patyayini running ladder:
      returns [ [lords_tuple, start_tuple, end_tuple], ... ]

    Zero handling (your clean policy):
      • Base keeps zero-duration rows.
      • Runner skips zero spans ONLY when building selector periods.
      • If there is no positive-span period at a level, return a degenerate rung at parent_end.
      • If user asks exactly at the final boundary with no next positive span, you can raise.
    """
    global avg_year_days
    avg_year_days = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    # clamp depth
    try:
        target = int(dhasa_level_index)
    except Exception:
        target = int(const.MAHA_DHASA_DEPTH.DEHA)
    lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    hi = int(const.MAHA_DHASA_DEPTH.DEHA)
    target = min(hi, max(lo, target))

    # L1 rows from base (years-only; includes zero durations)
    l1_rows = get_dhasa_bhukthi(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,                 # ignored in years-only base
        compress_dhasa_to_annual=compress_dhasa_to_annual,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # Build selector periods from positive spans only
    periods = []
    last_end_jd = None
    last_pos_lords = None
    for (lt, st, dur_years) in l1_rows:
        lt = tuple(lt)
        sjd = _t2jd(st)
        dur = float(dur_years)
        ejd = sjd + dur * avg_year_days
        if ejd > sjd:  # positive span only for selection
            periods.append((lt, st))
            last_end_jd = ejd
            last_pos_lords = lt

    if not periods:
        # No positive span at L1. Your edge-case policy can raise if current_jd is at the boundary.
        s = utils.jd_to_gregorian(jd_at_dob)
        if current_jd == _t2jd(s):
            raise ValueError("Patyayini: no positive-span Maha period to select at boundary.")
        return [[(), s, s]]

    # sentinel end = end of last positive-span period
    periods.append((last_pos_lords, utils.jd_to_gregorian(last_end_jd)))

    # running L1
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # descend levels
    for _depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running
        parent_end_jd = _t2jd(parent_end)

        kids = patyayini_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            compress_dhasa_to_annual=compress_dhasa_to_annual,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        # child selector periods from positive spans only; sentinel parent_end
        child_periods = []
        last_pos = None
        for (lt, st, en) in kids:
            sjd = _t2jd(st)
            ejd = _t2jd(en)
            if ejd > sjd:
                child_periods.append((lt, st))
                last_pos = lt

        if not child_periods:
            # No positive-span child; degenerate rung (or raise at boundary if you prefer)
            if current_jd == parent_end_jd:
                raise ValueError("Patyayini: no positive-span child period to select at parent boundary.")
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        child_periods.append((last_pos, parent_end))  # sentinel = parent end

        rdk = utils.get_running_dhasa_for_given_date(current_jd, child_periods)
        running = [tuple(rdk[0]), rdk[1], rdk[2]]
        ladder.append(running)

    return ladder

if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)    
    jd_at_dob  = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y,m,d = map(int,current_date_str.split(','))
    hh,mm,ss = map(int,current_time_str.split(':')); fh = hh+mm/60+ss/3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y,m,d),(hh,mm,ss))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA; dcf = 1
    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(dd, jd_at_dob, place)
        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)
        start_time = time.time()
        rd1 = get_running_dhasa_for_given_date(current_jd, jd_at_dob, place,dhasa_level_index=DLI,divisional_chart_factor=dcf,
                                               compress_dhasa_to_annual=False,dhasa_duration_type=dd)
        print(rd1)
        for row in rd1:
            lords,ds,de = row
            print([ utils.resource_strings['ascendant_str'] if lord=='L' else utils.PLANET_NAMES[lord] for lord in lords],ds,de)
        print('new method elapsed time',time.time()-start_time)
        start_time = time.time()
        ad = get_dhasa_bhukthi(jd_at_dob, place, dhasa_level_index=DLI,divisional_chart_factor=dcf,compress_dhasa_to_annual=False,
                               dhasa_duration_type=dd)
        #"""
        if DLI <= const.MAHA_DHASA_DEPTH.ANTARA:
            for row in ad:
                lords,ds,de = row
                print([ utils.resource_strings['ascendant_str'] if lord=='L' else utils.PLANET_NAMES[lord] for lord in lords],ds,de)
            exit()
        #"""
        rd2 = utils.get_running_dhasa_at_all_levels_for_given_date(current_jd, ad,DLI,
                                                                   extract_running_period_for_all_levels=True)
        for row in rd2:
            lords,ds,de = row
            print([ utils.resource_strings['ascendant_str'] if lord=='L' else utils.PLANET_NAMES[lord] for lord in lords],ds,de)
        print('old method elapsed time',time.time()-start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.patyayini_tests()
