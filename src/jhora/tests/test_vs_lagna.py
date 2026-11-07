"""
Tests for step 6 of vateshwara_sidhantha.py: Chapter III (Sun's declination, day-radius, earthsine, ascensional difference, rising times
of the signs, Lagna) and the true sunrise / sunset that use them.
Run:  python test_vs_lagna.py      (needs const.py with the VS block, version with the Chapter III constants)

How the module is checked
  * every book identity the verses state (formula 1 = formula 2, 416/1023 = Rsin 24 / R, Rsin(3 signs - d) = day-radius, vs.27 constants
    ~ vs.26 values, local rising times add up to 21600, ...) is re-derived here independently of the module;
  * the Lagna walk of Sec.8 vs.10(c-d)-12 is compared with an independent implementation (cumulative rising-time function + search);
    lagnakala (vs.16, 20) must undo it;
  * math.sin / math.tan / math.atan2 appear ONLY as test oracles ("exact geometry"), to bound the size of the book's own approximations
    (its Rsine table and its sign-by-sign rising times) and to catch a wrong sign or direction, which would give errors of tens of degrees.
Every place is a vs.Place.
"""
import math, random
try:
    from jhora.panchanga import vateshwara_sidhantha as vs      # adjust to wherever you put the module
    from jhora import const
except ImportError:
    from jhora import vateshwara_sidhantha as vs
    from jhora import const

random.seed(31)
n_checks = 0
def check(cond, msg):
    global n_checks
    n_checks += 1
    assert cond, "FAILED: " + msg
def circ(a, b): return (a - b + 180.0) % 360.0 - 180.0
R = const.VS_RSINE_RADIUS
S = const._SUN
HE = vs.Place('Hoffman Estates', 42.06, -88.12, -5.0)
BLR = vs.Place('Bangalore', 12.97, 77.59, 5.5)
UJN = vs.Place('Ujjain', 23.18, 75.79, 5.5)
SYD = vs.Place('Sydney', -33.87, 151.21, 10.0)
EPS = math.radians(24.0)
def x_decl(lam): return math.asin(math.sin(math.radians(lam)) * math.sin(EPS))                    # exact geometry (oracle)
def x_ra(lam): return math.degrees(math.atan2(math.cos(EPS) * math.sin(math.radians(lam)), math.cos(math.radians(lam)))) % 360
def x_asc(theta, lat):
    t, p = math.radians(theta), math.radians(lat)
    return math.degrees(math.atan2(math.cos(t), -(math.sin(EPS) * math.tan(p) + math.cos(EPS) * math.sin(t)))) % 360
def x_asc_diff_asus(lam, lat):
    x = math.tan(math.radians(lat)) * math.tan(x_decl(lam))
    return math.degrees(math.asin(max(-1.0, min(1.0, x)))) * 60.0

# =====================================================================================================
# 1. CONSTANTS AND THE BOOK'S OWN IDENTITIES (Sec.3 vs.1-2, Sec.8 vs.8)
# =====================================================================================================
check(sum(const.VS_RISING_TIMES_LANKA) == 5400, "1669 + 1796 + 1935 = 5400 asus = a quadrant")
check(const.VS_ASUS_PER_DAY == 21600 == 4 * 5400, "21600 asus in a circle / civil day")
check(abs(const.VS_RSIN_GREATEST_DECLINATION - vs._vs_rsine(24 * 60)) < 1.0 / 60, "printed Rsin 24 deg = 1398'13\" agrees with Table 13 within 1\"")
check(abs(const.VS_RSIN_GREATEST_DECLINATION / R / (416 / 1023) - 1) < 2.5e-4, "Rsin 24 / R = 416/1023 (Sec.3 vs.1: 'formulae (1) and (2) are equivalent')")
check(const.vs_declination_method_default == const.VS_DECLINATION_METHOD.RSINE_OF_GREATEST_DECLINATION, "default = formula (1)")
for lam in range(0, 361, 3):
    f1 = vs._vs_declination_rsine(lam, method=const.VS_DECLINATION_METHOD.RSINE_OF_GREATEST_DECLINATION)
    f2 = vs._vs_declination_rsine(lam, method=const.VS_DECLINATION_METHOD.RATIO_416_1023)
    check(abs(f1 - f2) <= 3e-4 * max(abs(f1), 1.0), "declination formula (1) = formula (2) at %d deg" % lam)
    d = vs._sun_declination(lam)
    check(abs(d - math.degrees(x_decl(lam))) < 0.002, "declination vs exact geometry at %d deg (book's table error only)" % lam)
    check(abs(d + vs._sun_declination(360 - lam)) < 1e-9 or lam in (0, 360), "declination antisymmetric about 0/360 (%d)" % lam)
    if lam <= 180: check(abs(d - vs._sun_declination(180 - lam)) < 1e-9, "declination symmetric about 90 deg (%d)" % lam)
check(abs(vs._sun_declination(90.0) - 24.0) < 0.002 and abs(vs._sun_declination(270.0) + 24.0) < 0.002, "greatest declination +/-24 deg")
check(vs._sun_declination(0.0) == 0.0 and abs(vs._sun_declination(180.0)) < 1e-12, "zero at the equinoxes")
check(all(vs._sun_declination(l) > 0 for l in range(1, 180)) and all(vs._sun_declination(l) < 0 for l in range(181, 360)), "north for Aries..Virgo, south for Libra..Pisces")
# a different obliquity goes through Table 13 and keeps the identities
check(abs(vs._sun_declination(90.0, 23.5) - 23.5) < 0.002, "other obliquity: greatest declination = that obliquity")

# =====================================================================================================
# 2. DAY-RADIUS, EARTHSINE, PALABHA, ASCENSIONAL DIFFERENCE  (Sec.4 vs.1,3 / Sec.5 vs.1 / Sec.6 vs.1 / Sec.7 vs.1,3,24)
# =====================================================================================================
def rvers(arc_minutes):                    # Rversed-sine by linear reading of the Rversed-sine table (vs.58 applied to it)
    T, h = const.VS_RVERSED_TABLE, const.VS_RSINE_ELEMENTAL_ARC
    n = int(arc_minutes // h)
    return T[96] if n >= 96 else T[n] + (arc_minutes - n * h) * (T[n + 1] - T[n]) / h
for lam in range(0, 360, 7):
    rsd = vs._vs_declination_rsine(lam)
    dr = vs._vs_day_radius(rsd)
    check(abs(dr * dr + rsd * rsd - R * R) < 1e-6, "day-radius^2 + Rsin^2(declination) = R^2   (Sec.4 vs.1 formula 1)")
    d_arc = vs._vs_arc_from_rsine(abs(rsd))                                   # declination in minutes
    check(abs(dr - vs._vs_rsine(5400.0 - d_arc)) < 0.25, "day-radius = Rsin(3 signs - declination)   (Sec.4 vs.3 formula 5)")
    check(abs(dr - (R - rvers(d_arc))) < 0.25, "day-radius = R - Rvers(declination)   (Sec.4 vs.2 formula 4)")
    # formula (3), Rsin^2 / Rvers - R, is an algebraic identity but ill-conditioned when Rvers is read from the 56' table (errors of 2' to 175'),
    # so it is deliberately not tested numerically.
for lat in (-60.0, -33.87, -12.0, 0.0, 12.97, 23.18, 30.0, 42.06, 55.0, 66.0):
    P = vs._vs_palabha(lat)
    phi = abs(lat)
    check(abs(P - math.copysign(12.0 * vs._vs_rsine(phi * 60) / vs._vs_rsine((90 - phi) * 60), lat)) < 1e-9, "palabha = 12 Rsin(lat)/Rcos(lat)  (Sec.7 vs.10)")
    check(abs(P - 12.0 * math.tan(math.radians(lat))) <= 0.004 * max(abs(12.0 * math.tan(math.radians(lat))), 1.0), "palabha ~ 12 tan(lat) (angulas)")
    for lam in range(0, 360, 11):
        rsd = vs._vs_declination_rsine(lam)
        es = vs._vs_earthsine(rsd, lat)
        check(abs(es - rsd * P / 12.0) < 1e-6 * max(1.0, abs(es)), "earthsine = Rsin(decl) x palabha / 12   (Sec.5 vs.1 formula 2)")
        dr = vs._vs_day_radius(rsd)
        ad = vs._vs_asc_diff_asus(lam, lat)
        if abs(es) < 0.999 * dr:
            rs_ad = math.copysign(vs._vs_rsine(abs(ad)), ad)
            check(abs(rs_ad - es * R / dr) < 0.25, "Rsin(asc. diff.) = earthsine x R / day-radius   (Sec.7 vs.1)")
            sgn = 1.0 if lat >= 0 else -1.0
            agra = rsd * R / vs._vs_rsine((90 - phi) * 60)                       # Sec.6 vs.1 formula (2): agra = Rsin(decl) x R / Rcos(lat), signed by the declination
            check(abs(sgn * vs._vs_rsine(phi * 60) * agra / dr - es * R / dr) < 1e-6 * R, "Rsin(asc. diff.) = agra x Rsin(lat) / day-radius   (Sec.7 vs.3 formula 5)")
            check(abs(ad - x_asc_diff_asus(lam, lat)) < (0.3 if abs(lat) <= 45.0 else 2.0), "ascensional difference vs exact geometry (lat %.2f, long %d): %.3f asus" % (lat, lam, ad - x_asc_diff_asus(lam, lat)))
# sign rules and symmetries
check(vs._vs_asc_diff_asus(45.0, 0.0) == 0.0 and abs(vs._vs_asc_diff_asus(0.0, 42.0)) < 1e-9 and abs(vs._vs_asc_diff_asus(180.0, 42.0)) < 1e-9,
      "no ascensional difference on the equator or at the equinoxes")
for lat in (12.97, 42.06):
    for lam in range(1, 180, 9):
        a, b = vs._vs_asc_diff_asus(lam, lat), vs._vs_asc_diff_asus(360 - lam, lat)
        check(a > 0 > b and abs(a + b) < 1e-9, "north-latitude: + while the Sun is north, - while south (day longer/shorter than 15 ghatis)")
        check(abs(vs._vs_asc_diff_asus(lam, -lat) + a) < 1e-9, "latitude -> -latitude flips the sign")
check(abs(vs._general_cara_vinadis(75.0, 42.06) * 6.0 - vs._vs_asc_diff_asus(75.0, 42.06)) < 1e-12, "cara in vinadis = asus / 6 (1 degree = 60 asus = 10 vinadis)")
polar = vs._vs_asc_diff_asus(90.0, 80.0)
check(abs(polar - 5400.0) < 1e-6, "polar case clamped to a quadrant (%.3f)" % polar)
check(abs(vs._vs_palabha(45.0) - 12.0) < 0.05, "palabha at 45 deg latitude = 12 angulas")
for bad in (91.0, -91.0):
    try: vs._vs_palabha(bad); check(False, "latitude beyond the pole refused")
    except ValueError: check(True, "latitude beyond the pole refused")
# semi-duration of the day (Sec.7 vs.24): 5400 +/- asus of ascensional difference
check(abs((5400.0 + vs._vs_asc_diff_asus(80.0, 42.06)) - 5400.0) > 100.0, "semi-duration of the day differs from 15 ghatis away from the equinox")

# =====================================================================================================
# 3. RISING TIMES (Sec.8 vs.1, 8) -- local table
# =====================================================================================================
base = vs._vs_base_rising_asus()
check(base == [1669, 1796, 1935, 1935, 1796, 1669, 1669, 1796, 1935, 1935, 1796, 1669] and abs(sum(base) - 21600) < 1e-9, "times of rising at Lanka (vs.8), 12 signs add up to 21600")
check([x * 6 for x in vs._base_rising_times_vinadis()] == base, "base rising times in vinadis = asus / 6")
m1 = vs._vs_base_rising_asus(method=const.VS_RISING_TIMES_METHOD.COMPUTED_METHOD_1)
check(all(abs(m1[i] - base[i]) < 3.0 for i in range(12)) and abs(sum(m1) - 21600) < 1e-6, "Method 1 of vs.1 through Table 13 gives the printed times within 3 asus: %s" % [round(x, 1) for x in m1[:3]])
m_eps = vs._vs_base_rising_asus(23.5)
check(abs(sum(m_eps) - 21600) < 1e-6 and m_eps[0] > m1[0] and m_eps[2] < m1[2], "other obliquity: Method 1 path works (a smaller obliquity makes Aries slower and Gemini faster)")
for lat in (-60.0, -33.87, -12.0, 0.0, 12.97, 23.18, 30.0, 42.06, 55.0):
    loc = vs._vs_local_rising_asus(lat)
    a = vs._vs_asc_diff_asus(30.0, lat); b = vs._vs_asc_diff_asus(60.0, lat) - a; c = vs._vs_asc_diff_asus(90.0, lat) - a - b
    book_table = [1669 - a, 1796 - b, 1935 - c, 1935 + c, 1796 + b, 1669 + a, 1669 + a, 1796 + b, 1935 + c, 1935 - c, 1796 - b, 1669 - a]  # the table of vs.8 (+ vs.9 mirror)
    check(all(abs(loc[i] - book_table[i]) < 1e-9 for i in range(12)), "local rising times = the table of Sec.8 vs.8 (lat %.2f)" % lat)
    check(abs(sum(loc) - 21600) < 1e-6, "local rising times of the 12 signs add up to 21600 (lat %.2f)" % lat)
    check(all(abs(loc[i] + loc[(i + 6) % 12] - 2 * base[i]) < 1e-9 for i in range(12)), "sign and its opposite: sum = 2 x Lanka time (lat %.2f)" % lat)
    check(all(abs(x * 6 - y) < 1e-9 for x, y in zip(vs._local_rising_times_vinadis(lat), loc)), "local rising times in vinadis = asus / 6")
    if lat == 0.0: check(all(abs(loc[i] - base[i]) < 1e-9 for i in range(12)), "on the equator local = Lanka times")
    if lat > 0: check(loc[0] < base[0] and loc[5] > base[5], "north latitude: Aries rises faster, Virgo slower than at Lanka")
    if lat < 0: check(loc[0] > base[0], "south latitude: Aries rises slower than at Lanka")
# vs.27 constants vs vs.26 computation
saved = const.vs_asc_diff_method_default
try:
    for lat, tol in ((12.97, 0.01), (23.18, 0.012), (42.06, 0.04)):
        const.vs_asc_diff_method_default = const.VS_ASC_DIFF_METHOD.COMPUTED
        loc1 = vs._vs_local_rising_asus(lat)
        const.vs_asc_diff_method_default = const.VS_ASC_DIFF_METHOD.CONSTANTS
        loc2 = vs._vs_local_rising_asus(lat)
        P = vs._vs_palabha(lat)
        ends = [k * P / 12.0 for k in const.VS_ASC_DIFF_SIGN_END_COEFFICIENTS]
        a, b, c = ends[0], ends[1] - ends[0], ends[2] - ends[1]
        check(all(abs(loc2[i] - (base[i] + [-a, -b, -c, c, b, a, a, b, c, -c, -b, -a][i])) < 1e-9 for i in range(12)), "CONSTANTS method = 714, 1294, 1530 x palabha / 12 at the sign ends")
        check(max(abs(x - y) for x, y in zip(loc1, loc2)) < tol * 1669 + 1.0, "vs.27 constants close to vs.26 computation at lat %.2f (%.1f asus)" % (lat, max(abs(x - y) for x, y in zip(loc1, loc2))))
        # the book's own example under vs.27: Aries / Taurus / Gemini = 714P/12, 580P/12, 236P/12 asus
        check(abs(a - 714 * P / 12) < 1e-9 and abs(b - 580 * P / 12) < 1e-9 and abs(c - 236 * P / 12) < 1e-9, "individual signs 714P/12, 580P/12, 236P/12 (vs.27 note)")
finally:
    const.vs_asc_diff_method_default = saved

# =====================================================================================================
# 4. LAGNA WALK  (Sec.8 vs.10(c-d)-12, 16, 19, 20) against an independent implementation
# =====================================================================================================
def cumulative(local):
    cum = [0.0]
    for t in local: cum.append(cum[-1] + t)
    return cum
def oblique_asc(lam, local, cum):                      # asus from 0 deg Aries to longitude lam, signs piecewise linear
    s = int(lam // 30) % 12
    return cum[s] + (lam - 30 * s) / 30.0 * local[s]
def lagna_independent(sun, elapsed, local):
    cum = cumulative(local)
    target = (oblique_asc(sun % 360, local, cum) + elapsed) % 21600.0
    s = max(i for i in range(12) if cum[i] <= target + 1e-12)
    s = min(s, 11)
    return (30 * s + (target - cum[s]) / local[s] * 30.0) % 360.0
for lat in (-33.87, 0.0, 12.97, 23.18, 42.06, 55.0):
    local = vs._vs_local_rising_asus(lat)
    for _ in range(1500):
        sun = random.uniform(0, 360); el = random.uniform(0, 21600)
        got = vs._vs_lagna_from_elapsed(sun, el, local)
        check(abs(circ(got, lagna_independent(sun, el, local))) < 1e-7, "Lagna walk == cumulative-ascension solution (lat %.2f, sun %.2f, %.0f asus)" % (lat, sun, el))
        back = vs.vs_lagnakala_asus(sun, got, local)
        check(abs(back - el) < 1e-6 or abs(back - el - 21600.0) < 1e-6 or abs(back - el + 21600.0) < 1e-6, "lagnakala undoes the walk (vs.16)")
    sun = random.uniform(0, 360)
    check(abs(circ(vs._vs_lagna_from_elapsed(sun, 0.0, local), sun)) < 1e-9, "no time elapsed -> Lagna = Sun")
    check(abs(circ(vs._vs_lagna_from_elapsed(sun, 21600.0, local), sun)) < 1e-6, "a full circle of asus brings the Lagna back to the Sun")
    # vs.19: the elapsed time is less than the rising time of the untraversed part of the Sun's sign
    s0 = int(sun // 30) % 12; within = sun - 30 * s0; rest = (30 - within) / 30.0 * local[s0]
    el = 0.5 * rest
    check(abs(circ(vs._vs_lagna_from_elapsed(sun, el, local), sun + el * 30.0 / local[s0])) < 1e-9, "vs.19: elapsed x 30 / own-sign rising time added to the Sun")
    # vs.20: Lagna and Sun in the same sign -> degrees between them x rising time / 30
    check(abs(vs.vs_lagnakala_asus(sun, sun + 0.4 * (30 - within), local) - 0.4 * (30 - within) * local[s0] / 30.0) < 1e-9, "vs.20: same sign")
    xs = [vs._vs_lagna_from_elapsed(sun, e, local) for e in range(0, 21601, 400)]
    unwrapped = [xs[0]]
    for x in xs[1:]: unwrapped.append(unwrapped[-1] + (x - unwrapped[-1]) % 360.0)
    check(all(unwrapped[i + 1] > unwrapped[i] for i in range(len(unwrapped) - 1)), "Lagna advances steadily with elapsed time (lat %.2f)" % lat)
# direction check: Lagna is AHEAD of the Sun after sunrise
check(0.0 < circ(vs._vs_lagna_from_elapsed(10.0, 300.0, vs._vs_local_rising_asus(42.06)), 10.0) < 40.0, "Lagna moves forward (towards Taurus) after sunrise")
# a south-latitude place: Aries rises slower, so 1669-a is replaced by 1669+|a|
check(vs._vs_local_rising_asus(-33.87)[0] > vs._vs_base_rising_asus()[0], "southern place has the opposite adjustment")
# bounded by exact geometry (test oracle): the book's sign-by-sign table, not a mistake
for lat, tol in ((12.97, 2.0), (23.18, 2.2), (42.06, 3.6)):
    local = vs._vs_local_rising_asus(lat); errs = []
    for _ in range(3000):
        lam = random.uniform(0, 360); t = random.uniform(0, 21600)
        d = x_decl(lam); H0 = math.degrees(math.acos(max(-1, min(1, -math.tan(math.radians(lat)) * math.tan(d)))))
        theta = x_ra(lam) - H0 + 360.0 * (t / 21600.0) * (1 + 1 / 365.2422)
        errs.append(abs(circ(vs._vs_lagna_from_elapsed(lam, t, local), x_asc(theta, lat))))
    errs.sort()
    check(errs[-1] < tol and errs[len(errs) // 2] < 0.8, "Lagna vs exact ascendant at lat %.2f: median %.2f, max %.2f deg" % (lat, errs[len(errs) // 2], errs[-1]))

# =====================================================================================================
# 5. EQUATION OF TIME, SUNRISE, SUNSET  (Ch.II vs.93-95 and commentary; Sec.7 vs.24)
# =====================================================================================================
c_ = const.VS_MEAN_SUNRISE_DAY_FRACTION
jd_year = [2460311.5 + k for k in range(0, 366, 4)]
eots = []
for jd0 in jd_year:
    for pl in (HE, BLR):
        lmt = jd0 + 0.25
        e = vs._equation_of_time_days(lmt, pl)
        eots.append(e)
        mean_sun = vs._mean_longitude_raw(lmt, pl, S)
        bh = vs._mandaphala(lmt, pl, S, mean_sun, None)
        check(e * bh <= 1e-15, "true Sun ahead of the mean Sun -> apparent noon later (EoT negative), and vice versa")
        check(abs(e + bh / (360.0 + vs._vs_daily_motion(S))) < 1e-15, "EoT = - bhujaphala / (360 + Sun's daily motion)")
check(max(abs(x) for x in eots) < 0.00618 and max(abs(x) for x in eots) > 0.0055, "bhujantara part only: |EoT| <= 8.9 minutes (%.2f)" % (max(abs(x) for x in eots) * 1440))
for pl, tol in ((BLR, 1.0), (UJN, 1.0), (HE, 1.5), (SYD, 1.5)):
    worst = 0.0
    for jd0 in jd_year:
        jd = jd0 + 0.5
        sr, ss = vs._sunrise_jd(jd, pl), vs._sunset_jd(jd, pl)
        lmt = math.floor(jd - 0.5) + 0.5 + c_
        sun = (vs._sidereal_longitude_lmt(lmt, pl, S) + vs._rising_ayanamsa(lmt, pl)) % 360
        H0 = math.acos(max(-1, min(1, -math.tan(math.radians(pl.latitude)) * math.tan(x_decl(sun)))))
        worst = max(worst, abs((ss - sr) - 2 * math.degrees(H0) / 360.0) * 1440)
        mid = math.floor(jd - 0.5) + 0.5
        check(sr < mid + 0.5 - vs.zone_longitude_correction_days(pl) < ss, "sunrise before local noon before sunset")
        eot = vs._equation_of_time_days(mid + c_, pl)
        cara = vs._general_cara_vinadis(sun, pl.latitude) / 3600.0
        check(abs(sr + vs.zone_longitude_correction_days(pl) - (mid + c_ - cara - eot)) < 1e-12, "sunrise = mean sunrise - cara - EoT")
        check(sr < ss, "sunrise before sunset")
    check(worst < tol, "day length vs exact geometric day length at %s: worst %.2f min" % (pl.name, worst))
# the cara has the right direction: longer days in the northern summer for a northern place, shorter for a southern place
def day_len(pl, jd): return (vs._sunset_jd(jd + 0.5, pl) - vs._sunrise_jd(jd + 0.5, pl)) * 24.0
jd_june, jd_dec = 2460462.5, 2460646.5     # about 10 June, 11 December 2024
check(day_len(HE, jd_june) > 14.9 and day_len(HE, jd_dec) < 9.2, "northern place: long June days, short December days (%.2f h, %.2f h)" % (day_len(HE, jd_june), day_len(HE, jd_dec)))
check(day_len(SYD, jd_june) < 10.0 and day_len(SYD, jd_dec) > 14.0, "southern place: reversed (%.2f h, %.2f h)" % (day_len(SYD, jd_june), day_len(SYD, jd_dec)))
# the one derived constant moves sunrise by the same amount (the book gives no clock hour for mean sunrise at Lanka)
sr0 = vs._sunrise_jd(jd_june + 0.5, BLR)
const.VS_MEAN_SUNRISE_DAY_FRACTION = c_ + 0.01
try: sr1 = vs._sunrise_jd(jd_june + 0.5, BLR)
finally: const.VS_MEAN_SUNRISE_DAY_FRACTION = c_
check(abs((sr1 - sr0) - 0.01) < 5e-4, "VS_MEAN_SUNRISE_DAY_FRACTION also moves sunrise (shift %.5f day)" % (sr1 - sr0))

# =====================================================================================================
# 6. THE LAGNA FUNCTION  _ascendant_longitude
# =====================================================================================================
def x_lagna_now(jd, pl):                                     # exact geometry for the same instant (oracle)
    lmt = jd + vs.zone_longitude_correction_days(pl)
    sun = (vs._sidereal_longitude_lmt(lmt, pl, S) + vs._rising_ayanamsa(jd, pl)) % 360
    apparent_hours = ((lmt - 0.5) % 1.0 + vs._equation_of_time_days(lmt, pl)) * 24.0
    return x_asc(x_ra(sun) + (apparent_hours - 12.0) * 15.0, pl.latitude)
NIGHT = const.VS_LAGNA_NIGHT_METHOD
saved = const.vs_lagna_night_method_default
try:
    for pl, step_max, err_max in ((BLR, 1.7, 2.6), (HE, 3.0, 3.2)):   # steps: normal motion + up to ~0.7 deg when the day counter resets at sunrise
        for jd0 in (2460462.5, 2460554.5, 2460646.5, 2460737.5):
            tracks = {}
            for meth in NIGHT:
                const.vs_lagna_night_method_default = meth
                vals = [vs._ascendant_longitude(jd0 + k / 288.0, pl) for k in range(0, 289)]
                tracks[meth] = vals
                check(all(0.0 <= x < 360.0 for x in vals), "Lagna in [0, 360)")
                steps = [circ(vals[k + 1], vals[k]) for k in range(288)]
                if meth == NIGHT.SINCE_SUNRISE:
                    check(min(steps) > 0.0, "SINCE_SUNRISE: the Lagna never moves backwards at 5-minute resolution (%s, jd %.1f)" % (pl.name, jd0))
                    check(max(steps) < step_max, "SINCE_SUNRISE: largest 5-min step %.2f deg (%s)" % (max(steps), pl.name))
                errs = [abs(circ(vs._ascendant_longitude(jd0 + k / 96.0, pl) + vs._rising_ayanamsa(jd0 + k / 96.0, pl), x_lagna_now(jd0 + k / 96.0, pl))) for k in range(97)]
                check(max(errs) < err_max, "%s Lagna vs exact geometry at %s, jd %.1f: max %.2f deg" % (meth.name, pl.name, jd0, max(errs)))
            sr, ss = vs._sunrise_jd(jd0 + 0.5, pl), vs._sunset_jd(jd0 + 0.5, pl)
            for k in range(289):
                jd = jd0 + k / 288.0
                if sr <= jd <= ss:
                    check(abs(circ(tracks[NIGHT.SINCE_SUNRISE][k], tracks[NIGHT.SINCE_SUNSET_OPPOSITE_SUN][k])) < 1e-9, "in daytime the night option changes nothing")
                else:
                    check(abs(circ(tracks[NIGHT.SINCE_SUNRISE][k], tracks[NIGHT.SINCE_SUNSET_OPPOSITE_SUN][k])) < 3.4, "at night the two readings agree within the book's own precision")
finally:
    const.vs_lagna_night_method_default = saved
# at sunrise the Lagna is the Sun; the Lagna a civil day later is about one degree further (the Sun's motion)
for pl in (BLR, HE, UJN, SYD):
    for jd0 in (2460311.5, 2460462.5, 2460646.5):
        sr = vs._sunrise_jd(jd0 + 0.5, pl)
        ayan = vs._rising_ayanamsa(sr, pl)
        sun = (vs._sidereal_longitude_impl(sr, pl, S) + ayan) % 360
        check(abs(circ(vs._ascendant_longitude(sr + 1e-9, pl) + ayan, sun)) < 0.01, "at sunrise the Lagna is the Sun (%s)" % pl.name)
        l0, l1 = vs._ascendant_longitude(sr + 0.3, pl), vs._ascendant_longitude(sr + 1.3, pl)
        check(0.0 < circ(l1, l0) % 360 < 3.5, "after one civil day the Lagna is about a degree further (%.2f)" % (circ(l1, l0) % 360))
# the public wrapper keeps the Surya Siddhantha return format [sign, degrees in sign, nakshatra, pada]
if hasattr(vs, 'ascendant'):
    try:
        a = vs.ascendant(2460462.3, HE)
        check(len(a) == 4 and 0 <= a[0] < 12 and 0.0 <= a[1] < 30.0, "ascendant() return format")
        check(abs((a[0] * 30 + a[1]) - vs._ascendant_longitude(2460462.3, HE)) < 1e-9, "ascendant() = _ascendant_longitude()")
    except (AttributeError, KeyError):
        pass          # needs utils.nakshatra_pada (present in the real package)
print("ALL %d CHECKS PASSED" % n_checks)
