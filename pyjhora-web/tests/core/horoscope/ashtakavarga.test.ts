/**
 * Ashtakavarga Tests
 * Test cases from PyJHora ashtakavarga.py
 */

import { describe, it, expect } from 'vitest';
import {
  getAshtakavarga,
  sodhayaPindas,
  getPlanetToHouseFromChart,
  trikonaSodhana,
  ekadhipatyaSodhana,
  getCompleteAshtakavarga
} from '../../../src/core/horoscope/ashtakavarga';

describe('Ashtakavarga', () => {
  // Chart 7 from PVR book - test case from Python
  // ['6/1/7','','','','','','8/4','L','3/2','0','5','']
  // House 0 (Aries): Saturn(6), Moon(1), Rahu(7)
  // House 6 (Libra): Ketu(8), Jupiter(4)
  // House 7 (Scorpio): Lagna
  // House 8 (Sagittarius): Mercury(3), Mars(2)
  // House 9 (Capricorn): Sun(0)
  // House 10 (Aquarius): Venus(5)
  const chart7 = ['6/1/7', '', '', '', '', '', '8/4', 'L', '3/2', '0', '5', ''];

  describe('getPlanetToHouseFromChart', () => {
    it('should correctly parse house chart to planet positions', () => {
      const pToH = getPlanetToHouseFromChart(chart7);

      expect(pToH[0]).toBe(9); // Sun in Capricorn
      expect(pToH[1]).toBe(0); // Moon in Aries
      expect(pToH[2]).toBe(8); // Mars in Sagittarius
      expect(pToH[3]).toBe(8); // Mercury in Sagittarius
      expect(pToH[4]).toBe(6); // Jupiter in Libra
      expect(pToH[5]).toBe(10); // Venus in Aquarius
      expect(pToH[6]).toBe(0); // Saturn in Aries
      expect(pToH[7]).toBe(0); // Rahu in Aries
      expect(pToH[8]).toBe(6); // Ketu in Libra
      expect(pToH['L']).toBe(7); // Lagna in Scorpio
    });
  });

  describe('getAshtakavarga', () => {
    it('should calculate correct Binna Ashtakavarga values', () => {
      const result = getAshtakavarga(chart7);

      // Expected BAV from Python test (Sun to Saturn, excluding Lagna)
      const expectedBav = [
        [4, 2, 3, 4, 6, 5, 5, 3, 2, 6, 6, 2], // Sun
        [6, 3, 5, 3, 5, 5, 6, 3, 3, 4, 4, 2], // Moon
        [3, 2, 3, 4, 2, 5, 4, 3, 3, 4, 3, 3], // Mars
        [4, 6, 4, 3, 4, 7, 4, 5, 6, 3, 5, 3], // Mercury
        [4, 4, 3, 5, 6, 5, 6, 4, 6, 4, 3, 6], // Jupiter
        [3, 5, 5, 4, 6, 2, 3, 6, 5, 2, 7, 4], // Venus
        [3, 2, 2, 3, 5, 6, 3, 4, 1, 3, 6, 1]  // Saturn
      ];

      // Check planets 0-6 (Sun to Saturn)
      for (let p = 0; p < 7; p++) {
        expect(result.binnaAshtakavarga[p]).toEqual(expectedBav[p]);
      }
    });

    it('should calculate correct Sarva Ashtakavarga values', () => {
      const result = getAshtakavarga(chart7);

      // Expected SAV from Python test
      const expectedSav = [27, 24, 25, 26, 34, 35, 31, 28, 26, 26, 34, 21];

      expect(result.sarvaAshtakavarga).toEqual(expectedSav);
    });
  });

  describe('sodhayaPindas', () => {
    it('should calculate correct Sodhya Pindas', () => {
      const avResult = getAshtakavarga(chart7);
      const pindas = sodhayaPindas(avResult.binnaAshtakavarga, chart7);

      // Expected values from Python test
      // Note: Python test has slight discrepancy with book values
      const expectedRaasiPindas = [155, 92, 55, 99, 93, 154, 166];
      const expectedGrahaPindas = [81, 55, 43, 33, 56, 54, 63];
      const expectedSodhyaPindas = [236, 147, 98, 132, 149, 208, 229];

      expect(pindas.raasiPindas).toEqual(expectedRaasiPindas);
      expect(pindas.grahaPindas).toEqual(expectedGrahaPindas);
      expect(pindas.sodhyaPindas).toEqual(expectedSodhyaPindas);
    });
  });

  describe('trikonaSodhana', () => {
    it('should apply trikona reduction correctly', () => {
      const avResult = getAshtakavarga(chart7);
      const reduced = trikonaSodhana(avResult.binnaAshtakavarga);

      // After trikona, all trine groups should have at least one zero
      // or have had minimum subtracted
      for (let p = 0; p < 7; p++) {
        for (let r = 0; r < 4; r++) {
          const v1 = reduced[p][r] ?? 0;
          const v2 = reduced[p][r + 4] ?? 0;
          const v3 = reduced[p][r + 8] ?? 0;

          // If none are zero, they must have been equal and zeroed
          // or had minimum subtracted (so one should now be zero)
          if (v1 > 0 && v2 > 0 && v3 > 0) {
            // This shouldn't happen after trikona sodhana
            // unless original had at least one zero
            const orig1 = avResult.binnaAshtakavarga[p][r] ?? 0;
            const orig2 = avResult.binnaAshtakavarga[p][r + 4] ?? 0;
            const orig3 = avResult.binnaAshtakavarga[p][r + 8] ?? 0;
            expect(orig1 === 0 || orig2 === 0 || orig3 === 0).toBe(true);
          }
        }
      }
    });
  });

  describe('ekadhipatyaSodhana', () => {
    it('should apply ekadhipatya reduction correctly', () => {
      const avResult = getAshtakavarga(chart7);
      const afterTrikona = trikonaSodhana(avResult.binnaAshtakavarga);
      const reduced = ekadhipatyaSodhana(afterTrikona, chart7);

      // The result should be defined
      expect(reduced).toBeDefined();
      expect(reduced.length).toBe(8);

      // Each planet row should have 12 values
      for (let p = 0; p < 8; p++) {
        expect(reduced[p]?.length).toBe(12);
      }
    });
  });

  describe('getCompleteAshtakavarga', () => {
    it('should return complete analysis', () => {
      const result = getCompleteAshtakavarga(chart7);

      expect(result.binnaAshtakavarga).toBeDefined();
      expect(result.sarvaAshtakavarga).toBeDefined();
      expect(result.prastaraAshtakavarga).toBeDefined();
      expect(result.sodhyaPindas).toBeDefined();

      expect(result.binnaAshtakavarga.length).toBe(8);
      expect(result.sarvaAshtakavarga.length).toBe(12);
      expect(result.prastaraAshtakavarga.length).toBe(8);
    });
  });

  describe('Edge cases', () => {
    it('should handle empty chart gracefully', () => {
      const emptyChart = ['', '', '', '', '', '', '', '', '', '', '', ''];
      const result = getAshtakavarga(emptyChart);

      // Should still return valid structure
      expect(result.binnaAshtakavarga.length).toBe(8);
      expect(result.sarvaAshtakavarga.length).toBe(12);
    });

    it('should handle chart with only Lagna', () => {
      const lagnaOnlyChart = ['', '', '', '', '', '', '', 'L', '', '', '', ''];
      const result = getAshtakavarga(lagnaOnlyChart);

      expect(result.binnaAshtakavarga.length).toBe(8);
      // Lagna's BAV should have some values
      expect(result.binnaAshtakavarga[7]).toBeDefined();
    });
  });
});
