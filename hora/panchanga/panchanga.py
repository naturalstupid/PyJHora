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
# Downloaded from https://github.com/naturalstupid/pyhoroscope
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
""" TODO: For western chart - replace Rahu and Ketu with Uranus Neptune and Pluto """
#swe.KETU =  swe.PLUTO  # I've mapped Pluto to Ketu
planet_list = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER,
               swe.VENUS, swe.SATURN,swe.RAHU,swe.KETU]#,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
_sideral_planet_list = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER,
               swe.VENUS, swe.SATURN,swe.RAHU,swe.KETU]#,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
#if const._INCLUDE_URANUS_TO_PLUTO: _sideral_planet_list += [swe.URANUS,swe.NEPTUNE,swe.PLUTO]
_tropical_planet_list = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER,
               swe.VENUS, swe.SATURN,swe.URANUS,swe.NEPTUNE,swe.PLUTO] # Rahu = MEAN_NODE
revati_359_50 = lambda: swe.set_sid_mode(swe.SIDM_USER, 1926892.343164331, 0)
galc_cent_mid_mula = lambda: swe.set_sid_mode(swe.SIDM_USER, 1922011.128853056, 0)
# Hindu sunrise/sunset is calculated w.r.t middle of the sun's disk
# They are geometric, i.e. "true sunrise/set", so refraction is not considered
_rise_flags = swe.BIT_DISC_CENTER + swe.BIT_NO_REFRACTION  # + swe.BIT_GEOCTR_NO_ECL_LAT
#_rise_flags = swe.BIT_HINDU_RISING 

def set_tropical_planets():
    global planet_list
    planet_list = _tropical_planet_list    
def set_sideral_planets():
    global planet_list
    planet_list = _sideral_planet_list
    
#PLANET_NAMES= ['Suriyan', 'Chandran', 'Sevvay','Budhan','Viyaazhan','VeLLi','Sani','Raahu','Kethu','Uranus','Neptune']
_ayanamsa_mode = "Lahiri"
_ayanamsa_value = None
def _ayanamsa_surya_siddhantha_model(jd,as_string=False):
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
    if as_string:
        return utils.to_dms(ayanamsa, as_string,is_lat_long='plong')
    else:
        return ayanamsa
def _calculate_ayanamsa_senthil_from_jd(jd,as_string=False):
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
    if as_string:
        return utils.to_dms(ayanamsa, as_string)
    else:
        return ayanamsa
def get_ayanamsa_value(jd):
    """
        Get ayanamsa value for the julian day number
        @param jd: Julian Day Number
        @return: ayanamsa value - ayanamsa for the day based on the model used. 
    """
    global _ayanamsa_mode,_ayanamsa_value
    key = _ayanamsa_mode.lower()
    if key =='sidm_user' or key =='senthil' or key == 'sundar_ss':
        #print(key,'returning',_ayanamsa_value)
        return _ayanamsa_value
    else:
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        return swe.get_ayanamsa(jd)
def set_ayanamsa_mode(ayanamsa_mode = "KP",ayanamsa_value=None,jd=None):
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
            _ayanamsa_value = _calculate_ayanamsa_senthil_from_jd(jd,as_string=False)
        elif key == "SUNDAR_SS":
            _ayanamsa_value = _ayanamsa_surya_siddhantha_model(jd,as_string=False)
        else:
            swe.set_sid_mode(const.available_ayanamsa_modes[key])
    else:
        warnings.warn("Unsupported Ayanamsa mode:", ayanamsa_mode,"KP Assumed")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    #print("Ayanamsa mode",ayanamsa_mode,'set')
    _ayanamsa_mode = ayanamsa_mode
#set_ayanamsa_mode = lambda: swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
reset_ayanamsa_mode = lambda: swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
""" TODO: Need to make panchanga resource independent """
def read_list_types_from_file(lstTypeFile):
    import os.path
    from os import path
    import codecs
    if not path.exists(lstTypeFile):
        print('Error: List Types File:'+lstTypeFile+' does not exist. Script aborted.')
        exit()
    
    global cal_key_list
    cal_key_list = {}
    with codecs.open(lstTypeFile, encoding='utf-8', mode='r') as fp:
        line_list = fp.read().splitlines()
    fp.close()
    for line in line_list: #  fp:
        if line.replace("\r\n","").replace("\r","").rstrip().lstrip()[0] == '#':
            continue
        splitLine = line.split('=')
        cal_key_list[splitLine[0].strip()]=splitLine[1].strip()
#    print (cal_key_list)
    return cal_key_list       
    
def read_lists_from_file(inpFile):
    import os.path
    from os import path
    import codecs
    global PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST, MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST
    if not path.exists(inpFile):
        print('Error: input file:'+inpFile+' does not exist. Script aborted.')
        exit()
    fp = codecs.open(inpFile, encoding='utf-8', mode='r')
    line = fp.readline().strip().replace('\n','')
    line = line.replace("\r","").rstrip()
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    PLANET_NAMES = line.replace("\r","").rstrip('\n').split(',')
    """ For troipcal mode Rahi and Kethu are excluded, Uranus, Neptune and Pluto are included """
    if const._TROPICAL_MODE:
        PLANET_NAMES = PLANET_NAMES[:7] + PLANET_NAMES[9:]
    line = fp.readline().strip().replace('\n','')
    line = line.replace("\r","").rstrip()
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    NAKSHATRA_LIST = line.replace("\r","").rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    TITHI_LIST = line.replace("\r","").rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    RAASI_LIST = line.replace("\r","").rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    KARANA_LIST = line.replace("\r","").rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    DAYS_LIST = line.rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    PAKSHA_LIST = line.replace("\r","").rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    YOGAM_LIST = line.replace("\r","").rstrip('\n').split(',')

    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    MONTH_LIST = line.replace("\r","").rstrip('\n').split(',')

    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    YEAR_LIST = line.rstrip('\n').split(',')

    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    DHASA_LIST = line.rstrip('\n').split(',')

    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    BHUKTHI_LIST = line.rstrip('\n').split(',')

    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    PLANET_SHORT_NAMES = line.rstrip('\n').split(',')

    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    RAASI_SHORT_LIST = line.rstrip('\n').split(',')
#    exit()
    return [PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST,MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST]    
def get_dhasa_name(planet):
    names = { swe.SURYA: DHASA_LIST[0], swe.CHANDRA: DHASA_LIST[1], swe.KUJA: DHASA_LIST[2],
              swe.BUDHA: DHASA_LIST[3], swe.GURU: DHASA_LIST[4], swe.SUKRA: DHASA_LIST[5],
              swe.SANI: DHASA_LIST[6], swe.RAHU: DHASA_LIST[10], swe.KETU: DHASA_LIST[11], swe.URANUS:DHASA_LIST[7], swe.NEPTUNE:DHASA_LIST[8], swe.PLUTO:DHASA_LIST[9]}
    return names[planet]
def get_bhukthi_name(planet):
    names = { swe.SURYA: BHUKTHI_LIST[0], swe.CHANDRA: BHUKTHI_LIST[1], swe.KUJA: BHUKTHI_LIST[2],
              swe.BUDHA: BHUKTHI_LIST[3], swe.GURU: BHUKTHI_LIST[4], swe.SUKRA: BHUKTHI_LIST[5],
              swe.SANI: BHUKTHI_LIST[6], swe.RAHU: BHUKTHI_LIST[10], swe.KETU: BHUKTHI_LIST[11], swe.URANUS:BHUKTHI_LIST[7], swe.NEPTUNE:BHUKTHI_LIST[8], swe.PLUTO:BHUKTHI_LIST[9]}
    return names[planet]

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
        Computes nirayana (sidereal) longitude of given planet on jd
        Note: This is where the selected/default ayanamsa is adjusted to tropical longitude obtained from swiss ephimeride
        @param jd: Julian Day Number of the date/time
        @param planet: index of the planet 0..8. 0 is Sun, 1 = Moon, 7=Rahu, 8-Kethu
        @return: the sidereal londitude of the planet  
    """
    global _ayanamsa_mode,_ayanamsa_value
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
    longi,flgs = swe.calc_ut(jd, planet, flag = flags)
    reset_ayanamsa_mode()
    return utils.norm360(longi[0]) # degrees

solar_longitude = lambda jd: sidereal_longitude(jd, swe.SUN)
lunar_longitude = lambda jd: sidereal_longitude(jd, swe.MOON)
def sunrise(jd, place,as_string=False):
    """
        Sunrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return sunrise time as julian day number, sunrise time in local time
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    
    city,lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)
    rise = result[1][0]  # julian-day number
    # Convert to local time
    return [rise + tz/24., utils.to_dms((rise - jd_utc) * 24 + tz,as_string)]

def sunset(jd, place,as_string=False):
    """
        Sunset when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return sunset time as julian day number, sunset time in local time 
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    city,lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_SET)
    setting = result[1][0]  # julian-day number
    # Convert to local time
    return [setting + tz/24., utils.to_dms((setting - jd_utc) * 24 + tz,as_string)]

def moonrise(jd, place,as_string=False):
    """
        Moonrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return moonrise time as julian day number, moonise time in local time 
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    city, lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.MOON, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)
    rise = result[1][0]  # julian-day number
    # Convert to local time
    return utils.to_dms((rise - jd_utc) * 24 + tz,as_string)

def moonset(jd, place,as_string=False):
    """
        Moonset when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return moonset time as julian day number, moonset time in local time 
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    # First convert jd to UTC
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    city, lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.MOON, lon, lat, rsmi = _rise_flags + swe.CALC_SET)
    setting = result[1][0]  # julian-day number
    # Convert to local time
    return utils.to_dms((setting - jd_utc) * 24 + tz,as_string)

# Tithi doesn't depend on Ayanamsa
def tithi(jd, place, as_string=False):
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
    paksha = ''
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[0] - tz / 24
    #print('sunrise,jd',rise,jd)
    
    # 2. Find tithi at this JDN
    moon_phase = lunar_phase(rise)
    today = ceil(moon_phase / 12)  
    degrees_left = today * 12 - moon_phase
    
    # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
    solar_long_diff = [ (solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets ]
    relative_motion = [ moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]
    
    # 4. Find end time by 4-point inverse Lagrange interpolation
    y = relative_motion
    x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = utils.inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end -jd) * 24 + tz
    tithi_no = int(today)
        
    answer = [tithi_no, utils.to_dms(ends,as_string)]
    if as_string:
        if tithi_no <15:
            paksha = PAKSHA_LIST[0]
        elif tithi_no > 15 and tithi_no <= 30:
            paksha = PAKSHA_LIST[1]
        answer=paksha + '-'+TITHI_LIST[tithi_no-1]+' '+ utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']
    
    # 5. Check for skipped tithi
    moon_phase_tmrw = lunar_phase(rise + 1)
    tomorrow = ceil(moon_phase_tmrw / 12)
    isSkipped = (tomorrow - today) % 30 > 1
    if isSkipped:
      # interpolate again with same (x,y)
      leap_tithi = today + 1
      tithi_no = int(leap_tithi)
      degrees_left = leap_tithi * 12 - moon_phase
      approx_end = utils.inverse_lagrange(x, y, degrees_left)
      ends = (rise + approx_end -jd) * 24 + place.timezone
      leap_tithi = 1 if today == 30 else leap_tithi
      if as_string:
          if tithi_no <15:
              paksha = PAKSHA_LIST[0]
          elif tithi_no > 15 and tithi_no < 30:
              paksha = PAKSHA_LIST[1]
          answer += paksha + '-'+TITHI_LIST[tithi_no-1]+' '+utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']
      else:
          answer += [tithi_no, utils.to_dms(ends,as_string)]
    return answer

def raasi(jd, place, as_string=False):
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
    city, lat, lon, tz = place
    jd_ut = jd - place.timezone / 24.
    rise = sunrise(jd, place)[0] - tz / 24
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(jd_ut+t, swe.MOON) for t in offsets]
    nirayana_long = longitudes[0]
    raasi_no = int(nirayana_long/360*12)+1
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, raasi_no * 360 / 12)
    ends = (rise - jd + approx_end) * 24 + tz
    #print('jd,jd_ut,rise,approx_end,ends',jd,jd_ut,rise,approx_end,ends)
    answer = [raasi_no, utils.to_dms(ends,as_string)]
    if as_string:
        answer=RAASI_LIST[raasi_no-1]+' '+utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']
    
    # 4. Check for skipped raasi
    raasi_tmrw = ceil(longitudes[-1] * 12 / 360)
    isSkipped = (raasi_tmrw - raasi_no) % 12 > 1
    if isSkipped:
      leap_raasi = raasi_no + 1
      approx_end = utils.inverse_lagrange(offsets, longitudes, leap_raasi * 360 / 12)
      ends = (rise - jd + approx_end) * 24 + tz
      leap_raasi = 1 if raasi_no == 12 else leap_raasi
      raasi_no = int(leap_raasi)
      if as_string:
        answer+=[RAASI_LIST[raasi_no-1], utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']]
      else:
        answer += [raasi_no, utils.to_dms(ends,as_string)]
    #print(' rassi new ends',ends,isSkipped, answer)
    return answer
   
def nakshatra(jd, place, as_string=False):
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
    """ TODO: Not sure whether end time is correct """
    city, lat, lon, tz = place
    jd_ut = jd - place.timezone / 24.
    rise = sunrise(jd, place)[0] - tz / 24
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise+t, swe.MOON) for t in offsets] # Fixed 1.1.0 lunar longitude from sunrise to next sunrise
    nirayana_long = lunar_longitude(jd)#longitudes[0] # Fixed 1.1.0 lunar longitude at JD and NOT at RISE
    nak_no,padam_no,_ = nakshatra_pada(nirayana_long)
    # 3. Find end time by 5-point inverse Lagrange interpolation
    y = utils.unwrap_angles(longitudes)
    x = offsets
    approx_end = utils.inverse_lagrange(x, y, nak_no * 360 / 27)
    ends = (rise - jd + approx_end) * 24 + tz
    answer = [nak_no,padam_no, utils.to_dms(ends,as_string)]
    if as_string:
        answer=NAKSHATRA_LIST[nak_no-1]+' '+cal_key_list['paadham_str']+str(padam_no)+' '+utils.to_dms(ends,as_string)+' '+utils.resource_strings['ends_at_str']
    
    # 4. Check for skipped nakshatra
    nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    isSkipped = (nak_tmrw - nak_no) % 27 > 1
    if isSkipped:
      leap_nak = nak_no + 1
      approx_end = utils.inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
      ends = (rise - jd + approx_end) * 24 + tz
      leap_nak = 1 if nak_no == 27 else leap_nak
      nak_no = int(leap_nak)
      if as_string:
        answer+=NAKSHATRA_LIST[nak_no-1]+' '+cal_key_list['paadham_str']+str(padam_no)+' '+utils.to_dms(ends,as_string)+' '+utils.resource_strings['ends_at_str']
      else:
        answer += [nak_no,padam_no, utils.to_dms(ends,as_string)]
    return answer
   
def _nakshatra_old(jd, place,as_string=False):
    """Current nakshatra as of julian day (jd)
       1 = Asvini, 2 = Bharani, ..., 27 = Revati
    """
    # 1. Find time of sunrise
    jd_ut = jd - place.timezone / 24.
    city, lat, lon, tz = place
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes=[]
    rise = sunrise(jd, place)[0] - tz / 24.  # Sunrise at UT 00:00    
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
    answer = [nak_no,padam_no, utils.to_dms(ends,as_string)]
    if as_string:
        answer=[NAKSHATRA_LIST[nak_no-1]+' '+cal_key_list['paadham_str']+str(padam_no), utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']]
    
    # 4. Check for skipped nakshatra
    nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    isSkipped = (nak_tmrw - nak_no) % 27 > 1
    if isSkipped:
      leap_nak = nak_no + 1
      approx_end = utils.inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
      ends = (rise - jd + approx_end) * 24 + tz
      leap_nak = 1 if nak_no == 27 else leap_nak
      nak_no = int(leap_nak)
      if as_string:
        answer+=NAKSHATRA_LIST[nak_no-1]+' '+cal_key_list['paadham_str']+str(padam_no), utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']
      else:
        answer += [nak_no,padam_no, utils.to_dms(ends,as_string)]
    return answer


def yogam(jd, place,as_string=False):
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
    rise = sunrise(jd, place)[0] - tz / 24.  # Sunrise at UT 00:00
    
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
    answer = [yogam_no, utils.to_dms(ends,as_string)]
    if as_string:
        answer = YOGAM_LIST[yogam_no-1]+' '+utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']
    
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
      if as_string:
          answer += YOGAM_LIST[yogam_no-1]+' '+utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']
      else:
          answer += [yogam_no, utils.to_dms(ends,as_string)]
    
    return answer

def karana(jd, place,as_string=False):
    """
        returns the karanam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return karanam index, karanam ending time, 
          karanam index = [1..60]  1 = Kimstugna, 2 = Bava, ..., 60 = Naga
    """
    # 1. Find time of sunrise
    rise = sunrise(jd, place)[0]
    
    # 2. Find karana at this JDN
    #  solar_long = solar_longitude(rise)
    #  lunar_long = lunar_longitude(rise)
    #  moon_phase = (lunar_long - solar_long) % 360
    moon_phase = lunar_phase(jd)
    today = ceil(moon_phase / 6 )
    degrees_left = today * 6 - moon_phase
    answer = int(today)
    if as_string:
        answer=KARANA_LIST[answer-1] 
    return answer

def vaara(jd, as_string=False):
    """
        Weekday for given Julian day. 
        @param jd: Julian Day Number of the date/time
        @return: day of the date
          0 = Sunday, 1 = Monday,..., 6 = Saturday
    """
    answer = int(ceil(jd + 1) % 7)
    if as_string:
        answer=DAYS_LIST[answer] 
    return answer
  
def _tamil_maadham(date_in,place,as_string=False):
    """
        returns tamil maadham index of the date
        @param date_in: in the datetime format
        NOTE: Does not support BC Dates 
        @return: tamil maadham index [1..12] 1=Chithirai, 12=Panguni
    """
    city, lat, lon, tz = place
    jd = gregorian_to_jd(date_in)
    sun_set = sunset(jd, place)[0] - tz / 24.  # Sunrise at UT 00:00
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
    if as_string:
        return MONTH_LIST[int(month_no)]+'-'+str(day_no)
    else:
        return [month_no, day_no]
  
def maasa(jd, place,as_string=False):
    """
        Returns lunar month and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: indian month index, whether leap month (adhika maasa) or not - boolean
            0 = Chaitra, 2 = Vaisakha, ..., 11 = Phalguna
            True if adhika maasa
    """
    ti = tithi(jd, place,as_string=False)[0]
    critical = sunrise(jd, place)[0]  # - tz/24 ?
    last_new_moon = new_moon(critical, ti, -1)
    next_new_moon = new_moon(critical, ti, +1)
    #  this_solar_month = _raasi(last_new_moon,place,as_string=False)[0]
    #  next_solar_month = _raasi(next_new_moon,place,as_string=False)[0]
    this_solar_month = _raasi(last_new_moon,place,as_string=False)[0]
    next_solar_month = _raasi(next_new_moon,place,as_string=False)[0]
    #  print ('next new moon',next_new_moon,next_solar_month)
    is_leap_month = (this_solar_month == next_solar_month)
    maasa = this_solar_month+1
    if maasa > 12: maasa = (maasa % 12)
    if as_string:
        return [MONTH_LIST[int(maasa-1)], is_leap_month]
    else:
        return [int(maasa), is_leap_month]

# epoch-midnight to given midnight
# Days elapsed since beginning of Kali Yuga
ahargana = lambda jd: jd - 588465.5

def elapsed_year(jd, maasa_index):
    """
        returns Indian era/epoch year indices (kali year number, saka year and vikrama year numbers)
        @param jd: Julian Day Number of the date/time
        @param maasa_index: [1..12] (use panchanga.maasa function to get this) 
        @return kali year number, vikrama year number, saka year number 
    """
    ahar = ahargana(jd)  # or (jd + sunrise(jd, place)[0])
    kali = int((ahar + (4 - maasa_index) * 30) / const.sidereal_year)
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

def _raasi(jd, place, as_string=False):
    """Tithi at sunrise for given date and place. Also returns tithi's end time."""
    city, lat, lon, tz = place
    rise = sunrise(jd, place)[0] - tz / 24
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
    if as_string:
        answer = [RAASI_LIST[raasi_no-1], utils.to_dms(raasi_ends_at,as_string)+' '+cal_key_list['ends_at_str']]
    else:
        answer = [raasi_no, utils.to_dms(raasi_ends_at,as_string)]
    
    return answer

def __raasi(jd,place, as_string=False):
    """Zodiac of given jd. 1 = Mesha, ... 12 = Meena"""
    city, lat, lon, tz = place
    rise = sunrise(jd, place)[0] - tz / 24.  # Sunrise at UT 00:00
    
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
    if as_string:
        answer = [RAASI_LIST[raasi_no-1], utils.to_dms(ends,as_string)+' '+cal_key_list['ends_at_str']]
    else:
        answer = [raasi_no, utils.to_dms(ends,as_string)]
    
    return answer
  
def lunar_phase(jd):
    solar_long = solar_longitude(jd)
    lunar_long = lunar_longitude(jd)
    moon_phase = (lunar_long - solar_long) % 360
    return moon_phase

def samvatsara(jd, maasa_index,as_string=False,north_indian_tradition=False):
    """
        return the year name index for the given julian day number of the date
        @param jd: Julian Day Number of the date/time
        @param maasa_index: [1..12] (use panchanga.maasa function to get this) 
        @param north_indian_tradition: Set to to True
            Note: South Indian year names are off by 14 years compared to North Indian Tradition after Kali Year 4009.
        @return year/samvastara index
          1=Prabhava, 2=Vibhava... 59=Krodhana, 60=Akshaya
    """
    kali_off = 14
    if north_indian_tradition: kali_off = 0
    kali = elapsed_year(jd, maasa_index)[0]
    # Change 14 to 0 for North Indian tradition
    # See the function "get_Jovian_Year_name_south" in pancanga.pl
    if kali >= 4009:    kali = (kali - kali_off) % 60
    samvat = (kali + 27 + int((kali * 211 - 108) / 18000)) % 60
    if as_string:
        samvat = YEAR_LIST[samvat-1]
    return samvat

def ritu(maasa_index):
    """ returns ritu / season index. 
        @param maasa_index: [1..12] (use panchanga.maasa function to get this) 
        @return: ritu index  0 = Vasanta,...,5 = Shishira
    """
    return (maasa_index - 1) // 2

def day_duration(jd, place):
    srise = sunrise(jd, place)[0]  # julian day num
    sset = sunset(jd, place)[0]    # julian day num
    diff = (sset - srise) * 24     # In hours
    return [diff, utils.to_dms(diff)]

# The day duration is divided into 8 parts
# Similarly night duration
def gauri_chogadiya(jd, place,as_string=False):
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
    srise = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    
    end_times = []
    for i in range(1, 9):
      if (as_string):
          end_times.append(utils.to_dms((srise + (i * day_dur) / 8 - jd) * 24 + tz,as_string)+' '+cal_key_list['ends_at_str'])
      else:
          end_times.append(utils.to_dms((srise + (i * day_dur) / 8 - jd) * 24 + tz))
    
    # Night duration = time from today's sunset to tomorrow's sunrise
    srise = swe.rise_trans((jd + 1) - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    night_dur = (srise - sset)
    for i in range(1, 9):
        if(as_string):
            end_times.append(utils.to_dms((sset + (i * night_dur) / 8 - jd) * 24 + tz,as_string)+' '+cal_key_list['ends_at_str'])
        else:
            end_times.append(utils.to_dms((sset + (i * night_dur) / 8 - jd) * 24 + tz))
    
    return end_times

def trikalam(jd, place, option='raahu kaalam',as_string=False):
    """
        Get tri kaalam (Raahu kaalam, yama kandam and Kuligai Kaalam) for the given Julian day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @param option: one of 'raahu kaalam', 'gulikai', 'yamagandam'. Default:'raahu kaalam' 
            Note: One can use separate lambda function for each of these options
            raahu_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'raahu kaalam', as_string=as_string)
            yamaganda_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'yamagandam', as_string=as_string)
            gulikai_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'gulikai',as_string=as_string)
        @return: start and end time of requested tri column - as list e.g. [start_time, end_time]
          Note: Time is returned as 
              degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values 
    """
    city, lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_SET)[1][0]
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
    if as_string:
        start_time = utils.to_dms(start_time,as_string)
        end_time = utils.to_dms(end_time,as_string)+' '+cal_key_list['ends_at_str']
    else:
        start_time = utils.to_dms(start_time,as_string=False)
        end_time = utils.to_dms(end_time,as_string=False)
    
    return [start_time, end_time] # decimal hours to H:M:S

raahu_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'raahu kaalam', as_string=as_string)
yamaganda_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'yamagandam', as_string=as_string)
gulikai_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'gulikai',as_string=as_string)

def durmuhurtam(jd, place,as_string=False):
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
    sset = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_SET)[1][0]
    srise = swe.rise_trans((jd + 1) - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    night_dur = (srise - sset)
    
    # Day = today's sunrise to today's sunset
    srise = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)[1][0]
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
        if (as_string):
            start_times[i] = utils.to_dms(start_times[i],as_string)
            end_times[i]=utils.to_dms(end_times[i],as_string)+' '+cal_key_list['ends_at_str']
        else:
            start_times[i] = utils.to_dms(start_times[i],as_string=False)
            end_times[i] = utils.to_dms(end_times[i],False)
        answer += [start_times[i],end_times[i]]
            
    return answer
#  return [start_times, end_times]  # in decimal hours

def abhijit_muhurta(jd, place,as_string=False):
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
    srise = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi = _rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    
    start_time = srise + 7 / 15 * day_dur
    end_time = srise + 8 / 15 * day_dur
    start_time = (start_time - jd) * 24 + tz
    end_time = (end_time - jd) * 24 + tz
    if (as_string):
        start_time = utils.to_dms(start_time,as_string)
        end_time = utils.to_dms(end_time,as_string)+' '+cal_key_list['ends_at_str']
    else:
        start_time = utils.to_dms(start_time,as_string=False)
        end_time = utils.to_dms(end_time,False)
    # to local time
    return [start_time, end_time]

# 'jd' can be any time: ex, 2015-09-19 14:20 UTC
# today = swe.julday(2015, 9, 19, 14 + 20./60)
def planetary_positions(jd, place,as_string=False):
    """
        Computes instantaneous planetary positions (i.e., which celestial object lies in which constellation)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @return: 2D List of [ [planet index, planet longitude, planet constellation],...]]
            Example: [ [0,87.32148,2],...] - Sun longitude 87.32148, Gemini,...
        Note: Planet list is by default Sun to Kethuand does not include Uranus/Neptune/Pluto
    """
    jd_ut = jd - place.timezone / 24.
    
    positions = []
    #print('planet list',planet_list)
    for planet in planet_list:
      p_id = planet_list.index(planet)
      #print('planet in planetrary positions',planet,p_id,'ketu=',swe.KETU)
      if planet == swe.KETU:
        nirayana_long = ketu(sidereal_longitude(jd_ut, swe.RAHU))
      else: # Ketu
        nirayana_long = sidereal_longitude(jd_ut, planet)
      nak_no,paadha_no,_ = nakshatra_pada(nirayana_long)
      # 12 zodiac signs span 360°, so each one takes 30°
      # 0 = Mesha, 1 = Vrishabha, ..., 11 = Meena
      constellation = int(nirayana_long / 30)
      coordinates = utils.to_dms(nirayana_long-constellation*30,as_string,is_lat_long='plong')
    #    positions.append([planet, constellation, coordinates, nakshatra_pada(nirayana_long)])
      if as_string:
          positions.append([PLANET_NAMES[p_id],RAASI_LIST[constellation]+' '+coordinates+' '+ NAKSHATRA_LIST[nak_no-1]+'-'+cal_key_list['paadham_str']+str(paadha_no)])
      else:
          positions.append([p_id,nirayana_long, constellation])
    
    return positions
def ascendant(jd, place, as_string=False):
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
    nirayana_lagna = swe.houses_ex(jd_utc, lat, lon, flag = flags)[1][0]
    nak_no,paadha_no,_ = nakshatra_pada(nirayana_lagna)
    # 12 zodiac signs span 360°, so each one takes 30°
    # 0 = Mesha, 1 = Vrishabha, ..., 11 = Meena
    constellation = int(nirayana_lagna / 30)
    coordinates = utils.to_dms(nirayana_lagna-constellation*30,as_string,is_lat_long='plong')
    
    reset_ayanamsa_mode()
    if as_string:
        return RAASI_LIST[constellation]+' '+coordinates+' '+NAKSHATRA_LIST[nak_no-1]+'-'+cal_key_list['paadham_str']+str(paadha_no)
    else:
        return [constellation, nirayana_lagna, nak_no, paadha_no]    
def dasavarga_from_long(longitude, sign_division_factor):
    """
        Calculates the dasavarga-sign in which given longitude falls
        @param longitude: longitude of the planet
        @param sign_division_factor: divisional chart index as below. 
          sign_division_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: constellation,longitude within_raasi
            0 = Aries, 1 = Taurus, ..., 11 = Pisces
    """
    if sign_division_factor not in const.division_chart_factors:
        raise ValueError("Wrong sign_division_factor",sign_division_factor,' Valid value:',const.division_chart_factors)
    one_pada = (360.0 / (12 * sign_division_factor))  # There are also 108 navamsas
    one_sign = 12.0 * one_pada    # = 40 degrees exactly
    signs_elapsed = longitude / one_sign
    fraction_left = signs_elapsed % 1
    constellation = int(fraction_left * 12)
    long_in_raasi = (longitude-(constellation*30)) % 30
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

def dhasavarga(jd, place,sign_division_factor, as_string=False):
    """
        Calculate planet positions for a given divisional chart index
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',;atitude,longitude,timezone)
        @param sign_division_factor: divisional chart index as below. 
          sign_division_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: 2D List of planet positions in the following format:
        [ [planet_index,[planet_raasi, planet_longitude],...]
        The planet index is in range ['L',0..8] 'L' is Lagname (first element of the 2D List
    """
    jd_utc = jd - place.timezone / 24.
    positions = []
    for planet in planet_list:
      p_id = planet_list.index(planet)
      if planet != swe.KETU:
        nirayana_long = sidereal_longitude(jd_utc, planet)
      else: # Ketu
        nirayana_long = ketu(sidereal_longitude(jd_utc, swe.RAHU))
      divisional_chart = dasavarga_from_long(nirayana_long,sign_division_factor)
      if as_string:
          positions.append([PLANET_NAMES[p_id],RAASI_LIST[divisional_chart[0]]+' '+utils.to_dms(divisional_chart[1],True,'plong')])
      else:
          positions.append([p_id, divisional_chart])
    return positions
    
def navamsa(jd, place,as_string=False):
  """Calculates navamsa of all planets"""
  jd_utc = jd - place.timezone / 24.

  positions = []
  for planet in planet_list:
    p_id = planet_list.index(planet)
    if planet != swe.KETU:
      nirayana_long = sidereal_longitude(jd_utc, planet)
    else: # Ketu
      nirayana_long = ketu(sidereal_longitude(jd_utc, swe.RAHU))

    if as_string:
        positions.append([PLANET_NAMES[p_id],utils.to_dms(nirayana_long,is_lat_long='plong')+' '+RAASI_LIST[navamsa_from_long(nirayana_long)]])
    else:
        positions.append([[planet,nirayana_long], navamsa_from_long(nirayana_long)])
  return positions

### --- Vimoshatari functions
def next_adhipati(lord):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.adhipati_list.index(lord)
    next_index = (current + 1) % len(const.adhipati_list)
    return const.adhipati_list[next_index]

def nakshatra_position(jdut1):
    """Get the Nakshatra index and degrees traversed at a given JD(UT1) """
    moon = sidereal_longitude(jdut1, swe.MOON)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    nak = int(moon / one_star)    # 0..26
    rem = (moon - nak * one_star) # degrees traversed in given nakshatra

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
        lord = next_adhipati(lord)

    return retval

def vimsottari_bhukti(maha_lord, start_date):
    """Compute all bhuktis of given nakshatra-lord of Mahadasa
    and its start date"""
    lord = maha_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = const.mahadasa[lord] * const.mahadasa[maha_lord] / const.human_life_span_for_dhasa
        start_date += factor * const.sidereal_year
        lord = next_adhipati(lord)

    return retval

# North Indian tradition: dasa-antardasa-pratyantardasa
# South Indian tradition: dasa-bhukti-antara-sukshma
def vimsottari_antara(maha_lord, bhukti_lord, start_date):
    """Compute all antaradasas from given bhukit's start date.
    The bhukti's lord and its lord (mahadasa lord) must be given"""
    lord = bhukti_lord
    retval = Dict()
    for i in range(9):
        retval[lord] = start_date
        factor = const.mahadasa[lord] * (const.mahadasa[maha_lord] / const.human_life_span_for_dhasa)
        factor *= (const.mahadasa[bhukti_lord] / const.human_life_span_for_dhasa)
        start_date += factor * const.sidereal_year
        lord = next_adhipati(lord)

    return retval


def where_occurs(jd, some_dict):
    """Returns minimum key such that some_dict[key] < jd"""
    # It is assumed that the dict is sorted in ascending order
    # i.e. some_dict[i] < some_dict[j]  where i < j
    for key in reversed(some_dict.keys()):
        if some_dict[key] < jd: return key


def compute_antara_from(jd, mahadashas):
    """Returns antaradasha within which given `jd` falls"""
    # Find mahadasa where this JD falls
    i = where_occurs(jd, mahadashas)
    # Compute all bhuktis of that mahadasa
    bhuktis = vimsottari_bhukti(i, mahadashas[i])
    # Find bhukti where this JD falls
    j = where_occurs(jd, bhuktis)
    # JD falls in i-th dasa / j-th bhukti
    # Compute all antaras of that bhukti
    antara = vimsottari_antara(i, j, bhuktis[j])
    return (i, j, antara)

# ---------------------- ALL TESTS ------------------------------
def __adhipati_tests():
    # nakshatra indexes counted from 0
    satabhisha, citta, aslesha = 23, 13, 8
    assert(adhipati(satabhisha) == swe.RAHU)
    assert(const.mahadasa[adhipati(satabhisha)] == 18)
    assert(adhipati(citta) == swe.MARS)
    assert(const.mahadasa[adhipati(citta)] == 7)
    assert(adhipati(aslesha) == swe.MERCURY)
    assert(const.mahadasa[adhipati(aslesha)] == 17)

def get_dhasa_bhukthi(jd, place):
    # jd is julian date with birth time included
    city,lat,long,tz = place
    jdut1 = jd - tz/24
    dashas = vimsottari_mahadasa(jdut1)
    #print('dasha lords',dashas)
    dhasa_bukthi=[]
    for i in dashas:
        #print(' ---------- ' + get_dhasa_name(i) + ' ---------- ')
        bhuktis = vimsottari_bhukti(i, dashas[i])
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
    result = dtm.datetime.fromordinal(int(date))
    result += dtm.timedelta(seconds=86400.0 * _fract(date))
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
  [sunset_hour,sunset_minute,sunset_second] = sunset(jd,place,as_string=False)[1]
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
_dhuma_longitude = lambda jd: (solar_longitude(jd)+133+20.0/60) % 360
_vyatipaata_longitude = lambda jd: (360.0 - _dhuma_longitude(jd))
_parivesha_longitude = lambda jd: (_vyatipaata_longitude(jd)+180.0) % 360
_indrachaapa_longitude = lambda jd: (360.0-_parivesha_longitude(jd))
_upaketu_longitude = lambda jd: (solar_longitude(jd)-30.0)
def solar_upagraha_longitudes(jd,upagraha,divisional_chart_factor=1,as_string=False):
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
        long = eval('_'+upagraha+"_longitude(jd)")
        constellation,coordinates = dasavarga_from_long(long, divisional_chart_factor) #int(long/30)
        if as_string:
            return RAASI_LIST[constellation]+' '+utils.to_dms(coordinates,True,'plong')
        else:
            return [constellation,coordinates]
"""
  Kaala rises at the middle of Sun’s part. In other words, we find the time at the
  middle of Sun’s part and find lagna rising then. That gives Kaala’s longitude.
"""
kaala_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=0,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
""" Mrityu rises at the middle of Mars’s part."""
mrityu_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=2,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
""" Artha Praharaka rises at the middle of Mercury’s part."""
artha_praharaka_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=3,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
""" Yama Ghantaka rises at the middle of Jupiter’s part. """
yama_ghantaka_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=4,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
""" Gulika rises at the middle of Saturn’s part. """
gulika_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=6,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
""" Maandi rises at the beginning of Saturn’s part. """
maandi_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=6,divisional_chart_factor=divisional_chart_factor,upagraha_part='begin',as_string=as_string)

def upagraha_longitude(dob,tob,place,planet_index,divisional_chart_factor=1,upagraha_part='middle',as_string=False):
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
    day_number = vaara(jd_utc, as_string=False)
    srise = sunrise(jd_utc, place, as_string=False)[1]
    sset = sunset(jd_utc, place, as_string=False)[1]
    srise = srise[0]+srise[1]/60.0+srise[2]/3600.0
    sset = sset[0]+sset[1]/60.0+sset[2]/3600.0
    planet_part = const.day_rulers[day_number].index(planet_index)            
    tob_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
    if tob_hrs < srise: # Previous day sunset to today's sunrise
        sset = sunset((jd_utc-1), place, as_string=False)[1]
        sset = sset[0]+sset[1]/60.0+sset[2]/3600.0
        planet_part = const.night_rulers[day_number].index(planet_index)
    if tob_hrs > sset: # today's sunset to next sunrise
        srise = sunrise((jd_utc+1), place, as_string=False)[1]
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
    upagraha_long = ascendant(jd_kaala, place, False)[1]
    constellation,coordinates = dasavarga_from_long(upagraha_long, divisional_chart_factor) #int(upagraha_long / 30)
    #coordinates = utils.to_dms(upagraha_long-constellation*30,as_string,is_lat_long='plong')
    if as_string:
        return RAASI_LIST[constellation]+' '+utils.to_dms(coordinates,True,is_lat_long='plong')
    return [constellation,upagraha_long-constellation*30]
bhava_lagna = lambda jd,place,time_of_birth_in_hours,divisional_chart_factor,as_string=False: special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=1.0,divisional_chart_factor=divisional_chart_factor,as_string=as_string) 
hora_lagna = lambda jd,place,time_of_birth_in_hours,divisional_chart_factor=1,as_string=False: special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=0.5,divisional_chart_factor=divisional_chart_factor,as_string=as_string) 
ghati_lagna = lambda jd,place,time_of_birth_in_hours,divisional_chart_factor=1,as_string=False: special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=1.25,divisional_chart_factor=divisional_chart_factor,as_string=as_string) 
def special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=1.0,divisional_chart_factor=1,as_string=False):
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
    y, m, d, h = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(Date(y, m, d))
    h,m,s = sunrise(jd_utc, place, False)[1]
    sun_rise_hours = utils.from_dms(h,m,s)
    time_diff_mins = (time_of_birth_in_hours-sun_rise_hours)*60
    sun_long = solar_longitude(jd)
    spl_long = (sun_long+(time_diff_mins* lagna_rate_factor)) % 360
    da = dasavarga_from_long(spl_long, divisional_chart_factor)
    if as_string:
        return RAASI_LIST[da[0]]+' '+utils.to_dms(da[1],True,'plong')
    else:
        return da
          
    return spl_sa_long
def sree_lagna(jd,place,divisional_chart_factor=1,as_string=True):
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
    moon_long = lunar_longitude(jd)
    asc_long = ascendant(jd, place, as_string=False)[1]
    reminder = nakshatra_pada(moon_long)[2]
    one_rasi = 360 / 27
    reminder_fraction = reminder * 27
    sree_long = asc_long + reminder_fraction
    constellation,coordinates = dasavarga_from_long(sree_long, divisional_chart_factor)
    if as_string:
        return RAASI_LIST[constellation]+' '+utils.to_dms(coordinates,True,'plong')
    else:
        return constellation,coordinates
def sree_lagna_from_moon_asc_longitudes(moon_longitude,ascendant_longitude,divisional_chart_factor=1,as_string=False):
    moon_long = moon_longitude
    asc_long = ascendant_longitude
    reminder = nakshatra_pada(moon_long)[2]
    one_rasi = 360 / 27
    reminder_fraction = reminder * 27
    sree_long = asc_long + reminder_fraction
    constellation,coordinates = dasavarga_from_long(sree_long, divisional_chart_factor)
    if as_string:
        return RAASI_LIST[constellation]+' '+utils.to_dms(coordinates,True,'plong')
    else:
        return constellation,coordinates
if __name__ == "__main__":
    """
    jd = swe.julday(1967,3,8,17+40.0/60)
    years = 33+1.0/12
    jd_after = jd_to_gregorian(jd+sidereal_year*years)
    print("Sidereal - After",years," years - sun's entry",jd_after)
    print(utils.to_dms(jd_after[3]))
    exit()
    """
    as_string = True
    """
    for year in range(-3101,25000,200):
        jd = swe.julday(year,1,23,12,cal=swe.JUL_CAL)
        ayan = _ayanamsa_surya_siddhantha_model(jd,as_string)
        print(year,ayan)
    exit()
    """
    set_ayanamsa_mode('LAHIRI')
    from hora import utils
    utils.get_resource_lists()
    utils.get_resource_messages()
    #read_lists_from_file(const._LANGUAGE_PATH+'list_values_ta.txt')
    #read_list_types_from_file(const._LANGUAGE_PATH+'msg_strings_ta.txt')
    lat = 13.0389
    lon = 80.2619
    tz = 5.5
    place = Place('Chennai,IN',lat, lon, tz)
    dob = Date(1996,12,7)
    tob = (10,34,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd = swe.julday(dob.year,dob.month,dob.day, time_of_birth_in_hours)
    print(nakshatra(jd, place, as_string))
    print('moon long',lunar_longitude(jd))
    #print(sree_lagna(jd, place))
    #exit()
    print('sun long',solar_longitude(jd))
    as_string = True
    for sign_division_factor in [1,2,3]:
        for lagna_rate_factor in [1.0,0.5,1.25]:
                for lagna_rate_factor in [1,0.5,1.25]:
                    sa = special_ascendant(jd, place, time_of_birth_in_hours, lagna_rate_factor, sign_division_factor, as_string)
                    print(sign_division_factor,lagna_rate_factor,sa)
                exit()
    exit()
