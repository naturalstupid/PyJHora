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
def get_dhasa_antardhasa(dob,tob,place,years=1,months=1,sixty_hours=1,include_antardhasa=False):
    """
        provides kaala dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months,sixty_hours=sixty_hours)
    kaala_type, kaala_frac,dhasas_first, dhasas_second = _dhasa_progression_and_periods(jd_years, place)
    dhasa_info = []
    start_jd = jd_years
    for dhasa_lord in range(9):
        _dhasa_duration = dhasas_first[dhasa_lord]
        if include_antardhasa:
            _dhasa_duration = kaala_frac*dhasas_first[dhasa_lord]
            for bhukthi_lord in range(9):
                _bhukthi_duration = (bhukthi_lord+1)*_dhasa_duration/45.0
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                start_jd += _bhukthi_duration * const.sidereal_year
            # Second cycle of Antardhasa
            _dhasa_duration = (1.0-kaala_frac)*dhasas_first[dhasa_lord]
            for bhukthi_lord in range(9):
                _bhukthi_duration = (bhukthi_lord+1)*_dhasa_duration/45.0
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                start_jd += _bhukthi_duration * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,round(_dhasa_duration,2)))
            start_jd += _dhasa_duration * const.sidereal_year
    # Second Cycle
    for dhasa_lord in range(9):
        _dhasa_duration = dhasas_second[dhasa_lord]
        if include_antardhasa:
            _dhasa_duration = kaala_frac*dhasas_second[dhasa_lord]
            for bhukthi_lord in range(9):
                _bhukthi_duration = (bhukthi_lord+1)*_dhasa_duration/45.0
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                start_jd += _bhukthi_duration * const.sidereal_year
            # Second cycle of Antardhasa
            _dhasa_duration = (1.0-kaala_frac)*dhasas_second[dhasa_lord]
            for bhukthi_lord in range(9):
                _bhukthi_duration = (bhukthi_lord+1)*_dhasa_duration/45.0
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(_bhukthi_duration,2)))
                start_jd += _bhukthi_duration * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,round(_dhasa_duration,2)))
            start_jd += _dhasa_duration * const.sidereal_year
    return kaala_type, dhasa_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.kaala_test()