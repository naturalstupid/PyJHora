import { describe, expect, it } from 'vitest';
import { getBuddhiGathiDashaBhukti } from '../../../../src/core/dhasa/graha/buddhi-gathi';
import type { Place } from '../../../../src/core/types';

describe('Buddhi Gathi Dasha', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  // Sample planet positions with ascendant and multiple planets per house
  const samplePlanetPositions = [
    { planet: -1, rasi: 0, longitude: 15 },  // Ascendant in Aries
    { planet: 0, rasi: 4, longitude: 25 },   // Sun in Leo
    { planet: 1, rasi: 3, longitude: 18 },   // Moon in Cancer (4th from Asc - starting point)
    { planet: 2, rasi: 3, longitude: 10 },   // Mars in Cancer (same house as Moon)
    { planet: 3, rasi: 5, longitude: 22 },   // Mercury in Virgo
    { planet: 4, rasi: 8, longitude: 12 },   // Jupiter in Sagittarius
    { planet: 5, rasi: 6, longitude: 20 },   // Venus in Libra
    { planet: 6, rasi: 9, longitude: 8 },    // Saturn in Capricorn
    { planet: 7, rasi: 11, longitude: 15 },  // Rahu in Pisces
  ];

  describe('Dasha Progression', () => {
    it('should return dasha progression', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions);
      expect(result.dashaProgression).toBeDefined();
      expect(result.dashaProgression.length).toBeGreaterThan(0);
    });

    it('should start from 4th house planets', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions);
      // First dasha should be from the 4th house from ascendant
      // Ascendant is in Aries (0), 4th house is Cancer (3)
      // Moon (1) and Mars (2) are in Cancer, Moon has higher longitude
      if (result.dashaProgression.length > 0) {
        const firstPlanet = result.dashaProgression[0]!.planet;
        expect([1, 2]).toContain(firstPlanet); // Moon or Mars
      }
    });

    it('should order planets by decreasing longitude within same house', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions);
      // In Cancer (rasi 3): Moon at 18°, Mars at 10°
      // Moon should come before Mars
      const moonIndex = result.dashaProgression.findIndex(d => d.planet === 1);
      const marsIndex = result.dashaProgression.findIndex(d => d.planet === 2);

      if (moonIndex !== -1 && marsIndex !== -1) {
        expect(moonIndex).toBeLessThan(marsIndex);
      }
    });

    it('should calculate total duration', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions);
      expect(result.totalDuration).toBeGreaterThan(0);
    });
  });

  describe('Dasha Structure', () => {
    it('should return valid mahadasha structure', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: false
      });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBeGreaterThan(0);
    });

    it('should have duration based on house count', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: false
      });

      for (const dasha of result.mahadashas) {
        // Duration should be 0-11 (house count)
        expect(dasha.durationYears).toBeGreaterThanOrEqual(0);
        expect(dasha.durationYears).toBeLessThanOrEqual(11);
      }
    });

    it('should have increasing start JDs', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: false
      });

      for (let i = 1; i < result.mahadashas.length; i++) {
        expect(result.mahadashas[i]!.startJd).toBeGreaterThanOrEqual(result.mahadashas[i - 1]!.startJd);
      }
    });

    it('should run 2 cycles', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: false
      });

      const numPlanets = result.dashaProgression.length;
      if (numPlanets > 0) {
        // Should have up to 2× the number of dashas as planets (2 cycles)
        expect(result.mahadashas.length).toBeLessThanOrEqual(numPlanets * 2);
      }
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: true
      });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should not include bhuktis when not requested', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: false
      });
      expect(result.bhuktis).toBeUndefined();
    });

    it('should have valid bhukti structure', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: true
      });

      if (result.bhuktis && result.bhuktis.length > 0) {
        const firstBhukti = result.bhuktis[0]!;

        expect(firstBhukti.dashaLord).toBeDefined();
        expect(firstBhukti.dashaLordName).toBeDefined();
        expect(firstBhukti.bhuktiLord).toBeDefined();
        expect(firstBhukti.bhuktiLordName).toBeDefined();
        expect(firstBhukti.startJd).toBeDefined();
        expect(firstBhukti.startDate).toBeDefined();
        expect(firstBhukti.durationYears).toBeGreaterThanOrEqual(0);
      }
    });

    it('should rotate through all planets for bhuktis', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions, {
        includeBhuktis: true
      });

      if (result.bhuktis && result.bhuktis.length > 0) {
        const numPlanets = result.dashaProgression.length;
        const firstDashaLord = result.mahadashas[0]!.lord;
        const firstDashaBhuktis = result.bhuktis.filter(b => b.dashaLord === firstDashaLord);

        // Should have bhuktis (may repeat due to 2 cycles)
        // In each dasha occurrence, there should be numPlanets bhuktis
        expect(firstDashaBhuktis.length).toBeGreaterThanOrEqual(numPlanets);
      }
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty planet positions', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, []);
      expect(result.dashaProgression).toEqual([]);
      expect(result.mahadashas).toEqual([]);
      expect(result.totalDuration).toBe(0);
    });

    it('should handle positions without ascendant', () => {
      const positionsNoAsc = samplePlanetPositions.filter(p => p.planet !== -1);
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, positionsNoAsc);

      expect(result.dashaProgression).toBeDefined();
      expect(result.mahadashas).toBeDefined();
    });

    it('should handle single planet position', () => {
      const singlePlanet = [
        { planet: -1, rasi: 0, longitude: 15 },  // Ascendant
        { planet: 0, rasi: 3, longitude: 20 },   // Sun in 4th house
      ];

      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, singlePlanet);
      expect(result.dashaProgression.length).toBe(1);
      expect(result.dashaProgression[0]!.planet).toBe(0);
    });

    it('should have reasonable total duration', () => {
      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, samplePlanetPositions);
      // Total duration depends on planet positions and cycles
      // Should be reasonable (positive and not extremely large)
      expect(result.totalDuration).toBeGreaterThan(0);
      expect(result.totalDuration).toBeLessThanOrEqual(200); // 2 cycles max
    });
  });

  describe('House Traversal', () => {
    it('should traverse houses starting from 4th house', () => {
      // Create positions where planets are in known houses
      const knownPositions = [
        { planet: -1, rasi: 0, longitude: 15 },  // Ascendant in Aries (0)
        { planet: 0, rasi: 3, longitude: 20 },   // Sun in Cancer (4th house - first checked)
        { planet: 1, rasi: 4, longitude: 15 },   // Moon in Leo (5th house)
        { planet: 2, rasi: 5, longitude: 10 },   // Mars in Virgo (6th house)
      ];

      const result = getBuddhiGathiDashaBhukti(testJd, testPlace, knownPositions);

      // First planet should be from 4th house (Cancer = rasi 3)
      expect(result.dashaProgression[0]!.planet).toBe(0); // Sun
    });
  });
});
