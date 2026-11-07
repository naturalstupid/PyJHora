"""
test_book_mks.py
=================
Book tests for the Makaranda Sarini engine (makaranda_sarini.py), in the
same house style as test_book_vakya.py / the other test_book_* functions
inside test.py (banner, book-stated values printed alongside the computed
ones, explicit MATCH/CHECK verdicts).

Source: the Makaranda Sarini's own worked example, Saka 1534 Vaisakha
sukla 15 (pp. 0072-0081 of the scanned pages catalogued for this project).
This is the SAME epoch that makaranda_sarini.py's own mks_selftest()
checks; this file re-presents that same comparison in the book-test
narrative format the rest of the test suite uses, and is what
run_mks_book_tests() (imported by test.py / test1.py) calls.

HONESTY NOTE (carried over from makaranda_sarini.py's own docstring):
Sun, Moon, Mercury and the node are read from the book's own vatika/valli
tables and the bija rule, and track the book's printed example closely.
Jupiter, Venus and Saturn's manda/sighra PHALA TABLES have not been
transcribed cell-by-cell from the scans -- they are regenerated from the
classical Surya-Siddhanta sine/tangent laws (confidence='fitted' in the
engine), so differences of a few arcminutes there are EXPECTED and are
not a sign the procedure is wrong. Mars has an unresolved ~2-degree
discrepancy: the book's own printed manda phala for this example does not
follow from its own printed manda kendra under any tested table law, and
this has not been explained -- it is reported here, not silently dropped.
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
    """ Pretty-print a decimal-degree value as D(sign)M'S", matching the
        book's own rasi;degree;minute;second notation after conversion. """
    sign = '-' if deg < 0 else ''
    total_cs = round(abs(deg) % 360 * 3600 * 100)   # centiseconds, avoids 59.996 -> "60.00" rounding artifacts
    rasi, rem = divmod(total_cs, 30 * 3600 * 100)
    d, rem = divmod(rem, 3600 * 100)
    m, cs = divmod(rem, 6000)
    s = cs / 100.0
    return f"{sign}{rasi}r{d:02d}\u00b0{m:02d}'{s:05.2f}\""


def _book_dms(d, m, s):
    """ Format a (degree, minute, second) triple the same way, for printing
        known constants like the ayanamsa without going through _dms(). """
    return f"{d}\u00b0{m:02d}'{s:05.2f}\""


def test_book_graha_sadhana_saka_1534():
    """
    Makaranda Sarini's own worked example -- graha-sadhana (planet
    computation), Saka 1534 Vaisakha sukla 15 (pp. 0072-0081).
    Ahargana (graha-dina-valli, read as the Kali day-count in base 60):
        valli 7|58|11|40 (base 60) = 1,721,500 days
        Kali-gata 4713 = Saka 1534 + 3179  (confirms the valli reading)
    Book's own printed true (sphuta) longitudes for this example (read by
    eye from the scans; see makaranda_sarini.py's module docstring and
    mks_selftest() for the per-body reading notes):
        Sun     1r 06;26;00   (seconds digit 0/10 unclear)
        Moon    7r 04;56;33
        Mars    11r 06;49;24  (4/6 digit unclear -- see note below)
        Mercury 1r 19;26;20   (first digit 1/11 unclear)
        Jupiter 3r 29;32;28   (this is the book's "saurabha"/method-B
                               result; the method-A line was not read)
        Venus   2r 13;10;55   (first digit 2/3 unclear)
        Saturn  10r 28;38;35  (seconds 35/48 differ between the book's two
                               methods on this page)
        Ketu    7r 15;52;29   (mean node; the book adds a node bija of
                               -Saturn/6 per this session's reading)
    """
    mks = _imp('makaranda_sarini')
    print("=" * 78)
    print("BOOK TEST (MS-1): Makaranda Sarini graha-sadhana, Saka 1534")
    print("                  Vaisakha sukla 15 (pp. 0072-0081)")
    print("=" * 78)
    rows = mks.mks_selftest(verbose=False)
    print(f"{'Body':20s}{'book (printed)':>18s}{'engine (computed)':>20s}{'diff':>12s}")
    print("-" * 70)
    for label, printed_deg, engine_deg, diff_arcsec in rows:
        flag = "OK" if abs(diff_arcsec) < 60 else "CHECK (see note)"
        print(f"{label:20s}{_dms(printed_deg):>18s}{_dms(engine_deg):>20s}"
              f"{diff_arcsec:+9.1f}\"  [{flag}]")
    print()
    print("Notes:")
    print("  - Sun, Moon, Mercury and Ketu match the book's printed example")
    print("    closely (see the per-body reading-confidence notes in")
    print("    makaranda_sarini.py's _EXAMPLE table).")
    print("  - Jupiter, Venus, Saturn differences are EXPECTED: their")
    print("    manda/sighra phala tables are 'fitted' (regenerated from the")
    print("    classical Surya-Siddhanta sine/tangent laws), not transcribed")
    print("    cell-by-cell from the book's own printed tables.")
    print("  - Mars has an UNRESOLVED ~2-degree discrepancy: the book's own")
    print("    printed manda phala for this example does not follow from its")
    print("    own printed manda kendra under the tested table law. This is")
    print("    reported, not silently corrected.")
    ay = mks._rising_ayanamsa_utc(mks._KALI_JD0 + mks._EXAMPLE_AHARGANA - mks._UJJAIN_LONGITUDE / 360.0)
    ay_cs = round(ay * 3600 * 100)
    ay_d, rem = divmod(ay_cs, 3600 * 100)
    ay_m, ay_cs2 = divmod(rem, 6000)
    ay_s = ay_cs2 / 100.0
    print(f"\n  Ayanamsa: book={_book_dms(16, 41, 42.0)}   engine={_book_dms(ay_d, ay_m, ay_s)}"
          f"   (continuous-in-time model; book uses whole Saka years)")
    print()


def run_mks_book_tests():
    """ Entry point imported by test.py / test1.py, matching the signature
        of run_vakya_book_tests(). Runs every Makaranda Sarini book test
        in this file. """
    test_book_graha_sadhana_saka_1534()


if __name__ == "__main__":
    run_mks_book_tests()
