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
    Sandhya is another Ayurdasa system. Concept: Sandhya is the Dvadashāńśa Ayurdaya of the Param Ayurdaya. 
    In this dasa system, the parama-ayush is spread among the 12 Rāśis, making the dasa span of each Rāśi as 1/12th of the Paramaayush. 
    For humans the Paramayush have been agreed by savants as 120 years. Hence the span of each Sandhya Dasa is 10 years. 
    
    Also includes Panchaka Dasa Variation - wherein 10 years are divided into 3 compartments: 
    1 rasi - 61/30, 3 rasis-61/60 and 8 rasis - 61/90  - each fraction of 10 years 
"""
from jhora import utils, const
from jhora.horoscope.chart import charts

_sandhya_duration = [10 for _ in range(12)]
_panchaka_duration = [60/31,30/31,30/31,30/31,20/31,20/31,20/31,20/31,20/31,20/31,20/31,20/31]


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    use_panchaka_variation=False,  # if True, use _panchaka_duration as weights for children at every level
    round_duration=True           # only affects returned rows; progression uses full precision
):
    """
    Sandhya Dasha with multi-level expansion (L1..L6).

    Output (variable arity by level):
      L1: (MD, start_str, dur_years)
      L2: (MD, AD, start_str, dur_years)
      L3: (MD, AD, PD, start_str, dur_years)
      ...
      L6: (L1, L2, L3, L4, L5, L6, start_str, dur_years)

    Rules:
      • Replaces include_antardhasa with dhasa_level_index (1..6).
      • Each deeper level is computed from its immediate parent.
      • Equal split ×12 by default; if use_panchaka_variation=True, use _panchaka_duration as weights (normalized).
      • Σ(children) == parent. No rounding in progression; rounding only in returned rows if round_duration=True.
      • Timestamps via utils.julian_day_to_date_time_string(jd).
      • Preserves Sandhya MD order from _sandhya_duration.
    """
    # ------------------------
    # Prepare chart & MD progression
    # ------------------------
    jd_at_dob = utils.julian_day_number(dob, tob)
    pp = charts.divisional_chart(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours
    )[:const._pp_count_upto_ketu]

    _dhasa_seed = pp[0][1][0]  # asc house index
    # MD progression: 12 signs starting from seed; durations from module-level _sandhya_duration
    _dhasa_progression = [((_dhasa_seed + h) % 12, _durn) for h, _durn in enumerate(_sandhya_duration)]

    dhasa_info = []
    start_jd = jd_at_dob

    # ------------------------
    # Local helpers (no timestamp wrapper; use utils.* directly)
    # ------------------------
    def _child_sequence(parent_lord):
        """Ordered list of 12 child lords for Sandhya: forward from parent_lord."""
        return [(parent_lord + h) % 12 for h in range(12)]

    def _child_durations(parent_duration_years):
        """
        Child durations for the next level.
        - If use_panchaka_variation: use _panchaka_duration as weights (normalized to sum=1).
        - Else: equal split among 12 (each 1/12).
        Returns list of 12 absolute durations whose sum equals parent_duration_years.
        """
        if use_panchaka_variation:
            total_w = float(sum(_panchaka_duration))
            if total_w <= 0:
                return [parent_duration_years / 12.0] * 12
            return [parent_duration_years * (w / total_w) for w in _panchaka_duration]
        else:
            return [parent_duration_years / 12.0] * 12

    def _append_leaf(lords_stack, start_jd_val, seg_duration_years):
        """
        Append a single leaf row with start time string and (optionally rounded) duration.
        """
        disp_dur = seg_duration_years if not round_duration else round(
            seg_duration_years, getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)
        )
        dhasa_info.append(tuple(
            lords_stack + [utils.julian_day_to_date_time_string(start_jd_val), disp_dur]
        ))
        # Advance time by the leaf duration
        return start_jd_val + seg_duration_years * const.sidereal_year

    def _expand_children(start_jd_val, parent_duration_years, parent_lords_stack, current_level, target_level):
        """
        Recursively expand segments down to target_level.
        - If current_level == target_level: append a single row for the entire segment.
        - Else: split into 12 children using order from _child_sequence and durations from _child_durations.
        Returns updated start_jd after consuming this segment.
        """
        if current_level == target_level:
            return _append_leaf(parent_lords_stack, start_jd_val, parent_duration_years)

        parent_lord = parent_lords_stack[-1]
        children = _child_sequence(parent_lord)
        child_durs = _child_durations(parent_duration_years)

        for i, child_lord in enumerate(children):
            start_jd_val = _expand_children(
                start_jd_val,
                child_durs[i],
                parent_lords_stack + [child_lord],
                current_level + 1,
                target_level
            )
        return start_jd_val

    # ------------------------
    # Generate rows (single cycle; Sandhya has MD durations from _sandhya_duration)
    # ------------------------
    for md_lord, md_years in _dhasa_progression:
        start_jd = _expand_children(
            start_jd,
            md_years,
            [md_lord],
            current_level=1,
            target_level=dhasa_level_index
        )

    return dhasa_info

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.sandhya_test()        