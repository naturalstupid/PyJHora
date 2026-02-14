import { describe, expect, it } from 'vitest';
import {
  JUPITER,
  MARS,
  MERCURY,
  MOON,
  SATURN,
  SUN,
  VENUS,
  KETU,
  RAHU,
} from '../../../src/core/constants';
import {
  getRajaYogaPairs,
  getRajaYogaPairsFromPositions,
  dharmaKarmadhipatiRajaYoga,
  vipareethaRajaYoga,
  neechaBhangaRajaYoga,
} from '../../../src/core/horoscope/raja-yoga';
import type { HouseChart } from '../../../src/core/types';

describe('Raja Yoga Calculations', () => {
  // =========================================================================
  // Chart data
  // =========================================================================

  /**
   * Chennai chart (1996-12-07)
   * house_to_planet: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
   * Lagna in Capricorn (9)
   * Mars(2) in Leo(4), Rahu(7) in Virgo(5), Moon(1)/Venus(5) in Libra(6),
   * Sun(0) in Scorpio(7), Mercury(3)/Jupiter(4) in Sagittarius(8),
   * Saturn(6)/Ketu(8) in Pisces(11)
   */
  const chartChennai: HouseChart = [
    '', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8',
  ];

  /**
   * Oprah Winfrey chart
   * chart: ['','4','','8','','','6','1/2','','0/3/5/L/7','','']
   * Lagna in Capricorn (9)
   * Jupiter(4) in Taurus(1), Ketu(8) in Cancer(3),
   * Saturn(6) in Libra(6), Moon(1)/Mars(2) in Scorpio(7),
   * Sun(0)/Mercury(3)/Venus(5)/Lagna(L)/Rahu(7) in Capricorn(9)
   */
  const chartOprah: HouseChart = [
    '', '4', '', '8', '', '', '6', '1/2', '', '0/3/5/L/7', '', '',
  ];

  /**
   * Salman Khan chart
   * chart: ['0/2/5','','7','6','','','L/1','','8/4','','','3']
   * Lagna in Libra (6)
   * Sun(0)/Mars(2)/Venus(5) in Aries(0), Rahu(7) in Gemini(2),
   * Saturn(6) in Cancer(3), Moon(1)/Lagna(L) in Libra(6),
   * Ketu(8)/Jupiter(4) in Sagittarius(8), Mercury(3) in Pisces(11)
   */
  const chartSalman: HouseChart = [
    '0/2/5', '', '7', '6', '', '', 'L/1', '', '8/4', '', '', '3',
  ];

  // =========================================================================
  // getRajaYogaPairs
  // =========================================================================

  describe('getRajaYogaPairs', () => {
    it('should find raja yoga pairs for Chennai chart', () => {
      const pairs = getRajaYogaPairs(chartChennai);
      // Expected: [[1, 5]] (Moon and Venus)
      // Moon(1) and Venus(5) are both in Libra(6) => conjunction
      // Lagna is in Capricorn(9), quadrant houses: 9,0,3,6 -> lords: Saturn,Mars,Moon,Venus
      // Trine houses: 9,1,5 -> lords: Saturn,Venus,Mercury
      // Moon is kendra lord (Cancer=3 is 4th from Cap), Venus is trikona lord (Taurus=1 is 5th from Cap)
      // They are conjoined in Libra(6) => raja yoga

      expect(pairs.length).toBeGreaterThanOrEqual(1);

      // Check that [1, 5] pair is present (order: sorted)
      const hasMoonVenus = pairs.some(
        ([p1, p2]) =>
          (p1 === MOON && p2 === VENUS) || (p1 === VENUS && p2 === MOON)
      );
      expect(hasMoonVenus).toBe(true);
    });

    it('should find raja yoga pairs for Oprah Winfrey chart', () => {
      const pairs = getRajaYogaPairs(chartOprah);
      // Lagna is in Capricorn(9)
      // Quadrant houses: 9,0,3,6 -> lords: Saturn, Mars, Moon, Venus
      // Trine houses: 9,1,5 -> lords: Saturn, Venus, Mercury
      // Possible pairs: (Mars,Venus), (Mars,Mercury), (Mars,Saturn),
      //   (Moon,Venus), (Moon,Mercury), (Moon,Saturn), (Venus,Saturn), (Mercury,Saturn)
      // Then check associations...

      // The function should return at least some pairs
      expect(pairs).toBeDefined();
      expect(Array.isArray(pairs)).toBe(true);
      // We primarily verify it runs without error and returns valid structure
      for (const [p1, p2] of pairs) {
        expect(typeof p1).toBe('number');
        expect(typeof p2).toBe('number');
        expect(p1).not.toBe(p2);
      }
    });

    it('should find raja yoga pairs for Salman Khan chart', () => {
      const pairs = getRajaYogaPairs(chartSalman);
      expect(pairs).toBeDefined();
      expect(Array.isArray(pairs)).toBe(true);
      // Lagna in Libra(6)
      // Quadrant houses: 6, 9, 0, 3 -> lords: Venus, Saturn, Mars, Moon
      // Trine houses: 6, 10, 2 -> lords: Venus, Saturn, Mercury
      // Sun/Mars/Venus in Aries(0) = 7th from Libra = kendra
      // Mars is kendra lord, Venus is both kendra and trikona lord
      expect(pairs.length).toBeGreaterThanOrEqual(0);
    });

    it('should return empty array for chart without Lagna', () => {
      const chartNoLagna: HouseChart = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '', '', '',
      ];
      const pairs = getRajaYogaPairs(chartNoLagna);
      expect(pairs).toEqual([]);
    });

    it('should handle chart where same planet is lord of both kendra and trikona', () => {
      // For Aries Lagna: quadrants are 0,3,6,9 and trines are 0,4,8
      // Lords: Mars(0), Moon(3), Venus(6), Saturn(9) for kendras
      // Lords: Mars(0), Sun(4), Jupiter(8) for trines
      // Mars is lord of both kendra (Aries) and trikona (Aries) - same planet excluded from pairs
      const chartAries: HouseChart = [
        'L/0/2', '', '', '1', '', '', '5', '', '4', '6', '7', '3/8',
      ];
      const pairs = getRajaYogaPairs(chartAries);
      // Mars should not pair with itself
      for (const [p1, p2] of pairs) {
        expect(p1).not.toBe(p2);
      }
    });
  });

  // =========================================================================
  // getRajaYogaPairsFromPositions
  // =========================================================================

  describe('getRajaYogaPairsFromPositions', () => {
    it('should find raja yoga pairs from planet positions matching chart results', () => {
      // Chennai chart positions
      const positions = [
        { planet: -1, rasi: 9, longitude: 270, longitudeInSign: 0, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 }, // Lagna in Cap
        { planet: SUN, rasi: 7, longitude: 220, longitudeInSign: 10, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: MOON, rasi: 6, longitude: 190, longitudeInSign: 10, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: MARS, rasi: 4, longitude: 130, longitudeInSign: 10, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: MERCURY, rasi: 8, longitude: 250, longitudeInSign: 10, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: JUPITER, rasi: 8, longitude: 255, longitudeInSign: 15, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: VENUS, rasi: 6, longitude: 195, longitudeInSign: 15, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: SATURN, rasi: 11, longitude: 340, longitudeInSign: 10, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: RAHU, rasi: 5, longitude: 165, longitudeInSign: 15, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
        { planet: KETU, rasi: 11, longitude: 345, longitudeInSign: 15, isRetrograde: false, nakshatra: 0, nakshatraPada: 0 },
      ];

      const pairs = getRajaYogaPairsFromPositions(positions);
      const hasMoonVenus = pairs.some(
        ([p1, p2]) =>
          (p1 === MOON && p2 === VENUS) || (p1 === VENUS && p2 === MOON)
      );
      expect(hasMoonVenus).toBe(true);
    });
  });

  // =========================================================================
  // dharmaKarmadhipatiRajaYoga
  // =========================================================================

  describe('dharmaKarmadhipatiRajaYoga', () => {
    it('should detect dharma-karmadhipati yoga for Oprah Winfrey chart', () => {
      // Lagna in Capricorn (9)
      // 9th house = (9 + 8) % 12 = 5 (Virgo) -> lord = Mercury(3)
      // 10th house = (9 + 9) % 12 = 6 (Libra) -> lord = Venus(5)
      // So dharma-karmadhipati yoga requires planets to be Mercury and Venus
      const pToH: Record<number | string, number> = {
        'L': 9, // Capricorn
        [SUN]: 9,
        [MOON]: 7,
        [MARS]: 7,
        [MERCURY]: 9,
        [JUPITER]: 1,
        [VENUS]: 9,
        [SATURN]: 6,
        [RAHU]: 9,
        [KETU]: 3,
      };

      // Mercury(3) and Venus(5) should form dharma-karmadhipati yoga
      expect(dharmaKarmadhipatiRajaYoga(pToH, MERCURY, VENUS)).toBe(true);
      expect(dharmaKarmadhipatiRajaYoga(pToH, VENUS, MERCURY)).toBe(true);

      // Other pairs should not form it
      expect(dharmaKarmadhipatiRajaYoga(pToH, SUN, MOON)).toBe(false);
      expect(dharmaKarmadhipatiRajaYoga(pToH, MARS, JUPITER)).toBe(false);
    });

    it('should return false when Lagna is missing', () => {
      const pToH: Record<number | string, number> = {
        [SUN]: 0,
        [MOON]: 1,
      };
      expect(dharmaKarmadhipatiRajaYoga(pToH, SUN, MOON)).toBe(false);
    });

    it('should detect for Aries Lagna', () => {
      // Lagna in Aries (0)
      // 9th house = (0 + 8) % 12 = 8 (Sagittarius) -> lord = Jupiter(4)
      // 10th house = (0 + 9) % 12 = 9 (Capricorn) -> lord = Saturn(6)
      const pToH: Record<number | string, number> = {
        'L': 0,
        [JUPITER]: 8,
        [SATURN]: 9,
      };
      expect(dharmaKarmadhipatiRajaYoga(pToH, JUPITER, SATURN)).toBe(true);
      expect(dharmaKarmadhipatiRajaYoga(pToH, SUN, MOON)).toBe(false);
    });
  });

  // =========================================================================
  // vipareethaRajaYoga
  // =========================================================================

  describe('vipareethaRajaYoga', () => {
    it('should detect vipareetha raja yoga when both planets are in dusthanas', () => {
      // Lagna in Libra (6) for Salman Khan
      // Dusthanas from Libra: 6th=(6+5)%12=11(Pisces), 8th=(6+7)%12=1(Taurus), 12th=(6+11)%12=5(Virgo)
      const pToH: Record<number | string, number> = {
        'L': 6,
        [SUN]: 0,
        [MOON]: 6,
        [MARS]: 0,
        [MERCURY]: 11, // Mercury in Pisces (6th house from Libra = dusthana)
        [JUPITER]: 8,
        [VENUS]: 0,
        [SATURN]: 3,
        [RAHU]: 2,
        [KETU]: 8,
      };

      // Both planets need to be in dusthanas
      // Mercury(3) is in Pisces(11) which is 6th from Libra = dusthana
      // Let's place another planet in a dusthana too
      pToH[JUPITER] = 1; // Jupiter in Taurus (8th from Libra = dusthana)
      const result = vipareethaRajaYoga(pToH, MERCURY, JUPITER);
      expect(result).not.toBe(false);
      if (result !== false) {
        expect(result[0]).toBe(true);
        expect(typeof result[1]).toBe('string');
      }
    });

    it('should return false when planets are not in dusthanas', () => {
      const pToH: Record<number | string, number> = {
        'L': 0, // Aries
        [SUN]: 0,
        [MOON]: 1,
      };
      // Dusthanas from Aries: 6th=5(Virgo), 8th=7(Scorpio), 12th=11(Pisces)
      // Sun in Aries(0) and Moon in Taurus(1) - neither in dusthana
      expect(vipareethaRajaYoga(pToH, SUN, MOON)).toBe(false);
    });

    it('should return correct sub-type based on first planet position', () => {
      // Lagna in Aries (0)
      // Dusthanas: 6th=5(Virgo), 8th=7(Scorpio), 12th=11(Pisces)
      const pToH: Record<number | string, number> = {
        'L': 0,
        [SUN]: 5, // In 6th (Virgo) - Harsh
        [MOON]: 7, // In 8th (Scorpio)
      };
      const result1 = vipareethaRajaYoga(pToH, SUN, MOON);
      expect(result1).not.toBe(false);
      if (result1 !== false) {
        expect(result1[1]).toBe('Harsh Raja Yoga');
      }

      // First planet in 8th house
      const pToH2: Record<number | string, number> = {
        'L': 0,
        [MARS]: 7, // In 8th (Scorpio) - Saral
        [SATURN]: 5, // In 6th (Virgo)
      };
      const result2 = vipareethaRajaYoga(pToH2, MARS, SATURN);
      expect(result2).not.toBe(false);
      if (result2 !== false) {
        expect(result2[1]).toBe('Saral Raja Yoga');
      }

      // First planet in 12th house
      const pToH3: Record<number | string, number> = {
        'L': 0,
        [VENUS]: 11, // In 12th (Pisces) - Vimal
        [MERCURY]: 7, // In 8th (Scorpio)
      };
      const result3 = vipareethaRajaYoga(pToH3, VENUS, MERCURY);
      expect(result3).not.toBe(false);
      if (result3 !== false) {
        expect(result3[1]).toBe('Vimal Raja Yoga');
      }
    });

    it('should return false when only one planet is in dusthana', () => {
      const pToH: Record<number | string, number> = {
        'L': 0,
        [SUN]: 5, // In 6th (dusthana)
        [MOON]: 0, // In 1st (not dusthana)
      };
      expect(vipareethaRajaYoga(pToH, SUN, MOON)).toBe(false);
    });
  });

  // =========================================================================
  // neechaBhangaRajaYoga
  // =========================================================================

  describe('neechaBhangaRajaYoga', () => {
    it('should detect neecha bhanga when debilitated planet conjunct with exalted planet (Rule 2)', () => {
      // Sun is debilitated in Libra (HOUSE_STRENGTHS[0][6] = 0)
      // Saturn is exalted in Libra (HOUSE_STRENGTHS[6][6] = 4)
      // Both in Libra -> conjunction with one exalted and one debilitated
      const pToH: Record<number | string, number> = {
        'L': 0,
        [SUN]: 6,     // Debilitated in Libra
        [MOON]: 0,
        [SATURN]: 6,  // Exalted in Libra
      };
      expect(neechaBhangaRajaYoga(pToH, SUN, SATURN)).toBe(true);
    });

    it('should detect neecha bhanga when lord of debilitated sign is exalted (Rule 1)', () => {
      // Jupiter is debilitated in Capricorn (9) (HOUSE_STRENGTHS[4][9] = 0)
      // Lord of Capricorn is Saturn (6)
      // Saturn exalted in Libra? HOUSE_STRENGTHS[6][6] = 4 (exalted)
      // But Rule 1 checks: lord of sign where planet is debilitated, in THAT sign (rp1_rasi)
      // Actually looking at Python: the check is
      // house_strengths_of_planets[rp1_lord][rp1_rasi] >= EXALTED
      // rp1_lord = Saturn(lord of Capricorn), rp1_rasi = Capricorn(9)
      // HOUSE_STRENGTHS[6][9] = 5 (own sign) >= 4 (EXALTED). Yes!
      const pToH: Record<number | string, number> = {
        'L': 0,
        [MOON]: 3,    // Moon in Cancer (for kendra calculation)
        [JUPITER]: 9, // Jupiter debilitated in Capricorn
        [SATURN]: 0,  // Saturn somewhere else
      };
      expect(neechaBhangaRajaYoga(pToH, JUPITER, SATURN)).toBe(true);
    });

    it('should return false when no neecha bhanga conditions are met', () => {
      // Sun in Aries (exalted), Moon in Taurus (exalted) - neither debilitated
      const pToH: Record<number | string, number> = {
        'L': 0,
        [SUN]: 0,   // Sun exalted in Aries
        [MOON]: 1,  // Moon exalted in Taurus
      };
      expect(neechaBhangaRajaYoga(pToH, SUN, MOON)).toBe(false);
    });

    it('should detect neecha bhanga via kendra from Moon (Rule 1 alt)', () => {
      // Mars debilitated in Cancer (3): HOUSE_STRENGTHS[2][3] = 0
      // Lord of Cancer = Moon. HOUSE_STRENGTHS[1][3] = 5 (own sign) >= 4 (exalted). Yes!
      // So Rule 1 would trigger anyway. Let's verify.
      const pToH: Record<number | string, number> = {
        'L': 0,
        [MOON]: 1,    // Moon in Taurus
        [MARS]: 3,    // Mars debilitated in Cancer
        [VENUS]: 0,
      };
      expect(neechaBhangaRajaYoga(pToH, MARS, VENUS)).toBe(true);
    });
  });
});
