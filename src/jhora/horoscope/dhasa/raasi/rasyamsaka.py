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
Raashiyanka Dasa

Alias module for rasyamsaka.py - "Rasyamsaka" and "Raashiyanka" (also
seen spelled "Rashiyanka") are two names for the same dasa system. All
computation lives in rasyamsaka.py; this module re-exports its public
names unchanged, so existing code that imports raashiyanka can keep
doing so without any behavior difference from importing rasyamsaka
directly.

See rasyamsaka.py's own module docstring for the full description of
the dasa's rules, reference source, and known open points.
"""
from raashiyanka import (  # noqa: F401
    get_dhasa_antardhasa,
    get_immediate_children,
    get_running_dhasa_for_given_date,
)

__all__ = [
    "get_dhasa_antardhasa",
    "get_immediate_children",
    "get_running_dhasa_for_given_date",
]

if __name__ == "__main__":
    from jhora import utils
    from jhora.panchanga.drik import Date, Place
    utils.set_language('en')

    def _print_md_table(dob, tob, place, label, expected=None, **kwargs):
        print("=" * 70)
        print(label)
        print("=" * 70)
        rows = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=1, **kwargs)
        ok = 0
        for lords, start_tuple, dur_years in rows:
            sign = lords[0]
            lord_name = utils.RAASI_SHORT_LIST[sign]
            y_, m_, d_, fh_ = start_tuple
            marker = ""
            if expected is not None and lord_name in expected:
                match = int(dur_years) == expected[lord_name]
                ok += match
                marker = "  OK" if match else f"  MISMATCH (expected {expected[lord_name]})"
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs{marker}")
        if expected is not None:
            print(f"-> {ok}/{len(expected)} durations match the reference")
        print()

    # Chart 1 (Tony Blair) - reference's own stated durations do not fully
    # reconcile with this module's duration formula beyond a few signs;
    # see module docstring.
    chart1_dob = Date(1953, 5, 6)
    chart1_tob = (6, 10, 0)
    chart1_place = Place('Edinburgh,Scotland', 55 + 57 / 60, -3 - 13 / 60, +1.0)
    chart1_expected = {'Cp': 5, 'Aq': 8, 'Pi': 11, 'Ar': 2, 'Ta': 3, 'Ge': 11, 'Cn': 10, 'Le': 9, 'Vi': 5}
    _print_md_table(chart1_dob, chart1_tob, chart1_place, "Chart 1 (Tony Blair)", chart1_expected)

    # Chart 2 (King George VI) - matches 11 of 12 signs exactly; Leo is the
    # one unresolved exception (module docstring).
    chart2_dob = Date(1895, 12, 14)
    chart2_tob = (3, 5, 0)
    chart2_place = Place('Sandringham Estate,England', 52 + 50 / 60, 0 + 30 / 60, 0.0)
    chart2_expected = {'Aq': 9, 'Pi': 9, 'Ar': 8, 'Ta': 8, 'Ge': 6, 'Cn': 9, 'Le': 5,
                        'Vi': 11, 'Li': 12, 'Sc': 12, 'Sg': 8, 'Cp': 4}
    _print_md_table(chart2_dob, chart2_tob, chart2_place, "Chart 2 (King George VI)", chart2_expected)

    # Research use: same chart, seed derived from a different Dn instead
    # of the default D-9, to illustrate seed_divisional_chart_factor.
    _print_md_table(chart2_dob, chart2_tob, chart2_place,
                     "Chart 2 (King George VI) - seed via D-11 instead of D-9 (exploratory, not per reference)",
                     expected=None, seed_divisional_chart_factor=11)
    exit()
