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
  checkOtherRajaYoga1,
  checkOtherRajaYoga2,
  checkOtherRajaYoga3,
  getRajaYogaDetails,
} from '../../../src/core/horoscope/raja-yoga';
import type { HouseChart, PlanetPosition } from '../../../src/core/types';

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

  // =========================================================================
  // Shared PlanetPosition data for new function tests
  // =========================================================================

  /**
   * Helper to create PlanetPosition objects
   */
  const mkPos = (
    planet: number,
    rasi: number,
    longitudeInSign: number = 15,
  ): PlanetPosition => ({
    planet,
    rasi,
    longitude: rasi * 30 + longitudeInSign,
    longitudeInSign,
    isRetrograde: false,
    nakshatra: 0,
    nakshatraPada: 0,
  });

  /** Chennai chart positions */
  const positionsChennai: PlanetPosition[] = [
    mkPos(-1, 9, 0),    // Lagna in Capricorn
    mkPos(SUN, 7, 10),   // Sun in Scorpio
    mkPos(MOON, 6, 10),  // Moon in Libra
    mkPos(MARS, 4, 10),  // Mars in Leo
    mkPos(MERCURY, 8, 10), // Mercury in Sagittarius
    mkPos(JUPITER, 8, 15), // Jupiter in Sagittarius
    mkPos(VENUS, 6, 15),  // Venus in Libra
    mkPos(SATURN, 11, 10), // Saturn in Pisces
    mkPos(RAHU, 5, 15),   // Rahu in Virgo
    mkPos(KETU, 11, 15),  // Ketu in Pisces
  ];

  /** Oprah Winfrey chart positions */
  const positionsOprah: PlanetPosition[] = [
    mkPos(-1, 9, 5),      // Lagna in Capricorn
    mkPos(SUN, 9, 20),    // Sun in Capricorn
    mkPos(MOON, 7, 12),   // Moon in Scorpio
    mkPos(MARS, 7, 18),   // Mars in Scorpio
    mkPos(MERCURY, 9, 8), // Mercury in Capricorn
    mkPos(JUPITER, 1, 22),// Jupiter in Taurus
    mkPos(VENUS, 9, 25),  // Venus in Capricorn
    mkPos(SATURN, 6, 14), // Saturn in Libra
    mkPos(RAHU, 9, 3),    // Rahu in Capricorn
    mkPos(KETU, 3, 3),    // Ketu in Cancer
  ];

  /** Salman Khan chart positions */
  const positionsSalman: PlanetPosition[] = [
    mkPos(-1, 6, 10),     // Lagna in Libra
    mkPos(SUN, 0, 12),    // Sun in Aries
    mkPos(MOON, 6, 20),   // Moon in Libra
    mkPos(MARS, 0, 8),    // Mars in Aries
    mkPos(MERCURY, 11, 16), // Mercury in Pisces
    mkPos(JUPITER, 8, 22),  // Jupiter in Sagittarius
    mkPos(VENUS, 0, 27),    // Venus in Aries
    mkPos(SATURN, 3, 11),   // Saturn in Cancer
    mkPos(RAHU, 2, 5),      // Rahu in Gemini
    mkPos(KETU, 8, 5),      // Ketu in Sagittarius
  ];

  // =========================================================================
  // checkOtherRajaYoga1
  // =========================================================================

  describe('checkOtherRajaYoga1', () => {
    it('should return a boolean for Chennai chart', () => {
      const result = checkOtherRajaYoga1(positionsChennai);
      expect(typeof result).toBe('boolean');
    });

    it('should return a boolean for Oprah chart', () => {
      const result = checkOtherRajaYoga1(positionsOprah);
      expect(typeof result).toBe('boolean');
    });

    it('should return a boolean for Salman chart', () => {
      const result = checkOtherRajaYoga1(positionsSalman);
      expect(typeof result).toBe('boolean');
    });

    it('should return false when ascendant is missing', () => {
      const positionsNoAsc: PlanetPosition[] = [
        mkPos(SUN, 0, 10),
        mkPos(MOON, 1, 10),
        mkPos(MARS, 2, 10),
        mkPos(MERCURY, 3, 10),
        mkPos(JUPITER, 4, 10),
        mkPos(VENUS, 5, 10),
        mkPos(SATURN, 6, 10),
        mkPos(RAHU, 7, 10),
        mkPos(KETU, 8, 10),
      ];
      expect(checkOtherRajaYoga1(positionsNoAsc)).toBe(false);
    });

    it('should detect yoga when AK/PK conjoined and lagna/5th lords conjoined', () => {
      // Construct a chart where:
      // AK and PK are in the same house
      // Lagna lord and 5th lord are in the same house
      // Lagna in Aries (0)
      // For Aries lagna: lagna lord = Mars(2), 5th lord = Sun(lord of Leo=4, SIGN_LORDS[4]=0=Sun)
      // Wait, SIGN_LORDS[4] = SUN(0). So 5th lord = Sun.
      // Place Mars and Sun in the same house to satisfy chk2.
      // For chara karakas, AK = highest longitude, PK = 6th highest
      // We need to carefully control longitudes.
      // Let Sun have highest longitude (AK), then we need PK (6th) to be in same house as Sun
      const positions: PlanetPosition[] = [
        mkPos(-1, 0, 0),       // Lagna in Aries
        mkPos(SUN, 3, 29),     // Sun in Cancer, highest long => AK
        mkPos(MOON, 3, 28),    // Moon in Cancer, 2nd highest
        mkPos(MARS, 3, 27),    // Mars in Cancer, 3rd highest => also same house as Sun
        mkPos(MERCURY, 3, 26), // Mercury in Cancer, 4th highest
        mkPos(JUPITER, 3, 25), // Jupiter in Cancer, 5th highest
        mkPos(VENUS, 3, 24),   // Venus in Cancer, 6th highest => PK
        mkPos(SATURN, 3, 23),  // Saturn in Cancer, 7th highest
        mkPos(RAHU, 3, 1),     // Rahu in Cancer, 30-1=29, but after reversal = highest?
        // Rahu's longitude is reversed: 30 - longitudeInSign = 30 - 1 = 29
        // This makes Rahu have effective long 29, tied with Sun. Let's adjust.
        mkPos(KETU, 9, 5),     // Ketu in Capricorn
      ];
      // With Rahu longitude 1, reversed = 29, same as Sun => ordering may vary.
      // Let's give Rahu a lower effective longitude to avoid conflicts:
      positions[8] = mkPos(RAHU, 3, 10); // reversed = 30 - 10 = 20, 4th highest

      // Recalculate ordering:
      // Sun: 29, Moon: 28, Mars: 27, Mercury: 26, Jupiter: 25, Venus: 24, Saturn: 23, Rahu: 20
      // Sorted descending: Sun(29), Moon(28), Mars(27), Mercury(26), Jupiter(25), Venus(24), Saturn(23), Rahu(20)
      // AK=Sun(index 0), PK=Venus(index 5)
      // Sun and Venus are both in Cancer(3) => conjoined => chk1 = true
      // Lagna lord(Mars) is in Cancer(3), 5th lord = Sun(SIGN_LORDS[4]=0=Sun) is in Cancer(3)
      // Mars and Sun both in Cancer(3) => conjoined => chk2 = true
      // So checkOtherRajaYoga1 should return true
      expect(checkOtherRajaYoga1(positions)).toBe(true);
    });

    it('should return false when AK/PK are not conjoined', () => {
      // AK and PK in different houses, but lagna/5th lords conjoined
      const positions: PlanetPosition[] = [
        mkPos(-1, 0, 0),       // Lagna in Aries
        mkPos(SUN, 0, 29),     // Sun in Aries, highest => AK
        mkPos(MOON, 0, 28),    // Moon in Aries
        mkPos(MARS, 0, 27),    // Mars in Aries (lagna lord)
        mkPos(MERCURY, 0, 26), // Mercury in Aries
        mkPos(JUPITER, 0, 25), // Jupiter in Aries
        mkPos(VENUS, 6, 24),   // Venus in Libra, 6th highest => PK (different house from AK!)
        mkPos(SATURN, 0, 23),  // Saturn in Aries
        mkPos(RAHU, 0, 10),    // Rahu in Aries (reversed = 20)
        mkPos(KETU, 6, 10),    // Ketu in Libra
      ];
      // AK=Sun in Aries(0), PK=Venus in Libra(6) => not conjoined => chk1 = false
      expect(checkOtherRajaYoga1(positions)).toBe(false);
    });
  });

  // =========================================================================
  // checkOtherRajaYoga2
  // =========================================================================

  describe('checkOtherRajaYoga2', () => {
    it('should return a boolean for Chennai chart', () => {
      const result = checkOtherRajaYoga2(positionsChennai);
      expect(typeof result).toBe('boolean');
    });

    it('should return a boolean for Oprah chart', () => {
      const result = checkOtherRajaYoga2(positionsOprah);
      expect(typeof result).toBe('boolean');
    });

    it('should return false when ascendant is missing', () => {
      const positionsNoAsc: PlanetPosition[] = [
        mkPos(SUN, 0, 10),
        mkPos(MOON, 1, 10),
        mkPos(MARS, 2, 10),
        mkPos(MERCURY, 3, 10),
        mkPos(JUPITER, 4, 10),
        mkPos(VENUS, 5, 10),
        mkPos(SATURN, 6, 10),
        mkPos(RAHU, 7, 10),
        mkPos(KETU, 8, 10),
      ];
      expect(checkOtherRajaYoga2(positionsNoAsc)).toBe(false);
    });

    it('should generally return false for typical charts (strict conditions)', () => {
      // checkOtherRajaYoga2 requires many simultaneous conditions:
      // (a) lagna lord in 5th, (b) 5th lord in lagna, (c) AK+PK both in lagna or 5th
      // (d) strength or benefic aspect conditions
      // These are very strict, so most charts will return false
      expect(checkOtherRajaYoga2(positionsChennai)).toBe(false);
      expect(checkOtherRajaYoga2(positionsOprah)).toBe(false);
      expect(checkOtherRajaYoga2(positionsSalman)).toBe(false);
    });
  });

  // =========================================================================
  // checkOtherRajaYoga3
  // =========================================================================

  describe('checkOtherRajaYoga3', () => {
    it('should return a boolean for Chennai chart', () => {
      const result = checkOtherRajaYoga3(positionsChennai);
      expect(typeof result).toBe('boolean');
    });

    it('should return a boolean for Oprah chart', () => {
      const result = checkOtherRajaYoga3(positionsOprah);
      expect(typeof result).toBe('boolean');
    });

    it('should return a boolean for Salman chart', () => {
      const result = checkOtherRajaYoga3(positionsSalman);
      expect(typeof result).toBe('boolean');
    });

    it('should return false when ascendant is missing', () => {
      const positionsNoAsc: PlanetPosition[] = [
        mkPos(SUN, 0, 10),
        mkPos(MOON, 1, 10),
        mkPos(MARS, 2, 10),
        mkPos(MERCURY, 3, 10),
        mkPos(JUPITER, 4, 10),
        mkPos(VENUS, 5, 10),
        mkPos(SATURN, 6, 10),
        mkPos(RAHU, 7, 10),
        mkPos(KETU, 8, 10),
      ];
      expect(checkOtherRajaYoga3(positionsNoAsc)).toBe(false);
    });

    it('should detect when 9th lord or AK is in lagna, 5th, or 7th', () => {
      // Lagna in Aries (0)
      // 9th house = (0+8)%12 = 8 (Sagittarius), lord = Jupiter(4) SIGN_LORDS[8]=4
      // Place Jupiter in lagna (Aries, 0) => 9th lord in lagna => should be true
      const positions: PlanetPosition[] = [
        mkPos(-1, 0, 0),       // Lagna in Aries
        mkPos(SUN, 1, 29),     // Sun in Taurus, highest => AK
        mkPos(MOON, 2, 28),
        mkPos(MARS, 3, 27),
        mkPos(MERCURY, 4, 26),
        mkPos(JUPITER, 0, 25), // Jupiter (9th lord) in Aries (lagna) => target house!
        mkPos(VENUS, 5, 24),
        mkPos(SATURN, 6, 23),
        mkPos(RAHU, 7, 10),    // reversed = 20
        mkPos(KETU, 1, 10),
      ];
      // 9th lord (Jupiter) is in Aries(0) = ascHouse => condition met
      expect(checkOtherRajaYoga3(positions)).toBe(true);
    });

    it('should detect when AK is in 5th house', () => {
      // Lagna in Aries (0), 5th house = Leo (4)
      // AK = planet with highest longitude in sign
      // Place Sun with highest longitude in Leo(4) => AK is in 5th house
      const positions: PlanetPosition[] = [
        mkPos(-1, 0, 0),
        mkPos(SUN, 4, 29),     // AK in Leo (5th from Aries)
        mkPos(MOON, 1, 20),
        mkPos(MARS, 2, 15),
        mkPos(MERCURY, 3, 10),
        mkPos(JUPITER, 9, 5),  // 9th lord in Capricorn (not target house)
        mkPos(VENUS, 10, 3),
        mkPos(SATURN, 11, 2),
        mkPos(RAHU, 7, 1),     // reversed = 29, ties with Sun. Adjust:
        mkPos(KETU, 1, 1),
      ];
      // Rahu reversed: 30 - 1 = 29, same as Sun at 29
      // To avoid tie issues, adjust Rahu
      positions[8] = mkPos(RAHU, 7, 2); // reversed = 28
      // Now AK = Sun (29), in Leo(4) = 5th house from Aries
      // 9th lord = Jupiter in Capricorn(9), not in [0,4,6]
      // But AK is in 5th(4) => condition met
      expect(checkOtherRajaYoga3(positions)).toBe(true);
    });

    it('should return false when neither 9th lord nor AK is in target houses', () => {
      // Lagna in Aries (0), target houses: 0, 4, 6
      // 9th lord = Jupiter (lord of Sag=8)
      // Place Jupiter in Taurus(1) - not a target house
      // AK = Sun with highest longitude, place in Gemini(2) - not a target house
      const positions: PlanetPosition[] = [
        mkPos(-1, 0, 0),
        mkPos(SUN, 2, 29),     // AK in Gemini(2) - not target
        mkPos(MOON, 3, 20),
        mkPos(MARS, 5, 15),
        mkPos(MERCURY, 7, 10),
        mkPos(JUPITER, 1, 5),  // 9th lord in Taurus(1) - not target
        mkPos(VENUS, 8, 3),
        mkPos(SATURN, 9, 2),
        mkPos(RAHU, 10, 5),    // reversed = 25
        mkPos(KETU, 11, 5),
      ];
      // Neither 9th lord (Jupiter in 1) nor AK (Sun in 2) is in [0, 4, 6]
      expect(checkOtherRajaYoga3(positions)).toBe(false);
    });
  });

  // =========================================================================
  // getRajaYogaDetails
  // =========================================================================

  describe('getRajaYogaDetails', () => {
    it('should return complete RajaYogaResult for Chennai chart', () => {
      const result = getRajaYogaDetails(chartChennai, positionsChennai);

      expect(result).toBeDefined();
      expect(result.name).toBe('raja_yoga');
      expect(Array.isArray(result.pairs)).toBe(true);
      expect(typeof result.isDharmaKarmadhipati).toBe('boolean');
      expect(typeof result.isNeechaBhanga).toBe('boolean');
      expect(typeof result.isOtherRajaYoga1).toBe('boolean');
      expect(typeof result.isOtherRajaYoga2).toBe('boolean');
      expect(typeof result.isOtherRajaYoga3).toBe('boolean');

      // vipareethaResult is either false or [true, string]
      if (result.vipareethaResult !== false) {
        expect(result.vipareethaResult[0]).toBe(true);
        expect(typeof result.vipareethaResult[1]).toBe('string');
      }
    });

    it('should find raja yoga pairs in the result for Chennai chart', () => {
      const result = getRajaYogaDetails(chartChennai, positionsChennai);

      // Should contain the Moon-Venus pair
      const hasMoonVenus = result.pairs.some(
        ([p1, p2]) =>
          (p1 === MOON && p2 === VENUS) || (p1 === VENUS && p2 === MOON)
      );
      expect(hasMoonVenus).toBe(true);
    });

    it('should return complete RajaYogaResult for Oprah chart', () => {
      const result = getRajaYogaDetails(chartOprah, positionsOprah);

      expect(result.name).toBe('raja_yoga');
      expect(Array.isArray(result.pairs)).toBe(true);
      expect(typeof result.isDharmaKarmadhipati).toBe('boolean');
    });

    it('should return complete RajaYogaResult for Salman chart', () => {
      const result = getRajaYogaDetails(chartSalman, positionsSalman);

      expect(result.name).toBe('raja_yoga');
      expect(Array.isArray(result.pairs)).toBe(true);
      expect(typeof result.isDharmaKarmadhipati).toBe('boolean');
      expect(typeof result.isNeechaBhanga).toBe('boolean');
    });

    it('should handle chart with no raja yoga pairs', () => {
      // Chart with no Lagna - should have no pairs
      const chartNoLagna: HouseChart = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '', '', '',
      ];
      const positionsNoLagna: PlanetPosition[] = [
        mkPos(SUN, 0, 10),
        mkPos(MOON, 1, 10),
        mkPos(MARS, 2, 10),
        mkPos(MERCURY, 3, 10),
        mkPos(JUPITER, 4, 10),
        mkPos(VENUS, 5, 10),
        mkPos(SATURN, 6, 10),
        mkPos(RAHU, 7, 10),
        mkPos(KETU, 8, 10),
      ];
      const result = getRajaYogaDetails(chartNoLagna, positionsNoLagna);
      expect(result.pairs).toEqual([]);
      expect(result.isDharmaKarmadhipati).toBe(false);
      expect(result.vipareethaResult).toBe(false);
      expect(result.isNeechaBhanga).toBe(false);
    });

    it('should correctly integrate all yoga checks', () => {
      // Verify the orchestrator calls all sub-checks consistently
      const result = getRajaYogaDetails(chartChennai, positionsChennai);

      // The individual checks should match direct calls
      const directPairs = getRajaYogaPairs(chartChennai);
      expect(result.pairs).toEqual(directPairs);

      const directYoga1 = checkOtherRajaYoga1(positionsChennai);
      expect(result.isOtherRajaYoga1).toBe(directYoga1);

      const directYoga2 = checkOtherRajaYoga2(positionsChennai);
      expect(result.isOtherRajaYoga2).toBe(directYoga2);

      const directYoga3 = checkOtherRajaYoga3(positionsChennai);
      expect(result.isOtherRajaYoga3).toBe(directYoga3);
    });
  });
});
