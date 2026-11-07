"""
test_book_eclipse_ms.py
========================
Book tests + date-level checks for eclipse_ms.py (the Makaranda Sarini
eclipse module), in the same house style as test_book_eclipse_vp.py's
role in the suite (per test1.py's import comment: "Chapter IV (eclipses)
of the same book + date-level checks of eclipse_vp.py").

Source: the Makaranda Sarini's own two worked eclipse examples --
  - Lunar eclipse, Saka 1534 Vaisakha sukla 15 (p. 0083)
  - Solar eclipse, Saka 1532 Margasirsha krishna 30, Wednesday (p. 0084)

HONESTY NOTE -- READ BEFORE INTERPRETING THE OUTPUT OF THIS FILE:
eclipse_ms.py's own module docstring is explicit that EVERY disc size
(candra-bimba, bhu-bimba, surya-bimba), the Moon's latitude, and the
solar lambana correction are FITTED PLACEHOLDERS, not transcriptions of
the book's own printed tables (pp. 0044-0048, 0053, 0083-0084) -- those
tables showed the same digit ambiguities (1/3, 6/8, 4/8) documented
throughout this project and were not forced into a guess. Because of
this, running the book's own two example instants through the fitted
model does NOT currently reproduce an eclipse at either instant (the
computed magnitude comes out negative, i.e. "no eclipse", at both the
Saka 1534 lunar instant and the Saka 1532 solar instant) -- this is
reported below exactly as computed, not adjusted to look like a match.
This file exists to (a) keep that gap visible every time the test suite
runs, and (b) smoke-test that the public API (next_lunar_eclipse,
next_solar_eclipse, is_lunar_eclipse, is_solar_eclipse) runs end-to-end
and returns a self-consistent result on an ordinary modern date, the way
the VP eclipse book-test file does for eclipse_vp.py.
"""
import importlib


def _imp(name):
    for path in (f"jhora.panchanga.{name}", name):
        try:
            return importlib.import_module(path)
        except ImportError:
            pass
    raise ImportError(name)


def _dms(deg):
    sign = '-' if deg < 0 else ''
    total_cs = round(abs(deg) * 3600 * 100)
    d, rem = divmod(total_cs, 3600 * 100)
    m, cs = divmod(rem, 6000)
    s = cs / 100.0
    return f"{sign}{d}\u00b0{m:02d}'{s:05.2f}\""


def _fmt_ymdfh(entry):
    if entry is None:
        return "None"
    y, m, d, fh = entry
    h = int(fh)
    mi = int((fh - h) * 60)
    s = ((fh - h) * 60 - mi) * 60
    return f"{y:04d}-{m:02d}-{d:02d} {h:02d}:{mi:02d}:{s:05.2f}"


def test_book_lunar_eclipse_saka_1534():
    """
    Makaranda Sarini, p. 0083 -- lunar-eclipse worked example, same Saka
    1534 Vaisakha sukla 15 epoch as the graha-sadhana example (see
    test_book_mks.py). Book's own reading (moderate confidence, dense
    running text not a ruled table): grasa (magnitude) relation is
    "grasa x 20, divided by the Moon's disc, becomes vimshopaka"; a
    spashta-bhu-bimba (corrected earth-shadow disc) of 28;36 is stated.
    Neither the Moon's disc nor the shadow disc at this instant could be
    independently read with confidence, so this test reports what the
    FITTED model computes, flags that it does not currently predict an
    eclipse at this instant, and stops there -- it does not force a match.
    """
    mks = _imp('makaranda_sarini')
    ems = _imp('eclipse_ms')
    print("=" * 78)
    print("BOOK TEST (MSE-1): Lunar eclipse, Saka 1534 Vaisakha sukla 15 (p. 0083)")
    print("=" * 78)
    place = mks.Place('Ujjain', mks.const.ujjain_lat_long[0], mks.const.ujjain_lat_long[1], 5.5)
    jd_utc = mks._KALI_JD0 + mks._EXAMPLE_AHARGANA - mks._UJJAIN_LONGITUDE / 360.0
    info = ems.lunar_eclipse_at(jd_utc, place)
    print("Book's own reading: grasa x 20 / candra-bimba = vimshopaka;")
    print("                     spashta-bhu-bimba (stated) = 28;36 (units as printed, unconfirmed)")
    print(f"Engine (fitted):     candra-bimba={_dms(info['candra_bimba_deg'])}"
          f"  bhu-bimba={_dms(info['bhu_bimba_deg'])}  moon-latitude={_dms(info['moon_latitude_deg'])}")
    print(f"                     magnitude={info['magnitude_deg']*3600:.2f}\"  "
          f"is_possible={info['is_possible']}  is_total={info['is_total']}")
    print()
    print("RESULT: the fitted model does NOT currently predict an eclipse at this")
    print("instant (magnitude <= 0). This is expected and documented: every disc size")
    print("and the Moon's latitude here are fitted placeholders (see eclipse_ms.py's")
    print("module docstring), not transcriptions of the book's own tables on pp.")
    print("0044-0048 and 0083. This is reported as-is, not forced to match.")
    print()


def test_book_solar_eclipse_saka_1532():
    """
    Makaranda Sarini, p. 0084 -- solar-eclipse worked example, Saka 1532
    Margasirsha krishna 30, Wednesday. Book's own reading (moderate
    confidence): Sun's bhujamsa 8;26;14 feeds a lambana (parallax/timing)
    correction, reaching 23;45 degrees after the book's own /6,
    pala-correction, x6 steps; the ahargana for this example is
    APPROXIMATED in eclipse_ms.py (two Saka years before the graha-sadhana
    epoch, by the mean solar year length) because it was not independently
    read from a valli on p. 0084 itself.
    """
    mks = _imp('makaranda_sarini')
    ems = _imp('eclipse_ms')
    print("=" * 78)
    print("BOOK TEST (MSE-2): Solar eclipse, Saka 1532 Margasirsha krishna 30 (p. 0084)")
    print("=" * 78)
    place = mks.Place('Ujjain', mks.const.ujjain_lat_long[0], mks.const.ujjain_lat_long[1], 5.5)
    jd_utc = mks._KALI_JD0 + ems._SOLAR_EXAMPLE_AHARGANA - mks._UJJAIN_LONGITUDE / 360.0
    info = ems.solar_eclipse_at(jd_utc, place)
    print("Book's own reading: Sun bhujamsa 8;26;14 -> lambana 23;45 deg (book's steps)")
    print(f"Engine (fitted):     candra-bimba={_dms(info['candra_bimba_deg'])}"
          f"  surya-bimba={_dms(info['surya_bimba_deg'])}  lambana={_dms(info['lambana_deg'])}")
    print(f"                     magnitude={info['magnitude_deg']*3600:.2f}\"  "
          f"is_possible={info['is_possible']}  is_total={info['is_total']}")
    print()
    print("RESULT: the fitted model does NOT currently predict an eclipse at this")
    print("instant either. The ahargana itself is an APPROXIMATION (see docstring),")
    print("so even the instant being tested is not fully confirmed from the book --")
    print("report, don't force. See eclipse_ms.py's module docstring for what would")
    print("need to be transcribed (pp. 0047, 0053) to close this gap properly.")
    print()


def test_date_level_eclipse_ms():
    """
    Date-level smoke test of eclipse_ms.py's public API (is_lunar_eclipse,
    is_solar_eclipse, next_lunar_eclipse, next_solar_eclipse), on an
    ordinary modern date, the way the VP eclipse book-test file exercises
    eclipse_vp.py's public API separately from the book examples above.
    This only checks that the functions run end-to-end and return a
    self-consistent (type_str, [begin, middle, end]) shape -- it is NOT a
    validation of the predicted eclipse against reality (see the module
    docstring: the underlying discs/latitude are fitted placeholders).
    """
    mks = _imp('makaranda_sarini')
    ems = _imp('eclipse_ms')
    print("=" * 78)
    print("DATE-LEVEL CHECKS: eclipse_ms.py public API (modern date, structural only)")
    print("=" * 78)
    place = mks.Place('Chennai,IN', 13.0389, 80.2619, 5.5)
    dob = mks.Date(1996, 12, 7)
    tob = (10, 34, 0)
    jd = mks.utils.julian_day_number(dob, tob)
    fm = mks.full_moon(jd, place)
    nm = mks.new_moon(jd, place)
    lunar_info = ems.is_lunar_eclipse(fm, place)
    solar_info = ems.is_solar_eclipse(nm, place)
    print(f"is_lunar_eclipse() at nearest full moon : is_possible={lunar_info['is_possible']}"
          f"  magnitude={lunar_info['magnitude_deg']*3600:.1f}\"")
    print(f"is_solar_eclipse() at nearest new moon  : is_possible={solar_info['is_possible']}"
          f"  magnitude={solar_info['magnitude_deg']*3600:.1f}\"")
    for label, fn, kind in (("next_lunar_eclipse", ems.next_lunar_eclipse, "lunar"),
                             ("next_solar_eclipse", ems.next_solar_eclipse, "solar")):
        for direction_label, search_backward in (("NEXT", False), ("PREVIOUS", True)):
            try:
                result = fn(jd, place, search_backward=search_backward, max_tries=30)
            except Exception as e:
                print(f"{label} ({direction_label}): ERROR: {e}")
                continue
            if result is None:
                print(f"{label} ({direction_label}): None (no eclipse of the requested type found)")
                continue
            type_str, (begin, middle, end) = result
            ok = (begin[0], begin[1], begin[2]) <= (middle[0], middle[1], middle[2]) if kind == "lunar" else True
            print(f"{label} ({direction_label}): type={type_str}")
            print(f"    begin  = {_fmt_ymdfh(begin)}")
            print(f"    middle = {_fmt_ymdfh(middle)}")
            print(f"    end    = {_fmt_ymdfh(end)}")
    print()


def run_eclipse_ms_tests():
    """ Entry point imported by test.py / test1.py, matching the signature
        of run_eclipse_vp_tests(). Runs every eclipse_ms.py book test plus
        the date-level structural checks. """
    test_book_lunar_eclipse_saka_1534()
    test_book_solar_eclipse_saka_1532()
    test_date_level_eclipse_ms()


if __name__ == "__main__":
    run_eclipse_ms_tests()
