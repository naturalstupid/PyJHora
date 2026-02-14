import { describe, expect, it } from 'vitest';
import {
  JUPITER, KETU, MARS, MERCURY, MOON, RAHU, SATURN, SUN, VENUS,
  ARIES, TAURUS, GEMINI, CANCER, LEO, VIRGO, LIBRA, SCORPIO,
  SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES
} from '../../../src/core/constants';
import {
  getArgala, getCharaKarakas, getRaasiDrishtiFromChart,
  getLordOfSign, getRelativeHouseOfPlanet, getStrongerPlanetFromPositions,
  getStrongerRasi
} from '../../../src/core/horoscope/house';

describe('House Calculations', () => {

  describe('getArgala', () => {
    it('should calculate primary Argala accurately', () => {
      // Setup: Ascendant in Aries (0).
      // Planet in Taurus (1) -> 2nd house from Asc -> Causes Argala on Asc (House 1)
      // Planet in Cancer (3) -> 4th house from Asc -> Causes Argala on Asc
      // Planet in Aquarius (10) -> 11th house from Asc -> Causes Argala on Asc

      const planetToHouse: Record<number | string, number> = {
        [SUN]: 1, // Taurus (2nd from Ari)
        [MOON]: 3, // Cancer (4th from Ari)
        [MARS]: 10, // Aquarius (11th from Ari)
        [MERCURY]: 0, // Aries (1st)
        'L': 0 // Ascendant in Aries
      };

      const ascendantRasi = 0; // Aries

      const { argala, virodhargala } = getArgala(planetToHouse, ascendantRasi);

      // argala[0] correponds to 1st House (Aries)
      // Expect Sun, Moon, Mars to cause Argala on 1st House
      expect(argala[0]).toContain(SUN);
      expect(argala[0]).toContain(MOON);
      expect(argala[0]).toContain(MARS);
      expect(argala[0]).not.toContain(MERCURY); // In 1st house doesn't cause Argala on 1st (usually)

      // Check specific lists
      // Argala on House 1 (Index 0) comes from 2, 4, 11 (Taurus, Cancer, Aquarius)
      // Taurus has SUN. Cancer has MOON. Aquarius has MARS.
      expect(argala[0].sort()).toEqual([SUN, MOON, MARS].sort());
    });

    it('should calculate primary Obstruction (Virodha Argala)', () => {
        // Setup: Asc in Aries (0)
        // Obstruction from 12 (Pisces), 10 (Capricorn), 3 (Gemini)

        const planetToHouse: Record<number | string, number> = {
            [SATURN]: 11, // Pisces (12th from Ari)
            [JUPITER]: 9, // Capricorn (10th from Ari)
            [VENUS]: 2, // Gemini (3rd from Ari)
            'L': 0
        };

        const { virodhargala } = getArgala(planetToHouse, 0);

        expect(virodhargala[0]).toContain(SATURN);
        expect(virodhargala[0]).toContain(JUPITER);
        expect(virodhargala[0]).toContain(VENUS);
    });

    it('should calculate Argala for non-Aries ascendant', () => {
        // Ascendant in Leo (4)
        // Argala on House 1 (Leo) from 2nd (Virgo=5), 4th (Scorpio=7), 11th (Gemini=2)
        const planetToHouse: Record<number | string, number> = {
            [SUN]: 5,    // Virgo (2nd from Leo)
            [MOON]: 7,   // Scorpio (4th from Leo)
            [MARS]: 2,   // Gemini (11th from Leo)
            'L': 4
        };

        const { argala } = getArgala(planetToHouse, 4);

        // House 0 is 1st house = Leo
        expect(argala[0]).toContain(SUN);
        expect(argala[0]).toContain(MOON);
        expect(argala[0]).toContain(MARS);
    });

    it('should return empty arrays for houses with no argala', () => {
        const planetToHouse: Record<number | string, number> = {
            [SUN]: 0,
            'L': 0
        };

        const { argala, virodhargala } = getArgala(planetToHouse, 0);

        // Most houses should have empty argala lists
        // Sun in Aries causes argala only on specific houses
        let emptyCount = 0;
        for (let h = 0; h < 12; h++) {
            if (argala[h].length === 0) emptyCount++;
        }
        expect(emptyCount).toBeGreaterThan(0);
    });
  });

  describe('getRaasiDrishtiFromChart', () => {
      it('should calculate Movable Sign aspects correctly', () => {
          // Aries (0) is Movable. Aspects Fixed signs (1, 4, 7, 10) EXCEPT adjacent (1).
          // So Aries aspects Leo (4), Scorpio (7), Aquarius (10).

          const planetToHouse = {
              [SUN]: 0, // Aries
              [MOON]: 4, // Leo
              [MARS]: 1, // Taurus
          };

          const { arp, app } = getRaasiDrishtiFromChart(planetToHouse);

          // SUN in Aries.
          // Aspects on Rasis (arp[SUN]): Leo, Scorpio, Aquarius.
          expect(arp[SUN]).toContain(4);
          expect(arp[SUN]).toContain(7);
          expect(arp[SUN]).toContain(10);
          expect(arp[SUN]).not.toContain(1); // Taurus is adjacent fixed

          // Aspects on Planets (app[SUN]):
          // Aries aspects Leo. Moon is in Leo. So Sun aspects Moon via Rasi Drishti.
          expect(app[SUN]).toContain(MOON);
          expect(app[SUN]).not.toContain(MARS); // Mars in Taurus (Unaffected)
      });

      it('should calculate Fixed Sign aspects correctly', () => {
          // Taurus (1) is Fixed. Aspects Movable signs (0, 3, 6, 9) EXCEPT adjacent (0).
          // So Taurus aspects Cancer (3), Libra (6), Capricorn (9).
          const planetToHouse = {
              [SUN]: 1, // Taurus
              [MOON]: 3, // Cancer
              [MARS]: 0, // Aries (adjacent - not aspected)
              [JUPITER]: 6, // Libra
          };

          const { arp, app } = getRaasiDrishtiFromChart(planetToHouse);

          // Sun in Taurus aspects Cancer, Libra, Capricorn
          expect(arp[SUN]).toContain(3);  // Cancer
          expect(arp[SUN]).toContain(6);  // Libra
          expect(arp[SUN]).toContain(9);  // Capricorn
          expect(arp[SUN]).not.toContain(0); // Aries is adjacent

          // Sun aspects Moon (Cancer) and Jupiter (Libra) via rasi drishti
          expect(app[SUN]).toContain(MOON);
          expect(app[SUN]).toContain(JUPITER);
          expect(app[SUN]).not.toContain(MARS); // Mars in Aries (not aspected)
      });

      it('should calculate Dual Sign aspects correctly', () => {
          // Gemini (2) is Dual. Aspects all other Dual signs: Virgo (5), Sagittarius (8), Pisces (11).
          const planetToHouse = {
              [SUN]: 2,  // Gemini
              [MOON]: 5, // Virgo
              [MARS]: 8, // Sagittarius
              [JUPITER]: 0, // Aries (not dual - not aspected)
          };

          const { arp, app } = getRaasiDrishtiFromChart(planetToHouse);

          // Sun in Gemini aspects Virgo, Sagittarius, Pisces
          expect(arp[SUN]).toContain(5);  // Virgo
          expect(arp[SUN]).toContain(8);  // Sagittarius
          expect(arp[SUN]).toContain(11); // Pisces
          expect(arp[SUN]).not.toContain(0); // Aries is movable - not aspected

          // Sun aspects Moon (Virgo) and Mars (Sagittarius)
          expect(app[SUN]).toContain(MOON);
          expect(app[SUN]).toContain(MARS);
          expect(app[SUN]).not.toContain(JUPITER); // Jupiter in Aries
      });

      it('should handle Leo (Fixed) aspects', () => {
          // Leo (4) is Fixed. Aspects Movable signs EXCEPT adjacent (3=Cancer, 5=Virgo not movable).
          // Adjacent movable to Leo: Cancer (3) is adjacent.
          // So Leo aspects Aries (0), Libra (6), Capricorn (9), but NOT Cancer (3).
          const planetToHouse = {
              [SUN]: 4,  // Leo
              [MOON]: 0, // Aries
              [MARS]: 3, // Cancer (adjacent)
          };

          const { arp, app } = getRaasiDrishtiFromChart(planetToHouse);

          expect(arp[SUN]).toContain(0);  // Aries
          expect(arp[SUN]).toContain(6);  // Libra
          expect(arp[SUN]).toContain(9);  // Capricorn
          expect(arp[SUN]).not.toContain(3); // Cancer is adjacent

          expect(app[SUN]).toContain(MOON);    // Moon in Aries
          expect(app[SUN]).not.toContain(MARS); // Mars in Cancer (adjacent)
      });
  });

  describe('getCharaKarakas', () => {
      it('should order planets by longitude correctly', () => {
          // Sun: 10 deg, Moon: 20 deg, Mars: 5 deg
          // Order: Moon (AK), Sun (AmK), Mars (BK) ...

          const positions = [
              { planet: SUN, rasi: 0, longitude: 10 },
              { planet: MOON, rasi: 0, longitude: 20 },
              { planet: MARS, rasi: 0, longitude: 5 },
              // Fill others with lower deg to avoid interference
              { planet: MERCURY, rasi: 0, longitude: 1 },
              { planet: JUPITER, rasi: 0, longitude: 1 },
              { planet: VENUS, rasi: 0, longitude: 1 },
              { planet: SATURN, rasi: 0, longitude: 1 },
              { planet: RAHU, rasi: 0, longitude: 29 } // 30-29 = 1 deg effective
          ];

          const karakas = getCharaKarakas(positions);

          expect(karakas[0]).toBe(MOON); // Atma Karaka
          expect(karakas[1]).toBe(SUN);  // Amatya Karaka
          expect(karakas[2]).toBe(MARS); // Bhratri Karaka
      });

      it('should return 8 karakas (7 planets + Rahu)', () => {
          const positions = [
              { planet: SUN, rasi: 0, longitude: 25 },
              { planet: MOON, rasi: 1, longitude: 15 },
              { planet: MARS, rasi: 2, longitude: 10 },
              { planet: MERCURY, rasi: 3, longitude: 20 },
              { planet: JUPITER, rasi: 4, longitude: 5 },
              { planet: VENUS, rasi: 5, longitude: 28 },
              { planet: SATURN, rasi: 6, longitude: 12 },
              { planet: RAHU, rasi: 7, longitude: 8 } // 30-8 = 22 deg effective
          ];

          const karakas = getCharaKarakas(positions);
          expect(karakas).toHaveLength(8);
          // Each planet should appear exactly once
          const unique = new Set(karakas);
          expect(unique.size).toBe(8);
      });

      it('should handle Rahu longitude reversal (30 - longitude)', () => {
          // Rahu at 5 deg -> effective 25 deg, should be high in ranking
          const positions = [
              { planet: SUN, rasi: 0, longitude: 10 },
              { planet: MOON, rasi: 0, longitude: 8 },
              { planet: MARS, rasi: 0, longitude: 6 },
              { planet: MERCURY, rasi: 0, longitude: 4 },
              { planet: JUPITER, rasi: 0, longitude: 2 },
              { planet: VENUS, rasi: 0, longitude: 1 },
              { planet: SATURN, rasi: 0, longitude: 3 },
              { planet: RAHU, rasi: 0, longitude: 5 } // 30-5 = 25 deg effective
          ];

          const karakas = getCharaKarakas(positions);
          // Rahu (effective 25 deg) should be first (Atma Karaka)
          expect(karakas[0]).toBe(RAHU);
      });
  });

  describe('getStrongerPlanetFromPositions', () => {
      // Sample positions for testing stronger planet determination
      const samplePositions = [
          { planet: -1, rasi: 9, longitude: 15 },  // Ascendant in Capricorn
          { planet: SUN, rasi: 7, longitude: 22 },
          { planet: MOON, rasi: 6, longitude: 8 },
          { planet: MARS, rasi: 5, longitude: 12 },
          { planet: MERCURY, rasi: 7, longitude: 5 },
          { planet: JUPITER, rasi: 8, longitude: 18 },
          { planet: VENUS, rasi: 9, longitude: 25 },
          { planet: SATURN, rasi: 11, longitude: 10 },
          { planet: RAHU, rasi: 5, longitude: 20 },
          { planet: KETU, rasi: 11, longitude: 20 }
      ];

      it('should return same planet when both are equal', () => {
          const result = getStrongerPlanetFromPositions(samplePositions, SUN, SUN);
          expect(result).toBe(SUN);
      });

      it('should determine stronger planet based on conjunction count', () => {
          // Mars (rasi 5) and Rahu (rasi 5) are in same house
          // Mercury (rasi 7) and Sun (rasi 7) are in same house
          // Mars has 1 companion (Rahu), Mercury has 1 companion (Sun) - equal
          // Needs tiebreaker rules
          const result = getStrongerPlanetFromPositions(samplePositions, MARS, MERCURY);
          expect([MARS, MERCURY]).toContain(result);
      });

      it('should return a valid planet ID', () => {
          const result = getStrongerPlanetFromPositions(samplePositions, SUN, MOON);
          expect([SUN, MOON]).toContain(result);
      });

      it('should handle co-lord comparison (Mars vs Ketu for Scorpio)', () => {
          const result = getStrongerPlanetFromPositions(samplePositions, MARS, KETU);
          expect([MARS, KETU]).toContain(result);
      });

      it('should handle co-lord comparison (Saturn vs Rahu for Aquarius)', () => {
          const result = getStrongerPlanetFromPositions(samplePositions, SATURN, RAHU);
          expect([SATURN, RAHU]).toContain(result);
      });
  });

  describe('getStrongerRasi', () => {
      const samplePositions = [
          { planet: -1, rasi: 9, longitude: 15 },
          { planet: SUN, rasi: 7, longitude: 22 },
          { planet: MOON, rasi: 6, longitude: 8 },
          { planet: MARS, rasi: 5, longitude: 12 },
          { planet: MERCURY, rasi: 7, longitude: 5 },
          { planet: JUPITER, rasi: 8, longitude: 18 },
          { planet: VENUS, rasi: 9, longitude: 25 },
          { planet: SATURN, rasi: 11, longitude: 10 },
          { planet: RAHU, rasi: 5, longitude: 20 },
          { planet: KETU, rasi: 11, longitude: 20 }
      ];

      it('should return one of the two rasis', () => {
          const result = getStrongerRasi(samplePositions, 0, 6);
          expect([0, 6]).toContain(result);
      });

      it('should prefer rasi with more planets', () => {
          // Rasi 7 has Sun and Mercury (2 planets)
          // Rasi 6 has Moon (1 planet)
          const result = getStrongerRasi(samplePositions, 7, 6);
          expect(result).toBe(7);
      });

      it('should prefer rasi with more planets (rasi 5 vs empty rasi)', () => {
          // Rasi 5 has Mars and Rahu (2 planets)
          // Rasi 0 has no planets
          const result = getStrongerRasi(samplePositions, 5, 0);
          expect(result).toBe(5);
      });
  });

});

// ============================================================================
// Python Parity Tests: Chennai 1996-12-07 10:34
// ============================================================================

describe('House parity with Python (Chennai 1996-12-07)', () => {

  // D-1 positions matching the Python house_to_planet:
  // ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
  const chennaiPositions = [
    { planet: -1, rasi: CAPRICORN, longitude: 15 },  // Ascendant
    { planet: SUN, rasi: SCORPIO, longitude: 22 },
    { planet: MOON, rasi: LIBRA, longitude: 8 },
    { planet: MARS, rasi: LEO, longitude: 12 },
    { planet: MERCURY, rasi: SAGITTARIUS, longitude: 5 },
    { planet: JUPITER, rasi: SAGITTARIUS, longitude: 18 },
    { planet: VENUS, rasi: LIBRA, longitude: 25 },
    { planet: SATURN, rasi: PISCES, longitude: 10 },
    { planet: RAHU, rasi: VIRGO, longitude: 20 },
    { planet: 8, rasi: PISCES, longitude: 20 },  // Ketu
  ];

  describe('getLordOfSign', () => {
    it('should return correct lords for all 12 signs', () => {
      // Aries -> Mars(2), Taurus -> Venus(5), Gemini -> Mercury(3),
      // Cancer -> Moon(1), Leo -> Sun(0), Virgo -> Mercury(3),
      // Libra -> Venus(5), Scorpio -> Mars(2), Sagittarius -> Jupiter(4),
      // Capricorn -> Saturn(6), Aquarius -> Saturn(6), Pisces -> Jupiter(4)
      expect(getLordOfSign(ARIES)).toBe(MARS);
      expect(getLordOfSign(TAURUS)).toBe(VENUS);
      expect(getLordOfSign(GEMINI)).toBe(MERCURY);
      expect(getLordOfSign(CANCER)).toBe(MOON);
      expect(getLordOfSign(LEO)).toBe(SUN);
      expect(getLordOfSign(VIRGO)).toBe(MERCURY);
      expect(getLordOfSign(LIBRA)).toBe(VENUS);
      expect(getLordOfSign(SCORPIO)).toBe(MARS);
      expect(getLordOfSign(SAGITTARIUS)).toBe(JUPITER);
      expect(getLordOfSign(CAPRICORN)).toBe(SATURN);
      expect(getLordOfSign(AQUARIUS)).toBe(SATURN);
      expect(getLordOfSign(PISCES)).toBe(JUPITER);
    });
  });

  describe('getRelativeHouseOfPlanet', () => {
    it('should return correct relative house numbers', () => {
      // From Capricorn (9) ascendant:
      // Sun in Scorpio (7): (7 + 12 - 9) % 12 + 1 = 11
      expect(getRelativeHouseOfPlanet(CAPRICORN, SCORPIO)).toBe(11);

      // Moon in Libra (6): (6 + 12 - 9) % 12 + 1 = 10
      expect(getRelativeHouseOfPlanet(CAPRICORN, LIBRA)).toBe(10);

      // Mars in Leo (4): (4 + 12 - 9) % 12 + 1 = 8
      expect(getRelativeHouseOfPlanet(CAPRICORN, LEO)).toBe(8);

      // Jupiter in Sagittarius (8): (8 + 12 - 9) % 12 + 1 = 12
      expect(getRelativeHouseOfPlanet(CAPRICORN, SAGITTARIUS)).toBe(12);

      // Venus in Libra (6): same as Moon
      expect(getRelativeHouseOfPlanet(CAPRICORN, LIBRA)).toBe(10);

      // Saturn in Pisces (11): (11 + 12 - 9) % 12 + 1 = 3
      expect(getRelativeHouseOfPlanet(CAPRICORN, PISCES)).toBe(3);

      // Same house should return 1
      expect(getRelativeHouseOfPlanet(CAPRICORN, CAPRICORN)).toBe(1);
    });
  });

  describe('getStrongerPlanetFromPositions', () => {
    it('should return one of the two planets being compared', () => {
      // The function should always return either p1 or p2
      const result = getStrongerPlanetFromPositions(chennaiPositions, SUN, MOON);
      expect([SUN, MOON]).toContain(result);
    });

    it('should return same planet when comparing to itself', () => {
      expect(getStrongerPlanetFromPositions(chennaiPositions, MARS, MARS)).toBe(MARS);
    });

    it('should prefer planet with more conjunctions (Rule 1)', () => {
      // Mercury(3) and Jupiter(4) are both in Sagittarius (2 planets in house)
      // Mars(2) is alone in Leo (0 other planets)
      // Mercury vs Mars: Mercury has more conjunctions -> Mercury should be stronger
      const result = getStrongerPlanetFromPositions(chennaiPositions, MERCURY, MARS);
      expect(result).toBe(MERCURY);
    });

    it('should handle planets in same house', () => {
      // Moon(1) and Venus(5) are both in Libra
      const result = getStrongerPlanetFromPositions(chennaiPositions, MOON, VENUS);
      // Both have the same conjunction count, so tiebreakers apply
      expect([MOON, VENUS]).toContain(result);
    });
  });

  describe('getStrongerRasi', () => {
    it('should compare Aries vs Libra', () => {
      // Both are movable signs, comparison should use tiebreaker rules
      const result = getStrongerRasi(chennaiPositions, ARIES, LIBRA);
      // Libra has planets (Moon, Venus), Aries has none -> Libra is stronger
      expect(result).toBe(LIBRA);
    });

    it('should prefer signs with more planets', () => {
      // Sagittarius has Mercury, Jupiter (2 planets); Scorpio has Sun (1 planet)
      const result = getStrongerRasi(chennaiPositions, SAGITTARIUS, SCORPIO);
      expect(result).toBe(SAGITTARIUS);
    });
  });
});

// ============================================================================
// Python-Exact Parity Tests
// ============================================================================

describe('Python-exact parity: Chara Karakas', () => {
  // Planet positions for chara karaka test
  // Python result: [4, 2, 5, 0, 7, 3, 1, 6]
  // AK=Jupiter(4), AmK=Mars(2), BK=Venus(5), MK=Sun(0),
  // PK=Rahu(7), GK=Mercury(3), DK=Moon(1), JK=Saturn(6)
  const sampleD1Positions = [
    { planet: -1, rasi: 9, longitude: 22.45 },  // Lagna (excluded from karakas)
    { planet: SUN, rasi: 7, longitude: 21.57 },
    { planet: MOON, rasi: 6, longitude: 6.96 },
    { planet: MARS, rasi: 4, longitude: 25.54 },
    { planet: MERCURY, rasi: 8, longitude: 9.94 },
    { planet: JUPITER, rasi: 8, longitude: 25.83 },
    { planet: VENUS, rasi: 6, longitude: 23.72 },
    { planet: SATURN, rasi: 11, longitude: 6.81 },
    { planet: RAHU, rasi: 5, longitude: 10.55 },
    { planet: KETU, rasi: 11, longitude: 10.55 },
  ];

  it('should match Python exact chara karaka order [4, 2, 5, 0, 7, 3, 1, 6]', () => {
    // Python: chara_karakas returns [4, 2, 5, 0, 7, 3, 1, 6]
    // Longitudes within sign:
    //   Jupiter: 25.83, Mars: 25.54, Venus: 23.72, Sun: 21.57,
    //   Rahu: 30-10.55=19.45, Mercury: 9.94, Moon: 6.96, Saturn: 6.81
    const karakas = getCharaKarakas(sampleD1Positions);

    expect(karakas).toHaveLength(8);
    expect(karakas).toEqual([JUPITER, MARS, VENUS, SUN, RAHU, MERCURY, MOON, SATURN]);
  });

  it('should identify Atma Karaka as Jupiter (planet with highest longitude in sign)', () => {
    const karakas = getCharaKarakas(sampleD1Positions);
    expect(karakas[0]).toBe(JUPITER); // AK
  });

  it('should identify Amatya Karaka as Mars', () => {
    const karakas = getCharaKarakas(sampleD1Positions);
    expect(karakas[1]).toBe(MARS); // AmK
  });

  it('should identify Dara Karaka as Saturn (planet with lowest longitude in sign)', () => {
    const karakas = getCharaKarakas(sampleD1Positions);
    expect(karakas[7]).toBe(SATURN); // DK (last = lowest longitude)
  });

  it('should correctly reverse Rahu longitude (30 - 10.55 = 19.45)', () => {
    // Rahu at 10.55 becomes effective 19.45, placing it 5th (PK)
    const karakas = getCharaKarakas(sampleD1Positions);
    expect(karakas[4]).toBe(RAHU); // Pitri Karaka
  });
});

describe('Python-exact parity: Raasi Drishti from Chart', () => {
  // Chennai chart: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
  // planetToHouse maps: planet -> rasi index
  const chennaiPlanetToHouse: Record<number, number> = {
    [SUN]: SCORPIO,        // 7
    [MOON]: LIBRA,         // 6
    [MARS]: LEO,           // 4
    [MERCURY]: SAGITTARIUS, // 8
    [JUPITER]: SAGITTARIUS, // 8
    [VENUS]: LIBRA,        // 6
    [SATURN]: PISCES,      // 11
    [RAHU]: VIRGO,         // 5
    [KETU]: PISCES,        // 11
  };

  // Python output for arp (planet -> aspected rasis):
  // {0: [0, 3, 9], 1: [1, 4, 10], 2: [0, 6, 9], 3: [2, 5, 11],
  //  4: [2, 5, 11], 5: [1, 4, 10], 6: [2, 5, 8], 7: [2, 8, 11], 8: [2, 5, 8]}

  it('should match Python raasi drishti for Sun in Scorpio (Fixed)', () => {
    // Scorpio(7) is Fixed. Aspects Movable signs except adjacent.
    // Adjacent to 7: 6(Libra) and 8(Sagittarius). Movable: 0,3,6,9. Exclude 6.
    // Result: [0, 3, 9] = [Aries, Cancer, Capricorn]
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[SUN].sort()).toEqual([ARIES, CANCER, CAPRICORN].sort());
  });

  it('should match Python raasi drishti for Moon in Libra (Movable)', () => {
    // Libra(6) is Movable. Aspects Fixed signs except adjacent.
    // Adjacent to 6: 5(Virgo) and 7(Scorpio). Fixed: 1,4,7,10. Exclude 7.
    // Result: [1, 4, 10] = [Taurus, Leo, Aquarius]
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[MOON].sort()).toEqual([TAURUS, LEO, AQUARIUS].sort());
  });

  it('should match Python raasi drishti for Mars in Leo (Fixed)', () => {
    // Leo(4) is Fixed. Aspects Movable except adjacent.
    // Adjacent to 4: 3(Cancer) and 5(Virgo). Movable: 0,3,6,9. Exclude 3.
    // Result: [0, 6, 9] = [Aries, Libra, Capricorn]
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[MARS].sort()).toEqual([ARIES, LIBRA, CAPRICORN].sort());
  });

  it('should match Python raasi drishti for Mercury in Sagittarius (Dual)', () => {
    // Sagittarius(8) is Dual. Aspects other Duals: 2, 5, 11.
    // Result: [2, 5, 11] = [Gemini, Virgo, Pisces]
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[MERCURY].sort()).toEqual([GEMINI, VIRGO, PISCES].sort());
  });

  it('should match Python raasi drishti for Jupiter in Sagittarius (Dual)', () => {
    // Same sign as Mercury -> same aspects
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[JUPITER].sort()).toEqual([GEMINI, VIRGO, PISCES].sort());
  });

  it('should match Python raasi drishti for Saturn in Pisces (Dual)', () => {
    // Pisces(11) is Dual. Aspects other Duals: 2, 5, 8.
    // Result: [2, 5, 8] = [Gemini, Virgo, Sagittarius]
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[SATURN].sort()).toEqual([GEMINI, VIRGO, SAGITTARIUS].sort());
  });

  it('should match Python raasi drishti for Rahu in Virgo (Dual)', () => {
    // Virgo(5) is Dual. Aspects other Duals: 2, 8, 11.
    // Result: [2, 8, 11] = [Gemini, Sagittarius, Pisces]
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[RAHU].sort()).toEqual([GEMINI, SAGITTARIUS, PISCES].sort());
  });

  it('should match Python raasi drishti for Ketu in Pisces (Dual)', () => {
    // Same sign as Saturn -> same aspects
    const { arp } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(arp[KETU].sort()).toEqual([GEMINI, VIRGO, SAGITTARIUS].sort());
  });

  it('should derive correct planet aspects (app) for Mars in Leo', () => {
    // Mars in Leo(4) aspects rasis [0, 6, 9].
    // Aries(0): empty -> no planets aspected
    // Libra(6): Moon(1), Venus(5) -> Mars aspects Moon and Venus
    // Capricorn(9): empty (only Lagna, not in planetToHouse) -> no planets
    const { app } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(app[MARS]).toContain(MOON);
    expect(app[MARS]).toContain(VENUS);
    expect(app[MARS]).not.toContain(SUN);
    expect(app[MARS]).not.toContain(MERCURY);
  });

  it('should derive correct planet aspects (app) for Saturn in Pisces', () => {
    // Saturn in Pisces(11) aspects rasis [2, 5, 8].
    // Gemini(2): empty
    // Virgo(5): Rahu(7)
    // Sagittarius(8): Mercury(3), Jupiter(4)
    const { app } = getRaasiDrishtiFromChart(chennaiPlanetToHouse);
    expect(app[SATURN]).toContain(RAHU);
    expect(app[SATURN]).toContain(MERCURY);
    expect(app[SATURN]).toContain(JUPITER);
    expect(app[SATURN]).not.toContain(SUN);
    expect(app[SATURN]).not.toContain(MOON);
  });
});

describe('Python-exact parity: Stronger Rasi', () => {
  // Chennai chart positions (excluding Lagna to match Python behavior,
  // which explicitly excludes the ascendant symbol in planet count)
  const chennaiPositionsNoLagna = [
    { planet: SUN, rasi: SCORPIO, longitude: 22 },
    { planet: MOON, rasi: LIBRA, longitude: 8 },
    { planet: MARS, rasi: LEO, longitude: 12 },
    { planet: MERCURY, rasi: SAGITTARIUS, longitude: 5 },
    { planet: JUPITER, rasi: SAGITTARIUS, longitude: 18 },
    { planet: VENUS, rasi: LIBRA, longitude: 25 },
    { planet: SATURN, rasi: PISCES, longitude: 10 },
    { planet: RAHU, rasi: VIRGO, longitude: 20 },
    { planet: KETU, rasi: PISCES, longitude: 20 },
  ];

  it('should match Python: Aries(0) vs Libra(6) -> Libra wins', () => {
    // Python result: Libra(6) is stronger
    // Aries has 0 planets, Libra has 2 (Moon, Venus) -> Rule 1: Libra wins
    const result = getStrongerRasi(chennaiPositionsNoLagna, ARIES, LIBRA);
    expect(result).toBe(LIBRA);
  });

  it('should match Python: Capricorn(9) vs Cancer(3) -> Cancer wins', () => {
    // Python result: Cancer(3) is stronger
    // Both have 0 planets (Lagna excluded) -> falls through to tiebreakers
    // Rule 4 (oddity): Capricorn(9) lord Saturn(6) in Pisces(11).
    //   Capricorn is even, Pisces is even -> same oddity -> not different
    // Cancer(3) lord Moon(1) in Libra(6).
    //   Cancer is even, Libra is odd -> different oddity -> Cancer gets the edge
    const result = getStrongerRasi(chennaiPositionsNoLagna, CAPRICORN, CANCER);
    expect(result).toBe(CANCER);
  });

  it('should match Python: Sagittarius vs Scorpio -> Sagittarius wins', () => {
    // Sagittarius has Mercury + Jupiter (2 planets), Scorpio has Sun (1 planet)
    // Rule 1: more planets wins
    const result = getStrongerRasi(chennaiPositionsNoLagna, SAGITTARIUS, SCORPIO);
    expect(result).toBe(SAGITTARIUS);
  });
});
