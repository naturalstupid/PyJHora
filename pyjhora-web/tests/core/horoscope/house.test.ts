import { describe, expect, it } from 'vitest';
import { JUPITER, MARS, MERCURY, MOON, RAHU, SATURN, SUN, VENUS } from '../../../src/core/constants';
import { getArgala, getCharaKarakas, getRaasiDrishtiFromChart } from '../../../src/core/horoscope/house';

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
  });

});
