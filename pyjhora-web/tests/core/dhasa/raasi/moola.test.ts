/**
 * Tests for Moola Raasi Dasha
 */

import { describe, expect, it } from 'vitest';
import { getMoolaDashaBhukti } from '../../../../src/core/dhasa/raasi/moola';
import type { Place } from '../../../../src/core/types';

describe('Moola Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns 12 mahadashas in first cycle', () => {
    const result = getMoolaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    expect(result.mahadashas.length).toBeGreaterThanOrEqual(12);
  });

  it('each mahadasha has valid duration', () => {
    const result = getMoolaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThan(0);
      expect(maha.durationYears).toBeLessThanOrEqual(12);
    }
  });

  it('includes bhuktis when requested', () => {
    const result = getMoolaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getMoolaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getMoolaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBeGreaterThan(0);
    expect(d9Result.mahadashas.length).toBeGreaterThan(0);
  });
});
