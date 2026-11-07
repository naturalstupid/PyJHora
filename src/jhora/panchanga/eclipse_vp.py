#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
eclipse_vp.py
=============
Lunar and solar eclipses by the rules of Chapter IV ("The Eclipses", verses 1-24, Examples 32-38) of
"Vakyakarana with Laghuprakasika by Sundararaja", ed. T.S. Kuppanna Sastri and K.V. Sarma (Kuppuswami Sastri Research
Institute, Madras, 1962), using the longitudes of vakya_panchanga.py.

    from jhora.panchanga import eclipse_vp

Two layers:

  A. BOOK LEVEL (pure arithmetic, no ephemeris).  Each function takes the numbers the book's worked examples start from
     and returns what the book returns, so Examples 32-38 can be reproduced line by line (see test_eclipse_vp.py).
         sine_of_arc(), bhuja_koti()                  III.2b-6    sine segments 11, 10.5, 9, 7, 4, 1.5 per 15 degrees
         conjunction_time_days()                      IV.1-5a     Ex. 32
         parva_end_longitude()                        IV.5b-7a    Ex. 33
         angular_diameters()                          IV.7b-8     Ex. 34
         moon_latitude_min()                          IV.9        Ex. 35
         lunar_eclipse_elements()                     IV.10-15    Ex. 36, 37
         parallax_vinadis(), nati_multiplier()        IV.20-23a
         solar_eclipse_elements()                     IV.16-24    Ex. 38

  B. DATE LEVEL (uses vakya_panchanga for the Sun, Moon and Rahu).
         parva_events(), lunar_eclipses(), solar_eclipses()

  C. SAME PUBLIC API AS eclipse_ss.py (same names, parameters, defaults and return shapes):
         EclipseLocation, SolarEclipseType, LunarEclipseType
         is_lunar_eclipse(jd_full_moon, place) -> dict
         next_lunar_eclipse(jd_local, place, eclipse_location_type, lunar_eclipse_type, search_backward,
                            show_maximum_eclipse_global_location, max_tries) -> (type_str, [begin, middle, end]) or None
         is_solar_eclipse(jd_new_moon, place) -> dict
         next_solar_eclipse(jd_local, place, eclipse_location_type, solar_eclipse_type, search_backward,
                            show_maximum_eclipse_global_location, max_tries) -> (type_str, [begin, middle, end]) or None
     Unlike eclipse_ss.py, next_solar_eclipse() reports real first and last contacts (not begin = end = middle).

UNITS: longitudes in degrees, angles of the Moon's latitude and diameters in arc-minutes, times in NADIS (60 nadis = 1 day,
60 vinadis = 1 nadi), counted from sunrise.  Latitude is positive when South, negative when North (the book's convention).

WHAT THE BOOK DOES NOT SAY (choices made here, marked [CHOICE] in the code):
  * No rule is given for visibility of a lunar eclipse (is the Moon above the horizon?).  The date-level functions report the
    times only.
  * The Nati multiplier is given at 12', 24' and 36' (2, 8, 18).  Linear interpolation between them is used (confirmed only for
    0-12', Ex. 38 iv), and the sign of the Nati is ignored.  Beyond 36' the series 2*(n/12)**2 is continued.
  * "Total" is decided as in IV.10: magnitude greater than the eclipsed body's diameter.  The book has no annular case.
  * Example 38 prints a Sayana Lagna about 21-27' lower than the Sun-at-the-given-time rule of Ex. 23-24 gives (2r 26 51.4
    against 2r 27 14).  Building the Lagna from the Sun at sunrise reproduces Example 38 (First Contact 16-43.5 against 16-43,
    Middle 20-35.5 against 20-35, Last Contact 23-50.2 against 23-50), so that is the default; lagna_sun='given_time' is
    kept for comparison.  See test_eclipse_vp.py.
"""
import math

try:                                        # inside PyJHora
    from jhora.panchanga import vakya_panchanga as vp
    from jhora import const, utils
except ImportError:                         # stand-alone: vakya_panchanga.py (and a jhora package) next to this file
    import vakya_panchanga as vp
    from jhora import const, utils

# ----------------------------------------------------------------------------------------------
# Constants from the book
# ----------------------------------------------------------------------------------------------
_SINE_SEGMENTS = (11.0, 10.5, 9.0, 7.0, 4.0, 1.5)           # III.2b-4: sine gained per 15 degrees of arc
_PARALLAX_TABLE = (0.0, 39.0, 78.0, 115.0, 144.0, 172.0, 192.0, 208.0, 219.0, 227.0,
                   231.0, 234.0, 238.0, 240.0, 240.0, 240.0)  # IV.20-20a: vinadis at 0, 6, 12 ... 90 degrees from the Sun
_NATI_POINTS = ((0.0, 0.0), (12.0, 2.0), (24.0, 8.0), (36.0, 18.0))    # IV.21-23a: Nati (minutes) -> multiplier
_ECLIPSE_LATITUDE_LIMIT = 100.0             # [CHOICE] date level only: skip a parva whose |Moon latitude| exceeds this (minutes)
_LUNATION_DAYS = 29.53                      # search step of next_lunar_eclipse() / next_solar_eclipse()


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


def _wrap180(x):
    """ @param x: angle in degrees  @return: the same angle in (-180, 180] """
    return ((x + 180.0) % 360.0) - 180.0


def nadi_vinadi(nadis):
    """ Formats a time as the book writes it, 'NN-VV.v' (nadis - vinadis).
        @param nadis: time in nadis (float)
        @return: string
    """
    sign = "-" if nadis < 0 else ""
    n = abs(nadis)
    whole = int(n)
    return f"{sign}{whole}-{(n - whole) * 60.0:04.1f}"


# ----------------------------------------------------------------------------------------------
# A1. Sine, Bhuja, Koti  (III.2b-6)
# ----------------------------------------------------------------------------------------------
def sine_of_arc(arc_deg):
    """ Sine of an arc up to 90 degrees from the sine segments 11, 10.5, 9, 7, 4, 1.5 per 15 degrees (III.2b-4).
        Ex. 17a: 35 degrees gives 24.5.
        @param arc_deg: arc in degrees, 0-90
        @return: sine (maximum 43)
    """
    a = min(max(arc_deg, 0.0), 90.0)
    full = int(a // 15.0)
    left = a - 15.0 * full
    s = sum(_SINE_SEGMENTS[:full])
    if full < len(_SINE_SEGMENTS):
        s += _SINE_SEGMENTS[full] * left / 15.0
    return s


def bhuja_koti(arc_deg):
    """ Bhuja and Koti of an arc (III.5-6).  The part gone in the 1st and 3rd quadrants is the Bhuja; in the 2nd and 4th it is the
        Koti and the Bhuja is 90 degrees less that.  Ex. 18: 10r 7 30' gives Bhuja 1r 22 30', Koti 1r 7 30'.
        @param arc_deg: arc in degrees
        @return: (bhuja, koti) in degrees
    """
    arc = arc_deg % 360.0
    q = int(arc // 90.0)
    part = arc - 90.0 * q
    return (part, 90.0 - part) if q % 2 == 0 else (90.0 - part, part)


def _odd_quadrant(arc_deg):
    """ True if the arc lies in the 1st or 3rd quadrant (the book's 'odd quadrants').  @param arc_deg: degrees  @return: bool """
    return int((arc_deg % 360.0) // 90.0) % 2 == 0


# ----------------------------------------------------------------------------------------------
# A2. Conjunction, end of the Parva, diameters, latitude  (IV.1-9)
# ----------------------------------------------------------------------------------------------
def conjunction_time_days(A_min, a_min, B_min, b_min):
    """ Time of conjunction (IV.2b-3a): t = (A - B) / (b - a).  A is the greater longitude with daily motion a, B the lesser with
        daily motion b (retrograde motion negative).  Positive: conjunction to come; negative: gone.  Ex. 32 gives -5/6 day.
        @param A_min, B_min: longitudes in arc-minutes
        @param a_min, b_min: daily motions in arc-minutes
        @return: days
    """
    return (A_min - B_min) / (b_min - a_min)


def parva_end_longitude(longitude_min, daily_motion_min, nadis):
    """ Longitude at the end of the Parva (IV.5b-7a): minutes equal to the nadis, and seconds equal to the nadis times the excess
        of the daily motion over 60', are added for nadis to go and deducted for nadis gone.  Ex. 33: 70 deg 0', 58', 25 nadis
        gives 70 deg 24' 10".  Equal to longitude + daily motion * nadis / 60.
        @param longitude_min: longitude at sunrise, arc-minutes
        @param daily_motion_min: daily motion, arc-minutes
        @param nadis: nadis after sunrise (negative: before)
        @return: longitude in arc-minutes
    """
    return longitude_min + nadis * 1.0 + nadis * (daily_motion_min - 60.0) / 60.0


def angular_diameters(sun_daily_min, moon_daily_min):
    """ Angular diameters in minutes (IV.7b-9): Sun = daily motion * 5 / 9; Moon = daily motion / 25; the Shadow that hides the
        Moon = Moon * 5 / 2 + 1.  Ex. 34: 58' and 778' give 32.2 and 31.1.
        @param sun_daily_min, moon_daily_min: daily motions in arc-minutes
        @return: (sun, moon, shadow) in arc-minutes
    """
    moon = moon_daily_min / 25.0
    return sun_daily_min * 5.0 / 9.0, moon, moon * 5.0 / 2.0 + 1.0


def moon_latitude_min(moon_minus_rahu_deg):
    """ Latitude of the Moon (IV.9): six times the Sine of the Bhuja of (Moon - Rahu), plus a 21st part of the result.  Positive
        (South) if Moon - Rahu is from 6 to 12 rasis, negative (North) if from 0 to 6.  Ex. 35: 11r 28 gives +9'.2.
        @param moon_minus_rahu_deg: degrees
        @return: latitude in arc-minutes (South positive)
    """
    d = moon_minus_rahu_deg % 360.0
    s = sine_of_arc(bhuja_koti(d)[0])
    lat = 6.0 * s * (1.0 + 1.0 / 21.0)
    return lat if d >= 180.0 else -lat


# ----------------------------------------------------------------------------------------------
# A3. Circumstances of an eclipse, general  (IV.10-15)
# ----------------------------------------------------------------------------------------------
def _circumstances(d_eclipsing, d_eclipsed, lat_min, rel_motion_deg):
    """ Magnitude, total-phase test and half-durations (IV.10-12a).
        @param d_eclipsing, d_eclipsed: diameters in minutes
        @param lat_min: latitude in minutes (sign ignored)
        @param rel_motion_deg: difference of the daily motions of the Sun and Moon, degrees per day
        @return: dict, or None when the latitude is too great (no eclipse)
    """
    lat = abs(lat_min)
    half_sum = (d_eclipsing + d_eclipsed) / 2.0
    magnitude = half_sum - lat
    if magnitude <= 0.0:
        return None
    total = magnitude > d_eclipsed
    half_dur = math.sqrt(half_sum ** 2 - lat ** 2) / rel_motion_deg
    half_tot = None
    if total:
        half_diff = (d_eclipsing - d_eclipsed) / 2.0
        half_tot = math.sqrt(max(half_diff ** 2 - lat ** 2, 0.0)) / rel_motion_deg
    return dict(magnitude=magnitude, total=total, half_sum=half_sum, half_duration=half_dur, half_total=half_tot)


def lunar_eclipse_elements(moon_minus_rahu_deg, moon_daily_min, sun_daily_min, parva_nadis):
    """ Elements and circumstances of a lunar eclipse (IV.7b-15).  Ex. 36 and 37.
        @param moon_minus_rahu_deg: Moon minus Rahu at the end of Purnima, degrees
        @param moon_daily_min, sun_daily_min: daily motions, arc-minutes
        @param parva_nadis: end of the Parva in nadis from the sunrise the times are counted from
        @return: dict (see keys below), or None if there is no eclipse.  Times are in nadis.
            diameters (sun, moon, shadow), latitude_min, magnitude_min, total, half_duration, half_total,
            first_contact, last_contact, immersion, emergence (corrected, IV.14b-15), middle (= end of the Parva),
            correction_vinadis, and the same four contacts uncorrected as *_uncorrected
    """
    sun_d, moon_d, shadow_d = angular_diameters(sun_daily_min, moon_daily_min)
    lat = moon_latitude_min(moon_minus_rahu_deg)
    c = _circumstances(shadow_d, moon_d, lat, (moon_daily_min - sun_daily_min) / 60.0)
    if c is None:
        return None
    corr_vin = abs(lat) / 2.0 * 5.0 / 6.0                  # IV.14b-15: half the latitude, less its sixth, in vinadis
    adj = (-corr_vin if _odd_quadrant(moon_minus_rahu_deg) else corr_vin) / 60.0
    mid = parva_nadis
    raw = dict(first_contact=mid - c["half_duration"], last_contact=mid + c["half_duration"])
    if c["total"]:
        raw.update(immersion=mid - c["half_total"], emergence=mid + c["half_total"])
    out = dict(diameters=(sun_d, moon_d, shadow_d), latitude_min=lat, magnitude_min=c["magnitude"], total=c["total"],
               half_duration=c["half_duration"], half_total=c["half_total"], middle=mid, correction_vinadis=corr_vin)
    for k, v in raw.items():
        out[k + "_uncorrected"] = v
        out[k] = v + adj
    return out


# ----------------------------------------------------------------------------------------------
# A4. Solar eclipse: parallax  (IV.16-24)
# ----------------------------------------------------------------------------------------------
def parallax_vinadis(diff_deg):
    """ Parallax in vinadis for the difference in degrees between the Nonagesimal and the Sun (IV.20-20a): the difference divided by
        6 gives the table position; the fraction is interpolated linearly.  Ex. 38: 26 51.4' gives 157.
        @param diff_deg: degrees, 0-90 (larger values are treated as 90)
        @return: vinadis
    """
    x = min(max(diff_deg, 0.0), 90.0) / 6.0
    i = int(x)
    if i >= len(_PARALLAX_TABLE) - 1:
        return _PARALLAX_TABLE[-1]
    return _PARALLAX_TABLE[i] + (_PARALLAX_TABLE[i + 1] - _PARALLAX_TABLE[i]) * (x - i)


def nati_multiplier(nati_min):
    """ Multiplier for a Nati (IV.21-23a): 2 at 12', 8 at 24', 18 at 36'.  [CHOICE] linear between these points (Ex. 38: 5' gives
        5 x 2 / 12), sign ignored, and 2 * (n / 12)**2 beyond 36'.
        @param nati_min: Nati in minutes
        @return: multiplier
    """
    n = abs(nati_min)
    if n >= 36.0:
        return 2.0 * (n / 12.0) ** 2
    for (x0, y0), (x1, y1) in zip(_NATI_POINTS, _NATI_POINTS[1:]):
        if n <= x1:
            return y0 + (y1 - y0) * (n - x0) / (x1 - x0)
    return 18.0


def solar_eclipse_elements(sun_sunrise_deg, sun_daily_min, moon_sunrise_deg, moon_daily_min, rahu_deg, ayanamsa_deg,
                           eq_shadow, parva_nadis=None, lagna_sun="sunrise", always=False):
    """ Elements and circumstances of a solar eclipse at a place (IV.7b-24).  Ex. 38.
        @param sun_sunrise_deg, moon_sunrise_deg: Nirayana longitudes at sunrise, degrees
        @param sun_daily_min, moon_daily_min: daily motions, arc-minutes
        @param rahu_deg: Rahu at the end of the Parva, degrees
        @param ayanamsa_deg: precession, degrees (Sayana = Nirayana + this)
        @param eq_shadow: equinoctial shadow of the place, angulas
        @param parva_nadis: end of Amavasya in nadis after sunrise; None to find it from the longitudes (IV.2b-3a)
        @param lagna_sun: 'sunrise' (default: the Lagna is walked from the Sun at sunrise; reproduces Ex. 38) or 'given_time'
            (the Sun at the time, as in Ex. 23-24; this counts the Sun's own motion twice and is 1-2 vinadis off in Ex. 38)
        @param always: if True, return the elements (with eclipse=False and a negative or zero magnitude) instead of None when the
            Parallax-corrected Latitude is too great; used by is_solar_eclipse()
        @return: dict, or None if there is no eclipse at the place.  Times in nadis after sunrise:
            visible, parva, pcp (Parva corrected for parallax), middle, first_contact, last_contact, immersion, emergence,
            parallax_vinadis, parallax_corrected_vinadis, nati_min, moon_latitude_min, pcl_min, magnitude_min, total,
            half_duration, half_total, diameters (sun, moon), and 'detail' with the Lagna and Nonagesimal at each time.
    """
    sun_at = lambda t: sun_sunrise_deg + sun_daily_min / 60.0 * (t / 60.0)           # t in nadis; deg = (arcmin/day)/60 * days
    moon_at = lambda t: moon_sunrise_deg + moon_daily_min / 60.0 * (t / 60.0)
    if parva_nadis is None:
        d_min = _wrap180(sun_sunrise_deg - moon_sunrise_deg) * 60.0
        parva_nadis = d_min / (moon_daily_min - sun_daily_min) * 60.0
    tp = parva_nadis
    hyp = math.hypot(eq_shadow, 12.0)
    rasimana = vp.rasimana_vinadis(eq_shadow)

    def horizon(t):                                          # Nonagesimal and parallax in vinadis at time t (IV.16-23a)
        s = (sun_at(t) + ayanamsa_deg) % 360.0
        s_for_lagna = s if lagna_sun == "given_time" else (sun_at(0.0) + ayanamsa_deg) % 360.0
        lagna = vp.lagna_sayana(s_for_lagna, t * 60.0, rasimana)
        nonag = (lagna - 90.0) % 360.0                       # IV.16: deduct 3 rasis from the Lagna
        diff = _wrap180(nonag - s)
        return dict(sun=s, lagna=lagna, nonagesimal=nonag, diff=diff, add=diff > 0.0, visible=(t >= 0.0 and abs(diff) <= 90.0),
                    parallax_vinadis=parallax_vinadis(abs(diff)))

    h0 = horizon(tp)
    if not h0["visible"]:
        return dict(visible=False, parva=tp, detail=dict(at_parva=h0))
    sgn0 = 1.0 if h0["add"] else -1.0                        # Sun less than Nonagesimal: add to the end of the Parva
    pcp = tp + sgn0 * h0["parallax_vinadis"] / 60.0          # IV.21-23a: Parva corrected for parallax (first approximation)
    h1 = horizon(pcp)

    nonag = h1["nonagesimal"]                                # IV.16-17a: correction in latitude due to the Ayana
    ayana_corr = sine_of_arc(bhuja_koti(nonag)[0]) * 6.0 / 13.0 * (1.0 if nonag >= 180.0 else -1.0)
    place_corr = 49.0 * eq_shadow / hyp                      # IV.17b-19: due to the latitude of the place, always positive
    nati = ayana_corr + place_corr
    moon_lat = moon_latitude_min(moon_at(pcp) - rahu_deg)    # Moon at the Parva corrected for parallax
    pcl = moon_lat + nati                                    # IV.19: Parallax-corrected Latitude
    corr_vin = h0["parallax_vinadis"] / 60.0 * nati_multiplier(nati)       # IV.21-23a: multiplier times the parallax in nadis
    par_corrected = h0["parallax_vinadis"] - corr_vin
    middle = tp + sgn0 * par_corrected / 60.0

    sun_d, moon_d, _ = angular_diameters(sun_daily_min, moon_daily_min)
    c = _circumstances(moon_d, sun_d, pcl, (moon_daily_min - sun_daily_min) / 60.0)
    if c is None:
        if not always:
            return None
        return dict(visible=True, eclipse=False, parva=tp, pcp=pcp, middle=middle, nati_min=nati, moon_latitude_min=moon_lat,
                    pcl_min=pcl, magnitude_min=(sun_d + moon_d) / 2.0 - abs(pcl), total=False, diameters=(sun_d, moon_d))
    sign_changed = moon_lat * pcl < 0.0                      # IV.14b-15: if the sign changed by parallax, the rule is reversed
    deduct = _odd_quadrant(moon_at(pcp) - rahu_deg) != sign_changed
    adj = (-1.0 if deduct else 1.0) * (abs(pcl) / 2.0 * 5.0 / 6.0) / 60.0

    raw = dict(first_contact=tp - c["half_duration"], last_contact=tp + c["half_duration"])
    if c["total"]:
        raw.update(immersion=tp - c["half_total"], emergence=tp + c["half_total"])
    out = dict(visible=True, parva=tp, pcp=pcp, middle=middle, parallax_vinadis=h0["parallax_vinadis"], parallax_corrected_vinadis=par_corrected,
               nati_min=nati, ayana_correction_min=ayana_corr, place_correction_min=place_corr, moon_latitude_min=moon_lat, pcl_min=pcl,
               magnitude_min=c["magnitude"], total=c["total"], half_duration=c["half_duration"], half_total=c["half_total"],
               diameters=(sun_d, moon_d), detail=dict(at_parva=h0, at_pcp=h1))
    for k, v in raw.items():
        t = v + adj                                          # not yet corrected for parallax alone (IV.14b-15)
        h = horizon(t)
        par = h["parallax_vinadis"] - corr_vin               # IV.23b-24: each contact corrected separately, same Nati correction
        out[k + "_uncorrected"] = v
        out[k] = t + (par if h["add"] else -par) / 60.0
        out["detail"][k] = h
    return out


# ----------------------------------------------------------------------------------------------
# B. Date level
# ----------------------------------------------------------------------------------------------
def _jd_utc_of_kali_day(K):
    """ Julian day (UT) of the end of Kali day K, the Ujjain mean sunrise.  Inverse of vakya_panchanga.kali_days_from_jd_utc.
        @param K: Kali day  @return: Julian day, UT
    """
    return K + vp.KALI_EPOCH_JDN - 0.25 - vp._UJJAIN_LONGITUDE / 360.0


def parva_events(jd_utc_start, jd_utc_end):
    """ Amavasyas and Purnimas between two instants, each found from the longitudes at the nearest Ujjain sunrise by
        t = (A - B) / (b - a) (IV.2b-3a), so |t| <= half a day (the book allows either 'gone' or 'to go').
        @param jd_utc_start, jd_utc_end: Julian days, UT
        @return: list of dict(kind 'amavasya'/'purnima', K, t_days, jd_utc, moon_minus_rahu, sun_daily_min, moon_daily_min), by time
    """
    k0 = math.floor(vp.kali_days_from_jd_utc(jd_utc_start)) - 1
    k1 = math.floor(vp.kali_days_from_jd_utc(jd_utc_end)) + 1
    ev = []
    for K in range(k0, k1 + 1):
        ml, md = vp.longitude_end_of_day(const._MOON, K)
        sl, sd = vp.longitude_end_of_day(const._SUN, K)
        rl, rd = vp.longitude_end_of_day(const._RAHU, K)
        e, rel = (ml - sl) % 360.0, md - sd
        for kind, target in (("amavasya", 0.0), ("purnima", 180.0)):
            t = _wrap180(target - e) / rel
            if -0.5 <= t < 0.5:
                jd = _jd_utc_of_kali_day(K) + t
                if jd_utc_start <= jd <= jd_utc_end:
                    ev.append(dict(kind=kind, K=K, t_days=t, jd_utc=jd, moon_minus_rahu=(ml + md * t - (rl + rd * t)) % 360.0,
                                   sun_daily_min=sd * 60.0, moon_daily_min=md * 60.0))
    ev.sort(key=lambda x: x["jd_utc"])
    out = []                                    # two neighbouring sunrises can both give |t| just under half a day: keep the nearer
    for e in ev:
        if out and out[-1]["kind"] == e["kind"] and abs(out[-1]["jd_utc"] - e["jd_utc"]) < 1.0:
            if abs(e["t_days"]) < abs(out[-1]["t_days"]):
                out[-1] = e
        else:
            out.append(e)
    return out


def _times_from(elements, jd_parva_utc, keys, tz_hours=0.0):
    """ Converts times in nadis (relative to the Parva) into Julian days.  @return: {key: (nadis, jd_utc, jd_local)} """
    out = {}
    for k in keys:
        if elements.get(k) is not None:
            jd = jd_parva_utc + (elements[k] - elements["parva_ref"]) / 60.0
            out[k] = (elements[k], jd, jd + tz_hours / 24.0)
    return out


def lunar_eclipses(jd_utc_start, jd_utc_end, place=None):
    """ Lunar eclipses between two instants by IV.7b-15.  Visibility (is the Moon up?) is not given by the book and is not tested.
        @param jd_utc_start, jd_utc_end: Julian days, UT
        @param place: Place (only to add local times)
        @return: list of dict: jd_utc (end of the Parva = middle), total, magnitude_min, latitude_min, contacts {name: jd_utc}, elements
    """
    out = []
    for ev in parva_events(jd_utc_start, jd_utc_end):
        if ev["kind"] != "purnima":
            continue
        el = lunar_eclipse_elements(ev["moon_minus_rahu"], ev["moon_daily_min"], ev["sun_daily_min"], 0.0)
        if el is None:
            continue
        el["parva_ref"] = 0.0
        keys = ("first_contact", "immersion", "middle", "emergence", "last_contact")
        tz = place.timezone if place is not None else 0.0
        times = _times_from(el, ev["jd_utc"], keys, tz)
        out.append(dict(jd_utc=ev["jd_utc"], total=el["total"], magnitude_min=el["magnitude_min"], latitude_min=el["latitude_min"],
                        contacts={k: v[1] for k, v in times.items()}, contacts_local={k: v[2] for k, v in times.items()}, elements=el))
    return out


def _state_at(jd_utc):
    """ Sun/Moon/Rahu state at an arbitrary instant, found the way parva_events() does: from the nearest Ujjain sunrise (Kali day-end)
        and its daily motions.
        @param jd_utc: Julian day, UT
        @return: dict(K, t_days, jd_utc, moon_minus_rahu, sun_daily_min, moon_daily_min)
    """
    K = int(round(vp.kali_days_from_jd_utc(jd_utc)))
    t = jd_utc - _jd_utc_of_kali_day(K)
    ml, md = vp.longitude_end_of_day(const._MOON, K)
    sl, sd = vp.longitude_end_of_day(const._SUN, K)
    rl, rd = vp.longitude_end_of_day(const._RAHU, K)
    return dict(K=K, t_days=t, jd_utc=jd_utc, moon_minus_rahu=(ml + md * t - (rl + rd * t)) % 360.0,
                sun_daily_min=sd * 60.0, moon_daily_min=md * 60.0)


def _lunar_info(st):
    """ is_lunar_eclipse() result for a state from parva_events() or _state_at(). """
    sun_d, moon_d, shadow_d = angular_diameters(st["sun_daily_min"], st["moon_daily_min"])
    lat = moon_latitude_min(st["moon_minus_rahu"])
    half_sum = (moon_d + shadow_d) / 2.0
    magnitude = half_sum - abs(lat)
    possible = magnitude > 0.0
    half_dur = None
    if possible:                                             # nadis -> days
        half_dur = math.sqrt(half_sum ** 2 - lat ** 2) / ((st["moon_daily_min"] - st["sun_daily_min"]) / 60.0) / 60.0
    return {"sun_diameter": sun_d / 60.0, "moon_diameter": moon_d / 60.0, "shadow_diameter": shadow_d / 60.0,
            "moon_latitude": -lat / 60.0, "grasa": magnitude / 60.0, "is_possible": possible, "is_total": magnitude > moon_d,
            "half_duration_days": half_dur}


def _solar_elements_at(st, place, always=False):
    """ Solar-eclipse elements at a place for a state from parva_events() or _state_at().
        @return: (elements dict or None, local sunrise Julian day)
    """
    jd_local = st["jd_utc"] + place.timezone / 24.0
    sr = vp._sunrise_jd(jd_local, place)
    if sr > jd_local:
        sr = vp._sunrise_jd(jd_local - 1.0, place)
    tp = (jd_local - sr) * 60.0                              # nadis after the local sunrise
    jd_sr_utc = sr - place.timezone / 24.0
    sun0 = vp.sidereal_longitude(jd_sr_utc, const._SUN, place)
    moon0 = vp.sidereal_longitude(jd_sr_utc, const._MOON, place)
    rahu = vp.sidereal_longitude(st["jd_utc"], const._RAHU, place)
    ayan = vp.get_ayanamsa_value(jd_local, place)
    shadow = vp.equinoctial_shadow(place.latitude)
    el = solar_eclipse_elements(sun0, st["sun_daily_min"], moon0, st["moon_daily_min"], rahu, ayan, shadow, parva_nadis=tp, always=always)
    return el, sr


def _solar_info(st, place):
    """ is_solar_eclipse() result for a state.  @return: (info dict, elements dict or None, local sunrise Julian day) """
    jd_local = st["jd_utc"] + place.timezone / 24.0
    el, sr = _solar_elements_at(st, place, always=True)
    sun_d, moon_d, _ = angular_diameters(st["sun_daily_min"], st["moon_daily_min"])
    if not el["visible"]:                                    # Sun not above the horizon, or Nonagesimal more than 90 degrees from it
        lat = moon_latitude_min(st["moon_minus_rahu"])
        return {"sun_diameter": sun_d / 60.0, "moon_diameter": moon_d / 60.0, "moon_latitude": -lat / 60.0,
                "grasa": ((sun_d + moon_d) / 2.0 - abs(lat)) / 60.0, "is_possible": False, "is_total": False,
                "jd_apparent_conjunction": jd_local}, None, sr
    possible = el["magnitude_min"] > 0.0
    return {"sun_diameter": el["diameters"][0] / 60.0, "moon_diameter": el["diameters"][1] / 60.0,
            "moon_latitude": -el["pcl_min"] / 60.0, "grasa": el["magnitude_min"] / 60.0, "is_possible": possible,
            "is_total": bool(el["total"]) and possible, "jd_apparent_conjunction": sr + el["middle"] / 60.0}, el, sr


def lunar_eclipses(jd_utc_start, jd_utc_end, place=None):
    """ Lunar eclipses between two instants by IV.7b-15.  Visibility (is the Moon up?) is not given by the book and is not tested.
        @param jd_utc_start, jd_utc_end: Julian days, UT
        @param place: Place (only to add local times)
        @return: list of dict: jd_utc (end of the Parva = middle), total, magnitude_min, latitude_min, contacts {name: jd_utc}, elements
    """
    out = []
    for ev in parva_events(jd_utc_start, jd_utc_end):
        if ev["kind"] != "purnima":
            continue
        el = lunar_eclipse_elements(ev["moon_minus_rahu"], ev["moon_daily_min"], ev["sun_daily_min"], 0.0)
        if el is None:
            continue
        el["parva_ref"] = 0.0
        keys = ("first_contact", "immersion", "middle", "emergence", "last_contact")
        tz = place.timezone if place is not None else 0.0
        times = _times_from(el, ev["jd_utc"], keys, tz)
        out.append(dict(jd_utc=ev["jd_utc"], total=el["total"], magnitude_min=el["magnitude_min"], latitude_min=el["latitude_min"],
                        contacts={k: v[1] for k, v in times.items()}, contacts_local={k: v[2] for k, v in times.items()}, elements=el))
    return out


def solar_eclipses(jd_utc_start, jd_utc_end, place):
    """ Solar eclipses visible at a place between two instants by IV.7b-24.  The times are counted from the place's sunrise (nadis).
        @param jd_utc_start, jd_utc_end: Julian days, UT
        @param place: Place (latitude, longitude, timezone)
        @return: list of dict: jd_utc (end of the Parva), total, magnitude_min, contacts {name: jd_utc}, contacts_local, elements
    """
    out = []
    for ev in parva_events(jd_utc_start, jd_utc_end):
        if ev["kind"] != "amavasya" or abs(moon_latitude_min(ev["moon_minus_rahu"])) > _ECLIPSE_LATITUDE_LIMIT:
            continue
        el, sr = _solar_elements_at(ev, place)
        if el is None or not el["visible"]:
            continue
        keys = ("first_contact", "immersion", "middle", "emergence", "last_contact")
        times = {}
        for k in keys:
            if el.get(k) is not None:
                jd_l = sr + el[k] / 60.0
                times[k] = (jd_l - place.timezone / 24.0, jd_l)
        out.append(dict(jd_utc=ev["jd_utc"], total=el["total"], magnitude_min=el["magnitude_min"],
                        contacts={k: v[0] for k, v in times.items()}, contacts_local={k: v[1] for k, v in times.items()}, elements=el))
    return out


# ----------------------------------------------------------------------------------------------
# C. Same public API as eclipse_ss.py
# ----------------------------------------------------------------------------------------------
def is_lunar_eclipse(jd_full_moon, place):
    """ Evaluates whether the full moon at jd_full_moon produces a lunar eclipse (IV.7b-12a).
        @param jd_full_moon: Julian Day of the full moon instant, local civil time
        @param place: Place (only place.timezone is used)
        @return: dict with keys sun_diameter, moon_diameter, shadow_diameter, moon_latitude (all degrees; latitude positive North,
            as in eclipse_ss.py, i.e. opposite to the book's South-positive sign), grasa (magnitude, degrees), is_possible (bool),
            is_total (bool), half_duration_days (float, None if not possible)
    """
    return _lunar_info(_state_at(jd_full_moon - place.timezone / 24.0))


def is_solar_eclipse(jd_new_moon, place):
    """ Evaluates whether the new moon at jd_new_moon produces a solar eclipse at the place, with the book's parallax (Nati and
        Lambana) correction (IV.16-24).  An eclipse not visible at the place (Sun below the horizon, or the Nonagesimal more than
        90 degrees from the Sun) gives is_possible False.
        @param jd_new_moon: Julian Day of the new moon instant, local civil time
        @param place: Place (latitude, longitude, timezone)
        @return: dict with keys sun_diameter, moon_diameter (degrees), moon_latitude (degrees, parallax-corrected, positive North),
            grasa (magnitude, degrees), is_possible (bool), is_total (bool), jd_apparent_conjunction (Julian Day, local civil time,
            of the parallax-corrected middle of the eclipse)
    """
    return _solar_info(_state_at(jd_new_moon - place.timezone / 24.0), place)[0]


def _parva_search(kind, jd_local, place, search_backward, max_tries):
    """ Yields the Parvas of the given kind ('purnima' / 'amavasya') after (or before) jd_local, one lunation-sized window at a time. """
    start = jd_local - place.timezone / 24.0
    for i in range(max_tries):
        if search_backward:
            evs = [e for e in parva_events(start - (i + 1) * _LUNATION_DAYS, start - i * _LUNATION_DAYS) if e["jd_utc"] < start]
            evs.reverse()
        else:
            evs = [e for e in parva_events(start + i * _LUNATION_DAYS, start + (i + 1) * _LUNATION_DAYS) if e["jd_utc"] > start]
        for e in evs:
            if e["kind"] == kind:
                yield e


def _sun_is_up(jd, place):
    """ Whether the Sun is above the horizon: the Julian Day lies between the sunrise and the sunset of its own civil day.
        @param jd: Julian Day (local civil time)
        @param place: Place struct
        @return: True if the Sun is up """
    eng = vp
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


def next_lunar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                       lunar_eclipse_type=LunarEclipseType.ANY, search_backward=False,
                       show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) full moon producing a lunar eclipse matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Moon is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param lunar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead of the next
        @param show_maximum_eclipse_global_location: accepted for signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before giving up
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples (first contact, end of the Purnima, last contact; local
            civil time), or None if no matching eclipse is found within max_tries
    """
    tz = place.timezone
    for ev in _parva_search("purnima", jd_local, place, search_backward, max_tries):
        info = _lunar_info(ev)
        if not info["is_possible"]:
            continue
        if (lunar_eclipse_type == LunarEclipseType.TOTAL and not info["is_total"]) or \
           (lunar_eclipse_type == LunarEclipseType.PARTIAL and info["is_total"]):
            continue
        el = lunar_eclipse_elements(ev["moon_minus_rahu"], ev["moon_daily_min"], ev["sun_daily_min"], 0.0)
        jd_mid = ev["jd_utc"] + tz / 24.0
        if not _lunar_seen_locally(eclipse_location_type, place, (jd_mid + el["first_contact"] / 60.0, jd_mid, jd_mid + el["last_contact"] / 60.0)):
            continue
        begin = utils.jd_to_gregorian(jd_mid + el["first_contact"] / 60.0)
        middle = utils.jd_to_gregorian(jd_mid)
        end = utils.jd_to_gregorian(jd_mid + el["last_contact"] / 60.0)
        return ("total" if info["is_total"] else "partial"), [begin, middle, end]
    return None


def next_solar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                       solar_eclipse_type=SolarEclipseType.ANY, search_backward=False,
                       show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) new moon producing a solar eclipse visible at the place, matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place
        @param eclipse_location_type: accepted for signature parity; the book's procedure (IV.16-24) treats only an eclipse seen at the place
            (the Sun above the horizon), so both scopes give the same result
        @param solar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead of the next
        @param show_maximum_eclipse_global_location: accepted for signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before giving up
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples (first contact, parallax-corrected middle, last contact;
            local civil time), or None if no matching eclipse is found within max_tries
    """
    for ev in _parva_search("amavasya", jd_local, place, search_backward, max_tries):
        if abs(moon_latitude_min(ev["moon_minus_rahu"])) > _ECLIPSE_LATITUDE_LIMIT:
            continue
        info, el, sr = _solar_info(ev, place)
        if not info["is_possible"]:
            continue
        if (solar_eclipse_type == SolarEclipseType.TOTAL and not info["is_total"]) or \
           (solar_eclipse_type == SolarEclipseType.PARTIAL and info["is_total"]):
            continue
        begin = utils.jd_to_gregorian(sr + el["first_contact"] / 60.0)
        middle = utils.jd_to_gregorian(info["jd_apparent_conjunction"])
        end = utils.jd_to_gregorian(sr + el["last_contact"] / 60.0)
        return ("total" if info["is_total"] else "partial"), [begin, middle, end]
    return None
