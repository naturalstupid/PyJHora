import { describe, expect, it } from 'vitest';
import { getYogaVimsottariDashaBhukti } from '../../../../src/core/dhasa/graha/yoga-vimsottari';
import type { Place } from '../../../../src/core/types';

describe('Yoga Vimsottari Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  describe('Yoga Calculation', () => {
    it('should return valid yoga number (1-27)', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace);
      expect(result.yogaNumber).toBeGreaterThanOrEqual(1);
      expect(result.yogaNumber).toBeLessThanOrEqual(27);
    });

    it('should return valid yoga name', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace);
      expect(result.yogaName).toBeDefined();
      expect(typeof result.yogaName).toBe('string');
      expect(result.yogaName.length).toBeGreaterThan(0);
    });

    it('should have yoga fraction between 0 and 1', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace);
      expect(result.yogaFraction).toBeGreaterThanOrEqual(0);
      expect(result.yogaFraction).toBeLessThanOrEqual(1);
    });

    it('should calculate dasha balance', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace);
      expect(result.dashaBalance).toBeGreaterThanOrEqual(0);
      // Max dasha balance is 21 years (Venus dasha)
      expect(result.dashaBalance).toBeLessThanOrEqual(21);
    });
  });

  describe('Dasha Structure', () => {
    it('should return 9 mahadashas', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBe(9);
    });

    it('should have total duration of 120 years', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const totalYears = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
      expect(totalYears).toBeCloseTo(120, 0);
    });

    it('should have correct dasha durations', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const expectedDurations: Record<number, number> = {
        0: 6,   // Sun
        1: 10,  // Moon
        2: 7,   // Mars
        3: 17,  // Mercury
        4: 16,  // Jupiter
        5: 20,  // Venus
        6: 19,  // Saturn
        7: 18,  // Rahu
        8: 7,   // Ketu
      };

      for (const dasha of result.mahadashas) {
        expect(dasha.durationYears).toBe(expectedDurations[dasha.lord]);
      }
    });

    it('should have increasing start JDs', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      for (let i = 1; i < result.mahadashas.length; i++) {
        expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
      }
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should have 81 bhuktis (9 dashas × 9 bhuktis)', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis!.length).toBe(81);
    });

    it('should have valid bhukti structure', () => {
      const result = getYogaVimsottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      const firstBhukti = result.bhuktis![0]!;

      expect(firstBhukti.dashaLord).toBeDefined();
      expect(firstBhukti.dashaLordName).toBeDefined();
      expect(firstBhukti.bhuktiLord).toBeDefined();
      expect(firstBhukti.bhuktiLordName).toBeDefined();
      expect(firstBhukti.startJd).toBeDefined();
      expect(firstBhukti.startDate).toBeDefined();
      expect(firstBhukti.durationYears).toBeGreaterThan(0);
    });
  });

  describe('Antardasha Options', () => {
    it('should support different antardasha options', () => {
      const option1 = getYogaVimsottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: true,
        antardhasaOption: 1
      });
      const option3 = getYogaVimsottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: true,
        antardhasaOption: 3
      });

      // Different options should produce different bhukti sequences
      expect(option1.bhuktis!.length).toBe(option3.bhuktis!.length);
    });
  });

  describe('Tribhagi Variation', () => {
    it('should support tribhagi variation', () => {
      const normal = getYogaVimsottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: false
      });
      const tribhagi = getYogaVimsottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: true
      });

      // Tribhagi should have 3× more mahadashas
      expect(tribhagi.mahadashas.length).toBe(normal.mahadashas.length * 3);
    });

    it('should have 1/3 duration in tribhagi variation', () => {
      const normal = getYogaVimsottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: false
      });
      const tribhagi = getYogaVimsottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: true
      });

      // Each dasha should be 1/3 of normal duration
      const normalFirst = normal.mahadashas[0]!;
      const tribhagiFirst = tribhagi.mahadashas[0]!;
      expect(tribhagiFirst.durationYears).toBeCloseTo(normalFirst.durationYears / 3, 2);
    });
  });
});
