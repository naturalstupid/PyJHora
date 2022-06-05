import itertools
from hora import const,utils
from hora.horoscope.chart import house
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
lords_of_quadrants = lambda raasi:[const.house_owners[h] for h in house.quadrants_of_the_raasi(raasi)]
lords_of_trines = lambda raasi:[const.house_owners[h] for h in house.trines_of_the_raasi(raasi)]
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
    chk3 = (lord1 == const.house_owners[p_to_h[lord2]]) and (lord2 == const.house_owners[p_to_h[lord1]])
    #print('parivarthana',lord1,const.house_owners[p_to_h[lord2]],lord2,const.house_owners[p_to_h[lord1]])
    return chk1 or chk2 or chk3
def __check_association(h_to_p,planet1,planet2):
    if planet1 == planet2:
        return False
    #print('raja yoga check ',planet1,planet2)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h['L']
    planet1_lord = const.house_owners[planet1]
    planet1_house = p_to_h[planet1]
    #print('planet1,lord,house',planet1,planet1_lord,planet1_house)
    planet2_lord = const.house_owners[planet2]
    planet2_house = p_to_h[planet2]
    #print('planet2,lord,house',planet2,planet2_lord,planet2_house)
    quadrant_lords = lords_of_quadrants(asc_house)
    trine_lords = lords_of_trines(asc_house)
    """ TODO: check if lords in the quad / trine houses """
    chk0 = (planet1_house in house.quadrants_of_the_raasi(asc_house) and planet2_house in house.trines_of_the_raasi(asc_house)) or \
           (planet2_house in house.quadrants_of_the_raasi(asc_house) and planet1_house in house.trines_of_the_raasi(asc_house))
    #print('lords in quad/trine',planet1,planet1_house, house.quadrants_of_the_raasi(asc_house),planet2,planet2_house,house.trines_of_the_raasi(asc_house),\
    #            planet2,planet2_house, house.quadrants_of_the_raasi(asc_house),planet1,planet1_house,house.trines_of_the_raasi(asc_house),chk0)
    chk1 = p_to_h[planet1] == p_to_h[planet2]
    #print('chk1',p_to_h[planet1],p_to_h[planet2],'conjoined check',chk1)
    #""" TODO: Change this to graha drishti """
    chk2 = str(planet2) in house.graha_drishti_of_the_planet(h_to_p, planet1) or \
           str(planet1) in house.graha_drishti_of_the_planet(h_to_p, planet2) 
    #print('chk2',planet2,house.graha_drishti_of_the_planet(h_to_p, planet1),'aspect check',chk2)
    chk3 = planet1_house == p_to_h[planet2_lord] and planet2_house == p_to_h[planet1_lord]
    #print('chk3',planet1_house,p_to_h[planet2_lord],planet2_house,p_to_h[planet1_lord],'exchange check',chk3)
    return chk1 or chk2 or chk3  
def dharma_karmadhipati_yoga(p_to_h,raja_yoga_planet1,raja_yoga_planet2):
    """ 
        Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords
        of dharma sthana (9th) and karma sthana (10th) form a raja yoga 
        @param p_to_h: planet_to_house dictionary Example: {0:1,1:2,...'L':11,..} Sun in Ar, Moon in Ta, Lagnam in Pi
        @param raja_yoga_planet1: Planet index for first raja yoga planet  [0 to 6] Rahu/Kethu/Lagnam not supported
        @param raja_yoga_planet2: Planet index for second raja yoga planet [0 to 6] Rahu/Kethu/Lagnam not supported
        @return: True/False = True = dharma karmadhipati yoga is present
    """
    asc_house = p_to_h['L']
    house_lords = [const.house_owners[h] for h in [(asc_house+8)%12,(asc_house+9)%12]]
    dkchk = all([any([hl == rp for hl in house_lords ]) for rp in [raja_yoga_planet1, raja_yoga_planet2] ])
    #print('dharma_karmadhipati_yoga check',dkchk)
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
    asc_house = p_to_h['L']
    lq = set(lords_of_quadrants(asc_house))
    lt = set(lords_of_trines(asc_house))
    possible_pairs =  [(q,l) for i,q in enumerate(lq) for j,l in enumerate(lt) if q !=l and (q,l)!=(l,q)]
    possible_pairs = list(set(tuple(sorted(x)) for x in possible_pairs))
    #print('possible_pairs',possible_pairs)
    raja_yoga_pairs = []
    for p1,p2 in possible_pairs:
        p1_raasi = p_to_h[p1]
        p1_house = (p1_raasi+12-asc_house)%12
        p1_rasi_lord = const.house_owners[p1_raasi]
        #print('\n','planet',p1,house.planet_list[p1],'raasi lord',house.planet_list[p1_rasi_lord],'house',p1_house,'strength',const.house_strengths_of_planets[p1][p1_raasi])
        p2_raasi = p_to_h[p2]
        p2_house = (p2_raasi+12-asc_house)%12
        p2_rasi_lord = const.house_owners[p2_raasi]
        #print('planet',p2,house.planet_list[p2],'raasi lord',house.planet_list[p2_rasi_lord],'house',p2_house,'strength',const.house_strengths_of_planets[p2][p2_raasi])
        chk = _check_association(house_to_planet_list, p1, p2)
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
    asc_house = p_to_h['L']
    house_lords = [const.house_owners[h] for h in [(asc_house+5)%12,(asc_house+7)%12,(asc_house+11)%12]]
    vrchk1 = ([([p_to_h[rp]==dh for dh in house.dushthanas_of_the_raasi(asc_house)]) \
              for rp in [raja_yoga_planet1, raja_yoga_planet2]])
    vrchk = (all([any(vrchk1[0]),any(vrchk1[1])]))
    vr_sub_type = 'Harsh Raja Yoga'
    if vrchk1[0][1]:
        vr_sub_type = 'Saral Raja Yoga'
    elif vrchk1[0][2]:
        vr_sub_type = 'Vimal Raja Yoga'
    #print('vipareetha_raja_yoga check',vrchk,vr_sub_type)
    return vrchk, vr_sub_type
def neecha_bhanga_raja_yoga(house_to_planet_list,raja_yoga_planet1, raja_yoga_planet2):
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
    "TODO: Rule 4 and 5. Get jd,place as inputs "
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_list)
    rp1_rasi = p_to_h[raja_yoga_planet1]
    rp2_rasi = p_to_h[raja_yoga_planet2]
    rp1_lord = const.house_owners[rp1_rasi]
    rp2_lord = const.house_owners[rp2_rasi]
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
if __name__ == "__main__":
    chart_10_akbar = ['','','1','','8','','4/5/6/L','0','3','2','7','']
    #print('chart_10_akbar',chart_10_akbar)
    chart_15_rajiv_gandhi = ['', '', '6', '7', 'L/0/1/3/4/5', '2', '', '', '', '8', '', '']
    #print('chart_15_rajiv_gandhi',chart_15_rajiv_gandhi)
    chart_oprah_winfrey = ['','4','','8','','','6','1/2','','0/3/5/L/7','',''] # For dharma karmadhipathi check
    chart_salman_khan = ['0/2/5','','7','6','','','L/1','','8/4','','','3'] # For vipareetha rajacheck
    chart = chart_10_akbar#chart_oprah_winfrey #chart_15_rajiv_gandhi #chart_10_akbar #chart_salman_khan
    print('chart',chart)
    ry_pairs = get_raja_yoga_pairs(chart)
    print(ry_pairs)
    exit()
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart)
    asc_house = p_to_h['L']
    print('p_to_h,asc_house',p_to_h,asc_house)
    lagna_lord = const.house_owners[asc_house]
    #print('asc_house',asc_house,'lagna lord',lagna_lord)
    #lq = set(lords_of_quadrants(asc_house))
    #print('quadrants_of_the_lagna',house.quadrants_of_the_raasi(asc_house),'lords_of_quadrants',lq)
    #print(house.trines_of_the_raasi(asc_house))
    #lt = set(lords_of_trines(asc_house))
    #print('trines_of_the_lagna',house.trines_of_the_raasi(asc_house),'lords_of_trines',lt)
    #comb =  [(q,l) for i,q in enumerate(lq) for j,l in enumerate(lt) if q !=l and (q,l)!=(l,q)]
    comb = [(q,l) for q in range(7) for l in range(7) if q != l and (q,l) != (l,q)]
    comb = list(set(tuple(sorted(x)) for x in comb))
    #print('combinations',comb)
    for p1,p2 in comb:
        p1_raasi = p_to_h[p1]
        p1_house = (p1_raasi+12-asc_house)%12
        p1_rasi_lord = const.house_owners[p1_raasi]
        #print('\n','planet',p1,house.planet_list[p1],'raasi lord',house.planet_list[p1_rasi_lord],'house',p1_house,'strength',const.house_strengths_of_planets[p1][p1_raasi])
        p2_raasi = p_to_h[p2]
        p2_house = (p2_raasi+12-asc_house)%12
        p2_rasi_lord = const.house_owners[p2_raasi]
        #print('planet',p2,house.planet_list[p2],'raasi lord',house.planet_list[p2_rasi_lord],'house',p2_house,'strength',const.house_strengths_of_planets[p2][p2_raasi])
        #"""
        chk = __check_association(chart, p1, p2)
        if chk:
            print('raja yoga pair',p1,p2,chk,'\n')
            dharma_karmadhipati_yoga(p_to_h,p1,p2)
            vipareetha_raja_yoga(p_to_h,p1,p2)
        #"""