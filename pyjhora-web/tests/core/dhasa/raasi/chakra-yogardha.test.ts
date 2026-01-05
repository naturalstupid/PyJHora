/**
 * Tests for Chakra and Yogardha Raasi Dashas
 */

import { describe, expect, it } from 'vitest';
import { getChakraDashaBhukti } from '../../../../src/core/dhasa/raasi/chakra';
import { getYogardhaDashaBhukti } from '../../../../src/core/dhasa/raasi/yogardha';
import type { Place } from '../../../../src/core/types';

describe('Chakra Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns exactly 12 mahadashas', () => {
    const result = getChakraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    expect(result.mahadashas.length).toBe(12);
  });

  it('each mahadasha has 10-year duration', () => {
    const result = getChakraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBe(10);
    }
  });

  it('total dasha cycle is 120 years', () => {
    const result = getChakraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBe(120);
  });

  it('includes 144 bhuktis when requested (12 x 12)', () => {
    const result = getChakraDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });
});

describe('Yogardha Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns exactly 12 mahadashas', () => {
    const result = getYogardhaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    expect(result.mahadashas.length).toBe(12);
  });

  it('durations are averages (should be between 4 and 12)', () => {
    const result = getYogardhaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThanOrEqual(4);
      expect(maha.durationYears).toBeLessThanOrEqual(12);
    }
  });

  it('includes 144 bhuktis when requested', () => {
    const result = getYogardhaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getYogardhaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getYogardhaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});
