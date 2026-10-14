"""Varnada chart-context regressions using synthetic Ascendant/Hora positions."""
import unittest
from unittest.mock import patch

from jhora import const
from jhora.panchanga import drik
from jhora.horoscope.chart import charts


class VarnadaCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.date = drik.Date(2000, 1, 1)
        self.time = (12, 0, 0)
        self.place = drik.Place('Synthetic', 0, 0, 0, elevation=0)
        self.asc = patch.object(charts, 'rasi_chart', return_value=[['L', [7, 12.5]]])
        self.hora = patch.object(drik, 'hora_lagna', return_value=[2, 10.0])
        self.asc.start()
        self.hora.start()
        self.addCleanup(self.asc.stop)
        self.addCleanup(self.hora.stop)

    def calculate(self, factor, compatible=True, **kwargs):
        return charts.varnada_lagna_longitudes(
            self.date, self.time, self.place, factor, 1,
            varnada_method=const.VARNADA_METHOD.BV_RAMAN, jhora_compatible=compatible, **kwargs)

    def test_navamsa_recomputes_signs_in_chart_context(self):
        expected_signs = [3, 4, 7, 8, 11, 0, 3, 4, 7, 8, 11, 0]
        expected = [[f'V{i+1}', [sign, 22.5]] for i, sign in enumerate(expected_signs)]
        self.assertEqual(self.calculate(9), expected)

    def test_mixed_chart_applies_second_chart_to_first_context(self):
        result = charts.varnada_lagna_longitudes_mixed_chart(
            self.date, self.time, self.place, 10, 1, 9, 1,
            varnada_method=const.VARNADA_METHOD.BV_RAMAN, jhora_compatible=True)
        self.assertEqual(result, [[f'V{i+1}', [1 if i % 2 == 0 else 4, 15.0]] for i in range(12)])

    def test_opt_out_preserves_existing_natal_projection(self):
        natal = self.calculate(1, compatible=False)
        expected = charts.divisional_positions_from_rasi_positions(natal, 9, 1)
        self.assertEqual(self.calculate(9, compatible=False), expected)
        self.assertNotEqual(self.calculate(9), expected)

    def test_rasi_is_identical_in_both_modes(self):
        self.assertEqual(self.calculate(1), self.calculate(1, compatible=False))

    def test_zero_chart_is_a_zero_degree_placeholder(self):
        result = self.calculate(0)
        self.assertEqual([value[1] for _, value in result], [0.0] * 12)
        self.assertEqual([value[0] for _, value in result], [1, 2, 5, 6, 9, 10, 1, 2, 5, 6, 9, 10])

    def test_compatibility_rejects_unverified_varnada_method(self):
        with self.assertRaisesRegex(ValueError, 'only for BV Raman'):
            charts.varnada_lagna_longitudes(self.date, self.time, self.place,
                varnada_method=const.VARNADA_METHOD.SANJAY_RATH, jhora_compatible=True)


if __name__ == '__main__':
    unittest.main()
