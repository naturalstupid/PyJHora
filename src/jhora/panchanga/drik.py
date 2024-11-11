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
from jhora import utils, const

""" Since datetime does not accept BC year values Use the following stucture to represent dates """
Date = struct('Date', ['year', 'month', 'day'])
Place = struct('Place', ['Place','latitude', 'longitude', 'timezone'])
planet_list = [const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER,
               const._VENUS, const._SATURN,const._RAHU,const._KETU]#,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
_sideral_planet_list = [const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER,
               const._VENUS, const._SATURN,const._RAHU,const._KETU]#,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
if const._INCLUDE_URANUS_TO_PLUTO: _sideral_planet_list += [swe.URANUS,swe.NEPTUNE,swe.PLUTO]
#print('_sideral_planet_list',_sideral_planet_list)
_tropical_planet_list = [const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER,
               const._VENUS, const._SATURN,const._URANUS,const._NEPTUNE,const._PLUTO] # Rahu = MEAN_NODE
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
        Note: Recommended to call this  immediately after calling set_ayanamsa_mode
        returns the ayanamsa value for the ayanamsa mode passed to set_ayanamsa_mode or that of const._DEFAULT_AYANAMSA_MODE
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
        #set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        _ayanamsa_value = swe.get_ayanamsa(jd)
        return _ayanamsa_value
def set_ayanamsa_mode(ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE,ayanamsa_value=None,jd=None):
    """
        Set Ayanamsa mode
        @param ayanamsa_mode - Default - Lahiri
            Other possible values: 
            FAGAN, KP, RAMAN, USHASHASHI, YUKTESHWAR, SURYASIDDHANTA, SURYASIDDHANTA_MSUN,ARYABHATA,ARYABHATA_MSUN,
            SS_CITRA, TRUE_CITRA, TRUE_REVATI, SS_REVATI, SENTHIL, SUNDAR_SS, SIDM_USER
        @param ayanamsa_value - Need to be supplied only in case of 'SIDM_USER'
        @param jd: Julian day number to be supplied only for ayanamsa modes: SENTHIL and SUNDAR_SS
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
        warnings.warn("Unsupported Ayanamsa mode:", ayanamsa_mode,const._DEFAULT_AYANAMSA_MODE+" Assumed")
        ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        swe.set_sid_mode(const.available_ayanamsa_modes[const._DEFAULT_AYANAMSA_MODE] )#swe.SIDM_LAHIRI)
    _ayanamsa_mode = ayanamsa_mode
    const._DEFAULT_AYANAMSA_MODE = _ayanamsa_mode
reset_ayanamsa_mode = lambda: swe.set_sid_mode(const.available_ayanamsa_modes[const._DEFAULT_AYANAMSA_MODE]) \
                      if const._DEFAULT_AYANAMSA_MODE not in ['SIDM_USER','SENTHIL','SUNDAR_SS','KP-SENTHIL'] else \
                      swe.set_sid_mode(swe.SIDM_LAHIRI)
""" TODO: Need to make panchanga resource independent """

# Ketu is always 180° after Rahu, so same coordinates but different constellations
# i.e if Rahu is in Pisces, Ketu is in Virgo etc
ketu = lambda rahu: (rahu + 180) % 360
rahu = lambda ketu: (ketu + 180) % 360

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
        Make sure to pass planets as const._SUN, const._MOON .. const._KETU etc
        For all other functions of this PyJHora libarary one can use 0 to 8 for Sun to Ketu and 9-11 for Urnaus to Pluto
        Computes nirayana (sidereal) longitude of given planet on jd
        Note: This is where the selected/default ayanamsa is adjusted to tropical longitude obtained from swiss ephimeride
        @param jd: Julian Day Number of the UTC date/time.
        NOTE: The julian day number supplied to this function must be UTC date/time.
              All other functions of this PyJHora library will require JD and not JD_UTC
              JD_UTC = JD - Place.TimeZoneInFloatHours
              For example for India JD_UTC = JD - 5.5. For wester time zone -5.0 it JD_UTC = JD - (-5.0)
        @param planet: index of the planet Use const._SUN, const._RAHU etc.
        @return: the sidereal longitude of the planet (0-360 degrees)
    """
    global _ayanamsa_mode,_ayanamsa_value
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
        #set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE,_ayanamsa_value,jd); _ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        #print('drik sidereal long ayanamsa',_ayanamsa_mode, const._DEFAULT_AYANAMSA_MODE)
    longi,flgs = swe.calc_ut(jd, planet, flags = flags)
    reset_ayanamsa_mode()
    return utils.norm360(longi[0]) # degrees
def planets_in_retrograde(jd,place):
    """
        To get the list of retrograding planets
        @param jd: julian day number (not UTC)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: list of retrograding planets e.g. [3,5]
        NOTE: To find the retrograding planets for kundali charts use this function.
        There is another function in `jhora.horoscope.chart.charts` module which calculates
        retrograding planet based on their positions and is used in yoga, dhasa calculations
    """
    jd_utc = jd - place.timezone / 24.
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
    set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
    retro_planets = []
    _planet_list = [p for p in _sideral_planet_list if p not in [const._RAHU, const._KETU]]
    for planet in _planet_list:
        p_id = _sideral_planet_list.index(planet)
        longi,_ = swe.calc_ut(jd_utc, planet, flags = flags)
        reset_ayanamsa_mode()
        if longi[3]<0 : retro_planets.append(p_id)
    return retro_planets
solar_longitude = lambda jd: sidereal_longitude(jd, const._SUN)
lunar_longitude = lambda jd: sidereal_longitude(jd, const._MOON)
def sunrise(jd, place):
    """
        Sunrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [sunrise time as local time in float hours, local time string, and sunrise julian number]
            e.g. [6.5,'06:30 AM',2450424.94]
    """
    # First convert jd to UTC
    y, m, d,_  = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    
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
        Return midday time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [midday time as local time in float hours, local time string, and midday julian number]
            e.g. [12.1,'12:10 PM',2450424.94]
    """
    sun_rise = sunrise(jd, place)#[2]
    sun_set = sunset(jd, place)#[2]
    _,_,_,srh = utils.jd_to_gregorian(sun_rise[2])
    _,_,_,ssh = utils.jd_to_local(sun_set[2],place)
    mdhl = 0.5*(srh+ssh)
    return mdhl
def midnight(jd,place):
    """
        Return midnight time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [midnight time as local time in float hours, local time string, and midnight julian number]
            e.g. [0.1,'00:10 AM',2450424.94]
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
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: day length in float hours. e.g. 12.125
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
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: night length in float hours. e.g. 12.125
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
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return sunset  time as local time in float hours, local time string, and rise sd julian number date
            Time Format: float hours or hh:mm:ss AM/PM
    """
    # First convert jd to UTC
    y, m, d,_  = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    _,lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)
    set_jd = result[1][0]
    set_local_time = (set_jd - jd_utc) * 24 + tz
    # Convert to local time
    return [set_local_time, utils.to_dms(set_local_time),set_jd]
def moonrise(jd, place):
    """
        Return local moonrise time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [Moonrise time as local time in float hours, local time string, and Moonrise julian number]
            e.g. [2.5,'02:30 AM',2450424.94]
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    city, lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.MOON, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)
    rise = result[1][0]  # julian-day number
    # Convert to local time
    local_time = (rise - jd_utc) * 24 + tz
    return [local_time,utils.to_dms(local_time),rise]

def moonset(jd, place):
    """
        Return local moonset time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [Moonset time as local time in float hours, local time string, and Moonset julian number]
            e.g. [14.5,'14:30 PM',2450424.94]
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    city, lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.MOON, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_SET)
    setting = result[1][0]  # julian-day number
    # Convert to local time
    local_time = (setting - jd_utc) * 24 + tz
    return [local_time,utils.to_dms(local_time),setting]

def _get_tithi(jd,place,tithi_index=1):
    # tithi_index = 1=>Janma Tithi 2=>Dhana 3=>Bhratri, 4=>Matri 5=Putra 6=>Satru 7=>Kalatra 8=>Mrutyu 9=>Bhagya 10=>Karma 11=>Laabha 12=>Vyaya 
    tz = place.timezone
    # First convert jd to UTC  # 2.0.3
    y, m, d,bt = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[2] # V2.2.8
    # 2. Find tithi at this JDN
    moon_phase = lunar_phase(rise,tithi_index=tithi_index)
    today = ceil(moon_phase / 12)
    """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME 
        See Dr. Jayasree Saranatha Mahabharatha date validation book """
    if jd < const.mahabharatha_tithi_julian_day: #V3.2.0
        today = (today+1)%30
    degrees_left = today * 12 - moon_phase
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
    tithi_no = int(today)
    #""" Start Time 
    answer = [tithi_no, ends]
    # 5. Check for skipped tithi
    moon_phase_tmrw = lunar_phase(rise + 1,tithi_index=tithi_index)
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
def __get_general_tithi(jd,place,tithi_index=1,planet1=const._MOON,planet2=const._SUN):
    tz = place.timezone
    # First convert jd to UTC  # 2.0.3
    y, m, d,bt = jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[2] # V2.2.8
    # 2. Find tithi at this JDN
    moon_phase = lunar_phase(rise,tithi_index)
    today = ceil(moon_phase / 12)
    """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME 
        See Dr. Jayasree Saranatha Mahabharatha date validation book """
    if jd < const.mahabharatha_tithi_julian_day: #V3.2.0
        today = (today+1)%30
    degrees_left = today * 12 - moon_phase
    # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    planet1_long_diff = [ (sidereal_longitude(rise + t,planet1) - sidereal_longitude(rise,planet1)) % 360 for t in offsets ]
    planet2_long_diff = [ (sidereal_longitude(rise + t,planet2) - sidereal_longitude(rise,planet2)) % 360 for t in offsets ]
    relative_motion = [ p1 - p2 for (p1, p2) in zip(planet1_long_diff, planet2_long_diff) ]
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = relative_motion; x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end -jd_utc) * 24 + tz #jd changed to jd_utc 2.0.3
    tithi_no = int(today)
    #""" Start Time 
    answer = [tithi_no, ends]
    # 5. Check for skipped tithi
    moon_phase_tmrw = lunar_phase(rise + 1,tithi_index)
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
def _general_tithi(jd,place,tithi_index=1,planet1=const._MOON, planet2=const._SUN):    
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
    _tithi = __get_general_tithi(jd,place,tithi_index,planet1,planet2)
    _tithi_prev = __get_general_tithi(jd-1,place,tithi_index,planet1,planet2)
    _tithi_no = _tithi[0]; _tithi_start = _tithi_prev[1]; _tithi_end = _tithi[1]
    if _tithi_start < 24.0:
        _tithi_start = -_tithi_start
    elif _tithi_start > 24:
        _tithi_start -= 24.0
    result = [_tithi_no,_tithi_start,_tithi_end]
    if len(_tithi)>2:
        _tn = _tithi[2]; _tn_start = _tithi_end; _tn_end = _tithi[3]
        result += [_tn,_tn_start,_tn_end]
    return result
def tithi(jd,place,tithi_index=1):
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
    _tithi = _get_tithi(jd,place,tithi_index)
    _tithi_prev = _get_tithi(jd-1,place,tithi_index)
    _tithi_no = _tithi[0]; _tithi_start = _tithi_prev[1]; _tithi_end = _tithi[1]
    if _tithi_start < 24.0:
        _tithi_start = -_tithi_start
    elif _tithi_start > 24:
        _tithi_start -= 24.0
    result = [_tithi_no,_tithi_start,_tithi_end]
    if len(_tithi)>2:
        _tn = _tithi[2]; _tn_start = _tithi_end; _tn_end = _tithi[3]
        result += [_tn,_tn_start,_tn_end]
    return result
    
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
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
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
    return answer
def _get_nakshathra(jd,place):
    tz = place.timezone
    y, m, d, _ = jd_to_gregorian(jd)
    jd_ut = utils.gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2] # Changed to jd_utc in V2.9.6
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise+t, const._MOON) for t in offsets]
    nirayana_long = lunar_longitude(jd_utc) # Changed to jd_utc in V2.9.7
    nak_no,padam_no,_ = nakshatra_pada(nirayana_long)
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, nak_no * 360 / 27)
    ends = (rise - jd_ut + approx_end) * 24 + tz # """ Changed to jd_utc to get correct end time for the jd -  2.0.3 """
    answer = [nak_no,padam_no, ends]
    # 4. Check for skipped nakshatra
    leap_nak = nak_no + 1
    approx_end = utils.inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
    ends = (rise - jd_utc + approx_end) * 24 + tz # """ Changed to jd_utc to get correct end time for the jd -  2.0.3 """
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
        _nak_start = -_nak_start #utils.to_dms(_tithi_start)+'(-1)'
    elif _nak_start > 24:
        _nak_start -= 24.0
    result = [_nak_no,_pad_no,_nak_start,_nak_end]+_nak[3:]
    return result
def yogam(jd,place):
    """
        returns the yogam at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left, 
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          next yogam index and next yogam time is additionally returned if two yogams on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
    _yoga = _get_yogam(jd, place)
    _yoga_prev = _get_yogam(jd-1, place)
    _yoga_no = _yoga[0]; _yoga_start = _yoga_prev[1]; _yoga_end = _yoga[1]
    if _yoga_start < 24.0:
        _yoga_start = -_yoga_start #utils.to_dms(_tithi_start)+'(-1)'
    elif _yoga_start > 24:
        _yoga_start -= 24.0
    result = [_yoga_no,_yoga_start,_yoga_end]+_yoga[2:]
    return result
def _get_yogam(jd, place):
    """
        returns the yogam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [yogam index, yogam ending time, 
                next yogam index, next yogam ending time]
          next yogam index and next yogam time is additionally returned if two yogam on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
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
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return karanam index, karanam starting time, karanam ending time, karanam fraction left 
          karanam index = [1..60]  1 = Kimstugna, 2 = Bava, ..., 60 = Naga
    """
    _tithi = tithi(jd,place)
    _karana = _tithi[0]*2-1; _k_start = _tithi[1]; _k_end = 0.5*(_tithi[1]+_tithi[2])
    return [_karana,_k_start,_k_end]
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
  
def lunar_month(jd, place):
    """
        Returns lunar month and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [indian month index, whether leap month (adhika lunar_month) or not - boolean]
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
        @param maasa_index: [1..12] (use jhora.panchanga.drik.lunar_month function to get this) 
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

def lunar_phase(jd,tithi_index=1):
    solar_long = solar_longitude(jd)
    lunar_long = lunar_longitude(jd)
    moon_phase = tithi_index*(lunar_long - solar_long) % 360
    return moon_phase
def samvatsara(panchanga_date,place,zodiac=None):
    """
        @param panchanga_date: Date as struct (year,month,day)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param zodiac: [0 .. 11] Aries/Mesham to Pisces/Meenam
        @return: samvastsara year index [0..59] 
         TODO: Chithirai always shows previous year
         Should we use previous sakranti which is solar based? 
        Is there an algorithm for lunar samvastra?
        0=Prabhava, 2=Vibhava... 59=Krodhana, 59=Akshaya
    """ 
    ps = _previous_sankranti_date_new(panchanga_date, place,zodiac=zodiac)
    year = ps[0][0]
    sv = (year-1926)%60
    if sv==0:
        sv=60
    return sv
def ritu(maasa_index):
    """ returns ritu / season index. 
        @param maasa_index: [1..12] (use jhora.panchanga.drik.lunar_month function to get this) 
        @return: ritu index  0 = Vasanta,...,5 = Shishira
    """
    return (maasa_index - 1) // 2

def gauri_chogadiya(jd, place):
    """
        Get end times of gauri chogadiya for the given julian day
        Chogadiya is 1/8th of daytime or nighttime practiced as time measure in North India 
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: end times of chogadiya as a list
    """
    _, lat, lon, tz = place
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
    """
    _, lat, lon, tz = place
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
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: start and end time of dhur muhurtham - as list e.g. [start_time, end_time]
    """
    _, lat, lon, tz = place
    
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
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: start and end time of Abhijit muhurta - as list e.g. [start_time, end_time]
    """
    _, lat, lon, tz = place
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
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: 2D List of [ [planet index, planet longitude, planet constellation],...]]
            Example: [ [0,87.32148,2],...] - Sun longitude 87.32148, Gemini,...
        Note: Planet list includes Uranus/Neptune/Pluto by default.
              use const._INCLUDE_URANUS_TO_PLUTO = False to remove them from the list.
        Note: swiss ephimeris does not include Rahu and Ketu. Rahu is mapped to MEAN_MODE (Planet index = 10)
            And Ketu is calculated 180 degrees from Rahu/Mean Mode.
            Though Rahu's ephimeris planet index is 10, we use 7 and 8 respectively in charts respectively.
        NOTE:DOES NOT INCLUDE ASCENDANT POSITION AND LONGITUDE. TO GET ASCENDANT CALL: ascendant()
    """
    jd_ut = jd - place.timezone / 24.
    
    positions = []
    for planet in planet_list:
        p_id = planet_list.index(planet)
        if planet == const._KETU:
            nirayana_long = ketu(sidereal_longitude(jd_ut, const._RAHU))
        else: # Ketu
            nirayana_long = sidereal_longitude(jd_ut, planet)
        constellation = int(nirayana_long / 30)
        coordinates = nirayana_long-constellation*30
        positions.append([p_id,coordinates, constellation])        
    return positions
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
def _bhaava_madhya_new(jd, place,bhava_madhya_method=const.bhaava_madhya_method):
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
            'P':'Placidus','K':'Koch','O':'Porphyrius','R':'Regiomontanus','C':'Campanus','A':'Equal (cusp 1 is Ascendant)',
            'V':'Vehlow equal (Asc. in middle of house 1)','X':'axial rotation system','H':'azimuthal or horizontal system',
            'T':'Polich/Page (topocentric system)','B':'Alcabitus','M':'Morinus'        
        
        @return: [[house1_rasi,(house1_start,house1_cusp,house1_end)],(...),[house12_rasi,(house12_start,house12_cusp,house12_end)]]
    """
    if bhava_madhya_method not in const.available_house_systems.keys():
        warn_msg = "bhava_madhya_method should be one of const.available_house_systems keys\n Value 1 assumed"
        warnings.warn(warn_msg)
        bhava_madhya_method = 1
    ascendant_constellation, ascendant_longitude, _, _ = ascendant(jd,place)
    ascendant_full_longitude = (ascendant_constellation*30+ascendant_longitude)%360
    planet_positions = dhasavarga(jd,place,divisional_chart_factor=1)
    planet_positions = [[const._ascendant_symbol,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    bhava_houses = []
    if bhava_madhya_method ==1: #Equal Housing - Lagna in the middle
        _bhava_mid = ascendant_full_longitude; 
        for h in range(12):
            _bhava_start = (_bhava_mid-15.0)%360; _bhava_end = (_bhava_mid+15.0)%360 
            bhava_houses.append((_bhava_start,_bhava_mid,_bhava_end))
            _bhava_mid = utils.norm360(_bhava_mid + 30)
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==2: #Equal Housing - Lagna as start
        _bhava_mid = ascendant_full_longitude; 
        for h in range(12):
            _bhava_start = _bhava_mid; _bhava_mid=(_bhava_start+15.0)%360; _bhava_end = (_bhava_mid+15.0)%360 
            bhava_houses.append((_bhava_start,_bhava_mid,_bhava_end))
            _bhava_mid = utils.norm360(_bhava_start + 30)
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==3: #Sripati method
        bm = bhaava_madhya_sripathi(jd, place); bm = bm[:]+[bm[0]]
        for h in range(12):
            _bhava_start = bm[h]; _bhava_mid = 0.5*(bm[h]+bm[h+1]); _bhava_end = bm[h+1] 
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==4 or bhava_madhya_method in const.western_house_systems.keys(): #KP Method (aka swiss ephemeris method) or western house systems
        bm = bhaava_madhya_kp(jd, place) if bhava_madhya_method ==4 else bhaava_madhya_swe(jd, place, house_code=bhava_madhya_method)
        bm = bm[:]+[bm[0]]
        for h in range(12):
            bmh = bm[h]; bmh1 = bm[h+1]
            if bmh1 < bmh: bmh1+=360
            _bhava_start = bmh; _bhava_mid = 0.5*(bmh+bmh1); _bhava_end = bmh1 
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
    elif bhava_madhya_method ==5: #Each Rasi is the house
        for h in range(12):
            h1 = (h+ascendant_constellation)%12
            _bhava_start = h1*30; _bhava_mid = _bhava_start + ascendant_longitude; _bhava_end = ((h1+1)%12)*30
            bhava_houses.append((_bhava_start%360,_bhava_mid%360,_bhava_end%360))
        return _assign_planets_to_houses(planet_positions, bhava_houses,bhava_madhya_method=bhava_madhya_method)
def bhaava_madhya(jd, place,bhava_method=const.bhaava_madhya_method):
    """
        returns house longitudes
        @param jd: Julian Day number
        @param place: Place('name',latitude,longitude,timezone_hours)
        @param bhava_method:   
        bhava_method = 1 Swiss Ephemeres Ascendant Cusp Calculations
                     = 2 Sripati modifications from swiss calculations
        @return: [house longitudes as a list] # First element first house longitude and so on
    """
    if bhava_method==1: # SWISS methof
        return bhaava_madhya_kp(jd, place)
    else: # SRIPATI METHOD
        return bhaava_madhya_sripathi(jd, place)
def bhaava_madhya_swe(jd,place,house_code='P'):
    """
        Acceptable house system codes in Swiss Ephemeris
        hsys= ‘P’     Placidus
            ‘K’     Koch
            ‘O’     Porphyrius
            ‘R’     Regiomontanus
            ‘C’     Campanus
            ‘A’ or ‘E’     Equal (cusp 1 is Ascendant)
            ‘V’     Vehlow equal (Asc. in middle of house 1)
            ‘X’     axial rotation system
            ‘H’     azimuthal or horizontal system
            ‘T’     Polich/Page (“topocentric” system)
            ‘B’     Alcabitus
            ‘G’     Gauquelin sectors
            ‘M’     Morinus
        
    """
    if house_code not in const.western_house_systems.keys():
        warn_msg = "house_code should be one of const.western_house_systems keys\n Value 1 assumed"
        warnings.warn(warn_msg)
        house_code = 'P'
    hsys = bytes(house_code,encoding='ascii')
    global _ayanamsa_mode,_ayanamsa_value
    _, lat, lon, tz = place
    jd_utc = jd - (tz / 24.)
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SIDEREAL
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd) # needed for swe.houses_ex()
    return list(swe.houses_ex(jd_utc, lat, lon,hsys, flags = flags)[0])
def bhaava_madhya_kp(jd,place):
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
    bm = bhaava_madhya_kp(jd, place)
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
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [constellation of Lagna, longitude of lagna, Lagna nakshatra number, Lagna paadham number]
    """
    global _ayanamsa_mode,_ayanamsa_value
    _, lat, lon, tz = place
    jd_utc = jd - (tz / 24.)
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SIDEREAL
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd) # needed for swe.houses_ex()
    nirayana_lagna = swe.houses_ex(jd_utc, lat, lon, flags = flags)[1][0]
    nak_no,paadha_no,_ = nakshatra_pada(nirayana_lagna)
    constellation = int(nirayana_lagna / 30)
    coordinates = nirayana_lagna-constellation*30
    reset_ayanamsa_mode()
    return [constellation, coordinates, nak_no, paadha_no]    
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
    if int(long_in_raasi+0.000001) == 30:
        long_in_raasi = 0; constellation = (constellation+1)%12
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

def dhasavarga(jd, place,divisional_chart_factor=1):
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
def declination_of_planets(jd,place):
    """
        return declination of planets
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: declination as a list
        first element for sun and last element for saturn
        
    """
    pp = dhasavarga(jd,place,divisional_chart_factor=1)[:7]
    bhujas = [0 for _ in range(7)]
    north_south_sign = [1 for _ in range(7)]
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
    declinations = [0 for _ in range(7)]
    for p in range(7):
        declinations[p] = north_south_sign[p] * utils.inverse_lagrange(bd, bx, bhujas[p])
    return declinations
""" TODO: Upagrah longitudes to be computed from planet positions using ayanamsa, div factor, chart method etc """
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
kaala_longitude = lambda dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1: \
    upagraha_longitude(dob,tob,place,planet_index=0,ayanamsa_mode=ayanamsa_mode,
                       divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Mrityu rises at the middle of Mars’s part."""
mrityu_longitude = lambda dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1: \
    upagraha_longitude(dob,tob,place,planet_index=2,ayanamsa_mode=ayanamsa_mode,
                       divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Artha Praharaka rises at the middle of Mercury’s part."""
artha_praharaka_longitude = lambda dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1: \
    upagraha_longitude(dob,tob,place,planet_index=3,ayanamsa_mode=ayanamsa_mode,
                       divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Yama Ghantaka rises at the middle of Jupiter’s part. """
yama_ghantaka_longitude = lambda dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1: \
    upagraha_longitude(dob,tob,place,planet_index=4,ayanamsa_mode=ayanamsa_mode,
                       divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')
""" Gulika rises at the start of Saturn’s part. (Book says middle) """
gulika_longitude = lambda dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1: \
    upagraha_longitude(dob,tob,place,planet_index=6,ayanamsa_mode=ayanamsa_mode,
                       divisional_chart_factor=divisional_chart_factor,upagraha_part='begin')
""" Maandi rises at the middle of Saturn’s part. (Book says start) """
maandi_longitude = lambda dob,tob,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1: \
    upagraha_longitude(dob,tob,place,planet_index=6,ayanamsa_mode=ayanamsa_mode,
                       divisional_chart_factor=divisional_chart_factor,upagraha_part='middle')

def upagraha_longitude(dob,tob,place,planet_index,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,
                       divisional_chart_factor=1,upagraha_part='middle'):
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
              Gulika rises at the middle of Saturn’s part.
          Since Maandi is upagraha of Saturn so planet_index should be 6
              Maandi rises at the beginning of Saturn’s part.
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
    set_ayanamsa_mode(ayanamsa_mode)#, ayanamsa_value, jd)
    jd_utc = utils.gregorian_to_jd(Date(dob.year,dob.month,dob.day))
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
    """ TODO Get Ascendant of div chart here below"""
    clong = ascendant(jd_kaala, place) #2.0.3
    upagraha_long = clong[0]*30+clong[1] #2.0.3
    constellation,coordinates = dasavarga_from_long(upagraha_long, divisional_chart_factor) #int(upagraha_long / 30)
    return [constellation,coordinates]
""" NOTE: Bhava Lagna Calculation in Section 5.2 of PVR Book should have mentioned DIVIDE BY 4 in Step (2) """
bhava_lagna = lambda jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,\
                                            base_rasi=None,count_from_end_of_sign=None: \
        special_ascendant(jd,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,\
                          chart_method=chart_method,lagna_rate_factor=0.25,
                          base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign) 
hora_lagna = lambda jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,\
                                            base_rasi=None,count_from_end_of_sign=None: \
        special_ascendant(jd,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,\
                          chart_method=chart_method,lagna_rate_factor=0.5,
                          base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign) 
ghati_lagna = lambda jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,\
                                            base_rasi=None,count_from_end_of_sign=None: \
        special_ascendant(jd,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,\
                          chart_method=chart_method,lagna_rate_factor=1.25,
                          base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign) 
vighati_lagna = lambda jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,\
                                            base_rasi=None,count_from_end_of_sign=None: \
        special_ascendant(jd,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,\
                          chart_method=chart_method,lagna_rate_factor=15.0,
                          base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign) 
def special_ascendant(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                      lagna_rate_factor=1.0,base_rasi=None,count_from_end_of_sign=None):
    """
        Get constellation and longitude of special lagnas (Bhava,Hora,Ghati,vighati)
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param lagna_rate_factor:    
            lagna_rate_factor   = 1 for Bhava Lagna
                                = 0.5 for Hora Lagna
                                = 5/4 for Ghati Lagna  
                                = 15.0 for vighati Lagna                          
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [special lagnas constellation, special lagna's longitude within constellation]
        Note: You can also individual lambda function for each special lagna without lagna_rate_factor
        Example: 
            bhava_lagna(jd,place,divisional_chart_factor)
            hora_lagna(jd,place,divisional_chart_factor)
            ghati_lagna(jd,place,divisional_chart_factor)
            vighati_lagna(jd,place,divisional_chart_factor)
        NOTE: There are separate functions for pranapada, indu,sree, bhrigu_bindhu, kunda with same arguments
    """
    _,_,_, time_of_birth_in_hours = jd_to_gregorian(jd)
    srise = sunrise(jd, place) #V2.3.1 Get sunrise JD - as we need sun longitude at sunrise
    sun_rise_hours = srise[0]
    time_diff_mins = (time_of_birth_in_hours-sun_rise_hours)*60
    from jhora.horoscope.chart import charts
    """ 
        Change in V3.6.3
        We need Sun position at sunrise. So we use srise[2] returned from sunrise function.
        Since sunrise function returns JD Local at sunrise we add local time here because charts will minus it to get UTC
    """
    jd_at_sunrise = srise[2]+place.timezone/24
    pp = charts.divisional_chart(jd_at_sunrise, place, ayanamsa_mode=ayanamsa_mode,
            divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,base_rasi=base_rasi,
            count_from_end_of_sign=count_from_end_of_sign)[:const._pp_count_upto_ketu]
    sun_long = pp[1][1][0]*30+pp[1][1][1]
    spl_long = (sun_long + (time_diff_mins * lagna_rate_factor) ) % 360
    da = dasavarga_from_long(spl_long, divisional_chart_factor)
    return da
bhava_lagna_mixed_chart = lambda jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1: \
        special_ascendant_mixed_chart(jd,place,varga_factor_1=varga_factor_1,chart_method_1=chart_method_1,
                          varga_factor_2=varga_factor_2,chart_method_2=chart_method_2,lagna_rate_factor=0.25) 
hora_lagna_mixed_chart = lambda jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1: \
        special_ascendant_mixed_chart(jd,place,varga_factor_1=varga_factor_1,chart_method_1=chart_method_1,
                          varga_factor_2=varga_factor_2,chart_method_2=chart_method_2,lagna_rate_factor=0.5) 
ghati_lagna_mixed_chart = lambda jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1: \
        special_ascendant_mixed_chart(jd,place,varga_factor_1=varga_factor_1,chart_method_1=chart_method_1,
                          varga_factor_2=varga_factor_2,chart_method_2=chart_method_2,lagna_rate_factor=1.25) 
vighati_lagna_mixed_chart = lambda jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1: \
        special_ascendant_mixed_chart(jd,place,varga_factor_1=varga_factor_1,chart_method_1=chart_method_1,
                          varga_factor_2=varga_factor_2,chart_method_2=chart_method_2,lagna_rate_factor=15.0) 
def special_ascendant_mixed_chart(jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                  lagna_rate_factor=1.0):
    mixed_dvf = varga_factor_1*varga_factor_2
    _,_,_, time_of_birth_in_hours = jd_to_gregorian(jd)
    srise = sunrise(jd, place) #V2.3.1 Get sunrise JD - as we need sun longitude at sunrise
    sun_rise_hours = srise[0]
    time_diff_mins = (time_of_birth_in_hours-sun_rise_hours)*60
    from jhora.horoscope.chart import charts
    """ 
        Change in V3.6.3
        We need Sun position at sunrise. So we use srise[2] returned from sunrise function.
        Since sunrise function returns JD Local at sunrise we add local time here because charts will minus it to get UTC
    """
    jd_at_sunrise = srise[2]+place.timezone/24
    pp = charts.mixed_chart(jd_at_sunrise, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    sun_long = pp[1][1][0]*30+pp[1][1][1]
    spl_long = (sun_long + (time_diff_mins * lagna_rate_factor) ) % 360
    da = dasavarga_from_long(spl_long, mixed_dvf)
    return da    
def pranapada_lagna_mixed_chart(jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    mixed_dvf = varga_factor_1*varga_factor_2
    birth_long = (utils.udhayadhi_nazhikai(jd, place)[1]*4)%12 #vighati/15=ghati*60/15 )
    """Note: V3.6.3 Pranapada requires sun longitude at birthtime not sunrise"""
    #srise = sunrise(jd, place)
    from jhora.horoscope.chart import charts
    pp = charts.mixed_chart(jd, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    sun_long = pp[1][1][0]*30+pp[1][1][1]
    pl1 = birth_long*30 + sun_long
    sl = dasavarga_from_long(sun_long, mixed_dvf)
    if sl[0] in const.fixed_signs:
        x = 240
    elif sl[0] in const.dual_signs:
        x = 120
    else:
        x = 0
    pl1 += x
    spl_long = pl1 % 360
    da = dasavarga_from_long(spl_long, mixed_dvf)
    return da
def pranapada_lagna(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                                            base_rasi=None,count_from_end_of_sign=None):
    """
        Get constellation and longitude of pranapada lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [paranapada lagnas constellation, pranapada lagna's longitude within constellation]
    """
    birth_long = (utils.udhayadhi_nazhikai(jd, place)[1]*4)%12 #vighati/15=ghati*60/15 )
    """Note: V3.6.3 Pranapada requires sun longitude at birthtime not sunrise"""
    #srise = sunrise(jd, place)
    from jhora.horoscope.chart import charts
    pp = charts.divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,
                        count_from_end_of_sign=count_from_end_of_sign)[:const._pp_count_upto_ketu]
    sun_long = pp[1][1][0]*30+pp[1][1][1]
    pl1 = birth_long*30 + sun_long
    sl = dasavarga_from_long(sun_long, divisional_chart_factor)
    if sl[0] in const.fixed_signs:
        x = 240
    elif sl[0] in const.dual_signs:
        x = 120
    else:
        x = 0
    pl1 += x
    spl_long = pl1 % 360
    da = dasavarga_from_long(spl_long, divisional_chart_factor)
    return da
def indu_lagna_mixed_chart(jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    il_factors = [30,16,6,8,10,12,1] # Sun to Saturn. Rahu/Ketu exempted
    from jhora.horoscope.chart import charts
    planet_positions = charts.mixed_chart(jd, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_house = planet_positions[2][1][0]
    asc_house = planet_positions[0][1][0]
    ninth_lord = const._house_owners_list[(asc_house+8)%12]
    ninth_lord_from_moon = const._house_owners_list[(moon_house+8)%12]
    il1 = (il_factors[ninth_lord]+il_factors[ninth_lord_from_moon])%12
    if il1==0: il1 = 12
    _indu_rasi = (moon_house+il1-1)%12
    return _indu_rasi,planet_positions[2][1][1]
def indu_lagna(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                                            base_rasi=None,count_from_end_of_sign=None):  # BV Raman Method
    """
        Get constellation and longitude of indu lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [indu lagnas constellation, indu lagna's longitude within constellation]
    """
    il_factors = [30,16,6,8,10,12,1] # Sun to Saturn. Rahu/Ketu exempted
    from jhora.horoscope.chart import charts
    planet_positions = charts.divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,
                        count_from_end_of_sign=count_from_end_of_sign)[:const._pp_count_upto_ketu]
    moon_house = planet_positions[2][1][0]
    asc_house = planet_positions[0][1][0]
    ninth_lord = const._house_owners_list[(asc_house+8)%12]
    ninth_lord_from_moon = const._house_owners_list[(moon_house+8)%12]
    il1 = (il_factors[ninth_lord]+il_factors[ninth_lord_from_moon])%12
    if il1==0: il1 = 12
    _indu_rasi = (moon_house+il1-1)%12
    return _indu_rasi,planet_positions[2][1][1]
def kunda_lagna_mixed_chart(jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1):
    mixed_dvf = varga_factor_1*varga_factor_2
    from jhora.horoscope.chart import charts
    planet_positions = charts.mixed_chart(jd, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    asc = planet_positions[0]; al = asc[1][0]*30+asc[1][1]; al1 = (al*81)%360
    spl = dasavarga_from_long(al1,divisional_chart_factor=mixed_dvf)
    return spl
def kunda_lagna(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                                            base_rasi=None,count_from_end_of_sign=None):
    """
        Get constellation and longitude of kunda lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [kunda lagnas constellation, kunda lagna's longitude within constellation]
    """
    from jhora.horoscope.chart import charts
    planet_positions = charts.divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,
                        count_from_end_of_sign=count_from_end_of_sign)[:const._pp_count_upto_ketu]
    asc = planet_positions[0]; al = asc[1][0]*30+asc[1][1]; al1 = (al*81)%360
    spl = dasavarga_from_long(al1,divisional_chart_factor=divisional_chart_factor)
    return spl
def bhrigu_bindhu_lagna_mixed_chart(jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                  lagna_rate_factor=1.0):
    mixed_dvf = varga_factor_1*varga_factor_2
    from jhora.horoscope.chart import charts
    planet_positions = charts.mixed_chart(jd, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    moon_house = planet_positions[2][1][0];rahu_house = planet_positions[8][1][0]
    moon_long = moon_house*30+planet_positions[2][1][1]; rahu_long = rahu_house*30+planet_positions[8][1][1]
    moon_add = 0 if moon_long > rahu_long else 360
    bb = (0.5*(rahu_long+moon_long+moon_add))%360
    return dasavarga_from_long(bb)
def bhrigu_bindhu_lagna(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                                            base_rasi=None,count_from_end_of_sign=None):
    """
        Get constellation and longitude of bhrigu bindhu lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [bhrigu bindhu lagnas constellation, bhrigu bindhu lagna's longitude within constellation]
    """
    from jhora.horoscope.chart import charts
    planet_positions = charts.divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,
                        count_from_end_of_sign=count_from_end_of_sign)[:const._pp_count_upto_ketu]
    moon_house = planet_positions[2][1][0];rahu_house = planet_positions[8][1][0]
    moon_long = moon_house*30+planet_positions[2][1][1]; rahu_long = rahu_house*30+planet_positions[8][1][1]
    moon_add = 0 if moon_long > rahu_long else 360
    bb = (0.5*(rahu_long+moon_long+moon_add))%360
    return dasavarga_from_long(bb)
def sree_lagna_mixed_chart(jd,place,varga_factor_1=1,chart_method_1=1,varga_factor_2=1,chart_method_2=1,
                                  lagna_rate_factor=1.0):
    mixed_dvf = varga_factor_1*varga_factor_2
    from jhora.horoscope.chart import charts
    planet_positions = charts.mixed_chart(jd, place, varga_factor_1, chart_method_1, varga_factor_2, chart_method_2)
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sl = sree_lagna_from_moon_asc_longitudes(moon_long, asc_long, divisional_chart_factor=mixed_dvf)
    return sl
def sree_lagna(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,chart_method=1,
                                            base_rasi=None,count_from_end_of_sign=None):
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
    from jhora.horoscope.chart import charts
    planet_positions = charts.divisional_chart(jd,place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=divisional_chart_factor,
                        chart_method=chart_method,base_rasi=base_rasi,
                        count_from_end_of_sign=count_from_end_of_sign)[:const._pp_count_upto_ketu]
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sl = sree_lagna_from_moon_asc_longitudes(moon_long, asc_long, divisional_chart_factor=divisional_chart_factor)
    return sl
def sree_lagna_from_moon_asc_longitudes(moon_longitude,ascendant_longitude,divisional_chart_factor=1):
    moon_long = moon_longitude
    asc_long = ascendant_longitude
    reminder = nakshatra_pada(moon_long)[2]
    reminder_fraction = reminder * 27
    sree_long = asc_long + reminder_fraction
    constellation,coordinates = dasavarga_from_long(sree_long, divisional_chart_factor)
    return constellation,coordinates
def tamil_solar_month_and_date(panchanga_date,place):
    """
        Returns tamil month and date (e.g. Aadi 28 )
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: tamil_month_number, tamil_date_number
        i.e. [0..11, 1..32]
        Note: Tamil month is sankranti based solar month - not lunar month
    """ 
    jd = utils.gregorian_to_jd(panchanga_date)
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
    jd = utils.gregorian_to_jd(panchanga_date)
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
    jd = utils.gregorian_to_jd(prev_day)
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
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    #print('before tm call sank date',sank_date,solar_hour,solar_hour1)
    sank_date,solar_hour1 = utils._convert_to_tamil_date_and_time(sank_date, solar_hour1,place)
    #print('after tm call sank date',sank_date)
    return sank_date, solar_hour1,tamil_month,tamil_day
def previous_sankranti_date(panchanga_date,place):
    """
        Get the previous sankranti date (sun entry to a raasi)
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: sankranti_date as Struct(y,m,d), sankranti time as float hours,tamil_month_number, tamil_date_number        
    """
    next_day = utils.previous_panchanga_day(panchanga_date, 1)# Date(panchanga_date[0],panchanga_date[1],panchanga_date[2]-1)
    t_month,_ = tamil_solar_month_and_date(next_day, place)
    multiple = t_month * 30
    #print(next_day,t_month,t_day)
    jd = utils.gregorian_to_jd(next_day)
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
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    sank_date,solar_hour1 = utils._convert_to_tamil_date_and_time(sank_date, solar_hour1,place)
    return sank_date, solar_hour1,tamil_month,tamil_day
def next_sankranti_date(panchanga_date,place):
    """
        Get the next sankranti date (sun entry to a raasi)
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: sankranti_date as Struct(y,m,d), sankranti time as float hours,tamil_month_number, tamil_date_number        
    """
    next_day = utils.previous_panchanga_day(panchanga_date, 1)# Date(panchanga_date[0],panchanga_date[1],panchanga_date[2]-1)
    t_month,_ = tamil_solar_month_and_date(next_day, place)
    multiple = (t_month+1)%12 * 30
    #print(next_day,t_month,t_day)
    jd = utils.gregorian_to_jd(next_day)
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
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
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
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    solar_hour1 = (sank_sunrise + solar_hour - sank_jd_utc)*24+place.timezone
    next_solar_jd = swe.julday(sank_date[0],sank_date[1],sank_date[2],solar_hour1)
    return next_solar_jd    
def next_solar_date(jd_at_dob,place,years=1,months=1,sixty_hours=1):
    """
        returns the next date at which sun's longitue is same as at jd_at_dob (at birth say)
        For example if someone was born on 1970,2,10 and years = 10, 
        will return date in 1979 at which sun longitude is same as calculated at (1970,2,10)
        These are used for Tajaka yearly/monthly/shashti-hora(60hr) charts
        @param jd_at_dob: Julian number at the time of birth
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param year: Number of years since birth (year=1 for the birth year)
        @param months: Number of months from the birth month (month=1 for the same birth month)
        @param sixty_hours: Number of 60 hr count
        @return: julian number for the matching solar date
    """
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
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    lon,lat = place.latitude, place.longitude
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
    ret,_ = swe.sol_eclipse_how(jd_utc,geopos=(lon, lat,0.0),flags=flags)
    return ret
def next_solar_eclipse(jd,place):
    """
        @param jd: Julian number 
        @param place: Place Struct ('place',latitude,longitude,timezone)
        returns next solar eclipse date, percentage of eclipse etc
        @param jd: Julian number
        @param place: Place Struct ('place',latitude,longitude,timezone)
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
        @param jd: Julian number 
        @param place: Place Struct ('place',latitude,longitude,timezone)
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
        if long_diff<1.0:
            ret = __next_conjunction_of_planet_pair(p1,p2,panchanga_place,cur_jd,direction,separation_angle)
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
    pl = planet_list[planet]
    if planet==const._ascendant_symbol or pl==const._MOON: increment_days = 1.0/24.0/60.0 # For moon/lagna increment days in minutes
    if pl==const._KETU:
        raghu_raasi = (raasi-1+6)%12+1 if raasi!=None else raasi
        ret = next_planet_entry_date(7, panchanga_date, place,direction=direction,raasi=raghu_raasi)
        p_long = (ret[1]+180)%360
        return ret[0],p_long
    next_day = panchanga_date
    " get current raasi of planet = t_month "
    jd = utils.gregorian_to_jd(next_day)+increment_days*direction
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
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    planet_hour1 = (sank_sunrise + planet_hour - sank_jd_utc)*24+place.timezone
    sank_jd_utc += planet_hour1/24.0
    planet_long = sidereal_longitude(sank_jd_utc-place.timezone/24, pl)#+(1.0/86400)# Error to cover
    y,m,d,fh = jd_to_gregorian(sank_jd_utc); sank_date = Date(y,m,d); planet_hour1 = fh
    return sank_jd_utc,planet_long
def next_planet_retrograde_change_date(planet,panchanga_date,place,increment_days=1,direction=1):
    """
        get the date when a retrograde planet changes its direction
        @param planet: planet index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param direction: 1= next direction change, -1 previous direction change
        @return Julian day number of planet changes retrogade direction
    """
    def _get_planet_longitude_sign(planet,jd):
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        longi,_ = swe.calc_ut(jd, pl, flags = flags)
        sl_sign = 1
        if longi[3] < 0: sl_sign = -1
        return sl_sign
    if planet not in [*range(2,7)]: return 
    jd = utils.gregorian_to_jd(panchanga_date)
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
        @param jd: Julian number 
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return julian date number of nisheka time
        TODO: Formula needs to be checked
        Does not match JHora value (differs by upto 15 days)
    """
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = Date(y,m,d); tob = utils.to_dms(fh,as_string=False)
    from jhora.horoscope.chart.charts import rasi_chart
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
    from jhora.horoscope.chart.charts import rasi_chart
    from jhora.horoscope.chart.house import house_owner_from_planet_positions
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
    utils.set_language('en')
    dob = (1996,12,7); tob = (10,34,0); place = Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob); dcf = 9
    for cm in range(4):
        sp_long = sree_lagna(jd,place,divisional_chart_factor=dcf,chart_method=cm)
        print('chart_method='+str(cm+1),'sree lagna',sp_long)
    exit()
    ayan = 'SENTHIL'
    set_ayanamsa_mode(ayan,jd=jd)
    print(get_ayanamsa_value(jd),const._DEFAULT_AYANAMSA_MODE,_ayanamsa_mode,_ayanamsa_value)
    for planet in range(9):
        print(utils.PLANET_NAMES[planet],utils.to_dms(sidereal_longitude(jd, planet),is_lat_long='plong'))
    print(get_ayanamsa_value(jd),const._DEFAULT_AYANAMSA_MODE,_ayanamsa_mode,_ayanamsa_value)
    ayan = 'TRUE_MULA'
    set_ayanamsa_mode(ayan)
    for planet in range(9):
        print(utils.PLANET_NAMES[planet],utils.to_dms(sidereal_longitude(jd, planet),is_lat_long='plong'))
    print(get_ayanamsa_value(jd),const._DEFAULT_AYANAMSA_MODE,_ayanamsa_mode,_ayanamsa_value)
