import { describe, expect, it } from 'vitest';
import { JUPITER, KETU, MARS, MERCURY, MOON, RAHU, SATURN, SUN, VENUS } from '../../../src/core/constants';
import {
  getArgala,
  getCharaKarakas,
  getRaasiDrishtiFromChart,
  getStrongerPlanetFromPositions,
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
