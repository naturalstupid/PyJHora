#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
test_book_vakya.py
==================
The worked examples of the Vakyakarana book, as separate tests of vakya_panchanga.py (the "VP" engine).

Book : "Vakyakarana with Laghuprakasika by Sundararaja" (Kuppanna Sastri & Sarma, Kuppuswami Sastri Research
       Institute, Madras, 1962).  Chapter I (printed pp. 249-257), Chapter II (pp. 257-265), Chapter III (pp. 267-276).
       Example numbers (Ex. n) are the book's own.

Each test is a separate function.  It feeds the book's own inputs to the VP engine, prints  computed / book / diff
and a status, and returns (checks_passed, checks_total).  run_vakya_book_tests() runs all of them and prints a summary.
Tolerances are arc-seconds (or the stated unit) and cover only the rounding in the book's own arithmetic; each test says
where the printed result is known to be rounded.

    test_book_vp_kali_days_ex1                Ex. 1       Kali days (I.2-3)
    test_book_vp_sun_ex2                      Ex. 2       True Sun and its daily motion (I.3b-8)
    test_book_vp_moon_ex3                     Ex. 3       True Moon and its daily motion (I.9-14a)
    test_book_vp_sunrise_reduction_ex4        Ex. 4       Bhujantara, Desantara, reduction to local sunrise (I.14b-17a)
    test_book_vp_rahu_ex5                     Ex. 5       Rahu (I.17b-19a)
    test_book_vp_sun_intraday_ex6             Ex. 6       Sun at 20 nadis after sunrise (I.19b)
    test_book_vp_star_planets_ex7_8           Ex. 7, 8    True Mars and True Venus (II.1-11)
    test_book_vp_new_sodhya_ex9               Ex. 9       New Sodhya and Sodhya-Dhruva for Mars (II.12)
    test_book_vp_planet_entry_ex10_11         Ex. 10, 11  When Saturn / Jupiter enter a given longitude (II.13-17a)
    test_book_vp_table_constants_ex12_13      Ex. 12, 13  Sodhya / Mandala constants (II.18b-20)
    test_book_vp_precession_ex15_16           Ex. 15, 16  Precession of the equinoxes (III.1)
    test_book_vp_latitude_cara_ex19_21        Ex. 19, 20  Latitude of a place, Cara (III.6-7)
    test_book_vp_rasimana_ex22                Ex. 22      The twelve Rasimanas (III.9-10a)
    test_book_vp_lagna_ex23_24                Ex. 23, 24  Lagna for a time after sunrise (III.10b-15a)
    test_book_vp_not_covered                  lists the book examples the VP engine has no function for

NOTE ON Ex. 3: it needs vakya_moon_arcmin.csv (the Moon's 248-row table, book Appendix II) in const._VAKYA_DATA_DIR.
"""
import math
from jhora import const
from jhora.panchanga import vakya_panchanga as vp

_TOL_ARCSEC = 2.0           # default tolerance for longitudes: the book rounds to 1"
_OK, _BAD = "MATCH", "MISMATCH"


# ---------------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------------
def _book_deg(r=0, d=0, m=0, s=0.0):
    """ Book notation  r (rasis) d (degrees) m (minutes) s (seconds)  ->  decimal degrees. """
    return r * 30.0 + d + m / 60.0 + s / 3600.0


def _wrap(a, b):
    """ b - a the short way round the circle, in degrees. """
    return ((b - a + 180.0) % 360.0) - 180.0


def _jd_utc_of_kali_day(K):
    """ Julian day (UT) at which the VP engine's Kali day number is K (inverse of vp.kali_days_from_jd_utc). """
    return K + vp.KALI_EPOCH_JDN - 0.25 - vp._UJJAIN_LONGITUDE / 360.0


def _banner(number, title, refs):
    print("=" * 78)
    print(f"VP BOOK TEST {number}: {title}")
    print(f"             ({refs})")
    print("=" * 78)


class _Tally:
    """ Collects the pass/fail count of one test and prints each comparison. """
    def __init__(self):
        self.passed = 0
        self.total = 0

    def _record(self, ok):
        self.total += 1
        self.passed += 1 if ok else 0

    def angle(self, label, computed_deg, book_deg, tol_arcsec=_TOL_ARCSEC):
        diff = _wrap(book_deg, computed_deg) * 3600.0
        ok = abs(diff) <= tol_arcsec + 1e-9
        self._record(ok)
        print(f"  {label:<46s} computed={vp.dms(computed_deg):>16s}  book={vp.dms(book_deg):>16s}  "
              f"diff={diff:+7.1f}\"  [{_OK if ok else _BAD}]")

    def value(self, label, computed, book, tol, unit=""):
        diff = computed - book
        ok = abs(diff) <= tol + 1e-9
        self._record(ok)
        print(f"  {label:<46s} computed={computed:>14.4f}  book={book:>14.4f}  "
              f"diff={diff:+9.4f} {unit}  [{_OK if ok else _BAD}]")

    def exact(self, label, computed, book):
        ok = (computed == book)
        self._record(ok)
        print(f"  {label:<46s} computed={computed!s:>14}  book={book!s:>14}  [{_OK if ok else _BAD}]")

    def seq(self, label, computed, book, tol):
        ok = len(computed) == len(book) and all(abs(c - b) <= tol + 1e-9 for c, b in zip(computed, book))
        self._record(ok)
        print(f"  {label}")
        print(f"      computed = {[round(c, 2) for c in computed]}")
        print(f"      book     = {list(book)}   [{_OK if ok else _BAD}]")

    def result(self):
        print(f"  -> {self.passed}/{self.total} checks match the book\n")
        return self.passed, self.total


# ---------------------------------------------------------------------------------------------------------------
# Chapter I -- the Sun, Moon and Rahu
# ---------------------------------------------------------------------------------------------------------------
def test_book_vp_kali_days_ex1():
    """ Ex. 1 (p. 251): Saka year gone 1869.  Kali year = 1869 + 3179 = 5048.  Kali days to the beginning of the year
        Sarvajit = 18,43,823-40-19; the Sankramana falls at night, so the day count to the end of that day is 18,43,824,
        which is a Monday (remainder 3 when divided by 7, counted from Friday: Sunday has gone; New Year's day is Monday).
        The 24th of Kanya is 156 + 24 = 180 days later: 18,44,004. """
    _banner(1, "Kali days", "Chapter I, verses 2-3, Example 1, p. 251")
    t = _Tally()
    import datetime
    kali_year = 1869 + vp.SAKA_TO_KALI
    t.exact("Kali year (Saka 1869 + 3179)", kali_year, 5048)
    start = vp.kali_days_to_year_start(kali_year)
    whole = math.floor(start)
    t.exact("Kali days, whole part", whole, 1843823)
    nadis = (start - whole) * 60.0
    t.value("Nadis at the Sankramana", nadis, 40 + 19 / 60.0, 1 / 60.0, "nadi")      # 40-19 in the book (1 vinadi tolerance)
    end_of_day = whole + 1                           # Sankramana at 40-19 nadis is at night -> take the whole next day
    t.exact("Kali days to the end of that day", end_of_day, 1843824)
    t.exact("kali_year_of(18,43,824)", vp.kali_year_of(end_of_day), 5048)
    t.exact("Remainder on dividing by 7", end_of_day % 7, 3)
    t.exact("Date -> Kali days (14 Apr 1947)", vp.kali_days_for_date(1947, 4, 14), 1843824)
    t.exact("New Year's day is a Monday (0=Mon)", datetime.date(1947, 4, 14).weekday(), 0)
    t.exact("Kali days at end of 24th Kanya", end_of_day + 156 + 24, 1844004)
    return t.result()


def test_book_vp_sun_ex2():
    """ Ex. 2 (p. 252): True Sun for Kali days 18,44,004: 5r 23 deg 28' 33"; daily motion 59' 36". """
    _banner(2, "True Sun and daily motion", "Chapter I, verses 3b-8, Example 2, p. 252")
    t = _Tally()
    K = 1844004
    lon_arcmin, dm_arcmin = vp._sun_state(K)
    t.angle("True Sun (engine internals)", lon_arcmin / 60.0, _book_deg(5, 23, 28, 33))
    t.value("Daily motion (arc-min)", dm_arcmin, 59 + 36 / 60.0, 1 / 60.0, "'")
    t.angle("True Sun (public API)", vp.sidereal_longitude(_jd_utc_of_kali_day(K), const._SUN), _book_deg(5, 23, 28, 33))
    return t.result()


def test_book_vp_moon_ex3():
    """ Ex. 3 (pp. 253-254): True Moon for Kali day 18,44,004.
        Quotients 19, 2, 7; mnemonic No. 154 (value 7r 21d 48', previous mnemonic 7r 7d 36'); Uncorrected True Moon
        4r 11d 14' 1"; daily motion 14d 12'; 208 plus-vinadis; correction +211"; True Moon 4r 11d 17' 32". """
    _banner(3, "True Moon and daily motion", "Chapter I, verses 9-14a, Example 3, p. 254")
    t = _Tally()
    K = 1844004
    n = K - vp._MOON_SODHYA_DAYS
    q1, rem = divmod(n - 1, vp._MOON_DIV[0])
    q2, rem = divmod(rem, vp._MOON_DIV[1])
    q3, r0 = divmod(rem, vp._MOON_DIV[2])
    t.exact("Quotients (12372, 3031, 248)", (q1, q2, q3), (19, 2, 7))
    t.exact("Mnemonic number", r0 + 1, 154)
    t.exact("Plus-vinadis (7x32 - 2x8)", 32 * q3 - 8 * q2, 208)
    lon_arcmin, dm_arcmin = vp._moon_state(K)
    t.value("Daily motion (arc-min)", dm_arcmin, 14 * 60 + 12, 0.5, "'")
    t.angle("True Moon (engine internals)", lon_arcmin / 60.0, _book_deg(4, 11, 17, 32))
    t.angle("True Moon (public API)", vp.sidereal_longitude(_jd_utc_of_kali_day(K), const._MOON), _book_deg(4, 11, 17, 32))
    return t.result()


def test_book_vp_sunrise_reduction_ex4():
    """ Ex. 4 (pp. 255-256): reduce the Sun (Ex. 2) and the Moon (Ex. 3) to the true sunrise of Pudukkottai on the date
        ending 24th Kanya.  Cara +26 vinadis (half = +13), place 24.4 yojanas east of Ujjain (Desantara -26.6 vinadis),
        Bhujantara -21 vinadis: total -34.6 vinadis.  Reduced Sun 5r 23d 27' 59"; reduced Moon 4r 11d 9' 21". """
    _banner(4, "Reduction to local true sunrise", "Chapter I, verses 14b-17a, Example 4, p. 256")
    t = _Tally()
    K = 1844004
    sun_arcmin, sun_dm = vp._sun_state(K)
    moon_arcmin, moon_dm = vp._moon_state(K)
    t.value("Bhujantara (vinadis)", vp.bhujantara_vinadis(sun_arcmin / 60.0), -21.0, 0.05, "vinadi")
    # 24.4 yojanas / 55 = 0.443 nadi = 26.6 vinadis, east of Ujjain => negative.  The engine takes the longitude
    # difference (6 deg of longitude = 1 nadi), so put the place 26.6 vinadis = 2.66 deg east of Ujjain.
    east_of_ujjain = vp._UJJAIN_LONGITUDE + 26.6 / 60.0 * 6.0
    t.value("Desantara (vinadis)", vp.desantara_vinadis(east_of_ujjain), -26.6, 0.05, "vinadi")
    total = -21.0 + 13.0 - 26.6
    t.value("Total vinadis (-21 + 13 - 26.6)", total, -34.6, 0.001, "vinadi")
    t.angle("Reduced Sun", vp.reduce_to_local_sunrise(sun_arcmin / 60.0, sun_dm / 60.0, total), _book_deg(5, 23, 27, 59))
    t.angle("Reduced Moon", vp.reduce_to_local_sunrise(moon_arcmin / 60.0, moon_dm / 60.0, total), _book_deg(4, 11, 9, 21))
    return t.result()


def test_book_vp_rahu_ex5():
    """ Ex. 5 (p. 256): Rahu at the end of Kali days 18,44,004: 10r 28d 53' 26" is deducted from 12r, giving 1r 1d 6' 34".
        The book works in whole vinadis so a difference of 1" is its own rounding. """
    _banner(5, "Rahu", "Chapter I, verses 17b-19a, Example 5, p. 257")
    t = _Tally()
    K = 1844004
    rahu_arcmin, _ = vp._rahu_state(K)
    t.angle("Rahu (engine internals)", rahu_arcmin / 60.0, _book_deg(1, 1, 6, 34))
    t.angle("Rahu (public API)", vp.sidereal_longitude(_jd_utc_of_kali_day(K), const._RAHU), _book_deg(1, 1, 6, 34))
    t.angle("Ketu = Rahu + 6r (public API)", vp.sidereal_longitude(_jd_utc_of_kali_day(K), const._KETU),
            _book_deg(7, 1, 6, 34))
    return t.result()


def test_book_vp_sun_intraday_ex6():
    """ Ex. 6 (p. 257): the Sun at sunrise is 5r 23d 27' 59", daily motion +59' 36"; at 20 nadis after sunrise the motion
        is 59' 36" x 20/60 = 19' 52", so the Sun is 5r 23d 47' 51". 20 nadis = 1200 vinadis. """
    _banner(6, "Sun at a time of the day", "Chapter I, verse 19b, Example 6, p. 257")
    t = _Tally()
    sun_at_sunrise = _book_deg(5, 23, 27, 59)
    motion_deg = (59 + 36 / 60.0) / 60.0
    t.angle("Sun at 20 nadis after sunrise", vp.reduce_to_local_sunrise(sun_at_sunrise, motion_deg, 20 * 60),
            _book_deg(5, 23, 47, 51))
    return t.result()


# ---------------------------------------------------------------------------------------------------------------
# Chapter II -- the planets
# ---------------------------------------------------------------------------------------------------------------
def test_book_vp_star_planets_ex7_8():
    """ Ex. 7 (p. 259): True Mars, Kali days 18,44,004.  Mandalas 1,32,589-21 x2 and 17,158-37 x1; Total Dhruva -852' = -14d 12';
        11 cycles gone, 259-6 days in the 12th; True Mars 3r 11d 13' 55"; daily motion 32' 58".8.
        Ex. 8 (p. 260): True Venus, same day.  Mandalas 1,74,594-8, 88,756-53, 2,919-38 x6; Total Dhruva -876' = -14d 36';
        2 cycles gone, 29-27 days in the 3rd; True Venus 6r 2d 26' 27"; daily motion 1d 14' 39". """
    _banner(7, "True Mars and True Venus", "Chapter II, verses 1-11, Examples 7 and 8, pp. 259-260")
    t = _Tally()
    K = 1844004
    jd = _jd_utc_of_kali_day(K)
    dh, cycles, day, used = vp.planet_dhruva_and_cycle(const._MARS, K)
    print("  -- Mars (Ex. 7) --")
    t.value("Total Dhruva (arc-min)", dh, -852.0, 0.001, "'")
    t.exact("Cycles gone", cycles, 11)
    t.value("Days in the 12th cycle (259-6)", day, 259 + 6 / 60.0, 1 / 3600.0, "day")
    t.exact("Mandala quotients (1,32,589 / 17,158)", [q for _, q in used], [2, 1])
    lon_arcmin, dm_arcmin = vp._planet_state(const._MARS, K)
    t.angle("True Mars (engine internals)", lon_arcmin / 60.0, _book_deg(3, 11, 13, 55))
    t.value("Daily motion (arc-min)", dm_arcmin, 32 + 58.8 / 60.0, 0.02, "'")
    t.angle("True Mars (public API)", vp.sidereal_longitude(jd, const._MARS), _book_deg(3, 11, 13, 55))
    print("  -- Venus (Ex. 8) --")
    dh, cycles, day, used = vp.planet_dhruva_and_cycle(const._VENUS, K)
    t.value("Total Dhruva (arc-min)", dh, -876.0, 0.001, "'")
    t.exact("Cycles gone", cycles, 2)
    t.value("Days in the 3rd cycle (29-27)", day, 29 + 27 / 60.0, 1 / 3600.0, "day")
    t.exact("Mandala quotients (1,74,594 / 88,756 / 2,919)", [q for _, q in used], [1, 1, 6])
    lon_arcmin, dm_arcmin = vp._planet_state(const._VENUS, K)
    t.angle("True Venus (engine internals)", lon_arcmin / 60.0, _book_deg(6, 2, 26, 27))
    t.value("Daily motion (arc-min)", dm_arcmin, 60 + 14 + 39 / 60.0, 0.02, "'")
    t.angle("True Venus (public API)", vp.sidereal_longitude(jd, const._VENUS), _book_deg(6, 2, 26, 27))
    return t.result()


def test_book_vp_new_sodhya_ex9():
    """ Ex. 9 (p. 261): new Sodhya for Mars from Kali days 18,48,500.  Mandalas 1,32,589-21 x2 and 28,857-41 x1; Dhruva
        -402 + 54 + 133 = -215'; days left after the Mandalas 1,636-2; new Sodhya 18,46,863-58, Dhruva -215'. """
    _banner(8, "New Sodhya and Sodhya-Dhruva", "Chapter II, verse 12, Example 9, p. 261")
    t = _Tally()
    K = 1848500
    dh, cycles, day, used = vp.planet_dhruva_and_cycle(const._MARS, K)
    left = cycles * vp._PLANET_CONST[const._MARS]["cycle"] + day         # days remaining after the Mandala division
    t.value("Total Dhruva (arc-min)", dh, -215.0, 0.001, "'")
    t.exact("Mandala quotients (1,32,589 / 28,857)", [q for _, q in used], [2, 1])
    t.value("Days left after the Mandalas", left, 1636 + 2 / 60.0, 1 / 3600.0, "day")
    t.value("New Sodhya (days)", K - left, 1846863 + 58 / 60.0, 1 / 3600.0, "day")
    return t.result()


def test_book_vp_planet_entry_ex10_11():
    """ Ex. 10 (pp. 262-263): after Saka 1869 gone, when does Saturn enter Uttara Phalguni (4r 26d 40')?
          Kali days 18,43,823-40-19: Total Dhruva -210', 17 cycles gone, Varsadi-sesa 275-49-19.
          Book answer: 144-12-2 days after Mesha Sankramana of Saka 1872.
        Ex. 11 (pp. 263-264): after Saka 1873 expired, when does Jupiter enter Dhanishta (8r)?
          Kali days 18,45,284-42-24: Total Dhruva -14d 58', 5 cycles gone (6th cycle), VS 26-57-24.
          Book answer: 279-14-48 days after Saka 1881 expired.
        The VP engine has no inverse (longitude -> time) function, so the book's answers are checked forwards: the
        engine's longitude at the book's answer instant must equal the wanted longitude. """
    _banner(9, "When a planet reaches a longitude", "Chapter II, verses 13-17a, Examples 10 and 11, pp. 262-264")
    t = _Tally()

    def days(d, n=0, v=0):
        return d + (n + v / 60.0) / 60.0

    print("  -- Saturn (Ex. 10) --")
    K = 1843823 + (40 + 19 / 60.0) / 60.0                                  # nadis -> days
    dh, cycles, day, used = vp.planet_dhruva_and_cycle(const._SATURN, K)
    t.value("Total Dhruva (arc-min)", dh, -210.0, 0.001, "'")
    t.exact("Cycles gone", cycles, 17)
    t.value("Varsadi-sesa (275-49-19)", day, 275 + (49 + 19 / 60.0) / 60.0, 1 / 3600.0, "day")
    answer_K = vp.kali_days_to_year_start(1872 + vp.SAKA_TO_KALI) + 144 + (12 + 2 / 60.0) / 60.0
    t.angle("Saturn at the book's answer", vp.sidereal_longitude(_jd_utc_of_kali_day(answer_K), const._SATURN),
            _book_deg(4, 26, 40), tol_arcsec=60.0)          # wanted: 4r 26d 40' (one day of Saturn's motion is ~ 7')
    print("  -- Jupiter (Ex. 11) --")
    K = 1845284 + (42 + 24 / 60.0) / 60.0
    dh, cycles, day, used = vp.planet_dhruva_and_cycle(const._JUPITER, K)
    t.value("Total Dhruva (arc-min)", dh, -(14 * 60 + 58), 0.001, "'")
    t.exact("Cycles gone (6th cycle running)", cycles, 5)
    t.value("Varsadi-sesa (26-57-24)", day, 26 + (57 + 24 / 60.0) / 60.0, 1 / 3600.0, "day")
    answer_K = vp.kali_days_to_year_start(1881 + vp.SAKA_TO_KALI) + 279 + (14 + 48 / 60.0) / 60.0
    t.angle("Jupiter at the book's answer", vp.sidereal_longitude(_jd_utc_of_kali_day(answer_K), const._JUPITER),
            _book_deg(8, 0, 0), tol_arcsec=60.0)
    return t.result()


def test_book_vp_table_constants_ex12_13():
    """ Ex. 12 (p. 264): Jupiter's Sodhya 15,70,425-17 and Sodhya-Dhruva -261' (verified in the book from the mean
        longitude, which is why they are correct).  Ex. 13 (p. 265): Mercury's Mandala 2,549-15 with Dhruva -447'.
        The examples verify the printed constants by astronomy; here the engine's constants are checked against them.
        (The astronomical derivation, Haridatta's Parahita with the Vagbhava correction, is not in the engine.) """
    _banner(10, "Sodhya / Mandala constants", "Chapter II, verses 18b-20, Examples 12 and 13, pp. 264-265")
    t = _Tally()
    jup = vp._PLANET_CONST[const._JUPITER]
    t.value("Jupiter Sodhya days", jup["sodhya"][0], 1570425 + 17 / 60.0, 1e-6, "day")
    t.value("Jupiter Sodhya Dhruva (arc-min)", jup["sodhya"][1], -261.0, 1e-9, "'")
    mer = vp._PLANET_CONST[const._MERCURY]
    wanted = (2549 + 15 / 60.0, -447)
    found = any(abs(d - wanted[0]) < 1e-6 and x == wanted[1] for d, x in mer["mandalas"])
    t._record(found)
    print(f"  {'Mercury Mandala (2,549-15, -447)':<34s} present in engine table = {found}  [{_OK if found else _BAD}]")
    return t.result()


# ---------------------------------------------------------------------------------------------------------------
# Chapter III -- time, position, direction
# ---------------------------------------------------------------------------------------------------------------
def test_book_vp_precession_ex15_16():
    """ Ex. 15 (p. 267): 5048 Kali expired: (5048-3600) less 1/121, divided by 60 = 23d 56'.
        Ex. 16: 5060 Kali gone: 24d 8' is above 24d, so 48d - 24d 8' = 23d 52'. """
    _banner(11, "Precession of the equinoxes", "Chapter III, verse 1, Examples 15 and 16, p. 267")
    t = _Tally()
    t.angle("Precession, Kali 5048", vp.book_precession(5048), _book_deg(0, 23, 56), tol_arcsec=5.0)    # book rounds to the minute
    t.angle("Precession, Kali 5060", vp.book_precession(5060), _book_deg(0, 23, 52), tol_arcsec=5.0)
    return t.result()


def test_book_vp_latitude_cara_ex19_21():
    """ Ex. 19 (p. 269): Pudukkottai's equinoctial shadow is 2 angulas 12 vyangulas = 2.2 angulas.  The book's sine table gives
        a latitude of 10d 34' and adds 'actually it is 10d 24''.  The engine uses the exact tangent, so it is compared with
        the 10d 24' (and the 10d 34' is only printed).
        Ex. 20 (p. 269): Sayana Sun 3r 29d + precession 23d 30' = 4r 22d 30' (Koti side), shadow 3 angulas: Cara
        = -(60 + 12) = -72 vinadis. """
    _banner(12, "Latitude from the equinoctial shadow, Cara", "Chapter III, verses 6-7, Examples 19 and 20, pp. 269")
    t = _Tally()
    lat = math.degrees(math.atan(2.2 / vp._GNOMON))
    t.angle("Latitude from shadow 2.2 (tan)", lat, _book_deg(0, 10, 24), tol_arcsec=90.0)
    print(f"      (the book's table arithmetic gives {vp.dms(_book_deg(0, 10, 34))} for the same shadow)")
    t.value("Shadow at latitude 10d 24' (angulas)", vp.equinoctial_shadow(_book_deg(0, 10, 24)), 2.2, 0.01, "ang")
    sayana = _book_deg(3, 29) + _book_deg(0, 23, 30)
    t.value("Cara, Sayana Sun 4r 22d 30', shadow 3", vp.cara_vinadis(sayana, 3.0), -72.0, 1e-6, "vinadi")
    return t.result()


def test_book_vp_rasimana_ex22():
    """ Ex. 22 (p. 270): Cara intervals 44, 36 and 14 vinadis give the twelve Sayana Rasimanas
        256, 281, 316, 330, 317, 300, 300, 317, 330, 316, 281, 256 vinadis. """
    _banner(13, "The twelve Rasimanas", "Chapter III, verses 9-10a, Example 22, p. 270")
    t = _Tally()
    book = (256, 281, 316, 330, 317, 300, 300, 317, 330, 316, 281, 256)
    t.seq("Rasimanas from Cara intervals 44, 36, 14", vp._rasimana_from_cara_intervals(44, 36, 14), book, 1e-9)
    # The public rasimana_vinadis takes the equinoctial shadow; 44/20 = 2.2 angulas of shadow gives intervals 44, 35.2, 14.7,
    # which is the book's example to within the book's own rounding of the three intervals.
    t.seq("Rasimanas from shadow 2.2 angulas", vp.rasimana_vinadis(2.2), book, 1.0)
    return t.result()


def test_book_vp_lagna_ex23_24():
    """ Ex. 23 (pp. 271-272): Lagna 47 nadis after sunrise.  Sun at sunrise 178d 28', daily motion 59'.6 -> Sun at 47 nadis
        179d 14'.7; precession 23d 56'.5 -> Sayana Sun 6r 23d 11'.2.  Rasimanas of Ex. 22.  Sayana Lagna 4r 6d 31'.8; Lagna
        (Nirayana) 3r 12d 35'.3.  The book rounds its intermediate vinadis, so 1' is allowed.
        Ex. 24 (p. 272): Lagna 1 nadi after sunrise, Sayana Sun 6r 22d 26'.5 (as printed): Sayana Lagna 6r 28d 26'.5;
        Lagna 6r 4d 29'. """
    _banner(14, "Lagna (orient ecliptic point)", "Chapter III, verses 10b-15a, Examples 23 and 24, pp. 271-272")
    t = _Tally()
    rasimana = vp._rasimana_from_cara_intervals(44, 36, 14)
    precession = _book_deg(0, 23, 56) + 0.5 / 60.0                          # 23d 56'.5
    sayana_sun = _book_deg(0, 179, 14) + 0.7 / 60.0 + precession           # 179d 14'.7 + precession
    t.angle("Sayana Sun at 47 nadis", sayana_sun, _book_deg(6, 23, 11) + 0.2 / 60.0, tol_arcsec=1.0)
    lagna_sayana = vp.lagna_sayana(sayana_sun, 47 * 60, rasimana)
    t.angle("Sayana Lagna (Ex. 23)", lagna_sayana, _book_deg(4, 6, 31) + 0.8 / 60.0, tol_arcsec=60.0)
    t.angle("Lagna (Ex. 23)", lagna_sayana - precession, _book_deg(3, 12, 35) + 0.3 / 60.0, tol_arcsec=60.0)
    sayana_sun24 = _book_deg(6, 22, 26) + 0.5 / 60.0
    lagna_sayana24 = vp.lagna_sayana(sayana_sun24, 60, rasimana)
    t.angle("Sayana Lagna (Ex. 24)", lagna_sayana24, _book_deg(6, 28, 26) + 0.5 / 60.0, tol_arcsec=2.0)
    t.angle("Lagna (Ex. 24)", lagna_sayana24 - precession, _book_deg(6, 4, 29), tol_arcsec=75.0)   # book: 23d 56'.5 off its own Sayana 6r 28d 26'.5 by 1'
    return t.result()


# ---------------------------------------------------------------------------------------------------------------
# What the VP engine cannot be tested against yet
# ---------------------------------------------------------------------------------------------------------------
def test_book_vp_not_covered():
    """ Book examples with no matching function in vakya_panchanga.py, so no test is possible yet. """
    print("=" * 78)
    print("VP BOOK TESTS NOT POSSIBLE YET (no engine function to test)")
    print("=" * 78)
    for line in (
        "Ex. 14a, 14b        Correctors of Mars / Venus by Haridatta's Parahita (derivation of the table; engine reads the table)",
        "Ex. 17a, 17b, 18    Sine, arc, Bhuja / Koti by the 11, 10.5, 9, 7, 4, 1.5 sine segments",
        "Ex. 21              Day-time / night-time / mid-day from Cara (plain arithmetic on Ex. 20)",
        "Ex. 23 (alt.)       Lagna after sunset by adding 6 rasis to the Sun",
        "Ex. 25, 26, 27      Time for a given Lagna (III.16b-19)",
        "Ex. 28              Moon's declination (III.19a-20); declination_of_planets() uses the SS table, not compared",
        "Ex. 29, 30          Mid-day shadow, shadow at any time, human shadow (III.21-29)",
        "Ex. 31              Time from a given human shadow (III.26b-29); reverse of Ex. 30",
        "Ex. 32              Time and longitude of a conjunction from given longitudes and motions (IV.2b-5a);",
        "                    next_conjunction_of_planet_pair() works from a Julian day, not from given longitudes",
        "Ex. 33-38           Chapter IV, eclipses (pp. 278-284): angular diameters, Rahu, lunar eclipse (Ex. 36-37, p. 280),",
        "                    solar eclipse with parallax (Ex. 38, pp. 281-284) -- no eclipse module for the Vakya model yet",
        "Ex. 39-44           Chapter V, heliacal rising / setting, Pata (pp. 285-289)",
    ):
        print("  " + line)
    print()
    return 0, 0


# ---------------------------------------------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------------------------------------------
VAKYA_BOOK_TESTS = (
    test_book_vp_kali_days_ex1,
    test_book_vp_sun_ex2,
    test_book_vp_moon_ex3,
    test_book_vp_sunrise_reduction_ex4,
    test_book_vp_rahu_ex5,
    test_book_vp_sun_intraday_ex6,
    test_book_vp_star_planets_ex7_8,
    test_book_vp_new_sodhya_ex9,
    test_book_vp_planet_entry_ex10_11,
    test_book_vp_table_constants_ex12_13,
    test_book_vp_precession_ex15_16,
    test_book_vp_latitude_cara_ex19_21,
    test_book_vp_rasimana_ex22,
    test_book_vp_lagna_ex23_24,
)


def run_vakya_book_tests():
    """ Runs every VP book test, one after the other.  A test that raises is reported and counted as failed; the rest still run.
        @return: (checks passed, checks total) over all tests
    """
    passed = total = 0
    failed_tests = []
    for fn in VAKYA_BOOK_TESTS:
        try:
            p, n = fn()
        except Exception as exc:                          # keep going: one missing table must not hide the other tests
            print(f"  !! {fn.__name__} raised {type(exc).__name__}: {exc}\n")
            failed_tests.append(fn.__name__)
            p, n = 0, 1
        passed += p
        total += n
    test_book_vp_not_covered()
    print("=" * 78)
    print(f"VP BOOK EXAMPLES: {passed}/{total} checks match the book across {len(VAKYA_BOOK_TESTS)} tests"
          + (f";  RAISED: {', '.join(failed_tests)}" if failed_tests else ""))
    print("=" * 78)
    return passed, total


if __name__ == "__main__":
    run_vakya_book_tests()
