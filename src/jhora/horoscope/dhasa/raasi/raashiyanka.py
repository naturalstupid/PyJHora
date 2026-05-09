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
    Compute Rashiyanka/Rasyamsaka Dhasa - Ref: https://astrologicalmusings.com/method-of-calculating-rashiyanka-dasha/
"""
from jhora import const, utils
from jhora.horoscope.chart import charts, house
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


def applicability(pp_d1):
    # lagna lord in exaltion, own or friends house
    asc_d1 = pp_d1[0][1][0]
    lord_asc_d1 = house.house_owner_from_planet_positions(pp_d1, asc_d1)
    house_lord_asc_d1 = pp_d1[lord_asc_d1 + 1][1][0]
    return utils.is_planet_strong(lord_asc_d1, house_lord_asc_d1)


def _dhasa_progression(planet_positions, dhasa_progression_method=1, chart_method_d9=1):
    """
        Dhasa progression direct in both cases
        dhasa method = 1 BPHS Venkateshwar Edition (Translator: Pandit Tara Chand Shastri)
            starts from navamsa rasi of rasi lagna lord
        dhasa method = 2 BPHS - (Translator: Pandit Ganesh Dutt Pathak)
            starts from navamsa rasi of rasi lagna lord
    """
    asc_d1 = planet_positions[0][1][0]
    lord_asc = const._house_owners_list[asc_d1]  # force Parāśari lords
    pp_d9 = charts.navamsa_chart(planet_positions, chart_method=chart_method_d9)
    asc_d9 = pp_d9[0][1][0]
    lord_asc_d9 = pp_d9[lord_asc + 1][1][0]

    if dhasa_progression_method == 1:
        seed = lord_asc_d9  # Venkateśvara: D-9 of Lagna-lord
    else:
        # Pathak: stronger(Lagna, Lagna-lord) in D-1 → take that entity’s D-9 sign
        stronger_in_d1 = house.stronger_rasi_from_planet_positions(
            planet_positions, asc_d1, planet_positions[lord_asc + 1][1][0]
        )
        seed = asc_d9 if stronger_in_d1 == asc_d1 else lord_asc_d9

    return [(seed + h) % 12 for h in range(12)]


def _dhasa_duration_mandooka_kn_rao(planet_positions, sign):
    lord_of_sign = const._house_owners_list[sign]
    lord_sign = planet_positions[lord_of_sign + 1][1][0]
    # Overrides first (explicit & unambiguous)
    if lord_sign == sign:
        return 12
    if lord_sign == (sign + 6) % 12:
        return 10
    # Parity-based inclusive count (Mandūka)
    if sign in const.even_signs:
        dhasa_duration = (sign - lord_sign + 1) % 12   # backward inclusive
    else:
        dhasa_duration = (lord_sign - sign + 1) % 12   # forward inclusive
    return dhasa_duration or 12  # map “0” (full loop) to 12


def __dhasa_duration_mandooka_kn_rao(planet_positions, sign):
    """ Use standard lord in case dual lord signs """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = const._house_owners_list[sign]  # Use standard lord in case dual lord signs
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_signs:  # count back from sign to house_of_lord
        dhasa_period = (sign - house_of_lord + 1) % 12
    else:
        dhasa_period = (house_of_lord - sign + 1) % 12
    if house_of_lord == sign:
        dhasa_period = 12
    if house_of_lord == (sign + 6) % 12:
        dhasa_period = 10
    return dhasa_period


def _dhasa_duration_mandooka_sanjay_rath(lord):
    if lord in const.movable_signs:
        return 7
    elif lord in const.fixed_signs:
        return 8
    else:
        return 9


def _dhasa_duration_reference(planet_positions, sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    dhasa_period = 0
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_signs:  # count back from sign to house_of_lord
        dhasa_period = (sign - house_of_lord + 1) % 12
    else:
        dhasa_period = (house_of_lord - sign + 1) % 12
    if dhasa_period <= 0 or const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._OWNER_RULER:
        dhasa_period = 12
    if house_of_lord == (sign + 6) % 12:
        dhasa_period = 10
    return dhasa_period


def _dhasa_duration(planet_positions, dhasa_lord, dhasa_duration_method=1):
    """
        dhasa duration similar to mandooka dhasa which has 2 methods
        method=1 - KN Rao method
            The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi.
            depending on dasa rasi is even/odd footed. 10 years if lord in 7th house from sign
        method=2 - Sanjay Rath method
            movable = 7 years, Fixed=8 and dual = 9
        method=3 - Reference version
            counting indirect for even, direct for odd, 10 if lord in 7th house from sign
    """
    if dhasa_duration_method == 1:
        return _dhasa_duration_mandooka_kn_rao(planet_positions, dhasa_lord)
    if dhasa_duration_method == 2:
        return _dhasa_duration_mandooka_sanjay_rath(dhasa_lord)
    return _dhasa_duration_reference(planet_positions, dhasa_lord)


def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,              # 1..6 (1=Maha only, 2=Bhukti, 3..6 deeper)
    dhasa_progression_method=1,       # 1=BPHS (Tara Chand Shastri), 2=BPHS (Ganesh Dutt Pathak)
    dhasa_duration_method=1,          # 1=KN Rao (Mandooka-like rule), 2=Sanjay Rath, 3=Reference
    chart_method=1,                   # chart method for Dx
    chart_method_for_navamsa=1,       # used inside _dhasa_progression
    sublevel_split="equal",           # "equal" | "proportional"
    round_duration=True,              # only the returned duration (display) is rounded
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Rāśyāṁśaka / Rāśiyanka Daśā (depth-enabled, 1..6).

    RETURNS (canonical flat list), each row shaped as:
      ( (L1, ..., Lk), (y,m,d,float_hours), dur_years_float )

    Mechanics:
      • Progression order (seed & cycle of 12): _dhasa_progression(...)
      • Durations per sign: _dhasa_duration(planet_positions, sign, dhasa_duration_method)
      • L1 (Maha) uses raw years; L2..N sublevels:
          - "equal"        → split parent equally into 12
          - "proportional" → scale raw 12-sign durations to exactly fill the parent
      • All JD arithmetic uses module-level year_duration.
      • Only the returned 'dur_years' is optionally rounded (display).
    """
    # ── 0) Validate depth & set rounding precision ───────────────────────────
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")
    ndigits = lvl if round_duration else None

    # ── 1) Epoch & chart ─────────────────────────────────────────────────────
    jd_birth = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_birth, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_birth,
        place,
        divisional_chart_factor,
        chart_method,
        **kwargs
    )[:const._pp_count_upto_ketu]

    # ── 2) Progression cycle of 12 (seeded order) ────────────────────────────
    progression_order = _dhasa_progression(
        planet_positions,
        dhasa_progression_method=dhasa_progression_method,
        chart_method_d9=chart_method_for_navamsa
    )

    # ── Local helpers ────────────────────────────────────────────────────────
    def _rotate(order, start_sign):
        idx = order.index(start_sign)
        return order[idx:] + order[:idx]

    def _raw_years_for(sign):
        """Raw years for a single sign at the current duration method."""
        return float(_dhasa_duration(
            planet_positions, sign, dhasa_duration_method=dhasa_duration_method
        ))

    def _raw_years_list(signs):
        return [_raw_years_for(s) for s in signs]

    def _children_for(parent_sign):
        """Sub-order for a parent is rotation of the same 12-sign cycle, starting at the parent."""
        return _rotate(progression_order, parent_sign)

    def _emit_row(chain_signs, start_jd, dur_years):
        y, m, d, fh = utils.jd_to_gregorian(start_jd)
        dur_out = round(dur_years, ndigits) if ndigits is not None else dur_years
        rows.append((tuple(chain_signs), (int(y), int(m), int(d), float(fh)), float(dur_out)))

    rows = []

    # ── Recursive builder (for depth ≥ 2) ────────────────────────────────────
    def _recurse(level, parent_sign, parent_start_jd, parent_years, chain_prefix):
        """
        Build level=level periods under parent_sign, starting at parent_start_jd, filling parent_years.
        chain_prefix: tuple of signs from L1..(level-1).
        """
        child_signs = _children_for(parent_sign)

        if sublevel_split == "equal":
            child_years_list = [parent_years / 12.0] * 12
        else:
            raw = _raw_years_list(child_signs)
            s = sum(raw) or 1.0
            scale = parent_years / s
            child_years_list = [r * scale for r in raw]

        jd_cursor = parent_start_jd
        for child_sign, cyrs in zip(child_signs, child_years_list):
            if level < lvl:
                _recurse(
                    level + 1,
                    child_sign,
                    jd_cursor,
                    cyrs,
                    chain_prefix + (child_sign,)
                )
            else:
                _emit_row(chain_prefix + (child_sign,), jd_cursor, cyrs)
            jd_cursor += cyrs * year_duration

    # ── 3) L1 loop over the 12 Mahās (seed cycle) ───────────────────────────
    jd_cursor = jd_birth
    for maha_sign in progression_order:
        maha_years = _raw_years_for(maha_sign)

        if lvl == 1:
            _emit_row((maha_sign,), jd_cursor, maha_years)
            jd_cursor += maha_years * year_duration
            continue

        _recurse(
            level=2,
            parent_sign=maha_sign,
            parent_start_jd=jd_cursor,
            parent_years=maha_years,
            chain_prefix=(maha_sign,)
        )
        jd_cursor += maha_years * year_duration

    return rows


def raashiyanka_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    dhasa_progression_method: int = 1,
    dhasa_duration_method: int = 1,
    chart_method: int = 1,
    chart_method_for_navamsa: int = 1,
    sublevel_split: str = "equal",
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Rāśyāṁśaka — return ONLY the immediate (parent -> children) splits as:
      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]
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
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor,
        chart_method,
        **kwargs
    )[:const._pp_count_upto_ketu]

    def _rotate(order, start_sign):
        idx = order.index(start_sign)
        return order[idx:] + order[:idx]

    progression_order = _dhasa_progression(
        planet_positions,
        dhasa_progression_method=dhasa_progression_method,
        chart_method_d9=chart_method_for_navamsa
    )
    child_signs = _rotate(progression_order, parent_sign)

    if sublevel_split == "equal":
        child_years_list = [parent_years / 12.0] * 12
    else:
        def _raw_years_for(sign):
            return float(_dhasa_duration(
                planet_positions, sign, dhasa_duration_method=dhasa_duration_method
            ))
        raw = [_raw_years_for(s) for s in child_signs]
        total = sum(raw) or 1.0
        scale = parent_years / total
        child_years_list = [r * scale for r in raw]

    rows, cursor = [], start_jd
    for i, (sgn, yrs) in enumerate(zip(child_signs, child_years_list)):
        child_end = end_jd if i == 11 else cursor + yrs * year_duration
        if child_end > cursor:
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
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    dhasa_progression_method: int = 1,
    dhasa_duration_method: int = 1,
    chart_method: int = 1,
    chart_method_for_navamsa: int = 1,
    sublevel_split: str = "equal",
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Rāśyāṁśaka — running ladder at `current_jd`.
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

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    def _is_zero_by_start_dur(start_tuple, dur_years, eps_seconds=1e-3):
        if dur_years <= 0.0:
            return True
        return (dur_years * year_duration * 86400.0) <= eps_seconds

    def _to_selector_periods_zero_safe(children_rows, parent_end_tuple, eps_seconds=1.0):
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

    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    base_rows = get_dhasa_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        dhasa_progression_method=dhasa_progression_method,
        dhasa_duration_method=dhasa_duration_method,
        chart_method=chart_method,
        chart_method_for_navamsa=chart_method_for_navamsa,
        sublevel_split=sublevel_split,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    ) or []

    periods = []
    jd_cursor = jd_at_dob
    for row in base_rows:
        if (isinstance(row, (list, tuple)) and len(row) == 3
                and isinstance(row[0], (list, tuple)) and isinstance(row[1], (list, tuple))):
            lords_tuple, start_tuple, dur = row[0], row[1], float(row[2])
        else:
            start_tuple = row[0]
            dur = float(row[-1])
            lords_tuple = tuple(int(x) for x in row[1:-1])

        if _is_zero_by_start_dur(start_tuple, dur):
            continue
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd_to_tuple(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd_to_tuple(jd_cursor)))

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = raashiyanka_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            dhasa_progression_method=dhasa_progression_method,
            dhasa_duration_method=dhasa_duration_method,
            chart_method=chart_method,
            chart_method_for_navamsa=chart_method_for_navamsa,
            sublevel_split=sublevel_split,
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
        ad = get_dhasa_bhukthi(
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
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.03862, 80.261818, 5.5)
    rd = get_dhasa_bhukthi(dob, tob, place, dhasa_level_index=2)
    for row in rd:
        print(row)
