from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house

sidereal_year = const.sidereal_year

def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    karakas = house.chara_karakas(planet_positions)
    #print('karakas',karakas)
    asc_house = planet_positions[0][1][0]
    dhasa_info = []
    start_jd = jd_at_dob
    human_life_span = sum([(planet_positions[k+1][1][0] - asc_house +12)%12 for k in karakas.keys()])
    for k in karakas.keys():
        k_h = planet_positions[k+1][1][0]
        duration = (k_h - asc_house + 12)%12
        bhukthis = list(karakas.keys())[1:]+[list(karakas.keys())[0]]
        if include_antardasa:
            for bhukthi_lord in bhukthis:
                b_h = planet_positions[bhukthi_lord+1][1][0]
                dd = (b_h - asc_house + 12)%12
                factor = dd *  duration / human_life_span
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((k,bhukthi_lord,dhasa_start,dd))
                start_jd += factor * sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((k,bhukthis,dhasa_start,duration))
            start_jd += duration * sidereal_year
    return dhasa_info
        

if __name__ == "__main__":
    utils.set_language('en')
    dob = (1996,12,7)
    #dob = (1964,11,16)
    #dob = (1917,11,19) #Indira Gandth
    tob = (10,34,0)
    #tob = (4,30,0)
    #tob = (23,11,0) #Indira Gandth
    place = drik.Place('Chennai',13.0878,80.2785,5.5)
    #place = drik.Place('karamadai',11.2428,76.9587,5.5)
    #place = drik.Place('',25+27/60,81+51/60,5.5) #Indira Gandth
    include_antardasa = True
    sd = get_dhasa_antardhasa(dob, tob, place,include_antardasa=include_antardasa)
    if include_antardasa:
        for d,b,t,_ in sd:
            print(house.planet_list[d],house.planet_list[b],t)
    else:
        for d,b,t,_ in sd:
            print(house.planet_list[d],b,t)
        