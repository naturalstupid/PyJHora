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
""" Kaala Dhasa """
from jhora.panchanga import drik
from jhora import utils, const
_kaala_dhasa_life_span = 120 # years
year_duration = const.sidereal_year

def _dhasa_progression_and_periods(jd,place):
    previous_day_sunset_time = drik.sunset(jd-1, place)[0]
    today_sunset_time = drik.sunset(jd, place)[0]
    today_sunrise_time = drik.sunrise(jd, place)[0]
    tomorrow_sunrise_time = 24.0+drik.sunrise(jd+1, place)[0]
    _,_,_,birth_time = utils.jd_to_gregorian(jd)
    df = abs(today_sunset_time - today_sunrise_time)/6.0
    nf1 = abs(today_sunrise_time-previous_day_sunset_time)/6.0
    nf2 = abs(tomorrow_sunrise_time-today_sunset_time)/6.0
    dawn_start = today_sunrise_time-nf1; dawn_end=today_sunrise_time+nf1
    day_start = dawn_end; day_end = today_sunset_time-nf1
    dusk_start = day_end ; dusk_end = today_sunset_time+nf2
    yday_night_start = -(previous_day_sunset_time+nf1); yday_night_end = today_sunrise_time-nf1
    tonight_start = today_sunset_time+nf2; tonight_end = tomorrow_sunrise_time-nf2
    # Night is before dawn_start and after dusk_end
    if birth_time > dawn_start and birth_time < dawn_end: # dawn
        kaala_type = 0 # 'Dawn'
        kaala_frac = (birth_time-dawn_start)/(dawn_end-dawn_start)
    elif birth_time > dusk_start and birth_time < dusk_end: # dusk
        kaala_type = 2 # 'Dusk'
        kaala_frac = (birth_time-dusk_start)/(dusk_end-dusk_start)
    elif birth_time > day_start and birth_time < day_end: # Day
        kaala_type = 1 # 'Day'
        kaala_frac = (birth_time-day_start)/(day_end-day_start)
    elif birth_time > yday_night_start and birth_time < yday_night_end: # yday-night
        kaala_type = 3 # 'YDay-Night'
        kaala_frac = (birth_time-yday_night_start)/(yday_night_end-yday_night_start)
    elif birth_time > tonight_start and birth_time < tonight_end: # yday-night
        kaala_type = 3 # 'ToNight'
        kaala_frac = (birth_time-tonight_start)/(tonight_end-tonight_start)
    _kaala_dhasa_life_span_first_cycle = _kaala_dhasa_life_span*kaala_frac
    _dhasas1 = [(p+1)*_kaala_dhasa_life_span_first_cycle/45.0 for p in range(9)]
    # Second Cycle
    _kaala_dhasa_life_span_second_cycle = _kaala_dhasa_life_span - _kaala_dhasa_life_span_first_cycle
    _dhasas2 = [(p+1)*_kaala_dhasa_life_span_second_cycle/45.0 for p in range(9)]
    return kaala_type, kaala_frac,_dhasas1,_dhasas2


def get_dhasa_antardhasa(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True                  # Round only returned durations; internal calcs use full precision
):
    """
        provides kaala dhasa bhukthi for a given date in julian day (includes birth time)

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param dhasa_level_index: Depth level (1..6)
            1 = Maha only (no Antara)
            2 = + Antara (Bhukthi)
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara
        @param round_duration: If True, round returned durations to const.DHASA_DURATION_ROUNDING_TO

        @return:
            kaala_type, dhasa_info

            if dhasa_level_index == 1:
                dhasa_info: [ (dhasa_lord, start_str, dur_yrs), ... ]
            else:
                dhasa_info: [ (dhasa_lord, bhukthi_lord, [sublords...], start_str, leaf_dur_yrs), ... ]
                (tuple grows by one lord label per requested level)
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha-antara).")

    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)

    kaala_type, kaala_frac, dhasas_first, dhasas_second = _dhasa_progression_and_periods(jd_years, place)

    dhasa_info = []
    start_jd = jd_years

    # Kaala sub-division of a parent period (two-phase, weighted 1..9)
    def _children_two_phase(parent_start_jd, parent_duration_years):
        """
        Yields (bhukthi_lord, child_start_jd, child_duration_years) for two phases:
          phase A = kaala_frac * parent, subdivided into weights 1..9 (sum 45)
          phase B = (1 - kaala_frac) * parent, subdivided into weights 1..9 (sum 45)
        bhukthi_lord is 0..8 in sequence (as in original code).
        """
        weights = list(range(1, 10))  # 1..9
        W = 45.0

        # Phase A
        phaseA = kaala_frac * parent_duration_years
        jd_cursor = parent_start_jd
        for blord, w in enumerate(weights):
            dur = phaseA * (w / W)
            yield (blord, jd_cursor, dur)
            jd_cursor += dur * year_duration

        # Phase B
        phaseB = (1.0 - kaala_frac) * parent_duration_years
        for blord, w in enumerate(weights):
            dur = phaseB * (w / W)
            yield (blord, jd_cursor, dur)
            jd_cursor += dur * year_duration

    # Recursive expander: apply Kaala rule at every depth (sum(children)=parent)
    def _recurse(level, parent_start_jd, parent_duration_years, prefix):
        """
        level: the current level to build (>=2). 'prefix' already contains lords up to previous level.
        """
        children = list(_children_two_phase(parent_start_jd, parent_duration_years))
        if not children:
            return

        if level < dhasa_level_index:
            # Go deeper: each child becomes parent for next level
            for blord, child_start_jd, child_dur in children:
                _recurse(level + 1, child_start_jd, child_dur, prefix + (blord,))
        else:
            # Leaf rows: round only for return (if requested); keep full precision for time accumulation
            for blord, child_start_jd, child_dur in children:
                durn = round(child_dur, const.DHASA_DURATION_ROUNDING_TO) if round_duration else child_dur
                dhasa_info.append(prefix + (blord, utils.julian_day_to_date_time_string(child_start_jd), durn))

    # First Cycle
    for dhasa_lord in range(9):
        maha_dur_unrounded = dhasas_first[dhasa_lord]  # full precision for calcs
        if dhasa_level_index == 1:
            durn = round(maha_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur_unrounded
            dhasa_info.append((dhasa_lord, utils.julian_day_to_date_time_string(start_jd), durn))
            start_jd += maha_dur_unrounded * year_duration
        else:
            _recurse(level=2, parent_start_jd=start_jd, parent_duration_years=maha_dur_unrounded, prefix=(dhasa_lord,))
            start_jd += maha_dur_unrounded * year_duration

    # Second Cycle
    for dhasa_lord in range(9):
        maha_dur_unrounded = dhasas_second[dhasa_lord]
        if dhasa_level_index == 1:
            durn = round(maha_dur_unrounded, const.DHASA_DURATION_ROUNDING_TO) if round_duration else maha_dur_unrounded
            dhasa_info.append((dhasa_lord, utils.julian_day_to_date_time_string(start_jd), durn))
            start_jd += maha_dur_unrounded * year_duration
        else:
            _recurse(level=2, parent_start_jd=start_jd, parent_duration_years=maha_dur_unrounded, prefix=(dhasa_lord,))
            start_jd += maha_dur_unrounded * year_duration

    return kaala_type, dhasa_info

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kaala_test()