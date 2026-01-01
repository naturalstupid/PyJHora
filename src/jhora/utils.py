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
    utils module
    contains common functions used by various PyJHora modules
"""
import os
import codecs
import warnings
import geocoder
import requests
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
import csv
import numpy as np
import swisseph as swe
from geopy.geocoders import Nominatim
from jhora import const
from jhora.panchanga import drik as drig_panchanga
import json
import datetime
from dateutil import relativedelta

world_cities_dict = {}
google_maps_url = "https://www.google.cl/maps/place/"#+' time zone'
def use_database_for_world_cities(enable_database=False):
    global world_cities_dict
    if enable_database:
        with open(const._world_city_csv_file, 'r', encoding='ISO-8859-1') as file:
            world_cities_dict = {row[1].lower(): idx for idx, row in enumerate(csv.reader(file))}
        const.check_database_for_world_cities = True
    else:
        world_cities_dict = {}
        const.check_database_for_world_cities = False

sort_tuple = lambda tup,tup_index,reverse=False: sorted(tup,key = lambda x: x[tup_index],reverse=reverse)

def save_location_to_database_old(location_data):
    global _world_city_db_df
    print('writing ',location_data,' to ',const._world_city_csv_file)
    _world_city_db_df.loc[len(_world_city_db_df.index)] = location_data
    _world_city_db_df.to_csv(const._world_city_csv_file,mode='w',header=None,index=False)#,quoting=None)
def save_location_to_database(location_data):
    global world_cities_dict
    print('writing ',location_data,' to ',const._world_city_csv_file)
    with open(const._world_city_csv_file, mode='a', newline='', encoding='ISO-8859-1') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(location_data)
    world_cities_dict[location_data[1]] = len(world_cities_dict)
" Flatten a list of lists "
flatten_list = lambda list: [item for sublist in list for item in sublist]
def _get_place_from_ipinfo():
    url = 'http://ipinfo.io/json'
    response = requests.get(url)
    data = json.loads(response.text)
    print('data recd from ipinfo',data)
    place = data['city']+','+data['country']
    latitude,longitude = data['loc'].split(',')
    time_zone_offset = get_place_timezone_offset(latitude,longitude)
    return place,latitude,longitude,time_zone_offset
def get_place_from_user_ip_address():
    """
        function to get place from user's IP address
        @param - None
        @return place,latitude,longitude,time_zone_offset
    """
    g = ''
    try:
        print("Trying to get using IP Address of the user")
        g = geocoder.ip('me') #ipinfo('me')
        #print('g',g,g.city,g.country,g.latlng)
        if g is None or g=='':
            print('Trying using ipinfo website')
            try:
                place,latitude,longitude,time_zone_offset = _get_place_from_ipinfo()
                return place,latitude,longitude,time_zone_offset
            except:
                print('No latitude/longitude provided. Could not guess location from IP Address')
                return []
        else:
            place,country,[latitude,longitude] = g.city,g.country, g.latlng
            place += ','+country
            #print('g',g.city,g.country,g.latlng)
            time_zone_offset = get_place_timezone_offset(latitude,longitude)
            print('Location obtained from IP Address:',place,[latitude,longitude,time_zone_offset])
            return place,latitude,longitude,time_zone_offset
    except:
        print('No latitude/longitude provided. Could not guess location from IP Address')
        return []
def get_elevation(lat = None, long = None):
    '''
        script for returning elevation/altitude in meters from lat, long
        It calls https://api.open-elevation.com/ website to get this information. 
        This will work only until the website offers free api requests.
        the elevation impacts sunrise and sunset timings 
        For example: sunrise is earlier and sunset is later by 1 minute for every 1.5 km of elevation (approx)
        But swiss ephemeris does not show this difference when elevation is passed into geopos argument (V2.10)
    '''
    if lat is None or long is None: return 0.0
    
    query = const._open_elevation_api_url(lat,long) 
    
    # Request with a timeout for slow responses
    r = requests.get(query, timeout = 20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = pd.json_normalize(r.json(), 'results')['elevation'].values[0]
    else: 
        elevation = 0.0
    return elevation
def _validate_data(place,latitude,longitude,time_zone_offset,dob,tob,division_chart_factor):
    country = ''
    if place  is not None and (latitude is None or longitude is None):
        city,latitude,longitude,time_zone_offset = get_location(place)
    if latitude is None or longitude is None:
        place,latitude,longitude,time_zone_offset = get_place_from_user_ip_address()
    if dob is None:
        today = datetime.datetime.today()
        dob = (today.year,today.month,today.day)
        print("Today's Date:",dob,'assumed')
    if tob is None:
        tob = tuple(str(datetime.datetime.now()).split()[1].split(':'))
        print('Current time:',tob,'assumed')
    if division_chart_factor not in const.division_chart_factors:
        str_dvf = ','.join([str(x) for x in const.division_chart_factors])
        w_msg = '\nInvalid value for dhasa varga factor. '+str(division_chart_factor)+ \
        '\nAllowed values '+ str_dvf +'\n' + 'division_chart_factor=1 (for Raasi) is assumed now '
        warnings.warn(w_msg)
        divisional_chart_factor = 1
    return place,latitude,longitude,time_zone_offset,dob,tob,division_chart_factor
def get_location(place_name=None):
    """
        function to get place's latitude, longitude and timezone
        if will make call following functions one by one until location info is obtained
            1. if place_name is none - it will try to get the place from the user's IP address.
            2. If step-1 fails, check if lat/long in world cities database file in data folder
            3. if step-2 fails, try google using _scrap_google_map_for_latlongtz_from_city_with_country()
            4. if step-3 fails, Try OpenStreetMaps using get_location_using_nominatim()
            5. if step-4 fails - return [] empty list
        
        @param place_name: Place name. Example: 'Shillong, India' 'Hoffman Estates,IL,US'
        @return: [place_name,latitude,longitude,time_zone] 
    """
    result = None
    place_found = False
    if place_name is None or place_name.strip()=='':
        result = get_place_from_user_ip_address()
        if result:
            return result
    ' first check if lat/long in world cities db'
    place_index = world_cities_dict.get(place_name.lower())
    #print('place_name,place_name_1,place_index',place_name,place_index)
    if place_index is not None and place_index>=0:
        place_found = True
        #print(place_name,'in the database',place_index)
        with open(const._world_city_csv_file, encoding='ISO-8859-1') as csvfile:
            reader = csv.reader(csvfile)
            for idx, row in enumerate(reader):
                if idx == place_index:
                    city = row[1]
                    _latitude = round(float(row[2]), 4)
                    _longitude = round(float(row[3]), 4)
                    _time_zone = round(float(row[5]), 2)
                    result = [city, _latitude, _longitude, _time_zone]
                    #print("RESULT:",result)
                    return result
    else:
        print(place_name,'not in '+const._world_city_csv_file+'.Trying to get from Google')
        result = _scrap_google_map_for_latlongtz_from_city_with_country(place_name)
        if result  is not None and len(result)==3:
            place_found = True
            #print(place_name,' found from google maps')
            _place_name = place_name
            _latitude = round(result[0],4)
            _longitude = round(result[1],4)
            _time_zone = round(result[2],2)
            result = [place_name,_latitude,_longitude,_time_zone]
            print('google result',result)
            """ TODO: To save in database
            result should be converted to the CSV format in world_cities file
            Country, place, lat, long, timezone string, timezone hours
            from place_name we should extract country and place name
            And somehow we should get timezone string
            """
            if ',' in place_name:
                _city,_country = place_name.split(','); _tz_str = ''
                #print('city,country',_city,_country)
                if _city not in world_cities_dict.keys():
                    #print('saving to database',_city,_country)
                    save_location_to_database([_country,_city,_latitude,_longitude,_tz_str,_time_zone])
        else:
            print('Could not get',place_name,'from google.Trying to get from OpenStreetMaps')
            place_found = False
            result = get_location_using_nominatim(place_name)
            if result:
                place_found = True
                print(place_name,'found in OpenStreetMap')
                [_place_name,_latitude,_longitude,_time_zone] = result
                _arr = place_name.split(','); 
                if len(_arr)>=2:
                    _city = ','.join(_arr[:-1]); _country=_arr[-1];_tz_str=''
                    #print('city,country',_city,_country)
                    if _city not in world_cities_dict.keys():
                        print('saving to database',_city,_country)
                        save_location_to_database([_country,_city,_latitude,_longitude,_tz_str,_time_zone])
    if place_found:
        return result
    return []
def scrap_google_map_for_latlongtz_from_city_with_country(city_with_country):
    """
        function to scrap google maps to get latitude/longitude of a city/country
        @param city_with_country: city name <comma> country name
            Example: Chennai, India
        @return [city,latitude,longitude,time_zone_offset]
    """
    url = google_maps_url+city_with_country
    resp=requests.request(method="GET",url=url)
    r = requests.get(url)
    txt = r.text
    
    find1 = "window.APP_INITIALIZATION_STATE="
    find2 = ";window.APP"
    
    i1 = txt.find(find1)
    i2 = txt.find(find2, i1+1 )
    js = txt[i1+len(find1):i2]
    data = json.loads(js)[0][0][1:3]
    latitude = data[1]
    longitude = data[0]
    timezone_offset = get_place_timezone_offset(latitude, longitude)
    print('city',city_with_country,'lat=',latitude,'long=',longitude,'timezone offset',timezone_offset)
    return city_with_country,latitude,longitude,timezone_offset
def get_location_using_nominatim(place_with_country_code):
    """
        function to get latitude/longitude from city with country code using Nominatim
        requires geopy installed
        @param place_with_country_code: city name <comma> country name
            Example: Chennai, IN
        @return [city,latitude,longitude,time_zone_offset]
    """
    #[city,latitude,longitude,tz_offset]=''
    geolocator = Nominatim(user_agent="Astro") #,format_string="%s, Bangalore")
    while True:
        try:
            #print('try')
            address,(latitude,longitude) = geolocator.geocode("city:" + place_with_country_code, featuretype='city')
            break
        except (RuntimeError, TypeError, NameError):
            #print('except')
            ValueError('City:'+place_with_country_code+' not found in OpenStreetMap')
            address = ''
            break
    if address:    
        #print('address')
        city = address.split(',')[0]
        time_zone_offset = get_place_timezone_offset(latitude, longitude)
        return [city,latitude,longitude,time_zone_offset]
    return None
def _scrap_google_map_for_latlongtz_from_city_with_country(city_with_country):
    url = "https://www.google.cl/maps/place/"+city_with_country#+' time zone'
    try:
        resp=requests.request(method="GET",url=url)
        r = requests.get(url)
        txt = r.text
        
        find1 = "window.APP_INITIALIZATION_STATE="
        find2 = ";window.APP"
        
        i1 = txt.find(find1)
        i2 = txt.find(find2, i1+1 )
        js = txt[i1+len(find1):i2]
        #print('_scrap_google_map_for_latlongtz_from_city_with_country','txt',txt,'js',js)
        data = json.loads(js)[0][0][1:3]
        latitude = data[1]
        longitude = data[0]
        timezone_offset = get_place_timezone_offset(latitude, longitude)
        print('city',city_with_country,'lat=',latitude,'long=',longitude,'timezone offset',timezone_offset)
        return latitude,longitude,timezone_offset
    except Exception as e: 
        print(e)
        warnings.warn("Unable to get location from Google Map Scrap. Aborted")
        return []
def _get_timezone_from_pytz(timezone_str_from_geocoder):
    print("Trying pytz to get timezone value")
    from pytz import timezone
    tz = datetime.datetime.now(timezone(timezone_str_from_geocoder)).utcoffset().total_seconds()/60/60
    return tz
def get_place_timezone_offset(latitude, longitude):
    """
        This can be used when latitude/longitude are known but not the time zone offset of the place.
        This is an internal function that returns a location's time zone offset from UTC in minutes - using latitude/longitude of the place.
        @param latitude: latitude of the place
        @param longitude: longitude of the place
        @return [city,latitude,longitude,time_zone_offset]
    """
    try:
        tf = TimezoneFinder()
        today = datetime.datetime.now()
        tz_target = timezone(tf.timezone_at(lng=longitude, lat=latitude))
        # ATTENTION: tz_target could be None! handle error case
        today_target = tz_target.localize(today)
        today_utc = utc.localize(today)
        tz_offset = (today_utc - today_target).total_seconds() / 3600.0 # in hours
        #print('timezone offset',tz_offset)
        return tz_offset
    except Exception as err:        
        print('Error in get_place_timezone_offset',err)
        print('WARNING: Time Zone returned as default +5.0. Need to change it')
        return 5.0
def get_house_to_planet_dict_from_planet_to_house_dict(planet_to_house_dict):
    """
        function to get house_to_planet list from planet_to_house dictionary 
        @param planet_to_house_dict: Format {planet_id : raasi_number, ....}
                Example: {0:0, 1:1,2:1,...} Sun in Aries, Moon in Tarus, Mars in Gemini etc
        @return: house_to_planet list - in the format ['0','1/2',...] Aries has Sun, Tarus has Moon/Mars etc
    """
    h_to_p = ['' for h in range(12)]
    for p,h in planet_to_house_dict.items():
        h_to_p[h] += str(p) + '/'
    h_to_p = [p[:-1] for p in h_to_p]
    return h_to_p
def get_planet_to_house_dict_from_chart(house_to_planet_list):
    """
        function to get planet_to_house dictionary from house_to_planet list  
        @param house_to_planet list - in the format ['0','1/2',...] Aries has Sun, Tarus has Moon/Mars etc
                'L' is used for Lagna
        @return: house_to_planet_list: 
                Format {planet_id : raasi_number, ....}
                Example: {0:0, 1:1,2:1,...} Sun in Aries, Moon in Tarus, Mars in Gemini etc
                Last element will be 'L' for Lagna
    """
    p_to_h = {p:h for p in [*range(9)]+[const._ascendant_symbol] for h,planets in enumerate(house_to_planet_list) if str(p) in planets }
    return p_to_h
def get_planet_house_dictionary_from_planet_positions(planet_positions):
    """ 
        Get Planet_to_House Dictionary {p:h}  from Planet_Positions {p:(h,long)}
        @param planet_positions: Format: {planet_index:(raasi_index,planet_longitude_in_the_raasi),...
        @return: planet_to_house_dictionary in the format {planet_index:raasi_index,...} 
    """ 
    p_to_h = {p:h for p,(h,_) in planet_positions}
    return p_to_h
def get_house_planet_list_from_planet_positions(planet_positions):
    """
        to convert from the format [planet,(house,planet_longitude,...]
        into a dict of {house_1:planet_1/planet_2,house_2:Lagnam/planet_2,....}
        @param planet_positions: Format: {planet_index:(raasi_index,planet_longitude_in_the_raasi),...
        @return: house_to_planet list - in the format ['0','1/2',...] Aries has Sun, Tarus has Moon/Mars etc
    """
    h_to_p = ['' for h in range(12)] 
    for sublist in planet_positions:
        p = sublist[0]
        h = sublist[1][0]
        h_to_p[h] += str(p) + '/'
    h_to_p = [x[:-1] for x in h_to_p]
    return h_to_p
def set_ephemeris_data_path(data_path=const._ephe_path):
    swe.set_ephe_path(data_path)
def set_language(language=const._DEFAULT_LANGUAGE):
    global resource_strings
    #print('language',language)
    if language in const.available_languages.values():
        #print('default language set to',language)
        const._DEFAULT_LANGUAGE = language
        language_list_file = const._LANGUAGE_PATH+const._DEFAULT_LANGUAGE_LIST_STR+language+'.txt'
        #print('language_list_file',language_list_file)
        language_message_file = const._LANGUAGE_PATH+const._DEFAULT_LANGUAGE_MSG_STR+language+'.txt'
        
        get_resource_lists(language_list_file)
        resource_strings = get_resource_messages(language_message_file=language_message_file)
def _read_resource_messages_from_file(message_file):
    if not os.path.exists(message_file):
        print('Error: List Types File:'+message_file+' does not exist. Script aborted.')
        exit()
    cal_key_list = {}
    with codecs.open(message_file, encoding='utf-8', mode='r') as fp:
        line_list = fp.read().splitlines()
    fp.close()
    for line in line_list: #  fp:
        if line.replace("\r\n","").replace("\r","").rstrip().lstrip()[0] == '#':
            continue
        splitLine = line.split('=')
        cal_key_list[splitLine[0].strip()]=splitLine[1].strip()
    #print ('length of messages',len(cal_key_list))
    return cal_key_list       
def get_resource_messages(language_message_file=const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_MSG_STR + const._DEFAULT_LANGUAGE + '.txt'):
    """
        Retrieve message strings from language specific message resource file
        @param param:language_message_file -language specific message resource file name
            Default: const._LANGUAGE_PATH + 'msg_strings_' + const._DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/msg_strings_en.txt
        @return: dictionary of message keys with language specific values
    """
    res = _read_resource_messages_from_file(language_message_file)
    return res
resource_strings = get_resource_messages(const._LANGUAGE_PATH+const._DEFAULT_LANGUAGE_MSG_STR+const._DEFAULT_LANGUAGE+'.txt')
def _read_resource_lists_from_file(language_list_file):
    import sys,os
    module = sys.modules[__name__]
    file_path = language_list_file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    #print('_read_resource_lists_from_file')
    with open(file_path, 'r',encoding='utf-8') as file: # V4.5.0
        for line in file:
            line = line.strip()
            if line.startswith("###"):
                continue
            elif "=" in line:
                var_name, var_value = line.split("=")
                var_name = var_name.strip()
                var_value = var_value.split(',')
                setattr(module, var_name, var_value)
                #print('length of',var_name,len(var_value))
def get_resource_lists(language_list_file=const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_LIST_STR + const._DEFAULT_LANGUAGE + '.txt'):
    """
        Retrieve resource list from language specific resource list file
        list values in resource language are read and returned
        @param param:language_message_file -language specific message resource file name
            Default: _DEFAULT_LANGUAGE_LIST_FILE = _LANGUAGE_PATH + 'list_values_' + _DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/list_values_en.txt
        @return: [PLANET_NAMES,NAKSHATRA_LIST,NAKSHATRA_SHORT_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,
                 YOGAM_LIST,MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST,
                 SHADVARGAMSA_NAMES,SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES]
    """
    _read_resource_lists_from_file(language_list_file)
# Convert 23d 30' 30" to 23.508333 degrees
from_dms = lambda degs, mins, secs: degs + mins/60 + secs/3600
from_dms_to_str = lambda dms_list: str(dms_list[0])+const._degree_symbol + str(dms_list[1])+const._minute_symbol + str(dms_list[2])+const._second_symbol
def from_dms_str_to_dms(dms_str):
    if '+1' in dms_str:
        dmsh = 24
    elif '-1' in dms_str:
        dmsh = -24
    else:
        dmsh = 0
    dms = dms_str.replace('(+1)','').replace('(-1)','').replace(' AM','').replace(' PM','').split(':')
    return dmsh+int(dms[0]),int(dms[1]),int(dms[2])
def from_dms_str_to_degrees(dms_str):
    dms = from_dms_str_to_dms(dms_str)
    return dms[0]+dms[1]/60.+dms[2]/3600.
# the inverse
def to_dms_prec(deg):
  """
      convert float degrees to (int)degrees, (int) minutes, (float) seconds tuple
  """
  d = int(deg)
  mins = (deg - d) * 60
  m = int(mins)
  s = round((mins - m) * 60, 2) # changed from 6 digit precision in 2.0.3
  return [d, m, s]

def to_dms(deg,as_string=True, is_lat_long=None,round_seconds_to_digits=None,round_to_minutes=None,
           use_24hour_format=None):
    """
        convert float degrees to (int)degrees, (int) minutes, (int) seconds tuple
        @param deg: degrees as float
        @param as_string: True - output will be single string with degree symbols
                          False - output will be tuple (int)degrees, (int) minutes, (float) seconds tuple
        @param is_lat_long: works with as_string=True
                            = plong - degree symbol shown
                            = lat  - N / S symbol is shown for degrees
                            = long - E / W symbol is shown for degrees
        @return: degrees/minutes/seconds as string or tuple depending on as_string=True and is_lat_long values
    """
    if use_24hour_format is None: use_24hour_format = const.use_24hour_format_in_to_dms
    sep = ':'
    am = " AM"
    pm = " PM"
    ampm= am
    degree_symbol = const._degree_symbol 
    minute_symbol = const._minute_symbol
    second_symbol = const._second_symbol
    next_day = ''
    d = int(deg)
    mins = (deg - d) * 60
    if round_to_minutes:
        m = int(round(mins,0))
    else:
        m = int(mins)
    ss = (mins-m)*60
    s = round(ss,round_seconds_to_digits) # V2.3.1 int changed to round
    #"""
    if (is_lat_long is None):
        if d > 23:
            q = d // 24
            d = d % 24 #d -= 24
            next_day = ' (+'+str(q)+')' if q>0 else ''
        elif d < 0:
            q = abs(d) // 24 + 1# V4.2.7
            d = abs(d) % 24
            m = abs(m)
            s = abs(s)
            next_day = ' (-'+str(q)+')' if q>0 else '' # V4.2.7
    #      print('d=',d)
    #"""
    if d >= 12:
        ampm = pm
    if s==60:
        m += 1
        s = 0
    if m==60:
        d += 1
        m = 0
    if round_to_minutes:
        answer = [d,m]
    else:
        answer = [d, m, s]
    if use_24hour_format: ampm = ''
    if as_string or is_lat_long  is not None:
        if is_lat_long=='plong':
            answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol+" "+str(abs(s))+second_symbol
            if round_to_minutes:
                answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol
        elif is_lat_long=='lat':
            answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol+" "+str(abs(s))+second_symbol
            if round_to_minutes:
                answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol
            if d > 0: answer += ' N'
            else: answer +=' S' 
        elif is_lat_long=='long':
            answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol+" "+str(abs(s))+second_symbol
            if round_to_minutes:
                answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol
            if d > 0: answer += ' E'
            else: answer +=' W' 
        else: ## as_string = =True
            answer= str(d).zfill(2)+ sep +str(m).zfill(2)+ sep +str(s).zfill(2)+ampm+next_day
            if round_to_minutes:
                answer = str(d).zfill(2)+ sep +str(m).zfill(2)+ampm+next_day # V4.4.0
    return answer
def _to_dms_old(deg):
  d, m, s = to_dms_prec(deg)
  return [d, m, int(s)]
def normalize_angle(angle, start=0):
    """
    Normalize angle to be within the range from start to start + 360 degrees.
    """
    while angle >= start + 360:
        angle -= 360
    while angle < start:
        angle += 360
    return angle
def extend_angle_range(angles, target):
    """
    Extend angles to cover a wider range if needed for interpolation.
    """
    extended_angles = angles[:]
    while max(extended_angles) - min(extended_angles) < target:
        extended_angles = extended_angles + [angle + 360 for angle in angles]
    return extended_angles

def unwrap_angles(angles):
    """
    Normalize angles to handle circular continuity.
    For example, if angles are [340, 350, 10, 20], it converts them to [340, 350, 370, 380].
    """
    result = [angles[0]]
    for i in range(1, len(angles)):
        angle = angles[i]
        if angle < result[i-1]:  # Detecting the wrap-around point
            angle += 360
        result.append(angle)
    return result

def unwrap_angles_old(angles):
  """
      Add 360 to those elements in the input list so that all elements are sorted in ascending order.
  """
  result = angles
  for i in range(1, len(angles)):
    if result[i] < result[i-1]: result[i] += 360

  assert(result == sorted(result))
  return result

# Make angle lie between [-180, 180) instead of [0, 360)
norm180 = lambda angle: (angle - 360) if angle >= 180 else angle;

# Make angle lie between [0, 360)
norm360 = lambda angle: angle % 360

def _function(point):
    swe.set_sid_mode(swe.SIDM_USER, point, 0.0)
    #swe.set_sid_mode(swe.SIDM_LAHIRI)
    # Place Revati at 359°50'
    #fval = norm180(swe.fixstar_ut("Revati", point, flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0]) - ((359 + 49/60 + 59/3600) - 360)
    # Place Revati at 0°0'0"
    #fval = norm180(swe.fixstar_ut("Revati", point, flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0])
    # Place Citra at 180°
    fval = swe.fixstar_ut("Citra", point, flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0] - (180)
    # Place Pushya (delta Cancri) at 106°
    # fval = swe.fixstar_ut(",deCnc", point, flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0] - (106)
    return fval

def _bisection_search(func, start, stop):
  left = start
  right = stop
  epsilon = 5E-10   # Anything better than this puts the loop below infinite

  while True:
    middle = (left + right) / 2
    midval =  func(middle)
    rtval = func(right)
    if midval * rtval >= 0:
      right = middle
    else:
      left = middle

    if (right - left) <= epsilon: break

  return (right + left) / 2

def inverse_lagrange(x, y, ya):
  """Given two lists x and y, find the value of x = xa when y = ya, i.e., f(xa) = ya"""
  assert(len(x) == len(y))
  total = 0
  for i in range(len(x)):
    numer = 1
    denom = 1
    for j in range(len(x)):
      if j != i:
        numer *= (ya - y[j])
        denom *= (y[i] - y[j])

    total += numer * x[i] / denom

  return total
def newton_polynomial(x_data, y_data, x):
    """
    x_data: data points at x
    y_data: data points at y
    x: evaluation point(s)
    """
    def _poly_newton_coefficient(x, y):
        """
        x: list or np array contanining x data points
        y: list or np array contanining y data points
        """
    
        m = len(x)
    
        x = np.copy(x)
        a = np.copy(y)
        for k in range(1, m):
            a[k:m] = (a[k:m] - a[k - 1])/(x[k:m] - x[k - 1])
    
        return a

    a = _poly_newton_coefficient(x_data, y_data)
    n = len(x_data) - 1  # Degree of polynomial
    p = a[n]

    for k in range(1, n + 1):
        p = a[n - k] + (x - x_data[n - k])*p

    return p
def julian_day_utc(julian_day,place):
     return julian_day - (place.timezone / 24.)
def julian_day_number_new(date_of_birth_as_tuple,time_of_birth_as_tuple):
    y,m,d = date_of_birth_as_tuple
    h,mm,s = time_of_birth_as_tuple
    jdn = d + int((153*m+2)/5) + 365*y + int(y/4) - int(y/100) + int(y/400) - 32045
    jdt =  h + mm/60 + s/3600
    jd = jdn+(jdt-12)/24,3
    return jd
def julian_day_number(date_of_birth_as_tuple,time_of_birth_as_tuple):
    """
        return julian day number for give Date of birth and time of birth as tuples
        @param date_of_birth_as_tuple: Date of birth as tuple. e.g. (2000,1,1)
            Note: For BC Dates use negative year e.g. (-3114,1,1) means 1-Jan of 3114 BC
            Note: There is no 0 BC or 0 AD so avoid Zero year
        @param time_of_birth_as_tuple: time of birth as tuple e.g. (18,0,30)
        @return julian day number 
    """
    tob_in_hours = time_of_birth_as_tuple[0]+time_of_birth_as_tuple[1]/60.0+time_of_birth_as_tuple[2]/3600.0
    jd = swe.julday(date_of_birth_as_tuple[0],date_of_birth_as_tuple[1],date_of_birth_as_tuple[2],tob_in_hours)
    return jd
# Julian Day number as on (year, month, day) at 00:00 UTC
gregorian_to_jd = lambda date: swe.julday(date.year, date.month, date.day, 0.0)
jd_to_gregorian = lambda jd: swe.revjul(jd, swe.GREG_CAL)   # returns (y, m, d, fh
def jd_to_local(jd,place):
    from jhora.panchanga import drik
    y, m, d,_  = jd_to_gregorian(jd)
    jd_utc = gregorian_to_jd(drik.Date(y, m, d))
    fhl = (jd - jd_utc) * 24 + place.timezone
    return y,m,d,fhl
def deeptaamsa_range_of_planet(planet,planet_longitude_within_raasi):
    """
        get deeptaaamsa range of the planet
        @param planet: the index of the planet 0 for Sun, 1 for moon, ... 7 for Rahu and 8 for Ketu
        @param planet_longitude_within_raasi: longitude of the planet within the raasi (0.0 to 30.0 degrees)
        @return: deeptaamsa range of the planet as a tuple (deeptaamsa_minimum, deeptaamsa_maximum) 
    """
    return (planet_longitude_within_raasi-const.deeptaamsa_of_planets[planet],
            const.deeptaamsa_of_planets[planet]+planet_longitude_within_raasi) 

def local_time_to_jdut1(year, month, day, hour = 0, minutes = 0, seconds = 0, timezone = 0.0):
  """Converts local time to JD(UT1)"""
  y, m, d, h, mnt, s = swe.utc_time_zone(year, month, day, hour, minutes, seconds, timezone)
  # BUG in pyswisseph: replace 0 by s
  jd_et, jd_ut1 = swe.utc_to_jd(y, m, d, h, mnt, 0, flag = swe.GREG_CAL)
  return jd_ut1
def _convert_to_tamil_date_and_time(panchanga_date,time_of_day_in_hours,place=None):
    #print('before',panchanga_date,time_of_day_in_hours)
    extra_days = 0
    sign = 1
    if time_of_day_in_hours < 0:
        extra_days = int(abs(time_of_day_in_hours/24))+1
        sign = -1
        #print(extra_days, sign)
    elif time_of_day_in_hours > 24:
        extra_days = int(abs(time_of_day_in_hours/24))
        sign = 1
    time_of_day_in_hours += - sign * extra_days*24
    #print('extra_days, sign',extra_days, sign,'time_of_day_in_hours',time_of_day_in_hours)
    #print('panchanga data before',panchanga_date)
    if extra_days !=0:
        panchanga_date = next_panchanga_day(panchanga_date, add_days=sign*extra_days)
    #print('panchanga data after',panchanga_date)
    if place  is not None: # if solar time > sunset time move to next day
        jd = gregorian_to_jd(panchanga_date)
        sunset_jd = drig_panchanga.sunset(jd, place)[0] - (place.timezone/24.)
        sunset_time = from_dms_str_to_degrees(drig_panchanga.sunset(sunset_jd,place)[1])
        if sunset_time < time_of_day_in_hours:
            new_panchanga_date = next_panchanga_day(panchanga_date, add_days=1)
            #print(panchanga_date,'sunset_time < solar_hour1',sunset_time,time_of_day_in_hours,'new_panchanga_date',new_panchanga_date)
            panchanga_date = new_panchanga_date
    #print('panchanga data returned',panchanga_date)
    return panchanga_date,time_of_day_in_hours
def previous_panchanga_day(panchanga_date,minus_days=1):
    np_date = np.datetime64(panchanga_date)
    prev_date = np_date - np.timedelta64(minus_days,"D")
    p_date_str = np.datetime_as_string(prev_date).split('-')
    if len(p_date_str) == 4:
        p_date = drig_panchanga.Date(-int(p_date_str[1]),int(p_date_str[2]),int(p_date_str[3]))
    else:
        p_date = drig_panchanga.Date(int(p_date_str[0]),int(p_date_str[1]),int(p_date_str[2]))
    return p_date 
def next_panchanga_day(panchanga_date,add_days=1):
    np_date = np.datetime64(panchanga_date)
    add_days_int = int(add_days)
    prev_date = np_date + np.timedelta64(int(add_days_int),"D")
    p_date_str = np.datetime_as_string(prev_date).split('-')
    #print('np_date',np_date,'add_days_int',add_days_int,'prev_date',prev_date,'p_date_str',p_date_str)
    if len(p_date_str) == 4:
        p_date = drig_panchanga.Date(-int(p_date_str[1]),int(p_date_str[2]),int(p_date_str[3]))
    else:
        p_date = drig_panchanga.Date(int(p_date_str[0]),int(p_date_str[1]),int(p_date_str[2]))
    return p_date 
def panchanga_date_diff(panchanga_date1,panchanga_date2):
    npdate1 = np.datetime64(panchanga_date1) ; npdate2 = np.datetime64(panchanga_date2)
    days_diff = (npdate2-npdate1)/np.timedelta64(1,"D")
    years_diff,days_diff = divmod(days_diff,const.sidereal_year)
    months_diff,days_diff = divmod(days_diff,(const.sidereal_year/12))
    days_diff = round(days_diff,0)
    return int(years_diff),int(months_diff),int(days_diff)
def panchanga_time_delta(panchanga_date1, panchanga_date2):#,**kwargs=None):
    np_date1 = np.datetime64(panchanga_date1)
    np_date2 = np.datetime64(panchanga_date2)
    diff_days = (np_date1-np_date2)/np.timedelta64(1,"D")
    return diff_days
def panchanga_date_to_tuple(panchanga_date): #V2.3.0
    return panchanga_date[0],panchanga_date[1],panchanga_date[2]
def date_diff_in_years_months_days(start_date_str,end_date_str,date_format_str='%Y-%m%-d'):
    start_date = datetime.datetime.strptime(start_date_str,date_format_str)
    end_date = datetime.datetime.strptime(end_date_str,date_format_str)
    delta = relativedelta.relativedelta(end_date, start_date)
    return delta.years,delta.months, delta.days
def get_dob_years_months_60hrs_from_today(dob,tob):
    jd_dob = julian_day_number(dob, tob)
    current_date_str,_ = datetime.datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    yt,mt,dt = map(int,current_date_str.split(','))
    jd_now = julian_day_number((yt,mt,dt), tob)
    if jd_now > jd_dob:
        years = int((jd_now-jd_dob)/const.sidereal_year)
        jdm = (jd_now-jd_dob) % const.sidereal_year
        months = int(jdm/30)
        jdh = jdm % 30
        _60hrs = int(jdh/2.5)
        return years+1,months+1,_60hrs
    else:
        return 1,1,1
def closest_elements(arr1, arr2):
    """
        Returns closest elements between arr1 and arr2
        Note: It assumes no two elements within an array are identical
    """
    result = []
    for a1 in arr1:
        for a2 in arr2:
            if a1 != a2:
                if a1 > a2:
                    result.append([a1, a2, a1-a2])
                else:
                    result.append([a1, a2, a2-a1])
    return sorted(result, key=lambda i:i[-1])[0][:2]
def _solar_mean_motion_since_1900(days_since_1900):
    """ Not working """
    i_d = int(days_since_1900)
    f_d = days_since_1900-i_d
    i_d_s = str(i_d) ; l = len(i_d_s)
    for i,c in enumerate(i_d_s):
        c1 = int(c)
        if c1!=0:
            lng = const.mean_solar_daily_motions_table_from_1900[c1-1][i]
            #print(i,c,'row',c1-1,'column',10**i,lng)
def udhayadhi_nazhikai(jd,place):
    import math
    _,_,_,birth_time_hrs = jd_to_gregorian(jd)
    sunrise_time_in_float_hours = drig_panchanga.sunrise(jd, place)[0]
    """ TODO If birthtime < sunrise then it is from previous day sun rise """
    time_diff = birth_time_hrs - sunrise_time_in_float_hours
    if birth_time_hrs < sunrise_time_in_float_hours:
        sunrise_time_in_float_hours = drig_panchanga.sunrise(jd-1, place)[0]
        #print('birth time less than sunrise - previous day sunrise considered',sunrise_time_in_float_hours)
        time_diff = 24.0+birth_time_hrs-sunrise_time_in_float_hours
    hours,minutes,seconds = to_dms(time_diff,as_string=False)
    tharparai1 = (int(hours))*9000+int(minutes)*150+int(seconds)
    naazhigai = math.floor(tharparai1/3600)
    vinadigal = math.floor( (tharparai1-(naazhigai*3600))/60 )
    tharparai = math.floor(tharparai1 - naazhigai*3600 - vinadigal*60)
    return [str(naazhigai)+':'+str(vinadigal)+':'+str(tharparai),tharparai1/3600.0]
closest_element_from_list = lambda list_array, value: list_array[min(range(len(list_array)), key = lambda i: abs(list_array[i]-value))]
def get_fraction(start_time_hrs,end_time_hrs,birth_time_hrs):
    tl = end_time_hrs - start_time_hrs
    if start_time_hrs < 0:
        tl = int(abs(start_time_hrs)/24+1)*24 + end_time_hrs - abs(start_time_hrs)
    tf = min((end_time_hrs-birth_time_hrs)/tl,1.0)
    #print(start_time_hrs,end_time_hrs,birth_time_hrs,'duration',tl,'frac',tf)
    #print('birth time',birth_time_hrs, 'tithi start',tithi_start_time_hrs,'tithi end',tithi_end_time_hrs,'tithi duration',tl,'tithi fraction',tf)
    return tf
def get_fraction_old(start_time_hrs,end_time_hrs,birth_time_hrs):
    tl = end_time_hrs - start_time_hrs
    if start_time_hrs < 0:
        tl = 24 + end_time_hrs - abs(start_time_hrs)
        print('duration',tl)
    tf = (end_time_hrs-birth_time_hrs)/tl
    #print('birth time',birth_time_hrs, 'tithi start',tithi_start_time_hrs,'tithi end',tithi_end_time_hrs,'tithi duration',tl,'tithi fraction',tf)
    return tf

count_stars = lambda from_star,to_star,dir=1,total=27: ((to_star + total - from_star) % total)+1 if dir==1 else ((from_star + total - to_star) % total)+1
count_rasis = lambda from_rasi,to_rasi,dir=1,total=12: ((to_rasi + total - from_rasi) % total)+1 if dir==1 else ((from_rasi + total - to_rasi) % total)+1
def parivritti_even_reverse(dcf,dirn=1):
    """
        generates parivritti tuple (rasi_sign, hora_portion_of_varga, varga_sign)
        in this method for varga factor = 2 (hora chart)
            for the first sign hora portion increases from 0 to 1 (varga factor - 1)
            for the next sign hora portion decreases from 1 to 0
            for rasi = 0 the tuples are (0,0,0), (0,1,1) (the middle hora element 0 and 1)
            for next rasi = 1 (1,1,2), (1,0,3) (the middle hora element 1 and 0)
        in this method for varga factor = 3 (drekkana chart)
            for the first sign hora portion increases from 0 to 2
            for the next sign hora portion decreases from 2 to 0
            for rasi = 0 the tuples are (0,0,0), (0,1,1),(0,2,2) (the middle hora element increase 0,1,2)
            for next rasi = 1 (1,2,3), (1,1,4), (1,0,5) (the middle hora element decrease 2,1,0)
        @param varga divisional chart factor: 2=>Hora, 3=Drekkana etc
        @return parivritti even reverse tuple 
    """
    pc = []
    hs = 0
    for r in range(0,12,2):
        for h in range(0,dcf):
            pc.append((r,h,hs)); hs = (hs+dirn)%12
        r += 1
        for h in range(dcf-1,-1,-1):
            pc.append((r,h,hs)); hs = (hs+dirn)%12
    return pc
def parivritti_cyclic(dcf,dirn=1):
    """
        generates parivritti tuple (rasi_sign, hora_portion_of_varga, varga_sign)
        In this method each hora portion gets zodiac order of the rasis
        for rasi_sign = 0, first hora portion gets rasi=0, next hora portion gets rasi=1 and so on
        For hora chart 
            (0-15 deg) of rasi sign = 0(Ar), 15-30deg of Ar  gets next rasi = 1 (Ta) = > (0,1), 
            Now for rasi sign = 2 (Gemini) 0-15 deg is Ge (2) and 15-30 deg is Cn (3) => (2,3)
            And so on (0,1), (2,3)..
            Similarly for drekkana (0,1,2), (2,3,4), (5,6,7), (7,8,9), (9,10,11), (0,1,2)... 
        @param varga divisional chart factor: 2=>Hora, 3=Drekkana etc
        @return parivritti cyclical tuple 
    """
    pc = []
    hs = 0
    for _ in range(12):
        t = tuple()
        for _ in range(dcf):
            t += (hs%12,); hs = (hs+dirn)%12
        pc.append(t)
    return pc
def parivritti_alternate(dcf,dirn=1):
    """
        Generates alternate parivritti tuple. Used for Somanatha method
        Odd Rasis get increasing rasis from Ar. Even rasis get decreasing rasis from Pi
        For Hora Ar = (Ar,Ta), Ta = (Pi, Aq), Ge = (Ge,Cn), Cn = (Cp,Sg) and so on
        @param varga divisional chart factor: 2=>Hora, 3=Drekkana etc
        @return parivritti alternate tuple 
    """
    pc = []
    hs1 = 0; hs2 = 11
    for _ in range(0,12,2):
        t1 = tuple(); t2 = tuple()
        for _ in range(dcf):
            t1 += (hs1%12,); hs1 = (hs1+dirn)%12
            t2 += (hs2%12,); hs2 = (hs2-dirn)%12
        pc.append(t1); pc.append(t2)
    return pc
    
def __varga_non_cyclic(dcf,base_rasi=0,start_sign_variation=1,count_from_end_of_sign=False):
    """
        STILL UNDER EXPERIMENT
        generates varga non_cyclic varga rasi tuple (rasi_sign, hora_portion_of_varga, varga_sign)
        @param divisional_chart_factor: 1.. 300
        @param start_sign_variation:
            0=>start from base for all signs
            1=>1st/7th from base if sign is odd/even
            2=>1st/9th from base if sign is odd/even
            3=>1st/5th from base if sign is odd/even
            4=>1st/11th from base if sign is odd/even
            5=>1st/3rd from base if sign is odd/even
            6=>1st/5th/9th from base if sign is movable/fixed/dual
            7=>1st/9th/5th from base if sign is movable/fixed/dual
            8=>1st/4th/7th/10th from base if sign is fire/earth/air/water
            9=>1st/10th/7th/4th from base if sign is fire/earth/air/water
        @param base_rasi: 0=>Base is Aries 1=>base is the sign
        @param count_from_end_of_sign=False. 
            If True = Count N divisions from end of the sign if sign is even
            And go anti-zodiac from there by N signs
            TODO: THIS PARAMETER IS NOT MATCHING WITH JHORA - STILL UNDER EXPERIMENT
        @return varga non cyclic tuple 
    """
    pc = []; dirn=1
    for sign in range(12):
        seed = 0 if base_rasi==0 else sign
        t = tuple()
        if count_from_end_of_sign and sign in const.even_signs:
            seed = (12 + sign - dcf + 1)%12
            dirn = -1
        start_sign = seed #start_sign_variation==0
        if start_sign_variation==1 and sign in const.even_signs: start_sign = (seed+6)%12
        elif start_sign_variation==2 and sign in const.even_signs: start_sign = (seed+8)%12
        elif start_sign_variation==3 and sign in const.even_signs: start_sign = (seed+4)%12
        elif start_sign_variation==4 and sign in const.even_signs: start_sign = (seed+10)%12
        elif start_sign_variation==5 and sign in const.even_signs: start_sign = (seed+2)%12
        elif start_sign_variation==6:
            if sign in const.fixed_signs: start_sign = (seed+4)%12
            elif sign in const.dual_signs: start_sign = (seed+8)%12
        elif start_sign_variation==7:
            if sign in const.fixed_signs: start_sign = (seed+8)%12
            elif sign in const.dual_signs: start_sign = (seed+4)%12
        elif start_sign_variation==8:
            if sign in const.earth_signs: start_sign = (seed+3)%12
            elif sign in const.air_signs: start_sign = (seed+6)%12
            elif sign in const.water_signs: start_sign = (seed+9)%12
        elif start_sign_variation==9:
            if sign in const.earth_signs: start_sign = (seed+9)%12
            elif sign in const.air_signs: start_sign = (seed+6)%12
            elif sign in const.water_signs: start_sign = (seed+3)%12        
        for h in range(dcf):
            t += ((start_sign+dirn*h)%12,)
        pc.append(t)
    return pc
def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1
def _convert_1d_house_data_to_2d(rasi_1d,chart_type='south_indian'):
    separator = '/'
    if 'south' in chart_type.lower():
        row_count = 4
        col_count = 4
        map_to_2d = [ [11,0,1,2], [10,"","",3], [9,"","",4], [8,7,6,5] ]
    elif 'east' in chart_type.lower():
        row_count = 3
        col_count = 3
        map_to_2d = [['2'+separator+'1','0','11'+separator+'10'], ['3', "",'9' ], ['4'+separator+'5','6','7'+separator+'8']]
    rasi_2d = [['X']*row_count for _ in range(col_count)]
    for p,val in enumerate(rasi_1d):
        for index, row in enumerate(map_to_2d):
            if 'south' in chart_type.lower():
                i,j = [(index, row.index(p)) for index, row in enumerate(map_to_2d) if p in row][0]
                rasi_2d[i][j] = str(val)
            elif 'east' in chart_type.lower():
                p_index = _index_containing_substring(row,str(p))
                if p_index != -1:
                    i,j = (index, p_index)
                    if rasi_2d[i][j] != 'X':
                        if index > 0:
                            rasi_2d[i][j] += separator + str(val)
                        else:
                            rasi_2d[i][j] = str(val) + separator + rasi_2d[i][j]
                    else:
                        rasi_2d[i][j] = str(val)
    for i in range(row_count):
        for j in range(col_count):
            if rasi_2d[i][j] == 'X':
                rasi_2d[i][j] = ''
    return rasi_2d
get_prasna_lagna_KP_249_for_rasi_chart = lambda kp_no: const.prasna_kp_249_dict[kp_no][0]
get_prasna_lagna_KP_249_for_varga_chart = lambda kp_no,varga_no=1: \
    int(0.5*(const.prasna_kp_249_dict[kp_no][2]+const.prasna_kp_249_dict[kp_no][3])//(30.0/varga_no))%12 if varga_no>1 \
    else get_prasna_lagna_KP_249_for_rasi_chart(kp_no)

get_prasna_lagna_108_for_rasi_chart = lambda kp_no: kp_no//9
get_prasna_lagna_108_for_navamsa = lambda kp_no: 11 if (kp_no%12==0) else (kp_no%12)-1 
get_prasna_lagna_108_for_varga_chart = lambda nadi_no,varga_no=1: \
    get_prasna_lagna_108_for_rasi_chart(nadi_no) if varga_no==1 else \
    (get_prasna_lagna_108_for_navamsa(nadi_no) if varga_no==9 else int(nadi_no//(108/varga_no))%12)
get_prasna_lagna_nadi_for_rasi_chart = lambda nadi_no: nadi_no//150
get_prasna_lagna_nadi_for_varga_chart = lambda nadi_no,varga_no=1: \
    int(nadi_no//(150/varga_no))%12 if varga_no>1 else get_prasna_lagna_nadi_for_rasi_chart(nadi_no)
# Get row,col of the element that contains a string
get_2d_list_index = lambda matrix,search_string,contains_in_element=False: next((i, j) for i, row in enumerate(matrix) \
                        for j, element in enumerate(row) if (contains_in_element and search_string in element) \
                            or (not contains_in_element and search_string == element))
get_1d_list_index = lambda matrix, search_string, contains_in_element=False: \
    next((i for i, element in enumerate(matrix) if (contains_in_element and search_string in element) \
            or (not contains_in_element and search_string == element)), None)
get_KP_nakshathra_from_kp_no = lambda kp_no: const.prasna_kp_249_dict[kp_no][1]
get_KP_details_from_planet_longitude = lambda planet_longitude: \
    {kp_no:[r,n,sd,ed,rl,sl,ssl] for kp_no,[r,n,sd,ed,rl,sl,ssl] in const.prasna_kp_249_dict.items() \
     if planet_longitude >= (r*30+sd) and planet_longitude <= (r*30+ed)}
# Search and replace a string from element of 1d/2d list
def search_replace(input_list, s1, s2):
    if isinstance(input_list[0], list):  # Check if the input_list is a 2D list
        return [[element.replace(s1, s2) if s1 in element else element for element in row] for row in input_list]
    else:  # It's a 1D list
        return [element.replace(s1, s2) if s1 in element else element for element in input_list]
# Lambda function for cyclic counting if stars in the range 1 to 28 (including Abhijit as 22
cyclic_count_of_stars_with_abhijit_in_22 = lambda lst, from_star, to_star: \
                                                (lambda start_idx, end_idx: 
                (end_idx - start_idx + 1) % len(lst) if start_idx <= end_idx else len(lst) - start_idx + end_idx + 1)(lst.index(from_star), lst.index(to_star))
cyclic_count_of_stars_with_abhijit = lambda from_star, count, direction=1,star_count=28: ((from_star - 1 + (count - 1) * direction) % star_count) + 1
cyclic_count_of_stars = lambda from_star, count, direction=1:cyclic_count_of_stars_with_abhijit(from_star, count, direction,star_count=27)
cyclic_count_of_stars_without_abhijit = lambda from_star, count, direction=1:cyclic_count_of_stars_with_abhijit(from_star, count, direction,star_count=27)
cyclic_count_of_numbers = lambda from_number, to_number, dir=1,number_count=30: \
    ((from_number - 1 + (to_number - 1) * dir) % number_count) + 1
def triguna_of_the_day_time(day_index, time_of_day):
    keys = sorted(const.triguna_days_dict.keys())
    
    # Finding min key and next key
    min_key = max((k for k in keys if k <= time_of_day), default=keys[-1])
    next_key = min((k for k in keys if k > min_key), default=keys[0])
    
    return const.triguna_days_dict[min_key][day_index], min_key, next_key
def julian_day_to_date_time_string(jd):
    jy,jm,jd,jfh = jd_to_gregorian(jd)
    ret = "{:04d}-{:02d}-{:02d} {}".format(jy,jm,jd,to_dms(jfh,as_string=True))
    return ret
def get_nakshathra_list_with_abhijith():
    return [NAKSHATRA_LIST[s] for s in range(20)]+[NAKSHATRA_LIST[27]]+[NAKSHATRA_LIST[s] for s in range(20,27)]
karana_lord = lambda karana_index: [_karana_lord for _karana_lord,kar_list in const.karana_lords.items() if karana_index in kar_list[0]][0]
nakshathra_lord = lambda nak_no: const.nakshatra_lords[nak_no-1]
kali_yuga_jd = lambda jd: jd - swe.julday(-3101,1,23,12,cal=swe.JUL_CAL)
def get_year_month_day_from_date_format(date_text):
    # Detect BCE year based on the count of hyphens
    is_bce = False
    hyphen_count = date_text.count('-')
    if hyphen_count in [1,4]:
        is_bce = True
        date_text = date_text[1:]  # Remove the minus sign for parsing
    parts = date_text.split(',')
    if len(parts) == 3 and len(parts[0]) < 4:
        parts[0] = parts[0].zfill(4)
        date_text = ','.join(parts)
    # Define possible date formats
    date_formats = [
        "%d/%m/%Y",  # 29/03/2025
        "%d/%m/%y",  # 29/03/25
        "%Y,%m,%d",  # 2025,02,09
        "%Y-%m-%d",  # 2025-02-09
        "%d-%m-%Y",  # 09-02-2025
        "%m/%d/%Y",  # 02/09/2025
        "%d/%m/%Y",  # 09/02/2025
        "%Y/%m/%d",  # 2025/02/09
        "%B %d, %Y",  # February 09, 2025
        "%b %d, %Y",  # Feb 09, 2025
        "%y,%m,%d",  # 25,02,09
        "%y-%m-%d",  # 25-02-09
        "%d-%m-%y",  # 09-02-25
        "%m/%d/%y",  # 02/09/25
        "%d/%m/%y",  # 09/02/25
        "%y/%m/%d",  # 25/02/09
    ]
    
    # Try to parse the date using the defined formats
    for fmt in date_formats:
        try:
            date_obj = datetime.datetime.strptime(date_text, fmt)
            if is_bce:
                date_obj = -date_obj.year,date_obj.month,date_obj.day
                return date_obj
            else:
                return date_obj.year, date_obj.month, date_obj.day
        except ValueError:
            continue
    # If no format matches, return None
    return map(int,date_text.split(','))
def vaakya_tamil_month(year, month_number):
    """
        Ref: https://groups.google.com/g/mintamil/c/DSXP2KHvgRw - by Ravi Annaswamy
    """
    tamil_month_names = 'சித்திரை,வைகாசி,ஆனி,ஆடி,ஆவணி,புரட்டாசி,ஐப்பசி,கார்த்திகை,மார்கழி,தை,மாசி,பங்குனி'.split(',')

    tamil_month_start_days = \
    [0,
     30.925555,
     62.328888,
     93.939444,
     125.409444,
     156.445555,
     186.901666,
     216.803611,
     246.310277,
     275.658333,
     305.112777,
     334.919444]
    
    
    # Step 1: Calculate how many Kali years are over.
    # Kali yuga started 3101 B.C. when all planets were aligned on one
    # star on other side of earth, so invisible in India.
    kali_year_finished = year+3101
    #print('Year:', year, 'Finished kali:', kali_year_finished)
    
    # Step 2: Count the number of solar years in days
    kd_base = 365.25868055555554 * kali_year_finished
    
    # Step 3: Adjust for Kali arrival delay time. This count represents
    # absolute count of days for this year's new year day.
    kali_sudda_dinam = kd_base - 2.147569444444444
    
    # Step 4: Calculate month start by adding the start days of the month according to
    # Aryabhatiya approximation for average month lengths.
    month_start_kd = kali_sudda_dinam + tamil_month_start_days[month_number-1]
    
    # Step 5: If this happened after sunset, then make the next day 
    kddays=int(month_start_kd)
    kdhours=month_start_kd-kddays
    hours=int(kdhours*24)
    #print(hours)
    minutes=round(((kdhours*24)-hours)*60)
    #print(hours,minutes)
    if kdhours>0.5:
        kddays+=1
    #print(kddays)
    
    # Step 6: Find the day of the week
    weekday = 'வெள்ளி சனி ஞாயிறு திங்கள் செவ்வாய் புதன் வியாழன்'.split()[kddays%7]
    
    # Step 7: Convert to English date.
    # January 1st of 1900 was Kali yuga's 1826555'th day
    # See how many days have elapsed since and add to English date.
    diff=kddays-1826555
    month_birthday = datetime.datetime(1900,1,1,0,0,0)+datetime.timedelta(days=diff)
    
    # Step 8: To calculate how many days in this month, find next month start.
    if month_number < 12:
        next_mon_kd = kali_sudda_dinam + tamil_month_start_days[month_number]
    else:
        next_mon_kd = kali_sudda_dinam + 365.258680555
    if next_mon_kd - int(next_mon_kd)>0.5:
        next_mon_kd=int(next_mon_kd)+1
    else:
        next_mon_kd=int(next_mon_kd)
    next_mon_birthday = datetime.datetime(1900,1,1,0,0,0)+datetime.timedelta(days=next_mon_kd-1826555)
    num_days_in_this_month = (next_mon_birthday-month_birthday).days
    
    return tamil_month_names[month_number-1], datetime.datetime.strftime(month_birthday, '%d-%m-%Y'), weekday, num_days_in_this_month, month_start_kd
def _validate_language_resources(lang):
    set_language(lang)
def trim_info_list_lines(info_lines: list[str], skip_lines: int) -> list[str]:
    """
    Trims the info_lines list by removing the last `skip_lines` before the final "Show more" line.
    Handles cases where the last line may be empty and "Show more" is second-to-last.

    Parameters:
        info_lines (list[str]): The full info list as a list of lines.
        skip_lines (int): Number of lines to skip before the "Show more" line.

    Returns:
        list[str]: The trimmed list of lines.
    """
    if skip_lines == 0 or len(info_lines) <= skip_lines:
        return info_lines

    # Identify the "Show more" line (last non-empty line)
    show_more_index = None
    for i in reversed(range(len(info_lines))):
        if info_lines[i].strip():  # skip empty lines
            show_more_index = i
            break

    if show_more_index is None or show_more_index <= skip_lines:
        return info_lines  # not enough lines to trim

    # Calculate the index to slice up to
    trimmed_end_index = show_more_index - skip_lines

    # Create the trimmed list
    trimmed_lines = info_lines[:trimmed_end_index]

    # Add the original "Show more" line back
    trimmed_lines.append(info_lines[show_more_index])

    return trimmed_lines
def get_varga_option_dict():
    global resource_strings
    """ dict: {dcf:(method_count,method_index,base_rasi_index,count_from_end_of_sign)}"""
    _varga_option_dict = {}; _res = resource_strings
    if const.TREAT_STANDARD_CHART_AS_CUSTOM:
        _varga_option_dict[1] = (None,None,None,None)
        for dcf in range(2,const.MAX_DHASAVARGA_FACTOR+1):                
            _opt_count = len([k for k in _res.keys() if 'dn_custom_option' in k ])
            _varga_option_dict[dcf] = (_opt_count,0,None,None)
    else:
        _varga_option_dict[1] = (None,None,None,None)
        for dcf in const.division_chart_factors[1:]:
            _opt_count = len([k for k in _res.keys() if 'd'+str(dcf)+'_option' in k ])
            _varga_option_dict[dcf] = (_opt_count,1,None,None)
        for dcf in [d for d in range(2,const.MAX_DHASAVARGA_FACTOR+1) if d not in const.division_chart_factors]:                
            _opt_count = len([k for k in _res.keys() if 'dn_custom_option' in k ])
            _varga_option_dict[dcf] = (_opt_count,0,None,None)
    return _varga_option_dict
def is_planet_in_moolatrikona(planet_id, p_pos_tuple=None, chart_1d_house=None, enforce_trikona_degrees=False):
    """
    Checks if a planet is in its Moolatrikona range.
    - If enforce_trikona_degrees is True and p_pos_tuple is provided: checks Sign AND Longitude.
    - Otherwise: checks Sign only (using p_pos_tuple[0] or chart_1d_house).
    """
    m_sign, m_start, m_end = const.moola_trikona_range_of_planets.get(planet_id, (None, None, None))
    
    # Priority 1: Precision check (Sign + Degree)
    if p_pos_tuple is not None and enforce_trikona_degrees:
        sign, lon = p_pos_tuple
        return sign == m_sign and m_start <= lon <= m_end
    # Priority 2: Zodiac check from tuple
    if p_pos_tuple is not None:
        return p_pos_tuple[0] == m_sign
    # Priority 3: Zodiac check from 1D house index
    return chart_1d_house == m_sign
def is_planet_in_exalation(planet,planet_house,planet_positions=None,enforce_deep_exaltation=True):
    if planet_positions is not None and enforce_deep_exaltation:
        sign_idx, lon_in_sign = planet_positions[planet + 1][1]
        abs_longitude = (sign_idx * 30) + lon_in_sign
        deep_ex_lon = const.planet_deep_exaltation_longitudes[planet]
        if abs(abs_longitude - deep_ex_lon) <= const.planet_deep_exaltation_tolerance:
            return True
    else:
        if const.house_strengths_of_planets[planet][planet_house] >= const._EXALTED_UCCHAM:
            return True
    return False
def is_planet_strong(planet,planet_house,include_neutral_samam=False):
    """ 
        If include_neutral_samam = True >= const.SAMAM_NEUTRAL
        else: >= const._FRIEND
    """
    if include_neutral_samam:
        return const.house_strengths_of_planets[planet][planet_house] >= const._NEUTRAL_SAMAM
    else:
        return const.house_strengths_of_planets[planet][planet_house] >= const._FRIEND
def is_planet_in_debilitation(planet,planet_house,planet_positions=None,enforce_deep_debilitation=True):
    if planet_positions is not None and enforce_deep_debilitation:
        sign_idx, lon_in_sign = planet_positions[planet + 1][1]
        abs_longitude = (sign_idx * 30) + lon_in_sign
        deep_ex_lon = const.planet_deep_debilitation_longitudes[planet]
        if abs(abs_longitude - deep_ex_lon) <= const.planet_deep_debilitation_tolerance:
            return True
    else:
        if const.house_strengths_of_planets[planet][planet_house] == const._DEBILITATED_NEECHAM:
            return True
    return False
def is_planet_weak(planet,planet_house,planet_positions=None,enforce_deep_debilitation=False):
    if planet_positions is not None and enforce_deep_debilitation:
        sign_idx, lon_in_sign = planet_positions[planet + 1][1]
        abs_longitude = (sign_idx * 30) + lon_in_sign
        deep_ex_lon = const.planet_deep_debilitation_longitudes[planet]
        if abs(abs_longitude - deep_ex_lon) <= const.planet_deep_debilitation_tolerance:
            return True
    else:
        if const.house_strengths_of_planets[planet][planet_house] <= const._DEBILITATED_NEECHAM:
            return True
    return False
if __name__ == "__main__":
    pass