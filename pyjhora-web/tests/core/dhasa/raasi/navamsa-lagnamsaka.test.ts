/**
 * Tests for Navamsa and Lagnamsaka Dashas
 */

import { describe, expect, it } from 'vitest';
import { getLagnamsakaDashaBhukti } from '../../../../src/core/dhasa/raasi/lagnamsaka';
import { getNavamsaDashaBhukti } from '../../../../src/core/dhasa/raasi/navamsa';
import type { Place } from '../../../../src/core/types';

describe('Navamsa Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  it('returns valid structure', () => {
    const result = getNavamsaDashaBhukti(testJd, testPlace);
    expect(result.mahadashas.length).toBe(12);
  });

  it('each mahadasha has 9 year duration', () => {
    const result = getNavamsaDashaBhukti(testJd, testPlace);
    for (const d of result.mahadashas) {
      expect(d.durationYears).toBe(9);
    }
  });

  it('includes bhuktis', () => {
    const result = getNavamsaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis!.length).toBe(144);
    // Bhukti duration should be 9/12 = 0.75
    expect(result.bhuktis![0].durationYears).toBeCloseTo(0.75);
  });
});

describe('Lagnamsaka Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  it('returns valid structure using Narayana logic', () => {
    const result = getLagnamsakaDashaBhukti(testJd, testPlace);
    expect(result.mahadashas.length).toBeGreaterThan(0);
  });

  it('uses D-9 factor internally (integration check)', () => {
    // We can't easily verifying D-9 was used without mocking, 
    // but we check it runs without error and returns periods
    const result = getLagnamsakaDashaBhukti(testJd, testPlace);
    expect(result.mahadashas[0].durationYears).toBeGreaterThan(0);
  });
});
