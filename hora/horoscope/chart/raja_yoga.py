import itertools
import json
from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house, charts
_lang_path = const._LANGUAGE_PATH
""" Basic Raaja Yoga: In any chart, Lord Vishnu sits in the quadrants and Goddess
    Lakshmi sits in the trines. If the lord of a quadrant is associated with the lord of a
    trine, that association brings the combined blessings of Lakshmi and Vishnu. This is
    called a Raaja Yoga.
    (1) The two planets are conjoined,
    (2) The two planets aspect each other with graha drishti, or,
    (3) The two planets have a parivartana (exchange). For example, if the 4th lord is in
        the 5th house and the 5th lord is in the 4th house, then we say that there is a
        parivartana between the 4th and 5th lords. This is an association.
    If the lord of a quadrant and the lord of a trine have one of the three kinds of
    associations mentioned above, it forms a Raaja Yoga. Lagna can be taken as a
    quadrant or a trine here. It is both. 
    The magnitude to which this raaja yoga fructifies depends on the strength of the two
    planets. The key factors that come into play are:
    (1) The two planets should be free from afflictions from functional malefics.
    (2) The conjunction or aspect responsible for the Raaja Yoga should be close (say,
        within 6° or so). """
division_chart_factors = const.division_chart_factors
lords_of_quadrants = lambda h_to_p,raasi:[house.house_owner(h_to_p,h) for h in house.quadrants_of_the_raasi(raasi)] #V2.3.1
lords_of_trines = lambda h_to_p, raasi:[house.house_owner(h_to_p,h) for h in house.trines_of_the_raasi(raasi)] #V2.3.1
lords_of_quadrants_from_planet_positions = lambda planet_positions,raasi:[house.house_owner_from_planet_positions(planet_positions,int(h)) for h in house.quadrants_of_the_raasi(raasi)] #V2.3.1
lords_of_trines_from_planet_positions = lambda planet_positions, raasi:[house.house_owner_from_planet_positions(planet_positions,int(h)) for h in house.trines_of_the_raasi(raasi)] #V2.3.1
def get_raja_yoga_resources(language='en'):
    """
        get raja yoga names from raja_yoga_msgs_<lang>.txt
        @param language: Two letter language code. en, hi, ka, ta, te
        @return json strings from the resource file as dictionary 
    """
    json_file = _lang_path + const._DEFAULT_RAJA_YOGA_JSON_FILE_PREFIX+language+'.json'
    #print('opening json file',json_file)
    f = open(json_file,"r",encoding="utf-8")
    msgs = json.load(f)
    #print('json msgs collected')
    return msgs
def get_raja_yoga_details_for_all_charts(jd,place,language='en'):
    """
        Get all the raja yoga information that are present in the divisional charts for a given julian day and place
        @param jd: Julian day number
        @param place: struct (plave name, latitude, longitude, timezone)
        @param language: two letter language code (en, hi, ka, ta, te)
        @return: returns a 2D List of raja yoga_name, raja yoga_details
            raja yoga_name in language
            raja yoga_details: [chart_ID, raja_yoga_name, raja_yoga_desription, raja_yoga_benfits] 
    """
    msgs = get_raja_yoga_resources(language=language)
    raja_yoga_results_combined = {}
    ascendant_index = const._ascendant_symbol
    planet_positions_navamsa = drik.dhasavarga(jd,place,divisional_chart_factor=9)
    ascendant_longitude = drik.ascendant(jd,place)[1]
    asc_house_navamsa,asc_long = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor=9)
    planet_positions_navamsa += [[ascendant_index,(asc_house_navamsa,asc_long)]]
    for dv in division_chart_factors:
        raja_yoga_results,_,_ = get_raja_yoga_details(jd,place,divisional_chart_factor=dv,language=language)
        raja_yoga_results.update(raja_yoga_results_combined)
        raja_yoga_results_combined = raja_yoga_results
    #print('Found',len(yoga_results_combined),'out of',len(msgs)*len(division_chart_factors),'yogas')
    return raja_yoga_results_combined,len(raja_yoga_results_combined),len(msgs)*len(division_chart_factors)
def get_raja_yoga_details(jd,place,divisional_chart_factor=1,language='en'):
    """
        Get all the raja yoga information that are present in the requested divisional charts for a given julian day and place
        @param jd: Julian day number
        @param place: struct (plave name, latitude, longitude, timezone)
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @param language: two letter language code (en, hi, ka, ta, te)
        @return: returns a 2D List of yoga_name, yoga_details
            raja yoga_name in language
            raja yoga_details: [chart_ID, raja_yoga_name, raja_yoga_desription, raja_yoga_benfits] 
    """
    utils.set_language(language)
    msgs = get_raja_yoga_resources(language=language)
    res = utils.get_resource_messages()
    ascendant_index = const._ascendant_symbol
    planet_positions = drik.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = drik.ascendant(jd,place)[1]
    asc_house,asc_long = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[ascendant_index,(asc_house,asc_long)]]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    raja_yoga_results = {}
    for raja_yoga_function,details in msgs.items():
        details_str = 'D'+str(divisional_chart_factor)+'-'
        raja_yoga_pairs = get_raja_yoga_pairs_from_planet_positions(planet_positions)
        if raja_yoga_pairs:
            rp_str = ''
            for rp1,rp2 in raja_yoga_pairs:
                raja_yoga_exists = eval(raja_yoga_function+'_from_planet_positions')(planet_positions,rp1,rp2)
                if raja_yoga_exists:
                    rp_str += ' '+'[' +utils.PLANET_NAMES[rp1]+'-'+utils.PLANET_NAMES[rp2]+'] '
                    #details_str += rp_str
            if rp_str != '':
                details_str += res['raja_yoga_pairs'] + rp_str
                details.insert(0,details_str)
                raja_yoga_results[raja_yoga_function] = details
    #print('Found',len(raja_yoga_results),'out of',len(msgs),'raja_yogas in D'+str(divisional_chart_factor),'chart')
    return raja_yoga_results,len(raja_yoga_results),len(msgs)
def _check_association(h_to_p,lord1,lord2):
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    """ (1) The two lords are conjoined, """
    chk1 = p_to_h[lord1] == p_to_h[lord2]
    if chk1:
        #print('conjoined',p_to_h[lord1],p_to_h[lord2])
        return True
    """ (2) The two lords aspect each other with graha drishti Rahu/Ketu dont form graha drishti"""
    chk2_1 = lord1 not in [7,8] and lord2 not in [7,8] 
    chk2 = chk2_1 and str(lord1) in house.graha_drishti_of_the_planet(h_to_p, lord2) and str(lord2) in house.graha_drishti_of_the_planet(h_to_p, lord1)
    if chk2:
        #print('graha drishti',lord1,house.graha_drishti_of_the_planet(h_to_p, lord2),lord2,house.graha_drishti_of_the_planet(h_to_p, lord1))
        return True
    """ (3) The two lords have a parivartana (exchange). """
    chk3 = (lord1 == house.house_owner(h_to_p,p_to_h[lord2])) and (lord2 == house.house_owner(h_to_p,p_to_h[lord1]))
    return chk1 or chk2 or chk3
def _check_association_from_planet_positions(planet_positions,lord1,lord2):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    """ (1) The two lords are conjoined, """
    chk1 = p_to_h[lord1] == p_to_h[lord2]
    if chk1:
        #print('conjoined',p_to_h[lord1],p_to_h[lord2])
        return True
    """ (2) The two lords aspect each other with graha drishti Rahu/Ketu dont form graha drishti"""
    chk2_1 = lord1 not in [7,8] and lord2 not in [7,8] 
    chk2 = chk2_1 and str(lord1) in house.graha_drishti_of_the_planet(h_to_p, lord2) and str(lord2) in house.graha_drishti_of_the_planet(h_to_p, lord1)
    if chk2:
        #print('graha drishti',lord1,house.graha_drishti_of_the_planet(h_to_p, lord2),lord2,house.graha_drishti_of_the_planet(h_to_p, lord1))
        return True
    """ (3) The two lords have a parivartana (exchange). """
    chk3 = (lord1 == house.house_owner_from_planet_positions(planet_positions,p_to_h[lord2])) and \
           (lord2 == house.house_owner_from_planet_positions(planet_positions,p_to_h[lord1]))
    return chk1 or chk2 or chk3
def __check_association(h_to_p,planet1,planet2):
    if planet1 == planet2:
        return False
    #print('raja yoga check ',planet1,planet2)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    planet1_lord = house.house_owner(h_to_p,planet1) #V2.3.1
    planet1_house = p_to_h[planet1]
    #print('planet1,lord,house',planet1,planet1_lord,planet1_house)
    planet2_lord = house.house_owner(h_to_p,planet2) #V2.3.1
    planet2_house = p_to_h[planet2]
    #print('planet2,lord,house',planet2,planet2_lord,planet2_house)
    """ TODO: check if lords in the quad / trine houses """
    chk0 = (planet1_house in house.quadrants_of_the_raasi(asc_house) and planet2_house in house.trines_of_the_raasi(asc_house)) or \
           (planet2_house in house.quadrants_of_the_raasi(asc_house) and planet1_house in house.trines_of_the_raasi(asc_house))
    #print('lords in quad/trine',planet1,planet1_house, house.quadrants_of_the_raasi(asc_house),planet2,planet2_house,house.trines_of_the_raasi(asc_house),\
    #            planet2,planet2_house, house.quadrants_of_the_raasi(asc_house),planet1,planet1_house,house.trines_of_the_raasi(asc_house),chk0)
    chk1 = p_to_h[planet1] == p_to_h[planet2]
    #print('chk1',p_to_h[planet1],p_to_h[planet2],'conjoined check',chk1)
    chk2 = str(planet2) in house.graha_drishti_of_the_planet(h_to_p, planet1) or \
           str(planet1) in house.graha_drishti_of_the_planet(h_to_p, planet2) 
    #print('chk2',planet2,house.graha_drishti_of_the_planet(h_to_p, planet1),'aspect check',chk2)
    chk3 = planet1_house == p_to_h[planet2_lord] and planet2_house == p_to_h[planet1_lord]
    #print('chk3',planet1_house,p_to_h[planet2_lord],planet2_house,p_to_h[planet1_lord],'exchange check',chk3)
    return chk1 or chk2 or chk3  
def __check_association_from_planet_positions(planet_positions,planet1,planet2):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    if planet1 == planet2:
        return False
    #print('raja yoga check ',planet1,planet2)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    planet1_lord = house.house_owner_from_planet_positions(planet_positions,planet1) #V2.3.1
    planet1_house = p_to_h[planet1]
    #print('planet1,lord,house',planet1,planet1_lord,planet1_house)
    planet2_lord = house.house_owner_from_planet_positions(planet_positions,planet2) #V2.3.1
    planet2_house = p_to_h[planet2]
    #print('planet2,lord,house',planet2,planet2_lord,planet2_house)
    """ TODO: check if lords in the quad / trine houses """
    chk0 = (planet1_house in house.quadrants_of_the_raasi(asc_house) and planet2_house in house.trines_of_the_raasi(asc_house)) or \
           (planet2_house in house.quadrants_of_the_raasi(asc_house) and planet1_house in house.trines_of_the_raasi(asc_house))
    #print('lords in quad/trine',planet1,planet1_house, house.quadrants_of_the_raasi(asc_house),planet2,planet2_house,house.trines_of_the_raasi(asc_house),\
    #            planet2,planet2_house, house.quadrants_of_the_raasi(asc_house),planet1,planet1_house,house.trines_of_the_raasi(asc_house),chk0)
    chk1 = p_to_h[planet1] == p_to_h[planet2]
    #print('chk1',p_to_h[planet1],p_to_h[planet2],'conjoined check',chk1)
    chk2 = str(planet2) in house.graha_drishti_of_the_planet(h_to_p, planet1) or \
           str(planet1) in house.graha_drishti_of_the_planet(h_to_p, planet2) 
    #print('chk2',planet2,house.graha_drishti_of_the_planet(h_to_p, planet1),'aspect check',chk2)
    chk3 = planet1_house == p_to_h[planet2_lord] and planet2_house == p_to_h[planet1_lord]
    #print('chk3',planet1_house,p_to_h[planet2_lord],planet2_house,p_to_h[planet1_lord],'exchange check',chk3)
    return chk1 or chk2 or chk3  
def dharma_karmadhipati_raja_yoga(p_to_h,raja_yoga_planet1,raja_yoga_planet2):
    """ 
        Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords
        of dharma sthana (9th) and karma sthana (10th) form a raja yoga 
        @param p_to_h: planet_to_house dictionary Example: {0:1,1:2,...'L':11,..} Sun in Ar, Moon in Ta, Lagnam in Pi
        @param raja_yoga_planet1: Planet index for first raja yoga planet  [0 to 6] Rahu/Kethu/Lagnam not supported
        @param raja_yoga_planet2: Planet index for second raja yoga planet [0 to 6] Rahu/Kethu/Lagnam not supported
        @return: True/False = True = dharma karmadhipati yoga is present
    """
    asc_house = p_to_h[const._ascendant_symbol]
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    house_lords = [house.house_owner(h_to_p,h) for h in [(asc_house+8)%12,(asc_house+9)%12]]
    dkchk = all([any([hl == rp for hl in house_lords ]) for rp in [raja_yoga_planet1, raja_yoga_planet2] ])
    #print('dharma_karmadhipati_raja_yoga check',dkchk)
    return dkchk  
    
def dharma_karmadhipati_raja_yoga_from_planet_positions(planet_positions,raja_yoga_planet1,raja_yoga_planet2):
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
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    asc_house = p_to_h[const._ascendant_symbol]
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    house_lords = [house.house_owner_from_planet_positions(planet_positions,h) for h in [(asc_house+8)%12,(asc_house+9)%12]]
    dkchk = all([any([hl == rp for hl in house_lords ]) for rp in [raja_yoga_planet1, raja_yoga_planet2] ])
    #print('dharma_karmadhipati_raja_yoga check',dkchk)
    return dkchk  
    
def get_raja_yoga_pairs(house_to_planet_list):
    """
       To get raja yoga planet pairs from house to planet list
       NOTE: !!! Strength of the pairs are not checked !!!
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @return 2D List of raja yoga planet pairs
          Example: [[0,2],[3,6]] : Tow raja yoga pairs [Sun,Mars] and [Mercury,Saturn]
    """
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    asc_house = p_to_h[const._ascendant_symbol]
    lq = set(lords_of_quadrants(house_to_planet_list,asc_house))
    lt = set(lords_of_trines(house_to_planet_list,asc_house))
    possible_pairs =  [(q,l) for i,q in enumerate(lq) for j,l in enumerate(lt) if q !=l and (q,l)!=(l,q)]
    possible_pairs = list(set(tuple(sorted(x)) for x in possible_pairs))
    #print('possible_pairs',possible_pairs)
    raja_yoga_pairs = []
    for p1,p2 in possible_pairs:
        chk = _check_association(house_to_planet_list, p1, p2)
        if chk:
            raja_yoga_pairs.append([p1,p2])
    return raja_yoga_pairs
def get_raja_yoga_pairs_from_planet_positions(planet_positions):
    """
       To get raja yoga planet pairs from house to planet list
       NOTE: !!! Strength of the pairs are not checked !!!
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @return 2D List of raja yoga planet pairs
          Example: [[0,2],[3,6]] : Tow raja yoga pairs [Sun,Mars] and [Mercury,Saturn]
    """
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    asc_house = p_to_h[const._ascendant_symbol]
    lq = set(lords_of_quadrants_from_planet_positions(planet_positions,asc_house))
    lt = set(lords_of_trines_from_planet_positions(planet_positions,asc_house))
    possible_pairs =  [(q,l) for i,q in enumerate(lq) for j,l in enumerate(lt) if q !=l and (q,l)!=(l,q)]
    possible_pairs = list(set(tuple(sorted(x)) for x in possible_pairs))
    #print('possible_pairs',possible_pairs)
    raja_yoga_pairs = []
    for p1,p2 in possible_pairs:
        chk = _check_association_from_planet_positions(planet_positions, p1, p2)
        if chk:
            raja_yoga_pairs.append([p1,p2])
    return raja_yoga_pairs
def vipareetha_raja_yoga(p_to_h,raja_yoga_planet1,raja_yoga_planet2):
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
    asc_house = p_to_h[const._ascendant_symbol]
    vrchk1 = ([([p_to_h[rp]==dh for dh in house.dushthanas_of_the_raasi(asc_house)]) \
              for rp in [raja_yoga_planet1, raja_yoga_planet2]])
    vrchk = (all([any(vrchk1[0]),any(vrchk1[1])]))
    vr_sub_type = 'Harsh Raja Yoga'
    if vrchk1[0][1]:
        vr_sub_type = 'Saral Raja Yoga'
    elif vrchk1[0][2]:
        vr_sub_type = 'Vimal Raja Yoga'
    if vrchk:
        return vrchk, vr_sub_type
    else:
        return vrchk
def vipareetha_raja_yoga_from_planet_positions(planet_positions,raja_yoga_planet1,raja_yoga_planet2):
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
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    asc_house = p_to_h[const._ascendant_symbol]
    vrchk1 = ([([p_to_h[rp]==dh for dh in house.dushthanas_of_the_raasi(asc_house)]) \
              for rp in [raja_yoga_planet1, raja_yoga_planet2]])
    vrchk = (all([any(vrchk1[0]),any(vrchk1[1])]))
    vr_sub_type = 'Harsh Raja Yoga'
    if vrchk1[0][1]:
        vr_sub_type = 'Saral Raja Yoga'
    elif vrchk1[0][2]:
        vr_sub_type = 'Vimal Raja Yoga'
    if vrchk:
        return vrchk, vr_sub_type
    else:
        return vrchk
def neecha_bhanga_raja_yoga(p_to_h,raja_yoga_planet1, raja_yoga_planet2):
    """
        Checks if given raja yoga pairs form neecha bhanga raja yoga
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
    "TODO: Rule 4 and 5. Get jd,place as inputs "
    house_to_planet_list = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    #p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    rp1_rasi = p_to_h[raja_yoga_planet1]
    rp2_rasi = p_to_h[raja_yoga_planet2]
    rp1_lord = house.house_owner(house_to_planet_list,rp1_rasi)
    rp2_lord = house.house_owner(house_to_planet_list,rp2_rasi)
    kendra_from_moon = house.quadrants_of_the_raasi(p_to_h[1])
    #print(rp1_rasi,rp1_lord,rp2_rasi,rp2_lord)
    " Rule-1"
    chk1_1 = const.house_strengths_of_planets[raja_yoga_planet1][rp1_rasi] <= const._DEFIBILATED_NEECHAM and \
        (const.house_strengths_of_planets[rp1_lord][rp1_rasi] >= const._EXALTED_UCCHAM or \
        rp1_rasi in kendra_from_moon)
    chk1_2 = const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] <= const._DEFIBILATED_NEECHAM and \
        (const.house_strengths_of_planets[rp2_lord][rp2_rasi] >= const._EXALTED_UCCHAM or \
        rp2_rasi in kendra_from_moon)
    chk1 = chk1_1 or chk1_2
    if chk1:
        return True
    "Rule 2"
    chk2_1 = (rp1_rasi == rp2_rasi)
    chk2_2 = (const.house_strengths_of_planets[raja_yoga_planet1][rp1_rasi] >= const._EXALTED_UCCHAM) and \
             (const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] <= const._DEFIBILATED_NEECHAM)
    chk2_3 = (const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] >= const._EXALTED_UCCHAM) and \
             (const.house_strengths_of_planets[raja_yoga_planet1][rp1_rasi] <= const._DEFIBILATED_NEECHAM)
    chk2 = chk2_1 and (chk2_2 or chk2_3)
    if chk2:
        return True
    " Rule 3"
    chk3_1 = (const.house_strengths_of_planets[raja_yoga_planet1][rp2_rasi] <= const._DEFIBILATED_NEECHAM) and \
             (str(raja_yoga_planet1) in house.graha_drishti_of_the_planet(house_to_planet_list, rp1_lord))
    chk3_2 = (const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] <= const._DEFIBILATED_NEECHAM) and \
             (str(raja_yoga_planet1) in house.graha_drishti_of_the_planet(house_to_planet_list, rp2_lord))
    chk3 = chk3_1 or chk3_2
    return chk3
def neecha_bhanga_raja_yoga_from_planet_positions(planet_positions,raja_yoga_planet1, raja_yoga_planet2):
    """
        Checks if given raja yoga pairs form neecha bhanga raja yoga
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
    "TODO: Rule 4 and 5. Get jd,place as inputs "
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    rp1_rasi = p_to_h[raja_yoga_planet1]
    rp2_rasi = p_to_h[raja_yoga_planet2]
    rp1_lord = house.house_owner_from_planet_positions(planet_positions,rp1_rasi)
    rp2_lord = house.house_owner_from_planet_positions(planet_positions,rp2_rasi)
    kendra_from_moon = house.quadrants_of_the_raasi(p_to_h[1])
    " Rule-1"
    chk1_1 = const.house_strengths_of_planets[raja_yoga_planet1][rp1_rasi] <= const._DEFIBILATED_NEECHAM and \
        (const.house_strengths_of_planets[rp1_lord][rp1_rasi] >= const._EXALTED_UCCHAM or \
        rp1_rasi in kendra_from_moon)
    chk1_2 = const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] <= const._DEFIBILATED_NEECHAM and \
        (const.house_strengths_of_planets[rp2_lord][rp2_rasi] >= const._EXALTED_UCCHAM or \
        rp2_rasi in kendra_from_moon)
    chk1 = chk1_1 or chk1_2
    if chk1:
        return True
    "Rule 2"
    chk2_1 = (rp1_rasi == rp2_rasi)
    chk2_2 = (const.house_strengths_of_planets[raja_yoga_planet1][rp1_rasi] >= const._EXALTED_UCCHAM) and \
             (const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] <= const._DEFIBILATED_NEECHAM)
    chk2_3 = (const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] >= const._EXALTED_UCCHAM) and \
             (const.house_strengths_of_planets[raja_yoga_planet1][rp1_rasi] <= const._DEFIBILATED_NEECHAM)
    chk2 = chk2_1 and (chk2_2 or chk2_3)
    if chk2:
        return True
    " Rule 3"
    chk3_1 = (const.house_strengths_of_planets[raja_yoga_planet1][rp2_rasi] <= const._DEFIBILATED_NEECHAM) and \
             (str(raja_yoga_planet1) in house.graha_drishti_of_the_planet(house_to_planet_list, rp1_lord))
    chk3_2 = (const.house_strengths_of_planets[raja_yoga_planet2][rp2_rasi] <= const._DEFIBILATED_NEECHAM) and \
             (str(raja_yoga_planet1) in house.graha_drishti_of_the_planet(house_to_planet_list, rp2_lord))
    chk3 = chk3_1 or chk3_2
    return chk3
def check_other_raja_yoga_1(jd,place,divisional_chart_factor=1):
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    chara_karakas = house.chara_karakas(planet_positions)
    """
        If (a) chara putra karaka (PK) and chara atmaka karaka (AK) are conjoined and
        (b) lagna and 5th lords conjoin, then Raaja Yoga is present and the native
        enjoys power and prosperity. If only one condition is satisfied, still the results
        may be felt, but not fully.
    """
    asc_house = p_to_h['L'] ; lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    fifth_lord = house.house_owner_from_planet_positions(planet_positions,(asc_house+4)%12)
    ak = chara_karakas[0]; pk = chara_karakas[5]
    chk1 = p_to_h[ak] == p_to_h[pk]
    chk2 = p_to_h[lagna_lord] == p_to_h[fifth_lord]
    return chk1 and chk2
def check_other_raja_yoga_2(jd,place,divisional_chart_factor=1):
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    chara_karakas = house.chara_karakas(planet_positions)
    """
        If (a) lagna lord is in 5th, (b) 5th lord is in lagna, (c) AK and PK are in lagna or
        the 5th house, and (d) those planets in owns rasi or amsa or in exaltation or
        aspected by benefics, then this yoga is present
    """
    asc_house = p_to_h['L'] ; lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    fifth_house = (asc_house+4)%12
    fifth_lord = house.house_owner_from_planet_positions(planet_positions,fifth_house)
    ak = chara_karakas[0]; pk = chara_karakas[5]
    chk1 = (p_to_h[lagna_lord] == fifth_house) and (p_to_h[fifth_lord]==asc_house) 
    chk2_1 = (p_to_h[ak] == asc_house) and (p_to_h[pk] == asc_house)
    chk2_2 = (p_to_h[ak] == fifth_house) and (p_to_h[pk] == fifth_house)
    chk2 = chk2_1 or chk2_2
    chk3_1 = const.house_strengths_of_planets[ak][p_to_h[ak]] > const._FRIEND and \
                const.house_strengths_of_planets[pk][p_to_h[pk]] > const._FRIEND
    chk3_2 = const.house_strengths_of_planets[lagna_lord][fifth_house] > const._FRIEND and \
                const.house_strengths_of_planets[fifth_lord][asc_house] > const._FRIEND
    chk3 = chk3_1 and chk3_2
    lagna_lord_aspects = house.aspected_planets_of_the_raasi(h_to_p, fifth_house)
    #chk4_1 = any([lp in const.natural_benefics for lp in lagna_lord_aspects])
    chk4_1 = any([lp in charts.benefics(jd, place)[0] for lp in lagna_lord_aspects])
    fifth_lord_aspects = house.aspected_planets_of_the_raasi(h_to_p, asc_house)
    #chk4_2 = any([fp in const.natural_benefics for fp in fifth_lord_aspects])
    chk4_2 = any([fp in charts.benefics(jd,place) for fp in fifth_lord_aspects])
    ak_lord_aspects = house.aspected_planets_of_the_raasi(h_to_p, p_to_h[ak])
    #chk4_3 = any([lp in const.natural_benefics for lp in ak_lord_aspects])
    chk4_3 = any([lp in charts.benefics(jd, place) for lp in ak_lord_aspects])
    pk_lord_aspects = house.aspected_planets_of_the_raasi(h_to_p, p_to_h[pk])
    #chk4_4 = any([fp in const.natural_benefics for fp in pk_lord_aspects])
    chk4_4 = any([fp in charts.benefics(jd, place) for fp in pk_lord_aspects])
    chk4 = chk4_1 and chk4_2 and chk4_3 and chk4_4
    return chk1 and chk2 and (chk3 or chk4)
def check_other_raja_yoga_3(jd,place,divisional_chart_factor=1):
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    chara_karakas = house.chara_karakas(planet_positions)
    """
        If the 9th lord and AK are in lagna, 5th or 7th, aspected by benefics, then Raaja
        Yoga is present.
    """
    asc_house = p_to_h['L'] ; lagna_lord = house.house_owner_from_planet_positions(planet_positions,asc_house)
    ninth_house = (asc_house+8)%12
    ninth_lord = house.house_owner_from_planet_positions(planet_positions,ninth_house)
    ak = chara_karakas[0]
    chk = any([h1 == h2 for h1 in [p_to_h[ninth_lord],p_to_h[ak]] for h2 in [(asc_house+h)%12 for h in [0,4,6]] ])
    pass
if __name__ == "__main__":
    #from hora.tests import pvr_tests
    #pvr_tests.raja_yoga_tests()
    #exit()
    def raja_yoga_tests():
        chapter = 'Chapter 11.7 Raja Yoga Tests '
        chart_10_akbar = ['','','1','','8','','4/5/6/L','0','3','2','7','']
        dob = (1542,12,4)
        tob = (3,39,0)
        place = drik.Place('unknown',25+19/60,69+47/60,5.0)
        jd_at_dob = utils.julian_day_number(dob, tob)
        planet_positions = charts.rasi_chart(jd_at_dob, place)
        p_to_h = utils.get_planet_to_house_dict_from_chart(chart_10_akbar)
        print(chapter+'chart_10_akbar',chart_10_akbar)
        ry_pairs = get_raja_yoga_pairs_from_planet_positions(planet_positions)
        print(chapter+'raja yoga pairs',ry_pairs)
        for p1,p2 in ry_pairs:
            print(chapter+'neecha_bhanga_raja_yoga',p1,p2,neecha_bhanga_raja_yoga_from_planet_positions(planet_positions, p1, p2))
        chart_14_rajiv_gandhi = ['', '', '6', '7', 'L/0/1/3/4/5', '2', '', '', '', '8', '', '']
        dob = (1944,8,20)
        tob = (7,41,0)
        place = drik.Place('unknown',18+58/60,72+49/60,5.5)
        jd_at_dob = utils.julian_day_number(dob, tob)
        planet_positions = charts.rasi_chart(jd_at_dob, place)
        #p_to_h = utils.get_planet_to_house_dict_from_chart(chart_14_rajiv_gandhi)
        print(chapter+'chart_14_rajiv_gandhi',chart_14_rajiv_gandhi)
        ry_pairs = get_raja_yoga_pairs_from_planet_positions(planet_positions)
        print(chapter+'raja yoga pairs',ry_pairs)
        for p1,p2 in ry_pairs:
            print(chapter+'neecha_bhanga_raja_yoga',p1,p2,neecha_bhanga_raja_yoga_from_planet_positions(planet_positions, p1, p2))
        dob = (1954,1,29)
        tob = (4,30,0)
        place = drik.Place('unknown',33+3/60,-89-35/60,-5.0)
        jd_at_dob = utils.julian_day_number(dob, tob)
        planet_positions = charts.rasi_chart(jd_at_dob, place)
        chart_oprah_winfrey = ['','4','','8','','','6','1/2','','0/3/5/L/7','',''] # For dharma karmadhipathi check
        print(chapter+'chart_oprah_winfrey',chart_oprah_winfrey)
        ry_pairs = get_raja_yoga_pairs_from_planet_positions(planet_positions)
        print(chapter+'raja yoga pairs',ry_pairs)
        #p_to_h = utils.get_planet_to_house_dict_from_chart(chart_oprah_winfrey)
        for p1,p2 in ry_pairs:
            print(chapter+'neecha_bhanga_raja_yoga',p1,p2,neecha_bhanga_raja_yoga_from_planet_positions(planet_positions, p1, p2))
            print(chapter+'dharma_karmadhipati_raja_yoga',p1,p2,dharma_karmadhipati_raja_yoga_from_planet_positions(planet_positions, p1, p2))
        dob = (1965,12,27)
        tob = (14,30,0)
        place = drik.Place('unknown',33+3/60,-89-35/60,5.5)
        jd_at_dob = utils.julian_day_number(dob, tob)
        planet_positions = charts.rasi_chart(jd_at_dob, place)
        chart_salman_khan = ['0/2/5','','7','6','','','L/1','','8/4','','','3'] # For vipareetha rajacheck
        print(chapter+'chart_salman_khan',chart_salman_khan)
        ry_pairs = get_raja_yoga_pairs_from_planet_positions(planet_positions)
        print(chapter+'raja yoga pairs',ry_pairs)
        #p_to_h = utils.get_planet_to_house_dict_from_chart(chart_salman_khan)
        for p1,p2 in ry_pairs:
            print(chapter+'neecha_bhanga_raja_yoga',p1,p2,neecha_bhanga_raja_yoga_from_planet_positions(planet_positions, p1, p2))
            print(chapter+'vipareetha_raja_yoga',p1,p2,vipareetha_raja_yoga_from_planet_positions(planet_positions, p1, p2))
    raja_yoga_tests()
    exit()
