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
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Release History:
        V4.8.9 - Module is restricted to calculate sphutas only for rasi chart. varga chart related arguments removed.
            - Use charts.sphuta_longitudes to get sphuta longitudes for varga charts.
            - Functions have been revised. Now sphuta values match very closely with Jaganath Hora for same settings.
"""
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import house, charts

def _tri_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    moon_long = planet_positions[const.MOON_ID+1][1][0]*30 + planet_positions[const.MOON_ID+1][1][1]
    asc_long = planet_positions[0][1][0]*30 + planet_positions[0][1][1]
    gulika_long = drik.gulika_raw(dob, tob, place, dhasa_progression_correction=dhasa_progression_correction)
    return (moon_long + asc_long + gulika_long) % 360.0

def tri_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_tri_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _chatur_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    sun_long = planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1]
    tri_long = _tri_sphuta_raw(dob, tob, place, dhasa_progression_correction)
    return (sun_long + tri_long) % 360.0

def chatur_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_chatur_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _pancha_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    rahu_long = planet_positions[const.RAHU_ID+1][1][0]*30+planet_positions[const.RAHU_ID+1][1][1]
    chatur_long = _chatur_sphuta_raw(dob, tob, place, dhasa_progression_correction)
    return (rahu_long + chatur_long) % 360.0

def pancha_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_pancha_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _prana_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika_long = drik.gulika_raw(dob, tob, place, dhasa_progression_correction=dhasa_progression_correction)
    return (asc_long * 5 + gulika_long) % 360.0

def prana_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_prana_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _deha_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    moon_long = planet_positions[const.MOON_ID+1][1][0]*30+planet_positions[const.MOON_ID+1][1][1]
    gulika_long = drik.gulika_raw(dob, tob, place, dhasa_progression_correction=dhasa_progression_correction)
    return (moon_long * 8 + gulika_long) % 360.0

def deha_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_deha_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _mrityu_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    sun_long = planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1]
    gulika_long = drik.gulika_raw(dob, tob, place, dhasa_progression_correction=dhasa_progression_correction)
    return (gulika_long * 7 + sun_long) % 360.0

def mrityu_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_mrityu_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def sookshma_tri_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    prana_long = _prana_sphuta_raw(dob, tob, place, dhasa_progression_correction)
    deha_long = _deha_sphuta_raw(dob, tob, place, dhasa_progression_correction)
    mrityu_long = _mrityu_sphuta_raw(dob, tob, place, dhasa_progression_correction)
    return drik.dasavarga_from_long((prana_long + deha_long + mrityu_long) % 360.0)

def _beeja_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    sun_long = planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1]
    jupiter_long = planet_positions[const.JUPITER_ID+1][1][0]*30+planet_positions[const.JUPITER_ID+1][1][1]
    venus_long = planet_positions[const.VENUS_ID+1][1][0]*30+planet_positions[const.VENUS_ID+1][1][1]
    return (sun_long + jupiter_long + venus_long) % 360.0

def beeja_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_beeja_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _kshetra_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    moon_long = planet_positions[const.MOON_ID+1][1][0]*30+planet_positions[const.MOON_ID+1][1][1]
    jupiter_long = planet_positions[const.JUPITER_ID+1][1][0]*30+planet_positions[const.JUPITER_ID+1][1][1]
    mars_long = planet_positions[const.MARS_ID+1][1][0]*30+planet_positions[const.MARS_ID+1][1][1]
    return (moon_long + jupiter_long + mars_long) % 360.0

def kshetra_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_kshetra_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _tithi_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    moon_long = planet_positions[const.MOON_ID+1][1][0]*30+planet_positions[const.MOON_ID+1][1][1]
    sun_long = planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1]
    return (moon_long - sun_long) % 360.0

def tithi_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_tithi_sphuta_raw(dob, tob, place, dhasa_progression_correction))

def _yoga_sphuta_raw(dob, tob, place, add_yogi_longitude=False, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    moon_long = planet_positions[const.MOON_ID+1][1][0]*30+planet_positions[const.MOON_ID+1][1][1]
    sun_long = planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1]
    yogi_long = 93.33333333333333 if add_yogi_longitude else 0.0
    return (moon_long + sun_long + yogi_long) % 360.0

def yoga_sphuta(dob, tob, place, add_yogi_longitude=False, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_yoga_sphuta_raw(dob, tob, place, add_yogi_longitude, dhasa_progression_correction))

def yogi_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return yoga_sphuta(dob, tob, place, dhasa_progression_correction=dhasa_progression_correction, add_yogi_longitude=True)

def avayogi_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    yl = _yoga_sphuta_raw(dob, tob, place, add_yogi_longitude=True, dhasa_progression_correction=dhasa_progression_correction)
    ayl = (yl + 186.66666666666666) % 360.0
    return drik.dasavarga_from_long(ayl)

def _rahu_tithi_sphuta_raw(dob, tob, place, dhasa_progression_correction=0.0):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place,  
                                        dhasa_progression_correction=dhasa_progression_correction,
                                        exclude_non_planets=True)
    rahu_long = planet_positions[const.RAHU_ID+1][1][0]*30+planet_positions[const.RAHU_ID+1][1][1]
    sun_long = planet_positions[const.SUN_ID+1][1][0]*30+planet_positions[const.SUN_ID+1][1][1]
    return (rahu_long - sun_long) % 360.0

def rahu_tithi_sphuta(dob, tob, place, dhasa_progression_correction=0.0):
    return drik.dasavarga_from_long(_rahu_tithi_sphuta_raw(dob, tob, place, dhasa_progression_correction))

if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    line_sep = '\n'
    yh,yl = yogi_sphuta(dob, tob, place)
    ystr = utils.resource_strings['yogi_sphuta_str']+' '+utils.resource_strings['raasi_str']+':'+\
            utils.RAASI_LIST[yh]+' '+utils.resource_strings['longitude_str']+':'+utils.to_dms(yl,is_lat_long='plong')
    ynak = utils.nakshatra_pada(yh*30+yl)
    ystr += line_sep+utils.resource_strings['yogi_sphuta_str']+' '+utils.resource_strings['nakshatra_str']+':'+ \
            utils.NAKSHATRA_LIST[ynak[0]-1]
    yogi_planet = [l for l,naks in const.nakshathra_lords.items() if ynak[0]-1 in naks][0]
    ystr += line_sep+utils.resource_strings['yogi_sphuta_str']+' '+utils.resource_strings['planet_str']+':'+ \
            utils.PLANET_NAMES[yogi_planet]
    sahayogi_planet = const._house_owners_list[yh]
    ystr += line_sep+utils.resource_strings['sahayogi_str']+' '+utils.resource_strings['planet_str']+':'+ \
            utils.PLANET_NAMES[sahayogi_planet]
    yh,yl = avayogi_sphuta(dob, tob, place)
    ynak = utils.nakshatra_pada(yh*30+yl)
    ystr += line_sep+utils.resource_strings['avayogi_sphuta_str']+' '+utils.resource_strings['raasi_str']+':'+\
            utils.RAASI_LIST[yh]+' '+utils.resource_strings['longitude_str']+':'+utils.to_dms(yl,is_lat_long='plong')
    ynak = utils.nakshatra_pada(yh*30+yl)
    ystr += line_sep+utils.resource_strings['avayogi_sphuta_str']+' '+utils.resource_strings['nakshatra_str']+':'+ \
            utils.NAKSHATRA_LIST[ynak[0]-1]
    yogi_planet = [l for l,naks in const.nakshathra_lords.items() if ynak[0]-1 in naks][0]
    ystr += line_sep+utils.resource_strings['avayogi_sphuta_str']+' '+utils.resource_strings['planet_str']+':'+ \
            utils.PLANET_NAMES[yogi_planet]
    print(ystr)
    exit()
    from jhora.tests import pvr_tests
    pvr_tests.sphuta_tests()