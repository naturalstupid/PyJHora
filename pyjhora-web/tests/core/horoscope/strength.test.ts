/**
 * Tests for Shadbala (Six-fold Strength) Calculations
 * Ported from PyJHora strength.py
 */

import { describe, it, expect } from 'vitest';
import type { PlanetPosition } from '../../../src/core/horoscope/charts';
import type { Place } from '../../../src/core/types';
import {
  calculateUchchaBala,
  calculateKendraBala,
  calculateDreshkonBala,
  calculateOjayugamaBala,
  calculateNaisargikaBala,
  calculateHarshaBala,
  calculatePanchaVargeeyaBala,
  calculateDwadhasaVargeeyaBala,
  calculateShadBala,
  calculateBhavaBala,
  calculatePlanetAspectRelationshipTable
} from '../../../src/core/horoscope/strength';
import { getDivisionalChart } from '../../../src/core/horoscope/charts';
import { gregorianToJulianDay } from '../../../src/core/utils/julian';

// Test data: Sample horoscope
const testPlace: Place = {
  name: 'Chennai',
  latitude: 13.0878,
  longitude: 80.2785,
  timezone: 5.5
};

const testDate = { year: 1996, month: 12, day: 7 };
const testTime = { hour: 10, minute: 34, second: 0 };

// Sample planet positions (approximate for testing)
const sampleD1Positions: PlanetPosition[] = [
  { planet: -1, rasi: 9, longitude: 15 },  // Ascendant in Capricorn
  { planet: 0, rasi: 7, longitude: 22 },   // Sun in Scorpio
  { planet: 1, rasi: 6, longitude: 8 },    // Moon in Libra
  { planet: 2, rasi: 5, longitude: 12 },   // Mars in Virgo
  { planet: 3, rasi: 7, longitude: 5 },    // Mercury in Scorpio
  { planet: 4, rasi: 8, longitude: 18 },   // Jupiter in Sagittarius
  { planet: 5, rasi: 9, longitude: 25 },   // Venus in Capricorn
  { planet: 6, rasi: 11, longitude: 10 },  // Saturn in Pisces
  { planet: 7, rasi: 5, longitude: 20 },   // Rahu in Virgo
  { planet: 8, rasi: 11, longitude: 20 }   // Ketu in Pisces
];

describe('Shadbala Calculations', () => {
  describe('Uchcha Bala (Exaltation Strength)', () => {
    it('should calculate uchcha bala for all 7 planets', () => {
      const ub = calculateUchchaBala(sampleD1Positions);

      expect(ub).toHaveLength(7);
      // All values should be between 0 and 60 (Saravali formula: pd/3, max 180/3=60)
      ub.forEach(val => {
        expect(val).toBeGreaterThanOrEqual(0);
        expect(val).toBeLessThanOrEqual(60);
      });
    });

    it('should give higher strength to exalted planets', () => {
      // Sun exalted in Aries at 10 degrees
      const exaltedSunPositions: PlanetPosition[] = [
        ...sampleD1Positions.filter(p => p.planet !== 0),
        { planet: 0, rasi: 0, longitude: 10 } // Sun at 10 Aries (deep exaltation)
      ];

      const ub = calculateUchchaBala(exaltedSunPositions);
      // Exalted Sun should have high uchcha bala (close to 60)
      expect(ub[0]).toBeGreaterThan(50);
    });
  });

  describe('Kendra Bala (Angular House Strength)', () => {
    it('should calculate kendra bala for all 7 planets', () => {
      const kb = calculateKendraBala(sampleD1Positions);

      expect(kb).toHaveLength(7);
      // Values should be 60, 30, 15, or 0
      kb.forEach(val => {
        expect([0, 15, 30, 60]).toContain(val);
      });
    });

    it('should give 60 points to planets in kendras', () => {
      // Ascendant is in Capricorn (rasi 9)
      // Kendras are 1, 4, 7, 10 from Ascendant = rasis 9, 0, 3, 6
      // Venus is in Capricorn (rasi 9) - should get 60
      const kb = calculateKendraBala(sampleD1Positions);
      expect(kb[5]).toBe(60); // Venus in lagna (kendra)
    });
  });

  describe('Dreshkon Bala', () => {
    it('should calculate dreshkon bala for all 7 planets', () => {
      const db = calculateDreshkonBala(sampleD1Positions);

      expect(db).toHaveLength(7);
      // Values should be 0 or 15
      db.forEach(val => {
        expect([0, 15]).toContain(val);
      });
    });
  });

  describe('Ojayugama Bala (Odd-Even Strength)', () => {
    it('should calculate ojayugama bala for all 7 planets', () => {
      const d9Positions = getDivisionalChart(sampleD1Positions, 9);
      const ob = calculateOjayugamaBala(sampleD1Positions, d9Positions);

      expect(ob).toHaveLength(7);
      // Values should be 0, 15, or 30
      ob.forEach(val => {
        expect([0, 15, 30]).toContain(val);
      });
    });
  });

  describe('Naisargika Bala (Natural Strength)', () => {
    it('should return fixed natural strength values', () => {
      const nb = calculateNaisargikaBala();

      expect(nb).toHaveLength(7);
      expect(nb[0]).toBe(60.0);    // Sun
      expect(nb[1]).toBe(51.43);   // Moon
      expect(nb[2]).toBe(17.14);   // Mars
      expect(nb[3]).toBe(25.71);   // Mercury
      expect(nb[4]).toBe(34.29);   // Jupiter
      expect(nb[5]).toBe(42.86);   // Venus
      expect(nb[6]).toBe(8.57);    // Saturn
    });
  });

  describe('Harsha Bala', () => {
    it('should calculate harsha bala for all 7 planets', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const hb = calculateHarshaBala(jd, testPlace, sampleD1Positions);

      expect(Object.keys(hb)).toHaveLength(7);
      // Values should be multiples of 5 (0, 5, 10, 15, 20)
      Object.values(hb).forEach(val => {
        expect(val % 5).toBe(0);
        expect(val).toBeGreaterThanOrEqual(0);
        expect(val).toBeLessThanOrEqual(20);
      });
    });
  });

  describe('Pancha Vargeeya Bala', () => {
    it('should calculate pancha vargeeya bala for all 7 planets', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const pvb = calculatePanchaVargeeyaBala(jd, testPlace, sampleD1Positions);

      expect(Object.keys(pvb)).toHaveLength(7);
      // All values should be positive
      Object.values(pvb).forEach(val => {
        expect(val).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('Dwadhasa Vargeeya Bala', () => {
    it('should calculate dwadhasa vargeeya bala for all 7 planets', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const dvb = calculateDwadhasaVargeeyaBala(jd, testPlace, sampleD1Positions);

      expect(Object.keys(dvb)).toHaveLength(7);
      // Values should be between 0 and 12 (max 12 vargas)
      Object.values(dvb).forEach(val => {
        expect(val).toBeGreaterThanOrEqual(0);
        expect(val).toBeLessThanOrEqual(12);
      });
    });
  });

  describe('Shadbala (Complete Six-fold Strength)', () => {
    it('should calculate all six components of shadbala', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const sb = calculateShadBala(jd, testPlace, sampleD1Positions);

      expect(sb.sthanaBala).toHaveLength(7);
      expect(sb.kaalaBala).toHaveLength(7);
      expect(sb.digBala).toHaveLength(7);
      expect(sb.cheshtaBala).toHaveLength(7);
      expect(sb.naisargikaBala).toHaveLength(7);
      expect(sb.drikBala).toHaveLength(7);
      expect(sb.total).toHaveLength(7);
      expect(sb.rupas).toHaveLength(7);
      expect(sb.strength).toHaveLength(7);
    });

    it('should have total as sum of all components', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const sb = calculateShadBala(jd, testPlace, sampleD1Positions);

      for (let i = 0; i < 7; i++) {
        const expectedTotal =
          sb.sthanaBala[i] +
          sb.kaalaBala[i] +
          sb.digBala[i] +
          sb.cheshtaBala[i] +
          sb.naisargikaBala[i] +
          sb.drikBala[i];

        // Allow small floating point difference
        expect(Math.abs(sb.total[i] - expectedTotal)).toBeLessThan(0.1);
      }
    });

    it('should calculate rupas as total/60', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const sb = calculateShadBala(jd, testPlace, sampleD1Positions);

      for (let i = 0; i < 7; i++) {
        const expectedRupa = sb.total[i] / 60;
        expect(Math.abs(sb.rupas[i] - expectedRupa)).toBeLessThan(0.1);
      }
    });
  });

  describe('Bhava Bala (House Strength)', () => {
    it('should calculate bhava bala for all 12 houses', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const bb = calculateBhavaBala(jd, testPlace, sampleD1Positions);

      expect(bb.total).toHaveLength(12);
      expect(bb.rupas).toHaveLength(12);
      expect(bb.strength).toHaveLength(12);
    });

    it('should have positive total values', () => {
      const jd = gregorianToJulianDay(testDate, testTime);
      const bb = calculateBhavaBala(jd, testPlace, sampleD1Positions);

      bb.total.forEach(val => {
        expect(val).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('Planet Aspect Relationship Table', () => {
    it('should calculate aspect table for 9 planets', () => {
      const table = calculatePlanetAspectRelationshipTable(sampleD1Positions, false);

      expect(table).toHaveLength(9);
      table.forEach(row => {
        expect(row).toHaveLength(9);
      });
    });

    it('should include houses when requested', () => {
      const table = calculatePlanetAspectRelationshipTable(sampleD1Positions, true);

      // Table is transposed: 9 aspecting planets as rows, 21 aspected entities as columns
      expect(table).toHaveLength(9);
      table.forEach(row => {
        expect(row).toHaveLength(21); // 9 planets + 12 houses
      });
    });

    it('should have self-aspect as 0 or specific value', () => {
      const table = calculatePlanetAspectRelationshipTable(sampleD1Positions, false);

      // Diagonal should be calculated based on 0 degree aspect
      for (let i = 0; i < 9; i++) {
        expect(typeof table[i][i]).toBe('number');
      }
    });
  });
});

describe('BV Raman Example Verification', () => {
  // Test case from BV Raman's book
  const bvRamanDate = { year: 1918, month: 10, day: 16 };
  const bvRamanTime = { hour: 14, minute: 22, second: 16 };
  const bvRamanPlace: Place = {
    name: 'BVRamanExample',
    latitude: 13,
    longitude: 77 + 35/60,
    timezone: 5.5
  };

  it('should produce reasonable shadbala values', () => {
    const jd = gregorianToJulianDay(bvRamanDate, bvRamanTime);

    // Sample positions for BV Raman chart (approximate)
    const bvRamanPositions: PlanetPosition[] = [
      { planet: -1, rasi: 9, longitude: 15 },
      { planet: 0, rasi: 5, longitude: 29 },
      { planet: 1, rasi: 9, longitude: 2 },
      { planet: 2, rasi: 7, longitude: 22 },
      { planet: 3, rasi: 6, longitude: 13 },
      { planet: 4, rasi: 1, longitude: 24 },
      { planet: 5, rasi: 6, longitude: 6 },
      { planet: 6, rasi: 3, longitude: 20 },
      { planet: 7, rasi: 8, longitude: 14 },
      { planet: 8, rasi: 2, longitude: 14 }
    ];

    const sb = calculateShadBala(jd, bvRamanPlace, bvRamanPositions);

    // Verify all components exist and are reasonable
    expect(sb.total.length).toBe(7);
    sb.total.forEach(val => {
      expect(val).toBeGreaterThan(0);
      expect(val).toBeLessThan(1000); // Reasonable upper bound
    });
  });
});
