from hora import const, utils
from hora.panchanga import panchanga
from hora.horoscope.chart.house import *
import swisseph as swe
def bhava_arudhas(chart):
    """
        gives Bhava Arudhas for each house from the chart
        @param chart: Enter chart information in the following format. For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return a bhava arudhas of houses. first element is for the first house from lagna and so on
    """
    h_to_p = chart[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    asc_house = p_to_h['L']
    houses = [(h+asc_house)%12 for h in range(12)]
    bhava_arudhas_of_houses =[]
    for i,h in enumerate(houses):
        # get house lord. For Aq/Sc get stronger lord
        #print('house',i,'in rasi',rasi_names_en[h])
        lord_of_the_house = const.house_owners[h]
        if h in [7,10]: ## If rasi1 is Aq or Sc there are two lords
            #print('house in [7,10]')
            rahu_kethu_house = list(const.houses_of_rahu_kethu.keys())[list(const.houses_of_rahu_kethu.values()).index(h)]
            #print('rahu_kethu_house',rahu_kethu_house)
            lord_of_the_house = stronger_co_lord(h_to_p, lord_of_the_house,rahu_kethu_house)
            #print('stronger_co_lord',lord_of_the_house,'is the lord_of_the_house')
            #lord_of_the_house = house_owners[stronger_co_lord]
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
        print('bhava arudha:','A'+str(i+1),'is',bhava_arudha_of_house,rasi_names_en[bhava_arudha_of_house])
        bhava_arudhas_of_houses.append(bhava_arudha_of_house)
    return bhava_arudhas_of_houses
def graha_arudhas(chart):
    """
        gives Graha Arudhas for each planet from the chart
        @param chart: Enter chart information in the following format. For each house from Aries planet numbers separated by /
            ['0/1','2','','','3/4/5','','','6','L/7','','8','']
        @return a graha arudhas of planet. first element is for Sun, last element is for Ketu
    """
    h_to_p = chart[:]
    #print('h_to_p',h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    #print('p_to_h',p_to_h)
    #print('house_lords_dict',house_lords_dict)
    asc_house = p_to_h['L']
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
    pass