from jhora import const, utils
from jhora.panchanga import drik as M          # change to the module under test
Date, place = M.Date, M.Place('Chennai,India', 13.0878, 80.2785, 5.5)

sank_rule = const.SANKRANTI_RULE.SUNRISE_TO_SUNRISE

#"""
d = Date(2000, 3, 15)
for i in range(400):
    tm,td = M.tamil_solar_month_and_date(d,place,sankranti_rule=sank_rule)
    dm = M.days_in_tamil_month(d,place,sankranti_rule=sank_rule)
    print(d,tm,td,dm)
    jd = utils.julian_day_number(d,(0,0,0)) + 1
    y,m,dd,_ = utils.jd_to_gregorian(jd)
    d = Date(y,m,dd)
exit()
#"""
def old(d):                                     # the original loop, without the print
    sj = M.sunset(utils.gregorian_to_jd(d), place)[2]
    sl = M.solar_longitude(sj, place)
    _, c = M.tamil_solar_month_and_date(d, place, sankranti_rule=sank_rule)
    while not (29 < sl % 30 < 30):
        sj += 1; sl = M.solar_longitude(sj, place); c += 1
        if c > 80: return None
    return c

def new(d):
    return M.days_in_tamil_month(d, place, sankranti_rule=sank_rule)

def by_date_function(d):                        # the month length that tamil_solar_month_and_date itself implies
    m, day = M.tamil_solar_month_and_date(d, place, sankranti_rule=sank_rule)
    jd = utils.gregorian_to_jd(d); c = day
    for k in range(1, 34):
        y, mo, dd, _ = utils.jd_to_gregorian(jd + k)
        if M.tamil_solar_month_and_date(Date(y, mo, dd), place, sankranti_rule=sank_rule)[0] != m: break
        c += 1
    return c

n = a = b = 0
for y in range(2000, 2021):
    for mo in range(1, 13):
        for dd in (3, 15, 27):
            d = Date(y, mo, dd); n += 1
            o, nw, bd = old(d), new(d), by_date_function(d)
            if o != nw:
                a += 1
                if a <= 15: print('old != new          ', d, o, nw)
            if nw != bd:
                b += 1
                if b <= 15: print('new != date function', d, nw, bd)
print(M.days_in_tamil_month.__code__.co_varnames[:4], new.__code__.co_names[:3])
print(n, 'dates | old != new:', a, '| new != date function:', b)