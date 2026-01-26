import { describe, expect, it } from 'vitest';
import { getTithiYoginiDashaBhukti } from '../../../../src/core/dhasa/graha/tithi-yogini';
import type { Place } from '../../../../src/core/types';

describe('Tithi Yogini Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  describe('Tithi Calculation', () => {
    it('should return valid tithi number (1-30)', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace);
      expect(result.tithiNumber).toBeGreaterThanOrEqual(1);
      expect(result.tithiNumber).toBeLessThanOrEqual(30);
    });

    it('should return valid tithi name', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace);
      expect(result.tithiName).toBeDefined();
      expect(typeof result.tithiName).toBe('string');
    });

    it('should have tithi fraction between 0 and 1', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace);
      expect(result.tithiFraction).toBeGreaterThanOrEqual(0);
      expect(result.tithiFraction).toBeLessThanOrEqual(1);
    });

    it('should calculate dasha balance', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace);
      expect(result.dashaBalance).toBeGreaterThanOrEqual(0);
      // Max dasha balance is 8 years (Rahu)
      expect(result.dashaBalance).toBeLessThanOrEqual(8);
    });
  });

  describe('Dasha Structure', () => {
    it('should return 24 mahadashas (8 lords × 3 cycles)', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBe(24); // 8 lords × 3 cycles
    });

    it('should have total duration of 108 years (36 × 3)', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const totalYears = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
      expect(totalYears).toBeCloseTo(108, 0);
    });

    it('should have correct lord durations (1-8 years)', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const expectedDurations: Record<number, number> = {
        0: 2,   // Sun
        1: 1,   // Moon
        2: 4,   // Mars
        3: 5,   // Mercury
        4: 3,   // Jupiter
        5: 7,   // Venus
        6: 6,   // Saturn
        7: 8,   // Rahu
      };

      for (const dasha of result.mahadashas) {
        expect(dasha.durationYears).toBe(expectedDurations[dasha.lord]);
      }
    });

    it('should cycle through 8 lords three times', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const firstCycle = result.mahadashas.slice(0, 8).map(d => d.lord);
      const secondCycle = result.mahadashas.slice(8, 16).map(d => d.lord);
      const thirdCycle = result.mahadashas.slice(16, 24).map(d => d.lord);

      // Each cycle should have the same lord sequence
      expect(firstCycle).toEqual(secondCycle);
      expect(secondCycle).toEqual(thirdCycle);
    });

    it('should have increasing start JDs', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      for (let i = 1; i < result.mahadashas.length; i++) {
        expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
      }
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should have 192 bhuktis (24 dashas × 8 bhuktis)', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis!.length).toBe(192);
    });

    it('should have valid bhukti structure', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      const firstBhukti = result.bhuktis![0]!;

      expect(firstBhukti.dashaLord).toBeDefined();
      expect(firstBhukti.dashaLordName).toBeDefined();
      expect(firstBhukti.bhuktiLord).toBeDefined();
      expect(firstBhukti.bhuktiLordName).toBeDefined();
      expect(firstBhukti.startJd).toBeDefined();
      expect(firstBhukti.startDate).toBeDefined();
      expect(firstBhukti.durationYears).toBeGreaterThan(0);
    });

    it('should have equal bhukti durations within a dasha', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      const firstDashaLord = result.mahadashas[0]!.lord;
      const firstDashaBhuktis = result.bhuktis!.filter(b => b.dashaLord === firstDashaLord);

      // All bhuktis in a dasha should have equal duration
      const durations = firstDashaBhuktis.map(b => b.durationYears);
      const firstDuration = durations[0]!;
      for (const dur of durations) {
        expect(dur).toBeCloseTo(firstDuration, 5);
      }
    });
  });

  describe('Antardasha Options', () => {
    it('should default to option 1 (dasha lord forward)', () => {
      const result = getTithiYoginiDashaBhukti(testJd, testPlace, {
        includeBhuktis: true
      });
      expect(result.bhuktis!.length).toBe(192);
    });

    it('should support all antardasha options (1-6)', () => {
      for (const option of [1, 2, 3, 4, 5, 6] as const) {
        const result = getTithiYoginiDashaBhukti(testJd, testPlace, {
          includeBhuktis: true,
          antardhasaOption: option
        });
        expect(result.bhuktis!.length).toBe(192);
      }
    });
  });

  describe('Tribhagi Variation', () => {
    it('should support tribhagi variation', () => {
      const normal = getTithiYoginiDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: false
      });
      const tribhagi = getTithiYoginiDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: true
      });

      // Tribhagi should have 3× more mahadashas
      expect(tribhagi.mahadashas.length).toBe(normal.mahadashas.length * 3);
    });
  });
});
