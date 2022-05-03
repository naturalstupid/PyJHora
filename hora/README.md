### Package Structure:

```
hora
   !- data       - contains program configuration data, world cities data, marriage compatibility table
         !- ephe - contains swiss ephimeride compressed JPL data
   !- images     - contains images
   !- lang       - contains language resource files
   !- panchanga  - panchanga module to calculate daily panchanga
   !- horoscope
        !- horoscope.py - horoscope package
        !- chart  - chart package
           !- arudhas.py     - arudhas, argala, virodhargal
           !- ashtavarga.py  - ashtavarga, trikona sodhana, ekadhipatya_sodhana, sodhaya pinda
           !- charts.py      - divisional charts, planet combustion, retrograde
           !- house.py       - aspects, drishti,stronger planets/raasi, kaarakas
           !- yoga.py        - 100+ yogas
           !- raja_yoga.py - raja_yoga and its sub-types
        !- dhasa  - dhasa package
           !- ashtottari.py  - ashtottari dhasa-bhuthi
           !- drig.py        - drigdhasa-bhuthi
           !- kalachakra.py  - kalachakra dhasa-bhuthi
           !- moola.py       - moola dhasa-bhuthi
           !- mudda.py  	  - mudda dhasa-bhuthi
           !- narayana.py    - narayana dhasa-bhuthi
           !- nirayana.py    - nirayana dhasa-bhuthi
           !- patyayini.py   - patyayini dhasa-bhuthi
           !- shoola.py      - shoola dhasa-bhuthi
           !- sudasa.py      - sudasa dhasa-bhuthi
           !- sudharsana_chakra.py   - sudharsana_chakra dhasa-bhuthi
           !- vimsottari.py  - vimsottari dhasa-bhuthi
        !- match  - marriage compatibility package
           !- compatibility.py  - marriage compatibility
        !- transit  - tajaka package
           !- tajaka.py      - annual, monthly and 60 hour charts, muntha, vargeeya balas, tajaka lord 
           !- tajaka_yoga.py - tajaka yogas
           !- saham.py       - 36 sahams
   !- ui  - user interface package
      !- horo_chart.py         - simple horoscope chart Raasi/Navamsa and calendar information
      !- horo_chart_tabs.py    - horoscope with lot of details
      !- match_ui.py           - ui for marriage compatibility
   !- utils.py             - utility functions
   !- const.py             - constants related to PyHora package        
   !- tests  - unit/integration tests
      !- unit_tests.py           - unit tests for the features based on examples from the book
      !- pvr_tests.py            - Exercise problems from book.
```
### utils module - functions
#### Required imports
```
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
```
##### get\_place\_from\_user\_location ()
    """
        function to get place from user's IP address
        @param - None
        @return place,latitude,longitude,time_zone_offset
    """
##### scrap\_google\_map\_for\_latlongtz\_from\_city\_with\_country (city\_with\_country)
    """
        function to scrap google maps to get latitude/longitude of a city/country
        @param city_with_country: city name <comma> country name
            Example: Chennai, India
        @return [city,latitude,longitude,time_zone_offset]
    """
##### get\_latitude\_longitude\_from\_place\_name (place\_with\_country\_code)
    """
        function to get latitude/longitude from city with country code using Nominatim
        requires geopy installed
        @param place_with_country_code: city name <comma> country name
            Example: Chennai, IN
        @return [city,latitude,longitude,time_zone_offset]
    """
##### get\_place\_latitude\_longitude (place\_name)
    """
        this is the top level function to be used to get latitude/longitude from the place name
        This internally calls other functions to try out the in the following order
        First checks if city is found in the CSV file comes up with the package
        Then checks google maps, and then Open Street Map / Nominatim
        @param place_name: city name <comma> country name
            Example: Chennai, IN
        @return [city,latitude,longitude,time_zone_offset]
    """
##### get\_place\_timezone\_offset (latitude, longitude)
    """
        This can be used when latitude/longitude are known but not the time zone offset of the place.
        This is an internal function that returns a location's time zone offset from UTC in minutes - using latitude/longitude of the place.
        @param latitude: latitude of the place
        @param longitude: longitude of the place
        @return [city,latitude,longitude,time_zone_offset]
    """
##### get\_house\_to\_planet\_dict\_from\_planet\_to\_house\_dict (planet\_to\_house\_dict)
    """
        function to get house_to_planet list from planet_to_house dictionary 
        @param planet_to_house dict: Format {planet_id : raasi_number, ....}
                Example: {0:0, 1:1,2:1,...} Sun in Aries, Moon in Tarus, Mars in Gemini etc
        @return: house_to_planet list 
        	- in the format ['0','1/2',...] Aries has Sun, Tarus has Moon/Mars etc
    """
##### get\_planet\_to\_house\_dict\_from\_chart (house\_to\_planet\_list)
    """
        function to get planet_to_house dictionary from house_to_planet list  
        @param house_to_planet list - in the format ['0','1/2',...] Aries has Sun, Tarus has Moon/Mars etc
        @return: house_to_planet_list: 
                Format {planet_id : raasi_number, ....}
                Example: {0:0, 1:1,2:1,...} Sun in Aries, Moon in Tarus, Mars in Gemini etc
    """
##### get\_planet\_house\_dictionary\_from\_planet\_positions (planet\_positions)
    """ 
        Get Planet_to_House Dictionary {p:h}  from Planet_Positions {p:(h,long)}
        @param planet_positions: Format: {planet_index:(raasi_index,planet_longitude_in_the_raasi),...
        @return: planet_to_house_dictionary in the format {planet_index:raasi_index,...} 
    """ 
##### get\_house\_planet\_list\_from\_planet\_positions (planet\_positions):
    """
        to convert from the format [planet,(house,planet_longitude,...]
        into a dict of {house_1:planet_1/planet_2,house_2:Lagnam/planet_2,....}
        @param planet_positions: Format: {planet_index:(raasi_index,planet_longitude_in_the_raasi),...
        @return: house_to_planet list - in the format ['0','1/2',...] Aries has Sun, Tarus has Moon/Mars etc
    """
##### get\_resource\_messages (language\_message\_file = const.\_DEFAULT\_LANGUAGE\_MSG\_FILE):
    """
        Retrieve message strings from language specific message resource file
        @param param:language_message_file -language specific message resource file name
            Default: const._LANGUAGE_PATH + 'msg_strings_' + const._DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/msg_strings_en.txt
        @return: dictionary of message keys with language specific values
    """
##### get\_resource\_lists (language\_list\_file=const.\_DEFAULT\_LANGUAGE\_LIST\_FILE):
    """
        Retrieve resource list from language specific resource list file
        list values in resource language are read and returned
        @param param:language_message_file -language specific message resource file name
            Default: _DEFAULT_LANGUAGE_LIST_FILE = _LANGUAGE_PATH + 'list_values_' + _DEFAULT_LANGUAGE + '.txt'
            Defualt: ./lang/list_values_en.txt
        @return: [PLANET_NAMES,NAKSHATRA_LIST,TITHI_LIST,RAASI_LIST,KARANA_LIST,DAYS_LIST,PAKSHA_LIST,
                 YOGAM_LIST,MONTH_LIST,YEAR_LIST,DHASA_LIST,BHUKTHI_LIST,PLANET_SHORT_NAMES,RAASI_SHORT_LIST]
    """
    
##### to\_dms\_prec (deg)
	"""
	convert float degrees to (int)degrees, (int) minutes, (float) seconds tuple
	"""
##### to\_dms (deg,as\_string=False, is\_lat\_long=None)
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
##### unwrap\_angles (angles)
	"""
      Add 360 to those elements in the input list so that all elements are sorted in ascending order.
	"""
##### inverse\_lagrange (x, y, ya)
	""" 
		Given two lists x and y, find the value of x = xa when y = ya, i.e., f(xa) = ya
	"""
##### julian\_day\_number (date\_of\_birth\_as\_tuple, time\_of\_birth\_as\_tuple)
    """
        return julian day number for give date of birth and time of birth as tuples
        @param date_of_birth_as_tuple: date of birth as tuple. e.g. (2000,1,1)
            Note: For BC Dates use negative year e.g. (-3114,1,1) means 1-Jan of 3114 BC
            Note: There is no 0 BC or 0 AD so avoid Zero year
        @param time_of_birth_as_tuple: time of birth as tuple e.g. (18,0,30)
        @return julian day number 
    """
##### deeptaamsa\_range\_of\_planet (planet, planet\_longitude\_within\_raasi)
    """
        get deeptaaamsa range of the planet
        @param planet: the index of the planet 0 for Sun, 1 for moon, ... 7 for Rahu and 8 for Ketu
        @param planet_longitude_within_raasi: longitude of the planet within the raasi (0.0 to 30.0 degrees)
        @return: deeptaamsa range of the planet as a tuple (deeptaamsa_minimum, deeptaamsa_maximum) 
    """
