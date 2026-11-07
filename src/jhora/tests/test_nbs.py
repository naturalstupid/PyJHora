import datetime as dt, types, enum
from jhora.panchanga import nepal_bs_calendar as B

# 1. round trip over EVERY day of the table, and continuity
d = dt.date.fromordinal(B._FIRST_ORDINAL); last = dt.date.fromordinal(B._LAST_ORDINAL); n = 0; prev = None; errs = []
while d <= last:
    r = B.ad_to_bs(d.year, d.month, d.day)
    if r is None: errs.append(("None", d)); break
    if B.bs_to_ad(*r) != d: errs.append(("round trip", d, r))
    if prev:
        py, pm, pd = prev; y, m, dd = r
        ok = (y, m, dd) == (py, pm, pd + 1) and pd + 1 <= B.month_days(py, pm) or (dd == 1 and ((y, m) == (py, pm + 1) if pm < 12 else (y, m) == (py + 1, 1)) and pd == B.month_days(py, pm))
        if not ok: errs.append(("continuity", d, prev, r))
    prev = r; n += 1; d += dt.timedelta(days=1)
print(f"1. {n} days checked ({dt.date.fromordinal(B._FIRST_ORDINAL)} .. {last}): round trip + continuity errors: {errs[:3] or 'none'}")
# 2. outside the table
print("2. outside the table ->", B.ad_to_bs(1844, 4, 10), B.ad_to_bs(2143, 4, 16), B.ad_to_bs(1500, 1, 1), B.ad_to_bs(3000, 1, 1), "(expected None x4)")
# 3. known anchors
for bs, ad in (((2080,1,1),(2023,4,14)),((2081,1,1),(2024,4,13)),((2082,1,1),(2025,4,14)),((2083,1,1),(2026,4,14)),((2000,1,1),(1943,4,14))):
    got = B.bs_to_ad(*bs); print(f"3. BS {bs[0]} Baisakh 1 = {got}  expected {dt.date(*ad)}  {'OK' if got == dt.date(*ad) else '<<< WRONG'}")
# 4. year lengths: every BS year is 365 or 366 days, and BS 2083 month lengths
print("4. year lengths seen:", sorted(set(B._YEAR_DAYS.values())), "| BS 2083 months:", B.YEAR_MONTH_DAYS_BS[2083], "sum", sum(B.YEAR_MONTH_DAYS_BS[2083]))
# 5. invalid input
for bad in ((2083, 13, 1), (2083, 6, 32), (1900, 1, 1), (2083, 0, 1)):
    try: B.bs_to_ad(*bad); print("5. NOT rejected:", bad)
    except ValueError: pass
print("5. invalid BS dates are rejected with ValueError")

# 6. the real integration: vedic_date branch + fallback, with PyJHora-like stand-ins
class CALENDAR_TYPE(enum.IntEnum):
    SOLAR = 0; LUNAR_AMANTHA = 1; LUNAR_PURNIMANTHA = 2; HIJRI_ISLAMIC = 3; GREGORIAN = 4; NANAKSHAHI_PUNJAB = 5; BANGLADESH_REFORMED = 6; NEPAL_BIKRAM_SAMBAT = 7
const = types.SimpleNamespace(CALENDAR_TYPE=CALENDAR_TYPE, SANKRANTI_RULE=types.SimpleNamespace(TAMIL_NADU_SUNSET_RULE=1))
class utils:                                         # same signature as PyJHora's utils.jd_to_gregorian: (year, month, day, fraction of hour)
    @staticmethod
    def jd_to_gregorian(jd):
        o = int(jd - 1721424.5 + 0.5); fh = ((jd + 0.5) % 1) * 24; x = dt.date.fromordinal(o); return x.year, x.month, x.day, fh
def jd_of(y, m, d, hour=0.0):
    return dt.date(y, m, d).toordinal() + 1721424.5 - 0.5 + hour / 24.0
calls = []
def solar_month_date(jd, place, rule=None, gh=None): calls.append(jd); return 3, 17            # stand-in used only by the fallback
def _nepal_bikram_sambat_civil_date(jd, place):
    """(month, day, year) of the Nepali Bikram Sambat date; month 1 = Baisakh ... 12 = Chaitra"""
    g_year, g_month, g_day, _ = utils.jd_to_gregorian(jd)
    r = B.ad_to_bs(g_year, g_month, g_day)
    if r is not None:
        return r[1], r[2], r[0]
    # outside BS 1901-2199: approximate with the solar engine (sunset rule). The month starts can be a day off.
    month_idx, day = solar_month_date(jd, place, const.SANKRANTI_RULE.TAMIL_NADU_SUNSET_RULE)
    bs_year = g_year + (56 if (month_idx >= 9 or (month_idx == 8 and g_month == 1)) else 57)
    return month_idx + 1, day, bs_year
def vedic_date(jd, place, calendar_type=None):
    if calendar_type == const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT:
        m, d, y = _nepal_bikram_sambat_civil_date(jd, place)
        return m, d, y, False, False, False
print("\n6. vedic_date(NEPAL_BIKRAM_SAMBAT):")
for ad in ((2026,4,14),(2026,10,18),(2027,4,13),(2027,4,14)):
    print("  ", ad, "->", vedic_date(jd_of(*ad, hour=10.5), None, const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT))
print("   same civil day at 00:00 and at 23:59 give the same BS date:", vedic_date(jd_of(2026,10,18,0.0),None,7)[:3]==vedic_date(jd_of(2026,10,18,23.98),None,7)[:3])
print("   fallback (outside the table, 2150-01-01):", vedic_date(jd_of(2150,1,1),None,const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT), "| solar engine called:", len(calls)==1)
print("   a date inside the table never calls the solar engine:", (lambda c0: (vedic_date(jd_of(2026,5,5),None,7), len(calls)==c0)[1])(len(calls)))
