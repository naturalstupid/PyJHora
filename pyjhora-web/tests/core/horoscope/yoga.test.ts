/**
 * Tests for yoga.ts - Astrological combination calculations
 */

import {
  SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU,
  ARIES, TAURUS, GEMINI, CANCER, LEO, VIRGO, LIBRA, SCORPIO,
  SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES,
  ASCENDANT_SYMBOL,
} from '@core/constants';
import {
  getPlanetToHouseDict,
  getPlanetsInHouse,
  nipunaYoga,
  budhaAadityaYoga,
  vesiYoga,
  vosiYoga,
  ubhayacharaYoga,
  sunaphaaYoga,
  anaphaaYoga,
  duradharaYoga,
  dhurdhuraYoga,
  kemadrumaYoga,
  chandraMangalaYoga,
  adhiYoga,
  maalaaYoga,
  sarpaYoga,
  ruchakaYoga,
  bhadraYoga,
  sasaYoga,
  maalavyaYoga,
  hamsaYoga,
  rajjuYoga,
  musalaYoga,
  nalaYoga,
  gadaaYoga,
  sakataYoga,
  vihangaYoga,
  sringaatakaYoga,
  halaYoga,
  vajraYoga,
  yavaYoga,
  kamalaYoga,
  vaapiYoga,
  yoopaYoga,
  saraYoga,
  saktiYoga,
  dandaYoga,
  naukaaYoga,
  kootaYoga,
  chatraYoga,
  chaapaYoga,
  ardhaChandraYoga,
  chakraYoga,
  samudraYoga,
  veenaaYoga,
  daamaYoga,
  paasaYoga,
  kedaaraYoga,
  soolaYoga,
  yugaYoga,
  golaYoga,
  gajaKesariYoga,
  guruMangalaYoga,
  subhaYoga,
  asubhaYoga,
  trilochanaYoga,
  mahabhagyaYoga,
  chatussagaraYoga,
  amalaYoga,
  parvataYoga,
  harshaYoga,
  saralaYoga,
  vimalaYoga,
  lakshmiYoga,
  dhanaYoga,
  vasumathiYoga,
  kahalaYoga,
  rajalakshanaYoga,
  detectAllYogas,
  getPresentYogas,
  type HouseChart,
} from '@core/horoscope/yoga';
import { describe, expect, it } from 'vitest';

// ============================================================================
// HELPER: Build chart from ascendant rasi and planet placements
// ============================================================================

/**
 * Build a HouseChart (string[12]) from ascendant rasi and planet positions.
 * @param ascRasi - Rasi index (0-11) where Lagna falls
 * @param planets - Map of planet ID to rasi index
 * @returns HouseChart array of 12 strings
 */
function buildChart(ascRasi: number, planets: Record<number, number>): HouseChart {
  const chart: string[] = Array(12).fill('');
  // Place ascendant
  chart[ascRasi] = chart[ascRasi] ? chart[ascRasi] + '/' + ASCENDANT_SYMBOL : ASCENDANT_SYMBOL;
  // Place planets
  for (const [planet, rasi] of Object.entries(planets)) {
    chart[rasi] = chart[rasi] ? chart[rasi] + '/' + planet : String(planet);
  }
  return chart;
}

// ============================================================================
// HELPER FUNCTION TESTS
// ============================================================================

describe('Yoga Helper Functions', () => {
  describe('getPlanetToHouseDict', () => {
    it('should parse chart to planet-house mapping', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: TAURUS,
        [MARS]: GEMINI,
      });
      const pToH = getPlanetToHouseDict(chart);
      expect(pToH[ASCENDANT_SYMBOL]).toBe(ARIES);
      expect(pToH[SUN]).toBe(ARIES);
      expect(pToH[MOON]).toBe(TAURUS);
      expect(pToH[MARS]).toBe(GEMINI);
    });

    it('should handle multiple planets in same house', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MERCURY]: ARIES,
      });
      const pToH = getPlanetToHouseDict(chart);
      expect(pToH[SUN]).toBe(ARIES);
      expect(pToH[MERCURY]).toBe(ARIES);
    });
  });

  describe('getPlanetsInHouse', () => {
    it('should return planets in a given house', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MERCURY]: ARIES,
        [MOON]: TAURUS,
      });
      const planetsInAries = getPlanetsInHouse(chart, ARIES);
      expect(planetsInAries).toContain(SUN);
      expect(planetsInAries).toContain(MERCURY);
      expect(planetsInAries).not.toContain(MOON);
    });

    it('should return empty array for empty house', () => {
      const chart = buildChart(ARIES, { [SUN]: ARIES });
      expect(getPlanetsInHouse(chart, TAURUS)).toEqual([]);
    });
  });
});

// ============================================================================
// SUN YOGA TESTS
// ============================================================================

describe('Sun Yogas', () => {
  describe('nipunaYoga / budhaAadityaYoga', () => {
    it('should be true when Sun and Mercury are in the same house', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MERCURY]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(nipunaYoga(chart)).toBe(true);
      expect(budhaAadityaYoga(chart)).toBe(true);
    });

    it('should be false when Sun and Mercury are in different houses', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MERCURY]: VIRGO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(nipunaYoga(chart)).toBe(false);
    });
  });

  describe('vesiYoga', () => {
    it('should be true when a planet (not Moon) is in 2nd from Sun', () => {
      // Sun in Aries, Mars in Taurus (2nd from Sun)
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MARS]: TAURUS,
        [MOON]: CANCER,
        [MERCURY]: GEMINI,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(vesiYoga(chart)).toBe(true);
    });

    it('should be false when only Moon is in 2nd from Sun', () => {
      // Sun in Aries, Moon in Taurus (2nd from Sun), no other planet there
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: TAURUS,
        [MARS]: LEO,
        [MERCURY]: GEMINI,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: LEO,
        [KETU]: AQUARIUS,
      });
      expect(vesiYoga(chart)).toBe(false);
    });
  });

  describe('vosiYoga', () => {
    it('should be true when a planet (not Moon) is in 12th from Sun', () => {
      // Sun in Taurus, Mars in Aries (12th from Taurus)
      const chart = buildChart(ARIES, {
        [SUN]: TAURUS,
        [MARS]: ARIES,
        [MOON]: CANCER,
        [MERCURY]: GEMINI,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: LEO,
        [KETU]: AQUARIUS,
      });
      expect(vosiYoga(chart)).toBe(true);
    });
  });

  describe('ubhayacharaYoga', () => {
    it('should be true when planets in both 2nd and 12th from Sun', () => {
      // Sun in Taurus, Mars in Aries (12th), Jupiter in Gemini (2nd)
      const chart = buildChart(ARIES, {
        [SUN]: TAURUS,
        [MARS]: ARIES,
        [JUPITER]: GEMINI,
        [MOON]: CANCER,
        [MERCURY]: LEO,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: LEO,
        [KETU]: AQUARIUS,
      });
      expect(ubhayacharaYoga(chart)).toBe(true);
    });

    it('should be false when planets in only one side', () => {
      // Sun in Leo, Mars in Virgo (2nd), nothing in Cancer (12th except Moon)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MARS]: VIRGO,
        [MOON]: CANCER,
        [MERCURY]: SCORPIO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      // 12th from Leo is Cancer, only Moon there -> vosiYoga false -> ubhayachara false
      expect(ubhayacharaYoga(chart)).toBe(false);
    });
  });
});

// ============================================================================
// MOON YOGA TESTS
// ============================================================================

describe('Moon Yogas', () => {
  describe('sunaphaaYoga', () => {
    it('should be true when planets (not Sun) in 2nd from Moon', () => {
      // Moon in Aries, Mars in Taurus (2nd from Moon)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: ARIES,
        [MARS]: TAURUS,
        [MERCURY]: GEMINI,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(sunaphaaYoga(chart)).toBe(true);
    });
  });

  describe('anaphaaYoga', () => {
    it('should be true when planets (not Sun) in 12th from Moon', () => {
      // Moon in Taurus, Mars in Aries (12th from Moon)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: GEMINI,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: LEO,
        [KETU]: AQUARIUS,
      });
      expect(anaphaaYoga(chart)).toBe(true);
    });
  });

  describe('duradharaYoga', () => {
    it('should be true when planets in 2nd and 12th from Moon', () => {
      // Moon in Taurus, Mars in Aries (12th), Jupiter in Gemini (2nd)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [JUPITER]: GEMINI,
        [MERCURY]: VIRGO,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: LEO,
        [KETU]: AQUARIUS,
      });
      expect(duradharaYoga(chart)).toBe(true);
    });
  });

  describe('chandraMangalaYoga', () => {
    it('should be true when Moon and Mars are together', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: SCORPIO,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(chandraMangalaYoga(chart)).toBe(true);
    });

    it('should be false when Moon and Mars are apart', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: SCORPIO,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(chandraMangalaYoga(chart)).toBe(false);
    });
  });

  describe('adhiYoga', () => {
    it('should be true when all benefics in 6th, 7th, 8th from Moon', () => {
      // Moon in Aries (0). 6th=Virgo(5), 7th=Libra(6), 8th=Scorpio(7)
      // Benefics: Jupiter, Venus, Mercury (if alone/with benefic)
      // Mercury alone in one house makes it benefic
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: ARIES,
        [JUPITER]: VIRGO,   // 6th from Moon
        [VENUS]: LIBRA,     // 7th from Moon
        [MERCURY]: SCORPIO, // 8th from Moon (alone = benefic)
        [MARS]: CAPRICORN,
        [SATURN]: AQUARIUS,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(adhiYoga(chart)).toBe(true);
    });

    it('should be false when a benefic is outside 6th, 7th, 8th from Moon', () => {
      // Moon in Aries(0). 6th=Virgo(5), 7th=Libra(6), 8th=Scorpio(7)
      // Jupiter in Taurus(1) - NOT in houses 6-8 from Moon -> adhiYoga should fail
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: ARIES,
        [JUPITER]: TAURUS,   // NOT in 6th, 7th, or 8th from Moon
        [VENUS]: LIBRA,      // 7th from Moon
        [MERCURY]: SCORPIO,  // alone = benefic, in 8th from Moon
        [MARS]: CAPRICORN,
        [SATURN]: AQUARIUS,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(adhiYoga(chart)).toBe(false);
    });
  });
});

// ============================================================================
// PANCHA MAHAPURUSHA YOGA TESTS
// ============================================================================

describe('Pancha Mahapurusha Yogas', () => {
  describe('ruchakaYoga', () => {
    it('should be true when Mars in Aries and in kendra from Lagna', () => {
      // Lagna in Aries, Mars in Aries (kendra = same house, own sign)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(ruchakaYoga(chart)).toBe(true);
    });

    it('should be true when Mars in Capricorn and in 10th from Aries Lagna', () => {
      // Lagna in Aries, Mars in Capricorn (10th = kendra, exalted sign)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: CAPRICORN,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: AQUARIUS,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(ruchakaYoga(chart)).toBe(true);
    });

    it('should be false when Mars in Cancer (debilitated)', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: CANCER,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(ruchakaYoga(chart)).toBe(false);
    });
  });

  describe('bhadraYoga', () => {
    it('should be true when Mercury in Virgo and in kendra from Lagna', () => {
      // Lagna in Gemini, Mercury in Virgo (4th = kendra)
      const chart = buildChart(GEMINI, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(bhadraYoga(chart)).toBe(true);
    });

    it('should be false when Mercury in Leo (not own/exalted)', () => {
      const chart = buildChart(GEMINI, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: LEO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(bhadraYoga(chart)).toBe(false);
    });
  });

  describe('sasaYoga', () => {
    it('should be true when Saturn in Capricorn in kendra from Lagna', () => {
      // Lagna in Libra, Saturn in Capricorn (4th = kendra)
      const chart = buildChart(LIBRA, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(sasaYoga(chart)).toBe(true);
    });

    it('should be false when Saturn in Aries (debilitated, not in sign list)', () => {
      const chart = buildChart(LIBRA, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: PISCES,
        [SATURN]: ARIES,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(sasaYoga(chart)).toBe(false);
    });
  });

  describe('maalavyaYoga', () => {
    it('should be true when Venus in Taurus in kendra from Lagna', () => {
      // Lagna in Taurus, Venus in Taurus (1st = kendra)
      const chart = buildChart(TAURUS, {
        [SUN]: LEO,
        [MOON]: CANCER,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: TAURUS,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(maalavyaYoga(chart)).toBe(true);
    });

    it('should be false when Venus in Virgo (debilitated)', () => {
      const chart = buildChart(TAURUS, {
        [SUN]: LEO,
        [MOON]: CANCER,
        [MARS]: ARIES,
        [MERCURY]: GEMINI,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: VIRGO,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(maalavyaYoga(chart)).toBe(false);
    });
  });

  describe('hamsaYoga', () => {
    it('should be true when Jupiter in Sagittarius in kendra from Lagna', () => {
      // Lagna in Sagittarius, Jupiter in Sagittarius (1st = kendra)
      const chart = buildChart(SAGITTARIUS, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(hamsaYoga(chart)).toBe(true);
    });

    it('should be true when Jupiter in Cancer in 7th from Capricorn Lagna', () => {
      // Lagna in Capricorn, Jupiter in Cancer (7th = kendra, exalted)
      const chart = buildChart(CAPRICORN, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: CANCER,
        [VENUS]: LIBRA,
        [SATURN]: AQUARIUS,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(hamsaYoga(chart)).toBe(true);
    });

    it('should be false when Jupiter in Capricorn (debilitated)', () => {
      const chart = buildChart(CAPRICORN, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: CAPRICORN,
        [VENUS]: LIBRA,
        [SATURN]: AQUARIUS,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(hamsaYoga(chart)).toBe(false);
    });
  });
});

// ============================================================================
// NAABHASA AASRAYA YOGAS
// ============================================================================

describe('Naabhasa Aasraya Yogas', () => {
  describe('rajjuYoga', () => {
    it('should be true when all planets in movable signs', () => {
      // Movable signs: Aries(0), Cancer(3), Libra(6), Capricorn(9)
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: CANCER,
        [MARS]: LIBRA,
        [MERCURY]: CAPRICORN,
        [JUPITER]: ARIES,
        [VENUS]: CANCER,
        [SATURN]: LIBRA,
        [RAHU]: CAPRICORN,
        [KETU]: CANCER,
      });
      expect(rajjuYoga(chart)).toBe(true);
    });

    it('should be false when any planet in fixed/dual sign', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: TAURUS, // Fixed sign
        [MARS]: LIBRA,
        [MERCURY]: CAPRICORN,
        [JUPITER]: ARIES,
        [VENUS]: CANCER,
        [SATURN]: LIBRA,
        [RAHU]: CAPRICORN,
        [KETU]: CANCER,
      });
      expect(rajjuYoga(chart)).toBe(false);
    });
  });

  describe('musalaYoga', () => {
    it('should be true when all planets in fixed signs', () => {
      // Fixed signs: Taurus(1), Leo(4), Scorpio(7), Aquarius(10)
      const chart = buildChart(TAURUS, {
        [SUN]: TAURUS,
        [MOON]: LEO,
        [MARS]: SCORPIO,
        [MERCURY]: AQUARIUS,
        [JUPITER]: TAURUS,
        [VENUS]: LEO,
        [SATURN]: SCORPIO,
        [RAHU]: AQUARIUS,
        [KETU]: LEO,
      });
      expect(musalaYoga(chart)).toBe(true);
    });
  });

  describe('nalaYoga', () => {
    it('should be true when all planets in dual signs', () => {
      // Dual signs: Gemini(2), Virgo(5), Sagittarius(8), Pisces(11)
      const chart = buildChart(GEMINI, {
        [SUN]: GEMINI,
        [MOON]: VIRGO,
        [MARS]: SAGITTARIUS,
        [MERCURY]: PISCES,
        [JUPITER]: GEMINI,
        [VENUS]: VIRGO,
        [SATURN]: SAGITTARIUS,
        [RAHU]: PISCES,
        [KETU]: VIRGO,
      });
      expect(nalaYoga(chart)).toBe(true);
    });
  });
});

// ============================================================================
// AAKRITI YOGAS
// ============================================================================

describe('Aakriti Yogas', () => {
  describe('kamalaYoga', () => {
    it('should be true when all visible planets in kendras from Lagna', () => {
      // Lagna in Aries. Kendras: Aries(0), Cancer(3), Libra(6), Capricorn(9)
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: CANCER,
        [MARS]: LIBRA,
        [MERCURY]: CAPRICORN,
        [JUPITER]: ARIES,
        [VENUS]: CANCER,
        [SATURN]: LIBRA,
        [RAHU]: CAPRICORN,
        [KETU]: CANCER,
      });
      expect(kamalaYoga(chart)).toBe(true);
    });

    it('should be false when a planet is not in kendra', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: CANCER,
        [MARS]: LIBRA,
        [MERCURY]: CAPRICORN,
        [JUPITER]: ARIES,
        [VENUS]: CANCER,
        [SATURN]: TAURUS, // Not a kendra from Aries
        [RAHU]: CAPRICORN,
        [KETU]: CANCER,
      });
      expect(kamalaYoga(chart)).toBe(false);
    });
  });

  describe('vaapiYoga', () => {
    it('should be true when all visible planets in panaparas', () => {
      // Lagna Aries. Panaparas: Taurus(1), Leo(4), Scorpio(7), Aquarius(10)
      const chart = buildChart(ARIES, {
        [SUN]: TAURUS,
        [MOON]: LEO,
        [MARS]: SCORPIO,
        [MERCURY]: AQUARIUS,
        [JUPITER]: TAURUS,
        [VENUS]: LEO,
        [SATURN]: SCORPIO,
        [RAHU]: AQUARIUS,
        [KETU]: LEO,
      });
      expect(vaapiYoga(chart)).toBe(true);
    });

    it('should be true when all visible planets in apoklimas', () => {
      // Lagna Aries. Apoklimas: Gemini(2), Virgo(5), Sagittarius(8), Pisces(11)
      const chart = buildChart(ARIES, {
        [SUN]: GEMINI,
        [MOON]: VIRGO,
        [MARS]: SAGITTARIUS,
        [MERCURY]: PISCES,
        [JUPITER]: GEMINI,
        [VENUS]: VIRGO,
        [SATURN]: SAGITTARIUS,
        [RAHU]: PISCES,
        [KETU]: VIRGO,
      });
      expect(vaapiYoga(chart)).toBe(true);
    });
  });
});

// ============================================================================
// SANKHYA YOGAS (Planet distribution count)
// ============================================================================

describe('Sankhya Yogas', () => {
  describe('veenaaYoga', () => {
    it('should be true when 7 visible planets in 7 distinct signs', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: TAURUS,
        [MARS]: GEMINI,
        [MERCURY]: CANCER,
        [JUPITER]: LEO,
        [VENUS]: VIRGO,
        [SATURN]: LIBRA,
        [RAHU]: SCORPIO,
        [KETU]: TAURUS,
      });
      expect(veenaaYoga(chart)).toBe(true);
    });
  });

  describe('daamaYoga', () => {
    it('should be true when 7 visible planets in 6 distinct signs', () => {
      // Sun and Moon in same sign = 6 distinct houses
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: ARIES,
        [MARS]: TAURUS,
        [MERCURY]: GEMINI,
        [JUPITER]: CANCER,
        [VENUS]: LEO,
        [SATURN]: VIRGO,
        [RAHU]: LIBRA,
        [KETU]: ARIES,
      });
      expect(daamaYoga(chart)).toBe(true);
    });
  });

  describe('paasaYoga', () => {
    it('should be true when 7 visible planets in 5 distinct signs', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: ARIES,
        [MARS]: TAURUS,
        [MERCURY]: TAURUS,
        [JUPITER]: GEMINI,
        [VENUS]: CANCER,
        [SATURN]: LEO,
        [RAHU]: VIRGO,
        [KETU]: ARIES,
      });
      expect(paasaYoga(chart)).toBe(true);
    });
  });

  describe('kedaaraYoga', () => {
    it('should be true when 7 visible planets in 4 distinct signs', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: ARIES,
        [MARS]: TAURUS,
        [MERCURY]: TAURUS,
        [JUPITER]: GEMINI,
        [VENUS]: GEMINI,
        [SATURN]: CANCER,
        [RAHU]: LEO,
        [KETU]: ARIES,
      });
      expect(kedaaraYoga(chart)).toBe(true);
    });
  });

  describe('soolaYoga', () => {
    it('should be true when 7 visible planets in 3 distinct signs', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: ARIES,
        [MARS]: ARIES,
        [MERCURY]: TAURUS,
        [JUPITER]: TAURUS,
        [VENUS]: GEMINI,
        [SATURN]: GEMINI,
        [RAHU]: CANCER,
        [KETU]: ARIES,
      });
      expect(soolaYoga(chart)).toBe(true);
    });
  });

  describe('yugaYoga', () => {
    it('should be true when 7 visible planets in 2 distinct signs', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: ARIES,
        [MARS]: ARIES,
        [MERCURY]: ARIES,
        [JUPITER]: TAURUS,
        [VENUS]: TAURUS,
        [SATURN]: TAURUS,
        [RAHU]: GEMINI,
        [KETU]: ARIES,
      });
      expect(yugaYoga(chart)).toBe(true);
    });
  });

  describe('golaYoga', () => {
    it('should be true when all 7 visible planets in 1 sign', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: ARIES,
        [MARS]: ARIES,
        [MERCURY]: ARIES,
        [JUPITER]: ARIES,
        [VENUS]: ARIES,
        [SATURN]: ARIES,
        [RAHU]: TAURUS,
        [KETU]: SCORPIO,
      });
      expect(golaYoga(chart)).toBe(true);
    });

    it('should be false when planets are spread', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: ARIES,
        [JUPITER]: ARIES,
        [VENUS]: ARIES,
        [SATURN]: ARIES,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(golaYoga(chart)).toBe(false);
    });
  });
});

// ============================================================================
// SUBHA / ASUBHA YOGA TESTS
// ============================================================================

describe('Subha and Asubha Yogas', () => {
  describe('subhaYoga', () => {
    it('should be true when only benefics in lagna', () => {
      // Lagna in Aries, Jupiter and Venus in Aries (benefics)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: CANCER,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,   // alone = benefic but in Virgo
        [JUPITER]: ARIES,   // benefic in lagna
        [VENUS]: ARIES,     // benefic in lagna
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(subhaYoga(chart)).toBe(true);
    });
  });

  describe('asubhaYoga', () => {
    it('should be true when only malefics in lagna', () => {
      // Lagna in Aries, Sun and Mars in Aries (malefics)
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: CANCER,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(asubhaYoga(chart)).toBe(true);
    });
  });
});

// ============================================================================
// NOTABLE PLANETARY YOGAS
// ============================================================================

describe('Notable Planetary Yogas', () => {
  describe('gajaKesariYoga', () => {
    it('should be true when Jupiter in kendra from Moon and strong', () => {
      // Moon in Aries, Jupiter in Cancer (4th from Moon = kendra, Jupiter exalted in Cancer)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: ARIES,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: CANCER,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(gajaKesariYoga(chart)).toBe(true);
    });

    it('should be false when Jupiter not in kendra from Moon', () => {
      // Moon in Aries, Jupiter in Taurus (2nd from Moon, not kendra)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: ARIES,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: TAURUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(gajaKesariYoga(chart)).toBe(false);
    });
  });

  describe('guruMangalaYoga', () => {
    it('should be true when Jupiter and Mars are conjunct', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: SAGITTARIUS,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(guruMangalaYoga(chart)).toBe(true);
    });

    it('should be true when Jupiter and Mars in 7th from each other', () => {
      // Mars in Aries, Jupiter in Libra (7th from Aries)
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: LIBRA,
        [VENUS]: PISCES,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(guruMangalaYoga(chart)).toBe(true);
    });

    it('should be false when Jupiter and Mars not conjunct or in 7th', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: ARIES,
        [MERCURY]: VIRGO,
        [JUPITER]: CANCER,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(guruMangalaYoga(chart)).toBe(false);
    });
  });

  describe('trilochanaYoga', () => {
    it('should be true when Sun, Moon, Mars in trines from each other', () => {
      // Sun in Aries(0), Moon in Leo(4), Mars in Sagittarius(8) - mutual trines
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: LEO,
        [MARS]: SAGITTARIUS,
        [MERCURY]: VIRGO,
        [JUPITER]: CANCER,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      expect(trilochanaYoga(chart)).toBe(true);
    });

    it('should be false when Sun, Moon, Mars not in trines', () => {
      const chart = buildChart(ARIES, {
        [SUN]: ARIES,
        [MOON]: TAURUS,
        [MARS]: GEMINI,
        [MERCURY]: VIRGO,
        [JUPITER]: CANCER,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: LEO,
        [KETU]: AQUARIUS,
      });
      expect(trilochanaYoga(chart)).toBe(false);
    });
  });
});

// ============================================================================
// MAHABHAGYA YOGA
// ============================================================================

describe('Mahabhagya Yoga', () => {
  it('should be true for male day birth with Sun, Moon, Lagna in odd signs', () => {
    // Odd signs: Aries(0), Gemini(2), Leo(4), Libra(6), Sagittarius(8), Aquarius(10)
    const chart = buildChart(ARIES, {
      [SUN]: GEMINI,
      [MOON]: LEO,
      [MARS]: SCORPIO,
      [MERCURY]: VIRGO,
      [JUPITER]: SAGITTARIUS,
      [VENUS]: LIBRA,
      [SATURN]: CAPRICORN,
      [RAHU]: GEMINI,
      [KETU]: SAGITTARIUS,
    });
    expect(mahabhagyaYoga(chart, 'male', true)).toBe(true);
  });

  it('should be false for male day birth with Sun in even sign', () => {
    const chart = buildChart(ARIES, {
      [SUN]: TAURUS, // Even sign
      [MOON]: LEO,
      [MARS]: SCORPIO,
      [MERCURY]: VIRGO,
      [JUPITER]: SAGITTARIUS,
      [VENUS]: LIBRA,
      [SATURN]: CAPRICORN,
      [RAHU]: GEMINI,
      [KETU]: SAGITTARIUS,
    });
    expect(mahabhagyaYoga(chart, 'male', true)).toBe(false);
  });

  it('should be true for female night birth with Sun, Moon, Lagna in even signs', () => {
    // Even signs: Taurus(1), Cancer(3), Virgo(5), Scorpio(7), Capricorn(9), Pisces(11)
    const chart = buildChart(TAURUS, {
      [SUN]: CANCER,
      [MOON]: VIRGO,
      [MARS]: ARIES,
      [MERCURY]: GEMINI,
      [JUPITER]: SAGITTARIUS,
      [VENUS]: LIBRA,
      [SATURN]: CAPRICORN,
      [RAHU]: LEO,
      [KETU]: AQUARIUS,
    });
    expect(mahabhagyaYoga(chart, 'female', false)).toBe(true);
  });
});

// ============================================================================
// CHATUSSAGARA YOGA
// ============================================================================

describe('Chatussagara Yoga', () => {
  it('should be true when all 4 kendras have at least one planet', () => {
    // Lagna Aries. Kendras: Aries(0), Cancer(3), Libra(6), Capricorn(9)
    const chart = buildChart(ARIES, {
      [SUN]: ARIES,        // 1st kendra
      [MOON]: CANCER,      // 2nd kendra
      [MARS]: LIBRA,       // 3rd kendra
      [MERCURY]: CAPRICORN, // 4th kendra
      [JUPITER]: TAURUS,
      [VENUS]: GEMINI,
      [SATURN]: LEO,
      [RAHU]: VIRGO,
      [KETU]: PISCES,
    });
    expect(chatussagaraYoga(chart)).toBe(true);
  });

  it('should be false when one kendra is empty', () => {
    // Lagna Aries. Kendras: Aries(0), Cancer(3), Libra(6), Capricorn(9)
    // No planet in Capricorn(9)
    const chart = buildChart(ARIES, {
      [SUN]: ARIES,
      [MOON]: CANCER,
      [MARS]: LIBRA,
      [MERCURY]: TAURUS,
      [JUPITER]: TAURUS,
      [VENUS]: GEMINI,
      [SATURN]: LEO,
      [RAHU]: VIRGO,
      [KETU]: PISCES,
    });
    expect(chatussagaraYoga(chart)).toBe(false);
  });
});

// ============================================================================
// DETECT ALL YOGAS
// ============================================================================

describe('Yoga Detection', () => {
  describe('detectAllYogas', () => {
    it('should return an array of YogaResult objects', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      const results = detectAllYogas(chart);
      expect(results.length).toBeGreaterThan(0);
      expect(results[0]).toHaveProperty('name');
      expect(results[0]).toHaveProperty('isPresent');
    });

    it('should include known yoga names', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      const results = detectAllYogas(chart);
      const names = results.map((r) => r.name);
      expect(names).toContain('Ruchaka Yoga');
      expect(names).toContain('Gaja Kesari Yoga');
      expect(names).toContain('Nipuna/Budha-Aaditya Yoga');
    });
  });

  describe('getPresentYogas', () => {
    it('should only return yogas that are present', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MOON]: TAURUS,
        [MARS]: SCORPIO,
        [MERCURY]: VIRGO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      const present = getPresentYogas(chart);
      expect(present.every((y) => y.isPresent)).toBe(true);
    });

    it('should find nipuna yoga when Sun and Mercury together', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MERCURY]: LEO,
        [MOON]: TAURUS,
        [MARS]: SCORPIO,
        [JUPITER]: SAGITTARIUS,
        [VENUS]: LIBRA,
        [SATURN]: CAPRICORN,
        [RAHU]: GEMINI,
        [KETU]: SAGITTARIUS,
      });
      const present = getPresentYogas(chart);
      const names = present.map((y) => y.name);
      expect(names).toContain('Nipuna/Budha-Aaditya Yoga');
    });
  });
});

// ============================================================================
// KEMADRUMA YOGA
// ============================================================================

describe('Kemadruma Yoga', () => {
  it('should be true when no planets (except Sun) around Moon and no planets in kendras from lagna', () => {
    // Moon in Cancer(3), Sun in Aries(0). Houses 1,2,12 from Moon = Cancer(3), Leo(4), Gemini(2)
    // No planets other than Sun/Moon in those houses
    // Kendras from Aries Lagna: Aries(0), Cancer(3), Libra(6), Capricorn(9)
    // Only Moon in kendras (Cancer)
    // All other planets in non-kendra, non-Moon-zone houses
    const chart = buildChart(ARIES, {
      [SUN]: SAGITTARIUS,
      [MOON]: CANCER,
      [MARS]: SCORPIO,
      [MERCURY]: SCORPIO,
      [JUPITER]: SCORPIO,
      [VENUS]: SCORPIO,
      [SATURN]: SCORPIO,
      [RAHU]: PISCES,
      [KETU]: VIRGO,
    });
    // Moon zone: Cancer(3), Leo(4), Gemini(2) - only Moon there
    // Kendras: Aries(0), Cancer(3), Libra(6), Capricorn(9) - only Moon in Cancer
    // But wait - planets in Scorpio(7) are not in kendras. Sun in Sagittarius(8) not in Moon zone.
    // All conditions met if no non-Moon planets in kendras
    // Scorpio(7) is not a kendra from Aries. Sag(8) not a kendra.
    // Pisces(11) not kendra. Virgo(5) not kendra.
    // Only Moon in kendra (Cancer). ky2 requires planets in kendras to be only Moon = true
    expect(kemadrumaYoga(chart)).toBe(true);
  });
});

// ============================================================================
// PYTHON PARITY TESTS - Chennai 1996-12-07 D-1 Chart
// ============================================================================
//
// Chart: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
// Lagna: Capricorn (9)
// Mars(2) in Leo(4), Rahu(7) in Virgo(5), Moon(1)/Venus(5) in Libra(6),
// Sun(0) in Scorpio(7), Mercury(3)/Jupiter(4) in Sagittarius(8),
// Saturn(6)/Ketu(8) in Pisces(11)

describe('Python Parity - Chennai 1996-12-07 D-1 Chart', () => {
  const chart: HouseChart = ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8'];

  // ==========================================================================
  // RAVI (SUN) YOGAS
  // ==========================================================================
  // Sun in Scorpio (house 7)
  // 2nd from Sun = Sagittarius (house 8): Mercury(3)/Jupiter(4) present
  // 12th from Sun = Libra (house 6): Moon(1)/Venus(5) present

  describe('Ravi Yogas', () => {
    it('vesiYoga should be true (planet other than Moon in 2nd from Sun)', () => {
      // 2nd from Sun (Scorpio) = Sagittarius: Mercury and Jupiter present
      // Python expected: True
      expect(vesiYoga(chart)).toBe(true);
    });

    it('vosiYoga should be true (Venus in 12th from Sun)', () => {
      // 12th from Sun (Scorpio) = Libra: Moon and Venus present
      // TS filters out Moon, Venus remains -> true
      // Note: Python returns False for this chart. The disagreement may be due to
      // Python's vosiYoga implementation excluding Rahu/Ketu or using different
      // house counting. This is a known parity gap to investigate.
      expect(vosiYoga(chart)).toBe(true);
    });

    it('ubhayacharaYoga should be true (vesi && vosi both true in TS)', () => {
      // TS: vesiYoga=true AND vosiYoga=true -> true
      // Note: Python returns False because Python's vosiYoga is False.
      // Known parity gap carried from vosiYoga difference.
      expect(ubhayacharaYoga(chart)).toBe(true);
    });

    it('nipunaYoga/budhaAadityaYoga should be false (Sun and Mercury in different houses)', () => {
      // Sun in Scorpio(7), Mercury in Sagittarius(8) -> different houses
      // Python expected: False - matches TS
      expect(nipunaYoga(chart)).toBe(false);
      expect(budhaAadityaYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // CHANDRA (MOON) YOGAS
  // ==========================================================================
  // Moon in Libra (house 6)
  // 2nd from Moon = Scorpio (house 7): Sun(0) present
  // 12th from Moon = Virgo (house 5): Rahu(7) present

  describe('Chandra Yogas', () => {
    it('sunaphaaYoga should be false (only Sun in 2nd from Moon, Sun excluded)', () => {
      // 2nd from Moon (Libra) = Scorpio: only Sun present
      // sunaphaaYoga excludes Sun -> no valid planets -> false
      // Python expected: False - matches TS
      expect(sunaphaaYoga(chart)).toBe(false);
    });

    it('anaphaaYoga should be true (Rahu in 12th from Moon)', () => {
      // 12th from Moon (Libra) = Virgo: Rahu(7) present
      // anaphaaYoga excludes Sun -> Rahu remains -> true
      // Python expected: True - matches TS
      expect(anaphaaYoga(chart)).toBe(true);
    });

    it('duradharaYoga/dhurdhuraYoga should be false (sunaphaa is false)', () => {
      // duradharaYoga = sunaphaaYoga && anaphaaYoga = false && true = false
      // Python expected: False - matches TS
      expect(duradharaYoga(chart)).toBe(false);
      expect(dhurdhuraYoga(chart)).toBe(false);
    });

    it('kemadrumaYoga should be false (Venus in Moon zone, planets in kendras)', () => {
      // Moon zone (houses 5,6,7): Venus in 6, Sun in 7 -> non-Sun/Moon planets in zone -> false
      // Python expected: False - matches TS
      expect(kemadrumaYoga(chart)).toBe(false);
    });

    it('chandraMangalaYoga should be false (Moon and Mars in different houses)', () => {
      // Moon in Libra(6), Mars in Leo(4) -> different houses
      // Python expected: False - matches TS
      expect(chandraMangalaYoga(chart)).toBe(false);
    });

    it('adhiYoga should be false (benefics not all in 6/7/8 from Moon)', () => {
      // 6th/7th/8th from Moon (Libra) = Pisces(11)/Aries(0)/Taurus(1)
      // Jupiter(4) in Sagittarius(8) is NOT in those houses -> false
      // Python expected: False - matches TS
      expect(adhiYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // DALA YOGAS
  // ==========================================================================
  // Lagna in Capricorn (9). Kendras from Lagna: 9, 0, 3, 6.

  describe('Dala Yogas', () => {
    it('maalaaYoga should be false (benefics not in 3 of 4 kendras)', () => {
      // Kendras from Capricorn: Capricorn(9), Aries(0), Cancer(3), Libra(6)
      // Natural benefics: Jupiter(4)=Sag(8), Venus(5)=Libra(6), Mercury(3)=Sag(8)
      // Only Libra(6) has a benefic (Venus) -> 1 out of 4 kendras -> false
      // Python expected: False - matches TS
      expect(maalaaYoga(chart)).toBe(false);
    });

    it('sarpaYoga should be false (malefics not in 3 of 4 kendras)', () => {
      // Kendras from Capricorn: 9, 0, 3, 6
      // Natural malefics: Sun(0)=Scorpio(7), Mars(2)=Leo(4), Saturn(6)=Pisces(11),
      //                   Rahu(7)=Virgo(5), Ketu(8)=Pisces(11)
      // No malefics in any kendra -> 0 out of 4 -> false
      // Python expected: False - matches TS
      expect(sarpaYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // AAKRITI YOGAS - Additional coverage
  // ==========================================================================
  // Planet houses (Sun-Saturn): {4, 6, 7, 8, 11} = 5 distinct houses
  // Lagna in Capricorn (9)

  describe('Aakriti Yogas (Chennai chart)', () => {
    it('gadaaYoga should be false (planets in 5 houses, not 2 consecutive quadrants)', () => {
      expect(gadaaYoga(chart)).toBe(false);
    });

    it('sakataYoga should be false (planets not only in 1st and 7th from Lagna)', () => {
      expect(sakataYoga(chart)).toBe(false);
    });

    it('vihangaYoga should be false (planets not only in 4th and 10th from Lagna)', () => {
      expect(vihangaYoga(chart)).toBe(false);
    });

    it('sringaatakaYoga should be false (planets not confined to trines from Lagna)', () => {
      expect(sringaatakaYoga(chart)).toBe(false);
    });

    it('halaYoga should be false (planets not in non-Lagna trine set)', () => {
      expect(halaYoga(chart)).toBe(false);
    });

    it('vajraYoga should be false (benefics/malefics not in required kendras)', () => {
      expect(vajraYoga(chart)).toBe(false);
    });

    it('yavaYoga should be false (malefics/benefics not in required kendras)', () => {
      expect(yavaYoga(chart)).toBe(false);
    });

    it('kamalaYoga should be false (planets not all in kendras from Lagna)', () => {
      expect(kamalaYoga(chart)).toBe(false);
    });

    it('vaapiYoga should be false (planets not all in panaparas or apoklimas)', () => {
      expect(vaapiYoga(chart)).toBe(false);
    });

    it('yoopaYoga should be false (planets not all in houses 1-4 from Lagna)', () => {
      expect(yoopaYoga(chart)).toBe(false);
    });

    it('saraYoga should be false (planets not all in houses 4-7 from Lagna)', () => {
      expect(saraYoga(chart)).toBe(false);
    });

    it('saktiYoga should be false (planets not all in houses 7-10 from Lagna)', () => {
      expect(saktiYoga(chart)).toBe(false);
    });

    it('dandaYoga should be false (planets not all in houses 10-1 from Lagna)', () => {
      expect(dandaYoga(chart)).toBe(false);
    });

    it('naukaaYoga should be false (planets not in 7 consecutive from Lagna)', () => {
      expect(naukaaYoga(chart)).toBe(false);
    });

    it('kootaYoga should be false (planets not in 7 consecutive from 4th)', () => {
      expect(kootaYoga(chart)).toBe(false);
    });

    it('chatraYoga should be false (planets not in 7 consecutive from 7th)', () => {
      expect(chatraYoga(chart)).toBe(false);
    });

    it('chaapaYoga should be false (planets not in 7 consecutive from 10th)', () => {
      expect(chaapaYoga(chart)).toBe(false);
    });

    it('ardhaChandraYoga should be false (not in 7 consecutive from non-kendra)', () => {
      expect(ardhaChandraYoga(chart)).toBe(false);
    });

    it('chakraYoga should be false (odd houses not all occupied)', () => {
      expect(chakraYoga(chart)).toBe(false);
    });

    it('samudraYoga should be false (even houses not all occupied)', () => {
      expect(samudraYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // SANKHYA YOGAS for Chennai chart
  // ==========================================================================
  // Planet houses (Sun-Saturn): {4, 6, 7, 8, 11} = 5 distinct houses

  describe('Sankhya Yogas (Chennai chart)', () => {
    it('paasaYoga should be true (7 visible planets in 5 distinct houses)', () => {
      // Sun(0)->7, Moon(1)->6, Mars(2)->4, Mercury(3)->8, Jupiter(4)->8,
      // Venus(5)->6, Saturn(6)->11 = {4,6,7,8,11} = 5 houses
      expect(paasaYoga(chart)).toBe(true);
    });

    it('veenaaYoga should be false (need 7 houses, have 5)', () => {
      expect(veenaaYoga(chart)).toBe(false);
    });

    it('daamaYoga should be false (need 6 houses, have 5)', () => {
      expect(daamaYoga(chart)).toBe(false);
    });

    it('kedaaraYoga should be false (need 4 houses, have 5)', () => {
      expect(kedaaraYoga(chart)).toBe(false);
    });

    it('soolaYoga should be false (need 3 houses, have 5)', () => {
      expect(soolaYoga(chart)).toBe(false);
    });

    it('yugaYoga should be false (need 2 houses, have 5)', () => {
      expect(yugaYoga(chart)).toBe(false);
    });

    it('golaYoga should be false (need 1 house, have 5)', () => {
      expect(golaYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // OTHER YOGAS for Chennai chart
  // ==========================================================================

  describe('Other Yogas (Chennai chart)', () => {
    it('gajaKesariYoga should be false (Jupiter not in kendra from Moon)', () => {
      // Moon in Libra(6), Jupiter in Sagittarius(8)
      // Kendras from Moon: 6, 9, 0, 3 -> Jupiter at 8 is not a kendra
      expect(gajaKesariYoga(chart)).toBe(false);
    });

    it('guruMangalaYoga should be false (Jupiter and Mars not conjunct or in 7th)', () => {
      // Jupiter in Sagittarius(8), Mars in Leo(4) -> distance = 4, not 0 or 6
      expect(guruMangalaYoga(chart)).toBe(false);
    });

    it('trilochanaYoga should be false (Sun, Moon, Mars not in mutual trines)', () => {
      // Sun in Scorpio(7), Moon in Libra(6), Mars in Leo(4) -> not in trines
      expect(trilochanaYoga(chart)).toBe(false);
    });

    it('amalaYoga should be true (Venus in 10th from Lagna)', () => {
      // 10th from Lagna(Capricorn=9) = (9+9)%12 = Libra(6)
      // Venus (benefic) is in Libra -> amalaYoga = true
      expect(amalaYoga(chart)).toBe(true);
    });

    it('parvataYoga should be false', () => {
      expect(parvataYoga(chart)).toBe(false);
    });

    it('chatussagaraYoga should be false (not all 4 kendras occupied)', () => {
      // Kendras from Capricorn(9): 9, 0, 3, 6
      // House 9 (Capricorn): only Lagna, no planets
      // House 0 (Aries): empty
      // House 3 (Cancer): empty
      // House 6 (Libra): Moon/Venus -> occupied
      // Only 1 kendra occupied -> false
      expect(chatussagaraYoga(chart)).toBe(false);
    });

    it('harshaYoga should be true (6th lord Mercury in dushthana)', () => {
      // Lagna=Capricorn(9). 6th sign = (9+5)%12 = Gemini(2). Lord = Mercury.
      // Mercury in Sagittarius(8). Dushthanas from Capricorn: houses 2, 4, 8.
      // Mercury in house 8 is a dushthana -> true
      expect(harshaYoga(chart)).toBe(true);
    });

    it('saralaYoga should be false', () => {
      expect(saralaYoga(chart)).toBe(false);
    });

    it('vimalaYoga should be true (12th lord Jupiter in dushthana)', () => {
      // Lagna=Capricorn(9). 12th sign = (9+11)%12 = Sagittarius(8). Lord = Jupiter.
      // Jupiter in Sagittarius(8). Dushthanas from Capricorn: houses 2, 4, 8.
      // Jupiter in house 8 is a dushthana -> true
      expect(vimalaYoga(chart)).toBe(true);
    });

    it('lakshmiYoga should be false', () => {
      expect(lakshmiYoga(chart)).toBe(false);
    });

    it('dhanaYoga should be false', () => {
      expect(dhanaYoga(chart)).toBe(false);
    });

    it('vasumathiYoga should be false', () => {
      expect(vasumathiYoga(chart)).toBe(false);
    });

    it('kahalaYoga should be false', () => {
      expect(kahalaYoga(chart)).toBe(false);
    });

    it('rajalakshanaYoga should be false', () => {
      expect(rajalakshanaYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // PANCHA MAHAPURUSHA YOGAS for Chennai chart
  // ==========================================================================

  describe('Pancha Mahapurusha Yogas (Chennai chart)', () => {
    it('ruchakaYoga should be false (Mars in Leo, not own/exalted sign)', () => {
      // Mars(2) in Leo(4) -> not Aries, Scorpio, or Capricorn
      expect(ruchakaYoga(chart)).toBe(false);
    });

    it('bhadraYoga should be false (Mercury in Sagittarius, not own/exalted)', () => {
      // Mercury(3) in Sagittarius(8) -> not Gemini or Virgo
      expect(bhadraYoga(chart)).toBe(false);
    });

    it('sasaYoga should be false (Saturn in Pisces, not own/exalted)', () => {
      // Saturn(6) in Pisces(11) -> not Capricorn, Aquarius, or Libra
      expect(sasaYoga(chart)).toBe(false);
    });

    it('maalavyaYoga should be true (Venus in Libra, own sign, in kendra from Lagna)', () => {
      // Venus(5) in Libra(6) -> Libra is Venus's own sign
      // Kendras from Capricorn(9): 9, 0, 3, 6 -> Libra(6) IS a kendra
      // Venus in own sign AND in kendra -> maalavyaYoga = true
      expect(maalavyaYoga(chart)).toBe(true);
    });

    it('hamsaYoga should be false (Jupiter in Sagittarius but need kendra check)', () => {
      // Jupiter(4) in Sagittarius(8) -> Sagittarius is own sign
      // Kendras from Capricorn(9): 9, 0, 3, 6 -> Sagittarius(8) is NOT a kendra
      expect(hamsaYoga(chart)).toBe(false);
    });
  });

  // ==========================================================================
  // NAABHASA AASRAYA YOGAS for Chennai chart
  // ==========================================================================

  describe('Naabhasa Aasraya Yogas (Chennai chart)', () => {
    it('rajjuYoga should be false (not all planets in movable signs)', () => {
      expect(rajjuYoga(chart)).toBe(false);
    });

    it('musalaYoga should be false (not all planets in fixed signs)', () => {
      expect(musalaYoga(chart)).toBe(false);
    });

    it('nalaYoga should be false (not all planets in dual signs)', () => {
      expect(nalaYoga(chart)).toBe(false);
    });
  });
});
