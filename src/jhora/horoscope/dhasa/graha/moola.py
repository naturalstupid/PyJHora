#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from jhora import const, utils
from jhora.horoscope.chart import house, charts
from jhora.panchanga import drik

""" Also called Lagna Kendradi Graha Dhasa """

year_duration = const.sidereal_year


def get_dhasa_antardhasa(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6
    round_duration=True,
    *,
    use_lagna_for_seed=True,
    use_sun_for_seed=True,
    use_moon_for_seed=True,
    moolatrikona_correction=12,   # set to 0 to match JHora's "0 years" toggle
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
    Mūla (Lagna‑Kendrādi Graha Daśā) — depth-enabled (Mahā → Antara → … → Deha)

    Returns rows like your other base daśās:
        [lords_tuple, start_tuple, dur_years]

    • MD (planetary) order: Kendra (ranked) → Panapara (ranked) → Apoklima (ranked) from Lagna (D‑1).
    • Seed: among Kendra planets of the selected candidates (Lagna/Moon/Sun), pick the strongest; rotate MD to start from it.
    • MD years (cycle‑1): VimśottarīYears − (cw distance to MT) ± 1 (exalt/debil in D‑1);
        if planet is in its MT sign (D‑1) then subtract `moolatrikona_correction` (0 or 12) instead of distance.
        If result ≤ 0, clamp to 1. Nodes: Rahu→Aquarius, Ketu→Scorpio for MT distance.
      MD years (cycle‑2): Vimśottarī − cycle‑1 (two cycles sum to 120).
    • Antardaśā & deeper: order = global rotation from the parent; durations = proportional to cycle‑1 years (Σ children = parent).
    • Rounding: returned durations rounded to (dhasa_level_index + 1) decimals if round_duration=True; JD math uses full precision.
    """
    global year_duration

    # ---- Safety ---------------------------------------------------------------
    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    # ---- Epoch & charts (D‑1 for Moola) --------------------------------------
    start_jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=start_jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # Ordering varga: per JHora, Moola is D‑1; keep divisional_chart_factor for compatibility
    pp_ord = charts.divisional_chart(
        start_jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
    )[:const._pp_count_upto_ketu]

    p2h_ord = utils.get_planet_house_dictionary_from_planet_positions(pp_ord)

    # D‑1 again for count/rider (JHora behavior)
    pp_d1 = pp_ord
    p2h_d1 = p2h_ord

    asc = p2h_d1["L"]  # Lagna sign index (0..11)

    # ---- Participating grahas (Sun..Saturn + nodes) --------------------------
    GSET = [
        const.SUN_ID,
        const.MOON_ID,
        const.MARS_ID,
        const.MERCURY_ID,
        const.JUPITER_ID,
        const.VENUS_ID,
        const.SATURN_ID,
        const.RAHU_ID,
        const.KETU_ID,
    ]

    # ---- House groups from a reference sign ----------------------------------
    def _kpa_from(ref_sign):
        K = set(house.quadrants_of_the_raasi(ref_sign))
        P = set(house.panapharas_of_the_raasi(ref_sign))
        A = set(house.apoklimas_of_the_raasi(ref_sign))
        return K, P, A

    # ---- Ranking via your strength API ---------------------------------------
    def _rank_grahas_in_houses(p2h_map, houses):
        cands = [g for g in GSET if p2h_map.get(g, -99) in houses]
        ranked = []
        while cands:
            sp = house.stronger_planet_from_list_of_planets(pp_ord, cands)
            ranked.append(sp)
            cands = [c for c in cands if c != sp]
        return ranked

    # ---- Build planetary MD order: K -> P -> A from Lagna --------------------
    K, P, A = _kpa_from(asc)
    Q = (
        _rank_grahas_in_houses(p2h_ord, K)
        + _rank_grahas_in_houses(p2h_ord, P)
        + _rank_grahas_in_houses(p2h_ord, A)
    )

    if not Q:
        Q = _rank_grahas_in_houses(p2h_ord, P) + _rank_grahas_in_houses(p2h_ord, A)
        if not Q:
            return []

    # ---- Choose seed from selected candidates (Lagna/Moon/Sun KENDRAs) -------
    seed_refs = []
    if use_lagna_for_seed:
        seed_refs.append(asc)
    if use_moon_for_seed:
        seed_refs.append(p2h_d1[const.MOON_ID])
    if use_sun_for_seed:
        seed_refs.append(p2h_d1[const.SUN_ID])

    seed_kendra_planets = []
    for ref in seed_refs:
        Kc, _, _ = _kpa_from(ref)
        seed_kendra_planets.extend([g for g in GSET if p2h_d1.get(g, -99) in Kc])

    seed_kendra_planets = list(dict.fromkeys(seed_kendra_planets))

    if seed_kendra_planets:
        seed = house.stronger_planet_from_list_of_planets(pp_ord, seed_kendra_planets)
        if seed in Q:
            j = Q.index(seed)
            Q = Q[j:] + Q[:j]

    # ---- Vimśottarī base years (from const) ----------------------------------
    VIM = const.vimsottari_dict

    # ---- Mūlatrikoṇa signs (override nodes per Rider‑2) -----------------------
    MT_LIST = list(getattr(const, "moola_trikona_of_planets", [4, 1, 0, 5, 8, 6, 10, 5, 11]))
    MT_LIST[const.RAHU_ID] = 10  # Aquarius
    MT_LIST[const.KETU_ID] = 7   # Scorpio

    # ---- Exaltation / Debilitation detection via your matrix ------------------
    EXALT_VAL = const._EXALTED_UCCHAM
    DEBIL_VAL = const._DEBILITATED_NEECHAM
    HS = const.house_strengths_of_planets

    def _is_exalted_d1(g):
        return HS[g][p2h_d1[g]] == EXALT_VAL

    def _is_debilitated_d1(g):
        return HS[g][p2h_d1[g]] == DEBIL_VAL

    # ---- Distance helpers (clockwise) ----------------------------------------
    def _dist_cw(a, b):
        return (b - a) % 12

    # ---- Cycle‑1 years per JHora options -------------------------------------
    def _moola_cycle1_years(g):
        """
        Vim(g) − distance_to_MT  (distance = cw steps; equals sign-count−1)
        If planet is in its own MT sign (D‑1): use Vim(g) − moolatrikona_correction (0 or 12).
        Then rider: +1 exalted / −1 debilitated (in D‑1).
        If result <= 0, clamp to 1.
        """
        vim = float(VIM[g])
        cur = p2h_d1[g]
        mt = MT_LIST[g]

        if cur == mt and moolatrikona_correction in (0, 12):
            yrs = vim - float(moolatrikona_correction)
        else:
            dist = _dist_cw(cur, mt)
            yrs = vim - float(dist)

        if _is_exalted_d1(g):
            yrs += 1.0
        elif _is_debilitated_d1(g):
            yrs -= 1.0

        if yrs <= 0.0:
            yrs = 1.0

        return yrs

    # Build MD durations: cycle‑1 & cycle‑2 (two cycles = 120)
    md1_map = {g: _moola_cycle1_years(g) for g in Q}
    md1_years = [md1_map[g] for g in Q]
    md2_years = [float(VIM[g]) - md1_map[g] for g in Q]

    md_planets = Q + Q
    md_years = md1_years + md2_years

    # AD/PD queue for any parent: global rotation of Q starting from the parent
    def _child_queue(parent_g):
        if parent_g not in Q:
            return []
        j = Q.index(parent_g)
        return Q[j:] + Q[:j]

    # Weights for proportional split: use cycle‑1 Mūla years
    def _weights_for(queue):
        w = [md1_map[g] for g in queue]
        S = sum(w)
        if S <= 0.0:
            w = [1.0] * len(queue)
        return w

    def _emit(out, labels, start_jd_local, years_value):
        start_tuple = utils.jd_to_gregorian(start_jd_local)
        nd = (dhasa_level_index + 1) if round_duration else None
        dur_out = round(years_value, nd) if round_duration else years_value
        out.append([labels, start_tuple, float(dur_out)])

    # Recursive builder for L3..L6
    def _recurse(level, parent_g, parent_start_jd, parent_years, prefix, out_rows):
        cq = _child_queue(parent_g)
        if not cq:
            return parent_start_jd + parent_years * year_duration

        weights = _weights_for(cq)
        S = float(sum(weights))
        jd_here = parent_start_jd

        for g, wi in zip(cq, weights):
            child_years = parent_years * (wi / S)
            if level < dhasa_level_index:
                jd_here = _recurse(
                    level + 1,
                    g,
                    jd_here,
                    child_years,
                    prefix + (g,),
                    out_rows,
                )
            else:
                _emit(out_rows, prefix + (g,), jd_here, child_years)
                jd_here += child_years * year_duration

        return jd_here

    # ---- Build rows per requested depth --------------------------------------
    rows = []
    jd_cursor = start_jd

    if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
        for y_md, g in zip(md_years, md_planets):
            _emit(rows, (g,), jd_cursor, y_md)
            jd_cursor += y_md * year_duration
        return rows

    if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
        for y_md, md_g in zip(md_years, md_planets):
            cq = _child_queue(md_g)
            weights = _weights_for(cq)
            S = float(sum(weights))
            jd_b = jd_cursor
            for g, wi in zip(cq, weights):
                y_ad = y_md * (wi / S)
                _emit(rows, (md_g, g), jd_b, y_ad)
                jd_b += y_ad * year_duration
            jd_cursor = jd_b
        return rows

    # L3..L6
    for y_md, md_g in zip(md_years, md_planets):
        jd_end = _recurse(
            const.MAHA_DHASA_DEPTH.ANTARA,
            md_g,
            jd_cursor,
            y_md,
            (md_g,),
            rows,
        )
        jd_cursor = jd_end

    return rows


def moola_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    chart_method: int = 1,
    use_lagna_for_seed: bool = True,
    use_sun_for_seed: bool = True,
    use_moon_for_seed: bool = True,
    moolatrikona_correction: int = 12,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Return ONLY the immediate (parent -> children) splits for Mūla Daśā.

    Rows returned:
        [ [lords_tuple_{k+1}, start_tuple, end_tuple], ... ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- normalize parent path
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")

    k = len(path)

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    start_jd = _tuple_to_jd(parent_start)

    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end")

    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    rows = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        chart_method=chart_method,
        dhasa_level_index=k + 1,
        round_duration=False,
        use_lagna_for_seed=use_lagna_for_seed,
        use_sun_for_seed=use_sun_for_seed,
        use_moon_for_seed=use_moon_for_seed,
        moolatrikona_correction=moolatrikona_correction,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    children = []
    for lords_tuple, start_tuple, dur_years in rows:
        if len(lords_tuple) != k + 1:
            continue
        if tuple(lords_tuple[:k]) != path:
            continue

        sjd = _tuple_to_jd(start_tuple)
        ejd = sjd + float(dur_years) * year_duration

        if ejd <= start_jd or sjd >= end_jd:
            continue

        cs = max(sjd, start_jd)
        ce = min(ejd, end_jd)

        if ce > cs:
            children.append([tuple(lords_tuple), _jd_to_tuple(cs), _jd_to_tuple(ce)])

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)

    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = 1,
    years: int = 1,
    months: int = 1,
    sixty_hours: int = 1,
    chart_method: int = 1,
    use_lagna_for_seed: bool = True,
    use_sun_for_seed: bool = True,
    use_moon_for_seed: bool = True,
    moolatrikona_correction: int = 12,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Mūla Daśā — running ladder at current_jd:
      [
        [(g1,),              start1, end1],
        [(g1,g2),            start2, end2],
        ...
      ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))

    target = _norm(dhasa_level_index)

    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _to_periods(children_rows, parent_end_tuple):
        if not children_rows:
            return []
        rows = sorted(children_rows, key=lambda r: _tuple_to_jd(r[1]))
        proj = []
        for lords, st, en in rows:
            if (not proj) or (_tuple_to_jd(st) > _tuple_to_jd(proj[-1][1])):
                proj.append((lords, st))
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    # ---- Step 1: running Mahā via base (depth=1)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)

    maha_rows = get_dhasa_antardhasa(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        chart_method=chart_method,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        use_lagna_for_seed=use_lagna_for_seed,
        use_sun_for_seed=use_sun_for_seed,
        use_moon_for_seed=use_moon_for_seed,
        moolatrikona_correction=moolatrikona_correction,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    periods = []
    jd_cursor = jd_at_dob

    for lords_tuple, start_tuple, dur_years in maha_rows:
        periods.append((tuple(lords_tuple), start_tuple))
        jd_cursor = _tuple_to_jd(start_tuple) + float(dur_years) * year_duration

    periods.append((periods[-1][0], utils.jd_to_gregorian(jd_cursor)))

    rd1 = utils.get_running_dhasa_for_given_date(current_jd, periods)
    running = [tuple(rd1[0]), rd1[1], rd1[2]]
    ladder = [running]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    # ---- Step 2+: deeper levels via immediate_children on the running parent
    for depth in range(2, target + 1):
        parent_lords, parent_start, parent_end = running

        kids = moola_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            divisional_chart_factor=divisional_chart_factor,
            years=years,
            months=months,
            sixty_hours=sixty_hours,
            chart_method=chart_method,
            use_lagna_for_seed=use_lagna_for_seed,
            use_sun_for_seed=use_sun_for_seed,
            use_moon_for_seed=use_moon_for_seed,
            moolatrikona_correction=moolatrikona_correction,
            round_duration=False,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )

        if not kids:
            ladder.append((parent_lords + (parent_lords[-1],), parent_end, parent_end))
            break

        periods = _to_periods(kids, parent_end)
        rdk = utils.get_running_dhasa_for_given_date(current_jd, periods)
        running = [tuple(rdk[0]), rdk[1], rdk[2]]
        ladder.append(running)

    return ladder


if __name__ == "__main__":
    utils.set_language("en")

    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place("Chennai,IN", 13.0389, 80.2619, +5.5)

    jd_at_dob = utils.julian_day_number(dob, tob)

    from datetime import datetime
    import time

    current_date_str, current_time_str = datetime.now().strftime("%Y,%m,%d;%H:%M:%S").split(";")
    y, m, d = map(int, current_date_str.split(","))
    hh, mm, ss = map(int, current_time_str.split(":"))
    fh = hh + mm / 60 + ss / 3600

    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))

    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    for dd in const.DHASA_YEAR_DURATION:
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        start_time = time.time()

        print(
            "Deha:",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_duration_type=dd,
            ),
        )

        print("new method elapsed time", time.time() - start_time)

        start_time = time.time()

        ad = get_dhasa_antardhasa(
            dob,
            tob,
            place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=dd,
        )

        print(
            utils.get_running_dhasa_at_all_levels_for_given_date(
                current_jd,
                ad,
                const.MAHA_DHASA_DEPTH.DEHA,
                extract_running_period_for_all_levels=True,
                dhasa_cycle_count=2,
            )
        )

        print("old method elapsed time", time.time() - start_time)

    exit()

    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.moola_dhasa_test()
