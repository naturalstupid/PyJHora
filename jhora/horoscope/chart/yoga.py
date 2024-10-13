import json
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house
_lang_path = const._LANGUAGE_PATH

movable_signs = const.movable_signs
fixed_signs = const.fixed_signs
dual_signs = const.dual_signs
seven_planets = [*range(7)] # Rahu and Ketu are excluded
all_planets = [*range(9)]

division_chart_factors = const.division_chart_factors
quadrants_of_the_house = lambda raasi: house.quadrants_of_the_raasi(raasi) 
#h_to_p = lambda pp,h: utils.get_house_planet_list_from_planet_positions(pp)[h]
#p_to_h = lambda pp,p: utils.get_planet_house_dictionary_from_planet_positions(pp)[p]
def get_yoga_resources(language='en'):
    """
        get yoga names from yoga_msgs_<lang>.txt
        @param language: Two letter language code. en, hi, ka, ta, te
        @return json strings from the resource file as dictionary 
    """
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
    global p_to_h_navamsa, h_to_p_navamsa, asc_house_navamsa,planet_positions
    msgs = get_yoga_resources(language=language)
    yoga_results_combined = {}
    ascendant_index = const._ascendant_symbol
    planet_positions_navamsa = drik.dhasavarga(jd,place,divisional_chart_factor=9)
    ascendant_longitude = drik.ascendant(jd,place)[1]
    asc_house_navamsa,asc_long = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor=9)
    planet_positions_navamsa += [[ascendant_index,(asc_house_navamsa,asc_long)]]
    p_to_h_navamsa = utils.get_planet_house_dictionary_from_planet_positions(planet_positions_navamsa)
    h_to_p_navamsa = utils.get_house_planet_list_from_planet_positions(planet_positions_navamsa)
    for dv in division_chart_factors:
        yoga_results,_,_ = get_yoga_details(jd,place,divisional_chart_factor=dv,language=language)
        yoga_results.update(yoga_results_combined)
        yoga_results_combined = yoga_results
    #print('Found',len(yoga_results_combined),'out of',len(msgs)*len(division_chart_factors),'yogas')
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
    ascendant_index = const._ascendant_symbol
    planet_positions = drik.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = drik.ascendant(jd,place)[1]
    asc_house,asc_long = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[ascendant_index,(asc_house,asc_long)]]
    p_to_h = { p:h for p,(h,_) in planet_positions}
    h_to_p = ['' for h in range(12)] 
    for sublist in planet_positions:
        p = sublist[0]
        h = sublist[1][0]
        h_to_p[h] += str(p) + '/'
    yoga_results = {}
    for yoga_function,details in msgs.items():
        """ TODO: yoga functions have only one argument h_to_p. Here we call 3 args - need to synch"""
        yoga_exists = eval(yoga_function+'_from_planet_positions')(planet_positions)#(h_to_p)#
        if yoga_exists:
            details.insert(0,'D'+str(divisional_chart_factor))
            yoga_results[yoga_function] = details
    #print('Found',len(yoga_results),'out of',len(msgs),'yogas in D'+str(divisional_chart_factor),'chart')
    return yoga_results,len(yoga_results),len(msgs)
""" Sun Yogas """
def vesi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vesi Yoga - There is a planet other than Moon in the 2nd house from Sun. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    yoga_house = (p_to_h[0]+1)%12
    yoga_house_planets = h_to_p[yoga_house].split('/')
    yp = str(1) not in yoga_house_planets and ((len(yoga_house_planets) == 1 and const._ascendant_symbol not in yoga_house_planets) or len(yoga_house_planets) > 1)
    return yp
def vosi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vosi Yoga - There is a planet other than Moon in the 12th house from Sun. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    yoga_house = (p_to_h[0]+11)%12
    yoga_house_planets = h_to_p[yoga_house].split('/')
    yp = str(1) not in yoga_house_planets and ((len(yoga_house_planets) == 1 and const._ascendant_symbol not in yoga_house_planets) or len(yoga_house_planets) > 1)
    return yp
def ubhayachara_yoga_from_planet_positions(planet_positions):
    """ Ubhayachara  Yoga - There is a planet other than Moon in the 2nd and 12th house from Sun. """
    yp = vesi_yoga_from_planet_positions(planet_positions) and vosi_yoga_from_planet_positions(planet_positions)
    return yp
def nipuna_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Budha-Aaditya Yoga (Nipuna Yoga)- If Sun and Mercury are together (in one sign), this yoga is present."""
    nipuna_yoga = any(['0' in p and '3' in p for p in h_to_p])
    return nipuna_yoga
budha_aaditya_yoga_from_planet_positions = lambda planet_positions:nipuna_yoga_from_planet_positions(planet_positions)
def sunaphaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sunaphaa Yoga - There are planets other than Sun in the 2nd house from Moon"""
    from_planet = 1
    from_house = 2
    other_than_planet = 0
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    yoga_house = (p_to_h[from_planet]+from_house-1)%12
    yoga_house_planets = h_to_p[yoga_house].split('/')
    yp = str(other_than_planet) not in yoga_house_planets and ((len(yoga_house_planets) == 1 and const._ascendant_symbol not in yoga_house_planets) or len(yoga_house_planets) > 1)
    return yp
def anaphaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Anaphaa Yoga - There are planets other than Sun in the 12th house from Moon"""
    from_planet = 1
    from_house = 12
    other_than_planet = 0
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    yoga_house = (p_to_h[from_planet]+from_house-1)%12
    yoga_house_planets = h_to_p[yoga_house].split('/')
    yp = str(other_than_planet) not in yoga_house_planets and ((len(yoga_house_planets) == 1 and const._ascendant_symbol not in yoga_house_planets) or len(yoga_house_planets) > 1)
    return yp
def duradhara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Duradhara Yoga - There is a planet other than Sun in the 2nd and 12th house from Moon. """
    return sunaphaa_yoga_from_planet_positions(planet_positions) and anaphaa_yoga_from_planet_positions(planet_positions)
def kemadruma_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kemadruma Yoga - there are no planets other than Sun in the 1st, 2nd and 12th houses from
        Moon and if there are no planets other than Moon in the quadrants from lagna"""
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print(h_to_p,p_to_h)
    moon_house = p_to_h[1]
    houses_from_moon = [((h+moon_house-1)%12) for h in [1,2,12]]
    #print(moon_house,houses_from_moon)
    planets_from_moon = [p for h in houses_from_moon for p,h1 in p_to_h.items() if h==h1]
    #print(planets_from_moon)
    ky1 = all([p not in planets_from_moon for p in range(2,9)])
    #print(ky1)
    quadrants_from_lagna = house.quadrants_of_the_raasi(p_to_h[const._ascendant_symbol])
    #print(quadrants_from_lagna)
    planets_from_quadrants_of_lagna = [p for h in quadrants_from_lagna for p,h1 in p_to_h.items() if h==h1]
    #print(planets_from_quadrants_of_lagna)
    ky2 = all([p not in planets_from_quadrants_of_lagna for p in range(2,9)])
    #print(ky2)
    return ky1 and ky2
def chandra_mangala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chandra-Mangala Yoga - Moon and Mars are together (in one sign). """
    chandra_mangala_yoga = any(['1' in p and '2' in p for p in h_to_p])
    return chandra_mangala_yoga
def adhi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Adhi Yoga - natural benefics occupy 6th, 7th and 8th from Moon, """
    # AND is used to check ALL NATURAL BENEFICS are in 6 or 7 or 8 from moon
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    adhi_yoga_1 = any('4' in x or '5' in x for x in [h_to_p[(p_to_h[1]+mh-1)%12] for mh in [6,7,8] ])
    #Mercury (3) benefic if alone.
    adhi_yoga_2 = any(x=='3' for x in [h_to_p[(p_to_h[1]+mh-1)%12] for mh in [6,7,8] ])
    adhi_yoga = adhi_yoga_1 or adhi_yoga_2
    return adhi_yoga
def ruchaka_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """  Ruchaka Yoga - Mars should be in 0 or 7 or 9th rasi and he should be in 1, 4, 7 or 10th from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    ruchaka_yoga_1 = any('2' in x for x in [h_to_p[y] for y in [0,7,9]])
    ruchaka_yoga_2 = any('2' in x for x in [h_to_p[(p_to_h[const._ascendant_symbol]+mh-1)%12] for mh in [1,4,7,10] ])
    ruchaka_yoga = ruchaka_yoga_1 and ruchaka_yoga_2
    return ruchaka_yoga
def bhadra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Bhadra Yoga - Mercury should be in Ge or Vi and he should be in 1st, 4th, 7th or 10th from lagna. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    bhadra_yoga_1 = any('3' in x for x in [h_to_p[y] for y in [2,5]])
    bhadra_yoga_2 = any('3' in x for x in [h_to_p[(p_to_h[const._ascendant_symbol]+mh-1)%12] for mh in [1,4,7,10] ])
    bhadra_yoga = bhadra_yoga_1 and bhadra_yoga_2
    return bhadra_yoga
def sasa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Saturn should be in Cp, Aq or Li and he should be in 1st, 4th, 7th or 10th from lagna. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    sasa_yoga_1 = any('6' in x for x in [h_to_p[y] for y in [6,9,10]])
    sasa_yoga_2 = any('6' in x for x in [h_to_p[(p_to_h[const._ascendant_symbol]+mh-1)%12] for mh in [1,4,7,10] ])
    sasa_yoga = sasa_yoga_1 and sasa_yoga_2
    return sasa_yoga
def maalavya_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Maalavya Yoga - Venus should be in Ta, Li or Pi and he should be in 1st, 4th, 7th or 10th from lagna. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    maalavya_yoga_1 = any('5' in x for x in [h_to_p[y] for y in [1,6,11]])
    maalavya_yoga_2 = any('5' in x for x in [h_to_p[(p_to_h[const._ascendant_symbol]+mh-1)%12] for mh in [1,4,7,10] ])
    maalavya_yoga = maalavya_yoga_1 and maalavya_yoga_2
    return maalavya_yoga
def hamsa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Hamsa Yoga - Jupiter should be in Sg, Pi or Cn and he should be in 1st, 4th, 7th or 10th from lagna. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    hamsa_yoga_1 = any('4' in x for x in [h_to_p[y] for y in [8,9,11]])
    hamsa_yoga_2 = any('4' in x for x in [h_to_p[(p_to_h[const._ascendant_symbol]+mh-1)%12] for mh in [1,4,7,10] ])
    hamsa_yoga = hamsa_yoga_1 and hamsa_yoga_2
    return hamsa_yoga
def rajju_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Rajju Yoga: all the planets are exclusively in movable signs """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    rajju_yoga = all(p_to_h[p] in movable_signs for p in range(9))
    return rajju_yoga
def musala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Musala Yoga: all the planets are exclusively in fixed signs """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    musala_yoga = all(p_to_h[p] in fixed_signs for p in range(9))
    return musala_yoga
def nala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Nala Yoga: all the planets are exclusively in dual signs, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    nala_yoga = all(p_to_h[p] in dual_signs for p in range(9))
    return nala_yoga
def maalaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Maalaa Yoga: If three quadrants from Lagna are occupied by natural benefics, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    planets_in_lagnam_quadrant = [h_to_p[a].split('/') for a in quadrants_of_the_house(p_to_h[const._ascendant_symbol])]
    chk = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant] for nb in const.natural_benefics]
    maalaa_yoga = all(any(row) for row in chk)
    return maalaa_yoga
def sarpa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sarpa Yoga: If three quadrants from lagna are occupied by natural malefics, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    planets_in_lagnam_quadrant = [h_to_p[a].split('/') for a in quadrants_of_the_house(p_to_h[const._ascendant_symbol])]
    #print('planets_in_lagnam_quadrant',planets_in_lagnam_quadrant,'const.natural_malefics',const.natural_malefics)
    chk = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant] for nb in const.natural_malefics]
    #print('chk',chk,)
    sarpa_yoga = sum([sum(x) for x in chk]) >2 #all(any(row) for row in chk)
    return sarpa_yoga
def gadaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Gadaa Yoga: all the planets occupy two successive quadrants from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    slq = [tuple(sorted(((asc_house)%12, (asc_house+3)%12))), tuple(sorted(((asc_house+3)%12,(asc_house+6)%12))),
            tuple(sorted(((asc_house+6)%12,(asc_house+9)%12))),tuple(sorted(((asc_house+9)%12,asc_house%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    gadaa_yoga = sph in slq
    return gadaa_yoga
def sakata_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sakata Yoga: If all the planets occupy 1st and 7th houses from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    slq = slq = [tuple(sorted(((asc_house)%12, (asc_house+6)%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    sakata_yoga = sph in slq
    return sakata_yoga
def vihanga_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vihanga Yoga: If all the planets occupy 4th and 10th houses from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    slq = [tuple(sorted(((asc_house+3)%12, (asc_house+9)%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    vihanga_yoga = sph in slq
    return vihanga_yoga
def sringaataka_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sringaataka Yoga: If all the planets occupy trines (1st, 5th and 9th) from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    slq = [tuple(sorted(((asc_house)%12, (asc_house+4)%12, (asc_house+8)%12)))]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    sringaataka_yoga = sph in slq
    return sringaataka_yoga
def hala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Hala Yoga: If all the planets occupy mutual trines but not trines from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    slq = [tuple(sorted(((asc_house+1)%12, (asc_house+5)%12, (asc_house+9)%12))),
        tuple(sorted(((asc_house+2)%12, (asc_house+6)%12, (asc_house+10)%12))),
        tuple(sorted(((asc_house+3)%12, (asc_house+7)%12, (asc_house+11)%12)))
        ]
    sph = tuple(sorted(set(list(p_to_h.values())[:-1])))
    hala_yoga = sph in slq
    return hala_yoga
def vajra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vajra Yoga: If lagna and the 7th houses are occupied by natural benefics and the 4th
        and 10th houses are occupied by natural malefics """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    chk1 = [[str(nb) in h_to_p[a] for a in [asc_house%12,(asc_house+6)%12 ]] for nb in const.natural_benefics]
    vajra_yoga_1 = sum([sum(x) for x in chk1]) > 1 #all(any(row) for row in chk1)
    chk2 = [[str(nb) in h_to_p[a] for a in [(asc_house+3)%12,(asc_house+9)%12 ]] for nb in const.natural_malefics]
    vajra_yoga_2 = sum([sum(x) for x in chk2]) > 1 #all(any(row) for row in chk2)
    vajra_yoga = vajra_yoga_1 and vajra_yoga_2
    return vajra_yoga
def yava_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Yava Yoga: If lagna and the 7th houses are occupied by natural malefics and the 4th
        and 10th houses are occupied by natural benefics, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    chk1 = [[str(nb) in h_to_p[a] for a in [asc_house%12,(asc_house+6)%12 ]] for nb in const.natural_malefics]
    chk2 = [[str(nb) in h_to_p[a] for a in [(asc_house+3)%12,(asc_house+9)%12 ]] for nb in const.natural_benefics]
    yava_yoga_1 = sum([sum(x) for x in chk1]) > 1 #all(any(row) for row in chk1)
    yava_yoga_2 = sum([sum(x) for x in chk2]) > 1 #all(any(row) for row in chk2)
    yava_yoga = yava_yoga_1 and yava_yoga_2
    return yava_yoga
def kamala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kamala Yoga: If all the planets are in quadrants from lagna, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    planets_in_lagnam_quadrant = [h_to_p[a] for a in quadrants_of_the_house(asc_house)]
    chk = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant] for nb in all_planets]
    kamala_yoga = all(any(row) for row in chk)
    return kamala_yoga
def vaapi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vaapi Yoga: If all the planets are panaparas or in apoklimas """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    panapharas_planets = [h_to_p[h] for h in [(asc_house+1)%12,(asc_house+4)%12,(asc_house+7)%12,(asc_house+10)%12]]
    apoklimas_planets = [h_to_p[h] for h in [(asc_house+2)%12,(asc_house+5)%12,(asc_house+8)%12,(asc_house+11)%12]]
    chk1 = [[str(nb) in str(pl) for pl in panapharas_planets] for nb in all_planets]
    chk2 = [[str(nb) in str(pl) for pl in apoklimas_planets] for nb in all_planets]
    vaapi_yoga = all(any(row) for row in chk1) or all(any(row) for row in chk2)
    return vaapi_yoga
def yoopa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Yoopa Yoga: all the planets are in 1st, 2nd, 3rd and 4th houses from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house)%12,(asc_house+1)%12,(asc_house+2)%12,(asc_house+3)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    yoopa_yoga = all(any(row) for row in chk)
    return yoopa_yoga
def sara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sara Yoga: all the planets are in 4th, 5th, 6th and 7th houses from lagna, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+3)%12,(asc_house+4)%12,(asc_house+5)%12,(asc_house+6)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    sara_yoga = all(any(row) for row in chk)
    return sara_yoga
def sakti_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sakti Yoga: If all the planets are in 7th, 8th, 9th and 10th houses from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+6)%12,(asc_house+7)%12,(asc_house+8)%12,(asc_house+9)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    sakti_yoga = all(any(row) for row in chk)
    return sakti_yoga
def danda_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Danda Yoga: If all the planets are in 10th, 11th, 12th and 1st houses from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+9)%12,(asc_house+10)%12,(asc_house+11)%12,(asc_house+12)%12]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    danda_yoga = all(any(row) for row in chk)
    return danda_yoga
def naukaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Naukaa Yoga: If all the planets occupy the 7 signs from lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    naukaa_yoga = all(any(row) for row in chk)
    return naukaa_yoga
def koota_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Koota Yoga: If all the planets occupy the 7 signs from the 4th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+3+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    koota_yoga = all(any(row) for row in chk)
    return koota_yoga
def chatra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chatra Yoga: If all the planets occupy the 7 signs from the 7th house, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+6+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    chatra_yoga = all(any(row) for row in chk)
    return chatra_yoga
def chaapa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chaapa Yoga: If all the planets occupy the 7 signs from the 10th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house+9+i)%12 for i in range(7)]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    chaapa_yoga = all(any(row) for row in chk)
    return chaapa_yoga
def ardha_chandra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Ardha Chandra Yoga: If all the planets occupy the 7 signs starting from a panapara or an apoklima """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
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
def chakra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chakra Yoga: If all the planets occupy 1st, 3rd, 5th, 7th, 9th and 11th houses """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house-1+i)%12 for i in [1,3,5,7,9,11]]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    chakra_yoga = all(any(row) for row in chk)
    return chakra_yoga
def samudra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Samudra Yoga: If all the planets occupy 2nd, 4th, 6th, 8th, 10th and 12th houses """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    spl = [h_to_p[h] for h in [(asc_house-1+i)%12 for i in [2,4,6,8,10,12]]]
    chk = [[str(nb) in str(pl) for pl in spl] for nb in all_planets]
    samudra_yoga = all(any(row) for row in chk)
    return samudra_yoga
def veenaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Veenaa Yoga: If the seven planets occupy exactly 7 distinct signs among them """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    veenaa_yoga = len(chk) == 7
    return veenaa_yoga
def daama_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Daama Yoga: If the seven planets occupy exactly 6 distinct signs among them """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    daama_yoga = len(chk) == 6
    return daama_yoga
def paasa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Paasa Yoga: If the seven planets occupy exactly 5 distinct signs among them """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    paasa_yoga = len(chk) == 5
    return paasa_yoga
def kedaara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kedaara Yoga: If the seven planets occupy exactly 4 distinct signs among them """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    kedaara_yoga = len(chk) == 4
    return kedaara_yoga
def soola_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Soola Yoga: If the seven planets occupy exactly 3 distinct signs among them """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    soola_yoga = len(chk) == 3
    return soola_yoga
def yuga_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Yuga Yoga: If the seven planets occupy exactly 2 distinct signs among them """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    yuga_yoga = len(chk) == 2
    return yuga_yoga
def gola_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Gola Yoga: If the seven planets are in one sign """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    chk = set([p_to_h[p] for p in seven_planets])
    gola_yoga = len(chk) == 1
    return gola_yoga
def subha_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Subha Yoga: If lagna has benefics or has “subha kartari – benefics in 12th and 2nd """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    chk = [[str(nb) in h_to_p[a] for a in [(asc_house)%12,(asc_house+1)%12,(asc_house+11)%12 ]] for nb in const.natural_benefics]
    subha_yoga = any(any(row) for row in chk)
    return subha_yoga
def asubha_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Asubha Yoga: If lagna has malefics or has “paapa kartari” – malefics in 12th and 2nd """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    chk = [[str(nb) in h_to_p[a] for a in [(asc_house)%12,(asc_house+1)%12,(asc_house+11)%12 ]] for nb in const.natural_malefics]
    asubha_yoga = any(any(row) for row in chk)
    return asubha_yoga
def gaja_kesari_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Gaja-Kesari Yoga: If (1) Jupiter is in a quadrant from Moon, (2) a benefic planet
        conjoins or aspects Jupiter, and, (3) Jupiter is not debilitated or combust or in an
        enemy’s house, """
    """
        TODO: Not implemented fully - so return False
    """
    return False
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    jupiter_house = p_to_h[4]
    chk1 = jupiter_house in quadrants_of_the_house(p_to_h[1])
    #print(chk1,quadrants_of_the_house(p_to_h[1]))
    #if not chk1:
    #    return False
    bpj = house.aspected_planets_of_the_raasi(h_to_p, jupiter_house)
    #bpj = tajaka.benefic_aspects_of_the_planet(h_to_p, 4)[1] 
    chk2 = any(int(p) in const.natural_benefics or p_to_h[int(p)]==jupiter_house  for p in bpj if p!= const._ascendant_symbol)
    print(chk2,bpj)
    #if not chk2:
    #    return False
    chk3 = const.house_strengths_of_planets[4][jupiter_house] > const._ENEMY #not debiliated not in enemy's house
    print(chk3,const.house_strengths_of_planets[4][jupiter_house])
    """ TODO: Planet Positions is required as argument here """
    chk4 = True
    #combustion_planets = charts.planets_in_combustion(planet_positions)
    #print('combustion_planets',combustion_planets)
    #chk4 = 4 not in combustion_planets
    #print(chk1,bpj,const.natural_benefics,chk2,chk3,combustion_planets,chk4)
    return chk3 or chk4
def guru_mangala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Guru-Mangala Yoga: If Jupiter and Mars are together or in the 7th house from each other """
    #p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    gm_yoga = p_to_h[2]==p_to_h[4] or p_to_h[2]==(p_to_h[4]+6)%12 or p_to_h[4]==(p_to_h[2]+6)%12
    return  gm_yoga
def amala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Amala Yoga: If there are only natural benefics in the 10th house from lagna or Moon """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    lagna_tenth_house = (p_to_h[const._ascendant_symbol]+9)%12
    moon_tenth_house = (p_to_h[1]+9)%12
    ay = any([str(p1) in str(h_to_p[h]) for p1 in const.natural_benefics for h in [lagna_tenth_house,moon_tenth_house]]) 
    return ay
def parvata_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)    
    """ Parvata Yoga: If (1) quadrants are occupied only by benefics and (2) the 7th and 8th houses 
        are either vacant or occupied only by benefics """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    planets_in_lagnam_quadrant = [h_to_p[a] for a in quadrants_of_the_house(asc_house)]
    #print('planets_in_lagnam_quadrant',planets_in_lagnam_quadrant)
    chk1 = [[str(nb) in str(pl) for pl in planets_in_lagnam_quadrant[:]] for nb in const.natural_benefics]
    #print('chk1',chk1)
    py1 = all(any(row) for row in chk1)
    if not py1:
        return False
    chk2 = [[h_to_p[a] =='' or (str(nb) in h_to_p[a]) for a in [(asc_house+6)%12,(asc_house+7)%12]] for nb in const.natural_benefics]
    py2 = all(any(row) for row in chk2)
    #print('chk2',chk2)
    return py1 and py2
def kaahala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kaahala Yoga: If (1) the 4th lord and Jupiter are in mutual quadrants and (2) lagna lord is strong """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    fourth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+3)%12)
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    ky1 = str(fourth_lord) in [h_to_p[a] for a in quadrants_of_the_house((p_to_h[4]))]
    #print(fourth_lord,[h_to_p[a] for a in quadrants_of_the_house((asc_house+3)%12)],ky1)
    if not ky1:
        return False
    ky2 = const.house_strengths_of_planets[lagna_lord][asc_house] > const._NEUTRAL_SAMAM
    #print(const.house_strengths_of_planets[lagna_lord][asc_house],const._NEUTRAL_SAMAM,ky2)
    return ky1 and ky2
def chaamara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chaamara Yoga: If the lagna lord is exalted in a quadrant with Jupiter’s aspect or
        two benefics join in 7th, 9th or 10th """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    lagna_house = p_to_h[lagna_lord]
    cy = [[(str(nb) in h_to_p[a]) for a in [(asc_house+6)%12,(asc_house+8)%12,(asc_house+9)%12]] for nb in const.natural_benefics]
    cy1 = sum(sum(cy,[])) > 1
    if cy1:
        return True
    cy2 = const.house_strengths_of_planets[lagna_lord][lagna_house] >= const._EXALTED_UCCHAM and str(lagna_lord) in house.graha_drishti_of_the_planet(h_to_p, 4)
    #print('cy2',const.house_strengths_of_planets[lagna_lord][lagna_house],lagna_lord,house.graha_drishti_of_the_planet(h_to_p, 4))
    return cy1 or cy2
def sankha_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sankha Yoga: If (1) lagna lord is strong and (2) 5th and 6th lords are in mutual
        quadrants, then this yoga is present. Alternately, this yoga is present if (1) lagna lord
        and 10th lord are together in a movable sign and (2) the 9th lord is strong. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    fifth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+4)%12)
    sixth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+5)%12)
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    ky1 = str(fifth_lord) in [h_to_p[a] for a in quadrants_of_the_house((asc_house+5)%12)]
    ky2 = str(sixth_lord) in [h_to_p[a] for a in quadrants_of_the_house((asc_house+4)%12)]
    ky3 = const.house_strengths_of_planets[lagna_lord][asc_house] > const._NEUTRAL_SAMAM
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    ky4 = const.house_strengths_of_planets[ninth_lord][p_to_h[ninth_lord]] > const._NEUTRAL_SAMAM
    ky5 = p_to_h[lagna_lord] == p_to_h[ninth_lord] and p_to_h[lagna_lord] in const.movable_signs
    return (ky1 and ky2 and ky3) or (ky4 and ky5)
def bheri_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Bheri Yoga: If (1) the 9th lord is strong and (2) 1st, 2nd, 7th and 12th houses are
        occupied by planets, then this yoga is present. Alternately, this is yoga is present if
        (1) the 9th lord is strong and (2) Jupiter, Venus and lagna lord are in mutual
        quadrants. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    by1 = const.house_strengths_of_planets[ninth_lord][p_to_h[ninth_lord]] > const._NEUTRAL_SAMAM
    by2 = all([ any([str(p_to_h[p]) in str(hp) for hp in [asc_house, (asc_house+1)%12, (asc_house+6)%12, (asc_house+11)%12]]) for p in [*range(9)] ])
    by3 = [h in quadrants_of_the_house(asc_house) for h in [p_to_h[4], p_to_h[5], asc_house]]
    return by1 and (by2 or by3)
def mridanga_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Mridanga Yoga: If (1) there are planets in own and exaltation signs in quadrants
        and trines and (2) lagna lord is strong. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    quadrants_and_trines = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(asc_house)
    my1 = any([any([p_to_h[p]==h and const.house_strengths_of_planets[p][h]>const._FRIEND for h in quadrants_and_trines]) for p in range(9)])
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    my2 = const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return my1 and my2
def sreenaatha_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sreenaatha Yoga: If (1) the 7th lord is exalted in 10th and (2) 10th lord is with 9th lord. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    seventh_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+6)%12)
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    tenth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    sy1 = const.house_strengths_of_planets[seventh_lord][(asc_house+9)%12]>const._FRIEND
    sy2 = p_to_h[ninth_lord] == p_to_h[tenth_lord]
    return sy1 and sy2
def matsya_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Matsya Yoga: If (1) benefics are in lagna and 9th, (2) some planets are in 5th, and,
        (3) malefics are in chaturasras (4th and 8th houses). """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
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
def koorma_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Koorma Yoga: If (1) the 5th, 6th and 7th houses are occupied by benefics who are in
        own, exaltation or friendly signs and (2) the 1st, 3rd and 11th houses are occupied by
        malefics who are in own or exaltation signs. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ph = sum([h_to_p[h].split('/') for h in [(asc_house+4)%12,(asc_house+5)%12,(asc_house+6)%12]],[])
    ph = [p for p in ph if p != '']
    my1 = ([any(str(p) in str(nb) for nb in const.natural_benefics) for p in ph])
    if not my1:
        return False
    my1 = all([const.house_strengths_of_planets[int(p)][p_to_h[int(p)]] > const._NEUTRAL_SAMAM for p in ph if p!=const._ascendant_symbol])
    ph = sum([h_to_p[h].split('/') for h in [asc_house,(asc_house+2)%12,(asc_house+10)%12]],[])
    ph = [p for p in ph if p != '']
    my2 = ([any(str(p) in str(nb) for nb in const.natural_malefics) for p in ph])
    if my2:
        my2 = all([const.house_strengths_of_planets[int(p)][p_to_h[int(p)]] > const._NEUTRAL_SAMAM for p in ph  if p!=const._ascendant_symbol])
    return my1 and my2
def khadga_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Khadga Yoga: If (1) the 2nd lord is in the 9th house, (2) the 9th lord is in the 2nd
        house, and, (3) lagna lord is in a quadrant or a trine. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    second_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+1)%12)
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    ky1 = (p_to_h[second_lord] == (asc_house+8)%12) and (p_to_h[ninth_lord] == (asc_house+1)%12)
    quadrants_and_trines = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(asc_house)
    ky2 = p_to_h[lagna_lord] in quadrants_and_trines
    return ky1 and ky2
def kusuma_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kusuma Yoga: If (1) lagna is in a fixed sign, (2) Venus is in a quadrant, (3) Moon is
        in a trine with a benefic, and, (4) Saturn is in the 10th house. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ky1 = asc_house in const.fixed_signs
    if not ky1:
        return False
    ky2 = p_to_h[5] in quadrants_of_the_house(asc_house)
    if not ky2:
        return False
    ky4 = p_to_h[6] == (asc_house+9)%12
    if not ky4:
        return False
    ky3 = any([p_to_h[1] in house.trines_of_the_raasi(p_to_h[nb]) for  nb in const.natural_benefics])
    return ky1 and ky2 and ky3 and ky4
def kalaanidhi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kalaanidhi Yoga: If (1) Jupiter is in the 2nd house or the 5th house and (2) he is
        conjoined or aspected by Mercury and Venus. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ky1 = p_to_h[4] == (asc_house+1)%12 or p_to_h[4] == (asc_house+4)%12
    if not ky1:
        return False
    ky2 = p_to_h[4] == p_to_h[3] and p_to_h[4] == p_to_h[5]
    ky3 = all([any([str(p1) in str(p2) for p2 in house.aspected_planets_of_the_raasi(h_to_p, p_to_h[4])]) for p1 in [3,5]])
    return ky1 and (ky2 or ky3)
def kalpadruma_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kalpadruma Yoga: Consider (1) lagna lord, (2) his dispositor, (3) the latter’s
        dispositor in rasi and (4) in navamsa. If all the four planets are all in quadrants, trines
        or exaltation signs. """
    """ UnComment this For testing 
    h_to_p_rasi = ['5','7','2','','L','1','6','8','','','4/0','3']
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    asc_house = p_to_h[const._ascendant_symbol]
    h_to_p_navamsa = ['0','','5','','3','7/1','','4','L','','6/2','8']
    p_to_h_navamsa = utils.get_planet_to_house_dict_from_chart(h_to_p_navamsa)
    asc_house_navamsa = p_to_h_navamsa[const._ascendant_symbol]
    #Uncomment this for testing """
    #""" Comment this for actual 
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    # Comment this for actual """
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    depositor_1 = house.house_owner_from_planet_positions(planet_positions,p_to_h[lagna_lord])
    depositor_2 = house.house_owner_from_planet_positions(planet_positions,p_to_h[depositor_1])
    depositor_3 = house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[depositor_1])
    all_four_planets = [lagna_lord,depositor_1,depositor_2,depositor_3]
    ky1 = []
    quadrants_and_trines_of_rasi = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(asc_house)
    quadrants_and_trines_of_navamsa = house.quadrants_of_the_raasi(asc_house_navamsa)+house.trines_of_the_raasi(asc_house_navamsa)
    for p in all_four_planets:
        kyp = const.house_strengths_of_planets[p][p_to_h[p]] > const._FRIEND
        kyp = kyp or p_to_h[p] in quadrants_and_trines_of_rasi
        ky1.append(kyp)
    ky2 = []
    for p in all_four_planets:
        kyp = const.house_strengths_of_planets[p][p_to_h_navamsa[p]] > const._FRIEND
        kyp = kyp or p_to_h_navamsa[p] in quadrants_and_trines_of_navamsa
        ky2.append(kyp)
    return all(ky1) and all(ky2)
def lagnaadhi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Lagnaadhi Yoga: If (1) the 7th and 8th houses from lagna are occupied by benefics
        and (2) no malefics conjoin or aspect these planets. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ly1 = all([any([p_to_h[nb] == h for h in [(asc_house+6)%12,(asc_house+7)%12]]) for nb in const.natural_benefics])
    if not ly1:
        return False
    ly2 = all([any([p_to_h[nb] == h for h in [(asc_house+6)%12,(asc_house+7)%12]]) for nb in const.natural_malefics])
    return ly1 and ly2 
def hari_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Hari Yoga: If benefics occupy the 2nd, 12th and 8th houses counted from the 2nd lord """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    lord_house = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+1)%12)]
    benefic_houses = [(lord_house+1)%12,(lord_house+7)%12,(lord_house+11)%12]
    ly1 = all([any([p_to_h[nb] == h for h in benefic_houses]) for nb in const.natural_benefics])
    return ly1
def hara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Hara Yoga: If benefics occupy the 4th, 9th and 8th houses counted from the 7th lord. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    lord_house = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+6)%12)]
    benefic_houses = [(lord_house+3)%12,(lord_house+8)%12,(lord_house+7)%12]
    ly1 = all([any([p_to_h[nb] == h for h in benefic_houses]) for nb in const.natural_benefics])
    return ly1
def brahma_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Brahma Yoga: If benefics occupy the 4th, 10th and 11th houses counted from lagna lord. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    lord_house = p_to_h[house.house_owner_from_planet_positions(planet_positions,asc_house)]
    benefic_houses = [(lord_house+3)%12,(lord_house+9)%12,(lord_house+10)%12]
    ly1 = all([any([p_to_h[nb] == h for h in benefic_houses]) for nb in const.natural_benefics])
    """ Brahma yoga (another variation): “If (1) Jupiter is in a quadrant from
        the 9th lord, (2) Venus is in a quadrant from the 11th lord, and, (3) Mercury is in a
        quadrant from the 1st lord or 10th lord. """
    ly2 = p_to_h[4] in quadrants_of_the_house(p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)])
    ly3 = p_to_h[5] in quadrants_of_the_house(p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+10)%12)])
    ly4_1 = p_to_h[3] in quadrants_of_the_house(p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house)%12)])
    ly4_2 = p_to_h[3] in quadrants_of_the_house(p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)])
    return ly1 or (ly2 and ly3 and (ly4_1 or ly4_1))
def vishnu_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vishnu Yoga: If (1) the 9th and 10th lords are in the 2nd house and (2) the lord of the
        sign occupied in navamsa by the 9th lord in rasi chart is also in the 2nd house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ninth_lord_in_rasi = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12) 
    vy1 = p_to_h[ninth_lord_in_rasi]==(asc_house+1)%12 and p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)]==(asc_house+1)%12
    if not vy1:
        return False
    lord_of_ninth_in_navamsa = house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[ninth_lord_in_rasi])
    vy2 = p_to_h[lord_of_ninth_in_navamsa] == (asc_house+1)%12
    return vy1 and vy2
def siva_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Siva Yoga: If (1) the 5th lord is in the 9th house, (2) the 9th lord is in the 10th house,
        and, (3) the 10th lord is in the 5th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    fifth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+4)%12)
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    tenth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)
    sy = p_to_h[fifth_lord] == (asc_house+8)%12 and p_to_h[ninth_lord] == (asc_house+9)%12 and p_to_h[tenth_lord] == (asc_house+4)%12
    return sy
def trilochana_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Trilochana Yoga: If Sun, Moon and Mars are in mutual trines """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ty = p_to_h[1] in house.trines_of_the_raasi(p_to_h[0]) and p_to_h[2] in house.trines_of_the_raasi(p_to_h[0])
    return ty
def gouri_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Gouri Yoga: If the lord of the sign occupied in navamsa by the 10th lord is exalted in
        the 10th house and lagna lord joins him """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    navamsa_lord = house.house_owner_from_planet_positions(planet_positions,asc_house_navamsa)
    rasi_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    gy = p_to_h[rasi_lord] == (asc_house+9)%12 and p_to_h[navamsa_lord] == (asc_house+9)%12 and const.house_strengths_of_planets[navamsa_lord][(asc_house+9)%12] > const._FRIEND 
    return gy
def chandikaa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chandikaa Yoga: If (1) lagna is in a fixed sign aspected by 6th lord and (2) Sun
        joins the lords of the signs occupied in navamsa by 6th and 9th lords """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    sixth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+5)%12)
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    #cy1 = asc_house in const.fixed_signs and asc_house in house.aspected_rasis_of_the_planet(h_to_p, sixth_lord)
    cy1 = asc_house in const.fixed_signs and str(lagna_lord) in house.graha_drishti_of_the_planet(h_to_p, sixth_lord)
    #print('cy1',asc_house,const.fixed_signs,str(lagna_lord),house.graha_drishti_of_the_planet(h_to_p, sixth_lord))
    sixth_lord_owner_in_navamsa = house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[sixth_lord])
    ninth_lord_owner_in_navamsa = house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[ninth_lord])
    cy2 = p_to_h[0] == p_to_h[sixth_lord_owner_in_navamsa] and p_to_h[0] == p_to_h[ninth_lord_owner_in_navamsa]
    return cy1 and cy2
def lakshmi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Lakshmi Yoga: If (1) the 9th lord is in an own sign or in his exaltation sign that
        happens to be quadrant from lagna and (2) lagna lord is strong """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    ly1 = const.house_strengths_of_planets[ninth_lord][p_to_h[ninth_lord]] > const._FRIEND and p_to_h[ninth_lord] in house.quadrants_of_the_raasi(asc_house)
    ly2 =  const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return ly1 and ly2
def saarada_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Saarada Yoga: If (1) the 10th lord is in the 5th house, (2) Mercury is in a quadrant,
        (3) Sun is strong in Leo, (4) Mercury or Jupiter is in a trine from Moon, and, (5)
        Mars is in 11th, """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    sy1 = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)]==(asc_house+4)%12
    if not sy1:
        return False
    sy2 = p_to_h[3] in quadrants_of_the_house(asc_house)
    if not sy2:
        return False
    sy3 = p_to_h[0]==4 and const.house_strengths_of_planets[0][4] > const._FRIEND
    if not sy3:
        return False
    sy4 = [any([str(h) in str(t) for t in house.trines_of_the_raasi(p_to_h[1])]) for h in [p_to_h[3],p_to_h[4]]]
    if not sy4:
        return False
    sy5 = p_to_h[2]==(asc_house+10)%12
def bhaarathi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Bhaarathi Yoga: If the lord of the sign occupied in navamsa by 2nd, 5th or 11th lord
        exalted and joins the 9th lord """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    second_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+1)%12)
    fifth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+4)%12)
    eleventh_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+10)%12)
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)
    navamsa_lords = [house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[second_lord]),house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[fifth_lord]),
                     house.house_owner_from_planet_positions(planet_positions,p_to_h_navamsa[eleventh_lord])]
    by1 = [p_to_h[ninth_lord] == p_to_h[nl] and const.house_strengths_of_planets[nl][p_to_h[ninth_lord]] > const._FRIEND for nl in navamsa_lords]
    return by1
def saraswathi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Saraswathi Yoga: If (1) each of Mercury, Jupiter and Venus occupies a quadrant or
        a trine or the 2nd house (not necessarily together) and (2) Jupiter is in an own or
        friendly or exaltation sign """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    quadrants_and_trines = house.quadrants_of_the_raasi(asc_house)+house.trines_of_the_raasi(p_to_h[3])
    sy1 = all([any([str(p) in str(qt) for qt in [(asc_house+1)%12]+quadrants_and_trines]) for p in [3,4,5]])
    if not sy1:
        return False
    sy2 = const.house_strengths_of_planets[4][p_to_h[4]] > const._NEUTRAL_SAMAM
    return sy1 and sy2
def amsaavatara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Amsaavatara Yoga: If Jupiter, Venus and exalted Saturn are in quadrants """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    ay1 = all([any([str(p) in str(q) for q in house.quadrants_of_the_raasi(p_to_h[4])]) for p in [4,5,6]])
    ay2 = const.house_strengths_of_planets[6][p_to_h[6]] > const._FRIEND
    return ay1 and ay2
def devendra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Devendra Yoga: If (1) lagna is in a fixed sign, (2) 2nd and 10th lords have an
        exchange, and, (3) lagna and 11th lords have an exchange """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    dy1 = asc_house in const.fixed_signs
    if not dy1:
        return False
    dy2 = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+1)%12)] == (asc_house+9)%12 and p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)] == (asc_house+1)%12
    if not dy2:
        return False
    dy3 = p_to_h[house.house_owner_from_planet_positions(planet_positions,asc_house)] == (asc_house+10)%12 and p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+10)%12)] == asc_house
    return dy1 and dy2 and dy3
def indra_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Indra Yoga: If (1) the 5th and 11th lords have an exchange and (2) Moon occupies
        the 5th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    iy1 = p_to_h[1]==(asc_house+4)%12
    if not iy1:
        return False
    iy2 = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+4)%12)] == (asc_house+10)%12 and p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+10)%12)] == (asc_house+4)%12
    return iy1 and iy2
def ravi_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Ravi Yoga: If (1) Sun is in the 10th house and (2) the 10th lord is in the 3rd housewith Saturn """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    ry1 = p_to_h[0] == (asc_house+9)%12
    if not ry1:
        return False
    ry2 = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)] == (asc_house+2)%12 and p_to_h[6] == (asc_house+2)%12
    return ry1 and ry2 
def bhaaskara_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Bhaaskara Yoga: If (1) Moon is in the 12th from Sun, (2) Mercury is in the 2nd from
        Sun, and, (3) Jupiter is in the 5th or 9th from Moon. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    by1 = p_to_h[1] == (p_to_h[0]+11)%12
    if not by1:
        return False
    by2 = p_to_h[3] == (p_to_h[0]+1)%12
    if not by2:
        return False
    by3 = (p_to_h[4] == (p_to_h[1]+4)%12) or (p_to_h[4] == (p_to_h[1]+8)%12)
    return by1 and by2 and by3
def kulavardhana_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Kulavardhana Yoga: If each planet occupies the 5th house from either lagna or Moon or Sun """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    ky = all([ p_to_h[p]==(p_to_h[const._ascendant_symbol]+4)%12 or p_to_h[p]==(p_to_h[0]+4)%12 or p_to_h[p]==(p_to_h[1]+4)%12 for p in [*range(2,9)] ])
    return ky
def vasumati_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vasumati Yoga: benefics occupy upachayas """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    vy = str(p_to_h[6]) in house.upachayas_of_the_raasi(p_to_h[5]) or p_to_h[5] in house.upachayas_of_the_raasi(p_to_h[6])
    return vy
def gandharva_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Gandharva Yoga: If (1) the 10th lord is in a trine from the 7th house, (2) lagna lord
        is conjoined or aspected by Jupiter, (3) Sun is exalted and strong, and, (4) Moon is in
        the 9th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    gy1 = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)] in house.trines_of_the_raasi((asc_house+6)%12)
    if not gy1:
        return False
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
def go_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Go Yoga: If (1) Jupiter is strong in his moolatrikona, (2) the lord of the 2nd house is
        with Jupiter, and, (3) lagna lord is exalted """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    gy1 = const.house_strengths_of_planets[4][const.moola_trikona_of_planets[4]] > const._FRIEND
    if not gy1:
        return False
    gy2 = p_to_h[4] == p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+1)%12)]
    if not gy2:
        return False
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    gy3 = const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return gy1 and gy2 and gy3
def vidyut_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vidyut Yoga: If (1) the 11th lord is in deep exaltation, (2) he joins Venus, and, (3)
        the two of them are in a quadrant from lagna lord """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    eleventh_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+10)%12)
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    vy1 = const.house_strengths_of_planets[eleventh_lord][p_to_h[eleventh_lord]] > const._FRIEND
    if not vy1:
        return False
    vy2 = p_to_h[eleventh_lord] == p_to_h[5]
    if not vy2:
        return False
    vy3 = p_to_h[eleventh_lord] in house.quadrants_of_the_raasi(p_to_h[lagna_lord])
    return vy1 and vy2 and vy3
def chapa_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Chapa Yoga: If (1) the 4th and 10th lords have an exchange and (2) lagna lord is exalted. """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    cy1 = p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+3)%12)] == (asc_house+9)%12 and p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)] == (asc_house+3)%12
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    cy2 = const.house_strengths_of_planets[lagna_lord][p_to_h[lagna_lord]] > const._FRIEND
    return cy1 and cy2
def pushkala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Pushkala Yoga: If (1) lagna lord is with Moon, (2) dispositor of Moon is in a
        quadrant or in the house of an adhimitra (good friend), (2) dispositor of Moon
        aspects lagna, and, (4) there is a planet in lagna """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    moon_house = p_to_h[1]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    py1 = p_to_h[lagna_lord] == moon_house
    dispositor_of_moon = house.house_owner_from_planet_positions(planet_positions,moon_house)
    dispositor_house = p_to_h[dispositor_of_moon]
    dispositor_quadrants = house.quadrants_of_the_raasi(dispositor_house)
    py2_1 = dispositor_house in house.strong_signs_of_planet(dispositor_of_moon)
    py2_2 = dispositor_house in dispositor_quadrants
    py2_3 = dispositor_of_moon in house.aspected_planets_of_the_raasi(h_to_p,asc_house)
    py3 =len([h for h in h_to_p[p_to_h[const._ascendant_symbol]].split('/') if h!= '']) > 1
    return py1 and (py2_1 or py2_2) and py2_3 and py3
def makuta_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Makuta Yoga: If (1) Jupiter is in the 9th house from the 9th lord, (2) the 9th house
        from Jupiter has a benefic, and, (3) Saturn is in the 10th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    my1 = p_to_h[4] == (p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+8)%12)]+8)%12
    my2 = any([np in ['5','6'] for np in h_to_p[(asc_house+8)%12].split('/') if np !=const._ascendant_symbol and np!=''])
    my3 = p_to_h[6] == (asc_house+9)%12
    return my1 and my2 and my3
def jaya_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Jaya Yoga: If (1) the 10th lord is in deep exaltation and (2) the 6th lord is debilitated """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    tenth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+9)%12)
    jy1 = const.house_strengths_of_planets[tenth_lord][p_to_h[tenth_lord]] == const._EXALTED_UCCHAM
    sixth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+5)%12)
    jy2 = const.house_strengths_of_planets[sixth_lord][p_to_h[sixth_lord]] == const._DEFIBILATED_NEECHAM
    return jy1 and jy2
def harsha_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Harsha Yoga: If the 6th lord occupies the 6th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    return p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+5)%12)] == (asc_house+5)%12
def sarala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Sarala Yoga: If the 8th lord occupies the 8th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    return p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+7)%12)] == (asc_house+7)%12
def vimala_yoga_from_planet_positions(planet_positions):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    """ Vimala Yoga: If the 12th lord occupies the 12th house """
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    return p_to_h[house.house_owner_from_planet_positions(planet_positions,(asc_house+11)%12)] == (asc_house+11)%12
if __name__ == "__main__":
    pass