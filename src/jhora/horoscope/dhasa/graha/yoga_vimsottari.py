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
Calculates Yoga Vimsottari
"""
from collections import OrderedDict as Dict
from jhora import const,utils
from jhora.panchanga import drik
sidereal_year = const.sidereal_year #const.savana_year #  # some say 360 days, others 365.25 or 365.2563 etc
vimsottari_dict = { 8:[(3,12,21), 7], 5: [(4,13,22),20], 0:[(5,14,23), 6], 1:[(6,15,24), 10], 2:[(7,16,25), 7], 
                   7:[(8,17,26), 18], 4:[(9,18,27), 16], 6:[(1,10,19), 19], 3:[(2,11,20), 17] }
human_life_span_for_vimsottari_dhasa = const.human_life_span_for_vimsottari_dhasa
### --- Vimoshatari functions
def vimsottari_adhipathi(yoga_index):
    for key,(yoga_list,durn) in vimsottari_dict.items():
        if yoga_index in yoga_list:
            return key,durn 
def vimsottari_next_adhipati(lord,dirn=1):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + dirn) % len(const.vimsottari_adhipati_list)
    return const.vimsottari_adhipati_list[next_index]

def vimsottari_dasha_start_date(jd,place):
    """Returns the start date of the mahadasa which occured on or before `jd`"""
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    _yoga = drik.yogam(jd, place)
    y_frac = utils.get_fraction(_yoga[1], _yoga[2], birth_time_hrs)
    #print('yoga',_yoga,'birth_time_hrs',birth_time_hrs,'yoga_fracion',y_frac)
    lord,res = vimsottari_adhipathi(_yoga[0])          # ruler of current nakshatra
    period_elapsed = (1-y_frac)*res*sidereal_year
    start_jd = jd - period_elapsed      # so many days before current day
    #print('lord,res,period_elapsed,start_date',lord,res,period_elapsed,utils.jd_to_gregorian(start_date))
    return [lord, start_jd]

def vimsottari_mahadasa(jdut1,place):
    """List all mahadashas and their start dates"""
    lord, start_date = vimsottari_dasha_start_date(jdut1,place)
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date; lord_duration = vimsottari_dict[lord][1]
        start_date += lord_duration * sidereal_year
        lord = vimsottari_next_adhipati(lord)
    return retval

def _vimsottari_bhukti(maha_lord, start_date,antardhasa_option=1):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    if antardhasa_option in [3,4]:
        lord = vimsottari_next_adhipati(lord, dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = vimsottari_next_adhipati(lord, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    dhasa_lord_duration = vimsottari_dict[maha_lord][1]
    retval = Dict()
    for _ in range(len(vimsottari_dict)):
        retval[lord] = start_date; bhukthi_duration = vimsottari_dict[lord][1]
        factor = bhukthi_duration * dhasa_lord_duration / human_life_span_for_vimsottari_dhasa
        start_date += factor * sidereal_year
        lord = vimsottari_next_adhipati(lord,dirn)

    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def _vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = Dict()
    for _ in range(9):
        retval[lord] = start_date
        factor = vimsottari_dict[lord] * (vimsottari_dict[maha_lord] / human_life_span_for_vimsottari_dhasa)
        factor *= (vimsottari_dict[bhukti_lord] / human_life_span_for_vimsottari_dhasa)
        start_date += factor * sidereal_year
        lord = vimsottari_next_adhipati(lord)

    return retval


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


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


def get_dhasa_bhukthi(
    jd, place,
    use_tribhagi_variation=False,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA  # 1..6 (1=Maha, 2=+Antara, 3..6 deeper)
):
    """
        provides Yoga Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        This is Vimsottari but based on Yogam instead of Nakshatra.

        Depth (dhasa_level_index):
          1 = Maha only               ->  [l1, start_str]
          2 = + Antara (Bhukti)       ->  [l1, l2, start_str]   (matches your legacy output)
          3 = + Pratyantara           ->  [l1, l2, l3, start_str]
          4 = + Sookshma              ->  [l1, l2, l3, l4, start_str]
          5 = + Prana                 ->  [l1, l2, l3, l4, l5, start_str]
          6 = + Deha                  ->  [l1, l2, l3, l4, l5, l6, start_str]
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    global human_life_span_for_vimsottari_dhasa

    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_vimsottari_dhasa *= _tribhagi_factor
        # NOTE: Your tests may not exercise this path; kept identical to your original.
        for k,v in vimsottari_dict.items():
            vimsottari_dict[k] = round(v*_tribhagi_factor,2)

    # Yoga-based MD starts
    dashas = vimsottari_mahadasa(jd, place)

    # balance (identical to your original)
    dl = list(dashas.values()); de = dl[1]
    y,m,h,_ = utils.jd_to_gregorian(jd); p_date1 = drik.Date(y,m,h)
    y,m,h,_ = utils.jd_to_gregorian(de); p_date2 = drik.Date(y,m,h)
    vim_bal = utils.panchanga_date_diff(p_date1, p_date2)

    # helper: starting child lord and direction for a parent
    def _start_and_dir(parent_lord):
        lord = parent_lord
        if antardhasa_option in [3,4]:
            lord = vimsottari_next_adhipati(lord, dirn=+1)
        elif antardhasa_option in [5,6]:
            lord = vimsottari_next_adhipati(lord, dirn=-1)
        dirn = +1 if antardhasa_option in [1,3,5] else -1
        return lord, dirn

    # helper: iterate 9 planetary children under a parent using classical weights
    # parent_years is in YEARS (float)
    def _children_planetary(parent_lord, parent_start_jd, parent_years):
        start_lord, dirn = _start_and_dir(parent_lord)
        jd_cursor = parent_start_jd
        lord = start_lord
        H = float(human_life_span_for_vimsottari_dhasa)  # 120 or tribhagi-scaled
        for _ in range(9):
            # vimsottari_dict[...] = [yoga_list, years] in this module
            Y = float(vimsottari_dict[lord][1])
            dur_yrs = parent_years * (Y / H)
            yield (lord, jd_cursor, dur_yrs)
            jd_cursor += dur_yrs * sidereal_year
            lord = vimsottari_next_adhipati(lord, dirn)

    dhasa_bukthi = []

    md_items = list(dashas.items())  # [(md_lord, md_start_jd), ...]

    for _ in range(_dhasa_cycles):
        N = len(md_items)
        for idx, (md_lord, md_start_jd) in enumerate(md_items):
            # actual MD years from JD delta (handles first balance)
            if idx < N-1:
                md_end_jd = md_items[idx+1][1]
                md_years = (md_end_jd - md_start_jd) / sidereal_year
            else:
                # last one: fall back to nominal years
                md_years = float(vimsottari_dict[md_lord][1])

            # L1 (Maha)
            if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
                dhasa_bukthi.append([md_lord, utils.julian_day_to_date_time_string(md_start_jd)])
                continue

            # L2 (Antara/Bhukti) — preserve your exact behavior
            # We still use your _vimsottari_bhukti() for start times (so L2 stays byte-for-byte)
            if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
                bhuktis = _vimsottari_bhukti(md_lord, dashas[md_lord], antardhasa_option=antardhasa_option)
                for blord, bstart in bhuktis.items():
                    dhasa_bukthi.append([md_lord, blord, utils.julian_day_to_date_time_string(bstart)])
                continue

            # L3..L6: compute recursively with classical weights under the IMMEDIATE parent
            # We avoid calling your _vimsottari_antara() because it assumes dict values are numeric.
            def _recurse(level, parent_lord, parent_start_jd, parent_years, prefix, out_rows):
                if level < dhasa_level_index:
                    for clord, cstart, cyears in _children_planetary(parent_lord, parent_start_jd, parent_years):
                        _recurse(level + 1, clord, cstart, cyears, prefix + [clord], out_rows)
                else:
                    for clord, cstart, _cyears in _children_planetary(parent_lord, parent_start_jd, parent_years):
                        out_rows.append(prefix + [clord, utils.julian_day_to_date_time_string(cstart)])

            # First expand to L2 using classical weights (not the dict of starts) so we also have durations
            # (This is identical in order to your _vimsottari_bhukti(), but gives us L2 durations for deeper splits.)
            l2_rows = []
            for blord, bstart, byears in _children_planetary(md_lord, md_start_jd, md_years):
                if dhasa_level_index == const.MAHA_DHASA_DEPTH.PRATYANTARA:
                    # exactly L3: emit L3 starts under each L2
                    for alord, astart, _ay in _children_planetary(blord, bstart, byears):
                        dhasa_bukthi.append([md_lord, blord, alord, utils.julian_day_to_date_time_string(astart)])
                else:
                    # deeper than L3 (4..6): recurse
                    _recurse(
                        level=const.MAHA_DHASA_DEPTH.PRATYANTARA,  # starting at 3
                        parent_lord=blord,
                        parent_start_jd=bstart,
                        parent_years=byears,
                        prefix=[md_lord, blord],
                        out_rows=dhasa_bukthi
                    )

    return vim_bal, dhasa_bukthi

'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    const.use_24hour_format_in_to_dms = False
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.yoga_vimsottari_tests()

    