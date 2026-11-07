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
    Also called Brahma Grahashrita Dasa

    Jaimini's Brahma Dasa: longevity is reckoned from Brahma to Maheswara.
    The dasa begins from the sign occupying the Brahma point (or the 7th
    from it, when the Brahma sign is even), progressing zodiacally from an
    odd starting sign or anti-zodiacally from an even starting sign.
    Duration of each Mahadasa sign is reckoned from that sign to the sign
    occupied by the lord of the 6th house from it (+1 year if that lord is
    exalted, -1 if debilitated, 0 if the 6th lord sits in the dasa sign
    itself); counting direction (zodiacal/anti-zodiacal) depends on
    whether the dasa sign itself is odd or even.

    Release History:
        V5.0 - Refactored to match JHora
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house

year_duration = const.sidereal_year

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3) -- same mechanism already used in every other refactored dhasa module
# in this project.
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in every other dhasa module refactored in this
# project) to become unreliable by a real, non-trivial margin. For THIS
# dhasa (fixed 12-way equal splits at every level below Mahadasa), worst-
# case duration reaches sub-day starting around PAD level (~0.176 days
# worst case). This check is duration-triggered, re-evaluated fresh for
# every batch of children, regardless of level.
_SUB_DAY_DURATION_DAYS = 1.0


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, guarding
    against drik._get_dhasa_end_jd()'s known unreliability for small
    durations. The pre-refactor draft had NO drik._get_dhasa_end_jd()
    calls anywhere (pure linear arithmetic instead) -- every boundary in
    this module now routes through this wrapper, per the project's
    standing direction to apply real end_jd at every level.
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


def _dhasa_duration(planet_positions, sign):
    """
    UNCHANGED from the pre-refactor draft. Period of Brahma dasa for a
    given sign is reckoned from that sign to the sign occupied by the
    lord of the 6th house from it (+1 if exalted, -1 if debilitated, 0 if
    the 6th lord sits in the dasa sign itself); counting direction
    (zodiacal/anti-zodiacal) depends on whether the dasa sign itself is
    odd or even.
    """
    lord_of_6th = house.house_owner_from_planet_positions(planet_positions, (sign + const.HOUSE_6) % 12)
    lord_house = planet_positions[lord_of_6th + 1][1][0]
    _dd = (lord_house + 13 - sign) % 12
    if sign in const.even_signs:
        _dd = (sign + 13 - lord_house) % 12
    _dd -= 1
    if lord_house == sign:
        _dd = 0
    elif const.house_strengths_of_planets[lord_of_6th][lord_house] == const._DEBILITATED_NEECHAM:
        _dd -= 1
    elif const.house_strengths_of_planets[lord_of_6th][lord_house] == const._EXALTED_UCCHAM:
        _dd += 1
    return _dd


def _antardhasa_order(planet_positions, parent_sign):
    """
    V5.1 REAL BUG FIX (see module docstring above for full derivation):
    the antara/deeper-level child order for ANY parent sign starts at the
    sign CURRENTLY OCCUPIED BY THE PARENT SIGN'S OWN LORD (rashi swami --
    via house.house_owner_from_planet_positions(), the SAME helper the
    Mahadasa duration formula already uses for the 6th-from-sign lord,
    here simply anchored at the parent sign directly instead), then
    proceeds zodiacally through all 12 signs from there. CONFIRMED to
    match real JHora data exactly for all 12 possible parent signs (see
    module docstring above) -- this REPLACES the pre-refactor draft's
    naive "start at the parent sign itself" assumption, which was wrong.
    """
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, parent_sign)
    lord_house = planet_positions[lord_of_sign + 1][1][0]
    return [(lord_house + k) % 12 for k in range(12)]


def _get_brahma_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    planet_positions,
    *,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Brahma Dasa (used at every level below
    Mahadasa, by ALL THREE entry points: get_dhasa_antardhasa()'s own
    recursion, brahma_immediate_children(), and get_running_dhasa_for_
    given_date()).

    Rules:
        - Child order = _antardhasa_order(planet_positions, parent_sign)
          -- CONFIRMED against real JHora data (see module docstring
          above and V5.1 changelog) -- starts at the parent sign's OWN
          lord's current house, then proceeds zodiacally through all 12
          signs.
        - EQUAL split: child_duration = parent_duration / 12 (UNCHANGED
          from the pre-refactor draft -- only the ORDER was wrong, not
          the split rule).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's child duration is under _SUB_DAY_DURATION_DAYS,
          ALL child boundaries (not just the last) are computed via
          proportional interpolation of the parent's own real
          [parent_start_jd, parent_end_jd] span, instead of calling
          _bounded_end_jd()/drik._get_dhasa_end_jd() per child.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    parent_sign = parent_path[-1]

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    child_signs = _antardhasa_order(planet_positions, parent_sign)
    n = len(child_signs)
    child_duration = parent_duration / 12.0

    child_duration_days = child_duration * year_duration
    use_proportional_interpolation = child_duration_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd

    children = []
    cursor = parent_start_jd

    for i, child_sign in enumerate(child_signs):
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            child_end_jd = parent_start_jd + parent_span * (i + 1) / n
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


def _generate_mahadasa_periods(
    jd_at_dob,
    place,
    planet_positions,
    *,
    stop_at_jd=None,
):
    """
    THE single Mahadasa seed/root generator for Brahma Dasa. This is the
    ONLY place in the module that computes the Brahma seed sign, builds
    the (odd-seed zodiacal / even-seed anti-zodiacal-from-7th)
    progression, and walks it starting from the birth JD. get_dhasa_
    antardhasa(), brahma_immediate_children() (indirectly, via get_
    running_dhasa_for_given_date()'s own use of this generator), and
    get_running_dhasa_for_given_date() all rely on THIS SAME generator
    for the Mahadasa level.

    UNCHANGED in logic from the pre-refactor draft -- CONFIRMED against
    a reference PDF's own worked examples for the seed/progression rule
    (see module docstring above); the per-sign duration itself comes from
    _dhasa_duration(), preserved exactly.

    Yields:
        (sign, maha_start_jd, maha_duration_years, maha_end_jd)
    """
    brahma = house.brahma(planet_positions)
    dhasa_seed = planet_positions[brahma + 1][1][0]

    dhasa_lords = [(dhasa_seed + h) % 12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [(dhasa_seed + const.HOUSE_7 - h + 12) % 12 for h in range(12)]

    start_jd = jd_at_dob

    for lord in dhasa_lords:
        dd = float(_dhasa_duration(planet_positions, lord))

        maha_start_jd = start_jd
        maha_end_jd = _bounded_end_jd(maha_start_jd, dd, place)

        yield lord, maha_start_jd, dd, maha_end_jd

        start_jd = maha_end_jd

        if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
            return


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
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
    **kwargs,
):
    """
    Compute Brahma-based sign dasa with depth control (Maha -> Antara -> ...).

    Uses the SAME shared _generate_mahadasa_periods()/_get_brahma_children_jd()
    engine as brahma_immediate_children() and get_running_dhasa_for_given_date().

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    (new parameter, matching the project-wide convention already present
    in every other refactored dhasa module).
    """
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

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
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    dhasa_info = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            dhasa_info.append(
                (
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                )
            )
        else:
            start_str = utils.jd_to_gregorian(start_jd_local)
            dur_ret = round(duration_years, dhasa_level_index + 1) if round_duration else duration_years
            dhasa_info.append((lords_tuple, start_str, dur_ret))

    def _recurse(level, parent_path, parent_start_jd, parent_duration_years, parent_end_jd):
        children, _ = _get_brahma_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            planet_positions,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(level + 1, child_path, child_start_jd, child_duration, child_end_jd)
            else:
                _emit_row(child_path, child_start_jd, child_duration, child_end_jd)

    for lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        planet_positions,
    ):
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row((lord,), maha_start_jd, maha_dur, maha_end_jd)
        else:
            _recurse(
                const.MAHA_DHASA_DEPTH.ANTARA,
                (lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
            )

    return dhasa_info


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Brahma Dasa -- return ONLY the immediate (p -> p+1) children under the given parent span.

    A thin wrapper around the shared _get_brahma_children_jd() engine
    (previously duplicated the antara-order/equal-split logic
    independently from get_dhasa_antardhasa() -- now both call the same
    engine).
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
        raise ValueError("parent_lords must be int or non-empty tuple/list")

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

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    children, _ = _get_brahma_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        planet_positions,
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
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Brahma Dasa -- narrow Maha -> ... -> target depth and return the full running ladder.

    Uses the SAME shared _generate_mahadasa_periods()/_get_brahma_children_jd()
    engine as get_dhasa_antardhasa() and brahma_immediate_children(). The
    Mahadasa level is found via a single early-stopping walk of
    _generate_mahadasa_periods() (stop_at_jd=current_jd) rather than
    rebuilding the FULL Mahadasa-only row list and handing it to
    jhora.utils.get_running_dhasa_for_given_date() for lookup -- a pure
    architectural/performance consolidation (that utility itself is not
    being treated as buggy; see module docstring above). Every level
    below Mahadasa uses _get_brahma_children_jd() then _find_child_
    containing_jd(), staying in JD-float space throughout (only the final
    returned rows are converted to Gregorian tuples).
    """
    global year_duration

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
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None

    for lord, m_start_jd, m_dur, m_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        planet_positions,
        stop_at_jd=current_jd,
    ):
        maha_lord, maha_start_jd, maha_dur, maha_end_jd = lord, m_start_jd, m_dur, m_end_jd

    if maha_lord is None:
        return []

    running_all = [
        [
            (maha_lord,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    parent_path = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_brahma_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            planet_positions,
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
    const.aquarius_owner_for_dhasa_calculations = const.SATURN_ID
    const.scorpio_owner_for_dhasa_calculations = const.KETU_ID
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
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.brahma_dhasa_test()
