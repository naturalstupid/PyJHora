from hora import const,utils
from hora.panchanga import panchanga
from hora.horoscope.chart import house
from hora.horoscope.dhasa import narayana
import swisseph as swe
import datetime
def sudasa_dhasa(chart,sree_lagna_house,sree_lagna_longitude,dob):
    """
        calculate Sudasa Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param sree_lagna_house:Raasi index where sree lagna is
        @param sree_lagna_longitude: Longitude of Sree Lagna 
            Note: one can get sree lagna information from panchanga.sree_lagna()
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    h_to_p = chart[:]
    print('sree_lagna_house,sree_lagna_longitude',sree_lagna_house,sree_lagna_longitude)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    print(p_to_h)
    direction = 1
    if sree_lagna_house in const.even_signs:
        direction = -1
    ks = sum(house.kendras()[:3],[])
    print('ks',ks)
    dhasa_progression = [(sree_lagna_house+direction*(k-1))%12 for k in ks]
    print(dhasa_progression)
    dhasa_periods = []
    #dhasa_start = dob_year
    dhasa_start = datetime.date(dob_year,dob_month,dob_day)
    dhasa_start_remaining = round((30.0 - (sree_lagna_longitude % 30))/30.0,2)
    dhasa_end = dhasa_start+datetime.timedelta(days=dhasa_start_remaining)
    """ TODO: Determine Dhasa Start and End based on dhasa_start_remaining """
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
    pass