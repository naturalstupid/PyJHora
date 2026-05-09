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
Calculates Vimshottari (=120) Dasha-bhukthi-antara-sukshma-prana
"""
from collections import OrderedDict as Dict
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

year_duration = const.sidereal_year
one_star = 360 / 27.0

vimsottari_adhipati = (
    lambda nak, seed_star=3: const.vimsottari_adhipati_list[
        (nak - seed_star + 3) % (len(const.vimsottari_adhipati_list))
    ]
)

# IMPORTANT: decouple from const to avoid mutating the library-wide constants object
vimsottari_dict = const.vimsottari_dict.copy()
human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa


### --- Vimsottari functions
def vimsottari_next_adhipati(lord, direction=1):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + direction) % len(const.vimsottari_adhipati_list)
    return const.vimsottari_adhipati_list[next_index]


def vimsottari_dasha_start_date(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    seed_star=3,
    dhasa_starting_planet=1,
):
    """Returns the start date of the mahadasa which occurred on or before `jd`"""
    planet_long = charts.get_chart_element_longitude(
        jd,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )
    nak = int(planet_long / one_star)
    rem = planet_long - nak * one_star
    lord = vimsottari_adhipati(nak, seed_star)
    period = vimsottari_dict[lord]

    period_elapsed = rem / one_star * period
    period_elapsed *= year_duration
    start_date = jd - period_elapsed
    return [lord, start_date]


def vimsottari_mahadasa(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    seed_star=3,
    dhasa_starting_planet=1,
):
    """List all mahadashas and their start dates"""
    lord, start_date = vimsottari_dasha_start_date(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )
    retval = Dict()
    for _ in range(9):
        retval[lord] = start_date
        start_date += vimsottari_dict[lord] * year_duration
        lord = vimsottari_next_adhipati(lord)

    return retval


def _vimsottari_rasi_bhukthi(maha_lord, maha_lord_rasi, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa using rasi bhukthi variation."""
    retval = Dict()
    bhukthi_duration = vimsottari_dict[maha_lord] / 12
    for bhukthi_rasi in [(maha_lord_rasi + h) % 12 for h in range(12)]:
        retval[bhukthi_rasi] = start_date
        start_date += bhukthi_duration * year_duration
    return retval


def _vimsottari_bhukti(maha_lord, start_date, antardhasa_option=1):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa and its start date."""
    lord = maha_lord
    if antardhasa_option in [3, 4]:
        lord = vimsottari_next_adhipati(lord, direction=1)
    elif antardhasa_option in [5, 6]:
        lord = vimsottari_next_adhipati(lord, direction=-1)
    dirn = 1 if antardhasa_option in [1, 3, 5] else -1
    retval = Dict()
    for _ in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa
        start_date += factor * year_duration
        lord = vimsottari_next_adhipati(lord, dirn)

    return retval


# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def _vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukti's start date."""
    lord = bhukti_lord
    retval = Dict()
    for _ in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * (vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa)
        factor *= (vimsottari_dict[bhukti_lord] / human_life_span_for_vimsottari_dhasa)
        start_date += factor * year_duration
        lord = vimsottari_next_adhipati(lord)

    return retval


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    for key in reversed(list(some_dict.keys())):
        if some_dict[key] < jd:
            return key


def compute_vimsottari_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    i = _where_occurs(jd, mahadashas)
    bhuktis = _vimsottari_bhukti(i, mahadashas[i])
    j = _where_occurs(jd, bhuktis)
    antara = _vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)


def get_vimsottari_dhasa_bhukthi(
    jd,
    place,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=3,
    antardhasa_option=1,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Provides Vimsottari dhasa at selected depth for a given birth Julian day (includes birth time).

    RETURNS (for ALL levels 1..6):
        (vim_balance, [ (lords_tuple), (Y, M, D, fractional_hour), duration_years_float ])
    """
    global human_life_span_for_vimsottari_dhasa, vimsottari_dict, year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    _orig_H = human_life_span_for_vimsottari_dhasa
    _orig_dict = vimsottari_dict.copy()

    try:
        _working_dict = _orig_dict
        if use_tribhagi_variation:
            _trib = 1.0 / 3.0
            H = _orig_H * _trib
            _working_dict = {k: round(v * _trib, 6) for k, v in _orig_dict.items()}
            _dhasa_cycles = int(1 / _trib)
        else:
            H = _orig_H
            _dhasa_cycles = 1

        human_life_span_for_vimsottari_dhasa = H
        vimsottari_dict = _working_dict

        dashas = vimsottari_mahadasa(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            star_position_from_moon=star_position_from_moon,
            seed_star=seed_star,
            dhasa_starting_planet=dhasa_starting_planet,
        )

        dl = list(dashas.values())
        de = dl[1]
        y, m, d, _ = utils.jd_to_gregorian(jd)
        p_date1 = drik.Date(y, m, d)
        y, m, d, _ = utils.jd_to_gregorian(de)
        p_date2 = drik.Date(y, m, d)
        vim_bal = utils.panchanga_date_diff(p_date1, p_date2)

        dhasa_bhukthi = []

        def _start_and_dir(parent_lord):
            lord = parent_lord
            if antardhasa_option in [3, 4]:
                lord = vimsottari_next_adhipati(lord, direction=+1)
            elif antardhasa_option in [5, 6]:
                lord = vimsottari_next_adhipati(lord, direction=-1)
            dirn = +1 if antardhasa_option in [1, 3, 5] else -1
            return lord, dirn

        def _children_planetary(parent_lord, parent_start_jd, parent_years):
            start_lord, dirn = _start_and_dir(parent_lord)
            jd_cursor = parent_start_jd
            lord = start_lord
            for _ in range(len(const.vimsottari_adhipati_list)):
                Y = float(vimsottari_dict[lord])
                dur_yrs = parent_years * (Y / H)
                yield (lord, jd_cursor, dur_yrs)
                jd_cursor += dur_yrs * year_duration
                lord = vimsottari_next_adhipati(lord, direction=dirn)

        def _emit_row(lords_tuple, start_jd, duration_years):
            dhasa_bhukthi.append([lords_tuple, utils.jd_to_gregorian(start_jd), float(duration_years)])

        def _emit_children_from_starts(parent_tuple, starts_list, parent_end_jd):
            for idx, (clord, cstart) in enumerate(starts_list):
                cend = parent_end_jd if idx == len(starts_list) - 1 else starts_list[idx + 1][1]
                dur_years = (cend - cstart) / year_duration
                _emit_row(parent_tuple + (clord,), cstart, dur_years)

        md_items = list(dashas.items())

        for _ in range(_dhasa_cycles):
            N = len(md_items)
            for idx, (md_lord, md_start_jd) in enumerate(md_items):
                if idx < N - 1:
                    md_end_jd = md_items[idx + 1][1]
                else:
                    md_end_jd = md_start_jd + float(vimsottari_dict[md_lord]) * year_duration
                md_years = (md_end_jd - md_start_jd) / year_duration

                if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                    _emit_row((md_lord,), md_start_jd, md_years)

                elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                    if use_rasi_bhukthi_variation:
                        planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=1)
                        maha_lord_rasi = planet_positions[md_lord + 1][1][0]
                        bhuktis = _vimsottari_rasi_bhukthi(md_lord, maha_lord_rasi, md_start_jd)
                    else:
                        bhuktis = _vimsottari_bhukti(md_lord, md_start_jd, antardhasa_option=antardhasa_option)
                    _emit_children_from_starts((md_lord,), list(bhuktis.items()), md_end_jd)

                elif dhasa_level_index == const.MAHA_DHASA_DEPTH.PRATYANTARA:
                    if use_rasi_bhukthi_variation:
                        raise ValueError(
                            "L3+ not supported with use_rasi_bhukthi_variation=True. "
                            "Keep depth at L2 or specify a custom L3 rule."
                        )
                    bhuktis = _vimsottari_bhukti(md_lord, md_start_jd, antardhasa_option=antardhasa_option)
                    bh_list = list(bhuktis.items())

                    for b_idx, (blord, bstart) in enumerate(bh_list):
                        bend = md_end_jd if b_idx == len(bh_list) - 1 else bh_list[b_idx + 1][1]
                        antara = _vimsottari_antara(md_lord, blord, bstart)
                        _emit_children_from_starts((md_lord, blord), list(antara.items()), bend)

                else:
                    if use_rasi_bhukthi_variation:
                        raise ValueError(
                            "L3+ not supported with use_rasi_bhukthi_variation=True. "
                            "Keep depth at L2 or specify a custom L3/L4 rule."
                        )

                    def _recurse_to_depth(level, parent_lord, parent_start_jd, parent_years, prefix):
                        if level == dhasa_level_index:
                            _emit_row(tuple(prefix), parent_start_jd, parent_years)
                            return
                        for clord, cstart, cyears in _children_planetary(parent_lord, parent_start_jd, parent_years):
                            _recurse_to_depth(level + 1, clord, cstart, cyears, prefix + [clord])

                    _recurse_to_depth(
                        level=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
                        parent_lord=md_lord,
                        parent_start_jd=md_start_jd,
                        parent_years=md_years,
                        prefix=[md_lord],
                    )

        return vim_bal, dhasa_bhukthi

    finally:
        human_life_span_for_vimsottari_dhasa = _orig_H
        vimsottari_dict = _orig_dict


def _start_lord_and_dir(parent_lord: int, antardhasa_option: int) -> tuple[int, int]:
    """
    Replicates your existing option handling.
    """
    lord = parent_lord
    if antardhasa_option in [3, 4]:
        lord = vimsottari_next_adhipati(lord, direction=+1)
    elif antardhasa_option in [5, 6]:
        lord = vimsottari_next_adhipati(lord, direction=-1)
    dirn = +1 if antardhasa_option in [1, 3, 5] else -1
    return lord, dirn


def vimsottari_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    antardhasa_option=1,
    use_rasi_bhukthi_variation=False,
    jd=None,
    place=None,
    divisional_chart_factor=1,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Returns ONLY the immediate (p->p+1) children under a given Vimśottarī parent period.
    """
    global year_duration

    if jd is not None and place is not None:
        year_duration = drik.dhasa_year_duration(
            jd=jd,
            place=place,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)):
        if len(parent_lords) == 0:
            raise ValueError("parent_lords cannot be empty")
        path = tuple(parent_lords)
    else:
        raise TypeError("parent_lords must be int or tuple/list of ints")

    parent_lord = path[-1]

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
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    children = []

    if use_rasi_bhukthi_variation and len(path) == 1:
        if jd is None or place is None:
            raise ValueError("jd and place are required for rasi-bhukthi at L2.")
        planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
        maha_lord_rasi = planet_positions[parent_lord + 1][1][0]
        rasi_bhuktis = _vimsottari_rasi_bhukthi(parent_lord, maha_lord_rasi, start_jd)
        if not rasi_bhuktis:
            return []

        items = list(rasi_bhuktis.items())
        for idx, (child_lord, child_start_jd) in enumerate(items):
            child_end_jd = end_jd if idx == len(items) - 1 else items[idx + 1][1]
            children.append([
                path + (child_lord,),
                _jd_to_tuple(child_start_jd),
                _jd_to_tuple(child_end_jd),
            ])

        if children:
            children[-1][2] = _jd_to_tuple(end_jd)
        return children

    lord, dirn = _start_lord_and_dir(parent_lord, antardhasa_option)
    H = float(human_life_span_for_vimsottari_dhasa)
    jd_cursor = start_jd

    for idx in range(len(const.vimsottari_adhipati_list)):
        Y = float(vimsottari_dict[lord])
        child_years = parent_years * (Y / H)
        child_end_jd = end_jd if idx == len(const.vimsottari_adhipati_list) - 1 else jd_cursor + child_years * year_duration

        children.append([
            path + (lord,),
            _jd_to_tuple(jd_cursor),
            _jd_to_tuple(child_end_jd),
        ])

        jd_cursor = child_end_jd
        if jd_cursor >= end_jd:
            break
        lord = vimsottari_next_adhipati(lord, direction=dirn)

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)
    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd,
    place,
    dhasa_level_index=6,
    *,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Vimśottarī-specific runner that finds the running daśā at the requested depth.
    Returns full running ladder.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    def _normalize_level1_rows_for_utils(maha_rows):
        out = []
        for row in maha_rows:
            if isinstance(row, (list, tuple)) and len(row) == 2:
                lords_any, start_t = row
            elif isinstance(row, (list, tuple)) and len(row) == 3:
                lords_any, start_t, _third = row
            else:
                raise ValueError(f"Unexpected Mahā row shape: {row}")
            out.append((_as_tuple_lords(lords_any), start_t))
        return out

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
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
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    try:
        target_depth = int(dhasa_level_index)
    except Exception:
        target_depth = 6
    target_depth = max(1, min(6, target_depth))

    _vim_bal, maha_rows_raw = get_vimsottari_dhasa_bhukthi(
        jd=jd,
        place=place,
        dhasa_level_index=1,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )
    maha_for_utils = _normalize_level1_rows_for_utils(maha_rows_raw)
    running_all = []

    rd = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    lords = _as_tuple_lords(rd[0])
    running = [lords, rd[1], rd[2]]
    running_all.append(running)
    if target_depth == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        return running_all

    antardhasa_option = kwargs.get("antardhasa_option", 1)
    use_rasi_bhukthi_variation = kwargs.get("use_rasi_bhukthi_variation", False)
    divisional_chart_factor = kwargs.get("divisional_chart_factor", 1)

    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running
        use_rasi = use_rasi_bhukthi_variation and len(parent_lords) == 1 and depth == 2

        children = vimsottari_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            antardhasa_option=antardhasa_option,
            use_rasi_bhukthi_variation=use_rasi,
            jd=jd,
            place=place,
            divisional_chart_factor=divisional_chart_factor if use_rasi else 1,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )

        if not children:
            raise ValueError("No children generated; check parent span or child generator options.")

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rd_k = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            lords_k = _as_tuple_lords(rd_k[0])
            running = [lords_k, rd_k[1], rd_k[2]]
        running_all.append(running)
    return running_all


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=3,
    antardhasa_option=1,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
        For nakshathra dhasa calculations for divisional charts - first calculate progression for raasi
        Then do varga division to progressed raasi longitudes
    """
    DLI = dhasa_level_index
    _, vd = get_vimsottari_dhasa_bhukthi(
        jd_at_dob,
        place,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        use_rasi_bhukthi_variation=use_rasi_bhukthi_variation,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        antardhasa_option=antardhasa_option,
        dhasa_starting_planet=dhasa_starting_planet,
        dhasa_level_index=DLI,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    if get_running_dhasa:
        vdc = utils.get_running_dhasa_for_given_date(jd_current, vd)
        print(vdc)
    jds = [utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0)) for _, (y, m, d, fh), _ in vd]
    planet_long = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=1,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    birth_star_index = int((planet_long % 360.0) // utils.ONE_NAK)
    prog_long = utils.progressed_abs_long_general(
        jds,
        jd_current,
        birth_star_index,
        dhasa_level_index=DLI,
        total_lords_in_dhasa=len(const.vimsottari_adhipati_list),
    )
    progression_correction = (prog_long - planet_long) % 360
    if get_running_dhasa:
        return progression_correction, vdc
    else:
        return progression_correction


'------ main -----------'
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
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    rb_var = False
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
                dhasa_level_index=DLI,
                use_rasi_bhukthi_variation=rb_var,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        _, ad = get_vimsottari_dhasa_bhukthi(
            jd_at_dob,
            place,
            dhasa_level_index=DLI,
            use_rasi_bhukthi_variation=rb_var,
            dhasa_duration_type=dd,
        )
        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                DLI,
                extract_running_period_for_all_levels=True,
            )
        )
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.vimsottari_tests()
