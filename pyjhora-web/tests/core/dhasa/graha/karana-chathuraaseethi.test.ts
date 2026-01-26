import { describe, expect, it } from 'vitest';
import { getKaranaChathuraaseethiDashaBhukti } from '../../../../src/core/dhasa/graha/karana-chathuraaseethi';
import type { Place } from '../../../../src/core/types';

describe('Karana Chathuraaseethi Sama Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  describe('Karana Calculation', () => {
    it('should return valid karana number (1-60)', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace);
      expect(result.karanaNumber).toBeGreaterThanOrEqual(1);
      expect(result.karanaNumber).toBeLessThanOrEqual(60);
    });

    it('should return valid karana name', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace);
      expect(result.karanaName).toBeDefined();
      expect(typeof result.karanaName).toBe('string');
    });

    it('should have karana fraction between 0 and 1', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace);
      expect(result.karanaFraction).toBeGreaterThanOrEqual(0);
      expect(result.karanaFraction).toBeLessThanOrEqual(1);
    });

    it('should calculate dasha balance', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace);
      expect(result.dashaBalance).toBeGreaterThanOrEqual(0);
      // Max dasha balance is 12 years
      expect(result.dashaBalance).toBeLessThanOrEqual(12);
    });
  });

  describe('Dasha Structure', () => {
    it('should return 7 mahadashas', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBe(7);
    });

    it('should have total duration of 84 years (7 × 12)', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const totalYears = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
      expect(totalYears).toBeCloseTo(84, 0);
    });

    it('should have 12 years for each dasha', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      for (const dasha of result.mahadashas) {
        expect(dasha.durationYears).toBe(12);
      }
    });

    it('should use only Sun to Saturn (lords 0-6)', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      for (const dasha of result.mahadashas) {
        expect(dasha.lord).toBeGreaterThanOrEqual(0);
        expect(dasha.lord).toBeLessThanOrEqual(6);
      }
    });

    it('should not include Rahu or Ketu', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      const lords = result.mahadashas.map(d => d.lord);
      expect(lords).not.toContain(7); // Rahu
      expect(lords).not.toContain(8); // Ketu
    });

    it('should have increasing start JDs', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
      for (let i = 1; i < result.mahadashas.length; i++) {
        expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
      }
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should have 49 bhuktis (7 dashas × 7 bhuktis)', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis!.length).toBe(49);
    });

    it('should have valid bhukti structure', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
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
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      const firstDashaLord = result.mahadashas[0]!.lord;
      const firstDashaBhuktis = result.bhuktis!.filter(b => b.dashaLord === firstDashaLord);

      // All bhuktis in a dasha should have duration 12/7 years
      const expectedDuration = 12 / 7;
      for (const bhukti of firstDashaBhuktis) {
        expect(bhukti.durationYears).toBeCloseTo(expectedDuration, 5);
      }
    });

    it('should only use lords 0-6 in bhuktis', () => {
      const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
      for (const bhukti of result.bhuktis!) {
        expect(bhukti.bhuktiLord).toBeGreaterThanOrEqual(0);
        expect(bhukti.bhuktiLord).toBeLessThanOrEqual(6);
      }
    });
  });

  describe('Antardasha Options', () => {
    it('should support all antardasha options (1-6)', () => {
      for (const option of [1, 2, 3, 4, 5, 6] as const) {
        const result = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, {
          includeBhuktis: true,
          antardhasaOption: option
        });
        expect(result.bhuktis!.length).toBe(49);
      }
    });
  });

  describe('Tribhagi Variation', () => {
    it('should support tribhagi variation', () => {
      const normal = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: false
      });
      const tribhagi = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: true
      });

      // Tribhagi should have 3× more mahadashas
      expect(tribhagi.mahadashas.length).toBe(normal.mahadashas.length * 3);
    });

    it('should have 4 year durations in tribhagi variation', () => {
      const tribhagi = getKaranaChathuraaseethiDashaBhukti(testJd, testPlace, {
        includeBhuktis: false,
        useTribhagiVariation: true
      });

      for (const dasha of tribhagi.mahadashas) {
        expect(dasha.durationYears).toBe(4); // 12/3 = 4
      }
    });
  });
});
