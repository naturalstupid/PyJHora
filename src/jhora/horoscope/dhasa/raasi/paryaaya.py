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
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts, house
from jhora.horoscope.dhasa.raasi.narayana import _dhasa_duration as _narayana_dhasa_duration
from jhora.horoscope.dhasa.raasi.narayana import _narayana_antardhasa
"""
Paryaaya Dasa.

Ref: https://www.indiadivine.org/content/topic/1209053-varnada-and-paryaaya-dasa/

Seed: the nth house of the D-n chart (same seeding idea as Mandooka Dasa).
Based on the modality of that seed sign, one of three variants is used:
  - Seed is a dual sign     -> Chara Paryaaya Dasa
  - Seed is a movable sign  -> Ubhaya Paryaaya Dasa
  - Seed is a fixed sign    -> Sthira Paryaaya Dasa

Starting sign (sr) for each variant:
  - Chara:  strongest of the 3 trines from the seed (1st/5th/9th group).
  - Ubhaya: strongest of the 4 quadrants from the seed (1st/4th/7th/10th group).
  - Sthira: stronger of the seed and its 7th house.

Progression order from sr (12 Mahadasas per cycle, 2 cycles):
  - Chara:  1,5,9, 2,6,10, 3,7,11, 4,8,12 (trinal grouping)
  - Ubhaya: 1,4,7,10, 2,5,8,11, 3,6,9,12 (quadrant grouping)
  - Sthira: 1,7, 2,8, 3,9, 4,10, 5,11, 6,12 (opposition-pair grouping)

Direction: forward if sr is odd-footed, reverse if even-footed
(Ar,Ta,Ge,Li,Sc,Sg = odd-footed; Cn,Le,Vi,Cp,Aq,Pi = even-footed),
reversed if Saturn occupies sr.

2nd Mahadasa cycle: duration of each sign = 12 - its 1st-cycle duration.

Antardasa (level 2+): narayana.py's own antardasa engine, applied at every level.

V5.0 - Chart-specific "stronger of X & Y" / Aquarius-Scorpio co-lord overrides
(apply_jhora_dhasa_settings(), matching JHora's own "Paryaaya dasa options"
dialog) may be required to match JHora exactly for a given chart - see
__main__ for example usage. These are chart-specific; never reuse one
chart's override values for another chart.
"""
dhasa_adhipati_list = [0, 4, 6, 10, 0, 4, 6, 10, 0, 4, 6, 10]
antardhasa_list = [6, 0, 8, 10, 4, 8, 6, 0, 8, 10, 4, 8]
chara_paryaaya_list = [1, 5, 9, 2, 6, 10, 3, 7, 11, 4, 8, 12]
ubhaya_paryaaya_list = [1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12]
sthira_paryaaya_list = [1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12]
year_duration = const.sidereal_year
_DEFAULT_VARGA = 6
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30
_USE_SANITY_BACKSTOP = True
_USE_SUB_DAY_FALLBACK = True
def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration
def _bounded_end_jd(start_jd, place, duration_in_years, backstop_days=_BACKSTOP_DAYS):
    """Return the real (transit-based) end JD, with a naive-estimate backstop."""
    naive_end = start_jd + duration_in_years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, duration_in_years)
    except Exception:
        return naive_end
    if real_end is None or real_end <= start_jd:
        return naive_end
    if _USE_SANITY_BACKSTOP and abs(real_end - naive_end) > backstop_days:
        return naive_end
    return real_end
def _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq):
    """Return the (start,end) JD pairs for each child in child_seq."""
    child_years = parent_years / 12.0
    parent_real_days = parent_end_jd - parent_start_jd
    n = len(child_seq)
    out = []
    cursor = parent_start_jd
    for idx in range(n):
        is_last = (idx == n - 1)
        if is_last:
            end_jd = parent_end_jd
        elif _USE_SUB_DAY_FALLBACK and (child_years * year_duration) < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
        else:
            end_jd = _bounded_end_jd(cursor, place, child_years)
        out.append((cursor, end_jd))
        cursor = end_jd
    return out
def apply_jhora_dhasa_settings(
    default_varga=None,
    aquarius_owner=None,
    scorpio_owner=None,
    stronger_of_Ar_and_Li=None,
    stronger_of_Ta_and_Sc=None,
    stronger_of_Ge_and_Sg=None,
    stronger_of_Cn_and_Cp=None,
    stronger_of_Le_and_Aq=None,
    stronger_of_Vi_and_Pi=None,
):
    """
    Apply JHora's own "Paryaaya dasa options" dialog overrides for THIS
    chart (owners and/or stronger-of-pair values). These are chart-specific;
    never reuse one chart's values for a different chart.
    """
    global _DEFAULT_VARGA
    if default_varga is not None:
        _DEFAULT_VARGA = int(default_varga)
    owners = {}
    if scorpio_owner is not None:
        owners[const.SCORPIO] = int(scorpio_owner)
    if aquarius_owner is not None:
        owners[const.AQUARIUS] = int(aquarius_owner)
    pair_args = [
        (const.ARIES, const.LIBRA, stronger_of_Ar_and_Li),
        (const.TAURUS, const.SCORPIO, stronger_of_Ta_and_Sc),
        (const.GEMINI, const.SAGITTARIUS, stronger_of_Ge_and_Sg),
        (const.CANCER, const.CAPRICORN, stronger_of_Cn_and_Cp),
        (const.LEO, const.AQUARIUS, stronger_of_Le_and_Aq),
        (const.VIRGO, const.PISCES, stronger_of_Vi_and_Pi),
    ]
    stronger_pairs = {}
    for sign_a, sign_b, override in pair_args:
        if override is None:
            continue
        forced_sign, exception_planet = override
        stronger_pairs[(sign_a, sign_b)] = {
            "stronger": int(forced_sign),
            "exception": exception_planet,
        }
    existing_pairs = dict(utils.get_dhasa_stronger_pair_rules())
    existing_pairs.update(stronger_pairs)
    utils.set_owner_overrides_for_dhasa({
        "owners": owners,
        "stronger_pairs": existing_pairs,
    })
def clear_jhora_dhasa_settings():
    """Reset all JHora-settings overrides back to defaults."""
    global _DEFAULT_VARGA
    _DEFAULT_VARGA = 6
    utils.set_owner_overrides_for_dhasa(None)
def print_natural_stronger_rasi_defaults(planet_positions):
    """Print the natural (unforced) stronger-of-pair and Sc/Aq owner results."""
    saved_pairs = dict(utils.get_dhasa_stronger_pair_rules())
    saved_aq = getattr(const, 'aquarius_owner_for_dhasa_calculations', None)
    saved_sc = getattr(const, 'scorpio_owner_for_dhasa_calculations', None)
    try:
        utils.set_owner_overrides_for_dhasa(None)
        pair_labels = [
            ("Ar", "Li", const.ARIES, const.LIBRA), ("Ta", "Sc", const.TAURUS, const.SCORPIO),
            ("Ge", "Sg", const.GEMINI, const.SAGITTARIUS), ("Cn", "Cp", const.CANCER, const.CAPRICORN),
            ("Le", "Aq", const.LEO, const.AQUARIUS), ("Vi", "Pi", const.VIRGO, const.PISCES),
        ]
        print("Natural (unforced) 'stronger of X & Y' results:")
        for name_a, name_b, sign_a, sign_b in pair_labels:
            winner = house.stronger_rasi_from_planet_positions(planet_positions, sign_a, sign_b)
            winner_name = name_a if winner == sign_a else name_b
            print(f"  Stronger of {name_a} & {name_b}: {winner_name}")
        aq_owner = house.house_owner_from_planet_positions(planet_positions, const.AQUARIUS)
        sc_owner = house.house_owner_from_planet_positions(planet_positions, const.SCORPIO)
        print(f"  Lord of Aquarius (natural): planet id {aq_owner}")
        print(f"  Lord of Scorpio (natural): planet id {sc_owner}")
    finally:
        utils.set_owner_overrides_for_dhasa({
            "owners": {
                **({const.AQUARIUS: saved_aq} if saved_aq is not None else {}),
                **({const.SCORPIO: saved_sc} if saved_sc is not None else {}),
            },
            "stronger_pairs": saved_pairs,
        })
def applicability(planet_positions):
    """Return True if Paryaaya Dasa's applicability condition is met."""
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lagna = p_to_h[const._ascendant_symbol]
    trines = house.trines_of_the_raasi(lagna)
    jupiter_in_trines = p_to_h[const.JUPITER_ID] in trines
    if jupiter_in_trines:
        return True
    mercury_in_trines = p_to_h[const.MERCURY_ID] in trines
    if mercury_in_trines:
        return True
    ak_in_trines = house.chara_karakas(planet_positions)[0] in trines
    if ak_in_trines:
        return True
    own_lord_in_trines = any([p_to_h[const.house_owners[h]] == h in trines for _, (h, _) in planet_positions])
    return own_lord_in_trines
def _direction_for_sr(planet_positions, sr):
    """Return the MD/antardasa direction (+1/-1) for starting sign sr."""
    direction = 1 if sr in const.odd_footed_signs else -1
    if planet_positions[const.SATURN_ID + 1][1][0] == sr:
        direction *= -1
    return direction
def _dhasa_lords(planet_positions, dhasa_seed, chara_seed_method=None):
    """Return (dhasa_type, md_lords) - dhasa_type: 1=Chara, 2=Ubhaya, 3=Sthira."""
    if chara_seed_method is None: chara_seed_method = const.paryaaya_chara_seed_method_default
    if dhasa_seed in const.dual_signs:  # Dual seed -> Chara Paryaaya
        dhasa_type = 1
        if chara_seed_method == 1:
            ts = house.trines_of_the_raasi(dhasa_seed)
            sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
            sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        else:
            sr = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_seed, (dhasa_seed + const.HOUSE_7) % 12)
        direction = _direction_for_sr(planet_positions, sr)
        dhasa_lords = [(sr + direction * (h-1)) % 12 for h in chara_paryaaya_list]
    elif dhasa_seed in const.movable_signs:  # Movable seed -> Ubhaya Paryaaya
        dhasa_type = 2
        ts = house.quadrants_of_the_raasi(dhasa_seed)
        sr = house.stronger_rasi_from_planet_positions(planet_positions, ts[0], ts[1])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[2])
        sr = house.stronger_rasi_from_planet_positions(planet_positions, sr, ts[3])
        direction = _direction_for_sr(planet_positions, sr)
        dhasa_lords = [(sr + direction * (h-1)) % 12 for h in ubhaya_paryaaya_list]
    else:  # Fixed seed -> Sthira Paryaaya
        dhasa_type = 3
        sr = house.stronger_rasi_from_planet_positions(planet_positions, dhasa_seed, (dhasa_seed + 6) % 12)
        direction = _direction_for_sr(planet_positions, sr)
        dhasa_lords = [(sr + direction * (h-1)) % 12 for h in sthira_paryaaya_list]
    return dhasa_type, dhasa_lords
def get_dhasa_antardhasa(
    dob, tob, place,
    divisional_chart_factor=None,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=2,
    use_tribhagi_variation=False,
    round_duration=False,
    chara_seed_method=None,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return (dhasa_type, rows) - dhasa/antardhasa periods, depth-enabled."""
    if divisional_chart_factor is None: divisional_chart_factor = _DEFAULT_VARGA
    if chara_seed_method is None: chara_seed_method = const.paryaaya_chara_seed_method_default
    lvl = int(dhasa_level_index)
    if not (1 <= lvl <= 6):
        raise ValueError("dhasa_level_index must be within [1..6].")
    cycles = 2
    scale = 1.0
    if use_tribhagi_variation:
        scale = 1.0 / 3.0
        cycles = int(cycles / scale)
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    asc_house = pp[0][1][0]
    dhasa_seed = (asc_house + divisional_chart_factor - 1) % 12
    dhasa_type, md_lords = _dhasa_lords(pp, dhasa_seed, chara_seed_method=chara_seed_method)
    rows = []
    start_jd = jd_at_dob
    def _append_row(labels, start_jd_val, seg_years):
        disp = round(seg_years, lvl + 1) if round_duration else seg_years
        rows.append((tuple(labels), utils.jd_to_gregorian(start_jd_val), float(disp)))
    def _recurse(level, parent_lord, pstart_jd, parent_years, parent_end_jd, prefix):
        child_seq = _narayana_antardhasa(pp, parent_lord)
        child_years = parent_years / 12.0
        child_bounds = _split_into_children(place, pstart_jd, parent_end_jd, parent_years, child_seq)
        if level + 1 == lvl:
            for c, (child_start_jd, _child_end_jd) in zip(child_seq, child_bounds):
                _append_row(prefix + (c,), child_start_jd, child_years)
            return parent_end_jd
        for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
            _recurse(level + 1, c, child_start_jd, child_years, child_end_jd, prefix + (c,))
        return parent_end_jd
    cycle1_years_by_lord = {}
    for cycle_idx in range(cycles):
        for md in md_lords:
            if cycle_idx == 0:
                md_years = float(_narayana_dhasa_duration(pp, md)) * scale
                cycle1_years_by_lord[md] = md_years
            else:
                md_years = max(0.0, 12.0 - cycle1_years_by_lord[md]) * scale
            md_end_jd = _bounded_end_jd(start_jd, place, md_years)
            if lvl == 1:
                _append_row((md,), start_jd, md_years)
            else:
                _recurse(1, md, start_jd, md_years, md_end_jd, (md,))
            start_jd = md_end_jd
    return dhasa_type, rows
def get_immediate_children(
    parent_lords, parent_start,
    parent_duration=None, parent_end=None,
    *,
    jd_at_dob, place,
    divisional_chart_factor: int = None,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    use_tribhagi_variation: bool = False,
    chara_seed_method: int = None,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return immediate (parent -> children) periods for a parent dasha."""
    if divisional_chart_factor is None: divisional_chart_factor = _DEFAULT_VARGA
    if chara_seed_method is None: chara_seed_method = const.paryaaya_chara_seed_method_default
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if isinstance(parent_lords, int):
        path = (int(parent_lords),)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(int(x) for x in parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    parent_lord = path[-1]
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)
    start_jd = _tuple_to_jd(parent_start)
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration (years) or parent_end (tuple)")
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, place, parent_years)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    child_seq = _narayana_antardhasa(pp, parent_lord)
    child_bounds = _split_into_children(place, start_jd, end_jd, parent_years, child_seq)
    children = []
    for c, (child_start_jd, child_end_jd) in zip(child_seq, child_bounds):
        if child_end_jd > child_start_jd:
            children.append((path + (c,), _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)))
    return children
def get_running_dhasa_for_given_date(
    current_jd, jd_at_dob, place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    divisional_chart_factor: int = None,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    use_tribhagi_variation: bool = False,
    chara_seed_method: int = None,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs
):
    """Return the running dhasa sequence for a given date."""
    if divisional_chart_factor is None: divisional_chart_factor = _DEFAULT_VARGA
    if chara_seed_method is None: chara_seed_method = const.paryaaya_chara_seed_method_default
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    def _norm(x):
        try:
            d = int(x)
        except Exception:
            d = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, d))
    target = _norm(dhasa_level_index)
    y0, m0, d0, fh0 = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y0, m0, d0)
    tob = (fh0, 0, 0)
    pp = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        years=years, months=months, sixty_hours=sixty_hours, **kwargs
    )[:const._pp_count_upto_ketu]
    asc_house = pp[0][1][0]
    dhasa_seed = (asc_house + divisional_chart_factor - 1) % 12
    _, md_lords = _dhasa_lords(pp, dhasa_seed, chara_seed_method=chara_seed_method)
    cycles = 2
    scale = 1.0
    if use_tribhagi_variation:
        scale = 1.0 / 3.0
        cycles = int(cycles / scale)
    md_entries = []
    cursor_jd = jd_at_dob
    cycle1_years_by_lord = {}
    for cycle_idx in range(cycles):
        for md in md_lords:
            if cycle_idx == 0:
                md_years = float(_narayana_dhasa_duration(pp, md)) * scale
                cycle1_years_by_lord[md] = md_years
            else:
                md_years = max(0.0, 12.0 - cycle1_years_by_lord[md]) * scale
            if md_years <= 0:
                continue
            md_end_jd = _bounded_end_jd(cursor_jd, place, md_years)
            md_entries.append((md, cursor_jd, md_end_jd, md_years))
            cursor_jd = md_end_jd
    located_entry = None
    for md, seg_start, seg_end, seg_years in md_entries:
        if seg_start <= current_jd < seg_end:
            located_entry = (md, seg_start, seg_end, seg_years)
            break
    if located_entry is None:
        located_entry = md_entries[-1]
    md_lord, md_start, md_end, md_years = located_entry
    ladder = [([md_lord], utils.julian_day_to_date_time_string(md_start),
               utils.julian_day_to_date_time_string(md_end))]
    if target == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return ladder
    parent_lords = [md_lord]
    parent_start_jd, parent_end_jd, parent_years = md_start, md_end, md_years
    parent_lord = md_lord
    for level in range(2, target + 1):
        child_seq = _narayana_antardhasa(pp, parent_lord)
        child_bounds = _split_into_children(place, parent_start_jd, parent_end_jd, parent_years, child_seq)
        child_years = parent_years / 12.0
        chosen = None
        for c, (c_start, c_end) in zip(child_seq, child_bounds):
            if c_start <= current_jd < c_end:
                chosen = (c, c_start, c_end)
                break
        if chosen is None:
            chosen = (child_seq[-1], child_bounds[-1][0], child_bounds[-1][1])
        child_rasi, child_start_jd, child_end_jd = chosen
        parent_lords = parent_lords + [child_rasi]
        ladder.append((parent_lords, utils.julian_day_to_date_time_string(child_start_jd),
                       utils.julian_day_to_date_time_string(child_end_jd)))
        parent_lord = child_rasi
        parent_start_jd, parent_end_jd, parent_years = child_start_jd, child_end_jd, child_years
    return ladder
if __name__ == "__main__":
    utils.set_language('en')
    CHART = "1996-12-07"  # "2004-06-25"
    if CHART == "1996-12-07":
        dob = drik.Date(1996, 12, 7)
        tob = (10, 34, 0)
    else:
        dob = drik.Date(2004, 6, 25)
        tob = (14, 47, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    y, m, d = (2010, 11, 9)
    hh, mm, ss = (15, 29, 45)
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
    DLI = const.MAHA_DHASA_DEPTH.DEHA
    # Chart-specific overrides (matching JHora's own dialog for THIS chart) -
    # required to match JHora exactly; never reuse for a different chart.
    if CHART == "1996-12-07":
        apply_jhora_dhasa_settings(
            default_varga=6,
            aquarius_owner=const.RAHU_ID,
            scorpio_owner=const.MARS_ID,
        )
    else:
        apply_jhora_dhasa_settings(
            default_varga=6,
            aquarius_owner=const.RAHU_ID,
            scorpio_owner=const.KETU_ID,
        )
    for dd in [const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR]:
        const.dhasa_year_duration_default = dd
        yd = drik.dhasa_year_duration(jd=jd_at_dob, place=place, dhasa_duration_type=dd)
        print(dd.name, dd.value, yd)
        print(f"\n--- MD-only table (D-6, both cycles) - {CHART} ---")
        dhasa_type, md_only_rows = get_dhasa_antardhasa(
            dob, tob, place, dhasa_level_index=1, dhasa_duration_type=dd,
        )
        print("dhasa_type:", dhasa_type, "(1=Chara, 2=Ubhaya, 3=Sthira)")
        for lords, start_tuple, dur_years in md_only_rows:
            lord_name = utils.RAASI_SHORT_LIST[lords[0]]
            y_, m_, d_, fh_ = start_tuple
            print(f"{lord_name:4s} start=({y_}-{m_}-{d_} {utils.to_dms(fh_)})  duration={dur_years:.4f} yrs")
        print(f"\n--- Running dasha chain (down to Deha) for {y}-{m}-{d} {hh}:{mm}:{ss} ---")
        start_time = time.time()
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
        )
        for lords, start_str, end_str in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:15s} {start_str}  ->  {end_str}")
        print('elapsed time', time.time() - start_time)
