from hora import const, utils
from hora.panchanga import panchanga
from hora.horoscope.chart import charts
def patyayini_dhasa(jd_years,place,ayanamsa_mode='Lahiri',divisional_chart_factor=1):
    """
        Compute Patyaayini Dhasa
        Should be used for Tajaka Annual charts
        @param jd_years:Julian day number for Tajaka Annual date/time
        @param place: panchanga.Place struct tuple of ('Place',latitude,longitude,time_zone_offset)
        @param ayanamsa_mode: Default = 'Lahiri'
        @param divisional_chart_factor: Default = 1 (Raasi) - See const.division_chart_factors for other possible values
        @return patyayini dhasa values as a list [planet, dhasa_duration in days]
        Example: [[5, (1993, 6, 26), 24.9], [3, (1993, 8, 13), 48.1], [1, (1993, 8, 14), 0.57],...]]
    """
    cht = charts.divisional_chart(jd_years,place,ayanamsa_mode,divisional_chart_factor)
    cht_1 = cht[:-2]  # Exclude Rahu and Ketu
    cht_1.sort(key=lambda x:x[1][1])
    max_long = max(cht_1, key=lambda x:x[1][-1])[1][1]
    cht_2 = []
    for i,[p,(h,long)] in enumerate(cht_1):
        if i==0:
            cht_2.append([p,round(long/max_long*const.average_gregorian_year,2)])
        else:
            long1 = long - cht_1[i-1][1][1]
            cht_2.append([p,round(long1/max_long*const.average_gregorian_year,2)])
    jd_start = jd_years
    cht3 = []
    for p,dd in cht_2:
        jd_end = jd_start + dd
        dhasa_end = utils.jd_to_gregorian(jd_end)[:3]
        cht3.append([p,dhasa_end,dd])
        jd_start = jd_end        
    return cht3
if __name__ == "__main__":
    jd_at_dob = utils.julian_day_number((1996,12,7),(10,34,0))
    place = panchanga.Place('unknown',13.0389,80.2619,5.5)
    divisional_chart_factor = 9
    ayanamsa_mode = 'Lahiri'
    years = 26
    jd_at_years = jd_at_dob + years*const.sidereal_year
    cht=patyayini_dhasa(jd_at_years, place, ayanamsa_mode, divisional_chart_factor)
    print(cht)
    years = 30
    jd_at_years = jd_at_dob + years*const.sidereal_year
    cht=patyayini_dhasa(jd_at_years, place, ayanamsa_mode, divisional_chart_factor)
    print(cht)
    