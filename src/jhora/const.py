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
""" Module describing PyJHora constants"""
import os
import swisseph as swe
import numpy as np
from jhora._package_info import version as _APP_VERSION

" setup paths "
_sep = os.path.sep
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.dirname(ROOT_DIR+_sep+"data"+_sep)
_IMAGES_PATH = os.path.dirname(ROOT_DIR+_sep+"images"+_sep)
_IMAGE_ICON_PATH=os.path.join(_IMAGES_PATH+_sep+"lord_ganesha2.jpg")
_INPUT_DATA_FILE = _DATA_DIR +'program_inputs.txt' #os.path.join(ROOT_DIR,'data'+_sep+'program_inputs.txt')
_FESTIVAL_FILE = _DATA_DIR +_sep+'hindu_festivals_multilingual_unicode_bom.csv'
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

available_languages = {"English":'en','Tamil':'ta','Telugu':'te','Hindi':"hi",'Kannada':'ka','Malayalam':'ml'}
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
nakshatra_lords = [8,5,0,1,2,7,4,6,3,8,5,0,1,2,7,4,6,3,8,5,0,1,2,7,4,6,3]
" house module constants " #V2.3.0
# in the order of Janma, Sampath,Vipath, Kshema, Prathyak, Saadhana, Naidhana, Mithra, Parama/Adhi Mithra
nakshathra_lords = {8:(0,9,18), 5:(1,10,19), 0:(2,11,20), 1:(3,12,21), 2:(4,13,22), 7:(5,14,23), 
                    4:(6,15,24), 6:(7,16,25), 3:(8,17,26)}
# Ref: https://www.indiadivine.org/content/topic/1423092-special-tara-table/
special_thaara_lords = {8:(0,9,18,26), 5:(1,10,19), 0:(2,11,27), 1:(3,12,20), 2:(4,13,21), 7:(5,14,22), 
                    4:(6,15,23), 6:(7,16,24), 3:(8,17,25)}
special_thaara_lords_1 = {8:(0,9,18), 5:(1,10,19), 0:(2,11,20), 1:(3,12,21,22), 2:(4,13,23,), 7:(5,14,24),
                          4:(6,15,25,), 6:(7,16,26), 3:(8,17,27)}
# In the order of Janma, Karma, Samudayika, Sanghatika, Jaathi, Naidhana, Desha,Abhisheka, Aadhaana, Vainasika, Maanasa
special_thaara_map = [1,10,18,16,4,7,12,27,19,22,25]#[1,10,18,16,4,7,12,28,19,22,25]
_ABHIJITH_STAR_INDEX = 21 # In the range of 1..28
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
""" SPECIAL CASE OF TITHI SKIPPING BEFORE MAHABHARATHA TIME 
    See Dr. Jayasree Saranatha Mahabharatha date validation book
"""
increase_tithi_by_one_before_kali_yuga = True
mahabharatha_tithi_julian_day = 588465.5

use_aharghana_for_vaara_calcuation = False # V4.4.5
minimum_separation_longitude=0.00001
conjunction_increment=0.00001 #1.0/86400 #
include_charts_only_for_western_type = False
include_maandhi_in_charts=True
_PRAVESHA_LIST = ['birth_str','annual_str','tithi_pravesha_str','lunar_month_year_str','present_str','planetary_conjunctions_str',
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
                6:[(8,15,22,29,36,43,50,57),12],7:[(58,60),12],8:[(1,59),12]}
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
                    'Dandayuda','Nirmala','Saumya','Kroora','Atisheetala','Amrita','Payodhi','Bhramana','Chandrarekha'],
                150:["Vasudhaa","Vaishnavi","Braahmi","Kaalakoota","Shaankari","Sudhaakari","Samaa","Saumyaa","Suraa","Maayaa",
        "Manoharaa","Maadhavi","Manjuswanaa","Ghoraa","Kumbhini","Kutilaa","Prabhaa","Paraa","Payasvini","Maalaa","Jagati",
        "Jarjharaa","Dhruvaa","Musalaa","Mudgaraa","Paashaa","Champakaa","Daamakaa(Daamini)","Mahi","Kulashaa","Kamalaa",
        "Kaantaa","Kaalaa","Karikaraa","Kahamaa","Durdharaa","Durbhagaa","Vishwaa","Visheernaa","Vikataa","Avilaa",
        "Vibhramaa","Sukhadaa","Snigdhaa","Sodaraa","Surasundari","Amritaplaavini","Kaalaa","Kaamadhuk","Karaveerani",
        "Gahvaraa","Kundini","Raudraa","Vishaakhyaa","Vishanaashini","Narmadaa","Sheetalaa","Nimnaa","Preetaa",
        "Priyavardhini","Maanaghnaa","Durbhagaa","Chiraa","Chitrini","Chiranjeevini","Bhoopaa","Gakaharaa","Naalaa","Nalini",
        "Nirmalaa","Nadi","Sudhaamritaamshu","Kaalikaa","Kalushankuraa","Trailokyamohankari","Mahaamaari","Susheetalaa",
        "Sukhadaa","Suprabhaa","Shobhaa","Shobhanaa","Shivadaa","Shivaa","Balaa","Jwaalaa","Gadaa","Gaadhaa","Nootanaa",
        "Sumanoharaa","Somavalli","Somalataa","Mangalaa","Mudrikaa","Kshudhaa","Mokshaapavargaa","Balayaa","Navaneeta",
        "Nishaachari","Nirritti","Nigadaa","Saraa","Sangeetaa","Saamadaa","Samaa","Viwhwambharaa","Kumaari","Kokilaa",
        "Kunjaraakriti","Aindraa","Swaahaa","Swaraa","Vahni","Preetaa","Rakshajalaaplavaa","Vaaruni","Madiraa","Maitri",
        "Haarini","Harini","Marut","Dhananjayaa","Dhanakari","Dhanadaa","Kamchhapaambuja","Maamshaani","Shooeini","Raudri",
        "Shivaa","Shivakari","Kalaa","Kundaa","Mukundaa","Bharataa","Haritaa","Kadalee","Smaraa","Kandalaa","Kokilaa",
        "Paapaa","Kaamini","Kalashodbhavaa","Veeraprasoo","Sangaraa","Shatayajnaa","Shataavari","Prahvi","Paatalini",
        "Naagaa","Pankajaa","Parameshwari"]
                }
hora_chart_by_pvr_method = True
mrityu_bhaga_tolerances = {0:1/3, 1:2/3, 2:0.25, 3:2/3, 4:0.25,5:0.25,6:0.25,7:0.25,8:0.25,'Md':0.25,'L':2/3}
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

# {kp_no: [rasi, nakshatra,(start_degress),(end_degrees),sign_lord,star lord, star sub lord]}
prasna_kp_249_dict = {
                        1:[0,0,0,0.777777777777778,2,8,8],
                        2:[0,0,0.777777777777778,3,2,8,5],
                        3:[0,0,3,3.66666666666667,2,8,0],
                        4:[0,0,3.66666666666667,4.77777777777778,2,8,1],
                        5:[0,0,4.77777777777778,5.55555555555556,2,8,2],
                        6:[0,0,5.55555555555556,7.55555555555556,2,8,7],
                        7:[0,0,7.55555555555556,9.33333333333333,2,8,4],
                        8:[0,0,9.33333333333333,11.4444444444444,2,8,6],
                        9:[0,0,11.4444444444444,13.3333333333333,2,8,3],
                        10:[0,1,13.3333333333333,15.5555555555556,2,5,5],
                        11:[0,1,15.5555555555556,16.2222222222222,2,5,0],
                        12:[0,1,16.2222222222222,17.3333333333333,2,5,1],
                        13:[0,1,17.3333333333333,18.1111111111111,2,5,2],
                        14:[0,1,18.1111111111111,20.1111111111111,2,5,7],
                        15:[0,1,20.1111111111111,21.8888888888889,2,5,4],
                        16:[0,1,21.8888888888889,24,2,5,6],
                        17:[0,1,24,25.8888888888889,2,5,3],
                        18:[0,1,25.8888888888889,26.6666666666667,2,5,8],
                        19:[0,2,26.6666666666667,27.3333333333333,2,0,0],
                        20:[0,2,27.3333333333333,28.4444444444444,2,0,1],
                        21:[0,2,28.4444444444444,29.2222222222222,2,0,2],
                        22:[0,2,29.2222222222222,30,2,0,7],
                        23:[1,2,0,1.22222222222222,5,0,7],
                        24:[1,2,1.22222222222222,3,5,0,4],
                        25:[1,2,3,5.11111111111111,5,0,6],
                        26:[1,2,5.11111111111111,7,5,0,3],
                        27:[1,2,7,7.77777777777778,5,0,8],
                        28:[1,2,7.77777777777778,10,5,0,5],
                        29:[1,3,10,11.1111111111111,5,1,1],
                        30:[1,3,11.1111111111111,11.8888888888889,5,1,2],
                        31:[1,3,11.8888888888889,13.8888888888889,5,1,7],
                        32:[1,3,13.8888888888889,15.6666666666667,5,1,4],
                        33:[1,3,15.6666666666667,17.7777777777778,5,1,6],
                        34:[1,3,17.7777777777778,19.6666666666667,5,1,3],
                        35:[1,3,19.6666666666667,20.4444444444444,5,1,8],
                        36:[1,3,20.4444444444444,22.6666666666667,5,1,5],
                        37:[1,3,22.6666666666667,23.3333333333333,5,1,0],
                        38:[1,4,23.3333333333333,24.1111111111111,5,2,2],
                        39:[1,4,24.1111111111111,26.1111111111111,5,2,7],
                        40:[1,4,26.1111111111111,27.8888888888889,5,2,4],
                        41:[1,4,27.8888888888889,30,5,2,6],
                        42:[2,4,0,1.88888888888889,3,2,3],
                        43:[2,4,1.88888888888889,2.66666666666667,3,2,8],
                        44:[2,4,2.66666666666667,4.88888888888889,3,2,5],
                        45:[2,4,4.88888888888889,5.55555555555556,3,2,0],
                        46:[2,4,5.55555555555556,6.66666666666667,3,2,1],
                        47:[2,5,6.66666666666667,8.66666666666667,3,7,7],
                        48:[2,5,8.66666666666667,10.4444444444444,3,7,4],
                        49:[2,5,10.4444444444444,12.5555555555556,3,7,6],
                        50:[2,5,12.5555555555556,14.4444444444444,3,7,3],
                        51:[2,5,14.4444444444444,15.2222222222222,3,7,8],
                        52:[2,5,15.2222222222222,17.4444444444444,3,7,5],
                        53:[2,5,17.4444444444444,18.1111111111111,3,7,0],
                        54:[2,5,18.1111111111111,19.2222222222222,3,7,1],
                        55:[2,5,19.2222222222222,20,3,7,2],
                        56:[2,6,20,21.7777777777778,3,4,4],
                        57:[2,6,21.7777777777778,23.8888888888889,3,4,6],
                        58:[2,6,23.8888888888889,25.7777777777778,3,4,3],
                        59:[2,6,25.7777777777778,26.5555555555556,3,4,8],
                        60:[2,6,26.5555555555556,28.7777777777778,3,4,5],
                        61:[2,6,28.7777777777778,29.4444444444444,3,4,0],
                        62:[2,6,29.4444444444444,30,3,4,1],
                        63:[3,6,0,0.555555555555556,1,4,1],
                        64:[3,6,0.555555555555556,1.33333333333333,1,4,2],
                        65:[3,6,1.33333333333333,3.33333333333333,1,4,7],
                        66:[3,7,3.33333333333333,5.44444444444444,1,6,6],
                        67:[3,7,5.44444444444444,7.33333333333333,1,6,3],
                        68:[3,7,7.33333333333333,8.11111111111111,1,6,8],
                        69:[3,7,8.11111111111111,10.3333333333333,1,6,5],
                        70:[3,7,10.3333333333333,11,1,6,0],
                        71:[3,7,11,12.1111111111111,1,6,1],
                        72:[3,7,12.1111111111111,12.8888888888889,1,6,2],
                        73:[3,7,12.8888888888889,14.8888888888889,1,6,7],
                        74:[3,7,14.8888888888889,16.6666666666667,1,6,4],
                        75:[3,8,16.6666666666667,18.5558333333333,1,3,3],
                        76:[3,8,18.5558333333333,19.3333333333333,1,3,8],
                        77:[3,8,19.3333333333333,21.5555555555556,1,3,5],
                        78:[3,8,21.5555555555556,22.2222222222222,1,3,0],
                        79:[3,8,22.2222222222222,23.3333333333333,1,3,1],
                        80:[3,8,23.3333333333333,24.1111111111111,1,3,2],
                        81:[3,8,24.1111111111111,26.1111111111111,1,3,7],
                        82:[3,8,26.1111111111111,27.8888888888889,1,3,4],
                        83:[3,8,27.8888888888889,30,1,3,6],
                        84:[4,9,0,0.777777777777778,0,8,8],
                        85:[4,9,0.777777777777778,3,0,8,5],
                        86:[4,9,3,3.66666666666667,0,8,0],
                        87:[4,9,3.66666666666667,4.77777777777778,0,8,1],
                        88:[4,9,4.77777777777778,5.55555555555556,0,8,2],
                        89:[4,9,5.55555555555556,7.55555555555556,0,8,7],
                        90:[4,9,7.55555555555556,9.33333333333333,0,8,4],
                        91:[4,9,9.33333333333333,11.4444444444444,0,8,6],
                        92:[4,9,11.4444444444444,13.3333333333333,0,8,3],
                        93:[4,10,13.3333333333333,15.5555555555556,0,5,5],
                        94:[4,10,15.5555555555556,16.2222222222222,0,5,0],
                        95:[4,10,16.2222222222222,17.3333333333333,0,5,1],
                        96:[4,10,17.3333333333333,18.1111111111111,0,5,2],
                        97:[4,10,18.1111111111111,20.1111111111111,0,5,7],
                        98:[4,10,20.1111111111111,21.8888888888889,0,5,4],
                        99:[4,10,21.8888888888889,24,0,5,6],
                        100:[4,10,24,25.8888888888889,0,5,3],
                        101:[4,10,25.8888888888889,26.6666666666667,0,5,8],
                        102:[4,11,26.6666666666667,27.3333333333333,0,0,0],
                        103:[4,11,27.3333333333333,28.4444444444444,0,0,1],
                        104:[4,11,28.4444444444444,29.2222222222222,0,0,2],
                        105:[4,11,29.2222222222222,30,0,0,7],
                        106:[5,11,0,1.22222222222222,3,0,7],
                        107:[5,11,1.22222222222222,3,3,0,4],
                        108:[5,11,3,5.11111111111111,3,0,6],
                        109:[5,11,5.11111111111111,7,3,0,3],
                        110:[5,11,7,7.77777777777778,3,0,8],
                        111:[5,11,7.77777777777778,10,3,0,5],
                        112:[5,12,10,11.1111111111111,3,1,1],
                        113:[5,12,11.1111111111111,11.8888888888889,3,1,2],
                        114:[5,12,11.8888888888889,13.8888888888889,3,1,7],
                        115:[5,12,13.8888888888889,15.6666666666667,3,1,4],
                        116:[5,12,15.6666666666667,17.7777777777778,3,1,6],
                        117:[5,12,17.7777777777778,19.6666666666667,3,1,3],
                        118:[5,12,19.6666666666667,20.4444444444444,3,1,8],
                        119:[5,12,20.4444444444444,22.6666666666667,3,1,5],
                        120:[5,12,22.6666666666667,23.3333333333333,3,1,0],
                        121:[5,13,23.3333333333333,24.1111111111111,3,2,2],
                        122:[5,13,24.1111111111111,26.1111111111111,3,2,7],
                        123:[5,13,26.1111111111111,27.8888888888889,3,2,4],
                        124:[5,13,27.8888888888889,30,3,2,6],
                        125:[6,13,0,1.88888888888889,5,2,3],
                        126:[6,13,1.88888888888889,2.66666666666667,5,2,8],
                        127:[6,13,2.66666666666667,4.88888888888889,5,2,5],
                        128:[6,13,4.88888888888889,5.55555555555556,5,2,0],
                        129:[6,13,5.55555555555556,6.66666666666667,5,2,1],
                        130:[6,14,6.66666666666667,8.66666666666667,5,7,7],
                        131:[6,14,8.66666666666667,10.4444444444444,5,7,4],
                        132:[6,14,10.4444444444444,12.5555555555556,5,7,6],
                        133:[6,14,12.5555555555556,14.4444444444444,5,7,3],
                        134:[6,14,14.4444444444444,15.2222222222222,5,7,8],
                        135:[6,14,15.2222222222222,17.4444444444444,5,7,5],
                        136:[6,14,17.4444444444444,18.1111111111111,5,7,0],
                        137:[6,14,18.1111111111111,19.2222222222222,5,7,1],
                        138:[6,14,19.2222222222222,20,5,7,2],
                        139:[6,15,20,21.7777777777778,5,4,4],
                        140:[6,15,21.7777777777778,23.8888888888889,5,4,6],
                        141:[6,15,23.8888888888889,25.7777777777778,5,4,3],
                        142:[6,15,25.7777777777778,26.5555555555556,5,4,8],
                        143:[6,15,26.5555555555556,28.7777777777778,5,4,5],
                        144:[6,15,28.7777777777778,29.4444444444444,5,4,0],
                        145:[6,15,29.4444444444444,30,5,4,1],
                        146:[7,15,0,0.555555555555556,2,4,1],
                        147:[7,15,0.555555555555556,1.33333333333333,2,4,2],
                        148:[7,15,1.33333333333333,3.33333333333333,2,4,7],
                        149:[7,16,3.33333333333333,5.44444444444444,2,6,6],
                        150:[7,16,5.44444444444444,7.33333333333333,2,6,3],
                        151:[7,16,7.33333333333333,8.11111111111111,2,6,8],
                        152:[7,16,8.11111111111111,10.3333333333333,2,6,5],
                        153:[7,16,10.3333333333333,11,2,6,0],
                        154:[7,16,11,12.1111111111111,2,6,1],
                        155:[7,16,12.1111111111111,12.8888888888889,2,6,2],
                        156:[7,16,12.8888888888889,14.8888888888889,2,6,7],
                        157:[7,16,14.8888888888889,16.6666666666667,2,6,4],
                        158:[7,17,16.6666666666667,18.5555555555556,2,3,3],
                        159:[7,17,18.5555555555556,19.3333333333333,2,3,8],
                        160:[7,17,19.3333333333333,21.5555555555556,2,3,5],
                        161:[7,17,21.5555555555556,22.2222222222222,2,3,0],
                        162:[7,17,22.2222222222222,23.3333333333333,2,3,1],
                        163:[7,17,23.3333333333333,24.1111111111111,2,3,2],
                        164:[7,17,24.1111111111111,26.1111111111111,2,3,7],
                        165:[7,17,26.1111111111111,27.8888888888889,2,3,4],
                        166:[7,17,27.8888888888889,30,2,3,6],
                        167:[8,18,0,0.777777777777778,4,8,8],
                        168:[8,18,0.777777777777778,3,4,8,5],
                        169:[8,18,3,3.66666666666667,4,8,0],
                        170:[8,18,3.66666666666667,4.77777777777778,4,8,1],
                        171:[8,18,4.77777777777778,5.88888888888889,4,8,2],
                        172:[8,18,5.88888888888889,7.55555555555556,4,8,7],
                        173:[8,18,7.55555555555556,9.33333333333333,4,8,4],
                        174:[8,18,9.33333333333333,11.4444444444444,4,8,6],
                        175:[8,18,11.4444444444444,13.3333333333333,4,8,3],
                        176:[8,19,13.3333333333333,15.5555555555556,4,5,5],
                        177:[8,19,15.5555555555556,16.2222222222222,4,5,0],
                        178:[8,19,16.2222222222222,17.3333333333333,4,5,1],
                        179:[8,19,17.3333333333333,18.1111111111111,4,5,2],
                        180:[8,19,18.1111111111111,20.1111111111111,4,5,7],
                        181:[8,19,20.1111111111111,21.8888888888889,4,5,4],
                        182:[8,19,21.8888888888889,24,4,5,6],
                        183:[8,19,24,25.8888888888889,4,5,3],
                        184:[8,19,25.8888888888889,26.6666666666667,4,5,8],
                        185:[8,20,26.6666666666667,27.3333333333333,4,0,0],
                        186:[8,20,27.3333333333333,28.4444444444444,4,0,1],
                        187:[8,20,28.4444444444444,29.2222222222222,4,0,2],
                        188:[8,20,29.2222222222222,30,4,0,7],
                        189:[9,20,0,1.22222222222222,6,0,7],
                        190:[9,20,1.22222222222222,3,6,0,4],
                        191:[9,20,3,5.11111111111111,6,0,6],
                        192:[9,20,5.11111111111111,7,6,0,3],
                        193:[9,20,7,7.77777777777778,6,0,8],
                        194:[9,20,7.77777777777778,10,6,0,5],
                        195:[9,21,10,11.1111111111111,6,1,1],
                        196:[9,21,11.1111111111111,11.8888888888889,6,1,2],
                        197:[9,21,11.8888888888889,13.8888888888889,6,1,7],
                        198:[9,21,13.8888888888889,15.6666666666667,6,1,4],
                        199:[9,21,15.6666666666667,17.7777777777778,6,1,6],
                        200:[9,21,17.7777777777778,19.6666666666667,6,1,3],
                        201:[9,21,19.6666666666667,20.7777777777778,6,1,8],
                        202:[9,21,20.7777777777778,22.6666666666667,6,1,5],
                        203:[9,21,22.6666666666667,23.3333333333333,6,1,0],
                        204:[9,22,23.3333333333333,24.1111111111111,6,2,2],
                        205:[9,22,24.1111111111111,26.1111111111111,6,2,7],
                        206:[9,22,26.1111111111111,27.8888888888889,6,2,4],
                        207:[9,22,27.8888888888889,30,6,2,6],
                        208:[10,22,0,1.88888888888889,6,2,3],
                        209:[10,22,1.88888888888889,2.66666666666667,6,2,8],
                        210:[10,22,2.66666666666667,4.88888888888889,6,2,5],
                        211:[10,22,4.88888888888889,5.55555555555556,6,2,0],
                        212:[10,22,5.55555555555556,6.67222222222222,6,2,1],
                        213:[10,23,6.67222222222222,8.66666666666667,6,7,7],
                        214:[10,23,8.66666666666667,10.4444444444444,6,7,4],
                        215:[10,23,10.4444444444444,12.5555555555556,6,7,6],
                        216:[10,23,12.5555555555556,14.4444444444444,6,7,3],
                        217:[10,23,14.4444444444444,15.2222222222222,6,7,8],
                        218:[10,23,15.2222222222222,17.4444444444444,6,7,5],
                        219:[10,23,17.4444444444444,18.1111111111111,6,7,0],
                        220:[10,23,18.1111111111111,19.2222222222222,6,7,1],
                        221:[10,23,19.2222222222222,20,6,7,2],
                        222:[10,24,20,21.7777777777778,6,4,4],
                        223:[10,24,21.7777777777778,23.8888888888889,6,4,6],
                        224:[10,24,23.8888888888889,25.7777777777778,6,4,3],
                        225:[10,24,25.7777777777778,26.5555555555556,6,4,8],
                        226:[10,24,26.5555555555556,28.7777777777778,6,4,5],
                        227:[10,24,28.7777777777778,29.4444444444444,6,4,0],
                        228:[10,24,29.4444444444444,30,6,4,1],
                        229:[11,24,0,0.555555555555556,4,4,1],
                        230:[11,24,0.555555555555556,1.33333333333333,4,4,2],
                        231:[11,24,1.33333333333333,3.33333333333333,4,4,7],
                        232:[11,25,3.33333333333333,5.44444444444444,4,6,6],
                        233:[11,25,5.44444444444444,7.33333333333333,4,6,3],
                        234:[11,25,7.33333333333333,8.11111111111111,4,6,8],
                        235:[11,25,8.11111111111111,10.3333333333333,4,6,5],
                        236:[11,25,10.3333333333333,11,4,6,0],
                        237:[11,25,11,12.1111111111111,4,6,1],
                        238:[11,25,12.1111111111111,12.8888888888889,4,6,2],
                        239:[11,25,12.8888888888889,14.8888888888889,4,6,7],
                        240:[11,25,14.8888888888889,16.6666666666667,4,6,4],
                        241:[11,26,16.6666666666667,18.5555555555556,4,3,3],
                        242:[11,26,18.5555555555556,19.3333333333333,4,3,8],
                        243:[11,26,19.3333333333333,21.5555555555556,4,3,5],
                        244:[11,26,21.5555555555556,22.2222222222222,4,3,0],
                        245:[11,26,22.2222222222222,23.3333333333333,4,3,1],
                        246:[11,26,23.3333333333333,24.1111111111111,4,3,2],
                        247:[11,26,24.1111111111111,26.1111111111111,4,3,7],
                        248:[11,26,26.1111111111111,27.8888888888889,4,3,4],
                        249:[11,26,27.8888888888889,30,4,3,6],
}
_saham_list = ['punya','vidya','yasas','mitra','mahatmaya','asha','samartha','bhratri','gaurava','pithri','rajya','maathri',
               'puthra','jeeva','karma','roga','kali','sastra','bandhu','mrithyu','paradesa','artha','paradara','vanika',
               'karyasiddhi','vivaha','santapa','sraddha','preethi','jadya','vyaapaara','sathru','jalapatna','bandhana',
               'apamrithyu','laabha']
"""
# Tuples in the order Pachaka, Bhodhaka, Kaarka and Vedhaka.
# First element planet is Pachaka etc if it is in the 2nd element house from the planet
# For Example 0:[(6,6),(2,7),(4,9),(5,11)]
    Saturn is Sun's Pachaka if it is 6th house from Sun - 'E' stands for inimical relation
    Mars is Sun's Bodhaka if it is in 7th house from Sun
    Jupiter is Sun's Karaka if it is in 9th house from Sun
    Venus is Sun's Vedhaka if it is in 11th house from Sun
"""
paachakaadi_sambhandha = {0:[(6,6,'E'),(2,7,''),(4,9,''),(5,11,'')],1:[(5,7,''),(2,9,''),(6,11,''),(0,3,'')],
                         2:[(0,2,''),(1,6,''),(6,11,''),(3,12,'E')],3:[(1,2,''),(4,4,''),(5,5,''),(2,3,'E')],
                         4:[(6,6,'E'),(2,5,''),(1,7,''),(0,12,'')],5:[(1,2,''),(3,6,''),(0,12,''),(6,4,'E')],
                         6:[(5,3,''),(1,11,''),(4,6,'E'),(2,7,'')]
                         }
paachaadi_relations = ['paachaka','bodhaka','kaaraka','vedhaka']
# Pushkara bhaga = specific degress at which each sign is beneficial
# Pushkara navamsa = 3.20 degree range at which each sign is beneficial
pushkara_navamsa = [20,6+40/60,16+40/60,0,20,6+40/60,16+40/60,0,20,6+40/60,16+40/60,0]
pushkara_bhagas = [21,14,24,7,21,14,24,7,21,14,24,7]
pushkara_bhaga_jathaka_paarijaatha = [21,14,18,8,19,9,24,11,23,14,19,9]
graha_yudh_criteria_1 = 20 # planet latitudes are within 20 seconds
graha_yudh_criteria_2 = 1 # planet latitudes are within 1 degree
graha_yudh_criteria_3 = 2 # planet latitudes are within 2 degrees
planetary_aspect_ratios_on_houses = [
    [0,0,0.25,0.75,0.5,0,1.0,0.75,0.5,0.25,0,0], #Sun
    [0,0,0.25,0.75,0.5,0,1.0,0.75,0.5,0.25,0,0], #Moon
    [0,0,0.5,1.0,0.75,0,0.25,1.0,0.75,0.5,0,0], #Mars
    [0,0,0.25,0.75,0.5,0,1.0,0.75,0.5,0.25,0,0], #Mercury
    [0,0,0.75,0.25,1.0,0,0.5,0.25,1.0,0.75,0,0], #Jupiter
    [0,0,0.25,0.75,0.5,0,1.0,0.75,0.5,0.25,0,0], #Venus
    [0,0,1.0,0.5,0.25,0,0.75,0.5,0.25,1.0,0,0], #Saturn
    [1,1,1,1,1,1,1,1,1,1,1,1], # Rahu
    [1,1,1,1,1,1,1,1,1,1,1,1] #Ketu
]
 # Sun in 12th house, Moon/8th,Ma/7th,Me/7th,Ju/3rd,Ve/6th,Sa/1st,Ra/9th house,Ke/4th
marana_karaka_sthana_of_planets= [12,8,7,7,3,6,1,9,4]
# Latta Stars of planets = (nth star from planet's star based on its longitude, forward=1/backward=-1)
latta_stars_of_planets = [(12,1),(22,-1),(3,1),(7,-1),(6,1),(5,-1),(8,1),(9,-1),(9,-1)]
# Drekkana Table for each rasi with drekkana type for each drekkana hora
# Drekkana hora is 1st part 0-10 deg, 2nd part 10-20 and 3rd 20-30
# Drekkana types are Ayudha (1), Paasa (2), Nigala (3), Sarpa (4) Pakshi (5) and Chatushpada (6). And None = 0
# For example: Ar = Ayudha if rasi long in 0-10deg, Chatushpada if in 10-20 deg, Ayudha if rasi long in 20-30 deg
graha_drekkana_types = ['','ayudha','paasa','nigala','sarpa','pakshi','chatushpaada']
drekkana_table = [(1,6,1),(0,6,4),(0,1,1),(6,0,5),(4,0,1),(0,1,0),(0,4,1),(5,2,6),(1,0,1),(3,0,0),(4,0,0),(0,0,5)]
drekkana_table_bvraman = [(1,5,0),(0,6,6),(0,5,1),(6,4,4),(5,1,6),(0,1,5),(0,0,6),(4,4,6),(6,0,1),(2,0,1),(0,0,0),(0,0,0)]
# 3d List
# 1st 2d list is Vulture Last 2d list is Peacock
# 2d List: Each row is day (Sunday to Saturday) and Each column is 5 divisions of day time (sunrise to sunset)
# Activities: 1- Rule. 2- Eat. 3- Walk. 4- Sleep. 5- Die
pancha_pakshi_sukla_paksha_ruling_day_timings = [
    [[2,3,1,4,5],[5,2,3,1,4],[2,3,1,4,5],[5,2,3,1,4],[4,5,2,3,1],[1,4,5,2,3],[3,1,4,5,2] ], # Vulture
    ]
pancha_pakshi_sukla_paksha_ruling_night_timings = [
    [[5,3,4,2,1],[3,4,2,1,5],[5,3,4,2,1],[3,4,2,1,5],[4,2,1,5,3],[2,1,5,3,4],[1,5,3,4,2] ], # Vulture
    ]
pancha_pakshi_krishna_paksha_ruling_day_timings = [
    [[],[],[],[],[],[],[] ], # Vulture
    ]
pancha_pakshi_krishna_paksha_ruling_night_timings = [
    [[],[],[],[],[],[],[] ], # Vulture
    ]
#0:Udveg (Bad), 1:Chara(Good), 2:Laabha (Good), 3:Amrit(Good), 4:Kaala(Bad), 5:Shubha (Good), 6:Rog(Bad)
# Rows = Days Columns - choghadiyas
gauri_choghadiya_types = ['0:Udveg (Bad)','1:Chara(Good)','2:Laabha (Good)','3:Amrit(Good)','4:Kaala(Bad)','5:Shubha (Good)','6:Rog(Bad)']
gauri_choghadiya_day_table = [[0,1,2,3,4,5,6,0], # Sunday
                          [3,4,5,6,0,1,2,3], # Monday
                          [6,0,1,2,3,4,5,6], # Tuesday
                          [2,3,4,5,6,0,1,2], # Wednesday
                          [5,6,0,1,2,3,4,5], # Thursday
                          [1,2,3,4,5,6,0,1], # Friday
                          [4,5,6,0,1,2,3,4] # Saturday
                          ]
gauri_choghadiya_night_table = [[5,3,1,6,4,2,0,5], # Sunday
                          [1,6,4,2,0,5,3,1], # Monday
                          [4,2,0,5,3,1,6,4], # Tuesday
                          [0,5,3,1,6,4,2,0], # Wednesday
                          [3,1,6,4,2,0,5,3], # Thursday
                          [6,4,2,0,5,3,1,6], # Friday
                          [2,0,5,3,1,6,4,2] # Saturday
                          ]
#Rows = Days, Columns = Hora (12 hora for day and 12 hora for night)
#Hora = day/night length / 12.
#Each element is the planet that gives hora result
#Moon,Mercury,Jupiter and Venus are good
#order of hora results by planets [0:'Vigorous (Bad)',1:'Gentle (Good)' 2:'Aggressive (Bad)',3:'Quick (Good)',
#4:'Fruitful (Good), 5:'Beneficial (Good), 6:'Sluggish (Bad)'
shubha_hora_day_table = [[0, 1, 2, 3, 4, 5, 6],[5, 6, 0, 1, 2, 3, 4],[3, 4, 5, 6, 0, 1, 2],[1, 2, 3, 4, 5, 6, 0],
                         [6, 0, 1, 2, 3, 4, 5],[4, 5, 6, 0, 1, 2, 3],[2, 3, 4, 5, 6, 0, 1],[0, 1, 2, 3, 4, 5, 6],
                         [5, 6, 0, 1, 2, 3, 4],[3, 4, 5, 6, 0, 1, 2],[1, 2, 3, 4, 5, 6, 0],[6, 0, 1, 2, 3, 4, 5]
                        ]
shubha_hora_night_table = [[4, 5, 6, 0, 1, 2, 3],[2, 3, 4, 5, 6, 0, 1],[0, 1, 2, 3, 4, 5, 6],[5, 6, 0, 1, 2, 3, 4],
                            [3, 4, 5, 6, 0, 1, 2],[1, 2, 3, 4, 5, 6, 0],[6, 0, 1, 2, 3, 4, 5],[4, 5, 6, 0, 1, 2, 3],
                            [2, 3, 4, 5, 6, 0, 1],[0, 1, 2, 3, 4, 5, 6],[5, 6, 0, 1, 2, 3, 4],[3, 4, 5, 6, 0, 1, 2]
                        ]
# First element is starting time for amrita gadiya and second element starting time for varjyam for each star
# First tuple is Aswini and Last one for Revathi
# AmritaGadiya/Varjyam Starting time = starting time of star * factor from below table/24
# Duration = Duration of Star * 1.6/24 

amrita_gadiya_varjyam_star_map = [(16.8,20),(19.2,9.6),(21.6,12),(20.8,16),(15.2,5.6),(14,8.4),(21.6,12),(17.6,8),
                                  (22.4,12.8),(21.6,12),(17.6,8),(16.8,7.2),(18,8.4),(17.6,8),(15.2,5.6),(15.2,5.6),
                                  (13.6,4),(15.2,5.6),(17.6,(8,22.4)),(19.2,9.6),(17.6,8),(13.6,4),(13.6,4),
                                  (16.8,7.2),(16,6.4),(19.2,9.6),(21.6,12)]

anandhaadhi_yoga_names = ['anand','kaal','dhumra','prajapathi','soumya','dhwanksha','dhwaja','shreevathsa','vajra',
                          'mudgar','chathra','mithra','mansa','padhma','lumbkak','uthpath','mrithyu','kaan',
                          'siddhi','shubha','amruth','musal','gada','maathanga','raakshasa','chara','sthira',
                          'vrudh']
_get_abhijith_order_of_stars = lambda start_nak=1: \
            [*range(start_nak,21)]+[27]+[*range(21,27)]+[*range(start_nak)] if start_nak < 21 else \
            [*range(start_nak,27)]+[*range(21)]+[27]+[*range(21,start_nak)]
anandhaadhi_yoga_day_star_list = [_get_abhijith_order_of_stars(0), # Sunday
                                  _get_abhijith_order_of_stars(4), # Monday
                                  _get_abhijith_order_of_stars(7), # Tuesday
                                  _get_abhijith_order_of_stars(12),# Wednesday
                                  _get_abhijith_order_of_stars(16),# Thursday
                                  _get_abhijith_order_of_stars(20),# Friday
                                  _get_abhijith_order_of_stars(23) # Saturday
                                  ]
#0=Sathva 1=Rajas 2=Thamas index of each value element is Day
triguna_names = ['sathva','rajas','thamas']
triguna_days_dict = {1.3:[2,0,1,2,0,1,2],3:[0,1,2,0,1,2,0],4.5:[1,2,0,1,2,0,1],6:[2,0,1,2,0,1,2],7.5:[0,1,2,0,1,2,0],
                     9:[1,2,0,1,2,0,1],10.5:[2,0,1,2,0,1,2],12:[0,1,2,0,1,2,0],13.3:[1,2,0,1,2,0,1],15:[2,0,1,2,0,1,2],
                     16.5:[0,1,2,0,1,2,0],18:[1,2,0,1,2,0,1],19.5:[2,0,1,2,0,1,2],21:[0,1,2,0,1,2,0],22.5:[1,2,0,1,2,0,1],
                     24:[2,0,1,2,0,1,2]}
""" ========== Tamil Yogam Constants ========= """
tamil_yoga_names = ['siddha', 'prabalarishta', 'marana', 'amirtha','amirtha_siddha','mrithyu','daghda','yamaghata',
                    'uthpatha','sarvartha_siddha']
### Ref: https://tuningmymelody.blogspot.com/2023/04/the-type-of-yogas-and-muhurtha-yogas.html
tamil_basic_yoga_list=[[0,1,0,0,0,0,0,0,0,2,0,3,0,0,0,2,2,2,3,0,3,3,2,0,0,3,3], #Sunday
                       [0,0,2,3,0,0,3,0,0,2,0,0,0,1,3,2,0,0,0,2,2,3,0,0,0,0,0], #Monday
                       [0,0,0,3,0,2,0,0,0,0,0,3,0,0,0,2,0,2,3,0,1,0,0,2,2,3,0], #Tuesday
                       [2,0,3,0,0,0,0,0,0,0,3,3,2,0,0,0,0,0,2,3,3,0,1,0,3,0,2], #Wednesday
                       [3,0,2,2,2,2,3,0,0,3,0,2,0,0,3,0,0,1,0,0,0,0,0,2,0,0,0], #Thursday
                       [3,0,0,2,0,0,0,2,2,2,0,0,3,0,0,0,0,2,3,1,0,2,0,0,0,0,0], #Friday
                       [0,0,0,3,0,0,0,0,2,3,0,2,2,2,0,0,0,0,0,0,0,0,0,3,2,0,1]  #Saturday
                      ]
#Ref: https://sringeri.net/wp-content/uploads/2024/04/2024_25_krodhi_tamil_panchanga_sringeri.pdf
tamil_basic_yoga_sringeri_panchanga_list=[
        [0,0,0,3,0,0,0,0,0,2,0,3,3,0,0,2,2,2,3,0,3,3,2,0,0,3,3], #Sunday
        [0,0,2,3,3,0,3,0,0,2,0,0,0,0,3,2,0,0,0,0,2,3,0,0,2,0,0], #Monday
        [0,0,0,3,0,2,0,0,0,0,0,3,0,0,0,2,0,0,3,0,0,0,0,2,2,3,0], #Tuesday
        [2,0,3,0,0,0,0,0,0,0,3,3,2,0,0,0,0,0,2,3,3,0,1,0,3,0,2], #Wednesday
        [3,0,2,2,2,2,3,3,0,3,0,2,0,0,3,0,0,0,0,0,0,0,0,2,0,0,0], #Thursday
        [3,0,0,2,0,0,0,2,2,2,0,0,3,0,0,0,0,2,3,0,0,2,0,0,0,0,3], #Friday
        [0,0,3,3,0,0,0,0,2,3,0,2,2,2,3,0,0,0,0,0,0,0,0,3,2,0,2]  #Saturday
        ]
amrita_siddha_yoga_dict = {0:12,1:4,2:0,3:16,4:7,5:26,6:3} # day:star
mrityu_yoga_dict = {0:16, 1:20, 2:23, 3:0, 4:4, 5:17, 6:12} # day:star
daghda_yoga_dict = {0:1,1:13,2:20,3:22, 4:11,5:8,6:26}# day:star
yamaghata_yoga_dict = {0:9,1:15,2:5,3:18,4:2,5:3,6:12}# day: star
utpata_yoga_dict = {0:15, 1:19, 2:22, 3:26, 4:3, 5:7, 6:11}#day:star

sarvartha_siddha_yoga = {0:(12,18,20,11,25,0,7),1:(21,3,4,7,16),2:(0,25,2,8),3:(3,16,12,2,4),4:(26,16,0,6,7),
                       5:(26,16,0,6,21),6:(21,3,14)}# day:star

use_24hour_format_in_to_dms = True # V4.2.6
""" ============================================"""
tithi_deities = ['kaameshwari','bhaagamaalini','nithyaklinna','bherunda','vaahinivaasini','mahaavajreshwari',
                 'shivadoothi','thwaritha','kulasundari','nithya','neelapathaka','vijaya','sarvamangala',
                 'jwaalamaalini','chithra','shodhashi'] ## Last 2 are Amavasai and Pournami
#(Yogam Ruling Planet / Yoga Point , Avayogi Planet)
yogam_lords_and_avayogis = [(6,1),(3,2),(8,7),(5,4),(0,6),(1,3),(2,8),(7,5),(4,0),
                            (6,1),(3,2),(8,7),(5,4),(0,6),(1,3),(2,8),(7,5),(4,0),
                            (6,1),(3,2),(8,7),(5,4),(0,6),(1,3),(2,8),(7,5),(4,0)
                            ]
use_planet_speed_for_panchangam_end_timings = True # True # Changed to False in V4.6.0
#0=East, 1=South, 2=West, 3=North
disha_shool_map = [2,0,3,3,1,2,0]#Sunday to Saturday

#Ref:https://www.astrodivine.com/chandra_bhedi_plot.htm
#0=East, 1=South, 2=West, 3=North, 4=South West, 5=North West, 6=North East 7=South East
yogini_vaasa_tithi_map = [0,3,7,5,1,2,5,6,0,3,7,5,1,2,5,0,3,7,5,1,2,5,6,0,3,7,5,1,2,6]
periods_of_the_day = ['purvaanha','madhyannha','aparanha','saayankaala','pradosha','nishitha','triyaama','ushaa']
muhurthas_of_the_day = {'rudra':0,'aahi':0,'mithra':1,'pithra':0,'vasu':1,'varaaha':1,'vishvedeva':1,'vidhi':1,
                         'sathamukhi':1,'puruhootha':0,'vaahini':0,'nakthanakaara':0,'varuna':1,'aaryaman':1,'bhaga':0,
                         'girisha':1,'ajapaadha':0,'aahirbhudhnya':1,'pushya':1,'ashvini':1,'yama':0,'agni':1,
                         'vidharth':1,'kanda':1,'adhithi':1,'jeeva':1,'vishnu':1,'dhyumadadhyuthi':1,
                         'brahma':1,'samudhra':1} # 0 - Inauspicious 1=Auspicious
### Tamil month methods: 0=> Ravi Annasamy (sunset/UTC) 1=>V4.3.5 (sunset as starting jd) 2=>Start jd with 10AM
##                       3 => Midday, UTC
tamil_month_method = 3
#### Enable / Disable World City Checking
check_database_for_world_cities = True
use_internet_for_location_check = True
one_second_lontitude_in_degrees = 1.0/3600.
""" To match Pramaadhi (North Indian) or Prabhava (South Indian) Set ONLY ONE of the below to True.
    Or If you dont like this experiment set both to False
    This means before Kali Year 4099 - i.e. 908AD - The South And North do not share year names
"""
force_kali_start_year_for_years_before_kali_year_4009 = True
kali_start_year = 13 # 13 (Pramaadhi) North or 1 (Prabhava) for South
# Special Tithis
special_tithis = ['janma','dhana','bhrartri','matri','putra','satru','kalatra','mrutyu','bhagya','karma','laabha','vyaya']
skip_using_girls_varna_for_minimum_tamil_porutham = True # V4.5.5

if __name__ == "__main__":
    pass
