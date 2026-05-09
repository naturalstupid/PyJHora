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
    jd, place,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha, 2=+Antara [default], 3..6 deeper)
    round_duration=True,                               # round only returned duration; JD math stays full precision
    dhasa_duration_type=None,
    savana_year_method=None,
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
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # Build maha sequence (each item = (lord, start_jd, duration_days))
    dashas = varsha_vimsottari_mahadasa(
        jd, place, years,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method
    )

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
                dur_ret = round(cdur, dhasa_level_index+1) if round_duration else cdur
                out_rows.append((prefix + (clord,), utils.jd_to_gregorian(cstart), dur_ret))

    dhasa_bukthi = []

    for maha_lord, maha_start, maha_dur_days in dashas:

        # L1: Maha only
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            dur_ret = round(maha_dur_days, dhasa_level_index+1) if round_duration else maha_dur_days
            dhasa_bukthi.append(((maha_lord,), utils.jd_to_gregorian(maha_start), dur_ret))
            continue

        # L2: Antara (uses your existing bhukti function for exact legacy timings)
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            bhuktis = varsha_vimsottari_bhukti(maha_lord, maha_start)
            for bhukthi_lord, bhukthi_start, bhukthi_durn in bhuktis:
                dur_ret = round(bhukthi_durn, dhasa_level_index+1) if round_duration else bhukthi_durn
                dhasa_bukthi.append(((maha_lord, bhukthi_lord), utils.jd_to_gregorian(bhukthi_start), dur_ret))
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

def mudda_dhasa_bhukthi(jd,place,years,dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,divisional_chart_factor=1,
                        dhasa_duration_type=None,savana_year_method=None):
    return varsha_vimsottari_dhasa_bhukthi(jd,place,years,dhasa_level_index=dhasa_level_index,
                                           divisional_chart_factor=divisional_chart_factor,
                                           dhasa_duration_type=dhasa_duration_type,
                                           savana_year_method=savana_year_method)
def mudda_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    **kwargs):
    return varsha_vimsottari_immediate_children(parent_lords, parent_start, parent_duration, parent_end,**kwargs)
def varsha_vimsottari_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (provide exactly one of: duration OR end)
    parent_end=None,             # (Y, M, D, fractional_hour)
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    year_duration: float = const.sidereal_year,
    round_duration: bool = False,    # tiler returns exact spans; keep unrounded here
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Varsha Vimshottari (Mudda) — return ONLY the immediate (parent -> children) splits.

      [ (lords_tuple_{k+1}, start_tuple, end_tuple), ... ]

    Strategy:
      • Ask the base for depth = len(parent_lords)+1.
      • Filter rows that belong to the given parent path.
      • Keep only children whose span intersects the parent span.
      • Clamp the last child to the parent's end; exact tiling (no rounding).
    """
    # normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    k = len(path)   # parent level (L1 -> 1, L2 -> 2, ...)

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

    # resolve parent span
    start_jd = _t2jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _t2jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []

    # reconstruct dob/tob from JD @ birth
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0); tob = (fh0, 0, 0)

    # ask base for depth = k+1 (unrounded)
    rows = varsha_vimsottari_dhasa_bhukthi(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=k+1,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    ) or []

    # Extract only the children under this parent path and intersecting the span
    kids, OUT = [], []
    for (lords_tuple, child_start_t, dur_years) in rows:
        if tuple(lords_tuple[:k]) != path:
            continue
        cst = _t2jd(child_start_t)
        cen = cst + float(dur_years) * year_duration
        # keep only if intersects [start_jd, end_jd]
        if cen > start_jd and cst < end_jd:
            kids.append((tuple(lords_tuple), cst, cen))

    if not kids:
        return []

    # sort by start JD & tile; clamp last child's end to parent end
    kids.sort(key=lambda r: r[1])
    for i, (lt, cst, cen) in enumerate(kids):
        st = max(cst, start_jd)
        en = min(cen, end_jd) if i < len(kids) - 1 else end_jd
        if en > st:
            OUT.append((lt, _jd2t(st), _jd2t(en)))

    return OUT
def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,   # 1..6
    *,
    divisional_chart_factor: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    year_duration: float = const.sidereal_year,
    round_duration: bool = False,                    # runner uses exact spans; keep unrounded here
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Varsha Vimshottari (Mudda) — running ladder at `current_jd`:

      [
        [(L1,),                  start1, end1],
        [(L1,L2),                start2, end2],
        ...
        [(L1,..,L_d),            startd, endd]
      ]

    Simple zero-duration handling:
      • Skip only `duration <= 0` rows when building selector period lists.
      • Append a sentinel end to the last period at each depth.
      • If the *last* Mahā has `duration <= 0` and `current_jd` is beyond the previous end,
        you may raise a terminal error (edge case you described).
    """
    # depth normalization
    def _norm(x):
        try: d = int(x)
        except Exception: d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)

    # tuple <-> JD
    def _t2jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd2t(jd):
        return utils.jd_to_gregorian(jd)

    # L1 via base (unrounded)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0); tob = (fh0, 0, 0)

    l1_rows = varsha_vimsottari_dhasa_bhukthi(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    ) or []

    year_duration = globals()['year_duration']

    # Build (lords,start)+sentinel — skip ONLY duration <= 0
    periods, jd_cursor = [], jd_at_dob
    for (lords_tuple, start_tuple, dur_years) in l1_rows:
        dur = float(dur_years)
        if dur <= 0.0:
            continue
        L1 = int(lords_tuple[0]) if isinstance(lords_tuple, (list, tuple)) else int(lords_tuple)
        periods.append(((L1,), start_tuple))
        jd_cursor = _t2jd(start_tuple) + dur * year_duration

    if not periods:
        sentinel = _jd2t(jd_at_dob)
        return [[(), sentinel, sentinel]]

    periods.append((periods[-1][0], _jd2t(jd_cursor)))  # sentinel

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder  = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # Deeper: expand the running parent each time using the immediate-children helper
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = varsha_vimsottari_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years, months=months, sixty_hours=sixty_hours,
            year_duration=year_duration,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
        )
        if not kids:
            # If no children, collapse to a degenerate final rung
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        # Convert children rows to selector periods (lords, start) + sentinel end
        child_periods = []
        for lt, st, en in kids:
            if _t2jd(en) > _t2jd(st):
                child_periods.append((lt, st))
        if not child_periods:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break
        child_periods.append((child_periods[-1][0], parent_end))  # sentinel

        rdk = utils.get_running_dhasa_for_given_date(current_jd, child_periods)
        running = [tuple(rdk[0]), rdk[1], rdk[2]]
        ladder.append(running)

    return ladder

'------ main -----------'
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)    
    jd_at_dob  = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y,m,d = map(int,current_date_str.split(','))
    hh,mm,ss = map(int,current_time_str.split(':')); fh = hh+mm/60+ss/3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y,m,d),(hh,mm,ss))
    DLI = const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
    import time
    _years = utils.jd_to_gregorian(current_jd)[0]-utils.jd_to_gregorian(jd_at_dob)[0]-1
    for dd in const.DHASA_YEAR_DURATION:
        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("-" * 80)
        start_time = time.time()
        print("Dehā        :", get_running_dhasa_for_given_date(current_jd, jd_at_dob, place,
                                                                dhasa_level_index=DLI,
                                                                years=_years,
                                                                dhasa_duration_type=dd))
        print('new method elapsed time',time.time()-start_time)
        start_time = time.time()
        ad = varsha_vimsottari_dhasa_bhukthi(jd_at_dob, place,dhasa_level_index=DLI,years=_years,
                                              dhasa_duration_type=dd)
        for row in ad:
            lords,ds,dur = row
            print([utils.PLANET_NAMES[lord] for lord in lords],ds,dur)
        print(utils.get_running_dhasa_at_all_levels_for_given_date(current_jd, ad,DLI,
                                                                   extract_running_period_for_all_levels=True))
        print('old method elapsed time',time.time()-start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.mudda_varsha_vimsottari_tests()
