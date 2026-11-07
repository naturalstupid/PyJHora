import math
from jhora import const, utils
from jhora.panchanga import drik, surya_sidhantha

# ---------------------------------------------------------------------
# Main: Sun..Ketu + Lagna comparison against drik, plus sunrise/sunset/
# moonrise/moonset self-check
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
    t_dr = drik.tithi(jd,place)
    print('tithi SS',t_ss,'\ndrik',t_dr)
    n_ss = surya_sidhantha.nakshatra(jd,place)
    n_dr = drik.nakshatra(jd,place)
    print('nak SS',n_ss,'\ndrik',n_dr)
    n_ss = surya_sidhantha.yogam(jd,place)
    n_dr = drik.yogam(jd,place)
    print('yogam SS',n_ss,'\ndrik',n_dr)
    n_ss = surya_sidhantha.karana(jd,place)
    n_dr = drik.karana(jd,place)
    print('karana SS',n_ss,'\ndrik',n_dr)
    pp = surya_sidhantha.dhasavarga(jd,place)
    for p,(h,long) in pp:
        print(p,utils.RAASI_LIST[h],utils.to_dms(long,is_lat_long='plong'))
    for bm in surya_sidhantha.SUPPORTED_BHAVA_METHODS:
        print("Bhava Method",bm,surya_sidhantha.bhaava_madhya(jd,place,bhava_method=bm))
    #exit()
    planet = const._SATURN
    ncp = surya_sidhantha.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('SS next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    ncp = drik.next_planet_retrograde_change_date(planet,dob,place)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('drik next planet retro',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    #exit()
    sr = surya_sidhantha.sunrise(jd,place)
    y,m,d,fh = utils.jd_to_gregorian(sr)
    print(y,m,d,utils.to_dms(fh),'drik',drik.sunrise(jd,place)[1])
    ncp = surya_sidhantha.next_conjunction_of_planet_pair(jd,place,const._SUN,'L',separation_angle=180)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print(y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    sr = surya_sidhantha.sunset(jd,place)
    y,m,d,fh = utils.jd_to_gregorian(sr)
    print(y,m,d,utils.to_dms(fh),'drik',drik.sunset(jd,place)[1])
    ncp = surya_sidhantha.next_conjunction_of_planet_pair(jd,place,const._SUN,'L')
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('Moon/Lagna/0',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    sr = surya_sidhantha.moonrise(jd,place)
    y,m,d,fh = utils.jd_to_gregorian(sr)
    print('moonrise',y,m,d,utils.to_dms(fh),'drik',drik.moonrise(jd,place)[1])
    ncp = surya_sidhantha.next_conjunction_of_planet_pair(jd,place,const._MOON,'L',separation_angle=180)
    y,m,d,fh = utils.jd_to_gregorian(ncp[0])
    print('Moon/Lagna/180',y,m,d,utils.to_dms(fh),utils.deg_to_sign_str(ncp[1]))
    sr = surya_sidhantha.moonset(jd,place)
    y,m,d,fh = utils.jd_to_gregorian(sr)
    print('moonset',y,m,d,utils.to_dms(fh),'drik',drik.moonset(jd,place)[1])
    #exit()
    test_cases = [
        ("Chicago, 10-Jan-2016 00:00", drik.Place('Chicago', 41.8781, -87.6298, -6.0),
         drik.Date(2016, 1, 10), (0, 0, 0)),
        ("Bangalore, 14-Nov-2013 06:00", drik.Place('Bangalore', 12.9716, 77.5946, 5.5),
         drik.Date(2013, 11, 14), (6, 0, 0)),
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
    # --- Planetary longitude + Lagna: DRIK vs SURYA_SIDDHANTHA, side by side ---
    for label, place, dob, tob in test_cases:
        jd = utils.julian_day_number(dob, tob)
        jd_utc = jd - place.timezone / 24.0
        print("=" * 100)
        print(label)
        print("=" * 100)
        header = f"{'Body':9s}{'DRIK':>22s}{'SURYA_SIDDHANTHA':>22s}"
        print(header)
        print("-" * len(header))
        for body_name, body in bodies:
            if body == 'L':
                asc = drik.ascendant(jd, place)
                drik_val = asc[0] * 30 + asc[1]
                ss_asc = surya_sidhantha.ascendant(jd, place)
                ss_val = ss_asc[0] * 30 + ss_asc[1]      # FIXED: unpack the same way as drik_val
            else:
                drik_val = drik.sidereal_longitude(jd_utc, body)
                ss_val = surya_sidhantha.sidereal_longitude(jd, body, place)
            row = f"{body_name:9s}{_fmt_dms(drik_val):>22s}{_fmt_dms(ss_val):>22s}"
            print(row)
        print()
    # --- Sunrise / Sunset / Moonrise / Moonset: DRIK (swisseph) vs SURYA_SIDDHANTHA, side by side ---
    for label, place, dob, tob in test_cases:
        jd = utils.julian_day_number(dob, tob)
        jd_utc = jd - place.timezone / 24.0
        print("-" * 100)
        print(label + "  (sunrise/sunset/moonrise/moonset)")
        print("-" * 100)
        sr_ss = surya_sidhantha.sunrise(jd, place)
        se_ss = surya_sidhantha.sunset(jd, place)
        mr_ss = surya_sidhantha.moonrise(jd, place)
        ms_ss = surya_sidhantha.moonset(jd, place)
        if surya_sidhantha._HAVE_SWE:
            jd_midnight_ut = math.floor(jd_utc - 0.5) + 0.5
            geopos = (place.longitude, place.latitude, 0.0)
            sr_drik = drik.sunrise(jd,place)[2]
            se_drik = drik.sunset(jd,place)[2]
            mr_drik = drik.moonrise(jd,place)[2]
            ms_drik = drik.moonset(jd,place)[2]
        else:
            sr_drik = se_drik = mr_drik
        print(f"Sunrise: SS/Drik {_fmt_time(sr_ss)} {_fmt_time(sr_drik)}")
        print(f"Sunset: SS/Drik {_fmt_time(se_ss)} {_fmt_time(se_drik)}")
        print(f"Moonrise: SS/Drik {_fmt_time(mr_ss)} {_fmt_time(mr_drik)}")
        print(f"Moonset: SS/Drik {_fmt_time(ms_ss)} {_fmt_time(ms_drik)}")
        
def test_batch5(jd, place, dob, tob):
    import sys
    print("="*80)
    print("SOLAR UPAGRAHAS")
    print("="*80)
    sun_long_ss = surya_sidhantha.sidereal_longitude(jd, const._SUN, place)
    jd_utc = jd - place.timezone/24.0
    sun_long_drik = drik.sidereal_longitude(jd_utc, const._SUN)
    for name in const.sub_planet_list_2:
        try:
            ss_val = surya_sidhantha.solar_upagraha_longitudes(sun_long_ss, upagraha=name)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            drik_val = drik.solar_upagraha_longitudes(sun_long_drik, upagraha=name)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        label = utils.resource_strings.get(name + "_str", name)
        print(f"{label:20s} SS={ss_val}   drik={drik_val}")

    print()
    print("="*80)
    print("OTHER (TIME-BASED) UPAGRAHAS")
    print("="*80)
    for label_key, func_name in const.sub_planet_dict_1.items():
        ss_func = getattr(surya_sidhantha, func_name, None)
        drik_func = getattr(drik, func_name, None)
        label = utils.resource_strings.get(label_key, label_key)
        if ss_func is None or drik_func is None:
            print(f"{label:20s} MISSING: ss_func={ss_func is not None} drik_func={drik_func is not None} (expected name: {func_name})")
            continue
        try:
            ss_val = ss_func(dob, tob, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(dob, tob, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}   drik={drik_val}")

    print()
    print("="*80)
    print("SPECIAL LAGNAS")
    print("="*80)
    for name in const._special_lagna_list:
        lookup_name = name if name != 'bhrigu_bindhu' else 'bhrigu_bindhu_lagna'
        ss_func = getattr(surya_sidhantha, lookup_name, None)
        drik_func = getattr(drik, lookup_name, None)
        label = utils.resource_strings.get(name + "_str", name)
        if name in ('varnada_lagna',):
            print(f"{label:20s} SKIPPED (lives in charts.py, different signature -- test separately)")
            continue
        if ss_func is None or drik_func is None:
            print(f"{label:20s} MISSING: ss_func={ss_func is not None} drik_func={drik_func is not None} (expected name: {lookup_name})")
            continue
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}   drik={drik_val}")

def test_batch6(panchanga_date, place):
    print("=" * 70)
    print("BATCH 6: SANKRANTI / SOLAR-CALENDAR -- SS vs drik")
    print("=" * 70)
    for label in ("previous_sankranti_date", "next_sankranti_date",
                  "tamil_solar_month_and_date", "days_in_tamil_month"):
        ss_func = getattr(surya_sidhantha, label, None)
        #ss_func = globals()[label]
        drik_func = getattr(drik, label)
        try:
            ss_val = ss_func(panchanga_date, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(panchanga_date, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:28s} SS={ss_val}   drik={drik_val}")
    jd = utils.gregorian_to_jd(panchanga_date)
    try:
        ss_val = surya_sidhantha.solar_month_date(jd, place)
    except Exception as e:
        ss_val = f"ERROR: {e}"
    try:
        drik_val = drik.solar_month_date(jd, place)
    except Exception as e:
        drik_val = f"ERROR: {e}"
    print(f"{'solar_month_date':28s} SS={ss_val}   drik={drik_val}")

def test_batch7(jd, place):
    print("=" * 70)
    print("BATCH 7: WEEKDAY + KAALA-VIBHAGA -- SS vs drik")
    print("=" * 70)
    simple_funcs = ("vaara", "trikalam", "raahu_kaalam", "yamaganda_kaalam", "gulikai_kaalam",
                    "durmuhurtam", "abhijit_muhurta", "gauri_choghadiya", "amrit_kaalam",
                    "shubha_hora", "brahma_muhurtha", "godhuli_muhurtha", "sandhya_periods",
                    "vijaya_muhurtha", "nishita_kaala", "nishita_muhurtha", "tamil_jaamam",
                    "muhurthas")
    for label in simple_funcs:
        ss_func = getattr(surya_sidhantha, label, None)
        drik_func = getattr(drik, label)
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:20s} SS={ss_val}\n{'':20s} drik={drik_val}")
    print(f"{'civil_weekday':20s} SS={surya_sidhantha.civil_weekday(jd)}   drik={drik.civil_weekday(jd)}")

def test_batch8(jd, place):
    print("=" * 70)
    print("BATCH 8: PANCHAKA / CHANDRABALAM / THAARAABALAM -- SS vs drik")
    print("=" * 70)
    for label in ("udhaya_lagna_muhurtha", "thaaraabalam", "chandrabalam",
                  "panchaka_rahitha", "next_panchaka_days", "chandrashtama"):
        ss_func = getattr(surya_sidhantha, label, None)
        drik_func = getattr(drik, label)
        try:
            ss_val = ss_func(jd, place)
        except Exception as e:
            ss_val = f"ERROR: {e}"
        try:
            drik_val = drik_func(jd, place)
        except Exception as e:
            drik_val = f"ERROR: {e}"
        print(f"{label:24s} SS={ss_val}\n{'':24s} drik={drik_val}")

def test_batch9(jd, place):
    print("=" * 70)
    print("BATCH 9: LUNAR CALENDAR CORE -- SS vs drik")
    print("=" * 70)
    ti_ss = surya_sidhantha.tithi(jd, place)[0]
    ti_drik = drik.tithi(jd, place)[0]
    for label, ss_call, drik_call in (
        ("new_moon", lambda: surya_sidhantha.new_moon(jd, place, ti_ss, -1), lambda: drik.new_moon(jd, ti_drik, -1)),
        ("full_moon", lambda: surya_sidhantha.full_moon(jd, place, ti_ss, -1), lambda: drik.full_moon(jd, ti_drik, -1)),
        ("lunar_month", lambda: surya_sidhantha.lunar_month(jd, place), lambda: drik.lunar_month(jd, place)),
        ("lunar_month_date", lambda: surya_sidhantha.lunar_month_date(jd, place), lambda: drik.lunar_month_date(jd, place)),
        ("next_lunar_month", lambda: surya_sidhantha.next_lunar_month(jd, place), lambda: drik.next_lunar_month(jd, place)),
        ("previous_lunar_month", lambda: surya_sidhantha.previous_lunar_month(jd, place), lambda: drik.previous_lunar_month(jd, place)),
        ("next_lunar_year", lambda: surya_sidhantha.next_lunar_year(jd, place), lambda: drik.next_lunar_year(jd, place)),
        ("previous_lunar_year", lambda: surya_sidhantha.previous_lunar_year(jd, place), lambda: drik.previous_lunar_year(jd, place)),
    ):
        try:
            ss_v = ss_call()
        except Exception as e:
            ss_v = f"ERROR: {e}"
        try:
            drik_v = drik_call()
        except Exception as e:
            drik_v = f"ERROR: {e}"
        print(f"{label:22s} SS={ss_v}\n{'':22s} drik={drik_v}")

    py, pm, pd, _ = utils.jd_to_gregorian(jd)
    pdate = drik.Date(py, pm, pd)
    try:
        ss_v = surya_sidhantha.samvatsara(pdate, place)
    except Exception as e:
        ss_v = f"ERROR: {e}"
    try:
        drik_v = drik.samvatsara(pdate, place)
    except Exception as e:
        drik_v = f"ERROR: {e}"
    print(f"{'samvatsara':22s} SS={ss_v}   drik={drik_v}")

    for maasa in (1, 6):
        print(f"{'ritu(' + str(maasa) + ')':22s} SS={surya_sidhantha.ritu(maasa)}   drik={drik.ritu(maasa)}")

    try:
        ss_v = surya_sidhantha.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        ss_v = f"ERROR: {e}"
    try:
        drik_v = drik.vedic_date(jd, place, calendar_type=const.CALENDAR_TYPE.SOLAR)
    except Exception as e:
        drik_v = f"ERROR: {e}"
    print(f"{'vedic_date(SOLAR)':22s} SS={ss_v}   drik={drik_v}")

if __name__ == "__main__":
    utils.set_language('en')
    const.astrology_model_default = const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA
    drik.set_ayanamsa_mode('LAHIRI')
    drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)
    dob = drik.Date(1996,12,7); tob = (10,34,0)
    place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    main(jd,dob,tob,place)
    test_batch5(jd,place,dob,tob)
    test_batch6(dob,place)
    test_batch7(jd, place)
    test_batch8(jd, place)
    test_batch9(jd, place)