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
Padanadhamsa Dasa.

Seed sign: the Navamsa sign occupied by the lord of the Rasi-chart Arudha Lagna.
(Dual lords - Scorpio/Aquarius - resolved by comparing the strength of the two
candidate Navamsa SIGNS, not the two planets.)

Three interchangeable methods (const.PADHANADHAMSA_TYPE):
  - PVR_JHORA:    Arudha Lagna via longitude method; dasha via Narayana Dasa engine.
  - SANJAY_RATH:  Arudha Lagna via classical book method; dasha via Narayana Dasa
                  engine run on the same varga chart used for the seed (generalizes
                  to any divisional_chart_factor, default D-9).
  - IRANGATTI_RANGACHARYA: same seed rule, own order/duration rules -
                  movable sign: step 1; fixed sign: step 6; dual sign: 1-5-9 trine
                  cycle; each direct if the dasa-sign is odd, reverse if even.
                  Duration: count dasa-sign to its lord (same odd/even direction
                  rule), with own-lord=12yr and 7th-lord=10yr overrides. Single
                  12-sign pass (Narayana Dasa uses two). Always uses D-9,
                  chart_method=4 (Krishna-Mishra/Nadi Navamsa).

References:
- Sanjay Rath, "Narayana Dasa" (Padanadhamsa chapter) - PVR_JHORA / SANJAY_RATH
- https://www.scribd.com/doc/274289709/aDasaPadanadhamsad-Hamsa - IRANGATTI_RANGACHARYA
- Yelluripati Krishna Rao, "Padanadhamsa Dasa - A Forgotten Dasa System"

Verification notes:
-  PVR_JHORA: This method requires owner overrides instead of default strength calculation:
    utils.set_owner_overrides_for_dhasa(overrides={
        "stronger_pairs": {
            (const.LEO, const.AQUARIUS): {"stronger": const.AQUARIUS}
        }
    })
Release History
----------------
    V5.0    
        - IRANGATTI_RANGACHARYA dual-sign order corrected (see _dhasa_progression).
        - PVR_JHORA/SANJAY_RATH running-dasha chain verified end-to-end against
           JHora using utils.set
"""
from jhora import const, utils
from jhora.horoscope.chart import charts, house, arudhas
from jhora.horoscope.dhasa.raasi import narayana
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
year_duration = const.sidereal_year
def _set_year_duration(jd, place, dhasa_duration_type=None, savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd, place=place,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
    )
    narayana._set_year_duration(jd, place, dhasa_duration_type, savana_year_method)
    return year_duration
def _arudha_lagna_sign(d1_positions):
    """Return the Arudha Lagna sign."""
    return arudhas.bhava_arudhas_from_planet_positions(d1_positions)[0]
def _padanadhamsa_seed_sign(jd_at_dob, place, divisional_chart_factor=9, chart_method=1,
                            dhasa_method=None,**kwargs):
    """Return (seed_sign, varga_planet_positions) for the requested method."""
    if dhasa_method is None: dhasa_method = const.PADHANADHAMSA_TYPE_DEFAULT
    d1_positions = charts.rasi_chart(jd_at_dob, place)[:const._pp_count_upto_ketu]
    if dhasa_method == const.PADHANADHAMSA_TYPE.PVR_JHORA:
        al_long = charts.get_chart_element_longitude(jd_at_dob,place,divisional_chart_factor=1,
                                                     dhasa_starting_planet="A1")
        al = drik.dasavarga_from_long(al_long)[0]
    else:
        al = arudhas.bhava_arudhas_from_planet_positions(d1_positions,arudha_base=0)[0]
    varga_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, **kwargs
    )[:const._pp_count_upto_ketu]
    p_to_h_varga = utils.get_planet_house_dictionary_from_planet_positions(varga_positions)
    al_lord = house.house_owner_from_planet_positions(d1_positions, al)
    lord_sign = p_to_h_varga[al_lord]
    seed = narayana._seed_from_candidate_sign(varga_positions, lord_sign)
    return seed, varga_positions
# =============================================================================
#   Method: IRANGATTI_RANGACHARYA - own order/duration rules, D-9 (KM/Nadi) only
# =============================================================================
def _dhasa_duration(planet_positions, dhasa_sign):
    """Return the Mahadasa duration (years) of dhasa_sign."""
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, dhasa_sign)
    house_of_lord = int(p_to_h[lord_of_sign]) % 12
    if house_of_lord == dhasa_sign:
        return 12
    if house_of_lord == (dhasa_sign + const.HOUSE_7) % 12:
        return 10
    direction = 1 if dhasa_sign in const.odd_signs else -1
    return utils.count_rasis(dhasa_sign, house_of_lord, direction=direction, total=12)
def _dhasa_progression(dhasa_lord):
    """Return the 12-sign dasa order starting from dhasa_lord."""
    direction = 1 if dhasa_lord in const.odd_signs else -1
    if dhasa_lord in const.fixed_signs:
        return [(dhasa_lord + direction * h * const.HOUSE_6) % 12 for h in range(12)]
    if dhasa_lord in const.movable_signs:
        return [(dhasa_lord + direction * h) % 12 for h in range(12)]
    frame = [1, 5, 9, 2, 6, 10, 3, 7, 11, 4, 8, 12]
    return [(dhasa_lord + direction * (h - 1)) % 12 for h in frame]
_IR_SUB_DAY_THRESHOLD_DAYS = narayana._SUB_DAY_THRESHOLD_DAYS
def _split_iranganti_children_jd(parent_sign, parent_start_jd, parent_end_jd, parent_years, place):
    """Return the 12 child periods of a parent dasha."""
    order = _dhasa_progression(parent_sign)
    parent_real_days = parent_end_jd - parent_start_jd
    base_years = parent_years / 12.0
    out = []
    jd_cursor = parent_start_jd
    for idx in range(12):
        child_sign = order[idx]
        child_years = (parent_years - base_years * 11.0) if idx == 11 else base_years
        if idx == 11:
            child_end_jd = parent_end_jd
        else:
            naive_days = child_years * year_duration
            if naive_days < _IR_SUB_DAY_THRESHOLD_DAYS:
                child_end_jd = parent_start_jd + parent_real_days * (idx + 1) / 12.0
            else:
                child_end_jd = narayana._bounded_end_jd(jd_cursor, place, child_years)
        out.append((child_sign, jd_cursor, child_end_jd, child_years))
        jd_cursor = child_end_jd
    return out
def _iranganti_whole_table(dob, tob, place, years=1, months=1, sixty_hours=1,
                            dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                            round_duration=True,
                            dhasa_duration_type=None, savana_year_method=None, **kwargs):
    """Return dhasa/antardhasa periods for the Rangacharya method."""
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    seed, d9_km_positions = _padanadhamsa_seed_sign(jd_at_dob, place, divisional_chart_factor=9,
                                                    chart_method=4,
                                                    dhasa_method=const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA)
    dhasa_start_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    md_order = _dhasa_progression(seed)
    prec = dhasa_level_index + 1
    do_round = round if round_duration else (lambda x, _: x)
    rows = []
    def _append_row(level_key, start_jd, years_len):
        rows.append((tuple(level_key), utils.jd_to_gregorian(start_jd), do_round(years_len, prec)))
    def _recurse(level, parent_sign, parent_start_jd, parent_end_jd, parent_years, prefix_list):
        children = _split_iranganti_children_jd(parent_sign, parent_start_jd, parent_end_jd, parent_years, place)
        if level < dhasa_level_index:
            for child_sign, child_start_jd, child_end_jd, child_years in children:
                prefix_list.append(child_sign)
                _recurse(level + 1, child_sign, child_start_jd, child_end_jd, child_years, prefix_list)
                prefix_list.pop()
        else:
            for child_sign, child_start_jd, child_end_jd, child_years in children:
                _append_row(prefix_list + [child_sign], child_start_jd, child_years)
    md_start_jd = dhasa_start_jd
    for md_sign in md_order:
        md_years = float(_dhasa_duration(d9_km_positions, md_sign))
        md_end_jd = narayana._bounded_end_jd(md_start_jd, place, md_years)
        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            rows.append((md_sign, utils.jd_to_gregorian(md_start_jd), do_round(md_years, prec)))
        else:
            _recurse(2, md_sign, md_start_jd, md_end_jd, md_years, [md_sign])
        md_start_jd = md_end_jd
    return rows
def _iranganti_immediate_children(parent_lords, parent_start, parent_duration=None, parent_end=None,
                                   *, place, round_duration=False,
                                   dhasa_duration_type=None, savana_year_method=None, jd_at_dob=None, **kwargs):
    """Return immediate child periods for a parent dasha."""
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
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = start_jd + parent_years * year_duration
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration
    if end_jd <= start_jd:
        return []
    children = _split_iranganti_children_jd(parent_sign, start_jd, end_jd, parent_years, place)
    return [
        [path + (child_sign,), _jd_to_tuple(child_start_jd), _jd_to_tuple(child_end_jd)]
        for child_sign, child_start_jd, child_end_jd, _child_years in children
    ]
def _iranganti_running(jd_given, jd_at_dob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                        years=1, months=1, sixty_hours=1,
                        dhasa_duration_type=None, savana_year_method=None, **kwargs):
    """Return the running dhasa sequence for a given date."""
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    seed, d9_km_positions = _padanadhamsa_seed_sign(jd_at_dob, place, divisional_chart_factor=9,
                                                    chart_method=4,
                                                    dhasa_method=const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA)
    epoch_jd = drik.next_solar_date(jd_at_dob, place, years=years, months=months, sixty_hours=sixty_hours)
    md_order = _dhasa_progression(seed)
    md_years_list = [float(_dhasa_duration(d9_km_positions, s)) for s in md_order]
    md_starts_jd = [epoch_jd]
    for y in md_years_list:
        md_starts_jd.append(narayana._bounded_end_jd(md_starts_jd[-1], place, y))
    from bisect import bisect_right
    i = bisect_right(md_starts_jd, jd_given) - 1
    i = max(0, min(i, len(md_order) - 1))
    md_sign = md_order[i]
    md_start, md_end, md_years = md_starts_jd[i], md_starts_jd[i + 1], md_years_list[i]
    jd_to_gregorian = utils.jd_to_gregorian
    out = [((md_sign,), jd_to_gregorian(md_start), jd_to_gregorian(md_end))]
    parent_sign, parent_start, parent_end, parent_years = md_sign, md_start, md_end, md_years
    for level in range(2, int(dhasa_level_index) + 1):
        children = _split_iranganti_children_jd(parent_sign, parent_start, parent_end, parent_years, place)
        chosen = children[-1]
        for child_sign, child_start_jd, child_end_jd, child_years in children:
            if jd_given < child_end_jd:
                chosen = (child_sign, child_start_jd, child_end_jd, child_years)
                break
        child_sign, child_start_jd, child_end_jd, child_years = chosen
        out.append((out[-1][0] + (child_sign,), jd_to_gregorian(child_start_jd), jd_to_gregorian(child_end_jd)))
        parent_sign, parent_start, parent_end, parent_years = child_sign, child_start_jd, child_end_jd, child_years
    return out
# =============================================================================
#   Public router - 3 methods (const.PADHANADHAMSA_TYPE)
# =============================================================================
def get_dhasa_antardhasa(dob, tob, place,
                          divisional_chart_factor=9, chart_method=1,
                          years=1, months=1, sixty_hours=1,
                          dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                          round_duration=True, dhasa_method=None,
                          dhasa_duration_type=None, savana_year_method=None,
                          **kwargs):
    """Return dhasa/antardhasa periods. dhasa_method: const.PADHANADHAMSA_TYPE.*"""
    if dhasa_method is None:
        dhasa_method = const.PADHANADHAMSA_TYPE_DEFAULT
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(jd_at_dob, place, dhasa_duration_type, savana_year_method)
    if dhasa_method == const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA:
        return _iranganti_whole_table(
            dob, tob, place, years=years, months=months, sixty_hours=sixty_hours,
            dhasa_level_index=dhasa_level_index, round_duration=round_duration,
            dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
            **kwargs
        )
    seed, varga_positions = _padanadhamsa_seed_sign(jd_at_dob, place, divisional_chart_factor,
                                                    chart_method=chart_method,
                                                    dhasa_method=dhasa_method,
                                                      **kwargs)
    return narayana._narayana_dhasa_calculation(
        varga_positions, seed, dob, tob, place,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_level_index=dhasa_level_index,
        varsha_narayana=False,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
        **kwargs
    )
def get_immediate_children(parent_lords, parent_start,
                                     parent_duration=None, parent_end=None,
                                     *, jd_at_dob, place,
                                     divisional_chart_factor=9, chart_method=1,
                                     round_duration=False, dhasa_method=None,
                                     dhasa_duration_type=None, savana_year_method=None,
                                     **kwargs):
    """Return immediate child periods for a parent dasha."""
    if dhasa_method is None:
        dhasa_method = const.PADHANADHAMSA_TYPE_DEFAULT
    if dhasa_method == const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA:
        return _iranganti_immediate_children(
            parent_lords, parent_start, parent_duration=parent_duration, parent_end=parent_end,
            jd_at_dob=jd_at_dob, place=place, round_duration=round_duration,
            dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
            **kwargs
        )
    return narayana.get_immediate_children(
        parent_lords, parent_start, parent_duration=parent_duration, parent_end=parent_end,
        jd_at_dob=jd_at_dob, place=place,
        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
        round_duration=round_duration,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
        **kwargs
    )
def get_running_dhasa_for_given_date(jd_given, jd_at_dob, place,
                                       divisional_chart_factor=9, chart_method=1,
                                       dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                                       years=1, months=1, sixty_hours=1,
                                       dhasa_method=None,
                                       dhasa_duration_type=None, savana_year_method=None,
                                       **kwargs):
    """Return the running dhasa sequence for a given date."""
    if dhasa_method is None:
        dhasa_method = const.PADHANADHAMSA_TYPE_DEFAULT
    if dhasa_method == const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA:
        return _iranganti_running(
            jd_given, jd_at_dob, place, dhasa_level_index=dhasa_level_index,
            years=years, months=months, sixty_hours=sixty_hours,
            dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
            **kwargs
        )
    seed, _varga_positions = _padanadhamsa_seed_sign(jd_at_dob, place, divisional_chart_factor,
                                                     chart_method=chart_method,
                                                      dhasa_method=dhasa_method, **kwargs)
    return narayana.get_running_dhasa_for_given_date(
        jd_given, jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
        dhasa_level_index=dhasa_level_index,
        years=years, months=months, sixty_hours=sixty_hours,
        dhasa_duration_type=dhasa_duration_type, savana_year_method=savana_year_method,
        dhasa_seed_sign_override=seed,
        **kwargs
    )


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    dob = drik.Date(2004, 6,25)
    dob = drik.Date(1946,8,19)
    tob = (10, 34, 0)
    tob = (14, 47, 0)
    tob = (3,44,0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    place = drik.Place('Bill Clinton', 33.+40/60, -93-35/60, -6.0)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR
    """ 
        This override is requireed to match JHora for above chart data 1996,12,7
        Comment this for Other methods
        for Sanjay Rath method enable
            const.aquarius_owner_for_dhasa_calculations = const.RAHU_ID
    """
    """
    utils.set_owner_overrides_for_dhasa(overrides={
        "stronger_pairs": {
            (const.LEO, const.AQUARIUS): {"stronger": const.AQUARIUS}
        }
    })
    """
    const.aquarius_owner_for_dhasa_calculations = const.RAHU_ID
    """
    db = get_dhasa_antardhasa(dob, tob, place,
                    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
                    dhasa_method=const.PADHANADHAMSA_TYPE.PVR_JHORA)
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
    exit()
    """
    for method_name, method in (("SANJAY_RATH", const.PADHANADHAMSA_TYPE.SANJAY_RATH),
                                ("PVR_JHORA",const.PADHANADHAMSA_TYPE.PVR_JHORA),
                                 ("IRANGATTI_RANGACHARYA", const.PADHANADHAMSA_TYPE.IRANGATTI_RANGACHARYA)):
        print("=" * 70)
        print(method_name, "- Maha Dasas")
        print("=" * 70)
        db_maha = get_dhasa_antardhasa(dob, tob, place,
                        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
                        dhasa_method=method)
        for lord, start_date, durn in db_maha:
            y, m, d, fh = start_date
            print(utils.RAASI_SHORT_LIST[lord], f"{y}-{m:02d}-{d:02d}", utils.to_dms(fh), durn)

        y, m, d = (1998, 11, 9)
        hh, mm, ss = (15, 29, 45)
        print("\n", method_name, f"- running dasha chain for ({y}-{m}-{d} {hh}:{mm}:{ss})")
        current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
        grd = get_running_dhasa_for_given_date(
            current_jd, jd_at_dob, place,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_duration_type=const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR,
            dhasa_method=method,
        )
        for lords, (y1, m1, d1, fh1), (y2, m2, d2, fh2) in grd:
            label = '-'.join(utils.RAASI_SHORT_LIST[l] for l in lords)
            print(f"{label:20s} {y1}-{m1:02d}-{d1:02d} {utils.to_dms(fh1)}  ->  {y2}-{m2:02d}-{d2:02d} {utils.to_dms(fh2)}")
        print()
