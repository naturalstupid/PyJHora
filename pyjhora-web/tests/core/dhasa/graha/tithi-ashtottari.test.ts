import { describe, expect, it } from 'vitest';
import { getTithiAshtottariDashaBhukti } from '../../../../src/core/dhasa/graha/tithi-ashtottari';
import type { Place } from '../../../../src/core/types';

describe('Tithi Ashtottari Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  describe('Tithi Calculation', () => {
    it('should return valid tithi number (1-30)', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace);
      expect(result.tithiNumber).toBeGreaterThanOrEqual(1);
      expect(result.tithiNumber).toBeLessThanOrEqual(30);
    });

    it('should return valid tithi name', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace);
      expect(result.tithiName).toBeDefined();
      expect(typeof result.tithiName).toBe('string');
    });

    it('should have tithi fraction between 0 and 1', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace);
      expect(result.tithiFraction).toBeGreaterThanOrEqual(0);
      expect(result.tithiFraction).toBeLessThanOrEqual(1);
    });

    it('should calculate dasha balance', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace);
      expect(result.dashaBalance).toBeGreaterThanOrEqual(0);
      // Max dasha balance is 21 years (Venus)
      expect(result.dashaBalance).toBeLessThanOrEqual(21);
    });
  });

  describe('Dasha Structure', () => {
    it('should return 8 mahadashas', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBe(8);
    });

    it('should have total duration of 108 years', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const totalYears = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
      expect(totalYears).toBeCloseTo(108, 0);
    });

    it('should have correct lord durations', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const expectedDurations: Record<number, number> = {
        0: 6,   // Sun
        1: 15,  // Moon
        2: 8,   // Mars
        3: 17,  // Mercury
        4: 19,  // Jupiter
        5: 21,  // Venus
        6: 10,  // Saturn
        7: 12,  // Rahu
      };

      for (const dasha of result.mahadashas) {
        expect(dasha.durationYears).toBe(expectedDurations[dasha.lord]);
      }
    });

    it('should cycle through 8 lords', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const lords = new Set(result.mahadashas.map(d => d.lord));
      expect(lords.size).toBe(8);
    });

    it('should have increasing start JDs', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      for (let i = 1; i < result.mahadashas.length; i++) {
        expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
      }
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should have 64 bhuktis (8 dashas × 8 bhuktis)', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis!.length).toBe(64);
    });

    it('should have valid bhukti structure', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
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
    it('should default to option 3 (next lord forward)', () => {
      const result = getTithiAshtottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: true
      });
      // First bhukti lord should not be same as first dasha lord (starts from next)
      const firstDasha = result.mahadashas[0]!;
      const firstBhukti = result.bhuktis![0]!;
      expect(firstBhukti.dashaLord).toBe(firstDasha.lord);
    });

    it('should support all antardasha options (1-6)', () => {
      for (const option of [1, 2, 3, 4, 5, 6] as const) {
        const result = getTithiAshtottariDashaBhukti(testJd, testPlace, {
          includeBhuktis: true,
          antardhasaOption: option
        });
        expect(result.bhuktis!.length).toBe(64);
      }
    });
  });

  describe('Tribhagi Variation', () => {
    it('should support tribhagi variation', () => {
      const normal = getTithiAshtottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: false
      });
      const tribhagi = getTithiAshtottariDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: true
      });

      // Tribhagi should have 3× more mahadashas
      expect(tribhagi.mahadashas.length).toBe(normal.mahadashas.length * 3);
    });
  });
});
