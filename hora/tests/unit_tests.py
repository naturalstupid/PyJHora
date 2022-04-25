import swisseph as swe
from hora import const, utils
from hora.horoscope.dhasa import sudasa, moola,drig,nirayana,shoola,kalachakra,vimsottari,patyayini, mudda,narayana, sudharsana_chakra
from hora.horoscope.chart import arudhas, house, charts, ashtakavarga
from hora.panchanga import panchanga
from hora.horoscope.transit import tajaka, saham, tajaka_yoga
# ----- panchanga TESTS ------
bangalore = panchanga.Place('Bangalore',12.972, 77.594, +5.5)
shillong = panchanga.Place('shillong',25.569, 91.883, +5.5)
helsinki = panchanga.Place('helsinki',60.17, 24.935, +2.0)
date1 = panchanga.gregorian_to_jd(panchanga.Date(2009, 7, 15))
date2 = panchanga.gregorian_to_jd(panchanga.Date(2013, 1, 18))
date3 = panchanga.gregorian_to_jd(panchanga.Date(1985, 6, 9))
date4 = panchanga.gregorian_to_jd(panchanga.Date(2009, 6, 21))
apr_8 = panchanga.gregorian_to_jd(panchanga.Date(2010, 4, 8))
apr_10 = panchanga.gregorian_to_jd(panchanga.Date(2010, 4, 10))
def panchanga_tests():
  tithi_tests()
  nakshatra_tests()
  yoga_tests()
  masa_tests()
  print(panchanga.moonrise(date2, bangalore)) # Expected: 11:28:06
  print(panchanga.moonset(date2, bangalore))  # Expected: 24:12:48
  print(panchanga.sunrise(date2, bangalore)[1])  # Expected:  6:47:20
  print(panchanga.sunset(date2, bangalore)[1])   # Expected: 18:12:58
  #assert(panchanga.vaara(date2) == 5)
  print(panchanga.vaara(date2))
  print(panchanga.sunrise(date4, shillong)[1])   # On this day, Nakshatra and Yoga are skipped!
#  assert(panchanga.karana(date2, helsinki) == [14])   # Expected: 14, Vanija
  print(panchanga.karana(date2, helsinki))
  return

def tithi_tests():
  feb3 = panchanga.gregorian_to_jd(panchanga.Date(2013, 2, 3))
  apr24 = panchanga.gregorian_to_jd(panchanga.Date(2010, 4, 24))
  apr19 = panchanga.gregorian_to_jd(panchanga.Date(2013, 4, 19))
  apr20 = panchanga.gregorian_to_jd(panchanga.Date(2013, 4, 20))
  apr21 = panchanga.gregorian_to_jd(panchanga.Date(2013, 4, 21))
  bs_dob = panchanga.gregorian_to_jd(panchanga.Date(1996,12,7))
  chennai = panchanga.Place('chennai',13.0389,80.2619,5.5)
  print('Expected: krishna ashtami (23), ends at 27:07:09',panchanga.tithi(date1, bangalore))  # Expected: krishna ashtami (23), ends at 27:07:09
  print(panchanga.tithi(date2, bangalore))  # Expected: Saptami, ends at 16:24:04
  print(panchanga.tithi(date3, bangalore))  # Expected: Krishna Saptami, ends at 25:03:22
  print('Expected: Shukla saptami until 12:54:04',panchanga.tithi(date2, helsinki))   # Expected: Shukla saptami until 12:54:04
  print(panchanga.tithi(apr24, bangalore))  # Expected: [10, [6,9,18], 11, [27, 33, 50]]
  print(panchanga.tithi(feb3, bangalore))   # Expected: [22, [8,13,52], 23, [30, 33, 6]]
  print('Expected: [9, [28, 44, 60]]',panchanga.tithi(apr19, helsinki))   # Expected: [9, [28, 44, 60]]
  print(panchanga.tithi(apr20, helsinki))   # Expected: [10, - ahoratra -]
  print(panchanga.tithi(apr21, helsinki))   # Expected: [10, [5, 22, 6]]
  print('bhuvana dob',panchanga.tithi(bs_dob,chennai))
  return

def nakshatra_tests():
  print(panchanga.nakshatra(date1, bangalore))  # Expected: 27 (Revati), ends at 17:06:24
  print(panchanga.nakshatra(date2, bangalore))  # Expected: 27 (Revati), ends at 19:22:54
  print(panchanga.nakshatra(date3, bangalore))  # Expecred: 24 (Shatabhisha) ends at 26:32:36
  print(panchanga.nakshatra(date4, shillong))   # Expected: [3, [5,0,59]] then [4,[26,31,00]]
  return

def yoga_tests():
  may22 = panchanga.gregorian_to_jd(panchanga.Date(2013, 5, 22))
  print(panchanga.yoga(date3, bangalore))  # Expected: Vishkambha (1), ends at 22:59:38
  print(panchanga.yoga(date2, bangalore))  # Expected: Siddha (21), ends at 29:10:40
  print(panchanga.yoga(may22, helsinki))   # [16, [6,20,25], 17, [27,21,53]]

def masa_tests():
  jd = panchanga.gregorian_to_jd(panchanga.Date(2013, 2, 10))
  aug17 = panchanga.gregorian_to_jd(panchanga.Date(2012, 8, 17))
  aug18 = panchanga.gregorian_to_jd(panchanga.Date(2012, 8, 18))
  sep19 = panchanga.gregorian_to_jd(panchanga.Date(2012, 9, 18))
  may20 = panchanga.gregorian_to_jd(panchanga.Date(2012, 5, 20))
  may21 = panchanga.gregorian_to_jd(panchanga.Date(2012, 5, 21))
  print(panchanga.maasa(jd, bangalore))     # Pusya (10)
  print(panchanga.maasa(aug17, bangalore))  # Shravana (5) amavasya
  print(panchanga.maasa(aug18, bangalore))  # Adhika Bhadrapada [6, True]
  print(panchanga.maasa(sep19, bangalore))  # Normal Bhadrapada [6, False]
  print(panchanga.maasa(may20, helsinki))   # Vaisakha [2]
  print(panchanga.maasa(may21, helsinki))   # Jyestha [3]
  
def stronger_rasi_tests():
    chart_12 = ['8','5','','','','L','7','2/4','3/1','0','','6']
    rasi_names_en = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    # Ar is stronger by Rule-2
    rasi1 = 0
    rasi2 = 6
    # Sc is stronger than Ta, from rule (1).
    print('stronger rasi',house.stronger_rasi(chart_12, rasi1, rasi2))
    rasi1 = 1
    rasi2 = 7
    # Sg is stronger than Ta, from rule (1).
    print('stronger rasi',house.stronger_rasi(chart_12, rasi1, rasi2))
    rasi1 = 2
    rasi2 = 8
    # Cp is stronger than Cn, from rule (1).
    print('stronger rasi',house.stronger_rasi(chart_12, rasi1, rasi2))
    rasi1 = 3
    rasi2 = 9
    # Le is stronger than Aq from rule (2).
    print('stronger rasi',house.stronger_rasi(chart_12, rasi1, rasi2))
    rasi1 = 4
    rasi2 = 10
    # Pi is stronger than Vi, from rule (1).
    print('stronger rasi',house.stronger_rasi(chart_12, rasi1, rasi2))
    rasi1 = 5
    rasi2 = 11
    print('stronger rasi',house.stronger_rasi(chart_12, rasi1, rasi2))
def moola_dhasa_tests():
    dob = (1912,1,1)
    chart_34 = ['6/1/7','','','','','','8/4','L','2/3','0','5','']
    # Ans:           Ta Aq Sc Le Ar Cp Li Cn Pi Sg Vi Ge    
    # Ans: Dasa years 9 10 11 7  8  8  4  3  5  10  9  6
    print('moola dhasa test\n')
    print(chart_34)
    kd = moola.moola_dhasa(chart_34,dob)    
    for p in kd:
        print(p)
def sudasa_dhasa_tests():
    # Chart 3 chart of Vajpayee
    chart_3 = ['2','','7','','1','','','3/L/6','5/0/8','','4','']
    print('sudasa_dhasa_tests','chart_3',chart_3)
    sree_lagna_house = 9
    sree_lagna_longitude = 282+21.0/60
    dob = (1926,12,25)
    #Ans: Cp:1.18,Li:2,Cn:11,Ar:12,Sg:2,Vi:10,Ge:5,Pi:1,Sc:2,Le:8,Ta:7,Aq:3
    #SL is at 12°21' in Capricorn. The fraction of the first dasa left at birth = (30° – 12°21'/30° = (1800 – 741)/1800*2 = 1.18
    sd = sudasa.sudasa_dhasa(chart_3,sree_lagna_house, sree_lagna_longitude, dob)    
    for p in sd:
        print(p)
def graha_arudha_tests():
    chart_bs_9 = ['7','5','3','L','','6','8','2/4','1','0','','']
    #Ans: AL to UL, A1..A12. [1,2,8,8,5,6,1,0,3,2,10,11]
    ba = arudhas.bhava_arudhas(chart_bs_9)
    print('chart BS 9 bhava arudha',ba)
    chart_1 = ['4/2/6','','1','7','','L','','','','8','','3/0/5']
    ba = arudhas.bhava_arudhas(chart_1)
    print('chart 1 bhava arudha',ba)
    #Ans A1/AL:Ge, A2:Le, A3:Vi, A4:Le, A5:Ar, A6:Ge, A7:Ta, A8:Cp, A9:Cp, A10:Vi, A11: Ta, A12:Li
    asc_house = 5
    houses = [(h + asc_house) % 12 for h in range(12)] 
    for i, h in enumerate(houses):
        print('bhava arudha:', 'A' + str(i + 1), 'is', house.rasi_names_en[ba[i]])
    ga = arudhas.graha_arudhas(chart_1)
    for p,planet in enumerate(house.planet_list):
        print('graha padha of',planet,'is',house.rasi_names_en[ga[p]])

    chart_2 = ['6','5','','7/8','','','','','3/L','4','0/1/2','']
    # Ans AL in Aq, A2 in Ar, A3 in Sg, A4 in Sc, A5 in Sg, A6 in Aq, A7 in Pi, A8 in Vi, A9 in Ta, A10 in Sg, A11 in Sg, UL in Aq.
    asc_house = 8
    ba = arudhas.bhava_arudhas(chart_2)
    print('chart 2 bhava arudha',ba)
    houses = [(h + asc_house) % 12 for h in range(12)] 
    for i, h in enumerate(houses):
        print('bhava arudha:', 'A' + str(i + 1), 'is', house.rasi_names_en[ba[i]])
    
    # Ans: Sun – Sc, Moon – Sg, Mars – Ge, Mercury – Vi, Jupiter – Sc, Venus – Aq, Saturn – Sg, Rahu – Vi, Ketu – Pi.
    ga = arudhas.graha_arudhas(chart_2)
    for p,planet in enumerate(house.planet_list):
        print('graha padha of',planet,'is',house.rasi_names_en[ga[p]])
def drig_dhasa_tests():
    chart_36 = ['','8','6','','5','2/0','3/L','7','','1','4','']
    # Ans: Ge, Vi, Sg, Pi, Cn, Ta, Aq, Sc, Le, Ar, Cp, Li.
    # Ans: 2,5,8,11,3,1,10,7,4,0,9,6
    print('drig dhasa test\n',drig.drig_dhasa(chart_36,(1912,1,1)))
    chart_37 = ['6','','','','8','','','4/2/5','3','0/1','7/L','']
    # Ans: Li, Aq, Ta, Le, Sc, Cp, Ar, Cn, Sg, Pi, Ge, Vi
    print(drig.drig_dhasa(chart_37,(1971,26,1)))
def nirayana_shoola_dhasa_tests():
    chart_8 = ['','7','','6','','','4/3/5','0/L/8/2','','','1','']
    #Ans: Sg (9), Cp(7), Aq(8), Pi(9), Ar(7), Ta(8), Ge(9) etc
    sd = nirayana.nirayana_shoola_dhasa(chart_8, (1946,12,2))
    print('nirayana shoola dhasa test\n',sd)
def sudharsana_chakra_dhasa_tests():
    # Excercise 48
    dob = (1970,10,28)
    tob = (17,50,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    place = panchanga.Place('unknown',16+15.0/60, 81+12.0/60, +5.5)
    years_from_dob = 17
    divisional_chart_factor = 24
    jd_at_dob = swe.julday(dob[0],dob[1],dob[2], time_of_birth_in_hours)
    jd_at_years = jd_at_dob + years_from_dob * const.sidereal_year
    lsd,msd,ssd = sudharsana_chakra.sudharsana_chakra_dhasa_for_divisional_chart(jd_at_dob,place,dob,years_from_dob,divisional_chart_factor)
    print('sudharsana_chakra_dhasa tests\n')#,sd)
    print('sudharsana_chakra_dhasa - Lagna')
    for dh,ad,dd,ds in lsd:
        for adh,add,ads in ad:
            print(adh,add,ads)
        print(dh,dd,ds)
    pad = sudharsana_chakra.sudharsana_pratyantardasas(jd_at_years,7)
    print(pad)
    print('sudharsana_chakra_dhasa - Moon')
    for dh,ad,dd,ds in msd:
        for adh,add,ads in ad:
            print(adh,add,ads)
        print(dh,dd,ds)
    pad = sudharsana_chakra.sudharsana_pratyantardasas(jd_at_years,4)
    print(pad)
    print('sudharsana_chakra_dhasa - Sun')
    for dh,ad,dd,ds in ssd:
        for adh,add,ads in ad:
            print(adh,add,ads)
        print(dh,dd,ds)
    pad = sudharsana_chakra.sudharsana_pratyantardasas(jd_at_years,0)
    print(pad)
def narayana_dhasa_tests():
    # Chart 24 - Bill Gates
    """
    dob = (1955,10,28)
    tob = (21,18,0)
    place = panchanga.Place('unknown',47+36.0/60, -122.33, -8.0)
    divisional_chart_factor = 1
    """
    """
    # Chart 25 - India's indepdendence
    dob = (1947,8,15)
    tob = (0,0,0)
    place = panchanga.Place('unknown',27.0, 78.5, +5.5)
    divisional_chart_factor = 1
    """
    #"""
    # Chart 27
    dob = (1972,6,1)
    tob = (4,16,0)
    years = 21
    place = panchanga.Place('unknown',16+15.0/60, 81+12.0/60, +5.5)
    divisional_chart_factor = 9
    #Ans : 7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], 
    #[8, '1996-6-1', '2000-6-1', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 4]
    #[9, '2000-6-1', '2002-6-1', [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10], 2]
    #[10, '2002-6-1', '2005-6-1', [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 3]
    #[11, '2005-6-1', '2016-6-1', [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], 11]
    #"""
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd_at_dob = swe.julday(dob[0],dob[1],dob[2], time_of_birth_in_hours)
    jd_at_years = jd_at_dob + years * const.sidereal_year
    nd = narayana.narayana_dhasa_for_divisional_chart(jd_at_dob,place,dob,years,divisional_chart_factor)
    print('varsha narayana dhasa tests')
    for p in nd:
        print(p)    
def shoola_dhasa_tests():  
    chart_8 = ['','7','','6','','','4/3/5','0/L/8/2','','','1','']
    # Ans Sc, Sg, Cp, Aq etc each 9 years
    sd = shoola.shoola_dhasa(chart_8, (1946,12,2))
    print('shoola dhasa\n',sd)
def kalachakra_dhasa_tests():
    # Example_95
    lunar_longitude = 45+50/60.0
    dob = (1912,1,1)
    kd = kalachakra.kalachakra_dhasa(lunar_longitude,dob)
    #Ans:Sc(4.75),Li(16),Vi, Le, Cn, Ge, Ta, Ar, Sg [9, 5, 21, 9, 16, 7, 10]
    print('kalachakra dhasa test\n',kd)
    # Example_96
    lunar_longitude = 93.0
    #Ans Pi(8.6) Sc, Li, Vi, Cn, Le, Ge, Ta, Ar [ 7, 16, 9, 21, 5, 9, 16, 7]
    kd = kalachakra.kalachakra_dhasa(lunar_longitude,dob)
    print('kalachakra dhasa test\n',kd)
def utils_tests():
    # should return location based on IP addressm, todays date and time dvf=1
    result = utils._validate_data(place=None,latitude=None,longitude=None,time_zone_offset=None,dob=None,tob=None,division_chart_factor=None)
    print(result)
    result = utils._validate_data(place='Karamadai',latitude=None,longitude=None,time_zone_offset=None,dob=None,tob=None,division_chart_factor=4)
    print(result)
    #And: Karamadai  11.2428 76.9587 5.5 Date(year=2022, month=3, day=31) ('12', '55', '45.425760') 4
def chart_tests():    
    dob = panchanga.Date(1967,3,8)
    tob = (17,40,0)
    lat=73+4/60.0
    long=26+18.0/60
    tz = 5.5
    place = panchanga.Place('unknown',lat,long,tz)
    print(place)
    jd = panchanga.julian_day_number(dob,tob)
    print(jd)
    cht = charts.divisional_chart(jd_at_dob=jd, place_as_tuple=place, ayanamsa_mode='Lahiri', divisional_chart_factor=1)
    print(cht)
def vimsottari_adhipati_tests():
    # nakshatra indexes counted from 0
    satabhisha, citta, aslesha = 23, 13, 8
    assert(vimsottari.vimsottari_adhipati(satabhisha) == swe.RAHU)
    assert(const.vimsottari_dict[vimsottari.vimsottari_adhipati(satabhisha)] == 18)
    assert(vimsottari.vimsottari_adhipati(citta) == swe.MARS)
    assert(const.vimsottari_dict[vimsottari.vimsottari_adhipati(citta)] == 7)
    assert(vimsottari.vimsottari_adhipati(aslesha) == swe.MERCURY)
    assert(const.vimsottari_dict[vimsottari.vimsottari_adhipati(aslesha)] == 17)
def ashtaka_varga_tests():
    print('ashtaka_varga_tests')
    # Exercise 18, 19 and 20
    chart_7 = ['6/1/7','','','','','','8/4','L','3/2','0','5','']
    chart_6 = ['8/5','','2/0/3','','6/4','L','7','','','','','1']
    bav, sav, pav = ashtakavarga.get_ashtaka_varga(chart_6,False)
    print('binna ashtaka varga\n',bav)
    print('samudhaya ashtaka varga\n',bav)
    print('prastara ashtaka varga\n',pav)
    sp = ashtakavarga.sodhaya_pindas(bav, chart_6)
    print(sp)
    """
                    Ar Ta Ge Cn Le Vi Li Sc Sg Cp Aq Pi
            Sun     5 3 5 3 4 4 2 3 5 4 5 5
            Moon    3 2 5 3 6 3 4 5 5 5 3 5*
            Mars    4 3 4 3 4 3 2 5 1 3 3 4
            Mercury 7 4 7 4 4 3 4 4 4 3 6 4
            Jupiter 4 3 5 6 3 7 4 3 5 6 5 5
            Venus   8 7 4 3 3 2 4 6 4 4 4 3
            Saturn  3 3 4 3 2 3 2 3 4 5 3 4

                Ar Ta Ge Cn Le Vi Li Sc Sg Cp Aq Pi
            Sum 34 25 34 25 26 25 22 29 28 30 29 30            
    """
    #Exercise 21
    chart_12 = ['8','5','','','','L','7','4/2','3/0','1','','6']
def patyayini_tests():
    # Example 122 chart_67
    #Ans: [[5, 24.98], [3, 48.17], [1, 0.51], [6, 25.74], ['L', 11.24], [4, 57.35], [0, 93.29], [2, 103.99]]
    # Note: Difference in ans is due to use of sidereal year instead of book's approx method to calculate jf_at_years 
    jd_at_dob = panchanga.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = panchanga.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = 'Lahiri'
    jd_at_years = panchanga.julian_day_number((1993,6,1),(13,30,4))
    cht=patyayini.patyayini_dhasa(jd_at_years, place, ayanamsa_mode, divisional_chart_factor)
    print('patyayini_tests',cht)
def mudda_tests():
    # Example 122 chart_67
    """ SET AYANAMSA MODE FIRST """
    panchanga.set_ayanamsa_mode('LAHIRI')
    # Chart_67 
    jd_at_dob = panchanga.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = panchanga.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = 'Lahiri'
    chart_67_pp = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode, divisional_chart_factor=1)
    print(chart_67_pp)
    db=mudda.varsha_vimsottari_dhasa_bhukthi(jd_at_dob, place,years)
    # Ans - [(7, 7, '1993-06-03', 8.22), (7, 4, '1993-06-11', 7.31) ....
    print('varsha_vimsottari_tests',db)
def saham_tests():
    # Example 118 Chart 66
    dob = (2000,3,8)
    tob = (4,41,0)
    divisional_chart_factor = 1
    tob_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
    jd_at_dob = utils.julian_day_number(dob, tob)
    place_as_tuple = panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    sunrise = panchanga.sunrise(jd_at_dob, place_as_tuple, as_string=False)[1]
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = panchanga.sunset(jd_at_dob, place_as_tuple, as_string=False)[1]
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    #print(tob_hrs,'night_time_birth',night_time_birth,'sunrise',sunrise_hrs,'sunset',sunset_hrs)
    chart_66 = charts.divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri', divisional_chart_factor=divisional_chart_factor)
    print(chart_66)
    h_to_p = utils.get_house_planet_list_from_planet_positions(chart_66)
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print(p_to_h)
    asl = saham.artha_saham(chart_66,night_time_birth=night_time_birth)
    print('artha_saham_longitude',panchanga.dasavarga_from_long(asl,divisional_chart_factor))
    ssl = saham.samartha_saham(chart_66,night_time_birth=night_time_birth)
    print('smartha_saham_longitude',panchanga.dasavarga_from_long(ssl,divisional_chart_factor))
    psl = saham.punya_saham(chart_66,night_time_birth=night_time_birth)
    print('punya_saham_longitude',panchanga.dasavarga_from_long(psl,divisional_chart_factor))
    psl = saham.vidya_saham(chart_66,night_time_birth=night_time_birth)
    print('vidya_saham_longitude',panchanga.dasavarga_from_long(psl,divisional_chart_factor))
    ysl = saham.yasas_saham(chart_66,night_time_birth=night_time_birth)
    print('yasas_saham_longitude',panchanga.dasavarga_from_long(ysl,divisional_chart_factor))
    msl = saham.mitra_saham(chart_66,night_time_birth=night_time_birth)
    print('mitra_saham_longitude',panchanga.dasavarga_from_long(msl,divisional_chart_factor))
    msl = saham.mahatmaya_saham(chart_66,night_time_birth=night_time_birth)
    print('mahatmaya_saham_longitude',panchanga.dasavarga_from_long(msl,divisional_chart_factor))
    asl = saham.asha_saham(chart_66,night_time_birth=night_time_birth)
    print('asha_saham_longitude',panchanga.dasavarga_from_long(asl,divisional_chart_factor))
    bsl = saham.bhratri_saham(chart_66)
    print('bhratri_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    gsl = saham.gaurava_saham(chart_66,night_time_birth=night_time_birth)
    print('gaurava_saham_longitude',panchanga.dasavarga_from_long(gsl,divisional_chart_factor))
    bsl = saham.pithri_saham(chart_66,night_time_birth=night_time_birth)
    print('pithri_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.rajya_saham(chart_66,night_time_birth=night_time_birth)
    print('rajya_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.maathri_saham(chart_66,night_time_birth=night_time_birth)
    print('maathri_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.puthra_saham(chart_66,night_time_birth=night_time_birth)
    print('puthra_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.jeeva_saham(chart_66,night_time_birth=night_time_birth)
    print('jeeva_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.karma_saham(chart_66,night_time_birth=night_time_birth)
    print('karma_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.roga_saham(chart_66,night_time_birth=night_time_birth)
    print('roga_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.roga_sagam_1(chart_66,night_time_birth=night_time_birth)
    print('roga_saham_1_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.kali_saham(chart_66,night_time_birth=night_time_birth)
    print('kali_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.sastra_saham(chart_66,night_time_birth=night_time_birth)
    print('sastra_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.bandhu_saham(chart_66,night_time_birth=night_time_birth)
    print('bandhu_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.mrithyu_saham(chart_66)
    print('mrithyu_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.paradesa_saham(chart_66, night_time_birth)
    print('paradesa_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.paradara_saham(chart_66,night_time_birth=night_time_birth)
    print('paradara_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.vanika_saham(chart_66,night_time_birth=night_time_birth)
    print('vanika_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.karyasiddhi_saham(chart_66,night_time_birth=night_time_birth)
    print('karyasiddhi_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.vivaha_saham(chart_66,night_time_birth=night_time_birth)
    print('vivaha_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.santapa_saham(chart_66,night_time_birth=night_time_birth)
    print('santapa_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.sraddha_saham(chart_66,night_time_birth=night_time_birth)
    print('sraddha_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.preethi_saham(chart_66,night_time_birth=night_time_birth)
    print('preethi_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.jadya_saham(chart_66,night_time_birth=night_time_birth)
    print('jadya_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.vyaapaara_saham(chart_66)
    print('vyaapaara_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.sathru_saham(chart_66,night_time_birth=night_time_birth)
    print('sathru_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.jalapatna_saham(chart_66,night_time_birth=night_time_birth)
    print('jalapatna_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.bandhana_saham(chart_66,night_time_birth=night_time_birth)
    print('bandhana_saham_longitude',panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    asl = saham.apamrithyu_saham(chart_66,night_time_birth=night_time_birth)
    print('apamrithyu_saham_longitude',panchanga.dasavarga_from_long(asl,divisional_chart_factor))
    lsl = saham.laabha_saham(chart_66,night_time_birth=night_time_birth)
    print('laabha_saham_longitude',panchanga.dasavarga_from_long(lsl,divisional_chart_factor))
    # Chart 67 Vivaha Saham = 2deg 22min in Sagitarius
    dob = (1993,6,1)
    tob = (13,30,0)
    tob_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
    jd_at_dob = utils.julian_day_number(dob, tob)
    place_as_tuple = panchanga.Place('unknown',16+5.0/60,81+12.0/60,5.5)
    sunrise = panchanga.sunrise(jd_at_dob, place_as_tuple, as_string=False)[1]
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = panchanga.sunset(jd_at_dob, place_as_tuple, as_string=False)[1]
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    #print(tob_hrs,'night_time_birth',night_time_birth,'sunrise',sunrise_hrs,'sunset',sunset_hrs)
    chart_67 = charts.divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode='Lahiri', divisional_chart_factor=1)
    print(chart_67)
    h_to_p = utils.get_house_planet_list_from_planet_positions(chart_67)
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print(p_to_h)
    vsl = saham.vivaha_saham(chart_67,night_time_birth=night_time_birth)
    print('vivaha_saham_longitude',panchanga.dasavarga_from_long(vsl,1))
def harsha_bala_tests():
    chart_66 = ['6/4','','','7','','','','','','5/L/8','3/0','2/1']
    #Ans: {0: 0, 1: 15, 2: 0, 3: 10, 4: 5, 5: 10, 6: 5}
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    hb = tajaka.harsha_bala(p_to_h, new_year_daytime_start=False)
    print(hb)
def tajaka_harsha_bala_tests():
    chart_66 = ['6/4','','','7','','','','','','5/L/8','3/0','2/1']
    hb = tajaka.harsha_bala(p_to_h, new_year_daytime_start=False)
    #Ans: {0: 0, 1: 15, 2: 10, 3: 10, 4: 5, 5: 10, 6: 5}
    print(hb)    
def pancha_vargeeya_bala_tests():
    chart_66 = ['6/4','','','7','','','','','','5/L/8','3/0','2/1']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    chart_66 = ['6/2','','','7','','','','','','5/L/8','3/0','4/1']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    #Ans: {0: 7.5, 1: 15, 2: 30, 3: 15, 4: 30, 5: 22.5, 6: 0}
    print('_kshetra_bala test',tajaka._kshetra_bala(p_to_h))
    jd_at_dob = panchanga.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    jd_at_years = jd_at_dob + years * const.sidereal_year
    print(' Varsha Pravesha time after',years,'years',swe.revjul(jd_at_years)) # 4.41 AM 2000,3,8
    place = panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = 'Lahiri'
    print(tajaka.pancha_vargeeya_bala(jd_at_years,place))
def dwadhasa_vargeeya_bala_tests():    
    jd_at_dob = panchanga.julian_day_number((1996,12,7),(10,34,0))
    years = 26
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = 'Lahiri'
    dvp,dvpp = tajaka.dwadhasa_vargeeya_bala(jd_at_years,place)
    print('dwadhasa_vargeeya_bala',dvp,dvpp)
def lord_of_the_year_test():
    # Example 118 Chart 66 Lord of the year should be 2 - Mars
    jd_at_dob = panchanga.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    ld = tajaka.lord_of_the_year(jd_at_dob, place,years_from_dob=years)#,night_time_birth=True)
    print('Lord of the year',ld)    
def lord_of_the_month_test():
    # Example 118 Chart 66 Lord of the year should be 2 - Mars
    jd_at_dob = panchanga.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    months = 6
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    ld = tajaka.lord_of_the_month(jd_at_dob, place,years_from_dob=years,months_from_dob=months)#,night_time_birth=True)
    print('Lord of the month',ld)
def _ishkavala_yoga_test():
    chart_66 = ['0','','3','7','','4','8','','6','5/L','','2/1']
    print(chart_66)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    print('p_to_h',p_to_h)
    asc_house = p_to_h['L']
    print('asc_house',asc_house)
    print('ishkavala_yoga is',tajaka_yoga.ishkavala_yoga(p_to_h,asc_house))
def _induvara_yoga_test():
    chart_66 = ['','','3/0/5','','','4/7/8','','','6','L','','2/1']
    print(chart_66)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    print('p_to_h',p_to_h)
    asc_house = p_to_h['L']
    print('asc_house',asc_house)
    print('induvara_yoga is',tajaka_yoga.induvara_yoga(p_to_h,asc_house))            
def tajaka_yoga_tests():
    _ishkavala_yoga_test()
    _induvara_yoga_test()
def retrograde_combustion_tests():
    jd_at_dob = panchanga.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    cht = charts.divisional_chart(jd_at_dob,place)
    print(cht)
    print('retrograde planets',charts.planets_in_retrograde(cht))
    print('combustion planets',charts.planets_in_combustion(cht))
    cht = charts.divisional_chart(jd_at_years,place)
    print(cht)
    print('retrograde planets',charts.planets_in_retrograde(cht))
    print('combustion planets',charts.planets_in_combustion(cht))
def _tajaka_aspect_test(chart, planet1, planet2):
    ta1 = tajaka.planets_have_aspects(chart, planet1, planet2)
    print('tajaka.planets_have_aspects',ta1)
    ta2 = tajaka.planets_have_aspects(chart, planet2, planet1)
    print('tajaka.planets_have_aspects',ta2)
def _deeptamsa_test(planet_positions,planet1,planet2):
    da = tajaka.both_planets_within_their_deeptamsa(planet_positions,planet1,planet2)
    print('deeptansa_test',(planet1,planet2),da)
def ithasala_yoga_tests():
    jd_at_dob = panchanga.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = panchanga.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = 'Lahiri'
    jd_at_years = panchanga.julian_day_number((1993,6,1),(13,30,4))
    chart_67_rasi = charts.divisional_chart(jd_at_years, place, ayanamsa_mode, divisional_chart_factor=1)
    print(chart_67_rasi)
    chart_67_navamsa = charts.divisional_chart(jd_at_years, place, ayanamsa_mode, divisional_chart_factor=9)
    planet1 = 3
    planet2 = 4
    ty = tajaka_yoga.ithasala_yoga(chart_67_rasi,planet1,planet2)
    print('ithasala yoga',ty)
    planet1 = 1
    planet1_house = 4
    planet1_long = 14.0
    planet2 = 5
    planet2_house = 6
    planet2_long = 19.0
    planet_positions=[['L',(0,0)],[0,(0,0)],[1,(4,14.0)],[2,(0,0)],[3,(0,0)],[4,(0,0)],[5,(6,19.0)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
    h_to_p = {0:'L',1:'0',2:'2',3:'1',4:'3',5:'5',6:'4',7:'7',8:'8',9:'6',10:'',11:''}
    chart = ['L','0','2','1','3','5','4','7','8','8','','']
    _tajaka_aspect_test(chart, planet1, planet2)
    _deeptamsa_test(planet_positions,planet1,planet2)
    print('ithasala_yoga',tajaka_yoga.ithasala_yoga(planet_positions,planet1,planet2))
    planet1_long = 18+25.0/60 # should have Poora thasala (2)
    planet_positions=[['L',(0,0)],[0,(0,0)],[1,(4,18+25.0/60)],[2,(0,0)],[3,(0,0)],[4,(0,0)],[5,(6,19.0)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
    print('ithasala_yoga',tajaka_yoga.ithasala_yoga(planet_positions,planet1,planet2))
    planet1_long = 13+35.0/60 # should have bhavishya thasala (3)
    planet2_long = 21+20.0/60
    planet_positions=[['L',(0,0)],[0,(0,0)],[1,(4,13+35.0/60)],[2,(0,0)],[3,(0,0)],[4,(0,0)],[5,(6,21+20.0/60)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
    print('ithasala_yoga',tajaka_yoga.ithasala_yoga(planet_positions,planet1,planet2))
    iy = tajaka_yoga.get_ithasala_yoga_planet_pairs(chart_67_rasi)
    print('ithasala combinations in rasi\n',iy)
    iy = tajaka_yoga.get_ithasala_yoga_planet_pairs(chart_67_navamsa)
    print('ithasala combinations in navamsa\n',iy)
    exit()
if __name__ == "__main__":
    """
    " Rajiv Gandhi"
    dob = (1944,8,20)
    tob = (7,11,40)
    lat = 18.0+59.0/60
    lon = 72.0+49.0/60
    tz = 5.5
    tob_in_hours = tob[0]+tob[1]/60.0+tob[2]/3600.0
    place = panchanga.Place('unknown',lat,lon,tz)
    jd = panchanga.julian_day_number(dob,tob)
    cht = charts.divisional_chart(jd,place)
    print(cht)
    exit()
    """
    #"""
    utils_tests()
    panchanga_tests()
    stronger_rasi_tests()
    ashtaka_varga_tests()
    # Dhasa tests
    moola_dhasa_tests()
    graha_arudha_tests()
    sudasa_dhasa_tests()
    drig_dhasa_tests()
    narayana_dhasa_tests()
    nirayana_shoola_dhasa_tests()
    shoola_dhasa_tests()
    kalachakra_dhasa_tests()
    vimsottari_adhipati_tests()
    patyayini_tests()
    mudda_tests()
    sudharsana_chakra_dhasa_tests()
    # Other tajaka tests
    saham_tests()
    harsha_bala_tests()
    pancha_vargeeya_bala_tests()
    dwadhasa_vargeeya_bala_tests()
    lord_of_the_year_test()
    lord_of_the_month_test()
    tajaka_yoga_tests()
    retrograde_combustion_tests()
    #"""
    ithasala_yoga_tests()
    #chart_tests()