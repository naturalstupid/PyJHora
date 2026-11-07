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
Calculates Varsha Vimshottari (also called Mudda dasa) Dasha-bhukthi-antara-sukshma-prana.

Mudda dasa is the annual (Tajaka) form of Vimshottari dasa. It uses the
same nine planetary lords, the same fixed cyclic order, and the same
proportional shares of a 120 unit lifespan as natal Vimshottari dasa, but
the entire 120 unit lifespan is compressed into a single solar year, so
that it can be used to time events within one annual (varsha) chart.

The starting lord for a given year is found by progressing the lord of
natal Moon's nakshatra by the number of completed years since birth
(taken modulo nine); the balance of that lord's period at the start of
the year is found from how much of natal Moon's nakshatra remains to be
traversed. This progression rule is specific to Mudda dasa. All of the
child-generation logic below it (Antardasa, Pratyantardasa, Sookshma,
Prana, Deha) is identical in structure to natal Vimshottari dasa and is
provided by jhora.horoscope.dhasa.graha.vimsottari, called here with the
120-to-1-real-year compression enabled.

Every duration value returned by any public function in this module is
always expressed in real years, matching the single convention used by
jhora.horoscope.dhasa.graha.vimsottari throughout. A duration obtained
from get_dhasa_antardhasa() below may therefore be passed unchanged into
get_immediate_children() or get_running_dhasa_for_given_date() without any
additional unit conversion.
V5.0 Refactored to call vimsottari with varsha_vimsottari = True
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts
from jhora.horoscope.dhasa.graha import vimsottari
### --- Varsha Vimsottari (Mudda) lord sequence
def varsha_vimsottari_adhipati(nak):
    """Returns the Mudda dasa lord corresponding to nakshatra index `nak`."""
    return const.varsha_vimsottari_adhipati_list[nak % (len(const.varsha_vimsottari_adhipati_list))]
def varsha_vimsottari_next_adhipati(lord):
    """Returns the next lord after `lord` in the Mudda dasa cyclic order."""
    current = const.varsha_vimsottari_adhipati_list.index(lord)
    next_index = (current + 1) % len(const.varsha_vimsottari_adhipati_list)
    return const.varsha_vimsottari_adhipati_list[next_index]
def _varsha_seed_lord_and_start(
    jd_at_dob, place, years,
    divisional_chart_factor=1, chart_method=1,
    dhasa_duration_type=None, savana_year_method=None,
):
    """
    Finds the Mudda dasa lord running at the start of the given year of
    life, and its exact start date.

    `years` is 1-indexed: years=1 is the birth year itself (varsha
    pravesh coincides with birth, zero completed years elapsed), years=2
    is the second year of life (one completed year elapsed), and so on --
    matching how a year of life is ordinarily counted. The completed-years
    count used in the seed-progression rule below is therefore
    (years - 1).

    The starting lord is the lord of natal Moon's nakshatra, progressed by
    the number of completed years (years - 1, modulo nine). The balance of
    that lord's period already elapsed is proportional to how much of
    natal Moon's nakshatra has been traversed, using the same
    120-to-1-real-year compression used for every other level of the
    dasa. For years=1 (the birth year), completed years elapsed is zero,
    so the seed lord and its balance reduce to the natal Vimshottari
    mahadasa lord and balance directly, only time-compressed to a single
    year instead of spread across a lifetime.
    """
    one_star = 360 / 27.0
    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )
    moon_long = planet_positions[2][1][0] * 30 + planet_positions[2][1][1]
    nak = int(moon_long / one_star)
    rem = moon_long - nak * one_star
    natal_lord_index = vimsottari.vimsottari_adhipati(nak)
    completed_years = years - 1
    lord_index = (natal_lord_index + completed_years) % 9
    lord = const.varsha_vimsottari_adhipati_list[lord_index]
    raw_year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob, place=place,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
    )
    lord_period_days = (vimsottari.vimsottari_dict[lord] / float(vimsottari.human_life_span_for_vimsottari_dhasa)) * raw_year_duration
    fraction_elapsed = rem / one_star
    period_elapsed_days = fraction_elapsed * lord_period_days
    start_jd = jd_at_dob + completed_years * raw_year_duration - period_elapsed_days
    return lord, start_jd
### --- Public API
def get_dhasa_antardhasa(
    dob, tob, place,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha, 2=+Antara [default], 3..6 deeper)
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Calculates Varsha Vimshottari (Mudda dasa) Dasha-bhukthi-antara-sukshma-prana.

    @param years: 1-indexed year of life (years=1 is the birth year,
        years=2 the second year of life, and so on); determines which
        varsha's Mudda dasa cycle is calculated.
    @param dhasa_level_index: depth of the dasa hierarchy to return, 1..6
        (1=Maha, 2=Antara/Bhukti [default], 3=Pratyantara, 4=Sookshma,
        5=Prana, 6=Deha).
    @param round_duration: if True, each duration is rounded to a fixed
        number of decimal places that increases with depth. Durations are
        expressed in real years and shrink rapidly at deeper levels (a
        Deha-level duration can be a small fraction of a day), so a fixed
        small number of decimal places would round some of them away to
        zero; internal date calculations always retain full precision
        regardless of this setting.
    @return: list of (lords_tuple, (Y, M, D, fractional_hour), duration_in_years)
        tuples. Duration is always expressed in real years -- the same
        convention used by get_immediate_children() and
        get_running_dhasa_for_given_date() below -- so a row returned here
        (start date and duration) can be used directly wherever a real
        year duration is expected elsewhere in this module.
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")
    seed_lord, seed_start_jd = _varsha_seed_lord_and_start(
        jd_at_dob, place, years,
        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
    )
    _, rows = vimsottari.get_dhasa_antardhasa(
        dob, tob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_level_index=dhasa_level_index,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        varsha_vimsottari=True,
        seed_lord_and_start=(seed_lord, seed_start_jd),
        return_exact_bounds=False,
    )
    # Each row's duration is already expressed in real years (a small
    # fraction, since the 120 unit lifespan is compressed into one real
    # year inside vimsottari.get_dhasa_antardhasa), so it is returned here
    # unchanged -- no unit conversion -- keeping a single real-year
    # convention throughout this module.
    decimals = 4 + 2 * (dhasa_level_index - 1)
    dhasa_bukthi = []
    for lords_tuple, start_tuple, dur_years_real in rows:
        dur_ret = round(float(dur_years_real), decimals) if round_duration else float(dur_years_real)
        dhasa_bukthi.append((lords_tuple, start_tuple, dur_ret))
    return dhasa_bukthi
def mudda_dhasa_bhukthi(dob, tob, place, years, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                        divisional_chart_factor=1, dhasa_duration_type=None, savana_year_method=None):
    return get_dhasa_antardhasa(dob, tob, place, years, dhasa_level_index=dhasa_level_index,
                                 divisional_chart_factor=divisional_chart_factor,
                                 dhasa_duration_type=dhasa_duration_type,
                                 savana_year_method=savana_year_method)
def immediate_children(parent_lords, parent_start, parent_duration=None, parent_end=None, **kwargs):
    return get_immediate_children(parent_lords, parent_start, parent_duration, parent_end, **kwargs)
def get_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns the immediate children of one Mudda dasa period, one level down.
    Provide exactly one of parent_duration (in real years) or parent_end
    (an exact end date). parent_duration, when given directly, must be
    expressed in real years -- the same value returned by
    get_dhasa_antardhasa() above -- so a row's duration can be passed
    straight back into this function unchanged to expand it further.
    """
    return vimsottari.get_immediate_children(
        parent_lords, parent_start, parent_duration, parent_end,
        jd_at_dob=jd_at_dob, place=place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs,
    )
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,   # 1..6
    *,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Finds the running Mudda dasa ladder at `current_jd`, down to the
    requested depth:
      [
        [(L1,),                  start1, end1],
        [(L1,L2),                start2, end2],
        ...
        [(L1,..,L_d),            startd, endd]
      ]

    @param years: 1-indexed year of life (years=1 is the birth year,
        years=2 the second year of life, and so on) for the varsha whose
        Mudda dasa cycle should be examined.
    """
    seed_lord, seed_start_jd = _varsha_seed_lord_and_start(
        jd_at_dob, place, years,
        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
    )
    return vimsottari.get_running_dhasa_for_given_date(
        current_jd, jd_at_dob, place, dhasa_level_index,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        varsha_vimsottari=True,
        seed_lord_and_start=(seed_lord, seed_start_jd),
        **kwargs,
    )
'------ main -----------'
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7); tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':')); fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    md_rows = get_dhasa_antardhasa(dob,tob,place,dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    for lords,start,durn in md_rows:
        print(utils.PLANET_NAMES[lords[0]],f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])} {durn}")
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    _years = utils.jd_to_gregorian(current_jd)[0] - utils.jd_to_gregorian(jd_at_dob)[0]
    for dd in const.DHASA_YEAR_DURATION:
        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("-" * 80)
        print("Dehā (ladder):", get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=DLI, years=_years, dhasa_duration_type=dd))
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.mudda_varsha_vimsottari_tests()
