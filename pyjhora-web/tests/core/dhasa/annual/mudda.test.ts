/**
 * Structural tests for Mudda (Varsha Vimsottari) Annual Dhasa.
 * Birth data: 1996/12/7, 10:34, Hyderabad (17.385, 78.487, +5.5)
 */
import { describe, expect, it } from 'vitest';
import { getMuddaDhasa } from '../../../../src/core/dhasa/annual/mudda';
import type { PlanetPosition } from '../../../../src/core/horoscope/charts';
import {
  VARSHA_VIMSOTTARI_DAYS,
  VARSHA_VIMSOTTARI_ADHIPATI_LIST,
} from '../../../../src/core/constants';

// Mock D1 positions for testing (deterministic)
const mockPositions: PlanetPosition[] = [
  { planet: -1, rasi: 0, longitude: 15.0 },   // Lagna (Aries)
  { planet: 0, rasi: 7, longitude: 21.5 },     // Sun (Scorpio)
  { planet: 1, rasi: 3, longitude: 10.3 },     // Moon (Cancer)
  { planet: 2, rasi: 8, longitude: 5.0 },      // Mars
  { planet: 3, rasi: 7, longitude: 28.7 },     // Mercury
  { planet: 4, rasi: 8, longitude: 12.0 },     // Jupiter
  { planet: 5, rasi: 9, longitude: 27.5 },     // Venus
  { planet: 6, rasi: 11, longitude: 8.3 },     // Saturn
  { planet: 7, rasi: 5, longitude: 20.1 },     // Rahu
  { planet: 8, rasi: 11, longitude: 20.1 },    // Ketu
];

const jd = 2450424.940278;
const years = 5; // 5th annual chart

describe('Mudda (Varsha Vimsottari) Dhasa', () => {
  it('should produce 9 mahadasha periods', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    expect(result.mahadashas).toHaveLength(9);
  });

  it('should have lords from the Varsha Vimsottari adhipati list', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    for (const d of result.mahadashas) {
      expect(VARSHA_VIMSOTTARI_ADHIPATI_LIST).toContain(d.lord);
    }
  });

  it('should have each lord appear exactly once', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    const lords = result.mahadashas.map(d => d.lord);
    const unique = new Set(lords);
    expect(unique.size).toBe(9);
  });

  it('should have consecutive start dates', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('should have positive durations', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    for (const d of result.mahadashas) {
      expect(d.durationDays).toBeGreaterThan(0);
    }
  });

  it('should produce 81 bhuktis (9 per mahadasha) when requested', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, true);
    expect(result.bhuktis).toHaveLength(81);
  });

  it('should have 9 bhuktis per mahadasha', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, true);
    for (const dasha of result.mahadashas) {
      const dashaBhuktis = result.bhuktis.filter(b => b.dashaLord === dasha.lord);
      expect(dashaBhuktis).toHaveLength(9);
    }
  });

  it('should have valid date strings', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    for (const d of result.mahadashas) {
      expect(d.startDate).toMatch(/^\d{4}-\d{2}-\d{2}/);
    }
  });

  it('should have lord names set', () => {
    const result = getMuddaDhasa(jd, mockPositions, years, false);
    for (const d of result.mahadashas) {
      expect(d.lordName).toBeTruthy();
    }
  });

  it('should work for year 0 (birth year)', () => {
    const result = getMuddaDhasa(jd, mockPositions, 0, false);
    expect(result.mahadashas).toHaveLength(9);
  });
});
