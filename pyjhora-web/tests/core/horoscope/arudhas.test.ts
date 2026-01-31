/**
 * Tests for Arudha Pada calculations
 * Test data generated from PyJHora Python implementation
 */

import { describe, expect, it } from 'vitest';
import {
  bhavaArudhasFromPlanetPositions,
  suryaArudhasFromPlanetPositions,
  chandraArudhasFromPlanetPositions,
  grahaArudhasFromPlanetPositions,
  getArudhaLagna,
  getUpaLagna,
  formatBhavaArudhasAsChart,
  formatGrahaArudhasAsChart,
  type ArudhaPlanetPosition,
} from '../../../src/core/horoscope/arudhas';

/**
 * Test case from PyJHora arudhas.py main block:
 * dob = (1996, 12, 7); tob = (10, 34, 0); place = Chennai (13.0878, 80.2785, +5.5)
 *
 * For D-1 chart with arudha_base = 1 (Sun):
 * ba = [0, 4, 7, 7, 6, 10, 6, 4, 8, 8, 1, 5]
 * ba_chart = ['Su1', 'Su11', '', '', 'Su2/Su8', 'Su12', 'Su5/Su7', 'Su3/Su4', 'Su9/Su10', '', 'Su6', '']
 *
 * Graha Arudhas:
 * ga = [8, 4, 0, 8, 7, 0, 10, 8, 11, 1]
 * ga_chart = ['2/4', '9', '', '', '1', '', '', '5', 'L/3/7', '', '6', '8']
 */

// Sample planet positions for testing (Chennai, 1996-12-07, 10:34:00)
// These positions should match the PyJHora test case
// Position format: Lagna (index 0), Sun (1), Moon (2), Mars (3), Mercury (4),
// Jupiter (5), Venus (6), Saturn (7), Rahu (8), Ketu (9)
const samplePlanetPositions: ArudhaPlanetPosition[] = [
  { planet: -1, rasi: 8, longitude: 258.5 },  // Lagna in Sagittarius (8)
  { planet: 0, rasi: 7, longitude: 231.2 },   // Sun in Scorpio (7)
  { planet: 1, rasi: 0, longitude: 15.3 },    // Moon in Aries (0)
  { planet: 2, rasi: 5, longitude: 168.7 },   // Mars in Virgo (5)
  { planet: 3, rasi: 7, longitude: 217.4 },   // Mercury in Scorpio (7)
  { planet: 4, rasi: 8, longitude: 265.1 },   // Jupiter in Sagittarius (8)
  { planet: 5, rasi: 7, longitude: 225.8 },   // Venus in Scorpio (7)
  { planet: 6, rasi: 11, longitude: 357.2 },  // Saturn in Pisces (11)
  { planet: 7, rasi: 5, longitude: 175.3 },   // Rahu in Virgo (5)
  { planet: 8, rasi: 11, longitude: 355.3 },  // Ketu in Pisces (11)
];

describe('Arudha Pada Calculations', () => {
  describe('bhavaArudhasFromPlanetPositions', () => {
    it('should calculate Bhava Arudhas from Lagna (A1-A12)', () => {
      const bhavaArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 0);

      // Should return 12 values
      expect(bhavaArudhas).toHaveLength(12);

      // All values should be valid rasi indices (0-11)
      bhavaArudhas.forEach((rasi) => {
        expect(rasi).toBeGreaterThanOrEqual(0);
        expect(rasi).toBeLessThanOrEqual(11);
      });
    });

    it('should handle different arudha bases', () => {
      // Sun-based (base = 1)
      const suryaArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 1);
      expect(suryaArudhas).toHaveLength(12);

      // Moon-based (base = 2)
      const chandraArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 2);
      expect(chandraArudhas).toHaveLength(12);

      // Results should be different for different bases
      expect(suryaArudhas).not.toEqual(chandraArudhas);
    });
  });

  describe('suryaArudhasFromPlanetPositions', () => {
    it('should calculate Surya Arudhas (S1-S12)', () => {
      const suryaArudhas = suryaArudhasFromPlanetPositions(samplePlanetPositions);

      expect(suryaArudhas).toHaveLength(12);
      suryaArudhas.forEach((rasi) => {
        expect(rasi).toBeGreaterThanOrEqual(0);
        expect(rasi).toBeLessThanOrEqual(11);
      });
    });

    it('should be equivalent to bhavaArudhasFromPlanetPositions with base=1', () => {
      const suryaArudhas = suryaArudhasFromPlanetPositions(samplePlanetPositions);
      const bhavaArudhasFromSun = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 1);

      expect(suryaArudhas).toEqual(bhavaArudhasFromSun);
    });
  });

  describe('chandraArudhasFromPlanetPositions', () => {
    it('should calculate Chandra Arudhas (M1-M12)', () => {
      const chandraArudhas = chandraArudhasFromPlanetPositions(samplePlanetPositions);

      expect(chandraArudhas).toHaveLength(12);
      chandraArudhas.forEach((rasi) => {
        expect(rasi).toBeGreaterThanOrEqual(0);
        expect(rasi).toBeLessThanOrEqual(11);
      });
    });

    it('should be equivalent to bhavaArudhasFromPlanetPositions with base=2', () => {
      const chandraArudhas = chandraArudhasFromPlanetPositions(samplePlanetPositions);
      const bhavaArudhasFromMoon = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 2);

      expect(chandraArudhas).toEqual(bhavaArudhasFromMoon);
    });
  });

  describe('grahaArudhasFromPlanetPositions', () => {
    it('should calculate Graha Arudhas for all planets', () => {
      const grahaArudhas = grahaArudhasFromPlanetPositions(samplePlanetPositions);

      // Should return 10 values: Lagna + 9 planets (Sun to Ketu)
      expect(grahaArudhas).toHaveLength(10);

      // All values should be valid rasi indices (0-11)
      grahaArudhas.forEach((rasi) => {
        expect(rasi).toBeGreaterThanOrEqual(0);
        expect(rasi).toBeLessThanOrEqual(11);
      });
    });

    it('should have Lagna Pada as first element', () => {
      const grahaArudhas = grahaArudhasFromPlanetPositions(samplePlanetPositions);

      // First element should be Lagna's rasi
      expect(grahaArudhas[0]).toBe(samplePlanetPositions[0].rasi);
    });
  });

  describe('getArudhaLagna', () => {
    it('should return the Arudha Lagna (A1)', () => {
      const arudhaLagna = getArudhaLagna(samplePlanetPositions);
      const bhavaArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 0);

      expect(arudhaLagna).toBe(bhavaArudhas[0]);
    });
  });

  describe('getUpaLagna', () => {
    it('should return the Upa Lagna (A12)', () => {
      const upaLagna = getUpaLagna(samplePlanetPositions);
      const bhavaArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 0);

      expect(upaLagna).toBe(bhavaArudhas[11]);
    });
  });

  describe('formatBhavaArudhasAsChart', () => {
    it('should format Bhava Arudhas as a chart array', () => {
      const bhavaArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 0);
      const chart = formatBhavaArudhasAsChart(bhavaArudhas);

      expect(chart).toHaveLength(12);

      // Each element should be a string
      chart.forEach((cell) => {
        expect(typeof cell).toBe('string');
      });

      // Should contain all 12 Arudha labels somewhere in the chart
      const allLabels = chart.join('/');
      for (let i = 1; i <= 12; i++) {
        expect(allLabels).toContain(`A${i}`);
      }
    });

    it('should use custom prefix', () => {
      const bhavaArudhas = bhavaArudhasFromPlanetPositions(samplePlanetPositions, 1);
      const chart = formatBhavaArudhasAsChart(bhavaArudhas, 'Su');

      const allLabels = chart.join('/');
      expect(allLabels).toContain('Su1');
      expect(allLabels).toContain('Su12');
    });
  });

  describe('formatGrahaArudhasAsChart', () => {
    it('should format Graha Arudhas as a chart array', () => {
      const grahaArudhas = grahaArudhasFromPlanetPositions(samplePlanetPositions);
      const chart = formatGrahaArudhasAsChart(grahaArudhas);

      expect(chart).toHaveLength(12);

      // Should contain 'L' for Lagna somewhere
      const allLabels = chart.join('/');
      expect(allLabels).toContain('L');
    });
  });
});

describe('Arudha calculation edge cases', () => {
  it('should handle when lord is in same house', () => {
    // Create a test case where a planet is in its own sign
    const positions: ArudhaPlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 5.0 },   // Lagna in Aries
      { planet: 0, rasi: 4, longitude: 125.0 },  // Sun in Leo (own sign)
      { planet: 1, rasi: 3, longitude: 95.0 },   // Moon in Cancer (own sign)
      { planet: 2, rasi: 0, longitude: 10.0 },   // Mars in Aries (own sign)
      { planet: 3, rasi: 2, longitude: 70.0 },   // Mercury in Gemini
      { planet: 4, rasi: 8, longitude: 260.0 },  // Jupiter in Sagittarius
      { planet: 5, rasi: 1, longitude: 40.0 },   // Venus in Taurus
      { planet: 6, rasi: 9, longitude: 280.0 },  // Saturn in Capricorn
      { planet: 7, rasi: 10, longitude: 310.0 }, // Rahu in Aquarius
      { planet: 8, rasi: 4, longitude: 130.0 },  // Ketu in Leo
    ];

    const bhavaArudhas = bhavaArudhasFromPlanetPositions(positions, 0);

    // Should still return valid results
    expect(bhavaArudhas).toHaveLength(12);
    bhavaArudhas.forEach((rasi) => {
      expect(rasi).toBeGreaterThanOrEqual(0);
      expect(rasi).toBeLessThanOrEqual(11);
    });
  });

  it('should handle positions with only required planets', () => {
    // Minimal positions: Lagna + Sun through Ketu
    const minimalPositions: ArudhaPlanetPosition[] = [
      { planet: -1, rasi: 6, longitude: 195.0 }, // Lagna in Libra
      { planet: 0, rasi: 3, longitude: 100.0 },  // Sun
      { planet: 1, rasi: 7, longitude: 220.0 },  // Moon
      { planet: 2, rasi: 1, longitude: 45.0 },   // Mars
      { planet: 3, rasi: 4, longitude: 135.0 },  // Mercury
      { planet: 4, rasi: 2, longitude: 75.0 },   // Jupiter
      { planet: 5, rasi: 5, longitude: 165.0 },  // Venus
      { planet: 6, rasi: 10, longitude: 305.0 }, // Saturn
      { planet: 7, rasi: 9, longitude: 285.0 },  // Rahu
      { planet: 8, rasi: 3, longitude: 105.0 },  // Ketu
    ];

    const bhavaArudhas = bhavaArudhasFromPlanetPositions(minimalPositions, 0);
    const grahaArudhas = grahaArudhasFromPlanetPositions(minimalPositions);

    expect(bhavaArudhas).toHaveLength(12);
    expect(grahaArudhas).toHaveLength(10);
  });
});
