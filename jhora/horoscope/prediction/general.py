import json
from hora.horoscope.chart import charts, house
from hora import utils, const
from hora.panchanga import drik
_lang_path = const._LANGUAGE_PATH

def get_prediction_resources(language='en'):
    """
        get resources from prediction_msgs_<lang>.txt
        @param language: Two letter language code. en, hi, ka, ta, te
        @return json strings from the resource file as dictionary 
    """
    json_file = _lang_path + const._DEFAULT_PREDICTION_JSON_FILE_PREFIX+language+'.json'
    f = open(json_file,"r",encoding="utf-8")
    msgs = json.load(f)
    return msgs

def _get_general_lagna_rasi_prediction(jd,place,prediction_msgs,language=const._DEFAULT_LANGUAGE):
    janma_rasi = drik.raasi(jd, place)[0]-1
    results = {}
    source_count = 2
    for s in range(source_count):
        ks = utils.resource_strings['janma_rasi_str']+'_'+str(s+1)
        results[ks] = "<html><b>"+utils.resource_strings['general_prediction_str']+"</b><br>"
        #results[ks] += "<b>"+prediction_msgs['general_prediction_caution']+"</b><br>"
        results[ks] += "<b>"+prediction_msgs['janma_raasi_'+str(s+1)]['source']+"</b><br>"
        pdict = prediction_msgs['janma_raasi_'+str(s+1)][str(janma_rasi+1)]
        for k,v in pdict.items():
            results[ks] += "<b>"+k+"</b><br>"+v+"<br>"
    return results
def _get_planets_in_houses_prediction(planet_positions,prediction_msgs):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lagna_house = p_to_h['L']
    ks = utils.resource_strings['planets_str']
    results = {}
    results[ks] = "<html>"#<b>"+ks+"</b><br>"
    #results[ks] += "<b>"+utils.resource_strings['general_prediction_caution']+"</b><br>"
    planet_msgs = prediction_msgs['planets_in_houses']
    #print('planet msgs',planet_msgs)
    for planet in [*range(9)]:
        planet_house = house.get_relative_house_of_planet(lagna_house,p_to_h[planet])
        pl_msg = planet_msgs[str(planet_house)][planet]
        #print(planet,planet_house,pl_msg)
        key = utils.PLANET_NAMES[planet]+'-'+utils.resource_strings['house_str']+'#'+str(planet_house)+":"
        results[ks] += "<b>"+key+"</b><br>"+pl_msg+"<br>"
    return results
def _get_lords_in_houses_prediction(planet_positions,prediction_msgs):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lagna_house = p_to_h['L']
    ks = utils.resource_strings['houses_str']
    results = {}
    results[ks] = "<html>"#<b>"+ks+"</b><br>"
    #results[ks] += "<b>"+utils.resource_strings['general_prediction_caution']+"</b><br>"
    planet_msgs = prediction_msgs['lord_of_a_house_joining_lord_of_another_house']
    #print('planet msgs',planet_msgs)
    for h in [*range(12)]:
        lord = const._house_owners_list[(h+lagna_house)%12]
        house_of_lord = house.get_relative_house_of_planet(lagna_house,p_to_h[lord])
        key = "Lord of House#"+str(h+1)+" in house#"+str(house_of_lord)
        #print('key',key)
        pl_msg = planet_msgs[str(h+1)][house_of_lord-1]
        results[ks] += "<b>"+key+"</b><br>"+pl_msg+"<br>"
    return results
def get_prediction_details(jd_at_dob,place,language=const._DEFAULT_LANGUAGE):
    prediction_msgs = get_prediction_resources(language=language)
    #print('prediction keys',prediction_msgs.keys())
    results = {}
    planet_positions = charts.rasi_chart(jd_at_dob, place)
    results1 = _get_general_lagna_rasi_prediction(jd_at_dob,place,prediction_msgs,language=language)
    results.update(results1)
    results2 = _get_planets_in_houses_prediction(planet_positions,prediction_msgs)
    results.update(results2)
    results3 = _get_lords_in_houses_prediction(planet_positions,prediction_msgs)
    results.update(results3)
    return results
if __name__ == "__main__":
    lang = 'te'
    utils.set_language(lang)
    res = utils.resource_strings
    from hora.horoscope.chart import charts
    from hora.panchanga import drik
    dob = (1996,12,7); tob = (10,34,0); jd_at_dob = utils.julian_day_number(dob, tob)
    place_as_tuple = drik.Place('Chennai, India',13.0878,80.2785,5.5)
    planet_positions = charts.rasi_chart(jd_at_dob, place_as_tuple)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    print(h_to_p)
    #prediction_msgs = get_prediction_resources(language=lang)
    ks = get_prediction_details(jd_at_dob,place_as_tuple, language=lang)
    print(ks)
