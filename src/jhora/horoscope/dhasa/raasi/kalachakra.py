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
import numpy as np
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import house, charts
""" TODO: Dhasa Progression does not seem to match with JHora """
def _get_dhasa_progression(planet_longitude):
    nakshatra,paadham,_ = drik.nakshatra_pada(planet_longitude)
    nakshatra -= 1
    paadham -= 1
    kalachakra_index = 0
    if nakshatra in const.savya_stars_1:
        kalachakra_index = 0
    elif nakshatra in const.savya_stars_2:
        kalachakra_index = 1
    elif nakshatra in const.apasavya_stars_1:
        kalachakra_index = 2
    else:
        kalachakra_index = 3
    dhasa_progression = const.kalachakra_rasis[kalachakra_index][paadham]
    dhasa_paramayush = const.kalachakra_paramayush[kalachakra_index][paadham]
    dhasa_duration = [const.kalachakra_dhasa_duration[r] for r in dhasa_progression]
    one_star = (360.0/27)
    one_paadha = (360.0 / 108)
    nak_start_long = nakshatra*one_star + paadham * one_paadha
    nak_travel_fraction = (planet_longitude-nak_start_long)/one_paadha
    dhasa_duration_cumulative = np.cumsum(dhasa_duration)
    paramayush_completed = nak_travel_fraction * dhasa_paramayush
    dhasa_index_at_birth = next(x[0] for x in enumerate(dhasa_duration_cumulative) if x[1] > paramayush_completed)
    dhasa_remaining_at_birth = dhasa_duration_cumulative[dhasa_index_at_birth]-paramayush_completed
    kalachakra_index_next = kalachakra_index
    paadham_next = (paadham+1)%4
    if paadham==3:
        if kalachakra_index == 0:
            kalachakra_index_next = 1
        elif kalachakra_index == 1:
            kalachakra_index_next = 0
        elif kalachakra_index == 2:
            kalachakra_index_next = 3
        elif kalachakra_index == 3:
            kalachakra_index_next = 2
    dhasa_progression = dhasa_progression[dhasa_index_at_birth:]+const.kalachakra_rasis[kalachakra_index_next][paadham_next][:dhasa_index_at_birth]
    dhasa_duration = [const.kalachakra_dhasa_duration[r] for r in dhasa_progression]
    dhasa_duration[0] = dhasa_remaining_at_birth
    dhasa_periods = []
    for i,dp in enumerate(dhasa_progression):
        ad = antardhasa(dhasa_index_at_birth,i, kalachakra_index_next, paadham)
        """
            Temporary Fix if ad = empty list
        """
        if len(ad)==0: ad=[dhasa_progression,[const.kalachakra_dhasa_duration[r] for r in dhasa_progression]]
        dhasa_periods.append([dp,ad,dhasa_duration[i]])
    return dhasa_periods
def antardhasa(dhasa_index_at_birth,dp_index,kc_index,paadham):
    dp_begin = kc_index*9*4+paadham*9+dhasa_index_at_birth+dp_index
    antardhasa_progression=const.kalachakra_rasis_list[dp_begin:dp_begin+9]
    antardhasa_duration = [const.kalachakra_dhasa_duration[r] for r in antardhasa_progression]
    """ TODO: handle if above is empty list [] """
    if len(antardhasa_duration)==0:
        return []
    dhasa_duration = antardhasa_duration[0]
    antardhasa_fraction = dhasa_duration/sum(antardhasa_duration)
    antardhasa_duration = [(ad * antardhasa_fraction) for ad in antardhasa_duration]
    return [antardhasa_progression,antardhasa_duration]

def kalachakra_dhasa(
    planet_longitude,
    jd,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6 (1=Maha only, 2=+Antara [default], 3..6 pending spec)
    round_duration=True
):
    """
        Kalachakra Dasha calculation (depth-enabled: L1 & L2 ready; L3+ to be added per your spec)

        @param planet_longitude: longitude (deg) of the seed body (Moon by default in caller) at birth epoch
        @param jd:               JD at birth epoch (float)
        @param dhasa_level_index: 1..6
            1 = Maha only                  -> (l1,             start_str, dur_years)
            2 = + Antardasa (Bhukti)      -> (l1, l2,         start_str, dur_years)    [DEFAULT]
            3..6 = deeper levels           -> (l1, l2, l3, …,  start_str, dur_years)   [to be wired after spec]
        @param round_duration: Round only returned durations; JD math uses full precision.
    """
    if not (1 <= dhasa_level_index <= 6):
        raise ValueError("dhasa_level_index must be in 1..6")

    dhasa_periods = _get_dhasa_progression(planet_longitude)
    if not dhasa_periods:
        return []

    rows = []
    dhasa_start_jd = jd
    _ndig = getattr(const, 'DHASA_DURATION_ROUNDING_TO', 2)

    for dp in dhasa_periods:
        ds, ad, dd = dp  # ds = dasha rasi, ad = [bhukti_rasis, bhukti_years], dd = maha years

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY:
            # L1: Maha only
            start_str = utils.julian_day_to_date_time_string(dhasa_start_jd)
            dur_ret   = round(dd, _ndig) if round_duration else dd
            rows.append([ds, start_str, dur_ret])
            dhasa_start_jd += dd * const.sidereal_year
            continue

        if dhasa_level_index == const.MAHA_DHASA_DEPTH.ANTARA:
            # L2: Antardasa (use your ad as-is)
            bhut_rasis, bhut_years = ad
            jd_b = dhasa_start_jd
            for b_idx in range(len(bhut_rasis)):
                bhukthi_lord   = bhut_rasis[b_idx]
                bhukthi_years  = float(bhut_years[b_idx])
                start_str      = utils.julian_day_to_date_time_string(jd_b)
                dur_ret        = round(bhukthi_years, _ndig) if round_duration else bhukthi_years
                rows.append([ds, bhukthi_lord, start_str, dur_ret])
                jd_b += bhukthi_years * const.sidereal_year

            # Advance to next Maha; we keep this line as in your code (you can choose to
            # disable if your AD durations already exactly sum to dd).
            dhasa_start_jd += dd * const.sidereal_year
            continue

        # L3..L6: pending your exact rule on recursive antardasa indexing and kc_index/pada usage.
        raise NotImplementedError(
            "Kalachakra levels 3..6 will be wired after you confirm dp_index/kc_index/pada rules (see questions)."
        )

    return rows


def get_dhasa_bhukthi(
    dob, tob, place,
    divisional_chart_factor=1,
    dhasa_starting_planet=1,
    star_position_from_moon=1,
    dhasa_level_index=const.MAHA_DHASA_DEPTH.ANTARA,  # 1..6
    round_duration=True
):
    """
        returns kalachakra dhasa/bhukthi (depth-enabled)
        Shapes by depth:
          L1 -> [ [l1,             start_str, dur_years], ...]
          L2 -> [ [l1, l2,         start_str, dur_years], ...]
          L3+-> [ [l1, l2, l3, …,  start_str, dur_years], ...]  (pending spec)

        Notes:
        - Seed body is controlled by dhasa_starting_planet (Moon default), with star_position_from_moon shift.
        - We do not re-implement any KCD table logic here.
    """
    jd = utils.julian_day_number(dob, tob)
    from jhora.horoscope.chart import charts, sphuta
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)

    # Compute seed longitude per your original logic
    if dhasa_starting_planet in const.SUN_TO_KETU:
        planet_long = planet_positions[dhasa_starting_planet+1][1][0]*30 + planet_positions[dhasa_starting_planet+1][1][1]
    elif dhasa_starting_planet == const._ascendant_symbol:
        planet_long = planet_positions[0][1][0]*30 + planet_positions[0][1][1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == 'M':
        mn = drik.maandi_longitude(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0]*30 + mn[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == 'G':
        gl = drik.gulika_longitude(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30 + gl[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == 'B':
        bb = drik.bhrigu_bindhu_lagna(jd, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = bb[0]*30 + bb[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == 'I':
        il = drik.indu_lagna(jd, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = il[0]*30 + il[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == 'P':
        pr = drik.pranapada_lagna(jd, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = pr[0]*30 + pr[1]
    elif isinstance(dhasa_starting_planet, str) and dhasa_starting_planet.upper() == 'T':
        sp = sphuta.tri_sphuta(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        planet_long = sp[0]*30 + sp[1]
    else:
        # Default = Moon
        planet_long = planet_positions[const.MOON_ID+1][1][0]*30 + planet_positions[const.MOON_ID+1][1][1]

    if dhasa_starting_planet == 1:  # Moon-based shifts
        one_star = (360.0 / 27.0)
        planet_long += (star_position_from_moon - 1) * one_star

    return kalachakra_dhasa(
        planet_long, jd,
        dhasa_level_index=dhasa_level_index,
        round_duration=round_duration
    )

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = True
    pvr_tests.kalachakra_dhasa_tests()
