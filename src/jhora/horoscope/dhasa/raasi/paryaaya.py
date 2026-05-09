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

""" TODO: Paryaaya Dasa NOT IMPLEMENTED FULLY YET
    Dhasas are ok. Antardasa and periods are not matching JHora
    Try: https://sutramritam.blogspot.com/2010/03/chara-paryaya-dasa-introduction.html
"""

dhasa_adhipati_list = [0, 4, 6, 10, 0, 4, 6, 10, 0, 4, 6, 10]
antardhasa_list = [6, 0, 8, 10, 4, 8, 6, 0, 8, 10, 4, 8]
chara_paryaaya_list = [1, 5, 9, 2, 6, 10, 3, 7, 11, 4, 8, 12]
ubhaya_paryaaya_list = [1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12]
sthira_paryaaya_list = [1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12]

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


def applicability(planet_positions):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lagna = p_to_h[const._ascendant_symbol]
    trines = house.trines_of_the_raasi(lagna)
    # Jupiter in either of Trines
    jupiter_in_trines = p_to_h[const.JUPITER_ID] in trines
    if jupiter_in_trines:
        return True
    # Mercury in either of trines
    mercury_in_trines = p_to_h[const.MERCURY_ID] in trines
    if mercury_in_trines:
        return True
    # Placement of atma karaka in trines
    ak_in_trines = house.chara_karakas(planet_positions)[0] in trines
    if ak_in_trines:
        return True
    # Placement of own lord in trines
    own_lord_in_trines = any([p_to_h[const.house_owners[h]] == h in trines for _, (h, _) in planet_positions])
    return own_lord_in_trines


def _dhasa_duration_iranganti(planet_positions, dhasa_lord):
    ak_planet = house.chara_karakas(planet_positions)[0]
    ak_rasi = planet_positions[ak_planet + 1][1][0]
    target_houses = {ak_rasi}
    kendra_rasis = set(house.quadrants_of_the_raasi(ak_rasi))
    panapara_rasis = set(house.panapharas_of_the_raasi(ak_rasi))
    apoklima_rasis = set(house.apoklimas_of_the_raasi(ak_rasi))
    kpa_rasis = kendra_rasis | panapara_rasis | apoklima_rasis
    rasis_with_planets = set([r for p, (r, _) in planet_positions if r in kpa_rasis and p != const._ascendant_symbol])
    target_houses |= rasis_with_planets
    dirn = 1 if dhasa_lord in const.odd_signs else -1
    count = 1
    for h in range(12):
        if (dhasa_lord + dirn * h) % 12 in target_houses:
            return count
        count += 1
    return None


def _dhasa_duration_indiadivine(planet_positions, dhasa_lord):
    lord_owner = house.house_owner_from_planet_positions(planet_positions, dhasa_lord)
    house_of_lord = planet_positions[lord_owner + 1][1][0]
    dhasa_period = (house_of_lord + 13 - dhasa_lord) % 12
    if dhasa_lord in const.even_signs:
        dhasa_period = (dhasa_lord + 13 - house_of_lord) % 12
    return dhasa_period


def _dhasa_lords(planet_positions, dhasa_seed, chara_seed_method=1):
    if dhasa_seed in const.dual_signs:  # Dual and Chara Paryaaya
        dhasa_type = 1  # Chara
        if chara_seed_method == 1:  # Chara method = 1 - Iranganti / Raghava Bhatta - stronger of 1,5,9
            ts = house.trines_of_the_raasi(dhasa_seed)
            sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
            sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        else:  # chara method = 2 - Krishna Mishra - stronger of Lagna and 7th
            sr = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_seed, (dhasa_seed + const.HOUSE_7) % 12)
        dhasa_lords = [(sr + h - 1) % 12 for h in chara_paryaaya_list]
        if sr in const.even_footed_signs:
            dhasa_lords = [(sr - h + 13) % 12 for h in chara_paryaaya_list]
    elif dhasa_seed in const.movable_signs:  # Movable and Ubhaya Paryaaya
        dhasa_type = 2  # Ubhaya
        ts = house.quadrants_of_the_raasi(dhasa_seed)
        sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[3])
        dhasa_lords = [(sr + h - 1) % 12 for h in ubhaya_paryaaya_list]
        if sr in const.even_footed_signs:  # Fixed and Sthira Paryaaya
            dhasa_lords = [(sr - h + 13) % 12 for h in ubhaya_paryaaya_list]
    else:  # Fixed = Sthira Paryaaya
        dhasa_type = 3  # Sthira
        sr = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_seed, (dhasa_seed + 6) % 12)
        dhasa_lords = [(sr + h - 1) % 12 for h in sthira_paryaaya_list]
        if sr in const.even_footed_signs:
            dhasa_lords = [(sr - h + 13) % 12 for h in sthira_paryaaya_list]
    return dhasa_type, dhasa_lords


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=6,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=2,             # 1..6; default L2 (Maha + Antara)
    use_tribhagi_variation=False,
    round_duration=False,
    chara_seed_method=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Paryāya Daśā (base) — depth-enabled (Mahā → Antara → …)

    Returns:
      (dhasa_type, rows)
        dhasa_type: 1=Chara, 2=Ubhaya, 3=Sthira
        rows: [(lords_tuple, start_tuple, dur_years_display), ...]

    Policy:
      • NO lifespan/total-duration cutoff.
      • Rounding ONLY on returned 'dur_years' (not used in JD math).
      • Children = equal split (/12) with full-precision JD arithmetic (exact tiling).
    """
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")

    # Tribhāgī
    cycles = 2
    scale = 1.0
    if use_tribhagi_variation:
        scale = 1.0 / 3.0
        cycles = int(cycles / scale)  # e.g., 6 cycles

    # Epoch & varga
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    # Seed (your original logic)
    asc_house = pp[0][1][0]
    dhasa_seed = (asc_house + divisional_chart_factor - 1) % 12

    # Mahā order
    dhasa_type, md_lords = _dhasa_lords(pp, dhasa_seed, chara_seed_method=chara_seed_method)

    rows = []
    start_jd = jd_at_dob

    def _append_row(labels, start_jd_val, seg_years):
        """Append row with display rounding only; JD math stays exact."""
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))

    def _recurse(level, parent_lord, pstart_jd, parent_years, prefix):
        """
        Expand one level at a time:
          • If level+1 == target: emit 12 child rows (final expansion).
          • Else: recurse into each child.
        """
        _, child_seq = _dhasa_lords(pp, parent_lord, chara_seed_method=chara_seed_method)
        child_years = parent_years / 12.0
        jd_ptr = pstart_jd

        if level + 1 == lvl:
            # Final expansion: emit 12 child rows
            for c in child_seq:
                _append_row(prefix + (c,), jd_ptr, child_years)
                jd_ptr += child_years * year_duration
            return jd_ptr

        # Go deeper
        for c in child_seq:
            jd_ptr = _recurse(level + 1, c, jd_ptr, child_years, prefix + (c,))
        return jd_ptr

    # Build across cycles
    for _ in range(cycles):
        for md in md_lords:
            md_years = float(_dhasa_duration_indiadivine(pp, md)) * scale
            if lvl == 1:
                _append_row((md,), start_jd, md_years)
                start_jd += md_years * year_duration
            else:
                # Start recursion at Mahā level = 1 (so depth math is consistent)
                start_jd = _recurse(1, md, start_jd, md_years, (md,))

    return dhasa_type, rows


def paryaaya_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years  (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 6,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    use_tribhagi_variation: bool = False,      # parent_years already encodes this in practice
    chara_seed_method: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Paryāya — return ONLY the immediate (parent -> children) splits.
    Children order comes from _dhasa_lords(<target varga>, parent_lord)[1].
    Children durations = parent_years / 12. Exact tiling on [parent_start, parent_end).
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # normalize path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_lord = path[-1]

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

    # ⛔ zero-length parent → no children
    if end_jd <= start_jd:
        return []

    # build target varga (same as base)
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    # order & equal split
    _, child_seq = _dhasa_lords(pp, parent_lord, chara_seed_method=chara_seed_method)
    child_years = parent_years / 12.0
    incr_days = child_years * year_duration

    # tile children
    children, cursor = [], start_jd
    for i, c in enumerate(child_seq):
        child_end = end_jd if i == 11 else cursor + incr_days
        if child_end > end_jd:
            child_end = end_jd
        if child_end > cursor:  # skip any degenerate zero spans
            children.append((path + (c,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)))
        cursor = child_end
        if cursor >= end_jd:
            break

    # close exactly on the parent end
    if children:
        children[-1] = (children[-1][0], children[-1][1], _jd_to_tuple(end_jd))
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 6,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    use_tribhagi_variation: bool = False,
    chara_seed_method: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Paryāya — running ladder at `current_jd`:
      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        ...
        [(l1,..,l_d),        startd, endd]
      ]

    Zero-duration-safe:
      • Mahā ladder is taken from the base (L1) and any zero-length Mahā is skipped
        when building the period list for selection.
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

    def _to_periods(children_rows, parent_end_tuple):
        """children_rows → [(lords, start), ..., sentinel(parent_end)] with strictly increasing starts."""
        if not children_rows:
            return []
        rows = sorted(children_rows, key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, en in rows:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    # derive dob/tob once
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    # ---- L1 Mahā via base (unrounded) ----
    _, maha_rows = get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        use_tribhagi_variation=use_tribhagi_variation,
        round_duration=False,
        chara_seed_method=chara_seed_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
    if not maha_rows:
        return []

    # Build Mahā periods + sentinel using exact JD math
    periods = []
    jd_cursor = jd_at_dob

    # ⛔ Skip zero-duration Mahās to keep starts strictly increasing
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        dur = float(dur_years)
        if dur <= 0.0:
            continue
        lords = tuple(lords_tuple) if isinstance(lords_tuple, (tuple, list)) else (lords_tuple,)
        periods.append((lords, start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + dur * year_duration

    # If all Mahās were zero (extremely rare), fall back to a single-point sentinel
    if not periods:
        sentinel = utils.jd_to_gregorian(jd_at_dob)
        return [[(), sentinel, sentinel]]

    # Sentinel end: after last *positive* Mahā
    periods.append((periods[-1][0], utils.jd_to_gregorian(jd_cursor)))

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Deeper levels via fast immediate-children ----
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = paryaaya_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years, months=months, sixty_hours=sixty_hours,
            use_tribhagi_variation=use_tribhagi_variation,
            chara_seed_method=chara_seed_method,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )
        if not kids:
            # zero-length (or no deeper split) → represent boundary
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_periods(kids, parent_end_tuple=parent_end)
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
    _dhasa_cycle_count = 2
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
        _, ad = get_dhasa_antardhasa(
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
    pvr_tests.paryaaya_dhasa_test()
