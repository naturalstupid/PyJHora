#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    This is an attempt to create horoscope based surya sidhantha meant/true position calculations
    Reference: Indian Astronomy - An Introduction - S. Balachandra Rao
    WORK STILL IN PROGRESS - NOT WORKING FOR SOME PLANETS YET
"""
import math
from hora import utils, const
from hora.panchanga import drik1 as drik
import swisseph as swe
from hora.horoscope.chart import charts

sind = lambda x : math.sin(math.radians(x)) 
cosd = lambda x : math.cos(math.radians(x))
to_dms = lambda x: utils.to_dms(x,is_lat_long='plong')
ahargana_khanda_khaadyaka = lambda jd: jd - 1964031
#ahargana_graha_laghavam = lambda jd: jd - 1687850
mandaphala_of_sun = 0.0
def kali_ahargana(jd):
    """ TODO: CHECK: Should this be int or float? """
    kad = (jd - 588466)  # Or this should be 588466?
    wday = int(kad) % 7
    wdayjd = drik.vaara(jd)
    winc = (wdayjd - 5 - wday)
    wdayc = (wday + winc + 5) % 7
    assert wdayc==wdayjd
    return kad+winc
def _mean_solar_longitude(jd):
    mean_daily_motion_sun_at_kali = const.mean_revolutions_sun_kali / const.civil_days_in_mahayuga * 360
    kan = kali_ahargana(jd)
    mean_longitude_sun = (kan * mean_daily_motion_sun_at_kali) %360
    return mean_longitude_sun,utils.to_dms(mean_longitude_sun,is_lat_long='plong')
def _mean_lunar_longitude(jd):
    mean_daily_motion_moon_at_kali = const.mean_revolutions_moon_kali / const.civil_days_in_mahayuga * 360
    kan = kali_ahargana(jd)
    mean_longitude_moon = (kan * mean_daily_motion_moon_at_kali) %360
    return mean_longitude_moon,utils.to_dms(mean_longitude_moon,is_lat_long='plong')
def _mean_lunar_apogee_longitude(jd):
    mean_daily_motion_moon_apogee = const.madocca_revolutions[const._MOON] / const.civil_days_in_mahayuga * 360
    kan = kali_ahargana(jd)
    mean_longitude_moon_apogee = (kan * mean_daily_motion_moon_apogee) %360 + const.manodcca_positions_at_kali[const._MOON]
    return mean_longitude_moon_apogee,utils.to_dms(mean_longitude_moon_apogee,is_lat_long='plong')
def _mean_rahu_longitude(jd):
    mean_daily_motion_rahu_at_kali = const.mean_revolutions_rahu_kali / const.civil_days_in_mahayuga * 360
    kan = kali_ahargana(jd)
    mean_longitude_rahu = 180.0 - (kan * mean_daily_motion_rahu_at_kali) %360
    return mean_longitude_rahu,utils.to_dms(mean_longitude_rahu,is_lat_long='plong')
def _mean_ketu_longitude(jd):
    mean_longitude_ketu = (180.0 + _mean_rahu_longitude(jd)[0]) % 360 
    return mean_longitude_ketu,utils.to_dms(mean_longitude_ketu,is_lat_long='plong')
def _planet_mean_longitude(jd, place,planet):
    """ TODO: Mars not matching close to Drik """
    """ RESET Planet's mean longitude"""
    p_id = drik.planet_list.index(planet)
    const.planet_mean_longitudes[planet] = 0.0 
    mean_revolutions = const.planet_mean_revolutions_at_kali[planet]
    mean_daily_motion = mean_revolutions / const.civil_days_in_mahayuga * 360 #const.daily_mean_motions[planet] #
    kan = kali_ahargana(jd)
    mean_longitude = ((kan * mean_daily_motion) + 360) %360
    #print('planet,kan,mean_revolutions,mean_daily_motion,mean_longitude',p_id,kan,mean_revolutions,
    #      mean_daily_motion,const.daily_mean_motions[planet],mean_longitude,utils.to_dms(mean_longitude,is_lat_long='plong'))
    if planet in [const._RAHU, const._KETU]:
        mean_longitude = 180.0 - mean_longitude
    if planet == const._KETU:
        mean_longitude = (180.0 + mean_longitude) % 360
    #print('mean long',kan,planet,mean_daily_motion,mean_revolutions,mean_longitude)
    """ Apply Corrections """
    dc = _desantara_correction(place, planet)
    corrected_long = (mean_longitude+dc+360.0)%360
    #print(p_id,'mean longitude after DC',corrected_long,utils.to_dms(corrected_long,is_lat_long='plong')) 
    const.planet_mean_longitudes[planet] = corrected_long   
    return corrected_long
def _desantara_correction(place:drik.Place,planet):
    p_id = drik.planet_list.index(planet)
    planet_daily_motion = const.daily_mean_motions[planet]
    plong = place.longitude
    ulong = const.ujjain_lat_long[1]
    dc = (ulong - plong)/360.0 * planet_daily_motion
    #print('dc',p_id,dc,utils.to_dms(dc,is_lat_long='plong'))
    return dc
def bhujantara_correction(planet,mandaphala_of_sun):
    """ TODO: To use Planet's true motion """
    p_id = drik.planet_list.index(planet)
    bc = const.daily_mean_motions[planet]*mandaphala_of_sun/360
    #print(p_id,'bhujantara_correction',mandaphala_of_sun*60,const.daily_mean_motions[planet]*60,bc,utils.to_dms(bc,is_lat_long='plong'))
    return bc
def ascendant_new(jd, place:drik.Place, sun_long):
    """ TODO NOT WORKING STILL UNDER TESTING """
    _,lat,_,_ = place
    R = 3438
    eps = math.radians(24.0)
    def _delination(lat): # radians
        delination = [11.733998794908114, 20.624646006223887, 24.0]
        td = [R/6* math.tan(math.radians(lat))* math.tan(math.radians(d)) for d in delination]
        td = [-td[0]] + [-(y-x) for x,y in zip(td,td[1:])]
        td1 = td.copy()
        td1.reverse()
        td += [-d1 for d1 in td1]
        td2 = td.copy()
        td2.reverse()
        td += [d1 for d1 in td2]
        return td
    td = _delination(lat)
    lanka_rising_durations = [278,299,323,323,299,278,278,299,323,323,299,278]
    place_rising_durations = [d1+d2 for d1,d2 in zip(lanka_rising_durations,td)]
    sun_rise = drik.sunrise(jd, place)
    jd_sunrise = sun_rise[-1]
    y, m, d,_  = utils.jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(drik.Date(y, m, d))
    print(jd,jd_sunrise,sun_rise[1],jd_utc)
    time_from_sunrise_vinadi = (jd-jd_sunrise)*24/2.5*60
    sun_long_rem = sun_long % 30
    sun_long_rem_vinadi = sun_long_rem * 60.0
    sun_long_raasi = int(sun_long/30)
    print('sun_long',sun_long,'sun_long_raasi',sun_long_raasi,'sun_long_rem',sun_long_rem)
    place_rising = place_rising_durations[sun_long_raasi]*sun_long_rem_vinadi/(30*60)
    print('time_from_sunrise_vinadi',time_from_sunrise_vinadi,'sun_long_rem_vinadi',sun_long_rem_vinadi,'place_rising',place_rising)
    residue = time_from_sunrise_vinadi-place_rising
    print('residue',residue)
    asc_long = residue/place_rising_durations[(sun_long_raasi+1)%12]*30
    print('asc_long',asc_long)
    return int(asc_long/30),asc_long%30
def ascendant(jd, place:drik.Place, sun_long):
    """ TODO: ASC calculations not matching with Drik """
    import math
    _,lat,long,_ = place
    R = 3438
    eps = math.radians(24.0)
    def _delination(lat): # radians
        delination = [11.733998794908114, 20.624646006223887, 24.0]
        td = [R/6* math.tan(math.radians(lat))* math.tan(math.radians(d)) for d in delination]
        td = [-td[0]] + [-(y-x) for x,y in zip(td,td[1:])]
        td1 = td.copy()
        td1.reverse()
        td += [-d1 for d1 in td1]
        td2 = td.copy()
        td2.reverse()
        td += [d1 for d1 in td2]
        return td
    td = _delination(lat)
    lanka_rising_durations = [278,299,323,323,299,278,278,299,323,323,299,278]
    place_rising_durations = [d1+d2 for d1,d2 in zip(lanka_rising_durations,td)]
    #print(lanka_rising_durations)
    #print(td)
    #print(place_rising_durations)
    sun_long_rem = sun_long % 30
    sun_long_rem_vinadi = sun_long_rem * 60.0
    sun_long_raasi = int(sun_long/30)
    place_rising = place_rising_durations[sun_long_raasi]*sun_long_rem_vinadi/(30*60)
    srt = utils.from_dms_str_to_dms(drik.sunrise(jd, place)[1])
    ud = drik.udhayadhi_nazhikai((10,34,0), srt)[1]
    asc_long = (ud * 60. - sun_long_rem_vinadi)/place_rising_durations[sun_long_raasi]*30.0
    asc_rasi = int(asc_long / 30)
    asc_coordinates = asc_long % 30 
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SIDEREAL
        drik.set_ayanamsa_mode(drik._ayanamsa_mode,drik._ayanamsa_value,jd) # needed for swe.houses_ex()
    nak_no,paadha_no,_ = drik.nakshatra_pada(asc_long)
    return [const._ascendant_symbol,[asc_rasi,asc_coordinates]]#,nak_no,paadha_no]
def _mandaphala_planet_new(jd,planet):
    """ Mandaphala using just periphery and mandocca """
    pass
def _mandaphala_planet(jd,planet,planet_mean_long):
    p_id = drik.planet_list.index(planet)
    if planet in [const._RAHU, const._KETU]:
        return 0.0
    kan = kali_ahargana(jd)
    mandocca_mean_revolutions = const.madocca_revolutions[planet]
    planet_mandocca_at_kali = const.manodcca_positions_at_kali[planet]
    mandocca_motion = (kan / (const.civil_days_in_mahayuga) * mandocca_mean_revolutions*360) %360 # Degrees
    #print(p_id,'kan,mandocca_motion',kan,mandocca_mean_revolutions,mandocca_motion,utils.to_dms(mandocca_motion,is_lat_long='plong'))
    planet_mandocca = planet_mandocca_at_kali + mandocca_motion
    #print(p_id,'planet_mandocca_at_kali,mandocca_motion,planet_mandocca',planet_mandocca_at_kali,mandocca_motion,planet_mandocca)
    planet_mandocca_anomaly = (planet_mandocca + 360.0 - planet_mean_long) %360 
    #print(p_id,'planet_mandocca',utils.to_dms(planet_mandocca,is_lat_long='plong'))
    #print(p_id,'planet mean long, planet_anomaly',utils.to_dms(planet_mean_long,is_lat_long='plong'),utils.to_dms(planet_mandocca_anomaly,is_lat_long='plong'))
    planet_mean_motion = const.daily_mean_motions[planet] 
    mandakendra = (planet_mandocca - planet_mean_long + 360 ) % 360
    #print(p_id,'mandakendra',utils.to_dms(mandakendra,is_lat_long='plong'))
    mandakendra_sign = 1.0
    if mandakendra > 180.0:
        mandakendra_sign = -1.0
    " Mandaphala - Equarion of Center"
    if planet in [const._SUN, const._MOON]:
        planet_mandaphala_periphery = const.planet_mandaphala_periphery[planet]
        corrected_periphery = planet_mandaphala_periphery - (1.0/3.0)*abs(sind(mandakendra))
        #Po,Pe = const.planet_mandaphala_periphery[planet]
        #corrected_periphery = Pe - (Pe-Po) * abs(sind(mandakendra))
        if planet == const._MOON:
            #print(p_id,'planet_mean_motion before',planet_mean_motion)
            planet_mean_motion = planet_mean_motion - const.moon_apogee_mean_motion
            #print(p_id,'planet_mean_motion after',planet_mean_motion)
        #print(p_id,'corrected_periphery',corrected_periphery)
        rectified_periphery = (const.mandakendrajya_indian_sine_radius/360.0) * corrected_periphery
        #print(p_id,'rectified_periphery',rectified_periphery) 
        tab_sine_diff = abs(225*0.991335735*cosd(1.024764846*(180.0-planet_mandocca_anomaly-3.75)))
        #print(p_id,'tab_sine_diff',tab_sine_diff)
        " You should use true motion here"
        planet_true_motion_correction = corrected_periphery*planet_mean_motion*tab_sine_diff/(360*225)
        planet_true_motion = planet_mean_motion + mandakendra_sign * planet_true_motion_correction
        #print(p_id,'planet_true_motion',planet_mean_motion,planet_true_motion_correction,corrected_periphery,tab_sine_diff,utils.to_dms(planet_true_motion,is_lat_long='plong')) 
        mandaphala_correction = mandakendra_sign * rectified_periphery*sind(mandakendra)
    else:
        Po,Pe = const.planet_mandaphala_periphery[planet]
        corrected_periphery = Pe - (Pe-Po) * abs(sind(mandakendra))
        #print(p_id,'corrected_periphery',Po,Pe,corrected_periphery)
        mandaphala_correction = const.mandakendrajya_indian_sine_radius/360.0 * corrected_periphery * sind(mandakendra)
    """ TODO Check sine inverse is required for MPH """
    #mandaphala_correction = math.asin(mandaphala_correction*math.pi/180.0)
    #print(p_id,'mandaphala_correction',mandaphala_correction)
    return mandaphala_correction
def _true_longitude_after_sighra_correction(jd,place,planet,planet_mean_long,mandaphala_correction):
    p_id = drik.planet_list.index(planet)
    MP = planet_mean_long
    if planet in [const._SUN, const._MOON, const._RAHU, const._KETU]:
        return 0.0
    ME1 = mandaphala_correction
    def _get_sighra_correction(jd,planet,planet_mean_long):
        p_id = drik.planet_list.index(planet)
        if const.planet_mean_longitudes[const._SUN]==0.0:
            const.planet_mean_longitudes[const._SUN] = _mean_solar_longitude(jd)[0] #_planet_mean_longitude(jd, place, const._SUN)
        if planet in [const._MERCURY, const._VENUS]:
            m = (planet_mean_long - const.planet_mean_longitudes[const._SUN]+360)%360
            #print(p_id,'Sighra anomaly = Planets sighrocca - mean sun',to_dms(planet_mean_long),'-',to_dms(const.planet_mean_longitudes[const._SUN]),'=',to_dms(m))                  
        else:
            m = (const.planet_mean_longitudes[const._SUN] - planet_mean_long+360)%360 #const.planet_mean_longitudes[planet]+360)%360
            #print(p_id,'Sighra anomaly = Mean sun - mean planet',to_dms(const.planet_mean_longitudes[const._SUN]),'-', to_dms(const.planet_mean_longitudes[planet]),'=',to_dms(m))
        sign = 1.0
        if m > 90. and m < 270.0:
            sign = -1.0
        """ Calculate corrected sighra periphery """
        Po,Pe = const.planet_sighra_peripheries[planet]
        P = Pe - (Pe-Po) * abs(sind(m))
        r = P/360.0
        R = const.mandakendrajya_indian_sine_radius * 60.0
        #print(p_id,'Po,Pe,P,r,sighra anomaly(m)',to_dms(Po),to_dms(Pe),to_dms(P),r,to_dms(m))
        dohphala = r * R * sind(m)
        kotiphala = r * R * cosd(m)
        sphutakoti = R + kotiphala
        sighrakarna = math.sqrt(sphutakoti*sphutakoti+dohphala*dohphala)
        rsinsighraphala = dohphala*R/sighrakarna
        #print(p_id,'dohphala,kotiphala,sphutakoti,sighrakarna,rsinsighraphala',dohphala,kotiphala,sphutakoti,sighrakarna,rsinsighraphala)
        sighraphala = math.asin(rsinsighraphala/R)*180.0/math.pi
        #print(p_id,'sighraphala',to_dms(sighraphala))
        return sighraphala
    SE1 = _get_sighra_correction(jd,planet,MP)
    P1 = MP + 0.5 * SE1
    #print(p_id,'first step _get_sighra_correction','MP,SE1,P1',MP,SE1,P1)
    P2 = P1 + 0.5 * ME1
    #print(p_id,'2nd step','P1,ME1,P2',P1,ME1,P2)
    ME2 = _mandaphala_planet(jd,planet, P2)
    P3 = MP + ME2
    const.planet_mean_longitudes[planet] = P3
    #print(p_id,'3rd step _mandaphala_planet','MP,ME2,P3',MP,ME2,P3)
    SE2 = _get_sighra_correction(jd,planet,P3)
    P4 = P3 + SE2
    #print(p_id,'4th step _get_sighra_correction','P3,SE2,P4',P3,SE2,P4)
    return P4
def _planet_true_longitude(jd,place,planet,planet_mean_long):
    p_id = drik.planet_list.index(planet)
    if planet in [const._RAHU, const._KETU]:
        return planet_mean_long
    """ Correction for Equation of Center aka Mandaphala """
    mandaphala = _mandaphala_planet(jd,planet,planet_mean_long)
    if planet == const._SUN:
        global mandaphala_of_sun
        mandaphala_of_sun = mandaphala
    #print(p_id,'mandaphala',mandaphala,utils.to_dms(mandaphala,is_lat_long='plong'))
    mandaphala_corrected_longitude = planet_mean_long + mandaphala
    #print(p_id,'_planet_true_longitude',planet_mean_long,mandaphala_of_sun,mandaphala_corrected_longitude,utils.to_dms(mandaphala_corrected_longitude,is_lat_long='plong'))
    bcs = bhujantara_correction(planet, mandaphala_of_sun)
    mandaphala_corrected_longitude += bcs
    true_longitude = (mandaphala_corrected_longitude+360)%360
    if planet in [const._SUN, const._MOON, const._RAHU, const._KETU]: 
        return true_longitude
    else:
        true_longitude = (_true_longitude_after_sighra_correction(jd,place,planet,planet_mean_long,mandaphala)+360)%360
        return true_longitude
def planet_positions(jd,place:drik.Place):
    planet_positions_ss = []
    #planet_corrections = [0,90.0,0,-120.0,0,-180,0,0,0]
    #drik.set_ayanamsa_mode('SURYASIDDHANTA', ayanamsa_value=None, jd=jd)
    #ss_ayanamsa = drik.get_ayanamsa_value(jd)
    #print('SS Ayanamsa',ss_ayanamsa)
    planet_corrections = [0,0.0,0,0.0,0,0,0,0,0] # [x-ss_ayanamsa for x in [0,0.0,0,0.0,0,0,0,0,0]]
    for planet in drik.planet_list: #[const._SUN,const._MOON,const._SATURN]:#
        p_id = drik.planet_list.index(planet)
        mean_long = _planet_mean_longitude(jd,place,planet)
        #print(p_id,'mean longitude',planet,mean_long,utils.to_dms(mean_long, is_lat_long='plong'))
        corrected_long = (_planet_true_longitude(jd,place,planet, mean_long)+planet_corrections[p_id])%360.
        planet_positions_ss.append([p_id,[int(corrected_long/30),corrected_long%30]]    )
        #print(p_id,'true longitude',planet,corrected_long,utils.to_dms(corrected_long, is_lat_long='plong'))
    # Calculate ascendant and add to planet positions
    #asc = drik.ascendant(jd, place)
    sun_long = planet_positions_ss[0][1][0]*30+planet_positions_ss[0][1][1]
    asc = ascendant_new(jd, place, sun_long)
    planet_positions_ss = [[const._ascendant_symbol,[asc[0],asc[1]]]] + planet_positions_ss
    return planet_positions_ss
def _lunar_evection(sun_mean_longitude, moon_mean_longitude):
    pass
if __name__ == "__main__":
    place = drik.Place('Ujjain',23.1765, 75.7885,5.5)
    #place = drik.Place('Durham',35.994, -78.8986,-4.0)
    place = drik.Place('Royapuram',13.1,80.2833,5.5)
    dt = drik.Date(-3101,1,22) #1991,3,22)
    dt = drik.Date(1995,1,11)
    #dt = drik.Date(2023,4,25)
    jd = swe.julday(dt[0],dt[1],dt[2],23.43)
    jd = swe.julday(dt[0],dt[1],dt[2],15+50/60.+37/3600.)
    #"""
    loc = utils.get_place_from_user_ip_address()
    place = drik.Place(loc[0],loc[1],loc[2],loc[3])
    from _datetime import datetime,time,date
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    print(current_date_str,current_time_str)
    dt = current_date_str.split(",")
    dob = tuple(map(int,dt))
    dt1 = current_time_str.split(':')
    tob = tuple(map(int,dt1))
    print('date',dob,'time',tob,utils.julian_day_number(dob, (6,46,30)))
    #jd = swe.julday(int(dt[0]),int(dt[1]),int(dt[2]),int(dt1[0])+int(dt1[1])/60.0+int(dt1[2])/3600.0)
    jd = utils.julian_day_number(dob, tob)
    #"""
    planet_positions_ss = planet_positions(jd,place)
    sun_long = planet_positions_ss[1][1][0]*30+planet_positions_ss[1][1][1]
    print(ascendant_new(jd, place, sun_long))
    print(planet_positions_ss)
    planet_positions_drik = charts.rasi_chart(jd, place)
    print(planet_positions_drik)
    for p in range(len(planet_positions_ss)):
        p_long_ss = planet_positions_ss[p][1][0]*30+planet_positions_ss[p][1][1]
        p_long_drik = planet_positions_drik[p][1][0]*30+planet_positions_drik[p][1][1]
        p_diff = abs(p_long_drik-p_long_ss)
        print(planet_positions_drik[p][0],'drik-posn',p_long_drik,'ss-posn',p_long_ss,'diff',p_diff)
    sun_long = planet_positions_ss[1][1][0]*30+planet_positions_ss[1][1][1]
    print(sun_long,ascendant_new(jd, place, sun_long), drik.ascendant(jd, place))