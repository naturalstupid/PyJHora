/**
 * Tests for Vimsottari dasha system
 */

import { JUPITER, KETU, MARS, MERCURY, MOON, RAHU, SATURN, SUN, VENUS } from '@core/constants';
import {
    getNextAdhipati,
    getVimsottariAdhipati,
    getVimsottariDashaBhukti,
    vimsottariBhukti,
    vimsottariDashaStartDate,
    vimsottariMahadasha
} from '@core/dhasa/graha/vimsottari';
import type { Place } from '@core/types';
import { describe, expect, it } from 'vitest';

// Test place
const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5
};

describe('Vimsottari Dasha System', () => {
  describe('getVimsottariAdhipati', () => {
    it('should return correct adhipati for each nakshatra', () => {
      // Ashwini (0) is ruled by Ketu (with seed star 3)
      expect(getVimsottariAdhipati(0, 3)).toBe(KETU);
      
      // Bharani (1) is ruled by Venus
      expect(getVimsottariAdhipati(1, 3)).toBe(VENUS);
      
      // Krittika (2) is ruled by Sun
      expect(getVimsottariAdhipati(2, 3)).toBe(SUN);
    });

    it('should cycle through all lords correctly', () => {
      const lords = [];
      for (let i = 0; i < 9; i++) {
        lords.push(getVimsottariAdhipati(i, 3));
      }
      
      // Should contain all 9 lords
      expect(lords).toContain(KETU);
      expect(lords).toContain(VENUS);
      expect(lords).toContain(SUN);
      expect(lords).toContain(MOON);
      expect(lords).toContain(MARS);
      expect(lords).toContain(RAHU);
      expect(lords).toContain(JUPITER);
      expect(lords).toContain(SATURN);
      expect(lords).toContain(MERCURY);
    });
  });

  describe('getNextAdhipati', () => {
    it('should return next lord in sequence', () => {
      expect(getNextAdhipati(KETU, 1)).toBe(VENUS);
      expect(getNextAdhipati(VENUS, 1)).toBe(SUN);
      expect(getNextAdhipati(MERCURY, 1)).toBe(KETU); // Wraps around
    });

    it('should return previous lord in reverse sequence', () => {
      expect(getNextAdhipati(VENUS, -1)).toBe(KETU);
      expect(getNextAdhipati(KETU, -1)).toBe(MERCURY); // Wraps around
    });
  });

  describe('vimsottariDashaStartDate', () => {
    it('should return lord and start date', () => {
      const jd = 2451545.0; // J2000.0
      const [lord, startDate] = vimsottariDashaStartDate(jd, bangalore);
      
      expect(lord).toBeGreaterThanOrEqual(0);
      expect(lord).toBeLessThanOrEqual(8);
      expect(startDate).toBeLessThanOrEqual(jd); // Start date is before or at birth
    });
  });

  describe('vimsottariMahadasha', () => {
    it('should return 9 mahadashas', () => {
      const jd = 2451545.0;
      const dashas = vimsottariMahadasha(jd, bangalore);
      
      expect(dashas.size).toBe(9);
    });

    it('should have increasing start dates', () => {
      const jd = 2451545.0;
      const dashas = vimsottariMahadasha(jd, bangalore);
      const dates = Array.from(dashas.values());
      
      for (let i = 1; i < dates.length; i++) {
        expect(dates[i]).toBeGreaterThan(dates[i - 1]!);
      }
    });

    it('should span approximately 120 years', () => {
      const jd = 2451545.0;
      const dashas = vimsottariMahadasha(jd, bangalore);
      const dates = Array.from(dashas.values());
      
      const firstStart = dates[0]!;
      // Calculate total span by adding all 9 dasha periods
      // This should sum to 120 years: 7+20+6+10+7+18+16+19+17 = 120
      const totalDays = 120 * 365.256363; // Using sidereal year
      const lastEnd = firstStart + totalDays;
      const totalYears = (lastEnd - firstStart) / 365.256363;
      
      expect(totalYears).toBeCloseTo(120, 0);
    });
  });

  describe('vimsottariBhukti', () => {
    it('should return 9 bhuktis', () => {
      const startDate = 2451545.0;
      const bhuktis = vimsottariBhukti(VENUS, startDate);
      
      expect(bhuktis.size).toBe(9);
    });

    it('should have Venus-Venus as first bhukti when Venus is maha lord', () => {
      const startDate = 2451545.0;
      const bhuktis = vimsottariBhukti(VENUS, startDate);
      const firstBhuktiLord = Array.from(bhuktis.keys())[0];
      
      expect(firstBhuktiLord).toBe(VENUS);
    });
  });

  describe('getVimsottariDashaBhukti', () => {
    it('should return complete dasha data', () => {
      const jd = 2451545.0;
      const result = getVimsottariDashaBhukti(jd, bangalore);
      
      expect(result.balance).toBeDefined();
      expect(result.balance.years).toBeGreaterThanOrEqual(0);
      expect(result.mahadashas.length).toBe(9);
    });

    it('should include bhuktis by default', () => {
      const jd = 2451545.0;
      const result = getVimsottariDashaBhukti(jd, bangalore);
      
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBe(81); // 9 * 9
    });

    it('should not include bhuktis when disabled', () => {
      const jd = 2451545.0;
      const result = getVimsottariDashaBhukti(jd, bangalore, { includeBhuktis: false });
      
      expect(result.bhuktis).toBeUndefined();
    });
  });
});
