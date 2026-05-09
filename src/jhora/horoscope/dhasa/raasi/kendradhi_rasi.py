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
from jhora.horoscope.dhasa.raasi import narayana
from jhora.panchanga import drik

year_duration = const.sidereal_year
""" Also called Lagna Kendradi Raasi Dhasa """
""" This file also finds Karaka Kendraddi Rasi Dasa - See karaka_kendradhi_rasi_dhasa() """


def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    """Resolve and cache the daśā year duration used by this module."""
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def lagna_kendradhi_rasi_dhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    return kendradhi_rasi_dhasa(
        dob,
        tob,
        place,
        divisional_chart_factor,
        dhasa_level_index,
        round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )


def kendradhi_rasi_dhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kendraadhi Rāśi Daśā with multi-level depth (Maha → Antara → …)

    Depth control:
      1 = MAHA_DHASA_ONLY          -> (l1,                 start_str, dur_years)
      2 = ANTARA                   -> (l1, l2,             start_str, dur_years)  [DEFAULT]
      3 = PRATYANTARA              -> (l1, l2, l3,         start_str, dur_years)
      4 = SOOKSHMA                 -> (l1, l2, l3, l4,     start_str, dur_years)
      5 = PRANA                    -> (l1, l2, l3, l4, l5, start_str, dur_years)
      6 = DEHA                     -> (l1, l2, l3, l4, l5, l6, start_str, dur_years)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(
        jd_at_dob,
        place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs,
    )[:const._pp_count_upto_ketu]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)

    asc_house = p_to_h[const._ascendant_symbol]
    seventh_house = (asc_house + const.HOUSE_7) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(
        planet_positions,
        asc_house,
        seventh_house,
    )

    if p_to_h[const.SATURN_ID] == dhasa_seed_sign:
        direction = 1
    elif p_to_h[const.KETU_ID] == dhasa_seed_sign:
        direction = -1
    elif dhasa_seed_sign in const.odd_signs:
        direction = 1
    else:
        direction = -1

    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [(dhasa_seed_sign + direction * (k - 1)) % 12 for k in ks]

    def _children(parent_sign):
        return _antardhasa(parent_sign, p_to_h)

    def _emit_period(lords_tuple, start_jd, dur_years, out_rows):
        start_str = utils.jd_to_gregorian(start_jd)
        dur_out = round(dur_years, dhasa_level_index + 1) if round_duration else dur_years
        out_rows.append((lords_tuple, start_str, dur_out))
        return start_jd + dur_years * year_duration

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        child_years = parent_years / 12.0
        jd_cursor = parent_start_jd
        for child_sign in _children(parent_sign):
            if level < dhasa_level_index:
                _recurse(level + 1, child_sign, jd_cursor, child_years, prefix + (child_sign,), out_rows)
                jd_cursor += child_years * year_duration
            else:
                jd_cursor = _emit_period(prefix + (child_sign,), jd_cursor, child_years, out_rows)

    rows = []
    start_jd = jd_at_dob

    for dhasa_lord in dhasa_progression:
        dd = float(narayana._dhasa_duration(planet_positions, dhasa_lord))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            start_jd = _emit_period((dhasa_lord,), start_jd, dd, rows)

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                jd_b = _emit_period((dhasa_lord, bhukthi_lord), jd_b, ddb, rows)
            start_jd = jd_b

        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd, (dhasa_lord,), rows)
            start_jd += dd * year_duration

    for dhasa_lord in dhasa_progression:
        first_dd = float(narayana._dhasa_duration(planet_positions, dhasa_lord))
        dd2 = 12.0 - first_dd
        if dd2 < 0.0:
            dd2 = 0.0

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            start_jd = _emit_period((dhasa_lord,), start_jd, dd2, rows)

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd2 / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                jd_b = _emit_period((dhasa_lord, bhukthi_lord), jd_b, ddb, rows)
            start_jd = jd_b

        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd2, (dhasa_lord,), rows)
            start_jd += dd2 * year_duration

    return rows


def karaka_kendradhi_rasi_dhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    karaka_index=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Kāraka Kendraadhi Rāśi Daśā with multi-level depth.
    """
    if karaka_index not in range(1, 9):
        print('Karaka Index should be in the range (1..8). Index 1 assumed')
        karaka_index = 1

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(
        jd_at_dob,
        place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    planet_positions = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        **kwargs,
    )[:const._pp_count_upto_ketu]

    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    ak = house.chara_karakas(planet_positions)[karaka_index - 1]
    ak_house = p_to_h[ak]
    seventh_house = (ak_house + const.HOUSE_7) % 12
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, ak_house, seventh_house)

    if p_to_h[const.SATURN_ID] == dhasa_seed_sign:
        direction = 1
    elif p_to_h[const.KETU_ID] == dhasa_seed_sign:
        direction = -1
    elif dhasa_seed_sign in const.odd_signs:
        direction = 1
    else:
        direction = -1

    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [(dhasa_seed_sign + direction * (k - 1)) % 12 for k in ks]

    def _children(parent_sign):
        return _antardhasa(parent_sign, p_to_h)

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows):
        child_years = parent_years / 12.0
        jd_cursor = parent_start_jd
        for child_sign in _children(parent_sign):
            if level < dhasa_level_index:
                _recurse(level + 1, child_sign, jd_cursor, child_years, prefix + (child_sign,), out_rows)
            else:
                start_str = utils.jd_to_gregorian(jd_cursor)
                dur_ret = round(child_years, dhasa_level_index + 1) if round_duration else child_years
                out_rows.append((prefix + (child_sign,), start_str, dur_ret))
            jd_cursor += child_years * year_duration

    rows = []
    start_jd = jd_at_dob

    for dhasa_lord in dhasa_progression:
        dd = float(narayana._dhasa_duration(planet_positions, dhasa_lord))

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(dd, dhasa_level_index + 1) if round_duration else dd,
            ))
            start_jd += dd * year_duration
        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                rows.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_b),
                    round(ddb, dhasa_level_index + 1) if round_duration else ddb,
                ))
                jd_b += ddb * year_duration
            start_jd += dd * year_duration
        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd, (dhasa_lord,), rows)
            start_jd += dd * year_duration

    for dhasa_lord in dhasa_progression:
        first_dd = float(narayana._dhasa_duration(planet_positions, dhasa_lord))
        dd2 = 12.0 - first_dd
        if dd2 <= 0:
            dd2 = 0.0

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                (dhasa_lord,),
                utils.jd_to_gregorian(start_jd),
                round(dd2, dhasa_level_index + 1) if round_duration else dd2,
            ))
            start_jd += dd2 * year_duration
        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ddb = dd2 / 12.0
            jd_b = start_jd
            for bhukthi_lord in _children(dhasa_lord):
                rows.append((
                    (dhasa_lord, bhukthi_lord),
                    utils.jd_to_gregorian(jd_b),
                    round(ddb, dhasa_level_index + 1) if round_duration else ddb,
                ))
                jd_b += ddb * year_duration
            start_jd += dd2 * year_duration
        else:
            _recurse(const.MAHA_DHASA_DEPTH.ANTARA, dhasa_lord, start_jd, dd2, (dhasa_lord,), rows)
            start_jd += dd2 * year_duration

    return rows


def _antardhasa(antardhasa_seed_rasi, p_to_h):
    direction = -1
    if p_to_h[const.SATURN_ID] == antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs:
        direction = 1
    if p_to_h[const.KETU_ID] == antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi + direction * i) % 12 for i in range(12)]


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
    dcf = 1

    # Exercise all supported daśā-year duration methods, matching the newer module test pattern.
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

        # Lagna/Kendradhi path
        start_time = time.time()
        ad = kendradhi_rasi_dhasa(
            dob,
            tob,
            place,
            divisional_chart_factor=dcf,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
        )
        print(
            "Kendradhi/Lagna:",
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                DLI,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=2,
            ),
        )
        print('kendradhi elapsed time', time.time() - start_time)

        # Karaka-Kendradhi path in this same module
        start_time = time.time()
        ad_karaka = karaka_kendradhi_rasi_dhasa(
            dob,
            tob,
            place,
            divisional_chart_factor=dcf,
            karaka_index=1,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
        )
        print(
            "Karaka-Kendradhi:",
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad_karaka,
                DLI,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=2,
            ),
        )
        print('karaka-kendradhi elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kendradhi_rasi_test()
