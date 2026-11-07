#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
test_vs_eclipse.py -- tests of jhora/panchanga/eclipse_vs.py (Vateswara Siddhanta eclipses).

The VS engine is its own ephemeris: the Sun, Moon and node longitudes come from vateshwara_sidhantha.py. Modern trigonometry is used ONLY
inside the Oracle class below, as the yardstick for the parallax chain; eclipse_vs.py itself reads the Rsine table.

  PART A  the book's numbers (constants, mean diameters, Rsine, Moon's latitude)
  PART B  new moon / full moon finder
  PART C  lunar eclipse: contacts against an exact, unlinearised solution; possibility test; counts; ordering
  PART D  solar eclipse: lambana / apparent conjunction and nati against an exact topocentric calculation; contacts; existence
  PART E  next_lunar_eclipse / next_solar_eclipse: shapes, filters, LOCAL / GLOBAL (all times always returned), backward == forward, no exceptions

Run:  python test_vs_eclipse.py            (about 3 minutes)
"""
import math
import statistics
import sys
import time
from jhora import const, utils
from jhora.panchanga import vateshwara_sidhantha as vs
from jhora.panchanga import eclipse_vs as ev

d2r, r2d = math.radians, math.degrees
EPS = 24.0
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print("  FAIL:", name, detail)


def info(text):
    print("   ", text)


PLACES = [vs.Place('Chennai', 13.04, 80.26, 5.5), vs.Place('Hoffman Estates', 42.06, -88.14, -5.0), vs.Place('London', 51.5, -0.13, 0.0),
          vs.Place('Sydney', -33.87, 151.21, 10.0), vs.Place('Tokyo', 35.7, 139.7, 9.0), vs.Place('Quito', -0.2, -78.5, -5.0),
          vs.Place('Cape Town', -33.9, 18.4, 2.0), vs.Place('Mumbai', 19.1, 72.9, 5.5)]
BASE = utils.julian_day_number(vs.Date(2000, 1, 1), (0, 0, 0))


# ------------------------------------------------------------------ the exact yardstick (modern trigonometry)
def ecl_to_eq(lam, bet):
    x = math.cos(d2r(bet)) * math.cos(d2r(lam))
    y = math.cos(d2r(bet)) * math.sin(d2r(lam))
    z = math.sin(d2r(bet))
    c, s = math.cos(d2r(EPS)), math.sin(d2r(EPS))
    return x, y * c - z * s, y * s + z * c


def eq_to_ecl(v):
    x, y, z = v
    c, s = math.cos(d2r(EPS)), math.sin(d2r(EPS))
    yy, zz = y * c + z * s, -y * s + z * c
    return r2d(math.atan2(yy, x)) % 360.0, r2d(math.asin(zz / math.sqrt(x * x + yy * yy + zz * zz)))


def exact_rising_point(lst, phi):
    return r2d(math.atan2(math.cos(d2r(lst)), -(math.sin(d2r(EPS)) * math.tan(d2r(phi)) + math.cos(d2r(EPS)) * math.sin(d2r(lst))))) % 360.0


class Oracle:
    """ Exact topocentric positions of the Sun and Moon (spherical Earth, obliquity 24 deg) from the VS longitudes. """

    def __init__(self, se, mean_distances=False):
        self.se, self.place, self.fr = se, se.place, se.frame
        e = ev._EARTH_SEMI_DIAMETER
        self.d_moon = (const.VS_MOON_MEAN_DISTANCE_YOJANAS if mean_distances else self.fr.moon_distance) / e
        self.d_sun = (const.VS_SUN_MEAN_DISTANCE_YOJANAS if mean_distances else self.fr.sun_distance) / e

    def lst(self, t):
        ayan = vs._rising_ayanamsa(t, self.place)
        ls = (vs._sidereal_longitude_impl(t, self.place, const._SUN) + ayan) % 360
        ra = r2d(math.atan2(math.cos(d2r(EPS)) * math.sin(d2r(ls)), math.cos(d2r(ls)))) % 360
        return (ra + (t - self.se.noon_jd) * 360.0) % 360.0

    def topo(self, t):
        p = self.place
        ayan = vs._rising_ayanamsa(t, p)
        s, m, n = ev._longitudes(t, p)
        ls, lm = (s + ayan) % 360, (m + ayan) % 360
        bm = ev._moon_latitude_minutes(m, n) / 60.0
        lst, phi = self.lst(t), d2r(p.latitude)
        obs = (math.cos(phi) * math.cos(d2r(lst)), math.cos(phi) * math.sin(d2r(lst)), math.sin(phi))
        out = []
        for lam, bet, dist in ((ls, 0.0, self.d_sun), (lm, bm, self.d_moon)):
            u = ecl_to_eq(lam, bet)
            out.append(eq_to_ecl(tuple(dist * u[i] - obs[i] for i in range(3))))
        return out

    def _bisect(self, f, lo, hi):
        flo = f(lo)
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            fm = f(mid)
            if (fm < 0) == (flo < 0):
                lo, flo = mid, fm
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def apparent_conjunction(self, t0):
        t = self._bisect(lambda x: ev._wrap180(self.topo(x)[1][0] - self.topo(x)[0][0]), t0 - 0.2, t0 + 0.2)
        (ls, bs), (lm, bm) = self.topo(t)
        return t, (bm - bs) * 60.0

    def separation(self, t):
        (ls, bs), (lm, bm) = self.topo(t)
        return math.hypot(ev._wrap180(lm - ls) * math.cos(d2r(0.5 * (bs + bm))), bm - bs) * 60.0

    def closest_approach(self, t0):
        lo, hi = t0 - 0.1, t0 + 0.1
        for _ in range(60):
            a, b = lo + (hi - lo) / 3, hi - (hi - lo) / 3
            if self.separation(a) < self.separation(b):
                hi = b
            else:
                lo = a
        t = 0.5 * (lo + hi)
        return t, self.separation(t)

    def contact(self, t_mid, radius, direction):
        return self._bisect(lambda x: self.separation(x) - radius, t_mid, t_mid + direction * 0.2)


def with_exact_rising_point(oracle, fn):
    """ Runs fn with the module's Lagna replaced by the exact rising point of the oracle's sidereal time. """
    original = ev._rising_point_sayana
    ev._rising_point_sayana = lambda jd, place: exact_rising_point(oracle.lst(jd), place.latitude)
    try:
        return fn()
    finally:
        ev._rising_point_sayana = original


def mn_med_max(values):
    a = sorted(abs(v) for v in values)
    return a[len(a) // 2], a[-1]


# ================================================================== PART A
def part_a():
    print("PART A: the book's numbers")
    R = const.VS_RSINE_RADIUS
    check("A1 Sun's mean diameter is 33'", abs(const.VS_SUN_DIAMETER_YOJANAS * R / const.VS_SUN_MEAN_DISTANCE_YOJANAS - 33.0) < 0.01)
    check("A2 Moon's mean diameter is 33'", abs(const.VS_MOON_DIAMETER_YOJANAS * R / const.VS_MOON_MEAN_DISTANCE_YOJANAS - 33.0) < 0.01)
    moon_term = const.VS_EARTH_DIAMETER_YOJANAS * R / const.VS_MOON_MEAN_DISTANCE_YOJANAS
    sun_term = (const.VS_SUN_DIAMETER_YOJANAS - const.VS_EARTH_DIAMETER_YOJANAS) * R / const.VS_SUN_MEAN_DISTANCE_YOJANAS
    check("A3 105'24\" = Earth's diameter x R / Moon's distance (vs.16)", abs(moon_term - (105 + 24 / 60)) < 0.02, moon_term)
    check("A4 25'7\" = (Sun - Earth) x R / Sun's distance (vs.16)", abs(sun_term - (25 + 7 / 60)) < 0.03, sun_term)
    earth, sun_d, moon_d = const.VS_EARTH_DIAMETER_YOJANAS, const.VS_SUN_MEAN_DISTANCE_YOJANAS, const.VS_MOON_MEAN_DISTANCE_YOJANAS
    length = sun_d * earth / (const.VS_SUN_DIAMETER_YOJANAS - earth)
    shadow = earth * (length - moon_d) / length * R / moon_d
    check("A5 shadow by vs.8-10 equals 105'24\" - 25'7\" (vs.12, 16)", abs(shadow - (moon_term - sun_term)) < 0.05, shadow)
    check("A6 Rsine quadrants", abs(ev._rsin(90.0) - R) < 1e-6 and abs(ev._rsin(210.0) + ev._rsin(30.0)) < 1e-9 and abs(ev._rsin(-30.0) + ev._rsin(30.0)) < 1e-9)
    check("A7 Moon's greatest latitude is 270'", abs(ev._moon_latitude_minutes(90.0, 0.0) - 270.0) < 1e-6 and abs(ev._moon_latitude_minutes(270.0, 0.0) + 270.0) < 1e-6)
    check("A8 latitude is north in the Aries half and zero at the node", ev._moon_latitude_minutes(100.0, 10.0) > 0 > ev._moon_latitude_minutes(10.0, 100.0)
          and abs(ev._moon_latitude_minutes(50.0, 50.0)) < 1e-9)


# ================================================================== PART B
def part_b():
    print("PART B: new moon / full moon finder")
    p = PLACES[0]
    for target, label in ((0.0, "new moon"), (180.0, "full moon")):
        t, worst, last, gaps = BASE, 0.0, None, []
        for _ in range(60):
            t = ev._syzygy_jd(t, p, target, 1)
            worst = max(worst, abs(ev._wrap180(ev._phase(t, p) - target)))
            if last is not None:
                gaps.append(t - last)
            check("B %s strictly after the start" % label, last is None or t > last)
            last = t
            t += 1.0
        check("B1 %s phase error below 1e-7 degrees" % label, worst < 1e-7, worst)
        check("B2 %s spacing between 29.2 and 29.9 days" % label, 29.2 < min(gaps) and max(gaps) < 29.9, (min(gaps), max(gaps)))
        back = ev._syzygy_jd(last + 5.0, p, target, -1)
        check("B3 %s backward search finds the same instant" % label, abs(back - last) < 1e-7, back - last)
    jd = ev._syzygy_jd(BASE, p, 0.0, 1)
    check("B4 a syzygy exactly at the start is skipped", ev._syzygy_jd(jd, p, 0.0, 1) > jd + 20)


# ================================================================== PART C
def lunar_separation(t, place):
    s, m, n = ev._longitudes(t, place)
    return math.hypot(ev._wrap180(m - (s + 180.0)) * 60.0, ev._moon_latitude_minutes(m, n))


def solve_lunar_contact(place, t_mid, radius, direction):
    f = lambda t: lunar_separation(t, place) - radius
    lo, hi = t_mid, t_mid + direction * 0.4
    flo = f(lo)
    if flo > 0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def part_c():
    print("PART C: lunar eclipse")
    p = PLACES[0]
    jd, found, errors, types, order_ok, total_ok = BASE, 0, [], {'total': 0, 'partial': 0}, True, True
    disagree = 0
    for _ in range(260):
        jd_opp = ev._syzygy_jd(jd, p, 180.0, 1)
        jd = jd_opp + 1
        res = ev.is_lunar_eclipse(jd_opp, p)
        fr = ev._frame(jd_opp, p)
        outer, inner = 0.5 * (fr.shadow_diameter + fr.moon_diameter), 0.5 * (fr.shadow_diameter - fr.moon_diameter)
        closest = min(lunar_separation(jd_opp + h / 24.0, p) for h in range(-6, 7))
        disagree += (closest < outer) != res['is_possible']
        if not res['is_possible']:
            continue
        found += 1
        types[res['type']] += 1
        errors += [abs(res['jd_begin'] - solve_lunar_contact(p, jd_opp, outer, -1)) * 86400, abs(res['jd_end'] - solve_lunar_contact(p, jd_opp, outer, +1)) * 86400]
        if res['is_total']:
            total_ok &= res['jd_immersion'] is not None and res['grasa'] * 60.0 >= res['moon_diameter'] * 60.0 - 1e-9
            errors += [abs(res['jd_immersion'] - solve_lunar_contact(p, jd_opp, inner, -1)) * 86400, abs(res['jd_emersion'] - solve_lunar_contact(p, jd_opp, inner, +1)) * 86400]
        else:
            total_ok &= res['jd_immersion'] is None and res['jd_emersion'] is None
        seq = [t for t in (res['jd_begin'], res['jd_immersion'], res['jd_middle'], res['jd_emersion'], res['jd_end']) if t is not None]
        order_ok &= seq == sorted(seq)
    med, mx = mn_med_max(errors)
    info("%d lunar eclipses in 260 lunations %s; contact time vs exact solution: median %.1f s, max %.1f s" % (found, types, med, mx))
    check("C1 contacts agree with the exact unlinearised solution to 20 s", mx < 20.0, mx)
    check("C2 possibility agrees with the exact minimum separation in every lunation", disagree == 0, disagree)
    check("C3 contacts are in order", order_ok)
    check("C4 totality contacts exist exactly for total eclipses", total_ok)
    check("C5 about 1.5 umbral lunar eclipses a year (260 lunations = 21 years)", 28 <= found <= 44, found)
    check("C6 both types occur", types['total'] > 5 and types['partial'] > 5, types)
    r = ev.is_lunar_eclipse(ev._syzygy_jd(BASE, p, 180.0, 1) + 0.03, p)
    check("C7 a full moon given with an error of 0.03 day is refined to the opposition", abs(ev._wrap180(ev._phase(r['jd_opposition'], p) - 180.0)) < 1e-8)


# ================================================================== PART D
def solar_cases(places, lunations, max_latitude):
    for k in range(lunations):
        for p in places:
            jd = ev._syzygy_jd(BASE + k * 29.53, p, 0.0, 1)
            s, m, n = ev._longitudes(jd, p)
            if abs(ev._moon_latitude_minutes(m, n)) > max_latitude:
                continue
            se = ev._SolarEclipse(jd, p)
            if se.geometry(jd).above_horizon:
                yield jd, p, se


def part_d():
    print("PART D: solar eclipse")
    places = PLACES[:6]
    t_exact, t_lagna, lat_exact, lat_lagna, lat_book_mean, lat_nolat_mean, sign_bad, n = [], [], [], [], [], [], 0, 0
    for jd, p, se in solar_cases(places, 110, 90.0):
        o, o_mean = Oracle(se), Oracle(se, mean_distances=True)
        ta, ba = o.apparent_conjunction(jd)
        t_e = with_exact_rising_point(o, lambda: se.apparent_time(jd))
        t_exact.append((t_e - ta) * 1440.0)
        t_l = se.apparent_time(jd)
        t_lagna.append((t_l - ta) * 1440.0)
        lat_exact.append(with_exact_rising_point(o, lambda: se.true_latitude(t_e)) - ba)
        lat_lagna.append(se.true_latitude(t_l) - ba)
        s, m, nd = ev._longitudes(ta, p)
        beta = ev._moon_latitude_minutes(m, nd)
        (ls, bs), (lm, bm) = o_mean.topo(ta)
        reference = (bm - bs) * 60.0 - beta                      # relative nati with the mean distances the book's nati assumes
        (ls2, bs2), (lm2, bm2) = o.topo(ta)
        physical = (bm2 - bs2) * 60.0 - beta
        for flag, store in ((True, lat_book_mean), (False, lat_nolat_mean)):
            const.vs_nati_include_moon_latitude = flag
            store.append(with_exact_rising_point(o, lambda: se.relative_nati(se.geometry(ta))) - reference)
        const.vs_nati_include_moon_latitude = True
        engine = with_exact_rising_point(o, lambda: se.relative_nati(se.geometry(ta)))
        if abs(physical) > 8.0 and engine * physical < 0:
            sign_bad += 1
        n += 1
    const.vs_nati_include_moon_latitude = True
    info("%d eclipse-capable conjunctions with the Sun up at six places" % n)
    med, mx = mn_med_max(t_exact)
    info("apparent conjunction vs exact topocentric, exact rising point: median %.3f min, max %.3f min" % (med, mx))
    check("D1 lambana / apparent conjunction agrees with the exact calculation to 0.7 min", mx < 0.7, mx)
    med, mx = mn_med_max(t_lagna)
    info("apparent conjunction, module's own Lagna: median %.3f min, max %.3f min" % (med, mx))
    check("D2 with the module's own Lagna the apparent conjunction is within 4 min", mx < 4.0, mx)
    med, mx = mn_med_max(lat_nolat_mean)
    info("relative nati without the central-point latitude term vs the mean-distance exact result: median %.2f', max %.2f'" % (med, mx))
    check("D3 nati follows the book's mean-parallax model to 2.5' when the central-point latitude term is off", mx < 2.5, mx)
    med, mx = mn_med_max(lat_book_mean)
    info("relative nati as the book states it (latitude at the central ecliptic point): median %.2f', max %.2f'" % (med, mx))
    check("D4 nati as stated in Sec.2 vs.2 stays within 6' of the mean-distance exact result", mx < 6.0, mx)
    med, mx = mn_med_max(lat_exact)
    info("true latitude vs exact topocentric (true distances), exact rising point: median %.2f', max %.2f'" % (med, mx))
    check("D5 true latitude within 8' of the exact topocentric value (book's mean parallax and Sec.2 vs.2)", mx < 8.0, mx)
    check("D6 the direction (north / south) of a large nati is right in every case", sign_bad == 0, sign_bad)

    # contacts and existence against the exact geometry
    both = engine_only = missed = 0
    deep, borderline_ok = [], True
    for jd, p, se in solar_cases(PLACES, 130, 150.0):
        o = Oracle(se)
        fr = se.frame
        outer = 0.5 * fr.sun_diameter + 0.5 * fr.moon_diameter - fr.moon_speed * 60.0 / const.VS_SOLAR_MOON_SEMIDIAMETER_DIVISOR
        tm, mn = with_exact_rising_point(o, lambda: o.closest_approach(o.apparent_conjunction(jd)[0]))
        res = ev.is_solar_eclipse(jd, p)
        e, x = res['is_possible'], mn < outer
        both += e and x
        engine_only += e and not x
        missed += x and not e
        if e != x:
            borderline_ok &= abs(mn - outer) < 6.0
        if e and x and res['visible_begin'] and res['visible_middle'] and res['visible_end'] and outer - mn > 15.0:
            tb = with_exact_rising_point(o, lambda: o.contact(tm, outer, -1))
            te = with_exact_rising_point(o, lambda: o.contact(tm, outer, +1))
            deep += [(res['jd_begin'] - tb) * 1440.0, (res['jd_end'] - te) * 1440.0]
    info("existence: both agree %d, module only %d, exact only %d" % (both, engine_only, missed))
    check("D7 existence of an eclipse agrees with the exact geometry (disagreements are all within 6' of the limit, the nati error of D4)",
          borderline_ok and both > 30 and (engine_only + missed) <= 0.15 * (both + engine_only + missed))
    med, mx = mn_med_max(deep)
    info("first / last contact vs exact, eclipses overlapping by more than 15': median %.2f min, max %.2f min (N=%d)" % (med, mx, len(deep)))
    check("D8 first / last contact of a deep eclipse within 25 min of the exact value (median 3 min)", mx < 25.0 and med < 3.0, (med, mx))

    # internal consistency of one eclipse
    for jd, p, se in solar_cases(PLACES, 130, 40.0):
        res = ev.is_solar_eclipse(jd, p)
        if res['is_possible'] and res['visible_middle']:
            seq = [t for t in (res['jd_begin'], res['jd_immersion'], res['jd_apparent_conjunction'], res['jd_emersion'], res['jd_end']) if t is not None]
            check("D9 solar contacts are in order", seq == sorted(seq), seq)
            check("D10 type matches the magnitude rule",
                  (res['type'] == 'total') == (res['is_total']) and (res['type'] in ('total', 'annular')) == (res['jd_immersion'] is not None))
            break
    # method switches
    jd, p, se = next(solar_cases(PLACES[:2], 40, 90.0))
    saved = (const.vs_lambana_method_default, const.vs_eclipse_diameter_method_default)
    base_t = se.apparent_time(jd)
    for method in (const.VS_LAMBANA_METHOD.FOUR_GHATIS, const.VS_LAMBANA_METHOD.SAKRT):
        const.vs_lambana_method_default = method
        t = ev._SolarEclipse(jd, p).apparent_time(jd)
        check("D11 lambana method %s within 15 min of method 1" % method.name, abs(t - base_t) * 1440.0 < 15.0, (t - base_t) * 1440.0)
    const.vs_lambana_method_default = saved[0]
    fr1 = ev._frame(jd, p)
    const.vs_eclipse_diameter_method_default = const.VS_ECLIPSE_DIAMETER_METHOD.DAILY_MOTION
    fr2 = ev._frame(jd, p)
    const.vs_eclipse_diameter_method_default = saved[1]
    check("D12 the two diameter methods agree to 2' for the Sun and the Moon", all(abs(a - b) < 2.0 for a, b in zip(fr1[6:8], fr2[6:8])), (fr1[6:8], fr2[6:8]))
    info("Shadow at this date: %.2f' by the distances (vs.8-11), %.2f' by the daily motions (vs.15 as printed, 41/113); see test_book_eclipse_vs.py" % (fr1[8], fr2[8]))


# ================================================================== PART E
def gregorian_to_jd(t):
    return utils.julian_day_number(vs.Date(t[0], t[1], t[2]), (t[3], 0, 0))


def solar_visible_flags(result, place):
    """ Whether the Sun is above the horizon at begin, middle and end of a result of next_solar_eclipse(). """
    res = ev.is_solar_eclipse(gregorian_to_jd(result[1][1]), place)
    return [res['visible_begin'], res['visible_middle'], res['visible_end']]


def lunar_moon_up_flags(result, place):
    """ Whether the Moon is above the horizon at each time of a result of next_lunar_eclipse(). """
    out = []
    for t in result[1]:
        tj = gregorian_to_jd(t)
        out.append(ev._above_horizon_nirayana(tj, place, ev._longitudes(tj, place)[1]))
    return out


def part_e():
    print("PART E: next_lunar_eclipse / next_solar_eclipse")
    p = PLACES[0]
    jd0 = utils.julian_day_number(vs.Date(2010, 6, 1), (12, 0, 0))
    for name, fn, middle in (("lunar", ev.next_lunar_eclipse, True), ("solar", ev.next_solar_eclipse, False)):
        chain, jd = [], jd0
        for _ in range(8):
            r = fn(jd, p, ev.EclipseLocation.GLOBAL)
            times = [t for t in r[1] if t is not None]
            chain.append(gregorian_to_jd(times[len(times) // 2]))
            jd = chain[-1] + 2.0
        back, jd = [], chain[-1] + 2.0
        for _ in range(8):
            r = fn(jd, p, ev.EclipseLocation.GLOBAL, search_backward=True)
            times = [t for t in r[1] if t is not None]
            back.append(gregorian_to_jd(times[len(times) // 2]))
            jd = back[-1] - 2.0
        check("E1 %s: eight forward eclipses equal eight backward eclipses" % name, all(abs(a - b) < 2e-3 for a, b in zip(back[::-1], chain)))
        gaps = [chain[i + 1] - chain[i] for i in range(7)]
        check("E2 %s: eclipses are 5.7 to 25 months apart (six-monthly seasons)" % name, all(170 < g < 780 for g in gaps), gaps)
    r = ev.next_lunar_eclipse(jd0, p)
    check("E3 lunar shapes: 3 times for a partial, 5 for a total", r is not None and ((r[0] == 'partial' and len(r[1]) == 3) or (r[0] == 'total' and len(r[1]) == 5)))
    seen = set()
    jd = jd0
    for _ in range(14):
        r = ev.next_lunar_eclipse(jd, p)
        seen.add((r[0], len(r[1])))
        jd = gregorian_to_jd(r[1][0]) + 5
    check("E4 both lunar shapes occur and match their type", seen == {('partial', 3), ('total', 5)}, seen)
    for kind, want in ((ev.LunarEclipseType.TOTAL, 'total'), (ev.LunarEclipseType.PARTIAL, 'partial')):
        r = ev.next_lunar_eclipse(jd0, p, lunar_eclipse_type=kind)
        check("E5 lunar filter %s" % want, r is not None and r[0] == want)
    check("E6 PENUMBRAL and HYBRID are not in the book: None",
          ev.next_lunar_eclipse(jd0, p, lunar_eclipse_type=ev.LunarEclipseType.PENUMBRAL) is None
          and ev.next_solar_eclipse(jd0, p, solar_eclipse_type=ev.SolarEclipseType.HYBRID) is None)
    r_any = ev.next_solar_eclipse(jd0, p, ev.EclipseLocation.GLOBAL)
    check("E7 solar shape: type and three times", r_any is not None and r_any[0] in ('total', 'annular', 'partial') and len(r_any[1]) == 3)
    for kind, want in ((ev.SolarEclipseType.PARTIAL, 'partial'), (ev.SolarEclipseType.TOTAL, 'total'), (ev.SolarEclipseType.ANNULAR, 'annular')):
        r = ev.next_solar_eclipse(jd0, p, ev.EclipseLocation.GLOBAL, kind, max_tries=400)
        check("E8 solar filter %s (found %s)" % (want, None if r is None else r[0]), r is None or r[0] == want)
    # LOCAL skips an eclipse that is not seen; every time of the eclipse found is returned (no None), GLOBAL as well
    sun_down = 0
    jd = utils.julian_day_number(vs.Date(2000, 1, 1), (0, 0, 0))
    for _ in range(25):
        r = ev.next_solar_eclipse(jd, p, ev.EclipseLocation.LOCAL)
        g = ev.next_solar_eclipse(jd, p, ev.EclipseLocation.GLOBAL)
        flags = solar_visible_flags(r, p)
        check("E9 LOCAL solar: all three times are returned and the Sun is up at one of them", r is not None and all(t is not None for t in r[1]) and any(flags), flags)
        check("E10 GLOBAL solar: all three times are returned", g is not None and all(t is not None for t in g[1]))
        sun_down += sum(not f for f in flags)
        jd = gregorian_to_jd(r[1][1]) + 3
    info("contacts with the Sun below the horizon in 25 local solar searches: %d (all of them returned)" % sun_down)
    moon_down, ok_all, ok_up = 0, True, True
    jd = jd0
    for _ in range(10):
        r = ev.next_lunar_eclipse(jd, p, ev.EclipseLocation.LOCAL)
        flags = lunar_moon_up_flags(r, p)
        ok_all &= all(t is not None for t in r[1])
        ok_up &= any(flags)
        moon_down += sum(not f for f in flags)
        jd = gregorian_to_jd(r[1][0]) + 5
    info("contacts with the Moon below the horizon in 10 local lunar searches: %d (all of them returned)" % moon_down)
    check("E11 LOCAL lunar: every time of the eclipse is returned", ok_all)
    check("E12 LOCAL lunar: the Moon is above the horizon at one of the times of every eclipse found", ok_up)
    # the same eclipse is returned by LOCAL and by GLOBAL, with identical times
    rl = ev.next_lunar_eclipse(jd0, p, ev.EclipseLocation.LOCAL)
    rg = ev.next_lunar_eclipse(gregorian_to_jd(rl[1][0]) - 3.0, p, ev.EclipseLocation.GLOBAL)
    check("E13 lunar: LOCAL and GLOBAL give identical times for the same eclipse", rl == rg, (rl, rg))
    sl = ev.next_solar_eclipse(jd0, p, ev.EclipseLocation.LOCAL)
    sg = ev.next_solar_eclipse(gregorian_to_jd(sl[1][0]) - 3.0, p, ev.EclipseLocation.GLOBAL)
    check("E14 solar: LOCAL and GLOBAL give identical times for the same eclipse", sl == sg, (sl, sg))
    # no exceptions over places, latitudes and dates
    t0, errors, count = time.time(), 0, 0
    far = [vs.Place('Reykjavik', 64.1, -21.9, 0.0), vs.Place('Ushuaia', -54.8, -68.3, -3.0), vs.Place('Tromso', 69.65, 18.96, 1.0), vs.Place('Quito', -0.2, -78.5, -5.0)]
    for q in PLACES + far:
        for start in (1800, 1500, 900, 2400, 3000):
            jd = utils.julian_day_number(vs.Date(start, 3, 1), (6, 0, 0))
            for fn in (ev.next_solar_eclipse, ev.next_lunar_eclipse):
                for backward in (False, True):
                    try:
                        count += 1
                        fn(jd, q, ev.EclipseLocation.LOCAL, search_backward=backward, max_tries=30)
                    except Exception as exc:
                        errors += 1
                        print("   exception", fn.__name__, q.name, start, type(exc).__name__, str(exc)[:80])
    check("E15 no exceptions in %d searches over 12 places (to 69.65 N / 54.8 S) and five centuries (%.0f s)" % (count, time.time() - t0), errors == 0, errors)
    check("E16 utils.get_eclipse_engine returns this module for the Vateswara model",
          utils.get_eclipse_engine(const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA) is ev)


if __name__ == "__main__":
    start = time.time()
    saved_switches = (const.vs_nati_include_moon_latitude, const.vs_lambana_method_default, const.vs_eclipse_diameter_method_default,
                      const.vs_solar_reduce_moon_semidiameter)
    try:
        for part in (part_a, part_b, part_c, part_d, part_e):
            t = time.time()
            part()
            print("   (%.0f s)" % (time.time() - t))
    finally:
        (const.vs_nati_include_moon_latitude, const.vs_lambana_method_default, const.vs_eclipse_diameter_method_default,
         const.vs_solar_reduce_moon_semidiameter) = saved_switches
    print("\n%d checks passed, %d failed (%.0f s)" % (PASS, FAIL, time.time() - start))
    sys.exit(1 if FAIL else 0)
