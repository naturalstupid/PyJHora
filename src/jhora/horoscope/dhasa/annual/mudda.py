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
Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
"""

import datetime
from collections import OrderedDict as Dict
import swisseph as swe
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts
from jhora.horoscope.dhasa.graha import vimsottari
year_duration = const.tropical_year#const.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
varsha_vimsottari_adhipati = lambda nak: const.varsha_vimsottari_adhipati_list[nak % (len(const.varsha_vimsottari_adhipati_list))]

### --- Vimoshatari functions
def varsha_vimsottari_next_adhipati(lord):
    """Returns next element after `lord` in the adhipati_list"""
    current = const.varsha_vimsottari_adhipati_list.index(lord)
    next_index = (current + 1) % len(const.varsha_vimsottari_adhipati_list)
    next_lord = const.varsha_vimsottari_adhipati_list[next_index]
    return next_lord

def varsha_vimsottari_dasha_start_date(jd,place,years,divisional_chart_factor=1,chart_method=1):
    """Returns the start date of the mahadasa which occured on or before `jd`"""
    from jhora.horoscope.chart import charts
    one_star = (360 / 27.)
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method)
    moon = planet_positions[2][1][0]*30+planet_positions[2][1][1]#+(star_position_from_moon-1)*one_star
    nak = int(moon / one_star); rem = (moon - nak * one_star)
    lord = vimsottari.vimsottari_adhipati(nak) #vimsottari_dasha_start_date(jd,place)[0]
    lord = (lord+years) % 9
    lord = const.varsha_vimsottari_adhipati_list[lord]
    period = const.varsha_vimsottari_days[lord]       # total years of nakshatra lord
    period_elapsed = (rem / one_star) * period # yet to be traversed in days
    start_date = jd +years*year_duration - period_elapsed      # so many days before current day
    return [lord, start_date]

def varsha_vimsottari_mahadasa(jdut1,place,years,divisional_chart_factor=1,chart_method=1):
    """List all mahadashas and their start dates"""
    lord, start_date = varsha_vimsottari_dasha_start_date(jdut1,place,years,
                                divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
    retval = []
    for i in range(9):
        duration = const.varsha_vimsottari_days[lord] * year_duration / 360.0
        retval.append((lord,start_date,duration))
        start_date += duration
        lord = varsha_vimsottari_next_adhipati(lord)
    return retval

def varsha_vimsottari_bhukti(maha_lord, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    retval = []
    for i in range(9):
        factor = const.varsha_vimsottari_days[lord] * const.varsha_vimsottari_days[maha_lord] / const.human_life_span_for_varsha_vimsottari_dhasa
        duration = factor * year_duration / 360.0
        retval.append((lord,start_date,round(duration,2)))
        start_date += duration
        lord = varsha_vimsottari_next_adhipati(lord)
    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def varsha_vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = []
    for i in range(9):
        factor = const.varsha_vimsottari_days[lord] * (const.varsha_vimsottari_days[maha_lord] / const.human_life_span_for_varsha_vimsottari_dhasa)
        duration = factor * (const.varsha_vimsottari_days[bhukti_lord] / const.human_life_span_for_varsha_vimsottari_dhasa)
        retval.append((lord,start_date,round(duration,2)))
        start_date += duration
        lord = varsha_vimsottari_next_adhipati(lord)
    return retval


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


def compute_varsha_vimsottari_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = _where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = varsha_vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = _where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = varsha_vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)

# ---------------------- ALL TESTS ------------------------------


def varsha_vimsottari_dhasa_bhukthi(
    jd, place, years,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha, 2=+Antara [default], 3..6 deeper)
    round_duration=True                               # round only returned duration; JD math stays full precision
):
    """
        Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana

        @param jd: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param years: # years from year of birth

        Depth control (replaces include_antardhasa):
            dhasa_level_index: 1..6
              1 = Maha only                     -> (l1,               date_str, dur_days)
              2 = + Antara (Bhukti) [default]  -> (l1, l2,           date_str, dur_days)
              3 = + Pratyantara                 -> (l1, l2, l3,       date_str, dur_days)
              4 = + Sookshma                    -> (l1, l2, l3, l4,   date_str, dur_days)
              5 = + Prana                       -> (l1, l2, l3, l4, l5, date_str, dur_days)
              6 = + Deha                        -> (l1, l2, l3, l4, l5, l6, date_str, dur_days)

        @param round_duration: If True, only the returned duration is rounded
                               (all internal JD math uses full precision).

        @return: list of tuples per the shapes above.
                 Example (L2): [(7, 7, '1993-06-03 00:00:00 AM', 8.22), (7, 4, '1993-06-11 00:00:00 AM', 7.31), ...]
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # Build maha sequence (each item = (lord, start_jd, duration_days))
    dashas = varsha_vimsottari_mahadasa(
        jd, place, years,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method
    )

    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    def _fmt(jdx):
        # Keep your module’s unified timestamp style
        return utils.julian_day_to_date_time_string(jdx)

    def _children_planetary(parent_lord, parent_start_jd, parent_dur_days):
        """
        Split 'parent_dur_days' among 9 children using classical Varsha‑Vimshottari weights:
            child_dur_days = parent_dur_days * varsha_days(child) / H
        where H = const.human_life_span_for_varsha_vimsottari_dhasa.
        """
        H = float(const.human_life_span_for_varsha_vimsottari_dhasa)
        lord = parent_lord
        jd_cursor = parent_start_jd
        for _ in range(9):
            days_w = float(const.varsha_vimsottari_days[lord])
            dur_days_unrounded = parent_dur_days * (days_w / H)
            yield (lord, jd_cursor, dur_days_unrounded)
            jd_cursor += dur_days_unrounded
            lord = varsha_vimsottari_next_adhipati(lord)

    def _recurse(level, parent_lord, parent_start_jd, parent_dur_days, prefix, out_rows):
        """Depth >= 3: recursive planetary split under the immediate parent."""
        if level < dhasa_level_index:
            for clord, cstart, cdur in _children_planetary(parent_lord, parent_start_jd, parent_dur_days):
                _recurse(level + 1, clord, cstart, cdur, prefix + (clord,), out_rows)
        else:
            for clord, cstart, cdur in _children_planetary(parent_lord, parent_start_jd, parent_dur_days):
                dur_ret = round(cdur, _round_ndigits) if round_duration else cdur
                out_rows.append(prefix + (clord, _fmt(cstart), dur_ret))

    dhasa_bukthi = []

    for maha_lord, maha_start, maha_dur_days in dashas:

        # L1: Maha only
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            dur_ret = round(maha_dur_days, _round_ndigits) if round_duration else maha_dur_days
            dhasa_bukthi.append((maha_lord, _fmt(maha_start), dur_ret))
            continue

        # L2: Antara (uses your existing bhukti function for exact legacy timings)
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            bhuktis = varsha_vimsottari_bhukti(maha_lord, maha_start)
            for bhukthi_lord, bhukthi_start, bhukthi_durn in bhuktis:
                dur_ret = round(bhukthi_durn, _round_ndigits) if round_duration else bhukthi_durn
                dhasa_bukthi.append((maha_lord, bhukthi_lord, _fmt(bhukthi_start), dur_ret))
            continue

        # L3..L6: planetary recursion with weights (durations in days)
        _recurse(
            level=const.MAHA_DHASA_DEPTH.ANTARA,   # start from 2 -> builds 3..N
            parent_lord=maha_lord,
            parent_start_jd=maha_start,
            parent_dur_days=maha_dur_days,
            prefix=(maha_lord,),
            out_rows=dhasa_bukthi
        )

    return dhasa_bukthi

def mudda_dhasa_bhukthi(jd,place,years,dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,divisional_chart_factor=1):
    return varsha_vimsottari_dhasa_bhukthi(jd,place,years,dhasa_level_index=dhasa_level_index,
                                           divisional_chart_factor=divisional_chart_factor)
'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.mudda_varsha_vimsottari_tests()
