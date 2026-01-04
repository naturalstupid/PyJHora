import { describe, expect, it } from 'vitest';
import { AQUARIUS, ARIES, CAPRICORN, GEMINI, LEO, LIBRA, PISCES, SAGITTARIUS, SCORPIO, SUN, TAURUS, VIRGO } from '../../../src/core/constants';
import { getDivisionalChart, PlanetPosition } from '../../../src/core/horoscope/charts';
import {
    calculateD1_Rasi,
    calculateD30_Trimsamsa_Parashara,
    calculateD3_Drekkana_Parashara,
    calculateD9_Navamsa_Parashara
} from '../../../src/core/horoscope/varga-utils';

describe('Divisional Chart Calculations', () => {
  const ONE_DEGREE = 1;
  const HALF_DEGREE = 0.5;

  describe('D-1 Rasi', () => {
    it('should calculate correct rasi for 0-30 degrees', () => {
      expect(calculateD1_Rasi(15)).toBe(ARIES); // 15 deg
      expect(calculateD1_Rasi(45)).toBe(TAURUS); // 45 deg
      expect(calculateD1_Rasi(359)).toBe(PISCES); // 359 deg
    });
  });

  describe('D-9 Navamsa (Parashara)', () => {
    // Navamsa span is 3°20' (3.333 degrees)
    // 1st Navamsa: 0 - 3.33
    // 2nd Navamsa: 3.33 - 6.66
    // ...
    // 8th Navamsa: 23.33 - 26.66

    it('should calculate Navamsa for Movable Sign (Aries)', () => {
      // Aries is Movable. Count from Aries.
      const posAries8thPart = 25.5; // 8th Navamsa (23.20 to 26.40) -> Scorpio
      // 0->Aries, ... 7->Scorpio
      expect(calculateD9_Navamsa_Parashara(posAries8thPart)).toBe(SCORPIO);
      
      const posAries1stPart = 1; // 1st Navamsa -> Aries
      expect(calculateD9_Navamsa_Parashara(posAries1stPart)).toBe(ARIES);
    });

    it('should calculate Navamsa for Fixed Sign (Taurus)', () => {
      // Taurus is Fixed. Count from 9th from Taurus (Capricorn).
      // 0-3.33 (1st part) -> Capricorn
      const posTaurus1stPart = 30 + 1; // 31 deg
      expect(calculateD9_Navamsa_Parashara(posTaurus1stPart)).toBe(CAPRICORN);
    });

    it('should calculate Navamsa for Dual Sign (Gemini)', () => {
      // Gemini is Dual. Count from 5th from Gemini (Libra).
      // 0-3.33 (1st part) -> Libra
      const posGemini1stPart = 60 + 1; // 61 deg
      expect(calculateD9_Navamsa_Parashara(posGemini1stPart)).toBe(LIBRA);
    });
  });

  describe('D-3 Drekkana (Parashara)', () => {
    // 0-10, 10-20, 20-30
    
    it('should calculate Drekkana for Aries', () => {
      // 1st part -> Aries
      expect(calculateD3_Drekkana_Parashara(5)).toBe(ARIES);
      // 2nd part -> Leo (5th)
      expect(calculateD3_Drekkana_Parashara(15)).toBe(LEO);
      // 3rd part -> Sagittarius (9th)
      expect(calculateD3_Drekkana_Parashara(25)).toBe(SAGITTARIUS);
    });
  });

  describe('D-30 Trimsamsa (Parashara)', () => {
    it('should calculate Trimsamsa for Odd Sign (Aries)', () => {
      // 0-5: Mars (Aries)
      expect(calculateD30_Trimsamsa_Parashara(2)).toBe(ARIES);
      // 5-10: Saturn (Aquarius)
      expect(calculateD30_Trimsamsa_Parashara(7)).toBe(AQUARIUS);
      // 10-18: Jupiter (Sagittarius)
      expect(calculateD30_Trimsamsa_Parashara(15)).toBe(SAGITTARIUS);
      // 18-25: Mercury (Gemini)
      expect(calculateD30_Trimsamsa_Parashara(20)).toBe(GEMINI);
      // 25-30: Venus (Libra)
      expect(calculateD30_Trimsamsa_Parashara(28)).toBe(LIBRA);
    });

    it('should calculate Trimsamsa for Even Sign (Taurus)', () => {
      // 0-5: Venus (Taurus)
      const taurusBase = 30;
      expect(calculateD30_Trimsamsa_Parashara(taurusBase + 2)).toBe(TAURUS);
      // 5-12: Mercury (Virgo)
      expect(calculateD30_Trimsamsa_Parashara(taurusBase + 7)).toBe(VIRGO);
      // 12-20: Jupiter (Pisces)
      expect(calculateD30_Trimsamsa_Parashara(taurusBase + 15)).toBe(PISCES);
      // 20-25: Saturn (Capricorn)
      expect(calculateD30_Trimsamsa_Parashara(taurusBase + 22)).toBe(CAPRICORN);
      // 25-30: Mars (Scorpio)
      expect(calculateD30_Trimsamsa_Parashara(taurusBase + 28)).toBe(SCORPIO);
    });
  });

  describe('getDivisionalChart Integration', () => {
    it('should transform planet positions correctly', () => {
      const d1Positions: PlanetPosition[] = [
        { planet: SUN, rasi: ARIES, longitude: 15 } // 15 deg Aries -> D3 Leo
      ];
      
      const d3Positions = getDivisionalChart(d1Positions, 3);
      
      expect(d3Positions[0].rasi).toBe(LEO);
      expect(d3Positions[0].planet).toBe(SUN);
      // Longitude check: (15 * 3) % 30 = 45 % 30 = 15
      expect(d3Positions[0].longitude).toBe(15);
    });
  });
});
