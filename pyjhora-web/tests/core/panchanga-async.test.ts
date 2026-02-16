/**
 * Tests for async panchanga functions (tithi, nakshatra, yogam, karana, raasi)
 * Using inverseLagrange + swe_rise_trans for accurate end times.
 *
 * Python reference data generated from drik.py:
 *   tithi_using_inverse_lagrange, _get_nakshathra, yogam_old, karana, raasi
 */

import { beforeAll, describe, expect, it } from 'vitest';
import { initializeEphemeris } from '@core/ephemeris/swe-adapter';
import {
  calculateTithiAsync,
  calculateNakshatraAsync,
  calculateYogaAsync,
  calculateKaranaAsync,
  raasiAsync,
} from '@core/panchanga/drik';
import type { Place } from '@core/types';
import { gregorianToJulianDay } from '@core/utils/julian';

const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5,
};

function jdForDate(year: number, month: number, day: number): number {
  return gregorianToJulianDay({ year, month, day }, { hour: 0, minute: 0, second: 0 });
}

describe('Async Panchanga (inverseLagrange)', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  /*
   * Python reference data (Bangalore, tithi_using_inverse_lagrange):
   *
   * 1996-12-07: [27, 3.794, 27.738]   → tithi 27, start ~3.79h, end ~27.74h
   * 2024-01-15: [5, 4.993, 26.200]     → tithi 5, start ~4.99h, end ~26.20h
   * 2024-06-21: [15, 7.552, 30.859]    → tithi 15, start ~7.55h, end ~30.86h
   * 2024-03-20: [11, 0.356, 26.322]    → tithi 11, start ~0.36h, end ~26.32h
   */
  describe('Tithi (calculateTithiAsync)', () => {
    it('should get tithi number for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[0]).toBe(27); // Tithi number
    });

    it('should get tithi end time for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(27.738, 0); // End time ±0.5h
    });

    it('should get tithi number for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[0]).toBe(5);
    });

    it('should get tithi end time for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(26.200, 0);
    });

    it('should get tithi number for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[0]).toBe(15);
    });

    it('should get tithi end time for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(30.859, 0);
    });

    it('should get tithi number for 2024-03-20', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[0]).toBe(11);
    });

    it('should get tithi end time for 2024-03-20', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await calculateTithiAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(26.322, 0);
    });
  });

  /*
   * Python reference data (_get_nakshathra):
   * Note: Python passes jd_utc (= jd - tz/24) to sunrise(), which for +tz
   * gives the PREVIOUS day's sunrise. Nakshatra is computed from that sunrise.
   *
   * 1996-12-07: [14, 3, 10.028, 15, 3, 34.147]
   * 2024-01-15: [24, 3, 8.116, 25, 3, 30.154]
   * 2024-06-21: [18, 1, 18.312, 19, 1, 41.830]
   * 2024-03-20: [8, 1, 22.636, 9, 1, 49.354]
   */
  describe('Nakshatra (calculateNakshatraAsync)', () => {
    it('should get nakshatra for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[0]).toBe(14); // Nakshatra number
      expect(result[1]).toBe(3);  // Pada
    });

    it('should get nakshatra end time for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(10.028, 0); // End time ±0.5h
    });

    it('should get next nakshatra for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[3]).toBe(15); // Next nakshatra
    });

    it('should get next nakshatra end time for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[5]).toBeCloseTo(34.147, 0);
    });

    it('should get nakshatra for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[0]).toBe(24);
      expect(result[1]).toBe(3);
    });

    it('should get nakshatra end time for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(8.116, 0);
    });

    it('should get nakshatra for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[0]).toBe(18);
      expect(result[1]).toBe(1);
    });

    it('should get nakshatra for 2024-03-20', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await calculateNakshatraAsync(jd, bangalore);
      expect(result[0]).toBe(8);
      expect(result[1]).toBe(1);
    });
  });

  /*
   * Python reference data (_get_yogam → yogam_old):
   *
   * 1996-12-07: yogam_old = [5, 1.708, 24.460, ...]
   * 2024-01-15: yogam_old = [18, 2.632, 23.118, ...]
   * 2024-06-21: yogam_old = [23, -3.711, 18.719, ...]
   * 2024-03-20: yogam_old = [6, -7.495, 16.985, ...]
   */
  describe('Yogam (calculateYogaAsync)', () => {
    it('should get yogam number for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[0]).toBe(5);
    });

    it('should get yogam end time for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(24.460, 0); // End time ±0.5h
    });

    it('should get yogam number for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[0]).toBe(18);
    });

    it('should get yogam end time for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(23.118, 0);
    });

    it('should get yogam number for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[0]).toBe(23);
    });

    it('should get yogam end time for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(18.719, 0);
    });

    it('should get yogam number for 2024-03-20', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[0]).toBe(6);
    });

    it('should get yogam end time for 2024-03-20', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await calculateYogaAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(16.985, 0);
    });
  });

  /*
   * Python reference data (karana):
   *
   * 1996-12-07: (53, 3.794, 15.766)
   * 2024-01-15: (9, 4.993, 15.596)
   * 2024-06-21: (29, 7.552, 19.205)
   * 2024-03-20: (21, 0.356, 13.339)
   */
  describe('Karana (calculateKaranaAsync)', () => {
    it('should get karana for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateKaranaAsync(jd, bangalore);
      expect(result[0]).toBe(53); // Karana number
    });

    it('should get karana end time for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await calculateKaranaAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(15.766, 0); // End time ±0.5h
    });

    it('should get karana for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateKaranaAsync(jd, bangalore);
      expect(result[0]).toBe(9);
    });

    it('should get karana end time for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await calculateKaranaAsync(jd, bangalore);
      expect(result[2]).toBeCloseTo(15.596, 0);
    });

    it('should get karana for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const result = await calculateKaranaAsync(jd, bangalore);
      expect(result[0]).toBe(29);
    });

    it('should get karana for 2024-03-20', async () => {
      const jd = jdForDate(2024, 3, 20);
      const result = await calculateKaranaAsync(jd, bangalore);
      expect(result[0]).toBe(21);
    });
  });

  /*
   * Python reference data (raasi):
   *
   * For raasi we check the raasi number (1-12) = Moon's sign.
   * Python: raasi(jd, place) returns [raasi_no, end_time_hours, frac_left, ...]
   */
  describe('Raasi (raasiAsync)', () => {
    it('should get raasi for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await raasiAsync(jd, bangalore);
      // Just check that it returns valid raasi (1-12) and end time
      expect(result[0]).toBeGreaterThanOrEqual(1);
      expect(result[0]).toBeLessThanOrEqual(12);
      expect(result.length).toBeGreaterThanOrEqual(3);
    });

    it('should get raasi for 2024-01-15', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await raasiAsync(jd, bangalore);
      expect(result[0]).toBeGreaterThanOrEqual(1);
      expect(result[0]).toBeLessThanOrEqual(12);
    });

    it('raasi end time should be reasonable', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await raasiAsync(jd, bangalore);
      // End time should be within a reasonable range (hours)
      expect(result[1]).toBeGreaterThan(-50);
      expect(result[1]).toBeLessThan(100);
    });

    it('should return frac_left between 0 and 1', async () => {
      const jd = jdForDate(2024, 1, 15);
      const result = await raasiAsync(jd, bangalore);
      expect(result[2]).toBeGreaterThan(0);
      expect(result[2]).toBeLessThanOrEqual(1);
    });
  });
});
