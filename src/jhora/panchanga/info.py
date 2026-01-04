import sys, os
# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from jhora.panchanga import drik, vratha, pancha_paksha
from jhora import utils, const

def get_panchangam_resources_basic(jd,place):
    results_dict = {}
    year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
    key = utils.resource_strings['place_str']+': '; value = place.Place; place_str1 = value
    _lat = utils.to_dms(float(place.latitude),is_lat_long='lat')
    _long = utils.to_dms(float(place.longitude),is_lat_long='long')
    place_str2 = ' ('+_lat+', '+_long+', '+str(place.timezone)+')'
    value += place_str2
    results_dict[key] = value
    key = utils.resource_strings['vaaram_str']+': '
    value = utils.DAYS_LIST[drik.vaara(jd)]
    results_dict[key] = value
    date_str1 = str(year)+','+str(month)+','+str(day)
    date_str2 = str(day)+'-'+utils.MONTH_SHORT_LIST_EN[month-1]+'-'+str(year)
    time_str = utils.to_dms(birth_time_hrs)
    key = utils.resource_strings['date_of_birth_str']; value = date_str2+'  '+utils.resource_strings['time_of_birth_str']+' '+time_str
    results_dict[key] = value
    keys = [utils.resource_strings['solar_str']+' '+utils.resource_strings['year_str']+'/'+utils.resource_strings['month_str'],utils.resource_strings['lunar_year_month_str'],utils.resource_strings['lunar_year_month_str']]
    _calendar_type_str = ['',' ('+utils.resource_strings['amantha_str']+')',' ('+utils.resource_strings['purnimantha_str']+')']
    for _calendar_type in range(3):
        _month,_day,_year,adhik_maasa,nija_maasa = drik.vedic_date(jd, place, calendar_type=_calendar_type)
        adhik_maasa_str = ''; nija_month_str = ''
        if adhik_maasa: adhik_maasa_str = utils.resource_strings['adhika_maasa_str']
        if nija_maasa: nija_month_str = utils.resource_strings['nija_month_str']
        spl_month_text = utils.MONTH_LIST[_month-1]+' '+ adhik_maasa_str+nija_month_str+' '+str(_day)
        year_str = utils.YEAR_LIST[_year]
        key = keys[_calendar_type]
        value = utils.YEAR_LIST[_year]+' / '+utils.MONTH_LIST[_month-1]+' '+ \
                        adhik_maasa_str+nija_month_str+' '+str(_day)
        value += _calendar_type_str[_calendar_type]
        results_dict[key] = value
    key = utils.resource_strings['sunrise_str']
    value = drik.sunrise(jd,place)[1]
    results_dict[key] = value
    key = utils.resource_strings['sunset_str']
    value = drik.sunset(jd,place)[1]
    results_dict[key] = value
    key = utils.resource_strings['moonrise_str']
    value = drik.moonrise(jd, place)[1]
    results_dict[key] = value
    key = utils.resource_strings['moonset_str']
    value = drik.moonset(jd, place)[1]
    results_dict[key] = value        
    #"""
    _festival_list = vratha.get_festivals_of_the_day(jd,place)
    if len(_festival_list)>0:
        key = utils.resource_strings['todays_festivals_str']; value = ''
        for row in _festival_list:
            value += row['Festival_en']+'\n'
        results_dict[key] = value
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
        value = utils.NAKSHATRA_LIST[_next_nak-1]+' '+  \
                    ' ('+utils.PLANET_SHORT_NAMES[utils.nakshathra_lord(_next_nak)]+') '+ \
                    ' '+ utils.to_dms(nak[3]) + ' ' + utils.resource_strings['starts_at_str']
        results_dict[key] = value
    key = utils.resource_strings['raasi_str']
    rasi = drik.raasi(jd,place)
    frac_left = rasi[2]*100
    frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
    value = utils.RAASI_LIST[rasi[0]-1]+' '+utils.to_dms(rasi[1])+ ' ' + utils.resource_strings['ends_at_str']+frac_str
    results_dict[key] = value
    if rasi[1] < 24:
        _next_rasi = (rasi[0])%12+1
        value = utils.RAASI_LIST[_next_rasi-1]+' '+utils.to_dms(rasi[1])+ ' ' + utils.resource_strings['starts_at_str']
        results_dict[key] = value
    key = utils.resource_strings['tithi_str']; _tithi = drik.tithi(jd, place)
    frac_left = 100*utils.get_fraction(_tithi[1], _tithi[2], birth_time_hrs)
    frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
    _paksha = 0
    if _tithi[0] > 15: _paksha = 1 # V3.1.1
    value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[_tithi[0]-1]+ \
                    ' (' + utils.TITHI_DEITIES[_tithi[0]-1]+') '+ \
                    utils.to_dms(_tithi[2])+ ' ' + utils.resource_strings['ends_at_str']+frac_str
    results_dict[key] = value
    if _tithi[2] < 24:
        key = utils.resource_strings['tithi_str']
        _paksha = 0
        if (_tithi[0])%30+1 > 15: _paksha = 1 # V3.1.1
        value = utils.PAKSHA_LIST[_paksha]+' '+utils.TITHI_LIST[(_tithi[0])%30]+ \
                        ' (' + utils.TITHI_DEITIES[(_tithi[0])%30]+') '+ \
                        utils.to_dms(_tithi[2])+ ' ' + utils.resource_strings['starts_at_str']
        results_dict[key] = value
    key = utils.resource_strings['yogam_str']
    yogam = drik.yogam(jd,place)
    frac_left = 100*utils.get_fraction(yogam[1], yogam[2], birth_time_hrs)
    frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
    yoga_lord = ' ('+utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[yogam[0]-1][0]]+'/'+\
                    utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[yogam[0]-1][1]]+') '
    value = utils.YOGAM_LIST[yogam[0]-1] + yoga_lord + '  '+ \
                        utils.to_dms(yogam[2])+ ' ' + utils.resource_strings['ends_at_str']+frac_str
    results_dict[key] = value
    if yogam[2] < 24:
        yoga_lord = ' ('+utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[(yogam[0])%27][0]]+'/'+\
                        utils.PLANET_SHORT_NAMES[const.yogam_lords_and_avayogis[(yogam[0])%27][1]]+') '
        value = utils.YOGAM_LIST[(yogam[0])%27] + yoga_lord + '  '+ \
                            utils.to_dms(yogam[2])+ ' ' + utils.resource_strings['starts_at_str']
        results_dict[key] = value
    key = utils.resource_strings['karanam_str']
    karanam = drik.karana(jd,place)
    karana_lord = utils.PLANET_SHORT_NAMES[utils.karana_lord(karanam[0])]
    frac_left = 100*utils.get_fraction(karanam[1], karanam[2], birth_time_hrs)
    frac_str = ' ('+"{0:.2f}".format(frac_left)+'% ' + utils.resource_strings['balance_str']+' )'
    value = utils.KARANA_LIST[karanam[0]-1]+' ('+ karana_lord +') '+utils.to_dms(karanam[1])+' '+ \
            utils.resource_strings['starts_at_str']+ ' ' +utils.to_dms(karanam[2])+ ' ' + utils.resource_strings['ends_at_str']+frac_str
    results_dict[key] = value
    if karanam[2] < 24:
        _next_karana = karanam[0]%60+1
        karana_lord = utils.PLANET_SHORT_NAMES[utils.karana_lord(_next_karana)]
        value = utils.KARANA_LIST[_next_karana-1]+' ('+ karana_lord +') '+\
                        utils.to_dms(karanam[2])+ ' ' + utils.resource_strings['starts_at_str']
        results_dict[key] = value
    key = utils.resource_strings['raahu_kaalam_str']
    _raahu_kaalam = drik.raahu_kaalam(jd,place)
    value = _raahu_kaalam[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ _raahu_kaalam[1]+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    kuligai = drik.gulikai_kaalam(jd,place)
    key = utils.resource_strings['kuligai_str']
    value = kuligai[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ kuligai[1]+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    yamagandam = drik.yamaganda_kaalam(jd,place)
    key = utils.resource_strings['yamagandam_str'] 
    value = yamagandam[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ yamagandam[1]+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    car,ca_jd = drik.chandrashtama(jd, place); key = utils.resource_strings['chandrashtamam_str']
    value = utils.RAASI_LIST[car-1]+' '+utils.julian_day_to_date_time_string(ca_jd)+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    abhijit = drik.abhijit_muhurta(jd,place)
    key = utils.resource_strings['abhijit_str']
    value = abhijit[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ abhijit[1]+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    _dhurmuhurtham = drik.durmuhurtam(jd,place)
    key = utils.resource_strings['dhurmuhurtham_str']
    value = _dhurmuhurtham[0] + ' '+ utils.resource_strings['starts_at_str']+' '+ _dhurmuhurtham[1]+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    nm = drik.nishita_muhurtha(jd, place)
    key = utils.resource_strings['nishitha_muhurtha_str']+' : '
    value = utils.to_dms(nm[0]) +' '+utils.resource_strings['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ utils.resource_strings['ends_at_str']
    results_dict[key] = value
    y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob=utils.to_dms(fh,as_string=False)
    scd = drik.sahasra_chandrodayam(jd, place)
    if scd is not None:
        key = utils.resource_strings['sahasra_chandrodhayam_str']+' '+utils.resource_strings['day_str']
        value = str(scd[0])+'-'+'{:02d}'.format(scd[1])+'-'+'{:02d}'.format(scd[2])\
                #+' '+'{:02d}'.format(scd[3])+':'+'{:02d}'.format(scd[4])+':'+'{:02d}'.format(scd[5])
        results_dict[key] = value #'%-40s%-40s\n' % (key,value)        
    ag = drik.amrita_gadiya(jd, place)
    key = utils.resource_strings['amritha_gadiya_str']
    value = utils.to_dms(ag[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(ag[1])+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value        
    ag = drik.varjyam(jd, place)
    key = utils.resource_strings['varjyam_str']
    value = utils.to_dms(ag[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(ag[1])+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value        
    if len(ag)>2:
        value += '\t'+utils.to_dms(ag[2])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(ag[3])+' '+utils.resource_strings['ends_at_str']
    ay = drik.anandhaadhi_yoga(jd, place)
    key = utils.resource_strings['anandhaadhi_yoga_str']
    value = utils.resource_strings['ay_'+const.anandhaadhi_yoga_names[ay[0]]+'_str']+' '+utils.to_dms(ay[1])+' '+utils.resource_strings['starts_at_str']
    results_dict[key] = value
    key = utils.resource_strings['day_length_str']
    _day_length = drik.day_length(jd, place)
    value = utils.to_dms(_day_length).replace(' AM','').replace(' PM','')+' '+utils.resource_strings['hours_str']
    results_dict[key] = value
    key = utils.resource_strings['night_length_str']
    _night_length = drik.night_length(jd, place)
    value = utils.to_dms(_night_length).replace(' AM','').replace(' PM','')+' '+utils.resource_strings['hours_str']
    results_dict[key] = value
    key = utils.resource_strings['present_str']+' '+utils.resource_strings['triguna_str']
    tg = drik.triguna(jd, place)
    value = utils.resource_strings[const.triguna_names[tg[0]]+'_str']
    value += '\t'+utils.to_dms(tg[1])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(tg[2])+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    key = utils.resource_strings['present_str']+' '+utils.resource_strings['vivaha_chakra_palan']+' :'
    value = drik.vivaha_chakra_palan(jd, place)
    value = utils.resource_strings['vivaha_chakra_palan_'+str(value)]
    results_dict[key] = value
    key = utils.resource_strings['tamil_yogam_str']+' : '
    tg = drik.tamil_yogam(jd, place)
    value = utils.resource_strings[const.tamil_yoga_names[tg[0]]+'_yogam_str']
    value += ' ('+utils.resource_strings[const.tamil_yoga_names[tg[3]]+'_yogam_str']+')' if len(tg)>3 and tg[0] != tg[3] else '' 
    value += '\t'+utils.to_dms(tg[1])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(tg[2])+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    value = drik.pushkara_yoga(jd, place)
    if len(value)>0:
        key = utils.resource_strings['dwi_pushkara_yoga_str'] if value[0]==1 else utils.resource_strings['tri_pushkara_yoga_str']
        value = utils.to_dms(value[1])+' '+utils.resource_strings['starts_at_str']
        results_dict[key] = value
    value = drik.aadal_yoga(jd, place)
    if len(value)>0:
        key = utils.resource_strings['aadal_yoga_str']
        value = utils.to_dms(value[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(value[1])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
    value = drik.vidaal_yoga(jd, place)
    if len(value)>0:
        key = utils.resource_strings['vidaal_yoga_str']
        value = utils.to_dms(value[0])+' '+utils.resource_strings['starts_at_str']+' '+utils.to_dms(value[1])+' '+utils.resource_strings['ends_at_str']
        results_dict[key] = value
    key = utils.resource_strings['shiva_vaasa_str']
    sv = drik.shiva_vaasa(jd, place)
    value = utils.resource_strings['shiva_vaasa_str'+str(sv[0])]+' '+utils.to_dms(sv[1])+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    key = utils.resource_strings['agni_vaasa_str']
    av = drik.agni_vaasa(jd, place)
    value = utils.resource_strings['agni_vaasa_str'+str(av[0])]+' '+utils.to_dms(av[1])+' '+utils.resource_strings['ends_at_str']
    results_dict[key] = value
    directions = ['east','south','west','north','south_west','north_west','north_east','south_east']
    yv = drik.yogini_vaasa(jd, place)
    key = utils.resource_strings['yogini_vaasa_str']; value = utils.resource_strings[directions[yv]+'_str']
    results_dict[key] = value
    ds = drik.disha_shool(jd)
    key = utils.resource_strings['disha_shool_str']; value = utils.resource_strings[directions[ds]+'_str']
    results_dict[key] = value
    car,ca_jd = drik.chandrashtama(jd, place); key = utils.resource_strings['chandrashtamam_str']
    value = utils.RAASI_LIST[car-1]+' '+utils.julian_day_to_date_time_string(ca_jd)+' '+utils.resource_strings['ends_at_str']
    #"""
    key = utils.resource_strings['ayanamsam_str']+' ('+const._DEFAULT_AYANAMSA_MODE+') '
    value = drik.get_ayanamsa_value(jd)
    value = utils.to_dms(value,as_string=True,is_lat_long='lat').replace('N','').replace('S','')
    results_dict[key] = value
    #"""
    paksha_index = _paksha+1
    bird_index = pancha_paksha._get_birth_bird_from_nakshathra(nak[0],paksha_index)
    key = utils.resource_strings['pancha_pakshi_sastra_str']+' '+utils.resource_strings['main_bird_str'].replace('\\n',' ')+' : '
    value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
    results_dict[key] = value
    [kali_year, vikrama_year,saka_year] = drik.elapsed_year(jd,_month)
    key = utils.resource_strings['kali_year_str']
    value = str(kali_year)
    results_dict[key] = value
    key = utils.resource_strings['vikrama_year_str']
    value = str(vikrama_year)
    results_dict[key] = value
    key = utils.resource_strings['saka_year_str']; value = str(saka_year)
    results_dict[key] = value
    key = utils.resource_strings['kali_ahargana_str']
    value = str(drik.kali_ahargana_days(jd))+' '+utils.resource_strings['days_str']
    results_dict[key] = value    
    return results_dict
def get_panchangam_resources_special_tithis(jd,place):
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
def get_panchangam_resources_gowri(jd,place):
    results_dict = {}
    year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
    results_dict[utils.resource_strings['daytime_str']+' '+utils.resource_strings['gauri_choghadiya_str']+':']=''
    gc = drik.gauri_choghadiya(jd, place)
    _gc_types = ['gc_udvega_str','gc_chara_str','gc_laabha_str','gc_amrit_str','gc_kaala_str','gc_shubha_str','gc_roga_str']
    for g,(gt,st,et) in enumerate(gc):
        if g==8: # V4.3.6
            results_dict[utils.resource_strings['nighttime_str']+' '+utils.resource_strings['gauri_choghadiya_str']+':']=''
        key = '('+str(g+1)+') '+utils.resource_strings[_gc_types[gt]]
        value = st +' '+utils.resource_strings['starts_at_str']+ ' '+ et + ' '+ utils.resource_strings['ends_at_str']
        results_dict[key]=value
    return results_dict
def get_panchangam_resources_muhurtham(jd,place):
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
def get_panchangam_resources_horai(jd,place):
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
def get_panchangam_resources_misc(jd,place):
    results_dict = {}
    year, month, day,birth_time_hrs = utils.jd_to_gregorian(jd)
    bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
    pr = drik.panchaka_rahitha(jd, place)
    results_dict[utils.resource_strings['panchaka_rahitha_str']+' :']=''
    for prc,pr_beg,pr_end in pr[:1]:
        key=utils.resource_strings['muhurtha_str']+' ('+utils.resource_strings['good_str']+') ' if prc==0 \
                else utils.resource_strings[bad_panchakas[prc]+'_panchaka_str']
        value1 = utils.to_dms(pr_beg)+' '+utils.resource_strings['starts_at_str']
        value2 = utils.to_dms(pr_end)+' '+utils.resource_strings['ends_at_str']
        results_dict[key]=value1+' '+value2
        tb = drik.thaaraabalam(jd, place, return_only_good_stars=True)
        key = utils.resource_strings['thaaraabalam_str']+' :'
        star_list = [utils.NAKSHATRA_LIST[t-1] for t in tb]; knt=6
        star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
        key = ''; value = ''
        for sl in star_list:
            value += sl
        results_dict[key] = value
        cb = drik.chandrabalam(jd, place)
        key = utils.resource_strings['chandrabalam_str']+' :'
        star_list = [utils.RAASI_LIST[t-1] for t in cb]; knt=5
        star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
        value = ''
        for sl in star_list:
            value += sl
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
        value = _paksha +' '+utils.TITHI_LIST[kt[0]-1]; _t_deity = utils.TITHI_DEITIES[kt[0]-1]
        value_str=str(value)
        results_dict[key] = value
        key = utils.resource_strings['karaka_str']+' '+utils.resource_strings['yogam_str']
        ky = drik.karaka_yogam(jd, place)
        value = utils.YOGAM_LIST[ky[0]-1]
        value_str=str(value)
        results_dict[key] = value
    return results_dict
def get_panchangam_resources(jd,place,resource_type=None):
    try:
        if not isinstance(resource_type, list): resource_type = [resource_type]
        results_dict = {}
        if any(map(lambda v: v in [0,None,1], resource_type)):
            results_dict.update(get_panchangam_resources_basic(jd,place))
        if any(map(lambda v: v in [0,None,2], resource_type)): 
            results_dict.update(get_panchangam_resources_special_tithis(jd,place))
        if any(map(lambda v: v in [0,None,3], resource_type)): 
            results_dict.update(get_panchangam_resources_gowri(jd,place))
        if any(map(lambda v: v in [0,None,4], resource_type)):
            results_dict.update(get_panchangam_resources_muhurtham(jd,place))
        if any(map(lambda v: v in [0,None,5], resource_type)):
            results_dict.update(get_panchangam_resources_horai(jd,place))
        if any(map(lambda v: v in [0,None,6], resource_type)):
            results_dict.update(get_panchangam_resources_misc(jd,place))
        return results_dict
    except Exception as e:
        tb = sys.exc_info()[2]
        print(f"info:get_panchangam_resources: An error occurred: {e}",'line number',tb.tb_lineno)
if __name__ == "__main__":
    jd = utils.julian_day_number(drik.Date(1996,12,7),(10,34,0))
    place = drik.Place('Chennai, India',13.0878,80.2785,5.5)
    utils.set_language('en')
    results_dict = get_panchangam_resources(jd, place)
    for key,value in results_dict.items():
        print(key,value)