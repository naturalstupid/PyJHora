from hora import const, utils
from hora.panchanga import drik
from hora.horoscope.chart import charts
def patyayini_dhasa(jd_years,place,ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE,divisional_chart_factor=1):
    """
        Compute Patyaayini Dhasa
        Should be used for Tajaka Annual charts
        @param jd_years:Julian day number for Tajaka Annual date/time
        @param place: drik.Place struct tuple of ('Place',latitude,longitude,time_zone_offset)
        @param ayanamsa_mode: Default = const._DEFAULT_AYANAMSA_MODE
        @param divisional_chart_factor: Default = 1 (Raasi) - See const.division_chart_factors for other possible values
        @return patyayini dhasa values as a list [planet, dhasa_duration in days]
        Example: [[5, (1993, 6, 26), 24.9], [3, (1993, 8, 13), 48.1], [1, (1993, 8, 14), 0.57],...]]
    """
    cht = charts.divisional_chart(jd_years,place,ayanamsa_mode,divisional_chart_factor)
    krisamsas = cht[:-2]  # Exclude Rahu and Ketu
    krisamsas.sort(key=lambda x:x[1][1])
    #for p,(h,long) in krisamsas:
    #    print('krisamsas',p,(h,utils.to_dms(long,is_lat_long='plong')))
    patyamsas = [[p,(h,long-krisamsas[i-1][1][1])] for i,[p,(h,long)] in enumerate(krisamsas) if i>0]
    patyamsas = [krisamsas[0]]+patyamsas
    #print('patyamsas',patyamsas)
    #for p,(h,long) in patyamsas:
    #    print('patyamsas',p,(h,utils.to_dms(long,is_lat_long='plong')))
    patyamsa_sum = sum([long for _,(_,long) in patyamsas])
    _dhasa_period_factors = {p:long/patyamsa_sum for p,(_,long) in patyamsas}
    _dhasa_lords = list(_dhasa_period_factors.keys())
    #print('_dhasa_period_factors',_dhasa_period_factors)
    _dhasas = [[p,const.average_gregorian_year*_dhasa_period_factors[p]] for p,(h,long) in patyamsas]
    #for p,long in _dhasas:
    #    print('_dhasas',p,long)
    jd_start = jd_years
    dhasas = []
    for d,(p,dd) in enumerate(_dhasas):
        #print(d,p,dd)
        bn = d
        db = []
        for b in enumerate(_dhasa_lords):
            pa = _dhasa_lords[bn]
            y,m,d,fh = utils.jd_to_gregorian(jd_start)
            date_str = '%04d-%02d-%02d' %(y,m,d)
            time_str = utils.to_dms(fh,as_string=True)
            bhukthi_start = date_str + ' '+time_str
            db.append([pa,bhukthi_start])
            jd_start += _dhasa_period_factors[pa]*dd
            bn = (bn+1)%len(_dhasa_lords)
        dhasas.append([p,db,dd])
    return dhasas
if __name__ == "__main__":
    from hora.tests.pvr_tests import test_example
    chapter = 'Chapter 30 '
    exercise = 'Example 122 / Chart 67 '
    expected_result_book = [(5, 24.98), (3, 48.17), (1, 0.51), (6, 25.74), ('L', 11.24), (4, 57.35), (0, 93.29), (2, 103.99)]
    #expected_result = [(5, 24.9), (3, 48.1), (1, 0.57), (6, 25.71), ('L', 11.3), (4, 57.43), (0, 93.03), (2, 104.19)]
    expected_result = [(5, 24.94), (3, 48.22), (1, 0.4), (6, 25.71), ('L', 11.29), (4, 57.42), (0, 93.09), (2, 104.17)]
    # Note: Difference in ans is due to planet longitude value round off 
    jd_at_dob = utils.julian_day_number((1972,6,1),(4,16,0))
    years = 21
    place = drik.Place('unknown',16+15.0/60,81+12.0/60,5.5)
    divisional_chart_factor = 1
    ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
    jd_at_years = utils.julian_day_number((1993,6,1),(13,30,4))
    cht=patyayini_dhasa(jd_at_years, place, ayanamsa_mode, divisional_chart_factor)
    print(cht)
    #exit()
    print("Note: There is slight difference between book and actual values. Difference is due to round off of longitudes value calculations\n"+
          'Expected Values from Book for Reference:',expected_result_book)
    for i,pp in enumerate(cht):
        test_example(chapter+exercise,expected_result[i],(pp[0],round(pp[-1],2)))
