/**
 * Tests for dhasa applicability checks.
 */
import { describe, expect, it } from 'vitest';
import {
  isAshtottariApplicable,
  isChaturaseethiApplicable,
  isDwadasottariApplicable,
  isDwisatpathiApplicable,
  isPanchottariApplicable,
  isSataabdikaApplicable,
  isShastihayaniApplicable,
  getApplicableDhasas,
} from '../../../../src/core/dhasa/graha/applicability';
import type { PlanetPosition } from '../../../../src/core/horoscope/charts';

// Helper to create minimal positions
function makePositions(overrides: Partial<Record<number, { rasi: number; longitude: number }>>): PlanetPosition[] {
  const defaults: PlanetPosition[] = [
    { planet: -1, rasi: 0, longitude: 15.0 },   // Lagna (Aries)
    { planet: 0, rasi: 4, longitude: 10.5 },     // Sun (Leo)
    { planet: 1, rasi: 3, longitude: 22.3 },     // Moon (Cancer)
    { planet: 2, rasi: 7, longitude: 5.0 },      // Mars (Scorpio)
    { planet: 3, rasi: 5, longitude: 18.7 },     // Mercury (Virgo)
    { planet: 4, rasi: 8, longitude: 12.0 },     // Jupiter (Sagittarius)
    { planet: 5, rasi: 1, longitude: 27.5 },     // Venus (Taurus)
    { planet: 6, rasi: 11, longitude: 8.3 },     // Saturn (Pisces)
    { planet: 7, rasi: 5, longitude: 20.1 },     // Rahu (Virgo)
    { planet: 8, rasi: 11, longitude: 20.1 },    // Ketu (Pisces)
  ];
  for (const [idx, val] of Object.entries(overrides)) {
    const i = Number(idx);
    if (defaults[i]) {
      defaults[i] = { ...defaults[i]!, ...val };
    }
  }
  return defaults;
}

describe('Dhasa Applicability Checks', () => {
  describe('isShastihayaniApplicable', () => {
    it('should return true when Sun is in Lagna sign', () => {
      // Lagna in Aries(0), Sun in Aries(0)
      const pos = makePositions({ 1: { rasi: 0, longitude: 10.0 } });
      expect(isShastihayaniApplicable(pos)).toBe(true);
    });

    it('should return false when Sun is not in Lagna sign', () => {
      // Lagna in Aries(0), Sun in Leo(4) — default
      const pos = makePositions({});
      expect(isShastihayaniApplicable(pos)).toBe(false);
    });
  });

  describe('isDwadasottariApplicable', () => {
    it('should return true when navamsa Lagna is Taurus', () => {
      const navamsa = makePositions({ 0: { rasi: 1, longitude: 15.0 } });
      expect(isDwadasottariApplicable(navamsa)).toBe(true);
    });

    it('should return true when navamsa Lagna is Libra', () => {
      const navamsa = makePositions({ 0: { rasi: 6, longitude: 15.0 } });
      expect(isDwadasottariApplicable(navamsa)).toBe(true);
    });

    it('should return false when navamsa Lagna is Aries', () => {
      const navamsa = makePositions({ 0: { rasi: 0, longitude: 15.0 } });
      expect(isDwadasottariApplicable(navamsa)).toBe(false);
    });
  });

  describe('isPanchottariApplicable', () => {
    it('should return true when dwadasamsa Lagna is Cancer', () => {
      const d12 = makePositions({ 0: { rasi: 3, longitude: 15.0 } });
      expect(isPanchottariApplicable(d12)).toBe(true);
    });

    it('should return false when dwadasamsa Lagna is not Cancer', () => {
      const d12 = makePositions({ 0: { rasi: 0, longitude: 15.0 } });
      expect(isPanchottariApplicable(d12)).toBe(false);
    });
  });

  describe('isSataabdikaApplicable', () => {
    it('should return true when rasi and navamsa lagnas match', () => {
      const rasi = makePositions({ 0: { rasi: 5, longitude: 15.0 } });
      const navamsa = makePositions({ 0: { rasi: 5, longitude: 10.0 } });
      expect(isSataabdikaApplicable(rasi, navamsa)).toBe(true);
    });

    it('should return false when rasi and navamsa lagnas differ', () => {
      const rasi = makePositions({ 0: { rasi: 5, longitude: 15.0 } });
      const navamsa = makePositions({ 0: { rasi: 8, longitude: 10.0 } });
      expect(isSataabdikaApplicable(rasi, navamsa)).toBe(false);
    });
  });

  describe('isChaturaseethiApplicable', () => {
    it('should return true when 10th lord is in 10th house', () => {
      // Lagna Aries(0), 10th house = Capricorn(9), lord = Saturn(6)
      // Place Saturn in Capricorn(9)
      const pos = makePositions({ 7: { rasi: 9, longitude: 8.3 } });
      // Saturn is at index 7 in positions (planet 6)
      expect(isChaturaseethiApplicable(pos)).toBe(true);
    });

    it('should return false when 10th lord is not in 10th house', () => {
      // Default: Saturn in Pisces(11), not Capricorn(9)
      const pos = makePositions({});
      expect(isChaturaseethiApplicable(pos)).toBe(false);
    });
  });

  describe('isDwisatpathiApplicable', () => {
    it('should return true when lagna lord is in 7th house', () => {
      // Lagna Aries(0), lord = Mars(2), 7th house = Libra(6)
      // Place Mars in Libra(6)
      const pos = makePositions({ 3: { rasi: 6, longitude: 5.0 } });
      expect(isDwisatpathiApplicable(pos)).toBe(true);
    });

    it('should return false when neither exchange exists', () => {
      // Default positions: Mars in Scorpio(7), Venus(Libra lord) in Taurus(1)
      const pos = makePositions({});
      expect(isDwisatpathiApplicable(pos)).toBe(false);
    });
  });

  describe('isAshtottariApplicable', () => {
    it('should return a boolean', () => {
      const pos = makePositions({});
      const result = isAshtottariApplicable(pos);
      expect(typeof result).toBe('boolean');
    });

    it('should return false when Rahu is in Ascendant', () => {
      const pos = makePositions({ 8: { rasi: 0, longitude: 20.0 } });
      expect(isAshtottariApplicable(pos)).toBe(false);
    });
  });

  describe('getApplicableDhasas', () => {
    it('should return an array', () => {
      const pos = makePositions({});
      const result = getApplicableDhasas(pos);
      expect(Array.isArray(result)).toBe(true);
    });

    it('should only contain valid dhasa names', () => {
      const validNames = [
        'ashtottari', 'chaturaseethi', 'dwadasottari',
        'dwisatpathi', 'panchottari', 'sataabdika', 'shastihayani',
      ];
      const pos = makePositions({});
      const result = getApplicableDhasas(pos);
      for (const name of result) {
        expect(validNames).toContain(name);
      }
    });

    it('should include shastihayani when Sun is in Lagna', () => {
      const pos = makePositions({ 1: { rasi: 0, longitude: 10.0 } });
      const result = getApplicableDhasas(pos);
      expect(result).toContain('shastihayani');
    });
  });
});
