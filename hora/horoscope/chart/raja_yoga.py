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
def _check_association(h_to_p,planet1,planet2):
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
    chk2 = planet2 in house.aspected_planets_of_the_planet(h_to_p, planet1)
    #print('chk2',planet2,house.aspected_planets_of_the_planet(h_to_p, planet1),'aspect check',chk2)
    chk3 = planet1_house == p_to_h[planet2_lord] and planet2_house == p_to_h[planet1_lord]
    #print('chk3',planet1_house,p_to_h[planet2_lord],planet2_house,p_to_h[planet1_lord],'exchange check',chk3)
    return chk1 or chk2 or chk3  
def dharma_karmadhipati_yoga(p_to_h,raja_yoga_planet1,raja_yoga_planet2):
    """ Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords
        of dharma sthana (9th) and karma sthana (10th) form a raja yoga """
    asc_house = p_to_h['L']
    house_lords = [const.house_owners[h] for h in [(asc_house+8)%12,(asc_house+9)%12]]
    dkchk = all([any([hl == rp for hl in house_lords ]) for rp in [raja_yoga_planet1, raja_yoga_planet2] ])
    print('dharma_karmadhipati_yoga check',dkchk)
    return dkchk  
    
def basic_raja_yoga(h_to_p,p_to_h,asc_house):
    pass
def vipareetha_raja_yoga(p_to_h,raja_yoga_planet1,raja_yoga_planet2):
    """ Vipareeta Raaja Yoga: The 6th, 8th and 12th houses are known as trik sthanas or
        dusthanas (bad houses). If their lords occupies dusthanas or conjoin dusthanas """
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
    print('vipareetha_raja_yoga check',vrchk,vr_sub_type)
    return vrchk  

if __name__ == "__main__":
    chart_10_akbar = ['','','1','','8','','4/5/6/L','0','3','2','7','']
    #print('chart_10_akbar',chart_10_akbar)
    chart_15_rajiv_gandhi = ['', '', '6', '7', 'L/0/1/3/4/5', '2', '', '', '', '8', '', '']
    #print('chart_15_rajiv_gandhi',chart_15_rajiv_gandhi)
    chart_oprah_winfrey = ['','4','','8','','','6','1/2','','0/3/5/L/7','',''] # For dharma karmadhipathi check
    chart_salman_khan = ['0/2/5','','7','6','','','L/1','','8/4','','','3'] # For vipareetha rajacheck
    chart = chart_salman_khan#chart_oprah_winfrey #chart_15_rajiv_gandhi #chart_10_akbar
    print('chart',chart)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart)
    asc_house = p_to_h['L']
    print('p_to_h,asc_house',p_to_h,asc_house)
    lagna_lord = const.house_owners[asc_house]
    print('asc_house',asc_house,'lagna lord',lagna_lord)
    lq = set(lords_of_quadrants(asc_house))
    print('quadrants_of_the_lagna',house.quadrants_of_the_raasi(asc_house),'lords_of_quadrants',lq)
    print(house.trines_of_the_raasi(asc_house))
    lt = set(lords_of_trines(asc_house))
    print('trines_of_the_lagna',house.trines_of_the_raasi(asc_house),'lords_of_trines',lt)
    comb =  [(q,l) for i,q in enumerate(lq) for j,l in enumerate(lt) if q !=l and (q,l)!=(l,q)]
    comb = list(set(tuple(sorted(x)) for x in comb))
    print('combinations',comb)
    for p1,p2 in comb:
        p1_raasi = p_to_h[p1]
        p1_house = (p1_raasi+12-asc_house)%12
        p1_rasi_lord = const.house_owners[p1_raasi]
        print('\n','planet',p1,house.planet_list[p1],'raasi lord',house.planet_list[p1_rasi_lord],'house',p1_house,'strength',const.house_strengths_of_planets[p1][p1_raasi])
        p2_raasi = p_to_h[p2]
        p2_house = (p2_raasi+12-asc_house)%12
        p2_rasi_lord = const.house_owners[p2_raasi]
        print('planet',p2,house.planet_list[p2],'raasi lord',house.planet_list[p2_rasi_lord],'house',p2_house,'strength',const.house_strengths_of_planets[p2][p2_raasi])
        #"""
        chk = _check_association(chart, p1, p2)
        if chk:
            print('raja yoga pair',p1,p2,chk,'\n')
            dharma_karmadhipati_yoga(p_to_h,p1,p2)
            vipareetha_raja_yoga(p_to_h,p1,p2)
        #"""