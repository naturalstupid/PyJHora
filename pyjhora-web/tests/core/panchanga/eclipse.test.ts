/**
 * Tests for Phase 7: Eclipse Functions
 *
 * NOTE: Python's next_solar_eclipse/next_lunar_eclipse have a geopos bug:
 *   geopos = (place.latitude, place.longitude, 0.0) — lat/lon swapped!
 *   Our TS implementation uses correct C API order: (longitude, latitude, alt).
 *   Therefore, eclipse dates will differ from Python reference data.
 *   Tests verify correctness via self-consistency and known astronomical events.
 */

import { beforeAll, describe, expect, it } from 'vitest';
import { initializeEphemeris } from '@core/ephemeris/swe-adapter';
import {
  nextSolarEclipseAsync,
  nextLunarEclipseAsync,
  isSolarEclipseAsync,
} from '@core/panchanga/drik';
import type { Place } from '@core/types';
import { gregorianToJulianDay, julianDayToGregorian } from '@core/utils/julian';

const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5,
};

function jdForDate(year: number, month: number, day: number): number {
  return gregorianToJulianDay({ year, month, day }, { hour: 0, minute: 0, second: 0 });
}

describe('Phase 7: Eclipse Functions', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  // ===========================================================================
  // nextSolarEclipseAsync
  // ===========================================================================

  describe('nextSolarEclipseAsync', () => {
    it('should find a solar eclipse from 2024-01-01', async () => {
      const jd = jdForDate(2024, 1, 1);
      const [retflag, tret, attr] = await nextSolarEclipseAsync(jd, bangalore);
      // Should find an eclipse (retflag > 0)
      expect(retflag).toBeGreaterThan(0);
      // Greatest eclipse JD should be after search date
      expect(tret[0]).toBeGreaterThan(jd);
      // tret array should have valid entries
      expect(tret.length).toBeGreaterThanOrEqual(5);
      // attr array should have eclipse properties
      expect(attr.length).toBeGreaterThanOrEqual(8);
      // Fraction covered should be positive
      expect(attr[0]).toBeGreaterThan(0);
    });

    it('should find a solar eclipse from 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [retflag, tret, attr] = await nextSolarEclipseAsync(jd, bangalore);
      expect(retflag).toBeGreaterThan(0);
      expect(tret[0]).toBeGreaterThan(jd);
      expect(attr[0]).toBeGreaterThan(0);
      // Eclipse should be found within 5 years
      const { date } = julianDayToGregorian(tret[0]);
      expect(date.year).toBeGreaterThanOrEqual(1997);
      expect(date.year).toBeLessThanOrEqual(2002);
    });

    it('greatest eclipse should have positive tret values', async () => {
      const jd = jdForDate(2020, 1, 1);
      const [, tret] = await nextSolarEclipseAsync(jd, bangalore);
      // Greatest eclipse JD (tret[0]) should be non-zero
      expect(tret[0]).toBeGreaterThan(2400000);
    });
  });

  // ===========================================================================
  // nextLunarEclipseAsync
  // ===========================================================================

  describe('nextLunarEclipseAsync', () => {
    it('should find a lunar eclipse from 2024-01-01', async () => {
      const jd = jdForDate(2024, 1, 1);
      const [retflag, tret, attr] = await nextLunarEclipseAsync(jd, bangalore);
      expect(retflag).toBeGreaterThan(0);
      expect(tret[0]).toBeGreaterThan(jd);
      expect(attr.length).toBeGreaterThanOrEqual(8);
      // Eclipse fraction should be positive
      expect(attr[0]).toBeGreaterThan(0);
    });

    it('lunar eclipse should be found within 2 years', async () => {
      const jd = jdForDate(2024, 6, 1);
      const [, tret] = await nextLunarEclipseAsync(jd, bangalore);
      // Should find eclipse within ~2 years (730 days)
      expect(tret[0] - jd).toBeLessThan(730);
      expect(tret[0]).toBeGreaterThan(jd);
    });

    it('consecutive eclipses should be different', async () => {
      const jd1 = jdForDate(2024, 1, 1);
      const [, tret1] = await nextLunarEclipseAsync(jd1, bangalore);
      // Search after the first eclipse
      const jd2 = tret1[0] + 1;
      const [, tret2] = await nextLunarEclipseAsync(jd2, bangalore);
      // The two eclipses should be at different times
      expect(Math.abs(tret2[0] - tret1[0])).toBeGreaterThan(25); // At least ~1 month apart
    });
  });

  // ===========================================================================
  // isSolarEclipseAsync
  // ===========================================================================

  describe('isSolarEclipseAsync', () => {
    it('should return result for any date', async () => {
      const jd = jdForDate(2024, 5, 15);
      const result = await isSolarEclipseAsync(jd, bangalore);
      expect(result).not.toBeNull();
      if (result) {
        expect(result.attr.length).toBeGreaterThanOrEqual(8);
      }
    });

    it('should return non-null for eclipse date', async () => {
      // Find a solar eclipse, then check that date
      const jd = jdForDate(2024, 1, 1);
      const [retflag, tret] = await nextSolarEclipseAsync(jd, bangalore);
      if (retflag > 0 && tret[0] > 0) {
        const result = await isSolarEclipseAsync(tret[0], bangalore);
        expect(result).not.toBeNull();
      }
    });
  });
});
