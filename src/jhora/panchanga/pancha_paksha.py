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
"""
    Module for Pancha Paksha Sastra
"""

import pandas as pd
from jhora import utils, const
from jhora.panchanga import drik, pancha_paksha

PP_DB_FILE = const.ROOT_DIR+ '/data/pancha_pakshi_db.csv'
IMAGE_PATH = const._IMAGES_PATH + const._sep
_WEEK_DAY_INDEX = 0; _PAKSHA_INDEX = 1; _DAYNIGHT_INDEX = 2
_NAK_BIRD_INDEX = 3; _NAK_ACTIVITY_INDEX = 4; _SUB_BIRD_INDEX = 5; _SUB_ACTIVITY_INDEX = 6
_DURATION_FACTOR = 7; _RELATION = 8; _POWER_FACTOR=9;_EFFECT = 10; _RATING=11;
_PADU_PAKSHI = 12; _BHARANA_PAKSHI = 13
_LAST_COL_FOR_READING = _BHARANA_PAKSHI#_RELATION
_DATE_FORMAT = "yyyy-MM-dd HH:mm:ss"  # Custom format string

_FROM_DATE_DISP = 0; _TO_DATE_DISP=1; _DURATION_DISP=2; _MAIN_BIRD_DISP=3;
_MAIN_ACT_DISP = 4; _SUB_BIRD_DISP = 5; _SUB_ACT_DISP = 6; _RELATION_DISP = 7; _POWER_FACTOR_DISP = 8
_EFFECT_DISP = 9; _RATING_DISP = 10

_DEFAULT_ICON_SIZE = 16
#Pancha Pakshi for each star (birth if sukla paksha, birth if in krishna paksha)
#1:Vulture 2:Owl, 3:Crow, 4:Cock, 5:Peacock
pancha_pakshi_birds = ['vulture','owl','crow','cock','peacock']
pancha_pakshi_images = ['vulture.png','owl.png','crow.png','cock.png','peacock.png']
pancha_pakshi_activities = ['ruling','eating','walking','sleeping','dying']
pp_activity_background_colors = ['dark green','yellow','light green','orange','red']
pp_relations = ['enemy','same','friend']; pp_relation_colors = ['orange','yellow','light green']
pp_effect = ['very_bad','bad','average','good','very_good']
pp_effect_colors = ['red','orange','yellow','light green','dark green']
pancha_pakshi_activity_images = [p+'.png' for p in pancha_pakshi_activities]
bird_list = [0,1,2,3,4];activity_list = [1,2,3,4,5] 
pancha_pakshi_stars_birds_paksha = [(1,5),(1,5),(1,5),(1,5),(1,5),(2,4),(2,4),(2,4),(2,4),(2,4),(2,4),
                                    (3,3),(3,3),(3,3),(3,3),(3,3),(4,2),(4,2),(4,2),(4,2),(4,2),
                                    (5,1),(5,1),(5,1),(5,1),(5,1),(5,1)]
# Duration List: First list is for day time and 2nd list for night time
# Each duration is respectively for activities: Rule, Eat, Walk, Sleep, Death
_pancha_pakshi_duration_list = [[48,30,36,18,12],[24,30,30,24,36]]
pancha_pakshi_duration_list = [[ele/144 for ele in row] for row in _pancha_pakshi_duration_list ]
def _get_birth_nakshathra(jd,place):
    return drik.nakshatra(jd, place)[0]
def _get_paksha(jd,place):
    _tithi = drik.tithi(jd, place)[0]
    return 1 if _tithi <= 15 else 2
def _get_birth_bird_from_nakshathra(birth_star,_paksha):
    return pancha_pakshi_stars_birds_paksha[birth_star-1][_paksha-1]
def get_matching_pancha_pakshi_data_from_db(bird_index,weekday_index,paksha_index):
    pp_db = pd.read_csv(PP_DB_FILE,index_col=None, encoding='utf-8',usecols=range(_LAST_COL_FOR_READING+1))
    search_criteria = (
        (pp_db.iloc[:,_NAK_BIRD_INDEX] == bird_index - 1) &
        (pp_db.iloc[:,_WEEK_DAY_INDEX] == weekday_index - 1) &
        (pp_db.iloc[:,_PAKSHA_INDEX] == paksha_index - 1)
    )
    search_results = pp_db[search_criteria]
    result_list = search_results.values.tolist()
    return result_list
def construct_pancha_pakshi_information(dob=None,tob=None,place=None,nakshathra_bird_index=None):
    jd = utils.julian_day_number(dob,tob)
    sunrise_jd = drik.sunrise(jd, place)[-1]
    if jd < sunrise_jd:
        jd -= 1
        sunrise_jd = drik.sunrise(jd, place)[-1]
    weekday_index = drik.vaara(jd)+1
    paksha_index = pancha_paksha._get_paksha(jd, place)
    day_length = drik.day_length(jd, place)
    night_length = drik.night_length(jd, place)
    day_inc = day_length/5.0; night_inc = night_length/5.0
    result_list = pancha_paksha.get_matching_pancha_pakshi_data_from_db(nakshathra_bird_index,weekday_index,paksha_index)
    headers = ['starts_at','ends_at','duration','main_bird','main_activity','sub_bird','sub_activity','relation',
               'power','effect','rating']
    headers = [utils.resource_strings[h+'_str'] for h in headers]
    top_level_list = []; child_level_list = []; parent_level_labels = []
    time_from_jd = sunrise_jd
    for row in range(0,len(result_list),5):
        wdi,pi,dni,mbi,mai,sbi,sai,df,reli,pf,efi,rtng,ppi,bpi = result_list[row]
        time_inc = day_inc/24 if dni==0 else night_inc/24
        time_to_jd = time_from_jd + time_inc
        by,bm,bd,bfh = utils.jd_to_gregorian(time_from_jd)
        time_from = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh,use_24hour_format=True)
        by,bm,bd,bfh = utils.jd_to_gregorian(time_to_jd)
        time_to = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh,use_24hour_format=True)
        time_from1 = ('day_sun.png',time_from) if dni==0 else ('moon_with_star.png',time_from)
        duration = str(round(time_inc*24,2))+' '+utils.resource_strings['hours_str']
        main_bird = utils.resource_strings[pancha_pakshi_birds[int(mbi)]+'_str']
        main_bird_image = pancha_pakshi_images[int(mbi)]
        main_act = utils.resource_strings[pancha_pakshi_activities[int(mai)]+'_str']
        main_act_image = pancha_pakshi_activity_images[int(mai)]
        main_act_color = pp_activity_background_colors[int(mai)]
        sub_bird = ''; sub_act = ''
        rel='';pf = ''; eff = ''; rtng = ''
        nkb = utils.resource_strings['nakshathra_pakshi_str']+' : '+utils.resource_strings[pancha_pakshi_birds[int(mbi)]+'_str']
        nkbi = pancha_pakshi_images[int(mbi)]; ppbi = pancha_pakshi_images[int(ppi)] 
        ppb = utils.resource_strings['padu_pakshi_str']+' : '+utils.resource_strings[pancha_pakshi_birds[int(ppi)]+'_str']
        bpb = utils.resource_strings['bharana_pakshi_str']+' : '+utils.resource_strings[pancha_pakshi_birds[int(bpi)]+'_str']
        bpbi = pancha_pakshi_images[int(bpi)]; kp_icon = 'shukla_paksha.png' if int(pi)==0 else  'krishna_paksha.png'
        kpstr = (utils.PAKSHA_LIST[int(pi)],kp_icon)
        wstr = (utils.DAYS_LIST[int(wdi)],'')
        tstr = (utils.resource_strings['daytime_str'],'day_sun.png') if dni==0 else (utils.resource_strings['nighttime_str'],'moon_with_star.png')
        parent_level_labels.append([kpstr,wstr,tstr,(nkb,nkbi),(ppb,ppbi),(bpb,bpbi)]) 
        tlist = [time_from1,time_to,duration,(main_bird_image,main_bird),(main_act_image,main_act,main_act_color),
                    sub_bird,sub_act,rel,pf,eff,rtng]
        top_level_list.append(tlist)
        clist = []
        for irow in range(row,row+5):
            wdi,pi,dni,mbi,mai,sbi,sai,df,reli,pf,efi,rtng,ppi,bpi = result_list[irow]
            time_inc = day_inc/24 if dni==0 else night_inc/24
            time_to_jd = time_from_jd + time_inc*df
            by,bm,bd,bfh = utils.jd_to_gregorian(time_from_jd)
            time_from = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh,use_24hour_format=True)
            by,bm,bd,bfh = utils.jd_to_gregorian(time_to_jd)
            time_to = str(by)+'-'+'{:02d}'.format(bm)+'-'+'{:02d}'.format(bd)+' '+utils.to_dms(bfh,use_24hour_format=True)
            time_from1 = ('day_sun.png',time_from) if dni==0 else ('moon_with_star.png',time_from)
            duration = str(round(df*time_inc*24*60))+' '+utils.resource_strings['minutes_str']
            sub_bird = utils.resource_strings[pancha_pakshi_birds[int(sbi)]+'_str']
            sub_bird_image = pancha_pakshi_images[int(sbi)]
            sub_act = utils.resource_strings[pancha_pakshi_activities[int(sai)]+'_str']
            sub_act_image = pancha_pakshi_activity_images[int(sai)]
            sub_act_color = pp_activity_background_colors[int(sai)]
            rel = ('',utils.resource_strings[pp_relations[int(reli)]+'_str'],pp_relation_colors[int(reli)])
            eff = ('',utils.resource_strings[pp_effect[int(efi)]+'_str'],pp_effect_colors[int(efi)])
            cll = [time_from1,time_to,duration,(main_bird_image,main_bird),(main_act_image,main_act,main_act_color),
                   (sub_bird_image,sub_bird),(sub_act_image,sub_act,sub_act_color),rel,pf,eff,rtng]
            clist.append(cll)
            time_from_jd = time_to_jd
        time_from_jd = time_to_jd
        child_level_list.append(clist)
    """
    print("headers = ",headers)
    print("parent_level_list = ",top_level_list)
    print("child_level_list = ",child_level_list)
    print("parent_level_labels = ",parent_level_labels)
    """
    return headers,top_level_list,child_level_list, parent_level_labels
if __name__ == "__main__":
    utils.set_language('ta')
    #_create_pancha_paksha_db(); exit()
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    bs = _get_birth_nakshathra(jd, place)
    paksha_index = _get_paksha(jd, place)
    bird_index = _get_birth_bird_from_nakshathra(bs,paksha_index)
    weekday_index = drik.vaara(jd)+1
    print('bird',bird_index,utils.resource_strings[pancha_pakshi_birds[bird_index-1]+'_str'])
