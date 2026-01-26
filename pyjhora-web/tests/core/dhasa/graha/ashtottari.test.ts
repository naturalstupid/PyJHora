
import { describe, expect, it } from 'vitest';
import {
    MOON,
    SUN
} from '../../../../src/core/constants';
import {
    getAshtottariDashaBhukti
} from '../../../../src/core/dhasa/graha/ashtottari';
import type { Place } from '../../../../src/core/types';

describe('Ashtottari Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  it('should return valid dasha structure', () => {
    const result = getAshtottariDashaBhukti(testJd, testPlace);
    expect(result.mahadashas).toBeDefined();
    expect(result.mahadashas.length).toBe(8); // 8 lords
    expect(result.mahadashas[0].durationYears).toBeGreaterThan(0);
  });

  it('should cycle through 8 lords', () => {
    const result = getAshtottariDashaBhukti(testJd, testPlace);
    const lords = result.mahadashas.map(m => m.lord);
    // Sequence: Sun, Moon, Mars, Mercury, Saturn, Jupiter, Rahu(7), Venus
    // Assuming starting lord might vary based on Moon position
    // But the cycle order should be consistent.
    
    // Find index of Sun
    const sunIndex = lords.indexOf(SUN);
    if (sunIndex !== -1) {
        const nextIndex = (sunIndex + 1) % 8;
        expect(lords[nextIndex]).toBe(MOON);
    }
  });

  it('should include bhuktis', () => {
    const result = getAshtottariDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
  });

  // TODO: Add specific calculation verification against known data
});
