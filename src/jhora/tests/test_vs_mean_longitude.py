"""
Tests for step 2 (mean longitudes) of vateshwara_sidhantha.py.
Run:  python test_vs_mean_longitude.py      (needs const.py with the VS block)
Expected values are computed here from the book's PRINTED rules with exact Fraction arithmetic, independently of the
module's own code path.  Every place is a vs.Place.
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
C = Y.CIVIL_DAYS
PM = const.VS_PRIME_MERIDIAN_LONGITUDE
ON_PM = vs.Place('prime meridian', 23.18, PM, 5.5)
random.seed(11)
n_checks = 0
def check(cond, msg):
    global n_checks
    n_checks += 1
    assert cond, "FAILED: " + msg
def circ(a, b):                                    # smallest angular difference, degrees
    return abs((a - b + 180.0) % 360.0 - 180.0)
def book_longitude(k, rev, period=C, epoch=0.0):   # the book's rule: k x rev / period revolutions (exact)
    return float(F(epoch) + 360 * ((F(k * rev, period)) % 1)) % 360.0
SUNRISE_JD0 = const.VS_KALI_EPOCH_JD + const.VS_MEAN_SUNRISE_DAY_FRACTION   # sunrise at Lanka on the epoch day
S, MO, MA, ME, JU, VE, SA = const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER, const._VENUS, const._SATURN
PLANETS = (S, MO, MA, ME, JU, VE, SA)

# ---- 0. model id ---------------------------------------------------------------------------------
check(const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA == 8, "VS model id is 8")
check(const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA_MODERN_SIGHRA == 9, "SS modern-sighra id moved to 9")

# ---- 1. the epoch positions (Tables 8, 9) vs Table 4 + Sec.4 vs.54, recomputed independently -----
def vs54_degrees(R):                               # (R + R/40) signs + 613 R / 4480 minutes
    return float((F(R) + F(R, 40)) * 30 + F(613 * R, 4480) / 60)
for p, R in const.VS_APOGEE_REVOLUTIONS_BRAHMA.items():
    check(circ(vs54_degrees(R), const.VS_APOGEE_AT_KALI[p]) < 0.5 / 3600, "Table 8 apogee reproduces (arcsec) %s" % p)
for p, R in const.VS_NODE_REVOLUTIONS_BRAHMA.items():
    check(circ(-vs54_degrees(R), const.VS_NODE_AT_KALI[p]) < 0.5 / 3600, "Table 9 node reproduces (arcsec) %s" % p)
# Mercury / Venus node: actual revolutions = vs.18 big number mod (sighrocca revolutions - Sun revolutions)
check(int("98827145641" "8719") % (const.VS_REVOLUTIONS[ME] - const.VS_REVOLUTIONS[S]) == const.VS_NODE_REVOLUTIONS_BRAHMA[ME] == 162719,
      "Mercury node revolutions (vs.18-20)")
check(int("1961276406" "36895") % (const.VS_REVOLUTIONS[VE] - const.VS_REVOLUTIONS[S]) == const.VS_NODE_REVOLUTIONS_BRAHMA[VE] == 60895,
      "Venus node revolutions (vs.18-20)")
check(const.VS_BRAHMA_LIFE_YUGAS == 72576000, "yugas in the life of Brahma (Table 4 heading)")

# ---- 2. the planets are all at 0 at the start of Kaliyuga (3/4 yuga x revolutions is whole) ------
for p in PLANETS:
    check((F(3, 4) * const.VS_REVOLUTIONS[p]).denominator == 1, "3/4 yuga x revolutions whole for %s" % p)
# (the Moon's node and apogee are NOT whole at 3/4 yuga -- the book gives their epoch positions explicitly: Tables 8, 9)
for p in PLANETS:
    check(circ(vs._mean_longitude_raw(SUNRISE_JD0, ON_PM, p), 0.0) < 1e-6, "mean longitude 0 at epoch sunrise for %s" % p)
check(circ(vs._mean_longitude_raw(SUNRISE_JD0, ON_PM, const._RAHU), 180.0) < 1e-6, "Rahu 6 signs at epoch")
check(circ(vs._mean_longitude_raw(SUNRISE_JD0, ON_PM, const._KETU), 0.0) < 1e-6, "Ketu 0 at epoch")
check(circ(vs._mean_apogee_longitude(SUNRISE_JD0, ON_PM, MO), 90.0) < 1e-6, "Moon apogee 3 signs at epoch")
for p, v in const.VS_APOGEE_AT_KALI.items():
    check(circ(vs._mean_apogee_longitude(SUNRISE_JD0, ON_PM, p), v) < 1e-6, "apogee Table 8 at epoch %s" % p)
for p, v in const.VS_NODE_AT_KALI.items():
    check(circ(vs._mean_node_longitude(SUNRISE_JD0, ON_PM, p), v) < 1e-6, "node Table 9 at epoch %s" % p)

# ---- 3. THE BOOK'S RULE at every mean sunrise at Lanka: longitude = Ahargana x revolutions / civil days ----
for _ in range(3000):
    k = random.randint(0, 2_000_000)               # Ahargana counted from sunrise at Lanka on the epoch day
    jd = SUNRISE_JD0 + k
    for p in PLANETS:
        got = vs._mean_longitude_raw(jd, ON_PM, p)
        check(circ(got, book_longitude(k, const.VS_REVOLUTIONS[p])) < 2e-6, "book rule %s at k=%d" % (p, k))
    check(circ(vs._mean_longitude_raw(jd, ON_PM, const._RAHU),
               book_longitude(k, -const.VS_MOON_NODE_REVOLUTIONS, epoch=180.0)) < 2e-6, "book rule Rahu")
    check(circ(vs._mean_longitude_raw(jd, ON_PM, const._KETU), vs._mean_longitude_raw(jd, ON_PM, const._RAHU) + 180.0) < 1e-9, "Ketu = Rahu+180")
    check(circ(vs._mean_apogee_longitude(jd, ON_PM, MO),
               book_longitude(k, const.VS_MOON_APOGEE_REVOLUTIONS, epoch=90.0)) < 2e-6, "Moon apogee rule")
    for p, R in const.VS_APOGEE_REVOLUTIONS_BRAHMA.items():
        want = book_longitude(k, R, C * const.VS_BRAHMA_LIFE_YUGAS, const.VS_APOGEE_AT_KALI[p])
        check(circ(vs._mean_apogee_longitude(jd, ON_PM, p), want) < 2e-6, "planet apogee rule %s" % p)
    for p, R in const.VS_NODE_REVOLUTIONS_BRAHMA.items():
        want = book_longitude(k, -R, C * const.VS_BRAHMA_LIFE_YUGAS, const.VS_NODE_AT_KALI[p])
        check(circ(vs._mean_node_longitude(jd, ON_PM, p), want) < 2e-6, "planet node rule %s" % p)
    # relations the book derives from the revolution numbers (Sec.4 vs.26, 23, 28, 25)
    sun, moon = vs._mean_longitude_raw(jd, ON_PM, S), vs._mean_longitude_raw(jd, ON_PM, MO)
    inter = 360 * float((F(k * Y.INTERCALARY_MONTHS, C)) % 1)
    check(circ(moon - 13 * sun, inter) < 3e-5, "Moon - 13 Sun = Ahargana x intercalary months / C  (vs.26)")
    check(circ(moon - sun, 360 * float(F(k * Y.LUNAR_MONTHS, C) % 1)) < 3e-5, "Moon - Sun = Ahargana x lunar months / C  (vs.27)")
    check(circ(sun, 360 * float((F(k * Y.RISINGS_OF_ASTERISMS, C)) % 1)) < 2e-6, "Sun from risings of asterisms (vs.25)")
    vyat = 2 * (const.VS_REVOLUTIONS[S] + const.VS_REVOLUTIONS[MO])
    check(circ(sun + moon, 360 * float(F(k * vyat, 2 * C) % 1)) < 3e-5, "Sun + Moon = half the vyatipata revolutions (vs.28)")

# ---- 4. the instant between two sunrises: linear continuation with the same daily motion -----------
for _ in range(1000):
    k = random.randint(0, 2_000_000); frac = random.random() * 0.9 + 0.05
    for p in (S, MO, MA, SA):
        a = vs._mean_longitude_raw(SUNRISE_JD0 + k, ON_PM, p)
        b = vs._mean_longitude_raw(SUNRISE_JD0 + k + frac, ON_PM, p)
        check(circ(b - a, frac * vs._vs_daily_motion(p)) < 3e-5, "linear in time for %s" % p)
    # midnight handling: the instant just before / after local midnight is continuous
    jd_mid = const.VS_KALI_EPOCH_JD + k + 1
    l0 = vs._mean_longitude_raw(jd_mid - 1e-7, ON_PM, MO); l1 = vs._mean_longitude_raw(jd_mid + 1e-7, ON_PM, MO)
    check(circ(l0, l1) < 1e-4, "no jump at civil midnight")
# daily motions: revolutions x 360 / civil days; compare with the book's own figures
check(abs(vs._vs_daily_motion(S) - 59.1359 / 60.0) < 1e-4, "Sun daily motion ~ 59'8\" (Sec.4 vs.14)")
check(abs(vs._vs_daily_motion(MO) - 790.5833 / 60.0) < 5e-4, "Moon daily motion ~ 790'35\" (Sec.4 vs.14)")
check(vs._vs_daily_motion(const._RAHU) < 0 and vs._vs_daily_motion(const._KETU) < 0, "nodes retrograde")
check(abs((vs._vs_daily_motion(MO) - vs._vs_daily_motion(S)) * 60 - 731.45) < 0.02, "Moon - Sun motion ~ 731'27\" (Sec.4 vs.16)")

# ---- 5. longitude (desantara) correction: Sec.8 vs.6, 10, 12 ----------------------------------------
for dlong in (-30.0, -7.5, 0.0, 1.0, 15.0, 37.4):
    east = vs.Place('x', 12.0, PM + dlong, 5.5)
    for p in PLANETS + (const._RAHU,):
        dc = vs._desantara_correction(east, p)
        check(abs(dc - (-(dlong / 360.0) * vs._vs_daily_motion(p))) < 1e-12, "desantara = -(longitude in time) x daily motion")
        check((dc < 0) == (dlong > 0) or dlong == 0 or vs._vs_daily_motion(p) < 0, "subtract for EAST, add for WEST")
    # equivalent to moving the clock: local mean time at an eastern place is AHEAD of the prime meridian's
    jd = SUNRISE_JD0 + 123456 + 0.4
    for p in (S, MO, MA):
        a = vs._mean_longitude_raw(jd, east, p)
        b = vs._mean_longitude_raw(jd - dlong / 360.0, ON_PM, p)
        check(circ(a, b) < 1e-5, "place east by %.1f deg == clock shifted by that longitude in time (%s)" % (dlong, p))
check(vs._desantara_correction(None, S) == 0.0, "place=None on the prime meridian")
# vs.10 worked in ghatis: longitude in nadis x daily motion (minutes) / 60 -> minutes
east15 = vs.Place('x', 12.0, PM + 15.0, 5.5)
nadis = 15.0 / 360.0 * 60.0
check(abs(abs(vs._desantara_correction(east15, S)) * 60 - nadis * (vs._vs_daily_motion(S) * 60) / 60.0) < 1e-9, "vs.10 formula in nadis")

# ---- 6. node & apogee motion: direction, rate ---------------------------------------------------------
j0, j1 = SUNRISE_JD0 + 700000.0, SUNRISE_JD0 + 700001.0
check(circ(vs._mean_longitude_raw(j1, ON_PM, const._RAHU) - vs._mean_longitude_raw(j0, ON_PM, const._RAHU),
           -const.VS_MOON_NODE_REVOLUTIONS * 360.0 / C) < 1e-5, "Rahu moves -0.0530 deg/day")
check(circ(vs._mean_apogee_longitude(j1, ON_PM, MO) - vs._mean_apogee_longitude(j0, ON_PM, MO),
           const.VS_MOON_APOGEE_REVOLUTIONS * 360.0 / C) < 1e-5, "Moon apogee moves +0.1114 deg/day")
check(circ(vs._mean_node_longitude(j1, ON_PM, const._RAHU), vs._mean_longitude_raw(j1, ON_PM, const._RAHU)) < 1e-12, "Moon node = Rahu")
check(circ(vs._mean_node_longitude(j1, ON_PM, MO), vs._mean_longitude_raw(j1, ON_PM, const._RAHU)) < 1e-12, "Moon node via _MOON")
# planets' apogees / nodes are essentially fixed (Table 4 revolutions: "of no utility", book Sec.1 after Table 4)
for p in const.VS_APOGEE_REVOLUTIONS_BRAHMA:
    d = circ(vs._mean_apogee_longitude(SUNRISE_JD0 + 2_000_000, ON_PM, p), const.VS_APOGEE_AT_KALI[p])
    check(d < 0.01, "planet apogee drifts < 0.01 deg in 5,500 years: %s (%.5f)" % (p, d))

# ---- 6b. planets the book does not cover give a clear error, not a KeyError ------------------------------
try: vs._mean_longitude_raw(2451545.0, None, const._URANUS); check(False, "Uranus should be refused")
except ValueError: check(True, "Uranus refused with ValueError")

# ---- 7. place=None == a place on the prime meridian; vs.Place with a zone ------------------------------
check(vs._mean_longitude_raw(2451545.0, None, S) == vs._mean_longitude_raw(2451545.0, ON_PM, S), "place=None == prime meridian")
HE = vs.Place('Hoffman Estates', 42.06, -88.12, -5.0)
check(circ(vs._mean_longitude_raw(2451545.0, HE, MO), vs._mean_longitude_raw(2451545.0 - (HE.longitude - PM) / 360.0, ON_PM, MO)) < 1e-5,
      "a western place (vs.Place) equals the prime meridian at the clock shifted by the longitude in time")
print("ALL %d CHECKS PASSED" % n_checks)
