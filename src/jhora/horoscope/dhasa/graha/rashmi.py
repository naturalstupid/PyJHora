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
Rashmi Dasa
Ref: https://astrosutras.in/index.php/2025/03/05/rashmi-dasha-as-per-brihat-parashara-hora-shastra-bphs/
For each of the 7 grahas Sun..Saturn (no Rahu/Ketu), a ray strength is
computed: base rays = (angular distance from the planet's own deepest-
debilitation point / 180) * that planet's MAX_RAYS constant; then
multiplied by 2x if exalted, multiplied by 2x if vargottama (same sign
in D1 and D9), multiplied by 4/3x if in its own sign, and multiplied by
0.5x if combust (within the Sun's combustion range).

Sequence order (dhasa_method): BPHS_HIGHEST_RAY orders planets by
descending ray strength; NATURAL_ORDER uses the fixed Sun..Saturn order;
VIMSOTTARI_ORDER uses a Vimsottari-style nakshatra-seeded cyclic order
based on the Moon's own nakshatra, with a balance_factor (birth-fraction
adjustment) applied only to the very first Mahadasa's first occurrence.

Duration: each Mahadasa's own length is that planet's own ray value
directly, in years. Every level below Mahadasa splits proportionally by
ray-share: child_years = parent_years * (child's own ray / total_rays).

Cycling: the fixed (order, rays, total_rays) list, computed once from
the birth/progressed chart, is repeated as many times as needed until
the cumulative duration across all cycles reaches TARGET_SPAN
(const.human_life_span_for_vimsottari_dhasa, 120 years), capped at
max_cycles.
"""
from jhora import const, utils
from jhora.horoscope.chart import charts
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy

MAX_RAYS = {0: 10, 1: 9, 2: 5, 3: 5, 4: 7, 5: 16, 6: 4}
year_duration = const.sidereal_year

vimsottari_adhipati = (
    lambda nak, seed_star=3: const.vimsottari_adhipati_list[
        (nak - seed_star + 3) % (len(const.vimsottari_adhipati_list))
    ]
)

_SMALL_DURATION_BACKSTOP_DAYS = 30.0
_SUB_DAY_DURATION_DAYS = 1.0


def vimsottari_next_adhipati(lord, direction=1):
    """Returns next guy after `lord` in the adhipati_list"""
    current = const.vimsottari_adhipati_list.index(lord)
    next_index = (current + direction) % len(const.vimsottari_adhipati_list)
    return const.vimsottari_adhipati_list[next_index]


def _bounded_end_jd(start_jd_local, duration_years, place):
    """ Real dasa-period end JD, guarded by a naive average-year backstop. """
    end_jd = drik._get_dhasa_end_jd(
        start_jd=start_jd_local,
        place=place,
        total_dasa_years=duration_years,
    )

    expected_jd = start_jd_local + duration_years * year_duration

    if abs(end_jd - expected_jd) > _SMALL_DURATION_BACKSTOP_DAYS:
        return expected_jd

    return end_jd


def _rashmi_order_rays_and_balance(
    jd_start,
    place,
    *,
    divisional_chart_factor=1,
    chart_method=1,
    navamsa_chart_method=1,
    dhasa_method=None,
    vimsottari_method_seed_star=3,
    use_real_combusion_limits=True,
):
    """
    Computes each of the 7 grahas' (Sun..Saturn) ray strength, the total
    rays, the Mahadasa order for dhasa_method, and the first-Mahadasa
    balance_factor (only non-1.0 for VIMSOTTARI_ORDER).

    Returns (planet_rays, total_rays, order, balance_factor).
    """
    if dhasa_method is None:
        dhasa_method = const.RASHMI_TYPE_DEFAULT

    MAX_RAYS_LOCAL = {0: 10, 1: 9, 2: 5, 3: 5, 4: 7, 5: 16, 6: 4}
    DEEP_EXALT = {0: 10, 1: 33, 2: 298, 3: 165, 4: 95, 5: 357, 6: 200}
    EXALT_SIGNS = {0: 0, 1: 1, 2: 9, 3: 5, 4: 3, 5: 11, 6: 6}
    OWNERS = {0: 2, 1: 5, 2: 3, 3: 1, 4: 0, 5: 3, 6: 5, 7: 2, 8: 4, 9: 6, 10: 6, 11: 4}
    VIM_LIST = const.vimsottari_adhipati_list

    d1_pos = charts.divisional_chart(
        jd_start,
        place,
        divisional_chart_factor,
        chart_method=chart_method,
    )
    d9_pos = charts.divisional_chart(
        jd_start,
        place,
        9,
        chart_method=navamsa_chart_method,
    )

    sun_z, sun_l = next(pos for p_id, pos in d1_pos if p_id == 0)
    sun_abs_lon = (sun_z * 30) + sun_l
    retro_planets = drik.planets_in_retrograde(jd_start, place)

    planet_rays = {}

    for p_id, (zod, lon) in d1_pos[const.SUN_ID + 1:const._pp_count_upto_saturn]:  # Sun to Saturn
        idx = p_id - 1

        if use_real_combusion_limits:
            combusion_limit = (
                const.combustion_range_of_planets_from_sun_while_in_retrogade[idx]
                if p_id in retro_planets
                else const.combustion_range_of_planets_from_sun[idx]
            )
        else:
            combusion_limit = 8.0

        abs_lon = (zod * 30) + lon
        deb_lon = (DEEP_EXALT[p_id] + 180) % 360
        dist = abs(abs_lon - deb_lon)

        if dist > 180:
            dist = 360 - dist

        rays = (dist / 180.0) * MAX_RAYS_LOCAL[p_id]

        d9_zod = next(z for pid, (z, l) in d9_pos if pid == p_id)

        if zod == EXALT_SIGNS[p_id]:
            rays *= 2.0

        if zod == d9_zod:
            rays *= 2.0
        elif p_id == OWNERS.get(zod):
            rays *= (4.0 / 3.0)

        if p_id != 0 and abs(abs_lon - sun_abs_lon) < combusion_limit:
            rays *= 0.5

        planet_rays[p_id] = round(rays, 8)

    total_rays = sum(planet_rays.values())

    balance_factor = 1.0

    if dhasa_method == const.RASHMI_TYPE.BPHS_HIGHEST_RAY:
        order = sorted(planet_rays.keys(), key=lambda x: planet_rays[x], reverse=True)
    elif dhasa_method == const.RASHMI_TYPE.NATURAL_ORDER:
        order = list(const.SUN_TO_SATURN)
    elif dhasa_method == const.RASHMI_TYPE.VIMSOTTARI_ORDER:
        moon_z, moon_l = next(pos for p_id, pos in d1_pos if p_id == 1)
        moon_abs_lon = (moon_z * 30) + moon_l
        nak_val = moon_abs_lon / (360.0 / 27.0)
        start_lord = VIM_LIST[(int(nak_val) - vimsottari_method_seed_star + 3) % len(VIM_LIST)]
        order = [start_lord]

        for _ in range(len(VIM_LIST) - 1):
            order.append(vimsottari_next_adhipati(order[-1]))

        order = [p for p in order if p in planet_rays and planet_rays[p] > 0]
        balance_factor = 1.0 - (nak_val - int(nak_val))
    else:
        order = sorted(planet_rays.keys(), key=lambda x: planet_rays[x], reverse=True)

    return planet_rays, total_rays, order, balance_factor


def _get_rashmi_children_jd(
    parent_path,
    parent_start_jd,
    parent_duration,
    place,
    order,
    planet_rays,
    total_rays,
    *,
    parent_end_jd=None,
):
    """
    Returns the children of parent_path under the given order/planet_rays
    for one level below Mahadasa: each child's share of parent_duration is
    (child's own ray / total_rays). Children with zero or negative
    ray-share duration are skipped. The last (non-skipped) child's end is
    forced to parent_end_jd exactly.

    Returns:
        children: list of
            (child_path_tuple, child_start_jd, child_duration_years, child_end_jd)
        parent_end_jd: float JD
    """
    if parent_end_jd is None:
        parent_end_jd = _bounded_end_jd(parent_start_jd, parent_duration, place)

    if parent_end_jd <= parent_start_jd or total_rays <= 0 or not order:
        return [], parent_end_jd

    raw_shares = []

    for p_id in order:
        ray = planet_rays.get(p_id, 0)
        share = ray / total_rays
        child_duration = parent_duration * share

        if child_duration > 0:
            raw_shares.append((p_id, child_duration))

    n = len(raw_shares)

    if n == 0:
        return [], parent_end_jd

    smallest_child_years = min(cd for _p, cd in raw_shares)
    smallest_child_days = smallest_child_years * year_duration
    use_proportional_interpolation = smallest_child_days < _SUB_DAY_DURATION_DAYS
    parent_span = parent_end_jd - parent_start_jd
    total_included_duration = sum(cd for _p, cd in raw_shares)

    children = []
    cursor = parent_start_jd
    cumulative_duration = 0.0

    for i, (p_id, child_duration) in enumerate(raw_shares):
        child_start_jd = cursor

        if i == n - 1:
            child_end_jd = parent_end_jd
        elif use_proportional_interpolation:
            cumulative_duration += child_duration
            child_end_jd = parent_start_jd + parent_span * cumulative_duration / total_included_duration
        else:
            child_end_jd = _bounded_end_jd(child_start_jd, child_duration, place)

        children.append(
            (
                tuple(parent_path) + (p_id,),
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
    *,
    divisional_chart_factor=1,
    years=1,
    months=1,
    sixty_hours=1,
    chart_method=1,
    navamsa_chart_method=1,
    dhasa_method=None,
    vimsottari_method_seed_star=3,
    use_real_combusion_limits=True,
    max_cycles=8,
    stop_at_jd=None,
):
    """
    Generates Mahadasa periods by cycling through the fixed (order, rays)
    list, applying balance_factor to only the very first Mahadasa's
    first occurrence, until cumulative duration reaches TARGET_SPAN or
    max_cycles is hit. If stop_at_jd is given, generation stops once a
    Mahadasa containing stop_at_jd has been yielded.

    Yields:
        (maha_lord, maha_start_jd, maha_dur, maha_end_jd, order, planet_rays, total_rays)
    """
    if dhasa_method is None:
        dhasa_method = const.RASHMI_TYPE_DEFAULT

    TARGET_SPAN = const.human_life_span_for_vimsottari_dhasa

    jd_start = drik.next_solar_date(jd_at_dob, place, years, months, sixty_hours)

    planet_rays, total_rays, order, balance_factor = _rashmi_order_rays_and_balance(
        jd_start,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        navamsa_chart_method=navamsa_chart_method,
        dhasa_method=dhasa_method,
        vimsottari_method_seed_star=vimsottari_method_seed_star,
        use_real_combusion_limits=use_real_combusion_limits,
    )

    if total_rays <= 0 or not order:
        return

    total_duration_years = 0.0
    jd_cursor = jd_start
    cycles = 0

    while total_duration_years < TARGET_SPAN and cycles < max_cycles:
        for i, p_id in enumerate(order):
            if total_duration_years >= TARGET_SPAN:
                return

            duration = planet_rays.get(p_id, 0)

            if cycles == 0 and i == 0:
                duration *= balance_factor

            if duration <= 0:
                continue

            maha_start_jd = jd_cursor
            maha_end_jd = _bounded_end_jd(maha_start_jd, duration, place)

            yield p_id, maha_start_jd, duration, maha_end_jd, order, planet_rays, total_rays

            jd_cursor = maha_end_jd
            total_duration_years += duration

            if stop_at_jd is not None and maha_start_jd <= stop_at_jd < maha_end_jd:
                return

        cycles += 1


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
    dob, tob, place,
    divisional_chart_factor=1,
    years=1, months=1, sixty_hours=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    dhasa_method=const.RASHMI_TYPE.BPHS_HIGHEST_RAY,      # 1=Highest Ray (BPHS), 2=Natural, 3=Vimshottari Order
    chart_method=1,
    navamsa_chart_method=1,
    vimsottari_method_seed_star=3,
    max_cycles=8,
    use_real_combusion_limits=True,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
    return_exact_bounds=False,
):
    """
    Provides Rashmi dhasa-bhukthi for a given date, to the requested
    depth (1..6).

    If return_exact_bounds=True, each row is instead:
        [lords_tuple, start_jd_float, end_jd_float, duration_years]
    """
    utils.validate_star_index(vimsottari_method_seed_star)

    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    jd_birth = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd_birth,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

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
            y, m, d, fh = utils.jd_to_gregorian(start_jd_local)
            durn = (
                round(duration_years, dhasa_level_index + 1)
                if round_duration
                else duration_years
            )

            retval.append([lords_tuple, (y, m, d, fh), durn])

    def _recurse(
        level,
        parent_path,
        parent_start_jd,
        parent_duration_years,
        parent_end_jd,
        order,
        planet_rays,
        total_rays,
    ):
        children, _ = _get_rashmi_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            order,
            planet_rays,
            total_rays,
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
                    order,
                    planet_rays,
                    total_rays,
                )
            else:
                _emit_row(
                    child_path,
                    child_start_jd,
                    child_duration,
                    child_end_jd,
                )

    for (
        maha_lord, maha_start_jd, maha_dur, maha_end_jd,
        order, planet_rays, total_rays,
    ) in _generate_mahadasa_periods(
        jd_birth,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        chart_method=chart_method,
        navamsa_chart_method=navamsa_chart_method,
        dhasa_method=dhasa_method,
        vimsottari_method_seed_star=vimsottari_method_seed_star,
        use_real_combusion_limits=use_real_combusion_limits,
        max_cycles=max_cycles,
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
                2,
                (maha_lord,),
                maha_start_jd,
                maha_dur,
                maha_end_jd,
                order,
                planet_rays,
                total_rays,
            )

    return retval


def get_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (optional)
    parent_end=None,             # (Y, M, D, fractional_hour) (optional)
    *,
    jd_at_dob,
    place,
    dhasa_method: int = None,
    chart_method: int = 1,
    navamsa_chart_method: int = 1,
    vimsottari_method_seed_star: int = 3,
    use_real_combusion_limits: bool = True,
    divisional_chart_factor: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns the immediate (parent -> children) splits for a given parent
    span.

    Output rows: [ child_lords_tuple, child_start_tuple, child_end_tuple ]
    """
    if dhasa_method is None:
        dhasa_method = const.RASHMI_TYPE_DEFAULT

    utils.validate_star_index(vimsottari_method_seed_star)

    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")

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
        end_jd = _bounded_end_jd(start_jd, parent_years, place)
    else:
        end_jd = _tuple_to_jd(parent_end)
        parent_years = (end_jd - start_jd) / year_duration

    if end_jd <= start_jd:
        return []

    jd_start = drik.next_solar_date(jd_at_dob, place, years, months, sixty_hours)

    planet_rays, total_rays, order, _balance_factor = _rashmi_order_rays_and_balance(
        jd_start,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        navamsa_chart_method=navamsa_chart_method,
        dhasa_method=dhasa_method,
        vimsottari_method_seed_star=vimsottari_method_seed_star,
        use_real_combusion_limits=use_real_combusion_limits,
    )

    if not order or total_rays <= 0.0:
        return []

    children, _ = _get_rashmi_children_jd(
        path,
        start_jd,
        parent_years,
        place,
        order,
        planet_rays,
        total_rays,
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
    dhasa_method: int = None,
    chart_method: int = 1,
    navamsa_chart_method: int = 1,
    vimsottari_method_seed_star: int = 3,
    use_real_combusion_limits: bool = True,
    divisional_chart_factor: int = 1,
    years: int = 1, months: int = 1, sixty_hours: int = 1,
    max_cycles: int = 8,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Returns the running dasa/antardasa/... chain, from Mahadasha down to
    the requested depth, for current_jd.

    Returns:
        [
            [(l1,),                start1, end1],
            [(l1,l2),              start2, end2],
            [(l1,l2,l3),           start3, end3],
            [(l1,l2,l3,l4),        start4, end4],
            [(l1,l2,l3,l4,l5),     start5, end5],
            [(l1,l2,l3,l4,l5,l6),  start6, end6],
        ]
    """
    if dhasa_method is None:
        dhasa_method = const.RASHMI_TYPE_DEFAULT

    utils.validate_star_index(vimsottari_method_seed_star)

    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)

        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)

        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    maha_lord = maha_start_jd = maha_end_jd = maha_dur = None
    order = planet_rays = total_rays = None

    for (
        maha_lord, maha_start_jd, maha_dur, maha_end_jd,
        order, planet_rays, total_rays,
    ) in _generate_mahadasa_periods(
        jd_at_dob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        years=years,
        months=months,
        sixty_hours=sixty_hours,
        chart_method=chart_method,
        navamsa_chart_method=navamsa_chart_method,
        dhasa_method=dhasa_method,
        vimsottari_method_seed_star=vimsottari_method_seed_star,
        use_real_combusion_limits=use_real_combusion_limits,
        max_cycles=max_cycles,
        stop_at_jd=current_jd,
    ):
        pass

    if maha_lord is None:
        return []

    running_all = [
        [
            (maha_lord,),
            utils.jd_to_gregorian(maha_start_jd),
            utils.jd_to_gregorian(maha_end_jd),
        ]
    ]

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    parent_path = (maha_lord,)
    parent_start_jd = maha_start_jd
    parent_end_jd = maha_end_jd
    parent_duration_years = maha_dur

    for _depth in range(2, target_depth + 1):
        children, _ = _get_rashmi_children_jd(
            parent_path,
            parent_start_jd,
            parent_duration_years,
            place,
            order,
            planet_rays,
            total_rays,
            parent_end_jd=parent_end_jd,
        )

        found = _find_child_containing_jd(children, current_jd)

        if found is None:
            running_all.append(
                [
                    parent_path + (parent_path[-1],),
                    utils.jd_to_gregorian(parent_start_jd),
                    utils.jd_to_gregorian(parent_end_jd),
                ]
            )
            break

        child_path, child_start_jd, child_duration_years, child_end_jd = found

        running_all.append(
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

    return running_all


if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    const.dhasa_year_duration_default = const.DHASA_YEAR_DURATION.TRUE_TROPICAL_YEAR

    from datetime import datetime
    import random
    y, m, d = (random.randrange(1997, 2050), random.randrange(1, 12), random.randrange(1, 26))
    y,m,d = (1998,11,9)
    hh, mm, ss = (random.randrange(1, 23), random.randrange(0, 59), random.randrange(0, 59))
    hh,mm,ss = (15,29,45)
    fh = hh + mm / 60 + ss / 3600
    check_date = utils.date_time_tuple_to_date_time_string(y, m, d, fh)
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
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

    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,India', 13.03862, 80.261818, 5.5)
    rd = get_dhasa_antardhasa(dob, tob, place, dhasa_level_index=2, dhasa_method=1, use_real_combusion_limits=True)
    for row in rd:
        print(row)
