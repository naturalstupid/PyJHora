from collections import Counter
import numpy as np
from hora import const
from hora.panchanga import panchanga

planet_list = ['sun','moon','mars','mercury','jupiter','venus','saturn','lagnam']
raasi_list=['Mesham','Rishabam','Mithunam','Katakam','Simmam','Kanni','Thulaam','Vrichigam','Dhanusu','Makaram','Kumbam','Meenam']
raasi_index = lambda planet,planet_positions_in_chart: [i for i,raasi in enumerate(planet_positions_in_chart) if planet !='L' and planet.lower() in raasi.lower() ][0]
def get_ashtaka_varga(planet_positions_in_chart,chart_has_planet_names=True):
    """
        get binna, samudhaya and prastara varga from the given horoscope planet positions
        @param planet_positions_in_chart: 1-D array [0..11] with planets in each raasi
            Example: ['','','','','Mars','Rahu','Moon/Venus','Sun','Mercury/Jupiter','Lagnam','','Saturn/Ketu']
        @return: 
            binna_ashtaka_varga - 2-D List [0..7][0..7] 0=Sun..7=Lagnam
            samudhaya ashtaka varga - 1D List [0..11] 0=Aries 11=Pisces
            prastara ashtaka varga - 3D List [0..7][0..7][0..12]
    """
    raasi_ashtaka = [[0 for r in range(12)] for p in range(9)]
    prastara_ashtaka_varga  = [[[0 for r in range(12)] for p1 in range(10)] for p2 in range(9)]
    for key in const.ashtaka_varga_dict.keys():
        p = int(key)
        #planet = planet_list[p]
        planet_raasi_list = const.ashtaka_varga_dict[key]
        for op,other_planet in enumerate(planet_raasi_list):
            if chart_has_planet_names:
                pr = raasi_index(planet_list[op],planet_positions_in_chart)
            else:
                pr = raasi_index(str(op),planet_positions_in_chart)
            for raasi in other_planet:
                r = (raasi-1+pr) % 12
                raasi_ashtaka[p][r] +=1
                prastara_ashtaka_varga[p][op][r] = 1
                prastara_ashtaka_varga[p][-1][r] += 1
    binna_ashtaka_varga = raasi_ashtaka[0:8][:]
    prastara_ashtaka_varga = prastara_ashtaka_varga[0:8][0:9][:]
    samudhaya_ashtaka_varga = np.asarray(binna_ashtaka_varga).sum(axis=0).tolist()
    return binna_ashtaka_varga, samudhaya_ashtaka_varga,prastara_ashtaka_varga
def _trikona_sodhana(binna_ashtaka_varga):
    bav = binna_ashtaka_varga[:]
    for p in range(7):
        for r in range(4):
            if bav[p][r]==0 or bav[p][r+4]==0 or bav[p][r+8]==0:
                continue
            elif bav[p][r]==bav[p][r+4] and bav[p][r+4]==bav[p][r+8]:
                bav[p][r]=0
                bav[p][r+4]=0
                bav[p][r+8]=0
            else:
                min_value = min([bav[p][r],bav[p][r+4],bav[p][r+8]])
                bav[p][r] -= min_value
                bav[p][r+4] -= min_value
                bav[p][r+8] -= min_value
    return bav
def _ekadhipatya_sodhana(binna_ashtaka_varga_after_trikona,chart_1d):
    bav = binna_ashtaka_varga_after_trikona[:]
    rasi_owners=[4,3,(0,7),(2,5),(8,11),(1,6),(9,10)]
    for p in range(2,7):
        r1,r2 = rasi_owners[p]
        r1_occupied = not (chart_1d[r1].strip() == '')
        r2_occupied = not (chart_1d[r2].strip() == '')
        if (bav[p][r1]==0 or bav[p][r2]==0) or (r1_occupied and r2_occupied) :
            continue
        elif (not r1_occupied) and (not r2_occupied ): # both empty
            if bav[p][r1] != bav[p][r2]:
                min_value = min([bav[p][r1],bav[p][r2]])
                bav[p][r1] = min_value
                bav[p][r2] = min_value
            else:
                bav[p][r1] = 0
                bav[p][r2] = 0
        else:
            if (r1_occupied): #r2 is empty
                if (bav[p][r2] < bav[p][r1]):
                    bav[p][r2] = 0
                else:
                    bav[p][r2] = bav[p][r1]
            else: #r1 is empty
                if (bav[p][r1] < bav[p][r2]):
                    bav[p][r1] = 0
                else:
                    bav[p][r1] = bav[p][r2]
    return bav
def _get_planet_positions(chart_1d):
    planet_houses = [-1 for p in range(7)]
    for p,planet in enumerate(planet_list[0:-1]): # Excluding Lagnam
        for house,rasi in enumerate(chart_1d):
            if planet.lower() in rasi.lower():
                planet_houses[p] = house
                break
    return planet_houses
def _sodhya_pindas(binna_ashtaka_varga_after_ekadhipatya,chart_1d):
    rasimana_multipliers = [7,10,8,4,10,6,7,8,9,5,11,12]
    grahamana_multipliers = [5,5,8,5,10,7,5]
    bav = binna_ashtaka_varga_after_ekadhipatya[:]
    raasi_pindas = [0 for p in range(7)]
    graha_pindas = [0 for p in range(7)]
    sodhya_pindas = [0 for p in range(7)]
    for p in range(7):
        raasi_pindas[p] = sum(np.multiply(bav[p][:],rasimana_multipliers))
    planet_houses = _get_planet_positions(chart_1d)
    for p in range(7):
        graha_pindas[p] = sum([ grahamana_multipliers[i]*bav[p][pr] for i,pr in enumerate(planet_houses)])
        sodhya_pindas[p] = raasi_pindas[p]+graha_pindas[p]
    return raasi_pindas,graha_pindas,sodhya_pindas
def sodhaya_pindas(binna_ashtaka_varga,planet_positions_in_chart):
    binna_ashtaka_varga_after_trikona = _trikona_sodhana(binna_ashtaka_varga)
    binna_ashtaka_varga_after_ekadhipatya = _ekadhipatya_sodhana(binna_ashtaka_varga_after_trikona,planet_positions_in_chart)
    raasi_pindas,graha_pindas,sodhya_pindas = _sodhya_pindas(binna_ashtaka_varga_after_ekadhipatya,planet_positions_in_chart)
    return raasi_pindas,graha_pindas,sodhya_pindas
if __name__ == "__main__":
    # Chart 7 from the book
    planet_positions_in_chart = ['Saturn/Moon/Rahu','','','','','','Ketu/Jupiter','Lagnam','Mercury/Mars','Sun','Venus','']
    binna_ashtaka_varga,samudhaya_ashtaka_varga,prastara_ashtaka_varga = get_ashtaka_varga(planet_positions_in_chart)
    print('binna_ashtaka_varga\n',binna_ashtaka_varga)
    print('samudhaya_ashtaka_varga\n',samudhaya_ashtaka_varga)
    print('prastara_ashtaka_varga\n',prastara_ashtaka_varga)
    bav = _trikona_sodhana(binna_ashtaka_varga)
    print('after trikona\n',bav)
    bav = _ekadhipatya_sodhana(bav,planet_positions_in_chart)
    print('after _ekaadhipatya_sodhana\n',bav)
    raasi_pindas,graha_pindas,shodya_pindas = _sodhya_pindas(bav,planet_positions_in_chart)
    print('raasi_pindas\n',raasi_pindas)
    print('graha_pindas\n',graha_pindas)
    print('_sodhya_pindas\n',shodya_pindas)
    exit()
    for planet in range(8):
        print(planet_list[planet],binna_ashtaka_varga[planet])
    print(samudhaya_ashtaka_varga)
    print('prastara_ashtaka_varga\n',prastara_ashtaka_varga)