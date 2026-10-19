"""Synthetic native-curve controls; no birth inputs or native artifacts.

The interval endpoint oracle is independent of the production branching code.
Each interval has independently specified exact-start and left-limit values.
"""

import copy
import math
import struct
import unittest
from typing import Dict

from jhora.compatibility import aspects

# One entry per [30*n, 30*(n+1)) interval: exact start and left-limit end.
_STARTS = {
    0: (0, 0, 15, 45, 30, 0, 60, 45, 30, 15, 0, 0),
    2: (0, 0, 15, 60, 30, 0, 60, 60, 30, 15, 0, 0),
    4: (0, 0, 15, 45, 60, 0, 60, 45, 60, 15, 0, 0),
    6: (0, 0, 60, 45, 30, 0, 60, 45, 30, 60, 0, 0),
}
_ENDS = {
    0: (0, 15, 45, 30, 0, 60, 45, 30, 15, 0, 0, 0),
    2: (0, 15, 60, 30, 0, 60, 60, 30, 15, 0, 0, 0),
    4: (0, 15, 45, 60, 0, 60, 45, 60, 15, 0, 0, 0),
    6: (0, 60, 45, 30, 0, 60, 45, 30, 60, 0, 0, 0),
}


def reference(angle: float, source: int) -> float:
    """Interpolate independently reviewed interval endpoints."""
    sector = int(angle // 30)
    start = _STARTS.get(source, _STARTS[0])[sector]
    end = _ENDS.get(source, _ENDS[0])[sector]
    return start + (end - start) * ((angle - 30 * sector) / 30)


def adjacent(value: float, direction: int) -> float:
    """Return an adjacent positive double without Python 3.9's nextafter."""
    if value == 0:
        return direction * 5e-324
    bits = struct.unpack(">Q", struct.pack(">d", value))[0]
    return struct.unpack(">d", struct.pack(">Q", bits + direction))[0]


def synthetic_points() -> Dict[int, float]:
    """Return an arithmetic construction, not a transformed personal chart."""
    return {source: (source * 40.0 + 0.125) % 360 for source in range(9)}


class AspectCompatibilityTests(unittest.TestCase):
    def test_all_planets_match_interval_reference_every_arcminute(self) -> None:
        for source in range(9):
            for minute in range(360 * 60):
                angle = minute / 60
                value = aspects.jhora8_parasara_virupas(angle, source)
                self.assertAlmostEqual(value, reference(angle, source), places=11)
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 60)

    def test_all_exact_and_adjacent_boundaries_match_reference(self) -> None:
        for source in range(9):
            for knot in range(0, 361, 30):
                for angle in (adjacent(float(knot), -1), float(knot), adjacent(float(knot), 1), knot - 1e-8, knot + 1e-8):
                    if 0 <= angle < 360:
                        with self.subTest(source=source, angle=angle):
                            self.assertAlmostEqual(aspects.jhora8_parasara_virupas(angle, source), reference(angle, source), places=11)

    def test_special_branches_use_complete_native_parasara_rules(self) -> None:
        cases = (
            (2, 75, 37.5),
            (2, 105, 45),
            (2, 135, 15),
            (2, 195, 60),
            (2, 225, 45),
            (4, 105, 52.5),
            (4, 135, 30),
            (4, 225, 52.5),
            (4, 255, 37.5),
            (6, 45, 30),
            (6, 75, 52.5),
            (6, 255, 45),
            (6, 285, 30),
        )
        for source, angle, expected in cases:
            with self.subTest(source=source, angle=angle):
                self.assertEqual(aspects.jhora8_parasara_virupas(angle, source), expected)

    def test_jupiter_native_taper_is_distinct_from_classical(self) -> None:
        # Classical [240,270) uses 60-2*r: at 255 that gives 30, not 37.5.
        self.assertEqual(aspects.FORMULA_ID, "JH8-Parasara-sphuta-v1")
        self.assertEqual(aspects.FORMULA_VERSION, "1.0.0")
        self.assertEqual(aspects.jhora8_parasara_virupas(240, 4), 60)
        self.assertEqual(aspects.jhora8_parasara_virupas(255, 4), 37.5)
        self.assertAlmostEqual(aspects.jhora8_parasara_virupas(270 - 1e-8, 4), 15.000000015)
        self.assertEqual(aspects.jhora8_parasara_virupas(270, 4), 15)

    def test_direction_and_canonical_ids_ignore_presentation_order(self) -> None:
        points = synthetic_points()
        points.update({0: 0.0, 1: 75.0})
        result = aspects.jhora8_parasara_aspects(dict(reversed(list(points.items()))))
        self.assertEqual(list(result), list(range(9)))
        self.assertTrue(all(list(row) == list(range(9)) for row in result.values()))
        self.assertEqual(result[0][1], 50)  # 75 degrees -> 30 virupas.
        self.assertEqual(result[1][0], 13)  # 285 degrees -> 7.5 virupas; 12.5% half-up.

    def test_self_blank_is_distinct_from_coincident_zero(self) -> None:
        result = aspects.jhora8_parasara_aspects({source: 0.0 for source in range(9)}, ascendant_longitude=0.0)
        self.assertEqual(sum(value is None for row in result.values() for value in row.values()), 9)
        self.assertEqual(sum(value is not None for row in result.values() for value in row.values()), 180)
        for source, row in result.items():
            self.assertIsNone(row[source])
            self.assertTrue(all(row[target] == 0 for target in range(9) if target != source))
            self.assertEqual(row["H1"], 0)
            self.assertEqual(row["H7"], 100)

    def test_nodes_use_ordinary_curve_in_both_directions(self) -> None:
        for source in (7, 8):
            for angle in range(360):
                self.assertEqual(aspects.jhora8_parasara_virupas(angle, source), aspects.jhora8_parasara_virupas(angle, 0))
        points = synthetic_points()
        points.update({7: 15.0, 8: 195.0})
        table = aspects.jhora8_parasara_aspects(points)
        self.assertEqual(table[7][8], 100)
        self.assertEqual(table[8][7], 100)

    def test_raw_units_and_final_half_up_rounding_without_angle_rounding(self) -> None:
        points = synthetic_points()
        points.update({0: 0.0, 1: 75.0, 3: 285.0})
        raw = aspects.jhora8_parasara_aspects(points, normalize_as_percentage=False)
        percent = aspects.jhora8_parasara_aspects(points)
        self.assertEqual(raw[0][1], 30)
        self.assertEqual(raw[0][3], 7.5)
        self.assertEqual(percent[0][3], 13)  # Python's round(12.5) would be 12.
        for source in range(9):
            for target in range(9):
                if source != target:
                    self.assertIsInstance(percent[source][target], int)
                    self.assertEqual(percent[source][target], math.floor(raw[source][target] * (100 / 60) + 0.5))
        points[3] = 285.000001
        self.assertEqual(aspects.jhora8_parasara_aspects(points)[0][3], 12)
        self.assertNotEqual(aspects.jhora8_parasara_aspects(points, normalize_as_percentage=False)[0][3], 7.5)

    def test_houses_use_this_charts_ascendant_plus_thirty_degrees(self) -> None:
        points = synthetic_points()
        result = aspects.jhora8_parasara_aspects(points, ascendant_longitude=347.125, normalize_as_percentage=False)
        for source, row in result.items():
            self.assertEqual(list(row), list(range(9)) + ["H%d" % house for house in range(1, 13)])
            for house in range(1, 13):
                angle = (347.125 + 30 * (house - 1) - points[source]) % 360
                self.assertEqual(row["H%d" % house], reference(angle, source))
        self.assertNotEqual(result, aspects.jhora8_parasara_aspects(points, ascendant_longitude=17.125, normalize_as_percentage=False))

    def test_common_rotation_does_not_change_planet_or_house_table(self) -> None:
        points = synthetic_points()
        original = copy.deepcopy(points)
        expected = aspects.jhora8_parasara_aspects(points, ascendant_longitude=17.125)
        for offset in (30, 90, 180, 330):
            rotated = {source: (longitude + offset) % 360 for source, longitude in points.items()}
            self.assertEqual(aspects.jhora8_parasara_aspects(rotated, ascendant_longitude=(17.125 + offset) % 360), expected)
        self.assertEqual(points, original)

    def test_invalid_angle_or_source_fails_instead_of_clamping(self) -> None:
        for invalid in (None, True, False, "90", -0.001, 360, float("nan"), float("inf"), 10**1000):
            with self.subTest(angle=invalid), self.assertRaises(ValueError):
                aspects.jhora8_parasara_virupas(invalid, 4)
        for invalid in (-1, 9, True, None, 2.0, "Mars"):
            with self.subTest(source=invalid), self.assertRaises(ValueError):
                aspects.jhora8_parasara_virupas(90, invalid)

    def test_missing_invalid_or_unsupported_matrix_inputs_fail_explicitly(self) -> None:
        points = synthetic_points()
        invalid_maps = (
            None,
            list(points.values()),
            {},
            {0: 0.0},
            {**points, 9: 0.0},
            {**points, 1: None},
            {**points, 3: 360},
            {**points, 2: float("nan")},
        )
        for invalid in invalid_maps:
            with self.subTest(points=invalid), self.assertRaises(ValueError):
                aspects.jhora8_parasara_aspects(invalid)
        invalid_ids = dict(points)
        invalid_ids[True] = invalid_ids.pop(1)
        with self.assertRaises(ValueError):
            aspects.jhora8_parasara_aspects(invalid_ids)
        for invalid in (True, -1, 360, float("inf"), "0"):
            with self.subTest(ascendant=invalid), self.assertRaises(ValueError):
                aspects.jhora8_parasara_aspects(points, ascendant_longitude=invalid)
        with self.assertRaises(ValueError):
            aspects.jhora8_parasara_aspects(points, normalize_as_percentage="False")
        # Neither Raman nor alternate house methods are silently substituted.
        with self.assertRaises(TypeError):
            aspects.jhora8_parasara_aspects(points, method="raman")
        with self.assertRaises(TypeError):
            aspects.jhora8_parasara_aspects(points, bhava_madhya_method=3)


class AspectChartContextTests(unittest.TestCase):
    def test_each_varga_and_mixed_chart_is_recomputed_from_its_own_positions(self) -> None:
        from jhora.horoscope.chart import charts

        # Independent synthetic arithmetic sequence, never a supplied chart.
        natal = [[body, [int(longitude // 30), longitude % 30]] for body, longitude in [("L", 17.125)] + list(synthetic_points().items())]
        inputs = [charts.divisional_positions_from_rasi_positions(natal, factor, 1) for factor in (1, 9, 10, 144)]
        inputs.append(charts.mixed_chart_from_rasi_positions(natal, 10, 1, 9, 1))
        results = []
        for positions in inputs:
            longitudes = {body: sign * 30 + degree for body, (sign, degree) in positions}
            points = {source: longitudes[source] for source in range(9)}
            result = aspects.jhora8_parasara_aspects(points, ascendant_longitude=longitudes["L"], normalize_as_percentage=False)
            results.append(result)
            for source, row in result.items():
                for target in range(9):
                    if source != target:
                        self.assertEqual(row[target], reference((points[target] - points[source]) % 360, source))
                for house in range(1, 13):
                    angle = (longitudes["L"] + 30 * (house - 1) - points[source]) % 360
                    self.assertEqual(row["H%d" % house], reference(angle, source))
        self.assertTrue(all(result != results[0] for result in results[1:]))

    def test_opt_in_calculation_leaves_legacy_strength_results_and_settings_unchanged(self) -> None:
        from jhora import const
        from jhora.horoscope.chart import strength
        from jhora.panchanga import drik

        points = synthetic_points()
        positions = [["L", [0, 17.125]]] + [[source, [int(longitude // 30), longitude % 30]] for source, longitude in points.items()]
        settings = (const._DEFAULT_AYANAMSA_MODE, const._RAHU, const._KETU, drik.planet_list)
        previous = [
            strength.planet_aspect_relationship_table(positions, True),
            strength.planet_aspect_relationship_table_pvr(positions, True),
        ]
        native = aspects.jhora8_parasara_aspects(points, ascendant_longitude=17.125)
        self.assertNotEqual(native[2][4], previous[1][2][4])
        self.assertEqual(strength.planet_aspect_relationship_table(positions, True), previous[0])
        self.assertEqual(strength.planet_aspect_relationship_table_pvr(positions, True), previous[1])
        self.assertEqual(settings, (const._DEFAULT_AYANAMSA_MODE, const._RAHU, const._KETU, drik.planet_list))


if __name__ == "__main__":
    unittest.main()
