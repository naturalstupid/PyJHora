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
def patyayini_dhasa(jd_years,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1):
    """
        Compute Patyaayini Dhasa
        Should be used for Tajaka Annual charts
        @param jd_years:Julian day number for Tajaka Annual date/time
        @param place: drik.Place struct tuple of ('Place',latitude,longitude,time_zone_offset)
        @param ayanamsa_mode: Default = const._DEFAULT_AYANAMSA_MODE
        @param divisional_chart_factor: Default = 1 (Raasi) - See const.division_chart_factors for other possible values
        @param chart_method: default=1, various methods available for each division chart. See charts module 
        @return patyayini dhasa values as a list [planet, dhasa_duration in days]
        Example: [[5, (1993, 6, 26), 24.9], [3, (1993, 8, 13), 48.1], [1, (1993, 8, 14), 0.57],...]]
    """
    cht = charts.divisional_chart(jd_years,place,ayanamsa_mode,divisional_chart_factor,chart_method=chart_method)
    krisamsas = cht[:-2]  # Exclude Rahu and Ketu
    krisamsas.sort(key=lambda x:x[1][1])
    #for p,(h,long) in krisamsas:
    #    print('krisamsas',p,(h,utils.to_dms(long,is_lat_long='plong')))
    patyamsas = [[p,(h,long-krisamsas[i-1][1][1])] for i,[p,(h,long)] in enumerate(krisamsas) if i>0]
    patyamsas = [krisamsas[0]]+patyamsas
    #print('patyamsas',patyamsas)
    #for p,(h,long) in patyamsas:
    #    print('patyamsas',p,(h,utils.to_dms(long,is_lat_long='plong')))
    patyamsa_sum = sum([long for _,(_,long) in patyamsas])
    _dhasa_period_factors = {p:long/patyamsa_sum for p,(_,long) in patyamsas}
    _dhasa_lords = list(_dhasa_period_factors.keys())
    #print('_dhasa_period_factors',_dhasa_period_factors)
    _dhasas = [[p,const.average_gregorian_year*_dhasa_period_factors[p]] for p,(h,long) in patyamsas]
    #for p,long in _dhasas:
    #    print('_dhasas',p,long)
    jd_start = jd_years
    dhasas = []
    for d,(p,dd) in enumerate(_dhasas):
        #print(d,p,dd)
        bn = d
        db = []
        for b in enumerate(_dhasa_lords):
            pa = _dhasa_lords[bn]
            y,m,d,fh = utils.jd_to_gregorian(jd_start)
            date_str = '%04d-%02d-%02d' %(y,m,d)
            time_str = utils.to_dms(fh,as_string=True)
            bhukthi_start = date_str + ' '+time_str
            db.append([pa,bhukthi_start])
            jd_start += _dhasa_period_factors[pa]*dd
            bn = (bn+1)%len(_dhasa_lords)
        dhasas.append([p,db,dd])
    return dhasas
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.patyayini_tests()
