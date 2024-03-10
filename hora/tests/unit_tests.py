from datetime import datetime
from dateutil import relativedelta
import swisseph as swe
from hora import const,utils
from hora.horoscope.dhasa import ashtottari, sudasa, kendradhi_rasi,drig,nirayana,shoola,kalachakra
from hora.horoscope.dhasa import vimsottari,patyayini, mudda,narayana, sudharsana_chakra
from hora.horoscope.chart import arudhas, house, charts, ashtakavarga, raja_yoga, yoga
from hora.panchanga import drik as drig_panchanga, vratha
from hora.horoscope.transit import tajaka, saham, tajaka_yoga
from hora.const import rasi_names_en
from hora.tests import pvr_tests
# ----- panchanga TESTS ------
bangalore = drig_panchanga.Place('Bangalore',12.972, 77.594, +5.5)
shillong = drig_panchanga.Place('shillong',25.569, 91.883, +5.5)
helsinki = drig_panchanga.Place('helsinki',60.17, 24.935, +2.0)
date1 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2009, 7, 15))
date2 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 1, 18))
date3 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(1985, 6, 9))
date4 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2009, 6, 21))
apr_8 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2010, 4, 8))
apr_10 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2010, 4, 10))
_assert_result = True
def test_example(test_description,expected_result,actual_result,*extra_data_info):
    assert_result=_assert_result
    pvr_tests._total_tests += 1
    if len(extra_data_info)==0:
        extra_data_info = ''
    if assert_result:
        if expected_result==actual_result:
            print('Test#:'+str(pvr_tests._total_tests),test_description,"Expected:",expected_result,"Actual:",actual_result,extra_data_info,'Test Passed')
        else:
            pvr_tests._failed_tests += 1
            pvr_tests._failed_tests_str += str(pvr_tests._total_tests) +';'
            print('Test#:'+str(pvr_tests._total_tests),test_description,"Expected:",expected_result,"Actual:",actual_result,extra_data_info,'Test Failed')
    else:
        print('Test#:'+str(pvr_tests._total_tests),test_description,"Expected:",expected_result,"Actual:",actual_result,extra_data_info)
def panchanga_tests():
    print('panchanga_tests')
    test_example('Moon Rise Test','11:32:04 AM',drig_panchanga.moonrise(date2, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('Moon Set Test','00:08:47 AM (+1)',drig_panchanga.moonset(date2, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('Sun Rise Test','06:49:47 AM',drig_panchanga.sunrise(date2, bangalore)[1],'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('Sun Set Test','18:10:25 PM',drig_panchanga.sunset(date2, bangalore)[1],'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    #assert(drig_panchanga.vaara(date2) == 5)
    test_example('Vaara/Day Test','5',drig_panchanga.vaara(date2),'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('Sun Rise Test','04:36:17 AM',drig_panchanga.sunrise(date4, shillong)[1],'Date/Place',drig_panchanga.jd_to_gregorian(date4),shillong)
    test_example('Karana Test','14',drig_panchanga.karana(date2, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(date2),helsinki)
    return

def tithi_tests():
    print('tithi_tests')
    feb3 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 2, 3))
    apr24 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2010, 4, 24))
    apr19 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 4, 19))
    apr20 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 4, 20))
    apr21 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 4, 21))
    bs_dob = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(1996,12,7))
    place = drig_panchanga.Place('place',13.0389,80.2619,5.5)
    test_example('tithi test:',"[23, '03:07:39 AM (+1)']",drig_panchanga.tithi(date1, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date1),bangalore)
    test_example('tithi test:',"[7, '16:24:20 PM']",drig_panchanga.tithi(date2, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('tithi test:',"[22, '01:03:31 AM (+1)']",drig_panchanga.tithi(date3, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date3),bangalore)
    test_example('tithi test:',"[7, '12:54:20 PM']",drig_panchanga.tithi(date2, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(date2),helsinki)
    test_example('tithi test:',"[10, '06:09:30 AM', 11, '03:33:59 AM (+1)']",drig_panchanga.tithi(apr24, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(apr24),bangalore)
    test_example('tithi test:',"[22, '08:14:07 AM', 23, '06:33:18 AM (+1)']",drig_panchanga.tithi(feb3, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(feb3),bangalore)
    test_example('tithi test:',"[9, '04:45:00 AM (+1)']",drig_panchanga.tithi(apr19, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(apr19),helsinki)
    test_example('tithi test:',"[10, '05:22:08 AM (+1)']",drig_panchanga.tithi(apr20, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(apr20),helsinki) 
    test_example('tithi test:',"[10, '05:22:07 AM']",drig_panchanga.tithi(apr21, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(apr21),helsinki)
    test_example('tithi test:',"[27, '03:30:28 AM (+1)']",drig_panchanga.tithi(bs_dob,place),'Date/Place',drig_panchanga.jd_to_gregorian(bs_dob),place)
    return

def nakshatra_tests():
    print('nakshatra_tests')
    test_example('nakshatra_tests',"[27, 3, '17:06:38 PM', 1, 3, '17:04:38 PM (+1)']",drig_panchanga.nakshatra(date1, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date1),bangalore)
    test_example('nakshatra_tests',"[27, 2, '19:23:10 PM', 1, 2, '21:47:01 PM (+1)']",drig_panchanga.nakshatra(date2, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('nakshatra_tests',"[24, 1, '02:32:44 AM (+1)', 25, 1, '04:52:10 AM (+2)']",drig_panchanga.nakshatra(date3, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date3),bangalore)
    test_example('nakshatra_tests',"[4, 1, '02:31:14 AM (+1)', 5, 1, '23:44:40 PM (+1)']",drig_panchanga.nakshatra(date4, shillong),'Date/Place',drig_panchanga.jd_to_gregorian(date4),shillong)
    return

def yogam_tests():
    print('yogam_tests')
    may22 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 5, 22))
    test_example('yogam_tests',"[1, '22:59:46 PM']",drig_panchanga.yogam(date3, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date3),bangalore)
    test_example('yogam_tests',"[21, '05:10:57 AM (+1)']",drig_panchanga.yogam(date2, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(date2),bangalore)
    test_example('yogam_tests',"[16, '06:20:34 AM', 17, '03:21:59 AM (+1)']",drig_panchanga.yogam(may22, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(may22),helsinki)

def masa_tests():
    print('masa_tests')
    jd = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2013, 2, 10))
    aug17 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2012, 8, 17))
    aug18 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2012, 8, 18))
    sep19 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2012, 9, 18))
    may20 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2012, 5, 20))
    may21 = drig_panchanga.gregorian_to_jd(drig_panchanga.Date(2012, 5, 21))
    test_example('masa_tests',"[10, False]",drig_panchanga.lunar_month(jd, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(jd),bangalore)
    test_example('masa_tests',"[5, False]",drig_panchanga.lunar_month(aug17, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(aug17),bangalore)
    test_example('masa_tests',"[6, True]",drig_panchanga.lunar_month(aug18, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(aug18),bangalore)
    test_example('masa_tests',"[6, False]",drig_panchanga.lunar_month(sep19, bangalore),'Date/Place',drig_panchanga.jd_to_gregorian(sep19),bangalore)
    test_example('masa_tests',"[2, False]",drig_panchanga.lunar_month(may20, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(may20),helsinki)
    test_example('masa_tests',"[3, False]",drig_panchanga.lunar_month(may21, helsinki),'Date/Place',drig_panchanga.jd_to_gregorian(may21),helsinki)

def graha_drishti_tests():
    chapter = 'Chapter 10.2 graha_drishti_tests Exercise 14/Chart 4'
    print(chapter)
    # Excercise 14
    chart_5 = ['1','0','','','7','4','','2/L/6','3','5','8','']
    """ Answer
    Planet Aspected Rasis Aspected Houses Aspected Planets
    Sun Sc 1st Mars, Saturn
    Moon Li 12th —
    Mars Aq, Ta, Ge 4th, 7th, 8th Ketu, Sun
    Mercury Ge 8th —
    Jupiter Cp, Pi, Ta 3rd, 5th, 7th Venus, Sun
    Venus Cn 9th —
    Saturn Cp, Ta, Le 3rd, 7th, 10th Venus, Sun, Rahu
    """
    arp_e = {0: [7], 1: [6], 2: [10, 1, 2], 3: [2], 4: [9, 11, 1], 5: [3], 6: [9, 1, 4]} 
    ahp_e = {0: [0], 1: [11], 2: [3, 6, 7], 3: [7], 4: [2, 4, 6], 5: [8], 6: [2, 6, 9]}
    app_e = {0: ['2', '6'], 1: [], 2: ['8', '0'], 3: [], 4: ['5', '0'], 5: [], 6: ['5', '0', '7']}
    arp,ahp,app = house.graha_drishti_from_chart(chart_5)
    #print(arp,ahp,app)
    for p in range(7):
        test_example(chapter+' Aspected Rasis for '+house.planet_list[p],[house.rasi_names_en[int(r)] for r in arp_e[p]],[house.rasi_names_en[int(r)] for r in arp[p]])
        test_example(chapter+' Aspected Houses for '+house.planet_list[p],[int(r+1) for r in ahp_e[p]],[int(r+1) for r in ahp[p]])
        test_example(chapter+' Aspected Planets for '+house.planet_list[p],[house.planet_list[int(r)] for r in app_e[p]],[house.planet_list[int(r)] for r in app[p]])
        #print(house.planet_list[p],[house.rasi_names_en[int(r)] for r in arp[p]],[int(h)+1 for h in ahp[p]], [house.planet_list[int(r)] for r in app[p]])
def raasi_drishti_tests():
    chapter = 'Chapter 10.3 raasi_drishti_tests Exercise 15/Chart 5'
    print(chapter)
    chart_5 = ['1','0','','','7','4','','2/L/6','3','5','8','']
    """ Answer
        Planet Aspected Rasis Aspected Houses Aspected Planets
        Sun Cn, Li, Cp 9th, 12th, 3rd Venus
        Moon Le, Sc, Aq 10th, 1st, 4th Rahu, Mars, Saturn,
        Ketu
        Mars Cp, Ar, Cn 3rd, 6th, 9th Venus, Moon
        Mercury Pi, Ge, Vi 5th, 8th, 11th Jupiter
        Jupiter Sg, Pi, Ge 2nd, 5th, 8th Mercury
        Venus Ta, Le, Sc 7th, 10th, 1st Sun, Rahu, Mars,
        Saturn
        Saturn Cp, Ar, Cn 3rd, 6th, 9th Venus, Moon
        Rahu Li, Cp, Ar 12th, 3rd, 6th Venus, Moon
        Ketu Ar, Cn, Li 6th, 9th, 12th Moon
    """
      
    arp_e = {0: [3, 6, 9], 1: [4, 7, 10], 2: [0, 3, 9], 3: [2, 5, 11], 4: [2, 8, 11], 5: [1, 4, 7], 6: [0, 3, 9], 7: [0, 6, 9], 8: [0, 3, 6]} 
    ahp_e = {0: [8, 11, 2], 1: [9, 0, 3], 2: [5, 8, 2], 3: [7, 10, 4], 4: [7, 1, 4], 5: [6, 9, 0], 6: [5, 8, 2], 7: [5, 11, 2], 8: [5, 8, 11]}
    app_e = {0: ['5'], 1: ['7', '2', '6', '8'], 2: ['1', '5'], 3: ['4'], 4: ['3'], 5: ['0', '7', '2', '6'], 6: ['1', '5'], 7: ['1', '5'], 8: ['1']}
    arp,ahp,app = house.raasi_drishti_from_chart(chart_5)
    for p in range(9):
        test_example(chapter+' Aspected Rasis for '+house.planet_list[p],[house.rasi_names_en[int(r)] for r in arp_e[p]],[house.rasi_names_en[int(r)] for r in arp[p]])
        test_example(chapter+' Aspected Houses for '+house.planet_list[p],[int(r+1) for r in ahp_e[p]],[int(r+1) for r in ahp[p]])
        test_example(chapter+' Aspected Planets for '+house.planet_list[p],[house.planet_list[int(r)] for r in app_e[p]],[house.planet_list[int(r)] for r in app[p]])
        #print(house.planet_list[p],[house.rasi_names_en[int(r)] for r in arp[p]],[int(h)+1 for h in ahp[p]], [house.planet_list[int(r)] for r in app[p]])
def stronger_lord_tests():
    chapter = 'Chapter 15.5.2 stronger_Lord_tests Exercise 25/Chart 12'
    # Exercise 26
    chart_12 = ['8','5','','','','L','7','2/4','3/1','0','','6']
    print(chart_12)
    stronger_planet = house.stronger_planet(chart_12, const._SATURN, 7)
    test_example(chapter,house.planet_list[6],house.planet_list[stronger_planet],'is stronger of Saturn and Rahu', )
    stronger_planet = house.stronger_planet(chart_12, const._MARS, 8)
    test_example(chapter,house.planet_list[8],house.planet_list[stronger_planet],'is stronger of Mars and Ketu', )
def stronger_rasi_tests():
    chapter = 'Chapter 15.5.2 stronger_rasi_tests Exercise 26/Chart 12'
    # Exercise 26
    chart_12 = ['8','5','','','','L','7','2/4','3/1','0','','6']
    print(chart_12)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_12)
    print(p_to_h)
    print('graha drishti',house.graha_drishti_from_chart(chart_12))
    print('raasi drishti',house.raasi_drishti_from_chart(chart_12))

    # Ar is stronger by Rule-2
    rasi1 = 0
    rasi2 = 6
    # Sc is stronger than Ta, from rule (1).
    test_example(chapter+" (1) ",house.rasi_names_en[rasi1],house.rasi_names_en[house.stronger_rasi(chart_12, rasi1, rasi2)],'among',house.rasi_names_en[rasi1],house.rasi_names_en[rasi2])
    print("Explanation: Ar and Li have one planet each. There is a tie in rule (1). \n Ar is aspected by Jupiter & lord Mars. Li is aspected only by lord Venus. \n Ar is stronger than Li, from rule (2).")
    rasi1 = 1
    rasi2 = 7
    # Sg is stronger than Ta, from rule (1).
    test_example(chapter+" (2) ",house.rasi_names_en[rasi2],house.rasi_names_en[house.stronger_rasi(chart_12, rasi1, rasi2)],'among',house.rasi_names_en[rasi1],house.rasi_names_en[rasi2])
    print("Explanation: Sc has 2 planets and Ta has 1. Sc is stronger than Ta, from rule (1).")
    rasi1 = 2
    rasi2 = 8
    # Cp is stronger than Cn, from rule (1).
    test_example(chapter+" (3) ",house.rasi_names_en[rasi2],house.rasi_names_en[house.stronger_rasi(chart_12, rasi1, rasi2)],'among',house.rasi_names_en[rasi1],house.rasi_names_en[rasi2])
    print("Explanation: Sg has 2 planets and Ge is empty. Sg is stronger than Ta, from rule (1).")
    rasi1 = 3
    rasi2 = 9
    # Le is stronger than Aq from rule (2).
    test_example(chapter+" (4) ",house.rasi_names_en[rasi2],house.rasi_names_en[house.stronger_rasi(chart_12, rasi1, rasi2)],'among',house.rasi_names_en[rasi1],house.rasi_names_en[rasi2])
    print("Explanation: Cp has 1 planet and Cn is empty. Cp is stronger than Cn, from rule (1).")
    rasi1 = 4
    rasi2 = 10
    # Pi is stronger than Vi, from rule (1).
    test_example(chapter+" (5) ",house.rasi_names_en[rasi1],house.rasi_names_en[house.stronger_rasi(chart_12, rasi1, rasi2)],'among',house.rasi_names_en[rasi1],house.rasi_names_en[rasi2])
    print("Explanation: Le and Aq are empty. There is a tie after rule (1). \n Le is not aspected by any of Jupiter, Mercury and lord Sun. \n Aq is aspected by co-lord Rahu (though Saturn is the primary/stronger lord, Rahu’s aspect also counts). \n Aq is stronger than Le, from rule (2).")
    rasi1 = 5
    rasi2 = 11
    test_example(chapter+" (6) ",house.rasi_names_en[rasi2],house.rasi_names_en[house.stronger_rasi(chart_12, rasi1, rasi2)],'among',house.rasi_names_en[rasi1],house.rasi_names_en[rasi2])
    print("Explanation: Pi has 1 planet and Vi is empty. Pi is stronger than Vi, from rule (1).")
def vimsottari_tests():
    def vimsottari_tests_1():
        chapter = 'Chapter 16.4 Example 53/ Chart 18 Vimsottari Tests'
        dob = (1972,6,1)
        tob = (4,16,0)
        place = ('unknown',16.+15./60,81.+12.0/60,5.5)
        jd = utils.julian_day_number(dob, tob)
        vd = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
        expected_dhasa_planet = 0 # Sun
        test_example(chapter,vd[0][0],expected_dhasa_planet,'Sun Maha Dhasa at birth')
        end_date = datetime.strptime(vd[9][2], "%Y-%m-%d")
        start_date = datetime.strptime("1972-06-01", "%Y-%m-%d")
        delta = relativedelta.relativedelta(end_date, start_date)
        test_example(chapter+'-Balance '+house.planet_list[expected_dhasa_planet]+' Dhasa, At Birth, is',(4,9,4),(delta.years,delta.months,delta.days),'years,months,days till',vd[9][2])
    def vimsottari_tests_2():
        chapter = 'Chapter 16.4 Example 58/ Chart 23 Vimsottari Tests'
        dob = (1912,8,8)
        tob = (19,38,0)
        lat = 13.0+0.0/60
        long = 77.+35.0/60
        place = drig_panchanga.Place('unknown',lat,long,5.5)
        jd = utils.julian_day_number(dob, tob)
        vd = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
        expected_dhasa_planet = vd[0][0]
        end_date = datetime.strptime(vd[9][2], "%Y-%m-%d")
        start_date = datetime.strptime('-'.join(map(str,dob)), "%Y-%m-%d")
        delta = relativedelta.relativedelta(end_date, start_date)
        test_example(chapter+'-Balance '+house.planet_list[expected_dhasa_planet]+' Dhasa, At Birth, is',(6,10,10),(delta.years,delta.months,delta.days),'years,months,days till',vd[9][2])
    def vimsottari_tests_3():
        chapter = 'Chapter 16.4 Example 50 Vimsottari Tests'
        dob = (2000,4,28)
        tob = (5,50,0)
        lat = 13.0+0.0/60
        long = -77.+35.0/60
        place = drig_panchanga.Place('unknown',lat,long,-4.0)
        jd = utils.julian_day_number(dob, tob)
        vd = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
        expected_dhasa_planet = 2
        end_date = datetime.strptime(vd[9][2], "%Y-%m-%d")
        start_date = datetime.strptime('-'.join(map(str,dob)), "%Y-%m-%d")
        delta = relativedelta.relativedelta(end_date, start_date)
        test_example(chapter+'-Balance '+house.planet_list[expected_dhasa_planet]+' Dhasa, At Birth, is',(2,2,29),(delta.years,delta.months,delta.days),'years,months,days till',vd[9][2])
        #test_example(chapter+'-Balance Sun Dhasa, At Birth, is',(4,9,4),(delta.years,delta.months,delta.days),'years,months,days')
    vimsottari_tests_1()
    vimsottari_tests_2()
    vimsottari_tests_3()
def ashtottari_tests():
    chapter = 'Chapter 17.3 ashtottari_tests '
    def ashtottari_tests_1():
        example = 'Example 62 PV Narasimha Rao - Chart 6'
        chart_pv_narasimha_rao = []
        dob = (1921,6,28)
        tob = (12,49,0)
        lat = 18.0+26.0/60
        long = 79.+9.0/60
        " Expected Answer Mercury Dhasa during 1981-1997"
        place = drig_panchanga.Place('unknown',lat,long,5.5)
        jd = utils.julian_day_number(dob, tob)
        ad = ashtottari.get_ashtottari_dhasa_bhukthi(jd, place)
        actual_results = (ad[41][0],ad[41][2].split('-')[0],ad[48][2].split('-')[0])
        expected_results = (3,1978,1994)
        test_example(chapter+example,expected_results,actual_results)
    def ashtottari_tests_2():    
        example = 'Example 60 - BV Raman - Chart 23'
        dob = (1912,8,8)
        tob = (19,38,0)
        lat = 13.0+0.0/60
        long = 77.+35.0/60
        place = drig_panchanga.Place('unknown',lat,long,5.5)
        jd = utils.julian_day_number(dob, tob)
        " Expected Answer Rahu Dhasa during 1998"
        pp = charts.rasi_chart(jd, place)
        ad = ashtottari.get_ashtottari_dhasa_bhukthi(jd, place)
        actual_results = (ad[41][0],ad[41][2].split('-')[0],ad[48][2].split('-')[0])
        expected_results = (7,1998,1998)
        test_example(chapter+example,expected_results,actual_results)
    def ashtottari_tests_3():    
        example = 'Example 61 Indira Gandhi - Chart 61'
        dob = (1917,11,19)
        tob = (23,3,0)
        lat = 25.0+28.0/60
        long = 81.+52.0/60
        place = drig_panchanga.Place('unknown',lat,long,5.5)
        jd = utils.julian_day_number(dob, tob)
        " Expected Answer Moon Dhasa during 1980-1994"
        ad = ashtottari.get_ashtottari_dhasa_bhukthi(jd, place)
        actual_results = (ad[41][0],ad[41][2].split('-')[0],ad[48][2].split('-')[0])
        expected_results = (1,1980,1994)
        test_example(chapter+example,expected_results,actual_results)
    ashtottari_tests_1()
    ashtottari_tests_2()
    ashtottari_tests_3()
def kendradhi_rasi_dhasa_tests():
    chapter = 'Chapter 19.3 kendradhi_rasi_dhasa tests '
    exercise = 'Example 76 / Chart 34'
    dob = (1912,1,1)
    chart_34 = ['6/1/7','','','','','','8/4','L','2/3','0','5','']
    # Ans:           Ta Aq Sc Le Ar Cp Li Cn Pi Sg Vi Ge    
    # Ans: Dasa years 9 10 11 7  8  8  4  3  5  10  9  6
    expected_result = [(1,9),(10,9),(7,11),(4,7),(0,8),(9,8),(6,4),(3,3),(11,5),(8,10),(5,9),(2,6)]
    #print(chart_34)
    kd = kendradhi_rasi.kendradhi_rasi_dhasa(chart_34,dob)    
    for pe,p in enumerate(kd[:len(expected_result)]):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
def sudasa_dhasa_tests():
    chapter = 'Chapter 20 Sudasa tests '
    exercise ='Example 77 / Chart 3 ' 
    # Chart 3 chart of Vajpayee
    chart_3 = ['2','','7','','1','','','3/L/6','5/0/8','','4','']
    #print('sudasa_dhasa_tests','chart_3',chart_3)
    sree_lagna_house = 9
    sree_lagna_longitude = 282+21.0/60
    dob = (1926,12,25)
    #Ans: Cp:1.18,Li:2,Cn:11,Ar:12,Sg:2,Vi:10,Ge:5,Pi:1,Sc:2,Le:8,Ta:7,Aq:3
    expected_result = [(9,1.18),(6,2),(3,11),(0,12),(8,2),(5,10),(2,5),(11,1),(7,2),(4,8),(1,7),(10,3)]
    #SL is at 12°21' in Capricorn. The fraction of the first dasa left at birth = (30° – 12°21'/30° = (1800 – 741)/1800*2 = 1.18
    sd = sudasa.sudasa_dhasa(chart_3,sree_lagna_house, sree_lagna_longitude, dob)    
    for pe,p in enumerate(sd[:len(expected_result)]):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
def bhava_graha_arudha_tests():
    chapter = 'Chapter 9.2 Bhava/Graha Arudhas '
    chart_1 = ['4/2/6','','1','7','','L','','','','8','','3/0/5']
    chart_2 = ['6','5','','7/8','','','','','3/L','4','1/0/2','']
    def bhava_arudha_tests_1():
        exercise = 'Example 29 / Chart 1 Bhava Arudha'
        asc_house = 5
        ba = arudhas.bhava_arudhas(chart_1)
        expected_result = [2, 4, 5, 4, 0, 2, 1, 9, 9, 5, 1, 6]
        #Ans A1/AL:Ge, A2:Le, A3:Vi, A4:Le, A5:Ar, A6:Ge, A7:Ta, A8:Cp, A9:Cp, A10:Vi, A11: Ta, A12:Li
        houses = [(h + asc_house) % 12 for h in range(12)] 
        for i, h in enumerate(houses):
            test_example(chapter+exercise,house.rasi_names_en[expected_result[i]],house.rasi_names_en[ba[i]],'A' + str(i + 1))
    def bhava_arudha_tests_2():
        exercise = 'Exercise 12 / Chart 2 Bhava Arudha'
        asc_house = 8
        ba = arudhas.bhava_arudhas(chart_2)
        expected_result = [10,0,8,7,8,10,11,5,1,8,8,10]
        houses = [(h + asc_house) % 12 for h in range(12)] 
        for i, h in enumerate(houses):
            test_example(chapter+exercise,house.rasi_names_en[expected_result[i]],house.rasi_names_en[ba[i]],'A' + str(i + 1))
    def graha_arudha_tests_1():
        exercise = 'Example 29 / Chart 1 Graha Arudha'
        ba = arudhas.graha_arudhas(chart_1)
        expected_result = [9,4,9,2,10,1,3,5,5]
        for p in range(9):
            test_example(chapter+exercise,house.rasi_names_en[expected_result[p]],house.rasi_names_en[ba[p]],'contains',house.planet_list[p],"Graha Pada")
    def graha_arudha_tests_2():
        exercise = 'Exercise 13 / Chart 2 Graha Arudha'
        ba = arudhas.graha_arudhas(chart_2)
        expected_result = [7,8,2,11,7,10,8,5,11]
        for p in range(9):
            test_example(chapter+exercise,house.rasi_names_en[expected_result[p]],house.rasi_names_en[ba[p]],'contains',house.planet_list[p],"Graha Pada")
    bhava_arudha_tests_1()
    bhava_arudha_tests_2()
    graha_arudha_tests_1()
    graha_arudha_tests_2()
def drig_dhasa_tests():
    chapter = 'Chapter 21 / Drig Dhasa Tests '
    def drig_dhasa_test_1():
        exercise = 'Example 80 / Chart 36'
        chart_36 = ['','8','6','','5','2/0','3/L','7','','1','4','']
        dd = drig.drig_dhasa(chart_36,(1912,1,1))
        expected_result = [(2,4),(6,11),(8,2),(11,1),(3,6),(1,3),(10,8),(7,10),(4,11),(0,5),(9,7),(6,10)]
        # Ans: Ge, Vi, Sg, Pi, Cn, Ta, Aq, Sc, Le, Ar, Cp, Li.
        # Ans: 2,5,8,11,3,1,10,7,4,0,9,6
        for pe,p in enumerate(dd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
    def drig_dhasa_test_2():
        exercise = 'Example 82 / Chart 37'
        chart_37 = ['6','','','','8','','','4/2/5','3','0/1','7/L','']
        dd = drig.drig_dhasa(chart_37,(1971,26,1))
        expected_result = [(6,1),(10,9),(1,6),(4,7),(7,9),(9,8),(0,8),(3,6),(8,11),(11,4),(2,6),(5,9)]
        # Ans: Li, Aq, Ta, Le, Sc, Cp, Ar, Cn, Sg, Pi, Ge, Vi
        for pe,p in enumerate(dd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
        test_example(chapter+exercise,('1987','1994'),(dd[3][1].split('-')[0],dd[3][2].split('-')[0]),'Leo Dhasa Period')
    drig_dhasa_test_1()
    drig_dhasa_test_2()   
def nirayana_shoola_dhasa_tests():
    chapter = 'Chapter 22 / Nirayana Shoola Dhasa Tests '
    def nirayana_shoola_dhasa_test_1():
        exercise = 'Example 84 / Chart 8'
        chart_8 = ['','7','','6','','','4/3/5','0/L/8/2','','','1','']
        #print('nirayana shoola dhasa test\n',chart_8)
        #print('nirayana shoola dhasa\n',sd)
        #Ans: Sg (9), Cp(7), Aq(8), Pi(9), Ar(7), Ta(8), Ge(9) etc
        sd = nirayana.nirayana_shoola_dhasa(chart_8, (1946,12,2))
        expected_result = [(8,9),(9,7),(10,8),(11,9),(0,7),(1,8),(2,9)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    def nirayana_shoola_dhasa_test_2():
        exercise = 'Example 85 / Chart 39'
        chart_39 = ['','','6','7','0/1/3/4/5/L','2','','','','8','','']
        sd = nirayana.nirayana_shoola_dhasa(chart_39, (1944,8,20))
        expected_result = [(5,9),(4,8),(3,7),(2,9),(1,8),(0,7)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    nirayana_shoola_dhasa_test_1()
    nirayana_shoola_dhasa_test_2()
def sudharsana_chakra_dhasa_tests():
    chapter = 'Chapter 31.2 Sudarsana Chakra chart tests '
    def sudharsana_chakra_chart_test():
        exercise = 'Chart 72'
        chart_72 = ['','','7','5/0','3','2','','','8','6','1','4/L']
        print('chart_72',chart_72)
        chart_72_lagna = []
        dob = (1963,8,7)
        tob = (21,14,0)
        place = drig_panchanga.Place('unknown',21+27.0/60, 83+58.0/60, +5.5)
        years_from_dob = 0 # 17
        divisional_chart_factor = 1
        jd_at_dob = utils.julian_day_number(dob, tob)
        jd_at_years = jd_at_dob + years_from_dob * const.sidereal_year
        lsd,msd,ssd,_ = sudharsana_chakra.sudharshana_chakra_chart(jd_at_dob,place,dob,years_from_dob,divisional_chart_factor)
        lagna_chart = [(11, 'L/4'), (0, ''), (1, ''), (2, '7'), (3, '0/5'), (4, '3'), (5, '2'), (6, ''), (7, ''), (8, '8'), (9, '6'), (10, '1')] 
        moon_chart =  [(10, '1'), (11, 'L/4'), (0, ''), (1, ''), (2, '7'), (3, '0/5'), (4, '3'), (5, '2'), (6, ''), (7, ''), (8, '8'), (9, '6')] 
        sun_chart =  [(3, '0/5'), (4, '3'), (5, '2'), (6, ''), (7, ''), (8, '8'), (9, '6'), (10, '1'), (11, 'L/4'), (0, ''), (1, ''), (2, '7')]
        test_example(chapter+exercise,lagna_chart,lsd,'Lagna Chart')
        test_example(chapter+exercise,moon_chart,msd,'Moon Chart')
        test_example(chapter+exercise,sun_chart,ssd,'Sun Chart')
    def sudharsana_chakra_dhasa_test():
        exercise='Example 126 / Chart 69 '
        chart_69_D24 = ['6','L','4','5','','8/7','','1/0/2','','','','3']
        chart_69_rasi = {'L':'13Cp25','0':'20Pi52','1':'4Ge55','2':'5Ta46','3':'24Aq46','4':'14Pi17','5':'14Aq55','6':'27Sc27','7':'17Pi50','8':'17Vi50'}
        chart_69_rasi = ['','2','1','','','8','','6','','L','3/5','0/4/7']
        chart_72 = ['','','7','5/0','3','2','','','8','6','1','4/L']
        print('chart_72',chart_72)
        dob = (1970,10,28)
        tob = (17,50,0)
        time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
        place = drig_panchanga.Place('unknown',16+15.0/60, 81+12.0/60, +5.5)
        years_from_dob = 0 # 17
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
    sudharsana_chakra_chart_test()
def narayana_dhasa_tests():
    # Chart 24 - Bill Gates
    #"""
    dob = (1955,10,28)
    tob = (21,18,0)
    place = drig_panchanga.Place('unknown',47+36.0/60, -122.33, -8.0)
    divisional_chart_factor = 1
    #"""
    """
    # Chart 25 - India's indepdendence
    dob = (1947,8,15)
    tob = (0,0,0)
    place = drig_panchanga.Place('unknown',27.0, 78.5, +5.5)
    divisional_chart_factor = 1
    """
    """
    # Chart 27
    dob = (1972,6,1)
    tob = (4,16,0)
    years = 0
    place = drig_panchanga.Place('unknown',16+15.0/60, 81+12.0/60, +5.5)
    divisional_chart_factor = 4
    #Ans : 7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], 
    #[8, '1996-6-1', '2000-6-1', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 4]
    #[9, '2000-6-1', '2002-6-1', [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10], 2]
    #[10, '2002-6-1', '2005-6-1', [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 3]
    #[11, '2005-6-1', '2016-6-1', [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], 11]
    """
    h_to_p = ['','6/1','','0','3/2/5','8','','4','','','L','7']
    #nd = narayana.narayana_dhasa_for_divisional_chart(dob,tob,place,divisional_chart_factor)
    nd = narayana.narayana_dhasa_for_rasi_chart(h_to_p, dob)
    expected_result= [(4,1),(9,8),(2,2),(7,9),(0,4),(5,1),(10,9),(3,3),(8,11),(1,3),(6,10),(11,4),(4,11),(9,4),(2,10),(7,3),(0,8),(5,11),(10,3),(3,9)]
    for pe,p in enumerate(nd):
        test_example('narayana dhasa tests',expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
def shoola_dhasa_tests():  
    chapter = 'Chapter 23 / Shoola Dhasa Tests '
    def shoola_dhasa_test_1():
        exercise = 'Example 89 / Chart 8'
        chart_8 = ['','7','','6','','','4/3/5','0/L/8/2','','','1','']
        # Ans Sc, Sg, Cp, Aq etc each 9 years
        sd = shoola.shoola_dhasa(chart_8, (1946,12,2))
        expected_result = [(7,9),(8,9),(9,9),(10,9),(11,9),(0,9)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    def shoola_dhasa_test_2():
        exercise = 'Example 90 / Chart 39'
        chart_39 = ['','','6','7','0/1/3/4/5/L','2','','','','8','','']
        sd = shoola.shoola_dhasa(chart_39, (1944,8,20))
        expected_result = [(4,9),(5,9),(6,9),(7,9),(8,9),(9,9)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    def shoola_dhasa_test_3():
        """ TODO: Stronger Rasi fails - needs Rule 6 to be implemented"""
        exercise = 'Example 91 / Chart 61'
        chart_61 = ['','4','8','6/L','2','','','3/0','7/5','1','','']
        sd = shoola.shoola_dhasa(chart_61, (1917,11,19))
        expected_result = [(9,9),(10,9),(11,9),(0,9),(1,9),(2,9)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    def shoola_dhasa_test_4():
        exercise = 'Example 92 / Chart 40'
        chart_40 = ['2/L','','7','','1','','','6','8','3/0/5','4','']
        sd = shoola.shoola_dhasa(chart_40, (1927,1,20))
        expected_result = [(0,9),(1,9),(2,9),(3,9),(4,9),(5,9)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    def shoola_dhasa_test_5():
        exercise = 'Exercise 33 / Chart 45'
        chart_45 = ['','','','','6','8/2','','','3/L','4/0/4','','8/1']
        sd = shoola.shoola_dhasa(chart_45, (1950,1,1))
        expected_result = [(8,9),(9,9),(10,9),(11,9),(0,9),(1,9)]
        for pe,p in enumerate(sd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    shoola_dhasa_test_1()
    shoola_dhasa_test_2()
    #shoola_dhasa_test_3() """ TODO: Stronger Rasi fails - needs Rule 6 to be implemented"""
    shoola_dhasa_test_4()
    shoola_dhasa_test_5()
def kalachakra_dhasa_tests():
    chapter = 'Chapter 24 Kalachakra Dhasa Tests '
    exercise = 'Example 95 / Moon 15Ta50 '
    # Example_95
    lunar_longitude = 45+50/60.0 # 15 Ta 50'
    dob = (1912,1,1)
    kd = kalachakra.kalachakra_dhasa(lunar_longitude,dob)
    #Ans:Sc(4.75),Li(16),Vi, Le, Cn, Ge, Ta, Ar, Sg [9, 5, 21, 9, 16, 7, 10]
    expected_result = [(7,4.75),(6,16),(5,9),(4,5),(3,21),(2,9),(1,16),(0,7),(8,10)]
    for pe, p in enumerate(kd):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')
    #print('kalachakra dhasa test\n',kd)
    exercise = 'Example 95 / Moon 3Cn00 '
    lunar_longitude = 93.0
    #Ans Pi(8.6) Sc, Li, Vi, Cn, Le, Ge, Ta, Ar [ 7, 16, 9, 21, 5, 9, 16, 7]
    #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
    kd = kalachakra.kalachakra_dhasa(lunar_longitude,dob)
    expected_result = [(11,8.6),(7,7),(6,16),(5,9),(3,21),(4,5),(2,9),(1,16),(0,7)]
    for pe, p in enumerate(kd):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')

    exercise = 'Exercise 34 / Moon 5Aq50 '
    lunar_longitude = 10*30+5+50./60.
    # Ans: Ge(2), Ta(16), Ar(7), Sg(10), Cp(4), Aq(4), Pi(10), Ar(7), Ta(16), Ge(9).
    #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
    kd = kalachakra.kalachakra_dhasa(lunar_longitude,dob)
    expected_result = [(2,2),(1,16),(0,7),(8,10),(9,4),(10,4),(11,10),(0,7),(1,16),(2,9)]
    for pe, p in enumerate(kd):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years','Diff due to error in house.stronger_rasi')
def utils_tests():
    # should return location based on IP addressm, todays date and time dvf=1
    result = utils._validate_data(place=None,latitude=None,longitude=None,time_zone_offset=None,dob=None,tob=None,division_chart_factor=None)
    print(result)
    result = utils._validate_data(place='Karamadai',latitude=None,longitude=None,time_zone_offset=None,dob=None,tob=None,division_chart_factor=4)
    print(result)
    #And: Karamadai  11.2428 76.9587 5.5 Date(year=2022, month=3, day=31) ('12', '55', '45.425760') 4
def chart_tests():    
    dob = drig_panchanga.Date(1967,3,8)
    tob = (17,40,0)
    lat=73+4/60.0
    long=26+18.0/60
    tz = 5.5
    place = drig_panchanga.Place('unknown',lat,long,tz)
    print(place)
    jd = utils.julian_day_number(dob,tob)
    print(jd)
    cht = charts.divisional_chart(jd_at_dob=jd, place_as_tuple=place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=1)
    print(cht)
def vimsottari_adhipati_tests():
    # nakshatra indexes counted from 0
    satabhisha, citta, aslesha = 23, 13, 8
    test_example('Chapter 16 Vimsottari Adhipathi Tests:', 7, vimsottari.vimsottari_adhipati(satabhisha))
    test_example('Chapter 16 Vimsottari Adhipathi Tests:', 18, const.vimsottari_dict[vimsottari.vimsottari_adhipati(satabhisha)])
    test_example('Chapter 16 Vimsottari Adhipathi Tests:', 2, vimsottari.vimsottari_adhipati(citta))
    test_example('Chapter 16 Vimsottari Adhipathi Tests:', 7, const.vimsottari_dict[vimsottari.vimsottari_adhipati(citta)])
    test_example('Chapter 16 Vimsottari Adhipathi Tests:', 3, vimsottari.vimsottari_adhipati(aslesha))
    test_example('Chapter 16 Vimsottari Adhipathi Tests:', 17, const.vimsottari_dict[vimsottari.vimsottari_adhipati(aslesha)])
def _raasi_Ashtaka(planet,chart):
    chapter = 'Chaper 12.3 ashtaka_varga_tests Exercise 18/Chart 6:'
    chart_6 = chart # ['8/5','','2/0/3','','6/4','L','7','','','','','1']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_6)
    raasi_ashtaka = []
    r_a_e = [['Aries', 'Taurus', 'Libra', 'Scorpio', 'Aquarius'],
             ['Aries', 'Gemini', 'Leo', 'Libra', 'Sagittarius', 'Capricorn'],
             ['Aries', 'Gemini', 'Cancer', 'Virgo', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
             ['Aries', 'Taurus', 'Gemini', 'Leo', 'Libra', 'Scorpio', 'Aquarius', 'Pisces'],
             ['Gemini', 'Cancer', 'Capricorn', 'Pisces'],
             ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Scorpio', 'Sagittarius', 'Aquarius'],
             ['Aries', 'Taurus', 'Gemini', 'Leo', 'Virgo', 'Scorpio', 'Aquarius', 'Pisces'],
             ['Aries', 'Gemini', 'Cancer', 'Virgo', 'Libra', 'Sagittarius', 'Aquarius']
            ]  
    key = str(planet)
    for p in range(8):
        pr = p_to_h[p]
        p_name = house.planet_list[p]
        if p==7:
            pr = p_to_h['L']
            p_name = 'Lagnam'
        avr = const.ashtaka_varga_dict[key][p]
        avr = sorted([(r+pr-1)%12 for r in avr])
        avr = [house.rasi_names_en[r] for r in avr]
        test_example(chapter+p_name,r_a_e[p],avr,'Benefic to',house.planet_list[planet])
        #test_example(chapter,'',[house.rasi_names_en[(pr+r-1)%12] for r in planet_raasi_list[p]])
def ashtaka_varga_tests():
    chapter = 'Chaper 12.3 ashtaka_varga_tests'
    # Exercise 18, 19 and 20
    chart_7 = ['6/1/7','','','','','','8/4','L','3/2','0','5','']
    chart_6 = ['8/5','','2/0/3','','6/4','L','7','','','','','1']
    chart_11 = ['5/8/L', '', '0/2/3', '', '4/6', '', '7', '', '', '', '', '1']
    chart_12 = ['8','5','','','','L','7','2/4','0/3','1','','6']
            
    _raasi_Ashtaka(3,chart_6)
    bav_e = [[5, 3, 5, 3, 4, 4, 2, 3, 5, 4, 5, 5], 
             [3, 2, 5, 3, 6, 3, 4, 5, 5, 5, 3, 5], 
             [4, 3, 4, 3, 4, 3, 2, 5, 1, 3, 3, 4], 
             [7, 4, 7, 4, 4, 3, 4, 4, 4, 3, 6, 4], 
             [4, 3, 5, 6, 3, 7, 4, 3, 5, 6, 5, 5], 
             [8, 7, 4, 3, 3, 2, 4, 6, 4, 4, 4, 3], 
             [3, 3, 4, 3, 2, 3, 2, 3, 4, 5, 3, 4], 
             [5, 5, 6, 3, 6, 3, 1, 7, 3, 4, 3, 3]]
    sav_e = [34, 25, 34, 25, 26, 25, 22, 29, 28, 30, 29, 30]
    pav_e = [[[1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1], [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0], [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1], [1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1], [1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1], [1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1], [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [5, 3, 5, 3, 4, 4, 2, 3, 5, 4, 5, 5]], [[1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1], [0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1], [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1], [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1], [0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1], [0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0], [0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [3, 2, 5, 3, 6, 3, 4, 5, 5, 5, 3, 5]], [[1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1], [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0], [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1], [1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1], [0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [4, 3, 4, 3, 4, 3, 2, 5, 1, 3, 3, 4]], [[1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0], [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0], [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1], [1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1], [0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1], [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0], [1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1], [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [7, 4, 7, 4, 4, 3, 4, 4, 4, 3, 6, 4]], [[1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1], [1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0], [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1], [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1], [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1], [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0], [0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0], [0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [4, 3, 5, 6, 3, 7, 4, 3, 5, 6, 5, 5]], [[1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], [1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1], [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0], [1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0], [1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1], [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0], [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1], [1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [8, 7, 4, 3, 3, 2, 4, 6, 4, 4, 4, 3]], [[1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1], [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0], [1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1], [1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1], [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1], [0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [3, 3, 4, 3, 2, 3, 2, 3, 4, 5, 3, 4]], [[1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1], [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1], [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0], [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0], [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [5, 5, 6, 3, 6, 3, 1, 7, 3, 4, 3, 3]]]
    sp_e = ([108, 132, 90, 77, 119, 128, 69], [71, 91, 107, 75, 35, 35, 48], [179, 223, 197, 152, 154, 163, 117])
    bav, sav, pav = ashtakavarga.get_ashtaka_varga(chart_6)
    exercise = 'Exercise 19/Chart 6:'
    test_example(chapter+exercise+' binna ashtaka varga',bav_e,bav,assert_result=True)
    exercise = 'Exercise 20/Chart 6:'
    test_example(chapter+exercise+' samudhaya ashtaka varga',sav_e,sav)
    exercise = 'Exercise 19/20/Chart 6:'
    test_example(chapter+exercise+' prastara ashtaka varga',pav_e,pav,assert_result=True)
    exercise = 'Example 40/Chart 11:'
    bav = [[7,4,7,4,4,3,4,4,4,3,6,4] for p in range(8)]
    bav = ashtakavarga._trikona_sodhana(bav)
    bav_e = [[3,1,3,0,0,0,0,0,0,0,2,0] for p in range(8)]
    test_example(chapter+exercise+' BAV',bav_e[0],bav[0])
    rp,gp,sp = ashtakavarga.sodhaya_pindas(bav,chart_11)
    rp_e,gp_e,sp_e = [77  for p in range(8)],[75  for p in range(8)],[152  for p in range(8)]
    test_example(chapter+exercise+' Rasi Pinda',rp_e[0],rp[0])
    exercise = 'Example 41/Chart 11:'
    test_example(chapter+exercise+' Graha Pinda',gp_e[0],gp[0])
    exercise = 'Example 42/Chart 11:'
    test_example(chapter+exercise+' Sodhaya Pinda',sp_e[0],sp[0])
    exercise = 'Exercise 21/Chart 12:'
    bav, sav, pav = ashtakavarga.get_ashtaka_varga(chart_12)
    sav_e = [24,25,31,28,27,39,33,29,26,22,28,25]
    test_example(chapter+exercise+' samudhaya ashtaka varga',sav_e,sav)
    exercise = 'Exercise 22/Chart 7:'
    bav, sav,pav = ashtakavarga.get_ashtaka_varga(chart_7)
    bav_e = [[4,2,3,4,6,5,5,3,2,6,6,2],
             [6,3,5,3,5,5,6,3,3,4,4,2],
             [3,2,3,4,2,5,4,3,3,4,3,3],
             [4,6,4,3,4,7,4,5,6,3,5,3],
             [4,4,3,5,6,5,6,4,6,4,3,6],
             [3,5,5,4,6,2,3,6,5,2,7,4],
             [3,2,2,3,5,6,3,4,1,3,6,1]]
    test_example(chapter+exercise+' BAV',bav_e,bav[:-1],assert_result=True)
    sav_e = [27,24,25,26,34,35,31,28,26,26,34,21]
    test_example(chapter+exercise+' SAV',sav_e,sav,assert_result=True)
    sp_e = [[152,85,52,95,68,154,162],[81,55,43,33,56,54,63],[233,140,95,128,124,208,225]]
    sp = ashtakavarga.sodhaya_pindas(bav, chart_7)
    test_example(chapter+exercise+' Sodhaya Pindas',sp_e,sp)
    print(chapter+exercise+' Sodhaya Pindas:\n NOTE: Not clear why this case SP failed to match the book\n'+
          ' Examples 40,41 & 42 based on Chart 12 are matching BAV, SAV and SP.\n So the calculations in this code is thus verified')
def patyayini_tests():
    chapter = 'Chapter 30 '
    exercise = 'Example 122 / Chart 67 '
    expected_result = [(5, 24.98), (3, 48.17), (1, 0.51), (6, 25.74), ('L', 11.24), (4, 57.35), (0, 93.29), (2, 103.99)]
    # Note: Difference in ans is due to use of sidereal year instead of book's approx method to calculate jf_at_years 
    jd_at_dob = utils.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = drig_panchanga.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    jd_at_years = utils.julian_day_number((1993,6,1),(13,30,4))
    cht=patyayini.patyayini_dhasa(jd_at_years, place, ayanamsa_mode, divisional_chart_factor)
    for i,pp in enumerate(cht):
        test_example(chapter+exercise,expected_result[i],(pp[0],round(pp[-1],2)),'Difference due to sideral year value used')
def varsha_narayana_tests():
    chapter = 'Chapter 30.4 '
    def varsha_narayana_test_1():
        exercise = 'Example in 30.4 '
        dob = (1972,6,1)
        tob = (4,16,0)
        jd_at_dob = utils.julian_day_number(dob,tob)
        years = 21
        place = drig_panchanga.Place('unknown',16+15.0/60,81+12.0/60,5.5)
        divisional_chart_factor = 9
        vd = narayana.varsha_narayana_dhasa_bhukthi(dob,tob,place,years,divisional_chart_factor=divisional_chart_factor)
        expected_result = [(7,21),(8,12),(9,6),(10,9),(11,33)]
        for i,[p,_,_,d] in enumerate(vd[:len(expected_result)]):
            test_example(chapter+exercise,expected_result[i],(p,d),'days')
    varsha_narayana_test_1()
def mudda_tests():
    chapter = 'Chapter 30.3 Mudda Tests '
    exercise = 'Example 122 / Chart_67'
    """ SET AYANAMSA MODE FIRST """
    drig_panchanga.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
    # Chart_67 
    jd_at_dob = utils.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = drig_panchanga.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    chart_67_pp = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode, divisional_chart_factor=1)
    #print(chart_67_pp)
    db=mudda.varsha_vimsottari_dhasa_bhukthi(jd_at_dob, place,years)
    # Ans - [(7, 7, '1993-06-03', 8.22), (7, 4, '1993-06-11', 7.31) ....
    expected_result = [(7,54),(4,48),]
    i = 0
    ppsum = round(sum(db[j][-1] for j in range(i,i+9)),1)
    test_example(chapter+exercise,expected_result[0],(db[i][0],ppsum))
    i += 9
    ppsum = round(sum(db[j][-1] for j in range(i,i+9)),1)
    test_example(chapter+exercise,expected_result[1],(db[i][0],ppsum))
    #print('varsha_vimsottari_tests',db)
def saham_tests():
    chapter = 'Chaper 28.2 - Saham Tests '
    exercise = 'Example 121 / Chart 66 '
    dob = (2000,3,8)
    tob = (4,41,0)
    divisional_chart_factor = 1
    tob_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
    jd_at_dob = utils.julian_day_number(dob, tob)
    place_as_tuple = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    sunrise = utils.from_dms_str_to_dms(drig_panchanga.sunrise(jd_at_dob, place_as_tuple)[1])
    #print('saham_tests',utils.from_dms_str_to_dms(sunrise))
    sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
    sunset = utils.from_dms_str_to_dms(drig_panchanga.sunset(jd_at_dob, place_as_tuple)[1])
    sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
    night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
    #print(tob_hrs,'night_time_birth',night_time_birth,'sunrise',sunrise_hrs,'sunset',sunset_hrs)
    chart_66 = charts.divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    for p,(h,long) in chart_66:
        if p=='L':
            planet = 'Lagnam'
        else:
            planet = house.planet_list[p]
        print(planet,rasi_names_en[h],utils.to_dms(long,is_lat_long='plong'))
    h_to_p = utils.get_house_planet_list_from_planet_positions(chart_66)
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
    asl = saham.artha_saham(chart_66,night_time_birth=night_time_birth)
    expected_result = (7,2.5)
    test_example(chapter+exercise+'artha_saham_longitude',expected_result,drig_panchanga.dasavarga_from_long(asl,divisional_chart_factor))
    ssl = saham.samartha_saham(chart_66,night_time_birth=night_time_birth)
    expected_result = (11,5)
    test_example(chapter+exercise+'smartha_saham_longitude',expected_result,drig_panchanga.dasavarga_from_long(ssl,divisional_chart_factor))
    psl = saham.punya_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'punya_saham_longitude',drig_panchanga.dasavarga_from_long(psl,divisional_chart_factor))
    psl = saham.vidya_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'vidya_saham_longitude',drig_panchanga.dasavarga_from_long(psl,divisional_chart_factor))
    ysl = saham.yasas_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'yasas_saham_longitude',drig_panchanga.dasavarga_from_long(ysl,divisional_chart_factor))
    msl = saham.mitra_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'mitra_saham_longitude',drig_panchanga.dasavarga_from_long(msl,divisional_chart_factor))
    msl = saham.mahatmaya_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'mahatmaya_saham_longitude',drig_panchanga.dasavarga_from_long(msl,divisional_chart_factor))
    asl = saham.asha_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'asha_saham_longitude',drig_panchanga.dasavarga_from_long(asl,divisional_chart_factor))
    bsl = saham.bhratri_saham(chart_66)
    print(chapter+exercise+'bhratri_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    gsl = saham.gaurava_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'gaurava_saham_longitude',drig_panchanga.dasavarga_from_long(gsl,divisional_chart_factor))
    bsl = saham.pithri_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'pithri_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.rajya_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'rajya_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.maathri_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'maathri_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.puthra_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'puthra_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.jeeva_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'jeeva_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.karma_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'karma_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.roga_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'roga_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.roga_sagam_1(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'roga_saham_1_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.kali_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'kali_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.sastra_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'sastra_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.bandhu_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'bandhu_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.mrithyu_saham(chart_66)
    print(chapter+exercise+'mrithyu_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.paradesa_saham(chart_66, night_time_birth)
    print(chapter+exercise+'paradesa_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.paradara_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'paradara_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.vanika_saham(chart_66,night_time_birth=night_time_birth)
    expected_result = (8,7+4/60.)
    test_example(chapter+exercise+'vanika_saham_longitude',expected_result,drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.karyasiddhi_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'karyasiddhi_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.vivaha_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'vivaha_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.santapa_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'santapa_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.sraddha_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'sraddha_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.preethi_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'preethi_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.jadya_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'jadya_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.vyaapaara_saham(chart_66)
    print(chapter+exercise+'vyaapaara_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.sathru_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'sathru_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.jalapatna_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'jalapatna_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    bsl = saham.bandhana_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'bandhana_saham_longitude',drig_panchanga.dasavarga_from_long(bsl,divisional_chart_factor))
    asl = saham.apamrithyu_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'apamrithyu_saham_longitude',drig_panchanga.dasavarga_from_long(asl,divisional_chart_factor))
    lsl = saham.laabha_saham(chart_66,night_time_birth=night_time_birth)
    print(chapter+exercise+'laabha_saham_longitude',drig_panchanga.dasavarga_from_long(lsl,divisional_chart_factor))
    def _vivaha_saham_calculation(dob,tob,exercise,expected_result):
        tob_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
        jd_at_dob = utils.julian_day_number(dob, tob)
        place_as_tuple = drig_panchanga.Place('unknown',16+5.0/60,81+12.0/60,5.5)
        sunrise = utils.from_dms_str_to_dms(drig_panchanga.sunrise(jd_at_dob, place_as_tuple)[1])
        sunrise_hrs = sunrise[0]+sunrise[1]/60.0+sunrise[2]/3600.0
        sunset = utils.from_dms_str_to_dms(drig_panchanga.sunset(jd_at_dob, place_as_tuple)[1])
        sunset_hrs = sunset[0]+sunset[1]/60.0+sunset[2]/3600.0
        night_time_birth = tob_hrs > sunset_hrs or tob_hrs < sunrise_hrs
        #print(tob_hrs,'night_time_birth',night_time_birth,'sunrise',sunrise_hrs,'sunset',sunset_hrs)
        chart = charts.divisional_chart(jd_at_dob, place_as_tuple, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=1)
        #print(chart)
        h_to_p = utils.get_house_planet_list_from_planet_positions(chart)
        #print(h_to_p)
        p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
        #print(p_to_h)
        vsl = saham.vivaha_saham(chart,night_time_birth=night_time_birth)
        test_example(chapter+exercise+'vivaha_saham_longitude',expected_result,drig_panchanga.dasavarga_from_long(vsl,1))
    def vivaha_saham_test_1():
        exercise = 'Chart 96 Vivaha Saham '
        dob = (1991,5,22)
        tob = (20,29,0)
        place_as_tuple = drig_panchanga.Place('unknown',18+40.0/60,78+10.0/60,5.5)
        expected_result = (2,22+54./60.)
        _vivaha_saham_calculation(dob,tob,exercise,expected_result)
    def vivaha_saham_test_2():
        exercise = 'Chart 67 Vivaha Saham '
        dob = (1993,6,1)
        tob = (13,30,0)
        expected_result = (8,2+22/60.)
        _vivaha_saham_calculation(dob,tob,exercise,expected_result)
    vivaha_saham_test_1()
    vivaha_saham_test_2()
def harsha_bala_tests():
    chapter = 'Chapter 28.3 Harsha Bala tests'
    exercise = 'Example 119 / Chart 66'
    chart_66 = ['6/4','','','7','','','','','','5/L/8','3/0','2/1']
    expected_result = {0: 0, 1: 15, 2: 0, 3: 10, 4: 5, 5: 10, 6: 5}
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    hb = tajaka.harsha_bala(p_to_h, new_year_daytime_start=False)
    test_example(chapter+exercise,expected_result,hb)
def pancha_vargeeya_bala_tests():
    chapter = 'Chapter 28.4 Pancha Vargeeya Bala Tests'
    def _kshetra_bala_test():
        # Planet in own rasi should have 30 pts
        p = 0
        r  = 0
        exp = 30
        exercise ='KShetra Bala '+str(p)+'/'+str(r)+' = 30 pts'
        p_to_h_of_rasi_chart = {p:r,1:2,2:3,3:4,4:5,5:6,6:7,7:8,8:9,'L':10}
        kb = tajaka._kshetra_bala(p_to_h_of_rasi_chart)
        test_example(chapter+exercise,exp,kb[p])
        # planet in friend rasi = 15 pts
        p = 1
        r  = 2
        exp = 15
        exercise ='KShetra Bala '+str(p)+'/'+str(r)+' = 15 pts'
        p_to_h_of_rasi_chart = {p:r,0:3,2:3,3:4,4:5,5:6,6:7,7:8,8:9,'L':10}
        kb = tajaka._kshetra_bala(p_to_h_of_rasi_chart)
        test_example(chapter+exercise,exp,kb[p])
        # planet in enemy rasi = 7.5 pts
        p = 2
        r  = 5
        exp = 7.5
        exercise ='KShetra Bala '+str(p)+'/'+str(r)+' = 7.5 pts'
        p_to_h_of_rasi_chart = {p:r,0:1,1:2,3:4,4:1,5:6,6:7,7:8,8:9,'L':10}
        kb = tajaka._kshetra_bala(p_to_h_of_rasi_chart)
        test_example(chapter+exercise,exp,kb[p])
    _kshetra_bala_test()
    def uchcha_bala_test():
        exercise = 'Uchcha Bala Test - Jupiter is at 8Vi30'
        pp = [['L',(0,0)],[0,(0,0)],[1,(0,0)],[2,(0,0)],[3,(0,0)],[4,(5,8+30/60)],[5,(0,0)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
        const.use_BPHS_formula_for_uccha_bala = False # To Book Value True> Sravali
        ub = tajaka._uchcha_bala(pp)
        test_example(chapter+exercise,12.94,ub[4])
    uchcha_bala_test()
    chart_66 = ['6/4','','','7','','','','','','5/L/8','3/0','2/1']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    chart_66 = ['6/2','','','7','','','','','','5/L/8','3/0','4/1']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_66)
    #Ans: {0: 7.5, 1: 15, 2: 30, 3: 15, 4: 30, 5: 22.5, 6: 0}
    print('_kshetra_bala test',tajaka._kshetra_bala(p_to_h))
    jd_at_dob = utils.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    jd_at_years = jd_at_dob + years * const.sidereal_year
    print(' Varsha Pravesha time after',years,'years',swe.revjul(jd_at_years)) # 4.41 AM 2000,3,8
    place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    print(tajaka.pancha_vargeeya_bala(jd_at_years,place))
def chapter_27_tests():
    chapter = 'Chapter 27 Annual Charts '
    def annual_chart_test():
        exercise = 'Example 118 '
        jd_at_dob = utils.julian_day_number((1967,3,8),(17,40,0))
        place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
        natal_chart = charts.rasi_chart(jd_at_dob, place)
        natal_solar_long = utils.to_dms(natal_chart[1][1][1],is_lat_long='plong')
        #print(natal_chart)
        years = 34
        cht,jd_ymd = tajaka.annual_chart(jd_at_dob, place, divisional_chart_factor=1, years=years)
        #cht = charts.divisional_chart(jd_at_years,place)
        expected_result = natal_solar_long + '([(2000, 3, 8), "04:41:21 AM"])' # '23° 50’ 29" ([(2000, 3, 8), "04:41:21 AM"])'
        test_example(chapter+exercise+'Varsha Pravesha Solar Longitude Test',expected_result,
                     utils.to_dms(cht[1][1][1],is_lat_long='plong'),jd_ymd)
        months = 2
        cht,jd_ymd = tajaka.monthly_chart(jd_at_dob, place, divisional_chart_factor=1, years=years, months=months)
        expected_result = natal_solar_long + '([(2000, 4, 7), "10:38:06 AM"])' #'23° 50’ 29" ([(2000, 4, 7), "10:38:06 AM"])'
        test_example(chapter+exercise+'Maasa Pravesha Solar Longitude Test',expected_result,
                     utils.to_dms(cht[1][1][1],is_lat_long='plong'),jd_ymd)
        sixty_hours = 2
        cht,jd_ymd = tajaka.sixty_hour_chart(jd_at_dob, place, divisional_chart_factor=1, years=years, months=months,sixty_hour_count=sixty_hours)
        expected_result = '26° 20’ 25" ([(2000, 4, 9), "23:40:51 PM"])'
        test_example(chapter+exercise+'Sashti hora (60hr) Pravesha Solar Longitude Test',expected_result,
                     utils.to_dms(cht[1][1][1],is_lat_long='plong'),jd_ymd)

        exercise = 'Exercise 47 '
        dob = (1967,3,8)
        tob = (17,40,0)
        jd_at_dob = utils.julian_day_number(dob,tob)
        place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
        natal_chart = charts.rasi_chart(jd_at_dob, place)
        #print(natal_chart)
        years = 27
        cht,jd_ymd = tajaka.annual_chart(jd_at_dob, place, divisional_chart_factor=1, years=years)
        #cht = charts.divisional_chart(jd_at_years,place)
        expected_result = natal_solar_long + ' ([(1993, 3, 8), "09:36:18 AM"])' ##'23° 50’ 29" ([(1993, 3, 8), "09:36:18 AM"])'
        test_example(chapter+exercise+'Varsha Pravesha Solar Longitude Test',expected_result,
                     utils.to_dms(cht[1][1][1],is_lat_long='plong'),jd_ymd)
        cht,jd_ymd = tajaka.annual_chart_approximate(dob,tob, place, divisional_chart_factor=1, years=years)
        #cht = charts.divisional_chart(jd_at_years,place)
        expected_result = natal_solar_long + ' ([(1993, 3, 8), "09:36:18 AM"])' #'23° 50’ 29" ([(1993, 3, 8), "09:36:18 AM"])'
        test_example(chapter+exercise+'Varsha Pravesha (Approximate+Correction Per book) Solar Longitude Test',expected_result,
                     utils.to_dms(cht[1][1][1],is_lat_long='plong'),jd_ymd)
    annual_chart_test()    
def dwadhasa_vargeeya_bala_tests():    
    jd_at_dob = utils.julian_day_number((1996,12,7),(10,34,0))
    years = 26
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    dvp,dvpp = tajaka.dwadhasa_vargeeya_bala(jd_at_years,place)
    print('dwadhasa_vargeeya_bala',dvp,dvpp)
def lord_of_the_year_test():
    chapter = 'Chapter 28.6 Lord of Year Test '
    exercise = 'Example 120 / Chart 66 '
    jd_at_dob = utils.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    ld = tajaka.lord_of_the_year(jd_at_dob, place,years_from_dob=years)#,night_time_birth=True)
    test_example(chapter+exercise,'Mars',house.planet_list[ld])    
def lord_of_the_month_test():
    chapter = 'Chapter 28.6 Lord of Month Test '
    exercise = 'Example 120 / Chart 66 '
    jd_at_dob = utils.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    months = 6
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    ld = tajaka.lord_of_the_month(jd_at_dob, place,years_from_dob=years,months_from_dob=months)#,night_time_birth=True)
    test_example(chapter+exercise,'Jupiter',house.planet_list[ld])    
def _ishkavala_yoga_test():
    chapter = 'Chapter 29.2.1 Ishkavala Yoga '
    def _ishkavala_yoga_test_1():
        exercise = 'False Test'
        chart = ['0','','3','7','','4','8','','6','5/L','','2/1']
        p_to_h = utils.get_planet_to_house_dict_from_chart(chart)
        test_example(chapter+exercise,'False',tajaka_yoga.ishkavala_yoga(p_to_h))
    def _ishkavala_yoga_test_2():
        exercise = 'True Test'
        chart = ['3','4','','5','7','','8','6/2','','L/0','1','']
        p_to_h = utils.get_planet_to_house_dict_from_chart(chart)
        test_example(chapter+exercise,'True',tajaka_yoga.ishkavala_yoga(p_to_h))
    _ishkavala_yoga_test_1()
    _ishkavala_yoga_test_2()
def _induvara_yoga_test():
    chapter = 'Chapter 29.2.2 Induvara Yoga '
    def _induvara_yoga_test_1():
        exercise = 'False Test'
        chart = ['0','','3','7','','4','8','','6','5/L','','2/1']
        p_to_h = utils.get_planet_to_house_dict_from_chart(chart)
        test_example(chapter+exercise,'False',tajaka_yoga.induvara_yoga(p_to_h))
    def _induvara_yoga_test_2():
        exercise = 'True Test'
        chart = ['','','2/3','','','4/5','','','6/7/8','L','','0/1']
        p_to_h = utils.get_planet_to_house_dict_from_chart(chart)
        test_example(chapter+exercise,'True',tajaka_yoga.induvara_yoga(p_to_h))
    _induvara_yoga_test_1()
    _induvara_yoga_test_2()
def tajaka_yoga_tests():
    _ishkavala_yoga_test()
    _induvara_yoga_test()
def retrograde_combustion_tests():
    jd_at_dob = utils.julian_day_number((1967,3,8),(17,40,0))
    years = 33
    jd_at_years = jd_at_dob + years * const.sidereal_year
    place = drig_panchanga.Place('unknown',26+18.0/60,73+4.0/60,5.5)
    cht = charts.divisional_chart(jd_at_dob,place)
    print(cht)
    print('retrograde planets',charts.planets_in_retrograde(cht))
    print('combustion planets',charts.planets_in_combustion(cht))
    print('retrograde planets',charts.planets_in_retrograde(cht))
    print('combustion planets',charts.planets_in_combustion(cht))
def _tajaka_aspect_test(chart, planet1, planet2):
    ta1 = tajaka.planets_have_aspects(chart, planet1, planet2)
    print('tajaka.planets_have_aspects',ta1)
    ta2 = tajaka.planets_have_aspects(chart, planet2, planet1)
    print('tajaka.planets_have_aspects',ta2)
def _deeptamsa_test(planet_positions,planet1,planet2):
    da = tajaka.both_planets_within_their_deeptamsa(planet_positions,planet1,planet2)
    print('deeptamsa_test',(planet1,planet2),da)
def ithasala_yoga_tests():
    chapter = 'Chapter 29.2.3 ithasala_yoga_tests'
    def ithasala_yoga_1_test():
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        pp = [['L',(0,0)],[0,(0,0)],[1,(4,14)],[2,(0,0)],[3,(0,0)],[4,(0,0)],[5,(4,19)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
        planet1 = 1
        planet2 = 5
        ty = tajaka_yoga.ithasala_yoga(pp,planet1,planet2)
        expected_result = (True,'Vartamaana (1)')
        dp = tajaka.both_planets_within_their_deeptamsa(pp, planet1, planet2)
        test_example(chapter+' planets within deeptamsa ',(True,1),dp)
        test_example(chapter,expected_result,ty)
    ithasala_yoga_1_test()
def eesarpa_yoga_tests():
    chapter = 'Chapter 29.2.4 eesarpa_yoga_tests'
    def eesarpa_yoga_1_test():
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        pp = [['L',(0,0)],[0,(0,0)],[1,(4,23)],[2,(0,0)],[3,(0,0)],[4,(0,0)],[5,(4,19)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
        planet1 = 1
        planet2 = 5
        ty = tajaka_yoga.eesarpha_yoga(pp,planet1,planet2)
        expected_result = True
        test_example(chapter,expected_result,ty)
    eesarpa_yoga_1_test()
def nakta_yoga_tests():
    chapter = 'Chapter 29.2.5 nakta_yoga_tests'
    def nakta_yoga_1_test():
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        pp = [['L',(1,5)],[0,(0,0)],[1,(3,11)],[2,(7,15)],[3,(0,0)],[4,(0,0)],[5,(2,13)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
        planet1 = 2
        planet2 = 5
        planet3 = 1
        ty = tajaka_yoga.nakta_yoga(pp,planet3)
        expected_result = (True,[(planet1,planet2)])
        test_example(chapter,expected_result,ty)
        ty = tajaka_yoga._check_nakta_yoga(pp, planet3, planet1, planet2)
        expected_result = True
        test_example(chapter,expected_result,ty)
    nakta_yoga_1_test()
def yamaya_yoga_tests():
    chapter = 'Chapter 29.2.6 yamaya_yoga_tests'
    def yamaya_yoga_1_test():
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        pp = [['L',(1,5)],[0,(0,25)],[1,(0,20)],[2,(7,15)],[3,(0,23)],[4,(3,16)],[5,(2,13)],[6,(0,0)],[7,(0,0)],[8,(0,0)]]
        planet1 = 2
        planet2 = 5
        planet3 = 4
        
        ty = tajaka_yoga.check_yamaya_yoga(planet3, planet1, planet2, pp)
        expected_result = True
        test_example(chapter,expected_result,ty)
    yamaya_yoga_1_test()
def raja_yoga_tests():
    chapter = 'Chapter 11.7 Raja Yoga Tests '
    chart_10_akbar = ['','','1','','8','','4/5/6/L','0','3','2','7','']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_10_akbar)
    print(chapter+'chart_10_akbar',chart_10_akbar)
    ry_pairs = raja_yoga.get_raja_yoga_pairs(chart_10_akbar)
    print(chapter+'raja yoga pairs',ry_pairs)
    for p1,p2 in ry_pairs:
        print(chapter+'neecha_bhanga_raja_yoga',p1,p2,raja_yoga.neecha_bhanga_raja_yoga(chart_10_akbar, p1, p2))
    chart_15_rajiv_gandhi = ['', '', '6', '7', 'L/0/1/3/4/5', '2', '', '', '', '8', '', '']
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_15_rajiv_gandhi)
    print(chapter+'chart_15_rajiv_gandhi',chart_15_rajiv_gandhi)
    ry_pairs = raja_yoga.get_raja_yoga_pairs(chart_15_rajiv_gandhi)
    print(chapter+'raja yoga pairs',ry_pairs)
    for p1,p2 in ry_pairs:
        print(chapter+'neecha_bhanga_raja_yoga',p1,p2,raja_yoga.neecha_bhanga_raja_yoga(chart_15_rajiv_gandhi, p1, p2))
    chart_oprah_winfrey = ['','4','','8','','','6','1/2','','0/3/5/L/7','',''] # For dharma karmadhipathi check
    print(chapter+'chart_oprah_winfrey',chart_oprah_winfrey)
    ry_pairs = raja_yoga.get_raja_yoga_pairs(chart_oprah_winfrey)
    print(chapter+'raja yoga pairs',ry_pairs)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_oprah_winfrey)
    for p1,p2 in ry_pairs:
        print(chapter+'neecha_bhanga_raja_yoga',p1,p2,raja_yoga.neecha_bhanga_raja_yoga(chart_oprah_winfrey, p1, p2))
        print(chapter+'dharma_karmadhipati_raja_yoga',p1,p2,raja_yoga.dharma_karmadhipati_raja_yoga(p_to_h, p1, p2))
    chart_salman_khan = ['0/2/5','','7','6','','','L/1','','8/4','','','3'] # For vipareetha rajacheck
    print(chapter+'chart_salman_khan',chart_salman_khan)
    ry_pairs = raja_yoga.get_raja_yoga_pairs(chart_salman_khan)
    print(chapter+'raja yoga pairs',ry_pairs)
    p_to_h = utils.get_planet_to_house_dict_from_chart(chart_salman_khan)
    for p1,p2 in ry_pairs:
        print(chapter+'neecha_bhanga_raja_yoga',p1,p2,raja_yoga.neecha_bhanga_raja_yoga(chart_salman_khan, p1, p2))
        print(chapter+'vipareetha_raja_yoga',p1,p2,raja_yoga.vipareetha_raja_yoga(p_to_h, p1, p2))
def ravi_yoga_tests():
    chapter = 'Chapter 11.2 '
    def vesi_yoga_test():
        exercise = 'Vesi Yoga '
        h_to_p = ['L','0','2','3','4','5','6','7','8','1','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vesi_yoga(h_to_p),h_to_p)
        h_to_p = ['','0','L','3/2','4','5','6','7','8','1','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vesi_yoga(h_to_p),h_to_p)
    vesi_yoga_test()
    def vosi_yoga_test():
        exercise = 'Vosi Yoga '
        h_to_p = ['L/2','0','','3','4','5','6','7','8','1','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vosi_yoga(h_to_p),h_to_p)
        h_to_p = ['L','0','1','3/2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vosi_yoga(h_to_p),h_to_p)
    vosi_yoga_test()
    def ubhayachara_yoga_test():
        exercise = 'ubhayachara Yoga '
        h_to_p = ['L/2','0','3','','4','5','6','7','8','1','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.ubhayachara_yoga(h_to_p),h_to_p)
        h_to_p = ['2','0','3/1','','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.ubhayachara_yoga(h_to_p),h_to_p)
    ubhayachara_yoga_test()
    def nipuna_yoga_test():
        exercise = 'Nipuna / budha_aaditya Yoga '
        h_to_p = ['L/2','','','0/3','4','5','6','7','8','1','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.nipuna_yoga(h_to_p),h_to_p)
        h_to_p = ['L','0/5','1','3/2','4','','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.budha_aaditya_Yoga(h_to_p),h_to_p)
    nipuna_yoga_test()
def chandra_yoga_tests():
    chapter = 'Chapter 11.3 '
    def sunaphaa_yoga_test():
        exercise = 'Sunaphaa Yoga '
        h_to_p = ['L','1','2','3','4','5','6','7','8','0','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sunaphaa_yoga(h_to_p),h_to_p)
        h_to_p = ['','1','L','3/2','4','5','6','7','8','0','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sunaphaa_yoga(h_to_p),h_to_p)
    sunaphaa_yoga_test()
    def anaphaa_yoga_test():
        exercise = 'Anaphaa Yoga '
        h_to_p = ['2','1','L','3','4','5','6','7','8','0','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.anaphaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','','3/2','4','5','6','7','8','0','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.anaphaa_yoga(h_to_p),h_to_p)
    anaphaa_yoga_test()
    def duradhara_yoga_test():
        exercise = 'Duradhara Yoga '
        h_to_p = ['2','1','L/3','','4','5','6','7','8','0','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.duradhara_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','0','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.duradhara_yoga(h_to_p),h_to_p)
    duradhara_yoga_test()
    def kemadruma_yoga_test():
        exercise = 'kemadruma Yoga '
        h_to_p = ['','1/0','L','','2/3','','4/5','6/7','','8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.kemadruma_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.kemadruma_yoga(h_to_p),h_to_p)
    kemadruma_yoga_test()
    def chandra_mangala_yoga_test():
        exercise = 'chandra_mangala Yoga '
        h_to_p = ['','0/1/2','L','','3','','4/5','6/7','','8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.chandra_mangala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.chandra_mangala_yoga(h_to_p),h_to_p)
    chandra_mangala_yoga_test()
    def adhi_yoga_test():
        exercise = 'Adhi Yoga '
        h_to_p = ['','0/1/2','L','4','3','','5','6','','8','7','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.adhi_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.adhi_yoga(h_to_p),h_to_p)
    adhi_yoga_test()
def pancha_mahapurusha_yogas():
    chapter = 'Chapter 11.4 Pancha Mahapurusha Yogas '
    def ruchaka_yoga_test():
        exercise = 'Ruchaga Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['2','0/1','','4','3','5','L','6','','8','7','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.ruchaka_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.ruchaka_yoga(h_to_p),h_to_p)
    ruchaka_yoga_test()
    def bhadra_yoga_test():
        exercise = 'Bhadra Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['5','0/1','L','4','2','3','','6','','8','7','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.bhadra_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.bhadra_yoga(h_to_p),h_to_p)
    bhadra_yoga_test()
    def sasa_yoga_test():
        exercise = 'Sasa Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['5','0/1','8','4','2','3','6','','','L','7','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sasa_yoga(h_to_p),h_to_p)
        h_to_p = ['','L/1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sasa_yoga(h_to_p),h_to_p)
    sasa_yoga_test()
    def maalavya_yoga_test():
        exercise = 'Maalavya Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['','0/1','L','4','8','3','6','2','','','7','5']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.maalavya_yoga(h_to_p),h_to_p)
        h_to_p = ['','L/1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.maalavya_yoga(h_to_p),h_to_p)
    maalavya_yoga_test()
    def hamsa_yoga_test():
        exercise = 'Hamsa Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['','0/1','','5','8','3','6','2','L','','7','4']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.hamsa_yoga(h_to_p),h_to_p)
        h_to_p = ['','L/1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.hamsa_yoga(h_to_p),h_to_p)
    hamsa_yoga_test()
def naabhasa_aasrya_yogas():
    chapter = 'Chapter 11.5 Naabhasa Aasraya Yogas '
    def rajju_yoga_test():
        exercise = 'Rajju Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['0/1','L','','2/3','','','4/5','','','6/7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.rajju_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.rajju_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4/5','','','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.rajju_yoga(h_to_p),h_to_p)
    rajju_yoga_test()
    def musala_yoga_test():
        exercise = 'Musala Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['','L/0/1','','','2/3','','','4/5','','','6/7/8','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.musala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.musala_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4/5','','','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.musala_yoga(h_to_p),h_to_p)
    musala_yoga_test()
    def nala_yoga_test():
        exercise = 'Nala Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['','L','0/1','','','2/3','','','4/5','','','6/7/8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.nala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.nala_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4/5','','','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.nala_yoga(h_to_p),h_to_p)
    nala_yoga_test()
def dala_yogas():
    chapter = 'Chapter 11.6 Dala Yogas '
    def maalaa_yoga_test():
        exercise = 'Maalaa Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['L','0','1','5','2','6','4','7','8','3','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.maalaa_yoga(h_to_p),h_to_p)
        h_to_p = ['','0','1','L/5','2','6','4','7','8','3','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.maalaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.maalaa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.maalaa_yoga(h_to_p),h_to_p)
    maalaa_yoga_test()
    def sarpa_yoga_test():
        exercise = 'Sarpa Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['0','2','3','1','7','','4','L','5','','8','6']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sarpa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sarpa_yoga(h_to_p),h_to_p)
    sarpa_yoga_test()
def aakriti_yogas():
    chapter = 'Chapter 11.7 Aakriti Yogas '
    def gadaa_yoga_test():
        exercise = 'Gadaa Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['L/0/1/2/3','','','4/5/6/7/8','','','','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.gadaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','','','4/5/6/7/8','','','0/1/2/3','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.gadaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','','','','','','0/1/2/3','','','4/5/6/7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.gadaa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1/2/3','','','','','','L','','','4/5/6/7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.gadaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.gadaa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.gadaa_yoga(h_to_p),h_to_p)
    gadaa_yoga_test()
    def sakata_yoga_test():
        exercise = 'Sakata Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['L/0/1/2/3','','','','','','4/5/6/7/8','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sakata_yoga(h_to_p),h_to_p)
        h_to_p = ['','','L/0/1/2/3','','','','','','4/5/6/7/8','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sakata_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sakata_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sakata_yoga(h_to_p),h_to_p)
    sakata_yoga_test()
    def vihanga_yoga_test():
        exercise = 'Vihanga Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['L','','','/0/1/2/3','','','','','','4/5/6/7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vihanga_yoga(h_to_p),h_to_p)
        h_to_p = ['','','L','','','0/1/2/3','','','','','','4/5/6/7/8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vihanga_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vihanga_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vihanga_yoga(h_to_p),h_to_p)
    vihanga_yoga_test()
    def sringaataka_yoga_test():
        exercise = 'Sringaataka Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['L/0/1/2','','','','3/4/5','','','','6/7/8','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sringaataka_yoga(h_to_p),h_to_p)
        h_to_p = ['6/7/8','','','','L/0/1/2','','','','3/4/5','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sringaataka_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sringaataka_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sringaataka_yoga(h_to_p),h_to_p)
    sringaataka_yoga_test()
    def hala_yoga_test():
        exercise = 'Hala Yoga '
        #Ar,Ta,Ge,Cn,Le,Vi,Li,Sc,Sg,Cp,Aq,Pi
        h_to_p = ['L','0/1/2','','','','3/4/5','','','','6/7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.hala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','','0/1/2','','','','3/4/5','','','','6/7/8','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.hala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','','','0/1/2','','','','3/4/5','','','','6/7/8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.hala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.hala_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.hala_yoga(h_to_p),h_to_p)
    hala_yoga_test()
    def vajra_yoga_test():
        exercise = 'Vajra Yoga '
        h_to_p = ['L/4','','1/3','2','','8','5','0','','6','','7']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vajra_yoga(h_to_p),h_to_p)
        h_to_p = ['L/4/2','','','0/1','','','5','','','7/8/3','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vajra_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vajra_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vajra_yoga(h_to_p),h_to_p)
    vajra_yoga_test()  
    def yava_yoga_test():
        exercise = 'Yava Yoga '
        h_to_p = ['L/0/1','','2/3','4','','','7/8','','','5','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.yava_yoga(h_to_p),h_to_p)
        h_to_p = ['L/0/1/2','','','4','','','7/8/3','','','5','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.yava_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.yava_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.yava_yoga(h_to_p),h_to_p)
    yava_yoga_test()  
    def kamala_yoga_test():
        exercise = 'Kamala Yoga '
        h_to_p = ['L/0/1','','','2/3/4','','','7/8','','','5/6','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.kamala_yoga(h_to_p),h_to_p)
        h_to_p = ['2/4','','','L/0/1/','','','7/8/3','','','5/6','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.kamala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.kamala_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.kamala_yoga(h_to_p),h_to_p)
    kamala_yoga_test()  
    def vaapi_yoga_test():
        exercise = 'Vaapi Yoga '
        h_to_p = ['L','0/1','','','2/3/4','','','7/8','','','5/6','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vaapi_yoga(h_to_p),h_to_p)
        h_to_p = ['L','','0/1/2','','','3/4','','','5/6','','','7/8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.vaapi_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vaapi_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.vaapi_yoga(h_to_p),h_to_p)
    vaapi_yoga_test()  
    def yoopa_yoga_test():
        exercise = 'Yoopa Yoga '
        h_to_p = ['L/0/1','2/3/4','7/8','5/6','','','','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.yoopa_yoga(h_to_p),h_to_p)
        h_to_p = ['','','L/0/1','2/3/4','7/8','5/6','','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.yoopa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.yoopa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.yoopa_yoga(h_to_p),h_to_p)
    yoopa_yoga_test()  
    def sakti_yoga_test():
        exercise = 'Sakti Yoga '
        h_to_p = ['L','','','','','','5/6','0/1','2/3/4','7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sakti_yoga(h_to_p),h_to_p)
        h_to_p = ['','','L','','','','','','5/6','0/1','2/3/4','7/8','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.sakti_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sakti_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.sakti_yoga(h_to_p),h_to_p)
    sakti_yoga_test()  
    def danda_yoga_test():
        exercise = 'Danda Yoga '
        h_to_p = ['L/7/8','','','','','','','','','5/6','0/1','2/3/4']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.danda_yoga(h_to_p),h_to_p)
        h_to_p = ['5/6','0/1','2/3/4','L/7/8','','','','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.danda_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.danda_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.danda_yoga(h_to_p),h_to_p)
    danda_yoga_test()  
    def naukaa_yoga_test():
        exercise = 'Naukaa Yoga '
        h_to_p = ['L/0','1','2','3/7','4','5/8','6','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.naukaa_yoga(h_to_p),h_to_p)
        h_to_p = ['','','L/0','1','2','3/7','4','5/8','6','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.naukaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.naukaa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.naukaa_yoga(h_to_p),h_to_p)
    naukaa_yoga_test()  
    def koota_yoga_test():
        exercise = 'Koota Yoga '
        h_to_p = ['L','','','0','1','2','3/7','4','5/8','6','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.koota_yoga(h_to_p),h_to_p)
        h_to_p = ['4','5/8','6','','','L','','','0','1','2','3/7']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.koota_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.koota_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.koota_yoga(h_to_p),h_to_p)
    koota_yoga_test()  
    def chatra_yoga_test():
        exercise = 'Chatra Yoga '
        h_to_p = ['L/6','','','','','','0','1','2','3/7','4','5/8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.chatra_yoga(h_to_p),h_to_p)
        h_to_p = ['1','2','3/7','4','5/8','L/6','','','','','','0']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.chatra_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.chatra_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.chatra_yoga(h_to_p),h_to_p)
    chatra_yoga_test()  
    def chaapa_yoga_test():
        exercise = 'Chaapa Yoga '
        h_to_p = ['4/L','5/6','7','8','','','','','','0/1','2','3']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.chaapa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','2','3','4/L','5/6','7','8','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.chaapa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','4','5','6','7','8','','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.chaapa_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.chaapa_yoga(h_to_p),h_to_p)
    chaapa_yoga_test()  
    def ardha_chandra_yoga_test():
        exercise = 'ardha_chandra Yoga '
        h_to_p = ['4/L','5/6','7','8','','','','','','0/1','2','3']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.ardha_chandra_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','2','3','4/L','5/6','7','8','','','','','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.ardha_chandra_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','','5','6','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.ardha_chandra_yoga(h_to_p),h_to_p)
        h_to_p = ['0/1','','','2/3','','8','4','','5','6/7/L','','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.ardha_chandra_yoga(h_to_p),h_to_p)
    ardha_chandra_yoga_test()  
    def chakra_yoga_test():
        exercise = 'chakra Yoga '
        h_to_p = ['4/L','','7','','5/6','','8','','0/1','','2/3','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.chakra_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','','5','6','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.chakra_yoga(h_to_p),h_to_p)
    chakra_yoga_test()  
    def samudra_yoga_test():
        exercise = 'Samudra Yoga '
        h_to_p = ['L','4','','7','','5/6','','8','','0/1','','2/3']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.samudra_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','','5','6','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.samudra_yoga(h_to_p),h_to_p)
    samudra_yoga_test()
def sankhya_yoga_tests():
    chapter = 'Chapter 11.5.4 Sankhya Yogas '
    def veenaa_yoga_test():  
        exercise = 'Veenaa Yoga '
        h_to_p = ['L/0','4','','1','2','5','','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.veenaa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','','5','6','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.veenaa_yoga(h_to_p),h_to_p)
    veenaa_yoga_test()
    def daama_yoga_test():  
        exercise = 'Daama Yoga '
        h_to_p = ['L/0/1','4','','','2','5','','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.daama_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2/5','','','6','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.daama_yoga(h_to_p),h_to_p)
    daama_yoga_test()
    def paasa_yoga_test():  
        exercise = 'Paasa Yoga '
        h_to_p = ['L/0/1','4','','','2/5','','','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.paasa_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1/6','0/3','2/5','','','','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.paasa_yoga(h_to_p),h_to_p)
    paasa_yoga_test()
    def kedaara_yoga_test():  
        exercise = 'Kedaara Yoga '
        h_to_p = ['L/0/1','','4/3','7','2/5','','','6','','','8','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.kedaara_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1/6/8','0/3','2','','','','5/7','','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.kedaara_yoga(h_to_p),h_to_p)
    kedaara_yoga_test()
    def soola_yoga_test():  
        exercise = 'Soola Yoga '
        h_to_p = ['L/0/1','','','','4/2/5','','','3/6','','','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.soola_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1/6','0/3','2/5','','','','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.soola_yoga(h_to_p),h_to_p)
    soola_yoga_test()
    def yuga_yoga_test():  
        exercise = 'Yuga Yoga '
        h_to_p = ['L/0/1/3','','','','4/2/5/6','','','','','','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.yuga_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1/6','0/3','2/5','','','','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.yuga_yoga(h_to_p),h_to_p)
    yuga_yoga_test()
    def gola_yoga_test():  
        exercise = 'Gola Yoga '
        h_to_p = ['L','','','','4/2/5/6/0/1/3','','','','','','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.gola_yoga(h_to_p),h_to_p)
        h_to_p = ['L','','','','4/2/5/7/0/1/3','','','','','','6','8']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.gola_yoga(h_to_p),h_to_p)
    gola_yoga_test()
def other_yoga_tests():
    chapter = 'Chapter 11.6 Other Popular Yogas '
    def subha_yoga_test():
        exercise = 'Subha Yoga '
        h_to_p = ['L/4','5','','1','2','6','0','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.subha_yoga(h_to_p),h_to_p)
        h_to_p = ['L','5','4','1','2','6','0','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.subha_yoga(h_to_p),h_to_p)
        h_to_p = ['L/4','8','','1','2','0','','3','','6','7','5']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.subha_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','0/3','2','','5','6','7','8','','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.subha_yoga(h_to_p),h_to_p)
    subha_yoga_test()
    def asubha_yoga_test():
        exercise = 'Asubha Yoga '
        h_to_p = ['L/0','5','','1','2','6','4','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.asubha_yoga(h_to_p),h_to_p)
        h_to_p = ['L','1','4','5','2','6','0','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.asubha_yoga(h_to_p),h_to_p)
        h_to_p = ['L/4','5','','1','2','0','','3','','6','7','8']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.asubha_yoga(h_to_p),h_to_p)
        h_to_p = ['L','5','0/3','2','','5','6','7','8','1','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.asubha_yoga(h_to_p),h_to_p)
    asubha_yoga_test()
    def gaja_kesari_yoga_test():
        """ TODO: Not impmented yet"""
        return
        exercise = 'Gaja Kesari Yoga '
        h_to_p = ['','','','','6/5','0/3/8','','1/2/L','','','4','7'] #Narendra Modi
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.gaja_kesari_yoga(h_to_p),h_to_p)
        #h_to_p = ['L','5','0/3','2','','5','6','7','8','1','4','']
        #expected_result = False
        #test_example(chapter+exercise,expected_result,yoga.gaja_kesari_yoga(h_to_p),h_to_p)
    gaja_kesari_yoga_test()
    def guru_mangala_yoga_test():
        exercise = 'Guru Mangala Yoga '
        h_to_p = ['','2/4','','','6/5','0/3/8','','1/L','','','','7'] #Narendra Modi
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.guru_mangala_yoga(h_to_p),h_to_p)
        h_to_p = ['','2','','','6/5','0/3/8','','1/L/4','','','','7'] #Narendra Modi
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.guru_mangala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','5','0/3','2','','5','6','7','8','1','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.guru_mangala_yoga(h_to_p),h_to_p)
    guru_mangala_yoga_test()
    def amala_yoga_test():
        exercise = 'Amala Yoga '
        h_to_p = ['L','2','','','6/5','0/3/8','','1/L','','4','','7']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.amala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','2','','','6/5','0/3/8','','1/L/4','','','','7']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.amala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','5','0/3','2','','','6','7','8','1','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.amala_yoga(h_to_p),h_to_p)
    amala_yoga_test()
    def parvata_yoga_test():
        exercise = 'Parvata Yoga '
        h_to_p = ['3','','','','','','','5','','','L/4','']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.parvata_yoga(h_to_p),h_to_p)
        h_to_p = ['L','5','0/3','2','','','6','7','8','1','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.parvata_yoga(h_to_p),h_to_p)
    parvata_yoga_test()
    def kaahala_yoga_test():
        exercise = 'Kaahala Yoga '
        h_to_p = ['','','','L/4','','','5','','','','','1']
        expected_result = True
        test_example(chapter+exercise,expected_result,yoga.kaahala_yoga(h_to_p),h_to_p)
        h_to_p = ['L','5','0/3','2','','','6','7','8','1','4','']
        expected_result = False
        test_example(chapter+exercise,expected_result,yoga.kaahala_yoga(h_to_p),h_to_p)
    kaahala_yoga_test()
def special_lagna_tests():
    date_of_birth_as_tuple = (1996,12,7)
    time_of_birth_as_tuple = (10,34,0)
    place = drig_panchanga.Place('unknown',13.0389,80.2629,5.5)
    time_of_birth_in_hours = time_of_birth_as_tuple[0]+time_of_birth_as_tuple[1]/60+time_of_birth_as_tuple[2]/3600.0
    jd = utils.julian_day_number(date_of_birth_as_tuple, time_of_birth_as_tuple)
    expected_results = [(4, 2.865436635526862),(11, 27.123769968860245),(6, 5.736269968860142)]
    #print(time_of_birth_in_hours,sun_rise_hours,time_diff_mins)
    for l, lagna_rate_factor in enumerate([1,0.5,1.25]):
        sa = drig_panchanga.special_ascendant(jd, place, time_of_birth_in_hours, lagna_rate_factor, divisional_chart_factor=1)
        test_example("Special Lagna tests",expected_results[l],sa)
def special_vratha_tests():
    utils.set_language('ta')
    utils.get_resource_lists()
    msgs = utils.get_resource_messages()
    drig_panchanga.set_ayanamsa_mode(ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
    lat = 13.0389 # 42.1181# 13.0389 # 41.881832 # 65.8252 N # Latitude - N+/S-
    lon = 80.2619#-88.0962 #-87.623177# -144.0657 W # Longitude  - E+/W-
    tz = 5.5#-5.0#
    place = drig_panchanga.Place('PlacePerLatLong',lat, lon, tz)#('Chennai,IN',lat, lon, tz)
    start_date = drig_panchanga.Date(2022,1,1)
    end_date = drig_panchanga.Date(2022,12,31)
    tithi_index = vratha._pournami_tithi
    vdates = vratha.tithi_dates(place, start_date, end_date, tithi_index)
    print('tithi_dates',vdates)
    vdates = vratha.search(place,start_date,end_date,tithi_index=vratha._pournami_tithi[0])
    print('search pournami',vdates)
    mpds = vratha.search(place,start_date,end_date,tithi_index=vratha._pournami_tithi[0],tamil_month_index=vratha._purattaasi)
    print('search puratasi pournami',mpds)
    sr_dates = vratha.srartha_dates(place, start_date, end_date)
    print('srartha dates',sr_dates)
    sr_dates = vratha.special_vratha_dates(place, start_date, end_date, 'srartha', vratha_index_list=None)
    print('search special srartha',sr_dates)
    print('search special yugadhi',vratha.special_vratha_dates(place,start_date,end_date,'yugadhi'))
    #Sankranti Test
    s_dates = vratha.sankranti_dates(place, start_date, end_date, return_as_str=False)
    print('sankranti_dates',s_dates)
    vdates = vratha.manvaadhi_dates(place, start_date, end_date)
    print('manvaadhi_dates',vdates)
    vdates = vratha.ashtaka_dates(place, start_date, end_date)
    print('ashtaka_dates',vdates)
    vdates = vratha.yugadhi_dates(place, start_date, end_date)
    print('yugadhi_dates',vdates)
    print('nakshathra_dates',vratha.nakshathra_dates(place,start_date,end_date,vratha._pournami_tithi))
    print('special_vratha_dates nakshathra',vratha.special_vratha_dates(place,start_date,end_date,'nakshathra',vratha._pournami_tithi))
    vdates = vratha.sankatahara_chathurthi_dates(place, start_date, end_date)
    print('sankatahara_chathurthi_dates',vdates)
    vdates = vratha.shivarathri_dates(place, start_date, end_date)
    print('shivarathri_dates',vdates)
    vdates = vratha.pradosham_dates(place,start_date,end_date)
    print('pradosham_dates',vdates)
    start_date = drig_panchanga.Date(-3101,1,22)
    end_date = drig_panchanga.Date(-3101,1,23)
    vdates = vratha.conjunctions(place,start_date,end_date,30.0,planets_in_same_house=True)
    print('conjunctions',vdates)
def chapter_14_tests():
    chapter = 'Chapter 14'
    place = drig_panchanga.Place('unknown',15+39/60, 38+6/60, +1.0)
    dob = drig_panchanga.Date(1946,12,2)
    tob = (6,45,0)
    time_of_birth_in_hours = tob[0]+tob[1]/60+tob[2]/3600.0
    jd = swe.julday(dob.year,dob.month,dob.day, time_of_birth_in_hours)
    divisional_chart_factor = 1
    planet_positions = drig_panchanga.dhasavarga(jd,place,divisional_chart_factor)
    ascendant_longitude = drig_panchanga.ascendant(jd,place)[1]
    asc_house,asc_long = drig_panchanga.dasavarga_from_long(ascendant_longitude,divisional_chart_factor)
    planet_positions += [[const._ascendant_symbol,(asc_house,asc_long)]]
    def maraka_tests():
        chapter = 'Chapter 14.2 Maraka Tests'
        """
            Suppose lagna is in Le, Saturn is in Sg and Mars is in Ge. 
            Then Saturn is a maraka on account of owning the 7th house (Aq).
            Mars is a malefic and he is in Ge.
        """
        chart_12 = ['8','5','2','','L','','7','4','3/6','0','','1']
        chk = house.marakas(chart_12)
        test_example(chapter+' Maraka Tests',[3,6],chk,'marakas in',chart_12)        
        """
            Suppose lagna is in Pi,Mars is in Ge, Mercury is in Cp and Saturn is in Ar. 
            Mars and Mercury are marakas. Saturn is also a maraka
        """
        chart_12 = ['6','0','2','1','4','','7','','8','3','5','L']
        chk = house.marakas(chart_12)
        test_example(chapter+' Maraka Tests',[2,3,6],chk,'marakas in',chart_12)
    
        exercise = 'Exercise 23'    
        chart_8 = ['','7','','6','','','3/4/5','L/0/2/8','','','1','']
        chk = house.marakas(chart_8)
        test_example(chapter+exercise,[3,4,5,7],chk,'marakas in',chart_8)
    def rudra_trishoola_tests():
        chapter = 'Chapter 14.3 Rudra Trishoola Tests'
        exercise = 'Exercise 23'
        chart_8 = ['','7','','6','','','3/4/5','L/0/2/8','','','1','']
        r = house.rudra_based_on_planet_positions(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        test_example(chapter+exercise,(3, 6, [6, 10, 2]),r)
    def maheshwara_tests():
        chapter = 'Chapter 14.3 Maheshwara Tests '
        exercise = 'Exercise 23'
        mh = house.maheshwara(dob, tob, place, divisional_chart_factor)
        test_example(chapter+exercise,4,mh)

    def longevity_tests():
        chapter = 'Chapter 14.4 Longevity Tests '
        exercise = 'Exercise 23'
        lp = house.longevity(dob,tob,place,divisional_chart_factor=1)
        test_example(chapter+exercise,64,lp,'Longevity Years')
    
    maraka_tests()
    rudra_trishoola_tests()
    maheshwara_tests()
    longevity_tests()
if __name__ == "__main__":
    chapter_14_tests()
    exit()
    #"""
    chapter_14_tests()
    exit()
    drig_panchanga.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE) #('TRUE_CITRA')
    utils_tests()
    panchanga_tests()
    tithi_tests()
    nakshatra_tests()
    yogam_tests()
    masa_tests()
    special_lagna_tests()
    graha_drishti_tests()
    raasi_drishti_tests()
    stronger_lord_tests()
    stronger_rasi_tests()
    ashtaka_varga_tests()
    vimsottari_tests()
    ashtottari_tests()
    # Dhasa tests
    narayana_dhasa_tests()
    kendradhi_rasi_dhasa_tests()
    bhava_graha_arudha_tests()
    sudasa_dhasa_tests()
    drig_dhasa_tests()
    nirayana_shoola_dhasa_tests()
    shoola_dhasa_tests()
    kalachakra_dhasa_tests()
    vimsottari_adhipati_tests()
    patyayini_tests()
    mudda_tests()
    varsha_narayana_tests()
    sudharsana_chakra_dhasa_tests()
    # Other tajaka tests
    saham_tests()
    harsha_bala_tests()
    pancha_vargeeya_bala_tests()
    dwadhasa_vargeeya_bala_tests()
    lord_of_the_year_test()
    lord_of_the_month_test()
    tajaka_yoga_tests()
    ithasala_yoga_tests()
    yamaya_yoga_tests()
    retrograde_combustion_tests()
    #"""
    raja_yoga_tests()
    special_vratha_tests()
    ravi_yoga_tests()
    chandra_yoga_tests()
    pancha_mahapurusha_yogas()
    naabhasa_aasrya_yogas()
    dala_yogas()
    aakriti_yogas()
    sankhya_yoga_tests()
    other_yoga_tests()
    chapter_27_tests()
    #chart_tests()