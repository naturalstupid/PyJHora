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
hijri.py — Hijri/Islamic date with two modes:

1) TABLE MODE (DEFAULT): hijridate (Umm al-Qura civil table)
   - Place independent, date-only conversion.
   - Best when you want a stable, widely used civil Hijri calendar.

2) CALCULATED MODE: calculated sighting (research-style)
   - Place/policy/criterion configurable (LOCAL / ANCHOR / GLOBAL_VISIBILITY).
   - Uses drik for sunset/moonset/new_moon + Swiss Ephemeris for Moon altitude.
   - Intended to approximate "sightability by calculation" (not actual reports).

 !!!! CAUTION: This code was generated using AI (Gemini / CoPoilot) - so review before using it !!!!

"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntFlag, auto
from types import SimpleNamespace
from typing import Optional, Tuple, Dict,Sequence, Union, List
from datetime import date as _date
from math import floor
from pyIslam.praytimes import PrayerConf, Prayer, LIST_FAJR_ISHA_METHODS

from jhora import utils
from jhora.panchanga import drik
import swisseph as swe

# =========================
# Public Options & Config
# =========================

class ISLAMIC_PRAYER_OPTIONS(IntFlag):
    # --- Calculation method (pick ONE) ---
    METHOD_KARACHI = auto()   # id=1 in LIST_FAJR_ISHA_METHODS [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_MWL     = auto()   # id=2 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_EGYPT   = auto()   # id=3 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_UMM_AL_QURA = auto()  # id=4 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_ISNA    = auto()   # id=5 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_UOIF    = auto()   # id=6 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_SINGAPORE = auto() # id=7 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_RUSSIA  = auto()   # id=8 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    METHOD_FIXED_90 = auto()  # id=9 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)

    # --- Asr madhab (pick ONE) ---
    ASR_SHAFII_MALIKI_HANBALI = auto()  # asr_madhab=1 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    ASR_HANAFI                = auto()  # asr_madhab=2 [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)

    # --- DST / summer time handling ---
    # pyIslam adds +1 hour internally if enable_summer_time=True [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    DST_OFF  = auto()
    DST_ON   = auto()

    # --- Output extras ---
    INCLUDE_MIDNIGHT  = auto()
    INCLUDE_QIYAM_LAST_THIRD = auto()

    # Default: ISNA, Shafii/Maliki/Hanbali, DST_OFF, no extras
    DEFAULT = METHOD_ISNA | ASR_SHAFII_MALIKI_HANBALI | DST_OFF


# Convenience namespaces like you did for ISLAMIC_OPTIONS
ISLAMIC_PRAYER_OPTIONS.METHOD = SimpleNamespace(
    KARACHI=ISLAMIC_PRAYER_OPTIONS.METHOD_KARACHI,
    MWL=ISLAMIC_PRAYER_OPTIONS.METHOD_MWL,
    EGYPT=ISLAMIC_PRAYER_OPTIONS.METHOD_EGYPT,
    UMM_AL_QURA=ISLAMIC_PRAYER_OPTIONS.METHOD_UMM_AL_QURA,
    ISNA=ISLAMIC_PRAYER_OPTIONS.METHOD_ISNA,
    UOIF=ISLAMIC_PRAYER_OPTIONS.METHOD_UOIF,
    SINGAPORE=ISLAMIC_PRAYER_OPTIONS.METHOD_SINGAPORE,
    RUSSIA=ISLAMIC_PRAYER_OPTIONS.METHOD_RUSSIA,
    FIXED_90=ISLAMIC_PRAYER_OPTIONS.METHOD_FIXED_90,
)
ISLAMIC_PRAYER_OPTIONS.ASR = SimpleNamespace(
    JOMHOR=ISLAMIC_PRAYER_OPTIONS.ASR_SHAFII_MALIKI_HANBALI,
    HANAFI=ISLAMIC_PRAYER_OPTIONS.ASR_HANAFI,
)
ISLAMIC_PRAYER_OPTIONS.DST = SimpleNamespace(OFF=ISLAMIC_PRAYER_OPTIONS.DST_OFF, ON=ISLAMIC_PRAYER_OPTIONS.DST_ON)
ISLAMIC_PRAYER_OPTIONS.OUTPUT = SimpleNamespace(
    MIDNIGHT=ISLAMIC_PRAYER_OPTIONS.INCLUDE_MIDNIGHT,
    QIYAM_LAST_THIRD=ISLAMIC_PRAYER_OPTIONS.INCLUDE_QIYAM_LAST_THIRD,
)
@dataclass(frozen=True)
class IslamicPrayerTimesConfig:
    # Seconds to add/subtract to each prayer time (can be negative).
    # Order: fajr, sunrise, dhuhr, asr, maghrib, isha
    offsets_seconds: Sequence[float] = (0, 0, 0, 0, 0, 0)

    # Hijri correction value used internally by pyIslam for Ramadan check in Umm al-Qura Isha fixed time. [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    correction_val: int = 0

def islamic_prayer_times(
    jd: float,
    place,
    prayer_options: Optional[Union[ISLAMIC_PRAYER_OPTIONS, int]] = None,
    config: Optional[IslamicPrayerTimesConfig] = None
) -> List[float]:
    """
    Compute prayer times for the Gregorian date corresponding to Julian Day `jd`
    at the given `place`.

    Parameters
    ----------
    jd : float
        Julian Day number (may include fractional day).
    place : struct/obj
        Must have attributes: latitude, longitude, timezone (GMT offset).
        (Matches your Place struct: ['Place','latitude','longitude','timezone']).
    prayer_options : ISLAMIC_PRAYER_OPTIONS | int | None
        Bitmask controlling method, madhab, DST, and extra outputs.
    config : IslamicPrayerTimesConfig | None
        Optional per-prayer offsets (seconds) and correction_val.

    Returns
    -------
    List[float]
        Float hours in local time: [fajr, sunrise, dhuhr, asr, maghrib, isha]
        Optionally appends [midnight] and/or [last_third] if enabled.
    """
    if prayer_options is None:
        prayer_options = ISLAMIC_PRAYER_OPTIONS.DEFAULT
    else:
        prayer_options = ISLAMIC_PRAYER_OPTIONS(prayer_options)

    if config is None:
        config = IslamicPrayerTimesConfig()

    # ---- Choose method id (1..9) from options; default ISNA (id=5) ----
    method_map = {
        ISLAMIC_PRAYER_OPTIONS.METHOD_KARACHI: 1,
        ISLAMIC_PRAYER_OPTIONS.METHOD_MWL: 2,
        ISLAMIC_PRAYER_OPTIONS.METHOD_EGYPT: 3,
        ISLAMIC_PRAYER_OPTIONS.METHOD_UMM_AL_QURA: 4,
        ISLAMIC_PRAYER_OPTIONS.METHOD_ISNA: 5,
        ISLAMIC_PRAYER_OPTIONS.METHOD_UOIF: 6,
        ISLAMIC_PRAYER_OPTIONS.METHOD_SINGAPORE: 7,
        ISLAMIC_PRAYER_OPTIONS.METHOD_RUSSIA: 8,
        ISLAMIC_PRAYER_OPTIONS.METHOD_FIXED_90: 9,
    }

    chosen_method_id = 5  # ISNA [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    for flag, mid in method_map.items():
        if prayer_options & flag:
            chosen_method_id = mid
            break

    # Validate method id against pyIslam's predefined list [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    if not (1 <= chosen_method_id <= len(LIST_FAJR_ISHA_METHODS)):
        chosen_method_id = 5

    # ---- Asr madhab ----
    asr_madhab = 2 if (prayer_options & ISLAMIC_PRAYER_OPTIONS.ASR_HANAFI) else 1  # [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)

    # ---- DST / summer time ----
    enable_summer_time = bool(prayer_options & ISLAMIC_PRAYER_OPTIONS.DST_ON)  # [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)

    # ---- Convert Julian Day -> Gregorian date ----
    # pyIslam provides julian_to_gregorian(jd) -> (year, month, day). [2](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/baselib.py)
    y, m, d = utils.jd_to_gregorian(jd)[:-1]
    gdate = _date(int(y), int(m), int(floor(d)))  # ignore fractional day component safely

    # ---- Build pyIslam config and compute times ----
    # PrayerConf signature: (longitude, latitude, timezone, angle_ref, asr_madhab, enable_summer_time). [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    pconf = PrayerConf(
        float(place.longitude),
        float(place.latitude),
        float(place.timezone),
        int(chosen_method_id),
        int(asr_madhab),
        bool(enable_summer_time),
    )

    # Prayer(conf, date, correction_val=0) [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    p = Prayer(pconf, gdate, correction_val=int(config.correction_val))

    # Offsets: fajr, sunrise, dhuhr, asr, maghrib, isha
    offs = list(config.offsets_seconds)
    if len(offs) != 6:
        raise ValueError("config.offsets_seconds must have 6 elements (fajr..isha)")

    # Convert datetime.time -> float hour
    def _t2h(t) -> float:
        return t.hour + (t.minute / 60.0) + (t.second / 3600.0)

    # Prayer time methods provided by pyIslam Prayer class [1](https://github.com/abougouffa/pyIslam/blob/master/pyIslam/praytimes.py)
    times = [
        _t2h(p.fajr_time(shift=offs[0])),
        _t2h(p.sherook_time(shift=offs[1])),
        _t2h(p.dohr_time(shift=offs[2])),
        _t2h(p.asr_time(shift=offs[3])),
        _t2h(p.maghreb_time(shift=offs[4])),
        _t2h(p.ishaa_time(shift=offs[5])),
    ]

    # Optional extras
    if prayer_options & ISLAMIC_PRAYER_OPTIONS.INCLUDE_MIDNIGHT:
        times.append(_t2h(p.midnight()))
    if prayer_options & ISLAMIC_PRAYER_OPTIONS.INCLUDE_QIYAM_LAST_THIRD:
        times.append(_t2h(p.last_third_of_night()))

    return times

class ISLAMIC_OPTIONS(IntFlag):
    METHOD_HIJRIDATE = auto()      
    METHOD_CALCULATED = auto()     

    POLICY_LOCAL = auto()
    POLICY_ANCHOR_PLACE = auto()
    POLICY_GLOBAL_VISIBILITY = auto()

    CRITERIA_MOONSET_ONLY = auto()
    CRITERIA_AGE_LAG_ELONG = auto()
    CRITERIA_ECFR_8_5 = auto()     

    BOUNDARY_SUNSET = auto()
    BOUNDARY_MIDNIGHT = auto()

    LABEL_TABULAR = auto()

    DEFAULT = METHOD_HIJRIDATE | BOUNDARY_MIDNIGHT

ISLAMIC_OPTIONS.METHOD = SimpleNamespace(HIJRIDATE=ISLAMIC_OPTIONS.METHOD_HIJRIDATE, CALCULATED=ISLAMIC_OPTIONS.METHOD_CALCULATED)
ISLAMIC_OPTIONS.POLICY = SimpleNamespace(LOCAL=ISLAMIC_OPTIONS.POLICY_LOCAL, ANCHOR_PLACE=ISLAMIC_OPTIONS.POLICY_ANCHOR_PLACE, GLOBAL_VISIBILITY=ISLAMIC_OPTIONS.POLICY_GLOBAL_VISIBILITY)
ISLAMIC_OPTIONS.CRITERIA = SimpleNamespace(MOONSET_ONLY=ISLAMIC_OPTIONS.CRITERIA_MOONSET_ONLY, AGE_LAG_ELONG=ISLAMIC_OPTIONS.CRITERIA_AGE_LAG_ELONG, ECFR_8_5=ISLAMIC_OPTIONS.CRITERIA_ECFR_8_5)
ISLAMIC_OPTIONS.BOUNDARY = SimpleNamespace(SUNSET=ISLAMIC_OPTIONS.BOUNDARY_SUNSET, MIDNIGHT=ISLAMIC_OPTIONS.BOUNDARY_MIDNIGHT)
ISLAMIC_OPTIONS.LABEL = SimpleNamespace(TABULAR=ISLAMIC_OPTIONS.LABEL_TABULAR)

@dataclass(frozen=True)
class HijriCriteriaConfig:
    min_age_hours: float = 18.0
    min_lag_minutes: float = 40.0
    min_elong_deg: float = 10.0
    at_pressure_mbar: float = 1013.25
    at_temperature_c: float = 15.0
    observer_alt_m: float = 0.0
    scan_days: int = 3
    lon_step_deg: int = 15
    lat_samples: Tuple[float, ...] = (-30.0, 0.0, 30.0)
    use_solar_tz_for_scan: bool = True  
    global_pick: str = "earliest"

# =========================
# Core Astronomy Helpers
# =========================

GREENWICH = drik.Place("Greenwich", 0.0, 0.0, 0.0)

def _jd_to_ut(jd_local: float, place) -> float:
    return jd_local - place.timezone / 24.0

def _ut_to_local(jd_ut: float, place) -> float:
    return jd_ut + place.timezone / 24.0

def _get_boundary_start(jd_local: float, place, options: ISLAMIC_OPTIONS) -> float:
    if options & ISLAMIC_OPTIONS.BOUNDARY.MIDNIGHT:
        return math.floor(jd_local + 0.5) - 0.5
    ss_today = drik.sunset(jd_local, place)[2]
    return ss_today if jd_local >= ss_today else drik.sunset(jd_local - 1.0, place)[2]

def _get_conjunction_ut(jd_probe_ut: float) -> float:
    jd_ref = _ut_to_local(jd_probe_ut, GREENWICH)
    tithi_idx = drik.tithi(jd_ref, GREENWICH)[0]
    nm_local = drik.new_moon(jd_ref, tithi_idx, opt=-1)
    return _jd_to_ut(nm_local, GREENWICH)

def _is_visible(ss_local: float, place, nm_ut: float, options: ISLAMIC_OPTIONS, cfg: HijriCriteriaConfig) -> bool:
    nm_local = _ut_to_local(nm_ut, place)
    if ss_local <= nm_local: return False
    ms_local = drik.moonset(ss_local, place)[2]
    if ms_local <= ss_local: return False
    if options & ISLAMIC_OPTIONS.CRITERIA.MOONSET_ONLY: return True
    jd_ut = _jd_to_ut(ss_local, place)
    elon = (drik.lunar_longitude(jd_ut) - drik.solar_longitude(jd_ut)) % 360.0
    elon = 360.0 - elon if elon > 180.0 else elon
    if options & ISLAMIC_OPTIONS.CRITERIA.AGE_LAG_ELONG:
        age = (ss_local - nm_local) * 24.0
        lag = (ms_local - ss_local) * 1440.0
        return age >= cfg.min_age_hours and lag >= cfg.min_lag_minutes and elon >= cfg.min_elong_deg
    if options & ISLAMIC_OPTIONS.CRITERIA.ECFR_8_5:
        swe.set_topo(float(place.longitude), float(place.latitude), float(cfg.observer_alt_m))
        flags = swe.FLG_EQUATORIAL | swe.FLG_TOPOCTR
        pos, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
        _, alt, _ = swe.azalt(jd_ut, swe.EQU2HOR, [float(place.longitude), float(place.latitude), float(cfg.observer_alt_m)], 
                               cfg.at_pressure_mbar, cfg.at_temperature_c, [pos[0], pos[1], pos[2]])
        return elon >= 8.0 and alt >= 5.0
    return False

# =========================
# Month Start Logic
# =========================

_TRIGGER_CACHE: Dict[Tuple, float] = {}

def _find_trigger_ut(nm_ut: float, place, options: ISLAMIC_OPTIONS, cfg: HijriCriteriaConfig, anchor=None) -> float:
    key = (round(nm_ut, 4), int(options), anchor.Place if anchor else None)
    if key in _TRIGGER_CACHE: return _TRIGGER_CACHE[key]
    if options & ISLAMIC_OPTIONS.POLICY.LOCAL:
        search_places = [place]
    elif options & ISLAMIC_OPTIONS.POLICY.ANCHOR_PLACE:
        search_places = [anchor]
    else: # Global
        search_places = []
        for lat in cfg.lat_samples:
            for lon in range(-180, 181, cfg.lon_step_deg):
                search_places.append(drik.Place("SCAN", float(lat), float(lon), lon/15.0))
    best_ut = None
    for day in range(cfg.scan_days):
        for p in search_places:
            ss_l = drik.sunset(_ut_to_local(nm_ut, p) + 0.2 + day, p)[2]
            if _is_visible(ss_l, p, nm_ut, options, cfg):
                ut = _jd_to_ut(ss_l, p)
                if best_ut is None or ut < best_ut: best_ut = ut
        if best_ut is not None: break
    res = best_ut if best_ut else nm_ut + 2.0 
    _TRIGGER_CACHE[key] = res
    return res

def _get_month_start_boundary(nm_ut: float, place, options: ISLAMIC_OPTIONS, cfg: HijriCriteriaConfig, anchor=None) -> float:
    trig_ut = _find_trigger_ut(nm_ut, place, options, cfg, anchor)
    trig_l = _ut_to_local(trig_ut, place)
    if options & ISLAMIC_OPTIONS.BOUNDARY.MIDNIGHT:
        m_start = math.floor(trig_l + 0.5) - 0.5
        return m_start if m_start >= trig_l else m_start + 1.0
    ss = drik.sunset(trig_l, place)[2]
    return ss if ss >= trig_l else drik.sunset(ss + 1.1, place)[2]

def _islamic_from_jd_tabular(jd: float) -> Tuple[int, int, int]:
    days = math.floor(jd + 0.5) - math.floor(1948439.5 + 0.5) + 1
    year = int(math.floor((30 * days + 10646) / 10631))
    first = (year - 1) * 354 + math.floor((3 + 11 * year) / 30)
    month = int(min(12, math.ceil((days - first) / 29.5)))
    day = int(days - first - math.ceil(29.5 * (month - 1)))
    return year, max(1, min(12, month)), max(1, min(30, day))

# =========================
# Public API
# =========================

def islamic_lunar_date(jd: float, place=None, options=None, cfg=None, anchor_place=None) -> Tuple[int, int, int]:
    if options is None: options = ISLAMIC_OPTIONS.DEFAULT
    
    # --- Hijridate Tabular Option (Place Independent) ---
    if options & ISLAMIC_OPTIONS.METHOD_HIJRIDATE:
        from hijridate import Gregorian
        y, m, d, _ = utils.jd_to_gregorian(jd)
        h = Gregorian(y, m, d).to_hijri()
        return h.year, h.month, h.day

    # --- Calculated Model (Requires Place) ---
    if place is None:
        raise ValueError("Place argument is required for METHOD_CALCULATED")
    if cfg is None: cfg = HijriCriteriaConfig()

    current_boundary = _get_boundary_start(jd, place, options)
    probe_ut = _jd_to_ut(current_boundary + 0.5, place)
    nm_ut = _get_conjunction_ut(probe_ut)
    month_start = _get_month_start_boundary(nm_ut, place, options, cfg, anchor_place)

    if current_boundary < (month_start - 0.001):
        nm_ut = _get_conjunction_ut(_jd_to_ut(month_start - 5.0, place))
        month_start = _get_month_start_boundary(nm_ut, place, options, cfg, anchor_place)

    day = int(round(current_boundary - month_start)) + 1
    y, m, _ = _islamic_from_jd_tabular(month_start + 5.0)
    return y, m, day

# =========================
# Testing Matrix
# =========================

def run_option_matrix_tests(jd: float, place, anchor_place):
    policies = [
        ("LOCAL", ISLAMIC_OPTIONS.POLICY.LOCAL),
        ("ANCHOR", ISLAMIC_OPTIONS.POLICY.ANCHOR_PLACE),
        ("GLOBAL", ISLAMIC_OPTIONS.POLICY.GLOBAL_VISIBILITY),
    ]
    criteria = [
        ("MOONSET_ONLY", ISLAMIC_OPTIONS.CRITERIA.MOONSET_ONLY),
        ("AGE_LAG_ELONG", ISLAMIC_OPTIONS.CRITERIA.AGE_LAG_ELONG),
        ("ECFR_8_5", ISLAMIC_OPTIONS.CRITERIA.ECFR_8_5),
    ]
    boundaries = [
        ("SUNSET", ISLAMIC_OPTIONS.BOUNDARY.SUNSET),
        ("MIDNIGHT", ISLAMIC_OPTIONS.BOUNDARY.MIDNIGHT),
    ]

    cfg = HijriCriteriaConfig()

    for b_name, b_flag in boundaries:
        print("\n=== Boundary:", b_name, "===")
        for p_name, p_flag in policies:
            for c_name, c_flag in criteria:
                opts = (ISLAMIC_OPTIONS.METHOD_CALCULATED | p_flag | c_flag | b_flag | ISLAMIC_OPTIONS.LABEL_TABULAR)
                try:
                    res = islamic_lunar_date(jd, place, options=opts, cfg=cfg, anchor_place=anchor_place)
                    print(f"{p_name:6} {c_name:12} -> {res}")
                except Exception as e:
                    print(f"{p_name:6} {c_name:12} -> ERROR: {e}")

if __name__ == "__main__":
    utils.set_language('ta')
    Date = drik.Date
    Place = drik.Place

    chicago = Place("Chicago,US", 41.85, -87.65, -5.0)
    mecca = Place("Mecca",21.42664,39.82563,+3.0)
    prayer_types = ['fajr_str','shurook_str','dhuhr_str','asr_str','maghrib_str','isha_str']

    dob = Date(2026, 4, 1)
    tob = (8, 30, 0)
    jd = utils.julian_day_number(dob, tob)
    times = islamic_prayer_times(
        jd,
        chicago,
        prayer_options=ISLAMIC_PRAYER_OPTIONS.METHOD.ISNA | ISLAMIC_PRAYER_OPTIONS.ASR.JOMHOR | ISLAMIC_PRAYER_OPTIONS.DST.OFF
    )
    
    print([utils.resource_strings[prayer_types[p]]+':'+utils.to_dms(pt) for p,pt, in enumerate(times)])
    tob = (20, 30, 0)
    jd = utils.julian_day_number(dob, tob)
    print(drik.sunrise(jd, chicago),drik.sunset(jd,chicago))
    times = islamic_prayer_times(
        jd,
        chicago,
        prayer_options=ISLAMIC_PRAYER_OPTIONS.METHOD.ISNA | ISLAMIC_PRAYER_OPTIONS.ASR.JOMHOR | ISLAMIC_PRAYER_OPTIONS.DST.OFF
    )
    print([utils.resource_strings[prayer_types[p]]+':'+utils.to_dms(pt) for p,pt, in enumerate(times)])
    # loop for 60 days
    for d in range(60):
        # 1. default: hijridate (table)
        table_y, table_m, table_d = islamic_lunar_date(jd)
        
        # 2. calculated model (sighting)
        calc_y, calc_m, calc_d = islamic_lunar_date(
            jd, chicago,
            options=(ISLAMIC_OPTIONS.METHOD_CALCULATED |
                     ISLAMIC_OPTIONS.POLICY.GLOBAL_VISIBILITY |
                     ISLAMIC_OPTIONS.CRITERIA.ECFR_8_5 |
                     ISLAMIC_OPTIONS.BOUNDARY.SUNSET |
                     ISLAMIC_OPTIONS.LABEL_TABULAR),
            cfg=HijriCriteriaConfig(),
            anchor_place=mecca
        )

        g = utils.jd_to_gregorian(jd)
        print(f"{g[:3]}", 
              (table_y, utils.ISLAMIC_MONTH_LIST[table_m-1], table_d),
              (calc_y, utils.ISLAMIC_MONTH_LIST[calc_m-1], calc_d))
        jd += 1

    # Matrix test for a specific date
    jd_test = utils.julian_day_number(Date(2026, 4, 19), (8, 30, 0))
    run_option_matrix_tests(jd_test, chicago, mecca)
