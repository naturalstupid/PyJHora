from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts, house
from hora.horoscope.dhasa import narayana
""" Paryaaya Dasa NOT IMPLEMENTED FULLY YET
    Dhasas are ok. Antardasa and periods are not matching JHora
"""
sidereal_year = const.sidereal_year
dhasa_adhipati_list = [0,4,6,10,0,4,6,10,0,4,6,10]
antardhasa_list = [6,0,8,10,4,8,6,0,8,10,4,8]
_dhasa_cycles = 2

def _dhasa_duration(planet_positions,dhasa_lord):
    lord_owner = house.house_owner_from_planet_positions(planet_positions, dhasa_lord)
    house_of_lord = planet_positions[lord_owner+1][1][0]
    dhasa_period = (dhasa_lord+13-house_of_lord)%12
    if dhasa_lord in const.even_signs:
        dhasa_period = (house_of_lord+13-dhasa_lord)%12
    return dhasa_period
def _dhasa_lords(planet_positions,dhasa_seed):
    if dhasa_seed in const.dual_signs: # Dual and Chara Paryaaya
        ts = house.trines_of_the_raasi(dhasa_seed)
        sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        dhasa_lords = [(sr+h-1)%12 for h in [1,5,9,2,6,10,3,7,11,4,8,12]]
        if sr in const.even_footed_signs:
            dhasa_lords = [(sr-h+13)%12 for h in [1,5,9,2,6,10,3,7,11,4,8,12]]
    elif dhasa_seed in const.movable_signs: # Movable and Ubhaya Paryaaya
        ts = house.quadrants_of_the_raasi(dhasa_seed)
        sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[3])
        dhasa_lords = [(sr+h-1)%12 for h in [1,4,7,10,2,5,8,11,3,6,9,12]]
        if sr in const.even_footed_signs: # Fixed and Sthira Paryaaya
            dhasa_lords = [(sr-h+13)%12 for h in [1,4,7,10,2,5,8,11,3,6,9,12]]
    else:
        sr = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_seed, (dhasa_seed+6)%12)
        dhasa_lords = [(sr+h-1)%12 for h in [1,7,2,8,3,9,4,10,5,11,6,12]]
        if sr in const.even_footed_signs:
            dhasa_lords = [(sr-h+13)%12 for h in [1,7,2,8,3,9,4,10,5,11,6,12]]
    return dhasa_lords
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=6,years=1,months=1,sixty_hours=1,include_antardasa=False):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    asc_house = planet_positions[0][1][0]
    dhasa_seed = (asc_house+5)%12
    dhasa_lords = _dhasa_lords(planet_positions,dhasa_seed)
    dhasa_info = []
    start_jd = jd_at_dob
    for dc in range(_dhasa_cycles):
        for dhasa_lord in dhasa_lords:
            duration = _dhasa_duration(planet_positions,dhasa_lord)
            bhukthis = _dhasa_lords(planet_positions, dhasa_lord)
            #print('bhukthis',bhukthis)
            if include_antardasa:
                dd = duration/12
                for bhukthi_lord in bhukthis:
                    y,m,d,h = utils.jd_to_gregorian(start_jd)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                    start_jd += dd * sidereal_year
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthis,dhasa_start,duration))
                start_jd += duration * sidereal_year
    return dhasa_info
if __name__ == "__main__":
    utils.set_language('en')
    dob = (1996,12,7)
    #dob = (1819,5,24)
    #dob = (1944,8,20) #Indira Gandth
    tob = (10,34,0)
    #tob = (4,15,0)
    #tob = (8,11,0) #Indira Gandth
    place = drik.Place('Chennai',13.0878,80.2785,5.5)
    #place = drik.Place('',51+30/60,-0-10/60,0.0)
    #place = drik.Place('',18+58/60,72+50/60,5.5) #Indira Gandth
    include_antardasa = False
    sd = get_dhasa_antardhasa(dob, tob, place,include_antardasa=include_antardasa)
    if include_antardasa:
        for d,b,t,_ in sd:
            print(house.rasi_names_en[d],house.rasi_names_en[b],t)
    else:
        for d,b,t,_ in sd:
            print(house.rasi_names_en[d],b,t)
