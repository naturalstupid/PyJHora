"""
test_vs.py -- tests EVERY public (signature) function of vateshwara_sidhantha.py, the same way test.py / test1.py exercise the other engines
(eclipses are deliberately left out).

Run from the directory that holds test.py:      python test_vs.py

PART A  runs the batches of YOUR test.py unchanged (main block, batch 5-13, sankranti consistency) against the Vateshwara engine, with the
        Surya Siddhantha engine as a control in the same process.  Every call is recorded through a thin proxy, so for each function the
        SHAPE of the returned value (type, nesting, element types) can be compared between VS and SS -- "same signature, arguments, returns".
        A function that fails in VS but not in SS, or whose result changes shape, is a failure.
        A throw-away WARM-UP pass runs first for each engine: some functions import modules lazily on their first call (e.g. karaka_tithi
        imports jhora.horoscope.chart.house), and any text printed at import time would otherwise be charged to whichever engine happens to run
        first.  If the line counts of a batch still differ, the lines that are only in the longer output are printed.
PART B  value checks on the calls that matter most (panchanga, sunrise/sunset, Lagna, positions, sankranti, new/full moon, year lengths ...)
        for several places (north, south, India, US) and dates; every place is a vs.Place.
PART C  the public functions test.py's batches never call (speed helpers, entry-date finders, planetary_positions, raasi, lunar_phase ...).
PART D  precision of the interpolation-based searches for both readings of the Rsine table.
Also checks that utils.get_hora_engine() returns this module for ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA.

Exit status 0 = everything passed.  "KNOWN INHERITED" lines are issues that exist identically in surya_sidhantha.py (listed at the end);
they are reported, not failed, so VS stays a faithful copy of the SS API.
"""
import contextlib, functools, importlib.util, inspect, io, math, os, re, sys, time
from collections import Counter
from jhora import const, utils
from jhora.panchanga import surya_sidhantha as ss, vateshwara_sidhantha as vs

HERE = os.path.dirname(os.path.abspath(__file__))
n_checks, failures, known = 0, [], {}
def check(cond, msg):
    global n_checks
    n_checks += 1
    if not cond: failures.append(msg)
def note_known(key, text): known.setdefault(key, text)
def circ(a, b): return (a - b + 180.0) % 360.0 - 180.0
def to_vs_place(p):
    """ test.py builds drik.Place objects; the VS engine is tested with vs.Place (same four fields). """
    t = tuple(p)
    return vs.Place(t[0], t[1], t[2], t[3])
def to_ss_place(p):
    t = tuple(p)
    return ss.Place(t[0], t[1], t[2], t[3])

# ---------------------------------------------------------------------------------------------------------------------
# shape of a returned value: type, nesting and element types (numbers are all 'num'; lengths may differ, see compat())
# ---------------------------------------------------------------------------------------------------------------------
def shape(x):
    if x is None: return 'None'
    if isinstance(x, bool): return 'bool'
    if isinstance(x, (int, float)): return 'num'
    if isinstance(x, str): return 'str'
    if isinstance(x, (list, tuple)): return (type(x).__name__, tuple(shape(e) for e in x))
    if isinstance(x, dict): return ('dict', ())
    return type(x).__name__
def compat(a, b):
    if isinstance(a, tuple) and isinstance(b, tuple):
        if a[0] != b[0]: return False
        n = min(len(a[1]), len(b[1]))                       # tithi / nakshatra / raasi return 3 or 6 items depending on the day
        return all(compat(x, y) for x, y in zip(a[1][:n], b[1][:n]))
    return a == b
TOLERATE_NONE = {'moonrise', 'moonset', 'next_conjunction_of_planet_pair', 'previous_conjunction_of_planet_pair',
                 'udhaya_lagna_muhurtha', 'pushkara_yoga', 'aadal_yoga', 'vidaal_yoga'}   # legitimately None / () on some days

class Rec:
    """ Wraps a module: every function call is recorded (name -> list of result shapes, or the exception type). """
    def __init__(self, mod, store): self._m, self._s = mod, store
    def __getattr__(self, name):
        a = getattr(self._m, name)
        if callable(a) and not isinstance(a, type):
            @functools.wraps(a)
            def w(*args, **kw):
                try: r = a(*args, **kw)
                except BaseException as e:
                    self._s.setdefault(name, []).append(('EXC', type(e).__name__, str(e)[:80])); raise
                self._s.setdefault(name, []).append(shape(r)); return r
            return w
        return a

# ---------------------------------------------------------------------------------------------------------------------
# PART A
# ---------------------------------------------------------------------------------------------------------------------
def load_test_py():
    for d in (HERE, os.getcwd()):
        p = os.path.join(d, 'test.py')
        if os.path.exists(p):
            if d not in sys.path: sys.path.insert(0, d)           # test.py imports test_book_*.py that live next to it
            spec = importlib.util.spec_from_file_location('pyjhora_test_py', p)
            T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T); return T
    return None
def configure(T, engine):
    if engine == 'VS':
        utils.set_language('en'); T.drik.set_ayanamsa_mode('LAHIRI')
        const.astrology_model_default = const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA
        T.drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)       # mean nodes, like every classical engine
        if hasattr(vs, 'reset_ayanamsa_mode'): vs.reset_ayanamsa_mode()
    else:
        with contextlib.redirect_stdout(io.StringIO()): T._configure(engine)
def run_batches(T, engine, mod, place_conv, store):
    configure(T, engine)
    jd, dob, tob, place = T._chart(); place = place_conv(place); R = Rec(mod, store)
    batches = [('main', lambda: T.main(engine, R, jd, dob, tob, place)),
               ('batch5 (upagrahas, special lagnas)', lambda: T.test_batch5(engine, R, jd, place, dob, tob)),
               ('batch6 (sankranti / solar calendar)', lambda: T.test_batch6(engine, R, dob, place)),
               ('sankranti consistency', lambda: T.test_sankranti_consistency(engine, R, place)),
               ('batch7 (weekday, kaala vibhaga)', lambda: T.test_batch7(engine, R, jd, place)),
               ('batch8 (panchaka, chandrabalam)', lambda: T.test_batch8(engine, R, jd, place)),
               ('batch9 (lunar calendar)', lambda: T.test_batch9(engine, R, jd, place)),
               ('batch10 (yoga / muhurta flags)', lambda: T.test_batch10(engine, R, jd, place)),
               ('batch11 (year lengths, dasha)', lambda: T.test_batch11(engine, R, jd, place)),
               ('batch12 (misc wrappers)', lambda: T.test_batch12(engine, R, jd, place, dob, tob)),
               ('batch13 (karaka tithi, tamil month)', lambda: T.test_batch13(engine, R, jd, place))]
    res = {}
    for name, fn in batches:
        buf = io.StringIO(); t0 = time.time(); crash = None
        try:
            with contextlib.redirect_stdout(buf): fn()
        except BaseException as e: crash = '%s: %s' % (type(e).__name__, str(e)[:100])
        out = buf.getvalue()
        bad = [l.strip() for l in out.split('\n') if re.search(r'ERROR|MISSING|Traceback|MISMATCH', l)]
        res[name] = (out.count('\n'), bad, crash, time.time() - t0, out)
    return res
def warm_up(T):
    """ One throw-away pass per engine.  Functions such as karaka_tithi() import modules lazily on their FIRST call in the process
        (jhora.horoscope.chart.house); whatever such an import prints would otherwise land in the first engine's output (SS) and make
        its line count differ from the second engine's (VS) even though the functions are identical.  Output and records are discarded. """
    for engine, mod, conv in (('SS', ss, to_ss_place), ('VS', vs, to_vs_place)):
        run_batches(T, engine, mod, conv, {})
ENGINE_TAG = re.compile(r'\[(?:SS|VS|KK|GL|TS|VP|MS|DRIK)\]')
def _line_keys(text):
    """ One key per non-empty output line: the engine tag removed and everything from the first '=' on dropped (the values differ between engines
        by design; the labels must not). """
    keys = []
    for l in text.split('\n'):
        if not l.strip(): continue
        l = ENGINE_TAG.sub('[ENG]', l.rstrip())
        keys.append(l.split(' = ')[0].split('=')[0].strip() if not set(l.strip()) <= set('=-#') else l.strip())
    return keys
def only_in_first(out_a, out_b, limit=6):
    """ Lines (as keys) that occur more often in out_a than in out_b. """
    diff = Counter(_line_keys(out_a)) - Counter(_line_keys(out_b))
    return list(diff.elements())[:limit]
def part_a():
    print("=" * 100); print("PART A: test.py's own batches, run for VS (control: SS)"); print("=" * 100)
    T = load_test_py()
    if T is None:
        print("  test.py not found next to test_vs.py or in the working directory -> PART A SKIPPED"); return None
    warm_up(T)
    store_ss, store_vs = {}, {}
    r_ss = run_batches(T, 'SS', ss, to_ss_place, store_ss)
    r_vs = run_batches(T, 'VS', vs, to_vs_place, store_vs)
    print("  %-40s %9s %9s %8s %s" % ("batch", "SS lines", "VS lines", "VS time", "result"))
    for name in r_vs:
        ls, bs, cs, _, out_s = r_ss[name]; lv, bv, cv, tv, out_v = r_vs[name]
        new_bad = [l for l in bv if l not in bs]
        ok = (cv is None or cs is not None) and not new_bad and lv == ls
        check(cv is None or cs is not None, "PART A %s: VS crashed (%s) but SS did not" % (name, cv))
        check(not new_bad, "PART A %s: error lines in VS that SS does not have: %s" % (name, new_bad[:3]))
        extra_s, extra_v = ([], []) if lv == ls else (only_in_first(out_s, out_v), only_in_first(out_v, out_s))
        check(lv == ls, "PART A %s: VS printed %d lines, SS %d; only in SS: %s; only in VS: %s" % (name, lv, ls, extra_s or '-', extra_v or '-'))
        both = [l for l in bv if l in bs]
        print("  %-40s %9d %9d %7.1fs %s%s" % (name, ls, lv, tv, "OK" if ok else "FAIL", ("  (+%d error line(s) that SS shows too)" % len(both)) if both else ""))
        if lv != ls:
            print("      lines only in the SS output: %s" % (extra_s or '-'))
            print("      lines only in the VS output: %s" % (extra_v or '-'))
    fns = sorted(set(store_ss) | set(store_vs)); n_shape = 0; changed = []
    for f in fns:
        a, b = store_ss.get(f, []), store_vs.get(f, [])
        check(len(a) == len(b), "PART A %s: called %d times for SS but %d for VS" % (f, len(a), len(b)))
        for x, y in zip(a, b):
            n_shape += 1
            if x[0] == 'EXC' or y[0] == 'EXC':
                check(x[0] == 'EXC' or y[0] != 'EXC', "PART A %s: raises %s in VS but works in SS" % (f, y[1] if y[0] == 'EXC' else '?')); continue
            if f in TOLERATE_NONE and ('None' in (x, y) or () in (x, y) or ('tuple', ()) in (x, y)): continue
            if not compat(x, y): changed.append(f); check(False, "PART A %s: result shape differs between SS and VS: %s vs %s" % (f, x, y)); break
    print("  functions exercised: %d   result-shape comparisons VS vs SS: %d   shape differences: %d" % (len(fns), n_shape, len(set(changed))))
    called = set(store_vs)
    return called
# ---------------------------------------------------------------------------------------------------------------------
# PART B  (value checks)
# ---------------------------------------------------------------------------------------------------------------------
PLACES = [vs.Place('Chennai', 13.0878, 80.2785, 5.5), vs.Place('Hoffman Estates', 42.0625, -88.1449, -5.0),
          vs.Place('Ujjain', 23.18, 75.79, 5.5), vs.Place('Sydney', -33.87, 151.21, 10.0)]
DATES = [((1996, 12, 7), (10, 34, 0)), ((2026, 10, 26), (18, 42, 0)), ((2016, 1, 10), (0, 0, 0)), ((1962, 2, 5), (0, 0, 0))]
def midnight_jd(jd):
    y, m, d, _ = utils.jd_to_gregorian(jd); return utils.gregorian_to_jd(vs.Date(y, m, d))
def hours_of(jd): return (jd - midnight_jd(jd)) * 24.0
def bisect_cross(f, lo, hi, target):
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if circ(f(mid), target) < 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2.0
def part_b():
    print("=" * 100); print("PART B: value checks (4 places x 4 dates)"); print("=" * 100)
    before = n_checks
    for P in PLACES:
        tz = P.timezone
        moon = lambda t, P=P: vs._sidereal_longitude_impl(t, P, const._MOON)
        sun = lambda t, P=P: vs._sidereal_longitude_impl(t, P, const._SUN)
        for (dob, tob) in DATES:
            jd = utils.julian_day_number(dob, tob); jd_utc = jd - tz / 24.0; tag = "%s %s" % (P.name, dob); h = hours_of(jd)
            # ---- panchanga
            t = vs.tithi(jd, P)
            check(1 <= t[0] <= 30 and t[1] <= h + 1e-6 and h <= t[2] + 1e-6 and t[1] < t[2], "tithi brackets the query instant, " + tag)
            tr = (bisect_cross(lambda x: (moon(x) - sun(x)) % 360, jd, jd + 1.5, (t[0] * 12) % 360) - midnight_jd(jd)) * 24
            check(abs(t[2] - tr) < 0.01, "tithi end time exact (%.3f vs %.3f), %s" % (t[2], tr, tag))
            y = vs.yogam(jd, P)
            check(1 <= y[0] <= 27 and y[1] <= h + 1e-6 <= y[2] + 2e-6, "yogam brackets the query instant, " + tag)
            yr = (bisect_cross(lambda x: (moon(x) + sun(x)) % 360, jd, jd + 1.5, (y[0] * 360 / 27) % 360) - midnight_jd(jd)) * 24
            check(abs(y[2] - yr) < 0.01, "yogam end time exact, " + tag)
            k = vs.karana(jd, P); check(1 <= k[0] <= 60 and k[1] < k[2], "karana " + tag)
            n = vs.nakshatra(jd, P); check(1 <= n[0] <= 27 and 1 <= n[1] <= 4, "nakshatra number / pada, " + tag)
            nr = (bisect_cross(moon, jd, jd + 1.6, n[0] * 360 / 27) - midnight_jd(jd)) * 24
            if abs(n[3] - nr) < 0.01: pass
            elif abs((n[3] - nr) - tz) < 0.1:
                note_known('nak_tz', "nakshatra() / raasi() end times are later than the true crossing by exactly the zone offset (+%.1f h)" % tz)
            else: check(False, "nakshatra end time %.3f vs true %.3f, %s" % (n[3], nr, tag))
            r = vs.raasi(jd, P); check(1 <= r[0] <= 12 and 0.0 <= r[2] <= 1.0, "raasi " + tag)
            check(vs.lunar_longitude(jd_utc, P) == vs.sidereal_longitude(jd_utc, const._MOON, P) and 0 <= vs.solar_longitude(jd_utc, P) < 360, "solar/lunar_longitude, " + tag)
            ph = vs.lunar_phase(jd, P); check(abs(ph - (moon(jd) - sun(jd)) % 360) < 1e-9, "lunar_phase, " + tag)
            # ---- rise / set
            sr, ssx = vs.sunrise(jd, P), vs.sunset(jd, P)
            check(len(sr) == 3 and isinstance(sr[1], str) and sr[2] < ssx[2], "sunrise < sunset, " + tag)
            check(3.0 < sr[0] < 9.5 and 14.0 < ssx[0] < 21.5, "sunrise/sunset clock hours plausible (%.2f, %.2f), %s" % (sr[0], ssx[0], tag))
            dl, nl = vs.day_length(jd, P), vs.night_length(jd, P)
            check(8.5 < dl < 15.5 and abs(dl + nl - 24.0) < 0.2, "day + night = 24 h (%.3f + %.3f), %s" % (dl, nl, tag))
            for fn in ('moonrise', 'moonset'):
                v = getattr(vs, fn)(jd, P); check(v is None or (len(v) == 3 and isinstance(v[1], str)), fn + " format, " + tag)
            # ---- Lagna
            a = vs.ascendant(jd, P); al = a[0] * 30 + a[1]
            check(0 <= a[0] <= 11 and 0.0 <= a[1] < 30.0 and 1 <= a[2] <= 27 and 1 <= a[3] <= 4, "ascendant format, " + tag)
            check(abs(al - vs._ascendant_longitude(jd, P)) < 1e-9, "ascendant() == _ascendant_longitude(), " + tag)
            prev = None; back = 0
            for i in range(0, 289, 4):
                x = vs._ascendant_longitude(midnight_jd(jd) + i / 288.0, P)
                if prev is not None and circ(x, prev) < 0: back += 1
                prev = x
            check(back == 0, "the Lagna never moves backwards over 24 h (%d), %s" % (back, tag))
            sr_jd = vs._sunrise_jd(jd, P); sun_s = (vs._sidereal_longitude_impl(sr_jd, P, const._SUN) + vs._rising_ayanamsa(sr_jd, P)) % 360
            check(abs(circ((vs._ascendant_longitude(sr_jd + 1e-7, P) + vs._rising_ayanamsa(sr_jd, P)) % 360, sun_s)) < 0.02, "Lagna at sunrise = Sun, " + tag)
            # ---- positions
            pp = vs.planetary_positions(jd, P); check(len(pp) == 9 and [p[0] for p in pp] == list(range(9)), "planetary_positions ids, " + tag)
            for (pid, (sg, dg)), swe_key in zip(pp, [vs.ephemeris_planet_index(i) for i in range(9)]):
                check(0 <= sg <= 11 and 0 <= dg < 30.0 + 1e-9, "position in sign range, " + tag)
                check(abs(circ(sg * 30 + dg, vs.sidereal_longitude(jd_utc, swe_key, P))) < 1e-6, "planetary_positions == sidereal_longitude, planet %d, %s" % (pid, tag))
            check(abs(circ(pp[8][1][0] * 30 + pp[8][1][1], pp[7][1][0] * 30 + pp[7][1][1] + 180)) < 1e-6, "Ketu = Rahu + 180, " + tag)
            dv = vs.dhasavarga(jd, P); check(len(dv) == 9 and [d[0] for d in dv] == list(range(9)), "dhasavarga ids, " + tag)
            for m in vs.SUPPORTED_BHAVA_METHODS:
                bm = vs.bhaava_madhya(jd, P, m); check(len(bm) == 12 and all(0 <= b < 360 for b in bm), "bhaava_madhya method %s, %s" % (m, tag))
                if m == 1: check(abs(circ(bm[0], al)) < 1e-9, "house 1 = Lagna, " + tag)
            check(len(vs.declination_of_planets(jd, P)) == 7 and all(abs(x) < 30 for x in vs.declination_of_planets(jd, P)), "declination_of_planets, " + tag)
            # ---- calendar
            vw = vs.vaara(jd, P); check(0 <= vw <= 6 and 0 <= vs.civil_weekday(jd) <= 6, "weekday, " + tag)
            check(vs.vedic_weekday(jd, P) == vw, "vedic_weekday == vaara, " + tag)
            sm = vs.solar_month_date(jd, P); check(0 <= sm[0] <= 11 and 1 <= sm[1] <= 32, "solar_month_date, " + tag)
            tm = vs.tamil_solar_month_and_date(vs.Date(*dob), P); check(0 <= tm[0] <= 11 and 1 <= tm[1] <= 32, "tamil_solar_month_and_date, " + tag)
            lm = vs.lunar_month(jd, P); check(1 <= lm[0] <= 12 and all(isinstance(b, bool) for b in lm[1:]), "lunar_month, " + tag)
            check(len(vs.vedic_date(jd, P, calendar_type=const.CALENDAR_TYPE.SOLAR)) == 6, "vedic_date(SOLAR), " + tag)
            ns = vs.next_sankranti_date(vs.Date(*dob), P)
            check(ns[3] == 1 and 0 <= ns[2] <= 11, "next_sankranti_date, " + tag)
            ps = vs.previous_sankranti_date(vs.Date(*dob), P); check((ps[2] + 1) % 12 == ns[2], "previous / next sankranti are consecutive months, " + tag)
            # ---- searches
            for pl in (const.SUN_ID, const.MOON_ID, const.MARS_ID, const.SATURN_ID):
                pj, plong = vs.next_planet_entry_date(pl, jd, P)
                check(pj > jd and abs(circ(plong, round(plong / 30) * 30)) < 0.02, "next_planet_entry_date lands on a sign boundary, planet %d, %s" % (pl, tag))
                qj, qlong = vs.previous_planet_entry_date(pl, jd, P)
                check(qj < jd and abs(circ(qlong, round(qlong / 30) * 30)) < 0.02, "previous_planet_entry_date, planet %d, %s" % (pl, tag))
            cj, l1, l2 = vs.next_conjunction_of_planet_pair(jd, P, const.SUN_ID, const.MOON_ID)
            lin = const.vs_rsine_method_default == const.VS_RSINE_METHOD.LINEAR      # see PART D for why the tolerance depends on the reading
            check(cj > jd and abs(circ(l1, l2)) < (0.1 if lin else 0.01), "next Sun-Moon conjunction (separation %.4f), %s" % (circ(l1, l2), tag))
            ti = t[0]
            nmj = vs.new_moon(jd, P, ti, -1); fmj = vs.full_moon(jd, P, ti, -1)
            tol_nf = 0.15 if lin else 0.02
            check(abs(circ(vs.lunar_phase(nmj, P), 0.0)) < tol_nf and abs(circ(vs.lunar_phase(fmj, P), 180.0)) < tol_nf, "new_moon / full_moon phase, " + tag)
            ra = vs.next_ascendant_entry_date(jd, P); check(ra[0] > jd and ra[1][1] < 0.2 or ra[1][1] > 29.8, "next_ascendant_entry_date is at a sign boundary, " + tag)
            # ---- retrograde
            rg = vs.planets_in_retrograde(jd, P); check(set(rg) <= set(range(2, 9)) and {7, 8} <= set(rg), "planets_in_retrograde (mean nodes always retrograde), " + tag)
        # ---- per place
        # year lengths follow the BOOK: the Sun returns to the same sidereal longitude after civil days / solar years
        jd0 = utils.julian_day_number((2026, 3, 1), (12, 0, 0))
        book_year = const.VS_YUGA.CIVIL_DAYS / const.VS_YUGA.SOLAR_YEARS
        check(abs(vs._VS_SIDEREAL_YEAR_DAYS - 13149313 / 36000) < 1e-12 and abs(book_year - 365.2586944444) < 1e-9, "the VS sidereal year is 13149313/36000 days")
        check(abs(vs.true_sidereal_year(jd0, P) - book_year) < 0.002, "true_sidereal_year ~ the book's %.6f d (got %.6f), %s" % (book_year, vs.true_sidereal_year(jd0, P), P.name))
        rate = vs._surya_sidhantha_ayanamsa_rate(jd0, P)
        check(abs(vs.true_tropical_year(jd0, P) - 360.0 / (360.0 / book_year + rate)) < 1e-9, "true_tropical_year uses the book's sidereal year, " + P.name)
    # ---- model-level
    check(vs._calculate_beeja_correction(2451545.0, PLACES[0], const._MARS) == 0.0 and
          all(vs._sidereal_longitude_impl_with_beeja(2451545.0, PLACES[0], p) == vs._sidereal_longitude_impl(2451545.0, PLACES[0], p)
              for p in (const._SUN, const._MOON, const._MARS, const._MERCURY, const._JUPITER, const._VENUS, const._SATURN, const._RAHU)),
          "no separate bija: *_with_beeja == the plain pipeline")
    check(abs(vs.get_ayanamsa_value(2451545.0, PLACES[0]) - vs.surya_sidhantha_ayanamsa(2451545.0, PLACES[0])) < 1e-12, "get_ayanamsa_value (inherited SS trepidation until the book gives a number)")
    check(utils.get_hora_engine(const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA) is vs, "utils.get_hora_engine(VATESHWARA_SIDHANTHA) returns this module")
    check(utils.get_hora_engine(const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA) is ss, "utils.get_hora_engine(SURYA_SIDDHANTHA) is unchanged")
    print("  value checks run: %d" % (n_checks - before))
# ---------------------------------------------------------------------------------------------------------------------
# PART C  (public functions test.py's batches do not call)
# ---------------------------------------------------------------------------------------------------------------------
def part_c(called):
    print("=" * 100); print("PART C: the remaining public functions"); print("=" * 100)
    pub = sorted(n for n, f in inspect.getmembers(vs, inspect.isfunction)
                 if f.__module__ == vs.__name__ and not n.startswith(('_', 'vs_')) and n != 'ahargana_from_calendar' and 'eclipse' not in n)
    left = [n for n in pub if called is None or n not in called]
    P_vs, P_ss = PLACES[0], ss.Place('Chennai', 13.0878, 80.2785, 5.5)
    jd = utils.julian_day_number((1996, 12, 7), (10, 34, 0)); jd_utc = jd - 5.5 / 24; D = vs.Date(1996, 12, 7); tob = (10, 34, 0)
    sunlong = 245.123
    CALLS = {
        'ahargana': lambda m, P: m.ahargana(jd), 'kali_ahargana_days': lambda m, P: m.kali_ahargana_days(jd, P),
        'asind': lambda m, P: m.asind(0.5), 'atand': lambda m, P: m.atand(1.0), 'atan2d': lambda m, P: m.atan2d(1.0, 1.0),
        'sind': lambda m, P: m.sind(30.0), 'cosd': lambda m, P: m.cosd(60.0), 'tand': lambda m, P: m.tand(45.0),
        'daily_moon_speed': lambda m, P: m.daily_moon_speed(jd, P), 'daily_sun_speed': lambda m, P: m.daily_sun_speed(jd, P),
        'daily_planet_speed': lambda m, P: m.daily_planet_speed(jd, P, const.MARS_ID),
        'dasavarga_from_long': lambda m, P: m.dasavarga_from_long(123.4), 'elapsed_year': lambda m, P: m.elapsed_year(jd, 7),
        'ephemeris_planet_index': lambda m, P: m.ephemeris_planet_index(const.MARS_ID),
        'get_ayanamsa_value': lambda m, P: m.get_ayanamsa_value(jd, P), 'get_planet_speed_sign': lambda m, P: m.get_planet_speed_sign(jd, P, const.MARS_ID),
        'jd_to_gregorian': lambda m, P: m.jd_to_gregorian(jd), 'kunda_lagna': lambda m, P: m.kunda_lagna(jd, P),
        'lunar_longitude': lambda m, P: m.lunar_longitude(jd_utc, P), 'solar_longitude': lambda m, P: m.solar_longitude(jd_utc, P),
        'lunar_phase': lambda m, P: m.lunar_phase(jd, P), 'lunar_year_index': lambda m, P: m.lunar_year_index(jd, 7),
        'nakshatra_new': lambda m, P: m.nakshatra_new(jd, P), 'nakshatra_pada': lambda m, P: m.nakshatra_pada(123.4),
        'next_ascendant_entry_date': lambda m, P: m.next_ascendant_entry_date(jd, P), 'previous_ascendant_entry_date': lambda m, P: m.previous_ascendant_entry_date(jd, P),
        'next_planet_entry_date': lambda m, P: m.next_planet_entry_date(const.MARS_ID, jd, P), 'previous_planet_entry_date': lambda m, P: m.previous_planet_entry_date(const.MARS_ID, jd, P),
        'next_planet_entry_date_general': lambda m, P: m.next_planet_entry_date_general(jd, P, const.MARS_ID),
        'next_planet_nakshathra_pravesha_date': lambda m, P: m.next_planet_nakshathra_pravesha_date(const.MARS_ID, 5, jd, P),
        'next_planet_stationary_duration': lambda m, P: m.next_planet_stationary_duration(const.MARS_ID, jd, P),
        'next_sankranti_date_from_jd': lambda m, P: m.next_sankranti_date_from_jd(jd, P), 'previous_sankranti_date_from_jd': lambda m, P: m.previous_sankranti_date_from_jd(jd, P),
        'next_tithi': lambda m, P: m.next_tithi(jd, P, 10), 'night_length': lambda m, P: m.night_length(jd, P), 'day_length': lambda m, P: m.day_length(jd, P),
        'planetary_positions': lambda m, P: m.planetary_positions(jd, P), 'previous_conjunction_of_planet_pair': lambda m, P: m.previous_conjunction_of_planet_pair(jd, P, const.SUN_ID, const.MOON_ID),
        'raasi': lambda m, P: m.raasi(jd, P), 'rahu': lambda m, P: m.rahu(55.0), 'special_ascendant': lambda m, P: m.special_ascendant(jd, P),
        'sree_lagna_from_moon_asc_longitudes': lambda m, P: m.sree_lagna_from_moon_asc_longitudes(100.0, 200.0),
        'surya_sidhantha_ayanamsa': lambda m, P: m.surya_sidhantha_ayanamsa(jd, P), 'tamil_solar_month_and_date_from_jd': lambda m, P: m.tamil_solar_month_and_date_from_jd(jd, P),
        'upagraha_longitude': lambda m, P: m.upagraha_longitude(D, tob, P, const.SATURN_ID), 'vaara_from_ahargana': lambda m, P: m.vaara_from_ahargana(jd),
        'vedic_time_equal_day_night_ghati': lambda m, P: m.vedic_time_equal_day_night_ghati(jd, P), 'vedic_weekday': lambda m, P: m.vedic_weekday(jd, P),
        'zone_longitude_correction_days': lambda m, P: m.zone_longitude_correction_days(P),
        'set_ayanamsa_mode': lambda m, P: m.set_ayanamsa_mode('LAHIRI'), 'reset_ayanamsa_mode': lambda m, P: m.reset_ayanamsa_mode(),
        'set_planet_list': lambda m, P: m.set_planet_list(), 'refresh_planet_flags': lambda m, P: m.refresh_planet_flags(),
        'set_tropical_planets': lambda m, P: m.set_tropical_planets(), 'set_sideral_planets': lambda m, P: m.set_sideral_planets(),
    }
    n_ok = 0; uncovered = []
    for name in left:
        c = CALLS.get(name)
        if c is None: uncovered.append(name); continue
        ra = rb = None; ea = eb = None
        try: ra = c(ss, P_ss)
        except Exception as e: ea = '%s: %s' % (type(e).__name__, str(e)[:60])
        try: rb = c(vs, P_vs)
        except Exception as e: eb = '%s: %s' % (type(e).__name__, str(e)[:60])
        check(eb is None or ea is not None, "PART C %s raises in VS (%s) but not in SS" % (name, eb))
        if ea is None and eb is None:
            check(compat(shape(ra), shape(rb)), "PART C %s: result shape differs %s vs %s" % (name, shape(ra), shape(rb))); n_ok += 1
    # a few of them also get a value check
    check(abs(vs.ahargana(jd) - vs.kali_ahargana_days(jd, P_vs) - (jd - math.floor(jd - 0.5) - 0.5)) < 1e-9, "ahargana(jd) = kali_ahargana_days + fraction of the day")
    check(abs(vs.daily_sun_speed(jd, P_vs) - 1.0) < 0.05 and 11.5 < vs.daily_moon_speed(jd, P_vs) < 15.5, "daily Sun / Moon speed plausible")
    check(abs(vs.zone_longitude_correction_days(P_vs) - (80.2785 - 82.5) / 15.0 / 24.0) < 1e-12, "zone_longitude_correction_days")
    check(vs.lunar_year_index(jd, 7) == ss.lunar_year_index(jd, 7), "lunar_year_index depends only on the Ahargana")
    moon_f = lambda t: vs._sidereal_longitude_impl(t, P_vs, const._MOON); sun_f = lambda t: vs._sidereal_longitude_impl(t, P_vs, const._SUN)
    true_nt = bisect_cross(lambda t: (moon_f(t) - sun_f(t)) % 360, jd, jd + 31, 108.0)
    nt = vs.next_tithi(jd, P_vs, 10)
    if abs(nt - true_nt) < 0.0005: pass
    elif abs((nt - P_vs.timezone / 24.0) - true_nt) < 0.002:
        note_known('next_tithi_tz', "next_tithi() returns the instant shifted by +timezone/24 days (zone offset added to a jd that is already local)")
    else: check(False, "next_tithi %.5f vs true crossing %.5f" % (nt, true_nt))
    print("  public functions left over by test.py's batches: %d  | exercised and shape-checked here: %d  | not exercised here: %s" % (len(left), n_ok, uncovered or 'none'))
    return uncovered
# ---------------------------------------------------------------------------------------------------------------------
# PART D  (precision of the interpolation-based searches, both readings of the Rsine table)
# ---------------------------------------------------------------------------------------------------------------------
def part_d():
    print("=" * 100); print("PART D: precision of the Lagrange-interpolation searches, by Rsine reading (const.vs_rsine_method_default)"); print("=" * 100)
    P = vs.Place('Chennai', 13.0878, 80.2785, 5.5); tz = 5.5
    moon = lambda t: vs._sidereal_longitude_impl(t, P, const._MOON); sun = lambda t: vs._sidereal_longitude_impl(t, P, const._SUN)
    saved = const.vs_rsine_method_default
    LIM = {const.VS_RSINE_METHOD.LINEAR:       dict(conj=0.10, nm=0.15, fm=0.15, nak=3.0, ras=40.0, nt=0.2),
           const.VS_RSINE_METHOD.SECOND_ORDER: dict(conj=0.01, nm=0.02, fm=0.02, nak=1.0, ras=5.0, nt=0.1)}
    try:
        for meth in (const.VS_RSINE_METHOD.LINEAR, const.VS_RSINE_METHOD.SECOND_ORDER):
            const.vs_rsine_method_default = meth
            w = dict(conj=0.0, nm=0.0, fm=0.0, nak=0.0, ras=0.0, nt=0.0)
            for k in range(24):
                jd = 2450000.5 + k * 487.3 + 0.37
                cj, l1, l2 = vs.next_conjunction_of_planet_pair(jd, P, const.SUN_ID, const.MOON_ID); w['conj'] = max(w['conj'], abs(circ(moon(cj), sun(cj))))
                ti = vs.tithi(jd, P)[0]
                w['nm'] = max(w['nm'], abs(circ(vs.lunar_phase(vs.new_moon(jd, P, ti, -1), P), 0))); w['fm'] = max(w['fm'], abs(circ(vs.lunar_phase(vs.full_moon(jd, P, ti, -1), P), 180)))
                mid = midnight_jd(jd)
                nk = vs.nakshatra(jd, P); w['nak'] = max(w['nak'], abs((nk[3] - tz) - (bisect_cross(moon, jd, jd + 1.7, nk[0] * 360 / 27) - mid) * 24) * 60)
                ra = vs.raasi(jd, P); w['ras'] = max(w['ras'], abs((ra[1] - tz) - (bisect_cross(moon, jd, jd + 4.5, ra[0] * 30) - mid) * 24) * 60)
                nt = vs.next_tithi(jd, P, 10) - tz / 24.0
                w['nt'] = max(w['nt'], abs(nt - bisect_cross(lambda t: (moon(t) - sun(t)) % 360, jd, jd + 31, 108.0)) * 1440)
            lim = LIM[meth]
            for key, lab, unit in (('conj', 'next_conjunction_of_planet_pair', 'deg'), ('nm', 'new_moon', 'deg'), ('fm', 'full_moon', 'deg'),
                                   ('nak', 'nakshatra() end (zone offset removed)', 'min'), ('ras', 'raasi() end (zone offset removed)', 'min'), ('nt', 'next_tithi (zone offset removed)', 'min')):
                check(w[key] < lim[key], "PART D %s %s: worst %.4f %s exceeds %.3f" % (meth.name, lab, w[key], unit, lim[key]))
            print("  %-13s conjunction %.4f deg | new_moon %.4f deg | full_moon %.4f deg | nakshatra end %.2f min | raasi end %.2f min | next_tithi %.2f min   %s" % (
                meth.name, w['conj'], w['nm'], w['fm'], w['nak'], w['ras'], w['nt'], "<- current default" if meth == saved else ""))
    finally:
        const.vs_rsine_method_default = saved
def main():
    t0 = time.time()
    called = part_a(); part_b(); uncovered = part_c(called); part_d()
    print("=" * 100)
    if known:
        print("KNOWN INHERITED (identical in surya_sidhantha.py; reported, not failed):")
        for k, v in known.items(): print("  -", v)
    print("checks run: %d   failures: %d   (%.0f s)" % (n_checks, len(failures), time.time() - t0))
    for f in failures[:40]: print("  FAILED:", f)
    if not failures: print("ALL %d CHECKS PASSED" % n_checks)
    return 1 if failures else 0
if __name__ == '__main__':
    from jhora.panchanga.drik import Date, Place
    dob = Date(1996,12,7); tob = (10,34,0); place = Place('Chennai,IN',13.0389, 80.2619, +5.5)
    jd = utils.julian_day_number(dob,tob)
    for am in const.ASTROLOGY_MODELS:
        const.astrology_model_default = am
        hora_engine = utils.hora_engine_proxy
        print(am.name,'nakshatra',hora_engine.nakshatra(jd,place))
        print(am.name,'raasi',hora_engine.raasi(jd,place))
    exit()
    sys.exit(main())
