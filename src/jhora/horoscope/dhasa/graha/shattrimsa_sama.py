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
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

year_duration = const.sidereal_year
""" 
    Lagna in Sun's hora in daytime or Lagna in Moon's hora in night time 
    This dasa is applicable if lagna is in deva hora and Sun (soul) is in the visible half from lagna 
    (self that acts in the world), or if lagna is in pitri hora and lagna (acting self) is in the visible 
    half from Sun (soul).
    We define Sukla paksha and Krishna paksha as Sun being in the visible half from
    Moon and and Moon being in the visible half from Sun, respectively. 
    We define daytime and night time as Sun being in the visible half from lagna 
    and lagna being in the visible half from Sun, respectively.
"""

# seed_star = 22 # Shravana / Thiruvonam
seed_lord = 1  # Moon
dhasa_adhipathi_list = {1: 1, 0: 2, 4: 3, 2: 4, 3: 5, 6: 6, 5: 7, 7: 8}  # Total 36 years each cycle
# dhasa_adhipathi_dict = {1: [22, 3, 11, 19], 0: [23, 4, 12, 20], 4: [24, 5, 13, 21], 2: [25, 6, 14], 3: [26, 7, 15], 6: [27, 8, 16], 5: [1, 9, 17], 7: [2, 10, 18]}
count_direction = 1  # 1 => base star to birth star zodiac -1 => base star to birth star antizodiac


def _next_adhipati(lord, dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + dirn) % len(dhasa_adhipathi_list))]
    return next_lord


def _get_dhasa_dict(seed_star=22):
    dhasa_dict = {k: [] for k in dhasa_adhipathi_list.keys()}
    nak = seed_star - 1
    lord = seed_lord
    lord_index = list(dhasa_adhipathi_list.keys()).index(lord)
    for _ in range(27):
        dhasa_dict[lord].append(nak + 1)
        nak = (nak + 1 * count_direction) % 27
        lord_index = (lord_index + 1) % len(dhasa_adhipathi_list)
        lord = list(dhasa_adhipathi_list.keys())[lord_index]
    return dhasa_dict


# dhasa_adhipathi_dict = _get_dhasa_dict()


def _maha_dhasa(nak, seed_star=22):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)
    return [
        (_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord])
        for _dhasa_lord, _star_list in dhasa_adhipathi_dict.items()
        if nak in _star_list
    ][0]


def _antardhasa(dhasa_lord, antardhasa_option=1):
    lord = dhasa_lord
    if antardhasa_option in [3, 4]:
        lord = _next_adhipati(dhasa_lord, dirn=1)
    elif antardhasa_option in [5, 6]:
        lord = _next_adhipati(dhasa_lord, dirn=-1)
    dirn = 1 if antardhasa_option in [1, 3, 5] else -1
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord, dirn)
    return _bhukthis


def _dhasa_start(
    jd,
    place,
    star_position_from_moon=1,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=22,
    dhasa_starting_planet=1,
):
    y, m, d, fh = utils.jd_to_gregorian(jd)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)
    one_star = 360 / 27.0  # 27 nakshatras span 360°
    planet_long = charts.get_chart_element_longitude(
        jd,
        place,
        divisional_chart_factor,
        chart_method,
        star_position_from_moon,
        dhasa_starting_planet,
    )
    nak = int(planet_long / one_star)
    rem = planet_long - nak * one_star
    lord, res = _maha_dhasa(nak + 1, seed_star)  # ruler of current nakshatra
    period = res
    period_elapsed = rem / one_star * period  # years
    period_elapsed *= year_duration  # days
    start_date = jd - period_elapsed  # so many days before current day
    return [lord, start_date, res]


def get_dhasa_bhukthi(
    dob,
    tob,
    place,
    divisional_chart_factor=1,
    chart_method=1,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    seed_star=22,
    dhasa_starting_planet=1,
    antardhasa_option=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    round_duration=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
        returns a list of dasha segments at the selected depth level

        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s)
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 22
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @param dhasa_level_index: Depth level (1..6)
            1 = Maha only (no Antardasha)
            2 = + Antardasha (Bhukthi)
            3 = + Pratyantara
            4 = + Sookshma
            5 = + Prana
            6 = + Deha-antara
        @param round_duration: If True, round only the returned durations to dhasa_level_index

        @return:
          if dhasa_level_index == 1:
              [ (l1, start_str, dur_years), ... ]
          else:
              [ (l1, l2, ..., start_str, leaf_dur_years), ... ]
          (tuple grows by one lord per requested level)
    """
    global year_duration

    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6 (1=Maha .. 6=Deha).")

    _tribhagi_factor = 1.0
    _dhasa_cycles = 3
    if use_tribhagi_variation:
        _tribhagi_factor = 1.0 / 3.0
        _dhasa_cycles = int(_dhasa_cycles / _tribhagi_factor)

    jd = utils.julian_day_number(dob, tob)

    year_duration = drik.dhasa_year_duration(
        jd=jd,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    dhasa_lord, start_jd, _ = _dhasa_start(
        jd,
        place,
        star_position_from_moon=star_position_from_moon,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    retval = []

    # Reuse your antara ordering at every level
    def _children_of(parent_lord):
        return list(_antardhasa(parent_lord, antardhasa_option))

    # Nested expansion: equal split of IMMEDIATE PARENT (sum(children) = parent)
    def _recurse(level, parent_lord, parent_start_jd, parent_duration_years, prefix):
        bhukthis = _children_of(parent_lord)
        if not bhukthis:
            return

        n = len(bhukthis)
        child_dur_unrounded = parent_duration_years / n
        jd_cursor = parent_start_jd

        if level < dhasa_level_index:
            for blord in bhukthis:
                _recurse(level + 1, blord, jd_cursor, child_dur_unrounded, prefix + (blord,))
                jd_cursor += child_dur_unrounded * year_duration
        else:
            for blord in bhukthis:
                start_str = utils.jd_to_gregorian(jd_cursor)
                durn = round(child_dur_unrounded, dhasa_level_index) if round_duration else child_dur_unrounded
                retval.append((prefix + (blord,), start_str, durn))
                jd_cursor += child_dur_unrounded * year_duration

    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            maha_dur_unrounded = dhasa_adhipathi_list[dhasa_lord] * _tribhagi_factor

            if dhasa_level_index == 1:
                start_str = utils.jd_to_gregorian(start_jd)
                durn = round(maha_dur_unrounded, dhasa_level_index) if round_duration else maha_dur_unrounded
                retval.append(((dhasa_lord,), start_str, durn))
                start_jd += maha_dur_unrounded * year_duration
            else:
                _recurse(
                    level=2,
                    parent_lord=dhasa_lord,
                    parent_start_jd=start_jd,
                    parent_duration_years=maha_dur_unrounded,
                    prefix=(dhasa_lord,),
                )
                start_jd += maha_dur_unrounded * year_duration

            dhasa_lord = _next_adhipati(dhasa_lord)

    return retval


def nakshathra_dhasa_progression(
    jd_at_dob,
    place,
    jd_current,
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=22,
    antardhasa_option=1,
    dhasa_starting_planet=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,
    get_running_dhasa=True,
    dhasa_duration_type=None,
    savana_year_method=None,
):
    """
        For nakshathra dhasa calculations for divisional charts - first calculate progression for raasi
        Then do varga division to progressed raasi longitudes
    """
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)
    DLI = dhasa_level_index
    vd = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        seed_star=seed_star,
        antardhasa_option=antardhasa_option,
        dhasa_starting_planet=dhasa_starting_planet,
        dhasa_level_index=DLI,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    if get_running_dhasa:
        vdc = utils.get_running_dhasa_for_given_date(jd_current, vd)
        print(vdc)
    jds = [
        utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))
        for _, (y, m, d, fh), *_ in vd
    ]
    """ Note: First we get rasi positions and then find varga division so for rasi we pass divisional_chart_factor=1"""
    planet_long = charts.get_chart_element_longitude(
        jd_at_dob,
        place,
        divisional_chart_factor=1,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        dhasa_starting_planet=dhasa_starting_planet,
    )

    birth_star_index = int((planet_long % 360.0) // utils.ONE_NAK)
    prog_long = utils.progressed_abs_long_general(
        jds,
        jd_current,
        birth_star_index,
        dhasa_level_index=DLI,
        total_lords_in_dhasa=len(dhasa_adhipathi_list),
    )
    progression_correction = utils.norm360(prog_long - planet_long)
    if get_running_dhasa:
        return progression_correction, vdc
    else:
        return progression_correction
    ppl = charts.get_nakshathra_dhasa_progression_longitudes(
        jd_at_dob,
        place,
        planet_progression_correction=progression_correction,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
    )
    return ppl


def shattrimsa_sama_immediate_children(
    parent_lords,
    parent_start,                # (Y, M, D, fractional_hour)
    parent_duration=None,        # float years (optional)
    parent_end=None,             # (Y, M, D, fractional_hour) (optional)
    *,
    jd_at_dob,
    place,
    # REQUIRED knob (explicit; used by _antardhasa)
    antardhasa_option: int = 1,
    # Accepted for API parity (not used here by the tiler itself)
    star_position_from_moon=1,
    use_tribhagi_variation=False,
    divisional_chart_factor=1,
    chart_method=1,
    seed_star=22,
    dhasa_starting_planet=1,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Shattrimsa (Sama) — return ONLY the immediate (p -> p+1) children for the given parent span.

    Rules (match your base get_dhasa_bhukthi):
      • Antara order at EVERY level: _antardhasa(parent_lord, antardhasa_option)
      • Sama subdivision at this level: child_years = parent_years / n
      • Exact tiling within [parent_start, parent_end)

    Output rows:
      [ (lords_tuple_with_child), child_start_tuple, child_end_tuple ]
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- normalize lords path
    if isinstance(parent_lords, int):
        path = (parent_lords,)
    elif isinstance(parent_lords, (list, tuple)) and parent_lords:
        path = tuple(parent_lords)
    else:
        raise ValueError("parent_lords must be int or non-empty tuple/list of ints")
    parent_lord = path[-1]

    # ---- canonical tuple <-> JD helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _jd_to_tuple(jd_val):
        return utils.jd_to_gregorian(jd_val)

    # ---- resolve parent span
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

    # ---- child order via your antara rule
    def _children_of(pl):
        return list(_antardhasa(pl, antardhasa_option))

    child_lords = _children_of(parent_lord)
    if not child_lords:
        return []

    # ---- equal split at this level
    n = len(child_lords)
    child_years = parent_years / n

    # ---- tile children within parent [start, end)
    children = []
    cursor = start_jd
    for i, cl in enumerate(child_lords):
        if i == n - 1:
            child_end = end_jd
        else:
            child_end = cursor + child_years * year_duration

        children.append([
            path + (cl,),
            _jd_to_tuple(cursor),
            _jd_to_tuple(child_end),
        ])
        cursor = child_end
        if cursor >= end_jd:
            break

    if children:
        children[-1][2] = _jd_to_tuple(end_jd)

    return children


def get_running_dhasa_for_given_date(
    current_jd,
    jd_at_dob,
    place,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
    *,
    # REQUIRED knob (explicit; forwarded to base + children)
    antardhasa_option: int = 1,
    # Forwarded to base Shattrimsa Sama get_dhasa_bhukthi:
    divisional_chart_factor: int = 1,
    chart_method: int = 1,
    star_position_from_moon: int = 1,
    use_tribhagi_variation: bool = False,
    seed_star: int = 22,
    dhasa_starting_planet: int = 1,
    round_duration: bool = False,
    dhasa_duration_type=None,
    savana_year_method=None,
    **kwargs,
):
    """
    Shattrimsa (Sama) — narrow Mahā -> … -> target depth and return the full running ladder.
    """
    global year_duration

    year_duration = drik.dhasa_year_duration(
        jd=jd_at_dob,
        place=place,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )

    # ---- depth normalization (Enum-friendly)
    def _normalize_depth(depth_val):
        try:
            depth = int(depth_val)
        except Exception:
            depth = int(const.MAHA_DHASA_DEPTH.DEHA)
        lo = int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY)
        hi = int(const.MAHA_DHASA_DEPTH.DEHA)
        return min(hi, max(lo, depth))

    target_depth = _normalize_depth(dhasa_level_index)

    # ---- tuple -> JD & zero-length helpers
    def _tuple_to_jd(t):
        y, m, d, fh = t
        return utils.julian_day_number(drik.Date(y, m, d), (fh, 0, 0))

    def _is_zero_length(s, e, eps_seconds=1.0):
        return (_tuple_to_jd(e) - _tuple_to_jd(s)) * 86400.0 <= eps_seconds

    def _to_utils_periods(children_rows, parent_end_tuple, eps_seconds=1.0):
        """
        children_rows: [ [lords_tuple, start_tuple, end_tuple], ... ]
        Returns: list of (lords_tuple, start_tuple) + sentinel (... , parent_end_tuple),
        filtering zero-length rows and enforcing strictly increasing starts.
        """
        filtered = [r for r in children_rows if not _is_zero_length(r[1], r[2], eps_seconds=eps_seconds)]
        if not filtered:
            return []
        filtered.sort(key=lambda r: _tuple_to_jd(r[1]))
        proj, prev = [], None
        for lords, st, _ in filtered:
            sjd = _tuple_to_jd(st)
            if prev is None or sjd > prev:
                proj.append((lords, st))
                prev = sjd
        proj.append((proj[-1][0], parent_end_tuple))
        return proj

    def _as_tuple_lords(x):
        return (x,) if isinstance(x, int) else tuple(x)

    # ---- derive dob/tob for base L1 generator
    y, m, d, fh = utils.jd_to_gregorian(jd_at_dob)
    dob = drik.Date(y, m, d)
    tob = (fh, 0, 0)

    running_all = []

    # ---- Level 1: Mahā via your base function
    maha_rows = get_dhasa_bhukthi(
        dob,
        tob,
        place,
        divisional_chart_factor=divisional_chart_factor,
        chart_method=chart_method,
        star_position_from_moon=star_position_from_moon,
        use_tribhagi_variation=use_tribhagi_variation,
        seed_star=seed_star,
        dhasa_starting_planet=dhasa_starting_planet,
        antardhasa_option=antardhasa_option,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        round_duration=False,
        dhasa_duration_type=dhasa_duration_type,
        savana_year_method=savana_year_method,
    )
    maha_for_utils = [(_as_tuple_lords(row[0]), row[1]) for row in maha_rows]

    # Running Mahā
    rd1 = utils.get_running_dhasa_for_given_date(current_jd, maha_for_utils)
    running = [_as_tuple_lords(rd1[0]), rd1[1], rd1[2]]
    running_all.append(running)

    if target_depth == int(const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY):
        return running_all

    # ---- Levels 2..target: expand only the running parent each step
    for depth in range(2, target_depth + 1):
        parent_lords, parent_start, parent_end = running

        children = shattrimsa_sama_immediate_children(
            parent_lords=parent_lords,
            parent_start=parent_start,
            parent_end=parent_end,
            jd_at_dob=jd_at_dob,
            place=place,
            antardhasa_option=antardhasa_option,
            star_position_from_moon=star_position_from_moon,
            use_tribhagi_variation=use_tribhagi_variation,
            divisional_chart_factor=divisional_chart_factor,
            chart_method=chart_method,
            seed_star=seed_star,
            dhasa_starting_planet=dhasa_starting_planet,
            dhasa_duration_type=dhasa_duration_type,
            savana_year_method=savana_year_method,
            **kwargs,
        )

        if not children:
            running = [parent_lords + (parent_lords[-1],), parent_end, parent_end]
            running_all.append(running)
            continue

        periods_for_utils = _to_utils_periods(children, parent_end_tuple=parent_end)
        if not periods_for_utils:
            last = children[-1]
            running = [last[0], last[1], last[1]]
        else:
            rdk = utils.get_running_dhasa_for_given_date(current_jd, periods_for_utils)
            running = [_as_tuple_lords(rdk[0]), rdk[1], rdk[2]]

        running_all.append(running)

    return running_all


'------ main -----------'
if __name__ == "__main__":
    utils.set_language('en')
    dob = drik.Date(1996, 12, 7)
    tob = (10, 34, 0)
    place = drik.Place('Chennai,IN', 13.0389, 80.2619, +5.5)
    jd_at_dob = utils.julian_day_number(dob, tob)
    from datetime import datetime
    current_date_str, current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    y, m, d = map(int, current_date_str.split(','))
    hh, mm, ss = map(int, current_time_str.split(':'))
    fh = hh + mm / 60 + ss / 3600
    print(utils.date_time_tuple_to_date_time_string(y, m, d, fh))
    current_jd = utils.julian_day_number(drik.Date(y, m, d), (hh, mm, ss))
    import time
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
            "Dehā        :",
            get_running_dhasa_for_given_date(
                current_jd,
                jd_at_dob,
                place,
                dhasa_level_index=const.MAHA_DHASA_DEPTH.DEHA,
                dhasa_duration_type=dd,
            ),
        )
        print('new method elapsed time', time.time() - start_time)

        start_time = time.time()
        ad = get_dhasa_bhukthi(
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
                dhasa_cycle_count=3,
            )
        )
        print('old method elapsed time', time.time() - start_time)
    exit()
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.shattrimsa_sama_test()
