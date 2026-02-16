/**
 * Tests for Phase 5: Special Lagnas and Phase 6: Panchanga Display
 *
 * Python reference data generated from drik.py:
 *   special_ascendant (bhava/hora/ghati lagna), kunda_lagna,
 *   trikalam, abhijit_muhurta, durmuhurtam
 *
 * NOTE: Special lagna calculations depend on sunrise time.
 * WASM uses Moshier ephemeris vs Python's JPL/Swiss ephemeris,
 * causing ~1 minute sunrise difference. This error scales with
 * the lagna rate factor (0.25° for bhava, 0.5° for hora, 1.25° for ghati).
 * Tolerances are set accordingly.
 */

import { beforeAll, describe, expect, it } from 'vitest';
import { initializeEphemeris } from '@core/ephemeris/swe-adapter';
import {
  specialAscendantAsync,
  bhavaLagnaAsync,
  horaLagnaAsync,
  ghatiLagnaAsync,
  kundaLagnaAsync,
  trikalamAsync,
  abhijitMuhurtaAsync,
  durmuhurtamAsync,
} from '@core/panchanga/drik';
import type { Place } from '@core/types';
import { gregorianToJulianDay } from '@core/utils/julian';

const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5,
};

function jdForDateTime(
  year: number, month: number, day: number,
  hour: number, minute: number, second: number = 0
): number {
  return gregorianToJulianDay({ year, month, day }, { hour, minute, second });
}

function jdForDate(year: number, month: number, day: number): number {
  return jdForDateTime(year, month, day, 0, 0, 0);
}

describe('Phase 5: Special Lagnas', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  // ===========================================================================
  // Bhava Lagna (rate = 0.25)
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 10:34: bhava_lagna → (9, 21.862)  — Capricorn, 21.86°
   * 2024-06-21 14:30: bhava_lagna → (6, 14.041)  — Libra, 14.04°
   */
  describe('bhavaLagnaAsync', () => {
    it('should return correct bhava lagna for 1996-12-07 10:34', async () => {
      const jd = jdForDateTime(1996, 12, 7, 10, 34);
      const [rasi, long] = await bhavaLagnaAsync(jd, bangalore);
      expect(rasi).toBe(9); // Capricorn
      expect(long).toBeCloseTo(21.862, 0);
    });

    it('should return correct bhava lagna for 2024-06-21 14:30', async () => {
      const jd = jdForDateTime(2024, 6, 21, 14, 30);
      const [rasi, long] = await bhavaLagnaAsync(jd, bangalore);
      expect(rasi).toBe(6); // Libra
      expect(long).toBeCloseTo(14.041, 0);
    });
  });

  // ===========================================================================
  // Hora Lagna (rate = 0.5)
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 10:34: hora_lagna → (11, 22.096)  — Pisces, 22.10°
   * 2024-06-21 14:30: hora_lagna → (10, 21.912)  — Aquarius, 21.91°
   */
  describe('horaLagnaAsync', () => {
    it('should return correct hora lagna for 1996-12-07 10:34', async () => {
      const jd = jdForDateTime(1996, 12, 7, 10, 34);
      const [rasi, long] = await horaLagnaAsync(jd, bangalore);
      expect(rasi).toBe(11); // Pisces
      // rate=0.5 → ~0.5° Moshier/JPL sunrise offset tolerance
      expect(Math.abs(long - 22.096)).toBeLessThan(1.5);
    });

    it('should return correct hora lagna for 2024-06-21 14:30', async () => {
      const jd = jdForDateTime(2024, 6, 21, 14, 30);
      const [rasi, long] = await horaLagnaAsync(jd, bangalore);
      expect(rasi).toBe(10); // Aquarius
      expect(Math.abs(long - 21.912)).toBeLessThan(1.5);
    });
  });

  // ===========================================================================
  // Ghati Lagna (rate = 1.25)
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 10:34: ghati_lagna → (5, 22.798)
   * 2024-06-21 14:30: ghati_lagna → (11, 15.525)
   */
  describe('ghatiLagnaAsync', () => {
    it('should return correct ghati lagna for 1996-12-07 10:34', async () => {
      const jd = jdForDateTime(1996, 12, 7, 10, 34);
      const [rasi, long] = await ghatiLagnaAsync(jd, bangalore);
      expect(rasi).toBe(5); // Virgo
      // rate=1.25 → ~1.25° Moshier/JPL sunrise offset tolerance
      expect(Math.abs(long - 22.798)).toBeLessThan(2.0);
    });

    it('should return correct ghati lagna for 2024-06-21 14:30', async () => {
      const jd = jdForDateTime(2024, 6, 21, 14, 30);
      const [rasi, long] = await ghatiLagnaAsync(jd, bangalore);
      expect(rasi).toBe(11); // Pisces
      expect(Math.abs(long - 15.525)).toBeLessThan(2.0);
    });
  });

  // ===========================================================================
  // Kunda Lagna (ascLong * 81 % 360)
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 10:34: kunda_lagna → (1, 25.725)  — Taurus, 25.72°
   * 2024-06-21 14:30: kunda_lagna → (2, 29.909)  — Gemini, 29.91°
   */
  describe('kundaLagnaAsync', () => {
    it('should return correct kunda lagna for 1996-12-07 10:34', async () => {
      const jd = jdForDateTime(1996, 12, 7, 10, 34);
      const [rasi, long] = await kundaLagnaAsync(jd, bangalore);
      expect(rasi).toBe(1); // Taurus
      expect(long).toBeCloseTo(25.725, 0);
    });

    it('should return correct kunda lagna for 2024-06-21 14:30', async () => {
      const jd = jdForDateTime(2024, 6, 21, 14, 30);
      const [rasi, long] = await kundaLagnaAsync(jd, bangalore);
      expect(rasi).toBe(2); // Gemini
      expect(long).toBeCloseTo(29.909, 0);
    });
  });

  // ===========================================================================
  // specialAscendantAsync — generic rate factor
  // ===========================================================================

  describe('specialAscendantAsync', () => {
    it('rate=0.25 should match bhavaLagnaAsync', async () => {
      const jd = jdForDateTime(1996, 12, 7, 10, 34);
      const [r1, l1] = await specialAscendantAsync(jd, bangalore, 0.25);
      const [r2, l2] = await bhavaLagnaAsync(jd, bangalore);
      expect(r1).toBe(r2);
      expect(l1).toBeCloseTo(l2, 6);
    });

    it('rate=0.5 should match horaLagnaAsync', async () => {
      const jd = jdForDateTime(2024, 6, 21, 14, 30);
      const [r1, l1] = await specialAscendantAsync(jd, bangalore, 0.5);
      const [r2, l2] = await horaLagnaAsync(jd, bangalore);
      expect(r1).toBe(r2);
      expect(l1).toBeCloseTo(l2, 6);
    });
  });
});

describe('Phase 6: Panchanga Display', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  // ===========================================================================
  // trikalamAsync
  // ===========================================================================

  /*
   * Python reference (1996-12-07 Saturday, vaara=6):
   * raahu kaalam: 09:22:05 - 10:46:36  (≈9.368 - 10.777)
   * yamagandam:   13:35:37 - 15:00:08  (≈13.594 - 15.002)
   * gulikai:      06:33:04 - 07:57:35  (≈6.551 - 7.960)
   */
  describe('trikalamAsync', () => {
    it('should return raahu kaalam for Saturday 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [start, end] = await trikalamAsync(jd, bangalore, 'raahu kaalam');
      expect(start).toBeCloseTo(9.368, 0); // ~9:22
      expect(end).toBeCloseTo(10.777, 0);  // ~10:47
    });

    it('should return yamagandam for Saturday 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [start, end] = await trikalamAsync(jd, bangalore, 'yamagandam');
      expect(start).toBeCloseTo(13.594, 0); // ~13:36
      expect(end).toBeCloseTo(15.002, 0);   // ~15:00
    });

    it('should return gulikai for Saturday 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [start, end] = await trikalamAsync(jd, bangalore, 'gulikai');
      expect(start).toBeCloseTo(6.551, 0); // ~6:33
      expect(end).toBeCloseTo(7.960, 0);   // ~7:58
    });

    it('trikalam period should be 1/8 of day duration', async () => {
      const jd = jdForDate(2024, 6, 21);
      const [start, end] = await trikalamAsync(jd, bangalore, 'raahu kaalam');
      // Duration should be approximately day_duration / 8
      const duration = end - start;
      expect(duration).toBeGreaterThan(1.0); // > 1 hour
      expect(duration).toBeLessThan(2.0);    // < 2 hours
    });
  });

  // ===========================================================================
  // abhijitMuhurtaAsync
  // ===========================================================================

  /*
   * Python reference (1996-12-07):
   * abhijit: 11:48:34 - 12:33:39  (≈11.810 - 12.561)
   */
  describe('abhijitMuhurtaAsync', () => {
    it('should return abhijit muhurta for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [start, end] = await abhijitMuhurtaAsync(jd, bangalore);
      expect(start).toBeCloseTo(11.810, 0); // ~11:49
      expect(end).toBeCloseTo(12.561, 0);   // ~12:34
    });

    it('abhijit should be around midday', async () => {
      const jd = jdForDate(2024, 6, 21);
      const [start, end] = await abhijitMuhurtaAsync(jd, bangalore);
      // Should be around noon ± 1 hour
      expect(start).toBeGreaterThan(11.0);
      expect(end).toBeLessThan(14.0);
    });
  });

  // ===========================================================================
  // durmuhurtamAsync
  // ===========================================================================

  /*
   * Python reference (1996-12-07 Saturday):
   * durmuhurtam: 08:03:13 - 08:48:17  (≈8.054 - 8.805)
   * (Saturday has only 1 durmuhurtam)
   */
  describe('durmuhurtamAsync', () => {
    it('should return durmuhurtam for Saturday 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const periods = await durmuhurtamAsync(jd, bangalore);
      // Saturday has 1 period
      expect(periods.length).toBe(1);
      expect(periods[0]![0]).toBeCloseTo(8.054, 0); // ~8:03
      expect(periods[0]![1]).toBeCloseTo(8.805, 0); // ~8:48
    });

    it('Monday should have 2 durmuhurtam periods', async () => {
      // Find a Monday — 1996-12-09 is Monday
      const jd = jdForDate(1996, 12, 9);
      const periods = await durmuhurtamAsync(jd, bangalore);
      expect(periods.length).toBe(2);
    });

    it('each period should be about 1/15 of day duration', async () => {
      const jd = jdForDate(2024, 6, 21);
      const periods = await durmuhurtamAsync(jd, bangalore);
      for (const [start, end] of periods) {
        const duration = end - start;
        // 0.8/12 * dayDur ≈ ~45 minutes = 0.75 hours
        expect(duration).toBeGreaterThan(0.5);
        expect(duration).toBeLessThan(1.2);
      }
    });
  });
});
