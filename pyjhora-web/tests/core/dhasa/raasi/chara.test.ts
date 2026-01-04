
import { describe, expect, it } from 'vitest';
import {
    ARIES,
    CANCER,
    GEMINI,
    LEO,
    MARS,
    MOON,
    PISCES,
    TAURUS
} from '../../../../src/core/constants';
import {
    getCharaDhasaDuration,
    getCharaDhasaProgression
} from '../../../../src/core/dhasa/raasi/chara';

describe('Chara Dasha (KN Rao)', () => {

  const createPlanets = (map: Record<number, number>) => {
      return Object.entries(map).map(([p, r]) => ({
          planet: parseInt(p),
          rasi: r,
          longitude: 15
      }));
  };

  describe('getCharaDhasaDuration', () => {
       it('should calculate duration for Odd Footed Sign (Forward)', () => {
           // Aries (Odd Footed). Lord Mars in Gemini.
           // Ar -> Ge = 3. Duration = 2.
           const planets = createPlanets({ [MARS]: GEMINI });
           const duration = getCharaDhasaDuration(planets, ARIES);
           expect(duration).toBe(2);
       });
       
       it('should calculate duration for Even Footed Sign (Reverse of Narayana? Or same?)', () => {
           // Narayana Even Footed: Count from Lord TO Sign.
           // Chara Even Footed: Count from Lord TO Sign (Code: countRasis(houseOfLord, sign)).
           // Cancer (Even). Lord Moon in Leo.
           // Leo -> Cancer = 12. Duration = 11.
           
           const planets = createPlanets({ [MOON]: LEO });
           const duration = getCharaDhasaDuration(planets, CANCER);
           expect(duration).toBe(11);
       });
       
       it('should handle Exception 1: Count is 1 -> 12', () => {
           const planets = createPlanets({ [MARS]: ARIES });
           expect(getCharaDhasaDuration(planets, ARIES)).toBe(12);
       });
       
       it('should handle Exception 2: Exalted (+1)', () => {
           // Moon in Taurus (Exalted).
           // Cancer (Even). Count Taurus to Cancer.
           // Ta -> Cn = 3.
           // Duration = 3 - 1 = 2.
           // Exalted +1 => 3.
           const planets = createPlanets({ [MOON]: TAURUS });
           expect(getCharaDhasaDuration(planets, CANCER)).toBe(3);
       });
  });
  
  describe('getCharaDhasaProgression', () => {
      it('should determine forward progression if 9th house from Seed is Odd Footed', () => {
          // Asc (Seed) = Aries. 9th = Sagittarius.
          // Sagittarius is Odd Footed (Odd Signs: Ar, Ge, Le, Li, Sg, Aq. Odd Footed: Ar, Ta, Ge, Li, Sc, Sg).
          // Sagittarius is Odd Footed.
          // Progression Forward: Aries, Taurus, Gemini...
          
          const prog = getCharaDhasaProgression(ARIES);
          expect(prog[0]).toBe(ARIES);
          expect(prog[1]).toBe(TAURUS);
          expect(prog[11]).toBe(PISCES);
      });
      
      it('should determine reverse progression if 9th house from Seed is Even Footed', () => {
          // Asc = Cancer. 9th = Pisces.
          // Pisces is Even Footed?
          // Even Footed Signs: Cn, Le, Vi, Cp, Aq, Pi. Yes.
          // Progression Reverse: Cancer, Gemini, Taurus...
          
          const prog = getCharaDhasaProgression(CANCER);
          expect(prog[0]).toBe(CANCER);
          expect(prog[1]).toBe(GEMINI);
          expect(prog[2]).toBe(TAURUS);
      });
  });

});
