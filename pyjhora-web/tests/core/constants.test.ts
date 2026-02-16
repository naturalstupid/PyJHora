/**
 * Tests for core constants - rasi classifications and sign groupings
 * Verifies that the constant arrays match the Vedic astrological definitions
 */

import { describe, expect, it } from 'vitest';
import {
  ARIES, TAURUS, GEMINI, CANCER, LEO, VIRGO,
  LIBRA, SCORPIO, SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES,
  ODD_SIGNS, EVEN_SIGNS,
  MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS,
  FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS,
  ODD_FOOTED_SIGNS, EVEN_FOOTED_SIGNS,
  SIGN_LORDS,
  SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN,
  KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, UPACHAYA_HOUSES, MARAKA_HOUSES,
  VARSHA_VIMSOTTARI_DAYS, VARSHA_VIMSOTTARI_ADHIPATI_LIST, HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI,
  PINDAYU_FULL_LONGEVITY, NISARGAYU_FULL_LONGEVITY,
  PLANET_DEEP_EXALTATION_LONGITUDES, PLANET_DEEP_DEBILITATION_LONGITUDES,
  IL_FACTORS,
} from '@core/constants';

describe('Rasi (Sign) Classification Constants', () => {
  describe('ODD_SIGNS and EVEN_SIGNS', () => {
    it('should contain exactly 6 signs each', () => {
      expect(ODD_SIGNS).toHaveLength(6);
      expect(EVEN_SIGNS).toHaveLength(6);
    });

    it('ODD_SIGNS should be Aries, Gemini, Leo, Libra, Sagittarius, Aquarius', () => {
      expect(ODD_SIGNS).toEqual([ARIES, GEMINI, LEO, LIBRA, SAGITTARIUS, AQUARIUS]);
    });

    it('EVEN_SIGNS should be Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces', () => {
      expect(EVEN_SIGNS).toEqual([TAURUS, CANCER, VIRGO, SCORPIO, CAPRICORN, PISCES]);
    });

    it('should be mutually exclusive and cover all 12 signs', () => {
      const all = [...ODD_SIGNS, ...EVEN_SIGNS].sort((a, b) => a - b);
      expect(all).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    });

    it('should have no overlap between ODD and EVEN', () => {
      const overlap = ODD_SIGNS.filter(s => EVEN_SIGNS.includes(s));
      expect(overlap).toHaveLength(0);
    });
  });

  describe('MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS (Quality)', () => {
    it('should contain exactly 4 signs each', () => {
      expect(MOVABLE_SIGNS).toHaveLength(4);
      expect(FIXED_SIGNS).toHaveLength(4);
      expect(DUAL_SIGNS).toHaveLength(4);
    });

    it('MOVABLE_SIGNS should be Aries, Cancer, Libra, Capricorn (Chara)', () => {
      expect(MOVABLE_SIGNS).toEqual([ARIES, CANCER, LIBRA, CAPRICORN]);
    });

    it('FIXED_SIGNS should be Taurus, Leo, Scorpio, Aquarius (Sthira)', () => {
      expect(FIXED_SIGNS).toEqual([TAURUS, LEO, SCORPIO, AQUARIUS]);
    });

    it('DUAL_SIGNS should be Gemini, Virgo, Sagittarius, Pisces (Dwiswabhava)', () => {
      expect(DUAL_SIGNS).toEqual([GEMINI, VIRGO, SAGITTARIUS, PISCES]);
    });

    it('should be mutually exclusive and cover all 12 signs', () => {
      const all = [...MOVABLE_SIGNS, ...FIXED_SIGNS, ...DUAL_SIGNS].sort((a, b) => a - b);
      expect(all).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    });

    it('should have no overlap between quality groups', () => {
      const mf = MOVABLE_SIGNS.filter(s => FIXED_SIGNS.includes(s));
      const md = MOVABLE_SIGNS.filter(s => DUAL_SIGNS.includes(s));
      const fd = FIXED_SIGNS.filter(s => DUAL_SIGNS.includes(s));
      expect(mf).toHaveLength(0);
      expect(md).toHaveLength(0);
      expect(fd).toHaveLength(0);
    });
  });

  describe('FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS (Element)', () => {
    it('should contain exactly 3 signs each', () => {
      expect(FIRE_SIGNS).toHaveLength(3);
      expect(EARTH_SIGNS).toHaveLength(3);
      expect(AIR_SIGNS).toHaveLength(3);
      expect(WATER_SIGNS).toHaveLength(3);
    });

    it('FIRE_SIGNS should be Aries, Leo, Sagittarius', () => {
      expect(FIRE_SIGNS).toEqual([ARIES, LEO, SAGITTARIUS]);
    });

    it('EARTH_SIGNS should be Taurus, Virgo, Capricorn', () => {
      expect(EARTH_SIGNS).toEqual([TAURUS, VIRGO, CAPRICORN]);
    });

    it('AIR_SIGNS should be Gemini, Libra, Aquarius', () => {
      expect(AIR_SIGNS).toEqual([GEMINI, LIBRA, AQUARIUS]);
    });

    it('WATER_SIGNS should be Cancer, Scorpio, Pisces', () => {
      expect(WATER_SIGNS).toEqual([CANCER, SCORPIO, PISCES]);
    });

    it('should be mutually exclusive and cover all 12 signs', () => {
      const all = [...FIRE_SIGNS, ...EARTH_SIGNS, ...AIR_SIGNS, ...WATER_SIGNS].sort((a, b) => a - b);
      expect(all).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    });

    it('should have no overlap between element groups', () => {
      const elements = [FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS];
      for (let i = 0; i < elements.length; i++) {
        for (let j = i + 1; j < elements.length; j++) {
          const overlap = elements[i]!.filter(s => elements[j]!.includes(s));
          expect(overlap).toHaveLength(0);
        }
      }
    });

    it('element should follow 4-sign cycle (Fire, Earth, Air, Water)', () => {
      for (let i = 0; i < 12; i++) {
        const element = i % 4;
        if (element === 0) expect(FIRE_SIGNS).toContain(i);
        if (element === 1) expect(EARTH_SIGNS).toContain(i);
        if (element === 2) expect(AIR_SIGNS).toContain(i);
        if (element === 3) expect(WATER_SIGNS).toContain(i);
      }
    });
  });

  describe('ODD_FOOTED_SIGNS and EVEN_FOOTED_SIGNS', () => {
    it('should contain exactly 6 signs each', () => {
      expect(ODD_FOOTED_SIGNS).toHaveLength(6);
      expect(EVEN_FOOTED_SIGNS).toHaveLength(6);
    });

    it('ODD_FOOTED should be Aries-Gemini and Libra-Sagittarius', () => {
      expect(ODD_FOOTED_SIGNS).toEqual([ARIES, TAURUS, GEMINI, LIBRA, SCORPIO, SAGITTARIUS]);
    });

    it('EVEN_FOOTED should be Cancer-Virgo and Capricorn-Pisces', () => {
      expect(EVEN_FOOTED_SIGNS).toEqual([CANCER, LEO, VIRGO, CAPRICORN, AQUARIUS, PISCES]);
    });

    it('should be mutually exclusive and cover all 12 signs', () => {
      const all = [...ODD_FOOTED_SIGNS, ...EVEN_FOOTED_SIGNS].sort((a, b) => a - b);
      expect(all).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    });
  });

  describe('SIGN_LORDS', () => {
    it('should have 12 entries (one per sign)', () => {
      expect(SIGN_LORDS).toHaveLength(12);
    });

    it('Aries lord should be Mars', () => {
      expect(SIGN_LORDS[ARIES]).toBe(MARS);
    });

    it('Taurus lord should be Venus', () => {
      expect(SIGN_LORDS[TAURUS]).toBe(VENUS);
    });

    it('Gemini lord should be Mercury', () => {
      expect(SIGN_LORDS[GEMINI]).toBe(MERCURY);
    });

    it('Cancer lord should be Moon', () => {
      expect(SIGN_LORDS[CANCER]).toBe(MOON);
    });

    it('Leo lord should be Sun', () => {
      expect(SIGN_LORDS[LEO]).toBe(SUN);
    });

    it('Virgo lord should be Mercury', () => {
      expect(SIGN_LORDS[VIRGO]).toBe(MERCURY);
    });

    it('Libra lord should be Venus', () => {
      expect(SIGN_LORDS[LIBRA]).toBe(VENUS);
    });

    it('Scorpio lord should be Mars', () => {
      expect(SIGN_LORDS[SCORPIO]).toBe(MARS);
    });

    it('Sagittarius lord should be Jupiter', () => {
      expect(SIGN_LORDS[SAGITTARIUS]).toBe(JUPITER);
    });

    it('Capricorn lord should be Saturn', () => {
      expect(SIGN_LORDS[CAPRICORN]).toBe(SATURN);
    });

    it('Aquarius lord should be Saturn', () => {
      expect(SIGN_LORDS[AQUARIUS]).toBe(SATURN);
    });

    it('Pisces lord should be Jupiter', () => {
      expect(SIGN_LORDS[PISCES]).toBe(JUPITER);
    });
  });
});

describe('House Classification Constants', () => {
  describe('KENDRA_HOUSES', () => {
    it('should be houses 1, 4, 7, 10 (0-indexed: 0, 3, 6, 9)', () => {
      expect(KENDRA_HOUSES).toEqual([0, 3, 6, 9]);
    });
  });

  describe('TRIKONA_HOUSES', () => {
    it('should be houses 1, 5, 9 (0-indexed: 0, 4, 8)', () => {
      expect(TRIKONA_HOUSES).toEqual([0, 4, 8]);
    });
  });

  describe('DUSTHANA_HOUSES', () => {
    it('should be houses 6, 8, 12 (0-indexed: 5, 7, 11)', () => {
      expect(DUSTHANA_HOUSES).toEqual([5, 7, 11]);
    });
  });

  describe('UPACHAYA_HOUSES', () => {
    it('should be houses 3, 6, 10, 11 (0-indexed: 2, 5, 9, 10)', () => {
      expect(UPACHAYA_HOUSES).toEqual([2, 5, 9, 10]);
    });
  });

  describe('MARAKA_HOUSES', () => {
    it('should be houses 2, 7 (0-indexed: 1, 6)', () => {
      expect(MARAKA_HOUSES).toEqual([1, 6]);
    });
  });
});

describe('Varsha (Annual) Vimsottari Constants', () => {
  it('VARSHA_VIMSOTTARI_DAYS should have 9 planet entries summing to 360', () => {
    const keys = Object.keys(VARSHA_VIMSOTTARI_DAYS);
    expect(keys).toHaveLength(9);
    const total = Object.values(VARSHA_VIMSOTTARI_DAYS).reduce((a, b) => a + b, 0);
    expect(total).toBe(HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI);
  });

  it('VARSHA_VIMSOTTARI_ADHIPATI_LIST should have 9 entries covering all 9 planets', () => {
    expect(VARSHA_VIMSOTTARI_ADHIPATI_LIST).toHaveLength(9);
    const sorted = [...VARSHA_VIMSOTTARI_ADHIPATI_LIST].sort((a, b) => a - b);
    expect(sorted).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it('HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI should be 360 days', () => {
    expect(HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI).toBe(360);
  });
});

describe('Longevity (Aayu) Constants', () => {
  it('PINDAYU_FULL_LONGEVITY should have 7 entries (Sun to Saturn)', () => {
    expect(PINDAYU_FULL_LONGEVITY).toHaveLength(7);
    expect(PINDAYU_FULL_LONGEVITY).toEqual([19, 25, 15, 12, 15, 21, 20]);
  });

  it('NISARGAYU_FULL_LONGEVITY should have 7 entries (Sun to Saturn)', () => {
    expect(NISARGAYU_FULL_LONGEVITY).toHaveLength(7);
    expect(NISARGAYU_FULL_LONGEVITY).toEqual([20, 1, 2, 9, 18, 20, 50]);
  });

  it('Deep exaltation longitudes should have 7 entries in 0-360 range', () => {
    expect(PLANET_DEEP_EXALTATION_LONGITUDES).toHaveLength(7);
    for (const lon of PLANET_DEEP_EXALTATION_LONGITUDES) {
      expect(lon).toBeGreaterThanOrEqual(0);
      expect(lon).toBeLessThan(360);
    }
  });

  it('Deep debilitation = (exaltation + 180) % 360', () => {
    expect(PLANET_DEEP_DEBILITATION_LONGITUDES).toHaveLength(7);
    for (let i = 0; i < 7; i++) {
      expect(PLANET_DEEP_DEBILITATION_LONGITUDES[i]).toBeCloseTo(
        (PLANET_DEEP_EXALTATION_LONGITUDES[i]! + 180) % 360, 5
      );
    }
  });
});

describe('Indu Lagna Constants', () => {
  it('IL_FACTORS should have 7 entries (Sun to Saturn)', () => {
    expect(IL_FACTORS).toHaveLength(7);
    expect(IL_FACTORS).toEqual([30, 16, 6, 8, 10, 12, 1]);
  });
});
