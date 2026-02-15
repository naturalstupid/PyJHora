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
  ASCENDANT_SYMBOL,
} from '../constants';

import type { PlanetPosition } from '../types';

import {
  getQuadrantsOfRaasi,
  getTrinesOfRaasi,
  getLordOfSign,
} from './house';

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
export const getHouseOwner = (_chart: HouseChart, houseSign: number): number => {
  return getLordOfSign(houseSign);
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
 * Harsha Yoga: 6th lord in 6th, 8th, or 12th house
 */
export const harshaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const sixthSign = (ascHouse + HOUSE_6) % 12;
  const sixthLord = getLordOfSign(sixthSign);
  const lordHouse = pToH[sixthLord];
  const dushthanas = getDushthanas(ascHouse);
  return dushthanas.includes(lordHouse);
};

/**
 * Sarala Yoga: 8th lord in 6th, 8th, or 12th house
 */
export const saralaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const eighthSign = (ascHouse + HOUSE_8) % 12;
  const eighthLord = getLordOfSign(eighthSign);
  const lordHouse = pToH[eighthLord];
  const dushthanas = getDushthanas(ascHouse);
  return dushthanas.includes(lordHouse);
};

/**
 * Vimala Yoga: 12th lord in 6th, 8th, or 12th house
 */
export const vimalaYoga = (chart: HouseChart): boolean => {
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);
  const twelfthSign = (ascHouse + HOUSE_12) % 12;
  const twelfthLord = getLordOfSign(twelfthSign);
  const lordHouse = pToH[twelfthLord];
  const dushthanas = getDushthanas(ascHouse);
  return dushthanas.includes(lordHouse);
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
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const secondSign = (ascHouse + HOUSE_2) % 12;
  const eleventhSign = (ascHouse + HOUSE_11) % 12;
  const secondLord = getLordOfSign(secondSign);
  const eleventhLord = getLordOfSign(eleventhSign);

  // Check if lords are conjunct or in mutual quadrants
  const secondLordHouse = pToH[secondLord];
  const eleventhLordHouse = pToH[eleventhLord];

  // Conjunct
  if (secondLordHouse === eleventhLordHouse) return true;

  // In mutual quadrants
  const quadrantsOfSecond = getQuadrants(secondLordHouse);
  const quadrantsOfEleventh = getQuadrants(eleventhLordHouse);

  return (
    quadrantsOfSecond.includes(eleventhLordHouse) &&
    quadrantsOfEleventh.includes(secondLordHouse)
  );
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
  const pToH = getPlanetToHouseDict(chart);
  const ascHouse = h(pToH, ASCENDANT_SYMBOL);

  const fourthSign = (ascHouse + HOUSE_4) % 12;
  const fourthLord = getLordOfSign(fourthSign);
  const lagnaLord = getLordOfSign(ascHouse);

  const fourthLordHouse = h(pToH, fourthLord);
  const jupiterHouse = h(pToH, JUPITER);
  const lagnaLordHouse = h(pToH, lagnaLord);

  // 4th lord in quadrant from Jupiter
  const quadrantsOfJupiter = getQuadrants(jupiterHouse);
  if (!quadrantsOfJupiter.includes(fourthLordHouse)) return false;

  // Lagna lord strong
  return isPlanetStrong(lagnaLord, lagnaLordHouse, true);
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
  detectAllYogasFromPlanetPositions,
  getPresentYogasFromPlanetPositions,
};
