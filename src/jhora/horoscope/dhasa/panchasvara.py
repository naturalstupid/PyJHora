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
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

"""
    Compute Panchasvara Dhasa - Ref: https://astrosutras.in/index.php/2025/03/04/panchasvara-dasha-system/
"""

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


SVARAS = {
    0: ("A", "aakaasha"),
    1: ("I", "agni"),
    2: ("U", "prithvi"),
    3: ("E", "vaayu"),
    4: ("O", "jala"),
}  # You can use A_str, I_str,U_str,E_str,O_str for native language strings
SVARA_YEARS = 12.0
TOTAL_CYCLE = 60.0


def _get_svara_id(idx):
    if idx in [0, 2, 4, 7, 9, 11, 13, 15]:
        return 0  # A
    if idx in [1, 3, 5, 8, 10, 12, 14, 16]:
        return 1  # I
    if idx in [17, 18, 19, 20, 21, 22, 23]:
        return 2  # U # 20=Uthiradam, 21 is Abhijit, 22 is Shravan
    if idx in [24, 25, 26, 27]:
        return 3  # E # 27 is Revathi
    return 4  # O (fallback)


def _panchasvara_order_from_start_longitude(start_lon):
    """Return the five svara ids in cyclic order from the 28-nakshatra start point."""
    nak_span = 360.0 / 28.0
    nak_val = start_lon / nak_span
    nak_index = int(nak_val)
    start_svara_id = _get_svara_id(nak_index)

    order = []
    curr = start_svara_id
    for _ in range(5):
        order.append(curr)
        curr = (curr + 1) % 5
    return order, nak_val, nak_index


def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    star_position_from_moon=1,  # '1'=Moon, 'L'=Lagna, etc.
    dhasa_starting_planet=1,
    chart_method=1,  # divisional_chart_method
    round_duration=True,
    use_pancha_elements_for_svaras=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Panchasvara Dasa (60-year cycle).
    - 28 Nakshatra system (including Abhijit).
    - 5 Svaras (A, I, U, E, O), each 12 years.
    """
    # 1. Get starting position (Moon, Lagna, etc.)
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type, savana_year_method)

    pp = charts.divisional_chart(
        jd, place,
        divisional_chart_factor,
        chart_method=chart_method,
        **kwargs
    )

    # Find longitude of the starting point (p_id '1' for Moon)
    start_lon = charts.get_chart_element_longitude(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet
    )

    # 2. 28-Nakshatra Logic (360 / 28)
    order, nak_val, nak_index = _panchasvara_order_from_start_longitude(start_lon)
    balance_factor = 1.0 - (nak_val - nak_index)

    # 5. Recursive Engine
    results = []
    total_elapsed = 0.0
    jd_tracker = jd

    def recurse_dasa(current_depth, parent_duration, lords_stack, is_first_maha):
        nonlocal jd_tracker, total_elapsed

        for i, s_id in enumerate(order):
            if current_depth == 1:
                duration = SVARA_YEARS
                if is_first_maha and i == 0:
                    duration *= balance_factor
            else:
                # Proportional sub-period: (12 * 12) / 60 = 2.4 years
                duration = parent_duration * (SVARA_YEARS / TOTAL_CYCLE)

            new_lord = [SVARAS[s_id][1]] if use_pancha_elements_for_svaras else [SVARAS[s_id][0]]
            new_lords = lords_stack + new_lord

            if current_depth == dhasa_level_index:
                y, m, d, fh = utils.jd_to_gregorian(jd_tracker)
                durn = round(duration, dhasa_level_index) if round_duration else duration
                results.append([new_lords] + [(y, m, d, fh)] + [durn])

                jd_tracker += (duration * year_duration)
                total_elapsed += duration
            else:
                recurse_dasa(current_depth + 1, duration, new_lords, False)

    # 6. Execute
    is_initial = True
    max_dhasa_cycles = 2
    for _ in range(max_dhasa_cycles):
        recurse_dasa(1, None, [], is_initial)
        is_initial = False
    return results


def panchasvara_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (one of duration or end must be provided)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    # accepted for API parity (not used by Panchasvara itself)
    antardhasa_option: int = 1,
    # forwarded knobs used to compute start order (same as base)
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=None,
    dhasa_starting_planet=1,
    use_tribhagi_variation=False,
    round_duration: bool = False,
    use_pancha_elements_for_svaras: bool = True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Panchasvara — return ONLY the immediate (parent -> children) splits.

    Output:
      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Notes:
      • Branching factor is 5 (A-I-U-E-O), not 12.
      • Each deeper level uses the same 5-item order; each child duration = parent * (12/60) = parent * 0.2.
      • Uses parent span passed in (so it automatically handles balance on the very first maha).
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize parent path
    if isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        path = (parent_lords,)  # allow scalar

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

    if end_jd <= start_jd:
        return []

    # ---- compute the 5-svara order (same logic as base) ----
    # start longitude of chosen reference point (moon/lagna/etc.)
    start_lon = charts.get_chart_element_longitude(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet
    )

    order_ids, _, _ = _panchasvara_order_from_start_longitude(start_lon)

    # choose label strings (elements vs vowels)
    if use_pancha_elements_for_svaras:
        order_labels = [SVARAS[sid][1] for sid in order_ids]
    else:
        order_labels = [SVARAS[sid][0] for sid in order_ids]

    # ---- split into 5 children (each = parent * 12/60) ----
    child_years = parent_years * (SVARA_YEARS / TOTAL_CYCLE)  # 12/60 = 0.2
    rows, cursor = [], start_jd

    for i, lab in enumerate(order_labels):
        child_end = end_jd if i == 4 else cursor + child_years * year_duration
        if child_end > cursor:
            rows.append((path + (lab,), _jd2t(cursor), _jd2t(child_end)))
        cursor = child_end
        if cursor >= end_jd:
            break

    if rows:
        rows[-1] = (rows[-1][0], rows[-1][1], _jd2t(end_jd))
    return rows


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    # forwarded to base/tiler
    use_tribhagi_variation: bool = False,
    star_position_from_moon: int = 1,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    seed_star=None,
    dhasa_starting_planet: int = 1,
    antardhasa_option: int = 1,
    use_pancha_elements_for_svaras: bool = True,
    round_duration: bool = False,     # runner uses exact start/end
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Panchasvara — running ladder at `current_jd`:

      [
        [lords_tuple_L1, start1, end1],
        [lords_tuple_L2, start2, end2],
        ...
      ]

    Notes:
      • L1 periods come from your base (unrounded), skip only duration<=0 if any.
      • Deeper levels use panchasvara_immediate_children (5-way split).
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize depth
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # tuple<->JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    # --- L1 via base (unrounded) ---
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    l1 = get_dhasa_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
        chart_method=chart_method,
        round_duration=False,
        use_pancha_elements_for_svaras=use_pancha_elements_for_svaras,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # base rows are: [new_lords_list] + [(y,m,d,fh)] + [dur]
    # build selector periods: [(lords_tuple, start_tuple), ...] + sentinel(end)
    periods = []
    last_end_jd = None
    for row in l1:
        lords_list = row[0]
        start_tuple = row[1]
        dur_years = float(row[2])
        if dur_years <= 0.0:
            continue
        lords_tuple = tuple(lords_list)
        periods.append((lords_tuple, start_tuple))
        last_end_jd = _t2jd(start_tuple) + dur_years * year_duration

    if not periods:
        # nothing usable
        s = utils.jd_to_gregorian(jd_at_dob)
        return [[(), s, s]]

    # sentinel: end of last non-zero L1
    periods.append((periods[-1][0], utils.jd_to_gregorian(last_end_jd)))

    # Running L1 (expects [(lords,start),..., sentinel])
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # descend levels 2..target using immediate children
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = panchasvara_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            star_position_from_moon=star_position_from_moon,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_starting_planet=dhasa_starting_planet,
            use_pancha_elements_for_svaras=use_pancha_elements_for_svaras,
            antardhasa_option=antardhasa_option,
            seed_star=seed_star,
            use_tribhagi_variation=use_tribhagi_variation,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        # selector list for children: [(lords,start),..., sentinel(parent_end)]
        child_periods = [(lt, st) for (lt, st, en) in kids if _t2jd(en) > _t2jd(st)]
        if not child_periods:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break
        child_periods.append((child_periods[-1][0], parent_end))

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
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            dob, tob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, DLI,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=2
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    utils.set_language('ta')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.03862, 80.261818, 5.5)
    dhasa_level_index = 2
    divisional_chart_factor = 1
    star_position_from_moon = 1
    dhasa_starting_planet = 1
    chart_method = 1
    rd = get_dhasa_bhukthi(
        dob, tob, place, divisional_chart_factor, dhasa_level_index,
        star_position_from_moon, dhasa_starting_planet, chart_method,
        use_pancha_elements_for_svaras=True
    )
    print(rd)
    for plords, s_date, durn in rd:
        pancha_str = '-'.join([utils.resource_strings[plord + '_str'] for plord in plords])
        s_date_str = f"({s_date[0]},{s_date[1]},{s_date[2]} " + utils.to_dms(s_date[3])
        print(pancha_str, s_date_str, durn)
