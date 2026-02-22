
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
Calculates Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana
"""

from collections import OrderedDict as Dict
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import house

year_duration = const.sidereal_year  # const.tropical_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = const.human_life_span_for_ashtottari_dhasa

""" 
    {ashtottari adhipati:[(starting_star_number,ending_star_number),dasa_length]} 
        ashtottari longitude range: (starting_star_number-1) * 360/27 TO (ending_star_number) * 360/27
        Example: 66.67 to 120.00 = 53 deg 20 min range
"""
ashtottari_adhipathi_list = [0, 1, 2, 3, 6, 4, 7, 5]
ashtottari_adhipathi_dict_seed = {
    0: [(6, 9), 6],
    1: [(10, 12), 15],
    2: [(13, 16), 8],
    3: [(17, 19), 17],
    6: [(20, 22), 10],
    4: [(23, 25), 19],
    7: [(26, 2), 12],
    5: [(3, 5), 21],
}


def applicability_check(planet_positions):
    asc_house = planet_positions[0][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    house_of_lagna_lord = planet_positions[lagna_lord + 1][1][0]
    rahu_house = planet_positions[const.RAHU_ID + 1][1][0]
    chk1 = rahu_house in house.trines_of_the_raasi(house_of_lagna_lord) and rahu_house != asc_house
    chk2 = rahu_house in house.quadrants_of_the_raasi(house_of_lagna_lord) and rahu_house != asc_house
    return chk1 or chk2


def _get_dhasa_dict(seed_star=6):
    if seed_star == 6:
        return ashtottari_adhipathi_dict_seed
    ashtottari_adhipathi_dict = {}
    nak = seed_star
    for p, [(nb, ne), durn] in ashtottari_adhipathi_dict_seed.items():
        nak_diff = ne - nb
        nsb = nak
        nse = (nsb + nak_diff) % 28
        ashtottari_adhipathi_dict[p] = [(nsb, nse), durn]
        nak = (nse + 1) % 28
    return ashtottari_adhipathi_dict


# Initialize default mapping once so other functions are safe to call even
# if get_ashtottari_dhasa_bhukthi() hasn’t set a custom mapping yet.
ashtottari_adhipathi_dict = _get_dhasa_dict(seed_star=6)


def ashtottari_adhipathi(nak):
    global ashtottari_adhipathi_dict
    for key, value in ashtottari_adhipathi_dict.items():
        starting_star = value[0][0]
        ending_star = value[0][1]
        nak1 = nak
        if ending_star < starting_star:
            ending_star += 27
            if nak1 < starting_star:
                nak1 += 27
        if starting_star <= nak1 <= ending_star:
            return key, value


def ashtottari_dasha_start_date(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    dhasa_starting_planet=1,
):
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
        sp = sphuta.tri_sphuta(
            dob, tob, place, divisional_chart_factor=divisional_chart_factor, chart_method=chart_method
        )
        planet_long = sp[0] * 30 + sp[1]
    else:
        # Default to Moon
        planet_long = planet_positions[2][1][0] * 30 + planet_positions[2][1][1]

    if dhasa_starting_planet == 1:
        planet_long += (star_position_from_moon - 1) * one_star
    nak = int(planet_long / one_star)
    lord, res = ashtottari_adhipathi(nak + 1)  # ruler of current nakshatra
    period = res[1]
    start_nak = res[0][0]
    end_nak = res[0][1]
    period_elapsed = (planet_long - (start_nak - 1) * one_star) / ((end_nak - start_nak + 1) * one_star)
    period_elapsed *= (period * year_duration)  # days
    start_date = jd - period_elapsed  # so many days before current day
    return [lord, start_date]


def ashtottari_next_adhipati(lord, dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = ashtottari_adhipathi_list.index(lord)
    next_index = (current + dirn) % len(ashtottari_adhipathi_list)
    return ashtottari_adhipathi_list[next_index]


def ashtottari_mahadasa(
    jd, place, divisional_chart_factor=1, chart_method=1, star_position_from_moon=1, dhasa_starting_planet=1
):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    lord, start_date = ashtottari_dasha_start_date(
        jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )
    retval = Dict()
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        start_date += lord_duration * year_duration
        lord = ashtottari_next_adhipati(lord)
    return retval


def ashtottari_bhukthi(dhasa_lord, start_date, antardhasa_option=1):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa and its start date
    """
    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict
    lord = dhasa_lord
    if antardhasa_option in [3, 4]:
        lord = ashtottari_next_adhipati(dhasa_lord, dirn=1)
    elif antardhasa_option in [5, 6]:
        lord = ashtottari_next_adhipati(dhasa_lord, dirn=-1)
    dirn = 1 if antardhasa_option in [1, 3, 5] else -1
    retval = Dict()
    dhasa_lord_duration = ashtottari_adhipathi_dict[lord][1]
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        start_date += factor * year_duration
        lord = ashtottari_next_adhipati(lord, dirn)
    return retval


def ashtottari_anthara(dhasa_lord, bhukthi_lord, bhukthi_lord_start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa, its bhukthi lord and bhukthi_lord's start date
    """
    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = bhukthi_lord
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        bhukthi_lord_start_date += factor * year_duration
        lord = ashtottari_next_adhipati(lord)
    return retval


def get_ashtottari_dhasa_bhukthi(
    jd,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # NEW: 1..6
    antardhasa_option=1,
    dhasa_starting_planet=1,
    seed_star=6,
):
    """
        provides Ashtottari dhasa at selected depth for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default 1; various methods available for each divisional chart. See charts module
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param dhasa_level_index: Depth level (1..6)
            1 = Maha only (no Antardasha)
            2 = + Antardasha (Bhukthi)
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @param seed_star 1..27. Default = 6
        @return:
          If dhasa_level_index==1: [ [dhasa_lord, start_str], ... ]
          If dhasa_level_index==2: [ [dhasa_lord, bhukthi_lord, start_str], ... ]
          If dhasa_level_index>=3: [ [l1, l2, l3, ..., start_str], ... ] (variable-length lists)
    """
    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict

    # ---- SNAPSHOT GLOBALS (critical to avoid cross-test leakage) -------
    _orig_H = human_life_span_for_ashtottari_dhasa
    _orig_dict = ashtottari_adhipathi_dict.copy()

    try:
        # ---- Build a LOCAL working dict for this call -------------------
        _working_dict = _get_dhasa_dict(seed_star)

        # Compute the effective life span H for this call (don’t leak!)
        if use_tribhagi_variation:
            _trib = 1.0 / 3.0
            H = _orig_H * _trib
            # scale durations inside a fresh dict (no mutation to seed/default dict)
            _working_dict = {k: [v[0], v[1] * _trib] for k, v in _working_dict.items()}
        else:
            H = _orig_H

        # Temporarily patch the globals so that the existing helpers
        # (ashtottari_mahadasa/ashtottari_bhukthi/ashtottari_adhipathi)
        # see the right mapping and H during *this* call.
        human_life_span_for_ashtottari_dhasa = H
        ashtottari_adhipathi_dict = _working_dict

        _dhasa_cycles = 1

        dashas = ashtottari_mahadasa(
            jd,
            place,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            star_position_from_moon=star_position_from_moon,
            dhasa_starting_planet=dhasa_starting_planet,
        )

        dhasa_bhukthi = []

        # Helper: start child lord & direction for a given parent lord (mirrors antara rule)
        def _child_start_and_dir(parent_lord):
            lord = parent_lord
            if antardhasa_option in [3, 4]:
                lord = ashtottari_next_adhipati(parent_lord, dirn=1)
            elif antardhasa_option in [5, 6]:
                lord = ashtottari_next_adhipati(parent_lord, dirn=-1)
            dirn = 1 if antardhasa_option in [1, 3, 5] else -1
            return lord, dirn

        # Helper: generate one full child cycle beneath a parent, as nested partition of parent_duration
        def _children_of(parent_lord, parent_start_jd, parent_duration_years):
            """Yield (child_lord, child_start_jd, child_duration_years) for 8 segments."""
            start_lord, dirn = _child_start_and_dir(parent_lord)
            jd_cursor = parent_start_jd
            lord = start_lord
            for _ in range(len(ashtottari_adhipathi_list)):
                Y = ashtottari_adhipathi_dict[lord][1]          # child 'year share' per Ashtottari
                dur_yrs = parent_duration_years * (Y / H)       # nested partition respecting H
                yield (lord, jd_cursor, dur_yrs)
                jd_cursor += dur_yrs * year_duration
                lord = ashtottari_next_adhipati(lord, dirn)

        for _ in range(_dhasa_cycles):
            # L1: Maha only (unchanged format)
            if dhasa_level_index == 1:
                for lord in dashas:
                    jd1 = dashas[lord]
                    date_str = utils.julian_day_to_date_time_string(jd1)
                    dhasa_bhukthi.append([lord, date_str])
                continue

            # L2: Maha + Antara (reuse your current antara function)
            if dhasa_level_index == 2:
                for lord in dashas:
                    bhukthis = ashtottari_bhukthi(lord, dashas[lord], antardhasa_option)
                    for blord in bhukthis:
                        jd1 = bhukthis[blord]
                        date_str = utils.julian_day_to_date_time_string(jd1)
                        dhasa_bhukthi.append([lord, blord, date_str])
                continue

            # L3..L6: nested partition at every level using the same antara rule recursively
            def _recurse(level, parent_lord, parent_start_jd, parent_duration_yrs, prefix, out_rows):
                if level < dhasa_level_index:
                    # expand to the next level down
                    for child_lord, child_start_jd, child_dur in _children_of(parent_lord, parent_start_jd, parent_duration_yrs):
                        _recurse(level + 1, child_lord, child_start_jd, child_dur, prefix + [child_lord], out_rows)
                else:
                    # LEAF: emit a row with lords up to this level + start time
                    for child_lord, child_start_jd, child_dur in _children_of(parent_lord, parent_start_jd, parent_duration_yrs):
                        date_str = utils.julian_day_to_date_time_string(child_start_jd)
                        out_rows.append(prefix + [child_lord, date_str])

            # Expand each Maha to requested depth (3..6)
            for lord in dashas:
                maha_start = dashas[lord]
                maha_years = ashtottari_adhipathi_dict[lord][1]  # Maha duration in years
                if dhasa_level_index == 3:
                    # One level below Antara (Pratyantara): l1 + l2 + l3
                    for blord, bstart, bdur in _children_of(lord, maha_start, maha_years):
                        # Emit pratyantara rows directly
                        for plord, pstart, pdur in _children_of(blord, bstart, bdur):
                            date_str = utils.julian_day_to_date_time_string(pstart)
                            dhasa_bhukthi.append([lord, blord, plord, date_str])
                else:
                    # Generic recursion for L4..L6
                    # prefix starts with [l1]; recurse from next level
                    _recurse(
                        level=3,
                        parent_lord=lord,
                        parent_start_jd=maha_start,
                        parent_duration_yrs=maha_years,
                        prefix=[lord],
                        out_rows=dhasa_bhukthi,
                    )

        return dhasa_bhukthi

    finally:
        # ---- RESTORE GLOBALS (guaranteed, even if exceptions occur) -----
        human_life_span_for_ashtottari_dhasa = _orig_H
        ashtottari_adhipathi_dict = _orig_dict


'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.ashtottari_tests()
