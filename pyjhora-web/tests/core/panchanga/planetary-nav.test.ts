/**
 * Tests for Phase 4: Planetary Navigation functions
 *
 * Python reference data generated from drik.py:
 *   lunar_phase, new_moon, full_moon, next_planet_entry_date
 */

import { beforeAll, describe, expect, it } from 'vitest';
import { initializeEphemeris } from '@core/ephemeris/swe-adapter';
import {
  lunarPhaseAsync,
  newMoonAsync,
  fullMoonAsync,
  nextPlanetEntryDateAsync,
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

describe('Phase 4: Planetary Navigation', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  // ===========================================================================
  // lunarPhaseAsync
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07: 312.863
   * 2024-06-21: 166.950
   */
  describe('lunarPhaseAsync', () => {
    it('should return correct lunar phase for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const phase = await lunarPhaseAsync(jd);
      expect(phase).toBeCloseTo(312.863, 0);
    });

    it('should return correct lunar phase for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const phase = await lunarPhaseAsync(jd);
      expect(phase).toBeCloseTo(166.950, 0);
    });

    it('should be between 0 and 360', async () => {
      const jd = jdForDate(2024, 1, 15);
      const phase = await lunarPhaseAsync(jd);
      expect(phase).toBeGreaterThanOrEqual(0);
      expect(phase).toBeLessThan(360);
    });
  });

  // ===========================================================================
  // newMoonAsync
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 (tithi=26): prev=2450398.6783, next=2450428.2062
   * 2024-06-21 (tithi=14): prev=2460468.0266, next=2460497.457
   */
  describe('newMoonAsync', () => {
    it('should find previous new moon for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const nm = await newMoonAsync(jd, 26, -1);
      expect(nm).toBeCloseTo(2450398.6783, 0); // ±0.5 day
    });

    it('should find next new moon for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const nm = await newMoonAsync(jd, 26, +1);
      expect(nm).toBeCloseTo(2450428.2062, 0);
    });

    it('should find previous new moon for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const nm = await newMoonAsync(jd, 14, -1);
      expect(nm).toBeCloseTo(2460468.0266, 0);
    });

    it('should find next new moon for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const nm = await newMoonAsync(jd, 14, +1);
      expect(nm).toBeCloseTo(2460497.457, 0);
    });

    it('lunar phase at new moon should be near 360/0', async () => {
      const jd = jdForDate(1996, 12, 7);
      const nm = await newMoonAsync(jd, 26, -1);
      const phase = await lunarPhaseAsync(nm);
      // Phase should be very close to 360 (= 0)
      const normalized = phase > 350 ? 360 - phase : phase;
      expect(normalized).toBeLessThan(2);
    });
  });

  // ===========================================================================
  // fullMoonAsync
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 (tithi=26): prev=2450412.674, next=2450442.3623
   */
  describe('fullMoonAsync', () => {
    it('should find previous full moon for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const fm = await fullMoonAsync(jd, 26, -1);
      expect(fm).toBeCloseTo(2450412.674, 0);
    });

    it('should find next full moon for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const fm = await fullMoonAsync(jd, 26, +1);
      expect(fm).toBeCloseTo(2450442.3623, 0);
    });

    it('lunar phase at full moon should be near 180', async () => {
      const jd = jdForDate(1996, 12, 7);
      const fm = await fullMoonAsync(jd, 26, -1);
      const phase = await lunarPhaseAsync(fm);
      expect(phase).toBeCloseTo(180, 0);
    });
  });

  // ===========================================================================
  // nextPlanetEntryDateAsync
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07 Sun next entry: JD=2450433.2349, long=240.0
   * 2024-06-21 Sun next entry: JD=2460507.9656, long=90.0
   */
  describe('nextPlanetEntryDateAsync', () => {
    it('should find Sun next sign entry for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [entryJd, entryLong] = await nextPlanetEntryDateAsync(0, jd, bangalore, 1);
      // Sun enters Sagittarius (240°) around Dec 16-17
      expect(entryJd).toBeCloseTo(2450433.2349, 0);
      expect(entryLong).toBeCloseTo(240.0, 0);
    });

    it('should find Sun next sign entry for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const [entryJd, entryLong] = await nextPlanetEntryDateAsync(0, jd, bangalore, 1);
      // Sun enters Cancer (90°) around July 16-17
      expect(entryJd).toBeCloseTo(2460507.9656, 0);
      expect(entryLong).toBeCloseTo(90.0, 0);
    });

    it('entry longitude should be near a sign boundary (multiple of 30)', async () => {
      const jd = jdForDate(2024, 1, 15);
      const [, entryLong] = await nextPlanetEntryDateAsync(0, jd, bangalore, 1);
      // Should be close to a multiple of 30°
      const remainder = entryLong % 30;
      const nearBoundary = Math.min(remainder, 30 - remainder);
      expect(nearBoundary).toBeLessThan(1);
    });
  });
});
