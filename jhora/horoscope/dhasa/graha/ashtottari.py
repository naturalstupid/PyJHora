#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ashtottari.py -- routines for computing time periods of ashtottari dhasa bhukthi
#
# Copyright by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid
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
Calculates Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana
"""

from collections import OrderedDict as Dict
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house
import datetime
#swe.KETU = swe.PLUTO  # I've mapped Pluto to Ketu
sidereal_year = const.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = 108
""" 
    {ashtottari adhipati:[(starting_star_number,ending_star_number),dasa_length]} 
        ashtottari longitude range: (starting_star_number-1) * 360/27 TO (ending_star_number) * 360/27
        Example: 66.67 to 120.00 = 53 deg 20 min range
"""
#ashtottari_adhipathi_list = [swe.SUN,swe.MOON,swe.MARS,swe.MERCURY,swe.SATURN,swe.JUPITER,swe.RAHU,swe.VENUS]
#ashtottari_adhipathi_dict = {swe.SUN:[(6,9),6],swe.MOON:[(10,12),15],swe.MARS:[(13,16),8],swe.MERCURY:[(17,19),17],
#                             swe.SATURN:[(20,22),10],swe.JUPITER:[(23,25),19],swe.RAHU:[(26,2),12],swe.VENUS:[(3,5),21]}
ashtottari_adhipathi_list = [0,1,2,3,6,4,7,5]
ashtottari_adhipathi_dict = {0:[(6,9),6],1:[(10,12),15],2:[(13,16),8],3:[(17,19),17],
                             6:[(20,22),10],4:[(23,25),19],7:[(26,2),12],5:[(3,5),21]}
def applicability_check(planet_positions):
    asc_house = planet_positions[0][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    house_of_lord = planet_positions[lagna_lord+1][1][0]
    #print('asc house',asc_house,'lagna_lord',lagna_lord,'house_of_lord',house_of_lord)
    rahu_house = planet_positions[8][1][0]
    chk =  rahu_house in house.trines_of_the_raasi(house_of_lord) and rahu_house != asc_house 
    #print('rahu_house',rahu_house,'trines_of_the_lagna lord',house.trines_of_the_raasi(house_of_lord),'applicability',chk)
    return chk
def ashtottari_adhipathi(nak):
    for key,value in ashtottari_adhipathi_dict.items():
        starting_star = value[0][0]
        ending_star = value[0][1]
        nak1 = nak
        if ending_star < starting_star:# and nak < starting_star:
            ending_star += 27
            if nak1 < starting_star:
                nak1 += 27
        if nak1 >= starting_star and nak1 <= ending_star:
            return key,value
def ashtottari_dasha_start_date(jd,star_position_from_moon=1):
    nak, rem = drik.nakshatra_position(jd,star_position_from_moon=star_position_from_moon)
    #print('moon star at dob',nak+1)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    lord,res = ashtottari_adhipathi(nak+1)          # ruler of current nakshatra
    #print(lord,res)
    period = res[1]
    period_elapsed = rem / one_star * period # years
    period_elapsed *= sidereal_year        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date]
def ashtottari_next_adhipati(lord):
    """Returns next lord after `lord` in the adhipati_list"""
    current = ashtottari_adhipathi_list.index(lord)
    #print(current)
    next_index = (current + 1) % len(ashtottari_adhipathi_list)
    #print(next_index)
    return list(ashtottari_adhipathi_dict.keys())[next_index]
def ashtottari_mahadasa(jd,star_position_from_moon=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    lord, start_date = ashtottari_dasha_start_date(jd,star_position_from_moon=star_position_from_moon)
    retval = Dict()
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        start_date += lord_duration * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def ashtottari_bhukthi(dhasa_lord, start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa and its start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = dhasa_lord if const.ashtottari_bhukthi_starts_from_dhasa_lord else ashtottari_next_adhipati(dhasa_lord)
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        start_date += factor * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def ashtottari_anthara(dhasa_lord, bhukthi_lord,bhukthi_lord_start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa, its bhukthi lord and bhukthi_lord's start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = bhukthi_lord if const.ashtottari_bhukthi_starts_from_dhasa_lord else ashtottari_next_adhipati(bhukthi_lord)
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        bhukthi_lord_start_date += factor * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def get_ashtottari_dhasa_bhukthi(jd, place,star_position_from_moon=1,use_tribhagi_variation=False):
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_ashtottari_dhasa
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_ashtottari_dhasa *= _tribhagi_factor
        for k,(v1,v2) in ashtottari_adhipathi_dict.items():
            ashtottari_adhipathi_dict[k] = [v1,round(v2*_tribhagi_factor,2)]
    city,lat,long,tz = place
    jdut1 = jd - tz/24 # Need to pass JD in UT - to calculate moon longitude using swiss ephmeris
    dashas = ashtottari_mahadasa(jdut1,star_position_from_moon=star_position_from_moon)
    #print('dasha lords',dashas)
    dhasa_bhukthi=[]
    for _ in range(_dhasa_cycles):
        for i in dashas:
            #print(i, dashas[i])
            bhukthis = ashtottari_bhukthi(i, dashas[i])
            #print(bhukthis)
            dhasa_lord = i
            for j in bhukthis:
                bhukthi_lord = j
                jd1 = bhukthis[j]+tz/24.
                y, m, d, h = utils.jd_to_gregorian(jd1)#swe.revjul(round(jd1 + tz/24))
                """ TODO: Need to figure out passing date and time string to UI, main.py and pvr_tests.py """
                date_str = '%04d-%02d-%02d' %(y,m,d)+' '+utils.to_dms(h,as_string=True)
                bhukthi_start = date_str
                dhasa_bhukthi.append([dhasa_lord,bhukthi_lord,bhukthi_start]) 
                #dhasa_bhukthi[i][j] = [dhasa_lord,bhukthi_lord,bhukthi_start]
    return dhasa_bhukthi
'------ main -----------'
if __name__ == "__main__":
    """ SET AYANAMSA MODE FIRST """
    from hora import utils
    from hora.horoscope.chart import charts
    drik.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
    dob = drik.Date(1996,12,7)
    tob = (10,34,0)
    place = drik.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    jd = utils.julian_day_number(dob,tob)
    pp = charts.rasi_chart(jd, place)
    print('Ashtottari availability',applicability_check(pp))
    db = get_ashtottari_dhasa_bhukthi(jd, place,use_tribhagi_variation=False)
    for d,b,s in db:
        print(d,b,s)
    exit()
