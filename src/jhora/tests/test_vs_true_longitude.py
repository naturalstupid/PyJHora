"""
Tests for steps 3-5 (true longitudes, Ch.II) of vateshwara_sidhantha.py.
Run:  python test_vs_true_longitude.py      (needs const.py with the VS block)

How the module is checked:
  * the Rsine / Rversed-sine tables are transcribed a SECOND time here (from Table 13) and compared with the verse lists
    in const; they must also satisfy the book's own identities (R - Rvers(n) = Rsine(96-n), R^2, worked examples);
  * every interpolation rule the book states (vs.58-62 first-order, vs.65-80 second-order) is re-implemented here literally
    from the verse and compared with the module;
  * the corrections are re-implemented in a different style from the verses (vs.1, vs.2, vs.3-4, vs.93-94) and compared;
  * math.sin / math.atan2 appear ONLY as test oracles, to bound the size of the book's own table-interpolation error; the
    module itself never uses them for the model.
Every place is a vs.Place.
"""
import math, random
from fractions import Fraction as F
try:
    from jhora.panchanga import vateshwara_sidhantha as vs      # adjust to wherever you put the module
    from jhora import const
except ImportError:
    from jhora import vateshwara_sidhantha as vs
    from jhora import const

random.seed(23)
n_checks = 0
def check(cond, msg):
    global n_checks
    n_checks += 1
    assert cond, "FAILED: " + msg
def circ(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)
sd = lambda x: math.sin(math.radians(x))
cd = lambda x: math.cos(math.radians(x))
LIN, SEC = const.VS_RSINE_METHOD.LINEAR, const.VS_RSINE_METHOD.SECOND_ORDER
R = const.VS_RSINE_RADIUS
H = const.VS_RSINE_ELEMENTAL_ARC
T = const.VS_RSINE_TABLE
S, MO, MA, ME, JU, VE, SA = const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER, const._VENUS, const._SATURN
HE = vs.Place('Hoffman Estates', 42.06, -88.12, -5.0)
BLR = vs.Place('Bangalore', 12.97, 77.59, 5.5)
ON_PM = vs.Place('prime meridian', 23.18, const.VS_PRIME_MERIDIAN_LONGITUDE, 5.5)

# =====================================================================================================
# 1. TABLES (Sec.1 vs.2-51, Table 13)
# =====================================================================================================
TABLE13 = """56 15 0 27|112 29 1 50|168 41 4 8|224 50 7 21|280 56 11 30|336 57 16 33|392 53 22 31|448 43 29 24|504 25 37 12|559 59 45 55|615 25 55 32|670 40 66 3|725 45 77 29|780 38 89 48|835 18 103 1|889 45 117 8|943 58 132 8|997 55 148 1|1051 37 164 47|1105 1 182 26|1158 8 200 57|1210 56 220 20|1263 25 240 35|1315 34 261 41|1367 21 283 38|1418 47 306 25|1469 49 330 3|1520 28 354 31|1570 43 379 49|1620 32 405 55|1669 55 432 51|1718 52 460 34|1767 21 489 5|1815 22 518 24|1862 53 548 29|1909 54 579 21|1956 25 610 59|2002 24 643 23|2047 52 676 31|2092 46 710 23|2137 6 745 0|2180 53 780 19|2224 4 816 22|2266 39 853 6|2308 39 890 32|2350 1 928 39|2390 45 967 26|2430 51 1006 53|2470 18 1046 59|2509 5 1087 43|2547 12 1129 5|2584 38 1171 5|2621 22 1213 40|2657 25 1256 51|2692 44 1300 38|2727 21 1344 58|2761 13 1389 52|2794 21 1435 20|2826 45 1481 19|2858 23 1527 50|2889 15 1574 51|2919 20 1622 22|2948 39 1670 23|2977 10 1718 52|3004 53 1767 49|3031 49 1817 12|3057 55 1867 1|3083 13 1917 16|3107 41 1967 55|3131 19 2018 57|3154 6 2070 23|3176 3 2122 10|3197 9 2174 19|3217 24 2226 48|3236 47 2279 36|3255 18 2332 43|3272 57 2386 7|3289 43 2439 49|3305 36 2493 46|3320 36 2547 59|3334 43 2602 26|3347 56 2657 6|3360 15 2711 59|3371 41 2767 4|3382 12 2822 19|3391 49 2877 45|3400 32 2933 19|3408 20 2989 1|3415 13 3044 51|3421 11 3100 47|3426 14 3156 48|3430 23 3212 54|3433 36 3269 3|3435 54 3325 15|3437 17 3381 29|3437 44 3437 44"""
rows = [tuple(map(int, r.split())) for r in TABLE13.split("|")]
check(len(rows) == 96 and len(const.VS_RSINE_TABLE_DMS) == 96 and len(const.VS_RVERSED_TABLE_DMS) == 96, "96 entries each")
check([(a, b) for a, b, c, d in rows] == [tuple(x) for x in const.VS_RSINE_TABLE_DMS], "Rsine verse lists == Table 13 (all 96)")
check([(c, d) for a, b, c, d in rows] == [tuple(x) for x in const.VS_RVERSED_TABLE_DMS], "Rversed-sine verse lists == Table 13 (all 96)")
check(len(T) == 97 and T[0] == 0.0 and len(const.VS_RVERSED_TABLE) == 97, "tables carry the extra Rsin 0 entry")
check(R == 3437.0 + 44.0 / 60 and H == 56.25 and 96 * H == 5400.0, "radius 3437'44\", elemental arc 56'15\", 96 of them = 90 deg")
check(T[96] == R, "the 96th Rsine is the radius")
check(abs((21600 / 6.2832) ** 2 - (11818047 + 35 / 60)) < 0.01, "R^2 = 1,18,18,047'35\" with pi = 3.1416 (vs.49c-50)")
check(abs(21600 / 6.2832 - R) < 1.0 / 60, "R = 21600/(2 pi) = 3437'44\" correct to seconds")
check(all(T[i] < T[i + 1] for i in range(96)), "Rsines strictly increase")
D = [T[i + 1] - T[i] for i in range(96)]
check(all(D[i] >= D[i + 1] - 1.0 / 60 for i in range(95)), "Rsine differences decrease (concave) to within a second")
check(max(abs(T[n] - R * sd(n * 0.9375)) for n in range(97)) < 1.0 / 60, "every Rsine within 1\" of R sin (book rounds to seconds)")
check(max(abs(const.VS_RVERSED_TABLE[n] - R * (1 - cd(n * 0.9375))) for n in range(97)) < 1.0 / 60, "every Rversed-sine within 1\" of R(1-cos)")
for n in range(1, 96):
    check(abs((R - const.VS_RVERSED_TABLE[n]) - T[96 - n]) < 1e-9, "R - Rvers(%d) == Rsine(%d)  (vs.55 formula 3)" % (n, 96 - n))
check(abs(vs._vs_rsine(58 * 60) - (2915 + 19 / 60)) < 1.0 / 60, "worked example vs.58-60: Rsin(1s28deg) = 2915'19\"")
check(abs(vs._vs_rsine(24 * 60) - (1398 + 13 / 60)) < 1.0 / 60, "worked example vs.61, 49(c-d): Rsin 24deg = 1398'13\"")
check(abs(vs._vs_rsine(24 * 60) - (1367 + 21 / 60 + (51 + 26 / 60) * 9 / 15)) < 1e-9, "vs.61: 25th Rsine + 9/15 of 51'26\"")

# =====================================================================================================
# 2. FIRST-ORDER RULES  vs.58-62 (five rules, one arithmetic)
# =====================================================================================================
def rule_58(a):                                    # arc in minutes
    q, r = divmod(a, H); q = int(q)
    return T[q] + r * (T[q + 1] - T[q]) / H
def rule_59(a):                                    # arc in degrees -> signs x 32
    d = a / 60.0
    x = (d / 30.0) * 32.0
    S_, D_ = int(x), (x - int(x)) * 30.0
    return T[S_] + D_ * (T[S_ + 1] - T[S_]) / 30.0
def rule_60(d):                                    # integer degrees: d = 15 q + r ; serial d + q
    q, r = divmod(d, 15)
    return T[d + q] + r * (T[d + q + 1] - T[d + q]) / 15.0
def rule_61(d):                                    # integer degrees x 16 / 15
    q, r = divmod(d * 16, 15)
    return T[q] + r * (T[q + 1] - T[q]) / 15.0
def rule_62(a):                                    # minutes x 4 / 225
    q = int(a * 4 // 225); r = a * 4 - q * 225
    return T[q] + r * (T[q + 1] - T[q]) / 225.0
for _ in range(3000):
    a = random.uniform(0.0, 5399.999)
    got = vs._vs_rsine(a, LIN)
    check(abs(got - rule_58(a)) < 1e-9 and abs(got - rule_59(a)) < 1e-9, "vs.58 / vs.59 == module")
    check(abs(got - rule_62(a / 4.0 * 4.0)) < 1e-6, "vs.62 == module")
for d in range(0, 90):
    got = vs._vs_rsine(d * 60.0, LIN)
    check(abs(got - rule_60(d)) < 1e-9 and abs(got - rule_61(d)) < 1e-9, "vs.60 / vs.61 == module at %d deg" % d)
for n in range(0, 97):
    check(abs(vs._vs_rsine(n * H, LIN) - T[n]) < 1e-9 and abs(vs._vs_rsine(n * H, SEC) - T[n]) < 1e-9, "table value reproduced at node %d" % n)

# =====================================================================================================
# 3. SECOND-ORDER RULES vs.65-80: each form re-implemented from the verse, all must agree with the module
# =====================================================================================================
def Tf(i): return T[i] if i >= 0 else -T[-i]       # Rsin(-x) = -Rsin(x): gives D(-1) = Rsin h
def second_order_forms(a):
    n = int(a // H); lam = a - n * H
    Dm1 = Tf(n) - Tf(n - 1); Dn = Tf(n + 1) - Tf(n)
    V = abs(Dn - Dm1); sgn = -1.0 if Dn <= Dm1 else 1.0     # "- or + according as Dn <= Dn-1"
    u = lam / H
    out = {}
    out["vs66(2)"] = u * Dm1 + sgn * u * (u + 1) / 2 * V
    out["vs65(1)"] = u * (Dm1 + sgn * (V / 2 + u * V / 2))
    out["vs67"] = u * (Dm1 + sgn * (lam + H) * V / (2 * H))
    out["vs68"] = u * Dm1 + sgn * (lam * lam / H + lam) * (V / H) / 2
    out["vs78-79"] = (Dm1 + sgn * (u + 1) / 2 * V) * u
    out["vs80"] = (Dm1 + sgn * ((H + lam) / 2) * V / H) / (H / lam) if lam > 0 else 0.0
    out["Brahmagupta"] = u * ((Dn + Dm1) / 2 + sgn * u * V / 2)
    return Tf(n) + 0 * lam, out
for _ in range(4000):
    a = random.uniform(0.0, 5399.999)
    base, forms = second_order_forms(a)
    got = vs._vs_rsine(a, SEC)
    for name, delta in forms.items():
        check(abs(got - (base + delta)) < 1e-8, "second-order form %s == module (arc %.3f)" % (name, a))
for _ in range(3000):                               # continuity at each node from the left
    n = random.randint(1, 95)
    check(abs(vs._vs_rsine(n * H - 1e-9, SEC) - T[n]) < 1e-6, "second order continuous at node %d" % n)
# accuracy of the two readings against the true sine (test oracle only): the book's own table error
errL = max(abs(vs._vs_rsine(a, LIN) - R * sd(a / 60.0)) for a in (random.uniform(0, 5400) for _ in range(20000)))
errS = max(abs(vs._vs_rsine(a, SEC) - R * sd(a / 60.0)) for a in (random.uniform(0, 5400) for _ in range(20000)))
check(errL < 0.12 and errS < 0.015 and errS < errL / 5, "linear error %.4f' < 0.12', second-order %.5f' < 0.015'" % (errL, errS))

# =====================================================================================================
# 4. ARC FROM RSINE  vs.83-92
# =====================================================================================================
for meth in (LIN, SEC):
    check(vs._vs_arc_from_rsine(0.0, meth) == 0.0 and abs(vs._vs_arc_from_rsine(R, meth) - 5400.0) < 1e-9, "arc of 0 and of R")
    prev = -1.0
    for _ in range(3000):
        a = random.uniform(0.0, 5399.9)
        r = vs._vs_rsine(a, meth)
        check(abs(vs._vs_arc_from_rsine(r, meth) - a) < 1e-6, "arc(Rsine(a)) == a, method %s" % meth.name)
    for _ in range(3000):
        r = random.uniform(0.0, R)
        check(abs(vs._vs_rsine(vs._vs_arc_from_rsine(r, meth), meth) - r) < 1e-6, "Rsine(arc(r)) == r, method %s" % meth.name)
    xs = sorted(random.uniform(0.0, R) for _ in range(2000))
    arcs = [vs._vs_arc_from_rsine(x, meth) for x in xs]
    check(all(arcs[i] <= arcs[i + 1] + 1e-9 for i in range(1999)), "arc is non-decreasing in the Rsine, method %s" % meth.name)
for _ in range(2000):                               # vs.84: 225 x remainder / (4 x current difference) + 56'15" x serial number
    r = random.uniform(0.0, R - 1e-6)
    n = min(sum(1 for t in T[1:] if t <= r), 95)
    alt = 225.0 * (r - T[n]) / ((T[n + 1] - T[n]) * 4.0) + 56.25 * n
    check(abs(alt - vs._vs_arc_from_rsine(r, LIN)) < 1e-9, "vs.84 == vs.83 == module")
for bad in (-1.0, R + 1.0):
    try: vs._vs_arc_from_rsine(bad); check(False, "should refuse")
    except ValueError: check(True, "Rsine outside 0..R refused")
for bad in (-1.0, 5401.0):
    try: vs._vs_rsine(bad); check(False, "should refuse")
    except ValueError: check(True, "arc outside 0..90 deg refused")

# =====================================================================================================
# 5. ANOMALY, BHUJA, KOTI  (vs.54-57)
# =====================================================================================================
for _ in range(2000):
    t = random.uniform(0, 360)
    want = t if t <= 90 else 180 - t if t <= 180 else t - 180 if t <= 270 else 360 - t     # vs.55, literally
    check(abs(vs._vs_bhuja(t) - want) < 1e-12, "bhuja of the anomaly (vs.55)")
    check(abs(vs._vs_bhuja(t + 360) - want) < 1e-9 and abs(vs._vs_bhuja(-t) - vs._vs_bhuja(t)) < 1e-9, "bhuja periodic and even")
    bj, kj = vs._vs_bhujajya_kotijya(t)
    check(abs(bj - vs._vs_rsine(want * 60)) < 1e-12 and abs(kj - vs._vs_rsine((90 - want) * 60)) < 1e-12, "bhujajya, kotijya (formulas 1-2)")
    # vs.56 formulas 5-8: bhujajya^2 + kotijya^2 = R^2.  (Compared as squares: the square root itself amplifies the table's
    # own +/-0.1' interpolation error without limit as the bhuja approaches 90 deg.)
    check(abs(bj * bj + kj * kj - R * R) / (R * R) < 2.5e-4, "bhujajya^2 + kotijya^2 = R^2  (vs.56 formulas 5-8, to the table's accuracy)")
    check(abs((R - bj) * (R + bj) - kj * kj) / (R * R) < 2.5e-4, "kotijya^2 = (R-bhujajya)(R+bhujajya)  (vs.56 formula 7)")
for n in range(0, 97):                               # formula (3): kotijya = R - Rvers(bhuja), exact at the table nodes
    bj, kj = vs._vs_bhujajya_kotijya(n * 0.9375)
    check(abs(kj - (R - const.VS_RVERSED_TABLE[n])) < 1e-9, "kotijya = R - Rvers(bhuja) at node %d  (vs.55 formula 3)" % n)
check(vs._vs_koti_sign(0) == 1 and vs._vs_koti_sign(89.9) == 1 and vs._vs_koti_sign(90.1) == -1 and vs._vs_koti_sign(269.9) == -1
      and vs._vs_koti_sign(270.1) == 1 and vs._vs_koti_sign(359.9) == 1, "koti sign: + in the half-orbit beginning with Capricorn")

# =====================================================================================================
# 6. EPICYCLES (Table 14) and the book's own cross-check in the rationale of vs.100
# =====================================================================================================
check(const.VS_MANDA_EPICYCLES == {S: 14.0, MO: 31.5, MA: 72.0, ME: 22.0, JU: 33.0, VE: 11.0, SA: 46.0}, "Table 14 manda epicycles")
check(const.VS_SIGHRA_EPICYCLES == {MA: 233.0, ME: 138.0, JU: 65.0, VE: 260.0, SA: 32.0}, "Table 14 sighra epicycles")
# vs.100 rationale: Sun's motion-correction  = Rsine-diff x 59'8" x 14 / ((225/4) x 360)  ~ 7/172 ;  Moon's x (13d10'34" - 6'40") x 31.50 ~ 49/40
check(abs((59 + 8 / 60) * const.VS_MANDA_EPICYCLES[S] / (56.25 * 360) / (7 / 172) - 1) < 0.006, "vs.100: Sun's constant 7/172 follows from epicycle 14 (13.5 or 14.5 would not)")
check(abs((790 + 34 / 60 - (6 + 40 / 60)) * const.VS_MANDA_EPICYCLES[MO] / (56.25 * 360) / (49 / 40) - 1) < 0.006, "vs.100: Moon's constant 49/40 follows from epicycle 31.5 (31 or 32 would not)")

# =====================================================================================================
# 7. MANDA CORRECTION  (vs.93-94, vs.16)
# =====================================================================================================
for meth in (LIN, SEC):
    tol = 0.0006 if meth == LIN else 0.0003
    for _ in range(4000):
        t = random.uniform(0, 360)
        for p, e in const.VS_MANDA_EPICYCLES.items():
            got = vs._vs_manda_correction(t, e, meth)
            want = -math.degrees(math.asin(sd(t) * e / 360.0))               # oracle: sign by the Aries half
            check(abs(got - want) < tol, "manda correction vs exact oracle, method %s, e=%s" % (meth.name, e))
const.vs_rsine_method_default = LIN
check(abs(vs._vs_manda_correction(90.0, 14.0) + math.degrees(math.asin(14 / 360))) < 0.0006, "Sun's maximum equation: -2.23 deg at anomaly 90")
check(abs(vs._vs_manda_correction(270.0, 31.5) - math.degrees(math.asin(31.5 / 360))) < 0.0006, "Moon's maximum equation +5.02 deg at anomaly 270")
for t in (0.0, 180.0, 360.0):
    check(vs._vs_manda_correction(t, 14.0) == 0.0, "no correction at anomaly %s" % t)
for _ in range(2000):
    t = random.uniform(0.1, 179.9)
    a, b = vs._vs_manda_correction(t, 22.0), vs._vs_manda_correction(360 - t, 22.0)
    check(a < 0 < b and abs(a + b) < 1e-12, "subtract in the Aries half, add in the Libra half, antisymmetric")
# vs.16 (first method of the 'Mandaphala and Sighraphala corrections'): kendra = apogee - mean, ADD when it lies in the Aries half
for _ in range(1000):
    jd = random.uniform(2400000, 2500000)
    for p in (S, MO, MA, ME, JU, VE, SA):
        mean = random.uniform(0, 360)
        apo = vs._mean_apogee_longitude(jd, ON_PM, p)
        kendra = (apo - mean) % 360.0
        mag = abs(vs._vs_manda_correction(kendra, const.VS_MANDA_EPICYCLES[p]))
        want = mag if 0 < kendra < 180 else -mag
        check(abs(vs._mandaphala(jd, ON_PM, p, mean, None) - want) < 1e-9, "vs.16 sign rule == module (planet %s)" % p)
check(vs._mandaphala(2451545.0, ON_PM, const._RAHU, 10.0, None) == 0.0 and vs._mandaphala(2451545.0, ON_PM, const._KETU, 10.0, None) == 0.0, "no manda for the nodes")

# =====================================================================================================
# 8. SIGHRA CORRECTION  (Sec.2 vs.3-4, vs.5, vs.9)
# =====================================================================================================
for meth in (LIN, SEC):
    const.vs_rsine_method_default = meth
    tol = 0.004 if meth == LIN else 0.0006
    for p, e in const.VS_SIGHRA_EPICYCLES.items():
        rho = e / 360.0
        best = 0.0
        for i in range(0, 3600):
            m = i * 0.1
            got = vs._sighra_correction_classical(m, p)
            want = math.degrees(math.atan2(rho * sd(m), 1 + rho * cd(m)))   # oracle: angle subtended at the centre
            check(abs(got - want) < tol, "sighraphala vs exact oracle, %s, planet %s, m=%.1f" % (meth.name, p, m))
            best = max(best, abs(got))
        check(abs(best - math.degrees(math.asin(rho))) < 0.02, "largest sighraphala of planet %s = asin(e/360)" % p)
const.vs_rsine_method_default = LIN
for p in const.VS_SIGHRA_EPICYCLES:
    for _ in range(500):
        m = random.uniform(0.1, 179.9)
        a, b = vs._sighra_correction_classical(m, p), vs._sighra_correction_classical(360 - m, p)
        check(a > 0 > b and abs(a + b) < 1e-12, "positive in the Aries half, negative in the Libra half")
    check(vs._sighra_correction_classical(0.0, p) == 0.0 and vs._sighra_correction_classical(180.0, p) == 0.0, "zero at anomaly 0 and 180")
# the book's alternative forms of the karna (vs.3-4 / vs.5 / vs.9) agree: antyaphalajya = R e / 360
for _ in range(3000):
    m = random.uniform(0, 360); p = random.choice(list(const.VS_SIGHRA_EPICYCLES)); e = const.VS_SIGHRA_EPICYCLES[p]
    bj, kj = vs._vs_bhujajya_kotijya(m)
    bahu, koti_ph = bj * e / 360, kj * e / 360 * vs._vs_koti_sign(m)
    true_koti = R + koti_ph
    anty = R * e / 360
    k1 = math.sqrt(true_koti ** 2 + bahu ** 2)                                  # vs.3-4
    k2 = math.sqrt(true_koti ** 2 - koti_ph ** 2 + anty ** 2)                   # vs.5
    k3 = math.sqrt(R ** 2 + anty ** 2 + 2 * R * koti_ph)                        # vs.9 (sum for Capricorn half, difference for Cancer half)
    check(abs(k1 - k2) / k1 < 3e-4 and abs(k1 - k3) / k1 < 3e-4, "karna forms vs.3-4, vs.5, vs.9 agree to the table's accuracy")

# =====================================================================================================
# 9. BHUJANTARA  (vs.93-94: planet's daily motion x Sun's bhujaphala / (21600 + Sun's daily motion), minutes)
# =====================================================================================================
C_ = const.VS_YUGA.CIVIL_DAYS
dm_min = lambda rev: rev * 21600.0 / C_            # minutes of arc per civil day
for p in (S, MO, MA, ME, JU, VE, SA):
    rev = const.VS_REVOLUTIONS[S] if p in (ME, VE) else const.VS_REVOLUTIONS[p]
    for x_deg in (-2.2, -0.7, 0.0, 1.3, 2.2):
        want_min = dm_min(rev) * (x_deg * 60.0) / (21600.0 + dm_min(const.VS_REVOLUTIONS[S]))
        check(abs(vs._bhujantara_correction(p, x_deg) * 60.0 - want_min) < 1e-9, "bhujantara formula in minutes, planet %s" % p)
        check(vs._bhujantara_correction(p, x_deg) * x_deg >= 0, "same sign as the Sun's bhujaphala")
check(abs(vs._bhujantara_correction(MO, -2.23)) < 0.09, "Moon's bhujantara is under 0.09 deg")

# =====================================================================================================
# 10. THE TRUE LONGITUDES (Sec.1 vs.93-94, Sec.2 vs.1-2), re-implemented from the verses with exact trig
# =====================================================================================================
def oracle_sphuta(jd, place, p, bhuj=True):
    mean = lambda q: vs._mean_longitude_raw(jd, place, q)
    apo = lambda q: vs._mean_apogee_longitude(jd, place, q)
    mphala = lambda q, long_: -math.degrees(math.asin(sd((long_ - apo(q)) % 360) * const.VS_MANDA_EPICYCLES[q] / 360.0))
    sphala = lambda q, kendra: math.degrees(math.atan2(const.VS_SIGHRA_EPICYCLES[q] / 360 * sd(kendra), 1 + const.VS_SIGHRA_EPICYCLES[q] / 360 * cd(kendra)))
    ms = mean(S); sun_eq = mphala(S, ms)
    dmS = vs._vs_daily_motion(S)
    bt = lambda q, dm: dm * sun_eq / (360.0 + dmS) if bhuj else 0.0
    if p == S: return (ms + sun_eq + bt(S, dmS)) % 360
    if p == MO: return (mean(MO) + mphala(MO, mean(MO)) + bt(MO, vs._vs_daily_motion(MO))) % 360
    if p in (ME, VE):                                              # vs.2
        sig = mean(p); p1 = ms + sphala(p, (sig - ms) % 360); p2 = p1 + mphala(p, p1)
        return (p2 + bt(p, dmS)) % 360
    mp = mean(p)                                                   # vs.1
    q1 = mp + 0.5 * mphala(p, mp)
    q2 = q1 + 0.5 * sphala(p, (ms - q1) % 360)
    q3 = mp + mphala(p, q2)
    q4 = q3 + sphala(p, (ms - q3) % 360)
    return (q4 + bt(p, vs._vs_daily_motion(p))) % 360
for meth, tol in ((LIN, 0.015), (SEC, 0.003)):
    const.vs_rsine_method_default = meth
    worst = 0.0
    for _ in range(600):
        jd = random.uniform(2400000.0, 2500000.0)
        for pl in (BLR, HE, None):
            for p in (S, MO, MA, ME, JU, VE, SA):
                d = circ(vs._sidereal_longitude_lmt(jd, pl, p), oracle_sphuta(jd, pl, p)); worst = max(worst, d)
                check(d < tol, "pipeline == verse-by-verse oracle, %s, planet %s (dev %.5f)" % (meth.name, p, d))
    print("  worst pipeline deviation from the exact-trig oracle, %s: %.5f deg" % (meth.name, worst))
const.vs_rsine_method_default = LIN

# =====================================================================================================
# 11. PUBLIC API, SWITCHES, SANITY OF THE BOOK'S OWN PARAMETERS
# =====================================================================================================
for _ in range(300):                                                # public wrapper: UTC -> local civil -> local mean time
    jd_utc = random.uniform(2400000.0, 2500000.0)
    for pl in (HE, BLR):
        for p in (S, MO, MA, ME, JU, VE, SA, const._RAHU, const._KETU):
            jd_lmt = jd_utc + pl.timezone / 24.0 + vs.zone_longitude_correction_days(pl)
            check(abs(vs.sidereal_longitude(jd_utc, p, pl) - vs._sidereal_longitude_lmt(jd_lmt, pl, p)) < 1e-9, "sidereal_longitude() wrapper")
    check(0.0 <= vs.solar_longitude(jd_utc, HE) < 360.0 and abs(vs.solar_longitude(jd_utc, HE) - vs.sidereal_longitude(jd_utc, S, HE)) < 1e-12, "solar_longitude()")
    check(abs(vs.lunar_longitude(jd_utc, HE) - vs.sidereal_longitude(jd_utc, MO, HE)) < 1e-12, "lunar_longitude()")
    jd_l = jd_utc
    check(circ(vs._sidereal_longitude_lmt(jd_l, HE, const._KETU), vs._sidereal_longitude_lmt(jd_l, HE, const._RAHU) + 180) < 1e-9, "Ketu = Rahu + 180")
    check(circ(vs._sidereal_longitude_lmt(jd_l, HE, const._RAHU), vs._mean_longitude_raw(jd_l, HE, const._RAHU)) < 1e-12, "nodes are the mean nodes")
# model argument is accepted and ignored (signature parity with SS)
check(vs._sidereal_longitude_lmt(2451545.0, HE, S, const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA) == vs._sidereal_longitude_lmt(2451545.0, HE, S), "model argument")
# switches
jd = 2451545.7
for p in (S, MO, MA, ME, JU, VE, SA):
    on = vs._sidereal_longitude_lmt(jd, HE, p)
    saved = dict(const.VS_BHUJANTARA_APPLIES_TO)
    try:
        const.VS_BHUJANTARA_APPLIES_TO[p] = False
        off = vs._sidereal_longitude_lmt(jd, HE, p)
    finally:
        const.VS_BHUJANTARA_APPLIES_TO.clear(); const.VS_BHUJANTARA_APPLIES_TO.update(saved)
    ms = vs._mean_longitude_raw(jd, HE, S); sun_eq = vs._mandaphala(jd, HE, S, ms, None)
    check(circ(on - off if True else 0, vs._bhujantara_correction(p, sun_eq)) < 1e-9, "bhujantara switch changes the result by exactly the correction (planet %s)" % p)
const.vs_rsine_method_default = SEC
sec = [vs._sidereal_longitude_lmt(jd, HE, p) for p in (S, MO, MA, ME, JU, VE, SA)]
const.vs_rsine_method_default = LIN
lin = [vs._sidereal_longitude_lmt(jd, HE, p) for p in (S, MO, MA, ME, JU, VE, SA)]
check(max(circ(a, b) for a, b in zip(sec, lin)) < 0.01, "the two interpolation readings agree to 0.01 deg")
for bad in (const._URANUS, const._NEPTUNE, const._PLUTO):
    try: vs._sidereal_longitude_lmt(jd, HE, bad); check(False, "should refuse")
    except ValueError: check(True, "planet the book does not cover is refused")
# the Lagna (step 6) is implemented and is tested in test_vs_lagna.py; here only that it works
lg = vs._ascendant_longitude(jd, HE)
check(isinstance(lg, float) and 0.0 <= lg < 360.0, "Lagna available (step 6 done)")

# behaviour implied by the book's own epicycles (no modern numbers)
mx = {ME: 0.0, VE: 0.0}
retro = {p: 0 for p in (S, MO, MA, ME, JU, VE, SA)}
lo = {S: 9, MO: 99}; hi = {S: -9, MO: -9}
jd0 = 2451545.0
prev = {p: vs._sidereal_longitude_lmt(jd0, BLR, p) for p in retro}
for d in range(1, 3000):
    ms = vs._mean_longitude_raw(jd0 + d, BLR, S)
    for p in retro:
        cur = vs._sidereal_longitude_lmt(jd0 + d, BLR, p)
        step = (cur - prev[p] + 180) % 360 - 180
        if step < 0: retro[p] += 1
        if p in lo: lo[p] = min(lo[p], step); hi[p] = max(hi[p], step)
        if p in mx: mx[p] = max(mx[p], abs((cur - ms + 180) % 360 - 180))
        prev[p] = cur
e = lambda x: math.degrees(math.asin(x))
check(abs(mx[ME] - (e(138 / 360) + e(22 / 360))) < 0.6 and abs(mx[VE] - (e(260 / 360) + e(11 / 360))) < 1.0,
      "Mercury / Venus reach the elongation implied by their sighra + manda epicycles (%.2f, %.2f)" % (mx[ME], mx[VE]))
check(retro[S] == 0 and retro[MO] == 0, "Sun and Moon never retrograde")
check(all(retro[p] > 0 for p in (MA, ME, JU, VE, SA)), "Mars, Mercury, Jupiter, Venus, Saturn all have retrograde motion (vs.11: later < earlier)")
check(0.94 < lo[S] and hi[S] < 1.03, "Sun's daily motion %.3f..%.3f" % (lo[S], hi[S]))
check(11.9 < lo[MO] and hi[MO] < 14.4, "Moon's daily motion %.3f..%.3f" % (lo[MO], hi[MO]))
print("ALL %d CHECKS PASSED" % n_checks)
