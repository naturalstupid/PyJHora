from hora import const, utils
from hora.horoscope.chart.house import *
def bhava_arudhas_from_planet_positions(planet_positions):
    """
        gives Bhava Arudhas for each house from the chart
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
    """
        TODO: Check if A11 is calculated correct for tajaka charts?
    """
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    houses = [(h+asc_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for i,h in enumerate(houses):
        # get house lord. For Aq/Sc get stronger lord
        #print('house',i,'in rasi',rasi_names_en[h])
        lord_of_the_house = house_owner_from_planet_positions(planet_positions, h, check_during_dhasa=False)
        house_of_the_lord = p_to_h[lord_of_the_house]
        #print('house',i,'lord_of_the_house',lord_of_the_house,'house_of_the_lord',house_of_the_lord)
        #print(planet_list[lord_of_the_house],rasi_names_en[house_of_the_lord])
        signs_between_house_and_lord = (house_of_the_lord+1+12-h)%12
        #print('signs_between_house_and_lord',h,house_of_the_lord,signs_between_house_and_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = ((bhava_arudha_of_house+1+12-h)%12)
        #print('signs_from_the_house',signs_from_the_house)
        if signs_from_the_house in [1,7]:
            #print('in [1,7] from the original house')
            bhava_arudha_of_house = (bhava_arudha_of_house+10-1)%12
        #print('bhava arudha:','A'+str(i+1),'is',bhava_arudha_of_house,rasi_names_en[bhava_arudha_of_house])
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def bhava_arudhas(chart):
    """
        gives Bhava Arudhas for each house from the chart
        @param chart: Enter chart information in the following format. For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return bhava arudhas of houses. first element is for the first house from lagna and so on
    """
    h_to_p = chart[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    houses = [(h+asc_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for i,h in enumerate(houses):
        # get house lord. For Aq/Sc get stronger lord
        #print('house',i,'in rasi',rasi_names_en[h])
        lord_of_the_house = house_owner(h_to_p, h) # V2.3.1
        house_of_the_lord = p_to_h[lord_of_the_house]
        #print('house',i,'lord_of_the_house',lord_of_the_house,'house_of_the_lord',house_of_the_lord)
        #print(planet_list[lord_of_the_house],rasi_names_en[house_of_the_lord])
        signs_between_house_and_lord = (house_of_the_lord+1+12-h)%12
        #print('signs_between_house_and_lord',h,house_of_the_lord,signs_between_house_and_lord)
        bhava_arudha_of_house = (house_of_the_lord+signs_between_house_and_lord-1)%12
        signs_from_the_house = ((bhava_arudha_of_house+1+12-h)%12)
        #print('signs_from_the_house',signs_from_the_house)
        if signs_from_the_house in [1,7]:
            #print('in [1,7] from the original house')
            bhava_arudha_of_house = (bhava_arudha_of_house+10-1)%12
        #print('bhava arudha:','A'+str(i+1),'is',bhava_arudha_of_house,rasi_names_en[bhava_arudha_of_house])
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def graha_arudhas_from_planet_positions(planet_positions):
    """
        gives Graha Arudhas for each planet from the planet positions
        @param planet_positions: Planet Positions in the format: \
        [ [planet,[rasi,longitude]], [[,]].., [[,]]]
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    graha_arudhas_of_planets = []
    for p,planet in enumerate(planet_list):
        house_of_the_planet = p_to_h[p]
        #print('house_of_the_planet',house_of_the_planet,rasi_names_en[house_of_the_planet])
        sign_owned_by_planet = const.house_lords_dict[p]
        #print('sign_owned_by_planet',sign_owned_by_planet)
        if len(sign_owned_by_planet)>1:
            #print('stronger of',sign_owned_by_planet[0],sign_owned_by_planet[1])
            sign_owned_by_planet = stronger_rasi_from_planet_positions(planet_positions,sign_owned_by_planet[0],sign_owned_by_planet[1])
            #print('stronger raasi', sign_owned_by_planet)
        else:
            sign_owned_by_planet = sign_owned_by_planet[0]
        #print(planet,rasi_names_en[sign_owned_by_planet])
        count_to_strong = (sign_owned_by_planet+1+12-house_of_the_planet)%12
        #print('count_to_strong',count_to_strong)
        count_to_arudha = (house_of_the_planet+2*(count_to_strong-1))%12
        #print('count again',count_to_arudha,rasi_names_en[count_to_arudha])
        count_from_house = (house_of_the_planet+12-count_to_arudha)%12
        #print('count_from_house',count_from_house)
        if count_from_house in [0,6]:
            count_to_arudha = (count_to_arudha+9)%12
            #print('count in [1,7] from house',count_to_arudha)
        graha_padha_of_planet = count_to_arudha
        #print(planet_list[p],rasi_names_en[graha_padha_of_planet],'\n')
        graha_arudhas_of_planets.append(graha_padha_of_planet)
    return graha_arudhas_of_planets
def graha_arudhas(chart):
    """
        gives Graha Arudhas for each planet from the chart
        @param chart: Enter chart information in the following format. For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
    h_to_p = chart[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    #print('house_lords_dict',house_lords_dict)
    asc_house = p_to_h[const._ascendant_symbol]
    graha_arudhas_of_planets = []
    for p,planet in enumerate(planet_list):
        house_of_the_planet = p_to_h[p]
        #print('house_of_the_planet',house_of_the_planet,rasi_names_en[house_of_the_planet])
        sign_owned_by_planet = const.house_lords_dict[p]
        #print('sign_owned_by_planet',sign_owned_by_planet)
        if len(sign_owned_by_planet)>1:
            #print('stronger of',sign_owned_by_planet[0],sign_owned_by_planet[1])
            sign_owned_by_planet = stronger_rasi(h_to_p,sign_owned_by_planet[0],sign_owned_by_planet[1])
            #print('stronger raasi', sign_owned_by_planet)
        else:
            sign_owned_by_planet = sign_owned_by_planet[0]
        #print(planet,rasi_names_en[sign_owned_by_planet])
        count_to_strong = (sign_owned_by_planet+1+12-house_of_the_planet)%12
        #print('count_to_strong',count_to_strong)
        count_to_arudha = (house_of_the_planet+2*(count_to_strong-1))%12
        #print('count again',count_to_arudha,rasi_names_en[count_to_arudha])
        count_from_house = (house_of_the_planet+12-count_to_arudha)%12
        #print('count_from_house',count_from_house)
        if count_from_house in [0,6]:
            count_to_arudha = (count_to_arudha+9)%12
            #print('count in [1,7] from house',count_to_arudha)
        graha_padha_of_planet = count_to_arudha
        #print(planet_list[p],rasi_names_en[graha_padha_of_planet],'\n')
        graha_arudhas_of_planets.append(graha_padha_of_planet)
    return graha_arudhas_of_planets
    
if __name__ == "__main__":
    from hora.tests.pvr_tests import test_example
    from hora.horoscope.chart import house, charts
    def chapter_9_tests():
        chapter = 'Chapter 9.2 Bhava/Graha Arudhas '
        chart_1 = ['4/2/6','','1','7','','L','','','','8','','3/0/5']
        chart_1_dob = (2000,4,9)
        chart_1_tob = (17,55,0)
        chart_1_place = drik.Place('unknwon',42+30/60,-71-12/60,-4.0)
        chart_1_dcf = 1
        chart_2 = ['6','5','','7/8','','','','','3/L','4','1/0/2','']
        chart_2_dob = chart_1_dob
        chart_2_tob = chart_1_tob
        chart_2_place = drik.Place('unknwon',42+30/60,-71-12/60,-5.0)
        chart_2_dcf = 16
        def bhava_arudha_tests_1():
            exercise = 'Example 29 / Chart 1 Bhava Arudha'
            jd_at_dob = utils.julian_day_number(chart_1_dob, chart_1_tob)
            planet_positions = charts.divisional_chart(jd_at_dob, chart_1_place, divisional_chart_factor=chart_1_dcf)
            asc_house = planet_positions[0][1][0]
            ba = bhava_arudhas_from_planet_positions(planet_positions)#bhava_arudhas(chart_1)
            expected_result = [2, 4, 5, 4, 0, 2, 1, 9, 9, 5, 1, 6]
            #Ans A1/AL:Ge, A2:Le, A3:Vi, A4:Le, A5:Ar, A6:Ge, A7:Ta, A8:Cp, A9:Cp, A10:Vi, A11: Ta, A12:Li
            houses = [(h + asc_house) % 12 for h in range(12)] 
            for i, h in enumerate(houses):
                test_example(chapter+exercise,house.rasi_names_en[expected_result[i]],house.rasi_names_en[ba[i]],'A' + str(i + 1))
        def bhava_arudha_tests_2():
            exercise = 'Exercise 12 / Chart 2 Bhava Arudha'
            jd_at_dob = utils.julian_day_number(chart_2_dob, chart_2_tob)
            planet_positions = charts.divisional_chart(jd_at_dob, chart_2_place, divisional_chart_factor=chart_2_dcf)
            asc_house = planet_positions[0][1][0]
            ba = bhava_arudhas_from_planet_positions(planet_positions)#ba = bhava_arudhas(chart_2)
            expected_result = [10,0,8,7,8,10,11,5,1,8,8,10]
            houses = [(h + asc_house) % 12 for h in range(12)] 
            for i, h in enumerate(houses):
                test_example(chapter+exercise,house.rasi_names_en[expected_result[i]],house.rasi_names_en[ba[i]],'A' + str(i + 1))
        def graha_arudha_tests_1():
            exercise = 'Example 29 / Chart 1 Graha Arudha'
            jd_at_dob = utils.julian_day_number(chart_1_dob, chart_1_tob)
            planet_positions = charts.divisional_chart(jd_at_dob, chart_1_place, divisional_chart_factor=chart_1_dcf)
            asc_house = planet_positions[0][1][0]
            ba = graha_arudhas_from_planet_positions(planet_positions)#graha_arudhas(chart_1)
            expected_result = [9,4,9,2,10,1,3,5,5]
            for p in range(9):
                test_example(chapter+exercise,house.rasi_names_en[expected_result[p]],house.rasi_names_en[ba[p]],'contains',house.planet_list[p],"Graha Pada")
        def graha_arudha_tests_2():
            exercise = 'Exercise 13 / Chart 2 Graha Arudha'
            jd_at_dob = utils.julian_day_number(chart_2_dob, chart_2_tob)
            planet_positions = charts.divisional_chart(jd_at_dob, chart_2_place, divisional_chart_factor=chart_2_dcf)
            asc_house = planet_positions[0][1][0]
            ba = graha_arudhas_from_planet_positions(planet_positions)#ba = graha_arudhas(chart_2)
            expected_result = [7,8,2,11,7,10,8,5,11]
            for p in range(9):
                test_example(chapter+exercise,house.rasi_names_en[expected_result[p]],house.rasi_names_en[ba[p]],'contains',house.planet_list[p],"Graha Pada")
        bhava_arudha_tests_1()
        bhava_arudha_tests_2()
        graha_arudha_tests_1()
        graha_arudha_tests_2()
    chapter_9_tests()