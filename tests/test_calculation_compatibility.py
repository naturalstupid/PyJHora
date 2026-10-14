"""Portable regressions with synthetic inputs; no JHora installation required."""
import unittest
from unittest.mock import patch

from jhora import const, utils
from jhora.panchanga import drik


class CalculationCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.date = drik.Date(2000, 1, 1)
        self.place = drik.Place('Synthetic', 0.0, 0.0, 5.5, elevation=0.0)
        self.midnight = utils.gregorian_to_jd(self.date)

    def events(self, jd, _place, hour):
        y, m, d, _ = utils.jd_to_gregorian(jd)
        midnight = utils.gregorian_to_jd(drik.Date(y, m, d))
        return [hour, '', midnight + hour / 24]

    def sunrise(self, jd, place):
        return self.events(jd, place, 6.0)

    def sunset(self, jd, place):
        return self.events(jd, place, 18.0)

    def fake_ascendant(self, jd, _place):
        hour = (jd - self.midnight) * 24
        longitude = hour * 10 % 360
        return [int(longitude // 30), longitude % 30, 1, 1]

    def test_sunrise_and_sunset_preserve_fractional_seconds(self):
        # The third return value is local JD, not a second-rounded display value.
        for function in (drik.sunrise, drik.sunset):
            with self.subTest(function=function.__name__):
                event_ut = self.midnight + 0.123456789
                with patch.object(drik.swe, 'rise_trans', return_value=(0, (event_ut,))):
                    event = function(self.midnight, self.place)
                self.assertAlmostEqual(event[2], event_ut + self.place.timezone / 24, places=9)

    def test_special_lagna_uses_local_sunrise_without_double_timezone(self):
        birth = self.midnight + 18 / 24
        def positions(jd, _place):
            # Synthetic Sun longitude = local hour; an extra timezone is observable.
            longitude = (jd - self.midnight) * 24
            return [[0, (int(longitude // 30), longitude % 30)]]
        with patch.object(drik, 'sunrise', side_effect=self.sunrise), \
             patch.object(drik, 'dhasavarga', side_effect=positions):
            result = drik.special_ascendant(birth, self.place, .5, special_lagna_continuity=False)
        self.assertAlmostEqual(result[0] * 30 + result[1], 6.0, places=5)

    def test_special_lagna_before_sunrise_uses_previous_sunrise(self):
        birth = self.midnight + 4 / 24
        def positions(jd, _place):
            return [[0, (1, 10.0 if jd < self.midnight else 20.0)]]
        with patch.object(drik, 'sunrise', side_effect=self.sunrise), \
             patch.object(drik, 'dhasavarga', side_effect=positions):
            result = drik.special_ascendant(birth, self.place, .25, special_lagna_continuity=False)
        # 22 hours from previous 06:00 sunrise: 40 + 22*15 = 370 -> 10.
        self.assertAlmostEqual(result[0] * 30 + result[1], 10.0, places=5)

    def test_night_upagraha_starts_at_sunset_and_crosses_midnight(self):
        with patch.object(drik, 'sunrise', side_effect=self.sunrise), \
             patch.object(drik, 'sunset', side_effect=self.sunset), \
             patch.object(drik, 'ascendant', side_effect=self.fake_ascendant):
            longitude = drik._upagraha_longitude_full(
                self.date, (20, 0, 0), self.place, const.SATURN_ID, 'begin')
        # Saturday night Saturn is part 3: 18:00 + 3*(12h/8) = 22:30.
        self.assertAlmostEqual(longitude, 225.0, places=5)

    def test_pre_dawn_upagraha_uses_previous_evening(self):
        with patch.object(drik, 'sunrise', side_effect=self.sunrise), \
             patch.object(drik, 'sunset', side_effect=self.sunset), \
             patch.object(drik, 'ascendant', side_effect=self.fake_ascendant):
            longitude = drik._upagraha_longitude_full(
                self.date, (4, 0, 0), self.place, const.SATURN_ID, 'begin')
        # Friday night Saturn is part 4: previous 18:00 + 6h = current 00:00.
        self.assertAlmostEqual(longitude, 0.0, places=5)

    def test_pranapada_anchors_to_birth_sun_and_applies_correction_once(self):
        birth = self.midnight + 18 / 24
        with patch.object(drik, 'sunrise', side_effect=self.sunrise), \
             patch.object(drik, 'dhasavarga', return_value=[[0, (0, 6.0)]]), \
             patch.object(drik, 'solar_longitude', return_value=100.0):
            result = drik.pranapada_lagna(birth, self.place, 1.0, special_lagna_continuity=False)
        # 12h * 300 degrees/hour is a complete number of circles; Cancer is movable.
        self.assertAlmostEqual(result[0] * 30 + result[1], 101.0, places=5)

    def test_node_selection_updates_special_point_reference(self):
        previous = (const._use_true_nodes_for_rahu_ketu, const._INCLUDE_URANUS_TO_PLUTO,
                    const._RAHU, const._KETU, drik.planet_list)
        try:
            drik.set_planet_list(set_rahu_ketu_as_true_nodes=False, include_western_planets=False)
            self.assertEqual(const._RAHU, drik.swe.MEAN_NODE)
            self.assertEqual(drik.planet_list[const._RAHU], const.RAHU_ID)
            drik.set_planet_list(set_rahu_ketu_as_true_nodes=True, include_western_planets=False)
            self.assertEqual(const._RAHU, drik.swe.TRUE_NODE)
            self.assertEqual(drik.planet_list[const._RAHU], const.RAHU_ID)
        finally:
            (const._use_true_nodes_for_rahu_ketu, const._INCLUDE_URANUS_TO_PLUTO,
             const._RAHU, const._KETU, drik.planet_list) = previous


if __name__ == '__main__':
    unittest.main()
