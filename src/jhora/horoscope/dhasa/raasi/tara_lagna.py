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


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,     # 1..6; default L2 (Mahā + Antar)
    round_duration=False,    # only affects returned rows; progression uses full precision
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Tara Lagna Daśā (single cycle), depth-enabled.

    Returns (canonical flat list), each row shaped as:
        ( (L1,...,Lk),  (y,m,d,fh),  duration_years_float )

    Rules:
      • L1 (Mahā) duration = 9 years for each MD.
      • Seed = Ascendant + twelfth-of-current-nakshatra (Moon). If seed is even, reverse MD order.
      • L2..L6 child order ALWAYS follows Atma Karaka (AK) sign:
            forward from AK; reverse if AK sign ∈ {1,5,7,10}.
      • Lx duration = parent / 12 (equal split) at every deeper level.
      • Σ(children) == parent (exact JD tiling; no double-advance).
      • No rounding in progression; if `round_duration` is True, round only the returned duration.

    Notes:
      • Assumes planet_positions format where:
            planet_positions[i][1][0] = sign index (0..11),
            planet_positions[i][1][1] = decimal degrees within sign.
    """
    # ---- clamp depth to 1..6 ----
    try:
        lvl = int(dhasa_level_index)
    except Exception:
        lvl = const.MAHA_DHASA_DEPTH.ANTARA
    lvl = max(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, min(const.MAHA_DHASA_DEPTH.DEHA, lvl))

    # ---- epoch & chart ----
    start_jd = utils.julian_day_number(dob, tob)
    _set_year_duration(start_jd, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        start_jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # Asc sign (0..11)
    asc_house = planet_positions[0][1][0]

    # Absolute Moon longitude (decimal degrees 0..360)
    moon_sign = planet_positions[2][1][0]
    moon_deg_in_sign = float(planet_positions[2][1][1])  # decimal degrees within sign
    moon_longitude = moon_sign * 30.0 + moon_deg_in_sign

    # Nakshatra & its twelfth
    one_star = 360.0 / 27.0
    nak_frac = one_star / 12.0
    nak, _, _ = drik.nakshatra_pada(moon_longitude)          # nak ∈ {1..27}
    inside = moon_longitude - (nak - 1) * one_star           # degrees into current nakshatra
    which_12th = int(inside // nak_frac)                     # 0..11

    # Seed & MD order
    dhasa_seed = (asc_house + which_12th) % 12
    md_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        md_lords = [(dhasa_seed - h) % 12 for h in range(12)]

    # Atma Karaka & its sign
    ak = house.chara_karakas(planet_positions)[0]            # AK = first in chara_karakas
    akh = planet_positions[ak + 1][1][0]                     # AK sign (0..11)

    rows = []

    # ---- leaf appender (round only returned duration) ----
    def _append_leaf(lords_stack, start_jd_val, seg_years):
        dur_out = seg_years if not round_duration else round(seg_years, lvl + 1)
        rows.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), float(dur_out)))
        return start_jd_val + seg_years * year_duration

    # ---- AK-driven sequence for all deeper levels (keep your rule) ----
    def _ak_child_sequence():
        seq = [(akh + h) % 12 for h in range(12)]
        # keep as-is per your note: reverse if AK sign ∈ {1,5,7,10}
        if akh in [1, 5, 7, 10]:
            seq = [(akh - h) % 12 for h in range(12)]
        return seq

    # ---- recursive builder ----
    def _expand(start_jd_val, parent_years, lords_stack, level, target):
        if level == target:
            return _append_leaf(lords_stack, start_jd_val, parent_years)
        child_years = parent_years / 12.0
        children = _ak_child_sequence()
        for child in children:
            start_jd_val = _expand(start_jd_val, child_years, lords_stack + [child], level + 1, target)
        return start_jd_val

    # ---- Single cycle; each MD = 9 years ----
    jd_cursor = start_jd
    for md in md_lords:
        jd_cursor = _expand(jd_cursor, 9.0, [md], level=1, target=lvl)

    return rows


def tara_lagna_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method=1,
    round_duration: bool = False,        # tiler returns exact spans; no rounding here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Tara Lagna — return ONLY the immediate (parent -> 12 children) splits:

      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Rules:
      • Child order at ALL deeper levels is driven by AK sign:
            forward from AK; reverse if AK sign ∈ {1,5,7,10}.
      • Equal split of parent (/12); exact JD tiling on [start,end).
      • No rounding in JD math here (Σ children == parent).
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd2t(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # resolve parent span
    start_jd = _t2jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _t2jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    # zero-span parent → no children
    if end_jd <= start_jd:
        return []

    # planet positions @ birth
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # AK sign & child order (keep your reverse set {1,5,7,10})
    ak = house.chara_karakas(planet_positions)[0]
    akh = planet_positions[ak + 1][1][0]   # 0..11
    order = [(akh + h) % 12 for h in range(12)]
    if akh in [1, 5, 7, 10]:
        order = [(akh - h) % 12 for h in range(12)]

    # equal split & exact tiling
    child_years = parent_years / 12.0
    rows, cursor = [], start_jd
    for i, sgn in enumerate(order):
        child_end = end_jd if i == 11 else cursor + child_years * year_duration
        if child_end > cursor:  # skip degenerate zero-length (defensive)
            rows.append((path + (int(sgn),), _jd2t(cursor), _jd2t(child_end)))
        cursor = child_end
        if cursor >= end_jd:
            break

    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd2t(end_jd))  # clamp final child to parent end
    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,   # 1..6
    *,
    divisional_chart_factor: int = 1,
    chart_method=1,
    round_duration: bool = False,                    # runner uses exact start/end; no rounding here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Tara Lagna — running ladder at `current_jd`:

      [
        [(L1,),                  start1, end1],
        [(L1,L2),                start2, end2],
        ...
        [(L1,..,L_d),            startd, endd]
      ]

    Notes:
      • L1 is sourced from base `get_dhasa_antardhasa(..., MAHA_DHASA_ONLY)` (unrounded).
      • Zero-duration safety in selector lists (skip 0y; add sentinel).
      • Children are expanded via `tara_lagna_immediate_children(...)` (AK-driven at all deeper levels).
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # depth normalization
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd2t(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # zero-length checks & selector projector
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
            if (_t2jd(en) - _t2jd(st)) * 86400.0 > eps_seconds:
                rows.append((lt, st))
        if not rows:
            return []
        rows.sort(key=lambda r: _t2jd(r[1]))
        proj, prev = [], None
        for lt, st in rows:
            sj = _t2jd(st)
            if prev is None or sj > prev:
                proj.append((lt, st))
                prev = sj
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel
        return proj

    # 1) L1 MD via base (unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    l1_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # Build (lords,start)+sentinel for selector — skip 0y MDs (defensive)
    periods, jd_cursor = [], jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in l1_rows:
        dur = float(dur_years)
        if _is_zero_by_start_dur(start_tuple, dur):
            continue
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _t2jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd2t(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd2t(jd_cursor)))  # sentinel end

    # Running L1
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # 2) Expand only the running parent per deeper level (AK-driven)
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = tara_lagna_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
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
        """
        for row in ad:
            lords, ds, dur = row
            print([utils.RAASI_LIST[lord] for lord in lords], ds, dur)
        exit()
        """
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=_dhasa_cycle_count
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.tara_lagna_dhasa_test()
