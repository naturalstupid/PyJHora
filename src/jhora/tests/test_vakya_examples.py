#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Acceptance tests for jhora.panchanga.vakya_panchanga.

Part A  the worked Examples of the book (English translation pp.250-274):  Examples 1-11, 15-16, 20, 22-24.
Part B  independent checks of every table (Mandalas against the book's own Table II) and of dates before the Sodhya.
Part C  SS-signature checks (planet_list, sidereal_longitude, sunrise/sunset, ascendant) against an independent
        low-precision solar model written here with plain math (not Swiss Ephemeris).
Part D  no planet is named in the code.

Run:  python test_vakya_examples.py          (needs the two CSVs in const._VAKYA_DATA_DIR)"""
import ast
import inspect
import math
import sys
from datetime import date
from jhora import const
from jhora.panchanga import vakya_panchanga as V

FAIL = []


def check(name, cond, detail=""):
    print("%-4s %-62s %s" % ("OK" if cond else "FAIL", name, detail))
    if not cond:
        FAIL.append(name)


def close(name, got_deg, book_dms, tol_sec=1.5, note=""):
    r, d, m, s = book_dms
    want = (r * 30 + d + m / 60.0 + s / 3600.0)
    diff = ((got_deg - want + 180) % 360 - 180) * 3600.0
    check(name, abs(diff) <= tol_sec, "got %-17s book %dr %dd %d' %d\" diff %+.1f\"%s" % (V.dms(got_deg), r, d, m, s, diff,
                                                                                    ("  " + note) if note else ""))


SUN, MOON, RAHU, KETU = const._SUN, const._MOON, const._RAHU, const._KETU
STAR = V._STAR_PLANETS                                    # (Mars, Mercury, Jupiter, Venus, Saturn) as const aliases
MARS, MERCURY, JUPITER, VENUS, SATURN = const._MARS, const._MERCURY, const._JUPITER, const._VENUS, const._SATURN


def lon(p, K):
    return V.longitude_end_of_day(p, K)[0]


# =============================== PART A: the book's examples ==========================================
# ---- Example 1: Kali days (I.2-3) ----
Y = 1869 + V.SAKA_TO_KALI
S = V.kali_days_to_year_start(Y)
check("Ex1 Kali days at Mesha sankramana Saka 1869", abs(S - (1843823 + 40 / 60 + 19 / 3600)) < 1e-3, "got %.5f book 18,43,823-40-19" % S)
check("Ex1 date mapping: 14 Apr 1947 -> 18,43,824", V.kali_days_for_date(1947, 4, 14) == 1843824)
check("Ex1 date mapping: 11 Oct 1947 -> 18,44,004", V.kali_days_for_date(1947, 10, 11) == 1844004)
check("weekday of Kali day K = (K+5) mod 7 on 5 dates",
      all((V.kali_days_for_date(*d) + 5) % 7 == date(*d).isoweekday() % 7
          for d in ((2000, 1, 1), (2026, 10, 10), (1947, 8, 15), (1900, 3, 1), (2100, 12, 31))))
jd_sunrise = 2432470 - 0.25 - const.ujjain_lat_long[1] / 360.0      # 06:00 LMT at Ujjain on 11 Oct 1947
check("JD(UT) -> Kali days at Ujjain sunrise 11 Oct 1947", abs(V.kali_days_from_jd_utc(jd_sunrise) - 1844004) < 1e-9)

K = 1844004
sun, sdm = V.longitude_end_of_day(SUN, K)
close("Ex2 True Sun, Kali 18,44,004", sun, (5, 23, 28, 33))
check("Ex2 Sun daily motion 59'36\"", abs(sdm * 60 - (59 + 36 / 60.0)) < 0.01, "got %.3f'" % (sdm * 60))
moon, mdm = V.longitude_end_of_day(MOON, K)
close("Ex3 True Moon", moon, (4, 11, 17, 32))
check("Ex3 Moon daily motion 14d12'", abs(mdm - 14.2) < 1e-6, "got %.4f" % mdm)
bh = V.bhujantara_vinadis(sun)
check("Ex4 Bhujantara = -21", abs(bh + 21) < 1e-9, "got %.2f" % bh)
vin = bh + 26 / 2.0 + V.desantara_vinadis(const.ujjain_lat_long[1] + 24.4 / 55.0 * 6.0)   # 24.4 yojanas east
check("Ex4 total vinadis = -34.6", abs(vin + 34.6) < 0.05, "got %.2f" % vin)
close("Ex4(a) reduced Sun", V.reduce_to_local_sunrise(sun, sdm, vin), (5, 23, 27, 59))
close("Ex4(b) reduced Moon", V.reduce_to_local_sunrise(moon, mdm, vin), (4, 11, 9, 21))
close("Ex5 Rahu", lon(RAHU, K), (1, 1, 6, 34))
check("Ex5 Ketu = Rahu + 180", abs(((lon(KETU, K) - lon(RAHU, K)) % 360) - 180) < 1e-9)
sun_after = V.reduce_to_local_sunrise(V.reduce_to_local_sunrise(sun, sdm, vin), sdm, 0) + sdm * 20 / 60.0
close("Ex6 Sun 20 nadis after sunrise", sun_after, (5, 23, 47, 51), tol_sec=2)

dh, cyc, day, used = V.planet_dhruva_and_cycle(MARS, K)
check("Ex7 Mars total Dhruva -852'", abs(dh + 852) < 1e-9, "got %s" % dh)
check("Ex7 Mars 11 cycles gone, 259-6 days in 12th", cyc == 11 and abs(day - (259 + 6 / 60.0)) < 1e-6)
close("Ex7 True Mars", lon(MARS, K), (3, 11, 13, 55), note="(book p.259, checked on the page image)")
dh, cyc, day, used = V.planet_dhruva_and_cycle(VENUS, K)
check("Ex8 Venus total Dhruva -876'", abs(dh + 876) < 1e-9, "got %s" % dh)
check("Ex8 Venus 2 cycles gone, 29-27 days in 3rd", cyc == 2 and abs(day - (29 + 27 / 60.0)) < 1e-6)
close("Ex8 True Venus", lon(VENUS, K), (6, 2, 26, 27))
dh, cyc, day, used = V.planet_dhruva_and_cycle(MARS, 1848500)
rest = (1848500 - (1552827 + 35 / 60.0)) - sum(d * q for d, q in used)
check("Ex9 Mars total Dhruva -215'", abs(dh + 215) < 1e-9, "got %s" % dh)
check("Ex9 remainder after Mandalas = 1,636-2", abs(rest - (1636 + 2 / 60.0)) < 1e-6, "got %.4f" % rest)
Ks = 1843823 + 40 / 60.0 + 19 / 3600.0
dh, cyc, day, used = V.planet_dhruva_and_cycle(SATURN, Ks)
check("Ex10 Saturn total Dhruva -210'", abs(dh + 210) < 1e-9, "got %s" % dh)
check("Ex10 Saturn 17 cycles gone, VS 275-49-19", cyc == 17 and abs(day - (275 + 49 / 60.0 + 19 / 3600.0)) < 1e-4)
P = V._load_planets()
r21 = [r for r in P[SATURN][21] if r[0] == 378][0]
r22 = [r for r in P[SATURN][22] if r[0] == 30][0]
check("Ex10 table XXI-378 = 4r 29d 44' cor +1", abs(r21[1] - ((4 * 30 + 29) * 60 + 44)) < 1e-9 and r21[2] == 1)
check("Ex10 table XXII-30 = 5r 3d 30' cor -1", abs(r22[1] - ((5 * 30 + 3) * 60 + 30)) < 1e-9 and r22[2] == -1)
Kj = 1845284 + 42 / 60.0 + 24 / 3600.0
dh, cyc, day, used = V.planet_dhruva_and_cycle(JUPITER, Kj)
check("Ex11 Jupiter total Dhruva -898' (= -14d58')", abs(dh + 898) < 1e-9, "got %s" % dh)
check("Ex11 Jupiter 5 cycles gone, VS 26-57-24", cyc == 5 and abs(day - (26 + 57 / 60.0 + 24 / 3600.0)) < 1e-4)
j30 = [r for r in P[JUPITER][3] if r[0] == 30][0]
j60 = [r for r in P[JUPITER][3] if r[0] == 60][0]
check("Ex11 table III-30 = 8r 8d 37' cor -2", abs(j30[1] - ((8 * 30 + 8) * 60 + 37)) < 1e-9 and j30[2] == -2)
check("Ex11 table III-60 = 8r 14d 20' cor -2", abs(j60[1] - ((8 * 30 + 14) * 60 + 20)) < 1e-9 and j60[2] == -2)

# ---- Chapter III ----
check("Ex15 precession for 5048 Kali = 23d56'", abs(V.book_precession(5048) - (23 + 56 / 60.0)) < 0.01, "got %.4f" % V.book_precession(5048))
check("Ex16 precession for 5060 Kali = 23d52'", abs(V.book_precession(5060) - (23 + 52 / 60.0)) < 0.01, "got %.4f" % V.book_precession(5060))
c20 = V.cara_vinadis(3 * 30 + 29 + 23.5, 3.0)
check("Ex20 Cara = -72 vinadis (Sun 3r 29d + 23d30', shadow 3)", abs(c20 + 72.0) < 1e-9, "got %.3f" % c20)
c4 = V.cara_vinadis(sun + V.book_precession(5048), 2.2)
check("Ex4 Cara at Pudukkottai on that date = +26 vinadis (shadow 2.2)", abs(c4 - 26.0) < 1.0, "got %.2f" % c4)
ras22 = V._rasimana_from_cara_intervals(44, 36, 14)
check("Ex22 twelve Rasimanas", [round(x) for x in ras22] == [256, 281, 316, 330, 317, 300, 300, 317, 330, 316, 281, 256], str([round(x) for x in ras22]))
check("Rasimanas sum to one day (3600 vinadis)", abs(sum(V.rasimana_vinadis(2.2)) - 3600.0) < 1e-9)
prec = 23 + 56.5 / 60.0
sun47 = 178 + 28 / 60.0 + (59.6 / 60.0) * 47 / 60.0
l23 = (V.lagna_sayana(sun47 + prec, 47 * 60.0, ras22) - prec) % 360.0
close("Ex23 Lagna at 47 nadis from sunrise", l23, (3, 12, 35, 18), tol_sec=60, note="(book 3r 12d 35'.3)")
l23b = (V.lagna_sayana((sun47 + prec + 180.0) % 360.0, 1054.0, ras22) - prec) % 360.0
check("Ex23 alternative (after-sunset) method gives the same Lagna", abs(l23b - l23) < 0.002, "%.4f vs %.4f (book rounds the 1054 vinadis)" % (l23b, l23))
l24 = (V.lagna_sayana(178 + 29 / 60.0 + prec, 60.0, ras22) - prec) % 360.0
close("Ex24 Lagna at 1 nadi from sunrise", l24, (6, 4, 29, 0), tol_sec=60, note="(book 6r 4d 29')")

# =============================== PART B: tables ======================================================
bad = []
for pl in STAR:
    c = V._PLANET_CONST[pl]
    for D, x in c["mandalas"]:
        rv = D * V._MAHAYUGA_REVS[pl] / V._MAHAYUGA_DAYS
        resid_deg = ((rv + 0.5) % 1 - 0.5) * 360.0
        if abs(resid_deg - x / 60.0) > 0.1:
            bad.append((pl, round(D, 2), round(resid_deg, 2), x / 60.0))
check("all 22 used Mandalas: book Dhruva == residual from Table II (<0.1 deg)", not bad, str(bad))
for D, x in V._PLANET_CONST[JUPITER]["unused_mandalas"]:
    rv = D * V._MAHAYUGA_REVS[JUPITER] / V._MAHAYUGA_DAYS
    check("Jupiter M1 4,74,875-27 is NOT a period (excluded)", abs(((rv + 0.5) % 1 - 0.5) * 360.0 - x / 60.0) > 100)
err = []
for Kt in (-100000, 0, 1, 2, 1000, 1500000):
    for p in V.planet_list:
        try:
            V.longitude_end_of_day(p, Kt)
        except Exception as e:
            err.append((Kt, p, repr(e)))
check("K = -100000, 0, 1, 2, 1000, 1500000 run for all 9 bodies", not err, str(err[:3]))
worst = 0.0
for pl in STAR:
    s0 = int(V._PLANET_CONST[pl]["sodhya"][0])
    a, b2, c2 = (lon(pl, s0 + k) for k in (-1, 0, 1))
    worst = max(worst, abs((b2 - a + 180) % 360 - 180 - ((c2 - b2 + 180) % 360 - 180)))
check("planet longitudes continuous across each Sodhya", worst < 1.0, "largest change in daily step %.2f deg" % worst)
n = {pl: sum(len(v) for v in P[pl].values()) for pl in STAR}
check("table rows 570/528/231/195/551", [n[MARS], n[MERCURY], n[JUPITER], n[VENUS], n[SATURN]] == [570, 528, 231, 195, 551], str(list(n.values())))
Mn = V._load_moon()
check("Moon table closure v1+v247 = v248", Mn[1] + Mn[247] == Mn[248])

# =============================== PART C: SS-signature API =============================================
check("planet_list maps swe keys to 0-based ids 0..8", sorted(V.planet_list.values()) == list(range(9)))
check("ephemeris_planet_index round-trip", all(V.planet_list[V.ephemeris_planet_index(i)] == i for i in range(9)))
check("ephemeris_planet_index('L') passes through", V.ephemeris_planet_index(const._ascendant_symbol) == const._ascendant_symbol)
try:
    V.ephemeris_planet_index(99)
    check("ephemeris_planet_index rejects unknown id", False)
except ValueError:
    check("ephemeris_planet_index rejects unknown id", True)
place = V.Place("Chennai,IN", 13.0389, 80.2619, +5.5)
jd_at = lambda Kv: Kv + V.KALI_EPOCH_JDN - 0.25 - const.ujjain_lat_long[1] / 360.0          # jd_utc at Kali day Kv
worst = max(abs(((V.sidereal_longitude(jd_at(K), p, place) - lon(p, K) + 180) % 360) - 180) for p in V.planet_list)
check("sidereal_longitude(jd_utc, planet, place) == book value at whole Kali day", worst < 1e-9, "max diff %.2e" % worst)
worst = 0.0
for p in V.planet_list:
    a, b = lon(p, K), lon(p, K + 1)
    mid = V.sidereal_longitude(jd_at(K + 0.5), p, place)
    if p == SUN:
        continue                                   # the Sun is evaluated directly, not interpolated
    worst = max(worst, abs(((mid - (a + ((b - a + 180) % 360 - 180) / 2) + 180) % 360) - 180))
check("sidereal_longitude interpolates linearly between day-ends (II.19b)", worst < 1e-9, "max diff %.2e" % worst)
jd_loc = jd_at(K + 0.3) + place.timezone / 24.0
check("_sidereal_longitude_impl(local jd) == sidereal_longitude(jd_utc)",
      abs(V._sidereal_longitude_impl(jd_loc, place, MOON) - V.sidereal_longitude(jd_at(K + 0.3), MOON, place)) < 1e-9)
check("solar_longitude/lunar_longitude wrappers", V.solar_longitude(jd_at(K), place) == V.sidereal_longitude(jd_at(K), SUN, place)
      and V.lunar_longitude(jd_at(K), place) == V.sidereal_longitude(jd_at(K), MOON, place))
jd_prev = jd_at(K - 0.5) + place.timezone / 24.0                       # inside the day that ENDS at K (daily motion 14d12')
check("daily_planet_speed: Moon 14.2 deg/day (Ex3), Saturn small and positive",
      abs(V.daily_planet_speed(jd_prev, place, const.MOON_ID) - 14.2) < 0.01 and 0 < V.daily_planet_speed(jd_prev, place, const.SATURN_ID) < 0.2,
      "%.3f %.3f" % (V.daily_planet_speed(jd_prev, place, const.MOON_ID), V.daily_planet_speed(jd_prev, place, const.SATURN_ID)))
pp = V.planetary_positions(jd_loc, place)
check("planetary_positions format [[id,(rasi,deg)],...] for 9 bodies", len(pp) == 9 and all(0 <= r < 12 and 0 <= d < 30 for _, (r, d) in pp))
check("ayanamsa_model 'ss' is the default; get_ayanamsa_value within +-27", V.ayanamsa_model == 'ss' and abs(V.get_ayanamsa_value(jd_loc, place)) <= 27.0)
V.set_ayanamsa_mode('vakya')
check("set_ayanamsa_mode('vakya') gives the book's precession (23d56' for 1947)",
      abs(V.get_ayanamsa_value(jd_loc, place) - V.book_precession(5048)) < 0.1, "%.3f" % V.get_ayanamsa_value(jd_loc, place))
V.reset_ayanamsa_mode()

# ---- independent solar model (plain math) for sunrise and Lagna ----
def indep_sun_tropical(jd):
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    return (L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360


def indep_eot_decl(jd):
    lam = math.radians(indep_sun_tropical(jd))
    eps = math.radians(23.439 - 0.0000004 * (jd - 2451545.0))
    ra = math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    eot_min = (((L - ra + 180) % 360) - 180) * 4.0
    return eot_min, math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def indep_sunrise_lmt_hours(jd_noon, lat):
    eot, dec = indep_eot_decl(jd_noon)
    c = (math.sin(math.radians(-0.833)) - math.sin(math.radians(lat)) * math.sin(math.radians(dec))) / \
        (math.cos(math.radians(lat)) * math.cos(math.radians(dec)))
    return 12.0 - eot / 60.0 - math.degrees(math.acos(max(-1, min(1, c)))) / 15.0


def indep_tropical_lagna(jd_utc, lat, lon_east):
    lst = math.radians((280.46061837 + 360.98564736629 * (jd_utc - 2451545.0) + lon_east) % 360)
    eps = math.radians(23.439)
    return math.degrees(math.atan2(math.cos(lst), -(math.sin(lst) * math.cos(eps) + math.tan(math.radians(lat)) * math.sin(eps)))) % 360


def indep_book_sunrise_lmt_hours(jd_noon, lat):
    """What the BOOK's method approximates: Equation of Centre only (no RA reduction, I.14b-16a note 9), no refraction."""
    n = jd_noon - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = (L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360
    eot_centre = ((L - lam + 180) % 360 - 180) * 4.0
    dec = indep_eot_decl(jd_noon)[1]
    c = -math.tan(math.radians(lat)) * math.tan(math.radians(dec))
    return 12.0 - eot_centre / 60.0 - math.degrees(math.acos(max(-1, min(1, c)))) / 15.0


def ours_lmt_hours(pl, jd0):
    sr = V._sunrise_jd(jd0, pl)
    return (sr + V.zone_longitude_correction_days(pl) - (math.floor(sr - 0.5) + 0.5)) * 24.0


w_book, w_full = {}, {}
for pl_name, pl in (("Chennai 13N", place), ("Chicago-like 42N", V.Place("Test", 42.0, -87.6, -6.0)),
                    ("Cape Town 34S", V.Place("CT", -34.0, 18.4, 2.0))):
    a = b = 0.0
    for d in range(0, 365, 9):
        jd0 = 2461041.5 + d + 0.5
        ju = jd0 - pl.timezone / 24.0
        a = max(a, abs(ours_lmt_hours(pl, jd0) - indep_book_sunrise_lmt_hours(ju, pl.latitude)) * 60.0)
        b = max(b, abs(ours_lmt_hours(pl, jd0) - indep_sunrise_lmt_hours(ju, pl.latitude)) * 60.0)
    w_book[pl_name], w_full[pl_name] = a, b
check("sunrise within 5 min of an independent model of the book's own approximation (3 places, all year)", max(w_book.values()) < 5.0,
      "  ".join("%s %.1f" % (k, v) for k, v in w_book.items()))
check("sunrise within 18 min of full solar geometry (book ignores RA reduction of the equation of time and refraction)",
      max(w_full.values()) < 18.0, "  ".join("%s %.1f" % (k, v) for k, v in w_full.items()))
dl_ok = True
for d in range(0, 365, 30):
    jd0 = 2461041.5 + d + 0.5
    L = (V._sunset_jd(jd0, place) - V._sunrise_jd(jd0, place)) * 24.0
    dl_ok = dl_ok and 10.9 < L < 13.1
check("day length at 13N between 10.9 h and 13.1 h all year", dl_ok)
# Lagna: at sunrise it must equal the Sun; it must rise through 12 signs per day; must match independent Lagna
for pl_name, pl, lagna_tol in (("Chennai", place, 5.0), ("42N", V.Place("Test", 42.0, -87.6, -6.0), 7.5)):
    worst_sr = 0.0
    for d in range(0, 365, 17):
        jd0 = 2461041.5 + d + 0.5
        sr = V._sunrise_jd(jd0, pl)
        asc = V._ascendant_longitude(sr, pl)
        sun_l = V.sidereal_longitude(sr - pl.timezone / 24.0, SUN, pl)
        worst_sr = max(worst_sr, abs(((asc - sun_l + 180) % 360) - 180))
    check("Lagna at sunrise equals the Sun (%s)" % pl_name, worst_sr < 0.05, "max diff %.3f deg" % worst_sr)
    mono = True
    tot = 0.0
    for d in (10, 100, 200, 300):
        jd0 = 2461041.5 + d + 0.5
        sr = V._sunrise_jd(jd0, pl)
        prev = V._ascendant_longitude(sr, pl)
        total = 0.0
        for k in range(1, 97):                                          # every 15 minutes for 24 h
            cur = V._ascendant_longitude(sr + k / 96.0, pl)
            step = (cur - prev) % 360.0
            mono = mono and 0.0 < step < 20.0
            total += step
            prev = cur
        tot = max(tot, abs(total - 360.0))
    check("Lagna moves forward every 15 min and makes one turn per day (%s)" % pl_name, mono and tot < 3.0, "turn error %.2f deg" % tot)
    wl = 0.0
    for d in range(0, 365, 23):
        for hr in (0.1, 0.35, 0.6, 0.85):
            jd = 2461041.5 + d + hr
            ours = V._ascendant_longitude(jd, pl)
            ju = jd - pl.timezone / 24.0
            offset = (indep_sun_tropical(ju) - V.sidereal_longitude(ju, SUN, pl)) % 360.0     # tropical - Vakya frame
            theirs = (indep_tropical_lagna(ju, pl.latitude, pl.longitude) - offset) % 360.0
            wl = max(wl, abs(((ours - theirs + 180) % 360) - 180))
    check("Lagna within %.1f deg of an independent LST-based Lagna (%s)" % (lagna_tol, pl_name), wl < lagna_tol,
          "max diff %.2f deg (the book's Rasimana is a linear approximation, worse at high latitude)" % wl)
a = V.ascendant(jd_loc, place)
check("ascendant() format [rasi, deg, nakshatra, pada]", len(a) == 4 and 0 <= a[0] < 12 and 0 <= a[1] < 30 and 1 <= a[2] <= 27 and 1 <= a[3] <= 4, str(a))

# =============================== PART D: no planet names in the code =================================
names = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu", "surya", "chandra", "kuja", "budha",
         "guru", "sukra", "sani")
tree = ast.parse(inspect.getsource(V))
doc_nodes = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body and isinstance(node.body[0], ast.Expr) \
            and isinstance(getattr(node.body[0], "value", None), ast.Constant) and isinstance(node.body[0].value.value, str):
        doc_nodes.add(id(node.body[0].value))
hits = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_nodes:
        if node.value.strip().lower() in names:
            hits.append(node.value)
    if isinstance(node, ast.Dict):                       # no dict is keyed by a bare string naming a planet
        for k in node.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str) and k.value.strip().lower() in names:
                hits.append(k.value)
check("no planet name used as a string / dict key (all keys are const aliases)", not hits, str(sorted(set(hits)))[:200])

print("\n%s : %d failed" % ("ALL PASSED" if not FAIL else "FAILURES", len(FAIL)))
sys.exit(1 if FAIL else 0)
