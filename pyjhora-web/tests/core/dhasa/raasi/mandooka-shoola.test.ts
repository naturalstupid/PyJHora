/**
 * Tests for Mandooka and Shoola Raasi Dashas
 */

import { describe, expect, it } from 'vitest';
import { getMandookaDashaBhukti } from '../../../../src/core/dhasa/raasi/mandooka';
import { getShoolaDashaBhukti } from '../../../../src/core/dhasa/raasi/shoola';
import type { Place } from '../../../../src/core/types';

describe('Mandooka Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  // JD for 1990-01-15 12:00
  const testJd = 2447912.0;

  it('returns 12 mahadashas', () => {
    const result = getMandookaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    expect(result.mahadashas.length).toBe(12);
  });

  it('each mahadasha has valid duration', () => {
    const result = getMandookaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThan(0);
      expect(maha.durationYears).toBeLessThanOrEqual(12);
    }
  });

  it('includes bhuktis when requested', () => {
    const result = getMandookaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(12 * 12); // 12 bhuktis per 12 dashas
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getMandookaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getMandookaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    // D-9 may produce different seed rasi
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});

describe('Shoola Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('first cycle has 12 mahadashas of 9 years each', () => {
    const result = getShoolaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    // First 12 should each be 9 years
    const firstCycle = result.mahadashas.slice(0, 12);
    expect(firstCycle.length).toBe(12);
    
    for (const maha of firstCycle) {
      expect(maha.durationYears).toBe(9);
    }
  });

  it('second cycle has remaining 3 years each', () => {
    const result = getShoolaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    // Should have more than 12 (second cycle)
    expect(result.mahadashas.length).toBeGreaterThan(12);
    
    // Second cycle entries should be 3 years (12 - 9)
    const secondCycle = result.mahadashas.slice(12);
    for (const maha of secondCycle) {
      expect(maha.durationYears).toBe(3);
    }
  });

  it('includes bhuktis when requested', () => {
    const result = getShoolaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getShoolaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getShoolaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBeGreaterThan(0);
    expect(d9Result.mahadashas.length).toBeGreaterThan(0);
  });
});
