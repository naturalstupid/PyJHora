/**
 * Tests for angle utilities
 */

import {
    almostEqual,
    angularDistance,
    countRasis,
    fromDMS,
    longitudeInSign,
    nakshatraFromLongitude,
    normalizeDegrees,
    rasiFromLongitude,
    toDMS
} from '@core/utils/angle';
import { describe, expect, it } from 'vitest';

describe('Angle Utilities', () => {
  describe('normalizeDegrees', () => {
    it('should normalize positive angles', () => {
      expect(normalizeDegrees(0)).toBe(0);
      expect(normalizeDegrees(180)).toBe(180);
      expect(normalizeDegrees(360)).toBe(0);
      expect(normalizeDegrees(450)).toBe(90);
    });

    it('should normalize negative angles', () => {
      expect(normalizeDegrees(-90)).toBe(270);
      expect(normalizeDegrees(-180)).toBe(180);
      expect(normalizeDegrees(-360)).toBe(0);
    });
  });

  describe('rasiFromLongitude', () => {
    it('should return correct rasi indices', () => {
      // Aries: 0-30°
      expect(rasiFromLongitude(0)).toBe(0);
      expect(rasiFromLongitude(15)).toBe(0);
      expect(rasiFromLongitude(29.99)).toBe(0);
      
      // Taurus: 30-60°
      expect(rasiFromLongitude(30)).toBe(1);
      expect(rasiFromLongitude(45)).toBe(1);
      
      // Pisces: 330-360°
      expect(rasiFromLongitude(330)).toBe(11);
      expect(rasiFromLongitude(359)).toBe(11);
    });
  });

  describe('longitudeInSign', () => {
    it('should return position within sign', () => {
      expect(longitudeInSign(0)).toBe(0);
      expect(longitudeInSign(15)).toBe(15);
      expect(longitudeInSign(45)).toBe(15); // 45 - 30 = 15 in Taurus
      expect(longitudeInSign(94.3166)).toBeCloseTo(4.3166, 4); // Test from Exercise 1
    });
  });

  describe('DMS conversions', () => {
    it('should convert decimal to DMS', () => {
      const dms = toDMS(94.3166);
      expect(dms.degrees).toBe(94);
      expect(dms.minutes).toBe(18);
      expect(dms.seconds).toBeCloseTo(60, 0); // 0.3166 * 60 = 18.996'
    });

    it('should be reversible', () => {
      const original = 123.456;
      const dms = toDMS(original);
      const result = fromDMS(dms);
      expect(result).toBeCloseTo(original, 2);
    });
  });

  describe('angularDistance', () => {
    it('should calculate shortest angular distance', () => {
      expect(angularDistance(0, 90)).toBe(90);
      expect(angularDistance(0, 180)).toBe(180);
      expect(angularDistance(0, 270)).toBe(90); // Shortest path is 90° backward
      expect(angularDistance(10, 350)).toBe(20);
    });
  });

  describe('nakshatraFromLongitude', () => {
    it('should calculate nakshatra and pada', () => {
      // Ashwini starts at 0°
      const result1 = nakshatraFromLongitude(0);
      expect(result1.nakshatra).toBe(0); // Ashwini
      expect(result1.pada).toBe(1);

      // Each nakshatra is 13°20' = 13.333°
      const result2 = nakshatraFromLongitude(14);
      expect(result2.nakshatra).toBe(1); // Bharani
      expect(result2.pada).toBe(1);
    });
  });

  describe('almostEqual', () => {
    it('should compare with tolerance', () => {
      expect(almostEqual(1.0, 1.0000000001)).toBe(true);
      expect(almostEqual(1.0, 1.1)).toBe(false);
      expect(almostEqual(1.0, 1.05, 0.1)).toBe(true);
    });
  });

  describe('countRasis', () => {
    it('should count rasis inclusively (same sign = 1)', () => {
      // Python: count_rasis(0, 0) = ((0 + 12 - 0) % 12) + 1 = 1
      expect(countRasis(0, 0)).toBe(1);
      expect(countRasis(5, 5)).toBe(1);
      expect(countRasis(11, 11)).toBe(1);
    });

    it('should count forward from one rasi to another', () => {
      // Python: count_rasis(0, 1) = ((1 + 12 - 0) % 12) + 1 = 2
      expect(countRasis(0, 1)).toBe(2);
      // Python: count_rasis(0, 2) = ((2 + 12 - 0) % 12) + 1 = 3
      expect(countRasis(0, 2)).toBe(3);
      // Python: count_rasis(0, 11) = ((11 + 12 - 0) % 12) + 1 = 12
      expect(countRasis(0, 11)).toBe(12);
    });

    it('should handle wraparound correctly', () => {
      // From Pisces (11) to Aries (0) = 2 signs
      // Python: count_rasis(11, 0) = ((0 + 12 - 11) % 12) + 1 = 2
      expect(countRasis(11, 0)).toBe(2);
      // From Scorpio (7) to Aries (0) = 6 signs
      // Python: count_rasis(7, 0) = ((0 + 12 - 7) % 12) + 1 = 6
      expect(countRasis(7, 0)).toBe(6);
    });

    it('should count backward when dir=-1', () => {
      // Python: count_rasis(0, 2, dir=-1) = ((0 + 12 - 2) % 12) + 1 = 11
      expect(countRasis(0, 2, -1)).toBe(11);
      // Python: count_rasis(2, 0, dir=-1) = ((2 + 12 - 0) % 12) + 1 = 3
      expect(countRasis(2, 0, -1)).toBe(3);
    });

    it('should match Python count_rasis examples from arudhas.py', () => {
      // These are the exact patterns used in bhava_arudhas_from_planet_positions
      // When counting from house to lord's position
      expect(countRasis(0, 4)).toBe(5);  // 1st house to Leo (lord's position)
      expect(countRasis(3, 6)).toBe(4);  // 4th house to Libra
      expect(countRasis(8, 2)).toBe(7);  // 9th house to Gemini (wraparound)
    });
  });
});
