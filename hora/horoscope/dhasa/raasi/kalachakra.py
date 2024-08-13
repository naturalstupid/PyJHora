import numpy as np
from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import house
def _get_dhasa_progression(lunar_longitude):
    nakshatra,paadham,_ = drik.nakshatra_pada(lunar_longitude)
    nakshatra -= 1
    paadham -= 1
    dhasa_progression = []
    kalachakra_index = 0
    if nakshatra in const.savya_stars_1:
        #print('savya_stars_1')
        kalachakra_index = 0
    elif nakshatra in const.savya_stars_2:
        #print('savya_stars_2')
        kalachakra_index = 1
    elif nakshatra in const.apasavya_stars_1:
        #print('apasavya_stars_1')
        kalachakra_index = 2
    else:
        #print('apasavya_stars_2')
        kalachakra_index = 3
    nak_index = const.kalachakra_stars[kalachakra_index].index(nakshatra)
    dhasa_progression = const.kalachakra_rasis[kalachakra_index][paadham]
    dhasa_paramayush = const.kalachakra_paramayush[kalachakra_index][paadham]
    dhasa_duration = [const.kalachakra_dhasa_duration[r] for r in dhasa_progression]
    #print('nakshatra',nakshatra,'paadham',paadham,'kalachakra_index',kalachakra_index)
    one_star = (360.0/27)
    one_paadha = (360.0 / 108)
    nak_start_long = nakshatra*one_star + paadham * one_paadha
    nak_end_long = nak_start_long + one_paadha
    nak_travel_fraction = (lunar_longitude-nak_start_long)/one_paadha
    dhasa_duration_cumulative = np.cumsum(dhasa_duration)
    paramayush_completed = nak_travel_fraction * dhasa_paramayush
    dhasa_index_at_birth = next(x[0] for x in enumerate(dhasa_duration_cumulative) if x[1] > paramayush_completed)
    dhasa_remaining_at_birth = dhasa_duration_cumulative[dhasa_index_at_birth]-paramayush_completed
    #print(nakshatra,paadham,nak_start_long,nak_end_long,nak_travel_fraction)
    #print(dhasa_progression,dhasa_duration,dhasa_duration_cumulative,dhasa_paramayush,paramayush_completed,dhasa_index_at_birth,dhasa_remaining_at_birth)
    kalachakra_index_next = kalachakra_index
    paadham_next = (paadham+1)%4
    if paadham==3:
        if kalachakra_index == 0:
            kalachakra_index_next = 1
        elif kalachakra_index == 1:
            kalachakra_index_next = 0
        elif kalachakra_index == 2:
            kalachakra_index_next = 3
        elif kalachakra_index == 3:
            kalachakra_index_next = 2
    dhasa_progression = dhasa_progression[dhasa_index_at_birth:]+const.kalachakra_rasis[kalachakra_index_next][paadham_next][:dhasa_index_at_birth]
    dhasa_duration = [const.kalachakra_dhasa_duration[r] for r in dhasa_progression]
    dhasa_duration[0] = dhasa_remaining_at_birth
    dp_begin = kalachakra_index_next*9*4+paadham*9+dhasa_index_at_birth
    #print('kalachakra_index_next',kalachakra_index_next,'paadham',paadham,'dhasa_index_at_birth',dhasa_index_at_birth)
    #print('dp_begin,kalachakra_rasis_list[dp_begin],dhasa_progression[0]',dp_begin,kalachakra_rasis_list[dp_begin:dp_begin+9],dhasa_progression[0])
    dhasa_periods = []
    for i,dp in enumerate(dhasa_progression):
        ad = antardhasa(dhasa_index_at_birth,i, dhasa_paramayush, kalachakra_index_next, paadham)
        dhasa_periods.append([dp,ad,dhasa_duration[i]])
    return dhasa_periods#dhasa_progression,dhasa_duration,ad,dhasa_paramayush
def antardhasa(dhasa_index_at_birth,dp_index,paramayush,kc_index,paadham):
    #print('dhasa_index_at_birth,dp_index,paramayush,kc_index,paadham',dhasa_index_at_birth,dp_index,paramayush,kc_index,paadham)
    dp_begin = kc_index*9*4+paadham*9+dhasa_index_at_birth+dp_index
    #print('dp_begin:dp_begin+9',dp_begin,':',dp_begin+9)
    antardhasa_progression=const.kalachakra_rasis_list[dp_begin:dp_begin+9]
    #print('antardhasa_progression',antardhasa_progression)
    antardhasa_duration = [const.kalachakra_dhasa_duration[r] for r in antardhasa_progression]
    """ TODO: handle if above is empty list [] """
    if len(antardhasa_duration)==0:
        return []
    #print('antardhasa_duration',antardhasa_duration)
    dhasa_duration = antardhasa_duration[0]
    antardhasa_fraction = dhasa_duration/sum(antardhasa_duration)
    antardhasa_duration = [round((ad * antardhasa_fraction),2) for ad in antardhasa_duration]
    #print('antardhasa_progression',antardhasa_progression,antardhasa_duration)
    #print('sum of antardhasa_duration',sum(antardhasa_duration),dhasa_duration)
    return [antardhasa_progression,antardhasa_duration]
def kalachakra_dhasa(lunar_longitude,dob):
    """
        Kalachara Dhasa calculation
        @param lunar_longitude: Longitude of moon at the time of Date/time of birth as float
            Note: one can get this from drik.lunar_longitude()
        @param dob: Date of birth as tuple (year,month,day)
        @return: list of [dhasa_rasi,dhasa_rasi_start_date, dhasa_rasi_end_date,[abtadhasa_rasis],dhasa_rasi_duration]
        Example: [[7, '1946-12-2', '1955-12-2', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 9], [8, '1955-12-2', '1964-12-2', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 9], ...]
    """
    dhasa_periods = _get_dhasa_progression(lunar_longitude)
    #print('dhasa periods',dhasa_periods)
    if len(dhasa_periods)==0:
        return []
    #"""
    dob_year = dob[0]
    dob_month = dob[1]
    dob_day = dob[2]
    import datetime
    #dhasa_start = datetime.date(dob_year,dob_month,dob_day)
    dhasa_start = drik.Date(dob_year,dob_month,dob_day)
    dp_new = []
    for dp in dhasa_periods:
        #ds,[ads,add],dd = dp
        ds,ad,dd = dp
        dhasa_duration_in_days = round(dd*const.sidereal_year)
        #dhasa_end = dhasa_start+datetime.timedelta(days=dhasa_duration_in_days)
        dhasa_end = utils.next_panchanga_day(dhasa_start, add_days=dhasa_duration_in_days)
        #dp_new.append([ds,str(dhasa_start),str(dhasa_end),[ads,add],dd])
        dp_new.append([ds,str(dhasa_start),str(dhasa_end),ad,dd])
        dhasa_start = dhasa_end
    #"""    
    dhasa_periods = dp_new[:]
    return dhasa_periods
    #dhasa_progression,dhasa_duration,ad,dhasa_paramayush = _get_dhasa_progression(lunar_longitude)
    #return dhasa_progression,dhasa_duration,ad,dhasa_paramayush
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.kalachakra_dhasa_tests()
