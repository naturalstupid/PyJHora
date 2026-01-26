/**
 * Tests for Varga-dependent Graha Dashas
 * Verifies that divisionalChartFactor correctly modifies planet positions
 */

import { describe, expect, it } from 'vitest';
import { getAshtottariDashaBhukti } from '../../../../src/core/dhasa/graha/ashtottari';
import { getVimsottariDashaBhukti } from '../../../../src/core/dhasa/graha/vimsottari';
import { getYoginiDashaBhukti } from '../../../../src/core/dhasa/graha/yogini';
import type { Place } from '../../../../src/core/types';

describe('Varga-dependent Graha Dashas', () => {
  // Standard test data
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  
  // JD for 1990-01-15 12:00 (example birth)
  const testJd = 2447912.0;

  describe('Vimsottari Dasha with divisionalChartFactor', () => {
    it('D-1 (factor=1) returns same result as default', () => {
      const defaultResult = getVimsottariDashaBhukti(testJd, testPlace);
      const d1Result = getVimsottariDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1 });
      
      expect(d1Result.mahadashas.length).toBe(defaultResult.mahadashas.length);
      expect(d1Result.mahadashas[0]?.lord).toBe(defaultResult.mahadashas[0]?.lord);
      expect(d1Result.mahadashas[0]?.startJd).toBeCloseTo(defaultResult.mahadashas[0]?.startJd ?? 0, 2);
    });

    it('D-9 (Navamsa) may produce different starting lord', () => {
      const d1Result = getVimsottariDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1 });
      const d9Result = getVimsottariDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9 });
      
      // D-9 should have valid mahadashas
      expect(d9Result.mahadashas.length).toBe(9);
      expect(d9Result.mahadashas[0]?.durationYears).toBeGreaterThan(0);
      
      // The lords or start dates may differ from D-1
      // (This is expected behavior - we're checking structure, not exact values)
      console.log('D-1 First Lord:', d1Result.mahadashas[0]?.lordName);
      console.log('D-9 First Lord:', d9Result.mahadashas[0]?.lordName);
    });

    it('D-10 (Dasamsa) produces valid dasha periods', () => {
      const d10Result = getVimsottariDashaBhukti(testJd, testPlace, { divisionalChartFactor: 10 });
      
      expect(d10Result.mahadashas.length).toBe(9);
      
      // Verify total duration is approximately 120 years
      const totalYears = d10Result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
      expect(totalYears).toBe(120);
    });
  });

  describe('Ashtottari Dasha with divisionalChartFactor', () => {
    it('D-1 returns same result as default', () => {
      const defaultResult = getAshtottariDashaBhukti(testJd, testPlace);
      const d1Result = getAshtottariDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1 });
      
      expect(d1Result.mahadashas.length).toBe(defaultResult.mahadashas.length);
      expect(d1Result.mahadashas[0]?.lord).toBe(defaultResult.mahadashas[0]?.lord);
    });

    it('D-9 produces valid 8-lord system', () => {
      const d9Result = getAshtottariDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9 });
      
      expect(d9Result.mahadashas.length).toBe(8);
      
      // Verify total is 108 years
      const totalYears = d9Result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
      expect(totalYears).toBe(108);
    });
  });

  describe('Yogini Dasha with divisionalChartFactor', () => {
    it('D-1 returns same result as default', () => {
      const defaultResult = getYoginiDashaBhukti(testJd, testPlace, { cycles: 1 });
      const d1Result = getYoginiDashaBhukti(testJd, testPlace, { cycles: 1, divisionalChartFactor: 1 });
      
      expect(d1Result.mahadashas.length).toBe(defaultResult.mahadashas.length);
      expect(d1Result.mahadashas[0]?.lord).toBe(defaultResult.mahadashas[0]?.lord);
    });

    it('D-9 produces valid 8-lord cycle system', () => {
      const d9Result = getYoginiDashaBhukti(testJd, testPlace, { cycles: 1, divisionalChartFactor: 9 });
      
      expect(d9Result.mahadashas.length).toBe(8);
      
      // Verify total is 36 years per cycle
      const totalYears = d9Result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
      expect(totalYears).toBe(36);
    });
  });
});
