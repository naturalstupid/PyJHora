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
from collections import OrderedDict as Dict
from jhora import const, utils
from jhora.panchanga import drik


_dhasa_duration = 10
_dhasa_count = 10
year_duration = const.sidereal_year
human_life_span_for_dhasa = 100

dhasa_adhipathi_list = lambda lord: {(lord - i) % 27: _dhasa_duration for i in range(_dhasa_count)}


def _next_adhipati(lord, dhasa_lords, dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = dhasa_lords.index(lord)
    next_lord = dhasa_lords[(current + dirn) % len(dhasa_lords)]
    return next_lord


def _antardhasa(dhasa_lord, antardhasa_option=1):
    dhasa_lords = [(dhasa_lord - i) % 27 for i in range(_dhasa_count)]
    lord = dhasa_lord
    if antardhasa_option in [3, 4]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords, dirn=1)
    elif antardhasa_option in [5, 6]:
        lord = _next_adhipati(dhasa_lord, dhasa_lords, dirn=-1)
    dirn = 1 if antardhasa_option in [1, 3, 5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_lords)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord, dhasa_lords, dirn)
    return _bhukthis


def _dhasa_progression(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
):
    y, m, d, fh = utils.jd_to_gregorian(jd)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)
    one_star = 360 / 27.0  # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts, sphuta

    _special_planets = ['M', 'G', 'T', 'I', 'B', 'I', 'P']
    planet_positions = charts.divisional_chart(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )[:const._pp_count_upto_ketu]

    if dhasa_starting_planet in const.SUN_TO_KETU:
        planet_long = planet_positions[dhasa_starting_planet + 1][1][0] * 30 + planet_positions[dhasa_starting_planet + 1][1][1]
    elif dhasa_starting_planet == const._ascendant_symbol:
        planet_long = planet_positions[0][1][0] * 30 + planet_positions[0][1][1]
    elif dhasa_starting_planet.upper() == 'M':
        mn = drik.maandi_longitude(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0] * 30 + mn[1]
    elif dhasa_starting_planet.upper() == 'G':
        gl = drik.gulika_longitude(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0] * 30 + gl[1]
    elif dhasa_starting_planet.upper() == 'B':
        gl = drik.bhrigu_bindhu_lagna(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
        )
        planet_long = gl[0] * 30 + gl[1]
    elif dhasa_starting_planet.upper() == 'I':
        gl = drik.indu_lagna(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
        )
        planet_long = gl[0] * 30 + gl[1]
    elif dhasa_starting_planet.upper() == 'P':
        gl = drik.pranapada_lagna(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
        )
        planet_long = gl[0] * 30 + gl[1]
    elif dhasa_starting_planet.upper() == 'T':
        sp = sphuta.tri_sphuta(
            dob,
            tob,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
        )
        planet_long = sp[0] * 30 + sp[1]
    else:
        planet_long = planet_positions[2][1][0] * 30 + planet_positions[2][1][1]

    if dhasa_starting_planet == 1:
        planet_long += (star_position_from_moon - 1) * one_star

    nak = int(planet_long / one_star)
    _dp = [(nak - i) % 27 for i in range(_dhasa_count)]
    return _dp


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
        returns a list of dasha segments at the selected depth level

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1
        @param chart_method: Default=1
        @param star_position_from_moon: 1=Moon(default), 4=Kshema, 5=Utpanna, 8=Adhana
        @param use_tribhagi_variation: False (default), True => durations scaled to 1/3 with 3 cycles
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna, M/G/T/B/I/P as supported
        @param antardhasa_option: ordering rule passed to _antardhasa(...)
        @param dhasa_level_index: Depth 1..6 (1=Maha only, 2=+Antara, 3=+Pratyantara, 4=+Sookshma, 5=+Prana, 6=+Deha)
        @param round_duration: If True, round only the returned duration values to dhasa_level_index

        @return:
            if dhasa_level_index == 1:
                [ (l1, start_str, dur_years), ... ]
            else:
                [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
            (tuple grows by one lord per requested level)
    """
    global human_life_span_for_dhasa, year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # --- original cycles/tribhagi behavior preserved ---
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1.0 / 3.0
        _dhasa_cycles = int(_dhasa_cycles / _tribhagi_factor)
        human_life_span_for_dhasa *= _tribhagi_factor  # preserves original behavior

    jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # Original progression (unchanged)
    dhasa_progression = _dhasa_progression(
        jd,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )

    # Existing antara ordering reused at every depth
    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option))

    retval = []
    start_jd = jd

    # Nested expansion: equal split of the IMMEDIATE PARENT (sum(children) = parent)
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        children = _children_of(parent_lord)
        if not children:
            return

        n = len(children)
        if n <= 0:
            return

        child_dur_unrounded = parent_duration_years / n  # equal split (same as your Antara branch)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # go deeper
            for blord in children:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            # leaf: round ONLY returned value; keep full precision for time accumulation
            for blord in children:
                start_str = utils.jd_to_gregorian(jd_cursor)
                durn = round(child_dur_unrounded, dhasa_level_index + 1) if round_duration else child_dur_unrounded
                retval.append((prefix + (blord,), start_str, durn))
                jd_cursor += child_dur_unrounded * year_duration

    # Main loop (original order & cycles preserved)
    for _ in range(_dhasa_cycles):
        for dhasa_lord in dhasa_progression:
            # Original maha duration logic preserved: _dhasa_duration is your module's base unit
            maha_dur_unrounded = _dhasa_duration * _tribhagi_factor

            if dhasa_level_index == 1:
                start_str = utils.jd_to_gregorian(start_jd)
                durn = round(maha_dur_unrounded, dhasa_level_index + 1) if round_duration else maha_dur_unrounded
                retval.append(((dhasa_lord,), start_str, durn))
                start_jd += maha_dur_unrounded * year_duration
            else:
                _recurse(
                    level=2,
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_duration_years=maha_dur_unrounded,
                    prefix=(dhasa_lord,),
                )
                start_jd += maha_dur_unrounded * year_duration

    return retval


def saptharishi_nakshathra_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (optional)
    parent_end=None,             # (Y, M, D, fractional_hour) (optional)
    *,
    jd_at_dob,
    place,
    # REQUIRED knob for this dasha (explicit):
    antardhasa_option: int = 1,
    # Accepted but unused here (kept for API parity / future variants):
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_starting_planet=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Saptharishi Nakshathra (Sama) — return ONLY the immediate (p -> p+1) children
    for the given parent span.

    Rules (match your base get_dhasa_bhukthi):
      • Child order at every level via your antara rule: _antardhasa(parent_lord, antardhasa_option)
      • Equal split at this level: child_years = parent_years / n
      • Last child end forced to parent_end (exact tiling)

    Output rows:
      [ (lords_tuple_with_child), child_start_tuple, child_end_tuple ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- normalize lords path
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")
    parent_lord = path[-1]

    # ---- canonical tuple <-> JD
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- resolve parent span
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []  # instantaneous parent -> nothing to tile

    # ---- child sequence via your antara rule (order/direction)
    def _children_of(pl):
        return list(_antardhasa(pl, antardhasa_option))

    child_lords = _children_of(parent_lord)
    if not child_lords:
        return []

    # ---- equal split at this level
    n = len(child_lords)
    child_years = parent_years / n

    # ---- tile children within parent [start, end)
    children = []
    cursor = start_jd
    for i, cl in enumerate(child_lords):
        if i == n - 1:
            child_end = end_jd
        else:
            child_end = cursor + child_years * year_duration

        children.append([
            path + (cl,),
            _jd_to_tuple(cursor),
            _jd_to_tuple(child_end),
        ])
        cursor = child_end
        if cursor >= end_jd:
            break

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)  # closure

    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    # REQUIRED knob for this dasha:
    antardhasa_option: int = 1,
    # Forwarded to base Saptharishi Nakshathra get_dhasa_bhukthi:
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    star_position_from_moon: int = 1,
    use_tribhagi_variation: bool = False,
    dhasa_starting_planet: int = 1,
    round_duration: bool = False,     # runner uses exact start/end
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Saptharishi Nakshathra — narrow Mahā -> … -> target depth and return the full running ladder:

      [
        [(l1,),              start1, end1],
        [(l1,l2),            start2, end2],
        [(l1,l2,l3),         start3, end3],
        [(l1,l2,l3,l4),      start4, end4],
        [(l1,l2,l3,l4,l5),   start5, end5],
        [(l1,l2,l3,l4,l5,l6),start6, end6],
      ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- depth normalization (Enum-friendly)
    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    # ---- tuple -> JD & zero-length helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ [lords_tuple, start_tuple, end_tuple], ... ]
        Returns: list of (lords_tuple, start_tuple) + sentinel (any_lords, parent_end_tuple),
        filtering zero-length rows and enforcing strictly increasing starts.
        """
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds=eps_seconds)]
        if not filtered:
            return []
        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _en in filtered:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel
        return proj

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    # ---- derive dob/tob for base
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    running_all = []

    # ---- Level 1: Mahā via your base function
    maha_rows = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        dhasa_starting_planet=dhasa_starting_planet,
        antardhasa_option=antardhasa_option,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    # normalize for utils: (lords_tuple, start_tuple)
    maha_for_utils = []
    for row in maha_rows:
        # row: ((lord,), start_tuple, duration_years)
        lords_any, start_t = row[0], row[1]
        maha_for_utils.append((_as_tuple_lords(lords_any), start_t))

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    lords1 = _as_tuple_lords(rd1[0])
    running = [lords1, rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    # ---- Levels 2..target (expand only the running parent each step)
    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        # Equal split + antara order at this level
        children = saptharishi_nakshathra_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            antardhasa_option=antardhasa_option,
            star_position_from_moon=star_position_from_moon,
            use_tribhagi_variation=use_tribhagi_variation,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            dhasa_starting_planet=dhasa_starting_planet,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )

        if not children:
            # represent as zero-length at parent_end
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            continue

        # utils selection with sentinel
        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            lords_k = _as_tuple_lords(rdk[0])
            running = [lords_k, rdk[1], rdk[2]]

        running_all.append(running)

    return running_all


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
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        print(
            "Dehā        :",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd,
        )
        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
            )
        )
        print('old method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.saptharishi_nakshathra_test()
