#### Arduhas - functions to calculate Bhava and Graha Arudhas from Planet Positions or from Chart
```
from hora import const, utils
from hora.horoscope.chart.house import *
```
##### bhava\_arudhas\_from\_planet\_positions (planet_positions)
    """
        gives Bhava Arudhas for each house from the planet positions
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
##### graha\_arudhas\_from\_planet\_positions (planet_positions)
    """
        gives Graha Arudhas for each planet from the planet positions
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
##### bhava\_arudhas (house\_to\_planet_list)
    """
        gives Bhava Arudhas for each house from the chart
        @param house_to_planet_list: Enter chart information in the following format. 
        	For each house from Aries planet numbers separated by /
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
##### graha\_arudhas (house\_to\_planet_list)
    """
        gives Graha Arudhas for each planet from the chart
        @param house_to_planet_list: Enter chart information in the following format. 
        	For each house from Aries planet numbers separated by /
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
#### Asktakavarga - functions to get binna, samudhaya and prastara varga from the given horoscope planet positions/chart
```
import numpy as np
from hora import const, utils
```
##### get\_ashtaka\_varga (house\_to\_planaet\_chart)
    """
        get binna, samudhaya and prastara varga from the given horoscope chart
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
from hora.panchanga import drik
from hora import const,utils
from hora.horoscope.chart import house
```
##### rasi\_chart(jd\_at\_dob,place\_as\_tuple,ayanamsa\_mode=const.\_DEFAULT\_AYANAMSA\_MODE,years=1,months=1,sixty_hours=1)
    """
        Get Rasi chart - D1 Chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:'Lahiri' - See const.available_ayanamsa_modes for more options
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### hora\_chart(planet\_positions\_in\_rasi,pvn\_rao\_method=True):
    """ 
    	Hora Chart - D2 Chart
    	@param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """

##### drekkana\_chart(planet\_positions\_in\_rasi):
    """ 
        Drekkana Chart - D3 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### chaturthamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Chaturthamsa Chart - D4 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### panchamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Panchamsa Chart - D5 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### shashthamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Shashthamsa Chart - D6 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### saptamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Saptamsa Chart - D7 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### ashtamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Ashtamsa Chart - D8 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### navamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Navamsa Chart - D9 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### dasamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Dasamsa Chart - D10 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### rudramsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Rudramsa Chart - D11 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### dwadasamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Dwadasamsa Chart - D12 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### shodasamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Shodasamsa Chart - D16 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### vimsamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Vimsamsa Chart - D20 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### chaturvimsamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Chathur Vimsamsa Chart - D24 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### nakshatramsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Nakshatramsa Chart - D27 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### trimsamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Trimsamsa Chart - D30 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### khavedamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Khavedamsa Chart - D40 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### akshavedamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Akshavedamsa Chart - D45 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### shashtyamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Shashtyamsa Chart - D60 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### nava\_navamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Nava Navamsa Chart - D81 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### ashtotharamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Ashtotharamsa Chart - D108 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### dwadas\_dwadasamsa\_chart(planet\_positions\_in\_rasi):
    """ 
        Dwadas Dwadasamsa Chart - D144 Chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
    """
##### divisional\_chart (jd\_at\_dob, place\_as\_tuple, ayanamsa\_mode='Lahiri', divisional\_chart\_factor=1,                  years=1,months=1,sixty\_hours=1):
    """
        Get divisional/varga chart
        @param jd_at_dob:Julian day number at the date/time of birth
            Note: It can be obtained from utils.julian_day_number(...)
        @param place_as_tuple - panjanga.place format
                example drik.place('Chennai,IN',13.0,78.0,+5.5)
        @param ayanamsa_mode Default:const._DEFAULT_AYANAMSA_MODE - See const.available_ayanamsa_modes for more options
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @return: planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
                First element is that of Lagnam
            Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]] Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
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
##### varnada\_lagna(dob,tob,place):
    """
        Get Varnada Lagna
        @param: dob : date of birth as tuple (year,month,day)
        @param: tob : time of birth as tuple (hours, minutes, seconds)
        @param: place: Place as tuple (place_name,latitude,longitude,timezone)
        @return varna_lagna_rasi, varnada_lagna_longitude 
    """

#### House - functions
```
from hora import const, utils
from hora.panchanga import drik
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
##### chara\_karakas (planet\_positions)
    """
        get chara karakas for a dasa varga chart
        @param planet_positions_in_rasi: Rasi chart planet_positions list in the format [[planet,(raasi,planet_longitude)],...]]. First element is that of Lagnam
            Example: [ ['L',(0,13.4)],[0,(11,12.7)],...]] Lagnam in Aries 13.4 degrees, Sun in Taurus 12.7 degrees
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
##### graha\_drishti\_of\_the\_planet(house\_to\_planet_dict,planet,separator='/'):
    """
        Get graha drishti of a planet on other planets. 
            returns list of planets on which given planet has graha drishti
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet: The index of the planet for which graha drishti is sought (0=Sun, 9-Ketu, 'L'=Lagnam) 
        @param separator: separator character used separate planets in a house
        @return: graha drishti of the planet as a list of planets
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
##### raasi\_drishti\_of\_the\_planet (house\_to\_planet\_dict, planet, separator='/')
    """
        get raasi drishti from the chart positions of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet - planet for which rasi drishti is required
        @param separator: separator character used separate planets in a house
        @return: arp, ahp, app
            Each tuple item is a 2D List
            arp = raasis' graha drishti on raasis. Example: [[1,2,],...]] Aries has raasi drishti in Tauras and Gemini
            ahp = raasis' graha drishti on houses. Example: [[1,2,],...]] 1st house/Lagnam has raasi drishti in 2nd and 3rd houses
            app = raasis' graha drishti on planets. Example: [[1,2,],...]] Aries has raasi drishti on Moon and Mars
    """
##### aspected\_planets\_of\_the\_raasi(house\_to\_planet\_dict,raasi,separator='/'):
    """
        get planets, from the raasi drishti from the chart, that has drishti on the given raasi
    """
##### aspected\_houses\_of\_the\_raasi(house\_to\_planet\_dict,raasi,separator='/'):
    """
        get aspected houses of the given rasi from the chart
    """
##### aspected\_raasis\_of\_the\_raasi(house\_to\_planet\_dict,raasi,separator='/'):
    """
        get aspected raasis of the given rasi from the chart
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
##### stronger\_planet\_from\_planet\_positions(planet\_positions,planet1=const.\_SATURN,planet2=7,check\_during\_dhasa=False):
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @param planet1 and planet2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
          Default: planet1=6 (Saturn) and planet2=7 (Rahu)
        @param check_during_dhasa True/False. Set this to True if checking for dhasa-bhukthi
        @return stronger of planet1 and planet2
            Stronger of Rahu/Saturn or Ketu/Mars is returned
    """
##### stronger\_planet(house\_to\_planet\_dict,planet1=const._SATURN,planet2=7,check\_during\_dhasa=False,planet1\_longitude=None,planet2\_longitude=None):
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1 and planet2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
          Default: planet1=6 (Saturn) and planet2=7 (Rahu)
        @return stronger of planet1 and planet2
    	  TODO: To implement Rule 5(b) for Arudhas. For that we need planet longitudes 
    """
##### stronger\_rasi\_from\_planet\_positions(planet\_positions,rasi1,rasi2):
    """
        To find stronger rasi  
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @param rasi1 and rasi2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
          Default: planet1=6 (Saturn) and planet2=7 (Rahu)
        @return stronger of rasi1 and rasi2
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
##### natural\_friends\_of\_planets(house\_to\_planet\_list=None):
    """
        Take the moolatrikona of the planet. Lord of the rasi where it is exalted is its friend. 
        Lords of 2nd, 4th, 5th, 8th, 9th and 12th rasis from it are also its natural friends.
    """
##### natural\_neutral\_of\_planets(house\_to\_planet\_list=None):
##### natural\_enemies\_of\_planets(house\_to\_planet\_list=None):
##### house\_owner\_from\_planet\_positions(planet\_positions,sign,check\_during\_dhasa=False)
##### house\_owner(house\_planet\_to\_list,sign)
##### marakas\_from\_planet_positions(planet\_positions):
    """
        If a malefic planet powerfully conjoins or aspects, using graha drishti, 
        the 2nd and 7th houses or their lords, then it qualifies as a maraka graha.
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @return: maraka graha/planets as a list
    """
##### marakas(house\_to\_planet\_list):
    """
        If a malefic planet powerfully conjoins or aspects, using graha drishti, 
        the 2nd and 7th houses or their lords, then it qualifies as a maraka graha.
        @param house_to_planet_dict: list of raasi with planet ids in them
          	Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and 
          	last is Pisces
        @return: maraka graha/planets as a list
    """
##### rudra\_based\_on\_planet\_positions(dob,tob,place,divisional\_chart\_factor=1):
	"""
		Get Rudra
	"""
##### brahma(planet\_positions):
	"""	
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @return: Brahma Planet
   """ 
##### maheshwara(dob,tob,place,divisional\_chart\_factor=1):
	"""
		Get Maheshwara Planet
	"""
##### longevity(dob,tob,place,divisional\_chart\_factor=1):
	"""
		Get Longevity in years
	"""
#### Yoga - functions
```
import json
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house
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
vesi_yoga_from_planet_positions(planet_positions)
vosi_yoga_from_planet_positions(planet_positions)
ubhayachara_from_planet_positions(planet_positions)
nipuna_yoga_from_planet_positions(planet_positions)
sunaphaa_yoga_from_planet_positions(planet_positions)
anaphaa_yoga_from_planet_positions(planet_positions)
duradhara_yoga_from_planet_positions(planet_positions)
kemadruma_yoga_from_planet_positions(planet_positions)
chandra_mangala_yoga_from_planet_positions(planet_positions)
adhi_yoga_from_planet_positions(planet_positions)
ruchaka_yoga_from_planet_positions(planet_positions)
bhadra_yoga_from_planet_positions(planet_positions)
sasa_yoga_from_planet_positions(planet_positions)
maalavya_yoga_from_planet_positions(planet_positions)
hamsa_yoga_from_planet_positions(planet_positions)
rajju_yoga_from_planet_positions(planet_positions)
musala_yoga_from_planet_positions(planet_positions)
nala_yoga_from_planet_positions(planet_positions)
maalaa_yoga_from_planet_positions(planet_positions)
sarpa_yoga_from_planet_positions(planet_positions)
gadaa_yoga_from_planet_positions(planet_positions)
sakata_yoga_from_planet_positions(planet_positions)
vihanga_yoga_from_planet_positions(planet_positions)
sringaataka_yoga_from_planet_positions(planet_positions)
hala_yoga_from_planet_positions(planet_positions)
vajra_yoga_from_planet_positions(planet_positions)
yava_yoga_from_planet_positions(planet_positions)
kamala_yoga_from_planet_positions(planet_positions)
vaapi_yoga_from_planet_positions(planet_positions)
yoopa_yoga_from_planet_positions(planet_positions)
sara_yoga_from_planet_positions(planet_positions)
sakti_yoga_from_planet_positions(planet_positions)
danda_yoga_from_planet_positions(planet_positions)
naukaa_yoga_from_planet_positions(planet_positions)
koota_yoga_from_planet_positions(planet_positions)
chatra_yoga_from_planet_positions(planet_positions)
chaapa_yoga_from_planet_positions(planet_positions)
ardha_chandra_yoga_from_planet_positions(planet_positions)
chakra_yoga_from_planet_positions(planet_positions)
samudra_yoga_from_planet_positions(planet_positions)
veenaa_yoga_from_planet_positions(planet_positions)
daama_yoga_from_planet_positions(planet_positions)
paasa_yoga_from_planet_positions(planet_positions)
kedaara_yoga_from_planet_positions(planet_positions)
soola_yoga_from_planet_positions(planet_positions)
yuga_yoga_from_planet_positions(planet_positions)
gola_yoga_from_planet_positions(planet_positions)
subha_yoga_from_planet_positions(planet_positions)
asubha_yoga_from_planet_positions(planet_positions)
gaja_kesari_yoga_from_planet_positions(planet_positions)
guru_mangala_yoga_from_planet_positions(planet_positions)
amala_yoga_from_planet_positions(planet_positions)
parvata_yoga_from_planet_positions(planet_positions)    
kaahala_yoga_from_planet_positions(planet_positions)
chaamara_yoga_from_planet_positions(planet_positions)
sankha_yoga_from_planet_positions(planet_positions)
bheri_yoga_from_planet_positions(planet_positions)
mridanga_yoga_from_planet_positions(planet_positions)
sreenaatha_yoga_from_planet_positions(planet_positions)
matsya_yoga_from_planet_positions(planet_positions)
koorma_yoga_from_planet_positions(planet_positions)
khadga_yoga_from_planet_positions(planet_positions)
kusuma_yoga_from_planet_positions(planet_positions)
kalaanidhi_yoga_from_planet_positions(planet_positions)
kalpadruma_yoga_from_planet_positions(planet_positions)
lagnaadhi_yoga_from_planet_positions(planet_positions)
hari_yoga_from_planet_positions(planet_positions)
hara_yoga_from_planet_positions(planet_positions)
brahma_yoga_from_planet_positions(planet_positions)
vishnu_yoga_from_planet_positions(planet_positions)
siva_yoga_from_planet_positions(planet_positions)
trilochana_yoga_from_planet_positions(planet_positions)
gouri_yoga_from_planet_positions(planet_positions)
chandikaa_yoga_from_planet_positions(planet_positions)
lakshmi_yoga_from_planet_positions(planet_positions)
saarada_yoga_from_planet_positions(planet_positions)
bhaarathi_yoga_from_planet_positions(planet_positions)
saraswathi_yoga_from_planet_positions(planet_positions)
amsaavatara_yoga_from_planet_positions(planet_positions)
devendra_yoga_from_planet_positions(planet_positions)
indra_yoga_from_planet_positions(planet_positions)
ravi_yoga_from_planet_positions(planet_positions)
bhaaskara_yoga_from_planet_positions(planet_positions)
kulavardhana_yoga_from_planet_positions(planet_positions)
vasumati_yoga_from_planet_positions(planet_positions)
gandharva_yoga_from_planet_positions(planet_positions)
go_yoga_from_planet_positions(planet_positions)
vidyut_yoga_from_planet_positions(planet_positions)
chapa_yoga_from_planet_positions(planet_positions)
pushkala_yoga_from_planet_positions(planet_positions)
makuta_yoga_from_planet_positions(planet_positions)
jaya_yoga_from_planet_positions(planet_positions)
harsha_yoga_from_planet_positions(planet_positions)
sarala_yoga_from_planet_positions(planet_positions)
vimala_yoga_from_planet_positions(planet_positions)
```
#### Raja Yoga - functions
```
import itertools
import json
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house, charts
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
##### dharma\_karmadhipati\_yoga\_from\_plant\_positions (planet\_positions, raja\_yoga\_planet1, raja\_yoga\_planet2)
    """ 
        Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords
        of dharma sthana (9th) and karma sthana (10th) form a raja yoga 
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
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
###### vipareetha\_raja\_yoga\_from\_plant\_positions (planet\_positions, raja\_yoga\_planet1, raja\_yoga\_planet2)
    """
        Checks if given two raja yoga planets also for vipareetha raja yoga/
        Also returns the sub type of vipareetha raja yoga
            Harsh Raja Yoga, Saral Raja Yoga and Vimal Raja Yoga
        Vipareeta Raaja Yoga: The 6th, 8th and 12th houses are known as trik sthanas or
        dusthanas (bad houses). If their lords occupies dusthanas or conjoin dusthanas
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
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
##### neecha\_bhanga\_raja\_yoga\_from\_plant\_positions (planet\_positions, raja\_yoga\_planet1, raja\_yoga\_planet2)
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
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @param raja_yoga_planet1: Planet index for first raja yoga planet  [0 to 6] Rahu/Kethu/Lagnam not supported
        @param raja_yoga_planet2: Planet index for second raja yoga planet [0 to 6] Rahu/Kethu/Lagnam not supported
        @return: True/False = True = neecha bhanga raja yoga is present
    """
    