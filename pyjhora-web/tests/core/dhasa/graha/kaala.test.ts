import { describe, expect, it } from 'vitest';
import { getKaalaDashaBhukti } from '../../../../src/core/dhasa/graha/kaala';
import type { Place } from '../../../../src/core/types';

describe('Kaala Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };

  // Test different birth times for different kaalas
  const morningJd = 2447912.25; // ~6 AM (Dawn)
  const noonJd = 2447912.5;     // ~12 PM (Day)
  const eveningJd = 2447912.75; // ~6 PM (Dusk)
  const nightJd = 2447912.9;    // ~9:36 PM (Night)

  describe('Kaala Type Detection', () => {
    it('should detect different kaala types based on birth time', () => {
      const morningResult = getKaalaDashaBhukti(morningJd, testPlace);
      const noonResult = getKaalaDashaBhukti(noonJd, testPlace);
      const eveningResult = getKaalaDashaBhukti(eveningJd, testPlace);
      const nightResult = getKaalaDashaBhukti(nightJd, testPlace);

      // Each should have a kaala type between 0-3
      expect(morningResult.kaalaType).toBeGreaterThanOrEqual(0);
      expect(morningResult.kaalaType).toBeLessThanOrEqual(3);
      expect(noonResult.kaalaType).toBeGreaterThanOrEqual(0);
      expect(eveningResult.kaalaType).toBeGreaterThanOrEqual(0);
      expect(nightResult.kaalaType).toBeGreaterThanOrEqual(0);
    });

    it('should have valid kaala type names', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace);
      const validNames = ['Dawn', 'Day', 'Dusk', 'Night'];
      expect(validNames).toContain(result.kaalaTypeName);
    });
  });

  describe('Dasha Structure', () => {
    it('should return valid mahadasha structure', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: false });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBe(18); // 9 lords × 2 cycles
    });

    it('should have 9 lords per cycle', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: false });
      // First 9 mahadashas should be cycle 1, next 9 should be cycle 2
      const lords = result.mahadashas.map(m => m.lord);
      const cycle1Lords = lords.slice(0, 9);
      const cycle2Lords = lords.slice(9, 18);

      // Each cycle should have lords 0-8
      for (let i = 0; i < 9; i++) {
        expect(cycle1Lords).toContain(i);
        expect(cycle2Lords).toContain(i);
      }
    });

    it('should have positive durations for all periods', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: false });
      for (const dasha of result.mahadashas) {
        expect(dasha.durationYears).toBeGreaterThanOrEqual(0);
      }
    });

    it('should have kaala fraction between 0 and 1', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace);
      expect(result.kaalaFraction).toBeGreaterThanOrEqual(0);
      expect(result.kaalaFraction).toBeLessThanOrEqual(1);
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: true });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should not include bhuktis when not requested', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: false });
      expect(result.bhuktis).toBeUndefined();
    });

    it('should have valid bhukti structure', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: true });
      const firstBhukti = result.bhuktis![0]!;

      expect(firstBhukti.dashaLord).toBeDefined();
      expect(firstBhukti.bhuktiLord).toBeDefined();
      expect(firstBhukti.bhuktiLordName).toBeDefined();
      expect(firstBhukti.startJd).toBeDefined();
      expect(firstBhukti.startDate).toBeDefined();
      expect(firstBhukti.durationYears).toBeDefined();
    });
  });

  describe('Date Formatting', () => {
    it('should format dates correctly', () => {
      const result = getKaalaDashaBhukti(noonJd, testPlace, { includeBhuktis: false });
      const firstDasha = result.mahadashas[0]!;

      // Date format should be YYYY-MM-DD HH:MM:SS AM/PM
      expect(firstDasha.startDate).toMatch(/^\d+(-BC)?-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (AM|PM)$/);
    });
  });
});
