"""
Tests for step 1 (Ahargana) of vateshwara_sidhantha.py.
Run:  python test_vs_ahargana.py      (needs const.py with the VS block)
Everything is checked against the book's own printed numbers / relations, not against another program.
"""
import math, random
from fractions import Fraction as F
try:
    from jhora.panchanga import vateshwara_sidhantha as vs      # adjust to wherever you put the module
    from jhora import const
except ImportError:
    from jhora import vateshwara_sidhantha as vs
    from jhora import const

Y = const.VS_YUGA
M = const.VS_AHARGANA_METHOD
E = const.VS_EPOCH
random.seed(7)
n_checks = 0
def check(cond, msg):
    global n_checks
    n_checks += 1
    assert cond, "FAILED: " + msg

# ---- 1. constants: every derived relation printed in Sec.1-3 -------------------------------------
check(Y.SOLAR_DAYS == Y.SOLAR_YEARS * 360, "solar days = years x 360")
check(Y.SOLAR_MONTHS == Y.SOLAR_YEARS * 12, "solar months")
check(Y.LUNAR_DAYS == Y.LUNAR_MONTHS * 30, "lunar days = lunar months x 30")
check(Y.INTERCALARY_MONTHS == Y.LUNAR_MONTHS - Y.SOLAR_MONTHS, "intercalary months")
check(Y.LUNAR_DAYS - Y.SOLAR_DAYS == 30 * Y.INTERCALARY_MONTHS, "lunar days - solar days = intercalary days")
check(Y.OMITTED_DAYS == Y.LUNAR_DAYS - Y.CIVIL_DAYS == 25082520, "omitted days (Table 6 misprints 2,50,82,250)")
check(Y.RISINGS_OF_ASTERISMS == Y.CIVIL_DAYS + Y.SOLAR_YEARS == 1582237560, "risings of asterisms (Sec.2 vs.1)")
check(F(Y.CIVIL_DAYS, Y.SOLAR_YEARS) == F(13149313, 36000), "civil days per year 13149313/36000")
check(F(Y.CIVIL_DAYS, Y.SOLAR_YEARS) == 360 + F(189313, 36000) == 365 + F(9313, 36000) == 364 + F(45313, 36000),
      "civil days per year in the 3 forms of Methods 9/10/11")
check(F(30 * Y.INTERCALARY_MONTHS, Y.SOLAR_YEARS) == F(66389, 6000), "intercalary days per year (vs.10d-11)")
check(F(Y.INTERCALARY_MONTHS, Y.SOLAR_MONTHS) == F(66389, 2160000), "intercalary months per solar month (vs.24-26)")
check(F(Y.OMITTED_DAYS, Y.LUNAR_DAYS) == F(209021, Y.LUNAR_DAYS // 120), "omitted per lunar day (vs.24-26)")
check(const.VS_REVOLUTIONS[const._MOON] - 13 * const.VS_REVOLUTIONS[const._SUN] == Y.INTERCALARY_MONTHS,
      "Moon revs - 13 x Sun revs = intercalary months (Sec.4 vs.26)")
check(const.VS_REVOLUTIONS[const._MOON] - const.VS_REVOLUTIONS[const._SUN] == Y.LUNAR_MONTHS, "Moon - Sun revs = lunar months")

# ---- 2. epoch: independent Julian-calendar computation ------------------------------------------
def julian_calendar_jdn(year, month, day):          # JDN (noon) of a Julian-calendar date; astronomical years
    a = (14 - month) // 12; yy = year + 4800 - a; mm = month + 12 * a - 3
    return day + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083
jdn = julian_calendar_jdn(-3101, 2, 18)             # 3102 BC = astronomical year -3101
check(jdn == 588466, "JDN of 18 Feb 3102 BC (Julian) is 588466")
check(const.VS_KALI_EPOCH_JD == jdn - 0.5, "VS_KALI_EPOCH_JD is the 0h starting that day")
check(math.floor(jdn + 1.5) % 7 == 5 == const.VS_KALI_EPOCH_WEEKDAY, "that day is a Friday")

# ---- 3. kali_ahargana_days / ahargana ------------------------------------------------------------
check(vs.kali_ahargana_days(const.VS_KALI_EPOCH_JD, None) == 0, "epoch midnight -> 0")
check(vs.kali_ahargana_days(const.VS_KALI_EPOCH_JD + 0.999, None) == 0, "still 0 at the end of epoch day")
check(vs.kali_ahargana_days(const.VS_KALI_EPOCH_JD + 1.0, None) == 1, "next midnight -> 1")
check(vs.kali_ahargana_days(const.VS_KALI_EPOCH_JD - 0.001, None) == -1, "just before the epoch -> -1")
HE = vs.Place('Hoffman Estates', 42.06, -88.12, -5.0)              # vs.Place is used everywhere a place is needed
check(abs(HE.longitude + 88.12) < 1e-12 and HE.name == 'Hoffman Estates' and HE.timezone == -5.0, "vs.Place fields")
for _ in range(2000):
    jd = random.uniform(588465.5, 2500000.0)
    a, f = vs.kali_ahargana_days(jd, None, return_fraction=True)
    check(0.0 <= f < 1.0, "fraction in [0,1)")
    check(abs((a + f) - vs.ahargana(jd)) < 1e-6, "ahargana(jd) = whole + fraction")
    check((a + 5) % 7 == math.floor(jd + 1.5) % 7, "weekday identity (Ahargana+5)%7")
    check(vs.vs_lord_of_day(a) == math.floor(jd + 1.5) % 7, "vs_lord_of_day")
    check(vs.kali_ahargana_days(jd, HE) == a, "place is accepted for signature parity and does not change the Ahargana")
    check(vs.kali_ahargana_days(jd, HE, return_fraction=True) == (a, f), "same with return_fraction")
# modern anchor: 2000-01-01 12:00 is JD 2451545.0 (a Saturday); that civil day starts at JD 2451544.5
a = vs.kali_ahargana_days(2451545.0, None)
check(a == 1863079 and (a + 5) % 7 == 6, "2000-01-01 -> Ahargana 1863079, a Saturday")

# ---- 4. weekday facts of the 4 epochs vs the book's OWN constants --------------------------------
C = Y.CIVIL_DAYS
check(vs.vs_ahargana_epoch_offset(E.BRAHMA_BIRTH) == 9782551985550210, "Brahma-epoch offset = printed 9,78,25,51,98,55,50,210")
for ep in E:
    off = vs.vs_ahargana_epoch_offset(ep)
    # a day that is Friday from Kaliyuga must come out as the same weekday from every epoch
    check((const.VS_EPOCH_WEEKDAY[ep] + off) % 7 == const.VS_EPOCH_WEEKDAY[E.KALIYUGA],
          "epoch weekday consistent with civil-days-in-a-yuga for %s" % ep.name)
    for k in range(50):
        a = random.randint(0, 10 ** 7)
        check(vs.vs_lord_of_day(vs.vs_ahargana_since_epoch(a, ep), ep) == vs.vs_lord_of_day(a), "same weekday from any epoch")
        # vs.20: counted BACKWARDS from 7 x span, same answer as forward counting
        span = 7 * C
        back = (const.VS_EPOCH_WEEKDAY[E.KALIYUGA] - ((span - a) % 7)) % 7
        check(back == vs.vs_lord_of_day(a), "backward counting (vs.20) equals forward counting")

# ---- 5. lunar / solar Ahargana (vs.21) -----------------------------------------------------------
for _ in range(200):
    A = random.randint(1, 3 * 10 ** 6)
    la = vs.vs_lunar_ahargana(A)
    check(la == F(A * Y.LUNAR_DAYS, C), "lunar Ahargana = A x L / C")
    check(vs.vs_solar_ahargana(la) == F(A * Y.SOLAR_DAYS, C), "solar Ahargana = A x S / C")

# ---- 6. the methods of Sec.3 ----------------------------------------------------------------------
def resolves(quotient, A):
    """ The book's rule: integer part, +1 or -1, chosen by the lord of the day (raises if more than 1 day away). """
    return vs.vs_resolve_ahargana(quotient, weekday=vs.vs_lord_of_day(A)) == A
def nearest(x):                                   # nearest whole count, half up
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)
# NOTE on inputs: the book's "+/-1" rule presumes the elapsed counts are the NEAREST whole numbers. If they are
# truncated instead, the quotient can be up to C/S = 1.0146 days short, and in about 1.4% of cases the result is
# 2 days from the true Ahargana -- outside the book's rule. The tests below therefore feed nearest counts.
for _ in range(2000):
    A = random.randint(10 ** 5, 3 * 10 ** 6)
    # Method 4: solar days elapsed -> Ahargana
    se = nearest(F(A * Y.SOLAR_DAYS, C))
    check(resolves(vs.vs_ahargana_solar_days(se), A), "Method 4 resolved by the lord of the day")
    # Method 1: any (years, months, days) with the same solar-day count
    yrs, rem = divmod(se, 360); mo, d = divmod(rem, 30)
    q1 = vs.vs_ahargana_general(yrs, mo, d)
    check(q1 == F(se * C, Y.SOLAR_DAYS), "Method 1 collapses exactly to solar days x C/S")
    check(resolves(q1, A), "Method 1 resolved")
    # Method 5 (exact residues from the book's own derivation) and Method 6
    omitted = (A * Y.OMITTED_DAYS) // C; r_o = (A * Y.OMITTED_DAYS) % C
    lunar = A + omitted
    n_int = (lunar * Y.INTERCALARY_MONTHS) // Y.LUNAR_DAYS; r_i = (lunar * Y.INTERCALARY_MONTHS) % Y.LUNAR_DAYS
    check(vs.vs_ahargana_residues(n_int, r_i, r_o) == A, "Method 5 exact")
    check(vs.vs_ahargana_omitted_days(F(omitted) + F(r_o, C)) == A, "Method 6 exact")
    # Method 2 / Other-second collapse for whole months (d = 0)
    sm = se // 30
    check(vs.vs_ahargana_other_second(sm, 0) == F(sm * 30 * C, Y.SOLAR_DAYS), "Other-second collapses to solar days x C/S")
    # Other-first uses approximate constants: must agree with the exact collapse to a hundredth of a day
    check(abs(vs.vs_ahargana_other_first(se) - F(se * C, Y.SOLAR_DAYS)) < F(1, 100), "Other-first approximation error < 0.01 day")
for _ in range(500):
    yrs = random.randint(1, 5100); exact = (yrs * C) // Y.SOLAR_YEARS
    check(math.floor(vs.vs_ahargana_end_of_solar_year(yrs)) == exact, "Method 10 = civil days in the years")
    check(math.floor(vs.vs_ahargana_end_of_solar_year_alt(yrs)) == exact, "Method 11 = civil days in the years")
    check(vs.vs_ahargana_end_of_solar_year_alt(yrs) == 364 * yrs + vs.vs_shorter_ahargana(yrs), "Ahargana = 364 x years + shorter Ahargana")
    check(vs.vs_ahargana_other_third(yrs, 0) == F(yrs * C, Y.SOLAR_YEARS), "Other-third")
    # Method 9 (suddhi = 0, nothing elapsed since Caitra) is the civil days of the years
    check(vs.vs_ahargana_suddhi(yrs, 0, 0, 0) == F(yrs * C, Y.SOLAR_YEARS), "Method 9 with no Caitra part")
# Method 2 on consistent inputs (whole solar months whose lunar-month count agrees with the true calendar)
agree = total = 0
for _ in range(3000):
    A = random.randint(10 ** 5, 3 * 10 ** 6)
    ld = (A * Y.LUNAR_DAYS) // C; lm, d = divmod(ld, 30)
    sm = nearest(F(A * Y.SOLAR_MONTHS, C))
    total += 1
    if (sm * Y.LUNAR_DAYS) // Y.SOLAR_DAYS == lm:
        agree += 1
        check(resolves(vs.vs_ahargana_shorter(sm, d), A), "Method 2 resolved")
check(agree > 0.4 * total, "Method 2 test used a meaningful share of inputs (%d/%d)" % (agree, total))

# ---- 7. dispatcher + deliberate NotImplemented ---------------------------------------------------
check(vs.ahargana_from_calendar(jd=2451545.3, place=None) == vs.kali_ahargana_days(2451545.3, None), "dispatcher default")
check(vs.ahargana_from_calendar(jd=2451545.3, place=HE) == vs.kali_ahargana_days(2451545.3, HE), "dispatcher default with vs.Place")
check(vs.ahargana_from_calendar(M.END_OF_SOLAR_YEAR, years=5000) == (5000 * C) // Y.SOLAR_YEARS, "dispatcher Method 10")
for name in (vs.vs_ahargana_adhimasa_sesa, vs.vs_ahargana_sun_moon_known):
    try: name(); check(False, "should raise")
    except NotImplementedError: check(True, "raises")
# the Lagna (step 6) is implemented: a longitude in [0, 360) at the Kali-epoch-based Julian day of today in Hoffman Estates
lag = vs._ascendant_longitude(2451545.0, HE)
check(isinstance(lag, float) and 0.0 <= lag < 360.0, "Lagna is available (step 6 done)")
print("ALL %d CHECKS PASSED" % n_checks)
