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
from math import ceil
from collections import namedtuple as struct
import swisseph as swe
from _datetime import datetime, timedelta
from datetime import date
import math, os, warnings
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
    #reminder = (longitude - quotient * one_star)
    reminder = longitude%one_star
    pada = int(reminder / one_pada)
    #  print (longitude,quotient,pada)
    # convert 0..26 to 1..27 and 0..3 to 1..4
    #print(longitude,quotient,reminder,pada)
    return [1 + quotient, 1 + pada,reminder]
ephemeris_planet_index = lambda planet: planet_list.index(planet)
def sidereal_longitude(jd_utc, planet):
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
        set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE,_ayanamsa_value,jd_utc); _ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        #print('drik sidereal long ayanamsa',_ayanamsa_mode, const._DEFAULT_AYANAMSA_MODE)
        #import inspect; print('called by',inspect.stack()[1].function)
    longi,_ = swe.calc_ut(jd_utc, planet, flags = flags)
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
def _planet_speed_info(jd, place,planet):
    """ 
        JD (not UTC)
        planet = 0 to 7 - Ketu is same as Rahu 
        @return: [longitude,latitude,distance_from_earth,longitude_speed,latitude_speed,distance_speed]
    """
    round_factors = [3,3,4,3,3,6]
    jd_utc = jd - place.timezone / 24.
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
    longi,_ = swe.calc_ut(jd_utc, planet, flags = flags)
    return [round(l,round_factors[i]) for i,l in enumerate(longi)]
daily_moon_speed = lambda jd,place: _planet_speed_info(jd,place,const._MOON)[3]
daily_sun_speed = lambda jd,place: _planet_speed_info(jd,place,const._SUN)[3]
daily_planet_speed = lambda jd,place,planet: _planet_speed_info(jd, place, planet)[3]
def planets_speed_info(jd,place):
    """
        To get the speed information of planets
        @param jd: julian day number (not UTC)
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [(longitude,latitude,distance_from_earth,longitude_speed,latitude_speed,distance_speed),...]
    """
    round_factors = [3,3,4,3,3,6]
    jd_utc = jd - place.timezone / 24.
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
    set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
    _planets_speed_info = {}
    for planet in planet_list:
        planet_index = planet_list.index(planet)
        if planet == const._KETU:
            _planets_speed_info[planet_index] = _planets_speed_info[planet_list.index(const._RAHU)]
            continue
        longi,_ = swe.calc_ut(jd_utc, planet, flags = flags)
        reset_ayanamsa_mode()
        _planets_speed_info[planet_index] = [round(l,round_factors[i]) for i,l in enumerate(longi)]
        #print(planet_index, planet,_planets_speed_info[planet])
    return _planets_speed_info
def planets_in_graha_yudh(jd,place):
    """
        Graha Yudh
        Bhed-yuti (भेद युति): Happens when longitudes of two planets and also the latitude in the same direction (N or S) are exactly the same, even to the last second. During this, one planet transits over the other and covers the other exactly.
        Ullekh-yuti: (उल्लेख युति)  when longitudes are equal and latitudes of both planets, in the same direction are mutually away by 15-20”. here planets moves neck to neck by touching almost their ends.
        Apsavya-yuti (अपसव्य युति) moving at equal longitude, two planets move within 1° distance in latitude.
        Anshumard-yuti (अंशु-मर्दन युति) with equal longitudes, the two pass each other with less than 1° difference in latitude.
        Ref: https://www.planetarypositions.com/yoga/2014/10/30/conjunction-planets-grah-yudh/

        NOTE: Looks like last 2 categories are identical whereas JHora seem to use 2° difference in latitude for Anshumard-yuti
            So we have used 2° difference in latitude for Anshumard-yuti
            
        @return graha yudh pairs of planets with the category of yudh
            [(planet1, planet2, yudh category)]
                yudh category 0 =>Bhed-yuti
                yudh category 1 =>Ullekh-yuti: (उल्लेख युति)
                yudh category 2 =>Apsavya-yuti (अपसव्य युति)
                yudh category 3 =>Anshumard-yuti (अंशु-मर्दन युति)
            For Example: Date=(2013,11,13) Time=(6,26,0) for Bangalore, India
            we will get [(5, 6, 3)] => Venus and Saturn are within 2° difference in latitude for Anshumard-yuti
    """
    from math import radians, sin, atan2, sqrt, degrees
    def compare_planet_coordinates(planet_coords):
        result = []
        n = len(planet_coords)
        
        def lat_distance(lat1, lat2):
            # Convert latitude to radians
            lat1_rad = radians(lat1)
            lat2_rad = radians(lat2)
            dlat = lat2_rad - lat1_rad
            a = sin(dlat / 2)**2
            return degrees(2 * atan2(sqrt(a), sqrt(1 - a)))
    
        for i in range(n):
            for j in range(i + 1, n):
                long1, lat1 = planet_coords[i]
                long2, lat2 = planet_coords[j]
                if long1 == long2:
                    if lat1 == lat2:
                        result.append((i, j, 0))
                    elif (lat1*lat2>0) and (lat_distance(lat1, lat2) * 3600 <= const.graha_yudh_criteria_1):  # 20 seconds
                        result.append((i, j, 1))
                    elif (lat1*lat2>0) and (lat_distance(lat1, lat2) <= const.graha_yudh_criteria_2):
                        result.append((i, j, 2))
                    elif lat_distance(lat1, lat2) <= const.graha_yudh_criteria_3:
                        result.append((i, j, 3))
        return result
    psi = planets_speed_info(jd, place)
    long_lat_list = [(long,lat) for _,(long,lat,_,_,_,_) in psi.items()]
    _graha_yudh_pairs = compare_planet_coordinates(long_lat_list)
    return _graha_yudh_pairs
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
    return (sunset(jd, place)[0] - sunrise(jd, place)[0])
def night_length(jd, place):
    """
        Return local night length in float hours
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: night length in float hours. e.g. 12.125
    """
    return (24.0 + sunrise(jd+1, place)[0] - sunset(jd, place)[0])
def sunset(jd, place,gauri_choghadiya_setting=False):
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
    if gauri_choghadiya_setting:
        # Convert to local time
        """ ADDED THE FOLLOWING IN V4.2.0 TO RECALCULATE RISE_JD"""
        dob = (y,m,d)
        tob = tuple(utils.to_dms(set_local_time, as_string=False))
        set_jd = utils.julian_day_number(dob, tob)
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
    moon_phase = _special_tithi_phase(rise, planet1, planet2, tithi_index, cycle)
    today = ceil(moon_phase / 12)
    """ SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME 
        See Dr. Jayasree Saranatha Mahabharatha date validation book """
    if const.increase_tithi_by_one_before_kali_yuga and jd < const.mahabharatha_tithi_julian_day: #V3.2.0
        #print('tithi increased by 1 before mahabharatha date from',today,'to',today+1)
        today = (today+1)%30
    degrees_left = today * 12 - moon_phase
    # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    planet1_long_diff = [ (sidereal_longitude(rise + t,planet1) - sidereal_longitude(rise,planet1)) % 360 for t in offsets ]
    planet2_long_diff = [ (sidereal_longitude(rise + t,planet2) - sidereal_longitude(rise,planet2)) % 360 for t in offsets ]
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
    moon_phase_tmrw = _special_tithi_phase(rise+1, planet1, planet2, tithi_index, cycle)
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
    #if not const.use_planet_speed_for_panchangam_end_timings: return _general_tithi(jd, place, tithi_index, planet1, planet2)
    def _get_tithi_using_planet_speed(jd,place):
        jd_utc = jd - place.timezone/24.
        #sunrise_jd = sunrise(jd, place)[2]
        tithi_phase = _special_tithi_phase(jd_utc, planet1=planet1, planet2=planet2, tithi_index=tithi_index, cycle=cycle)
        total = tithi_phase % 360
        one_tithi = 360/30
        tit = ceil(total /one_tithi)
        tithi_no = int(tit)
        degrees_left = tit * one_tithi-total
        one_day_hours = day_length(jd, place)+night_length(jd, place)
        """ Use only Moon/Sun Speeds for end time calculations and not the speeds of respective planets """
        daily_planet1_motion = daily_moon_speed(jd,place)
        daily_planet2_motion = daily_sun_speed(jd,place)
        end_time = jd_hours + degrees_left/(daily_planet1_motion-daily_planet2_motion)*one_day_hours
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
def tithi(jd,place,tithi_index=1,planet1=const._MOON, planet2=const._SUN,cycle=1):    
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
    if const.use_planet_speed_for_panchangam_end_timings:
        return tithi_using_planet_speed(jd, place, tithi_index, planet1, planet2, cycle)
    else:
        return tithi_using_inverse_lagrange(jd, place, tithi_index, planet1, planet2, cycle)
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
def _special_tithi_phase(jd,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1):
    planet1_long = sidereal_longitude(jd,planet1)
    planet2_long = sidereal_longitude(jd,planet2)
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
    jd_utc = utils.gregorian_to_jd(Date(y, m, d)); jd_ut = jd - tz/24.
    rise = sunrise(jd, place)[2] # - tz / 24 #V2.3.0
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [lunar_longitude(rise+t) for t in offsets] #V2.3.0 # Fixed 1.1.0 lunar longitude from sunrise to next sunrise
    # V4.4.0 changed from jd_ut to jd to match Adhik Maasa calculations
    nirayana_long = lunar_longitude(jd)
    raasi_no = int(nirayana_long/30)+1
    frac_left = 1.0 - (nirayana_long/30) % 1
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, raasi_no * 30)
    ends = (rise - jd_utc + approx_end) * 24 + tz #jd changed to jd_utc 2.0.3
    answer = [raasi_no, ends, frac_left]
    
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
        answer += [raasi_no, ends, frac_left]
    return answer
def _get_nakshathra(jd, place):
    """
        V4.2.1 With CoPilot help fixed special case of inverse lagrange
        where y list for Revathi may have longitudes either 0-14 degrees or 350-365 degrees
        or a mix of 0-14 and 350-365. This is now fixed 'somewhat'
    """
    tz = place.timezone
    y, m, d, _ = utils.jd_to_gregorian(jd)
    jd_ut = utils.gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2]
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise + t, const._MOON) for t in offsets]
    unwrapped_longitudes = utils.unwrap_angles(longitudes)
    #print("Unwrapped longitudes:", unwrapped_longitudes)

    # Extend angle range if needed
    extended_longitudes = utils.extend_angle_range(unwrapped_longitudes, 360)
    x = offsets * (len(extended_longitudes) // len(unwrapped_longitudes))
    
    nirayana_long = lunar_longitude(jd_utc)
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
    longitudes = [sidereal_longitude(rise+t, const._MOON) for t in offsets]
    nirayana_long = lunar_longitude(jd_utc) # Changed to jd_utc in V2.9.7
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
    if not const.use_planet_speed_for_panchangam_end_timings: return nakshatra(jd, place)
    _,_,_,jd_hours = utils.jd_to_gregorian(jd)
    def _get_nakshathra_new(jd):
        jd_utc = jd - place.timezone/24.
        one_star = 360/27
        moon_long = lunar_longitude(jd_utc)
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
def _special_yoga_phase(jd,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1):
    planet1_long = sidereal_longitude(jd,planet1)
    planet2_long = sidereal_longitude(jd,planet2)
    tithi_phase = (tithi_index*(planet1_long + planet2_long)+(cycle-1)*180) % 360
    return tithi_phase
def _get_yogam(jd,place,planet1=const._MOON,planet2=const._SUN,tithi_index=1,cycle=1):
    # 1. Find time of sunrise
    city, lat, lon, tz = place
    y, m, d,bt = jd_to_gregorian(jd);jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    rise = sunrise(jd, place)[2] # V2.2.8
    one_yoga = 360./27.
    # 2. Find the Nirayana longitudes and add them
    total = _special_yoga_phase(rise, planet1, planet2, tithi_index, cycle)
    # There are 27 Yogas spanning 360 degrees
    yog = ceil(total /one_yoga)
    yogam_no = int(yog)
    # 3. Find how many longitudes is there left to be swept
    degrees_left = yog * one_yoga - total
    
    # 3. Compute longitudinal sums at intervals of 0.25 days from sunrise
    offsets = [0.0,0.25, 0.5, 0.75, 1.0]
    """ Use only Moon/Sun longitudes for end time calculations and not the speeds of respective planets """
    planet1_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
    planet2_long_diff = [ (solar_longitude(rise + t,) - solar_longitude(rise)) % 360 for t in offsets ]
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
    total_tmrw = _special_yoga_phase(rise+1, planet1, planet2, tithi_index, cycle)
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
    if not const.use_planet_speed_for_panchangam_end_timings: return yogam_old(jd, place)
    _,_,_,jd_hours = utils.jd_to_gregorian(jd)
    def _get_yogam_new(jd):
        jd_utc = jd - place.timezone/24.
        yoga_phase = _special_yoga_phase(jd_utc, planet1=planet1, planet2=planet2, tithi_index=tithi_index, cycle=cycle)
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
        next_res = _get_yogam_new(jd+result[2])
        next_res [1] = result[2];
        next_res[2] += 24
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
    #if const.use_planet_speed_for_panchangam_end_timings: return yogam(jd, place, tithi_index, planet1, planet2, cycle)
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
def karana(jd, place):
    """
        returns the karanam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return karanam index, karanam starting time, karanam ending time, karanam fraction left 
          karanam index = [1..60]  1 = Kimstugna, 2 = Bava, ..., 60 = Naga
        This is corrected function from V4.2.8 onwards
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
def vaara(jd):
    """
        Weekday for given Julian day. 
        @param jd: Julian Day Number of the date/time
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    return ( int(ahargana(jd)) % 7 + 5) % 7 if const.use_aharghana_for_vaara_calcuation else int(ceil(jd + 1) % 7)  
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
    this_solar_month = raasi(last_new_moon,place)[0]
    next_solar_month = raasi(next_new_moon,place)[0]
    is_leap_month = (this_solar_month == next_solar_month)
    _lunar_month = (this_solar_month+1)%12
    #if _lunar_month > 12: _lunar_month = (_lunar_month % 12)
    is_nija_month = False
    if not is_leap_month:
        pm,pa,_ = lunar_month(jd-30, place)
        is_nija_month = (pm==_lunar_month and pa)
    return [int(_lunar_month), is_leap_month,is_nija_month]
def vedic_date(jd, place,calendar_type=0,tamil_month_method=const.tamil_month_method,base_time=0,use_utc=True):
    """
        Returns lunar month, lunar day and if it is adhika or not. and the vedic year
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param calendar_type: 0=Solar Calendar, 1=Amantha and 2=Purnimatha Lunar Calendar
        @param tamil_month_method,base_time,use_utc : See tamil_solar_month_and_date
        @return:
            vedic month,day,year,is_adhik_maasa?,is_nija_maaja?
            Vedic Year 0=Prabhava, 1=Vibhava... 58=Krodhana, 59=Akshaya
            Month range = 1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            adhika lunar_month True/False,
            Nija Month True/False
    """
    if calendar_type==0:
        py,pm,pd,_ = utils.jd_to_gregorian(jd); panchanga_date = Date(py,pm,pd)
        _month,_day = tamil_solar_month_and_date(panchanga_date, place, tamil_month_method, base_time, use_utc)
        _year = samvatsara(panchanga_date, place, zodiac=0)
        return _month+1,_day,_year, False,False
    else:
        use_purnimanta_system = (calendar_type==2)
        return lunar_month_date(jd, place, use_purnimanta_system)
def lunar_month_date(jd, place,use_purnimanta_system=False):
    """
        Returns lunar month, lunar day and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [indian month index,lunar_day, vedic_year,Adhika_Maasa_Boolean,Nija_Maasa_Boolean]
            1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            True if adhika lunar_month
        TODO: Purnimanta System Calculations have not been validated yet.
    """
    critical = sunrise(jd, place)[2] # V2.2.8
    ti = tithi(critical, place)[0]
    last_new_moon = new_moon(critical, ti, -1)
    next_new_moon = new_moon(critical, ti, +1)
    this_solar_month = raasi(last_new_moon,place)[0]-1
    next_solar_month = raasi(next_new_moon,place)[0]-1
    is_leap_month = (this_solar_month == next_solar_month)
    _lunar_month = (this_solar_month+1)%12
    lunar_day = utils.cyclic_count_of_numbers(from_number=1,to_number=ti,number_count=30,dir=1)
    if use_purnimanta_system:
        if lunar_day > 15: _lunar_month = (_lunar_month+1)%12
        lunar_day = (lunar_day - 16)%30 + 1
    is_nija_month = False
    if not is_leap_month:
        pm,pa,_ = lunar_month(jd-30, place)
        is_nija_month = (pm==_lunar_month and pa)
    _lunar_year = lunar_year_index(jd, _lunar_month+1)
    return [int(_lunar_month+1),lunar_day,_lunar_year, is_leap_month,is_nija_month]
def lunar_year_index(jd,maasa_index):
    """ 
        TODO: Need to investigate the following patching stuff 
        return samvat_index-1 returns -1 sometimes which is wrong??
    """
    kali = elapsed_year(jd, maasa_index)[0]
    kali_base = 14; kali_start = 27 # Pramaadhi
    """ Following is patching to match Prmaadhi at kali yuga start date """
    if kali < 4009 and const.force_kali_start_year_for_years_before_kali_year_4009:
        kali_start = const.kali_start_year
    if kali >= 4009:    kali = (kali - kali_base) % 60
    samvat_index = (kali + kali_start + int((kali * 211 - 108) / 18000)) % 60
    return samvat_index-1
# epoch-midnight to given midnight
# Days elapsed since beginning of Kali Yuga
ahargana = lambda jd: jd - const.mahabharatha_tithi_julian_day
kali_ahargana_days = lambda jd: int(ahargana(jd))
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
    #print('new moon',tithi(start+y0,place))
    return start + y0
def full_moon(jd, tithi_, opt = -1):
    """Returns JDN, where
       opt = -1:  JDN < jd such that lunar_phase(JDN) = 180 degrees
       opt = +1:  JDN >= jd such that lunar_phase(JDN) = 180 degrees
    """
    if tithi_ <=15:
        start = jd - tithi_ - 15 if opt==-1 else jd + (15-tithi_)
    else:
        start = jd - (tithi_ - 15) if opt==-1 else jd + (45 - tithi_)
    # Search within a span of (start +- 2) days
    x = [ -2 + offset/4 for offset in range(17) ]
    y = [lunar_phase(start + i) for i in x]
    y = utils.unwrap_angles(y)
    y0 = utils.inverse_lagrange(x, y, 180)
    return start + y0
def next_tithi(jd,place,required_tithi,opt=1,start_of_tithi=True):
    """
    TODO: UNDER EXPERIMENTATION
      Returns JDN, where
       opt = -1:  JDN < jd such that lunar_phase(JDN) = required_tithi*12 degrees
       opt = +1:  JDN >= jd such that lunar_phase(JDN) = required_tithi*12 degrees
    """
    tz = place.timezone
    tithi_ = tithi(jd,place)[0]
    tithi_angle = (required_tithi-1)*12 if start_of_tithi else required_tithi*12 
    if tithi_ <=required_tithi:
        inc_days = - tithi_ - required_tithi if opt==-1 else  (required_tithi-tithi_)
    else:
        inc_days = - (tithi_ - required_tithi) if opt==-1 else  (30+required_tithi - tithi_)
    start = jd + inc_days
    #print(tithi_,required_tithi,inc_days,utils.jd_to_gregorian(start))
    x = [ -2 + offset/4 for offset in range(17) ]
    y = [lunar_phase(start + i) for i in x]
    #y = utils.unwrap_angles(y)
    y0 = utils.inverse_lagrange(x, y, tithi_angle)
    tithi_jd = start+y0+tz/24
    #print(tithi(tithi_jd,place),solar_longitude(tithi_jd),lunar_longitude(tithi_jd),lunar_phase(tithi_jd))
    return tithi_jd
def next_lunar_month(jd, place,lunar_month_type=0,direction=1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(next_planet_entry_date(0, jd, place)[0]) if direction==1 else \
                          utils.jd_to_gregorian(previous_planet_entry_date(0, jd, place)[0])
        return Date(lmy,lmm,lmd),lmh
    _tithi_to_check = 30 if lunar_month_type==0 else 15
    tithi_ = tithi(jd,place)[0]
    lm_jd = new_moon(jd, tithi_, opt=direction) if lunar_month_type==0 else full_moon(jd, tithi_, opt=direction)
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
def previous_lunar_month(jd, place,lunar_month_type=0,direction=-1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(next_planet_entry_date(0, jd, place)[0]) if direction==1 else \
                          utils.jd_to_gregorian(previous_planet_entry_date(0, jd, place)[0])
        return Date(lmy,lmm,lmd),lmh
    _tithi_to_check = 30 if lunar_month_type==0 else 15
    tithi_ = tithi(jd,place)[0]
    lm_jd = new_moon(jd, tithi_, opt=direction) if lunar_month_type==0 else full_moon(jd, tithi_, opt=direction)
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
def lunar_phase(jd,tithi_index=1):
    solar_long = solar_longitude(jd)
    lunar_long = lunar_longitude(jd)
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
    srise = sunrise(jd, place); sset = sunset(jd,place,gauri_choghadiya_setting=True)
    day_dur = (sset[0] - srise[0])/24
    end_times = []; start_time = srise[1]
    _vaara = vaara(jd)
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
    srise = sunrise(jd, place); sset = sunset(jd,place,gauri_choghadiya_setting=True)
    day_dur = (sset[0] - srise[0])/24
    end_times = []; start_time = srise[1]
    _vaara = vaara(jd)
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
    weekday = vaara(jd)
    
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
        Get dhur muhurtham timing for the given julian day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: start and end time of dhur muhurtham - as list e.g. [start_time, end_time]
    """
    # Night = today's sunset to tomorrow's sunrise
    srise = sunrise(jd, place)[0]; day_dur = day_length(jd,place); night_dur = night_length(jd,place)
    sset = sunset(jd,place)[0]
    weekday = vaara(jd)
    
    # There is one durmuhurtam on Sun, Wed, Sat; the rest have two
    # Offsets from sunrise 10.4 means 6 + 10.4 = 16.4 = 4:24 PM
    # Ref: Panchangam Calculations - Karanam Ramakumar
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
            start_times[i] = utils.to_dms(start_times[i])
            end_times[i] = utils.to_dms(end_times[i])
            answer += [start_times[i],end_times[i]]
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
    if int(long_in_raasi+const.one_second_lontitude_in_degrees) == 30:
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
    _ayanamsa = get_ayanamsa_value(jd)
    pp = dhasavarga(jd,place,divisional_chart_factor=1)[:7]
    bhujas = [0 for _ in range(7)]
    north_south_sign = [1 for _ in range(7)]
    for p,(h,long) in pp:
        p_long = h*30 + long+_ayanamsa #V4.5.0
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
    sl = solar_longitude(start_jd)
    _tamil_month = int(sl/30)
    sunset_count=1
    while True:
        if sl%30<1 and sl%30>0:
            break
        start_jd -= 1
        sl = solar_longitude(start_jd)
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
def tamil_solar_month_and_date_RaviAnnnaswamy(panchanga_date,place): #_RaviAnnnaswamy V4.4.0
    jd = utils.julian_day_number(panchanga_date, (10,0,0))
    jd_set = sunset(jd, place)[2]
    jd_utc = jd_set - place.timezone/24
    sr = solar_longitude(jd_utc)
    tamil_month = int(sr/30)
    daycount=1
    while True:
        if sr%30<1 and sr%30>0:
            break
        jd_utc -= 1
        sr = solar_longitude(jd_utc)
        daycount+=1
    return tamil_month, daycount
def tamil_solar_month_and_date(panchanga_date,place,tamil_month_method=const.tamil_month_method,base_time=0,use_utc=True):
    """
        Returns tamil month and date (e.g. Aadi 28 )
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @param base_time: 0 => sunset time, 1 => sunrise time 2 => midday time
        @param use_utc: True (default) use uninversal time
        @return: tamil_month_number, tamil_date_number
        i.e. [0..11, 1..32]
        Note: Tamil month is sankranti based solar month - not lunar month
        And it is very sensitive to solar longitude. 
        """
    if tamil_month_method==0: # sunset and UTC
        return tamil_solar_month_and_date_RaviAnnnaswamy(panchanga_date, place)
    elif tamil_month_method==1: # sunset jd as starting jd
        return tamil_solar_month_and_date_V4_3_5(panchanga_date, place)
    elif tamil_month_method==2: # startjd at 10AM
        return tamil_solar_month_and_date_V4_3_8(panchanga_date, place)
    else: #
        return tamil_solar_month_and_date_new(panchanga_date, place, base_time, use_utc)
def tamil_solar_month_and_date_new(panchanga_date,place,base_time=0,use_utc=True): # V4.4.0
    """
        @param base_time: 0 => sunset time, 1 => sunrise time 2 => midday time
        @param use_utc: True (default) use uninversal time
    """
    jd = utils.julian_day_number(panchanga_date, (10,0,0))
    jd_base = sunset(jd, place)[2] if base_time==0 else (sunrise(jd,place)[2] if base_time==1 else midday(jd, place)[1])
    jd_utc = jd_base - place.timezone/24 if use_utc else jd_base
    sr = solar_longitude(jd_utc)
    tamil_month = int(sr/30)
    daycount=1
    while True:
        if sr%30<1 and sr%30>0:
            break
        jd -= 1
        jd_base = sunset(jd, place)[2] if base_time==0 else (sunrise(jd,place)[2] if base_time==1 else midday(jd, place)[1])
        jd_utc = jd_base - place.timezone/24 if use_utc else jd_base
        sr = solar_longitude(jd_utc)
        daycount+=1
    return tamil_month, daycount
def tamil_solar_month_and_date_from_jd(jd,place):
    jd_set = sunset(jd, place)[2]
    jd_utc = jd_set - place.timezone/24
    sr = solar_longitude(jd_utc)
    tamil_month = int(sr/30)
    daycount=1
    while True:
        if sr%30<1 and sr%30>0:
            break
        jd_utc -= 1
        sr = solar_longitude(jd_utc)
        daycount+=1
    return tamil_month, daycount
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
    """
        TODO: Handle While loop if not converging - provide max count to stop
    """
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
    if (years==1 and months==1 and sixty_hours==1): return jd_at_dob
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
def __next_conjunction_of_planet_pair(jd,panchanga_place:Place,p1,p2,direction=1,separation_angle=0):
    divisional_chart_factor = 1
    start_jd = jd
    cur_jd = start_jd - 1*direction
    end_jd = start_jd + 1*direction
    while cur_jd*direction < end_jd*direction:
        cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
        if p1==8:
            p1_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        elif p1==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p1_long = (sla[0]*30+sla[1])*divisional_chart_factor%360
        else:
            p1_long = (sidereal_longitude(cur_jd_utc, planet_list[p1]))
        if p2==8:
            p2_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        elif p2==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p2_long = (sla[0]*30+sla[1])*divisional_chart_factor%360
        else:
            p2_long = (sidereal_longitude(cur_jd_utc, planet_list[p2]))
        long_diff = (p1_long - p2_long - separation_angle)%360
        if abs(long_diff) < const.minimum_separation_longitude:
            #print('Found closest time:',utils.jd_to_gregorian(cur_jd))
            return cur_jd,utils.norm360(p1_long),utils.norm360(p2_long)
        cur_jd += const.conjunction_increment*direction
    return None
def next_conjunction_of_planet_pair(jd,panchanga_place:Place,p1,p2,direction=1,separation_angle=0,increment_speed_factor=0.25):
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
    _planet_speeds = [361]+[abs(psi[3]) for p,psi in planets_speed_info(jd, panchanga_place).items()]
    p1_speed = _planet_speeds[0] if p1=='L' else _planet_speeds[p1+1]
    p2_speed = _planet_speeds[0] if p2=='L' else _planet_speeds[p2+1]
    increment_days = increment_speed_factor/p1_speed if p1_speed > p2_speed else increment_speed_factor/p2_speed
    increment_days *= direction
    _DEBUG_ = False
    if (p1==7 and p2==8) or (p1==8 and p2==7):
        warnings.warn("Rahu and Ketu do not conjoin ever. Program returns error")
        return None
    #increment_days=1.0/24.0/60.0*direction if p1 in ['L'] or p2 in ['L'] else 1*direction
    long_diff_check = 0.5# if p1 in ['L'] or p2 in ['L'] else 1.0
    max_days_to_search = 1000000
    cur_jd = jd# utils.julian_day_number(panchanga_start_date, (0,0,0))
    cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
    search_counter = 1
    while search_counter < max_days_to_search:
        cur_jd += increment_days
        cur_jd_utc = cur_jd - panchanga_place.timezone/24.0
        if p1==8:
            p1_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        elif p1==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p1_long = (sla[0]*30+sla[1])
        else:
            p1_long = (sidereal_longitude(cur_jd_utc, planet_list[p1]))
        if p2==8:
            p2_long = (ketu(sidereal_longitude(cur_jd_utc, planet_list[7])))
        elif p2==const._ascendant_symbol:
            sla = ascendant(cur_jd, panchanga_place); p2_long = (sla[0]*30+sla[1])
        else:
            p2_long = (sidereal_longitude(cur_jd_utc, planet_list[p2]))
        long_diff = (360+p1_long - p2_long - separation_angle)%360
        if _DEBUG_: print(search_counter,p1,p1_long,p2,p2_long,long_diff,long_diff_check,utils.jd_to_gregorian(cur_jd))
        if long_diff<long_diff_check:
            if _DEBUG_: print(long_diff,'<',long_diff_check)
            #ret = __next_conjunction_of_planet_pair(p1,p2,panchanga_place,cur_jd,direction,separation_angle)
            jd_list = [cur_jd+t*increment_days for t in range(-10,10)]
            long_diff_list = []
            for jdt in jd_list:
                if p1==8:
                    p1_long = (ketu(sidereal_longitude(jdt-panchanga_place.timezone/24, planet_list[7])))
                elif p1==const._ascendant_symbol:
                    sla = ascendant(jdt, panchanga_place); p1_long = (sla[0]*30+sla[1])
                else:
                    p1_long = (sidereal_longitude(jdt-panchanga_place.timezone/24, planet_list[p1]))
                if p2==8:
                    p2_long = (ketu(sidereal_longitude(jdt-panchanga_place.timezone/24, planet_list[7])))
                elif p2==const._ascendant_symbol:
                    sla = ascendant(jdt, panchanga_place); p2_long = (sla[0]*30+sla[1])
                else:
                    p2_long = (sidereal_longitude(jdt-panchanga_place.timezone/24, planet_list[p2]))
                long_diff = (360+p1_long-p2_long-separation_angle)%360
                long_diff_list.append(long_diff)
            """ TODO: For separation Angle > 180 Lagrange may not work """
            try:
                if _DEBUG_: print('Lagrange method of fine tuning')
                if _DEBUG_: print(jd_list,'\n',long_diff_list)
                conj_jd = utils.inverse_lagrange(jd_list, long_diff_list, 0.0)
                if p1==8:
                    p1_long = (ketu(sidereal_longitude(conj_jd-panchanga_place.timezone/24, planet_list[7])))
                elif p1==const._ascendant_symbol:
                    sla = ascendant(conj_jd, panchanga_place); p1_long = (sla[0]*30+sla[1])
                else:
                    p1_long = (sidereal_longitude(conj_jd-panchanga_place.timezone/24, planet_list[p1]))
                if p2==8:
                    p2_long = (ketu(sidereal_longitude(conj_jd-panchanga_place.timezone/24, planet_list[7])))
                elif p2==const._ascendant_symbol:
                    sla = ascendant(conj_jd, panchanga_place); p2_long = (sla[0]*30+sla[1])
                else:
                    p2_long = (sidereal_longitude(conj_jd-panchanga_place.timezone/24, planet_list[p2]))
                if conj_jd is not None:
                    if _DEBUG_: print(p1,p2,utils.jd_to_gregorian(conj_jd),p1_long,p2_long)
                    return conj_jd, p1_long, p2_long
            except:
                if _DEBUG_: print('Normal method of fine tuning - since Lagrange failed')
                if _DEBUG_: print(search_counter,p1,p1_long,p2,p2_long,long_diff,long_diff_check,utils.jd_to_gregorian(cur_jd))
                ret = __next_conjunction_of_planet_pair(cur_jd,panchanga_place,p1,p2,direction,separation_angle)
                if ret is not None:
                    return ret
                
        search_counter += 1
    print('Could not find planetary conjunctions for sep angle',separation_angle,' Try increasing search range')
    return None
def __previous_conjunction_of_planet_pair(p1,p2,panchanga_place:Place,start_jd,separation_angle=0):
    return __next_conjunction_of_planet_pair(p1, p2, panchanga_place, start_jd, direction=-1,separation_angle=separation_angle)
def previous_conjunction_of_planet_pair(jd,panchanga_place:Place,p1,p2,separation_angle=0,increment_speed_factor=0.25):
    return next_conjunction_of_planet_pair(jd, panchanga_place, p1, p2, direction=-1, separation_angle=separation_angle,
                                           increment_speed_factor=increment_speed_factor)
def previous_planet_entry_date(planet,jd,place,increment_days=0.01,precision=0.1,raasi=None):
    return next_planet_entry_date(planet,jd,place,direction=-1,increment_days=increment_days,precision=precision,raasi=raasi)
def previous_ascendant_entry_date(jd,place,increment_days=0.01,precision=0.1,raasi=None,divisional_chart_factor=1):
    return next_ascendant_entry_date(jd, place, direction=-1, increment_days=increment_days, precision=precision, raasi=raasi,divisional_chart_factor=divisional_chart_factor)
def next_ascendant_entry_date(jd,place,direction=1,precision=1.0,raasi=None,divisional_chart_factor=1):
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
        multiple = (raasi-1)*30
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
def next_planet_entry_date(planet,jd,place,direction=1,increment_days=0.01,precision=0.1,raasi=None):
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
    if planet == const._ascendant_symbol:
        return next_ascendant_entry_date(jd, place, direction=direction, precision=1.0, raasi=raasi)
    pl = planet_list[planet] if isinstance(planet,int) else const._ascendant_symbol
    if pl==const._ascendant_symbol or pl==const._MOON: increment_days = 1.0/24.0/60.0 # For moon/lagna increment days in minutes
    if pl==const._KETU:
        raghu_raasi = (raasi-1+6)%12+1 if raasi!=None else raasi
        ret = next_planet_entry_date(7, jd, place,direction=direction,raasi=raghu_raasi)
        p_long = (ret[1]+180)%360
        return ret[0],p_long
    " get current raasi of planet = t_month "
    jd_utc = jd - place.timezone/24.0
    if planet==const._ascendant_symbol:
        sla = ascendant(jd, place); sl = sla[0]*30+sla[1]
    else:
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
        jd += increment_days*direction; jd_utc = jd - place.timezone/24.0
        if planet==const._ascendant_symbol:
            sla = ascendant(jd, place); sl = sla[0]*30+sla[1]
        else:
            sl = sidereal_longitude(jd_utc,pl)
    sank_date = jd_to_gregorian(jd_utc)
    sank_sunrise = sunrise(jd_utc,place)[2]
    sank_date = Date(sank_date[0],sank_date[1],sank_date[2])
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0] 
    planet_longs = []
    for t in offsets:
        if planet==const._ascendant_symbol:
            sla = ascendant(sank_sunrise+t, place); sl = sla[0]*30+sla[1]
        else:
            sl = sidereal_longitude(sank_sunrise+t,pl)
        planet_longs.append(sl)
    planet_hour = utils.inverse_lagrange(offsets, planet_longs, multiple) # Do not move % 360 above
    sank_jd_utc = utils.gregorian_to_jd(sank_date)
    planet_hour1 = (sank_sunrise + planet_hour - sank_jd_utc)*24+place.timezone
    sank_jd_utc += planet_hour1/24.0
    if planet==const._ascendant_symbol:
        sla = ascendant(sank_jd_utc-place.timezone/24, place); planet_long = sla[0]*30+sla[1]
    else:
        planet_long = sidereal_longitude(sank_jd_utc-place.timezone/24,pl)
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
def graha_drekkana(jd,place,use_bv_raman_table=False):
    return [const.drekkana_table_bvraman[h][int(long//10)] for _,(h,long) in dhasavarga(jd, place)] if use_bv_raman_table \
        else [const.drekkana_table[h][int(long//10)] for _,(h,long) in dhasavarga(jd, place)]
def sahasra_chandrodayam_old(dob,tob,place):
    """
        TODO: Does not support BCE dates as ephem supports only datetime
    """
    if '-' in str(dob[0]): return (-1,-1,-1)
    import ephem
    from datetime import datetime, timedelta
    try:
        birth_date = datetime(dob[0],dob[1],dob[2],tob[0],tob[1])
        current_date = birth_date - timedelta(hours=place.timezone)  # Convert to UTC
    except:
        print(birth_date,'not a valid date')
        return None
    observer = ephem.Observer()
    observer.lat = str(place.latitude)
    observer.lon = str(place.longitude)
    observer.elevation = 0
    full_moons_count = 0
    while full_moons_count < 1000:
        observer.date = current_date
        next_full_moon = ephem.next_full_moon(observer.date)
        full_moons_count += 1
        current_date = next_full_moon.datetime()
    sahasra_date = current_date + timedelta(hours=place.timezone)
    return sahasra_date.timetuple()[:-3]
def sahasra_chandrodayam(jd,place):
    full_moons_count = 0
    tithi_ = tithi(jd,place)[0]
    while full_moons_count < 1000:
        full_moon_jd = full_moon(jd, tithi_, opt=1)
        #print(full_moons_count,utils.jd_to_gregorian(full_moon_jd))
        full_moons_count += 1
        jd = full_moon_jd+0.25
        tithi_ = tithi(jd,place)[0]
    sahasra_date = utils.jd_to_gregorian(full_moon_jd)
    return sahasra_date[:-1]
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
    day = vaara(jd)
    return const.anandhaadhi_yoga_day_star_list[day].index(nak[0]-1),nak[2]
def triguna(jd,place):
    _,_,_,fh = utils.jd_to_gregorian(jd)
    day = vaara(jd)
    return utils.triguna_of_the_day_time(day,fh)
def vivaha_chakra_palan(jd,place):
    jd_utc = jd - place.timezone/24
    sun_long = sidereal_longitude(jd, const._SUN)
    sun_star = nakshatra_pada(sun_long)[0]
    
    moon_long = sidereal_longitude(jd, const._MOON)
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
    wday = vaara(jd)
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
def tamil_jaamam(jd,place):
    """ 
        In Tamil 1 jaamam = 3 muhurthas. 10 jaamam = 1 day (5 jaamam) and night (5 jaamam)
        8th jaamam = 3rd muhurtha of night
    """
    dl = day_length(jd, place); day_jaamam = dl/5
    nl = night_length(jd, place); night_jaamam = nl/5
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
def udhaya_lagna_muhurtha(jd,place):
    """
        returns ascendant entry jd into each of 12 rasis from given date/time
        returns [(rasi,rasi_entry_jd,rasi_exit_jd),...]
    """
    asc = ascendant(jd, place)[0]
    jd_start = next_ascendant_entry_date(jd, place, direction=-1)[0]
    jd = jd_start+const.conjunction_increment
    ulm = []
    for l in range(12):
        jd_end = next_ascendant_entry_date(jd, place,precision=1.0)[0]
        _,_,_,fhs = utils.jd_to_gregorian(jd_start)
        _,_,_,fhe = utils.jd_to_gregorian(jd_end)
        ulm.append(((asc+l)%12,fhs,fhe))
        jd_start = jd_end
        jd = jd_end+const.conjunction_increment
    return ulm
def chandrabalam(jd,place):
    ascs = [(ulm[0],ulm[1]) for ulm in udhaya_lagna_muhurtha(jd, place)]
    moon = int(lunar_longitude(jd)/30)+1
    next_sunrise = sunrise(jd+1,place)[-1]
    cb_good = [1,3,6,7,10]
    cb = [ah for ah,at in ascs if utils.count_rasis(ah,moon) in cb_good and at < next_sunrise]
    next_moon = next_planet_entry_date(planet=1, jd=jd, place=place)[0]
    if next_moon < next_sunrise:
        #print('moon in two rasis today')
        cb += [ah for ah,at in ascs if utils.count_rasis(ah,(moon+1)%12) in cb_good and at < next_sunrise]
    return cb
def panchaka_rahitha(jd,place):
    ulm = udhaya_lagna_muhurtha(jd, place)
    bad_panchakas = [1,2,4,6,8]
    pr = []
    for asc,asc_beg,asc_end in ulm:
        _tithi = tithi(jd, place)[0]+1
        _nak = nakshatra(jd, place)[0]
        _day = vaara(jd)+1
        _asc_rasi = asc+1
        rem = (_tithi+_nak+_day+_asc_rasi)%9
        if rem in bad_panchakas:
            pr.append((rem,asc_beg,asc_end))
        else:
            pr.append((0,asc_beg,asc_end))
    return pr
def next_panchaka_days(jd,place):
    """
        Added in V4.2.6
        Start and ending of panchak nakshthras
        The five Panchak Nakshatras are as follows:3rd and 4th pada of Dhanishta, Shatabisha, Purva Bhadrapada
        Uttara Bhadrapada, Revati.
        Calculate moon entry of Kumbha (Dhanishta 3rd paadham) and moon entry of Aries (end of Revathi)
        @return: start_jd_of_dhanishta 3rd paada, end_jd_of_revathi
    """
    panchaka_start_jd = next_planet_entry_date(const._MOON, jd, place, raasi=11)[0]
    panchaka_end_jd = next_planet_entry_date(const._MOON, jd, place, raasi=1)[0]
    return panchaka_start_jd, panchaka_end_jd
def chandrashtama(jd, place):
    jd_utc = jd - place.timezone/24.
    moon_long = lunar_longitude(jd_utc); moon = dasavarga_from_long(moon_long)[0]
    _chandrashtama_rasi = (moon-7)%12+1
    next_moon_jd = next_planet_entry_date(const._MOON, jd, place)[0]
    return _chandrashtama_rasi, next_moon_jd
def nava_thaara(jd,place,from_lagna_or_moon=0):
    base_star = nakshatra(jd, place)[0]-1 if from_lagna_or_moon==1 else ascendant(jd,place)[2]-1
    ntl = [[(base_star+s)%27 for s in star_list] for _, star_list in const.nakshathra_lords.items()]
    return [(lord,sl) for sl in ntl for lord,csl in const.nakshathra_lords.items() if sorted(sl)==sorted(csl) ]
def special_thaara(jd,place,from_lagna_or_moon=0):
    """
        Note: the star list includes Abhijith as 21st star
    """
    base_star = nakshatra(jd, place)[0]-1 if from_lagna_or_moon==1 else ascendant(jd,place)[2]-1
    base_inc = -1  if from_lagna_or_moon==1 else 0
    stl = [(base_star+s+base_inc)%28 for s in const.special_thaara_map]
    _star_list = utils.get_nakshathra_list_with_abhijith()
    if base_star+1 > const._ABHIJITH_STAR_INDEX: base_star += 1
    #print(base_star,'base_star',_star_list[base_star],stl)
    return [(lord,star) for star in stl for lord, csl in const.special_thaara_lords_1.items() if star in csl]
def karaka_tithi(jd,place):
    pp = [['L',(0,-10)]]+dhasavarga(jd, place) # Dummy Lagna Positions added
    from jhora.horoscope.chart import house
    ks = house.chara_karakas(pp); p1 = planet_list[ks[1]];p2 = planet_list[ks[0]]
    kt = tithi(jd, place, tithi_index=1, planet1=p1, planet2=p2)
    return kt
def karaka_yogam(jd,place):
    """
        returns the yogam at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left, 
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          next yogam index and next yogam time is additionally returned if two yogams on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
    pp = [['L',(0,-10)]]+dhasavarga(jd, place) # Dummy Lagna Positions added
    from jhora.horoscope.chart import house
    ks = house.chara_karakas(pp); p1 = planet_list[ks[1]];p2 = planet_list[ks[0]]
    return yogam(jd, place, tithi_index=1, planet1=p1, planet2=p2, cycle=1)
    _yoga = _get_yogam(jd, place,planet1=p1,planet2=p2)
    _yoga_prev = _get_yogam(jd-1, place,planet1=p1,planet2=p2)
    _yoga_no = _yoga[0]; _yoga_start = _yoga_prev[1]; _yoga_end = _yoga[1]
    if _yoga_start < 24.0:
        _yoga_start = -_yoga_start
    elif _yoga_start > 24:
        _yoga_start -= 24.0
    result = [_yoga_no,_yoga_start,_yoga_end]
    if len(_yoga)>2:
        _yn = _yoga[2]; _yn_start = _yoga_end; _yn_end = _yoga[3]
        result += [_yn,_yn_start,_yn_end]
    return result
def fraction_moon_yet_to_traverse(jd,place,round_to_digits=5):
    jd_utc = jd - place.timezone/24.
    one_star = 360/27
    moon_long = lunar_longitude(jd_utc)
    _,_,rem = nakshatra_pada(moon_long)
    moon_fraction_yet_to_traverse = (one_star-rem)/one_star
    return round(moon_fraction_yet_to_traverse,round_to_digits)
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
    day = vaara(jd)+1
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
    day = vaara(jd)+1
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
    moon_star = nakshatra_pada(lunar_longitude(jd_utc))[0]
    sun_star = nakshatra_pada(solar_longitude(jd_utc))[0]
    srise = sunrise(jd,place)[0]
    knt = utils.cyclic_count_of_stars_with_abhijit_in_22(const.abhijit_order_of_stars, sun_star-1,moon_star-1)
    #print(moon_star,sun_star,knt,'in',[2,7,9,14,16,21,23,28])
    return (srise,star_end) if knt in [2,7,9,14,16,21,23,28] else ()
def vidaal_yoga(jd,place):
    jd_utc = jd - place.timezone/24.
    nak = nakshatra(jd, place); star_end = nak[3]
    moon_star = nakshatra_pada(lunar_longitude(jd_utc))[0]
    sun_star = nakshatra_pada(solar_longitude(jd_utc))[0]
    srise = sunrise(jd,place)[0]
    knt = utils.cyclic_count_of_stars_with_abhijit_in_22(const.abhijit_order_of_stars, sun_star-1,moon_star-1)
    #print(moon_star,sun_star,knt,'in',[3,6,10,13,17,20,24,27])
    return (srise,star_end) if knt in [3,6,10,13,17,20,24,27] else ()
def disha_shool(jd):
    return const.disha_shool_map[vaara(jd)]
def yogini_vaasa(jd,place):
    tithi_index = tithi(jd,place)[0]
    return const.yogini_vaasa_tithi_map[tithi_index-1]
 # Convert to Ghati, Phala Vighati
def float_hours_to_vedic_time_equal_day_night_ghati(jd,place,float_hours=None,
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
def float_hours_to_vedic_time(jd, place, float_hours=None,force_equal_day_night_ghati=False,
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
    if vedic_hours_per_day not in [30,60]: vedic_hours_per_day = 60
    if force_equal_day_night_ghati: return float_hours_to_vedic_time_equal_day_night_ghati(jd, place, float_hours)
    if float_hours is None:
        _, _, _, float_hours = utils.jd_to_gregorian(jd)
    
    today_sunrise = sunrise(jd, place)[0]
    tomorrow_sunrise = 24 + sunrise(jd + 1, place)[0]
    ghati_per_hour = vedic_hours_per_day / (tomorrow_sunrise - today_sunrise)
    local_hours_since_sunrise = float_hours - today_sunrise
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
def next_lunar_year(jd,place,lunar_month_type=0,direction=1):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    _DEBUG_= False
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(next_solar_year(jd, place)[0]); 
        return Date(lmy,lmm,lmd),lmh
    for _ in range(13):
        (lmy,lmm,lmd),lmh = next_lunar_month(jd, place, lunar_month_type) if direction==1 else previous_lunar_month(jd, place, lunar_month_type)
        #tithi_ = tithi(jd,place)[0]
        #lmy,lmm,lmd,lmh = utils.jd_to_gregorian(new_moon(jd,tithi_,opt=direction)) if lunar_month_type==0 else utils.jd_to_gregorian(full_moon(jd,tithi_,opt=direction))
        if _DEBUG_: print(lunar_month_type,(lmy,lmm,lmd),lmh)
        jd = utils.julian_day_number(Date(lmy,lmm,lmd), (lmh,0,0))
        lm = lunar_month_date(jd, place, use_purnimanta_system=lunar_month_type)
        if _DEBUG_: print('lunar month date',lm)
        _lunar_month_number=((lm[0]+1)%12 if lm[-1]==30 else lm[0])
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
                if _DEBUG_: print('after lm',lunar_month_date(jd-1, place, use_purnimanta_system=lunar_month_type))
            elif _tithi[1] < 0 and (_tithi[0]==1 or _tithi[0]==16) and direction==1:
                if _DEBUG_: print('tithi on lunar year day starts previous day',_tithi[1])
                lmy,lmm,lmd = utils.previous_panchanga_day(Date(lmy,lmm,lmd), minus_days=1)
                lmh = abs(_tithi[1])
            return Date(lmy,lmm,lmd),lmh
        jd += direction*14
    if _DEBUG_: print('next/prev lunar_year could not be found')
def previous_lunar_year(jd,place,lunar_month_type=0):
    """
        @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month
    """
    _DEBUG_ = False
    if lunar_month_type==2:
        lmy,lmm,lmd,lmh = utils.jd_to_gregorian(previous_solar_year(jd, place)[0]); 
        return Date(lmy,lmm,lmd),lmh
    return next_lunar_year(jd, place, lunar_month_type, direction=-1)
    for _ in range(13):
        (lmy,lmm,lmd),lmh = previous_lunar_month(jd, place, lunar_month_type)
        if _DEBUG_: print((lmy,lmm,lmd),lmh)
        jd = utils.julian_day_number(Date(lmy,lmm,lmd), (lmh,0,0))
        lm = lunar_month_date(jd, place, use_purnimanta_system=lunar_month_type)
        if _DEBUG_: print(lm)
        #if direction==1:
        _lunar_month_number=(lm[0]+1)%12 if lm[-1]==30 else lm[0]
        _lunar_month_start = 1
        if _lunar_month_number==_lunar_month_start:
            if _DEBUG_: print('found lunar year date')
            jd = utils.julian_day_number(Date(lmy,lmm,lmd), (lmh,0,0))
            lm = lunar_month_date(jd, place, use_purnimanta_system=lunar_month_type)
            if _DEBUG_: print(lm)
            return Date(lmy,lmm,lmd),lmh
        jd -= 14
    if _DEBUG_: print('next/prev lunar_year could not be found')
special_tithis = lambda jd,place: [[tithi(jd, place, tithi_index=t,cycle=c) for t in range(1,13)] for c in range(1,4)]
if __name__ == "__main__":
    utils.set_language('ta')
    #const.use_24hour_format_in_to_dms= False
    set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
    dob = Date(1909,7,29); tob = (6,50,0); place = Place('Hyderabad,India',17,77,5.5)
    #dob = Date(2025,3,19); #place = Place('Chicago,US', 41.85, -87.65, -6.0)
    #dob = (-3101,1,22); place = Place('Ujjain,India',23.18,75.77,5.5)
    #dob = (-5114,1,9); tob = (12,10,0); place = Place('Ayodhya,India',26+48/60,82+12/60,5.5)
    jd = utils.julian_day_number(dob,tob);jd1 = utils.julian_day_number(dob,tob)
    print(gulika_longitude(dob,tob,place))
    print(dhasavarga(jd, place, divisional_chart_factor=1))
    print(ascendant(jd, place))
    exit()
    const.use_planet_speed_for_panchangam_end_timings = True
    print(tithi(jd,place)); print(tithi(jd1,place))
    const.use_planet_speed_for_panchangam_end_timings = False
    print(tithi(jd,place)); print(tithi(jd1,place))
    exit()
    st = special_tithis(jd, place)
    for _cycle in range(1,4):
        for t in range(1,13):
            _tithi_returned = st[_cycle-1][t-1]
            _paksha = 0 if _tithi_returned[0]<=15 else 1
            _cycle_str = '' if _cycle==1 else ' ('+utils.resource_strings['cycle_str']+'-'+str(_cycle)+')'
            key = utils.resource_strings[const.special_tithis[t-1]+'_tithi_str']+_cycle_str
            from_str = utils.to_dms(_tithi_returned[1])+' '+utils.resource_strings['starts_at_str']
            end_str = utils.to_dms(_tithi_returned[2])+' '+utils.resource_strings['ends_at_str']
            value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi_returned[0]-1]
            value += ' '+from_str+' '+end_str
            print(key,value)
    exit()
    for _ in range(365):
        y,m,d,_=utils.jd_to_gregorian(jd)
        lmd = lunar_month_date(jd,place)
        srise = sunrise(jd, place); sset = sunset(jd,place)
        print(y,m,d,'tithi',tithi(srise[2],place),'Amanta lunar month date',lmd)
        lmd = lunar_month_date(jd,place,use_purnimanta_system=True)
        print(y,m,d,'tithi',tithi(srise[2],place),'Purnimanta lunar month date',lmd)
        jd += 1
    exit()
    print(utils.to_dms(sunrise(jd, place)[0],round_to_minutes=True))
    exit()
    m=muhurthas(jd, place)
    for mn,ma,(ms,me) in m:
        print(utils.resource_strings['muhurtha_'+mn+'_str'],
              utils.resource_strings['auspicious_str'] if ma==1 else utils.resource_strings["inauspicious_str"],
              utils.to_dms(ms),utils.to_dms(me))
    exit()
    _,_,_,bt_hours = utils.jd_to_gregorian(jd)
    print('btime',float_hours_to_vedic_time(jd, place),float_hours_to_vedic_time_equal_day_night_ghati(jd, place))
    srise = sunrise(jd,place)
    print('sunrise',float_hours_to_vedic_time(jd, place, srise[0]),float_hours_to_vedic_time_equal_day_night_ghati(jd, place, srise[0]))
    sset = sunset(jd,place)
    print('sunset',float_hours_to_vedic_time(jd, place, sset[0]),float_hours_to_vedic_time_equal_day_night_ghati(jd, place, sset[0]))
    mrise = moonrise(jd, place)
    print('moonrise',float_hours_to_vedic_time(jd, place, mrise[0]),float_hours_to_vedic_time_equal_day_night_ghati(jd, place, mrise[0]))
    mset = moonset(jd, place)
    print('moonset',float_hours_to_vedic_time(jd, place, mset[0]),float_hours_to_vedic_time_equal_day_night_ghati(jd, place, mset[0]))
    print('next sunrise',float_hours_to_vedic_time(srise[2]+0.999, place),float_hours_to_vedic_time_equal_day_night_ghati(srise[2]+0.999, place))
    exit()
    print('raahu kaalam',trikalam(jd,place,'raahu kaalam'))
    print('yamagandam',trikalam(jd,place,'yamagandam'))
    print('gulikai',trikalam(jd,place,'gulikai'))
    print('durmuhurtam',durmuhurtam(jd, place))
    print('abhijit_muhurta',abhijit_muhurta(jd,place))
    print('gauri choghadiya',gauri_choghadiya(jd, place))
    print('amrit_kaalam',amrit_kaalam(jd,place))
    sv = shiva_vaasa(jd,place)
    print(utils.resource_strings['shiva_vaasa_str']+' '+utils.resource_strings['shiva_vaasa_str'+str(sv[0])],utils.to_dms(sv[1]),utils.resource_strings['ends_at_str'])
    sv = shiva_vaasa(jd,place,method=1)
    print(utils.resource_strings['shiva_vaasa_str']+' '+utils.resource_strings['shiva_vaasa_str'+str(sv[0])],utils.to_dms(sv[1]),utils.resource_strings['ends_at_str'])
    sv = agni_vaasa(jd,place)
    print(utils.resource_strings['agni_vaasa_str']+' '+utils.resource_strings['agni_vaasa_str'+str(sv[0])],utils.to_dms(sv[1]),utils.resource_strings['ends_at_str'])
    print(utils.resource_strings['kali_ahargana_str'],kali_ahargana_days(jd),utils.resource_strings['days_str'])
    print('pushkara_yoga',pushkara_yoga(jd,place))
    print('aadal_yoga',aadal_yoga(jd,place))
    print('vidaal_yoga',vidaal_yoga(jd,place))
    directions = ['east','south','west','north','south_west','north_west','north_east','south_east']
    ds = disha_shool(jd)
    print('disha_shool',utils.resource_strings[directions[ds]+'_str'])
    yv = yogini_vaasa(jd, place)
    print('yogini_vaasa',utils.resource_strings[directions[yv]+'_str'])
    exit()
    y,m,d,birth_time_hrs = utils.jd_to_gregorian(jd); jd_utc = utils.gregorian_to_jd(Date(y,m,d))
    nak = nakshatra(jd, place)
    n_frac = utils.get_fraction(nak[2], nak[3], birth_time_hrs)
    print('nakshatra old',utils.NAKSHATRA_LIST[nak[0]-1],utils.to_dms(nak[2]),utils.to_dms(nak[3]),n_frac)
    nak = nakshatra_new(jd, place)
    n_frac = utils.get_fraction(nak[2], nak[3], birth_time_hrs)
    print('nakshatra new',utils.NAKSHATRA_LIST[nak[0]-1],utils.to_dms(nak[2]),utils.to_dms(nak[3]),n_frac)
    tit = tithi(jd,place)
    print('tithi old',utils.TITHI_LIST[tit[0]-1],utils.to_dms(tit[1]),utils.to_dms(tit[2]),utils.get_fraction(tit[1], tit[2], birth_time_hrs))
    tit = tithi(jd, place)
    print('tithi new',utils.TITHI_LIST[tit[0]-1],utils.to_dms(tit[1]),utils.to_dms(tit[2]),utils.get_fraction(tit[1], tit[2], birth_time_hrs))
    tit = tithi_using_planet_speed(jd,place)
    print('tithi using planet speed',utils.NAKSHATRA_LIST[tit[0]-1],utils.to_dms(tit[1]),utils.to_dms(tit[2]),utils.get_fraction(tit[1], tit[2], birth_time_hrs))
    kt = karaka_tithi(jd, place)
    print('karaka tithi',utils.KARANA_LIST[kt[0]-1],utils.to_dms(kt[1]),utils.to_dms(kt[1]),utils.get_fraction(kt[1], kt[2], birth_time_hrs))
    const.use_planet_speed_for_panchangam_end_timings = False
    yog = yogam_old(jd, place)
    print('yogam',utils.YOGAM_LIST[yog[0]-1],utils.to_dms(yog[1]),utils.to_dms(yog[2]),utils.get_fraction(yog[1], yog[2], birth_time_hrs))
    const.use_planet_speed_for_panchangam_end_timings = True
    yog = yogam(jd, place)
    print('yogam new',utils.YOGAM_LIST[yog[0]-1],utils.to_dms(yog[1]),utils.to_dms(yog[2]),utils.get_fraction(yog[1], yog[2], birth_time_hrs))
    ky = karaka_yogam(jd, place)
    print('karaka yogam',utils.YOGAM_LIST[ky[0]-1],utils.to_dms(ky[1]),utils.to_dms(ky[2]),utils.get_fraction(ky[1], ky[2], birth_time_hrs))
    kr = karana(jd, place)
    print('karanam',utils.KARANA_LIST[kr[0]-1],utils.to_dms(kr[1]),utils.to_dms(kr[2]),utils.get_fraction(kr[1], kr[2], birth_time_hrs))
    print('raasi',raasi(jd, place))
    