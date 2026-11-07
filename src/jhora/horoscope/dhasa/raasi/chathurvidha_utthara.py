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
    Chaturvidha Uttara Dasha
        Lagna Uttara Dasha  -> Start from Lagna (Ascendant Rashi) - Dhasa Method = 1
        Kendra Uttara Dasha -> Start from strongest Kendra (1st, 4th, 7th, 10th house Rashi) - Dhasa Method = 2
        Trikona Uttara Dasha -> Start from strongest Trikona (1st, 5th, 9th house Rashi) - Dhasa Method = 3
        Dasha Uttara Dasha -> Start from Rashi with the strongest planetary influence - Dhasa Method = 4

    Mahadasa duration: each Rashi's period is weighted by its house-distance
    (1..12) from the starting sign, out of a total of 78 (sum of 1..12).

    Antardasha: not specified in the source. As with other conditional rasi
    dashas in this project, the same seed/order/weighted-split rule used for
    the Mahadasa is applied recursively at every deeper level.

    Ref: https://astrosutras.in/index.php/2025/03/05/chaturvidha-uttara-dasha-as-per-brihat-parashara-hora-shastra-bphs/

    Release History:
        V5.0 - Refactored.
"""

from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year

# Sum of weights 1..12 - denominator for the proportional split at every level.
_SUM_WEIGHTS = 78.0

# Total Mahadasa-level span in years (== _SUM_WEIGHTS, so each sign's own
# weighted share reduces to duration_years == weight).
_TOTAL_LIFESPAN_YEARS = 78.0

# Sanity backstop (days) against drik._get_dhasa_end_jd() drift for small durations.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# Below this duration (days), switch to proportional interpolation instead of
# calling drik._get_dhasa_end_jd() per child, to avoid sub-day unreliability.
_SUB_DAY_DURATION_DAYS = 1.0


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, with a
    fallback to naive average-year arithmetic if drik._get_dhasa_end_jd()
    drifts beyond _SMALL_DURATION_BACKSTOP_DAYS from the expected value.
    """
    end_jd = drik._get_dhasa_end_jd(
        start_jd=start_jd_local,
        place=place,
        total_dasa_years=duration_years,
    )

    expected_jd = start_jd_local + duration_years * year_duration
    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd

    return end_jd


def valid_methods_available_for_planet_positions(planet_positions):
    """
    Returns the unique dhasa_method numbers whose seed sign differs, since
    two or more of the four methods can resolve to the same seed for a
    given chart.
    """
    asc_house = planet_positions[0][1][0]
    _seeds = {}
    _seeds[1] = asc_house
    raasi_list = house.quadrants_of_the_raasi(asc_house)
    _seeds[2] = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    raasi_list = house.trines_of_the_raasi(asc_house)
    _seeds[3] = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    raasi_list = [(asc_house + h) % 12 for h in range(12)]
    _seeds[4] = house.stronger_raasi_from_list_of_raasis(planet_positions, raasi_list)
    unique_methods = list(set({v: k for k, v in _seeds.items()}.values()))
    return unique_methods


def _seed_for_method(planet_positions, asc_house, dhasa_method):
    """
    Determines the seed sign for the chosen Chaturvidha Uttara Dasha method:
        CHATHURVIDHA_METHOD.LAGNA_UTTHARA   = Lagna itself
        CHATHURVIDHA_METHOD.KENDRA_UTTHARA  = stronger of the 4 Kendra signs from Lagna
        CHATHURVIDHA_METHOD.TRIKONA_UTTHARA = stronger of the 3 Trikona signs from Lagna
        CHATHURVIDHA_METHOD.DHASA_UTTHARA   = stronger of all 12 signs from Lagna
    """
    if dhasa_method == const.CHATHURVIDHA_METHOD.LAGNA_UTTHARA:
        return asc_house
    elif dhasa_method == const.CHATHURVIDHA_METHOD.KENDRA_UTTHARA:
        return house.stronger_raasi_from_list_of_raasis(
            planet_positions, house.quadrants_of_the_raasi(asc_house)
        )
    elif dhasa_method == const.CHATHURVIDHA_METHOD.TRIKONA_UTTHARA:
        return house.stronger_raasi_from_list_of_raasis(
            planet_positions, house.trines_of_the_raasi(asc_house)
        )
    elif dhasa_method == const.CHATHURVIDHA_METHOD.DHASA_UTTHARA:
        return house.stronger_raasi_from_list_of_raasis(
            planet_positions, [(asc_house + h) % 12 for h in range(12)]
        )
    else:
        raise ValueError(f"Unknown dhasa_method: {dhasa_method}")


def _get_chathurvidha_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    *,
    parent_end_jd=None,
):
    """
    Splits a parent sign's span into its 12 child signs (parent, parent+1,
    ..., wrap), weighted 1..12 by house-distance out of _SUM_WEIGHTS.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD
    """
    parent_sign = parent_path[-1]

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    progression = [(parent_sign + h) % 12 for h in range(12)]
    weights = [i + 1 for i in range(len(progression))]
    n = len(progression)

    child_durations = [parent_duration * (w / _SUM_WEIGHTS) for w in weights]

    smallest_child_years = min(child_durations)
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(child_durations)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, child_sign in enumerate(progression):
        child_duration = child_durations[i]
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_duration += child_duration
            child_end_jd = parent_start_jd + parent_span * cumulative_duration / total_child_duration
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                parent_path + (child_sign,),
                child_start_jd,
                child_duration,
                child_end_jd,
            )
        )

        cursor = child_end_jd

    return children, parent_end_jd


def _get_mahadasa_periods(jd_at_dob, place, seed):
    """
    Returns:
        list of (md_sign, md_start_jd, md_duration_years, md_end_jd)
    """
    raw_children, _ = _get_chathurvidha_children_jd(
        (seed,),
        jd_at_dob,
        _TOTAL_LIFESPAN_YEARS,
        place,
    )

    return [
        (child_path[-1], child_start_jd, child_duration, child_end_jd)
        for child_path, child_start_jd, child_duration, child_end_jd in raw_children
    ]


def _find_child_containing_jd(children, target_jd):
    """
    Returns the single child tuple whose [start_jd, end_jd) contains
    target_jd. Falls back to the last child if target_jd is at/past the
    final boundary.
    """
    if not children:
        return None

    for child in children:
        _, s, _, e = child

        if s <= target_jd < e:
            return child

    return children[-1]


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_method=None,
    chart_method=1,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
    **kwargs,
):
    """
    Returns a flat list of the lowest-level entries:
      [ [raasi_path], (y, m, d, fh), duration_years ], ...
    where raasi_path contains raasi indices (0..11) per level.

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    """
    global year_duration

    if dhasa_method is None:
        dhasa_method = const.chathurvidha_utthara_dhasa_default

    def _sanitize_depth(depth):
        try:
            d = int(depth)
        except Exception:
            d = 2
        return max(1, min(6, d))

    jd_at_dob = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs,
    )

    asc_house = planet_positions[0][1][0]
    seed = _seed_for_method(planet_positions, asc_house, dhasa_method)

    depth = _sanitize_depth(dhasa_level_index)

    rows = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            rows.append(
                (
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                )
            )
        else:
            y, m, d, fh = utils.jd_to_gregorian(start_jd_local)
            dur_ret = round(duration_years, depth + 1) if round_duration else duration_years
            rows.append([list(lords_tuple), (y, m, d, fh), dur_ret])

    def _recurse(level, parent_path, parent_start_jd, parent_duration_years, parent_end_jd):
        children, _ = _get_chathurvidha_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if level < depth:
                _recurse(level + 1, child_path, child_start_jd, child_duration, child_end_jd)
            else:
                _emit_row(child_path, child_start_jd, child_duration, child_end_jd)

    for md_sign, md_start_jd, md_dur, md_end_jd in _get_mahadasa_periods(jd_at_dob, place, seed):
        if depth == 1:
            _emit_row((md_sign,), md_start_jd, md_dur, md_end_jd)
        else:
            _recurse(2, (md_sign,), md_start_jd, md_dur, md_end_jd)

    return rows


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    dhasa_method=None,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns only the immediate (parent -> children) split under the given
    parent span: progression = [parent, parent+1, ..., wrap], weighted
    1..12 out of 78, exactly tiling [parent_start, parent_end].
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    children, _ = _get_chathurvidha_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        parent_end_jd=end_jd,
    )

    return [
        [
            child_path,
            _jd_to_tuple(child_start_jd),
            _jd_to_tuple(child_end_jd),
        ]
        for child_path, child_start_jd, _child_duration, child_end_jd in children
    ]


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    dhasa_method=None,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns the running Maha -> ... -> target-depth ladder for current_jd.
    """
    global year_duration

    if dhasa_method is None:
        dhasa_method = const.chathurvidha_utthara_dhasa_default

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        **kwargs,
    )

    asc_house = planet_positions[0][1][0]
    seed = _seed_for_method(planet_positions, asc_house, dhasa_method)

    maha_sign = maha_start_jd = maha_end_jd = maha_dur = None

    for md_sign, md_start_jd, md_dur, md_end_jd in _get_mahadasa_periods(jd_at_dob, place, seed):
        if md_start_jd <= current_jd < md_end_jd:
            maha_sign, maha_start_jd, maha_dur, maha_end_jd = md_sign, md_start_jd, md_dur, md_end_jd
            break
    else:
        # current_jd is at/past the final boundary - fall back to the last MD.
        _all_md = _get_mahadasa_periods(jd_at_dob, place, seed)
        if _all_md:
            maha_sign, maha_start_jd, maha_dur, maha_end_jd = _all_md[-1]

    if maha_sign is None:
        return []

    running_all = [
        [
            (maha_sign,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    parent_path = (maha_sign,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_chathurvidha_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            parent_end_jd=parent_end_jd,
        )

        found = _find_child_containing_jd(children, current_jd)

        if found is None:
            running_all.append(
                [
                    parent_path + (parent_path[-1],),
                    utils.jd_to_gregorian(parent_start_jd),
                    utils.jd_to_gregorian(parent_end_jd),
                ]
            )
            break

        child_path, child_start_jd, child_duration_years, child_end_jd = found

        running_all.append(
            [
                child_path,
                utils.jd_to_gregorian(child_start_jd),
                utils.jd_to_gregorian(child_end_jd),
            ]
        )

        parent_path = child_path
        parent_start_jd = child_start_jd
        parent_end_jd = child_end_jd
        parent_duration_years = child_duration_years

    return running_all


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    from datetime import datetime
    import random
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    print(check_date)
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    # ---- Print Mahadasa list ----
    _md = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    print("=== Mahadasas ===")
    for row in _md:
        lords, (y, m, d, fh), dur = row
        print(f"{utils.RAASI_SHORT_LIST[lords[0]]} "
              f"{y}-{m:02d}-{d:02d} {utils.to_dms(fh)}  dur={dur:.4f}")

    db = get_dhasa_antardhasa(dob,tob,place,dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
    md_ad_seq = {}
    for lords,_,_ in db:
        lord,sub_lord = lords
        lord_name = utils.RAASI_SHORT_LIST[lord]
        if lord_name not in md_ad_seq:
            md_ad_seq[lord_name] = []
        md_ad_seq[lord_name].append(utils.RAASI_SHORT_LIST[sub_lord])
    md_ad_seq = {k: ','.join(v) for k,v in md_ad_seq.items()}
    for lord,sub_lord_seq in md_ad_seq.items():
        print(lord," > ",md_ad_seq[lord])
    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
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
        grd = get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=DLI,
                dhasa_duration_type=dd,
            )
        print('running_all',grd)
        grdn = [
                ['-'.join([utils.RAASI_SHORT_LIST[lord] for lord in lords]),
                 (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))]
                    for [lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2)] in grd]
        print("Dehā (new)  :", grdn)
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd,
            return_exact_bounds=True,
        )
        deha_groups = utils._group_ancestors_from_leaves(ad, DLI)
        old_last_lords, old_start_jd, old_end_jd = utils._find_containing_group(deha_groups, current_jd)
        old_last_name = '-'.join([utils.RAASI_SHORT_LIST[lord] for lord in old_last_lords])
        y1, m1, d1, fh1 = utils.jd_to_gregorian(old_start_jd)
        y2, m2, d2, fh2 = utils.jd_to_gregorian(old_end_jd)
        print("Dehā (old)  :", [old_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('old method elapsed time', time.time() - start_time)

        print("\n" + "-" * 80)
        print("DIFF (new - old), Deha level only:")
        print("  new lords:", grdn[-1][0], " old lords:", old_last_name)
        print("-" * 80)
    exit()
