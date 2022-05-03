Package Structure:

```
hora
   !- horoscope
        !- horoscope.py - horoscope class 
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
```
#### Arduhas - functions
```
from hora import const, utils
from hora.panchanga import panchanga
from hora.horoscope.chart.house import *
import swisseph as swe
```
##### bhava\_arudhas (house\_to\_planet_list)
    """
        gives Bhava Arudhas for each house from the chart
        @param house_to_planet_list: Enter chart information in the following format. 
        	For each house from Aries planet numbers separated by /
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
##### graha_arudhas (house\_to\_planet_list)
    """
        gives Graha Arudhas for each planet from the chart
        @param house_to_planet_list: Enter chart information in the following format. 
        	For each house from Aries planet numbers separated by /
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
#### Asktavarga - functions
```
from hora import const, utils
from hora.panchanga import panchanga
from hora.horoscope.chart.house import *
import swisseph as swe
```
##### get\_ashtaka\_varga (house\_to\_planaet\_chart)
    """
        get binna, samudhaya and prastara varga from the given horoscope planet positions
		 @param house_to_planet_chart: 1-D array [0..11] with planets in each raasi
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return: 
            binna_ashtaka_varga - 2-D List [0..7][0..7] 0=Sun..7=Lagnam
            samudhaya ashtaka varga - 1D List [0..11] 0=Aries 11=Pisces
            prastara ashtaka varga - 3D List [0..7][0..7][0..11]
    """
##### sodhaya\_pindas (binna\_ashtaka\_varga, house\_to\_planaet\_chart)
    """
        Get sodhaya pindas from binna ashtaka varga
        @param :binna_ashtaka_varga - 2-D List [0..7][0..7] 0=Sun..7=Lagnam - of BAV values
       	 NOTE: To pass binn ashtaka varga as parameter - you need to get it from get_ashtaka_varga function
		 @param house_to_planet_chart: 1-D array [0..11] with planets in each raasi
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return: raasi_pindas,graha_pindas,sodhya_pindas
                raasi_pindas : raasi pindas of planets 0=Sun to 6=Saturn [0..6]
                graha_pindas : graha pindas of planets 0=Sun to 6=Saturn [0..6]
                sidhaya_pindas : sodhaya pindas of planets 0=Sun to 6=Saturn [0..6]
    """
#### Charts - functions
```
from hora.panchanga import panchanga
from hora import const,utils
```
##### divisional\_chart (jd\_at\_dob, place\_as\_tuple, ayanamsa\_mode='Lahiri', divisional\_chart\_factor=1)
    """
        Get division chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
        		example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
        	1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[1,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.3 degrees
    """
##### planets\_in\_retrograde (planet\_positions)
    """
        Get the list of planets that are in retrograde - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in retrograde 
    """
##### planets\_in\_combustion (planet\_positions)
    """
        Get the list of planets that are in combustion - based on the planet positions returned by the divisional_chart()
        @param planet_positions: planet_positions returned by divisional_chart()
        @return list of planets in combustion 
    """
##### dhasavarga\_of\_planets (jd\_at\_dob, place\_as\_tuple, ayanamsa\_mode='Lahiri')
    """
        Get the count - in how many dhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Paarijaataamsa – 2, Uttamaamsa – 3, Gopuraamsa– 4, Simhaasanaamsa – 5,
            Paaraavataamsa – 6, Devalokaamsa – 7, Brahmalokamsa – 8, Airaavataamsa – 9,
            Sreedhaamaamsa – 10.
    """
##### shadvarga\_of\_planets(jd\_at\_dob, place\_as\_tuple, ayanamsa\_mode='Lahiri')
    """
        Get the count - in how many shad varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5,  Kundalaamsa – 6.
    """
##### sapthavarga\_of\_planets(jd\_at\_dob, place\_as\_tuple, ayanamsa_mode='Lahiri')
    """
        Get the count - in how many saptha varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Kimsukaamsa – 2, Vyanjanaamsa – 3, Chaamaraamsa – 4, Chatraamsa – 5, Kundalaamsa – 6, Mukutaamsa – 7.
    """
##### shodhasavarga\_of\_planets(jd\_at\_dob, place\_as\_tuple, ayanamsa\_mode='Lahiri')
    """
        Get the count - in how many shodhasa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
##### vimsamsavarga\_of\_planets(jd\_at\_dob, place\_as\_tuple, ayanamsa\_mode='Lahiri')
    """
        Get the count - in how many vimsamsa varga charts the planets are in their own raasi or exalted
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example panchanga.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return count for each planet - list - Example [3,4,5,6..] Sun in its own house in 3 charts, moon in 4 charts and so on.
            Special names of the count are as follows:
            Bhedakaamsa – 2, Kusumaamsa – 3, Nagapurushaamsa – 4, Kandukaamsa – 5,
            Keralaamsa – 6, Kalpavrikshaamsa – 7, Chandanavanaamsa – 8, Poornachandraamsa – 9, 
            Uchchaisravaamsa – 10, Dhanvantaryamsa – 11, Sooryakaantaamsa – 12,
            Vidrumaamsa – 13, Indraasanaamsa – 14, Golokaamsa – 15, Sree Vallabhaamsa – 16.
    """
#### House - functions
```
from hora.panchanga import panchanga
from hora import const,utils
```
##### Lambda functions
```
get_relative_house_of_planet = lambda from_house, planet_house: (planet_house + 12 -from_house) % 12 + 1
strong_signs_of_planet = lambda planet,strength=const._FRIEND: [h for h in range(12) if const.house_strengths_of_planets[planet][h]==strength]
""" Get All trikona aspects of the given raasi"""
trikona_aspects_of_the_raasi = lambda raasi: [(raasi)%12, (raasi+4)%12, (raasi+8)%12]
trines_of_the_raasi = lambda raasi: trikona_aspects_of_the_raasi(raasi)

functional_benefic_lord_houses = lambda asc_house: trines_of_the_raasi(asc_house)
functional_malefic_lord_houses = lambda asc_house: [(asc_house+2)%12,(asc_house+5)%12,(asc_house+10)%12]
functional_neutral_lord_houses = lambda asc_house: [(asc_house+1)%12,(asc_house+7)%12,(asc_house+11)%12]
dushthana_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+2)%12, (raasi+6)%12]
dushthanas_of_the_raasi = lambda raasi: dushthana_aspects_of_the_raasi(raasi)
chathusra_aspects_of_the_raasi = lambda raasi:[(raasi+2)%12, (raasi+4)%12]    
chathusras_of_the_raasi = lambda raasi: chathusra_aspects_of_the_raasi(raasi)
kendra_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+3)%12, (raasi+6)%12,(raasi+9)%12]
quadrants_of_the_raasi = lambda raasi:kendra_aspects_of_the_raasi(raasi)
upachaya_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+3)%12, (raasi+7)%12,(raasi+8)%12]    
upachayas_of_the_raasi = lambda raasi: upachaya_aspects_of_the_raasi(raasi)
```
##### is\_yoga\_kaaraka (asc\_house, planet, planet\_house):
    """
        Check if a planet is yoga kaaraka
        @param asc_house: Raasi index of Lagnam (0=Aries, 11=Pisces)
        @param planet: Index of Planet  (0=Sun, 8=Kethu)
        @param planet_house: Raasi index of where planet is (0=Aries, 11=Pisces)
        @return: True/False whether planet is yoga kaaraka or not
    """
##### trikonas()
    """ Get All trikonas of all houses """
##### dushthanas()
    """ Get All dushthanas of all houses """
##### chathusras()
    """ Get All chathusras of all houses """
##### upachayas()
    """ Get All upachayas of all houses """
##### quadrants():
    """ 
    	Get All quadrants of all houses
    	Same as kendras() function 
    """
##### aspected\_kendras\_of\_raasi (raasi, reverse\_direction=False)
    """ 
        @param raasi: 0 .. 11
        @param reverse_direction = True (default):  
        	NOTE: !!! use reverse_direction=True only for some dhasa-bukthi such as drig dhasa !!!
        @return: aspected house numbers [1,4,7,10] with respect to the raasi
        	NOTE: !!! Kendras return as 1..12 instead of 0..11. !!!
    """
##### chara\_karakas (jd, place, divisional\_chart\_factor = 1)
    """
        get chara karakas for a dasa varga chart
        @param jd - juliday number for date/time of birth
        	use utils.julian_day_number() function
        @param place: panchanga.place struct(place,lat,long,timezone)
        @param divisional_chart_factor: 1=Rasi, 2=Hora...,9=Navamsa etc
        	see const.division_chart_factors
        @return: chara karaka for all planets as a list. First element is Sun
    """
##### graha\_drishti\_from\_chart (house\_to\_planet\_dict, separator='/')
    """
        get graha drishti from the chart positions of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param separator: separator character used separate planets in a house
        @return: arp, ahp, app
            Each tuple item is a 2D List
            arp = planets' graha drishti on raasis. Example: [[0,1,],...]] Sun has graha drishti in Aries and Tauras
            ahp = planets' graha drishti on houses. Example: [[0,1,],...]] Sun has graha drishti in 1st and 2nd houses
            app = planets' graha drishti on planets. Example: [[1,2,],...]] Sun has graha drishti on Moon and Mars
    """
##### raasi\_drishti\_from\_chart (house\_to\_planet\_dict, separator='/')
    """
        get raasi drishti from the chart positions of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param separator: separator character used separate planets in a house
        @return: arp, ahp, app
            Each tuple item is a 2D List
            arp = raasis' graha drishti on raasis. Example: [[1,2,],...]] Aries has raasi drishti in Tauras and Gemini
            ahp = raasis' graha drishti on houses. Example: [[1,2,],...]] 1st house/Lagnam has raasi drishti in 2nd and 3rd houses
            app = raasis' graha drishti on planets. Example: [[1,2,],...]] Aries has raasi drishti on Moon and Mars
    """
##### get\_argala (house\_to\_planet\_dict, separator='\n')
    """
        Get argala and Virodhargala from the chart
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param separator: separator character used separate planets in a house
        @return argala,virodhargala
            argala = list of houses each planet causing argala - 2D List [ [0,2]..]] Sun causing argala in Ar and Ge
            virodhargala = list of houses each planet causing virodhargala - 2D List [ [0,2]..]] Sun causing virodhargala in Ar and Ge
    """
##### stronger\_co\_lord (house\_to\_planet\_dict, planet1=swe.SATURN, planet2=swe.RAHU)
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1 and planet2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
        @return stronger of planet1 and planet2
            Stronger of Rahu/Saturn or Ketu/Mar is returned
    """
##### stronger\_rasi(house\_to\_planet\_dict, rasi1, rasi2)
    """
        To find stronger rasi between rasi1 and rasi2 
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param rasi1: [ 0,,11] 0 = Ar and 11 = Pi 
        @param rasi2: [ 0,,11] 0 = Ar and 11 = Pi
        @return  return stringer raasi (raasi index 0 to 11, 0 = Ar, 11=Pi) 
    """
#### Yoga - functions
```
import swisseph as swe
import json
from hora import const,utils
from hora.horoscope import horoscope
from hora.panchanga import panchanga
from hora.horoscope.chart import house, charts
from hora.horoscope.transit import tajaka
```
##### Lambda functions
```
quandrants_of_the_house = lambda raasi: house.quadrants_of_the_raasi(raasi) 
```
##### get\_yoga\_details\_for\_all\_charts (jd, place, language='en')
    """
        Get all the yoga information that are present in the divisional charts for a given julian day and place
        @param jd: Julian day number
        @param place: struct (plave name, latitude, longitude, timezone)
        @param language: two letter language code (en, hi, ka, ta, te)
        @return: returns a 2D List of yoga_name, yoga_details
            yoga_name in language
            yoga_details: [chart_ID, yoga_name, yoga_desription, yoga_benfits] 
    """
##### get\_yoga\_details (jd, place, divisional\_chart\_factor=1, language='en')
    """
        Get all the yoga information that are present in the requested divisional charts for a given julian day and place
        @param jd: Julian day number
        @param place: struct (plave name, latitude, longitude, timezone)
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @param language: two letter language code (en, hi, ka, ta, te)
        @return: returns a 2D List of yoga_name, yoga_details
            yoga_name in language
            yoga_details: [chart_ID, yoga_name, yoga_desription, yoga_benfits] 
    """
##### Supported 95 yogas are given below - calling each of them check and return True or False if yoga is present
```
vesi_yoga(h_to_p,p_to_h,asc_house)
vosi_yoga(h_to_p,p_to_h,asc_house)
ubhayachara_yoga(h_to_p,p_to_h,asc_house)
nipuna_yoga(h_to_p,p_to_h,asc_house)
sunaphaa_yoga(h_to_p,p_to_h,asc_house)
anaphaa_yoga(h_to_p,p_to_h,asc_house)
duradhara_yoga(h_to_p,p_to_h,asc_house)
kemadruma_yoga(h_to_p,p_to_h,asc_house)
chandra_mangala_yoga(h_to_p,p_to_h,asc_house)
adhi_yoga(h_to_p,p_to_h,asc_house)
ruchaka_yoga(h_to_p,p_to_h,asc_house)
bhadra_yoga(h_to_p,p_to_h,asc_house)
sasa_yoga(h_to_p,p_to_h,asc_house)
maalavya_yoga(h_to_p,p_to_h,asc_house)
hamsa_yoga(h_to_p,p_to_h,asc_house)
rajju_yoga(h_to_p,p_to_h,asc_house)
musala_yoga(h_to_p,p_to_h,asc_house)
nala_yoga(h_to_p,p_to_h,asc_house)
maalaa_yoga(h_to_p,p_to_h,asc_house)
sarpa_yoga(h_to_p,p_to_h,asc_house)
gadaa_yoga(h_to_p,p_to_h,asc_house)
sakata_yoga(h_to_p,p_to_h,asc_house)
vihanga_yoga(h_to_p,p_to_h,asc_house)
sringaataka_yoga(h_to_p,p_to_h,asc_house)
hala_yoga(h_to_p,p_to_h,asc_house)
vajra_yoga(h_to_p,p_to_h,asc_house)
yava_yoga(h_to_p,p_to_h,asc_house)
kamala_yoga(h_to_p,p_to_h,asc_house)
vaapi_yoga(h_to_p,p_to_h,asc_house)
yoopa_yoga(h_to_p,p_to_h,asc_house)
sara_yoga(h_to_p,p_to_h,asc_house)
sakti_yoga(h_to_p,p_to_h,asc_house)
danda_yoga(h_to_p,p_to_h,asc_house)
naukaa_yoga(h_to_p,p_to_h,asc_house)
koota_yoga(h_to_p,p_to_h,asc_house)
chatra_yoga(h_to_p,p_to_h,asc_house)
chaapa_yoga(h_to_p,p_to_h,asc_house)
ardha_chandra_yoga(h_to_p,p_to_h,asc_house)
chakra_yoga(h_to_p,p_to_h,asc_house)
samudra_yoga(h_to_p,p_to_h,asc_house)
veenaa_yoga(h_to_p,p_to_h,asc_house)
daama_yoga(h_to_p,p_to_h,asc_house)
paasa_yoga(h_to_p,p_to_h,asc_house)
kedaara_yoga(h_to_p,p_to_h,asc_house)
soola_yoga(h_to_p,p_to_h,asc_house)
yuga_yoga(h_to_p,p_to_h,asc_house)
gola_yoga(h_to_p,p_to_h,asc_house)
subha_yoga(h_to_p,p_to_h,asc_house)
asubha_yoga(h_to_p,p_to_h,asc_house)
gaja_kesari_yoga(h_to_p,p_to_h,asc_house)
guru_mangala_yoga(h_to_p,p_to_h,asc_house)
amala_yoga(h_to_p,p_to_h,asc_house)
parvata_yoga(h_to_p,p_to_h,asc_house)    
kaahala_yoga(h_to_p,p_to_h,asc_house)
chaamara_yoga(h_to_p,p_to_h,asc_house)
sankha_yoga(h_to_p,p_to_h,asc_house)
bheri_yoga(h_to_p,p_to_h,asc_house)
mridanga_yoga(h_to_p,p_to_h,asc_house)
sreenaatha_yoga(h_to_p,p_to_h,asc_house)
matsya_yoga(h_to_p,p_to_h,asc_house)
koorma_yoga(h_to_p,p_to_h,asc_house)
khadga_yoga(h_to_p,p_to_h,asc_house)
kusuma_yoga(h_to_p,p_to_h,asc_house)
kalaanidhi_yoga(h_to_p,p_to_h,asc_house)
kalpadruma_yoga(h_to_p,p_to_h,asc_house)
lagnaadhi_yoga(h_to_p,p_to_h,asc_house)
hari_yoga(h_to_p,p_to_h,asc_house)
hara_yoga(h_to_p,p_to_h,asc_house)
brahma_yoga(h_to_p,p_to_h,asc_house)
vishnu_yoga(h_to_p,p_to_h,asc_house)
siva_yoga(h_to_p,p_to_h,asc_house)
trilochana_yoga(h_to_p,p_to_h,asc_house)
gouri_yoga(h_to_p,p_to_h,asc_house)
chandikaa_yoga(h_to_p,p_to_h,asc_house)
lakshmi_yoga(h_to_p,p_to_h,asc_house)
saarada_yoga(h_to_p,p_to_h,asc_house)
bhaarathi_yoga(h_to_p,p_to_h,asc_house)
saraswathi_yoga(h_to_p,p_to_h,asc_house)
amsaavatara_yoga(h_to_p,p_to_h,asc_house)
devendra_yoga(h_to_p,p_to_h,asc_house)
indra_yoga(h_to_p,p_to_h,asc_house)
ravi_yoga(h_to_p,p_to_h,asc_house)
bhaaskara_yoga(h_to_p,p_to_h,asc_house)
kulavardhana_yoga(h_to_p,p_to_h,asc_house)
vasumati_yoga(h_to_p,p_to_h,asc_house)
gandharva_yoga(h_to_p,p_to_h,asc_house)
go_yoga(h_to_p,p_to_h,asc_house)
vidyut_yoga(h_to_p,p_to_h,asc_house)
chapa_yoga(h_to_p,p_to_h,asc_house)
pushkala_yoga(h_to_p,p_to_h,asc_house)
makuta_yoga(h_to_p,p_to_h,asc_house)
jaya_yoga(h_to_p,p_to_h,asc_house)
harsha_yoga(h_to_p,p_to_h,asc_house)
sarala_yoga(h_to_p,p_to_h,asc_house)
vimala_yoga(h_to_p,p_to_h,asc_house)
```
#### Raja Yoga - functions
```
import itertools
from hora import const,utils
from hora.horoscope.chart import house
```
##### Lambda functions
```
lords_of_quadrants = lambda raasi:[const.house_owners[h] for h in house.quadrants_of_the_raasi(raasi)]
lords_of_trines = lambda raasi:[const.house_owners[h] for h in house.trines_of_the_raasi(raasi)]
```
##### get\_raja\_yoga\_pairs (house\_to\_planet\_list)
    """
       To get raja yoga planet pairs from house to planet list
       NOTE: !!! Strength of the pairs are not checked !!!
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return 2D List of raja yoga planet pairs
          Example: [[0,2],[3,6]] : Tow raja yoga pairs [Sun,Mars] and [Mercury,Saturn]
    """
##### dharma\_karmadhipati\_yoga (p\_to\_h, raja\_yoga\_planet1, raja\_yoga\_planet2)
    """ 
        Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords
        of dharma sthana (9th) and karma sthana (10th) form a raja yoga 
        @param p_to_h: planet_to_house dictionary Example: {0:1,1:2,...'L':11,..} Sun in Ar, Moon in Ta, Lagnam in Pi
        @param raja_yoga_planet1: Planet index for first raja yoga planet  [0 to 6] Rahu/Kethu/Lagnam not supported
        @param raja_yoga_planet2: Planet index for second raja yoga planet [0 to 6] Rahu/Kethu/Lagnam not supported
        @return: True/False = True = dharma karmadhipati yoga is present
    """
###### vipareetha\_raja\_yoga (p\_to\_h, raja\_yoga\_planet1, raja\_yoga\_planet2)
    """
        Checks if given two raja yoga planets also for vipareetha raja yoga/
        Also returns the sub type of vipareetha raja yoga
            Harsh Raja Yoga, Saral Raja Yoga and Vimal Raja Yoga
        Vipareeta Raaja Yoga: The 6th, 8th and 12th houses are known as trik sthanas or
        dusthanas (bad houses). If their lords occupies dusthanas or conjoin dusthanas
        @param p_to_h: planet_to_house dictionary Example: {0:1,1:2,...'L':11,..} Sun in Ar, Moon in Ta, Lagnam in Pi
        @param raja_yoga_planet1: Planet index for first raja yoga planet  [0 to 6] Rahu/Kethu/Lagnam not supported
        @param raja_yoga_planet2: Planet index for second raja yoga planet [0 to 6] Rahu/Kethu/Lagnam not supported
        return [Boolean, Sub_type]
         Example: [True,'Harsh Raja Yoga']
    """
##### neecha\_bhanga\_raja\_yoga (house\_to\_planet\_list, raja\_yoga\_planet1, raja\_yoga\_planet2)
    """
        Checks if given raja yoga pais form neecha bhanga raja yoga
        NOTE: Checks only the first 3 conditions below. 4 and 5 to be done in future version
        1. If the lord of the sign occupied by a weak or debilitated planet is exalted or is in Kendra from Moon. 
            Ex, If Jupiter is debilitated in Capricorn and if Saturn is exalted and placed in Kendra from moon 
        2. If the debilitated planet is conjunct with the Exalted Planet
        3. If the debilitated planet is aspected by the master of that sign. 
            Ex, If Sun is debilitated in Libra and it is aspect by Venus with 7th aspect.
        4. If the debilitated planet is Exalted in Navamsa Chart.
        5. The planet which gets exalted in the sign where a debilitated planet is placed is in a Kendra from the Lagna or the Moon. 
            Ex, If Sun is debilitated in the birth chart in Libra and Saturn which gets exalted in Libra is placed in Kendra from Lagna or Moon.
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raja_yoga_planet1: Planet index for first raja yoga planet  [0 to 6] Rahu/Kethu/Lagnam not supported
        @param raja_yoga_planet2: Planet index for second raja yoga planet [0 to 6] Rahu/Kethu/Lagnam not supported
        @return: True/False = True = neecha bhanga raja yoga is present
    """
