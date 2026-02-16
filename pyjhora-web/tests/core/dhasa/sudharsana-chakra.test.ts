/**
 * Tests for Sudharsana Chakra Dhasa System.
 */
import { describe, expect, it } from 'vitest';
import {
  sudharsanaChakraChart,
  getSudharsanaChakraDhasa,
  sudharsanaPratyantardasas,
} from '../../../src/core/dhasa/sudharsana-chakra';
import type { PlanetPosition } from '../../../src/core/horoscope/charts';
import { SIDEREAL_YEAR, RASI_NAMES_EN } from '../../../src/core/constants';

const mockPositions: PlanetPosition[] = [
  { planet: -1, rasi: 3, longitude: 15.0 },  // Lagna (Cancer)
  { planet: 0, rasi: 7, longitude: 12.5 },   // Sun (Scorpio)
  { planet: 1, rasi: 1, longitude: 22.3 },   // Moon (Taurus)
  { planet: 2, rasi: 9, longitude: 5.0 },    // Mars (Capricorn)
  { planet: 3, rasi: 8, longitude: 28.7 },   // Mercury (Sagittarius)
  { planet: 4, rasi: 2, longitude: 18.0 },   // Jupiter (Gemini)
  { planet: 5, rasi: 10, longitude: 9.5 },   // Venus (Aquarius)
  { planet: 6, rasi: 6, longitude: 1.2 },    // Saturn (Libra)
  { planet: 7, rasi: 5, longitude: 20.1 },   // Rahu
  { planet: 8, rasi: 11, longitude: 20.1 },  // Ketu
];

const jd = 2450424.0;

describe('Sudharsana Chakra', () => {
  describe('sudharsanaChakraChart', () => {
    it('should produce 3 charts with 12 entries each', () => {
      const result = sudharsanaChakraChart(mockPositions);
      expect(result.lagnaChart).toHaveLength(12);
      expect(result.moonChart).toHaveLength(12);
      expect(result.sunChart).toHaveLength(12);
    });

    it('should start lagna chart from Lagna house', () => {
      const result = sudharsanaChakraChart(mockPositions);
      // Lagna is Cancer(3), so first entry sign should be 3
      expect(result.lagnaChart[0]![0]).toBe(3);
    });

    it('should start moon chart from Moon house', () => {
      const result = sudharsanaChakraChart(mockPositions);
      // Moon is Taurus(1), so first entry sign should be 1
      expect(result.moonChart[0]![0]).toBe(1);
    });

    it('should start sun chart from Sun house', () => {
      const result = sudharsanaChakraChart(mockPositions);
      // Sun is Scorpio(7), so first entry sign should be 7
      expect(result.sunChart[0]![0]).toBe(7);
    });

    it('should return retrograde planets array', () => {
      const result = sudharsanaChakraChart(mockPositions);
      expect(Array.isArray(result.retrogradePlanets)).toBe(true);
    });

    it('should have sign indices in range 0-11', () => {
      const result = sudharsanaChakraChart(mockPositions);
      for (const [sign] of result.lagnaChart) {
        expect(sign).toBeGreaterThanOrEqual(0);
        expect(sign).toBeLessThanOrEqual(11);
      }
    });
  });

  describe('getSudharsanaChakraDhasa', () => {
    it('should produce 12 periods each for lagna, moon, and sun', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      expect(result.lagnaPeriods).toHaveLength(12);
      expect(result.moonPeriods).toHaveLength(12);
      expect(result.sunPeriods).toHaveLength(12);
    });

    it('should have each period lasting one sidereal year', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      for (const p of result.lagnaPeriods) {
        expect(p.durationDays).toBeCloseTo(SIDEREAL_YEAR, 2);
      }
    });

    it('should have 12 antardhasas per period', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      for (const p of result.lagnaPeriods) {
        expect(p.antardhasas).toHaveLength(12);
      }
    });

    it('should have consecutive end dates', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      for (let i = 1; i < result.lagnaPeriods.length; i++) {
        expect(result.lagnaPeriods[i]!.endJd).toBeGreaterThan(
          result.lagnaPeriods[i - 1]!.endJd
        );
      }
    });

    it('should have valid sign names', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      for (const p of result.moonPeriods) {
        expect(RASI_NAMES_EN).toContain(p.signName);
      }
    });

    it('should progress through all 12 signs in order', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      const signs = result.lagnaPeriods.map(p => p.sign);
      // Each consecutive sign should be prev + 1 (mod 12)
      for (let i = 1; i < signs.length; i++) {
        expect(signs[i]).toBe((signs[i - 1]! + 1) % 12);
      }
    });

    it('should have valid date strings', () => {
      const result = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      for (const p of result.sunPeriods) {
        expect(p.endDate).toMatch(/^\d{4}-\d{2}-\d{2}/);
      }
    });

    it('should shift seed sign based on yearsFromDob', () => {
      const r1 = getSudharsanaChakraDhasa(mockPositions, jd, 1);
      const r5 = getSudharsanaChakraDhasa(mockPositions, jd, 5);
      // The seed sign shifts by yearsFromDob difference
      const diff = (r5.lagnaPeriods[0]!.sign - r1.lagnaPeriods[0]!.sign + 12) % 12;
      expect(diff).toBe(4); // 5 - 1 = 4
    });
  });

  describe('sudharsanaPratyantardasas', () => {
    it('should produce 12 pratyantardasas', () => {
      const result = sudharsanaPratyantardasas(jd, 0);
      expect(result).toHaveLength(12);
    });

    it('should progress through 12 signs from seed', () => {
      const seed = 5; // Virgo
      const result = sudharsanaPratyantardasas(jd, seed);
      for (let i = 0; i < 12; i++) {
        expect(result[i]!.sign).toBe((seed + i) % 12);
      }
    });

    it('should have positive durations', () => {
      const result = sudharsanaPratyantardasas(jd, 0);
      for (const p of result) {
        expect(p.durationDays).toBeGreaterThan(0);
      }
    });

    it('should have total duration close to 1/12 of a sidereal year', () => {
      const result = sudharsanaPratyantardasas(jd, 0);
      const total = result.reduce((acc, p) => acc + p.durationDays, 0);
      // 12 * (sidereal_year / 144) = sidereal_year / 12
      expect(total).toBeCloseTo(SIDEREAL_YEAR / 12, 0);
    });

    it('should have valid sign names', () => {
      const result = sudharsanaPratyantardasas(jd, 3);
      for (const p of result) {
        expect(RASI_NAMES_EN).toContain(p.signName);
      }
    });
  });
});
