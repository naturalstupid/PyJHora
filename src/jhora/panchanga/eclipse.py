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
# BUGFIX: swe.sol_eclipse_when_loc()/swe.lun_eclipse_when_loc() (used for
# EclipseLocation.LOCAL below) have NO type-filter parameter at all in the
# Swiss Ephemeris API -- unlike their GLOBAL counterparts
# (sol_eclipse_when_glob/lun_eclipse_when), which DO accept an ecltype mask.
# Previously, LOCAL searches silently ignored solar_eclipse_type/
# lunar_eclipse_type entirely (as the old docstring explicitly noted --
# "This parameter can be only for GLOBAL. For Local this is not used.") and
# always returned whichever eclipse type Swiss Ephemeris found next, which
# could visibly contradict a user-selected "Total"/"Partial" filter. Both
# LOCAL branches below now loop, retrying past each non-matching local
# eclipse (advancing just past its own end/begin contact instant) until one
# actually matches the requested type, giving LOCAL searches the same
# type-filtering behavior GLOBAL already had.
DEFAULT_MAX_TRIES = 40
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
def _solar_type_matches(retflag: int, solar_eclipse_type: int) -> bool:
    """ Whether a LOCAL solar eclipse's actual retflag satisfies the
        requested solar_eclipse_type filter.
        BUGFIX: previously this did a raw bitwise AND against the
        composite SolarEclipseType.* masks (e.g. TOTAL = ECL_TOTAL |
        ECL_CENTRAL | ECL_NONCENTRAL). That composite is correct when
        used as a REQUEST mask for swisseph's GLOBAL ecltype parameter,
        but ECL_CENTRAL/ECL_NONCENTRAL are independent flags describing
        the eclipse's GLOBAL geometry (whether the shadow axis passes
        centrally through the earth) -- they can be set on a retflag
        whose LOCAL type is actually "partial", causing a false-positive
        AND match against the TOTAL mask. Comparing the derived type
        STRING (same logic _solar_type_str_from_retflag already uses for
        display) instead of raw bits avoids this entirely. """
    if solar_eclipse_type in (SolarEclipseType.ANY, 0):
        return True
    expected = {
        SolarEclipseType.TOTAL: "total",
        SolarEclipseType.ANNULAR: "annular",
        SolarEclipseType.HYBRID: "hybrid",
        SolarEclipseType.PARTIAL: "partial",
    }.get(solar_eclipse_type)
    if expected is None:
        return bool(retflag & solar_eclipse_type)
    return _solar_type_str_from_retflag(retflag) == expected
def _lunar_type_matches(retflag: int, lunar_eclipse_type: int) -> bool:
    """ Whether a LOCAL lunar eclipse's actual retflag satisfies the
        requested lunar_eclipse_type filter. Mirrors
        _solar_type_matches()'s string-comparison approach for
        consistency (LunarEclipseType's own constants are plain,
        non-composite bits, so this is primarily defensive). """
    if lunar_eclipse_type in (LunarEclipseType.ANY, 0):
        return True
    expected = {
        LunarEclipseType.TOTAL: "total",
        LunarEclipseType.PARTIAL: "partial",
        LunarEclipseType.PENUMBRAL: "penumbral",
    }.get(lunar_eclipse_type)
    if expected is None:
        return bool(retflag & lunar_eclipse_type)
    return _lunar_type_str_from_retflag(retflag) == expected
def _safe_tret_to_gregorian(tret_val, tz_hrs):
    """ Converts a swisseph tret[] contact-time value to
        (y,m,d,fh), or returns None if that phase did not occur
        (swisseph leaves the corresponding tret[] slot at 0.0 in
        that case, which would otherwise produce a bogus
        year -4713 -- proleptic Julian epoch -- date). """
    if tret_val == 0.0:
        return None
    return utils.jd_to_gregorian(tret_val + tz_hrs)
# ---------------------- Public API ----------------------
def next_solar_eclipse(
    jd_local: float,
    place:Tuple[str,float,float,float], #(Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
    eclipse_location_type: int = EclipseLocation.LOCAL,
    solar_eclipse_type: int = SolarEclipseType.ANY,
    search_backward:bool = False,
    flags: int = DEFAULT_FLAGS,
    show_maximum_eclipse_global_location=False,
    max_tries: int = DEFAULT_MAX_TRIES,
) -> Optional[Tuple[float, float, float]]:
    """
        Find next/previous solar eclipse and return (start_local_jd, max_local_jd, end_local_jd).
        @param jd_local: user's LOCAL JD
        @param param: place: (Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL.
             LOCAL returns the next eclipse seen at the place, with its local begin, maximum and end.
             GLOBAL returns the next eclipse on Earth, with its global begin, maximum and end.
        @param solar_eclipse_type: one of SolarEclipseType.* (ANY/TOTAL/ANNULAR/HYBRID/PARTIAL).
             Honored for BOTH LOCAL and GLOBAL searches: for LOCAL, since
             Swiss Ephemeris's own local-eclipse search has no type-filter
             parameter, this is enforced by retrying (up to max_tries times)
             past each non-matching local eclipse found.
        @param search_backward = False (Default). If True - Find previous date
        @param max_tries: for LOCAL searches only, maximum number of
            successive local eclipses to examine before giving up on
            finding one that matches solar_eclipse_type (default 40).
            Unused for GLOBAL (Swiss Ephemeris's own ecltype mask finds a
            match directly). NOTE: a TOTAL/ANNULAR/HYBRID eclipse recurs
            at any single location only about once every 300-400 years on
            average, so 40 tries (~40 lunations, ~3 years) will often be
            too narrow a window for those filters -- consider raising
            this substantially (e.g. into the hundreds) if searches keep
            returning None for a rare local type.
        if show_maximum_eclipse_global_location = False (Default)
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd]
        if show_maximum_eclipse_global_location = True  Only for GLOBAL option
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd],(Max_ecl_latitude,Max_ecl_longitude)
        NOTE: Max_ecl_longitude and latitude - may be in middle of a sea or inhabitant places
            You can use reverse_geocode or reverse_geocoder to find the nearest habitant place
        eclipse_type = "hybrid", "total", "annular", "partial"
        Note: !!! Sometimes date may have -4173 year - which means that eclipse portion is not visible
        """
    if place is not None:
        _,lat,long,tz = place; ele = getattr(place, 'elevation', 0.0) or 0.0
    tz_hrs = tz/24.0 if place is not None else 0.0
    jd_ut = jd_local - tz_hrs
    if eclipse_location_type == EclipseLocation.LOCAL:
        if place is None:
            raise ValueError("place is required for LOCAL solar eclipse search")
        geopos = (long, lat, ele)  # (lon, lat, height)
        jd = jd_ut
        for _ in range(max_tries):
            retflag, tret, _ = swe.sol_eclipse_when_loc(jd, geopos, flags=flags, backwards=search_backward)
            if retflag == -1: return None
            if _solar_type_matches(retflag, solar_eclipse_type):
                results = (_solar_type_str_from_retflag(retflag),
                        [utils.jd_to_gregorian(tr+tz_hrs) for tr in [tret[1],tret[0],tret[4]]]
                        )
                break
            # Step just past this (non-matching) eclipse's own contact
            # window before asking Swiss Ephemeris for the next one.
            # Step one day past this eclipse's maximum (tret[0] is always populated;
            # contact slots can be 0.0 when a phase does not occur).
            jd = (tret[0] - 1.0) if search_backward else (tret[0] + 1.0)
        else:
            return None
    else:  # GLOBAL
        eclmask = solar_eclipse_type
        retflag, tret = swe.sol_eclipse_when_glob(jd_ut, flags=flags, ecltype=eclmask, backwards=search_backward)
        if retflag == -1: return None
        results = (_solar_type_str_from_retflag(retflag),
                [utils.jd_to_gregorian(tr+tz_hrs) for tr in [tret[2],tret[0],tret[3]]]
                )
    if show_maximum_eclipse_global_location and eclipse_location_type==EclipseLocation.GLOBAL:
        # Swiss Ephemeris docs 8.3/8.5: sol_eclipse_when_glob tret[0] = time of MAXIMUM eclipse
        # (tret[2] is the BEGIN); 2nd argument of sol_eclipse_where is the ephemeris flag (ifl).
        retflag,geopos,_ = swe.sol_eclipse_where(tret[0],flags=flags)
        if retflag == -1:
            print("Unable to find maximum eclipse location")
            return results
        else:
            return [results,(geopos[1],geopos[0])] # latitude,longitude because swiss ephimeris return long,lat
    return results
def next_lunar_eclipse(
    jd_local: float,
    place:Tuple[str,float,float,float], #(Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
    eclipse_location_type: int = EclipseLocation.GLOBAL,
    lunar_eclipse_type: int = LunarEclipseType.ANY,
    search_backward:bool = False, 
    flags: int = DEFAULT_FLAGS,
    show_maximum_eclipse_global_location=False,
    max_tries: int = DEFAULT_MAX_TRIES,
) -> Optional[Tuple[float, float, float]]:
    """
        Find next/previous lunar eclipse and return (start_local_jd, max_local_jd, end_local_jd).
        @param jd_local: user's LOCAL JD
        @param param: place: (Place name,latitude,longitude,time_zone_hours e.g. ('US City',-13.0,-84.0,-6.0)
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL.
             LOCAL returns the next eclipse seen at the place.
             GLOBAL returns the next eclipse whether or not it is seen at the place.
        @param lunar_eclipse_type: one of LunarEclipseType.* (ANY/TOTAL/PARTIAL/PENUMBRAL).
             Honored for BOTH LOCAL and GLOBAL searches: for LOCAL, since
             Swiss Ephemeris's own local-eclipse search has no type-filter
             parameter, this is enforced by retrying (up to max_tries times)
             past each non-matching local eclipse found.
        @param search_backward = False (Default). If True - Find previous date
        @param max_tries: for LOCAL searches only, maximum number of
            successive local eclipses to examine before giving up on
            finding one that matches lunar_eclipse_type (default 40).
            Unused for GLOBAL (Swiss Ephemeris's own ecltype mask finds a
            match directly).
        if show_maximum_eclipse_global_location = False (Default)
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd]
        if show_maximum_eclipse_global_location = True  Only for GLOBAL option
            @return eclipse_type, [eclipse_begin_jd,eclipse_max_jd,eclipse_end_jd],(Max_ecl_latitude,Max_ecl_longitude)
        NOTE: Max_ecl_longitude and latitude - may be in middle of a sea or inhabitant places
            You can use reverse_geocode or reverse_geocoder to find the nearest habitant place
        eclipse_type = "hybrid", "total", "penumbral", "partial"
        Note: !!! Sometimes date may have -4173 year - which means that eclipse portion is not visible
    """
    if place is not None:
        _,lat,long,tz = place; ele = getattr(place, 'elevation', 0.0) or 0.0
    tz_hrs = tz/24.0 if place is not None else 0.0
    jd_ut = jd_local - tz_hrs
    if eclipse_location_type == EclipseLocation.LOCAL:
        if place is None:
            raise ValueError("place is required for LOCAL lunar eclipse search")
        geopos = (long, lat, ele)  # (lon, lat, height)
        jd = jd_ut
        for _ in range(max_tries):
            retflag, tret, _ = swe.lun_eclipse_when_loc(jd, geopos, flags=flags, backwards=search_backward)
            if retflag == -1: return None
            if _lunar_type_matches(retflag, lunar_eclipse_type):
                results = (_lunar_type_str_from_retflag(retflag),
                    [_safe_tret_to_gregorian(tret[6], tz_hrs),   # penumbral_begin
                     _safe_tret_to_gregorian(tret[2], tz_hrs),   # partial_begin
                     _safe_tret_to_gregorian(tret[0], tz_hrs),             # eclipse_max (always populated)
                     _safe_tret_to_gregorian(tret[3], tz_hrs),   # partial_end
                     _safe_tret_to_gregorian(tret[7], tz_hrs)]   # penumbral_end
                    )
                break
            # Step just past this (non-matching) eclipse's own contact
            # window before asking Swiss Ephemeris for the next one.
            # Step one day past this eclipse's maximum. Docs 8.9: tret[6]/tret[7] (penumbral
            # begin/end) can be 0.0 when not visible locally; stepping from 0.0 would restart
            # the search at JD 0 (4713 BC). tret[0] (maximum) is always populated.
            jd = (tret[0] - 1.0) if search_backward else (tret[0] + 1.0)
        else:
            return None
    else:  # GLOBAL
        eclmask = lunar_eclipse_type
        retflag, tret = swe.lun_eclipse_when(jd_ut, flags=flags, ecltype=eclmask, backwards=search_backward)
        if retflag == -1: return None
        results = (_lunar_type_str_from_retflag(retflag),
            [_safe_tret_to_gregorian(tret[6], tz_hrs),
             _safe_tret_to_gregorian(tret[2], tz_hrs),
             _safe_tret_to_gregorian(tret[0], tz_hrs),
             _safe_tret_to_gregorian(tret[3], tz_hrs),
             _safe_tret_to_gregorian(tret[7], tz_hrs)]
            )
    if show_maximum_eclipse_global_location and eclipse_location_type==EclipseLocation.GLOBAL:
        # Swiss Ephemeris has no "lun_eclipse_where" (sol_eclipse_where is for SOLAR eclipses only).
        # Place of best visibility = sub-lunar point at maximum eclipse (tret[0]):
        # latitude = Moon's declination, longitude = Moon's right ascension - Greenwich sidereal time.
        try:
            eq_flags = (flags & ~swe.FLG_SIDEREAL) | swe.FLG_EQUATORIAL
            (ra, dec, _dist, *_), _ = swe.calc_ut(tret[0], swe.MOON, eq_flags)
            gst_deg = swe.sidtime(tret[0]) * 15.0
            lon = ((ra - gst_deg + 180.0) % 360.0) - 180.0
            return [results,(dec, lon)] # latitude,longitude
        except Exception as e:
            print("Unable to find maximum eclipse location", e)
            return results
    return results
# ---------- Example usage ----------
if __name__ == "__main__":
    utils.set_language('en')
    from jhora import const
    const.use_24hour_format_in_to_dms = False
    dob = drik.Date(2026, 1, 1)
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
                                    lunar_eclipse_type=LunarEclipseType.TOTAL,search_backward=backward_search,
                                    show_maximum_eclipse_global_location=True)
    ecl_str = utils.resource_strings[l_glob[0]+'_str']+' '+utils.resource_strings['lunar_str']+' '+ utils.resource_strings['eclipse_str']
    if l_glob: print('Lunar (Global, Partial):', ecl_str,[(y,m,d,utils.to_dms(fh)) for y,m,d,fh in l_glob[1]],geopos)
