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
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

_sandhya_duration = [10 for _ in range(12)]
_panchaka_duration = [60/31,30/31,30/31,30/31,20/31,20/31,20/31,20/31,20/31,20/31,20/31,20/31]

def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,
                         include_antardhasa=False,use_panchaka_variation=False):
    jd_at_dob = utils.julian_day_number(dob, tob)
    pp = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor, years=years, months=months,sixty_hours=sixty_hours)
    _dhasa_seed = pp[0][1][0]
    _dhasa_progression = [((_dhasa_seed+h)%12,_durn) for h,_durn in enumerate(_sandhya_duration)]
    start_jd = jd_at_dob
    dhasa_info = []
    for dhasa_lord, dhasa_duration in _dhasa_progression:
        if include_antardhasa:
            bhukthi_duration = dhasa_duration/12.0
            for bhukthi_lord in [(dhasa_lord+h)%12 for h in range(12)]:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(bhukthi_duration,2)))
                start_jd += bhukthi_duration * const.sidereal_year
        elif use_panchaka_variation:
            for b,bhukthi_lord in enumerate([(dhasa_lord+h)%12 for h in range(12)]):
                bhukthi_duration = _panchaka_duration[b]
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(bhukthi_duration,2)))
                start_jd += bhukthi_duration * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,round(dhasa_duration,2)))
            start_jd += dhasa_duration * const.sidereal_year
    return dhasa_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests.sandhya_test()        