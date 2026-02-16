/**
 * Structural tests for Patyayini Annual Dhasa.
 */
import { describe, expect, it } from 'vitest';
import { getPatyayiniDhasa } from '../../../../src/core/dhasa/annual/patyayini';
import type { PlanetPosition } from '../../../../src/core/horoscope/charts';
import { AVERAGE_GREGORIAN_YEAR } from '../../../../src/core/constants';

// Mock annual chart positions (7 planets Sun–Saturn + Rahu + Ketu)
const mockPositions: PlanetPosition[] = [
  { planet: -1, rasi: 3, longitude: 15.0 },  // Lagna
  { planet: 0, rasi: 7, longitude: 12.5 },   // Sun
  { planet: 1, rasi: 1, longitude: 22.3 },   // Moon
  { planet: 2, rasi: 4, longitude: 5.0 },    // Mars
  { planet: 3, rasi: 8, longitude: 28.7 },   // Mercury
  { planet: 4, rasi: 2, longitude: 18.0 },   // Jupiter
  { planet: 5, rasi: 10, longitude: 9.5 },   // Venus
  { planet: 6, rasi: 6, longitude: 1.2 },    // Saturn
  { planet: 7, rasi: 5, longitude: 20.1 },   // Rahu
  { planet: 8, rasi: 11, longitude: 20.1 },  // Ketu
];

const jdYear = 2450424.0; // Arbitrary annual return JD

describe('Patyayini Annual Dhasa', () => {
  it('should produce 8 mahadasha periods (Lagna + Sun to Saturn, excluding Rahu/Ketu)', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    expect(result.mahadashas).toHaveLength(8);
  });

  it('should not include Rahu or Ketu in dashas', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    for (const d of result.mahadashas) {
      expect(d.lord).not.toBe(7); // Rahu
      expect(d.lord).not.toBe(8); // Ketu
    }
  });

  it('should have positive durations for all dashas', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    for (const d of result.mahadashas) {
      expect(d.durationDays).toBeGreaterThan(0);
    }
  });

  it('should have total durations summing close to one year', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    const total = result.mahadashas.reduce((acc, d) => acc + d.durationDays, 0);
    expect(total).toBeCloseTo(AVERAGE_GREGORIAN_YEAR, 0);
  });

  it('should have consecutive start dates', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('should produce bhuktis for each mahadasha', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    expect(result.bhuktis.length).toBe(8 * 8); // 8 bhuktis per 8 dashas
  });

  it('should have valid date strings', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    for (const d of result.mahadashas) {
      expect(d.startDate).toMatch(/^\d{4}-\d{2}-\d{2}/);
    }
  });

  it('should have lord names set', () => {
    const result = getPatyayiniDhasa(jdYear, mockPositions);
    for (const d of result.mahadashas) {
      expect(d.lordName).toBeTruthy();
      expect(d.lordName).not.toBe('');
    }
  });
});
