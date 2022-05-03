"""
    utils module
    contains common functions used by various PyHora modules
"""
import os
import sys
import codecs
import warnings
import datetime
import geocoder
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
import pandas as pd
import numpy as np
import swisseph as swe
from geopy.geocoders import Nominatim
from hora import const
df = []
world_cities_db = []
google_maps_url = "https://www.google.cl/maps/place/"#+' time zone'

" Flatten a list of lists "
flatten_list = lambda list: [item for sublist in list for item in sublist]

def get_place_from_user_location():
    """
        function to get place from user's IP address
        @param - None
        @return place,latitude,longitude,time_zone_offset
    """
    g = ''
    try:
        """ Try to get using IP Address of the user """
        g = geocoder.ip('me')
        if g==None:
            sys.exit('No latitude/longitude provided. Could not guess location from IP Address')
        else:
            place,country,[latitude,longitude] = g.city,g.country, g.latlng
            place += ','+country
            time_zone_offset = get_place_timezone_offset(latitude,longitude)
            print('Location obtained from IP Address:',place,[latitude,longitude])
            return place,latitude,longitude,time_zone_offset
    except:
        sys.exit('No latitude/longitude provided. Could not guess location from IP Address')
    
def _validate_data(place,latitude,longitude,time_zone_offset,dob,tob,division_chart_factor):
    country = ''
    if place != None and (latitude==None or longitude==None):
        city,latitude,longitude,time_zone_offset = get_place_latitude_longitude(place)
    if latitude==None or longitude==None:
        place,latitude,longitude,time_zone_offset = get_place_from_user_location()
    if dob==None:
        today = datetime.date.today()
        dob = (today.year,today.month,today.day)
        print("Today's date:",dob,'assumed')
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
def scrap_google_map_for_latlongtz_from_city_with_country(city_with_country):
    """
        function to scrap google maps to get latitude/longitude of a city/country
        @param city_with_country: city name <comma> country name
            Example: Chennai, India
        @return [city,latitude,longitude,time_zone_offset]
    """
    resp=requests.request(method="GET",url=google_maps_url+city_with_country)
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
    timezone_offset = _get_place_timezone_offset(latitude, longitude)
    print('city',city_with_country,'lat=',latitude,'long=',longitude,'timezone offset',timezone_offset)
    return city_with_country,latitude,longitude,timezone_offset
def get_latitude_longitude_from_place_name(place_with_country_code):
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
def get_place_latitude_longitude(place_name):
    """
        this is the top level function to be used to get latitude/longitude from the place name
        This internally calls other functions to try out the in the following order
        First checks if city is found in the CSV file comes up with the package
        Then checks google maps, and then Open Street Map / Nominatim
        @param place_name: city name <comma> country name
            Example: Chennai, IN
        @return [city,latitude,longitude,time_zone_offset]
    """
    result = None
    place_found = False
    latitude, longitude,time_zone = [0.0,0.0,0.0]
    df = pd.read_csv(const._world_city_csv_file,header=None,encoding='utf-8')
    world_cities_db = np.array(df.loc[:].values.tolist())
    ' first check if lat/long in world cities db'
    place_index = -1
    place_name_1 = place_name.replace(',',' ')
    world_cities_list = df[1].tolist()
    place_index = [row for row,city in enumerate(world_cities_list) if place_name_1.split()[0].lower() in city.lower()]
    if len(place_index)>0:
        place_found = True
        print(place_name,'is in the database')
        place_index = int(place_index[0])
        latitude = round(float(world_cities_db[place_index,2]),4)
        longitude = round(float(world_cities_db[place_index,3]),4)
        time_zone = round(float(world_cities_db[place_index,5]),2)
        return place_name,latitude,longitude,time_zone
    else:
        print(place_name,'is not in the world cities csv database.Trying to get from Google')
        result = scrap_google_map_for_latlongtz_from_city_with_country(place_name)
        if result != None and len(result)==3:
            place_found = True
            print(place_name,' found from google maps')
            place_name = place_name
            latitude = round(result[0],4)
            longitude = round(result[1],4)
            time_zone = round(result[2],2)
            return result
        else:
            print('Could not get',place_name,'from google.Trying to get from OpenStreetMaps')
            place_found = False
            result = get_latitude_longitude_from_place_name(place_name)
            if result:
                place_found = True
                print(place_name,'found in OpenStreetMap')
                return result
        msg = place_name+" could not be found in OpenStreetMap.\nTry entering latitude and longitude manually.\nOr try entering nearest big city"
        print(msg)
        return None
def get_place_timezone_offset(latitude, longitude):
    """
        This can be used when latitude/longitude are known but not the time zone offset of the place.
        This is an internal function that returns a location's time zone offset from UTC in minutes - using latitude/longitude of the place.
        @param latitude: latitude of the place
        @param longitude: longitude of the place
        @return [city,latitude,longitude,time_zone_offset]
    """
    tf = TimezoneFinder()
    today = datetime.datetime.now()
    tz_target = timezone(tf.timezone_at(lng=longitude, lat=latitude))
    # ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    tz_offset = (today_utc - today_target).total_seconds() / 3600.0 # in hours
    return tz_offset
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
        @return: house_to_planet_list: 
                Format {planet_id : raasi_number, ....}
                Example: {0:0, 1:1,2:1,...} Sun in Aries, Moon in Tarus, Mars in Gemini etc
    """
    p_to_h = {p:h for p in [*range(9)]+['L'] for h,planets in enumerate(house_to_planet_list) if str(p) in planets }
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
def get_resource_messages(language_message_file=const._DEFAULT_LANGUAGE_MSG_FILE):
    """
        Retrieve message strings from language specific message resource file
        @param param:language_message_file -language specific message resource file name
            Default: const._LANGUAGE_PATH + 'msg_strings_' + const._DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/msg_strings_en.txt
        @return: dictionary of message keys with language specific values
    """
    return _read_resource_messages_from_file(language_message_file)
resource_strings = get_resource_messages(language_message_file=const._DEFAULT_LANGUAGE_MSG_FILE)

def _read_resource_lists_from_file(language_list_file):
    import os.path
    from os import path
    import codecs
    global PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,YOGAM_LIST, MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST
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
def get_resource_lists(language_list_file=const._DEFAULT_LANGUAGE_LIST_FILE):
    """
        Retrieve resource list from language specific resource list file
        list values in resource language are read and returned
        @param param:language_message_file -language specific message resource file name
            Default: _DEFAULT_LANGUAGE_LIST_FILE = _LANGUAGE_PATH + 'list_values_' + _DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/list_values_en.txt
        @return: [PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,
                 YOGAM_LIST,MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST]
    """
    return _read_resource_lists_from_file(language_list_file)
get_resource_lists(language_list_file=const._DEFAULT_LANGUAGE_LIST_FILE)
# Convert 23d 30' 30" to 23.508333 degrees
from_dms = lambda degs, mins, secs: degs + mins/60 + secs/3600

# the inverse
def to_dms_prec(deg):
  """
      convert float degrees to (int)degrees, (int) minutes, (float) seconds tuple
  """
  d = int(deg)
  mins = (deg - d) * 60
  m = int(mins)
  s = round((mins - m) * 60, 6)
  return [d, m, s]

def to_dms(deg,as_string=False, is_lat_long=None):
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
  degree_symbol = "°" 
  minute_symbol = u'\u2019'
  second_symbol = '"'
  next_day = ''
  d = int(deg)
  mins = (deg - d) * 60
  m = int(mins)
  ss = (mins-m)*60
  s = int(ss)
  #"""
  if (is_lat_long==None) and d > 23:
      #print('is_lat_long,d',is_lat_long,d)
      # WEIRD Following subtraction does not happen
      q = d // 24
      d = d % 24 #d -= 24
      next_day = ' (+'+str(q)+')'
#      print('d=',d)
  #"""
  if d >= 12:
      ampm = pm
  if m==60:
      d += 1
      m = 0
  #s = int(round((mins - m) * 60))
  if s==60:
      m += 1
      s = 0
  answer = [d, m, s]
  if as_string or is_lat_long != None:
      if is_lat_long=='plong':
          answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol+" "+str(abs(s))+second_symbol
      elif is_lat_long=='lat':
          answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol+" "+str(abs(s))+second_symbol
          if d > 0: answer += ' N'
          else: answer +=' S' 
      elif is_lat_long=='long':
          answer = str((d))+degree_symbol+" "+str(abs(m))+minute_symbol+" "+str(abs(s))+second_symbol
          if d > 0: answer += ' E'
          else: answer +=' W' 
      else: ## as_string = =True
          answer= str(d).zfill(2)+ sep +str(m).zfill(2)+ sep +str(s).zfill(2)+ampm+next_day
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

# Ketu is always 180° after Rahu, so same coordinates but different constellations
# i.e if Rahu is in Pisces, Ketu is in Virgo etc
ketu = lambda rahu: (rahu + 180) % 360
rahu = lambda ketu: (ketu + 180) % 360

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

def julian_day_number(date_of_birth_as_tuple,time_of_birth_as_tuple):
    """
        return julian day number for give date of birth and time of birth as tuples
        @param date_of_birth_as_tuple: date of birth as tuple. e.g. (2000,1,1)
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
jd_to_gregorian = lambda jd: swe.revjul(jd, swe.GREG_CAL)   # returns (y, m, d, h, min, s)
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

if __name__ == "__main__":
    chart_36 = ['','8','6','','5','2/0','3/L','7','','1','4','']
    p_to_h = get_planet_to_house_dict_from_chart(chart_36)
    print(p_to_h)
    h_to_p = get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    print(h_to_p)