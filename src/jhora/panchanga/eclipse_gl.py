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
eclipse_gl.py
================
Graha Laaghavam (GL) eclipse engine. Depends on jhora.panchanga.graha_laaghavam
for planet longitudes, tithi, daily motion, and ascendant; performs all
eclipse-specific geometry (lunar/solar possibility, magnitude, parallax
correction) internally.

Reference: S. Balachandra Rao, "Ancient Indian Astronomy: Planetary
Positions and Eclipses" -- Section 9.9 (lunar eclipse per Graha Laghavam)
and Section 10.4 (solar eclipse per Graha Laghavam).

Diameters/Sara/Grasa are computed in the book's own native unit (angulas,
1 angula = 3 arcmin) and converted to degrees only when building the
returned dict, so the dict shape/units match eclipse_ss.py/eclipse_kk.py
exactly for direct cross-engine comparison.

NOTE: the solar-eclipse Nati (parallax-in-latitude) refinement described
in Ch 10.4 is not applied here -- the book's own Sec 10.4 worked example
is too badly OCR-corrupted at that specific step to reconstruct reliably;
grasa/half-duration instead use the same unrefined Sara as the lunar
engine, matching eclipse_kk.py's own documented omission of a nati term.

Public API:
    is_lunar_eclipse(jd_full_moon, place) -> dict
    next_lunar_eclipse(jd_local, place, ...) -> (type_str, events) or None
        events = [begin, middle, end] (partial) or
                 [begin, totality_begin, middle, totality_end, end] (total)
    is_solar_eclipse(jd_new_moon, place) -> dict
    next_solar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) or None
"""
import math
from jhora import utils, const

sind = lambda x: math.sin(math.radians(x))
cosd = lambda x: math.cos(math.radians(x))
tand = lambda x: math.tan(math.radians(x))
asind = lambda x: math.degrees(math.asin(max(-1.0, min(1.0, x))))
atand = lambda x: math.degrees(math.atan(x))
atan2d = lambda y, x: math.degrees(math.atan2(y, x))

_ANGULA_TO_DEG = 3.0 / 60.0   # 1 angula = 3 arcmin (GL.pdf Ch 9.9 note)

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

def _gl():
    """ Returns the Graha Laaghavam panchanga module. """
    from jhora.panchanga import graha_laaghavam as gl
    return gl

def _gl_bhuja_past_180(angle_deg):
    """ GL's Bhuja reduction of the Moon-minus-Rahu angle (Ch 9.9): the
        angular distance from the nearest node.
        @param angle_deg: Moon longitude minus Rahu longitude, degrees
        @return: bhuja in degrees, 0-90 """
    a = angle_deg % 360.0
    if a > 180.0:
        a -= 180.0
    return 180.0 - a if a > 90.0 else a

def _gl_moon_sara(moon_long, rahu_long):
    """ Moon's latitude (Sara), in angulas, per GL's linear
        approximation (Ch 9.9): Sara = (11/7) * Bhuja(Moon - Rahu).
        @return: Sara in angulas (unsigned magnitude) """
    bhuja = _gl_bhuja_past_180((moon_long - rahu_long) % 360.0)
    return (11.0 / 7.0) * bhuja

def _gl_sun_moon_diameters(jd, place):
    """ Sun's and Moon's angular diameters (Ch 9.9/10.4), in angulas,
        scaled from each body's true daily motion.
        @return: (sun_diameter_angulas, moon_diameter_angulas) """
    gl = _gl()
    sdm = abs(gl.daily_planet_speed(jd, place, const.SUN_ID)) * 60.0   # arcmin/day
    mdm = abs(gl.daily_planet_speed(jd, place, const.MOON_ID)) * 60.0  # arcmin/day
    sdia = (sdm - 55.0) / 5.0 + 10.0
    mdia = mdm / 74.0
    return sdia, mdia

def _gl_half_duration_ghatikas(semi_sum_plus_sara, grasa, diameter):
    """ Shared half-duration formula (Ch 9.9, reused structurally for
        the solar case in Ch 10.4): x = sqrt(semi_sum_plus_sara * 10 *
        grasa); half-duration = (x - x/6) / diameter, in ghatikas.
        @return: half-duration in ghatikas, or None if not computable """
    val = semi_sum_plus_sara * 10.0 * grasa
    if val < 0.0:
        return None
    x = math.sqrt(val)
    return (x - x / 6.0) / diameter if diameter else None

def is_lunar_eclipse(jd_full_moon, place):
    """ Evaluates whether the full moon at jd_full_moon produces a
        lunar eclipse.
        @param jd_full_moon: Julian Day of the full moon instant
        @param place: Place struct
        @return: dict with keys sun_diameter, moon_diameter,
            shadow_diameter, moon_latitude, grasa (all degrees),
            khagrasa (degrees, None unless total), is_possible (bool),
            is_total (bool), half_duration_days (float or None),
            half_duration_totality_days (float or None unless total) """
    gl = _gl()
    moon_long = gl._sidereal_longitude_impl(jd_full_moon, place, const._MOON)
    rahu_long = gl._sidereal_longitude_impl(jd_full_moon, place, const._RAHU)
    sdia, mdia = _gl_sun_moon_diameters(jd_full_moon, place)
    shdia = (36.0 / 11.0) * mdia - 8.0
    sara = _gl_moon_sara(moon_long, rahu_long)
    grasa = 0.5 * (mdia + shdia) - sara
    is_possible = grasa > 0.0
    is_total = is_possible and grasa > mdia
    khagrasa = (grasa - mdia) if is_total else None
    half_dur_gh = None
    half_dur_tot_gh = None
    if is_possible:
        half_dur_gh = _gl_half_duration_ghatikas(0.5 * (shdia + mdia) + sara, grasa, mdia)
        if is_total:
            manantara = 0.5 * (shdia - mdia)
            half_dur_tot_gh = _gl_half_duration_ghatikas(manantara + sara, khagrasa, mdia)
    return {
        'sun_diameter': sdia * _ANGULA_TO_DEG, 'moon_diameter': mdia * _ANGULA_TO_DEG,
        'shadow_diameter': shdia * _ANGULA_TO_DEG, 'moon_latitude': sara * _ANGULA_TO_DEG,
        'grasa': grasa * _ANGULA_TO_DEG,
        'khagrasa': khagrasa * _ANGULA_TO_DEG if khagrasa is not None else None,
        'is_possible': is_possible, 'is_total': is_total,
        'half_duration_days': half_dur_gh / 60.0 if half_dur_gh is not None else None,
        'half_duration_totality_days': half_dur_tot_gh / 60.0 if half_dur_tot_gh is not None else None,
    }

def _gl_vyagu_offset(jd, place):
    """ Vyagu (True Sun - Rahu) quadrant/Bhuja, for the sparsa/moksa
        half-duration asymmetry correction (Ch 9.9).
        @return: (offset_days, is_odd_quadrant) """
    gl = _gl()
    sun_long = gl._sidereal_longitude_impl(jd, place, const._SUN)
    rahu_long = gl._sidereal_longitude_impl(jd, place, const._RAHU)
    vyagu = (sun_long - rahu_long) % 360.0
    bhuja, _ = gl._bhuja_and_sign(vyagu)
    is_odd_quadrant = (vyagu % 180.0) < 90.0
    offset_days = (2.0 * bhuja) / 3600.0   # 2*bhuja(deg) taken directly as palas; 1 pala = 1/3600 day
    return offset_days, is_odd_quadrant

def _sun_is_up(jd, place):
    """ Whether the Sun is above the horizon: the Julian Day lies between the sunrise and the sunset of its own civil day.
        @param jd: Julian Day (local civil time)
        @param place: Place struct
        @return: True if the Sun is up """
    eng = _gl()
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
        @param place: Place struct
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Moon is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param lunar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead
            of the next
        @param show_maximum_eclipse_global_location: accepted for
            signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before
            giving up
        @return: (type_str, events) as (Y,M,D,fh) tuples. events =
            [begin, middle, end] (partial) or [begin, totality_begin,
            middle, totality_end, end] (total). Returns None if no
            matching eclipse is found within max_tries. """
    gl = _gl()
    direction = -1 if search_backward else 1
    search_jd = jd_local
    for _ in range(max_tries):
        ti = gl.tithi(search_jd, place)[0]
        jd_full = gl.full_moon(search_jd, place, ti, opt=direction)
        info = is_lunar_eclipse(jd_full, place)
        if info['is_possible']:
            is_match = (
                lunar_eclipse_type == LunarEclipseType.ANY or
                (lunar_eclipse_type == LunarEclipseType.TOTAL and info['is_total']) or
                (lunar_eclipse_type == LunarEclipseType.PARTIAL and not info['is_total'])
            )
            if is_match:
                type_str = "total" if info['is_total'] else "partial"
                offset_days, is_odd = _gl_vyagu_offset(jd_full, place)
                sthiti_days = info['half_duration_days']
                if is_odd:
                    sparsa_days, moksa_days = sthiti_days + offset_days, sthiti_days - offset_days
                else:
                    sparsa_days, moksa_days = sthiti_days - offset_days, sthiti_days + offset_days
                if not _lunar_seen_locally(eclipse_location_type, place, (jd_full - sparsa_days, jd_full, jd_full + moksa_days)):
                    search_jd = jd_full + 20.0 * direction
                    continue
                middle = utils.jd_to_gregorian(jd_full)
                begin = utils.jd_to_gregorian(jd_full - sparsa_days)
                end = utils.jd_to_gregorian(jd_full + moksa_days)
                if info['is_total']:
                    marda_days = info['half_duration_totality_days']
                    if is_odd:
                        sparsa_marda, moksa_marda = marda_days + offset_days, marda_days - offset_days
                    else:
                        sparsa_marda, moksa_marda = marda_days - offset_days, marda_days + offset_days
                    totality_begin = utils.jd_to_gregorian(jd_full - sparsa_marda)
                    totality_end = utils.jd_to_gregorian(jd_full + moksa_marda)
                    return type_str, [begin, totality_begin, middle, totality_end, end]
                return type_str, [begin, middle, end]
        search_jd = jd_full + 20.0 * direction
    return None

def _gl_eclipse_ayanamsa(jd, place):
    """ GL's own linear ayanamsa for eclipse computations (Ch 10.4):
        (Saka year elapsed - 444) / 60, in degrees.
        @return: ayanamsa in degrees """
    gl = _gl()
    lm = gl.lunar_month_date(jd, place)
    _, _, saka = gl.elapsed_year(jd, lm[0])
    return (saka - 444) / 60.0

def _gl_lambana_days(jd, place, ayanamsa_deg, eps_deg=24.0):
    """ GL's own Lambana (parallax-in-longitude) correction to the time
        of conjunction (Ch 10.4).
        @param ayanamsa_deg: precomputed _gl_eclipse_ayanamsa() value
        @return: signed lambana in days (apparent = true + this) """
    gl = _gl()
    nirayana_lagna = gl._ascendant_longitude(jd, place, eps_deg=eps_deg)
    tribhona_lagna = (nirayana_lagna - 90.0) % 360.0
    sayana_tribhona_lagna = (tribhona_lagna + ayanamsa_deg) % 360.0
    dec_nonagesimal = asind(sind(eps_deg) * sind(sayana_tribhona_lagna))
    natamsas = dec_nonagesimal - place.latitude
    x = natamsas / 22.0
    sq = x * x
    adj = sq + (sq - 2.0) / 2.0 if sq > 2.0 else sq
    hara = adj + 12.0
    true_sun = gl._sidereal_longitude_impl(jd, place, const._SUN)
    diff = (true_sun - tribhona_lagna) % 360.0
    bhuja, _ = gl._bhuja_and_sign(diff)
    numerator = (bhuja / 10.0) * (14.0 - bhuja / 10.0)
    lambana_ghatikas = numerator / hara if hara else 0.0
    diff_wrapped = ((true_sun - tribhona_lagna + 180.0) % 360.0) - 180.0
    lambana_ghatikas = -lambana_ghatikas if diff_wrapped > 0 else lambana_ghatikas
    return lambana_ghatikas / 60.0

def is_solar_eclipse(jd_new_moon, place, eps_deg=24.0, n_iter=4):
    """ Evaluates whether the new moon at jd_new_moon produces a solar
        eclipse at the given place, per GL's Ch 10.4 procedure: the
        true (geometric) conjunction instant is corrected to the
        apparent-conjunction instant by iterating GL's own Lambana
        formula.
        @param jd_new_moon: Julian Day of the (true) new moon instant,
            local civil time
        @param place: Place struct
        @param eps_deg: obliquity of the ecliptic in degrees
        @param n_iter: number of Lambana refinement passes
        @return: dict with keys sun_diameter, moon_diameter (degrees),
            moon_latitude (degrees), grasa (degrees), is_possible
            (bool), is_total (bool), jd_apparent_conjunction,
            half_duration_days (float or None) """
    gl = _gl()
    ayanamsa_deg = _gl_eclipse_ayanamsa(jd_new_moon, place)
    jd_app = jd_new_moon
    for _ in range(n_iter):
        jd_app = jd_new_moon + _gl_lambana_days(jd_app, place, ayanamsa_deg, eps_deg=eps_deg)
    moon_long = gl._sidereal_longitude_impl(jd_app, place, const._MOON)
    rahu_long = gl._sidereal_longitude_impl(jd_app, place, const._RAHU)
    sara = _gl_moon_sara(moon_long, rahu_long)
    sdia, mdia = _gl_sun_moon_diameters(jd_app, place)
    semi_sum = 0.5 * (sdia + mdia)
    grasa = semi_sum - sara
    is_possible = grasa > 0.0
    is_total = is_possible and grasa > min(sdia, mdia)
    half_dur_gh = _gl_half_duration_ghatikas(semi_sum + sara, grasa, mdia) if is_possible else None
    return {
        'sun_diameter': sdia * _ANGULA_TO_DEG, 'moon_diameter': mdia * _ANGULA_TO_DEG,
        'moon_latitude': sara * _ANGULA_TO_DEG, 'grasa': grasa * _ANGULA_TO_DEG,
        'is_possible': is_possible, 'is_total': is_total,
        'jd_apparent_conjunction': jd_app,
        'half_duration_days': half_dur_gh / 60.0 if half_dur_gh is not None else None,
    }

def next_solar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                        solar_eclipse_type=SolarEclipseType.ANY, search_backward=False,
                        show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) new moon producing a solar eclipse
        at the given place, matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place struct
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
            Returns None if no matching eclipse is found within
            max_tries. """
    gl = _gl()
    direction = -1 if search_backward else 1
    search_jd = jd_local
    for _ in range(max_tries):
        ti = gl.tithi(search_jd, place)[0]
        jd_new = gl.new_moon(search_jd, place, ti, opt=direction)
        info = is_solar_eclipse(jd_new, place)
        if info['is_possible']:
            is_match = (
                solar_eclipse_type == SolarEclipseType.ANY or
                (solar_eclipse_type == SolarEclipseType.TOTAL and info['is_total']) or
                (solar_eclipse_type == SolarEclipseType.PARTIAL and not info['is_total'])
            )
            if is_match:
                type_str = "total" if info['is_total'] else "partial"
                jd_app = info['jd_apparent_conjunction']
                half_dur_days = info['half_duration_days'] or 0.0
                if not _solar_seen_locally(eclipse_location_type, place, (jd_app - half_dur_days, jd_app, jd_app + half_dur_days)):
                    search_jd = jd_new + 20.0 * direction
                    continue
                middle = utils.jd_to_gregorian(jd_app)
                begin = utils.jd_to_gregorian(jd_app - half_dur_days)
                end = utils.jd_to_gregorian(jd_app + half_dur_days)
                return type_str, [begin, middle, end]
        search_jd = jd_new + 20.0 * direction
    return None
