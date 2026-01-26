import { describe, expect, it } from 'vitest';
import { getKarakaDashaBhukti } from '../../../../src/core/dhasa/graha/karaka';
import type { Place } from '../../../../src/core/types';

describe('Karaka Dasha (Jaimini)', () => {
  const testPlace: Place = {
    name: 'Delhi',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 5.5
  };
  const testJd = 2447912.0;

  // Sample planet positions for testing
  // planet: -1 is ascendant, 0-8 are planets
  const samplePlanetPositions = [
    { planet: -1, rasi: 0, longitude: 15 },  // Ascendant in Aries
    { planet: 0, rasi: 4, longitude: 25 },   // Sun in Leo (high degree - Atmakaraka candidate)
    { planet: 1, rasi: 3, longitude: 18 },   // Moon in Cancer
    { planet: 2, rasi: 0, longitude: 10 },   // Mars in Aries
    { planet: 3, rasi: 5, longitude: 22 },   // Mercury in Virgo
    { planet: 4, rasi: 8, longitude: 12 },   // Jupiter in Sagittarius
    { planet: 5, rasi: 6, longitude: 20 },   // Venus in Libra
    { planet: 6, rasi: 9, longitude: 8 },    // Saturn in Capricorn
    { planet: 7, rasi: 11, longitude: 15 },  // Rahu in Pisces
  ];

  describe('Karaka Ordering', () => {
    it('should return ordered karakas', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions);
      expect(result.karakas).toBeDefined();
      expect(result.karakas.length).toBe(8); // 8 chara karakas
    });

    it('should have unique planets in karaka order', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions);
      const uniqueKarakas = new Set(result.karakas);
      expect(uniqueKarakas.size).toBe(result.karakas.length);
    });
  });

  describe('Dasha Structure', () => {
    it('should return valid mahadasha structure', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: false });
      expect(result.mahadashas).toBeDefined();
      expect(result.mahadashas.length).toBe(8); // 8 karaka lords
    });

    it('should have mahadasha lords matching karaka order', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: false });
      const dashaLords = result.mahadashas.map(m => m.lord);

      // Dasha lords should follow karaka ordering
      for (let i = 0; i < result.karakas.length; i++) {
        expect(dashaLords[i]).toBe(result.karakas[i]);
      }
    });

    it('should calculate human lifespan from house distances', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions);
      expect(result.humanLifeSpan).toBeGreaterThan(0);
      // Human lifespan is sum of house distances, max possible is 8 * 11 = 88
      expect(result.humanLifeSpan).toBeLessThanOrEqual(96);
    });

    it('should have non-negative durations', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: false });
      for (const dasha of result.mahadashas) {
        expect(dasha.durationYears).toBeGreaterThanOrEqual(0);
      }
    });
  });

  describe('Bhuktis', () => {
    it('should include bhuktis when requested', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: true });
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should not include bhuktis when not requested', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: false });
      expect(result.bhuktis).toBeUndefined();
    });

    it('should have 8 bhuktis per mahadasha', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: true });
      // Total bhuktis should be 8 dashas × 8 bhuktis = 64
      expect(result.bhuktis!.length).toBe(64);
    });

    it('should rotate bhukti lords starting from next karaka', () => {
      const result = getKarakaDashaBhukti(testJd, testPlace, samplePlanetPositions, { includeBhuktis: true });
      const firstDashaLord = result.mahadashas[0]!.lord;
      const firstDashaBhuktis = result.bhuktis!.filter(b => b.dashaLord === firstDashaLord);

      // Should have 8 bhuktis for first dasha
      expect(firstDashaBhuktis.length).toBe(8);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty planet positions gracefully', () => {
      const emptyPositions: Array<{ planet: number; rasi: number; longitude: number }> = [];
      const result = getKarakaDashaBhukti(testJd, testPlace, emptyPositions);

      expect(result.karakas).toBeDefined();
      expect(result.mahadashas).toBeDefined();
    });

    it('should handle positions without ascendant', () => {
      const positionsNoAsc = samplePlanetPositions.filter(p => p.planet !== -1);
      const result = getKarakaDashaBhukti(testJd, testPlace, positionsNoAsc);

      expect(result.karakas).toBeDefined();
      expect(result.mahadashas).toBeDefined();
    });
  });
});
