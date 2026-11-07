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
Niryaana Shoola Dhasa - naming-only wrapper around nirayana.py.

"Nirayana Shoola Dhasa" and "Niryaana Shoola Dhasa" are the same dasha under
two different spellings encountered in this project (JHora's own UI/docs use
"Niryaana Shoola"). Rather than maintaining two copies of the same engine,
ALL real logic (antardhasa order, JD boundary resolution, the shared
children-tree function, the sub-day-fallback/sanity-backstop guards, etc.)
lives ONLY in nirayana.py. This module is a thin pass-through that re-exposes
the 3 public entry points under this alternate module name, so callers who
know it as "Niryaana Shoola" can still find it here.

No underscore/private functions are re-exported - only the 3 public entry
points, matching nirayana.py's own public surface:
    get_dhasa_antardhasa()
    immediate_children()
    get_running_dhasa_for_given_date()

IMPORTANT - shared flags, NOT duplicated here:
    nirayana.py exposes two module-level toggles that control its internal
    real-JD-boundary engine:
        nirayana._USE_SANITY_BACKSTOP    (default True)
        nirayana._USE_SUB_DAY_FALLBACK   (default True)
    Since this module calls straight through to nirayana's own functions
    (same engine, same module-level state - not a copy), these flags are
    NOT redefined or mirrored here to avoid two sources of truth going out
    of sync. To toggle them, set them directly on the nirayana module, e.g.:
        import nirayana
        nirayana._USE_SANITY_BACKSTOP = False
    before calling any function in this wrapper - the effect is identical
    whether you call nirayana.get_dhasa_antardhasa(...) or
    niryaana_shoola.get_dhasa_antardhasa(...), because it's the same code.
"""
from jhora.horoscope.dhasa.raasi.nirayana import (
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
    from jhora import const, utils
    utils.set_language('en')
    from jhora.panchanga.drik import Date, Place
    dob = Date(1996, 12, 7)  # PVR_Rao Example
    tob = (10, 34, 0)  # PVR_Rao Example
    place = Place('Chennai,IN', 13.0389, 80.2619, +5.5)  # PVR_Rao Example
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    print("\n--- MD only (benchmark: MD sequence/duration already confirmed) ---")
    md_only = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
    for row in md_only:
        lord, start_str, durn = row
        print(utils.RAASI_SHORT_LIST[lord], start_str, durn)

    print("\n--- MD -> AD (benchmark: Le MD antardasas, PVR_Rao chart) ---")
    md_ad = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA)
    md_ad_seq = {}
    for row in md_ad:
        md_lord, ad_lord, start_str, durn = row
        md_name = utils.RAASI_SHORT_LIST[md_lord]
        ad_name = utils.RAASI_SHORT_LIST[ad_lord]
        md_ad_seq.setdefault(md_name, []).append((ad_name, start_str, durn))
    for md_name, ad_rows in md_ad_seq.items():
        print(md_name, "->", ','.join(a for a, _, _ in ad_rows))
        for ad_name, start_str, durn in ad_rows:
            print("   ", ad_name, start_str, durn)

    print("\n--- Running dasha chain (down to Deha) for 1998-11-09 15:29:45 ---")
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    current_jd = utils.julian_day_number(Date(y, m, d), (hh, mm, ss))
    grd = get_running_dhasa_for_given_date(
        current_jd, jd_at_dob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
        divisional_chart_factor=1,
    )
    for lords, start_str, end_str in grd:
        label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
        print(f"{label:15s} {start_str}  ->  {end_str}")
