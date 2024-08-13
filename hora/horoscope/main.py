#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# py -- routines for computing tithi, vara, etc.
#
# Copyright (C) Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/pyhoroscope
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
"""
    TODO: Check use of julian_day vs julian_years if used consistently
    For example: Special Lagna/Ascendant Calculations require jd_years or years/months/60hrs and new tob
"""
"""
    TODO: When selecting Janma, Annual, Tithi Pravesha - which TABS should it be applied and which ones not
    For example only charts? Dhasa Bhukthi as well, how about other TABS line dosha, compatibility etc
    Which TABS should always be based on NATAL CHART?
"""
import swisseph as swe
from datetime import date
from hora import const, utils
from hora.panchanga import drik, surya_sidhantha
from hora.horoscope.chart import house,charts
from attr.filters import include
_lang_path = const._LANGUAGE_PATH
chara_karakas = ['atma_karaka','amatya_karaka','bhratri_karaka','maitri_karaka','pitri_karaka','putra_karaka','jnaati_karaka','data_karaka']

dhasavarga_dict = {}
class Horoscope():  
    def __init__(self,place_with_country_code:str=None,latitude:float=None,longitude:float=None,timezone_offset:float=None,
                 date_in:drik.Date=None,birth_time:str=None,ayanamsa_mode:str="TRUE_CITRA",ayanamsa_value:float=None,
                 calculation_type:str='drik',years=1,months=1,sixty_hours=1,pravesha_type=0,language='en'):
        self._language = language
        utils.set_language(language)
        self.cal_key_list = utils.resource_strings
        self.place_name = place_with_country_code
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_offset = timezone_offset
        self.Date = date_in
        self.birth_time = birth_time
        self.pravesha_type = pravesha_type
        #self.ayanamsa_mode = ayanamsa_mode
        #self.ayanamsa_value = ayanamsa_value
        #print(self.place_name,self.latitude,self.longitude,self.timezone_offset)
        if self.place_name == None:
            if self.latitude==None or self.longitude==None or self.timezone_offset==None:
                print('Please provide either place_with_country_code or combination of latitude and longitude ...\n Aborting script')
                exit()
            else:
                self.place_name = 'Not Provided'
                self.latitude = latitude
                self.longitude = longitude
                self.timezone_offset = timezone_offset                
        else:
            if self.latitude==None or self.longitude==None or self.timezone_offset==None:
                [_,self.latitude,self.longitude,self.timezone_offset] = \
                    utils.get_location_using_nominatim(place_with_country_code)
                
                
        if date_in==None:
            self.Date = drik.Date(date.today().year,date.today().month,date.today().day)
        else:
            self.Date = drik.Date(date_in.year,date_in.month,date_in.day)
        self.Place = drik.Place(self.place_name,self.latitude,self.longitude,self.timezone_offset)
        self.julian_utc = drik.gregorian_to_jd(self.Date)
        #self.timezone_offset = drik.get_place_timezone_offset(self.latitude,self.longitude)
        if (birth_time!=None):
            birth_time = birth_time.strip().replace('AM','').replace('PM','')
            btArr = birth_time.split(':')
            self.julian_day = swe.julday(self.Date.year,self.Date.month,self.Date.day, int(btArr[0])+int(btArr[1])/60)
            self.birth_time = (int(btArr[0]),int(btArr[1]),0)
            if (len(btArr)==3):
                self.julian_day = swe.julday(self.Date.year,self.Date.month,self.Date.day, int(btArr[0])+int(btArr[1])/60+int(btArr[2])/3600)
                self.birth_time = (int(btArr[0]),int(btArr[1]),int(btArr[2]))                
        else:
            self.julian_day = drik.gregorian_to_jd(self.Date)
        # Set Ayanamsa Mode
        if calculation_type not in const.available_horoscope_calculation_methods:
            print('calculation type',calculation_type,' not in list of available calculation methods',const.available_horoscope_calculation_methods,'Default:drik is used')
            calculation_type = 'drik'
        self.calculation_type = calculation_type.lower()
        self.ayanamsa_mode = ayanamsa_mode.upper()
        """ Force Surya sidhantha ayanamsa for SS calculation type"""
        if self.calculation_type == 'ss':
            print('Horoscope:main: Forcing ayanamsa to SURYASIDDHANTA for the SURYA SIDDHANTA calculation type')
            drik.set_ayanamsa_mode('SURYASIDDHANTA')
            self.ayanamsa_mode = 'SURYASIDDHANTA'
        #print('horoscope setting ayanamsa',key,self.ayanamsa_value,self.julian_day)
        drik.set_ayanamsa_mode(ayanamsa_mode,ayanamsa_value,self.julian_day)
        self.ayanamsa_value = drik.get_ayanamsa_value(self.julian_day)
        self.years = years; self.months=months; self.sixty_hours=sixty_hours
        place = drik.Place(self.place_name,self.latitude,self.longitude,self.timezone_offset)
        self.julian_years = drik.next_solar_date(self.julian_day, place, years, months, sixty_hours)
        self.julian_years_utc = utils.julian_day_utc(self.julian_day,self.Place)
        self.calendar_info = self.get_calendar_information()# language)
        ret = self.get_horoscope_information()#language)
        self.horoscope_info = ret[0]; self.horoscope_charts=ret[1]
        #print('Horoscope',self.Date,self.birth_time,years,months,sixty_hours)
        return
    def _get_planet_list(self):
        return utils.PLANET_NAMES,utils.PLANET_SHORT_NAMES
    def _get_raasi_list(self):
        return utils.RAASI_LIST,utils.RAASI_SHORT_LIST
    def _get_calendar_resource_strings(self):#, language='en'):
        list_file = _lang_path + 'list_values_'+self._language+'.txt'
        msg_file = _lang_path + 'msg_strings_'+self._language+'.txt'
        cal_key_list=utils._read_resource_messages_from_file(msg_file) #utils.get_resource_messages(msg_file)
        _ = utils._read_resource_lists_from_file(list_file)#utils.get_resource_lists(list_file)
        return cal_key_list
    def get_calendar_information(self):#, language='en'):
        jd = self.julian_utc # self.julian_day #jd = self.julian_years #
        place = drik.Place(self.place_name,self.latitude,self.longitude,self.timezone_offset)
        #utils.set_language(language)
        cal_key_list = utils.resource_strings
        self.cal_key_list = cal_key_list
        self._ascendant_str = cal_key_list['ascendant_str']
        as_string = True
        calendar_info = {
            cal_key_list['place_str'] : self.place_name,
            cal_key_list['latitude_str'] : utils.to_dms(self.latitude,is_lat_long='lat',as_string=as_string), #"{0:.2f}".format(self.latitude),
            cal_key_list['longitude_str'] : utils.to_dms(self.longitude,is_lat_long='long',as_string=as_string), # "{0:.2f}".format(self.longitude),
            cal_key_list['timezone_offset_str'] : "{0:.2f}".format(self.timezone_offset),
            cal_key_list['report_date_str'] : "{0:d}-{1:d}-{2:d}".format(self.Date.year,self.Date.month,self.Date.day)#self.Date.isoformat(),         
        }
        vaaram = drik.vaara(jd)
        calendar_info[cal_key_list['vaaram_str']]=utils.DAYS_LIST[vaaram]
        calendar_info[cal_key_list['calculation_type_str']]=cal_key_list['drik_panchang_str']
        if self.calculation_type.lower()=='ss':
            calendar_info[cal_key_list['calculation_type_str']]=cal_key_list['ss_panchang_str']
        jd = self.julian_years #jd = self.julian_day
        maasam_no,adhik_maasa,nija_maasa = drik.lunar_month(jd,place)
        """ Check if current month is Nija Maasa """
        nija_month_str = ''
        if nija_maasa:
            nija_month_str = cal_key_list['nija_month_str']
        _tithi = drik.tithi(self.julian_utc,place)
        #print('tithi',_tithi)
        _paksha = 0
        if _tithi[0] > 15: _paksha = 1 # V3.1.1
        """ Lunar Day is nothing but tithi number """
        #day_no = _tithi[0]
        """ Tamil Calendar gives solar day """
        tm,td = drik.tamil_solar_month_and_date(self.Date, place)
        #maasam = utils.MONTH_LIST[maasam_no-1]
        adhik_maasa_str = ''; 
        if adhik_maasa:
            adhik_maasa_str = cal_key_list['adhika_maasa_str']
        _samvatsara = drik.samvatsara(self.Date, place, maasam_no, zodiac=0)
        calendar_info[cal_key_list['lunar_year_month_str']]=utils.YEAR_LIST[_samvatsara-1]+' / '+utils.MONTH_LIST[maasam_no-1]+' '+adhik_maasa_str+nija_month_str
        #calendar_info[cal_key_list['maasa_str']] = maasam +' '+adhik_maasa_str+" "+cal_key_list['date_str']+' '+str(day_no)
        calendar_info[cal_key_list['tamil_month_str']] = utils.MONTH_LIST[tm] +" "+cal_key_list['date_str']+' '+str(td)
        [kali_year, vikrama_year,saka_year] = drik.elapsed_year(jd,maasam_no)
        calendar_info[cal_key_list['kali_year_str']] = kali_year
        calendar_info[cal_key_list['vikrama_year_str']] = vikrama_year
        calendar_info[cal_key_list['saka_year_str']] = saka_year
        #_samvatsara = drik._samvatsara_old(jd,maasam_no)
        #calendar_info[cal_key_list['samvatsara_str']] = utils.YEAR_LIST[_samvatsara-1]
        sun_rise = drik.sunrise(self.julian_utc,place)
        calendar_info[cal_key_list['sunrise_str']] = sun_rise[1]
        sun_set = drik.sunset(self.julian_utc,place)
        calendar_info[cal_key_list['sunset_str']] = sun_set[1]
        moon_rise = drik.moonrise(self.julian_utc,place)[1]
        calendar_info[cal_key_list['moonrise_str']] = moon_rise
        moon_set = drik.moonset(self.julian_utc,place)[1]
        calendar_info[cal_key_list['moonset_str']] = moon_set
        """ for tithi at sun rise time - use Julian UTC  """
        jd = self.julian_day # 2.0.3
        _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
        frac_left = 100*utils.get_fraction(_tithi[1], _tithi[2], birth_time_hrs)
        #print('tithi start',_tithi[1],'end',_tithi[2],'fraction',frac_left)
        calendar_info[cal_key_list['tithi_str']]= utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi[0]-1]+' '+ \
                        utils.to_dms(_tithi[1])+ ' ' + cal_key_list['starts_at_str'] + ' ' + \
                        utils.to_dms(_tithi[2])+ ' ' + cal_key_list['ends_at_str']+' ('+"{0:.2f}".format(frac_left)+'% ' + \
                        cal_key_list['remaining_str']+' )'
        rasi = drik.raasi(jd,place)
        frac_left = rasi[2]*100
        calendar_info[cal_key_list['raasi_str']] = utils.RAASI_LIST[rasi[0]-1]+' '+rasi[1]+ ' ' + \
                    cal_key_list['ends_at_str'] +' ('+"{0:.2f}".format(frac_left)+'% ' + \
                    cal_key_list['remaining_str']+' )'
        nak = drik.nakshatra(jd,place)
        frac_left = 100*utils.get_fraction(nak[2],nak[3],birth_time_hrs)
        #print('nakshatra',nak)
        calendar_info[cal_key_list['nakshatra_str']] = utils.NAKSHATRA_LIST[nak[0]-1]+' '+ cal_key_list['paadham_str']+ \
                    str(nak[1]) + ' '+ utils.to_dms(nak[2]) + ' '+ cal_key_list['starts_at_str'] + ' ' + \
                    utils.to_dms(nak[3]) + ' ' + cal_key_list['ends_at_str'] + \
                    ' ('+"{0:.2f}".format(frac_left)+'% ' + cal_key_list['remaining_str']+' )'
        results =drik.nakshatra(jd,place)
        self._nakshatra_number, self._paadha_number = results[0],results[1]
        """ # For kaalam, yogam use sunrise time """
        jd = self.julian_utc #jd = self.julian_years_utc # 
        _raahu_kaalam = drik.raahu_kaalam(jd,place)
        calendar_info[cal_key_list['raahu_kaalam_str']] = _raahu_kaalam[0] + ' ' + _raahu_kaalam[1]+' '+cal_key_list['ends_at_str']
        kuligai = drik.gulikai_kaalam(jd,place)
        calendar_info[cal_key_list['kuligai_str']] = kuligai
        yamagandam = drik.yamaganda_kaalam(jd,place)
        calendar_info[cal_key_list['yamagandam_str']] = yamagandam
        yogam = drik.yogam(jd,place)
        frac_left = 100*utils.get_fraction(yogam[1], yogam[2], birth_time_hrs)
        calendar_info[cal_key_list['yogam_str']] = utils.YOGAM_LIST[yogam[0]-1] + '  '+utils.to_dms(yogam[1])+ ' ' +\
                        cal_key_list['starts_at_str'] + ' ' + utils.to_dms(yogam[2])+ ' ' + \
                        cal_key_list['ends_at_str']+' ('+"{0:.2f}".format(frac_left)+'% ' + cal_key_list['remaining_str']+' )'

        karanam = drik.karana(jd,place); frac_left= 100*utils.get_fraction(karanam[1], karanam[2], birth_time_hrs)
        calendar_info[cal_key_list['karanam_str']] = utils.KARANA_LIST[karanam[0]-1]+' '+utils.to_dms(karanam[1])+ ' ' +\
                        cal_key_list['starts_at_str'] + ' ' + utils.to_dms(karanam[2])+ ' ' + \
                        cal_key_list['ends_at_str']+' ('+"{0:.2f}".format(frac_left)+'% ' + cal_key_list['remaining_str']+' )'
        abhijit = drik.abhijit_muhurta(jd,place)
        calendar_info[cal_key_list['abhijit_str']] = abhijit
        _dhurmuhurtham = drik.durmuhurtam(jd,place)
        calendar_info[cal_key_list['dhurmuhurtham_str']] = _dhurmuhurtham
        return calendar_info
    def get_horoscope_chart_counter(self,chart_key):
        global dhasavarga_dict
        value_list = list(dhasavarga_dict.values())
        counter = [ index for index,value in enumerate(value_list) if chart_key in value][0]
        return counter
    def get_horoscope_information(self):#,language='en'):
        horoscope_info = {}
        self._vimsottari_balance = ();self._yoga_vimsottari_balance = ()
        self._arudha_lagna_data = {}
        self._sphuta_data = {}
        self._graha_lagna_data = {}
        self._hora_lagna_data = {}; self._ghati_lagna_data = {}; self._vighati_lagna_data = {}
        self._pranapada_lagna_data = {}; self._indu_lagna_data = {}; self._bhrigu_bindhu_lagna_data = {}
        self._bhava_lagna_data = {}; self._sree_lagna_data = {}
        self._varnada_lagna_data = {}
        self._maandhi_data = {}
        cal_key_list = self.cal_key_list#self._get_calendar_resource_strings(language)
        global dhasavarga_dict
        dhasavarga_dict={2:cal_key_list['hora_str'],
                         3:cal_key_list['drekkanam_str'],
                         4:cal_key_list['chaturthamsa_str'],
                         5:cal_key_list['panchamsa_str'],
                         6:cal_key_list['shashthamsa_str'],
                         7:cal_key_list['saptamsam_str'],
                         8:cal_key_list['ashtamsa_str'],
                         9:cal_key_list['navamsam_str'],
                         10:cal_key_list['dhasamsam_str'],
                         11:cal_key_list['rudramsa_str'],
                         12:cal_key_list['dhwadamsam_str'],
                         16:cal_key_list['shodamsa_str'],
                         20:cal_key_list['vimsamsa_str'],
                         24:cal_key_list['chaturvimsamsa_str'],
                         27:cal_key_list['nakshatramsa_str'],
                         30:cal_key_list['thrisamsam_str'],
                         40:cal_key_list['khavedamsa_str'],
                         45:cal_key_list['akshavedamsa_str'],
                         60:cal_key_list['sashtiamsam_str'],
                         81:cal_key_list['nava_navamsa_str'],
                         108:cal_key_list['ashtotharamsa_str'],
                         144:cal_key_list['dwadas_dwadasamsa_str'],
        }
        jd = self.julian_day # V3.1.9 If Julian_Years to be used then years/months arguments should not be used
        place = drik.Place(self.place_name,self.latitude,self.longitude,self.timezone_offset)
        dob = drik.Date(self.Date.year,self.Date.month,self.Date.day)
        tob=self.birth_time
        tob_in_hrs = tob[0]+tob[1]/60.0+tob[2]/3600.0
        """ TODO: 
            Planet Positions return type should match for both Drik and SS
            SS does not have Lagna/Ascendant in planet positions - should be included
            retrograde depends on return types of planet positions
        """
        if self.calculation_type=='ss':
            planet_positions = surya_sidhantha.planet_positions(jd, place)
        else:
            planet_positions = charts.rasi_chart(jd, place, ayanamsa_mode=self.ayanamsa_mode,
                                                 years=self.years,months=self.months,sixty_hours=self.sixty_hours,
                                                 pravesha_type=self.pravesha_type)
        #retrograde_planets = charts.planets_in_retrograde(planet_positions)
        retrograde_planets = drik.planets_in_retrograde(jd, place)
        #print('rasi retrograde planets',retrograde_planets)
        _ascendant = planet_positions[0][1] #drik.ascendant(jd,place)
        horoscope_charts = [[ ''  for _ in range(len(utils.RAASI_LIST))] for _ in range(len(dhasavarga_dict)+1)]
        chart_counter = 0
        divisional_chart_factor=1
        jd = self.julian_day#jd = self.julian_years #
        #"""
        self._get_sphuta(dob, tob, place, divisional_chart_factor)
        abl = self._get_arudha_padhas(dob, tob, place, divisional_chart_factor=divisional_chart_factor,
                                      years=self.years,months=self.months,sixty_hours=self.sixty_hours,
                                                 pravesha_type=self.pravesha_type)
        #print('_get_arudha_padhas returned',abl)
        for bli,blk in const._arudha_lagnas_included_in_chart.items():
            key = list(abl)[bli-1]
            #print('arudha padha key',key,'value',abl[key])
            value = abl[key]
            horoscope_info[key] = value
        #"""
        jd = self.julian_years # V3.1.9 Special Lagna do not take years arguments - so use julian years
        key = cal_key_list['raasi_str']+'-'+cal_key_list['bhava_lagna_str']+' ('+cal_key_list['bhava_lagna_short_str']+')'
        value = drik.bhava_lagna(jd,place,divisional_chart_factor)
        self._bhava_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str']+'-'+cal_key_list['hora_lagna_str']+' ('+cal_key_list['hora_lagna_short_str']+')'
        value = drik.hora_lagna(jd,place,divisional_chart_factor)
        self._hora_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str']+'-'+cal_key_list['ghati_lagna_str']+' ('+cal_key_list['ghati_lagna_short_str']+')'
        value = drik.ghati_lagna(jd,place,divisional_chart_factor)
        self._ghati_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str']+'-'+cal_key_list['vighati_lagna_str']+' ('+cal_key_list['vighati_lagna_short_str']+')'
        value = drik.vighati_lagna(jd,place,divisional_chart_factor)
        self._vighati_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str']+'-'+cal_key_list['pranapada_lagna_str']
        value = drik.pranapada_lagna(jd,place,divisional_chart_factor)
        self._pranapada_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str']+'-'+cal_key_list['indu_lagna_str']
        value = drik.indu_lagna(jd,place,divisional_chart_factor)
        self._indu_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str']+'-'+cal_key_list['bhrigu_bindhu_lagna_str']+' ('+cal_key_list['bhrigu_bindhu_lagna_short_str']+')'
        value = drik.bhrigu_bindhu(jd,place,divisional_chart_factor)
        self._bhrigu_bindhu_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str'] +'-'+cal_key_list['sree_lagna_str']+' ('+cal_key_list['sree_lagna_short_str']+')'
        value = drik.sree_lagna(jd,place,divisional_chart_factor)
        self._sree_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str'] +'-'+cal_key_list['varnada_lagna_str']
        value = charts.varnada_lagna(dob, tob, place,divisional_chart_factor=1)
        self._varnada_lagna_data[divisional_chart_factor] = value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        key = cal_key_list['raasi_str'] +'-'+cal_key_list['maandi_str']
        value = drik.maandi_longitude(dob,tob,place,divisional_chart_factor)
        self._maandhi_data[divisional_chart_factor]=value[0]
        horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
        jd = self.julian_day # V3.1.9 revert to julian after special lagna calculations
        asc_house = _ascendant[0]
        horoscope_charts[chart_counter][asc_house] += cal_key_list['ascendant_str'] +"\n"
        horoscope_info[cal_key_list['raasi_str']+'-'+cal_key_list['ascendant_str']] = utils.RAASI_LIST[asc_house] +' ' + utils.to_dms(_ascendant[1],is_lat_long='plong')
        chara_karaka_names = [x+'_str' for x in house.chara_karaka_names]
        chara_karaka_dict = house.chara_karakas(planet_positions)
        for p,(h,long) in planet_positions[1:]:
            ret_str = ''
            if p in retrograde_planets:
                ret_str = const._retrogade_symbol
            planet_name = utils.PLANET_NAMES[p]+ret_str
            k = cal_key_list['raasi_str']+'-'+planet_name
            ck_str = ''
            if p !='L' and p < 8:
                ck_index = chara_karaka_dict.index(p)
                ck_str = ' (' + cal_key_list[chara_karaka_names[ck_index]] +')'
            v = utils.RAASI_LIST[h]+' '+ utils.to_dms(long,is_lat_long='plong') + ck_str
            planet_house = h
            horoscope_charts[chart_counter][planet_house] += planet_name + "\n"
            relative_planet_house = house.get_relative_house_of_planet(asc_house, planet_house)
            horoscope_info[k]=v # + str(relative_planet_house)
        # Shadow Sub Planet information
        #k = cal_key_list['raasi_str']+'-'+cal_key_list['upagraha_str']
        #horoscope_info[k]=''
        sub_planet_list_1 = {'kaala_str':'kaala_longitude','mrityu_str':'mrityu_longitude','artha_str':'artha_praharaka_longitude','yama_str':'yama_ghantaka_longitude',
                           'gulika_str':'gulika_longitude','maandi_str':'maandi_longitude'}
        sub_planet_list_2 = ['dhuma','vyatipaata','parivesha','indrachaapa','upaketu']
        place = drik.Place(self.place_name,self.latitude,self.longitude,self.timezone_offset)
        sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
        #print('solar longitude for D-'+str(divisional_chart_factor),sun_long)
        for sp,sp_func in sub_planet_list_1.items():
            k = cal_key_list['raasi_str']+'-'+cal_key_list[sp]
            v = eval('drik.'+sp_func+'(dob,tob,place,divisional_chart_factor=1)')
            horoscope_info[k]= utils.RAASI_LIST[v[0]] +' '+utils.to_dms(v[1],is_lat_long='plong')
        for sp in sub_planet_list_2:
            k = cal_key_list['raasi_str']+'-'+cal_key_list[sp+'_str']
            v = eval('drik.'+'solar_upagraha_longitudes(sun_long,sp,divisional_chart_factor)')
            horoscope_info[k]= utils.RAASI_LIST[v[0]] +' '+utils.to_dms(v[1],is_lat_long='plong')
        ## Dhasavarga Charts
        jd = self.julian_day  #V3.1.9
        for dhasavarga_factor in dhasavarga_dict.keys():
            " planet_positions lost: [planet_id, planet_constellation, planet_longitude] " 
            #print('get horo info language',dhasavarga_factor,language,utils.PLANET_NAMES,utils.RAASI_LIST)
            planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=self.ayanamsa_mode,
                                                       divisional_chart_factor=dhasavarga_factor,
                                                       years=self.years,months=self.months,sixty_hours=self.sixty_hours,
                                                       calculation_type=self.calculation_type,pravesha_type=self.pravesha_type)
            chara_karaka_dict = house.chara_karakas(planet_positions)
            ascendant_navamsa = planet_positions[0][1]
            asc_house = ascendant_navamsa[0]
            ascendant_longitude = ascendant_navamsa[1]
            jd = self.julian_day #V3.1.9
            chart_counter += 1
            horoscope_charts[chart_counter][asc_house] += cal_key_list['ascendant_str'] +"\n"
            self._get_sphuta(dob, tob, place, divisional_chart_factor=dhasavarga_factor)
            abl = self._get_arudha_padhas(dob, tob, place, divisional_chart_factor=dhasavarga_factor,
                                      years=self.years,months=self.months,sixty_hours=self.sixty_hours,
                                      pravesha_type=self.pravesha_type)
            for bli,blk in const._arudha_lagnas_included_in_chart.items():
                key = list(abl)[bli-1]
                #print('arudha padha key',key,'value',abl[key])
                value = abl[key]
                horoscope_info[key] = value
            jd = self.julian_years # V3.1.9 Special Lagna do not take years arguments - so use julian years
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['bhava_lagna_str']+' ('+cal_key_list['bhava_lagna_short_str']+')'
            value = drik.bhava_lagna(jd,place,dhasavarga_factor)
            self._bhava_lagna_data[dhasavarga_factor] = value[0] # V3.1.9
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['hora_lagna_str']+' ('+cal_key_list['hora_lagna_short_str']+')'
            value = drik.hora_lagna(jd,place,dhasavarga_factor)
            self._hora_lagna_data[dhasavarga_factor] = value[0]
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['ghati_lagna_str']+' ('+cal_key_list['ghati_lagna_short_str']+')'
            value = drik.ghati_lagna(jd,place,dhasavarga_factor)
            self._ghati_lagna_data[dhasavarga_factor] = value[0]
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['vighati_lagna_str']+' ('+cal_key_list['vighati_lagna_short_str']+')'
            value = drik.vighati_lagna(jd,place,dhasavarga_factor)
            self._vighati_lagna_data[dhasavarga_factor] = value[0]
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor]+'-'+cal_key_list['pranapada_lagna_str']
            value = drik.pranapada_lagna(jd,place,divisional_chart_factor)
            self._pranapada_lagna_data[divisional_chart_factor] = value[0]
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor]+'-'+cal_key_list['indu_lagna_str']
            value = drik.indu_lagna(jd,place,divisional_chart_factor)
            self._indu_lagna_data[divisional_chart_factor] = value[0]
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor]+'-'+cal_key_list['bhrigu_bindhu_lagna_str']+' ('+cal_key_list['bhrigu_bindhu_lagna_short_str']+')'
            value = drik.bhrigu_bindhu(jd,place,divisional_chart_factor)
            self._bhrigu_bindhu_lagna_data[divisional_chart_factor] = value[0]
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['sree_lagna_str']+' ('+cal_key_list['sree_lagna_short_str']+')'
            jd = self.julian_day # V3.1.9 revert to julian after special lagna calculations
            value = drik.sree_lagna(jd,place,dhasavarga_factor)
            self._sree_lagna_data[dhasavarga_factor] = value[0] # V3.1.9
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['varnada_lagna_str']
            value = charts.varnada_lagna(dob, tob, place, divisional_chart_factor=dhasavarga_factor)
            self._varnada_lagna_data[dhasavarga_factor]=value[0]            
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            key = dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['maandi_str']
            value = drik.maandi_longitude(dob,tob,place,dhasavarga_factor)
            self._maandhi_data[dhasavarga_factor]=value[0]            
            horoscope_info[key] = utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')
            horoscope_info[dhasavarga_dict[dhasavarga_factor] +'-'+cal_key_list['ascendant_str']] = \
                utils.RAASI_LIST[ascendant_navamsa[0]]+' '+utils.to_dms(ascendant_navamsa[1],True,'plong')
            for p,(h,long) in planet_positions[1:]:
                ret_str = ''
                if p in retrograde_planets:
                    ret_str = const._retrogade_symbol
                planet_name = utils.PLANET_NAMES[p]+ret_str
                #print('dhasavarga_factor',dhasavarga_factor,'planet_name',planet_name)
                k = dhasavarga_dict[dhasavarga_factor]+'-'+planet_name
                planet_house = h
                ck_str = ''
                if p !='L' and p < 8:
                    #print('D'+str(dhasavarga_factor),planet_name,chara_karaka_dict[p])
                    ck_str = ' (' + cal_key_list[chara_karaka_names[chara_karaka_dict[p]]] +')'
                v = utils.RAASI_LIST[h]+' ' +utils.to_dms(long,is_lat_long='plong') + ck_str
                horoscope_charts[chart_counter][planet_house] += planet_name +'\n'
                relative_planet_house = house.get_relative_house_of_planet(asc_house, planet_house)
                horoscope_info[k]= v #+ [relative_planet_house]
            #k = dhasavarga_dict[dhasavarga_factor]+'-'+cal_key_list['upagraha_str']
            #horoscope_info[k]=''
            for sp,sp_func in sub_planet_list_1.items():
                k = dhasavarga_dict[dhasavarga_factor]+'-'+cal_key_list[sp]
                v = eval('drik.'+sp_func+'(dob,tob,place,divisional_chart_factor=dhasavarga_factor)')
                horoscope_info[k] = utils.RAASI_LIST[v[0]] +' '+utils.to_dms(v[1],is_lat_long='plong') 
            for sp in sub_planet_list_2:
                k = dhasavarga_dict[dhasavarga_factor]+'-'+cal_key_list[sp+'_str']
                v = eval('drik.'+'solar_upagraha_longitudes(jd,sp,divisional_chart_factor=dhasavarga_factor)')
                horoscope_info[k] = utils.RAASI_LIST[v[0]] +' '+utils.to_dms(v[1],is_lat_long='plong')
        return horoscope_info, horoscope_charts#, vimsottari_dhasa_bhukti_info,ashtottari_dhasa_bhukti_info,narayana_dhasa_info
    def _get_shad_bala(self,dob,tob,place):
        from hora.horoscope.chart import strength
        jd = utils.julian_day_number(dob, tob)
        return strength.shad_bala(jd, place)
    def _get_bhava_bala(self,dob,tob,place):
        from hora.horoscope.chart import strength
        jd = utils.julian_day_number(dob, tob)
        bb = strength.bhava_bala(jd, place)
        #print('main bhava bala info',bb)
        import numpy as np
        bb = list(np.array(bb).T)
        #print('main bhava bala info',bb)
        return bb
    def _get_other_bala(self,dob,tob,place):
        #from hora.horoscope.transit import tajaka
        from hora.horoscope.chart import strength
        jd = utils.julian_day_number(dob, tob)
        hb = strength.harsha_bala(dob, tob, place)
        hb1 = {utils.PLANET_NAMES[p]:hb[p] for p in range(7)}
        pvb = strength.pancha_vargeeya_bala(jd, place)
        pvb1 = {utils.PLANET_NAMES[p]:pvb[p] for p in range(7)}
        dvb = strength.dwadhasa_vargeeya_bala(jd, place)
        dvb1 = {utils.PLANET_NAMES[p]:dvb[p] for p in range(7)}
        return [hb1, pvb1, dvb1]
    def _get_amsa_bala(self,dob,tob,place_as_tuple):
        jd_at_dob = utils.julian_day_number(dob, tob)
        sv = charts.shadvarga_of_planets(jd_at_dob, place_as_tuple)
        sv1 = {}
        for p in range(9):
            sv1[utils.PLANET_NAMES[p]]=utils.SHADVARGAMSA_NAMES[sv[p][0]]+'\n('+sv[p][1]+ ')\n'+str(round(sv[p][2],1))
        sv = charts.sapthavarga_of_planets(jd_at_dob, place_as_tuple)
        sv2 = {}
        for p in range(9):
            sv2[utils.PLANET_NAMES[p]]=utils.SAPTAVARGAMSA_NAMES[sv[p][0]]+'\n('+sv[p][1]+ ')\n'+str(round(sv[p][2],1))
        sv = charts.dhasavarga_of_planets(jd_at_dob, place_as_tuple)
        dv = {}
        for p in range(9):
            dv[utils.PLANET_NAMES[p]]=utils.DHASAVARGAMSA_NAMES[sv[p][0]]+'\n('+sv[p][1]+ ')\n'+str(round(sv[p][2],1))
        sv = charts.shodhasavarga_of_planets(jd_at_dob, place_as_tuple)
        sv3 = {}
        for p in range(9):
            sv3[utils.PLANET_NAMES[p]]=utils.SHODASAVARGAMSA_NAMES[sv[p][0]]+'\n('+sv[p][1]+ ')\n'+str(round(sv[p][2],1))
        return [sv1,sv2,dv,sv3]
    def _get_sphuta(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.chart import sphuta
        for s in const.sphuta_list:
            key = 'D'+str(divisional_chart_factor)+'-'+self.cal_key_list[s+'_sphuta_str']
            fn = 'sphuta.'+s+'_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor)'
            value = eval(fn)
            self._sphuta_data[key] = utils.RAASI_LIST[value[0]]+' '+utils.to_dms(value[1], is_lat_long='plong')
        return
    def _get_arudha_padhas(self,dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,pravesha_type=0):
        from hora.horoscope.chart import arudhas
        jd_at_dob = utils.julian_day_number(dob, tob)
        planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
                                                   years=years,months=months,sixty_hours=sixty_hours,
                                                   pravesha_type=pravesha_type)
        asc_house = planet_positions[0][1][0]
        ba = arudhas.bhava_arudhas_from_planet_positions(planet_positions)
        #print('D-'+str(divisional_chart_factor),ba)
        self._arudha_lagna_data[divisional_chart_factor] = ['' for _ in range(12)]
        for bk,bv in const._arudha_lagnas_included_in_chart.items():
            bai = int(bv.replace('bhava_arudha_a','').replace('_str',''))
            self._arudha_lagna_data[divisional_chart_factor][ba[bai-1]] += '\n'+self.cal_key_list[bv.replace("_str","_short_str")]
        #print('D-'+str(divisional_chart_factor),self._arudha_lagna_data[divisional_chart_factor])
        houses = [(h + asc_house) % 12 for h in range(12)]
        bhava_arudhas = {}
        for i, h in enumerate(houses):
            bhava_arudhas['D-'+str(divisional_chart_factor)+'-'+self.cal_key_list['bhava_arudha_a'+str(i+1)+'_str'] \
                          +' ('+self.cal_key_list['bhava_arudha_a'+str(i+1)+'_short_str']+')']=utils.RAASI_LIST[ba[i]]
        ga = arudhas.graha_arudhas_from_planet_positions(planet_positions)        
        for p in range(9):
            self._graha_lagna_data['D'+str(divisional_chart_factor)+'-'+utils.PLANET_NAMES[p]]=utils.RAASI_LIST[ga[p]]
        return bhava_arudhas
    def _get_graha_dhasa_bhukthi(self,dob,tob,place):
        self._vimsottari_balance,_vimsottari_dhasa_bhkthi_info = self._get_vimsottari_dhasa_bhukthi(dob, tob, place)
        print('horo _vimsottari_balance',self._vimsottari_balance)
        _ashtottari_dhasa_bhkthi_info = self._get_ashtottari_dhasa_bhukthi(dob, tob, place)
        _yogini_dhasa_bhkthi_info = self._get_yogini_dhasa_bhukthi(dob, tob, place)
        return _vimsottari_dhasa_bhkthi_info,_ashtottari_dhasa_bhkthi_info, _yogini_dhasa_bhkthi_info
    def _get_rasi_dhasa_bhukthi(self,dob,tob,place):
        _narayana_dhasa_bhukthi_info = self._get_narayana_dhasa(dob,tob,place)
        _kendraadhi_rasi_dhasa_bhukthi_info = self._get_kendraadhi_rasi_dhasa(dob,tob,place)
        _sudasa_dhasa_bhukthi_info = self._get_sudasa_dhasa(dob,tob,place)
        _drig_dhasa_bhukthi_info = self._get_drig_dhasa(dob,tob,place)
        _nirayana_dhasa_bhukthi_info = self._get_nirayana_dhasa(dob,tob,place)
        _shoola_dhasa_bhukthi_info = self._get_shoola_dhasa(dob,tob,place)
        _kendraadhi_karaka_dhasa_bhukthi_info = self._get_kendraadhi_karaka_dhasa(dob,tob,place)
        _chara_dhasa_bhukthi_info = self._get_chara_dhasa(dob,tob,place)
        _lagnamsaka_dhasa_bhukthi_info = self._get_lagnamsaka_dhasa(dob,tob,place)
        _padhanadhamsa_dhasa_bhukthi_info = self._get_padhanadhamsa_dhasa(dob, tob, place)
        _mandooka_dhasa_bhukthi_info = self._get_mandooka_dhasa(dob, tob, place)
        _sthira_dhasa_bhukthi_info = self._get_sthira_dhasa(dob, tob, place)
        _tara_lagna_dhasa_bhukthi_info = self._get_tara_lagna_dhasa(dob, tob, place)
        return [_narayana_dhasa_bhukthi_info, _kendraadhi_rasi_dhasa_bhukthi_info, _sudasa_dhasa_bhukthi_info, \
            _drig_dhasa_bhukthi_info, _nirayana_dhasa_bhukthi_info, _shoola_dhasa_bhukthi_info, \
            _kendraadhi_karaka_dhasa_bhukthi_info, _chara_dhasa_bhukthi_info, _lagnamsaka_dhasa_bhukthi_info, \
            _padhanadhamsa_dhasa_bhukthi_info]
    def _get_annual_dhasa_bhukthi(self):
        _patyayini_dhasa_bhukthi_info = self._get_patyatini_dhasa_bhukthi()
        _mudda_dhasa_bhukthi_info = self._get_varsha_vimsottari_dhasa(self.julian_day, self.Place, self.years-1)
        _varsha_narayana_dhasa_bhukthi_info = self._get_varsha_narayana_dhasa(self.Date, self.birth_time, self.Place, self.years)
        return [_patyayini_dhasa_bhukthi_info,_mudda_dhasa_bhukthi_info,_varsha_narayana_dhasa_bhukthi_info]
    def _get_varsha_narayana_dhasa(self,dob,tob,place,years):
        from hora.horoscope.dhasa.raasi import narayana
        db = narayana.varsha_narayana_dhasa_bhukthi(dob, tob, place, years, divisional_chart_factor=1,include_antardhasa=True)
        #print('varsha narayana dhasa',db)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_varsha_vimsottari_dhasa(self,jd, place, years):
        from hora.horoscope.dhasa.annual import mudda
        md = mudda.varsha_vimsottari_dhasa_bhukthi(jd, place, years)
        dhasa_bhukti_info = []
        for pd,pb,bs,_ in md:
            dhasa_lord = utils.PLANET_NAMES[pd]
            bhukthi_lord = utils.PLANET_NAMES[pb]
            dhasa_bhukti_info.append((dhasa_lord+'-'+bhukthi_lord,bs))
        return dhasa_bhukti_info
    def _get_patyatini_dhasa_bhukthi(self):
        from hora.horoscope.dhasa.annual import patyayini
        self.julian_years = drik.next_solar_date(self.julian_day, self.Place, self.years, self.months, self.sixty_hours)
        p_d_b = patyayini.patyayini_dhasa(self.julian_years, self.Place, self.ayanamsa_mode, divisional_chart_factor=1)
        #print('p_d_b',p_d_b)
        dhasa_bhukti_info = []
        for p,bhukthis,_ in p_d_b:
            #print('p,bhukthis',p,bhukthis)
            if p=='L':
                dhasa_lord = self._ascendant_str
            else:
                dhasa_lord = utils.PLANET_NAMES[p]
            for bk,bs in bhukthis:
                #print('bk,bs',bk,bs)
                if bk=='L':
                    bhukthi_lord = self._ascendant_str
                else:
                    bhukthi_lord = utils.PLANET_NAMES[bk]
                dhasa_bhukti_info.append((dhasa_lord+'-'+bhukthi_lord,bs))
                #print('key',dhasa_lord+'-'+bhukthi_lord,'value',bs)
        return dhasa_bhukti_info
    def _get_tara_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import tara
        db = tara.get_dhasa_bhukthi(dob, tob, place,include_antardasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_karaka_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import karaka
        planet_positions = charts.rasi_chart(jd, place)
        db = karaka.get_dhasa_antardhasa(dob, tob, place,include_antardhasa=True)
        chara_karaka_names = [x+'_str' for x in house.chara_karaka_names]
        chara_karaka_dict = house.chara_karakas(planet_positions)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'\n'+self.cal_key_list[chara_karaka_names[chara_karaka_dict[dhasa_lord]]]+'\n'
                                      +'-'+utils.PLANET_NAMES[bukthi_lord]+'\n'+self.cal_key_list[chara_karaka_names[chara_karaka_dict[bukthi_lord]]]+'\n',bukthi_start))
        return dhasa_bhukti_info
    def _get_naisargika_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import naisargika
        db = naisargika.get_dhasa_bhukthi(dob, tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_vimsottari_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import vimsottari
        self._vimsottari_balance,db = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place, star_position_from_moon=1)#drik.get_dhasa_bhukthi(jd,place)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_kaala_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import kaala
        db = kaala.get_dhasa_antardhasa(dob,tob, place,include_antardhasa=True)#drik.get_dhasa_bhukthi(jd,place)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_chakra_dhasa(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.raasi import chakra
        db = chakra.get_dhasa_antardhasa(dob,tob, place,include_antardhasa=True)#drik.get_dhasa_bhukthi(jd,place)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_rasi_bhukthi_vimsottari_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import vimsottari
        _,db = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place, star_position_from_moon=1,use_rasi_bhukthi_variation=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_yoga_vimsottari_dhasa_bhukthi(self,dob,tob,place):
        jd = utils.julian_day_number(dob, tob)
        from hora.horoscope.dhasa.graha import yoga_vimsottari
        self._yoga_vimsottari_balance,db = yoga_vimsottari.get_dhasa_bhukthi(jd, place)#drik.get_dhasa_bhukthi(jd,place)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_ashtottari_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import ashtottari
        jd = utils.julian_day_number(dob,tob)
        #chk = ashtottari.applicability_check(charts.rasi_chart(jd, place))
        db = ashtottari.get_ashtottari_dhasa_bhukthi(jd, place)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        #print(dhasa_bhukti_info)
        return dhasa_bhukti_info
    def _get_tithi_ashtottari_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import tithi_ashtottari
        jd = utils.julian_day_number(dob,tob)
        #chk = ashtottari.applicability_check(charts.rasi_chart(jd, place))
        db = tithi_ashtottari.get_ashtottari_dhasa_bhukthi(jd, place)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start]=db[i]
            #dhasa_bhukti_info[utils.DHASA_LIST[dhasa_lord]+'-'+utils.BHUKTHI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        #print(dhasa_bhukti_info)
        return dhasa_bhukti_info
    def _get_buddhi_gathi_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import buddhi_gathi
        jd = utils.julian_day_number(dob,tob)
        #chk = ashtottari.applicability_check(charts.rasi_chart(jd, place))
        db = buddhi_gathi.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_yogini_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import yogini
        jd = utils.julian_day_number(dob,tob)
        #chk = ashtottari.applicability_check(charts.rasi_chart(jd, place))
        db = yogini.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_tithi_yogini_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import tithi_yogini
        jd = utils.julian_day_number(dob,tob)
        #chk = ashtottari.applicability_check(charts.rasi_chart(jd, place))
        db = tithi_yogini.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_shodasottari_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import shodasottari
        jd = utils.julian_day_number(dob,tob)
        db = shodasottari.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_dwadasottari_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import dwadasottari
        jd = utils.julian_day_number(dob,tob)
        db = dwadasottari.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_dwisatpathi_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import dwisatpathi
        jd = utils.julian_day_number(dob,tob)
        db = dwisatpathi.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_panchottari_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import panchottari
        jd = utils.julian_day_number(dob,tob)
        db = panchottari.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_satabdika_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import sataatbika
        jd = utils.julian_day_number(dob,tob)
        db = sataatbika.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_chaturaaseeti_sama_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import chathuraaseethi_sama
        jd = utils.julian_day_number(dob,tob)
        db = chathuraaseethi_sama.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_karana_chaturaaseeti_sama_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import karana_chathuraaseethi_sama
        jd = utils.julian_day_number(dob,tob)
        db = karana_chathuraaseethi_sama.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_shashtisama_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import shastihayani
        jd = utils.julian_day_number(dob,tob)
        db = shastihayani.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_shattrimsa_sama_dhasa_bhukthi(self,dob,tob,place):
        from hora.horoscope.dhasa.graha import shattrimsa_sama
        jd = utils.julian_day_number(dob,tob)
        db = shattrimsa_sama.get_dhasa_bhukthi(dob,tob, place,include_antardhasa=True)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            if not db[i]:
                continue
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.PLANET_NAMES[dhasa_lord]+'-'+utils.PLANET_NAMES[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_narayana_dhasa(self,dob,tob,place):#,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import narayana
        db = narayana.narayana_dhasa_for_rasi_chart(dob, tob, place,include_antardhasa=True)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_kendraadhi_rasi_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import kendradhi_rasi
        db = kendradhi_rasi.kendradhi_rasi_dhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_sudasa_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import sudasa
        db = sudasa.sudasa_dhasa_bhukthi(dob, tob, place, divisional_chart_factor)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_drig_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import drig
        db = drig.drig_dhasa_bhukthi(dob, tob, place, divisional_chart_factor)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_nirayana_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import nirayana
        db = nirayana.nirayana_shoola_dhasa_bhukthi(dob, tob, place, divisional_chart_factor)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_shoola_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import shoola
        db = shoola.shoola_dhasa_bhukthi(dob, tob, place, divisional_chart_factor)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_kendraadhi_karaka_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import kendradhi_rasi
        db = kendradhi_rasi.karaka_kendradhi_rasi_dhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor, karaka_index=1)
        dhasa_bhukti_info = []
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_chara_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import chara
        db = chara.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor, chara_method=1)
        #print('chara dasa',db)
        dhasa_bhukti_info = []
        for _dhasa,_bhukthi,dhasa_start,_ in db:
            dhasa_lord = utils.RAASI_LIST[_dhasa]
            bukthi_lord = utils.RAASI_LIST[_bhukthi]
            #dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(fh, as_string=True)
            dhasa_bhukti_info.append((dhasa_lord+'-'+bukthi_lord,dhasa_start))
        return dhasa_bhukti_info
    def _get_lagnamsaka_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import lagnamsaka
        db = lagnamsaka.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_padhanadhamsa_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import padhanadhamsa
        db = padhanadhamsa.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_mandooka_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import mandooka
        db = mandooka.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_sthira_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import sthira
        db = sthira.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_tara_lagna_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import tara_lagna
        db = tara_lagna.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_brahma_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import brahma
        db = brahma.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_varnada_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import varnada
        db = varnada.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_yogardha_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import yogardha
        db = yogardha.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_navamsa_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import navamsa
        db = navamsa.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            #dhasa_bhukti_info[utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord]]=bukthi_start
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_paryaaya_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import paryaaya
        db = paryaaya.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        #print('paryaaya dhasa',db)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
            #dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_trikona_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import trikona
        db = trikona.get_dhasa_antardhasa(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        #print('trikona dhasa',db)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord, bukthi_lord,bukthi_start,_]=db[i]
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
            #dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord]+'-'+utils.RAASI_LIST[bukthi_lord],bukthi_start))
        return dhasa_bhukti_info
    def _get_kalachakra_dhasa(self,dob,tob,place,divisional_chart_factor=1):
        from hora.horoscope.dhasa.raasi import kalachakra
        jd_at_dob = utils.julian_day_number(dob, tob)
        pp = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=divisional_chart_factor)
        moon_long = pp[2][1][0]*30+pp[2][1][1]
        db = kalachakra.kalachakra_dhasa(moon_long, dob)
        #print(db)
        dhasa_bhukti_info = [] #{}
        for i in range(len(db)):
            [dhasa_lord,bukthi_start,_,_,_]=db[i]
            dhasa_bhukti_info.append((utils.RAASI_LIST[dhasa_lord],bukthi_start))
        return dhasa_bhukti_info
def get_chara_karakas(planet_positions):
    return house.chara_karakas(planet_positions)
if __name__ == "__main__":
    horoscope_language = 'ta' # """ Matplotlib charts available only English"""
    place = drik.Place('Chennai,IN',13.0389, 80.2619, +5.5)
    #place = drik.Place('Durham',35.994, -78.8986,-4.0)
    dob = drik.Date(1996,12,7)
    #dob = drik.Date(2023,4,25)
    tob = (10,34,0)
    years = 29
    jd_at_dob = utils.julian_day_number(dob, tob)
    a = Horoscope(place_with_country_code=place.Place,date_in=drik.Date(dob[0],dob[1],dob[2]),
                  birth_time="10:34:00",calculation_type='drik',years=years,language=horoscope_language)
    print(a.calendar_info)
    print(a.horoscope_charts[0])
    #exit()
    #pp = charts.rasi_chart(jd_at_dob, place)
    #h_to_p = utils.get_house_planet_list_from_planet_positions(pp)
    planet = 2
    h_to_p = ['5/2/3/0','','','L/4','6/7','','','1','','','8','']
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    print('aspects of ',utils.PLANET_NAMES[planet],house.aspected_planets_of_the_raasi(h_to_p, p_to_h[planet]))
    #exit()
    as_string = True
    a= Horoscope(place_with_country_code=place.Place,latitude=place.latitude,
                 longitude=place.longitude,timezone_offset=place.timezone,date_in=dob,birth_time='10:34:00',
                 language=horoscope_language)#,ayanamsa_mode="Lahiri")
    #a= Horoscope(latitude=35.994,longitude=-78.8986,timezone_offset=-4.0,date_in=dob,birth_time='23:43:00',ayanamsa_mode="Lahiri")
    a._sphuta_data = {}
    print(a._get_sphuta(dob, tob, place,divisional_chart_factor=1))
    print(a._sphuta_data)
    exit()
    db = a._get_kalachakra_dhasa(dob, tob, place)
    print(db)
    exit()
    a._arudha_lagna_data = {}
    a._get_arudha_padhas(dob, tob, place, divisional_chart_factor=1)
    a._get_arudha_padhas(dob, tob, place, divisional_chart_factor=9)
    exit()
    #db = a._get_drig_dhasa_bhukthi(dob, tob, place)
    #db = a._get_ashtottari_dhasa_bhukthi(dob, tob, place)
    db = a._get_narayana_dhasa(dob, tob, place)
    print('narayana',db)
    """
    db = a._get_naryana_dhasa(dob, tob, place)
    print('narayana',db)
    db = a._get_kendraadhi_dhasa(dob, tob, place)
    print('kendraadhi rasi',db)
    db = a._get_sudasa_dhasa(dob,tob,place)
    print('sudasa',db)
    db = a._get_drig_dhasa(dob,tob,place)
    print('drig',db)
    db = a._get_varsha_naryana_dhasa(dob, tob, place, years=1)
    print('varsha narayana',db)
    ba, ga = a._get_arudha_padhas(dob,tob,place,divisional_chart_factor=1)
    print(ba)
    print(ga)
    """
    exit()
