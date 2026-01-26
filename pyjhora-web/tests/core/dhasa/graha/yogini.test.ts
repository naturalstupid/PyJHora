
import { describe, expect, it } from 'vitest';
import {
    getYoginiDashaBhukti,
    YOGINI_DURATIONS,
    YOGINI_NAMES
} from '../../../../src/core/dhasa/graha/yogini';
import type { Place } from '../../../../src/core/types';

describe('Yogini Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  it('should return valid dasha structure', () => {
    const result = getYoginiDashaBhukti(testJd, testPlace);
    expect(result.mahadashas).toBeDefined();
    expect(result.mahadashas.length).toBeGreaterThan(0);
    // Should produce 3 cycles * 8 lords = 24 periods?
    expect(result.mahadashas.length).toBe(24);
  });

  it('should have correct durations', () => {
    const result = getYoginiDashaBhukti(testJd, testPlace);
    for (const d of result.mahadashas) {
        expect(d.durationYears).toBe(YOGINI_DURATIONS[d.lord]);
        expect(d.yoginiName).toBe(YOGINI_NAMES[d.lord]);
    }
  });

  it('should include bhuktis', () => {
    const result = getYoginiDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });
});
