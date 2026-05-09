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


def _shoola_dhasa(chart, dob):
    """
        calculate Shoola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house + 7 - 1) % 12
    dhasa_seed_sign = house.stronger_rasi(h_to_p, asc_house, seventh_house)
    if dhasa_seed_sign != asc_house:
        dhasa_seed_sign = (dhasa_seed_sign + asc_house - 1) % 12
    " direction is always forward for this shoola dhasa and dhasa duration is always 9 years"
    direction = 1
    dhasa_progression = [(dhasa_seed_sign + direction * k) % 12 for k in range(12)]
    dhasa_periods = []
    dhasa_duration = 9
    dhasa_start = dob_year
    for sign in dhasa_progression:
        dhasa_end = dhasa_start + dhasa_duration
        andtardhasa = _antardhasa(sign, p_to_h)
        dhasa_period_suffix = '-' + str(dob_month) + '-' + str(dob_day)
        dhasa_periods.append([sign, str(dhasa_start) + dhasa_period_suffix, str(dhasa_end) + dhasa_period_suffix, andtardhasa, dhasa_duration])
        dhasa_start = dhasa_end
    # Second cycle
    dhasa_start = dhasa_end
    total_dhasa_duration = sum([row[-1] for row in dhasa_periods])
    for c, sign in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_periods[c][-1]
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <= 0:  # no need for second cycle as first cycle had 12 years
            continue
        dhasa_end = dhasa_start + dhasa_duration
        andtardhasa = _antardhasa(sign, p_to_h)
        dhasa_period_suffix = '-' + str(dob_month) + '-' + str(dob_day)
        dhasa_periods.append([sign, str(dhasa_start) + dhasa_period_suffix, str(dhasa_end) + dhasa_period_suffix, andtardhasa, dhasa_duration])
        dhasa_start = dhasa_end
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_periods


def _antardhasa(antardhasa_seed_rasi, p_to_h):
    direction = -1
    if p_to_h[6] == antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs:  # Forward
        direction = 1
    if p_to_h[8] == antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi + direction * i) % 12 for i in range(12)]


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=2,                 # 1..6 (default: L2 = Maha + Antara)
    round_duration=False,
    *,
    house_index: int = 1,                # 1..12 — from where Shoola MD should start
    antardhasa_seed_option: int = 2,     # 1=lord; 2=stronger(S,7th); 3=lord(stronger(S,7th))
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Shoola Dasha entry point (depth-enabled).
    Returns canonical rows: [ ((L1..Lk), (y,m,d,fh), dur_years), ... ]
    """
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]

    return shoola_dhasa(
        planet_positions,
        dob,
        tob,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        house_index=house_index,
        antardhasa_seed_option=antardhasa_seed_option
    )


def shoola_dhasa(
    planet_positions,
    dob,
    tob,
    dhasa_level_index=2,                 # 1..6; default L2 (Maha + Antara)
    round_duration=False,
    *,
    house_index: int = 1,                # 1..12
    antardhasa_seed_option: int = 1      # 1=lord; 2=stronger(S,7th); 3=lord(stronger(S,7th))
):
    """
    Calculate Shoola Dasha up to the requested depth.

    Output (canonical, variable arity by level):
      L1: ((MD,),                (y,m,d,fh), dur_years)
      L2: ((MD, AD),             (y,m,d,fh), dur_years)
      L3: ((MD, AD, PD),         (y,m,d,fh), dur_years)
      ...
      L6: ((L1, L2, L3, L4, L5, L6), (y,m,d,fh), dur_years)

    Behavior:
      • MD seed = house at (Lagna + house_index - 1).
      • MD order: 12 signs forward, each 9 years.
      • Antardasha seed option (applied at every parent level):
          1 → start from rasi of lord(parent_sign)
          2 → start from stronger(parent_sign, 7th_from_parent)
          3 → start from rasi of lord(stronger(parent_sign, 7th_from_parent))
      • Children at each deeper level: 12 signs forward from resolved seed.
      • Children split = equal (/12). Σ(children) = parent (exact tiling).
      • No rounding in time math; optional rounding only on returned duration.
    """
    # ---- validate
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")
    if not (1 <= int(house_index) <= 12):
        raise ValueError("house_index must be in 1..12")
    if int(antardhasa_seed_option) not in (1, 2, 3):
        raise ValueError("antardhasa_seed_option must be 1, 2, or 3")

    # ---- chart mappings
    start_jd = utils.julian_day_number(dob, tob)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    # ---- MD seed from requested house_index (1-based from Lagna)
    asc_house = p_to_h[const._ascendant_symbol]
    base_sign = (asc_house + (int(house_index) - 1)) % 12
    base_sign_7th = (base_sign + const.HOUSE_7) % 12
    md_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, base_sign, base_sign_7th)

    # ---- MD progression: forward 12 from seed; each 9 years
    md_progression = [(md_seed_sign + k) % 12 for k in range(12)]
    md_years = 9.0

    # ---- helpers
    def _emit_row(lords_stack, start_jd_val, seg_years, out_rows):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        y, m, d, fh = utils.jd_to_gregorian(start_jd_val)
        out_rows.append((tuple(lords_stack), (int(y), int(m), int(d), float(fh)), float(disp)))
        return start_jd_val + seg_years * year_duration

    def _antara_seed(parent_sign: int) -> int:
        """Return the *rāśi* from which to start the 12-child sequence."""
        if antardhasa_seed_option == 1:
            lord = house.house_owner_from_planet_positions(planet_positions, parent_sign)
            return int(p_to_h[lord]) % 12
        elif antardhasa_seed_option == 2:
            strong = house.stronger_rasi_from_planet_positions(planet_positions, parent_sign, (parent_sign + 6) % 12)
            return int(strong) % 12
        else:  # antardhasa_seed_option == 3
            strong = house.stronger_rasi_from_planet_positions(planet_positions, parent_sign, (parent_sign + 6) % 12)
            lord = house.house_owner_from_planet_positions(planet_positions, strong)
            return int(p_to_h[lord]) % 12

    def _child_sequence(parent_sign: int):
        seed = _antara_seed(parent_sign)
        return [(seed + i) % 12 for i in range(12)]

    def _expand(start_jd_val, parent_years, lords_stack, level, target_level, out_rows):
        if level == target_level:
            return _emit_row(lords_stack, start_jd_val, parent_years, out_rows)
        child_years = parent_years / 12.0
        for child in _child_sequence(lords_stack[-1]):
            start_jd_val = _expand(start_jd_val, child_years, lords_stack + [child], level + 1, target_level, out_rows)
        return start_jd_val

    # ---- build rows (first cycle only, as in your current module)
    rows = []
    for md in md_progression:
        start_jd = _expand(start_jd, md_years, [md], level=1, target_level=lvl, out_rows=rows)

    return rows


def shoola_immediate_children(
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
    antardhasa_seed_option: int = 1,          # 1=lord; 2=stronger(S,7th); 3=lord(stronger)
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Śūla — return ONLY the immediate (parent -> children) splits:
      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]

    # tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # parent span
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

    # chart context
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)

    # antardasha seed resolution
    def _antara_seed(parent):
        if antardhasa_seed_option == 1:
            lord = house.house_owner_from_planet_positions(pp, parent)
            return int(p_to_h[lord]) % 12
        elif antardhasa_seed_option == 2:
            s = house.stronger_rasi_from_planet_positions(pp, parent, (parent + 6) % 12)
            return int(s) % 12
        elif antardhasa_seed_option == 3:
            s = house.stronger_rasi_from_planet_positions(pp, parent, (parent + 6) % 12)
            lord = house.house_owner_from_planet_positions(pp, s)
            return int(p_to_h[lord]) % 12
        else:
            raise ValueError("antardhasa_seed_option must be 1, 2, or 3")

    seed = _antara_seed(parent_sign)
    child_order = [(seed + i) % 12 for i in range(12)]

    # equal split at this level
    child_years = parent_years / 12.0
    incr_days = child_years * year_duration

    # tile
    rows, cursor = [], start_jd
    for i, c in enumerate(child_order):
        child_end = end_jd if i == 11 else cursor + incr_days
        if child_end > cursor:  # skip degenerate zero-span
            rows.append((path + (c,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)))
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
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    house_index: int = 1,
    antardhasa_seed_option: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Śūla — running ladder at `current_jd`:
      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        ...
        [(l1,..,l_d),        startd, endd]
      ]

    Zero-duration safe: 0-year Mahās (shouldn't occur for 7/8/9) are skipped defensively.
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

    # tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    def _is_zero(start_tuple, dur_years, eps_seconds=1e-3):
        if dur_years <= 0.0:
            return True
        return (dur_years * year_duration * 86400.0) <= eps_seconds

    def _to_selector_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
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

    # L1 Mahā via base (unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        house_index=house_index,
        antardhasa_seed_option=antardhasa_seed_option,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    # Build (lords, start) + sentinel; skip any 0-year
    periods = []
    jd_cursor = jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        dur = float(dur_years)
        if _is_zero(start_tuple, dur):
            continue
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd_to_tuple(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd_to_tuple(jd_cursor)))

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # Deeper levels via immediate-children (equal split; Antara seed option honored)
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running
        kids = shoola_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years, months=months, sixty_hours=sixty_hours,
            antardhasa_seed_option=antardhasa_seed_option,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_selector_periods(kids, parent_end_tuple=parent_end)
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
    _ant_option = 2

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Maha        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            antardhasa_seed_option=_ant_option,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            dob, tob, place,
            dhasa_level_index=DLI,
            antardhasa_seed_option=_ant_option,
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
    pvr_tests.shoola_dhasa_tests()
