import swisseph as swe
from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.transit import tajaka
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
        @param place: drik.place struct(place,lat,long,timezone)
        @param divisional_chart_factor: 1=Rasi, 2=Hora...,9=Navamsa etc
        @return: chara karaka for all planets as a list. First element is Sun
    """
    planet_positions = drik.dhasavarga(jd,place,divisional_chart_factor)[:8]
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
    for p,_ in enumerate(planet_list[:7]):
        house_of_the_planet = p_to_h[p]
        arp[p] = [(h+house_of_the_planet-1)%12 for h in const.graha_drishti[p]]
        ahp[p] = [ (h+asc_house-2) %12 for h in arp[p]]
        app[p] = sum([h_to_p[ar].replace(const._ascendant_symbol,'').split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = [pp for pp in app[p] if pp != '' ]
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
    """ TODO: This does not find aspected planets of the Lagnam Raasi """
    h_to_p = house_to_planet_dict[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    arp = {}
    ahp = {}
    app = {}
    for p,_ in enumerate(planet_list[:9]):
        arp[p] = raasi_drishti[p_to_h[p]]
        ahp[p] = [ (h+asc_house-2) %12 for h in arp[p]]
        #app[p] = sum([h_to_p[ar].replace(const._ascendant_symbol,'').split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = sum([h_to_p[ar].split(separator) for ar in arp[p] if h_to_p[ar] !=''],[])
        app[p] = [pp for pp in app[p] if pp != '' and pp != const._ascendant_symbol]
    return arp,ahp,app
def raasi_drishti_of_the_planet(house_to_planet_dict,planet,separator='/'):
    arp,_,_ = raasi_drishti_from_chart(house_to_planet_dict,separator=separator)
    return arp[planet]
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
def stronger_co_lord_from_planet_positions(planet_positions,planet1=const._SATURN,planet2=7,check_during_dhasa=False):
    """
        To find stronger planet between Rahu/Saturn/Aquarius or Ketu/Mars/Scorpio 
        @param house_to_planet_dict: list of raasi with planet ids in them
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param planet1 and planet2 has to be either Rahu/Saturn 7 and 6 or Ketu/Mars 8 and 3
          Default: planet1=6 (Saturn) and planet2=7 (Rahu)
        @return stronger of planet1 and planet2
            Stronger of Rahu/Saturn or Ketu/Mars is returned
    """
    if planet1==planet2:
        return planet1
    house_to_planet_dict = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    stronger_planet = stronger_co_lord_new(house_to_planet_dict,planet1,planet2)
    if stronger_planet is not None:
        return stronger_planet
    #print("Rule-4: Both planets are in same type of rasi Dual/fixed/movable - and are equally stronger")
    planet1_house = p_to_h[planet1]
    planet1_longitude = planet_positions[planet1+1][1][1] # +1 to inlcude first element 'L'
    planet2_house = p_to_h[planet2]
    planet2_longitude = planet_positions[planet2+1][1][1]
    if check_during_dhasa:
        """ Rule-5-a, planet giving a larger length for narayana dhasa"""
        from hora.horoscope.dhasa import narayana 
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
    else: # Check during Arudhas
        """ Rule 5(b) the planet that is more advanced in its rasi. """
        if planet1_longitude is not None and planet2_longitude is not None:
            if planet1_longitude > planet2_longitude:
                #print('Rule 5(b)',planet_list[planet1],' is stronger than',planet_list[planet2],planet1_longitude,'>',planet2_longitude)
                return planet1
            else:
                #print('Rule 5(b)',planet_list[planet2],' is stronger than',planet_list[planet1],planet2_longitude,'>',planet1_longitude)
                return planet2
def stronger_co_lord_new(house_to_planet_dict,planet1=const._SATURN,planet2=7):
    #print('stronger_co_lord_new: finding stronger co lords ',planet_list[planet1],planet_list[planet2])
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
    #print('lord_house_of_planets',lord_house_of_planets,rasi_names_en[lord_house_of_planets])
    """ Basic Rule - If Planet1/Saturn/Mars in Aq/Sc and Planet2/Rahu/Ketu elsewhere then Planet2/Rahu/Ketu is stronger """
    if (planet1_house==lord_house_of_planets and planet2_house != lord_house_of_planets):
        #print('Basic Rule','Planet2/Rahu/Ketu is stronger')
        return planet2
    if (planet2_house==lord_house_of_planets and planet1_house != lord_house_of_planets):
        #print('Basic Rule','Planet1/Saturn/Mars is stronger')
        return planet1
    #print('Basic Rule: Neither',planet_list[planet1],' nor ',planet_list[planet2],'in',const.rasi_names_en[lord_house_of_planets])
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
    ##print('Planet1',planet_list[planet1],' cojoin count',planet1_co_planet_count)
    planet1_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, planet1_house)
    #print('Aspects of',planet_list[planet1],[planet_list[p] for p in planet1_aspects])
    planet1_co_planet_count += sum(p1 in planet1_aspects for p1 in [3,4,dispositor_of_planet1_house])
    #print('Planet1',planet_list[planet1],' aspect count',planet1_co_planet_count)
    #print('Rule-2','Planet1',planet_list[planet1],'Aspect/Cojoin count',planet1_co_planet_count)

    planet2_co_planet_count = 0
    dispositor_of_planet2_house = const.house_owners[planet2_house]
    #print('dispositor_of_planet2_house',planet_list[dispositor_of_planet2_house])
    planet2_co_planet_count += [p_to_h[3],p_to_h[4],dispositor_of_planet2_house].count(planet2_house)
    #print('Planet2',planet_list[planet2],' cojoin count',planet2_co_planet_count)
    planet2_aspects = aspected_planets_of_the_raasi(house_to_planet_dict, planet2_house)
    #print('Aspects of',planet_list[planet2],[planet_list[p] for p in planet2_aspects])
    planet2_co_planet_count += sum(p2 in planet2_aspects for p2 in [3,4,dispositor_of_planet2_house])
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
    #print("Rule-3:None of the planets are exhalted and thus stronger")
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
    print('stronger_co_lord_new - Upto Rule-4 not satisfied - returning None')
    return None
def stronger_co_lord(house_to_planet_dict,planet1=const._SATURN,planet2=7,check_during_dhasa=False,planet1_longitude=None,planet2_longitude=None):
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
    #print('stronger_co_lord',planet_list[planet1],planet_list[planet2])
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
    print("Rule-4: Both planets are in same type of rasi Dual/fixed/movable - and are equally stronger")
    if check_during_dhasa:
        """ Rule-5-a, planet giving a larger length for narayana dhasa"""
        from hora.horoscope.dhasa import narayana 
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
    else: # Check during Arudhas
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
    _stronger_rasi = stronger_rasi_new(house_to_planet_dict,rasi1,rasi2)
    if _stronger_rasi is not None:
        return _stronger_rasi
    """ Rule-6: The rasi owned by the planet with the higher advancement of longitude is stronger. """
    #print("Upto Rule 5 - not met. Stronger Rasi to be found from stronger_co_lords",rasi1,rasi2)
    lord_of_rasi1 = house_owner(house_to_planet_dict, rasi1) # const.house_owners[rasi1]
    lord_of_rasi2 = house_owner(house_to_planet_dict, rasi2) #const.house_owners[rasi2]
    sp = stronger_co_lord_from_planet_positions(planet_positions, lord_of_rasi1, lord_of_rasi1)
    if sp is None:
        print('could not find stronger co lord',lord_of_rasi1,lord_of_rasi2)
    if sp == lord_of_rasi1:
        return rasi1
    else:
        return rasi2
     
def stronger_rasi_new(house_to_planet_dict,rasi1,rasi2):
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
    """
    lord_of_rasi1 = house_owner(house_to_planet_dict, rasi1) # V2.3.1
    rasi1_planet_count = sum( ((value==rasi1) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==lord_of_rasi1)) for key,value in p_to_h.items() if key != const._ascendant_symbol)
    #print('Rule-2','rasi1',rasi1,'lord_of_rasi1',lord_of_rasi1,'rasi1_planet_count',rasi1_planet_count)
    rasi1_planet_count += len(set([3,4,lord_of_rasi1]) & set(aspected_planets_of_the_raasi(house_to_planet_dict,rasi1, separator='/')))
    #print('Rule-2','rasi1',rasi1,'lord_of_rasi1',lord_of_rasi1,'rasi1_planet_count incl aspects',rasi1_planet_count,aspected_planets_of_the_raasi(house_to_planet_dict,rasi1))
    lord_of_rasi2 = house_owner(house_to_planet_dict, rasi2) # V2.3.1
    rasi2_planet_count = sum( ((value==rasi2) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==lord_of_rasi2)) for key,value in p_to_h.items() if key != const._ascendant_symbol)
    
    #print('Rule-2','rasi2',rasi2,'lord_of_rasi2',lord_of_rasi2,'rasi2_planet_count',rasi2_planet_count)
    rasi2_planet_count += len(set([3,4,lord_of_rasi2]) & set(aspected_planets_of_the_raasi(house_to_planet_dict,rasi2, separator='/')))
    #print('Rule-2','rasi2',rasi2,'lord_of_rasi2',lord_of_rasi2,'rasi2_planet_count incl aspects',rasi2_planet_count,aspected_planets_of_the_raasi(house_to_planet_dict,rasi2))
    """
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
    if rasi1_planet_count > rasi2_planet_count:
        #print('Rule-2 Rasi1',rasi1,'is stronger')
        return rasi1
    elif rasi2_planet_count > rasi1_planet_count:
        #print('Rule-2 Rasi2',rasi2,'is stronger')
        return rasi2
    #print('Rule-2: Both rasis have same aspect/cojoin count')
    """
    lord_of_rasi1 = house_owner(house_to_planet_dict, rasi1) # V2.3.1
    rasi1_planet_count = sum( ((value==rasi1) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==lord_of_rasi1)) for key,value in p_to_h.items() if key != const._ascendant_symbol)
    #print('Rule-2','rasi1',rasi1,'lord_of_rasi1',lord_of_rasi1,'rasi1_planet_count',rasi1_planet_count)
    rasi1_planet_count += len(set([3,4,lord_of_rasi1]) & set(aspected_planets_of_the_raasi(house_to_planet_dict,rasi1, separator='/')))
    #print('Rule-2','rasi1',rasi1,'lord_of_rasi1',lord_of_rasi1,'rasi1_planet_count incl aspects',rasi1_planet_count,aspected_planets_of_the_raasi(house_to_planet_dict,rasi1))
    lord_of_rasi2 = house_owner(house_to_planet_dict, rasi2) # V2.3.1
    rasi2_planet_count = sum( ((value==rasi2) and (value==p_to_h[3]) and (value==p_to_h[4]) \
                                   and (value==lord_of_rasi2)) for key,value in p_to_h.items() if key != const._ascendant_symbol)
    
    #print('Rule-2','rasi2',rasi2,'lord_of_rasi2',lord_of_rasi2,'rasi2_planet_count',rasi2_planet_count)
    rasi2_planet_count += len(set([3,4,lord_of_rasi2]) & set(aspected_planets_of_the_raasi(house_to_planet_dict,rasi2, separator='/')))
    #print('Rule-2','rasi2',rasi2,'lord_of_rasi2',lord_of_rasi2,'rasi2_planet_count incl aspects',rasi2_planet_count,aspected_planets_of_the_raasi(house_to_planet_dict,rasi2))
    """
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
    else:
        if rasi2 not in const.movable_signs:
            #print('Rule-5 rasi2',rasi2,'is stronger')
            return rasi2
    """ Rule-6: The rasi owned by the planet with the higher advancement of longitude is stronger. """
    print("WARNING: Rule (6) of house.stronger_rasi not implmented. So returning first rasi as stronger.\nResults can be wrong")
    sp = stronger_co_lord(house_to_planet_dict, lord_of_rasi1, lord_of_rasi2)
    if sp == lord_of_rasi1:
        return rasi1
    else:
        return rasi2
def natural_friends_of_planets():
    return const.friendly_planets
def natural_neutral_of_planets():
    return const.neutral_planets
def natural_enemies_of_planets():
    return const.enemy_planets
def _temporary_friends_of_planets_from_chart(chart):
    h_p = utils.get_planet_to_house_dict_from_chart(chart)
    tfl = []
    for p in range(7):
        z = h_p[p]
        tf = []
        for zz in const.temporary_friend_raasi_positions:
            z1 = (z+zz-1)%12
            pls = chart[z1].split('/')
            pls = [p1 for p1 in pls  if p1 not in [str(p),const._ascendant_symbol,'7','8','']]
            for p2 in pls:
                if p2 not in [str(p),const._ascendant_symbol,'7','8','']:
                    tf.append(int(p2))
        tfl.append(tf)
    return tfl
def _temporary_enemies_of_planets_from_chart(chart):
    h_p = utils.get_planet_to_house_dict_from_chart(chart)
    tfl = []
    for p in range(7):
        z = h_p[p]
        tf = []
        for zz in const.temporary_enemy_raasi_positions:
            z1 = (z+zz-1)%12
            pls = chart[z1].split('/')
            pls = [p1 for p1 in pls  if p1 not in [str(p),const._ascendant_symbol,'7','8','']]
            for p2 in pls:
                if p2 not in [str(p),const._ascendant_symbol,'7','8','']:
                    tf.append(int(p2))
        tfl.append(tf)
    return tfl
def house_owner(h_to_p,sign):
    lord_of_sign = const.house_owners[sign]
    l_o_s = lord_of_sign
    #print('sign',sign,'lord_of_sign',lord_of_sign)
    if sign==7:
        lord_of_sign = stronger_co_lord(h_to_p,2,8) #MArs and Ketu
        #print('Stronger in Scorpio',lord_of_sign)
    elif sign==10:
        lord_of_sign = stronger_co_lord(h_to_p,6,7)#Saturn and Rahu
        #print('Stronger in Aquarius',lord_of_sign)
    """ Added checking Aq/Sc Stronger co-lord checking in V2.3.1 """
    """
    if sign in [7,10]: ## If rasi1 is Aq or Sc there are two lords
        print('house in [7,10]')
        rahu_kethu_house = list(const.houses_of_rahu_kethu.keys())[list(const.houses_of_rahu_kethu.values()).index(sign)]
        print('rahu_kethu_house',rahu_kethu_house,'lord_of_sign',lord_of_sign)
        lord_of_sign = stronger_co_lord(h_to_p, lord_of_sign,rahu_kethu_house)
    """
    if lord_of_sign==None:
        print('Rule (5) Requires longitudes of planets which are not provided, hence house.house_owner returning None')
        print('h_to_p',h_to_p,'sign',sign,'lord_of_sign',lord_of_sign)
        print('Warning: Returning lord of sign as owner of house',l_o_s,' without checking Sc/Aq stronger lord')
        return l_o_s
        #exit()
    return lord_of_sign
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
    #_rudra = stronger_co_lord(h_to_p, eighth_house_lord, seventh_house_lord, False, eighth_house_lord_longitude, seventh_house_lord_longitude)
    _rudra = stronger_co_lord_from_planet_positions(planet_positions, eighth_house_lord, seventh_house_lord, check_during_dhasa=False)
    _rudra_sign = p_to_h[_rudra]
    trishoola_rasis = trines_of_the_raasi(_rudra_sign)
    return _rudra, _rudra_sign,trishoola_rasis
    
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
    _rudra = stronger_co_lord_from_planet_positions(planet_positions, eighth_house_lord, seventh_house_lord)
    #print('Stronger of ',planet_list[eighth_house_lord],'and',planet_list[seventh_house_lord],'is',planet_list[_rudra])
    _rudra_sign = p_to_h[_rudra]
    trishoola_rasis = trines_of_the_raasi(_rudra_sign)
    return _rudra, _rudra_sign,trishoola_rasis
def trishoola_rasis(h_to_p):
    return trines_of_the_raasi(rudra(h_to_p)[1])
def maheshwara(dob,tob,place,divisional_chart_factor=1): #jd,place,divisional_chart_factor=1):
    jd = utils.julian_day_number(dob, tob)
    _chara_karakas = chara_karakas(jd, place, divisional_chart_factor)
    atma_karaka = [key for key in _chara_karakas.keys() if _chara_karakas[key]==0][0]
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
        _maheshwara = stronger_co_lord(h_to_p, atma_8th_lord, atma_12th_lord)#, check_during_dhasa, planet1_longitude, planet2_longitude)
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
    hora_lagna_house = drik.hora_lagna(jd,place,time_of_birth_in_hours,divisional_chart_factor)[0] # only rasi part not longitude
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
if __name__ == "__main__":
    """
    chart_8 = ['','7','','6','','','3/4/5','L/0/2/8','','','1','']
    chart_8_pp = [['L',[7,13+14/60]],]
    r = rudra(chart_8)
    print('Rudra planet and Rasi',r)
    exit()
    """
    place = drik.Place('unknown',15+39/60, 38+6/60, +1.0)
    dob = drik.Date(1946,12,2)
    tob = (6,45,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd = swe.julday(dob.year,dob.month,dob.day, time_of_birth_in_hours)
    divisional_chart_factor = 1
    chart_8 = ['','7','','6','','','3/4/5','L/0/2/8','','','1','']
    print('marakas',marakas(chart_8))
    print('rudra',rudra_based_on_planet_positions(dob, tob, place, divisional_chart_factor=divisional_chart_factor))
    print('maheshwara',maheshwara(dob, tob, place, divisional_chart_factor))
    print('longevity',longevity(dob,tob,place,divisional_chart_factor=1))
    exit()
    ascendant_index = const._ascendant_symbol
    planet_positions = drik.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = drik.ascendant(jd,place)[1]
    asc_house,asc_long = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[ascendant_index,(asc_house,asc_long)]]
    exit()
    _m = maheshwara(dob,tob,place,divisional_chart_factor=1) #jd,place,divisional_chart_factor=1)
    print('Maheshwara Planet',planet_list[_m])
    #r = rudra_based_on_planet_positions(pp)
    #print('Rudra Planet',planet_list[r[0]],rasi_names_en[r[1]])
    chart_12 = ['6','0','2','1','4','','7','','8','3','5','L']
    r = rudra(chart_12)
    print('Rudra Planet',planet_list[r[0]],rasi_names_en[r[1]],chart_12)
    ck = chara_karakas(jd, place, 1)
    print(ck)
    exit()
    chapter = 'Chapter 15.5.2 stronger_Lord_tests Exercise 25/Chart 12'
    # Exercise 26
    chart_12 = ['8','5','2','','L','','7','4','3/1/6','0','','']
    chart_12 = ['6','0','2','1','4','','7','','8','3','5','L']
    print(marakas(chart_12))
    exit()
    print(chart_12)
    stronger_planet = stronger_co_lord(chart_12, const._SATURN, 7)#, check_during_dhasa, planet1_longitude, planet2_longitude)
    print(planet_list[stronger_planet],'is stronger of Saturn and Rahu', )
    stronger_planet = stronger_co_lord(chart_12, const._MARS, 8)#, check_during_dhasa, planet1_longitude, planet2_longitude)
    print(planet_list[stronger_planet],'is stronger of Mars and Kethu', )
    exit()
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
    place = drik.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    dob = drik.Date(1996,12,7)
    tob = (10,34,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd = swe.julday(dob.year,dob.month,dob.day, time_of_birth_in_hours)
    divisional_chart_factor = 1
    ascendant_index = const._ascendant_symbol
    planet_positions = drik.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = drik.ascendant(jd,place)[1]
    asc_house,asc_long = drik.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
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
    ck = chara_karakas(jd, place, 1)
    print('chara_karakas',ck)
    print('trikonas',trikonas())
    print('kendras',kendras())
    print('upachayas',upachayas())        
    print('dushthanas',dushthanas())
    print('chathusras',chathusras())