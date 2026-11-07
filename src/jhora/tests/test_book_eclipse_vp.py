#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
test_book_eclipse_vp.py
=======================
Tests of eclipse_vp.py (the Vakya eclipse engine, "VP"), in the same style as test_book_vakya.py: one function per topic, each
printing computed / book / diff with a status, each returning (checks_passed, checks_total).

PART 1 -- BOOK EXAMPLES  (Vakyakarana with Laghuprakasika, Kuppanna Sastri & Sarma, Madras 1962; Chapter IV, printed pp. 276-284,
         plus the Sine rules of Chapter III, p. 267-268).  The book's own numbers are fed in; the book's printed results are the
         reference.  Tolerance = half a unit of the last digit the book prints, widened only where the book's own arithmetic is
         visibly rounded (each such place says so).
             test_book_ecl_sine_bhuja_koti_ex17_18      Ex. 17a, 18     Sine, Bhuja, Koti             III.2b-6
             test_book_ecl_conjunction_ex32             Ex. 32          Time of conjunction           IV.1-5a
             test_book_ecl_parva_end_ex33               Ex. 33          Sun = Moon at the end of Ama  IV.5b-7a
             test_book_ecl_diameters_latitude_ex34_35   Ex. 34, 35      Diameters, Moon's latitude    IV.7b-9
             test_book_ecl_lunar_ex36_37                Ex. 36, 37      Lunar eclipse, all elements   IV.10-15
             test_book_ecl_parallax_table_ex38          Ex. 38 (part)   Parallax table                IV.20-20a
             test_book_ecl_solar_ex38                   Ex. 38          Solar eclipse at Pudukkottai  IV.16-24
             test_book_ecl_solar_ex38_given_time        Ex. 38          the same, Lagna from the Sun at the given time (information only)

PART 2 -- DATE LEVEL  (the public functions that test.py / test1.py call).  These have no book answer, so:
             test_eclipse_vp_api_consistency            next_/is_ functions agree with each other (no outside reference)
             test_eclipse_vp_modern_lunar               lunar eclipses of 2018-2026 against their published times (UT)
             test_eclipse_vp_modern_solar               solar eclipses at three places against the published new-moon times
         The published times are modern values (Swiss-Ephemeris-class).  The Vakya tables are not that accurate, so the tests
         compare dates strictly and times with a stated tolerance (OFFSET_TOL_HOURS), and print every signed offset.

run_eclipse_vp_book_tests()  runs PART 1;  run_eclipse_vp_reference_tests() runs PART 2;  run_eclipse_vp_tests() runs both.
"""
import math
from jhora import const
from jhora.panchanga import vakya_panchanga as vp
try:                                                   # inside PyJHora
    from jhora.panchanga import eclipse_vp as ev
except ImportError:                                    # stand-alone: eclipse_vp.py next to this file
    import eclipse_vp as ev
from test_book_vakya import _Tally, _book_deg, _wrap, _OK, _BAD

OFFSET_TOL_HOURS = 2.0      # Vakya time vs modern time; every reference eclipse is printed with its signed offset


# ---------------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------------
def _nv(nadis, vinadis=0.0):
    """ 'n nadis v vinadis' as nadis. """
    return nadis + vinadis / 60.0


_VIN = 1.0 / 60.0           # one vinadi in nadis


def _jd(y, m, d, h=0.0):
    """ Julian day (Gregorian calendar) of year, month, day, hour -- no dependency on utils. """
    if m <= 2:
        y, m = y - 1, m + 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5 + h / 24.0


def _jd_of_tuple(t):
    """ (Y, M, D, fractional hours) as returned by next_lunar_eclipse() / next_solar_eclipse() -> Julian day. """
    return _jd(t[0], t[1], t[2], t[3])


def _banner(tag, title, refs):
    print("=" * 78)
    print(f"VP ECLIPSE {tag}: {title}")
    print(f"             ({refs})")
    print("=" * 78)


class _ETally(_Tally):
    """ _Tally plus 'information' lines (printed, never counted) and comparisons with a non-book reference. """
    def __init__(self, reference="the book"):
        super().__init__()
        self._reference = reference

    def result(self):
        print(f"  -> {self.passed}/{self.total} checks pass ({self._reference})\n")
        return self.passed, self.total

    def info(self, label, text):
        print(f"  {label:<46s} {text}   [INFO]")

    def against(self, label, computed, reference, tol, refname, unit=""):
        diff = computed - reference
        ok = abs(diff) <= tol + 1e-9
        self._record(ok)
        print(f"  {label:<46s} computed={computed:>12.4f}  {refname}={reference:>12.4f}  diff={diff:+8.3f} {unit}  [{_OK if ok else _BAD}]")

    def flag(self, label, ok, detail=""):
        self._record(ok)
        print(f"  {label:<46s} {detail}  [{_OK if ok else _BAD}]")


# ---------------------------------------------------------------------------------------------------------------
# PART 1 -- the book's examples
# ---------------------------------------------------------------------------------------------------------------
def test_book_ecl_sine_bhuja_koti_ex17_18():
    """ Ex. 17a (p. 268): the Sine of 1r 5 deg = 35 deg is 11 + 10.5 + 5 x 9/15 = 24.5.  The largest Sine is 43 (the sum of the
        six segments; III.6 and III.22 divide by it).  Ex. 18: 10r 7d 30' lies in the 4th quadrant, so 1r 7d 30' is the Koti and
        3r - that = 1r 22d 30' is the Bhuja.  (Ex. 17b, the arc of a given Sine, has no function in eclipse_vp.py.) """
    _banner("TEST 1", "Sine, Bhuja, Koti", "Chapter III, verses 2b-6, Examples 17a and 18, pp. 267-268")
    t = _ETally()
    t.value("Sine of 35 deg (Ex. 17a)", ev.sine_of_arc(35.0), 24.5, 1e-9)
    t.value("Sine of 90 deg (the maximum)", ev.sine_of_arc(90.0), 43.0, 1e-9)
    bhuja, koti = ev.bhuja_koti(_book_deg(10, 7, 30))
    t.angle("Bhuja of 10r 7d 30' (Ex. 18)", bhuja, _book_deg(1, 22, 30), tol_arcsec=0.01)
    t.angle("Koti of 10r 7d 30' (Ex. 18)", koti, _book_deg(1, 7, 30), tol_arcsec=0.01)
    return t.result()


def test_book_ecl_conjunction_ex32():
    """ Ex. 32 (p. 277): at sunrise the Moon is 5r 11d 50' (motion 776') and Saturn 5r 1d 0' (motion 4', retrograde).
        t = (A - B)/(b - a) = (5r 11d 50' - 5r 1d 0') / (-4' - 776') = -5/6 day = -50 nadis: the conjunction took place 50 nadis
        before the given time, at longitude 5r 1d 3'.3 (from either body). """
    _banner("TEST 2", "Time of conjunction", "Chapter IV, verses 1-5a, Example 32, p. 277")
    t = _ETally()
    A, a = _book_deg(5, 11, 50) * 60.0, 776.0
    B, b = _book_deg(5, 1, 0) * 60.0, -4.0
    days = ev.conjunction_time_days(A, a, B, b)
    t.value("Time of conjunction (nadis)", days * 60.0, -50.0, 1e-6, "nadi")
    t.value("Longitude above 5r 1d from the Moon (')", A + a * days - B, 3.3, 0.05, "'")
    t.value("Longitude above 5r 1d from Saturn (')", B + b * days - B, 3.3, 0.05, "'")
    t.flag("Conjunction has gone (t < 0)", days < 0.0, f"t = {days:+.4f} day")
    return t.result()


def test_book_ecl_parva_end_ex33():
    """ Ex. 33 (p. 278): the Sun at sunrise is 70 deg (daily motion 58'), the Moon 65 deg (daily motion 778'); Amavasya ends 25 nadis
        after sunrise.  Adding 25' and, the motion being 2' under 60', deducting 25 x 2 seconds: the Sun (= the Moon) is 70d 24' 10". """
    _banner("TEST 3", "Longitude at the end of the Parva", "Chapter IV, verses 5b-7a, Example 33, p. 278")
    t = _ETally()
    sun = ev.parva_end_longitude(70.0 * 60.0, 58.0, 25.0) / 60.0
    moon = ev.parva_end_longitude(65.0 * 60.0, 778.0, 25.0) / 60.0
    t.angle("Sun at the end of Amavasya", sun, _book_deg(0, 70, 24, 10), tol_arcsec=0.5)
    t.angle("Moon at the end of Amavasya (= Sun)", moon, sun, tol_arcsec=0.5)
    return t.result()


def test_book_ecl_diameters_latitude_ex34_35():
    """ Ex. 34 (p. 278): from the data of Ex. 33 the Sun's diameter is 58' x 5/9 = 32'.2 and the Moon's 778'/25 = 31'.1.
        Ex. 35: with Rahu at 72d 24'.2, Moon - Rahu = 11r 28d, its Bhuja is 2d, Sine 2 x 11/15, Latitude 6 x Sine + 1/21 of it
        = 9'.2, positive (South) because Moon - Rahu is between 6r and 12r. """
    _banner("TEST 4", "Angular diameters and the Moon's latitude", "Chapter IV, verses 7b-9, Examples 34 and 35, pp. 278-279")
    t = _ETally()
    sun_d, moon_d, _ = ev.angular_diameters(58.0, 778.0)
    t.value("Angular diameter of the Sun (')", sun_d, 32.2, 0.06, "'")
    t.value("Angular diameter of the Moon (')", moon_d, 31.1, 0.06, "'")
    moon_end = ev.parva_end_longitude(65.0 * 60.0, 778.0, 25.0) / 60.0
    moon_minus_rahu = (moon_end - _book_deg(0, 72, 24) - 0.2 / 60.0) % 360.0
    # the book gives Rahu to 0.1' (6") and Moon - Rahu as exactly 11r 28d, so 6" is allowed
    t.angle("Moon - Rahu (11r 28d)", moon_minus_rahu, _book_deg(11, 28), tol_arcsec=6.0)
    t.angle("Bhuja of Moon - Rahu (2d)", ev.bhuja_koti(moon_minus_rahu)[0], 2.0, tol_arcsec=6.0)
    lat = ev.moon_latitude_min(_book_deg(11, 28))
    t.value("Latitude of the Moon (')", lat, 9.2, 0.06, "'")
    t.flag("Latitude is South (positive)", lat > 0.0, f"{lat:+.3f}'")
    return t.result()


def test_book_ecl_lunar_ex36_37():
    """ Ex. 36 (pp. 278-279): at sunrise 15 nadis of Pratipad are gone; Sun 8r 2d (motion 61'), Moon 2r 5d 15' (motion 841'), Rahu 1r 28d
        at the end of Purnima.  Ex. 37 (pp. 279-281): the circumstances.  The Middle is the end of the Parva, 45 nadis of the previous day.
        Book: Sun 8r 1d 44'.8, Moon 2r 1d 44'.8; Moon's diameter 33'.64, shadow 85'.1; latitude 17'.3 North; magnitude 42'.1
        (greater than 33'.6 so a total phase); half-duration 4-22.2 nadis, half of the total phase 1-27.7; approximate First Contact
        40-37.8, Last 49-22.2, Immersion 43-32.3, Emergence 46-27.7; correction 7.2 vinadis (odd quadrant: deduct); corrected
        First Contact 40-31, Last Contact 49-15, Immersion 43-25, Emergence 46-21. """
    _banner("TEST 5", "Lunar eclipse", "Chapter IV, verses 10-15, Examples 36 and 37, pp. 278-281")
    t = _ETally()
    moon_end = ev.parva_end_longitude(_book_deg(2, 5, 15) * 60.0, 841.0, -15.0) / 60.0
    sun_end = ev.parva_end_longitude(_book_deg(8, 2) * 60.0, 61.0, -15.0) / 60.0
    t.angle("Moon at the end of Purnima (Ex. 36 i)", moon_end, _book_deg(2, 1, 44) + 0.8 / 60.0, tol_arcsec=6.0)
    t.angle("Sun at the end of Purnima (Ex. 36 i)", sun_end, _book_deg(8, 1, 44) + 0.8 / 60.0, tol_arcsec=6.0)
    t.angle("Moon + 6 rasis = Sun", (moon_end + 180.0) % 360.0, sun_end, tol_arcsec=0.5)
    moon_minus_rahu = moon_end - _book_deg(1, 28)
    t.angle("Moon - Rahu (3d 44'.8)", moon_minus_rahu, _book_deg(0, 3, 44) + 0.8 / 60.0, tol_arcsec=6.0)
    el = ev.lunar_eclipse_elements(moon_minus_rahu, 841.0, 61.0, 45.0)
    t.flag("An eclipse occurs", el is not None)
    if el is None:
        return t.result()
    t.value("Moon's diameter (')", el["diameters"][1], 33.64, 0.006, "'")
    t.value("Shadow's diameter (')", el["diameters"][2], 85.1, 0.06, "'")
    t.value("Latitude of the Moon (', North negative)", el["latitude_min"], -17.3, 0.06, "'")
    t.value("Magnitude (')", el["magnitude_min"], 42.1, 0.06, "'")
    t.flag("Total phase (42.1 > 33.6)", bool(el["total"]))
    t.value("Half-duration (nadis)", el["half_duration"], _nv(4, 22.2), 0.5 * _VIN, "nadi")
    t.value("Half-duration of the total phase (nadis)", el["half_total"], _nv(1, 27.7), 0.5 * _VIN, "nadi")
    t.value("First Contact, approximate (nadis)", el["first_contact_uncorrected"], _nv(40, 37.8), 0.5 * _VIN, "nadi")
    t.value("Last Contact, approximate (nadis)", el["last_contact_uncorrected"], _nv(49, 22.2), 0.5 * _VIN, "nadi")
    t.value("Immersion, approximate (nadis)", el["immersion_uncorrected"], _nv(43, 32.3), 0.5 * _VIN, "nadi")
    t.value("Emergence, approximate (nadis)", el["emergence_uncorrected"], _nv(46, 27.7), 0.5 * _VIN, "nadi")
    t.value("Correction (vinadis)", el["correction_vinadis"], 7.2, 0.06, "vinadi")
    # the book prints the corrected times to the whole vinadi
    t.value("First Contact (nadis)", el["first_contact"], _nv(40, 31), _VIN, "nadi")
    t.value("Last Contact (nadis)", el["last_contact"], _nv(49, 15), _VIN, "nadi")
    t.value("Immersion (nadis)", el["immersion"], _nv(43, 25), _VIN, "nadi")
    t.value("Emergence (nadis)", el["emergence"], _nv(46, 21), _VIN, "nadi")
    return t.result()


def test_book_ecl_parallax_table_ex38():
    """ IV.20-20a with Ex. 38 (pp. 282-284): the Parallax in vinadis from the difference between Nonagesimal and Sun, by the table
        39, 78, 115, 144, 172, 192, 208, ... at 6, 12, 18 ... degrees.  Book: 26d 51'.4 gives 144 + 28 x 2d51'.4/6 = 157; 12d 11' gives
        79; 40d 29' gives 203 (the book writes 192 + 16 x 4d20'/6, using 4d20' where 40d29' - 36d is 4d29', so the exact rule gives
        204 and a vinadi is allowed). """
    _banner("TEST 6", "Parallax table", "Chapter IV, verses 20-20a, Example 38, pp. 282-284")
    t = _ETally()
    t.value("Parallax for 26d 51'.4 (vinadis)", ev.parallax_vinadis(_book_deg(0, 26, 51) + 0.4 / 60.0), 157.0, 0.5, "vinadi")
    t.value("Parallax for 12d 11' (vinadis)", ev.parallax_vinadis(_book_deg(0, 12, 11)), 79.0, 0.5, "vinadi")
    t.value("Parallax for 40d 29' (vinadis)", ev.parallax_vinadis(_book_deg(0, 40, 29)), 203.0, 1.0, "vinadi")
    t.value("Parallax at 90d, the table's end (vinadis)", ev.parallax_vinadis(90.0), 240.0, 1e-9, "vinadi")
    t.value("Nati multiplier for 12'", ev.nati_multiplier(12.0), 2.0, 1e-9)
    t.value("Nati multiplier for 24'", ev.nati_multiplier(24.0), 8.0, 1e-9)
    t.value("Nati multiplier for 36'", ev.nati_multiplier(36.0), 18.0, 1e-9)
    t.value("Nati correction for 5' of Nati and 157 vinadis", 157.0 / 60.0 * ev.nati_multiplier(5.0), 2.0, 0.5, "vinadi")
    return t.result()


def _solar_ex38(lagna_sun):
    """ The data of Ex. 38 (p. 282) run through solar_eclipse_elements().  @return: elements dict """
    return ev.solar_eclipse_elements(
        sun_sunrise_deg=_book_deg(10, 6, 41) + 0.8 / 60.0, sun_daily_min=60.6,
        moon_sunrise_deg=_book_deg(10, 2, 46) + 0.5 / 60.0, moon_daily_min=845.0,
        rahu_deg=_book_deg(10, 5), ayanamsa_deg=23.0, eq_shadow=2.2, lagna_sun=lagna_sun)


def test_book_ecl_solar_ex38():
    """ Ex. 38 (pp. 282-284): solar eclipse at Pudukkottai (equinoctial shadow 2.2).  Sun at sunrise 10r 6d 41'.8, Moon 10r 2d 46'.5, Rahu
        10r 5d, motions 60'.6 and 845', Ayanamsa 23d.  Book results, in the order of the example:
          I   end of Parva 18 nadis; Sun = Moon 10r 7d; diameters 33'.7 and 33'.8
          II  (i)   Sayana Lagna at the Parva 2r 26d 51'.4; Nonagesimal 11r 26d 51'.4; difference from the Sun 26d 51'.4; Parallax 157
                    vinadis; PCP 20-37
              (ii)  Sun at PCP 11r 0d 2'.6; Lagna 3r 11d 19'; Nonagesimal 0r 11d 19'; Sine of its Bhuja 8.3; Ayana correction -3'.8;
                    place correction +8'.8
              (iii) Nati +5'; Moon - Rahu 2d 37'; Moon's Latitude -12'; PCL -7'
              (iv)  corrected Parallax 155 vinadis; Middle 20-35; Magnitude 26'.7; no total phase
              (v)   half-duration 2-31.5; First / Last Contact not corrected for Parallax 15-28.5 / 20-31.5; at First Contact the
                    Lagna is 2r 12d 11', Parallax 79 less 2 = 77, First Contact 16-43; at Last Contact the Lagna is 3r 10d 35', the
                    difference 1r 10d 29', Last Contact 23-50.
        The book's Lagna (2r 26d 51'.4) is 6' below what the Sun-at-sunrise Lagna gives, and the quantities that follow from it are
        widened accordingly (stated per line).  The Lagna built from the Sun at the given time is 21-27' off (see the next test). """
    _banner("TEST 7", "Solar eclipse at Pudukkottai", "Chapter IV, verses 16-24, Example 38, pp. 282-284")
    t = _ETally()
    s = _solar_ex38("sunrise")
    t.flag("Eclipse visible at the place", bool(s.get("visible")))
    if not s.get("visible"):
        return t.result()
    h0, h1 = s["detail"]["at_parva"], s["detail"]["at_pcp"]
    print("  -- I. the elements --")
    t.value("End of the Parva (nadis)", s["parva"], 18.0, 0.5 * _VIN, "nadi")
    t.angle("Sun = Moon at the end of the Parva", (h0["sun"] - 23.0) % 360.0, _book_deg(10, 7), tol_arcsec=120.0)   # book: 10r 7d (whole degrees)
    t.angle("Sayana Sun at the end of the Parva", h0["sun"], _book_deg(11), tol_arcsec=120.0)
    t.value("Sun's diameter (')", s["diameters"][0], 33.7, 0.06, "'")
    t.value("Moon's diameter (')", s["diameters"][1], 33.8, 0.06, "'")
    print("  -- II (i). Lagna, Nonagesimal, Parallax at the end of the Parva --")
    t.angle("Sayana Lagna at the Parva", h0["lagna"], _book_deg(2, 26, 51) + 0.4 / 60.0, tol_arcsec=600.0)   # 10'
    t.angle("Nonagesimal (Lagna - 3r)", h0["nonagesimal"], _book_deg(11, 26, 51) + 0.4 / 60.0, tol_arcsec=600.0)
    t.value("Nonagesimal - Sun (deg)", h0["diff"], _book_deg(0, 26, 51) + 0.4 / 60.0, 10.0 / 60.0, "deg")
    t.value("Parallax (vinadis)", s["parallax_vinadis"], 157.0, 1.0, "vinadi")
    t.flag("Sun less than Nonagesimal: add", bool(h0["add"]))
    t.value("PCP, the Parva corrected for Parallax (nadis)", s["pcp"], _nv(20, 37), _VIN, "nadi")
    print("  -- II (ii). at the PCP --")
    t.angle("Sun at the PCP (11r 0d 2'.6)", (h1["sun"]) % 360.0, _book_deg(11, 0, 2) + 0.6 / 60.0, tol_arcsec=30.0)
    t.angle("Sayana Lagna at the PCP", h1["lagna"], _book_deg(3, 11, 19), tol_arcsec=600.0)
    t.value("Sine of the Bhuja of the book's 11d 19' (rule)", ev.sine_of_arc(_book_deg(0, 11, 19)), 8.3, 0.06)
    t.value("Ayana correction (', negative)", s["ayana_correction_min"], -3.8, 0.1, "'")        # follows from the Lagna above
    t.value("Place correction (')", s["place_correction_min"], 8.8, 0.06, "'")
    print("  -- II (iii). Nati and the Parallax-corrected Latitude --")
    t.value("Nati (')", s["nati_min"], 5.0, 0.5, "'")                                         # book prints whole minutes
    t.value("Latitude of the book's Moon - Rahu 2d 37' (rule)", ev.moon_latitude_min(2.0 + 37.0 / 60.0), -12.0, 0.5, "'")
    t.value("Moon's latitude at the PCP (')", s["moon_latitude_min"], -12.0, 0.5, "'")
    t.value("PCL (')", s["pcl_min"], -7.0, 0.5, "'")
    print("  -- II (iv). Middle and magnitude --")
    t.value("Corrected Parallax (vinadis)", s["parallax_corrected_vinadis"], 155.0, 1.0, "vinadi")
    t.value("Middle of the eclipse (nadis)", s["middle"], _nv(20, 35), _VIN, "nadi")
    t.value("Magnitude (')", s["magnitude_min"], 26.7, 0.1, "'")                             # the book subtracts rounded 7' from 33.7
    t.flag("No total phase", not s["total"])
    print("  -- II (v). Contacts --")
    t.value("Half-duration (nadis)", s["half_duration"], _nv(2, 31.5), 0.5 * _VIN, "nadi")
    t.value("First Contact, not corrected (nadis)", s["first_contact_uncorrected"], _nv(15, 28.5), _VIN, "nadi")
    t.value("Last Contact, not corrected (nadis)", s["last_contact_uncorrected"], _nv(20, 31.5), _VIN, "nadi")
    d1, d2 = s["detail"]["first_contact"], s["detail"]["last_contact"]
    t.angle("Sayana Lagna at First Contact (2r 12d 11')", d1["lagna"], _book_deg(2, 12, 11), tol_arcsec=600.0)
    t.angle("Sayana Lagna at Last Contact (3r 10d 35')", d2["lagna"], _book_deg(3, 10, 35), tol_arcsec=600.0)
    t.value("Nonagesimal - Sun at Last Contact (deg)", d2["diff"], _book_deg(1, 10, 29), 10.0 / 60.0, "deg")
    t.value("First Contact (nadis)", s["first_contact"], _nv(16, 43), _VIN, "nadi")
    t.value("Last Contact (nadis)", s["last_contact"], _nv(23, 50), _VIN, "nadi")
    for k in ("first_contact", "middle", "last_contact"):
        t.info(f"{k} as the book writes it", ev.nadi_vinadi(s[k]))
    return t.result()


def test_book_ecl_solar_ex38_given_time():
    """ Ex. 38 again with lagna_sun='given_time': the Lagna is built from the Sun at the time asked for, as in Ex. 23-24.  eclipse_vp.py
        documents that this puts the Lagna 21-27' under the printed 2r 26d 51'.4 and the end results a few vinadis off, so these lines
        are printed for comparison and NOT counted.  The default, lagna_sun='sunrise', is what test_book_ecl_solar_ex38 checks. """
    _banner("TEST 8", "Solar eclipse at Pudukkottai, Lagna from the Sun at the given time", "same example; information only, not counted")
    t = _ETally()
    s = _solar_ex38("given_time")
    book = (("Sayana Lagna at the Parva (deg)", s["detail"]["at_parva"]["lagna"], _book_deg(2, 26, 51) + 0.4 / 60.0, "deg"),
            ("Sayana Lagna at the PCP (deg)", s["detail"]["at_pcp"]["lagna"], _book_deg(3, 11, 19), "deg"),
            ("Parallax (vinadis)", s["parallax_vinadis"], 157.0, "vinadi"),
            ("PCL (')", s["pcl_min"], -7.0, "'"),
            ("Magnitude (')", s["magnitude_min"], 26.7, "'"),
            ("First Contact (nadis)", s["first_contact"], _nv(16, 43), "nadi"),
            ("Middle (nadis)", s["middle"], _nv(20, 35), "nadi"),
            ("Last Contact (nadis)", s["last_contact"], _nv(23, 50), "nadi"))
    for label, got, book_val, unit in book:
        t.info(label, f"computed={got:10.4f}  book={book_val:10.4f}  diff={got - book_val:+8.4f} {unit}")
    print("  -> information only; 0 checks counted\n")
    return 0, 0


# ---------------------------------------------------------------------------------------------------------------
# PART 2 -- date level
# ---------------------------------------------------------------------------------------------------------------
_HOFFMAN = vp.Place("Hoffman Estates, IL", 42.0629, -88.1226, -5.0)
_CHENNAI = vp.Place("Chennai", 13.0827, 80.2707, 5.5)
_DELHI = vp.Place("Delhi", 28.6139, 77.2090, 5.5)


def test_eclipse_vp_api_consistency():
    """ The public functions next_lunar_eclipse(), next_solar_eclipse(), is_lunar_eclipse(), is_solar_eclipse() against each other.  There is
        no outside reference here: the checks are that what one returns, the others accept (shape, order of contacts, type filters,
        search direction, and is_*() at the instant next_*() reported). """
    _banner("TEST 9", "Public API consistency (next_/is_ functions)", "no book or modern reference; internal agreement only")
    t = _ETally("internal agreement")
    start = _jd(2026, 10, 10)                                   # local civil Julian day of the search start
    print("  -- lunar, from Hoffman Estates --")
    nl = ev.next_lunar_eclipse(start, _HOFFMAN)
    t.flag("next_lunar_eclipse returns a result", nl is not None)
    if nl is not None:
        kind, times = nl
        b, m, e = (_jd_of_tuple(x) for x in times)
        t.flag("type is 'total' or 'partial'", kind in ("total", "partial"), f"type={kind}")
        t.flag("three times: begin < middle < end", len(times) == 3 and b < m < e, f"length {(e - b) * 24:.2f} h")
        t.flag("the eclipse is after the start date", m > start)
        t.flag("hours of day are within 0..24", all(0.0 <= x[3] < 24.0 for x in times))
        d = ev.is_lunar_eclipse(m, _HOFFMAN)
        t.flag("is_lunar_eclipse at the middle: is_possible", bool(d["is_possible"]))
        t.flag("is_lunar_eclipse type agrees with next_", bool(d["is_total"]) == (kind == "total"), f"is_total={d['is_total']}")
        t.flag("is_lunar_eclipse keys", set(d) == {"sun_diameter", "moon_diameter", "shadow_diameter", "moon_latitude", "grasa",
                                                  "is_possible", "is_total", "half_duration_days"})
        t.flag("half-duration agrees with the contacts", d["half_duration_days"] is not None and
               abs(d["half_duration_days"] * 2.0 - (e - b)) < 0.02, f"{d['half_duration_days'] * 48.0:.2f} h vs {(e - b) * 24:.2f} h")
        pl = ev.next_lunar_eclipse(start, _HOFFMAN, search_backward=True)
        t.flag("backward search finds an earlier eclipse", pl is not None and _jd_of_tuple(pl[1][1]) < start)
    for label, flt, want in (("TOTAL", ev.LunarEclipseType.TOTAL, "total"), ("PARTIAL", ev.LunarEclipseType.PARTIAL, "partial")):
        r = ev.next_lunar_eclipse(start, _HOFFMAN, lunar_eclipse_type=flt)
        t.flag(f"filter {label} returns only '{want}'", r is not None and r[0] == want, f"type={r[0] if r else None}")
    print("  -- solar, from Chennai --")
    ns = ev.next_solar_eclipse(start, _CHENNAI)
    t.flag("next_solar_eclipse returns a result", ns is not None)
    if ns is not None:
        kind, times = ns
        b, m, e = (_jd_of_tuple(x) for x in times)
        t.flag("type is 'total' or 'partial'", kind in ("total", "partial"), f"type={kind}")
        t.flag("three times: begin < middle < end", b < m < e, f"length {(e - b) * 24:.2f} h")
        t.flag("real first and last contacts (not begin = end = middle)", (e - b) * 24.0 > 0.2)
        t.flag("the eclipse is after the start date", m > start)
        tz = _CHENNAI.timezone
        nm = [x for x in ev.parva_events(m - 3.0 - tz / 24.0, m + 3.0 - tz / 24.0) if x["kind"] == "amavasya"]
        t.flag("an Amavasya lies within 3 days of the middle", len(nm) >= 1)
        if nm:
            d = ev.is_solar_eclipse(nm[0]["jd_utc"] + tz / 24.0, _CHENNAI)
            t.flag("is_solar_eclipse at that new moon: is_possible", bool(d["is_possible"]))
            t.flag("is_solar_eclipse type agrees with next_", bool(d["is_total"]) == (kind == "total"), f"is_total={d['is_total']}")
            t.flag("is_solar_eclipse keys", set(d) == {"sun_diameter", "moon_diameter", "moon_latitude", "grasa", "is_possible",
                                                      "is_total", "jd_apparent_conjunction"})
            t.flag("jd_apparent_conjunction = the middle reported", abs(d["jd_apparent_conjunction"] - m) < 1e-6)
    r = ev.next_solar_eclipse(start, _CHENNAI, solar_eclipse_type=ev.SolarEclipseType.TOTAL, max_tries=60)
    t.flag("filter TOTAL returns None or a 'total' eclipse", r is None or r[0] == "total", f"{'None' if r is None else r[0]}")
    return t.result()


# greatest-eclipse times, UT, of the umbral lunar eclipses 2018-2026 (published: NASA / USNO tables); kind as published
_MODERN_LUNAR = (
    ("2018-01-31", (2018, 1, 31, 13, 30), "total"), ("2018-07-27", (2018, 7, 27, 20, 22), "total"),
    ("2019-01-21", (2019, 1, 21, 5, 12), "total"), ("2019-07-16", (2019, 7, 16, 21, 31), "partial"),
    ("2021-05-26", (2021, 5, 26, 11, 19), "total"), ("2021-11-19", (2021, 11, 19, 9, 3), "partial"),
    ("2022-05-16", (2022, 5, 16, 4, 11), "total"), ("2022-11-08", (2022, 11, 8, 11, 0), "total"),
    ("2023-10-28", (2023, 10, 28, 20, 14), "partial"), ("2024-09-18", (2024, 9, 18, 2, 44), "partial"),
    ("2025-03-14", (2025, 3, 14, 6, 59), "total"), ("2025-09-07", (2025, 9, 7, 18, 12), "total"),
    ("2026-03-03", (2026, 3, 3, 11, 34), "total"), ("2026-08-28", (2026, 8, 28, 4, 13), "partial"),
)
# penumbral-only eclipses: the book has no penumbral case, so the engine can only report them as small partial eclipses or not at all
_MODERN_PENUMBRAL = (("2020-11-30", (2020, 11, 30, 9, 43)), ("2024-03-25", (2024, 3, 25, 7, 12)))


def test_eclipse_vp_modern_lunar():
    """ eclipse_vp.lunar_eclipses() against the published lunar eclipses of 2018-2026 (14 umbral eclipses).  For each: is it found within
        a day (counted); is the middle within OFFSET_TOL_HOURS of the published greatest eclipse (counted); the type is printed, not
        counted (the book's diameters decide 'total', and a 97 % partial can come out total).  Two penumbral-only eclipses are listed
        for information. """
    _banner("TEST 10", "Lunar eclipses 2018-2026 against modern times (UT)", f"published values; tolerance +/-{OFFSET_TOL_HOURS} h")
    t = _ETally("modern reference")
    offsets = []
    for label, ut, kind in _MODERN_LUNAR:
        ref = _jd(*ut[:3], ut[3] + ut[4] / 60.0)
        found = [r for r in ev.lunar_eclipses(ref - 1.0, ref + 1.0)]
        t.flag(f"{label} {kind:7s} found", len(found) >= 1)
        if not found:
            continue
        r = found[0]
        off = (r["jd_utc"] - ref) * 24.0
        offsets.append(off)
        t.against(f"{label} middle offset (h)", off, 0.0, OFFSET_TOL_HOURS, "modern", "h")
        same = (("total" if r["total"] else "partial") == kind)
        t.info(f"{label} type", f"vakya={'total' if r['total'] else 'partial'}  published={kind}  magnitude {r['magnitude_min']:.1f}'"
               + ("" if same else "   <- differs"))
    if offsets:
        t.info("offsets (Vakya - modern), mean / min / max",
               f"{sum(offsets) / len(offsets):+.2f} / {min(offsets):+.2f} / {max(offsets):+.2f} h  (a steady lag, not scatter)")
    for label, ut in _MODERN_PENUMBRAL:
        ref = _jd(*ut[:3], ut[3] + ut[4] / 60.0)
        found = ev.lunar_eclipses(ref - 1.0, ref + 1.0)
        t.info(f"{label} penumbral-only",
               f"vakya reports {'partial, magnitude %.1f' % found[0]['magnitude_min'] + chr(39) if found else 'no eclipse'}")
    return t.result()


# (label, place, published new moon UT) -- the solar eclipse is visible at the place on that date
_MODERN_SOLAR = (
    ("2017-08-21 Hoffman Estates", _HOFFMAN, (2017, 8, 21, 18, 30)),
    ("2024-04-08 Hoffman Estates", _HOFFMAN, (2024, 4, 8, 18, 21)),
    ("2019-12-26 Chennai", _CHENNAI, (2019, 12, 26, 5, 13)),
    ("2020-06-21 Delhi", _DELHI, (2020, 6, 21, 6, 41)),
    ("2022-10-25 Delhi (near sunset)", _DELHI, (2022, 10, 25, 10, 49)),
)


def test_eclipse_vp_modern_solar():
    """ eclipse_vp.solar_eclipses() at three places against published solar eclipses visible there.  Counted: the eclipse is found at the
        place within a day, and the Amavasya (Parva) is within OFFSET_TOL_HOURS of the published new moon.  The contact times are not
        compared: they add the book's parallax rule (built for latitudes of India) and local circumstances not tabulated here.
        2022-10-25 at Delhi is a sunset eclipse; if the Vakya Parva falls after sunset the eclipse is lost, and the line shows that. """
    _banner("TEST 11", "Solar eclipses at three places against modern new moon (UT)", f"published values; tolerance +/-{OFFSET_TOL_HOURS} h")
    t = _ETally("modern reference")
    offsets = []
    for label, place, ut in _MODERN_SOLAR:
        ref = _jd(*ut[:3], ut[3] + ut[4] / 60.0)
        lo, hi = ref - 1.0, ref + 1.0
        parva = [e for e in ev.parva_events(lo, hi) if e["kind"] == "amavasya"]
        if parva:
            off = (parva[0]["jd_utc"] - ref) * 24.0
            offsets.append(off)
            t.against(f"{label}: Parva offset (h)", off, 0.0, OFFSET_TOL_HOURS, "modern", "h")
        else:
            t.flag(f"{label}: Amavasya found", False)
        found = ev.solar_eclipses(lo, hi, place)
        if found:
            r = found[0]
            t.flag(f"{label}: found", True, f"magnitude {r['magnitude_min']:.1f}'  middle {ev.nadi_vinadi(r['elements']['middle'])} after sunrise")
        else:
            why = "no Amavasya"
            if parva:
                lat = ev.moon_latitude_min(parva[0]["moon_minus_rahu"])
                jd_loc = parva[0]["jd_utc"] + place.timezone / 24.0
                sunset = vp._sunset_jd(jd_loc, place)
                after = (jd_loc - sunset) * 24.0
                why = (f"Moon's latitude {lat:+.1f}'; Parva at {((jd_loc + 0.5) % 1.0) * 24.0:05.2f} local, "
                       f"{'%.2f h after' % after if after > 0 else '%.2f h before' % -after} sunset")
            t.flag(f"{label}: found", False, f"not found ({why})")
    if offsets:
        t.info("Parva offsets (Vakya - modern), mean / min / max",
               f"{sum(offsets) / len(offsets):+.2f} / {min(offsets):+.2f} / {max(offsets):+.2f} h")
    return t.result()


# ---------------------------------------------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------------------------------------------
ECLIPSE_VP_BOOK_TESTS = (
    test_book_ecl_sine_bhuja_koti_ex17_18,
    test_book_ecl_conjunction_ex32,
    test_book_ecl_parva_end_ex33,
    test_book_ecl_diameters_latitude_ex34_35,
    test_book_ecl_lunar_ex36_37,
    test_book_ecl_parallax_table_ex38,
    test_book_ecl_solar_ex38,
    test_book_ecl_solar_ex38_given_time,
)
ECLIPSE_VP_REFERENCE_TESTS = (
    test_eclipse_vp_api_consistency,
    test_eclipse_vp_modern_lunar,
    test_eclipse_vp_modern_solar,
)


def _run(tests, title):
    passed = total = 0
    raised = []
    for fn in tests:
        try:
            p, n = fn()
        except Exception as exc:                          # one broken test must not hide the others
            print(f"  !! {fn.__name__} raised {type(exc).__name__}: {exc}\n")
            raised.append(fn.__name__)
            p, n = 0, 1
        passed += p
        total += n
    print("=" * 78)
    print(f"{title}: {passed}/{total} checks match across {len(tests)} tests" + (f";  RAISED: {', '.join(raised)}" if raised else ""))
    print("=" * 78)
    return passed, total


def run_eclipse_vp_book_tests():
    """ PART 1: the book's eclipse examples (Ex. 17a, 18, 32-38).  @return: (checks passed, checks total) """
    return _run(ECLIPSE_VP_BOOK_TESTS, "VP ECLIPSE BOOK EXAMPLES")


def run_eclipse_vp_reference_tests():
    """ PART 2: public-API consistency and comparison with modern eclipse times.  @return: (checks passed, checks total) """
    return _run(ECLIPSE_VP_REFERENCE_TESTS, "VP ECLIPSE DATE-LEVEL TESTS")


def run_eclipse_vp_tests():
    """ Both parts.  @return: (checks passed, checks total) """
    p1, n1 = run_eclipse_vp_book_tests()
    p2, n2 = run_eclipse_vp_reference_tests()
    return p1 + p2, n1 + n2


if __name__ == "__main__":
    run_eclipse_vp_tests()
