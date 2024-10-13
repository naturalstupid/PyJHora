from hora import utils, const
from hora.horoscope.chart import charts
from hora.panchanga import drik
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions[1:])
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    planet_dict = {int(p):p_long for p,(_,p_long) in planet_positions[1:]}
    asc_house = p_to_h[const._ascendant_symbol]
    dhasa_progression = []
    h1 = 0
    start_jd = jd_at_dob
    for h in range(12):
        hs = (asc_house+3+h)%12
        # Get planets from the house
        if h_to_p[hs] == '': continue
        planets = list(map(int,h_to_p[hs].split('/')))
        d1 = {p:l for p,l in planet_dict.items() if p in planets}
        pl_new = [p for (p,_) in sorted(d1.items(), key=lambda item:item[1],reverse=True)]
        for pl in pl_new:
            durn = ((asc_house+h1+12) - p_to_h[pl])%12
            dhasa_progression.append((pl,durn))
            h1 += 1
    dhasa_bhukthi_info = []; dhasa_len = len(dhasa_progression); total_dhasa_duration = 0
    for dhasa_cycle in range(2):
        for dhasa in range(dhasa_len):
            dhasa_lord,dhasa_duration = dhasa_progression[dhasa]
            total_dhasa_duration += dhasa_duration
            if include_antardhasa:
                bhukthi_duration = dhasa_duration/dhasa_len
                for bhukthi in range(dhasa_len):
                    y,m,d,h = utils.jd_to_gregorian(start_jd)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    bhukthi_lord = dhasa_progression[(dhasa+bhukthi)%dhasa_len][0]
                    dhasa_bhukthi_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(bhukthi_duration,2)))
                    start_jd += bhukthi_duration*const.sidereal_year
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_bhukthi_info.append((dhasa_lord,dhasa_start,dhasa_duration))
                start_jd += dhasa_duration*const.sidereal_year
            if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
                break
    return dhasa_bhukthi_info
if __name__ == "__main__":
    """
    dhasa_progression = [(2,9),(1,9),(3,9),(5,9),(4,9),(6,9),(7,9),(8,9),(0,9)]
    dhasa_len = len(dhasa_progression)
    for d in range(dhasa_len):
        dhasa_lord,dhasa_duration = dhasa_progression[d]
        bhukthi_duration = round(dhasa_duration/dhasa_len,2)
        for b in range(dhasa_len):
            bhukthi_lord = dhasa_progression[(d+b)%dhasa_len][0]
            print(dhasa_lord,bhukthi_lord,bhukthi_duration)
    exit()
    """
    from hora.tests import pvr_tests
    pvr_tests.buddha_gathi_test()