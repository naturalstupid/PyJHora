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
""" eclipse_vs.py
    ==============
    Vateswara Siddhanta eclipse engine (const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA). Self-contained: planet longitudes, speeds, sunrise,
    sunset and the Lagna come from jhora.panchanga.vateshwara_sidhantha; the eclipse geometry is the book's.
    Source: K. S. Shukla, "Vatesvara-Siddhanta and Gola of Vatesvara", Part II, Ch.IV (Lunar eclipse) and Ch.V (Solar eclipse).

    Public API:
        is_lunar_eclipse(jd_full_moon, place) -> dict
        next_lunar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) for a partial eclipse,
                                                    (type_str, [begin, immersion, middle, emersion, end]) for a total eclipse, or None
        is_solar_eclipse(jd_new_moon, place) -> dict
        next_solar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) or None
    Every time is a (year, month, day, local clock hours) tuple; all contacts of the eclipse found are always returned, including those at
    which the body is below the horizon.

    Lunar eclipse (Ch.IV): true diameters of the Sun, Moon and Shadow (vs.11); Moon's latitude 270 x Rsin(Moon - node) / R (vs.19);
        measure of eclipse and its type (vs.21-22); sthityardha and vimardardha with the iteration of the Moon's latitude at the contacts
        (vs.24-30). The middle of the eclipse is the opposition.
    Solar eclipse (Ch.V): central ecliptic point, madhyajya, udayajya, drkksepa and drggati (Sec.1 vs.4-14, 31); lambana and the apparent
        conjunction by iteration (vs.15-27); nati and the Moon's true latitude (Sec.2); contacts, immersion and emersion with the lambana
        applied to each (Sec.3). The Moon's semi-diameter is reduced for the visible contacts (Sec.3 vs.8-9).
    Scope: lunar eclipses are geocentric (the same times for every place); solar eclipses are for the given place. With EclipseLocation.LOCAL an
        eclipse that is not seen at the place (lunar: the Moon is above the horizon at none of the contacts; solar: the Sun is above the horizon at
        none of begin, middle and end) is skipped and the next one that is seen is returned; with EclipseLocation.GLOBAL the next eclipse is returned
        whether or not it is seen. The book has no ground-track model, so show_maximum_eclipse_global_location is accepted and not used.
        The book names total and partial eclipses; "annular" is reported when the Moon lies wholly inside the Sun's disc. Penumbral and
        hybrid eclipses do not exist in the book.
    Switches (const.py): vs_eclipse_diameter_method_default, vs_lambana_method_default, vs_solar_reduce_moon_semidiameter,
        vs_nati_include_moon_latitude. """
import math
from collections import namedtuple
from jhora import utils, const
from jhora.panchanga import vateshwara_sidhantha as vs


class EclipseLocation:
    """ Visibility scope of the search. LOCAL: an eclipse in which the Sun (solar) or the Moon (lunar) is below the horizon of the place at
        every contact is skipped. GLOBAL: the next eclipse is returned whether or not it is seen at the place. """
    LOCAL = 0
    GLOBAL = 1


class EclipseType:
    """ Kind of eclipse. """
    SOLAR = 0
    LUNAR = 1


class SolarEclipseType:
    """ Filter for next_solar_eclipse(). HYBRID does not exist in the book: a search for it returns None. """
    ANY = 0
    TOTAL = 1
    PARTIAL = 2
    ANNULAR = 3
    HYBRID = 4


class LunarEclipseType:
    """ Filter for next_lunar_eclipse(). PENUMBRAL does not exist in the book: a search for it returns None. """
    ANY = 0
    TOTAL = 1
    PARTIAL = 2
    PENUMBRAL = 3


DEFAULT_FLAGS = 0
DEFAULT_MAX_TRIES = 240   # lunations examined (about 19 years)
_R = const.VS_RSINE_RADIUS
_EARTH_SEMI_DIAMETER = const.VS_EARTH_DIAMETER_YOJANAS / 2.0
_SOLAR_GEOMETRY = namedtuple('_SolarGeometry', 'jd ayanamsa sun_sayana rising_sayana vitribha drkksepa vitribha_sanku drggati east '
                                               'north_of_zenith ra_meridian_deg above_horizon')
_FRAME = namedtuple('_Frame', 'sun_speed moon_speed sun_mean moon_mean sun_distance moon_distance sun_diameter moon_diameter shadow_diameter')


def _rsin(angle_deg):
    """ Signed Rsine, in minutes, of any angle, read from the Rsine table of the module (Ch.II Table 13).
        @param angle_deg: angle in degrees
        @return: Rsine in minutes (positive for 0..180 degrees, negative for 180..360) """
    a = angle_deg % 360.0
    v = vs._vs_rsine(vs._vs_bhuja(a) * 60.0)
    return v if a < 180.0 else -v


def _rcos(angle_deg):
    """ Signed Rcosine, in minutes.
        @param angle_deg: angle in degrees
        @return: Rcosine in minutes """
    return _rsin(angle_deg + 90.0)


def _wrap180(angle_deg):
    """ Angle reduced to (-180, 180].
        @param angle_deg: angle in degrees
        @return: reduced angle in degrees """
    return (angle_deg + 180.0) % 360.0 - 180.0


def _moon_latitude_minutes(moon_longitude, node_longitude):
    """ Moon's celestial latitude, Ch.IV vs.19: 270 x Rsin(Moon + westward node) / R; the node of the module is measured eastwards, so the
        argument is Moon - node. North is positive.
        @param moon_longitude: sidereal longitude of the Moon in degrees
        @param node_longitude: sidereal longitude of the ascending node (Rahu) in degrees
        @return: latitude in minutes """
    return const.VS_MOON_GREATEST_LATITUDE * _rsin(moon_longitude - node_longitude) / _R


def _longitudes(jd, place):
    """ Sidereal longitudes of the Sun, the Moon and the ascending node at a local civil-time Julian day.
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @return: (sun, moon, node) in degrees """
    return (vs._sidereal_longitude_impl(jd, place, const._SUN), vs._sidereal_longitude_impl(jd, place, const._MOON),
            vs._sidereal_longitude_impl(jd, place, const._RAHU))


def _phase(jd, place):
    """ Moon minus Sun longitude, in degrees (0-360).
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct
        @return: elongation in degrees """
    return (vs._sidereal_longitude_impl(jd, place, const._MOON) - vs._sidereal_longitude_impl(jd, place, const._SUN)) % 360.0


def _refine_syzygy(jd, place, target_deg):
    """ Instant at which the elongation of the Moon from the Sun equals target_deg, found by the book's iteration (the error in degrees is
        divided by the relative daily motion and subtracted from the time until it vanishes).
        @param jd: Julian Day Number (local civil time) near the instant
        @param place: Place struct
        @param target_deg: 0 = conjunction (new moon), 180 = opposition (full moon)
        @return: Julian Day Number of the instant """
    t = jd
    for _ in range(30):
        err = _wrap180(_phase(t, place) - target_deg)
        if abs(err) < 1e-9:
            break
        rate = _wrap180(_phase(t + 0.01, place) - _phase(t - 0.01, place)) / 0.02
        t -= err / rate
    return t


def _syzygy_jd(jd, place, target_deg, direction):
    """ The next (direction=1) or previous (direction=-1) instant, strictly after or before jd, at which the elongation equals target_deg.
        @param jd: Julian Day Number (local civil time) from which the search starts
        @param place: Place struct
        @param target_deg: 0 = new moon, 180 = full moon
        @param direction: +1 = next, -1 = previous
        @return: Julian Day Number of the syzygy """
    mean_rate = vs._vs_daily_motion(const._MOON) - vs._vs_daily_motion(const._SUN)
    ph = _phase(jd, place)
    gap = ((target_deg - ph) if direction > 0 else (ph - target_deg)) % 360.0
    if gap < 1e-6:
        gap = 360.0
    return _refine_syzygy(jd + direction * gap / mean_rate, place, target_deg)


def _frame(jd, place):
    """ True and mean daily motions, true distances and true angular diameters of the Sun, Moon and Shadow (Ch.IV vs.6-18).
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct
        @return: namedtuple (sun_speed, moon_speed [degrees/day], sun_mean, moon_mean [degrees/day], sun_distance, moon_distance [yojanas],
            sun_diameter, moon_diameter, shadow_diameter [minutes]) """
    sun_speed = abs(vs.daily_planet_speed(jd, place, const.SUN_ID))
    moon_speed = abs(vs.daily_planet_speed(jd, place, const.MOON_ID))
    sun_mean = vs._vs_daily_motion(const._SUN)
    moon_mean = vs._vs_daily_motion(const._MOON)
    sun_distance = const.VS_SUN_MEAN_DISTANCE_YOJANAS * sun_mean / sun_speed
    moon_distance = const.VS_MOON_MEAN_DISTANCE_YOJANAS * moon_mean / moon_speed
    if const.vs_eclipse_diameter_method_default == const.VS_ECLIPSE_DIAMETER_METHOD.DAILY_MOTION:
        sun_dia = const.VS_MEAN_DIAMETER_MINUTES * sun_speed / sun_mean
        moon_dia = const.VS_MEAN_DIAMETER_MINUTES * moon_speed / moon_mean
        f_moon, f_sun = const.VS_SHADOW_DAILY_MOTION_FACTORS
        shadow_dia = f_moon * moon_speed * 60.0 - f_sun * sun_speed * 60.0
    else:
        sun_dia = const.VS_SUN_DIAMETER_YOJANAS * _R / sun_distance
        moon_dia = const.VS_MOON_DIAMETER_YOJANAS * _R / moon_distance
        earth, sun_d, moon_d = const.VS_EARTH_DIAMETER_YOJANAS, const.VS_SUN_MEAN_DISTANCE_YOJANAS, const.VS_MOON_MEAN_DISTANCE_YOJANAS
        shadow_length = sun_d * earth / (const.VS_SUN_DIAMETER_YOJANAS - earth)
        shadow_yojanas = earth * (shadow_length - moon_d) / shadow_length
        shadow_dia = shadow_yojanas * _R / moon_distance
    return _FRAME(sun_speed, moon_speed, sun_mean, moon_mean, sun_distance, moon_distance, sun_dia, moon_dia, shadow_dia)


def _rising_point_sayana(jd, place):
    """ Sayana longitude of the rising point of the ecliptic (the Lagna of the module with the ayanamsa added).
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct
        @return: longitude in degrees (0-360) """
    return (vs._ascendant_longitude(jd, place) + vs._rising_ayanamsa(jd, place)) % 360.0


def _above_horizon_nirayana(jd, place, longitude):
    """ Whether an ecliptic point is above the horizon: it lies between the setting point and the rising point of the Lagna.
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct
        @param longitude: sidereal longitude of the body in degrees
        @return: True if above the horizon """
    return 0.0 < (vs._ascendant_longitude(jd, place) - longitude) % 360.0 < 180.0


def _matches_type(type_str, requested, enum_class):
    """ Whether an eclipse of type type_str satisfies a requested filter.
        @param type_str: 'total', 'partial' or 'annular'
        @param requested: one of the SolarEclipseType / LunarEclipseType constants
        @param enum_class: SolarEclipseType or LunarEclipseType
        @return: True if it matches """
    if requested == enum_class.ANY:
        return True
    return {'total': enum_class.TOTAL, 'partial': enum_class.PARTIAL, 'annular': getattr(enum_class, 'ANNULAR', -1)}.get(type_str) == requested


def _half_duration_days(radius, latitude_at, jd_middle, rate_deg_per_day, direction):
    """ Half-duration, in days, from the middle of an eclipse to a contact on one side, by the book's iteration (Ch.IV vs.24-30): the
        sthityardha is the square root of (radius squared minus the Moon's latitude squared) divided by the motion-difference in degrees,
        and the latitude is taken again at the contact until the result stops changing.
        @param radius: sum (or difference) of the semi-diameters, in minutes
        @param latitude_at: function of the Julian Day returning the Moon's latitude in minutes
        @param jd_middle: Julian Day Number of the middle of the eclipse
        @param rate_deg_per_day: difference of the true daily motions of the Moon and the Sun, in degrees per day
        @param direction: -1 = before the middle (first contact), +1 = after it (last contact)
        @return: half-duration in days """
    s = math.sqrt(max(radius ** 2 - latitude_at(jd_middle) ** 2, 0.0)) / rate_deg_per_day    # ghatis
    for _ in range(60):
        b = latitude_at(jd_middle + direction * s / 60.0)
        s_new = math.sqrt(max(radius ** 2 - b ** 2, 0.0)) / rate_deg_per_day
        if abs(s_new - s) < 1e-10:
            s = s_new
            break
        s = s_new
    return s / 60.0


def is_lunar_eclipse(jd_full_moon, place):
    """ Evaluates the full moon at jd_full_moon for a lunar eclipse (Ch.IV).
        @param jd_full_moon: Julian Day Number (local civil time) of the full moon; it is refined to the exact opposition
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @return: dict with sun_diameter, moon_diameter, shadow_diameter, moon_latitude and grasa (degrees), is_possible, is_total, type
            ('total', 'partial' or None), jd_opposition, half_duration_days (None if not possible), and, if possible, jd_begin, jd_immersion,
            jd_middle, jd_emersion, jd_end (jd_immersion and jd_emersion are None unless total) """
    jd_opp = _refine_syzygy(jd_full_moon, place, 180.0)
    fr = _frame(jd_opp, place)
    _, moon_long, node_long = _longitudes(jd_opp, place)
    beta = _moon_latitude_minutes(moon_long, node_long)
    grasa = 0.5 * (fr.moon_diameter + fr.shadow_diameter) - abs(beta)
    is_possible = grasa > 0.0
    is_total = grasa >= fr.moon_diameter
    info = {'sun_diameter': fr.sun_diameter / 60.0, 'moon_diameter': fr.moon_diameter / 60.0, 'shadow_diameter': fr.shadow_diameter / 60.0,
            'moon_latitude': beta / 60.0, 'grasa': grasa / 60.0, 'is_possible': is_possible, 'is_total': is_total,
            'type': ('total' if is_total else 'partial') if is_possible else None, 'jd_opposition': jd_opp, 'half_duration_days': None,
            'jd_begin': None, 'jd_immersion': None, 'jd_middle': jd_opp, 'jd_emersion': None, 'jd_end': None}
    if not is_possible:
        return info

    def latitude_at(t):   # Moon's latitude in minutes at a Julian Day
        _, m, n = _longitudes(t, place)
        return _moon_latitude_minutes(m, n)
    rate = fr.moon_speed - fr.sun_speed
    outer = 0.5 * (fr.shadow_diameter + fr.moon_diameter)
    before = _half_duration_days(outer, latitude_at, jd_opp, rate, -1)
    after = _half_duration_days(outer, latitude_at, jd_opp, rate, +1)
    info.update(half_duration_days=0.5 * (before + after), jd_begin=jd_opp - before, jd_end=jd_opp + after)
    if is_total:
        inner = 0.5 * (fr.shadow_diameter - fr.moon_diameter)
        info.update(jd_immersion=jd_opp - _half_duration_days(inner, latitude_at, jd_opp, rate, -1),
                    jd_emersion=jd_opp + _half_duration_days(inner, latitude_at, jd_opp, rate, +1))
    return info


def next_lunar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.GLOBAL, lunar_eclipse_type=LunarEclipseType.ANY,
                       search_backward=False, flags=DEFAULT_FLAGS, show_maximum_eclipse_global_location=False,
                       max_tries=DEFAULT_MAX_TRIES):
    """ Finds the next (or previous) lunar eclipse matching the requested type (Ch.IV).
        @param jd_local: starting Julian Day Number (local civil time)
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Moon is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param lunar_eclipse_type: one of LunarEclipseType.ANY / TOTAL / PARTIAL (PENUMBRAL returns None)
        @param search_backward: True = the previous eclipse
        @param flags: not used
        @param show_maximum_eclipse_global_location: not used (the book has no ground-track model)
        @param max_tries: maximum number of full moons examined
        @return: (type_str, [begin, middle, end]) for a partial eclipse or (type_str, [begin, immersion, middle, emersion, end]) for a total
            eclipse, each time a (year, month, day, local hours) tuple; None if no eclipse is found """
    if lunar_eclipse_type == LunarEclipseType.PENUMBRAL:
        return None
    direction = -1 if search_backward else 1
    jd = jd_local
    for _ in range(max_tries):
        jd_opp = _syzygy_jd(jd, place, 180.0, direction)
        jd = jd_opp + direction
        info = is_lunar_eclipse(jd_opp, place)
        if not info['is_possible'] or not _matches_type(info['type'], lunar_eclipse_type, LunarEclipseType):
            continue
        times = [info['jd_begin'], info['jd_middle'], info['jd_end']]
        if info['is_total']:
            times = [info['jd_begin'], info['jd_immersion'], info['jd_middle'], info['jd_emersion'], info['jd_end']]
        if (eclipse_location_type == EclipseLocation.LOCAL
                and not any(_above_horizon_nirayana(t, place, _longitudes(t, place)[1]) for t in times)):
            continue
        return info['type'], [utils.jd_to_gregorian(t) for t in times]
    return None


class _SolarEclipse:
    """ The parallax chain of Ch.V for one conjunction at one place. """

    def __init__(self, jd_conjunction, place):
        """ Prepares the constants of the eclipse.
            @param jd_conjunction: Julian Day Number (local civil time) of the geocentric conjunction of the Sun and the Moon
            @param place: Place struct ('Place',latitude,longitude,timezone) """
        self.place = place
        self.jd_conjunction = jd_conjunction
        self.frame = _frame(jd_conjunction, place)
        self.noon_jd = 0.5 * (vs._sunrise_jd(jd_conjunction, place) + vs._sunset_jd(jd_conjunction, place))
        self.rising_asus = vs._vs_base_rising_asus()
        self.rate = self.frame.moon_speed - self.frame.sun_speed
        self.rsin_eps = const.VS_RSIN_GREATEST_DECLINATION
        self.rcos_eps = vs._vs_day_radius(self.rsin_eps)

    def geometry(self, jd):
        """ Central ecliptic point, drkksepa and drggati at a time (Sec.1 vs.4-14, 31).
            @param jd: Julian Day Number (local civil time)
            @return: namedtuple (jd, ayanamsa, sun_sayana, rising_sayana, vitribha, drkksepa, vitribha_sanku, drggati, east, north_of_zenith,
                ra_meridian_deg, above_horizon) """
        p = self.place
        ayan = vs._rising_ayanamsa(jd, p)
        sun_say = (vs._sidereal_longitude_impl(jd, p, const._SUN) + ayan) % 360.0
        rising = _rising_point_sayana(jd, p)
        ra_sun = vs.vs_lagnakala_asus(0.0, sun_say, self.rising_asus)
        ra_meridian = (ra_sun + (jd - self.noon_jd) * const.VS_ASUS_PER_DAY) % const.VS_ASUS_PER_DAY      # vs.6
        meridian = vs._vs_lagna_from_elapsed(0.0, ra_meridian, self.rising_asus)
        phi = p.latitude
        madhyajya = vs._vs_rsine(min(abs(phi - vs._sun_declination(meridian)), 90.0) * 60.0)           # vs.8
        udayajya = abs(vs._vs_declination_rsine(rising)) * _R / vs._vs_rsine((90.0 - min(abs(phi), 89.9)) * 60.0)
        denominator = max(1.0 - (madhyajya * udayajya / _R ** 2) ** 2, 1e-12)
        sanku = math.sqrt(max(_R ** 2 - madhyajya ** 2, 0.0) / denominator)                              # vs.13-14
        sanku = min(sanku, _R)
        drkksepa = math.sqrt(max(_R ** 2 - sanku ** 2, 0.0))
        vitribha = (rising - 90.0) % 360.0
        diff = _wrap180(sun_say - vitribha)
        drggati = abs(_rsin(diff)) * sanku / _R                                                           # vs.31
        ra_deg = ra_meridian / 60.0
        side = _rsin(phi) * self.rcos_eps - _rcos(phi) * self.rsin_eps * _rsin(ra_deg) / _R              # sign of the zenith's ecliptic latitude
        return _SOLAR_GEOMETRY(jd, ayan, sun_say, rising, vitribha, drkksepa, sanku, drggati, diff > 0.0, side < 0.0, ra_deg,
                               0.0 < (rising - sun_say) % 360.0 < 180.0)

    def lambana_ghatis(self, geo):
        """ Lambana in ghatis for a geometry (Sec.1 vs.15, 16, 27).
            @param geo: namedtuple returned by geometry()
            @return: lambana in ghatis (positive) """
        method = const.vs_lambana_method_default
        fr = self.frame
        if method == const.VS_LAMBANA_METHOD.FOUR_GHATIS:
            return const.VS_LAMBANA_GHATIS_PER_R * geo.drggati / _R
        if method == const.VS_LAMBANA_METHOD.SAKRT:
            altitude = abs(_rsin(_wrap180(geo.rising_sayana - geo.sun_sayana))) * geo.vitribha_sanku / _R
            upright = altitude * self.rsin_eps / geo.vitribha_sanku
            base = geo.drggati * self.rsin_eps / geo.vitribha_sanku
            hypotenuse = math.hypot(_R - upright, base)
            return geo.vitribha_sanku * base / hypotenuse / (const.VS_ASUS_PER_DAY / 60.0)
        minutes = geo.drggati * _EARTH_SEMI_DIAMETER * (1.0 / fr.moon_distance - 1.0 / fr.sun_distance)
        return minutes / self.rate

    def apparent_time(self, jd_geocentric):
        """ Apparent time of an event: the lambana, found by iteration for the apparent time itself, is subtracted from the geocentric time
            when the event lies east of the central ecliptic point and added when it lies west (Sec.1 vs.15-16, Sec.3 vs.1-2).
            @param jd_geocentric: Julian Day Number (local civil time) of the geocentric event
            @return: Julian Day Number of the apparent event """
        t = jd_geocentric
        for _ in range(1 if const.vs_lambana_method_default == const.VS_LAMBANA_METHOD.SAKRT else 40):
            geo = self.geometry(t)
            t_new = jd_geocentric - (1.0 if geo.east else -1.0) * self.lambana_ghatis(geo) / 60.0
            if abs(t_new - t) < 1e-9:
                return t_new
            t = t_new
        return t

    def relative_nati(self, geo):
        """ Moon's nati relative to the Sun (Sec.2 vs.1-7), north positive.
            @param geo: namedtuple returned by geometry()
            @return: relative nati in minutes """
        fr = self.frame
        _, moon_long, node = _longitudes(geo.jd, self.place)
        vitribha_nirayana = (geo.vitribha - geo.ayanamsa) % 360.0
        z_v = vs._vs_arc_from_rsine(min(geo.drkksepa, _R)) / 60.0
        side = 1.0 if geo.north_of_zenith else -1.0
        latitude_at_v = _moon_latitude_minutes(vitribha_nirayana, node) if const.vs_nati_include_moon_latitude else 0.0
        moon_zeta = side * z_v + latitude_at_v / 60.0                                                   # vs.2
        moon_true = _rsin(moon_zeta) * fr.moon_mean / fr.moon_speed                                       # vs.3
        sun_true = _rsin(side * z_v) * fr.sun_mean / fr.sun_speed
        return (moon_true * _EARTH_SEMI_DIAMETER / fr.moon_distance - sun_true * _EARTH_SEMI_DIAMETER / fr.sun_distance)

    def true_latitude(self, jd):
        """ Moon's true latitude: the latitude plus the relative nati (Sec.2 vs.7).
            @param jd: Julian Day Number (local civil time)
            @return: latitude in minutes (north positive) """
        _, moon_long, node = _longitudes(jd, self.place)
        return _moon_latitude_minutes(moon_long, node) + self.relative_nati(self.geometry(jd))

    def contact(self, jd_middle, radius, direction):
        """ Apparent time of a contact: the sthityardha is iterated with the Moon's true latitude at the geocentric contact, and the lambana
            is then applied to that time (Sec.3 vs.1-2, 10-11).
            @param jd_middle: Julian Day Number of the geocentric conjunction
            @param radius: sum (outer contacts) or difference (inner contacts) of the semi-diameters, in minutes
            @param direction: -1 = first contact or immersion, +1 = last contact or emersion
            @return: Julian Day Number of the apparent contact """
        s = math.sqrt(max(radius ** 2 - self.true_latitude(jd_middle) ** 2, 0.0)) / self.rate
        for _ in range(60):
            b = self.true_latitude(jd_middle + direction * s / 60.0)
            s_new = math.sqrt(max(radius ** 2 - b ** 2, 0.0)) / self.rate
            if abs(s_new - s) < 1e-9:
                s = s_new
                break
            s = s_new
        return self.apparent_time(jd_middle + direction * s / 60.0)


def is_solar_eclipse(jd_new_moon, place):
    """ Evaluates the new moon at jd_new_moon for a solar eclipse at a place, with the lambana and nati (Ch.V).
        @param jd_new_moon: Julian Day Number (local civil time) of the new moon; it is refined to the exact conjunction
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @return: dict with sun_diameter, moon_diameter, moon_latitude (true, with the nati) and grasa (degrees), is_possible, is_total, type
            ('total', 'annular', 'partial' or None), jd_conjunction, jd_apparent_conjunction, half_duration_days (None if not possible),
            jd_begin, jd_immersion, jd_end, jd_emersion (jd_immersion and jd_emersion are None unless total or annular),
            visible_begin, visible_middle, visible_end (the Sun is above the horizon at that time) """
    jd_conj = _refine_syzygy(jd_new_moon, place, 0.0)
    se = _SolarEclipse(jd_conj, place)
    fr = se.frame
    jd_app = se.apparent_time(jd_conj)
    beta = se.true_latitude(jd_app)
    reduced = 0.5 * fr.moon_diameter - (fr.moon_speed * 60.0 / const.VS_SOLAR_MOON_SEMIDIAMETER_DIVISOR if const.vs_solar_reduce_moon_semidiameter else 0.0)
    outer = 0.5 * fr.sun_diameter + reduced
    grasa = 0.5 * (fr.sun_diameter + fr.moon_diameter) - abs(beta)
    is_possible = outer - abs(beta) > 0.0
    is_total = is_possible and fr.moon_diameter >= fr.sun_diameter and 0.5 * (fr.moon_diameter - fr.sun_diameter) >= abs(beta)
    is_annular = is_possible and fr.moon_diameter < fr.sun_diameter and 0.5 * (fr.sun_diameter - fr.moon_diameter) >= abs(beta)
    type_str = ('total' if is_total else 'annular' if is_annular else 'partial') if is_possible else None
    info = {'sun_diameter': fr.sun_diameter / 60.0, 'moon_diameter': fr.moon_diameter / 60.0, 'moon_latitude': beta / 60.0,
            'grasa': grasa / 60.0, 'is_possible': is_possible, 'is_total': is_total, 'type': type_str, 'jd_conjunction': jd_conj,
            'jd_apparent_conjunction': jd_app, 'half_duration_days': None, 'jd_begin': None, 'jd_immersion': None, 'jd_end': None,
            'jd_emersion': None, 'visible_begin': False, 'visible_middle': False, 'visible_end': False}
    if not is_possible:
        return info
    begin = se.contact(jd_conj, outer, -1)
    end = se.contact(jd_conj, outer, +1)
    info.update(half_duration_days=0.5 * (end - begin), jd_begin=begin, jd_end=end)
    if is_total or is_annular:
        inner = 0.5 * abs(fr.sun_diameter - fr.moon_diameter)
        info.update(jd_immersion=se.contact(jd_conj, inner, -1), jd_emersion=se.contact(jd_conj, inner, +1))
    info.update(visible_begin=se.geometry(begin).above_horizon, visible_middle=se.geometry(jd_app).above_horizon,
                visible_end=se.geometry(end).above_horizon)
    return info


def next_solar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL, solar_eclipse_type=SolarEclipseType.ANY,
                       search_backward=False, flags=DEFAULT_FLAGS, show_maximum_eclipse_global_location=False,
                       max_tries=DEFAULT_MAX_TRIES):
    """ Finds the next (or previous) solar eclipse at a place matching the requested type (Ch.V).
        @param jd_local: starting Julian Day Number (local civil time)
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Sun is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param solar_eclipse_type: one of SolarEclipseType.ANY / TOTAL / PARTIAL / ANNULAR (HYBRID returns None)
        @param search_backward: True = the previous eclipse
        @param flags: not used
        @param show_maximum_eclipse_global_location: not used (the book has no ground-track model)
        @param max_tries: maximum number of new moons examined
        @return: (type_str, [begin, middle, end]) with each time a (year, month, day, local hours) tuple; middle is the apparent conjunction;
            None if no eclipse is found """
    if solar_eclipse_type == SolarEclipseType.HYBRID:
        return None
    direction = -1 if search_backward else 1
    jd = jd_local
    for _ in range(max_tries):
        jd_new = _syzygy_jd(jd, place, 0.0, direction)
        jd = jd_new + direction
        fr = _frame(jd_new, place)
        sun_long, moon_long, node_long = _longitudes(jd_new, place)
        reach = 0.5 * (fr.sun_diameter + fr.moon_diameter) + (fr.moon_speed - fr.sun_speed) * 60.0 / 15.0 + 3.0   # + horizontal parallaxes (Ch.IV vs.12)
        if abs(_moon_latitude_minutes(moon_long, node_long)) > reach:
            continue
        info = is_solar_eclipse(jd_new, place)
        if not info['is_possible'] or not _matches_type(info['type'], solar_eclipse_type, SolarEclipseType):
            continue
        times = [info['jd_begin'], info['jd_apparent_conjunction'], info['jd_end']]
        if (eclipse_location_type == EclipseLocation.LOCAL
                and not (info['visible_begin'] or info['visible_middle'] or info['visible_end'])):
            continue
        return info['type'], [utils.jd_to_gregorian(t) for t in times]
    return None


if __name__ == "__main__":
    utils.set_language('en')
    place = vs.Place('Chennai,India', 13.03862, 80.261818, 5.5)
    jd_local = utils.julian_day_number(vs.Date(2026, 1, 1), (10, 34, 0))
    fmt = lambda t: None if t is None else (t[0], t[1], t[2], utils.to_dms(t[3]))
    solar = next_solar_eclipse(jd_local, place)
    lunar = next_lunar_eclipse(jd_local, place)
    print('Solar:', solar[0], [fmt(t) for t in solar[1]] if solar else None)
    print('Lunar:', lunar[0], [fmt(t) for t in lunar[1]] if lunar else None)
