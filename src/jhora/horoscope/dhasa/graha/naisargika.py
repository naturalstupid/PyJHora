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

year_duration = const.sidereal_year

_bhukthi_house_list = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]
_bhukthi_exempt_list_1 = [2, 9]
_bhukthi_exempt_list_2 = [1, 5, 10, 11]
dhasa_adhipathi_dict = {1: 1, 2: 2, 3: 9, 5: 20, 4: 18, 0: 20, 6: 50, 'L': 12}


def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1, chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    mahadhasa_lord_has_no_antardhasa=True,
    antardhasa_option1=False, antardhasa_option2=False,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
        provides Naisargika dhasa bhukthi for a given date in julian day (includes birth time)
        @param antardhasa_option1 = True 3rd/10th house has no antardhasa
        @param antardhasa_option2 = True 2/6/11/12 house has no antardhasa
        @return:
          if dhasa_level_index == 1:
            [ (dhasa_lord, start_str, duration_years), ... ]
          else:
            [ (l1, l2, ..., start_str, leaf_duration_years), ... ]  # equal-split of immediate parent
    """
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # Build base chart once
    start_jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=start_jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        start_jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_saturn]  # Ignore Rahu onwards

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    dhasa_lords = list(dhasa_adhipathi_dict.keys())  # preserve existing order

    # --- Build bhukthi house list (with requested exclusions) ---
    bhukthi_house_list = list(_bhukthi_house_list)
    if antardhasa_option1:
        bhukthi_house_list = [p for p in bhukthi_house_list if p not in _bhukthi_exempt_list_1]
    if antardhasa_option2:
        bhukthi_house_list = [p for p in bhukthi_house_list if p not in _bhukthi_exempt_list_2]

    def _bhukthis_for(parent_lord):
        """
        SAME antara selection as your original code, applied to `parent_lord`.
        - Houses are picked relative to `parent_lord`'s sign
        - Flattens h_to_p lists, removes 'L','7','8'
        - Optionally removes parent lord itself (if flag is set and not Lagna)
        Returns: list[int] of child lords in order
        """
        lord_house = planet_positions[parent_lord + 1][1][0] if parent_lord != const._ascendant_symbol \
                     else planet_positions[0][1][0]
        # Collect planet labels from targeted houses
        raw_lists = [h_to_p[(h + lord_house) % 12] for h in bhukthi_house_list]
        raw_lists = [s for s in raw_lists if s != '']
        bhukthis = utils.flatten_list([s.split('/') for s in raw_lists])

        # Remove these labels if present (mirror original)
        for p in ['L', '7', '8']:
            if p in bhukthis:
                bhukthis.remove(p)

        # “Maha lord has no antara” option
        if mahadhasa_lord_has_no_antardhasa and parent_lord != const._ascendant_symbol:
            if str(parent_lord) in bhukthis:
                bhukthis.remove(str(parent_lord))

        return list(map(int, bhukthis))

    retval = []

    # --- Recursive expansion: equal split of the immediate parent at every level ---
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        children = _bhukthis_for(parent_lord)
        if not children:
            return

        n = len(children)
        child_dur_unrounded = parent_duration_years / n  # equal split (as in your Antara today)
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            # Go deeper (each child becomes parent for next level)
            for blord in children:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            # Leaf rows: round ONLY the returned duration; advance with full precision
            for blord in children:
                start_str = utils.jd_to_gregorian(jd_cursor)
                durn = round(child_dur_unrounded, dhasa_level_index + 1) if round_duration else child_dur_unrounded
                retval.append((prefix + (blord,), start_str, durn))
                jd_cursor += child_dur_unrounded * year_duration

    # --- Top-level (Maha) progression using your dhasa_adhipathi_dict ---
    for dhasa_lord in dhasa_lords:
        maha_dur_unrounded = dhasa_adhipathi_dict[dhasa_lord]  # full precision internally

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
                prefix=(dhasa_lord,)
            )
            start_jd += maha_dur_unrounded * year_duration

    return retval


def naisargika_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (optional)
    parent_end=None,             # (Y, M, D, fractional_hour) (optional)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    # Naisargika options (match your base):
    mahadhasa_lord_has_no_antardhasa: bool = True,
    antardhasa_option1: bool = False,      # True => 3rd/10th houses have no antara
    antardhasa_option2: bool = False,      # True => 2/6/11/12 houses have no antara
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Naisargika — return ONLY the immediate (p -> p+1) children under the given parent span.

    Matches your base get_dhasa_bhukthi:
      • Antara selection by targeted houses (relative to parent lord’s sign), with optional exclusions:
            - antardhasa_option1: drop 3rd/10th
            - antardhasa_option2: drop 2/6/11/12
            - mahadhasa_lord_has_no_antardhasa: drop parent itself (if not Lagna)
      • Flatten house bins; drop 'L','7','8'; map labels to planet ints
      • Equal split at this level (sum(children) = parent)
      • Tile exactly inside [parent_start, parent_end)
    Returns:
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
        return []

    # ---- chart & house bins (exactly like your base)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_saturn]

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)

    # Build bhukthi_house_list with exclusions
    bhukthi_house_list = list(_bhukthi_house_list)
    if antardhasa_option1:
        bhukthi_house_list = [h for h in bhukthi_house_list if h not in _bhukthi_exempt_list_1]
    if antardhasa_option2:
        bhukthi_house_list = [h for h in bhukthi_house_list if h not in _bhukthi_exempt_list_2]

    # Parent's sign (house index)
    lord_house = (planet_positions[parent_lord + 1][1][0]
                  if parent_lord != const._ascendant_symbol else planet_positions[0][1][0])

    # Collect planet labels from targeted houses (relative to parent lord)
    raw_lists = [h_to_p[(h + lord_house) % 12] for h in bhukthi_house_list]
    raw_lists = [s for s in raw_lists if s != '']
    labels = utils.flatten_list([s.split('/') for s in raw_lists])

    # Remove unwanted labels
    for p in ['L', '7', '8']:
        if p in labels:
            labels.remove(p)

    # Drop Maha lord from antara if requested (and not Lagna)
    if mahadhasa_lord_has_no_antardhasa and parent_lord != const._ascendant_symbol:
        sp = str(parent_lord)
        if sp in labels:
            labels.remove(sp)

    # Final child list (planet ints). # of children may be < full set → OK.
    try:
        children = list(map(int, labels))
    except Exception as e:
        raise ValueError(f"Non-integer labels in antara selection: {labels}") from e

    if not children:
        return []

    # ---- Equal split at this level
    n = len(children)
    child_years = parent_years / n

    # ---- Tile children inside parent [start, end)
    out = []
    cursor = start_jd
    for i, blord in enumerate(children):
        if i == n - 1:
            child_end = end_jd
        else:
            child_end = cursor + child_years * year_duration

        out.append([
            path + (blord,),
            _jd_to_tuple(cursor),
            _jd_to_tuple(child_end),
        ])
        cursor = child_end
        if cursor >= end_jd:
            break

    if out:
        out[-1][2] = _jd_to_tuple(end_jd)

    return out


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
    # Naisargika options (forwarded to base + children):
    mahadhasa_lord_has_no_antardhasa: bool = True,
    antardhasa_option1: bool = False,
    antardhasa_option2: bool = False,
    round_duration: bool = False,      # runner uses exact start/end; rounding not needed here
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """
    Naisargika — narrow Mahā -> … -> target depth and return the full running ladder:

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

    # ---- depth normalization
    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    # ---- tuple -> JD & zero-length filtering
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ [lords_tuple, start_tuple, end_tuple], ... ]
        Returns: list of (lords_tuple, start_tuple) + sentinel (… , parent_end_tuple),
        filtering zero-length rows and enforcing strictly increasing starts.
        """
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds)]
        if not filtered:
            return []
        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _en in filtered:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st)); prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))  # sentinel
        return proj

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, (int, str)) else tuple(x)

    running_all = []

    # ---- Level 1: Mahā via your base function
    # Derive dob/tob for the base Naisargika generator
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    maha_rows = get_dhasa_bhukthi(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        mahadhasa_lord_has_no_antardhasa=mahadhasa_lord_has_no_antardhasa,
        antardhasa_option1=antardhasa_option1,
        antardhasa_option2=antardhasa_option2,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # Normalize for utils: (lords_tuple, start_tuple)
    maha_for_utils = [(_as_tuple_lords(row[0]), row[1]) for row in maha_rows]

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_as_tuple_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    # ---- Levels 2..target
    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = naisargika_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            years=years, months=months, sixty_hours=sixty_hours,
            mahadhasa_lord_has_no_antardhasa=mahadhasa_lord_has_no_antardhasa,
            antardhasa_option1=antardhasa_option1,
            antardhasa_option2=antardhasa_option2,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs
        )

        if not children:
            # No children produced under options → freeze at this depth
            running_all.append([parent_lords + (parent_lords[-1],), parent_end, parent_end])
            break

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            running = [_as_tuple_lords(rdk[0]), rdk[1], rdk[2]]

        running_all.append(running)

    return running_all


if __name__ == "__main__":
    utils.set_language('en')

    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)

    jd_at_dob = utils.julian_day_number(dob, tob)

    from datetime import datetime
    import time

    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600

    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))

    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

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
                dhasa_level_index=6,
                dhasa_duration_type=dd,
            )
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
                extract_running_period_for_all_levels=True
            )
        )

        print('old method elapsed time', time.time() - start_time)

    exit()

    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.naisargika_test()
