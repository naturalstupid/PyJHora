import math
from jhora import const, utils
from jhora.panchanga import drik as _drik_raw
from jhora.panchanga import surya_sidhantha as _ss_raw
from jhora.panchanga import khanda_khaadyaka as _kk_raw
from jhora.panchanga import graha_laaghavam as _gl_raw 
from jhora.panchanga import tantra_sangraha as _ts_raw
from jhora.panchanga import vakya_panchanga as _vp_raw
from jhora.panchanga import makaranda_sarini as _ms_raw
from jhora.panchanga import vateshwara_sidhantha as _vs_raw
from jhora.panchanga import sphuta_nirnaya_tantra as _snt_raw
from test_book_vakya import run_vakya_book_tests   # the Vakyakarana book's worked examples (VP)
from test_book_eclipse_vp import run_eclipse_vp_tests   # Chapter IV (eclipses) of the same book + date-level checks of eclipse_vp.py
from test_book_mks import run_mks_book_tests   # the Makaranda Sarini's own worked example (MS), pp. 0072-0081
from test_book_eclipse_ms import run_eclipse_ms_tests   # eclipse_ms.py's book-example self-test (pp. 0083-0084) + date-level checks
from test_book_eclipse_vs import run_eclipse_vs_tests   # the numbers printed in Chapters IV and V of the Vateswara book (VS)
# ---------------------------------------------------------------------
# ENGINE ISOLATION (makes every column identical to test.py's passes)
# ---------------------------------------------------------------------
# PyJHora has PROCESS-GLOBAL settings (astrology_model_default, ayanamsa,
# mean/true nodes) that drik and the other engines read. test.py handles
# this by running four separate passes, calling _configure(engine) before
# each. This file prints the four engines side by side, so instead EVERY
# call made through drik./surya_sidhantha./khanda_khaadyaka./
# graha_laaghavam. (and the eclipse modules) first applies exactly the
# same _configure(engine) settings as test.py. Same settings -> same
# results as test.py; only the presentation differs.
SS, KK, GL, TS, VP, MS, VS, DRIK = 'SS', 'KK', 'GL', 'TS', 'VP', 'MS', 'VS', 'DRIK'
SNT = 'SNT'   # Sphutanirnaya-tantra (Acyuta Pisharati). It has no eclipse chapter: BATCH 14 runs eclipse_ts.py under the label SNT
def _configure(engine):
    """ Identical to test.py _configure(), minus the banner print. """
    utils.set_language('en')
    _drik_raw.set_ayanamsa_mode('LAHIRI')
    if engine == SS:
        const.astrology_model_default = const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == KK:
        const.astrology_model_default = const.ASTROLOGY_MODELS.KHANDA_KHAADYAKA
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == GL:
        gl_model = getattr(const.ASTROLOGY_MODELS, 'GRAHA_LAAGHAVAM', None)
        if gl_model is not None:
            const.astrology_model_default = gl_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == TS:
        ts_model = getattr(const.ASTROLOGY_MODELS, 'TANTRA_SANGRAHA', None)
        if ts_model is not None:
            const.astrology_model_default = ts_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == VP:
        vp_model = getattr(const.ASTROLOGY_MODELS, 'VAKYA_PANCHANGAM', None)
        if vp_model is not None:
            const.astrology_model_default = vp_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
        _vp_raw.reset_ayanamsa_mode()
    elif engine == MS:
        ms_model = getattr(const.ASTROLOGY_MODELS, 'MAKARANDA_SARINI', None)
        if ms_model is not None:
            const.astrology_model_default = ms_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
        _ms_raw.reset_ayanamsa_mode()
    elif engine == VS:
        vs_model = getattr(const.ASTROLOGY_MODELS, 'VATESHWARA_SIDHANTHA', None)
        if vs_model is not None:
            const.astrology_model_default = vs_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    elif engine == SNT:
        snt_model = getattr(const.ASTROLOGY_MODELS, 'SPHUTA_NIRNAYA_TANTRA', None)
        if snt_model is not None:
            const.astrology_model_default = snt_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    else:
        drik_model = getattr(const.ASTROLOGY_MODELS, 'DRIK',
                             getattr(const.ASTROLOGY_MODELS, 'DRIK_GANITHA', None))
        if drik_model is not None:
            const.astrology_model_default = drik_model
        _drik_raw.set_planet_list(set_rahu_ketu_as_true_nodes=True)
class _Engine:
    """ Wraps a module: every FUNCTION call runs after _configure(engine).
        Classes (Place, Date, enums like EclipseLocation) and constants are
        returned unwrapped. """
    def __init__(self, module, engine):
        self._m, self._engine = module, engine
    def __getattr__(self, name):
        attr = getattr(self._m, name)
        if not callable(attr) or isinstance(attr, type):
            return attr
        def _call(*args, **kwargs):
            _configure(self._engine)
            return attr(*args, **kwargs)
        return _call
drik = _Engine(_drik_raw, DRIK)
surya_sidhantha = _Engine(_ss_raw, SS)
khanda_khaadyaka = _Engine(_kk_raw, KK)
graha_laaghavam = _Engine(_gl_raw, GL)
tantra_sangraha = _Engine(_ts_raw, TS)
vakya_panchanga = _Engine(_vp_raw, VP)
makaranda_sarini = _Engine(_ms_raw, MS)
vateshwara_sidhantha = _Engine(_vs_raw, VS)
sphuta_nirnaya_tantra = _Engine(_snt_raw, SNT)
def _snt_try(func):
    """ func() or 'ERROR: ...' (every Sphutanirnaya-tantra addition of this file is guarded, so a failure shows in the output and does not stop the run) """
    try:
        return func()
    except Exception as e:
        return f"ERROR: {e}"
def _snt_idx(value, index=1):
    """ value[index] of a list / tuple result, None for an empty result (as the other engines' rise/set printing does), an error string unchanged """
    return value[index] if isinstance(value, (list, tuple)) and value else (value if isinstance(value, str) else None)
def _snt_time(func):
    """ _fmt_time() of the Julian day (index 2) of a rise/set result, as the other engines' tables print it, or 'ERROR: ...' """
    try:
        v = func()
        return _fmt_time(v[2] if v else None)
    except Exception as e:
        return f"ERROR: {e}"
def _drik_long(jd_utc, body):
    """ drik convention: sidereal_longitude(jd_utc, planet) -- UT, NO place.
        Ketu = Rahu + 180 (same as test.py). """
    if body == const._KETU:
        return (drik.sidereal_longitude(jd_utc, const._RAHU) + 180.0) % 360.0
    return drik.sidereal_longitude(jd_utc, body)
# ---------------------------------------------------------------------
# NOTE ON MODULE NAMING: this file imports jhora.panchanga.khanda_khaadyaka,
# matching utils.get_hora_engine()'s import path and
# const.ASTROLOGY_MODELS.KHANDA_KHAADYAKA. Make sure the KK engine module
# is saved under that exact filename, or this import will fail. Likewise,
# eclipse_kk.py/eclipse_gl.py must be saved under jhora.panchanga.eclipse_kk/
# jhora.panchanga.eclipse_gl for BATCH 14 below. The same applies to the MS
# (Makaranda Sarini) engine added in this file: makaranda_sarini.py must be
# saved under jhora.panchanga.makaranda_sarini, and eclipse_ms.py under
# jhora.panchanga.eclipse_ms, or the MS imports/column will fail or be
# skipped. const.ASTROLOGY_MODELS.MAKARANDA_SARINI is looked up defensively
# (getattr ... None) exactly like GRAHA_LAAGHAVAM/TANTRA_SANGRAHA/
# VAKYA_PANCHANGAM above, so MS still runs even if that enum member does not
# exist yet in your installed const.py -- only astrology_model_default stays
# at its previous value in that case, the engine's own tables are unaffected.
# ---------------------------------------------------------------------
# Main: Sun..Ketu + Lagna comparison, SS vs KK vs drik, plus sunrise/
# sunset/moonrise/moonset self-check
# ---------------------------------------------------------------------
def _fmt_dms(deg):
    d = int(deg)
    m = (deg - d) * 60
    mm = int(m)
    s = (m - mm) * 60
    return f"{d:3d}\u00b0 {mm:02d}' {s:05.2f}\""
def _fmt_time(jd):
    if jd is None:
        return "   NOT FOUND   "
    frac = (jd + 0.5) % 1.0
    total_seconds = frac * 86400.0
    hh = int(total_seconds // 3600)
    mm = int((total_seconds % 3600) // 60)
    ss = total_seconds % 60
    return f"{hh:02d}:{mm:02d}:{ss:05.2f}"
def main(jd,dob,tob,place):
    t_ss = surya_sidhantha.tithi(jd,place)
    t_kk = khanda_khaadyaka.tithi(jd,place)
    t_gl = graha_laaghavam.tithi(jd,place)
    t_ts = tantra_sangraha.tithi(jd,place)
    t_vp = vakya_panchanga.tithi(jd,place)
    t_ms = makaranda_sarini.tithi(jd,place)
    t_vs = vateshwara_sidhantha.tithi(jd,place)
    t_dr = drik.tithi(jd,place)
    print('tithi SS',t_ss,'\nKK',t_kk,'\nGL',t_gl,'\nTS',t_ts,'\nVP',t_vp,'\nMS',t_ms,'\nVS',t_vs,'\ndrik',t_dr)
    print('SNT',_snt_try(lambda: sphuta_nirnaya_tantra.tithi(jd,place)))
    n_ss = surya_sidhantha.nakshatra(jd,place)
    n_kk = khanda_khaadyaka.nakshatra(jd,place)
    n_gl = graha_laaghavam.nakshatra(jd,place)
    n_ts = tantra_sangraha.nakshatra(jd,place)
    n_vp = vakya_panchanga.nakshatra(jd,place)
    n_ms = makaranda_sarini.nakshatra(jd,place)
    n_vs = vateshwara_sidhantha.nakshatra(jd,place)
    n_dr = drik.nakshatra(jd,place)
    print('nak SS',n_ss,'\nKK',n_kk,'\nGL',n_gl,'\nTS',n_ts,'\nVP',n_vp,'\nMS',n_ms,'\nVS',n_vs,'\ndrik',n_dr)
    print('SNT',_snt_try(lambda: sphuta_nirnaya_tantra.nakshatra(jd,place)))
    n_ss = surya_sidhantha.yogam(jd,place)
    n_kk = khanda_khaadyaka.yogam(jd,place)
    n_gl = graha_laaghavam.yogam(jd,place)
    n_ts = tantra_sangraha.yogam(jd,place)
    n_vp = vakya_panchanga.yogam(jd,place)
    n_ms = makaranda_sarini.yogam(jd,place)
    n_vs = vateshwara_sidhantha.yogam(jd,place)
    n_dr = drik.yogam(jd,place)
    print('yogam SS',n_ss,'\nKK',n_kk,'\nGL',n_gl,'\nTS',n_ts,'\nVP',n_vp,'\nMS',n_ms,'\nVS',n_vs,'\ndrik',n_dr)
    print('SNT',_snt_try(lambda: sphuta_nirnaya_tantra.yogam(jd,place)))
    n_ss = surya_sidhantha.karana(jd,place)
    n_kk = khanda_khaadyaka.karana(jd,place)
    n_gl = graha_laaghavam.karana(jd,place)
    n_ts = tantra_sangraha.karana(jd,place)
    n_vp = vakya_panchanga.karana(jd,place)
    n_ms = makaranda_sarini.karana(jd,place)
    n_vs = vateshwara_sidhantha.karana(jd,place)
    n_dr = drik.karana(jd,place)
    print('karana SS',n_ss,'\nKK',n_kk,'\nGL',n_gl,'\nTS',n_ts,'\nVP',n_vp,'\nMS',n_ms,'\nVS',n_vs,'\ndrik',n_dr)
    print('SNT',_snt_try(lambda: sphuta_nirnaya_tantra.karana(jd,place)))
    pp = surya_sidhantha.dhasavarga(jd,place)
    for p,(h,long) in pp:
        print(p,utils.RAASI_LIST[h],utils.to_dms(long,is_lat_long='plong'))
    for bm in surya_sidhantha.SUPPORTED_BHAVA_METHODS:
        print("Bhava Method",bm,surya_sidhantha.bhaava_madhya(jd,place,bhava_method=bm))
    for bm in khanda_khaadyaka.SUPPORTED_BHAVA_METHODS:
        print("KK Bhava Method",bm,khanda_khaadyaka.bhaava_madhya(jd,place,bhava_method=bm))
    for bm in graha_laaghavam.SUPPORTED_BHAVA_METHODS:
        print("GL Bhava Method",bm,graha_laaghavam.bhaava_madhya(jd,place,bhava_method=bm))
    for bm in tantra_sangraha.SUPPORTED_BHAVA_METHODS:
        print("TS Bhava Method",bm,tantra_sangraha.bhaava_madhya(jd,place,bhava_method=bm))
    for bm in vakya_panchanga.SUPPORTED_BHAVA_METHODS:
        print("VP Bhava Method",bm,vakya_panchanga.bhaava_madhya(jd,place,bhava_method=bm))
    for bm in makaranda_sarini.SUPPORTED_BHAVA_METHODS:
        print("MS Bhava Method",bm,makaranda_sarini.bhaava_madhya(jd,place,bhava_method=bm))
    for bm in vateshwara_sidhantha.SUPPORTED_BHAVA_METHODS:
        print("VS Bhava Method",bm,vateshwara_sidhantha.bhaava_madhya(jd,place,bhava_method=bm))
    try:
        for bm in sphuta_nirnaya_tantra.SUPPORTED_BHAVA_METHODS:
            print("SNT Bhava Method",bm,_snt_try(lambda: sphuta_nirnaya_tantra.bhaava_madhya(jd,place,bhava_method=bm)))
    except Exception as e:
        print("SNT Bhava Method ERROR:",e)
    planet = const._SATURN
    ncp = surya_sidhantha.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('SS next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = khanda_khaadyaka.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('KK next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = graha_laaghavam.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('GL next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = tantra_sangraha.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('TS next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = vakya_panchanga.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('VP next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = makaranda_sarini.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('MS next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = vateshwara_sidhantha.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('VS next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    try:
        ncp = sphuta_nirnaya_tantra.next_planet_retrograde_change_date(planet,dob,place)
        y,m,d,fh = utils.jd_to_gregorian(ncp[0])
        print('SNT next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    except Exception as e:
        print('SNT next planet retro ERROR:',e)
    ncp = drik.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('drik next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    sr = surya_sidhantha.sunrise(jd,place)
    kr = khanda_khaadyaka.sunrise(jd,place)
    gr = graha_laaghavam.sunrise(jd,place)
    tr = tantra_sangraha.sunrise(jd,place)
    vr = vakya_panchanga.sunrise(jd,place)
    mr_sun = makaranda_sarini.sunrise(jd,place)
    vsr_sun = vateshwara_sidhantha.sunrise(jd,place)
    print('sunrise SS',sr[1],'KK',kr[1],'GL',gr[1],'TS',tr[1],'VP',vr[1],'MS',mr_sun[1],'VS',vsr_sun[1],'drik',drik.sunrise(jd,place)[1])
    snt_sunrise = _snt_try(lambda: sphuta_nirnaya_tantra.sunrise(jd,place))
    print('sunrise SNT',_snt_idx(snt_sunrise))
    ncp = surya_sidhantha.next_conjunction_of_planet_pair(jd,place,const._SUN,'L',separation_angle=180)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('next_conjunction_of_planet_pair',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    se = surya_sidhantha.sunset(jd,place)
    ke = khanda_khaadyaka.sunset(jd,place)
    ge = graha_laaghavam.sunset(jd,place)
    te = tantra_sangraha.sunset(jd,place)
    ve = vakya_panchanga.sunset(jd,place)
    me_sun = makaranda_sarini.sunset(jd,place)
    vse_sun = vateshwara_sidhantha.sunset(jd,place)
    print('sunset SS',se[1],'KK',ke[1],'GL',ge[1],'TS',te[1],'VP',ve[1],'MS',me_sun[1],'VS',vse_sun[1],'drik',drik.sunset(jd,place)[1])
    snt_sunset = _snt_try(lambda: sphuta_nirnaya_tantra.sunset(jd,place))
    print('sunset SNT',_snt_idx(snt_sunset))
    ncp = surya_sidhantha.next_conjunction_of_planet_pair(jd,place,const._SUN,'L')
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('Moon/Lagna/0',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    sr = surya_sidhantha.moonrise(jd,place)
    kr = khanda_khaadyaka.moonrise(jd,place)
    gr = graha_laaghavam.moonrise(jd,place)
    tr = tantra_sangraha.moonrise(jd,place)
    vr = vakya_panchanga.moonrise(jd,place)
    mr_moon = makaranda_sarini.moonrise(jd,place)
    vsr_moon = vateshwara_sidhantha.moonrise(jd,place)
    print('moonrise SS',sr[1] if sr else None,'KK',kr[1] if kr else None,
          'GL',gr[1] if gr else None,'TS',tr[1] if tr else None,'VP',vr[1] if vr else None,
          'MS',mr_moon[1] if mr_moon else None,'VS',vsr_moon[1] if vsr_moon else None,'drik',drik.moonrise(jd,place)[1])
    snt_moonrise = _snt_try(lambda: sphuta_nirnaya_tantra.moonrise(jd,place))
    print('moonrise SNT',_snt_idx(snt_moonrise))
    ncp = surya_sidhantha.next_conjunction_of_planet_pair(jd,place,const._MOON,'L',separation_angle=180)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('Moon/Lagna/180',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    sr = surya_sidhantha.moonset(jd,place)
    ke = khanda_khaadyaka.moonset(jd,place)
    ge = graha_laaghavam.moonset(jd,place)
    te = tantra_sangraha.moonset(jd,place)
    ve = vakya_panchanga.moonset(jd,place)
    me_moon = makaranda_sarini.moonset(jd,place)
    vse_moon = vateshwara_sidhantha.moonset(jd,place)
    print('moonset SS',sr[1] if sr else None,'KK',ke[1] if ke else None,
          'GL',ge[1] if ge else None,'TS',te[1] if te else None,'VP',ve[1] if ve else None,
          'MS',me_moon[1] if me_moon else None,'VS',vse_moon[1] if vse_moon else None,'drik',drik.moonset(jd,place)[1])
    snt_moonset = _snt_try(lambda: sphuta_nirnaya_tantra.moonset(jd,place))
    print('moonset SNT',_snt_idx(snt_moonset))
    test_cases = [
        ("Chicago, 10-Jan-2016 00:00", drik.Place('Chicago', 41.8781, -87.6298, -6.0),
         drik.Date(2016, 1, 10), (0, 0, 0)),
        ("Bangalore, 5-Feb-1962 midnight", drik.Place('Bangalore', 12.9716, 77.5946, 5.5),
         drik.Date(1962, 2, 5), (0, 0, 0)),
        ("Hoffman Estates, 15-Sep-2026 19:00", drik.Place('Hoffman Estates', 42.0625, -88.1449, -5.0),
         drik.Date(2026, 9, 15), (19, 0, 0)),
        ("Kali Yuga, 22-Jan-(-3101) 12:00", drik.Place('Ujjain', 23+11/60, 75+46/60, 5.5),
         drik.Date(-3101, 1, 22), (12, 0, 0)),
    ]
    bodies = [
        ('Sun', const._SUN), ('Moon', const._MOON), ('Mars', const._MARS),
        ('Mercury', const._MERCURY), ('Jupiter', const._JUPITER),
        ('Venus', const._VENUS), ('Saturn', const._SATURN),
        ('Rahu', const._RAHU), ('Ketu', const._KETU),
        ('Lagna', 'L'),
    ]
    # --- Planetary longitude + Lagna: DRIK vs SURYA_SIDDHANTHA vs KK vs GL, side by side ---
    for label, place, dob, tob in test_cases:
        jd = utils.julian_day_number(dob, tob)
        jd_utc = jd - place.timezone / 24.0
        print("=" * 120)
        print(label)
        print("=" * 120)
        header = (f"{'Body':9s}{'DRIK':>22s}{'SURYA_SIDDHANTHA':>22s}"
                  f"{'KHANDAKHADYAKA':>22s}{'GRAHA_LAAGHAVAM':>22s}{'TANTRA_SANGRAHA':>22s}{'VAKYA_PANCHANGAM':>22s}"
                  f"{'MAKARANDA_SARINI':>22s}{'VATESHWARA_SIDHANTHA':>22s}")
        print(header)
        print("-" * len(header))
        snt_rows = []
        for body_name, body in bodies:
            if body == 'L':
                asc = drik.ascendant(jd, place)
                drik_val = asc[0] * 30 + asc[1]
                ss_asc = surya_sidhantha.ascendant(jd, place)
                ss_val = ss_asc[0] * 30 + ss_asc[1]      # FIXED: unpack the same way as drik_val
                kk_asc = khanda_khaadyaka.ascendant(jd, place)
                kk_val = kk_asc[0] * 30 + kk_asc[1]
                gl_asc = graha_laaghavam.ascendant(jd, place)
                gl_val = gl_asc[0] * 30 + gl_asc[1]
                ts_asc = tantra_sangraha.ascendant(jd, place)
                ts_val = ts_asc[0] * 30 + ts_asc[1]
                vp_asc = vakya_panchanga.ascendant(jd, place)
                vp_val = vp_asc[0] * 30 + vp_asc[1]
                ms_asc = makaranda_sarini.ascendant(jd, place)
                vs_asc = vateshwara_sidhantha.ascendant(jd, place)
                ms_val = ms_asc[0] * 30 + ms_asc[1]
                vs_val = vs_asc[0] * 30 + vs_asc[1]
            else:
                drik_val = _drik_long(jd_utc, body)
                ss_val = surya_sidhantha.sidereal_longitude(jd_utc, body,place)
                kk_val = khanda_khaadyaka.sidereal_longitude(jd_utc, body, place)
                gl_val = graha_laaghavam.sidereal_longitude(jd_utc, body, place)
                ts_val = tantra_sangraha.sidereal_longitude(jd_utc, body, place)
                vp_val = vakya_panchanga.sidereal_longitude(jd_utc, body, place)
                ms_val = makaranda_sarini.sidereal_longitude(jd_utc, body, place)
                vs_val = vateshwara_sidhantha.sidereal_longitude(jd_utc, body, place)
            row = (f"{body_name:9s}{_fmt_dms(drik_val):>22s}{_fmt_dms(ss_val):>22s}"
                  f"{_fmt_dms(kk_val):>22s}{_fmt_dms(gl_val):>22s}{_fmt_dms(ts_val):>22s}{_fmt_dms(vp_val):>22s}"
                  f"{_fmt_dms(ms_val):>22s}{_fmt_dms(vs_val):>22s}")
            print(row)
            snt_rows.append((body_name, body, drik_val, ss_val, ts_val))
        print()
        snt_header = (f"{'Body':9s}{'SPHUTA_NIRNAYA_TANTRA':>22s}{'SNT-DRIK (deg)':>16s}{'SNT-TS (deg)':>16s}{'SNT-SS (deg)':>16s}")
        print(snt_header)
        print("-" * len(snt_header))
        for body_name, body, d_val, s_val, t_val in snt_rows:
            try:
                if body == 'L':
                    snt_asc = sphuta_nirnaya_tantra.ascendant(jd, place)
                    snt_val = snt_asc[0] * 30 + snt_asc[1]
                else:
                    snt_val = sphuta_nirnaya_tantra.sidereal_longitude(jd_utc, body, place)
                dd = lambda other: f"{((snt_val - other + 180.0) % 360.0) - 180.0:+16.4f}"
                print(f"{body_name:9s}{_fmt_dms(snt_val):>22s}{dd(d_val)}{dd(t_val)}{dd(s_val)}")
            except Exception as e:
                print(f"{body_name:9s}ERROR: {e}")
        print()
    # --- Sunrise / Sunset / Moonrise / Moonset: DRIK (swisseph) vs SS vs KK vs GL, side by side ---
    for label, place, dob, tob in test_cases:
        jd = utils.julian_day_number(dob, tob)
        jd_utc = jd - place.timezone / 24.0
        print("-" * 100)
        print(label + "  (sunrise/sunset/moonrise/moonset)")
        print("-" * 100)
        sr_ss = surya_sidhantha.sunrise(jd, place)[2]
        se_ss = surya_sidhantha.sunset(jd, place)[2]
        mr_ss = surya_sidhantha.moonrise(jd, place)
        mr_ss = mr_ss[2] if mr_ss else None
        ms_ss = surya_sidhantha.moonset(jd, place)
        ms_ss = ms_ss[2] if ms_ss else None
        sr_kk = khanda_khaadyaka.sunrise(jd, place)[2]
        se_kk = khanda_khaadyaka.sunset(jd, place)[2]
        mr_kk = khanda_khaadyaka.moonrise(jd, place)
        mr_kk = mr_kk[2] if mr_kk else None
        ms_kk = khanda_khaadyaka.moonset(jd, place)
        ms_kk = ms_kk[2] if ms_kk else None
        sr_gl = graha_laaghavam.sunrise(jd, place)[2]
        se_gl = graha_laaghavam.sunset(jd, place)[2]
        mr_gl = graha_laaghavam.moonrise(jd, place)
        mr_gl = mr_gl[2] if mr_gl else None
        ms_gl = graha_laaghavam.moonset(jd, place)
        ms_gl = ms_gl[2] if ms_gl else None
        sr_ts = tantra_sangraha.sunrise(jd, place)[2]
        se_ts = tantra_sangraha.sunset(jd, place)[2]
        mr_ts = tantra_sangraha.moonrise(jd, place)
        mr_ts = mr_ts[2] if mr_ts else None
        ms_ts = tantra_sangraha.moonset(jd, place)
        ms_ts = ms_ts[2] if ms_ts else None
        sr_vp = vakya_panchanga.sunrise(jd, place)[2]
        se_vp = vakya_panchanga.sunset(jd, place)[2]
        mr_vp = vakya_panchanga.moonrise(jd, place)
        mr_vp = mr_vp[2] if mr_vp else None
        ms_vp = vakya_panchanga.moonset(jd, place)
        ms_vp = ms_vp[2] if ms_vp else None
        mks_sr = makaranda_sarini.sunrise(jd, place)[2]
        vsk_sr = vateshwara_sidhantha.sunrise(jd, place)[2]
        mks_se = makaranda_sarini.sunset(jd, place)[2]
        vsk_se = vateshwara_sidhantha.sunset(jd, place)[2]
        mks_mr = makaranda_sarini.moonrise(jd, place)
        vsk_mr = vateshwara_sidhantha.moonrise(jd, place)
        mks_mr = mks_mr[2] if mks_mr else None
        vsk_mr = vsk_mr[2] if vsk_mr else None
        mks_ms = makaranda_sarini.moonset(jd, place)
        vsk_ms = vateshwara_sidhantha.moonset(jd, place)
        mks_ms = mks_ms[2] if mks_ms else None
        vsk_ms = vsk_ms[2] if vsk_ms else None
        if surya_sidhantha._HAVE_SWE:
            jd_midnight_ut = math.floor(jd_utc - 0.5) + 0.5
            geopos = (place.longitude, place.latitude, 0.0)
            sr_drik = drik.sunrise(jd,place)[2]
            se_drik = drik.sunset(jd,place)[2]
            mr_drik = drik.moonrise(jd,place)[2]
            ms_drik = drik.moonset(jd,place)[2]
        else:
            sr_drik = se_drik = mr_drik = ms_drik = None
        print(f"Sunrise:  SS/KK/GL/TS/VP/MS/VS/Drik {_fmt_time(sr_ss)} {_fmt_time(sr_kk)} {_fmt_time(sr_gl)} {_fmt_time(sr_ts)} {_fmt_time(sr_vp)} {_fmt_time(mks_sr)} {_fmt_time(vsk_sr)} {_fmt_time(sr_drik)}")
        print(f"Sunset:   SS/KK/GL/TS/VP/MS/VS/Drik {_fmt_time(se_ss)} {_fmt_time(se_kk)} {_fmt_time(se_gl)} {_fmt_time(se_ts)} {_fmt_time(se_vp)} {_fmt_time(mks_se)} {_fmt_time(vsk_se)} {_fmt_time(se_drik)}")
        print(f"Moonrise: SS/KK/GL/TS/VP/MS/VS/Drik {_fmt_time(mr_ss)} {_fmt_time(mr_kk)} {_fmt_time(mr_gl)} {_fmt_time(mr_ts)} {_fmt_time(mr_vp)} {_fmt_time(mks_mr)} {_fmt_time(vsk_mr)} {_fmt_time(mr_drik)}")
        print(f"Moonset:  SS/KK/GL/TS/VP/MS/VS/Drik {_fmt_time(ms_ss)} {_fmt_time(ms_kk)} {_fmt_time(ms_gl)} {_fmt_time(ms_ts)} {_fmt_time(ms_vp)} {_fmt_time(mks_ms)} {_fmt_time(vsk_ms)} {_fmt_time(ms_drik)}")
        print(f"Sunrise:  SNT {_snt_time(lambda: sphuta_nirnaya_tantra.sunrise(jd, place))}")
        print(f"Sunset:   SNT {_snt_time(lambda: sphuta_nirnaya_tantra.sunset(jd, place))}")
        print(f"Moonrise: SNT {_snt_time(lambda: sphuta_nirnaya_tantra.moonrise(jd, place))}")
        print(f"Moonset:  SNT {_snt_time(lambda: sphuta_nirnaya_tantra.moonset(jd, place))}")
## V5.0 -- regression test for sankranti timezone-double-count + date-rollback bugs (fixed this session)
def test_sankranti_consistency(place):
    print("=" * 70)
    print("SANKRANTI CONSISTENCY (next/previous_sankranti_date vs tamil_solar_month_and_date)")
    print("=" * 70)
    rules = []
    for rule_name, gh in (("TAMIL_NADU_SUNSET_RULE", None), ("BEFORE_GHATIKAS", 13),
                          ("SUNRISE_TO_SUNRISE", None)):
        rule = getattr(const.SANKRANTI_RULE, rule_name, None)
        if rule is not None:
            rules.append((rule_name, rule, gh))
    test_dates = [drik.Date(y, m, 15) for y in (1996, 2005, 2016, 2026) for m in (1, 4, 7, 10)]
    for label, mod in (("SS", surya_sidhantha), ("KK", khanda_khaadyaka), ("GL", graha_laaghavam),
                       ("TS", tantra_sangraha), ("VP", vakya_panchanga), ("MS", makaranda_sarini), ("VS", vateshwara_sidhantha),
                       ("drik", drik)):
        next_fn = getattr(mod, 'next_sankranti_date', None)
        prev_fn = getattr(mod, 'previous_sankranti_date', None)
        tmd_fn = getattr(mod, 'tamil_solar_month_and_date', None)
        if next_fn is None or prev_fn is None or tmd_fn is None:
            print(f"{label:6s} SKIPPED: missing next/previous_sankranti_date/tamil_solar_month_and_date")
            continue
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
        print(f"{label:6s} Total checks: {total}   Mismatches: {len(mismatches)}")
        for m in mismatches:
            print(f"{label:6s}   MISMATCH: {m}")
    for label, mod in (("SNT", sphuta_nirnaya_tantra),):
        next_fn = getattr(mod, 'next_sankranti_date', None)
        prev_fn = getattr(mod, 'previous_sankranti_date', None)
        tmd_fn = getattr(mod, 'tamil_solar_month_and_date', None)
        if next_fn is None or prev_fn is None or tmd_fn is None:
            print(f"{label:6s} SKIPPED: missing next/previous_sankranti_date/tamil_solar_month_and_date")
            continue
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
        print(f"{label:6s} Total checks: {total}   Mismatches: {len(mismatches)}")
        for m in mismatches:
            print(f"{label:6s}   MISMATCH: {m}")

def test_batch5(jd, place, dob, tob):
    print("="*80)
    print("SOLAR UPAGRAHAS")
    print("="*80)
    jd_utc = jd - place.timezone/24.0
    sun_long_ss = surya_sidhantha.sidereal_longitude(jd_utc, const._SUN,place)
    sun_long_kk = khanda_khaadyaka.sidereal_longitude(jd_utc, const._SUN, place)
    sun_long_gl = graha_laaghavam.sidereal_longitude(jd_utc, const._SUN, place)
    sun_long_ts = tantra_sangraha.sidereal_longitude(jd_utc, const._SUN, place)
    sun_long_vp = vakya_panchanga.sidereal_longitude(jd_utc, const._SUN, place)
    sun_long_ms = makaranda_sarini.sidereal_longitude(jd_utc, const._SUN, place)
    sun_long_vs = vateshwara_sidhantha.sidereal_longitude(jd_utc, const._SUN, place)
    sun_long_snt = _snt_try(lambda: sphuta_nirnaya_tantra.sidereal_longitude(jd_utc, const._SUN, place))
    sun_long_drik = _drik_long(jd_utc, const._SUN)
    for name in const.sub_planet_list_2:
        try:
            ss_val = surya_sidhantha.solar_upagraha_longitudes(sun_long_ss, upagraha=name)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = khanda_khaadyaka.solar_upagraha_longitudes(sun_long_kk, upagraha=name)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = graha_laaghavam.solar_upagraha_longitudes(sun_long_gl, upagraha=name)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = tantra_sangraha.solar_upagraha_longitudes(sun_long_ts, upagraha=name)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vakya_panchanga.solar_upagraha_longitudes(sun_long_vp, upagraha=name)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = makaranda_sarini.solar_upagraha_longitudes(sun_long_ms, upagraha=name)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vateshwara_sidhantha.solar_upagraha_longitudes(sun_long_vs, upagraha=name)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = sphuta_nirnaya_tantra.solar_upagraha_longitudes(sun_long_snt, upagraha=name)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik.solar_upagraha_longitudes(sun_long_drik, upagraha=name)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        label = utils.resource_strings.get(name + "_str", name)
        print(f"{label:20s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:20s} SNT={snt_val}")
    print()
    print("="*80)
    print("OTHER (TIME-BASED) UPAGRAHAS")
    print("="*80)
    for label_key, func_name in const.sub_planet_dict_1.items():
        ss_func = getattr(surya_sidhantha, func_name, None)
        kk_func = getattr(khanda_khaadyaka, func_name, None)
        gl_func = getattr(graha_laaghavam, func_name, None)
        ts_func = getattr(tantra_sangraha, func_name, None)
        vp_func = getattr(vakya_panchanga, func_name, None)
        ms_func = getattr(makaranda_sarini, func_name, None)
        vs_func = getattr(vateshwara_sidhantha, func_name, None)
        snt_func = getattr(sphuta_nirnaya_tantra, func_name, None)
        drik_func = getattr(drik, func_name, None)
        label = utils.resource_strings.get(label_key, label_key)
        if ss_func is None or kk_func is None or gl_func is None or ts_func is None or drik_func is None:
            print(f"{label:20s} MISSING: ss_func={ss_func is not None} kk_func={kk_func is not None} "
                  f"gl_func={gl_func is not None} ts_func={ts_func is not None} "
                  f"drik_func={drik_func is not None} (expected name: {func_name})")
            continue
        try:
            ss_val = ss_func(dob, tob, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(dob, tob, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(dob, tob, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(dob, tob, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(dob, tob, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(dob, tob, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(dob, tob, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(dob, tob, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(dob, tob, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:20s} SNT={snt_val}")
    print()
    print("="*80)
    print("SPECIAL LAGNAS")
    print("="*80)
    for name in const._special_lagna_list:
        lookup_name = name if name != 'bhrigu_bindhu' else 'bhrigu_bindhu_lagna'
        ss_func = getattr(surya_sidhantha, lookup_name, None)
        kk_func = getattr(khanda_khaadyaka, lookup_name, None)
        gl_func = getattr(graha_laaghavam, lookup_name, None)
        ts_func = getattr(tantra_sangraha, lookup_name, None)
        vp_func = getattr(vakya_panchanga, lookup_name, None)
        ms_func = getattr(makaranda_sarini, lookup_name, None)
        vs_func = getattr(vateshwara_sidhantha, lookup_name, None)
        snt_func = getattr(sphuta_nirnaya_tantra, lookup_name, None)
        drik_func = getattr(drik, lookup_name, None)
        label = utils.resource_strings.get(name + "_str", name)
        if name in ('varnada_lagna',):
            print(f"{label:20s} SKIPPED (lives in charts.py, different signature -- test separately)")
            continue
        if ss_func is None or kk_func is None or gl_func is None or ts_func is None or drik_func is None:
            print(f"{label:20s} MISSING: ss_func={ss_func is not None} kk_func={kk_func is not None} "
                  f"gl_func={gl_func is not None} ts_func={ts_func is not None} "
                  f"drik_func={drik_func is not None} (expected name: {lookup_name})")
            continue
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(jd, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(jd, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(jd, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(jd, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(jd, place) if ms_func is not None else "MISSING"
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(jd, place) if vs_func is not None else "MISSING"
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(jd, place) if snt_func is not None else "MISSING"
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:20s} SNT={snt_val}")
def test_batch6(panchanga_date, place):
    print("=" * 70)
    print("BATCH 6: SANKRANTI / SOLAR-CALENDAR -- SS vs KK vs GL vs drik")
    print("=" * 70)
    for label in ("previous_sankranti_date", "next_sankranti_date",
                  "tamil_solar_month_and_date", "days_in_tamil_month"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try:
            ss_val = ss_func(panchanga_date, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(panchanga_date, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(panchanga_date, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(panchanga_date, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(panchanga_date, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(panchanga_date, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(panchanga_date, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(panchanga_date, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(panchanga_date, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:28s} SNT={snt_val}")
    jd = utils.gregorian_to_jd(panchanga_date)
    try:
        ss_val = surya_sidhantha.solar_month_date(jd, place)
    except Exception as e:
        ss_val = f"ERROR: {e}"
    try:
        kk_val = khanda_khaadyaka.solar_month_date(jd, place)
    except Exception as e:
        kk_val = f"ERROR: {e}"
    try:
        gl_val = graha_laaghavam.solar_month_date(jd, place)
    except Exception as e:
        gl_val = f"ERROR: {e}"
    try:
        ts_val = tantra_sangraha.solar_month_date(jd, place)
    except Exception as e:
        ts_val = f"ERROR: {e}"
    try:
        vp_val = vakya_panchanga.solar_month_date(jd, place)
    except Exception as e:
        vp_val = f"ERROR: {e}"
    try:
        ms_val = makaranda_sarini.solar_month_date(jd, place)
    except Exception as e:
        ms_val = f"ERROR: {e}"
    try:
        vs_val = vateshwara_sidhantha.solar_month_date(jd, place)
    except Exception as e:
        vs_val = f"ERROR: {e}"
    try:
        snt_val = sphuta_nirnaya_tantra.solar_month_date(jd, place)
    except Exception as e:
        snt_val = f"ERROR: {e}"
    try:
        drik_val = drik.solar_month_date(jd, place)
    except Exception as e:
        drik_val = f"ERROR: {e}"
    print(f"{'solar_month_date':28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
    print(f"{'solar_month_date':28s} SNT={snt_val}")
def test_batch7(jd, place):
    print("=" * 70)
    print("BATCH 7: WEEKDAY + KAALA-VIBHAGA -- SS vs KK vs GL vs drik")
    print("=" * 70)
    simple_funcs = ("vaara", "trikalam", "raahu_kaalam", "yamaganda_kaalam", "gulikai_kaalam",
                    "durmuhurtam", "abhijit_muhurta", "gauri_choghadiya", "amrit_kaalam",
                    "shubha_hora", "brahma_muhurtha", "godhuli_muhurtha", "sandhya_periods",
                    "vijaya_muhurtha", "nishita_kaala", "nishita_muhurtha", "tamil_jaamam",
                    "muhurthas")
    for label in simple_funcs:
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(jd, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(jd, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(jd, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(jd, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(jd, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(jd, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(jd, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}\n{'':20s} KK={kk_val}\n{'':20s} GL={gl_val}\n{'':20s} TS={ts_val}\n{'':20s} VP={vp_val}\n{'':20s} MS={ms_val}\n{'':20s} VS={vs_val}\n{'':20s} drik={drik_val}")
        print(f"{'':20s} SNT={snt_val}")
    print(f"{'civil_weekday':20s} SS={surya_sidhantha.civil_weekday(jd)}   "
          f"KK={khanda_khaadyaka.civil_weekday(jd)}   GL={graha_laaghavam.civil_weekday(jd)}   "
          f"TS={tantra_sangraha.civil_weekday(jd)}   "
          f"VP={vakya_panchanga.civil_weekday(jd)}   "
          f"MS={makaranda_sarini.civil_weekday(jd)}   VS={vateshwara_sidhantha.civil_weekday(jd)}   "
          f"drik={drik.civil_weekday(jd)}")
    print(f"{'civil_weekday':20s} SNT={_snt_try(lambda: sphuta_nirnaya_tantra.civil_weekday(jd))}")
def test_batch8(jd, place):
    print("=" * 70)
    print("BATCH 8: PANCHAKA / CHANDRABALAM / THAARAABALAM -- SS vs KK vs GL vs drik")
    print("=" * 70)
    for label in ("udhaya_lagna_muhurtha", "thaaraabalam", "chandrabalam",
                  "panchaka_rahitha", "next_panchaka_days", "chandrashtama"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(jd, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(jd, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(jd, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(jd, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(jd, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(jd, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(jd, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:24s} SS={ss_val}\n{'':24s} KK={kk_val}\n{'':24s} GL={gl_val}\n{'':24s} TS={ts_val}\n{'':24s} VP={vp_val}\n{'':24s} MS={ms_val}\n{'':24s} VS={vs_val}\n{'':24s} drik={drik_val}")
        print(f"{'':24s} SNT={snt_val}")
def test_batch9(jd, place):
    print("=" * 70)
    print("BATCH 9: LUNAR CALENDAR CORE -- SS vs KK vs GL vs drik")
    print("=" * 70)
    ti_ss = surya_sidhantha.tithi(jd, place)[0]
    ti_kk = khanda_khaadyaka.tithi(jd, place)[0]
    ti_gl = graha_laaghavam.tithi(jd, place)[0]
    ti_drik = drik.tithi(jd, place)[0]
    ti_ts = tantra_sangraha.tithi(jd, place)[0]
    ti_vp = vakya_panchanga.tithi(jd, place)[0]
    ti_ms = makaranda_sarini.tithi(jd, place)[0]
    ti_vs = vateshwara_sidhantha.tithi(jd, place)[0]
    ti_snt = _snt_try(lambda: sphuta_nirnaya_tantra.tithi(jd, place)[0])
    for label, ss_call, kk_call, gl_call, ts_call, vp_call, ms_call, vs_call, drik_call in (
        ("new_moon", lambda: surya_sidhantha.new_moon(jd, place, ti_ss, -1),
                     lambda: khanda_khaadyaka.new_moon(jd, place, ti_kk, -1),
                     lambda: graha_laaghavam.new_moon(jd, place, ti_gl, -1),
                     lambda: tantra_sangraha.new_moon(jd, place, ti_ts, -1),
                     lambda: vakya_panchanga.new_moon(jd, place, ti_vp, -1),
                     lambda: makaranda_sarini.new_moon(jd, place, ti_ms, -1),
                     lambda: vateshwara_sidhantha.new_moon(jd, place, ti_vs, -1),
                     lambda: drik.new_moon(jd, place, ti_drik, -1)),
        ("full_moon", lambda: surya_sidhantha.full_moon(jd, place, ti_ss, -1),
                      lambda: khanda_khaadyaka.full_moon(jd, place, ti_kk, -1),
                      lambda: graha_laaghavam.full_moon(jd, place, ti_gl, -1),
                      lambda: tantra_sangraha.full_moon(jd, place, ti_ts, -1),
                      lambda: vakya_panchanga.full_moon(jd, place, ti_vp, -1),
                      lambda: makaranda_sarini.full_moon(jd, place, ti_ms, -1),
                      lambda: vateshwara_sidhantha.full_moon(jd, place, ti_vs, -1),
                      lambda: drik.full_moon(jd, place, ti_drik, -1)),
        ("lunar_month", lambda: surya_sidhantha.lunar_month(jd, place),
                        lambda: khanda_khaadyaka.lunar_month(jd, place),
                        lambda: graha_laaghavam.lunar_month(jd, place),
                        lambda: tantra_sangraha.lunar_month(jd, place),
                        lambda: vakya_panchanga.lunar_month(jd, place),
                        lambda: makaranda_sarini.lunar_month(jd, place),
                        lambda: vateshwara_sidhantha.lunar_month(jd, place),
                        lambda: drik.lunar_month(jd, place)),
        ("lunar_month_date", lambda: surya_sidhantha.lunar_month_date(jd, place),
                             lambda: khanda_khaadyaka.lunar_month_date(jd, place),
                             lambda: graha_laaghavam.lunar_month_date(jd, place),
                             lambda: tantra_sangraha.lunar_month_date(jd, place),
                             lambda: vakya_panchanga.lunar_month_date(jd, place),
                             lambda: makaranda_sarini.lunar_month_date(jd, place),
                             lambda: vateshwara_sidhantha.lunar_month_date(jd, place),
                             lambda: drik.lunar_month_date(jd, place)),
        ("next_lunar_month", lambda: surya_sidhantha.next_lunar_month(jd, place),
                            lambda: khanda_khaadyaka.next_lunar_month(jd, place),
                            lambda: graha_laaghavam.next_lunar_month(jd, place),
                            lambda: tantra_sangraha.next_lunar_month(jd, place),
                            lambda: vakya_panchanga.next_lunar_month(jd, place),
                            lambda: makaranda_sarini.next_lunar_month(jd, place),
                            lambda: vateshwara_sidhantha.next_lunar_month(jd, place),
                            lambda: drik.next_lunar_month(jd, place)),
        ("previous_lunar_month", lambda: surya_sidhantha.previous_lunar_month(jd, place),
                                lambda: khanda_khaadyaka.previous_lunar_month(jd, place),
                                lambda: graha_laaghavam.previous_lunar_month(jd, place),
                                lambda: tantra_sangraha.previous_lunar_month(jd, place),
                                lambda: vakya_panchanga.previous_lunar_month(jd, place),
                                lambda: makaranda_sarini.previous_lunar_month(jd, place),
                                lambda: vateshwara_sidhantha.previous_lunar_month(jd, place),
                                lambda: drik.previous_lunar_month(jd, place)),
        ("next_lunar_year", lambda: surya_sidhantha.next_lunar_year(jd, place),
                            lambda: khanda_khaadyaka.next_lunar_year(jd, place),
                            lambda: graha_laaghavam.next_lunar_year(jd, place),
                            lambda: tantra_sangraha.next_lunar_year(jd, place),
                            lambda: vakya_panchanga.next_lunar_year(jd, place),
                            lambda: makaranda_sarini.next_lunar_year(jd, place),
                            lambda: vateshwara_sidhantha.next_lunar_year(jd, place),
                            lambda: drik.next_lunar_year(jd, place)),
        ("previous_lunar_year", lambda: surya_sidhantha.previous_lunar_year(jd, place),
                               lambda: khanda_khaadyaka.previous_lunar_year(jd, place),
                               lambda: graha_laaghavam.previous_lunar_year(jd, place),
                               lambda: tantra_sangraha.previous_lunar_year(jd, place),
                               lambda: vakya_panchanga.previous_lunar_year(jd, place),
                               lambda: makaranda_sarini.previous_lunar_year(jd, place),
                               lambda: vateshwara_sidhantha.previous_lunar_year(jd, place),
                               lambda: drik.previous_lunar_year(jd, place)),
    ):
        try:
            ss_v = ss_call()
        except Exception as e:
            ss_v = f"ERROR: {e}"
        try:
            kk_v = kk_call()
        except Exception as e:
            kk_v = f"ERROR: {e}"
        try:
            gl_v = gl_call()
        except Exception as e:
            gl_v = f"ERROR: {e}"
        try:
            ts_v = ts_call()
        except Exception as e:
            ts_v = f"ERROR: {e}"
        try:
            vp_v = vp_call()
        except Exception as e:
            vp_v = f"ERROR: {e}"
        try:
            ms_v = ms_call()
        except Exception as e:
            ms_v = f"ERROR: {e}"
        try:
            vs_v = vs_call()
        except Exception as e:
            vs_v = f"ERROR: {e}"
        try:
            drik_v = drik_call()
        except Exception as e:
            drik_v = f"ERROR: {e}"
        print(f"{label:22s} SS={ss_v}\n{'':22s} KK={kk_v}\n{'':22s} GL={gl_v}\n{'':22s} TS={ts_v}\n{'':22s} VP={vp_v}\n{'':22s} MS={ms_v}\n{'':22s} VS={vs_v}\n{'':22s} drik={drik_v}")
    for label, snt_call in (
        ('new_moon', lambda: sphuta_nirnaya_tantra.new_moon(jd, place, ti_snt, -1)),
        ('full_moon', lambda: sphuta_nirnaya_tantra.full_moon(jd, place, ti_snt, -1)),
        ('lunar_month', lambda: sphuta_nirnaya_tantra.lunar_month(jd, place)),
        ('lunar_month_date', lambda: sphuta_nirnaya_tantra.lunar_month_date(jd, place)),
        ('next_lunar_month', lambda: sphuta_nirnaya_tantra.next_lunar_month(jd, place)),
        ('previous_lunar_month', lambda: sphuta_nirnaya_tantra.previous_lunar_month(jd, place)),
        ('next_lunar_year', lambda: sphuta_nirnaya_tantra.next_lunar_year(jd, place)),
        ('previous_lunar_year', lambda: sphuta_nirnaya_tantra.previous_lunar_year(jd, place)),
    ):
        try:
            snt_v = snt_call()
        except Exception as e:
            snt_v = f"ERROR: {e}"
        print(f"{label:22s} SNT={snt_v}")
    py, pm, pd, _ = utils.jd_to_gregorian(jd)
    pdate = drik.Date(py, pm, pd)
    try:
        ss_v = surya_sidhantha.samvatsara(pdate, place)
    except Exception as e:
        ss_v = f"ERROR: {e}"
    try:
        kk_v = khanda_khaadyaka.samvatsara(pdate, place)
    except Exception as e:
        kk_v = f"ERROR: {e}"
    try:
        gl_v = graha_laaghavam.samvatsara(pdate, place)
    except Exception as e:
        gl_v = f"ERROR: {e}"
    try:
        ts_v = tantra_sangraha.samvatsara(pdate, place)
    except Exception as e:
        ts_v = f"ERROR: {e}"
    try:
        vp_v = vakya_panchanga.samvatsara(pdate, place)
    except Exception as e:
        vp_v = f"ERROR: {e}"
    try:
        ms_v = makaranda_sarini.samvatsara(pdate, place)
    except Exception as e:
        ms_v = f"ERROR: {e}"
    try:
        vs_v = vateshwara_sidhantha.samvatsara(pdate, place)
    except Exception as e:
        vs_v = f"ERROR: {e}"
    try:
        snt_v = sphuta_nirnaya_tantra.samvatsara(pdate, place)
    except Exception as e:
        snt_v = f"ERROR: {e}"
    try:
        drik_v = drik.samvatsara(pdate, place)
    except Exception as e:
        drik_v = f"ERROR: {e}"
    print(f"{'samvatsara':22s} SS={ss_v}   KK={kk_v}   GL={gl_v}   TS={ts_v}   VP={vp_v}   MS={ms_v}   VS={vs_v}   drik={drik_v}")
    print(f"{'samvatsara':22s} SNT={snt_v}")
    for maasa in (1, 6):
        print(f"{'ritu(' + str(maasa) + ')':22s} SS={surya_sidhantha.ritu(maasa)}   "
              f"KK={khanda_khaadyaka.ritu(maasa)}   GL={graha_laaghavam.ritu(maasa)}   "
              f"TS={tantra_sangraha.ritu(maasa)}   "
              f"VP={vakya_panchanga.ritu(maasa)}   "
              f"MS={makaranda_sarini.ritu(maasa)}   VS={vateshwara_sidhantha.ritu(maasa)}   "
              f"drik={drik.ritu(maasa)}")
        print(f"{'ritu(' + str(maasa) + ')':22s} SNT={_snt_try(lambda: sphuta_nirnaya_tantra.ritu(maasa))}")
    try:
        ss_v = surya_sidhantha.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        ss_v = f"ERROR: {e}"
    try:
        kk_v = khanda_khaadyaka.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        kk_v = f"ERROR: {e}"
    try:
        gl_v = graha_laaghavam.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        gl_v = f"ERROR: {e}"
    try:
        ts_v = tantra_sangraha.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        ts_v = f"ERROR: {e}"
    try:
        vp_v = vakya_panchanga.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        vp_v = f"ERROR: {e}"
    try:
        ms_v = makaranda_sarini.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        ms_v = f"ERROR: {e}"
    try:
        vs_v = vateshwara_sidhantha.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        vs_v = f"ERROR: {e}"
    try:
        snt_v = sphuta_nirnaya_tantra.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        snt_v = f"ERROR: {e}"
    try:
        drik_v = drik.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        drik_v = f"ERROR: {e}"
    print(f"{'vedic_date(SOLAR)':22s} SS={ss_v}   KK={kk_v}   GL={gl_v}   TS={ts_v}   VP={vp_v}   MS={ms_v}   VS={vs_v}   drik={drik_v}")
    print(f"{'vedic_date(SOLAR)':22s} SNT={snt_v}")
def test_batch10(jd, place):
    print("=" * 70)
    print("BATCH 10: MISC YOGA / MUHURTA FLAGS -- SS vs KK vs GL vs drik")
    print("=" * 70)
    simple_funcs = ("tamil_yogam", "anandhaadhi_yoga", "triguna", "vivaha_chakra_palan",
                    "amrita_gadiya", "varjyam", "shiva_vaasa", "agni_vaasa", "pushkara_yoga",
                    "aadal_yoga", "vidaal_yoga", "disha_shool", "yogini_vaasa",
                    "fraction_moon_yet_to_traverse", "vedic_time", "midday", "midnight",
                    "graha_drekkana", "is_night_birth")
    for label in simple_funcs:
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(jd, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(jd, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(jd, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(jd, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(jd, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(jd, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(jd, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:24s} SS={ss_val}\n{'':24s} KK={kk_val}\n{'':24s} GL={gl_val}\n{'':24s} TS={ts_val}\n{'':24s} VP={vp_val}\n{'':24s} MS={ms_val}\n{'':24s} VS={vs_val}\n{'':24s} drik={drik_val}")
        print(f"{'':24s} SNT={snt_val}")
    for label, ss_call, kk_call, gl_call, ts_call, vp_call, ms_call, vs_call, drik_call in (
        ("nava_thaara('L')", lambda: surya_sidhantha.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: khanda_khaadyaka.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: graha_laaghavam.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: tantra_sangraha.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: vakya_panchanga.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: makaranda_sarini.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: vateshwara_sidhantha.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                              lambda: drik.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol)),
        ("special_thaara('L')", lambda: surya_sidhantha.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: khanda_khaadyaka.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: graha_laaghavam.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: tantra_sangraha.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: vakya_panchanga.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: makaranda_sarini.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: vateshwara_sidhantha.special_thaara(jd, place, base_star_planet=const._ascendant_symbol),
                                lambda: drik.special_thaara(jd, place, base_star_planet=const._ascendant_symbol)),
        ("nava_thaara(default)", lambda: surya_sidhantha.nava_thaara(jd, place),
                                 lambda: khanda_khaadyaka.nava_thaara(jd, place),
                                 lambda: graha_laaghavam.nava_thaara(jd, place),
                                 lambda: tantra_sangraha.nava_thaara(jd, place),
                                 lambda: vakya_panchanga.nava_thaara(jd, place),
                                 lambda: makaranda_sarini.nava_thaara(jd, place),
                                 lambda: vateshwara_sidhantha.nava_thaara(jd, place),
                                 lambda: drik.nava_thaara(jd, place)),
    ):
        try:
            ss_v = ss_call()
        except Exception as e:
            ss_v = f"ERROR: {e}"
        try:
            kk_v = kk_call()
        except Exception as e:
            kk_v = f"ERROR: {e}"
        try:
            gl_v = gl_call()
        except Exception as e:
            gl_v = f"ERROR: {e}"
        try:
            ts_v = ts_call()
        except Exception as e:
            ts_v = f"ERROR: {e}"
        try:
            vp_v = vp_call()
        except Exception as e:
            vp_v = f"ERROR: {e}"
        try:
            ms_v = ms_call()
        except Exception as e:
            ms_v = f"ERROR: {e}"
        try:
            vs_v = vs_call()
        except Exception as e:
            vs_v = f"ERROR: {e}"
        try:
            drik_v = drik_call()
        except Exception as e:
            drik_v = f"ERROR: {e}"
        print(f"{label:24s} SS={ss_v}\n{'':24s} KK={kk_v}\n{'':24s} GL={gl_v}\n{'':24s} TS={ts_v}\n{'':24s} VP={vp_v}\n{'':24s} MS={ms_v}\n{'':24s} VS={vs_v}\n{'':24s} drik={drik_v}")
    for label, snt_call in (
        ("nava_thaara('L')", lambda: sphuta_nirnaya_tantra.nava_thaara(jd, place, base_star_planet=const._ascendant_symbol)),
        ("special_thaara('L')", lambda: sphuta_nirnaya_tantra.special_thaara(jd, place, base_star_planet=const._ascendant_symbol)),
        ('nava_thaara(default)', lambda: sphuta_nirnaya_tantra.nava_thaara(jd, place)),
    ):
        try:
            snt_v = snt_call()
        except Exception as e:
            snt_v = f"ERROR: {e}"
        print(f"{label:24s} SNT={snt_v}")
    try:
        ss_v = surya_sidhantha.sahasra_chandrodayam(jd, place)
    except Exception as e:
        ss_v = f"ERROR: {e}"
    try:
        kk_v = khanda_khaadyaka.sahasra_chandrodayam(jd, place)
    except Exception as e:
        kk_v = f"ERROR: {e}"
    try:
        gl_v = graha_laaghavam.sahasra_chandrodayam(jd, place)
    except Exception as e:
        gl_v = f"ERROR: {e}"
    try:
        ts_v = tantra_sangraha.sahasra_chandrodayam(jd, place)
    except Exception as e:
        ts_v = f"ERROR: {e}"
    try:
        vp_v = vakya_panchanga.sahasra_chandrodayam(jd, place)
    except Exception as e:
        vp_v = f"ERROR: {e}"
    try:
        ms_v = makaranda_sarini.sahasra_chandrodayam(jd, place)
    except Exception as e:
        ms_v = f"ERROR: {e}"
    try:
        vs_v = vateshwara_sidhantha.sahasra_chandrodayam(jd, place)
    except Exception as e:
        vs_v = f"ERROR: {e}"
    try:
        snt_v = sphuta_nirnaya_tantra.sahasra_chandrodayam(jd, place)
    except Exception as e:
        snt_v = f"ERROR: {e}"
    try:
        drik_v = drik.sahasra_chandrodayam(jd, place)
    except Exception as e:
        drik_v = f"ERROR: {e}"
    print(f"{'sahasra_chandrodayam':24s} SS={ss_v}   KK={kk_v}   GL={gl_v}   TS={ts_v}   VP={vp_v}   MS={ms_v}   VS={vs_v}   drik={drik_v}")
    print(f"{'sahasra_chandrodayam':24s} SNT={snt_v}")
    print(f"{'special_tithis[0][0]':24s} SS={surya_sidhantha.special_tithis(jd, place)[0][0]}   "
          f"KK={khanda_khaadyaka.special_tithis(jd, place)[0][0]}   "
          f"GL={graha_laaghavam.special_tithis(jd, place)[0][0]}   "
          f"TS={tantra_sangraha.special_tithis(jd, place)[0][0]}   "
          f"VP={vakya_panchanga.special_tithis(jd, place)[0][0]}   "
          f"MS={makaranda_sarini.special_tithis(jd, place)[0][0]}   VS={vateshwara_sidhantha.special_tithis(jd, place)[0][0]}   "
          f"drik={drik.special_tithis(jd, place)[0][0]}")
    print(f"{'special_tithis[0][0]':24s} SNT={_snt_try(lambda: sphuta_nirnaya_tantra.special_tithis(jd, place)[0][0])}")
def test_batch11(jd, place):
    print("=" * 70)
    print("BATCH 11: YEAR-LENGTH / DASHA SUPPORT -- SS vs KK vs GL vs drik")
    print("=" * 70)
    for label in ("true_sidereal_year", "lunar_year", "savana_year", "tithi_year",
                  "true_tithi_year", "true_lunar_year", "true_tropical_year"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = kk_func(jd, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = gl_func(jd, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = ts_func(jd, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vp_func(jd, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = ms_func(jd, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vs_func(jd, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = snt_func(jd, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:20s} SNT={snt_val}")
    for dd_name in ("MEAN_SIDEREAL_YEAR", "TRUE_SIDEREAL_YEAR", "SAVANA_YEAR",
                    "MEAN_LUNAR_YEAR", "TRUE_LUNAR_YEAR", "GREGORIAN_YEAR", "TRUE_TROPICAL_YEAR",
                    "GREGORIAN_YEAR"):
        dd = getattr(const.DHASA_YEAR_DURATION, dd_name)
        try:
            ss_val = surya_sidhantha.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = khanda_khaadyaka.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = graha_laaghavam.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = tantra_sangraha.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = vakya_panchanga.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = makaranda_sarini.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = vateshwara_sidhantha.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = sphuta_nirnaya_tantra.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        try:
            drik_val = drik.dhasa_year_duration(dd, jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"dhasa_year_duration({dd_name}) SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"dhasa_year_duration({dd_name}) SNT={snt_val}")
        const.dhasa_year_duration_default = dd
        try:
            ss_start = surya_sidhantha._get_dhasa_start_jd(jd, place, 0.5, 10)
            ss_end = surya_sidhantha._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            ss_start = ss_end = f"ERROR: {e}"
        try:
            kk_start = khanda_khaadyaka._get_dhasa_start_jd(jd, place, 0.5, 10)
            kk_end = khanda_khaadyaka._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            kk_start = kk_end = f"ERROR: {e}"
        try:
            gl_start = graha_laaghavam._get_dhasa_start_jd(jd, place, 0.5, 10)
            gl_end = graha_laaghavam._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            gl_start = gl_end = f"ERROR: {e}"
        try:
            ts_start = tantra_sangraha._get_dhasa_start_jd(jd, place, 0.5, 10)
            ts_end = tantra_sangraha._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            ts_start = ts_end = f"ERROR: {e}"
        try:
            vp_start = vakya_panchanga._get_dhasa_start_jd(jd, place, 0.5, 10)
            vp_end = vakya_panchanga._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            vp_start = vp_end = f"ERROR: {e}"
        try:
            ms_start = makaranda_sarini._get_dhasa_start_jd(jd, place, 0.5, 10)
            ms_end = makaranda_sarini._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            ms_start = ms_end = f"ERROR: {e}"
        try:
            vs_start = vateshwara_sidhantha._get_dhasa_start_jd(jd, place, 0.5, 10)
            vs_end = vateshwara_sidhantha._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            vs_start = vs_end = f"ERROR: {e}"
        try:
            snt_start = sphuta_nirnaya_tantra._get_dhasa_start_jd(jd, place, 0.5, 10)
            snt_end = sphuta_nirnaya_tantra._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            snt_start = snt_end = f"ERROR: {e}"
        try:
            drik_start = drik._get_dhasa_start_jd(jd, place, 0.5, 10)
            drik_end = drik._get_dhasa_end_jd(jd, place, 10)
        except Exception as e:
            drik_start = drik_end = f"ERROR: {e}"
        ss_start_s = ss_start if isinstance(ss_start, str) else utils.jd_to_gregorian(ss_start)
        ss_end_s = ss_end if isinstance(ss_end, str) else utils.jd_to_gregorian(ss_end)
        kk_start_s = kk_start if isinstance(kk_start, str) else utils.jd_to_gregorian(kk_start)
        kk_end_s = kk_end if isinstance(kk_end, str) else utils.jd_to_gregorian(kk_end)
        gl_start_s = gl_start if isinstance(gl_start, str) else utils.jd_to_gregorian(gl_start)
        gl_end_s = gl_end if isinstance(gl_end, str) else utils.jd_to_gregorian(gl_end)
        ts_start_s = ts_start if isinstance(ts_start, str) else utils.jd_to_gregorian(ts_start)
        ts_end_s = ts_end if isinstance(ts_end, str) else utils.jd_to_gregorian(ts_end)
        vp_start_s = vp_start if isinstance(vp_start, str) else utils.jd_to_gregorian(vp_start)
        vp_end_s = vp_end if isinstance(vp_end, str) else utils.jd_to_gregorian(vp_end)
        ms_start_s = ms_start if isinstance(ms_start, str) else utils.jd_to_gregorian(ms_start)
        vs_start_s = vs_start if isinstance(vs_start, str) else utils.jd_to_gregorian(vs_start)
        snt_start_s = snt_start if isinstance(snt_start, str) else utils.jd_to_gregorian(snt_start)
        ms_end_s = ms_end if isinstance(ms_end, str) else utils.jd_to_gregorian(ms_end)
        vs_end_s = vs_end if isinstance(vs_end, str) else utils.jd_to_gregorian(vs_end)
        snt_end_s = snt_end if isinstance(snt_end, str) else utils.jd_to_gregorian(snt_end)
        drik_start_s = drik_start if isinstance(drik_start, str) else utils.jd_to_gregorian(drik_start)
        drik_end_s = drik_end if isinstance(drik_end, str) else utils.jd_to_gregorian(drik_end)
        print(f"  start/end jd [{dd_name}] SS=({ss_start_s}, {ss_end_s})")
        print(f"{'':28s} KK=({kk_start_s}, {kk_end_s})")
        print(f"{'':28s} GL=({gl_start_s}, {gl_end_s})")
        print(f"{'':28s} TS=({ts_start_s}, {ts_end_s})")
        print(f"{'':28s} VP=({vp_start_s}, {vp_end_s})")
        print(f"{'':28s} MS=({ms_start_s}, {ms_end_s})")
        print(f"{'':28s} VS=({vs_start_s}, {vs_end_s})")
        print(f"{'':28s} SNT=({snt_start_s}, {snt_end_s})")
        print(f"{'':28s} drik=({drik_start_s}, {drik_end_s})")
def test_batch12(jd, place, dob, tob):
    print("=" * 70)
    print("BATCH 12: MISC UTILITY / WRAPPERS -- SS vs KK vs GL vs drik")
    print("=" * 70)
    for label in ("planets_in_retrograde", "planets_in_stationary", "ascendant_speed"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try: ss_val = ss_func(jd, place)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = kk_func(jd, place)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = gl_func(jd, place)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = ts_func(jd, place)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vp_func(jd, place)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = ms_func(jd, place)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vs_func(jd, place)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = snt_func(jd, place)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik_func(jd, place)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:28s} SNT={snt_val}")
    for label in ("next_solar_month", "previous_solar_month", "next_solar_year", "previous_solar_year"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try: ss_val = ss_func(jd, place)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = kk_func(jd, place)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = gl_func(jd, place)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = ts_func(jd, place)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vp_func(jd, place)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = ms_func(jd, place)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vs_func(jd, place)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = snt_func(jd, place)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik_func(jd, place)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:28s} SNT={snt_val}")
    try: ss_val = surya_sidhantha.ardra_pravesha_date(jd, place)
    except Exception as e: ss_val = f"ERROR: {e}"
    try: kk_val = khanda_khaadyaka.ardra_pravesha_date(jd, place)
    except Exception as e: kk_val = f"ERROR: {e}"
    try: gl_val = graha_laaghavam.ardra_pravesha_date(jd, place)
    except Exception as e: gl_val = f"ERROR: {e}"
    try: ts_val = tantra_sangraha.ardra_pravesha_date(jd, place)
    except Exception as e: ts_val = f"ERROR: {e}"
    try: vp_val = vakya_panchanga.ardra_pravesha_date(jd, place)
    except Exception as e: vp_val = f"ERROR: {e}"
    try: ms_val = makaranda_sarini.ardra_pravesha_date(jd, place)
    except Exception as e: ms_val = f"ERROR: {e}"
    try: vs_val = vateshwara_sidhantha.ardra_pravesha_date(jd, place)
    except Exception as e: vs_val = f"ERROR: {e}"
    try: snt_val = sphuta_nirnaya_tantra.ardra_pravesha_date(jd, place)
    except Exception as e: snt_val = f"ERROR: {e}"
    try: drik_val = drik.ardra_pravesha_date(jd, place)
    except Exception as e: drik_val = f"ERROR: {e}"
    print(f"{'ardra_pravesha_date':28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
    print(f"{'ardra_pravesha_date':28s} SNT={snt_val}")
    try: ss_val = surya_sidhantha.next_solar_date(jd, place, years=5)
    except Exception as e: ss_val = f"ERROR: {e}"
    try: kk_val = khanda_khaadyaka.next_solar_date(jd, place, years=5)
    except Exception as e: kk_val = f"ERROR: {e}"
    try: gl_val = graha_laaghavam.next_solar_date(jd, place, years=5)
    except Exception as e: gl_val = f"ERROR: {e}"
    try: ts_val = tantra_sangraha.next_solar_date(jd, place, years=5)
    except Exception as e: ts_val = f"ERROR: {e}"
    try: vp_val = vakya_panchanga.next_solar_date(jd, place, years=5)
    except Exception as e: vp_val = f"ERROR: {e}"
    try: ms_val = makaranda_sarini.next_solar_date(jd, place, years=5)
    except Exception as e: ms_val = f"ERROR: {e}"
    try: vs_val = vateshwara_sidhantha.next_solar_date(jd, place, years=5)
    except Exception as e: vs_val = f"ERROR: {e}"
    try: snt_val = sphuta_nirnaya_tantra.next_solar_date(jd, place, years=5)
    except Exception as e: snt_val = f"ERROR: {e}"
    try: drik_val = drik.next_solar_date(jd, place, years=5)
    except Exception as e: drik_val = f"ERROR: {e}"
    print(f"{'next_solar_date(yrs=5)':28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
    print(f"{'next_solar_date(yrs=5)':28s} SNT={snt_val}")
    try: ss_val = surya_sidhantha.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: ss_val = f"ERROR: {e}"
    try: kk_val = khanda_khaadyaka.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: kk_val = f"ERROR: {e}"
    try: gl_val = graha_laaghavam.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: gl_val = f"ERROR: {e}"
    try: ts_val = tantra_sangraha.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: ts_val = f"ERROR: {e}"
    try: vp_val = vakya_panchanga.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: vp_val = f"ERROR: {e}"
    try: ms_val = makaranda_sarini.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: ms_val = f"ERROR: {e}"
    try: vs_val = vateshwara_sidhantha.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: vs_val = f"ERROR: {e}"
    try: snt_val = sphuta_nirnaya_tantra.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: snt_val = f"ERROR: {e}"
    try: drik_val = drik.next_annual_solar_date_approximate(dob, tob, 5)
    except Exception as e: drik_val = f"ERROR: {e}"
    print(f"{'next_annual_solar_date_approx':28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
    print(f"{'next_annual_solar_date_approx':28s} SNT={snt_val}")
    try: ss_val = surya_sidhantha.declination_of_planets(jd, place)
    except Exception as e: ss_val = f"ERROR: {e}"
    try: kk_val = khanda_khaadyaka.declination_of_planets(jd, place)
    except Exception as e: kk_val = f"ERROR: {e}"
    try: gl_val = graha_laaghavam.declination_of_planets(jd, place)
    except Exception as e: gl_val = f"ERROR: {e}"
    try: ts_val = tantra_sangraha.declination_of_planets(jd, place)
    except Exception as e: ts_val = f"ERROR: {e}"
    try: vp_val = vakya_panchanga.declination_of_planets(jd, place)
    except Exception as e: vp_val = f"ERROR: {e}"
    try: ms_val = makaranda_sarini.declination_of_planets(jd, place)
    except Exception as e: ms_val = f"ERROR: {e}"
    try: vs_val = vateshwara_sidhantha.declination_of_planets(jd, place)
    except Exception as e: vs_val = f"ERROR: {e}"
    try: snt_val = sphuta_nirnaya_tantra.declination_of_planets(jd, place)
    except Exception as e: snt_val = f"ERROR: {e}"
    try: drik_val = drik.declination_of_planets(jd, place)
    except Exception as e: drik_val = f"ERROR: {e}"
    print(f"{'declination_of_planets':28s} SS={ss_val}")
    print(f"{'':28s} KK={kk_val}")
    print(f"{'':28s} GL={gl_val}")
    print(f"{'':28s} TS={ts_val}")
    print(f"{'':28s} VP={vp_val}")
    print(f"{'':28s} MS={ms_val}")
    print(f"{'':28s} VS={vs_val}")
    print(f"{'':28s} SNT={snt_val}")
    print(f"{'':28s} drik={drik_val}")
    for label in ("kaala_longitude", "mrityu_longitude", "artha_praharaka_longitude",
                  "yama_ghantaka_longitude", "gulika_longitude", "maandi_longitude"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try: ss_val = ss_func(dob, tob, place)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = kk_func(dob, tob, place)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = gl_func(dob, tob, place)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = ts_func(dob, tob, place)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vp_func(dob, tob, place)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = ms_func(dob, tob, place)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vs_func(dob, tob, place)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = snt_func(dob, tob, place)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik_func(dob, tob, place)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:28s} SNT={snt_val}")
    for label in ("kaala_raw", "mrityu_raw", "artha_praharaka_raw",
                  "yama_ghantaka_raw", "gulika_raw", "maandi_raw"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try: ss_val = ss_func(dob, tob, place)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = kk_func(dob, tob, place)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = gl_func(dob, tob, place)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = ts_func(dob, tob, place)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vp_func(dob, tob, place)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = ms_func(dob, tob, place)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vs_func(dob, tob, place)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = snt_func(dob, tob, place)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik_func(dob, tob, place)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:28s} SNT={snt_val}")
    print(f"{'navamsa_from_long(123.4)':28s} SS={surya_sidhantha.navamsa_from_long(123.4)}   "
          f"KK={khanda_khaadyaka.navamsa_from_long(123.4)}   "
          f"GL={graha_laaghavam.navamsa_from_long(123.4)}   "
          f"TS={tantra_sangraha.navamsa_from_long(123.4)}   VP={vakya_panchanga.navamsa_from_long(123.4)}   "
          f"MS={makaranda_sarini.navamsa_from_long(123.4)}   VS={vateshwara_sidhantha.navamsa_from_long(123.4)}   drik={drik.navamsa_from_long(123.4)}")
    print(f"{'navamsa_from_long(123.4)':28s} SNT={_snt_try(lambda: sphuta_nirnaya_tantra.navamsa_from_long(123.4))}")
    print(f"{'ketu(55.0)':28s} SS={surya_sidhantha.ketu(55.0)}   "
          f"KK={khanda_khaadyaka.ketu(55.0)}   "
          f"GL={graha_laaghavam.ketu(55.0)}   "
          f"TS={tantra_sangraha.ketu(55.0)}   VP={vakya_panchanga.ketu(55.0)}   "
          f"MS={makaranda_sarini.ketu(55.0)}   VS={vateshwara_sidhantha.ketu(55.0)}   drik={drik.ketu(55.0)}")
    print(f"{'ketu(55.0)':28s} SNT={_snt_try(lambda: sphuta_nirnaya_tantra.ketu(55.0))}")
def test_batch13(jd, place):
    print("=" * 70)
    print("BATCH 13: KARAKA TITHI/YOGAM + TAMIL SOLAR MONTH VARIANTS -- SS vs KK vs GL vs drik")
    print("=" * 70)
    for label in ("karaka_tithi", "karaka_yogam"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try: ss_val = ss_func(jd, place)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = kk_func(jd, place)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = gl_func(jd, place)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = ts_func(jd, place)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vp_func(jd, place)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = ms_func(jd, place)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vs_func(jd, place)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = snt_func(jd, place)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik_func(jd, place)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:28s} SNT={snt_val}")
    py, pm, pd, _ = utils.jd_to_gregorian(jd)
    pdate = drik.Date(py, pm, pd)
    for label in ("tamil_solar_month_and_date", "tamil_solar_month_and_date_new",
                  "tamil_solar_month_and_date_V4_3_8", "tamil_solar_month_and_date_V4_3_5",
                  "tamil_solar_month_and_date_RaviAnnnaswamy"):
        ss_func = getattr(surya_sidhantha, label, None)
        kk_func = getattr(khanda_khaadyaka, label, None)
        gl_func = getattr(graha_laaghavam, label, None)
        ts_func = getattr(tantra_sangraha, label, None)
        vp_func = getattr(vakya_panchanga, label, None)
        ms_func = getattr(makaranda_sarini, label, None)
        vs_func = getattr(vateshwara_sidhantha, label, None)
        snt_func = getattr(sphuta_nirnaya_tantra, label, None)
        drik_func = getattr(drik, label, None)
        try: ss_val = ss_func(pdate, place)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = kk_func(pdate, place)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = gl_func(pdate, place)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = ts_func(pdate, place)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vp_func(pdate, place)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = ms_func(pdate, place)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vs_func(pdate, place)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = snt_func(pdate, place)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik_func(pdate, place)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"{label:42s} SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"{label:42s} SNT={snt_val}")
    for method_name in ("BASED_ON_LOCAL_10AM", "BASED_ON_SUNSET_TIME", "BASED_ON_BIRTH_TIME"):
        method = getattr(const.TAMIL_MONTH_METHOD, method_name, None)
        if method is None:
            print(f"tamil_solar_month_and_date({method_name}) SKIPPED: const.TAMIL_MONTH_METHOD.{method_name} not found")
            continue
        try: ss_val = surya_sidhantha.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: ss_val = f"ERROR: {e}"
        try: kk_val = khanda_khaadyaka.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: kk_val = f"ERROR: {e}"
        try: gl_val = graha_laaghavam.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: gl_val = f"ERROR: {e}"
        try: ts_val = tantra_sangraha.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: ts_val = f"ERROR: {e}"
        try: vp_val = vakya_panchanga.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: vp_val = f"ERROR: {e}"
        try: ms_val = makaranda_sarini.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: ms_val = f"ERROR: {e}"
        try: vs_val = vateshwara_sidhantha.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: vs_val = f"ERROR: {e}"
        try: snt_val = sphuta_nirnaya_tantra.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: snt_val = f"ERROR: {e}"
        try: drik_val = drik.tamil_solar_month_and_date(pdate, place, tamil_month_method=method)
        except Exception as e: drik_val = f"ERROR: {e}"
        print(f"tamil_solar_month_and_date({method_name}) SS={ss_val}   KK={kk_val}   GL={gl_val}   TS={ts_val}   VP={vp_val}   MS={ms_val}   VS={vs_val}   drik={drik_val}")
        print(f"tamil_solar_month_and_date({method_name}) SNT={snt_val}")
def test_batch14(jd, place, scope='LOCAL', run_book_tests=True):
    """
    @param jd: Julian Day Number (local civil time)
    @param place: Place struct
    @param scope: 'LOCAL' (an eclipse is returned only if the Sun / the Moon is above the horizon at one or more of its contacts) or
        'GLOBAL' (the next eclipse, whether or not it is seen at the place: every model returns the same eclipse, so the models can be
        compared event for event)
    @param run_book_tests: False to skip the book-example tests at the end (they do not depend on the scope)
    Compares SS (eclipse_ss.py), KK (eclipse_kk.py), GL (eclipse_gl.py),
    TS (eclipse_ts.py), VP (eclipse_vp.py), MS (eclipse_ms.py), VS (eclipse_vs.py)
    and drik (eclipse.py) for next/previous solar and lunar eclipses. VS returns
    [begin, apparent conjunction, end] with genuine contact times for a solar
    eclipse, and 3 (partial) or 5 (total) elements for a lunar eclipse, like GL.  VP returns the same shapes as
    SS/KK/TS: solar (type_str, [begin, max, end]) with real first/last
    contacts; lunar (type_str, [first contact, middle, last contact]), 3
    elements also for a total eclipse.
    WHAT IS DIRECTLY COMPARABLE (SS vs KK vs GL vs TS vs drik):
      - Solar eclipses, LOCAL mode: all five engines return the same
        3-element shape (type_str, [begin, max, end]) as (y,m,d,fh)
        tuples, so these are compared element-by-element.
      - Lunar eclipses: drik always returns 5 elements
        [penumbral_begin, partial_begin, max, partial_end, penumbral_end]
        (fixed in eclipse.py regardless of LOCAL/GLOBAL); SS/KK/GL each
        return either 3 elements [partial_begin, max, partial_end] for a
        partial eclipse, or 5 elements [begin, totality_begin, max,
        totality_end, end] for a total eclipse (no penumbral phase in any
        of the three classical models). TS ALWAYS returns exactly 3
        elements regardless of total/partial/annular (it does not
        separately report a totality phase -- see eclipse_ts.py
        docstring). Only "max" (drik index 2, SS/KK/GL/TS middle index)
        and type_str are safely comparable across all five; begin/end
        are shown separately since element counts can differ.
      - type_str: drik can return "any"/"total"/"annular"/"hybrid"/"partial"
        (solar) or "any"/"total"/"partial"/"penumbral" (lunar); SS/KK/GL
        can only return "total"/"partial"; TS can additionally return
        "annular" for solar eclipses. Comparisons use SolarEclipseType.ANY
        / LunarEclipseType.ANY on all sides for a fair, unfiltered search.
    WHAT IS NOT COMPARABLE (see chat explanation, not tested here):
      - GLOBAL solar eclipse search (none of SS/KK/GL/TS have an eclipse-
        path/ground-track model; solar eclipses are only visible from a
        limited path, unlike lunar which are visible hemisphere-wide).
      - show_maximum_eclipse_global_location (SS/KK/GL/TS have no lat/long
        output).
      - ANNULAR / HYBRID / PENUMBRAL specific-type searches (TS supports
        an ANNULAR filter internally but it is not separately exercised
        here).
    """
    from jhora.panchanga import eclipse, eclipse_ss, eclipse_kk, eclipse_gl, eclipse_ts, eclipse_vp, eclipse_ms, eclipse_vs
    eclipse, eclipse_ss = _Engine(eclipse, DRIK), _Engine(eclipse_ss, SS)
    eclipse_kk, eclipse_gl = _Engine(eclipse_kk, KK), _Engine(eclipse_gl, GL)
    eclipse_ts, eclipse_vp = _Engine(eclipse_ts, TS), _Engine(eclipse_vp, VP)
    eclipse_ms = _Engine(eclipse_ms, MS)
    eclipse_vs = _Engine(eclipse_vs, VS)
    eclipse_snt = _Engine(eclipse_ts._m, SNT)   # the Sphutanirnaya has no eclipse chapter: eclipse_ts.py is used
    print("=" * 70)
    print(f"BATCH 14: ECLIPSES ({scope}) -- SS vs KK vs GL vs TS vs VP vs MS vs VS vs drik")
    print("=" * 70)
    def _fmt(entry):
        if entry is None:
            return "None"
        y, m, d, fh = entry
        return f"{y:04d}-{m:02d}-{d:02d} {utils.to_dms(fh, as_string=True)}"
    for direction_label, search_backward in (("NEXT", False), ("PREVIOUS", True)):
        print(f"\n--- {direction_label} SOLAR ECLIPSE (LOCAL) ---")
        try:
            drik_val = eclipse.next_solar_eclipse(
                jd, place, getattr(eclipse.EclipseLocation, scope), eclipse.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        try:
            ss_val = eclipse_ss.next_solar_eclipse(
                jd, place, getattr(eclipse_ss.EclipseLocation, scope), eclipse_ss.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = eclipse_kk.next_solar_eclipse(
                jd, place, getattr(eclipse_kk.EclipseLocation, scope), eclipse_kk.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = eclipse_gl.next_solar_eclipse(
                jd, place, getattr(eclipse_gl.EclipseLocation, scope), eclipse_gl.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = eclipse_ts.next_solar_eclipse(
                jd, place, getattr(eclipse_ts.EclipseLocation, scope), eclipse_ts.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = eclipse_vp.next_solar_eclipse(
                jd, place, getattr(eclipse_vp.EclipseLocation, scope), eclipse_vp.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = eclipse_ms.next_solar_eclipse(
                jd, place, getattr(eclipse_ms.EclipseLocation, scope), eclipse_ms.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = eclipse_vs.next_solar_eclipse(
                jd, place, getattr(eclipse_vs.EclipseLocation, scope), eclipse_vs.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = eclipse_snt.next_solar_eclipse(
                jd, place, getattr(eclipse_snt.EclipseLocation, scope), eclipse_snt.SolarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        if isinstance(drik_val, tuple) and isinstance(ss_val, tuple):
            d_type, d_times = drik_val
            s_type, s_times = ss_val
            print(f"{'type':10s} drik={d_type:10s} SS={s_type}")
            for label, dt, st in zip(("begin", "max  ", "end  "), d_times, s_times):
                print(f"{label:10s} drik={_fmt(dt):28s} SS={_fmt(st)}")
        else:
            print(f"drik={drik_val}")
            print(f"SS  ={ss_val}")
        if isinstance(kk_val, tuple):
            k_type, k_times = kk_val
            print(f"{'type':10s} KK={k_type}")
            for label, kt in zip(("begin", "max  ", "end  "), k_times):
                print(f"{label:10s} KK={_fmt(kt)}")
        else:
            print(f"KK  ={kk_val}")
        if isinstance(gl_val, tuple):
            g_type, g_times = gl_val
            print(f"{'type':10s} GL={g_type}")
            for label, gt in zip(("begin", "max  ", "end  "), g_times):
                print(f"{label:10s} GL={_fmt(gt)}")
        else:
            print(f"GL  ={gl_val}")
        if isinstance(ts_val, tuple):
            t_type, t_times = ts_val
            print(f"{'type':10s} TS={t_type}")
            for label, tt in zip(("begin", "max  ", "end  "), t_times):
                print(f"{label:10s} TS={_fmt(tt)}")
        else:
            print(f"TS  ={ts_val}")
        if isinstance(vp_val, tuple):
            v_type, v_times = vp_val
            print(f"{'type':10s} VP={v_type}")
            for label, vt in zip(("begin", "max  ", "end  "), v_times):
                print(f"{label:10s} VP={_fmt(vt)}")
        else:
            print(f"VP  ={vp_val}")
        if isinstance(ms_val, tuple):
            m_type, m_times = ms_val
            print(f"{'type':10s} MS={m_type}")
            for label, mt in zip(("begin", "max  ", "end  "), m_times):
                print(f"{label:10s} MS={_fmt(mt)}")
        else:
            print(f"MS  ={ms_val}")
        if isinstance(vs_val, tuple):
            vs_type, vs_times = vs_val
            print(f"{'type':10s} VS={vs_type}")
            for label, vt in zip(("begin", "max  ", "end  "), vs_times):
                print(f"{label:10s} VS={_fmt(vt)}")
        else:
            print(f"VS  ={vs_val}")
        if isinstance(snt_val, tuple):
            snt_type, snt_times = snt_val
            print(f"{'type':10s} SNT={snt_type}")
            for label, vt in zip(("begin", "max  ", "end  "), snt_times):
                print(f"{label:10s} SNT={_fmt(vt)}")
        else:
            print(f"SNT ={snt_val}")
        print(f"\n--- {direction_label} LUNAR ECLIPSE ---")
        try:
            drik_val = eclipse.next_lunar_eclipse(
                jd, place, getattr(eclipse.EclipseLocation, scope), eclipse.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        try:
            ss_val = eclipse_ss.next_lunar_eclipse(
                jd, place, getattr(eclipse_ss.EclipseLocation, scope), eclipse_ss.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            kk_val = eclipse_kk.next_lunar_eclipse(
                jd, place, getattr(eclipse_kk.EclipseLocation, scope), eclipse_kk.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            kk_val = f"ERROR: {e}"
        try:
            gl_val = eclipse_gl.next_lunar_eclipse(
                jd, place, getattr(eclipse_gl.EclipseLocation, scope), eclipse_gl.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            gl_val = f"ERROR: {e}"
        try:
            ts_val = eclipse_ts.next_lunar_eclipse(
                jd, place, getattr(eclipse_ts.EclipseLocation, scope), eclipse_ts.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            ts_val = f"ERROR: {e}"
        try:
            vp_val = eclipse_vp.next_lunar_eclipse(
                jd, place, getattr(eclipse_vp.EclipseLocation, scope), eclipse_vp.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            vp_val = f"ERROR: {e}"
        try:
            ms_val = eclipse_ms.next_lunar_eclipse(
                jd, place, getattr(eclipse_ms.EclipseLocation, scope), eclipse_ms.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            ms_val = f"ERROR: {e}"
        try:
            vs_val = eclipse_vs.next_lunar_eclipse(
                jd, place, getattr(eclipse_vs.EclipseLocation, scope), eclipse_vs.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            vs_val = f"ERROR: {e}"
        try:
            snt_val = eclipse_snt.next_lunar_eclipse(
                jd, place, getattr(eclipse_snt.EclipseLocation, scope), eclipse_snt.LunarEclipseType.ANY,
                search_backward=search_backward)
        except Exception as e:
            snt_val = f"ERROR: {e}"
        if isinstance(drik_val, tuple) and isinstance(ss_val, tuple):
            d_type, d_times = drik_val   # 5 elements: penumbral_b, partial_b, max, partial_e, penumbral_e
            s_type, s_times = ss_val     # 3 elements: partial_b, max, partial_e
            print(f"{'type':10s} drik={d_type:10s} SS={s_type}")
            print(f"{'max':10s} drik={_fmt(d_times[2]):28s} SS={_fmt(s_times[1])}")
            print(f"{'partial_b':10s} drik={_fmt(d_times[1]):28s} SS={_fmt(s_times[0])}")
            print(f"{'partial_e':10s} drik={_fmt(d_times[3]):28s} SS={_fmt(s_times[2])}")
            print(f"{'penumbra_b':10s} drik={_fmt(d_times[0]):28s} SS=N/A (no penumbral phase in SS)")
            print(f"{'penumbra_e':10s} drik={_fmt(d_times[4]):28s} SS=N/A (no penumbral phase in SS)")
        else:
            print(f"drik={drik_val}")
            print(f"SS  ={ss_val}")
        for label_prefix, val in (("KK", kk_val), ("GL", gl_val), ("TS", ts_val), ("VP", vp_val), ("MS", ms_val), ("VS", vs_val)):
            # NOTE: VP (eclipse_vp.py) and MS (eclipse_ms.py) also always return 3 elements,
            # like TS below. TS (eclipse_ts.py) always returns exactly 3 elements
            # [partial_b, max, partial_e] -- it does not separately report
            # a totality phase the way GL's 5-element return does -- so it
            # falls through to the "else" (3-element) branch below.
            if isinstance(val, tuple):
                e_type, e_times = val
                print(f"{'type':10s} {label_prefix}={e_type}")
                if len(e_times) == 5:
                    labels5 = ("begin", "totality_b", "max", "totality_e", "end")
                    for label, t in zip(labels5, e_times):
                        print(f"{label:10s} {label_prefix}={_fmt(t)}")
                else:
                    print(f"{'partial_b':10s} {label_prefix}={_fmt(e_times[0])}")
                    print(f"{'max':10s} {label_prefix}={_fmt(e_times[1])}")
                    print(f"{'partial_e':10s} {label_prefix}={_fmt(e_times[2])}")
            else:
                print(f"{label_prefix}  ={val}")
        for label_prefix, val in (("SNT", snt_val),):
            # NOTE: VP (eclipse_vp.py) and MS (eclipse_ms.py) also always return 3 elements,
            # like TS below. TS (eclipse_ts.py) always returns exactly 3 elements
            # [partial_b, max, partial_e] -- it does not separately report
            # a totality phase the way GL's 5-element return does -- so it
            # falls through to the "else" (3-element) branch below.
            if isinstance(val, tuple):
                e_type, e_times = val
                print(f"{'type':10s} {label_prefix}={e_type}")
                if len(e_times) == 5:
                    labels5 = ("begin", "totality_b", "max", "totality_e", "end")
                    for label, t in zip(labels5, e_times):
                        print(f"{label:10s} {label_prefix}={_fmt(t)}")
                else:
                    print(f"{'partial_b':10s} {label_prefix}={_fmt(e_times[0])}")
                    print(f"{'max':10s} {label_prefix}={_fmt(e_times[1])}")
                    print(f"{'partial_e':10s} {label_prefix}={_fmt(e_times[2])}")
            else:
                print(f"{label_prefix}  ={val}")
    if not run_book_tests:
        return
    # VP book examples, run once (they are not part of the side-by-side columns):
    run_vakya_book_tests()   # test_book_vakya.py: Chapters I-III (Kali days, Sun, Moon, Rahu, planets, Lagna)
    run_eclipse_vp_tests()   # test_book_eclipse_vp.py: Chapter IV (Ex. 32-38 via eclipse_vp.py) + date-level checks
    # MS book examples, run once (they are not part of the side-by-side columns):
    run_mks_book_tests()      # test_book_mks.py: Makaranda Sarini's own worked example, pp. 0072-0081
    run_eclipse_ms_tests()    # test_book_eclipse_ms.py: eclipse_ms.py's book-example self-test, pp. 0083-0084
    # VS book numbers, run once:
    run_eclipse_vs_tests()    # test_book_eclipse_vs.py: the numbers printed in Chapters IV and V of the Vateswara book
def test_batch14_both(jd, place):
    """ Runs Batch 14 twice: first with GLOBAL (the next eclipse, whether or not it is seen at the place: every model returns the same
        eclipse, so the models are compared event for event), then with LOCAL (an eclipse is returned only if the Sun / the Moon is above
        the horizon at one or more of its contacts).
        @param jd: Julian Day Number (local civil time)
        @param place: Place struct """
    for scope in ('GLOBAL', 'LOCAL'):
        print("#" * 70)
        print(f"# BATCH 14 with eclipse_location_type = EclipseLocation.{scope}")
        print("#" * 70)
        test_batch14(jd, place, scope=scope, run_book_tests=(scope == 'LOCAL'))
def test_rao_book_table_12_7():
    """ Rao, Ancient Indian Astronomy, Table 12.7 (astagraha yoga, 4/5 Feb 1962, Bangalore).
        Book's SS/KK/GL columns = Bangalore LOCAL MEAN midnight (00:19:37 IST).
        Book's 'Modern' column  = 00:00 IST.
    """
    import importlib
    try:
        from jhora import utils, const
    except ImportError:
        raise SystemExit("run inside your PyJHora environment")

    def _imp(name):
        for path in (f"jhora.panchanga.{name}", name):
            try:
                return importlib.import_module(path)
            except ImportError:
                pass
        raise ImportError(name)

    ENGINES = ('surya_sidhantha', 'khanda_khaadyaka', 'graha_laaghavam', 'drik')
    LABELS  = ('SS', 'KK', 'GL', 'DRIK')
    BOOK = {  # Table 12.7: (SS, KK, GL, Modern) degrees, minutes
     'Sun':    ((292, 8), (292, 6), (292, 6), (292, 9)),
     'Moon':   ((286,52), (288,31), (288,57), (288,53)),
     'Mars':   ((277, 7), (277,21), (279,22), (278,52)),
     'Mercury':((291,49), (302,57), (293,15), (293,52)),
     'Jupiter':((299, 9), (299,46), (296,20), (295,14)),
     'Venus':  ((297,30), (299,50), (294,46), (294,10)),
     'Saturn': ((274, 9), (272,14), (278, 0), (280,27)),
     'Ketu':   ((298,38), (294,20), (294,50), (294,37))}
    PLANET = {'Sun':const._SUN,'Moon':const._MOON,'Mars':const._MARS,'Mercury':const._MERCURY,
              'Jupiter':const._JUPITER,'Venus':const._VENUS,'Saturn':const._SATURN,'Ketu':const._KETU}

    def dms(x):
        x %= 360; d = int(x); m = (x - d) * 60
        return f"{d:3d}°{int(m):02d}'{min(59, round((m % 1) * 60)):02d}\""

    LAT, LON, TZ = 12.972, 77.594, 5.5

    # Two instants, both expressed as local CLOCK time (PyJHora convention), then -> UT
    jd_ist_midnight = utils.julian_day_number((1962, 2, 5), (0, 0, 0))   # 00:00 IST
    lmt_offset      = (LON - 15.0 * TZ) / 360.0                          # -19.6 min (days)
    jd_lmt_midnight = jd_ist_midnight - lmt_offset                       # 00:19:37 IST

    jd_utc_classical = jd_lmt_midnight - TZ / 24.0   # SS / KK / GL
    jd_utc_drik      = jd_ist_midnight - TZ / 24.0   # DRIK vs 'Modern'

    mods = [_imp(e) for e in ENGINES]
    drik = mods[-1]
    if hasattr(drik, 'set_ayanamsa_mode'):
        drik.set_ayanamsa_mode('LAHIRI')

    def drik_long(planet):
        """ Swiss-Ephemeris / Lahiri, forced to DRIK model. Ketu = Rahu + 180. """
        if planet == const._KETU:
            return (drik_long(const._RAHU) + 180.0) % 360.0
        saved = const.astrology_model_default
        const.astrology_model_default = const.ASTROLOGY_MODELS.DRIK
        try:
            return drik.sidereal_longitude(jd_utc_drik, planet)   # drik: UT, no place
        finally:
            const.astrology_model_default = saved

    print("Bangalore 4/5 Feb 1962: SS/KK/GL at local mean midnight (00:19:37 IST), "
          "DRIK at 00:00 IST  (Δ = engine − book; DRIK vs book 'Modern')")
    print(f"{'Body':8}" + "".join(f"{e:>26}" for e in LABELS))
    tot = [0.0] * len(ENGINES)
    for name, p in PLANET.items():
        row = f"{name:8}"
        for i, m in enumerate(mods):
            if m is drik:
                lon = drik_long(p)
            else:
                place = m.Place('Bangalore', LAT, LON, TZ)
                lon = m.sidereal_longitude(jd_utc_classical, p, place)
            b = BOOK[name][i]
            d = ((lon - (b[0] + b[1] / 60) + 180) % 360 - 180) * 60
            tot[i] += abs(d)
            row += f"{dms(lon):>15}{d:+9.0f}'  "
        print(row)
    print(f"{'sum|Δ|':8}" + "".join(f"{t:24.0f}'  " for t in tot))
    
def run_all_tests():
    # Global model / ayanamsa / node settings are now applied per call by
    # _Engine (see top of file) -- exactly as test.py's _configure() does
    # per pass. Do NOT set const.astrology_model_default here.
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0)
    place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    main(jd,dob,tob,place)
    test_batch5(jd,place,dob,tob)
    test_batch6(dob,place)
    test_sankranti_consistency(place)
    test_batch7(jd, place)
    test_batch8(jd, place)
    test_batch9(jd, place)
    test_batch10(jd, place)
    test_batch11(jd, place)
    test_batch12(jd, place, dob, tob)
    test_batch13(jd, place)
    test_batch14_both(jd, place)
def partial_tests():
    utils.set_language('en')
    dob = drik.Date(1996,12,7); tob = (10,34,0)
    place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    test_batch14_both(jd, place)
if __name__ == "__main__":
    #partial_tests()
    run_all_tests()
