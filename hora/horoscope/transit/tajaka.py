""" To calculate Tajaka - Annual, monthly, sixty-hour, charts """
import swisseph as swe
from hora import const,utils
from hora.panchanga import panchanga
from hora.horoscope.chart import charts, house

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
    map = sqp+cop+opp#sum(sqp+cop+opp,[])
    return mah,map
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
    map = sqp+cop+opp#sum(sqp+cop+opp,[])
    return mah,map
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
def planets_have_aspects(house_planet_dict,planet1,planet2):
    """
        Return True/False if planet1 and planet2 have ANU aspects on each other
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
def annual_chart(jd_at_dob,place,divisional_chart_factor=1,years=1):
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
    jd_years = jd_at_dob + years*const.sidereal_year
    cht = _get_tajaka_chart(jd_years,place,divisional_chart_factor)
    return cht
def _get_tajaka_chart(jd,place,divisional_chart_factor):
    charts.divisional_chart(jd,place,divisional_chart_factor)
def maasa_pravesh(jd_at_dob,place,divisional_chart_factor=1,years=1,months=1):
    return monthly_chart(jd_at_dob,place,divisional_chart_factor,years,months)
def monthly_chart(jd_at_dob,place,divisional_chart_factor=1,years=1,months=1):
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
    jd_years = jd_at_dob + (years + months/12.0)*const.sidereal_year
    cht = _get_tajaka_chart(jd_years,placedivisional_chart_factor)
    return cht
def sixty_hour_chart(jd_at_dob,place,divisional_chart_factor=1,years=1,months=1,sixty_hour_count=1):
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
    jd_years = jd_at_dob + (years + months/12.0+sixty_hour_count/144.0)*const.sidereal_year
    cht = _get_tajaka_chart(jd_years,place,divisional_chart_factor)
    return cht
#def harsha_bala(tajaka_planet_positions,new_year_daytime_start=True):
#    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(tajaka_chart)
def harsha_bala(p_to_h,new_year_daytime_start=True):
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
    #print(p_to_h)
    asc_house = p_to_h['L']
    harsha_bala = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h[p]
        h_f_a = (p_to_h[p]-asc_house)%12
        #print('planet',p,'house',h_p,'house from asc',h_f_a)
        " Rule-1 - planets in their harsha bala houses"
        if const.harsha_bala_houses[p] == h_f_a:
            #print('rule-1',p,'in',h_f_a)
            harsha_bala[p] +=5
        " Rule-2 - exhalted planets in their own house "
        if const.house_strengths_of_planets[p][h_p] > const._FRIEND or h_p in const.house_lords_dict[p]: # Exhalted or Own
            #print('rule-2',p,'is exhalted or in own house')
            harsha_bala[p]+= 5
        " Rule-3 Feminine"
        if p in const.feminine_planets and h_f_a in const.harsha_bala_feminine_houses:
            #print('rule-3',p,'is feminine planet and in prescribed house')
            harsha_bala[p] += 5
        elif p in const.masculine_planets and h_f_a in const.harsha_bala_masculine_houses:
            #print('rule-3',p,'is masculine planet and in prescribed house')
            harsha_bala[p] += 5
        "Rule-4 "
        if new_year_daytime_start and p in const.masculine_planets:
            #print('rule-4',p,'daytime and masculine')
            harsha_bala[p] += 5
        elif not new_year_daytime_start and p in const.feminine_planets:
            #print('rule-4',p,'nighttime and feminine')
            harsha_bala[p] += 5
    return harsha_bala
def _kshetra_bala(p_to_h_of_rasi_chart):
    kb = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h_of_rasi_chart[p]
        if const.house_strengths_of_planets[p][h_p] > const._FRIEND:
            kb[p] = 30
        elif const.house_strengths_of_planets[p][h_p] == const._FRIEND:
            kb[p] = 22.5
        elif const.house_strengths_of_planets[p][h_p] == const._NEUTRAL_SAMAM:
            kb[p] = 15
        elif const.house_strengths_of_planets[p][h_p] == const._DEFIBILATED_NEECHAM:
            kb[p] = 7.5
    return kb
def _uchcha_bala(tajaka_planet_positions):
    ub = []
    for p,(h,p_long) in tajaka_planet_positions[1:8]: #exclude 0th element Lagnam and Rahu/Ketu
        pd = const.planet_deep_debilitation_longitudes[p] - p_long
        if pd > 180.0:
            pd = 360.0 - pd
        if const.use_BPHS_formula_for_uccha_bala:
            ub.append(round(pd/3,2)) # Sravali formula
        else:
            ub.append(round(pd/180.0*20.0,2)) # PVR formula
    return ub
def __hadda_points(rasi,p_long,p):
    l_range = const.hadda_lords[rasi]
    hp = [planet for planet,long in l_range if p_long<=long ][0]
    if p == hp:
        return const.hadda_points[0]
    elif hp in const.friendly_planets[p]:
        return const.hadda_points[1]
    elif hp in const.enemy_planets[p]:
        return const.hadda_points[2]
    return 0.0
def _hadda_bala(tajaka_planet_positions):
    hb = [ __hadda_points(h, p_long,p) for p,(h,p_long) in tajaka_planet_positions[1:8]]
    return hb
def _drekkana_bala(p_to_h_of_drekkana_chart):
    kb = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h_of_drekkana_chart[p]
        if const.house_strengths_of_planets[p][h_p] > const._FRIEND:
            kb[p] = 10
        elif const.house_strengths_of_planets[p][h_p]==const._FRIEND:
            kb[p] = 5
        elif const.house_strengths_of_planets[p][h_p]==const._ENEMY:
            kb[p] = 2.5
    return kb
def _navamsa_bala(p_to_h_navamsa_chart):
    kb = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h_navamsa_chart[p]
        if const.house_strengths_of_planets[p][h_p]>const._FRIEND:
            kb[p] = 5
        elif const.house_strengths_of_planets[p][h_p]==const._FRIEND:
            kb[p] = 2.5
        elif const.house_strengths_of_planets[p][h_p]==const._ENEMY:
            kb[p] = 1.25
    return kb
def pancha_vargeeya_bala(jd,place):
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
    rasi_chart = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    #print('rasi chart',rasi_chart)
    p_to_h_of_rasi_chart = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    #print('p_to_h_of_rasi_chart',p_to_h_of_rasi_chart)
    kb = _kshetra_bala(p_to_h_of_rasi_chart)
    #print('kshetra bala',kb)
    ub = _uchcha_bala(rasi_chart)
    #print('uccha bala',ub)
    hb = _hadda_bala(rasi_chart)
    #print('hadda bala',hb)
    drekkana_chart = charts.divisional_chart(jd, place,divisional_chart_factor=3)
    #print('drekkana_chart',drekkana_chart)
    p_to_h_of_drekkana_chart = utils.get_planet_house_dictionary_from_planet_positions(drekkana_chart)
    #print('p_to_h_of_drekkana_chart',p_to_h_of_drekkana_chart)
    db = _drekkana_bala(p_to_h_of_drekkana_chart)
    #print('drekkana bala',db)
    navamsa_chart = charts.divisional_chart(jd, place,divisional_chart_factor=9)
    #print('navamsa_chart',navamsa_chart)
    p_to_h_of_navamsa_chart = utils.get_planet_house_dictionary_from_planet_positions(navamsa_chart)
    #print('p_to_h_of_navamsa_chart',p_to_h_of_navamsa_chart)
    nb = _navamsa_bala(p_to_h_of_navamsa_chart)
    #print('navamsa bala',nb)
    pvb = [kb,ub,hb,db,nb]
    pvb = [round(sum(x)/4.0,2) for x in zip(*pvb)]
    return pvb
def dwadhasa_vargeeya_bala(jd,place):
    """
        Calculates dwadhasa_vargeeya_bala score of the planets
        @param jd: Julian Day Number (of the annual day
        @param place: panchanga.Place struct: Place('place_name',latitude, longitude, timezone) 
        @return:   returns dict of strong (>0) and weak (<0) planets. Also returns list of only strong planets
            Example: {0: -4, 1: 0, 2: -4, 3: 2, 4: 0, 5: -2, 6: 2} [3, 6]
    """
    dvp = {p:0 for p in range(7) }
    for dvf in range(1,13): #D1-D12 charts
        planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=dvf)
        p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
        for p in range(7):
            if const.house_strengths_of_planets[p][p_to_h[p]] >= const._FRIEND:
                dvp[p]+=1
            else:
                dvp[p]-=1
    return dvp,[d for d,v in dvp.items() if v>0]
def _get_lord_candidates(tajaka_chart_p_to_h,years_from_dob,natal_lagna_house,night_time_birth):
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    " Rule-1 Sun-Sign's  or Moon-Sign's Lord?"
    candidates = []
    if night_time_birth:
        candidates.append(const.house_owners[tajaka_chart_p_to_h[1]])
    else:
        candidates.append(const.house_owners[tajaka_chart_p_to_h[0]])
    candidates.append(const.house_owners[natal_lagna_house])
    asc_house = tajaka_chart_p_to_h['L']
    m_house = muntha_house(asc_house,years_from_dob)
    candidates.append(const.house_owners[m_house])
    candidates.append(const.house_owners[asc_house])
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
    asc_house = tajaka_chart_p_to_h['L']
    #print('candidates',candidates)
    asc_house = tajaka_chart_p_to_h['L']
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
    
    pvb = pancha_vargeeya_bala(jd, place)
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
    natal_lagna_house = tajaka_chart_p_to_h['L']
    print('natal_lagna_house',natal_lagna_house)
    " Get annual chart "
    jd_at_years = jd_at_dob + years_from_dob*const.sidereal_year
    tob_hrs = panchanga.jd_to_gregorian(jd_at_years)[3]
    sunrise = panchanga.sunrise(jd_at_years, place, as_string=False)[1]
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = panchanga.sunset(jd_at_years, place, as_string=False)[1]
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    print('night_time_birth',night_time_birth,sunrise_hrs,tob_hrs,sunset_hrs)
    rasi_chart = charts.divisional_chart(jd_at_years, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    asc_house = tajaka_chart_p_to_h['L']
    print('asc_house',asc_house)
    candidates = _get_lord_candidates(tajaka_chart_p_to_h,years_from_dob,natal_lagna_house,night_time_birth)
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
    natal_lagna_house = tajaka_chart_p_to_h['L']
    print('natal_lagna_house',natal_lagna_house)
    lord_of_year = lord_of_the_year(jd_at_dob, place, years_from_dob)
    jd_at_years = jd_at_dob + (years_from_dob+months_from_dob/12.0)*const.sidereal_year
    
    tob_hrs = panchanga.jd_to_gregorian(jd_at_years)[3]
    sunrise = panchanga.sunrise(jd_at_years, place, as_string=False)[1]
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = panchanga.sunset(jd_at_years, place, as_string=False)[1]
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    print('night_time_birth',night_time_birth,sunrise_hrs,tob_hrs,sunset_hrs)
    rasi_chart = charts.divisional_chart(jd_at_years, place,divisional_chart_factor=1)
    tajaka_chart_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    tajaka_chart_h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(tajaka_chart_p_to_h)
    asc_house = tajaka_chart_p_to_h['L']
    print('asc_house',asc_house)
    candidates = _get_lord_candidates(tajaka_chart_p_to_h,years_from_dob,natal_lagna_house,night_time_birth)
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
    # Example 118 Chart 66 Lord of the year should be 2 - Mars
    jd_at_dob = utils.julian_day_number((1996,12,7),(10,34,0))
    years = 26
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = utils.Place('unknown',13.0389,80.2619,5.5)
    cht = charts.divisional_chart(jd_at_dob,place)
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(cht)
    print(house_planet_dict)
    map = []
    planet_list = ['L']+[*range(9)]
    for planet in planet_list:
        map.append(malefic_aspects_of_the_planet(house_planet_dict, planet)[1])
    print(map)
    mapp = []
    for planet in planet_list:
        mapp.append([planet_list[p] for p,plst in enumerate(map) if str(planet) in plst])
    print(mapp)
    exit()
    print(charts.planets_in_retrograde(cht))
    ld = lord_of_the_year(jd_at_dob, place, years_from_dob=years)#,night_time_birth=True)
    print('Lord of the year',ld)
    #exit()
    chart_66 = ['6/4','','','7','','','','','','5/L/8','3/0','2/1']
    print(chart_66)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    print(p_to_h)
    asc_house = p_to_h['L']
    print('asc_house',asc_house)
    lord_of_the_year(jd_at_dob,place,years)
    tah,tap = benefic_aspects_of_the_planet(chart_66, 2)
    print('benefic_aspects_of_the_planet:',2,'on houses',tah,'on planets',tap)
    tah,tap = malefic_aspects_of_the_planet(chart_66, 2)
    print('malefic_aspects_of_the_planet:',2,'on houses',tah,'on planets',tap)
    tah,tap = neutral_aspects_of_the_planet(chart_66, 2)
    print('neutral_aspects_of_the_planet','on houses',tah,'on planets',tap)
    print('planet_has_benefic_aspect_on_house',[planet_has_benefic_aspect_on_house(chart_66, planet, asc_house) for planet in [4,0,5,6,2]])
    print('planet_has_malefic_aspect_on_house',[planet_has_malefic_aspect_on_house(chart_66, planet, asc_house) for planet in [4,0,5,6,2]])
    exit()
    jd_at_dob = panchanga.julian_day_number((1996,12,7),(10,34,0))
    years = 26
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = panchanga.Place('unknown',13.0389,80.2619,5.5)
    divisional_chart_factor = 1
    pvb = pancha_vargeeya_bala(jd_at_years,place)
    print(pvb)
    dvp,dvpp = dwadhasa_vargeeya_bala(jd_at_years,place)
    print('dwadhasa_vargeeya_bala',dvp,dvpp)
    exit()
    cht=charts.divisional_chart(jd_at_years, place,divisional_chart_factor)
    print(cht)
    ub = _uchcha_bala(cht)
    print('uccha bala',ub)
    hb = _hadda_bala(cht)
    print('hadda bala',hb)
    d3_cht=charts.divisional_chart(jd_at_years, place,divisional_chart_factor=3)
    print('d3 chart',d3_cht)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(d3_cht)
    print('d3 ptoh',p_to_h)
    db = _drekkana_bala(p_to_h)
    print('drekana bala',db)
    d9_cht=charts.divisional_chart(jd_at_years, place,divisional_chart_factor=9)
    print('d9 chart',d9_cht)
    p_to_h_navamsa = utils.get_planet_house_dictionary_from_planet_positions(d9_cht)
    print('D9 ptoh',p_to_h_navamsa)
    nb = _navamsa_bala(p_to_h_navamsa)
    print('navamsa bala',nb)
    exit()
    h_to_p = utils.get_house_planet_list_from_planet_positions(cht)
    print(h_to_p)
    p_to_h  = utils.get_planet_house_dictionary_from_planet_positions(cht)
    print(p_to_h)