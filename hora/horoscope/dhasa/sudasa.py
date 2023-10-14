from hora import const,utils
from hora.panchanga import drik
from hora.horoscope.chart import house
from hora.horoscope.dhasa import narayana
from hora import utils
from hora.horoscope.chart import charts
import swisseph as swe
import datetime
def sudasa_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1):
    from hora.panchanga import drik
    jd = utils.julian_day_number(dob, tob)
    sl = drik.sree_lagna(jd, place, divisional_chart_factor)
    sree_lagna_house = sl[0]
    sree_lagna_longitude = sl[0]*30+sl[1]
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    return sudasa_dhasa_from_chart(chart,sree_lagna_house,sree_lagna_longitude,dob)
def sudasa_dhasa_from_chart(chart,sree_lagna_house,sree_lagna_longitude,dob):
    """
        calculate Sudasa Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param sree_lagna_house:Raasi index where sree lagna is
        @param sree_lagna_longitude: Longitude of Sree Lagna 
            Note: one can get sree lagna information from drik.sree_lagna()
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    #print('sree_lagna_house,sree_lagna_longitude',sree_lagna_house,sree_lagna_longitude)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    direction = 1
    if sree_lagna_house in const.even_signs:
        direction = -1
    ks = sum(house.kendras()[:3],[])
    #print('ks',ks)
    dhasa_progression = [(sree_lagna_house+direction*(k-1))%12 for k in ks]
    #print(dhasa_progression)
    dhasa_periods = []
    #dhasa_start = dob_year
    dhasa_start = datetime.date(dob_year,dob_month,dob_day)
    dhasa_start_remaining = round((30.0 - (sree_lagna_longitude % 30))/30.0,2)
    dhasa_end = dhasa_start+datetime.timedelta(days=dhasa_start_remaining)
    for s,sign in enumerate(dhasa_progression):
        dhasa_duration = narayana._dhasa_duration(p_to_h,sign)
        if s==0:
            dhasa_duration *= dhasa_start_remaining
        dhasa_duration_in_days = round(dhasa_duration*const.sidereal_year)
        dhasa_end = dhasa_start+datetime.timedelta(days=dhasa_duration_in_days)
        andtardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = ''#-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        dhasa_start = dhasa_end
    # Second cycle
    dhasa_start = dhasa_end
    total_dhasa_duration = sum([row[-1] for row in dhasa_periods ])
    for c,sign in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_periods[c][-1]
        dhasa_duration_in_days = round(dhasa_duration*const.sidereal_year)
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            #dhasa_duration = 12
            continue
        dhasa_end = dhasa_start+datetime.timedelta(days=dhasa_duration_in_days)
        #print(sign,_narayana_antardhasa(sign))
        andtardhasa = _antardhasa(sign,p_to_h)#)+' '+str(dhasa_duration)+' months each'
        dhasa_period_suffix = ''#-'+str(dob_month)+'-'+str(dob_day)
        dhasa_periods.append([sign,str(dhasa_start)+dhasa_period_suffix,str(dhasa_end)+dhasa_period_suffix,andtardhasa,dhasa_duration])
        dhasa_start = dhasa_end
        #print('total_dhasa_duration',total_dhasa_duration,dhasa_end)
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_periods
def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from hora.tests.pvr_tests import test_example
    chapter = 'Chapter 20 Sudasa tests '
    exercise ='Example 77 / Chart 3 ' 
    # Chart 3 chart of Vajpayee
    chart_3 = ['2','','7','','1','','','3/L/6','5/0/8','','4','']
    #print('sudasa_dhasa_tests','chart_3',chart_3)
    sree_lagna_house = 9
    sree_lagna_longitude = 282+21.0/60
    dob = (1926,12,25)
    #Ans: Cp:1.18,Li:2,Cn:11,Ar:12,Sg:2,Vi:10,Ge:5,Pi:1,Sc:2,Le:8,Ta:7,Aq:3
    expected_result = [(9,1.18),(6,2),(3,11),(0,12),(8,2),(5,10),(2,5),(11,1),(7,1),(4,8),(1,7),(10,3)]
    #SL is at 12°21' in Capricorn. The fraction of the first dasa left at birth = (30° – 12°21'/30° = (1800 – 741)/1800*2 = 1.18
    sd = sudasa_dhasa_from_chart(chart_3,sree_lagna_house, sree_lagna_longitude, dob)
    print(sd)    
    for pe,p in enumerate(sd[:len(expected_result)]):
        test_example(chapter+exercise,expected_result[pe],(p[0],p[-1]),house.rasi_names_en[p[0]],'Dhasa duration',p[-1],'years')   
