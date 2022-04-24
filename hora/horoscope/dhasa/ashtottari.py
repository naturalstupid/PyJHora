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
Calculates Vimshottari (=120) Dasha-bhukthi-antara-sukshma-prana
"""

import swisseph as swe
from collections import OrderedDict as Dict
import hora.panchanga
import datetime
#swe.KETU = swe.PLUTO  # I've mapped Pluto to Ketu
sidereal_year = panchanga.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = 108
""" 
    {ashtottari adhipati:[(starting_star_number,ending_star_number),dasa_length]} 
        ashtottari longitude range: (starting_star_number-1) * 360/27 TO (ending_star_number) * 360/27
        Example: 66.67 to 120.00 = 53 deg 20 min range
"""
ashtottari_adhipathi_list = [swe.SUN,swe.MOON,swe.MARS,swe.MERCURY,swe.SATURN,swe.JUPITER,swe.RAHU,swe.VENUS]
ashtottari_adhipathi_dict = {swe.SUN:[(6,9),6],swe.MOON:[(10,12),15],swe.MARS:[(13,16),8],swe.MERCURY:[(17,19),17],
                             swe.SATURN:[(20,22),10],swe.JUPITER:[(23,25),19],swe.RAHU:[(26,2),12],swe.VENUS:[(3,5),21]}

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
def ashtottari_dasha_start_date(jd):
    nak, rem = panchanga.nakshatra_position(jd)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    lord,res = ashtottari_adhipathi(nak+1)          # ruler of current nakshatra
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
def ashtottari_mahadasa(jd):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    lord, start_date = ashtottari_dasha_start_date(jd)
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
    lord = ashtottari_next_adhipati(dhasa_lord) # For Ashtottari first bhukkti starts from dhasa's next lord
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        start_date += factor * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def ashtottari_anthara(dhasa_lord, bhukthi_lord,bhukthi_lord_start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa, ots bhukthi lord and bhukthi_lord's start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = ashtottari_next_adhipati(bhukthi_lord) # For Ashtottari first bhukkti starts from dhasa's next lord
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        bhukthi_lord_start_date += factor * sidereal_year
        lord = ashtottari_next_adhipati(lord)
    return retval
def get_ashtottari_dhasa_bhukthi(jd):
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
    """
    city,lat,long,tz = place
    jdut1 = jd - tz/24
    dashas = ashtottari_mahadasa(jdut1)
    #print('dasha lords',dashas)
    dhasa_bhukthi=[]
    for i in dashas:
        #print(i, dashas[i])
        bhukthis = ashtottari_bhukthi(i, dashas[i])
        #print(bhukthis)
        dhasa_lord = i
        for j in bhukthis:
            bhukthi_lord = j
            jd1 = bhukthis[j]
            y, m, d, h = swe.revjul(round(jd1 + tz))
            date_str = '%04d-%02d-%02d' %(y,m,d)
            bhukthi_start = date_str
            dhasa_bhukthi.append([dhasa_lord,bhukthi_lord,bhukthi_start]) 
            #dhasa_bhukthi[i][j] = [dhasa_lord,bhukthi_lord,bhukthi_start]
    return dhasa_bhukthi
'------ main -----------'
if __name__ == "__main__":
    """ SET AYANAMSA MODE FIRST """
    panchanga.set_ayanamsa_mode('LAHIRI')
    dob = panchanga.Date(1996,12,7)
    tob = (10,34,0)
    place = panchanga.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    tz = place.timezone
    jd = swe.julday(dob[0],dob[1],dob[2],tob[0]+tob[1]/60.0+tob[2]/3600.0)
    db = get_ashtottari_dhasa_bhukthi(jd)
    for d,b,s in db:
        print(d,b,s)
    exit()
