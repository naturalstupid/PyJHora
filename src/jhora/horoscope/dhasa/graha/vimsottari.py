
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

year_duration = const.sidereal_year  # const.tropical_year  # some say 360 days, others 365.25 or 365.2563 etc

vimsottari_adhipati = (
    lambda nak, seed_star=3: const.vimsottari_adhipati_list[
        (nak - seed_star + 3) % (len(const.vimsottari_adhipati_list))
    ]
)

# IMPORTANT: decouple from const to avoid mutating the library-wide constants object
vimsottari_dict = const.vimsottari_dict.copy()

human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa


### --- Vimsottari functions
def vimsottari_next_adhipati(lord, dir=1):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + dir) % len(const.vimsottari_adhipati_list)
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
    """Returns the start date of the mahadasa which occured on or before `jd`"""
    y, m, d, fh = utils.jd_to_gregorian(jd)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)
    one_star = (360 / 27.0)  # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts, sphuta

    _special_planets = ["M", "G", "T", "I", "B", "I", "P"]
    planet_positions = charts.divisional_chart(
        jd, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method
    )[:const._pp_count_upto_ketu]

    if dhasa_starting_planet in const.SUN_TO_KETU:
        planet_long = (
            planet_positions[dhasa_starting_planet + 1][1][0] * 30
            + planet_positions[dhasa_starting_planet + 1][1][1]
        )
    elif dhasa_starting_planet == const._ascendant_symbol:
        planet_long = planet_positions[0][1][0] * 30 + planet_positions[0][1][1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == "M":
        mn = drik.maandi_longitude(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0] * 30 + mn[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == "G":
        gl = drik.gulika_longitude(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0] * 30 + gl[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == "B":
        gl = drik.bhrigu_bindhu_lagna(
            jd, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method
        )
        planet_long = gl[0] * 30 + gl[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == "I":
        gl = drik.indu_lagna(
            jd, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method
        )
        planet_long = gl[0] * 30 + gl[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == "P":
        gl = drik.pranapada_lagna(jd, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0] * 30 + gl[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == "T":
        sp = sphuta.tri_sphuta(dob, tob, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method)
        planet_long = sp[0] * 30 + sp[1]
    else:
        planet_long = planet_positions[2][1][0] * 30 + planet_positions[2][1][1]

    if dhasa_starting_planet == 1:
        planet_long += (star_position_from_moon - 1) * one_star

    nak = int(planet_long / one_star)
    rem = (planet_long - nak * one_star)
    lord = vimsottari_adhipati(nak, seed_star)  # ruler of current nakshatra
    period = vimsottari_dict[lord]              # total years of nakshatra lord

    period_elapsed = rem / one_star * period  # years
    period_elapsed *= year_duration           # days
    start_date = jd - period_elapsed          # so many days before current day
    return [lord, start_date]


def vimsottari_mahadasa(
    jd, place, divisional_chart_factor=1, chart_method=1, star_position_from_moon=1, seed_star=3, dhasa_starting_planet=1
):
    """List all mahadashas and their start dates"""
    lord, start_date = vimsottari_dasha_start_date(
        jd, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet
    )
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        start_date += vimsottari_dict[lord] * year_duration
        lord = vimsottari_next_adhipati(lord)

    return retval


def _vimsottari_rasi_bhukthi(maha_lord, maha_lord_rasi, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa using rasi bhukthi variation
    and its start date"""
    retval = Dict()
    bhukthi_duration = vimsottari_dict[maha_lord] / 12
    for bhukthi_rasi in [(maha_lord_rasi + h) % 12 for h in range(12)]:
        retval[bhukthi_rasi] = start_date
        start_date += bhukthi_duration * year_duration
    return retval


def _vimsottari_bhukti(maha_lord, start_date, antardhasa_option=1):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa and its start date"""
    global human_life_span_for_vimsottari_dhasa, vimsottari_dict
    lord = maha_lord
    if antardhasa_option in [3, 4]:
        lord = vimsottari_next_adhipati(lord, dir=1)
    elif antardhasa_option in [5, 6]:
        lord = vimsottari_next_adhipati(lord, dir=-1)
    dir = 1 if antardhasa_option in [1, 3, 5] else -1
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa
        start_date += factor * year_duration
        lord = vimsottari_next_adhipati(lord, dir)

    return retval


# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def _vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukti's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    global human_life_span_for_vimsottari_dhasa, vimsottari_dict
    lord = bhukti_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * (vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa)
        factor *= (vimsottari_dict[bhukti_lord] / human_life_span_for_vimsottari_dhasa)
        start_date += factor * year_duration
        lord = vimsottari_next_adhipati(lord)

    return retval


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(list(some_dict.keys())):
        if some_dict[key] < jd:
            return key


def compute_vimsottari_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = _where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = _vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = _where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = _vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)


def get_vimsottari_dhasa_bhukthi(
    jd, place,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    use_rasi_bhukthi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=3,
    antardhasa_option=1,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara, 3=+Pratyantara, 4=+Sookshma, 5=+Prana, 6=+Deha)
    round_duration=True                                # kept for parity; this function returns no durations
):
    """
        provides Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)

        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param use_tribhagi_variation: False (default), True means tribhagi behavior (your legacy):
               scales human_life_span_for_vimsottari_dhasa & vimsottari_dict; increases cycles
        @param use_rasi_bhukthi_variation: Default False. True gives rasi-bhukthi variation at L2 (only)
        @param star_position_from_moon: 1=Moon (default), 4=Kshema, 5=Utpanna, 8=Adhana
        @param divisional_chart_factor: Default=1 (1=Raasi, 9=Navamsa)
        @param chart_method: various chart methods (see charts module)
        @param seed_star: 1..27 (Default=3)
        @param antardhasa_option (ignored for rasi-bhukthi at L2):
               1 => dhasa lord - forward (Default)
               2 => dhasa lord - backward
               3 => next dhasa lord - forward
               4 => next dhasa lord - backward
               5 => prev dhasa lord - forward
               6 => prev dhasa lord - backward
        @param dhasa_starting_planet: 0=Sun ... 8=Ketu, 'L','M','G','T','B','I','P'
        @param dhasa_level_index: depth 1..6
        @param round_duration: reserved (this function returns no durations)

        @return: (vim_bal, dhasa_bhukthi)

          if dhasa_level_index == 1:
              dhasa_bhukthi -> [ [l1, start_str], ... ]
          elif dhasa_level_index == 2:
              dhasa_bhukthi -> [ [l1, l2, start_str], ... ]        # honors use_rasi_bhukthi_variation at L2
          else (>=3):
              dhasa_bhukthi -> [ [l1, l2, l3, ..., start_str], ... ]  # variable length rows, no durations
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    global human_life_span_for_vimsottari_dhasa, vimsottari_dict

    # ---- SNAPSHOT GLOBALS (avoid cross-test leakage) -------------------
    _orig_H = human_life_span_for_vimsottari_dhasa
    _orig_dict = vimsottari_dict.copy()

    try:
        # ---- Build call-local working dict & H --------------------------
        _working_dict = _orig_dict
        if use_tribhagi_variation:
            _trib = 1.0 / 3.0
            H = _orig_H * _trib
            # scale durations inside a fresh dict (no mutation to _orig_dict)
            _working_dict = {k: round(v * _trib, 2) for k, v in _orig_dict.items()}
            _dhasa_cycles = int(1 / _trib)
        else:
            H = _orig_H
            _dhasa_cycles = 1

        # Temporarily patch module-level globals so legacy helpers see the correct values
        human_life_span_for_vimsottari_dhasa = H
        vimsottari_dict = _working_dict

        # --- Ordered MD starts (your function produces an OrderedDict) ---
        dashas = vimsottari_mahadasa(
            jd, place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            star_position_from_moon=star_position_from_moon,
            seed_star=seed_star,
            dhasa_starting_planet=dhasa_starting_planet
        )

        # Vimśottarī balance (unchanged)
        dl = list(dashas.values())
        de = dl[1]
        y, m, h, _ = utils.jd_to_gregorian(jd); p_date1 = drik.Date(y, m, h)
        y, m, h, _ = utils.jd_to_gregorian(de); p_date2 = drik.Date(y, m, h)
        vim_bal = utils.panchanga_date_diff(p_date1, p_date2)

        dhasa_bhukthi = []

        # --- helpers for L3+ planetary recursion ------------------------
        def _start_and_dir(parent_lord):
            lord = parent_lord
            if antardhasa_option in [3, 4]:
                lord = vimsottari_next_adhipati(lord, dir=+1)
            elif antardhasa_option in [5, 6]:
                lord = vimsottari_next_adhipati(lord, dir=-1)
            dirn = +1 if antardhasa_option in [1, 3, 5] else -1
            return lord, dirn

        def _children_planetary(parent_lord, parent_start_jd, parent_years):
            """Yield (child_lord, child_start_jd, child_years) for 9 children under parent_lord."""
            start_lord, dirn = _start_and_dir(parent_lord)
            jd_cursor = parent_start_jd
            lord = start_lord
            for _ in range(len(const.vimsottari_adhipati_list)):
                Y = float(vimsottari_dict[lord])  # already tribhagi-scaled if enabled
                dur_yrs = parent_years * (Y / H)
                yield (lord, jd_cursor, dur_yrs)
                jd_cursor += dur_yrs * year_duration
                lord = vimsottari_next_adhipati(lord, dir=dirn)

        # An ordered list of (md_lord, md_start_jd)
        md_items = list(dashas.items())

        for _ in range(_dhasa_cycles):
            N = len(md_items)
            for idx, (md_lord, md_start_jd) in enumerate(md_items):
                # Actual MD length from consecutive starts (handles first birth-balance accurately)
                if idx < N - 1:
                    md_end_jd = md_items[idx + 1][1]
                    md_years = (md_end_jd - md_start_jd) / year_duration
                else:
                    md_years = float(vimsottari_dict[md_lord])

                if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                    # L1: Maha only (unchanged format)
                    dhasa_bhukthi.append([md_lord, utils.julian_day_to_date_time_string(md_start_jd)])

                elif dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                    # L2: honor existing branches for Antardasha (planetary or rasi-bhukthi)
                    if use_rasi_bhukthi_variation:
                        from jhora.horoscope.chart import charts
                        planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=1)
                        maha_lord_rasi = planet_positions[md_lord + 1][1][0]
                        bhuktis = _vimsottari_rasi_bhukthi(md_lord, maha_lord_rasi, dashas[md_lord])
                    else:
                        bhuktis = _vimsottari_bhukti(md_lord, dashas[md_lord], antardhasa_option=antardhasa_option)

                    for blord, bstart in bhuktis.items():
                        dhasa_bhukthi.append([md_lord, blord, utils.julian_day_to_date_time_string(bstart)])

                elif dhasa_level_index == const.MAHA_DHASA_DEPTH.PRATYANTARA:
                    # L3: Use antara helper (only valid for planetary L2)
                    if use_rasi_bhukthi_variation:
                        raise ValueError(
                            "L3+ not supported with use_rasi_bhukthi_variation=True. "
                            "Keep depth at L2 or specify a custom L3 rule."
                        )
                    bhuktis = _vimsottari_bhukti(md_lord, dashas[md_lord], antardhasa_option=antardhasa_option)
                    for blord, bstart in bhuktis.items():
                        antara = _vimsottari_antara(md_lord, blord, bstart)
                        for alord, astart in antara.items():
                            dhasa_bhukthi.append([md_lord, blord, alord, utils.julian_day_to_date_time_string(astart)])

                else:
                    # L4..L6: generic planetary recursion with classical weights
                    if use_rasi_bhukthi_variation:
                        raise ValueError(
                            "L3+ not supported with use_rasi_bhukthi_variation=True. "
                            "Keep depth at L2 or specify a custom L3/L4 rule."
                        )

                    def _recurse(level, parent_lord, parent_start_jd, parent_years, prefix, out_rows):
                        if level < dhasa_level_index:
                            for clord, cstart, cyears in _children_planetary(parent_lord, parent_start_jd, parent_years):
                                _recurse(level + 1, clord, cstart, cyears, prefix + [clord], out_rows)
                        else:
                            for clord, cstart, _cy in _children_planetary(parent_lord, parent_start_jd, parent_years):
                                out_rows.append(prefix + [clord, utils.julian_day_to_date_time_string(cstart)])

                    _recurse(
                        level=const.MAHA_DHASA_DEPTH.PRATYANTARA,  # i.e., 3; will go to 4/5/6 as requested
                        parent_lord=md_lord,
                        parent_start_jd=md_start_jd,
                        parent_years=md_years,
                        prefix=[md_lord],
                        out_rows=dhasa_bhukthi
                    )

        return vim_bal, dhasa_bhukthi

    finally:
        # ---- RESTORE GLOBALS (guaranteed) --------------------------------
        human_life_span_for_vimsottari_dhasa = _orig_H
        vimsottari_dict = _orig_dict


'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.vimsottari_tests()
