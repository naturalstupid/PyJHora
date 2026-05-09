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
from jhora.horoscope.chart import charts, house
from jhora.horoscope.dhasa.raasi import chara, sthira
from jhora.panchanga import drik

""" Mahadasa match with JHora. Antardasa does not match with JHora """

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
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,   # 1..6; default L2 (Maha + Antara)
    round_duration=False,   # only affects returned rows; progression uses full precision
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Yogardha Dasha with multi-level expansion (L1..L6).

    Return shape by level:
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Rules:
      • L1 lords: stronger of Lagna vs 7th as seed; forward from seed, reverse if seed is even.
      • L1 duration (years): 0.5 * (chara._dhasa_duration(md) + sthira._dhasa_duration(md)).
      • Lx+1 lords: chara._antardhasa(Lx_lords)  (global transformation per level).
      • Lx duration: L(x-1) / 12 (equal split at each deeper level).
      • Σ(children) == parent; no double-advancing JD.
      • Timestamps via utils.jd_to_gregorian(jd).
      • No rounding in progression; optional rounding in returned durations via round_duration.
    """
    # --- Chart & seed ---
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    asc_house = planet_positions[0][1][0]
    seventh_house = (asc_house + 6) % 12  # your original uses (asc+6)%12
    dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)

    # L1 (Maha) sequence: forward from seed; reverse if seed is even
    l1_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        l1_lords = [(dhasa_seed - h + 12) % 12 for h in range(12)]

    # Precompute lords sequence per level using chara._antardhasa(Lx) → Lx+1
    levels_lords = {1: l1_lords}
    for lvl in range(2, int(dhasa_level_index) + 1):
        levels_lords[lvl] = chara._antardhasa(levels_lords[lvl - 1])

    dhasa_info = []
    start_jd = jd_at_dob

    # --- Helpers ---
    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row and advance by seg_duration_years.
        """
        disp_dur = seg_duration_years if not round_duration else round(seg_duration_years, dhasa_level_index + 1)
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))
        return start_jd_val + seg_duration_years * year_duration

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand a segment down to target_level.
          • If current_level == target_level → append one row for the entire segment.
          • Else → split evenly among 12 children (order from precomputed levels_lords[current_level+1]).
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        # Children at next level are the global sequence for that level (from chara._antardhasa)
        children = levels_lords[current_level + 1]
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

    # --- Generate rows (single cycle; L1 durations via chara/sthira average) ---
    for md_lord in l1_lords:
        md_years = 0.5 * (
            chara._dhasa_duration(planet_positions, md_lord) +
            sthira._dhasa_duration(md_lord)
        )

        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    return dhasa_info


def yogardha_immediate_children(
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
    round_duration: bool = False,   # tiler returns exact spans; leave unrounded here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Yogardha — return ONLY the immediate (parent -> 12 children) splits:

      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Child-order rule (matches your base):
      • L1 lords: seed = stronger(Lagna, 7th); forward from seed; reverse if seed is even.
      • L(k+1) lords: level-wise global sequence via `chara._antardhasa(Lk)`.

    Equal split at this step (/12); exact JD tiling; Σ(children) == parent.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_level = len(path)          # L1→1, L2→2, ...

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

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

    # positions @ birth
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # ---- rebuild level-wise global sequences (like your base) ----
    asc = planet_positions[0][1][0]
    sev = (asc + 6) % 12
    seed = house.stronger_rasi_from_planet_positions(planet_positions, asc, sev) % 12

    level_lords = [(seed + h) % 12 for h in range(12)]
    if seed in const.even_signs:
        level_lords = [(seed - h) % 12 for h in range(12)]

    # parent at level=k → children = sequence at level k+1
    for _ in range(1, parent_level):
        level_lords = chara._antardhasa(level_lords)
    children = chara._antardhasa(level_lords)

    # equal split & exact tiling
    child_years = parent_years / 12.0
    rows, cursor = [], start_jd
    for i, sgn in enumerate(children):
        child_end = end_jd if i == 11 else cursor + child_years * year_duration
        if child_end > cursor:  # defensive: skip degenerate zero-length
            rows.append((path + (int(sgn) % 12,), _jd2t(cursor), _jd2t(child_end)))
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
    divisional_chart_factor: int = 1,
    chart_method=1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,                    # runner uses exact spans; keep unrounded here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Yogardha — running ladder at `current_jd`:

      [
        [(L1,),                  start1, end1],
        [(L1,L2),                start2, end2],
        ...
        [(L1,..,L_d),            startd, endd]
      ]

    Notes:
      • L1 is pulled from your base (unrounded).
      • Deeper levels expanded via `yogardha_immediate_children(...)`.
      • Zero-duration safety in selector lists (skip ≤0 spans; add sentinel).
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

    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

    # zero-length checks & projector
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
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # Build (lords,start)+sentinel — skip 0y MDs (defensive)
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

    # 2) Expand only the running parent at deeper levels
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = yogardha_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years, months=months, sixty_hours=sixty_hours,
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
        print("Deha        :", get_running_dhasa_for_given_date(
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
    pvr_tests.yogardha_dhasa_test()
