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
from mudda import (  # noqa: F401
    get_dhasa_antardhasa,
    get_immediate_children,
    get_running_dhasa_for_given_date,
)

__all__ = [
    "get_dhasa_antardhasa",
    "get_immediate_children",
    "get_running_dhasa_for_given_date",
]

'------ main -----------'
if __name__ == "__main__":
    from jhora import const,utils
    """ 
        drik here is generic model name can be surya_sidhantha or drik depending on value 
        of const.astrology_model_default value
    """
    drik = utils.hora_engine_proxy
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
        ad = get_dhasa_antardhasa(dob,tob, place,dhasa_level_index=DLI,years=_years,
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
