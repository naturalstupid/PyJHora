
import { describe, expect, it } from 'vitest';
import {
    ARIES,
    CANCER,
    CAPRICORN,
    GEMINI,
    JUPITER,
    LEO,
    MARS,
    MERCURY,
    MOON,
    SAGITTARIUS,
    SATURN,
    SUN,
    TAURUS,
    VENUS
} from '../../../../src/core/constants';
import {
    calculateNarayanaDasha,
    getNarayanaDashaDuration,
    getNarayanaDashaSeedSign
} from '../../../../src/core/dhasa/raasi/narayana';

describe('Narayana Dasha', () => {
    
  // Helper to create planet positions
  const createPlanets = (map: Record<number, number>) => {
      // map: Planet ID -> Rasi
      return Object.entries(map).map(([p, r]) => ({
          planet: parseInt(p),
          rasi: r,
          longitude: 15 // midpoint default
      }));
  };

  describe('getNarayanaDashaDuration', () => {
    it('should calculate duration for Odd Footed Sign (Forward count)', () => {
        // Aries (Odd Footed). Lord Mars in Gemini.
        // Count Aries -> Gemini (Forward)
        // Aries(1) -> Taurus(2) -> Gemini(3). Count = 3.
        // Duration = Count - 1 = 2 years.
        
        const planets = createPlanets({ [MARS]: GEMINI });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(2);
    });

    it('should calculate duration for Even Footed Sign (Reverse count?)', () => {
        // Cancer (Even Footed). Lord Moon in Leo.
        // Count Lord(Leo) -> Sign(Cancer) (Forward from Lord to Sign?)
        // Wait, Python logic:
        // if even_footed: count_rasis(house_of_lord, sign) => Lord to Sign.
        // Leo -> Cancer. Leo(1)..Virgo..Libra..Scorpio..Sag..Cap..Aq..Pis..Ari..Tau..Gem..Can(12).
        // Count = 12.
        // Duration = 12 - 1 = 11 years.
        
        // Let's verify standard counting.
        // From Leo(4) to Cancer(3). (3 - 4 + 12)%12 + 1 = (-1+12)%12 + 1 = 11 + 1 = 12.
        // Wait count_rasis: (to - from + 12)%12 + 1.
        // (3 - 4 + 12)%12 + 1 = 12.
        // Duration = 12 - 1 = 11.
        
        const planets = createPlanets({ [MOON]: LEO });
        const duration = getNarayanaDashaDuration(planets, CANCER);
        expect(duration).toBe(11);
    });
    
    it('should handle Exception 1: Count is 1 -> Duration 12', () => {
        // Aries Lord Mars in Aries.
        // Count Aries -> Aries = 1.
        // Duration = 1 - 1 = 0.
        // Exception -> 12.
        const planets = createPlanets({ [MARS]: ARIES });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(12);
    });
    
    it('should handle Exception 2: Exalted Lord -> +1 year', () => {
        // Aries Lord Mars in Capricorn (Exalted).
        // Aries (Odd Footed). Count Aries -> Capricorn.
        // Ar -> Cap = 10?
        // (9 - 0 + 12)%12 + 1 = 10.
        // Base Duration = 10 - 1 = 9.
        // Exalted (+1) -> 10.
        
        const planets = createPlanets({ [MARS]: CAPRICORN });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(10);
    });
    
    it('should handle Exception 3: Debilitated Lord -> -1 year', () => {
        // Aries Lord Mars in Cancer (Debilitated).
        // Aries (Odd Footed). Count Aries -> Cancer.
        // Ar -> Can = 4.
        // Base Duration = 4 - 1 = 3.
        // Debilitated (-1) -> 2.
        
        const planets = createPlanets({ [MARS]: CANCER });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(2);
    });
  });
  
  describe('getNarayanaDashaSeedSign', () => {
      it('should return stronger of Ascendant and 7th House', () => {
          // Ascendant Aries. 7th Libra.
          // Planets: Sun in Aries (Exalted). Libra empty.
          // Aries should be stronger.
          
          const planets = createPlanets({ [SUN]: ARIES });
          const seed = getNarayanaDashaSeedSign(planets, ARIES);
          expect(seed).toBe(ARIES);
      });
  });
  
  describe('calculateNarayanaDasha', () => {
      it('should generate periods with correct progression', () => {
          // Seed Aries. Normal progression.
          // Aries -> Taurus -> Gemini ...
          // Mock calculate duration to always be 1 for simplicity? No, we use real logic.
          // Let's create a chart where everything is in own house (Duration 12 for all).
          
          const planets = createPlanets({
              [MARS]: ARIES, // Lord of Ar, Sc
              [VENUS]: TAURUS, // Lord of Ta, Li
              [MERCURY]: GEMINI, // Lord of Ge, Vi
              [MOON]: CANCER, // Lord of Cn
              [SUN]: LEO, // Lord of Le
              [JUPITER]: SAGITTARIUS, // Lord of Sg, Pi
              [SATURN]: CAPRICORN // Lord of Cp, Aq
          });
          
          const startDate = new Date('2000-01-01');
          const periods = calculateNarayanaDasha(planets, ARIES, startDate);
          
          expect(periods.length).toBeGreaterThan(0);
          expect(periods[0].sign).toBe(ARIES);
          expect(periods[0].duration).toBe(12);
          
          // Verify end date Logic
          // Start 2000. End 2012.
          expect(periods[0].start.getFullYear()).toBe(2000);
          expect(periods[0].end.getFullYear()).toBe(2012);
          
          // Second period Taurus
          expect(periods[1].sign).toBe(TAURUS);
          expect(periods[1].duration).toBe(12);
          expect(periods[1].start.getFullYear()).toBe(2012);
      });
  });

});
