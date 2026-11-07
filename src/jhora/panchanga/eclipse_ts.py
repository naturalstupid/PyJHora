#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
eclipse_ts.py
=============
Tantrasangraha eclipse engine (Nilakantha Somayaji). Planet longitudes, tithi, daily motion, sunrise and sunset come from
jhora.panchanga.tantra_sangraha; the eclipse geometry (lunar and solar possibility, magnitude, lambana and nati parallax) is done here.
Public API:
    is_lunar_eclipse(jd_full_moon, place, require_visible=True) -> dict
    next_lunar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) or None
    is_solar_eclipse(jd_new_moon, place, require_visible=True) -> dict
    next_solar_eclipse(jd_local, place, ...) -> (type_str, [begin, middle, end]) or None
Visibility: with EclipseLocation.LOCAL an eclipse is returned only if the Moon (lunar) or the Sun (solar) is above the horizon at one or more of its
contacts; with EclipseLocation.GLOBAL the next eclipse is returned whether or not it is seen.
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

_R = 3438.0
_D_SUN_YOJANA = 4410.0
_D_MOON_YOJANA = 315.0
_D_EARTH_YOJANA = 3300.0 / (355.0 / 113.0)

class EclipseLocation:
    """ Visibility scope of the search. LOCAL: an eclipse in which the Sun (solar) or the Moon (lunar) is below the horizon of the place at
        every contact is skipped. GLOBAL: the next eclipse is returned whether or not it is seen at the place. """
    LOCAL = 0
    GLOBAL = 1
class SolarEclipseType:
    ANY = 0
    TOTAL = 1
    PARTIAL = 2
    ANNULAR = 3
class LunarEclipseType:
    ANY = 0
    TOTAL = 1
    PARTIAL = 2

def _ts():
    from jhora.panchanga import tantra_sangraha as ts
    return ts

def _ts_manda_kendra_and_karna(jd, place, planet):
    ts = _ts()
    mean_long = ts._mean_longitude_raw(jd, place, planet)
    mandocca = ts._mandocca(jd, place, planet)
    kendra = (mandocca - mean_long + 360.0) % 360.0
    ratio_fn = lambda k: ts._manda_ratio(planet, k)
    K_over_R = ts._avisesa_manda_karna(kendra, ratio_fn)
    return kendra, K_over_R

def _ts_orbital_radii_yojana():
    ts = _ts()
    rm = _R * 10.0
    rs = rm * ts.TS_REVOLUTIONS[const._MOON] / ts.TS_REVOLUTIONS[const._SUN]
    return rm, rs

def _ts_sphuta_yojana_karnas(jd, place):
    ts = _ts()
    rm, rs = _ts_orbital_radii_yojana()
    kendra_sun, K_sun_over_R = _ts_manda_kendra_and_karna(jd, place, const._SUN)
    kendra_moon, K_moon_over_R = _ts_manda_kendra_and_karna(jd, place, const._MOON)
    d1m = rm * K_moon_over_R
    d1s = rs * K_sun_over_R
    half_r_cos = _R * cosd(kendra_moon) / 2.0
    d2m = d1m + half_r_cos
    d2s_lunar = d1s - half_r_cos
    d2s_solar = d1s + half_r_cos
    return d1m, d1s, d2m, d2s_lunar, d2s_solar, kendra_moon, K_moon_over_R

def _ts_moon_latitude_raw(jd, place):
    """ Moon's latitude (Eq 4.30): beta (arcmin) = 270 * sin(moon - node).
        270 is the orbital inclination in ARCMINUTES (Ch 4.1); the book's
        own "270 x Rsin(..)/R" cancels the trijya R algebraically, so the
        270 must be divided by 60 (arcmin->deg), NOT by R. """
    ts = _ts()
    moon_long = ts._sidereal_longitude_lmt(jd, place, const._MOON)
    rahu_long = ts._mean_longitude_raw(jd, place, const._RAHU)
    return (270.0 / 60.0) * sind(moon_long - rahu_long)

def _ts_lunar_diameters_and_latitude(jd, place):
    ts = _ts()
    (d1m, d1s, d2m, d2s_lunar, _d2s_solar,
     _kendra_moon, _K_moon_over_R) = _ts_sphuta_yojana_karnas(jd, place)
    alpha_m = _D_MOON_YOJANA * _R / d2m / 60.0
    lc = d2s_lunar * 1050.0 / 3360.0
    Dc = (lc - d2m) * _D_EARTH_YOJANA / lc
    alpha_c = Dc * _R / d2m / 60.0
    beta_raw = _ts_moon_latitude_raw(jd, place)
    beta = beta_raw * d1m / d2m
    mdm_raw = abs(ts.daily_planet_speed(jd, place, const.MOON_ID))
    mdm = mdm_raw * d1m / d2m
    return alpha_m, alpha_c, beta, mdm

def _ts_is_nighttime(jd, place):
    """ True if jd (local civil clock time) falls OUTSIDE that calendar
        day's sunrise-to-sunset window at `place` -- i.e. the Moon (which
        is opposite the Sun at a full moon) is above the horizon and the
        eclipse, if real, is actually visible from here.
        A lunar eclipse is visible from the whole night hemisphere, so
        (unlike the solar case) this check does not depend on longitude/
        latitude geometry beyond "is it currently night here" -- but
        without it, an eclipse that is only visible from the OTHER side
        of the Earth at this moment (daytime here) would otherwise be
        reported as a match. """
    ts = _ts()
    sr = ts._sunrise_jd(jd, place)
    ss = ts._sunset_jd(jd, place)
    return not (sr <= jd <= ss)

def is_lunar_eclipse(jd_full_moon, place, require_visible=True):
    """ Evaluates whether the full moon at jd_full_moon produces a lunar eclipse.
        @param jd_full_moon: Julian Day of the full moon instant (local civil time)
        @param place: Place struct
        @param require_visible: True = is_possible also requires night at the place at jd_full_moon; False = geometry only
        @return: dict with moon_diameter, shadow_diameter, moon_latitude, grasa (degrees), is_nighttime, is_possible, is_total and
            half_duration_days (None if not possible) """
    ts = _ts()
    mdia, shdia, mlat, mdm = _ts_lunar_diameters_and_latitude(jd_full_moon, place)
    grasa = 0.5 * (mdia + shdia) - abs(mlat)
    is_nighttime = _ts_is_nighttime(jd_full_moon, place)
    is_possible = (grasa > 0.0) and (is_nighttime or not require_visible)
    is_total = is_possible and (grasa > mdia)
    half_dur = None
    if is_possible:
        sdm = abs(ts.daily_planet_speed(jd_full_moon, place, const.SUN_ID))
        S = 0.5 * (shdia + mdia)
        half_dur = math.sqrt(max(0.0, S * S - mlat * mlat)) / (mdm - sdm)
        for _ in range(4):
            jd_contact = jd_full_moon - half_dur
            _, _, mlat_c, mdm_c = _ts_lunar_diameters_and_latitude(jd_contact, place)
            sdm_c = abs(ts.daily_planet_speed(jd_contact, place, const.SUN_ID))
            new_half_dur = math.sqrt(max(0.0, S * S - mlat_c * mlat_c)) / (mdm_c - sdm_c)
            if abs(new_half_dur - half_dur) < 1e-6:
                half_dur = new_half_dur
                break
            half_dur = new_half_dur
    return {
        'moon_diameter': mdia, 'shadow_diameter': shdia,
        'moon_latitude': mlat, 'grasa': grasa, 'is_nighttime': is_nighttime,
        'is_possible': is_possible, 'is_total': is_total,
        'half_duration_days': half_dur,
    }

def _lunar_seen_locally(eclipse_location_type, place, jd_times):
    """ Whether a lunar eclipse is returned under the scope. With EclipseLocation.LOCAL it must be night at the place (the Moon above the horizon) at one or more of the contacts (with EclipseLocation.GLOBAL every eclipse is returned).
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param place: Place struct
        @param jd_times: Julian Days (local civil time) of the contacts of the eclipse
        @return: True if the eclipse is to be returned """
    if eclipse_location_type != EclipseLocation.LOCAL:
        return True
    return any(_ts_is_nighttime(t, place) for t in jd_times)


def _solar_seen_locally(eclipse_location_type, place, jd_times):
    """ Whether a solar eclipse is returned under the scope. With EclipseLocation.LOCAL it must be day at the place (the Sun above the horizon) at one or more of the contacts (with EclipseLocation.GLOBAL every eclipse is returned).
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param place: Place struct
        @param jd_times: Julian Days (local civil time) of the contacts of the eclipse
        @return: True if the eclipse is to be returned """
    if eclipse_location_type != EclipseLocation.LOCAL:
        return True
    return any(_ts_is_daytime(t, place) for t in jd_times)


def next_lunar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                        lunar_eclipse_type=LunarEclipseType.ANY, search_backward=False,
                        show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) full moon producing a lunar eclipse matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place struct
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in which it is day
            at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param lunar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead of the next
        @param show_maximum_eclipse_global_location: accepted for signature parity; not used
        @param max_tries: maximum number of lunations to search
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples, or None if no matching eclipse is found """
    ts = _ts()
    direction = -1 if search_backward else 1
    search_jd = jd_local
    for _ in range(max_tries):
        ti = ts.tithi(search_jd, place)[0]
        jd_full = ts.full_moon(search_jd, place, ti, opt=direction)
        info = is_lunar_eclipse(jd_full, place, require_visible=False)
        if info['is_possible']:
            is_match = (
                lunar_eclipse_type == LunarEclipseType.ANY or
                (lunar_eclipse_type == LunarEclipseType.TOTAL and info['is_total']) or
                (lunar_eclipse_type == LunarEclipseType.PARTIAL and not info['is_total'])
            )
            if is_match:
                hd = info['half_duration_days']
                if not _lunar_seen_locally(eclipse_location_type, place, (jd_full - hd, jd_full, jd_full + hd)):
                    search_jd = jd_full + 20.0 * direction
                    continue
                type_str = "total" if info['is_total'] else "partial"
                begin = utils.jd_to_gregorian(jd_full - hd)
                middle = utils.jd_to_gregorian(jd_full)
                end = utils.jd_to_gregorian(jd_full + hd)
                return type_str, [begin, middle, end]
        search_jd = jd_full + 20.0 * direction
    return None

def _ts_local_sidereal_time_deg(jd, place):
    jd_ut = jd - place.timezone / 24.0
    t = (jd_ut - 2451545.0) / 36525.0
    gst_deg = (280.46061837 + 360.98564736629 * (jd_ut - 2451545.0)
               + 0.000387933 * t * t - t * t * t / 38710000.0) % 360.0
    return (gst_deg + place.longitude) % 360.0

def _ts_madhya_lagna(jd, place, eps_deg=24.0):
    lst = _ts_local_sidereal_time_deg(jd, place)
    if abs(lst - 90) < 1e-9: return 90.0
    if abs(lst - 270) < 1e-9: return 270.0
    a2 = atand(tand(lst) / cosd(eps_deg))
    mc = (180 + a2) if 90 < lst < 270 else a2
    return mc % 360.0

def _ts_tropical_ascendant(jd, place, eps_deg=24.0):
    lst = _ts_local_sidereal_time_deg(jd, place)
    lat = place.latitude
    numerator = cosd(lst)
    denominator = -sind(eps_deg) * tand(lat) - cosd(eps_deg) * sind(lst)
    return atan2d(numerator, denominator) % 360.0

def _ts_drkkshepa_chain(jd, place, eps_deg=24.0):
    mc = _ts_madhya_lagna(jd, place, eps_deg=eps_deg)
    lagna_deg = _ts_tropical_ascendant(jd, place, eps_deg=eps_deg)
    dec_mc = asind(sind(eps_deg) * sind(mc))
    madhyajya = _R * sind(dec_mc - place.latitude)
    udayajya = sind(eps_deg) * _R * sind(lagna_deg) / cosd(place.latitude)
    bahumaurvika = madhyajya * udayajya / _R
    num = madhyajya * madhyajya - bahumaurvika * bahumaurvika
    den = _R * _R - bahumaurvika * bahumaurvika
    drkkshepa = math.copysign(_R * math.sqrt(max(0.0, num) / max(1e-9, den)), madhyajya)
    drggati = math.sqrt(max(0.0, _R * _R - drkkshepa * drkkshepa))
    cheda = (_R * sind(30.0)) ** 2 / drggati if drggati != 0 else float('inf')
    return drkkshepa, drggati, cheda, mc

def _ts_lambana_nadis(jd, place, sun_long):
    drkkshepa, drggati, cheda, mc = _ts_drkkshepa_chain(jd, place)
    if cheda in (0.0, float('inf')):
        return 0.0, drkkshepa
    return (_R * sind(sun_long - mc) / cheda), drkkshepa

def _ts_nati_arcmin(daily_motion_deg, drkkshepa):
    """ nati (Eq 5.25): daily_motion * Rsin(zv) / 51570, where
        51570 = 15 * R (R = 3438'). drkkshepa here IS Rsin(zv) (already
        R-scaled, see _ts_drkkshepa_chain), so the divisor must be
        15*R, NOT 15. """
    return daily_motion_deg * drkkshepa / (15.0 * _R)

def _ts_solar_diameters(jd, place):
    (d1m, d1s, d2m, _d2s_lunar, d2s_solar,
     _kendra_moon, _K_moon_over_R) = _ts_sphuta_yojana_karnas(jd, place)
    alpha_s = _D_SUN_YOJANA * _R / d2s_solar / 60.0
    alpha_m = _D_MOON_YOJANA * _R / d2m / 60.0
    return alpha_s, alpha_m

def _ts_effective_nati_deg(jd, place):
    ts = _ts()
    sun_long = ts._sidereal_longitude_lmt(jd, place, const._SUN)
    beta_t = _ts_moon_latitude_raw(jd, place)
    mdm = abs(ts.daily_planet_speed(jd, place, const.MOON_ID))
    sdm = abs(ts.daily_planet_speed(jd, place, const.SUN_ID))
    _lambana, drkkshepa = _ts_lambana_nadis(jd, place, sun_long)
    nm = _ts_nati_arcmin(mdm, drkkshepa) / 60.0
    ns = _ts_nati_arcmin(sdm, drkkshepa) / 60.0
    nt = beta_t + nm
    ne = nt - ns
    return ne, drkkshepa, sun_long, mdm, sdm

def _ts_is_daytime(jd, place):
    """ True if jd (local civil clock time, same convention as every
        other public function in tantra_sangraha.py) falls between that
        calendar day's sunrise and sunset at `place`.
        A solar eclipse's lambana/nati/drkkshepa geometry is a purely
        algebraic function of hour angle -- it does not know whether the
        Sun is actually above the horizon, so it can return a
        superficially valid-looking (and even POSITIVE, i.e.
        "eclipse-shaped") result for an instant that falls at local
        midnight, when the conjunction is in fact on the opposite side of
        the Earth and therefore invisible from `place`. Without this
        check, next_solar_eclipse() can report an eclipse (e.g. a real
        eclipse visible only from another continent) as "visible" at a
        place where the Sun was below the horizon at the time. """
    ts = _ts()
    sr = ts._sunrise_jd(jd, place)
    ss = ts._sunset_jd(jd, place)
    return sr <= jd <= ss

def is_solar_eclipse(jd_new_moon, place, require_visible=True):
    """ Evaluates whether the new moon at jd_new_moon produces a solar eclipse at the place, with the lambana and nati parallax.
        @param jd_new_moon: Julian Day of the new moon instant (local civil time)
        @param place: Place struct
        @param require_visible: True = is_possible also requires daytime at the place at the apparent conjunction; False = geometry only
        @return: dict with sun_diameter, moon_diameter, effective_nati, grasa (degrees), is_daytime, is_possible, is_total, is_annular and
            jd_apparent_conjunction """
    ts = _ts()
    jd_app = jd_new_moon
    for _ in range(4):
        sun_long = ts._sidereal_longitude_lmt(jd_app, place, const._SUN)
        lambana_nadis, _drkkshepa = _ts_lambana_nadis(jd_app, place, sun_long)
        jd_app = jd_new_moon + lambana_nadis / 60.0
    sdia, mdia = _ts_solar_diameters(jd_app, place)
    ne, _drkkshepa, _sun_long, _mdm, _sdm = _ts_effective_nati_deg(jd_app, place)
    grasa = 0.5 * (sdia + mdia) - abs(ne)
    # A solar eclipse can only be seen from `place` if the Sun is above
    # the horizon at the (parallax-corrected) apparent conjunction --
    # see _ts_is_daytime() docstring for why this check is necessary.
    is_daytime = _ts_is_daytime(jd_app, place)
    is_possible = (grasa > 0.0) and (is_daytime or not require_visible)
    is_total = is_possible and (mdia >= sdia) and (grasa > sdia)
    is_annular = is_possible and (sdia > mdia) and (grasa > mdia)
    return {
        'sun_diameter': sdia, 'moon_diameter': mdia,
        'effective_nati': ne, 'grasa': grasa, 'is_daytime': is_daytime,
        'is_possible': is_possible, 'is_total': is_total, 'is_annular': is_annular,
        'jd_apparent_conjunction': jd_app,
    }

def next_solar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                        solar_eclipse_type=SolarEclipseType.ANY, search_backward=False,
                        show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) new moon producing a solar eclipse at the place matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place struct
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in which it is night
            at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param solar_eclipse_type: ANY / TOTAL / PARTIAL / ANNULAR filter
        @param search_backward: search for the previous eclipse instead of the next
        @param show_maximum_eclipse_global_location: accepted for signature parity; not used
        @param max_tries: maximum number of lunations to search
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples, or None if no matching eclipse is found """
    ts = _ts()
    direction = -1 if search_backward else 1
    search_jd = jd_local
    for _ in range(max_tries):
        ti = ts.tithi(search_jd, place)[0]
        jd_new = ts.new_moon(search_jd, place, ti, opt=direction)
        info = is_solar_eclipse(jd_new, place, require_visible=False)
        if info['is_possible']:
            is_match = (
                solar_eclipse_type == SolarEclipseType.ANY or
                (solar_eclipse_type == SolarEclipseType.TOTAL and info['is_total']) or
                (solar_eclipse_type == SolarEclipseType.ANNULAR and info['is_annular']) or
                (solar_eclipse_type == SolarEclipseType.PARTIAL and not (info['is_total'] or info['is_annular']))
            )
            if is_match:
                jd_app = info['jd_apparent_conjunction']
                sdia, mdia = info['sun_diameter'], info['moon_diameter']
                ne = info['effective_nati']
                mdm = abs(ts.daily_planet_speed(jd_app, place, const.MOON_ID))
                sdm = abs(ts.daily_planet_speed(jd_app, place, const.SUN_ID))
                if info['is_total'] or info['is_annular']:
                    D = abs(mdia - sdia)
                    S = D
                else:
                    S = 0.5 * (sdia + mdia)
                half_dur = math.sqrt(max(0.0, S * S - ne * ne)) / (mdm - sdm) if (mdm - sdm) != 0 else 0.0
                if not _solar_seen_locally(eclipse_location_type, place, (jd_app - half_dur, jd_app, jd_app + half_dur)):
                    search_jd = jd_new + 20.0 * direction
                    continue
                type_str = "total" if info['is_total'] else ("annular" if info['is_annular'] else "partial")
                middle = utils.jd_to_gregorian(jd_app)
                begin = utils.jd_to_gregorian(jd_app - half_dur)
                end = utils.jd_to_gregorian(jd_app + half_dur)
                return type_str, [begin, middle, end]
        search_jd = jd_new + 20.0 * direction
    return None
