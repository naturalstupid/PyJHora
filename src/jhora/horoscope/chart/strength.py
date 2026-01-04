#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" To Calculate strengths of planets/rasis from chart positions of planets """
""" Ref: https://www.scribd.com/document/426763000/Shadbala-and-Bhavabala-Calculation-pdf """
""" Ref: https://medium.com/thoughts-on-jyotish/shadbala-the-6-sources-of-strength-4c5befc0c59a """
from jhora import const,utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house

######################### Chesta bala constants start here #############################
_DOB_EPOCH = (1900,1,1); _TOB_EPOCH = (0,0,0); _PLACE_EPOCH = drik.Place('Ujjain,India',23.18,76,5.5)
_EPOCH_YEAR = 1900
_JD_EPOCH = utils.julian_day_number(_DOB_EPOCH, _TOB_EPOCH)
_DAYS_FROM_EPOCH = lambda jd,place: jd - _JD_EPOCH + (_PLACE_EPOCH.longitude-place.longitude)/15/24
is_leap_year = lambda year: (((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0))
leap_count_between_years = lambda start,end,include_both=False: \
    [is_leap_year(year) for year in range(start,end+1)].count(True) if include_both else \
    [is_leap_year(year) for year in range(start+1,end)].count(True)
list_of_leap_years_between_years = lambda start,end,include_both=False: \
    [year for year in range(start,end+1) if is_leap_year(year)] if include_both else \
    [year for year in range(start+1,end) if is_leap_year(year)]
planet_mean_positions_at_epoch_ujjain_1900 = [257.4568,-1,270.22,164,220.04,328.51,236.74]
planet_speed_at_epoch_ujjain_1900 = [0.9856,-1,0.524,4.0923,0.0831,1.60215,0.033439]
planet_correction_factors_per_year_since_epoch = [(1,0,0),(1,0,0),(1,0,0),(1,6.67,-0.00133),(-1,3.3,0.0067),(-1,5,0.0001),(1,5,0.001)]
planet_longitude_correction = lambda planet_index,years_since_epoch: \
    planet_correction_factors_per_year_since_epoch[planet_index][0]* \
    (planet_correction_factors_per_year_since_epoch[planet_index][1]+ \
     planet_correction_factors_per_year_since_epoch[planet_index][2]*years_since_epoch)
# Ujjain Epoch 1900 Mean Daily Motion Table for the Planets
ujjain_epoch_table_for_planets = [
        { # Sun
            1: [0.9856, 98.5602, 265.6026, 136.0265],
            2: [1.9712, 197.1205, 171.2053, 272.0531],
            3: [2.9568, 295.6808, 76.8080, 48.0796],
            4: [3.9424, 34.2411, 342.4106, 184.1062],
            5: [4.9280, 132.8013, 248.0133, 320.1327],
            6: [5.9136, 231.3616, 153.6159, 96.1593],
            7: [6.8992, 329.9218, 59.2186, 232.1868],
            8: [7.8848, 68.4821, 324.8212, 8.2124],
            9: [8.8704, 167.0424, 230.4239, 144.2389]
        }, 
        { # Moon
            1: [0.9856, 98.5602, 265.6026, 136.0265],
            2: [1.9712, 197.1205, 171.2053, 272.0531],
            3: [2.9568, 295.6808, 76.8080, 48.0796],
            4: [3.9424, 34.2411, 342.4106, 184.1062],
            5: [4.9280, 132.8013, 248.0133, 320.1327],
            6: [5.9136, 231.3616, 153.6159, 96.1593],
            7: [6.8992, 329.9218, 59.2186, 232.1868],
            8: [7.8848, 68.4821, 324.8212, 8.2124],
            9: [8.8704, 167.0424, 230.4239, 11.1442389]
        }, 
        { # Mars
            1: [0.524, 52.40,164.02,200.19],
            2: [1.048, 104.80, 328.04, 40.39],
            3: [1.572, 157.21, 132.06, 240.58],
            4: [2.096, 209.61, 296.08, 80.78],
            5: [2.620, 262.01, 100.10, 280.97],
            6: [3.144, 314.41, 264.12, 121.16],
            7: [3.668, 6.81, 68.14, 321.36],
            8: [4.192, 59.22, 232.15, 161.55],
            9: [4.716, 111.62, 36.17, 1.74]
        }, 
        { # Mercury
            1: [4.09, 40.92, 49.23, 132.32, 243.18],
            2: [8.18, 81.84, 98.46, 264.64, 126.36],
            3: [12.28, 122.77, 147.70, 36.95, 9.54],
            4: [16.37, 163.69, 196.93, 169.27, 252.72],
            5: [20.46, 204.62, 246.16, 301.59, 135.90],
            6: [24.55, 245.54, 295.39, 73.91, 19.08],
            7: [28.65, 286.46, 344.62, 206.23, 262.26],
            8: [32.74, 327.38, 33.85, 338.54, 145.44],
            9: [36.83, 8.31, 83.09, 110.86, 28.63]
        }, 
        { # Jupiter
            1: [0.08,0.83,8.31,83.1,110.96],
            2: [0.17,1.66,16.62,166.19,221.93],
            3: [0.25,2.49,24.93,249.29,332.89],
            4: [0.33,3.32,33.24,332.39,83.85],
            5: [0.41,4.15,41.55,55.48,194.82],
            6: [0.50,4.99,49.86,138.58,305.78],
            7: [0.58,5.82,58.17,221.67,56.74],
            8: [0.66,6.65,66.48,304.77,167.71],
            9: [0.75,7.48,74.79,27.87,278.67]
        },
        { # Venus
            1: [1.60, 16.02, 160.21, 162.15, 181.46],
            2: [3.20, 32.04, 320.43, 324.29, 2.93],
            3: [4.81, 48.06, 120.64, 126.44, 184.39],
            4: [6.41, 64.09, 280.86, 288.59, 5.86],
            5: [8.01, 80.11, 81.07, 90.73, 187.32],
            6: [9.61, 96.13, 241.29, 252.88, 8.78],
            7: [11.21, 112.15, 41.50, 55.02, 190.25],
            8: [12.82, 128.17, 201.72, 217.17, 11.71],
            9: [14.42, 144.19, 1.93, 19.32, 193.18]
        },
        { # Saturn
            1: [0.03, 0.33, 3.34, 33.44, 334.39],
            2: [0.07, 0.67, 6.69, 66.88, 308.79],
            3: [0.10, 1.00, 10.03, 100.32, 283.18],
            4: [0.13, 1.34, 13.38, 133.76, 257.57],
            5: [0.17, 1.67, 16.72, 167.20, 231.97],
            6: [0.20, 2.01, 20.06, 200.64, 206.36],
            7: [0.23, 2.34, 23.41, 234.08, 180.75],
            8: [0.27, 2.68, 26.75, 267.51, 155.14],
            9: [0.30, 3.01, 30.10, 300.95, 129.54]
        },
    ]
######################### Chesta bala constants end here #############################
kendras = lambda asc_house:[(asc_house+h-1)%12 for h in [1,4,7,10] ]
panapharas = lambda asc_house:[(asc_house+h-1)%12 for h in [2,5,8,11] ]
apoklimas = lambda asc_house:[(asc_house+h-1)%12 for h in [3,6,9,12] ]

def harsha_bala(dob,tob,place,divisional_factor=1):
    """
        computes the harsha bala score of the planets
        @param dob: date of solar entry in the annual chart / date of birth in natal chart
        @param tob: time of solar entry in the annual chart / time of birth in natal chart
        @return: Harsha Bala score for each planet - as a list 
            Example: {0: 0, 1: 15, 2: 0, 3: 10, 4: 5, 5: 10, 6: 5} - Sun's score = 0, Venus's score = 10
    """
    jd = utils.julian_day_number(dob, tob)
    sun_rise = drik.sunrise(jd, place)[0]
    sun_set = drik.sunset(jd, place)[0]
    new_year_daytime_start = True
    fh = utils.from_dms(tob[0],tob[1],tob[2])
    if fh < sun_rise or fh > sun_set:
        new_year_daytime_start = False
    planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=divisional_factor)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    asc_house = p_to_h[const._ascendant_symbol]
    harsha_bala = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h[p]
        h_f_a = (p_to_h[p]-asc_house)%12
        " Rule-1 - planets in their harsha bala houses"
        if const.harsha_bala_houses[p] == h_f_a:
            harsha_bala[p] +=5
        " Rule-2 - exhalted planets in their own house "
        if const.house_strengths_of_planets[p][h_p] > const._FRIEND or h_p in const.house_lords_dict[p]: # Exhalted or Own
            harsha_bala[p]+= 5
        " Rule-3 Feminine"
        if p in const.feminine_planets and h_f_a in const.harsha_bala_feminine_houses:
            harsha_bala[p] += 5
        elif p in const.masculine_planets and h_f_a in const.harsha_bala_masculine_houses:
            harsha_bala[p] += 5
        "Rule-4 "
        if new_year_daytime_start and p in const.masculine_planets:
            harsha_bala[p] += 5
        elif not new_year_daytime_start and p in const.feminine_planets:
            harsha_bala[p] += 5
    return harsha_bala
""" 
    Ref: https://www.scribd.com/document/426763000/Shadbala-and-Bhavabala-Calculation-pdf
"""    
def _kshetra_bala(p_to_h_of_rasi_chart):
    kb = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h_of_rasi_chart[p]
        if const.house_strengths_of_planets[p][h_p] > const._FRIEND:
            kb[p] = 30
        elif const.house_strengths_of_planets[p][h_p] == const._FRIEND:
            kb[p] = 15 #22.5
        elif const.house_strengths_of_planets[p][h_p] == const._ENEMY:#const._DEBILITATED_NEECHAM:
            kb[p] = 7.5
    return kb.values()
def _sapthavargaja_bala(jd,place):
    sv = [1, 2, 3, 7, 9, 12, 30]
    pp_sv = {}
    for dcf in sv:
        pp = charts.divisional_chart(jd, place,divisional_chart_factor=dcf)
        pp_sv[dcf] = pp
    svb = []
    for dcf in sv:
        svbc = _sapthavargaja_bala_1(pp_sv[dcf],dcf)
        svb.append(svbc)
    svb_sum = list(map(sum,zip(*svb)))
    return svb_sum
def _sapthavargaja_bala1(jd,place,ayanamsa_mode='LAHIRI'):
    sv = [1, 2, 3, 7, 9, 12, 30]
    pp_sv = {}
    planet_positions_in_rasi = charts.rasi_chart(jd, place,ayanamsa_mode=ayanamsa_mode)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions_in_rasi)
    cr = house._get_compound_relationships_of_planets(h_to_p)
    for dcf in sv:
        pp = charts.divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=dcf) if dcf!=2 \
                else charts.hora_chart(planet_positions_in_rasi, chart_method=2)
        pp_sv[dcf] = pp
    svb = []
    for dcf in sv:
        svbc = _sapthavargaja_bala_2(pp_sv[dcf],dcf,cr)
        svb.append(svbc)
    svb_sum = list(map(sum,zip(*svb)))
    svb_sum = [round(v,2) for v in svb_sum]
    return svb_sum
def _sthana_bala(jd, place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    sv = [1, 2, 3, 7, 9, 12, 30]
    pp_sv = {}
    for dcf in sv:
        pp = charts.divisional_chart(jd, place,ayanamsa_mode=ayanamsa_mode,divisional_chart_factor=dcf)
        pp_sv[dcf] = pp
    ub = _uchcha_bala(pp_sv[1])
    #print('uccha bala',ub)
    svb = _sapthavargaja_bala1(jd, place,ayanamsa_mode=ayanamsa_mode)
    #print('_sapthavargaja_bala',svb)
    ob = _ojayugama_bala(pp_sv[1], pp_sv[9])
    #print('_ojayugama_bala',ob)
    kb = _kendra_bala(pp_sv[1])
    #print('_kendra_bala',kb)
    db = _dreshkon_bala(pp_sv[1])
    #print('_dreshkon_bala',db)
    sb = list(map(sum,zip(*[ub,svb,ob,kb,db])))
    sb = [round(v,2) for v in sb]
    return sb
def _sapthavargaja_bala_2(planet_positions,dcf,compound_relations):
    sb = [0 for _ in range(8)]
    cr = compound_relations
    sb_fac = {const._ADHISATHRU_GREATENEMY-1:1.875,const._SATHRU_ENEMY-1:3.75,const._SAMAM_NEUTRAL-1:7.5,
              const._MITHRA_FRIEND-1:15,const._ADHIMITRA_GREATFRIEND-1:22.5}
    for p,(h,_) in planet_positions[1:8]:
        owner = const._house_owners_list[h]
        if h == const.moola_trikona_of_planets[p] and dcf==1: # Moola Trinkona Rasi
            sb[p] = 45
            #print('chart-',dcf,'planet',p,'in moola trikona','strength=45')
        elif const.house_strengths_of_planets[p][h]==const._OWNER_RULER: # Swastha Rasi
            sb[p] = 30
            #print('chart-',dcf,'planet',p,'in own rasi','strength=30')
        else:
            sb[p] = sb_fac[cr[p][owner]]
            #print('chart-',dcf,'planet',p,'is in',owner,"'s rasi",'relation=',cr[p][owner],'strength',sb[p])
    return sb
def _sapthavargaja_bala_1(planet_positions,dcf):
    sb = [0 for _ in range(8)]
    #sb_fac = {const._ADHISATHRU_GREATENEMY:4,const._SATHRU_ENEMY:4,const._SAMAM_NEUTRAL:10,const._MITHRA_FRIEND:15,
    #          const._ADHIMITRA_GREATFRIEND:20}
    sb_fac = {const._ADHISATHRU_GREATENEMY:1.875,const._SATHRU_ENEMY:3.75,const._SAMAM_NEUTRAL:7.5,const._MITHRA_FRIEND:15,
              const._ADHIMITRA_GREATFRIEND:22.5}
    for p,(h,_) in planet_positions[1:8]:
        owner = house.house_owner_from_planet_positions(planet_positions, h)
        if h == const.moola_trikona_of_planets[p] and dcf==1: # Moola Trinkona Rasi
            sb[p] = 45
        elif const.house_strengths_of_planets[p][h]==const._OWNER_RULER: # Swastha Rasi
            sb[p] = 30
        else:
            sb[p] = sb_fac[const.compound_planet_relations[p][owner]]
    return sb
def _yugmayugma_bala(rasi_planet_positions, navamsa_planet_positions):
    return _ojayugama_bala(rasi_planet_positions, navamsa_planet_positions)
def _ojayugama_bala(rasi_planet_positions, navamsa_planet_positions):
    sb = [0 for _ in range(7)]
    for p in range(7):
        rh = rasi_planet_positions[p+1][1][0]
        nh = navamsa_planet_positions[p+1][1][0]
        if p in [1,5]:
            if rh in const.even_signs:
                sb[p] = 15
            if nh in const.even_signs:
                sb[p] += 15
        else:
            if rh in const.odd_signs:
                sb[p] = 15
            if nh in const.odd_signs:
                sb[p] += 15
    return sb
def _kendra_bala(rasi_planet_positions):
    kb = [0 for _ in range(7)]
    asc_house = rasi_planet_positions[0][1][0]
    for p,(h,_) in rasi_planet_positions[1:8]: #exclude 0th element Lagnam and Rahu/Ketu
        if h in kendras(asc_house):
            kb[p] = 60
        elif h in panapharas(asc_house):
            kb[p] = 30
        elif h in apoklimas(asc_house):
            kb[p] = 15
    return kb
def _dreshkon_bala(planet_positions):
    kb = [0 for _ in range(7)]
    kbf = [(0,2,4),(3,6),(1,5)]
    for p,(h,long) in planet_positions[1:8]: #exclude 0th element Lagnam and Rahu/Ketu
        pd = int(long//10.0)
        if p in kbf[pd]:
            kb[p] = 15
    return kb
def _uccha_rashmi(planet_positions):
    ub = []
    for p,(h,long) in planet_positions[1:const._pp_count_upto_saturn]: #exclude 0th element Lagnam and Rahu/Ketu
        p_long = h*30+long
        pd = (const.planet_deep_debilitation_longitudes[p]+360 - p_long)%360
        if pd > 180.0:
            pd = 360.0 - pd
        pd += 30
        ub.append(round(pd*2/30,1))
    return ub    
def _uchcha_bala(planet_positions):
    ub = []
    for p,(h,long) in planet_positions[1:const._pp_count_upto_saturn]: #exclude 0th element Lagnam and Rahu/Ketu
        p_long = h*30+long
        pd = (p_long+360 - const.planet_deep_debilitation_longitudes[p])%360
        if pd > 180.0:
            pd = 360.0 - pd
        if const.use_saravali_formula_for_uccha_bala:
            ubv = round(pd/3,2)
            ub.append(ubv) # Saravali formula #https://saravali.github.io/astrology/bala_sthana.html#uchcha
        else: # PVR Book formula
            ubv = round(pd/180.0*20.0,2)
            ub.append(ubv) # PVR formula
    return ub
def __hadda_points(rasi,p_long,p):
    l_range = const.hadda_lords[rasi]
    hp = [planet for planet,long in l_range if p_long<=long ][0]
    if p == hp:
        return const.hadda_points[0]
    elif hp in const.friendly_planets[p]:
        return const.hadda_points[1]
    elif hp in const.enemy_planets[p]:
        return const.hadda_points[2]
    return 0.0
def _hadda_bala(planet_positions):
    hb = [ __hadda_points(h, p_long,p) for p,(h,p_long) in planet_positions[1:8]]
    return hb
def _drekkana_bala(p_to_h_of_drekkana_chart):
    kb = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h_of_drekkana_chart[p]
        if const.house_strengths_of_planets[p][h_p] > const._FRIEND:
            kb[p] = 10
        elif const.house_strengths_of_planets[p][h_p]==const._FRIEND:
            kb[p] = 5
        elif const.house_strengths_of_planets[p][h_p]==const._ENEMY:
            kb[p] = 2.5
    return kb
def _navamsa_bala(p_to_h_navamsa_chart):
    kb = {p:0 for p in range(7) }
    for p in range(7):
        h_p = p_to_h_navamsa_chart[p]
        if const.house_strengths_of_planets[p][h_p]>const._FRIEND:
            kb[p] = 5
        elif const.house_strengths_of_planets[p][h_p]==const._FRIEND:
            kb[p] = 2.5
        elif const.house_strengths_of_planets[p][h_p]==const._ENEMY:
            kb[p] = 1.25
    return kb
def pancha_vargeeya_bala(jd,place):
    """
        computes the Pancha Vargeeya bala score of the planets
            Keshetra Bala:
                A planet gets 30 units of Bala in own sign, 22.5 units in friendly sign, 15 units in neutral sign 
                and 7.5 units in an enemy sign.
            Drekkana Bala
                A planet in own rasi in D-3 gets 10 units of Drekkana bala. A planet in a friend’s rasi in D-3 gets 5 units of
                Drekkana bala. A planet in an enemy’s rasi in D-3 gets 2.5 units of Drekkana bala.
            Navamsa Bala
                A planet in own rasi in D-9 gets 5 units of Navamsa bala. A planet in a friend’s rasi in D-9 gets 2.5 units of
                Navamsa bala. A planet in an enemy’s rasi in D-9 gets 1.25 units of Navamsa bala.
            Uchcha Bala
                Uchcha bala shows how close a planet is from its exaltation point. A planet gets 20
                units of uchcha bala if it is at its deep exaltation point (Sun: 10º Ar, Moon: 3º Ta,
                Mars: 28º Cp, Mercury: 15º Vi, Jupiter: 5º Cn, Venus: 27º Pi, Saturn: 20º Li). At
                180º from its deep exaltation point, a planet is deeply debilitated and it gets 0 units of
                uchcha bala.
            Hadda Bala
                A planet in own hadda gets 15 units of Hadda bala. A planet in a friend’s hadda gets 7.5 units of Hadda bala. 
                A planet in an enemy’s hadda gets 3.75 units of Hadda bala.
        @param jd: Julian Day Number (of the annual day
        @param place: drik.Place struct: Place('place_name',latitude, longitude, timezone) 
        @return: Pancha Vargeeya Bala score for each planet - as a list 
            Example: [15.72, 14.27, 13.0, 6.33, 11.87, 16.05, 6.45] - Sun's score = 15.72, Venus's score = 16.05
    """
    rasi_chart = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    p_to_h_of_rasi_chart = utils.get_planet_house_dictionary_from_planet_positions(rasi_chart)
    kb = _kshetra_bala(p_to_h_of_rasi_chart)
    ub = _uchcha_bala(rasi_chart)
    hb = _hadda_bala(rasi_chart)
    drekkana_chart = charts.divisional_chart(jd, place,divisional_chart_factor=3)
    p_to_h_of_drekkana_chart = utils.get_planet_house_dictionary_from_planet_positions(drekkana_chart)
    db = _drekkana_bala(p_to_h_of_drekkana_chart)
    navamsa_chart = charts.divisional_chart(jd, place,divisional_chart_factor=9)
    p_to_h_of_navamsa_chart = utils.get_planet_house_dictionary_from_planet_positions(navamsa_chart)
    nb = _navamsa_bala(p_to_h_of_navamsa_chart)
    pvb = [kb,ub,hb,db,nb]
    pvb = [round(sum(x)/4.0,2) for x in zip(*pvb)]
    pvbd = {k:pvb[k] for k in range(7)}
    return pvbd
def dwadhasa_vargeeya_bala(jd,place):
    """
        Calculates dwadhasa_vargeeya_bala score of the planets
        @param jd: Julian Day Number (of the annual day
        @param place: drik.Place struct: Place('place_name',latitude, longitude, timezone) 
        @return:   returns dict of strong (>0) and weak (<0) planets. Also returns list of only strong planets
            Example: {0: -4, 1: 0, 2: -4, 3: 2, 4: 0, 5: -2, 6: 2} [3, 6]
    """
    dvp = {p:0 for p in range(7) }
    for dvf in range(1,13): #D1-D12 charts
        planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=dvf)
        p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
        for p in range(7):
            if const.house_strengths_of_planets[p][p_to_h[p]] >= const._FRIEND:
                dvp[p]+=1
    dvpd = {k:dvp[k] for k in range(7)}
    return dvpd
def _dig_bala(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    planet_positions = charts.rasi_chart(jd, place,ayanamsa_mode=ayanamsa_mode)
    powerless_houses_of_planets = [3,9,3,6,6,9,0]#[4,10,4,7,7,10,1]
    bm = drik.bhaava_madhya(jd, place)
    dbf = [bm[p] for p in powerless_houses_of_planets]
    dbp = [0 for _ in range(7)]
    for p,(h,long) in planet_positions[1:const._pp_count_upto_saturn]:
        p_long = h*30+long
        dbp[p] = round(abs(dbf[p]-p_long)/3,2)
    return dbp
def _divaratri_bala(jd,place):
    return _nathonnath_bala(jd,place)
def _nathonnath_bala(jd,place):
    nbp = [0 for _ in range(7)]
    _,_,_,tobh = utils.jd_to_gregorian(jd)
    mnhl = drik.midnight(jd, place)
    t_diff = (tobh - mnhl)*60/12 if tobh < 12.0 else (24.0 + mnhl - tobh)*60/12
    for p in [0,4,5]:
        nbp[p] = round(t_diff,2)
    for p in [1,2,6]:
        nbp[p] = round(60 - t_diff,2)
    nbp[3] = 60.0
    return nbp
def _paksha_bala(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    planet_positions = drik.dhasavarga(jd, place,divisional_chart_factor=1)
    sun_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    moon_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    pb = round(abs(sun_long - moon_long) / 3.0,2)
    pbp = [pb for _ in range(7)]
    cht_benefics,cht_malefics = charts.benefics_and_malefics(jd, place,ayanamsa_mode=ayanamsa_mode,exclude_rahu_ketu=True)
    #print(cht_benefics,cht_malefics)
    for p in cht_benefics:# const.natural_benefics:
        pbp[p] = pb
    for p in cht_malefics[:]:#const.natural_malefics[:-2]:#  #Exclude Rahu Kethu
        pbp[p] = round(60.0 - pb,2)
    pbp[1] *=2 
    return pbp
def _tribhaga_bala(jd,place):
    tbp = [0 for _ in range(7)]
    _,_,_,tobh = utils.jd_to_gregorian(jd)
    srh = drik.sunrise(jd, place)[0]
    ssh = drik.sunset(jd, place)[0]
    dl = drik.day_length(jd, place)
    nl = drik.night_length(jd, place)
    dlinc = dl/3 ; nlinc = nl / 3
    tbp[4] = 60 # Guru/Jupiter
    if tobh >= srh and tobh < srh+dlinc:  # 1st part of day
        tbp[3] = 60 # Mercury
    elif tobh >= srh+dlinc and tobh < srh+2*dlinc: #2nd part of day
        tbp[0] = 60 # Sun
    elif tobh >= srh+2*dlinc and tobh < ssh: # 3rd part of day
        tbp[6] = 60 # Saturn
    elif tobh > ssh and tobh < ssh+nlinc:#24: 1st part of night
        tbp[1] = 60 # Moon
    elif (tobh >= ssh+nlinc and tobh < 24) or (tobh >=0 and tobh < srh-nlinc): #2nd part of night
        tbp[5] = 60 # Venus
    elif tobh >= srh-nlinc and tobh < srh: #3rd part of night
        tbp[2] = 60 # Mars
    return tbp
def _days_elapsed_since_base(year,base_year=1951,base_days=174):
    # Base year and its initial day count based on BV Raman's Bhava and Graha Bala Table - I
    #base_year = 1951#1827#
    #base_days = 174#244#

    # Total years elapsed
    total_years = year - base_year

    # Count leap years between the base year and target year
    leap_years = len([
        y for y in range(base_year + 1, year + 1)
        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
    ])

    # Calculate total days directly
    non_leap_years = total_years - leap_years
    total_days = base_days + (leap_years * 366) + (non_leap_years * 365)

    return total_days
def _abdadhipathi(jd,place):
    abp = [0 for _ in range(7)]
    _abda_weekdays = [2,3,4,5,6,0,1] # Starts from Tuesday
    ay,am,ad,_ = utils.jd_to_gregorian(jd)
    elpased_days_in_year = int(jd-utils.gregorian_to_jd(drik.Date(ay,1,1))+1)
    _ahargana_days = _days_elapsed_since_base(ay-1)+elpased_days_in_year
    day = (int(_ahargana_days//360)*3+1)%7 # Add 1 get 1st day of the next kali year
    abp[_abda_weekdays[day]] = 15
    return abp
def _abda_bala(jd,place):
    abp = [0 for _ in range(7)]
    day = drik.vaara(jd)
    abp[day] = 15
    return abp
def _masadhipathi(jd,place):
    abp = [0 for _ in range(7)]
    _abda_weekdays = [2,3,4,5,6,0,1] # Starts from Tuesday
    ay,am,ad,_ = utils.jd_to_gregorian(jd)
    elpased_days_in_year = int(jd-utils.gregorian_to_jd(drik.Date(ay,1,1))+1)
    _ahargana_days = _days_elapsed_since_base(ay-1)+elpased_days_in_year
    day = (int(_ahargana_days//30)*2+1)%7 # Add 1 get 1st day of the next kali year
    #print(_ahargana_days,day,_abda_weekdays[day],abp[_abda_weekdays[day]])
    abp[_abda_weekdays[day]] = 30
    return abp
def _masa_bala(jd,place):
    abp = [0 for _ in range(7)]
    day = drik.vaara(jd)
    abp[day] = 30
    return abp
def _vaaradhipathi(jd,place):
    abp = [0 for _ in range(7)]
    _abda_weekdays = [2,3,4,5,6,0,1]
    ay,am,ad,bth = utils.jd_to_gregorian(jd)
    elpased_days_in_year = int(jd-utils.gregorian_to_jd(drik.Date(ay,1,1))+1)
    _ahargana_days = _days_elapsed_since_base(ay-1, base_year=1827, base_days=244)+elpased_days_in_year
    #_ahargana_days = _days_elapsed_since_base(ay-1)+elpased_days_in_year if vaaradhipathi_method==1 \
    #                    else _days_elapsed_since_base(ay-1, base_year=1827, base_days=244)+elpased_days_in_year
    if bth < drik.sunrise(jd, place)[0]: _ahargana_days -= 1
    day = int(_ahargana_days)%7 # Add 1 get 1st day of the next kali year
    abp[_abda_weekdays[day]] = 45
    return abp
def _vaara_bala(jd,place):
    abp = [0 for _ in range(7)]
    day = drik.vaara(jd)
    _,_,_,tobh = utils.jd_to_gregorian(jd)
    srise = drik.sunrise(jd, place)[0]
    if tobh < srise:
        day = (day-1)%7
    abp[day] = 45
    return abp
def _hora_bala(jd,place):
    abp = [0 for _ in range(7)]
    day = drik.vaara(jd)
    _,_,_,tobh = utils.jd_to_gregorian(jd)
    srise = drik.sunrise(jd, place)[0]
    if tobh < srise:
        day = (day-1)%7
        tobh += 24.0
    hora_order = [6,4,2,0,5,3,1]
    hora = (int(tobh-srise)+day+1)%7
    abp[hora_order[hora]] = 60
    return abp
def _ayana_bala(jd,place):
    _declinations = drik.declination_of_planets(jd, place)
    ab = [0 for _ in range(7)]
    for p in range(7):
        ab[p] = round((24.0 + _declinations[p])*1.25,2)
        if p==0:
            ab[p] *= 2
    return ab
def _yuddha_bala(jd,place):
    yb = [0 for _ in range(7)]
    pp = drik.dhasavarga(jd, place, divisional_chart_factor=1)[:7]
    p_longs = [h*30+long for _,(h,long) in pp]
    p_longs_copy = p_longs[:]
    ce = sorted(utils.closest_elements(p_longs, p_longs))
    indices = [p_longs.index(v) for v in ce]
    if any([sm==i for sm in [0,1] for i in indices]):
        return yb # All Zero
    # Find Sum of balas upto hora bala
    sb = _sthana_bala(jd, place)
    dgb = _dig_bala(jd,place)
    nb = _nathonnath_bala(jd, place)
    pb = _paksha_bala(jd,place)
    tb = _tribhaga_bala(jd, place)
    hb = _hora_bala(jd, place)
    bala_totals = [0 for _ in range(7)]
    for i in indices:
        bala_totals[i] += sb[i]
        bala_totals[i] += dgb[i]
        bala_totals[i] += nb[i]
        bala_totals[i] += pb[i]
        bala_totals[i] += tb[i]
        bala_totals[i] += hb[i]
    b_diff = abs(bala_totals[indices[0]] - bala_totals[indices[1]])
    dia_diff = abs(const.planets_disc_diameters[indices[0]]-const.planets_disc_diameters[indices[1]])
    y_bala = round(b_diff/dia_diff,2)
    yb[indices[0]] =  y_bala ; yb[indices[1]] =  -y_bala
    return yb
def _kaala_bala(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    kb = [0 for _ in range(7)]
    nb = _nathonnath_bala(jd, place)
    pb = _paksha_bala(jd, place,ayanamsa_mode=ayanamsa_mode)
    tb = _tribhaga_bala(jd, place)
    ab = _abdadhipathi(jd,place)# _abda_bala(jd, place)
    mb = _masadhipathi(jd, place) # _masa_bala(jd, place)
    vb = _vaaradhipathi(jd, place) # _vaara_bala(jd, place)
    hb = _hora_bala(jd, place)
    ayb = _ayana_bala(jd, place)
    yb = _yuddha_bala(jd, place)
    for p in range(7):
        kb[p] += nb[p]
        kb[p] += pb[p]
        kb[p] += tb[p]
        kb[p] += ab[p]
        kb[p] += mb[p]
        kb[p] += vb[p]
        kb[p] += hb[p]
        kb[p] += ayb[p]
        kb[p] += yb[p]
    kb = [round(kbp,2) for kbp in kb]
    return kb
def _ishta_phala(jd,place):
    planet_positions = charts.rasi_chart(jd, place)
    ip_score = {const._ADHIMITRA_GREATFRIEND:22,
                const._MITHRA_FRIEND:15,const._SAMAM_NEUTRAL:8,const._ADHISATHRU_GREATENEMY:4,
                const._SATHRU_ENEMY:2}
    ip = [0 for _ in range(7)]
    for p,(h,_) in planet_positions[1:const._pp_count_upto_saturn]:
        owner = house.house_owner_from_planet_positions(planet_positions, h)
        if const.house_strengths_of_planets[p][h]==const._EXALTED_UCCHAM:
            ip[p] = 60
        elif h == const.moola_trikona_of_planets[p]: # Moola Trinkona Rasi
            ip[p] = 45
        elif const.house_strengths_of_planets[p][h]==const._OWNER_RULER: # Swastha Rasi
            ip[p] = 30
        else:
            ip[p] = ip_score[const.compound_planet_relations[p][owner]]
    return ip
def _subha_rashmi(jd,place):
    planet_positions = charts.rasi_chart(jd, place)
    cr = _cheshta_rashmi(jd, place); ur = _uccha_rashmi(planet_positions)
    return [0.25*(cr[i]+ur[i]) for i in range(7)]
def _cheshta_rashmi(jd,place):
    """ STILL UNDER EXPERIMENT - Exact Algorithm unknown"""
    cb = [c*3.0 for c in _cheshta_bala(jd, place)]
    pp = drik.dhasavarga(jd, place, divisional_chart_factor=1)
    sun_long = pp[0][1][0]*30+pp[0][1][1]; moon_long = pp[1][1][0]*30+pp[1][1][1]
    cb[0] = (sun_long+90.0)%360 # Add 3 rasis to sun long
    cb[1] = (moon_long-sun_long)%360
    for p in range(7):
        if cb[p] > 180.0: cb[p] = 360.0 - cb[p]
        cb[p] = ((cb[p]+30)*2)/30
    return cb
def _cheshta_bala(jd,place):
    pp = drik.dhasavarga(jd, place, divisional_chart_factor=1)
    cb = [0 for _ in range(7)]
    from jhora.panchanga import surya_sidhantha
    sun_mean_long = surya_sidhantha._planet_mean_longitude(jd, place, const._SUN)
    #print('planet',0,'mean longitude',sun_mean_long)
    for p in [const._MARS, const._MERCURY, const._JUPITER, const._VENUS, const._SATURN]: #range(2,7):
        p_id = drik.planet_list.index(p)
        mean_long = surya_sidhantha._planet_mean_longitude(jd, place, p)
        seegrocha = sun_mean_long
        if p in [const._MERCURY,const._VENUS]:
            seegrocha = mean_long
            mean_long = sun_mean_long
        true_long = pp[p_id][1][0]*30+pp[p_id][1][1]
        ave_long = 0.5*(true_long+mean_long)
        reduced_chesta_kendra = abs(seegrocha - ave_long)
        cb[p_id] = round(reduced_chesta_kendra/3,2)
        #print('planet',p_id,'mean longitude',mean_long, surya_sidhantha._planet_true_longitude(jd, place, p, mean_long))
    return cb
def _naisargika_bala(jd=None,place=None):
    return const.naisargika_bala[:-2]
def __drik_bala_calc_1(dk_p1_p2,p1,p2):
    _DEBUG_ = False
    """ 
        TODO: Aspects for div charts go beyond 60 (>100%) WHY???
        Should we use aspect strength factors 1/4, 1/2 3/4 and 1.0??
    """
    
    if _DEBUG_:  print(p1,p2,'drishti angle',dk_p1_p2)
    dk_p1_p2_new = dk_p1_p2
    if dk_p1_p2 >= 0 and dk_p1_p2 <= 30:
        dk_p1_p2_new = 0.0
        if _DEBUG_:  print('diff between',0,30,dk_p1_p2_new)
    elif dk_p1_p2 >= 30 and dk_p1_p2 <= 60:
        dk_p1_p2_new = 0.5*(dk_p1_p2-30.0)
        if _DEBUG_:  print('diff between',30,60,dk_p1_p2_new)
    elif dk_p1_p2 >= 60 and dk_p1_p2 <= 90:
        dk_p1_p2_new = (dk_p1_p2-60.0)+15
        if _DEBUG_:  print('diff between',60,90,dk_p1_p2_new)
        if p1 == 6: # Saturn
            dk_p1_p2_new += 45
            if _DEBUG_:  print('p1',6,'add',45,dk_p1_p2_new)
    elif dk_p1_p2 >= 90 and dk_p1_p2 <= 120:
        dk_p1_p2_new = 0.5*(120.0 - dk_p1_p2) + 30
        if _DEBUG_:  print('diff between',90,120,dk_p1_p2_new)
        if p1 == 2: # Mars
            dk_p1_p2_new += 15
            if _DEBUG_:  print('p1',2,'add',15,dk_p1_p2_new)
    elif dk_p1_p2 >= 120 and dk_p1_p2 <= 150:
        dk_p1_p2_new = (150.0 - dk_p1_p2)
        if _DEBUG_:  print('diff between',120,150,dk_p1_p2_new)
        if p1 == 4: # Jupiter
            dk_p1_p2_new += 30
            if _DEBUG_:  print('p1',4,'add',30,dk_p1_p2_new)
    elif dk_p1_p2 >= 150 and dk_p1_p2 <= 180:
        dk_p1_p2_new = 2.0*(dk_p1_p2 - 150)
        if _DEBUG_:  print('diff between',150,180,dk_p1_p2_new)
    elif dk_p1_p2 >= 180 and dk_p1_p2 <= 300:
        dk_p1_p2_new = 0.5*(300.0 - dk_p1_p2)
        if _DEBUG_:  print('diff between',180,300,dk_p1_p2_new)
        if p1 == 2 and (dk_p1_p2 >= 210 and dk_p1_p2 <= 240) : # Mars
            dk_p1_p2_new += 15
            if _DEBUG_:  print('p1',2,'add',15,dk_p1_p2_new)
        if p1 == 4 and (dk_p1_p2 >= 240 and dk_p1_p2 <= 270) : # Jupiter
            dk_p1_p2_new += 30
            if _DEBUG_:  print('p1',4,'add',30,dk_p1_p2_new)
        if p1 == 6 and (dk_p1_p2 >= 270 and dk_p1_p2 <= 300) : # Saturn
            dk_p1_p2_new += 45
            if _DEBUG_:  print('p1',6,'add',45,dk_p1_p2_new)
    else:
        dk_p1_p2_new = 0.0
        if _DEBUG_: print('<30 or >300',dk_p1_p2_new)
    #dk_p1_p2_new = min(100,round(dk_p1_p2_new/60*100)) ## Forcing >100 to 100 Not sure this is correct?
    #dk_p1_p2_new = min(60,dk_p1_p2_new) ## Forcing >60 to 60 Not sure this is correct?
    if _DEBUG_: print('final',p1,p2,'drishti value',dk_p1_p2_new)
    return dk_p1_p2_new
def planet_aspect_relationship_table(planet_positions,include_houses=False):
    _DEBUG_ = False
    pp = planet_positions[1:]
    rows = 21 if include_houses else 9
    dk = [[ 0 for _ in range(9)] for _ in range(rows)]
    for p1 in range(9): # Aspected Planet
        p1_long = pp[p1][1][0]*30+pp[p1][1][1]
        for p2 in range(9): # Aspecting Planet
            p2_long = pp[p2][1][0]*30+pp[p2][1][1]
            dk_p1_p2 = round((360.0+p1_long-p2_long)%360,2)
            if _DEBUG_: print('drishti angle',p2,p2_long,p1,p1_long,dk_p1_p2)
            dk_p1_p2 = __drik_bala_calc_1(dk_p1_p2,p2,p1)
            dk[p1][p2] = round(dk_p1_p2,2)
    if include_houses:
        asc_house = pp[0][1][0]; asc_long = pp[0][1][1]
        for h in range(12): # Aspected Planet
            h1 = (asc_house+h)%12
            p1_long = h1*30+asc_long
            for p2 in range(9): # Aspecting Planet
                p2_long = pp[p2][1][0]*30+pp[p2][1][1]
                dk_p1_p2 = round((360.0+p1_long-p2_long)%360,2)
                if _DEBUG_: print('drishti angle',p2,p2_long,p1,p1_long,dk_p1_p2)
                dk_p1_p2 = __drik_bala_calc_1(dk_p1_p2,p2,p1)
                dk[p1+h+1][p2] = round(dk_p1_p2,2)
    import numpy as np
    dk = np.array(dk).T
    return dk.tolist()
def _drik_bala(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    dk = [[ 0 for _ in range(7)] for _ in range(7)]
    pp = charts.rasi_chart(jd, place,ayanamsa_mode=ayanamsa_mode)
    #planets_with_mercury = [p for p,(h,_) in pp[1:] if h==pp[4][1][0] and p != 3]
    _tithi = drik.tithi(jd, place)[0]; waxing_moon = _tithi <= 15
    pp = pp[1:-2]
    subha_grahas,asubha_grahas = charts.benefics_and_malefics(jd, place,ayanamsa_mode=ayanamsa_mode,exclude_rahu_ketu=True)
    for p1 in range(7): # Aspected Planet
        p1_long = pp[p1][1][0]*30+pp[p1][1][1]
        for p2 in range(7): # Aspecting Planet
            p2_long = pp[p2][1][0]*30+pp[p2][1][1]
            dk_p1_p2 = round((360.0+p1_long-p2_long)%360,2)
            dk_p1_p2 = __drik_bala_calc_1(dk_p1_p2,p2,p1)
            dk[p1][p2] = round(dk_p1_p2,2)
    import numpy as np
    dk = np.array(dk).T.tolist()
    #print('drik bala before',dk)
    dkp = [0 for _ in range(7)] ; dkm = [0 for _ in range(7)]; dk_final = [0 for _ in range(7)]
    for row in range(7):
        for col in range(7):
            if row in subha_grahas:
                dkp[col] += dk[row][col] 
            if row in asubha_grahas:
                dkm[col] += dk[row][col]
            dk_final[col] = round((dkp[col] - dkm[col])/4,2) 
    #print('drik bala values',dk_final)
    return dk_final
def shad_bala(jd,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE):
    sb = []
    stb = _sthana_bala(jd, place,ayanamsa_mode=ayanamsa_mode)
    #print('_sthana_bala',stb)
    sb.append(stb)
    kb = _kaala_bala(jd, place,ayanamsa_mode=ayanamsa_mode)
    #print('_kaala_bala',kb)
    sb.append(kb)
    dgb = _dig_bala(jd, place,ayanamsa_mode=ayanamsa_mode)
    #print('_dig_bala',dgb)
    sb.append(dgb)
    cb = _cheshta_bala_new(jd, place,use_epoch_table=True)
    #print('_cheshta_bala',cb)
    sb.append(cb)
    nb = _naisargika_bala(jd, place)
    #print('_naisargika_bala',nb)
    sb.append(nb)
    dkb = _drik_bala(jd, place,ayanamsa_mode=ayanamsa_mode)
    #print('_drik_bala',dkb)
    sb.append(dkb)
    import numpy as np
    sbn = np.array(sb).tolist()
    sb_sum = np.around(np.sum(sbn,0),2).tolist()
    sb_rupa = [round(ss/60.0,2) for ss in sb_sum]
    sb_req = [5,6,5,7,6.5,5.5,5]
    sb_strength = [round(sb_rupa[p]/sb_req[p],2) for p in range(7)]
    return [stb, kb, dgb, cb, nb, dkb, sb_sum, sb_rupa,sb_strength]
def _bhava_adhipathi_bala(jd,place):
    bhava_pp = charts.bhava_chart_houses(jd, place)
    asc_rasi = bhava_pp[const._ascendant_symbol][0]
    bb = []
    sb_sum = shad_bala(jd, place)[6]
    for h in range(12):
        r = (h+asc_rasi)%12
        owner = const.house_owners[r]
        bb.append(sb_sum[owner])
    return bb
def _bhava_dig_bala(jd,place):
    bdb = [0 for _ in range(12)]
    bm = drik.bhaava_madhya(jd, place)
    brl = {0:const.nara_rasi_longitudes,3:const.jalachara_rasi_longitudes,9:const.chatushpada_rasis,6:const.keeta_rasis}
    chk = []
    for k,v in brl.items():
        chk += list(set([((k+h)%12,abs(60-abs(h)*10)) for h in range(-7,7) for l1,l2 in v if bm[(k+h)%12] >= l1 and bm[(k+h)%12] <= l2]))
    chk = {k:v for k,v in chk}
    return list(dict(sorted(chk.items())).values())
def __bhava_drik_bala_calc_1(dk_p1_p2,p1):
    dk_p1_p2_new = dk_p1_p2
    if dk_p1_p2 > 0 and dk_p1_p2 <= 30.0:
        dk_p1_p2_new = 0.0
    elif dk_p1_p2 >= 30.01 and dk_p1_p2 <= 60.0:
        dk_p1_p2_new = 0.5*(dk_p1_p2-30.0)
    elif dk_p1_p2 >= 60.01 and dk_p1_p2 <= 90.0:
        dk_p1_p2_new = (dk_p1_p2-60.0)+15
        if p1 == 6: # Mars
            dk_p1_p2_new += 45
    elif dk_p1_p2 >= 90.01 and dk_p1_p2 <= 120.0:
        dk_p1_p2_new = 0.5*(120.0 - dk_p1_p2) + 30
        if p1 == 2: # Mars
            dk_p1_p2_new += 15
    elif dk_p1_p2 >= 120.01 and dk_p1_p2 <= 150.0:
        dk_p1_p2_new = (150.0 - dk_p1_p2)
        if p1 == 4: # Jupiter
            dk_p1_p2_new += 30
    elif dk_p1_p2 >= 150.01 and dk_p1_p2 <= 180.0:
        dk_p1_p2_new = 2.0*(dk_p1_p2 - 150)
    elif dk_p1_p2 >= 180.01 and dk_p1_p2 <= 300.0:
        dk_p1_p2_new = 0.5*(300.0 - dk_p1_p2)
        if p1 == 2 and (dk_p1_p2 > 210.01 and dk_p1_p2 < 240.01) : # Mars
            dk_p1_p2_new += 15
        if p1 == 4 and (dk_p1_p2 > 240.01 and dk_p1_p2 < 270.01) : # Mars
            dk_p1_p2_new += 30
        if p1 == 6 and (dk_p1_p2 > 270.01 and dk_p1_p2 < 300.01) : # Mars
            dk_p1_p2_new += 45
    else:
        dk_p1_p2_new = 0.0
    if p1 not in [3,4]:
        dk_p1_p2_new = round(dk_p1_p2_new*0.25,2)
    return dk_p1_p2_new
def bhava_drishti_bala(jd,place):
    """ TODO: Check if Bhava Drishi bala is same as Aspect Relationship Table??? """
    return _bhava_drik_bala(jd, place)
def _bhava_drik_bala(jd,place):
    dk = [[ 0 for _ in range(7)] for _ in range(12)]
    pp = charts.rasi_chart(jd, place)
    house_planet_dict = utils.get_house_planet_list_from_planet_positions(pp)
    pp = pp[1:-2]
    subha_grahas = [1,3,4,5] ; asubha_grahas = [0,2,6]
    """ 
        TODO: Find out the aspect dictionary as below from the chart
        For example Sun aspects Moon and Venus, Moon aspects All but itelf...
        How to find this? Graha/Rasi Drishti?
        (1) Jupiter and Venus are natural benefics (saumya grahas or subha grahas).
        Mercury becomes a natural benefic when he is alone or with more natural
        benefics. Waxing Moon of Sukla paksha is a natural benefic.
        (2) Sun, Mars, Rahu and Ketu are natural malefics (kroora grahas or paapa grahas).
        Mercury becomes a natural malefic when he is joined by more natural malefics.
        Waning Moon of Krishna paksha is a natural malefic.        
    """ 
    grp,ghp,gpp = house.graha_drishti_from_chart(house_planet_dict)
    rrp,rhp,rpp = house.raasi_drishti_from_chart(house_planet_dict)
    planet_house_aspects = {}
    for planet in range(7):
        planet_house_aspects[planet] = sorted(list(set(ghp[planet]+rhp[planet])))
        planet_house_aspects[planet] = [int(p) for p in planet_house_aspects[planet] if p not in [const._ascendant_symbol,'7','8']]
    bm = drik.bhaava_madhya(jd, place)
    for h in range(12): # Aspected Planet
        h_mid = bm[h]
        for p in range(7): # Aspecting Planet
            if (h+1) in planet_house_aspects[p]:
                p_long = pp[p][1][0]*30+pp[p][1][1]
                dk_h_p = round((360.0+h_mid-p_long)%360,2)
                dk_h_p = __bhava_drik_bala_calc_1(dk_h_p,p)
            else:
                dk_h_p = 0.0
            dk[h][p] = round(dk_h_p,2)
    import numpy as np
    dkp = [0 for _ in range(12)] ; dkm = [0 for _ in range(12)]; dk_final = [0 for _ in range(12)]
    for row in range(12):
        for col in range(7):
            if col in subha_grahas:
                dkp[row] += dk[row][col] 
            if row in asubha_grahas:
                dkm[row] += dk[row][col]
            dk_final[row] = round((dkp[row] - dkm[row])/4,2) 
    return dk_final
def bhava_bala(jd,place):
    """
        Computes bhava bala
        Returns bhava bala as list of bhava bala followed by list of bhava bala in rupas
    """
    bab = _bhava_adhipathi_bala(jd, place)
    bdb = _bhava_dig_bala(jd, place)
    bdrb = _bhava_drik_bala(jd, place)
    bb = list(map(sum,zip(*[bab,bdb,bdrb])))
    bb = [round(b,2) for b in bb]
    bb_rupas = [round(b/60,2) for b in bb]
    bb_strength = [round(b/const.minimum_bhava_bala_rupa,2) for b in bb_rupas]
    return [bb,bb_rupas,bb_strength]
def get_planet_mean_longitude_using_epoch_table(jd,place,planet_index=0):
    if planet_index == 1: return 0.0
    days_from_epoch = _DAYS_FROM_EPOCH(jd,place); year_jd = utils.jd_to_gregorian(jd)[0]
    _ujjain_epoch_table_for_planets = ujjain_epoch_table_for_planets[planet_index]
    # Determine if the table has 4 columns (missing tens) or more
    has_tens = len(next(iter(_ujjain_epoch_table_for_planets.values()))) > 4
    # Break the days_from_epoch into its components
    digits = str(days_from_epoch).split('.')
    whole_days_from_epoch = int(digits[0])
    decimal_part = float(f"0.{digits[1]}") if len(digits) > 1 else 0

    # Extract each position value
    ten_thousands = (whole_days_from_epoch // 10000) % 10
    thousands = (whole_days_from_epoch // 1000) % 10
    hundreds = (whole_days_from_epoch // 100) % 10
    tens_and_units = whole_days_from_epoch % 100  # Combine tens and units if tens is missing
    tens = (whole_days_from_epoch // 10) % 10
    units = whole_days_from_epoch % 10

    #print(days_from_epoch, whole_days_from_epoch, ten_thousands, thousands, hundreds, tens, units, tens_and_units)

    # Lookup and calculate corresponding values
    value_ten_thousands = _ujjain_epoch_table_for_planets.get(ten_thousands, [0, 0, 0, 0])[-1]  # 4th column
    value_thousands = _ujjain_epoch_table_for_planets.get(thousands, [0, 0, 0, 0])[-2]          # 3rd column
    value_hundreds = _ujjain_epoch_table_for_planets.get(hundreds, [0, 0, 0, 0])[-3]            # 2nd column

    # Handle tens and units based on the presence of the tens column
    if has_tens:
        # Use tens and units separately
        value_tens = _ujjain_epoch_table_for_planets.get(tens, [0, 0, 0, 0, 0])[1]  # 5th column (tens)
        value_units = _ujjain_epoch_table_for_planets.get(units, [0, 0, 0, 0])[0]   # 1st column (units)
        combined_units_value = value_tens + value_units
    else:
        # Combine tens and units, using the units column
        units_row = tens_and_units // 10
        units_row_value = _ujjain_epoch_table_for_planets.get(units_row, [0, 0, 0, 0])[0]  # Units column
        combined_units_value = 10 * units_row_value

    value_decimal = decimal_part * _ujjain_epoch_table_for_planets.get(1, [0, 0, 0, 0])[0]     # Decimal uses 1st column
    #print(value_ten_thousands, value_thousands, value_hundreds, combined_units_value, value_decimal)

    # Compute the final sum
    total_sum = value_ten_thousands + value_thousands + value_hundreds + combined_units_value + value_decimal + \
                planet_mean_positions_at_epoch_ujjain_1900[planet_index]
    years_since_epoch = year_jd - _EPOCH_YEAR
    _planet_longitude_correction = planet_longitude_correction(planet_index,years_since_epoch)
    #print(planet_index,planet_correction_factors_per_year_since_epoch[planet_index],_planet_longitude_correction)
    total_sum += _planet_longitude_correction
    return total_sum % 360
def get_planet_mean_longitude(jd,place,planet_index=0):
    if planet_index == 1: return 0.0
    days_from_epoch = _DAYS_FROM_EPOCH(jd,place)
    planet_speed_at_epoch = planet_speed_at_epoch_ujjain_1900[planet_index]
    years_since_epoch = utils.jd_to_gregorian(jd)[0] - _EPOCH_YEAR
    _planet_longitude_correction = planet_longitude_correction(planet_index,years_since_epoch)
    planet_mean_position_at_jd = ( (planet_mean_positions_at_epoch_ujjain_1900[planet_index]+days_from_epoch*planet_speed_at_epoch) + \
                                    _planet_longitude_correction) % 360
    #print(days_from_epoch,planet_mean_positions_at_epoch_ujjain_1900[planet_index],_planet_longitude_correction,planet_speed_at_epoch,planet_mean_position_at_jd)
    return planet_mean_position_at_jd
def _cheshta_bala_new(jd,place,use_epoch_table=False):
    pp = drik.dhasavarga(jd, place, divisional_chart_factor=1)
    cb = [0 for _ in range(7)]
    sun_mean_long = get_planet_mean_longitude(jd, place, const._SUN)
    for p in [const._MARS, const._MERCURY, const._JUPITER, const._VENUS, const._SATURN]: #range(2,7):
        p_id = drik.planet_list.index(p)
        mean_long = get_planet_mean_longitude_using_epoch_table(jd, place, p_id) if use_epoch_table \
                        else get_planet_mean_longitude(jd, place, p_id)
        seegrocha = sun_mean_long
        if p in [const._MERCURY,const._VENUS]:
            seegrocha = mean_long
            mean_long = sun_mean_long
        true_long = pp[p_id][1][0]*30+pp[p_id][1][1]
        ave_long = 0.5*(true_long+mean_long)
        reduced_chesta_kendra = abs(seegrocha - ave_long)
        cb[p_id] = round(reduced_chesta_kendra/3,2)
        #print('planet',p_id,'mean longitude',mean_long, surya_sidhantha._planet_true_longitude(jd, place, p, mean_long))
    return cb
if __name__ == "__main__":
    #dob = (1996,12,7); tob = (10,34,0); place = drik.Place('Chennai',13.0878,80.2785,5.5)
    #dob = drik.Date(1981,9,13); tob = (1,30,0); place = drik.Place('VPJainExample',28+39/60,77+13/60,5.5)
    #dob = drik.Date(1974,7,29); tob = (5,5,0); place = drik.Place('UserExample',27+18/60,78.0,5.5)
    #jd = utils.julian_day_number(dob, tob)
    dob = drik.Date(1918,10,16); tob = (14,22,16); place = drik.Place('BVRamanExample',13,77+35/60,5.5)
    jd = utils.julian_day_number(dob, tob)
    drik.set_ayanamsa_mode('RAMAN')
    pp = charts.rasi_chart(jd, place); print('BVRamanExample Planet Positions',pp)
    print("Expected: [15.86, -21.73, 0.95, 15.64, -16.04, 18.47, 7.21]\n",_drik_bala(jd, place))
    exit()
    pp = charts.rasi_chart(jd, place)
    print(pp[1:10])
    pa = planet_aspect_relationship_table(pp,include_houses=True)
    print(pa)
    exit()
    ur = _uccha_rashmi(pp)
    print(ur)
    print(_cheshta_rashmi(jd,place))
    print(_subha_rashmi(jd,place))
    print(_ishta_phala(jd,place))
    exit()
    rasi_chart = utils.get_house_planet_list_from_planet_positions(pp)
    print('rasi chart',rasi_chart)
    from jhora.horoscope.transit import tajaka
    print(tajaka.planet_aspects_from_chart(rasi_chart))
    #exit()
    print('_bhava_adhipathi_bala',_bhava_adhipathi_bala(jd, place))
    print('_bhava_dig_bala',_bhava_dig_bala(jd, place))
    print('_bhava_drik_bala',_bhava_drik_bala(jd,place))
    print('bhava_bala',bhava_bala(jd, place))
    exit()
    sb = shad_bala(jd,place)
    for i,b in enumerate(['sthaana bala','kaala bala','dig bala','chesta bala','naisargika bala','drik bala','shad bala','shad bala (rupas)','shad bala (strength)']):
        print(b,sb[i])
    exit()
    """
    print('uccha bala',_uchcha_bala(pp_sv[1]))
    print('saptha vargaja bala',_sapthavargaja_bala(jd,place))
    print('ojayugama bala',_ojayugama_bala(pp_sv[1],pp_sv[9]))
    print('kendra bala',_kendra_bala(pp_sv[1]))
    print(' dreshkon bala',_dreshkon_bala(pp_sv[1]))
    """
    print('sthana bala', _sthana_bala(jd,place))
    print('dig bala',_dig_bala(jd,place))
    print('_nathonnath_bala',_nathonnath_bala(jd,place))
    print('_paksha_bala',_paksha_bala(jd,place))
    print('_tribhaga_bala',_tribhaga_bala(jd,place))
    print('_hora_bala',_hora_bala(jd,place))
    print('_abda_bala',_abda_bala(jd,place))
    print('_masa_bala',_masa_bala(jd,place))
    print('_vaara_bala',_vaara_bala(jd,place))
    print('_ayana_bala',_ayana_bala(jd,place))
    print('_yuddha_bala',_yuddha_bala(jd,place))
    print('_kaala_bala',_kaala_bala(jd,place))
    print('_cheshta_bala',_cheshta_bala(jd,place))
    print('_naisargika_bala',_naisargika_bala(jd,place))
    print('_drik_bala',_drik_bala(jd,place))