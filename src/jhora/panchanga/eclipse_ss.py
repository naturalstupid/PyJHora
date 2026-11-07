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
eclipse_ss.py
================
Surya Siddhantha (classical) eclipse engine. Fully self-contained --
depends only on jhora.panchanga.surya_sidhantha for planet longitudes,
tithi, daily motion, and ayanamsa; performs all eclipse-specific
geometry (lunar/solar possibility, magnitude, parallax correction)
internally.

Reference: S. Balachandra Rao, "Ancient Indian Astronomy: Planetary
Positions and Eclipses" -- Section 9.7 (lunar eclipse per Surya
Siddhantha) and Section 10.3 (solar eclipse per Surya Siddhantha,
including the lambana/nati parallax correction).

Public API:
    is_lunar_eclipse(jd_full_moon, place) -> dict
    next_lunar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) or None
    is_solar_eclipse(jd_new_moon, place) -> dict
    next_solar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) or None
"""
import math
from jhora import utils, const
from jhora.panchanga import drik

sind = lambda x: math.sin(math.radians(x))
cosd = lambda x: math.cos(math.radians(x))
tand = lambda x: math.tan(math.radians(x))
asind = lambda x: math.degrees(math.asin(max(-1.0, min(1.0, x))))
atand = lambda x: math.degrees(math.atan(x))
atan2d = lambda y, x: math.degrees(math.atan2(y, x))

_R = 3438.0  # Classical "Indian sine" radius (Surya Siddhantha convention)


class EclipseLocation:
    """ Visibility scope of the search. LOCAL: an eclipse in which the Sun (solar) or the Moon (lunar) is below the horizon of the place at
        every contact is skipped. GLOBAL: the next eclipse is returned whether or not it is seen at the place. """
    LOCAL = 0
    GLOBAL = 1


class SolarEclipseType:
    """ Filter for next_solar_eclipse(): ANY, TOTAL, or PARTIAL. """
    ANY = 0
    TOTAL = 1
    PARTIAL = 2


class LunarEclipseType:
    """ Filter for next_lunar_eclipse(): ANY, TOTAL, or PARTIAL. """
    ANY = 0
    TOTAL = 1
    PARTIAL = 2


def _ss():
    """ Returns the active Surya Siddhantha panchanga module (classical
        or modern-sighra variant). Both variants share identical
        eclipse geometry; only planet-longitude computation differs,
        which this module accesses generically through the returned
        module's own functions. """
    from jhora.panchanga import surya_sidhantha as ss
    return ss


def _ss_moon_latitude(jd, place):
    """ Moon's celestial latitude at jd, in degrees.
        @param jd: Julian Day (local civil time)
        @param place: drik.Place / SS Place struct
        @return: latitude in degrees (signed) """
    ss = _ss()
    moon_long = ss._sidereal_longitude_impl(jd, place, const._MOON)
    rahu_long = ss._sidereal_longitude_impl(jd, place, const._RAHU)
    beta_arcmin = 270.0 * sind(moon_long - rahu_long)
    return beta_arcmin / 60.0


def _ss_eclipse_diameters(jd, place):
    """ Angular diameters of the Sun, Moon, and Earth's umbral shadow at
        jd, scaled from each body's true daily motion.
        @param jd: Julian Day (local civil time)
        @param place: drik.Place / SS Place struct
        @return: (sun_diameter_deg, moon_diameter_deg, shadow_diameter_deg) """
    ss = _ss()
    sdm = abs(ss.daily_planet_speed(jd, place, const.SUN_ID)) * 60.0
    mdm = abs(ss.daily_planet_speed(jd, place, const.MOON_ID)) * 60.0
    scdia = sdm * 6500.0 / 59.136
    sdiay = scdia * 4320000.0 / 57753336.0
    sdia = sdiay / 15.0
    mdiay = mdm * 480.0 / 790.581
    mdia = mdiay / 15.0
    ecdia = mdm * 1600.0 / 790.581
    scdedia = scdia - 1600.0
    shdiay = ecdia - scdedia * 480.0 / 6500.0
    shdia = shdiay / 15.0
    return sdia / 60.0, mdia / 60.0, shdia / 60.0


def is_lunar_eclipse(jd_full_moon, place):
    """ Evaluates whether the full moon at jd_full_moon produces a
        lunar eclipse.
        @param jd_full_moon: Julian Day of the full moon instant
        @param place: drik.Place / SS Place struct
        @return: dict with keys sun_diameter, moon_diameter,
            shadow_diameter, moon_latitude (all degrees), grasa
            (magnitude, degrees), is_possible (bool), is_total (bool),
            half_duration_days (float or None if not possible) """
    sdia, mdia, shdia = _ss_eclipse_diameters(jd_full_moon, place)
    mlat = _ss_moon_latitude(jd_full_moon, place)
    grasa = 0.5 * (mdia + shdia) - abs(mlat)
    is_possible = grasa > 0.0
    is_total = grasa > mdia
    half_dur = None
    if is_possible:
        ss = _ss()
        sdm = abs(ss.daily_planet_speed(jd_full_moon, place, const.SUN_ID))
        mdm = abs(ss.daily_planet_speed(jd_full_moon, place, const.MOON_ID))
        half_dur = math.sqrt(((shdia + mdia) / 2.0) ** 2 - mlat ** 2) / (mdm - sdm)
    return {
        'sun_diameter': sdia, 'moon_diameter': mdia, 'shadow_diameter': shdia,
        'moon_latitude': mlat, 'grasa': grasa,
        'is_possible': is_possible, 'is_total': is_total,
        'half_duration_days': half_dur,
    }


def _sun_is_up(jd, place):
    """ Whether the Sun is above the horizon: the Julian Day lies between the sunrise and the sunset of its own civil day.
        @param jd: Julian Day (local civil time)
        @param place: Place struct
        @return: True if the Sun is up """
    eng = _ss()
    return eng.sunrise(jd, place)[2] <= jd <= eng.sunset(jd, place)[2]


def _lunar_seen_locally(eclipse_location_type, place, jd_times):
    """ Whether a lunar eclipse is returned under the scope. With EclipseLocation.LOCAL the Moon, opposite the Sun, must be above the horizon (the Sun down) at one or more of the contacts (with EclipseLocation.GLOBAL every eclipse is returned).
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param place: Place struct
        @param jd_times: Julian Days (local civil time) of the contacts of the eclipse
        @return: True if the eclipse is to be returned """
    if eclipse_location_type != EclipseLocation.LOCAL:
        return True
    return any(not _sun_is_up(t, place) for t in jd_times)


def _solar_seen_locally(eclipse_location_type, place, jd_times):
    """ Whether a solar eclipse is returned under the scope. With EclipseLocation.LOCAL the Sun must be above the horizon at one or more of the contacts (with EclipseLocation.GLOBAL every eclipse is returned).
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param place: Place struct
        @param jd_times: Julian Days (local civil time) of the contacts of the eclipse
        @return: True if the eclipse is to be returned """
    if eclipse_location_type != EclipseLocation.LOCAL:
        return True
    return any(_sun_is_up(t, place) for t in jd_times)


def next_lunar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                        lunar_eclipse_type=LunarEclipseType.ANY, search_backward=False,
                        show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) full moon producing a lunar
        eclipse matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: drik.Place / SS Place struct
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Moon is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param lunar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead
            of the next
        @param show_maximum_eclipse_global_location: accepted for
            signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before
            giving up
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples,
            or None if no matching eclipse is found within max_tries """
    ss = _ss()
    direction = -1 if search_backward else 1
    search_jd = jd_local
    for _ in range(max_tries):
        ti = ss.tithi(search_jd, place)[0]
        jd_full = ss.full_moon(search_jd, place, ti, opt=direction)
        info = is_lunar_eclipse(jd_full, place)
        if info['is_possible']:
            is_match = (
                lunar_eclipse_type == LunarEclipseType.ANY or
                (lunar_eclipse_type == LunarEclipseType.TOTAL and info['is_total']) or
                (lunar_eclipse_type == LunarEclipseType.PARTIAL and not info['is_total'])
            )
            if is_match:
                hd = info['half_duration_days']
                if _lunar_seen_locally(eclipse_location_type, place, (jd_full - hd, jd_full, jd_full + hd)):
                    type_str = "total" if info['is_total'] else "partial"
                    begin = utils.jd_to_gregorian(jd_full - hd)
                    middle = utils.jd_to_gregorian(jd_full)
                    end = utils.jd_to_gregorian(jd_full + hd)
                    return type_str, [begin, middle, end]
        search_jd = jd_full + 20.0 * direction
    return None


def _ss_local_sidereal_time_deg(jd, place):
    """ Local sidereal time at jd, in degrees (0-360).
        @param jd: Julian Day, local civil time
        @param place: drik.Place / SS Place struct (place.timezone in
            hours, place.longitude in degrees east)
        @return: local sidereal time in degrees """
    jd_ut = jd - place.timezone / 24.0
    t = (jd_ut - 2451545.0) / 36525.0
    gst_deg = (280.46061837 + 360.98564736629 * (jd_ut - 2451545.0)
               + 0.000387933 * t * t - t * t * t / 38710000.0) % 360.0
    lst_deg = (gst_deg + place.longitude) % 360.0
    return lst_deg


def _ss_madhya_lagna(jd, place, eps_deg=24.0):
    """ Madhya Lagna (meridian ecliptic point, "MC"), tropical, at jd.
        @param jd: Julian Day, local civil time
        @param place: drik.Place / SS Place struct
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: MC longitude in degrees (0-360), tropical frame """
    lst = _ss_local_sidereal_time_deg(jd, place)
    if abs(lst - 90) < 1e-9:
        return 90.0
    if abs(lst - 270) < 1e-9:
        return 270.0
    a2 = atand(tand(lst) / cosd(eps_deg))
    mc = (180 + a2) if 90 < lst < 270 else a2
    return mc % 360.0


def _ss_tropical_ascendant(jd, place, eps_deg=24.0):
    """ Orient ecliptic point (Lagna), tropical, at jd -- the ascendant
        in the same tropical frame as _ss_madhya_lagna(), via the
        standard right-ascension-based ascendant formula.
        @param jd: Julian Day, local civil time
        @param place: drik.Place / SS Place struct
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: Lagna longitude in degrees (0-360), tropical frame """
    lst = _ss_local_sidereal_time_deg(jd, place)
    lat = place.latitude
    numerator = cosd(lst)
    denominator = -sind(eps_deg) * tand(lat) - cosd(eps_deg) * sind(lst)
    return atan2d(numerator, denominator) % 360.0


def _ss_parallax_chain(jd, place, eps_deg=24.0):
    """ Computes the solar-eclipse parallax correction chain: drkkshepa
        (Rsine of ecliptic zenith distance), lambana (parallax in
        longitude, in nadis), and the declination of the meridian
        ecliptic point.
        @param jd: Julian Day, local civil time (candidate instant of
            conjunction)
        @param place: drik.Place / SS Place struct
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: (lambana_nadis, drkkshepa, dec_mc) where lambana_nadis
            is signed parallax correction in nadis (1 day = 60 nadis),
            drkkshepa is in R-sine (arcmin) units, dec_mc is in degrees """
    ss = _ss()
    lagna_deg = _ss_tropical_ascendant(jd, place, eps_deg=eps_deg)
    mc = _ss_madhya_lagna(jd, place, eps_deg=eps_deg)

    orient_sine = sind(eps_deg) * _R * sind(lagna_deg) / cosd(place.latitude)
    dec_mc = asind(sind(eps_deg) * sind(mc))
    merid_zen = dec_mc - place.latitude
    sn_merz = _R * sind(merid_zen)
    osmz = orient_sine * sn_merz / _R

    drkkshepa = math.sqrt(max(0.0, sn_merz ** 2 - osmz ** 2))
    drggati = math.sqrt(max(0.0, _R ** 2 - drkkshepa ** 2))
    cheda = (_R * sind(30.0)) ** 2 / drggati if drggati != 0 else float('inf')

    sun_long = ss._sidereal_longitude_impl(jd, place, const._SUN)
    tropical_sun_long = (sun_long + ss.surya_sidhantha_ayanamsa(jd, place)) % 360.0

    lambana_nadis = (_R * sind(mc - tropical_sun_long) / cheda
                      if cheda not in (0.0, float('inf')) else 0.0)
    return lambana_nadis, drkkshepa, dec_mc


def is_solar_eclipse(jd_new_moon, place):
    """ Evaluates whether the new moon at jd_new_moon produces a solar
        eclipse at the given place, including lambana/nati parallax
        correction.
        @param jd_new_moon: Julian Day of the (mean/true) new moon
            instant, local civil time
        @param place: drik.Place / SS Place struct
        @return: dict with keys sun_diameter, moon_diameter (degrees),
            moon_latitude (degrees, parallax-corrected), grasa
            (magnitude, degrees), is_possible (bool), is_total (bool),
            jd_apparent_conjunction (Julian Day of the parallax-
            corrected apparent conjunction) """
    ss = _ss()
    jd_app = jd_new_moon
    drkkshepa = 0.0
    for _ in range(4):
        lambana_nadis, drkkshepa, dec_mc = _ss_parallax_chain(jd_app, place)
        jd_app = jd_new_moon + lambana_nadis / 60.0

    mdm_deg = abs(ss.daily_planet_speed(jd_app, place, const.MOON_ID))
    mdm_arcmin = mdm_deg * 60.0
    nati_arcmin = (mdm_arcmin / 15.0) * (drkkshepa / _R)

    sdia, mdia, shdia = _ss_eclipse_diameters(jd_app, place)
    mlat = _ss_moon_latitude(jd_app, place) + nati_arcmin / 60.0
    grasa = 0.5 * (sdia + mdia) - abs(mlat)
    is_possible = grasa > 0.0
    is_total = grasa > sdia
    return {
        'sun_diameter': sdia, 'moon_diameter': mdia,
        'moon_latitude': mlat, 'grasa': grasa,
        'is_possible': is_possible, 'is_total': is_total,
        'jd_apparent_conjunction': jd_app,
    }


def next_solar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                        solar_eclipse_type=SolarEclipseType.ANY, search_backward=False,
                        show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) new moon producing a solar eclipse
        at the given place, matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: drik.Place / SS Place struct
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Sun is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param solar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead
            of the next
        @param show_maximum_eclipse_global_location: accepted for
            signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before
            giving up
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples.
            begin and end are currently reported equal to middle; only
            middle (the parallax-corrected apparent conjunction) is
            populated with a distinct value. Returns None if no
            matching eclipse is found within max_tries. """
    ss = _ss()
    direction = -1 if search_backward else 1
    search_jd = jd_local
    for _ in range(max_tries):
        ti = ss.tithi(search_jd, place)[0]
        jd_new = ss.new_moon(search_jd, place, ti, opt=direction)
        info = is_solar_eclipse(jd_new, place)
        if info['is_possible']:
            is_match = (
                solar_eclipse_type == SolarEclipseType.ANY or
                (solar_eclipse_type == SolarEclipseType.TOTAL and info['is_total']) or
                (solar_eclipse_type == SolarEclipseType.PARTIAL and not info['is_total'])
            )
            if is_match and _solar_seen_locally(eclipse_location_type, place, (info['jd_apparent_conjunction'],)):
                type_str = "total" if info['is_total'] else "partial"
                middle = utils.jd_to_gregorian(info['jd_apparent_conjunction'])
                return type_str, [middle, middle, middle]
        search_jd = jd_new + 20.0 * direction
    return None
