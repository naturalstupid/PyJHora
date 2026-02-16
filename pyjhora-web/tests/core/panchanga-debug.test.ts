/**
 * Sanity tests for WASM ephemeris calculations.
 * Verifies that siderealLongitudeAsync returns consistent results
 * across consecutive calls and after sunrise calculations.
 */
import { beforeAll, describe, expect, it } from 'vitest';
import {
  initializeEphemeris,
  siderealLongitudeAsync,
  sunriseAsync,
} from '@core/ephemeris/swe-adapter';
import type { Place } from '@core/types';
import { gregorianToJulianDay } from '@core/utils/julian';

const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5,
};

describe('WASM ephemeris sanity checks', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  it('Moon longitude should be consistent before and after sunrise call', async () => {
    const jd = 2460482.7489583334; // ~June 21 2024 sunrise
    const moonBefore = await siderealLongitudeAsync(jd, 1);

    const inputJd = gregorianToJulianDay(
      { year: 2024, month: 6, day: 21 },
      { hour: 0, minute: 0, second: 0 }
    );
    await sunriseAsync(inputJd, bangalore);

    const moonAfter = await siderealLongitudeAsync(jd, 1);
    expect(moonBefore).toBeCloseTo(moonAfter, 10);
    expect(moonBefore).toBeCloseTo(236.19, 0);
  });

  it('consecutive Moon calculations should be monotonically increasing', async () => {
    const baseJd = 2460482.74;
    let prev = await siderealLongitudeAsync(baseJd, 1);
    for (let i = 1; i < 10; i++) {
      const jd = baseJd + i * 0.001;
      const moon = await siderealLongitudeAsync(jd, 1);
      expect(moon).toBeGreaterThan(prev);
      prev = moon;
    }
  });

  it('Sun and Moon at known JD should match Python reference', async () => {
    // JD for 2024-06-21 06:00 UT
    const jd = gregorianToJulianDay(
      { year: 2024, month: 6, day: 21 },
      { hour: 6, minute: 0, second: 0 }
    );
    const moon = await siderealLongitudeAsync(jd, 1);
    const sun = await siderealLongitudeAsync(jd, 0);
    // Python: Moon≈236.19, Sun≈66.17
    expect(moon).toBeCloseTo(236.19, 0);
    expect(sun).toBeCloseTo(66.17, 0);
  });
});
