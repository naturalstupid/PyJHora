#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
test_book_eclipse_vs.py -- the numbers printed in Chapters IV and V of Shukla's "Vatesvara-Siddhanta and Gola of Vatesvara" (Part II),
checked against the constants and the mean motions of the Vateswara engine (const.py, vateshwara_sidhantha.py) and eclipse_vs.py.

Each check prints  computed / book / difference / [MATCH] or [MISMATCH]. [INFO] lines are not counted: they are facts about the printed book.
Printed pages used: Ch.IV vs.2-18 (pp. 436-447), vs.19 (p. 448); Ch.V Sec.3 vs.8-9 (p. 495), Sec.5 vs.1-14 (pp. 506-514), vs.9 (p. 512).
The book's worked examples (if any) for these chapters are not in the pages checked here.

    from test_book_eclipse_vs import run_eclipse_vs_tests
    run_eclipse_vs_tests()
"""
import math
from jhora import const
from jhora.panchanga import vateshwara_sidhantha as vs
from jhora.panchanga import eclipse_vs as ev

_RESULT = {'ok': 0, 'bad': 0}


def _head(title, ref):
    print("=" * 78)
    print(title)
    print("             (%s)" % ref)
    print("=" * 78)


def _dms(deg):
    """ Degrees as signs, degrees, minutes and seconds text. """
    s = deg * 3600.0
    sign, rem = divmod(s, 30 * 3600.0)
    d, rem = divmod(rem, 3600.0)
    m, sec = divmod(rem, 60.0)
    return "%ds %d\u00b0%02d'%02.0f\"" % (sign, d, m, sec)


def _check(label, compute, book, tol, unit="", fmt="%12.4f", show=None):
    """ One counted check: |computed - book| <= tol. A failure to compute is counted as a mismatch. """
    try:
        value = compute()
    except Exception as exc:
        _RESULT['bad'] += 1
        print("  %-52s ERROR %s: %s  [MISMATCH]" % (label, type(exc).__name__, str(exc)[:60]))
        return False
    diff = value - book
    ok = abs(diff) <= tol
    _RESULT['ok' if ok else 'bad'] += 1
    shown_v = show(value) if show else fmt % value
    shown_b = show(book) if show else fmt % book
    print("  %-52s computed=%s  book=%s  diff=%+10.4f %s [%s]" % (label, shown_v, shown_b, diff, unit, "MATCH" if ok else "MISMATCH"))
    return ok


def _info(label, text):
    print("  %-52s %s  [INFO]" % (label, text))


def _mean_motion_deg(planet):
    return abs(vs._vs_daily_motion(planet))


def test_distances():
    _head("VS ECLIPSE BOOK TEST 1: Distances and orbits of the Sun and the Moon", "Chapter IV, verses 2-5 and 7, pp. 436-438")
    R = const.VS_RSINE_RADIUS
    _check("Sun's distance (yojanas, vs.5)", lambda: const.VS_SUN_MEAN_DISTANCE_YOJANAS, 459585, 0.5, "yojanas", "%12.1f")
    _check("Moon's distance (yojanas, vs.5: 3437.7 x 10)", lambda: const.VS_MOON_MEAN_DISTANCE_YOJANAS, 34377, 0.5, "yojanas", "%12.1f")
    orbit = lambda dist: dist * 62832.0 / 10000.0                       # vs.2: orbit = distance x 62832 / 10000
    _check("1' of the Sun's orbit (yojanas, vs.7 note)", lambda: orbit(const.VS_SUN_MEAN_DISTANCE_YOJANAS) / 21600.0, 133.688, 0.01, "yojanas")
    _check("1' of the Moon's orbit (yojanas, vs.7 note)", lambda: orbit(const.VS_MOON_MEAN_DISTANCE_YOJANAS) / 21600.0, 10.0, 0.001, "yojanas")
    _check("Radius used for the minutes (vs.3: 3437.7)", lambda: R, 3437.7, 0.5, "minutes", "%12.2f")


def test_diameters():
    _head("VS ECLIPSE BOOK TEST 2: Diameters of the Sun and the Moon", "Chapter IV, verses 7(c-d) and 11-14, pp. 438-444")
    R = const.VS_RSINE_RADIUS
    _check("Sun's diameter (yojanas, vs.7)", lambda: const.VS_SUN_DIAMETER_YOJANAS, 4412, 0.5, "yojanas", "%12.1f")
    _check("Moon's diameter (yojanas, vs.7)", lambda: const.VS_MOON_DIAMETER_YOJANAS, 330, 0.5, "yojanas", "%12.1f")
    _check("Sun's mean angular diameter (', vs.7: 33' approx.)", lambda: const.VS_SUN_DIAMETER_YOJANAS * R / const.VS_SUN_MEAN_DISTANCE_YOJANAS, 33.0, 0.05, "'")
    _check("Moon's mean angular diameter (', vs.7: 33')", lambda: const.VS_MOON_DIAMETER_YOJANAS * R / const.VS_MOON_MEAN_DISTANCE_YOJANAS, 33.0, 0.05, "'")
    _check("vs.14 mean diameter in const (33')", lambda: const.VS_MEAN_DIAMETER_MINUTES, 33.0, 1e-9, "'")


def test_shadow():
    _head("VS ECLIPSE BOOK TEST 3: Diameter of the Earth's Shadow", "Chapter IV, verses 8-12 and 16, pp. 439-446")
    R = const.VS_RSINE_RADIUS
    earth, sun_d, moon_d = const.VS_EARTH_DIAMETER_YOJANAS, const.VS_SUN_MEAN_DISTANCE_YOJANAS, const.VS_MOON_MEAN_DISTANCE_YOJANAS
    sun_dia = const.VS_SUN_DIAMETER_YOJANAS
    first = lambda: earth * R / moon_d
    second = lambda: (sun_dia - earth) * R / sun_d
    _check("105'24\" = Earth dia. x R / Moon dist. (vs.16)", first, 105 + 24 / 60.0, 0.02, "'", show=lambda v: "%d'%04.1f\"" % (int(v), (v % 1) * 60.0))
    _check("25'7\" = (Sun - Earth) x R / Sun dist. (vs.16)", second, 25 + 7 / 60.0, 0.03, "'", show=lambda v: "%d'%04.1f\"" % (int(v), (v % 1) * 60.0))

    def by_lengths():
        length = sun_d * earth / (sun_dia - earth)                       # vs.8
        return earth * (length - moon_d) / length * R / moon_d           # vs.8 then vs.11 (3)
    _check("Shadow by vs.8 and vs.11 (')", by_lengths, (105 + 24 / 60.0) - (25 + 7 / 60.0), 0.05, "'")
    _check("Shadow by vs.12 (')", lambda: first() - second(), (105 + 24 / 60.0) - (25 + 7 / 60.0), 0.05, "'")
    shadow = first() - second()
    _check("Shadow semi-diameter (Sec.5 vs.4: 41' approx.)", lambda: shadow / 2.0, 41.0, 1.0, "'")
    _check("Moon semi-diameter (Sec.5 vs.4: 16' approx.)", lambda: const.VS_MOON_DIAMETER_YOJANAS * R / moon_d / 2.0, 16.0, 0.6, "'")
    # Method 5 (vs.15) as printed, against the other statements of the same quantity at the mean motions
    moon_m = _mean_motion_deg(const._MOON) * 60.0
    sun_m = _mean_motion_deg(const._SUN) * 60.0
    f_moon, f_sun = const.VS_SHADOW_DAILY_MOTION_FACTORS
    printed = f_moon * moon_m - f_sun * sun_m
    reference = (105 + 24 / 60.0) - (25 + 7 / 60.0)
    _info("Method 5 as printed (2/15, 41/113), mean motions", "shadow = %.2f' ; vs.8-10 / vs.16 give %.2f' (difference %+.2f')" % (printed, reference, printed - reference))
    _info("Brahmagupta's rule on p.445 (2/15, 5/12)", "shadow = %.2f'" % (2 / 15.0 * moon_m - 5 / 12.0 * sun_m))
    _info("Karanasara rule on p.444 ((4 M - 13 S)/30)", "shadow = %.2f'" % ((4 * moon_m - 13 * sun_m) / 30.0))
    _info("Sun's coefficient that would agree", "%.4f = %.2f/113 (printed 41/113 = %.4f)" % ((2 / 15.0 * moon_m - reference) / sun_m, (2 / 15.0 * moon_m - reference) / sun_m * 113.0, 41 / 113.0))


def test_section5_rules():
    _head("VS ECLIPSE BOOK TEST 4: Constants quoted in the rules of Chapter V Section 5", "Chapter V, Sec.5 vs.2, 4, 8 and 9 with their rationales, pp. 506-512")
    R = const.VS_RSINE_RADIUS
    d_deg = _mean_motion_deg(const._MOON) - _mean_motion_deg(const._SUN)
    _check("Moon - Sun mean motion (vs.4: (791-59)/60 deg)", lambda: d_deg, (791 - 59) / 60.0, 0.05, "deg")
    shadow_semi = ((const.VS_EARTH_DIAMETER_YOJANAS * R / const.VS_MOON_MEAN_DISTANCE_YOJANAS)
                   - ((const.VS_SUN_DIAMETER_YOJANAS - const.VS_EARTH_DIAMETER_YOJANAS) * R / const.VS_SUN_MEAN_DISTANCE_YOJANAS)) / 2.0
    moon_semi = const.VS_MOON_DIAMETER_YOJANAS * R / const.VS_MOON_MEAN_DISTANCE_YOJANAS / 2.0
    _check("((S + M) / d)^2 (vs.4: 21 approx.)", lambda: ((shadow_semi + moon_semi) / d_deg) ** 2, 21.0, 1.0, "")
    _check("((S - M) / d)^2 (vs.4: 4 approx.)", lambda: ((shadow_semi - moon_semi) / d_deg) ** 2, 4.0, 0.5, "")
    _check("Latitude per degree of ksepaka (vs.2: 5 x 14/15)", lambda: ev._moon_latitude_minutes(1.0, 0.0), 5.0 * 14.0 / 15.0, 0.07, "'")
    _check("Nati for Rsin z = R (vs.9 rationale: 49')", lambda: d_deg * 60.0 / 15.0, 49.0, 0.5, "'")
    _check("R x 2 / 141 (vs.9: 49')", lambda: R * 2.0 / 141.0, 49.0, 0.5, "'")
    _check("Greatest lambana R / 860 (ghatis, vs.8: 4)", lambda: R / 860.0, 4.0, 0.01, "ghatis")
    _check("Sun's diameter/12 = Moon's motion/300 (Sec.3 vs.8-9)", lambda: const.VS_SUN_DIAMETER_YOJANAS * R / const.VS_SUN_MEAN_DISTANCE_YOJANAS / 12.0,
           _mean_motion_deg(const._MOON) * 60.0 / const.VS_SOLAR_MOON_SEMIDIAMETER_DIVISOR, 0.15, "'")


def test_six_monthly_ksepas():
    _head("VS ECLIPSE BOOK TEST 5: Motions in 177 days (six lunar months)", "Chapter V, Sec.5 vs.12-14, pp. 513-514")
    days = 177.0
    civil = const.VS_YUGA.CIVIL_DAYS
    sec = 1.0 / 3600.0
    _check("Sun, 5s 24\u00b027'6\"", lambda: (_mean_motion_deg(const._SUN) * days) % 360.0, 5 * 30 + 24 + 27 / 60.0 + 6 * sec, 30 * sec, "deg", show=_dms)
    _check("Moon, 5s 22\u00b012'53\"", lambda: (_mean_motion_deg(const._MOON) * days) % 360.0, 5 * 30 + 22 + 12 / 60.0 + 53 * sec, 30 * sec, "deg", show=_dms)
    _check("Moon's apogee, 19\u00b042'56\"", lambda: const.VS_MOON_APOGEE_REVOLUTIONS * 360.0 / civil * days, 19 + 42 / 60.0 + 56 * sec, 30 * sec, "deg", show=_dms)
    _check("Moon's ascending node, 9\u00b022'41\"", lambda: _mean_motion_deg(const._RAHU) * days, 9 + 22 / 60.0 + 41 * sec, 30 * sec, "deg", show=_dms)
    y = const.VS_YUGA
    lunar_month = 30.0 * civil / y.LUNAR_DAYS
    _check("6 lunar months (vs.14: 177d 11 ghatis)", lambda: 6.0 * lunar_month, 177.0 + 11.0 / 60.0, 0.01, "days", "%12.5f")
    _info("lunar month of the engine", "%.6f days = %dd %dg %dv (book quoting Bhaskara II: 29d 31g 50v)" % (
        lunar_month, int(lunar_month), int((lunar_month % 1) * 60), round(((lunar_month % 1) * 60 % 1) * 60)))
    _info("remainder of 177d 11g on division by 7 (vs.14)", "%dd %dg (book: 2 days 11 nadis)" % (177 % 7, 11))


def run_eclipse_vs_tests():
    """ Runs the book-number checks of Chapters IV and V. @return: (checks that match, number of checks). """
    _RESULT['ok'] = _RESULT['bad'] = 0
    for test in (test_distances, test_diameters, test_shadow, test_section5_rules, test_six_monthly_ksepas):
        test()
    total = _RESULT['ok'] + _RESULT['bad']
    print("=" * 78)
    print("VS ECLIPSE BOOK NUMBERS: %d/%d checks match the book" % (_RESULT['ok'], total))
    print("=" * 78)
    return _RESULT['ok'], total


if __name__ == "__main__":
    run_eclipse_vs_tests()
