"""
check_engines_vs_drik.py -- review harness: every PyJHora engine against ITSELF and against drik.

Run from the folder that holds test.py (it reuses test.py's engine names and _configure()):

    python check_engines_vs_drik.py                 # SS KK GL TS VP MS VS, each compared with drik
    python check_engines_vs_drik.py SS VS           # only these engines
    python check_engines_vs_drik.py --full SS       # more places / dates / hours (about 4x slower)

WHY IT NEEDS NO REFERENCE VALUES
  Every engine can be asked for its OWN Sun/Moon longitude (mod.sidereal_longitude).  For any instant the exact start/end of a
  nakshatra, raasi, tithi or yogam is then just a root-find on that engine's own longitude.  So each engine is checked for
  internal consistency, and a wrong time-zone term shows up as an error of exactly k x tz hours, whatever Moon model the engine uses.

PER ENGINE (places with different time zones x dates x local times of day)
  nakshatra()/raasi()/tithi()/yogam() END time           vs the exact crossing of the engine's own longitude   (minutes)
  nakshatra() START <= query time <= END                  must hold
  raasi() number and fraction-left                       vs the engine's own Moon at the query instant
  next_tithi()                                           vs the exact crossing
  nakshatra_new() number                                 vs the engine's own Moon
  against drik, same cases: how much of the difference in end times the two Moon positions explain, and what is left over
VERDICT words:  ok | LATE by tz | EARLY by tz | other (not a constant shift: look at the examples printed)

Exit status 0 always (this is a review tool, not a pass/fail test).
"""
import importlib.util, math, os, statistics as st, sys, time

PLACES_QUICK = [('Chennai,India', 13.0878, 80.2785, 5.5), ('Hoffman Estates,US', 42.0625, -88.1449, -5.0),
                ('London,UK', 51.5072, -0.1276, 0.0), ('Sydney,AU', -33.8688, 151.2093, 10.0)]
PLACES_FULL = PLACES_QUICK + [('Los Angeles,US', 34.0522, -118.2437, -8.0), ('Kolkata,India', 22.5726, 88.3639, 5.5)]
HOURS_QUICK = [1.5, 7.0, 10.567, 14.0, 18.0, 23.0]
HOURS_FULL = [0.5, 3.0, 5.5, 7.0, 9.0, 10.567, 12.0, 14.0, 16.0, 18.0, 20.0, 23.0]
N_DATES_QUICK, N_DATES_FULL = 6, 10
TOL_MIN = 5.0                                    # minutes: below this an end time counts as correct
MOON, SUN = None, None                           # filled from jhora.const in main() (swe-style keys)

# ---------------------------------------------------------------------------------------------------------------
def circ(a, b): return (a - b + 180.0) % 360.0 - 180.0
def local_midnight(jd): return math.floor(jd - 0.5) + 0.5
def cross(f, lo, hi, target, n=42):
    """ first t in [lo, hi] where the increasing angle f(t) passes `target` (degrees) """
    for _ in range(n):
        m = 0.5 * (lo + hi)
        if circ(f(m), target) < 0: lo = m
        else: hi = m
    return 0.5 * (lo + hi)

class Engine:
    """ Thin adapter around one engine module.  `lon(jd_utc, planet, place)` is the engine's OWN longitude. """
    def __init__(self, name, mod, lon, configure=None):
        self.name, self.mod, self.lon, self.configure = name, mod, lon, configure
    def call(self, fn, *a, **k):
        f = getattr(self.mod, fn, None)
        if f is None: return None
        try: return f(*a, **k)
        except Exception as e:
            self.errors[fn] = self.errors.get(fn, 0) + 1; self.last_error[fn] = "%s: %s" % (type(e).__name__, str(e)[:80]); return None
    errors, last_error = None, None

def collect(eng, cases):
    """ For each case (place, jd_local, hour) ask the engine for its panchanga values and compute the exact truth from its own longitude. """
    eng.errors, eng.last_error = {}, {}
    if eng.configure: eng.configure()
    recs = []
    for (place, jd, h) in cases:
        tz = place.timezone; mid = local_midnight(jd); T = jd - tz / 24.0
        moon = lambda t: eng.lon(t, MOON, place); sun = lambda t: eng.lon(t, SUN, place)
        phase = lambda t: (moon(t) - sun(t)) % 360.0; ysum = lambda t: (moon(t) + sun(t)) % 360.0
        L = moon(T); one_star = 360.0 / 27
        rec = dict(place=place, tz=tz, h=h, jd=jd, L=L, speed=((moon(T + 1 / 24.0) - moon(T - 1 / 24.0) + 540.0) % 360.0 - 180.0) / 2.0)   # degrees per hour
        nak = int(L // one_star) + 1; ras = int(L // 30) + 1; tit = int(phase(T) // 12) + 1; yog = int(ysum(T) // one_star) + 1
        hrs = lambda t_ut: (t_ut + tz / 24.0 - mid) * 24.0
        truth = dict(nak=nak, ras=ras, tit=tit, yog=yog, frac=1.0 - (L / 30.0) % 1.0,
                     nak_end=hrs(cross(moon, T, T + 1.7, (nak * one_star) % 360)), ras_end=hrs(cross(moon, T, T + 4.6, (ras * 30) % 360)),
                     tit_end=hrs(cross(phase, T, T + 1.7, (tit * 12) % 360)), yog_end=hrs(cross(ysum, T, T + 1.7, (yog * one_star) % 360)))
        rec['truth'] = truth
        n = eng.call('nakshatra', jd, place); r = eng.call('raasi', jd, place); t = eng.call('tithi', jd, place); y = eng.call('yogam', jd, place)
        rec['nak'] = n; rec['ras'] = r; rec['tit'] = t; rec['yog'] = y
        req = (truth['tit'] + 1) % 30 + 1
        nt = eng.call('next_tithi', jd, place, req, opt=1, start_of_tithi=True)
        # window must stay below one lunar cycle (29.5 d): the Moon-Sun phase wraps through 360 deg, so a longer window breaks the bisection
        # (a 31-day window returned a crossing a month away in about 20% of the cases).  The tithi after next starts within ~3 days; 5 d is safe.
        rec['next_tithi_err'] = None if nt is None else (nt - (cross(phase, T, T + 5.0, ((req - 1) * 12) % 360) + tz / 24.0)) * 1440.0
        nn = eng.call('nakshatra_new', jd, place); rec['nak_new'] = None if nn is None else nn[0]
        recs.append(rec)
    return recs

def minutes(rec, key):
    v = rec[key[0]]
    if v is None: return None
    idx, tk = key[1], key[2]
    return (v[idx] - rec['truth'][tk]) * 60.0

def verdict(vals, tzs):
    """ ok: at most 2% of the cases off by more than TOL_MIN.  LATE/EARLY by tz: most of the cases that are off are off by exactly +/- tz hours
        (within 3%).  otherwise 'wrong in N%' (not a constant shift -- look at the examples). """
    vals = [(v, z) for v, z in zip(vals, tzs) if v is not None]
    if not vals: return "n/a", None
    bad = [(v, z) for v, z in vals if abs(v) > TOL_MIN]
    share = len(bad) / len(vals)
    nz = [v / (60.0 * z) for v, z in bad if z != 0]
    ratio = st.median(nz) if nz else None
    if share <= 0.02: return "ok", ratio
    if len(nz) >= 8:
        late = sum(1 for x in nz if 0.97 <= x <= 1.03) / len(nz); early = sum(1 for x in nz if -1.03 <= x <= -0.97) / len(nz)
        if late >= 0.6: return "LATE by tz" + ("" if late > 0.98 else " (+%.0f%% other)" % (100 * (1 - late))), ratio
        if early >= 0.6: return "EARLY by tz" + ("" if early > 0.98 else " (+%.0f%% other)" % (100 * (1 - early))), ratio
    return "wrong in %.0f%%" % (100 * share), None

QUANT = [('nakshatra() end', ('nak', 3, 'nak_end')), ('raasi() end', ('ras', 1, 'ras_end')),
         ('tithi() end', ('tit', 2, 'tit_end')), ('yogam() end', ('yog', 2, 'yog_end'))]

def report(eng, recs, ref=None):
    tzs = [r['tz'] for r in recs]; out = {}
    print("\n" + "=" * 100); print("%s   (%d cases, call exceptions: %s)" % (eng.name, len(recs), eng.errors or "none"))
    for fn, msg in (eng.last_error or {}).items(): print("   last exception in %s(): %s" % (fn, msg))
    print("  %-18s %12s %12s %10s %14s   %s" % ("quantity", "median |err|", "max |err|", ">%d min" % TOL_MIN, "off-cases/(tz*60)", "verdict"))
    for label, key in QUANT:
        v = [minutes(r, key) for r in recs]; vv = [x for x in v if x is not None]
        if not vv: print("  %-18s %s" % (label, "not available")); out[label] = "n/a"; continue
        vd, ratio = verdict(v, tzs)
        big = sum(1 for x in vv if abs(x) > TOL_MIN) / len(vv)
        print("  %-18s %10.1f m %10.1f m %9.0f%% %14s   %s" % (label, st.median([abs(x) for x in vv]), max(abs(x) for x in vv), 100 * big, "%.3f" % ratio if ratio is not None else "-", vd))
        out[label] = vd
    # raasi number / fraction
    rr = [r for r in recs if r['ras'] is not None]
    if rr:
        wrong = [r for r in rr if r['ras'][0] != r['truth']['ras']]; fr = [abs(r['ras'][2] - r['truth']['frac']) for r in rr]
        nzr = [r for r in rr if r['tz'] != 0]; wnz = [r for r in nzr if r['ras'][0] != r['truth']['ras']]
        print("  raasi() number differs from the engine's own Moon sign: %d of %d (tz != 0: %d of %d)  | fraction-left |err| median %.3f, max %.3f of a sign" % (
            len(wrong), len(rr), len(wnz), len(nzr), st.median(fr), max(fr)))
        out['raasi number'] = "ok" if not wrong else "WRONG in %.0f%%" % (100.0 * len(wrong) / len(rr))
        out['raasi fraction'] = "ok" if st.median(fr) < 0.01 else "off by %.2f sign" % st.median(fr)
        if wrong:
            for r in wrong[:2]:
                print("     e.g. %s tz %+.1f local %.2f h: engine says raasi %d, its own Moon (%.2f deg) is in raasi %d" % (r['place'].name, r['tz'], r['h'], r['ras'][0], r['L'], r['truth']['ras']))
    nn = [r for r in recs if r['nak'] is not None]
    if nn:
        viol = [r for r in nn if not (r['nak'][2] <= r['h'] + 1e-6 <= r['nak'][3] + 1e-6)]
        print("  nakshatra(): start <= query <= end violated in %d of %d cases" % (len(viol), len(nn))); out['bracket'] = len(viol)
        if viol:
            r = viol[0]; print("     e.g. %s tz %+.1f query %.2f h: start %.2f  end %.2f" % (r['place'].name, r['tz'], r['h'], r['nak'][2], r['nak'][3]))
    nt = [r['next_tithi_err'] for r in recs if r['next_tithi_err'] is not None]
    if nt:
        vd, ratio = verdict(nt, [r['tz'] for r in recs if r['next_tithi_err'] is not None])
        print("  next_tithi(): median |err| %.1f min, max |err| %.1f min, off-cases/(tz*60) %s   %s" % (st.median([abs(x) for x in nt]), max(abs(x) for x in nt), "%.3f" % ratio if ratio is not None else "-", vd)); out['next_tithi'] = vd
    nw = [r for r in recs if r['nak_new'] is not None]
    if nw:
        bad = sum(1 for r in nw if r['nak_new'] != r['truth']['nak'])
        print("  nakshatra_new(): number differs from the engine's own Moon in %d of %d cases" % (bad, len(nw))); out['nakshatra_new'] = "ok" if not bad else "WRONG in %.0f%%" % (100.0 * bad / len(nw))
    if ref is not None and eng.name != 'DRIK':
        diffs, expl, unexpl, ratios = [], [], [], []
        for r, d in zip(recs, ref):
            if r['tz'] == 0 or r['nak'] is None or d['nak'] is None or r['nak'][0] != d['nak'][0]: continue
            e = r['nak'][3] - d['nak'][3]                                  # hours, engine - drik, same nakshatra number
            x = circ(d['L'], r['L']) / (abs(d['speed']) if d['speed'] else 0.55)   # hours the Moon-position difference accounts for
            diffs.append(e); expl.append(x); unexpl.append(e - x); ratios.append((e - x) / r['tz'])
        if diffs:
            ok_share = sum(1 for z in ratios if abs(z) < 0.15) / len(ratios)
            print("  vs drik (tz != 0, same nakshatra number, %d cases): engine end - drik end = median %+.2f h; the two Moons' positions explain %+.2f h; "
                  "UNEXPLAINED %+.2f h = %.2f x tz (%.0f%% of cases within 0.15 x tz of zero)" % (len(diffs), st.median(diffs), st.median(expl), st.median(unexpl), st.median(ratios), 100 * ok_share))
            out['vs drik unexplained/tz'] = "%.2f x tz" % st.median(ratios)
    return out

def build_cases(Place, julian_day_number, full):
    places = [Place(*p) for p in (PLACES_FULL if full else PLACES_QUICK)]
    hours = HOURS_FULL if full else HOURS_QUICK; n = N_DATES_FULL if full else N_DATES_QUICK
    base = julian_day_number((2024, 1, 3), (0, 0, 0)); cases = []
    for p in places:
        for k in range(n):
            mid = local_midnight(base + 4.3 * k)
            for h in hours: cases.append((p, mid + h / 24.0, h))
    return cases

# ---------------------------------------------------------------------------------------------------------------
def load_test_py(here):
    p = os.path.join(here, 'test.py')
    if not os.path.exists(p): p = os.path.join(os.getcwd(), 'test.py')
    for d in (here, os.getcwd()):
        if d not in sys.path: sys.path.insert(0, d)       # test.py imports test_book_*.py that live beside it
    spec = importlib.util.spec_from_file_location('pyjhora_test_py', p); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T); return T

def main(argv):
    global MOON, SUN
    full = '--full' in argv; names = [a for a in argv if not a.startswith('--')] or ['SS', 'KK', 'GL', 'TS', 'VP', 'MS', 'VS']
    here = os.path.dirname(os.path.abspath(__file__)); T = load_test_py(here)
    from jhora import const, utils
    from jhora.panchanga import drik
    MOON, SUN = const._MOON, const._SUN
    mods = {'SS': T.surya_sidhantha, 'KK': T.khanda_khaadyaka, 'GL': T.graha_laaghavam, 'TS': T.tantra_sangraha, 'VP': T.vakya_panchanga,
            'MS': T.makaranda_sarini, 'DRIK': drik}
    try:
        from jhora.panchanga import vateshwara_sidhantha; mods['VS'] = vateshwara_sidhantha
    except Exception: pass
    def configure(name):
        def f():
            if name == 'VS':
                utils.set_language('en'); drik.set_ayanamsa_mode('LAHIRI')
                const.astrology_model_default = const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA; drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
            else:
                import io, contextlib
                with contextlib.redirect_stdout(io.StringIO()): T._configure(name)
        return f
    cases = build_cases(drik.Place, utils.julian_day_number, full)
    print("cases per engine:", len(cases), "| places:", sorted(set((c[0].name, c[0].timezone) for c in cases)))
    t0 = time.time()
    ref_eng = Engine('DRIK', drik, lambda t, p, place: drik.sidereal_longitude(t, p), configure('DRIK'))
    ref = collect(ref_eng, cases); report(ref_eng, ref)
    summary = {}
    for nm in names:
        if nm not in mods: print("\n(skipping %s: module not importable)" % nm); continue
        eng = Engine(nm, mods[nm], (lambda m: (lambda t, p, place: m.sidereal_longitude(t, p, place)))(mods[nm]), configure(nm))
        summary[nm] = report(eng, collect(eng, cases), ref)
    print("\n" + "=" * 100); print("SUMMARY (verdict per engine)   [%.0f s]" % (time.time() - t0))
    cols = ['nakshatra() end', 'raasi() end', 'tithi() end', 'yogam() end', 'raasi number', 'raasi fraction', 'next_tithi', 'nakshatra_new']
    print("%-6s " % "" + " ".join("%-17s" % c[:17] for c in cols))
    for nm, s in [('DRIK', report_quiet(ref_eng, ref))] + list(summary.items()):
        print("%-6s " % nm + " ".join("%-17s" % str(s.get(c, '-'))[:17] for c in cols))

def report_quiet(eng, recs):
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): return report(eng, recs)

if __name__ == '__main__':
    main(sys.argv[1:])
