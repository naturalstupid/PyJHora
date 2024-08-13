from hora import const, utils
from hora.panchanga import drik
chara_karaka_names = const.chara_karaka_names
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
    """
        Check if a planet is yoga kaaraka
        @param asc_house: Raasi index of Lagnam (0=Aries, 11=Pisces)
        @param planet: Index of Planet  (0=Sun, 8=Kethu)
        @param planet_house: Raasi index of where planet is (0=Aries, 11=Pisces)
        @return: True/False whether planet is yoga kaaraka or not
    """
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
        @param reverse_direction = True/False (default=False):  
        NOTE: !!! use reverse_direction=True only for some dhasa-bukthi such as drig dhasa !!!
        @return: aspected house numbers [1,4,7,10] with respect to the raasi
        NOTE: !!! Kendras return as 1..12 instead of 0..11. !!!
    """
    #ks = kendras()[raasi]
    rd = _get_raasi_drishti()[raasi]
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
def chara_karakas(planet_positions):
    """
        get chara karakas for a dasa varga chart
        @param jd - juliday number for date of birth + time of birth
        @param place: drik.place struct(place,lat,long,timezone)
        @param divisional_chart_factor: 1=Rasi, 2=Hora...,9=Navamsa etc
        @return: chara karakas as a list. First element planet_index that is Atma Karaka etc
                ['atma_karaka','amatya_karaka','bhratri_karaka','maitri_karaka','pitri_karaka','putra_karaka',
                'jnaati_karaka','data_karaka']
    """
    #print(planet_positions)
    pp = [[i,row[-1][1]] for i,row in enumerate(planet_positions[1:9]) ]
    one_rasi = 360.0/12#/divisional_chart_factor
    pp[-1][-1] = one_rasi-pp[-1][-1]
    pp1 = sorted(pp,key=lambda x:  x[1],reverse=True)
    #print('sorted by long',pp1)
    pp2 = [pi[0] for _,pi in enumerate(pp1)]
    return pp2
def graha_drishti_from_chart(house_to_planet_dict,separator='/'):
    """
        get graha drishti from the chart positions of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param separator: separator character used separate planets in a house
        @return: arp, ahp, app
            Each tuple item is a 2D List
            arp = planets' graha drishti on raasis. Example: [[0,1,],...]] Sun has graha drishti in Aries and Tauras
            ahp = planets' graha drishti on houses. Example: [[0,1,],...]] Sun has graha drishti in 1st and 2nd houses
            app = planets' graha drishti on planets. Example: [[1,2,],...]] Sun has graha drishti on Moon and Mars
    """
    h_to_p = house_to_planet_dict[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    arp = {}
    ahp = {}
    app = {}
    for p,_ in enumerate(planet_list):#[:7]):
        house_of_the_planet = p_to_h[p]
        arp[p] = [(h+house_of_the_planet-1)%12 for h in const.graha_drishti[p]]
        ahp[p] = [ (h-asc_house)%12+1 for h in arp[p]]
        app[p] = sum([h_to_p[ar].replace(const._ascendant_symbol,'').split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = [int(pp) for pp in app[p] if pp != '' ]
    return arp,ahp,app
def graha_drishti_of_the_planet(house_to_planet_dict,planet,separator='/'):
    """
        Get graha drishti of a planet on other planets. 
            returns list of planets on which given planet has graha drishti
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet: The index of the planet for which graha drishti is sought (0=Sun, 9-Ketu, 'L'=Lagnam) 
        @param separator: separator character used separate planets in a house
        @return: graha drishti of the planet as a list of planets
    """
    #_,_,app =  graha_drishti_from_chart(house_to_planet_dict,separator)
    #"""
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_dict)
    _,_,app =  graha_drishti_from_chart(house_to_planet_dict,separator)
    #print(planet,'graha drishi of planets',app[planet])
    arp,_,app1 = raasi_drishti_from_chart(house_to_planet_dict)
    #print('rasi drishti of rasis',arp)
    #print(planet,'rasi drishi of planets',app1[planet])
    app[planet] += app1[planet]
    #print(planet,'combined drishti of planets',app[planet])
    #print('arp',arp)
    ppd = {}
    hl = arp[planet]
    hp = p_to_h[planet]
    #print('planet',planet,'its rasi',p_to_h[planet],'its rasi drishti from its house',hl)
    pp = []
    for h in hl:
        pl = house_to_planet_dict[(h+hp-1)%12].split('/')
        pp += [int(p1) for p1 in pl if p1 not in ['','L']]
        #print(planet,hp, h,pl,pp)
    ppd[planet] = pp+app[planet]
    return ppd[planet]
    #"""
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
    #print('movable rasi drishti',_get_raasi_drishti_movable())
    #print('fixed rasi drishti',_get_raasi_drishti_fixed())
    #print('dual rasi drishti',_get_raasi_drishti_dual())
    _raasi_drishti = {**_get_raasi_drishti_movable(), **_get_raasi_drishti_fixed(), **_get_raasi_drishti_dual()}
    _raasi_drishti = dict(sorted(_raasi_drishti.items()))
    return _raasi_drishti
#raasi_drishti = _get_raasi_drishti()    
#print('raasi_drishti_map',raasi_drishti)
def raasi_drishti_from_chart(house_to_planet_dict,separator='/'):
    """
        get raasi drishti from the chart positions of the planet
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param separator: separator character used separate planets in a house
        @return: arp, ahp, app
            Each tuple item is a 2D List
            arp = raasis' graha drishti on raasis. Example: [[1,2,],...]] Aries has raasi drishti in Tauras and Gemini
            ahp = raasis' graha drishti on houses. Example: [[1,2,],...]] 1st house/Lagnam has raasi drishti in 2nd and 3rd houses
            app = raasis' graha drishti on planets. Example: [[1,2,],...]] Aries has graha raasi on Moon and Mars
    """
    h_to_p = house_to_planet_dict[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    rd = _get_raasi_drishti()
    #print('raasi drishti',rd)
    arp = {}
    #print('rasi drishti',_get_raasi_drishti())
    ahp = {}
    app = {}
    for p,_ in enumerate(planet_list[:9]):
        ph = p_to_h[p]
        #print(p,'its rasi',ph,'its aspected rasi',rd[ph])
        arp[p] = rd[ph] #rd[p_to_h[p]] # raasi_drishti[p_to_h[p]]
        ahp[p] = [ (h-asc_house) %12+1 for h in arp[p]]
        #app[p] = sum([h_to_p[ar].replace(const._ascendant_symbol,'').split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = sum([h_to_p[ar].split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = [int(pp) for pp in app[p] if pp != '' and pp != const._ascendant_symbol]
    return arp,ahp,app
def raasi_drishti_of_the_planet(house_to_planet_dict,planet,separator='/'):
    arp,_,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    return arp[planet]
def aspected_planets_of_the_planet(house_to_planet_dict,planet,separator='/'):
    """
        Uses Graha Drishti
        @return: list of planets aspected by the input planet
    """
    _,_,app = graha_drishti_from_chart(house_to_planet_dict, separator)
    #print('app',app)
    aspected_planets = utils.flatten_list([map(int,value) for key,value in app.items() if planet == key])
    return aspected_planets
def aspected_rasis_of_the_planet(house_to_planet_dict,planet,separator='/'):
    """
        Uses Graha Drishti
        @return: list of raasis aspected by the input planet
    """
    arp,_, = graha_drishti_from_chart(house_to_planet_dict, separator)
    aspected_rasis = utils.flatten_list([map(int,value) for key,value in arp.items() if planet == key])
    return aspected_rasis
def aspected_houses_of_the_planet(house_to_planet_dict,planet,separator='/'):
    """
        Uses Graha Drishti
        @return: list of houses aspected by the input planet
    """
    _,ahp,_ = graha_drishti_from_chart(house_to_planet_dict, separator)
    aspected_houses = utils.flatten_list([map(int,value) for key,value in ahp.items() if planet == key])
    return aspected_houses
def aspected_planets_of_the_raasi(house_to_planet_dict,raasi,separator='/'):
    """
        get planets, from the raasi drishti from the chart, that has drishti on the given raasi
    """
    arp,_,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    aspected_planets = [key for key,value in arp.items() if raasi in value]
    return aspected_planets
def aspected_houses_of_the_raasi(house_to_planet_dict,raasi,separator='/'):
    """
        get aspected houses of the given rasi from the chart
    """
    _,ahp,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    aspected_houses = [key for key,value in ahp.items() if str(raasi) in value]
    return aspected_houses
def aspected_raasis_of_the_raasi(house_to_planet_dict,raasi,separator='/'):
    """
        get aspected raasis of the given rasi from the chart
    """
    arr,_,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    aspected_raasis = [key for key,value in arr.items() if str(raasi) in value]
    return aspected_raasis
def get_argala(house_to_planet_dict,separator='\n'):
    """
        Get argala and Virodhargala from the chart
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param separator: separator character used separate planets in a house
        @return argala,virodhargala
            argala = list of houses each planet causing argala - 2D List [ [0,2]..]] Sun causing argala in Ar and Ge
            virodhargala = list of houses each planet causing virodhargala - 2D List [ [0,2]..]] Sun causing virodhargala in Ar and Ge
    """
    h_to_p = house_to_planet_dict[:]
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    argala = [[h_to_p[(r+asc_house+a-1)%12].replace(const._ascendant_symbol,'').replace(separator,'/').replace('//','/') for a in const.argala_houses] for r in range(12)]
    virodhargala = [[h_to_p[(r+asc_house+a-1)%12].replace(const._ascendant_symbol,'').replace(separator,'/').replace('//','/') for a in const.virodhargala_houses] for r in range(12)]
    return argala,virodhargala
def stronger_planet_from_planet_positions(planet_positions,planet1=const._SATURN,planet2=7,check_during_dhasa=False):
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @param planet1 and planet2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
          Default: planet1=6 (Saturn) and planet2=7 (Rahu)
        @param check_during_dhasa True/False. Set this to True if checking for dhasa-bhukthi
        @return stronger of planet1 and planet2
            Stronger of Rahu/Saturn or Ketu/Mars is returned
    """
    _debug_print = False
    if planet1==planet2:
        return planet1
    house_to_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    stronger_planet = _stronger_planet_new(house_to_planet_dict,planet1,planet2)
    if stronger_planet is not None:
        return stronger_planet
    if _debug_print: print("Rule-4: Both planets are in same type of rasi Dual/fixed/movable - and are equally stronger")
    planet1_house = p_to_h[planet1]
    planet1_longitude = planet_positions[planet1+1][1][1] # +1 to inlcude first element 'L'
    planet2_house = p_to_h[planet2]
    planet2_longitude = planet_positions[planet2+1][1][1]
    if check_during_dhasa:
        """ Rule-5-a, planet giving a larger length for narayana dhasa"""
        from hora.horoscope.dhasa.raasi import narayana 
        planet1_narayana_dhasa_duration = narayana._dhasa_duration(planet_positions,planet1_house)
        if _debug_print: print('planet1_narayana_dhasa_duration',planet1_narayana_dhasa_duration)
        planet2_narayana_dhasa_duration = narayana._dhasa_duration(planet_positions,planet2_house)
        if _debug_print: print('planet2_narayana_dhasa_duration',planet2_narayana_dhasa_duration)
        if planet1_narayana_dhasa_duration > planet2_narayana_dhasa_duration:
            if _debug_print: print('Rule-5(a): Planet1/Saturn/Mars is stronger')
            return planet1
        elif planet2_narayana_dhasa_duration > planet1_narayana_dhasa_duration:
            if _debug_print: print('Rule-5(a): Planet2/Rahu/Ketu is stronger')
            return planet2
    #else: # Check during Arudhas
    """ Rule 5(b) the planet that is more advanced in its rasi. """
    if planet1_longitude is not None and planet2_longitude is not None:
        if planet1_longitude > planet2_longitude:
            if _debug_print: print('Rule 5(b)',planet_list[planet1],' is stronger than',planet_list[planet2],planet1_longitude,'>',planet2_longitude)
            return planet1
        else:
            if _debug_print: print('Rule 5(b)',planet_list[planet2],' is stronger than',planet_list[planet1],planet2_longitude,'>',planet1_longitude)
            return planet2
def _stronger_planet_new(house_to_planet_dict,planet1=const._SATURN,planet2=7):
    _debug_print = False 
    if _debug_print: print('stronger_planet_new: finding stronger co lords ',planet_list[planet1],planet_list[planet2])
    if planet1==planet2:
        return planet1
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_dict)
    if _debug_print: print('p_to_h',p_to_h)
    """
    ### Validate planet inputs
    valid_input = (planet1 == 6 and planet2 == 7) or (planet1 == 2 and planet2 == 8)
    if not valid_input:
        print('Only accepted planet combinations are Saturn/Rahu or Mar/Ketu')
        return None  
    """
    planet1_house = p_to_h[planet1]
    if _debug_print: print('planet1',planet1,planet_list[planet1],'in house',planet1_house,rasi_names_en[planet1_house])
    planet2_house = p_to_h[planet2]
    if _debug_print: print('planet2',planet2,planet_list[planet2],'in house',planet2_house,rasi_names_en[planet2_house])
    lord_house_of_planets = const.house_lords_dict#const.houses_of_rahu_kethu[planet2]
    if _debug_print: print('lord_house_of_planets',lord_house_of_planets)
    """ Basic Rule - If Planet1/Saturn/Mars in Aq/Sc and Planet2/Rahu/Ketu elsewhere then Planet2/Rahu/Ketu is stronger """
    if (planet1_house==lord_house_of_planets and planet2_house != lord_house_of_planets):
        if _debug_print: print('Basic Rule','Planet2/Rahu/Ketu is stronger')
        return planet2
    if (planet2_house==lord_house_of_planets and planet1_house != lord_house_of_planets):
        if _debug_print: print('Basic Rule','Planet1/Saturn/Mars is stronger')
        return planet1
    if _debug_print: print('Basic Rule: Neither',planet_list[planet1],' nor ',planet_list[planet2],'in',lord_house_of_planets)
    """ Rule-1: If one planet is joined by more planets than the other, it is stronger. """
    planet1_co_planet_count = sum(value==planet1_house for value in p_to_h.values()) - 1 # Exclude planet itsef
    if _debug_print: print('Rule-1','planet1_co_planet_count',planet1_co_planet_count)
    planet2_co_planet_count = sum(value==planet2_house for value in p_to_h.values()) - 1 # Exclude planet itself
    if _debug_print: print('Rule-1','planet2_co_planet_count',planet2_co_planet_count)
    if planet1_co_planet_count > planet2_co_planet_count:
        if _debug_print: print('Rule-1','Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_co_planet_count > planet1_co_planet_count:
        if _debug_print: print('Rule-1','Planet2/Rahu/Ketu is stronger')
        return planet2
    if _debug_print: print('Rule-1: Both planets have same co planet count',planet1_co_planet_count,planet2_co_planet_count)
    """ Rule-2: how many of the following planets conjoin/aspect a planet: (1) Jupiter,(2) Mercury, and, (3) dispositor. """
    # Dispositor of a planet = lord of the house where the planet is
    dispositor_of_planet1_house = const.house_owners[planet1_house]
    if _debug_print: print('dispositor_of_planet1_house',planet_list[dispositor_of_planet1_house])
    planet1_co_planet_count = 0
    planet1_co_planet_count += [p_to_h[3],p_to_h[4],dispositor_of_planet1_house].count(planet1_house)
    #if _debug_print: print('Planet1',planet_list[planet1],' cojoin count',planet1_co_planet_count)
    planet1_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, planet1_house)
    if _debug_print: print('Aspects of',planet_list[planet1],[planet_list[p] for p in planet1_aspects])
    planet1_co_planet_count += sum(p1 in planet1_aspects for p1 in [3,4,dispositor_of_planet1_house])
    if _debug_print: print('Planet1',planet_list[planet1],' aspect count',planet1_co_planet_count)
    if _debug_print: print('Rule-2','Planet1',planet_list[planet1],'Aspect/Cojoin count',planet1_co_planet_count)

    planet2_co_planet_count = 0
    dispositor_of_planet2_house = const.house_owners[planet2_house]
    if _debug_print: print('dispositor_of_planet2_house',planet_list[dispositor_of_planet2_house])
    planet2_co_planet_count += [p_to_h[3],p_to_h[4],dispositor_of_planet2_house].count(planet2_house)
    if _debug_print: print('Planet2',planet_list[planet2],' cojoin count',planet2_co_planet_count)
    planet2_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, planet2_house)
    if _debug_print: print('Aspects of',planet_list[planet2],[planet_list[p] for p in planet2_aspects])
    planet2_co_planet_count += sum(p2 in planet2_aspects for p2 in [3,4,dispositor_of_planet2_house])
    if _debug_print: print('Planet2',planet_list[planet2],' aspect count',planet2_co_planet_count)
    if _debug_print: print('Rule-2','Planet2',planet_list[planet2],'Aspect/Cojoin count',planet2_co_planet_count)
    """
    planet1_co_planet_count = sum( ((value==planet1_house) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==dispositor_of_planet1_house)) for value in p_to_h.values())
    print('Rule-2','planet1_house',planet1_house,'dispositor_of_planet1_house',dispositor_of_planet1_house,'planet1_co_planet_count',planet1_co_planet_count)
    dispositor_of_planet2_house = const.house_owners[planet2_house]
    print('dispositor_of_planet2_house',planet_list[dispositor_of_planet2_house])
    planet2_co_planet_count = sum( ((value==planet2_house) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==dispositor_of_planet2_house)) for value in p_to_h.values())
    """
    if planet1_co_planet_count > planet2_co_planet_count:
        if _debug_print: print('Rule-2','Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_co_planet_count > planet1_co_planet_count:
        if _debug_print: print('Rule-2','Planet2/Rahu/Ketu is stronger')
        return planet2
    if _debug_print: print("Rule-2 Both planets have same Cojoin/Aspects count",planet1_co_planet_count,planet2_co_planet_count)
    """ Rule-3: If one planet is exalted and the other not, then the exalted planet is stronger. """
    if _debug_print: print('house_strengths_of_planet1',const.house_strengths_of_planets[planet1][planet1_house], 'house_strengths_of_planet2',const.house_strengths_of_planets[planet2][planet2_house])
    if const.house_strengths_of_planets[planet1][planet1_house] == const._EXALTED_UCCHAM and \
        (const.house_strengths_of_planets[planet1][planet1_house] > const.house_strengths_of_planets[planet2][planet2_house]):
        if _debug_print: print('Rule-3','Planet1/Saturn/Mars is exhalted and thus stronger')
        return planet1
    if const.house_strengths_of_planets[planet2][planet2_house] == const._EXALTED_UCCHAM and \
        (const.house_strengths_of_planets[planet2][planet2_house] > const.house_strengths_of_planets[planet2][planet2_house]):
        if _debug_print: print('Rule-3','Planet2/Rahu/Ketu is exhalted and thus stronger')
        return planet2
    if _debug_print: print("Rule-3:None of the planets are exhalted and thus stronger")
    """ Rule - 4: natural strength of the rasi containing the planet. 
        Dual rasis are stronger than fixed rasis and fixed rasis are stronger than movable rasis.
    """
    if planet1_house in const.dual_signs and planet2_house not in const.dual_signs:
            if _debug_print: print('Rule-4','Planet1/Saturn/Mars is stronger')
            return planet1
    elif planet1_house in const.fixed_signs:
        if planet2_house in const.dual_signs:
            if _debug_print: print('Rule-4','Planet2/Rahu/Ketu is stronger')
            return planet2
        elif planet2_house in const.movable_signs: 
            if _debug_print: print('Rule-4','Planet1/Saturn/Mars is stronger')
            return planet1
    else: # Saturn/Mars in movable
        if planet2_house not in const.movable_signs:
            if _debug_print: print('Rule-4','Planet2/Rahu/Ketu is stronger')
            return planet2
    if _debug_print: print('stronger_planet_new - Upto Rule-4 not satisfied - returning None')
    return None
def stronger_planet(house_to_planet_dict,planet1=const._SATURN,planet2=7,check_during_dhasa=False,planet1_longitude=None,planet2_longitude=None):
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1 and planet2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
          Default: planet1=6 (Saturn) and planet2=7 (Rahu)
        @return stronger of planet1 and planet2
            Stronger of Rahu/Saturn or Ketu/Mars is returned
    """
    """ TODO: To implement Rule 5(b) for Arudhas. For that we need planet longitudes """
    #print('stronger_planet',planet_list[planet1],planet_list[planet2])
    if planet1==planet2:
        return planet1
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
    lord_house_of_planets = const.house_lords_dict#const.houses_of_rahu_kethu[planet2]
    #print('lord_house_of_planets',lord_house_of_planets,[rasi_names_en[p] for p in lord_house_of_planets])
    """ Basic Rule - If Planet1/Saturn/Mars in Aq/Sc and Planet2/Rahu/Ketu elsewhere then Planet2/Rahu/Ketu is stronger """
    if (planet1_house==lord_house_of_planets and planet2_house != lord_house_of_planets):
        #print('Basic Rule','Planet2/Rahu/Ketu is stronger')
        return planet2
    if (planet2_house==lord_house_of_planets and planet1_house != lord_house_of_planets):
        #print('Basic Rule','Planet1/Saturn/Mars is stronger')
        return planet1
    #print('Basic Rule: Neither',planet1,' nor ',planet2,'in',lord_house_of_planets)
    """ Rule-1: If one planet is joined by more planets than the other, it is stronger. """
    planet1_co_planet_count = sum(value==planet1_house for value in p_to_h.values()) - 1 # Exclude planet itsef
    #print('Rule-1','planet1_co_planet_count',planet1_co_planet_count)
    planet2_co_planet_count = sum(value==planet2_house for value in p_to_h.values()) - 1 # Exclude planet itself
    #print('Rule-1','planet2_co_planet_count',planet2_co_planet_count)
    if planet1_co_planet_count > planet2_co_planet_count:
        #print('Rule-1','Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_co_planet_count > planet1_co_planet_count:
        #print('Rule-1','Planet2/Rahu/Ketu is stronger')
        return planet2
    #print('Rule-1: Both planets have same co planet count',planet1_co_planet_count,planet2_co_planet_count)
    """ Rule-2: how many of the following planets conjoin/aspect a planet: (1) Jupiter,(2) Mercury, and, (3) dispositor. """
    # Dispositor of a planet = lord of the house where the planet is
    dispositor_of_planet1_house = const.house_owners[planet1_house]
    #print('dispositor_of_planet1_house',planet_list[dispositor_of_planet1_house])
    planet1_co_planet_count = 0
    planet1_co_planet_count += [p_to_h[3],p_to_h[4],dispositor_of_planet1_house].count(planet1_house)
    #print('Planet1',planet_list[planet1],' cojoin count',planet1_co_planet_count)
    planet1_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, planet1_house)
    #print('Aspects of',planet_list[planet1],[planet_list[p] for p in planet1_aspects])
    planet1_co_planet_count += sum(planet1_aspects.count(p1) for p1 in [3,4,dispositor_of_planet1_house])
    #print('Planet1',planet_list[planet1],' aspect count',planet1_co_planet_count)
    #print('Rule-2','Planet1',planet_list[planet1],'Aspect/Cojoin count',planet1_co_planet_count)

    planet2_co_planet_count = 0
    dispositor_of_planet2_house = const.house_owners[planet2_house]
    #print('dispositor_of_planet2_house',planet_list[dispositor_of_planet2_house])
    planet2_co_planet_count += [p_to_h[3],p_to_h[4],dispositor_of_planet2_house].count(planet2_house)
    #print('Planet2',planet_list[planet2],' cojoin count',planet2_co_planet_count)
    planet2_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, planet2_house)
    #print('Aspects of',planet_list[planet2],[planet_list[p] for p in planet2_aspects])
    planet2_co_planet_count += sum(planet2_aspects.count(p2) for p2 in [3,4,dispositor_of_planet2_house])
    #print('Planet2',planet_list[planet2],' aspect count',planet2_co_planet_count)
    #print('Rule-2','Planet2',planet_list[planet2],'Aspect/Cojoin count',planet2_co_planet_count)
    """
    planet1_co_planet_count = sum( ((value==planet1_house) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==dispositor_of_planet1_house)) for value in p_to_h.values())
    print('Rule-2','planet1_house',planet1_house,'dispositor_of_planet1_house',dispositor_of_planet1_house,'planet1_co_planet_count',planet1_co_planet_count)
    dispositor_of_planet2_house = const.house_owners[planet2_house]
    print('dispositor_of_planet2_house',planet_list[dispositor_of_planet2_house])
    planet2_co_planet_count = sum( ((value==planet2_house) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==dispositor_of_planet2_house)) for value in p_to_h.values())
    """
    if planet1_co_planet_count > planet2_co_planet_count:
        #print('Rule-2','Planet1/Saturn/Mars is stronger')
        return planet1
    elif planet2_co_planet_count > planet1_co_planet_count:
        #print('Rule-2','Planet2/Rahu/Ketu is stronger')
        return planet2
    #print("Rule-2 Both planets have same Cojoin/Aspects count",planet1_co_planet_count,planet2_co_planet_count)
    """ Rule-3: If one planet is exalted and the other not, then the exalted planet is stronger. """
    #print('house_strengths_of_planet1',const.house_strengths_of_planets[planet1][planet1_house], 'house_strengths_of_planet2',const.house_strengths_of_planets[planet2][planet2_house])
    if const.house_strengths_of_planets[planet1][planet1_house] == const._EXALTED_UCCHAM and \
        (const.house_strengths_of_planets[planet1][planet1_house] > const.house_strengths_of_planets[planet2][planet2_house]):
        #print('Rule-3','Planet1/Saturn/Mars is exhalted and thus stronger')
        return planet1
    if const.house_strengths_of_planets[planet2][planet2_house] == const._EXALTED_UCCHAM and \
        (const.house_strengths_of_planets[planet2][planet2_house] > const.house_strengths_of_planets[planet2][planet2_house]):
        #print('Rule-3','Planet2/Rahu/Ketu is exhalted and thus stronger')
        return planet2
    #print("Rule-3:None of the planers are exhalted and thus stronger")
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
    #print("Rule-4: Both planets are in same type of rasi Dual/fixed/movable - and are equally stronger")
    if check_during_dhasa:
        """ Rule-5-a, planet giving a larger length for narayana dhasa"""
        from hora.horoscope.dhasa.raasi import narayana 
        planet1_narayana_dhasa_duration = narayana._dhasa_duration(p_to_h,planet1_house)
        #print('planet1_narayana_dhasa_duration',planet1_narayana_dhasa_duration)
        planet2_narayana_dhasa_duration = narayana._dhasa_duration(p_to_h,planet2_house)
        #print('planet2_narayana_dhasa_duration',planet2_narayana_dhasa_duration)
        if planet1_narayana_dhasa_duration > planet2_narayana_dhasa_duration:
            #print('Rule-5(a): Planet1/Saturn/Mars is stronger')
            return planet1
        elif planet2_narayana_dhasa_duration > planet1_narayana_dhasa_duration:
            #print('Rule-5(a): Planet2/Rahu/Ketu is stronger')
            return planet2
    #else: # Check during Arudhas
    """ Rule 5(b) the planet that is more advanced in its rasi. """
    if planet1_longitude is not None and planet2_longitude is not None:
        if planet1_longitude > planet2_longitude:
            #print('Rule 5(b)',planet_list[planet1],' is stronger than',planet_list[planet2])
            return planet1
        else:
            #print('Rule 5(b)',planet_list[planet2],' is stronger than',planet_list[planet2])
            return planet2
def stronger_rasi_from_planet_positions(planet_positions,rasi1,rasi2):
    house_to_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    _stronger_rasi = stronger_rasi(house_to_planet_dict,rasi1,rasi2)
    if _stronger_rasi is not None:
        return _stronger_rasi
    """ Rule-6: The rasi owned by the planet with the higher advancement of longitude is stronger. """
    #print("Upto Rule 5 - not met. Stronger Rasi to be found from stronger_co_lords",rasi1,rasi2)
    lord_of_rasi1 = house_owner_from_planet_positions(planet_positions, rasi1) # const.house_owners[rasi1]
    lord_of_rasi2 = house_owner_from_planet_positions(planet_positions, rasi2) #const.house_owners[rasi2]
    #sp = stronger_planet_from_planet_positions(planet_positions, lord_of_rasi1, lord_of_rasi1)
    #if sp is None:
    #    print('could not find stronger co lord',lord_of_rasi1,lord_of_rasi2)
    #    exit()
    if planet_positions[lord_of_rasi1+1][1][1] > planet_positions[lord_of_rasi2+1][1][1]:#sp == lord_of_rasi1:
        #print("Rule-6:",rasi1,'is stronger by higher advancement of longitude',planet_positions[lord_of_rasi1+1][1][1],'>',planet_positions[lord_of_rasi2+1][1][1])
        return rasi1
    else:
        #print("Rule-6:",rasi2,'is stronger by higher advancement of longitude',planet_positions[lord_of_rasi2+1][1][1],'>',planet_positions[lord_of_rasi1+1][1][1])
        return rasi2
     
def stronger_rasi(house_to_planet_dict,rasi1,rasi2):
    """
        To find stronger rasi between rasi1 and rasi2 
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param rasi1: [ 0,,11] 0 = Ar and 11 = Pi 
        @param rasi2: [ 0,,11] 0 = Ar and 11 = Pi
        @return  return stringer raasi (raasi index 0 to 11, 0 = Ar, 11=Pi) 
    """
    p_to_h = utils.get_planet_to_house_dict_from_chart(house_to_planet_dict)
    #print(p_to_h)
    """ Rule-1 rasi contains more planets than the other rasi, then it is stronger. """
    rasi1_planet_count = sum(value==rasi1 for key,value in p_to_h.items() if key != const._ascendant_symbol)
    #print('Rule-1',rasi1,'rasi1_planet_count',rasi1_planet_count)
    rasi2_planet_count = sum(value==rasi2 for key,value in p_to_h.items() if key != const._ascendant_symbol)
    #print('Rule-1',rasi2,'rasi2_planet_count',rasi2_planet_count)
    if rasi1_planet_count > rasi2_planet_count:
        #print('Rule-1 Rasi1',rasi1,'is stronger')
        return rasi1
    if rasi2_planet_count > rasi1_planet_count:
        #print('Rule-1 Rasi2',rasi2,'is stronger')
        return rasi2
    #print('Rule-1: Both rasis have same count of planets')
    """ Rule-2: how many of the following planets in/aspecting the rasi: (1) Jupiter,(2) Mercury, and, (3) dispositor. """
    # Dispositor of a planet = lord of the house where the planet is
    lord_of_rasi1 = const.house_owners[rasi1]
    rasi1_co_planet_count = 0
    rasi1_co_planet_count += [p_to_h[3],p_to_h[4],lord_of_rasi1].count(rasi1)
    #print('rasi1',rasi_names_en[rasi1],' cojoin count',rasi1_co_planet_count)
    rasi1_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, rasi1)
    #print('Aspects of',rasi_names_en[rasi1],[planet_list[p] for p in rasi1_aspects])
    rasi1_co_planet_count += sum(rasi1_aspects.count(p1) for p1 in [3,4,lord_of_rasi1])
    
    lord_of_rasi2 = const.house_owners[rasi2]
    rasi2_co_planet_count = 0
    rasi2_co_planet_count += [p_to_h[3],p_to_h[4],lord_of_rasi2].count(rasi2)
    #print('rasi2',rasi_names_en[rasi2],' cojoin count',rasi2_co_planet_count)
    rasi2_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, rasi2)
    #print('Aspects of',rasi_names_en[rasi2],[planet_list[p] for p in rasi2_aspects])
    rasi2_co_planet_count += sum(rasi2_aspects.count(p1) for p1 in [3,4,lord_of_rasi2])
    if rasi1_co_planet_count > rasi2_co_planet_count:
        #print('Rule-2 Rasi1',rasi1,'is stronger')
        return rasi1
    elif rasi2_co_planet_count > rasi1_co_planet_count:
        #print('Rule-2 Rasi2',rasi2,'is stronger')
        return rasi2
    #print('Rule-2: Both rasis have same aspect/cojoin count',rasi1)
    """ Rule-3: If one rasi contains an exalted planet and the other does not, then the former rasi is stronger."""
    rasi1_exhalted_planet_count = sum([const.house_strengths_of_planets[int(p)][rasi1] == const._EXALTED_UCCHAM for p in p_to_h if p!= const._ascendant_symbol and p_to_h[p]==rasi1])
    #print('Rule-3','rasi1_exhalted_planet_count',rasi1_exhalted_planet_count)
    rasi2_exhalted_planet_count = sum([const.house_strengths_of_planets[int(p)][rasi2] == const._EXALTED_UCCHAM for p in p_to_h if p!= const._ascendant_symbol and p_to_h[p]==rasi2])
    #print('Rule-3','rasi2_exhalted_planet_count',rasi2_exhalted_planet_count)
    if rasi1_exhalted_planet_count > 0 and rasi2_exhalted_planet_count ==0:
        #print('rasi1',rasi1,'contains exhalted planet and rasi2',rasi2,'does not')
        return rasi1
    if rasi2_exhalted_planet_count > 0 and rasi1_exhalted_planet_count ==0:
        #print('rasi2',rasi2,'contains exhalted planet and rasi1',rasi1,'does not')
        return rasi2
    """ Rule - 4: A rasi whose lord is in a rasi with a different oddity (odd/even) is stronger than a
                    rasi whose lord is in a rasi with the same oddity. """
    #print(rasi1,lord_of_rasi1,p_to_h[lord_of_rasi1])
    rasi1_has_oddity = (rasi1 in const.odd_signs and p_to_h[lord_of_rasi1] in const.even_signs) or (rasi1 in const.even_signs and p_to_h[lord_of_rasi1] in const.odd_signs)
    #print(rasi2,lord_of_rasi2,p_to_h[lord_of_rasi2])
    rasi2_has_oddity = (rasi2 in const.odd_signs and p_to_h[lord_of_rasi2] in const.even_signs) or (rasi2 in const.even_signs and p_to_h[lord_of_rasi2] in const.odd_signs)
    #print('Rule-4','rasi1_has_oddity',rasi1_has_oddity,'rasi2_has_oddity',rasi2_has_oddity)
    if rasi1_has_oddity and not rasi2_has_oddity:
        #print('Rule-4:rasi1',rasi1,'has oddity and thus stronger')
        return rasi1
    if rasi2_has_oddity and not rasi1_has_oddity:
        #print('Rule-4:rasi2',rasi2,'has oddity and thus stronger')
        return rasi2
    #print('Rule-4: Both Rasis have same oddity')
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
    else:
        if rasi2 not in const.movable_signs:
            #print('Rule-5 rasi2',rasi2,'is stronger')
            return rasi2
    return None
    #import sys
    #sys.exit('No Stronger Rasi found. Use stronger_rasi_from_planet_positions instead.')
def natural_friends_of_planets(h_to_p=None):
    """
        Take the moolatrikona of the planet. Lord of the rasi where it is exalted is its friend. 
        Lords of 2nd, 4th, 5th, 8th, 9th and 12th rasis from it are also its natural friends.
    """
    if h_to_p==None:
        return const.friendly_planets
    nf = {p:[] for p in range(9)}
    for p in range(9):
        mtr = const.moola_trikona_of_planets[p]
        if p < 7:
            er = [house_owner(h_to_p,r) for r in range(12) if const.house_strengths_of_planets[p][r]==const._EXALTED_UCCHAM]
            #ler = house_owner(h_to_p, er)
            nf[p].append(er)
        fr = [house_owner(h_to_p,r) for r in range(12) if const.house_strengths_of_planets[p][r]==const._FRIEND]
        nf[p].append(fr)
        nf[p] = utils.flatten_list(nf[p])
        #print(p,mtr,er,nf[p])
        nf[p] = list(set(nf[p]))
    return nf # const.friendly_planets
def natural_neutral_of_planets(h_to_p=None):
    return const.neutral_planets
def natural_enemies_of_planets(h_to_p=None):
    return const.enemy_planets
def _get_temporary_friends_of_planets(h_to_p):
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    p_temp_friends = {}
    for p in range(9):
        p_raasi = p_to_h[p]
        _temp_friends = utils.flatten_list([h_to_p[(p_raasi+h)%12].split('/') for h in const.temporary_friend_raasi_positions if h_to_p[(p_raasi+h)%12] !=''])
        [_temp_friends.remove(rp) for rp in [str(p),'L'] if rp in _temp_friends]
        _temp_friends = list(set(map(int,_temp_friends)))
        p_temp_friends[p] = _temp_friends
    return p_temp_friends
def _get_temporary_enemies_of_planets(h_to_p):
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    p_temp_enemies = {}
    for p in range(9):
        p_raasi = p_to_h[p]
        _temp_enemies = utils.flatten_list([h_to_p[(p_raasi+h)%12].split('/') for h in const.temporary_enemy_raasi_positions if h_to_p[(p_raasi+h)%12] !=''])
        [_temp_enemies.remove(rp) for rp in [str(p),'L'] if rp in _temp_enemies]
        _temp_enemies = list(set(map(int,_temp_enemies)))
        p_temp_enemies[p] = _temp_enemies
    return p_temp_enemies
def _get_compound_relationships_of_planets(h_to_p):
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    tf = _get_temporary_friends_of_planets(h_to_p)
    #print('_get_temporary_friends_of_planets',tf)
    te = _get_temporary_enemies_of_planets(h_to_p)
    #print('_get_temporary_enemies_of_planets',te)
    nf = const.friendly_planets
    #print('friendly_planets',nf)
    nn = const.neutral_planets
    #print('neutral_planets',nn)
    ne = const.enemy_planets
    #print('enemy_planets',ne)
    p_compound = [[0 for _ in range(9)] for _ in range(9)]
    for p in range(9):
        tfp = tf[p]; tep = te[p]; nfp = nf[p]; nnp = nn[p]; nep = ne[p]
        #print('tfp',tfp,'tep',tep,'nfp',nfp,'nnp',nnp,'nep',nep)
        #am=[];m=[];n=[];e=[];ae=[]
        for p1 in range(9):
            if p==p1:
                continue
            if p1 in nfp and p1 in tfp: # Adhimitras
                p_compound[p][p1] = 4
                #am.append(p1)
            elif (p1 in nfp and p1 in tep) or (p1 in nep and p1 in tfp): # Neutral
                p_compound[p][p1] = 2
                #n.append(p1)
            elif (p1 in nnp and p1 in tfp):
                p_compound[p][p1] = 3
                #m.append(p1)
            elif (p1 in nnp and p1 in tep):
                p_compound[p][p1] = 1
                #e.append(p1)
            elif (p1 in nep and p1 in tep):
                p_compound[p][p1] = 0
                #ae.append(p1)
        #p_compound[p] = [am,m,n,e,ae]
    return p_compound
def _get_varga_viswa_of_planets(h_to_p):
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    cs = _get_compound_relationships_of_planets(h_to_p)
    scores = [5,7,10,15,18]
    #print('compound releations',cs)
    vv = [0 for _ in range(9)]
    for p in range(9):
        if const.house_strengths_of_planets[p][ p_to_h[p]]==const._OWNER_RULER:
            #print('planet',p,'is a ruler/owner of',p_to_h[p],'score=20')
            vv[p] = 20
        else:
            d = const.house_owners[p_to_h[p]]
            vv[p] = scores[cs[p][d]]
    return vv    
def house_owner_from_planet_positions(planet_positions,sign,check_during_dhasa=False):
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    lord_of_sign = house_owner(h_to_p, sign)
    if sign == 7:
        lord_of_sign = stronger_planet_from_planet_positions(planet_positions, 2, 8, check_during_dhasa=check_during_dhasa)
    elif sign == 10:
        lord_of_sign = stronger_planet_from_planet_positions(planet_positions, 6, 7, check_during_dhasa=check_during_dhasa)
    return lord_of_sign
def house_owner(h_to_p,sign):
    lord_of_sign = const.house_owners[sign]
    l_o_s = lord_of_sign
    #print('sign',sign,'lord_of_sign',lord_of_sign)
    if sign==7:
        lord_of_sign = stronger_planet(h_to_p,2,8) #MArs and Ketu
        #print('Stronger in Scorpio',lord_of_sign)
    elif sign==10:
        lord_of_sign = stronger_planet(h_to_p,6,7)#Saturn and Rahu
    if lord_of_sign==None:
        #print('Rule (5) Requires longitudes of planets which are not provided, hence house.house_owner returning None')
        #print('h_to_p',h_to_p,'sign',sign,'lord_of_sign',lord_of_sign)
        #print('Warning: Returning lord of sign as owner of house',l_o_s,' without checking Sc/Aq stronger lord')
        return None # l_o_s
        #exit()
    return lord_of_sign
def marakas_from_planet_positions(planet_positions):
    """
        If a malefic planet powerfully conjoins or aspects, using graha drishti, 
        the 2nd and 7th houses or their lords, then it qualifies as a maraka graha.
        @param planet_positions list in the format [[planet,(raasi,planet_longitude)],...]] 
            First element is that of Lagnam. Example: [ ['L',(0,123.4)],[0,(11,32.7)],...]]
            Lagnam in Aries 123.4 degrees, Sun in Taurus 32.7 degrees
        @return: maraka graha/planets as a list
    """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    #print(p_to_h)
    maraka_sthanas = [(h+p_to_h['L']-1)%12 for h in [2,7]]
    maraka_planets = [house_owner_from_planet_positions(planet_positions, sign) for sign in maraka_sthanas] ## 2 and 7th houses are maraka sthanas
    #print(maraka_sthanas,'maraka_sthana_owners',maraka_planets)
    mpls = [mp for mp in [*range(9)] if p_to_h[mp] in maraka_sthanas or p_to_h[mp] in [p_to_h[p] for p in maraka_planets]]
    #print('mpls',mpls)
    if mpls:
        maraka_planets += mpls
    maraka_planets = list(set(maraka_planets))
    return maraka_planets    
def marakas(h_to_p):
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    """
        If a malefic planet powerfully conjoins or aspects, using graha drishti, 
        the 2nd and 7th houses or their lords, then it qualifies as a maraka graha.
    """
    #print(p_to_h)
    maraka_sthanas = [(h+p_to_h['L']-1)%12 for h in [2,7]]
    maraka_planets = [house_owner(h_to_p, sign) for sign in maraka_sthanas] ## 2 and 7th houses are maraka sthanas
    #print(maraka_sthanas,'maraka_sthana_owners',maraka_planets)
    mpls = [mp for mp in [*range(9)] if p_to_h[mp] in maraka_sthanas or p_to_h[mp] in [p_to_h[p] for p in maraka_planets]]
    #print('mpls',mpls)
    if mpls:
        maraka_planets += mpls
    maraka_planets = list(set(maraka_planets))
    return maraka_planets
def rudra_based_on_planet_positions(dob,tob,place,divisional_chart_factor=1):
    jd = utils.julian_day_number(dob, tob)
    planet_positions = drik.dhasavarga(jd, place, divisional_chart_factor=divisional_chart_factor)
    ascendant_constellation, ascendant_longitude, _, _ = drik.ascendant(jd,place)
    planet_positions = [[const._ascendant_symbol,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    #print(planet_positions)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    lagna_house = p_to_h['L']
    eighth_house_lord = house_owner(h_to_p, const.rudra_eighth_house[(lagna_house+7)%12])
    seventh_house_lord = house_owner(h_to_p, (lagna_house+6)%12)
    eighth_house_lord_longitude = planet_positions[eighth_house_lord+1][1][1]
    seventh_house_lord_longitude = planet_positions[seventh_house_lord+1][1][1]
    #print('eighth_house_lord',eighth_house_lord,eighth_house_lord_longitude,'seventh_house_lord',seventh_house_lord,seventh_house_lord_longitude)
    #_rudra = stronger_planet(h_to_p, eighth_house_lord, seventh_house_lord, False, eighth_house_lord_longitude, seventh_house_lord_longitude)
    _rudra = stronger_planet_from_planet_positions(planet_positions, eighth_house_lord, seventh_house_lord, check_during_dhasa=False)
    _rudra_sign = p_to_h[_rudra]
    trishoola_rasis = trines_of_the_raasi(_rudra_sign)
    return _rudra, _rudra_sign,trishoola_rasis
def brahma(planet_positions):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]
    seventh_house = (asc_house+6) %12
    sp = stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    #print('asc_house',asc_house,'seventh_house',seventh_house,'stronger rasi',sp)
    lords = [house_owner_from_planet_positions(planet_positions, (sp+h-1)%12) for h in [6,8,12]]
    #print('lords',lords)
    lords = [l for l in lords if l not in [7,8]] # Remove Rahu and Kethu
    #print('lords',lords)
    lords_scores = {l:0 for l in lords}
    for l in lords:
        h = p_to_h[l]
        if const.house_strengths_of_planets[l][h] >= const._FRIEND:
            lords_scores[l] += 1
        if h in const.odd_signs:
            lords_scores[l] += 1
        if h in [(sp+j)%12 for j in range(6)]:
            lords_scores[l] += 1
    #print(lords_scores)
    lords_scores = dict(sorted(lords_scores.items(), key = lambda x: x[1], reverse = True)[:2])
    #print(lords_scores)
    if len(lords_scores)==1:
        brahma = list(lords_scores.keys())[0]
    elif len(lords_scores)==2:
        brahma = stronger_planet_from_planet_positions(planet_positions, list(lords_scores.keys())[0], list(lords_scores.keys())[1])
    else:
        b1 = stronger_planet_from_planet_positions(planet_positions, list(lords_scores.keys())[0], list(lords_scores.keys())[1])
        brahma = stronger_planet_from_planet_positions(planet_positions, brahma, list(lords_scores.keys())[2])
    return brahma
def rudra(planet_positions):
    """ Stronger of lord of the 8th house from (i) lagna and (ii) the 7th house - is Rudra """
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    lagna_house = p_to_h['L']
    #print('lagna_house',rasi_names_en[lagna_house])
    eighth_house_lord = house_owner(h_to_p, const.rudra_eighth_house[lagna_house])
    #print('8th Rudra house',rasi_names_en[const.rudra_eighth_house[lagna_house]],'8th rudra lord',planet_list[eighth_house_lord])
    seventh_house_lord = house_owner(h_to_p, const.rudra_eighth_house[(lagna_house+6)%12]) #8th house of 7th house from Lagna
    #print('7th house',rasi_names_en[const.rudra_eighth_house[(lagna_house+6)%12]],'7th house lord',planet_list[seventh_house_lord])
    _rudra = stronger_planet_from_planet_positions(planet_positions, eighth_house_lord, seventh_house_lord)
    #print('Stronger of ',planet_list[eighth_house_lord],'and',planet_list[seventh_house_lord],'is',planet_list[_rudra])
    _rudra_sign = p_to_h[_rudra]
    trishoola_rasis = trines_of_the_raasi(_rudra_sign)
    return _rudra, _rudra_sign,trishoola_rasis
def trishoola_rasis(planet_positions):
    return trines_of_the_raasi(rudra(planet_positions)[1])
def maheshwara(dob,tob,place,divisional_chart_factor=1):
    """
        Get Maheshwara Planet
    """
    jd = utils.julian_day_number(dob, tob)
    from hora.horoscope.chart import charts
    pp = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    _chara_karakas = chara_karakas(pp) #jd, place, divisional_chart_factor)
    atma_karaka = _chara_karakas[0]
    #print('_maheshwara',atma_karaka)
    pp = drik.dhasavarga(jd, place, divisional_chart_factor)
    ascendant_constellation, ascendant_longitude, _, _ = drik.ascendant(jd,place)
    pp = [[const._ascendant_symbol,(ascendant_constellation, ascendant_longitude)]] + pp
    #print(pp)
    h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(pp)
    #print(h_to_p)
    atma_karaka_house = pp[atma_karaka+1][1][0]
    _maheshwara = house_owner(h_to_p,(atma_karaka_house+7)%12)
    #print('atma_karaka_house',atma_karaka_house,'atma_8th_lord',_maheshwara)
    #print(p_to_h[_maheshwara],'==?',const.house_owners[_maheshwara])
    if p_to_h[_maheshwara] == const.house_owners[_maheshwara]:
        atma_karaka_house = p_to_h[_maheshwara]
        atma_8th_lord = house_owner(h_to_p,(atma_karaka_house+7)%12)
        atma_12th_lord = house_owner(h_to_p,(atma_karaka_house+11)%12)
        _maheshwara = stronger_planet(h_to_p, atma_8th_lord, atma_12th_lord)#, check_during_dhasa, planet1_longitude, planet2_longitude)
    #print(p_to_h[_maheshwara],'==',p_to_h[7],'or',p_to_h[_maheshwara],'==',p_to_h[8])
    #print(p_to_h[7],'==',(p_to_h[_maheshwara]+7)%12,'or', p_to_h[8],'==',(p_to_h[_maheshwara]+7)%12)
    if p_to_h[_maheshwara]==p_to_h[7] or p_to_h[_maheshwara]==p_to_h[8]:
        _maheshwara = house_owner(h_to_p,(atma_karaka_house+5)%12)
    elif p_to_h[7]==(p_to_h[_maheshwara]+7)%12 or p_to_h[8]==(p_to_h[_maheshwara]+7)%12:
        _maheshwara = house_owner(h_to_p,(atma_karaka_house+5)%12)
    if _maheshwara == 7:
        _maheshwara = 3
    elif _maheshwara == 8:
        _maheshwara = 4
    return _maheshwara
longevity_of_pair = lambda rasi1,rasi2: [key for key,value in const.longevity.items() if (rasi1,rasi2) in value][0]
def longevity(dob,tob,place,divisional_chart_factor=1):
    jd = utils.julian_day_number(dob, tob)
    planet_positions = drik.dhasavarga(jd, place, divisional_chart_factor=divisional_chart_factor)
    ascendant_constellation, ascendant_longitude, _, _ = drik.ascendant(jd,place)
    planet_positions = [[const._ascendant_symbol,(ascendant_constellation, ascendant_longitude)]] + planet_positions
    rasi_type = lambda rasi:[index for index,r_type in enumerate([const.fixed_signs,const.movable_signs,const.dual_signs]) if rasi in r_type][0]
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    #print('p_to_h',p_to_h)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print('h_to_p',h_to_p)
    lagna_house = p_to_h['L']
    # first pair houses of Lagna Lord and 8th lord 
    lagna_lord_house = p_to_h[house_owner(h_to_p, lagna_house)]
    #print('lagna_house',lagna_house,'lagna lord',house_owner(h_to_p, lagna_house),'lagna_lord_house',lagna_lord_house)
    eighth_lord_house = p_to_h[house_owner(h_to_p, const.rudra_eighth_house[lagna_house])]
    #print('eighth_lord',house_owner(h_to_p, const.rudra_eighth_house[lagna_house]),'eighth_lord_house',eighth_lord_house)
    #print('lagna_lord_house rasi_type',rasi_type(lagna_lord_house),'eighth_lord rasi type',rasi_type(eighth_lord_house))
    pair1_longevity = longevity_of_pair(rasi_type(lagna_lord_house),rasi_type(eighth_lord_house))
    #print('pair1_longevity',pair1_longevity)
    
    # Second pair - houses of moon and Saturn
    pair2_longevity = longevity_of_pair(rasi_type(p_to_h[1]),rasi_type(p_to_h[6]))
    #print('pair2_longevity',pair2_longevity)
    
    # Third pair Houses of Lagna and Hora Lagna
    time_of_birth_in_hours = utils.from_dms(tob[0],tob[1],tob[2])
    hora_lagna_house = drik.hora_lagna(jd,place,divisional_chart_factor)[0]  # V3.1.9
    #print('hora_lagna_house',hora_lagna_house)
    pair3_longevity = longevity_of_pair(rasi_type(lagna_house),rasi_type(hora_lagna_house))
    #print('pair3_longevity',pair3_longevity)
    def _longevity_pair_check(pair1_longevity,pair2_longevity,pair3_longevity):
        if pair1_longevity==pair2_longevity and pair2_longevity == pair3_longevity:
            #print('all pairs equal')
            return const.longevity_years[pair1_longevity][pair2_longevity]
        elif pair1_longevity==pair2_longevity and pair2_longevity != pair3_longevity:
            #print('Pair 1 and 2 equal')
            return const.longevity_years[pair1_longevity][pair3_longevity]
        elif pair2_longevity==pair3_longevity and pair2_longevity != pair1_longevity:
            #print('Pair 2 and 3 equal')
            return const.longevity_years[pair2_longevity][pair1_longevity]
        elif pair1_longevity==pair3_longevity and pair1_longevity != pair2_longevity:
            #print('Pair 1 and 3 equal')
            return const.longevity_years[pair1_longevity][pair2_longevity]
        elif pair1_longevity!=pair2_longevity and pair1_longevity != pair3_longevity and pair2_longevity != pair3_longevity:
            #print('All are not equal')
            if p_to_h[1]==p_to_h['L'] or p_to_h[1] == p_to_h[(lagna_house+7)%12]:
                #print('Order Pair 3 and 2')
                return const.longevity_years[pair2_longevity][pair2_longevity]
            else:
                #print('Order Pair 3 and 1')
                return const.longevity_years[pair2_longevity][pair1_longevity]
    return _longevity_pair_check(pair1_longevity,pair2_longevity,pair3_longevity)
def associations_of_the_planet(planet_positions,planet):
    """ There are 3 important associations:
        (1) The two planets are conjoined,
        (2) The two planets aspect each other with graha drishti, or,
        (3) The two planets have a parivartana (exchange). For example, if the 4th lord is in
            the 5th house and the 5th lord is in the 4th house, then we say that there is a
            parivartana between the 4th and 5th lords. This is an association.
    """
    house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    planet_to_house_dict = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    ap = []
    """ (1) The two planets are conjoined,"""
    pl = [int(p) for p in [*range(9)] if planet_to_house_dict[p]==planet_to_house_dict[planet] and p!=planet]
    #print('1',planet,pl)
    ap += pl
    """ (2) The two planets aspect each other with graha drishti """
    pl = list(map(int,graha_drishti_of_the_planet(house_to_planet_list, planet)))
    if planet in pl:
        pl.remove(planet)
    #print('2',planet,pl)
    ap += pl
    """ (3) The two planets have a parivartana (exchange) """
    pl = [int(p) for p in [*range(9)] if int(planet)!=int(p) and \
          house_owner_from_planet_positions(planet_positions, planet_to_house_dict[p])==planet and \
          house_owner_from_planet_positions(planet_positions, planet_to_house_dict[planet])==p]
    #print('3',planet,pl)
    ap += pl
    """ remove duplicates """
    ap = list(set(ap))
    return ap
def baadhakas_of_raasi(planet_position,raasi):
    """ return [Baadhaka Sthaana/rasi, [baadhaka planets]]  of the given raasi"""
    return const.baadhakas[raasi]
def planets_aspecting_the_planet(house_to_planet_dict,planet,separator='/'):
    _,_,app = graha_drishti_from_chart(house_to_planet_dict)
    aspecting_planets = [k for k,v in app.items() if planet in v]
    return aspecting_planets
def order_of_planets_by_strength(planet_positions):
    from functools import cmp_to_key
    planets = [*range(9)]
    def compare(planet1,planet2):
        sp = stronger_planet_from_planet_positions(planet_positions, planet1,planet2)
        return -1 if sp==planet1 else 1 #Left stronger = -1 ; right stronger = +1
    return sorted(planets, key=cmp_to_key(compare))
if __name__ == "__main__":
    from hora.horoscope.chart import charts
    utils.set_language('en')
    dob = (1996,12,7); tob = (10,34,0);place_as_tuple = drik.Place('Chennai, India',13.0878,80.2785,5.5)
    #dob = (1836,2,18); tob = (6,44,0); place_as_tuple = drik.Place('kamarpukur, India',22+53/60,87+44/60,6.0)
    #dob = (1879,12,30); tob = (1,0,0); place_as_tuple = drik.Place('Pondy?, India',9+50/60,78+15/60,6.0)
    dcf = 20
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place_as_tuple, divisional_chart_factor=dcf)
    ck = chara_karakas(planet_positions); print(ck)
    print('strength ordered planets',order_of_planets_by_strength(planet_positions))
    exit()
    for p in [*range(9)]:
        print(p,associations_of_the_planet(planet_positions, p))
    exit()
