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
Kendradhi Rasi Dhasa - naming-only wrapper around lagna_kendradhi.py.

"Kendradhi Rasi Dhasa" and "Lagna Kendradhi Dhasa" are the same dasha under
two different spellings encountered in this project. Rather than maintaining 
two copies of the same engine, ALL real logic (antardhasa order, JD boundary resolution, 
the shared children-tree function, the sub-day-fallback/sanity-backstop guards, etc.)
lives ONLY in lagna_kendradhi.py. This module is a thin pass-through that re-exposes
the 3 public entry points under this alternate module name, so callers who
know it as "Kendradhi Rasi" can still find it here.

No underscore/private functions are re-exported - only the 3 public entry
points, matching lagna_kendradhi.py's own public surface:
    get_dhasa_antardhasa()
    immediate_children()
    get_running_dhasa_for_given_date()

"""
from jhora.horoscope.dhasa.raasi.lagna_kendraadhi import (
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
    from jhora import const,utils
    from jhora.panchanga.drik import Date, Place, dhasa_year_duration
    utils.set_language('en')
    dob = Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    y, m, d = (1998, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(Date(y, m, d), (hh, mm, ss))
    print(check_date)
    import time

    DLI = const.MAHA_DHASA_DEPTH.DEHA
    LEVEL_NAMES = ['MD', 'AD', 'PD', 'SD', 'PAD', 'Deha']

    db = get_dhasa_antardhasa(dob, tob, place,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
    md_ad_seq = {}
    for lords, _, _ in db:
        lord, sub_lord = lords
        lord_name = utils.RAASI_SHORT_LIST[lord]
        if lord_name not in md_ad_seq:
            md_ad_seq[lord_name] = []
        md_ad_seq[lord_name].append(utils.RAASI_SHORT_LIST[sub_lord])
    md_ad_seq = {k: ','.join(v) for k, v in md_ad_seq.items()}
    for lord, sub_lord_seq in md_ad_seq.items():
        print(lord, " > ", md_ad_seq[lord])

    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
        )
        grdn = [
            ['-'.join([utils.RAASI_SHORT_LIST[lord] for lord in lords]),
             (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))]
            for [lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2)] in grd
        ]

        print("\nFull running-dhasa chain (NEW method) - MD/AD/PD/SD/PAD/Deha:")
        for name, row in zip(LEVEL_NAMES, grdn):
            print(f"  {name:5s}: {row}")
        print('new method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kendradhi_rasi_test()
