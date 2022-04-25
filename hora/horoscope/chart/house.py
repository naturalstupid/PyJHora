import swisseph as swe
from hora import const, utils
from hora.panchanga import panchanga
chara_karaka_names = ['atma_karaka','amatya_karaka','bhratri_karaka','maitri_karaka','pitri_karaka','putra_karaka','jnaati_karaka','data_karaka']
planet_list = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
rasi_names_en = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

get_relative_house_of_planet = lambda from_house, planet_house: (planet_house + 12 -from_house) % 12 + 1
strong_signs_of_planet = lambda planet,strength=const._FRIEND: [h for h in range(12) if const.house_strengths_of_planets[planet][h]==strength]
""" Get All trikona aspects of the given raasi"""
trikona_aspects_of_the_raasi = lambda raasi: [(raasi)%12, (raasi+4)%12, (raasi+8)%12]
trines_of_the_raasi = lambda raasi: trikona_aspects_of_the_raasi(raasi)

functional_benefic_lord_houses = lambda asc_house: trines_of_the_raasi(asc_house)
functional_malefic_lord_houses = lambda asc_house: [(asc_house+2)%12,(asc_house+5)%12,(asc_house+10)%12]
functional_neutral_lord_houses = lambda asc_house: [(asc_house+1)%12,(asc_house+7)%12,(asc_house+11)%12]

def is_yoga_kaaraka(asc_house,planet,planet_house):
    return planet_house in quadrants_of_the_raasi(asc_house) and planet_house in trines_of_the_raasi(asc_house) and \
            const.house_strengths_of_planets[planet][planet_house]==5

def trikonas():
    """ Get All trikonas of all houses """
    trikonas = []
    for house in range(12):
        trik = [house, trikona_aspects_of_the_raasi(house)]#[house,[(house)%12, (house+4)%12, (house+8)%12]]
        trik = [x+1 for x in trik[1]]
        trikonas.append(trik)
    return trikonas
""" Get All dushthana aspects of the given raasi"""
dushthana_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+2)%12, (raasi+6)%12]
dushthanas_of_the_raasi = lambda raasi: dushthana_aspects_of_the_raasi(raasi)
def dushthanas():
    """ Get All dushthanas of all houses """
    dushthanas = []
    for house in range(12):
        dust = [house, dushthana_aspects_of_the_raasi(house)] #[house,[(house)%12, (house+2)%12, (house+6)%12]]
        dust = [x+1 for x in dust[1]]
        dushthanas.append(dust)
    return dushthanas
""" Get All chathusra aspects of the given raasi"""
chathusra_aspects_of_the_raasi = lambda raasi:[(raasi+2)%12, (raasi+4)%12]    
chathusras_of_the_raasi = lambda raasi: chathusra_aspects_of_the_raasi(raasi)
def chathusras():
    """ Get All chathusras of all houses """
    chathusras = []
    for house in range(12):
        chat = [house, chathusra_aspects_of_the_raasi(house)] #[house,[(house)%12, (house+4)%12]]
        chat = [x+1 for x in chat[1]]
        chathusras.append(chat)
    return chathusras
""" Get All kendra aspects of the given raasi"""
kendra_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+3)%12, (raasi+6)%12,(raasi+9)%12]
quadrants_of_the_raasi = lambda raasi:kendra_aspects_of_the_raasi(raasi)
def quadrants():
    return kendras()
def kendras():
    """ Get All kendras of all houses """
    kendras = []
    for house in range(12):
        ken = [house, kendra_aspects_of_the_raasi(house)] #[house,[(house)%12, (house+3)%12, (house+6)%12,(house+9)%12]]
        ken = [x+1 for x in ken[1]]
        kendras.append(ken)
    return kendras
def aspected_kendras_of_raasi(raasi,reverse_direction=False):
    """ 
        @param raasi: 0 .. 11
        @param reverse_direction = True (default):  
        NOTE: !!! use reverse_direction=True only for some dhasa-bukthi such as drig dhasa !!!
        @return: aspected house numbers [1,4,7,10] with respect to the raasi
        NOTE: !!! Kendras return as 1..12 instead of 0..11. !!!
    """
    #ks = kendras()[raasi]
    rd = raasi_drishti[raasi]
    rd = [r for r in rd if r>raasi]+[r for r in rd if r<raasi]
    rdr = rd[:]
    if reverse_direction:
        rdr.reverse()
        rdr = [r for r in rdr if r<raasi]+[r for r in rdr if r>raasi]
    return rdr
""" Get All kendra aspects of the given raasi"""
upachaya_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+3)%12, (raasi+7)%12,(raasi+8)%12]    
upachayas_of_the_raasi = lambda raasi: upachaya_aspects_of_the_raasi(raasi)
def upachayas():
    """ Get All upachayas of all houses """
    upachayas = []
    for house in range(12):
        upa = [house,[(house)%12, (house+3)%12, (house+7)%12,(house+8)%12]]
        upa = [x+1 for x in upa[1]]
        upachayas.append(upa)
    return upachayas
def chara_karakas(jd,place,divisional_chart_factor=1):
    """
        get chara karakas for a dasa varga chart
        @param jd - juliday number for date of birth + time of birth
        @param place: panchanga.place struct(place,lat,long,timezone)
        @param divisional_chart_factor: 1=Rasi, 2=Hora...,9=Navamsa etc
        @return: chara karaka for all planets as a list. First element is Sun
    """
    planet_positions = panchanga.dhasavarga(jd,place,divisional_chart_factor,as_string=False)[:8]
    pp = [[i,row[-1][1]] for i,row in enumerate(planet_positions) ]
    one_rasi = 360.0/12/divisional_chart_factor
    pp[-1][-1] = one_rasi-pp[-1][-1]
    pp1 = sorted(pp,key=lambda x:  x[1],reverse=True)
    pp2 = {pi[0]:ci for ci,pi in enumerate(pp1)}
    pp2 = {**pp2, **{8:''}} # Append Kethu
    if const._INCLUDE_URANUS_TO_PLUTO:
        pp2 = {**pp2, **{9:'',10:'',11:''}} ## Append Uranus to Pluto
    return pp2
def graha_drishti_from_chart(house_to_planet_dict,separator='/'):
    h_to_p = house_to_planet_dict[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h['L']
    arp = {}
    ahp = {}
    app = {}
    for p,planet in enumerate(planet_list[:7]):
        house_of_the_planet = p_to_h[p]
        arp[p] = [(h+house_of_the_planet-1)%12 for h in const.graha_drishti[p]]
        ahp[p] = [ (h+asc_house-2) %12 for h in arp[p]]
        app[p] = sum([h_to_p[ar].replace('L','').split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
    return arp,ahp,app
def aspected_planets_of_the_planet(house_to_planet_dict,planet,separator='/'):
    _,_,app =  graha_drishti_from_chart(house_to_planet_dict,separator)
    return app[planet]
def _get_raasi_drishti_movable():
    raasi_drishti = {}
    for ms in const.movable_signs:
        rd = []
        for fs in const.fixed_signs:
            if fs != ms+1 and fs != ms-1:
                rd.append(fs)
        raasi_drishti[ms] = rd
    return raasi_drishti
def _get_raasi_drishti_fixed():
    raasi_drishti = {}
    for fs in const.fixed_signs:
        rd = []
        for ms in const.movable_signs:
            if ms != fs+1 and ms != fs-1:
                rd.append(ms)
        raasi_drishti[fs] = rd
    return raasi_drishti
def _get_raasi_drishti_dual():
    raasi_drishti = {}
    for fs in const.dual_signs:
        rd = []
        for ms in const.dual_signs:
            if fs != ms:
                rd.append(ms)
        raasi_drishti[fs] = rd
    return raasi_drishti
def _get_raasi_drishti():
    raasi_drishti = {**_get_raasi_drishti_movable(), **_get_raasi_drishti_fixed(), **_get_raasi_drishti_dual()}
    raasi_drishti = dict(sorted(raasi_drishti.items()))
    return raasi_drishti
raasi_drishti = _get_raasi_drishti()    
#print('raasi_drishti_map',raasi_drishti)
def raasi_drishti_from_chart(house_to_planet_dict,separator='/'):
    """ TODO: This does not find aspected planets of the Lagnam Raasi """
    h_to_p = house_to_planet_dict[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h['L']
    arp = {}
    ahp = {}
    app = {}
    for p,planet in enumerate(planet_list[:9]):
        arp[p] = raasi_drishti[p_to_h[p]]
        ahp[p] = [ (h+asc_house-2) %12 for h in arp[p]]
        #app[p] = sum([h_to_p[ar].replace('L','').split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = sum([h_to_p[ar].split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
    return arp,ahp,app
def aspected_rasis_of_the_planet(house_to_planet_dict,planet,separator='/'):
    arp,ahp,app = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    #print('arp',arp)
    #print('Raasi Drishti')
    #print('Planet\t\tAspected Raasis\t\tAspected Houses\t\tAspected Planets')
    #p = planet
    #pl = planet_list[p]
    #print(pl,'\t\t',','.join([rasi_names_en[arp] for arp in arp[p]]),'\t\t',','.join([rasi_names_en[arp] for arp in ahp[p]]),'\t\t',','.join([planet_list[int(pl)] for pl in app[p] if pl != '']))
    return arp[planet]
def aspected_planets_of_the_raasi(house_to_planet_dict,raasi,separator='/'):
    """
        get aspected planets of the given rasi from the chart
    """
    _,_,arp = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    #print('arp',arp,'for raasi',raasi)
    aspected_planets = [key for key,value in arp.items() if str(raasi) in value]
    #print(rasi_names_en[raasi],'aspected_planets',aspected_planets)
    return aspected_planets
def aspected_houses_of_the_raasi(house_to_planet_dict,raasi,separator='/'):
    """
        get aspected houses of the given rasi from the chart
    """
    _,ahp,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    #print('arp',arp)
    aspected_houses = [key for key,value in ahp.items() if str(raasi) in value]
    #print(rasi_names_en[raasi],'aspected_planets',aspected_planets)
    return aspected_houses
def aspected_raasis_of_the_raasi(house_to_planet_dict,raasi,separator='/'):
    """
        get aspected raasis of the given rasi from the chart
    """
    arr,_,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    #print('arr',arr)
    aspected_raasis = [key for key,value in arr.items() if str(raasi) in value]
    #print(rasi_names_en[raasi],'aspected_planets',aspected_planets)
    return aspected_raasis
def get_argala(house_to_planet_dict,separator='\n'):
    """
        Get argala and Virodhargala from the chart
    """
    h_to_p = house_to_planet_dict[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h['L']
    argala = [[h_to_p[(r+asc_house+a-1)%12].replace('L','').replace(separator,'/').replace('//','/') for a in const.argala_houses] for r in range(12)]
    #print(argala)
    virodhargala = [[h_to_p[(r+asc_house+a-1)%12].replace('L','').replace(separator,'/').replace('//','/') for a in const.virodhargala_houses] for r in range(12)]
    #print(virdohargala)
    return argala,virodhargala
def stronger_co_lord(house_to_planet_dict,planet1=swe.SATURN,planet2=swe.RAHU):
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
    """
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_dict)
    #print('p_to_h',p_to_h)
    """
    ### Validate planet inputs
    valid_input = (planet1 == 6 and planet2 == 7) or (planet1 == 2 and planet2 == 8)
    if not valid_input:
        print('Only accepted planet combinations are Saturn/Rahu or Mar/Ketu')
        return None  
    """
    planet1_house = p_to_h[planet1]
    #print('planet1',planet1,planet_list[planet1],'in house',planet1_house,rasi_names_en[planet1_house])
    planet2_house = p_to_h[planet2]
    #print('planet2',planet2,planet_list[planet2],'in house',planet2_house,rasi_names_en[planet2_house])
    lord_house_of_planets = const.houses_of_rahu_kethu[planet2]
    #print('lord_house_of_planets',lord_house_of_planets,rasi_names_en[lord_house_of_planets])
    """ Basic Rule - If Planet1/Saturn/Mars in Aq/Sc and Planet2/Rahu/Ketu elsewhere then Planet2/Rahu/Ketu is stronger """
    if (planet1_house==lord_house_of_planets and planet2_house != lord_house_of_planets):
        #print('Basic Rule','Planet2/Rahu/Ketu is stronger')
        return planet2
    if (planet2_house==lord_house_of_planets and planet1_house != lord_house_of_planets):
        #print('Basic Rule','Planet1/Saturn/Mars is stronger')
        return planet1
    """ Rule-1: If one planet is joined by more planets than the other, it is stronger. """
    planet1_co_planet_count = sum(value==planet1_house for value in p_to_h.values())
    #print('Rule-1','planet1_co_planet_count',planet1_co_planet_count)
    planet2_co_planet_count = sum(value==planet2_house for value in p_to_h.values())
    #print('Rule-1','planet2_co_planet_count',planet2_co_planet_count)
    if planet1_co_planet_count > planet2_co_planet_count:
        #print('Rule-1','Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_co_planet_count > planet1_co_planet_count:
        #print('Rule-1','Planet2/Rahu/Ketu is stronger')
        return planet2
    """ Rule-2: how many of the following planets conjoin/aspect a planet: (1) Jupiter,(2) Mercury, and, (3) dispositor. """
    # Dispositor of a planet = lord of the house where the planet is
    dispositor_of_planet1_house = const.house_owners[planet1_house]
    planet1_co_planet_count = sum( ((value==planet1_house) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==dispositor_of_planet1_house)) for value in p_to_h.values())
    #print('Rule-2','planet1_house',planet1_house,'dispositor_of_planet1_house',dispositor_of_planet1_house,'planet1_co_planet_count',planet1_co_planet_count)
    dispositor_of_planet2_house = const.house_owners[planet2_house]
    planet2_co_planet_count = sum( ((value==planet2_house) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==dispositor_of_planet2_house)) for value in p_to_h.values())
    #print('Rule-2','planet2_house',planet2_house,'dispositor_of_planet2_house',dispositor_of_planet2_house,'planet2_co_planet_count',planet2_co_planet_count)
    if planet1_co_planet_count > planet2_co_planet_count:
        #print('Rule-2','Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_co_planet_count > planet1_co_planet_count:
        #print('Rule-2','Planet2/Rahu/Ketu is stronger')
        return planet2
    """ Rule-3: If one planet is exalted and the other not, then the exalted planet is stronger. """
    #print('house_strengths_of_planet1',house_strengths_of_planets[planet1][planet1_house], 'house_strengths_of_planet2',house_strengths_of_planets[planet2][planet2_house])
    if const.house_strengths_of_planets[planet1][planet1_house] > const._FRIEND and \
        (const.house_strengths_of_planets[planet1][planet1_house] > const.house_strengths_of_planets[planet2][planet2_house]):
        #print('Rule-3','Planet1/Saturn/Mars is exhalted and thus stronger')
        return planet1
    if const.house_strengths_of_planets[planet2][planet2_house] > const._FRIEND and \
        (const.house_strengths_of_planets[planet2][planet2_house] > const.house_strengths_of_planets[planet2][planet2_house]):
        #print('Rule-3','Planet2/Rahu/Ketu is exhalted and thus stronger')
        return planet2
    """ Rule - 4: natural strength of the rasi containing the planet. 
        Dual rasis are stronger than fixed rasis and fixed rasis are stronger than movable rasis.
    """
    if planet1_house in const.dual_signs and planet2_house not in const.dual_signs:
            #print('Rule-4','Planet1/Saturn/Mars is stronger')
            return planet1
    elif planet1_house in const.fixed_signs:
        if planet2_house in const.dual_signs:
            #print('Rule-4','Planet2/Rahu/Ketu is stronger')
            return planet2
        elif planet2_house in const.movable_signs: 
            #print('Rule-4','Planet1/Saturn/Mars is stronger')
            return planet1
    else: # Saturn/Mars in movable
        if planet2_house not in const.movable_signs:
            #print('Rule-4','Planet2/Rahu/Ketu is stronger')
            return planet2
    """ Rule-5-a, planet giving a larger length for narayana dhasa"""
    import narayana 
    planet1_narayana_dhasa_duration = narayana._dhasa_duration(p_to_h,planet1_house)
    #print('planet1_narayana_dhasa_duration',planet1_narayana_dhasa_duration)
    planet2_narayana_dhasa_duration = narayana._dhasa_duration(p_to_h,planet2_house)
    #print('planet2_narayana_dhasa_duration',planet2_narayana_dhasa_duration)
    if planet1_narayana_dhasa_duration > planet2_narayana_dhasa_duration:
        #print('Rule-5: Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_narayana_dhasa_duration > planet1_narayana_dhasa_duration:
        #print('Rule-5: Planet2/Rahu/Ketu is stronger')
        return planet2
def stronger_rasi(house_to_planet_dict,rasi1,rasi2):
    """
        To find stronger rasi between rasi1 and rasi2 
    """
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_dict)
    #print(p_to_h)
    """ Rule-1 rasi contains more planets than the other rasi, then it is stronger. """
    rasi1_planet_count = sum(value==rasi1 for key,value in p_to_h.items() if key != 'L')
    #print('Rule-1',rasi1,'rasi1_planet_count',rasi1_planet_count)
    rasi2_planet_count = sum(value==rasi2 for key,value in p_to_h.items() if key != 'L')
    #print('Rule-1',rasi2,'rasi2_planet_count',rasi2_planet_count)
    if rasi1_planet_count > rasi2_planet_count:
        #print('Rule-1 Rasi1',rasi1,'is stronger')
        return rasi1
    if rasi2_planet_count > rasi1_planet_count:
        #print('Rule-1 Rasi2',rasi2,'is stronger')
        return rasi2
    """ Rule-2: how many of the following planets in/aspecting the rasi: (1) Jupiter,(2) Mercury, and, (3) dispositor. """
    # Dispositor of a planet = lord of the house where the planet is
    lord_of_rasi1 = const.house_owners[rasi1]
    if rasi1 in [7,10]: ## If rasi1 is Aq or Sc there are two lords
        rahu_kethu_house = list(const.houses_of_rahu_kethu.keys())[list(const.houses_of_rahu_kethu.values()).index(rasi1)]
        #print('rahu_kethu_house of rasi2',rahu_kethu_house)
        lord_of_rasi1 = const.house_owners[stronger_co_lord(house_to_planet_dict, lord_of_rasi1,rahu_kethu_house)]
    rasi1_planet_count = sum( ((value==rasi1) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==lord_of_rasi1)) for key,value in p_to_h.items() if key != 'L')
    #print('Rule-2','rasi1',rasi1,'lord_of_rasi1',lord_of_rasi1,'rasi1_planet_count',rasi1_planet_count)
    rasi1_planet_count += len(set([3,4,lord_of_rasi1]) & set(aspected_planets_of_the_raasi(house_to_planet_dict,rasi1, separator='/')))
    #print('Rule-2','rasi1',rasi1,'lord_of_rasi1',lord_of_rasi1,'rasi1_planet_count incl aspects',rasi1_planet_count)
    lord_of_rasi2 = const.house_owners[rasi2]
    if rasi2 in [7,10]: ## If rasi1 is Aq or Sc there are two lords
        rahu_kethu_house = list(const.houses_of_rahu_kethu.keys())[list(const.houses_of_rahu_kethu.values()).index(rasi2)]
        #print('rahu_kethu_house of rasi2',rahu_kethu_house)
        lord_of_rasi2 = const.house_owners[stronger_co_lord(house_to_planet_dict, lord_of_rasi2,rahu_kethu_house)]
    rasi2_planet_count = sum( ((value==rasi2) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==lord_of_rasi2)) for key,value in p_to_h.items() if key != 'L')
    
    #print('Rule-2','rasi2',rasi2,'lord_of_rasi2',lord_of_rasi2,'rasi2_planet_count',rasi2_planet_count)
    rasi2_planet_count += len(set([3,4,lord_of_rasi2]) & set(aspected_planets_of_the_raasi(house_to_planet_dict,rasi2, separator='/')))
    #print('Rule-2','rasi2',rasi2,'lord_of_rasi2',lord_of_rasi2,'rasi2_planet_count incl aspects',rasi2_planet_count)
    if rasi1_planet_count > rasi2_planet_count:
        #print('Rule-2 Rasi1',rasi1,'is stronger')
        return rasi1
    elif rasi2_planet_count > rasi1_planet_count:
        #print('Rule-2 Rasi2',rasi2,'is stronger')
        return rasi2
    """ Rule-3: If one rasi contains an exalted planet and the other does not, then the former rasi is stronger."""
    rasi1_exhalted_planet_count = sum([const.house_strengths_of_planets[int(p)][rasi1] > const._FRIEND for p in p_to_h if p!= 'L' and p_to_h[p]==rasi1])
    #print('Rule-3','rasi1_exhalted_planet_count',rasi1_exhalted_planet_count)
    rasi2_exhalted_planet_count = sum([const.house_strengths_of_planets[int(p)][rasi2] > const._FRIEND for p in p_to_h if p!= 'L' and p_to_h[p]==rasi2])
    #print('Rule-3','rasi2_exhalted_planet_count',rasi2_exhalted_planet_count)
    """ Rule - 4: A rasi whose lord is in a rasi with a different oddity (odd/even) is stronger than a
                    rasi whose lord is in a rasi with the same oddity. """
    rasi1_has_oddity = (rasi1 in const.odd_signs and lord_of_rasi1 in const.even_signs) or (rasi1 in const.even_signs and lord_of_rasi1 in const.odd_signs)
    rasi2_has_oddity = (rasi2 in const.odd_signs and lord_of_rasi2 in const.even_signs) or (rasi2 in const.even_signs and lord_of_rasi2 in const.odd_signs)
    #print('Rule-4','rasi1_has_oddity',rasi1_has_oddity,'rasi2_has_oddity',rasi2_has_oddity)
    if rasi1_has_oddity:
        #print('Rule-4:rasi1',rasi1,'has oddity and thus stronger')
        return rasi1
    if rasi2_has_oddity:
        #print('Rule-4:rasi2',rasi2,'has oddity and thus stronger')
        return rasi2
    """ Rule - 5: natural strength of the rasi. 
        Dual rasis are stronger than fixed rasis and fixed rasis are stronger than movable rasis.
    """
    if rasi1 in const.dual_signs and rasi2 not in const.dual_signs:
        #print('Rule-5 rasi1',rasi1,'is stronger')
        return rasi1
    elif rasi1 in const.fixed_signs:
        if rasi2 in const.dual_signs:
            #print('Rule-5 rasi2',rasi2,'is stronger')
            return rasi2
        elif rasi2 in const.movable_signs: 
            #print('Rule-5 rasi1',rasi1,'is stronger')
            return rasi1
    else: # Saturn/Mars in movable
        if rasi2 not in const.movable_signs:
            #print('Rule-5 rasi2',rasi2,'is stronger')
            return rasi2
    """ Rule-6: The rasi owned by the planet with the higher advancement of longitude is stronger. """
    """ TODO """
if __name__ == "__main__":
    print(const.planet_deep_debilitation_longitudes)
    exit()
    print(raasi_drishti)
    for r in range(12):
        rd = aspected_kendras_of_raasi(r)
        rdr = aspected_kendras_of_raasi(r,True)
        print('raasi',r,rasi_names_en[r],rd,rdr)
    exit()
    #h_to_p = ['1','0','','','7','4','','2/L/6','3','5','8','']
    #h_to_p= ['', '', '', '', '2\n', '7\n', '1\n5\n', '0\n', '3\n4\n', 'L\n', '', '6\n8\n']
    #chart_12 = ['8','5','','','','L','7','2/4','3/1','0','','6']
    place = panchanga.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    dob = panchanga.Date(1996,12,7)
    tob = (10,34,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd = swe.julday(dob.year,dob.month,dob.day, time_of_birth_in_hours)
    divisional_chart_factor = 1
    ascendant_index = 'L'
    planet_positions = panchanga.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = panchanga.ascendant(jd,place,as_string=False)[1]
    asc_house,asc_long = panchanga.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[ascendant_index,(asc_house,asc_long)]]
    house_to_planet_dict = ['' for h in range(12)] 
    for sublist in planet_positions:
        p = sublist[0]
        h = sublist[1][0]
        house_to_planet_dict[h] += str(p) + '/'
    #h_to_p = ['1','0','','','7','4','','L/2/6','3','5','8','']
    print('h_to_p\n',house_to_planet_dict)
    print(stronger_rasi(house_to_planet_dict,6,8))
    exit()
    #p_to_h = get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h\n',p_to_h)
    stronger_co_lord(house_to_planet_dict,6,7)
    stronger_co_lord(house_to_planet_dict,2,8)
    exit()
    arp,ahp,app = raasi_drishti_from_chart(house_to_planet_dict)
    print('Raasi Drishti')
    print('Planet\t\tAspected Raasis\t\tAspected Houses\t\tAspected Planets')
    for p,planet in enumerate(planet_list[:9]):
        print(planet,'\t\t',','.join([rasi_names_en[arp] for arp in arp[p]]),'\t\t',','.join([rasi_names_en[arp] for arp in ahp[p]]),'\t\t',','.join([planet_list[int(pl)] for pl in app[p] if pl != '']))
    #exit()
    arp,ahp,app = graha_drishti_from_chart(house_to_planet_dict)
    print('\nGriha Drishti')
    print('Planet\t\tAspected Raasis\t\tAspected Houses\t\tAspected Planets')
    for p,planet in enumerate(planet_list[:7]):
        print(planet,'\t\t',','.join([rasi_names_en[arp] for arp in arp[p]]),'\t\t',','.join([rasi_names_en[arp] for arp in ahp[p]]),'\t\t',','.join([planet_list[int(pl)] for pl in app[p] if pl != '']))
    exit()
    ck = chara_karakas(jd, place, 1, as_string=False)
    print('chara_karakas',ck)
    print('trikonas',trikonas())
    print('kendras',kendras())
    print('upachayas',upachayas())        
    print('dushthanas',dushthanas())
    print('chathusras',chathusras())