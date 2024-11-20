#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import swisseph as swe
import numpy as np
""" Module describing PyJHora constants"""
" setup paths "
_sep = os.path.sep
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_IMAGES_PATH = os.path.dirname(ROOT_DIR+_sep+"images"+_sep)
_IMAGE_ICON_PATH=os.path.join(ROOT_DIR,_sep+"images"+_sep+"lord_ganesha2.jpg")
_INPUT_DATA_FILE = os.path.join(ROOT_DIR,'data'+_sep+'program_inputs.txt')
_world_city_csv_file = os.path.join(ROOT_DIR,'data'+_sep+'world_cities_with_tz.csv')
_open_elevation_api_url = lambda lat,long:f'https://api.open-elevation.com/api/v1/lookup?locations={lat},{long}'
_EPHIMERIDE_DATA_PATH = os.path.join(ROOT_DIR,'data'+_sep+'ephe'+_sep)
_LANGUAGE_PATH = os.path.join(ROOT_DIR,'lang'+_sep)
_DEFAULT_LANGUAGE = 'en'
_DEFAULT_LANGUAGE_LIST_STR = 'list_values_'
_DEFAULT_LANGUAGE_MSG_STR = 'msg_strings_'
_DEFAULT_YOGA_JSON_FILE_PREFIX = "yoga_msgs_" 
_DEFAULT_RAJA_YOGA_JSON_FILE_PREFIX = "raja_yoga_msgs_" 
_DEFAULT_DOSHA_JSON_FILE_PREFIX = "dosha_msgs_" 
_DEFAULT_PREDICTION_JSON_FILE_PREFIX = "prediction_msgs_" 
_INCLUDE_URANUS_TO_PLUTO = True # Only for Western Charts
_degree_symbol = "°" 
_minute_symbol = u'\u2019'
_second_symbol = '"'
_retrogade_symbol = '℞'
_ascendant_symbol = 'L'
" Planet names mapped to swiss ephemerides "
_KETU = -swe.MEAN_NODE
_RAHU = swe.MEAN_NODE
_SUN = swe.SUN; SURYA = _SUN 
_MOON = swe.MOON; CHANDRA = _MOON
_MARS = swe.MARS; KUJA = _MARS
_MERCURY = swe.MERCURY; BUDHA = _MERCURY
_JUPITER = swe.JUPITER; GURU = _JUPITER
_VENUS = swe.VENUS; SUKRA = _VENUS
_SATURN = swe.SATURN; SANI = _SATURN
_URANUS = swe.URANUS
_NEPTUNE = swe.NEPTUNE
_PLUTO = swe.PLUTO
_pp_count_upto_saturn = 8; _pp_count_upto_ketu = 10; _pp_count_upto_rahu = 9
_planets_upto_ketu = 9; _planets_upto_saturn = 7; _planets_upto_rahu = 8
""" Surya Siddhantha Constants """
planet_mean_revolutions_at_kali = {_SUN: 4320000,_MOON:57753336,_MARS: 2296832,_MERCURY: 17937060,
                                   _JUPITER:364220,_VENUS:7022376,_SATURN:146568,_RAHU:232238,_KETU:232238,
                                   _URANUS:51417, _NEPTUNE:26219, _PLUTO:17390}
mean_revolutions_sun_kali = 4320000
mean_revolutions_moon_kali = 57753336
mean_revolutions_rahu_kali = 232238
moon_mandocca_revolutions = 488203
sun_mandocca_revolutions = 0.387 # 387 revolutions in a Kalpa
mandakendrajya_indian_sine_radius = 3438/60.0
planet_eccentricity = {_SUN:0.01675104,_MOON:0.0549,_MARS:0.093,_MERCURY:0.206,_JUPITER:0.048,_VENUS:0.007,_SATURN:0.056,_URANUS:0.047,_NEPTUNE:0.009,_PLUTO:0.248}
#planet_eccentricity_coefficients = {p:((2.0*e-0.25*pow(e,3)),(1.25*pow(e,2)-11.0/24.0*pow(e,4))) for p,e in planet_eccentricity.items()}
planet_eccentricity_coefficients={_SUN: (0.03350090492567891, 0.0003507105895375814), 
                                  _MOON: (0.10975863271274999, 0.003763348882538287), 
                                  _MARS: (0.18579891075, 0.010776964282875001), 
                                  _MERCURY: (0.409814546, 0.05221962687266666), 
                                  _JUPITER: (0.095972352, 0.0028775669760000002), 
                                  _VENUS: (0.01399991425, 6.124889954166668e-05), 
                                  _SATURN: (0.111956096, 0.003915492522666667), 
                                  _URANUS: (0.09397404425, 0.0027590134795416666), 
                                  _NEPTUNE: (0.017999817749999997, 0.00010124699287499999), 
                                  _PLUTO: (0.492186752, 0.07514624324266665)}
""" mandaphala = E1 * sin(M) + E2 * sin (2M) - where M is manda anomaly  E1,E2 are above coefficients """

planet_mandaphala_periphery = {_SUN:14.0,_MOON:32.0,_MARS:(72.0,75.0),_MERCURY:(28.0,30),_JUPITER:(32.0,33.0),_VENUS:(11.0,12.0),_SATURN:(48.0,49.0)}
planet_mandaphala_periphery_modern = {_SUN:(11.78,12.29),_MOON:(36.98,42.43),_MARS:(60.27,76.20),_MERCURY:(117.72,198.19),_JUPITER:(32.77,36.97),_VENUS:(4.8,4.88),_SATURN:(36.28,41.52)}
planet_sighra_peripheries = {_MARS:(232.0,235.0),_MERCURY:(132.0,133.0),_JUPITER:(72.0,70.0),_VENUS:(260.0,262.0),_SATURN:(40.0,39.0)}
civil_days_in_mahayuga = 1577917828
daily_mean_motions_1 = [0.0+59.0/60+8/3600.0+10.0/2160600+9.7/12960000, 
                      13.0+10.0/60+34/3600.0+52.0/2160600+2./12960000,
                      0.0+31.0/60+26/3600.0+28.0/2160600+10./12960000,
                      4.0+5.0/60+32/3600.0+20.0/2160600+42./12960000,
                      0.0+4.0/60+59/3600.0+8.0/2160600+48./12960000,
                      1.0+36.0/60+7/3600.0+43.0/2160600+37./12960000,
                      0.0+2.0/60+0.0/3600.0+22.0/2160600+53./12960000,
                      -0.0-3.0/60-10/3600.0-44.0/2160600-43./12960000, # << Rahu
                      -0.0-3.0/60-10/3600.0-44.0/2160600-43./12960000, # << Ketu
                     ]
daily_mean_motions = {_SUN:0.9855609323563241, _MOON:13.176135332820786, _MARS:0.5240193,
                      _MERCURY: 4.0923181,_JUPITER: 0.0830963,_VENUS: 1.6021464,
                      _SATURN: 0.0334393,_RAHU: -0.05280146039251785, _KETU: -0.05280146039251785}
planet_mean_longitudes = {_SUN:0.0,_MOON:0.0, _MARS:0.0,_MERCURY:0.0,_JUPITER:0.0,_VENUS:0.0,_SATURN:0.0,_RAHU:0.0,_KETU:0.0}
moon_apogee_mean_motion = 6.684/60 # minutes
ujjain_lat_long = [23.1765, 75.7885]
planet_mean_positions_at_kali = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,180.0] # Sun to Rahu
manodcca_positions_at_kali = {_SUN:77.13,_MOON:90.0,_MARS:129.96,_MERCURY:220.32,_JUPITER:171.0,_VENUS:79.65,_SATURN:236.61,
                              _RAHU:180.0,_KETU:180.0}
madocca_revolutions = {_SUN:0.387,_MOON:488203,_MARS:204,_MERCURY:0.368,_JUPITER:0.900,_VENUS:0.535,_SATURN:0.039}
mandocca_sun_at_kali = 77.13 #77.0+7.0/60+48/3600.0
mandocca_moon_at_kali = 90.0

_planet_symbols=['ℒ','☉','☾','♂','☿','♃','♀','♄','☊','☋']
_zodiac_symbols = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D', '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653']

available_languages = {"English":'en','Tamil':'ta','Telugu':'te','Hindi':"hi",'Kannada':'ka',}
" declare constants "
"""
# Planet Rulers of the 8 parts of the DAY and NIGHT
# Column = Weekday (0=Sun,1=Mon..7=Sat)
# Row= part of the day (0-7) =< (1st-8th) part of the day
# Value of the cell is the planet 0=>Sun, 1=>Moon, .. 6=>Saturn) 
# -1 means no ruler at that part of the day
"""
day_rulers = [[0,1,2,3,4,5,6,-1],[1,2,3,4,5,6,-1,0],[2,3,4,5,6,-1,0,1],[3,4,5,6,-1,0,1,2],[4,5,6,-1,0,1,2,3],[5,6,-1,0,1,2,3,4],[6,-1,0,1,2,3,4,5]]
night_rulers = [[4,5,6,-1,0,1,2,3],[5,6,-1,0,1,2,3,4],[6,-1,0,1,2,3,4,5],[0,1,2,3,4,5,6,-1],[1,2,3,4,5,6,-1,0],[2,3,4,5,6,-1,0,1],[3,4,5,6,-1,0,1,2]]
division_chart_factors = [1,2,3,4,5,6,7,8,9,10,11,12,16,20,24,27,30,40,45,60,81,108,144]
dhasavarga_amsa_vimsopaka = {1:3,2:1.5,3:1.5,7:1.5,9:1.5,10:1.5,12:1.5,16:1.5,30:1.5,60:5}
shadvarga_amsa_vimsopaka = {1:6,2:2,3:4,9:5,12:2,30:1}
sapthavarga_amsa_vimsopaka = {1:5,2:2,3:3,7:1,9:2.5,12:4.5,30:2}
shodhasa_varga_amsa_vimsopaka = {1:3.5,2:1,3:1,4:0.5,7:0.5,9:3,10:0.5,12:0.5,16:2,20:0.5,24:0.5,27:0.5,30:1,40:0.5,45:0.5,60:4}
vimsamsa_varga_amsa_factors = division_chart_factors
""" In the order: Own, Adhimitra,Mithra,Neutral/Samam,Sathru,Enemy,Great Enemy/Adhisathru """
vimsopaka_planet_position_values = [20,18,15,10,7,5] 
dhasavarga_amsa_vaiseshikamsa = {1:1,2:1,3:1,7:1,9:1,10:1,12:1,16:1,30:1,60:1}
shadvarga_amsa_vaiseshikamsa = {1:1,2:1,3:1,9:1,12:1,30:1}
sapthavarga_amsa_vaiseshikamsa = {1:1,2:1,3:1,7:1,9:1,12:1,30:1}
shodhasa_varga_amsa_vaiseshikamsa = {1:1,2:1,3:1,4:1,7:1,9:1,10:1,12:1,16:1,20:1,24:1,27:1,30:1,40:1,45:1,60:1}
""" In the order: Own, Adhimitra,Mithra,Neutral/Samam,Sathru,Enemy,Great Enemy/Adhisathru """
vaiseshikamsa_planet_position_values = [20,18,15,10,7,5] 

### String Constants for panchanga.
"""
    set this to =swe.PLUTO  for Vimoshotari functions. BUT KETHU will be SHOWN AS PLUTO DHASA/BHUKTI
    set this to - -10 for chart creation (otherwise chart will show Pluto for Kethu)
    following assignments due to changes in swiss ephe 2.8
    !!! IMPORTANT NOTE !!!
        swiss ephemeris constant values of planets such swe.MARS are different what is used in PyHor
        If PyJHora does not use const. values explicitly it assumes the planet values as follows:
                0 = Sun, 1= Moon, 2=Mars, 6=Saturn 7=Rahu and 8=Ketu
    !!!!!!!!!!!!!!!!!!!!!!!!  
"""
_TROPICAL_MODE = False
_EPHIMERIDE_DATA_PATH = ROOT_DIR+'/data/ephe/'
_LANGUAGE_PATH = ROOT_DIR+'/lang/'
_solar_upagraha_list = ['dhuma','vyatipaata','parivesha','indrachaapa','upaketu']
_other_upagraha_list = ['kaala','mrityu','artha_prabhakara','yama','gulika','maandi']
_special_lagna_list = ['bhava_lagna','hora_lagna','ghati_lagna','vighati_lagna','sree_lagna','varnada_lagna',
                       'pranapada_lagna','indu_lagna','bhrigu_bindhu']

_ephe_path = os.path.abspath(_EPHIMERIDE_DATA_PATH)
swe.set_ephe_path(_ephe_path)
sidereal_year = 365.256364   # From JHora
lunar_year = 354.36707
savana_year = 360
average_gregorian_year = 365.2425
tropical_year = 365.242190#365.242190=>JHora value #PyJHora Value=>365.24219879 
human_life_span_for_dhasa = 120. ## years
# Nakshatra lords, order matters. See https://en.wikipedia.org/wiki/Dasha_(astrology)
adhipati_list = [ 8, 5, 0, 1, 2, 7, 4, 6, 3 ]

# (Maha-)dasha periods (in years)
mahadasa = { 8: 7, 5: 20, 0: 6, 1: 10, 2: 7,7: 18, 4: 16, 6: 19, 3: 17 }

# assert(0 <= nak <= 26)
available_horoscope_calculation_methods = ['drik','ss']
available_ayanamsa_modes = {"FAGAN":swe.SIDM_FAGAN_BRADLEY ,"KP": swe.SIDM_KRISHNAMURTI, "LAHIRI": swe.SIDM_LAHIRI, 
                            "RAMAN": swe.SIDM_RAMAN, "USHASHASHI": swe.SIDM_USHASHASHI, 
                            "YUKTESHWAR": swe.SIDM_YUKTESHWAR, "SURYASIDDHANTA": swe.SIDM_SURYASIDDHANTA,
                            "SURYASIDDHANTA_MSUN": swe.SIDM_SURYASIDDHANTA_MSUN, "ARYABHATA":swe.SIDM_ARYABHATA, 
                            "ARYABHATA_MSUN":swe.SIDM_ARYABHATA_MSUN,"SS_CITRA":swe.SIDM_SS_CITRA, 
                            "TRUE_CITRA":swe.SIDM_TRUE_CITRA, "TRUE_REVATI":swe.SIDM_TRUE_REVATI,
                            "SS_REVATI": swe.SIDM_SS_REVATI,'SENTHIL':'', "TRUE_LAHIRI":swe.SIDM_TRUE_CITRA,
                            "TRUE_PUSHYA":swe.SIDM_TRUE_PUSHYA, "TRUE_MULA":swe.SIDM_TRUE_MULA,
                            "KP-SENTHIL":swe.SIDM_KRISHNAMURTI_VP291,
                            "SIDM_USER":swe.SIDM_USER,'SUNDAR_SS':'',
                            #"ARYABHATA_522":swe.SIDM_ARYABHATA_522, 
                            }
_DEFAULT_AYANAMSA_MODE = 'LAHIRI' #'TRUE_CITRA'
human_life_span_for_vimsottari_dhasa = 120
# Nakshatra lords, order matters. See https://en.wikipedia.org/wiki/Dasha_(astrology)
 # Nak Lord Order: Aswini(Rahu),Bharani(Mars),Krithika(Moon),Rohini(Sun),Mrigasira(Venus),Ardra(Ketu),...
vimsottari_adhipati_list = [ 8, 5, 0, 1, 2, 7, 4, 6, 3 ]
# In the above Dhasa Seed for Ketu is Aswini. As variations we can choose any star as the Starting Dhasa Lord for Ketu
# And the next stars will be for Venus, Sun etc..

# (Maha-)dasha periods (in years)
vimsottari_dict = { 8: 7, 5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17 }

varsha_vimsottari_days = {0:18, 1:30, 2:21, 7:54, 4:48,6:57, 3:51, 8:21, 5:60}
varsha_vimsottari_adhipati_list = list(varsha_vimsottari_days.keys())
human_life_span_for_varsha_vimsottari_dhasa = sum(varsha_vimsottari_days.values())
#varsha_vimsottari_adhipati_list = [0, 1, 2, 7, 4, 6, 3, 8, 5]
# assert(0 <= nak <= 26)
# Return nakshatra lord (adhipati)
rasi_names_en = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
savya_stars_1 = [0,2,6,8,12,14,18,20,24]
savya_stars_2 = [1,7,13,19,25,26]
apasavya_stars_1 = [3,9,15,21]
apasavya_stars_2 = [4,5,10,11,16,17,22,23]
kalachakra_stars = [savya_stars_1,savya_stars_2,apasavya_stars_1,apasavya_stars_2]
kalachakra_dhasa_duration = [7,16,9,21,5,9,16,7,10,4,4,10]
savya_stars_1_rasis =[[0,1,2,3,4,5,6,7,8],[9,10,11,7,6,5,3,4,2],[1,0,11,10,9,8,0,1,2],[3,4,5,6,7,8,9,10,11]]
savya_stars_1_rasis_paramayush=[100,85,83,86]
savya_stars_2_rasis =[[7,6,5,3,4,2,1,0,11],[10,9,8,0,1,2,3,4,5],[6,7,8,9,10,11,7,6,5],[3,4,2,1,0,11,10,9,8]]
savya_stars_2_rasis_paramayush=savya_stars_1_rasis_paramayush
apasavya_stars_1_rasis=[[8,9,10,11,0,1,2,4,3],[5,6,7,11,10,9,8,7,6],[5,4,3,2,1,0,8,9,10],[11,0,1,2,4,3,5,6,7]]
apasavya_stars_1_rasis_paramayush=[86,83,85,100]
apasavya_stars_2_rasis=[[11,10,9,8,7,6,5,4,3],[2,1,0,8,9,10,11,0,1],[2,4,3,5,6,7,11,10,9],[8,7,6,5,4,3,2,1,0]]
apasavya_stars_2_rasis_paramayush=apasavya_stars_1_rasis_paramayush
kalachakra_rasis = [savya_stars_1_rasis,savya_stars_2_rasis,apasavya_stars_1_rasis,apasavya_stars_2_rasis]
kalachakra_rasis_list = sum(savya_stars_1_rasis,[])+sum(savya_stars_2_rasis,[])+sum(apasavya_stars_1_rasis,[])+sum(apasavya_stars_2_rasis,[])
#print(kalachakra_rasis_list)

kalachakra_paramayush = [savya_stars_1_rasis_paramayush,savya_stars_2_rasis_paramayush,apasavya_stars_1_rasis_paramayush,apasavya_stars_2_rasis_paramayush]
ashtaka_varga_dict={ #7 is used for Lagna here
    "0":[[1,2,4,7,8,9,10,11],[3,6,10,11],[1,2,4,7,8,9,10,11],[3,5,6,9,10,11,12],[5,6,9,11],[6,7,12],[1,2,4,7,8,9,10,11],[3,4,6,10,11,12]],
    "1":[[3,6,7,8,10,11 ],[1,3,6,7,9,10,11],[2,3,5,6,10,11],[1,3,4,5,7,8,10,11],[1,2,4,7,8,10,11],[3,4,5,7,9,10,11],[3,5,6,11],[3,6,10,11]],
    "2":[[3,5,6,10,11],[3,6,11],[1,2,4,7,8,10,11],[3,5,6,11],[6,10,11,12],[6,8,11,12],[1,4,7,8,9,10,11],[1,3,6,10,11]],
    "3":[[5,6,9,11,12],[2,4,6,8,10,11],[1,2,4,7,8,9,10,11],[1,3,5,6,9,10,11,12],[6,8,11,12],[1,2,3,4,5,8,9,11],[1,2,4,7,8,9,10,11],[1,2,4,6,8,10,11]],
    "4":[[1,2,3,4,7,8,9,10,11],[2,5,7,9,11],[1,2,4,7,8,10,11],[1,2,4,5,6,9,10,11],[1,2,3,4,7,8,10,11],[2,5,6,9,10,11],[3,5,6,12],[1,2,4,5,6,7,9,10,11]],
    "5":[[8,11,12],[1,2,3,4,5,8,9,11,12],[3,4,6,9,11,12],[3,5,6,9,11],[5,8,9,10,11],[1,2,3,4,5,8,9,10,11],[3,4,5,8,9,10,11],[1,2,3,4,5,8,9,11]],
    "6":[[1,2,4,7,8,10,11],[3,6,11],[3,5,6,10,11,12],[6,8,9,10,11,12],[5,6,11,12],[6,11,12],[3,5,6,11],[1,3,4,6,10,11]],
    "7":[[3,4,6,10,11,12],[3,6,10,11,12],[1,3,6,10,11],[1,2,4,6,8,10,11],[1,2,4,5,6,7,9,10,11],[1,2,3,4,5,8,9],[1,3,4,6,10,11],[3,6,10,11]] ## This is for Lagna
    }
 #Jupiter/Venus. Mercury benefic if alone or with other benefics. Moon benefic in sukla paksha (tithi <=15)
natural_benefics = [4,5] 
natural_malefics = [0,2,6,7,8]
""" TODO: Check some of the following female planets should go to neutral planets 
    It will impact Harsha Bala calculations as well.
"""
feminine_planets = [1,3,5,6]
masculine_planets = [0,2,4]
harsha_bala_houses = [8,2,5,0,10,11,11]
harsha_bala_feminine_houses = [0,1,2,6,7,8]
harsha_bala_masculine_houses = [3,4,5,9,10,11]
" house module constants " #V2.3.0
nakshathra_lords = {_KETU:(0,9,18), _VENUS:(1,10,19), _SUN:(2,11,20), _MOON:(3,12,21), _MARS:(4,13,22), _RAHU:(5,14,23), 
                    _JUPITER:(6,15,24), _SATURN:(7,16,25), _MERCURY:(8,17,26)}

house_lords_dict = {0:[4],1:[3],2:[0,7],3:[2,5],4:[8,11],5:[1,6],6:[9,10],7:[10],8:[7]}
houses_of_rahu_kethu = {7:10,8:7}
#Ar Ta Ge Cn Le Vi Li Sc Sg Cp Aq Pi
#Sc Ge Cp Sg Cn Aq Ta Sg Cn Ge Cp Le
rudra_eighth_house = [7,2,9,8,3,10,1,8,3,2,9,4]
# Uccham = Exhalted  Neecham = Debilated
_OWNER_RULER = 5
_EXALTED_UCCHAM = 4
_FRIEND = 3
_NEUTRAL_SAMAM = 2
_ENEMY = 1
_DEFIBILATED_NEECHAM = 0
house_strength_types = {5:'Ruler/Owner/Lord',4:'Uccham/Exalted',3:'Friend',2:'Samam',1:'Enemy',0:'Neecham/Defibilated'}
house_strengths_of_planets=[[4,1,2,2,5,2,0,3,3,1,1,3],
                            [2,4,3,5,3,3,2,0,2,2,2,2],
                            [5,2,1,0,3,1,2,5,3,4,2,3],
                            [2,3,5,1,3,5,3,2,2,2,2,0],
                            [3,1,1,4,3,3,1,3,5,0,2,5],
                            [2,5,3,1,1,0,5,2,3,3,3,4],
                            [0,3,3,1,1,3,4,1,2,5,5,2],
                            [1,0,3,1,1,3,3,4,3,3,1,3],
                            [1,0,3,1,1,3,3,4,3,3,1,3]]
moola_trikona_of_planets = [4,1,0,5,8,6,10,5,11]
temporary_friend_raasi_positions = [1,2,3,9,10,11]
temporary_enemy_raasi_positions = [0,4,5,6,7,8]
friend_enemy_addition =   [[0.5, 0],
                           [0  , 0],
                           [0, -0.5]
                          ] 
"""
        Table 8: Compound Relationships
                Temporary friend             Temporary enemy
Natural friend     Adhimitra (good friend)     Sama (neutral)
Natural neutral     Mitra (friend)             Satru (enemy)
Natural enemy       Sama (neutral)             Adhisatru (bad enemy)
"""
compound_relations_of_planets = [[5,3],[4,2],[3,1]]
""" 5: AdhiMitra/GreatFriend 4:Mitra/Friend 3: Neutral/Samam 2: Satru/Enemy 1: AdhiSatru/GreatEnemy """
_ADHIMITRA_GREATFRIEND = 5
_MITHRA_FRIEND = 4
_SAMAM_NEUTRAL = 3
_SATHRU_ENEMY = 2
_ADHISATHRU_GREATENEMY = 1
compound_planet_relations = [[-1,5,5,4,3,3,3,3,3], # Sun
                             [5,-1,2,5,2,2,4,1,1], # Moon
                             [5,3,-1,3,3,2,4,1,5], # Mars
                             [5,3,4,-1,2,5,2,4,2], # Mercury
                             [3,3,3,1,-1,1,2,3,4], # Jupiter
                             [3,1,2,5,2,-1,5,3,5], # Venus
                             [3,3,3,3,2,5,-1,5,1], # Saturn
                             [3,1,1,4,2,3,5,-1,1], # Rahu
                             [3,1,5,2,4,5,1,1,-1]] # Ketu
""" 3:'Friend',2:'Samam',1:'Enemy' """
planet_relations = [ [5,3,3,2,3,1,1,1,2],
                     [3,5,2,3,2,2,2,2,2],
                     [3,3,5,1,3,2,2,2,2],
                     [3,1,2,5,2,3,2,2,1],
                     [3,3,3,1,5,1,2,1,2],
                     [1,1,2,3,2,5,3,3,2],
                     [1,1,1,3,2,3,5,3,1],
                     [1,1,1,2,2,3,3,5,2],
                     [3,2,3,2,2,1,1,2,5]
                   ]
friendly_planets = []
for row in planet_relations:
    fp = []
    for c,col in enumerate(row):
        if _FRIEND == col:
            fp.append(c)
    friendly_planets.append(fp)
neutral_planets = []
for row in planet_relations:
    fp = []
    for c,col in enumerate(row):
        if _NEUTRAL_SAMAM == col:
            fp.append(c)
    neutral_planets.append(fp)
enemy_planets = []
for row in planet_relations:
    fp = []
    for c,col in enumerate(row):
        if _ENEMY == col:
            fp.append(c)
    enemy_planets.append(fp)
#print('planet_relations',planet_relations)
#print('friendly_planets',friendly_planets)
#print('neutral_planets',neutral_planets)
#print('enemy_planets',enemy_planets)
#"""
_friendly_planets = [[1,2,4],[0,3],[0,1,4],[0,5],[0,1,2],[3,6],[3,5]]
_neutral_planets = [[3],[2,4,5,6],[5,6],[2,4,6],[6],[2,4],[4]]
_enemy_planets = [[5,6],[],[3],[1],[3,5],[0,1],[0,1,2]]
#"""
house_owners = np.where(np.array(house_strengths_of_planets).transpose()==_OWNER_RULER)[1]
_house_owners_list = [2,5,3,1,0,3,5,2,4,6,6,4]
planet_deep_exaltation_longitudes = [10.0,33.0,298.0,165.0,95.0,357.0,200.0]
planet_deep_debilitation_longitudes = [(e+180.0)%360 for e in planet_deep_exaltation_longitudes]
graha_drishti = {0:[7],1:[7],2:[4,7,8],3:[7],4:[5,7,9],5:[7],6:[3,7,10],7:[7],8:[7],9:[],10:[],11:[]}
movable_signs = [0,3,6,9]
fixed_signs = [1,4,7,10]
dual_signs = [2,5,8,11]
longevity = {0:[(0,0),(1,2),(2,1)],1:[(0,1),(1,0),(2,2)],2:[(0,2),(1,1),(2,0)]} #0=>Fixed, 1=> Movable, 2=>Dual
longevity_years = [[32,36,40],[64,72,80],[96,108,120]] # 0th element Short Life, 1st : Middle Life, 2nd element: Long Life
odd_signs = [0,2,4,6,8,10] # => 1,3,5,7,9,11
even_signs = [1,3,5,7,9,11]# 2,4,6,8,10, 12
odd_footed_signs = [0,1,2,6,7,8]
even_footed_signs = [3,4,5,9,10,11]
fire_signs = [0,4,8]
earth_signs = [1,5,9]
air_signs = [2,6,10]
water_signs = [3,7,11]
space_signs = [*range(12)]
pittha_nature_signs = [0,4,8]
vaatha_nature_signs = [1,5,9]
kapa_nature_signs = [3,7,11]
mixed_nature_signs = [2,6,10]
east_signs = [0,4,8]
south_signs = [1,5,9]
west_signs = [2,6,10]
north_signs = [3,7,11]
nara_rasi_longitudes = [(60,90),(150,180),(180,210),(240,255),(300,330)] # Rasi and longitude range
jalachara_rasi_longitudes = [(90,120),(285,300),(330,360)]
chatushpada_rasis = [(0,30),(30,60),(120,150),(255,270),(270,285)]
keeta_rasis = [(210,240)]

argala_houses = [2,4,5,11]
argala_houses_str = ['2nd','4th','5th','11th']
virodhargala_houses = [12,10,9,3] # respectively to argala houses [2,4,11,5]
virodhargala_houses_str = ['12th','10th','9th','3rd']
houses_str = ['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th']
" Tajaka constants"
hadda_lords = [[(4,6),(5,12),(3,20),(2,25),(6,30)], #Aries (planet, long_degree_max
               [(5,8),(3,14),(5,22),(6,27),(2,30)], #Taurus
               [(3,6),(5,12),(4,17),(2,24),(6,30)], #Gemini
               [(2,7),(5,13),(3,19),(4,26),(6,30)], #Cancer
               [(4,6),(5,11),(6,18),(3,24),(2,30)], #Leo
               [(3,7),(5,17),(4,21),(2,28),(6,30)], #Virgo
               [(6,6),(3,14),(4,21),(5,28),(2,30)], #Libra
               [(2,7),(5,11),(3,19),(4,24),(6,30)], #Scorpio
               [(4,12),(5,17),(3,21),(2,26),(6,30)], #Sagitarius
               [(3,7),(4,14),(5,22),(6,26),(2,30)], #Capricorn
               [(3,7),(5,13),(4,20),(2,25),(6,50)], #Aquarius
               [(5,12),(4,16),(3,19),(2,28),(6,30)]] #Pisces
hadda_points = [15,7.5,3.75] # [15,11.5,7.5,3.75] # Own, Friend, Enemy, Neutral
" Narayana Dhasa constants "
human_life_span_for_narayana_dhasa = 120
narayana_dhasa_normal_progression = \
    [[0,1,2,3,4,5,6,7,8,9,10,11],
    [1,8,3,10,5,0,7,2,9,4,11,6],
    [2,10,6,5,1,9,8,4,0,11,7,3],
    [3,2,1,0,11,10,9,8,7,6,5,4],
    [4,9,2,7,0,5,10,3,8,1,6,11],
    [5,9,1,2,6,10,11,3,7,8,0,4],
    [6,7,8,9,10,11,0,1,2,3,4,5],
    [7,2,9,4,11,6,1,8,3,10,5,0],
    [8,4,0,11,7,3,2,10,6,5,1,9],
    [9,8,7,6,5,4,3,2,1,0,11,10],
    [10,3,8,1,6,11,4,9,2,7,0,5],
    [11,3,7,8,0,4,5,9,1,2,6,10]]
narayana_dhasa_saturn_exception_progression = \
    [[0,1,2,3,4,5,6,7,8,9,10,11],
    [1,2,3,4,5,6,7,8,9,10,11,0],
    [2,3,4,5,6,7,8,9,10,11,0,1],
    [3,4,5,6,7,8,9,10,11,0,1,2],
    [4,5,6,7,8,9,10,11,0,1,2,3],
    [5,6,7,8,9,10,11,0,1,2,3,4],
    [6,7,8,9,10,11,0,1,2,3,4,5],
    [7,8,9,10,11,0,1,2,3,4,5,6],
    [8,9,10,11,0,1,2,3,4,5,6,7],
    [9,10,11,0,1,2,3,4,5,6,7,8],
    [10,11,0,1,2,3,4,5,6,7,8,9],
    [11,0,1,2,3,4,5,6,7,8,9,10]]
narayana_dhasa_ketu_exception_progression = \
    [[0,11,10,9,8,7,6,5,4,3,2,1],
    [1,6,11,4,9,2,7,0,5,10,3,8],
    [2,6,10,11,3,7,8,0,4,5,9,1],
    [3,4,5,6,7,8,9,10,11,0,1,2],
    [4,11,6,1,8,3,10,5,0,7,2,9],
    [5,1,9,8,4,0,11,7,3,2,10,6],
    [6,5,4,3,2,1,0,11,10,9,8,7],
    [7,0,5,10,3,8,1,6,11,4,9,2],
    [8,0,4,5,9,1,2,6,10,11,3,7],
    [9,10,11,0,1,2,3,4,5,6,7,8],
    [10,5,0,7,2,9,4,11,6,1,8,3],
    [11,7,3,2,10,6,5,1,9,8,4,0]]
tri_rasi_daytime_lords = [0,5,6,5,4,1,3,2,6,2,4,1]
tri_rasi_nighttime_lords = [4,1,3,2,0,5,6,5,6,2,4,1]
# TRUE => Saravali formula from https://saravali.github.io/astrology/bala_sthana.html#uchcha 
# Sarvali formula is also used in BV Raman Book
# False => PVR Book formua
use_saravali_formula_for_uccha_bala = True  
pancha_vargeeya_bala_strength_threshold = 10
order_of_planets_by_speed = [6,7,8,4,2,0,5,3,1] # Saturn is slowest and moon is fastest
deeptaamsa_of_planets=[15,12,8,7,9,7,9] #sun, moon,mars,mercury,jupiter,venus,saturn
combustion_range_of_planets_from_sun = [12,17,14,10,11,15] #moon,mars,mercury,jupiter,venus,saturn
combustion_range_of_planets_from_sun_while_in_retrogade = [12,8,12,11,8,16] # [12,17,12,8,11,15] #moon,mars,mercury,jupiter,venus,saturn
ritu_per_solar_tamil_month = True # False means calculate ritu based on north indian lunaro month index
annual_chart_solar_positions = {1:(1,6,9,12),2:(2,12,18,18),3:(3,18,27,30),4:(5,0,36,36),5:(6,6,45,48),6:(0,12,55,0),7:(1,19,4,6),
                                8:(3,1,13,18),9:(4,7,22,30),10:(5,13,31,36),20:(4,3,3,12),30:(2,16,34,54),40:(1,6,6,30),50:(6,19,38,6),
                                60:(5,9,9,42),70:(3,22,41,24),80:(2,12,13,0),90:(1,1,44,36),100:(6,15,16,12)}
_arudha_lagnas_included_in_chart = {k:'bhava_arudha_a'+str(k)+'_str' for k in range(1,13)}# [1,12]}
northern_rasis = [0,1,2,9,10,11]
southern_rasis = [3,4,5,6,7,8]
planets_disc_diameters = [-1,-1,9.4,6.6,190.4,16.6,158.0,-1,-1]
planet_mean_daily_motions_at_1900 = [257.4568, -1, 270.22, 164.0, 220.04, 328.51, 236.74]
""" Columns => Units, Hundreds, thousands, ten thousands """
mean_solar_daily_motions_table_from_1900 = [
    [0.9856, 98.5602, 265.6026, 136.0265],
    [1.9712, 197.1205, 171.2053, 272.0531],
    [2.9568, 295.6808, 76.8080,  48.0796],
    [3.9424, 34.2411, 342.4106, 184.1062],
    [4.9280, 132.8013, 248.0133, 320.1327],
    [5.9136, 231.3616, 153.6159, 96.1593],
    [6.8992, 329.9218, 59.2186, 232.1868],
    [7.8848, 68.4821, 324.8212, 8.2124],
    [8.8704, 167.0424, 230.4239, 144.2389]]
""" Columns => Units, Hundreds, thousands, ten thousands """
mean_mars_daily_motions_table_from_1900 = [
    [0.524, 52.40, 164.02, 200.19],
    [1.048, 104.80, 328.04, 40.39],
    [1.572, 157.21, 132.06, 240.58],
    [2.096, 209.61, 296.08, 80.78],
    [2.620, 262.01, 100.10, 280.97],
    [3.144, 314.41, 264.12, 121.16],
    [3.668, 6.81  , 68.14 , 321.36],
    [4.192, 59.22, 232.15,  161.55],
    [4.716, 111.62, 36.17,  1.74]]
""" Columns => Units, Hundreds, thousands, ten thousands """
mean_jupiter_daily_motions_table_from_1900 = [
    [0.08, 0.83, 8.31, 83.1, 110.96],
    [0.17, 1.66, 16.62, 166.19, 221.93],
    [0.25, 2.49, 24.93, 249.29, 332.89],
    [0.33, 3.32, 33.24, 332.39, 83.85],
    [0.41, 4.15, 41.55, 55.48, 194.82],
    [0.50, 4.99, 49.86, 138.58, 305.78],
    [0.58, 5.82, 58.17, 221.67, 56.74],
    [0.66, 6.65, 66.48, 304.77, 167.71],
    [0.75, 7.48, 74.79, 27.87, 278.67]]
""" Columns => Units, Hundreds, thousands, ten thousands """
mean_saturn_daily_motions_table_from_1900 = [
    [.03, 0.33, 3.34, 33.44, 334.39],
    [0.07, 0.67, 6.69, 66.88, 308.79],
    [0.10, 1.00, 10.03, 100.32, 283.18],
    [0.13, 1.34, 13.38, 133.76,257.57],
    [0.17, 1.67, 16.72, 167.20, 231.97],
    [0.20, 2.01, 20.06, 200.64, 206.36],
    [0.23, 2.34, 23.41, 234.08, 180.75],
    [0.27, 2.68, 26.75, 267.51, 155.14],
    [0.30, 3.01, 30.10, 300.95, 129.54]]
""" Columns => Units, Hundreds, thousands, ten thousands """
mean_mercury_daily_motions_table_from_1900 = [
    [4.09, 40.92, 49.23, 132.32, 243.18],
    [8.18, 81.84, 98.46, 264.64, 126.36],
    [12.28, 122.77, 147.70, 36.95, 9.54],
    [16.37, 163.69, 196.93, 169.27, 252.72],
    [20.46, 204.62, 246.16, 301.59, 135.90],
    [24.55, 245.54, 295.39, 73.91, 19.08],
    [28.65, 286.46, 344.62, 206.23, 262.26],
    [32.74, 327.38, 33.85, 338.54, 145.44],
    [36.83, 8.31, 83.09, 110.86, 28.63]]
""" Columns => Units, Hundreds, thousands, ten thousands """
mean_venus_daily_motions_table_from_1900 = [
    [1.60, 16.02, 160.21, 162.15, 181.46],
    [3.20, 32.04, 320.43, 324.29, 2.93],
    [4.81, 48.06, 120.64, 126.44, 184.39],
    [6.41, 64.09, 280.86, 288.59, 5.86],
    [8.01, 80.11, 81.07,  90.73, 187.32],
    [9.61, 96.13, 241.29,  252.88,  8.78],
    [11.21, 112.15, 41.50, 55.02, 190.25],
    [12.82, 128.17, 201.72, 217.17, 11.71],
    [14.42, 144.19, 1.93, 19.32, 193.18]]
naisargika_bala = [60.00,51.43,17.14,25.71,34.29,42.86,8.57,0.0,0.0]
minimum_bhava_bala_rupa = 7.0
planets_retrograde_limits_from_sun = {2:(164,196),3:(144,216),4:(130,230),5:(163,197),6:(115,245)}
planet_retrogression_calculation_method = 1 # 1 => Old method 2 = Wiki calculations
lunar_gregory_month_max = 6
sthree_dheerga_threshold = 13
sthree_dheerga_threshold_south = 7
raasi_threshold_south = 6
gana_threshold_south = 14
rasi_sandhi_duration = 1.0
annual_maximum_age = 90
""" Baadhakas [Baadhaka Sthaana,[baadhaka planets]]..."""
baadhakas = [[10,[6,7]],[9,[6]],[8,[4]],[1,[5]],[0,[2]],[11,[4]],[4,[0]],[3,[1]],[2,[3]],[7,[2,8]],[6,[5]],[5,[3]]]
ganda_moola_stars = [1,9,10,18,19,27] # Ashwini, Ashlesha/Ayilyam, Magha, Jyeshta, Moola, or Revati
conjunction_aspect_threshold = 8.0
square_aspect_threshold = 8.0 ; chathusra_aspect_threshold = square_aspect_threshold
sextile_aspect_threshold = 7.0; trine_aspect_threhold = 8.0; parallel_aspect_threshold = 1.0
compatibility_minimum_score_north = 18.0
compatibility_minimum_score_south = 6.0
compatibility_maximum_score_south = 10.0
compatibility_maximum_score_north = 36.0
mandatory_compatibility_south_list = [1,2,3,5] # Gana(1), Dhinam/Thara/Star(2), Yoni(3), Rasi(5). Rajju is also added.
available_chart_types = ['south indian','north indian','east indian','western','sudarsana chakra']
birth_rectification_step_minutes = 0.25
birth_rectification_loop_count = 120 # Number of steps
_GREEN_CHECK = '\u2705' ; _RED_CROSS = '\u274C'
_GREEN_OR_RED = lambda b:_GREEN_CHECK if b else _RED_CROSS
include_special_and_arudha_lagna_in_charts = True # V3.1.9
mahabharatha_tithi_julian_day = 588465.5
use_aharghana_for_vaara_calcuation = True
minimum_separation_longitude=0.00001
conjunction_increment=0.00001 #1.0/86400 #
include_charts_only_for_western_type = False
include_maandhi_in_charts=True
_PRAVESHA_LIST = ['birth_str','annual_str','tithi_pravesha_str','present_str','planetary_conjunctions_str',
                  'planet_transit_str','vakra_gathi_change_str','prenatal_time_str','vrathas_str','customized_str']
sphuta_list = ["tri","chatur","pancha","prana","deha","mrityu","sookshma_tri","beeja","kshetra","tithi","yoga",
               "rahu_tithi","yogi","avayogi"]
ashtottari_bhukthi_starts_from_dhasa_lord = True #PVR Book says this should be False. But JHora has this True
chara_karaka_names = ['atma_karaka','amatya_karaka','bhratri_karaka','maitri_karaka','pitri_karaka','putra_karaka',
                      'jnaati_karaka','data_karaka']
""" Donot remember from where I got this dictionary of karana to lord mapping. JHora does not have Rahu and Kethu
    for Karana Chathuraseethi sama dasa. So the lords of Rahu/Ketu have been distributed to other lords as per the original sequence.
"""
karana_lords = {0:[(2,9,16,23,30,37,44,51,58),12],1:[(3,10,17,24,31,38,45,52,59),12],2:[(4,11,18,25,32,39,46,53,60),12],
                3:[(5,12,19,26,33,40,47,54,1),12],4:[(6,13,20,27,34,41,48,55),12],5:[(7,14,21,28,35,42,49,56),12],
                6:[(8,15,22,29,36,43,50,57),12]}#,7:[(58,60),12],8:[(1,59),12]}
pindayu_full_longevity_of_planets=[19,25,15,12,15,21,20] #in years for Sun to Saturn - when they are in highest exhaltation
pindayu_base_longevity_of_planets=[0.5*full for full in pindayu_full_longevity_of_planets] #in years for Sun to Saturn - when they are in deepest debilitation
nisargayu_full_longevity_of_planets=[20,1,2,9,18,20,50] #in years for Sun to Saturn - when they are in highest exhaltation
nisargayu_base_longevity_of_planets=[0.5*full for full in nisargayu_full_longevity_of_planets] #in years for Sun to Saturn - when they are in deepest debilitation
aayu_dhasa_types = ['pinda','nisarga','amsa']
kaala_dhasa_types = ['dawn','day','dusk','night']
aayu_types = {0:['alpaayu','0-32'],1:['madhyaayu','33-70'],2:['poornaayu','71-100']}
indian_house_systems = {1:'Equal Housing - Lagna in the middle',2:'Equal Housing - Lagna as start',3:'Sripati method',
                        4:'KP Method (aka Placidus Houses method)',5:'Each Rasi is the house'}
western_house_systems = {'P':'Placidus','K':'Koch','O':'Porphyrius','R':'Regiomontanus','C':'Campanus','A':'Equal (cusp 1 is Ascendant)',
                         'V':'Vehlow equal (Asc. in middle of house 1)','X':'axial rotation system','H':'azimuthal or horizontal system',
                         'T':'Polich/Page (topocentric system)','B':'Alcabitus','M':'Morinus'}
available_house_systems = {**indian_house_systems, **western_house_systems}
""" Bhaava Madhya Methods: = one of the above keys as the value """
bhaava_madhya_method = 1 # 'Equal Housing - Lagna in the middle'
nakshatra_rulers = ['Aswini Kumara','Yama','Agni','Bramha','Moon','Shiva','Aditi','Jupiter','Rahu','Sun','Aryaman','Sun',
                    'Viswakarma','Vaayu','Indra','Mitra','Indra','Nirriti','Varuna','Viswaa deva','Brahma','Vishnu','Vasu',
                    'Varuna','Ajacharana','Ahirbudhanya','Pooshan']
nakshatra_lords = [8,5,0,1,2,7,4,6,3,8,5,0,1,2,7,4,6,3,8,5,0,1,2,7,4,6,3]
amsa_rulers = {
                2:['Devas','Pitris'],
                3:['Naarada','Agastya','Durvaasa'],
                4:['Sanaka','Sananda','Kumaara','Sanaatana'],
                7:['Kshaara','Ksheera','Dadhi','Ghrita','Ikshu Rasa','Madya','Suddha Jala'],
                10:['Indra','Agni','Yama','Nirriti','Varuna','Vayu','Kubera','Ishana','Brahma','Ananta'],
                12:['Ganesha','Aswini Kumara','Yama','Sarpa (Ahi)','Ganesha','Aswini Kumara','Yama','Sarpa (Ahi)',
                    'Ganesha','Aswini Kumara','Yama','Sarpa (Ahi)'],
                16:['Brahma','Vishnu','Shiva','Surya']*4,
                20:['Kali/Daya','Gouri','Chinna Sheersha','Pishachini','Dhoomavati',
                    'Vimalaa','Baalaa','Taaraa','Arunaa','Swethaa','Pingalaa','Bagalamukhi','Ghoraa','Sachi','Roudri',
                    'Sitaa','Varadaa','Jayaa','Tripura/Mangala','Sumkhi/Aparaajita'],
                24:['Skanda','Parashudhara', 'Anala', 'Vishvakarma', 'Bhaga', 'Mitra', 'Maya', 'Antaka', 'Vrishdhawaja',
                    'Govinda','Madana','Bhima']*2,
                27:nakshatra_rulers,
                30:['Agni','Vaayu','Indra','Kubera','Varuna']*6,
                40:['Vishnu','Chandra','Marichi','Twashta','Dhata','Shiva','Ravi','Yama','Yaksha',
                    'Gandharva','Kaala','Varuna']*3+['Vishnu','Chandra','Marichi','Twashta'],
                60:['Ghoraa','Rakshasa','Deva','Kuber','Yaksha','Kinnar','Bhrashta','Kulaghna','Garala','Agni/Vahini','Maya',
                    'Purishaka','Apampati','Marut','Kaala','Sarpa','Amrita','Indu','Mridu','Komala','Heramba','Brahma','Vishnu',
                    'Maheshwara','Deva','Ardra','Kalinasha','Kshitish','Kamalakara','Gulika','Mrityu','Kaal','Daavagni',
                    'Ghora','Yama','Kantaka','Sudha','Amrita','Poornachandra','Vishadagdha','Kulanasha','Vanshakshya',
                    'Utpata','Kaal','Saumya','Komal','Sheetala','Karal danstra','Chandramukhi','Praveena','Kalagni',
                    'Dandayuda','Nirmala','Saumya','Kroora','Atisheetala','Amrita','Payodhi','Bhramana','Chandrarekha']            }
hora_chart_by_pvr_method = True
mrityu_bhaga_tolerances = {'L':2/3, 1:2/3, 3:2/3, 0:1/3, 2:0.25,4:0.25,5:0.25,6:0.25,7:0.25,8:0.25,'maandi_str':0.25}
# For each rasi (row) Order of planets Sun, Moon, Mars, Merc, Jup, Ven,Sat,Rah,Ket,Mandi,Lagna
mrityu_bhaga_base_longitudes = [[20,26,19,15,19,28,10,14,8,23,1],
                                [9,12,28,14,29,15,4,13,18,24,9],
                                [12,13,25,13,12,11,7,12,20,11,22],
                                [6,25,23,12,27,17,9,11,10,12,22],
                                [8,24,29,8,6,10,12,24,21,13,25],
                                [24,11,28,18,4,13,16,23,22,14,2],
                                [16,26,14,20,13,4,3,22,23,8,4],
                                [17,14,21,10,10,6,18,21,24,18,23],
                                [22,13,2,21,17,27,28,10,11,20,18],
                                [2,25,15,22,11,12,14,20,12,10,20],
                                [3,5,11,7,15,29,13,18,13,21,24],
                                [23,12,6,5,28,19,15,8,14,22,10]
                                ]

_asc_house_row_col__chart_map = [(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(3,2),(3,1),(3,0),(2,0),(1,0),(0,0)]
hora_list_raman = [(7,9), (1,11), (5,0), (3,6), (4,2),(2,3),(6,4), (0,5), (11,1), (9,7), (10,8), (8,10)] 
drekkana_jagannatha = [(0,4,8),(9,1,5),(6,10,2),(3,7,11), (0,4,8),(9,1,5),(6,10,2),(3,7,11), (0,4,8),(9,1,5),(6,10,2),(3,7,11)]
# Kalachakra Navamsa - Star => Rasi/padha mapping
# For Aswini (0) Padham 1 is Ar (0, P2=1(Ta) etc
kalachakra_navamsa = {0:[0,1,2,3], 1:[4,5,6,7], 2:[8,9,10,11], 3:[7,6,5,3], 4:[4,2,1,0],5:[11,10,9,8],
            6:[0,1,2,3], 7:[4,5,6,7], 8:[8,9,10,11], 9:[7,6,5,3], 10:[4,2,1,0],11:[11,10,9,8],
           12:[0,1,2,3],13:[4,5,6,7],14:[8,9,10,11],15:[7,6,5,3],16:[4,2,1,0],17:[11,10,9,8],
           18:[0,1,2,3],19:[4,5,6,7],20:[8,9,10,11],21:[7,6,5,3],22:[4,2,1,0],23:[11,10,9,8],
           24:[0,1,2,3],25:[4,5,6,7],26:[8,9,10,11]}
# chart_method options for each varga chart {varga:(number_of_options,defualt_option)}
varga_option_dict = {2:(6,1),3:(5,1),4:(4,1),5:(4,1),6:(4,1),7:(6,1),8:(4,1),9:(5,1),10:(6,1),11:(5,1),12:(5,1),16:(4,1),
                      20:(4,1),24:(3,1),27:(4,1),30:(5,1),40:(4,1),45:(4,1),60:(4,1),81:(3,1),108:(4,1),144:(4,1)
                      }
dhasa_default_options={0:[False,2,1,0,0,0,-1],1:[False,0],2:[True,False,2,1,0,0,0,-1],3:[False,5,1,0,0,0,-1],
                       4:[0,False,2],5:[False,6,1,0,0,0,-1],6:[0,False,0],7:[False,7,1,0,0,0,-1],
                       8:[False,26,1,0,0,0,-1],9:[False,18,1,0,0,0,-1],10:[False,16,1,0,0,0,-1],
                       11:[False,26,1,0,0,0,-1],12:[False,14,1,0,0,0,-1],13:[False,0],14:[False,0,1,0,0,0,-1],
                       15:[False,21,1,0,0,0,-1],16:[True,False,False],17:[0,0,-1],18:[],19:[0,-1],20:[],
                       21:[3],22:[False,1,0,0,0,-1]
                       }
MAX_DHASAVARGA_FACTOR = 300
DEFAULT_CUSTOM_VARGA_FACTOR=57
# If True standard vargas such as D2,D3 etc will follow custom calculations and not standard calculations
""" DO NOT CHANGE THIS TO TRUE. NOT IMPLEMENTED YET """
TREAT_STANDARD_CHART_AS_CUSTOM = False
_bhava_arudha_list = ['bhava_arudha_str','sun_arudha','moon_arudha','mars_arudha','mercury_arudha','jupiter_arudha',
                      'venus_arudha','saturn_arudha','rahu_arudha','ketu_arudha']
"""
# Kota Chakra Star Placement - From Outer square to Inner Square
# For Inner most square - only middle no corner placement
# Order of stars are as below for the placement of kota chakra stars:
# NOTE: Abhijit is added after Uthiraadam (UttaraShada)
#Aswini,Bharani,Karthigai,Rohini,Mrigasheesham,Thiruvaathirai,Punarpoosam,Poosam,Aayilyam,Makam,Pooram,Uthiram,
#Hastham,Chithirai,Swaathi,Visaakam,Anusham,Kaettai,Moolam,Pooraadam,Uthiraadam,ABHIJIT,
#Thiruvonam,Avittam,Sadhayam,#Poorattathi,Uthirattathi,Revathi
# Number 1 in below list indicates Birth star (i.e. 1st position from birth star). 2=> 2nd position from birth star etc.
Star positions are as per birth star even for tajaka charts.
But Planets are placed per tajaka chart at its star longitude/position
"""
abhijit_order_of_stars = [*range(21)]+[27]+[*range(21,27)]
kota_chakra_star_placement_from_birth_star = [[1,7,8,14,15,21,22,28],[2,6,9,13,16,20,23,27],[3,5,10,12,17,19,24,26],
                                              [4,11,18,25]]
kota_paala_lord_for_star_paadha = [
[5,5,5,1],[1,1,1,1],[0,0,0,0],[0,1,1,1],[1,1,2,2],[2,2,2,5],[2,2,7,7],[7,7,7,3],[3,3,3,3],[6,6,6,6],[6,3,3,3],[3,3,6,6],[6,7,3,3],[6,6,1,1],
[1,1,1,4],[4,4,4,4],[4,4,4,4],[4,1,1,1],[1,1,6,6],[6,4,6,3],[6,6,5,5],[3,3,3,3],[3,3,3,3],[3,7,7,7],[7,7,4,4],[4,4,5,5],[4,4,5,5],[4,4,4,4]
]

prasna_kp_249_dict = { 1:[(0,0,0),(0,46,40),1], 
                    2:[(0,46,40),(3,0,0),1],
                    3:[(3,0,0),(3,40,0),1],
                    4:[(3,40,0),(4,46,40),1],
                    5:[(4,46,40),(5,33,20),1],
                    6:[(5,33,20),(7,33,20),1],
                    7:[(7,33,20),(9,20,0),1],
                    8:[(9,20,0),(11,26,40),1],
                    9:[(11,26,40),(13,20,0),1],
                    10:[(13,20,0),(15,33,20),1],
                    11:[(15,33,20),(16,13,20),1],
                    12:[(16,13,20),(17,20,0),1],
                    13:[(17,20,0),(18,6,40),1],
                    14:[(18,6,40),(20,6,40),1],
                    15:[(20,6,40),(21,53,20),1],
                    16:[(21,53,20),(24,0,0),1],
                    17:[(24,0,0),(25,53,20),1],
                    18:[(25,53,20),(26,40,0),1],
                    19:[(26,40,0),(27,20,0),1],
                    20:[(27,20,0),(28,26,40),1],
                    21:[(28,26,40),(29,13,20),1],
                    22:[(29,13,20),(30,0,0),1],
                    23:[(0,0,0),(1,13,20),2],
                    24:[(1,13,20),(3,0,0),2],
                    25:[(3,0,0),(5,6,40),2],
                    26:[(5,6,40),(7,0,0),2],
                    27:[(7,0,0),(7,46,40),2],
                    28:[(7,46,40),(10,0,0),2],
                    29:[(10,0,0),(11,6,40),2],
                    30:[(11,6,40),(11,53,20),2],
                    31:[(11,53,20),(13,53,20),2],
                    32:[(13,53,20),(15,40,0),2],
                    33:[(15,40,0),(17,46,40),2],
                    34:[(17,46,40),(19,40,0),2],
                    35:[(19,40,0),(20,46,40),2],
                    36:[(20,46,40),(22,40,0),2],
                    37:[(22,40,0),(23,20,0),2],
                    38:[(23,20,0),(24,6,40),2],
                    39:[(24,6,40),(26,6,40),2],
                    40:[(26,6,40),(27,53,20),2],
                    41:[(27,53,20),(30,0,0),2],
                    42:[(0,0,0),(1,53,20),3],
                    43:[(1,53,20),(2,40,0),3],
                    44:[(2,40,0),(4,53,20),3],
                    45:[(4,53,20),(5,33,20),3],
                    46:[(5,33,20),(6,40,0),3],
                    47:[(6,40,0),(8,40,0),3],
                    48:[(8,40,0),(10,26,40),3],
                    49:[(10,26,40),(12,33,20),3],
                    50:[(12,33,20),(14,26,40),3],
                    51:[(14,26,40),(15,13,20),3],
                    52:[(15,13,20),(17,26,40),3],
                    53:[(17,26,40),(18,6,40),3],
                    54:[(18,6,40),(19,13,20),3],
                    55:[(19,13,20),(20,0,0),3],
                    56:[(20,0,0),(21,46,40),3],
                    57:[(21,46,40),(23,53,20),3],
                    58:[(23,53,20),(25,46,40),3],
                    59:[(25,46,40),(26,33,20),3],
                    60:[(26,33,20),(28,46,40),3],
                    61:[(28,46,40),(29,26,40),3],
                    62:[(29,26,40),(30,0,0),3],
                    63:[(0,0,0),(0,33,20),4],
                    64:[(0,33,20),(1,20,0),4],
                    65:[(1,20,0),(3,20,0),4],
                    66:[(3,20,0),(5,26,40),4],
                    67:[(5,26,40),(7,20,0),4],
                    68:[(7,20,0),(8,6,40),4],
                    69:[(8,6,40),(10,20,0),4],
                    70:[(10,20,0),(11,0,0),4],
                    71:[(11,0,0),(12,6,40),4],
                    72:[(12,6,40),(12,53,20),4],
                    73:[(12,53,20),(14,53,20),4],
                    74:[(14,53,20),(16,40,0),4],
                    75:[(16,40,0),(18,33,21),4],
                    76:[(18,33,21),(19,20,0),4],
                    77:[(19,20,0),(21,33,20),4],
                    78:[(21,33,20),(22,13,20),4],
                    79:[(22,13,20),(23,20,0),4],
                    80:[(23,20,0),(24,6,40),4],
                    81:[(24,6,40),(26,6,40),4],
                    82:[(26,6,40),(27,53,20),4],
                    83:[(27,53,20),(30,0,0),4],
                    84:[(0,0,0),(0,46,40),5],
                    85:[(0,46,40),(3,0,0),5],
                    86:[(3,0,0),(3,40,0),5],
                    87:[(3,40,0),(4,46,40),5],
                    88:[(4,46,40),(5,33,20),5],
                    89:[(5,33,20),(7,33,20),5],
                    90:[(7,33,20),(9,20,0),5],
                    91:[(9,20,0),(11,26,40),5],
                    92:[(11,26,40),(13,20,0),5],
                    93:[(13,20,0),(15,33,20),5],
                    94:[(15,33,20),(16,13,20),5],
                    95:[(16,13,20),(17,20,0),5],
                    96:[(17,20,0),(18,6,40),5],
                    97:[(18,6,40),(20,6,40),5],
                    98:[(20,6,40),(21,53,20),5],
                    99:[(21,53,20),(24,0,0),5],
                    100:[(24,0,0),(25,53,20),5],
                    101:[(25,53,20),(26,40,0),5],
                    102:[(26,40,0),(27,20,0),5],
                    103:[(27,20,0),(28,26,40),5],
                    104:[(28,26,40),(29,13,20),5],
                    105:[(29,13,20),(30,0,0),5],
                    106:[(0,0,0),(1,13,20),6],
                    107:[(1,13,20),(3,0,0),6],
                    108:[(3,0,0),(5,6,40),6],
                    109:[(5,6,40),(7,0,0),6],
                    110:[(7,0,0),(7,46,40),6],
                    111:[(7,46,40),(10,0,0),6],
                    112:[(10,0,0),(11,6,40),6],
                    113:[(11,6,40),(11,53,20),6],
                    114:[(11,53,20),(13,53,20),6],
                    115:[(13,53,20),(15,40,0),6],
                    116:[(15,40,0),(17,46,40),6],
                    117:[(17,46,40),(19,40,0),6],
                    118:[(19,40,0),(20,46,40),6],
                    119:[(20,46,40),(22,40,0),6],
                    120:[(22,40,0),(23,20,0),6],
                    121:[(23,20,0),(24,6,40),6],
                    122:[(24,6,40),(26,6,40),6],
                    123:[(26,6,40),(27,53,20),6],
                    124:[(27,53,20),(30,0,0),6],
                    125:[(0,0,0),(1,53,20),7],
                    126:[(1,53,20),(2,40,0),7],
                    127:[(2,40,0),(4,53,20),7],
                    128:[(4,53,20),(5,33,20),7],
                    129:[(5,33,20),(6,40,0),7],
                    130:[(6,40,0),(8,40,0),7],
                    131:[(8,40,0),(10,26,40),7],
                    132:[(10,26,40),(12,33,20),7],
                    133:[(12,33,20),(14,26,40),7],
                    134:[(14,26,40),(15,13,20),7],
                    135:[(15,13,20),(17,26,40),7],
                    136:[(17,26,40),(18,6,40),7],
                    137:[(18,6,40),(19,13,20),7],
                    138:[(19,13,20),(20,0,0),7],
                    139:[(20,0,0),(21,46,40),7],
                    140:[(21,46,40),(23,53,20),7],
                    141:[(23,53,20),(25,46,40),7],
                    142:[(25,46,40),(26,33,20),7],
                    143:[(26,33,20),(28,46,40),7],
                    144:[(28,46,40),(29,26,40),7],
                    145:[(29,26,40),(30,0,0),7],
                    146:[(0,0,0),(0,33,20),8],
                    147:[(0,33,20),(1,20,0),8],
                    148:[(1,20,0),(3,20,0),8],
                    149:[(3,20,0),(5,26,40),8],
                    150:[(5,26,40),(7,20,0),8],
                    151:[(7,20,0),(8,6,40),8],
                    152:[(8,6,40),(10,20,0),8],
                    153:[(10,20,0),(11,0,0),8],
                    154:[(11,0,0),(12,6,40),8],
                    155:[(12,6,40),(12,53,20),8],
                    156:[(12,53,20),(14,53,20),8],
                    157:[(14,53,20),(16,40,0),8],
                    158:[(16,40,0),(18,33,21),8],
                    159:[(18,33,21),(19,20,0),8],
                    160:[(19,20,0),(21,33,20),8],
                    161:[(21,33,20),(22,13,20),8],
                    162:[(22,13,20),(23,20,0),8],
                    163:[(23,20,0),(24,6,40),8],
                    164:[(24,6,40),(26,6,40),8],
                    165:[(26,6,40),(27,53,20),8],
                    166:[(27,53,20),(30,0,0),8],
                    167:[(0,0,0),(0,46,40),9],
                    168:[(0,46,40),(3,0,0),9],
                    169:[(3,0,0),(3,40,0),9],
                    170:[(3,40,0),(4,46,40),9],
                    171:[(4,46,40),(5,33,20),9],
                    172:[(5,33,20),(7,33,20),9],
                    173:[(7,33,20),(9,20,0),9],
                    174:[(9,20,0),(11,26,40),9],
                    175:[(11,26,40),(13,20,0),9],
                    176:[(13,20,0),(15,33,20),9],
                    177:[(15,33,20),(16,13,20),9],
                    178:[(16,13,20),(17,20,0),9],
                    179:[(17,20,0),(18,6,40),9],
                    180:[(18,6,40),(20,6,40),9],
                    181:[(20,6,40),(21,53,20),9],
                    182:[(21,53,20),(24,0,0),9],
                    183:[(24,0,0),(25,53,20),9],
                    184:[(25,53,20),(26,40,0),9],
                    185:[(26,40,0),(27,20,0),9],
                    185:[(27,20,0),(28,26,40),9],
                    187:[(28,26,40),(29,13,20),9],
                    188:[(29,13,20),(30,0,0),9],
                    189:[(0,0,0),(1,13,20),2],
                    190:[(1,13,20),(3,0,0),10],
                    191:[(3,0,0),(5,6,40),10],
                    192:[(5,6,40),(7,0,0),10],
                    193:[(7,0,0),(7,46,40),10],
                    194:[(7,46,40),(10,0,0),10],
                    195:[(10,0,0),(11,6,40),10],
                    196:[(11,6,40),(11,53,20),10],
                    197:[(11,53,20),(13,53,20),10],
                    198:[(13,53,20),(15,40,0),10],
                    199:[(15,40,0),(17,46,40),10],
                    200:[(17,46,40),(19,40,0),10],
                    201:[(19,40,0),(20,46,40),10],
                    202:[(20,46,40),(22,40,0),10],
                    203:[(22,40,0),(23,20,0),10],
                    204:[(23,20,0),(24,6,40),10],
                    205:[(24,6,40),(26,6,40),10],
                    206:[(26,6,40),(27,53,20),10],
                    207:[(27,53,20),(30,0,0),10],
                    208:[(0,0,0),(1,53,20),11],
                    209:[(1,53,20),(2,40,0),11],
                    210:[(2,40,0),(4,53,20),11],
                    211:[(4,53,20),(5,33,20),11],
                    212:[(5,33,20),(6,40,0),11],
                    213:[(6,40,0),(8,40,0),11],
                    214:[(8,40,0),(10,26,40),11],
                    215:[(10,26,40),(12,33,20),11],
                    216:[(12,33,20),(14,26,40),11],
                    217:[(14,26,40),(15,13,20),11],
                    218:[(15,13,20),(17,26,40),11],
                    219:[(17,26,40),(18,6,40),11],
                    220:[(18,6,40),(19,13,20),11],
                    221:[(19,13,20),(20,0,0),11],
                    222:[(20,0,0),(21,46,40),11],
                    223:[(21,46,40),(23,53,20),11],
                    224:[(23,53,20),(25,46,40),11],
                    225:[(25,46,40),(26,33,20),11],
                    226:[(26,33,20),(28,46,40),11],
                    227:[(28,46,40),(29,26,40),11],
                    228:[(29,26,40),(30,0,0),11],
                    229:[(0,0,0),(0,33,20),12],
                    230:[(0,33,20),(1,20,0),12],
                    231:[(1,20,0),(3,20,0),12],
                    232:[(3,20,0),(5,26,40),12],
                    233:[(5,26,40),(7,20,0),12],
                    234:[(7,20,0),(8,6,40),12],
                    235:[(8,6,40),(10,20,0),12],
                    236:[(10,20,0),(11,0,0),12],
                    237:[(11,0,0),(12,6,40),12],
                    238:[(12,6,40),(12,53,20),12],
                    239:[(12,53,20),(14,53,20),12],
                    240:[(14,53,20),(16,40,0),12],
                    241:[(16,40,0),(18,33,21),12],
                    242:[(18,33,21),(19,20,0),12],
                    243:[(19,20,0),(21,33,20),12],
                    244:[(21,33,20),(22,13,20),12],
                    245:[(22,13,20),(23,20,0),12],
                    246:[(23,20,0),(24,6,40),12],
                    247:[(24,6,40),(26,6,40),12],
                    248:[(26,6,40),(27,53,20),12],
                    249:[(27,53,20),(30,0,0),12]
}
prasna_kp_249_table = [(0.3888888888888889, 0), (1.8888888888888888, 0), (3.333333333333333, 0), (4.222222222222222, 0), (5.166666666666666, 0), (6.555555555555555, 0), (8.444444444444445, 0), (10.38888888888889, 0), (12.38888888888889, 0), (14.444444444444446, 0), (15.88888888888889, 0), (16.77777777777778, 0), (17.72222222222222, 0), (19.111111111111114, 0), (21.0, 0), (22.944444444444443, 0), (24.944444444444443, 0), (26.27777777777778, 0), (27.0, 0), (27.88888888888889, 0), (28.833333333333336, 0), (29.61111111111111, 0), (0.6111111111111112, 1), (2.111111111111111, 1), (4.055555555555555, 1), (6.055555555555555, 1), (7.388888888888889, 1), (8.88888888888889, 1), (10.555555555555555, 1), (11.5, 1), (12.88888888888889, 1), (14.777777777777779, 1), (16.72222222222222, 1), (18.72222222222222, 1), (20.22222222222222, 1), (21.72222222222222, 1), (23.0, 1), (23.72222222222222, 1), (25.111111111111114, 1), (27.0, 1), (28.944444444444443, 1), (0.9444444444444444, 2), (2.2777777777777777, 2), (3.7777777777777777, 2), (5.222222222222221, 2), (6.111111111111111, 2), (7.666666666666666, 2), (9.555555555555555, 2), (11.5, 2), (13.5, 2), (14.833333333333334, 2), (16.333333333333336, 2), (17.77777777777778, 2), (18.666666666666668, 2), (19.61111111111111, 2), (20.88888888888889, 2), (22.833333333333336, 2), (24.833333333333336, 2), (26.166666666666668, 2), (27.666666666666668, 2), (29.111111111111114, 2), (29.72222222222222, 2), (0.2777777777777778, 3), (0.9444444444444444, 3), (2.3333333333333335, 3), (4.388888888888889, 3), (6.388888888888889, 3), (7.722222222222221, 3), (9.222222222222221, 3), (10.666666666666668, 3), (11.555555555555555, 3), (12.5, 3), (13.88888888888889, 3), (15.777777777777779, 3), (17.61125, 3), (18.944583333333334, 3), (20.444444444444443, 3), (21.88888888888889, 3), (22.77777777777778, 3), (23.72222222222222, 3), (25.111111111111114, 3), (27.0, 3), (28.944444444444443, 3), (0.3888888888888889, 4), (1.8888888888888888, 4), (3.333333333333333, 4), (4.222222222222222, 4), (5.166666666666666, 4), (6.555555555555555, 4), (8.444444444444445, 4), (10.38888888888889, 4), (12.38888888888889, 4), (14.444444444444446, 4), (15.88888888888889, 4), (16.77777777777778, 4), (17.72222222222222, 4), (19.111111111111114, 4), (21.0, 4), (22.944444444444443, 4), (24.944444444444443, 4), (26.27777777777778, 4), (27.0, 4), (27.88888888888889, 4), (28.833333333333336, 4), (29.61111111111111, 4), (0.6111111111111112, 5), (2.111111111111111, 5), (4.055555555555555, 5), (6.055555555555555, 5), (7.388888888888889, 5), (8.88888888888889, 5), (10.555555555555555, 5), (11.5, 5), (12.88888888888889, 5), (14.777777777777779, 5), (16.72222222222222, 5), (18.72222222222222, 5), (20.22222222222222, 5), (21.72222222222222, 5), (23.0, 5), (23.72222222222222, 5), (25.111111111111114, 5), (27.0, 5), (28.944444444444443, 5), (0.9444444444444444, 6), (2.2777777777777777, 6), (3.7777777777777777, 6), (5.222222222222221, 6), (6.111111111111111, 6), (7.666666666666666, 6), (9.555555555555555, 6), (11.5, 6), (13.5, 6), (14.833333333333334, 6), (16.333333333333336, 6), (17.77777777777778, 6), (18.666666666666668, 6), (19.61111111111111, 6), (20.88888888888889, 6), (22.833333333333336, 6), (24.833333333333336, 6), (26.166666666666668, 6), (27.666666666666668, 6), (29.111111111111114, 6), (29.72222222222222, 6), (0.2777777777777778, 7), (0.9444444444444444, 7), (2.3333333333333335, 7), (4.388888888888889, 7), (6.388888888888889, 7), (7.722222222222221, 7), (9.222222222222221, 7), (10.666666666666668, 7), (11.555555555555555, 7), (12.5, 7), (13.88888888888889, 7), (15.777777777777779, 7), (17.61125, 7), (18.944583333333334, 7), (20.444444444444443, 7), (21.88888888888889, 7), (22.77777777777778, 7), (23.72222222222222, 7), (25.111111111111114, 7), (27.0, 7), (28.944444444444443, 7), (0.3888888888888889, 8), (1.8888888888888888, 8), (3.333333333333333, 8), (4.222222222222222, 8), (5.166666666666666, 8), (6.555555555555555, 8), (8.444444444444445, 8), (10.38888888888889, 8), (12.38888888888889, 8), (14.444444444444446, 8), (15.88888888888889, 8), (16.77777777777778, 8), (17.72222222222222, 8), (19.111111111111114, 8), (21.0, 8), (22.944444444444443, 8), (24.944444444444443, 8), (26.27777777777778, 8), (27.88888888888889, 8), (28.833333333333336, 8), (29.61111111111111, 8), (0.6111111111111112, 1), (2.111111111111111, 9), (4.055555555555555, 9), (6.055555555555555, 9), (7.388888888888889, 9), (8.88888888888889, 9), (10.555555555555555, 9), (11.5, 9), (12.88888888888889, 9), (14.777777777777779, 9), (16.72222222222222, 9), (18.72222222222222, 9), (20.22222222222222, 9), (21.72222222222222, 9), (23.0, 9), (23.72222222222222, 9), (25.111111111111114, 9), (27.0, 9), (28.944444444444443, 9), (0.9444444444444444, 10), (2.2777777777777777, 10), (3.7777777777777777, 10), (5.222222222222221, 10), (6.111111111111111, 10), (7.666666666666666, 10), (9.555555555555555, 10), (11.5, 10), (13.5, 10), (14.833333333333334, 10), (16.333333333333336, 10), (17.77777777777778, 10), (18.666666666666668, 10), (19.61111111111111, 10), (20.88888888888889, 10), (22.833333333333336, 10), (24.833333333333336, 10), (26.166666666666668, 10), (27.666666666666668, 10), (29.111111111111114, 10), (29.72222222222222, 10), (0.2777777777777778, 11), (0.9444444444444444, 11), (2.3333333333333335, 11), (4.388888888888889, 11), (6.388888888888889, 11), (7.722222222222221, 11), (9.222222222222221, 11), (10.666666666666668, 11), (11.555555555555555, 11), (12.5, 11), (13.88888888888889, 11), (15.777777777777779, 11), (17.61125, 11), (18.944583333333334, 11), (20.444444444444443, 11), (21.88888888888889, 11), (22.77777777777778, 11), (23.72222222222222, 11), (25.111111111111114, 11), (27.0, 11), (28.944444444444443, 11)]
 
if __name__ == "__main__":
    from jhora import utils
    kp_no = 51; dcf = 1
    #print(prasna_kp_249_table[kp_no])
    print('P-108',utils.get_prasna_lagna_108_for_rasi_chart(kp_no),utils.get_prasna_lagna_108_for_varga_chart(kp_no,dcf))
    print('P-249',utils.get_prasna_lagna_KP_249_for_rasi_chart(kp_no),utils.get_prasna_lagna_KP_249_for_varga_chart(kp_no,dcf))
    print('Nadi',utils.get_prasna_lagna_nadi_for_rasi_chart(kp_no),utils.get_prasna_lagna_nadi_for_varga_chart(kp_no,dcf))
    exit()
