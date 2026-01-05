import { describe, expect, it } from 'vitest';
import { AQUARIUS, ARIES, CANCER, CAPRICORN, GEMINI, LEO, LIBRA, PISCES, SAGITTARIUS, SCORPIO, SUN, TAURUS, VIRGO } from '../../../src/core/constants';
import { getDivisionalChart, PlanetPosition } from '../../../src/core/horoscope/charts';
import {
  calculateD10_Dasamsa_Parashara,
  calculateD12_Dwadasamsa_Parashara,
  calculateD16_Shodasamsa_Parashara,
  calculateD1_Rasi,
  calculateD20_Vimsamsa_Parashara,
  calculateD24_Chaturvimsamsa_Parashara,
  calculateD27_Bhamsa_Parashara,
  calculateD2_Hora_Parashara,
  calculateD30_Trimsamsa_Parashara,
  calculateD3_Drekkana_Parashara,
  calculateD40_Khavedamsa_Parashara,
  calculateD45_Akshavedamsa_Parashara,
  calculateD4_Chaturthamsa_Parashara,
  calculateD60_Shashtiamsa_Parashara,
  calculateD7_Saptamsa_Parashara,
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

  describe('D-2 Hora (Parashara)', () => {
    // Odd signs: 1st half -> Sun (Leo), 2nd half -> Moon (Cancer)
    // Even signs: 1st half -> Moon (Cancer), 2nd half -> Sun (Leo)

    it('should calculate Hora for Odd Sign (Aries)', () => {
      // 1st half (0-15) -> Leo
      expect(calculateD2_Hora_Parashara(10)).toBe(LEO);
      // 2nd half (15-30) -> Cancer
      expect(calculateD2_Hora_Parashara(20)).toBe(CANCER);
    });

    it('should calculate Hora for Even Sign (Taurus)', () => {
      const taurusBase = 30;
      // 1st half (0-15) -> Cancer
      expect(calculateD2_Hora_Parashara(taurusBase + 10)).toBe(CANCER);
      // 2nd half (15-30) -> Leo
      expect(calculateD2_Hora_Parashara(taurusBase + 20)).toBe(LEO);
    });
  });

  describe('D-4 Chaturthamsa (Parashara)', () => {
    // 1, 4, 7, 10
    it('should calculate Chaturthamsa', () => {
      // Aries (Odd): 0-7.5 -> Aries
      expect(calculateD4_Chaturthamsa_Parashara(5)).toBe(ARIES);
      // 7.5-15 -> 4th (Cancer)
      expect(calculateD4_Chaturthamsa_Parashara(10)).toBe(CANCER); // Cancer is 3
    });
  });

  describe('D-7 Saptamsa (Parashara)', () => {
    it('should calculate Saptamsa for Odd Sign (Aries)', () => {
      // Count from sign itself (Aries)
      // 1st 7th-part (0 - 4.28) -> Aries
      expect(calculateD7_Saptamsa_Parashara(1)).toBe(ARIES);
    });

    it('should calculate Saptamsa for Even Sign (Taurus)', () => {
      // Count from 7th from sign (Scorpio)
      const taurusBase = 30;
      // 1st 7th-part -> Scorpio
      expect(calculateD7_Saptamsa_Parashara(taurusBase + 1)).toBe(SCORPIO);
    });
  });

  describe('D-10 Dasamsa (Parashara)', () => {
    it('should calculate Dasamsa for Odd Sign (Aries)', () => {
      // Count from sign itself
      expect(calculateD10_Dasamsa_Parashara(1)).toBe(ARIES);
    });

    it('should calculate Dasamsa for Even Sign (Taurus)', () => {
      // Count from 9th from sign (Capricorn)
      const taurusBase = 30;
      expect(calculateD10_Dasamsa_Parashara(taurusBase + 1)).toBe(CAPRICORN);
    });
  });

  describe('D-12 Dwadasamsa (Parashara)', () => {
    it('should count from sign itself cyclically', () => {
      // Aries: 1st part -> Aries
      expect(calculateD12_Dwadasamsa_Parashara(1)).toBe(ARIES);
      // Aries: 2nd part -> Taurus
      expect(calculateD12_Dwadasamsa_Parashara(3)).toBe(TAURUS);
    });
  });

  describe('D-16 Shodasamsa (Parashara)', () => {
    it('should calculate for Movable Sign (Aries)', () => {
      // Start from Aries
      expect(calculateD16_Shodasamsa_Parashara(1)).toBe(ARIES);
    });
    it('should calculate for Fixed Sign (Leo)', () => {
      const leoBase = 120;
      // Start from Leo
      expect(calculateD16_Shodasamsa_Parashara(leoBase + 0.5)).toBe(LEO);
    });
    it('should calculate for Dual Sign (Sagittarius)', () => {
      const sagBase = 240;
      // Start from Sagittarius
      expect(calculateD16_Shodasamsa_Parashara(sagBase + 0.5)).toBe(SAGITTARIUS);
    });
  });

  describe('D-20 Vimsamsa (Parashara)', () => {
    it('should calculate for Movable Sign (Aries)', () => {
      // Start from Aries
      expect(calculateD20_Vimsamsa_Parashara(0.5)).toBe(ARIES);
    });
    it('should calculate for Fixed Sign (Leo)', () => {
      // Start from Sagittarius
      const leoBase = 120;
      expect(calculateD20_Vimsamsa_Parashara(leoBase + 0.5)).toBe(SAGITTARIUS);
    });
    it('should calculate for Dual Sign (Sagittarius)', () => {
      // Start from Leo
      const sagBase = 240;
      expect(calculateD20_Vimsamsa_Parashara(sagBase + 0.5)).toBe(LEO);
    });
  });

  describe('D-24 Chaturvimsamsa (Parashara)', () => {
    it('should calculate D-24 for Odd Sign', () => {
      // Start from Leo
      expect(calculateD24_Chaturvimsamsa_Parashara(0.5)).toBe(LEO);
    });
    it('should calculate D-24 for Even Sign', () => {
      const taurusBase = 30;
      // Start from Cancer
      expect(calculateD24_Chaturvimsamsa_Parashara(taurusBase + 0.5)).toBe(Number(3)); // Cancer
    });
  });

  describe('D-27 Bhamsa (Parashara)', () => {
    it('should calculate D-27 for Fiery Sign (Aries)', () => {
      // Start from Aries
      expect(calculateD27_Bhamsa_Parashara(0.5)).toBe(ARIES);
    });
    it('should calculate D-27 for Earthy Sign (Taurus)', () => {
      // Start from Cancer
      const taurusBase = 30;
      expect(calculateD27_Bhamsa_Parashara(taurusBase + 0.5)).toBe(Number(3)); // Cancer
    });
  });

  describe('D-40 Khavedamsa (Parashara)', () => {
    it('should calculate D-40', () => {
      // Odd -> Aries
      expect(calculateD40_Khavedamsa_Parashara(0.1)).toBe(ARIES);
      // Even -> Libra
      expect(calculateD40_Khavedamsa_Parashara(30.1)).toBe(LIBRA);
    });
  });

  describe('D-45 Akshavedamsa (Parashara)', () => {
    it('should calculate D-45', () => {
      // Movable -> Aries
      expect(calculateD45_Akshavedamsa_Parashara(0.1)).toBe(ARIES);
      // Fixed -> Leo
      expect(calculateD45_Akshavedamsa_Parashara(120.1)).toBe(LEO);
      // Dual -> Sagittarius
      expect(calculateD45_Akshavedamsa_Parashara(240.1)).toBe(SAGITTARIUS);
    });
  });

  describe('D-60 Shashtiamsa (Parashara)', () => {
    it('should calculate D-60', () => {
      // Count from sign itself: (Sign + Part) % 12
      // Aries (0), Part 0 -> 0
      expect(calculateD60_Shashtiamsa_Parashara(0.1)).toBe(ARIES);
      // Aries (0), Part 1 -> 1
      expect(calculateD60_Shashtiamsa_Parashara(0.6)).toBe(TAURUS);
    });
  });

  describe('getDivisionalChart Integration', () => {
    it('should transform planet positions correctly', () => {
      const d1Positions: PlanetPosition[] = [
        { planet: SUN, rasi: ARIES, longitude: 15 } // 15 deg Aries -> D3 Leo
      ];
      
      const d3Positions = getDivisionalChart(d1Positions, 3);
      
      expect(d3Positions[0]!.rasi).toBe(LEO);
      expect(d3Positions[0]!.planet).toBe(SUN);
      // Longitude check: (15 * 3) % 30 = 45 % 30 = 15
      expect(d3Positions[0]!.longitude).toBe(15);
    });
  });
});
