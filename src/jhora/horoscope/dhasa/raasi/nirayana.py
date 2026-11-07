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
Niryaana Shoola Dhasa
V5.0 - Refactored to match JHora results

Mahadasa seed sign is the stronger of the 2nd and 8th houses from Lagna.
The 12-sign Mahadasa progression runs forward (zodiacal) from the seed
if it is an odd sign, backward (anti-zodiacal) if even. Each Mahadasa's
duration is 7 years for a movable sign, 8 for a fixed sign, 9 for a dual
sign, for a first cycle; a second cycle follows in which each sign's
duration is 12 minus its first-cycle duration (skipped if this is zero
or negative), continuing until the cumulative age reaches
const.human_life_span_for_narayana_dhasa (108 years).

Antardasa (and every level below Mahadasa) uses the same seed/order rule
as raasi Narayana Dasa's own antardhasa (_narayana_antardhasa), applied
recursively, with an equal 12-way duration split at every level.
"""
from jhora import const, utils
from jhora.horoscope.chart import house, charts
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.dhasa.raasi.narayana import _narayana_antardhasa

year_duration = const.sidereal_year

_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    """
    Sets the module-level year_duration used by _bounded_end_jd() and
    sub-day interpolation. If dhasa_duration_type is given, it also sets
    const.dhasa_year_duration_default; otherwise the existing global is
    left unchanged.
    """
    global year_duration
    if dhasa_duration_type is not None:
        const.dhasa_year_duration_default = dhasa_duration_type
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """ Real dasa-period end JD, guarded by a naive average-year backstop. """
    naive_end = start_jd + duration_in_years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, duration_in_years)
    except Exception:
        return naive_end
    if real_end is None or real_end <= start_jd:
        return naive_end
    if _USE_SANITY_BACKSTOP and abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end


def _antardhasa_order(planet_positions, seed_rasi):
    """ Antardhasa seed/order: same rule as raasi Narayana Dasa's own
    antardhasa (_narayana_antardhasa). """
    return _narayana_antardhasa(planet_positions, seed_rasi)


def _children_of(planet_positions, place, seed_rasi, start_jd, duration_years, parent_end_jd=None):
    """
    Returns the 12 immediate children of one parent (seed rasi / start_jd /
    duration) as (child_rasi, child_start_jd, child_end_jd,
    child_duration_years) tuples. The last child is clamped exactly to
    parent_end_jd when supplied. If a child's duration falls under
    _SUB_DAY_THRESHOLD_DAYS, its end is found by proportional
    interpolation of the parent's own real span instead of a fresh
    boundary call.
    """
    child_duration = duration_years / 12.0
    child_sequence = _antardhasa_order(planet_positions, seed_rasi)
    parent_real_days = (parent_end_jd - start_jd) if parent_end_jd is not None else None

    children = []
    cursor_jd = start_jd
    for idx, child_rasi in enumerate(child_sequence):
        is_last = (idx == len(child_sequence) - 1)
        if is_last and parent_end_jd is not None:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and parent_real_days is not None and \
                (child_duration * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = start_jd + parent_real_days * (idx + 1) / 12.0
        else:
            end_jd = _bounded_end_jd(cursor_jd, place, child_duration)

        children.append((child_rasi, cursor_jd, end_jd, child_duration))
        cursor_jd = end_jd
    return children


def get_immediate_children(
        parent_lords, parent_start, parent_duration=None, parent_end=None,
        *, jd_at_dob, place, divisional_chart_factor=9, chart_method=1,
        years=1, months=1, sixty_hours=1,
        dhasa_duration_type=None, savana_year_method=None,
        **kwargs
    ):
    """
    Returns the immediate 12 children under a given parent span.

    parent_lords: int (single seed rasi) or tuple/list (path ending in the
        parent's seed rasi).
    parent_start: (Y, M, D, fractional_hour)
    parent_duration (years) or parent_end (Y, M, D, fractional_hour):
        provide exactly one.

    Output rows: [ [child_lords_tuple, child_start_tuple, child_end_tuple], ... ]
    """
    if jd_at_dob is not None:
        _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    if isinstance(parent_lords, int):
        path = (int(parent_lords) % 12,)
    else:
        path = tuple(int(x) % 12 for x in parent_lords)
    parent_seed_rasi = path[-1]

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
        end_jd = _bounded_end_jd(start_jd, place, parent_years)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []
    planet_positions = charts.divisional_chart(jd_at_dob,place,
                                               divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method,
                                               years=years,months=months,sixty_hours=sixty_hours,
                                               )
    children = _children_of(planet_positions, place, parent_seed_rasi, start_jd, parent_years, parent_end_jd=end_jd)

    return [
        [path + (child_rasi,), _jd_to_tuple(c_start), _jd_to_tuple(c_end)]
        for child_rasi, c_start, c_end, _c_dur in children
    ]


def _expand_tree(planet_positions, place, seed_rasi, start_jd, duration_years, end_jd,
                  lords_stack, current_level, target_level, birth_jd,
                  dhasa_info, stop_flag, round_duration):
    """
    Recursive whole-tree builder used by get_dhasa_antardhasa(). Applies
    the same _children_of() function at each level, threading the
    already-resolved end_jd down so the sub-day fallback and exact-clamp
    are available at every level.
    """
    if current_level == target_level:
        disp_dur = duration_years
        if round_duration:
            _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
            disp_dur = round(disp_dur, _round_ndigits)
        dhasa_info.append([tuple(lords_stack), utils.jd_to_gregorian(start_jd), disp_dur])

        age_years = (start_jd - birth_jd) / year_duration
        if age_years >= getattr(const, 'human_life_span_for_narayana_dhasa', 108):
            stop_flag['stop'] = True
        return

    children = _children_of(planet_positions, place, seed_rasi, start_jd, duration_years, parent_end_jd=end_jd)
    for child_rasi, child_start_jd, child_end_jd, child_duration in children:
        if stop_flag['stop']:
            break
        _expand_tree(
            planet_positions, place, child_rasi, child_start_jd, child_duration, child_end_jd,
            lords_stack + [child_rasi], current_level + 1, target_level,
            birth_jd, dhasa_info, stop_flag, round_duration
        )


def _maha_dhasa_progression(planet_positions):
    """
    Seed sign (stronger of 2H/8H) and 12-sign MD progression, zodiacal for
    odd seed signs, anti-zodiacal for even seed signs.
    """
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart[:])
    asc_house = p_to_h[const._ascendant_symbol]
    second_house = (asc_house + 2 - 1) % 12
    eighth_house = (asc_house + 8 - 1) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(
        planet_positions, second_house, eighth_house
    )
    direction = 1 if dhasa_seed_sign in const.odd_signs else -1
    return [(dhasa_seed_sign + direction * k) % 12 for k in range(12)]


def _md_years(md_rasi):
    """ Maha duration: 7/8/9 years by sign modality (movable/fixed/dual). """
    if md_rasi in const.fixed_signs:
        return 8
    elif md_rasi in const.dual_signs:
        return 9
    return 7  # movable


def get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=1,
                          dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                          round_duration=True,
                          dhasa_duration_type=None, savana_year_method=None):
    """
    Full Nirayana Shoola Dhasa table, from MD down to the requested depth
    (up to Deha).

    Returns rows: [ [lords_tuple, (Y, M, D, fractional_hour), duration_years], ... ]
    """
    jd = utils.julian_day_number(dob, tob)
    _set_year_duration(jd, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd, place, divisional_chart_factor=divisional_chart_factor
    )[:const._pp_count_upto_ketu]

    md_progression = _maha_dhasa_progression(planet_positions)

    dhasa_info = []
    birth_jd = jd
    start_jd = jd
    stop_flag = {'stop': False}
    first_cycle_basis_for_second = []

    for md_rasi in md_progression:
        if stop_flag['stop']:
            break
        md_years = _md_years(md_rasi)
        basis = md_years if dhasa_level_index == 1 else (md_years / 12.0)
        first_cycle_basis_for_second.append(basis)

        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        _expand_tree(
            planet_positions, place, md_rasi, start_jd, md_years, md_end_jd,
            [md_rasi], 1, dhasa_level_index, birth_jd, dhasa_info, stop_flag, round_duration
        )
        start_jd = md_end_jd

    if stop_flag['stop']:
        return dhasa_info

    for idx, md_rasi in enumerate(md_progression):
        if stop_flag['stop']:
            break
        md2_years = round(12 - first_cycle_basis_for_second[idx], 2)
        if md2_years <= 0:
            continue

        md2_end_jd = _bounded_end_jd(start_jd, place, md2_years)
        _expand_tree(
            planet_positions, place, md_rasi, start_jd, md2_years, md2_end_jd,
            [md_rasi], 1, dhasa_level_index, birth_jd, dhasa_info, stop_flag, round_duration
        )
        start_jd = md2_end_jd

        age_years = (start_jd - birth_jd) / year_duration
        if age_years >= getattr(const, 'human_life_span_for_narayana_dhasa', 108):
            break

    return dhasa_info


def get_running_dhasa_for_given_date(current_jd, jd_at_dob, place,
                                      dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                                      divisional_chart_factor=1,
                                      dhasa_duration_type=None, savana_year_method=None):
    """
    Returns the running dasa/antardasa/... chain, from Mahadasha down to
    the requested depth, for current_jd. Descends only the single branch
    containing current_jd at each level, reusing the same _children_of()
    function level-by-level.

    Returns: [ [lords_tuple, start_tuple, end_tuple], ... ] - one entry
    per level, from MD down to dhasa_level_index.
    """
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor
    )[:const._pp_count_upto_ketu]

    md_progression = _maha_dhasa_progression(planet_positions)
    birth_jd = jd_at_dob
    result = []

    def _locate(seed_rasi, seg_start_jd, seg_end_jd, seg_duration_years, lords_stack, level):
        result.append([
            tuple(lords_stack),
            utils.jd_to_gregorian(seg_start_jd),
            utils.jd_to_gregorian(seg_end_jd),
        ])
        if level == dhasa_level_index:
            return
        children = _children_of(planet_positions, place, seed_rasi, seg_start_jd,
                                  seg_duration_years, parent_end_jd=seg_end_jd)
        for child_rasi, child_start_jd, child_end_jd, child_duration in children:
            if child_start_jd <= current_jd < child_end_jd:
                _locate(child_rasi, child_start_jd, child_end_jd, child_duration,
                        lords_stack + [child_rasi], level + 1)
                return
        last_rasi, last_start, last_end, last_dur = children[-1]
        _locate(last_rasi, last_start, last_end, last_dur, lords_stack + [last_rasi], level + 1)

    md_entries = []  # (md_rasi, start_jd, end_jd, years)
    cursor_jd = birth_jd
    first_cycle_basis_for_second = []
    for md_rasi in md_progression:
        md_years = _md_years(md_rasi)
        basis = md_years if dhasa_level_index == 1 else (md_years / 12.0)
        first_cycle_basis_for_second.append(basis)
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        md_entries.append((md_rasi, cursor_jd, md_end_jd, md_years))
        cursor_jd = md_end_jd

    for idx, md_rasi in enumerate(md_progression):
        md2_years = round(12 - first_cycle_basis_for_second[idx], 2)
        if md2_years <= 0:
            continue
        md2_end_jd = _bounded_end_jd(cursor_jd, place, md2_years)
        md_entries.append((md_rasi, cursor_jd, md2_end_jd, md2_years))
        cursor_jd = md2_end_jd

    located_entry = None
    for md_rasi, seg_start, seg_end, seg_years in md_entries:
        if seg_start <= current_jd < seg_end:
            located_entry = (md_rasi, seg_start, seg_end, seg_years)
            break
    if located_entry is None:
        located_entry = md_entries[-1]

    md_rasi, md_start, md_end, md_years = located_entry
    _locate(md_rasi, md_start, md_end, md_years, [md_rasi], 1)

    return result


if __name__ == "__main__":
    utils.set_language('en')
    from jhora.panchanga.drik import Date, Place
    dob = Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    print("\n--- MD only ---")
    md_only = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
                                    dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR)
    for row in md_only:
        lords, start_tuple, durn = row
        print(utils.RAASI_SHORT_LIST[lords[0]], start_tuple, durn)

    print("\n--- MD -> AD ---")
    md_ad = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                                  dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR)
    md_ad_seq = {}
    for row in md_ad:
        lords, start_tuple, durn = row
        md_name = utils.RAASI_SHORT_LIST[lords[0]]
        ad_name = utils.RAASI_SHORT_LIST[lords[1]]
        md_ad_seq.setdefault(md_name, []).append((ad_name, start_tuple, durn))
    for md_name, ad_rows in md_ad_seq.items():
        print(md_name, "->", ','.join(a for a, _, _ in ad_rows))
        for ad_name, start_tuple, durn in ad_rows:
            print("   ", ad_name, start_tuple, durn)

    print("\n--- Running dasha chain (down to Deha) for 2010-11-09 15:29:45 ---")
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    current_jd = utils.julian_day_number(Date(y, m, d), (hh, mm, ss))
    grd = get_running_dhasa_for_given_date(
        current_jd, jd_at_dob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
        divisional_chart_factor=1,
        dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR,
    )
    for lords, start_tuple, end_tuple in grd:
        label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
        print(f"{label:15s} {start_tuple}  ->  {end_tuple}")
