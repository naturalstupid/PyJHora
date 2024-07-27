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
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/pyhora
"""
    To calculate panchanga/calendar elements such as tithi, nakshatra, etc.
    Uses swiss ephemeris
"""
from geopy.geocoders import Nominatim
from pytz import timezone, utc
from math import ceil
from collections import namedtuple as struct
import swisseph as swe
from _datetime import datetime, timedelta
from datetime import date
import math, os, warnings
from collections import OrderedDict as Dict
from hora import utils, const


""" Since datetime does not accept BC year values Use the following stucture to represent dates """
Date = struct('Date', ['year', 'month', 'day'])
Place = struct('Place', ['Place','latitude', 'longitude', 'timezone'])
planet_list = [const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER,
               const._VENUS, const._SATURN,const._RAHU,const._KETU]#,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
_sideral_planet_list = [const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER,
               const._VENUS, const._SATURN,const._RAHU,const._KETU]#,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
#if const._INCLUDE_URANUS_TO_PLUTO: _sideral_planet_list += [swe.URANUS,swe.NEPTUNE,swe.PLUTO]
_tropical_planet_list = [const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER,
               const._VENUS, const._SATURN,const._URANUS,const._NEPTUNE,const._PLUTO] # Rahu = MEAN_NODE
revati_359_50 = lambda: swe.set_sid_mode(swe.SIDM_USER, 1926892.343164331, 0)
galc_cent_mid_mula = lambda: swe.set_sid_mode(swe.SIDM_USER, 1922011.128853056, 0)
# Hindu sunrise/sunset is calculated w.r.t middle of the sun's disk
# They are geometric, i.e. "true sunrise/set", so refraction is not considered
_rise_flags = swe.BIT_HINDU_RISING | swe.FLG_TRUEPOS | swe.FLG_SPEED # V3.2.3 # Speed flag added for retrogression
#_rise_flags = swe.BIT_DISC_CENTER + swe.BIT_NO_REFRACTION #+ swe.BIT_GEOCTR_NO_ECL_LAT #V3.0.6

def set_tropical_planets():
    global planet_list
    planet_list = _tropical_planet_list    
def set_sideral_planets():
    global planet_list
    planet_list = _sideral_planet_list
    
#PLANET_NAMES= ['Suriyan', 'Chandran', 'Sevvay','Budhan','Viyaazhan','VeLLi','Sani','Raahu','Kethu','Uranus','Neptune']
_ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
_ayanamsa_value = None
def _ayanamsa_surya_siddhantha_model(jd):
    maha_yuga_years = 4320000
    completed_maha_yuga_years = 3888000
    cycle_of_equinoxes = 7200
    """ 
    Precession Rate Reference
            Walter Cruttenden and Vince Dayes, “Understanding Precession of the Equinox”, New Frontiers in Science. 
            http://carlotto.us/newfrontiersinscience/Papers/v02n01a/v02n01a.pdf
    """
    precession_rate_maximum = 12 # As per above reference max 12 arc seconds in 21600 years
    yuga_of_equinoxes = 3 * cycle_of_equinoxes # half period
    ayanamsa_peak_in_degrees = 27.0 # 27 degrees either side from Aries 0 degrees
    kali_yuga_jd =  swe.julday(-3101,1,23,12,cal=swe.JUL_CAL)
    ss_sideral_year = 365.256363 #365.2421988 # 365.2587565
    diff_days = jd - kali_yuga_jd
    sideral_diff_days = diff_days / ss_sideral_year
    ayanamsa_cycle_fraction = (sideral_diff_days/cycle_of_equinoxes)
    ayanamsa_rate_cycle_fraction = (sideral_diff_days/yuga_of_equinoxes)
    precession_rate = -precession_rate_maximum * math.sin(ayanamsa_rate_cycle_fraction * math.pi)
    ayanamsa = math.sin(ayanamsa_cycle_fraction * 2.0 * math.pi) *(ayanamsa_peak_in_degrees+precession_rate)
    return ayanamsa
def _calculate_ayanamsa_senthil_from_jd(jd):
    #print('calling senthil')
    reference_jd =  swe.julday(2000, 1, 1, 12,cal=swe.GREG_CAL)
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
def get_ayanamsa_value(jd):
    """
        Get ayanamsa value for the julian day number
        @param jd: Julian Day Number
        @return: ayanamsa value - ayanamsa for the day based on the model used. 
    """
    global _ayanamsa_mode,_ayanamsa_value
    #print('Drik:get_ayanamsa_value',_ayanamsa_mode,_ayanamsa_value)
    key = _ayanamsa_mode.lower()
    if key =='sidm_user' or key =='senthil' or key == 'sundar_ss':
        #print(key,'returning',_ayanamsa_value)
        return _ayanamsa_value
    else:
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        return swe.get_ayanamsa(jd)
def set_ayanamsa_mode(ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE,ayanamsa_value=None,jd=None):
    """
        Set Ayanamsa mode
        @param ayanamsa_mode - Default - Lahiri
        @param ayanamsa_value - Need to be supplied only in case of 'SIDM_USER'
        See 'available_ayanamsa_modes' for the list of available models
        @return None
    """
    global _ayanamsa_mode,_ayanamsa_value
    key = ayanamsa_mode.upper()
    #print('panchanga setting',key,ayanamsa_value,jd)
    if key in [am.upper() for am in const.available_ayanamsa_modes.keys()]:
        if key == "SIDM_USER":
            _ayanamsa_value = ayanamsa_value
            swe.set_sid_mode(swe.SIDM_USER,ayanamsa_value)
        elif key == "SENTHIL":
            _ayanamsa_value = _calculate_ayanamsa_senthil_from_jd(jd)
        elif key == "SUNDAR_SS":
            _ayanamsa_value = _ayanamsa_surya_siddhantha_model(jd)
        else:
            swe.set_sid_mode(const.available_ayanamsa_modes[key])
    else:
        warnings.warn("Unsupported Ayanamsa mode:", ayanamsa_mode,"KP Assumed")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    #print("Ayanamsa mode",ayanamsa_mode,'set')
    _ayanamsa_mode = ayanamsa_mode
    #print('Drik:set_ayanamsa_mode',_ayanamsa_mode,_ayanamsa_value)
#set_ayanamsa_mode = lambda: swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
reset_ayanamsa_mode = lambda: swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
""" TODO: Need to make panchanga resource independent """
# Convert 23d 30' 30" to 23.508333 degrees
from_dms = lambda degs, mins, secs: degs + mins/60 + secs/3600

# Ketu is always 180° after Rahu, so same coordinates but different constellations
# i.e if Rahu is in Pisces, Ketu is in Virgo etc
ketu = lambda rahu: (rahu + 180) % 360
rahu = lambda ketu: (ketu + 180) % 360

# Julian Day number as on (year, month, day) at 00:00 UTC
gregorian_to_jd = lambda date: swe.julday(date.year, date.month, date.day, 0.0)
jd_to_gregorian = lambda jd: swe.revjul(jd, swe.GREG_CAL)   # returns (y, m, d, h, min, s)

# moon daily motion
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
  
# sun daily motion
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
    reminder = (longitude - quotient * one_star)
    pada = int(reminder / one_pada)
    #  print (longitude,quotient,pada)
    # convert 0..26 to 1..27 and 0..3 to 1..4
    return [1 + quotient, 1 + pada,reminder]

def sidereal_longitude(jd, planet):
    """
        The sequence number of 0 to 8 for planets is not followed by swiss ephemeris
        Need to be sure we pass correct planet reference to swiss ephemeris
    """
    """
        Computes nirayana (sidereal) longitude of given planet on jd
        Note: This is where the selected/default ayanamsa is adjusted to tropical longitude obtained from swiss ephimeride
        @param jd: Julian Day Number of the UTC date/time
        @param planet: index of the planet Use const._SUN, const._RAHU etc.
        @return: the sidereal longitude of the planet  
    """
    global _ayanamsa_mode,_ayanamsa_value
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
    longi,flgs = swe.calc_ut(jd, planet, flags = flags)
    reset_ayanamsa_mode()
    return utils.norm360(longi[0]) # degrees
def planets_in_retrograde(jd,place):
    """ TODO: Under TEST - Retrogression using llongitude speed value from swiss ephemeris """
    jd_utc = jd - place.timezone / 24.
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
    set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
    retro_planets = []
    for planet in planet_list[2:7]:
        p_id = planet_list.index(planet)
        longi,flgs = swe.calc_ut(jd, planet, flags = flags)
        reset_ayanamsa_mode()
        #print(p_id,longi,longi[3])
        if longi[3]<0 : retro_planets.append(p_id)
    return retro_planets
solar_longitude = lambda jd: sidereal_longitude(jd, const._SUN)
lunar_longitude = lambda jd: sidereal_longitude(jd, const._MOON)
def sunrise(jd, place):
    """
        Sunrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return sunrise time as local time in float hours, local time string, and rise sd julian number date
            Time Format: float hours or hh:mm:ss AM/PM
    """
    # First convert jd to UTC
    y, m, d,_  = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    
    _,lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)
    rise_jd = result[1][0]  # julian-day number
    rise_local_time = (rise_jd - jd_utc) * 24 + tz
    """ ADDED THE FOLLOWING IN V2.5.2 TO RECALCULATE RISE_JD"""
    dob = (y,m,d)
    tob = tuple(utils.to_dms(rise_local_time, as_string=False))
    rise_jd = utils.julian_day_number(dob, tob)
    # Convert to local time
    return [rise_local_time, utils.to_dms(rise_local_time),rise_jd]
def midday(jd,place):
    """
        Return midday time in float hours
    """
    sun_rise = sunrise(jd, place)#[2]
    sun_set = sunset(jd, place)#[2]
    _,_,_,srh = utils.jd_to_gregorian(sun_rise[2])
    _,_,_,ssh = utils.jd_to_local(sun_set[2],place)
    mdhl = 0.5*(srh+ssh)
    return mdhl
def midnight(jd,place):
    """
        Return midday time in float hours
    """
    sun_rise = sunrise(jd, place)#[2]
    prev_sun_set = sunset(jd-1, place)#[2]
    _,_,_,srh = utils.jd_to_gregorian(sun_rise[2])
    _,_,_,pssh = utils.jd_to_local(prev_sun_set[2],place)
    mnhl = 0.5*(srh+pssh)
    if mnhl < 12:
        mnhl = 12 - mnhl
    else:
        mnhl -= 12
    return mnhl
def day_length(jd, place):
    """
        Return local day length in float hours
    """
    sun_rise = sunrise(jd, place)#[2]
    sun_set = sunset(jd, place)#[2]
    _,_,_,srh = utils.jd_to_gregorian(sun_rise[2])
    _,_,_,ssh = utils.jd_to_local(sun_set[2],place)
    dl = ssh - srh
    return dl
def night_length(jd, place):
    """
        Return local night length in float hours
    """
    next_sun_rise = sunrise(jd+1, place)#[2]
    sun_set = sunset(jd, place)#[2]
    _,_,_,nsrh = utils.jd_to_gregorian(next_sun_rise[2])
    _,_,_,ssh = utils.jd_to_local(sun_set[2],place)
    nl = 24.0 + nsrh - ssh 
    return nl
def sunset(jd, place):
    """
        Sunset when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return sunset  time as local time in float hours, local time string, and rise sd julian number date
            Time Format: float hours or hh:mm:ss AM/PM
    """
    # First convert jd to UTC
    y, m, d,_  = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    _,lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)
    set_jd = result[1][0]
    set_local_time = (set_jd - jd_utc) * 24 + tz
    # Convert to local time
    return [set_local_time, utils.to_dms(set_local_time),set_jd]
def moonrise(jd, place):
    """
        Moonrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return moonrise time in Julian day and local time
            Time Format: float hours or hh:mm:ss depending on as_string=False/True in to_dms()
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    city, lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.MOON, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)
    rise = result[1][0]  # julian-day number
    # Convert to local time
    local_time = (rise - jd_utc) * 24 + tz
    return [local_time,utils.to_dms(local_time),rise]

def moonset(jd, place,yesterdays_moon_set_time=False):
    """
        Moonset when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return moonset time in Julian day and local time
            Time Format: float hours or hh:mm:ss depending on as_string=False/True in to_dms()
        NOTE:
            Unlike sun which rises and sets on same day, Moon sets first and rises later on same day
            Moonset time on given JD gives the time of previous day's moon setting
            If you want today's moon set time (which will be on tomorrow) then you should provide JD+1
            So here as default - tomorrow's moon set time is returned.
            To get yesterday's moon set today - set yesterdays_moon_set_time=True
    """
    # First convert jd to UTC
    today_moonset_jd = 1; today_moonset_str = ' (+1)'
    if yesterdays_moon_set_time:
        today_moonset_jd = 0; today_moonset_str = ''
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d)) + today_moonset_jd # V3.2.7 +1 added to get today's moon set which is tomorrow
    city, lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.MOON, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)
    setting = result[1][0]  # julian-day number
    # Convert to local time
    local_time = (setting - jd_utc) * 24 + tz
    return [local_time,utils.to_dms(local_time)+today_moonset_str,setting+today_moonset_jd]

def _get_tithi(jd,place):
    tz = place.timezone
    # First convert jd to UTC  # 2.0.3
    y, m, d,bt = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[2] # V2.2.8
    # 2. Find tithi at this JDN
    moon_phase = lunar_phase(rise)
    today = ceil(moon_phase / 12)
    """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME See Dr. Jayasree Saranatha Mahabharatha datte validation book """
    if jd < const.mahabharatha_tithi_julian_day: #V3.2.0
        today = (today+1)%30
    degrees_left = today * 12 - moon_phase
    #print('frac left',frac_left, 1.0-frac_left)
    # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
    solar_long_diff = [ (solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets ]
    relative_motion = [ moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = relative_motion; x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end -jd_utc) * 24 + tz #jd changed to jd_utc 2.0.3
    #print('tithi start time',starts,utils.to_dms(starts))
    tithi_no = int(today)
    #""" Start Time 
    answer = [tithi_no, ends]
    # 5. Check for skipped tithi
    moon_phase_tmrw = lunar_phase(rise + 1)
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
        ends = (rise + approx_end -jd_utc) * 24 + place.timezone #jd changed to jd_utc 2.0.3
        leap_tithi = 1 if today == 30 else leap_tithi
        answer += [tithi_no, ends]
    return answer
def tithi(jd,place):
    """
        Tithi at sunrise for given date and place. Also returns tithi's end time.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return [tithi index, tithi_start_time, tithi ending time, tithi_fraction]
          next tithi index and next tithi time is additionally returned if two tithis on same day
          tithi index = [1..30] 
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    _tithi = _get_tithi(jd,place)
    #print('_tithi',_tithi)
    _tithi_prev = _get_tithi(jd-1,place)
    #print('_tithi_prev',_tithi_prev)
    _tithi_no = _tithi[0]; _tithi_start = _tithi_prev[1]; _tithi_end = _tithi[1]
    #print('before',_tithi_no,_tithi_start,_tithi_end,_tithi_frac)
    if _tithi_start < 24.0:
        _tithi_start = -_tithi_start #utils.to_dms(_tithi_start)+'(-1)'
    elif _tithi_start > 24:
        _tithi_start -= 24.0
    result = [_tithi_no,_tithi_start,_tithi_end]
    if len(_tithi)>2:
        _tn = _tithi[2]; _tn_start = _tithi_end; _tn_end = _tithi[3]
        result += [_tn,_tn_start,_tn_end]
    #print('after',_tithi_no,_tithi_start,_tithi_end,_tithi_frac,_tithi)
    return result
    
# Tithi doesn't depend on Ayanamsa
def _tithi_old(jd, place):
    """
        Tithi at sunrise for given date and place. Also returns tithi's end time.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return [tithi index, tithi ending time, next tithi index, next tithi ending time]
          next tithi index and next tithi time is additionally returned if two tithis on same day
          tithi index = [1..30] 
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    tz = place.timezone
    # First convert jd to UTC  # 2.0.3
    y, m, d, _ = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[2] # V2.2.8
    # 2. Find tithi at this JDN
    moon_phase = lunar_phase(rise)
    today = ceil(moon_phase / 12)
    degrees_left = today * 12 - moon_phase
    frac_left = 1.0 - (moon_phase/12) % 1
    #print('frac left',frac_left, 1.0-frac_left)
    # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
    solar_long_diff = [ (solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets ]
    relative_motion = [ moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = relative_motion; x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end -jd_utc) * 24 + tz #jd changed to jd_utc 2.0.3
    #print('tithi start time',starts,utils.to_dms(starts))
    tithi_no = int(today)
    #""" Start Time 
    answer = [tithi_no, utils.to_dms(ends),frac_left]
    # 5. Check for skipped tithi
    moon_phase_tmrw = lunar_phase(rise + 1)
    tomorrow = ceil(moon_phase_tmrw / 12)
    isSkipped = (tomorrow - today) % 30 > 1
    if isSkipped:
        # interpolate again with same (x,y)
        starts = ends # starts is ends of prev day
        leap_tithi = today + 1
        tithi_no = int(leap_tithi)
        degrees_left = leap_tithi * 12 - moon_phase_tmrw
        approx_end = utils.inverse_lagrange(x, y, degrees_left)
        ends = (rise + approx_end -jd_utc) * 24 + place.timezone #jd changed to jd_utc 2.0.3
        leap_tithi = 1 if today == 30 else leap_tithi
        frac_left = 1.0 - (moon_phase_tmrw/12) % 1
        answer += [tithi_no, utils.to_dms(ends),frac_left]
    return answer

def raasi(jd, place):
    """
        returns the raasi of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return [raasi index, raasi ending time, next raasi index, next raasi ending time]
          next raasi index and next raasi time is additionally returned if two raasis on same day 
          raasi index = [1..12]
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
        
    """
    tz = place.timezone
    # First convert jd to UTC # 2.0.3
    y, m, d, _ = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    rise = sunrise(jd, place)[2] # - tz / 24 #V2.3.0
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [lunar_longitude(rise+t) for t in offsets] #V2.3.0 # Fixed 1.1.0 lunar longitude from sunrise to next sunrise
    nirayana_long = lunar_longitude(jd)#longitudes[0] # Fixed 1.1.0 lunar longitude at JD and NOT at RISE
    raasi_no = int(nirayana_long/30)+1
    frac_left = 1.0 - (nirayana_long/30) % 1
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, raasi_no * 30)
    ends = (rise - jd_utc + approx_end) * 24 + tz #jd changed to jd_utc 2.0.3
    answer = [raasi_no, utils.to_dms(ends), frac_left]
    
    # 4. Check for skipped raasi
    raasi_tmrw = ceil(longitudes[-1] / 30)
    frac_left = 1.0 - (longitudes[-1] / 30) % 1
    isSkipped = (raasi_tmrw - raasi_no) % 12 > 1
    if isSkipped:
        leap_raasi = raasi_no + 1
        approx_end = utils.inverse_lagrange(offsets, longitudes, leap_raasi * 30)
        ends = (rise+1 - jd_utc + approx_end) * 24 + tz #rise => rise + 1
        leap_raasi = 1 if raasi_no == 12 else leap_raasi
        raasi_no = int(leap_raasi)
        answer += [raasi_no, utils.to_dms(ends), frac_left]
    #print(' rassi new ends',ends,isSkipped, answer)
    return answer
def _get_nakshathra(jd,place):
    tz = place.timezone
    # First convert jd to UTC
    y, m, d, _ = jd_to_gregorian(jd)
    jd_ut = gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2] # Changed to jd_utc in V2.9.6
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise+t, const._MOON) for t in offsets]
    nirayana_long = lunar_longitude(jd_utc) # Changed to jd_utc in V2.9.7
    nak_no,padam_no,rem = nakshatra_pada(nirayana_long)
    #print('moon long',nirayana_long,nak_no,padam_no,jd_utc)
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, nak_no * 360 / 27)
    ends = (rise - jd_ut + approx_end) * 24 + tz # """ Changed to jd_utc to get correct end time for the jd -  2.0.3 """
    answer = [nak_no,padam_no, ends]
    # 4. Check for skipped nakshatra
    #nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    #isSkipped = (nak_tmrw - nak_no) % 27 > 1
    #if isSkipped:
    leap_nak = nak_no + 1
    approx_end = utils.inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
    ends = (rise - jd_utc + approx_end) * 24 + tz # """ Changed to jd_utc to get correct end time for the jd -  2.0.3 """
    leap_nak = 1 if nak_no == 27 else leap_nak
    nak_no = int(leap_nak)
    answer += [nak_no,padam_no, ends] ## TODO: FRAC_LEFT USED HERE IS WRONG
    return answer
def nakshatra(jd,place):
    _nak = _get_nakshathra(jd, place)
    _nak_prev = _get_nakshathra(jd-1, place)
    _nak_no = _nak[0]; _pad_no = _nak[1]; _nak_start = _nak_prev[2]; _nak_end = _nak[2]
    if _nak_start < 24.0:
        _nak_start = -_nak_start #utils.to_dms(_tithi_start)+'(-1)'
    elif _nak_start > 24:
        _nak_start -= 24.0
    result = [_nak_no,_pad_no,_nak_start,_nak_end]+_nak[3:]
    return result
    
def nakshatra_old(jd, place):
    """
        returns the nakshatra of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return [nakshatra index, paadham index, nakshatra ending time, 
                next nakshatra index, next paadham index, next nakshatra ending time]
          next nakshatra index and next nakshatra time is additionally returned if two nakshatra on same day 
          nakshatra index = [1..27] paadham index [1..4]
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
        
    """
    """
        TODO Lunar longitude value is different than from dhasavarga function
    """
    tz = place.timezone
    # First convert jd to UTC
    y, m, d, _ = jd_to_gregorian(jd)
    jd_ut = gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2] # Changed to jd_utc in V2.9.6
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise+t, const._MOON) for t in offsets]
    nirayana_long = lunar_longitude(jd_utc) # Changed to jd_utc in V2.9.7
    nak_no,padam_no,frac_left = nakshatra_pada(nirayana_long)
    #print('moon long',nirayana_long,nak_no,padam_no,jd_utc)
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, nak_no * 360 / 27)
    ends = (rise - jd_ut + approx_end) * 24 + tz # """ Changed to jd_utc to get correct end time for the jd -  2.0.3 """
    answer = [nak_no,padam_no, utils.to_dms(ends),frac_left]
    # 4. Check for skipped nakshatra
    #nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    #isSkipped = (nak_tmrw - nak_no) % 27 > 1
    #if isSkipped:
    leap_nak = nak_no + 1
    approx_end = utils.inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
    ends = (rise - jd_utc + approx_end) * 24 + tz # """ Changed to jd_utc to get correct end time for the jd -  2.0.3 """
    leap_nak = 1 if nak_no == 27 else leap_nak
    nak_no = int(leap_nak)
    answer += [nak_no,padam_no, utils.to_dms(ends), frac_left] ## TODO: FRAC_LEFT USED HERE IS WRONG
    return answer
   
def _nakshatra_old(jd, place):
    """Current nakshatra as of julian day (jd)
       1 = Asvini, 2 = Bharani, ..., 27 = Revati
    """
    # 1. Find time of sunrise
    jd_ut = jd - place.timezone / 24.
    city, lat, lon, tz = place
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes=[]
    rise = sunrise(jd, place)[2] # V2.2.8    
    longitudes = [ lunar_longitude(rise + t) for t in offsets]
    #  print(longitudes)
    # 2. Today's nakshatra is when offset = 0
    # There are 27 Nakshatras spanning 360 degrees
    #  nak = ceil(longitudes[0] * 27 / 360)
    #  print('moon longitude=',longitudes[0])
    nak,padam_no,_ = nakshatra_pada(longitudes[0])
    #  print(nak,padam_no)
    nak_no = int(nak)
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, nak_no * 360 / 27)
    ends = (rise - jd + approx_end) * 24 + tz
    answer = [nak_no,padam_no, utils.to_dms(ends)]
    # 4. Check for skipped nakshatra
    nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    isSkipped = (nak_tmrw - nak_no) % 27 > 1
    if isSkipped:
        leap_nak = nak_no + 1
        approx_end = utils.inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
        ends = (rise - jd + approx_end) * 24 + tz
        leap_nak = 1 if nak_no == 27 else leap_nak
        nak_no = int(leap_nak)
        answer += [nak_no,padam_no, utils.to_dms(ends)]
    return answer


def yogam(jd, place):
    """
        returns the yogam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return [yogam index, yogam ending time, 
                next yogam index, next yogam ending time]
          next yogam index and next yogam time is additionally returned if two yogam on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    # 1. Find time of sunrise
    city, lat, lon, tz = place
    rise = sunrise(jd, place)[2] # V2.2.8
    
    # 2. Find the Nirayana longitudes and add them
    lunar_long = lunar_longitude(rise)
    solar_long = solar_longitude(rise)
    total = (lunar_long + solar_long) % 360
    # There are 27 Yogas spanning 360 degrees
    yog = ceil(total * 27 / 360)
    yogam_no = int(yog)
    # 3. Find how many longitudes is there left to be swept
    degrees_left = yog * (360 / 27) - total
    
    # 3. Compute longitudinal sums at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
    solar_long_diff = [ (solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets ]
    total_motion = [ moon + sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]
    
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = total_motion
    x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end - jd) * 24 + tz
    answer = [yogam_no, ends]
    # 5. Check for skipped yoga
    lunar_long_tmrw = lunar_longitude(rise + 1)
    solar_long_tmrw = solar_longitude(rise + 1)
    total_tmrw = (lunar_long_tmrw + solar_long_tmrw) % 360
    tomorrow = ceil(total_tmrw * 27 / 360)
    isSkipped = (tomorrow - yog) % 27 > 1
    if isSkipped:
        # interpolate again with same (x,y)
        leap_yog = yog + 1
        degrees_left = leap_yog * (360 / 27) - total
        approx_end = utils.inverse_lagrange(x, y, degrees_left)
        ends = (rise + approx_end - jd) * 24 + tz
        leap_yog = 1 if yog == 27 else leap_yog
        yogam_no = int(leap_yog)
        answer += [yogam_no, ends]
    return answer

def karana(jd, place):
    """
        returns the karanam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return karanam index, karanam ending time, 
          karanam index = [1..60]  1 = Kimstugna, 2 = Bava, ..., 60 = Naga
    """
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[2] # V2.2.8
    
    # 2. Find karana at this JDN
    #  solar_long = solar_longitude(rise)
    #  lunar_long = lunar_longitude(rise)
    #  moon_phase = (lunar_long - solar_long) % 360
    moon_phase = lunar_phase(jd)
    today = ceil(moon_phase / 6 )
    degrees_left = today * 6 - moon_phase
    answer = int(today)
    return answer

def vaara(jd):
    """
        Weekday for given Julian day. 
        @param jd: Julian Day Number of the date/time
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    if const.use_aharghana_for_vaara_calcuation:
        answer = ( int(ahargana(jd)) % 7 + 5) % 7
    else:
        answer = int(ceil(jd + 1) % 7)
    return answer
  
def _tamil_maadham(date_in,place):
    """
        returns tamil maadham index of the date
        @param date_in: in the datetime format
        NOTE: Does not support BC Dates 
        @return: tamil maadham index [1..12] 1=Chithirai, 12=Panguni
    """
    city, lat, lon, tz = place
    jd = gregorian_to_jd(date_in)
    sun_set = sunset(jd, place)[2]# V2.3.0 # - tz / 24.  # Sunrise at UT 00:00
    #  sr=sun_long_precessed(dt,zone)
    sr = solar_longitude(sun_set)
    #print('sun long',sr,'at',date_in)
    month_no = (int(sr/30))
    daycount=1
    dt = date_in
    while True:
      if sr%30<1 and sr%30>0:
        break
      dt = dt - timedelta(days=1)
      jdn = gregorian_to_jd(dt)
      sr=solar_longitude(jdn)
      #print('sun long',sr,'at',dt)
      daycount+=1
      #print (dt,jdn,sr,daycount)
    day_no = daycount
    return [month_no, day_no]
  
def _lunar_month(jd, place):
    """
        Returns lunar month and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: indian month index, whether leap month (adhika lunar_month) or not - boolean
            1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            True if adhika lunar_month
    """
    """ TODO: Adhika Maasa calculation to be checked """
    ti = tithi(jd, place)[0]
    critical = sunrise(jd, place)[2] # V2.2.8
    last_new_moon = new_moon(critical, ti, -1)
    next_new_moon = new_moon(critical, ti, +1)
    this_solar_month = raasi(last_new_moon,place)[0]#_raasi(last_new_moon,place)[0]
    next_solar_month = raasi(next_new_moon,place)[0]#_raasi(next_new_moon,place)[0]
    #print (jd,ti,'last new moon',last_new_moon,this_solar_month,'next new moon',next_new_moon,next_solar_month)
    is_leap_month = (this_solar_month == next_solar_month)
    __lunar_month = (this_solar_month+1)
    if __lunar_month > 12: __lunar_month = (__lunar_month % 12)
    return [int(__lunar_month), is_leap_month]
def lunar_month(jd, place):
    """
        Returns lunar month and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: indian month index, whether leap month (adhika lunar_month) or not - boolean
            1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            True if adhika lunar_month
    """
    ti = tithi(jd, place)[0]
    critical = sunrise(jd, place)[2] # V2.2.8
    last_new_moon = new_moon(critical, ti, -1)
    next_new_moon = new_moon(critical, ti, +1)
    this_solar_month = raasi(last_new_moon,place)[0]#_raasi(last_new_moon,place)[0]
    next_solar_month = raasi(next_new_moon,place)[0]#_raasi(next_new_moon,place)[0]
    #print (jd,ti,'last new moon',last_new_moon,this_solar_month,'next new moon',next_new_moon,next_solar_month)
    is_leap_month = (this_solar_month == next_solar_month)
    _lunar_month = (this_solar_month+1)
    if _lunar_month > 12: _lunar_month = (_lunar_month % 12)
    is_nija_month = False
    if not is_leap_month:
        #print('checking if current month is nija maasa')
        pm,pa,_ = lunar_month(jd-30, place)
        is_nija_month = (pm==_lunar_month and pa)
        #print('current month is nija maasa?',is_nija_month)
    return [int(_lunar_month), is_leap_month,is_nija_month]

# epoch-midnight to given midnight
# Days elapsed since beginning of Kali Yuga
ahargana = lambda jd: jd - const.mahabharatha_tithi_julian_day

def elapsed_year(jd, maasa_index):
    """
        returns Indian era/epoch year indices (kali year number, saka year and vikrama year numbers)
        @param jd: Julian Day Number of the date/time
        @param maasa_index: [1..12] (use drig.lunar_month function to get this) 
        @return kali year number, vikrama year number, saka year number 
    """
    """ TODO - may not be right for dates before Kali yuaga - to be checked """
    ahar = ahargana(jd)  # or (jd + sunrise(jd, place)[0])
    kali = int((ahar + (4 - maasa_index) * 30) / const.sidereal_year)
    year = jd_to_gregorian(jd)[0]
    #kali = 3101+year
    saka = kali - 3179
    vikrama = saka + 135
    return kali, vikrama, saka

# New moon day: sun and moon have same longitude (0 degrees = 360 degrees difference)
# Full moon day: sun and moon are 180 deg apart
def new_moon(jd, tithi_, opt = -1):
    """Returns JDN, where
       opt = -1:  JDN < jd such that lunar_phase(JDN) = 360 degrees
       opt = +1:  JDN >= jd such that lunar_phase(JDN) = 360 degrees
    """
    if opt == -1:  start = jd - tithi_         # previous new moon
    if opt == +1:  start = jd + (30 - tithi_)  # next new moon
    # Search within a span of (start +- 2) days
    x = [ -2 + offset/4 for offset in range(17) ]
    y = [lunar_phase(start + i) for i in x]
    y = utils.unwrap_angles(y)
    y0 = utils.inverse_lagrange(x, y, 360)
    return start + y0

def _raasi(jd, place):
    """Tithi at sunrise for given date and place. Also returns tithi's end time."""
    city, lat, lon, tz = place
    rise = sunrise(jd, place)[2] # V2.2.8
    moon_longitude = lunar_longitude(jd)
    if (moon_longitude > 360):
        moon_longitude -= 360
    raasi_durn = 360/12
    raasi_no = ceil(moon_longitude / raasi_durn)
    raasi_remaining = moon_longitude- (raasi_no-1)*raasi_durn
    #raasi = RAASI_LIST[raasi_no-1]
    moon_daily_motion = _lunar_daily_motion(jd)
    raasi_remain_degrees = (raasi_no*raasi_durn) - moon_longitude
    sun_rise_time = (rise - jd) * 24 + tz
    raasi_ends_at = ( sun_rise_time + raasi_remain_degrees*24/(moon_daily_motion) ) % 360
    #  raasi_end_time = (rise - jd + raasi_ends_at) * 24 + tz
    #      print(moon_longitude,raasi_no,nak_no,moon_daily_motion,raasi_remain_degrees,nak_remain_degrees,raasi_ends_at,nak_ends_at)
    answer = [raasi_no, utils.to_dms(raasi_ends_at)]
    
    return answer

def __raasi(jd,place):
    """Zodiac of given jd. 1 = Mesha, ... 12 = Meena"""
    city, lat, lon, tz = place
    rise = sunrise(jd, place)[2] # V2.2.8
    
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [ solar_longitude(rise + t) for t in offsets]
    raasi_durn = 360/12
    solar_nirayana = longitudes[0]
    # 12 rasis occupy 360 degrees, so each one is 30 degrees
    raasi_no = ceil(solar_nirayana / raasi_durn)
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, raasi_no * raasi_durn)
    ends = (rise - jd + approx_end) * 24 + tz
    #  print('raasi end time',ends)
    answer = [raasi_no, utils.to_dms(ends)]
    
    return answer
  
def lunar_phase(jd):
    solar_long = solar_longitude(jd)
    lunar_long = lunar_longitude(jd)
    moon_phase = (lunar_long - solar_long) % 360
    return moon_phase
def _get_previous_chaitra_month_date(jd,place):
    """TODO: DO NOT USE THIS - UNDER TESTING """
    lm = lunar_month(jd, place)
    jd -= 30*lm[0]
    for d in range(366):
        lm = lunar_month(jd, place)
        if lm[0] == 1:
            break
        jd+=1
    print('previous chaitra date',utils.jd_to_gregorian(jd))
    return utils.jd_to_gregorian(jd)
    
def samvatsara(panchanga_date,place,maasa_index,zodiac=None):
    """ TODO: Chithirai always shows previous year """
    """ Should we use previous sakranti which is solar based? 
        Is there an algorithm for lunar samvastra?
    """ 
    """ Note lunar_month returns lunar month but tamil_month_date returns solar month """
    ps = _previous_sankranti_date_new(panchanga_date, place,zodiac=zodiac)
    year = ps[0][0]
    #print('previous sankranti date',ps)
    #year,_,_,_ = _get_previous_chaitra_month_date(jd, place)
    #print('prev sank',ps,maasa_index)
    """
    if month < const.lunar_gregory_month_max and month < maasa_index:
        year -= 1
    """
    sv = (year-1926)%60
    if sv==0:
        sv=60
    return sv
def _samvatsara_old(jd, maasa_index,north_indian_tradition=False,method=1):
    """
        return the year name index for the given julian day number of the date
        @param jd: Julian Day Number of the date/time
        @param maasa_index: [1..12] (use drig.lunar_month function to get this) 
        @param north_indian_tradition: Set to to True
            Note: South Indian year names are off by 14 years compared to North Indian Tradition after Kali Year 4009.
        @return year/samvastara index
          1=Prabhava, 2=Vibhava... 59=Krodhana, 60=Akshaya
    """
    """ TODO: Year name/number is wrong for BCE dates especially before Kali yuga """
    """ TODO: Year number is wrong every 26/27/28 years """
    if method == 1:
        year,month,_,_ = utils.jd_to_gregorian(jd)
        """ This is cheap trick to get lunar year """
        if month < const.lunar_gregory_month_max and month < maasa_index:
            year -= 1
        sv = (year-1926)%60
        if sv==0:
            sv=60
        return sv
    else:
        kali_off = 14
        if north_indian_tradition: kali_off = 0
        kali = elapsed_year(jd, maasa_index)[0]
        # Change 14 to 0 for North Indian tradition
        # See the function "get_Jovian_Year_name_south" in pancanga.pl
        if kali >= 4009:    kali = (kali - kali_off) % 60
        samvat = (kali + 27 + int((kali * 211 - 108) / 18000)) % 60
        if samvat==0:
            samvat=60
        return samvat
def ritu(maasa_index):
    """ returns ritu / season index. 
        @param maasa_index: [1..12] (use drig.lunar_month function to get this) 
        @return: ritu index  0 = Vasanta,...,5 = Shishira
    """
    return (maasa_index - 1) // 2

def day_duration(jd, place):
    """ TODO THIS IS INCORRECT - USE day_length() """
    srise = sunrise(jd, place)[2] # V2.2.8
    sset = sunset(jd, place)[2] # V2.2.8
    diff = (sset - srise) * 24     # In hours
    return [diff, utils.to_dms(diff)]
def gauri_chogadiya(jd, place):
    """
        Get end times of gauri chogadiya for the given julian day
        Chogadiya is 1/8th of daytime or nighttime practiced as time measure in North India 
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: end times of chogadiya as a list
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    city, lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    
    end_times = []
    for i in range(1, 9):
      end_times.append(utils.to_dms((srise + (i * day_dur) / 8 - jd) * 24 + tz))
    
    # Night duration = time from today's sunset to tomorrow's sunrise
    srise = swe.rise_trans((jd + 1) - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    night_dur = (srise - sset)
    for i in range(1, 9):
        end_times.append(utils.to_dms((sset + (i * night_dur) / 8 - jd) * 24 + tz))
    
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
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    city, lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    weekday = vaara(jd)
    
    # value in each array is for given weekday (0 = sunday, etc.)
    offsets = { 'raahu kaalam': [0.875, 0.125, 0.75, 0.5, 0.625, 0.375, 0.25],
                'gulikai': [0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0.0],
                'yamagandam': [0.5, 0.375, 0.25, 0.125, 0.0, 0.75, 0.625] }
    
    start_time = srise + day_dur * offsets[option][weekday]
    end_time = start_time + 0.125 * day_dur
    
    # to local timezone
    start_time = (start_time - jd) * 24 + tz
    end_time = (end_time - jd) * 24 + tz
    start_time = utils.to_dms(start_time)
    end_time = utils.to_dms(end_time)
    
    return [start_time, end_time] # decimal hours to H:M:S

raahu_kaalam = lambda jd, place: trikalam(jd, place, 'raahu kaalam')
yamaganda_kaalam = lambda jd, place: trikalam(jd, place, 'yamagandam')
gulikai_kaalam = lambda jd, place: trikalam(jd, place, 'gulikai')

def durmuhurtam(jd, place):
    """
        Get dhur muhurtham timing for the given julian day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: start and end time of dhur muhurtham - as list e.g. [start_time, end_time]
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    city, lat, lon, tz = place
    tz = place.timezone
    
    # Night = today's sunset to tomorrow's sunrise
    sset = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)[1][0]
    srise = swe.rise_trans((jd + 1) - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    night_dur = (srise - sset)
    
    # Day = today's sunrise to today's sunset
    srise = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    day_dur = (sset - srise)
    
    weekday = vaara(jd)
    
    # There is one durmuhurtam on Sun, Wed, Sat; the rest have two
    offsets = [[10.4, 0.0],  # Sunday
               [6.4, 8.8],   # Monday
               [2.4, 4.8],   # Tuesday, [day_duration , night_duration]
               [5.6, 0.0],   # Wednesday
               [4.0, 8.8],   # Thursday
               [2.4, 6.4],   # Friday
               [1.6, 0.0]]   # Saturday
    
    # second durmuhurtam of tuesday uses night_duration instead of day_duration
    dur = [day_dur, day_dur]
    base = [srise, srise]
    if weekday == 2:  dur[1] = night_dur; base[1] = sset
    
    # compute start and end timings
    start_times = [0, 0]
    end_times = [0, 0]
    answer = []
    for i in range(0, 2):
      offset = offsets[weekday][i]
      if offset != 0.0:
        start_times[i] = base[i] + dur[i] * offsets[weekday][i] / 12
        end_times[i] = start_times[i] + day_dur * 0.8 / 12
    
        # convert to local time
        start_times[i] = (start_times[i] - jd) * 24 + tz
        end_times[i] = (end_times[i] - jd) * 24 + tz
        start_times[i] = utils.to_dms(start_times[i])
        end_times[i] = utils.to_dms(end_times[i])
        answer += [start_times[i],end_times[i]]
            
    return answer
#  return [start_times, end_times]  # in decimal hours

def abhijit_muhurta(jd, place):
    """
        Get Abhijit muhurta timing for the given julian day
        Abhijit muhurta is the 8th muhurta (middle one) of the 15 muhurtas during the day_duration (~12 hours)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: start and end time of Abhijit muhurta - as list e.g. [start_time, end_time]
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    city, lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    
    start_time = srise + 7 / 15 * day_dur
    end_time = srise + 8 / 15 * day_dur
    start_time = (start_time - jd) * 24 + tz
    end_time = (end_time - jd) * 24 + tz
    start_time = utils.to_dms(start_time)
    end_time = utils.to_dms(end_time)
    # to local time
    return [start_time, end_time]

# 'jd' can be any time: ex, 2015-09-19 14:20 UTC
# today = swe.julday(2015, 9, 19, 14 + 20./60)
def planetary_positions(jd, place):
    """
        Computes instantaneous planetary positions (i.e., which celestial object lies in which constellation)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: 2D List of [ [planet index, planet longitude, planet constellation],...]]
            Example: [ [0,87.32148,2],...] - Sun longitude 87.32148, Gemini,...
        Note: Planet list is by default Sun to Kethu and does not include Uranus/Neptune/Pluto
              if drig.set_tropical_planets() is used then Uranus/Neptune/Plutoare used instead of Rahu/Ketu
        Note: swiss ephimeris does not include Rahu and Ketu. Rahu is mapped to MEAN_MODE (Planet index = 10)
            And Ketu is calculated 180 degrees from Rahu/Mean Mode.
            Though Rahu's ephimeris planet index is 10, we use 7 and 8 respectively in charts respectively.
        NOTE:DOES NOT INCLUDE ASCENDANT POSITION AND LONGITUDE
        TO GET ASCENDANT CALL: dasavarga_from_long() or ascendant()
    """
    jd_ut = jd - place.timezone / 24.
    
    positions = []
    #print('planet list',planet_list)
    for planet in planet_list:
        p_id = planet_list.index(planet)
        #print('planet in planetrary positions',planet,p_id,'ketu=',swe.KETU)
        if planet == const._KETU:
            nirayana_long = ketu(sidereal_longitude(jd_ut, const._RAHU))
        else: # Ketu
            nirayana_long = sidereal_longitude(jd_ut, planet)
        #nak_no,paadha_no,_ = nakshatra_pada(nirayana_long)
        # 12 zodiac signs span 360°, so each one takes 30°
        # 0 = Mesha, 1 = Vrishabha, ..., 11 = Meena
        constellation = int(nirayana_long / 30)
        coordinates = nirayana_long-constellation*30
        #    positions.append([planet, constellation, coordinates, nakshatra_pada(nirayana_long)])
        positions.append([p_id,coordinates, constellation])
        
    return positions
def bhaava_madhya(jd, place):
    if const.bhaava_madhya_method.upper() == "SWISS":
        return bhaava_madhya_swe(jd, place)
    else: # SRIPATI METHOD
        return bhaava_madhya_sripathi(jd, place)
def bhaava_madhya_swe(jd,place):
    """
        Compute the mid angle / cusp of each of each house.
        0th element is ascendant, 9th element is mid-heaven (mid coeli) etc 
    """
    global _ayanamsa_mode,_ayanamsa_value
    _, lat, lon, tz = place
    jd_utc = jd - (tz / 24.)
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SIDEREAL
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd) # needed for swe.houses_ex()
    return list(swe.houses_ex(jd_utc, lat, lon, flags = flags)[0])
def bhaava_madhya_sripathi(jd, place):
    bm = bhaava_madhya_swe(jd, place)
    #print(bm)
    bmf = [0,3,6,9,12]
    for b in bmf[1:]:
        ib = bmf.index(b)
        bi1 = bmf[ib-1]%12
        bi2 = bmf[ib]%12
        b1 = bm[bi1]
        b2 = bm[bi2]
        if b2 < b1:
            b2 += 360
        bd = abs(b2-b1)/3.0
        #print(ib,bi1,bm[bi1],bi2,bm[bi2],bd)
        bm[(bi1+1)%12] = (bm[bi1%12]+bd)%360
        bm[(bi2-1)%12] = (bm[bi2%12]-bd)%360
        #print((bi1+1)%12,bm[(bi1+1)%12],(bi2-1)%12,bm[(bi2-1)%12])
    return bm
def ascendant(jd, place):
    """
        Compute Lagna (=ascendant) position/longitude at any given time & place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: [constellation of Lagna, longitude of lagna, Lagna nakshatra number, Lagna paadham number]
    """
    global _ayanamsa_mode,_ayanamsa_value
    city, lat, lon, tz = place
    jd_utc = jd - (tz / 24.)
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SIDEREAL
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd) # needed for swe.houses_ex()
    # returns two arrays, cusps and ascmc, where ascmc[0] = Ascendant
    nirayana_lagna = swe.houses_ex(jd_utc, lat, lon, flags = flags)[1][0]
    #print('ascendant nirayana_lagna',nirayana_lagna)
    nak_no,paadha_no,_ = nakshatra_pada(nirayana_lagna)
    # 12 zodiac signs span 360°, so each one takes 30°
    # 0 = Mesha, 1 = Vrishabha, ..., 11 = Meena
    constellation = int(nirayana_lagna / 30)
    coordinates = nirayana_lagna-constellation*30
    
    reset_ayanamsa_mode()
    return [constellation, coordinates, nak_no, paadha_no]    
def dasavarga_from_long(longitude, divisional_chart_factor):
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
    if divisional_chart_factor not in const.division_chart_factors:
        raise ValueError("Wrong divisional_chart_factor",divisional_chart_factor,' Valid value:',const.division_chart_factors)
    one_pada = (360.0 / (12 * divisional_chart_factor))  # There are also 108 navamsas
    one_sign = 12.0 * one_pada    # = 40 degrees exactly
    signs_elapsed = longitude / one_sign
    fraction_left = signs_elapsed % 1
    constellation = int(fraction_left * 12)
    long_in_raasi = (longitude-(constellation*30)) % 30
    " if long_in_raasi 30 make it and zero and add a rasi"
    if int(long_in_raasi+0.000001) == 30:
        long_in_raasi = 0; constellation = (constellation+1)%12
    #print(longitude,signs_elapsed,fraction_left,constellation,long_in_raasi)
    return constellation,long_in_raasi

navamsa_from_long = lambda longitude: dasavarga_from_long(longitude,9) 

# http://www.oocities.org/talk2astrologer/LearnAstrology/Details/Navamsa.html
# Useful for making D9 divisional chart
def navamsa_from_long_old(longitude):
    """Calculates the navamsa-sign in which given longitude falls
    0 = Aries, 1 = Taurus, ..., 11 = Pisces
    """
    one_pada = (360 / (12 * 9))  # There are also 108 navamsas
    one_sign = 12 * one_pada    # = 40 degrees exactly
    signs_elapsed = longitude / one_sign
    fraction_left = signs_elapsed % 1
    return int(fraction_left * 12)

def dhasavarga(jd, place,divisional_chart_factor):
    """
        Calculate planet positions for a given divisional chart index
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param divisional_chart_factor: divisional chart index as below. 
          divisional_chart_factor = 1=> Rasi, 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: 2D List of planet positions in the following format:
        [ [planet_index,[planet_raasi, planet_longitude],...]
        The planet index is in range [0..8]
        NOTE:DOES NOT INCLUDE ASCENDANT POSITION AND LONGITUDE
        TO GET ASCENDANT CALL: dasavarga_from_long()
    """
    #y, m, d, _ = jd_to_gregorian(jd)
    #jd_utc = gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    positions = []
    for planet in planet_list:
        p_id = planet_list.index(planet)
        if planet != const._KETU:
            nirayana_long = sidereal_longitude(jd_utc, planet)
        else: # Ketu
            nirayana_long = ketu(sidereal_longitude(jd_utc, const._RAHU)) # 7 = swe.RAHU
        #print(p_id,planet,nirayana_long)
        divisional_chart = dasavarga_from_long(nirayana_long,divisional_chart_factor)
        positions.append([p_id, divisional_chart])
    #print('drik.dhasavarga planet positions',h_to_p)
    return positions
def declination_of_planets(jd,place):
    pp = dhasavarga(jd,place,divisional_chart_factor=1)[:7]
    bhujas = [0 for _ in range(7)]
    north_south_sign = [1 for _ in range(7)]
    #print(pp)
    for p,(h,long) in pp:
        p_long = h*30 + long #planet positions already are Sayana Longitude
        if p_long >= 0.0 and p_long < 180.0: # North
            north_south_sign[p] = -1
            if p in [0,2,4,5]:
                north_south_sign[p] = 1
        else: # South
            north_south_sign[p] = -1
            if p in [1,6]:
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
    bx = [i*15 for i in range(7)]
    #print(bx,bd)
    declinations = [0 for _ in range(7)]
    for p in range(7):
        declinations[p] = north_south_sign[p] * utils.inverse_lagrange(bd, bx, bhujas[p])
        #print('bhujas and declination',p,bhujas[p],declinations[p])
    return declinations
def navamsa(jd, place):
  """Calculates navamsa of all planets"""
  jd_utc = jd - place.timezone / 24.

  positions = []
  for planet in planet_list:
    p_id = planet_list.index(planet)
    if planet != const._KETU:
      nirayana_long = sidereal_longitude(jd_utc, planet)
    else: # Ketu
      nirayana_long = ketu(sidereal_longitude(jd_utc, const._RAHU)) # 7 = swe.RAHU

    positions.append([[planet,nirayana_long], navamsa_from_long(nirayana_long)])
  return positions

### --- Vimoshatari functions
def _next_adhipati(lord):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.adhipati_list.index(lord)
    next_index = (current + 1) % len(const.adhipati_list)
    return const.adhipati_list[next_index]

def nakshatra_position(jdut1,star_position_from_moon=1):
    """Get the Nakshatra index and degrees remaining at a given JD(UT1) """ # changed traversed to remaining in V2.6.1
    """Note: star_position_from_moon can also take values 4,5,8 
    (namely kshema, utpanna and adhana stars. Other values default to 1"""
    if star_position_from_moon not in [1,4,5,8]:
        print('Warning:function nakshatra_position takes only one of [1,4,5,8] for the argument: star_position_from_moon')
        star_position_from_moon=1
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    moon = sidereal_longitude(jdut1, swe.MOON)+(star_position_from_moon-1)*one_star
    nak = int(moon / one_star)
    rem = (moon - nak * one_star) # degrees traversed in given nakshatra
    #print('moon longitude',utils.to_dms(moon,is_lat_long='plong'),nak,utils.to_dms(rem,is_lat_long='plong'),utils.to_dms(one_star,is_lat_long='plong'),(one_star-rem)/one_star)
    return [nak, rem]
# Return nakshatra lord (adhipati)
adhipati = lambda nak: const.adhipati_list[nak % (len(const.adhipati_list))]

def dasha_start_date(jdut1):
    """Returns the start date (UT1) of the mahadasa which occured on or before `jd(UT1)`"""
    nak, rem = nakshatra_position(jdut1)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    lord = adhipati(nak)          # ruler of current nakshatra
    period = const.mahadasa[lord]       # total years of nakshatra lord
    period_elapsed = rem / one_star * period # years
    period_elapsed *= const.sidereal_year        # days
    start_date = jdut1 - period_elapsed      # so many days before current day

    return [lord, start_date]

def vimsottari_mahadasa(jdut1):
    """List all mahadashas and their start dates"""
    lord, start_date = dasha_start_date(jdut1)
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        start_date += const.mahadasa[lord] * const.sidereal_year
        lord = _next_adhipati(lord)

    return retval

def _vimsottari_bhukti(maha_lord, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = const.mahadasa[lord] * const.mahadasa[maha_lord] / const.human_life_span_for_dhasa
        start_date += factor * const.sidereal_year
        lord = _next_adhipati(lord)

    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def _vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = const.mahadasa[lord] * (const.mahadasa[maha_lord] / const.human_life_span_for_dhasa)
        factor *= (const.mahadasa[bhukti_lord] / const.human_life_span_for_dhasa)
        start_date += factor * const.sidereal_year
        lord = _next_adhipati(lord)

    return retval


def _where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


def _compute_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = _where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = _vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = _where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = _vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)

def get_dhasa_bhukthi(jd, place):
    # jd is julian date with birth time included
    city,lat,long,tz = place
    jdut1 = jd - tz/24
    dashas = vimsottari_mahadasa(jdut1)
    #print('dasha lords',dashas)
    dhasa_bukthi=[]
    for i in dashas:
        #print(' ---------- ' + get_dhasa_name(i) + ' ---------- ')
        bhuktis = _vimsottari_bhukti(i, dashas[i])
        dhasa_lord = i
        for j in bhuktis:
            bhukthi_lord = j
            jd = bhuktis[j]
            y, m, d, h = swe.revjul(round(jd + tz))
            date_str = '%04d-%02d-%02d' %(y,m,d)
            bhukthi_start = date_str
            dhasa_bukthi.append([dhasa_lord,bhukthi_lord,bhukthi_start]) 
            #dhasa_bukthi[i][j] = [dhasa_lord,bhukthi_lord,bhukthi_start]
    return dhasa_bukthi

### --- get tamil date private functions
def _fract(x):
    return x - int(x)


def _cd_to_jd(gdate):
    """Convert Greenwich date to Julian date."""
    result = 1721424.5 + gdate.toordinal()
    try:
        return result + (gdate.hour * 3600 + gdate.minute * 60 +
                         gdate.second + gdate.microsecond * 1e-6) / 86400.0
    except AttributeError:
        # date parameter is of type 'date' instead of 'datetime'
        return result

def _jd_to_cd(jd):
    """Convert Julian date to calendar date."""
    date = jd - 1721424.5
    result = datetime.datetime.fromordinal(int(date))
    result += datetime.timedelta(seconds=86400.0 * _fract(date))
    return result
def _eccentric_anomaly(am, ec):
    """Return eccentric anomaly for given mean anomaly and eccentricity.

    am: mean anomaly
    ec: eccentricity,
    """
    m = am % (2 * math.pi)
    ae = m
    while 1:
        d = ae - (ec * math.sin(ae)) - m
        if abs(d) < 0.000001:
            break
        ae -= d / (1.0 - (ec * math.cos(ae)))
    return ae


def _true_anomaly(am, ec):
    """Return true anomaly for given mean anomaly and eccentricity.

    am: mean anomaly
    ec: eccentricity,
    """
    ae = _eccentric_anomaly(am, ec)
    return 2.0 * math.atan(math.sqrt((1.0 + ec) / (1.0 - ec)) * math.tan(ae * 0.5))

  
def _get_ayan(year, month, day):
    a = 16.90709 * year/1000 - 0.757371 * year/1000 * year/1000 - 6.92416100010001000
    b = (month-1 + day/30) * 1.1574074/1000
    return -(a+b)

def _sun_long(gdate, zone):
    """Return sun longitude in degrees for given Greenwich datetime (UTC)."""

    t = (_cd_to_jd(gdate) - 2415020.0 + zone/24.0) / 36525.0
    t2 = t * t

    l = 279.69668 + 0.0003025 * t2 + 360.0 * _fract(100.0021359 * t)
    m1 = 358.47583 - (0.00015 + 0.0000033 * t) * t2 + 360.0 * _fract(99.99736042 * t)
    ec = 0.01675104 - 0.0000418 * t - 0.000000126 * t2

    # sun anomaly
    at = _true_anomaly(math.radians(m1), ec)

    a1 = math.radians(153.23 + 360.0 * _fract(62.55209472 * t))
    b1 = math.radians(216.57 + 360.0 * _fract(125.1041894 * t))
    c1 = math.radians(312.69 + 360.0 * _fract(91.56766028 * t))
    d1 = math.radians(350.74 - 0.00144 * t2 + 360.0 * _fract(1236.853095 * t))
    e1 = math.radians(231.19 + 20.2 * t)
    h1 = math.radians(353.4 + 360.0 * _fract(183.1353208 * t))

    d2 = (0.00134 * math.cos(a1) + 0.00154 * math.cos(b1) + 0.002 * math.cos(c1) +
          0.00179 * math.sin(d1) + 0.00178 * math.sin(e1))

    sr = (at + math.radians(l - m1 + d2)) % (2 * math.pi)
    return math.degrees(sr)
  
def _sun_long_precessed(gdate, zone):
    t = (_cd_to_jd(gdate) - 2415020.0 + zone/24.0) / 36525.0
    sr = _sun_long(gdate, zone)
    ay = _get_ayan(gdate.year, gdate.month, gdate.day+gdate.hour/24.0)
    return sr+ay

def tamil_date(date_in,jd, place):
  """
      TODO: Does not work for BC Dates as datetime is used
  """
  city, lat, lon, tz = place
#  hour,minute=18,10
  #[sunset_hour,sunset_minute,sunset_second] = sunset(jd,place)[1]
  sset = sunset(jd,place)[1]
  [sunset_hour,sunset_minute,sunset_second] = [int(ss) for ss in sset.replace(' AM','').replace(' PM','').split(':')]
  #print(sunset_hour,sunset_minute,sunset_second)
#  print('sunset',hour,minute,seconds)
  zone=-tz
  dt=datetime(date_in.year,date_in.month,date_in.day,sunset_hour,sunset_minute,sunset_second)
  sr=_sun_long_precessed(dt,zone)
#  print('sun long',sr,'at',dt)
#  print(month_names[int(sr/30)])
  daycount=1
  while True:
    if sr%30<1 and sr%30>0:
      break
    dt = dt - timedelta(days=1)
    sr=_sun_long_precessed(dt,zone)
#    print('sun long',sr,'at',dt)
    daycount+=1
  return daycount
### Upagraha longitudes
_dhuma_longitude = lambda sun_long: (sun_long+133+20.0/60) % 360
_vyatipaata_longitude = lambda sun_long: (360.0 - _dhuma_longitude(sun_long))%360
_parivesha_longitude = lambda sun_long: (_vyatipaata_longitude(sun_long)+180.0) % 360
_indrachaapa_longitude = lambda sun_long: (360.0-_parivesha_longitude(sun_long))%360
_upaketu_longitude = lambda sun_long: (sun_long-30.0)%360
def solar_upagraha_longitudes(solar_longitude,upagraha,divisional_chart_factor=1):
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
        long = eval('_'+upagraha+"_longitude(solar_longitude)")
        constellation,coordinates = dasavarga_from_long(long, divisional_chart_factor) #int(long/30)
        return [constellation,coordinates]
"""
  Kaala rises at the middle of Sun’s part. In other words, we find the time at the
  middle of Sun’s part and find lagna rising then. That gives Kaala’s longitude.
"""
kaala_longitude = lambda dob,tob,place,divisional_chart_factor=1: upagraha_longitude(dob,tob,place,planet_index=0,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Mrityu rises at the middle of Mars’s part."""
mrityu_longitude = lambda dob,tob,place,divisional_chart_factor=1: upagraha_longitude(dob,tob,place,planet_index=2,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Artha Praharaka rises at the middle of Mercury’s part."""
artha_praharaka_longitude = lambda dob,tob,place,divisional_chart_factor=1: upagraha_longitude(dob,tob,place,planet_index=3,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Yama Ghantaka rises at the middle of Jupiter’s part. """
yama_ghantaka_longitude = lambda dob,tob,place,divisional_chart_factor=1: upagraha_longitude(dob,tob,place,planet_index=4,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Gulika rises at the start of Saturn’s part. (Book says middle) """
gulika_longitude = lambda dob,tob,place,divisional_chart_factor=1: upagraha_longitude(dob,tob,place,planet_index=6,divisional_chart_factor=divisional_chart_factor,upagraha_part='begin')
""" Maandi rises at the middle of Saturn’s part. (Book says start) """
maandi_longitude = lambda dob,tob,place,divisional_chart_factor=1: upagraha_longitude(dob,tob,place,planet_index=6,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')

def upagraha_longitude(dob,tob,place,planet_index,divisional_chart_factor=1,upagraha_part='middle'):
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
          Since Artha Prabhakara is upagraha of Mercury so planet_index should be 3
              Artha Praharaka rises at the middle of Mercury’s part.
          Since Kaala is upagraha of Jupiter so planet_index should be 4
              Yama Ghantaka rises at the middle of Jupiter’s part.
          Since Gulika is upagraha of Saturn so planet_index should be 6
              Gulika rises at the middle of Saturn’s part.
          Since Maandi is upagraha of Saturn so planet_index should be 6
              Maandi rises at the beginning of Saturn’s part.
          You can use specific lambda functions for these.
      @param as_string = return results as string or list. True or False
      @return: [constellation of upagraha,upagraha_longitude within constellation]
    """
    jd_utc = gregorian_to_jd(Date(dob.year,dob.month,dob.day))
    tz = place.timezone
    #day_rulers = [[0,1,2,3,4,5,6,-1],[1,2,3,4,5,6,-1,0],[2,3,4,5,6,-1,0,1],[3,4,5,6,-1,0,1,2],[4,5,6,-1,0,1,2,3],[5,6,-1,0,1,2,3,4],[6,-1,0,1,2,3,4,5]]
    #night_rulers = [[4,5,6,-1,0,1,2,3],[5,6,-1,0,1,2,3,4],[6,-1,0,1,2,3,4,5],[0,1,2,3,4,5,6,-1],[1,2,3,4,5,6,-1,0],[2,3,4,5,6,-1,0,1],[3,4,5,6,-1,0,1,2]]
    day_number = vaara(jd_utc)
    srise = sunrise(jd_utc, place)[1]
    srise = [int(ss) for ss in srise.replace(' AM','').replace(' PM','').split(':')]
    sset = sunset(jd_utc, place)[1]
    sset = [int(ss) for ss in sset.replace(' AM','').replace(' PM','').split(':')]
    srise = srise[0]+srise[1]/60.0+srise[2]/3600.0
    sset = sset[0]+sset[1]/60.0+sset[2]/3600.0
    planet_part = const.day_rulers[day_number].index(planet_index)            
    tob_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
    if tob_hrs < srise: # Previous day sunset to today's sunrise
        sset = sunset((jd_utc-1), place)[1]
        sset = [int(ss) for ss in sset.replace(' AM','').replace(' PM','').split(':')]
        sset = sset[0]+sset[1]/60.0+sset[2]/3600.0
        planet_part = const.night_rulers[day_number].index(planet_index)
    if tob_hrs > sset: # today's sunset to next sunrise
        srise = sunrise((jd_utc+1), place)[1]
        srise = [int(ss) for ss in srise.replace(' AM','').replace(' PM','').split(':')]
        #print('sunrise',srise)
        srise = srise[0]+srise[1]/60.0+srise[2]/3600.0
        planet_part = const.night_rulers[day_number].index(planet_index)            
    day_dur = abs(sset - srise)
    one_part = day_dur/8.0
    planet_start_time = srise + planet_part * one_part
    if upagraha_part.lower()=='middle':
        planet_end_time = srise + (planet_part+1)*one_part
        planet_middle_time = 0.5*(planet_start_time+planet_end_time)
        jd_kaala = swe.julday(dob.year,dob.month,dob.day,planet_middle_time)
    else:
        jd_kaala = swe.julday(dob.year,dob.month,dob.day,planet_start_time)
    clong = ascendant(jd_kaala, place) #2.0.3
    upagraha_long = clong[0]*30+clong[1] #2.0.3
    constellation,coordinates = dasavarga_from_long(upagraha_long, divisional_chart_factor) #int(upagraha_long / 30)
    return [constellation,coordinates]
bhava_lagna = lambda jd,place,divisional_chart_factor=1: special_ascendant(jd,place,lagna_rate_factor=1.0,divisional_chart_factor=divisional_chart_factor) 
hora_lagna = lambda jd,place,divisional_chart_factor=1: special_ascendant(jd,place,lagna_rate_factor=0.5,divisional_chart_factor=divisional_chart_factor) 
ghati_lagna = lambda jd,place,divisional_chart_factor=1: special_ascendant(jd,place,lagna_rate_factor=1.25,divisional_chart_factor=divisional_chart_factor) 
def special_ascendant(jd,place,lagna_rate_factor=1.0,divisional_chart_factor=1):
    """
        Get constellation and longitude of special lagnas (Bhava Lagna, Hora Lagna and Ghato Lagna)
        For Sree Lagna use sree_lagna function
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param time_of_birth_in_hours: Time of birth in hours. example 5:37 PM = 17.37
        @param lagna_rate_factor:    
            lagna_rate_factor   = 1 for Bhava Lagna
                                = 0.5 for Hora Lagna
                                = 5/4 for Ghati Lagna                            
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [special lagnas constellation, special lagna's longitude within constellation]
    """
  # First convert jd to UTC
    y, m, d, time_of_birth_in_hours = jd_to_gregorian(jd)
    #print('special lagna',time_of_birth_in_hours)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    srise_jd = sunrise(jd, place)[2] #V2.3.1 Get sunrise JD - as we need sun longitude at sunrise
    _,_,_,sun_rise_hours = utils.jd_to_gregorian(srise_jd)
    #print('sun_rise_hours',sun_rise_hours)
    time_diff_mins = (time_of_birth_in_hours-sun_rise_hours)*60
    sun_long = solar_longitude(srise_jd) #V2.3.1 Use JD at sunrise to get sun longitude at sunrise
    #print('sun_long',sun_long)
    spl_long = (sun_long + (time_diff_mins * lagna_rate_factor) ) % 360
    da = dasavarga_from_long(spl_long, divisional_chart_factor)
    return da
def sree_lagna(jd,place,divisional_chart_factor=1):
    """
        Get constellation and longitude of Sree Lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [Sree lagna constellation, Sree lagna's longitude within constellation]
    """
    ascendant_constellation, ascendant_longitude, _, _ = ascendant(jd,place)
    ascendant_index = const._ascendant_symbol
    planet_positions = dhasavarga(jd,place,divisional_chart_factor=divisional_chart_factor)
    planet_positions = [[ascendant_index,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sl = sree_lagna_from_moon_asc_longitudes(moon_long, asc_long, divisional_chart_factor=divisional_chart_factor)
    return sl
def sree_lagna_from_moon_asc_longitudes(moon_longitude,ascendant_longitude,divisional_chart_factor=1):
    moon_long = moon_longitude
    asc_long = ascendant_longitude
    reminder = nakshatra_pada(moon_long)[2]
    one_rasi = 360 / 27
    reminder_fraction = reminder * 27
    sree_long = asc_long + reminder_fraction
    constellation,coordinates = dasavarga_from_long(sree_long, divisional_chart_factor)
    return constellation,coordinates
def tamil_solar_month_and_date(panchanga_date,place):
    """ Tamil month is sankranti based solar month - not lunar month""" 
    jd = gregorian_to_jd(panchanga_date)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd)
    _tamil_month = int(sl/30)
    daycount=1
    while True:
        if sl%30<1 and sl%30>0:
            break
        sunset_jd -= 1
        sl = solar_longitude(sunset_jd)
        daycount+=1
    _tamil_day = daycount
    return _tamil_month, _tamil_day#, month_days
def days_in_tamil_month(panchanga_date,place):
    """ get # of days in that tamil month """
    jd = gregorian_to_jd(panchanga_date)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd)
    _,daycount = tamil_solar_month_and_date(panchanga_date, place)
    while True:
        if sl%30<30 and sl%30>29:
            break
        sunset_jd += 1
        sl = solar_longitude(sunset_jd)
        daycount+=1
    month_days = daycount
    return month_days
def _previous_sankranti_date_new(panchanga_date,place,zodiac=None):
    prev_day = utils.previous_panchanga_day(panchanga_date, minus_days=1)
    if zodiac is None:
        t_month,_ = tamil_solar_month_and_date(prev_day, place)
        multiple = t_month * 30
    else:
        multiple = zodiac * 30
    #print(prev_day,t_month,t_day)
    jd = gregorian_to_jd(prev_day)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd)
    while True:
        slq,slr = divmod(sl,30)
        if slr<1 and slr>0 and zodiac is None:
            break
        if slr<1 and slr>0 and zodiac is not None and int(slq)==int(zodiac):
            break
        sunset_jd -= 1
        sl = solar_longitude(sunset_jd)
    sank_date = jd_to_gregorian(sunset_jd)
    sank_sunrise = sunrise(sunset_jd,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    tamil_month,tamil_day = tamil_solar_month_and_date(sank_date, place)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    solar_longs = [ solar_longitude(sank_sunrise + t) % 360 for t in offsets ]
    solar_hour = utils.inverse_lagrange(offsets, solar_longs, multiple % 360) # Do not move % 360 above
    sank_jd_utc = gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    #print('before tm call sank date',sank_date,solar_hour,solar_hour1)
    sank_date,solar_hour1 = utils._convert_to_tamil_date_and_time(sank_date, solar_hour1,place)
    #print('after tm call sank date',sank_date)
    return sank_date, solar_hour1,tamil_month,tamil_day
def previous_sankranti_date(panchanga_date,place):
    next_day = utils.previous_panchanga_day(panchanga_date, 1)# Date(panchanga_date[0],panchanga_date[1],panchanga_date[2]-1)
    t_month,_ = tamil_solar_month_and_date(next_day, place)
    multiple = t_month * 30
    #print(next_day,t_month,t_day)
    jd = gregorian_to_jd(next_day)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd)
    while True:
        #print(sunset_jd,sl,multiple)
        if sl%30<1 and sl%30>0:
            break
        sunset_jd -= 1
        sl = solar_longitude(sunset_jd)
    sank_date = jd_to_gregorian(sunset_jd)
    sank_sunrise = sunrise(sunset_jd,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    tamil_month,tamil_day = tamil_solar_month_and_date(sank_date, place)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    solar_longs = [ solar_longitude(sank_sunrise + t) % 360 for t in offsets ]
    solar_hour = utils.inverse_lagrange(offsets, solar_longs, multiple % 360) # Do not move % 360 above
    sank_jd_utc = gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    sank_date,solar_hour1 = utils._convert_to_tamil_date_and_time(sank_date, solar_hour1,place)
    return sank_date, solar_hour1,tamil_month,tamil_day
def next_sankranti_date(panchanga_date,place):
    next_day = utils.previous_panchanga_day(panchanga_date, 1)# Date(panchanga_date[0],panchanga_date[1],panchanga_date[2]-1)
    t_month,_ = tamil_solar_month_and_date(next_day, place)
    multiple = (t_month+1)%12 * 30
    #print(next_day,t_month,t_day)
    jd = gregorian_to_jd(next_day)
    sunset_jd = sunset(jd, place)[2]
    sl = solar_longitude(sunset_jd)
    while True:
        #print(sunset_jd,sl,multiple,jd_to_gregorian(sunset_jd))
        if sl%30<1 and sl%30>0:
            break
        sunset_jd += 1
        sl = solar_longitude(sunset_jd)
    sank_date = jd_to_gregorian(sunset_jd)
    sank_sunrise = sunrise(sunset_jd,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    tamil_month,tamil_day = tamil_solar_month_and_date(sank_date, place)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    solar_longs = [ solar_longitude(sank_sunrise + t) % 360 for t in offsets ]
    solar_hour = utils.inverse_lagrange(offsets, solar_longs, multiple % 360) # Do not move % 360 above
    sank_jd_utc = gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    sank_date,solar_hour1 = utils._convert_to_tamil_date_and_time(sank_date, solar_hour1,place)
    return sank_date, solar_hour1,tamil_month,tamil_day # V2.3.0 date returned as tuple
def __next_solar_jd(jd,place,sun_long):
    #sunset_jd = sunset(jd, place)[2]
    jd_next = jd
    sl = solar_longitude(jd_next)
    while True:
        #print(jd_next,sl,sun_long,jd_to_gregorian(jd_next))
        sank_date = swe.revjul(jd_next)
        #print('sank_date',sank_date,sun_long,sl,sun_long+1)
        if sl<sun_long+1 and sl>sun_long:
            jd_next -= 1
            break
        jd_next += 1
        sl = solar_longitude(jd_next)
    sank_date = jd_to_gregorian(jd_next)
    #print('sank_date',sank_date)
    sank_sunrise = sunrise(jd_next,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    solar_longs = [ (solar_longitude(sank_sunrise + t)) for t in offsets ]
    #print(solar_longs,sun_long)
    solar_hour = utils.inverse_lagrange(offsets, solar_longs, sun_long) # Do not move % 360 above
    #print('solar_hour',solar_hour)
    sank_jd_utc = gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    next_solar_jd = swe.julday(sank_date[0],sank_date[1],sank_date[2],solar_hour1)
    return next_solar_jd    
def next_solar_date(jd_at_dob,place,years=1,months=1,sixty_hours=1):
    sun_long_at_dob = dhasavarga(jd_at_dob, place,divisional_chart_factor=1)[0][1]
    sun_long_at_dob = sun_long_at_dob[0]*30+sun_long_at_dob[1]
    (y,m,d,fh) = swe.revjul(jd_at_dob)
    #print((int(sun_long_at_dob/30),utils.to_dms(sun_long_at_dob%30,is_lat_long='plong')),(y,m,d,utils.to_dms(fh)))
    sun_long_extra = ((years-1)*360+(months-1)*30+(sixty_hours-1)*2.5)%360
    jd_extra = int(((years-1)+(months-1)/12+(sixty_hours-1)/144)*const.tropical_year) #const.sidereal_year)
    #print('jd_extra',jd_extra)
    jd_next = jd_at_dob+jd_extra
    #print('jd_next',jd_next,swe.revjul(jd_next))
    #print('sun_long_extra',sun_long_extra)
    sun_long_next = (sun_long_at_dob+sun_long_extra)%360
    #print((years,months,sixty_hours),(int(sun_long_next/30),utils.to_dms(sun_long_next%30,is_lat_long='plong')),(y,m,d,utils.to_dms(fh)))
    return __next_solar_jd(jd_next,place, sun_long_next)
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
def is_solar_eclipse(jd,place):
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    lon,lat = place.latitude, place.longitude
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
    ret,_ = swe.sol_eclipse_how(jd_utc,geopos=(lon, lat,0.0),flags=flags)
    return ret
def next_solar_eclipse(jd,place):
    """
        returns next solar eclipse date, percentage of eclipse etc
        @return: retflag, tret, attrs
        we can extract several info about eclipse from retflag, tret and attrs
            retflag != -1 = eclipse found 
            
            tret[0] = time of greatest eclipse (Julian day number)            
            tret[1] = first contact
            tret[2] = second contact
            tret[3] = third contact
            tret[4] = fourth contact
            
            attr[0]   fraction of solar diameter covered by moon;
                    with total/annular eclipses, it results in magnitude acc. to IMCCE.
            attr[1]   ratio of lunar diameter to solar one
            attr[2]   fraction of solar disc covered by moon (obscuration)
            attr[3]   diameter of core shadow in km
            attr[4]   azimuth of sun at tjd
            attr[5]   true altitude of sun above horizon at tjd
            attr[6]   apparent altitude of sun above horizon at tjd
            attr[7]   elongation of moon in degrees
            attr[8]   magnitude acc. to NASA;
                      = attr[0] for partial and attr[1] for annular and total eclipses
            attr[9]   saros series number (if available; otherwise -99999999) 
            attr[10]  saros series member number (if available; otherwise -99999999)

    """
    #ecl_dict = {"Annular":swe.ECL_ANNULAR | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL,
    #            "Total":swe.ECL_TOTAL | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL,
    #            "Annular Total":swe.ECL_ANNULAR_TOTAL | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL,
    #            "Partial":swe.ECL_PARTIAL | swe.ECL_CENTRAL | swe.ECL_NONCENTRAL}
    geopos = (place.latitude, place.longitude,0.0)
    retflag,tret,attrs = swe.sol_eclipse_when_loc(jd,geopos)
    #print(ecl_dict.values(),retflag)
    #if retflag in ecl_dict.values(): print( list(ecl_dict.keys())[list(ecl_dict.values()).index(retflag)])
    #y,m,d,fh_ut = utils.jd_to_gregorian(tret[1])
    #fh_l = fh_ut + place.timezone
    #ecl_local = (y,m,d,fh_l)
    return [retflag,tret,attrs]
def next_lunar_eclipse(jd,place):
    """
        returns next lunar eclipse date, percentage of eclipse etc
        @return: retflag, tret, attrs
        we can extract several info about eclipse from retflag, tret and attrs
            retflag != -1 = eclipse found 
            
            NOTE: All the times are in UT to get local time add timezone
            tret[0] = time of greatest eclipse (Julian day number)            
            tret[1] = first contact
            tret[2] = second contact
            tret[3] = third contact
            tret[4] = fourth contact
            
            attr[0]   fraction of solar diameter covered by moon;
                    with total/annular eclipses, it results in magnitude acc. to IMCCE.
            attr[1]   ratio of lunar diameter to solar one
            attr[2]   fraction of solar disc covered by moon (obscuration)
            attr[3]   diameter of core shadow in km
            attr[4]   azimuth of sun at tjd
            attr[5]   true altitude of sun above horizon at tjd
            attr[6]   apparent altitude of sun above horizon at tjd
            attr[7]   elongation of moon in degrees
            attr[8]   magnitude acc. to NASA;
                      = attr[0] for partial and attr[1] for annular and total eclipses
            attr[9]   saros series number (if available; otherwise -99999999) 
            attr[10]  saros series member number (if available; otherwise -99999999)

    """
    geopos = (place.latitude, place.longitude,0.0)
    retflag,tret,attrs = swe.lun_eclipse_when_loc(jd,geopos)
    #y,m,d,fh_ut = utils.jd_to_gregorian(tret[1])
    #fh_l = fh_ut + place.timezone
    #ecl_local = (y,m,d,fh_l)
    return [retflag,tret,attrs]
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
    from hora.horoscope.chart import charts,house
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
def _birthtime_rectification_janma_suddhi(jd,place,gender):
    """
        Convert Ishtakaal Ghatikas to Phala (* 60)
        Divide by 225; If the reminder is:
        0 - 15 - Male /  16 - 45 - Female / 46 - 90 - Male / 91 - 150 - Female / 151 - 224 - Male
        Will check if actual gender does not matche with above calculation and return True/False 
        False => birthtime rectification is NOT required based on gender match
        True => birthtime rectification IS required based on gender match
    """
    ud = utils.udhayadhi_nazhikai(jd, place)
    ud1n = int(round(ud[1]*60)//225); ud1d = int(ud[1]*60%225)
    #print(round(ud[1]*60),'The mixed number of {}/{} is {} and {}/{}'.format(round(ud[1]*60),225,ud1n, ud1d, 225))
    janma_suddhi_dict = {0:[(0,15),(46,90),(151,224)],1:[(16,45),(91,150)]}
    jsc = not any([(ud1d > js_pair[0] and ud1d < js_pair[1]) for js_pair in janma_suddhi_dict[gender]])
    return jsc
def __next_conjunction_of_planet_pair(p1,p2,panchanga_place:Place,start_jd,direction=1,separation_angle=0):
    cur_jd = start_jd - 1*direction
    end_jd = start_jd + 1*direction
    while cur_jd*direction < end_jd*direction:
        cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
        if p1==8:
            p1_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        else:
            p1_long = (sidereal_longitude(cur_jd_utc, planet_list[p1]))
        if p2==8:
            p2_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        else:
            p2_long = (sidereal_longitude(cur_jd_utc, planet_list[p2]))
        long_diff = (p1_long - p2_long - separation_angle)%360
        if abs(long_diff) < const.minimum_separation_longitude:
            #print('Found closest time:',utils.jd_to_gregorian(cur_jd))
            return cur_jd,utils.norm360(p1_long),utils.norm360(p2_long)
        cur_jd += const.conjunction_increment*direction
    return None
def next_conjunction_of_planet_pair(p1,p2,panchanga_place:Place,panchanga_start_date:Date,direction=1,separation_angle=0):
    start_time = datetime.now()
    if (p1==7 and p2==8) or (p1==8 and p2==7):
        warnings.warn("Rahu and Ketu do not conjoin ever. Program returns error")
        return None
    increment_days=1*direction # start with 1 day after/before
    _start_date = Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    max_days_to_search = 365*25
    cur_jd = utils.julian_day_number(panchanga_start_date, (0,0,0))
    cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
    search_counter = 1
    while search_counter < max_days_to_search:
        cur_jd += increment_days
        cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
        if p1==8:
            p1_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        else:
            p1_long = (sidereal_longitude(cur_jd_utc, planet_list[p1]))
        if p2==8:
            p2_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        else:
            p2_long = (sidereal_longitude(cur_jd_utc, planet_list[p2]))
        long_diff = (p1_long - p2_long - separation_angle)%360
        #print(utils.jd_to_gregorian(cur_jd),utils.to_dms(p1_long,is_lat_long='plong'),utils.to_dms(p2_long,is_lat_long='plong'),'sign',long_diff)
        if long_diff<1.0:
            #print('Found closest date:',utils.jd_to_gregorian(cur_jd),'fine tuning to closest time')
            ret = __next_conjunction_of_planet_pair(p1,p2,panchanga_place,cur_jd,direction,separation_angle)
            end_time = datetime.now()
            #print("Elapsed", (end_time - start_time).total_seconds(),'seconds')
            if ret != None:
                return ret
        search_counter += 1
    print('Could not find planetary conjunctions for sep angle',separation_angle,' Try increasing search range')
    return None
def __previous_conjunction_of_planet_pair(p1,p2,panchanga_place:Place,start_jd,separation_angle=0):
    return __next_conjunction_of_planet_pair(p1, p2, panchanga_place, start_jd, direction=-1,separation_angle=separation_angle)
def previous_conjunction_of_planet_pair(p1,p2,panchanga_place:Place,panchanga_start_date:Date,separation_angle=0):
    return next_conjunction_of_planet_pair(p1, p2, panchanga_place, panchanga_start_date, direction=-1,separation_angle=separation_angle)
def previous_planet_entry_date(planet,panchanga_date,place,increment_days=1,precision=0.1):
    return next_planet_entry_date(planet,panchanga_date,place,direction=-1,increment_days=increment_days,precision=precision)
def next_planet_entry_date(planet,panchanga_date,place,direction=1,increment_days=1,precision=0.1,raasi=None):
    """
        If raasi==None: gives entry to next constellation
        If raasi is specified [1..12] gives entry to specified constellation/raasi
    """
    " following conversion is required as sidereal_lognitude planet should use const/swe names for planet"
    pl = planet_list[planet]
    if planet==const._ascendant_symbol or pl==const._MOON: increment_days = 1.0/24.0/60.0 # For moon/lagna increment days in minutes
    if pl==const._KETU:
        raghu_raasi = (raasi-1+6)%12+1 if raasi!=None else raasi
        ret = next_planet_entry_date(7, panchanga_date, place,direction=direction,raasi=raghu_raasi)
        p_long = (ret[1]+180)%360
        return ret[0],p_long
    next_day = panchanga_date
    " get current raasi of planet = t_month "
    jd = gregorian_to_jd(next_day)+increment_days*direction
    jd_utc = jd - place.timezone/24.0
    sl = sidereal_longitude(jd_utc,pl)
    if raasi==None:
        multiple = (((sl//30)+1)%12)*30
        if direction==-1: multiple = (sl//30)%12*30
        if pl == const._RAHU:
            multiple = ((sl//30)%12 * 30)%360
            if direction==-1:
                multiple = ((sl//30+1)%12*30)%360
    else: 
        multiple = (raasi-1)*30
    while True:
        if sl < (multiple+precision) and sl>(multiple-precision):
            break
        jd_utc += 0.01*direction
        sl = sidereal_longitude(jd_utc,pl)
    sank_date = jd_to_gregorian(jd_utc)
    sank_sunrise = sunrise(jd_utc,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    planet_longs = [ sidereal_longitude(sank_sunrise + t,pl) % 360 for t in offsets ]
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    sank_jd_utc = gregorian_to_jd(sank_date)
    planet_hour1 = (sank_sunrise + planet_hour - sank_jd_utc)*24+place.timezone
    sank_jd_utc += planet_hour1/24.0
    planet_long = sidereal_longitude(sank_jd_utc-place.timezone/24, pl)
    y,m,d,fh = jd_to_gregorian(sank_jd_utc); sank_date = Date(y,m,d); planet_hour1 = fh
    return sank_jd_utc,planet_long
def next_planet_retrograde_change_date(planet,panchanga_date,place,increment_days=1,direction=1):
    def _get_planet_longitude_sign(planet,jd):
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        longi,_ = swe.calc_ut(jd, pl, flags = flags)
        sl_sign = 1
        if longi[3] < 0: sl_sign = -1
        return sl_sign
    if planet not in [*range(2,7)]: return 
    jd = gregorian_to_jd(panchanga_date)
    jd_utc = jd - place.timezone/24.0; pl = planet_list[planet]
    sl_sign = _get_planet_longitude_sign(pl, jd_utc); sl_sign_next = sl_sign
    while sl_sign == sl_sign_next:
        jd_utc += increment_days*direction
        sl_sign_next = _get_planet_longitude_sign(pl, jd_utc)
    jd_utc -= 1*direction; increment_days=const.conjunction_increment; sl_sign_next=sl_sign
    while sl_sign == sl_sign_next:
        jd_utc += increment_days*direction
        sl_sign_next = _get_planet_longitude_sign(pl, jd_utc)
    jd_utc += place.timezone/24.0
    return jd_utc,sl_sign_next
def _nisheka_time(jd,place):
    """
        TODO: Formula needs to be checked
        Does not match JHora value (differs by upt0 15 days)
    """
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = Date(y,m,d); tob = utils.to_dms(fh,as_string=False)
    from hora.horoscope.chart.charts import rasi_chart
    pp = rasi_chart(jd,place)
    sat_long = pp[7][1][0]*30+pp[7][1][1];moon_long=pp[2][1][0]*30+pp[2][1][1]
    lagna_long = pp[0][1][0]*30+pp[0][1][1]
    ninth_house_long = (240+lagna_long+15)%360
    gl = gulika_longitude(dob,tob,place); gulika_long = gl[0]*30+gl[1]
    ml = maandi_longitude(dob,tob,place); maandi_long = ml[0]*30+ml[1]
    a = 0.5*( (sat_long-gulika_long)%30 + ((sat_long-maandi_long)%30) ); b = (ninth_house_long-lagna_long)%360
    c = (a+b)%360 ; c1 = c%30; bm = c//30
    d = (c1+moon_long%30)
    jd_nisheka = jd - (bm*const.sidereal_year/12+d)
    return jd_nisheka
def _nisheka_time_1(jd,place):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = Date(y,m,d); tob = utils.to_dms(fh,as_string=False)
    from hora.horoscope.chart.charts import rasi_chart
    from hora.horoscope.chart.house import house_owner_from_planet_positions
    pp = rasi_chart(jd,place)
    asc_house = pp[0][1][0]; lagna_long = asc_house*30 + pp[0][1][1]
    lagna_lord = house_owner_from_planet_positions(pp,asc_house,check_during_dhasa=False)
    lagna_lord_long = pp[lagna_lord+1][1][0]*30+pp[lagna_lord+1][1][1]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    drishya = 1.0
    if (lagna_lord_long < (lagna_long+15)) or (lagna_lord_long>(lagna_long+195)):
        drishya = -1
    sat_long = pp[7][1][0]*30+pp[7][1][1]; gl = gulika_longitude(dob,tob,place); gulika_long = gl[0]*30+gl[1]
    moon_long=pp[2][1][1]
    a = abs(sat_long-gulika_long)%30; c= (a+moon_long)%30
    print('a',a,c,drishya)
    jd_nisheka = jd - (273 + drishya*c*27.3217/30)
    return jd_nisheka
if __name__ == "__main__":
    utils.set_language('ta')
    dcf = 1; dob = (1996,12,7); tob = (10,34,0); place = Place('Chennai,India',13.0878,80.2785,5.5)
    #dcf = 1; dob = (1985,6,9); tob = (10,34,0); place = Place('Bangalore', 12.972, 77.594, +5.5)
    jd = utils.julian_day_number(dob, tob)
    
    #dcf = 1; dob = (1995,1,11); tob = (15,50,37); place = Place('Chennai,India',13.+6/60,80+17/60,5.5)
    #dcf = 1; dob = (2024,1,1); tob = (10,34,0); place = Place('Chennai,India',13.2/60+20/3600,80+15/60+7/3600,5.5)
    import time
    start_time = time.perf_counter()
    planet = 8; direction = 1; raasi = 6
    p_date = Date(dob[0],dob[1],dob[2])
    for raasi in range(1,13):
        t = next_planet_entry_date(planet, p_date, place,raasi=raasi,direction=direction)
        y,m,d,fh = utils.jd_to_gregorian(t[0])
        print(utils.PLANET_NAMES[planet],y,m,d,utils.to_dms(fh),utils.to_dms(t[1],is_lat_long='plong'))
    #sd = next_sankranti_date(p_date, place)
    #print(sd)
    end_time = time.perf_counter()
    print(end_time - start_time)
    exit()
    start_date = Date(dob[0],dob[1],dob[2])
    sank = next_sankranti_date(start_date, place)
    print(sank[0],utils.to_dms(sank[1]),sank[2],sank[3])
    sun_jd,sun_long = next_planet_entry_date(const._SUN, start_date, place)
    y,m,d,fh = utils.jd_to_gregorian(sun_jd)
    print((y,m,d),utils.to_dms(fh),utils.to_dms(sun_long,is_lat_long='plong'))
    exit()
    jd_nisheka = _nisheka_time(jd,place)
    y,m,d,fh = utils.jd_to_gregorian(jd_nisheka)
    print((y,m,d),utils.to_dms(fh))
    jd_nisheka = _nisheka_time_1(jd,place)
    y,m,d,fh = utils.jd_to_gregorian(jd_nisheka)
    print((y,m,d),utils.to_dms(fh))
    exit()
    for planet in range(2,7):
        y,m,d,fh = jd_to_gregorian(next_planet_retrograde_change_date(planet, start_date, place))
        print(planet,(y,m,d),utils.to_dms(fh))
    exit()
    #"""
    #"""
    from hora.tests import pvr_tests
    #pvr_tests.conjunction_tests()
    pvr_tests.planet_transit_tests()
    exit()
    dcf = 1; dob = (1996,12,7); tob = (10,34,0); place = Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    start_date = Date(dob[0],dob[1],dob[2])
    print(bhava_lagna(jd,place))
    ahar = ahargana(jd)
    day = int(ahar) %7; 
    ahar_days = ['Friday','Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday']
    vaara_days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    print(jd,ahar,ahar_days[day],vaara_days[vaara(jd)])
    years = 1; jd_years = next_solar_date(jd, place, years=years)
    print(_tithi_old(jd, place))
    t = tithi(jd,place)
    print(t,utils.get_fraction(t[1], t[2], 10.5667))
    exit()
    print('nakshatra suddhi',_birthtime_rectification_nakshathra_suddhi(jd, place))
    print('lagna suddhi',_birthtime_rectification_lagna_suddhi(jd, place))
    print('janma suddhi',_birthtime_rectification_janma_suddhi(jd,place,0))
    exit()
    start_date = (2023,1,1)
    end_date = (2025,12,31)
    #place = Place('Chennai',13.0878,80.2785,5.5)
    place = Place('Dallas, TX, USA',-96.7970,32.7767,-6.0)
    start_jd = utils.julian_day_number(start_date, (0,0,0))
    end_jd = utils.julian_day_number(end_date, (0,0,0))
    while start_jd < end_jd:
        se_date = utils.jd_to_gregorian(next_solar_eclipse(start_jd, place)[1][1])
        se_date = list(se_date);se_date[3] += place.timezone; se_date = tuple(se_date)
        print('Solar eclipse starts on/at',se_date)
        start_jd = utils.julian_day_number((se_date[0],se_date[1],se_date[2]), (0,0,0))+1
    exit()
    week_days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    dob = (1995,1,11)
    #dob = (1918,10,16)
    #dob = (1996,12,7)
    dob = (-5114,1,9)
    p_date = Date(dob[0],dob[1],dob[2])
    tob = (12,10,0)
    #tob = (14,6,16)
    #tob = (10,34,0)
    place = Place('Ayodhya',26+48/60,82+12/60,5.5)
    #place = drik.Place('unknown',13.00,77.5,5.5)
    #place = drik.Place('Chennai',13.0878,80.2785,5.5)
    tobh = (tob[0]+tob[1]/60+tob[2]/3600)/24
    jd = utils.julian_day_number(dob, tob)
    lang = 'ta'
    utils.set_language(lang)
    res = utils.resource_strings
    ret = next_solar_eclipse(jd,place)
    print(ret)
    ret = next_lunar_eclipse(jd,place)
    print(ret)
    exit()
    year = -5115 #2023 #-12239 # # 
    year1 = -5114 # 2024 #-12240 #-5115 # 
    day = 1
    jd_diff = -30
    """
    print(_get_previous_chaitra_month_date(jd, place))
    maasa_index,adhik_maasa,nija_maasa = lunar_month(jd,place)
    sam = samvatsara(p_date, place, maasa_index, zodiac=0)
    print(utils.YEAR_LIST[sam-1])
    exit()
    """
    for m in range(1,13):#[:1]:
        dob = (year,m,day)
        p_date = Date(dob[0],dob[1],dob[2])
        jd = utils.julian_day_number(dob, tob)
        maasa_index,adhik_maasa,nija_maasa = lunar_month(jd,place)
        tm,td = tamil_solar_month_and_date(p_date, place)
        sam = samvatsara(p_date,place, maasa_index,zodiac=0)
        am = ''
        if adhik_maasa:
            am = res['adhika_maasa_str']
        nm = ''
        if nija_maasa:
            nm = res['nija_month_str']
        print(dob,tm,td,maasa_index,utils.MONTH_LIST[maasa_index-1]+am+nm,adhik_maasa,utils.YEAR_LIST[sam-1])
        #print(dob,tm,td,maasa_index,utils.MONTH_LIST[maasa_index-1],adhik_maasa,utils.YEAR_LIST[_samvatsara_old(jd, maasa_index)-1])
    #exit()
    for m in range(1,13):#[:1]:
        dob = (year1,m,day)
        p_date = Date(dob[0],dob[1],dob[2])
        pp_date = utils.previous_panchanga_day(p_date, minus_days=15)
        jd = utils.julian_day_number(dob, tob)
        maasa_index,adhik_maasa,nija_maasa = lunar_month(jd,place)
        tm,td = tamil_solar_month_and_date(p_date, place)
        sam = samvatsara(p_date,place, maasa_index,zodiac=0)
        am = ''
        if adhik_maasa:
            am = res['adhika_maasa_str']
        nm = ''
        if nija_maasa:
            nm = res['nija_month_str']
        print(dob,tm,td,maasa_index,utils.MONTH_LIST[maasa_index-1]+am+nm,adhik_maasa,utils.YEAR_LIST[sam-1])
        #print(dob,tm,td,maasa_index,utils.MONTH_LIST[maasa_index-1],adhik_maasa,utils.YEAR_LIST[_samvatsara_old(jd, maasa_index)-1])
    #exit()
    dob = Date(-5115,12,1)
    jd = utils.julian_day_number(dob, tob)
    for d in range(1,90):
        p_date = Date(dob[0],dob[1],dob[2])
        maasa_index,adhik_maasa,nija_maasa = lunar_month(jd,place)
        tm,td = tamil_solar_month_and_date(p_date, place)
        sam = samvatsara(p_date,place, maasa_index,zodiac=0)
        am = ''
        if adhik_maasa:
            am = res['adhika_maasa_str']
        nm = ''
        if nija_maasa:
            nm = res['nija_month_str']
        print(dob,tm,td,maasa_index,utils.MONTH_LIST[maasa_index-1]+am+nm,adhik_maasa,utils.YEAR_LIST[sam-1])
        jd += 1
        dob = utils.jd_to_gregorian(jd)
    exit()
    m = lunar_month(jd, place)
    am = ''
    if m[1]:
        am = res['adhika_maasa_str']
    print(utils.MONTH_LIST[m[0]-1]+' '+am)
    m = tamil_solar_month_and_date(p_date, place)
    print(m,am)
    exit()
    sd = previous_sankranti_date(p_date, place)
    print(sd[0],tamil_solar_month_and_date(sd[0], place))
    sd = next_sankranti_date(p_date, place)
    print(sd)
    print(sd[0],tamil_solar_month_and_date(sd[0], place))
    print(tamil_solar_month_and_date(p_date, place))
    exit()
    jd_utc = jd - (place.timezone / 24.)
    bm1 = bhaava_madhya_swe(jd, place)
    bm2 = bhaava_madhya_sripathi(jd,place)
    for h in range(12):
        print(h+1,bm1[h],bm2[h])
    exit()
    nak = nakshatra(jd, place)
    print(nak)
    dv = dhasavarga(jd, place,divisional_chart_factor=1)
    #print(dv)
    dob = (2008,3,11)
    tob = (8,0,0)
    tobh = (tob[0]+tob[1]/60+tob[2]/3600)/24
    place = Place('cuddalore',11.75,79.75,5.5)
    jd = utils.julian_day_number(dob, tob)
    nak = nakshatra(jd, place)
    dv = dhasavarga(jd, place,divisional_chart_factor=1)
    print(nak)
    exit()
