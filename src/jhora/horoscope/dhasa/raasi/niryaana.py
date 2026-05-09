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
""" Called niryaana or niryaana Shoola Dhasa """
from jhora import const, utils
from jhora.horoscope.chart import house, charts
from jhora.panchanga import drik
from jhora.horoscope.dhasa.raasi.narayana import _narayana_antardhasa

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


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    return _niryaana_shoola_dhasa(
        planet_positions,
        dob,
        tob,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )


def __antardhasa(seed_rasi, p_to_h):
    direction = -1
    # Forward if AK (Saturn index '6' in your mapping?) is in seed, OR if seed is an odd sign
    if p_to_h[const.SATURN_ID] == seed_rasi or seed_rasi in const.odd_signs:
        direction = 1
    if p_to_h[const.KETU_ID] == seed_rasi:  # flip direction if Mangal (index '8' here) occupies seed
        direction *= -1
    return [(seed_rasi + direction * i) % 12 for i in range(12)]


def _antardhasa(planet_positions, dhasa_rasi):
    return _narayana_antardhasa(planet_positions, dhasa_rasi)


def _niryaana_shoola_dhasa(
    planet_positions,
    dob,
    tob,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Calculate niryaana Shoola Dasha up to the requested depth.

    Output (variable arity by level):
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)
    """
    def _append_row(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single row at the current depth with start time string and (optionally rounded) duration.
        Enforce lifespan cutoff AFTER appending (as per your rule).
        """
        disp_dur = round(seg_duration_years, dhasa_level_index + 1) if round_duration else seg_duration_years
        dhasa_info.append((tuple(lords_stack), utils.jd_to_gregorian(start_jd_val), disp_dur))

    def _expand_children(
        start_jd_val,
        parent_duration_years,
        parent_lords_stack,
        parent_seed_rasi,
        p_to_h,
        current_level,
        target_level
    ):
        """
        Recursive, level-by-level expansion:
          • For niryaana Shoola, each parent splits into 12 equal children.
          • Children order uses the same antara seed logic applied to the parent's seed.
          • We DO NOT round during progression; only in the returned rows.
          • Returns updated start_jd after expanding this branch.
        """
        if current_level == target_level:
            _append_row(parent_lords_stack, start_jd_val, parent_duration_years)
            return start_jd_val + parent_duration_years * year_duration

        child_duration = parent_duration_years / 12.0
        child_sequence = _antardhasa(planet_positions, parent_seed_rasi)

        for child_lord in child_sequence:
            new_lords_stack = parent_lords_stack + [child_lord]
            next_seed = child_lord
            start_jd_val = _expand_children(
                start_jd_val,
                child_duration,
                new_lords_stack,
                next_seed,
                p_to_h,
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ------------------------
    # Build chart basics
    # ------------------------
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    h_to_p = chart[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

    asc_house = p_to_h[const._ascendant_symbol]
    second_house = (asc_house + 2 - 1) % 12
    eighth_house = (asc_house + 8 - 1) % 12

    # Seed sign: stronger of 2H and 8H
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(
        planet_positions, second_house, eighth_house
    )

    # Direction (odd signs forward, even backward)
    direction = 1
    if dhasa_seed_sign in const.even_signs:
        direction = -1

    md_progression = [(dhasa_seed_sign + direction * k) % 12 for k in range(12)]

    # ------------------------
    # Generate rows
    # ------------------------
    dhasa_info = []
    start_jd = utils.julian_day_number(dob, tob)

    # We also replicate the original basis used in the old code's second cycle:
    # If level == 1: basis = MD years; else basis = MD years / 12
    first_cycle_basis_for_second = []

    # ---------- First cycle ----------
    for md_rasi in md_progression:
        # Maha duration: 7/8/9 years by sign modality
        if md_rasi in const.fixed_signs:
            md_years = 8
        elif md_rasi in const.dual_signs:
            md_years = 9
        else:
            md_years = 7  # movable

        # Record basis for second cycle (preserving original behavior)
        basis = md_years if dhasa_level_index == 1 else (md_years / 12.0)
        first_cycle_basis_for_second.append(basis)

        start_jd = _expand_children(
            start_jd,
            md_years,
            parent_lords_stack=[md_rasi],
            parent_seed_rasi=md_rasi,
            p_to_h=p_to_h,
            current_level=1,
            target_level=dhasa_level_index
        )

    # ---------- Second cycle ----------
    # Original code: if L1 → basis was MD years; else → basis was (MD years)/12.
    # So that MD2 = round(12 - basis, 2).
    for idx, md_rasi in enumerate(md_progression):
        md2_years = round(12 - first_cycle_basis_for_second[idx], 2)
        if md2_years <= 0:
            md2_years = 0.0

        start_jd = _expand_children(
            start_jd,
            md2_years,
            parent_lords_stack=[md_rasi],
            parent_seed_rasi=md_rasi,
            p_to_h=p_to_h,
            current_level=1,
            target_level=dhasa_level_index
        )

    return dhasa_info


def niryaana_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years  (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    # varga/epoch knobs (match your base)
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    FAST: niryaana Śūla Daśā — return ONLY the immediate (parent -> children) splits,
    computed directly (no base call).

    Output rows:
        [ [lords_tuple_{k+1}, start_tuple, end_tuple], ... ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_rasi = path[-1]

    # ---- tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- parent span in JD / years (use selected module-level year_duration)
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

    # ---- build p_to_h in the SAME varga/method the base would use
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)

    children_signs = _antardhasa(pp, parent_rasi)

    # ---- equal split & tiling
    child_years = parent_years / 12.0
    incr_days = child_years * year_duration

    children, cursor = [], start_jd
    for i, sgn in enumerate(children_signs):
        child_end = end_jd if i == 11 else cursor + incr_days
        if child_end > end_jd:
            child_end = end_jd
        if child_end > cursor:  # positive span only
            children.append([path + (sgn,), _jd_to_tuple(cursor), _jd_to_tuple(child_end)])
        cursor = child_end
        if cursor >= end_jd:
            break

    # exact closure
    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    chart_method=1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    niryaana Śūla Daśā — running ladder at current_jd:
      [
        [(r1,),              start1, end1],
        [(r1,r2),            start2, end2],
        ...
        [(r1,..,r_d),        startd, endd]
      ]
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    # ---- depth normalization
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo, hi = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY), int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # ---- helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _to_periods(children_rows, parent_end_tuple):
        # children_rows: [[lords_tuple, start_tuple, end_tuple], ...]
        if not children_rows:
            return []
        rows = sorted(children_rows, key=lambda r: _tuple_to_jd(r[1]))
        proj = []
        for lords, st, en in rows:
            if (not proj) or (_tuple_to_jd(st) > _tuple_to_jd(proj[-1][1])):
                proj.append((lords, st))
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel end
        return proj

    # ---- Step 1: running Mahā via base (depth=1, unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )

    # Build periods + sentinel for selector (use selected module-level year_duration)
    periods = []
    jd_cursor = jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in maha_rows:
        periods.append((tuple(lords_tuple), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + float(dur_years) * year_duration
    periods.append((periods[-1][0], utils.jd_to_gregorian(jd_cursor)))  # sentinel

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Step 2+: deeper levels via immediate-children on the running parent
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = niryaana_immediate_children(
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
            # represent “no deeper split” as zero-length at the boundary
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_periods(kids, parent_end)
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
    import time

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        ))
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            dob, tob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=2
        ))
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.niryaana_shoola_dhasa_tests()
