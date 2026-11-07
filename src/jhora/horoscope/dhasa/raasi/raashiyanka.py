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
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik
"""
Rasyamsaka (Rashiyanka) Dasa.

Ref: https://astrologicalmusings.com/method-of-calculating-rashiyanka-dasha/

Applicable only when the Lagna lord is strong (exalted, own sign, or a
friend's sign) - see applicability().

Seed: the Dn sign (default D-9/Navamsa) occupied by the Lagna lord.
const.RASYAMSAKA_DHASA_METHOD offers a second reading from the same
reference: VENKATESHWAR_BPHS (default, seed always from the Lagna lord)
or GANESH_DUTT_PATHAK_BPHS (seed from whichever of Lagna/Lagna lord is
stronger). MD order: forward zodiacal from the seed.

MD duration: inclusive sign count from the sign to its lord's D-1
position (direct if odd, indirect if even); own-sign=12yr;
7th-from-lord=10yr. Matches the reference's own worked example (King
George VI chart) on 11 of 12 signs; Leo is an unresolved exception. A
second worked chart in the same reference (Tony Blair) does not
reconcile with this formula beyond a few signs; left undocumented in the
reference and not patched to fit.

Antardasa is not addressed in the reference; extends the Mahadasa order
recursively at each level (working assumption, not sourced).

divisional_chart_factor (default 1) is the chart used for Lagna/lord
identification and duration lookups; seed_divisional_chart_factor
(default 9) is used only for the seed lookup and may be set to any
other Dn for exploratory use.

Release History
----------------
V5.0 - Refactored.
"""
year_duration = const.sidereal_year
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True
_DEFAULT_SEED_VARGA = 9
def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration
def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """Return the real (transit-based) end JD, with a naive-estimate backstop."""
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
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq):
    """Return the (start,end) JD pairs for each child in child_seq."""
    child_years = parent_years / 12.0
    parent_real_days = parent_end_jd - parent_start_jd
    n = len(child_seq)
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        if is_last:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (child_years * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out
def applicability(planet_positions):
    """Return True if the Lagna lord is exalted, in its own sign, or in a friend's sign."""
    asc_house = planet_positions[0][1][0]
    lord_asc = house.house_owner_from_planet_positions(planet_positions, asc_house)
    house_lord_asc = planet_positions[lord_asc + 1][1][0]
    return utils.is_planet_strong(lord_asc, house_lord_asc)
def _varga_sign(planet_positions, jd_at_dob, place, chart_method, sign, longitude, divisional_chart_factor):
    """Return the Dn sign for the body known at (sign, longitude) in the base chart."""
    pp_dn = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method
    )
    for i, (body, (s, lon)) in enumerate(planet_positions):
        if s == sign and abs(lon - longitude) < 1e-6:
            return pp_dn[i][1][0]
    raise ValueError("Could not locate body for varga lookup")
def _md_seed(planet_positions, jd_at_dob, place, chart_method, dhasa_method, seed_divisional_chart_factor):
    """Return the Mahadasa seed sign."""
    asc_house, asc_long = planet_positions[0][1]
    lord_asc = const._house_owners_list[asc_house]
    lord_house, lord_long = planet_positions[lord_asc + 1][1]
    if dhasa_method == const.RASYAMSAKA_DHASA_METHOD.GANESH_DUTT_PATHAK_BPHS:
        stronger = house.stronger_planet_from_planet_positions(planet_positions, 'L', lord_asc)
        if stronger == 'L':
            return _varga_sign(planet_positions, jd_at_dob, place, chart_method,
                                asc_house, asc_long, seed_divisional_chart_factor)
        return _varga_sign(planet_positions, jd_at_dob, place, chart_method,
                            lord_house, lord_long, seed_divisional_chart_factor)
    return _varga_sign(planet_positions, jd_at_dob, place, chart_method,
                        lord_house, lord_long, seed_divisional_chart_factor)
def _md_order(seed):
    """Return the 12 Mahadasa lords, starting from seed."""
    return [(seed + h) % 12 for h in range(12)]
def _dhasa_duration(planet_positions, sign):
    """Return the Mahadasa duration (years) of sign."""
    lord_of_sign = const._house_owners_list[sign]
    lord_sign = planet_positions[lord_of_sign + 1][1][0]
    if lord_sign == sign:
        return 12
    if lord_sign == (sign + 6) % 12:
        return 10
    if sign in const.even_signs:
        duration = (sign - lord_sign + 1) % 12
    else:
        duration = (lord_sign - sign + 1) % 12
    return duration or 12
def _antardhasa_order(parent_sign):
    """Return the antardasa order for parent_sign."""
    return [(parent_sign + h) % 12 for h in range(12)]
def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    seed_divisional_chart_factor=_DEFAULT_SEED_VARGA,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_method=None,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return dhasa/antardhasa periods. dhasa_method: const.RASYAMSAKA_DHASA_METHOD.*"""
    if dhasa_method is None:
        dhasa_method = const.rasyamsaka_dhasa_method_default
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    seed = _md_seed(planet_positions, jd_at_dob, place, chart_method, dhasa_method, seed_divisional_chart_factor)
    md_lords = _md_order(seed)
    rows = []
    start_jd = jd_at_dob
    def _append_row(labels, start_jd_val, seg_years):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))
    def _recurse(level, parent_lord, pstart_jd, parent_years, parent_end_jd, prefix):
        child_seq = _antardhasa_order(parent_lord)
        child_years = parent_years / 12.0
        child_bounds = _split_into_children(place, pstart_jd, parent_end_jd, parent_years, child_seq)
        if level + 1 == lvl:
            for c, (child_start_jd, _child_end_jd) in zip(child_seq, child_bounds):
                _append_row(prefix + (c,), child_start_jd, child_years)
            return parent_end_jd
        for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
            _recurse(level + 1, c, child_start_jd, child_years, child_end_jd, prefix + (c,))
        return parent_end_jd
    for md_lord in md_lords:
        md_years = float(_dhasa_duration(planet_positions, md_lord))
        md_end_jd = _bounded_end_jd(start_jd, place, md_years)
        if lvl == 1:
            _append_row((md_lord,), start_jd, md_years)
        else:
            _recurse(1, md_lord, start_jd, md_years, md_end_jd, (md_lord,))
        start_jd = md_end_jd
    return rows
def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method=1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return immediate child periods for a parent dasha."""
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1]
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd2t(jd_val):
        return utils.jd_to_gregorian(jd_val)
    start_jd = _t2jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, place, parent_years)
    else:
        end_jd = _t2jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []
    child_seq = _antardhasa_order(parent_sign)
    child_bounds = _split_into_children(place, start_jd, end_jd, parent_years, child_seq)
    rows = []
    for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
        if child_end_jd > child_start_jd:
            rows.append((path + (c,), _jd2t(child_start_jd), _jd2t(child_end_jd)))
    return rows
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    seed_divisional_chart_factor: int = _DEFAULT_SEED_VARGA,
    chart_method=1,
    dhasa_method=None,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return the running dhasa sequence for a given date."""
    if dhasa_method is None:
        dhasa_method = const.rasyamsaka_dhasa_method_default
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
    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    seed = _md_seed(planet_positions, jd_at_dob, place, chart_method, dhasa_method, seed_divisional_chart_factor)
    md_lords = _md_order(seed)
    md_entries = []
    cursor_jd = jd_at_dob
    for md_lord in md_lords:
        md_years = float(_dhasa_duration(planet_positions, md_lord))
        md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
        md_entries.append((md_lord, cursor_jd, md_end_jd, md_years))
        cursor_jd = md_end_jd
    located_entry = None
    for md, seg_start, seg_end, seg_years in md_entries:
        if seg_start <= current_jd < seg_end:
            located_entry = (md, seg_start, seg_end, seg_years)
            break
    if located_entry is None:
        located_entry = md_entries[-1]
    md_sign, md_start, md_end, md_years = located_entry
    ladder = [([md_sign], utils.julian_day_to_date_time_string(md_start),
               utils.julian_day_to_date_time_string(md_end))]
    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder
    parent_lords = [md_sign]
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_years
    parent_sign = md_sign
    for level in range(2, target + 1):
        child_seq = _antardhasa_order(parent_sign)
        child_bounds = _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq)
        child_years = parent_years / 12.0
        chosen = None
        for c, (c_start, c_end) in zip(child_seq, child_bounds):
            if c_start <= current_jd < c_end:
                chosen = (c, c_start, c_end)
                break
        if chosen is None:
            chosen = (child_seq[-1], child_bounds[-1][0], child_bounds[-1][1])
        child_sign, child_start_jd, child_end_jd = chosen
        parent_lords = parent_lords + [child_sign]
        ladder.append((parent_lords, utils.julian_day_to_date_time_string(child_start_jd),
                       utils.julian_day_to_date_time_string(child_end_jd)))
        parent_sign = child_sign
        parent_start_jd, parent_end_jd, parent_years = child_start_jd, child_end_jd, child_years
    return ladder
if __name__ == "__main__":
    utils.set_language('en')
    def _print_md_table(dob, tob, place, label, expected=None, **kwargs):
        print("=" * 70)
        print(label)
        print("=" * 70)
        rows = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=1, **kwargs)
        ok = 0
        for lords, start_tuple, dur_years in rows:
            sign = lords[0]
            lord_name = utils.RAASI_SHORT_LIST[sign]
            y_, m_, d_, fh_ = start_tuple
            marker = ""
            if expected is not None and lord_name in expected:
                match = int(dur_years) == expected[lord_name]
                ok += match
                marker = "  OK" if match else f"  MISMATCH (expected {expected[lord_name]})"
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs{marker}")
        if expected is not None:
            print(f"-> {ok}/{len(expected)} durations match the reference")
        print()
    # Chart 1 (Tony Blair) - does not fully reconcile with this duration
    # formula beyond a few signs; see module docstring.
    chart1_dob = drik.Date(1953, 5, 6)
    chart1_tob = (6, 10, 0)
    chart1_place = drik.Place('Edinburgh,Scotland', 55 + 57 / 60, -3 - 13 / 60, +1.0)
    chart1_expected = {'Cp': 5, 'Aq': 8, 'Pi': 11, 'Ar': 2, 'Ta': 3, 'Ge': 11, 'Cn': 10, 'Le': 9, 'Vi': 5}
    _print_md_table(chart1_dob, chart1_tob, chart1_place, "Chart 1 (Tony Blair)", chart1_expected)
    # Chart 2 (King George VI) - matches 11 of 12 signs; Leo is the one
    # unresolved exception.
    chart2_dob = drik.Date(1895, 12, 14)
    chart2_tob = (3, 5, 0)
    chart2_place = drik.Place('Sandringham Estate,England', 52 + 50 / 60, 0 + 30 / 60, 0.0)
    chart2_expected = {'Aq': 9, 'Pi': 9, 'Ar': 8, 'Ta': 8, 'Ge': 6, 'Cn': 9, 'Le': 5,
                        'Vi': 11, 'Li': 12, 'Sc': 12, 'Sg': 8, 'Cp': 4}
    _print_md_table(chart2_dob, chart2_tob, chart2_place, "Chart 2 (King George VI)", chart2_expected)
    # Research use: same chart, seed via a different Dn (not per reference).
    _print_md_table(chart2_dob, chart2_tob, chart2_place,
                     "Chart 2 (King George VI) - seed via D-11 instead of D-9 (exploratory)",
                     expected=None, seed_divisional_chart_factor=11)
    exit()
