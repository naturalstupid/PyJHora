""" To calculate Tajaka - Annual, monthly, sixty-hour, charts """
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house, strength
year_value = const.sidereal_year #const.tropical_year

kendras = lambda asc_house:[(asc_house+h-1)%12 for h in [1,4,7,10] ]
panaparas = lambda asc_house:[(asc_house+h-1)%12 for h in [2,5,8,11] ]
apoklimas = lambda asc_house:[(asc_house+h-1)%12 for h in [3,6,9,12] ]
""" Muntha house at x years after birth is xth house from Lagna. For example at 51th year, 50th house (i.e 4x12+2, 2nd house) from lagna """
muntha_house = lambda ascendant_house,years: (ascendant_house+years)%12
""" Aspects followed in Tajaka Analysis """
def trinal_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Trinal Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose trinal aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    aspected_houses = [(raasi+5-1)%12, (raasi+9-1)%12]
    aspected_planets = [ house_planet_dict[th].split('/') for th in aspected_houses if house_planet_dict[th]!='']
    aspected_planets = sum(aspected_planets,[])
    aspected_planets = [ap for ap in aspected_planets if ap.strip() != '']
    return aspected_houses,aspected_planets    
def trinal_aspects_of_the_planet(house_planet_dict,planet):
    """
        Trinal Aspects of the planet (strong benefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose trinal aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet_house = planet_to_house_dict[planet]
    return trinal_aspects_of_the_raasi(house_planet_dict,planet_house)
def sextile_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Sextile Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose sextile aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    aspected_houses = [(raasi+3-1)%12, (raasi+11-1)%12]
    aspected_planets = [ house_planet_dict[th].split('/') for th in aspected_houses if house_planet_dict[th]!='']
    aspected_planets = sum(aspected_planets,[])
    aspected_planets = [ap for ap in aspected_planets if ap.strip() != '']
    return aspected_houses,aspected_planets
def sextile_aspects_of_the_planet(house_planet_dict,planet):
    """
        Sextile Aspects of the planet (weak benefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose sextile aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet_house = planet_to_house_dict[planet]
    return sextile_aspects_of_the_raasi(house_planet_dict,planet_house)
def square_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Square Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose square aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    aspected_houses = [(raasi+4-1)%12, (raasi+10-1)%12]
    aspected_planets = [ house_planet_dict[th].split('/') for th in aspected_houses if house_planet_dict[th]!='']
    aspected_planets = sum(aspected_planets,[])
    aspected_planets = [ap for ap in aspected_planets if ap.strip() != '']
    return aspected_houses,aspected_planets
def square_aspects_of_the_planet(house_planet_dict,planet):
    """
        Square Aspects of the planet (weak maleefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose sextile aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet_house = planet_to_house_dict[planet]
    return square_aspects_of_the_raasi(house_planet_dict,planet_house)
def benefic_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Benefic Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose benefic aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    trh,trp = trinal_aspects_of_the_raasi(house_planet_dict, raasi)
    sqh,sqp = sextile_aspects_of_the_raasi(house_planet_dict, raasi)
    bah = trh + sqh
    bap = trp+sqp#sum(trp+sqp,[])
    return bah,bap
def benefic_aspects_of_the_planet(house_planet_dict,planet):
    """
        Benefic Aspects of the planet (weak maleefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose benefic aspects is sought
        @return: aspected raasis, aspected planets - as a list 
    """
    trh,trp = trinal_aspects_of_the_planet(house_planet_dict, planet)
    sqh,sqp = sextile_aspects_of_the_planet(house_planet_dict, planet)
    bah = trh + sqh
    bap = trp+sqp#sum(trp+sqp,[])
    return bah,bap
def planet_has_benefic_aspect_on_house(house_planet_dict,planet,house):
    """
        Return True/False if planet has benefic on a house
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose benefic aspects is sought
        @param house:House index whose benefic aspects is sought
        @return: True/False 
    """
    bh,_ = benefic_aspects_of_the_planet(house_planet_dict, planet)
    return house in bh
def semi_sextile_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Semi sextile Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose semi sextile aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    aspected_houses = [(raasi+2-1)%12, (raasi+12-1)%12]
    aspected_planets = [ house_planet_dict[th].split('/') for th in aspected_houses if house_planet_dict[th]!='']
    aspected_planets = sum(aspected_planets,[])
    aspected_planets = [ap for ap in aspected_planets if ap.strip() != '']
    return aspected_houses,aspected_planets
def semi_sextile_aspects_of_the_planet(house_planet_dict,planet):
    """
        Semi sextile Aspects of the planet (Neutral aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:palnet index whose semi sextile aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet_house = planet_to_house_dict[planet]
    return semi_sextile_aspects_of_the_raasi(house_planet_dict,planet_house)
def neutral_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Neutral Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose neutral aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    return semi_sextile_aspects_of_the_raasi(house_planet_dict,raasi)
def neutral_aspects_of_the_planet(house_planet_dict,planet):
    """
        Neutral Aspects of the Planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:planet index whose neutral aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    return semi_sextile_aspects_of_the_planet(house_planet_dict,planet)
def opposition_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Opposition Aspects of the Raasi (Strong Malefic Aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose opposition aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    aspected_houses = [(raasi+7-1)%12]
    aspected_planets = [ house_planet_dict[th].split('/') for th in aspected_houses if house_planet_dict[th]!='']
    aspected_planets = sum(aspected_planets,[])
    aspected_planets = [ap for ap in aspected_planets if ap.strip() != '']
    return aspected_houses,aspected_planets
def opposition_aspects_of_the_planet(house_planet_dict,planet):
    """
        Opposition Aspects of the Planet (Strong Malefic Aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose opposition aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet_house = planet_to_house_dict[planet]
    return opposition_aspects_of_the_raasi(house_planet_dict,planet_house)
def conjunction_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Conjunction Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose conjunction aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet = list(p_to_h.keys())[list(p_to_h.values()).index(raasi)]
    aspected_houses = [raasi]
    aspected_planets = [ house_planet_dict[th].replace(str(planet),'').split('/') for th in aspected_houses if house_planet_dict[th]!='']
    aspected_planets = sum(aspected_planets,[])
    aspected_planets = [ap for ap in aspected_planets if ap.strip() != '']
    return aspected_houses,aspected_planets
def conjunction_aspects_of_the_planet(house_planet_dict,planet):
    """
        Conjunction Aspects of the Planet (strong malefic aspect)
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose conjunction aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    planet_to_house_dict = utils.get_planet_to_house_dict_from_chart(house_planet_dict)
    planet_house = planet_to_house_dict[planet]
    return conjunction_aspects_of_the_raasi(house_planet_dict,planet_house)
def malefic_aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Malefic Aspects of the Raasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose malefic aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    sqh,sqp = square_aspects_of_the_raasi(house_planet_dict, raasi)
    coh,cop = conjunction_aspects_of_the_raasi(house_planet_dict, raasi)
    oph,opp = opposition_aspects_of_the_raasi(house_planet_dict, raasi)
    mah = sqh + coh + oph
    mapp = sqp+cop+opp#sum(sqp+cop+opp,[])
    return mah,mapp
def malefic_aspects_of_the_planet(house_planet_dict,planet):
    """
        Malefic Aspects of the Planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose malefic aspects is sought
        @return: aspected Raasis, aspected planets - as a list 
    """
    sqh,sqp = square_aspects_of_the_planet(house_planet_dict, planet)
    coh,cop = conjunction_aspects_of_the_planet(house_planet_dict, planet)
    oph,opp = opposition_aspects_of_the_planet(house_planet_dict, planet)
    mah = sqh + coh + oph
    mapp = sqp+cop+opp#sum(sqp+cop+opp,[])
    return mah,mapp
def planets_have_benefic_aspects(house_planet_dict,planet1,planet2):
    """
        Return True/False if planet1 and planet2 have benefic aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose benefic aspects is sought
        @param planet1:Planet2 index whose benefic aspects is sought
        @return: True/False if both planets have benefic aspect on each other
    """
    return str(planet2) in benefic_aspects_of_the_planet(house_planet_dict, planet1)[1]
def planets_have_malefic_aspects(house_planet_dict,planet1,planet2):
    """
        Return True/False if planet1 and planet2 have malefic aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose malefic aspects is sought
        @param planet1:Planet2 index whose malefic aspects is sought
        @return: True/False if both planets have malefic aspect on each other
    """
    return str(planet2) in malefic_aspects_of_the_planet(house_planet_dict, planet1)[1]
def planets_have_neutral_aspects(house_planet_dict,planet1,planet2):
    """
        Return True/False if planet1 and planet2 have neutral aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose neutral aspects is sought
        @param planet1:Planet2 index whose neutral aspects is sought
        @return: True/False if both planets have neutral aspect on each other
    """
    return str(planet2) in neutral_aspects_of_the_planet(house_planet_dict, planet1)[1]
def planet_aspects_from_chart(chart):
    planet_aspects = {k:[] for k in range(9)}
    for planet1 in range(9):
        for planet2 in range(9):
            if planets_have_aspects(chart, planet1, planet2):
                planet_aspects[planet1].append(planet2)
    return planet_aspects
    
def planets_have_aspects(house_planet_dict,planet1,planet2):
    """
        Return True/False if planet1 and planet2 have ANY aspects on each other
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1:Planet1 index whose aspects is sought
        @param planet1:Planet2 index whose aspects is sought
        @return: True/False if both planets have ANY aspect on each other
    """
    chk1 = planets_have_benefic_aspects(house_planet_dict,planet1,planet2)
    chk2 = planets_have_malefic_aspects(house_planet_dict,planet1,planet2)
    chk3 = planets_have_neutral_aspects(house_planet_dict,planet1,planet2)
    return chk1 or chk2 or chk3
def planet_has_malefic_aspect_on_house(house_planet_dict,planet,house):
    """
        Return True/False if planet has malefic aspect on the house
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose malefic aspects is sought
        @param house:House index whose malefic aspects is sought
        @return: True/False if planet has malefic aspect on the house
    """
    bh,_ = malefic_aspects_of_the_planet(house_planet_dict, planet)
    return house in bh
def aspects_of_the_raasi(house_planet_dict,raasi):
    """
        Return benefic, malefic and neutral aspected of the rasi
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param raasi:Raasi index whose malefic aspects is sought
        @return aspected houses, aspected planets
    """
    bah,bap = benefic_aspects_of_the_raasi(house_planet_dict, raasi)
    mah,map = malefic_aspects_of_the_raasi(house_planet_dict, raasi)
    nah,nap = neutral_aspects_of_the_raasi(house_planet_dict, raasi)
    ah = bah + mah + nah
    ap = bap + map + nap
    #ap = utils.flatten_list(ap)
    return ah,ap
def aspects_of_the_planet(house_planet_dict,planet):
    """
        Return benefic, malefic and neutral aspects of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet:Planet index whose malefic aspects is sought
        @return aspected houses, aspected planets
    """
    bah,bap = benefic_aspects_of_the_planet(house_planet_dict, planet)
    mah,map = malefic_aspects_of_the_planet(house_planet_dict, planet)
    nah,nap = neutral_aspects_of_the_planet(house_planet_dict, planet)
    ah = bah + mah + nah
    ap = bap + map + nap
    #ap = utils.flatten_list(ap)
    return ah,ap
def varsha_pravesh(jd_at_dob,place,divisional_chart_factor=1,years=1):
    return annual_chart(jd_at_dob,place,divisional_chart_factor,years)
def annual_chart_approximate(dob,tob,place,divisional_chart_factor=1,years=1):
    """
        (1) Find the birthday as per western calendar in the required year.
        (2) Find the years completed. Find the corresponding days, hours, minutes and
        seconds from Table 71. If the age is not in the list, express it as a sum of entries
        found in the table and add their values. For example, suppose someone finished
        46 years. Then add the values given for 40 years and 6 years.
        (3) Add the days found above to the weekday77 of birth and find the resulting
        weekday. Find the nearest date to the birthday found in (1) that falls on this
        weekday. A time equal to the birthtime on this date is taken as a reference. 
        (4) Add the hours, minutes and seconds found in (2) to the reference date and time
        found in (3). The result is the date and time of the commencement of new year.
        (5) Find the planetary positions, lagna etc at this time for the longitude and latitude
        of the birthplace.   
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    natal_chart = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    natal_solar_long = natal_chart[1][1][0]*30+natal_chart[1][1][1]
    jd_years = drik.next_annual_solar_date_approximate(dob, tob, years)
    yn,mn,dn,fhn = utils.jd_to_gregorian(jd_years)
    cht = _get_tajaka_chart(jd_years,place,divisional_chart_factor)
    years_solar_long = cht[1][1][0]*30+cht[1][1][1]
    solar_long_diff = natal_solar_long-years_solar_long
    solar_long_correction = solar_long_diff*year_value/360.0
    jd_years_corrected = jd_years+solar_long_correction
    #print('natal_solar_long',utils.to_dms(natal_solar_long,is_lat_long='plong'),
    #      'years_solar_long',utils.to_dms(years_solar_long,is_lat_long='plong'),
    #      'solar_long_diff',utils.to_dms(solar_long_diff,is_lat_long='plong'))
    #print('solar_long_correction',utils.to_dms(solar_long_correction*24,as_string=True),jd_years,jd_years_corrected)
    yc,mc,dc,fhc = utils.jd_to_gregorian(jd_years_corrected)
    #fhn = utils.to_dms(fhn)
    fhc = utils.to_dms(fhc)
    #print('jd_years',(yn,mn,dn,fhn),'jd_years_corrected',(yc,mc,dc,fhc))
    cht = _get_tajaka_chart(jd_years_corrected,place,divisional_chart_factor)
    return cht,[(yc,mc,dc),fhc]
def annual_chart(jd_at_dob,place,divisional_chart_factor=1,years=1):
    """
        Also can be called using:
            varsha_pravesh (jd_at_dob, place, divisional_chart_factor=1, years=1)
        Create Tajaka Annual Chart. Tajaka annual chart is chart for one year at "years" from date of birth/time of birth
        @param jd_at_dob: Julian Day nummber at date/time of birth
            Note: You can use swe.julday(dob_year,dob_month,dob_day,tob_hour+tob_minutes/60.0+tob_seconds/3600.0) to get
        @param place: should be a struct os drik.Place (place,latitude,longitude,time_sone_factor)
        @param divisional_chart_factor: 1=Rasi, 2=Hota, 9=navamsa etc. See drik.division_chart_factors for details
        @param years: number of years after dob the dhasa varga chart is sought 
        @return: Tjaka annual dhasa varga chart as list of planets
    """
    #jd_years = jd_at_dob + years*year_value_year
    jd_years = drik.next_solar_date(jd_at_dob, place, years=years) #, months, sixty_hours)
    y,m,d,fh = utils.jd_to_gregorian(jd_years)
    cht = _get_tajaka_chart(jd_years,place,divisional_chart_factor)
    return cht,[(y,m,d),utils.to_dms(fh)]
def _get_tajaka_chart(jd,place,divisional_chart_factor):
    return charts.divisional_chart(jd,place,divisional_chart_factor=divisional_chart_factor)
def maasa_pravesh(jd_at_dob,place,divisional_chart_factor=1,years=1,months=1):
    return monthly_chart(jd_at_dob,place,divisional_chart_factor,years,months)
def monthly_chart(jd_at_dob,place,divisional_chart_factor=1,years=1,months=1):
    """
        Also can be called using:
            maasa_pravesh (jd_at_dob, place, divisional_chart_factor=1, years=1, months=1)
        Create Tajaka monthly Chart. Tajaka monthly chart is chart for nth month at "years" from date of birth/time of birth
        @param jd_at_dob: Julian Day nummber at date/time of birth
            Note: You can use swe.julday(dob_year,dob_month,dob_day,tob_hour+tob_minutes/60.0+tob_seconds/3600.0) to get
        @param place: should be a struct os drik.Place (place,latitude,longitude,time_sone_factor)
        @param divisional_chart_factor: 1=Rasi, 2=Hota, 9=navamsa etc. See drik.division_chart_factors for details
        @param years: number of years after dob the dhasa varga chart is sought 
        @param months: number of month after years after dob the dhasa varga chart is sought 
        @return: Tjaka annual dhasa varga chart as list of planets
    """
    if months<1 or months > 12:
        months = 1
    #jd_years = jd_at_dob + (years + (months/12.0))*year_value
    jd_years = drik.next_solar_date(jd_at_dob, place, years, months)#, sixty_hours)
    y,m,d,fh = utils.jd_to_gregorian(jd_years)
    cht = _get_tajaka_chart(jd_years,place,divisional_chart_factor)
    return cht,[(y,m,d),utils.to_dms(fh)]
def sixty_hour_chart(jd_at_dob,place,divisional_chart_factor=1,years=1,months=1,sixty_hour_count=1):
    """
        Create Tajaka sizty hour Chart.
        @param jd_at_dob: Julian Day nummber at date/time of birth
            Note: You can use swe.julday(dob_year,dob_month,dob_day,tob_hour+tob_minutes/60.0+tob_seconds/3600.0) to get
        @param place: should be a struct os drik.Place (place,latitude,longitude,time_sone_factor)
        @param divisional_chart_factor: 1=Rasi, 2=Hota, 9=navamsa etc. See drik.division_chart_factors for details
        @param years: number of years after dob the dhasa varga chart is sought 
        @param months: number of month after years after dob the dhasa varga chart is sought 
        @param sizty_hour_count: number of 2.5 days in the tajaka month after years after dob the dhasa varga chart is sought 
        @return: Tjaka annual dhasa varga chart as list of planets
    """
    jd_years = drik.next_solar_date(jd_at_dob, place, years, months, sixty_hour_count)
    y,m,d,fh = utils.jd_to_gregorian(jd_years)
    #jd_years = jd_at_dob + (years + (months/12.0)+(sixty_hour_count/144.0))*year_value
    cht = _get_tajaka_chart(jd_years,place,divisional_chart_factor)
    return cht,[(y,m,d),utils.to_dms(fh)]
def _get_lord_candidates(planet_positions,years_from_dob,natal_lagna_house,night_time_birth):
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    " Rule-1 Sun-Sign's  or Moon-Sign's Lord?"
    candidates = []
    if night_time_birth:
        candidates.append(house.house_owner_from_planet_positions(planet_positions,tajaka_chart_p_to_h[1]))
    else:
        candidates.append(house.house_owner_from_planet_positions(planet_positions,tajaka_chart_p_to_h[0]))
    candidates.append(house.house_owner_from_planet_positions(planet_positions,natal_lagna_house))
    asc_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    m_house = muntha_house(asc_house,years_from_dob)
    candidates.append(house.house_owner_from_planet_positions(planet_positions,m_house))
    candidates.append(house.house_owner_from_planet_positions(planet_positions,asc_house))
    if night_time_birth:
        candidates.append(const.tri_rasi_nighttime_lords[asc_house]) 
    else:
        candidates.append(const.tri_rasi_daytime_lords[asc_house])
    ap = house.aspected_planets_of_the_raasi(tajaka_chart_h_to_p, asc_house)
    candidates = list(sorted(set(candidates),key=candidates.index)) # Remove duplicates and keep order same  
    return candidates
def _get_the_lord_of_tajaka_chart(jd, place,candidates):
    rasi_chart = charts.divisional_chart(jd, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    asc_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    #print('candidates',candidates)
    asc_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    candidates_shortlisted = [candidate for candidate in candidates if planet_has_benefic_aspect_on_house(tajaka_chart_h_to_p, candidate, asc_house)]
    #print('candidates_shortlisted based on benefic aspects',candidates_shortlisted)
    if len(candidates_shortlisted) == 1:
        lord_of_the_year = candidates_shortlisted[0] # Lord of the Year
        return lord_of_the_year
    if len(candidates_shortlisted) == 0:
        candidates_shortlisted = [candidate for candidate in candidates if planet_has_malefic_aspect_on_house(tajaka_chart_h_to_p, candidate, asc_house)]
    #print('candidates_shortlisted based on malefic aspects',candidates_shortlisted)
    if len(candidates_shortlisted) == 1:
        lord_of_the_year = candidates_shortlisted[0] # Lord of the Year 
        return lord_of_the_year
    " No or more than one candidate benefic or malefic - so let us check highest panchavargeeya bala"
    
    pvb = strength.pancha_vargeeya_bala(jd, place)
    pvbc = [pvb[candidate] for candidate in candidates]
    #pvbcl = pvbc[lord_of_the_year]
    pvb_max = max(pvbc)
    if pvb_max > const.pancha_vargeeya_bala_strength_threshold:
        lord_of_the_year = pvbc.index(pvb_max)
        #print('Lord of year as per pancha veerya bala (max) ',lord_of_the_year,'is',pvb_max)
        return lord_of_the_year
    "rasi occupied by Sun or Moon in the annual chart - candidate-1"
    lord_of_the_year = candidates[0]
    #print('Lord of the year based on new year start',lord_of_the_year)
    return lord_of_the_year    
def lord_of_the_year(jd_at_dob,place,years_from_dob):#,night_time_birth=False):
    """
        Get the Lord of the year/annual chart - Get natal lagna house from birth chart
        @param jd_at_dob: Julin Day Number for the date of birth
        @param place: pancha.Place Struct Place('place name',latitude,longitude,timezone)
        @param years_from_dob:# of years from date of birth.
            For example if Lord of the 25th year from DOB, then years_from_dob=25
        @return:  Lord of the year (planet index) [0..6]
            Note: Rahu/Ketu dont form lord of the year
    """
    rasi_chart = charts.divisional_chart(jd_at_dob, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    natal_lagna_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    #print('natal_lagna_house',natal_lagna_house)
    " Get annual chart "
    jd_at_years = jd_at_dob + years_from_dob*year_value
    tob_hrs = drik.jd_to_gregorian(jd_at_years)[3]
    sunrise = utils.from_dms_str_to_dms(drik.sunrise(jd_at_years, place)[1]) #2.0.3
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = utils.from_dms_str_to_dms(drik.sunset(jd_at_years, place)[1]) # 2.0.3
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    #print('night_time_birth',night_time_birth,sunrise_hrs,tob_hrs,sunset_hrs)
    rasi_chart = charts.divisional_chart(jd_at_years, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    asc_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    #print('asc_house',asc_house)
    candidates = _get_lord_candidates(rasi_chart,years_from_dob,natal_lagna_house,night_time_birth)
    return _get_the_lord_of_tajaka_chart(jd_at_years, place,candidates)
def lord_of_the_month(jd_at_dob,place,years_from_dob,months_from_dob):
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
    rasi_chart = charts.divisional_chart(jd_at_dob, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    natal_lagna_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    #print('natal_lagna_house',natal_lagna_house)
    lord_of_year = lord_of_the_year(jd_at_dob, place, years_from_dob)
    jd_at_years = jd_at_dob + (years_from_dob+months_from_dob/12.0)*year_value
    
    tob_hrs = drik.jd_to_gregorian(jd_at_years)[3]
    sunrise = utils.from_dms_str_to_dms(drik.sunrise(jd_at_years, place)[1]) #2.0.3
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = utils.from_dms_str_to_dms(drik.sunset(jd_at_years, place)[1]) #2.0.3
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    #print('night_time_birth',night_time_birth,sunrise_hrs,tob_hrs,sunset_hrs)
    rasi_chart = charts.divisional_chart(jd_at_years, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    asc_house = tajaka_chart_p_to_h[const._ascendant_symbol]
    #print('asc_house',asc_house)
    candidates = _get_lord_candidates(rasi_chart,years_from_dob,natal_lagna_house,night_time_birth)
    candidates += [lord_of_year]
    return _get_the_lord_of_tajaka_chart(jd_at_years, place,candidates)
def both_planets_within_their_deeptamsa(planet_positions,planet1,planet2):
    """
        Check if two planets are within their deeptamsa
        @param planet_positions: Planet Positions in the format [[planet,(raasi,longitude)],...]
        @param planet1: First planet index
        @param planet2: Second planet index comapred against
        @return: True/False, Ithasala Type
            Ithasala Type: 1. Varthamaana ithasala, 2. Bhavishya ithasala, 3. Poorna ithasala
    """
    planet1_long_within_raasi = planet_positions[planet1+1][1][1]
    planet2_long_within_raasi = planet_positions[planet2+1][1][1]
    ithasala_type = None
    planet1_deeptamsa_start,planet1_deeptamsa_end = utils.deeptaamsa_range_of_planet(planet1,planet1_long_within_raasi)
    planet2_deeptamsa_start,planet2_deeptamsa_end = utils.deeptaamsa_range_of_planet(planet2,planet2_long_within_raasi)
    chk1 = planet1_long_within_raasi >= planet2_deeptamsa_start and planet1_long_within_raasi <= planet2_deeptamsa_end
    chk1_1 = False
    if not chk1: #Check for bhavishya ithasala
        chk1_1 = abs(planet1_long_within_raasi-planet2_deeptamsa_start)<=1.0 or abs(planet1_long_within_raasi - planet2_deeptamsa_end)<=1.0
    #print('deeptamsa test',planet1,'in house',planet1_house,planet2_deeptamsa_start,planet2_deeptamsa_end,'planet1_long_within_raasi',planet1_long_within_raasi,'chk1',chk1)
    chk2 = planet2_long_within_raasi >= planet1_deeptamsa_start and planet2_long_within_raasi <= planet1_deeptamsa_end
    chk2_1 = False
    if not chk2: #Check for bhavishya ithasala
        chk2_1 = abs(planet2_long_within_raasi-planet1_deeptamsa_start)<=1.0 or abs(planet2_long_within_raasi - planet1_deeptamsa_end)<=1.0
    #print('deeptamsa test',planet2,'in house',planet2_house,planet1_deeptamsa_start,planet1_deeptamsa_end,'planet1_long_within_raasi',planet2_long_within_raasi,'chk2',chk2)
    ithasala = chk1 and chk2
    if ithasala:
        ithasala_type = 1 # Varthamaana
    elif (chk1 and chk2_1) or (chk2 and chk1_1):
        ithasala_type = 3 # Bhavishya
        ithasala = True
    if abs(planet1_long_within_raasi-planet2_long_within_raasi) <= 1.0:
        ithasala_type = 2 # Poorna ithasala
    return ithasala,ithasala_type
def both_planets_approaching(planet_positions,planet1,planet2):
    """
        Check if two planets are approaching each other
        NOTE: TODO: Check if planets in retrograde so they are moving away
        @param planet_positions: Planet Positions in the format [[planet,(raasi,longitude)],...]
        @param planet1: First planet index
        @param planet2: Second planet index comapred against
        @return: True/False
    """
    planet1_long_within_raasi = planet_positions[planet1+1][1][1]
    planet2_long_within_raasi = planet_positions[planet2+1][1][1]
    " Check speed of their planets and their advancement within raasi - faster planet less advanced"
    faster_planet = planet1
    if const.order_of_planets_by_speed.index(planet1) < const.order_of_planets_by_speed.index(planet2):
        faster_planet = planet2
    advanced_planet = planet1
    if planet1_long_within_raasi < planet2_long_within_raasi:
        advanced_planet = planet2
    #retrograde_planets = charts.planets_in_retrograde(planet_positions)
    #print('retrograde_planets',retrograde_planets,'faster planet',faster_planet,'advanced planet',advanced_planet)
    chk3_1 = (advanced_planet==planet2) and (faster_planet==planet1)
    chk3_2 = (advanced_planet==planet1) and (faster_planet==planet2)
    chk3 = chk3_1 or chk3_2
    #print('deeptamsa test',planet1,'is faster?',chk3_1,' OR ',planet2,'is faster?',chk3_2,'chk3',chk3)
    return chk3    
    """
    TODO: Implement retrogression in this ithasala yoga calculation
    # Retrograde check - following combinations for approaching
    # L is faster/forward R is slower/forward/backward
    # L is slower/forward R is faster backward
    # L is slower backward and R is faster backward
    chk4_1 = (planet1 not in retrograde_planets) and (planet1 == faster_planet)
    print('(planet1 not in retrograde_planets) and (planet1 == faster_planet)',chk4_1)
    chk4_2 = (planet2==faster_planet and planet2 in retrograde_planets)
    print('(planet2==faster_planet and planet2 in retrograde_planets)',chk4_2)
    chk4 = chk4_1 or chk4_2
    """
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.chapter_27_tests()
    