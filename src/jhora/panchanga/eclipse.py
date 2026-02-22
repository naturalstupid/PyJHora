#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# py -- routines for computing tithi, vara, etc.
#
# Copyright (C) 2013 Satish BD  <bdsatish@gmail.com>
# Downloaded from https://github.com/bdsatish/drik-panchanga
#
# This file is part of the "drik-panchanga" Python library
# for computing Hindu luni-solar calendar based on the Swiss ephemeris
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
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora
"""
Eclipse finder using pyswisseph (Swiss Ephemeris).

Features:
- Accepts LOCAL JD and converts to UT JD internally.
- Local vs Global searches (solar & lunar).
- Kind filters (solar: any/total/annular/hybrid/partial; lunar: any/total).
- Returns (start_jd_ut, max_jd_ut, end_jd_ut).
- Uses pyswisseph keywords: flags, backwards, ecltype.
"""
# -*- coding: utf-8 -*-
"""
Eclipse finder using pyswisseph (Swiss Ephemeris), using your class-constant structures.

- Input: LOCAL JD (NOT UTC)
- Modes: Local vs Global (via EclipseLocation).
- Types: Solar (ANY/TOTAL/ANNULAR/HYBRID/PARTIAL), Lunar (ANY/TOTAL/PARTIAL/PENUMBRAL).
- Output: (start_jd_local, max_jd_local, end_jd_local) — returned in **LOCAL JD** (not UT).
"""

from typing import Optional, Tuple
import swisseph as swe
from jhora import utils
from jhora.panchanga import drik
# ---------------------- Eclipse Constants ----------------------
class SolarEclipseType:
    ANY      = getattr(swe, "ECL_ALLTYPES_SOLAR", 0)  # any solar type (if not present, 0 acts as "any")
    TOTAL    = swe.ECL_TOTAL   | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL
    ANNULAR  = swe.ECL_ANNULAR | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL
    HYBRID   = swe.ECL_ANNULAR_TOTAL | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL
    PARTIAL  = swe.ECL_PARTIAL

class LunarEclipseType:
    ANY       = getattr(swe, "ECL_ALLTYPES_LUNAR", 0)  # any lunar type (if not present, 0 acts as "any")
    TOTAL     = swe.ECL_TOTAL
    PARTIAL   = swe.ECL_PARTIAL
    PENUMBRAL = getattr(swe, "ECL_PENUMBRAL", 0)

class EclipseLocation:
    LOCAL  = 0
    GLOBAL = 1

class EclipseType:
    SOLAR = 0
    LUNAR = 1

# ---------------------- Defaults ----------------------
DEFAULT_FLAGS = swe.FLG_SWIEPH  # you used Swiss ephemeris; keep it as default
# ---------------------- Type mapping to strings ----------------------
def _solar_type_str_from_retflag(retflag: int) -> str:
    # Hybrid first, then total, annular, partial
    if retflag & swe.ECL_ANNULAR_TOTAL:
        return "hybrid"
    if retflag & swe.ECL_TOTAL:
        return "total"
    if retflag & swe.ECL_ANNULAR:
        return "annular"
    if retflag & swe.ECL_PARTIAL:
        return "partial"
    return "any"

def _lunar_type_str_from_retflag(retflag: int) -> str:
    if retflag & swe.ECL_TOTAL:
        return "total"
    if retflag & swe.ECL_PARTIAL:
        return "partial"
    if hasattr(swe, "ECL_PENUMBRAL") and (retflag & swe.ECL_PENUMBRAL):
        return "penumbral"
    return "any"

# ---------------------- Public API ----------------------
def next_solar_eclipse(
    jd_local: float,
    place:Tuple[str,float,float,float], #(Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
    eclipse_location_type: int = EclipseLocation.LOCAL,
    solar_eclipse_type: int = SolarEclipseType.ANY,
    search_backward:bool = False,
    flags: int = DEFAULT_FLAGS,
    show_maximum_eclipse_global_location=False,
) -> Optional[Tuple[float, float, float]]:
    """
        Find next/previous solar eclipse and return (start_local_jd, max_local_jd, end_local_jd).
        @param jd_local: user's LOCAL JD
        @param param: place: (Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param solar_eclipse_type: one of SolarEclipseType.* (ANY/TOTAL/ANNULAR/HYBRID/PARTIAL)
             Note: This parameter can be only for GLOBAL. For Local this is not used.
                   And the function will next eclipse immaterial of its type.
        @param search_backward = False (Default). If True - Find previous date
        if show_maximum_eclipse_global_location = False (Default)
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd]
        if show_maximum_eclipse_global_location = True  Only for GLOBAL option
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd],(Max_ecl_longitude,Max_ecl_latitude)
        NOTE: Max_ecl_longitude and latitude - may be in middle of a sea or inhabitant places
            You can use reverse_geocode or reverse_geocoder to find the nearest habitant place
        eclipse_type = "hybrid", "total", "annular", "partial"
        Note: !!! Sometimes date may have -4173 year - which means that eclipse portion is not visible
        """
    _,lat,long,tz = place
    tz_hrs = tz/24.0 if place is not None else 0.0
    jd_ut = jd_local - tz_hrs
    if eclipse_location_type == EclipseLocation.LOCAL:
        if place is None:
            raise ValueError("place is required for LOCAL solar eclipse search")
        geopos = (long, lat, 0.0)  # (lon, lat, height)
        jd = jd_ut
        retflag, tret, _ = swe.sol_eclipse_when_loc(jd, geopos, flags=flags, backwards=search_backward)
        if retflag == -1: return None
        results = (_solar_type_str_from_retflag(retflag), 
                [utils.jd_to_gregorian(tr+tz_hrs) for tr in [tret[1],tret[0],tret[4]]]
                )
    else:  # GLOBAL
        eclmask = solar_eclipse_type
        retflag, tret = swe.sol_eclipse_when_glob(jd_ut, flags=flags, ecltype=eclmask, backwards=search_backward)
        if retflag == -1: return None
        results = (_solar_type_str_from_retflag(retflag), 
                [utils.jd_to_gregorian(tr+tz_hrs) for tr in [tret[2],tret[0],tret[3]]]
                )
    if show_maximum_eclipse_global_location and eclipse_location_type==EclipseLocation.GLOBAL:
        retflag,geopos,_ = swe.sol_eclipse_where(tret[2],SolarEclipseType.TOTAL)
        if retflag == -1:
            print("Unable to find maximum eclipse location")
            return results
        else:
            return results,(geopos[:2])
    return results
def next_lunar_eclipse(
    jd_local: float,
    place:Tuple[str,float,float,float], #(Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
    eclipse_location_type: int = EclipseLocation.GLOBAL,
    lunar_eclipse_type: int = LunarEclipseType.ANY,
    search_backward:bool = False, 
    flags: int = DEFAULT_FLAGS,
    show_maximum_eclipse_global_location=False,
) -> Optional[Tuple[float, float, float]]:
    """
        Find next/previous lunar eclipse and return (start_local_jd, max_local_jd, end_local_jd).
        @param jd_local: user's LOCAL JD
        @param param: place: (Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param solar_eclipse_type: one of SolarEclipseType.* (ANY/TOTAL/ANNULAR/HYBRID/PARTIAL)
             Note: This parameter can be only for GLOBAL. For Local this is not used.
                   And the function will next eclipse immaterial of its type.
        @param search_backward = False (Default). If True - Find previous date
        if show_maximum_eclipse_global_location = False (Default)
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd]
        if show_maximum_eclipse_global_location = True  Only for GLOBAL option
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd],(Max_ecl_longitude,Max_ecl_latitude)
        NOTE: Max_ecl_longitude and latitude - may be in middle of a sea or inhabitant places
            You can use reverse_geocode or reverse_geocoder to find the nearest habitant place
        eclipse_type = "hybrid", "total", "penumbral", "partial"
        Note: !!! Sometimes date may have -4173 year - which means that eclipse portion is not visible
    """
    _,lat,long,tz = place
    tz_hrs = tz/24.0 if place is not None else 0.0
    jd_ut = jd_local - tz_hrs
    if eclipse_location_type == EclipseLocation.LOCAL:
        if place is None:
            raise ValueError("place is required for LOCAL lunar eclipse search")
        geopos = (long, lat, 0.0)  # (lon, lat, height)
        jd = jd_ut
        retflag, tret, _ = swe.lun_eclipse_when_loc(jd, geopos, flags=flags, backwards=search_backward)
        penumbral_begin = tret[6]+tz_hrs; partial_begin = tret[2]+tz_hrs; eclipse_max = tret[0]
        partial_end = tret[3]+tz_hrs; penumbral_end = tret[7]+tz_hrs
        if retflag == -1: return None
        results = (_lunar_type_str_from_retflag(retflag), 
            [utils.jd_to_gregorian(tr) for tr in [penumbral_begin,partial_begin,eclipse_max,partial_end,penumbral_end]]
            )
    else:  # GLOBAL
        eclmask = lunar_eclipse_type
        retflag, tret = swe.lun_eclipse_when(jd_ut, flags=flags, ecltype=eclmask, backwards=search_backward)
        penumbral_begin = tret[6]+tz_hrs; partial_begin = tret[2]+tz_hrs; eclipse_max = tret[0]
        partial_end = tret[3]+tz_hrs; penumbral_end = tret[7]+tz_hrs
        if retflag == -1: return None
        results = (_lunar_type_str_from_retflag(retflag), 
            [utils.jd_to_gregorian(tr) for tr in [penumbral_begin,partial_begin,eclipse_max,partial_end,penumbral_end]]
            )
    if show_maximum_eclipse_global_location and eclipse_location_type==EclipseLocation.GLOBAL:
        retflag,geopos,_ = swe.sol_eclipse_where(tret[2],SolarEclipseType.TOTAL)
        if retflag == -1:
            print("Unable to find maximum eclipse location")
            return results
        else:
            return results,(geopos[:2])
    return results
# ---------- Example usage ----------
if __name__ == "__main__":
    utils.set_language('en')
    from jhora import const
    const.use_24hour_format_in_to_dms = False
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.03862, 80.261818, 5.5)  # timezone=+5.5
    jd_local = utils.julian_day_number(dob, tob)
    backward_search = False
    # Local solar, any
    s_loc = next_solar_eclipse(jd_local,place,eclipse_location_type=EclipseLocation.LOCAL,
                               solar_eclipse_type=SolarEclipseType.TOTAL,search_backward=backward_search)
    ecl_str = utils.resource_strings[s_loc[0]+'_str']+' '+utils.resource_strings['solar_str']+' '+ utils.resource_strings['eclipse_str']
    if s_loc:print('Solar (Local, Total):', ecl_str,[(y,m,d,utils.to_dms(fh)) for y,m,d,fh in s_loc[1]])
    # Global solar, total
    s_glob,geopos = next_solar_eclipse(jd_local,place,eclipse_location_type=EclipseLocation.GLOBAL,
                                      solar_eclipse_type=SolarEclipseType.TOTAL,search_backward=backward_search,
                                      show_maximum_eclipse_global_location=True)
    ecl_str = utils.resource_strings[s_glob[0]+'_str']+' '+utils.resource_strings['solar_str']+' '+ utils.resource_strings['eclipse_str']
    if s_glob: print('Solar (Global, TOTAL):', ecl_str,[(y,m,d,utils.to_dms(fh)) for y,m,d,fh in s_glob[1]],geopos)
    # Local lunar, partial
    l_loc = next_lunar_eclipse(jd_local,place,eclipse_location_type=EclipseLocation.LOCAL,
                                       lunar_eclipse_type=LunarEclipseType.TOTAL,search_backward=backward_search)
    ecl_str = utils.resource_strings[l_loc[0]+'_str']+' '+utils.resource_strings['lunar_str']+' '+ utils.resource_strings['eclipse_str']
    if l_loc: print('Lunar (Local, TOTAL):', ecl_str,[(y,m,d,utils.to_dms(fh)) for y,m,d,fh in l_loc[1]])
    # Global lunar, ANY (includes penumbral)
    l_glob,geopos = next_lunar_eclipse(jd_local,place,eclipse_location_type=EclipseLocation.GLOBAL,
                                    lunar_eclipse_type=LunarEclipseType.PARTIAL,search_backward=backward_search,
                                    show_maximum_eclipse_global_location=True)
    ecl_str = utils.resource_strings[l_glob[0]+'_str']+' '+utils.resource_strings['lunar_str']+' '+ utils.resource_strings['eclipse_str']
    if l_glob: print('Lunar (Global, Partial):', ecl_str,[(y,m,d,utils.to_dms(fh)) for y,m,d,fh in l_glob[1]],geopos)
