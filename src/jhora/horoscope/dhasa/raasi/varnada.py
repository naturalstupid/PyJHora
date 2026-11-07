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
Varnada Dasa

Mahadasa seed: stronger of Lagna and the Hora Lagna.
Mahadasa order: forward from the seed, reverse if the seed is an even
sign.
Mahadasa duration for each sign is (sign - varnada_lagna) % 12 years,
where varnada_lagna is the Varnada Lagna sign for the chart. One of the
twelve signs in the cycle will always coincide with the Varnada Lagna
itself, giving that sign a duration of zero years; this is expected
V5.0 Refactored to match JHora.
"""

year_duration = const.sidereal_year

_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True


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


def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq):
    """ Splits a parent span into twelve equal children using real dasa-period boundaries. """
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


def _child_sequence(parent_lord):
    """
    Antardasa order: forward from the parent sign if the parent sign is
    odd, backward if even - the same convention used for the Mahadasa
    order itself. Confirmed against full JHora antardasa tables for four
    Mahadasas (Pisces and Capricorn, both even, matching backward;
    Aquarius, odd, matching forward; Scorpio, even, matching backward).
    """
    direction = 1 if parent_lord in const.odd_signs else -1
    return [(parent_lord + direction * h) % 12 for h in range(12)]


def _md_seed_and_order(planet_positions, jd_at_dob, place, divisional_chart_factor, chart_method,
                        years, months, sixty_hours, varnada_method, **kwargs):
    lagna = planet_positions[0][1][0]
    hora_lagna_full = charts.get_chart_element_longitude(
        jd=jd_at_dob, place=place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, dhasa_starting_planet="HL")
    hora_lagna, _ = drik.dasavarga_from_long(hora_lagna_full)
    varnada_lagna_full = charts.get_chart_element_longitude(
        jd=jd_at_dob, place=place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, dhasa_starting_planet="V1", varnada_method=varnada_method)
    varnada_lagna, _ = drik.dasavarga_from_long(varnada_lagna_full)

    seed = house.stronger_rasi_from_planet_positions(planet_positions, lagna, hora_lagna)
    if seed in const.even_signs:
        order = [(seed - h) % 12 for h in range(12)]
    else:
        order = [(seed + h) % 12 for h in range(12)]
    return seed, order, varnada_lagna


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    varnada_method=None,
    **kwargs
):
    """
    Varnada Dasha, computed to the requested depth (1 = Mahadasa only,
    up to 6 = Mahadasa through Deha-antardasa).
    @return: list of rows, each (lords_tuple, start_tuple, duration_years)
    """
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    _, md_lords, varnada_lagna = _md_seed_and_order(
        planet_positions, jd_at_dob, place, divisional_chart_factor, chart_method,
        years, months, sixty_hours, varnada_method, **kwargs)

    rows = []
    start_jd = jd_at_dob

    def _append_row(labels, start_jd_val, seg_years):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))

    def _recurse(level, parent_lord, pstart_jd, parent_years, parent_end_jd, prefix):
        child_seq = _child_sequence(parent_lord)
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
        md_years = (md_lord - varnada_lagna) % 12
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
    jd_at_dob=None,
    place=None,
    dhasa_duration_type=None,
    savana_year_method=None,
    round_duration: bool = False,
    varnada_method=None,
    **kwargs
):
    """
    Returns the twelve immediate antardasa children of a given parent
    span, at any depth. Children always progress forward from the parent
    sign.
    """
    if jd_at_dob is not None and place is not None:
        _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)

    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = path[-1] % 12

    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

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

    child_seq = _child_sequence(parent_sign)
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
    chart_method=1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    varnada_method=None,
    **kwargs
):
    """
    Returns the running dasa/antardasa chain, from Mahadasa down to the
    requested depth, for `current_jd`.
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

    planet_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]

    _, md_lords, varnada_lagna = _md_seed_and_order(
        planet_positions, jd_at_dob, place, divisional_chart_factor, chart_method,
        years, months, sixty_hours, varnada_method, **kwargs)

    md_entries = []
    cursor_jd = jd_at_dob
    for md_lord in md_lords:
        md_years = (md_lord - varnada_lagna) % 12
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
        child_seq = _child_sequence(parent_sign)
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

    CHART = "1996-12-07"   # or "2004-06-25"
    if CHART == "1996-12-07":
        dob = drik.Date(1996, 12, 7)
        tob = (10, 34, 0)
    else:
        dob = drik.Date(2004, 6, 25)
        tob = (14, 47, 0)

    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    dcf = 1

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)
        print(f"\n--- MD-only table ({CHART}) ---")
        md_only_rows = get_dhasa_antardhasa(
            dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd, divisional_chart_factor=dcf,
        )
        for lords, start_tuple, dur_years in md_only_rows:
            lord_name = utils.RAASI_SHORT_LIST[lords[0]]
            y_, m_, d_, fh_ = start_tuple
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs")

        print(f"\n--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss} ---")
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            divisional_chart_factor=dcf,
        )
        for lords, start_str, end_str in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:15s} {start_str}  ->  {end_str}")
        print('elapsed time', time.time() - start_time)
