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
""" vateshwara_sidhantha.py
    =======================
    Vateswara Siddhanta (A.D. 904) planetary-position model for PyJHora (const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA).
    Source: K. S. Shukla, "Vatesvara-Siddhanta and Gola of Vatesvara", Part II (English translation and commentary), INSA, New Delhi, 1985.
    The values and formulas are the book's.
    Provides the same public functions, arguments and return formats as surya_sidhantha.py. The model constants are in const.py (VS_*).
    Book-specific parts:
    Ahargana (Ch.I Sec.3): kali_ahargana_days(), ahargana(), the book's methods vs_ahargana_*(), ahargana_from_calendar().
    Mean longitudes (Ch.I Sec.4, Sec.8): _mean_longitude_raw() for Sun..Saturn, Rahu and Ketu (Mercury and Venus return their sighrocca),
    _desantara_correction(), _mean_apogee_longitude(), _mean_node_longitude().
    True longitudes (Ch.II): Rsine table (Table 13) with its interpolation rules, manda and sighra epicycles (Table 14), _mandaphala(),
    _sighra_correction_classical(), _bhujantara_correction(), _sidereal_longitude_lmt().
    Chapter III: Sun's declination, day-radius, earthsine, ascensional difference, local rising times, Lagna and lagnakala, and the true
    sunrise
    and sunset (cara and bhujantara): _sun_declination(), _general_cara_vinadis(), _base_rising_times_vinadis(),
    _local_rising_times_vinadis(),
    _equation_of_time_days(), _sunrise_jd(), _sunset_jd(), _ascendant_longitude(), vs_lagnakala_asus().
    Ayanamsa: the book gives no value; _rising_ayanamsa() uses surya_sidhantha_ayanamsa().
    Bija: Vateswara has no separate bija; _calculate_beeja_correction() returns 0.
    declination_of_planets() and the eclipse functions follow the Surya Siddhantha tables and rules.
    PLANET-ID CONVENTION (matches drik.py exactly): see surya_sidhantha.py. """
import math
import bisect
from fractions import Fraction
import warnings
from collections import namedtuple as struct
from jhora import utils, const
from math import ceil
from datetime import datetime, timedelta, date
try:
    import swisseph as swe
    _HAVE_SWE = True
except ImportError:
    _HAVE_SWE = False
""" Since datetime does not accept BC year values Use the following structure to represent dates """
Date = struct('Date', ['year', 'month', 'day'])
from functools import lru_cache
_PlaceBase = struct('Place', ['name', 'latitude', 'longitude', 'timezone'])
class Place:
    __slots__ = ("_base", "_elevation")
    def __init__(self, name, latitude, longitude, timezone, elevation=None):
        self._base = _PlaceBase(
            name,
            float(latitude),
            float(longitude),
            float(timezone)
        )
        self._elevation = None if elevation is None else float(elevation)
    @property
    def name(self):
        return self._base.name
    @property
    def latitude(self):
        return self._base.latitude
    @property
    def longitude(self):
        return self._base.longitude
    @property
    def timezone(self):
        return self._base.timezone
    @property
    def elevation(self):
        if self._elevation is None:
            self._elevation = _elevation_lookup(self.latitude, self.longitude)
        return self._elevation
    def __iter__(self):
        yield self.name
        yield self.latitude
        yield self.longitude
        yield self.timezone
    def __repr__(self):
        return (
            f"Place(Place={self.name!r}, latitude={self.latitude}, "
            f"longitude={self.longitude}, timezone={self.timezone}, "
            f"elevation={self._elevation!r})"
        )
# Fixed 9-body planet list for SS (Sun..Ketu only -- see set_planet_list note)
# NOTE: keys are swe-style (const._SUN..const._KETU), values are 0-based
# (const.SUN_ID..const.KETU_ID) -- same {swe_id: 0_based_id} shape as
# drik.planet_list. _ss_ephemeris_planet_index() below does the reverse
# lookup (0-based -> swe-style) that every public function needs.
planet_list = {const._SUN: const.SUN_ID, const._MOON: const.MOON_ID, const._MARS: const.MARS_ID,
               const._MERCURY: const.MERCURY_ID, const._JUPITER: const.JUPITER_ID, const._VENUS: const.VENUS_ID,
               const._SATURN: const.SATURN_ID, const._RAHU: const.RAHU_ID, const._KETU: const.KETU_ID}
INFERIOR_PLANETS = (const._MERCURY, const._VENUS)
# Modern heliocentric sighra (SURYA_SIDDHANTHA_MODERN_SIGHRA only)
_SWE_ID = None
if _HAVE_SWE:
    _SWE_ID = {const._MARS: swe.MARS, const._MERCURY: swe.MERCURY, const._JUPITER: swe.JUPITER,
               const._VENUS: swe.VENUS, const._SATURN: swe.SATURN}
# Surya Siddhantha's own oscillating (trepidation) ayanamsa -- SINE model
_JD_PHASE0 = utils.julian_day_number(Date(-3101, 1, 22), (12, 0, 0))
_JD_PHASE_HALF = utils.julian_day_number(Date(499, 3, 20), (12, 0, 0))
_SS_AYANAMSA_PERIOD_DAYS = 2.0 * (_JD_PHASE_HALF - _JD_PHASE0)  # ~2,629,860 days (~7200.3 years)
_VS_SIDEREAL_YEAR_DAYS = const.VS_YUGA.CIVIL_DAYS / const.VS_YUGA.SOLAR_YEARS  # = 365 + 9313/36000 = 365.2586944 days (Ch.I Sec.3 vs.14)
# Bhaava Madhya (houses) -- classical/self-contained methods only
SUPPORTED_BHAVA_METHODS = (1, 2, 5) #, 'A', 'E', 'V', 'W')

# =====================================================================
# PART A - model specific (Vateshwara Sidhantha)
# =====================================================================
sind = lambda x: math.sin(math.radians(x))
cosd = lambda x: math.cos(math.radians(x))
tand = lambda x: math.tan(math.radians(x))
def ephemeris_planet_index(planet):
    """ Maps a 0-based planet index (const.SUN_ID..const.KETU_ID) to the swe-style key (const._SUN..const._KETU) used by
        _sidereal_longitude_impl() and planet_list.
        @param planet: 0-based index, or const._ascendant_symbol ('L') which is returned unchanged
        @return: swe-style key (const._SUN, const._MARS, ..., const._KETU); const._KETU is the sentinel -10, which
            _sidereal_longitude_impl() derives from Rahu """
    if planet == const._ascendant_symbol:
        return planet
    for p_key, p_id in planet_list.items():
        if p_id == planet:
            return p_key
    raise ValueError(f"Unknown 0-based planet id {planet!r} -- expected one of "
                     f"const.SUN_ID..const.KETU_ID or const._ascendant_symbol ('L').")
def set_planet_list(set_rahu_ketu_as_true_nodes=None, include_western_planets=None):
    """ No-op: this model has no true-node Rahu/Ketu and no theory for Uranus/Neptune/Pluto, so planet_list is not changed.
        @param set_rahu_ketu_as_true_nodes: True: Rahu/Ketu as true nodes; False: mean nodes; None: exclude Rahu/Ketu; not used
        @param include_western_planets: True: include Uranus/Neptune/Pluto; False/None: exclude them; not used
        @return: None """
def refresh_planet_flags(longitude=None,latitude=None,elevation=None):
    pass
def set_tropical_planets():
    pass    
def set_sideral_planets():
    pass
# (Vateswara has no peripheries: its manda / sighra epicycles are const.VS_MANDA_EPICYCLES / VS_SIGHRA_EPICYCLES, Table 14.)
# Ahargana / mean longitude (shared by both models)
def kali_ahargana_days(jd, place, return_fraction=False):
    """ Vateswara Ahargana: civil days elapsed since the Kali epoch day (Friday 18 Feb 3102 BC, Julian) for jd. const.VS_KALI_EPOCH_JD is
        the Julian Day of the 0h that starts that day, so (Ahargana + 5) % 7 is the weekday (0 = Sunday). The civil day runs midnight to
        midnight in the local-mean-time frame of jd; the offset to mean sunrise at Lanka and the longitude correction (Ch.I Sec.4 vs.1,
        Sec.8) are applied in _mean_longitude_raw().
        @param jd: Julian Day, local mean time
        @param place: Place struct (not used)
        @param return_fraction: if True, also return the fraction of the day elapsed since local midnight
        @return: ahargana (int), or (ahargana, kaala_days) """
    jd_midnight = math.floor(jd - 0.5) + 0.5
    kad = int(round(jd_midnight - const.VS_KALI_EPOCH_JD))
    if return_fraction:
        return kad, jd - jd_midnight
    return kad
# Ahargana from lunisolar calendar elements -- the methods of Ch.I Sec.3.
# A Julian-Day driven library does not need these to get the Ahargana (kali_ahargana_days does it directly);
# they are provided so the book's options are all available and testable (see test_vs_ahargana.py).
# Each vs_ahargana_* function takes the elapsed quantities the book names and returns the EXACT quotient
# (fractions.Fraction).  The book says the Ahargana is that quotient's integer part "or that increased by
# one" and decides which by the lord of the day: use vs_resolve_ahargana(), or the dispatcher
# ahargana_from_calendar().  "Elapsed since the epoch" always refers to the epoch chosen (const.VS_EPOCH).
def vs_lord_of_day(ahargana, epoch=None):
    """ Weekday (0 = Sunday ... 6 = Saturday) of the day with this Ahargana: the remainder of Ahargana / 7,
        counted from the weekday on which the epoch began (Sec.3 vs.1-2 and, counted backwards, vs.20). """
    if epoch is None: epoch = const.VS_EPOCH.KALIYUGA
    return (int(ahargana) + const.VS_EPOCH_WEEKDAY[epoch]) % 7
def vs_resolve_ahargana(quotient, weekday=None, epoch=None):
    """ Turn the exact quotient of a method into an integer Ahargana.
        Without `weekday` the integer part is returned.  With `weekday` (0 = Sunday .. 6) the book's rule is
        applied: if the lord obtained is that of the preceding day add one, if that of the following day
        subtract one (Sec.3 vs.3 commentary). """
    base = math.floor(quotient)
    if weekday is None:
        return base
    for k in (0, 1, -1):
        if vs_lord_of_day(base + k, epoch) == weekday:
            return base + k
    raise ValueError("quotient %s is more than one day away from a day whose lord is %s" % (quotient, weekday))
def vs_ahargana_general(years, lunar_months, lunar_days):
    """ Method 1 (vs.1-2). years = solar years elapsed since the epoch; lunar_months = lunar months elapsed since
        the beginning of the light half of Caitra; lunar_days = lunar days elapsed since the beginning of the
        current lunar month. """
    y = const.VS_YUGA
    x = (12 * years + lunar_months) * 30 + lunar_days
    intercalary_months = Fraction(x * y.INTERCALARY_MONTHS, y.SOLAR_DAYS)
    lunar_total = x + 30 * intercalary_months
    omitted = lunar_total * Fraction(y.OMITTED_DAYS, y.LUNAR_DAYS)
    return lunar_total - omitted
def vs_ahargana_shorter(solar_months, lunar_days):
    """ Method 2 (vs.3). solar_months = solar months elapsed since the epoch (12 x years + months);
        lunar_days = lunar days elapsed since the beginning of the current lunar month. """
    y = const.VS_YUGA
    lunar_months = (solar_months * y.LUNAR_DAYS) // y.SOLAR_DAYS      # "the resulting quotient"
    return Fraction((lunar_months * 30 + lunar_days) * y.CIVIL_DAYS, y.LUNAR_DAYS)
def vs_ahargana_adhimasa_sesa(*args, **kwargs):
    """ Method 3 (vs.4) of the Ahargana: (solar days x civil days - 30 x adhimasa-sesa) / solar days. Not available: raises
        NotImplementedError. """
    # the unit of adhimasa-sesa (Sec.4 vs.8-9) is ambiguous in the source text: divisor 'lunar days' or 'lunar months'
    raise NotImplementedError("Method 3 (adhimasa-sesa): residue unit not settled -- see docstring")
def vs_ahargana_solar_days(solar_days_elapsed):
    """ Method 4 (vs.5): solar days + solar days x (intercalary days - omitted days) / solar days (per yuga). """
    y = const.VS_YUGA
    se = Fraction(solar_days_elapsed)
    return se + se * (30 * y.INTERCALARY_MONTHS - y.OMITTED_DAYS) / y.SOLAR_DAYS
def vs_ahargana_residues(intercalary_months_elapsed, adhikasesa, avamasesa):
    """ Method 5 (vs.6-7ab). adhikasesa R_i = residue of intercalary months, avamasesa R_o = residue of omitted days
        (R_o/C and R_i/L are the fractional parts; C = civil days, L = lunar days in a yuga). """
    y = const.VS_YUGA
    corrected = Fraction(adhikasesa * y.CIVIL_DAYS + avamasesa * y.INTERCALARY_MONTHS, y.LUNAR_DAYS)
    return (intercalary_months_elapsed * y.CIVIL_DAYS + corrected) / y.INTERCALARY_MONTHS
def vs_ahargana_omitted_days(omitted_days_elapsed):
    """ Method 6 (vs.7cd): omitted days elapsed INCLUDING the residual fraction x civil days / omitted days. """
    y = const.VS_YUGA
    return Fraction(omitted_days_elapsed) * y.CIVIL_DAYS / y.OMITTED_DAYS
def vs_ahargana_sun_moon_known(*args, **kwargs):
    """ Methods 7 and 8 (vs.8-10) of the Ahargana from the known mean Sun and Moon. Not available: raises NotImplementedError. """
    # the printed rule mixes degrees with year counts
    raise NotImplementedError("Methods 7/8 not implemented yet")
def vs_ahargana_suddhi(years, suddhi_days, lunar_days_since_caitra, omitted_days):
    """ Method 9 (vs.12-13), as printed: years x 189313/36000 - suddhi + lunar days since the beginning of the light
        half of Caitra - corresponding omitted days + 360 x years. """
    return (Fraction(years * 189313, 36000) - suddhi_days + lunar_days_since_caitra - omitted_days + 360 * years)
def vs_ahargana_end_of_solar_year(years):
    """ Method 10 (vs.14): 365 x years + years x 9313/36000 (Ahargana at the END of the solar year). """
    return 365 * years + Fraction(years * 9313, 36000)
def vs_ahargana_end_of_solar_year_alt(years):
    """ Method 11 (vs.15): 364 x years + years x 45313/36000 (Ahargana at the END of the solar year). """
    return 364 * years + vs_shorter_ahargana(years)
def vs_shorter_ahargana(years):
    """ Shorter Ahargana (vs.16ab): Method 11 without the 364 x years term.  Ahargana = 364 x years + shorter
        Ahargana (the relation Ch.I Sec.4 vs.2-6 relies on). """
    return Fraction(years * 45313, 36000)
def vs_ahargana_other_first(solar_days):
    """ 'Other methods', first method (vs.23-24), with the book's approximate constants. """
    s = Fraction(solar_days)
    s = s - s * Fraction(271, 4050000)
    lunar_days = Fraction(solar_days) + (s / 976) * 30            # adds the intercalary days
    x = lunar_days * 11
    omitted = (x + x / 1651030) / 703
    return lunar_days - omitted
def vs_ahargana_other_second(solar_months, lunar_days):
    """ 'Other methods', second method (vs.24-26). solar_months elapsed; lunar_days since the beginning of the
        current lunar month. """
    y = const.VS_YUGA
    intercalary_months = Fraction(solar_months * 66389, 2160000)
    ld = (solar_months + intercalary_months) * 30 + lunar_days
    return ld - ld * Fraction(209021, y.LUNAR_DAYS // 120)
def vs_ahargana_other_third(years, days_since_vernal_equinox):
    """ 'Other methods', third method (vs.27): years x 13149313/36000 + days elapsed since the vernal equinox. """
    return Fraction(years * 13149313, 36000) + days_since_vernal_equinox
def vs_ahargana_epoch_offset(epoch):
    """ Civil days from `epoch` (const.VS_EPOCH) to the start of Kaliyuga (Sec.3 vs.17-19). For BRAHMA_BIRTH this is
        24798639 x civil days / 4 = 9,78,25,51,98,55,50,210 days as printed in the book. """
    return const.VS_YUGAS_TO_KALIYUGA_X4[epoch] * const.VS_YUGA.CIVIL_DAYS // 4
def vs_ahargana_since_epoch(kali_ahargana, epoch):
    """ Ahargana reckoned from `epoch` given the Ahargana reckoned from the start of Kaliyuga. """
    return kali_ahargana + vs_ahargana_epoch_offset(epoch)
def vs_lunar_ahargana(ahargana):
    """ Lunar Ahargana = lunar days elapsed since the epoch (Sec.3 vs.21): Ahargana + omitted days. """
    y = const.VS_YUGA
    return Fraction(ahargana) + Fraction(ahargana * y.OMITTED_DAYS, y.CIVIL_DAYS)
def vs_solar_ahargana(lunar_ahargana):
    """ Solar Ahargana = solar days elapsed since the epoch (Sec.3 vs.21): lunar Ahargana - intercalary days. """
    y = const.VS_YUGA
    la = Fraction(lunar_ahargana)
    return la - la * 30 * y.INTERCALARY_MONTHS / y.LUNAR_DAYS
def ahargana_from_calendar(method=None, weekday=None, epoch=None, **inputs):
    """ Integer Ahargana by any of the book's methods (const.VS_AHARGANA_METHOD).
        @param method: default const.vs_ahargana_method_default (DIRECT_FROM_JD, which takes jd=..., place=...)
        @param weekday: 0=Sunday..6 -- resolves the book's "or that increased by one"
        @param inputs: the keyword arguments of the chosen vs_ahargana_* function """
    M = const.VS_AHARGANA_METHOD
    if method is None: method = const.vs_ahargana_method_default
    if method == M.DIRECT_FROM_JD:
        return kali_ahargana_days(inputs['jd'], inputs.get('place'))
    table = {M.GENERAL: vs_ahargana_general, M.SHORTER: vs_ahargana_shorter,
             M.ADHIMASA_SESA: vs_ahargana_adhimasa_sesa, M.SOLAR_DAYS_DIFFERENCE: vs_ahargana_solar_days,
             M.ADHIMASA_AVAMA_SESA: vs_ahargana_residues, M.OMITTED_DAYS: vs_ahargana_omitted_days,
             M.SUN_MOON_KNOWN: vs_ahargana_sun_moon_known, M.SUN_MOON_KNOWN_ALT: vs_ahargana_sun_moon_known,
             M.SUDDHI_KNOWN: vs_ahargana_suddhi, M.END_OF_SOLAR_YEAR: vs_ahargana_end_of_solar_year,
             M.END_OF_SOLAR_YEAR_ALT: vs_ahargana_end_of_solar_year_alt, M.OTHER_FIRST: vs_ahargana_other_first,
             M.OTHER_SECOND: vs_ahargana_other_second, M.OTHER_THIRD: vs_ahargana_other_third}
    return vs_resolve_ahargana(table[method](**inputs), weekday, epoch)
# Mean longitudes (Ch.I Sec.4 vs.1, vs.53-62; Sec.8 vs.6, 10, 12-14)
#   book rule : (Ahargana x revolutions / civil days in a yuga) revolutions = longitude at MEAN SUNRISE AT LANKA.
#               Apogees and (planetary) nodes divide by the civil days in the LIFE OF BRAHMA instead.
#   epoch     : the planets are at 0 at the start of Kaliyuga; apogees / nodes start at Tables 8 / 9.
#   instant   : the book's Ahargana is a whole-day count from sunrise at Lanka, so for an arbitrary instant the same
#               linear motion is continued: elapsed days = Ahargana + (time since local mean midnight) - 6 h sunrise
#               offset (const.VS_MEAN_SUNRISE_DAY_FRACTION).  At every mean sunrise at Lanka this reduces EXACTLY to the
#               printed rule (tested).
#   place     : `jd` is local mean time (this module's convention); the longitude (desantara) correction of Sec.8 vs.10
#               shifts it to the prime meridian: - (longitude time) x daily motion for a place EAST of it.
def _vs_revolutions(planet):
    """ Revolutions in a yuga (Sec.1 vs.11-14, Table 3). @param planet: swe-style key (const._SUN..const._KETU).
        Rahu/Ketu: NEGATIVE (the node moves backward). Mercury/Venus: the SIGHROCCA's revolutions (same convention
        as surya_sidhantha.py; the planet's own mean longitude is the mean Sun's). """
    if planet in (const._RAHU, const._KETU):
        return -const.VS_MOON_NODE_REVOLUTIONS
    if planet not in const.VS_REVOLUTIONS:
        raise ValueError("Vateswara Siddhanta defines revolutions only for Sun..Saturn, Rahu and Ketu; got planet %r" % (planet,))
    return const.VS_REVOLUTIONS[planet]
def _vs_daily_motion(planet):
    """ Mean daily motion in degrees per civil day = revolutions x 360 / civil days (Sec.8 vs.14). Negative for Rahu/Ketu. """
    return _vs_revolutions(planet) * 360.0 / const.VS_YUGA.CIVIL_DAYS
def _vs_linear_longitude(jd, place, epoch_longitude, numerator, period_days, dc):
    """ epoch_longitude + 360 x (elapsed days x numerator / period_days), elapsed days measured from sunrise at Lanka on
        the epoch day.  The whole-day part uses exact integer arithmetic; `dc` is the longitude correction (degrees). """
    kan, kaala_days = kali_ahargana_days(jd, place, return_fraction=True)
    whole = ((kan * numerator) % period_days) * 360.0 / period_days
    part = (kaala_days - const.VS_MEAN_SUNRISE_DAY_FRACTION) * numerator * 360.0 / period_days
    return (epoch_longitude + whole + part + dc) % 360.0
def _desantara_correction(place, planet):
    """ Longitude (desantara) correction in degrees (Sec.8 vs.6, 10; sign rule: subtract for a place EAST of the prime
        meridian, add for WEST).  = (longitude in time) x daily motion; place=None -> on the prime meridian. """
    if place is None: return 0.0
    return (const.VS_PRIME_MERIDIAN_LONGITUDE - place.longitude) / 360.0 * _vs_daily_motion(planet)
def _mean_longitude_raw(jd, place, planet):
    """ Mean longitude from `planet`'s OWN revolution-count constant (Sec.4 vs.1).
        @param planet: swe-style key (const._SUN..const._KETU).
        Rahu/Ketu regress; Rahu starts at 6 signs, Ketu is Rahu + 180 (Table 9).
        Mercury/Venus return the SIGHROCCA's mean longitude (see _vs_revolutions). """
    epoch_longitude = const.VS_MOON_NODE_AT_KALI if planet == const._RAHU else \
                      (const.VS_MOON_NODE_AT_KALI + 180.0) % 360.0 if planet == const._KETU else 0.0
    return _vs_linear_longitude(jd, place, epoch_longitude, _vs_revolutions(planet), const.VS_YUGA.CIVIL_DAYS,
                                _desantara_correction(place, planet))
def _mean_apogee_longitude(jd, place, planet):
    """ Mean longitude of the apogee (mandocca) of `planet` (swe-style key): the Moon's (3 signs at the epoch, direct,
        488211 revolutions per yuga) or the Sun's / Mars' / Mercury's / Jupiter's / Venus' / Saturn's (Table 8, direct,
        revolutions in the life of Brahma, Table 4).  Sec.4 vs.1, 53-62. """
    if planet == const._MOON:
        rev, period, epoch_longitude = const.VS_MOON_APOGEE_REVOLUTIONS, const.VS_YUGA.CIVIL_DAYS, const.VS_MOON_APOGEE_AT_KALI
    else:
        rev = const.VS_APOGEE_REVOLUTIONS_BRAHMA[planet]
        period = const.VS_YUGA.CIVIL_DAYS * const.VS_BRAHMA_LIFE_YUGAS
        epoch_longitude = const.VS_APOGEE_AT_KALI[planet]
    dc = 0.0 if place is None else (const.VS_PRIME_MERIDIAN_LONGITUDE - place.longitude) / 360.0 * rev * 360.0 / period
    return _vs_linear_longitude(jd, place, epoch_longitude, rev, period, dc)
def _mean_node_longitude(jd, place, planet):
    """ Mean longitude of the ascending node: the Moon's node (= Rahu) or Mars' / Mercury's / Jupiter's / Venus' /
        Saturn's (Table 9, RETROGRADE, revolutions in the life of Brahma, Table 4).  Sec.4 vs.1, 53-62. """
    if planet in (const._MOON, const._RAHU):
        return _mean_longitude_raw(jd, place, const._RAHU)
    rev = -const.VS_NODE_REVOLUTIONS_BRAHMA[planet]
    period = const.VS_YUGA.CIVIL_DAYS * const.VS_BRAHMA_LIFE_YUGAS
    dc = 0.0 if place is None else (const.VS_PRIME_MERIDIAN_LONGITUDE - place.longitude) / 360.0 * rev * 360.0 / period
    return _vs_linear_longitude(jd, place, const.VS_NODE_AT_KALI[planet], rev, period, dc)
# True longitudes (Ch.II).  Everything below follows the book's verses; no modern sine is used.
#   Rsine table + interpolation : Sec.1 vs.2-51 (Table 13), vs.58-82 (Rsine from arc), vs.83-92 (arc from Rsine)
#   epicycles                   : Sec.1 vs.52-53 (Table 14)
#   anomalies / bhuja / koti    : Sec.1 vs.54-57
#   bhujaphala (Sun, Moon)      : Sec.1 vs.93-94;   bhujantara: Sec.1 vs.93-94 and Sec.2 vs.27-28
#   Mars Jupiter Saturn         : Sec.2 vs.1  (mandaphala/2, sighraphala/2, mandaphala, sighraphala)
#   Mercury Venus               : Sec.2 vs.2  (sighraphala, then mandaphala)
#   sighrakarna                 : Sec.2 vs.3-4 (first method)
# The CARA correction (Sec.1 vs.95) is applied where it belongs, in _sunrise_jd() / _sunset_jd() (see the Chapter III section below).
def _vs_rsine(arc_minutes, method=None):
    """ Rsine, in minutes, of an arc given in MINUTES (0 <= arc <= 5400 = 90 degrees), read from Table 13 by the book's
        interpolation.  const.VS_RSINE_METHOD.LINEAR = vs.58 (the 5 first-order rules of vs.58-62 are the same
        arithmetic); SECOND_ORDER = vs.65-66 (all forms of vs.65-82 reduce to it, per the book).  Rsin 0 - Rsin(-h) is
        Rsin h, so the traversed difference before the first entry is Rsin h. """
    if method is None: method = const.vs_rsine_method_default
    T = const.VS_RSINE_TABLE
    h = const.VS_RSINE_ELEMENTAL_ARC
    if arc_minutes < 0.0 or arc_minutes > 96 * h + 1e-9:
        raise ValueError("Rsine is tabulated for 0..90 degrees only; got %r minutes" % (arc_minutes,))
    n = int(arc_minutes // h)
    if n >= 96:
        return T[96]
    lam = arc_minutes - n * h                       # the "residual arc"
    d_cur = T[n + 1] - T[n]                         # current (untraversed) Rsine-difference
    if method == const.VS_RSINE_METHOD.LINEAR:
        return T[n] + lam * d_cur / h
    d_prev = (T[n] - T[n - 1]) if n > 0 else T[1]   # traversed Rsine-difference
    u = lam / h
    return T[n] + u * d_prev + u * (u + 1.0) / 2.0 * (d_cur - d_prev)
def _vs_arc_from_rsine(rsine_minutes, method=None):
    """ Arc, in minutes, whose Rsine is `rsine_minutes` (0 <= Rsine <= R).  LINEAR = vs.83-84; SECOND_ORDER solves the
        quadratic of vs.85-92 (the same equation as vs.65-66 solved for the residual arc). """
    if method is None: method = const.vs_rsine_method_default
    T = const.VS_RSINE_TABLE
    h = const.VS_RSINE_ELEMENTAL_ARC
    if rsine_minutes < 0.0 or rsine_minutes > T[96] + 1e-9:
        raise ValueError("Rsine must lie in 0..%s minutes; got %r" % (T[96], rsine_minutes))
    if rsine_minutes >= T[96]:
        return 96 * h
    n = min(bisect.bisect_right(T, rsine_minutes) - 1, 95)   # greatest tabular Rsine that can be subtracted
    rem = rsine_minutes - T[n]                              # the "residual Rsine-difference"
    d_cur = T[n + 1] - T[n]
    if method == const.VS_RSINE_METHOD.LINEAR:
        return n * h + rem * h / d_cur
    d_prev = (T[n] - T[n - 1]) if n > 0 else T[1]
    v = d_cur - d_prev
    b = d_prev + v / 2.0
    u = 2.0 * rem / (b + math.sqrt(max(0.0, b * b + 2.0 * v * rem)))
    return (n + u) * h
def _vs_bhuja(anomaly):
    """ bhuja (degrees, 0..90) of an anomaly (vs.55): theta, 180-theta, theta-180, 360-theta by quadrant. """
    t = anomaly % 360.0
    if t <= 90.0: return t
    if t <= 180.0: return 180.0 - t
    if t <= 270.0: return t - 180.0
    return 360.0 - t
def _vs_bhujajya_kotijya(anomaly, method=None):
    """ (bhujajya, kotijya) in minutes: Rsin(bhuja) and Rsin(90 - bhuja)  (vs.55, formulas 1-2). """
    b = _vs_bhuja(anomaly)
    return _vs_rsine(b * 60.0, method), _vs_rsine((90.0 - b) * 60.0, method)
def _vs_koti_sign(anomaly):
    """ +1 in the half-orbit beginning with Capricorn (anomaly 270..90), -1 in the one beginning with Cancer (90..270)
        -- the 'sum or difference' of Sec.2 vs.3-4. """
    t = anomaly % 360.0
    return -1.0 if 90.0 < t < 270.0 else 1.0
def _vs_manda_correction(anomaly, epicycle, method=None):
    """ Signed manda correction in DEGREES for a manda anomaly (planet - apogee), vs.93-94: the arc corresponding to the
        bhujaphala = Rsin(bhuja) x epicycle / 360, SUBTRACTED when the anomaly is in the half-orbit beginning with Aries
        (0..180), ADDED when in the one beginning with Libra (180..360). """
    bhujajya, _ = _vs_bhujajya_kotijya(anomaly, method)
    arc = _vs_arc_from_rsine(bhujajya * epicycle / 360.0, method) / 60.0
    return -arc if 0.0 < anomaly % 360.0 < 180.0 else arc
def _vs_planet_mean_daily_motion(planet):
    """ The planet's own mean daily motion (degrees/day).  Mercury and Venus move with the Sun on the average: their
        revolution numbers (4,320,000) are the Sun's, the independent ones belong to their sighroccas. """
    return _vs_daily_motion(const._SUN if planet in (const._MERCURY, const._VENUS) else planet)
def _bhujantara_correction(planet, manda_of_sun):
    """ Bhujantara (Sec.1 vs.93-94; Sec.2 vs.27-28), degrees: planet's mean daily motion x Sun's bhujaphala (equation of
        centre, signed, degrees) / (360 + Sun's mean daily motion)  [= minutes x minutes / (21600 + Sun's daily motion in
        minutes)].  Same sign as the Sun's bhujaphala.  @param planet: swe-style key. """
    return _vs_planet_mean_daily_motion(planet) * manda_of_sun / (360.0 + _vs_daily_motion(const._SUN))
def _mandaphala(jd, place, planet, base_long, periphery_table):
    """ Signed manda correction (degrees) to `base_long` for `planet` (swe-style key): the manda anomaly is base_long minus
        the planet's mean apogee (vs.54) and the epicycle is const.VS_MANDA_EPICYCLES (Table 14).  `periphery_table` is not used (pass None); VS has no peripheries. """
    if planet in (const._RAHU, const._KETU):
        return 0.0
    apogee = _mean_apogee_longitude(jd, place, planet)
    return _vs_manda_correction((base_long - apogee) % 360.0, const.VS_MANDA_EPICYCLES[planet])
def _sighra_correction_classical(m, planet):
    """ Signed sighraphala (degrees), Sec.2 vs.3-4 (first method).  @param m: sighra anomaly = sighrocca - planet (degrees);
        @param planet: swe-style key.  bahuphala = Rsin(bhuja) x e/360, kotiphala = Rsin(90-bhuja) x e/360; true koti = R plus
        (Capricorn half) or minus (Cancer half) the kotiphala; sighrakarna = sqrt(true koti^2 + bahuphala^2); the sighraphala
        is the arc of R x bahuphala / sighrakarna, positive for an anomaly in the half-orbit beginning with Aries. """
    R = const.VS_RSINE_RADIUS
    e = const.VS_SIGHRA_EPICYCLES[planet]
    bhujajya, kotijya = _vs_bhujajya_kotijya(m)
    bahuphala = bhujajya * e / 360.0
    true_koti = R + _vs_koti_sign(m) * kotijya * e / 360.0
    sighrakarna = math.hypot(true_koti, bahuphala)
    arc = _vs_arc_from_rsine(min(R * bahuphala / sighrakarna, R)) / 60.0
    return arc if 0.0 < m % 360.0 < 180.0 else -arc
def _sighra_geocentric_longitude_modern(jd_ut, planet):
    """ Geocentric TROPICAL longitude derived from real heliocentric vector geometry.
        @param planet: swe-style key. """
    if not _HAVE_SWE:
        raise RuntimeError("pyswisseph is required for SURYA_SIDDHANTHA_MODERN_SIGHRA")
    flags = swe.FLG_SWIEPH | swe.FLG_HELCTR | swe.FLG_TRUEPOS
    xx, _ = swe.calc_ut(jd_ut, _SWE_ID[planet], flags)
    H, b, r = xx[0], xx[1], xx[2]
    xx_sun, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH | swe.FLG_TRUEPOS)
    sun_geo_long, R = xx_sun[0], xx_sun[2]
    S = (sun_geo_long + 180.0) % 360.0
    HS = H - S
    numerator = R * sind(HS)
    denominator = r * cosd(b) - R * cosd(HS)
    correction = math.degrees(math.atan2(numerator, denominator))
    return (H + correction) % 360.0
def _true_longitude_modern_sighra(jd, place, planet):
    from jhora.panchanga.drik import get_ayanamsa_value as drik_ayanamsa_value
    jd_ut = jd - place.timezone / 24.0
    tropical_long = _sighra_geocentric_longitude_modern(jd_ut, planet)
    ayanamsa = drik_ayanamsa_value(jd_ut)
    return (tropical_long - ayanamsa) % 360.0
# Public API: planetary longitude
def _calculate_beeja_correction(jd, place, planet):
    """ Beeja (bija) drift correction in degrees. Vateswara Siddhanta has no separate bija correction: the revolution numbers of Ch.I Sec.1
        (Table 3) are used as printed, so this is always 0.0.
        @param jd: Julian Day Number
        @param place: Place struct
        @param planet: swe-style key
        @return: 0.0 """
    return 0.0
def _sidereal_longitude_impl_with_beeja(jd, place, planet):
    """ True sidereal longitude with beeja corrections. Vateswara has no separate bija, so this equals _sidereal_longitude_impl().
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct
        @param planet: swe-style key (const._SUN..const._KETU)
        @return: sidereal longitude in degrees (0-360) """
    return _sidereal_longitude_impl(jd, place, planet)
def _sidereal_longitude_impl(jd, place, planet, model=None):
    """ jd = local CIVIL (zone/clock) time. The classical mean-longitude
        pipeline (ahargana + desantara) is anchored to LOCAL MEAN midnight,
        so convert zone time -> local mean time once, here.
        place=None: no conversion (pure-formula testing, same convention as
        _place_correction()). """
    jd_lmt = jd if place is None else jd + zone_longitude_correction_days(place)
    return _sidereal_longitude_lmt(jd_lmt, place, planet, model)
def _sidereal_longitude_lmt(jd, place, planet, model=None):
    """ Returns the true (sphuta) sidereal longitude of `planet` (degrees,
        0-360) under the currently active astrology model
        (const.astrology_model_default).
        @param planet: swe-style key (const._SUN..const._KETU) -- this is
            the module's INTERNAL convention. Public-facing functions
            accept 0-based (const.SUN_ID..const.KETU_ID) and must convert
            via _ss_ephemeris_planet_index() before calling this. """
    if model is None:
        model = const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA
    # Vateswara Siddhanta, Ch.II.  Order of the book's corrections (commentary after Sec.1 vs.95): desantara (inside the mean
    # longitude), bhujaphala (Sun/Moon: Sec.1 vs.93-94; planets: Sec.2 vs.1-2), bhujantara; cara: in _sunrise_jd()/_sunset_jd().
    applies = const.VS_BHUJANTARA_APPLIES_TO
    mean_sun = _mean_longitude_raw(jd, place, const._SUN)
    manda_sun = _mandaphala(jd, place, const._SUN, mean_sun, None)
    def bhujantara(p):
        return _bhujantara_correction(p, manda_sun) if applies.get(p, False) else 0.0
    if planet == const._SUN:
        return (mean_sun + manda_sun + bhujantara(planet)) % 360
    if planet == const._MOON:
        mean_moon = _mean_longitude_raw(jd, place, planet)
        manda_moon = _mandaphala(jd, place, planet, mean_moon, None)
        return (mean_moon + manda_moon + bhujantara(planet)) % 360
    if planet in (const._RAHU, const._KETU):
        return _mean_longitude_raw(jd, place, planet)
    if planet in INFERIOR_PLANETS:
        # Sec.2 vs.2: sighraphala (whole) on the mean longitude (= the mean Sun), then mandaphala (whole).
        mean_planet = mean_sun
        sighrocca = _mean_longitude_raw(jd, place, planet)
        p1 = mean_planet + _sighra_correction_classical((sighrocca - mean_planet) % 360.0, planet)
        p2 = p1 + _mandaphala(jd, place, planet, p1, None)
        return (p2 + bhujantara(planet)) % 360
    # Sec.2 vs.1 (Mars, Jupiter, Saturn): 1/2 mandaphala, 1/2 sighraphala, whole mandaphala (on the mean), whole sighraphala
    mean_planet = _mean_longitude_raw(jd, place, planet)
    sighrocca = mean_sun
    p1 = mean_planet + 0.5 * _mandaphala(jd, place, planet, mean_planet, None)
    p2 = p1 + 0.5 * _sighra_correction_classical((sighrocca - p1) % 360.0, planet)
    p3 = mean_planet + _mandaphala(jd, place, planet, p2, None)
    p4 = p3 + _sighra_correction_classical((sighrocca - p3) % 360.0, planet)
    return (p4 + bhujantara(planet)) % 360
def sidereal_longitude(jd_utc, planet=None, place=None):
    """ Sidereal (nirayana) longitude of a planet at a UTC Julian day. The local civil jd used by the other functions of this module is
        rebuilt by adding place.timezone/24.0.
        @param jd_utc: Julian Day, UTC (already timezone-adjusted by the caller)
        @param planet: swe-style key, one of const._SUN..const._KETU
        @param place: Place struct (name, latitude, longitude, timezone); required, raises if None
        @return: sidereal longitude in degrees (0-360) """
    if place is None:
        jd_local = jd_utc
    else:
        jd_local = jd_utc + place.timezone / 24.0
    return _sidereal_longitude_impl(jd_local, place, planet)
def solar_longitude(jd_utc, place=None):
    return sidereal_longitude(jd_utc, const._SUN, place)
def lunar_longitude(jd_utc, place=None):
    return sidereal_longitude(jd_utc, const._MOON, place)
def surya_sidhantha_ayanamsa(jd, place, jd_phase0=_JD_PHASE0, amplitude=27.0,
                period_days=_SS_AYANAMSA_PERIOD_DAYS):
    """ Surya Siddhantha oscillating (trepidation) ayanamsa. Sign convention as in drik/Lahiri: sidereal_longitude = tropical_longitude -
        ayanamsa(t).
        @param jd: Julian Day Number (local civil time)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param jd_phase0: Julian Day at which the oscillation phase is zero
        @param amplitude: amplitude in degrees
        @param period_days: period of the oscillation in days
        @return: ayanamsa in degrees, range [-27, +27] """
    jd_utc = jd - place.timezone / 24.0
    phase = 2.0 * math.pi * (jd_utc - jd_phase0) / period_days
    return -amplitude * math.sin(phase)
def _surya_sidhantha_ayanamsa_rate(jd, place, jd_phase0=_JD_PHASE0, amplitude=27.0,
                period_days=_SS_AYANAMSA_PERIOD_DAYS):
    """ Instantaneous rate of change of `surya_sidhantha_ayanamsa`, in
        degrees per day (UT-based). """
    jd_utc = jd - place.timezone / 24.0
    phase = 2.0 * math.pi * (jd_utc - jd_phase0) / period_days
    return -amplitude * (2.0 * math.pi / period_days) * math.cos(phase)
# Sunrise / Sunset (fully self-contained, no swisseph)
def zone_longitude_correction_days(place):
    """
    Difference (in DAYS) between a location's TRUE LOCAL MEAN TIME (LMT)
    and its civil ZONE TIME.
    """
    standard_meridian_deg = place.timezone * 15.0
    return (place.longitude - standard_meridian_deg) / 15.0 / 24.0
# THREE PROBLEMS (Ch.III): the Sun's declination, day-radius, earthsine, ascensional difference (cara), rising times of the
# signs and the Lagna.  Everything follows the book's verses and reads the Rsine table (no modern trig):
#   declination   : Sec.3 vs.1-2         day-radius : Sec.4 vs.1          earthsine : Sec.5 vs.1
#   asc. difference: Sec.7 vs.1, 24, 26-27   rising times at Lanka: Sec.8 vs.1, 8   local rising times: Sec.8 vs.8
#   Lagna         : Sec.8 vs.10(c-d)-12, 19-20 (day), vs.10(a-b), 15 (night);  lagnakala: vs.16, 20
#   true sunrise  : Ch.II Sec.1 vs.93-95 and the commentary after vs.95 (bhujantara + cara move mean sunrise at the local
#                   equatorial place to true sunrise at the local place; Vateswara omits the udayantara)
# LATITUDE: the book's latitude is "always south" (its places lie north of the equator).  The same formulas with a SIGNED
# latitude (negative = south of the equator) give a negative ascensional difference, so southern places work as well.
# AYANA-CALANA: Ch.III Sec.2 vs.24(d)-27 prescribes applying the precession to longitudes used in these calculations but gives
# only a recipe based on observed shadows, no number.  _rising_ayanamsa() therefore stays the inherited SS function for now.
def _vs_rsin_eps(eps_deg=None):
    """ Rsine (minutes) of the Sun's greatest declination: the printed 1398'13" for the book's 24 deg (Ch.II vs.49c-50,
        Ch.III Sec.3 vs.1), else read from Table 13. """
    if eps_deg is None or abs(eps_deg - const.VS_GREATEST_DECLINATION) < 1e-12:
        return const.VS_RSIN_GREATEST_DECLINATION
    return _vs_rsine(eps_deg * 60.0)
def _vs_declination_rsine(sayana_longitude, eps_deg=None, method=None):
    """ SIGNED Rsine (minutes) of the Sun's declination (Sec.3 vs.1(c-d)-2): Rsin(bhuja of the tropical longitude) x Rsin 24deg / R
        (formula 1) or x 416 / 1023 (formula 2).  North (+) for 0..180 deg, south (-) for 180..360 deg. """
    lam = sayana_longitude % 360.0
    rs_lam = _vs_rsine(_vs_bhuja(lam) * 60.0)
    if method is None: method = const.vs_declination_method_default
    if method == const.VS_DECLINATION_METHOD.RATIO_416_1023 and (eps_deg is None or abs(eps_deg - const.VS_GREATEST_DECLINATION) < 1e-12):
        r = rs_lam * const.VS_DECLINATION_RATIO[0] / const.VS_DECLINATION_RATIO[1]
    else:
        r = rs_lam * _vs_rsin_eps(eps_deg) / const.VS_RSINE_RADIUS
    return r if lam < 180.0 else -r
def _sun_declination(sun_long_deg, eps_deg=24.0):
    """ Sun's declination in degrees (signed): the arc of the Rsine of the declination (Sec.3 vs.2). @param sun_long_deg: SAYANA longitude. """
    r = _vs_declination_rsine(sun_long_deg, eps_deg)
    arc = _vs_arc_from_rsine(abs(r)) / 60.0
    return arc if r >= 0.0 else -arc
def _vs_day_radius(rsin_declination):
    """ Day-radius = Rcos(declination) = sqrt(R^2 - Rsin^2(declination))  (Sec.4 vs.1, formula 1). """
    return math.sqrt(max(const.VS_RSINE_RADIUS ** 2 - rsin_declination ** 2, 0.0))
def _vs_palabha(lat_deg):
    """ Equinoctial midday shadow in angulas: 12 x Rsin(latitude) / Rcos(latitude)  (Sec.7 vs.10: Rsin(lat)/Rcos(lat) = palabha/12). """
    phi = abs(lat_deg)
    rc = _vs_rsine((90.0 - phi) * 60.0)
    v = 12.0 * _vs_rsine(phi * 60.0) / rc if rc > 0.0 else float('inf')
    return v if lat_deg >= 0.0 else -v
def _vs_earthsine(rsin_declination, lat_deg):
    """ Earthsine = Rsin(declination) x Rsin(latitude) / Rcos(latitude)  (Sec.5 vs.1, formula 1); signed like the product. """
    phi = abs(lat_deg)
    rc = _vs_rsine((90.0 - phi) * 60.0)
    es = rsin_declination * _vs_rsine(phi * 60.0) / rc if rc > 0.0 else math.copysign(float('inf'), rsin_declination)
    return es if lat_deg >= 0.0 else -es
def _vs_asc_diff_asus(sayana_longitude, lat_deg, eps_deg=None):
    """ Asus of the Sun's ascensional difference (Sec.7 vs.1, 24): Rsin(asc. diff.) = earthsine x R / day-radius, and its ARC in
        minutes is the number of asus.  Signed: positive when the day is longer than 15 ghatis.  A polar-circle value (earthsine
        beyond the day-radius) is clamped to a quadrant. """
    rsd = _vs_declination_rsine(sayana_longitude, eps_deg)
    dr = _vs_day_radius(rsd)
    es = _vs_earthsine(rsd, lat_deg)
    R = const.VS_RSINE_RADIUS
    x = es * R / dr if dr > 0.0 else math.copysign(R, es)
    x = max(-R, min(R, x))
    arc = _vs_arc_from_rsine(abs(x))
    return arc if x >= 0.0 else -arc
def _general_cara_vinadis(long_deg, lat_deg, eps_deg=24.0):
    """ Cara (ascensional difference) in vinadis (1 vinadi = 6 asus) for a sayana longitude and a latitude.
        @param long_deg: sayana longitude in degrees
        @param lat_deg: latitude in degrees (negative = south)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: cara in vinadis """
    return _vs_asc_diff_asus(long_deg, lat_deg, eps_deg) / 6.0
def _vs_base_rising_asus(eps_deg=None, method=None):
    """ Rising times (asus) of the 12 signs AT LANKA (Sec.8 vs.1, 8): Aries, Taurus, Gemini = 1669, 1796, 1935, Cancer..Virgo reversed,
        Libra..Pisces repeat.  method PRINTED = the book's stated values (24 deg); COMPUTED_METHOD_1 = Sec.8 vs.1:
        Rsin(alpha) = Rsin(lambda) x Rcos(delta at 90 deg) / Rcos(delta), arcs differenced. """
    if method is None: method = const.vs_rising_times_method_default
    if (eps_deg is None or abs(eps_deg - const.VS_GREATEST_DECLINATION) < 1e-12) and method == const.VS_RISING_TIMES_METHOD.PRINTED:
        first = tuple(float(x) for x in const.VS_RISING_TIMES_LANKA)
    else:
        R = const.VS_RSINE_RADIUS
        dr3 = _vs_day_radius(_vs_declination_rsine(90.0, eps_deg))
        alphas = []
        for r in (1, 2, 3):
            lam = 30.0 * r
            dr = _vs_day_radius(_vs_declination_rsine(lam, eps_deg))
            alphas.append(_vs_arc_from_rsine(min(_vs_rsine(_vs_bhuja(lam) * 60.0) * dr3 / dr, R)))
        first = (alphas[0], alphas[1] - alphas[0], alphas[2] - alphas[1])
    t1, t2, t3 = first
    return [t1, t2, t3, t3, t2, t1, t1, t2, t3, t3, t2, t1]
def _vs_local_rising_asus(lat_deg, eps_deg=None):
    """ Rising times (asus) of the 12 signs AT THE LOCAL PLACE (Sec.8 vs.8): Aries 1669 - a, Taurus 1796 - b, Gemini 1935 - c, Cancer
        1935 + c, Leo 1796 + b, Virgo 1669 + a, then Libra..Pisces repeat Virgo..Aries; a, b, c = the ascensional differences of the
        signs Aries, Taurus, Gemini, obtained (vs.26) from the Sun's ascensional difference at 30, 60, 90 deg and differenced, or
        (vs.27, const.VS_ASC_DIFF_METHOD.CONSTANTS) as 714, 1294, 1530 x palabha / 12 at those end points. """
    base = _vs_base_rising_asus(eps_deg)
    if const.vs_asc_diff_method_default == const.VS_ASC_DIFF_METHOD.CONSTANTS:
        P = _vs_palabha(lat_deg)
        ends = [k * P / 12.0 for k in const.VS_ASC_DIFF_SIGN_END_COEFFICIENTS]
    else:
        ends = [_vs_asc_diff_asus(30.0 * r, lat_deg, eps_deg) for r in (1, 2, 3)]
    a, b, c = ends[0], ends[1] - ends[0], ends[2] - ends[1]
    adj = [-a, -b, -c, +c, +b, +a, +a, +b, +c, -c, -b, -a]
    return [base[i] + adj[i] for i in range(12)]
def _base_rising_times_vinadis(eps_deg=24.0):
    """ Rising times of the 12 signs at Lanka, in vinadis.
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: list of 12 rising times in vinadis, Aries first """
    return [t / 6.0 for t in _vs_base_rising_asus(eps_deg)]
def _local_rising_times_vinadis(lat_deg, eps_deg=24.0):
    """ Rising times of the 12 signs at a latitude (local oblique ascensions), in vinadis.
        @param lat_deg: latitude in degrees (negative = south)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: list of 12 rising times in vinadis, Aries first """
    return [t / 6.0 for t in _vs_local_rising_asus(lat_deg, eps_deg)]
def _equation_of_time_days(jd_lmt, place, eps_deg=24.0):
    """ Equation of time in DAYS (local apparent = local mean + EoT).  Vateswara has the BHUJANTARA part only (the udayantara is omitted,
        Ch.II Sec.1 commentary after vs.94): the Sun's bhujaphala divided by (360 deg + the Sun's mean daily motion), negative when the
        true Sun is ahead of the mean Sun (apparent noon later). """
    mean_sun = _mean_longitude_raw(jd_lmt, place, const._SUN)
    bhujaphala = _mandaphala(jd_lmt, place, const._SUN, mean_sun, None)
    return -bhujaphala / (360.0 + _vs_daily_motion(const._SUN))
def _sunrise_jd(jd, place, eps_deg=24.0):
    """ Sunrise as a Julian Day in the same civil-clock convention as jd: mean sunrise at the local equatorial place
        (const.VS_MEAN_SUNRISE_DAY_FRACTION of the day after local mean midnight), moved earlier by the cara (Sun's ascensional difference,
        Ch.II vs.95: asus / 21600 of a day) and by the bhujantara (equation of time).
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: Julian Day Number of the sunrise """
    jd_midnight = math.floor(jd - 0.5) + 0.5
    mean_sunrise_lmt = jd_midnight + const.VS_MEAN_SUNRISE_DAY_FRACTION
    sun_long = _sidereal_longitude_lmt(mean_sunrise_lmt, place, const._SUN)
    sun_sayana = (sun_long + _rising_ayanamsa(mean_sunrise_lmt, place)) % 360.0
    cara_days = _general_cara_vinadis(sun_sayana, place.latitude, eps_deg) / 3600.0
    sunrise_lmt = mean_sunrise_lmt - cara_days - _equation_of_time_days(mean_sunrise_lmt, place, eps_deg)
    return sunrise_lmt - zone_longitude_correction_days(place)
def _sunset_jd(jd, place, eps_deg=24.0):
    """ Sunset as a Julian Day in the same convention as _sunrise_jd(): mean sunset (1 - const.VS_MEAN_SUNRISE_DAY_FRACTION of the day)
        moved later by the cara and earlier by the equation of time.
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: Julian Day Number of the sunset """
    jd_midnight = math.floor(jd - 0.5) + 0.5
    mean_sunset_lmt = jd_midnight + (1.0 - const.VS_MEAN_SUNRISE_DAY_FRACTION)
    sun_long = _sidereal_longitude_lmt(mean_sunset_lmt, place, const._SUN)
    sun_sayana = (sun_long + _rising_ayanamsa(mean_sunset_lmt, place)) % 360.0
    cara_days = _general_cara_vinadis(sun_sayana, place.latitude, eps_deg) / 3600.0
    sunset_lmt = mean_sunset_lmt + cara_days - _equation_of_time_days(mean_sunset_lmt, place, eps_deg)
    return sunset_lmt - zone_longitude_correction_days(place)
def _vs_lagna_from_elapsed(sun_sayana, elapsed_asus, local_asus):
    """ Sayana longitude of the rising point of the ecliptic (Sec.8 vs.10(c-d)-12, 19): by the untraversed part of the Sun's sign
        (multiply by that sign's rising time, divide by 30) subtract from the elapsed asus; then subtract the rising times of the
        following signs while possible; the remainder x 30 / the rising time of the next sign are the degrees traversed in it.
        If the elapsed time is less than the rising time of the untraversed part, elapsed x 30 / own-sign rising time is added to
        the Sun (vs.19). """
    s = int((sun_sayana % 360.0) // 30.0) % 12
    within = sun_sayana % 360.0 - s * 30.0
    time_to_finish = (30.0 - within) / 30.0 * local_asus[s]
    if elapsed_asus <= time_to_finish:
        frac = elapsed_asus / local_asus[s] if local_asus[s] > 0.0 else 0.0
        return (sun_sayana + frac * 30.0) % 360.0
    remaining = elapsed_asus - time_to_finish
    cur = (s + 1) % 12
    guard = 0
    while remaining > local_asus[cur] and guard < 24:
        remaining -= local_asus[cur]
        cur = (cur + 1) % 12
        guard += 1
    frac = remaining / local_asus[cur] if local_asus[cur] > 0.0 else 0.0
    return (cur * 30.0 + frac * 30.0) % 360.0
def vs_lagnakala_asus(sun_sayana, lagna_sayana, local_asus):
    """ Time in asus corresponding to a given Lagna (lagnakala / istakala), Sec.8 vs.16 (first approximation) and vs.20 (same sign):
        traversed degrees of the Lagna sign x its rising time / 30 + untraversed degrees of the Sun's sign x its rising time / 30 +
        the rising times of the signs between. """
    s = int((sun_sayana % 360.0) // 30.0) % 12
    l = int((lagna_sayana % 360.0) // 30.0) % 12
    sw, lw = sun_sayana % 30.0, lagna_sayana % 30.0
    if s == l and (lagna_sayana % 360.0) >= (sun_sayana % 360.0):
        return (lw - sw) * local_asus[s] / 30.0
    t = (30.0 - sw) * local_asus[s] / 30.0 + lw * local_asus[l] / 30.0
    k = (s + 1) % 12
    while k != l:
        t += local_asus[k]
        k = (k + 1) % 12
    return t
def _ascendant_longitude(jd, place, eps_deg=24.0):
    """ Raw (nirayana) Lagna longitude, Vateswara Ch.III Sec.8. The elapsed time in asus (21600 per civil day) since sunrise is walked
        forward from the instantaneous sayana Sun through the local rising times of the signs (vs.10(c-d)-12, 19); the ayanamsa is then
        removed. const.vs_lagna_night_method_default selects the treatment of the hours after sunset: SINCE_SUNRISE (time counted from
        sunrise through the whole day and night; continuous and monotonic) or SINCE_SUNSET_OPPOSITE_SUN (the book's night rule, vs.10(a-b)
        and the second example of vs.15: time counted from sunset, starting from the point opposite the Sun).
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: Lagna longitude in degrees (0-360) """
    sr_today = _sunrise_jd(jd, place, eps_deg=eps_deg)
    sr = sr_today if jd >= sr_today else _sunrise_jd(jd - 1.0, place, eps_deg=eps_deg)
    ayan = _rising_ayanamsa(jd, place)
    sun_sayana = (_sidereal_longitude_impl(jd, place, const._SUN) + ayan) % 360.0
    local = _vs_local_rising_asus(place.latitude, eps_deg)
    asus_per_day = const.VS_ASUS_PER_DAY
    method = const.vs_lagna_night_method_default
    last_sunset = None
    if method != const.VS_LAGNA_NIGHT_METHOD.SINCE_SUNRISE:
        if jd < sr_today:
            last_sunset = _sunset_jd(jd - 1.0, place, eps_deg=eps_deg)
        else:
            ss_today = _sunset_jd(jd, place, eps_deg=eps_deg)
            if jd > ss_today: last_sunset = ss_today
    if last_sunset is None:
        sayana_lagna = _vs_lagna_from_elapsed(sun_sayana, (jd - sr) * asus_per_day, local)
    else:
        sayana_lagna = _vs_lagna_from_elapsed((sun_sayana + 180.0) % 360.0, (jd - last_sunset) * asus_per_day, local)
    return (sayana_lagna - ayan) % 360.0
def _rising_ayanamsa(jd, place):
    """ Ayanamsa for equatorial quantities only (declination, cara, rising
        times, Lagna). Planet longitudes remain nirayana. Uses the SS trepidation ayanamsa. """
    return surya_sidhantha_ayanamsa(jd, place)
# Ascendant / Lagna (fully self-contained, no swisseph)
def _ra_at_longitude(lam_deg, eps_deg):
    lam = math.radians(lam_deg); eps = math.radians(eps_deg)
    return math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360
def ascendant(jd, place,dhasa_progression_correction=0.0):
    """ Lagna (ascendant) at the given time and place.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param dhasa_progression_correction: degrees added to the computed longitude (progressed charts); 0.0 for none
        @return: [constellation (0..11), longitude within the constellation, nakshatra number (1..27), pada (1..4)] """
    nirayana_lagna = _ascendant_longitude(jd, place)
    nirayana_lagna += dhasa_progression_correction
    nak_no, paadha_no, _ = utils.nakshatra_pada(nirayana_lagna)
    constellation = int(nirayana_lagna / 30)
    coordinates = nirayana_lagna - constellation * 30
    return [constellation, coordinates, nak_no, paadha_no]
# Moonrise / Moonset (fully self-contained, no swisseph)
def _wrapped_diff(a, b):
    """ (a - b), wrapped to (-180, 180]. """
    return (a - b + 180.0) % 360.0 - 180.0
def _find_crossing_forward(jd_lo, jd_hi, target_fn, num_scan=192, max_bisect=60):
    """ Scans FORWARD from jd_lo to jd_hi, returns the FIRST sign change found. """
    step = (jd_hi - jd_lo) / num_scan
    prev_t = jd_lo
    prev_v = target_fn(prev_t)
    for i in range(1, num_scan + 1):
        t = jd_lo + i * step
        v = target_fn(t)
        if prev_v == 0.0:
            return prev_t
        if (prev_v > 0) != (v > 0) and abs(v - prev_v) < 180.0:
            lo, hi = prev_t, t
            flo = prev_v
            for _ in range(max_bisect):
                mid = (lo + hi) / 2.0
                fmid = target_fn(mid)
                if abs(fmid) < 1e-7 or (hi - lo) < 1e-9:
                    return mid
                if (fmid > 0) == (flo > 0):
                    lo, flo = mid, fmid
                else:
                    hi = mid
            return (lo + hi) / 2.0
        prev_t, prev_v = t, v
    return None
def _moonrise_jd(jd, place, eps_deg=24.0, search_window_days=1.2):
    jd_midnight = math.floor(jd - 0.5) + 0.5
    def diff_fn(t):
        return _wrapped_diff(_ascendant_longitude(t, place, eps_deg=eps_deg),
                              _sidereal_longitude_impl(t, place, const._MOON))
    return _find_crossing_forward(jd_midnight, jd_midnight + search_window_days, diff_fn)
def _moonset_jd(jd, place, eps_deg=24.0, search_window_days=1.2):
    jd_midnight = math.floor(jd - 0.5) + 0.5
    def diff_fn(t):
        lagna = _ascendant_longitude(t, place, eps_deg=eps_deg)
        moon = _sidereal_longitude_impl(t, place, const._MOON)
        return _wrapped_diff(lagna, (moon + 180.0) % 360.0)
    return _find_crossing_forward(jd_midnight, jd_midnight + search_window_days, diff_fn)
def _ss_resolve_longitude(jd, place, planet):
    """ Longitude of a planet (0-based index) or the Lagna ('L'), degrees. """
    if planet == const._ascendant_symbol:
        return _ascendant_longitude(jd, place)
    p_swe = ephemeris_planet_index(planet)
    return _sidereal_longitude_impl(jd, place, p_swe)
# Speed helpers (finite-difference, no swisseph)
def daily_planet_speed(jd, place, planet, dt=0.02):
    """ Signed speed (deg/day) via central finite difference.
        @param planet: 0-based index (const.SUN_ID..const.KETU_ID) or 'L'. """
    l1 = _ss_resolve_longitude(jd - dt, place, planet)
    l2 = _ss_resolve_longitude(jd + dt, place, planet)
    diff = ((l2 - l1 + 180.0) % 360.0) - 180.0
    return diff / (2 * dt)
def _planet_speed_info(jd, place, planet):
    """ Longitude, latitude, distance and their speeds of a planet in this model.
        @param jd: Julian Day Number of the date/time (local civil time)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param planet: 0-based planet index (const.SUN_ID..const.KETU_ID) or const._ascendant_symbol ('L')
        @return: [longitude, latitude, distance_from_earth, longitude_speed, latitude_speed, distance_speed];
                 this model has no latitude or distance, so those entries are 0.0; for 'L' the speed of the ascendant """
    if planet == const._ascendant_symbol: return ascendant_speed(jd, place)
    return [_ss_resolve_longitude(jd, place, planet), 0.0, 0.0, daily_planet_speed(jd, place, planet), 0.0, 0.0]
def __next_solar_jd(jd,place,sun_long):
    """ Julian Day at which the Sun reaches a longitude, searched day by day from jd and refined by inverse Lagrange interpolation.
        @param jd: Julian Day Number from which the search starts
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param sun_long: sidereal longitude of the Sun in degrees
        @return: Julian Day Number at which the Sun reaches sun_long """
    jd_next = jd
    sl = solar_longitude(jd_next, place)
    while True:
        if sl<sun_long+1 and sl>sun_long:
            jd_next -= 1
            break
        jd_next += 1
        sl = solar_longitude(jd_next, place)
    sank_date = jd_to_gregorian(jd_next)
    sank_sunrise = sunrise(jd_next,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    solar_longs = [ (solar_longitude(sank_sunrise + t, place)) for t in offsets ]
    solar_hour = utils.inverse_lagrange(offsets, solar_longs, sun_long) # Do not move % 360 above
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    return sank_jd_utc + solar_hour1/24.0
def _planet_speed_sign(jd, place, planet):
    """ @param planet: 0-based index (const.SUN_ID..const.KETU_ID). """
    v = daily_planet_speed(jd, place, planet)
    if v > 0:
        return 1
    elif v < 0:
        return -1
    return 0
# Small support functions needed by tithi/yogam
def _local_hours(jd):
    """ Decimal local civil hours-of-day for a jd in this module's local
        civil-clock convention (fractional .5 = local midnight). """
    frac = (jd + 0.5) % 1.0
    return frac * 24.0
def daily_moon_speed(jd, place):
    return daily_planet_speed(jd, place, const._MOON)
def daily_sun_speed(jd, place):
    return daily_planet_speed(jd, place, const._SUN)
def _tithi_phase(jd, place, planet1=const._MOON, planet2=const._SUN, tithi_index=1, cycle=1):
    """ Tithi phase in degrees (0-360) at the local civil-time jd. The jd is converted to UTC for _special_tithi_phase().
        @param jd: Julian Day Number, local civil time
        @param place: Place struct
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param tithi_index: multiplier of the phase (1 = Janma tithi)
        @param cycle: number of phase cycles
        @return: phase angle in degrees """
    return _special_tithi_phase(jd - place.timezone/24.0, planet1, planet2, tithi_index, cycle, place)
def dhasavarga(jd, place, divisional_chart_factor=1, set_rahu_ketu_as_true_nodes=None,
               include_western_planets=None, dhasa_progression_correction=0.0):
    """ Planet positions in a divisional chart.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param divisional_chart_factor: divisional chart factor (1 = Rasi, 2 = Hora, 3 = Drekkana, 9 = Navamsa, 10 = Dasamsa, ...)
        @param set_rahu_ketu_as_true_nodes: True: Rahu/Ketu as true nodes; False: mean nodes; None: exclude Rahu/Ketu; not used
        @param include_western_planets: True: include Uranus/Neptune/Pluto; False/None: exclude them; not used
        @param dhasa_progression_correction: degrees added to the computed longitude (progressed charts); 0.0 for none
        @return: list of [planet index, (constellation, longitude within the constellation)] in the divisional chart, ordered by planet
            index """
    positions = []
    for planet, p_id in planet_list.items():
        if p_id == const.KETU_ID:
            continue
        nirayana_long = utils.norm360(_sidereal_longitude_impl(jd, place, planet) + dhasa_progression_correction)
        divisional_chart = dasavarga_from_long(nirayana_long, divisional_chart_factor)
        positions.append([p_id, divisional_chart])
        if p_id == const.RAHU_ID:
            p_id_ketu = planet_list[const._KETU]
            ketu_long = utils.norm360(nirayana_long + 180)
            divisional_chart_ketu = dasavarga_from_long(ketu_long, divisional_chart_factor)
            positions.append([p_id_ketu, divisional_chart_ketu])
    positions = sorted(positions, key=lambda x: -1 if x[0] == 'L' else x[0])
    return positions
def planetary_positions(jd, place):
    """ Instantaneous planetary positions.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: list of [planet index, (constellation, longitude within the constellation)] """
    positions = []
    for planet, p_id in planet_list.items():
        nirayana_long = _sidereal_longitude_impl(jd, place, planet)
        constellation = int(nirayana_long / 30)
        coordinates = nirayana_long - constellation * 30
        positions.append([p_id,(constellation,coordinates)])
    return positions
def _bhaava_madhya_new(jd, place, bhava_madhya_method=None):
    """
        returns house longitudes (start, cusp, end)
        @param jd: Julian Day number
        @param place: Place('name',latitude,longitude,timezone_hours)
        @param bhava_madhya_method:
            1=> Equal Housing - Lagna in the middle start = lagna-15, end lagna+15; asc same for all houses
            2=> Equal Housing - Lagna as start
            3=> Sripati method.
            4=> KP Method (aka Placidus Houses method)
            5=> Each Rasi is the house (rasi is the house, 0 is start and 30 is end, asc is asc+rasi*30)
        @return: [[house1_rasi,(house1_start,house1_cusp,house1_end)],(...),[house12_rasi,(house12_start,house12_cusp,house12_end)]]
    """
    if bhava_madhya_method is None:
        bhava_madhya_method = const.BHAVA_METHODS.KN_RAO_JHORA_DEFAULT.value
    elif hasattr(bhava_madhya_method, 'value'):
        bhava_madhya_method = bhava_madhya_method.value
    if bhava_madhya_method not in SUPPORTED_BHAVA_METHODS:
        raise ValueError(
            f"bhava_madhya_method={bhava_madhya_method!r} is not supported by the SS engine. "
            f"Supported: {SUPPORTED_BHAVA_METHODS} "
            "(1/W-alias-2=Parashari-whole-sign, 5=Nakshatra-paadha)."
            "All other methods like"
            "A/E/V=Equal variants, KP, BV_RAMAN, and all named western/Sripathi house systems require "
            "swe.houses_ex() and have no self-contained SS equivalent."
        )
    ascendant_constellation, ascendant_longitude, _, _ = ascendant(jd,place)
    ascendant_full_longitude = (ascendant_constellation*30+ascendant_longitude)%360
    planet_positions = dhasavarga(jd,place,divisional_chart_factor=1)
    planet_positions = [[const._ascendant_symbol,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    bhava_houses = []
    if bhava_madhya_method == 1:  # KN_RAO_JHORA_DEFAULT
        _bhava_mid = ascendant_full_longitude;
        for h in range(12):
            _bhava_start = (_bhava_mid-15.0)%360; _bhava_end = (_bhava_mid+15.0)%360
            bhava_houses.append((_bhava_start,_bhava_mid,_bhava_end))
            _bhava_mid = utils.norm360(_bhava_mid + 30)
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method == 2:  # PARASHARI
        _bhava_mid = ascendant_full_longitude;
        for h in range(12):
            _bhava_start = _bhava_mid; _bhava_mid=(_bhava_start+15.0)%360; _bhava_end = (_bhava_mid+15.0)%360
            bhava_houses.append((_bhava_start,_bhava_mid,_bhava_end))
            _bhava_mid = utils.norm360(_bhava_start + 30)
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method == 5:  # NAKSHATHRA_PAADHA
        for h in range(12):
            h1 = (h+ascendant_constellation)%12
            _bhava_start = h1*30; _bhava_mid = _bhava_start + ascendant_longitude; _bhava_end = ((h1+1)%12)*30
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    # NOTE: the SUPPORTED_BHAVA_METHODS check above already guarantees
    # bhava_madhya_method is one of (1, 2, 5) by this point, so no further
    # fallthrough/else is reachable.
def bhaava_madhya(jd, place, bhava_method=None):
    """ Middle longitude of each of the 12 bhava houses.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param bhava_method: one of const.BHAVA_METHODS values; None: const.bhaava_madhya_method
        @return: [house1_longitude, house2_longitude, ..., house12_longitude]; the house 1 value is the Ascendant """
    if bhava_method is None:
        bhava_method = const.bhaava_madhya_method
    bh = _bhaava_madhya_new(jd, place, bhava_madhya_method=bhava_method)
    return [entry[1][1] for entry in bh]
def _upagraha_longitude_full(dob, tob, place, planet_index, upagraha_part='middle',
                              dhasa_progression_correction=0.0):
    """ Raw upagraha longitude (0-360 deg). `planet_index` is 0-based
        (const.SUN_ID..const.SATURN_ID). """
    jd = utils.julian_day_number(dob, tob)
    tob_hrs = tob[0] + tob[1]/60.0 + tob[2]/3600.0
    sr = _sunrise_jd(jd, place)
    ss_ = _sunset_jd(jd, place)
    weekday = vaara(jd, place)
    planet_part = const.day_rulers[weekday].index(planet_index)
    if tob_hrs < _local_hours(sr):
        sr_use, ss_use = sr, _sunset_jd(jd - 1, place)
        planet_part = const.night_rulers[weekday].index(planet_index)
    elif tob_hrs > _local_hours(ss_):
        sr_use, ss_use = _sunrise_jd(jd + 1, place), ss_
        planet_part = const.night_rulers[weekday].index(planet_index)
    else:
        sr_use, ss_use = sr, ss_
    day_dur = abs(ss_use - sr_use)
    one_part = day_dur / 8.0
    planet_start_jd = sr_use + planet_part * one_part
    jd_kaala = planet_start_jd + 0.5 * one_part if upagraha_part.lower() == 'middle' else planet_start_jd
    clong = ascendant(jd_kaala, place)
    return utils.norm360(clong[0] * 30 + clong[1] + dhasa_progression_correction)
def _convert_to_tamil_date_and_time_ss(panchanga_date, time_of_day_in_hours, place):
    """ Tamil civil date and time: a time before 0h or after 24h moves the date, and a time after the sunset of the date moves it to the
        next day.
        @param panchanga_date: Date as struct (year,month,day)
        @param time_of_day_in_hours: local clock hours (may be negative or above 24)
        @param place: Place struct
        @return: (Date, time of day in hours) """
    extra_days = 0
    sign = 1
    if time_of_day_in_hours < 0:
        extra_days = int(abs(time_of_day_in_hours / 24)) + 1
        sign = -1
    elif time_of_day_in_hours > 24:
        extra_days = int(abs(time_of_day_in_hours / 24))
        sign = 1
    time_of_day_in_hours += -sign * extra_days * 24
    if extra_days != 0:
        panchanga_date = utils.next_panchanga_day(panchanga_date, add_days=sign * extra_days)
    jd = utils.gregorian_to_jd(panchanga_date)
    _, _, _, sunset_time = utils.jd_to_gregorian(_sunset_jd(jd, place))
    if sunset_time < time_of_day_in_hours:
        panchanga_date = utils.next_panchanga_day(panchanga_date, add_days=1)
    return panchanga_date, time_of_day_in_hours
def get_planet_speed_sign(jd, place, planet):
    """ Motion symbol of a planet.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param planet: 0-based planet index (const.SUN_ID..const.KETU_ID)
        @return: 'R' if retrograde, 'S' if stationary, '' otherwise """
    return (const.ret_stat_symbols[_planet_speed_sign(jd, place, planet)]
            if planet not in (const._SUN, const._MOON) else '')
def true_tropical_year(jd_start, place, round_to_digits=6):
    """ Tropical year (days) at jd_start: the book's sidereal year (civil days per solar year) combined with the rate of the ayanamsa in use. """
    rate_deg_per_day = _surya_sidhantha_ayanamsa_rate(jd_start, place)
    n_sidereal_deg_per_day = 360.0 / _VS_SIDEREAL_YEAR_DAYS
    n_tropical_deg_per_day = n_sidereal_deg_per_day + rate_deg_per_day
    return 360.0 / n_tropical_deg_per_day
def _sun_tropical_longitude(jd, place):
    """ Sun's tropical longitude: the sidereal longitude plus the ayanamsa.
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct
        @return: tropical longitude in degrees (0-360) """
    return (_sidereal_longitude_impl(jd, place, const._SUN)
            + surya_sidhantha_ayanamsa(jd, place)) % 360.0
def _next_sun_tropical_entry_date(seed_jd, place, target_tropical_longitude, direction=1):
    """ Finds jd near seed_jd where the Sun's tropical longitude equals
        target_tropical_longitude. """
    ayan1 = surya_sidhantha_ayanamsa(seed_jd, place)
    target_sid1 = (target_tropical_longitude - ayan1) % 360.0
    jd1, _ = next_planet_entry_date_general(seed_jd, place, const.SUN_ID,
                                             planet_longitude=target_sid1,
                                             direction=direction)
    ayan2 = surya_sidhantha_ayanamsa(jd1, place)
    target_sid2 = (target_tropical_longitude - ayan2) % 360.0
    refine_seed = jd1 - 2.0 * direction
    return next_planet_entry_date_general(refine_seed, place, const.SUN_ID,
                                           planet_longitude=target_sid2,
                                           direction=direction)
def _get_dhasa_start_jd_lunar(jd_birth, place, nakshatra_fraction, total_dasa_years):
    """ Julian day on which the lunar-year dasa running at birth started: the elapsed part of the dasa is converted to lunar months and
        elongation, and the Sun-Moon elongation of birth is searched backward with _sidereal_longitude_impl().
        @param jd_birth: Julian Day Number of birth
        @param place: Place struct
        @param nakshatra_fraction: fraction of the dasa elapsed at birth (0..1)
        @param total_dasa_years: duration of the dasa in years
        @return: Julian Day Number of the dasa start """
    birth_moon = _sidereal_longitude_impl(jd_birth, place, const._MOON)
    birth_sun = _sidereal_longitude_impl(jd_birth, place, const._SUN)
    natal_elongation = (birth_moon - birth_sun) % 360.0
    dasa_elapsed_years = nakshatra_fraction * total_dasa_years
    total_tithis_elapsed = dasa_elapsed_years * 360.0
    total_lunar_months = total_tithis_elapsed / 30.0
    full_lunar_cycles = int(total_lunar_months)
    fractional_month = total_lunar_months - full_lunar_cycles
    remaining_degrees = fractional_month * 360.0
    target_elongation = (natal_elongation - remaining_degrees) % 360.0
    mean_synodic_month = 29.530589
    approx_days_back = (full_lunar_cycles * mean_synodic_month) + (remaining_degrees / 12.1907)
    estimated_target_jd = jd_birth - approx_days_back
    low_jd, high_jd = estimated_target_jd - 1.0, estimated_target_jd + 1.0
    jd_start = estimated_target_jd
    for _ in range(50):
        mid_jd = (low_jd + high_jd) / 2.0
        m_long = _sidereal_longitude_impl(mid_jd, place, const._MOON)
        s_long = _sidereal_longitude_impl(mid_jd, place, const._SUN)
        current_elongation = (m_long - s_long) % 360.0
        diff = (current_elongation - target_elongation + 180) % 360 - 180
        if abs(diff) < 1e-7:
            jd_start = mid_jd
            break
        elif diff > 0: high_jd = mid_jd
        else: low_jd = mid_jd
    else:
        jd_start = (low_jd + high_jd) / 2.0
    return jd_start
def _get_dhasa_start_jd_tropical(jd_birth, place, fraction_elapsed, total_dasa_years):
    """ True-tropical-year dasha start (tropical = sidereal + surya_sidhantha_ayanamsa). """
    dasa_elapsed_years = fraction_elapsed * total_dasa_years
    whole_years = int(dasa_elapsed_years)
    fractional_year = dasa_elapsed_years - whole_years
    year_length = true_tropical_year(jd_birth, place)
    birth_tropical_long = _sun_tropical_longitude(jd_birth, place)
    current_jd_anchor = jd_birth
    for _ in range(whole_years):
        search_seed = current_jd_anchor - year_length - 1
        current_jd_anchor, _ = _next_sun_tropical_entry_date(
            search_seed, place, birth_tropical_long, direction=1)
    target_fractional_arc = fractional_year * 360.0
    target_longitude = (birth_tropical_long - target_fractional_arc) % 360.0
    approx_days_for_fraction = fractional_year * year_length
    final_search_seed = current_jd_anchor - (approx_days_for_fraction + 15.0)
    jd_start, _ = _next_sun_tropical_entry_date(
        final_search_seed, place, target_longitude, direction=1)
    return jd_start
def _get_dhasa_start_jd(jd_birth, place, fraction_elapsed, total_dasa_years,
                          dasha_sesham_method=None):
    """ Julian day on which the dasa running at birth started: the elapsed part of the dasa is subtracted from the birth time, using the
        year length selected by const.dhasa_year_duration_default.
        @param jd_birth: Julian Day Number of birth
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param fraction_elapsed: fraction of the dasa elapsed at birth (0..1)
        @param total_dasa_years: duration of the dasa in years
        @param dasha_sesham_method: one of const.DASHA_SESHAM_METHOD; None: const.default_dasha_sesham_method
        @return: Julian Day Number of the dasa start """
    if dasha_sesham_method is None: dasha_sesham_method = const.default_dasha_sesham_method
    if dasha_sesham_method == const.DASHA_SESHAM_METHOD.REVERSE:
        fraction_elapsed = 1.0 - fraction_elapsed
    elif dasha_sesham_method == const.DASHA_SESHAM_METHOD.NONE:
        fraction_elapsed = 0.0
    dasa_elapsed_years = fraction_elapsed * total_dasa_years
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.MEAN_SIDEREAL_YEAR:
        return jd_birth - dasa_elapsed_years * const.sidereal_year
    elif const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.MEAN_TROPICAL_YEAR:
        return jd_birth - dasa_elapsed_years * const.tropical_year
    elif const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.MEAN_LUNAR_YEAR:
        return jd_birth - dasa_elapsed_years * const.lunar_year
    elif const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.SAVANA_YEAR:
        return _get_dhasa_start_jd_savana(jd_birth, place, fraction_elapsed, total_dasa_years)
    elif const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.TRUE_LUNAR_YEAR:
        return _get_dhasa_start_jd_lunar(jd_birth, place, fraction_elapsed, total_dasa_years)
    elif const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR:
        return _get_dhasa_start_jd_tropical(jd_birth, place, fraction_elapsed, total_dasa_years)
    whole_years = int(dasa_elapsed_years)
    fractional_year = dasa_elapsed_years - whole_years
    year_length = const.average_gregorian_year
    birth_sun_long = _sidereal_longitude_impl(jd_birth, place, const._SUN)
    current_jd_anchor = jd_birth
    for _ in range(whole_years):
        search_seed = current_jd_anchor - year_length - 1
        current_jd_anchor, _ = next_planet_entry_date_general(
            search_seed, place, const.SUN_ID, planet_longitude=birth_sun_long, direction=1)
    target_fractional_arc = fractional_year * 360.0
    target_longitude = (birth_sun_long - target_fractional_arc) % 360.0
    approx_days_for_fraction = fractional_year * year_length
    final_search_seed = current_jd_anchor - (approx_days_for_fraction + 15.0)
    jd_start, _ = next_planet_entry_date_general(
        final_search_seed, place, const.SUN_ID, planet_longitude=target_longitude, direction=1)
    return jd_start
def _get_dhasa_end_jd_lunar(start_jd, place, total_dasa_years):
    start_moon = _sidereal_longitude_impl(start_jd, place, const._MOON)
    start_sun = _sidereal_longitude_impl(start_jd, place, const._SUN)
    start_elongation = (start_moon - start_sun) % 360.0
    total_tithis = total_dasa_years * 360.0
    total_lunar_months = total_tithis / 30.0
    full_lunar_cycles = int(total_lunar_months)
    fractional_month = total_lunar_months - full_lunar_cycles
    remaining_degrees = fractional_month * 360.0
    target_elongation = (start_elongation + remaining_degrees) % 360.0
    mean_synodic_month = 29.530589
    approx_days_forward = full_lunar_cycles * mean_synodic_month + remaining_degrees / 12.1907
    estimated_target_jd = start_jd + approx_days_forward
    low_jd, high_jd = estimated_target_jd - 1.0, estimated_target_jd + 1.0
    jd_end = estimated_target_jd
    for _ in range(50):
        mid_jd = (low_jd + high_jd) / 2.0
        m_long = _sidereal_longitude_impl(mid_jd, place, const._MOON)
        s_long = _sidereal_longitude_impl(mid_jd, place, const._SUN)
        current_elongation = (m_long - s_long) % 360.0
        diff = (current_elongation - target_elongation + 180.0) % 360.0 - 180.0
        if abs(diff) < 1e-7:
            jd_end = mid_jd
            break
        if diff > 0.0: high_jd = mid_jd
        else: low_jd = mid_jd
    else:
        jd_end = (low_jd + high_jd) / 2.0
    return jd_end
def _get_dhasa_end_jd_tropical(start_jd, place, total_dasa_years):
    """ True-tropical-year dasha end (tropical = sidereal + surya_sidhantha_ayanamsa). """
    if total_dasa_years == 0.0:
        return start_jd
    start_tropical_long = _sun_tropical_longitude(start_jd, place)
    fractional_year = total_dasa_years % 1.0
    target_fractional_arc = fractional_year * 360.0
    target_longitude = (start_tropical_long + target_fractional_arc) % 360.0
    year_length = true_tropical_year(start_jd, place)
    approx_total_days = total_dasa_years * year_length
    final_search_seed = (start_jd + approx_total_days - 0.001 if approx_total_days < 1.0
                          else start_jd + approx_total_days - min(30.0, approx_total_days / 4.0))
    jd_end, _ = _next_sun_tropical_entry_date(
        final_search_seed, place, target_longitude, direction=1)
    return jd_end
def _get_dhasa_end_jd(start_jd, place, total_dasa_years):
    """ Julian day on which a dasa that starts at start_jd ends, using the year length selected by const.dhasa_year_duration_default.
        @param start_jd: Julian Day Number at which the dasa starts
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param total_dasa_years: duration of the dasa in years
        @return: Julian Day Number of the dasa end """
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.MEAN_SIDEREAL_YEAR:
        return start_jd + total_dasa_years * const.sidereal_year
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.MEAN_TROPICAL_YEAR:
        return start_jd + total_dasa_years * const.tropical_year
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.MEAN_LUNAR_YEAR:
        return start_jd + total_dasa_years * const.lunar_year
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.SAVANA_YEAR:
        return _get_dhasa_end_jd_savana(start_jd, place, total_dasa_years)
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.TRUE_LUNAR_YEAR:
        return _get_dhasa_end_jd_lunar(start_jd, place, total_dasa_years)
    if const.dhasa_year_duration_default == const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR:
        return _get_dhasa_end_jd_tropical(start_jd, place, total_dasa_years)
    start_sun_long = _sidereal_longitude_impl(start_jd, place, const._SUN)
    if total_dasa_years == 0.0:
        return start_jd
    fractional_year = total_dasa_years % 1.0
    target_fractional_arc = fractional_year * 360.0
    target_longitude = (start_sun_long + target_fractional_arc) % 360.0
    year_length = const.average_gregorian_year
    approx_total_days = total_dasa_years * year_length
    final_search_seed = (start_jd + approx_total_days - 0.001 if approx_total_days < 1.0
                          else start_jd + approx_total_days - min(30.0, approx_total_days / 4.0))
    jd_end, _ = next_planet_entry_date_general(
        final_search_seed, place, const.SUN_ID, planet_longitude=target_longitude, direction=1)
    return jd_end
# Retrograde / stationary planet lists
def planets_in_retrograde(jd, place):
    """ Planets that are retrograde.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: list of planet indices, e.g. [3,5] """
    retro_planets = []
    _planet_list = {p: p_id for p, p_id in planet_list.items() if p not in (const._SUN, const._MOON)}
    for planet, p_id in _planet_list.items():
        if daily_planet_speed(jd, place, p_id) < 0:
            retro_planets.append(p_id)
    return retro_planets
def planets_in_stationary(jd, place, zero_threshold=None):
    """ Planets that are stationary.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param zero_threshold: speed in degrees per day below which a planet counts as stationary; None: const.one_arc_second
        @return: list of planet indices, e.g. [3,5] """
    if zero_threshold is None: zero_threshold = const.one_arc_second
    excluded = (const._SUN, const._MOON, const._RAHU, const._KETU)
    zero_planets = []
    _planet_list = {p: p_id for p, p_id in planet_list.items() if p not in excluded}
    for planet, p_id in _planet_list.items():
        if abs(daily_planet_speed(jd, place, p_id)) < zero_threshold:
            zero_planets.append(p_id)
    return zero_planets
def ascendant_speed(jd, place, dt=0.02):
    """ Daily motion of the ascendant.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param dt: time step in days used to measure the speed
        @return: speed in degrees per day """
    return daily_planet_speed(jd, place, const._ascendant_symbol, dt=dt)
def asind(x): return math.degrees(math.asin(max(-1.0, min(1.0, x))))
def atand(x): return math.degrees(math.atan(x))
def atan2d(y, x): return math.degrees(math.atan2(y, x))
# Shared helpers (used by both lunar and solar eclipse)
def _ss_moon_latitude(jd, place):
    """ Moon's celestial latitude (degrees), per SS's own simplified
        formula: beta = 270' * sin(Moon_long - Rahu_long). Rao,
        section 9.7 / 10.3. """
    moon_long = _sidereal_longitude_impl(jd, place, const._MOON)
    rahu_long = _sidereal_longitude_impl(jd, place, const._RAHU)
    beta_arcmin = 270.0 * sind(moon_long - rahu_long)
    return beta_arcmin / 60.0  # degrees
def _ss_eclipse_diameters(jd, place):
    """ Sun's, Moon's, and Earth's-shadow's angular diameters (degrees),
        scaled off each body's own TRUE daily motion via the classical
        mean-diameter-in-yojanas ratios (Rao, section 9.7). """
    sdm = abs(daily_planet_speed(jd, place, const.SUN_ID)) * 60.0
    mdm = abs(daily_planet_speed(jd, place, const.MOON_ID)) * 60.0
    scdia = sdm * 6500.0 / 59.136
    sdiay = scdia * 4320000.0 / 57753336.0
    sdia = sdiay / 15.0
    mdiay = mdm * 480.0 / 790.581
    mdia = mdiay / 15.0
    ecdia = mdm * 1600.0 / 790.581
    scdedia = scdia - 1600.0
    shdiay = ecdia - scdedia * 480.0 / 6500.0
    shdia = shdiay / 15.0
    return sdia/60.0, mdia/60.0, shdia/60.0
# Lunar eclipse
def is_lunar_eclipse(jd_full_moon, place):
    """ Checks whether the full moon at jd_full_moon produces a lunar
        eclipse, per the classical SS procedure (Rao, section 9.7 /
        Program 9.1 "SSLEC"). """
    sdia, mdia, shdia = _ss_eclipse_diameters(jd_full_moon, place)
    mlat = _ss_moon_latitude(jd_full_moon, place)
    grasa = 0.5*(mdia+shdia) - abs(mlat)
    is_possible = grasa > 0.0
    is_total = grasa > mdia
    if is_possible:
        sdm = abs(daily_planet_speed(jd_full_moon, place, const.SUN_ID))
        mdm = abs(daily_planet_speed(jd_full_moon, place, const.MOON_ID))
        half_dur = math.sqrt(((shdia+mdia)/2.0)**2 - mlat**2) / (mdm - sdm)
    else:
        half_dur = None
    return {
        'sun_diameter': sdia, 'moon_diameter': mdia, 'shadow_diameter': shdia,
        'moon_latitude': mlat, 'grasa': grasa,
        'is_possible': is_possible, 'is_total': is_total,
        'half_duration_days': half_dur,
    }
def next_lunar_eclipse(jd, place, max_tries=30):
    """ Finds the next full moon (via this module's own full_moon())
        that produces an eclipse (per is_lunar_eclipse()). """
    search_jd = jd
    for _ in range(max_tries):
        ti = tithi(search_jd, place)[0]
        jd_full = full_moon(search_jd, place, ti, opt=1)
        info = is_lunar_eclipse(jd_full, place)
        if info['is_possible']:
            hd = info['half_duration_days']
            return jd_full, info, jd_full - hd, jd_full + hd
        search_jd = jd_full + 20.0
    return None, None, None, None
# Solar eclipse -- requires the parallax (lambana/nati) chain, which
# needs the Lagna and Madhya-Lagna (meridian ecliptic point, "MC").
def _ss_local_sidereal_time_deg(jd, place):
    """ Local sidereal time, in degrees (0-360). """
    jd0 = math.floor(jd - 0.5) + 0.5
    t = (jd0 - 2451545.0) / 36525.0
    gst_deg = (280.46061837 + 360.98564736629*(jd - 2451545.0)
               + 0.000387933*t*t - t*t*t/38710000.0) % 360.0
    lst_deg = (gst_deg + place.longitude) % 360.0
    return lst_deg
def _ss_madhya_lagna(jd, place, eps_deg=24.0):
    """ Madhya Lagna (meridian ecliptic point, "MC"), in degrees, tropical. """
    lst = _ss_local_sidereal_time_deg(jd, place)
    if abs(lst - 90) < 1e-9: return 90.0
    if abs(lst - 270) < 1e-9: return 270.0
    a2 = atand(tand(lst) / cosd(eps_deg))
    if 90 < lst < 270:
        mc = 180 + a2
    else:
        mc = a2
    return mc % 360.0
def _ss_parallax_chain(jd, place, eps_deg=24.0):
    """ Computes drkkshepa, drggati, lambana (parallax in longitude, in
        NADIS -- 1 day = 60 nadis), and dec_mc, per Rao Ch. 10.3 /
        Program 10.1 "SSSEC". """
    lagna = ascendant(jd, place)
    lagna_deg = lagna[0]*30.0 + lagna[1] if isinstance(lagna, (list, tuple)) else lagna
    mc = _ss_madhya_lagna(jd, place, eps_deg=eps_deg)
    orient_sine = sind(eps_deg) * sind(lagna_deg) / cosd(place.latitude)
    dec_mc = asind(sind(eps_deg) * sind(mc))
    merid_zen = dec_mc - place.latitude
    sn_merz = sind(merid_zen)
    osmz = orient_sine * sn_merz
    drkkshepa = math.sqrt(max(0.0, sn_merz**2 - osmz**2))
    drggati = math.sqrt(max(0.0, 1.0 - drkkshepa**2))
    cheda = (sind(30.0)**2) / drggati if drggati != 0 else float('inf')
    sun_long = _sidereal_longitude_impl(jd, place, const._SUN)
    lambana_nadis = sind(mc - sun_long) / cheda if cheda not in (0.0, float('inf')) else 0.0
    return lambana_nadis, drkkshepa, dec_mc
def is_solar_eclipse(jd_new_moon, place):
    """ Checks whether the new moon at jd_new_moon produces a solar
        eclipse, per the classical SS procedure with lambana/nati
        parallax correction (Rao, Ch. 10.3 / Program 10.1 "SSSEC"). """
    jd_app = jd_new_moon
    drkkshepa = 0.0
    for _ in range(4):
        lambana_nadis, drkkshepa, dec_mc = _ss_parallax_chain(jd_app, place)
        jd_app = jd_new_moon + lambana_nadis / 60.0
    mdm_deg = abs(daily_planet_speed(jd_app, place, const.MOON_ID))
    mdm_arcmin = mdm_deg * 60.0
    nati_arcmin = (mdm_arcmin / 15.0) * drkkshepa
    sdia, mdia, shdia = _ss_eclipse_diameters(jd_app, place)
    mlat = _ss_moon_latitude(jd_app, place) + nati_arcmin / 60.0
    grasa = 0.5*(sdia+mdia) - abs(mlat)
    is_possible = grasa > 0.0
    is_total = grasa > sdia
    return {
        'sun_diameter': sdia, 'moon_diameter': mdia,
        'moon_latitude': mlat, 'grasa': grasa,
        'is_possible': is_possible, 'is_total': is_total,
        'jd_apparent_conjunction': jd_app,
    }
def next_solar_eclipse(jd, place, max_tries=30):
    """ Finds the next new moon producing a solar eclipse, analogous
        to next_lunar_eclipse() above. """
    search_jd = jd
    for _ in range(max_tries):
        ti = tithi(search_jd, place)[0]
        jd_new = new_moon(search_jd, place, ti, opt=1)
        info = is_solar_eclipse(jd_new, place)
        if info['is_possible']:
            return jd_new, info
        search_jd = jd_new + 20.0
    return None, None
def ahargana(jd):
    """ Continuous Vateswara Ahargana: days, with fraction, elapsed since the 0h that starts the Kali epoch civil day (Friday 18 Feb 3102
        BC, Julian).
        @param jd: Julian Day Number
        @return: days elapsed since the epoch """
    return jd - const.VS_KALI_EPOCH_JD
# Kali Yuga ahargana used for the calendar year numbering by elapsed_year()
_kali_ahargana_for_calendar = lambda jd: ahargana(jd)
# ENGINE-PARITY PATCH: public sunrise()/sunset()/moonrise()/moonset(),
# matching drik.py's exact return format: [float_hours, "HH:MM:SS
# AM/PM" string, julian_day].
def sunrise(jd, place, eps_deg=24.0):
    """ Sunrise for the date and place.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: [local time in hours, local time string, Julian Day Number] """
    rise_jd = _sunrise_jd(jd, place, eps_deg=eps_deg)
    _, _, _, rise_local_time = utils.jd_to_gregorian(rise_jd)
    return [rise_local_time, utils.to_dms(rise_local_time), rise_jd]
def sunset(jd, place, eps_deg=24.0):
    """ Sunset for the date and place.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @return: [local time in hours, local time string, Julian Day Number] """
    set_jd = _sunset_jd(jd, place, eps_deg=eps_deg)
    _, _, _, set_local_time = utils.jd_to_gregorian(set_jd)
    return [set_local_time, utils.to_dms(set_local_time), set_jd]
def moonrise(jd, place, eps_deg=24.0, search_window_days=1.2):
    """ Local moonrise time.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @param search_window_days: search window in days
        @return: [local time in hours, local time string, Julian Day Number]; None if no moonrise is found in the search window """
    rise_jd = _moonrise_jd(jd, place, eps_deg=eps_deg, search_window_days=search_window_days)
    if rise_jd is None:
        return None
    _, _, _, rise_local_time = utils.jd_to_gregorian(rise_jd)
    return [rise_local_time, utils.to_dms(rise_local_time), rise_jd]
def moonset(jd, place, eps_deg=24.0, search_window_days=1.2):
    """ Local moonset time.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param eps_deg: obliquity of the ecliptic in degrees
        @param search_window_days: search window in days
        @return: [local time in hours, local time string, Julian Day Number]; None if no moonset is found in the search window """
    set_jd = _moonset_jd(jd, place, eps_deg=eps_deg, search_window_days=search_window_days)
    if set_jd is None:
        return None
    _, _, _, set_local_time = utils.jd_to_gregorian(set_jd)
    return [set_local_time, utils.to_dms(set_local_time), set_jd]
# ENGINE-PARITY PATCH: ayanamsa functions matching drik.py's names.
def set_ayanamsa_mode(ayanamsa_mode=None, ayanamsa_value=None, jd=None, place=None):
    """ No-op; this engine has a fixed ayanamsa model.
        @param ayanamsa_mode: accepted for signature compatibility; ignored
        @param ayanamsa_value: accepted for signature compatibility; ignored
        @param jd: Julian Day Number of the date/time; not used
        @param place: Place as struct ('Place',latitude,longitude,timezone); not used
        @return: None """
    pass
def get_ayanamsa_value(jd, place=None):
    """ Ayanamsa value of this model: its own oscillating (trepidation) ayanamsa.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone); required, used to convert jd to UT; raises ValueError if None
        @return: ayanamsa in degrees """
    if place is None:
        raise ValueError("get_ayanamsa_value(jd, place, ...) requires place for the SS engine "
                          "(needed to convert jd to UT inside surya_sidhantha_ayanamsa).")
    return surya_sidhantha_ayanamsa(jd, place)
# ENGINE-PARITY PATCH: Date/Place re-exports, matching drik.py's names.
# Functions present in drik.py, provided here with the same signature and return format.
def _ayanamsa_surya_siddhantha_model(jd):
    """ Surya Siddhantha trepidation ayanamsa (degrees) for the Julian day. Oscillates +/-27 degrees over a 7200-year cycle; same sign convention as drik/Lahiri (sidereal = tropical - ayanamsa). """
    cycle_of_equinoxes = 7200
    ayanamsa_peak_in_degrees = 27.0  # 27 degrees either side from Aries 0 degrees
    kali_yuga_jd = utils.julian_day_number((-3101, 1, 22), (12, 0, 0))
    ss_sideral_year = 365.256363
    diff_days = jd - kali_yuga_jd
    sideral_diff_days = diff_days / ss_sideral_year
    ayanamsa_cycle_fraction = (sideral_diff_days / cycle_of_equinoxes)
    ayanamsa = math.sin(ayanamsa_cycle_fraction * 2.0 * math.pi) * ayanamsa_peak_in_degrees
    return -ayanamsa
def _calculate_ayanamsa_senthil_from_jd(jd):
    """ Senthil ayanamsa (degrees) for the Julian day. """
    reference_jd = 2451545.0  # JD of 2000-01-01 12:00 UT
    sidereal_year = 365.242198781
    p0 = 50.27972324
    m = 0.0002225
    a0 = 85591.25323
    q = m / 2
    diff_days = (jd - reference_jd) # in days
    t = diff_days / sidereal_year
    ayanamsa = a0 + p0*t + q*t*t
    ayanamsa /= 3600
    return ayanamsa
def _dhasavarga(jd, place,divisional_chart_factor=1):
    """
    Planet positions for a given divisional chart factor.
    @param jd: Julian Day Number of the date/time
    @param place: Place as struct ('Place',latitude,longitude,timezone)
    @param divisional_chart_factor: 1=Rasi, 2=Hora, 3=Drekkana ... 60=Shashtyamsa
    @return: [[planet_index,(raasi,longitude_in_raasi)],...]
    """
    jd_utc = jd - place.timezone / 24.
    positions = []
    for planet in planet_list:
        p_id = planet_list.index(planet)
        if planet != const._KETU:
            nirayana_long = sidereal_longitude(jd_utc, planet)
        else: # Ketu
            nirayana_long = ketu(sidereal_longitude(jd_utc, const._RAHU)) # 7 = swe.RAHU
        divisional_chart = dasavarga_from_long(nirayana_long,divisional_chart_factor)
        positions.append([p_id, divisional_chart])
    return positions
jd_to_gregorian = lambda jd: utils.jd_to_gregorian(jd)
def reset_ayanamsa_mode():
    """ No-op; this engine has a fixed ayanamsa model. """
    pass

# =====================================================================
# PART B - identical (character for character) in drik.py and every traditional-model module
# =====================================================================
@lru_cache(maxsize=4096)
def _elevation_lookup(lat, lon):
    try:
        return float(utils.get_elevation(lat, lon)) if const.get_place_elevation_from_internet else 0.0
    except Exception:
        return 0.0
ketu = lambda rahu: (rahu + 180) % 360
rahu = lambda ketu: (ketu + 180) % 360
def _lunar_daily_motion(jd):
    """ lunar daily motion"""
    today_longitude = lunar_longitude(jd)
    tomorrow_longitude = lunar_longitude(jd+1)
    #      print(tomorrow_longitude,today_longitude)
    if (tomorrow_longitude < today_longitude):
      tomorrow_longitude += utils.from_dms(360,0,0)
    daily_motion = tomorrow_longitude - today_longitude
    #      print(tomorrow_longitude,today_longitude)
    return daily_motion
def _solar_daily_motion(jd):
    """ Sun daily motion"""
    today_longitude = solar_longitude(jd)
    tomorrow_longitude = solar_longitude(jd+1)
    if (tomorrow_longitude < today_longitude):
      tomorrow_longitude = tomorrow_longitude + utils.from_dms(360,0,0)
    daily_motion = tomorrow_longitude - today_longitude
    #  print(tomorrow_longitude,today_longitude)
    return daily_motion
def nakshatra_pada(longitude):
    """ 
        Gives nakshatra (1..27) and paada (1..4) in which given longitude lies
        @param longitude: longitude of the planet 
        @return [nakshathra index, paadham, longitude remainder in the nakshathra]
            Note: Nakshatra index [1..27], Paadha [1..4] reminder in float degrees 
    """
    # 27 nakshatras span 360°
    one_star = (360 / 27)  # = 13°20'
    # Each nakshatra has 4 padas, so 27 x 4 = 108 padas in 360°
    one_pada = (360 / 108) # = 3°20'
    quotient = int(longitude / one_star)
    #reminder = (longitude - quotient * one_star)
    reminder = longitude%one_star
    pada = int(reminder / one_pada)
    #  print (longitude,quotient,pada)
    # convert 0..26 to 1..27 and 0..3 to 1..4
    #print(longitude,quotient,reminder,pada)
    return [1 + quotient, 1 + pada,reminder]
def planets_speed_info(jd,place):
    """
        To get the speed information of planets
        @param jd: julian day number (not UTC)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [(longitude,latitude,distance_from_earth,longitude_speed,latitude_speed,distance_speed),...]
    """
    return {planet: _planet_speed_info(jd, place, planet) for _,planet in planet_list.items()}
def midday(jd,place):
    """
        Return midday time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [midday time as local time in float hours, local time string, and midday julian number]
            e.g. [12.1,'12:10 PM',2450424.94]
    """
    sun_rise = sunrise(jd, place)#[2]
    sun_set = sunset(jd, place)#[2]
    _,_,_,srh = utils.jd_to_gregorian(sun_rise[2])
    _,_,_,ssh = utils.jd_to_gregorian(sun_set[2]) # V4.4.0
    mdhl = 0.5*(srh+ssh)
    return mdhl, 0.5*(sun_rise[2]+sun_set[2])
def midnight(jd,place):
    """
        Return midnight time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [midnight time as local time in float hours, local time string, and midnight julian number]
            e.g. [0.1,'00:10 AM',2450424.94]
    """
    sun_rise = sunrise(jd, place)#[2]
    prev_sun_set = sunset(jd-1, place)# V4.8.5
    _,_,_,srh = utils.jd_to_gregorian(sun_rise[2])
    _,_,_,pssh = utils.jd_to_gregorian(prev_sun_set[2]) # V4.8.5
    mnhl = 0.5*(srh+pssh)
    if mnhl < 12:
        mnhl = 12 - mnhl
    else:
        mnhl -= 12
    return mnhl
def day_length(jd, place):
    """
        Return local day length in float hours
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: day length in float hours. e.g. 12.125
    """
    return (sunset(jd, place)[0] - sunrise(jd, place)[0])
def night_length(jd, place):
    """
        Return local night length in float hours
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: night length in float hours. e.g. 12.125
    """
    return (24.0 + sunrise(jd+1, place)[0] - sunset(jd, place)[0])
def _get_tithi(jd,place,tithi_index=1,planet1=const._MOON,planet2=const._SUN,cycle=1):
    # tithi_index = 1=>Janma Tithi 2=>Dhana 3=>Bhratri, 4=>Matri 5=Putra 6=>Satru 7=>Kalatra 8=>Mrutyu 9=>Bhagya 10=>Karma 11=>Laabha 12=>Vyaya
    """
        TODO: Cycle option is not working as per JHora. Algorithm not clear
        So the results cannot be trusted
    """ 
    tz = place.timezone
    # First convert jd to UTC  # 2.0.3
    y, m, d,bt = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[2] # V2.2.8
    # 2. Find tithi at this JDN
    moon_phase = _special_tithi_phase(rise, planet1, planet2, tithi_index, cycle, place)
    today = ceil(moon_phase / 12)
    """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME 
        See Dr. Jayasree Saranatha Mahabharatha date validation book """
    if const.increase_tithi_by_one_before_kali_yuga and jd < const.mahabharatha_tithi_julian_day: #V3.2.0
        #print('tithi increased by 1 before mahabharatha date from',today,'to',today+1)
        today = (today+1)%30
    degrees_left = today * 12 - moon_phase
    # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    planet1_long_diff = [ (sidereal_longitude(rise + t,planet1,place) - sidereal_longitude(rise,planet1,place)) % 360 for t in offsets ]
    planet2_long_diff = [ (sidereal_longitude(rise + t,planet2,place) - sidereal_longitude(rise,planet2,place)) % 360 for t in offsets ]
    relative_motion = [ (tithi_index*(p1-p2)+(cycle-1)*180)%360 for (p1, p2) in zip(planet1_long_diff, planet2_long_diff) ]
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = relative_motion; x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end -jd_utc) * 24 + tz #jd changed to jd_utc 2.0.3
    tithi_no = int(today)
    #""" Start Time 
    answer = [tithi_no, ends]
    # 5. Check for skipped tithi
    moon_phase_tmrw = _special_tithi_phase(rise+1, planet1, planet2, tithi_index, cycle, place)
    tomorrow = ceil(moon_phase_tmrw / 12)
    """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME See Dr. Jayasree Saranatha Mahabharatha datte validation book """
    if jd < const.mahabharatha_tithi_julian_day: #V3.2.0
        tomorrow = (tomorrow+1)%30
    isSkipped = (tomorrow - today) % 30 > 1
    if isSkipped:
        # interpolate again with same (x,y)
        leap_tithi = today + 1
        tithi_no = int(leap_tithi)
        degrees_left = leap_tithi * 12 - moon_phase_tmrw
        approx_end = utils.inverse_lagrange(x, y, degrees_left)
        ends = (rise + approx_end -jd_utc) * 24 + tz #jd changed to jd_utc 2.0.3
        leap_tithi = 1 if today == 30 else leap_tithi
        answer += [tithi_no, ends]
    return answer
def tithi_using_planet_speed(jd,place,tithi_index=1,planet1=const._MOON,planet2=const._SUN,cycle=1):
    _,_,_,jd_hours = utils.jd_to_gregorian(jd)
    def _get_tithi_using_planet_speed(jd,place):
        jd_utc = jd - place.timezone/24.
        #sunrise_jd = sunrise(jd, place)[2]
        tithi_phase = _special_tithi_phase(jd_utc, planet1=planet1, planet2=planet2, tithi_index=tithi_index, cycle=cycle, place=place)
        total = tithi_phase % 360
        one_tithi = 360/30
        tit = ceil(total /one_tithi)
        tithi_no = int(tit)
        degrees_left = tit * one_tithi-total
        one_day_hours = day_length(jd, place)+night_length(jd, place)
        """ Use only Moon/Sun Speeds for end time calculations and not the speeds of respective planets """
        daily_planet1_motion = daily_moon_speed(jd,place)
        daily_planet2_motion = daily_sun_speed(jd,place)
        end_time = jd_hours + (degrees_left / (tithi_index*(daily_planet1_motion-daily_planet2_motion))
                               *one_day_hours)
        frac_left = degrees_left/one_tithi
        start_time = end_time - (end_time-jd_hours)/frac_left
        """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME 
            See Dr. Jayasree Saranatha Mahabharatha date validation book
        """
        #"""
        if const.increase_tithi_by_one_before_kali_yuga and jd < const.mahabharatha_tithi_julian_day: #V3.2.0
            #print('tithi increased by 1 before mahabharatha date from',tithi_no,'to',tithi_no+1)
            tithi_no = (tithi_no)%30+1
        #"""
        return [tithi_no,start_time,end_time]
    ret = _get_tithi_using_planet_speed(jd,place)
    if ret[2] < 24:
        ret1 = _get_tithi_using_planet_speed(jd+ret[2]/24, place)
        #print('next tithi',ret1)
        _next_tithi = (ret[0])%30+1; _next_tithi_start_time = ret[2]; _next_tithi_end_time = ret[2]+ret1[2]
        ret += [_next_tithi,_next_tithi_start_time,_next_tithi_end_time]
    return ret
def tithi(jd,place,tithi_index=1,planet1=const._MOON, planet2=const._SUN,cycle=1,force_tithi_at_sunrise=False):
    """
        Tithi given jd and place, with its start and end times; the method is set by const.tithi_yogam_calculation_method_default
        (const.TITHI_YOGAM_CALCULATION_METHODS: SPEED, LAGRANGE or PHASE_BOUNDARY)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param tithi_index = 1=>Janma Tithi 2=>Dhana 3=>Bhratri, 4=>Matri 5=Putra 6=>Satru 7=>Kalatra
                            8=>Mrutyu 9=>Bhagya 10=>Karma 11=>Laabha 12=>Vyaya (Default Janma tithi)
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param cycle: phase cycle number (1..3)
        @param force_tithi_at_sunrise: True - tithi prevailing at the sunrise of the date of jd
                                       False (default) - tithi prevailing at the jd instant itself
        @return [tithi number, tithi starting time, tithi ending time,
                 next tithi number, next tithi starting time, next tithi ending time]
          times are float hours from local midnight of the date of jd; the next tithi is returned only if the tithi ends before midnight
          tithi number = [1..30]
    """
    """
        TODO: Handle similar to JHora if planets are same
    """
    jd_tithi = sunrise(jd,place)[2] if force_tithi_at_sunrise else jd # V4.8.5
    _method = const.tithi_yogam_calculation_method_default
    if _method == const.TITHI_YOGAM_CALCULATION_METHODS.PHASE_BOUNDARY:
        return tithi_using_phase_boundary(jd_tithi, place, tithi_index, planet1, planet2, cycle)
    elif _method == const.TITHI_YOGAM_CALCULATION_METHODS.SPEED:
        return tithi_using_planet_speed(jd_tithi, place, tithi_index, planet1, planet2, cycle)
    else:
        return tithi_using_inverse_lagrange(jd_tithi, place, tithi_index, planet1, planet2, cycle)
def tithi_using_inverse_lagrange(jd,place,tithi_index=1,planet1=const._MOON, planet2=const._SUN,cycle=1):    
    """
        Tithi given jd and place. Also returns tithi's end time.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param tithi_index = 1=>Janma Tithi 2=>Dhana 3=>Bhratri, 4=>Matri 5=Putra 6=>Satru 7=>Kalatra 
                            8=>Mrutyu 9=>Bhagya 10=>Karma 11=>Laabha 12=>Vyaya (Default Janma tithi)
        @return [tithi number, tithi_start_time, tithi ending time, tithi_fraction,
                 next_tithi_number, next_tithi_start_time, next_tithi ending time, next_tithi_fraction]
          next tithi number and next tithi time is additionally returned if two tithis on same day
    """
    """
        TODO: Handle similar to JHora if planets are same
    """
    def __get_tithi_lagrange(jd,place,tithi_index=tithi_index,planet1=planet1, planet2=planet2,cycle=cycle):
        _tithi = _get_tithi(jd,place,tithi_index,planet1,planet2,cycle=cycle)
        _tithi_prev = _get_tithi(jd-1,place,tithi_index,planet1,planet2,cycle=cycle)
        _tithi_no = _tithi[0]; _tithi_start = _tithi_prev[1]; _tithi_end = _tithi[1]
        if _tithi_start < 24.0:
            _tithi_start = -_tithi_start
        elif _tithi_start > 24:
            _tithi_start -= 24.0
        result = [_tithi_no,_tithi_start,_tithi_end]
        return result
    ret = __get_tithi_lagrange(jd,place,tithi_index=tithi_index,planet1=planet1, planet2=planet2,cycle=cycle)
    if ret[2] < 24.0:
        ret1 = __get_tithi_lagrange(jd+ret[2]/24,place,tithi_index=tithi_index,planet1=planet1, planet2=planet2,cycle=cycle)
        _next_tithi = (ret[0])%30+1; _next_tithi_start_time = ret[2]; _next_tithi_end_time = ret[2]+ret1[2]
        ret += [_next_tithi,_next_tithi_start_time,_next_tithi_end_time]
    return ret
def _phase_boundary(phase_fn, jd, target_angle, direction, step_days, max_days):
    """ Local civil-time Julian day at which phase_fn(t) crosses target_angle, searching from jd forward or backward: steps until the signed
        phase difference changes sign near the target, then bisects to sub-second precision. If the window is missed it is doubled and
        retried. Shared by tithi() and yogam().
        @param phase_fn: angle in degrees as a function of the local civil-time Julian day
        @param jd: Julian Day Number at which the search starts
        @param target_angle: angle in degrees to be crossed
        @param direction: +1 = forward, -1 = backward
        @param step_days: search step in days, from _tithi_search_window() / _yoga_search_window()
        @param max_days: initial search window in days
        @return: Julian Day Number of the crossing; raises ValueError if it is not found """
    def f(t):
        return (phase_fn(t) - target_angle + 180.0) % 360.0 - 180.0

    def _search(step_days, max_days):
        t0 = jd; f0 = f(t0)
        if f0 == 0.0:
            return t0
        for _ in range(int(max_days/step_days) + 1):
            t1 = t0 + direction*step_days; f1 = f(t1)
            if f1 == 0.0:
                return t1
            if (f0 < 0) != (f1 < 0) and abs(f0) < 90.0 and abs(f1) < 90.0:
                lo, hi, f_lo = (t0, t1, f0) if t0 < t1 else (t1, t0, f1)
                for _ in range(60):
                    mid = 0.5*(lo+hi); f_mid = f(mid)
                    if (f_mid < 0) == (f_lo < 0):
                        lo, f_lo = mid, f_mid
                    else:
                        hi = mid
                return 0.5*(lo+hi)
            t0, f0 = t1, f1
        return None

    cur_step, cur_max = step_days, max_days
    for _ in range(6):                       # widen up to ~32x before giving up
        result = _search(cur_step, cur_max)
        if result is not None:
            return result
        cur_max *= 2
        cur_step = min(cur_step * 1.5, cur_max / 20)
    raise ValueError(f"Phase boundary at {target_angle} degrees not found within {cur_max:.0f} days")
def _tithi_search_window(planet1, planet2, tithi_index=1):
    """ Search step and window for _phase_boundary(), sized from the planets' fixed mean daily motions. The tithi phase is a difference of
        longitudes, so its rate is |s1-s2|.
        @param planet1: swe-style key of the first planet
        @param planet2: swe-style key of the second planet
        @param tithi_index: multiplier of the phase (1 = Janma tithi)
        @return: (step_days, max_days) """
    s1 = const.daily_mean_motions.get(planet1, 1.0)
    s2 = const.daily_mean_motions.get(planet2, 1.0)
    speed = max(abs(tithi_index * (s1 - s2)), 0.005)   # deg/day of PHASE; floored, never zero
    step_days = min(max(0.5 / speed, 0.05), 5.0)
    max_days  = min(max(3.0, 60.0 / speed), 40000.0)
    return step_days, max_days
def _yoga_search_window(planet1, planet2, tithi_index=1):
    """ Search step and window for _phase_boundary(), sized from the planets' fixed mean daily motions. The yogam phase is a sum of
        longitudes, so its rate is |s1+s2|.
        @param planet1: swe-style key of the first planet
        @param planet2: swe-style key of the second planet
        @param tithi_index: multiplier of the phase (1 = Janma yogam)
        @return: (step_days, max_days) """
    s1 = const.daily_mean_motions.get(planet1, 1.0)
    s2 = const.daily_mean_motions.get(planet2, 1.0)
    speed = max(abs(tithi_index * (s1 + s2)), 0.005)
    step_days = min(max(0.5 / speed, 0.05), 5.0)
    max_days  = min(max(3.0, 60.0 / speed), 40000.0)
    return step_days, max_days
def tithi_using_phase_boundary(jd,place,tithi_index=1,planet1=const._MOON,planet2=const._SUN,cycle=1):
    """
        Tithi with its start and end times, each found as the instant at which the phase crosses the 12 degree boundary
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param tithi_index: multiplier of the phase (1=Janma tithi)
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param cycle: phase cycle number (1..3)
        @return [tithi number, tithi starting time, tithi ending time,
                 next tithi number, next tithi starting time, next tithi ending time]
          times are float hours from local midnight of the date of jd; the next tithi is returned only if the tithi ends before midnight
    """
    y, m, d, _ = utils.jd_to_gregorian(jd)
    jd_midnight = utils.gregorian_to_jd(Date(y, m, d))
    to_hours = lambda x: (x - jd_midnight) * 24.0
    phase_fn = lambda t: _special_tithi_phase(t - place.timezone/24.0, planet1, planet2, tithi_index, cycle, place)
    step_days, max_days = _tithi_search_window(planet1, planet2, tithi_index)
    one_tithi = 360.0/30.0
    tithi_no = min(int(phase_fn(jd) // one_tithi) + 1, 30)
    start_jd = _phase_boundary(phase_fn, jd, (tithi_no-1)*one_tithi, -1, step_days, max_days)
    end_jd = _phase_boundary(phase_fn, jd, (tithi_no*one_tithi) % 360.0, +1, step_days, max_days)
    def _number(t):
        """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME
            See Dr. Jayasree Saranatha Mahabharatha date validation book """
        if const.increase_tithi_by_one_before_kali_yuga and jd < const.mahabharatha_tithi_julian_day: return t % 30 + 1
        return t
    result = [_number(tithi_no), to_hours(start_jd), to_hours(end_jd)]
    if to_hours(end_jd) < 24.0:
        next_no = tithi_no % 30 + 1
        next_end_jd = _phase_boundary(phase_fn, end_jd, (next_no*one_tithi) % 360.0, +1, step_days, max_days)
        result += [_number(next_no), to_hours(end_jd), to_hours(next_end_jd)]
    return result
def _special_tithi_phase(jd_utc,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1,place=None):
    """ Tithi phase at a UTC Julian day.
        @param jd_utc: Julian Day Number, UTC
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param tithi_index: multiplier of the phase (1=Janma tithi, 2=Dhana ... 12=Vyaya)
        @param cycle: phase cycle number (1..3)
        @param place: Place as struct ('Place',latitude,longitude,timezone); passed on to sidereal_longitude()
        @return: phase angle in degrees (0..360) """
    planet1_long = sidereal_longitude(jd_utc,planet1,place)
    planet2_long = sidereal_longitude(jd_utc,planet2,place)
    tithi_phase = (tithi_index*(planet1_long - planet2_long)+(cycle-1)*180) % 360
    return tithi_phase
def raasi(jd, place):
    """
        returns the raasi at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [raasi number, raasi ending time, raasi fraction left, 
                 next raasi number, next raasi ending time, next rasi fraction left]
          next raasi index and next raasi time is additionally returned if two raasis on same day 
          raasi number = [1..12]        
    """
    tz = place.timezone
    # First convert jd to UTC # 2.0.3
    y, m, d, _ = jd_to_gregorian(jd)
    jd_utc = jd - tz/24.
    jd_midnight = utils.gregorian_to_jd(Date(y, m, d)) # 0h of the date: the origin of the end-time hours
    rise = sunrise(jd, place)[2] # - tz / 24 #V2.3.0
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [lunar_longitude(rise+t, place) for t in offsets] #V2.3.0 # Fixed 1.1.0 lunar longitude from sunrise to next sunrise
    nirayana_long = lunar_longitude(jd_utc, place) # V5.0 reverted to jd_utc
    raasi_no = int(nirayana_long/30)+1
    frac_left = 1.0 - (nirayana_long/30) % 1
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, raasi_no * 30)
    ends = (rise - jd_midnight + approx_end) * 24 + tz
    answer = [raasi_no, ends, frac_left]
    
    # 4. Check for skipped raasi
    raasi_tmrw = ceil(longitudes[-1] / 30)
    frac_left = 1.0 - (longitudes[-1] / 30) % 1
    isSkipped = (raasi_tmrw - raasi_no) % 12 > 1
    if isSkipped:
        leap_raasi = raasi_no + 1
        approx_end = utils.inverse_lagrange(offsets, longitudes, leap_raasi * 30)
        ends = (rise+1 - jd_midnight + approx_end) * 24 + tz #rise => rise + 1
        leap_raasi = 1 if raasi_no == 12 else leap_raasi
        raasi_no = int(leap_raasi)
        answer += [raasi_no, ends, frac_left]
    return answer
def _get_nakshathra(jd, place):
    """
        Nakshatra at the given time and the ending times of it and of the next nakshatra, from the Moon's longitudes at sunrise
        (5-point inverse Lagrange interpolation; the angle range is extended when the longitudes wrap around 0/360 degrees, e.g. for Revathi)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [nakshatra number, paadham number, nakshatra ending time,
                 next nakshatra number, paadham number, next nakshatra ending time]
          nakshatra number = [1..27]  Aswini to Revathi; paadham number = [1..4]
          times are float hours from local midnight of the date of jd
    """
    tz = place.timezone
    y, m, d, _ = utils.jd_to_gregorian(jd)
    jd_ut = utils.gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2]
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise + t, const._MOON, place) for t in offsets]
    unwrapped_longitudes = utils.unwrap_angles(longitudes)
    #print("Unwrapped longitudes:", unwrapped_longitudes)

    # Extend angle range if needed
    extended_longitudes = utils.extend_angle_range(unwrapped_longitudes, 360)
    x = offsets * (len(extended_longitudes) // len(unwrapped_longitudes))
    
    nirayana_long = lunar_longitude(jd_utc, place)
    nak_no, padam_no, _ = nakshatra_pada(nirayana_long)
    y_check = (nak_no * 360 / 27)

    # Normalize y_check to the same range as extended_longitudes
    y_check = utils.normalize_angle(y_check, start=min(extended_longitudes))
    approx_end = utils.inverse_lagrange(x, extended_longitudes, y_check)
    #print(x, extended_longitudes, y_check, approx_end)

    ends = (rise - jd_ut + approx_end) * 24 + tz
    answer = [nak_no, padam_no, ends]
    leap_nak = nak_no + 1
    y_check = (leap_nak * 360 / 27)
    y_check = utils.normalize_angle(y_check, start=min(extended_longitudes))
    approx_end = utils.inverse_lagrange(x, extended_longitudes, y_check)
    ends = (rise - jd_ut + approx_end) * 24 + tz # V4.3.0 Changed back to jd_ut from jd_utc
    leap_nak = 1 if nak_no == 27 else leap_nak
    nak_no = int(leap_nak)
    answer += [nak_no, padam_no, ends]
    return answer
def _get_nakshathra_old(jd,place):
    """
        TODO: For Revathi 4th padha specifically - when looking for 360 deg end, Lagrange gives strange results
                because offsets may near 0 degrees while longitudes near 360
    """
    tz = place.timezone
    y, m, d, _ = jd_to_gregorian(jd)
    jd_ut = utils.gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2] # Changed to jd_utc in V2.9.6
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise+t, const._MOON, place) for t in offsets]
    nirayana_long = lunar_longitude(jd_utc, place) # Changed to jd_utc in V2.9.7
    nak_no,padam_no,_ = nakshatra_pada(nirayana_long)
    y = utils.unwrap_angles(longitudes)
    x = offsets; y_check = (nak_no * 360 / 27)
    approx_end = utils.inverse_lagrange(x, y, y_check)
    ends = (rise - jd_ut + approx_end) * 24 + tz
    answer = [nak_no,padam_no, ends]
    # 4. Check for skipped nakshatra
    leap_nak = nak_no + 1
    y_check = (leap_nak * 360 / 27)
    approx_end = utils.inverse_lagrange(offsets, longitudes, y_check)
    ends = (rise - jd_ut + approx_end) * 24 + tz
    leap_nak = 1 if nak_no == 27 else leap_nak
    nak_no = int(leap_nak)
    answer += [nak_no,padam_no, ends]
    return answer
def nakshatra(jd,place):
    """
        returns the nakshathra at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [nakshatra number, nakshatra starting time, nakshatra ending time, nakshatra fraction left, 
                 next nakshatra number, next nakshatra starting time, next nakshatra ending time, next nakshatra fraction left]
          next nakshatra index and next nakshatra time is additionally returned if two nakshatras on same day 
          nakshatra number = [1..27]  Aswini to Revathi
    """
    _nak = _get_nakshathra(jd, place)
    _nak_prev = _get_nakshathra(jd-1, place)
    _nak_no = _nak[0]; _pad_no = _nak[1]; _nak_start = _nak_prev[2]; _nak_end = _nak[2]
    if _nak_start < 24.0:
        _nak_start = -_nak_start
    elif _nak_start > 24:
        _nak_start -= 24.0
    result = [_nak_no,_pad_no,_nak_start,_nak_end]+_nak[3:]
    return result
def nakshatra_new(jd,place):
    """
        returns the nakshathra at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [nakshatra number, nakshatra starting time, nakshatra ending time, nakshatra fraction left, 
                 next nakshatra number, next nakshatra starting time, next nakshatra ending time, next nakshatra fraction left]
          next nakshatra index and next nakshatra time is additionally returned if two nakshatras on same day 
          nakshatra number = [1..27]  Aswini to Revathi
    """
    """
        TODO:
            If jd is at the Nakshathra time - results are awkward. Need to check the logic below
    """
    if const.tithi_yogam_calculation_method_default == const.TITHI_YOGAM_CALCULATION_METHODS.LAGRANGE: return nakshatra(jd, place)
    _,_,_,jd_hours = utils.jd_to_gregorian(jd)
    def _get_nakshathra_new(jd):
        jd_utc = jd - place.timezone/24.
        one_star = 360/27
        moon_long = lunar_longitude(jd_utc, place)
        nak_no, padam_no, _ = nakshatra_pada(moon_long)
        degrees_left = nak_no*one_star-moon_long
        end_time = jd_hours + degrees_left/daily_moon_speed(jd,place)*24
        #frac_left = degrees_left/one_star
        ret = [nak_no,padam_no,end_time]
        return ret
    _nak = _get_nakshathra_new(jd)
    _nak_prev = _get_nakshathra_new(jd-1)
    _nak_no = _nak[0]; _pad_no = _nak[1]; _nak_start = _nak_prev[2]; _nak_end = _nak[2]
    if _nak_start < 24.0:
        _nak_start = -_nak_start
    elif _nak_start > 24:
        _nak_start -= 24.0
    result = [_nak_no,_pad_no,_nak_start,_nak_end]+_nak[3:]
    return result
def _special_yoga_phase(jd_utc,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1,place=None):
    """ Yogam phase (sum of the planets' longitudes) at a UTC Julian day.
        @param jd_utc: Julian Day Number, UTC
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param tithi_index: multiplier of the phase (1=Janma yogam)
        @param cycle: phase cycle number (1..3)
        @param place: Place as struct ('Place',latitude,longitude,timezone); passed on to sidereal_longitude()
        @return: phase angle in degrees (0..360) """
    planet1_long = sidereal_longitude(jd_utc,planet1,place)
    planet2_long = sidereal_longitude(jd_utc,planet2,place)
    tithi_phase = (tithi_index*(planet1_long + planet2_long)+(cycle-1)*180) % 360
    return tithi_phase
def _get_yogam(jd,place,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1):
    # 1. Find time of sunrise
    city, lat, lon, tz = place
    y, m, d,bt = jd_to_gregorian(jd);jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    rise = sunrise(jd, place)[2] # V2.2.8
    one_yoga = 360./27.
    # 2. Find the Nirayana longitudes and add them
    total = _special_yoga_phase(rise, planet1, planet2, tithi_index, cycle, place)
    # There are 27 Yogas spanning 360 degrees
    yog = ceil(total /one_yoga)
    yogam_no = int(yog)
    # 3. Find how many longitudes is there left to be swept
    degrees_left = yog * one_yoga - total
    
    # 3. Compute longitudinal sums at intervals of 0.25 days from sunrise
    offsets = [0.0,0.25, 0.5, 0.75, 1.0]
    """ Use only Moon/Sun longitudes for end time calculations and not the speeds of respective planets """
    planet1_long_diff = [ (lunar_longitude(rise + t, place) - lunar_longitude(rise, place)) % 360 for t in offsets ]
    planet2_long_diff = [ (solar_longitude(rise + t, place) - solar_longitude(rise, place)) % 360 for t in offsets ]
    total_motion = [ (tithi_index*(p1+p2)+(cycle-1)*180)%360 for (p1, p2) in zip(planet1_long_diff, planet2_long_diff) ]
    
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = total_motion
    x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end - jd_utc) * 24 + tz
    #print(utils.jd_to_gregorian(rise),utils.jd_to_gregorian(jd_utc),utils.jd_to_gregorian(rise+approx_end),total,yog,degrees_left,x,y,approx_end,ends)
    answer = [yogam_no, ends]
    # 5. Check for skipped yoga
    total_tmrw = _special_yoga_phase(rise+1, planet1, planet2, tithi_index, cycle, place)
    tomorrow = ceil(total_tmrw / one_yoga)
    isSkipped = (tomorrow - yog) % 27 > 1
    if isSkipped:
        # interpolate again with same (x,y)
        leap_yog = yog + 1
        degrees_left = leap_yog * one_yoga - total
        approx_end = utils.inverse_lagrange(x, y, degrees_left)
        ends = (rise + approx_end - jd_utc) * 24 + tz
        leap_yog = 1 if yog == 27 else leap_yog
        yogam_no = int(leap_yog)
        answer += [yogam_no, ends]
    return answer
def yogam(jd,place,tithi_index=1,planet1=const._MOON,planet2=const._SUN,cycle=1):
    """
        returns the yogam at julian day/time; the method is set by const.tithi_yogam_calculation_method_default
        (const.TITHI_YOGAM_CALCULATION_METHODS: SPEED, LAGRANGE or PHASE_BOUNDARY); with SPEED the end times use the daily speeds of the Moon and the Sun
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param tithi_index: multiplier of the phase (1=Janma yogam)
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param cycle: phase cycle number (1..3)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left,
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          times are float hours from local midnight of the date of jd; the next yogam is returned only if the yogam ends before midnight
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
    _method = const.tithi_yogam_calculation_method_default
    if _method == const.TITHI_YOGAM_CALCULATION_METHODS.LAGRANGE: return yogam_old(jd, place)
    if _method == const.TITHI_YOGAM_CALCULATION_METHODS.PHASE_BOUNDARY: return yogam_using_phase_boundary(jd, place, tithi_index, planet1, planet2, cycle)
    _,_,_,jd_hours = utils.jd_to_gregorian(jd)
    def _get_yogam_new(jd):
        jd_utc = jd - place.timezone/24.
        yoga_phase = _special_yoga_phase(jd_utc, planet1=planet1, planet2=planet2, tithi_index=tithi_index, cycle=cycle, place=place)
        total = yoga_phase % 360
        one_yoga = 360/27
        yog = ceil(total /one_yoga)
        yogam_no = int(yog)
        # 3. Find how many longitudes is there left to be swept
        degrees_left = yog * one_yoga-total
        """ Use only Moon/Sun Speeds for end time calculations and not the speeds of respective planets """
        daily_planet1_motion = daily_moon_speed(jd,place)
        daily_planet2_motion = daily_sun_speed(jd,place)
        end_time = jd_hours + degrees_left/(daily_planet1_motion+daily_planet2_motion)*24
        frac_left = degrees_left/one_yoga
        start_time = end_time - (end_time-jd_hours)/frac_left
        #print('_get_yogam_new',yogam_no,end_time,'fracion left',frac_left,start_time)
        return [yogam_no,start_time,end_time,frac_left]
    result = _get_yogam_new(jd)
    if result[2] < 24:
        # FIX: next yogam starts at local midnight + result[2] hours (result[2] was added to jd in days before)
        y_, m_, d_, _ = utils.jd_to_gregorian(jd)
        jd_next = utils.gregorian_to_jd(Date(y_, m_, d_)) + result[2]/24.0
        one_yoga = 360/27
        duration = one_yoga/(daily_moon_speed(jd_next,place)+daily_sun_speed(jd_next,place))*24
        next_res = [result[0]%27+1, result[2], result[2]+duration, 0.0]
        next_res[3] = utils.get_fraction(next_res[1], next_res[2], jd_hours)
        result += next_res
    return result
def yogam_old(jd,place,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1):
    """
        returns the yogam at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left, 
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          next yogam index and next yogam time is additionally returned if two yogams on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
    """
        TODO: Ending time calculation using get_yogam() appears incorrect
    """
    _yoga = _get_yogam(jd,place, planet1, planet2, tithi_index, cycle)
    _yoga_prev = _get_yogam(jd-1,place, planet1, planet2, tithi_index, cycle)
    _yoga_no = _yoga[0]; _yoga_start = _yoga_prev[1]; _yoga_end = _yoga[1]
    if _yoga_start < 24.0:
        _yoga_start = -_yoga_start #utils.to_dms(_tithi_start)+'(-1)'
    elif _yoga_start > 24:
        _yoga_start -= 24.0
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    yoga_frac = utils.get_fraction(_yoga_start, _yoga_end, birth_time_hrs)
    result = [_yoga_no,_yoga_start,_yoga_end]+_yoga[2:]
    return result
def yogam_using_phase_boundary(jd,place,tithi_index=1,planet1=const._MOON,planet2=const._SUN,cycle=1):
    """
        Yogam with its start and end times, each found as the instant at which the phase crosses the 360/27 degree boundary
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param tithi_index: multiplier of the phase (1=Janma yogam)
        @param planet1: swe-style key of the first planet (default Moon)
        @param planet2: swe-style key of the second planet (default Sun)
        @param cycle: phase cycle number (1..3)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left,
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          times are float hours from local midnight of the date of jd; the next yogam is returned only if the yogam ends before midnight
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
    y, m, d, jd_hours = utils.jd_to_gregorian(jd)
    jd_midnight = utils.gregorian_to_jd(Date(y, m, d))
    to_hours = lambda x: (x - jd_midnight) * 24.0
    phase_fn = lambda t: _special_yoga_phase(t - place.timezone/24.0, planet1, planet2, tithi_index, cycle, place)
    step_days, max_days = _yoga_search_window(planet1, planet2, tithi_index)
    one_yoga = 360.0/27.0
    phase = phase_fn(jd)
    yogam_no = min(int(phase // one_yoga) + 1, 27)
    start_jd = _phase_boundary(phase_fn, jd, (yogam_no-1)*one_yoga, -1, step_days, max_days)
    end_jd = _phase_boundary(phase_fn, jd, (yogam_no*one_yoga) % 360.0, +1, step_days, max_days)
    result = [yogam_no, to_hours(start_jd), to_hours(end_jd), (yogam_no*one_yoga - phase)/one_yoga]
    if to_hours(end_jd) < 24.0:
        next_no = yogam_no % 27 + 1
        next_end_jd = _phase_boundary(phase_fn, end_jd, (next_no*one_yoga) % 360.0, +1, step_days, max_days)
        next_start, next_end = to_hours(end_jd), to_hours(next_end_jd)
        result += [next_no, next_start, next_end, utils.get_fraction(next_start, next_end, jd_hours)]
    return result
def karana(jd, place):
    """
        returns the karanam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return karanam index, karanam starting time, karanam ending time
          karanam index = [1..60]  1 = Kimstugna, 2 = Bava, ..., 60 = Naga
          each tithi has two karanams: the first half and the second half of the tithi
          times are float hours from local midnight of the date of jd
    """
    _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    _tithi = tithi(jd,place)
    _t_start = _tithi[1]; _t_end = _tithi[2]; _t_mid = 0.5*(_t_start+_t_end)
    _karana = _tithi[0]*2-1
    if birth_time_hrs> _t_mid: # second half of tithi
        _karana += 1
        _k_start = _t_mid; _k_end = _t_end
    else: # first of tithi
        _k_start = _t_start; _k_end = _t_mid
    return _karana,_k_start,_k_end
def civil_weekday(jd):
    """
        returns civil Weekday (local midnight to midnight)
        @param jd: Julian Day Number of the date/time
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    return math.floor(jd+1.5)%7
def vedic_weekday(jd, place):
    """
        returns Vedic Weekday (sunrise to sunrise)
        @param jd: Julian Day Number of the date/time
        @param place Place(city,latitude,longitude,timezone_hours)
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    cw = civil_weekday(jd)
    t_local_hour = utils.jd_to_gregorian(jd)[-1]
    sr = sunrise(jd, place)
    sunrise_local_hour = float(sr[0])
    return (cw - 1) % 7 if t_local_hour < sunrise_local_hour else cw
def vaara(jd,place,show_vedic_day=True):
    """
        Weekday for given Julian day. 
        @param jd: Julian Day Number of the date/time
        @param place Place(city,latitude,longitude,timezone_hours)
        @param show_vedic_day
            True will return day based sunrise to sunrise. (Default)
            False will return civil day (local midnight to midnight)
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    return vedic_weekday(jd, place) if show_vedic_day else civil_weekday(jd)
def vaara_from_ahargana(jd):
    """
        Weekday for given Julian day. 
        @param jd: Julian Day Number of the date/time
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    return ( int(ahargana(jd)) % 7 + 5) % 7 if const.use_aharghana_for_vaara_calcuation else int(ceil(jd + 1) % 7)  
def _solar_raasi_at(jd, place):
    """Returns the Sun's (1-based) zodiac sign (1=Aries..12=Pisces) at the given jd.
    """
    jd_utc = jd - place.timezone / 24.0
    _tropical = getattr(const, '_TROPICAL_MODE', False)
    try:
        const._TROPICAL_MODE = False
        sun_long = solar_longitude(jd_utc, place) % 360.0
    finally:
        const._TROPICAL_MODE = _tropical
    return int(sun_long // 30) % 12 + 1
def _bounding_new_moons(jd, place):
    """Returns (previous new moon, next new moon) bounding the given jd."""
    critical = sunrise(jd, place)[2]
    ti = tithi(critical, place)[0]
    return (new_moon(critical, place, ti, -1),
            new_moon(critical, place, ti, +1))
def lunar_month(jd, place):
    """
        Returns lunar month and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [indian month index, is_adhika_boolean, is_nija_boolean, is_kshaya_boolean]
            1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            True if adhika lunar_month (0 sankrantis in this lunar month)
            True if nija lunar_month (1 sankranti, AND previous month was adhika)
            True if kshaya lunar_month (2 sankrantis in this lunar month -- rare,
                ~once in 122-190 years; per Siddhanta-Siromani, always co-occurs
                with 2 adhika-masas in the same year)
    """
    last_nm, next_nm = _bounding_new_moons(jd, place)
    this_sign = _solar_raasi_at(last_nm, place)
    next_sign = _solar_raasi_at(next_nm, place)
    count = (next_sign - this_sign) % 12

    if count not in (0, 1, 2):
        warnings.warn(f"lunar_month(): unexpected sankranti count {count} "
                      "(expected 0, 1, or 2) -- check solar sign / new_moon() near a rashi boundary.")

    is_adhika = count == 0
    is_kshaya = count == 2
    month = this_sign % 12 + 1

    is_nija = False
    if count in (1,2):
        prev_nm, _ = _bounding_new_moons(last_nm - 2, place)
        is_nija = _solar_raasi_at(prev_nm, place) == this_sign

    return [month, is_adhika, is_nija, is_kshaya]
def lunar_month_date(jd, place, use_purnimanta_system=False):
    """
        Returns lunar month, lunar day and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [indian month index,lunar_day, vedic_year,Adhika_Maasa_Boolean,
                  Nija_Maasa_Boolean,Kshaya_Maasa_Boolean]
            1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            True if adhika lunar_month (0 sankrantis in this lunar month)
            True if nija lunar month (1 sankranti, AND previous month was adhika)
            True if kshaya lunar_month (2 sankrantis in this lunar month -- rare,
                ~once in 122-190 years; per Siddhanta-Siromani, always co-occurs
                with 2 adhika-masas in the same year)
        TODO: Purnimanta System Calculations have not been validated yet.
    """
    critical = sunrise(jd, place)[2]
    ti = tithi(critical, place)[0]
    last_nm, next_nm = _bounding_new_moons(critical, place)

    this_sign = _solar_raasi_at(last_nm, place) - 1
    next_sign = _solar_raasi_at(next_nm, place) - 1
    count = (next_sign - this_sign) % 12

    if count not in (0, 1, 2):
        warnings.warn(f"lunar_month_date(): unexpected sankranti count {count} "
                      "(expected 0, 1, or 2) -- check solar sign / new_moon() near a rashi boundary.")

    is_adhika = count == 0
    is_kshaya = count == 2

    is_nija = False
    if count in (1,2):
        prev_nm, _ = _bounding_new_moons(last_nm - 2, place)
        is_nija = (_solar_raasi_at(prev_nm, place) - 1) == this_sign

    month0 = (this_sign + 1) % 12
    amanta_month = month0 + 1
    lunar_day = utils.cyclic_count_of_numbers(from_number=1, to_number=ti,
                                              number_count=30, direction=1)

    if use_purnimanta_system and lunar_day > 15 and not is_adhika:
        nn_nm = _bounding_new_moons(next_nm + 2, place)[1]
        nn_sign = _solar_raasi_at(nn_nm, place) - 1
        next_count = (nn_sign - next_sign) % 12
        month0 = (next_sign + 1) % 12
        is_nija = next_count == 0
        is_kshaya = next_count == 2
    if use_purnimanta_system:
        lunar_day = (lunar_day - 16) % 30 + 1

    month = month0 + 1
    _lunar_year = lunar_year_index(jd, amanta_month)
    return [month, lunar_day, _lunar_year, is_adhika, is_nija, is_kshaya]
def _nepal_bikram_sambat_civil_date(jd, place):
    """(month, day, year) of the Nepali Bikram Sambat date; month 1 = Baisakh ... 12 = Chaitra"""
    from jhora.panchanga import nepal_bs_calendar
    g_year, g_month, g_day, _ = utils.jd_to_gregorian(jd)
    r = nepal_bs_calendar.ad_to_bs(g_year, g_month, g_day)
    if r is not None:
        return r[1], r[2], r[0]
    # outside BS 1901-2199: approximate with the solar engine (sunset rule); a month start can be a day off
    month_idx, day = solar_month_date(jd, place, const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE)
    bs_year = g_year + (56 if (month_idx >= 9 or (month_idx == 8 and g_month == 1)) else 57)
    return month_idx + 1, day, bs_year

def vedic_date(jd, place,calendar_type=None,sankranti_rule=None,ghatikas=None,hijri_options=None):
    """
        Returns lunar month, lunar day and if it is adhika or not. and the vedic year
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param calendar_type: one of const.CALENDAR_TYPE
             const.CALENDAR_TYPE.SOLAR    Solar Calendar (0 Default)
             const.CALENDAR_TYPE.LUNAR_AMANTHA    1=Amantha and 
             const.CALENDAR_TYPE.PURNIMANTHA    2 = Purnimatha Lunar Calendar
             const.CALENDAR_TYPE.HIJRI_ISLAMIC  3 = Hijri/Islamic Calendar
             const.GREGORIAN                    4 = Gregorian calendar
             const.NANAKSHAHI_PUNJAB            5 = Punjab version
             const.BANGLADESH_REFORMED          6 = Bangladesh version
             const.NEPAL_BIKRAM_SAMBAT          7 = Nepal Bikram Sambat Calendar
        @param sankranti_rule one of - for solar calendar type only
            const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE = 1 (Default: Sankranti day if sun enters zodiac before sunset)
            const.SANKRANTI_RULE.BEFORE_GHATIKAS = 2 (Sankranti day before prescribed ghatikas)
                    ghatikas = 13 => Tamil Calendar
                    ghatikas = 18 => Malabar calendar
                    ghatikas = 30 => Bengal Calendar
                    ghatikas = 45 => Kerala Calendar
            const.SANKRANTI_RULE.SUNRISE_TO_SUNRISE = 3 (Sankranti day if sun enters within sunrise to sunrise)
        @return:
            vedic month,day,year,is_adhik_maasa?,is_nija_maaja?
            Vedic Year 0=Prabhava, 1=Vibhava... 58=Krodhana, 59=Akshaya
            Month range = 1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            adhika lunar_month True/False,
            Nija Month True/False
            Kshaya Month True/False
    """
    if calendar_type == const.CALENDAR_TYPE.GREGORIAN:
        y,m,d,fh = utils.jd_to_gregorian(jd)
        return m,d,y,False,False, False
    if calendar_type == const.CALENDAR_TYPE.NANAKSHAHI_PUNJAB:
        m,d,y = _nanakshahi_civil_date(jd, place)
        return m,d,y,False,False, False
    if calendar_type == const.CALENDAR_TYPE.BANGLADESH_REFORMED:
        m, d, y = _bangladesh_reformed_civil_date(jd, place)
        return m, d, y, False, False, False
    if calendar_type == const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT:
        m, d, y = _nepal_bikram_sambat_civil_date(jd, place)
        return m, d, y, False, False, False
    if calendar_type==const.CALENDAR_TYPE.SOLAR:
        if ghatikas is None: ghatikas = const.calendar_day_ghatikas_after_sunrise
        py,pm,pd,_ = utils.jd_to_gregorian(jd); panchanga_date = Date(py,pm,pd)
        #_month,_day = tamil_solar_month_and_date_from_jd(jd, place)
        _month, _day = solar_month_date(jd, place, sankranti_rule, ghatikas)
        _year = samvatsara(panchanga_date, place, zodiac=0)
        return _month+1,_day,_year, False,False, False
    elif calendar_type==const.CALENDAR_TYPE.HIJRI_ISLAMIC:
        from jhora.panchanga.hijri import islamic_lunar_date as hijri_lunar_date
        y,m,d = hijri_lunar_date(jd,place) if hijri_options is None else hijri_lunar_date(jd,place,hijri_options)
        return m,d,y,False,False, False
    else:
        use_purnimanta_system = (calendar_type==const.CALENDAR_TYPE.LUNAR_PURNIMANTHA)
        return lunar_month_date(jd, place, use_purnimanta_system)
def lunar_year_index(jd,maasa_index):
    """
        Vedic year (samvatsara) index of the lunar year in which jd falls
        @param jd: Julian Day Number of the date/time
        @param maasa_index: lunar month index [1..12]  1 = Chaitra, ..., 12 = Phalguna (see lunar_month())
        @return: samvatsara index  0=Prabhava, 1=Vibhava, ..., 59=Akshaya
    """
    # TODO: samvat_index-1 returns -1 for some dates; the patching below needs investigation
    kali = elapsed_year(jd, maasa_index)[0]
    kali_base = 14; kali_start = 27 # Pramaadhi
    """ Following is patching to match Prmaadhi at kali yuga start date """
    if kali < 4009 and const.force_kali_start_year_for_years_before_kali_year_4009:
        kali_start = const.kali_start_year
    if kali >= 4009:    kali = (kali - kali_base) % 60
    samvat_index = (kali + kali_start + int((kali * 211 - 108) / 18000)) % 60
    return samvat_index-1
def elapsed_year(jd, maasa_index):
    """
        returns Indian era/epoch year indices (kali year number, saka year and vikrama year numbers)
        @param jd: Julian Day Number of the date/time
        @param maasa_index: [1..12] (use jhora.panchanga.drik.lunar_month function to get this) 
        @return kali year number, vikrama year number, saka year number 
    """
    """ TODO - may not be right for dates before Kali yuaga - to be checked """
    ahar = _kali_ahargana_for_calendar(jd)  # or (jd + sunrise(jd, place)[0])
    kali = int((ahar + (4 - maasa_index) * 30) / const.sidereal_year)
    year = jd_to_gregorian(jd)[0]
    #kali = 3101+year
    saka = kali - 3179
    vikrama = saka + 135
    return kali, vikrama, saka
def new_moon(jd, place=None, tithi_=None, opt = -1):
    """Returns JDN, where
       opt = -1:  JDN < jd such that lunar_phase(JDN) = 360 degrees
       opt = +1:  JDN >= jd such that lunar_phase(JDN) = 360 degrees
        @param jd: Julian Day Number, local civil time
        @param place: Place struct ('Place',latitude,longitude,timezone); passed
        @param tithi_: current ordinal tithi day number (1..30) at jd, used
            only to seed the search window. Required.
    """
    if tithi_ is None: tithi_ = tithi(jd,place)[0]
    if opt == -1:  start = jd - tithi_         # previous new moon
    if opt == +1:  start = jd + (30 - tithi_)  # next new moon
    # Search within a span of (start +- 2) days
    x = [ -2 + offset/4 for offset in range(17) ]
    y = [lunar_phase(start + i, place) for i in x]
    y = utils.unwrap_angles(y)
    y0 = utils.inverse_lagrange(x, y, 360)
    #print('new moon',tithi(start+y0,place))
    return start + y0
def full_moon(jd, place=None, tithi_=None, opt = -1):
    """Returns JDN, where
       opt = -1:  JDN < jd such that lunar_phase(JDN) = 180 degrees
       opt = +1:  JDN >= jd such that lunar_phase(JDN) = 180 degrees
        @param jd: Julian Day Number, local civil time
        @param place: Place struct ('Place',latitude,longitude,timezone); passed
        @param tithi_: current ordinal tithi day number (1..30) at jd, used
            only to seed the search window. Required.
    """
    if tithi_ is None: tithi_ = tithi(jd,place)[0]
    if tithi_ <=15:
        start = jd - tithi_ - 15 if opt==-1 else jd + (15-tithi_)
    else:
        start = jd - (tithi_ - 15) if opt==-1 else jd + (45 - tithi_)
    # Search within a span of (start +- 2) days
    x = [ -2 + offset/4 for offset in range(17) ]
    y = [lunar_phase(start + i, place) for i in x]
    y = utils.unwrap_angles(y)
    y0 = utils.inverse_lagrange(x, y, 180)
    return start + y0
def _tithi_bounds_jd(jd, place):
    y, m, d, _ = utils.jd_to_gregorian(jd)
    jd0 = utils.gregorian_to_jd(Date(y, m, d))
    t = tithi(jd, place)
    return t[0], jd0 + t[1]/24.0, jd0 + t[2]/24.0
def next_tithi(jd, place, required_tithi=None, direction=1, start_of_tithi=True, max_steps=40):
    n, s_jd, e_jd = _tithi_bounds_jd(jd, place)
    if required_tithi is None: required_tithi = n % 30 + 1
    m = (required_tithi - 1 if start_of_tithi else required_tithi) % 30 or 30   # boundary = end of tithi m
    step = 1/1440.0   # 1 minute, to hop past a boundary
    for _ in range(max_steps):
        if direction == 1:
            if n == m: return utils.jd_to_gregorian(e_jd)
            n, s_jd, e_jd = _tithi_bounds_jd(e_jd + step, place)
        else:
            if n == m % 30 + 1: return utils.jd_to_gregorian(s_jd)
            n, s_jd, e_jd = _tithi_bounds_jd(s_jd - step, place)
    return None
def next_tithi_by_conjunction(jd, place, required_tithi=None, direction=1, start_of_tithi=True):
    if required_tithi is None: required_tithi = tithi(jd, place)[0] % 30 + 1
    target = ((required_tithi - 1) * 12.0 if start_of_tithi else required_tithi * 12.0) % 360.0
    separation_angle = target if direction == 1 else (360.0 - target) % 360.0
    res = next_conjunction_of_planet_pair(jd, place, const.MOON_ID, const.SUN_ID,
                                          direction=direction, separation_angle=separation_angle)
    return None if res is None else utils.jd_to_gregorian(res[0])
def next_lunar_month(jd, place,lunar_month_type=None,direction=1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type is None: lunar_month_type = const.LUNAR_MONTH_TYPE.AMANTHA
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = (utils.jd_to_gregorian(next_planet_entry_date(const.SUN_ID, jd, place)[0]) if direction==1 
                            else utils.jd_to_gregorian(previous_planet_entry_date(0, jd, place)[0]))
        return Date(lmy,lmm,lmd),lmh
    if lunar_month_type==const.LUNAR_MONTH_TYPE.AMANTHA:
        ncp_jd,_,_ = next_conjunction_of_planet_pair(jd,place, const.SUN_ID, const.MOON_ID, separation_angle=0.0,
                                              direction=direction)
        return utils.jd_to_gregorian(ncp_jd)
    else:
        ncp_jd,_,_ = next_conjunction_of_planet_pair(jd,place, const.SUN_ID, const.MOON_ID, separation_angle=180.0,
                                              direction=direction)
        return utils.jd_to_gregorian(ncp_jd)
def _next_lunar_month(jd, place,lunar_month_type=None,direction=1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type is None: lunar_month_type = const.LUNAR_MONTH_TYPE.AMANTHA
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(next_planet_entry_date(0, jd, place)[0]) if direction==1 else \
                          utils.jd_to_gregorian(previous_planet_entry_date(0, jd, place)[0])
        return Date(lmy,lmm,lmd),lmh
    _tithi_to_check = 30 if lunar_month_type==0 else 15
    tithi_ = tithi(jd,place)[0]
    lm_jd = (new_moon(jd, place, tithi_, opt=direction) if lunar_month_type==const.LUNAR_MONTH_TYPE.AMANTHA 
             else full_moon(jd, place, tithi_, opt=direction) )
    _tit = tithi(lm_jd,place); #; print('tithi',_tit)
    lmh = _tit[2] if _tit[0]==_tithi_to_check else _tit[1]
    lmy,lmm,lmd,_ = utils.jd_to_gregorian(lm_jd)
    if lmh > 24:
        extra_days,lmh = divmod(lmh,24)
        lmy,lmm,lmd = utils.next_panchanga_day(Date(lmy,lmm,lmd), add_days=extra_days)
    elif lmh < 0:
        extra_days,lmh = 1,lmh+24
        lmy,lmm,lmd = utils.previous_panchanga_day(Date(lmy,lmm,lmd), minus_days=extra_days)
    return Date(lmy,lmm,lmd),lmh
def previous_lunar_month(jd, place,lunar_month_type=None,direction=-1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type is None: lunar_month_type = const.LUNAR_MONTH_TYPE.AMANTHA
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = (utils.jd_to_gregorian(next_planet_entry_date(const.SUN_ID, jd, place)[0]) if direction==1 
                            else utils.jd_to_gregorian(previous_planet_entry_date(0, jd, place)[0]))
        return lmy,lmm,lmd,lmh
    if lunar_month_type==const.LUNAR_MONTH_TYPE.AMANTHA:
        ncp_jd,_,_ = next_conjunction_of_planet_pair(jd,place, const.SUN_ID, const.MOON_ID, separation_angle=0.0,
                                              direction=direction)
        return utils.jd_to_gregorian(ncp_jd)
    else:
        ncp_jd,_,_ = next_conjunction_of_planet_pair(jd,place, const.SUN_ID, const.MOON_ID, separation_angle=180.0,
                                              direction=direction)
        return utils.jd_to_gregorian(ncp_jd)
def _previous_lunar_month(jd, place,lunar_month_type=None,direction=-1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type is None: lunar_month_type = const.LUNAR_MONTH_TYPE.AMANTHA
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = (utils.jd_to_gregorian(next_planet_entry_date(const.SUN_ID, jd, place)[0]) if direction==1 
                            else utils.jd_to_gregorian(previous_planet_entry_date(0, jd, place)[0]))
        return lmy,lmm,lmd,lmh
    _tithi_to_check = 30 if lunar_month_type==const.LUNAR_MONTH_TYPE.AMANTHA else 15
    tithi_ = tithi(jd,place)[0]
    lm_jd = (new_moon(jd, place, tithi_, opt=direction) if lunar_month_type==const.LUNAR_MONTH_TYPE.AMANTHA 
             else full_moon(jd, place, tithi_, opt=direction) )
    _tit = tithi(lm_jd,place); #; print('tithi',_tit)
    lmh = _tit[2] if _tit[0]==_tithi_to_check else _tit[1]
    lmy,lmm,lmd,_ = utils.jd_to_gregorian(lm_jd)
    if lmh > 24:
        extra_days,lmh = divmod(lmh,24)
        lmy,lmm,lmd = utils.next_panchanga_day(Date(lmy,lmm,lmd), add_days=extra_days)
    elif lmh < 0:
        extra_days,lmh = 1,lmh+24
        lmy,lmm,lmd = utils.previous_panchanga_day(Date(lmy,lmm,lmd), minus_days=extra_days)
    return Date(lmy,lmm,lmd),lmh
def lunar_phase(jd, place=None, tithi_index=1):
    """
        @param jd: Julian Day Number, local civil time
        @param place: Place struct ('Place',latitude,longitude,timezone)
        @param tithi_index: 1=>Janma Tithi 2=>Dhana ... 12=>Vyaya
        @return: lunar phase angle in degrees (0-360)
    """
    jd_utc = jd - place.timezone / 24.0 if place is not None else jd
    solar_long = solar_longitude(jd_utc, place)
    lunar_long = lunar_longitude(jd_utc, place)
    moon_phase = tithi_index*(lunar_long - solar_long) % 360
    return moon_phase
def samvatsara(panchanga_date,place,zodiac=0):
    """
        Returns Shaka Samvatsara
        @param panchanga_date: Date as struct (year,month,day)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param zodiac: [0 .. 11] Aries/Mesham to Pisces/Meenam
        @return: samvastsara year index [0..59] 
        NOTE: This algorithm is for Solar Years.
         TODO: Chithirai always shows previous year
         Should we use previous sakranti which is solar based? 
        Is there an algorithm for lunar samvastra?
        0=Prabhava, 1=Vibhava... 58=Krodhana, 59=Akshaya
    """ 
    ps = _previous_sankranti_date_new(panchanga_date, place,zodiac=zodiac)
    year = ps[0][0]
    if year >0: year-=1 # To account for removing 0BC/AD Year V4.4.5
    sv = (year-1926)%60
    #if sv==0:
    #    sv=60
    return sv
def ritu(maasa_index):
    """ returns ritu / season index. 
        @param maasa_index: [1..12] (use jhora.panchanga.drik.lunar_month function to get this) 
        @return: ritu index  0 = Vasanta,1=greeshma,2=varsha,3=Sharath,4=hemantha,5 = Shishira
    """
    return (maasa_index - 1) // 2
def gauri_choghadiya(jd, place):
    """
        Get end times of gauri chogadiya for the given julian day
        Chogadiya is 1/8th of daytime or nighttime practiced as time measure in North India 
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [(chogadiyua type,start_time_string,end_time_string)...]
    """
    srise = sunrise(jd, place); sset = sunset(jd,place) # V4.8.5
    day_dur = (sset[0] - srise[0])/24
    end_times = []; start_time = srise[1]
    _vaara = vaara(jd,place)
    for i in range(1, 9):
        gt = srise[2]+(i*day_dur)/8; _,_,_,fh = utils.jd_to_gregorian(gt); end_time = utils.to_dms(fh)
        gc_type = const.gauri_choghadiya_day_table[_vaara][i-1]
        end_times.append((gc_type,start_time,end_time))
        start_time = end_time
    
    # Night duration = time from today's sunset to tomorrow's sunrise
    srise = sunrise(jd+1,place); night_dur = (24+srise[0] - sset[0])/24
    for i in range(1, 9):
        gt = sset[2]+(i*night_dur)/8; _,_,_,fh = utils.jd_to_gregorian(gt); end_time = utils.to_dms(fh)
        gc_type = const.gauri_choghadiya_night_table[_vaara][i-1]
        end_times.append((gc_type,start_time,end_time))
        start_time = end_time
    
    return end_times
def amrit_kaalam(jd,place):
    return [(gb,ge) for gc,gb,ge in gauri_choghadiya(jd, place) if gc==3]
def shubha_hora(jd, place):
    """
        Get end times of Shubha Hora for the given julian day
        hora is 1/12th of daytime or nighttime practiced as time measure in South India 
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [(hora_planet,start_time_string,end_time_string)...]
    """
    srise = sunrise(jd, place); sset = sunset(jd,place) # V4.8.5
    day_dur = (sset[0] - srise[0])/24
    end_times = []; start_time = srise[1]
    _vaara = vaara(jd,place)
    for i in range(1, 13):
        gt = srise[2]+(i*day_dur)/12; _,_,_,fh = utils.jd_to_gregorian(gt); end_time = utils.to_dms(fh)
        gc_type = const.shubha_hora_day_table[i-1][_vaara]
        end_times.append((gc_type,start_time,end_time))
        start_time = end_time
    
    # Night duration = time from today's sunset to tomorrow's sunrise
    srise = sunrise(jd+1,place); night_dur = (24+srise[0] - sset[0])/24
    for i in range(1, 13):
        gt = sset[2]+(i*night_dur)/12; _,_,_,fh = utils.jd_to_gregorian(gt); end_time = utils.to_dms(fh)
        gc_type = const.shubha_hora_night_table[i-1][_vaara]
        end_times.append((gc_type,start_time,end_time))
        start_time = end_time
    
    return end_times
def trikalam(jd, place, option='raahu kaalam'):
    """
        Get tri kaalam (Raahu kaalam, yama kandam and Kuligai Kaalam) for the given Julian day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param option: one of 'raahu kaalam', 'gulikai', 'yamagandam'. Default:'raahu kaalam' 
            Note: One can use separate lambda function for each of these options
        raahu_kaalam = lambda jd, place: trikalam(jd, place, 'raahu kaalam')
            yamaganda_kaalam = lambda jd, place: trikalam(jd, place, 'yamagandam')
            gulikai_kaalam = lambda jd, place: trikalam(jd, place, 'gulikai')
        @return: start and end time of requested tri column - as list e.g. [start_time, end_time]
    """
    srise = sunrise(jd, place)[0] # V4.3.0
    day_dur = day_length(jd, place)
    weekday = vaara(jd,place)
    
    # value in each array is for given weekday (0 = sunday, etc.)
    offsets = { 'raahu kaalam': [0.875, 0.125, 0.75, 0.5, 0.625, 0.375, 0.25],
                'gulikai': [0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0.0],
                'yamagandam': [0.5, 0.375, 0.25, 0.125, 0.0, 0.75, 0.625] }
    
    start_time = srise + day_dur * offsets[option][weekday]
    end_time = start_time + 0.125 * day_dur
    
    start_time = utils.to_dms(start_time)
    end_time = utils.to_dms(end_time)
    
    return [start_time, end_time] # decimal hours to H:M:S
raahu_kaalam = lambda jd, place: trikalam(jd, place, 'raahu kaalam')
yamaganda_kaalam = lambda jd, place: trikalam(jd, place, 'yamagandam')
gulikai_kaalam = lambda jd, place: trikalam(jd, place, 'gulikai')
def durmuhurtam(jd, place):
    """
    Get dhur muhurtham timing for the given julian day using true 1/15th muhurta divisions.
    @param jd: Julian Day Number of the date/time
    @param place: Place as struct ('Place',latitude,longitude,timezone)
    @return: start and end time of dhur muhurtham - as flat list [start1, end1, start2, end2]
    Note: this function was updated in V5.0
    """
    srise = sunrise(jd, place)[0]
    sset = sunset(jd, place)[0]
    day_dur = day_length(jd, place)
    night_dur = night_length(jd, place)
    weekday = vaara(jd, place)  # 0: Sun, 1: Mon, ..., 6: Sat

    # Traditional Dur Muhurtham Muhurta slot indices (0-indexed out of 15 parts)
    # Each entry represents [day_muhurta_index, night_muhurta_index]
    # None or -1 means no second/night segment.
    # Ref standard Muhurta rules:
    # Sun: 14th slot (index 13)
    # Mon: 9th & 12th slots (indices 8, 11)
    # Tue: 4th daytime slot (index 3) & a night slot
    # Wed: 8th slot (index 7)
    # Thu: 4th & 7th slots (indices 3, 6)
    # Fri: 2nd & 9th slots (indices 1, 8)
    # Sat: 1st slot starting right at sunrise (index 0, spans 2 muhurtas)
    
    slots = [
        [13, None],  # Sunday
        [8, 11],     # Monday
        [3, 4],      # Tuesday (night slot varies by custom, mapped to index 4 of night)
        [7, None],   # Wednesday
        [3, 6],      # Thursday
        [1, 8],      # Friday
        [0, None]    # Saturday (Spans 2 muhurtas from index 0)
    ]

    dur = [day_dur, day_dur]
    base = [srise, srise]
    
    # Handle Tuesday night segment baseline if applicable
    if weekday == 2:  
        dur[1] = night_dur
        base[1] = sset

    answer = []
    day_m_len = day_dur / 15.0
    night_m_len = night_dur / 15.0

    for i in range(0, 2):
        slot_idx = slots[weekday][i]
        if slot_idx is not None:
            m_len = day_m_len if i == 0 or weekday != 2 else night_m_len
            b_time = base[i]
            
            # Saturday is unique: it lasts for 2 consecutive muhurtas starting at index 0
            span_count = 2.0 if (weekday == 6 and i == 0) else 1.0

            start_time = b_time + slot_idx * day_m_len if i == 0 else b_time + slot_idx * night_m_len
            end_time = start_time + span_count * m_len

            start_time_dms = utils.to_dms(start_time)
            end_time_dms = utils.to_dms(end_time)
            answer += [start_time_dms, end_time_dms]

    return answer
def abhijit_muhurta(jd, place):
    """
        Get Abhijit muhurta timing for the given julian day
        Abhijit muhurta is the 8th muhurta (middle one) of the 15 muhurtas during the day_duration (~12 hours)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: start and end time of Abhijit muhurta - as list e.g. [start_time, end_time]
    """
    _, lat, lon, tz = place
    srise = sunrise(jd,place)[0]; sset = sunset(jd,place)[0] 
    day_dur = day_length(jd, place)
    
    start_time = srise + 7 / 15 * day_dur
    end_time = srise + 8 / 15 * day_dur
    start_time = utils.to_dms(start_time)
    end_time = utils.to_dms(end_time)
    # to local time
    return [start_time, end_time]
def _assign_planets_to_houses(planet_positions,bhava_houses,bhava_madhya_method=1):
    _bhava_houses = []#bhava_houses[:]
    for _bhava_house in bhava_houses:
        [_bhava_start,_bhava_mid,_bhava_end] = _bhava_house; planets_in_house = []
        if _bhava_end < _bhava_start: _bhava_end+=360
        for p,(h,long) in planet_positions:
            p_long = h*30+long
            if (p_long >= _bhava_start and p_long < _bhava_end) or \
                (p_long+360 >= _bhava_start and p_long+360 < _bhava_end):
                planets_in_house.append(p)
        if bhava_madhya_method==1 or bhava_madhya_method==5: # Rasi is based on bhava cusp or Equal Rasi method
            _bhava_houses.append([int(_bhava_mid/30),(_bhava_start,_bhava_mid,_bhava_end),planets_in_house])
        elif bhava_madhya_method==2: # Rasi is based on bhava start
            _bhava_houses.append([int(_bhava_start/30),(_bhava_start,_bhava_mid,_bhava_end),planets_in_house])
        elif bhava_madhya_method in [3,4]+list(const.western_house_systems.keys()): # Sripati / KP method / Western House System
            _bhava_houses.append([int(_bhava_start/30),(_bhava_start%360,_bhava_mid%360,_bhava_end%360),planets_in_house])
    return _bhava_houses
def dasavarga_from_long(longitude, divisional_chart_factor=1):
    """
        Calculates the dasavarga-sign in which given longitude falls
        @param longitude: longitude of the planet
        @param divisional_chart_factor: divisional chart index as below. 
          divisional_chart_factor = 1=> Rasi, 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: constellation,longitude within_raasi
            0 = Aries, 1 = Taurus, ..., 11 = Pisces
    """
    #if divisional_chart_factor not in const.division_chart_factors:
    #    raise ValueError("Wrong divisional_chart_factor",divisional_chart_factor,' Valid value:',const.division_chart_factors)
    one_pada = (360.0 / (12 * divisional_chart_factor))  # There are also 108 navamsas
    one_sign = 12.0 * one_pada    # = 40 degrees exactly
    signs_elapsed = longitude / one_sign
    fraction_left = signs_elapsed % 1
    constellation = int(fraction_left * 12)
    long_in_raasi = (longitude-(constellation*30)) % 30
    " if long_in_raasi 30 make it and zero and add a rasi"
    if int(long_in_raasi+const.one_arc_second) == 30:
        long_in_raasi = 0; constellation = (constellation+1)%12
    return constellation,long_in_raasi
navamsa_from_long = lambda longitude: dasavarga_from_long(longitude,9) 
def navamsa_from_long_old(longitude):
    """Calculates the navamsa-sign in which given longitude falls
    0 = Aries, 1 = Taurus, ..., 11 = Pisces
    """
    one_pada = (360 / (12 * 9))  # There are also 108 navamsas
    one_sign = 12 * one_pada    # = 40 degrees exactly
    signs_elapsed = longitude / one_sign
    fraction_left = signs_elapsed % 1
    return int(fraction_left * 12)
def declination_of_planets(jd,place):
    """
        return declination of planets
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: declination as a list
        first element for sun and last element for saturn
        
    """
    _ayanamsa = get_ayanamsa_value(jd, place)
    pp = dhasavarga(jd,place,divisional_chart_factor=1)[:7]
    bhujas = [0 for _ in const.SUN_TO_SATURN]
    north_south_sign = [1 for _ in const.SUN_TO_SATURN]
    for p,(h,long) in pp:
        p_long = utils.norm360(h*30 + long+_ayanamsa) #V5.0
        if p_long >= 0.0 and p_long < 180.0: # North
            north_south_sign[p] = -1
            if p in [const.SUN_ID, const.MARS_ID, const.JUPITER_ID, const.VENUS_ID]: # [0,2,4,5]:
                north_south_sign[p] = 1
        else: # South
            north_south_sign[p] = -1
            if p in [const.MOON_ID, const.SATURN_ID]: #[1,6]:
                north_south_sign[p] = 1
        bhujas[p] = p_long%360
        if p_long > 90.0 and p_long < 180.0:
            bhujas[p] = 180.0 - p_long
        elif p_long > 180.0 and p_long < 270.0:
            bhujas[p] = p_long - 180.0
        elif p_long > 270.0 and p_long < 360.0:
            bhujas[p] = 360.0 - p_long
        bhujas[p] = round(bhujas[p],2)
    north_south_sign[3] = 1
    bd = [0,362/60.0,703/60.0,1002/60.0,1238/60.0,1388/60.0,1440/60.0]
    bx = [i*15 for i in const.SUN_TO_SATURN]
    declinations = [0 for _ in const.SUN_TO_SATURN]
    for p in const.SUN_TO_SATURN:
        declinations[p] = north_south_sign[p] * utils.inverse_lagrange(bd, bx, bhujas[p])
    return declinations
_dhuma_longitude = lambda sun_long: (sun_long+133+20.0/60) % 360
def _vyatipaata_longitude(sun_long):
    dhuma = _dhuma_longitude(sun_long)
    return ((360.0 - dhuma) %360 if const.vyatipada_calculation_method == 1
            else (dhuma + 53 + 2.0 / 3.0)) % 360
_parivesha_longitude = lambda sun_long: (_vyatipaata_longitude(sun_long)+180.0) % 360
_indrachaapa_longitude = lambda sun_long: (360.0-_parivesha_longitude(sun_long))%360
_upaketu_longitude = lambda sun_long: (sun_long-30.0)%360
def solar_upagraha_longitudes(solar_longitude,upagraha, dhasa_progression_correction=0.0):
    """
        Get logitudes of solar based upagrahas
        ['dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu']
        @param jd: Jilian day number for the date/time
        @param upagraha: one of the values from ['dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu']
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [constellation,longitude]
    """
    if upagraha.lower() in const._solar_upagraha_list:
        import sys
        func_name = '_' + upagraha + "_longitude"
        long = getattr(sys.modules[__name__], func_name)(solar_longitude)
        constellation,coordinates = dasavarga_from_long(long+dhasa_progression_correction)
        return [constellation,coordinates]
kaala_longitude = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    upagraha_longitude(dob,tob,place,planet_index=const.SUN_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
mrityu_longitude = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    upagraha_longitude(dob,tob,place,planet_index=const.MARS_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
artha_praharaka_longitude = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    upagraha_longitude(dob,tob,place,planet_index=const.MERCURY_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
yama_ghantaka_longitude = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    upagraha_longitude(dob,tob,place,planet_index=const.JUPITER_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
gulika_longitude = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    upagraha_longitude(dob,tob,place,planet_index=const.SATURN_ID,upagraha_part='begin',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
maandi_longitude = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    upagraha_longitude(dob,tob,place,planet_index=const.SATURN_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
kaala_raw = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    _upagraha_longitude_full(dob,tob,place,planet_index=const.SUN_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
mrityu_raw = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    _upagraha_longitude_full(dob,tob,place,planet_index=const.MARS_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
artha_praharaka_raw = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    _upagraha_longitude_full(dob,tob,place,planet_index=const.MERCURY_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
yama_ghantaka_raw = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    _upagraha_longitude_full(dob,tob,place,planet_index=const.JUPITER_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
gulika_raw = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    _upagraha_longitude_full(dob,tob,place,planet_index=const.SATURN_ID,upagraha_part='begin',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
maandi_raw = (
    lambda dob,tob,place,dhasa_progression_correction=0.0:
    _upagraha_longitude_full(dob,tob,place,planet_index=const.SATURN_ID,upagraha_part='middle',
                       dhasa_progression_correction=dhasa_progression_correction)
    )
def upagraha_longitude(dob,tob,place,planet_index,upagraha_part='middle',dhasa_progression_correction=0.0):
    """
      get upagraha longitude from dob,tob, place-lat/long and day/night ruling planet's part
      @param dob Date of birth as Date(year,month,day)
      @param tob Time of birth as (hours,minutes,seconds)
      @param planet_index 0=Sun, 1=Moon, 2=Mars, 3=Mercury,4=Jupiter, 5=Venus, 6=Saturn
      @param upagraha_part = 'Middle' or 'Begin'
      Notes:
          Since Kaala is upagraha of Sun so planet_index should be 0
              Kaala rises at the middle of Sun’s part. In other words, we find the time at the
              middle of Sun’s part and find lagna rising then. That gives Kaala’s longitude.
          Since Mrityu is upagraha of Mars so planet_index should be 2
              Mrityu rises at the middle of Mars’s part.
          Since Artha Praharaka is upagraha of Mercury so planet_index should be 3
              Artha Praharaka rises at the middle of Mercury’s part.
          Since Kaala is upagraha of Jupiter so planet_index should be 4
              Yama Ghantaka rises at the middle of Jupiter’s part.
          Since Gulika is upagraha of Saturn so planet_index should be 6
              Gulika rises at the beginning of Saturn’s part.
          Since Maandi is upagraha of Saturn so planet_index should be 6
              Maandi rises at the middle of Saturn’s part.
          You can also use specific lambda functions.
              kaala_longitude(dob,tob,place,divisional_chart_factor)
              mrityu_longitude(dob,tob,place,divisional_chart_factor)
              artha_longitude(dob,tob,place,,divisional_chart_factor)
              yama_ghantaka_longitude(dob,tob,place,divisional_chart_factor)
              gulika_longitude(dob,tob,place,divisional_chart_factor)
              maandi_longitude(dob,tob,place,divisional_chart_factor)
      @return: [constellation of upagraha,upagraha_longitude within constellation]
    """
    """
        TODO: Upagraha longitudes are not matching with JHora for divisional charts
              Upagraha longitudes are based on sunrise times - how does sunrise time change in div charts?
    """
    upagraha_long = _upagraha_longitude_full(dob, tob, place, planet_index, upagraha_part, dhasa_progression_correction)
    constellation,coordinates = dasavarga_from_long(upagraha_long) #int(upagraha_long / 30)
    return [constellation,coordinates]
bhava_lagna = (
    lambda jd, place, dhasa_progression_correction=0.0,special_lagna_continuity=None:
        special_ascendant(
            jd,place,lagna_rate_factor=0.25, dhasa_progression_correction=dhasa_progression_correction,
            special_lagna_continuity=special_lagna_continuity)
        )
hora_lagna = (
    lambda jd,place,dhasa_progression_correction=0.0,special_lagna_continuity=None: 
        special_ascendant(jd,place,lagna_rate_factor=0.5,
                          dhasa_progression_correction=dhasa_progression_correction,
                          special_lagna_continuity=special_lagna_continuity)
        )
ghati_lagna = (
    lambda jd,place,dhasa_progression_correction=0.0,special_lagna_continuity=None: 
        special_ascendant(jd,place,lagna_rate_factor=1.25,
                          dhasa_progression_correction=dhasa_progression_correction,
                          special_lagna_continuity=special_lagna_continuity)
        ) 
vighati_lagna = (
    lambda jd,place,dhasa_progression_correction=0.0,special_lagna_continuity=None: 
        special_ascendant(jd,place,lagna_rate_factor=5.0,
                          dhasa_progression_correction=dhasa_progression_correction,
                          special_lagna_continuity=special_lagna_continuity)
        ) 
def special_ascendant(jd,place,lagna_rate_factor=1.0,dhasa_progression_correction=0.0,
                      special_lagna_continuity=None):
    """
        Get constellation and longitude of special lagnas (Bhava,Hora,Ghati,vighati)
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param lagna_rate_factor:    
            lagna_rate_factor   = 0.25 for Bhava Lagna
                                = 0.5 for Hora Lagna
                                = 1.25 for Ghati Lagna  
                                = 5.0 for vighati Lagna                          
        @param special_lagna_continuity: Set to True to use the alternative definition that ensures 
            mathematical continuity around sunrise.
        @return: [special lagnas constellation, special lagna's longitude within constellation]
        Note: You can also individual lambda function for each special lagna without lagna_rate_factor
        Example: 
            bhava_lagna(jd,place,divisional_chart_factor)
            hora_lagna(jd,place,divisional_chart_factor)
            ghati_lagna(jd,place,divisional_chart_factor)
            vighati_lagna(jd,place,divisional_chart_factor)
        NOTE: There are separate functions for pranapada, indu,sree, bhrigu_bindhu, kunda with same arguments
    """
    if special_lagna_continuity is None: special_lagna_continuity = const.special_lagna_continuity
    _,_,_, time_of_birth_in_hours = jd_to_gregorian(jd)
    srise = sunrise(jd, place) #V2.3.1 Get sunrise JD - as we need sun longitude at sunrise
    sun_rise_hours = srise[0]
    time_diff_mins = (time_of_birth_in_hours-sun_rise_hours)*60
    from jhora.horoscope.chart import charts
    """ 
        Change in V3.6.3
        We need Sun position at sunrise. So we use srise[2] returned from sunrise function.
        Since sunrise function returns JD Local at sunrise we add local time here because 
        charts will minus it to get UTC
    """
    jd_spl_lagna = jd if special_lagna_continuity else srise[2]+place.timezone/24
    pp = dhasavarga(jd_spl_lagna, place)
    sun_long = pp[const.SUN_ID][1][0]*30+pp[const.SUN_ID][1][1]
    spl_long = utils.norm360(sun_long + (time_diff_mins * lagna_rate_factor) + dhasa_progression_correction )
    da = dasavarga_from_long(spl_long)
    return da
def pranapada_lagna(
    jd,
    place,
    dhasa_progression_correction=0.0,
    special_lagna_continuity=None,
):
    """
    Calculate Pranapada Lagna.

    Classical rule:
        Convert time from sunrise to birth into vighatis.
        Divide by 15.
        Convert the result into signs and degrees.
        If Sun is in movable sign, add to Sun's longitude.
        If Sun is in fixed sign, add to 9th from Sun.
        If Sun is in dual sign, add to 5th from Sun.

    Implementation:
        The Vighati Lagna (special_ascendant with lagna_rate_factor 5.0) gives the Sun's longitude plus the time from sunrise to birth.
        The Sun's sign at the birth time then adds 0 (movable), 240 (fixed) or 120 (dual) degrees.

    Parameters
    ----------
    jd : float
        Julian day number of birth (local time).
    place : tuple / struct
        Place information: name, latitude, longitude, timezone.
    dhasa_progression_correction : float
        Degrees added to the longitude (progressed charts); 0.0 for none.
    special_lagna_continuity : bool
        True: the Sun's longitude used for the Vighati Lagna is that at the birth time, so the result is continuous across sunrise.
        False: the Sun's longitude is that at the sunrise of the date of jd.
        None: const.special_lagna_continuity.
        The Sun's sign for the movable / fixed / dual test is always that at the birth time.

    Returns
    -------
    tuple
        (constellation of Pranapada Lagna [0..11, 0 = Aries], longitude within the constellation).
    """
    jd_utc = jd - place.timezone/24.0
    _vighati_lagna = vighati_lagna(jd, place,dhasa_progression_correction,
                            special_lagna_continuity=special_lagna_continuity)
    _vighati_long = _vighati_lagna[0]*30 + _vighati_lagna[1]
    sun_long = solar_longitude(jd_utc, place)
    sun_sign, _ = dasavarga_from_long(sun_long)
    # Movable: add directly.
    # Fixed: add 9th from Sun = +240 degrees.
    # Dual: add 5th from Sun = +120 degrees.
    if sun_sign in const.fixed_signs:
        offset = 240.0
    elif sun_sign in const.dual_signs:
        offset = 120.0
    else:
        offset = 0.0
    pranapada_longitude = utils.norm360(_vighati_long + offset + dhasa_progression_correction)
    da = dasavarga_from_long(pranapada_longitude)
    return da
def indu_lagna(jd,place,dhasa_progression_correction=0.0):  # BV Raman Method
    """
        Get constellation and longitude of indu lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @return: [indu lagnas constellation, indu lagna's longitude within constellation]
    """
    il_factors = [30,16,6,8,10,12,1] # Sun to Saturn. Rahu/Ketu exempted
    jd_utc = jd - place.timezone/24.0
    moon_long_full = lunar_longitude(jd_utc, place)
    moon_house,moon_long = dasavarga_from_long(moon_long_full)
    asc = ascendant(jd, place)
    asc_house = asc[0]
    ninth_lord = const._house_owners_list[(asc_house+const.HOUSE_9)%12]
    ninth_lord_from_moon = const._house_owners_list[(moon_house+const.HOUSE_9)%12]
    il1 = (il_factors[ninth_lord]+il_factors[ninth_lord_from_moon])%12
    if il1==0: il1 = 12
    _indu_rasi = (moon_house+il1-1)%12
    return _indu_rasi,moon_long
def kunda_lagna(jd,place,dhasa_progression_correction=0.0):
    """
        Get constellation and longitude of kunda lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @return: [kunda lagnas constellation, kunda lagna's longitude within constellation]
    """
    asc = ascendant(jd, place)
    al = asc[0]*30+asc[1]; al1 = utils.norm360(al*81+dhasa_progression_correction)
    spl = dasavarga_from_long(al1)
    return spl
def bhrigu_bindhu_lagna(jd,place,dhasa_progression_correction=0.0):
    """
        Get constellation and longitude of bhrigu bindhu lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @return: [bhrigu bindhu lagnas constellation, bhrigu bindhu lagna's longitude within constellation]
    """
    jd_utc = jd - place.timezone/24.0
    moon_long_full = lunar_longitude(jd_utc, place)
    rahu_long_full = sidereal_longitude(jd_utc, const._RAHU, place)
    moon_add = 0 if moon_long_full > rahu_long_full else 360
    bb = utils.norm360(0.5*(rahu_long_full+moon_long_full+moon_add)+dhasa_progression_correction)
    return dasavarga_from_long(bb)
def sree_lagna(jd,place,dhasa_progression_correction=0.0):
    """
        Get constellation and longitude of Sree Lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @return: [Sree lagna constellation, Sree lagna's longitude within constellation]
    """
    jd_utc = jd - place.timezone/24.0
    moon_long = lunar_longitude(jd_utc, place)
    asc = ascendant(jd, place)
    asc_long = asc[0]*30+asc[1]
    sl = sree_lagna_from_moon_asc_longitudes(moon_long, asc_long)
    return sl
def sree_lagna_from_moon_asc_longitudes(moon_longitude,ascendant_longitude):
    moon_long = moon_longitude
    asc_long = ascendant_longitude
    reminder = nakshatra_pada(moon_long)[2]
    reminder_fraction = reminder * 27
    sree_long = asc_long + reminder_fraction
    constellation,coordinates = dasavarga_from_long(sree_long)
    return constellation,coordinates
def tamil_solar_month_and_date_V4_3_8(panchanga_date,place):
    """
        Returns tamil month and date (e.g. Aadi 28 )
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: tamil_month_number, tamil_date_number
        i.e. [0..11, 1..32]
        Note: Tamil month is sankranti based solar month - not lunar month
    """ 
    start_jd = utils.gregorian_to_jd(panchanga_date)
    sl = solar_longitude(start_jd, place)
    _tamil_month = int(sl/30)
    sunset_count=1
    while True:
        if sl%30<1 and sl%30>0:
            break
        start_jd -= 1
        sl = solar_longitude(start_jd, place)
        sunset_count+=1
    _tamil_day = sunset_count
    return _tamil_month, _tamil_day
def tamil_solar_month_and_date_V4_3_5(panchanga_date,place): # _V4_3_5
    """
        Returns tamil month and date (e.g. Aadi 28 )
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: tamil_month_number, tamil_date_number
        i.e. [0..11, 1..32]
        Note: Tamil month is sankranti based solar month - not lunar month
        And it is very sensitive to solar longitude. 
    """ 
    jd = utils.gregorian_to_jd(panchanga_date)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd, place)
    _tamil_month = int(sl/30)
    daycount=1
    while True:
        if sl%30<1 and sl%30>0:
            break
        sunset_jd -= 1
        sl = solar_longitude(sunset_jd, place)
        daycount+=1
    _tamil_day = daycount
    return _tamil_month, _tamil_day#, month_days
def tamil_solar_month_and_date_RaviAnnnaswamy(panchanga_date,place): #_RaviAnnnaswamy V4.4.0
    jd = utils.julian_day_number(panchanga_date, (10,0,0))
    jd_set = sunset(jd, place)[2]
    jd_utc = jd_set - place.timezone/24
    sr = solar_longitude(jd_utc, place)
    tamil_month = int(sr/30)
    daycount=1
    while True:
        if sr%30<1 and sr%30>0:
            break
        jd_utc -= 1
        sr = solar_longitude(jd_utc, place)
        daycount+=1
    return tamil_month, daycount
def tamil_solar_month_and_date(panchanga_date, place, tamil_month_method=None, base_time=0, use_utc=True,
                                sankranti_rule=None, ghatikas=None):
    """
        Returns tamil month and date (e.g. Aadi 28 )
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param base_time: 0 => sunset time, 1 => sunrise time 2 => midday time
        @param use_utc: True (default) use universal time
        @param sankranti_rule one of - for solar calendar type only
            const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE = 1 
                (Default: Sankranti day if sun enters zodiac before sunset)
            const.SANKRANTI_RULE.BEFORE_GHATIKAS = 2 (Sankranti day before prescribed ghatikas)
                    ghatikas = 13 => Tamil Calendar
                    ghatikas = 18 => Malabar calendar
                    ghatikas = 30 => Bengal Calendar
                    ghatikas = 45 => Kerala Calendar
            const.SANKRANTI_RULE.SUNRISE_TO_SUNRISE = 3 
                (Sankranti day if sun enters within sunrise to sunrise)
        @return: tamil_month_number, tamil_date_number
        i.e. [0..11, 1..32]
        Note: Tamil month is sankranti based solar month - not lunar month
        And it is very sensitive to solar longitude.
    """
    if sankranti_rule is not None:
        jd = utils.julian_day_number(panchanga_date, (10, 0, 0))
        return solar_month_date(jd, place, sankranti_rule, ghatikas)
    if tamil_month_method is None: tamil_month_method = const.tamil_month_method
    if tamil_month_method==const.TAMIL_MONTH_METHOD.BASED_ON_LOCAL_10AM: # sunset and UTC
        return tamil_solar_month_and_date_RaviAnnnaswamy(panchanga_date, place)
    elif tamil_month_method==const.TAMIL_MONTH_METHOD.BASED_ON_SUNSET_TIME: # sunset jd as starting jd
        return tamil_solar_month_and_date_V4_3_5(panchanga_date, place)
    elif tamil_month_method==const.TAMIL_MONTH_METHOD.BASED_ON_BIRTH_TIME: # startjd at 10AM
        return tamil_solar_month_and_date_V4_3_8(panchanga_date, place)
    else: ### V5.0 fix
        jd = utils.julian_day_number(panchanga_date, (0, 0, 0))
        return solar_month_date(jd,place,sankranti_rule,ghatikas)
def tamil_solar_month_and_date_new(panchanga_date,place,base_time=0,use_utc=True): # V4.4.0
    """
        @param base_time: 0 => sunset time, 1 => sunrise time 2 => midday time
        @param use_utc: True (default) use uninversal time
    """
    jd = utils.julian_day_number(panchanga_date, (10,0,0))
    jd_base = sunset(jd, place)[2] if base_time==0 else (sunrise(jd,place)[2] if base_time==1 else midday(jd, place)[1])
    jd_utc = jd_base - place.timezone/24 if use_utc else jd_base
    sr = solar_longitude(jd_utc, place)
    tamil_month = int(sr/30)
    daycount=1
    while True:
        if sr%30<1 and sr%30>0:
            break
        jd -= 1
        jd_base = sunset(jd, place)[2] if base_time==0 else (sunrise(jd,place)[2] if base_time==1 else midday(jd, place)[1])
        jd_utc = jd_base - place.timezone/24 if use_utc else jd_base
        sr = solar_longitude(jd_utc, place)
        daycount+=1
    return tamil_month, daycount
def tamil_solar_month_and_date_from_jd(jd,place):
    return solar_month_date(jd, place, sankranti_rule=const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE)

def days_in_tamil_month(panchanga_date, place, sankranti_rule=None, ghatikas=None):
    """
        get # of days in that tamil month
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param sankranti_rule, ghatikas: same as previous_sankranti_date() / next_sankranti_date(); determines which civil day a sankranti is
            attributed to. Defaults to const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE
        @return: number of civil days from the previous sankranti date to the next one
        Note: updated in V5.0
    """
    jd = utils.gregorian_to_jd(panchanga_date)

    _, tamil_day = tamil_solar_month_and_date(panchanga_date, place)

    # Civil date on which the current Tamil month started
    month_start_jd = jd - (tamil_day - 1)

    # Search from the following civil day so that a sankranti on
    # month_start_jd itself cannot be returned again
    y, m, d, _ = utils.jd_to_gregorian(month_start_jd + 1)
    search_date = Date(y, m, d)

    next_date = next_sankranti_date(
        search_date, place, sankranti_rule, ghatikas
    )[0]

    return int(
        utils.gregorian_to_jd(next_date) - month_start_jd
    )

def _previous_sankranti_date_new(panchanga_date,place,zodiac=None):
    prev_day = utils.previous_panchanga_day(panchanga_date, minus_days=1)
    if zodiac is None:
        t_month,_ = tamil_solar_month_and_date(prev_day, place)
        multiple = t_month * 30
    else:
        multiple = zodiac * 30
    #print(prev_day,t_month,t_day)
    jd = utils.gregorian_to_jd(prev_day)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd, place)
    while True:
        slq,slr = divmod(sl,30)
        if slr<1 and slr>0 and zodiac is None:
            break
        if slr<1 and slr>0 and zodiac is not None and int(slq)==int(zodiac):
            break
        sunset_jd -= 1
        sl = solar_longitude(sunset_jd, place)
    sank_date = jd_to_gregorian(sunset_jd)
    sank_sunrise = sunrise(sunset_jd,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    tamil_month,tamil_day = tamil_solar_month_and_date(sank_date, place)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    solar_longs = [ solar_longitude(sank_sunrise + t, place) % 360 for t in offsets ]
    solar_hour = utils.inverse_lagrange(offsets, solar_longs, multiple % 360) # Do not move % 360 above
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24 ## V5.0 Removed place.timeone addition
    return sank_date, solar_hour1,tamil_month,tamil_day
def previous_sankranti_date(panchanga_date, place, sankranti_rule=None, ghatikas=None):
    """
        Get the previous sankranti date (sun entry to a raasi)
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param sankranti_rule, ghatikas: same as solar_month_date()/vedic_date() --
            determines which civil (sunrise-to-sunrise) day the sankranti is
            attributed to. Defaults to const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE
        @return: sankranti_date as Struct(y,m,d), sankranti time as float hours,tamil_month_number, tamil_date_number
    """
    jd = utils.julian_day_number(panchanga_date, (0, 0, 0))
    transit_jd, transit_long = previous_planet_entry_date(const.SUN_ID, jd, place)
    civil_sr_jd = _civil_start_sunrise_for_transit(transit_jd, place, sankranti_rule, ghatikas)
    y, m, d, _ = utils.jd_to_gregorian(civil_sr_jd)
    sank_date = Date(y, m, d)
    tamil_month = int(round(transit_long / 30)) % 12
    tamil_day = 1
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (transit_jd - sank_jd_utc) * 24 ## V5.0 Removed place.timeone addition
    return sank_date, solar_hour1, tamil_month, tamil_day
def next_sankranti_date(panchanga_date, place, sankranti_rule=None, ghatikas=None):
    """
        Get the next sankranti date (sun entry to a raasi)
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param sankranti_rule, ghatikas: same as solar_month_date()/vedic_date() --
            determines which civil (sunrise-to-sunrise) day the sankranti is
            attributed to. Defaults to const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE
        @return: sankranti_date as Struct(y,m,d), sankranti time as float hours,tamil_month_number, tamil_date_number
        NOTE: Sankranti date is the actual civil day for sankranti
              Sankranti time if negative, e.g. -3.0 means Sun entered the rasi yesterday
                i.e. Sankranti time is (24-3= 21:00 PM previous day, still sankranti is today)
    """
    jd = utils.julian_day_number(panchanga_date, (0, 0, 0))
    transit_jd, transit_long = next_planet_entry_date(const.SUN_ID, jd, place, direction=1)
    civil_sr_jd = _civil_start_sunrise_for_transit(transit_jd, place, sankranti_rule, ghatikas)
    y, m, d, _ = utils.jd_to_gregorian(civil_sr_jd)
    sank_date = Date(y, m, d)
    tamil_month = int(round(transit_long / 30)) % 12
    tamil_day = 1
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (transit_jd - sank_jd_utc) * 24 ## V5.0 Removed place.timeone addition
    return sank_date, solar_hour1, tamil_month, tamil_day
def next_sankranti_date_from_jd(jd,place, direction=1, increment_days=0.01, precision=0.1, raasi=None):
    """ Returns next sankranti date (y,m,d,fh) and sankranti_zodiac/raasi. Does not return tamil day """
    npe = next_planet_entry_date(const.SUN_ID, jd, place, direction=direction, increment_days=increment_days,
                                  precision=precision, raasi=raasi)
    return utils.jd_to_gregorian(npe[0]),int(npe[1]//30),1 # On Sankranti day is always 1
def previous_sankranti_date_from_jd(jd,place, increment_days=0.01, precision=0.1, raasi=None):
    """ Returns previous sankranti date (y,m,d,fh) and sankranti_zodiac/raasi. Does not return tamil day """
    ppe = previous_planet_entry_date(const.SUN_ID, jd, place, increment_days=increment_days,precision=precision, raasi=raasi)
    return utils.jd_to_gregorian(ppe[0]),int(ppe[1]//30),1 # On Sankranti day is always 1
def next_solar_date(
    jd_at_dob,
    place,
    years=1,
    months=1,
    sixty_hours=1,
    sookshma=1,
    prana=1,
    dehantar=1,
    use_sidereal=False,
):
    """
    Returns the next date at which the Sun's longitude equals its longitude at jd_at_dob,
    shifted by Varsha/Tajaka subdivisions (years → months → sixty_hours → sookshma → prana → dehantar).

    Parameters
    ----------
    jd_at_dob : float
        Julian Day at time of birth.
    place : tuple
        Place Struct ('place', latitude, longitude, timezone) used by downstream functions.
    years : int, default 1
        Varsha index (1 = birth year).
    months : int, default 1
        Antar index within the year (1..12).
    sixty_hours : int, default 1
        Pratyantar index within the month (1..12); each step ≈ 2.5° ≈ ~60h.
    sookshma : int, default 1
        Sookshma index within the pratyantar (1..12).
    prana : int, default 1
        Prana index within the sookshma (1..12).
    dehantar : int, default 1
        Dehantar index within the prana (1..12).
    use_sidereal : bool, default False
        If True, use const.sidereal_year; else const.tropical_year.

    Returns
    -------
    float
        Julian Day for the matching solar date.
    """
    # Fast-path: if everything is the first sub-period, return DOB JD.
    if (years == 1 and months == 1 and sixty_hours == 1
        and sookshma == 1 and prana == 1 and dehantar == 1):
        return jd_at_dob
    # Ordered 12-fold denominators for each level (year:1, month:12, …)
    denominators = [
        ("years",        1,        years),
        ("months",       12,       months),
        ("sixty_hours",  12**2,    sixty_hours),
        ("sookshma",     12**3,    sookshma),
        ("prana",        12**4,    prana),
        ("dehantar",     12**5,    dehantar),
    ]
    # Compute cumulative fraction of the year from birth
    frac_of_year = 0.0
    for _, denom, idx in denominators:
        # Each index is 1-based; index==1 means "no additional offset" at that level.
        frac_of_year += (int(idx) - 1) / float(denom)
    # Sun's natal longitude (absolute in degrees 0..360)
    sun_long_at_dob = dhasavarga(jd_at_dob, place, divisional_chart_factor=1)[0][1]
    sun_long_at_dob = sun_long_at_dob[0] * 30.0 + sun_long_at_dob[1]
    # Target longitude and time guess
    sun_long_next = (sun_long_at_dob + 360.0 * frac_of_year) % 360.0
    year_len = const.sidereal_year if use_sidereal else const.tropical_year
    jd_next_guess = jd_at_dob + year_len * frac_of_year
    return __next_solar_jd(jd_next_guess, place, sun_long_next)
def next_annual_solar_date_approximate(dob,tob,years):
    week_days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    tobh = (tob[0]+tob[1]/60+tob[2]/3600)/24
    jd_at_dob = utils.julian_day_number(dob,tob)
    weekday_of_dob = ceil(jd_at_dob % 7)
    acsp = {k:d+(h+m/60+s/3600)/24 for k,(d,h,m,s) in const.annual_chart_solar_positions.items() }
    d = sum(acsp[x] for x in [int(y)*(10**(len(str(years-1))-i-1)) for i,y in enumerate(str(years-1))])
    dy,dh = (int(d),d%1)
    weekday_increment = int(weekday_of_dob+dy)%7
    bday = date(dob[0]+years-1,dob[1],dob[2])
    bwd = (bday.weekday()+1)%7
    #print('find nearest',week_days[weekday_increment],'to',bwd)
    bday1 = timedelta( (weekday_increment-bwd) % 7 )
    bday0 = -timedelta( (bwd-weekday_increment) % 7 )
    dday = bday+min(bday0,bday1)
    #print(bday0,bday,bday1,dday)
    nd, nh = (int(tobh + dh),(tobh+dh)%1*24)
    dday += timedelta(days=nd)
    #print(dday,utils.to_dms(nh))
    next_jd = utils.julian_day_number((dday.year,dday.month,dday.day), utils.to_dms(nh,as_string=False))
    return next_jd
def _birthtime_rectification_nakshathra_suddhi(jd,place):
    """
        !!!!!! EXPERIMENTAL WORK - RESULTS MAY NOT BE ACCURATE !!!!
        Calculates expected birth star and if it does not match with actual,
        iteratively reduce/time birth time to see if matches with actual birth star
        If Successful - returns revised birth time as a tuple
            otherwise returns False and possible closest star for the time
    """
    step_minutes = const.birth_rectification_step_minutes; loop_count = const.birth_rectification_loop_count
    adjust_minutes = 0
    nak = nakshatra(jd, place)[0]
    def _get_estimated_nakshatra(jd,place):
        ud = utils.udhayadhi_nazhikai(jd, place)
        ud1n = int(round(ud[1]*60)*4//9); ud1d = int(ud[1]*4%9)
        #print(round(ud[1]*60),'The mixed number of {}/{} is {} and {}/{}'.format(round(ud[1]*60*4),9,ud1n, ud1d, 9))
        ud2 = [int(ud1d+n*9)%27+1 for n in range(3)]
        #print(ud2)
        rectification_required = not (nak in ud2); nak_close = nak
        if rectification_required:
            nak_close = utils.closest_element_from_list(ud2,nak)
            #print('Expected Star',nak,'Actual Star',nak_close,ud1d,'rectification_required',rectification_required)
        return [rectification_required, nak_close]
    [rectification_required, nak_close] = _get_estimated_nakshatra(jd, place)
    if not rectification_required:
        return adjust_minutes
    else:
        l = 0;
        while l < loop_count:
            l += 1
            adjust_minutes = l*step_minutes
            jd1 = jd + adjust_minutes/1440.0
            [rectification_required, nak_close] = _get_estimated_nakshatra(jd1, place)
            _,_,_,fh = utils.jd_to_gregorian(jd1)
            if not rectification_required:
                #print('loop',l,'CONVERGED',adjust_minutes,fh)
                revised_birth_time = tuple(utils.to_dms(fh, as_string=False))
                return revised_birth_time
            adjust_minutes = -l*step_minutes
            jd1 = jd + adjust_minutes/1440.0
            [rectification_required, nak_close] = _get_estimated_nakshatra(jd1, place)
            _,_,_,fh = utils.jd_to_gregorian(jd1)
            if not rectification_required:
                #print('loop',l,'CONVERGED',adjust_minutes,fh)
                revised_birth_time = tuple(utils.to_dms(fh, as_string=False))
                return revised_birth_time
    print('Could not rectify birth time beyond',int(step_minutes*loop_count),'minutes')
    return [rectification_required, nak_close]
def _birthtime_rectification_lagna_suddhi(jd,place):
    """
        !!!!!! EXPERIMENTAL WORK - RESULTS MAY NOT BE ACCURATE !!!!
        Checks if lagna is [1,5,7,9] from Moon or Maandi in Raasi and Navamsa
        Returns True (if rectification is required) False if no rectification is required
    """
    from jhora.horoscope.chart import charts,house
    y,m,h,fh = utils.jd_to_gregorian(jd); dob = Date(y,m,h); tob = tuple(utils.to_dms(fh, as_string=False))
    #print(dob,tob)
    ppr = charts.rasi_chart(jd, place); ppn = charts.divisional_chart(jd, place, divisional_chart_factor=9)
    lagna = ppr[0][1][0]; moon = ppr[2][1][0]
    maandi = maandi_longitude(dob,tob,place)[0]
    if house.get_relative_house_of_planet(lagna,moon) in [1,5,7,9]: return False
    #print('lagna not in [1,5,7,9] from moon',lagna,moon)
    if house.get_relative_house_of_planet(lagna,maandi) in [1,5,7,9]: return False
    #print('lagna not in [1,5,7,9] from Maandi',lagna,maandi)
    lagna = ppn[0][1][0]; moon = ppn[2][1][0]
    maandi = maandi_longitude(dob,tob,place, divisional_chart_factor=9)[0]
    if house.get_relative_house_of_planet(lagna,moon) in [1,5,7,9]: return False
    #print('Navamsa lagna not in [1,5,7,9] from moon',lagna,moon)
    if house.get_relative_house_of_planet(lagna,maandi) in [1,5,7,9]: return False
    #print('Navamsa lagna not in [1,5,7,9] from Maandi',lagna,maandi)
    return True
def _birthtime_rectification_janma_suddhi(jd,place,gender=None):
    """
        Convert Ishtakaal Ghatikas to Phala (* 60)
        Divide by 225; If the reminder is:
        0 - 15 - Male /  16 - 45 - Female / 46 - 90 - Male / 91 - 150 - Female / 151 - 224 - Male
        Will check if actual gender does not matche with above calculation and return True/False 
        False => birthtime rectification is NOT required based on gender match
        True => birthtime rectification IS required based on gender match
    """
    if gender is None: gender = const.gender_default
    ud = utils.udhayadhi_nazhikai(jd, place)
    ud1n = int(round(ud[1]*60)//225); ud1d = int(ud[1]*60%225)
    #print(round(ud[1]*60),'The mixed number of {}/{} is {} and {}/{}'.format(round(ud[1]*60),225,ud1n, ud1d, 225))
    janma_suddhi_dict = {0:[(0,15),(46,90),(151,224)],1:[(16,45),(91,150)]}
    jsc = not any([(ud1d > js_pair[0] and ud1d < js_pair[1]) for js_pair in janma_suddhi_dict[gender]])
    return jsc
def __next_conjunction_of_planet_pair(jd,panchanga_place:Place,p1,p2,direction=1,separation_angle=0,
                                      finer_tolerance=None):
    if finer_tolerance is None: finer_tolerance = const.minimum_separation_longitude
    p1_key = ephemeris_planet_index(p1)
    p2_key = ephemeris_planet_index(p2)
    divisional_chart_factor = 1
    start_jd = jd
    cur_jd = start_jd - 1*direction
    end_jd = start_jd + 1*direction
    while cur_jd*direction < end_jd*direction:
        cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
        if p1==const.KETU_ID:
            p1_long = (ketu(sidereal_longitude(cur_jd_utc, const._RAHU, panchanga_place)))
        elif p1==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p1_long = (sla[0]*30+sla[1])*divisional_chart_factor%360
        else:
            p1_long = (sidereal_longitude(cur_jd_utc, p1_key, panchanga_place))
        if p2==const.KETU_ID:
            p2_long = (ketu(sidereal_longitude(cur_jd_utc, const._RAHU, panchanga_place)))
        elif p2==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p2_long = (sla[0]*30+sla[1])*divisional_chart_factor%360
        else:
            p2_long = (sidereal_longitude(cur_jd_utc, p2_key, panchanga_place))
        p_long_diff = direction*(p1_long-p2_long)
        long_diff = (p_long_diff - separation_angle)%360
        if abs(long_diff) < const.minimum_separation_longitude:
            #print('Found closest time:',utils.jd_to_gregorian(cur_jd))
            return cur_jd,utils.norm360(p1_long),utils.norm360(p2_long)
        cur_jd += const.conjunction_increment*direction
    return None
def next_conjunction_of_planet_pair(jd,panchanga_place:Place,p1,p2,direction=1,separation_angle=0,
                                    increment_speed_factor=0.25,angle_tolerance=0.5,finer_angle_tolerance=0.001):
    """
        get the date when conjunction of given two planets occur
        @param p1: planet1 index (0=Sun..8=Kethu)
        @param p2: planet2 index (0=Sun..8=Kethu)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param panchanga_start_date: Date struct (y,m,d)
        @param direction: 1= next conjunction -1 previous conjunction
        @param separation_angle - angle by which the planets to each other
        @return: Julian day of conjunction   
    """
    if (p1==const.RAHU_ID and p2==const.KETU_ID) or (p1==const.KETU_ID and p2==const.RAHU_ID):
        warnings.warn("Rahu and Ketu do not conjoin ever. Program returns error")
        return None
    """         # swap planets Dont ask me Why I do this But it helps """
    if p1 in [const.RAHU_ID,const.KETU_ID]: tmp = p2; p2 = p1; p1 =tmp
    if p2 == const._ascendant_symbol and direction == -1: tmp = p1; p1 = p2; p2 =tmp
    if p2 in [const.RAHU_ID,const.KETU_ID] and p1 != const._ascendant_symbol: increment_speed_factor=0.01
    if finer_angle_tolerance is None: finer_angle_tolerance = const.minimum_separation_longitude
    p1_key = ephemeris_planet_index(p1)
    p2_key = ephemeris_planet_index(p2)
    asc_speed = ascendant_speed(jd, panchanga_place)
    _planet_speeds = [asc_speed]+[abs(psi[3]) for p,psi in planets_speed_info(jd, panchanga_place).items()]
    p1_speed = _planet_speeds[0] if p1=='L' else _planet_speeds[p1+1]
    p2_speed = _planet_speeds[0] if p2=='L' else _planet_speeds[p2+1]
    increment_days = increment_speed_factor/p1_speed if p1_speed > p2_speed else increment_speed_factor/p2_speed
    increment_days *= direction
    _DEBUG_ = False
    #increment_days=1.0/24.0/60.0*direction if p1 in ['L'] or p2 in ['L'] else 1*direction
    long_diff_check = angle_tolerance# if p1 in ['L'] or p2 in ['L'] else 1.0
    max_days_to_search = 1000000
    cur_jd = jd# utils.julian_day_number(panchanga_start_date, (0,0,0))
    cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
    search_counter = 1
    while search_counter < max_days_to_search:
        cur_jd += increment_days
        cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
        if p1==const.KETU_ID:
            p1_long = (ketu(sidereal_longitude(cur_jd_utc, const._RAHU, panchanga_place)))
        elif p1==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p1_long = (sla[0]*30+sla[1])
        else:
            p1_long = (sidereal_longitude(cur_jd_utc, p1_key, panchanga_place))
        if p2==const.KETU_ID:
            p2_long = (ketu(sidereal_longitude(cur_jd_utc, const._RAHU, panchanga_place)))
        elif p2==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p2_long = (sla[0]*30+sla[1])
        else:
            p2_long = (sidereal_longitude(cur_jd_utc, p2_key, panchanga_place))
        p_long_diff = direction*(p1_long-p2_long)
        long_diff = (360+p_long_diff - separation_angle)%360
        if _DEBUG_: print(search_counter,p1,p1_key,p1_long,p2,p2_key,p2_long,long_diff,long_diff_check,utils.jd_to_gregorian(cur_jd))
        if long_diff<long_diff_check:
            if _DEBUG_: print(long_diff,'<',long_diff_check)
            #ret = __next_conjunction_of_planet_pair(p1,p2,panchanga_place,cur_jd,direction,separation_angle)
            jd_list = [cur_jd+t*increment_days for t in range(-10,10)]
            long_diff_list = []
            for jdt in jd_list:
                if p1==const.KETU_ID:
                    p1_long = (ketu(sidereal_longitude(jdt-panchanga_place.timezone/24, const._RAHU, panchanga_place)))
                elif p1==const._ascendant_symbol:
                    sla = ascendant(jdt, panchanga_place); p1_long = (sla[0]*30+sla[1])
                else:
                    p1_long = (sidereal_longitude(jdt-panchanga_place.timezone/24, p1_key, panchanga_place))
                if p2==const.KETU_ID:
                    p2_long = (ketu(sidereal_longitude(jdt-panchanga_place.timezone/24, const._RAHU, panchanga_place)))
                elif p2==const._ascendant_symbol:
                    sla = ascendant(jdt, panchanga_place); p2_long = (sla[0]*30+sla[1])
                else:
                    p2_long = (sidereal_longitude(jdt-panchanga_place.timezone/24, p2_key, panchanga_place))
                p_long_diff = direction * (p1_long-p2_long)
                long_diff = (360+p_long_diff-separation_angle)%360
                long_diff_list.append(long_diff)
            """ TODO: For separation Angle > 180 Lagrange may not work """
            try:
                if _DEBUG_: print('Lagrange method of fine tuning')
                if _DEBUG_: print(jd_list,'\n',long_diff_list)
                conj_jd = utils.inverse_lagrange(jd_list, long_diff_list, 0.0)
                if p1==const.KETU_ID:
                    p1_long = (ketu(sidereal_longitude(conj_jd-panchanga_place.timezone/24, const._RAHU, panchanga_place)))
                elif p1==const._ascendant_symbol:
                    sla = ascendant(conj_jd, panchanga_place); p1_long = (sla[0]*30+sla[1])
                else:
                    p1_long = (sidereal_longitude(conj_jd-panchanga_place.timezone/24, p1_key, panchanga_place))
                if p2==const.KETU_ID:
                    p2_long = (ketu(sidereal_longitude(conj_jd-panchanga_place.timezone/24, const._RAHU, panchanga_place)))
                elif p2==const._ascendant_symbol:
                    sla = ascendant(conj_jd, panchanga_place); p2_long = (sla[0]*30+sla[1])
                else:
                    p2_long = (sidereal_longitude(conj_jd-panchanga_place.timezone/24, p2_key, panchanga_place))
                if conj_jd is not None:
                    if _DEBUG_: print(p1,p2,utils.jd_to_gregorian(conj_jd),p1_long,p2_long)
                    return conj_jd, p1_long, p2_long
            except:
                if _DEBUG_: print('Normal method of fine tuning - since Lagrange failed')
                if _DEBUG_: print(search_counter,p1,p1_long,p2,p2_long,long_diff,long_diff_check,utils.jd_to_gregorian(cur_jd))
                ret = __next_conjunction_of_planet_pair(cur_jd,panchanga_place,p1,p2,direction,separation_angle,
                                                        finer_tolerance=finer_angle_tolerance)
                if ret is not None:
                    return ret
                
        search_counter += 1
    print('Could not find planetary conjunctions for sep angle',separation_angle,' Try increasing search range')
    return None
def previous_conjunction_of_planet_pair(jd,panchanga_place:Place,p1,p2,separation_angle=0,increment_speed_factor=0.25):
    return next_conjunction_of_planet_pair(jd, panchanga_place, p1, p2, direction=-1, separation_angle=separation_angle,
                                           increment_speed_factor=increment_speed_factor)
def previous_planet_entry_date(planet,jd,place,increment_days=0.01,precision=0.1,raasi=None):
    return next_planet_entry_date(planet,jd,place,direction=-1,increment_days=increment_days,precision=precision,raasi=raasi)
def previous_ascendant_entry_date(jd,place,precision=0.1,raasi=None,divisional_chart_factor=1):
    return next_ascendant_entry_date(jd, place, direction=-1, precision=precision, raasi=raasi,divisional_chart_factor=divisional_chart_factor)
def next_ascendant_entry_date(jd, place, direction=1, precision=0.01, raasi=None, divisional_chart_factor=1):
    """
    Optimized drop-in replacement using Bisection followed by Exact Linear Interpolation.
    Yields 0.0s execution time with mathematically perfect sub-arcsecond accuracy.
    """
    _DEBUG_ = False
    
    # 1. Calculate starting longitude
    sla = ascendant(jd, place)
    sl = (sla[0] * 30 + sla[1]) * divisional_chart_factor % 360
    
    # 2. Determine target boundary
    if raasi is None:
        multiple = (((sl // 30) + 1) % 12) * 30
        if direction == -1: 
            multiple = ((sl // 30) % 12) * 30
    else: 
        multiple = (raasi - 1) * 30 if raasi > 0 else 0

    target_long = multiple

    def get_diff(t):
        sla_t = ascendant(t, place)
        sl_t = (sla_t[0] * 30 + sla_t[1]) * divisional_chart_factor % 360
        diff = (sl_t - target_long) % 360
        if diff > 180: 
            diff -= 360
        return diff

    # 3. Dynamic Step Size for Bracketing (~1 hour steps)
    step_days = (1.0 / 24.0) / divisional_chart_factor * direction

    t0 = jd
    diff0 = get_diff(t0)

    if abs(diff0) < 0.0001:
        t0 += (1.0 / 24.0 / 60.0 / divisional_chart_factor) * direction
        diff0 = get_diff(t0)

    t1 = t0
    diff1 = diff0

    # Phase 1: Bracket the root
    for _ in range(1000):
        t1 += step_days
        diff1 = get_diff(t1)
        
        if diff0 * diff1 <= 0 and abs(diff0) < 45: 
            break
            
        t0 = t1
        diff0 = diff1
    else:
        raise ValueError("Could not find an Ascendant transit within search limits.")

    # Phase 2: Fast Bisection to narrow the gap to ~1 minute
    precision_days = 0.001  # Broaden to ~1.4 minutes to save loops

    while abs(t1 - t0) > precision_days:
        t_mid = (t0 + t1) / 2.0
        diff_mid = get_diff(t_mid)
        
        if diff_mid == 0.0:
            t0 = t_mid
            diff0 = 0.0
            t1 = t_mid
            diff1 = 0.0
            break
        elif diff0 * diff_mid < 0:
            t1 = t_mid
            diff1 = diff_mid
        else:
            t0 = t_mid
            diff0 = diff_mid

    # Phase 3: Exact Linear Interpolation for Sub-Arcsecond Precision
    # Since the gap is now microscopic, planetary motion is a perfectly straight line.
    # This equation calculates the exact fractional Julian day of the 0.0" crossing.
    if diff1 - diff0 != 0:
        exact_jd = t0 - diff0 * (t1 - t0) / (diff1 - diff0)
    else:
        exact_jd = (t0 + t1) / 2.0

    sla_exact = ascendant(exact_jd, place)
    exact_long = (sla_exact[0] * 30 + sla_exact[1]) * divisional_chart_factor % 360
    
    if _DEBUG_: 
        print('JD', utils.jd_to_gregorian(exact_jd), 'asc long', exact_long)

    return exact_jd, exact_long
def next_ascendant_entry_date_old(jd,place,direction=1,precision=0.01,raasi=None,divisional_chart_factor=1):
    """
        get the date when the ascendant enters a zodiac
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param direction: 1= next entry, -1 previous entry
        @param precision: precision in degrees within which longitude entry whould be (default: 1.0 degrees)
        @param raasi: raasi at which planet should enter. 
            If raasi==None: gives entry to next constellation
            If raasi is specified [1..12] gives entry to specified constellation/raasi
        @return Julian day number of planet entry into zodiac
    """
    _DEBUG_ = False
    increment_days = 1.0/24.0/60.0/divisional_chart_factor # For moon/lagna increment days in minutes
    sla = ascendant(jd, place); sl = sla[0]*30+sla[1]
    if raasi==None:
        multiple = (((sl*divisional_chart_factor//30)+1)%12)*30
        if direction==-1: multiple = (sl*divisional_chart_factor//30)%12*30
    else: 
        multiple = (raasi-1)*30 if raasi>0 else 0
    if _DEBUG_: print(utils.jd_to_gregorian(jd),'sla',sla,'multiple',multiple,'precision',precision)
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        jd += increment_days*direction
        sla = ascendant(jd, place); sl = (sla[0]*30+sla[1])*divisional_chart_factor%360
        if _DEBUG_: print('sl',sl,utils.jd_to_gregorian(jd),'multiple',multiple)
    offsets = [t*increment_days for t in range(-10,10)] 
    asc_longs = []
    for t in offsets:
        sla = ascendant(jd+t, place); sl = (sla[0]*30+sla[1])*divisional_chart_factor%360
        asc_longs.append(sl)
    if _DEBUG_: print(offsets,asc_longs,multiple)
    asc_hour = utils.inverse_lagrange(offsets, asc_longs, multiple) # Do not move % 360 above
    #asc_hour /= divisional_chart_factor
    jd += asc_hour
    sla = ascendant(jd, place); asc_long = (sla[0]*30+sla[1])*divisional_chart_factor%360
    if _DEBUG_: print('JD',utils.jd_to_gregorian(jd),'asc long',asc_long)
    return jd,asc_long
def next_planet_entry_date_old(planet,jd,place,direction=1,increment_days=0.01,precision=0.1,raasi=None):
    """
        get the date when a planet enters a zodiac
        @param planet: planet index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param direction: 1= next entry, -1 previous entry
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param precision: precision in degrees within which longitude entry whould be (default: 0.1 degrees)
        @param raasi: raasi at which planet should enter. 
            If raasi==None: gives entry to next constellation
            If raasi is specified [1..12] gives entry to specified constellation/raasi
        @return Julian day number of planet entry into zodiac
    """
    search_jd = jd
    if planet == const._ascendant_symbol:
        return next_ascendant_entry_date(search_jd, place, direction=direction, precision=1.0, raasi=raasi)
    pl = ephemeris_planet_index(planet)
    if planet in [const._ascendant_symbol,const._MOON]: increment_days = 1.0/24.0/60.0 # For moon/lagna increment days in minutes
    if pl==const._KETU:
        raghu_raasi = (raasi-1+6)%12+1 if raasi!=None else raasi
        ret = next_planet_entry_date(const.RAHU_ID, search_jd, place,direction=direction,raasi=raghu_raasi)
        p_long = (ret[1]+180)%360
        return ret[0],p_long
    jd_utc = search_jd - place.timezone/24.0
    sl = sidereal_longitude(jd_utc,pl, place)
    #if planet in [const.RAHU_ID,const.KETU_ID]: direction *= -1 # Rahu/Ketu always in reverse direction
    if raasi==None:
        multiple = (((sl//30)+1)%12)*30
        if direction==-1: multiple = (sl//30)%12*30
        if pl == const._RAHU:
            multiple = ((sl//30)%12 * 30)%360
            if direction==-1:
                multiple = ((sl//30+1)%12*30)%360
    else: 
        multiple = (raasi-1)*30 if raasi>0 else 0
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        search_jd += increment_days*direction; jd_utc = search_jd - place.timezone/24.0
        sl = sidereal_longitude(jd_utc,pl, place)
    sank_date = jd_to_gregorian(jd_utc)
    sank_sunrise = sunrise(jd_utc,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    planet_longs = []
    for t in offsets:
        sl = sidereal_longitude(sank_sunrise+t,pl, place)
        planet_longs.append(sl)
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    planet_hour1 = (sank_sunrise + planet_hour - sank_jd_utc)*24+place.timezone
    sank_jd_utc += planet_hour1/24.0
    planet_long = sidereal_longitude(sank_jd_utc-place.timezone/24,pl, place)
    y,m,d,fh = jd_to_gregorian(sank_jd_utc); sank_date = Date(y,m,d); planet_hour1 = fh
    return sank_jd_utc,planet_long
def next_planet_entry_date(planet, jd, place, direction=1, increment_days=0.01, precision=0.1, raasi=None):
    """
    Hyper-Optimized using Kinematic Predictive Jumps, False Position, and 
    Exact Linear Interpolation for absolute down-to-the-second precision.
    """
    search_jd = jd
    
    # 1. Handle Ascendant 
    if planet == const._ascendant_symbol:
        return next_ascendant_entry_date(search_jd, place, direction=direction, precision=precision, raasi=raasi)
        
    pl = ephemeris_planet_index(planet)
    
    # 2. Handle Ketu recursively via Rahu
    if pl == const._KETU:
        raghu_raasi = (raasi - 1 + 6) % 12 + 1 if raasi is not None else raasi
        ret = next_planet_entry_date(const.RAHU_ID, search_jd, place, direction=direction, raasi=raghu_raasi)
        p_long = (ret[1] + 180) % 360
        return ret[0], p_long

    jd_utc = search_jd - place.timezone / 24.0
    current_sl = sidereal_longitude(jd_utc, pl, place)

    # 3. Determine target boundary
    if raasi is None:
        multiple = (((current_sl // 30) + 1) % 12) * 30
        if direction == -1: 
            multiple = (current_sl // 30) % 12 * 30
            
        if pl == const._RAHU:
            multiple = ((current_sl // 30) % 12 * 30) % 360
            if direction == -1:
                multiple = ((current_sl // 30 + 1) % 12 * 30) % 360
    else: 
        multiple = (raasi - 1) * 30 if raasi > 0 else 0

    target_long = multiple

    def get_diff(t):
        sl = sidereal_longitude(t, pl, place)
        diff = (sl - target_long) % 360
        if diff > 180: 
            diff -= 360
        return diff

    # 4. Kinematic Maximum Speeds (degrees per day)
    max_speeds = {
        const._MOON: 15.5,
        const._SUN: 1.05,
        const._MERCURY: 2.5,
        const._VENUS: 1.3,
        const._MARS: 0.85,
        const._JUPITER: 0.26,
        const._SATURN: 0.13,
        const._RAHU: 0.07
    }
    max_speed = max_speeds.get(pl, 2.0)
    
    bracket_steps = {
        const._MOON: 0.25,
        const._SUN: 2.0,
        const._MERCURY: 1.0,
        const._VENUS: 1.0,
        const._MARS: 3.0,
        const._JUPITER: 5.0,
        const._SATURN: 10.0,
        const._RAHU: 10.0
    }
    safe_bracket = bracket_steps.get(pl, 1.0) * direction

    t0 = jd_utc
    diff0 = get_diff(t0)

    if abs(diff0) < 0.0001:
        t0 += (0.01 * direction)
        diff0 = get_diff(t0)

    t1 = t0
    diff1 = diff0

    # Phase 1: Kinematic Predictive Bracketing
    for _ in range(1000):
        distance = abs(diff1)
        if distance > 3.0:
            step = (distance / max_speed) * 0.85 * direction
        else:
            step = safe_bracket
            
        t1 += step
        diff1 = get_diff(t1)
        
        if diff0 * diff1 <= 0 and abs(diff0) < 45: 
            break
            
        t0 = t1
        diff0 = diff1
    else:
        raise ValueError(f"Could not find a transit for planet {planet} within search limits.")

    # Phase 2: False Position to narrow the gap to ~1 minute (~0.001 days)
    precision_days = 0.001 

    while abs(t1 - t0) > precision_days:
        if diff1 - diff0 == 0:
            t_mid = (t0 + t1) / 2.0
        else:
            t_mid = t1 - diff1 * (t1 - t0) / (diff1 - diff0)
            
        diff_mid = get_diff(t_mid)
        
        if abs(diff_mid) < 0.000001:
            t0 = t_mid
            t1 = t_mid
            break
            
        if diff0 * diff_mid < 0:
            t1 = t_mid
            diff1 = diff_mid
        else:
            t0 = t_mid
            diff0 = diff_mid

    # Phase 3: Exact Linear Interpolation for Sub-Arcsecond Precision
    # Pinpoints the exact microscopic fraction of a second where longitude hits target_long exactly.
    if diff1 - diff0 != 0:
        exact_jd_utc = t0 - diff0 * (t1 - t0) / (diff1 - diff0)
    else:
        exact_jd_utc = (t0 + t1) / 2.0

    exact_long = sidereal_longitude(exact_jd_utc, pl, place)

    # 5. Return to local JD
    sank_jd_local = exact_jd_utc + place.timezone / 24.0
    
    return sank_jd_local, exact_long
def next_planet_retrograde_change_date(planet, panchanga_date, place, increment_days=1, direction=1):
    """
        Optimized drop-in replacement using Dynamic Bracketing and Bisection Root-Finding.
        Yields ~0.0s execution time with sub-second precision.
    """
    if planet in [const.SUN_ID, const.MOON_ID]:
        print(planet, "is not a retrograding planet")
        return 
    if not const._use_true_nodes_for_rahu_ketu and planet in [const.RAHU_ID, const.KETU_ID]:
        raise ValueError("Rahu/Ketu are always in retrograde if configured as Mean Nodes")
        return

    jd = utils.gregorian_to_jd(panchanga_date)

    # Helper function to get the current speed direction cleanly
    def get_sign(t):
        return _planet_speed_sign(t, place, planet)

    s0 = get_sign(jd)

    # If starting point itself is exactly stationary, nudge forward slightly
    while s0 == 0:
        jd += 0.01 * direction
        s0 = get_sign(jd)

    # Phase 1: Dynamic Bracketing
    # We set safe max steps to bracket the change rapidly. 
    # Mercury retrogrades for ~21 days, so a safe step is ~3 days to ensure we never jump over it.
    # Slower planets can safely jump further.
    step_map = {
        const.MERCURY_ID: 3.0,
        const.VENUS_ID: 10.0,
        const.MARS_ID: 15.0,
        const.JUPITER_ID: 30.0,
        const.SATURN_ID: 30.0,
        const.RAHU_ID: 1.0,
        const.KETU_ID: 1.0
    } if hasattr(const, 'MERCURY_ID') else {} # Safety fallback if constant names differ
    
    # Use dynamic step, but fallback to a foolproof 3.0 days (or 1.0 for nodes) if unmapped
    default_safe_step = 1.0 if planet in [const.RAHU_ID, const.KETU_ID] else 3.0
    safe_step = step_map.get(planet, default_safe_step) * direction

    t0 = jd
    t1 = t0
    s1 = s0

    # Fast forward until the direction sign flips
    for _ in range(1000):
        t1 += safe_step
        s1 = get_sign(t1)

        if s1 == 0: 
            break  # Exact stationary point hit by chance
        if s1 != s0:
            break  # Sign flipped, the zero crossing is trapped between t0 and t1

        t0 = t1
    else:
        raise ValueError(f"Could not find a retrograde direction change within search limits.")

    # Phase 2: Ultra-Precise Bisection Root-Finding
    # Halves the gap repeatedly, zeroing in on the exact stationary moment.
    # 0.0000001 days = 0.008 seconds of real-time accuracy.
    precision_days = 0.0000001  

    while abs(t1 - t0) > precision_days:
        t_mid = (t0 + t1) / 2.0
        s_mid = get_sign(t_mid)

        if s_mid == 0:  # Perfect mathematical zero hit
            t0 = t_mid
            t1 = t_mid
            break
        elif s_mid == s0:
            t0 = t_mid
        else:
            t1 = t_mid

    exact_jd = (t0 + t1) / 2.0
    
    # The new direction is mathematically the opposite of the initial non-zero direction
    new_direction = -s0 
    
    return exact_jd, new_direction
def next_planet_retrograde_change_date_old(planet, panchanga_date, place, increment_days=1, direction=1):
    """
        get the date when a retrograde planet changes its direction
        @param planet: planet index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param direction: 1= next direction change, -1 previous direction change
        @return Julian day number of planet changes retrograde direction
        NOTE: Sun and Moon do not retrograde. 
            Rahu/Ketu always retrograde as Mean Nodes (and do not exibit stationary or direct)
            Rahu/Ketu as True nodes - retrograde, stationary or even direct
    """
    if planet in [const.SUN_ID, const.MOON_ID]:
        print(planet,"is not a retrograding planet")
        return 
    if not const._use_true_nodes_for_rahu_ketu and planet in [const.RAHU_ID,const.KETU_ID]:
        raise ValueError("Rahu/Ketu are always in retrograde if configured as Mean Nodes")
        return

    jd = utils.gregorian_to_jd(panchanga_date)

    sl_sign = _planet_speed_sign(jd, place, planet)

    # if starting point itself is stationary, move until a definite direction is found
    while sl_sign == 0:
        jd += increment_days * direction
        sl_sign = _planet_speed_sign(jd, place, planet)

    sl_sign_next = sl_sign

    # coarse search: ignore stationary (0), stop only when opposite nonzero sign is found
    while True:
        jd += increment_days * direction
        sl_sign_next = _planet_speed_sign(jd, place, planet)

        if sl_sign_next == 0:
            continue

        if sl_sign_next == sl_sign:
            continue

        break

    # go back to previous coarse point
    jd -= increment_days * direction

    # refine with smaller step
    increment_days = const.conjunction_increment
    sl_sign_next = sl_sign

    while True:
        jd += increment_days * direction
        sl_sign_next = _planet_speed_sign(jd, place, planet)

        if sl_sign_next == 0:
            continue

        if sl_sign_next == sl_sign:
            continue

        break

    return jd, sl_sign_next
def _next_planet_retrograde_change_date(planet,panchanga_date,place,increment_days=1,direction=1):
    """
        get the date when a retrograde planet changes its direction
        @param planet: planet index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param direction: 1= next direction change, -1 previous direction change
        @return Julian day number of planet changes retrogade direction
        NOTE: Sun and Moon do not retrograde. 
            Rahu/Ketu always retrograde as Mean Nodes (and do not exibit stationary or direct)
            Rahu/Ketu as True nodes - retrograde, stationary or even direct
    """
    if planet in [const.SUN_ID, const.MOON_ID]:
        print(planet,"is not a retrograding planet")
        return 
    if not const._use_true_nodes_for_rahu_ketu and planet in [const.RAHU_ID,const.KETU_ID]:
        raise ValueError("Rahu/Ketu are always in retrograde if configured as Mean Nodes")
        return
    jd = utils.gregorian_to_jd(panchanga_date)
    sl_sign = _planet_speed_sign(jd,place,planet); sl_sign_next = sl_sign
    while sl_sign == sl_sign_next:
        jd += increment_days*direction
        sl_sign_next = _planet_speed_sign(jd,place,planet)
    jd -= increment_days*direction; increment_days=const.conjunction_increment; sl_sign_next=sl_sign
    while sl_sign == sl_sign_next:
        jd += increment_days*direction
        sl_sign_next = _planet_speed_sign(jd,place,planet)
    return jd,sl_sign_next
def next_planet_stationary_duration(
    planet,
    current_jd,
    place,
    threshold=0.02, # We use 0.02 deg/day instead of 1 arcsecond to get bigger window for stationary interval
    direction=1,
    step=0.01,
):
    """
    Find a stationary interval relative to current_jd.
    Uses ultra-fast float-safe bisection to perfectly capture the threshold boundaries.
    """
    if planet in [const.MOON_ID, const.SUN_ID]:
        raise ValueError("Sun/Moon are not stationary planets")
    if not const._use_true_nodes_for_rahu_ketu and planet in [const.RAHU_ID, const.KETU_ID]:
        raise ValueError("Rahu/Ketu are always in retrograde if configured as Mean Nodes")
    if direction not in (+1, -1):
        raise ValueError("direction must be +1 or -1")

    def get_speed(jd_):
        return daily_planet_speed(jd_, place, planet)

    def find_boundary(jd_in, step_dir):
        """Steps outward then bisects to find the exact millisecond it crosses the threshold."""
        jd_out = jd_in
        # Step outward until we exceed the threshold
        while abs(get_speed(jd_out)) < threshold:
            jd_out += step_dir * step
            
        # Bisect down to millisecond precision
        for _ in range(30):
            mid = (jd_in + jd_out) / 2.0
            if abs(get_speed(mid)) < threshold:
                jd_in = mid
            else:
                jd_out = mid
        return (jd_in + jd_out) / 2.0

    jd = current_jd
    v_curr = get_speed(jd)

    # --------------------------------------------------
    # 1. Handle if we are ALREADY inside a stationary interval
    # --------------------------------------------------
    if abs(v_curr) < threshold:
        start_jd = find_boundary(jd, -1)
        end_jd = find_boundary(jd, 1)
        
        if direction == -1:
            return utils.jd_to_gregorian(start_jd), utils.jd_to_gregorian(end_jd)
            
        # Fast-forward safely out of the current interval
        jd = end_jd + step
        while abs(get_speed(jd)) < threshold:
            jd += step
        v_curr = get_speed(jd)

    # --------------------------------------------------
    # 2. Fast forward to find the exact zero-crossing
    # --------------------------------------------------
    v_prev = v_curr
    coarse_step = max(step, 0.5)  # Safe large steps to skip days quickly
    
    while True:
        jd += direction * coarse_step
        v = get_speed(jd)

        # Jumped directly into the threshold?
        if abs(v) < threshold:
            jd_inside = jd
            break

        # Did the speed cross zero? (Boolean sign check - immune to float underflow)
        if (v > 0) != (v_prev > 0):
            a = jd - direction * coarse_step
            b = jd
            v_a = v_prev
            
            # Bisect exactly where speed == 0 
            for _ in range(30):
                mid = (a + b) / 2.0
                v_mid = get_speed(mid)
                if (v_mid > 0) == (v_a > 0):
                    a = mid
                    v_a = v_mid
                else:
                    b = mid
            
            jd_inside = (a + b) / 2.0
            break
            
        v_prev = v

    # --------------------------------------------------
    # 3. We found the anchor point. Resolve the exact boundaries.
    # --------------------------------------------------
    start_jd = find_boundary(jd_inside, -1)
    end_jd = find_boundary(jd_inside, 1)

    # Ensure chronological order
    if start_jd > end_jd:
        start_jd, end_jd = end_jd, start_jd

    return utils.jd_to_gregorian(start_jd), utils.jd_to_gregorian(end_jd)
def next_planet_stationary_duration_old(
    planet,
    current_jd,
    place,
    threshold=const.one_arc_second,
    direction=1,
    step=0.01,
):
    """
    Find a stationary interval relative to current_jd.

    direction:
        +1 -> return the next stationary interval whose start_jd > current_jd
        -1 -> return the stationary interval whose start_jd < current_jd;
              if already inside a stationary interval, return the current one

    threshold:
        Speed in degrees/day below which the planet is considered stationary.
        NOTE: Sun and Moon do not retrograde. 
            Rahu/Ketu always retrograde as Mean Nodes (and do not exibit stationary or direct)
            Rahu/Ketu as True nodes - retrograde, stationary or even direct
    """
    if planet in [const.MOON_ID, const.SUN_ID]:
        raise ValueError("Sun/Moon are not stationary planets")
    if not const._use_true_nodes_for_rahu_ketu and planet in [const.RAHU_ID,const.KETU_ID]:
        raise ValueError("Rahu/Ketu are always in retrograde if configured as Mean Nodes")
    if direction not in (+1, -1):
        raise ValueError("direction must be +1 or -1")

    def is_stationary(jd_):
        return abs(daily_planet_speed(jd_, place, planet)) < threshold

    def get_stationary_interval_containing(jd_):
        start_jd = jd_
        while is_stationary(start_jd):
            start_jd -= step

        end_jd = jd_
        while is_stationary(end_jd):
            end_jd += step
        _interval = start_jd + step, end_jd - step
        return _interval

    # --------------------------------------------------
    # If already inside a stationary interval:
    #   direction = -1 -> return current interval
    #   direction = +1 -> skip current interval and find next
    # --------------------------------------------------
    if is_stationary(current_jd):
        current_start, current_end = get_stationary_interval_containing(current_jd)

        if direction == -1:
            return utils.jd_to_gregorian(current_start), utils.jd_to_gregorian(current_end)

        # direction == +1
        jd = current_end + step
        while not is_stationary(jd):
            jd += step
        _sjd1,_sjd2 = get_stationary_interval_containing(jd)
        return utils.jd_to_gregorian(_sjd1), utils.jd_to_gregorian(_sjd2)

    # --------------------------------------------------
    # Not currently stationary:
    # search in requested direction until entering one
    # --------------------------------------------------
    jd = current_jd
    while not is_stationary(jd):
        jd += direction * step

    _sjd1,_sjd2 = get_stationary_interval_containing(jd)
    return utils.jd_to_gregorian(_sjd1), utils.jd_to_gregorian(_sjd2)
def _nisheka_time(jd,place):
    """
        @param jd: Julian number 
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return julian date number of nisheka time
        TODO: Formula needs to be checked
        Does not match JHora value (differs by upto 15 days)
    """
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = Date(y,m,d); tob = utils.to_dms(fh,as_string=False)
    asc = ascendant(jd, place)
    pp = dhasavarga(jd, place)
    sat_long = pp[const.SATURN_ID][1][0]*30+pp[const.SATURN_ID][1][1]
    moon_long=pp[const.MOON_ID][1][0]*30+pp[const.MOON_ID][1][1]
    lagna_long = asc[0]*30+asc[1]
    ninth_house_long = (const.HOUSE_9*30+lagna_long+15)%360
    gl = gulika_longitude(dob,tob,place); gulika_long = gl[0]*30+gl[1]
    ml = maandi_longitude(dob,tob,place); maandi_long = ml[0]*30+ml[1]
    a = 0.5*( (sat_long-gulika_long)%30 + ((sat_long-maandi_long)%30) ); b = (ninth_house_long-lagna_long)%360
    c = (a+b)%360 ; c1 = c%30; bm = c//30
    d = (c1+moon_long%30)
    jd_nisheka = jd - (bm*const.sidereal_year/12+d)
    return jd_nisheka
def _nisheka_time_1(jd,place):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = Date(y,m,d); tob = utils.to_dms(fh,as_string=False)
    asc = ascendant(jd, place)
    pp = dhasavarga(jd, place)
    from jhora.horoscope.chart.house import house_owner_from_planet_positions
    asc_house = asc[0]; lagna_long = asc_house*30 + asc[1]
    lagna_lord = house_owner_from_planet_positions(pp,asc_house,check_during_dhasa=False)
    lagna_lord_long = pp[lagna_lord][0]*30+pp[lagna_lord]
    drishya = 1.0
    if (lagna_lord_long < (lagna_long+15)) or (lagna_lord_long>(lagna_long+195)):
        drishya = -1
    sat_long = pp[const.SATURN_ID][1][0]*30+pp[const.SATURN_ID][1][1]
    gl = gulika_longitude(dob,tob,place); gulika_long = gl[0]*30+gl[1]
    moon_long=pp[const.MOON_ID][1][1]
    a = abs(sat_long-gulika_long)%30; c= (a+moon_long)%30
    jd_nisheka = jd - (273 + drishya*c*27.3217/30)
    return jd_nisheka
def graha_drekkana(jd,place,use_bv_raman_table=False):
    return [const.drekkana_table_bvraman[h][int(long//10)] for _,(h,long) in dhasavarga(jd, place)] if use_bv_raman_table \
        else [const.drekkana_table[h][int(long//10)] for _,(h,long) in dhasavarga(jd, place)]
def sahasra_chandrodayam(jd, place):
    _MEAN_SYNODIC_MONTH = 29.530588853
    tithi_ = tithi(jd, place)[0]
    # Step 1: first full moon after jd -- identical to the original's iteration #1.
    first_full_moon_jd = full_moon(jd, place, tithi_, opt=1)

    # Step 2: jump directly to an estimate of the 1000th full moon (999 more
    # lunations after the first one found above) using the mean synodic month.
    estimate_jd = first_full_moon_jd + 999 * _MEAN_SYNODIC_MONTH

    # Step 3: refine the estimate to the exact instant. Seed the search a
    # couple of days before the estimate (safety margin for the small
    # per-cycle variation around the mean) so full_moon() locks onto the
    # correct nearby full moon rather than potentially the wrong side of it.
    seed_jd = estimate_jd - 2.0
    tithi_at_seed = tithi(seed_jd, place)[0]
    full_moon_jd = full_moon(seed_jd, place, tithi_at_seed, opt=1)
    approx_count = round((full_moon_jd - first_full_moon_jd) / _MEAN_SYNODIC_MONTH) + 1
    while approx_count < 1000:
        jd_next = full_moon_jd + 0.25
        tithi_next = tithi(jd_next, place)[0]
        full_moon_jd = full_moon(jd_next, place, tithi_next, opt=1)
        approx_count += 1
    while approx_count > 1000:
        jd_prev_seed = full_moon_jd - _MEAN_SYNODIC_MONTH - 2.0
        tithi_prev = tithi(jd_prev_seed, place)[0]
        full_moon_jd = full_moon(jd_prev_seed, place, tithi_prev, opt=1)
        approx_count -= 1

    return utils.jd_to_gregorian(full_moon_jd)[:-1]
def amrita_gadiya(jd,place):
    """ Ref: Panchangam Calculations: Karanam Ramakumar """
    nak,_,nak_beg,nak_end = nakshatra(jd,place)[:4]
    nak_durn = nak_end-nak_beg
    nak_fac = const.amrita_gadiya_varjyam_star_map[nak-1][0]/24
    ag_start = nak_beg + nak_fac*nak_durn
    ag_durn = nak_durn * 1.6/24; ag_end = ag_start+ag_durn
    return ag_start,ag_end
def varjyam(jd,place):
    """ Ref: Panchangam Calculations: Karanam Ramakumar """
    nak,_,nak_beg,nak_end = nakshatra(jd,place)[:4]
    nak_durn = nak_end-nak_beg
    if (nak == 19): # Moolam has two Varjyam timings
        nak_fac1 = const.amrita_gadiya_varjyam_star_map[nak-1][1][0]/24
        nak_fac2 = const.amrita_gadiya_varjyam_star_map[nak-1][1][1]/24
        ag_start1 = nak_beg + nak_fac1*nak_durn
        ag_start2 = nak_beg + nak_fac2*nak_durn
        ag_durn = nak_durn * 1.6/24
        ag_end1 = ag_start1+ag_durn
        ag_end2 = ag_start2+ag_durn
        return ag_start1,ag_end1,ag_start2,ag_end2
    else:
        nak_fac = const.amrita_gadiya_varjyam_star_map[nak-1][1]/24
        ag_start = nak_beg + nak_fac*nak_durn
        ag_durn = nak_durn * 1.6/24; ag_end = ag_start+ag_durn
        return ag_start,ag_end
def anandhaadhi_yoga(jd,place):
    nak = nakshatra(jd,place)
    day = vaara(jd,place)
    return const.anandhaadhi_yoga_day_star_list[day].index(nak[0]-1),nak[2]
def triguna(jd,place):
    _,_,_,fh = utils.jd_to_gregorian(jd)
    day = vaara(jd,place)
    return utils.triguna_of_the_day_time(day,fh)
def vivaha_chakra_palan(jd,place):
    """
        1. Collateral damage to family
        2. Wealthy and Blessed
        3. Collateral damage to girl's family
        4. Poverty and cursed
        5. Gainful and beneficial
        6. Loss of reputation and honour
        7. Devastating results for the girl
        8. Completely successfull
        9. Wonderful pair and blessed
    """
    jd_utc = jd - place.timezone/24
    sun_long = sidereal_longitude(jd, const._SUN, place)
    sun_star = nakshatra_pada(sun_long)[0]
    
    moon_long = sidereal_longitude(jd, const._MOON, place)
    moon_star = nakshatra_pada(moon_long)[0]

    # Initialize 3x3 grid with three stars each cell
    grid = [[[(sun_star + (i + j) - 1) % 27 + 1 for j in range(-1, 2)] for i in range(-1, 2)] for _ in range(3)]

    # Define positions to place stars in 3x3 grid starting East and moving clockwise
    positions = [(1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2)]

    # Populate the grid with the calculated stars
    all_stars = [(sun_star + i - 2) % 27 + 1 for i in range(27)]
    for i, (r, c) in enumerate(positions):
        grid[r][c] = all_stars[3*(i+1):3*(i+2)]

    # Find the moon star position using next()
    position = next((i, j) for i in range(3) for j in range(3) if moon_star in grid[i][j])
    if position:
        r, c = position
        mapping = {(1, 1): 1, (1, 2): 2, (2, 2): 3, (2, 1): 4, (2, 0): 5, (1, 0): 6, (0, 0): 7, (0, 1): 8, (0, 2): 9}
        return mapping[(r, c)]
    return None
def tamil_yogam(jd, place,check_special_yogas=True,use_sringeri_panchanga_version=False):
    """
        @return tamil yoga index
        0:'siddha', 1:'prabalarishta', 2:'marana', 3:'amritha',4:'amritha_siddha',5:'mrithyu',6:'daghda',
        7:'yamaghata',8:'utpata'
    """
    panchang = const.tamil_basic_yoga_sringeri_panchanga_list if use_sringeri_panchanga_version else const.tamil_basic_yoga_list 
    nak = nakshatra(jd, place)
    naks = nak[0]-1
    wday = vaara(jd,place)
    #print(utils.DAYS_LIST[wday],utils.NAKSHATRA_LIST[naks],nak)
    yi = panchang[wday][naks]
    if not check_special_yogas: return yi,nak[2],nak[3]
    # Additional yoga checks
    ad = [const.amrita_siddha_yoga_dict,const.mrityu_yoga_dict,const.daghda_yoga_dict, const.yamaghata_yoga_dict,
          const.utpata_yoga_dict]
    for d in ad:
        if d[wday]==naks: return 4+ad.index(d),nak[2],nak[3],yi
    if naks in const.sarvartha_siddha_yoga[wday]: return len(const.tamil_yoga_names)-1,nak[2],nak[3]
    return yi,nak[2],nak[3],yi
def brahma_muhurtha(jd, place):
    dl = day_length(jd, place); nl = night_length(jd, place)
    dm = dl/15.0 ; nm = nl/15.0
    sunrise_hours = sunrise(jd, place)[0]
    bm_start = sunrise_hours-2*nm; bm_end = sunrise_hours-nm
    return bm_start,bm_end
def godhuli_muhurtha(jd, place):
    dl = day_length(jd, place); nl = night_length(jd, place)
    dm = dl/15.0 ; nm = nl/15.0
    sunset_hours = sunset(jd, place)[0]
    bm_start = sunset_hours-0.25*dm; bm_end = sunset_hours+0.25*nm
    return bm_start,bm_end
def sandhya_periods(jd,place):
    """
        returns three sandhya periods: - each (Ghati is 1/30th of day length)
            Pratah - 2 ghatis before sunrise and 1 ghati after sunrise
            Madhyaahna - 1.5 ghatis before noon and 1.5 ghatis after noon
            Saayam - 1 ghati before sunset and 2 after sunset
    """
    dl = day_length(jd, place); ghati = dl/30.
    sunrise_hours = sunrise(jd, place)[0]; sunset_hours = sunset(jd, place)[0]
    noon = sunrise_hours+0.5*dl
    ps = (sunrise_hours-2*ghati, sunrise_hours+ghati)
    ms = (noon-1.5*ghati, noon+1.5*ghati)
    ss = (sunset_hours-ghati,sunset_hours+2*ghati)
    return ps,ms,ss
def vijaya_muhurtha(jd,place):
    dl = day_length(jd, place); gd = dl/30.
    nl = night_length(jd, place); gn = nl/30.0
    sunrise_hours = sunrise(jd, place)[0]; sunset_hours = sunset(jd, place)[0]
    noon = sunrise_hours+0.5*dl; _midnight = sunset_hours+0.5*nl
    vmd = (noon-gd, noon+gd)
    vmn = (_midnight-gn, _midnight+gn)
    return vmd,vmn
def nishita_kaala(jd,place):
    """ Eighth muhurtha of the night """
    nl = night_length(jd, place); gn = nl/30.0
    sunset_hours = sunset(jd, place)[0]
    return sunset_hours+7*gn, sunset_hours+8*gn
def tamil_jaamam(jd,place,jaamam_count=8):
    """ 
        Same as Gauri Chogadiya
        In tamil there 8 jaamam (aka yaamam) 4 for day and 4 for night
        Alternative there is another ancient tamil system with 10 yaamam (5+5)
        In Tamil 1 jaamam = 3 muhurthas. 10 jaamam = 1 day (5 jaamam) and night (5 jaamam)
        8th jaamam = 3rd muhurtha of night
        In Sanskrit these are 8 prahar (4+4) => Gauri Chogadiya
    """
    if jaamam_count not in [8,10]: jaamam_count = 8
    dl = day_length(jd, place); day_jaamam = dl/jaamam_count/2
    nl = night_length(jd, place); night_jaamam = nl/jaamam_count/2
    sunrise_hours = sunrise(jd, place)[0]
    sunset_hours = sunset(jd, place)[0]
    jaamam = [(sunrise_hours+j*day_jaamam,sunrise_hours+(j+1)*day_jaamam) for j in range(5)]
    jaamam += [(sunset_hours+j*night_jaamam,sunset_hours+(j+1)*night_jaamam) for j in range(5)]
    return jaamam
def nishita_muhurtha(jd,place):
    """ 2 ghathis around midnight """
    nl = night_length(jd, place); gn = nl/30.0
    sunset_hours = sunset(jd, place)[0]
    _midnight = sunset_hours+0.5*nl
    return _midnight-gn,_midnight+gn
def thaaraabalam(jd,place,return_only_good_stars=True):
    """
    thaarabalam_names = [('Paramitra','Good'),('Janma','Not Good'),('Sampatha','Very Good'),('Vipatha','Bad'),
                        ('Kshema','Good'),('Pratyaka','Not Good'),('Sadhana','Very Good'),('Naidhana','Totally Bad'),
                         ('Mitra','Good')]
    """
    good_tharaabalam = [0,2,4,6,8]; gtb = []
    nak = nakshatra(jd, place); todays_star = nak[0]
    #print('todays star',utils.NAKSHATRA_LIST[todays_star-1],utils.to_dms(nak[2]))
    tb_dict = [[] for _ in range(9)]
    for birth_star in range(1,28):
        tb_div = utils.count_stars(birth_star,todays_star)%9
        if return_only_good_stars and tb_div in good_tharaabalam: gtb.append(birth_star)
        tb_dict[tb_div].append(birth_star) 
    return gtb if return_only_good_stars else tb_dict
def muhurthas(jd, place):
    dl = day_length(jd, place); day_muhurtha = dl/15
    nl = night_length(jd, place); night_muhurtha = nl/15
    sunrise_hours = sunrise(jd, place)[0]
    sunset_hours = sunset(jd, place)[0]
    _muhurthas = [(sunrise_hours+j*day_muhurtha,sunrise_hours+(j+1)*day_muhurtha) for j in range(15)]#Fixed V4.3.6
    _muhurthas += [(sunset_hours+j*night_muhurtha,sunset_hours+(j+1)*night_muhurtha) for j in range(15)]#Fixed 4.3.6
    _mh_list = [(mk,const.muhurthas_of_the_day[mk],_muhurthas[mh]) for mh,mk in enumerate(const.muhurthas_of_the_day.keys()) ]
    return _mh_list
def udhaya_lagna_muhurtha(jd, place):
    """
        returns the times at which the ascendant enters each of the 12 rasis, 
        starting from the sunrise of the date of jd
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [(rasi, entry_hour, exit_hour), ...] for 12 rasis in order of rising; rasi = [0..11]  0 = Aries
          entry_hour/exit_hour are local civil hours relative to the civil-day midnight of jd:
          negative if before that day, greater than 24 if after
    """
    # 1. Get the exact sunrise Julian Day
    jd_sunrise = sunrise(jd, place)[-1]
    
    # 2. Find local civil midnight for the given jd day
    # Assuming 'jd' is local time, or you have a way to find midnight of the civil day.
    # If jd is already at local midnight or you can compute it:
    # (Adjust this line if your framework has a specific local_midnight(jd, place) function)
    jd_midnight = int(jd + 0.5) - 0.5  # Standard UT midnight fallback; adjust to local midnight if needed
    
    # 3. Get the starting ascendant sign active exactly at sunrise
    current_asc = ascendant(jd_sunrise, place)[0]
    
    # 4. The Muhurtha sequence starts EXACTLY at sunrise
    jd_start = jd_sunrise
    ulm = []
    
    for l in range(12):
        # Determine the current rasi sign in the sequence
        rasi = (current_asc + l) % 12
        
        # Look forward to find when the next sign enters
        jd_next_search = jd_start + const.conjunction_increment
        jd_end = next_ascendant_entry_date(jd_next_search, place, precision=1.0)[0]
        
        # Convert absolute Julian Days to local civil hours relative to midnight
        fhs = (jd_start - jd_midnight) * 24.0
        fhe = (jd_end - jd_midnight) * 24.0
        
        ulm.append((rasi, fhs, fhe))
        
        # Move the window forward for the next sign
        jd_start = jd_end
    return ulm
def chandrabalam(jd,place):
    """
        returns the chandrabalam / favorable moon's transit zodiacs for the janma rasi at JD
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return list of favorable chandrabala raasis 
    """
    janma_raasi = raasi(jd, place)[0]-1
    return [ (janma_raasi+c-1)%12+1 for c in [1,3,6,7,10,11] ]
def panchaka_rahitha(jd, place):
    """
        returns the panchaka rahita
        bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return list of panchaka rahita muhurtha 
            format [ (0 or panchaka reminder code, begin_time_float, end_time_float) ...]
    """
    # 1. Fetch your Udaya Lagna Muhurtha windows
    ulm = udhaya_lagna_muhurtha(jd, place)
    
    # Reminders that match active Panchaka flaws
    bad_panchakas = {1, 2, 4, 6, 8}
    pr = []
    
    # Calculate local civil midnight to accurately convert civil hours back to absolute JD
    jd_midnight = int(jd + 0.5) - 0.5 
    
    for asc, asc_beg, asc_end in ulm:
        # 2. Dynamic Time: Find the absolute Julian Day timestamp when this specific Lagna begins
        jd_window = jd_midnight + (asc_beg / 24.0)
        
        # 3. Fetch panchaka components at this EXACT moment in time
        _tithi = tithi(jd_window, place)[0] + 1
        _nak = nakshatra(jd_window, place)[0]             # Assumed 1-indexed from your setup
        _day = vaara(jd_window, place) + 1                # Sunday=1, Monday=2, etc.
        _asc_rasi = asc + 1                               # Aries=1, Taurus=2, etc.
        
        # 4. Apply the Modulo 9 structural formula
        rem = (_tithi + _nak + _day + _asc_rasi) % 9
        
        # 5. Filter or flag the interval
        if rem in bad_panchakas:
            # Flawed window (Returns the specific Panchaka remainder code)
            pr.append((rem, asc_beg, asc_end))
        else:
            # Panchaka Rahitha window (Clean and auspicious!)
            pr.append((0, asc_beg, asc_end))
            
    return pr
def next_panchaka_days(jd,place):
    """
        Start and end of the panchaka (panchak nakshatras) period
        The five Panchak Nakshatras are: 3rd and 4th pada of Dhanishta, Shatabisha, Purva Bhadrapada, Uttara Bhadrapada, Revati.
        The period starts when the Moon enters Kumbha (Aquarius) (Dhanishta 3rd paadham) and ends when the Moon enters Aries (end of Revathi)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: (start, end), each (year, month, day, float hours): the next Moon entries into Aquarius and into Aries
    """
    panchaka_start_jd = next_planet_entry_date(const._MOON, jd, place, raasi=const.AQUARIUS+1)[0]
    panchaka_end_jd = next_planet_entry_date(const._MOON, jd, place, raasi=const.ARIES+1)[0]
    return utils.jd_to_gregorian(panchaka_start_jd), utils.jd_to_gregorian(panchaka_end_jd)
def chandrashtama(jd, place):
    jd_utc = jd - place.timezone/24.
    moon_long = lunar_longitude(jd_utc, place); moon = dasavarga_from_long(moon_long)[0]
    _chandrashtama_rasi = (moon-7)%12+1
    next_moon_jd = next_planet_entry_date(const._MOON, jd, place)[0]
    return _chandrashtama_rasi, next_moon_jd
def nava_thaara_old(jd,place,from_lagna_or_moon=None):
    if from_lagna_or_moon is None: from_lagna_or_moon = const.NAVA_THARA.FROM_LAGNA
    base_star = ( nakshatra(jd, place)[0]-1 if from_lagna_or_moon==const.NAVA_THARA.FROM_MOON
                  else ascendant(jd,place)[2]-1 )
    ntl = [[(base_star+s)%27 for s in star_list] for _, star_list in const.nakshathra_lords.items()]
    return [(lord,sl) for sl in ntl for lord,csl in const.nakshathra_lords.items() if sorted(sl)==sorted(csl) ]
def _nava_thaara_from_planet_longitude(planet_longitude):
    base_star = nakshatra_pada(planet_longitude)[0]-1
    ntl = [[(base_star+s)%27 for s in star_list] for _, star_list in const.nakshathra_lords.items()]
    result = [(lord,sl) for sl in ntl for lord,csl in const.nakshathra_lords.items() if sorted(sl)==sorted(csl) ]
    return result
def _special_thaara_from_planet_longitude(planet, planet_longitude):
    # Get 1-based nakshatra index and convert to 0-based (0 to 26 for standard 27)
    base_star = nakshatra_pada(planet_longitude)[0] - 1
    
    # Fix: Both Lagna and planets must use the same base increment (-1) 
    # so that the Janma star correctly matches the reference body's actual nakshatra.
    base_inc = -1 
    
    # Adjust base star index if it lies on or past Abhijit in the 28-star arrangement
    if base_star >= const._ABHIJITH_STAR_INDEX:
        base_star += 1
        
    stl = [(base_star + s + base_inc) % 28 for s in const.special_thaara_map]
    
    return [
        (lord, star - 1 if star > const._ABHIJITH_STAR_INDEX else star) 
        for star in stl 
        for lord, csl in const.special_thaara_lords_1.items() 
        if star in csl
    ]
def nava_thaara(jd,place,base_star_planet=None):
    if base_star_planet is None: base_star_planet = const._ascendant_symbol
    if base_star_planet not in [const._ascendant_symbol]+const.SUN_TO_KETU:
        raise ValueError("Base star planet should be either 'L' or 0 (Sun) to 8(Ketu)")
    if base_star_planet == const._ascendant_symbol:
        asc =  ascendant(jd,place)
        _planet_longitude = asc[0]*30+asc[1] 
    else:
        p_swe = ephemeris_planet_index(base_star_planet)
        jd_utc = jd - place.timezone/24.0
        _planet_longitude = sidereal_longitude(jd_utc,p_swe, place)
    return _nava_thaara_from_planet_longitude(_planet_longitude)
def special_thaara_old(jd,place,from_lagna_or_moon=0):
    """
        Note: the star list includes Abhijith as 21st star
    """
    base_star = nakshatra(jd, place)[0]-1 if from_lagna_or_moon==1 else ascendant(jd,place)[2]-1
    base_inc = -1  if from_lagna_or_moon==1 else 0
    stl = [(base_star+s+base_inc)%28 for s in const.special_thaara_map]
    _star_list = utils.get_nakshathra_list_with_abhijith()
    if base_star+1 > const._ABHIJITH_STAR_INDEX: base_star += 1
    return [(lord,star) for star in stl for lord, csl in const.special_thaara_lords_1.items() if star in csl]
def special_thaara(jd,place,base_star_planet=None):
    if base_star_planet is None: base_star_planet = const._ascendant_symbol
    if base_star_planet not in [const._ascendant_symbol]+const.SUN_TO_KETU:
        raise ValueError("Base star planet should be either 'L' or 0 (Sun) to 8(Ketu)")
    if base_star_planet == const._ascendant_symbol:
        asc = ascendant(jd,place)
        planet_longitude = asc[0] * 30 + asc[1]
    else:
        p_swe = ephemeris_planet_index(base_star_planet)
        jd_utc = jd - place.timezone/24.0
        planet_longitude = sidereal_longitude(jd_utc,p_swe, place)
    return _special_thaara_from_planet_longitude(base_star_planet, planet_longitude)
def karaka_tithi(jd,place):
    """
        Karaka Tithi: the tithi formed between the Atma Karaka and the Amatya Karaka (the chara karaka
        scheme's two highest-ranked planets by degree-within-sign), rather than the usual Moon/Sun pair.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: same shape as tithi(): [tithi number, start time, end time, ...]
    """
    pp = [['L',(0,-10)]]+dhasavarga(jd, place) # Dummy Lagna Positions added
    from jhora.horoscope.chart.house import chara_karakas
    ks = chara_karakas(pp)
    p1 = [k for k,v in planet_list.items() if v==ks[1]][0]
    p2 = [k for k,v in planet_list.items() if v==ks[0]][0]
    kt = tithi(jd, place, tithi_index=1, planet1=p1, planet2=p2)
    return kt
def karaka_yogam(jd,place):
    """
        returns the yogam at julian day/time, formed between the Atma Karaka and the Amatya Karaka (the
        chara karaka scheme's two highest-ranked planets by degree-within-sign), rather than the usual
        Moon/Sun pair.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left, 
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          next yogam index and next yogam time is additionally returned if two yogams on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
    pp = [['L',(0,-10)]]+dhasavarga(jd, place) # Dummy Lagna Positions added
    from jhora.horoscope.chart import house
    ks = house.chara_karakas(pp)
    p1 = [k for k,v in planet_list.items() if v==ks[1]][0]
    p2 = [k for k,v in planet_list.items() if v==ks[0]][0]
    return yogam(jd, place, tithi_index=1, planet1=p1, planet2=p2, cycle=1)
def fraction_moon_yet_to_traverse(jd,place,round_to_digits=5):
    jd_utc = jd - place.timezone/24.
    one_star = 360/27
    moon_long = lunar_longitude(jd_utc, place)
    _,_,rem = nakshatra_pada(moon_long)
    moon_fraction_yet_to_traverse = (one_star-rem)/one_star
    return moon_fraction_yet_to_traverse#round(moon_fraction_yet_to_traverse,round_to_digits)
def shiva_vaasa(jd,place,method=2):
    """ 
        Ref: https://vijayalur.com/2014/07/24/shiva-agni-vasa/
        Method=1: general from tithi table
        Method=2: for rudrabisheka
        Method: 1
            Tithis              Shiva’s Place                 Result
            1, 8 & 15           In Cemetery                   Death
            2, 9 & 30           With Gowri                    Happiness & Wealth
            3 & 10              In assembly                   Grief
            4 & 11              At work / play                Difficulty
            5 & 12              At Kailash                    Happiness
            6 & 13              Mounted on Vrishabha (Nandi)  Success
            7 & 14              At Dinner / Meditation        Trouble (Peeda)
        Method: 2
            (tithi_index (1 to 30) * 2 + 5) / 7 => Get Remainder
            {1: 5-Kailash 2: 2-With Gowri 3: 6-Mounted on Nandi 4: 3-In assembly
            5: 7-At dinner / meditation 6: 4-At work / play 0: 1-In cemetry
        @return shiva_vaasa_index (1:In Cemetery,2:With Gowri, 3:In assembly, 4:At work / play
                                   5:At Kailash, 6:Mounted on Vrishabha (Nandi), 7:At Dinner / Meditation
    """
    tit = tithi(jd,place); tithi_index = tit[0]; t_end = tit[2]
    _place_dict1 = {1:1,2:2,3:3,4:4,5:5,6:6,7:7,
                    8:1,9:2,10:3,11:4,12:5,13:6,14:7,
                    16:1,17:2,18:3,19:4,20:5,21:6,22:7,
                    23:1,24:2,25:3,26:4,27:5,28:6,29:7,
                    15:1,30:2}
    _place_dict2 = {0:1,1:5,2:2,3:6,4:3,5:7,6:4}
    _place_dict = _place_dict1 if method==1 else _place_dict2
    return _place_dict1[tithi_index] if method==1 else _place_dict2[(tithi_index*2+5) % 7],t_end
def agni_vaasa(jd,place):
    """
        
        @return agni_vaasa_index 
            1:Prithvi (Earth) - bestow comfort, 
            2:Akaasha (Space) - life threatening
            3:PaathaaLa (Nadir) - destroy wealth
    """
    tit = tithi(jd,place); tithi_index = tit[0]; t_end = tit[2]
    day = vaara(jd,place)+1
    _av_list = [1,2,3,1]
    return _av_list[(tithi_index+1+day)%4], t_end
def pushkara_yoga(jd, place):
    """
        returns dwi/tri pushkara yoga if exists
        @return 
            0,'',1/-1: No Dwi/Tri pushkara yoga
            1,time,1/-1: dwi pushakara yoga
            2,time,1/-1: tri pushkara yoga
                last element 1 means from time
                            -1 means to time
    """
    _tithi_list = [2, 17, 7, 22, 12, 27]; _day_list = [1,3,7]
    _dwi_star_list = [5, 14, 23]; _tri_star_list = [16, 7, 3, 11, 21, 25]
    tit = tithi(jd, place); _t_no = tit[0]; _t_start = tit[1]; _t_end = tit[2]
    day = vaara(jd,place)+1
    nk = nakshatra(jd, place);nak = nk[0]; _n_start = nk[2]; _n_end = nk[3]
    srise1 = sunrise(jd,place)[0]; srise2 = sunrise(jd+1,place)
    ptimes = ()
    chkd = day in _day_list
    chkt = _t_no in _tithi_list or (_t_no+29)%30 in _tithi_list
    if chkd and chkt:
        chkn11 = nak in _dwi_star_list; chkn12 = (nak+26)%27 in _dwi_star_list
        if chkn11 or chkn12:
            ptimes = (1,_n_start,srise2) if chkn11 else (1,srise1,_n_start)
        chkn21 = nak in _tri_star_list; chkn22 = (nak+26)%27 in _tri_star_list
        if chkn21 or chkn22:
            ptimes = (2,_n_start,srise2) if chkn11 else (2,srise1,_n_start)
    return ptimes
def aadal_yoga(jd,place):
    jd_utc = jd - place.timezone/24.
    nak = nakshatra(jd, place); star_end = nak[3]
    moon_star = nakshatra_pada(lunar_longitude(jd_utc, place))[0]
    sun_star = nakshatra_pada(solar_longitude(jd_utc, place))[0]
    srise = sunrise(jd,place)[0]
    knt = utils.cyclic_count_of_stars_with_abhijit_in_22(const.abhijit_order_of_stars, sun_star-1,moon_star-1)
    #print(moon_star,sun_star,knt,'in',[2,7,9,14,16,21,23,28])
    return (srise,star_end) if knt in [2,7,9,14,16,21,23,28] else ()
def vidaal_yoga(jd,place):
    jd_utc = jd - place.timezone/24.
    nak = nakshatra(jd, place); star_end = nak[3]
    moon_star = nakshatra_pada(lunar_longitude(jd_utc, place))[0]
    sun_star = nakshatra_pada(solar_longitude(jd_utc, place))[0]
    srise = sunrise(jd,place)[0]
    knt = utils.cyclic_count_of_stars_with_abhijit_in_22(const.abhijit_order_of_stars, sun_star-1,moon_star-1)
    #print(moon_star,sun_star,knt,'in',[3,6,10,13,17,20,24,27])
    return (srise,star_end) if knt in [3,6,10,13,17,20,24,27] else ()
def disha_shool(jd,place):
    return const.disha_shool_map[vaara(jd,place)]
def yogini_vaasa(jd,place):
    tithi_index = tithi(jd,place)[0]
    return const.yogini_vaasa_tithi_map[tithi_index-1]
def vedic_time_equal_day_night_ghati(jd,place,float_hours=None,
                                                    vedic_hours_per_day=60):
    """
        @param vedic_hours_per_day = 30 (Muhurthas) or 60 (Ghati)
        This feature is for experimental purpose. 
        Some panchang websites like drikpanchang may force 30 ghatis for both day and night
        so that sunset is always equals to 30 ghati. 
        But traditionally vedic praharas are unequal when day/nights are unequal
        So use this function with caution
    """
    if vedic_hours_per_day not in [30,60]: vedic_hours_per_day = 60
    _half_vedic_hour_per_day = vedic_hours_per_day/2
    _DEBUG_ = False
    if float_hours is None:
        if _DEBUG_: print('getting float hours from jd')
        _, _, _, float_hours = utils.jd_to_gregorian(jd)
    if _DEBUG_: print('float_hours',float_hours)
    today_sunrise = sunrise(jd, place)[0]; today_sunset = sunset(jd,place)[0]
    _day_length = day_length(jd, place); _night_length = night_length(jd, place)
    if _DEBUG_: print('today_sunrise',today_sunrise,'today_sunset',today_sunset)
    day_ghati_per_hour = _half_vedic_hour_per_day / _day_length
    night_ghati_per_hour = _half_vedic_hour_per_day / _night_length
    if _DEBUG_: print('day_ghati_per_hour',day_ghati_per_hour,'night_ghati_per_hour',night_ghati_per_hour)
    if float_hours <= today_sunset and float_hours >= today_sunrise:
        if _DEBUG_: print('float hours in day time')  
        ghati_hours = float_hours - today_sunrise
        if ghati_hours < 0:
            ghati_hours += 24
        total_ghati = ghati_hours * day_ghati_per_hour
    else:
        if _DEBUG_: print('float hours in night time')
        total_ghati = _half_vedic_hour_per_day + (float_hours-today_sunset)*night_ghati_per_hour if float_hours>=today_sunset \
                        else vedic_hours_per_day - (today_sunrise-float_hours)*night_ghati_per_hour
    total_ghati = total_ghati % vedic_hours_per_day  # Reset to 0 after 60 ghatis

    ghati = int(total_ghati)
    phala = int((total_ghati - ghati) * vedic_hours_per_day)
    vighati = int(((total_ghati - ghati) * vedic_hours_per_day - phala) * vedic_hours_per_day)

    return int(ghati), int(phala), int(vighati)
def vedic_time(jd, place, float_hours=None, force_equal_day_night_ghati=True,
                              vedic_hours_per_day=60):
    """
        @param vedic_hours_per_day = 30 (Muhurthas) or 60 (Ghati)
        @return (ghati, phala, vighati) for the given jd and place
        force_equal_day_night_ghati = True will force equal 30 ghatis for day and night.
        This feature is for experimental purpose. 
        Some panchang websites like drikpanchang may force 30 ghatis for both day and night
        so that sunset is always equals to 30 ghati. 
        But traditionally vedic praharas are unequal when day/nights are unequal
        So use this function with caution. 
        Also enabling this feature in vedic clock will show unqual hand movements
    """
    if vedic_hours_per_day not in [30, 60]: vedic_hours_per_day = 60
    if force_equal_day_night_ghati: return vedic_time_equal_day_night_ghati(jd, place, float_hours)
    if float_hours is None:
        _, _, _, float_hours = utils.jd_to_gregorian(jd)

    sunrise_1 = sunrise(jd, place)[0]

    # evaluation sunrise baselines
    if float_hours < sunrise_1:
        sunrise_0 = sunrise(jd - 1, place)[0] - 24  # yesterday sunrise on a continuous timeline
        sunrise_2 = sunrise_1                        # "end" is today's sunrise
    else:
        sunrise_2 = 24 + sunrise(jd + 1, place)[0]  # tomorrow sunrise on a continuous timeline
        sunrise_0 = sunrise_1                        # "start" is today's sunrise

    ghati_per_hour = vedic_hours_per_day / (sunrise_2 - sunrise_0)
    # ---- CHANGE ENDS HERE ----

    local_hours_since_sunrise = float_hours - sunrise_1
    if local_hours_since_sunrise < 0:
        local_hours_since_sunrise += 24

    total_ghati = local_hours_since_sunrise * ghati_per_hour
    total_ghati = total_ghati % vedic_hours_per_day  # Reset to 0 after 60 ghatis

    ghati = int(total_ghati)
    phala = int((total_ghati - ghati) * vedic_hours_per_day)
    vighati = int(((total_ghati - ghati) * vedic_hours_per_day - phala) * vedic_hours_per_day)

    return int(ghati), int(phala), int(vighati)
def next_solar_month(jd,place,raasi=None):
    """
        Next solar month is when Sun Enters a next zodiac/raasi
    """
    return next_planet_entry_date(0, jd, place,raasi=raasi)
def previous_solar_month(jd,place,raasi=None):
    """
        Previous solar month is when Sun Enters a previous/current zodiac/raasi
    """
    return previous_planet_entry_date(0, jd, place,raasi=raasi)
def next_solar_year(jd,place):
    """
        Next solar month is when Sun Enters Aries
    """
    return next_planet_entry_date(0, jd, place,raasi=1)
def previous_solar_year(jd,place):
    """
        Previous solar month is when Sun Enters Aries
    """
    return previous_planet_entry_date(0, jd, place, raasi=1)
def next_lunar_year(jd,place,lunar_month_type=None,direction=1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type is None: lunar_month_type = const.LUNAR_MONTH_TYPE.AMANTHA
    _DEBUG_= False
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(next_solar_year(jd, place)[0]); 
        return Date(lmy,lmm,lmd),lmh
    for _ in range(13):
        lmy,lmm,lmd,lmh = next_lunar_month(jd, place, lunar_month_type) if direction==1 else previous_lunar_month(jd, place, lunar_month_type)
        #tithi_ = tithi(jd,place)[0]
        #lmy,lmm,lmd,lmh = utils.jd_to_gregorian(new_moon(jd,tithi_,opt=direction)) if lunar_month_type==0 else utils.jd_to_gregorian(full_moon(jd,tithi_,opt=direction))
        if _DEBUG_: print(lunar_month_type,(lmy,lmm,lmd),lmh)
        jd = utils.julian_day_number(Date(lmy,lmm,lmd), (lmh,0,0))
        lm = lunar_month_date(jd, place, use_purnimanta_system=(lunar_month_type==const.LUNAR_MONTH_TYPE.PURNIMANTHA))
        if _DEBUG_: print('lunar month date',lm)
        _lunar_month_number=((lm[0]+1)%12 if lm[1]==30 else lm[0]) ##<<< TODO: Something wrong lm[-1] is not lunar day
        _lunar_month_start = 1
        if _lunar_month_number==_lunar_month_start:
            _tithi = tithi(jd,place)
            if _DEBUG_: print('found lunar year date',_tithi)
            if _DEBUG_: print('before lm',lm)
            if lm[-1]>1 and direction==1:
                if _DEBUG_: print('lunar month day is >1',lm[-1])
                lmy,lmm,lmd = utils.previous_panchanga_day(Date(lmy,lmm,lmd), minus_days=1)
                lm_jd = utils.julian_day_number(Date(lmy,lmm,lmd),(lmh,0,0))
                _tithi = tithi(lm_jd,place)
                lmh = _tithi[2]
                if _DEBUG_: print('after lm',lunar_month_date(jd-1, place,
                                        use_purnimanta_system=(lunar_month_type==const.LUNAR_MONTH_TYPE.PURNIMANTHA)))
            elif _tithi[1] < 0 and (_tithi[0]==1 or _tithi[0]==16) and direction==1:
                if _DEBUG_: print('tithi on lunar year day starts previous day',_tithi[1])
                lmy,lmm,lmd = utils.previous_panchanga_day(Date(lmy,lmm,lmd), minus_days=1)
                lmh = abs(_tithi[1])
            return Date(lmy,lmm,lmd),lmh
        jd += direction*14
    if _DEBUG_: print('next/prev lunar_year could not be found')
def previous_lunar_year(jd,place,lunar_month_type=None):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type is None: lunar_month_type = const.LUNAR_MONTH_TYPE.AMANTHA
    _DEBUG_ = False
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(previous_solar_year(jd, place)[0]); 
        return Date(lmy,lmm,lmd),lmh
    return next_lunar_year(jd, place, lunar_month_type, direction=-1)
special_tithis = lambda jd,place: [[tithi(jd, place, tithi_index=t,cycle=c) for t in range(1,13)] for c in range(1,4)]
def is_night_birth(jd, place):
    """
    Night birth = (birth_time >= sunset on birth date) or (birth_time < sunrise on birth date).
    Assumptions:
      - utils.jd_to_gregorian(jd) returns local date and local float hours for the birth place/time.
      - drik.sunrise/sunset return local float hours (as first item in their tuple) for that date and place.
    """
    _, _, _, birth_hours = utils.jd_to_gregorian(jd)
    sunrise_hours = sunrise(jd, place)[0]
    sunset_hours  = sunset(jd, place)[0]
    return (birth_hours >= sunset_hours) or (birth_hours < sunrise_hours)
def ardra_pravesha_date(jd,place,direction=1,increment_speed_factor=0.01,precision=0.1):
    return next_planet_nakshathra_pravesha_date(planet=const.SUN_ID, nakshathra=6, jd=jd, place=place, direction=direction,
                                                increment_speed_factor=increment_speed_factor, precision=precision)
def next_planet_nakshathra_pravesha_date(planet,nakshathra,jd,place,direction=1,increment_speed_factor=0.01,
                                          precision=0.1):
    """
        get the date when a planet enters a zodiac
        @param planet: planet index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param direction: 1= next entry, -1 previous entry
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param precision: precision in degrees within which longitude entry whould be (default: 0.1 degrees)
        @param raasi: raasi at which planet should enter. 
            If raasi==None: gives entry to next constellation
            If raasi is specified [1..12] gives entry to specified constellation/raasi
        @return Julian day number of planet entry into zodiac
    """
    multiple = 360.0/27.0*(nakshathra-1)
    p_swe = ephemeris_planet_index(planet)
    p_speed = daily_planet_speed(jd,place,planet)
    if abs(p_speed)<1.e-6: p_speed = 0.1 # Keep some non-zero speed
    jd_utc = jd - place.timezone/24.0
    increment_days = increment_speed_factor/p_speed
    if planet in [const.RAHU_ID,const.KETU_ID]: direction *= -1 # Rahu/Ketu always in reverse direction
    sl = sidereal_longitude(jd_utc,p_swe, place)
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        jd += increment_days*direction; jd_utc = jd - place.timezone/24.0
        sl = sidereal_longitude(jd_utc,p_swe, place)
    sank_date = jd_to_gregorian(jd_utc)
    sank_sunrise = sunrise(jd_utc,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    planet_longs = []
    for t in offsets:
        sl = sidereal_longitude(sank_sunrise+t,p_swe, place)
        planet_longs.append(sl)
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    planet_hour1 = (sank_sunrise + planet_hour - sank_jd_utc)*24+place.timezone
    sank_jd_utc += planet_hour1/24.0
    planet_long = sidereal_longitude(sank_jd_utc-place.timezone/24,p_swe, place)
    y,m,d,fh = jd_to_gregorian(sank_jd_utc); sank_date = Date(y,m,d); planet_hour1 = fh
    return sank_jd_utc,planet_long
def next_planet_entry_date_general(jd, place, planet, planet_longitude=None, nakshathra=None, raasi=None, direction=1,
                                    increment_speed_factor=0.001, precision=0.1, divisional_chart_factor=1,
                                    increment_days=0.01):
    """
    Optimized general entry date finder for custom longitudes, nakshatras, or raasis.
    Uses Kinematic Bracketing, False Position, and Exact Linear Interpolation.
    """
    jd_utc = jd - place.timezone / 24.0
    
    # 1. Handle Ascendant delegation
    if planet == const._ascendant_symbol:
        ret_jd, ret_long = next_ascendant_entry_date(
            jd=jd, place=place, direction=direction, raasi=raasi, 
            precision=max(precision, 0.1), divisional_chart_factor=divisional_chart_factor
        )
        return ret_jd, ret_long
        
    p_swe = ephemeris_planet_index(planet)
    
    # 2. Handle Rahu/Ketu delegation for standard constellation entry
    if planet_longitude is None and nakshathra is None and planet in [const.RAHU_ID, const.KETU_ID]:
        ret_jd, ret_long = next_planet_entry_date(planet, jd, place, direction, raasi=raasi)
        return ret_jd, ret_long

    # 3. Determine target boundary precisely
    if planet_longitude is not None: 
        multiple = planet_longitude
    elif nakshathra is not None: 
        multiple = (nakshathra - 1) * (360.0 / 27.0)
    elif raasi is not None: 
        multiple = (raasi - 1) * 30.0
    else:
        p_long = sidereal_longitude(jd_utc, p_swe, place)
        multiple = (((p_long // 30) + 1) % 12) * 30.0
        if direction == -1: 
            multiple = (p_long // 30) * 30.0

    target_long = multiple % 360.0

    def get_diff(t):
        sl = sidereal_longitude(t, p_swe, place)
        diff = (sl - target_long) % 360.0
        if diff > 180.0: 
            diff -= 360.0
        return diff

    # 4. Kinematic Maximum Speeds (degrees per day)
    max_speeds = {
        const._MOON: 15.5,
        const._SUN: 1.05,
        const._MERCURY: 2.5,
        const._VENUS: 1.3,
        const._MARS: 0.85,
        const._JUPITER: 0.26,
        const._SATURN: 0.13,
        const._RAHU: 0.07
    }
    max_speed = max_speeds.get(p_swe, 2.0)
    
    bracket_steps = {
        const._MOON: 0.25,
        const._SUN: 2.0,
        const._MERCURY: 1.0,
        const._VENUS: 1.0,
        const._MARS: 3.0,
        const._JUPITER: 5.0,
        const._SATURN: 10.0,
        const._RAHU: 10.0
    }
    safe_bracket = bracket_steps.get(p_swe, 1.0) * direction

    t0 = jd_utc
    diff0 = get_diff(t0)

    # Nudge forward slightly if starting exactly on target
    if abs(diff0) < 0.0001:
        t0 += (0.01 * direction)
        diff0 = get_diff(t0)

    t1 = t0
    diff1 = diff0

    # Phase 1: Kinematic Predictive Bracketing
    for _ in range(1000):
        distance = abs(diff1)
        if distance > 3.0:
            step = (distance / max_speed) * 0.85 * direction
        else:
            step = safe_bracket
            
        t1 += step
        diff1 = get_diff(t1)
        
        if diff0 * diff1 <= 0 and abs(diff0) < 45: 
            break
            
        t0 = t1
        diff0 = diff1
    else:
        raise ValueError(f"Could not find transit for planet {planet} within search limits.")

    # Phase 2: False Position Root-Finding to narrow to ~1 minute
    precision_days = 0.001 

    while abs(t1 - t0) > precision_days:
        if diff1 - diff0 == 0:
            t_mid = (t0 + t1) / 2.0
        else:
            t_mid = t1 - diff1 * (t1 - t0) / (diff1 - diff0)
            
        diff_mid = get_diff(t_mid)
        
        if abs(diff_mid) < 0.000001:
            t0 = t_mid
            t1 = t_mid
            break
            
        if diff0 * diff_mid < 0:
            t1 = t_mid
            diff1 = diff_mid
        else:
            t0 = t_mid
            diff0 = diff_mid

    # Phase 3: Exact Linear Interpolation for Sub-Arcsecond Precision
    if diff1 - diff0 != 0:
        exact_jd_utc = t0 - diff0 * (t1 - t0) / (diff1 - diff0)
    else:
        exact_jd_utc = (t0 + t1) / 2.0

    exact_long = sidereal_longitude(exact_jd_utc, p_swe, place)
    exact_jd = exact_jd_utc + place.timezone / 24.0
    return exact_jd, exact_long
def next_planet_entry_date_general_old(jd,place,planet,planet_longitude=None,nakshathra=None,raasi=None,direction=1,
                            increment_speed_factor=0.001,precision=0.1,divisional_chart_factor=1,
                            increment_days=0.01):
    """
        get the date when a planet enters a zodiac or nakshathra or a given longitude
        @param jd: julian day 
        @param planet: planet index (0=Sun..8=Kethu)
        @param place: Place struct ('place',latitude,longitude,timezone)
        Specify one of:
            @param planet_longitude: specific longitude of the planet
            @param nakshathra: Planet coinciding with a specified nakshathra (1 to 27)
            @param raasi: raasi at which planet should enter. 
                If raasi==None: gives entry to next constellation
                If raasi is specified [1..12] gives entry to specified constellation/raasi
        @param direction: 1= next entry, -1 previous entry
        @param increment_speed_factor: speed adjustment factor 
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param precision: precision in degrees within which longitude entry whould be (default: 0.1 degrees)
        @param divisional_chart_factor: varga chart index (default= 1 = Raasi chart) 
        @return (year,month,day,float_hours),planet_longitude
    """
    jd_utc = jd - place.timezone/24.0
    p_swe = ephemeris_planet_index(planet)
    if planet_longitude is None and nakshathra is None:
        if planet==const._ascendant_symbol:
            """ Do not decrease precision below 0.5 or even 0.1 Asc entry values are sensitive """
            return next_ascendant_entry_date(jd=jd, place=place, direction=direction,raasi=raasi, precision=0.5,
                                             divisional_chart_factor=divisional_chart_factor)
        if planet in [const.RAHU_ID,const.KETU_ID]:# and direction ==-1:
            return next_planet_entry_date(planet,jd, place, direction,raasi=raasi,increment_days=increment_days)
    if planet_longitude is not None: multiple = planet_longitude
    elif nakshathra is not None: multiple = (nakshathra-1)*(360/27.0)
    elif raasi is not None: multiple = (raasi-1)*30
    else:
        p_long = sidereal_longitude(jd_utc, p_swe, place)
        multiple = (((p_long//30)+1)%12)*30
        if direction==-1: multiple = (p_long//30)%12*30
    p_speed = daily_planet_speed(jd,place,planet)
    #if abs(p_speed)<1.e-6: p_speed = 0.1 # Keep some non-zero speed
    increment_days = increment_speed_factor/p_speed 
    if planet in [const.RAHU_ID,const.KETU_ID]: direction *= -1 # Rahu/Ketu always in reverse direction
    sl = sidereal_longitude(jd_utc,p_swe, place)
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        jd += increment_days*direction; jd_utc = jd - place.timezone/24.0
        sl = sidereal_longitude(jd_utc,p_swe, place)
    sank_date = jd_to_gregorian(jd_utc)
    sank_sunrise = sunrise(jd_utc,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    planet_longs = []
    for t in offsets:
        sl = sidereal_longitude(sank_sunrise+t,p_swe, place)
        planet_longs.append(sl)
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    planet_hour1 = (sank_sunrise + planet_hour - sank_jd_utc)*24+place.timezone
    sank_jd_utc += planet_hour1/24.0
    planet_long = sidereal_longitude(sank_jd_utc-place.timezone/24,p_swe, place)
    y,m,d,fh = jd_to_gregorian(sank_jd_utc); sank_date = Date(y,m,d); planet_hour1 = fh
    return sank_jd_utc,planet_long
def _get_next_raasi(pl,sl,direction=1):
    _next_raasi = int(((sl//30)+1)%12)
    if direction==-1: _next_raasi = int((sl//30)%12)
    if pl == const._RAHU:
        _next_raasi = int((sl//30)%12)
        if direction==-1:
            _next_raasi = int((sl//30+1)%12)
    #print(pl,sl,_next_raasi)
    return _next_raasi
def true_sidereal_year(jd,place,round_to_digits=6):
    """
        Sidereal Year = Duration earth takes to complete one revoultion around the sun relative fixed stars (Ayanamsa applied)
        returns duration in float up to six digits by default e.g. const.sidereal_year
    """
    jd_sid1,_ = previous_planet_entry_date(const.SUN_ID, jd, place, raasi=1)
    jd_sid2,_ = next_planet_entry_date(const.SUN_ID, jd, place, raasi=1)
    return jd_sid2-jd_sid1# round(jd_sid2-jd_sid1,round_to_digits)
def tithi_year(jd,place,round_to_digits=6):
    ps_date,psh = previous_lunar_year(jd, place, lunar_month_type=const.LUNAR_MONTH_TYPE.AMANTHA)
    jd_prev = utils.julian_day_number(ps_date,(psh,0,0))
    ps_date,psh = next_lunar_year(jd, place, lunar_month_type=const.LUNAR_MONTH_TYPE.AMANTHA)
    jd_next = utils.julian_day_number(ps_date,(psh,0,0))
    return jd_next-jd_prev# round(jd_next-jd_prev,round_to_digits)
def lunar_year(jd,place,round_to_digits=6):
    """
        duration of 12 full cycles of moon ~= 354 days
        returns duration in float up to six digits by default e.g. const.lunar_year
    """
    return const.lunar_year # round(const.lunar_year,round_to_digits)
def savana_year(jd,place,round_to_digits=6,savana_year_method=None):
    """ 
        Returns savana year = duration of 360 sunrise days
        savana_method = -1 (jd-360 to jd) # const.SAVANA_METHOD.RETROSPECTIVE
        savana_method = 0 (jd-180 to jd+180) # const.SAVANA_METHOD.MIDPOINT
        savana_method = 1 (jd to jd+360) # const.SAVANA_METHOD.PROSPECTIVE_0_to_360_JHORA
    """
    if savana_year_method is None: savana_year_method = const.savana_year_method_default
    jd1 = ( jd if savana_year_method==const.SAVANA_YEAR_METHOD.PROSPECTIVE_0_to_360_JHORA 
            else (jd-180 if savana_year_method==const.SAVANA_YEAR_METHOD.MIDPOINT else jd-360) )
    jd2 = ( jd+360 if savana_year_method==const.SAVANA_YEAR_METHOD.PROSPECTIVE_0_to_360_JHORA 
            else (jd+180 if savana_year_method==const.SAVANA_YEAR_METHOD.MIDPOINT else jd) )
    jd1_rise = sunrise(jd1,place)[-1]
    jd2_rise = sunrise(jd2,place)[-1]
    return jd2_rise-jd1_rise# round(jd2_rise-jd1_rise,round_to_digits)
def _tithi_number_at_jd(jd, place):
    """
    Return instantaneous tithi number at JD.

    Assumes tithi(jd, place, force_tithi_at_sunrise=False)[0]
    returns tithi number 1..30 at the exact JD.
    """
    return int(tithi(jd, place, force_tithi_at_sunrise=False)[0])
def _tithi_boundary_jd(
    jd,
    place,
    direction=+1,
    step_days=0.2,
    max_days=2.0,
    iterations=24,
):
    """
    Find the nearest tithi boundary relative to `jd`.

    Parameters
    ----------
    jd : float
        Julian day
    place : object
        Location / place object used by tithi()
    direction : int
        +1 -> next boundary after jd
        -1 -> previous boundary before jd
    step_days : float
        Scan step in days
    max_days : float
        Maximum scan distance in the chosen direction
    iterations : int
        Number of bisection iterations

    Returns
    -------
    float
        JD of the boundary
    """
    if direction not in (+1, -1):
        raise ValueError("direction must be +1 (next) or -1 (previous)")

    eps = 1.0 / 86400.0
    sign = 1.0 if direction > 0 else -1.0

    # Start just away from jd to avoid landing exactly on boundary
    current = jd + sign * eps
    t_current = _tithi_number_at_jd(current, place)

    probe = current + sign * step_days
    limit = current + sign * max_days

    def within_limit(x):
        return x <= limit if sign > 0 else x >= limit

    while within_limit(probe):
        t_probe = _tithi_number_at_jd(probe, place)

        if t_probe != t_current:
            # Arrange bracket so:
            #   t(lo) = old tithi
            #   t(hi) = new tithi
            if sign > 0:
                lo, hi = current, probe
                t_lo = t_current
            else:
                lo, hi = probe, current
                t_lo = t_probe

            for _ in range(iterations):
                mid = (lo + hi) / 2.0
                t_mid = _tithi_number_at_jd(mid, place)

                if t_mid == t_lo:
                    lo = mid
                else:
                    hi = mid

            return hi

        current = probe
        t_current = t_probe
        probe += sign * step_days

    raise RuntimeError(
        f"Could not find {'next' if direction > 0 else 'previous'} "
        f"tithi boundary within max_days."
    )
def true_tithi_year(jd, place,true_lunar_year_method=None, round_to_digits=6):
    """
    True duration of 360 actual tithis near the given JD.
    Counts exactly 360 instantaneous tithi transitions.
    """
    if true_lunar_year_method is None: true_lunar_year_method = const.true_lunar_year_method_default
    if true_lunar_year_method == const.TRUE_LUNAR_YEAR_METHOD.TITHI_AT_DOB:
        return _true_tithi_year_same_phase(jd, place, round_to_digits)
    return _true_tithi_year_boundary(jd, place, round_to_digits)
def _true_tithi_year_same_phase(jd, place, round_to_digits=6):
    jd_utc = jd - place.timezone/24
    theta0 = lunar_longitude(jd_utc, place)-solar_longitude(jd_utc, place)
    #print(tithi(jd,place))
    mean_synodic_month = 29.530588853
    seed = jd + 12 * mean_synodic_month - 2.0  # safely before 12th recurrence

    end_jd = next_conjunction_of_planet_pair(
        seed,
        place,
        const.MOON_ID,
        const.SUN_ID,
        direction=1,
        separation_angle=theta0,
        increment_speed_factor=0.25,
        angle_tolerance=0.5,
        finer_angle_tolerance=0.001,
    )[0]
    #print(tithi(end_jd,place))
    return end_jd - jd # round(end_jd - jd, round_to_digits)
def _true_tithi_year_boundary(
    jd,
    place,
    round_to_digits=6,
    months=12,
    mean_synodic_month=29.530588853,
    increment_speed_factor=0.25,
    angle_tolerance=0.5,
    finer_angle_tolerance=0.001,
):
    """
    Fast computation of the true duration of 360 tithis near `jd`.

    This is a faster replacement for counting 360 successive tithi transitions.
    It works by:

      1) finding the previous tithi boundary before `jd`
      2) determining the exact boundary phase angle (multiple of 12 degrees)
      3) finding the next recurrence of that same Moon-Sun separation angle
         near 12 synodic months later

    Parameters
    ----------
    jd : float
        Starting Julian day
    place : Place
        Panchanga place object
    round_to_digits : int
        Final rounding digits
    months : int
        Number of synodic months; default 12 gives 360 tithis
    mean_synodic_month : float
        Mean synodic month in days
    increment_speed_factor : float
        Passed through to next_conjunction_of_planet_pair()
    angle_tolerance : float
        Passed through to next_conjunction_of_planet_pair()
    finer_angle_tolerance : float
        Passed through to next_conjunction_of_planet_pair()

    Returns
    -------
    float
        Duration in days of 360 true tithis

    Notes
    -----
    This assumes that next_conjunction_of_planet_pair(..., separation_angle=x)
    finds the next JD where the *directed* separation angle

        (longitude(p1) - longitude(p2)) % 360

    equals x (within tolerance).

    For tithi logic, that must be a full 0..360 degree phase angle,
    NOT the smallest/unsigned angular separation.
    """
    eps = 1.0 / 86400.0

    # 1) Find the previous tithi boundary before jd
    start_jd = _tithi_boundary_jd(jd, place, direction=-1)

    # 2) Determine which tithi starts immediately after that boundary
    #    If boundary is the start of tithi N, its phase angle is (N-1)*12 degrees.
    t_after = int(tithi(start_jd + eps, place, force_tithi_at_sunrise=False)[0])
    target_angle = ((t_after - 1) * 12.0) % 360.0

    # 3) Seed the phase-angle search safely between the 11th and 12th recurrence
    #    so that "next occurrence" lands on the 12th one, not earlier.
    #
    #    For months=12, this places the seed at 11.5 mean synodic months after start.
    #    That is usually a very safe location.
    seed_jd = start_jd + (months - 0.5) * mean_synodic_month

    # 4) Find the next recurrence of the SAME Moon-Sun phase angle
    end_jd = next_conjunction_of_planet_pair(
        seed_jd,
        place,
        const.MOON_ID,
        const.SUN_ID,
        direction=1,
        separation_angle=target_angle,
        increment_speed_factor=increment_speed_factor,
        angle_tolerance=angle_tolerance,
        finer_angle_tolerance=finer_angle_tolerance,
    )[0]

    return end_jd - start_jd # round(end_jd - start_jd, round_to_digits)
def true_lunar_year(jd, place, true_lunar_year_method=None, round_to_digits=6):
    """
    Alias/wrapper for true_tithi_year.

    True lunar year here means:
        360 actual tithi transitions near the given JD.
    """
    return true_tithi_year(jd, place, true_lunar_year_method, round_to_digits)
def _nanakshahi_civil_date(jd, place=None):
    """
        Fixed-arithmetic Nanakshahi calendar date (original/"Mool" 2003 design by
        Pal Singh Purewal, adopted by SGPC in 1999, formally approved 2003).
        NOT ephemeris-based and NOT sankranti-based -- a pure Gregorian-date-anchored
        lookup table. `place` is accepted only for interface parity with the other
        calendar functions (no sunrise/sunset/longitude computation happens here).
        Epoch: 1 Chet = 14 March every Gregorian year.
        Distinct from the traditional lunisolar Bikrami calendar still used by
        Punjabi Hindus/agrarian communities (see const.SANKRANTI_RULE.ORISSA_RULE,
        which Punjab's Bikrami solar months are documented to follow).
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [month_index(1=Chet..12=Phagun), day(1-based), nanakshahi_year]
    """
    y, m, d, _ = utils.jd_to_gregorian(jd)
    if (m, d) >= (const.nanakshahi_epoch_month, const.nanakshahi_epoch_day):
        cycle_start_greg_year = y
    else:
        cycle_start_greg_year = y - 1
    nanakshahi_year = cycle_start_greg_year - const.nanakshahi_epoch_year_offset
    next_greg_year = cycle_start_greg_year + 1
    is_leap = (next_greg_year % 4 == 0 and (next_greg_year % 100 != 0 or next_greg_year % 400 == 0))
    month_lengths = list(const.nanakshahi_month_lengths)
    if is_leap:
        month_lengths[-1] += 1  # Phagun (last month) absorbs the leap day, never February itself
    epoch_jd = utils.gregorian_to_jd(Date(cycle_start_greg_year, const.nanakshahi_epoch_month,
                                           const.nanakshahi_epoch_day))
    elapsed_days = int(jd) - int(epoch_jd)
    remaining = elapsed_days
    month_idx = len(month_lengths) - 1
    day_number = month_lengths[-1]
    for i, length in enumerate(month_lengths):
        if remaining < length:
            month_idx = i
            day_number = remaining + 1
            break
        remaining -= length
    return [month_idx+1, day_number, nanakshahi_year]
def _bangladesh_reformed_civil_date(jd, place):
    """
        Fixed-arithmetic Bangladesh civil Bangabda date (2019 Bangla Academy revision,
        effective 16 Oct 2019; supersedes the earlier 1966 Saha-committee scheme).
        NOT ephemeris-based and NOT sankranti-based -- a pure Gregorian-date-anchored
        lookup table. `place` is accepted only for interface parity with the other
        calendar functions (no sunrise/sunset/longitude computation happens here).
        Epoch: 1 Boishakh = 14 April every Gregorian year.
        Distinct from West Bengal's traditional sankranti-based Panjika (see
        const.SANKRANTI_RULE.BENGAL_ASSAM_RULE) -- the two routinely land on different
        Gregorian dates for the same named day; that divergence is expected, not a bug.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [month_index(1=Boishakh..12=Choitro), day(1-based), bangla_year]
    """
    y, m, d, _ = utils.jd_to_gregorian(jd)
    if (m, d) >= (const.bangladesh_reformed_epoch_month, const.bangladesh_reformed_epoch_day):
        cycle_start_greg_year = y
    else:
        cycle_start_greg_year = y - 1
    bangla_year = cycle_start_greg_year - const.bangladesh_reformed_year_offset
    falgun_greg_year = cycle_start_greg_year + 1  # Falgun (month 11) falls in Feb/Mar of the following year
    is_leap = (falgun_greg_year % 4 == 0 and (falgun_greg_year % 100 != 0 or falgun_greg_year % 400 == 0))
    month_lengths = list(const.bangladesh_reformed_month_lengths)
    if is_leap:
        month_lengths[10] += 1  # Falgun (index 10) absorbs the leap day
    epoch_jd = utils.gregorian_to_jd(Date(cycle_start_greg_year, const.bangladesh_reformed_epoch_month,
                                           const.bangladesh_reformed_epoch_day))
    elapsed_days = int(jd) - int(epoch_jd)
    remaining = elapsed_days
    month_idx = len(month_lengths) - 1
    day_number = month_lengths[-1]
    for i, length in enumerate(month_lengths):
        if remaining < length:
            month_idx = i
            day_number = remaining + 1
            break
        remaining -= length
    return [month_idx+1, day_number, bangla_year]
def _civil_start_sunrise_for_transit(transit_jd, place, sankranti_rule=None, ghatikas=None):
    """
        Determines which civil (sunrise-to-sunrise) day a given solar transit
        instant belongs to, per the specified sankranti_rule.

        Base classical rule (applies directly to TAMIL_NADU_SUNSET_RULE, and
        underlies the day/night logic of all the "middle-tier" rules below):
        Dharma Sindhu, Poushya Maasa / Makara Sankranti Nirnaya chapter --
        "If Sankranti occurs in the day time... [it is kept that day]...
        But if Sankranti occurs in the night, the next day is of Punya."
        (condensed Eng. translation, Sri Kanchi Kamakoti Peetham, V.D.N. Rao)

        The 7 regional rules form a spectrum from loosest to strictest cutoff,
        not independent/unrelated cases:
          ORISSA_RULE            - loosest: no intra-day test, the civil day
                                    containing the instant always counts, however
                                    late (e.g. 23:59:59) the instant falls.
                                    Documented as the rule Punjab's Bikrami solar
                                    calendar also explicitly borrows ("the Orissa
                                    rule is observed").
          TAMIL_NADU_SUNSET_RULE  - the base Dharma-Sindhu day/night rule applied
                                    directly, with sunset as the day/night boundary.
          TAMIL_NADU_13_GHATIKA_RULE,
          MALAYALI_APARAHNA_RULE  - the cutoff tightened to earlier in the day
                                    (13 ghatikas after sunrise; 3/5 of daytime,
                                    i.e. before Aparahna begins, per the classical
                                    5-fold division of daylight: Prataha, Sangava,
                                    Madhyahna, Aparahna, Sayahna, each 1/5 of
                                    daytime).
          SUNRISE_TO_SUNRISE,
          BEFORE_GHATIKAS         - generic/parametrizable middle-tier
                                    implementations (not tied to one named
                                    region's classical text): SUNRISE_TO_SUNRISE
                                    is the simplest baseline ("did the instant
                                    occur before today's sunrise"); BEFORE_GHATIKAS
                                    is the general caller-supplied-threshold version
                                    of the same mechanism.
          BENGAL_ASSAM_RULE       - strictest: the civil day containing the instant
                                    NEVER counts; the sankranti always belongs to
                                    the day beginning at the NEXT sunrise. Documented
                                    as the one explicit regional exception to the
                                    "beginning of month" convention used everywhere
                                    else: "in the sidereal solar Bengali calendar and
                                    Assamese calendar, a Sankranti is marked as the
                                    END of each month and the day following as the
                                    beginning of a new month."

        @param transit_jd: Julian Day of the raw solar entry instant (local time)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param sankranti_rule: one of const.SANKRANTI_RULE 1-7. Rules 8
            (NANAKSHAHI_FIXED_RULE) and 9 (BANGLADESH_REFORMED_FIXED_RULE) are
            fixed-arithmetic, non-sankranti-based calendars and must NOT be passed
            to this function -- they are dispatched directly from solar_month_date()
            before any sankranti detection occurs. If passed here by mistake, this
            function falls back to TAMIL_NADU_SUNSET_RULE and emits a warning.
        @return: Julian Day of the sunrise that begins the civil sankranti day
    """
    if sankranti_rule is None: sankranti_rule = const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE
    _, _, sr_trans_jd = sunrise(transit_jd, place)
    _, _, ss_trans_jd = sunset(transit_jd, place)
    if sankranti_rule == const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE:
        is_day_one = transit_jd < ss_trans_jd
    elif sankranti_rule == const.SANKRANTI_RULE.BEFORE_GHATIKAS and ghatikas is not None:
        is_day_one = transit_jd < (sr_trans_jd + ghatikas/60.0)
    elif sankranti_rule == const.SANKRANTI_RULE.TAMIL_NADU_13_GHATIKA_RULE:
        is_day_one = transit_jd < (sr_trans_jd + 13/60.0)  # 13 ghatikas = 5h12m
    elif sankranti_rule == const.SANKRANTI_RULE.SUNRISE_TO_SUNRISE:
        is_day_one = transit_jd < sr_trans_jd
    elif sankranti_rule == const.SANKRANTI_RULE.MALAYALI_APARAHNA_RULE:
        day_length = ss_trans_jd - sr_trans_jd
        cutoff_jd = sr_trans_jd + 0.6 * day_length  # 3/5 of daytime = start of Aparahna
        is_day_one = transit_jd < cutoff_jd
    elif sankranti_rule == const.SANKRANTI_RULE.ORISSA_RULE:
        if transit_jd >= sr_trans_jd:
            return sr_trans_jd
        return sunrise(transit_jd - 1.0, place)[2]  # before sunrise: previous sunrise-day
    elif sankranti_rule == const.SANKRANTI_RULE.BENGAL_ASSAM_RULE:
        _, _, next_sr = sunrise(sr_trans_jd + 1.1, place)
        return next_sr  # unconditional -- never same civil day, per the sourced exception above
    else:
        is_day_one = transit_jd < ss_trans_jd  # error conditions default to Tamil Nadu
    if is_day_one:
        return sr_trans_jd
    else:
        _, _, next_sr = sunrise(sr_trans_jd + 1.1, place)
        return next_sr
def solar_month_date(jd, place, sankranti_rule=None, ghatikas=None):
    """
        returns solar month and day
        @param jd: julian day
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param sankranti_rule one of:
            const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE = 1 (Default: Sankranti day if sun enters zodiac before sunset)
            const.SANKRANTI_RULE.BEFORE_GHATIKAS = 2 (Sankranti day before prescribed ghatikas)
                    ghatikas = 13 => Tamil Calendar
                    ghatikas = 18 => Malabar calendar
                    ghatikas = 30 => Bengal Calendar
                    ghatikas = 45 => Kerala Calendar
            const.SANKRANTI_RULE.SUNRISE_TO_SUNRISE = 3 (Sankranti day if sun enters within sunrise to sunrise)
    """
    if sankranti_rule is None: sankranti_rule = const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE
    # Helper function to evaluate the civil start day for any given transit
    def get_civil_start_sunrise(transit_jd):
        _, _, sr_trans_jd = sunrise(transit_jd, place)
        _, _, ss_trans_jd = sunset(transit_jd, place)
        is_day_one = False
        
        if sankranti_rule == const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE:
            is_day_one = transit_jd < ss_trans_jd
        elif sankranti_rule == const.SANKRANTI_RULE.BEFORE_GHATIKAS and ghatikas is not None:
            is_day_one = transit_jd < (sr_trans_jd + ghatikas/60.0)
        elif sankranti_rule == const.SANKRANTI_RULE.SUNRISE_TO_SUNRISE:
            is_day_one = transit_jd < sr_trans_jd
        else:
            is_day_one = transit_jd < ss_trans_jd # error conditions is Tamil Nadu
        if is_day_one:
            return sr_trans_jd
        else:
            _, _, next_sr = sunrise(sr_trans_jd + 1.1, place)
            return next_sr

    # 1. Anchor the calculation to the Sunrise of the requested civil day
    _, _, current_sunrise_jd = sunrise(jd, place)

    # 2. Find the astronomical month at the exact moment of this sunrise
    jd_utc = current_sunrise_jd - (place.timezone / 24.0)
    lon = solar_longitude(jd_utc, place)
    astronomical_month_idx = int(lon / 30)

    # 3. Find the most recent transit (entry into current astronomical month)
    sankranti_jd, _ = next_planet_entry_date(const.SUN_ID, current_sunrise_jd, place, direction=-1)
    start_jd_current = get_civil_start_sunrise(sankranti_jd)

    # 4. Determine final Civil Month and Start Date
    if int(round(current_sunrise_jd)) < int(round(start_jd_current)):
        # EDGE CASE A: Astronomically in new month, but civilly the month hasn't started yet.
        # Belong to the previous month. Find the transit from ~30 days ago.
        sankranti_jd_prev, _ = next_planet_entry_date(const.SUN_ID, sankranti_jd - 1.0, place, direction=-1)
        final_start_jd = get_civil_start_sunrise(sankranti_jd_prev)
        final_month_idx = (astronomical_month_idx - 1) % 12
        
    else:
        # We are at least in the current month. 
        # EDGE CASE B: What if transit to the NEXT month happens later today?
        sankranti_jd_next, _ = next_planet_entry_date(const.SUN_ID, current_sunrise_jd, place, direction=1)
        start_jd_next = get_civil_start_sunrise(sankranti_jd_next)

        # If the next month's start day is evaluated to be today, today is Day 1 of the next month.
        if int(round(current_sunrise_jd)) >= int(round(start_jd_next)):
            final_start_jd = start_jd_next
            final_month_idx = (astronomical_month_idx + 1) % 12
        else:
            # Standard case: safely in the current month
            final_start_jd = start_jd_current
            final_month_idx = astronomical_month_idx

    # 5. Calculate continuous day number
    day_number = int(round(current_sunrise_jd)) - int(round(final_start_jd)) + 1

    return final_month_idx, day_number
def dhasa_year_duration(dhasa_duration_type=None,jd=None,place=None,round_to_digits=6,
                        savana_year_method=None,true_lunar_year_method=None): #V4.8.5
    jd_place_not_none = (jd is not None and place is not None)
    if dhasa_duration_type is None: 
        dhasa_duration_type = const.dhasa_year_duration_default
    elif dhasa_duration_type in const.DHASA_YEAR_DURATION:
        const.dhasa_year_duration_default = dhasa_duration_type
    if savana_year_method is None: savana_year_method = const.SAVANA_YEAR_METHOD.PROSPECTIVE_0_to_360_JHORA
    if dhasa_duration_type == const.DHASA_YEAR_DURATION.MEAN_SIDEREAL_YEAR: 
        return const.sidereal_year
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.MEAN_TROPICAL_YEAR: 
        return const.tropical_year
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.TRUE_SIDEREAL_YEAR and jd_place_not_none:
        return true_sidereal_year(jd, place, round_to_digits)
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR and jd_place_not_none:
        return true_tropical_year(jd, place, round_to_digits)
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.SAVANA_YEAR and jd_place_not_none:
        return savana_year(jd, place, round_to_digits,savana_year_method)
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.MEAN_LUNAR_YEAR and jd_place_not_none:
        return const.lunar_year#round(const.lunar_year,round_to_digits)
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.TRUE_LUNAR_YEAR and jd_place_not_none:
        return true_tithi_year(jd, place, true_lunar_year_method=true_lunar_year_method,
                               round_to_digits=round_to_digits)
    elif dhasa_duration_type == const.DHASA_YEAR_DURATION.GREGORIAN_YEAR:
        return const.average_gregorian_year
    else: return const.sidereal_year
def _get_dhasa_start_jd_savana(jd_birth:float, place:Place, fraction_elapsed:float,
                               total_dasa_years:float) -> float:
    elapsed_days_savana = fraction_elapsed * total_dasa_years * const.savana_year
    jd_start_local = jd_birth - elapsed_days_savana
    return jd_start_local
def _get_dhasa_end_jd_savana(
    start_jd: float,
    place: Place,
    total_dasa_years: float,
) -> float:
    """
    Calculates Dasa end JD using Savana year duration.
    One Savana year = const.savana_year days.
    """
    elapsed_days_savana = total_dasa_years * const.savana_year
    return start_jd + elapsed_days_savana

if __name__ == "__main__":
    utils.set_language('en')
    _ayan = "LAHIRI"
    set_ayanamsa_mode(_ayan)
    dob = Date(1996,12,7); tob = (10,34,0); place = Place('Chennai,IN',13.0389, 80.2619, +5.5)
    jd = utils.julian_day_number(dob,tob)
    print('tithi',tithi(jd,place))
    print('karaka tithi',karaka_tithi(jd, place))
    print('yogam',yogam(jd,place))
    print('karaka yogam',karaka_yogam(jd,place))
    exit()
    utils.set_language('en')
    dob = Date(1963,4,1); tob = (10,34,0); place = Place('Chennai,IN',13.0389, 80.2619, +5.5)
    jd = utils.julian_day_number(dob,tob)
    for _ in range(365):
        print(utils.jd_to_gregorian(jd),lunar_month_date(jd,place,use_purnimanta_system=True))
        jd += 1
