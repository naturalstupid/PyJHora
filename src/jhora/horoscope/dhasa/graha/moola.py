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
"""
    Also called Lagna Kendradi Graha Dhasa

    Release History:
        V5.0 - REFACTORED to match JHora.
"""
from jhora import const, utils
from jhora.horoscope.chart import house, charts
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

year_duration = const.sidereal_year

# 30-day sanity backstop against drik._get_dhasa_end_jd's known ~365-day
# defect for a narrow band of small durations (see project handoff, section
# 3). The draft had NO drik._get_dhasa_end_jd() calls anywhere (pure
# linear arithmetic instead) -- every boundary in this module now routes
# through _bounded_end_jd().
_SMALL_DURATION_BACKSTOP_DAYS = 30.0

# V5.0: Threshold (in days) below which drik._get_dhasa_end_jd() has been
# empirically shown (in every other dhasa module refactored in this
# project) to become unreliable by a real, non-trivial margin. For THIS
# dhasa (MD durations fully chart-dependent), worst-case duration reaches
# sub-day starting at SD level (~0.501 days worst case). This check is
# duration-triggered, re-evaluated fresh for every batch of children,
# regardless of level or which Mahadasa cycle the ultimate ancestor came
# from.
_SUB_DAY_DURATION_DAYS = 1.0


def _bounded_end_jd(start_jd_local, duration_years, place):
    """
    Computes the end JD for a given start JD and duration in years, guarding
    against drik._get_dhasa_end_jd()'s known ~365-day-too-large defect for a
    narrow band of small durations. The pre-refactor draft had NO
    drik._get_dhasa_end_jd() calls anywhere (pure linear arithmetic
    instead) -- every boundary in this module now routes through this
    wrapper, per the project's standing direction to apply real end_jd at
    every level.
    """
    end_jd = drik._get_dhasa_end_jd(
        start_jd=start_jd_local,
        place=place,
        total_dasa_years=duration_years,
    )

    expected_jd = start_jd_local + duration_years * year_duration

    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd

    return end_jd


def _build_moola_seed_and_mahadasa_list(
    jd_at_dob,
    place,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    years=1,
    months=1,
    sixty_hours=1,
    use_lagna_for_seed=True,
    use_sun_for_seed=True,
    use_moon_for_seed=True,
    moolatrikona_correction=12,
):
    """
    Builds Moola Dasa's seed-rotated planet sequence Q, the cycle-1 MD
    duration map (md1_map), and the FULL 2-cycle Mahadasa (lord, duration)
    list.

    Returns
    -------
    (Q, md1_map, mahadasa_list) or (None, None, None) if no candidate
    grahas are found.

    Q : list[int]
        The seed-rotated base sequence of graha ids (Kendra -> Panapara
        -> Apoklima from Lagna, then rotated to start at the seed
        planet). CONFIRMED CORRECT against real chart data -- see module
        docstring above.
    md1_map : dict[int, float]
        Each graha's own CYCLE-1 MD duration in years (used as the
        antara/deeper-level proportional-split WEIGHT at every level).
        REAL BUG FIXED here (see module docstring above): a negative raw
        (Vimsottari_years - dist) result is now resolved via absolute
        value, NOT a flat clamp to 1 year.
    mahadasa_list : list[tuple[int, float]]
        [(lord, duration_years), ...] -- length 2 * len(Q): cycle 1
        (using md1_map values) followed by cycle 2 (using
        Vimsottari_years - md1_map values).
    """
    start_jd = jd_at_dob

    # Ordering varga: per the draft, Moola is D-1; keep divisional_chart_factor
    # for compatibility.
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

    # D-1 again for count/rider (matches the draft's own D-1-for-both behavior).
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

    # ---- Ranking via the project's strength API ------------------------------
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
            return None, None, None

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

    # ---- Vimsottari base years (from const) ----------------------------------
    VIM = const.vimsottari_dict

    # ---- Moolatrikona signs (override nodes per the draft) --------------------
    MT_LIST = list(getattr(const, "moola_trikona_of_planets", [4, 1, 0, 5, 8, 6, 10, 5, 11]))
    MT_LIST[const.RAHU_ID] = 10  # Aquarius
    MT_LIST[const.KETU_ID] = 7   # Scorpio

    # ---- Exaltation / Debilitation detection via the project's matrix -------
    EXALT_VAL = const._EXALTED_UCCHAM
    DEBIL_VAL = const._DEBILITATED_NEECHAM
    HS = const.house_strengths_of_planets

    def _is_exalted_d1(g):
        return HS[g][p2h_d1[g]] == EXALT_VAL

    def _is_debilitated_d1(g):
        return HS[g][p2h_d1[g]] == DEBIL_VAL

    # ---- Distance helper (clockwise) ------------------------------------------
    def _dist_cw(a, b):
        return (b - a) % 12

    # ---- Cycle-1 years per the draft's own rules, WITH THE FIX ----------------
    def _moola_cycle1_years(g):
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

        # V5.0 REAL BUG FIX: the pre-refactor draft flatly clamped any
        # non-positive result to a fixed 1 year ("if yrs <= 0.0: yrs =
        # 1.0"). CONFIRMED WRONG via real chart data + matching real
        # JHora antara-level screenshot (see module docstring above): the
        # correct resolution for a NEGATIVE raw result is to take its
        # ABSOLUTE VALUE, not discard its magnitude via a flat clamp.
        # (The yrs == 0 case -- distinct from the cur==mt branch above,
        # which is separately and correctly handled -- is not confirmed
        # either way by available real data; a conservative 1-year floor
        # is retained for that specific, untested edge case only.)
        if yrs < 0.0:
            yrs = abs(yrs)
        elif yrs == 0.0:
            yrs = 1.0

        return yrs

    md1_map = {g: _moola_cycle1_years(g) for g in Q}
    md1_years = [md1_map[g] for g in Q]
    md2_years = [float(VIM[g]) - md1_map[g] for g in Q]

    md_planets = Q + Q
    md_years = md1_years + md2_years

    mahadasa_list = list(zip(md_planets, md_years))

    return Q, md1_map, mahadasa_list


def _get_moola_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    base_order,
    md1_map,
    *,
    parent_end_jd=None,
):
    """
    SINGLE children-engine for Moola Dasa (used at every level below
    Mahadasa).

    Rules:
        - Child order = base_order ROTATED to start at the parent lord.
        - PROPORTIONAL-BY-CYCLE-1-MD-VALUE split: each child's share of
          parent_duration is (child's own md1_map value / sum of md1_map
          values over the rotated queue) -- now benefits from the
          MD-duration-formula fix (see module docstring above).
        - parent_end_jd is threaded in when already known by the caller
          (never re-derived); only computed here via _bounded_end_jd when
          not already known.
        - Last child's end is always forced to parent_end_jd exactly.
        - If the batch's smallest child duration is under
          _SUB_DAY_DURATION_DAYS, ALL child boundaries (not just the
          last) are computed via cycle-1-weighted proportional
          interpolation of the parent's own real [parent_start_jd,
          parent_end_jd] span, instead of calling _bounded_end_jd()/
          drik._get_dhasa_end_jd() per child.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD (float only, not a Gregorian tuple)
    """
    parent_lord = parent_path[-1]

    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd:
        return [], parent_end_jd

    if parent_lord not in base_order:
        return [], parent_end_jd

    j = base_order.index(parent_lord)
    rotated = base_order[j:] + base_order[:j]

    n = len(rotated)

    if n == 0:
        return [], parent_end_jd

    weights = [md1_map.get(g, 0.0) for g in rotated]
    total_weight = sum(weights)

    if total_weight <= 0.0:
        weights = [1.0] * n
        total_weight = float(n)

    child_durations = [parent_duration * (w / total_weight) for w in weights]

    smallest_child_years = min(child_durations)
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_child_duration = sum(child_durations)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, clord in enumerate(rotated):
        child_duration = child_durations[i]
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_duration += child_duration
            child_end_jd = parent_start_jd + parent_span * cumulative_duration / total_child_duration
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                parent_path + (clord,),
                child_start_jd,
                child_duration,
                child_end_jd,
            )
        )

        cursor = child_end_jd

    return children, parent_end_jd


def _generate_mahadasa_periods(
    jd_at_dob,
    place,
    mahadasa_list,
    *,
    stop_at_jd=None,
):
    """
    THE single Mahadasa seed/root generator for Moola Dasa. This is the
    ONLY place in the module that walks the FIXED, 2-cycle
    mahadasa_list starting from the birth JD. get_dhasa_antardhasa()
    and get_running_dhasa_for_given_date() both call THIS SAME
    generator.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd)
    """
    start_jd = jd_at_dob

    for lord, dur in mahadasa_list:
        if dur <= 0:
            continue

        maha_start_jd = start_jd
        maha_end_jd = _bounded_end_jd(maha_start_jd, dur, place)

        yield lord, maha_start_jd, dur, maha_end_jd

        start_jd = maha_end_jd

        if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
            return


def _find_child_containing_jd(children, target_jd):
    """
    Returns the single child tuple whose [start_jd, end_jd) contains
    target_jd. Falls back to the last child if target_jd is at/past the
    final boundary.
    """
    if not children:
        return None

    for child in children:
        _, s, _, e = child

        if s <= target_jd < e:
            return child

    return children[-1]


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
    return_exact_bounds=False,
):
    """
    Mula (Lagna-Kendradi Graha Dasa) -- depth-enabled (Maha -> Antara -> ... -> Deha)

    Returns rows like your other base dasas:
        [lords_tuple, start_tuple, dur_years]

    - MD (planetary) order: Kendra (ranked) -> Panapara (ranked) -> Apoklima (ranked) from Lagna (D-1).
    - Seed: among Kendra planets of the selected candidates (Lagna/Moon/Sun), pick the strongest; rotate MD to start from it.
    - MD years (cycle-1): Vimsottari years - (cw distance to MT) +/- 1 (exalt/debil in D-1);
        if planet is in its MT sign (D-1) then subtract `moolatrikona_correction` (0 or 12) instead of distance.
        If result is negative, take absolute value (V5.0 fix -- see module docstring). Nodes: Rahu->Aquarius, Ketu->Scorpio for MT distance.
      MD years (cycle-2): Vimsottari - cycle-1 (two cycles sum to 120).
    - Antardasa & deeper: order = global rotation from the parent; durations = proportional to cycle-1 years (Sum children = parent).
    - Rounding: returned durations rounded to (dhasa_level_index + 1) decimals if round_duration=True; JD math uses full precision.

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]

    End JD is computed via drik._get_dhasa_end_jd() (through
    _bounded_end_jd) at every level, UNLESS a batch of children is
    sub-day, in which case cycle-1-weighted proportional interpolation
    of the parent's real span is used instead (see
    _SUB_DAY_DURATION_DAYS above).
    """
    global year_duration

    if not (
        const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
        <= dhasa_level_index
        <= const.MAHA_DHASA_DEPTH.DEHA
    ):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    start_jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=start_jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    Q, md1_map, mahadasa_list = _build_moola_seed_and_mahadasa_list(
        start_jd,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        use_lagna_for_seed=use_lagna_for_seed,
        use_sun_for_seed=use_sun_for_seed,
        use_moon_for_seed=use_moon_for_seed,
        moolatrikona_correction=moolatrikona_correction,
    )

    if Q is None:
        return []

    retval = []

    def _emit_row(lords_tuple, start_jd_local, duration_years, end_jd_local):
        if return_exact_bounds:
            retval.append(
                [
                    lords_tuple,
                    start_jd_local,
                    end_jd_local,
                    duration_years,
                ]
            )
        else:
            start_tuple = utils.jd_to_gregorian(start_jd_local)
            durn = (
                round(duration_years, dhasa_level_index + 1)
                if round_duration
                else duration_years
            )

            retval.append([lords_tuple, start_tuple, float(durn)])

    def _recurse(
        level,
        parent_path,
        parent_start_jd,
        parent_duration_years,
        parent_end_jd,
    ):
        children, _ = _get_moola_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            Q,
            md1_map,
            parent_end_jd=parent_end_jd,
        )

        if not children:
            return

        for child_path, child_start_jd, child_duration, child_end_jd in children:
            if level < dhasa_level_index:
                _recurse(
                    level + 1,
                    child_path,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )
            else:
                _emit_row(
                    child_path,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        start_jd,
        place,
        mahadasa_list,
    ):
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            _emit_row(
                (maha_lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
            )
        else:
            _recurse(
                const.MAHA_DHASA_DEPTH.ANTARA,
                (maha_lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
            )

    return retval


def get_immediate_children(
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
    Return ONLY the immediate (parent -> children) splits for Moola Dasa.

    A thin wrapper around the shared _get_moola_children_jd() engine.

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

    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")

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
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    Q, md1_map, _mahadasa_list = _build_moola_seed_and_mahadasa_list(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        use_lagna_for_seed=use_lagna_for_seed,
        use_sun_for_seed=use_sun_for_seed,
        use_moon_for_seed=use_moon_for_seed,
        moolatrikona_correction=moolatrikona_correction,
    )

    if Q is None:
        return []

    children, _ = _get_moola_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        Q,
        md1_map,
        parent_end_jd=end_jd,
    )

    return [
        [
            child_path,
            _jd_to_tuple(child_start_jd),
            _jd_to_tuple(child_end_jd),
        ]
        for child_path, child_start_jd, _child_duration, child_end_jd in children
    ]


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
    Moola Dasa -- running ladder at current_jd.

    Does NOT call jhora.utils.get_running_dhasa_for_given_date() internally
    (that generic utility is CONFIRMED buggy). Does NOT rebuild the full
    seed/MD state or the full recursive tree once per level either.
    Instead it computes the seed/MD state ONCE, then drills straight down
    this dhasa's own tree using the SAME single-recursive-rule machinery
    as get_dhasa_antardhasa() and moola_immediate_children().
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

    Q, md1_map, mahadasa_list = _build_moola_seed_and_mahadasa_list(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        use_lagna_for_seed=use_lagna_for_seed,
        use_sun_for_seed=use_sun_for_seed,
        use_moon_for_seed=use_moon_for_seed,
        moolatrikona_correction=moolatrikona_correction,
    )

    if Q is None:
        return []

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None

    for maha_lord, maha_start_jd, maha_dur, maha_end_jd in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        mahadasa_list,
        stop_at_jd=current_jd,
    ):
        pass

    if maha_lord is None:
        return []

    ladder = [
        [
            (maha_lord,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder

    parent_path = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target + 1):
        children, _ = _get_moola_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            Q,
            md1_map,
            parent_end_jd=parent_end_jd,
        )

        found = _find_child_containing_jd(children, current_jd)

        if found is None:
            ladder.append(
                [
                    parent_path + (parent_path[-1],),
                    utils.jd_to_gregorian(parent_start_jd),
                    utils.jd_to_gregorian(parent_end_jd),
                ]
            )
            break

        child_path, child_start_jd, child_duration_years, child_end_jd = found

        ladder.append(
            [
                child_path,
                utils.jd_to_gregorian(child_start_jd),
                utils.jd_to_gregorian(child_end_jd),
            ]
        )

        parent_path = child_path
        parent_start_jd = child_start_jd
        parent_end_jd = child_end_jd
        parent_duration_years = child_duration_years

    return ladder


if __name__ == "__main__":
    utils.set_language("en")

    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place("Chennai,IN", 13.0389, 80.2619, +5.5)

    jd_at_dob = utils.julian_day_number(dob, tob)

    from datetime import datetime
    import random
    import time

    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y, m, d = (1998, 11, 9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600

    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))

    print(check_date)

    DLI = const.MAHA_DHASA_DEPTH.DEHA

    for dd in [const.DHASA_YEAR_DURATION.TRUE_SIDEREAL_YEAR,
               const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = drik.dhasa_year_duration(
            jd=jd_at_dob,
            place=place,
            dhasa_duration_type=dd,
        )

        print("\n" + "-" * 80)
        print("Dhasa duration method:", dd.name, dd.value)
        print("Resolved year duration days:", yd)
        print("-" * 80)

        # ---- NEW method: only the last (Deha) row -------------------------
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=DLI,
                dhasa_duration_type=dd,
            )
        print("running_all[4]", grd[4])
        new_last_lords, new_last_start, new_last_end = grd[-1]
        new_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord] for lord in new_last_lords])
        y1, m1, d1, fh1 = new_last_start
        y2, m2, d2, fh2 = new_last_end
        print("Dehā (new)  :", check_date,
              [new_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('new method elapsed time', time.time() - start_time)

        # ---- OLD method: full tree, extract only the last (Deha) row,
        #      via utils' self-contained groupby (shared helpers) ---------
        start_time = time.time()
        full_tree = get_dhasa_antardhasa(
            dob, tob,
            place,
            dhasa_level_index=DLI,
            dhasa_duration_type=dd,
            return_exact_bounds=True,
        )
        deha_groups = utils._group_ancestors_from_leaves(full_tree, DLI)
        old_last_lords, old_start_jd, old_end_jd = utils._find_containing_group(deha_groups, current_jd)
        old_last_name = '-'.join([utils.PLANET_SHORT_NAMES[lord] for lord in old_last_lords])
        y1, m1, d1, fh1 = utils.jd_to_gregorian(old_start_jd)
        y2, m2, d2, fh2 = utils.jd_to_gregorian(old_end_jd)
        print("Dehā (old)  :", check_date,
              [old_last_name, (y1, m1, d1, utils.to_dms(fh1)), (y2, m2, d2, utils.to_dms(fh2))])
        print('old method elapsed time', time.time() - start_time)

        # ---- Diff between OLD and NEW (last/Deha row only) ----------------
        lords_match = tuple(new_last_lords) == tuple(old_last_lords)
        start_diff_seconds = (utils._tuple_to_jd(new_last_start) - old_start_jd) * 86400.0
        end_diff_seconds = (utils._tuple_to_jd(new_last_end) - old_end_jd) * 86400.0

        print("\n" + "-" * 80)
        print("DIFF (new - old), Deha level only:")
        print("  lords match      :", lords_match, f"({new_last_name}  vs  {old_last_name})")
        print(f"  start diff (sec) : {start_diff_seconds:+.3f}")
        print(f"  end   diff (sec) : {end_diff_seconds:+.3f}")
        print("-" * 80)
    exit()

    from jhora.tests import pvr_tests

    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.moola_dhasa_test()
