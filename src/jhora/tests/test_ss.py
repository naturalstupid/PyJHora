from jhora import utils, const
from jhora.panchanga import surya_sidhantha
from jhora.panchanga import eclipse_ss


def diagnose_previous_lunar_eclipse(jd_local, place, max_tries=30, model=None):
    if model is None:
        model = const.astrology_model_default
    jd = jd_local
    print(f"{'iter':>4s} {'jd_full':>14s} {'date':>20s} {'grasa':>8s} "
          f"{'is_poss':>8s} {'is_total':>9s} {'moon_up':>8s} {'ACCEPTED?':>10s}")
    for i in range(max_tries):
        ti = surya_sidhantha.tithi(jd, place, model=model)[0]
        jd_full = surya_sidhantha.full_moon(jd, place, ti, opt=-1, model=model)
        info = surya_sidhantha.is_lunar_eclipse(jd_full, place, model=model)
        y, m, d, fh = utils.jd_to_gregorian(jd_full)
        date_str = f"{y:04d}-{m:02d}-{d:02d} {fh:5.2f}h"
        moon_up = eclipse_ss._is_moon_up(jd_full, place, model=model) if hasattr(eclipse_ss, '_is_moon_up') else "N/A(no fix applied)"
        accepted = info['is_possible'] and (moon_up is True)
        print(f"{i:4d} {jd_full:14.4f} {date_str:>20s} {info['grasa']:8.4f} "
              f"{str(info['is_possible']):>8s} {str(info['is_total']):>9s} "
              f"{str(moon_up):>8s} {str(accepted):>10s}")
        if accepted:
            print(f"--> WOULD STOP HERE (iteration {i})")
            return info
        jd = jd_full - 20.0
    print(f"--> EXHAUSTED {max_tries} tries without an accepted candidate")
    return None


if __name__ == "__main__":
    from jhora.panchanga import drik
    utils.set_language('en')
    const.astrology_model_default = const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.0878, 80.2785, 5.5)
    jd = utils.julian_day_number(dob, tob)

    print("=" * 100)
    print("BACKWARD search trace (previous_lunar_eclipse) -- geometry vs. visibility gating")
    print("=" * 100)
    diagnose_previous_lunar_eclipse(jd, place)
