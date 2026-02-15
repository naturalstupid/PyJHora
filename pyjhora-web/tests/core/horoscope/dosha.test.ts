/**
 * Tests for Dosha (Affliction) Calculations
 * Ported from PyJHora dosha.py
 *
 * Python-validated expected values for Chennai 1996-12-07 10:34
 * Planet positions (D-1):
 *   [['L', (9, 22.45)], [0, (7, 21.57)], [1, (6, 6.96)], [2, (4, 25.54)],
 *    [3, (8, 9.94)], [4, (8, 25.83)], [5, (6, 23.72)], [6, (11, 6.81)],
 *    [7, (5, 10.55)], [8, (11, 10.55)]]
 * house_to_planet: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
 */

import { describe, expect, it } from 'vitest';
import type { PlanetPosition } from '../../../src/core/horoscope/charts';
import type { HouseChart } from '../../../src/core/types';
import {
  kalaSarpa,
  manglik,
  pitruDosha,
  guruChandalaDosha,
  kalathra,
  gandaMoola,
  ghata,
  shrapit,
} from '../../../src/core/horoscope/dosha';
import {
  SUN,
  MOON,
  MARS,
  MERCURY,
  JUPITER,
  VENUS,
  SATURN,
  RAHU,
  KETU,
} from '../../../src/core/constants';

// ============================================================================
// TEST DATA: Chennai 1996-12-07 10:34
// ============================================================================

/**
 * Planet positions for the test chart.
 * In Python format: [['L', (9, 22.45)], [0, (7, 21.57)], [1, (6, 6.96)], ...]
 * TS PlanetPosition: { planet, rasi, longitude }
 * planet -1 = Lagna, 0 = Sun, ..., 8 = Ketu
 */
const testPositions: PlanetPosition[] = [
  { planet: -1, rasi: 9, longitude: 22.45 }, // Lagna in Capricorn
  { planet: SUN, rasi: 7, longitude: 21.57 }, // Sun in Scorpio
  { planet: MOON, rasi: 6, longitude: 6.96 }, // Moon in Libra
  { planet: MARS, rasi: 4, longitude: 25.54 }, // Mars in Leo
  { planet: MERCURY, rasi: 8, longitude: 9.94 }, // Mercury in Sagittarius
  { planet: JUPITER, rasi: 8, longitude: 25.83 }, // Jupiter in Sagittarius
  { planet: VENUS, rasi: 6, longitude: 23.72 }, // Venus in Libra
  { planet: SATURN, rasi: 11, longitude: 6.81 }, // Saturn in Pisces
  { planet: RAHU, rasi: 5, longitude: 10.55 }, // Rahu in Virgo
  { planet: KETU, rasi: 11, longitude: 10.55 }, // Ketu in Pisces
];

/**
 * House-to-planet chart for the test horoscope.
 * Index 0 = Aries (house containing no planets for this chart since Lagna is Capricorn)
 * The chart string representation from Python:
 * ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
 */
const testChart: HouseChart = [
  '', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8',
];

// ============================================================================
// KALA SARPA DOSHA
// ============================================================================

describe('Kala Sarpa Dosha', () => {
  it('should return false for the test chart (planets not all between nodes)', () => {
    expect(kalaSarpa(testChart)).toBe(false);
  });

  it('should return true when all planets are between Rahu and Ketu', () => {
    // Construct chart: Rahu in house 0, all planets in houses 0-6, Ketu in house 6
    // Planets 0-6 in houses 1-6 (between Rahu at 0 and Ketu at 6)
    const chart: HouseChart = [
      '7',    // house 0: Rahu
      '0',    // house 1: Sun
      '1',    // house 2: Moon
      '2',    // house 3: Mars
      '3',    // house 4: Mercury
      '4',    // house 5: Jupiter
      '5/6',  // house 6: Venus, Saturn + Ketu
      '8',    // house 6: Ketu
      '', '', '', '',
    ];
    expect(kalaSarpa(chart)).toBe(true);
  });

  it('should return true when all planets are between Ketu and Rahu', () => {
    // Ketu at house 0, all planets in houses 0-6, Rahu at house 6
    const chart: HouseChart = [
      '8',    // house 0: Ketu
      '0',    // house 1: Sun
      '1',    // house 2: Moon
      '2',    // house 3: Mars
      '3',    // house 4: Mercury
      '4',    // house 5: Jupiter
      '5/6/7', // house 6: Venus, Saturn, Rahu
      '',
      '', '', '', '',
    ];
    expect(kalaSarpa(chart)).toBe(true);
  });

  it('should return false when a planet is outside the node range', () => {
    // Rahu at house 0, planets in houses 1-5, but Saturn at house 8 (outside)
    const chart: HouseChart = [
      '7',    // house 0: Rahu
      '0',    // house 1: Sun
      '1',    // house 2: Moon
      '2',    // house 3: Mars
      '3',    // house 4: Mercury
      '4',    // house 5: Jupiter
      '8',    // house 6: Ketu
      '',
      '6',    // house 8: Saturn (outside 0-6 range)
      '', '',
      '5',    // house 11: Venus
    ];
    expect(kalaSarpa(chart)).toBe(false);
  });

  // -----------------------------------------------------------------------
  // Python pvr_tests.py sarpa_dosha_tests() - all 7 chart configurations
  // -----------------------------------------------------------------------

  it('Python chart 1: Rahu in house 1, all planets between Rahu and Ketu -> true', () => {
    // h_to_p = ['L','7','0/1','5/6','2','3','4','8','','','','']
    const chart: HouseChart = ['L', '7', '0/1', '5/6', '2', '3', '4', '8', '', '', '', ''];
    expect(kalaSarpa(chart)).toBe(true);
  });

  it('Python chart 2: Ketu in house 1, Rahu in house 7 -> true', () => {
    // h_to_p = ['L','8','0/1','5/6','2','3','4','7','','','','']
    const chart: HouseChart = ['L', '8', '0/1', '5/6', '2', '3', '4', '7', '', '', '', ''];
    expect(kalaSarpa(chart)).toBe(true);
  });

  it('Python chart 3: Rahu conjunct Sun in house 1, Ketu conjunct Saturn in house 7 -> true', () => {
    // h_to_p = ['L','7/0','1','5','2','3','4','6/8','','','','']
    const chart: HouseChart = ['L', '7/0', '1', '5', '2', '3', '4', '6/8', '', '', '', ''];
    expect(kalaSarpa(chart)).toBe(true);
  });

  it('Python chart 4: Ketu conjunct Sun in house 1, Rahu conjunct Saturn in house 7 -> true', () => {
    // h_to_p = ['L','8/0','1','5','2','3','4','6/7','','','','']
    const chart: HouseChart = ['L', '8/0', '1', '5', '2', '3', '4', '6/7', '', '', '', ''];
    expect(kalaSarpa(chart)).toBe(true);
  });

  it('Python chart 5: Venus outside the node range -> false', () => {
    // h_to_p = ['L','7','0/1','5','2','3','4','8','6','','','']
    const chart: HouseChart = ['L', '7', '0/1', '5', '2', '3', '4', '8', '6', '', '', ''];
    expect(kalaSarpa(chart)).toBe(false);
  });

  it('Python chart 6: Sun conjunct Lagna at Rahu side -> false', () => {
    // h_to_p = ['L/0','7','1','5/6','2','3','4','8','','','','']
    const chart: HouseChart = ['L/0', '7', '1', '5/6', '2', '3', '4', '8', '', '', '', ''];
    expect(kalaSarpa(chart)).toBe(false);
  });

  it('Python chart 7: planets between Rahu(house 8) and Ketu(house 2) -> true', () => {
    // h_to_p = ['L/6','5','8','','','','','','7','0/1','2/3','4']
    const chart: HouseChart = ['L/6', '5', '8', '', '', '', '', '', '7', '0/1', '2/3', '4'];
    expect(kalaSarpa(chart)).toBe(true);
  });
});

// ============================================================================
// MANGLIK DOSHA
// ============================================================================

describe('Manglik Dosha', () => {
  it('should detect manglik dosha for the test chart (default from Lagna)', () => {
    const [isManglik] = manglik(testPositions);
    // Mars in Leo (rasi 4), Lagna in Capricorn (rasi 9)
    // Relative house: (4 + 12 - 9) % 12 + 1 = 7 + 1 = 8
    // House 8 is in the manglik list [2, 4, 7, 8, 12]
    expect(isManglik).toBe(true);
  });

  it('should detect exceptions for the test chart', () => {
    const [isManglik, hasExceptions, exceptionIndices] = manglik(testPositions);
    expect(isManglik).toBe(true);
    expect(hasExceptions).toBe(true);
    // Exception 1: Mars in Leo (rasi 4) -> matches LEO
    expect(exceptionIndices).toContain(1);
    // Exception 12: Mars in Leo -> HOUSE_STRENGTHS_OF_PLANETS[2][4] = 3 (Friend) >= 3
    expect(exceptionIndices).toContain(12);
  });

  it('should return false when Mars is not in a manglik house', () => {
    // Place Mars in rasi 0 (Aries), Lagna in rasi 9 (Capricorn)
    // Relative house: (0 + 12 - 9) % 12 + 1 = 3 + 1 = 4
    // House 4 IS in the manglik list, so let me use a position that is NOT
    // Mars in rasi 10 (Aquarius), Lagna rasi 9 (Capricorn)
    // Relative house: (10 + 12 - 9) % 12 + 1 = 13 % 12 + 1 = 1 + 1 = 2
    // House 2 is in manglik list. Let me try rasi 0:
    // (0 + 12 - 9) % 12 + 1 = 3 + 1 = 4 -> in list
    // Let me try Mars in same sign as Lagna (rasi 9):
    // (9 + 12 - 9) % 12 + 1 = 0 + 1 = 1 -> NOT in [2,4,7,8,12]
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 9, longitude: 22.45 },
      { planet: MARS, rasi: 9, longitude: 15 },
    ];
    const [isManglik] = manglik(positions);
    expect(isManglik).toBe(false);
  });

  it('should detect manglik from Moon reference', () => {
    // Moon in rasi 6, Mars in rasi 4
    // Relative house: (4 + 12 - 6) % 12 + 1 = 10 + 1 = 11
    // House 11 is NOT in [2, 4, 7, 8, 12] -> not manglik from Moon
    const [isManglik] = manglik(testPositions, MOON);
    expect(isManglik).toBe(false);
  });

  it('should detect exception 7 when Mars conjuncts Jupiter', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 10 },
      { planet: MARS, rasi: 6, longitude: 15 },     // Mars in Libra (house 7 from Aries)
      { planet: JUPITER, rasi: 6, longitude: 20 },   // Jupiter conjunct Mars
      { planet: SATURN, rasi: 3, longitude: 10 },
    ];
    const [isManglik, hasExceptions, indices] = manglik(positions);
    expect(isManglik).toBe(true);
    expect(hasExceptions).toBe(true);
    expect(indices).toContain(7);
  });

  // -----------------------------------------------------------------------
  // Python pvr_tests.py manglik_dosha_tests() - additional chart configurations
  // -----------------------------------------------------------------------

  it('Python manglik 1: Mars in Lagna (house 1) with default -> not manglik (house 1 not in list)', () => {
    // Python: pp = [['L',(0,0)],[0,(9,0)],[1,(9,0)],[2,(0,0)],[3,(10,0)],[4,(11,0)],[5,(1,0)],[6,(10,0)],[7,(8,0)],[8,(2,0)]]
    // Mars in Aries (rasi 0), Lagna in Aries (rasi 0) -> house 1 from Lagna
    // In Python with include_lagna_house=False (default): not manglik
    // TS does not include house 1 in manglik list (same as Python default)
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 0 },
      { planet: SUN, rasi: 9, longitude: 0 },
      { planet: MOON, rasi: 9, longitude: 0 },
      { planet: MARS, rasi: 0, longitude: 0 },
      { planet: MERCURY, rasi: 10, longitude: 0 },
      { planet: JUPITER, rasi: 11, longitude: 0 },
      { planet: VENUS, rasi: 1, longitude: 0 },
      { planet: SATURN, rasi: 10, longitude: 0 },
      { planet: RAHU, rasi: 8, longitude: 0 },
      { planet: KETU, rasi: 2, longitude: 0 },
    ];
    const [isManglik] = manglik(positions);
    expect(isManglik).toBe(false);
  });

  it('Python manglik 2: Mars in Taurus (house 2 from Lagna)', () => {
    // Mars in rasi 1 (Taurus), Lagna in rasi 0 (Aries)
    // Relative house: (1+12-0)%12+1 = 2 -> in manglik list [2,4,7,8,12]
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 0 },
      { planet: SUN, rasi: 9, longitude: 0 },
      { planet: MOON, rasi: 9, longitude: 0 },
      { planet: MARS, rasi: 1, longitude: 0 },
      { planet: MERCURY, rasi: 10, longitude: 0 },
      { planet: JUPITER, rasi: 11, longitude: 0 },
      { planet: VENUS, rasi: 1, longitude: 0 },
      { planet: SATURN, rasi: 10, longitude: 0 },
      { planet: RAHU, rasi: 8, longitude: 0 },
      { planet: KETU, rasi: 2, longitude: 0 },
    ];
    const [isManglik] = manglik(positions);
    expect(isManglik).toBe(true);
  });

  it('Python manglik 3: Mars in Cancer (house 4 from Lagna)', () => {
    // Mars in rasi 3 (Cancer), Lagna in rasi 0 (Aries)
    // Relative house: (3+12-0)%12+1 = 4 -> in manglik list
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 0 },
      { planet: SUN, rasi: 9, longitude: 0 },
      { planet: MOON, rasi: 9, longitude: 0 },
      { planet: MARS, rasi: 3, longitude: 0 },
      { planet: MERCURY, rasi: 10, longitude: 0 },
      { planet: JUPITER, rasi: 11, longitude: 0 },
      { planet: VENUS, rasi: 1, longitude: 0 },
      { planet: SATURN, rasi: 10, longitude: 0 },
      { planet: RAHU, rasi: 8, longitude: 0 },
      { planet: KETU, rasi: 2, longitude: 0 },
    ];
    const [isManglik] = manglik(positions);
    expect(isManglik).toBe(true);
  });

  it('Python manglik 4: Mars in Libra (house 7 from Lagna)', () => {
    // Mars in rasi 6 (Libra), Lagna in rasi 0 (Aries)
    // Relative house: (6+12-0)%12+1 = 7 -> in manglik list
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 0 },
      { planet: SUN, rasi: 9, longitude: 0 },
      { planet: MOON, rasi: 9, longitude: 0 },
      { planet: MARS, rasi: 6, longitude: 0 },
      { planet: MERCURY, rasi: 10, longitude: 0 },
      { planet: JUPITER, rasi: 11, longitude: 0 },
      { planet: VENUS, rasi: 1, longitude: 0 },
      { planet: SATURN, rasi: 10, longitude: 0 },
      { planet: RAHU, rasi: 8, longitude: 0 },
      { planet: KETU, rasi: 2, longitude: 0 },
    ];
    const [isManglik] = manglik(positions);
    expect(isManglik).toBe(true);
  });
});

// ============================================================================
// PITRU DOSHA
// ============================================================================

describe('Pitru Dosha', () => {
  it('should detect pitru dosha for the test chart', () => {
    const [hasPitru, conditions] = pitruDosha(testPositions);
    expect(hasPitru).toBe(true);
    // Expected conditions: [1, 3] based on Python-validated results
    expect(conditions).toContain(1);
    expect(conditions).toContain(3);
  });

  it('should return false when no conditions are met', () => {
    // Create positions where no pitru dosha conditions are satisfied
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 }, // Lagna in Aries
      { planet: SUN, rasi: 3, longitude: 10 },     // Sun in Cancer (4th, not 9th)
      { planet: MOON, rasi: 4, longitude: 10 },    // Moon in Leo (5th, not 9th)
      { planet: MARS, rasi: 1, longitude: 10 },    // Mars in Taurus
      { planet: MERCURY, rasi: 2, longitude: 10 }, // Mercury in Gemini
      { planet: JUPITER, rasi: 3, longitude: 20 }, // Jupiter in Cancer
      { planet: VENUS, rasi: 0, longitude: 10 },   // Venus in Aries
      { planet: SATURN, rasi: 5, longitude: 10 },  // Saturn in Virgo (6th)
      { planet: RAHU, rasi: 6, longitude: 10 },    // Rahu in Libra (7th)
      { planet: KETU, rasi: 0, longitude: 10 },    // Ketu in Aries (1st)
    ];
    const [hasPitru] = pitruDosha(positions);
    // Condition 3: Mars(1) or Saturn(5) same house as Sun(3)/Moon(4)/Rahu(6)/Ketu(0)? No.
    // Condition 5: Sun(3) or Moon(4) conjunct Rahu(6) or Ketu(0)? No.
    // Condition 1: Sun(3)/Moon(4)/Rahu(6) in 9th (rasi 8)? No.
    // Condition 2: Ketu(0) in 4th (rasi 3)? No.
    // Condition 4: 2+ of Mercury(2)/Venus(0)/Rahu(6) in same house among houses 2,5,9,12 from Lagna? No.
    expect(hasPitru).toBe(false);
  });

  it('should detect condition 1 (Sun/Moon/Rahu in 9th house)', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 }, // Lagna in Aries
      { planet: SUN, rasi: 8, longitude: 10 },     // Sun in 9th house (Sagittarius)
      { planet: MOON, rasi: 3, longitude: 10 },
      { planet: MARS, rasi: 1, longitude: 10 },
      { planet: MERCURY, rasi: 2, longitude: 10 },
      { planet: JUPITER, rasi: 5, longitude: 20 },
      { planet: VENUS, rasi: 4, longitude: 10 },
      { planet: SATURN, rasi: 10, longitude: 10 },
      { planet: RAHU, rasi: 6, longitude: 10 },
      { planet: KETU, rasi: 0, longitude: 10 },
    ];
    const [hasPitru, conditions] = pitruDosha(positions);
    expect(hasPitru).toBe(true);
    expect(conditions).toContain(1);
  });
});

// ============================================================================
// GURU CHANDALA DOSHA
// ============================================================================

describe('Guru Chandala Dosha', () => {
  it('should return false for the test chart (Jupiter and Rahu in different houses)', () => {
    const [hasDosha, jupiterStronger] = guruChandalaDosha(testPositions);
    // Jupiter in rasi 8 (Sagittarius), Rahu in rasi 5 (Virgo) -> not conjunct
    expect(hasDosha).toBe(false);
    expect(jupiterStronger).toBe(false);
  });

  it('should detect dosha when Jupiter conjuncts Rahu', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 },
      { planet: JUPITER, rasi: 5, longitude: 20 },
      { planet: RAHU, rasi: 5, longitude: 10 },
      { planet: KETU, rasi: 11, longitude: 10 },
    ];
    const [hasDosha, jupiterStronger] = guruChandalaDosha(positions);
    expect(hasDosha).toBe(true);
    // Jupiter longitude (20) > Rahu longitude (10)
    expect(jupiterStronger).toBe(true);
  });

  it('should detect dosha when Jupiter conjuncts Ketu', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 },
      { planet: JUPITER, rasi: 11, longitude: 5 },
      { planet: RAHU, rasi: 5, longitude: 10 },
      { planet: KETU, rasi: 11, longitude: 15 },
    ];
    const [hasDosha, jupiterStronger] = guruChandalaDosha(positions);
    expect(hasDosha).toBe(true);
    // Jupiter longitude (5) < Ketu longitude (15)
    expect(jupiterStronger).toBe(false);
  });
});

// ============================================================================
// KALATHRA DOSHA
// ============================================================================

describe('Kalathra Dosha', () => {
  it('should return false for the test chart', () => {
    const result = kalathra(testPositions);
    expect(result).toBe(false);
  });

  it('should return true when all malefics are in kalathra houses from 7th', () => {
    // Lagna in Aries (0). 7th house from Lagna = Libra (6).
    // Houses 1,2,4,7,8,12 from Libra (6):
    //   House 1 = rasi 6 (Libra)
    //   House 2 = rasi 7 (Scorpio)
    //   House 4 = rasi 9 (Capricorn)
    //   House 7 = rasi 0 (Aries)
    //   House 8 = rasi 1 (Taurus)
    //   House 12 = rasi 5 (Virgo)
    // All natural malefics (Sun=0, Mars=2, Saturn=6, Rahu=7, Ketu=8) must be in those signs
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 }, // Lagna Aries
      { planet: SUN, rasi: 6, longitude: 10 },    // Sun in Libra (house 1 from 7th)
      { planet: MOON, rasi: 3, longitude: 10 },
      { planet: MARS, rasi: 7, longitude: 10 },   // Mars in Scorpio (house 2 from 7th)
      { planet: MERCURY, rasi: 2, longitude: 10 },
      { planet: JUPITER, rasi: 4, longitude: 10 },
      { planet: VENUS, rasi: 3, longitude: 10 },
      { planet: SATURN, rasi: 9, longitude: 10 }, // Saturn in Capricorn (house 4 from 7th)
      { planet: RAHU, rasi: 0, longitude: 10 },   // Rahu in Aries (house 7 from 7th)
      { planet: KETU, rasi: 5, longitude: 10 },   // Ketu in Virgo (house 12 from 7th)
    ];
    const result = kalathra(positions);
    expect(result).toBe(true);
  });
});

// ============================================================================
// GANDA MOOLA DOSHA
// ============================================================================

describe('Ganda Moola Dosha', () => {
  it('should return false for nakshatra 15 (Swati)', () => {
    expect(gandaMoola(15)).toBe(false);
  });

  it('should return true for all ganda moola nakshatras', () => {
    const gandaMoolaStars = [1, 9, 10, 18, 19, 27];
    for (const star of gandaMoolaStars) {
      expect(gandaMoola(star)).toBe(true);
    }
  });

  it('should return false for non-ganda moola nakshatras', () => {
    const nonGandaMoola = [2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26];
    for (const star of nonGandaMoola) {
      expect(gandaMoola(star)).toBe(false);
    }
  });
});

// ============================================================================
// GHATA DOSHA
// ============================================================================

describe('Ghata Dosha', () => {
  it('should return false for the test chart (Mars and Saturn in different houses)', () => {
    // Mars in rasi 4 (Leo), Saturn in rasi 11 (Pisces)
    expect(ghata(testPositions)).toBe(false);
  });

  it('should return true when Mars and Saturn are in the same house', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 },
      { planet: MARS, rasi: 5, longitude: 10 },
      { planet: SATURN, rasi: 5, longitude: 20 },
    ];
    expect(ghata(positions)).toBe(true);
  });

  it('should return false when Mars and Saturn are in different houses', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 },
      { planet: MARS, rasi: 3, longitude: 10 },
      { planet: SATURN, rasi: 9, longitude: 20 },
    ];
    expect(ghata(positions)).toBe(false);
  });
});

// ============================================================================
// SHRAPIT DOSHA
// ============================================================================

describe('Shrapit Dosha', () => {
  it('should return false for the test chart (Rahu and Saturn in different houses)', () => {
    // Rahu in rasi 5 (Virgo), Saturn in rasi 11 (Pisces)
    expect(shrapit(testPositions)).toBe(false);
  });

  it('should return true when Rahu and Saturn are in the same house', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 },
      { planet: RAHU, rasi: 7, longitude: 10 },
      { planet: SATURN, rasi: 7, longitude: 20 },
    ];
    expect(shrapit(positions)).toBe(true);
  });

  it('should return false when Rahu and Saturn are in different houses', () => {
    const positions: PlanetPosition[] = [
      { planet: -1, rasi: 0, longitude: 15 },
      { planet: RAHU, rasi: 3, longitude: 10 },
      { planet: SATURN, rasi: 8, longitude: 20 },
    ];
    expect(shrapit(positions)).toBe(false);
  });
});
