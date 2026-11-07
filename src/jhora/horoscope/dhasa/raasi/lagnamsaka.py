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
Lagnamsaka Dasa.

Reference:
- P.V.R. Narasimha Rao
- Sanjay Rath

Release History
----------------
    V5.0 - Refactored to match JHora
"""
from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.horoscope.dhasa.raasi import narayana
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy


def _lagnamsaka_dhasa_seed_sign(jd_at_dob, place, divisional_chart_factor=9, chart_method=1, **kwargs):
    """Return the Lagnamsaka seed sign."""
    varga_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_positions)
    candidate_sign = p_to_h_varga[const._ascendant_symbol]
    rasi_positions = charts.rasi_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    return narayana._seed_from_candidate_sign(rasi_positions, candidate_sign)


def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=9,
    chart_method=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """Return dhasa/antardhasa periods."""
    jd_at_dob = utils.julian_day_number(dob, tob)
    seed_sign = _lagnamsaka_dhasa_seed_sign(jd_at_dob, place, divisional_chart_factor, chart_method, **kwargs)
    rasi_planet_positions = charts.rasi_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    return narayana._narayana_dhasa_calculation(
        rasi_planet_positions, seed_sign, dob, tob, place,
        years=years, months=months, sixty_hours=sixty_hours,
        varsha_narayana=varsha_narayana,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_method=dhasa_method,
        **kwargs
    )


def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """Return immediate child periods for a parent dasha."""
    return narayana.get_immediate_children(
        parent_lords, parent_start,
        parent_duration=parent_duration, parent_end=parent_end,
        jd_at_dob=jd_at_dob, place=place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_method=dhasa_method,
        **kwargs
    )


def get_running_dhasa_for_given_date(
    jd_given, jd_at_dob, place,
    divisional_chart_factor=9,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    years=1, months=1, sixty_hours=1,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """Return the running dhasa sequence for a given date."""
    seed_sign = _lagnamsaka_dhasa_seed_sign(jd_at_dob, place, divisional_chart_factor, chart_method, **kwargs)
    return narayana.get_running_dhasa_for_given_date(
        jd_given, jd_at_dob, place,
        divisional_chart_factor=1,
        chart_method=chart_method,
        dhasa_level_index=dhasa_level_index,
        years=years, months=months, sixty_hours=sixty_hours,
        varsha_narayana=varsha_narayana,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_method=dhasa_method,
        dhasa_seed_sign_override=seed_sign,
        **kwargs
    )


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    _dhasa_method = const.NARAYANA_OPTION.PVR_BOOK

    print("--- Lagnamsaka (D-9) Maha Dasas ---")
    db_maha = get_dhasa_antardhasa(dob, tob, place,
                    divisional_chart_factor=9,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
                    dhasa_method=_dhasa_method)
    for (lord,), start_date, durn in db_maha:
        y, m, d, fh = start_date
        print(utils.RAASI_SHORT_LIST[lord], f"{y}-{m:02d}-{d:02d}", utils.to_dms(fh), durn)

    print("\n--- Lagnamsaka (D-9) MD>AD sequence ---")
    db = get_dhasa_antardhasa(dob, tob, place,
                    divisional_chart_factor=9,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                    dhasa_method=_dhasa_method)
    md_ad_seq = {}
    for lords, start_date, durn in db:
        lord, sub_lord = lords
        lord_name = utils.RAASI_SHORT_LIST[lord]
        if lord_name not in md_ad_seq:
            md_ad_seq[lord_name] = []
        md_ad_seq[lord_name].append(utils.RAASI_SHORT_LIST[sub_lord])
    md_ad_seq = {k: ','.join(v) for k, v in md_ad_seq.items()}
    for lord, sub_lord_seq in md_ad_seq.items():
        print(lord, " > ", md_ad_seq[lord])

    print("\n--- Lagnamsaka (D-9) running dasha chain for 1998-11-09 15:29:45 ---")
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    grd = get_running_dhasa_for_given_date(
        current_jd, jd_at_dob, place,
        divisional_chart_factor=9,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
        dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR,
        dhasa_method=_dhasa_method,
    )
    for lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2) in grd:
        label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
        print(f"{label:20s} {y1}-{m1:02d}-{d1:02d} {utils.to_dms(fh1)}  ->  {y2}-{m2:02d}-{d2:02d} {utils.to_dms(fh2)}")
