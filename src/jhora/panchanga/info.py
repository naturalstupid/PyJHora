#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# py -- routines for computing tithi, vara, etc.
#
# Copyright (C) 2013 Satish BD  <bdsatish@gmail.com>
# Downloaded from https://github.com/bdsatish/drik-panchanga
#
# This file is part of the "drik-panchanga" Python library
# for computing Hindu luni-solar calendar based on the Swiss ephemeris
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

# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora
"""
    This module is meant for collecting all panchang information (from drik module mostly)
    The information can be used in UI modules for display.  
    Module uses language resources and hence requires setting language using utils.set_language
"""
import sys, os
# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

import time
from jhora.panchanga import vratha, pancha_paksha
from jhora.panchanga.hijri import islamic_lunar_date, islamic_prayer_times
def _current_segment(seg, hrs):
    """ Returns [no, start, end] of the entry of seg (3 or 6 values) whose start <= hrs < end;
        the first entry if none contains hrs. """
    for i in range(0, len(seg) - 2, 3):
        if seg[i+1] <= hrs < seg[i+2]:
            return seg[i:i+3]
    return seg[:3]

def _get_tithi_dict_pair(_tithi, jd):
    """ Returns (key, display value, paksha) for a tithi() result at the birth time of jd.
        The balance (fraction of the tithi still to come) is shown next to the tithi it belongs to. """
    key = utils.resource_strings['tithi_str']
    birth_hrs = utils.jd_to_gregorian(jd)[-1]
    _tithi = _current_segment(_tithi, birth_hrs)
    frac_left = 100*utils.get_fraction(_tithi[1], _tithi[2], birth_hrs)
    frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+') '
    def _name(t):
        """ Paksha, tithi name and deity of tithi number t (1-30). """
        return (utils.PAKSHA_LIST[0 if t <= 15 else 1]+' '+utils.TITHI_LIST[t-1]+
                ' (' + utils.TITHI_DEITIES[t-1]+')')
    _tithi_index = _tithi[0]
    _paksha = 0 if _tithi_index <= 15 else 1
    next_tithi = utils.next_tithi_index(_tithi_index)
    previous_tithi = utils.next_tithi_index(_tithi_index, direction=-1)
    after = "<br>" + utils.resource_strings['after_str'] + ' '
    if _tithi[1] < 0:            # started before midnight: current tithi, its end, then the next one
        value = (_name(_tithi_index)+' '+utils.to_dms(_tithi[2])+' '+utils.resource_strings['ends_at_str']+
                 frac_str + after + _name(next_tithi))
    elif _tithi[2] > 24.0:       # started during the day, ends after midnight: previous tithi's end, then current
        value = (_name(previous_tithi)+' '+utils.to_dms(_tithi[1])+' '+utils.resource_strings['ends_at_str']+
                 after + _name(_tithi_index) + frac_str)
    else:                        # starts and ends within the day
        value = (_name(_tithi_index)+' '+utils.to_dms(_tithi[1])+' '+utils.resource_strings['starts_at_str']+
                 utils.to_dms(_tithi[2])+' '+utils.resource_strings['ends_at_str']+frac_str +
                 after + _name(next_tithi))
    return key, value, _paksha
def get_panchangam_resources_basic(jd,place,ayanamsa_mode=None):
    results_dict = {}
    utils.profiler.start("BASIC")
    try:
        if ayanamsa_mode is not None and ayanamsa_mode in const.available_ayanamsa_modes.keys():
            drik.set_ayanamsa_mode(ayanamsa_mode)
        else:
            drik.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
        jd_utc = jd - place.timezone/24.0 # V5.0 fix
        year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
        key = utils.resource_strings['calculation_type_str']
        value = utils.resource_strings[const.supported_astrology_models[const.astrology_model_default-1]+'_str']
        results_dict[key] = value
        key = utils.resource_strings['place_str']+': '; value = place.name; place_str1 = value
        _lat = utils.to_dms(float(place.latitude),is_lat_long='lat')
        _long = utils.to_dms(float(place.longitude),is_lat_long='long')
        place_str2 = ' ('+_lat+', '+_long+', '+str(place.timezone)+')'
        value += place_str2
        results_dict[key] = value
        utils.profiler.mark("setup + place formatting", "BASIC")

        key = utils.resource_strings['civil_weekday_str']+': '
        value = utils.DAYS_LIST[drik.vaara(jd,place,show_vedic_day=False)]
        results_dict[key] = value
        key = utils.resource_strings['vedic_weekday_str']+': '
        value = utils.DAYS_LIST[drik.vaara(jd,place,show_vedic_day=True)]
        results_dict[key] = value
        utils.profiler.mark("vaara x2", "BASIC")

        date_str1 = str(year)+','+str(month)+','+str(day)
        date_str2 = str(day)+'-'+utils.MONTH_SHORT_LIST_EN[month-1]+'-'+str(year)
        time_str = utils.to_dms(birth_time_hrs)
        key = utils.resource_strings['date_of_birth_str']
        value = date_str2+'  '+utils.resource_strings['time_of_birth_str']+' '+time_str
        ghati,pala,vighati = drik.vedic_time(jd, place)
        vedic_time_str = " ("+str(ghati)+" "+utils.resource_strings["ghati_str"]+": "
        vedic_time_str += str(pala)+" "+utils.resource_strings["pala_str"]+": "
        vedic_time_str += str(vighati)+" "+utils.resource_strings["vighati_str"]+")"
        results_dict[key] = value+vedic_time_str
        utils.profiler.mark("vedic_time", "BASIC")

        if const.include_islamic_calendar and utils.astro_engine_is_drik() and year > 0:
            key = utils.resource_strings['islamic_date_str']
            iy,im,id = islamic_lunar_date(jd, place)
            value = str(iy)+' '+utils.ISLAMIC_MONTH_LIST[im-1]+' '+str(id)+'*'
            results_dict[key] = value
            prayer_types = ['fajr_str','shurook_str','dhuhr_str','asr_str','maghrib_str','isha_str']
            pr_times = islamic_prayer_times(jd,place)
            for p,pt, in enumerate(pr_times):
                key = (utils.resource_strings[prayer_types[p]]+' '+utils.resource_strings['prayer_str']
                       +' '+utils.resource_strings['time_of_birth_str'] )
                value = utils.to_dms(pt)
                results_dict[key] = value
            utils.profiler.mark("islamic calendar + prayer times", "BASIC")

        _calendar_type_str = ['',' ('+utils.resource_strings['amantha_str']+')',' ('+utils.resource_strings['purnimantha_str']+')']
        keys = [utils.resource_strings['solar_str']+' '+utils.resource_strings['year_str']+'/'+utils.resource_strings['month_str'],
                utils.resource_strings['lunar_year_month_str']+_calendar_type_str[1],
                utils.resource_strings['lunar_year_month_str']+_calendar_type_str[2]]
        if const.include_islamic_calendar and utils.astro_engine_is_drik() and year > 0:
            _calendar_type_str += [' ('+utils.resource_strings['hijri_str']+')']
            keys += [utils.resource_strings['hijri_str']+' '+utils.resource_strings['year_str']+'/'+utils.resource_strings['month_str']]
        calendar_count = len(keys)
        for _calendar_type in list(const.CALENDAR_TYPE)[:calendar_count]:
            vd = drik.vedic_date(jd, place, calendar_type=_calendar_type)
            _month,_day,_year,adhik_maasa,nija_maasa, kshaya_maasa = vd
            adhik_maasa_str = ''; nija_month_str = ''
            if adhik_maasa: adhik_maasa_str = utils.resource_strings['adhika_maasa_str']
            if nija_maasa: nija_month_str = utils.resource_strings['nija_month_str']
            if kshaya_maasa: nija_month_str = utils.resource_strings['kshaya_month_str']
            if _calendar_type == const.CALENDAR_TYPE.HIJRI_ISLAMIC:
                month_str = utils.ISLAMIC_MONTH_LIST[_month-1]
                year_str = str(_year)
                day_str = str(_day)+'*'
            else:
                month_str = utils.MONTH_LIST[_month-1]
                year_str = utils.YEAR_LIST[_year]
                day_str = str(_day)
            spl_month_text = month_str+' '+ adhik_maasa_str+nija_month_str+' '+str(_day)+'*'
            key = keys[_calendar_type]
            value = year_str+' / '+month_str+' '+ \
                            adhik_maasa_str+nija_month_str+' '+day_str
            results_dict[key] = value
        utils.profiler.mark(f"vedic_date loop x{calendar_count} calendars", "BASIC")

        key = utils.resource_strings['sunrise_str']
        value = drik.sunrise(jd,place)[1]
        results_dict[key] = value
        utils.profiler.mark("sunrise", "BASIC")
        key = utils.resource_strings['sunset_str']
        value = drik.sunset(jd,place)[1]
        results_dict[key] = value
        utils.profiler.mark("sunset", "BASIC")
        key = utils.resource_strings['moonrise_str']
        value = drik.moonrise(jd, place)[1]
        results_dict[key] = value
        utils.profiler.mark("moonrise", "BASIC")
        key = utils.resource_strings['moonset_str']
        value = drik.moonset(jd, place)[1]
        results_dict[key] = value
        utils.profiler.mark("moonset", "BASIC")

        _festival_list = vratha.get_festivals_of_the_day(jd,place)
        if len(_festival_list)>0:
            key = utils.resource_strings['todays_festivals_str']; value = ''
            for row in _festival_list:
                try:
                    value += row['Festival_' + const._DEFAULT_LANGUAGE]+', '
                except:
                    value += row['Festival_en']+', '
            results_dict[key] = value
        utils.profiler.mark("get_festivals_of_the_day", "BASIC")

        key = utils.resource_strings['nakshatra_str']
        nak = drik.nakshatra(jd,place)
        frac_left = 100*utils.get_fraction(nak[2], nak[3], birth_time_hrs)
        frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
        value = utils.NAKSHATRA_LIST[nak[0]-1]+' '+  \
                    ' ('+utils.PLANET_SHORT_NAMES[utils.nakshathra_lord(nak[0])]+') '+ utils.resource_strings['paadham_str']+\
                    str(nak[1]) + ' '+ utils.to_dms(nak[3]) + ' ' + utils.resource_strings['ends_at_str']+frac_str
        results_dict[key] = value
        if nak[3] < 24:
            _next_nak = (nak[0])%27+1
            value += utils.NAKSHATRA_LIST[_next_nak-1]+' '+  \
                        ' ('+utils.PLANET_SHORT_NAMES[utils.nakshathra_lord(_next_nak)]+') '+ \
                        ' '+ utils.to_dms(nak[3]) + ' ' + utils.resource_strings['starts_at_str']
            results_dict[key] = value
        utils.profiler.mark("nakshatra", "BASIC")

        key = utils.resource_strings['raasi_str']
        rasi = drik.raasi(jd,place)
        frac_left = rasi[2]*100
        frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
        value = utils.RAASI_LIST[rasi[0]-1]+' '+utils.to_dms(rasi[1])+ ' ' + utils.resource_strings['ends_at_str']+frac_str
        results_dict[key] = value
        if rasi[1] < 24:
            _next_rasi = (rasi[0])%12+1
            value += '\n'+utils.RAASI_LIST[_next_rasi-1]+' '+utils.to_dms(rasi[1])+ ' ' + utils.resource_strings['starts_at_str']
            results_dict[key] = value
        utils.profiler.mark("raasi", "BASIC")

        key = utils.resource_strings['solar_str']+' '+utils.resource_strings['raasi_str']
        sun_long = drik.solar_longitude(jd_utc, place)
        sun_raasi = drik.dasavarga_from_long(sun_long)
        value = utils.RAASI_LIST[sun_raasi[0]] +' ' + utils.to_dms(sun_raasi[1],is_lat_long='plong')
        results_dict[key] = value
        utils.profiler.mark("solar_longitude + dasavarga_from_long", "BASIC")

        key = utils.resource_strings['tithi_str']
        _tithi = drik.tithi(jd, place)
        key,value,_paksha = _get_tithi_dict_pair(_tithi,jd)
        results_dict[key] = value
        utils.profiler.mark("tithi", "BASIC")

        key = utils.resource_strings['yogam_str']
        _yogam = drik.yogam(jd,place)
        def _yoga_name(n):
            """ Yogam name (1-27) with its lord / avayogi. """
            lords = const.yogam_lords_and_avayogis[n-1]
            return (utils.YOGAM_LIST[n-1] + ' (' + utils.PLANET_SHORT_NAMES[lords[0]] + '/' +
                    utils.PLANET_SHORT_NAMES[lords[1]] + ') ')
        frac_left = 100*_yogam[3]
        frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
        value = (_yoga_name(_yogam[0]) + '  ' + utils.to_dms(_yogam[2]) + ' ' +
                 utils.resource_strings['ends_at_str'] + frac_str)
        if len(_yogam) > 4:      # next yogam starts before midnight
            value += ('<br>' + _yoga_name(_yogam[4]) + '  ' + utils.to_dms(_yogam[5]) + ' ' +
                      utils.resource_strings['starts_at_str'])
        results_dict[key] = value
        utils.profiler.mark("yogam", "BASIC")

        key = utils.resource_strings['karanam_str']
        karanam = drik.karana(jd,place)
        def _karana_name(n):
            """ Karana name (1-60) with its lord. """
            return utils.KARANA_LIST[n-1] + ' (' + utils.PLANET_SHORT_NAMES[utils.karana_lord(n)] + ') '
        frac_left = 100*utils.get_fraction(karanam[1], karanam[2], birth_time_hrs)
        frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
        value = (_karana_name(karanam[0]) + utils.to_dms(karanam[1]) + ' ' +
                 utils.resource_strings['starts_at_str'] + ' ' + utils.to_dms(karanam[2]) + ' ' +
                 utils.resource_strings['ends_at_str'] + frac_str)
        if karanam[2] < 24:     # next karana starts before midnight
            value += ('<br>' + _karana_name(karanam[0] % 60 + 1) + utils.to_dms(karanam[2]) + ' ' +
                      utils.resource_strings['starts_at_str'])
        results_dict[key] = value
        utils.profiler.mark("karana", "BASIC")
        
        key = utils.resource_strings['raahu_kaalam_str']
        _raahu_kaalam = drik.raahu_kaalam(jd,place)
        value = _raahu_kaalam[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ _raahu_kaalam[1]+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("raahu_kaalam", "BASIC")
        kuligai = drik.gulikai_kaalam(jd,place)
        key = utils.resource_strings['kuligai_str']
        value = kuligai[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ kuligai[1]+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("gulikai_kaalam", "BASIC")
        yamagandam = drik.yamaganda_kaalam(jd,place)
        key = utils.resource_strings['yamagandam_str']
        value = yamagandam[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ yamagandam[1]+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("yamaganda_kaalam", "BASIC")

        car,ca_jd = drik.chandrashtama(jd, place); key = utils.resource_strings['chandrashtamam_str']
        value = utils.RAASI_LIST[car-1]+' '+utils.julian_day_to_date_time_string(ca_jd)+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("chandrashtama", "BASIC")

        abhijit = drik.abhijit_muhurta(jd,place)
        key = utils.resource_strings['abhijit_str']
        value = abhijit[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ abhijit[1]+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("abhijit_muhurta", "BASIC")

        _dhurmuhurtham = drik.durmuhurtam(jd,place)
        key = utils.resource_strings['dhurmuhurtham_str']
        value = _dhurmuhurtham[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ _dhurmuhurtham[1]+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("durmuhurtam", "BASIC")

        nm = drik.nishita_muhurtha(jd, place)
        key = utils.resource_strings['nishitha_muhurtha_str']+' : '
        value = utils.to_dms(nm[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("nishita_muhurtha", "BASIC")

        y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob=utils.to_dms(fh,as_string=False)
        scd = drik.sahasra_chandrodayam(jd, place)
        if scd is not None:
            key = utils.resource_strings['sahasra_chandrodhayam_str']+' '+utils.resource_strings['day_str']
            value = str(scd[0])+'-'+'{:02d}'.format(scd[1])+'-'+'{:02d}'.format(scd[2])
            results_dict[key] = value
        utils.profiler.mark("sahasra_chandrodayam", "BASIC")

        ag = drik.amrita_gadiya(jd, place)
        key = utils.resource_strings['amritha_gadiya_str']
        value = utils.to_dms(ag[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(ag[1])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("amrita_gadiya", "BASIC")

        ag = drik.varjyam(jd, place)
        key = utils.resource_strings['varjyam_str']
        value = utils.to_dms(ag[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(ag[1])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        if len(ag)>2:
            value += '\t'+utils.to_dms(ag[2])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(ag[3])+' '+utils.resource_strings['ends_at_str']
        utils.profiler.mark("varjyam", "BASIC")

        ay = drik.anandhaadhi_yoga(jd, place)
        key = utils.resource_strings['anandhaadhi_yoga_str']
        value = utils.resource_strings['ay_'+const.anandhaadhi_yoga_names[ay[0]]+'_str']+' '+utils.to_dms(ay[1])+' '+utils.resource_strings['starts_at_str']
        results_dict[key] = value
        utils.profiler.mark("anandhaadhi_yoga", "BASIC")

        key = utils.resource_strings['day_length_str']
        _day_length = drik.day_length(jd, place)
        value = utils.to_dms(_day_length).replace(' AM','').replace(' PM','')+' '+utils.resource_strings['hours_str']
        results_dict[key] = value
        utils.profiler.mark("day_length", "BASIC")
        key = utils.resource_strings['night_length_str']
        _night_length = drik.night_length(jd, place)
        value = utils.to_dms(_night_length).replace(' AM','').replace(' PM','')+' '+utils.resource_strings['hours_str']
        results_dict[key] = value
        utils.profiler.mark("night_length", "BASIC")

        key = utils.resource_strings['present_str']+' '+utils.resource_strings['triguna_str']
        tg = drik.triguna(jd, place)
        value = utils.resource_strings[const.triguna_names[tg[0]]+'_str']
        value += '\t'+utils.to_dms(tg[1])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(tg[2])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("triguna", "BASIC")

        key = utils.resource_strings['present_str']+' '+utils.resource_strings['vivaha_chakra_palan']+' :'
        value = drik.vivaha_chakra_palan(jd, place)
        value = utils.resource_strings['vivaha_chakra_palan_'+str(value)]
        results_dict[key] = value
        utils.profiler.mark("vivaha_chakra_palan", "BASIC")

        key = utils.resource_strings['tamil_yogam_str']+' : '
        tg = drik.tamil_yogam(jd, place)
        value = utils.resource_strings[const.tamil_yoga_names[tg[0]]+'_yogam_str']
        value += ' ('+utils.resource_strings[const.tamil_yoga_names[tg[3]]+'_yogam_str']+')' if len(tg)>3 and tg[0] != tg[3] else ''
        value += '\t'+utils.to_dms(tg[1])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(tg[2])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("tamil_yogam", "BASIC")

        value = drik.pushkara_yoga(jd, place)
        if len(value)>0:
            key = utils.resource_strings['dwi_pushkara_yoga_str'] if value[0]==1 else utils.resource_strings['tri_pushkara_yoga_str']
            value = utils.to_dms(value[1])+' '+utils.resource_strings['starts_at_str']
            results_dict[key] = value
        utils.profiler.mark("pushkara_yoga", "BASIC")

        value = drik.aadal_yoga(jd, place)
        if len(value)>0:
            key = utils.resource_strings['aadal_yoga_str']
            value = utils.to_dms(value[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(value[1])+' '+utils.resource_strings['ends_at_str']
            results_dict[key] = value
        utils.profiler.mark("aadal_yoga", "BASIC")

        value = drik.vidaal_yoga(jd, place)
        if len(value)>0:
            key = utils.resource_strings['vidaal_yoga_str']
            value = utils.to_dms(value[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(value[1])+' '+utils.resource_strings['ends_at_str']
            results_dict[key] = value
        utils.profiler.mark("vidaal_yoga", "BASIC")

        key = utils.resource_strings['shiva_vaasa_str']
        sv = drik.shiva_vaasa(jd, place)
        value = utils.resource_strings['shiva_vaasa_str'+str(sv[0])]+' '+utils.to_dms(sv[1])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("shiva_vaasa", "BASIC")

        key = utils.resource_strings['agni_vaasa_str']
        av = drik.agni_vaasa(jd, place)
        value = utils.resource_strings['agni_vaasa_str'+str(av[0])]+' '+utils.to_dms(av[1])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
        utils.profiler.mark("agni_vaasa", "BASIC")

        directions = ['east','south','west','north','south_west','north_west','north_east','south_east']
        yv = drik.yogini_vaasa(jd, place)
        key = utils.resource_strings['yogini_vaasa_str']; value = utils.resource_strings[directions[yv]+'_str']
        results_dict[key] = value
        utils.profiler.mark("yogini_vaasa", "BASIC")

        ds = drik.disha_shool(jd,place)
        key = utils.resource_strings['disha_shool_str']; value = utils.resource_strings[directions[ds]+'_str']
        results_dict[key] = value
        utils.profiler.mark("disha_shool", "BASIC")

        car,ca_jd = drik.chandrashtama(jd, place); key = utils.resource_strings['chandrashtamam_str']
        value = utils.RAASI_LIST[car-1]+' '+utils.julian_day_to_date_time_string(ca_jd)+' '+utils.resource_strings['ends_at_str']
        utils.profiler.mark("chandrashtama (2nd redundant call)", "BASIC")

        key = utils.resource_strings['ayanamsam_str']+' ('+const._DEFAULT_AYANAMSA_MODE+') '
        value = drik.get_ayanamsa_value(jd, place)
        value = utils.to_dms(value,as_string=True,is_lat_long='lat').replace('N','').replace('S','')
        results_dict[key] = value
        utils.profiler.mark("get_ayanamsa_value", "BASIC")

        paksha_index = _paksha+1
        bird_index = pancha_paksha._get_birth_bird_from_nakshathra(nak[0],paksha_index)
        key = utils.resource_strings['pancha_pakshi_sastra_str']+' '+utils.resource_strings['main_bird_str'].replace('\\n',' ')+' : '
        value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
        results_dict[key] = value
        utils.profiler.mark("pancha_paksha bird", "BASIC")

        [kali_year, vikrama_year,saka_year] = drik.elapsed_year(jd,_month)
        key = utils.resource_strings['kali_year_str']
        value = str(kali_year)
        results_dict[key] = value
        key = utils.resource_strings['vikrama_year_str']
        value = str(vikrama_year)
        results_dict[key] = value
        key = utils.resource_strings['saka_year_str']; value = str(saka_year)
        results_dict[key] = value
        utils.profiler.mark("elapsed_year", "BASIC")

        key = utils.resource_strings['kali_ahargana_str']
        value = str(drik.kali_ahargana_days(jd, place))+' '+utils.resource_strings['days_str']
        results_dict[key] = value
        utils.profiler.mark("kali_ahargana_days", "BASIC")

        utils.profiler.end("BASIC")
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources_basic: An error occurred: {e}",'line number',tb.tb_lineno)
        return results_dict

def get_panchangam_resources_special_tithis(jd,place):
    try:
        results_dict = {}
        year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
        st = drik.special_tithis(jd,place)[:12]
        for t in range(1,13):
            _tithi_returned = st[0][t-1]
            frac_left = 100*utils.get_fraction(_tithi_returned[1], _tithi_returned[2], birth_time_hrs)
            frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
            _paksha = 0 if _tithi_returned[0]<=15 else 1
            key = utils.resource_strings[const.special_tithis[t-1]+'_tithi_str']
            _deity_str= ' (' + utils.TITHI_DEITIES[_tithi_returned[0]-1]+') '
            from_str = utils.to_dms(_tithi_returned[1])+' '+utils.resource_strings['starts_at_str']
            end_str = utils.to_dms(_tithi_returned[2])+' '+utils.resource_strings['ends_at_str']
            value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi_returned[0]-1]
            value += _deity_str+from_str+' '+end_str+' '+frac_str
            results_dict[key] = value
            if _tithi_returned[2] < 24:
                _paksha = 0
                if (_tithi_returned[0])%30+1 > 15: _paksha = 1 # V3.1.1
                value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[(_tithi_returned[0])%30]+ \
                                ' (' + utils.TITHI_DEITIES[(_tithi_returned[0])%30]+') '+ \
                                utils.to_dms(_tithi_returned[2])+ ' ' + utils.resource_strings['starts_at_str']
                results_dict[key] = value
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources_special_tithis: An error occurred: {e}",'line number',tb.tb_lineno)
        return results_dict
def get_panchangam_resources_gowri(jd,place):
    try:
        results_dict = {}
        year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
        results_dict[utils.resource_strings['daytime_str']+' '+utils.resource_strings['gauri_choghadiya_str']+':']=''
        gc = drik.gauri_choghadiya(jd, place)
        _gc_types = ['gc_udvega_str','gc_chara_str','gc_laabha_str','gc_amrit_str','gc_kaala_str','gc_shubha_str','gc_roga_str']
        yaama_types = ['purvaanha_str','madhyannha_str','aparanha_str','saayankaala_str','pradosha_str','nishitha_str','triyaama_str',
                       'ushaa_str'] # V4.8.5
        yt = 0
        for g,(gt,st,et) in enumerate(gc):
            if g==8: # V4.3.6
                results_dict[utils.resource_strings['nighttime_str']+' '+utils.resource_strings['gauri_choghadiya_str']+':']=''
            key = '('+str(g+1)+') '+utils.resource_strings[_gc_types[gt]]
            value = st +' '+utils.resource_strings['starts_at_str']+ ' '+ et + ' '+ utils.resource_strings['ends_at_str']
            if g%2 == 0: # V4.8.5
                value += " ("+utils.resource_strings[yaama_types[yt]]+')'
                yt += 1
            results_dict[key]=value
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources_gowri: An error occurred: {e}",'line number',tb.tb_lineno)
        return results_dict
def get_panchangam_resources_muhurtham(jd,place):
    try:
        results_dict = {}
        year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
        results_dict[utils.resource_strings['daytime_str']+' '+utils.resource_strings['muhurtha_str']+':']=''
        mh = drik.muhurthas(jd, place)
        for mi,(mn,ma,(ms,me)) in enumerate(mh):
            if mi==15: results_dict[utils.resource_strings['nighttime_str']+' '+utils.resource_strings['muhurtha_str']+':']=''
            key = '('+str(mi+1)+') '+utils.resource_strings['muhurtha_'+mn+'_str']+ ' ('
            key += utils.resource_strings['auspicious_str'] if ma==1 else utils.resource_strings["inauspicious_str"]
            key += ') '
            value = utils.to_dms(ms)+' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(me) + ' '+ utils.resource_strings['ends_at_str']
            results_dict[key]=value
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources_muhurtham: An error occurred: {e}",'line number',tb.tb_lineno)
        return results_dict
def get_panchangam_resources_horai(jd,place):
    try:
        results_dict = {}
        year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
        results_dict[utils.resource_strings['daytime_str']+' '+utils.resource_strings['shubha_hora_str']+':']=''
        gc = drik.shubha_hora(jd, place)
        for g,(gt,st,et) in enumerate(gc):
            #if g == 12: break
            if g==12: results_dict[utils.resource_strings['nighttime_str']+' '+utils.resource_strings['shubha_hora_str']+':']=''
            key = '('+str(g+1)+') '+utils.PLANET_NAMES[gt]+' '+utils.resource_strings['shubha_hora_'+str(gt)]
            value = st +' '+utils.resource_strings['starts_at_str']+ ' '+ et + ' '+ utils.resource_strings['ends_at_str']
            results_dict[key]=value
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources_horai: An error occurred: {e}",'line number',tb.tb_lineno)
        return results_dict
def get_panchangam_resources_misc(jd,place):
    try:
        results_dict = {}
        year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
        bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
        pr = drik.panchaka_rahitha(jd, place)
        panchaka_lines = []
        for prc, pr_beg, pr_end in pr:
            if prc == 0:
                # Wrap the good status in green color HTML tags
                key = f"<span style='color: green;'>{utils.resource_strings['panchaka_rahitha_str']} ({utils.resource_strings['good_str']})</span>"
            else:
                # Wrap the bad status flaws in red color HTML tags
                status_text = utils.resource_strings[bad_panchakas[prc] + '_panchaka_str']
                key = f"<span style='color: red;'>{status_text}</span>"
            value1 = utils.to_dms(pr_beg) + ' ' + utils.resource_strings['starts_at_str']
            value2 = utils.to_dms(pr_end) + ' ' + utils.resource_strings['ends_at_str']
            # Build each row safely as a flat HTML string snippet
            panchaka_lines.append(f"<b>{key}</b>: {value1} {value2}")
        # Join them using a valid HTML line break tag so it renders cleanly as a plain string in your UI engine
        _panch_key = key = f"<span style='color: green;'>{utils.resource_strings['panchaka_rahitha_str']}</span>"
        results_dict[f"<b>{_panch_key}</b>" + ' :<br>'] = "<br>".join(panchaka_lines)

        tb = drik.thaaraabalam(jd, place, return_only_good_stars=True)
        key = utils.resource_strings['thaaraabalam_str']+' :'
        star_list = [utils.NAKSHATRA_LIST[t-1] for t in tb]; knt=6
        star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
        value = ''
        for sl in star_list:
            value += sl
        results_dict[key] = value # V4.8.5
        cb = drik.chandrabalam(jd, place)
        key = utils.resource_strings['chandrabalam_str']+' :'
        star_list = [utils.RAASI_LIST[t-1] for t in cb]; knt=5
        star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
        value = ''
        for sl in star_list:
            value += sl
        results_dict[key] = value # V4.8.5
        bm = drik.brahma_muhurtha(jd, place)
        key = utils.resource_strings['brahma_str']+' '+utils.resource_strings['muhurtha_str']+' : '
        value = utils.to_dms(bm[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(bm[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        bm = drik.godhuli_muhurtha(jd, place)
        key = utils.resource_strings['godhuli_muhurtha_str']+' : '
        value = utils.to_dms(bm[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(bm[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        ps,ms,ss = drik.sandhya_periods(jd, place)
        key = utils.resource_strings['pratah_sandhya_kaalam_str']+' : '
        value = utils.to_dms(ps[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(ps[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        key = utils.resource_strings['madhyaahna_sandhya_kaalam_str']+' : '
        value = utils.to_dms(ms[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(ms[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        key = utils.resource_strings['saayam_sandhya_kaalam_str']+' : '
        value = utils.to_dms(ss[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(ss[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        nm = drik.nishita_kaala(jd, place)
        key = utils.resource_strings['nishitha_kaala_str']+' : '
        value = utils.to_dms(nm[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key] = value
        ulm = drik.udhaya_lagna_muhurtha(jd, place)
        results_dict[utils.resource_strings['udhaya_lagna_str']+':']=''
        for ulr,ulb,ule in ulm:
            key = utils.RAASI_LIST[ulr]+' : '
            ulb_str = utils.to_dms(ulb); ule_str=utils.to_dms(ule)
            value = ulb_str +' '+utils.resource_strings['starts_at_str']+ ' '+ ule_str + ' '+ utils.resource_strings['ends_at_str']
            results_dict[key] = value
        bs = pancha_paksha._get_birth_nakshathra(jd, place)
        paksha_index = pancha_paksha._get_paksha(jd, place)
        bird_index = pancha_paksha._get_birth_bird_from_nakshathra(bs,paksha_index)
        key = utils.resource_strings['pancha_pakshi_sastra_str']+' '+utils.resource_strings['main_bird_str'].replace('\\n',' ')+' : '
        value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
        results_dict[key] = value
        key = utils.resource_strings['karaka_str']+' '+utils.resource_strings['tithi_str']
        kt = drik.karaka_tithi(jd, place)
        _paksha = utils.PAKSHA_LIST[0] if kt[0]-1 <15 else utils.PAKSHA_LIST[1]
        value = _paksha +' '+utils.TITHI_LIST[kt[0]-1] + ' (' + utils.TITHI_DEITIES[kt[0]-1]+')'
        results_dict[key] = value
        key = utils.resource_strings['karaka_str']+' '+utils.resource_strings['yogam_str']
        ky = drik.karaka_yogam(jd, place)
        value = utils.YOGAM_LIST[ky[0]-1] + ' (' + utils.TITHI_DEITIES[ky[0]-1]+')'
        results_dict[key] = value
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources_misc: An error occurred: {e}",'line number',tb.tb_lineno)
        # IMPORTANT: return whatever was successfully computed so far instead
        # of implicitly returning None. The caller (get_panchangam_resources)
        # does results_dict.update(get_panchangam_resources_misc(...)) --
        # updating with None raises "'NoneType' object is not iterable",
        # which in turn causes get_panchangam_resources itself to also return
        # None, which then breaks Panchangam.update_panchangam_info() with
        # "'NoneType' object has no attribute 'items'". Returning a (possibly
        # partial) dict here breaks that whole cascade of unrelated-looking
        # downstream errors.
        return results_dict
def get_panchangam_resources(jd,place,resource_type=None,ayanamsa_mode=None,engine_model=None):
    results_dict = {}  # moved before try (see module docstring above)
    try:
        utils.profiler.start("GPR")
        if ayanamsa_mode is not None and ayanamsa_mode in const.available_ayanamsa_modes.keys():
            drik.set_ayanamsa_mode(ayanamsa_mode)
        else:
            drik.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
        drik.set_planet_list()
        if not isinstance(resource_type, list): resource_type = [resource_type]

        if any(map(lambda v: v in [0,None,1], resource_type)):
            results_dict.update(get_panchangam_resources_basic(jd,place))
            utils.profiler.mark("#1 get_panchangam_resources_basic", "GPR")

        if any(map(lambda v: v in [0,None,2], resource_type)):
            results_dict.update(get_panchangam_resources_special_tithis(jd,place))
            utils.profiler.mark("#2 get_panchangam_resources_special_tithis", "GPR")

        if any(map(lambda v: v in [0,None,3], resource_type)):
            results_dict.update(get_panchangam_resources_gowri(jd,place))
            utils.profiler.mark("#3 get_panchangam_resources_gowri", "GPR")

        if any(map(lambda v: v in [0,None,4], resource_type)):
            results_dict.update(get_panchangam_resources_muhurtham(jd,place))
            utils.profiler.mark("#4 get_panchangam_resources_muhurtham", "GPR")

        if any(map(lambda v: v in [0,None,5], resource_type)):
            results_dict.update(get_panchangam_resources_horai(jd,place))
            utils.profiler.mark("#5 get_panchangam_resources_horai", "GPR")

        if any(map(lambda v: v in [0,None,6], resource_type)):
            results_dict.update(get_panchangam_resources_misc(jd,place))
            utils.profiler.mark("#6 get_panchangam_resources_misc", "GPR")

        utils.profiler.end("GPR")
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources: An error occurred: {e}",'line number',tb.tb_lineno)
        return results_dict
    
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1964,12,7); tob = (7,42,8)
    #dob = drik.Date(1996,12,7); tob = (10,34,8)
    place = drik.Place('Hyderabad',17.3871,78.4916,5.5)
    #place = drik.Place('Chennai, India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob,tob)
    pb = get_panchangam_resources_basic(jd, place)
    