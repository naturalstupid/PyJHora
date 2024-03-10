from hora.panchanga import drik
from hora import const,utils
from hora.horoscope.chart import house, charts

def tri_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _tri_sphuta = (moon_long+asc_long+gulika_long)%360
    return _tri_sphuta
def chatu_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tri_sphuta= tri_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    return (sun_long+_tri_sphuta)%360
def pancha_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    _chatu_sphuta= chatu_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    return (rahu_long+_chatu_sphuta)%360
def prana_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    asc_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _prana_long = (asc_long*5 + gulika_long) %360
    return _prana_long
def deha_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _deha_long = (moon_long*8 + gulika_long) %360
    return _deha_long
def mrityu_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    gulika = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
    gulika_long = gulika[0]*30+gulika[1]
    _mrityu_long = (gulika_long*7 + sun_long) %360
    return _mrityu_long
def sookshma_tri_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    _prana_long = prana_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _deha_long = deha_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _mrityu_long = mrityu_sphuta(dob, tob, place, ayanamsa_mode, divisional_chart_factor, years, months, sixty_hours)
    _sookshma_long = (_prana_long + _deha_long + _mrityu_long) %360
    return _sookshma_long
def beeja_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    venus_long = planet_positions[6][1][0]*30+planet_positions[6][1][1]
    _beeja_long = (sun_long + jupiter_long + venus_long)%360
    return _beeja_long
def kshetra_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    jupiter_long = planet_positions[5][1][0]*30+planet_positions[5][1][1]
    mars_long = planet_positions[3][1][0]*30+planet_positions[3][1][1]
    _kshetra_long = (moon_long + jupiter_long + mars_long)%360
    return _kshetra_long
def tithi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (moon_long - sun_long) %360
    return _tithi_long
def yoga_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    moon_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _yoga_long = (moon_long + sun_long) %360
    return _yoga_long
def rahu_tithi_sphuta(dob,tob,place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1,years=1,months=1,sixty_hours=1):
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=ayanamsa_mode, 
                                        divisional_chart_factor=divisional_chart_factor, years=years, 
                                        months=months, sixty_hours=sixty_hours)
    rahu_long = planet_positions[8][1][0]*30+planet_positions[8][1][1]
    sun_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
    _tithi_long = (rahu_long - sun_long) %360
    return _tithi_long
if __name__ == "__main__":
    from hora.tests import pvr_tests
    pvr_tests.sphuta_tests()
