import swisseph as swe
import json
from hora import const,utils
from hora.horoscope import main
from hora.panchanga import panchanga
from hora.horoscope.chart import house, charts
from hora.horoscope.transit import tajaka
_lang_path = const._LANGUAGE_PATH

movable_signs = const.movable_signs
fixed_signs = const.fixed_signs
dual_signs = const.dual_signs
seven_planets = [*range(7)] # Rahu and Ketu are excluded
all_planets = [*range(9)]

division_chart_factors = const.division_chart_factors
quandrants_of_the_house = lambda raasi: house.quadrants_of_the_raasi(raasi) 
#h_to_p = lambda pp,h: utils.get_house_planet_list_from_planet_positions(pp)[h]
#p_to_h = lambda pp,p: utils.get_planet_house_dictionary_from_planet_positions(pp)[p]
def get_yoga_resources(language='en'):
    """
        get yoga names from yoga_msgs_<lang>.txt
        @param language: Tow letter language code. en, hi, ka, ta, te
        @return json strings from the resource file as dictionary 
    """
    msgs = {}
    json_file = _lang_path + const._DEFAULT_YOGA_JSON_FILE_PREFIX+language+'.json'
    f = open(json_file,"r",encoding="utf-8")
    msgs = json.load(f)
    return msgs
def get_yoga_details_for_all_charts(jd,place,language='en'):
    """
        Get all the yoga information that are present in the divisional charts for a given julian day and place
        @param jd: Julian day number
        @param place: struct (plave name, latitude, longitude, timezone)
        @param language: two letter language code (en, hi, ka, ta, te)
        @return: returns a 2D List of yoga_name, yoga_details
            yoga_name in language
            yoga_details: [chart_ID, yoga_name, yoga_desription, yoga_benfits] 
    """
    global p_to_h_navamsa, h_to_p_navamsa, asc_house_navamsa
    msgs = get_yoga_resources(language=language)
    yoga_results_combined = {}
    ascendant_index = 'L'
    planet_positions_navamsa = panchanga.dhasavarga(jd,place,sign_division_factor=9)
    ascendant_longitude = panchanga.ascendant(jd,place)[1]
    asc_house_navamsa,asc_long = panchanga.dasavarga_from_long(ascendant_longitude,sign_division_factor=9)
    planet_positions_navamsa += [[ascendant_index,(asc_house_navamsa,asc_long)]]
    p_to_h_navamsa = { p:h for p,(h,_) in planet_positions_navamsa}
    h_to_p_navamsa = ['' for h in range(12)] 
    for sublist in planet_positions_navamsa:
        p = sublist[0]
        h = sublist[1][0]
        h_to_p_navamsa[h] += str(p) + '/'
    for dv in division_chart_factors:
        yoga_results,_,_ = get_yoga_details(jd,place,divisional_chart_factor=dv,language=language)
        yoga_results.update(yoga_results_combined)
        yoga_results_combined = yoga_results
    print('Found',len(yoga_results_combined),'out of',len(msgs)*len(division_chart_factors),'yogas')
    return yoga_results_combined,len(yoga_results_combined),len(msgs)*len(division_chart_factors)
def get_yoga_details(jd,place,divisional_chart_factor=1,language='en'):
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
    global p_to_h, h_to_p, asc_house, planet_positions
    msgs = get_yoga_resources(language=language)
    ascendant_index = 'L'
    planet_positions = panchanga.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = panchanga.ascendant(jd,place)[1]
    asc_house,asc_long = panchanga.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[ascendant_index,(asc_house,asc_long)]]
    p_to_h = { p:h for p,(h,_) in planet_positions}
    h_to_p = ['' for h in range(12)] 
    for sublist in planet_positions:
        p = sublist[0]
        h = sublist[1][0]
        h_to_p[h] += str(p) + '/'
    yoga_results = {}
    for yoga_function,details in msgs.items():
        yoga_exists = eval(yoga_function)(h_to_p,p_to_h,asc_house)#(planet_positions)#
        if yoga_exists:
            details.insert(0,'D'+str(divisional_chart_factor))
            yoga_results[yoga_function] = details
    print('Found',len(yoga_results),'out of',len(msgs),'yogas in D'+str(divisional_chart_factor),'chart')
    return yoga_results,len(yoga_results),len(msgs)
""" Sun Yogas """
def vesi_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Vesi Yoga - There is a planet other than Moon in the 2nd house from Sun. """
    vesi_yoga = str(1) not in h_to_p[(p_to_h[0]+1)%12] # check if moon is present in 2nd house
    return vesi_yoga
def vosi_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Vosi Yoga - There is a planet other than Moon in the 12th house from Sun. """
    vosi_yoga = str(1) not in h_to_p[(p_to_h[0]+11)%12] # check if moon is present in 2nd house
    return vosi_yoga
def ubhayachara_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Ubhayachara  Yoga - There is a planet other than Moon in the 2nd and 12th house from Sun. """
    ubhayachara_yoga = vesi_yoga(h_to_p,p_to_h,asc_house) and vosi_yoga(h_to_p,p_to_h,asc_house)
    return ubhayachara_yoga
def nipuna_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Budha-Aaditya Yoga (Nipuna Yoga)- If Sun and Mercury are together (in one sign), this yoga is present."""
    nipuna_yoga = any(['0' in p and '3' in p for p in h_to_p])
    return nipuna_yoga
def sunaphaa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Sunaphaa Yoga - There are planets other than Sun in the 2nd house from Moon"""
    sunaphaa_yoga = str(0) not in h_to_p[(p_to_h[1]+1)%12]
    return sunaphaa_yoga
def anaphaa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Anaphaa Yoga - There are planets other than Sun in the 12th house from Moon"""
    anaphaa_yoga = str(0) not in h_to_p[(p_to_h[1]+11)%12]
    return anaphaa_yoga
def duradhara_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Duradhara Yoga - There is a planet other than Sun in the 2nd and 12th house from Moon. """
    duradhara_yoga = sunaphaa_yoga(h_to_p,p_to_h,asc_house) and anaphaa_yoga(h_to_p,p_to_h,asc_house)
    return duradhara_yoga
def kemadruma_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Kemadruma Yoga - there are no planets other than Sun in the 1st, 2nd and 12th houses from
        Moon and if there are no planets other than Moon in the quadrants from lagna"""
    ky_yoga_1 = str(0) not in h_to_p[(p_to_h[1])%12]
    ky_yoga_2 = duradhara_yoga and ky_yoga_1
    planets_in_lagnam_quadrant = []
    planets_in_lagnam_quadrant += [h_to_p[a] for a in quandrants_of_the_house(asc_house)]
    ky_yoga_3 = not( [0]+[range(2,9)] in planets_in_lagnam_quadrant)
    kemadruma_yoga = ky_yoga_2 and ky_yoga_3
    return kemadruma_yoga
def chandra_mangala_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Chandra-Mangala Yoga - Moon and Mars are together (in one sign). """
    chandra_mangala_yoga = any(['1' in p and '2' in p for p in h_to_p])
    return chandra_mangala_yoga
def adhi_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Adhi Yoga - natural benefics occupy 6th, 7th and 8th from Moon, """
    # AND is used to check ALL NATURAL BENEFICS are in 6 or 7 or 8 from moon
    adhi_yoga_1 = any('5' in x or '6' in x for x in [h_to_p[(p_to_h[1]+mh-1)%12] for mh in [6,7,8] ])
    #Mercury (3) benefic if alone.
    adhi_yoga_2 = any(x=='3' for x in [h_to_p[(p_to_h[1]+mh-1)%12] for mh in [6,7,8] ])
    adhi_yoga = adhi_yoga_1 or adhi_yoga_2
    return adhi_yoga
def ruchaka_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """  Ruchaka Yoga - Mars should be in 0 or 7 or 9th rasi and he should be in 1, 4, 7 or 10th from lagna """
    ruchaka_yoga_1 = any('2' in x for x in [h_to_p[y] for y in [0,7,9]])
    ruchaka_yoga_2 = any('2' in x for x in [h_to_p[(asc_house+mh-1)%12] for mh in [1,4,7,10] ])
    ruchaka_yoga = ruchaka_yoga_1 and ruchaka_yoga_2
    return ruchaka_yoga
def bhadra_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Bhadra Yoga - Mercury should be in Ge or Vi and he should be in 1st, 4th, 7th or 10th from lagna. """
    bhadra_yoga_1 = any('3' in x for x in [h_to_p[y] for y in [2,5]])
    bhadra_yoga_2 = any('3' in x for x in [h_to_p[(asc_house+mh-1)%12] for mh in [1,4,7,10] ])
    bhadra_yoga = bhadra_yoga_1 and bhadra_yoga_2
    return bhadra_yoga
def sasa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Saturn should be in Cp, Aq or Li and he should be in 1st, 4th, 7th or 10th from lagna. """
    sasa_yoga_1 = any('6' in x for x in [h_to_p[y] for y in [6,9,10]])
    sasa_yoga_2 = any('6' in x for x in [h_to_p[(asc_house+mh-1)%12] for mh in [1,4,7,10] ])
    sasa_yoga = sasa_yoga_1 and sasa_yoga_2
    return sasa_yoga
def maalavya_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Maalavya Yoga - Venus should be in Ta, Li or Pi and he should be in 1st, 4th, 7th or 10th from lagna. """
    maalavya_yoga_1 = any('5' in x for x in [h_to_p[y] for y in [1,6,11]])
    maalavya_yoga_2 = any('5' in x for x in [h_to_p[(asc_house+mh-1)%12] for mh in [1,4,7,10] ])
    maalavya_yoga = maalavya_yoga_1 and maalavya_yoga_2
    return maalavya_yoga
def hamsa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Hamsa Yoga - Jupiter should be in Sg, Pi or Cn and he should be in 1st, 4th, 7th or 10th from lagna. """
    hamsa_yoga_1 = any('4' in x for x in [h_to_p[y] for y in [8,9,11]])
    hamsa_yoga_2 = any('4' in x for x in [h_to_p[(asc_house+mh-1)%12] for mh in [1,4,7,10] ])
    hamsa_yoga = hamsa_yoga_1 and hamsa_yoga_2
    return hamsa_yoga
def rajju_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Rajju Yoga: all the planets are exclusively in movable signs """
    rajju_yoga = all(p_to_h[p] in movable_signs for p in range(9))
    return rajju_yoga
def musala_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Musala Yoga: all the planets are exclusively in fixed signs """
    musala_yoga = all(p_to_h[p] in fixed_signs for p in range(9))
    return musala_yoga
def nala_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Nala Yoga: all the planets are exclusively in dual signs, """
    nala_yoga = all(p_to_h[p] in dual_signs for p in range(9))
    return nala_yoga
def maalaa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Maalaa Yoga: If three quadrants from Lagna are occupied by natural benefics, """
    planets_in_lagnam_quadrant = []
    planets_in_lagnam_quadrant += [h_to_p[a].split('/') for a in quandrants_of_the_house(asc_house)]
    chk = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant[1:]] for nb in const.natural_benefics]
    maalaa_yoga = all(any(row) for row in chk)
    return maalaa_yoga
def sarpa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Sarpa Yoga: If three quadrants from lagna are occupied by natural malefics, """
    planets_in_lagnam_quadrant = []
    planets_in_lagnam_quadrant += [h_to_p[a].split('/') for a in quandrants_of_the_house(asc_house)]
    chk = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant[1:]] for nb in const.natural_malefics]
    sarpa_yoga = all(any(row) for row in chk)
    return sarpa_yoga
def gadaa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Gadaa Yoga: all the planets occupy two successive quadrants from lagna """
    slq = [tuple(sorted(((asc_house)%12, (asc_house+3)%12))), tuple(sorted(((asc_house+3)%12,(asc_house+6)%12))),
            tuple(sorted(((asc_house+6)%12,(asc_house+9)%12))),tuple(sorted(((asc_house+9)%12,asc_house%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    gadaa_yoga = sph in slq
    return gadaa_yoga
def sakata_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Sakata Yoga: If all the planets occupy 1st and 7th houses from lagna """
    slq = slq = [tuple(sorted(((asc_house)%12, (asc_house+6)%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    sakata_yoga = sph in slq
    return sakata_yoga
def vihanga_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Vihanga Yoga: If all the planets occupy 4th and 10th houses from lagna """
    slq = [tuple(sorted(((asc_house+3)%12, (asc_house+9)%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    vihanga_yoga = sph in slq
    return vihanga_yoga
def sringaataka_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Sringaataka Yoga: If all the planets occupy trines (1st, 5th and 9th) from lagna """
    slq = [tuple(sorted(((asc_house+3)%12, (asc_house+4)%12, (asc_house+8)%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    sringaataka_yoga = sph in slq
    return sringaataka_yoga
def hala_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Hala Yoga: If all the planets occupy mutual trines but not trines from lagna """
    slq = [tuple(sorted(((asc_house+1)%12, (asc_house+5)%12, (asc_house+9)%12))),
        tuple(sorted(((asc_house+2)%12, (asc_house+6)%12, (asc_house+10)%12))),
        tuple(sorted(((asc_house+3)%12, (asc_house+7)%12, (asc_house+11)%12)))
        ]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    hala_yoga = sph in slq
    return hala_yoga
def vajra_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Vajra Yoga: If lagna and the 7th houses are occupied by natural benefics and the 4th
        and 10th houses are occupied by natural malefics """
    chk1 = [[str(nb) in h_to_p[a] for a in [asc_house%12,(asc_house+6)%12 ]] for nb in const.natural_benefics]
    vajra_yoga_1 = all(any(row) for row in chk1)
    chk2 = [[str(nb) in h_to_p[a] for a in [(asc_house+3)%12,(asc_house+9)%12 ]] for nb in const.natural_malefics]
    vajra_yoga_2 = all(any(row) for row in chk2)
    vajra_yoga = vajra_yoga_1 and vajra_yoga_2
    return vajra_yoga
def yava_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Yava Yoga: If lagna and the 7th houses are occupied by natural malefics and the 4th
        and 10th houses are occupied by natural benefics, """
    chk1 = [[str(nb) in h_to_p[a] for a in [asc_house%12,(asc_house+6)%12 ]] for nb in const.natural_malefics]
    chk2 = [[str(nb) in h_to_p[a] for a in [(asc_house+3)%12,(asc_house+9)%12 ]] for nb in const.natural_benefics]
    yava_yoga_1 = all(any(row) for row in chk1)
    yava_yoga_2 = all(any(row) for row in chk2)
    yava_yoga = yava_yoga_1 and yava_yoga_2
    return yava_yoga
def kamala_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Kamala Yoga: If all the planets are in quadrants from lagna, """
    planets_in_lagnam_quadrant = [h_to_p[a] for a in quandrants_of_the_house(asc_house)]
    chk = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant] for nb in all_planets]
    kamala_yoga = all(any(row) for row in chk)
    return kamala_yoga
def vaapi_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Vaapi Yoga: If all the planets are panaparas or in apoklimas """
    panaparas_planets = [h_to_p[h] for h in [(asc_house+1)%12,(asc_house+4)%12,(asc_house+7)%12,(asc_house+10)%12]]
    apoklimas_planets = [h_to_p[h] for h in [(asc_house+2)%12,(asc_house+5)%12,(asc_house+8)%12,(asc_house+11)%12]]
    chk = [[str(nb) in str(pl) for pl in panaparas_planets+apoklimas_planets] for nb in all_planets]
    vaapi_yoga = all(any(row) for row in chk)
    return vaapi_yoga
def yoopa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Yoopa Yoga: all the planets are in 1st, 2nd, 3rd and 4th houses from lagna """
    spl = [h_to_p[h] for h in [(asc_house)%12,(asc_house+1)%12,(asc_house+2)%12,(asc_house+3)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    yoopa_yoga = all(any(row) for row in chk)
    return yoopa_yoga
def sara_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Sara Yoga: all the planets are in 4th, 5th, 6th and 7th houses from lagna, """
    spl = [h_to_p[h] for h in [(asc_house+3)%12,(asc_house+4)%12,(asc_house+5)%12,(asc_house+6)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    sara_yoga = all(any(row) for row in chk)
    return sara_yoga
def sakti_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Sakti Yoga: If all the planets are in 7th, 8th, 9th and 10th houses from lagna """
    spl = [h_to_p[h] for h in [(asc_house+6)%12,(asc_house+7)%12,(asc_house+8)%12,(asc_house+9)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    sakti_yoga = all(any(row) for row in chk)
    return sakti_yoga
def danda_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Danda Yoga: If all the planets are in 10th, 11th, 12th and 1st houses from lagna """
    spl = [h_to_p[h] for h in [(asc_house+9)%12,(asc_house+10)%12,(asc_house+11)%12,(asc_house+12)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    danda_yoga = all(any(row) for row in chk)
    return danda_yoga
def naukaa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Naukaa Yoga: If all the planets occupy the 7 signs from lagna """
    spl = [h_to_p[h] for h in [(asc_house+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    naukaa_yoga = all(any(row) for row in chk)
    return naukaa_yoga
def koota_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Koota Yoga: If all the planets occupy the 7 signs from the 4th house """
    spl = [h_to_p[h] for h in [(asc_house+3+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    koota_yoga = all(any(row) for row in chk)
    return koota_yoga
def chatra_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Chatra Yoga: If all the planets occupy the 7 signs from the 7th house, """
    spl = [h_to_p[h] for h in [(asc_house+6+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    chatra_yoga = all(any(row) for row in chk)
    return chatra_yoga
def chaapa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Chaapa Yoga: If all the planets occupy the 7 signs from the 10th house """
    spl = [h_to_p[h] for h in [(asc_house+9+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    chaapa_yoga = all(any(row) for row in chk)
    return chaapa_yoga
def ardha_chandra_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Ardha Chandra Yoga: If all the planets occupy the 7 signs starting from a panapara or an apoklima """
    chka=False
    for pa in [1,2,4,5,7,8,10,11]:
        spl = [h_to_p[h] for h in [(asc_house+pa-1+i)%12 for i in range(7)]]
        chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
        chka= chka or (all(any(row) for row in chk))
        #print(spl,chka)
        if chka:
            break
    ardha_chandra_yoga = chka
    return ardha_chandra_yoga
def chakra_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Chakra Yoga: If all the planets occupy 1st, 3rd, 5th, 7th, 9th and 11th houses """
    spl = [h_to_p[h] for h in [(asc_house-1+i)%12 for i in [1,3,5,7,9,11]]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    chakra_yoga = all(any(row) for row in chk)
    return chakra_yoga
def samudra_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Samudra Yoga: If all the planets occupy 2nd, 4th, 6th, 8th, 10th and 12th houses """
    spl = [h_to_p[h] for h in [(asc_house-1+i)%12 for i in [2,4,6,8,10,12]]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    samudra_yoga = all(any(row) for row in chk)
    return samudra_yoga
def veenaa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Veenaa Yoga: If the seven planets occupy exactly 7 distinct signs among them """
    chk = [p_to_h[p] for p in seven_planets]
    veenaa_yoga = len(chk) == 7
    return veenaa_yoga
def daama_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Daama Yoga: If the seven planets occupy exactly 6 distinct signs among them """
    chk = [p_to_h[p] for p in seven_planets]
    daama_yoga = len(chk) == 6
    return daama_yoga
def paasa_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Paasa Yoga: If the seven planets occupy exactly 5 distinct signs among them """
    chk = [p_to_h[p] for p in seven_planets]
    paasa_yoga = len(chk) == 5
    return paasa_yoga
def kedaara_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Kedaara Yoga: If the seven planets occupy exactly 4 distinct signs among them """
    chk = [p_to_h[p] for p in seven_planets]
    kedaara_yoga = len(chk) == 4
    return kedaara_yoga
def soola_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Soola Yoga: If the seven planets occupy exactly 3 distinct signs among them """
    chk = [p_to_h[p] for p in seven_planets]
    soola_yoga = len(chk) == 3
    return soola_yoga
def yuga_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Yuga Yoga: If the seven planets occupy exactly 2 distinct signs among them """
    chk = [p_to_h[p] for p in seven_planets]
    yuga_yoga = len(chk) == 2
    return yuga_yoga
def gola_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Gola Yoga: If the seven planets are in one sign """
    chk = [p_to_h[p] for p in seven_planets]
    gola_yoga = len(chk) == 1
    return gola_yoga
def subha_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Subha Yoga: If lagna has benefics or has “subha kartari – benefics in 12th and 2nd """
    chk = [[str(nb) in h_to_p[a] for a in [(asc_house)%12,(asc_house+1)%12,(asc_house+11)%12 ]] for nb in const.natural_benefics]
    subha_yoga = all(any(row) for row in chk)
    return subha_yoga
def asubha_yoga(h_to_p,p_to_h,asc_house):#(h_to_p,p_to_h,asc_house):
    """ Asubha Yoga: If lagna has malefics or has “paapa kartari” – malefics in 12th and 2nd """
    chk = [[str(nb) in h_to_p[a] for a in [(asc_house)%12,(asc_house+1)%12,(asc_house+11)%12 ]] for nb in const.natural_malefics]
    asubha_yoga = all(any(row) for row in chk)
    return asubha_yoga
def gaja_kesari_yoga(h_to_p,p_to_h,asc_house):
    """ Gaja-Kesari Yoga: If (1) Jupiter is in a quadrant from Moon, (2) a benefic planet
        conjoins or aspects Jupiter, and, (3) Jupiter is not debilitated or combust or in an
        enemy’s house, """
    #h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    jupiter_house = p_to_h[4]
    chk1 = 4 in quandrants_of_the_house(p_to_h[1])
    #print(chk1,quandrants_of_the_house(p_to_h[1]))
    if not chk1:
        return False
    bpj = tajaka.benefic_aspects_of_the_planet(h_to_p, 4)[1]
    chk2 = any(int(p) in const.natural_benefics or p_to_h[int(p)]==jupiter_house  for p in bpj if p!= 'L')
    if not chk1:
        return False
    chk3 = const.house_strengths_of_planets[4][jupiter_house] > const._ENEMY #not debiliated not in enemy's house
    combustion_planets = charts.planets_in_combustion(planet_positions)
    #print('combustion_planets',combustion_planets)
    chk4 = 4 not in combustion_planets
    #print(chk1,bpj,const.natural_benefics,chk2,chk3,combustion_planets,chk4)
    return chk3 or chk4
def guru_mangala_yoga(h_to_p,p_to_h,asc_house):
    """ Guru-Mangala Yoga: If Jupiter and Mars are together or in the 7th house from each other """
    #p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    gm_yoga = p_to_h[2]==p_to_h[4] or p_to_h[2]==(p_to_h[4]+6)%12 or p_to_h[4]==(p_to_h[2]+6)%12
    return  gm_yoga
def amala_yoga(h_to_p,p_to_h,asc_house):
    """ Amala Yoga: If there are only natural benefics in the 10th house from lagna or Moon """
    #p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lh = (planet_positions[0][1][0]+9)%12
    ay = all([p in const.natural_benefics for p,h in p_to_h.items() if h==lh])
    return ay
def parvata_yoga(h_to_p,p_to_h,asc_house):    
    """ Parvata Yoga: If (1) quadrants are occupied only by benefics and (2) the 7th and 8th houses 
        are either vacant or occupied only by benefics """
    planets_in_lagnam_quadrant = [h_to_p[a] for a in quandrants_of_the_house(asc_house)]
    chk1 = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant[1:]] for nb in const.natural_benefics]
    py1 = all(any(row) for row in chk1)
    chk2 = [[h_to_p[a] =='' or (str(nb) in h_to_p[a]) for a in [(asc_house+6)%12,(asc_house+7)%12]] for nb in const.natural_benefics]
    py2 = all(any(row) for row in chk2)
    return py1 and py2
def kaahala_yoga(h_to_p,p_to_h,asc_house):
    """ Kaahala Yoga: If (1) the 4th lord and Jupiter are in mutual quadrants and (2) lagna lord is strong """
    fourth_lord = const.house_owners[(asc_house+3)%12]
    lagna_lord = const.house_owners[asc_house]
    ky1 = '4' in [h_to_p[a] for a in quandrants_of_the_house((asc_house+3)%12)]
    ky2 = const.house_strengths_of_planets[lagna_lord][asc_house] > const._NEUTRAL_SAMAM
    return ky1 and ky2
def chaamara_yoga(h_to_p,p_to_h,asc_house):
    """ Chaamara Yoga: If the lagna lord is exalted in a quadrant with Jupiter’s aspect or
        two benefics join in 7th, 9th or 10th """
    lagna_lord = const.house_owners[asc_house]
    lagna_house = p_to_h[lagna_lord]
    cy = [[(str(nb) in h_to_p[a]) for a in [(asc_house+6)%12,(asc_house+8)%12,(asc_house+9)%12]] for nb in const.natural_benefics]
    cy1 = sum(sum(cy,[])) > 1
    #""" TODO Should we change this Graha Drishti??? """
    #cy2 = const.house_strengths_of_planets[lagna_lord][lagna_house]== const._OWNER_RULER and lagna_house in house.aspected_rasis_of_the_planet(h_to_p, 4)
    cy2 = const.house_strengths_of_planets[lagna_lord][lagna_house] >= const._EXALTED_UCCHAM and str(lagna_lord) in house.graha_drishti_of_the_planet(h_to_p, 4)
    #print('cy2',const.house_strengths_of_planets[lagna_lord][lagna_house],lagna_lord,house.graha_drishti_of_the_planet(h_to_p, 4))
    return cy1 or cy2
def sankha_yoga(h_to_p,p_to_h,asc_house):
    """ Sankha Yoga: If (1) lagna lord is strong and (2) 5th and 6th lords are in mutual
        quadrants, then this yoga is present. Alternately, this yoga is present if (1) lagna lord
        and 10th lord are together in a movable sign and (2) the 9th lord is strong. """
    fifth_lord = const.house_owners[(asc_house+4)%12]
    sixth_lord = const.house_owners[(asc_house+5)%12]
    lagna_lord = const.house_owners[asc_house]
    ky1 = str(fifth_lord) in [h_to_p[a] for a in quandrants_of_the_house((asc_house+5)%12)]
    ky2 = str(sixth_lord) in [h_to_p[a] for a in quandrants_of_the_house((asc_house+4)%12)]
    ky3 = const.house_strengths_of_planets[lagna_lord][asc_house] > const._NEUTRAL_SAMAM
    ninth_lord = const.house_owners[(asc_house+8)%12]
    ky4 = const.house_strengths_of_planets[ninth_lord][p_to_h[ninth_lord]] > const._NEUTRAL_SAMAM
    ky5 = p_to_h[lagna_lord] == p_to_h[ninth_lord] and p_to_h[lagna_lord] in const.movable_signs
    return (ky1 and ky2 and ky3) or (ky4 and ky5)
def bheri_yoga(h_to_p,p_to_h,asc_house):
    """ Bheri Yoga: If (1) the 9th lord is strong and (2) 1st, 2nd, 7th and 12th houses are
        occupied by planets, then this yoga is present. Alternately, this is yoga is present if
        (1) the 9th lord is strong and (2) Jupiter, Venus and lagna lord are in mutual
        quadrants. """
    ninth_lord = const.house_owners[(asc_house+8)%12]
    by1 = const.house_strengths_of_planets[ninth_lord][p_to_h[ninth_lord]] > const._NEUTRAL_SAMAM
    by2 = all([ any([str(p_to_h[p]) in str(hp) for hp in [asc_house, (asc_house+1)%12, (asc_house+6)%12, (asc_house+11)%12]]) for p in [*range(9)] ])
    by3 = [h in quandrants_of_the_house(asc_house) for h in [p_to_h[4], p_to_h[5], asc_house]]
    return by1 and (by2 or by3)
def mridanga_yoga(h_to_p,p_to_h,asc_house):
    """ Mridanga Yoga: If (1) there are planets in own and exaltation signs in quadrants
        and trines and (2) lagna lord is strong. """
    quadrants_and_trines = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(asc_house)
    my1 = any([any([p_to_h[p]==h and const.house_strengths_of_planets[p][h]>const._FRIEND for h in quadrants_and_trines]) for p in range(9)])
    lagna_lord = const.house_owners[asc_house]
    my2 = const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return my1 and my2
def sreenaatha_yoga(h_to_p,p_to_h,asc_house):
    """ Sreenaatha Yoga: If (1) the 7th lord is exalted in 10th and (2) 10th lord is with 9th lord. """
    seventh_lord = const.house_owners[(asc_house+6)%12]
    ninth_lord = const.house_owners[(asc_house+8)%12]
    tenth_lord = const.house_owners[(asc_house+8)%12]
    sy1 = const.house_strengths_of_planets[seventh_lord][(asc_house+9)%12]>const._FRIEND
    sy2 = p_to_h[ninth_lord] == p_to_h[tenth_lord]
    return sy1 and sy2
def matsya_yoga(h_to_p,p_to_h,asc_house):
    """ Matsya Yoga: If (1) benefics are in lagna and 9th, (2) some planets are in 5th, and,
        (3) malefics are in chaturasras (4th and 8th houses). """
    ph = sum([h_to_p[h].split('/') for h in [asc_house,(asc_house+8)%12]],[])
    ph = [p for p in ph if p != '']
    my1 = ([any(str(p) in str(nb) for nb in const.natural_benefics) for p in ph])
    if not my1:
        return False
    ph = sum([h_to_p[h].split('/') for h in [(asc_house+3)%12,(asc_house+7)%12]],[])
    ph = [p for p in ph if p != '']
    my3 = ([any(str(p) in str(nb) for nb in const.natural_malefics) for p in ph])
    my2 = h_to_p[(asc_house+4)%12] != ''
    return my1 and my2 and my3
def koorma_yoga(h_to_p,p_to_h,asc_house):
    """ Koorma Yoga: If (1) the 5th, 6th and 7th houses are occupied by benefics who are in
        own, exaltation or friendly signs and (2) the 1st, 3rd and 11th houses are occupied by
        malefics who are in own or exaltation signs. """
    ph = sum([h_to_p[h].split('/') for h in [(asc_house+4)%12,(asc_house+5)%12,(asc_house+6)%12]],[])
    ph = [p for p in ph if p != '']
    my1 = ([any(str(p) in str(nb) for nb in const.natural_benefics) for p in ph])
    if not my1:
        return False
    my1 = all([const.house_strengths_of_planets[int(p)][p_to_h[int(p)]] > const._NEUTRAL_SAMAM for p in ph if p!='L'])
    ph = sum([h_to_p[h].split('/') for h in [asc_house,(asc_house+2)%12,(asc_house+10)%12]],[])
    ph = [p for p in ph if p != '']
    my2 = ([any(str(p) in str(nb) for nb in const.natural_malefics) for p in ph])
    if my2:
        my2 = all([const.house_strengths_of_planets[int(p)][p_to_h[int(p)]] > const._NEUTRAL_SAMAM for p in ph  if p!='L'])
    return my1 and my2
def khadga_yoga(h_to_p,p_to_h,asc_house):
    """ Khadga Yoga: If (1) the 2nd lord is in the 9th house, (2) the 9th lord is in the 2nd
        house, and, (3) lagna lord is in a quadrant or a trine. """
    second_lord = const.house_owners[(asc_house+1)%12]
    ninth_lord = const.house_owners[(asc_house+8)%12]
    lagna_lord = const.house_owners[asc_house]
    ky1 = (p_to_h[second_lord] == (asc_house+8)%12) and (p_to_h[ninth_lord] == (asc_house+1)%12)
    quadrants_and_trines = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(asc_house)
    ky2 = p_to_h[lagna_lord] in quadrants_and_trines
    return ky1 and ky2
def kusuma_yoga(h_to_p,p_to_h,asc_house):
    """ Kusuma Yoga: If (1) lagna is in a fixed sign, (2) Venus is in a quadrant, (3) Moon is
        in a trine with a benefic, and, (4) Saturn is in the 10th house. """
    ky1 = asc_house in const.fixed_signs
    if not ky1:
        return False
    ky2 = p_to_h[5] in quandrants_of_the_house(asc_house)
    if not ky2:
        return False
    ky4 = p_to_h[6] == (asc_house+9)%12
    if not ky4:
        return False
    ky3 = any([p_to_h[1] in house.trines_of_the_raasi(p_to_h[nb]) for  nb in const.natural_benefics])
    return ky1 and ky2 and ky3 and ky4
def kalaanidhi_yoga(h_to_p,p_to_h,asc_house):
    """ Kalaanidhi Yoga: If (1) Jupiter is in the 2nd house or the 5th house and (2) he is
        conjoined or aspected by Mercury and Venus. """
    ky1 = p_to_h[4] == (asc_house+1)%12 or p_to_h[4] == (asc_house+4)%12
    if not ky1:
        return False
    ky2 = p_to_h[4] == p_to_h[3] and p_to_h[4] == p_to_h[5]
    ky3 = all([any([str(p1) in str(p2) for p2 in house.aspected_planets_of_the_raasi(h_to_p, p_to_h[4])]) for p1 in [3,5]])
    return ky1 and (ky2 or ky3)
def kalpadruma_yoga(h_to_p,p_to_h,asc_house):
    """ Kalpadruma Yoga: Consider (1) lagna lord, (2) his dispositor, (3) the latter’s
        dispositor in rasi and (4) in navamsa. If all the four planets are all in quadrants, trines
        or exaltation signs. """
    """ UnComment this For testing 
    h_to_p_rasi = ['5','7','2','','L','1','6','8','','','4/0','3']
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    asc_house = p_to_h_rasi['L']
    h_to_p_navamsa = ['0','','5','','3','7/1','','4','L','','6/2','8']
    p_to_h_navamsa = utils.get_planet_to_house_dict_from_chart(h_to_p_navamsa)
    asc_house_navamsa = p_to_h_navamsa['L']
    #Uncomment this for testing """
    #""" Comment this for actual 
    h_to_p_rasi = h_to_p
    p_to_h_rasi = p_to_h
    # Comment this for actual """
    lagna_lord = const.house_owners[asc_house]
    depositor_1 = const.house_owners[p_to_h_rasi[lagna_lord]]
    depositor_2 = const.house_owners[p_to_h_rasi[depositor_1]]
    depositor_3 = const.house_owners[p_to_h_navamsa[depositor_1]]
    all_four_planets = [lagna_lord,depositor_1,depositor_2,depositor_3]
    ky1 = []
    quadrants_and_trines_of_rasi = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(asc_house)
    quadrants_and_trines_of_navamsa = house.quadrants_of_the_raasi(asc_house_navamsa)+house.trines_of_the_raasi(asc_house_navamsa)
    for p in all_four_planets:
        kyp = const.house_strengths_of_planets[p][p_to_h_rasi[p]] > const._FRIEND
        kyp = kyp or p_to_h_rasi[p] in quadrants_and_trines_of_rasi
        ky1.append(kyp)
    ky2 = []
    for p in all_four_planets:
        kyp = const.house_strengths_of_planets[p][p_to_h_navamsa[p]] > const._FRIEND
        kyp = kyp or p_to_h_navamsa[p] in quadrants_and_trines_of_navamsa
        ky2.append(kyp)
    return all(ky1) and all(ky2)
def lagnaadhi_yoga(h_to_p,p_to_h,asc_house):
    """ Lagnaadhi Yoga: If (1) the 7th and 8th houses from lagna are occupied by benefics
        and (2) no malefics conjoin or aspect these planets. """
    ly1 = all([any([p_to_h[nb] == h for h in [(asc_house+6)%12,(asc_house+7)%12]]) for nb in const.natural_benefics])
    if not ly1:
        return False
    ly2 = all([any([p_to_h[nb] == h for h in [(asc_house+6)%12,(asc_house+7)%12]]) for nb in const.natural_malefics])
    return ly1 and ly2 
def hari_yoga(h_to_p,p_to_h,asc_house):
    """ Hari Yoga: If benefics occupy the 2nd, 12th and 8th houses counted from the 2nd lord """
    lord_house = p_to_h[const.house_owners[(asc_house+1)%12]]
    benefic_houses = [(lord_house+1)%12,(lord_house+7)%12,(lord_house+11)%12]
    ly1 = all([any([p_to_h[nb] == h for h in benefic_houses]) for nb in const.natural_benefics])
    return ly1
def hara_yoga(h_to_p,p_to_h,asc_house):
    """ Hara Yoga: If benefics occupy the 4th, 9th and 8th houses counted from the 7th lord. """
    lord_house = p_to_h[const.house_owners[(asc_house+6)%12]]
    benefic_houses = [(lord_house+3)%12,(lord_house+8)%12,(lord_house+7)%12]
    ly1 = all([any([p_to_h[nb] == h for h in benefic_houses]) for nb in const.natural_benefics])
    return ly1
def brahma_yoga(h_to_p,p_to_h,asc_house):
    """ Brahma Yoga: If benefics occupy the 4th, 10th and 11th houses counted from lagna lord. """
    lord_house = p_to_h[const.house_owners[asc_house]]
    benefic_houses = [(lord_house+3)%12,(lord_house+9)%12,(lord_house+10)%12]
    ly1 = all([any([p_to_h[nb] == h for h in benefic_houses]) for nb in const.natural_benefics])
    """ Brahma yoga (another variation): “If (1) Jupiter is in a quadrant from
        the 9th lord, (2) Venus is in a quadrant from the 11th lord, and, (3) Mercury is in a
        quadrant from the 1st lord or 10th lord. """
    ly2 = p_to_h[4] in quandrants_of_the_house(p_to_h[const.house_owners[(asc_house+8)%12]])
    ly3 = p_to_h[5] in quandrants_of_the_house(p_to_h[const.house_owners[(asc_house+10)%12]])
    ly4_1 = p_to_h[3] in quandrants_of_the_house(p_to_h[const.house_owners[(asc_house)%12]])
    ly4_2 = p_to_h[3] in quandrants_of_the_house(p_to_h[const.house_owners[(asc_house+9)%12]])
    return ly1 or (ly2 and ly3 and (ly4_1 or ly4_1))
def vishnu_yoga(h_to_p,p_to_h,asc_house):
    """ Vishnu Yoga: If (1) the 9th and 10th lords are in the 2nd house and (2) the lord of the
        sign occupied in navamsa by the 9th lord in rasi chart is also in the 2nd house """
    p_to_h_rasi = p_to_h
    ninth_lord_in_rasi = const.house_owners[(asc_house+8)%12] 
    vy1 = p_to_h_rasi[ninth_lord_in_rasi]==(asc_house+1)%12 and p_to_h_rasi[const.house_owners[(asc_house+9)%12]]==(asc_house+1)%12
    if not vy1:
        return False
    lord_of_ninth_in_navamsa = const.house_owners[p_to_h_navamsa[ninth_lord_in_rasi]]
    vy2 = p_to_h_rasi[lord_of_ninth_in_navamsa] == (asc_house+1)%12
    return vy1 and vy2
def siva_yoga(h_to_p,p_to_h,asc_house):
    """ Siva Yoga: If (1) the 5th lord is in the 9th house, (2) the 9th lord is in the 10th house,
        and, (3) the 10th lord is in the 5th house """
    fifth_lord = const.house_owners[(asc_house+4)%12]
    ninth_lord = const.house_owners[(asc_house+8)%12]
    tenth_lord = const.house_owners[(asc_house+9)%12]
    sy = p_to_h[fifth_lord] == (asc_house+8)%12 and p_to_h[ninth_lord] == (asc_house+9)%12 and p_to_h[tenth_lord] == (asc_house+4)%12
    return sy
def trilochana_yoga(h_to_p,p_to_h,asc_house):
    """ Trilochana Yoga: If Sun, Moon and Mars are in mutual trines """
    ty = p_to_h[1] in house.trines_of_the_raasi(p_to_h[0]) and p_to_h[2] in house.trines_of_the_raasi(p_to_h[0])
    return ty
def gouri_yoga(h_to_p,p_to_h,asc_house):
    """ Gouri Yoga: If the lord of the sign occupied in navamsa by the 10th lord is exalted in
        the 10th house and lagna lord joins him """
    navamsa_lord = const.house_owners[asc_house_navamsa]
    rasi_lord = const.house_owners[asc_house]
    gy = p_to_h[rasi_lord] == (asc_house+9)%12 and p_to_h[navamsa_lord] == (asc_house+9)%12 and const.house_strengths_of_planets[navamsa_lord][(asc_house+9)%12] > const._FRIEND 
    return gy
def chandikaa_yoga(h_to_p,p_to_h,asc_house):
    """ Chandikaa Yoga: If (1) lagna is in a fixed sign aspected by 6th lord and (2) Sun
        joins the lords of the signs occupied in navamsa by 6th and 9th lords """
    sixth_lord = const.house_owners[(asc_house+5)%12]
    ninth_lord = const.house_owners[(asc_house+8)%12]
    lagna_lord = const.house_owners[asc_house]
    #""" TODO Should we change this Graha Drishti??? """
    #cy1 = asc_house in const.fixed_signs and asc_house in house.aspected_rasis_of_the_planet(h_to_p, sixth_lord)
    cy1 = asc_house in const.fixed_signs and str(lagna_lord) in house.graha_drishti_of_the_planet(h_to_p, sixth_lord)
    #print('cy1',asc_house,const.fixed_signs,str(lagna_lord),house.graha_drishti_of_the_planet(h_to_p, sixth_lord))
    sixth_lord_owner_in_navamsa = const.house_owners[p_to_h_navamsa[sixth_lord]]
    ninth_lord_owner_in_navamsa = const.house_owners[p_to_h_navamsa[ninth_lord]]
    cy2 = p_to_h[0] == p_to_h[sixth_lord_owner_in_navamsa] and p_to_h[0] == p_to_h[ninth_lord_owner_in_navamsa]
    return cy1 and cy2
def lakshmi_yoga(h_to_p,p_to_h,asc_house):
    """ Lakshmi Yoga: If (1) the 9th lord is in an own sign or in his exaltation sign that
        happens to be quadrant from lagna and (2) lagna lord is strong """
    ninth_lord = const.house_owners[(asc_house+8)%12]
    lagna_lord = const.house_owners[asc_house]
    ly1 = const.house_strengths_of_planets[ninth_lord][p_to_h[ninth_lord]] > const._FRIEND and p_to_h[ninth_lord] in house.quadrants_of_the_raasi(asc_house)
    ly2 =  const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return ly1 and ly2
def saarada_yoga(h_to_p,p_to_h,asc_house):
    """ Saarada Yoga: If (1) the 10th lord is in the 5th house, (2) Mercury is in a quadrant,
        (3) Sun is strong in Leo, (4) Mercury or Jupiter is in a trine from Moon, and, (5)
        Mars is in 11th, """
    sy1 = p_to_h[const.house_owners[(asc_house+9)%12]]==(asc_house+4)%12
    if not sy1:
        return False
    sy2 = p_to_h[3] in quandrants_of_the_house(asc_house)
    if not sy2:
        return False
    sy3 = p_to_h[0]==4 and const.house_strengths_of_planets[0][4] > const._FRIEND
    if not sy3:
        return False
    sy4 = [any([str(h) in str(t) for t in house.trines_of_the_raasi(p_to_h[1])]) for h in [p_to_h[3],p_to_h[4]]]
    if not sy4:
        return False
    sy5 = p_to_h[2]==(asc_house+10)%12
def bhaarathi_yoga(h_to_p,p_to_h,asc_house):
    """ Bhaarathi Yoga: If the lord of the sign occupied in navamsa by 2nd, 5th or 11th lord
        exalted and joins the 9th lord """
    second_lord = const.house_owners[(asc_house+1)%12]
    fifth_lord = const.house_owners[(asc_house+4)%12]
    eleventh_lord = const.house_owners[(asc_house+10)%12]
    ninth_lord = const.house_owners[(asc_house+8)%12]
    navamsa_lords = [const.house_owners[p_to_h_navamsa[second_lord]],const.house_owners[p_to_h_navamsa[fifth_lord]],
                     const.house_owners[p_to_h_navamsa[eleventh_lord]]]
    by1 = [p_to_h[ninth_lord] == p_to_h[nl] and const.house_strengths_of_planets[nl][p_to_h[ninth_lord]] > const._FRIEND for nl in navamsa_lords]
    return by1
def saraswathi_yoga(h_to_p,p_to_h,asc_house):
    """ Saraswathi Yoga: If (1) each of Mercury, Jupiter and Venus occupies a quadrant or
        a trine or the 2nd house (not necessarily together) and (2) Jupiter is in an own or
        friendly or exaltation sign """
    quadrants_and_trines = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(p_to_h[3])
    sy1 = all([any([str(p) in str(qt) for qt in [(asc_house+1)%12]+quadrants_and_trines]) for p in [3,4,5]])
    if not sy1:
        return False
    sy2 = const.house_strengths_of_planets[4][p_to_h[4]] > const._NEUTRAL_SAMAM
    return sy1 and sy2
def amsaavatara_yoga(h_to_p,p_to_h,asc_house):
    """ Amsaavatara Yoga: If Jupiter, Venus and exalted Saturn are in quadrants """
    ay1 = all([any([str(p) in str(q) for q in house.quadrants_of_the_raasi(p_to_h[4])]) for p in [4,5,6]])
    ay2 = const.house_strengths_of_planets[6][p_to_h[6]] > const._FRIEND
    return ay1 and ay2
def devendra_yoga(h_to_p,p_to_h,asc_house):
    """ Devendra Yoga: If (1) lagna is in a fixed sign, (2) 2nd and 10th lords have an
        exchange, and, (3) lagna and 11th lords have an exchange """
    dy1 = asc_house in const.fixed_signs
    if not dy1:
        return False
    dy2 = p_to_h[const.house_owners[(asc_house+1)%12]] == (asc_house+9)%12 and p_to_h[const.house_owners[(asc_house+9)%12]] == (asc_house+1)%12
    if not dy2:
        return False
    dy3 = p_to_h[const.house_owners[asc_house]] == (asc_house+10)%12 and p_to_h[const.house_owners[(asc_house+10)%12]] == asc_house
    return dy1 and dy2 and dy3
def indra_yoga(h_to_p,p_to_h,asc_house):
    """ Indra Yoga: If (1) the 5th and 11th lords have an exchange and (2) Moon occupies
        the 5th house """
    iy1 = p_to_h[1]==(asc_house+4)%12
    if not iy1:
        return False
    iy2 = p_to_h[const.house_owners[(asc_house+4)%12]] == (asc_house+10)%12 and p_to_h[const.house_owners[(asc_house+10)%12]] == (asc_house+4)%12
    return iy1 and iy2
def ravi_yoga(h_to_p,p_to_h,asc_house):
    """ Ravi Yoga: If (1) Sun is in the 10th house and (2) the 10th lord is in the 3rd housewith Saturn """
    ry1 = p_to_h[0] == (asc_house+9)%12
    if not ry1:
        return False
    ry2 = p_to_h[const.house_owners[(asc_house+9)%12]] == (asc_house+2)%12 and p_to_h[6] == (asc_house+2)%12
    return ry1 and ry2 
def bhaaskara_yoga(h_to_p,p_to_h,asc_house):
    """ Bhaaskara Yoga: If (1) Moon is in the 12th from Sun, (2) Mercury is in the 2nd from
        Sun, and, (3) Jupiter is in the 5th or 9th from Moon. """
    by1 = p_to_h[1] == (p_to_h[0]+11)%12
    if not by1:
        return False
    by2 = p_to_h[3] == (p_to_h[0]+1)%12
    if not by2:
        return False
    by3 = (p_to_h[4] == (p_to_h[1]+4)%12) or (p_to_h[4] == (p_to_h[1]+8)%12)
    return by1 and by2 and by3
def kulavardhana_yoga(h_to_p,p_to_h,asc_house):
    """ Kulavardhana Yoga: If each planet occupies the 5th house from either lagna or Moon or Sun """
    ky = all([ p_to_h[p]==(p_to_h['L']+4)%12 or p_to_h[p]==(p_to_h[0]+4)%12 or p_to_h[p]==(p_to_h[1]+4)%12 for p in [*range(2,9)] ])
    return ky
def vasumati_yoga(h_to_p,p_to_h,asc_house):
    """ Vasumati Yoga: benefics occupy upachayas """
    vy = str(p_to_h[6]) in house.upachayas_of_the_raasi(p_to_h[5]) or p_to_h[5] in house.upachayas_of_the_raasi(p_to_h[6])
    return vy
def gandharva_yoga(h_to_p,p_to_h,asc_house):
    """ Gandharva Yoga: If (1) the 10th lord is in a trine from the 7th house, (2) lagna lord
        is conjoined or aspected by Jupiter, (3) Sun is exalted and strong, and, (4) Moon is in
        the 9th house """
    lagna_lord = const.house_owners[asc_house]
    gy1 = p_to_h[const.house_owners[(asc_house+9)%12]] in house.trines_of_the_raasi((asc_house+6)%12)
    if not gy1:
        return False
    #""" TODO Should we change this Graha Drishti??? """
    #gy2 = p_to_h[lagna_lord] == p_to_h[4] or p_to_h[lagna_lord] in house.aspected_rasis_of_the_planet(h_to_p, 4)
    gy2 = p_to_h[lagna_lord] == p_to_h[4] or str(lagna_lord) in house.graha_drishti_of_the_planet(h_to_p, 4)
    #print('gy2',p_to_h[lagna_lord],p_to_h[4],str(lagna_lord),house.graha_drishti_of_the_planet(h_to_p, 4))
    if not gy2:
        return False
    gy3 = const.house_strengths_of_planets[0][p_to_h[0]] > const._FRIEND
    if not gy3:
        return False
    gy4 = p_to_h[1] == (asc_house+8)%12
    return gy1 and gy2 and gy3 and gy4
def go_yoga(h_to_p,p_to_h,asc_house):
    """ Go Yoga: If (1) Jupiter is strong in his moolatrikona, (2) the lord of the 2nd house is
        with Jupiter, and, (3) lagna lord is exalted """
    gy1 = const.house_strengths_of_planets[4][const.moola_trikona_of_planets[4]] > const._FRIEND
    if not gy1:
        return False
    gy2 = p_to_h[4] == p_to_h[const.house_owners[(asc_house+1)%12]]
    if not gy2:
        return False
    lagna_lord = const.house_owners[asc_house]
    gy3 = const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return gy1 and gy2 and gy3
def vidyut_yoga(h_to_p,p_to_h,asc_house):
    """ Vidyut Yoga: If (1) the 11th lord is in deep exaltation, (2) he joins Venus, and, (3)
        the two of them are in a quadrant from lagna lord """
    eleventh_lord = const.house_owners[(asc_house+10)%12]
    lagna_lord = const.house_owners[asc_house]
    vy1 = const.house_strengths_of_planets[eleventh_lord][p_to_h[eleventh_lord]] > const._FRIEND
    if not vy1:
        return False
    vy2 = p_to_h[eleventh_lord] == p_to_h[5]
    if not vy2:
        return False
    vy3 = p_to_h[eleventh_lord] in house.quadrants_of_the_raasi(p_to_h[lagna_lord])
    return vy1 and vy2 and vy3
def chapa_yoga(h_to_p,p_to_h,asc_house):
    """ Chapa Yoga: If (1) the 4th and 10th lords have an exchange and (2) lagna lord is exalted. """
    cy1 = p_to_h[const.house_owners[(asc_house+3)%12]] == (asc_house+9)%12 and p_to_h[const.house_owners[(asc_house+9)%12]] == (asc_house+3)%12
    lagna_lord = const.house_owners[asc_house]
    cy2 = const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return cy1 and cy2
def pushkala_yoga(h_to_p,p_to_h,asc_house):
    """ Pushkala Yoga: If (1) lagna lord is with Moon, (2) dispositor of Moon is in a
        quadrant or in the house of an adhimitra (good friend), (2) dispositor of Moon
        aspects lagna, and, (4) there is a planet in lagna """
    moon_house = p_to_h[1]
    lagna_lord = const.house_owners[asc_house]
    py1 = p_to_h[lagna_lord] == moon_house
    dispositor_of_moon = const.house_owners[moon_house]
    dispositor_house = p_to_h[dispositor_of_moon]
    dispositor_quadrants = house.quadrants_of_the_raasi(dispositor_house)
    py2_1 = dispositor_house in house.strong_signs_of_planet(dispositor_of_moon)
    py2_2 = dispositor_house in dispositor_quadrants
    py2_3 = dispositor_of_moon in house.aspected_planets_of_the_raasi(h_to_p,asc_house)
    py3 =len([h for h in h_to_p[p_to_h['L']].split('/') if h!= '']) > 1
    return py1 and (py2_1 or py2_2) and py2_3 and py3
def makuta_yoga(h_to_p,p_to_h,asc_house):
    """ Makuta Yoga: If (1) Jupiter is in the 9th house from the 9th lord, (2) the 9th house
        from Jupiter has a benefic, and, (3) Saturn is in the 10th house """
    my1 = p_to_h[4] == (p_to_h[const.house_owners[(asc_house+8)%12]]+8)%12
    my2 = any([np in ['5','6'] for np in h_to_p[(asc_house+8)%12].split('/') if np !='L' and np!=''])
    my3 = p_to_h[6] == (asc_house+9)%12
    return my1 and my2 and my3
def jaya_yoga(h_to_p,p_to_h,asc_house):
    """ Jaya Yoga: If (1) the 10th lord is in deep exaltation and (2) the 6th lord is debilitated """
    tenth_lord = const.house_owners[(asc_house+9)%12]
    jy1 = const.house_strengths_of_planets[tenth_lord][p_to_h[tenth_lord]] == const._EXALTED_UCCHAM
    sixth_lord = const.house_owners[(asc_house+5)%12]
    jy2 = const.house_strengths_of_planets[sixth_lord][p_to_h[sixth_lord]] == const._DEFIBILATED_NEECHAM
    return jy1 and jy2
def harsha_yoga(h_to_p,p_to_h,asc_house):
    """ Harsha Yoga: If the 6th lord occupies the 6th house """
    return p_to_h[const.house_owners[(asc_house+5)%12]] == (asc_house+5)%12
def sarala_yoga(h_to_p,p_to_h,asc_house):
    """ Sarala Yoga: If the 8th lord occupies the 8th house """
    return p_to_h[const.house_owners[(asc_house+7)%12]] == (asc_house+7)%12
def vimala_yoga(h_to_p,p_to_h,asc_house):
    """ Vimala Yoga: If the 12th lord occupies the 12th house """
    return p_to_h[const.house_owners[(asc_house+11)%12]] == (asc_house+11)%12
if __name__ == "__main__":
    place = panchanga.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    dob = panchanga.Date(1996,12,7)
    tob = (10,34,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd = swe.julday(dob.year,dob.month,dob.day, time_of_birth_in_hours)
    divisional_chart_factor = 1
    lang = 'en'
    msgs = get_yoga_resources(language=lang)
    ascendant_index = 'L'
    planet_positions = panchanga.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = panchanga.ascendant(jd,place)[1]
    asc_house,asc_long = panchanga.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions = [[ascendant_index,(asc_house,asc_long)]] + planet_positions
    #print(planet_positions)
    p_to_h = { p:h for p,(h,_) in planet_positions}
    h_to_p = ['' for h in range(12)] 
    for sublist in planet_positions:
        p = sublist[0]
        h = sublist[1][0]
        h_to_p[h] += str(p) + '/'
    ascendant_index = 'L'
    planet_positions_navamsa = panchanga.dhasavarga(jd,place,sign_division_factor=9)
    ascendant_longitude = panchanga.ascendant(jd,place)[1]
    asc_house_navamsa,asc_long = panchanga.dasavarga_from_long(ascendant_longitude,sign_division_factor=9)
    planet_positions_navamsa += [[ascendant_index,(asc_house,asc_long)]]
    p_to_h_navamsa = { p:h for p,(h,_) in planet_positions_navamsa}
    h_to_p_navamsa = ['' for h in range(12)] 
    for sublist in planet_positions_navamsa:
        p = sublist[0]
        h = sublist[1][0]
        h_to_p_navamsa[h] += str(p) + '/'
    print('planet_positions',planet_positions)
    print('p_to_h',p_to_h)
    print('h_to_p',h_to_p)
    my = chaamara_yoga(h_to_p, p_to_h, asc_house)
    print('chaamara_yoga',my)
    my = gandharva_yoga(h_to_p, p_to_h, asc_house)
    print('gandharva_yoga',my)
    exit()
    print('language',lang)
    yrc = get_yoga_details(jd,place,divisional_chart_factor=1,language=lang)
    #yrc = get_yoga_details_for_all_charts(jd,place,lang)
    print(yrc)
    exit()
    gaja_kesari_yoga(planet_positions)
    exit()
    print('natural benefics',const.natural_benefics)
    print(asubha_yoga(h_to_p,p_to_h,asc_house))
    #exit()
    divisional_chart_factor = 1
    yoga_results = get_yoga_details(jd,place,divisional_chart_factor=divisional_chart_factor)
    #print(yoga_results)
    #exit()
    print(yogas_present)