/**
 * Tests for Drig and Trikona Raasi Dashas
 */

import { describe, expect, it } from 'vitest';
import { getDrigDashaBhukti } from '../../../../src/core/dhasa/raasi/drig';
import { getTrikonaDashaBhukti } from '../../../../src/core/dhasa/raasi/trikona';
import type { Place } from '../../../../src/core/types';

describe('Drig Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns 12 mahadashas in first cycle', () => {
    const result = getDrigDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    // Drig uses 9th, 10th, 11th houses with 4 kendras each = 12 signs
    expect(result.mahadashas.length).toBeGreaterThanOrEqual(12);
  });

  it('each mahadasha has valid duration', () => {
    const result = getDrigDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThan(0);
      expect(maha.durationYears).toBeLessThanOrEqual(12);
    }
  });

  it('includes bhuktis when requested', () => {
    const result = getDrigDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getDrigDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getDrigDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBeGreaterThan(0);
    expect(d9Result.mahadashas.length).toBeGreaterThan(0);
  });
});

describe('Trikona Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns exactly 12 mahadashas', () => {
    const result = getTrikonaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    expect(result.mahadashas.length).toBe(12);
  });

  it('each mahadasha has valid duration', () => {
    const result = getTrikonaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThan(0);
      expect(maha.durationYears).toBeLessThanOrEqual(12);
    }
  });

  it('includes 144 bhuktis when requested (12 x 12)', () => {
    const result = getTrikonaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getTrikonaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getTrikonaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});
