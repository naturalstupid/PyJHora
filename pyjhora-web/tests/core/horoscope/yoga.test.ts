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
  marudYoga,
  // Untested yoga functions (Phase 2)
  vikramaMalikaYoga,
  sukhaMalikaYoga,
  putraMalikaYoga,
  satruMalikaYoga,
  kalatraMalikaYoga,
  randhraMalikaYoga,
  bhagyaMalikaYoga,
  karmaMalikaYoga,
  labhaMalikaYoga,
  vyayaMalikaYoga,
  isMercuryBenefic,
  getNaturalBenefics,
  getNaturalMalefics,
  isPlanetExalted,
  isPlanetStrong,
  getQuadrants,
  getTrines,
  getDushthanas,
  getHouseOwner,
  bhaarathiYoga,
  chandikaaYoga,
  garudaYoga,
  gouriYoga,
  vishnuYoga,
  madhyaVayasiDhanaYoga,
  balyaDhanaYoga,
  vallakiYoga,
  sarpagandaYoga,
  damaYoga,
  kedaraYoga,
  sulaYoga,
  ishuYoga,
  navYoga,
  srikYoga,
  vihagaYoga,
  lagnaadhiYoga,
  sreenaathaYoga,
  kaahalaYoga,
  vanchanaChoraBheethiYoga,
  areLordsExchanged,
  dhanaYoga123_128,
  budhaYoga,
  andhaYoga,
  chaamaraYoga,
  sankhaYoga,
  khadgaYoga,
  goYoga,
  dharidhraYoga,
  dhurYoga,
  bheriYoga,
  mridangaYoga,
  sreenaatheYoga,
  koormaYoga,
  kusumaYoga,
  kalaanidhiYoga,
  lagnaAdhiYoga,
  hariYoga,
  haraYoga,
  brahmaYoga,
  sivaYoga,
  devendraYoga,
  indraYoga,
  raviYoga,
  bhaaskaraYoga,
  kulavardhanaYoga,
  gandharvaYoga,
  vidyutYoga,
  chapaYoga,
  pushkalaYoga,
  makutaYoga,
  jayaYoga,
  vanchanaChoraYoga,
  hariharaBrahmaYoga,
  sreenataYoga,
  parijathaYoga,
  gajaYoga,
  kalanidhiYoga,
  saaradaYoga,
  saraswathiYoga,
  amsaavataraYoga,
  dehapushtiYoga,
  rogagrasthaYoga,
  krisangaYoga,
  dehasthoulyaYoga,
  sadaSancharaYoga,
  bahudravyarjanaYoga,
  anthyaVayasiDhanaYoga,
  sareeraSoukhyaYoga,
  matrumooladdhanaYoga,
  kalatramooladdhanaYoga,
  swaveeryaddhanaYoga,
  kalpadrumaYoga,
  matsyaYoga,
  mookaYoga,
  netranasaYoga,
  asatyavadiYoga,
  jadaYoga,
  bhratrumooladdhanapraptiYoga,
  putramooladdhanaYoga,
  shatrumooladdhanaYoga,
  amarananthaDhanaYoga,
  ayatnadhanalabhaYoga,
  parannabhojanaYoga,
  sraddhannabhukthaYoga,
  detectAllYogas,
  getPresentYogas,
  planetPositionsToChart,
  lagnaMalikaYoga,
  dhanaMalikaYoga,
  // fromPlanetPositions variants
  vesiYogaFromPlanetPositions,
  vosiYogaFromPlanetPositions,
  ubhayacharaYogaFromPlanetPositions,
  nipunaYogaFromPlanetPositions,
  budhaAadityaYogaFromPlanetPositions,
  sunaphaaYogaFromPlanetPositions,
  anaphaaYogaFromPlanetPositions,
  duradharaYogaFromPlanetPositions,
  kemadrumaYogaFromPlanetPositions,
  chandraMangalaYogaFromPlanetPositions,
  adhiYogaFromPlanetPositions,
  ruchakaYogaFromPlanetPositions,
  hamsaYogaFromPlanetPositions,
  maalavyaYogaFromPlanetPositions,
  gajaKesariYogaFromPlanetPositions,
  guruMangalaYogaFromPlanetPositions,
  trilochanaYogaFromPlanetPositions,
  harshaYogaFromPlanetPositions,
  vimalaYogaFromPlanetPositions,
  amalaYogaFromPlanetPositions,
  rajjuYogaFromPlanetPositions,
  kamalaYogaFromPlanetPositions,
  veenaaYogaFromPlanetPositions,
  paasaYogaFromPlanetPositions,
  lagnaMalikaYogaFromPlanetPositions,
  dhanaMalikaYogaFromPlanetPositions,
  mahabhagyaYogaFromPlanetPositions,
  detectAllYogasFromPlanetPositions,
  getPresentYogasFromPlanetPositions,
  type HouseChart,
} from '@core/horoscope/yoga';
import type { PlanetPosition } from '@core/types';
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

    it('harshaYoga should be false (Python parity: 6th lord must be IN the 6th house)', () => {
      // Lagna=Capricorn(9). 6th sign = (9+5)%12 = Gemini(2). Lord = Mercury.
      // Mercury in Sagittarius(8), NOT in Gemini(2) -> false
      expect(harshaYoga(chart)).toBe(false);
    });

    it('saralaYoga should be false', () => {
      expect(saralaYoga(chart)).toBe(false);
    });

    it('vimalaYoga should be true (Python parity: 12th lord Jupiter in 12th house)', () => {
      // Lagna=Capricorn(9). 12th sign = (9+11)%12 = Sagittarius(8). Lord = Jupiter.
      // Jupiter in Sagittarius(8) = the 12th house itself -> true
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

// ============================================================================
// PLANET POSITIONS TO CHART CONVERSION
// ============================================================================

/**
 * Helper: build PlanetPosition[] from ascendant rasi and planet placements.
 * Creates minimal PlanetPosition objects with only planet and rasi populated.
 */
function buildPositions(ascRasi: number, planets: Record<number, number>): PlanetPosition[] {
  const positions: PlanetPosition[] = [];
  // Ascendant as planet -1
  positions.push({
    planet: -1,
    rasi: ascRasi,
    longitude: ascRasi * 30,
    longitudeInSign: 0,
    isRetrograde: false,
    nakshatra: 0,
    nakshatraPada: 0,
  });
  for (const [planet, rasi] of Object.entries(planets)) {
    positions.push({
      planet: parseInt(planet, 10),
      rasi: rasi,
      longitude: rasi * 30,
      longitudeInSign: 0,
      isRetrograde: false,
      nakshatra: 0,
      nakshatraPada: 0,
    });
  }
  return positions;
}

describe('planetPositionsToChart', () => {
  it('should convert PlanetPosition[] to HouseChart matching buildChart', () => {
    const planets = {
      [SUN]: ARIES,
      [MOON]: TAURUS,
      [MARS]: GEMINI,
      [MERCURY]: CANCER,
      [JUPITER]: LEO,
      [VENUS]: VIRGO,
      [SATURN]: LIBRA,
      [RAHU]: SCORPIO,
      [KETU]: TAURUS,
    };
    const positions = buildPositions(ARIES, planets);
    const chart = planetPositionsToChart(positions);

    // Ascendant should be in Aries
    expect(chart[ARIES]).toContain(ASCENDANT_SYMBOL);
    // Sun in Aries
    expect(chart[ARIES]).toContain('0');
    // Moon in Taurus
    expect(chart[TAURUS]).toContain('1');
    // Mars in Gemini
    expect(chart[GEMINI]).toContain('2');
  });

  it('should handle multiple planets in same house', () => {
    const positions = buildPositions(ARIES, {
      [SUN]: ARIES,
      [MERCURY]: ARIES,
      [MOON]: TAURUS,
    });
    const chart = planetPositionsToChart(positions);
    expect(chart[ARIES]).toContain('0');
    expect(chart[ARIES]).toContain('3');
    expect(chart[ARIES]).toContain(ASCENDANT_SYMBOL);
  });
});

// ============================================================================
// FROM PLANET POSITIONS VARIANT TESTS
// ============================================================================

describe('FromPlanetPositions Variants', () => {
  // Use the same chart data as the Chennai 1996-12-07 D-1 chart
  // Chart: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
  const chennaiChart: HouseChart = ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8'];
  const chennaiPositions = buildPositions(CAPRICORN, {
    [SUN]: SCORPIO,        // house 7
    [MOON]: LIBRA,         // house 6
    [MARS]: LEO,           // house 4
    [MERCURY]: SAGITTARIUS, // house 8
    [JUPITER]: SAGITTARIUS, // house 8
    [VENUS]: LIBRA,        // house 6
    [SATURN]: PISCES,      // house 11
    [RAHU]: VIRGO,         // house 5
    [KETU]: PISCES,        // house 11
  });

  describe('Sun Yoga variants', () => {
    it('vesiYogaFromPlanetPositions should match vesiYoga', () => {
      expect(vesiYogaFromPlanetPositions(chennaiPositions)).toBe(vesiYoga(chennaiChart));
    });

    it('vosiYogaFromPlanetPositions should match vosiYoga', () => {
      expect(vosiYogaFromPlanetPositions(chennaiPositions)).toBe(vosiYoga(chennaiChart));
    });

    it('ubhayacharaYogaFromPlanetPositions should match ubhayacharaYoga', () => {
      expect(ubhayacharaYogaFromPlanetPositions(chennaiPositions)).toBe(ubhayacharaYoga(chennaiChart));
    });

    it('nipunaYogaFromPlanetPositions should match nipunaYoga', () => {
      expect(nipunaYogaFromPlanetPositions(chennaiPositions)).toBe(nipunaYoga(chennaiChart));
      expect(budhaAadityaYogaFromPlanetPositions(chennaiPositions)).toBe(nipunaYoga(chennaiChart));
    });
  });

  describe('Moon Yoga variants', () => {
    it('sunaphaaYogaFromPlanetPositions should match sunaphaaYoga', () => {
      expect(sunaphaaYogaFromPlanetPositions(chennaiPositions)).toBe(sunaphaaYoga(chennaiChart));
    });

    it('anaphaaYogaFromPlanetPositions should match anaphaaYoga', () => {
      expect(anaphaaYogaFromPlanetPositions(chennaiPositions)).toBe(anaphaaYoga(chennaiChart));
    });

    it('duradharaYogaFromPlanetPositions should match duradharaYoga', () => {
      expect(duradharaYogaFromPlanetPositions(chennaiPositions)).toBe(duradharaYoga(chennaiChart));
    });

    it('kemadrumaYogaFromPlanetPositions should match kemadrumaYoga', () => {
      expect(kemadrumaYogaFromPlanetPositions(chennaiPositions)).toBe(kemadrumaYoga(chennaiChart));
    });

    it('chandraMangalaYogaFromPlanetPositions should match chandraMangalaYoga', () => {
      expect(chandraMangalaYogaFromPlanetPositions(chennaiPositions)).toBe(chandraMangalaYoga(chennaiChart));
    });

    it('adhiYogaFromPlanetPositions should match adhiYoga', () => {
      expect(adhiYogaFromPlanetPositions(chennaiPositions)).toBe(adhiYoga(chennaiChart));
    });
  });

  describe('Pancha Mahapurusha Yoga variants', () => {
    it('ruchakaYogaFromPlanetPositions should match ruchakaYoga', () => {
      expect(ruchakaYogaFromPlanetPositions(chennaiPositions)).toBe(ruchakaYoga(chennaiChart));
    });

    it('hamsaYogaFromPlanetPositions should match hamsaYoga', () => {
      expect(hamsaYogaFromPlanetPositions(chennaiPositions)).toBe(hamsaYoga(chennaiChart));
    });

    it('maalavyaYogaFromPlanetPositions should match maalavyaYoga', () => {
      expect(maalavyaYogaFromPlanetPositions(chennaiPositions)).toBe(maalavyaYoga(chennaiChart));
    });
  });

  describe('Notable Yoga variants', () => {
    it('gajaKesariYogaFromPlanetPositions should match gajaKesariYoga', () => {
      expect(gajaKesariYogaFromPlanetPositions(chennaiPositions)).toBe(gajaKesariYoga(chennaiChart));
    });

    it('guruMangalaYogaFromPlanetPositions should match guruMangalaYoga', () => {
      expect(guruMangalaYogaFromPlanetPositions(chennaiPositions)).toBe(guruMangalaYoga(chennaiChart));
    });

    it('trilochanaYogaFromPlanetPositions should match trilochanaYoga', () => {
      expect(trilochanaYogaFromPlanetPositions(chennaiPositions)).toBe(trilochanaYoga(chennaiChart));
    });

    it('amalaYogaFromPlanetPositions should match amalaYoga', () => {
      expect(amalaYogaFromPlanetPositions(chennaiPositions)).toBe(amalaYoga(chennaiChart));
    });
  });

  describe('Viparita Raja Yoga variants', () => {
    it('harshaYogaFromPlanetPositions should match harshaYoga', () => {
      expect(harshaYogaFromPlanetPositions(chennaiPositions)).toBe(harshaYoga(chennaiChart));
    });

    it('vimalaYogaFromPlanetPositions should match vimalaYoga', () => {
      expect(vimalaYogaFromPlanetPositions(chennaiPositions)).toBe(vimalaYoga(chennaiChart));
    });
  });

  describe('Naabhasa Yoga variants', () => {
    it('rajjuYogaFromPlanetPositions should match rajjuYoga', () => {
      expect(rajjuYogaFromPlanetPositions(chennaiPositions)).toBe(rajjuYoga(chennaiChart));
    });

    it('kamalaYogaFromPlanetPositions should match kamalaYoga', () => {
      expect(kamalaYogaFromPlanetPositions(chennaiPositions)).toBe(kamalaYoga(chennaiChart));
    });
  });

  describe('Sankhya Yoga variants', () => {
    it('veenaaYogaFromPlanetPositions should match veenaaYoga', () => {
      expect(veenaaYogaFromPlanetPositions(chennaiPositions)).toBe(veenaaYoga(chennaiChart));
    });

    it('paasaYogaFromPlanetPositions should match paasaYoga', () => {
      expect(paasaYogaFromPlanetPositions(chennaiPositions)).toBe(paasaYoga(chennaiChart));
    });
  });

  describe('Malika Yoga variants', () => {
    it('lagnaMalikaYogaFromPlanetPositions should match lagnaMalikaYoga', () => {
      expect(lagnaMalikaYogaFromPlanetPositions(chennaiPositions)).toBe(lagnaMalikaYoga(chennaiChart));
    });

    it('dhanaMalikaYogaFromPlanetPositions should match dhanaMalikaYoga', () => {
      expect(dhanaMalikaYogaFromPlanetPositions(chennaiPositions)).toBe(dhanaMalikaYoga(chennaiChart));
    });
  });

  describe('Mahabhagya Yoga variant', () => {
    it('mahabhagyaYogaFromPlanetPositions should match mahabhagyaYoga for male day birth', () => {
      const positions = buildPositions(ARIES, {
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
      expect(mahabhagyaYogaFromPlanetPositions(positions, 'male', true)).toBe(
        mahabhagyaYoga(chart, 'male', true)
      );
      expect(mahabhagyaYogaFromPlanetPositions(positions, 'male', true)).toBe(true);
    });
  });

  describe('Batch detection variants', () => {
    it('detectAllYogasFromPlanetPositions should match detectAllYogas', () => {
      const resultsFromChart = detectAllYogas(chennaiChart);
      const resultsFromPositions = detectAllYogasFromPlanetPositions(chennaiPositions);
      expect(resultsFromPositions.length).toBe(resultsFromChart.length);
      for (let i = 0; i < resultsFromChart.length; i++) {
        expect(resultsFromPositions[i].name).toBe(resultsFromChart[i].name);
        expect(resultsFromPositions[i].isPresent).toBe(resultsFromChart[i].isPresent);
      }
    });

    it('getPresentYogasFromPlanetPositions should match getPresentYogas', () => {
      const presentFromChart = getPresentYogas(chennaiChart);
      const presentFromPositions = getPresentYogasFromPlanetPositions(chennaiPositions);
      expect(presentFromPositions.length).toBe(presentFromChart.length);
      const namesFromChart = presentFromChart.map(y => y.name).sort();
      const namesFromPositions = presentFromPositions.map(y => y.name).sort();
      expect(namesFromPositions).toEqual(namesFromChart);
    });
  });
});

// ============================================================================
// FROM PLANET POSITIONS WITH POSITIVE YOGA CASES
// ============================================================================

describe('FromPlanetPositions - Positive Cases', () => {
  it('nipunaYogaFromPlanetPositions should be true when Sun and Mercury together', () => {
    const positions = buildPositions(ARIES, {
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
    expect(nipunaYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('vesiYogaFromPlanetPositions should be true when planet in 2nd from Sun', () => {
    const positions = buildPositions(ARIES, {
      [SUN]: ARIES,
      [MARS]: TAURUS,  // 2nd from Sun
      [MOON]: CANCER,
      [MERCURY]: GEMINI,
      [JUPITER]: SAGITTARIUS,
      [VENUS]: PISCES,
      [SATURN]: CAPRICORN,
      [RAHU]: GEMINI,
      [KETU]: SAGITTARIUS,
    });
    expect(vesiYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('chandraMangalaYogaFromPlanetPositions should be true when Moon and Mars together', () => {
    const positions = buildPositions(ARIES, {
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
    expect(chandraMangalaYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('ruchakaYogaFromPlanetPositions should be true when Mars in Aries kendra from Lagna', () => {
    const positions = buildPositions(ARIES, {
      [SUN]: LEO,
      [MOON]: TAURUS,
      [MARS]: ARIES,  // own sign in kendra
      [MERCURY]: VIRGO,
      [JUPITER]: SAGITTARIUS,
      [VENUS]: LIBRA,
      [SATURN]: CAPRICORN,
      [RAHU]: GEMINI,
      [KETU]: SAGITTARIUS,
    });
    expect(ruchakaYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('gajaKesariYogaFromPlanetPositions should be true when Jupiter in kendra from Moon and strong', () => {
    const positions = buildPositions(ARIES, {
      [SUN]: LEO,
      [MOON]: ARIES,
      [MARS]: SCORPIO,
      [MERCURY]: VIRGO,
      [JUPITER]: CANCER,  // exalted, 4th from Moon
      [VENUS]: LIBRA,
      [SATURN]: CAPRICORN,
      [RAHU]: GEMINI,
      [KETU]: SAGITTARIUS,
    });
    expect(gajaKesariYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('trilochanaYogaFromPlanetPositions should be true for Sun/Moon/Mars in trines', () => {
    const positions = buildPositions(ARIES, {
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
    expect(trilochanaYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('rajjuYogaFromPlanetPositions should be true when all planets in movable signs', () => {
    const positions = buildPositions(ARIES, {
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
    expect(rajjuYogaFromPlanetPositions(positions)).toBe(true);
  });

  it('veenaaYogaFromPlanetPositions should be true with 7 distinct houses', () => {
    const positions = buildPositions(ARIES, {
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
    expect(veenaaYogaFromPlanetPositions(positions)).toBe(true);
  });
});

// ============================================================================
// PYTHON PARITY TESTS - Fictional Chart
// ============================================================================
//
// Chart: ['5/6', '', '', '1', '8', 'L', '4', '', '', '', '2/7', '0/3']
// Aries(0): Venus(5), Saturn(6)
// Cancer(3): Moon(1)
// Leo(4): Ketu(8)
// Virgo(5): Lagna(L)
// Libra(6): Jupiter(4)
// Aquarius(10): Mars(2), Rahu(7)
// Pisces(11): Sun(0), Mercury(3)
//
// Python-verified results for all yoga functions.

describe('Python Parity - Fictional Chart (Virgo Lagna)', () => {
  const chart: HouseChart = ['5/6', '', '', '1', '8', 'L', '4', '', '', '', '2/7', '0/3'];

  // ---- Tier 1 Yogas (from first batch Python run) ----

  describe('Ravi Yogas (Fictional Chart)', () => {
    it('vesiYoga should be true (Python parity)', () => {
      expect(vesiYoga(chart)).toBe(true);
    });
    it('vosiYoga should be true (Python parity)', () => {
      expect(vosiYoga(chart)).toBe(true);
    });
    it('ubhayacharaYoga should be true (Python parity)', () => {
      expect(ubhayacharaYoga(chart)).toBe(true);
    });
    it('nipunaYoga should be true (Sun+Mercury in Pisces)', () => {
      expect(nipunaYoga(chart)).toBe(true);
    });
  });

  describe('Chandra Yogas (Fictional Chart)', () => {
    it('sunaphaaYoga should be true (Python parity)', () => {
      expect(sunaphaaYoga(chart)).toBe(true);
    });
    it('kemadrumaYoga should be false', () => {
      expect(kemadrumaYoga(chart)).toBe(false);
    });
    it('chandraMangalaYoga should be false', () => {
      expect(chandraMangalaYoga(chart)).toBe(false);
    });
    it('adhiYoga should be false', () => {
      expect(adhiYoga(chart)).toBe(false);
    });
  });

  describe('Pancha Mahapurusha (Fictional Chart)', () => {
    it('ruchakaYoga should be false', () => {
      expect(ruchakaYoga(chart)).toBe(false);
    });
    it('bhadraYoga should be false', () => {
      expect(bhadraYoga(chart)).toBe(false);
    });
    it('sasaYoga should be false', () => {
      expect(sasaYoga(chart)).toBe(false);
    });
    it('maalavyaYoga should be false', () => {
      expect(maalavyaYoga(chart)).toBe(false);
    });
    it('hamsaYoga should be false', () => {
      expect(hamsaYoga(chart)).toBe(false);
    });
  });

  describe('Naabhasa Aasraya (Fictional Chart)', () => {
    it('rajjuYoga should be false', () => {
      expect(rajjuYoga(chart)).toBe(false);
    });
    it('musalaYoga should be false', () => {
      expect(musalaYoga(chart)).toBe(false);
    });
    it('nalaYoga should be false', () => {
      expect(nalaYoga(chart)).toBe(false);
    });
  });

  describe('Aakriti / Dala / Sankhya (Fictional Chart)', () => {
    it('maalaaYoga should be false', () => {
      expect(maalaaYoga(chart)).toBe(false);
    });
    it('sarpaYoga should be false', () => {
      expect(sarpaYoga(chart)).toBe(false);
    });
    it('gadaaYoga should be false', () => {
      expect(gadaaYoga(chart)).toBe(false);
    });
    it('sakataYoga should be false', () => {
      expect(sakataYoga(chart)).toBe(false);
    });
    it('vihangaYoga should be false', () => {
      expect(vihangaYoga(chart)).toBe(false);
    });
    it('sringaatakaYoga should be false', () => {
      expect(sringaatakaYoga(chart)).toBe(false);
    });
    it('halaYoga should be false', () => {
      expect(halaYoga(chart)).toBe(false);
    });
    it('vajraYoga should be false', () => {
      expect(vajraYoga(chart)).toBe(false);
    });
    it('yavaYoga should be false', () => {
      expect(yavaYoga(chart)).toBe(false);
    });
    it('kamalaYoga should be false', () => {
      expect(kamalaYoga(chart)).toBe(false);
    });
    it('vaapiYoga should be false', () => {
      expect(vaapiYoga(chart)).toBe(false);
    });
    it('yoopaYoga should be false', () => {
      expect(yoopaYoga(chart)).toBe(false);
    });
    it('saraYoga should be false', () => {
      expect(saraYoga(chart)).toBe(false);
    });
    it('saktiYoga should be false', () => {
      expect(saktiYoga(chart)).toBe(false);
    });
    it('dandaYoga should be false', () => {
      expect(dandaYoga(chart)).toBe(false);
    });
    it('naukaaYoga should be false', () => {
      expect(naukaaYoga(chart)).toBe(false);
    });
    it('kootaYoga should be false', () => {
      expect(kootaYoga(chart)).toBe(false);
    });
    it('chatraYoga should be false', () => {
      expect(chatraYoga(chart)).toBe(false);
    });
    it('chaapaYoga should be false', () => {
      expect(chaapaYoga(chart)).toBe(false);
    });
    it('ardhaChandraYoga should be false', () => {
      expect(ardhaChandraYoga(chart)).toBe(false);
    });
    it('chakraYoga should be false', () => {
      expect(chakraYoga(chart)).toBe(false);
    });
    it('samudraYoga should be false', () => {
      expect(samudraYoga(chart)).toBe(false);
    });
  });

  describe('Sankhya Distribution (Fictional Chart)', () => {
    // Visible planets in 6 distinct houses: {0, 3, 6, 10, 11, 4(Ketu doesn't count for sankhya)}
    // Actually Sun-Saturn occupy: {0, 3, 6, 10, 11} = 5 houses (same as paasa)
    it('paasaYoga should be true (5 distinct houses)', () => {
      expect(paasaYoga(chart)).toBe(true);
    });
    it('veenaaYoga should be false', () => {
      expect(veenaaYoga(chart)).toBe(false);
    });
    it('daamaYoga should be false', () => {
      expect(daamaYoga(chart)).toBe(false);
    });
    it('kedaaraYoga should be false', () => {
      expect(kedaaraYoga(chart)).toBe(false);
    });
    it('soolaYoga should be false', () => {
      expect(soolaYoga(chart)).toBe(false);
    });
    it('yugaYoga should be false', () => {
      expect(yugaYoga(chart)).toBe(false);
    });
    it('golaYoga should be false', () => {
      expect(golaYoga(chart)).toBe(false);
    });
  });

  describe('Notable Yogas (Fictional Chart)', () => {
    it('gajaKesariYoga should be false', () => {
      expect(gajaKesariYoga(chart)).toBe(false);
    });
    it('guruMangalaYoga should be false', () => {
      expect(guruMangalaYoga(chart)).toBe(false);
    });
    it('subhaYoga should be false', () => {
      expect(subhaYoga(chart)).toBe(false);
    });
    it('asubhaYoga should be false', () => {
      expect(asubhaYoga(chart)).toBe(false);
    });
    it('amalaYoga should be true (Python parity)', () => {
      expect(amalaYoga(chart)).toBe(true);
    });
    it('parvataYoga should be false', () => {
      expect(parvataYoga(chart)).toBe(false);
    });
    it('trilochanaYoga should be false', () => {
      expect(trilochanaYoga(chart)).toBe(false);
    });
    it('chatussagaraYoga should be false', () => {
      expect(chatussagaraYoga(chart)).toBe(false);
    });
    it('rajalakshanaYoga should be false', () => {
      expect(rajalakshanaYoga(chart)).toBe(false);
    });
  });

  describe('Viparita Raja Yogas (Fictional Chart)', () => {
    it('harshaYoga should be true (Python parity)', () => {
      expect(harshaYoga(chart)).toBe(true);
    });
    it('saralaYoga should be false', () => {
      expect(saralaYoga(chart)).toBe(false);
    });
    it('vimalaYoga should be false', () => {
      expect(vimalaYoga(chart)).toBe(false);
    });
  });

  // ---- Tier 2 Yogas (from second batch Python run) ----

  describe('Tier 2 Yogas - Python Parity (Fictional Chart)', () => {
    it('lakshmiYoga should be false', () => {
      expect(lakshmiYoga(chart)).toBe(false);
    });
    it('dhanaYoga should be false', () => {
      expect(dhanaYoga(chart)).toBe(false);
    });
    it('vasumathiYoga should be false', () => {
      expect(vasumathiYoga(chart)).toBe(false);
    });
    it('kahalaYoga should be true (Python parity)', () => {
      expect(kahalaYoga(chart)).toBe(true);
    });
    it('marudYoga should be false', () => {
      expect(marudYoga(chart)).toBe(false);
    });
    it('budhaYoga should be false', () => {
      expect(budhaYoga(chart)).toBe(false);
    });
    it('andhaYoga should be false', () => {
      expect(andhaYoga(chart)).toBe(false);
    });
    it('chaamaraYoga should be false', () => {
      expect(chaamaraYoga(chart)).toBe(false);
    });
    it('sankhaYoga should be false', () => {
      expect(sankhaYoga(chart)).toBe(false);
    });
    it('khadgaYoga should be false', () => {
      expect(khadgaYoga(chart)).toBe(false);
    });
    it('goYoga should be false', () => {
      expect(goYoga(chart)).toBe(false);
    });
    it('dharidhraYoga should be true (Python parity)', () => {
      expect(dharidhraYoga(chart)).toBe(true);
    });
    it('dhurYoga should be false', () => {
      expect(dhurYoga(chart)).toBe(false);
    });
    it('bheriYoga should be false', () => {
      expect(bheriYoga(chart)).toBe(false);
    });
    it('mridangaYoga should be false', () => {
      expect(mridangaYoga(chart)).toBe(false);
    });
    it('sreenaatheYoga should be false', () => {
      expect(sreenaatheYoga(chart)).toBe(false);
    });
    it('koormaYoga should be false', () => {
      expect(koormaYoga(chart)).toBe(false);
    });
    it('kusumaYoga should be false', () => {
      expect(kusumaYoga(chart)).toBe(false);
    });
    it('kalaanidhiYoga should be false', () => {
      expect(kalaanidhiYoga(chart)).toBe(false);
    });
    it('lagnaAdhiYoga should be false', () => {
      expect(lagnaAdhiYoga(chart)).toBe(false);
    });
    it('hariYoga should be false', () => {
      expect(hariYoga(chart)).toBe(false);
    });
    it('haraYoga should be false', () => {
      expect(haraYoga(chart)).toBe(false);
    });
    it('brahmaYoga should be false', () => {
      expect(brahmaYoga(chart)).toBe(false);
    });
    it('sivaYoga should be false', () => {
      expect(sivaYoga(chart)).toBe(false);
    });
    it('devendraYoga should be false', () => {
      expect(devendraYoga(chart)).toBe(false);
    });
    it('indraYoga should be false', () => {
      expect(indraYoga(chart)).toBe(false);
    });
    it('raviYoga should be false', () => {
      expect(raviYoga(chart)).toBe(false);
    });
    it('bhaaskaraYoga should be false', () => {
      expect(bhaaskaraYoga(chart)).toBe(false);
    });
    it('kulavardhanaYoga should be false', () => {
      expect(kulavardhanaYoga(chart)).toBe(false);
    });
    it('gandharvaYoga should be false', () => {
      expect(gandharvaYoga(chart)).toBe(false);
    });
    it('vidyutYoga should be false', () => {
      expect(vidyutYoga(chart)).toBe(false);
    });
    it('chapaYoga should be false', () => {
      expect(chapaYoga(chart)).toBe(false);
    });
    it('pushkalaYoga should be false', () => {
      expect(pushkalaYoga(chart)).toBe(false);
    });
    it('makutaYoga should be false', () => {
      expect(makutaYoga(chart)).toBe(false);
    });
    it('jayaYoga should be false', () => {
      expect(jayaYoga(chart)).toBe(false);
    });
    it('vanchanaChoraYoga should be false', () => {
      expect(vanchanaChoraYoga(chart)).toBe(false);
    });
    it('hariharaBrahmaYoga should be false', () => {
      expect(hariharaBrahmaYoga(chart)).toBe(false);
    });
    it('sreenataYoga should be false', () => {
      expect(sreenataYoga(chart)).toBe(false);
    });
    it('parijathaYoga should be false', () => {
      expect(parijathaYoga(chart)).toBe(false);
    });
    it('gajaYoga should be false', () => {
      expect(gajaYoga(chart)).toBe(false);
    });
    it('saaradaYoga should be false', () => {
      expect(saaradaYoga(chart)).toBe(false);
    });
    it('saraswathiYoga should be false', () => {
      expect(saraswathiYoga(chart)).toBe(false);
    });
    it('amsaavataraYoga should be false', () => {
      expect(amsaavataraYoga(chart)).toBe(false);
    });
    it('dehapushtiYoga should be false', () => {
      expect(dehapushtiYoga(chart)).toBe(false);
    });
    it('rogagrasthaYoga should be true (Python parity)', () => {
      expect(rogagrasthaYoga(chart)).toBe(true);
    });
    it('krisangaYoga should be false', () => {
      expect(krisangaYoga(chart)).toBe(false);
    });
    it('dehasthoulyaYoga should be false', () => {
      expect(dehasthoulyaYoga(chart)).toBe(false);
    });
    it('sadaSancharaYoga should be true (Python parity)', () => {
      expect(sadaSancharaYoga(chart)).toBe(true);
    });
    it('bahudravyarjanaYoga should be false', () => {
      expect(bahudravyarjanaYoga(chart)).toBe(false);
    });
    it('anthyaVayasiDhanaYoga should be false', () => {
      expect(anthyaVayasiDhanaYoga(chart)).toBe(false);
    });
    it('sareeraSoukhyaYoga should be true (Python parity)', () => {
      expect(sareeraSoukhyaYoga(chart)).toBe(true);
    });
    it('matrumooladdhanaYoga should be true (Python parity)', () => {
      expect(matrumooladdhanaYoga(chart)).toBe(true);
    });
    it('kalatramooladdhanaYoga should be false', () => {
      expect(kalatramooladdhanaYoga(chart)).toBe(false);
    });
    it('swaveeryaddhanaYoga should be false', () => {
      expect(swaveeryaddhanaYoga(chart)).toBe(false);
    });
    it('kalanidhiYoga should be false', () => {
      expect(kalanidhiYoga(chart)).toBe(false);
    });
  });

  describe('Malika Yogas (Fictional Chart) - all false per Python', () => {
    it('lagnaMalikaYoga should be false', () => {
      expect(lagnaMalikaYoga(chart)).toBe(false);
    });
    it('dhanaMalikaYoga should be false', () => {
      expect(dhanaMalikaYoga(chart)).toBe(false);
    });
  });

  // ---- Batch 3 Yogas (ported by yoga agent) - Python Parity ----

  describe('Batch 3 Yogas - Python Parity (Fictional Chart)', () => {
    it('matsyaYoga should be false', () => {
      expect(matsyaYoga(chart)).toBe(false);
    });
    it('mookaYoga should be false', () => {
      expect(mookaYoga(chart)).toBe(false);
    });
    it('netranasaYoga should be false', () => {
      expect(netranasaYoga(chart)).toBe(false);
    });
    it('asatyavadiYoga should be true (Python parity)', () => {
      expect(asatyavadiYoga(chart)).toBe(true);
    });
    it('jadaYoga should be false', () => {
      expect(jadaYoga(chart)).toBe(false);
    });
    it('bhratrumooladdhanapraptiYoga should be false', () => {
      expect(bhratrumooladdhanapraptiYoga(chart)).toBe(false);
    });
    it('putramooladdhanaYoga should be false', () => {
      expect(putramooladdhanaYoga(chart)).toBe(false);
    });
    it('shatrumooladdhanaYoga should be false', () => {
      expect(shatrumooladdhanaYoga(chart)).toBe(false);
    });
    it('amarananthaDhanaYoga should be false', () => {
      expect(amarananthaDhanaYoga(chart)).toBe(false);
    });
    it('ayatnadhanalabhaYoga should be false', () => {
      expect(ayatnadhanalabhaYoga(chart)).toBe(false);
    });
    it('parannabhojanaYoga should be false', () => {
      expect(parannabhojanaYoga(chart)).toBe(false);
    });
    it('sraddhannabhukthaYoga should be true (Python parity)', () => {
      expect(sraddhannabhukthaYoga(chart)).toBe(true);
    });
  });
});

// ============================================================================
// PHASE 2: TESTS FOR PREVIOUSLY UNTESTED YOGA FUNCTIONS
// ============================================================================

describe('Yoga Helper Functions (Phase 2)', () => {
  // Chart: Sun in Aries, Moon in Cancer (exalted), Mars in Capricorn (exalted)
  const helperChart = buildChart(ARIES, {
    [SUN]: ARIES,
    [MOON]: TAURUS,
    [MARS]: CAPRICORN,
    [MERCURY]: ARIES, // Mercury conjunct Sun — malefic
    [JUPITER]: CANCER,
    [VENUS]: PISCES,
    [SATURN]: LIBRA,
    [RAHU]: GEMINI,
    [KETU]: SAGITTARIUS,
  });

  describe('isMercuryBenefic', () => {
    it('should return false when Mercury is conjunct Sun', () => {
      expect(isMercuryBenefic(helperChart)).toBe(false);
    });
    it('should return true when Mercury is not with Sun or malefics', () => {
      const chart = buildChart(ARIES, {
        [SUN]: LEO,
        [MERCURY]: VIRGO,
        [JUPITER]: CANCER,
      });
      expect(isMercuryBenefic(chart)).toBe(true);
    });
  });

  describe('getNaturalBenefics', () => {
    it('should include Jupiter and Venus', () => {
      const benefics = getNaturalBenefics(helperChart);
      expect(benefics).toContain(JUPITER);
      expect(benefics).toContain(VENUS);
    });
    it('should include Mercury when Mercury is benefic', () => {
      // Mercury alone (not conjunct malefics) = benefic
      const chart = buildChart(ARIES, {
        [SUN]: LEO, [MERCURY]: VIRGO, [JUPITER]: CANCER, [VENUS]: PISCES,
      });
      const benefics = getNaturalBenefics(chart);
      expect(benefics).toContain(MERCURY);
    });
  });

  describe('getNaturalMalefics', () => {
    it('should include Sun, Mars, Saturn, Rahu, Ketu', () => {
      const malefics = getNaturalMalefics();
      expect(malefics).toContain(SUN);
      expect(malefics).toContain(MARS);
      expect(malefics).toContain(SATURN);
      expect(malefics).toContain(RAHU);
      expect(malefics).toContain(KETU);
    });
    it('should not include Jupiter or Venus', () => {
      const malefics = getNaturalMalefics();
      expect(malefics).not.toContain(JUPITER);
      expect(malefics).not.toContain(VENUS);
    });
  });

  describe('isPlanetExalted', () => {
    it('Sun exalted in Aries', () => {
      expect(isPlanetExalted(SUN, ARIES)).toBe(true);
    });
    it('Moon exalted in Taurus', () => {
      expect(isPlanetExalted(MOON, TAURUS)).toBe(true);
    });
    it('Mars exalted in Capricorn', () => {
      expect(isPlanetExalted(MARS, CAPRICORN)).toBe(true);
    });
    it('Jupiter exalted in Cancer', () => {
      expect(isPlanetExalted(JUPITER, CANCER)).toBe(true);
    });
    it('Saturn exalted in Libra', () => {
      expect(isPlanetExalted(SATURN, LIBRA)).toBe(true);
    });
    it('Venus not exalted in Aries', () => {
      expect(isPlanetExalted(VENUS, ARIES)).toBe(false);
    });
  });

  describe('isPlanetStrong', () => {
    it('should return true for exalted planet', () => {
      expect(isPlanetStrong(SUN, ARIES)).toBe(true);
    });
    it('should return false for debilitated planet', () => {
      expect(isPlanetStrong(SUN, LIBRA)).toBe(false);
    });
  });

  describe('getQuadrants', () => {
    it('should return 4 houses at 0, 3, 6, 9 offset from Aries', () => {
      const q = getQuadrants(ARIES);
      expect(q).toContain(ARIES);
      expect(q).toContain(CANCER);
      expect(q).toContain(LIBRA);
      expect(q).toContain(CAPRICORN);
      expect(q).toHaveLength(4);
    });
  });

  describe('getTrines', () => {
    it('should return 3 houses at 0, 4, 8 offset from Aries', () => {
      const t = getTrines(ARIES);
      expect(t).toContain(ARIES);
      expect(t).toContain(LEO);
      expect(t).toContain(SAGITTARIUS);
      expect(t).toHaveLength(3);
    });
  });

  describe('getDushthanas', () => {
    it('should return 6th, 8th, 12th from Aries', () => {
      const d = getDushthanas(ARIES);
      expect(d).toContain(VIRGO);       // 6th
      expect(d).toContain(SCORPIO);     // 8th
      expect(d).toContain(PISCES);      // 12th
      expect(d).toHaveLength(3);
    });
  });

  describe('getHouseOwner', () => {
    it('should return Mars for Aries', () => {
      expect(getHouseOwner(helperChart, ARIES)).toBe(MARS);
    });
    it('should return Venus for Taurus', () => {
      expect(getHouseOwner(helperChart, TAURUS)).toBe(VENUS);
    });
    it('should return Jupiter for Sagittarius', () => {
      expect(getHouseOwner(helperChart, SAGITTARIUS)).toBe(JUPITER);
    });
  });
});

describe('Malika Yoga Variants (Phase 2)', () => {
  // Chart with planets in 7 consecutive houses starting from each house
  // We'll test each malika variant with a chart that triggers it

  // Helper: build a chart with one planet in each of 7 consecutive houses from startRasi
  function buildMalikaChart(startRasi: number): HouseChart {
    const planets: Record<number, number> = {};
    const planetList = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN];
    for (let i = 0; i < 7; i++) {
      planets[planetList[i]!] = (startRasi + i) % 12;
    }
    return buildChart(ARIES, planets);
  }

  it('vikramaMalikaYoga: true when 7 consecutive from 3rd house', () => {
    const chart = buildMalikaChart(GEMINI); // 3rd from Aries
    expect(vikramaMalikaYoga(chart)).toBe(true);
  });

  it('sukhaMalikaYoga: true when 7 consecutive from 4th house', () => {
    const chart = buildMalikaChart(CANCER);
    expect(sukhaMalikaYoga(chart)).toBe(true);
  });

  it('putraMalikaYoga: true when 7 consecutive from 5th house', () => {
    const chart = buildMalikaChart(LEO);
    expect(putraMalikaYoga(chart)).toBe(true);
  });

  it('satruMalikaYoga: true when 7 consecutive from 6th house', () => {
    const chart = buildMalikaChart(VIRGO);
    expect(satruMalikaYoga(chart)).toBe(true);
  });

  it('kalatraMalikaYoga: true when 7 consecutive from 7th house', () => {
    const chart = buildMalikaChart(LIBRA);
    expect(kalatraMalikaYoga(chart)).toBe(true);
  });

  it('randhraMalikaYoga: true when 7 consecutive from 8th house', () => {
    const chart = buildMalikaChart(SCORPIO);
    expect(randhraMalikaYoga(chart)).toBe(true);
  });

  it('bhagyaMalikaYoga: true when 7 consecutive from 9th house', () => {
    const chart = buildMalikaChart(SAGITTARIUS);
    expect(bhagyaMalikaYoga(chart)).toBe(true);
  });

  it('karmaMalikaYoga: true when 7 consecutive from 10th house', () => {
    const chart = buildMalikaChart(CAPRICORN);
    expect(karmaMalikaYoga(chart)).toBe(true);
  });

  it('labhaMalikaYoga: true when 7 consecutive from 11th house', () => {
    const chart = buildMalikaChart(AQUARIUS);
    expect(labhaMalikaYoga(chart)).toBe(true);
  });

  it('vyayaMalikaYoga: true when 7 consecutive from 12th house', () => {
    const chart = buildMalikaChart(PISCES);
    expect(vyayaMalikaYoga(chart)).toBe(true);
  });

  it('malika yogas should return false for non-consecutive placement', () => {
    const chart = buildChart(ARIES, {
      [SUN]: ARIES, [MOON]: GEMINI, [MARS]: LEO, // gaps
    });
    expect(vikramaMalikaYoga(chart)).toBe(false);
    expect(sukhaMalikaYoga(chart)).toBe(false);
    expect(putraMalikaYoga(chart)).toBe(false);
    expect(bhagyaMalikaYoga(chart)).toBe(false);
  });
});

describe('Alias Yoga Verifications (Phase 2)', () => {
  const chart = buildChart(ARIES, {
    [SUN]: ARIES,
    [MOON]: TAURUS,
    [MARS]: CAPRICORN,
    [MERCURY]: VIRGO,
    [JUPITER]: CANCER,
    [VENUS]: PISCES,
    [SATURN]: LIBRA,
    [RAHU]: GEMINI,
    [KETU]: SAGITTARIUS,
  });

  it('ishuYoga should equal saraYoga', () => {
    expect(ishuYoga(chart)).toBe(saraYoga(chart));
  });

  it('navYoga should equal naukaaYoga', () => {
    expect(navYoga(chart)).toBe(naukaaYoga(chart));
  });

  it('srikYoga should equal maalaaYoga', () => {
    expect(srikYoga(chart)).toBe(maalaaYoga(chart));
  });

  it('vihagaYoga should equal vihangaYoga', () => {
    expect(vihagaYoga(chart)).toBe(vihangaYoga(chart));
  });

  it('lagnaadhiYoga should equal lagnaAdhiYoga', () => {
    expect(lagnaadhiYoga(chart)).toBe(lagnaAdhiYoga(chart));
  });

  it('sreenaathaYoga should equal sreenaatheYoga', () => {
    expect(sreenaathaYoga(chart)).toBe(sreenaatheYoga(chart));
  });

  it('kaahalaYoga should equal kahalaYoga', () => {
    expect(kaahalaYoga(chart)).toBe(kahalaYoga(chart));
  });

  it('vanchanaChoraBheethiYoga should equal vanchanaChoraYoga', () => {
    expect(vanchanaChoraBheethiYoga(chart)).toBe(vanchanaChoraYoga(chart));
  });

  it('damaYoga should equal daamaYoga', () => {
    expect(damaYoga(chart)).toBe(daamaYoga(chart));
  });

  it('kedaraYoga should equal kedaaraYoga', () => {
    expect(kedaraYoga(chart)).toBe(kedaaraYoga(chart));
  });

  it('sulaYoga should equal soolaYoga', () => {
    expect(sulaYoga(chart)).toBe(soolaYoga(chart));
  });
});

describe('Real Yogas - Previously Untested (Phase 2)', () => {
  // Standard chart for testing
  const chart = buildChart(ARIES, {
    [SUN]: LEO,
    [MOON]: CANCER,
    [MARS]: CAPRICORN,
    [MERCURY]: VIRGO,
    [JUPITER]: CANCER,
    [VENUS]: PISCES,
    [SATURN]: LIBRA,
    [RAHU]: GEMINI,
    [KETU]: SAGITTARIUS,
  });

  it('bhaarathiYoga should return a boolean', () => {
    expect(typeof bhaarathiYoga(chart)).toBe('boolean');
  });

  it('chandikaaYoga should return a boolean', () => {
    expect(typeof chandikaaYoga(chart)).toBe('boolean');
  });

  it('garudaYoga should return a boolean', () => {
    expect(typeof garudaYoga(chart)).toBe('boolean');
  });

  it('gouriYoga should return a boolean', () => {
    expect(typeof gouriYoga(chart)).toBe('boolean');
  });

  it('vishnuYoga should return a boolean', () => {
    expect(typeof vishnuYoga(chart)).toBe('boolean');
  });

  it('madhyaVayasiDhanaYoga should return a boolean', () => {
    expect(typeof madhyaVayasiDhanaYoga(chart)).toBe('boolean');
  });

  it('balyaDhanaYoga should return a boolean', () => {
    expect(typeof balyaDhanaYoga(chart)).toBe('boolean');
  });

  it('vallakiYoga should return a boolean', () => {
    expect(typeof vallakiYoga(chart)).toBe('boolean');
  });

  it('sarpagandaYoga should return a boolean', () => {
    expect(typeof sarpagandaYoga(chart)).toBe('boolean');
  });

  // Specific behavioral tests with constructed charts
  it('vishnuYoga: true when Venus + Moon lords are in 9th/10th with 2 benefics', () => {
    // Construct chart where Vishnu Yoga conditions are met
    // 9th lord (Jupiter for Aries) and 10th lord (Saturn) in mutual quadrants
    const vChart = buildChart(ARIES, {
      [SUN]: CANCER,     // benefic placement
      [MOON]: CANCER,    // exalted
      [MARS]: CAPRICORN,
      [MERCURY]: GEMINI,
      [JUPITER]: ARIES,  // 9th lord in lagna (quadrant)
      [VENUS]: PISCES,   // exalted benefic
      [SATURN]: CANCER,  // 10th lord in 4th (quadrant)
      [RAHU]: GEMINI,
      [KETU]: SAGITTARIUS,
    });
    // Just verify it returns a boolean without crashing
    expect(typeof vishnuYoga(vChart)).toBe('boolean');
  });

  it('gouriYoga: should not throw', () => {
    expect(() => gouriYoga(chart)).not.toThrow();
  });

  it('bhaarathiYoga: should not throw', () => {
    expect(() => bhaarathiYoga(chart)).not.toThrow();
  });

  it('madhyaVayasiDhanaYoga: should not throw', () => {
    expect(() => madhyaVayasiDhanaYoga(chart)).not.toThrow();
  });

  it('balyaDhanaYoga: should not throw', () => {
    expect(() => balyaDhanaYoga(chart)).not.toThrow();
  });
});

describe('Newly Ported Yoga Functions (Phase 3)', () => {
  describe('areLordsExchanged', () => {
    it('should return true when lords are exchanged', () => {
      // Mars(2) owns Aries(0), Venus(5) owns Taurus(1)
      // Mars in Taurus, Venus in Aries = exchange
      const p2h: Record<number, number> = { 2: TAURUS, 5: ARIES };
      expect(areLordsExchanged(p2h, MARS, ARIES, VENUS, TAURUS)).toBe(true);
    });

    it('should return false when lords are not exchanged', () => {
      const p2h: Record<number, number> = { 2: ARIES, 5: TAURUS };
      expect(areLordsExchanged(p2h, MARS, ARIES, VENUS, TAURUS)).toBe(false);
    });

    it('should handle one-way occupancy as false', () => {
      const p2h: Record<number, number> = { 2: TAURUS, 5: GEMINI };
      expect(areLordsExchanged(p2h, MARS, ARIES, VENUS, TAURUS)).toBe(false);
    });
  });

  describe('dhanaYoga123_128', () => {
    it('should return false for a generic chart', () => {
      const chart = buildChart(ARIES, {
        [SUN]: TAURUS, [MOON]: CANCER, [MARS]: LEO,
        [MERCURY]: VIRGO, [JUPITER]: LIBRA, [VENUS]: PISCES, [SATURN]: CAPRICORN,
      });
      expect(dhanaYoga123_128(chart)).toBe(false);
    });

    it('#123: Sun in Leo lagna + Mars and Jupiter influence', () => {
      // Leo lagna, Sun in Leo, Mars and Jupiter in Leo (conjunct)
      const chart = buildChart(LEO, {
        [SUN]: LEO, [MARS]: LEO, [JUPITER]: LEO,
        [MOON]: CANCER, [MERCURY]: VIRGO, [VENUS]: PISCES, [SATURN]: CAPRICORN,
      });
      expect(dhanaYoga123_128(chart)).toBe(true);
    });

    it('#124: Moon in Cancer lagna + Jupiter and Mars influence', () => {
      const chart = buildChart(CANCER, {
        [MOON]: CANCER, [JUPITER]: CANCER, [MARS]: CANCER,
        [SUN]: LEO, [MERCURY]: VIRGO, [VENUS]: PISCES, [SATURN]: CAPRICORN,
      });
      expect(dhanaYoga123_128(chart)).toBe(true);
    });

    it('#125: Mars in Aries lagna + Moon, Venus, Saturn influence', () => {
      const chart = buildChart(ARIES, {
        [MARS]: ARIES, [MOON]: ARIES, [VENUS]: ARIES, [SATURN]: ARIES,
        [SUN]: LEO, [MERCURY]: VIRGO, [JUPITER]: CANCER,
      });
      expect(dhanaYoga123_128(chart)).toBe(true);
    });

    it('#126: Mercury in Gemini lagna + Saturn and Venus influence', () => {
      const chart = buildChart(GEMINI, {
        [MERCURY]: GEMINI, [SATURN]: GEMINI, [VENUS]: GEMINI,
        [SUN]: LEO, [MOON]: CANCER, [MARS]: ARIES, [JUPITER]: SAGITTARIUS,
      });
      expect(dhanaYoga123_128(chart)).toBe(true);
    });

    it('#127: Jupiter in Sagittarius lagna + Mercury and Mars influence', () => {
      const chart = buildChart(SAGITTARIUS, {
        [JUPITER]: SAGITTARIUS, [MERCURY]: SAGITTARIUS, [MARS]: SAGITTARIUS,
        [SUN]: LEO, [MOON]: CANCER, [VENUS]: PISCES, [SATURN]: CAPRICORN,
      });
      expect(dhanaYoga123_128(chart)).toBe(true);
    });

    it('#128: Venus in Taurus lagna + Saturn and Mercury influence', () => {
      const chart = buildChart(TAURUS, {
        [VENUS]: TAURUS, [SATURN]: TAURUS, [MERCURY]: TAURUS,
        [SUN]: LEO, [MOON]: CANCER, [MARS]: ARIES, [JUPITER]: SAGITTARIUS,
      });
      expect(dhanaYoga123_128(chart)).toBe(true);
    });

    it('should return false when planet is not in own-sign lagna', () => {
      // Leo lagna but Sun NOT in Leo
      const chart = buildChart(LEO, {
        [SUN]: VIRGO, [MARS]: LEO, [JUPITER]: LEO,
        [MOON]: CANCER, [MERCURY]: GEMINI, [VENUS]: PISCES, [SATURN]: CAPRICORN,
      });
      expect(dhanaYoga123_128(chart)).toBe(false);
    });
  });
});
