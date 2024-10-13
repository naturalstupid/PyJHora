### panchanga module - functions `jhora.panchanga.drik`: 

    To calculate the following features:
- setting one of 20 ayanamsa modes (FAGAN, KP, LAHIRI, RAMAN, USHASHASHI, YUKTESHWAR, SURYASIDDHANTA, SURYASIDDHANTA_MSUN, ARYABHATA, ARYABHATA_MSUN, SS_CITRA, TRUE_CITRA, TRUE_REVATI, SS_REVATI, SENTHIL, TRUE_LAHIRI, TRUE_PUSHYA, TRUE_MULA, KP-SENTHIL, SIDM_USER (where user can enter their own value). 
- panchanga: sunrise/set, moonrise/set, midday/night, day/night length, tithi,karana, yogam, raasi, nakshatra padha, vaara, lunar month, tamil month/date, elapsed year, new moon, samvasatra, ritu, gauri chogadiya, trikalam, durmuhurtham, abhijit muhurta, 
- sidereal longitude of planets, dhasavarga longitude of planets, bhaava madhya, ascendant, declination of planets, longitudes of upagrahas (such as dhuma, vyatipaata, parivesha, indrachapa and upakethu, kaala, mrithyu, artha praharaka, yama ghantaka, gulika and maandi), special lagnas (such as bhava, hora, ghati, vighati, pranapada, indu, bhrigu bindhu, kunda, sree lagna), 
- previous/next sankranti dates, previous/next solar entry dates, previous/next solar/lunar eclipse, birth rectification (BV Raman - experimental work - accuracy not guaranteed though), previous/next occurrence of planet pairs, previous/next planet entry into specified rasi, previous/next retrogression of planets and nisheka (does not match JHora values).


### Required imports
```
from geopy.geocoders import Nominatim
from pytz import timezone, utc
from math import ceil
from collections import namedtuple as struct
import swisseph as swe
from _datetime import datetime, timedelta
from datetime import date
import math, os, warnings
from collections import OrderedDict as Dict
```

```
""" Since datetime does not accept BC year values Use the following stucture to represent dates """
Date = struct('Date', ['year', 'month', 'day'])
""" To represent Place use the following structure as an argument """
Place = struct('Place', ['Place','latitude', 'longitude', 'timezone'])
```
##### Lamda functions
```
reset_ayanamsa_mode = lambda: swe.set_sid_mode() # resets ayanamsa_mode to Default
from_dms = lambda degs, mins, secs: degs + mins/60 + secs/3600
# Ketu is always 180° after Rahu, so same coordinates but different constellations
# i.e if Rahu is in Pisces, Ketu is in Virgo etc
ketu = lambda rahu: (rahu + 180) % 360
rahu = lambda ketu: (ketu + 180) % 360
solar_longitude = lambda jd: sidereal_longitude(jd, swe.SUN)
lunar_longitude = lambda jd: sidereal_longitude(jd, swe.MOON)
raahu_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'raahu kaalam', as_string=as_string)
yamaganda_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'yamagandam', as_string=as_string)
gulikai_kaalam = lambda jd, place,as_string=False: trikalam(jd, place, 'gulikai',as_string=as_string)
navamsa_from_long = lambda longitude: dasavarga_from_long(longitude,9) 
kaala_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=0,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
mrityu_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=2,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
artha_praharaka_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=3,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
yama_ghantaka_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=4,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
gulika_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=6,divisional_chart_factor=divisional_chart_factor,upagraha_part='middle',as_string=as_string)
maandi_longitude = lambda dob,tob,place,divisional_chart_factor=1,as_string=False: upagraha_longitude(dob,tob,place,planet_index=6,divisional_chart_factor=divisional_chart_factor,upagraha_part='begin',as_string=as_string)
bhava_lagna = lambda jd,place,time_of_birth_in_hours,divisional_chart_factor,as_string=False: special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=1.0,divisional_chart_factor=divisional_chart_factor,as_string=as_string) 
hora_lagna = lambda jd,place,time_of_birth_in_hours,divisional_chart_factor=1,as_string=False: special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=0.5,divisional_chart_factor=divisional_chart_factor,as_string=as_string) 
ghati_lagna = lambda jd,place,time_of_birth_in_hours,divisional_chart_factor=1,as_string=False: special_ascendant(jd,place,time_of_birth_in_hours,lagna_rate_factor=1.25,divisional_chart_factor=divisional_chart_factor,as_string=as_string) 
```
##### get\_ayanamsa\_value (jd)
    """
        Get ayanamsa value for the julian day number
        Note: Recommended to call this  immediately after calling set_ayanamsa_mode
        returns the ayanamsa value for the ayanamsa mode passed to set_ayanamsa_mode or that of const._DEFAULT_AYANAMSA_MODE
        @param jd: Julian Day Number
        @return: ayanamsa value - ayanamsa for the day based on the model used. 
    """
##### set\_ayanamsa\_mode (ayanamsa\_mode = `const._DEFAULT_AYANAMSA_MODE`, ayanamsa\_value=None, jd=None)
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
##### nakshatra\_pada (longitude)
    """
      Gives nakshatra (1..27) and paada (1..4) in which given longitude lies
      @param longitude: longitude of the planet 
      @return [nakshathra index, paadham, longitude remainder in the nakshathra]
          Note: Nakshatra index [1..27], Paadha [1..4] reminder in float degrees 
    """
##### sidereal\_longitude (jd, planet)
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
##### planets\_in\_retrograde(jd, place)
	"""
	    To get the list of retrograding planets
	    @param jd: julian day number (not UTC)
	    @param place: Place as struct ('Place',latitude,longitude,timezone)
	    @return: list of retrograding planets e.g. [3,5]
	    NOTE: To find the retrograding planets for kundali charts use this function.
	    There is another function in `jhora.horoscope.chart.charts` module which calculates
	    retrograding planet based on their positions and is used in yoga, dhasa calculations
	"""
##### sunrise(jd, place)
	"""
        Sunrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [sunrise time as local time in float hours, local time string, and sunrise julian number]
            e.g. [6.5,'06:30 AM',2450424.94]

	"""
##### midday(jd, place)
	"""
        Return midday time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [midday time as local time in float hours, local time string, and midday julian number]
            e.g. [12.1,'12:10 PM',2450424.94]

	"""
##### midnight(jd, place)
	"""
        Return midnight time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [midnight time as local time in float hours, local time string, and midnight julian number]
            e.g. [0.1,'00:10 AM',2450424.94]

	"""
##### day\_length(jd, place)
	"""
        Return local day length in float hours
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: day length in float hours. e.g. 12.125
	"""
##### night\_length(jd, place)
	"""
        Return local night length in float hours
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: night length in float hours. e.g. 12.125
	"""
##### sunset(jd, place)
	"""
        Sunset when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [sunset time as local time in float hours, local time string, and sunset julian number]
            e.g. [18.5,'18:30 PM',2450424.94]

	"""
##### moonrise(jd, place)
	"""
        Return local moonrise time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [Moonrise time as local time in float hours, local time string, and Moonrise julian number]
            e.g. [2.5,'02:30 AM',2450424.94]
	"""
##### moonset(jd, place)
	"""
        Return local moonset time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [Moonset time as local time in float hours, local time string, and Moonset julian number]
            e.g. [14.5,'14:30 PM',2450424.94]
	"""
##### tithi(jd, place,tithi\_index=1)
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
##### raasi(jd, place)
    """
        returns the raasi at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [raasi number, raasi ending time, raasi fraction left, 
                 next raasi number, next raasi ending time, next rasi fraction left]
          next raasi index and next raasi time is additionally returned if two raasis on same day 
          raasi number = [1..12]        
    """
##### nakshatra(jd, place)
    """
        returns the nakshathra at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [nakshatra number, nakshatra starting time, nakshatra ending time, nakshatra fraction left, 
                 next nakshatra number, next nakshatra starting time, next nakshatra ending time, next nakshatra fraction left]
          next nakshatra index and next nakshatra time is additionally returned if two nakshatras on same day 
          nakshatra number = [1..27]  Aswini to Revathi      
    """
##### yogam(jd, place)
    """
        returns the yogam at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [yogam number, yogam starting time, yogam ending time, yogam fraction left, 
                 next yogam number, next yogam starting time, next yogam ending time, next yogam fraction left]
          next yogam index and next yogam time is additionally returned if two yogams on same day 
          yogam index = [1..27]  1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
    """
##### karana(jd, place)
    """
        returns the karanam of the day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return karanam index, karanam starting time, karanam ending time, karanam fraction left 
          karanam index = [1..60]  1 = Kimstugna, 2 = Bava, ..., 60 = Naga
    """
##### vaara(jd)
	"""
      Weekday for given Julian day. 
      @param jd: Julian Day Number of the date/time
      @return: day of the date
        0 = Sunday, 1 = Monday,..., 6 = Saturday
	"""
##### lunar\_month(jd, place):
    """
        Returns lunar month and if it is adhika or not.
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [indian month index, whether leap month (adhika lunar_month) or not - boolean]
            1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna
            True if adhika lunar_month
    """
##### elapsed\_year(jd, maasa\_index)
    """
        returns Indian era/epoch year indices (kali year number, saka year and vikrama year numbers)
        @param jd: Julian Day Number of the date/time
        @param maasa_index: [1..12] (use jhora.panchanga.drik.lunar_month function to get this) 
        @return kali year number, vikrama year number, saka year number 
    """
    """ TODO - may not be right for dates before Kali yuaga - to be checked """
##### samvatsara(panchanga\_date,place,zodiac=None):
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
##### ritu(maasa\_index)
    """ 
    	returns ritu / season index. 
       @param maasa_index: [1..12] (use jhora.panchanga.drik.lunar_month function to get this) 
       @return: ritu index  0 = Vasanta,...,5 = Shishira
    """
##### gauri\_chogadiya(jd, place)
	"""
        Get end times of gauri chogadiya for the given julian day
        Chogadiya is 1/8th of daytime or nighttime practiced as time measure in North India 
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: end times of chogadiya as a list
	"""
##### trikalam(jd, place, option='raahu kaalam')
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
##### durmuhurtam(jd, place)
    """
        Get dhur muhurtham timing for the given julian day
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: start and end time of dhur muhurtham - as list e.g. [start_time, end_time]
    """
##### abhijit\_muhurta(jd, place)
    """
        Get Abhijit muhurta timing for the given julian day
        Abhijit muhurta is the 8th muhurta (middle one) of the 15 muhurtas during the day_duration (~12 hours)
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: start and end time of Abhijit muhurta - as list e.g. [start_time, end_time]
    """
##### planetary\_positions(jd, place)
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
##### \_bhaava\_madhya\_new(jd, place,bhava\_madhya\_method=const.bhaava\_madhya\_method)
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
        NOTE: Use this method to calculate house start/cusp/end
        For other purposes such as strength, aayu dasa etc use bhaava_madhya function.
        In future versions - both these functions will be merged into one.
    """
##### bhaava\_madhya(jd, place,bhava\_method=const.bhaava\_madhya\_method):
    """
        returns house longitudes
        @param jd: Julian Day number
        @param place: Place('name',latitude,longitude,timezone_hours)
        @param bhava_method:   
        bhava_method = 1 Swiss Ephemeres Ascendant Cusp Calculations
                     = 2 Sripati modifications from swiss calculations
        @return: [house longitudes as a list] # First element first house longitude and so on
    """
##### ascendant(jd, place, as\_string=False)
    """
        Compute Lagna (=ascendant) position/longitude at any given time & place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: [constellation of Lagna, longitude of lagna, Lagna nakshatra number, Lagna paadham number]
    """
##### dasavarga\_from\_long(longitude, sign\_division\_factor)
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
##### dhasavarga(jd, place, sign\_division\_factor)
    """
        Calculate planet positions for a given divisional chart index
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @param sign_division_factor: divisional chart index as below. 
          sign_division_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: 2D List of planet positions in the following format:
        [ [planet_index,[planet_raasi, planet_longitude],...]
        The planet index is in range [0..8]
        NOTE:DOES NOT INCLUDE ASCENDANT POSITION AND LONGITUDE
        TO GET ASCENDANT CALL: dasavarga_from_long()
    """
##### declination\_of\_planets(jd,place):
    """
        return declination of planets
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return: declination as a list
        first element for sun and last element for saturn
        
    """
##### solar\_upagraha\_longitudes(jd, upagraha, divisional\_chart\_factor=1)
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
##### upagraha\_longitude (dob, tob, place, planet\_index, divisional\_chart\_factor=1, upagraha\_part='middle')
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
          You can also use specific lambda functions.
              kaala_longitude(dob,tob,place,divisional_chart_factor)
              mrityu_longitude(dob,tob,place,divisional_chart_factor)
              artha_longitude(dob,tob,place,,divisional_chart_factor)
              yama_ghantaka_longitude(dob,tob,place,divisional_chart_factor)
              gulika_longitude(dob,tob,place,divisional_chart_factor)
              maandi_longitude(dob,tob,place,divisional_chart_factor)
      @return: [constellation of upagraha,upagraha_longitude within constellation]
      TODO: Upagraha longitudes are not matching with JHora for divisional charts
    """
##### special\_ascendant(jd, place, lagna\_rate\_factor=1.0, divisional\_chart\_factor=1)
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
##### pranapada\_lagna (jd, place, divisional\_chart\_factor=1)
    """
        Get constellation and longitude of pranapada Lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [pranapada lagna constellation, pranapada lagna's longitude within constellation]
    """
##### indu\_lagna (jd, place, divisional\_chart\_factor=1)
    """
        Get constellation and longitude of indu Lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [indu lagna constellation, indu lagna's longitude within constellation]
    """
##### kunda\_lagna (jd, place, divisional\_chart\_factor=1)
    """
        Get constellation and longitude of kunda Lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [kunda lagna constellation, kunda lagna's longitude within constellation]
    """
##### bhrigu\_bindhu\_lagna (jd, place, divisional\_chart\_factor=1)
    """
        Get constellation and longitude of bhrigu_bindhu Lagna
        @param jd: Julian day number
        @param place: Struct ('place name',latitude,longitude,time zone)
        @param divisional_chart_factor: divisional chart factor
          divisional_chart_factor = 2 => Hora, 3=>Drekana 4=>Chaturthamsa 5=>Panchamsa, 6=>Shashthamsa
          7=>Saptamsa, 8=>Ashtamsa, 9=>Navamsa, 10=>Dasamsa, 11=>Rudramsa, 12=>Dwadamsa, 16=>Shodamsa, 
          20=>Vimsamsa, 24=>Chaturvimsamsa, 27=>Nakshatramsa, 30=>Trisamsa, 40=>Khavedamsa, 
          45=>Akshavedamsa, 60=>Shastyamsa
        @return: [bhrigu_bindhu lagna constellation, bhrigu_bindhu lagna's longitude within constellation]
    """
##### sree\_lagna (jd, place, divisional\_chart\_factor=1)
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
##### tamil\_solar\_month\_and\_date(panchanga\_date,place)
    """
        Returns tamil month and date (e.g. Aadi 28 )
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: tamil_month_number, tamil_date_number
        i.e. [0..11, 1..32]
        Note: Tamil month is sankranti based solar month - not lunar month
    """ 
##### previous\_sankranti_date(panchanga\_date,place)
    """
        Get the previous sankranti date (sun entry to a raasi)
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: sankranti_date as Struct(y,m,d), sankranti time as float hours,tamil_month_number, tamil_date_number        
    """
##### next\_sankranti_date(panchanga\_date,place)
    """
        Get the next sankranti date (sun entry to a raasi)
        @param panchanga_date: Date Struct (year, month, day)
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return: sankranti_date as Struct(y,m,d), sankranti time as float hours,tamil_month_number, tamil_date_number        
    """
##### next\_solar\_date(jd\_at\_dob,place,years=1,months=1,sixty\_hours=1)
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
##### next\_solar\_eclipse(jd,place):
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
##### next\_solar\_eclipse(jd,place):
    """
        @param jd: Julian number 
        @param place: Place Struct ('place',latitude,longitude,timezone)
        returns next lunar eclipse date, percentage of eclipse etc
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
##### next\_conjunction\_of\_planet_pair(p1,p2,panchanga\_place:Place,panchanga\_start\_date:Date,direction=1,separation\_angle=0)
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
##### next\_planet\_entry\_date(planet,panchanga\_date,place,direction=1,increment\_days=1,precision=0.1,raasi=None)
    """
        get the date when a planet enters a zodiac
        @param planet: planet1 index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param direction: 1= next entry, -1 previous entry
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param precision: precision in degrees within which longitude entry whould be (default: 0.1 degrees)
        @param raasi: raasi at which planet should enter. 
            If raasi==None: gives entry to next constellation
            If raasi is specified [1..12] gives entry to specified constellation/raasi
        @return Julina day number of planet entry into zodiac
    """
##### next\_planet\_retrograde\_change\_date(planet,panchanga\_date,place,increment\_days=1,direction=1)
    """
        get the date when a retrograde planet changes its direction
        @param planet: planet index (0=Sun..8=Kethu)
        @param panchanga_date: Date struct (y,m,d)
        @param panchanga_place: Place struct ('place',latitude,longitude,timezone)
        @param increment_days: incremental steps in days algorithm to check for entry (Default=1 day)
        @param direction: 1= next direction change, -1 previous direction change
        @return Julian day number of planet changes retrogade direction
    """
##### \_nisheka\_time(jd,place):
    """
        @param jd: Julian number 
        @param place: Place Struct ('place',latitude,longitude,timezone)
        @return julian date number of nisheka time
        TODO: Formula needs to be checked
        Does not match JHora value (differs by upto 15 days)
    """
