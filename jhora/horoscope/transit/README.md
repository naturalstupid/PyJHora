#### Tajaka - Functions
This documentation may not be up to date with the source. Please refer to the source for details of functions.

##### Import
```
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house
```
##### Lambda Functions
	""" 
	Muntha house at n years after birth is nth house from Lagna. For example at 51th year, 50th house (i.e 4x12+2, 2nd house) from lagna 
	"""
```
muntha_house = lambda ascendant_house,years: (ascendant_house+years)%12
```
##### trinal\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Trinal Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose trinal aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### trinal\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Trinal Aspects of the planet (strong benefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose trinal aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
##### sextile\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Sextile Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose sextile aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### sextile\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Sextile Aspects of the planet (weak benefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose sextile aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
##### square\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Square Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose square aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### square\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Square Aspects of the planet (weak maleefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose sextile aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
##### benefic\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Benefic Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose benefic aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### benefic\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Benefic Aspects of the planet (weak maleefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose benefic aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
##### planet_has\_benefic\_aspect\_on\_house (house\_planet\_dict, planet, house)
    """
        Return True/False if planet has benefic on a house
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose benefic aspects is sought
        @param house:House index whose benefic aspects is sought
        @return: True/False 
    """
##### semi\_sextile\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Semi sextile Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose semi sextile aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### semi\_sextile\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Semi sextile Aspects of the planet (Neutral aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:palnet index whose semi sextile aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### neutral\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Neutral Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose neutral aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### neutral\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Neutral Aspects of the Planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:planet index whose neutral aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### opposition\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Opposition Aspects of the Raasi (Strong Malefic Aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose opposition aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### opposition\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Opposition Aspects of the Planet (Strong Malefic Aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose opposition aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### conjunction\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Conjunction Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose conjunction aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### conjunction\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Conjunction Aspects of the Planet (strong malefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose conjunction aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### malefic\_aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Malefic Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose malefic aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### malefic\_aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Malefic Aspects of the Planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose malefic aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
##### planets\_have\_benefic\_aspects (house\_planet\_dict, planet1, planet2)
    """
        Return True/False if planet1 and planet2 have benefic aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose benefic aspects is sought
        @param planet1:Planet2 index whose benefic aspects is sought
        @return: True/False if both planets have benefic aspect on each other
    """
##### planets\_have\_malefic\_aspects (house\_planet\_dict, planet1, planet2)
    """
        Return True/False if planet1 and planet2 have malefic aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose malefic aspects is sought
        @param planet1:Planet2 index whose malefic aspects is sought
        @return: True/False if both planets have malefic aspect on each other
    """
##### planets\_have\_neutral\_aspects (house\_planet\_dict, planet1, planet2)
    """
        Return True/False if planet1 and planet2 have neutral aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose neutral aspects is sought
        @param planet1:Planet2 index whose neutral aspects is sought
        @return: True/False if both planets have neutral aspect on each other
    """
##### planets\_have\_aspects (house\_planet\_dict, planet1, planet2)
    """
        Return True/False if planet1 and planet2 have ANU aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose aspects is sought
        @param planet1:Planet2 index whose aspects is sought
        @return: True/False if both planets have ANY aspect on each other
    """
##### planet\_has\_malefic\_aspect\_on\_house (house\_planet\_dict, planet, house)
    """
        Return True/False if planet has malefic aspect on the house
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose malefic aspects is sought
        @param house:House index whose malefic aspects is sought
        @return: True/False if planet has malefic aspect on the house
    """
##### aspects\_of\_the\_raasi (house\_planet\_dict, raasi)
    """
        Return benefic, malefic and neutral aspected of the rasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose malefic aspects is sought
        @return aspected houses, aspected planets
    """
##### aspects\_of\_the\_planet (house\_planet\_dict, planet)
    """
        Return benefic, malefic and neutral aspects of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose malefic aspects is sought
        @return aspected houses, aspected planets
    """
##### annual\_chart (jd\_at\_dob, place, divisional\_chart\_factor=1, years=1)
    """
        Also can be called using:
            varsha_pravesh (jd_at_dob, place, divisional_chart_factor=1, years=1)
        Create Tajaka Annual Chart. Tajaka annual chart is chart for one year at "years" from date of birth/time of birth
        @param jd_at_dob: Julian Day nummber at date/time of birth
            Note: You can use swe.julday(dob_year,dob_month,dob_day,tob_hour+tob_minutes/60.0+tob_seconds/3600.0) to get
        @param place: should be a struct os panchanga.Place (place,latitude,longitude,time_sone_factor)
        @param divisional_chart_factor: 1=Rasi, 2=Hota, 9=navamsa etc. See panchanga.division_chart_factors for details
        @param years: number of years after dob the dhasa varga chart is sought 
        @return: Tjaka annual dhasa varga chart as list of planets
    """
##### monthly\_chart (jd\_at\_dob, place, divisional\_chart\_factor=1, years=1, months=1)
    """
        Also can be called using:
            maasa_pravesh (jd_at_dob, place, divisional_chart_factor=1, years=1, months=1)
        Create Tajaka monthly Chart. Tajaka monthly chart is chart for nth month at "years" from date of birth/time of birth
        @param jd_at_dob: Julian Day nummber at date/time of birth
            Note: You can use swe.julday(dob_year,dob_month,dob_day,tob_hour+tob_minutes/60.0+tob_seconds/3600.0) to get
        @param place: should be a struct os panchanga.Place (place,latitude,longitude,time_sone_factor)
        @param divisional_chart_factor: 1=Rasi, 2=Hota, 9=navamsa etc. See panchanga.division_chart_factors for details
        @param years: number of years after dob the dhasa varga chart is sought 
        @param months: number of month after years after dob the dhasa varga chart is sought 
        @return: Tjaka annual dhasa varga chart as list of planets
    """
##### sixty\_hour\_chart (jd\_at\_dob, place, divisional\_chart\_factor=1, years=1, months=1, sixty\_hour\_count=1)
    """
        Create Tajaka sizty hour Chart.
        @param jd_at_dob: Julian Day nummber at date/time of birth
            Note: You can use swe.julday(dob_year,dob_month,dob_day,tob_hour+tob_minutes/60.0+tob_seconds/3600.0) to get
        @param place: should be a struct os panchanga.Place (place,latitude,longitude,time_sone_factor)
        @param divisional_chart_factor: 1=Rasi, 2=Hota, 9=navamsa etc. See panchanga.division_chart_factors for details
        @param years: number of years after dob the dhasa varga chart is sought 
        @param months: number of month after years after dob the dhasa varga chart is sought 
        @param sizty_hour_count: number of 2.5 days in the tajaka month after years after dob the dhasa varga chart is sought 
        @return: Tjaka annual dhasa varga chart as list of planets
    """
##### harsha\_bala (p\_to\_h, new\_year\_daytime\_start=True)
    """
        computes the harsha bala score of the planets
        @param p_to_h: Planet to House dictionary in the format:
            ={0:1,1:0,2:3...} # Sun in Ta, Moon in Ar, Mars in Ge etc
        @param new_year_daytime_start: If the birth time on the annual chart is daytime or nighttime
            For example.If some one was born 11:00 AM in 1970 and 25th year the same time is equivalent to say 7 pm
            because a solar year 365.2583 days then  24*365.2583 could lead to 7pm - so new_year_daytime_start = False
        @return: Harsha Bala score for each planet - as a list 
            Example: {0: 0, 1: 15, 2: 0, 3: 10, 4: 5, 5: 10, 6: 5} - Sun's score = 0, Venus's score = 10
    """
##### pancha\_vargeeya\_bala (jd, place)
    """
        computes the Pancha Vargeeya bala score of the planets
            Keshetra Bala:
                A planet gets 30 units of Bala in own sign, 22.5 units in friendly sign, 15 units in neutral sign 
                and 7.5 units in an enemy sign.
            Drekkana Bala
                A planet in own rasi in D-3 gets 10 units of Drekkana bala. A planet in a friend’s rasi in D-3 gets 5 units of
                Drekkana bala. A planet in an enemy’s rasi in D-3 gets 2.5 units of Drekkana bala.
            Navamsa Bala
                A planet in own rasi in D-9 gets 5 units of Navamsa bala. A planet in a friend’s rasi in D-9 gets 2.5 units of
                Navamsa bala. A planet in an enemy’s rasi in D-9 gets 1.25 units of Navamsa bala.
            Uchcha Bala
                Uchcha bala shows how close a planet is from its exaltation point. A planet gets 20
                units of uchcha bala if it is at its deep exaltation point (Sun: 10º Ar, Moon: 3º Ta,
                Mars: 28º Cp, Mercury: 15º Vi, Jupiter: 5º Cn, Venus: 27º Pi, Saturn: 20º Li). At
                180º from its deep exaltation point, a planet is deeply debilitated and it gets 0 units of
                uchcha bala.
            Hadda Bala
                A planet in own hadda gets 15 units of Hadda bala. A planet in a friend’s hadda gets 7.5 units of Hadda bala. 
                A planet in an enemy’s hadda gets 3.75 units of Hadda bala.
        @param jd: Julian Day Number (of the annual day
        @param place: panchanga.Place struct: Place('place_name',latitude, longitude, timezone) 
        @return: Pancha Vargeeya Bala score for each planet - as a list 
            Example: [15.72, 14.27, 13.0, 6.33, 11.87, 16.05, 6.45] - Sun's score = 15.72, Venus's score = 16.05
    """
##### dwadhasa\_vargeeya\_bala (jd, place)
    """
        Calculates dwadhasa_vargeeya_bala score of the planets
        @param jd: Julian Day Number (of the annual day
        @param place: panchanga.Place struct: Place('place_name',latitude, longitude, timezone) 
        @return:   returns dict of strong (>0) and weak (<0) planets. Also returns list of only strong planets
            Example: {0: -4, 1: 0, 2: -4, 3: 2, 4: 0, 5: -2, 6: 2} [3, 6]
    """
##### lord\_of\_the\_year (jd\_at\_dob, place, years\_from\_dob)
    """
        Get the Lord of the year/annual chart - Get natal lagna house from birth chart
        @param jd_at_dob: Julin Day Number for the date of birth
        @param place: pancha.Place Struct Place('place name',latitude,longitude,timezone)
        @param years_from_dob:# of years from date of birth.
            For example if Lord of the 25th year from DOB, then years_from_dob=25
        @return:  Lord of the year (planet index) [0..6]
            Note: Rahu/Ketu dont form lord of the year
    """
##### lord\_of\_the\_month (jd\_at\_dob, place, years\_from\_dob, months\_from\_dob)
    """
        Get the Lord of the monthly chart - Get natal lagna house from birth chart
        @param jd_at_dob: Julin Day Number for the date of birth
        @param place: pancha.Place Struct Place('place name',latitude,longitude,timezone)
        @param years_from_dob:# of years from date of birth.
            For example if Lord of the 25th year from DOB, then years_from_dob=25
        @param months_from_dob:# of months on the years_from_dob.
            For example if 10th month of 25th year from DOB, then months_from_dob=10
        @return:  Lord of the month (planet index) [0..6]
            Note: Rahu/Ketu dont form lord of the month
    """
##### both\_planets\_within\_their\_deeptamsa (planet\_positions, planet1, planet2)
    """
        Check if two planets are within their deeptamsa
        @param planet_positions: Planet Positions in the format [[planet,(raasi,longitude)],...]
        @param planet1: First planet index
        @param planet2: Second planet index comapred against
        @return: True/False, Ithasala Type
            Ithasala Type: 1. Varthamaana ithasala, 2. Bhavishya ithasala, 3. Poorna ithasala
    """
##### both\_planets\_approaching (planet\_positions, planet1, planet2)
    """
        Check if two planets are approaching each other
        NOTE: TODO: Check if planets in retrograde so they are moving away
        @param planet_positions: Planet Positions in the format [[planet,(raasi,longitude)],...]
        @param planet1: First planet index
        @param planet2: Second planet index comapred against
        @return: True/False
    """
#### Tajaka Yoga - Functions
##### Import
```
import itertools
from hora import const,utils
from hora.horoscope.chart import house
from hora.horoscope.transit import tajaka
```
##### ishkavala\_yoga (planet\_to\_house\_dict, asc\_house)
    """
         Ishkavala Yoga
            If planets occupy only kendras (1st, 4th, 7th and 10th houses) and panapharas (2nd, 5th,
            8th and 11th houses) and if apoklimas (3rd, 6th, 9th and 12th houses) are empty, then
            this yoga is present. This yoga gives wealth, happiness and good fortune.
        @param planet_to_house_dict: Example {0:1.1:2,2:0,..'L':1}
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether ishkaval yoga is present or not  
    """
##### induvara\_yoga (planet\_to\_house\_dict, asc\_house)
    """
        Induvara Yoga
            If planets occupy only apoklimas (3rd, 6th, 9th and 12th houses) and if kendras (1st, 4th,
            7th and 10th houses) and panapharas (2nd, 5th, 8th and 11th houses) are empty, then this
            yoga is present. This yoga gives disappointments, worries and illnesses.    
        @param planet_to_house_dict: Example {0:1.1:2,2:0,..'L':1}
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether induvara yoga is present or not  
    """
##### ithasala\_yoga (planet\_positions, planet1, planet2)
    """
        Ithasala Yoga
            If two planets have an aspect and if the faster moving planet83 is less advanced in its
            rasi than the slower moving planet, then we have an ithasala yoga between the two.        
        @param planet_to_house_dict: Example {0:1.1:2,2:0,..'L':1}
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether induvara yoga is present or not  
    """
##### eesarpha\_yoga (planet_\positions, planet1, planet2)
    """
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @param asc_house: Raasi index of the ascendant/Lagnam
        @return: True/False - whether yoga is present or not  
    """
##### get\_nakta\_yoga\_planet\_triples (planet\_positions)
    """
        nakta yoga between p2 and p3 if 
             p1 & p2 and p1 & p3 have ithasala yoga between them 
             but p2 and p3 have no aspects
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of natka yoga triples
    """
##### get\_yamaya\_yoga\_planet\_triples (planet\_positions)
    """
        yamaya yoga between p2 and p3 if 
             p1 & p2 and p1 & p3 have ithasala yoga between them 
             but p2 and p3 have no aspects
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of yamaya yoga triples
    """
##### get\_eesarpha\_yoga\_planet\_pairs (planet\_positions)
    """
        Get eeasrpha yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of eesarpha yoga pairs        
    """
##### get\_ithasala\_yoga\_planet\_pairs (planet\_positions)
    """
        Get ithasala yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of ithasala yoga pairs        
    """
##### get\_manahoo\_yoga\_planet\_pairs (planet\_positions)
    """
        Get manahoo yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of manahoo yoga pairs        
    """
##### get\_kamboola\_yoga\_planet\_pairs (planet\_positions)
    """
        Get kamboola yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of kamboola yoga pairs        
    """
##### get\_radda\_yoga\_planet\_pairs (planet\_positions)
    """
        Get radda yoga planet pairs
        @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]]
        @return: List of radda yoga pairs        
    """
##### get\_duhphali\_kutta\_yoga\_planet\_pairs (jd, place)
    """
        Get duhphali kutta yoga planet pairs
        @param jd: Julian Day Number
        @param place: panchanga.Place struct ('place name',latitude, longitude, timezone) 
        @return: List of duhphali kutta yoga pairs        
    """
#### Saham – Functions
    Saham calculation
    saham has a formula that looks like A – B + C. What this means is that we take the
    longitudes of A, B and C and find (A – B + C). This is equivalent to finding how far
    A is from B and then taking the same distance from C. However, if C is not between
    B and A (i.e. we start from B and go zodiacally till we meet A and we do not find C
    on the way), then we add 30º to the value evaluated above.    
##### Import
```
from hora import const, utils
from hora.panchanga import panchanga
from hora.horoscope.chart import charts, house
```
##### Lambda Functions
```
saham_longitude = lambda pp,p:pp[p][1][0]*30+pp[p][1][1]
lagna_longitude = lambda pp: saham_longitude(pp,0)
sun_longitude = lambda pp: saham_longitude(pp,1)
moon_longitude = lambda pp: saham_longitude(pp,2)
mars_longitude = lambda pp: saham_longitude(pp,3)
mercury_longitude = lambda pp: saham_longitude(pp,4)
jupiter_longitude = lambda pp: saham_longitude(pp,5)
venus_longitude = lambda pp: saham_longitude(pp,6)
saturn_longitude = lambda pp: saham_longitude(pp,7)
```
##### punya\_saham (planet\_positions,night\_time\_birth=False)
```
1 Punya Fortune/good deeds Moon – Sun + Lagna 
```
    
##### vidya\_saham (planet\_positions,night\_time\_birth=False)
```
2 Vidya Education Sun – Moon + Lagna 
```

##### yasas\_saham (planet\_positions,night\_time\_birth=False)
```
3 Yasas Fame Jupiter – PunyaSaham + Lagna 
```

##### mitra\_saham (planet\_positions,night\_time\_birth=False)
```
4 Mitra Friend Jupiter – PunyaSaham + Venus 
```

##### mahatmaya\_saham (planet\_positions,night\_time\_birth=False)
```
5 Mahatmya Greatness PunyaSaham – Mars + Lagna 
```

##### asha\_saham (planet\_positions,night\_time\_birth=False)
```
6 Asha Desires Saturn – Mars + Lagna 
```

##### samartha\_saham (planet\_positions,night\_time\_birth=False)
```
7 Samartha Enterprise/ability    Mars – Lagna Lord + Lagna  (Jupiter – Mars + Lagna, if Mars owns lagna) 
```

##### bhratri\_saham (planet\_positions)
```
8 Bhratri Brothers Jupiter – Saturn + Lagna  (same for day & night) 
```

##### gaurava\_saham (planet\_positions,night\_time\_birth=False)
```
9 Gaurava Respect/regard Jupiter – Moon + Sun 
```

##### pithri\_saham (planet\_positions,night\_time\_birth=False)
    ```
10 Pitri Father Saturn – Sun + Lagna 
```

##### rajya\_saham (planet\_positions,night\_time\_birth=False)
```
11 Rajya Kingdom Saturn – Sun + Lagna 
```

##### maathri\_saham (planet\_positions,night\_time\_birth=False)
```
12 Matri Mother Moon – Venus + Lagna 
```

##### puthra\_saham (planet\_positions,night\_time\_birth=False)
```
13 Putra Children Jupiter – Moon + Lagna 
```

##### jeeva\_saham (planet\_positions,night\_time\_birth=False)
```
14 Jeeva Life Saturn – Jupiter + Lagna 
```

##### karma\_saham (planet\_positions,night\_time\_birth=False)
```
15 Karma Action  (work) Mars – Mercury + Lagna 
```

##### roga\_saham (planet\_positions,night\_time\_birth=False)
```
16 Roga Disease Lagna – Moon + Lagna  (Same for night/day) 
```

##### roga\_sagam\_1 (planet\_positions,night\_time\_birth=False)
```
16 Roga Disease - Another Version -  Saturn – Moon + Lagna 
```

##### kali\_saham (planet\_positions,night\_time\_birth=False)
```
17 Kali Great misfortune Jupiter – Mars + Lagna 
```

##### sastra\_saham (planet\_positions,night\_time\_birth=False)
```
18 Sastra Sciences Jupiter – Saturn + Mercury 
```

##### bandhu\_saham (planet\_positions,night\_time\_birth=False)
```
19 Bandhu Relatives Mercury – Moon + Lagna 
```

##### mrithyu\_saham (planet\_positions)
```
20 Mrityu Death 8th house – Moon + Lagna  (same for day & night) 
```

##### paradesa\_saham (planet\_positions,night\_time\_birth=False)
```
21 Paradesa Foreign countries 9th house – 9th lord + Lagna  (same for day & night) 
```

##### artha\_saham (planet\_positions,night\_time\_birth=False)
```
22 Artha Money 2nd house – 2nd lord + Lagna  (same for day & night) 
```

##### paradara\_saham (planet\_positions,night\_time\_birth=False)
```
23 Paradara Adultery Venus – Sun + Lagna 
```

##### vanika\_saham (planet\_positions,night\_time\_birth=False)
```
24 Vanik Commerce Moon – Mercury + Lagna 
```

##### karyasiddhi\_saham (planet\_positions,night\_time\_birth=False)
```
25 Karyasiddhi Success in endeavours Saturn – Sun + Lord of sunsign  (Night: Saturn – Moon + Lord of Moonsign) 
```

##### vivaha\_saham (planet\_positions,night\_time\_birth=False)
```
26 Vivaha Marriage Venus – Saturn + Lagna 
```

##### santapa\_saham (planet\_positions,night\_time\_birth=False)
```
27 Santapa Sadness Saturn – Moon + 6th house 
```

##### sraddha\_saham (planet\_positions,night\_time\_birth=False)
```
28 Sraddha Devotion/sincerity Venus – Mars + Lagna 
```

##### preethi\_saham (planet\_positions,night\_time\_birth=False)
```
29 Preeti Love/attachment SastraSaham – PunyaSaham + Lagna 
```

##### jadya\_saham (planet\_positions,night\_time\_birth=False)
```
30 Jadya Chronic disease Mars – Saturn + Mercury 
```

##### vyaapaara\_saham (planet\_positions)
```
31 Vyapara Business Mars – Saturn + Lagna  (same for day & night) 
```

##### sathru\_saham (planet\_positions,night\_time\_birth=False)
```
32 Satru Enemy Mars – Saturn + Lagna 
```

##### jalapatna\_saham (planet\_positions,night\_time\_birth=False)
```
33 Jalapatana Crossing an ocean Cancer 15º– Saturn + Lagna 
```

##### bandhana\_saham (planet\_positions,night\_time\_birth=False)
```
34 Bandhana Imprisonment PunyaSaham – Saturn + Lagna 
```

##### apamrithyu\_saham (planet\_positions,night\_time\_birth=False)
```
35 Apamrityu Bad death 8th house – Mars + Lagna 
```

##### laabha\_saham (planet\_positions,night\_time\_birth=False)
```
36 Labha Material gains 11th house – 11th lord + Lagna  (same for day & night) 
```
