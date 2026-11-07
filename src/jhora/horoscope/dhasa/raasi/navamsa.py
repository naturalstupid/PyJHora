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
    Navamsa Dasa: 
    V5.0  Refactored to Match JHora results
    4 methods:
    1. Sanjay Rath / PV Narasimha Rao / JHora (all levels match)
    2. Irangatti Rangacharya
    3. Suresh Mishra
    4. P.S. Sastri
    Ref: https://shubhamalock.wordpress.com/2016/09/20/navamsa-dasa-part-1/
"""

from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts


year_duration = const.sidereal_year
ONE_NAVAMSA = 30.0 / 9.0
NAVAMSA_DASA_YEARS = 9.0
NAVAMSA_CYCLE_YEARS = 108.0
MALE, FEMALE = 0, 1
_SUB_DAY_THRESHOLD_DAYS = 1.0
_BACKSTOP_DAYS = 30.0

_ODD_SIGNS = {0, 2, 4, 6, 8, 10}
_EVEN_SIGNS = {1, 3, 5, 7, 9, 11}
_MOVABLE_SIGNS = {0, 3, 6, 9}
_FIXED_SIGNS = {1, 4, 7, 10}
_DUAL_SIGNS = {2, 5, 8, 11}

##E Ref: https://www.scribd.com/document/590034766/Navansha-Dasha-Jaimini
### Not used yet in this
JAIMINI_ADARSA_MAP = {const.ARIES:const.ARIES,const.TAURUS:const.LEO,const.GEMINI:const.LIBRA,
                      const.CANCER:const.AQUARIUS,const.LEO:const.ARIES,const.VIRGO:const.LEO,
                      const.LIBRA:const.LIBRA,const.SCORPIO:const.AQUARIUS,
                      const.SAGITTARIUS:const.ARIES,const.CAPRICORN:const.LEO,
                      const.AQUARIUS:const.LIBRA,const.PISCES:const.AQUARIUS}

SR_ADARSA_MAP = {
    0: 7,   # Aries -> Scorpio
    1: 6,   # Taurus -> Libra
    2: 5,   # Gemini -> Virgo
    3: 10,  # Cancer -> Aquarius (special)
    4: 9,   # Leo -> Capricorn (special)
    5: 2,   # Virgo -> Gemini
    6: 1,   # Libra -> Taurus
    7: 0,   # Scorpio -> Aries
    8: 11,  # Sagittarius -> Pisces
    9: 10,  # Capricorn -> Aquarius (other Saturn sign)
    10: 9,  # Aquarius -> Capricorn (other Saturn sign)
    11: 8,  # Pisces -> Sagittarius
}
PS_ADARSA_MAP = {
    0: 0, 1: 11, 2: 10, 3: 9, 4: 8, 5: 7,
    6: 6, 7: 5, 8: 4, 9: 3, 10: 2, 11: 1,
}
CLASSICAL_SIGN_LORDS = {
    0: 2, 1: 5, 2: 3, 3: 1, 4: 0, 5: 3,
    6: 5, 7: 2, 8: 4, 9: 6, 10: 6, 11: 4,
}


def _set_year_duration(jd, place, dhasa_duration_type=None,
                       savana_year_method=None):
    global year_duration
    year_duration = drik.dhasa_year_duration(
        jd=jd, place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    return year_duration


def _bounded_end_jd(start_jd, place, years, backstop_days=_BACKSTOP_DAYS):
    years = float(years)
    naive_end = start_jd + years * year_duration
    try:
        real_end = drik._get_dhasa_end_jd(start_jd, place, years)
    except Exception:
        return naive_end
    if real_end is None or real_end <= start_jd:
        return naive_end
    if abs(real_end - naive_end) > float(backstop_days):
        return naive_end
    return real_end


def _is_odd(sign):
    return int(sign) in _ODD_SIGNS


def _sequence(seed, direction=1):
    return [(int(seed) + direction * i) % 12 for i in range(12)]


def _rath_odd_member(sign):
    sign = int(sign)
    return sign if sign in _ODD_SIGNS else SR_ADARSA_MAP[sign]


def _rath_even_member(sign):
    sign = int(sign)
    return sign if sign in _EVEN_SIGNS else SR_ADARSA_MAP[sign]


def _ps_seed(sign):
    sign = int(sign)
    return sign if sign in _ODD_SIGNS else PS_ADARSA_MAP[sign]


def _method_is(method, *names):
    for name in names:
        value = getattr(const.NAVAMSA_METHOD, name, None)
        if value is not None and method == value:
            return True
    return False


def _is_rath_method(method):
    return (
        _method_is(method, "SANJAY_RATH_PVR_JHORA")
        or not any((
            _method_is(method, "SURESH_CHANDRA_MISHRA"),
            _method_is(method, "IRANGATTI_RANGACHARYA",
                       "IRANGANTI_RANGACHARYA"),
            _method_is(method, "PS_SASTRI"),
        ))
    )


def _validate_mapping(p_to_h):
    if const._ascendant_symbol not in p_to_h:
        raise KeyError("Ascendant missing from planet-house mapping")
    missing = [p for p in range(7) if p not in p_to_h]
    if missing:
        raise KeyError("Missing classical planets: %r" % missing)


def _other_md_order(method, d9_p_to_h, gender):
    asc = int(d9_p_to_h[const._ascendant_symbol])
    if _method_is(method, "SURESH_CHANDRA_MISHRA"):
        return _sequence(asc, 1 if _is_odd(asc) else -1)
    if _method_is(method, "IRANGATTI_RANGACHARYA",
                  "IRANGANTI_RANGACHARYA"):
        if gender == MALE:
            return _sequence(_rath_odd_member(asc), 1)
        if gender == FEMALE:
            return _sequence(_rath_even_member(asc), -1)
        raise ValueError("gender must be 0 (male) or 1 (female)")
    seed = _ps_seed(asc)
    return _sequence(seed, 1 if _is_odd(seed) else -1)


def _other_child_order(method, parent_sign, d9_p_to_h, gender):
    parent_sign = int(parent_sign)
    if _method_is(method, "SURESH_CHANDRA_MISHRA"):
        return _sequence(parent_sign, 1 if _is_odd(parent_sign) else -1)
    lord_d9 = int(d9_p_to_h[CLASSICAL_SIGN_LORDS[parent_sign]])
    if _method_is(method, "IRANGATTI_RANGACHARYA",
                  "IRANGANTI_RANGACHARYA"):
        if gender == MALE:
            return _sequence(_rath_odd_member(lord_d9), 1)
        if gender == FEMALE:
            return _sequence(_rath_even_member(lord_d9), -1)
        raise ValueError("gender must be 0 (male) or 1 (female)")
    seed = _ps_seed(lord_d9)
    return _sequence(seed, 1 if _is_odd(seed) else -1)


def _sanjay_rath_child_order(parent_sign):
    """JHora/Sanjay Navamsa subperiod order, freshly applied at every level.

    Validated against the supplied complete MD>AD table and the running
    Pi-Ge-Ge-Le-Ta chain:
      movable + odd  -> Libra seed
      movable + even -> Aquarius seed
      fixed   + odd  -> Leo seed
      fixed   + even -> Aries seed
      dual            -> Sagittarius seed
    All child orders are zodiacal from the selected seed.
    """
    parent_sign = int(parent_sign)
    if parent_sign in _MOVABLE_SIGNS:
        seed = 6 if parent_sign in _ODD_SIGNS else 10
    elif parent_sign in _FIXED_SIGNS:
        seed = 4 if parent_sign in _ODD_SIGNS else 0
    else:
        seed = 8
    return _sequence(seed, 1)


def _get_context(jd_at_dob, place, divisional_chart_factor, chart_method,
                 dhasa_method, gender=MALE, years=1, months=1,
                 sixty_hours=1, **kwargs):
    rasi_positions = charts.divisional_chart(
        jd_at_dob, place, divisional_chart_factor=1,
        chart_method=chart_method, years=years, months=months,
        sixty_hours=sixty_hours, **kwargs
    )
    d9_positions = charts.divisional_chart(
        jd_at_dob, place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method, years=years, months=months,
        sixty_hours=sixty_hours, **kwargs
    )
    rasi_map = utils.get_planet_house_dictionary_from_planet_positions(
        rasi_positions
    )
    d9_map = utils.get_planet_house_dictionary_from_planet_positions(d9_positions)
    _validate_mapping(rasi_map)
    _validate_mapping(d9_map)

    if _is_rath_method(dhasa_method):
        # JHora/Sanjay: Rasi Lagna if odd; directional Rath Adarsa if even.
        rasi_lagna = int(rasi_map[const._ascendant_symbol])
        md_order = _sequence(_rath_odd_member(rasi_lagna), 1)

        def child_order_fn(parent_sign):
            # Fresh modality/parity rule at AD, PD, SD, PAD, and Deha.
            return _sanjay_rath_child_order(parent_sign)
    else:
        md_order = _other_md_order(dhasa_method, d9_map, gender)

        def child_order_fn(parent_sign):
            return _other_child_order(
                dhasa_method, parent_sign, d9_map, gender
            )

    return rasi_positions, d9_positions, md_order, child_order_fn


def _fraction_elapsed(jd, place, divisional_chart_factor=1, chart_method=1,
                      star_position_from_moon=1, dhasa_starting_planet=1):
    longitude = charts.get_chart_element_longitude(
        jd=jd, place=place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )
    return (float(longitude) % ONE_NAVAMSA) / ONE_NAVAMSA


def _initial_md_start(jd, place, dhasa_method,
                      balance_divisional_chart_factor=1, chart_method=1,
                      star_position_from_moon=1, dhasa_starting_planet=1):
    # JHora Sanjay-Rath Navamsa starts exactly at birth; no Moon balance.
    if _is_rath_method(dhasa_method):
        return jd
    fraction = _fraction_elapsed(
        jd, place,
        divisional_chart_factor=balance_divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )
    return drik._get_dhasa_start_jd(
        jd, place, fraction_elapsed=fraction,
        total_dasa_years=NAVAMSA_DASA_YEARS,
    )


def navamsa_dasha_start_date(
    jd, place, divisional_chart_factor=9, chart_method=1,
    star_position_from_moon=1, seed_star=3, dhasa_starting_planet=1,
    dhasa_method=None, gender=MALE, balance_divisional_chart_factor=1,
    years=1, months=1, sixty_hours=1, **kwargs
):
    del seed_star
    if dhasa_method is None:
        dhasa_method = const.navamsa_dasa_method_default
    _rasi, _d9, order, _child_fn = _get_context(
        jd, place, divisional_chart_factor, chart_method, dhasa_method,
        gender, years, months, sixty_hours, **kwargs
    )
    start_jd = _initial_md_start(
        jd, place, dhasa_method, balance_divisional_chart_factor,
        chart_method, star_position_from_moon, dhasa_starting_planet,
    )
    return [order[0], start_jd]


def _split_parent_into_children_jd(parent_sign, parent_start_jd,
                                   parent_end_jd, parent_years,
                                   order_fn, place):
    order = list(order_fn(parent_sign))
    if len(order) != 12:
        raise ValueError("Child order must contain exactly 12 signs")
    parent_years = float(parent_years)
    parent_days = parent_end_jd - parent_start_jd
    child_years = parent_years / 12.0
    result, cursor = [], parent_start_jd

    for index, child_sign in enumerate(order):
        nominal_years = (
            parent_years - child_years * 11.0 if index == 11
            else child_years
        )
        if index == 11:
            end_jd = parent_end_jd
        elif nominal_years * year_duration < _SUB_DAY_THRESHOLD_DAYS:
            end_jd = parent_start_jd + parent_days * (index + 1) / 12.0
        else:
            end_jd = _bounded_end_jd(cursor, place, nominal_years)
            if end_jd <= cursor or end_jd >= parent_end_jd:
                end_jd = parent_start_jd + parent_days * (index + 1) / 12.0
        result.append((int(child_sign), cursor, end_jd, nominal_years))
        cursor = end_jd

    # Exact last-child clamp.
    sign, start, _end, years_len = result[-1]
    result[-1] = (sign, start, parent_end_jd, years_len)
    return result


def _recursive_rows(current_level, target_level, parent_sign,
                    parent_start_jd, parent_end_jd, parent_years,
                    prefix, order_fn, place):
    rows = []
    children = _split_parent_into_children_jd(
        parent_sign, parent_start_jd, parent_end_jd,
        parent_years, order_fn, place,
    )
    child_level = int(current_level) + 1
    for sign, start, end, years_len in children:
        path = tuple(prefix) + (sign,)
        if child_level == int(target_level):
            rows.append((path, start, end, years_len))
        else:
            rows.extend(_recursive_rows(
                child_level, target_level, sign, start, end,
                years_len, path, order_fn, place,
            ))
    return rows


def _depth(depth):
    depth = int(depth)
    if not 1 <= depth <= 6:
        raise ValueError("dhasa_level_index must be 1..6")
    return depth


def get_dhasa_antardhasa(
    dob, tob, place, divisional_chart_factor=9, chart_method=1,
    star_position_from_moon=1, seed_star=3, dhasa_starting_planet=1,
    balance_divisional_chart_factor=1, years=1, months=1,
    sixty_hours=1, dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True, dhasa_method=None, gender=MALE,
    dhasa_duration_type=None, savana_year_method=None, **kwargs
):
    del seed_star
    if dhasa_method is None:
        dhasa_method = const.navamsa_dasa_method_default
    target = _depth(dhasa_level_index)
    jd_at_dob = utils.julian_day_number(dob, tob)
    _set_year_duration(
        jd_at_dob, place, dhasa_duration_type, savana_year_method
    )
    _rasi, _d9, md_order, child_fn = _get_context(
        jd_at_dob, place, divisional_chart_factor, chart_method,
        dhasa_method, gender, years, months, sixty_hours, **kwargs
    )
    md_start = _initial_md_start(
        jd_at_dob, place, dhasa_method,
        balance_divisional_chart_factor, chart_method,
        star_position_from_moon, dhasa_starting_planet,
    )

    raw = []
    for md_sign in md_order:
        md_end = _bounded_end_jd(
            md_start, place, NAVAMSA_DASA_YEARS
        )
        if target == 1:
            raw.append(((md_sign,), md_start, md_end, NAVAMSA_DASA_YEARS))
        else:
            raw.extend(_recursive_rows(
                1, target, md_sign, md_start, md_end,
                NAVAMSA_DASA_YEARS, (md_sign,), child_fn, place,
            ))
        md_start = md_end

    precision = target + 1
    return [
        (
            tuple(path),
            utils.jd_to_gregorian(start),
            float(round(duration, precision) if round_duration else duration),
        )
        for path, start, _end, duration in raw
    ]


def _fh_to_hms(fh):
    hours = int(fh)
    minutes_float = (float(fh) - hours) * 60.0
    minutes = int(minutes_float)
    seconds = int(round((minutes_float - minutes) * 60.0))
    if seconds >= 60:
        seconds -= 60
        minutes += 1
    if minutes >= 60:
        minutes -= 60
        hours += 1
    return hours, minutes, seconds


def _tuple_to_jd(value):
    y, m, d, fh = value
    return utils.julian_day_number(
        drik.Date(int(y), int(m), int(d)), _fh_to_hms(fh)
    )


def get_immediate_children(
    parent_lords, parent_start, parent_duration=None, parent_end=None,
    *, jd_at_dob, place, divisional_chart_factor=9, chart_method=1,
    years=1, months=1, sixty_hours=1, dhasa_method=None,
    gender=MALE, dhasa_duration_type=None, savana_year_method=None,
    **kwargs
):
    if dhasa_method is None:
        dhasa_method = const.navamsa_dasa_method_default
    _set_year_duration(
        jd_at_dob, place, dhasa_duration_type, savana_year_method
    )
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (tuple, list)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list")
    if (parent_duration is None) == (parent_end is None):
        raise ValueError("Provide exactly one of parent_duration or parent_end")

    start_jd = _tuple_to_jd(parent_start)
    if parent_end is None:
        parent_years = float(parent_duration)
        end_jd = _bounded_end_jd(start_jd, place, parent_years)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    _rasi, _d9, _md_order, child_fn = _get_context(
        jd_at_dob, place, divisional_chart_factor, chart_method,
        dhasa_method, gender, years, months, sixty_hours, **kwargs
    )
    children = _split_parent_into_children_jd(
        path[-1], start_jd, end_jd, parent_years, child_fn, place
    )
    return [
        [path + (sign,), utils.jd_to_gregorian(start),
         utils.jd_to_gregorian(end)]
        for sign, start, end, _duration in children
    ]


immediate_children = get_immediate_children


def get_running_dhasa_for_given_date(
    jd_given, jd_at_dob, place, divisional_chart_factor=9,
    chart_method=1, star_position_from_moon=1, seed_star=3,
    dhasa_starting_planet=1, balance_divisional_chart_factor=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA, years=1,
    months=1, sixty_hours=1, dhasa_method=None, gender=MALE,
    dhasa_duration_type=None, savana_year_method=None, **kwargs
):
    del seed_star
    if dhasa_method is None:
        dhasa_method = const.navamsa_dasa_method_default
    target = _depth(dhasa_level_index)
    _set_year_duration(
        jd_at_dob, place, dhasa_duration_type, savana_year_method
    )
    _rasi, _d9, md_order, child_fn = _get_context(
        jd_at_dob, place, divisional_chart_factor, chart_method,
        dhasa_method, gender, years, months, sixty_hours, **kwargs
    )
    epoch = _initial_md_start(
        jd_at_dob, place, dhasa_method,
        balance_divisional_chart_factor, chart_method,
        star_position_from_moon, dhasa_starting_planet,
    )

    # Extend cyclically until the requested moment is covered.
    while jd_given < epoch:
        epoch -= NAVAMSA_CYCLE_YEARS * year_duration
    cursor, selected = epoch, None
    for _cycle in range(30):
        for sign in md_order:
            end = _bounded_end_jd(cursor, place, NAVAMSA_DASA_YEARS)
            if cursor <= jd_given < end:
                selected = (sign, cursor, end, NAVAMSA_DASA_YEARS)
                break
            cursor = end
        if selected is not None:
            break
    if selected is None:
        raise RuntimeError("Unable to locate running Navamsa Mahadasa")

    sign, start, end, years_len = selected
    path = (sign,)
    result = [(path, utils.jd_to_gregorian(start), utils.jd_to_gregorian(end))]

    for _level in range(2, target + 1):
        children = _split_parent_into_children_jd(
            sign, start, end, years_len, child_fn, place
        )
        chosen = children[-1]
        for child in children:
            if child[1] <= jd_given < child[2]:
                chosen = child
                break
        sign, start, end, years_len = chosen
        path = path + (sign,)
        result.append(
            (path, utils.jd_to_gregorian(start), utils.jd_to_gregorian(end))
        )
    return result


if __name__ == "__main__":
    utils.set_language("en")
    dob = drik.Date(1944,8,20) # JHora/ Misra/Irangatti/Sastri Example
    tob = (7,11,0) # Misra/Irangatti/Sastri Example
    place = drik.Place("Mumbai,IN", 18+58/60,72+49/60, +5.5) ## Misra/Irangatti/Sastri Example
    jd = utils.julian_day_number(dob, tob)
    query_jd = utils.julian_day_number(
        drik.Date(1998, 11, 9), (15, 29, 45)
    )
    for method in const.NAVAMSA_METHOD:
        print("=====================================")
        print("METHOD:",method.name)
        print("=====================================")
        ad_rows = get_dhasa_antardhasa(
            dob, tob, place, divisional_chart_factor=9,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
            dhasa_method=method,
        )
        grouped = {}
        for lords, _date, _duration in ad_rows:
            grouped.setdefault(lords[0], []).append(lords[1])
        for md, ads in grouped.items():
            print(utils.RAASI_SHORT_LIST[md], ">",
                ",".join(utils.RAASI_SHORT_LIST[x] for x in ads))

        print("Running chain:")
        for lords, start, end in get_running_dhasa_for_given_date(
            query_jd, jd, place, divisional_chart_factor=9,
            dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
            dhasa_method=method,
        ):
            start_date = f"{start[0]}-{start[1]}-{start[2]} {utils.to_dms(start[3])}"
            end_date = f"{end[0]}-{end[1]}-{end[2]} {utils.to_dms(end[3])}"
            print("-".join(utils.RAASI_SHORT_LIST[x] for x in lords),
                start_date, "->", end_date)
