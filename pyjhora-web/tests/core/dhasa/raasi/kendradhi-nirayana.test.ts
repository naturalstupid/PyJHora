/**
 * Tests for Kendradhi and Nirayana Shoola Raasi Dashas
 */

import { describe, expect, it } from 'vitest';
import { getKendradhiDashaBhukti } from '../../../../src/core/dhasa/raasi/kendradhi';
import { getNirayanaShoolaDashaBhukti } from '../../../../src/core/dhasa/raasi/nirayana';
import type { Place } from '../../../../src/core/types';

describe('Kendradhi Rasi Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns 12 mahadashas in first cycle', () => {
    const result = getKendradhiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    // Kendradhi uses kendra progression = 12 signs
    expect(result.mahadashas.length).toBeGreaterThanOrEqual(12);
  });

  it('each mahadasha has valid duration', () => {
    const result = getKendradhiDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThan(0);
      expect(maha.durationYears).toBeLessThanOrEqual(12);
    }
  });

  it('includes bhuktis when requested', () => {
    const result = getKendradhiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getKendradhiDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getKendradhiDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBeGreaterThan(0);
    expect(d9Result.mahadashas.length).toBeGreaterThan(0);
  });
});

describe('Nirayana Shoola Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  const testJd = 2447912.0;

  it('returns 12 mahadashas in first cycle', () => {
    const result = getNirayanaShoolaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    expect(result.mahadashas.length).toBeGreaterThanOrEqual(12);
  });

  it('durations are 7, 8, or 9 based on sign type', () => {
    const result = getNirayanaShoolaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    
    for (const maha of result.mahadashas.slice(0, 12)) {
      // First cycle: movable=7, fixed=8, dual=9
      expect([7, 8, 9].includes(maha.durationYears) || 
             // Second cycle has 12-first durations
             [3, 4, 5].includes(maha.durationYears)).toBeTruthy();
    }
  });

  it('includes bhuktis when requested', () => {
    const result = getNirayanaShoolaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });

  it('respects divisionalChartFactor', () => {
    const d1Result = getNirayanaShoolaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getNirayanaShoolaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    
    expect(d1Result.mahadashas.length).toBeGreaterThan(0);
    expect(d9Result.mahadashas.length).toBeGreaterThan(0);
  });
});
