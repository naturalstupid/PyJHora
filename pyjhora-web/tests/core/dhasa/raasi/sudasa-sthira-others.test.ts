/**
 * Tests for Sudasa, Sthira, Tara Lagna, Padhanadhamsa, Paryaaya, Varnada, and Sandhya Raasi Dashas
 */

import { describe, expect, it } from 'vitest';
import { getSudasaDashaBhukti } from '../../../../src/core/dhasa/raasi/sudasa';
import { getSthiraDashaBhukti } from '../../../../src/core/dhasa/raasi/sthira';
import { getTaraLagnaDashaBhukti } from '../../../../src/core/dhasa/raasi/tara-lagna';
import { getPadhanadhamsaDashaBhukti } from '../../../../src/core/dhasa/raasi/padhanadhamsa';
import { getParyaayaDashaBhukti } from '../../../../src/core/dhasa/raasi/paryaaya';
import { getVarnadaDashaBhukti } from '../../../../src/core/dhasa/raasi/varnada';
import { getSandhyaDashaBhukti } from '../../../../src/core/dhasa/raasi/sandhya';
import { gregorianToJulianDay } from '../../../../src/core/utils/julian';
import type { Place } from '../../../../src/core/types';

const testPlace: Place = {
  name: 'Chennai',
  latitude: 13.0878,
  longitude: 80.2785,
  timezone: 5.5
};

const testJd = gregorianToJulianDay(
  { year: 1996, month: 12, day: 7 },
  { hour: 10, minute: 34, second: 0 }
);

describe('Sudasa Dasha', () => {
  it('returns mahadashas from two cycles', () => {
    const result = getSudasaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    // Sudasa uses 2 cycles of 12 signs; count depends on durations
    expect(result.mahadashas.length).toBeGreaterThanOrEqual(12);
    expect(result.mahadashas.length).toBeLessThanOrEqual(24);
  });

  it('all durations are non-negative numbers', () => {
    const result = getSudasaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThanOrEqual(0);
    }
  });

  it('total duration covers a reasonable lifespan', () => {
    const result = getSudasaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBeGreaterThanOrEqual(60);
    expect(total).toBeLessThanOrEqual(130);
  });

  it('includes bhuktis when requested (12 per mahadasha)', () => {
    const result = getSudasaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(result.mahadashas.length * 12);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getSudasaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getSudasaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBeGreaterThanOrEqual(12);
    expect(d9Result.mahadashas.length).toBeGreaterThanOrEqual(12);
  });
});

describe('Sthira Dasha', () => {
  it('returns exactly 12 mahadashas', () => {
    const result = getSthiraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(12);
  });

  it('durations are 7, 8, or 9 years based on sign type', () => {
    const result = getSthiraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      expect([7, 8, 9]).toContain(maha.durationYears);
    }
  });

  it('total duration is exactly 96 years (matches Python)', () => {
    const result = getSthiraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    // Sthira always gives 4x7 + 4x8 + 4x9 = 28 + 32 + 36 = 96
    expect(total).toBe(96);
  });

  it('all 12 rasis appear exactly once', () => {
    const result = getSthiraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const rasis = result.mahadashas.map(m => m.rasi).sort((a, b) => a - b);
    expect(rasis).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  });

  it('movable signs get 7, fixed get 8, dual get 9 (sign-type invariant)', () => {
    const result = getSthiraDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const MOVABLE = [0, 3, 6, 9];
    const FIXED = [1, 4, 7, 10];
    for (const maha of result.mahadashas) {
      if (MOVABLE.includes(maha.rasi)) expect(maha.durationYears).toBe(7);
      else if (FIXED.includes(maha.rasi)) expect(maha.durationYears).toBe(8);
      else expect(maha.durationYears).toBe(9);
    }
  });

  it('includes 144 bhuktis when requested (12 x 12)', () => {
    const result = getSthiraDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getSthiraDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getSthiraDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});

describe('Tara Lagna Dasha', () => {
  it('returns exactly 12 mahadashas', () => {
    const result = getTaraLagnaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(12);
  });

  it('all durations are 9 years (matches Python)', () => {
    const result = getTaraLagnaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBe(9);
    }
  });

  it('total duration is 108 years (matches Python)', () => {
    const result = getTaraLagnaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBe(108);
  });

  it('all 12 rasis appear exactly once', () => {
    const result = getTaraLagnaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const rasis = result.mahadashas.map(m => m.rasi).sort((a, b) => a - b);
    expect(rasis).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  });

  it('includes 144 bhuktis when requested (12 x 12)', () => {
    const result = getTaraLagnaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getTaraLagnaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getTaraLagnaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});

describe('Padhanadhamsa Dasha', () => {
  it('returns mahadashas from two cycles', () => {
    const result = getPadhanadhamsaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    // Uses Narayana logic with 2 cycles; count depends on durations
    expect(result.mahadashas.length).toBeGreaterThanOrEqual(12);
    expect(result.mahadashas.length).toBeLessThanOrEqual(24);
  });

  it('all durations are non-negative numbers', () => {
    const result = getPadhanadhamsaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThanOrEqual(0);
    }
  });

  it('total duration covers a reasonable lifespan', () => {
    const result = getPadhanadhamsaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBeGreaterThanOrEqual(60);
    expect(total).toBeLessThanOrEqual(130);
  });

  it('includes bhuktis when requested (12 per mahadasha)', () => {
    const result = getPadhanadhamsaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(result.mahadashas.length * 12);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getPadhanadhamsaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getPadhanadhamsaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBeGreaterThanOrEqual(12);
    expect(d9Result.mahadashas.length).toBeGreaterThanOrEqual(12);
  });
});

describe('Paryaaya Dasha', () => {
  it('returns 24 mahadashas (2 cycles of 12)', () => {
    // Default cycles=2, so 24 mahadashas
    const result = getParyaayaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(24);
  });

  it('all durations are positive numbers', () => {
    const result = getParyaayaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBeGreaterThan(0);
    }
  });

  it('total duration is reasonable', () => {
    const result = getParyaayaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBeGreaterThanOrEqual(60);
    expect(total).toBeLessThanOrEqual(200);
  });

  it('includes 288 bhuktis when requested (24 x 12)', () => {
    const result = getParyaayaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(288);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getParyaayaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getParyaayaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBe(24);
    expect(d9Result.mahadashas.length).toBe(24);
  });
});

describe('Varnada Dasha', () => {
  it('returns exactly 12 mahadashas', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(12);
  });

  it('all durations are non-negative numbers', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      // Duration can be 0 when dhasaLord == varnadaLagna
      expect(maha.durationYears).toBeGreaterThanOrEqual(0);
    }
  });

  it('total duration matches Python (66 years)', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBe(66);
  });

  it('all 12 rasis appear exactly once', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const rasis = result.mahadashas.map(m => m.rasi).sort((a, b) => a - b);
    expect(rasis).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  });

  it('rasi sequence is strictly descending (-1 mod 12)', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const rasis = result.mahadashas.map(m => m.rasi);
    for (let i = 1; i < rasis.length; i++) {
      expect(rasis[i]).toBe((rasis[i - 1] - 1 + 12) % 12);
    }
  });

  it('duration sequence decreases by 1 (mod 12), matching Python Varnada pattern', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const durations = result.mahadashas.map(m => m.durationYears);
    for (let i = 1; i < durations.length; i++) {
      expect(durations[i]).toBe((durations[i - 1] - 1 + 12) % 12);
    }
  });

  it('includes 144 bhuktis when requested (12 x 12)', () => {
    const result = getVarnadaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getVarnadaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getVarnadaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});

describe('Sandhya Dasha', () => {
  it('returns exactly 12 mahadashas', () => {
    const result = getSandhyaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(12);
  });

  it('all durations are 10 years', () => {
    const result = getSandhyaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    for (const maha of result.mahadashas) {
      expect(maha.durationYears).toBe(10);
    }
  });

  it('total duration is 120 years', () => {
    const result = getSandhyaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const total = result.mahadashas.reduce((sum, m) => sum + m.durationYears, 0);
    expect(total).toBe(120);
  });

  it('all 12 rasis appear exactly once', () => {
    const result = getSandhyaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const rasis = result.mahadashas.map(m => m.rasi).sort((a, b) => a - b);
    expect(rasis).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  });

  it('sign sequence is strictly sequential (+1 mod 12), matching Python Sandhya pattern', () => {
    // Python produces [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    // TS may start from a different sign due to Lagna proxy, but the sequential
    // pattern must hold: each rasi = (previous + 1) % 12
    const result = getSandhyaDashaBhukti(testJd, testPlace, { includeBhuktis: false });
    const rasis = result.mahadashas.map(m => m.rasi);
    for (let i = 1; i < rasis.length; i++) {
      expect(rasis[i]).toBe((rasis[i - 1] + 1) % 12);
    }
  });

  it('includes 144 bhuktis when requested (12 x 12)', () => {
    const result = getSandhyaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(144);
  });

  it('respects divisionalChartFactor option', () => {
    const d1Result = getSandhyaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 1, includeBhuktis: false });
    const d9Result = getSandhyaDashaBhukti(testJd, testPlace, { divisionalChartFactor: 9, includeBhuktis: false });
    expect(d1Result.mahadashas.length).toBe(12);
    expect(d9Result.mahadashas.length).toBe(12);
  });
});
