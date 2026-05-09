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
from jhora.horoscope.chart import house, charts
from jhora.horoscope.dhasa.raasi import narayana
from jhora.panchanga import drik

""" Also called Lagna Kendradi Rasi Dhasa """

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


def moola_dhasa(
    dob, tob, place,
    divisional_chart_factor=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Lagna Kendraadhi Daśā (a.k.a. Moola Daśā) — depth-enabled (Maha → Antara → …)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    start_jd = utils.julian_day_number(dob, tob)
    _set_year_duration(start_jd, place, dhasa_duration_type, savana_year_method)

    pp = charts.divisional_chart(
        start_jd, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh = (asc_house + 7 - 1) % 12
    seed_sign = house.stronger_rasi_from_planet_positions(pp, asc_house, seventh)

    if p_to_h.get(const.SATURN_ID, -1) == seed_sign:
        direction = 1
    elif p_to_h.get(const.KETU_ID, -1) == seed_sign:
        direction = -1
    elif seed_sign in const.odd_signs:
        direction = 1
    else:
        direction = -1

    ks = sum(house.kendras()[:3], [])
    dhasa_progression = [(seed_sign + direction * (k - 1)) % 12 for k in ks]

    def _maha_duration(rasi):
        return float(narayana._dhasa_duration(pp, rasi))

    def _antara_order(parent_sign):
        return _antardhasa(parent_sign, p_to_h)

    _round_ndigits = max(0, int(getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)))

    def _recurse(level, parent_sign, parent_start_jd, parent_years, prefix, out_rows, totals):
        child_years = parent_years / 12.0
        jd_cursor = parent_start_jd
        for child_sign in _antara_order(parent_sign):
            if level < dhasa_level_index:
                _recurse(level + 1, child_sign, jd_cursor, child_years, prefix + (child_sign,), out_rows, totals)
            else:
                start_str = utils.julian_day_to_date_time_string(jd_cursor)
                dur_out = round(child_years, _round_ndigits) if round_duration else child_years
                out_rows.append(prefix + (child_sign, start_str, dur_out))
                totals['years'] += child_years
                if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                    totals['stop'] = True
                    return
            jd_cursor += child_years * year_duration
            if totals.get('stop'):
                return

    rows = []
    jd_cursor = start_jd
    totals = {'years': 0.0, 'stop': False}

    for md_sign in dhasa_progression:
        if totals['stop']:
            break
        md_years = _maha_duration(md_sign)

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                md_sign,
                utils.julian_day_to_date_time_string(jd_cursor),
                round(md_years, _round_ndigits) if round_duration else md_years
            ))
            totals['years'] += md_years
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break
            jd_cursor += md_years * year_duration

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ad_years = md_years / 12.0
            jd_b = jd_cursor
            for ad_sign in _antara_order(md_sign):
                rows.append((
                    md_sign, ad_sign,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(ad_years, _round_ndigits) if round_duration else ad_years
                ))
                totals['years'] += ad_years
                if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                    jd_cursor = jd_b + ad_years * year_duration
                    break
                jd_b += ad_years * year_duration
            jd_cursor = jd_b
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break

        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=md_sign,
                parent_start_jd=jd_cursor,
                parent_years=md_years,
                prefix=(md_sign,),
                out_rows=rows,
                totals=totals
            )
            if totals['stop']:
                break
            jd_cursor += md_years * year_duration

    if totals['years'] >= const.human_life_span_for_narayana_dhasa:
        return rows

    for _, md_sign in enumerate(dhasa_progression):
        if totals['stop']:
            break
        first_md = _maha_duration(md_sign)
        md2_years = 12.0 - first_md
        if md2_years <= 0:
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((
                md_sign,
                utils.julian_day_to_date_time_string(jd_cursor),
                round(md2_years, _round_ndigits) if round_duration else md2_years
            ))
            totals['years'] += md2_years
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break
            jd_cursor += md2_years * year_duration

        elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            ad_years = md2_years / 12.0
            jd_b = jd_cursor
            for ad_sign in _antara_order(md_sign):
                rows.append((
                    md_sign, ad_sign,
                    utils.julian_day_to_date_time_string(jd_b),
                    round(ad_years, _round_ndigits) if round_duration else ad_years
                ))
                totals['years'] += ad_years
                if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                    jd_cursor = jd_b + ad_years * year_duration
                    break
                jd_b += ad_years * year_duration
            jd_cursor = jd_b
            if totals['years'] >= const.human_life_span_for_narayana_dhasa:
                break

        else:
            _recurse(
                level=const.MAHA_DHASA_DEPTH.ANTARA,
                parent_sign=md_sign,
                parent_start_jd=jd_cursor,
                parent_years=md2_years,
                prefix=(md_sign,),
                out_rows=rows,
                totals=totals
            )
            if totals['stop']:
                break
            jd_cursor += md2_years * year_duration

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
    dcf = 1

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)

        start_time = time.time()
        ad = moola_dhasa(
            dob, tob, place,
            divisional_chart_factor=dcf,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd
        )
        print(utils.get_running_dhasa_at_all_levels_for_given_date(
            current_jd, ad, const.MAHA_DHASA_DEPTH.DEHA,
            extract_running_period_for_all_levels=True,
            dhasa_cycle_count=1
        ))
        print('old/full-list method elapsed time', time.time() - start_time)

    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.moola_dhasa_test()
