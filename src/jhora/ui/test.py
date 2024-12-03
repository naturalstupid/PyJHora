from jhora.panchanga import drik
from jhora.horoscope.chart import charts
from jhora import utils, const
from isort import place
def compare_planet_positions(planet_positions):
    result = []
    planet_names = [*range(const._planets_upto_ketu)]+['Md', 'L']
    planet_indices = {name: idx for idx, name in enumerate(planet_names)}

    for planet, (rasi, longitude) in planet_positions:
        if planet in planet_indices:
            planet_index = planet_indices[planet]
        else:
            planet_index = int(planet)
        
        tolerance = const.mrityu_bhaga_tolerances[planet] if planet in ['Md', 'L'] else const.mrityu_bhaga_tolerances[planet_index]
        
        base_longitude = const.mrityu_bhaga_base_longitudes[rasi][planet_index]
        long_diff = abs(longitude - base_longitude)
        if long_diff <= tolerance:
            result.append((planet_names[planet_index], rasi, long_diff))
    
    return result

# Example usage
mrityu_bhaga_base_longitudes = const.mrityu_bhaga_base_longitudes
mrityu_bhaga_tolerances = const.mrityu_bhaga_tolerances
#dob = drik.Date(1931,10,12); tob=(7,13,5); place = drik.Place('machili',16+10/60,81+8/60,5.5)
dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
jd = utils.julian_day_number(dob, tob); dcf = 3
planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=dcf)
"""
planet_positions = [[0, (5, 24.874369607123896)], [1, (6, 2.3291522842439463)],
                    [2, (6, 24.0221181353092)], [3, (5, 20.044048800728007)], [4, (3, 24.713050887525938)], 
                    [5, (6, 3.883130064160781)], [6, (8, 24.081449569232802)], [7, (11, 11.66590220662357)], 
                    [8, (5, 11.665902206623514)],['Md',(9, 19.084431751879606)],
                    ['L', (6, 12.066847362334187)], ]
"""
planet_positions = planet_positions+[['Md',drik.maandi_longitude(dob,tob,place)]]
print(planet_positions)
#print(maandi)
#exit()
print(compare_planet_positions(planet_positions))
