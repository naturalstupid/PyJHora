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
    Narayana Dasa
        1. PV Narasimha Rao - Intergrated Vedic Astrology (PVR_BOOK)
        2. Sanjay Rath - JHora software V8.0 (SANJAY_RATH)
    V5.0 Refactored to match both methods
"""
from jhora import const, utils
from jhora.horoscope.chart import charts, house
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
year_duration = const.sidereal_year
def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
def _bounded_end_jd(start_jd, place, years, backstop_days=_BACKSTOP_DAYS):
    """
    Real (transit-based) dasha-period end JD via drik._get_dhasa_end_jd(), guarded by a
    naive-average-year backstop.
    Real JHora does NOT multiply a single frozen year-length across an entire multi-year
    dasha span - it re-resolves the actual solar-transit end date via drik._get_dhasa_end_jd()
    at EACH step. This preserves the true equation-of-center / Kepler orbital speed variation
    (faster near perihelion ~Jan, slower near aphelion ~Jul), which is why individual
    antardasa durations legitimately differ by hours/minutes even though they are all
    nominally the same fraction of their parent's span.
    The `backstop_days` guard exists only to protect against the transit search behaving
    unexpectedly for unusual inputs; if the transit-based end deviates from the naive
    average-year estimate by more than `backstop_days`, fall back to the naive estimate
    rather than risk a wild jump.
    """
    naive_end = start_jd + years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, years)
    except Exception:
        return naive_end
    if real_end is None or abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end
def _split_parent_into_children_jd(parent_rasi, parent_start_jd, parent_end_jd, parent_years,
                                    antar_order_cache, place, varsha_narayana=False):
    """
    THE single shared "children" engine for one level of Narayana Dasa splitting
    (used identically by all 3 entry points - see module docstring).
    Divides [parent_start_jd, parent_end_jd] into 12 equal (by `years`) children in the
    order given by `antar_order_cache[parent_rasi]` (see `_narayana_antardhasa`):
      - Children 0..10: real per-step end via `_bounded_end_jd()` (transit-based, chained
        from the running cursor) - EXCEPT when a child's naive duration falls below
        `_SUB_DAY_THRESHOLD_DAYS` (duration-triggered, not depth-triggered), in which case
        the transit search is skipped (unreliable for tiny spans) and the boundary is
        instead interpolated proportionally within the PARENT's own already-resolved real
        span (parent_end_jd - parent_start_jd). This can happen at any level once spans get
        small enough (typically Prana/Deha), not only at a fixed recursion depth.
      - Child 11 (the last): always clamped EXACTLY to parent_end_jd - this is what
        prevents the real/naive per-step discrepancy from ever accumulating past one level.
    `parent_years` MUST already be expressed in whichever internal scale this call is
    operating on: real years when varsha_narayana=False, or "RU" (raw/varsha units, where
    1 real year = 360 RU) when varsha_narayana=True. Callers at the public API boundary
    (get_dhasa_antardhasa, get_immediate_children, get_running_dhasa_for_given_date) are
    responsible for performing that conversion before calling this function - see each of
    their docstrings for exactly where that single conversion happens.
    A parent_years of exactly 0.0 (a legitimate outcome -- see _dhasa_duration's
    cycle-2 complement, which is 0 whenever a rasi's own MD already consumed its
    full 12-year/36-RU allotment in cycle 1) simply produces 12 zero-length
    children, all coinciding with parent_start_jd == parent_end_jd. This is not
    an error condition and requires no special-casing here.
    NOTE (varsha_narayana): Varsha Narayana rescales the "years" unit (dhasa_factor =
    year_duration/360, so 1 unit ~= 1 real day instead of 1 real year). It is not yet
    confirmed whether drik._get_dhasa_end_jd() supports this rescaled unit directly, so for
    varsha_narayana=True this function keeps the original naive multiplier
    (year_duration/360) rather than guessing at an unverified real-transit call. Flag if
    this should also be routed through _bounded_end_jd().
    Returns: list of exactly 12 (child_rasi, child_start_jd, child_end_jd, child_years) tuples.
    """
    order = antar_order_cache[parent_rasi]
    parent_real_days = parent_end_jd - parent_start_jd
    base_years = parent_years / 12.0
    out = []
    jd_cursor = parent_start_jd
    for idx in range(12):
        child_rasi = order[idx]
        child_years = (parent_years - base_years * 11.0) if idx == 11 else base_years
        if idx == 11:
            child_end_jd = parent_end_jd  # exact clamp - no drift accumulation
        elif varsha_narayana:
            # See NOTE above - varsha scaling not yet routed through the real transit path.
            child_end_jd = jd_cursor + child_years * (year_duration / 360.0)
        else:
            naive_days = child_years * year_duration
            if naive_days < _SUB_DAY_THRESHOLD_DAYS:
                # Duration-triggered sub-day fallback: proportional interpolation of the
                # PARENT's real (already-resolved) span, not a fresh transit search. Also
                # covers parent_years == 0 exactly (parent_real_days == 0 too, so every
                # child correctly collapses to parent_start_jd == parent_end_jd).
                child_end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
            else:
                child_end_jd = _bounded_end_jd(jd_cursor, place, child_years)
        out.append((child_rasi, jd_cursor, child_end_jd, child_years))
        jd_cursor = child_end_jd
    return out
def _dhasa_duration(planet_positions, sign, varsha_narayana=False):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    dhasa_period = utils.count_rasis(house_of_lord, sign) if sign in const.even_footed_signs \
        else utils.count_rasis(sign, house_of_lord)
    dhasa_period -= 1  # Subtract one from the count
    if dhasa_period <= 0:
        """
            Exception (1) If the count of houses from dasa rasi to its lord is one,
            i.e. dasa rasi contains its lord, then we get zero by subtracting one from one.
            However, dasa length becomes 12 years then./
        """
        dhasa_period = 12
    if const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._EXALTED_UCCHAM:
        """ Exception (2) If the lord of dasa rasi is exalted, add one year to dasa length."""
        dhasa_period += 1
    elif const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._DEBILITATED_NEECHAM:
        """ Rule (3) If the lord of dasa rasi is debilitated, subtract one year from dasa length."""
        dhasa_period -= 1
    if varsha_narayana:
        # Per PVR ("Vedic Astrology: An Integrated Approach", ch. 30.4): "This is
        # essentially Narayana dasa compressed from 120 years to 360 solar days. If a
        # rasi's dasa is of n years, it becomes 3 x n solar days after compression."
        dhasa_period *= 3
    return dhasa_period
def _seed_from_candidate_sign(planet_positions, candidate_sign):
    """
    Shared "stronger of candidate-sign vs. 7th-from-candidate" rule.
    Used by:
      - `_narayana_dhasa_seed_for_rasi_chart()` below - candidate = D-1 Ascendant sign
        (plain Narayana Dasa's own MD seed rule).
      - Lagnamsaka-family dasas (lagnamsaka.py) - candidate = Ascendant sign in whichever
        varga chart (D-9, D-24, etc.) was requested, but this comparison itself, and
        `planet_positions`, are always D-1 (Rasi).
      - Padanadhamsa (padhanadhamsa.py, Sanjay Rath/PVR method) - candidate = Arudha
        Lagna lord's sign in the Navamsa (or other varga), comparison AND
        `planet_positions` both use that SAME varga chart.
    """
    seventh_from_candidate = (candidate_sign + const.HOUSE_7) % 12
    return house.stronger_rasi_from_planet_positions(planet_positions, candidate_sign, seventh_from_candidate)
def _narayana_dhasa_calculation(
    planet_positions,
    dhasa_seed_sign,
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    varsha_narayana=False,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """
    Narayana Dasa (depth-enabled) - "get whole table" entry point (ENTRY POINT #1 of 3
    that consume the shared `_split_parent_into_children_jd()` engine for every level
    from Antardasa downward; the Mahadasa level is computed separately - see module
    docstring for why).
    This function accepts an explicit `dhasa_seed_sign` AND arbitrary `planet_positions`,
    so it is directly reusable (unmodified) by Lagnamsaka/Padanadhamsa-family dasas -
    they just pass a different seed and/or different chart's positions.
    Output shape unchanged:
      L1: (l1, start_str, dur_years)
      L2: ((l1,l2), start_str, dur_years)
      L3+: ((l1,...,lk), start_str, dur_years)
    Every duration returned is always in REAL YEARS regardless of varsha_narayana --
    see `_append_row` below for the single point of conversion.
    dhasa_method: const.NARAYANA_OPTION.PVR_BOOK or const.NARAYANA_OPTION.SANJAY_RATH.
        Selects which book's antardasa (direction / Saturn-Ketu exception) rules to apply.
        Defaults to const.narayana_default_method when None. See `_narayana_antardhasa` for details.
    """
    # -- Validate depth --------------------------------------------------------
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    # -- Locals & constants (bind hot-path refs) --------------------------------
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    jd_to_gregorian = utils.jd_to_gregorian
    _dur = _dhasa_duration
    _antar = _narayana_antardhasa
    MAHA_ONLY = const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY
    ANTARA = const.MAHA_DHASA_DEPTH.ANTARA
    # Rounding precision increases with depth so that real-year durations (which
    # shrink rapidly at deeper levels) are not rounded away to zero. Varsha
    # durations shrink faster still (whole scheme compressed into ~1 year), so
    # use a finer base precision for varsha_narayana=True, matching the same
    # scheme used for Varsha Vimshottari (Mudda dasa).
    prec = (4 + 2 * (dhasa_level_index - 1)) if varsha_narayana else (dhasa_level_index + 1)
    # Base progression with exceptions
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    if p_to_h.get(const.KETU_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h.get(const.SATURN_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]
    # Epoch selection
    dhasa_start_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    # -- Precompute antar order per rasi (12 keys) to avoid repeated calls ----
    antar_order_cache = {}
    for r in range(12):
        antar_order_cache[r] = tuple(_antar(planet_positions, r, dhasa_method))
    # -- Precompute Cycle-1 MD durations and reuse for Cycle-2 complements ----
    md_durations_cycle1 = [float(_dur(planet_positions, lord, varsha_narayana)) for lord in dhasa_progression]
    # Every rasi's cycle-1 and cycle-2 periods must sum to a fixed per-rasi total
    # (12 real years for plain Narayana Dasa -- this is the pre-existing,
    # JHora-validated relationship already encoded by this module's cycle-2
    # formula). Since _dhasa_duration() above multiplies every period by 3 for
    # Varsha Narayana Dasa (per PVR 30.4, quoted above), the SAME per-rasi total
    # must be expressed on that identical x3 ("RU") scale: 12 * 3 = 36, not 12.
    # A cycle-2 value of exactly 0 is legitimate and expected whenever a rasi's
    # cycle-1 period already equals this per-rasi total (e.g. any rasi whose
    # lord sits in the 2nd house from it) -- for BOTH plain and varsha forms;
    # it must never be treated as an error or rounded away.
    _cycle_total_cap = 36.0 if varsha_narayana else 12.0
    # -- Helper: append one row -------------------------------------------------
    rows = []
    rows_append = rows.append
    do_round = round if round_duration else (lambda x, _: x)
    def _append_row(level_key, start_jd, years_len):
        start_str = jd_to_gregorian(start_jd)
        # years_len arrives in whatever unit the internal engine uses: real
        # years for plain Narayana Dasa, or the 3x-compressed "RU" (raw dasa
        # units) scale for Varsha Narayana Dasa (see _dhasa_duration's `*3`
        # and _split_parent_into_children_jd's (year_duration/360.0)
        # conversion). Convert to real years here, at this single point,
        # so the PUBLIC return value is uniformly in real years for both
        # forms -- matching every other dasa in this codebase (vimsottari,
        # mudda): 1 RU = 1/360 real year, independent of which year length
        # is configured.
        years_len_real = (years_len / 360.0) if varsha_narayana else years_len
        dur_out = do_round(years_len_real, prec)
        rows_append((level_key, start_str, dur_out))
    def _md_end_jd(md_start_jd, md_years):
        # One real (transit-based) call for the whole MD span - the individual antardasa
        # boundaries within it (via the shared children engine) may wobble seasonally, but
        # the LAST antardasa is always clamped back to this exact MD end, so nothing drifts
        # past one level.
        if varsha_narayana:
            return md_start_jd + md_years * (year_duration / 360.0)
        return _bounded_end_jd(md_start_jd, place, md_years)
    # -- Recursive builder for levels >= 3, ALL calls routed through the single
    # shared children engine `_split_parent_into_children_jd()` -----------------
    def _recurse(level, parent_rasi, parent_start_jd, parent_end_jd, parent_years, prefix_list):
        children = _split_parent_into_children_jd(
            parent_rasi, parent_start_jd, parent_end_jd, parent_years,
            antar_order_cache, place, varsha_narayana=varsha_narayana
        )
        if level < dhasa_level_index:
            for child_rasi, child_start_jd, child_end_jd, child_years in children:
                prefix_list.append(child_rasi)
                _recurse(level + 1, child_rasi, child_start_jd, child_end_jd, child_years, prefix_list)
                prefix_list.pop()
        else:
            for child_rasi, child_start_jd, child_end_jd, child_years in children:
                level_key = tuple(prefix_list + [child_rasi])
                _append_row(level_key, child_start_jd, child_years)
    # -----------------------------
    # Cycle #1  (MD level - NOT the shared 12-way-split engine; see module docstring)
    # -----------------------------
    for lord_idx, dhasa_lord in enumerate(dhasa_progression):
        dd = md_durations_cycle1[lord_idx]
        md_end_jd = _md_end_jd(dhasa_start_jd, dd)
        if dhasa_level_index == MAHA_ONLY:
            _append_row((dhasa_lord,), dhasa_start_jd, dd)
        elif dhasa_level_index == ANTARA:
            # AD level IS the shared engine, applied once directly here.
            children = _split_parent_into_children_jd(
                dhasa_lord, dhasa_start_jd, md_end_jd, dd,
                antar_order_cache, place, varsha_narayana=varsha_narayana
            )
            for bhukthi_lord, child_start_jd, child_end_jd, child_years in children:
                _append_row((dhasa_lord, bhukthi_lord), child_start_jd, child_years)
        else:
            # L3..L6 - shared engine applied recursively via _recurse()
            _recurse(
                level=ANTARA,                   # 2 -> build 3..N
                parent_rasi=dhasa_lord,
                parent_start_jd=dhasa_start_jd,
                parent_end_jd=md_end_jd,
                parent_years=dd,
                prefix_list=[dhasa_lord],
            )
        dhasa_start_jd = md_end_jd
    # -----------------------------
    # Cycle #2 (per-rasi complement to _cycle_total_cap, including legitimate
    # zeros -- see the note above `_cycle_total_cap`)
    # -----------------------------
    for lord_idx, dhasa_lord in enumerate(dhasa_progression):
        dd2 = _cycle_total_cap - md_durations_cycle1[lord_idx]
        if dd2 < 0.0:
            dd2 = 0.0
        md_end_jd = _md_end_jd(dhasa_start_jd, dd2)
        if dhasa_level_index == MAHA_ONLY:
            _append_row((dhasa_lord,), dhasa_start_jd, dd2)
        elif dhasa_level_index == ANTARA:
            children = _split_parent_into_children_jd(
                dhasa_lord, dhasa_start_jd, md_end_jd, dd2,
                antar_order_cache, place, varsha_narayana=varsha_narayana
            )
            for bhukthi_lord, child_start_jd, child_end_jd, child_years in children:
                _append_row((dhasa_lord, bhukthi_lord), child_start_jd, child_years)
        else:
            _recurse(
                level=ANTARA,
                parent_rasi=dhasa_lord,
                parent_start_jd=dhasa_start_jd,
                parent_end_jd=md_end_jd,
                parent_years=dd2,
                prefix_list=[dhasa_lord],
            )
        dhasa_start_jd = md_end_jd
    return rows
def _narayana_dhasa_seed_for_divisional_chart(jd_at_dob, place, divisional_chart_factor=1, chart_method=1, **kwargs):
    if divisional_chart_factor == 1:
        return _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place)
    planet_positions_rasi = charts.divisional_chart(jd_at_dob, place, **kwargs)[:const._pp_count_upto_ketu]
    h_to_p_rasi = utils.get_house_planet_list_from_planet_positions(planet_positions_rasi)
    p_to_h_rasi = utils.get_planet_to_house_dict_from_chart(h_to_p_rasi)
    seed_house = (p_to_h_rasi[const._ascendant_symbol] + divisional_chart_factor - 1) % 12
    lord_of_seed_house = house.house_owner_from_planet_positions(planet_positions_rasi, seed_house, check_during_dhasa=True)
    """
        Important:
        Take the rasi occupied by Lord of Seed House in the divisional planet_positions_rasi of interest as lagna of varga planet_positions_rasi
    """
    varga_planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    lord_sign = p_to_h_varga[lord_of_seed_house]
    dhasa_seed_sign = _seed_from_candidate_sign(varga_planet_positions, lord_sign)
    return dhasa_seed_sign
def get_dhasa_antardhasa(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    return narayana_dhasa_for_divisional_chart(dob=dob,tob=tob,place=place,years=years,months=months,
                                               sixty_hours=sixty_hours,
                                               divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method,
                                               dhasa_level_index=dhasa_level_index,
                                               dhasa_method=dhasa_method,
                                               varsha_narayana=varsha_narayana,
                                               dhasa_duration_type=dhasa_duration_type,
                                               savana_year_method=savana_year_method,
                                               round_duration=round_duration,
                                               **kwargs,
    )
def narayana_dhasa_for_divisional_chart(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """
    Narayana Dasa (depth-enabled; equal-split at each deeper level via the shared
    children engine - see module docstring / `_narayana_dhasa_calculation`)
    dhasa_method: const.NARAYANA_OPTION.PVR_BOOK or const.NARAYANA_OPTION.SANJAY_RATH.
        Selects which book's antardasa (direction / Saturn-Ketu exception) rules to apply.
        Defaults to const.narayana_default_method when None. See `_narayana_antardhasa` for details.
    """
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if divisional_chart_factor == 1:
        return narayana_dhasa_for_rasi_chart(
            dob, tob, place, years, months, sixty_hours, dhasa_level_index,
            round_duration, varsha_narayana,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            dhasa_method=dhasa_method,
            **kwargs
        )
    varga_planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _narayana_dhasa_seed_for_divisional_chart(jd_at_dob, place, divisional_chart_factor)
    return _narayana_dhasa_calculation(
        varga_planet_positions, dhasa_seed_sign, dob, tob, place,
        years=years, months=months,
        sixty_hours=sixty_hours, dhasa_level_index=dhasa_level_index,
        varsha_narayana=varsha_narayana, round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_method=dhasa_method,
        **kwargs
    )
def _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place, **kwargs):
    planet_positions = charts.rasi_chart(jd_at_dob, place, **kwargs)[:const._pp_count_upto_ketu]
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)
    asc_house = p_to_h[const._ascendant_symbol]
    dhasa_seed_sign = _seed_from_candidate_sign(planet_positions, asc_house)
    return dhasa_seed_sign
def narayana_dhasa_for_rasi_chart(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """
    Narayana Dasa (depth-enabled; equal-split at each deeper level via the shared
    children engine - see module docstring / `_narayana_dhasa_calculation`)
    dhasa_method: const.NARAYANA_OPTION.PVR_BOOK or const.NARAYANA_OPTION.SANJAY_RATH.
        Selects which book's antardasa (direction / Saturn-Ketu exception) rules to apply.
        Defaults to const.narayana_default_method when None. See `_narayana_antardhasa` for details.
    """
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    planet_positions = charts.rasi_chart(jd_at_dob, place, **kwargs)[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place, **kwargs)
    return _narayana_dhasa_calculation(
        planet_positions, dhasa_seed_sign, dob, tob, place,
        years=years, months=months,
        sixty_hours=sixty_hours, dhasa_level_index=dhasa_level_index, varsha_narayana=varsha_narayana,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_method=dhasa_method,
        **kwargs
    )
def _narayana_antardhasa(planet_positions, dhasa_rasi, dhasa_method=None):
    """
    Antardasa ORDER (which of the 12 signs, in what sequence) for a given MAHA-dasa sign
    (dhasa_rasi). NOTE: this only determines ORDER; the actual JD boundaries between the
    12 signs it returns are computed by the shared `_split_parent_into_children_jd()`
    engine, not here.
    Both PVR ("Vedic Astrology: An Integrated Approach", section 18.3) and Sanjay Rath
    ("Narayana Dasa", Ch III, rules 12-15, quoting Jaimini Sutras and BPHS 50.30-31) agree
    on the STARTING antardasa sign:
        antardhasa_seed = stronger(dhasa_rasi, 7th house from dhasa_rasi)   [compared directly,
                                                                              NOT via their lords]
        start_sign      = the sign occupied by the LORD of antardhasa_seed
    (Parasara's resolution of Jaimini's sutra 2.4.31-32, quoted verbatim by Rath: "Determine
    the stronger between the dasa Rasi and the seventh house from it. The sign occupied by
    the lord of the stronger sign shall furnish the first antardasa.")
    The two books differ on which sign's odd/even parity is used to fix the *direction*, and
    on which sign is tested for the Saturn/Ketu exceptions:
      - const.NARAYANA_OPTION.PVR_BOOK (18.3):
          direction = parity of `start_sign` (the sign antardasas actually start from).
          Saturn/Ketu exceptions tested on `antardhasa_seed` (dhasa_rasi or its 7th,
          whichever was stronger).
      - const.NARAYANA_OPTION.SANJAY_RATH (rule 12 + rule 14/15 notes):
          direction = parity of `dhasa_rasi` itself (explicitly NOT the 7th-house
          comparison used only to pick the starting point).
          Saturn/Ketu exceptions tested on `dhasa_rasi` itself.
    ------------------------------------------------------------------------------------
    NEW - JHora-matching Saturn/Ketu-exception OVERRIDE
    utils.get_dhasa_stronger_pair_rules() (populated by, e.g., Paryaaya's
    apply_jhora_dhasa_settings()) can carry an "exception" field alongside the "stronger"
    sign for each of the 6 opposition pairs (Ar/Li, Ta/Sc, Ge/Sg, Cn/Cp, Le/Aq, Vi/Pi) -
    mirroring JHora's own "Does Saturn or Ketu exception apply?" dialog field for that pair.
    (dhasa_rasi, seventh_from_dhasa_rasi) IS always one of these 6 opposition pairs, so the
    SAME override entry that forces `antardhasa_seed`'s "stronger" sign (via the
    house.stronger_rasi() Rule-0 patch) can ALSO force the Saturn/Ketu exception answer for
    THIS antardasa-seed calculation - instead of naturally checking where Saturn/Ketu
    actually sit in the real chart.
    When an override IS configured for this specific pair (i.e. the caller previously used
    apply_jhora_dhasa_settings()-style overrides for THIS chart): the override's "exception"
    value (NONE/SATURN/KETU/SATURN_KETU) is used AS-IS, replacing the natural placement-based
    check entirely for this call.
    When NO override is configured for this pair (the case for EVERY OTHER caller of this
    function that never touches the JHora-settings mechanism - plain Narayana, Lagnamsaka,
    Varsha Narayana, Padanadhamsa, Nirayana/Niryaana Shoola): behavior is COMPLETELY
    UNCHANGED - falls through to the exact same natural p_to_h-based check as before.
    ------------------------------------------------------------------------------------
    """
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    seventh_from_dhasa_rasi = (dhasa_rasi + const.HOUSE_7) % 12
    # 1) Antardasa seed = stronger of dasa rasi and the 7th house from it (common to both books)
    antardhasa_seed = house.stronger_rasi_from_planet_positions(
        planet_positions, dhasa_rasi, seventh_from_dhasa_rasi
    )
    exception_check_sign = antardhasa_seed if dhasa_method == const.NARAYANA_OPTION.PVR_BOOK else dhasa_rasi
    # --- NEW: JHora-matching exception override check (see docstring above) ---
    _pair_key = (min(dhasa_rasi, seventh_from_dhasa_rasi), max(dhasa_rasi, seventh_from_dhasa_rasi))
    _pair_override = utils.get_dhasa_stronger_pair_rules().get(_pair_key)
    _ketu_forced = None  # sentinel: None means "no override, compute naturally below"
    if _pair_override is not None and "exception" in _pair_override:
        _exc = _pair_override["exception"]
        saturn_exception = _exc in ("SATURN", "SATURN_KETU")
        _ketu_forced = _exc in ("KETU", "SATURN_KETU")
    else:
        saturn_exception = (p_to_h.get(const.SATURN_ID, -1) == exception_check_sign)
    """
        The code below is wrong and hence commented in V5.0 and will be removed in future versions
        Saturn/Ketu exception should only change direction not antardhasa seed
    """
    #if saturn_exception:
    #    antardhasa_seed = dhasa_rasi
    # 2) Starting antardasa sign = sign occupied by the lord of antardhasa_seed (common to both books)
    lord_of_seed = house.house_owner_from_planet_positions(
        planet_positions, antardhasa_seed, check_during_dhasa=True
    )
    start_sign = planet_positions[lord_of_seed + 1][1][0]
    # 3) Base direction - the sign whose parity is tested differs by book (see docstring)
    parity_sign = start_sign if dhasa_method == const.NARAYANA_OPTION.PVR_BOOK else dhasa_rasi
    direction = 1 if (parity_sign in const.odd_signs) else -1
    if saturn_exception:
        direction = 1
    if _ketu_forced is not None:
        if _ketu_forced:
            direction *= -1
    elif p_to_h.get(const.KETU_ID, -1) == exception_check_sign:
        direction *= -1
    # 4) Twelve antardasas from start_sign in final direction
    return [(start_sign + direction * i) % 12 for i in range(12)]
def _varsha_naryana_seed(dob, tob, place, years=1, months=1, sixty_hours=1, divisional_chart_factor=1, chart_method=1):
    """
    Varsha Narayana Dasa's MD seed (PVR ch. 30.4): "Just as we progress Moon by one
    constellation per year when finding Varsha Vimsottari dasa, we progress lagna by one
    rasi per year when finding Varsha Narayana dasa. In other words, we take muntha as
    lagna when finding Varsha Narayana dasa." Muntha (natal lagna progressed by one rasi
    per completed year) is substituted for the annual chart's own ascendant as the
    candidate sign; every OTHER ingredient (dasa order, dasa duration for each rasi) is
    still evaluated using the planetary positions of the annual (varsha pravesh) chart
    itself, computed at jd_at_years below -- matching the worked example in the book
    (Example 123: a D-4 chart cast at the varsha pravesh moment).
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    rasi_planet_positions = charts.rasi_chart(jd_at_years, place)[:const._pp_count_upto_ketu]
    p_to_h_rasi = utils.get_planet_house_dictionary_from_planet_positions(rasi_planet_positions)
    varga_planet_positions = charts.divisional_chart(
        jd_at_years, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method
    )[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_planet_positions)
    natal_lagna = p_to_h_rasi[const._ascendant_symbol]
    annual_house = (natal_lagna + (years - 1) + divisional_chart_factor - 1) % 12
    annual_house_owner_in_varga = house.house_owner_from_planet_positions(
        varga_planet_positions, annual_house, check_during_dhasa=True
    )
    dhasa_seed_sign = p_to_h_varga[annual_house_owner_in_varga]
    return dhasa_seed_sign
def varsha_narayana_dhasa_bhukthi(
    dob, tob, place,
    years=1, months=1, sixty_hours=1,
    divisional_chart_factor=1,
    chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """
    Varsha Narayana Dasa (depth-enabled; equal-split at each deeper level via the shared
    children engine - see module docstring / `_narayana_dhasa_calculation`)
    dhasa_method: const.NARAYANA_OPTION.PVR_BOOK or const.NARAYANA_OPTION.SANJAY_RATH.
        Selects which book's antardasa (direction / Saturn-Ketu exception) rules to apply.
        Defaults to const.narayana_default_method when None. See `_narayana_antardhasa` for details.
    """
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    varga_planet_positions = charts.divisional_chart(
        jd_at_years, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    dhasa_seed_sign = _varsha_naryana_seed(dob, tob, place, years, months, sixty_hours, divisional_chart_factor)
    nd = _narayana_dhasa_calculation(
        varga_planet_positions, dhasa_seed_sign, dob, tob, place,
        years=years, months=months,
        sixty_hours=sixty_hours, dhasa_level_index=dhasa_level_index, varsha_narayana=True,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        dhasa_method=dhasa_method,
        **kwargs
    )
    return nd
def get_running_dhasa_for_given_date(
    jd_given, jd_at_dob, place,
    divisional_chart_factor=1, chart_method=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,  # 6
    years=1, months=1, sixty_hours=1,
    varsha_narayana=False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    dhasa_seed_sign_override=None,
    **kwargs
):
    """
    Instant path finder (ENTRY POINT #3 of 3 that consume the shared
    `_split_parent_into_children_jd()` engine): return running lords and (start, end) at
    each level k=1..d for a SINGLE given moment, WITHOUT rebuilding the full multi-decade
    table. Only the MD (level 1) is located via the MD-specific mechanism (see module
    docstring); every level from AD downward calls the identical shared children engine
    used by `_narayana_dhasa_calculation()` and `get_immediate_children()`, so all
    three entry points always agree on where every boundary actually falls.
    This function never returns a duration field (only start/end tuples per level), so it
    has no unit-conversion boundary to manage -- it consumes md1_years/md2_years/
    parent_years entirely internally, in whichever scale (real years or RU) is active for
    the current varsha_narayana setting, and never round-trips that value through a public,
    externally-supplied duration the way get_immediate_children does.
    dhasa_method: const.NARAYANA_OPTION.PVR_BOOK or const.NARAYANA_OPTION.SANJAY_RATH.
        Selects which book's antardasa (direction / Saturn-Ketu exception) rules to apply.
        Defaults to const.narayana_default_method when None. See `_narayana_antardhasa` for details.
    dhasa_seed_sign_override: optional int (0..11). When None (default), the MD seed sign
        is derived exactly as before via `_narayana_dhasa_seed_for_rasi_chart()` /
        `_narayana_dhasa_seed_for_divisional_chart()` (NO behavior change for existing
        callers). When provided, this sign is used directly as the MD seed instead - this
        is the hook Lagnamsaka/Padanadhamsa-family dasas need to reuse this entire function
        (real-transit MD/AD/.../Deha resolution) unmodified, rather than duplicating it.
    """
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    # ---- derive dob,tob once (no need to recompute jd_at_dob)
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)
    # ---- base positions & seed (D1 unless varga requested)
    planet_positions = charts.rasi_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    if dhasa_seed_sign_override is not None:
        dhasa_seed_sign = int(dhasa_seed_sign_override)
    else:
        dhasa_seed_sign = _narayana_dhasa_seed_for_rasi_chart(jd_at_dob, place, **kwargs)
    if divisional_chart_factor > 1:
        varga_planet_positions = charts.divisional_chart(
            jd_at_dob, place,
            divisional_chart_factor=divisional_chart_factor, chart_method=chart_method, **kwargs
        )[:const._pp_count_upto_ketu]
        planet_positions = varga_planet_positions[:]
        if dhasa_seed_sign_override is None:
            dhasa_seed_sign = _narayana_dhasa_seed_for_divisional_chart(
                jd_at_dob, place, divisional_chart_factor, chart_method, **kwargs
            )
    # ---- bind locals
    jd_to_gregorian = utils.jd_to_gregorian
    _dur = _dhasa_duration
    _antar = _narayana_antardhasa
    # ---- progression with exceptions (same as generator)
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    dhasa_progression = const.narayana_dhasa_normal_progression[dhasa_seed_sign]
    if p_to_h.get(const.KETU_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_ketu_exception_progression[dhasa_seed_sign]
    elif p_to_h.get(const.SATURN_ID, -1) == dhasa_seed_sign:
        dhasa_progression = const.narayana_dhasa_saturn_exception_progression[dhasa_seed_sign]
    # ---- epoch (identical to the full-table generator)
    epoch_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    # ---- cache antar order per rasi (12 entries)
    antar_order_cache = {r: tuple(_antar(planet_positions, r, dhasa_method)) for r in range(12)}
    def _md_end_jd(md_start_jd, md_years):
        # Same real (transit-based) MD-boundary logic as _narayana_dhasa_calculation's
        # _md_end_jd - kept identical so this function and the full table builder always
        # agree on where each MD actually starts/ends.
        if varsha_narayana:
            return md_start_jd + md_years * (year_duration / 360.0)
        return _bounded_end_jd(md_start_jd, place, md_years)
    # ---- MD durations (cycle 1) and complements (cycle 2)
    md1_years = [float(_dur(planet_positions, lord, varsha_narayana)) for lord in dhasa_progression]
    # Same per-rasi total-of-12-(real)-years rule as _narayana_dhasa_calculation
    # (see the detailed comment there): on the varsha RU scale this total
    # becomes 36, not 12, since _dhasa_duration already multiplied by 3.
    _cycle_total_cap = 36.0 if varsha_narayana else 12.0
    md2_years = [max(0.0, _cycle_total_cap - y) for y in md1_years]
    md_lords = list(dhasa_progression) + list(dhasa_progression)
    md_years = md1_years + md2_years
    # ---- real (chained, transit-based) MD start/end JDs (length 24 + 1 sentinel)
    # NOTE: this walks all 24 MDs to LOCATE the running one - it does NOT rebuild the
    # full AD..Deha table (no reliance on rebuilding full tables just to find a running
    # position; only the single containing MD's own sub-levels get expanded below).
    md_starts_jd = [epoch_jd]
    for i in range(len(md_years)):
        md_starts_jd.append(_md_end_jd(md_starts_jd[-1], md_years[i]))
    # ---- select MD by JD (jd in [start_i, start_{i+1}); last open-ended)
    from bisect import bisect_right
    i = bisect_right(md_starts_jd, jd_given) - 1
    if i < 0:
        i = 0
    if i >= len(md_lords):
        i = len(md_lords) - 1
    md_lord = int(md_lords[i])
    md_year = float(md_years[i])
    md_start = md_starts_jd[i]
    md_end = md_starts_jd[i + 1]
    out = []
    out.append(((md_lord,), jd_to_gregorian(md_start), jd_to_gregorian(md_end)))
    # ---- descend levels 2..d, calling the SAME shared children-splitter used by
    # _narayana_dhasa_calculation() and get_immediate_children() at every step -
    # only the ONE containing child at each level is expanded (no full-table rebuild).
    parent_lord = md_lord
    parent_start_jd = md_start
    parent_end_jd = md_end
    parent_years = md_year
    for level in range(2, int(dhasa_level_index) + 1):
        children = _split_parent_into_children_jd(
            parent_lord, parent_start_jd, parent_end_jd, parent_years,
            antar_order_cache, place, varsha_narayana=varsha_narayana
        )
        chosen = children[-1]
        for child_rasi, child_start_jd, child_end_jd, child_years in children:
            if jd_given < child_end_jd:
                chosen = (child_rasi, child_start_jd, child_end_jd, child_years)
                break
        child_rasi, child_start_jd, child_end_jd, child_years = chosen
        prefix = out[-1][0] + (child_rasi,)
        out.append((prefix, jd_to_gregorian(child_start_jd), jd_to_gregorian(child_end_jd)))
        parent_lord = child_rasi
        parent_start_jd = child_start_jd
        parent_end_jd = child_end_jd
        parent_years = child_years
    return out
def get_immediate_children(
    parent_lords,
    parent_start,
    parent_duration=None,
    parent_end=None,
    *,
    jd_at_dob,
    place,
    divisional_chart_factor: int = 1,
    chart_method=1,
    varsha_narayana = False,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    dhasa_method=None,
    **kwargs
):
    """
    Narayana - return ONLY the immediate (p -> p+1) children inside the given parent span
    (ENTRY POINT #2 of 3 that consume the shared `_split_parent_into_children_jd()` engine -
    same function, same call signature, as used by `_narayana_dhasa_calculation()` and
    `get_running_dhasa_for_given_date()`).
    Note: this function never needs an MD-seed override (unlike
    `get_running_dhasa_for_given_date`) because antardasa order only ever depends on the
    CURRENT parent sign (`parent_lords[-1]`), never on the original MD seed - so it is
    already directly reusable, unmodified, by Lagnamsaka/Padanadhamsa-family dasas.
    parent_duration / parent_end are ALWAYS interpreted, and derived, in REAL YEARS <->
    real elapsed calendar time using the ORDINARY year_duration conversion -- this is
    completely independent of varsha_narayana, exactly matching how get_dhasa_antardhasa()
    above expresses its own returned durations. There is no "/360" or "*360" anywhere in
    this years<->days conversion step, regardless of mode.
    The "RU" (raw/varsha unit) scale used internally by `_split_parent_into_children_jd()`
    when varsha_narayana=True (1 RU = year_duration/360 real days, i.e. 1 real year = 360
    RU) is an implementation detail of THAT shared engine alone. It is applied here EXACTLY
    ONCE -- converting the already-correct real-year duration into RU immediately before,
    and only for, the single call into `_split_parent_into_children_jd()` below. Applying
    this factor anywhere else (e.g. also while deriving the duration from a given
    parent_end) double-counts it and inflates every level's span by an extra factor of
    360/12 = 30 per additional level of tree expansion -- exactly the runaway growth
    (days -> years -> centuries -> tens of thousands of years) that results if this
    conversion is applied more than once.
    A zero-duration parent (parent_end == parent_start, or parent_duration == 0) is
    legitimate and is NOT treated as an error: it correctly cascades into twelve
    children, all with child_start == child_end == parent_start. Only a genuinely
    INVALID span (parent_end strictly before parent_start) returns an empty list.
    This matters for interactive callers such as a UI tree widget: an empty return
    for a *valid* (zero-duration) span would otherwise be indistinguishable from a
    real "nothing here" case, and could leave such a caller in an inconsistent state
    after it has already made UI changes in anticipation of receiving children -- see
    dhasa_tree_widget.py's own additional defensive handling for the (now rare,
    should-not-normally-happen) case of a genuinely empty return.
    dhasa_method: const.NARAYANA_OPTION.PVR_BOOK or const.NARAYANA_OPTION.SANJAY_RATH.
        Selects which book's antardasa (direction / Saturn-Ketu exception) rules to apply.
        Defaults to const.narayana_default_method when None. See `_narayana_antardhasa` for details.
    """
    if dhasa_method is None:
        dhasa_method = const.narayana_default_method
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_sign = int(path[-1])
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple).")
    # Step 1: resolve (start_jd, end_jd) and the parent's REAL-YEAR duration using the
    # ORDINARY year_duration conversion -- identical regardless of varsha_narayana.
    if parent_end is None:
        parent_years_real = float(parent_duration)
        end_jd = start_jd + parent_years_real * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years_real = (end_jd - start_jd) / year_duration
    # Only a genuinely invalid (backwards) span is rejected. An EQUAL
    # (zero-duration) span is legitimate -- see docstring above -- and falls
    # through to _split_parent_into_children_jd(), which already handles
    # parent_years == 0 correctly (twelve children, all pinned to start_jd).
    if end_jd < start_jd:
        return []
    # Step 2: convert to the shared engine's internal scale, exactly once, ONLY for the
    # call below (1 real year = 360 RU when varsha_narayana=True; unchanged otherwise).
    parent_years_engine = parent_years_real * 360.0 if varsha_narayana else parent_years_real
    planet_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor, **kwargs
    )[:const._pp_count_upto_ketu]
    antar_order_cache = {parent_sign: tuple(_narayana_antardhasa(planet_positions, parent_sign, dhasa_method))}
    children = _split_parent_into_children_jd(
        parent_sign, start_jd, end_jd, parent_years_engine, antar_order_cache, place,
        varsha_narayana=varsha_narayana
    )
    return [
        [path + (child_rasi,), _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)]
        for child_rasi, child_start_jd, child_end_jd, _child_years in children
    ]

if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7) # PVR_Rao Example
    #dob = drik.Date(1872,8,15) # Sanjay Rath book Example
    tob = (10, 34, 0) # PVR_Rao Example
    #tob = (5,8,0)  # Sanjay Rath book Example
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5) # PVR_Rao Example
    #place = drik.Place('Aurobindo',22+32/60,88+22/60,+5.5) # Sanjay Rath book Example
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    _dhasa_method = const.NARAYANA_OPTION.SANJAY_RATH
    db = get_dhasa_antardhasa(dob, tob, place,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
                    dhasa_method=_dhasa_method,
                    varsha_narayana=False,round_duration=False)
    for lords,start,durn in db:
        print(utils.RAASI_LIST[lords[0]],f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])} {durn} years")
    exit()
    db = narayana_dhasa_for_divisional_chart(dob, tob, place,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                    dhasa_method=_dhasa_method)
    md_ad_seq = {}
    for lords, start_date, durn in db:
        y, m, d, fh = start_date
        start_str = f"({y}-{m}-{d} {utils.to_dms(fh)})"
        lord, sub_lord = lords
        lord_name = utils.RAASI_SHORT_LIST[lord]
        if lord_name not in md_ad_seq:
            md_ad_seq[lord_name] = []
        sub_lord_name = utils.RAASI_SHORT_LIST[sub_lord]
        md_ad_seq[lord_name].append(sub_lord_name)
        #print(lord_name, sub_lord_name, start_str, durn)
    md_ad_seq = {k: ','.join(v) for k, v in md_ad_seq.items()}
    for lord, sub_lord_seq in md_ad_seq.items():
        print(lord, " > ", md_ad_seq[lord])

    print("\n--- Running dasha chain (all 6 levels) for ",dob,tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    grd = get_running_dhasa_for_given_date(
        current_jd, jd_at_dob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
        divisional_chart_factor=1,
        varsha_narayana=False,
        dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR,
        dhasa_method=_dhasa_method,
    )
    for lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2) in grd:
        label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
        print(f"{label:20s} {y1}-{m1:02d}-{d1:02d} {utils.to_dms(fh1)}  ->  {y2}-{m2:02d}-{d2:02d} {utils.to_dms(fh2)}")
