import os
import swisseph as swe
import numpy as np
""" Module describing PyHora constants"""
" setup paths "
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_IMAGES_PATH = os.path.dirname(ROOT_DIR+"images\\")
_IMAGE_ICON_PATH=os.path.join(ROOT_DIR,"images\\lord_ganesha2.jpg")
_INPUT_DATA_FILE = os.path.join(ROOT_DIR,'data\\program_inputs.txt')
_world_city_csv_file = os.path.join(ROOT_DIR,'data\\world_cities_with_tz.csv')
_EPHIMERIDE_DATA_PATH = os.path.join(ROOT_DIR,'data\\ephe\\')
_LANGUAGE_PATH = os.path.join(ROOT_DIR,'lang\\')
_DEFAULT_LANGUAGE = 'en'
_DEFAULT_LANGUAGE_LIST_STR = 'list_values_'
_DEFAULT_LANGUAGE_MSG_STR = 'msg_strings_'
_DEFAULT_YOGA_JSON_FILE_PREFIX = "yoga_msgs_" 
_INCLUDE_URANUS_TO_PLUTO = True # Only for Western Charts
_degree_symbol = "°" 
_minute_symbol = u'\u2019'
_second_symbol = '"'

_planet_symbols=['ℒ','☉','☾','♂','☿','♃','♀','♄','☊','☋']
_zodiac_symbols = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D', '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653']

available_languages = {"English":'en','Tamil':'ta','Telugu':'te','Hindi':"hi",'Kannada':'ka'}
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
division_chart_factors = [1,2,3,4,5,6,7,8,9,10,11,12,16,20,24,27,30,40,45,60]
dhasavarga_amasa_factors = [1,2,3,7,9,10,12,16,30,60]
shadvarga_amsa_factors = [1,2,3,9,12,30]
sapthavarga_amsa_factors = [1,2,3,7,9,12,30]
shodhasa_varga_amsa_factors = [1,2,3,4,7,9,10,12,16,20,24,27,30,40,45,60]
vimsamsa_varga_amsa_factors = division_chart_factors

### String Constants for panchanga.
"""
    set this to =swe.PLUTO  for Vimoshotari functions. BUT KETHU will be SHOWN AS PLUTO DHASA/BHUKTI
    set this to - -10 for chart creation (otherwise chart will show Pluto for Kethu)
    following assignments due to changes in swiss ephe 2.8
"""
_KETU = -swe.MEAN_NODE
_RAHU = swe.MEAN_NODE
_SUN = swe.SUN
SURYA = _SUN 
_MOON = swe.MOON
CHANDRA = _MOON
_MARS = swe.MARS
KUJA = _MARS
_MERCURY = swe.MERCURY
BUDHA = _MERCURY
_JUPITER = swe.JUPITER 
GURU = _JUPITER
_VENUS = swe.VENUS
SUKRA = _VENUS
_SATURN = swe.SATURN
SANI = _SATURN
_URANUS = swe.URANUS
_NEPTUNE = swe.NEPTUNE
_PLUTO = swe.PLUTO
_TROPICAL_MODE = False
_EPHIMERIDE_DATA_PATH = ROOT_DIR+'/data/ephe/'
_LANGUAGE_PATH = ROOT_DIR+'/lang/'
_solar_upagraha_list = ['dhuma','vyatipaata','parivesha','indrachaapa','upaketu']
_other_upagraha_list = ['kaala','mrityu','artha_prabhakara','yama','gulika','maandi']
_special_lagna_list = ['bhava_lagna','hora_lagna','ghati_lagna','sree_lagna']

_ephe_path = os.path.abspath(_EPHIMERIDE_DATA_PATH)
swe.set_ephe_path(_ephe_path)
sidereal_year = 365.256360417   # From WolframAlpha
average_gregorian_year = 365.2425 
human_life_span_for_dhasa = 120. ## years
vimsottari_year = sidereal_year  # some say 360 days, others 365.25 or 365.2563 etc
# Nakshatra lords, order matters. See https://en.wikipedia.org/wiki/Dasha_(astrology)
adhipati_list = [ 8, 5, 0, 1, 2, 7, 4, 6, 3 ]

# (Maha-)dasha periods (in years)
mahadasa = { 8: 7, 5: 20, 0: 6, 1: 10, 2: 7,7: 18, 4: 16, 6: 19, 3: 17 }

# assert(0 <= nak <= 26)

available_ayanamsa_modes = {"FAGAN":swe.SIDM_FAGAN_BRADLEY ,"KP": swe.SIDM_KRISHNAMURTI, "LAHIRI": swe.SIDM_LAHIRI, "RAMAN": swe.SIDM_RAMAN, 
                            "USHASHASHI": swe.SIDM_USHASHASHI, "YUKTESHWAR": swe.SIDM_YUKTESHWAR, "SURYASIDDHANTA": swe.SIDM_SURYASIDDHANTA,
                            "SURYASIDDHANTA_MSUN": swe.SIDM_SURYASIDDHANTA_MSUN, "ARYABHATA":swe.SIDM_ARYABHATA, "ARYABHATA_MSUN":swe.SIDM_ARYABHATA_MSUN,
                            "SS_CITRA":swe.SIDM_SS_CITRA, "TRUE_CITRA":swe.SIDM_TRUE_CITRA, "TRUE_REVATI":swe.SIDM_TRUE_REVATI,
                            "SS_REVATI": swe.SIDM_SS_REVATI,'SENTHIL':'', 'SUNDAR_SS':'',"SIDM_USER":swe.SIDM_USER,
                            #"KP-SENTHIL":swe.SIDM_KRISHNAMURTI_VP291,
                            #"TRUE_PUSHYA":swe.SIDM_TRUE_PUSHYA, "TRUE_MULA":swe.SIDM_TRUE_MULA, "ARYABHATA_522":swe.SIDM_ARYABHATA_522, 
                            }

human_life_span_for_vimsottari_dhasa = 120
# Nakshatra lords, order matters. See https://en.wikipedia.org/wiki/Dasha_(astrology)
vimsottari_adhipati_list = [ 8, 5, 0, 1, 2, 7, 4, 6, 3 ]

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
ashtaka_varga_dict={
    "0":[[1,2,4,7,8,9,10,11],[3,6,10,11],[1,2,4,7,8,9,10,11],[3,5,6,9,10,11,12],[5,6,9,11],[6,7,12],[1,2,4,7,8,9,10,11],[3,4,6,10,11,12]],
    "1":[[3,6,7,8,10,11 ],[1,3,6,7,9,10,11],[2,3,5,6,10,11],[1,3,4,5,7,8,10,11],[1,2,4,7,8,10,11],[3,4,5,7,9,10,11],[3,5,6,11],[3,6,10,11]],
    "2":[[3,5,6,10,11],[3,6,11],[1,2,4,7,8,10,11],[3,5,6,11],[6,10,11,12],[6,8,11,12],[1,4,7,8,9,10,11],[1,3,6,10,11]],
    "3":[[5,6,9,11,12],[2,4,6,8,10,11],[1,2,4,7,8,9,10,11],[1,3,5,6,9,10,11,12],[6,8,11,12],[1,2,3,4,5,8,9,11],[1,2,4,7,8,9,10,11],[1,2,4,6,8,10,11]],
    "4":[[1,2,3,4,7,8,9,10,11],[2,5,7,9,11],[1,2,4,7,8,10,11],[1,2,4,5,6,9,10,11],[1,2,3,4,7,8,10,11],[2,5,6,9,10,11],[3,5,6,12],[1,2,4,5,6,7,9,10,11]],
    "5":[[8,11,12],[1,2,3,4,5,8,9,11,12],[3,4,6,9,11,12],[3,5,6,9,11],[5,8,9,10,11],[1,2,3,4,5,8,9,10,11],[3,4,5,8,9,10,11],[1,2,3,4,5,8,9,11]],
    "6":[[1,2,4,7,8,10,11],[3,6,11],[3,5,6,10,11,12],[6,8,9,10,11,12],[5,6,11,12],[6,11,12],[3,5,6,11],[1,3,4,6,10,11]],
    "7":[[3,4,6,10,11,12],[3,6,10,11,12],[1,3,6,10,11],[1,2,4,6,8,10,11],[1,2,4,5,6,7,9,10,11],[1,2,3,4,5,8,9],[1,3,4,6,10,11],[3,6,10,11]] ## This is for Lagna
    }

natural_benefics = [5,6] #Mercury benefic if alone or with other benefics. Moon benefic in sukla paksha (tithi <=15) 
natural_malefics = [0,1,7,8]
feminine_planets = [1,3,5,6]
masculine_planets = [0,2,4]
harsha_bala_houses = [8,2,5,0,10,11,11]
harsha_bala_feminine_houses = [0,1,2,6,7,8]
harsha_bala_masculine_houses = [3,4,5,9,10,11]

" house module constants "
house_lords_dict = {0:[4],1:[3],2:[0,7],3:[2,5],4:[8,11],5:[1,6],6:[9,10],7:[10],8:[7]}
houses_of_rahu_kethu = {7:10,8:7}
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
temporary_friend_raasi_positions = [2,3,4,10,11,12]
temporary_enemy_raasi_positions = [1,5,6,7,8,9]
friend_enemy_addition =   [[0.5, 0],
                           [0  , 0],
                           [0, -0.5]
                          ] 
""" 3:'Friend',2:'Samam',1:'Enemy' """
planet_relations = [ [5,3,3,2,3,1,1],
                     [3,5,2,3,2,2,2],
                     [3,3,5,1,3,2,2],
                     [3,1,2,5,2,3,2],
                     [3,3,3,1,5,1,2],
                     [1,1,2,3,2,5,3],
                     [1,1,1,3,2,3,5]
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

#"""
_friendly_planets = [[1,2,4],[0,3],[0,1,4],[0,5],[0,1,2],[3,6],[3,5]]
_neutral_planets = [[3],[2,4,5,6],[5,6],[2,4,6],[6],[2,4],[4]]
_enemy_planets = [[5,6],[],[3],[1],[3,5],[0,1],[0,1,2]]
#"""
house_owners = np.where(np.array(house_strengths_of_planets).transpose()==5)[1]
_house_owners_old = [2,5,3,1,0,3,5,2,4,6,6,4]
planet_deep_exaltation_longitudes = [10.0,33.0,298.0,165.0,95.0,357.0,200.0]
planet_deep_debilitation_longitudes = [(e+180.0)%360 for e in planet_deep_exaltation_longitudes]
graha_drishti = {0:[7],1:[7],2:[4,7,8],3:[7],4:[5,7,9],5:[7],6:[3,7,10],7:[],8:[],9:[],10:[],11:[]}
movable_signs = [0,3,6,9]
fixed_signs = [1,4,7,10]
dual_signs = [2,5,8,11]
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
use_BPHS_formula_for_uccha_bala = True
pancha_vargeeya_bala_strength_threshold = 10
order_of_planets_by_speed = [6,7,8,4,2,0,5,3,1] # Saturn is slowest and moon is fastest
deeptaamsa_of_planets=[15,12,8,7,9,7,9] #sun, moon,mars,mercury,jupiter,venus,saturn
combustion_range_of_planets_from_sun = [0,12,17,14,10,11,15] #moon,mars,mercury,jupiter,venus,saturn
combustion_range_of_planets_from_sun_while_in_retrogade = [12,17,12,8,11,15] #moon,mars,mercury,jupiter,venus,saturn

if __name__ == "__main__":
    pass