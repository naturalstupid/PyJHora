/**
 * Yoga (Astrological Combination) Calculations
 * Ported from PyJHora yoga.py
 * Contains 170+ yoga calculation functions
 */

import {
  SUN,
  MOON,
  MARS,
  MERCURY,
  JUPITER,
  VENUS,
  SATURN,
  RAHU,
  KETU,
  SUN_TO_SATURN,
  SUN_TO_KETU,
  ARIES,
  TAURUS,
  GEMINI,
  CANCER,
  LEO,
  VIRGO,
  LIBRA,
  SCORPIO,
  SAGITTARIUS,
  CAPRICORN,
  AQUARIUS,
  PISCES,
  MOVABLE_SIGNS,
  FIXED_SIGNS,
  DUAL_SIGNS,
  WATER_SIGNS,
  HOUSE_1,
  HOUSE_2,
  HOUSE_3,
  HOUSE_4,
  HOUSE_5,
  HOUSE_6,
  HOUSE_7,
  HOUSE_8,
  HOUSE_9,
  HOUSE_10,
  HOUSE_11,
  HOUSE_12,
  HOUSE_STRENGTHS_OF_PLANETS,
  STRENGTH_EXALTED,
  STRENGTH_FRIEND,
  STRENGTH_DEBILITATED,
  ASCENDANT_SYMBOL,
  MOOLA_TRIKONA_OF_PLANETS,
  GRAHA_DRISHTI,
  NATURAL_MALEFICS as CONST_NATURAL_MALEFICS,
  ODD_SIGNS,
  EVEN_SIGNS,
  COMPOUND_ADHIMITRA,
} from '../constants';

import type { PlanetPosition } from '../types';

import {
  getQuadrantsOfRaasi,
  getTrinesOfRaasi,
  getLordOfSign,
  getGrahaDrishtiPlanetsOfPlanet,
  getGrahaDrishtiRasisOfPlanet,
  getGrahaDrishtiHousesOfPlanet,
  getGrahaDrishtiOnPlanet,
  getRaasiDrishtiOfPlanet,
  getAspectedPlanetsOfRaasi,
  getUpachayasOfRaasi,
  getHouseOwnerFromChart,
} from './house';

// Derived constants matching Python
const DRY_SIGNS = [ARIES, TAURUS, GEMINI, LEO, VIRGO, SAGITTARIUS];
const DRY_PLANETS = [SUN, MARS, SATURN];
const WATERY_PLANETS = [MOON, VENUS];

// ============================================================================
// TYPES
// ============================================================================

/** House chart is an array of 12 strings, each containing planet IDs separated by '/' */
export type HouseChart = string[];

/** Planet to house mapping */
export type PlanetToHouseMap = Record<number | string, number>;

/** Detected yoga result */
export interface YogaResult {
  name: string;
  isPresent: boolean;
  planets?: number[];
  houses?: number[];
  description?: string;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get house of a planet from the chart (helper to avoid undefined issues)
 * @param pToH - Planet to house mapping
 * @param planet - Planet ID or symbol
 * @returns House index (0-11), defaults to 0 if not found
 */
const h = (pToH: PlanetToHouseMap, planet: number | string): number => {
  return pToH[planet] ?? 0;
};
const safeHouse = h;

/**
 * Convert house chart to planet-to-house dictionary
 */
export const getPlanetToHouseDict = (chart: HouseChart): PlanetToHouseMap => {
  const pToH: PlanetToHouseMap = {};
  chart.forEach((houseContent, houseIndex) => {
    if (!houseContent) return;
    const planets = houseContent.split('/').filter(Boolean);
    planets.forEach((p) => {
      if (p === ASCENDANT_SYMBOL) {
        pToH[ASCENDANT_SYMBOL] = houseIndex;
      } else {
        const planetId = parseInt(p, 10);
        if (!isNaN(planetId)) {
          pToH[planetId] = houseIndex;
        }
      }
    });
  });
  return pToH;
};

/**
 * Get planets in a specific house from chart
 */
export const getPlanetsInHouse = (chart: HouseChart, houseIndex: number): number[] => {
  const content = chart[houseIndex] || '';
  return content
    .split('/')
    .filter((p) => p && p !== ASCENDANT_SYMBOL)
    .map((p) => parseInt(p, 10))
    .filter((p) => !isNaN(p));
};

/**
 * Check if Mercury is acting as a benefic (alone or with Jupiter/Venus)
 */
export const isMercuryBenefic = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const mercuryHouse = h(pToH, MERCURY);
  const jupiterHouse = h(pToH, JUPITER);
  const venusHouse = h(pToH, VENUS);

  // Mercury with Jupiter
  if (mercuryHouse === jupiterHouse) return true;
  // Mercury with Venus
  if (mercuryHouse === venusHouse) return true;
  // Mercury alone in house
  const planetsInMercuryHouse = getPlanetsInHouse(chart, mercuryHouse);
  if (planetsInMercuryHouse.length === 1 && planetsInMercuryHouse[0] === MERCURY) {
    return true;
  }
  return false;
};

/**
 * Get natural benefics based on chart (Mercury conditional)
 */
export const getNaturalBenefics = (chart: HouseChart): number[] => {
  const benefics = [JUPITER, VENUS];
  if (isMercuryBenefic(chart)) {
    benefics.push(MERCURY);
  }
  return benefics;
};

/**
 * Get natural malefics
 */
export const getNaturalMalefics = (): number[] => {
  return [SUN, MARS, SATURN, RAHU, KETU];
};

/**
 * Check if planet is strong (exalted, own sign, or friend)
 */
export const isPlanetStrong = (
  planet: number,
  house: number,
  includeNeutral: boolean = false
): boolean => {
  const strength = HOUSE_STRENGTHS_OF_PLANETS[planet]?.[house] ?? 0;
  const threshold = includeNeutral ? 2 : STRENGTH_FRIEND; // 2 = neutral, 3 = friend
  return strength >= threshold;
};

/**
 * Check if planet is exalted
 */
export const isPlanetExalted = (planet: number, house: number): boolean => {
  const strength = HOUSE_STRENGTHS_OF_PLANETS[planet]?.[house] ?? 0;
  return strength === STRENGTH_EXALTED;
};

/**
 * Get quadrants of a house
 */
export const getQuadrants = (raasi: number): number[] => {
  return getQuadrantsOfRaasi(raasi);
};

/**
 * Get trines of a house
 */
export const getTrines = (raasi: number): number[] => {
  return getTrinesOfRaasi(raasi);
};

/**
 * Get dushthanas (6, 8, 12) from a house
 */
export const getDushthanas = (raasi: number): number[] => {
  return [
    (raasi + HOUSE_6) % 12,
    (raasi + HOUSE_8) % 12,
    (raasi + HOUSE_12) % 12,
  ];
};

/**
 * Get house owner/lord
 */
export const getHouseOwner = (chart: HouseChart, houseSign: number): number => {
  return getHouseOwnerFromChart(chart, houseSign);
};

// ============================================================================
// PLANET POSITIONS TO CHART CONVERSION
// ============================================================================

/**
 * Convert PlanetPosition[] to HouseChart (string[12]).
 * Mirrors Python's utils.get_house_planet_list_from_planet_positions.
 * A planet with planet === -1 is treated as the Ascendant (ASCENDANT_SYMBOL).
 * @param positions - Array of PlanetPosition objects
 * @returns HouseChart array of 12 strings
 */
export const planetPositionsToChart = (positions: PlanetPosition[]): HouseChart => {
  const chart: string[] = Array(12).fill('');
  for (const pos of positions) {
    const key = pos.planet === -1 ? ASCENDANT_SYMBOL : String(pos.planet);
    if (chart[pos.rasi] === '') {
      chart[pos.rasi] = key;
    } else {
      chart[pos.rasi] += '/' + key;
    }
  }
  return chart;
};

// ============================================================================
// SUN YOGAS
// ============================================================================

/**
 * Vesi Yoga: Planet other than Moon in 2nd house from Sun
 */
export const vesiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const sunHouse = h(pToH, SUN);
  const yogaHouse = (sunHouse + HOUSE_2) % 12;
  const planetsInHouse = getPlanetsInHouse(chart, yogaHouse);
  // Exclude Moon
  const validPlanets = planetsInHouse.filter((p) => p !== MOON);
  return validPlanets.length >= 1;
};

/**
 * Vosi Yoga: Planet other than Moon in 12th house from Sun
 */
export const vosiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const sunHouse = h(pToH, SUN);
  const yogaHouse = (sunHouse + HOUSE_12) % 12;
  const planetsInHouse = getPlanetsInHouse(chart, yogaHouse);
  const validPlanets = planetsInHouse.filter((p) => p !== MOON);
  return validPlanets.length >= 1;
};

/**
 * Ubhayachara Yoga: Planets other than Moon in both 2nd and 12th from Sun
 */
export const ubhayacharaYoga = (chart: HouseChart): boolean => {
  return vesiYoga(chart) && vosiYoga(chart);
};

/**
 * Nipuna/Budha-Aaditya Yoga: Sun and Mercury together
 */
export const nipunaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  return h(pToH, SUN) === h(pToH, MERCURY);
};
export const budhaAadityaYoga = nipunaYoga;

// ============================================================================
// MOON YOGAS
// ============================================================================

/**
 * Sunaphaa Yoga: Planets other than Sun in 2nd house from Moon
 */
export const sunaphaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const moonHouse = h(pToH, MOON);
  const yogaHouse = (moonHouse + HOUSE_2) % 12;
  const planetsInHouse = getPlanetsInHouse(chart, yogaHouse);
  const validPlanets = planetsInHouse.filter((p) => p !== SUN);
  return validPlanets.length >= 1;
};

/**
 * Anaphaa Yoga: Planets other than Sun in 12th house from Moon
 */
export const anaphaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const moonHouse = h(pToH, MOON);
  const yogaHouse = (moonHouse + HOUSE_12) % 12;
  const planetsInHouse = getPlanetsInHouse(chart, yogaHouse);
  const validPlanets = planetsInHouse.filter((p) => p !== SUN);
  return validPlanets.length >= 1;
};

/**
 * Duradhara/Dhurdhura Yoga: Planets other than Sun in both 2nd and 12th from Moon
 */
export const duradharaYoga = (chart: HouseChart): boolean => {
  return sunaphaaYoga(chart) && anaphaaYoga(chart);
};
export const dhurdhuraYoga = duradharaYoga;

/**
 * Kemadruma Yoga: No planets other than Sun in 1st, 2nd, 12th from Moon
 * AND no planets other than Moon in quadrants from lagna
 */
export const kemadrumaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const moonHouse = h(pToH, MOON);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);

  // Houses 1, 2, 12 from Moon
  const housesFromMoon = [moonHouse, (moonHouse + 1) % 12, (moonHouse + 11) % 12];

  // Planets in Moon zone - only Sun and Moon allowed
  const planetsInMoonZone = SUN_TO_KETU.filter(
    (p) => housesFromMoon.includes(h(pToH, p))
  );
  const ky1 = planetsInMoonZone.every((p) => p === MOON || p === SUN);

  // Quadrants from Lagna - only Moon allowed
  const quadrants = getQuadrants(lagnaHouse);
  const planetsInQuadrants = SUN_TO_KETU.filter((p) =>
    quadrants.includes(h(pToH, p))
  );
  const ky2 = planetsInQuadrants.every((p) => p === MOON);

  return ky1 && ky2;
};

/**
 * Chandra-Mangala Yoga: Moon and Mars together
 */
export const chandraMangalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  return h(pToH, MOON) === h(pToH, MARS);
};

/**
 * Adhi Yoga: Natural benefics in 6th, 7th, 8th from Moon
 */
export const adhiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const moonHouse = h(pToH, MOON);
  const yogaHouses = [
    (moonHouse + HOUSE_6) % 12,
    (moonHouse + HOUSE_7) % 12,
    (moonHouse + HOUSE_8) % 12,
  ];

  const naturalBenefics = getNaturalBenefics(chart);
  return naturalBenefics.every((p) => yogaHouses.includes(h(pToH, p)));
};

// ============================================================================
// PANCHA MAHAPURUSHA YOGAS
// ============================================================================

/**
 * Ruchaka Yoga: Mars in Aries, Scorpio, or Capricorn AND in quadrant from Lagna
 */
export const ruchakaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const marsHouse = h(pToH, MARS);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const yogaSigns = [ARIES, SCORPIO, CAPRICORN];
  const quadrants = getQuadrants(lagnaHouse);
  return yogaSigns.includes(marsHouse) && quadrants.includes(marsHouse);
};

/**
 * Bhadra Yoga: Mercury in Gemini or Virgo AND in quadrant from Lagna
 */
export const bhadraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const mercuryHouse = h(pToH, MERCURY);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const yogaSigns = [GEMINI, VIRGO];
  const quadrants = getQuadrants(lagnaHouse);
  return yogaSigns.includes(mercuryHouse) && quadrants.includes(mercuryHouse);
};

/**
 * Sasa Yoga: Saturn in Capricorn, Aquarius, or Libra AND in quadrant from Lagna
 */
export const sasaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const saturnHouse = h(pToH, SATURN);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const yogaSigns = [CAPRICORN, AQUARIUS, LIBRA];
  const quadrants = getQuadrants(lagnaHouse);
  return yogaSigns.includes(saturnHouse) && quadrants.includes(saturnHouse);
};

/**
 * Maalavya Yoga: Venus in Taurus, Libra, or Pisces AND in quadrant from Lagna
 */
export const maalavyaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const venusHouse = h(pToH, VENUS);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const yogaSigns = [TAURUS, LIBRA, PISCES];
  const quadrants = getQuadrants(lagnaHouse);
  return yogaSigns.includes(venusHouse) && quadrants.includes(venusHouse);
};

/**
 * Hamsa Yoga: Jupiter in Sagittarius, Pisces, or Cancer AND in quadrant from Lagna
 */
export const hamsaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const jupiterHouse = h(pToH, JUPITER);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const yogaSigns = [SAGITTARIUS, PISCES, CANCER];
  const quadrants = getQuadrants(lagnaHouse);
  return yogaSigns.includes(jupiterHouse) && quadrants.includes(jupiterHouse);
};

// ============================================================================
// NAABHASA / AASRAYA YOGAS
// ============================================================================

/**
 * Rajju Yoga: All planets exclusively in movable signs
 */
export const rajjuYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  return SUN_TO_KETU.every((p) => MOVABLE_SIGNS.includes(pToH[p]));
};

/**
 * Musala Yoga: All planets exclusively in fixed signs
 */
export const musalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  return SUN_TO_KETU.every((p) => FIXED_SIGNS.includes(pToH[p]));
};

/**
 * Nala Yoga: All planets exclusively in dual signs
 */
export const nalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  return SUN_TO_KETU.every((p) => DUAL_SIGNS.includes(pToH[p]));
};

// ============================================================================
// NAABHASA DALA YOGAS
// ============================================================================

/**
 * Maalaa/Srik Yoga: Three quadrants from Lagna occupied by natural benefics
 */
export const maalaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const kendras = getQuadrants(lagnaHouse);
  const naturalBenefics = getNaturalBenefics(chart);

  let occupiedBeneficKendras = 0;
  for (const h of kendras) {
    const planetsInHouse = getPlanetsInHouse(chart, h);
    if (planetsInHouse.some((p) => naturalBenefics.includes(p))) {
      occupiedBeneficKendras++;
    }
  }
  return occupiedBeneficKendras === 3;
};
export const srikYoga = maalaaYoga;

/**
 * Sarpa Yoga: Three quadrants from Lagna occupied by natural malefics
 */
export const sarpaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const kendras = getQuadrants(lagnaHouse);
  const naturalMalefics = getNaturalMalefics();

  let occupiedMaleficKendras = 0;
  for (const h of kendras) {
    const planetsInHouse = getPlanetsInHouse(chart, h);
    if (planetsInHouse.some((p) => naturalMalefics.includes(p))) {
      occupiedMaleficKendras++;
    }
  }
  return occupiedMaleficKendras === 3;
};

// ============================================================================
// AAKRITI YOGAS
// ============================================================================

/**
 * Gadaa Yoga: All planets in two successive quadrants from Lagna
 */
export const gadaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const quadrantHouses = [HOUSE_1, HOUSE_4, HOUSE_7, HOUSE_10];
  const quadrantPairs: [number, number][] = [];

  for (let i = 0; i < 4; i++) {
    const a = (ascHouse + quadrantHouses[i]) % 12;
    const b = (ascHouse + quadrantHouses[(i + 1) % 4]) % 12;
    quadrantPairs.push([Math.min(a, b), Math.max(a, b)] as [number, number]);
  }

  const planetHouses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  const sortedHouses = Array.from(planetHouses).sort((a, b) => a - b);

  if (sortedHouses.length !== 2) return false;

  const pair: [number, number] = [sortedHouses[0], sortedHouses[1]];
  return quadrantPairs.some(
    (qp) => qp[0] === pair[0] && qp[1] === pair[1]
  );
};

/**
 * Sakata Yoga: All planets in 1st and 7th houses from Lagna
 */
export const sakataYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_1) % 12,
    (ascHouse + HOUSE_7) % 12,
  ]);
  const planetHouses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return (
    planetHouses.size === 2 &&
    Array.from(planetHouses).every((h) => validHouses.has(h))
  );
};

/**
 * Vihanga Yoga: All planets in 4th and 10th houses from Lagna
 */
export const vihangaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_4) % 12,
    (ascHouse + HOUSE_10) % 12,
  ]);
  const planetHouses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return (
    planetHouses.size === 2 &&
    Array.from(planetHouses).every((h) => validHouses.has(h))
  );
};
export const vihagaYoga = vihangaYoga;

/**
 * Sringaataka Yoga: All planets in trines (1, 5, 9) from Lagna
 */
export const sringaatakaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const trikonasSet = new Set([
    (ascHouse + HOUSE_1) % 12,
    (ascHouse + HOUSE_5) % 12,
    (ascHouse + HOUSE_9) % 12,
  ]);
  const planetHouses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return (
    planetHouses.size === 3 &&
    Array.from(planetHouses).every((h) => trikonasSet.has(h))
  );
};

/**
 * Hala Yoga: All planets in mutual trines but not trines from Lagna
 */
export const halaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const trineGroups = [
    [
      (ascHouse + HOUSE_2) % 12,
      (ascHouse + HOUSE_6) % 12,
      (ascHouse + HOUSE_10) % 12,
    ],
    [
      (ascHouse + HOUSE_3) % 12,
      (ascHouse + HOUSE_7) % 12,
      (ascHouse + HOUSE_11) % 12,
    ],
    [
      (ascHouse + HOUSE_4) % 12,
      (ascHouse + HOUSE_8) % 12,
      (ascHouse + HOUSE_12) % 12,
    ],
  ];

  const planetHouses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));

  for (const group of trineGroups) {
    const groupSet = new Set(group);
    if (
      planetHouses.size === 3 &&
      Array.from(planetHouses).every((h) => groupSet.has(h))
    ) {
      return true;
    }
  }
  return false;
};

/**
 * Vajra Yoga: Benefics in 1st and 7th, malefics in 4th and 10th from Lagna
 */
export const vajraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const lagna = (ascHouse + HOUSE_1) % 12;
  const seventh = (ascHouse + HOUSE_7) % 12;
  const fourth = (ascHouse + HOUSE_4) % 12;
  const tenth = (ascHouse + HOUSE_10) % 12;

  const naturalBenefics = getNaturalBenefics(chart);
  const naturalMalefics = getNaturalMalefics();

  const anyInHouse = (planets: number[], house: number) =>
    planets.some((p) => pToH[p] === house);

  const beneficOk =
    anyInHouse(naturalBenefics, lagna) && anyInHouse(naturalBenefics, seventh);
  const maleficOk =
    anyInHouse(naturalMalefics, fourth) && anyInHouse(naturalMalefics, tenth);

  return beneficOk && maleficOk;
};

/**
 * Yava Yoga: Malefics in 1st and 7th, benefics in 4th and 10th from Lagna
 */
export const yavaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const lagna = (ascHouse + HOUSE_1) % 12;
  const seventh = (ascHouse + HOUSE_7) % 12;
  const fourth = (ascHouse + HOUSE_4) % 12;
  const tenth = (ascHouse + HOUSE_10) % 12;

  const naturalBenefics = getNaturalBenefics(chart);
  const naturalMalefics = getNaturalMalefics();

  const anyInHouse = (planets: number[], house: number) =>
    planets.some((p) => pToH[p] === house);

  const maleficOk =
    anyInHouse(naturalMalefics, lagna) && anyInHouse(naturalMalefics, seventh);
  const beneficOk =
    anyInHouse(naturalBenefics, fourth) && anyInHouse(naturalBenefics, tenth);

  return maleficOk && beneficOk;
};

/**
 * Kamala Yoga: All planets in quadrants (kendras) from Lagna
 */
export const kamalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const kendras = new Set(getQuadrants(ascHouse));
  return SUN_TO_SATURN.every((p) => kendras.has(pToH[p]));
};

/**
 * Vaapi Yoga: All planets in Panaparas (2,5,8,11) OR Apoklimas (3,6,9,12) from Lagna
 */
export const vaapiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const panaparas = new Set([
    (ascHouse + HOUSE_2) % 12,
    (ascHouse + HOUSE_5) % 12,
    (ascHouse + HOUSE_8) % 12,
    (ascHouse + HOUSE_11) % 12,
  ]);

  const apoklimas = new Set([
    (ascHouse + HOUSE_3) % 12,
    (ascHouse + HOUSE_6) % 12,
    (ascHouse + HOUSE_9) % 12,
    (ascHouse + HOUSE_12) % 12,
  ]);

  const allInPanaparas = SUN_TO_SATURN.every((p) => panaparas.has(pToH[p]));
  const allInApoklimas = SUN_TO_SATURN.every((p) => apoklimas.has(pToH[p]));

  return allInPanaparas || allInApoklimas;
};

/**
 * Yoopa Yoga: All planets in 1st, 2nd, 3rd, 4th houses from Lagna
 */
export const yoopaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_1) % 12,
    (ascHouse + HOUSE_2) % 12,
    (ascHouse + HOUSE_3) % 12,
    (ascHouse + HOUSE_4) % 12,
  ]);
  return SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
};

/**
 * Sara/Ishu Yoga: All planets in 4th, 5th, 6th, 7th houses from Lagna
 */
export const saraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_4) % 12,
    (ascHouse + HOUSE_5) % 12,
    (ascHouse + HOUSE_6) % 12,
    (ascHouse + HOUSE_7) % 12,
  ]);
  return SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
};
export const ishuYoga = saraYoga;

/**
 * Sakti Yoga: All planets in 7th, 8th, 9th, 10th houses from Lagna
 */
export const saktiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_7) % 12,
    (ascHouse + HOUSE_8) % 12,
    (ascHouse + HOUSE_9) % 12,
    (ascHouse + HOUSE_10) % 12,
  ]);
  return SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
};

/**
 * Danda Yoga: All planets in 10th, 11th, 12th, 1st houses from Lagna
 */
export const dandaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_10) % 12,
    (ascHouse + HOUSE_11) % 12,
    (ascHouse + HOUSE_12) % 12,
    (ascHouse + HOUSE_1) % 12,
  ]);
  return SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
};

/**
 * Naukaa/Nav Yoga: All 7 visible planets in 7 consecutive houses from Lagna
 */
export const naukaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const baseHouse = h(pToH, ASCENDANT_SYMBOL);
  const span7 = Array.from({ length: 7 }, (_, i) => (baseHouse + i) % 12);
  const span7Set = new Set(span7);

  // All visible planets in span
  const allInSpan = SUN_TO_SATURN.every((p) => span7Set.has(pToH[p]));
  if (!allInSpan) return false;

  // Each house in span must be occupied
  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return span7.every((h) => houseToVisible[h].size > 0);
};
export const navYoga = naukaaYoga;

/**
 * Koota Yoga: All planets in 7 signs from 4th house
 */
export const kootaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const baseHouse = (h(pToH, ASCENDANT_SYMBOL) + HOUSE_4) % 12;
  const span7 = Array.from({ length: 7 }, (_, i) => (baseHouse + i) % 12);
  const span7Set = new Set(span7);

  const allInSpan = SUN_TO_SATURN.every((p) => span7Set.has(pToH[p]));
  if (!allInSpan) return false;

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return span7.every((h) => houseToVisible[h].size > 0);
};

/**
 * Chatra Yoga: All planets in 7 signs from 7th house
 */
export const chatraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const baseHouse = (h(pToH, ASCENDANT_SYMBOL) + HOUSE_7) % 12;
  const span7 = Array.from({ length: 7 }, (_, i) => (baseHouse + i) % 12);
  const span7Set = new Set(span7);

  const allInSpan = SUN_TO_SATURN.every((p) => span7Set.has(pToH[p]));
  if (!allInSpan) return false;

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return span7.every((h) => houseToVisible[h].size > 0);
};

/**
 * Chaapa Yoga: All planets in 7 signs from 10th house
 */
export const chaapaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const baseHouse = (h(pToH, ASCENDANT_SYMBOL) + HOUSE_10) % 12;
  const span7 = Array.from({ length: 7 }, (_, i) => (baseHouse + i) % 12);
  const span7Set = new Set(span7);

  const allInSpan = SUN_TO_SATURN.every((p) => span7Set.has(pToH[p]));
  if (!allInSpan) return false;

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return span7.every((h) => houseToVisible[h].size > 0);
};

/**
 * Ardha Chandra Yoga: All 7 visible planets confined to 7 consecutive houses
 * starting from a non-Kendra (Panapara or Apoklima)
 */
export const ardhaChandraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  // Starting offsets: Panaparas (2,5,8,11) + Apoklimas (3,6,9,12)
  const startingOffsets = [
    HOUSE_2, HOUSE_5, HOUSE_8, HOUSE_11,
    HOUSE_3, HOUSE_6, HOUSE_9, HOUSE_12,
  ];

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  for (const offset of startingOffsets) {
    const startHouse = (ascHouse + offset) % 12;
    const span7 = Array.from({ length: 7 }, (_, i) => (startHouse + i) % 12);
    const span7Set = new Set(span7);

    const allInSpan = SUN_TO_SATURN.every((p) => span7Set.has(pToH[p]));
    if (!allInSpan) continue;

    const allOccupied = span7.every((h) => houseToVisible[h].size > 0);
    if (allOccupied) return true;
  }
  return false;
};

/**
 * Chakra Yoga: All planets in 1st, 3rd, 5th, 7th, 9th, 11th houses
 */
export const chakraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_1) % 12,
    (ascHouse + HOUSE_3) % 12,
    (ascHouse + HOUSE_5) % 12,
    (ascHouse + HOUSE_7) % 12,
    (ascHouse + HOUSE_9) % 12,
    (ascHouse + HOUSE_11) % 12,
  ]);

  const allInSpan = SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
  if (!allInSpan) return false;

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return Array.from(validHouses).every((h) => houseToVisible[h].size > 0);
};

/**
 * Samudra Yoga: All planets in 2nd, 4th, 6th, 8th, 10th, 12th houses
 */
export const samudraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const validHouses = new Set([
    (ascHouse + HOUSE_2) % 12,
    (ascHouse + HOUSE_4) % 12,
    (ascHouse + HOUSE_6) % 12,
    (ascHouse + HOUSE_8) % 12,
    (ascHouse + HOUSE_10) % 12,
    (ascHouse + HOUSE_12) % 12,
  ]);

  const allInSpan = SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
  if (!allInSpan) return false;

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return Array.from(validHouses).every((h) => houseToVisible[h].size > 0);
};

// ============================================================================
// SANKHYA YOGAS (Planet Distribution)
// ============================================================================

/**
 * Veenaa Yoga: 7 planets in exactly 7 distinct signs
 */
export const veenaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 7;
};

/**
 * Daama Yoga: 7 planets in exactly 6 distinct signs
 */
export const daamaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 6;
};

/**
 * Paasa Yoga: 7 planets in exactly 5 distinct signs
 */
export const paasaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 5;
};

/**
 * Kedaara Yoga: 7 planets in exactly 4 distinct signs
 */
export const kedaaraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 4;
};

/**
 * Soola Yoga: 7 planets in exactly 3 distinct signs
 */
export const soolaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 3;
};

/**
 * Yuga Yoga: 7 planets in exactly 2 distinct signs
 */
export const yugaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 2;
};

/**
 * Gola Yoga: All 7 planets in exactly 1 sign
 */
export const golaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const houses = new Set(SUN_TO_SATURN.map((p) => pToH[p]));
  return houses.size === 1;
};

// ============================================================================
// SUBHA / ASUBHA YOGAS
// ============================================================================

/**
 * Subha Yoga: Lagna has benefics OR is surrounded by benefics (12th and 2nd)
 */
export const subhaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const naturalBenefics = new Set(getNaturalBenefics(chart));
  const naturalMalefics = new Set(getNaturalMalefics());

  const planetsInHouse = (h: number) =>
    SUN_TO_KETU.filter((p) => pToH[p] === h);

  const houseHasOnlyBenefics = (h: number) => {
    const ps = planetsInHouse(h);
    return ps.length > 0 && ps.every((p) => naturalBenefics.has(p));
  };

  // Condition 1: Lagna has only benefics
  const cond1 = houseHasOnlyBenefics(lagnaHouse);

  // Condition 2: Surrounded by benefics (12th and 2nd both have only benefics)
  const h12 = (lagnaHouse + 11) % 12;
  const h2 = (lagnaHouse + 1) % 12;
  const cond2 = houseHasOnlyBenefics(h12) && houseHasOnlyBenefics(h2);

  return cond1 || cond2;
};

/**
 * Asubha Yoga: Lagna has malefics OR is surrounded by malefics (12th and 2nd)
 */
export const asubhaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const naturalMalefics = new Set(getNaturalMalefics());

  const planetsInHouse = (h: number) =>
    SUN_TO_KETU.filter((p) => pToH[p] === h);

  const houseHasOnlyMalefics = (h: number) => {
    const ps = planetsInHouse(h);
    return ps.length > 0 && ps.every((p) => naturalMalefics.has(p));
  };

  // Condition 1: Lagna has only malefics
  const cond1 = houseHasOnlyMalefics(lagnaHouse);

  // Condition 2: Surrounded by malefics
  const h12 = (lagnaHouse + 11) % 12;
  const h2 = (lagnaHouse + 1) % 12;
  const cond2 = houseHasOnlyMalefics(h12) && houseHasOnlyMalefics(h2);

  return cond1 || cond2;
};

// ============================================================================
// NOTABLE PLANETARY YOGAS
// ============================================================================

/**
 * Gaja Kesari Yoga: Jupiter in quadrant from Moon
 */
export const gajaKesariYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const moonHouse = h(pToH, MOON);
  const jupiterHouse = h(pToH, JUPITER);
  const quadrants = getQuadrants(moonHouse);

  // Condition 1: Jupiter in quadrant from Moon
  if (!quadrants.includes(jupiterHouse)) return false;

  // Condition 2: Jupiter not debilitated (in Capricorn)
  // Simplified check - Jupiter is strong
  const jupiterStrong = isPlanetStrong(JUPITER, jupiterHouse, true);

  return jupiterStrong;
};

/**
 * Guru-Mangala Yoga: Jupiter and Mars together OR in 7th from each other
 */
export const guruMangalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const marsHouse = h(pToH, MARS);
  const jupiterHouse = h(pToH, JUPITER);

  // Together
  if (marsHouse === jupiterHouse) return true;

  // In 7th from each other
  if (marsHouse === (jupiterHouse + HOUSE_7) % 12) return true;
  if (jupiterHouse === (marsHouse + HOUSE_7) % 12) return true;

  return false;
};

/**
 * Amala Yoga: Only natural benefics in 10th house from Lagna or Moon
 */
export const amalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const moonHouse = h(pToH, MOON);
  const naturalBenefics = getNaturalBenefics(chart);

  const lagnaTenth = (lagnaHouse + HOUSE_10) % 12;
  const moonTenth = (moonHouse + HOUSE_10) % 12;

  const beneficInLagnaTenth = naturalBenefics.some(
    (p) => pToH[p] === lagnaTenth
  );
  const beneficInMoonTenth = naturalBenefics.some((p) => pToH[p] === moonTenth);

  return beneficInLagnaTenth || beneficInMoonTenth;
};

/**
 * Parvata Yoga: Quadrants occupied only by benefics AND 7th/8th vacant or with benefics only
 */
export const parvataYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const naturalBenefics = new Set(getNaturalBenefics(chart));

  const quadrants = getQuadrants(ascHouse);
  const houses78 = [
    (ascHouse + HOUSE_7) % 12,
    (ascHouse + HOUSE_8) % 12,
  ];

  const houseHasOnlyBeneficsOrEmpty = (h: number) => {
    const planets = getPlanetsInHouse(chart, h);
    if (planets.length === 0) return true;
    return planets.every((p) => naturalBenefics.has(p));
  };

  const py1 = quadrants.every((q) => houseHasOnlyBeneficsOrEmpty(q));
  const py2 = houses78.every((h) => houseHasOnlyBeneficsOrEmpty(h));

  return py1 && py2;
};

// ============================================================================
// VIPARITA RAJA YOGAS
// ============================================================================

/**
 * Harsha Yoga: 6th lord occupies the 6th house
 */
export const harshaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const sixthSign = (ascHouse + HOUSE_6) % 12;
  const sixthLord = getHouseOwnerFromChart(chart, sixthSign);
  return h(pToH, sixthLord) === sixthSign;
};

/**
 * Sarala Yoga: 8th lord occupies the 8th house
 */
export const saralaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const eighthSign = (ascHouse + HOUSE_8) % 12;
  const eighthLord = getHouseOwnerFromChart(chart, eighthSign);
  return h(pToH, eighthLord) === eighthSign;
};

/**
 * Vimala Yoga: 12th lord occupies the 12th house
 */
export const vimalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const twelfthSign = (ascHouse + HOUSE_12) % 12;
  const twelfthLord = getHouseOwnerFromChart(chart, twelfthSign);
  return h(pToH, twelfthLord) === twelfthSign;
};

// ============================================================================
// CHATUSSAGARA AND OTHER YOGAS
// ============================================================================

/**
 * Chatussagara Yoga: All planets in all 4 quadrants (kendras)
 */
export const chatussagaraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const quadrants = getQuadrants(ascHouse);

  // Each quadrant must have at least one planet
  return quadrants.every((q) => {
    const planets = getPlanetsInHouse(chart, q);
    return planets.length > 0;
  });
};

/**
 * Rajalakshana Yoga: All planets in quadrants or trines
 */
export const rajalakshanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const quadrants = getQuadrants(ascHouse);
  const trines = getTrines(ascHouse);
  const validHouses = new Set([...quadrants, ...trines]);

  return SUN_TO_SATURN.every((p) => validHouses.has(pToH[p]));
};

// ============================================================================
// MALIKA YOGAS (Garland Pattern - 7 consecutive houses)
// ============================================================================

const malikaYogaBase = (chart: HouseChart, startingHouse: number): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const startHouse = (ascHouse + startingHouse) % 12;
  const span7 = Array.from({ length: 7 }, (_, i) => (startHouse + i) % 12);
  const span7Set = new Set(span7);

  const allInSpan = SUN_TO_SATURN.every((p) => span7Set.has(pToH[p]));
  if (!allInSpan) return false;

  const houseToVisible: Record<number, Set<number>> = {};
  for (let h = 0; h < 12; h++) houseToVisible[h] = new Set();
  for (const p of SUN_TO_SATURN) {
    houseToVisible[pToH[p]].add(p);
  }

  return span7.every((h) => houseToVisible[h].size > 0);
};

/** Lagna Malika: 7 consecutive from 1st house */
export const lagnaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_1);

/** Dhana Malika: 7 consecutive from 2nd house */
export const dhanaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_2);

/** Vikrama Malika: 7 consecutive from 3rd house */
export const vikramaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_3);

/** Sukha Malika: 7 consecutive from 4th house */
export const sukhaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_4);

/** Putra Malika: 7 consecutive from 5th house */
export const putraMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_5);

/** Satru Malika: 7 consecutive from 6th house */
export const satruMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_6);

/** Kalatra Malika: 7 consecutive from 7th house */
export const kalatraMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_7);

/** Randhra Malika: 7 consecutive from 8th house */
export const randhraMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_8);

/** Bhagya Malika: 7 consecutive from 9th house */
export const bhagyaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_9);

/** Karma Malika: 7 consecutive from 10th house */
export const karmaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_10);

/** Labha Malika: 7 consecutive from 11th house */
export const labhaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_11);

/** Vyaya Malika: 7 consecutive from 12th house */
export const vyayaMalikaYoga = (chart: HouseChart): boolean =>
  malikaYogaBase(chart, HOUSE_12);

// ============================================================================
// FROM PLANET POSITIONS VARIANTS
// ============================================================================
// Each function converts PlanetPosition[] to HouseChart and delegates to the
// chart-based function. Mirrors Python's *_from_planet_positions functions.

/** Vesi Yoga from planet positions */
export const vesiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vesiYoga(planetPositionsToChart(positions));

/** Vosi Yoga from planet positions */
export const vosiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vosiYoga(planetPositionsToChart(positions));

/** Ubhayachara Yoga from planet positions */
export const ubhayacharaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  ubhayacharaYoga(planetPositionsToChart(positions));

/** Nipuna Yoga from planet positions */
export const nipunaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  nipunaYoga(planetPositionsToChart(positions));

/** Budha-Aaditya Yoga from planet positions */
export const budhaAadityaYogaFromPlanetPositions = nipunaYogaFromPlanetPositions;

/** Sunaphaa Yoga from planet positions */
export const sunaphaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sunaphaaYoga(planetPositionsToChart(positions));

/** Anaphaa Yoga from planet positions */
export const anaphaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  anaphaaYoga(planetPositionsToChart(positions));

/** Duradhara Yoga from planet positions */
export const duradharaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  duradharaYoga(planetPositionsToChart(positions));

/** Dhurdhura Yoga from planet positions */
export const dhurdhuraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dhurdhuraYoga(planetPositionsToChart(positions));

/** Kemadruma Yoga from planet positions */
export const kemadrumaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kemadrumaYoga(planetPositionsToChart(positions));

/** Chandra-Mangala Yoga from planet positions */
export const chandraMangalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chandraMangalaYoga(planetPositionsToChart(positions));

/** Adhi Yoga from planet positions */
export const adhiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  adhiYoga(planetPositionsToChart(positions));

/** Ruchaka Yoga from planet positions */
export const ruchakaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  ruchakaYoga(planetPositionsToChart(positions));

/** Bhadra Yoga from planet positions */
export const bhadraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bhadraYoga(planetPositionsToChart(positions));

/** Sasa Yoga from planet positions */
export const sasaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sasaYoga(planetPositionsToChart(positions));

/** Maalavya Yoga from planet positions */
export const maalavyaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  maalavyaYoga(planetPositionsToChart(positions));

/** Hamsa Yoga from planet positions */
export const hamsaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  hamsaYoga(planetPositionsToChart(positions));

/** Rajju Yoga from planet positions */
export const rajjuYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  rajjuYoga(planetPositionsToChart(positions));

/** Musala Yoga from planet positions */
export const musalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  musalaYoga(planetPositionsToChart(positions));

/** Nala Yoga from planet positions */
export const nalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  nalaYoga(planetPositionsToChart(positions));

/** Maalaa/Srik Yoga from planet positions */
export const maalaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  maalaaYoga(planetPositionsToChart(positions));

/** Srik Yoga from planet positions */
export const srikYogaFromPlanetPositions = maalaaYogaFromPlanetPositions;

/** Sarpa Yoga from planet positions */
export const sarpaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sarpaYoga(planetPositionsToChart(positions));

/** Gadaa Yoga from planet positions */
export const gadaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  gadaaYoga(planetPositionsToChart(positions));

/** Sakata Yoga from planet positions */
export const sakataYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sakataYoga(planetPositionsToChart(positions));

/** Vihanga Yoga from planet positions */
export const vihangaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vihangaYoga(planetPositionsToChart(positions));

/** Vihaga Yoga from planet positions */
export const vihagaYogaFromPlanetPositions = vihangaYogaFromPlanetPositions;

/** Sringaataka Yoga from planet positions */
export const sringaatakaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sringaatakaYoga(planetPositionsToChart(positions));

/** Hala Yoga from planet positions */
export const halaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  halaYoga(planetPositionsToChart(positions));

/** Vajra Yoga from planet positions */
export const vajraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vajraYoga(planetPositionsToChart(positions));

/** Yava Yoga from planet positions */
export const yavaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  yavaYoga(planetPositionsToChart(positions));

/** Kamala Yoga from planet positions */
export const kamalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kamalaYoga(planetPositionsToChart(positions));

/** Vaapi Yoga from planet positions */
export const vaapiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vaapiYoga(planetPositionsToChart(positions));

/** Yoopa Yoga from planet positions */
export const yoopaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  yoopaYoga(planetPositionsToChart(positions));

/** Sara Yoga from planet positions */
export const saraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  saraYoga(planetPositionsToChart(positions));

/** Ishu Yoga from planet positions */
export const ishuYogaFromPlanetPositions = saraYogaFromPlanetPositions;

/** Sakti Yoga from planet positions */
export const saktiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  saktiYoga(planetPositionsToChart(positions));

/** Danda Yoga from planet positions */
export const dandaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dandaYoga(planetPositionsToChart(positions));

/** Naukaa Yoga from planet positions */
export const naukaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  naukaaYoga(planetPositionsToChart(positions));

/** Nav Yoga from planet positions */
export const navYogaFromPlanetPositions = naukaaYogaFromPlanetPositions;

/** Koota Yoga from planet positions */
export const kootaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kootaYoga(planetPositionsToChart(positions));

/** Chatra Yoga from planet positions */
export const chatraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chatraYoga(planetPositionsToChart(positions));

/** Chaapa Yoga from planet positions */
export const chaapaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chaapaYoga(planetPositionsToChart(positions));

/** Ardha Chandra Yoga from planet positions */
export const ardhaChandraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  ardhaChandraYoga(planetPositionsToChart(positions));

/** Chakra Yoga from planet positions */
export const chakraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chakraYoga(planetPositionsToChart(positions));

/** Samudra Yoga from planet positions */
export const samudraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  samudraYoga(planetPositionsToChart(positions));

/** Veenaa Yoga from planet positions */
export const veenaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  veenaaYoga(planetPositionsToChart(positions));

/** Daama Yoga from planet positions */
export const daamaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  daamaYoga(planetPositionsToChart(positions));

/** Paasa Yoga from planet positions */
export const paasaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  paasaYoga(planetPositionsToChart(positions));

/** Kedaara Yoga from planet positions */
export const kedaaraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kedaaraYoga(planetPositionsToChart(positions));

/** Soola Yoga from planet positions */
export const soolaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  soolaYoga(planetPositionsToChart(positions));

/** Yuga Yoga from planet positions */
export const yugaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  yugaYoga(planetPositionsToChart(positions));

/** Gola Yoga from planet positions */
export const golaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  golaYoga(planetPositionsToChart(positions));

/** Subha Yoga from planet positions */
export const subhaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  subhaYoga(planetPositionsToChart(positions));

/** Asubha Yoga from planet positions */
export const asubhaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  asubhaYoga(planetPositionsToChart(positions));

/** Gaja Kesari Yoga from planet positions */
export const gajaKesariYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  gajaKesariYoga(planetPositionsToChart(positions));

/** Guru-Mangala Yoga from planet positions */
export const guruMangalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  guruMangalaYoga(planetPositionsToChart(positions));

/** Amala Yoga from planet positions */
export const amalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  amalaYoga(planetPositionsToChart(positions));

/** Parvata Yoga from planet positions */
export const parvataYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  parvataYoga(planetPositionsToChart(positions));

/** Harsha Yoga from planet positions */
export const harshaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  harshaYoga(planetPositionsToChart(positions));

/** Sarala Yoga from planet positions */
export const saralaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  saralaYoga(planetPositionsToChart(positions));

/** Vimala Yoga from planet positions */
export const vimalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vimalaYoga(planetPositionsToChart(positions));

/** Chatussagara Yoga from planet positions */
export const chatussagaraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chatussagaraYoga(planetPositionsToChart(positions));

/** Rajalakshana Yoga from planet positions */
export const rajalakshanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  rajalakshanaYoga(planetPositionsToChart(positions));

/** Trilochana Yoga from planet positions */
export const trilochanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  trilochanaYoga(planetPositionsToChart(positions));

/** Mahabhagya Yoga from planet positions */
export const mahabhagyaYogaFromPlanetPositions = (
  positions: PlanetPosition[],
  gender: 'male' | 'female' = 'male',
  isDayBirth: boolean = true
): boolean =>
  mahabhagyaYoga(planetPositionsToChart(positions), gender, isDayBirth);

/** Kahala Yoga from planet positions */
export const kahalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kahalaYoga(planetPositionsToChart(positions));

/** Lagna Malika Yoga from planet positions */
export const lagnaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  lagnaMalikaYoga(planetPositionsToChart(positions));

/** Dhana Malika Yoga from planet positions */
export const dhanaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dhanaMalikaYoga(planetPositionsToChart(positions));

/** Vikrama Malika Yoga from planet positions */
export const vikramaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vikramaMalikaYoga(planetPositionsToChart(positions));

/** Sukha Malika Yoga from planet positions */
export const sukhaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sukhaMalikaYoga(planetPositionsToChart(positions));

/** Putra Malika Yoga from planet positions */
export const putraMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  putraMalikaYoga(planetPositionsToChart(positions));

/** Satru Malika Yoga from planet positions */
export const satruMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  satruMalikaYoga(planetPositionsToChart(positions));

/** Kalatra Malika Yoga from planet positions */
export const kalatraMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kalatraMalikaYoga(planetPositionsToChart(positions));

/** Randhra Malika Yoga from planet positions */
export const randhraMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  randhraMalikaYoga(planetPositionsToChart(positions));

/** Bhagya Malika Yoga from planet positions */
export const bhagyaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bhagyaMalikaYoga(planetPositionsToChart(positions));

/** Karma Malika Yoga from planet positions */
export const karmaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  karmaMalikaYoga(planetPositionsToChart(positions));

/** Labha Malika Yoga from planet positions */
export const labhaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  labhaMalikaYoga(planetPositionsToChart(positions));

/** Vyaya Malika Yoga from planet positions */
export const vyayaMalikaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vyayaMalikaYoga(planetPositionsToChart(positions));

// ============================================================================
// LAKSHMI & WEALTH YOGAS
// ============================================================================

/**
 * Lakshmi Yoga: 9th lord strong and in quadrant/trine, Venus strong in own/exaltation
 */
export const lakshmiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ninthSign = (ascHouse + HOUSE_9) % 12;
  const ninthLord = getLordOfSign(ninthSign);
  const ninthLordHouse = pToH[ninthLord];

  const quadrantsAndTrines = new Set([
    ...getQuadrants(ascHouse),
    ...getTrines(ascHouse),
  ]);

  // 9th lord in quadrant/trine and strong
  if (!quadrantsAndTrines.has(ninthLordHouse)) return false;
  if (!isPlanetStrong(ninthLord, ninthLordHouse)) return false;

  // Venus strong
  const venusHouse = h(pToH, VENUS);
  if (!isPlanetStrong(VENUS, venusHouse)) return false;

  return true;
};

/**
 * Dhana Yoga: Lords of 2nd and 11th in favorable positions
 */
export const dhanaYoga = (chart: HouseChart): boolean => {
  // BV Raman #118-122: Specific 5th/11th house combinations
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h5 = (ascHouse + HOUSE_5) % 12;
  const h11 = (ascHouse + HOUSE_11) % 12;

  // 118: 5th is Venus sign, Venus in 5th, Saturn in 11th
  if ((h5 === TAURUS || h5 === LIBRA) && h(pToH, VENUS) === h5 && h(pToH, SATURN) === h11) return true;
  // 119: 5th is Mercury sign, Mercury in 5th, Moon & Mars in 11th
  if ((h5 === GEMINI || h5 === VIRGO) && h(pToH, MERCURY) === h5 && h(pToH, MOON) === h11 && h(pToH, MARS) === h11) return true;
  // 120: 5th is Saturn sign, Saturn in 5th, Mercury & Mars in 11th
  if ((h5 === CAPRICORN || h5 === AQUARIUS) && h(pToH, SATURN) === h5 && h(pToH, MERCURY) === h11 && h(pToH, MARS) === h11) return true;
  // 121: 5th is Sun sign (Leo), Sun in 5th, Jupiter & Moon in 11th
  if (h5 === LEO && h(pToH, SUN) === h5 && h(pToH, JUPITER) === h11 && h(pToH, MOON) === h11) return true;
  // 122: 5th is Jupiter sign, Jupiter in 5th, Mars & Moon in 11th
  if ((h5 === SAGITTARIUS || h5 === PISCES) && h(pToH, JUPITER) === h5 && h(pToH, MARS) === h11 && h(pToH, MOON) === h11) return true;

  return false;
};

/**
 * Vasumathi Yoga: Benefics in upachayas (3, 6, 10, 11) from Moon
 */
export const vasumathiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const moonHouse = h(pToH, MOON);
  const upachayas = [
    (moonHouse + HOUSE_3) % 12,
    (moonHouse + HOUSE_6) % 12,
    (moonHouse + HOUSE_10) % 12,
    (moonHouse + HOUSE_11) % 12,
  ];
  const naturalBenefics = getNaturalBenefics(chart);

  // At least one benefic in each upachaya
  return upachayas.every((u) =>
    naturalBenefics.some((b) => h(pToH, b) === u)
  );
};

// ============================================================================
// RAJA YOGAS
// ============================================================================

/**
 * Kahala Yoga: 4th lord and Jupiter in mutual quadrants, Lagna lord strong
 */
export const kahalaYoga = (chart: HouseChart): boolean => {
  // Kahala Yoga: L4 and L9 in mutual kendras, and L1 is strong (in kendra/trine from lagna)
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const lagnaLord = getLordOfSign(ascHouse);
  const fourthLord = getLordOfSign((ascHouse + HOUSE_4) % 12);
  const ninthLord = getLordOfSign((ascHouse + HOUSE_9) % 12);

  // L1 must be in kendra or trine from lagna
  const l1H = h(pToH, lagnaLord);
  const strongHouses = [...getQuadrants(ascHouse), ...getTrines(ascHouse)];
  if (!strongHouses.includes(l1H)) return false;

  // L4 and L9 in mutual kendras
  const l4H = h(pToH, fourthLord);
  const l9H = h(pToH, ninthLord);
  const relativePos = (l9H - l4H + 12) % 12;
  return [HOUSE_1, HOUSE_4, HOUSE_7, HOUSE_10].includes(relativePos);
};

// ============================================================================
// SPECIAL YOGAS
// ============================================================================

/**
 * Trilochana Yoga: Sun, Moon, Mars in trines from each other
 */
export const trilochanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const sunHouse = h(pToH, SUN);
  const moonHouse = h(pToH, MOON);
  const marsHouse = h(pToH, MARS);

  // Check if all three are in mutual trines
  const sunTrines = getTrines(sunHouse);

  return sunTrines.includes(moonHouse) && sunTrines.includes(marsHouse);
};

/**
 * Mahabhagya Yoga: Special yoga based on gender and birth time
 * Male: Sun, Moon, Lagna in odd signs (day birth)
 * Female: Sun, Moon, Lagna in even signs (night birth)
 */
export const mahabhagyaYoga = (
  chart: HouseChart,
  gender: 'male' | 'female' = 'male',
  isDayBirth: boolean = true
): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const sunHouse = h(pToH, SUN);
  const moonHouse = h(pToH, MOON);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);

  const oddSigns = new Set([0, 2, 4, 6, 8, 10]);
  const evenSigns = new Set([1, 3, 5, 7, 9, 11]);

  if (gender === 'male' && isDayBirth) {
    return (
      oddSigns.has(sunHouse) &&
      oddSigns.has(moonHouse) &&
      oddSigns.has(lagnaHouse)
    );
  } else if (gender === 'female' && !isDayBirth) {
    return (
      evenSigns.has(sunHouse) &&
      evenSigns.has(moonHouse) &&
      evenSigns.has(lagnaHouse)
    );
  }

  return false;
};

// ============================================================================
// FROM PLANET POSITIONS VARIANTS (WEALTH & RAJA YOGAS)
// ============================================================================

/** Lakshmi Yoga from planet positions */
export const lakshmiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  lakshmiYoga(planetPositionsToChart(positions));

/** Dhana Yoga from planet positions */
export const dhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dhanaYoga(planetPositionsToChart(positions));

/** Vasumathi Yoga from planet positions */
export const vasumathiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vasumathiYoga(planetPositionsToChart(positions));

// ============================================================================
// PORTED YOGAS: marud, budha, andha, chaamara, sankha, khadga, go, dharidhra
// ============================================================================

/**
 * Helper: get relative house number (1-based) of planet_house from from_house.
 * Mirrors Python: house.get_relative_house_of_planet = lambda from_house, planet_house: (planet_house + 12 - from_house) % 12 + 1
 */
const getRelativeHouse = (fromHouse: number, planetHouse: number): number => {
  return (planetHouse + 12 - fromHouse) % 12 + 1;
};

/**
 * Marud Yoga: Jupiter in 5th or 9th from Venus, Moon in 5th from Jupiter,
 * Sun in a kendra from Moon.
 */
export const marudYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);

  // 1. Jupiter in 5th or 9th from Venus
  const jupFromVen = getRelativeHouse(h(pToH, VENUS), h(pToH, JUPITER));
  const cond1 = jupFromVen === 5 || jupFromVen === 9;

  // 2. Moon in 5th from Jupiter
  const moonFromJup = getRelativeHouse(h(pToH, JUPITER), h(pToH, MOON));
  const cond2 = moonFromJup === 5;

  // 3. Sun in a kendra (1,4,7,10) from Moon
  const sunHouse = h(pToH, SUN);
  const moonHouse = h(pToH, MOON);
  const cond3 = getQuadrants(moonHouse).includes(sunHouse);

  return cond1 && cond2 && cond3;
};

export const marudYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  marudYoga(planetPositionsToChart(positions));

/**
 * Budha Yoga: Jupiter in Lagna, Moon in a kendra from Lagna,
 * Rahu in 2nd from Moon, Sun and Mars in 3rd from Rahu.
 */
export const budhaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  // 1. Jupiter in Lagna
  const jupiterInLagna = h(pToH, JUPITER) === ascHouse;

  // 2. Moon in a kendra from Lagna
  const moonInKendra = getQuadrants(ascHouse).includes(h(pToH, MOON));

  // 3. Rahu in 2nd from Moon
  const rahuFromMoon = getRelativeHouse(h(pToH, MOON), h(pToH, RAHU));
  const rahu2ndFromMoon = rahuFromMoon === 2;

  // 4. Sun and Mars in 3rd from Rahu
  const sunFromRahu = getRelativeHouse(h(pToH, RAHU), h(pToH, SUN));
  const marsFromRahu = getRelativeHouse(h(pToH, RAHU), h(pToH, MARS));
  const sunMars3rdFromRahu = sunFromRahu === 3 && marsFromRahu === 3;

  return jupiterInLagna && moonInKendra && rahu2ndFromMoon && sunMars3rdFromRahu;
};

export const budhaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  budhaYoga(planetPositionsToChart(positions));

/**
 * Andha Yoga: Mercury and Moon in 2nd house, OR lords of Lagna and 2nd
 * join the 2nd house with the Sun.
 */
export const andhaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const lagnaHouse = h(pToH, ASCENDANT_SYMBOL);
  const house2 = (lagnaHouse + 1) % 12;

  // Condition 1: Mercury and Moon both in 2nd house
  const cond1 = h(pToH, MERCURY) === house2 && h(pToH, MOON) === house2;

  // Condition 2: Lords of Lagna and 2nd in 2nd house with Sun
  const lordOfLagna = getLordOfSign(lagnaHouse);
  const lordOf2 = getLordOfSign(house2);
  const cond2 =
    h(pToH, lordOfLagna) === house2 &&
    h(pToH, lordOf2) === house2 &&
    h(pToH, SUN) === house2;

  return cond1 || cond2;
};

export const andhaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  andhaYoga(planetPositionsToChart(positions));

/**
 * Chaamara Yoga: Two benefics conjoin in Lagna, 7th, 9th, or 10th house,
 * OR lagna lord is exalted in a kendra and aspected by Jupiter.
 */
export const chaamaraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const naturalBenefics = getNaturalBenefics(chart);

  // Target houses: 7th, 9th, 10th from Lagna
  const targets = [
    (ascHouse + HOUSE_7) % 12,
    (ascHouse + HOUSE_9) % 12,
    (ascHouse + HOUSE_10) % 12,
  ];

  // Check if two or more benefics are in any of the target houses
  const twoBeneficsJoin = targets.some((t) => {
    const planetsInHouse = getPlanetsInHouse(chart, t);
    const beneficCount = planetsInHouse.filter((p) => naturalBenefics.includes(p)).length;
    return beneficCount >= 2;
  });

  if (twoBeneficsJoin) return true;

  // Alternative: Lagna lord exalted in kendra, aspected by Jupiter
  const lagnaLord = getLordOfSign(ascHouse);
  const lagnaLordHouse = h(pToH, lagnaLord);
  const lagnaLordInKendra = getQuadrants(ascHouse).includes(lagnaLordHouse);
  const lagnaLordIsExalted = isPlanetExalted(lagnaLord, lagnaLordHouse);

  // Jupiter's aspected signs (using GRAHA_DRISHTI 0-based offsets)
  const jupiterHouse = h(pToH, JUPITER);
  const jupiterDrishtiOffsets = GRAHA_DRISHTI[JUPITER] ?? [];
  const jupiterAspectedSigns = jupiterDrishtiOffsets.map(
    (offset) => (offset + jupiterHouse) % 12
  );
  const jupiterAspectsLagnaLordHouse = jupiterAspectedSigns.includes(lagnaLordHouse);

  return lagnaLordInKendra && jupiterAspectsLagnaLordHouse && lagnaLordIsExalted;
};

export const chaamaraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chaamaraYoga(planetPositionsToChart(positions));

/**
 * Sankha Yoga:
 * Path 1: Lagna lord strong AND 5th & 6th lords in mutual quadrants.
 * Path 2: Lagna lord & 10th lord together in a movable sign AND 9th lord strong.
 */
export const sankhaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const lagnaLord = getLordOfSign(ascHouse);
  const fifthLord = getLordOfSign((ascHouse + HOUSE_5) % 12);
  const sixthLord = getLordOfSign((ascHouse + HOUSE_6) % 12);
  const ninthLord = getLordOfSign((ascHouse + HOUSE_9) % 12);
  const tenthLord = getLordOfSign((ascHouse + HOUSE_10) % 12);

  // Path 1
  const lagnaLordHouse = h(pToH, lagnaLord);
  const lagnaLordStrong = isPlanetStrong(lagnaLord, lagnaLordHouse);
  const fifthLordHouse = h(pToH, fifthLord);
  const sixthLordHouse = h(pToH, sixthLord);
  const mutualKendras =
    getQuadrants(sixthLordHouse).includes(fifthLordHouse) &&
    getQuadrants(fifthLordHouse).includes(sixthLordHouse);

  // Path 2
  const ninthLordHouse = h(pToH, ninthLord);
  const ninthLordStrong = isPlanetStrong(ninthLord, ninthLordHouse);
  const tenthLordHouse = h(pToH, tenthLord);
  const conjunct = lagnaLordHouse === tenthLordHouse;
  // Python: conj_sign_index = (asc_house + conj_house) % 12 where conj_house = lagna_lord_house
  // Faithfully replicate the Python formula
  const conjSignIndex = (ascHouse + lagnaLordHouse) % 12;
  const conjSignIsMovable = MOVABLE_SIGNS.includes(conjSignIndex);

  return (mutualKendras && lagnaLordStrong) || (ninthLordStrong && conjunct && conjSignIsMovable);
};

export const sankhaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sankhaYoga(planetPositionsToChart(positions));

/**
 * Khadga Yoga: 2nd lord in 9th house, 9th lord in 2nd house (mutual exchange),
 * and lagna lord in a quadrant or trine.
 */
export const khadgaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const secondHouseIdx = (ascHouse + HOUSE_2) % 12;
  const ninthHouseIdx = (ascHouse + HOUSE_9) % 12;

  const secondLord = getLordOfSign(secondHouseIdx);
  const ninthLord = getLordOfSign(ninthHouseIdx);
  const lagnaLord = getLordOfSign(ascHouse);

  // Cond 1 & 2: Exchange between 2nd and 9th lords
  const secondLordInNinth = h(pToH, secondLord) === ninthHouseIdx;
  const ninthLordInSecond = h(pToH, ninthLord) === secondHouseIdx;

  // Cond 3: Lagna lord in quadrant or trine
  const quadrantsAndTrines = new Set([
    ...getQuadrants(ascHouse),
    ...getTrines(ascHouse),
  ]);
  const lagnaLordInQT = quadrantsAndTrines.has(h(pToH, lagnaLord));

  return secondLordInNinth && ninthLordInSecond && lagnaLordInQT;
};

export const khadgaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  khadgaYoga(planetPositionsToChart(positions));

/**
 * Go Yoga: (1) Jupiter in Moolatrikona sign (Sagittarius),
 * (2) 2nd lord conjunct Jupiter, (3) Lagna lord exalted (strength >= EXALTED).
 * Note: chart-based variant uses sign-only moolatrikona check (no degree enforcement).
 */
export const goYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const jupPos = h(pToH, JUPITER);

  // (1) Jupiter in Moolatrikona sign (sign-only check)
  if (jupPos !== MOOLA_TRIKONA_OF_PLANETS[JUPITER]) return false;

  // (2) 2nd lord conjunct Jupiter
  const h2Idx = (ascHouse + HOUSE_2) % 12;
  const l2 = getLordOfSign(h2Idx);
  if (h(pToH, l2) !== jupPos) return false;

  // (3) Lagna lord is exalted (strength >= STRENGTH_EXALTED)
  const l1 = getLordOfSign(ascHouse);
  const l1Strength = HOUSE_STRENGTHS_OF_PLANETS[l1]?.[h(pToH, l1)] ?? 0;
  if (l1Strength < STRENGTH_EXALTED) return false;

  return true;
};

export const goYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  goYoga(planetPositionsToChart(positions));

/**
 * Dharidhra Yoga (Method 1): Lord of 2nd or 11th in 6th, 8th, or 12th house (dusthana).
 */
export const dharidhraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const secondHouse = (ascHouse + HOUSE_2) % 12;
  const sixthHouse = (ascHouse + HOUSE_6) % 12;
  const eighthHouse = (ascHouse + HOUSE_8) % 12;
  const eleventhHouse = (ascHouse + HOUSE_11) % 12;
  const twelfthHouse = (ascHouse + HOUSE_12) % 12;

  const lordOfSecond = getLordOfSign(secondHouse);
  const lordOfEleventh = getLordOfSign(eleventhHouse);

  const dusthanas = [sixthHouse, eighthHouse, twelfthHouse];

  const secondIn6_8_12 = dusthanas.includes(h(pToH, lordOfSecond));
  const eleventhIn6_8_12 = dusthanas.includes(h(pToH, lordOfEleventh));

  return secondIn6_8_12 || eleventhIn6_8_12;
};

export const dharidhraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dharidhraYoga(planetPositionsToChart(positions));

// ============================================================================
// SANKHYA YOGAS (alternate names)
// ============================================================================

/** Vallaki Yoga: 7 planets (Sun-Saturn) in 7 signs */
export const vallakiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const signs = new Set(SUN_TO_SATURN.map((p) => h(pToH, p)));
  return signs.size === 7;
};
export const vallakiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vallakiYoga(planetPositionsToChart(positions));

/** Dama Yoga: 7 planets in 6 signs */
export const damaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const signs = new Set(SUN_TO_SATURN.map((p) => h(pToH, p)));
  return signs.size === 6;
};
export const damaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  damaYoga(planetPositionsToChart(positions));

/** Kedara Yoga: 7 planets in 4 signs */
export const kedaraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const signs = new Set(SUN_TO_SATURN.map((p) => h(pToH, p)));
  return signs.size === 4;
};
export const kedaraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kedaraYoga(planetPositionsToChart(positions));

/** Sula Yoga: 7 planets in 3 signs */
export const sulaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const signs = new Set(SUN_TO_SATURN.map((p) => h(pToH, p)));
  return signs.size === 3;
};
export const sulaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sulaYoga(planetPositionsToChart(positions));

// ============================================================================
// DHUR YOGA
// ============================================================================

/** Dhur Yoga: Lord of 10th in 6th, 8th or 12th house */
export const dhurYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h6 = (ascHouse + HOUSE_6) % 12;
  const h8 = (ascHouse + HOUSE_8) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;
  const h12 = (ascHouse + HOUSE_12) % 12;
  const l10 = getLordOfSign(h10);
  const l10Pos = h(pToH, l10);
  return l10Pos === h6 || l10Pos === h8 || l10Pos === h12;
};
export const dhurYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dhurYoga(planetPositionsToChart(positions));

// ============================================================================
// BHERI YOGA
// ============================================================================

/** Bheri Yoga: 9th lord strong AND (houses 1,2,7,12 occupied OR Jup/Ven/L1 mutual quadrants) */
export const bheriYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const lagnaLord = getLordOfSign(ascHouse);
  const ninthLord = getLordOfSign((ascHouse + HOUSE_9) % 12);

  // Ninth lord must be strong (include neutral for BV Raman data compatibility)
  const ninthStrength = HOUSE_STRENGTHS_OF_PLANETS[ninthLord]?.[h(pToH, ninthLord)] ?? 0;
  const isNinthStrong = ninthStrength >= 2; // neutral or better

  if (!isNinthStrong) return false;

  const planetIds = SUN_TO_KETU;

  // Path A: houses 1,2,7,12 from lagna are occupied
  const requiredHouses = [HOUSE_1, HOUSE_2, HOUSE_7, HOUSE_12].map((off) => (ascHouse + off) % 12);
  const pathA = requiredHouses.every((hIdx) => planetIds.some((p) => h(pToH, p) === hIdx));

  // Path B: Jupiter, Venus, and Lagna lord are in mutual quadrants
  const jupH = h(pToH, JUPITER);
  const venH = h(pToH, VENUS);
  const l1H = h(pToH, lagnaLord);
  const inMutualQuad = (h1: number, h2: number): boolean =>
    getQuadrants(h1).includes(h2) && getQuadrants(h2).includes(h1);
  const pathB =
    inMutualQuad(jupH, venH) && inMutualQuad(jupH, l1H) && inMutualQuad(venH, l1H);

  return pathA || pathB;
};
export const bheriYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bheriYoga(planetPositionsToChart(positions));

// ============================================================================
// MRIDANGA YOGA
// ============================================================================

/** Mridanga Yoga: Planets in own/exalted in quadrants AND trines, lagna lord strong */
export const mridangaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const quads = getQuadrants(ascHouse);
  const trns = getTrines(ascHouse);

  const ownExaltedInQuad = SUN_TO_KETU.some((p) => {
    const pHouse = h(pToH, p);
    return quads.includes(pHouse) && (HOUSE_STRENGTHS_OF_PLANETS[p]?.[pHouse] ?? 0) > STRENGTH_FRIEND;
  });
  const ownExaltedInTrine = SUN_TO_KETU.some((p) => {
    const pHouse = h(pToH, p);
    return trns.includes(pHouse) && (HOUSE_STRENGTHS_OF_PLANETS[p]?.[pHouse] ?? 0) > STRENGTH_FRIEND;
  });

  const lagnaLord = getLordOfSign(ascHouse);
  const llStrong = (HOUSE_STRENGTHS_OF_PLANETS[lagnaLord]?.[h(pToH, lagnaLord)] ?? 0) > STRENGTH_FRIEND;

  return ownExaltedInQuad && ownExaltedInTrine && llStrong;
};
export const mridangaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  mridangaYoga(planetPositionsToChart(positions));

// ============================================================================
// SREENAATHA YOGA
// ============================================================================

/** Sreenaatha Yoga: 7th lord exalted in 10th AND 10th lord with 9th lord */
export const sreenaatheYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h7 = (ascHouse + HOUSE_7) % 12;
  const h9 = (ascHouse + HOUSE_9) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;

  const l7 = getLordOfSign(h7);
  const l9 = getLordOfSign(h9);
  const l10 = getLordOfSign(h10);

  const l7InTenth = h(pToH, l7) === h10;
  const l7Exalted = (HOUSE_STRENGTHS_OF_PLANETS[l7]?.[h10] ?? 0) >= STRENGTH_EXALTED;
  const l9WithL10 = h(pToH, l9) === h(pToH, l10);

  return l7InTenth && l7Exalted && l9WithL10;
};
export const sreenaatheYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sreenaatheYoga(planetPositionsToChart(positions));

// ============================================================================
// KOORMA YOGA
// ============================================================================

/** Koorma Yoga (Method 1 - BV Raman): benefics in 5,6,7 strong OR benefics in 1,3,11 strong */
export const koormaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const benefics = new Set(getNaturalBenefics(chart));
  const occ = (hIdx: number): number[] => SUN_TO_KETU.filter((p) => h(pToH, p) === hIdx);

  const beneficHouses = [HOUSE_5, HOUSE_6, HOUSE_7].map((off) => (ascHouse + off) % 12);
  const maleficHouses = [HOUSE_1, HOUSE_3, HOUSE_11].map((off) => (ascHouse + off) % 12);

  const firstCond = beneficHouses.every((hIdx) => {
    const occupants = occ(hIdx);
    return (
      occupants.length > 0 &&
      occupants.every((p) => benefics.has(p) && isPlanetStrong(p, hIdx))
    );
  });

  // BV Raman method 1: second condition also uses benefics, OR logic
  const secondCond = maleficHouses.every((hIdx) => {
    const occupants = occ(hIdx);
    return (
      occupants.length > 0 &&
      occupants.every((p) => benefics.has(p) && isPlanetStrong(p, hIdx))
    );
  });

  return firstCond || secondCond;
};
export const koormaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  koormaYoga(planetPositionsToChart(positions));

// ============================================================================
// KUSUMA YOGA
// ============================================================================

/** Kusuma Yoga: fixed lagna, Venus in quadrant, Moon in trine with benefic, Saturn in 10th */
export const kusumaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  if (!FIXED_SIGNS.includes(ascHouse)) return false;
  if (!getQuadrants(ascHouse).includes(h(pToH, VENUS))) return false;
  if (h(pToH, SATURN) !== (ascHouse + HOUSE_10) % 12) return false;

  const benefics = getNaturalBenefics(chart);
  const moonInTrineWithBenefic = benefics.some((b) =>
    getTrines(h(pToH, b)).includes(h(pToH, MOON))
  );
  return moonInTrineWithBenefic;
};
export const kusumaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kusumaYoga(planetPositionsToChart(positions));

// ============================================================================
// KALAANIDHI YOGA
// ============================================================================

/** Kalaanidhi Yoga: Jupiter in 2nd/5th, conjoined or aspected by Mercury and Venus */
export const kalaanidhiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const jupHouse = h(pToH, JUPITER);
  const h2 = (ascHouse + HOUSE_2) % 12;
  const h5 = (ascHouse + HOUSE_5) % 12;

  if (jupHouse !== h2 && jupHouse !== h5) return false;

  // Check conjunction
  const planetsInJupHouse = getPlanetsInHouse(chart, jupHouse);
  const mercConj = planetsInJupHouse.includes(MERCURY);
  const venConj = planetsInJupHouse.includes(VENUS);

  // Check aspect (graha drishti)
  const aspectedByMerc = getGrahaDrishtiPlanetsOfPlanet(chart, MERCURY).includes(JUPITER);
  const aspectedByVen = getGrahaDrishtiPlanetsOfPlanet(chart, VENUS).includes(JUPITER);

  const hasMercInfluence = mercConj || aspectedByMerc;
  const hasVenInfluence = venConj || aspectedByVen;

  return hasMercInfluence && hasVenInfluence;
};
export const kalaanidhiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kalaanidhiYoga(planetPositionsToChart(positions));

// ============================================================================
// LAGNAADHI YOGA
// ============================================================================

/** Lagnaadhi Yoga: benefics in 6th,7th,8th from lagna, no malefics conjoin/aspect */
export const lagnaAdhiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const targetHouses = [HOUSE_6, HOUSE_7, HOUSE_8].map((off) => (ascHouse + off) % 12);
  const benefics = getNaturalBenefics(chart);
  const malefics = getNaturalMalefics();

  // All benefics must be in target houses
  if (!benefics.every((p) => targetHouses.includes(h(pToH, p)))) return false;

  // No malefics in target houses
  if (malefics.some((m) => targetHouses.includes(h(pToH, m)))) return false;

  // No malefic aspects on benefics
  for (const b of benefics) {
    const aspectedBy = getGrahaDrishtiOnPlanet(chart, b);
    if (aspectedBy.some((m) => malefics.includes(m))) return false;
  }
  return true;
};
export const lagnaAdhiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  lagnaAdhiYoga(planetPositionsToChart(positions));

// ============================================================================
// HARI YOGA
// ============================================================================

/** Hari Yoga: benefics in 2nd, 8th, 12th from 2nd lord */
export const hariYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h2Idx = (ascHouse + HOUSE_2) % 12;
  const secondLord = getLordOfSign(h2Idx);
  const lordPos = h(pToH, secondLord);
  const targets = [
    (lordPos + HOUSE_2) % 12,
    (lordPos + HOUSE_8) % 12,
    (lordPos + HOUSE_12) % 12,
  ];
  const benefics = getNaturalBenefics(chart);
  return benefics.every((p) => targets.includes(h(pToH, p)));
};
export const hariYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  hariYoga(planetPositionsToChart(positions));

// ============================================================================
// HARA YOGA
// ============================================================================

/** Hara Yoga: benefics in 4th, 9th, 8th from 7th lord */
export const haraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h7Idx = (ascHouse + HOUSE_7) % 12;
  const seventhLord = getLordOfSign(h7Idx);
  const lordPos = h(pToH, seventhLord);
  const targets = [
    (lordPos + HOUSE_4) % 12,
    (lordPos + HOUSE_9) % 12,
    (lordPos + HOUSE_8) % 12,
  ];
  const benefics = getNaturalBenefics(chart);
  return benefics
    .filter((p) => p !== seventhLord)
    .every((p) => targets.includes(h(pToH, p)));
};
export const haraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  haraYoga(planetPositionsToChart(positions));

// ============================================================================
// BRAHMA YOGA
// ============================================================================

/** Brahma Yoga (Method 1): benefics in 4th, 10th, 11th from lagna lord */
export const brahmaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const lagnaLord = getLordOfSign(ascHouse);
  const llPos = h(pToH, lagnaLord);
  const m1Targets = [
    (llPos + HOUSE_4) % 12,
    (llPos + HOUSE_10) % 12,
    (llPos + HOUSE_11) % 12,
  ];
  const benefics = getNaturalBenefics(chart);
  return benefics
    .filter((p) => p !== lagnaLord)
    .every((p) => m1Targets.includes(h(pToH, p)));
};
export const brahmaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  brahmaYoga(planetPositionsToChart(positions));

// ============================================================================
// SIVA YOGA
// ============================================================================

/** Siva Yoga: 5th lord in 9th, 9th lord in 10th, 10th lord in 5th */
export const sivaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h5 = (ascHouse + HOUSE_5) % 12;
  const h9 = (ascHouse + HOUSE_9) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;

  const l5 = getLordOfSign(h5);
  const l9 = getLordOfSign(h9);
  const l10 = getLordOfSign(h10);

  return h(pToH, l5) === h9 && h(pToH, l9) === h10 && h(pToH, l10) === h5;
};
export const sivaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sivaYoga(planetPositionsToChart(positions));

// ============================================================================
// DEVENDRA YOGA
// ============================================================================

/** Devendra Yoga: fixed lagna, exchange 2nd/10th lords, exchange 1st/11th lords */
export const devendraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  if (!FIXED_SIGNS.includes(ascHouse)) return false;

  const h2 = (ascHouse + HOUSE_2) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;
  const h11 = (ascHouse + HOUSE_11) % 12;

  const l1 = getLordOfSign(ascHouse);
  const l2 = getLordOfSign(h2);
  const l10 = getLordOfSign(h10);
  const l11 = getLordOfSign(h11);

  const exchange2_10 = h(pToH, l2) === h10 && h(pToH, l10) === h2;
  const exchange1_11 = h(pToH, l1) === h11 && h(pToH, l11) === ascHouse;

  return exchange2_10 && exchange1_11;
};
export const devendraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  devendraYoga(planetPositionsToChart(positions));

// ============================================================================
// INDRA YOGA
// ============================================================================

/** Indra Yoga: exchange between 5th and 11th lords, Moon in 5th */
export const indraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h5 = (ascHouse + HOUSE_5) % 12;
  const h11 = (ascHouse + HOUSE_11) % 12;

  const l5 = getLordOfSign(h5);
  const l11 = getLordOfSign(h11);

  const exchange = h(pToH, l5) === h11 && h(pToH, l11) === h5;
  const moonIn5 = h(pToH, MOON) === h5;

  return exchange && moonIn5;
};
export const indraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  indraYoga(planetPositionsToChart(positions));

// ============================================================================
// RAVI YOGA
// ============================================================================

/** Ravi Yoga: Sun in 10th, 10th lord in 3rd with Saturn */
export const raviYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h3 = (ascHouse + HOUSE_3) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;

  const l10 = getLordOfSign(h10);

  return h(pToH, SUN) === h10 && h(pToH, l10) === h3 && h(pToH, SATURN) === h3;
};
export const raviYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  raviYoga(planetPositionsToChart(positions));

// ============================================================================
// BHAASKARA YOGA
// ============================================================================

/** Bhaaskara Yoga: Moon 12th from Sun, Mercury 2nd from Sun, Jupiter 5/9 from Moon */
export const bhaaskaraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const sunIdx = h(pToH, SUN);
  const moonIdx = h(pToH, MOON);
  const mercuryIdx = h(pToH, MERCURY);
  const jupiterIdx = h(pToH, JUPITER);

  const moonTarget = (sunIdx + HOUSE_12) % 12;
  const mercTarget = (sunIdx + HOUSE_2) % 12;
  const jupTarget5 = (moonIdx + HOUSE_5) % 12;
  const jupTarget9 = (moonIdx + HOUSE_9) % 12;

  return (
    moonIdx === moonTarget &&
    mercuryIdx === mercTarget &&
    (jupiterIdx === jupTarget5 || jupiterIdx === jupTarget9)
  );
};
export const bhaaskaraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bhaaskaraYoga(planetPositionsToChart(positions));

// ============================================================================
// KULAVARDHANA YOGA
// ============================================================================

/** Kulavardhana Yoga: all planets (Sun-Saturn) in 5th from lagna, moon, or sun */
export const kulavardhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascIdx = h(pToH, ASCENDANT_SYMBOL);
  const moonIdx = h(pToH, MOON);
  const sunIdx = h(pToH, SUN);

  const validHouses = new Set([
    (ascIdx + HOUSE_5) % 12,
    (moonIdx + HOUSE_5) % 12,
    (sunIdx + HOUSE_5) % 12,
  ]);

  return SUN_TO_SATURN.every((p) => validHouses.has(h(pToH, p)));
};
export const kulavardhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kulavardhanaYoga(planetPositionsToChart(positions));

// ============================================================================
// GANDHARVA YOGA
// ============================================================================

/** Gandharva Yoga: 10th lord in trine from 7th, L1 aspected by Jupiter, Sun exalted, Moon in 9th */
export const gandharvaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h7 = (ascHouse + HOUSE_7) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;
  const l10 = getLordOfSign(h10);
  const l1 = getLordOfSign(ascHouse);

  // (1) 10th lord in trine from 7th house
  const cond1 = getTrines(h7).includes(h(pToH, l10));

  // (2) Lagna lord conjoined or aspected by Jupiter
  const l1Pos = h(pToH, l1);
  const jupPos = h(pToH, JUPITER);
  const jupAspects = getGrahaDrishtiRasisOfPlanet(chart, JUPITER);
  const cond2 = l1Pos === jupPos || jupAspects.includes(l1Pos);

  // (3) Sun exalted and strong
  const sunPos = h(pToH, SUN);
  const cond3 = (HOUSE_STRENGTHS_OF_PLANETS[SUN]?.[sunPos] ?? 0) >= STRENGTH_EXALTED;

  // (4) Moon in 9th house
  const cond4 = h(pToH, MOON) === (ascHouse + HOUSE_9) % 12;

  return cond1 && cond2 && cond3 && cond4;
};
export const gandharvaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  gandharvaYoga(planetPositionsToChart(positions));

// ============================================================================
// VIDYUT YOGA
// ============================================================================

/** Vidyut Yoga: 11th lord exalted, conjoins Venus, both in quadrant from lagna lord */
export const vidyutYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h11 = (ascHouse + HOUSE_11) % 12;
  const l11 = getLordOfSign(h11);
  const l11Pos = h(pToH, l11);

  // (1) 11th lord exalted
  if ((HOUSE_STRENGTHS_OF_PLANETS[l11]?.[l11Pos] ?? 0) < STRENGTH_EXALTED) return false;

  // (2) 11th lord conjoins Venus
  if (l11Pos !== h(pToH, VENUS)) return false;

  // (3) Both in quadrant from lagna lord
  const l1 = getLordOfSign(ascHouse);
  if (!getQuadrants(h(pToH, l1)).includes(l11Pos)) return false;

  return true;
};
export const vidyutYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vidyutYoga(planetPositionsToChart(positions));

// ============================================================================
// CHAPA YOGA (exchange type, different from Chaaapa aakriti yoga)
// ============================================================================

/** Chapa Yoga: 4th/10th lords exchange, lagna lord exalted */
export const chapaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h4 = (ascHouse + HOUSE_4) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;

  const l4 = getLordOfSign(h4);
  const l10 = getLordOfSign(h10);

  if (!(h(pToH, l4) === h10 && h(pToH, l10) === h4)) return false;

  const l1 = getLordOfSign(ascHouse);
  const l1Pos = h(pToH, l1);
  return (HOUSE_STRENGTHS_OF_PLANETS[l1]?.[l1Pos] ?? 0) >= STRENGTH_EXALTED;
};
export const chapaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chapaYoga(planetPositionsToChart(positions));

// ============================================================================
// PUSHKALA YOGA
// ============================================================================

/** Pushkala Yoga: lagna lord with Moon, Moon's dispositor in quadrant or adhimitra, aspects lagna */
export const pushkalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l1 = getLordOfSign(ascHouse);
  const moonPos = h(pToH, MOON);

  // (1) Lagna lord is with Moon
  if (h(pToH, l1) !== moonPos) return false;

  // (2) Dispositor of Moon in quadrant or adhimitra house
  const lMoon = getLordOfSign(moonPos);
  const lMoonPos = h(pToH, lMoon);
  const isInQuadrant = getQuadrants(ascHouse).includes(lMoonPos);

  // Simplified adhimitra check: not available without compound relations, use quadrant only
  if (!isInQuadrant) return false;

  // (3) Dispositor aspects lagna (rasi drishti)
  const aspectedRasis = getRaasiDrishtiOfPlanet(chart, lMoon);
  return aspectedRasis.includes(ascHouse);
};
export const pushkalaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  pushkalaYoga(planetPositionsToChart(positions));

// ============================================================================
// MAKUTA YOGA
// ============================================================================

/** Makuta Yoga: Saturn in 10th, Jupiter 9th from 9th lord, benefic 9th from Jupiter */
export const makutaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h10 = (ascHouse + HOUSE_10) % 12;

  // (1) Saturn in 10th
  if (h(pToH, SATURN) !== h10) return false;

  // (2) Jupiter is 9th from 9th lord
  const h9 = (ascHouse + HOUSE_9) % 12;
  const l9 = getLordOfSign(h9);
  const l9Pos = h(pToH, l9);
  const targetForJup = (l9Pos + HOUSE_9) % 12;
  if (h(pToH, JUPITER) !== targetForJup) return false;

  // (3) 9th from Jupiter has a benefic
  const jupPos = h(pToH, JUPITER);
  const h9FromJup = (jupPos + HOUSE_9) % 12;
  const planetsInH9FromJup = getPlanetsInHouse(chart, h9FromJup);
  const benefics = getNaturalBenefics(chart);
  return planetsInH9FromJup.some((p) => benefics.includes(p));
};
export const makutaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  makutaYoga(planetPositionsToChart(positions));

// ============================================================================
// JAYA YOGA
// ============================================================================

/** Jaya Yoga: 10th lord exalted, 6th lord debilitated */
export const jayaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h10 = (ascHouse + HOUSE_10) % 12;
  const h6 = (ascHouse + HOUSE_6) % 12;

  const l10 = getLordOfSign(h10);
  const l6 = getLordOfSign(h6);

  const l10Pos = h(pToH, l10);
  const l6Pos = h(pToH, l6);

  const l10Exalted = (HOUSE_STRENGTHS_OF_PLANETS[l10]?.[l10Pos] ?? 0) >= STRENGTH_EXALTED;
  const l6Debilitated = (HOUSE_STRENGTHS_OF_PLANETS[l6]?.[l6Pos] ?? 0) === STRENGTH_DEBILITATED;

  return l10Exalted && l6Debilitated;
};
export const jayaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  jayaYoga(planetPositionsToChart(positions));

// ============================================================================
// VANCHANA CHORA BHEETHI YOGA
// ============================================================================

/** Vanchana Chora Bheethi Yoga (simplified): L1 with Rahu, Saturn, or Ketu */
export const vanchanaChoraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l1 = getLordOfSign(ascHouse);
  const l1House = h(pToH, l1);

  const c3Malefics = [RAHU, SATURN, KETU];
  const planetsInL1House = getPlanetsInHouse(chart, l1House);
  return planetsInL1House.some((m) => c3Malefics.includes(m) && m !== l1);
};
export const vanchanaChoraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vanchanaChoraYoga(planetPositionsToChart(positions));

// ============================================================================
// HARIHARA BRAHMA YOGA
// ============================================================================

/** Harihara Brahma Yoga: hari OR hara OR brahma yoga */
export const hariharaBrahmaYoga = (chart: HouseChart): boolean => {
  return hariYoga(chart) || haraYoga(chart) || brahmaYoga(chart);
};
export const hariharaBrahmaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  hariharaBrahmaYoga(planetPositionsToChart(positions));

// ============================================================================
// SREENATHA YOGA (same as sreenaatha but different spelling in Python)
// ============================================================================

/** Sreenatha Yoga: 7th lord exalted in 10th, 10th lord with 9th lord */
export const sreenataYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h7 = (ascHouse + HOUSE_7) % 12;
  const h9 = (ascHouse + HOUSE_9) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;

  const l7 = getLordOfSign(h7);
  const l9 = getLordOfSign(h9);
  const l10 = getLordOfSign(h10);

  const l7InTenth = h(pToH, l7) === h10;
  const l7Exalted = (HOUSE_STRENGTHS_OF_PLANETS[l7]?.[h10] ?? 0) >= STRENGTH_EXALTED;
  const l10WithL9 = h(pToH, l10) === h(pToH, l9);

  return l7InTenth && l7Exalted && l10WithL9;
};
export const sreenataYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sreenataYoga(planetPositionsToChart(positions));

// ============================================================================
// PARIJATHA YOGA
// ============================================================================

/** Parijatha Yoga: dispositor chain from lagna lord ends in quadrant/trine or exalted */
export const parijathaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const lagnaLord = getLordOfSign(ascHouse);
  const houseOfLL = h(pToH, lagnaLord);
  const dispositor1 = getLordOfSign(houseOfLL);
  const houseOfDisp1 = h(pToH, dispositor1);
  const targetPlanet = getLordOfSign(houseOfDisp1);
  const targetHouse = h(pToH, targetPlanet);

  const kendraTrikona = [...getQuadrants(ascHouse), ...getTrines(ascHouse)];
  const isInGoodHouse = kendraTrikona.includes(targetHouse);
  const isDignified = (HOUSE_STRENGTHS_OF_PLANETS[targetPlanet]?.[targetHouse] ?? 0) >= STRENGTH_EXALTED;

  return isInGoodHouse || isDignified;
};
export const parijathaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  parijathaYoga(planetPositionsToChart(positions));

// ============================================================================
// GAJA YOGA (different from Gaja Kesari)
// ============================================================================

/** Gaja Yoga: lord of 9th from 11th in 11th with Moon, aspected by 11th lord */
export const gajaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h11 = (ascHouse + HOUSE_11) % 12;
  const moonH = h(pToH, MOON);

  if (moonH !== h11) return false;

  const h9From11 = (h11 + HOUSE_9) % 12;
  const l11 = getLordOfSign(h11);
  const l9From11 = getLordOfSign(h9From11);

  // Target lord in 11th
  if (h(pToH, l9From11) !== h11) return false;

  // Aspected by 11th lord (graha or rasi aspect)
  const grahaAspects = getGrahaDrishtiPlanetsOfPlanet(chart, l11);
  const raasiAspects = getAspectedPlanetsOfRaasi(chart, h(pToH, l11));
  return grahaAspects.includes(l9From11) || raasiAspects.includes(l9From11);
};
export const gajaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  gajaYoga(planetPositionsToChart(positions));

// ============================================================================
// KALANIDHI YOGA (BV Raman variant)
// ============================================================================

/** Kalanidhi Yoga: Jupiter in 2nd/5th in Mercury/Venus sign, joined/aspected by both */
export const kalanidhiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const jupHouse = h(pToH, JUPITER);
  const h2 = (ascHouse + HOUSE_2) % 12;
  const h5 = (ascHouse + HOUSE_5) % 12;

  if (jupHouse !== h2 && jupHouse !== h5) return false;

  // Check influence from Mercury and Venus
  const mercConj = h(pToH, MERCURY) === jupHouse;
  const venConj = h(pToH, VENUS) === jupHouse;
  const mercAspects = getGrahaDrishtiPlanetsOfPlanet(chart, MERCURY);
  const venAspects = getGrahaDrishtiPlanetsOfPlanet(chart, VENUS);

  const hasMerc = mercConj || mercAspects.includes(JUPITER);
  const hasVen = venConj || venAspects.includes(JUPITER);

  // Swakshetra check: Jupiter in Mercury or Venus sign
  const jupSignOwner = getLordOfSign(jupHouse);
  const isInMercOrVenSign = jupSignOwner === MERCURY || jupSignOwner === VENUS;
  const isStrongConj = mercConj && venConj;

  return hasMerc && hasVen && (isInMercOrVenSign || isStrongConj);
};
export const kalanidhiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kalanidhiYoga(planetPositionsToChart(positions));

// ============================================================================
// SAARADA YOGA
// ============================================================================

/** Saarada Yoga: 10L in 5th, Mercury in quadrant, Sun in Leo, Merc/Jup trine from Moon, Mars in 11th */
export const saaradaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const h5 = (ascHouse + HOUSE_5) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;
  const h11 = (ascHouse + HOUSE_11) % 12;

  const l10 = getLordOfSign(h10);
  if (h(pToH, l10) !== h5) return false;

  const mercPos = h(pToH, MERCURY);
  if (!getQuadrants(ascHouse).includes(mercPos)) return false;

  const sunPos = h(pToH, SUN);
  if (sunPos !== LEO || (HOUSE_STRENGTHS_OF_PLANETS[SUN]?.[LEO] ?? 0) < STRENGTH_EXALTED) return false;

  const moonPos = h(pToH, MOON);
  const trinesFromMoon = getTrines(moonPos);
  const jupPos = h(pToH, JUPITER);
  if (!trinesFromMoon.includes(mercPos) && !trinesFromMoon.includes(jupPos)) return false;

  return h(pToH, MARS) === h11;
};
export const saaradaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  saaradaYoga(planetPositionsToChart(positions));

// ============================================================================
// SARASWATHI YOGA
// ============================================================================

/** Saraswathi Yoga: Mercury/Jupiter/Venus in quadrant/trine/2nd, Jupiter strong */
export const saraswathiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h2 = (ascHouse + HOUSE_2) % 12;
  const validHouses = new Set([...getQuadrants(ascHouse), ...getTrines(ascHouse), h2]);

  const mercPos = h(pToH, MERCURY);
  const jupPos = h(pToH, JUPITER);
  const venPos = h(pToH, VENUS);

  const placed = validHouses.has(mercPos) && validHouses.has(jupPos) && validHouses.has(venPos);
  const jupStrong = (HOUSE_STRENGTHS_OF_PLANETS[JUPITER]?.[jupPos] ?? 0) >= STRENGTH_FRIEND;

  return placed && jupStrong;
};
export const saraswathiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  saraswathiYoga(planetPositionsToChart(positions));

// ============================================================================
// AMSAAVATARA YOGA
// ============================================================================

/** Amsaavatara Yoga: Jupiter, Venus, exalted Saturn in quadrants */
export const amsaavataraYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const quads = getQuadrants(ascHouse);

  const jupPos = h(pToH, JUPITER);
  const venPos = h(pToH, VENUS);
  const satPos = h(pToH, SATURN);

  const inQuadrants = quads.includes(jupPos) && quads.includes(venPos) && quads.includes(satPos);
  const satExalted = (HOUSE_STRENGTHS_OF_PLANETS[SATURN]?.[satPos] ?? 0) === STRENGTH_EXALTED;

  return inQuadrants && satExalted;
};
export const amsaavataraYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  amsaavataraYoga(planetPositionsToChart(positions));

// ============================================================================
// DEHAPUSHTI YOGA
// ============================================================================

/** Dehapushti Yoga: lagna lord in movable sign, aspected by benefic */
export const dehapushtiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const llHouse = h(pToH, ll);

  if (!MOVABLE_SIGNS.includes(llHouse)) return false;

  const benefics = getNaturalBenefics(chart);
  const aspectingPlanets = getGrahaDrishtiOnPlanet(chart, ll);
  return aspectingPlanets.some((p) => benefics.includes(p));
};
export const dehapushtiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dehapushtiYoga(planetPositionsToChart(positions));

// ============================================================================
// ROGAGRASTHA YOGA
// ============================================================================

/** Rogagrastha Yoga: (a) LL in lagna joined by dusthana lord OR (b) weak LL in kendra/trikona */
export const rogagrasthaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const llHouse = h(pToH, ll);
  const dusthanas = getDushthanas(ascHouse);
  const quadTrineHouses = [...getQuadrants(ascHouse), ...getTrines(ascHouse)];

  const dusthanaLords = dusthanas.map((dh) => getLordOfSign(dh));

  // Condition A: LL in lagna + joined by dusthana lord
  const llInLagna = llHouse === ascHouse;
  const llCojoinsDustLord = dusthanaLords.some((dl) => h(pToH, dl) === llHouse);
  const condA = llInLagna && llCojoinsDustLord;

  // Condition B: weak LL in kendra/trikona
  const quadTrineLords = quadTrineHouses.map((qth) => getLordOfSign(qth));
  const llCojoinsQTLord = quadTrineLords.some((qtl) => h(pToH, qtl) === llHouse);
  const llWeak = (HOUSE_STRENGTHS_OF_PLANETS[ll]?.[llHouse] ?? 0) <= 2; // neutral or worse
  const condB = llCojoinsQTLord && llWeak;

  return condA || condB;
};
export const rogagrasthaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  rogagrasthaYoga(planetPositionsToChart(positions));

// ============================================================================
// KRISANGA YOGA (simplified - rasi-only check)
// ============================================================================

/** Krisanga Yoga: lagna lord in dry sign or sign owned by dry planet */
export const krisangaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const llHouse = h(pToH, ll);
  const llHouseOwner = getLordOfSign(llHouse);

  return DRY_SIGNS.includes(llHouse) || DRY_PLANETS.includes(llHouseOwner);
};
export const krisangaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  krisangaYoga(planetPositionsToChart(positions));

// ============================================================================
// DEHASTHOULYA YOGA (simplified - rasi-only check)
// ============================================================================

/** Dehasthoulya Yoga: Jupiter in lagna, or Jupiter aspects lagna from watery sign, or benefics in watery lagna */
export const dehasthoulyaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const benefics = getNaturalBenefics(chart);

  // Condition 2: Jupiter in lagna
  const jH = h(pToH, JUPITER);
  if (jH === ascHouse) return true;

  // Condition 2b: Jupiter aspects lagna from watery sign
  if (WATER_SIGNS.includes(jH)) {
    const jupAspects = [(jH + 4) % 12, (jH + 6) % 12, (jH + 8) % 12];
    if (jupAspects.includes(ascHouse)) return true;
  }

  // Condition 3a: Lagna in watery sign with benefics
  const benInLagna = benefics.some((b) => h(pToH, b) === ascHouse);
  if (WATER_SIGNS.includes(ascHouse) && benInLagna) return true;

  // Condition 3b: Lagna lord is a watery planet
  if (WATERY_PLANETS.includes(ll)) return true;

  return false;
};
export const dehasthoulyaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dehasthoulyaYoga(planetPositionsToChart(positions));

// ============================================================================
// SADA SANCHARA YOGA
// ============================================================================

/** Sada Sanchara Yoga: lagna lord or its dispositor in movable sign */
export const sadaSancharaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const llHouse = h(pToH, ll);

  if (MOVABLE_SIGNS.includes(llHouse)) return true;

  const llDispositor = getLordOfSign(llHouse);
  const llDispHouse = h(pToH, llDispositor);
  return MOVABLE_SIGNS.includes(llDispHouse);
};
export const sadaSancharaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sadaSancharaYoga(planetPositionsToChart(positions));

// ============================================================================
// BAHUDRAVYARJANA YOGA
// ============================================================================

/** Bahudravyarjana Yoga: L1 in 2nd, L2 in 11th, L11 in lagna */
export const bahudravyarjanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h2 = (ascHouse + HOUSE_2) % 12;
  const h11 = (ascHouse + HOUSE_11) % 12;

  const l1 = getLordOfSign(ascHouse);
  const l2 = getLordOfSign(h2);
  const l11 = getLordOfSign(h11);

  return h(pToH, l1) === h2 && h(pToH, l2) === h11 && h(pToH, l11) === ascHouse;
};
export const bahudravyarjanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bahudravyarjanaYoga(planetPositionsToChart(positions));

// ============================================================================
// MADHYA VAYASI DHANA YOGA
// ============================================================================

/** Madhya Vayasi Dhana Yoga: benefics in 2nd and 3rd from lagna lord position */
export const madhyaVayasiDhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const llHouse = h(pToH, ll);
  const benefics = getNaturalBenefics(chart);

  const h2FromLL = (llHouse + HOUSE_2) % 12;
  const h3FromLL = (llHouse + HOUSE_3) % 12;

  const planetsIn2 = getPlanetsInHouse(chart, h2FromLL);
  const planetsIn3 = getPlanetsInHouse(chart, h3FromLL);

  return (
    planetsIn2.some((p) => benefics.includes(p)) && planetsIn3.some((p) => benefics.includes(p))
  );
};
export const madhyaVayasiDhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  madhyaVayasiDhanaYoga(planetPositionsToChart(positions));

// ============================================================================
// ANTHYA VAYASI DHANA YOGA
// ============================================================================

/** Anthya Vayasi Dhana Yoga: L2 in kendra/trine from L1 */
export const anthyaVayasiDhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const ll = getLordOfSign(ascHouse);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const llHouse = h(pToH, ll);
  const l2House = h(pToH, l2);

  const validHouses = [...getQuadrants(llHouse), ...getTrines(llHouse)];
  return validHouses.includes(l2House);
};
export const anthyaVayasiDhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  anthyaVayasiDhanaYoga(planetPositionsToChart(positions));

// ============================================================================
// SAREERA SOUKHYA YOGA
// ============================================================================

/** Sareera Soukhya Yoga: L1, Jupiter, or Venus in a quadrant */
export const sareeraSoukhyaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const lagnaLord = getLordOfSign(ascHouse);
  const quads = getQuadrants(ascHouse);

  return (
    quads.includes(h(pToH, lagnaLord)) ||
    quads.includes(h(pToH, JUPITER)) ||
    quads.includes(h(pToH, VENUS))
  );
};
export const sareeraSoukhyaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sareeraSoukhyaYoga(planetPositionsToChart(positions));

// ============================================================================
// MATRUMOOLADDHANA YOGA
// ============================================================================

/** Matrumooladdhana Yoga: L2 joined or aspected by L4 */
export const matrumooladdhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const l4 = getLordOfSign((ascHouse + HOUSE_4) % 12);

  const conjoined = h(pToH, l2) === h(pToH, l4);
  const l4AspectsL2 = getGrahaDrishtiPlanetsOfPlanet(chart, l4).includes(l2);
  return conjoined || l4AspectsL2;
};
export const matrumooladdhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  matrumooladdhanaYoga(planetPositionsToChart(positions));

// ============================================================================
// KALATRAMOOLADDHANA YOGA
// ============================================================================

/** Kalatramooladdhana Yoga: strong L2 joined/aspected by L7 and Venus, L1 powerful */
export const kalatramooladdhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l1 = getLordOfSign(ascHouse);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const l7 = getLordOfSign((ascHouse + HOUSE_7) % 12);

  const l1Strong = (HOUSE_STRENGTHS_OF_PLANETS[l1]?.[h(pToH, l1)] ?? 0) >= STRENGTH_EXALTED;
  const l2Strong = (HOUSE_STRENGTHS_OF_PLANETS[l2]?.[h(pToH, l2)] ?? 0) >= STRENGTH_EXALTED;

  const l2H = h(pToH, l2);
  const planetsInL2H = getPlanetsInHouse(chart, l2H);
  const conjoined = h(pToH, l2) === h(pToH, l7) && planetsInL2H.includes(VENUS);

  const l7AspectsL2 = getGrahaDrishtiPlanetsOfPlanet(chart, l7).includes(l2);
  const venAspectsL2 = getGrahaDrishtiPlanetsOfPlanet(chart, VENUS).includes(l2);
  const aspected = l7AspectsL2 && venAspectsL2;

  return l1Strong && l2Strong && (conjoined || aspected);
};
export const kalatramooladdhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kalatramooladdhanaYoga(planetPositionsToChart(positions));

// ============================================================================
// MAHABHAGYA YOGA (already exists but adding parameterized version)
// ============================================================================

// mahabhagyaYoga already exists in the file, skip

// ============================================================================
// VISHNU YOGA (requires navamsa - simplified single-chart stub)
// ============================================================================

/** Vishnu Yoga (simplified): 9th and 10th lords in 2nd house */
export const vishnuYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h2 = (ascHouse + HOUSE_2) % 12;
  const h9 = (ascHouse + HOUSE_9) % 12;
  const h10 = (ascHouse + HOUSE_10) % 12;

  const l9 = getLordOfSign(h9);
  const l10 = getLordOfSign(h10);

  return h(pToH, l9) === h2 && h(pToH, l10) === h2;
};
export const vishnuYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  vishnuYoga(planetPositionsToChart(positions));

// ============================================================================
// GOURI YOGA (requires navamsa - simplified single-chart stub)
// ============================================================================

/** Gouri Yoga (simplified): 10th lord exalted in 10th with lagna lord */
export const gouriYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h10 = (ascHouse + HOUSE_10) % 12;
  const l1 = getLordOfSign(ascHouse);
  const l10 = getLordOfSign(h10);

  // Simplified: l10 in 10th, exalted, with l1
  const l10In10 = h(pToH, l10) === h10;
  const l10Exalted = (HOUSE_STRENGTHS_OF_PLANETS[l10]?.[h10] ?? 0) >= STRENGTH_EXALTED;
  const l1In10 = h(pToH, l1) === h10;

  return l10In10 && l10Exalted && l1In10;
};
export const gouriYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  gouriYoga(planetPositionsToChart(positions));

// ============================================================================
// CHANDIKAA YOGA (requires navamsa - simplified single-chart stub)
// ============================================================================

/** Chandikaa Yoga (simplified): fixed lagna aspected by 6th lord */
export const chandikaaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  if (!FIXED_SIGNS.includes(ascHouse)) return false;

  const h6 = (ascHouse + HOUSE_6) % 12;
  const l6 = getLordOfSign(h6);
  const l6Aspects = getRaasiDrishtiOfPlanet(chart, l6);
  return l6Aspects.includes(ascHouse);
};
export const chandikaaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  chandikaaYoga(planetPositionsToChart(positions));

// ============================================================================
// GARUDA YOGA (requires navamsa + tithi - simplified single-chart stub)
// ============================================================================

/** Garuda Yoga (simplified stub - always false without navamsa/tithi data) */
export const garudaYoga = (_chart: HouseChart): boolean => {
  // Requires navamsa chart, shukla paksha, and daytime birth data
  // Cannot be accurately computed from single chart alone
  return false;
};
export const garudaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  garudaYoga(planetPositionsToChart(positions));

// ============================================================================
// KALPADRUMA YOGA (requires navamsa - simplified single-chart stub)
// ============================================================================

/** Kalpadruma Yoga (simplified): dispositor chain from lagna lord in kendra/trikona or exalted */
export const kalpadrumaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const lagnaLord = getLordOfSign(ascHouse);
  const disp1 = getLordOfSign(h(pToH, lagnaLord));
  const disp2 = getLordOfSign(h(pToH, disp1));

  const favorable = new Set([...getQuadrants(ascHouse), ...getTrines(ascHouse)]);

  const isWellPlaced = (p: number): boolean => {
    const pHouse = h(pToH, p);
    return (
      favorable.has(pHouse) ||
      (HOUSE_STRENGTHS_OF_PLANETS[p]?.[pHouse] ?? 0) >= STRENGTH_EXALTED
    );
  };

  return [lagnaLord, disp1, disp2].every(isWellPlaced);
};
export const kalpadrumaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  kalpadrumaYoga(planetPositionsToChart(positions));

// ============================================================================
// BHAARATHI YOGA (requires navamsa - simplified single-chart stub)
// ============================================================================

/** Bhaarathi Yoga (simplified): exalted planet joins 9th lord */
export const bhaarathiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h9 = (ascHouse + HOUSE_9) % 12;
  const l9 = getLordOfSign(h9);
  const l9Pos = h(pToH, l9);

  // Check if any planet joined with l9 is exalted
  const planetsWithL9 = getPlanetsInHouse(chart, l9Pos).filter((p) => p !== l9);
  return planetsWithL9.some(
    (p) => (HOUSE_STRENGTHS_OF_PLANETS[p]?.[l9Pos] ?? 0) >= STRENGTH_EXALTED
  );
};
export const bhaarathiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bhaarathiYoga(planetPositionsToChart(positions));

// ============================================================================
// SWAVEERYADDHANA YOGA (simplified - rasi-only)
// ============================================================================

/** Swaveeryaddhana Yoga (simplified): L2 in kendra/trine from L1, or L2 benefic and exalted */
export const swaveeryaddhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l1 = getLordOfSign(ascHouse);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const l1H = h(pToH, l1);
  const l2H = h(pToH, l2);

  // (c) L2 in kendra/trine from L1
  const relPos = (l2H - l1H + 12) % 12;
  const kendraTrine = [HOUSE_1, HOUSE_4, HOUSE_5, HOUSE_7, HOUSE_9, HOUSE_10];
  if (kendraTrine.includes(relPos)) return true;

  // (d/e) L2 is benefic AND exalted
  const benefics = getNaturalBenefics(chart);
  const l2Strength = HOUSE_STRENGTHS_OF_PLANETS[l2]?.[l2H] ?? 0;
  if (benefics.includes(l2) && l2Strength >= STRENGTH_EXALTED) return true;

  return false;
};
export const swaveeryaddhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  swaveeryaddhanaYoga(planetPositionsToChart(positions));

// ============================================================================
// REMAINING YOGA FUNCTIONS (Batch 3)
// ============================================================================

/**
 * Matsya Yoga (method=2, Parashara/PVR default):
 * (1) Benefics in Lagna AND 9th
 * (2) 5th contains BOTH benefics AND malefics
 * (3) 4th AND 8th contain ONLY malefics (and at least one in each)
 */
export const matsyaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const benefics = new Set(getNaturalBenefics(chart));
  const malefics = new Set(getNaturalMalefics(chart));

  const lagnaAbs = ascHouse;
  const fifthAbs = (ascHouse + HOUSE_5) % 12;
  const ninthAbs = (ascHouse + HOUSE_9) % 12;
  const fourthAbs = (ascHouse + HOUSE_4) % 12;
  const eighthAbs = (ascHouse + HOUSE_8) % 12;

  const occupants = (hIdx: number) => SUN_TO_KETU.filter(p => h(pToH, p) === hIdx);

  const occLagna = new Set(occupants(lagnaAbs));
  const occFifth = new Set(occupants(fifthAbs));
  const occNinth = new Set(occupants(ninthAbs));
  const occFourth = new Set(occupants(fourthAbs));
  const occEighth = new Set(occupants(eighthAbs));

  // Method 2 (Parashara): benefics in lagna and 9th
  const lagnaOk = [...occLagna].some(p => benefics.has(p)) && [...occLagna].every(p => benefics.has(p));
  const ninthOk = [...occNinth].some(p => benefics.has(p)) && [...occNinth].every(p => benefics.has(p));
  const cond1 = lagnaOk && ninthOk;

  // 5th must contain BOTH benefic and malefic
  const cond2 = [...occFifth].some(p => benefics.has(p)) && [...occFifth].some(p => malefics.has(p));

  // 4th & 8th ONLY malefics (and present)
  const cond3 = occFourth.size > 0 && [...occFourth].every(p => malefics.has(p)) &&
                occEighth.size > 0 && [...occEighth].every(p => malefics.has(p));

  return cond1 && cond2 && cond3;
};
export const matsyaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  matsyaYoga(planetPositionsToChart(positions));

/**
 * Mooka Yoga: The 2nd lord should join the 8th with Jupiter.
 * Does not apply if 8th house is Jupiter's own or exaltation sign.
 */
export const mookaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const house2 = (ascHouse + HOUSE_2) % 12;
  const house8 = (ascHouse + HOUSE_8) % 12;
  const lordOf2 = getLordOfSign(house2);

  // 2nd lord and Jupiter in 8th house
  const condMain = h(pToH, lordOf2) === house8 && h(pToH, JUPITER) === house8;

  // Exception: if 8th house is Jupiter's own or exaltation sign
  const jupStrength = HOUSE_STRENGTHS_OF_PLANETS[JUPITER]?.[house8] ?? 0;
  const jupExalted = jupStrength >= STRENGTH_EXALTED;

  return condMain && !jupExalted;
};
export const mookaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  mookaYoga(planetPositionsToChart(positions));

/**
 * Netranasa Yoga: Lords of 10th and 6th occupy Lagna with 2nd lord,
 * or they are in debilitation.
 */
export const netranasaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const house2 = (ascHouse + HOUSE_2) % 12;
  const house6 = (ascHouse + HOUSE_6) % 12;
  const house10 = (ascHouse + HOUSE_10) % 12;

  const lordOf2 = getLordOfSign(house2);
  const lordOf6 = getLordOfSign(house6);
  const lordOf10 = getLordOfSign(house10);

  // Condition A: Lords of 10, 6, and 2 occupy Lagna
  const condA = h(pToH, lordOf10) === ascHouse &&
                h(pToH, lordOf6) === ascHouse &&
                h(pToH, lordOf2) === ascHouse;

  // Condition B: Lords of 10, 6, and 2 are debilitated
  const deb2 = (HOUSE_STRENGTHS_OF_PLANETS[lordOf2]?.[h(pToH, lordOf2)] ?? 0) === STRENGTH_DEBILITATED;
  const deb6 = (HOUSE_STRENGTHS_OF_PLANETS[lordOf6]?.[h(pToH, lordOf6)] ?? 0) === STRENGTH_DEBILITATED;
  const deb10 = (HOUSE_STRENGTHS_OF_PLANETS[lordOf10]?.[h(pToH, lordOf10)] ?? 0) === STRENGTH_DEBILITATED;
  const condB = deb2 && deb6 && deb10;

  return condA || condB;
};
export const netranasaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  netranasaYoga(planetPositionsToChart(positions));

/**
 * Asatyavadi Yoga: Lord of 2nd occupies sign owned by Saturn or Mars,
 * and malefics join kendras and trikonas.
 */
export const asatyavadiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const secondHouse = (ascHouse + HOUSE_2) % 12;
  const lordOf2 = getLordOfSign(secondHouse);
  const lord2Pos = h(pToH, lordOf2);
  const dispositorOf2Lord = getLordOfSign(lord2Pos);

  // 1. Lord of 2nd must be in sign owned by Saturn or Mars
  if (dispositorOf2Lord !== SATURN && dispositorOf2Lord !== MARS) return false;

  // 2. Malefics in kendras and trikonas
  const malefics = getNaturalMalefics(chart);
  const quads = getQuadrants(ascHouse);
  const tris = getTrines(ascHouse);
  const targetHouses = new Set([...quads, ...tris]);

  return malefics.some(p => targetHouses.has(h(pToH, p)));
};
export const asatyavadiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  asatyavadiYoga(planetPositionsToChart(positions));

/**
 * Jada Yoga: 2nd lord in 10th with malefics, OR 2nd house joined by Sun and Mandi.
 * Simplified: Without mandi data, only checks criterion A.
 */
export const jadaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const secondHouse = (ascHouse + HOUSE_2) % 12;
  const tenthHouse = (ascHouse + HOUSE_10) % 12;
  const lordOf2 = getLordOfSign(secondHouse);
  const malefics = getNaturalMalefics(chart);

  // Criterion A: 2nd Lord in 10th with malefics
  if (h(pToH, lordOf2) === tenthHouse) {
    for (const m of malefics) {
      if (m !== lordOf2 && h(pToH, m) === tenthHouse) return true;
    }
  }

  // Criterion B: Sun and Mandi in 2nd -- cannot check without mandi data
  return false;
};
export const jadaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  jadaYoga(planetPositionsToChart(positions));

/**
 * Bhratrumooladdhanaprapti Yoga (BV Raman 136/137):
 * Wealth from brothers. L1 and L2 in 3rd aspected by benefics,
 * or L3 in 2nd with Jupiter aspected by L1.
 * Note: Vaiseshikamsa check simplified (always false without scores).
 */
export const bhratrumooladdhanapraptiYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l1 = getLordOfSign(ascHouse);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const l3 = getLordOfSign((ascHouse + HOUSE_3) % 12);
  const benefics = getNaturalBenefics(chart);
  const h3 = (ascHouse + HOUSE_3) % 12;
  const h2 = (ascHouse + HOUSE_2) % 12;

  // 136: L1 and L2 in 3rd, 3rd aspected by benefic
  const l1L2In3 = h(pToH, l1) === h3 && h(pToH, l2) === h3;
  if (l1L2In3) {
    const h3AspectedByBenefic = benefics.some(b => {
      const aspectedRasis = getGrahaDrishtiRasisOfPlanet(chart, b);
      return aspectedRasis.includes(h3);
    });
    if (h3AspectedByBenefic) return true;
  }

  // 137: L3 in 2nd with Jupiter, aspected or conjoined by L1
  const l3In2 = h(pToH, l3) === h2;
  const planetsInH2 = getPlanetsInHouse(chart, h2);
  const withJupiter = planetsInH2.includes(JUPITER);
  const l1AspectsL3 = getGrahaDrishtiPlanetsOfPlanet(chart, l1).includes(l3);
  const l1ConjL3 = h(pToH, l1) === h(pToH, l3);

  // Without vaiseshikamsa scores, this condition always fails (conservative)
  return l3In2 && withJupiter && (l1AspectsL3 || l1ConjL3) && false;
};
export const bhratrumooladdhanapraptiYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  bhratrumooladdhanapraptiYoga(planetPositionsToChart(positions));

/**
 * Putramooladdhana Yoga (BV Raman 139):
 * Strong lord of 2nd conjunct 5th lord or Jupiter, and L1 in Vaiseshikamsa.
 * Simplified: without vaiseshikamsa scores, always returns false.
 */
export const putramooladdhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const l5 = getLordOfSign((ascHouse + HOUSE_5) % 12);
  const l2H = h(pToH, l2);
  const l2Strong = (HOUSE_STRENGTHS_OF_PLANETS[l2]?.[l2H] ?? 0) >= STRENGTH_EXALTED;

  const planetsInL2H = getPlanetsInHouse(chart, l2H);
  const conj = h(pToH, l2) === h(pToH, l5) || planetsInL2H.includes(JUPITER);

  // Vaiseshikamsa check: requires external data, return false conservatively
  return l2Strong && conj && false;
};
export const putramooladdhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  putramooladdhanaYoga(planetPositionsToChart(positions));

/**
 * Shatrumooladdhana Yoga (BV Raman 140):
 * Strong lord of 2nd joins 6th lord or Mars, and L1 in Vaiseshikamsa.
 * Simplified: without vaiseshikamsa scores, always returns false.
 */
export const shatrumooladdhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const l2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const l6 = getLordOfSign((ascHouse + HOUSE_6) % 12);
  const l2H = h(pToH, l2);
  const l2Strong = (HOUSE_STRENGTHS_OF_PLANETS[l2]?.[l2H] ?? 0) >= STRENGTH_EXALTED;

  const planetsInL2H = getPlanetsInHouse(chart, l2H);
  const conj = h(pToH, l2) === h(pToH, l6) || planetsInL2H.includes(MARS);

  // Vaiseshikamsa check: requires external data, return false conservatively
  return l2Strong && conj && false;
};
export const shatrumooladdhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  shatrumooladdhanaYoga(planetPositionsToChart(positions));

/**
 * Amaranantha Dhana Yoga (BV Raman 142):
 * Multiple planets (>=3) in 2nd house, wealth-giving planets strong.
 */
export const amarananthaDhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const h2 = (ascHouse + HOUSE_2) % 12;

  const planetsIn2 = getPlanetsInHouse(chart, h2);
  if (planetsIn2.length < 3) return false;

  const l2 = getLordOfSign(h2);
  const l11 = getLordOfSign((ascHouse + HOUSE_11) % 12);
  const wealthPlanets = new Set([l2, l11, JUPITER]);

  return [...wealthPlanets].some(p => planetsIn2.includes(p) && (HOUSE_STRENGTHS_OF_PLANETS[p]?.[h2] ?? 0) >= STRENGTH_EXALTED);
};
export const amarananthaDhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  amarananthaDhanaYoga(planetPositionsToChart(positions));

/**
 * Ayatnadhanalabha Yoga (BV Raman 143):
 * Lords of Lagna and 2nd exchange positions.
 */
export const ayatnadhanalabhaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const secondHouse = (ascHouse + HOUSE_2) % 12;
  const lagnaLord = getLordOfSign(ascHouse);
  const secondLord = getLordOfSign(secondHouse);

  return h(pToH, secondLord) === ascHouse && h(pToH, lagnaLord) === secondHouse;
};
export const ayatnadhanalabhaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  ayatnadhanalabhaYoga(planetPositionsToChart(positions));

/**
 * Parannabhojana Yoga: Lord of 2nd debilitated OR in unfriendly navamsa,
 * AND aspected by a debilitated planet.
 * Simplified: navamsa check omitted, only rasi debilitation used.
 */
export const parannabhojanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const house2 = (ascHouse + HOUSE_2) % 12;
  const lordOf2 = getLordOfSign(house2);

  // Check if lord of 2nd is debilitated
  const l2Strength = HOUSE_STRENGTHS_OF_PLANETS[lordOf2]?.[h(pToH, lordOf2)] ?? 0;
  const isDebRasi = l2Strength === STRENGTH_DEBILITATED;
  if (!isDebRasi) return false;

  // Check if aspected by a debilitated planet
  const aspectedBy = getGrahaDrishtiOnPlanet(chart, lordOf2);
  return aspectedBy.some(p => {
    const pStrength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[h(pToH, p)] ?? 0;
    return pStrength === STRENGTH_DEBILITATED;
  });
};
export const parannabhojanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  parannabhojanaYoga(planetPositionsToChart(positions));

/**
 * Sraddhannabhuktha Yoga: Saturn owns 2nd, OR joins 2nd lord,
 * OR debilitated Saturn aspects 2nd house.
 */
export const sraddhannabhukthaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const house2 = (ascHouse + HOUSE_2) % 12;
  const lordOf2 = getLordOfSign(house2);

  // Condition 1: Saturn owns the 2nd house
  const cond1 = lordOf2 === SATURN;

  // Condition 2: Saturn joins the 2nd lord (same house)
  const cond2 = h(pToH, lordOf2) === h(pToH, SATURN);

  // Condition 3: Debilitated Saturn aspects 2nd house
  const saturnStrength = HOUSE_STRENGTHS_OF_PLANETS[SATURN]?.[h(pToH, SATURN)] ?? 0;
  const isSaturnDebilitated = saturnStrength === STRENGTH_DEBILITATED;
  let cond3 = false;
  if (isSaturnDebilitated) {
    const aspectedHouses = getGrahaDrishtiHousesOfPlanet(chart, SATURN);
    cond3 = aspectedHouses.includes(house2);
  }

  return cond1 || cond2 || cond3;
};
export const sraddhannabhukthaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  sraddhannabhukthaYoga(planetPositionsToChart(positions));

/**
 * Sarpaganda Yoga: Rahu should join the 2nd house with Mandi.
 * Simplified: Without mandi data, always returns false.
 */
export const sarpagandaYoga = (_chart: HouseChart): boolean => {
  // Requires mandi house data which is not available from chart alone
  return false;
};
export const sarpagandaYogaFromPlanetPositions = (_positions: PlanetPosition[]): boolean => false;

/**
 * Balya Dhana Yoga: Lord of 2nd is a benefic, exalted or conjunct exalted planet.
 */
export const balyaDhanaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const lordOf2 = getLordOfSign((ascHouse + HOUSE_2) % 12);
  const benefics = getNaturalBenefics(chart);
  const l2House = h(pToH, lordOf2);

  const isExalted = (HOUSE_STRENGTHS_OF_PLANETS[lordOf2]?.[l2House] ?? 0) >= STRENGTH_EXALTED;

  // Check if conjunct an exalted planet
  const others = getPlanetsInHouse(chart, l2House).filter(p => p !== lordOf2);
  const isWithExalted = others.some(p => (HOUSE_STRENGTHS_OF_PLANETS[p]?.[l2House] ?? 0) >= STRENGTH_EXALTED);

  return benefics.includes(lordOf2) && (isExalted || isWithExalted);
};
export const balyaDhanaYogaFromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  balyaDhanaYoga(planetPositionsToChart(positions));

// Aliases for naming variants
// ============================================================================
// UTILITY: Lord Exchange Check
// ============================================================================

/**
 * Check if two lords are exchanged (mutual reception).
 * lord1 occupies lord2_house and lord2 occupies lord1_house.
 */
export const areLordsExchanged = (
  p2h: PlanetToHouseMap,
  lord1: number, lord1House: number,
  lord2: number, lord2House: number,
): boolean => {
  return p2h[lord1] === lord2House && p2h[lord2] === lord1House;
};

// ============================================================================
// DHANA YOGAS 123-128 (BV Raman)
// ============================================================================

/**
 * Dhana Yogas #123-128 (BV Raman).
 * Planet in Lagna (own sign) joined or aspected by specific planets.
 */
export const dhanaYoga123_128 = (chart: HouseChart): boolean => {
  const p2h = getPlanetToHouseDict(chart);
  const ascHouse = p2h[ASCENDANT_SYMBOL]!;

  const isPlanetInfluencedBy = (target: number, influencers: number[]): boolean => {
    const aspecting = getGrahaDrishtiOnPlanet(chart, target);
    for (const inf of influencers) {
      const conjoined = p2h[target] === p2h[inf];
      const aspected = aspecting.includes(inf);
      if (!conjoined && !aspected) return false;
    }
    return true;
  };

  // 123: Sun in Leo Lagna + Mars and Jupiter
  if (ascHouse === LEO && p2h[SUN] === ascHouse) {
    if (isPlanetInfluencedBy(SUN, [MARS, JUPITER])) return true;
  }
  // 124: Moon in Cancer Lagna + Jupiter and Mars
  if (ascHouse === CANCER && p2h[MOON] === ascHouse) {
    if (isPlanetInfluencedBy(MOON, [JUPITER, MARS])) return true;
  }
  // 125: Mars in Aries/Scorpio Lagna + Moon, Venus, Saturn
  if ((ascHouse === ARIES || ascHouse === SCORPIO) && p2h[MARS] === ascHouse) {
    if (isPlanetInfluencedBy(MARS, [MOON, VENUS, SATURN])) return true;
  }
  // 126: Mercury in Gemini/Virgo Lagna + Saturn and Venus
  if ((ascHouse === GEMINI || ascHouse === VIRGO) && p2h[MERCURY] === ascHouse) {
    if (isPlanetInfluencedBy(MERCURY, [SATURN, VENUS])) return true;
  }
  // 127: Jupiter in Sagittarius/Pisces Lagna + Mercury and Mars
  if ((ascHouse === SAGITTARIUS || ascHouse === PISCES) && p2h[JUPITER] === ascHouse) {
    if (isPlanetInfluencedBy(JUPITER, [MERCURY, MARS])) return true;
  }
  // 128: Venus in Taurus/Libra Lagna + Saturn and Mercury
  if ((ascHouse === TAURUS || ascHouse === LIBRA) && p2h[VENUS] === ascHouse) {
    if (isPlanetInfluencedBy(VENUS, [SATURN, MERCURY])) return true;
  }
  return false;
};

export const dhanaYoga123_128FromPlanetPositions = (positions: PlanetPosition[]): boolean =>
  dhanaYoga123_128(planetPositionsToChart(positions));

export const areLordsExchangedFromPlanetPositions = areLordsExchanged;

export const lagnaadhiYoga = lagnaAdhiYoga;
export const lagnaadhiYogaFromPlanetPositions = lagnaAdhiYogaFromPlanetPositions;
export const sreenaathaYoga = sreenaatheYoga;
export const sreenaathaYogaFromPlanetPositions = sreenaatheYogaFromPlanetPositions;
export const sreenathaYoga = sreenataYoga;
export const sreenathaYogaFromPlanetPositions = sreenataYogaFromPlanetPositions;
export const vanchanaChoraBheethiYoga = vanchanaChoraYoga;
export const vanchanaChoraBheethiYogaFromPlanetPositions = vanchanaChoraYogaFromPlanetPositions;
export const kaahalaYoga = kahalaYoga;
export const kaahalaYogaFromPlanetPositions = kahalaYogaFromPlanetPositions;

// ============================================================================
// YOGA DETECTION (Batch Processing)
// ============================================================================

/**
 * Detect all yogas present in the chart
 */
export const detectAllYogas = (chart: HouseChart): YogaResult[] => {
  const results: YogaResult[] = [];

  // Sun Yogas
  results.push({ name: 'Vesi Yoga', isPresent: vesiYoga(chart) });
  results.push({ name: 'Vosi Yoga', isPresent: vosiYoga(chart) });
  results.push({ name: 'Ubhayachara Yoga', isPresent: ubhayacharaYoga(chart) });
  results.push({ name: 'Nipuna/Budha-Aaditya Yoga', isPresent: nipunaYoga(chart) });

  // Moon Yogas
  results.push({ name: 'Sunaphaa Yoga', isPresent: sunaphaaYoga(chart) });
  results.push({ name: 'Anaphaa Yoga', isPresent: anaphaaYoga(chart) });
  results.push({ name: 'Duradhara Yoga', isPresent: duradharaYoga(chart) });
  results.push({ name: 'Kemadruma Yoga', isPresent: kemadrumaYoga(chart) });
  results.push({ name: 'Chandra-Mangala Yoga', isPresent: chandraMangalaYoga(chart) });
  results.push({ name: 'Adhi Yoga', isPresent: adhiYoga(chart) });

  // Pancha Mahapurusha
  results.push({ name: 'Ruchaka Yoga', isPresent: ruchakaYoga(chart) });
  results.push({ name: 'Bhadra Yoga', isPresent: bhadraYoga(chart) });
  results.push({ name: 'Sasa Yoga', isPresent: sasaYoga(chart) });
  results.push({ name: 'Maalavya Yoga', isPresent: maalavyaYoga(chart) });
  results.push({ name: 'Hamsa Yoga', isPresent: hamsaYoga(chart) });

  // Naabhasa Yogas
  results.push({ name: 'Rajju Yoga', isPresent: rajjuYoga(chart) });
  results.push({ name: 'Musala Yoga', isPresent: musalaYoga(chart) });
  results.push({ name: 'Nala Yoga', isPresent: nalaYoga(chart) });
  results.push({ name: 'Maalaa/Srik Yoga', isPresent: maalaaYoga(chart) });
  results.push({ name: 'Sarpa Yoga', isPresent: sarpaYoga(chart) });

  // Aakriti Yogas
  results.push({ name: 'Gadaa Yoga', isPresent: gadaaYoga(chart) });
  results.push({ name: 'Sakata Yoga', isPresent: sakataYoga(chart) });
  results.push({ name: 'Vihanga Yoga', isPresent: vihangaYoga(chart) });
  results.push({ name: 'Sringaataka Yoga', isPresent: sringaatakaYoga(chart) });
  results.push({ name: 'Hala Yoga', isPresent: halaYoga(chart) });
  results.push({ name: 'Vajra Yoga', isPresent: vajraYoga(chart) });
  results.push({ name: 'Yava Yoga', isPresent: yavaYoga(chart) });
  results.push({ name: 'Kamala Yoga', isPresent: kamalaYoga(chart) });
  results.push({ name: 'Vaapi Yoga', isPresent: vaapiYoga(chart) });
  results.push({ name: 'Yoopa Yoga', isPresent: yoopaYoga(chart) });
  results.push({ name: 'Sara Yoga', isPresent: saraYoga(chart) });
  results.push({ name: 'Sakti Yoga', isPresent: saktiYoga(chart) });
  results.push({ name: 'Danda Yoga', isPresent: dandaYoga(chart) });
  results.push({ name: 'Naukaa Yoga', isPresent: naukaaYoga(chart) });
  results.push({ name: 'Koota Yoga', isPresent: kootaYoga(chart) });
  results.push({ name: 'Chatra Yoga', isPresent: chatraYoga(chart) });
  results.push({ name: 'Chaapa Yoga', isPresent: chaapaYoga(chart) });
  results.push({ name: 'Ardha Chandra Yoga', isPresent: ardhaChandraYoga(chart) });
  results.push({ name: 'Chakra Yoga', isPresent: chakraYoga(chart) });
  results.push({ name: 'Samudra Yoga', isPresent: samudraYoga(chart) });

  // Sankhya Yogas
  results.push({ name: 'Veenaa Yoga', isPresent: veenaaYoga(chart) });
  results.push({ name: 'Daama Yoga', isPresent: daamaYoga(chart) });
  results.push({ name: 'Paasa Yoga', isPresent: paasaYoga(chart) });
  results.push({ name: 'Kedaara Yoga', isPresent: kedaaraYoga(chart) });
  results.push({ name: 'Soola Yoga', isPresent: soolaYoga(chart) });
  results.push({ name: 'Yuga Yoga', isPresent: yugaYoga(chart) });
  results.push({ name: 'Gola Yoga', isPresent: golaYoga(chart) });

  // Subha/Asubha
  results.push({ name: 'Subha Yoga', isPresent: subhaYoga(chart) });
  results.push({ name: 'Asubha Yoga', isPresent: asubhaYoga(chart) });

  // Notable Planetary Yogas
  results.push({ name: 'Gaja Kesari Yoga', isPresent: gajaKesariYoga(chart) });
  results.push({ name: 'Guru-Mangala Yoga', isPresent: guruMangalaYoga(chart) });
  results.push({ name: 'Amala Yoga', isPresent: amalaYoga(chart) });
  results.push({ name: 'Parvata Yoga', isPresent: parvataYoga(chart) });

  // Viparita Raja Yogas
  results.push({ name: 'Harsha Yoga', isPresent: harshaYoga(chart) });
  results.push({ name: 'Sarala Yoga', isPresent: saralaYoga(chart) });
  results.push({ name: 'Vimala Yoga', isPresent: vimalaYoga(chart) });

  // Other
  results.push({ name: 'Chatussagara Yoga', isPresent: chatussagaraYoga(chart) });
  results.push({ name: 'Rajalakshana Yoga', isPresent: rajalakshanaYoga(chart) });
  results.push({ name: 'Lakshmi Yoga', isPresent: lakshmiYoga(chart) });
  results.push({ name: 'Dhana Yoga', isPresent: dhanaYoga(chart) });
  results.push({ name: 'Vasumathi Yoga', isPresent: vasumathiYoga(chart) });
  results.push({ name: 'Kahala Yoga', isPresent: kahalaYoga(chart) });
  results.push({ name: 'Trilochana Yoga', isPresent: trilochanaYoga(chart) });

  // Newly Ported Yogas
  results.push({ name: 'Marud Yoga', isPresent: marudYoga(chart) });
  results.push({ name: 'Budha Yoga', isPresent: budhaYoga(chart) });
  results.push({ name: 'Andha Yoga', isPresent: andhaYoga(chart) });
  results.push({ name: 'Chaamara Yoga', isPresent: chaamaraYoga(chart) });
  results.push({ name: 'Sankha Yoga', isPresent: sankhaYoga(chart) });
  results.push({ name: 'Khadga Yoga', isPresent: khadgaYoga(chart) });
  results.push({ name: 'Go Yoga', isPresent: goYoga(chart) });
  results.push({ name: 'Dharidhra Yoga', isPresent: dharidhraYoga(chart) });

  // Newly Ported Yogas (Batch 2)
  results.push({ name: 'Vallaki Yoga', isPresent: vallakiYoga(chart) });
  results.push({ name: 'Dama Yoga', isPresent: damaYoga(chart) });
  results.push({ name: 'Kedara Yoga', isPresent: kedaraYoga(chart) });
  results.push({ name: 'Sula Yoga', isPresent: sulaYoga(chart) });
  results.push({ name: 'Dhur Yoga', isPresent: dhurYoga(chart) });
  results.push({ name: 'Bheri Yoga', isPresent: bheriYoga(chart) });
  results.push({ name: 'Mridanga Yoga', isPresent: mridangaYoga(chart) });
  results.push({ name: 'Sreenaatha Yoga', isPresent: sreenaatheYoga(chart) });
  results.push({ name: 'Koorma Yoga', isPresent: koormaYoga(chart) });
  results.push({ name: 'Kusuma Yoga', isPresent: kusumaYoga(chart) });
  results.push({ name: 'Kalaanidhi Yoga', isPresent: kalaanidhiYoga(chart) });
  results.push({ name: 'Lagnaadhi Yoga', isPresent: lagnaAdhiYoga(chart) });
  results.push({ name: 'Hari Yoga', isPresent: hariYoga(chart) });
  results.push({ name: 'Hara Yoga', isPresent: haraYoga(chart) });
  results.push({ name: 'Brahma Yoga', isPresent: brahmaYoga(chart) });
  results.push({ name: 'Siva Yoga', isPresent: sivaYoga(chart) });
  results.push({ name: 'Devendra Yoga', isPresent: devendraYoga(chart) });
  results.push({ name: 'Indra Yoga', isPresent: indraYoga(chart) });
  results.push({ name: 'Ravi Yoga', isPresent: raviYoga(chart) });
  results.push({ name: 'Bhaaskara Yoga', isPresent: bhaaskaraYoga(chart) });
  results.push({ name: 'Kulavardhana Yoga', isPresent: kulavardhanaYoga(chart) });
  results.push({ name: 'Gandharva Yoga', isPresent: gandharvaYoga(chart) });
  results.push({ name: 'Vidyut Yoga', isPresent: vidyutYoga(chart) });
  results.push({ name: 'Chapa Yoga', isPresent: chapaYoga(chart) });
  results.push({ name: 'Pushkala Yoga', isPresent: pushkalaYoga(chart) });
  results.push({ name: 'Makuta Yoga', isPresent: makutaYoga(chart) });
  results.push({ name: 'Jaya Yoga', isPresent: jayaYoga(chart) });
  results.push({ name: 'Vanchana Chora Bheethi Yoga', isPresent: vanchanaChoraYoga(chart) });
  results.push({ name: 'Harihara Brahma Yoga', isPresent: hariharaBrahmaYoga(chart) });
  results.push({ name: 'Sreenatha Yoga', isPresent: sreenataYoga(chart) });
  results.push({ name: 'Parijatha Yoga', isPresent: parijathaYoga(chart) });
  results.push({ name: 'Gaja Yoga', isPresent: gajaYoga(chart) });
  results.push({ name: 'Kalanidhi Yoga', isPresent: kalanidhiYoga(chart) });
  results.push({ name: 'Saarada Yoga', isPresent: saaradaYoga(chart) });
  results.push({ name: 'Saraswathi Yoga', isPresent: saraswathiYoga(chart) });
  results.push({ name: 'Amsaavatara Yoga', isPresent: amsaavataraYoga(chart) });
  results.push({ name: 'Dehapushti Yoga', isPresent: dehapushtiYoga(chart) });
  results.push({ name: 'Rogagrastha Yoga', isPresent: rogagrasthaYoga(chart) });
  results.push({ name: 'Krisanga Yoga', isPresent: krisangaYoga(chart) });
  results.push({ name: 'Dehasthoulya Yoga', isPresent: dehasthoulyaYoga(chart) });
  results.push({ name: 'Sada Sanchara Yoga', isPresent: sadaSancharaYoga(chart) });
  results.push({ name: 'Bahudravyarjana Yoga', isPresent: bahudravyarjanaYoga(chart) });
  results.push({ name: 'Madhya Vayasi Dhana Yoga', isPresent: madhyaVayasiDhanaYoga(chart) });
  results.push({ name: 'Anthya Vayasi Dhana Yoga', isPresent: anthyaVayasiDhanaYoga(chart) });
  results.push({ name: 'Sareera Soukhya Yoga', isPresent: sareeraSoukhyaYoga(chart) });
  results.push({ name: 'Matrumooladdhana Yoga', isPresent: matrumooladdhanaYoga(chart) });
  results.push({ name: 'Kalatramooladdhana Yoga', isPresent: kalatramooladdhanaYoga(chart) });
  results.push({ name: 'Vishnu Yoga', isPresent: vishnuYoga(chart) });
  results.push({ name: 'Gouri Yoga', isPresent: gouriYoga(chart) });
  results.push({ name: 'Chandikaa Yoga', isPresent: chandikaaYoga(chart) });
  results.push({ name: 'Kalpadruma Yoga', isPresent: kalpadrumaYoga(chart) });
  results.push({ name: 'Bhaarathi Yoga', isPresent: bhaarathiYoga(chart) });
  results.push({ name: 'Swaveeryaddhana Yoga', isPresent: swaveeryaddhanaYoga(chart) });
  results.push({ name: 'Dhana Yoga 123-128', isPresent: dhanaYoga123_128(chart) });

  // Batch 3 Yogas
  results.push({ name: 'Matsya Yoga', isPresent: matsyaYoga(chart) });
  results.push({ name: 'Mooka Yoga', isPresent: mookaYoga(chart) });
  results.push({ name: 'Netranasa Yoga', isPresent: netranasaYoga(chart) });
  results.push({ name: 'Asatyavadi Yoga', isPresent: asatyavadiYoga(chart) });
  results.push({ name: 'Jada Yoga', isPresent: jadaYoga(chart) });
  results.push({ name: 'Bhratrumooladdhanaprapti Yoga', isPresent: bhratrumooladdhanapraptiYoga(chart) });
  results.push({ name: 'Putramooladdhana Yoga', isPresent: putramooladdhanaYoga(chart) });
  results.push({ name: 'Shatrumooladdhana Yoga', isPresent: shatrumooladdhanaYoga(chart) });
  results.push({ name: 'Amaranantha Dhana Yoga', isPresent: amarananthaDhanaYoga(chart) });
  results.push({ name: 'Ayatnadhanalabha Yoga', isPresent: ayatnadhanalabhaYoga(chart) });
  results.push({ name: 'Parannabhojana Yoga', isPresent: parannabhojanaYoga(chart) });
  results.push({ name: 'Sraddhannabhuktha Yoga', isPresent: sraddhannabhukthaYoga(chart) });
  results.push({ name: 'Sarpaganda Yoga', isPresent: sarpagandaYoga(chart) });
  results.push({ name: 'Balya Dhana Yoga', isPresent: balyaDhanaYoga(chart) });

  // Malika Yogas
  results.push({ name: 'Lagna Malika Yoga', isPresent: lagnaMalikaYoga(chart) });
  results.push({ name: 'Dhana Malika Yoga', isPresent: dhanaMalikaYoga(chart) });
  results.push({ name: 'Vikrama Malika Yoga', isPresent: vikramaMalikaYoga(chart) });
  results.push({ name: 'Sukha Malika Yoga', isPresent: sukhaMalikaYoga(chart) });
  results.push({ name: 'Putra Malika Yoga', isPresent: putraMalikaYoga(chart) });
  results.push({ name: 'Satru Malika Yoga', isPresent: satruMalikaYoga(chart) });
  results.push({ name: 'Kalatra Malika Yoga', isPresent: kalatraMalikaYoga(chart) });
  results.push({ name: 'Randhra Malika Yoga', isPresent: randhraMalikaYoga(chart) });
  results.push({ name: 'Bhagya Malika Yoga', isPresent: bhagyaMalikaYoga(chart) });
  results.push({ name: 'Karma Malika Yoga', isPresent: karmaMalikaYoga(chart) });
  results.push({ name: 'Labha Malika Yoga', isPresent: labhaMalikaYoga(chart) });
  results.push({ name: 'Vyaya Malika Yoga', isPresent: vyayaMalikaYoga(chart) });

  return results;
};

/**
 * Get only present yogas
 */
export const getPresentYogas = (chart: HouseChart): YogaResult[] => {
  return detectAllYogas(chart).filter((y) => y.isPresent);
};

/**
 * Detect all yogas from planet positions
 * @param positions - Array of PlanetPosition objects
 * @returns Array of YogaResult objects
 */
export const detectAllYogasFromPlanetPositions = (positions: PlanetPosition[]): YogaResult[] => {
  return detectAllYogas(planetPositionsToChart(positions));
};

/**
 * Get only present yogas from planet positions
 * @param positions - Array of PlanetPosition objects
 * @returns Array of YogaResult objects where isPresent is true
 */
export const getPresentYogasFromPlanetPositions = (positions: PlanetPosition[]): YogaResult[] => {
  return getPresentYogas(planetPositionsToChart(positions));
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // Helpers
  getPlanetToHouseDict,
  getPlanetsInHouse,
  isMercuryBenefic,
  getNaturalBenefics,
  getNaturalMalefics,
  isPlanetStrong,
  isPlanetExalted,
  getQuadrants,
  getTrines,
  getDushthanas,
  getHouseOwner,
  planetPositionsToChart,

  // Sun Yogas
  vesiYoga,
  vosiYoga,
  ubhayacharaYoga,
  nipunaYoga,
  budhaAadityaYoga,

  // Moon Yogas
  sunaphaaYoga,
  anaphaaYoga,
  duradharaYoga,
  dhurdhuraYoga,
  kemadrumaYoga,
  chandraMangalaYoga,
  adhiYoga,

  // Pancha Mahapurusha
  ruchakaYoga,
  bhadraYoga,
  sasaYoga,
  maalavyaYoga,
  hamsaYoga,

  // Naabhasa Yogas
  rajjuYoga,
  musalaYoga,
  nalaYoga,
  maalaaYoga,
  srikYoga,
  sarpaYoga,

  // Aakriti Yogas
  gadaaYoga,
  sakataYoga,
  vihangaYoga,
  vihagaYoga,
  sringaatakaYoga,
  halaYoga,
  vajraYoga,
  yavaYoga,
  kamalaYoga,
  vaapiYoga,
  yoopaYoga,
  saraYoga,
  ishuYoga,
  saktiYoga,
  dandaYoga,
  naukaaYoga,
  navYoga,
  kootaYoga,
  chatraYoga,
  chaapaYoga,
  ardhaChandraYoga,
  chakraYoga,
  samudraYoga,

  // Sankhya Yogas
  veenaaYoga,
  daamaYoga,
  paasaYoga,
  kedaaraYoga,
  soolaYoga,
  yugaYoga,
  golaYoga,

  // Subha/Asubha
  subhaYoga,
  asubhaYoga,

  // Notable Yogas
  gajaKesariYoga,
  guruMangalaYoga,
  amalaYoga,
  parvataYoga,

  // Viparita Raja
  harshaYoga,
  saralaYoga,
  vimalaYoga,

  // Other
  chatussagaraYoga,
  rajalakshanaYoga,
  lakshmiYoga,
  dhanaYoga,
  vasumathiYoga,
  kahalaYoga,
  trilochanaYoga,
  mahabhagyaYoga,

  // Newly Ported Yogas (Batch 1)
  marudYoga,
  budhaYoga,
  andhaYoga,
  chaamaraYoga,
  sankhaYoga,
  khadgaYoga,
  goYoga,
  dharidhraYoga,

  // Newly Ported Yogas (Batch 2)
  vallakiYoga,
  damaYoga,
  kedaraYoga,
  sulaYoga,
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
  madhyaVayasiDhanaYoga,
  anthyaVayasiDhanaYoga,
  sareeraSoukhyaYoga,
  matrumooladdhanaYoga,
  kalatramooladdhanaYoga,
  vishnuYoga,
  gouriYoga,
  chandikaaYoga,
  garudaYoga,
  kalpadrumaYoga,
  bhaarathiYoga,
  swaveeryaddhanaYoga,

  // Batch 3 Yogas
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
  sarpagandaYoga,
  balyaDhanaYoga,

  // Aliases
  lagnaadhiYoga,
  sreenaathaYoga,
  sreenathaYoga,
  vanchanaChoraBheethiYoga,
  kaahalaYoga,

  // Malika Yogas
  lagnaMalikaYoga,
  dhanaMalikaYoga,
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

  // Batch Detection
  detectAllYogas,
  getPresentYogas,

  // From Planet Positions variants
  vesiYogaFromPlanetPositions,
  vosiYogaFromPlanetPositions,
  ubhayacharaYogaFromPlanetPositions,
  nipunaYogaFromPlanetPositions,
  budhaAadityaYogaFromPlanetPositions,
  sunaphaaYogaFromPlanetPositions,
  anaphaaYogaFromPlanetPositions,
  duradharaYogaFromPlanetPositions,
  dhurdhuraYogaFromPlanetPositions,
  kemadrumaYogaFromPlanetPositions,
  chandraMangalaYogaFromPlanetPositions,
  adhiYogaFromPlanetPositions,
  ruchakaYogaFromPlanetPositions,
  bhadraYogaFromPlanetPositions,
  sasaYogaFromPlanetPositions,
  maalavyaYogaFromPlanetPositions,
  hamsaYogaFromPlanetPositions,
  rajjuYogaFromPlanetPositions,
  musalaYogaFromPlanetPositions,
  nalaYogaFromPlanetPositions,
  maalaaYogaFromPlanetPositions,
  srikYogaFromPlanetPositions,
  sarpaYogaFromPlanetPositions,
  gadaaYogaFromPlanetPositions,
  sakataYogaFromPlanetPositions,
  vihangaYogaFromPlanetPositions,
  vihagaYogaFromPlanetPositions,
  sringaatakaYogaFromPlanetPositions,
  halaYogaFromPlanetPositions,
  vajraYogaFromPlanetPositions,
  yavaYogaFromPlanetPositions,
  kamalaYogaFromPlanetPositions,
  vaapiYogaFromPlanetPositions,
  yoopaYogaFromPlanetPositions,
  saraYogaFromPlanetPositions,
  ishuYogaFromPlanetPositions,
  saktiYogaFromPlanetPositions,
  dandaYogaFromPlanetPositions,
  naukaaYogaFromPlanetPositions,
  navYogaFromPlanetPositions,
  kootaYogaFromPlanetPositions,
  chatraYogaFromPlanetPositions,
  chaapaYogaFromPlanetPositions,
  ardhaChandraYogaFromPlanetPositions,
  chakraYogaFromPlanetPositions,
  samudraYogaFromPlanetPositions,
  veenaaYogaFromPlanetPositions,
  daamaYogaFromPlanetPositions,
  paasaYogaFromPlanetPositions,
  kedaaraYogaFromPlanetPositions,
  soolaYogaFromPlanetPositions,
  yugaYogaFromPlanetPositions,
  golaYogaFromPlanetPositions,
  subhaYogaFromPlanetPositions,
  asubhaYogaFromPlanetPositions,
  gajaKesariYogaFromPlanetPositions,
  guruMangalaYogaFromPlanetPositions,
  amalaYogaFromPlanetPositions,
  parvataYogaFromPlanetPositions,
  harshaYogaFromPlanetPositions,
  saralaYogaFromPlanetPositions,
  vimalaYogaFromPlanetPositions,
  chatussagaraYogaFromPlanetPositions,
  rajalakshanaYogaFromPlanetPositions,
  trilochanaYogaFromPlanetPositions,
  mahabhagyaYogaFromPlanetPositions,
  kahalaYogaFromPlanetPositions,
  lakshmiYogaFromPlanetPositions,
  dhanaYogaFromPlanetPositions,
  vasumathiYogaFromPlanetPositions,
  lagnaMalikaYogaFromPlanetPositions,
  dhanaMalikaYogaFromPlanetPositions,
  vikramaMalikaYogaFromPlanetPositions,
  sukhaMalikaYogaFromPlanetPositions,
  putraMalikaYogaFromPlanetPositions,
  satruMalikaYogaFromPlanetPositions,
  kalatraMalikaYogaFromPlanetPositions,
  randhraMalikaYogaFromPlanetPositions,
  bhagyaMalikaYogaFromPlanetPositions,
  karmaMalikaYogaFromPlanetPositions,
  labhaMalikaYogaFromPlanetPositions,
  vyayaMalikaYogaFromPlanetPositions,
  marudYogaFromPlanetPositions,
  budhaYogaFromPlanetPositions,
  andhaYogaFromPlanetPositions,
  chaamaraYogaFromPlanetPositions,
  sankhaYogaFromPlanetPositions,
  khadgaYogaFromPlanetPositions,
  goYogaFromPlanetPositions,
  dharidhraYogaFromPlanetPositions,
  vallakiYogaFromPlanetPositions,
  damaYogaFromPlanetPositions,
  kedaraYogaFromPlanetPositions,
  sulaYogaFromPlanetPositions,
  dhurYogaFromPlanetPositions,
  bheriYogaFromPlanetPositions,
  mridangaYogaFromPlanetPositions,
  sreenaatheYogaFromPlanetPositions,
  koormaYogaFromPlanetPositions,
  kusumaYogaFromPlanetPositions,
  kalaanidhiYogaFromPlanetPositions,
  lagnaAdhiYogaFromPlanetPositions,
  hariYogaFromPlanetPositions,
  haraYogaFromPlanetPositions,
  brahmaYogaFromPlanetPositions,
  sivaYogaFromPlanetPositions,
  devendraYogaFromPlanetPositions,
  indraYogaFromPlanetPositions,
  raviYogaFromPlanetPositions,
  bhaaskaraYogaFromPlanetPositions,
  kulavardhanaYogaFromPlanetPositions,
  gandharvaYogaFromPlanetPositions,
  vidyutYogaFromPlanetPositions,
  chapaYogaFromPlanetPositions,
  pushkalaYogaFromPlanetPositions,
  makutaYogaFromPlanetPositions,
  jayaYogaFromPlanetPositions,
  vanchanaChoraYogaFromPlanetPositions,
  hariharaBrahmaYogaFromPlanetPositions,
  sreenataYogaFromPlanetPositions,
  parijathaYogaFromPlanetPositions,
  gajaYogaFromPlanetPositions,
  kalanidhiYogaFromPlanetPositions,
  saaradaYogaFromPlanetPositions,
  saraswathiYogaFromPlanetPositions,
  amsaavataraYogaFromPlanetPositions,
  dehapushtiYogaFromPlanetPositions,
  rogagrasthaYogaFromPlanetPositions,
  krisangaYogaFromPlanetPositions,
  dehasthoulyaYogaFromPlanetPositions,
  sadaSancharaYogaFromPlanetPositions,
  bahudravyarjanaYogaFromPlanetPositions,
  madhyaVayasiDhanaYogaFromPlanetPositions,
  anthyaVayasiDhanaYogaFromPlanetPositions,
  sareeraSoukhyaYogaFromPlanetPositions,
  matrumooladdhanaYogaFromPlanetPositions,
  kalatramooladdhanaYogaFromPlanetPositions,
  vishnuYogaFromPlanetPositions,
  gouriYogaFromPlanetPositions,
  chandikaaYogaFromPlanetPositions,
  garudaYogaFromPlanetPositions,
  kalpadrumaYogaFromPlanetPositions,
  bhaarathiYogaFromPlanetPositions,
  swaveeryaddhanaYogaFromPlanetPositions,
  matsyaYogaFromPlanetPositions,
  mookaYogaFromPlanetPositions,
  netranasaYogaFromPlanetPositions,
  asatyavadiYogaFromPlanetPositions,
  jadaYogaFromPlanetPositions,
  bhratrumooladdhanapraptiYogaFromPlanetPositions,
  putramooladdhanaYogaFromPlanetPositions,
  shatrumooladdhanaYogaFromPlanetPositions,
  amarananthaDhanaYogaFromPlanetPositions,
  ayatnadhanalabhaYogaFromPlanetPositions,
  parannabhojanaYogaFromPlanetPositions,
  sraddhannabhukthaYogaFromPlanetPositions,
  sarpagandaYogaFromPlanetPositions,
  balyaDhanaYogaFromPlanetPositions,
  lagnaadhiYogaFromPlanetPositions,
  sreenaathaYogaFromPlanetPositions,
  sreenathaYogaFromPlanetPositions,
  vanchanaChoraBheethiYogaFromPlanetPositions,
  kaahalaYogaFromPlanetPositions,
  detectAllYogasFromPlanetPositions,
  getPresentYogasFromPlanetPositions,
};
