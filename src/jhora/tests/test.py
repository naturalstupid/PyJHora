"""
SS vs KK vs GL vs TS vs VP vs MS vs VS vs drik comparison -- SEQUENTIAL (one full pass per engine) version.
Why sequential passes?
----------------
drik.set_planet_list(set_rahu_ketu_as_true_nodes=...) is GLOBAL state.
Setting it to False (mean nodes) for Surya Siddhanta/Khandakhadyaka/Graha
Laaghavam also forces drik to use mean nodes, which corrupts the drik side
of any side-by-side comparison. So instead of comparing feature-by-feature
in one run, we:
    PASS 1 : configure for SURYA SIDDHANTA (mean nodes)   -> run ALL tests, print
    PASS 2 : configure for KHANDAKHADYAKA (mean nodes)    -> run ALL tests, print
    PASS 3 : configure for GRAHA LAAGHAVAM (mean nodes)   -> run ALL tests, print
    PASS 4 : configure for DRIK            (true nodes)   -> run ALL tests, print
Every test function takes (engine, mod, ...) where:
    engine = 'SS', 'KK', 'GL', or 'DRIK'
    mod    = surya_sidhantha module, khanda_khaadyaka module, graha_laaghavam
             module, or drik module
and prints a single-engine result line, prefixed by the engine name.
Diff the four printed blocks afterwards to compare.
NOTE ON MODULE NAMING: this file imports jhora.panchanga.khanda_khaadyaka
and jhora.panchanga.graha_laaghavam, matching utils.get_hora_engine()'s
import path and const.ASTROLOGY_MODELS.KHANDA_KHAADYAKA /
const.ASTROLOGY_MODELS.GRAHA_LAAGHAVAM. Make sure both engine modules are
saved under those exact filenames, or these imports will fail. Likewise,
eclipse_kk.py must be saved under jhora.panchanga.eclipse_kk, and
eclipse_gl.py must be saved under jhora.panchanga.eclipse_gl. The same
applies to the MS (Makaranda Sarini) engine added in this file:
makaranda_sarini.py must be saved under jhora.panchanga.makaranda_sarini,
and eclipse_ms.py under jhora.panchanga.eclipse_ms, or the MS pass will
fail. The VS (Vateswara Siddhanta) engine is vateshwara_sidhantha.py under
jhora.panchanga.vateshwara_sidhantha (const.ASTROLOGY_MODELS.VATESHWARA_SIDHANTHA);
its eclipses are in eclipse_vs.py (jhora.panchanga.eclipse_vs), and test_book_eclipse_vs.py checks the numbers printed in Chapters IV and V
of the book. const.ASTROLOGY_MODELS.MAKARANDA_SARINI is looked up defensively
(getattr ... None) exactly like GRAHA_LAAGHAVAM/TANTRA_SANGRAHA/
VAKYA_PANCHANGAM above, so the MS pass still runs even if that enum member
does not exist yet in your installed const.py.
The SNT (Sphutanirnaya-tantra of Acyuta Pisharati) engine is sphuta_nirnaya_tantra.py under jhora.panchanga.sphuta_nirnaya_tantra
(const.ASTROLOGY_MODELS.SPHUTA_NIRNAYA_TANTRA). The book has no eclipse chapter, so BATCH 14 of the SNT pass runs eclipse_ts.py with the
label SNT, and no book-example tests are run for it.
GL-SPECIFIC CAVEAT (read before trusting GL's PASS 3 output):
GL's engine math (mean longitudes, manda/sighra equations, Tables
11.2/12.5/12.6) has been independently verified against the book's own
worked examples USING THE BOOK'S OWN (Cakra, Ahargana) PAIRS DIRECTLY --
see test_book_star_planets_11_4_12_10_gl() below. What has NOT been
independently verified in this sandbox (no live `jhora` install was
available to test against) is whether graha_laaghavam._GL_EPOCH_JD
correctly reproduces those same (Cakra, Ahargana) pairs when derived from
the ACTUAL CALENDAR DATES the book associates with them (Feb 5, 1962 and
Apr 3, 1996). test_book_star_planets_11_4_12_10_gl() includes an explicit
ahargana round-trip check for exactly this -- if it reports a MISMATCH,
the engine formulas above are still correct, but _GL_EPOCH_JD (or
const.mahabharatha_tithi_julian_day it's built from) needs adjustment.
GL eclipse functions (test_book_lunar_eclipse_9_9_gl() /
test_book_solar_eclipse_10_4_gl() below) are verified the same way --
by feeding eclipse_gl's formula chain the book's own stated inputs
directly (monkeypatching graha_laaghavam's longitude/speed/ascendant
functions), so they are independent of the _GL_EPOCH_JD question above.
"""
import inspect
import math
from jhora import const, utils
from jhora.panchanga import drik, surya_sidhantha, khanda_khaadyaka, graha_laaghavam, tantra_sangraha, vakya_panchanga, makaranda_sarini, vateshwara_sidhantha
from jhora.panchanga import sphuta_nirnaya_tantra
from test_book_vakya import run_vakya_book_tests   # the Vakyakarana book's worked examples (VP), one test per chapter topic
from test_book_eclipse_vp import run_eclipse_vp_tests   # Chapter IV (eclipses) of the same book + date-level checks of eclipse_vp.py
from test_book_mks import run_mks_book_tests   # the Makaranda Sarini's own worked example (MS), pp. 0072-0081
from test_book_eclipse_ms import run_eclipse_ms_tests   # eclipse_ms.py's book-example self-test (pp. 0083-0084) + date-level checks
from test_book_eclipse_vs import run_eclipse_vs_tests   # the numbers printed in Chapters IV and V of the Vateswara book (VS)
SS = 'SS'
KK = 'KK'
DRIK = 'DRIK'
GL = 'GL'
TS = 'TS'
VP = 'VP'
MS = 'MS'
VS = 'VS'
SNT = 'SNT'
# ---------------------------------------------------------------------
# formatting helpers
# ---------------------------------------------------------------------
def _fmt_dms(deg):
    if deg is None:
        return "     None     "
    d = int(deg)
    m = (deg - d) * 60
    mm = int(m)
    s = (m - mm) * 60
    return f"{d:3d}\u00b0 {mm:02d}' {s:05.2f}\""
def _dms(deg):
    """ Pretty-print a decimal-degree value as D°M'S" for easy comparison
        against the book's own D-M-S notation. """
    sign = '-' if deg < 0 else ''
    deg = abs(deg)
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return f"{sign}{d}\u00b0{m:02d}'{s:05.2f}\""
def _fmt_time(jd):
    if jd is None:
        return "   NOT FOUND   "
    frac = (jd + 0.5) % 1.0
    total_seconds = frac * 86400.0
    hh = int(total_seconds // 3600)
    mm = int((total_seconds % 3600) // 60)
    ss = total_seconds % 60
    return f"{hh:02d}:{mm:02d}:{ss:05.2f}"
def _banner(engine, title):
    print("=" * 80)
    print(f"[{engine}] {title}")
    print("=" * 80)
def _safe(func, *args, **kwargs):
    """Call func, returning 'ERROR: ...' string instead of raising."""
    if func is None:
        return "MISSING (function not found)"
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return f"ERROR: {e}"
def _bhava_method_kw(func):
    """
    SS/KK and drik name the bhava-method argument differently
    (e.g. 'bhava_madhya_method' vs 'bhava_method'). Find whichever keyword
    this module's bhaava_madhya() actually accepts.
    Returns the parameter name, or None if it takes no such keyword.
    """
    if func is None:
        return None
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        return None
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return 'bhava_madhya_method'
    for name in params:
        if 'method' in name.lower():
            return name
    return None
def _bhava_methods(mod):
    """Method codes this module supports; fall back to the SS list."""
    return getattr(mod, 'SUPPORTED_BHAVA_METHODS',
                   getattr(surya_sidhantha, 'SUPPORTED_BHAVA_METHODS', []))
def _rise_set_jd(engine, mod, func_name, jd, place):
    """
    drik, SS, and KK rise/set functions all return the SAME format:
    [float_hours, "HH:MM:SS" string, jd] -- take index 2 for all engines.
    Returns None if the function is missing, raises, or itself returns
    None (e.g. SS/KK moonrise/moonset when no crossing is found in the
    search window).
    """
    f = getattr(mod, func_name, None)
    if f is None:
        return None
    try:
        v = f(jd, place)
    except Exception:
        return None
    if v is None:
        return None
    try:
        return v[2]
    except (TypeError, IndexError):
        return v
# ---------------------------------------------------------------------
# MAIN BLOCK: panchanga basics, varga, bhava, retrograde, rise/set,
#             conjunctions, longitude tables
# ---------------------------------------------------------------------
def main(engine, mod, jd, dob, tob, place):
    _banner(engine, "PANCHANGA BASICS")
    print(f"[{engine}] tithi     = {_safe(getattr(mod,'tithi',None), jd, place)}")
    print(f"[{engine}] nakshatra = {_safe(getattr(mod,'nakshatra',None), jd, place)}")
    print(f"[{engine}] yogam     = {_safe(getattr(mod,'yogam',None), jd, place)}")
    print(f"[{engine}] karana    = {_safe(getattr(mod,'karana',None), jd, place)}")
    print()
    _banner(engine, "DHASAVARGA")
    pp = _safe(getattr(mod, 'dhasavarga', None), jd, place)
    if isinstance(pp, str):
        print(f"[{engine}] dhasavarga = {pp}")
    else:
        for p, (h, long) in pp:
            print(f"[{engine}] {p} {utils.RAASI_LIST[h]} {utils.to_dms(long, is_lat_long='plong')}")
    print()
    _banner(engine, "BHAAVA MADHYA (all supported methods)")
    bm_func = getattr(mod, 'bhaava_madhya', None)
    bm_kw = _bhava_method_kw(bm_func)
    if bm_func is None:
        print(f"[{engine}] bhaava_madhya = MISSING (function not found)")
    elif bm_kw is None:
        # module exposes no method selector -- call it plain, once
        print(f"[{engine}] Bhava Method <default> = {_safe(bm_func, jd, place)}")
    else:
        print(f"[{engine}] (bhava method kwarg = '{bm_kw}')")
        for bm in _bhava_methods(mod):
            print(f"[{engine}] Bhava Method {bm} = "
                  f"{_safe(bm_func, jd, place, **{bm_kw: bm})}")
    print()
    _banner(engine, "NEXT PLANET RETROGRADE CHANGE (Saturn)")
    planet = const._SATURN
    ncp = _safe(getattr(mod, 'next_planet_retrograde_change_date', None), planet, dob, place)
    if isinstance(ncp, str):
        print(f"[{engine}] next planet retro = {ncp}")
    else:
        y, m, d, fh = utils.jd_to_gregorian(ncp[0])
        print(f"[{engine}] next planet retro {y} {m} {d} {utils.to_dms(fh)} "
              f"{utils.deg_to_sign_str(ncp[1])}")
    print()
    _banner(engine, "RISE / SET + CONJUNCTIONS (birth jd)")
    sr = _rise_set_jd(engine, mod, 'sunrise', jd, place)
    if sr is not None:
        y, m, d, fh = utils.jd_to_gregorian(sr)
        print(f"[{engine}] sunrise  {y} {m} {d} {utils.to_dms(fh)}")
    se = _rise_set_jd(engine, mod, 'sunset', jd, place)
    if se is not None:
        y, m, d, fh = utils.jd_to_gregorian(se)
        print(f"[{engine}] sunset   {y} {m} {d} {utils.to_dms(fh)}")
    mr = _rise_set_jd(engine, mod, 'moonrise', jd, place)
    if mr is not None:
        y, m, d, fh = utils.jd_to_gregorian(mr)
        print(f"[{engine}] moonrise {y} {m} {d} {utils.to_dms(fh)}")
    ms = _rise_set_jd(engine, mod, 'moonset', jd, place)
    if ms is not None:
        y, m, d, fh = utils.jd_to_gregorian(ms)
        print(f"[{engine}] moonset  {y} {m} {d} {utils.to_dms(fh)}")
    for cj_label, p1, sep in (("Sun/Lagna/180", const._SUN, 180),
                              ("Sun/Lagna/0", const._SUN, 0),
                              ("Moon/Lagna/0", const._MOON, 0),
                              ("Moon/Lagna/180", const._MOON, 180)):
        f = getattr(mod, 'next_conjunction_of_planet_pair', None)
        ncp = _safe(f, jd, place, p1, 'L', separation_angle=sep) if sep else \
              _safe(f, jd, place, p1, 'L')
        if isinstance(ncp, str):
            print(f"[{engine}] {cj_label:16s} {ncp}")
        else:
            y, m, d, fh = utils.jd_to_gregorian(ncp[0])
            print(f"[{engine}] {cj_label:16s} {y} {m} {d} {utils.to_dms(fh)} "
                  f"{utils.deg_to_sign_str(ncp[1])}")
    # -----------------------------------------------------------------
    # Multi-location longitude table
    # -----------------------------------------------------------------
    test_cases = [
        ("Chicago, 10-Jan-2016 00:00", drik.Place('Chicago', 41.8781, -87.6298, -6.0),
         drik.Date(2016, 1, 10), (0, 0, 0)),
        ("Bangalore, 21-Mar-1997 midnight", drik.Place('Bangalore', 12.9716, 77.5946, 5.5),
         drik.Date(1997, 3, 21), (0, 0, 0)),
        ("Hoffman Estates, 15-Sep-2026 19:00", drik.Place('Hoffman Estates', 42.0625, -88.1449, -5.0),
         drik.Date(2026, 9, 15), (19, 0, 0)),
        ("Kali Yuga, 22-Jan-(-3101) 12:00", drik.Place('Ujjain', 23 + 11 / 60, 75 + 46 / 60, 5.5),
         drik.Date(-3101, 1, 22), (12, 0, 0)),
    ]
    bodies = [
        ('Sun', const._SUN), ('Moon', const._MOON), ('Mars', const._MARS),
        ('Mercury', const._MERCURY), ('Jupiter', const._JUPITER),
        ('Venus', const._VENUS), ('Saturn', const._SATURN),
        ('Rahu', const._RAHU), ('Ketu', const._KETU),
        ('Lagna', 'L'),
    ]
    print()
    _banner(engine, "PLANETARY LONGITUDES + LAGNA")
    for label, tc_place, tc_dob, tc_tob in test_cases:
        tc_jd = utils.julian_day_number(tc_dob, tc_tob)
        tc_jd_utc = tc_jd - tc_place.timezone / 24.0
        print("-" * 60)
        print(f"[{engine}] {label}")
        print("-" * 60)
        header = f"{'Body':9s}{engine:>22s}"
        print(header)
        for body_name, body in bodies:
            # SS and KK both need an explicit `place` argument passed
            # through (desantara/timezone correction); drik's
            # sidereal_longitude/ascendant do not take place for the
            # longitude call (place is baked into jd_utc already).
            if body == 'L':
                if engine == DRIK:
                    asc = _safe(drik.ascendant, tc_jd, tc_place)
                else:
                    asc = _safe(mod.ascendant, tc_jd, tc_place)
                val = None if isinstance(asc, str) else asc[0] * 30 + asc[1]
            else:
                if engine == DRIK:
                    if body == const._KETU:   # FIX: swisseph has no Ketu body -> Rahu + 180
                        r = _safe(drik.sidereal_longitude, tc_jd_utc, const._RAHU)
                        val = r if isinstance(r, str) else (r + 180.0) % 360.0
                    else:
                        val = _safe(drik.sidereal_longitude, tc_jd_utc, body)
                else:
                    val = _safe(mod.sidereal_longitude, tc_jd_utc, body, tc_place)
                if isinstance(val, str):
                    val = None
            print(f"{body_name:9s}{_fmt_dms(val):>22s}")
        print()
    print()
    _banner(engine, "SUNRISE / SUNSET / MOONRISE / MOONSET")
    for label, tc_place, tc_dob, tc_tob in test_cases:
        tc_jd = utils.julian_day_number(tc_dob, tc_tob)
        print("-" * 60)
        print(f"[{engine}] {label}")
        print("-" * 60)
        print(f"[{engine}] Sunrise : {_fmt_time(_rise_set_jd(engine, mod, 'sunrise', tc_jd, tc_place))}")
        print(f"[{engine}] Sunset  : {_fmt_time(_rise_set_jd(engine, mod, 'sunset', tc_jd, tc_place))}")
        print(f"[{engine}] Moonrise: {_fmt_time(_rise_set_jd(engine, mod, 'moonrise', tc_jd, tc_place))}")
        print(f"[{engine}] Moonset : {_fmt_time(_rise_set_jd(engine, mod, 'moonset', tc_jd, tc_place))}")
# ---------------------------------------------------------------------
# BATCH 5: upagrahas + special lagnas
# ---------------------------------------------------------------------
def test_batch5(engine, mod, jd, place, dob, tob):
    _banner(engine, "BATCH 5a: SOLAR UPAGRAHAS")
    if engine == DRIK:
        sun_long = _safe(drik.sidereal_longitude, jd - place.timezone / 24.0, const._SUN)
    else:
        sun_long = _safe(mod.sidereal_longitude, jd - place.timezone / 24.0, const._SUN, place)
    print(f"[{engine}] sun_long = {sun_long}")
    for name in const.sub_planet_list_2:
        val = _safe(getattr(mod, 'solar_upagraha_longitudes', None), sun_long, upagraha=name)
        label = utils.resource_strings.get(name + "_str", name)
        print(f"[{engine}] {label:20s} = {val}")
    print()
    _banner(engine, "BATCH 5b: OTHER (TIME-BASED) UPAGRAHAS")
    for label_key, func_name in const.sub_planet_dict_1.items():
        func = getattr(mod, func_name, None)
        label = utils.resource_strings.get(label_key, label_key)
        print(f"[{engine}] {label:20s} = {_safe(func, dob, tob, place)}")
    print()
    _banner(engine, "BATCH 5c: SPECIAL LAGNAS")
    for name in const._special_lagna_list:
        lookup_name = name if name != 'bhrigu_bindhu' else 'bhrigu_bindhu_lagna'
        label = utils.resource_strings.get(name + "_str", name)
        if name in ('varnada_lagna',):
            print(f"[{engine}] {label:20s} SKIPPED (lives in charts.py, different signature)")
            continue
        print(f"[{engine}] {label:20s} = {_safe(getattr(mod, lookup_name, None), jd, place)}")
# ---------------------------------------------------------------------
# BATCH 6: sankranti / solar calendar
# ---------------------------------------------------------------------
def test_batch6(engine, mod, panchanga_date, place):
    _banner(engine, "BATCH 6: SANKRANTI / SOLAR-CALENDAR")
    for label in ("previous_sankranti_date", "next_sankranti_date",
                  "tamil_solar_month_and_date", "days_in_tamil_month"):
        print(f"[{engine}] {label:28s} = {_safe(getattr(mod, label, None), panchanga_date, place)}")
    jd = utils.gregorian_to_jd(panchanga_date)
    print(f"[{engine}] {'solar_month_date':28s} = "
          f"{_safe(getattr(mod,'solar_month_date',None), jd, place)}")
# ---------------------------------------------------------------------
# BATCH 7: weekday + kaala vibhaga
# ---------------------------------------------------------------------
def test_batch7(engine, mod, jd, place):
    _banner(engine, "BATCH 7: WEEKDAY + KAALA-VIBHAGA")
    simple_funcs = ("vaara", "trikalam", "raahu_kaalam", "yamaganda_kaalam", "gulikai_kaalam",
                    "durmuhurtam", "abhijit_muhurta", "gauri_choghadiya", "amrit_kaalam",
                    "shubha_hora", "brahma_muhurtha", "godhuli_muhurtha", "sandhya_periods",
                    "vijaya_muhurtha", "nishita_kaala", "nishita_muhurtha", "tamil_jaamam",
                    "muhurthas")
    for label in simple_funcs:
        print(f"[{engine}] {label:20s} = {_safe(getattr(mod, label, None), jd, place)}")
    print(f"[{engine}] {'civil_weekday':20s} = {_safe(getattr(mod,'civil_weekday',None), jd)}")
# ---------------------------------------------------------------------
# BATCH 8: panchaka / chandrabalam / thaaraabalam
# ---------------------------------------------------------------------
def test_batch8(engine, mod, jd, place):
    _banner(engine, "BATCH 8: PANCHAKA / CHANDRABALAM / THAARAABALAM")
    for label in ("udhaya_lagna_muhurtha", "thaaraabalam", "chandrabalam",
                  "panchaka_rahitha", "next_panchaka_days", "chandrashtama"):
        print(f"[{engine}] {label:24s} = {_safe(getattr(mod, label, None), jd, place)}")
# ---------------------------------------------------------------------
# BATCH 9: lunar calendar core
# ---------------------------------------------------------------------
def test_batch9(engine, mod, jd, place):
    _banner(engine, "BATCH 9: LUNAR CALENDAR CORE")
    ti = _safe(getattr(mod, 'tithi', None), jd, place)
    ti = ti[0] if not isinstance(ti, str) else None
    print(f"[{engine}] tithi[0] = {ti}")
    # new_moon()/full_moon() signatures now match across drik/SS/KK
    # (jd, place, tithi_, opt) -- call generically via mod.
    new_moon_call = lambda: mod.new_moon(jd, place, ti, -1)
    full_moon_call = lambda: mod.full_moon(jd, place, ti, -1)
    for label, call in (
        ("new_moon", new_moon_call),
        ("full_moon", full_moon_call),
        ("lunar_month", lambda: mod.lunar_month(jd, place)),
        ("lunar_month_date", lambda: mod.lunar_month_date(jd, place)),
        ("next_lunar_month", lambda: mod.next_lunar_month(jd, place)),
        ("previous_lunar_month", lambda: mod.previous_lunar_month(jd, place)),
        ("next_lunar_year", lambda: mod.next_lunar_year(jd, place)),
        ("previous_lunar_year", lambda: mod.previous_lunar_year(jd, place)),
    ):
        print(f"[{engine}] {label:22s} = {_safe(call)}")
    py, pm, pd, _ = utils.jd_to_gregorian(jd)
    pdate = drik.Date(py, pm, pd)
    print(f"[{engine}] {'samvatsara':22s} = {_safe(getattr(mod,'samvatsara',None), pdate, place)}")
    for maasa in (1, 6):
        print(f"[{engine}] {'ritu(' + str(maasa) + ')':22s} = {_safe(getattr(mod,'ritu',None), maasa)}")
    print(f"[{engine}] {'vedic_date(SOLAR)':22s} = "
          f"{_safe(getattr(mod,'vedic_date',None), jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)}")
# ---------------------------------------------------------------------
# BATCH 10: misc yoga / muhurta flags
# ---------------------------------------------------------------------
def test_batch10(engine, mod, jd, place):
    _banner(engine, "BATCH 10: MISC YOGA / MUHURTA FLAGS")
    simple_funcs = ("tamil_yogam", "anandhaadhi_yoga", "triguna", "vivaha_chakra_palan",
                    "amrita_gadiya", "varjyam", "shiva_vaasa", "agni_vaasa", "pushkara_yoga",
                    "aadal_yoga", "vidaal_yoga", "disha_shool", "yogini_vaasa",
                    "fraction_moon_yet_to_traverse", "vedic_time", "midday", "midnight",
                    "graha_drekkana", "is_night_birth")
    for label in simple_funcs:
        print(f"[{engine}] {label:24s} = {_safe(getattr(mod, label, None), jd, place)}")
    for label, call in (
        ("nava_thaara('L')", lambda: mod.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol)),
        ("special_thaara('L')", lambda: mod.special_thaara(jd, place, base_star_planet=const._ascendant_symbol)),
        ("nava_thaara(default)", lambda: mod.nava_thaara(jd, place)),
    ):
        print(f"[{engine}] {label:24s} = {_safe(call)}")
    print(f"[{engine}] {'sahasra_chandrodayam':24s} = "
          f"{_safe(getattr(mod,'sahasra_chandrodayam',None), jd, place)}")
    st = _safe(getattr(mod, 'special_tithis', None), jd, place)
    print(f"[{engine}] {'special_tithis[0][0]':24s} = "
          f"{st if isinstance(st, str) else st[0][0]}")
# ---------------------------------------------------------------------
# BATCH 11: year-length / dasha support
# ---------------------------------------------------------------------
def test_batch11(engine, mod, jd, place):
    _banner(engine, "BATCH 11: YEAR-LENGTH / DASHA SUPPORT")
    for label in ("true_sidereal_year", "lunar_year", "savana_year", "tithi_year",
                  "true_tithi_year", "true_lunar_year", "true_tropical_year"):
        print(f"[{engine}] {label:20s} = {_safe(getattr(mod, label, None), jd, place)}")
    for dd_name in ("MEAN_SIDEREAL_YEAR", "TRUE_SIDEREAL_YEAR", "SAVANA_YEAR",
                    "MEAN_LUNAR_YEAR", "TRUE_LUNAR_YEAR", "GREGORIAN_YEAR",
                    "TRUE_TROPICAL_YEAR"):
        dd = getattr(const.DHASA_YEAR_DURATION, dd_name)
        print(f"[{engine}] dhasa_year_duration({dd_name}) = "
              f"{_safe(getattr(mod,'dhasa_year_duration',None), dd, jd, place)}")
        const.dhasa_year_duration_default = dd
        start = _safe(getattr(mod, '_get_dhasa_start_jd', None), jd, place, 0.5, 10)
        end = _safe(getattr(mod, '_get_dhasa_end_jd', None), jd, place, 10)
        start_s = start if isinstance(start, str) else utils.jd_to_gregorian(start)
        end_s = end if isinstance(end, str) else utils.jd_to_gregorian(end)
        print(f"[{engine}]   start/end jd [{dd_name}] = ({start_s}, {end_s})")
# ---------------------------------------------------------------------
# BATCH 12: misc utility / wrappers
# ---------------------------------------------------------------------
def test_batch12(engine, mod, jd, place, dob, tob):
    _banner(engine, "BATCH 12: MISC UTILITY / WRAPPERS")
    for label in ("planets_in_retrograde", "planets_in_stationary", "ascendant_speed",
                  "next_solar_month", "previous_solar_month", "next_solar_year",
                  "previous_solar_year", "ardra_pravesha_date"):
        print(f"[{engine}] {label:28s} = {_safe(getattr(mod, label, None), jd, place)}")
    print(f"[{engine}] {'next_solar_date(yrs=5)':28s} = "
          f"{_safe(getattr(mod,'next_solar_date',None), jd, place, years=5)}")
    print(f"[{engine}] {'next_annual_solar_date_approx':28s} = "
          f"{_safe(getattr(mod,'next_annual_solar_date_approximate',None), dob, tob, 5)}")
    print(f"[{engine}] {'declination_of_planets':28s} = "
          f"{_safe(getattr(mod,'declination_of_planets',None), jd, place)}")
    for label in ("kaala_longitude", "mrityu_longitude", "artha_praharaka_longitude",
                  "yama_ghantaka_longitude", "gulika_longitude", "maandi_longitude",
                  "kaala_raw", "mrityu_raw", "artha_praharaka_raw",
                  "yama_ghantaka_raw", "gulika_raw", "maandi_raw"):
        print(f"[{engine}] {label:28s} = {_safe(getattr(mod, label, None), dob, tob, place)}")
    print(f"[{engine}] {'navamsa_from_long(123.4)':28s} = "
          f"{_safe(getattr(mod,'navamsa_from_long',None), 123.4)}")
    print(f"[{engine}] {'ketu(55.0)':28s} = {_safe(getattr(mod,'ketu',None), 55.0)}")
# ---------------------------------------------------------------------
# BATCH 13: karaka tithi/yogam + tamil solar month variants
# ---------------------------------------------------------------------
def test_batch13(engine, mod, jd, place):
    _banner(engine, "BATCH 13: KARAKA TITHI/YOGAM + TAMIL SOLAR MONTH VARIANTS")
    for label in ("karaka_tithi", "karaka_yogam"):
        print(f"[{engine}] {label:28s} = {_safe(getattr(mod, label, None), jd, place)}")
    py, pm, pd, _ = utils.jd_to_gregorian(jd)
    pdate = drik.Date(py, pm, pd)
    for label in ("tamil_solar_month_and_date", "tamil_solar_month_and_date_new",
                  "tamil_solar_month_and_date_V4_3_8", "tamil_solar_month_and_date_V4_3_5",
                  "tamil_solar_month_and_date_RaviAnnnaswamy"):
        print(f"[{engine}] {label:42s} = {_safe(getattr(mod, label, None), pdate, place)}")
    for method_name in ("BASED_ON_LOCAL_10AM", "BASED_ON_SUNSET_TIME", "BASED_ON_BIRTH_TIME"):
        method = getattr(const.TAMIL_MONTH_METHOD, method_name, None)
        if method is None:
            print(f"[{engine}] tamil_solar_month_and_date({method_name}) "
                  f"SKIPPED: const.TAMIL_MONTH_METHOD.{method_name} not found")
            continue
        print(f"[{engine}] tamil_solar_month_and_date({method_name}) = "
              f"{_safe(getattr(mod,'tamil_solar_month_and_date',None), pdate, place, tamil_month_method=method)}")
# ---------------------------------------------------------------------
# BATCH 14: eclipses  (eclipse_ss.py for SS, eclipse.py for drik,
#           eclipse_kk.py for KK, eclipse_gl.py for GL)
# ---------------------------------------------------------------------
def _fmt(ymdfh):
    if ymdfh is None:
        return "N/A"
    y, m, d, fh = ymdfh
    h, mi, s = utils.to_dms(fh, as_string=False)
    return f"{y:04d}-{m:02d}-{d:02d} {int(h):02d}:{int(mi):02d}:{int(round(s)):02d}"

## V5.0 -- regression test for sankranti timezone-double-count + date-rollback bugs (fixed this session)
def test_sankranti_consistency(engine, mod, place):
    _banner(engine, "SANKRANTI CONSISTENCY (next/previous_sankranti_date vs tamil_solar_month_and_date)")
    next_fn = getattr(mod, 'next_sankranti_date', None)
    prev_fn = getattr(mod, 'previous_sankranti_date', None)
    tmd_fn = getattr(mod, 'tamil_solar_month_and_date', None)
    if next_fn is None or prev_fn is None or tmd_fn is None:
        print(f"[{engine}] SKIPPED: missing next_sankranti_date/previous_sankranti_date/"
              f"tamil_solar_month_and_date")
        return
    rules = []
    for rule_name, gh in (("TAMIL_NADU_SUNSET_RULE", None), ("BEFORE_GHATIKAS", 13),
                          ("SUNRISE_TO_SUNRISE", None)):
        rule = getattr(const.SANKRANTI_RULE, rule_name, None)
        if rule is not None:
            rules.append((rule_name, rule, gh))
    test_dates = [drik.Date(y, m, 15) for y in (1996, 2005, 2016, 2026) for m in (1, 4, 7, 10)]
    total = 0
    mismatches = []
    for pdate in test_dates:
        for rule_name, rule, gh in rules:
            total += 1
            try:
                nsd = next_fn(pdate, place, sankranti_rule=rule, ghatikas=gh)
                psd = prev_fn(pdate, place, sankranti_rule=rule, ghatikas=gh)
            except Exception as e:
                mismatches.append(f"{pdate} rule={rule_name}: ERROR next/previous_sankranti_date: {e}")
                continue
            try:
                tm_next = tmd_fn(nsd[0], place, sankranti_rule=rule, ghatikas=gh)
                tm_prev = tmd_fn(psd[0], place, sankranti_rule=rule, ghatikas=gh)
            except Exception as e:
                mismatches.append(f"{pdate} rule={rule_name}: ERROR tamil_solar_month_and_date: {e}")
                continue
            if tm_next[1] != 1:
                mismatches.append(f"{pdate} rule={rule_name}: next={nsd} tamil_month_date(next)={tm_next} (expected day=1)")
            if tm_prev[1] != 1:
                mismatches.append(f"{pdate} rule={rule_name}: prev={psd} tamil_month_date(prev)={tm_prev} (expected day=1)")
            if (psd[2] + 1) % 12 != nsd[2]:
                mismatches.append(f"{pdate} rule={rule_name}: month sequence mismatch prev={psd[2]} next={nsd[2]}")
    print(f"[{engine}] Total checks: {total}   Mismatches: {len(mismatches)}")
    for m in mismatches:
        print(f"[{engine}]   MISMATCH: {m}")

def test_book_lunar_eclipse_9_7():
    """
    Book Section 9.7 -- Lunar eclipse, September 27, 1996 (per SS).
    Book's own SS-method result (Local Mean Time):
        Beginning of the eclipse   : 6h 42m
        Beginning of totality      : 7h 49m
        Middle of the eclipse      : 8h 24m
        End of totality            : 8h 59m
        End of the eclipse         : 10h 06m
    Book notes this matches the Indian Astronomical Ephemeris exactly,
    since true longitudes (not book's own approximate mean/manda
    positions) were used as the STARTING point for this specific
    worked example (see book text: "we use the true longitudes of the
    sun, moon etc., from the Ind. Ast. Eph. ... However the procedure
    of SS is adopted.").
    """
    from jhora.panchanga import eclipse, eclipse_ss
    print("=" * 70)
    print("BOOK TEST 1: Lunar eclipse, September 27, 1996 (Section 9.7, SS method)")
    print("=" * 70)
    dob = drik.Date(1996, 9, 27)
    tob = (5, 30, 0)  # 5:30 AM IST, book's stated starting instant
    place = drik.Place('Reference,IN', 23.18, 75.77, 5.5)  # Ujjayini-style ref meridian
    jd = utils.julian_day_number(dob, tob)
    result = eclipse_ss.next_lunar_eclipse(jd, place, search_backward=False)
    if result is None:
        print("SS engine: NO eclipse found within search window.")
    else:
        type_str, (begin, middle, end) = result
        print(f"SS engine result ({type_str}):")
        print(f"  Begin : {_fmt(begin)}")
        print(f"  Middle: {_fmt(middle)}")
        print(f"  End   : {_fmt(end)}")
    print()
    print("Book's stated SS-method result (LMT):")
    print("  Beginning of eclipse : 06:42:00")
    print("  Beginning of totality: 07:49:00")
    print("  Middle of eclipse    : 08:24:00")
    print("  End of totality      : 08:59:00")
    print("  End of eclipse       : 10:06:00")
    print()
    drik_result = eclipse.next_lunar_eclipse(
        jd, place, eclipse_location_type=eclipse.EclipseLocation.GLOBAL,
        lunar_eclipse_type=eclipse.LunarEclipseType.ANY)
    if drik_result:
        type_str, times = drik_result
        print(f"drik (swisseph) engine result ({type_str}):")
        labels = ["Penumbral begin", "Partial begin", "Max (middle)", "Partial end", "Penumbral end"]
        for label, t in zip(labels, times):
            print(f"  {label:16s}: {_fmt(t)}")
    print()
def test_book_solar_eclipse_10_3():
    """
    Book Section 10.3 -- Solar eclipse, October 24, 1995, at Bangalore
    (12N58', 77E35') (per SS).
    Book's own SS-method result (nadis converted to LMT... book gives
    directly in nadis/vinadis with H-M-S conversion at each step):
        Beginning of the eclipse : 10 nadi 1 vinadi  = 8h 00m 35s
        Middle of the eclipse    : 22 nadi 21 vinadi = 8h 58m 36s
        End of the eclipse       : 24 nadi 41 vinadi = 9h 52m 25s
    Magnitude (pramanam): 0.5994744 (partial eclipse).
    NOTE: this module's next_solar_eclipse() currently reports
    begin/end as placeholders equal to middle (see eclipse_ss.py
    docstring) -- only MIDDLE (the apparent-conjunction instant, fully
    analytically verified against the book's own parallax-chain
    numbers) is meaningful to compare here until the half-duration
    formula is separately validated and wired in.
    """
    from jhora.panchanga import eclipse, eclipse_ss
    rao_book_example_diagnostic_test()
    print("=" * 70)
    print("BOOK TEST 2: Solar eclipse, October 24, 1995, Bangalore (Section 10.3, SS method)")
    print("=" * 70)
    dob = drik.Date(1995, 10, 24)
    tob = (5, 30, 0)  # 5:30 AM IST, book's stated starting instant
    place = drik.Place('Bangalore,IN', 12 + 58/60, 77 + 35/60, 5.5)
    jd = utils.julian_day_number(dob, tob)
    result = eclipse_ss.next_solar_eclipse(jd, place, search_backward=False)
    if result is None:
        print("SS engine: NO eclipse found within search window.")
    else:
        type_str, (begin, middle, end) = result
        print(f"SS engine result ({type_str}):")
        print(f"  Begin  (placeholder = middle): {_fmt(begin)}")
        print(f"  Middle (analytically verified): {_fmt(middle)}")
        print(f"  End    (placeholder = middle): {_fmt(end)}")
    print()
    print("Book's stated SS-method result (LMT):")
    print("  Beginning of eclipse : 08:00:35")
    print("  Middle of eclipse    : 08:58:36  <-- compare SS 'Middle' against this")
    print("  End of eclipse       : 09:52:25")
    print("  Magnitude (pramanam) : 0.5994744 (partial)")
    print()
    drik_result = eclipse.next_solar_eclipse(
        jd, place, eclipse_location_type=eclipse.EclipseLocation.LOCAL,
        solar_eclipse_type=eclipse.SolarEclipseType.ANY)
    if drik_result:
        type_str, times = drik_result
        print(f"drik (swisseph) engine result ({type_str}):")
        labels = ["First contact", "Max (middle)", "Last contact"]
        for label, t in zip(labels, times):
            print(f"  {label:16s}: {_fmt(t)}")
    print()
def test_book_lunar_eclipse_9_8_kk():
    """
    Book Section 9.8 -- Lunar eclipse, December 10, 1992, according to KK
    (Khandakhadyaka), at Ujjayini.
    Book's own KK-method result (Local Mean Time at Ujjayini), VERIFIED
    by independently reproducing the book's own half-duration arithmetic
    (opposition +/- each half-duration reproduces every stated time to
    the second) -- and now also reproduced by eclipse_kk.py's own
    iterative contact refinement (_kk_lunar_contact_half_durations),
    which implements this exact method (fixed MDM/SDM/diameters at
    opposition, re-evaluate only the moon-Rahu angle at each trial
    instant, Rahu extrapolated at its classical mean rate):
        Instant of opposition (middle) : 03:51:51
        Beginning of the eclipse       : 02:08:25
        Beginning of the totality      : 03:17:57
        End of the totality            : 04:30:52
        End of the eclipse             : 05:40:22
    Book's own inputs at the preceding midnight (for reference, not
    reproduced by this test): true Sun=233d48'23", true Moon=51d50'35",
    true Rahu=237d13'58", SDM=61'13", MDM=792'53".
    """
    from jhora.panchanga import eclipse_kk
    print("=" * 70)
    print("BOOK TEST 3: Lunar eclipse, December 10, 1992 (Section 9.8, KK method)")
    print("=" * 70)
    dob = drik.Date(1992, 12, 11)
    tob = (0, 0, 0)  # book computes from "the preceding midnight"
    place = drik.Place('Ujjayini,IN', 23 + 11/60, 75 + 47/60, 5.5)
    jd = utils.julian_day_number(dob, tob)
    result = eclipse_kk.next_lunar_eclipse(jd, place, search_backward=True)
    if result is None:
        print("KK engine: NO eclipse found within search window.")
    else:
        type_str, events = result
        print(f"KK engine result ({type_str}):")
        if len(events) == 5:
            begin, totality_begin, middle, totality_end, end = events
            print(f"  Begin           : {_fmt(begin)}")
            print(f"  Totality begin  : {_fmt(totality_begin)}")
            print(f"  Middle          : {_fmt(middle)}")
            print(f"  Totality end    : {_fmt(totality_end)}")
            print(f"  End             : {_fmt(end)}")
        else:
            begin, middle, end = events
            print(f"  Begin : {_fmt(begin)}")
            print(f"  Middle: {_fmt(middle)}")
            print(f"  End   : {_fmt(end)}")
    print()
    print("Book's stated KK-method result (LMT at Ujjayini):")
    print("  Beginning of eclipse  : 02:08:25")
    print("  Beginning of totality : 03:17:57")
    print("  Middle of eclipse     : 03:51:51")
    print("  End of totality       : 04:30:52")
    print("  End of eclipse        : 05:40:22")
    print()
def test_book_solar_eclipse_10_5_kk():
    """
    Book Section 10.5 -- Solar eclipse, January 5, 1992, at Bangalore,
    according to KK (Khandakhadyaka).
    Book's own KK-method result, as stated in its "Summary of the solar
    eclipse" (times appear to be IST clock time; the book's OCR'd
    arithmetic in this section was partially garbled -- the values below
    are the book's own final stated summary line, NOT independently
    re-derived from the intermediate steps the way the 9.8 KK lunar
    example was. Treat this as the book's claimed result pending a
    cleaner re-check of the intermediate steps if a discrepancy shows up):
        Beginning of the eclipse : Jan 4, 1992, 23:35:10 (night before)
        Time of apparent conjn.  : Jan 5, 1992, 00:31:22  (middle)
        End of the eclipse       : Jan 5, 1992, 01:19:36
        Duration                 : 1h 44m 26s
    Book's own inputs (preceding midnight): KK Ahargana=4,84,596; true
    Sun=259d38'18", true Moon=259d17'44", Rahu=255d15'05",
    SDM=61'26", MDM=731'41".
    NOTE: Begin/End are no longer placeholders -- eclipse_kk.py now computes
    them via _kk_solar_contact_half_durations(), which applies the book's
    own general half-duration method (Sec. 9.8's formula) to the solar case
    (sun+moon semi-diameters, parallax-corrected latitude, re-evaluating the
    lambana/nati parallax chain at each trial instant). UNLIKE the 9.8 lunar
    refinement, this solar extension has NOT been independently verified
    against the book's own Sec. 10.5 intermediate arithmetic -- only Ch. 9.8
    was available as source material here, and the book's own summary line
    above is itself flagged (per this docstring) as imperfectly OCR'd.
    """
    from jhora.panchanga import eclipse_kk
    print("=" * 70)
    print("BOOK TEST 4: Solar eclipse, January 5, 1992, Bangalore (Section 10.5, KK method)")
    print("=" * 70)
    dob = drik.Date(1992, 1, 4)
    tob = (0, 0, 0)  # book computes from "the preceding midnight"
    place = drik.Place('Bangalore,IN', 12 + 58/60, 77 + 35/60, 5.5)
    jd = utils.julian_day_number(dob, tob)
    result = eclipse_kk.next_solar_eclipse(jd, place, search_backward=False)
    if result is None:
        print("KK engine: NO eclipse found within search window.")
    else:
        type_str, (begin, middle, end) = result
        print(f"KK engine result ({type_str}):")
        print(f"  Begin  (computed, unverified vs. book): {_fmt(begin)}")
        print(f"  Middle (apparent conjunction)         : {_fmt(middle)}")
        print(f"  End    (computed, unverified vs. book): {_fmt(end)}")
    print()
    print("Book's stated KK-method result (IST, IMPERFECTLY OCR'd -- see docstring):")
    print("  Beginning of eclipse (night of Jan 4): 23:35:10")
    print("  Middle (apparent conjunction, Jan 5) : 00:31:22")
    print("  End of eclipse (Jan 5)                : 01:19:36")
    print()
def _gl_dms(deg):
    """ Pretty-print a decimal-degree value as D°M'S", matching the book's
        own D-M-S notation (reused locally to avoid import-order issues
        with the module-level _dms() helper above). """
    sign = '-' if deg < 0 else ''
    deg = abs(deg) % 360
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return f"{sign}{d}\u00b0{m:02d}'{s:05.2f}\""
def test_book_star_planets_11_4_12_10_gl():
    """
    Book Sections 11.4 and 12.10 -- Graha Laaghavam (GL) star-planet
    mean/true longitudes, using the book's own TWO independent worked
    examples:
        Example A (Sec 11.4): Cakras=40, Ahargana=744 (Feb 5, 1962)
        Example B (Sec 12.10): Cakras=43, Ahargana=1173 (Apr 3, 1996)
    This test has TWO parts:
      PART 1 -- ENGINE MATH CHECK (the part that's been fully verified):
        Calls graha_laaghavam's internal engine functions directly with
        the book's own stated (Cakra, Ahargana) pairs (bypassing any
        jd/epoch derivation), confirming the mean-longitude formulas
        (Ch 11.4, Table 11.2) and the full manda/sighra true-longitude
        refinement (Ch 12.10, Tables 12.5/12.6) reproduce the book to
        within arcseconds.
      PART 2 -- EPOCH ROUND-TRIP CHECK (NOT yet independently verified
        in this sandbox -- see module docstring's GL-SPECIFIC CAVEAT):
        Calls graha_laaghavam.kali_ahargana_days() on the REAL calendar
        dates the book associates with each example, and checks whether
        the resulting (Cakra, Ahargana) split matches the book's own
        stated values. If this reports MISMATCH, _GL_EPOCH_JD (or the
        const.mahabharatha_tithi_julian_day it's built from) needs
        adjustment -- the Part 1 engine math itself is unaffected.
    """
    print("=" * 78)
    print("BOOK TEST 5: Graha Laaghavam star-planet mean/true longitudes")
    print("             (Sections 11.4 and 12.10)")
    print("=" * 78)
    # -------------------------------------------------------------
    # PART 1: engine math, fed the book's own (Cakra, Ahargana) directly
    # -------------------------------------------------------------
    print("\n--- PART 1: ENGINE MATH (book's own Cakra/Ahargana fed directly) ---")
    orig_cakra_ahargana = graha_laaghavam._gl_cakra_ahargana
    examples = [
        ("Example A (Sec 11.4, Feb 5 1962): C=40, A=744", 40, 744, {
            const._MARS: 275 + 40/60 + 50/3600,
            const._JUPITER: 302 + 5/60 + 22/3600,
            const._SATURN: 282 + 13/60 + 50/3600,
            const._MERCURY: 162 + 56/60 + 17/3600,
            const._VENUS: 7 + 32/60 + 54/3600,
        }, None),
        ("Example B (Sec 12.10, Apr 3 1996): C=43, A=1173", 43, 1173, {
            # NOTE: these are the MEAN longitudes / Sighra-kendras (Ch 12.10's
            # own intermediate "MP" values), NOT the true longitudes -- the
            # true-longitude check runs separately further below.
            const._MARS: 11*30 + 3 + 53/60 + 25/3600,
            const._JUPITER: 8*30 + 18 + 50/60 + 15/3600,
            const._SATURN: 11*30 + 9 + 28/60 + 31/3600,
            const._MERCURY: 1*30 + 15 + 21/60 + 8/3600,
            const._VENUS: 4*30 + 19 + 57/60 + 31/3600,
        }, 11*30 + 17 + 32/60 + 53/3600),  # book states Mean Sun directly for this example
    ]
    names = {const._MARS: 'Kuja', const._JUPITER: 'Guru', const._SATURN: 'Sani',
             const._MERCURY: 'Budha', const._VENUS: 'Sukra'}
    for label, C, A, mean_targets, true_targets_or_mean_sun in examples:
        print(f"\n  {label}")
        graha_laaghavam._gl_cakra_ahargana = lambda jd, place, C=C, A=A: (C, A)
        try:
            for planet, target in mean_targets.items():
                computed = graha_laaghavam._mean_longitude_raw(0, None, planet)
                diff_arcsec = abs(((computed - target + 180) % 360) - 180) * 3600
                status = "OK" if diff_arcsec < 60 else "CHECK"
                print(f"    Mean/Sighra-kendra {names[planet]:6s} computed={_gl_dms(computed):>14s}"
                      f"  book={_gl_dms(target):>14s}  diff={diff_arcsec:6.1f}\"  [{status}]")
            # Example B also gives us a clean end-to-end TRUE longitude
            # check (feeds through the full 3-step manda/sighra refinement)
            if label.startswith("Example B"):
                mean_sun = graha_laaghavam._mean_longitude_raw(0, None, const._SUN)
                print(f"    (Mean Sun for this example: computed={_gl_dms(mean_sun)}"
                      f"  book={_gl_dms(true_targets_or_mean_sun)})")
                true_targets = {
                    const._MARS: 11*30 + 13 + 24/60 + 54/3600,
                    const._JUPITER: 8*30 + 23 + 52/60 + 26/3600,
                    const._SATURN: 11*30 + 2 + 7/60 + 3/3600,
                    const._MERCURY: 11*30 + 27 + 26/60 + 55/3600,
                    const._VENUS: 1*30 + 4 + 43/60 + 59/3600,
                }
                for planet, target in true_targets.items():
                    computed = graha_laaghavam._sidereal_longitude_impl(0, None, planet)
                    diff_arcsec = abs(((computed - target + 180) % 360) - 180) * 3600
                    status = "OK" if diff_arcsec < 60 else "CHECK"
                    print(f"    TRUE longitude {names[planet]:6s}      computed={_gl_dms(computed):>14s}"
                          f"  book={_gl_dms(target):>14s}  diff={diff_arcsec:6.1f}\"  [{status}]")
        finally:
            graha_laaghavam._gl_cakra_ahargana = orig_cakra_ahargana
    # -------------------------------------------------------------
    # PART 2: epoch round-trip -- derive (Cakra, Ahargana) from the
    # REAL calendar dates and compare against the book's stated values.
    # UNVERIFIED in this sandbox -- see module docstring's GL-SPECIFIC
    # CAVEAT. Run this and inspect the result before trusting any
    # jd-based (not directly-injected-C/A) GL output elsewhere in this
    # test suite.
    # -------------------------------------------------------------
    print("\n--- PART 2: EPOCH ROUND-TRIP CHECK (real calendar date -> Cakra/Ahargana) ---")
    print("    NOTE: this part has NOT been independently verified in this sandbox")
    print("    (no live `jhora` install was available here to test against). If it")
    print("    reports MISMATCH, graha_laaghavam._GL_EPOCH_JD needs adjustment --")
    print("    PART 1 above (the actual engine math) is unaffected either way.\n")
    place_ujjayini = drik.Place('Ujjayini,IN', 23 + 11/60, 75 + 47/60, 5.5)
    # FIX: the book's (Cakra, Ahargana) pairs are at MEAN SUNRISE (06:00 LMT):
    # Example A is "A=744 at sunrise on the previous day, 4-2-1962".
    # _gl_cakra_ahargana() takes local-mean-time jd and returns a fractional A,
    # so query 06:00 on the book's day and compare with a tolerance.
    round_trip_cases = [
        ("Example A target: sunrise Feb 4, 1962, C=40, A=744",
         drik.Date(1962, 2, 4), (6, 0, 0), 40, 744),
        ("Example B target: sunrise Apr 3, 1996, C=43, A=1173",
         drik.Date(1996, 4, 3), (6, 0, 0), 43, 1173),
    ]
    for label, dob_rt, tob_rt, expected_C, expected_A in round_trip_cases:
        jd_rt = utils.julian_day_number(dob_rt, tob_rt)
        try:
            computed_C, computed_A = graha_laaghavam._gl_cakra_ahargana(jd_rt, place_ujjayini)
            match = (computed_C == expected_C and abs(computed_A - expected_A) < 1e-6)
            print(f"    {label}")
            print(f"      computed (Cakra, Ahargana) = ({computed_C}, {computed_A})"
                  f"   book = ({expected_C}, {expected_A})"
                  f"   [{'MATCH' if match else 'MISMATCH -- see caveat above'}]")
        except Exception as e:
            print(f"    {label}\n      ERROR: {e}")
    print()
def test_book_lunar_eclipse_9_9_gl():
    """
    Book Section 9.9 -- Lunar eclipse per Graha Laaghavam (GL method).
    Verifies eclipse_gl.is_lunar_eclipse()'s formula chain DIRECTLY
    against the book's own worked numbers, by monkeypatching
    graha_laaghavam's longitude/speed functions to return the book's own
    stated inputs (bypassing jd/epoch derivation -- same approach as
    test_book_star_planets_11_4_12_10_gl()'s Part 1, so this is
    independent of the _GL_EPOCH_JD question flagged there).
    Book's own stated inputs:
        True Sun   = 8s 0d12'6"  = 240.2017 deg
        True Moon  = 2s 0d12'6"  = 60.2017 deg
        True Rahu  = 7s28d23'18" = 268.3883 deg
        SDM = 61'11"/day, MDM = 823'50"/day
    Book's own stated results:
        SDIA=11ang14pra, MDIA=11ang7pra, Shadow dia=28ang23pra
        Sara=2ang48pra, Grasa=16ang57pra (total eclipse), Khagrasa=5ang50pra
        Sthiti (half-duration)=4gh38pala
        Marda (totality half-duration)=1gh56pala
    """
    from jhora.panchanga import eclipse_gl, graha_laaghavam as gl
    print("=" * 70)
    print("BOOK TEST 6: Lunar eclipse per Graha Laaghavam (Section 9.9)")
    print("=" * 70)
    true_sun = 8*30 + 0 + 12/60 + 6/3600
    true_moon = 2*30 + 0 + 12/60 + 6/3600
    true_rahu = 7*30 + 28 + 23/60 + 18/3600
    sdm = 61 + 11/60.0
    mdm = 823 + 50/60.0
    orig_long = gl._sidereal_longitude_impl
    orig_speed = gl.daily_planet_speed
    def fake_long(jd, place, planet):
        if planet == const._MOON: return true_moon
        if planet == const._RAHU: return true_rahu
        return orig_long(jd, place, planet)
    def fake_speed(jd, place, planet, dt=0.02):
        if planet == const.SUN_ID: return sdm / 60.0
        if planet == const.MOON_ID: return mdm / 60.0
        return orig_speed(jd, place, planet, dt)
    gl._sidereal_longitude_impl = fake_long
    gl.daily_planet_speed = fake_speed
    try:
        info = eclipse_gl.is_lunar_eclipse(0, None)
    finally:
        gl._sidereal_longitude_impl = orig_long
        gl.daily_planet_speed = orig_speed
    def _ang(deg):
        # reverses eclipse_gl's angula -> degree conversion, for comparison
        # against the book's own angula/pala notation.
        return deg / eclipse_gl._ANGULA_TO_DEG
    print(f"  SDIA               computed={_ang(info['sun_diameter']):.4f} ang"
          f"   book=11ang14pra={11+14/60:.4f}")
    print(f"  MDIA               computed={_ang(info['moon_diameter']):.4f} ang"
          f"   book=11ang7pra={11+7/60:.4f}")
    print(f"  Shadow diameter    computed={_ang(info['shadow_diameter']):.4f} ang"
          f"   book=28ang23pra={28+23/60:.4f}")
    print(f"  Sara               computed={_ang(info['moon_latitude']):.4f} ang"
          f"   book=2ang48pra={2+48/60:.4f}")
    print(f"  Grasa              computed={_ang(info['grasa']):.4f} ang"
          f"   book=16ang57pra={16+57/60:.4f}")
    print(f"  is_total           computed={info['is_total']}   book=True (total)")
    if info['khagrasa'] is not None:
        print(f"  Khagrasa           computed={_ang(info['khagrasa']):.4f} ang"
              f"   book=5ang50pra={5+50/60:.4f}")
    if info['half_duration_days'] is not None:
        print(f"  Sthiti (half-dur)  computed={info['half_duration_days']*60:.4f} gh"
              f"   book=4gh38pala={4+38/60:.4f}")
    if info['half_duration_totality_days'] is not None:
        print(f"  Marda (tot half-dur) computed={info['half_duration_totality_days']*60:.4f} gh"
              f"   book=1gh56pala={1+56/60:.4f}")
    print()
def test_book_solar_eclipse_10_4_gl():
    """
    Book Section 10.4 -- Solar eclipse per Graha Laaghavam (GL method),
    Varanasi, December 1610 (Saka 1532).
    Verifies eclipse_gl's Lambana (parallax-in-longitude) chain DIRECTLY
    against the book's own worked numbers, by monkeypatching
    graha_laaghavam's ascendant/longitude/calendar functions (same
    approach as the lunar test above).
    Book's own stated inputs/intermediate values:
        Nirayana Lagna = 11s2d46'17" = 332.7714 deg
        True Sun = 8s5d26'25" = 245.4403 deg
        Saka year = 1532, place latitude = 25d26'42" (Varanasi)
    Book's own stated results:
        Tribhona Lagna = 242.7714 deg
        Ayanamsa = 18d08' = 18.1333 deg
        Lambana = 11.9 pala (subtractive)
        Instant of (true) conjunction = 13gh4pala
        Middle of eclipse (apparent conjunction) = 12gh52.1pala
    """
    from jhora.panchanga import eclipse_gl, graha_laaghavam as gl
    print("=" * 70)
    print("BOOK TEST 7: Solar eclipse per Graha Laaghavam (Section 10.4)")
    print("=" * 70)
    nirayana_lagna = 11*30 + 2 + 46/60.0 + 17/3600.0
    true_sun = 8*30 + 5 + 26/60.0 + 25/3600.0
    saka_year = 1532
    place = drik.Place('Varanasi,IN', 25 + 26/60.0 + 42/3600.0, 83.0, 5.5)
    orig_asc_long = gl._ascendant_longitude
    orig_sid_long = gl._sidereal_longitude_impl
    orig_lunar_month_date = gl.lunar_month_date
    orig_elapsed_year = gl.elapsed_year
    def fake_asc_long(jd, place, eps_deg=24.0):
        return nirayana_lagna
    def fake_sid_long(jd, place, planet):
        if planet == const._SUN: return true_sun
        return orig_sid_long(jd, place, planet)
    def fake_lunar_month_date(jd, place):
        return [9, 1, 0, False, False]
    def fake_elapsed_year(jd, maasa_index):
        return None, None, saka_year
    gl._ascendant_longitude = fake_asc_long
    gl._sidereal_longitude_impl = fake_sid_long
    gl.lunar_month_date = fake_lunar_month_date
    gl.elapsed_year = fake_elapsed_year
    try:
        ayanamsa_deg = eclipse_gl._gl_eclipse_ayanamsa(0, place)
        lambana_days = eclipse_gl._gl_lambana_days(0, place, ayanamsa_deg)
    finally:
        gl._ascendant_longitude = orig_asc_long
        gl._sidereal_longitude_impl = orig_sid_long
        gl.lunar_month_date = orig_lunar_month_date
        gl.elapsed_year = orig_elapsed_year
    print(f"  Ayanamsa  computed={ayanamsa_deg:.4f} deg   book=18.1333 deg (18d08')")
    print(f"  Lambana   computed={lambana_days*3600:.4f} pala   book=-11.9 pala (subtractive)")
    instant_of_conjunction_gh = 13 + 4/60.0
    middle_gh = instant_of_conjunction_gh + lambana_days * 60
    print(f"  Middle of eclipse computed={middle_gh:.4f} gh   book=12gh52.1pala={12+52.1/60:.4f}")
    print()
def test_book_tantra_sangraha():
    """
    Tantrasangraha of Nilakantha Somayaji (Ramasubramanian & Sriram, 2011).
    Unlike the SS/KK/GL book tests above, Tantrasangraha has no single
    multi-planet worked example (nothing analogous to Rao's Table 12.7).
    Two checks the book DOES give explicitly are used instead:
      PART 1 -- AHARGANA (Ch 1.11, Example 1): the book computes the Kali
        ahargana for Phalguna-krsna-trayodasi, Saka 1922 (22-Mar-2001 CE)
        as 1863525, and verifies this independently via the remainder-by-7
        weekday check (1863525 = 266217*7 + 6 => Thursday; 22-Mar-2001 CE
        was in fact a Thursday). This checks tantra_sangraha.py's ahargana
        pipeline (TS_REVOLUTIONS/TS_DHRUVA/TS_CIVIL_DAYS_IN_MAHAYUGA) is
        wired correctly, independent of any manda/sighra computation.
      PART 2 -- SIDEREAL PERIODS (Appendix F, Table F.1): the book tabulates
        the sidereal period (civil days per revolution) implied by its own
        Table 1.5 revolution counts, for comparison against modern values.
        This is reproduced here as (TS_CIVIL_DAYS_IN_MAHAYUGA / revolutions)
        for all 7 bodies and checked against the book's own printed Table
        F.1 values (to 5 decimal places) -- this independently confirms
        TS_REVOLUTIONS and TS_CIVIL_DAYS_IN_MAHAYUGA are both transcribed
        correctly, since the two tables (1.5 and F.1) are in different
        chapters/appendices of the book and were extracted separately.
    There is no multi-planet TRUE longitude worked example in the source
    material available for this engine, so (unlike the GL/KK book tests)
    this does NOT check the manda/sighra correction chain end-to-end --
    only the mean-motion/epoch machinery. Cross-check tantra_sangraha's
    true longitudes against drik for several dates/places separately (see
    test1.py's planetary-longitude table) to sanity-check the corrections.
    """
    print("=" * 78)
    print("BOOK TEST 8: Tantrasangraha -- ahargana and sidereal periods")
    print("             (Ch 1.10/1.11 Example 1, Appendix F Table F.1)")
    print("=" * 78)
    print("\n--- PART 1: AHARGANA (Ch 1.11, Example 1) ---")
    place = drik.Place('Ujjayini,IN', 23 + 11/60, 75 + 47/60, 5.5)
    jd = utils.julian_day_number(drik.Date(2001, 3, 22), (0, 0, 0))
    computed_A = tantra_sangraha.kali_ahargana_days(jd, place)
    book_A = 1863525
    match = (computed_A == book_A)
    print(f"    computed ahargana = {computed_A}   book = {book_A}   "
          f"[{'MATCH' if match else 'MISMATCH'}]")
    weekday = computed_A % 7
    print(f"    computed_A mod 7 = {weekday}   book states remainder 6 => Thursday "
          f"(22-Mar-2001 CE was a Thursday)   [{'OK' if weekday == 6 else 'CHECK'}]")
    print("\n--- PART 2: SIDEREAL PERIODS (Appendix F, Table F.1) ---")
    book_periods = {
        const._SUN: 365.25868, const._MOON: 27.32168, const._MARS: 686.98778,
        const._JUPITER: 4332.79559, const._VENUS: 224.70198,
        const._SATURN: 10762.53990, const._MERCURY: 87.96974,
    }
    names = {const._SUN: 'Sun', const._MOON: 'Moon', const._MARS: 'Mars',
              const._MERCURY: 'Mercury', const._JUPITER: 'Jupiter',
              const._VENUS: 'Venus', const._SATURN: 'Saturn'}
    for planet, book_val in book_periods.items():
        rev = tantra_sangraha.TS_REVOLUTIONS[planet]
        computed = tantra_sangraha.TS_CIVIL_DAYS_IN_MAHAYUGA / rev
        diff = abs(computed - book_val)
        status = "OK" if diff < 0.0001 else "CHECK"
        print(f"    {names[planet]:8s} computed={computed:11.5f}  book={book_val:11.5f}  "
              f"diff={diff:.6f}  [{status}]")
    print()
def rao_book_example_diagnostic_test():
    from jhora.panchanga import eclipse_ss
    print("=" * 78)
    print("DIAGNOSTIC: Oct 24, 1995 Bangalore solar eclipse -- direct call, no search loop")
    print("=" * 78)
    # --- Setup: Bangalore, book's stated starting instant (5:30 AM IST) ---
    place = drik.Place('Bangalore,IN', 12 + 58/60, 77 + 35/60, 5.5)
    dob = drik.Date(1995, 10, 24)
    tob = (5, 30, 0)
    jd_start = utils.julian_day_number(dob, tob)
    print(f"\nSTEP 0: locating the actual new moon nearest {dob} {tob} IST")
    print("-" * 78)
    ti = surya_sidhantha.tithi(jd_start, place)[0]
    print(f"  tithi index at start instant: {ti}")
    jd_new = surya_sidhantha.new_moon(jd_start, place, ti, opt=1)
    y, m, d, fh = utils.jd_to_gregorian(jd_new)
    h, mi, s = utils.to_dms(fh, as_string=False)
    print(f"  New moon (mean/true conjunction, SS model) found at: "
          f"{y:04d}-{m:02d}-{d:02d} {int(h):02d}:{int(mi):02d}:{int(round(s)):02d} IST")
    print(f"  jd_new = {jd_new:.6f}")
    days_off = jd_new - jd_start
    print(f"  (offset from the 5:30 AM start instant: {days_off*24:.3f} hours)")
    # --- Run the exact same 4-iteration convergence loop as
    #     is_solar_eclipse(), but with full prints at every step ---
    print(f"\nSTEP 1: convergence loop (mirrors is_solar_eclipse() internals)")
    print("-" * 78)
    jd_app = jd_new
    drkkshepa = 0.0
    for i in range(4):
        lagna_deg = eclipse_ss._ss_tropical_ascendant(jd_app, place)
        mc = eclipse_ss._ss_madhya_lagna(jd_app, place)
        orient_sine = (math.sin(math.radians(24.0)) * eclipse_ss._R *
                       math.sin(math.radians(lagna_deg)) / math.cos(math.radians(place.latitude)))
        dec_mc = math.degrees(math.asin(max(-1.0, min(1.0,
                    math.sin(math.radians(24.0)) * math.sin(math.radians(mc))))))
        merid_zen = dec_mc - place.latitude
        sn_merz = eclipse_ss._R * math.sin(math.radians(merid_zen))
        osmz = orient_sine * sn_merz / eclipse_ss._R
        drkkshepa = math.sqrt(max(0.0, sn_merz**2 - osmz**2))
        drggati = math.sqrt(max(0.0, eclipse_ss._R**2 - drkkshepa**2))
        cheda = (eclipse_ss._R * math.sin(math.radians(30.0)))**2 / drggati if drggati != 0 else float('inf')
        sun_long = surya_sidhantha._sidereal_longitude_impl(jd_app, place, const._SUN)
        tropical_sun_long = (sun_long + surya_sidhantha.surya_sidhantha_ayanamsa(jd_app, place)) % 360.0
        lambana_nadis = (eclipse_ss._R * math.sin(math.radians(mc - tropical_sun_long)) / cheda
                          if cheda not in (0.0, float('inf')) else 0.0)
        print(f"\n  --- ITERATION {i} ---")
        print(f"    jd_app (input)          : {jd_app:.6f}")
        print(f"    Lagna (tropical)        : {lagna_deg:.4f} deg  [{_dms(lagna_deg)}]"
              f"   (book Approxn.3: 249.6023 deg [249 36' 8\"])")
        print(f"    MC (Madhya Lagna)       : {mc:.4f} deg  [{_dms(mc)}]"
              f"   (book Approxn.3: 161.834 deg [161 50' 3\"])")
        print(f"    Orient sine (Udayajya)  : {orient_sine:.3f}"
              f"   (book Approxn.3: -1344.974)")
        print(f"    Declination of MC       : {dec_mc:.4f} deg  [{_dms(dec_mc)}]")
        print(f"    Meridian zenith dist.   : {merid_zen:.4f} deg  [{_dms(merid_zen)}]")
        print(f"    R*sin(merid_zen)        : {sn_merz:.3f}")
        print(f"    Drkkshepa               : {drkkshepa:.3f}"
              f"   (book Approxn.3: 313.233)")
        print(f"    Drggati                 : {drggati:.3f}"
              f"   (book Approxn.3: 3423.700)")
        print(f"    Cheda                   : {cheda:.3f}"
              f"   (book Approxn.3: 863.083)")
        print(f"    Sidereal Sun longitude  : {sun_long:.4f} deg  [{_dms(sun_long)}]")
        print(f"    Tropical Sun (Sayana)   : {tropical_sun_long:.4f} deg  [{_dms(tropical_sun_long)}]")
        print(f"    Lambana (nadis)         : {lambana_nadis:.4f}")
        jd_app_next = jd_new + lambana_nadis / 60.0
        print(f"    -> next jd_app          : {jd_app_next:.6f}  (delta: {(jd_app_next-jd_app)*1440:.3f} min)")
        jd_app = jd_app_next
    y, m, d, fh = utils.jd_to_gregorian(jd_app)
    h, mi, s = utils.to_dms(fh, as_string=False)
    print(f"\n  Converged jd_app (apparent conjunction): "
          f"{y:04d}-{m:02d}-{d:02d} {int(h):02d}:{int(mi):02d}:{int(round(s)):02d} IST"
          f"   (book: 08:58:36 approx, after their own iterative correction)")
    # --- Final decision variables, exactly as is_solar_eclipse() computes them ---
    print(f"\nSTEP 2: final grasa/possibility check (mirrors is_solar_eclipse() tail)")
    print("-" * 78)
    mdm_deg = abs(surya_sidhantha.daily_planet_speed(jd_app, place, const.MOON_ID))
    mdm_arcmin = mdm_deg * 60.0
    nati_arcmin = (mdm_arcmin / 15.0) * (drkkshepa / eclipse_ss._R)
    sdia, mdia, shdia = eclipse_ss._ss_eclipse_diameters(jd_app, place)
    mlat_base = eclipse_ss._ss_moon_latitude(jd_app, place)
    mlat = mlat_base + nati_arcmin / 60.0
    grasa = 0.5 * (sdia + mdia) - abs(mlat)
    is_possible = grasa > 0.0
    is_total = grasa > sdia
    print(f"    Moon's true daily motion (mdm) : {mdm_deg:.4f} deg/day = {mdm_arcmin:.2f} arcmin/day")
    print(f"    Nati (parallax in latitude)    : {nati_arcmin:.4f} arcmin"
          f"   (book's own nati values are typically a few arcmin, e.g. 4'27\", 13'47\")")
    print(f"    Sun diameter                   : {sdia*60:.3f} arcmin"
          f"   (book: ~31-32 arcmin)")
    print(f"    Moon diameter                  : {mdia*60:.3f} arcmin"
          f"   (book: ~31-33 arcmin)")
    print(f"    Moon latitude (base, no nati)  : {mlat_base*60:.4f} arcmin")
    print(f"    Moon latitude (base + nati)    : {mlat*60:.4f} arcmin")
    print(f"    Grasa (0.5*(sdia+mdia)-|mlat|) : {grasa*60:.4f} arcmin"
          f"   ({'POSITIVE -> eclipse possible' if grasa > 0 else 'NEGATIVE -> NOT possible'})")
    print(f"    is_possible                    : {is_possible}   (book says: True, partial, magnitude 0.5995)")
    print(f"    is_total                       : {is_total}   (book says: False -- partial)")
    print(f"\n{'='*78}")
    if is_possible:
        print("RESULT: is_solar_eclipse() correctly finds this eclipse possible when")
        print("called DIRECTLY. => The remaining bug is in next_solar_eclipse()'s SEARCH")
        print("LOOP (skip-ahead distance / starting jd), NOT in the parallax/grasa math.")
    else:
        print("RESULT: is_solar_eclipse() itself says NOT possible for the book's own")
        print("confirmed real eclipse. => The bug is still in the parallax/nati/grasa")
        print("chain above -- compare the ITERATION 0 values against the book's")
        print("Approxn.3 table (printed alongside each line) to find which quantity")
        print("diverges first.")
    print(f"{'='*78}")
def test_batch14(engine, jd, place):
    """
    SS -> eclipse_ss.py ; drik -> eclipse.py ; KK -> eclipse_kk.py ;
    GL -> eclipse_gl.py ; TS -> eclipse_ts.py ; VP -> eclipse_vp.py ;
    MS -> eclipse_ms.py ; VS -> eclipse_vs.py.
    Shape notes (kept from the original, still relevant when diffing the
    printed blocks):
      - Solar eclipse, LOCAL mode: all six classical engines (SS/KK/GL/TS/
        VP/MS) plus drik return (type_str, [begin, max, end]). SS and KK
        both currently report begin/end as placeholders equal to middle
        (see eclipse_ss.py/eclipse_kk.py docstrings); drik reports genuine
        begin/end from swisseph; GL and TS both report genuine begin/end
        from their own half-duration formulas (TS additionally includes the
        lambana/nati parallax refinement from Ch 5 -- see eclipse_ts.py
        docstring). MS (eclipse_ms.py) also reports genuine begin/end from
        its own half-duration formula, but every number feeding it is
        presently FITTED (not transcribed from the Makaranda Sarini's own
        tables) -- see eclipse_ms.py's module docstring before trusting it.
      - Lunar eclipse: drik returns 5 elements
        [penumbral_begin, partial_begin, max, partial_end, penumbral_end];
        SS, KK, and GL return 3 [partial_begin, max, partial_end] for a
        partial eclipse, or 5 [begin, totality_begin, max, totality_end,
        end] for a total eclipse (no penumbral phase in any of the three
        classical models). TS, VP, and MS ALWAYS return 3 elements
        regardless of total/partial (none of them separately reports a
        totality phase -- see eclipse_ts.py / eclipse_ms.py docstrings), so
        they are grouped with SS/KK below, not GL. Labels below make the
        mapping explicit.
      - type_str vocabularies differ (drik: any/total/annular/hybrid/
        partial/penumbral ; SS/KK/GL/TS: total/partial only, TS also
        supports annular). All sides are queried with ...EclipseType.ANY
        for a fair unfiltered search.
      - NOT tested: GLOBAL solar search, maximum-eclipse global location,
        ANNULAR/HYBRID/PENUMBRAL specific-type searches (no SS/KK/GL
        equivalent; TS supports an ANNULAR filter but it is not
        separately exercised here).
    """
    if engine == VP:
        # Book examples of the Vakya model: test_book_vakya.py (Chapters I-III: Kali days, Sun, Moon, Rahu, planets, Lagna ...)
        # and test_book_eclipse_vp.py (Chapter IV: Ex. 32-38 through eclipse_vp.py, plus date-level checks of its public API)
        run_vakya_book_tests()
        run_eclipse_vp_tests()
    elif engine == MS:
        # Book examples of the Makaranda Sarini: test_book_mks.py (Saka 1534 Vaisakha sukla 15 graha-sadhana,
        # pp. 0072-0081) and test_book_eclipse_ms.py (lunar/solar eclipse examples, pp. 0083-0084, plus
        # date-level checks of eclipse_ms.py's public API)
        run_mks_book_tests()
        run_eclipse_ms_tests()
    elif engine == VS:
        # The numbers printed in Chapters IV and V of the Vateswara book (test_book_eclipse_vs.py); the algorithm itself is tested against
        # exact geometry in test_vs_eclipse.py
        run_eclipse_vs_tests()
    elif engine == SNT:
        # The Sphutanirnaya-tantra has no worked examples wired here and no eclipse chapter: no book tests; BATCH 14 below uses eclipse_ts.py
        print(f"[{engine}] no book-example tests for the Sphutanirnaya-tantra; BATCH 14 below uses eclipse_ts.py")
    else:
        test_book_lunar_eclipse_9_7()
        test_book_solar_eclipse_10_3()
        test_book_lunar_eclipse_9_8_kk()
        test_book_solar_eclipse_10_5_kk()
        test_book_star_planets_11_4_12_10_gl()
        test_book_lunar_eclipse_9_9_gl()
        test_book_solar_eclipse_10_4_gl()
        test_book_tantra_sangraha()
    from jhora.panchanga import eclipse, eclipse_ss, eclipse_kk, eclipse_gl, eclipse_ts, eclipse_vp, eclipse_ms, eclipse_vs
    ecl = {SS: eclipse_ss, KK: eclipse_kk, GL: eclipse_gl, TS: eclipse_ts, VP: eclipse_vp, MS: eclipse_ms,
           VS: eclipse_vs, SNT: eclipse_ts, DRIK: eclipse}[engine]
    ecl_module_name = {SS: 'eclipse_ss.py', KK: 'eclipse_kk.py', GL: 'eclipse_gl.py',
                       TS: 'eclipse_ts.py', VP: 'eclipse_vp.py', MS: 'eclipse_ms.py', VS: 'eclipse_vs.py',
                       SNT: 'eclipse_ts.py (the Sphutanirnaya has no eclipse chapter)', DRIK: 'eclipse.py'}[engine]
    _banner(engine, f"BATCH 14: ECLIPSES ({ecl_module_name})")
    def _fmt(entry):
        if entry is None:
            return "None"
        y, m, d, fh = entry
        return f"{y:04d}-{m:02d}-{d:02d} {utils.to_dms(fh, as_string=True)}"
    for direction_label, search_backward in (("NEXT", False), ("PREVIOUS", True)):
        print(f"\n[{engine}] --- {direction_label} SOLAR ECLIPSE (LOCAL) ---")
        val = _safe(ecl.next_solar_eclipse, jd, place,
                    ecl.EclipseLocation.LOCAL, ecl.SolarEclipseType.ANY,
                    search_backward=search_backward)
        if isinstance(val, tuple):
            e_type, e_times = val
            print(f"[{engine}] {'type':10s} = {e_type}")
            for label, t in zip(("begin", "max  ", "end  "), e_times):
                print(f"[{engine}] {label:10s} = {_fmt(t)}")
        else:
            print(f"[{engine}] {val}")
        print(f"\n[{engine}] --- {direction_label} LUNAR ECLIPSE ---")
        val = _safe(ecl.next_lunar_eclipse, jd, place,
                    ecl.EclipseLocation.LOCAL, ecl.LunarEclipseType.ANY,
                    search_backward=search_backward)
        if isinstance(val, tuple):
            e_type, e_times = val
            print(f"[{engine}] {'type':10s} = {e_type}")
            if engine in (GL, VS):   # GL and VS return 3 (partial) or 5 (total) elements
                if len(e_times) == 5:
                    labels5 = ("begin", "totality_b", "max", "totality_e", "end")
                    for label, t in zip(labels5, e_times):
                        print(f"[{engine}] {label:10s} = {_fmt(t)}")
                else:
                    print(f"[{engine}] {'partial_b':10s} = {_fmt(e_times[0])}")
                    print(f"[{engine}] {'max':10s} = {_fmt(e_times[1])}")
                    print(f"[{engine}] {'partial_e':10s} = {_fmt(e_times[2])}")
                    print(f"[{engine}] {'penumbra_b':10s} = N/A (no penumbral phase in {engine})")
                    print(f"[{engine}] {'penumbra_e':10s} = N/A (no penumbral phase in {engine})")
            elif engine in (SS, KK, TS, VP, MS, SNT):   # 3 elements (VP and MS, like TS, always return 3 -- no separate
                                            # totality times; TS: see eclipse_ts.py docstring -- unlike GL, none of
                                            # these distinguish a separate totality phase)
                print(f"[{engine}] {'partial_b':10s} = {_fmt(e_times[0])}")
                print(f"[{engine}] {'max':10s} = {_fmt(e_times[1])}")
                print(f"[{engine}] {'partial_e':10s} = {_fmt(e_times[2])}")
                print(f"[{engine}] {'penumbra_b':10s} = N/A (no penumbral phase in {engine})")
                print(f"[{engine}] {'penumbra_e':10s} = N/A (no penumbral phase in {engine})")
            else:              # drik, 5 elements fixed
                print(f"[{engine}] {'partial_b':10s} = {_fmt(e_times[1])}")
                print(f"[{engine}] {'max':10s} = {_fmt(e_times[2])}")
                print(f"[{engine}] {'partial_e':10s} = {_fmt(e_times[3])}")
                print(f"[{engine}] {'penumbra_b':10s} = {_fmt(e_times[0])}")
                print(f"[{engine}] {'penumbra_e':10s} = {_fmt(e_times[4])}")
        else:
            print(f"[{engine}] {val}")
# ---------------------------------------------------------------------
# Engine configuration + drivers
# ---------------------------------------------------------------------
def _configure(engine):
    """
    Set global state for ONE engine. Must be called immediately before that
    engine's pass -- these settings are process-global and mutually exclusive.
    """
    utils.set_language('en')
    drik.set_ayanamsa_mode('LAHIRI')
    if engine == SS:
        const.astrology_model_default = const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA
        # Surya Siddhanta requires MEAN nodes
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == KK:
        const.astrology_model_default = const.ASTROLOGY_MODELS.KHANDA_KHAADYAKA
        # Khandakhadyaka (Brahmagupta) is also a mean-node model, same as SS
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == GL:
        gl_model = getattr(const.ASTROLOGY_MODELS, 'GRAHA_LAAGHAVAM', None)
        if gl_model is not None:
            const.astrology_model_default = gl_model
        # Graha Laaghavam (Ganesha Daivajna) is also a mean-node model, same as SS/KK
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == TS:
        ts_model = getattr(const.ASTROLOGY_MODELS, 'TANTRA_SANGRAHA', None)
        if ts_model is not None:
            const.astrology_model_default = ts_model
        # Tantrasangraha (Nilakantha Somayaji) is also a mean-node model, same as SS/KK/GL
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == VP:
        vp_model = getattr(const.ASTROLOGY_MODELS, 'VAKYA_PANCHANGAM', None)
        if vp_model is not None:
            const.astrology_model_default = vp_model
        # Vakya Panchangam (Vakyakarana) is also a mean-node model, same as SS/KK/GL/TS
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
        vakya_panchanga.reset_ayanamsa_mode()
    elif engine == MS:
        ms_model = getattr(const.ASTROLOGY_MODELS, 'MAKARANDA_SARINI', None)
        if ms_model is not None:
            const.astrology_model_default = ms_model
        # Makaranda Sarini is also a mean-node model, same as SS/KK/GL/TS/VP
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
        makaranda_sarini.reset_ayanamsa_mode()
    elif engine == VS:
        vs_model = getattr(const.ASTROLOGY_MODELS, 'VATESHWARA_SIDHANTHA', None)
        if vs_model is not None:
            const.astrology_model_default = vs_model
        # Vateswara Siddhanta is a mean-node model, same as SS/KK/GL/TS/VP/MS

        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == SNT:
        snt_model = getattr(const.ASTROLOGY_MODELS, 'SPHUTA_NIRNAYA_TANTRA', None)
        if snt_model is not None:
            const.astrology_model_default = snt_model
        # Sphutanirnaya-tantra (Acyuta Pisharati) is also a mean-node model, same as SS/KK/GL/TS/VP/MS/VS
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    else:
        drik_model = getattr(const.ASTROLOGY_MODELS, 'DRIK',
                             getattr(const.ASTROLOGY_MODELS, 'DRIK_GANITHA', None))
        if drik_model is not None:
            const.astrology_model_default = drik_model
        # drik requires TRUE nodes
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=True)
    node_desc = 'TRUE' if engine == DRIK else 'MEAN'
    print("#" * 80)
    print(f"# PASS: {engine}  |  astrology_model_default={const.astrology_model_default}"
          f"  |  rahu/ketu={node_desc} nodes")
    print("#" * 80)
    print()
def run_engine(engine, jd, dob, tob, place):
    mod = {SS: surya_sidhantha, KK: khanda_khaadyaka, GL: graha_laaghavam, TS: tantra_sangraha,
           VP: vakya_panchanga, MS: makaranda_sarini, VS: vateshwara_sidhantha, SNT: sphuta_nirnaya_tantra, DRIK: drik}[engine]
    _configure(engine)
    main(engine, mod, jd, dob, tob, place)
    test_batch5(engine, mod, jd, place, dob, tob)
    test_batch6(engine, mod, dob, place)
    test_sankranti_consistency(engine, mod, place)
    test_batch7(engine, mod, jd, place)
    test_batch8(engine, mod, jd, place)
    test_batch9(engine, mod, jd, place)
    test_batch10(engine, mod, jd, place)
    test_batch11(engine, mod, jd, place)
    test_batch12(engine, mod, jd, place, dob, tob)
    test_batch13(engine, mod, jd, place)
    test_batch14(engine, jd, place)
    print()
    print(f"### END OF {engine} PASS ###")
    print()
def _chart():
    dob = drik.Date(1996, 12, 7); tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.0878, 80.2785, 5.5)
    jd = utils.julian_day_number(dob, tob)
    return jd, dob, tob, place
def run_all_tests():
    jd, dob, tob, place = _chart()
    run_engine(SS, jd, dob, tob, place)      # PASS 1: mean nodes (Surya Siddhanta)
    run_engine(KK, jd, dob, tob, place)      # PASS 2: mean nodes (Khandakhadyaka)
    run_engine(GL, jd, dob, tob, place)      # PASS 3: mean nodes (Graha Laaghavam)
    run_engine(TS, jd, dob, tob, place)      # PASS 4: mean nodes (Tantrasangraha)
    run_engine(VP, jd, dob, tob, place)      # PASS 5: mean nodes (Vakya Panchangam)
    run_engine(MS, jd, dob, tob, place)      # PASS 6: mean nodes (Makaranda Sarini)
    run_engine(VS, jd, dob, tob, place)      # PASS 7: mean nodes (Vateswara Siddhanta)
    run_engine(SNT, jd, dob, tob, place)     # PASS 8: mean nodes (Sphutanirnaya-tantra)
    run_engine(DRIK, jd, dob, tob, place)    # PASS 9: true nodes
def partial_tests():
    run_vakya_book_tests()
    run_eclipse_vp_tests()
    jd, dob, tob, place = _chart()
    mods = {SS: surya_sidhantha, KK: khanda_khaadyaka, GL: graha_laaghavam,
            TS: tantra_sangraha, VP: vakya_panchanga, MS: makaranda_sarini, VS: vateshwara_sidhantha, SNT: sphuta_nirnaya_tantra, DRIK: drik}
    for engine, mod in mods.items():
        _configure(engine)
        test_sankranti_consistency(engine, mod, place)
if __name__ == "__main__":
    #partial_tests()
    run_all_tests()
