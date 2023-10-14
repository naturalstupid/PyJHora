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
#### Vimsottari Dhasa - functions
##### Import
```
import datetime
from collections import OrderedDict as Dict
import swisseph as swe
from hora import const
from hora.panchanga import panchanga
```
##### Lambda functions
```
vimsottari_adhipati = lambda nak: const.vimsottari_adhipati_list[nak % (len(const.vimsottari_adhipati_list))]
```
##### get\_vimsottari\_dhasa\_bhukthi (jd, place)
    """
        provides Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """

#### Ashtottari Dhasa - functions
	"""
		Calculates Ashtottari (=120) Dasha-bhukthi-antara-sukshma-prana
	"""
##### Import
```
import swisseph as swe
from collections import OrderedDict as Dict
import hora.panchanga
import datetime
```
##### Lambda functions
```
sidereal_year = panchanga.sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = 108

""" 
    {ashtottari adhipati:[(starting_star_number,ending_star_number),dasa_length]} 
        ashtottari longitude range: (starting_star_number-1) * 360/27 TO (ending_star_number) * 360/27
        Example: 66.67 to 120.00 = 53 deg 20 min range
"""
ashtottari_adhipathi_list = [swe.SUN,swe.MOON,swe.MARS,swe.MERCURY,swe.SATURN,swe.JUPITER,swe.RAHU,swe.VENUS]
ashtottari_adhipathi_dict = {swe.SUN:[(6,9),6],swe.MOON:[(10,12),15],swe.MARS:[(13,16),8],swe.MERCURY:[(17,19),17],
                             swe.SATURN:[(20,22),10],swe.JUPITER:[(23,25),19],swe.RAHU:[(26,2),12],swe.VENUS:[(3,5),21]}
```
##### get\_ashtottari\_dhasa\_bhukthi(jd, place)
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Narayana Dhasa - functions
##### Import
```
from hora import const,utils
from hora.horoscope.chart import charts
from hora.horoscope.chart.house import *
import swisseph as swe
from hora.panchanga import panchanga
```
##### narayana\_dhasa\_for\_divisional\_chart (jd\_at\_dob, place, dob, years\_from\_dob=0, divisional\_chart\_factor=1)
    """
        calculate narayana dhasa for divisional charts / annual charts
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param jd_at_dob: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @param years_from_dob: # years of from year of birth
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """

#### Lagna Kendraadhi Raasi Dhasa (Moola)  - functions
##### Import
```
from hora import const, utils
from hora.horoscope.chart.house import *
from hora.horoscope.dhasa import narayana
```
##### moola\_dhasa (chart, dob)
    """
        calculate Lagna Kendraadhi dhasa aka Moola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """

#### Sudasa Dhasa - functions
##### Import
```
from hora import const,utils
from hora.panchanga import panchanga
from hora.horoscope.chart import house
from hora.horoscope.dhasa import narayana
import swisseph as swe
import datetime
```
##### sudasa\_dhasa (chart, sree\_lagna\_house, sree\_lagna\_longitude, dob)
    """
        calculate Sudasa Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param sree_lagna_house:Raasi index where sree lagna is
        @param sree_lagna_longitude: Longitude of Sree Lagna 
            Note: one can get sree lagna information from panchanga.sree_lagna()
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """

#### Drig Dhasa - functions
##### Import
```
from hora import const,utils
from hora.panchanga import panchanga
from hora.horoscope.chart import house
from hora.horoscope.dhasa import narayana
import swisseph as swe
import datetime
```
##### drig\_dhasa(chart, dob)
    """
        computes drig dhasa from the chart
        @param chart: chart list 1-D. Format ['1/2','3/L',...,'',5/6/7','9','0'] # 12 houses with planets and Lagnam
        @param dob: tuple of date of birth format: (year,month,day)
        @return: list of drig dhasa from date of birth 
          Format: [ [dhasa_lord, dhasa_start_date, dhasa_end_date, [bhukthi_lord1, bhukthi_lord2...], dhasa_duration],...]
          Example: [[2, '1912-1-1', '1916-1-1', [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1], 4], 
                    [5, '1916-1-1', '1927-1-1', [5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6], 11], ...]]
    """
#### Nirayana Shoola Dhasa - functions
##### Import
```
from hora import const, utils
from hora.horoscope.chart.house import *
from hora.horoscope.dhasa import narayana
```
##### nirayana\_shoola\_dhasa (chart, dob)
    """
        calculate Nirayana Shoola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """

#### Shoola Dhasa - functions
##### Import
```
from hora import const, utils
from hora.horoscope.chart.house import *
from hora.horoscope.dhasa import narayana
```
##### shoola\_dhasa(chart, dob)
    """
        calculate Shoola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """

#### Kalachakra Dhasa Functions
##### Imports
```
import numpy as np
from hora import const
from hora.panchanga import panchanga
from hora.horoscope.chart import house
```
##### kalachakra\_dhasa(lunar\_longitude, dob)
    """
        Kalachara Dhasa calculation
        @param lunar_longitude: Longitude of moon at the time of date/time of birth as float
        	Note: one can get this from panchanga.lunar_longitude()
        @param dob: date of birth as tuple (year,month,day)
        @return: list of [dhasa_rasi,dhasa_rasi_start_date, dhasa_rasi_end_date,[abtadhasa_rasis],dhasa_rasi_duration]
        Example: [[7, '1946-12-2', '1955-12-2', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 9], [8, '1955-12-2', '1964-12-2', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 9], ...]
    """

#### Sudharsana Chakra Dhasa - functions
##### Import
```
from hora.horoscope.chart import charts
from hora import const, utils
from hora.panchanga import panchanga
```
##### sudharsana\_chakra\_dhasa\_for\_divisional\_chart (jd\_at\_dob, place, dob, years\_from\_dob=0, divisional\_chart\_factor=1)
    """
        calculate sudharsana chakra dhasa for divisional charts / annual charts
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param jd_at_dob: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @param years_from_dob: # years of from year of birth
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @return: [lagna_periods,moon_periods,sun_periods]
          Each dhasa period will have the following format:
          [planet index,(dhasa_start_year, month, date,longitude),dhasa duration],...
          [0, (1987, 10, 31, 15.388383474200964), 2.5], [1, (1987, 11, 3, 4.348383475095034), 2.5],....
          
    """
#### Mudda (Varsha Vimsottari) - functions
##### Import
```
import datetime
from collections import OrderedDict as Dict
import swisseph as swe
from hora import const
from hora.panchanga import panchanga
from hora.horoscope.chart import charts
from hora.horoscope.dhasa import vimsottari
```
##### Lambda functions
```
varsha_vimsottari_adhipati = lambda nak: const.varsha_vimsottari_adhipati_list[nak % (len(const.varsha_vimsottari_adhipati_list))]
```
##### varsha\_vimsottari\_dhasa\_bhukthi (jd, place, years)
    """
        Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
        @param jd: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param years: # years of from year of birth
        @return: 2D list of [ (dhasa_lord,Bhukthi_lord,bhukthi_start date, bhukthi_duraation),...
          Example: [(7, 7, '1993-06-03', 8.22), (7, 4, '1993-06-11', 7.31), ...]
    """
#### Patyayini - functions
##### Import
```
from hora import const, utils
from hora.panchanga import panchanga
from hora.horoscope.chart import charts
```
##### patyayini\_dhasa (jd\_years, place, ayanamsa\_mode='Lahiri', divisional\_chart\_factor=1)
    """
        Compute Patyaayini Dhasa
        Should be used for Tajaka Annual charts
        @param jd_years:Julian day number for Tajaka Annual date/time
        @param place: panchanga.Place struct tuple of ('Place',latitude,longitude,time_zone_offset)
        @param ayanamsa_mode: Default = 'Lahiri'
        @param divisional_chart_factor: Default = 1 (Raasi) - See const.division_chart_factors for other possible values
        @return patyayini dhasa values as a list [planet, dhasa_duration in days]
        Example: [[5, (1993, 6, 26), 24.9], [3, (1993, 8, 13), 48.1], [1, (1993, 8, 14), 0.57],...]]
    """
