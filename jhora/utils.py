"""
    utils module
    contains common functions used by various PyHora modules
"""
import os
import codecs
import warnings
import geocoder
import requests
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
import pandas as pd
import numpy as np
import swisseph as swe
from geopy.geocoders import Nominatim
from hora import const
from hora.panchanga import drik as drig_panchanga
import json
import datetime
from dateutil import relativedelta

[PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,
    PAKSHA_LIST,YOGAM_LIST,MONTH_LIST,YEAR_LIST,DHASA_LIST,
    BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST] = ([''],)*14

_world_city_db_df = []
world_cities_db = []
google_maps_url = "https://www.google.cl/maps/place/"#+' time zone'
_world_city_db_df = pd.read_csv(const._world_city_csv_file,header=None,encoding='ISO-8859-1') #encoding='utf-8')
world_cities_db = np.array(_world_city_db_df.loc[:].values.tolist())
world_cities_list = _world_city_db_df[1].tolist()

sort_tuple = lambda tup,tup_index,reverse=False: sorted(tup,key = lambda x: x[tup_index],reverse=reverse)

def _get_time_zone_hours():
    import pytz
    tzl = []
    for c1,c2,_,_,tz1 in world_cities_db:#[:100]:
        try:
            tz2 = str(datetime.datetime.now(pytz.timezone(tz1)))[-6:].split(':')
            tz2n = int(tz2[0])+int(tz2[1])/60.0
        except:
            print(c1,c2,tz1,' not found')
            tz2n = 99.99
        tzl.append(tz2n)
    _world_city_db_df[""] = tzl
    _world_city_db_df.to_csv(const.ROOT_DIR+"//data//delme.csv",index=False,header=False)
#_get_time_zone_hours()
#exit()
def save_location_to_database(location_data):
    global _world_city_db_df, world_cities_db,world_cities_list
    print('writing ',location_data,' to ',const._world_city_csv_file)
    _world_city_db_df.loc[len(_world_city_db_df.index)] = location_data
    _world_city_db_df.to_csv(const._world_city_csv_file,mode='w',header=None,index=False)#,quoting=None)
    
" Flatten a list of lists "
flatten_list = lambda list: [item for sublist in list for item in sublist]
def _get_place_from_ipinfo():
    #from requests import get
    #import json
    
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
        if g==None or g=='':
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
            print('Location obtained from IP Address:',place,[latitude,longitude])
            return place,latitude,longitude,time_zone_offset
    except:
        print('No latitude/longitude provided. Could not guess location from IP Address')
        return [None,None,None,None]
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
    if place != None and (latitude==None or longitude==None):
        city,latitude,longitude,time_zone_offset = get_location(place)
    if latitude==None or longitude==None:
        place,latitude,longitude,time_zone_offset = get_place_from_user_ip_address()
    if dob==None:
        today = datetime.datetime.today()
        dob = (today.year,today.month,today.day)
        print("Today's Date:",dob,'assumed')
    if tob==None:
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
    if place_name==None or place_name.strip()=='':
        result = get_place_from_user_ip_address()
        if result:
            return result
    ' first check if lat/long in world cities db'
    place_index = -1
    place_name_1 = place_name.split(',')[0]
    place_index = [row for row,city in enumerate(world_cities_list) if place_name.lower() == city.lower()]
    #place_index = [row for row,city in enumerate(world_cities_list) if place_name_1.lower() in city.lower()]
    #print('place_name,place_name_1,place_index',place_name,place_name_1,place_index)
    if len(place_index)>0:
        place_found = True
        print(place_name,'in the database')
        place_index = int(place_index[0])
        city = world_cities_db[place_index,1]
        _latitude = round(float(world_cities_db[place_index,2]),4)
        _longitude = round(float(world_cities_db[place_index,3]),4)
        _time_zone = round(float(world_cities_db[place_index,5]),2)
        result = [city,_latitude,_longitude,_time_zone]
    else:
        print(place_name,'not in '+const._world_city_csv_file+'.Trying to get from Google')
        result = _scrap_google_map_for_latlongtz_from_city_with_country(place_name)
        if result != None and len(result)==3:
            place_found = True
            print(place_name,' found from google maps')
            _place_name = place_name
            _latitude = round(result[0],4)
            _longitude = round(result[1],4)
            _time_zone = round(result[2],2)
            result = [place_name,_latitude,_longitude,_time_zone]
            """ TODO: To save in database
            result should be converted to the CSV format in world_cities file
            Country, place, lat, long, timezone string, timezone hours
            from place_name we should extract country and place name
            And somehow we should get timezone string
            """
            if ',' in place_name:
                _city,_country = place_name.split(','); _tz_str = ''
                if _city not in world_cities_list:
                    save_location_to_database([_country,_city,_latitude,_longitude,_tz_str,_time_zone])
        else:
            print('Could not get',place_name,'from google.Trying to get from OpenStreetMaps')
            place_found = False
            result = get_location_using_nominatim(place_name)
            if result:
                place_found = True
                print(place_name,'found in OpenStreetMap')
                [_place_name,_latitude,_longitude,_time_zone] = result
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
    return latitude,longitude,timezone_offset
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
def set_language(language=const._DEFAULT_LANGUAGE):
    global PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST, MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST
    global SHADVARGAMSA_NAMES,SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES
    global SEASON_NAMES
    global resource_strings
    #print('language',language)
    if language in const.available_languages.values():
        #print('default language set to',language)
        const._DEFAULT_LANGUAGE = language
        language_list_file = const._LANGUAGE_PATH+const._DEFAULT_LANGUAGE_LIST_STR+language+'.txt'
        #print('language_list_file',language_list_file)
        language_message_file = const._LANGUAGE_PATH+const._DEFAULT_LANGUAGE_MSG_STR+language+'.txt'
        
    [PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST,MONTH_LIST,\
     YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST,SHADVARGAMSA_NAMES,\
     SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES,SEASON_NAMES] = \
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
#    print (cal_key_list)
    return cal_key_list       
def get_resource_messages(language_message_file=const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_MSG_STR + const._DEFAULT_LANGUAGE + '.txt'):
    """
        Retrieve message strings from language specific message resource file
        @param param:language_message_file -language specific message resource file name
            Default: const._LANGUAGE_PATH + 'msg_strings_' + const._DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/msg_strings_en.txt
        @return: dictionary of message keys with language specific values
    """
    global PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST, MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST
    global SHADVARGAMSA_NAMES,SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES
    global SEASON_NAMES, KALA_SARPA_LIST, MANGLIK_LIST
    res = _read_resource_messages_from_file(language_message_file)
    return res
resource_strings = get_resource_messages(const._LANGUAGE_PATH+const._DEFAULT_LANGUAGE_MSG_STR+const._DEFAULT_LANGUAGE+'.txt')
def _read_resource_lists_from_file(language_list_file):
    from os import path
    global PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST, MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST
    global SHADVARGAMSA_NAMES,SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES
    global SEASON_NAMES
    if not path.exists(language_list_file):
        print('Error: input file:'+language_list_file+' does not exist. Script aborted.')
        exit()
    fp = codecs.open(language_list_file, encoding='utf-8', mode='r')
    line = fp.readline().strip().replace('\n','')
    line = line.replace("\r","").rstrip()
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    PLANET_NAMES = line.replace("\r","").rstrip('\n').split(',')
    """ For troipcal mode Rahi and Kethu are excluded, Uranus, Neptune and Pluto are included """
    if const._TROPICAL_MODE:
        PLANET_NAMES = PLANET_NAMES[:7] + PLANET_NAMES[9:]
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    RAASI_LIST = line.replace("\r","").rstrip('\n').split(',')
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
    
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    SHADVARGAMSA_NAMES = line.rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    SAPTAVARGAMSA_NAMES = line.rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    DHASAVARGAMSA_NAMES = line.rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    SHODASAVARGAMSA_NAMES = line.rstrip('\n').split(',')
    line = fp.readline().strip().replace('\n','')
    if line.lstrip()[0] == '#':
        line = fp.readline().strip().replace('\n','')
    SEASON_NAMES = line.rstrip('\n').split(',')
#    exit()
    return [PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST,\
            MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST,SHADVARGAMSA_NAMES,\
            SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES,SEASON_NAMES]
def get_resource_lists(language_list_file=const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_LIST_STR + const._DEFAULT_LANGUAGE + '.txt'):
    """
        Retrieve resource list from language specific resource list file
        list values in resource language are read and returned
        @param param:language_message_file -language specific message resource file name
            Default: _DEFAULT_LANGUAGE_LIST_FILE = _LANGUAGE_PATH + 'list_values_' + _DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/list_values_en.txt
        @return: [PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,
                 YOGAM_LIST,MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST,
                 SHADVARGAMSA_NAMES,SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES]
    """
    return _read_resource_lists_from_file(language_list_file)
#get_resource_lists(language_list_file)
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

def to_dms(deg,as_string=True, is_lat_long=None,round_seconds_to_digits=None,round_to_minutes=None):
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
    if (is_lat_long==None):
        if d > 23:
            q = d // 24
            d = d % 24 #d -= 24
            next_day = ' (+'+str(q)+')'
        elif d < 0:
            d = abs(d) % 24
            m = abs(m)
            s = abs(s)
            next_day = ' (-1)'
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
    if as_string or is_lat_long != None:
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
                str(d).zfill(2)+ sep +str(m).zfill(2)+ampm+next_day
    return answer
def _to_dms_old(deg):
  d, m, s = to_dms_prec(deg)
  return [d, m, int(s)]

def unwrap_angles(angles):
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
    from hora.panchanga import drik
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
    if place != None: # if solar time > sunset time move to next day
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
#def udhayadhi_nazhikai(birth_time, sunrise_time_in_float_hours):
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
        tl = 24 + end_time_hrs - abs(start_time_hrs)
    tf = (end_time_hrs-birth_time_hrs)/tl
    #print('birth time',birth_time_hrs, 'tithi start',tithi_start_time_hrs,'tithi end',tithi_end_time_hrs,'tithi duration',tl,'tithi fraction',tf)
    return tf
    
if __name__ == "__main__":
    lang = 'ta'
    set_language(lang)
    res = get_resource_messages(language_message_file=const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_MSG_STR + lang + '.txt')
    print(PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST, MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST)
    print(SHADVARGAMSA_NAMES,SAPTAVARGAMSA_NAMES,DHASAVARGAMSA_NAMES,SHODASAVARGAMSA_NAMES)
    print(SEASON_NAMES, KALA_SARPA_LIST, MANGLIK_LIST)
    exit()
    from hora.panchanga import drik
    pdate1 = drik.Date(-1,12,7)
    npdate1=np.datetime64(pdate1)
    pdate2 = drik.Date(1,12,7)
    npdate2=np.datetime64(pdate2)
    days_diff = (npdate2-npdate1)/np.timedelta64(1,"D")
    years_diff,days_diff = divmod(days_diff,const.sidereal_year)
    months_diff,days_diff = divmod(days_diff,(const.sidereal_year/12))
    print(years_diff,months_diff,days_diff)
    exit()
    dob = (1996,12,7)
    tob = (10,34,0)
    print(get_dob_years_months_60hrs_from_today(dob,tob))
    exit()
    print(get_place_from_user_ip_address())
    exit()
    result = get_location('Shillong,India')
    lat = result[1]
    long = result[2]
    elevation = int(get_elevation(lat,long))
    print(result,elevation)
    exit()
    chart_36 = ['','8','6','','5','2/0','3/L','7','','1','4','']
    p_to_h = get_planet_to_house_dict_from_chart(chart_36)
    print(p_to_h)
    h_to_p = get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    print(h_to_p)