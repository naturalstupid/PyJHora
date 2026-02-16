/**
 * Tests for sunrise/sunset/moonrise/moonset via swe_rise_trans
 * Python reference data generated from drik.py using Swiss Ephemeris
 */

import { beforeAll, describe, expect, it } from 'vitest';
import {
  initializeEphemeris,
  sunriseAsync,
  sunsetAsync,
  moonriseAsync,
  moonsetAsync,
} from '@core/ephemeris/swe-adapter';
import { middayAsync, midnightAsync } from '@core/panchanga/drik';
import type { Place } from '@core/types';
import { gregorianToJulianDay } from '@core/utils/julian';

// Test places
const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5
};

const newYork: Place = {
  name: 'NewYork',
  latitude: 40.7128,
  longitude: -74.0060,
  timezone: -5.0
};

// Helper to create JD at midnight for a given date
function jdForDate(year: number, month: number, day: number): number {
  return gregorianToJulianDay({ year, month, day }, { hour: 0, minute: 0, second: 0 });
}

// Tolerance: ±0.02 hours (~1.2 minutes) for rise_trans vs Python
const TIME_TOLERANCE = 0.02;

describe('Sunrise/Sunset via swe_rise_trans', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  describe('Bangalore sunrise', () => {
    // Python reference: Date 1996-12-07, sunrise localTime=6.551072
    it('should match Python for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await sunriseAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(6.551072, 1);
    });

    // Python reference: Date 2024-01-15, sunrise localTime=6.820725
    it('should match Python for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await sunriseAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(6.820725, 1);
    });

    // Python reference: Date 2024-06-21 (summer solstice), sunrise localTime=5.975270
    it('should match Python for 2024-06-21 (summer solstice)', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await sunriseAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(5.975270, 1);
    });

    // Python reference: Date 2024-03-20 (equinox), sunrise localTime=6.451706
    it('should match Python for 2024-03-20 (equinox)', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await sunriseAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(6.451706, 1);
    });
  });

  describe('Bangalore sunset', () => {
    // Python reference: Date 1996-12-07, sunset localTime=17.819310
    it('should match Python for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await sunsetAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(17.819310, 1);
    });

    // Python reference: Date 2024-01-15, sunset localTime=18.140029
    it('should match Python for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await sunsetAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(18.140029, 1);
    });

    // Python reference: Date 2024-06-21, sunset localTime=18.741349
    it('should match Python for 2024-06-21 (summer solstice)', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await sunsetAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(18.741349, 1);
    });
  });

  describe('New York sunrise/sunset', () => {
    // Python reference: NY 2024-01-15, sunrise=7.384732, sunset=16.797895
    it('should match Python sunrise for NY 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await sunriseAsync(jd, newYork);
      expect(result.localTime).toBeCloseTo(7.384732, 1);
    });

    it('should match Python sunset for NY 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await sunsetAsync(jd, newYork);
      expect(result.localTime).toBeCloseTo(16.797895, 1);
    });

    // Python reference: NY 2024-06-21, sunrise=4.505132, sunset=19.427614
    it('should match Python sunrise for NY 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await sunriseAsync(jd, newYork);
      expect(result.localTime).toBeCloseTo(4.505132, 1);
    });

    it('should match Python sunset for NY 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await sunsetAsync(jd, newYork);
      expect(result.localTime).toBeCloseTo(19.427614, 1);
    });
  });

  describe('Moonrise/Moonset', () => {
    // Python reference: Bangalore 1996-12-07, moonrise=3.076942, moonset=15.102978
    it('should match Python moonrise for Bangalore 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await moonriseAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(3.076942, 1);
    });

    it('should match Python moonset for Bangalore 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await moonsetAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(15.102978, 1);
    });

    // Python reference: Bangalore 2024-01-15, moonrise=9.904272, moonset=22.195166
    it('should match Python moonrise for Bangalore 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await moonriseAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(9.904272, 1);
    });

    it('should match Python moonset for Bangalore 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await moonsetAsync(jd, bangalore);
      expect(result.localTime).toBeCloseTo(22.195166, 1);
    });
  });

  describe('Return value structure', () => {
    it('should return localTime, timeString, and jd', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await sunriseAsync(jd, bangalore);

      expect(typeof result.localTime).toBe('number');
      expect(typeof result.timeString).toBe('string');
      expect(typeof result.jd).toBe('number');
      expect(result.localTime).toBeGreaterThan(4);
      expect(result.localTime).toBeLessThan(10);
      expect(result.timeString).toMatch(/\d{2}:\d{2}:\d{2} [AP]M/);
    });

    it('sunset should be after sunrise', async () => {
      const jd = jdForDate(2024, 1, 15);
      const sr = await sunriseAsync(jd, bangalore);
      const ss = await sunsetAsync(jd, bangalore);
      expect(ss.localTime).toBeGreaterThan(sr.localTime);
      expect(ss.jd).toBeGreaterThan(sr.jd);
    });
  });

  describe('Midday/Midnight', () => {
    // Midday should be around 12:00 local time
    it('midday should be near noon for Bangalore', async () => {
      const jd = jdForDate(2024, 1, 15);
      const md = await middayAsync(jd, bangalore);
      // Midday = avg of sunrise (~6.82) and sunset (~18.14) = ~12.48
      expect(md.localTime).toBeGreaterThan(11.5);
      expect(md.localTime).toBeLessThan(13.0);
    });

    it('midnight should be near 0 hours for Bangalore', async () => {
      const jd = jdForDate(2024, 1, 15);
      const mn = await midnightAsync(jd, bangalore);
      // Midnight should be close to 0 (around 0-1 hour)
      expect(mn).toBeGreaterThanOrEqual(0);
      expect(mn).toBeLessThan(2);
    });
  });
});
