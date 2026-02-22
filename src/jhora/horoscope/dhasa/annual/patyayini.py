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
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

def patyayini_dhasa(
    jd_years, place,
    divisional_chart_factor=1, chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,   # 1..6 (1=Maha; 2=+Antara [default]; 3..6 deeper)
    round_duration=True
):
    """
        Compute Patyayini Dhasa
        Should be used for Tajaka Annual charts
        @param jd_years: Julian day number for Tajaka Annual date/time
        @param place:    drik.Place struct tuple ('Place', latitude, longitude, tz)
        @param divisional_chart_factor: Default=1 (Raasi). See const.division_chart_factors
        @param chart_method:            default=1. See charts module

        Depth control (new):
          dhasa_level_index: 1..6
            1 = Maha only                     -> (l1,                start_str, dur_days)
            2 = + Antara (Bhukthi) [default]  -> (l1, [[l2,start]...], dur_days)  << preserves your shape
            3 = + Pratyantara                 -> (l1, l2, l3,        start_str, dur_days)
            4 = + Sookshma                    -> (l1, l2, l3, l4,    start_str, dur_days)
            5 = + Prana                       -> (l1, l2, l3, l4, l5, start_str, dur_days)
            6 = + Deha                        -> (l1, l2, l3, l4, l5, l6, start_str, dur_days)

        Rounding:
          round_duration: If True, only the *returned* duration values are rounded to const.DHASA_DURATION_ROUNDING_TO.
                          JD/time accumulation uses full precision.

        @return:
          Depth 1: [ (p, start_str, dd), ... ]
          Depth 2: [ (p, [[pa, start_str], ...], dd), ... ]   # matches your (p, db, dd)
          Depth>=3: [ (p, pa, p3, ..., start_str, dur_leaf), ... ]  # flat leaf rows
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # --- Build the Patyayini frame exactly like your original code ---------------
    cht = charts.divisional_chart(jd_years, place, divisional_chart_factor, chart_method=chart_method)
    krisamsas = cht[:-2]  # Exclude Rahu and Ketu
    krisamsas.sort(key=lambda x: x[1][1])

    # successive arc lengths
    patyamsas = [[p, (h, long - krisamsas[i-1][1][1])] for i, [p, (h, long)] in enumerate(krisamsas) if i > 0]
    patyamsas = [krisamsas[0]] + patyamsas

    patyamsa_sum = sum([long for _, (_, long) in patyamsas])
    if patyamsa_sum <= 0:
        raise ValueError("Invalid Patyayini setup: sum of arcs is non-positive.")

    # Factors (weights) for each lord across the cycle
    _dhasa_period_factors = {p: (long / patyamsa_sum) for p, (_, long) in patyamsas}
    _dhasa_lords = [p for p, _ in patyamsas]  # fixed cycle order

    # Each Maha duration in *days* (your 'dd'): average_gregorian_year * factor
    avg_year_days = const.average_gregorian_year
    maha_blocks = []  # [(p, start_jd, dd_days), ...]
    jd_maha_cursor = jd_years
    for p in _dhasa_lords:
        dd_days = avg_year_days * _dhasa_period_factors[p]
        maha_blocks.append((p, jd_maha_cursor, dd_days))
        jd_maha_cursor += dd_days

    # --- helpers ---------------------------------------------------------------
    _round_ndigits = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    def _children_under(parent_index, parent_start_jd, parent_dur_days):
        """
        Child list for a given parent at position 'parent_index' in _dhasa_lords, in cyclic order
        starting at parent_index (exactly like your bn=d logic).
        Returns sequence of (child_lord, child_start_jd, child_dur_days).
        """
        n = len(_dhasa_lords)
        jd_cursor = parent_start_jd
        for k in range(n):
            idx = (parent_index + k) % n
            child = _dhasa_lords[idx]
            cdur = parent_dur_days * _dhasa_period_factors[child]
            yield (child, jd_cursor, cdur)
            jd_cursor += cdur

    def _recurse(level, parent_index, parent_start_jd, parent_dur_days, prefix, out_rows):
        """
        Depth >= 3 recursive split using the same cyclic order under the immediate parent.
        """
        n = len(_dhasa_lords)
        if level < dhasa_level_index:
            for k in range(n):
                idx = (parent_index + k) % n
                child = _dhasa_lords[idx]
                cstart = parent_start_jd + sum(
                    parent_dur_days * _dhasa_period_factors[_dhasa_lords[(parent_index + t) % n]]
                    for t in range(k)
                )
                cdur = parent_dur_days * _dhasa_period_factors[child]
                _recurse(level + 1, idx, cstart, cdur, prefix + (child,), out_rows)
        else:
            for k in range(n):
                idx = (parent_index + k) % n
                child = _dhasa_lords[idx]
                cstart = parent_start_jd + sum(
                    parent_dur_days * _dhasa_period_factors[_dhasa_lords[(parent_index + t) % n]]
                    for t in range(k)
                )
                cdur = parent_dur_days * _dhasa_period_factors[child]
                dur_ret = round(cdur, _round_ndigits) if round_duration else cdur
                out_rows.append(prefix + (child, utils.julian_day_to_date_time_string(cstart), dur_ret))

    # --- Emit per requested depth ---------------------------------------------
    if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        # L1
        rows = []
        for p, start_jd, dd_days in maha_blocks:
            dur_ret = round(dd_days, _round_ndigits) if round_duration else dd_days
            rows.append((p, utils.julian_day_to_date_time_string(start_jd), dur_ret))
        return rows

    if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
        # L2 — preserve your legacy shape: (p, db, dd)
        dhasas = []
        for d, (p, start_jd, dd_days) in enumerate(maha_blocks):
            bn = d
            db = []
            jd_b = start_jd
            n = len(_dhasa_lords)
            for _ in range(n):
                pa = _dhasa_lords[bn]
                db.append([pa, utils.julian_day_to_date_time_string(jd_b)])
                jd_b += _dhasa_period_factors[pa] * dd_days
                bn = (bn + 1) % n
            dd_ret = round(dd_days, _round_ndigits) if round_duration else dd_days
            dhasas.append([p, db, dd_ret])
        return dhasas

    # L3..L6 — flat leaf rows
    rows = []
    for d, (p, start_jd, dd_days) in enumerate(maha_blocks):
        _recurse(
            level=const.MAHA_DHASA_DEPTH.ANTARA,  # start at 2 → build 3..N
            parent_index=d,
            parent_start_jd=start_jd,
            parent_dur_days=dd_days,
            prefix=(p,),
            out_rows=rows
        )
    return rows
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.patyayini_tests()
