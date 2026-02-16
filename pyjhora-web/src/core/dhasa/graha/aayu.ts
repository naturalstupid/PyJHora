/**
 * Aayu (Longevity) Dhasa System
 * Ported from PyJHora aayu.py
 *
 * Implements Pindayu, Nisargayu, and Amsayu longevity dasha calculations
 * with harana (strength reduction) and bharana (strength increase) factors.
 */

import {
  PINDAYU_FULL_LONGEVITY,
  NISARGAYU_FULL_LONGEVITY,
  PLANET_DEEP_EXALTATION_LONGITUDES,
  HOUSE_STRENGTHS_OF_PLANETS,
  STRENGTH_EXALTED,
  STRENGTH_DEBILITATED,
  SIDEREAL_YEAR,
  PLANET_NAMES_EN,
  ASCENDANT_SYMBOL,
} from '../../constants';
import type { PlanetPosition } from '../../horoscope/charts';
import {
  planetsInCombustion,
  planetsInRetrograde,
  beneficsAndMalefics,
  getDivisionalChart,
  orderPlanetsFromKendrasOfRaasi,
} from '../../horoscope/charts';
import { getRelativeHouseOfPlanet, getHouseOwnerFromPlanetPositions } from '../../horoscope/house';
import { julianDayToGregorian } from '../../utils/julian';
import { normalizeDegrees } from '../../utils/angle';

// ============================================================================
// CONSTANTS
// ============================================================================

const STRENGTH_OWNER = 3; // friend/own sign in house_strengths
const STRENGTH_ENEMY = 1;
const TOTAL_PINDAYU = PINDAYU_FULL_LONGEVITY.reduce((a, b) => a + b, 0);  // 127
const TOTAL_NISARGAYU = NISARGAYU_FULL_LONGEVITY.reduce((a, b) => a + b, 0); // 120
const TOTAL_AMSAYU = 120;

// ============================================================================
// TYPES
// ============================================================================

export interface AayuDashaPeriod {
  lord: number | string;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface AayuBhuktiPeriod {
  dashaLord: number | string;
  bhuktiLord: number | string;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface AayuResult {
  aayurType: number; // 0=Pindayu, 1=Nisargayu, 2=Amsayu
  aayurTypeName: string;
  totalLongevity: number;
  mahadashas: AayuDashaPeriod[];
  bhuktis: AayuBhuktiPeriod[];
}

type HaranaFactors = Record<number | string, number>;

// ============================================================================
// HELPERS
// ============================================================================

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  return `${date.year}-${pad(date.month)}-${pad(date.day)} ${pad(time.hour)}:${pad(time.minute)}:${pad(time.second)}`;
}

function lordName(lord: number | string): string {
  if (lord === ASCENDANT_SYMBOL || lord === -1) return 'Lagna';
  return PLANET_NAMES_EN[lord as number] ?? `Planet${lord}`;
}

// ============================================================================
// HARANA (STRENGTH REDUCTION) FUNCTIONS
// ============================================================================

/**
 * Astangata Harana: Reduce by 1/2 for combusted or retrograde planets.
 * Does not apply to Venus (5) and Saturn (6).
 */
export function astangataHarana(positions: PlanetPosition[]): HaranaFactors {
  const factors: HaranaFactors = { [ASCENDANT_SYMBOL]: 1.0 };
  for (let p = 0; p < 7; p++) factors[p] = 1.0;

  const combusted = planetsInCombustion(positions);
  const retrograde = planetsInRetrograde(positions);
  const ignore = [5, 6]; // Venus, Saturn

  for (const p of combusted) {
    if (!ignore.includes(p)) factors[p] = 0.5;
  }
  for (const p of retrograde) {
    if (!ignore.includes(p)) factors[p] = 0.5;
  }
  return factors;
}

/**
 * Shatru Kshetra Harana: Reduce by 1/3 for planets in enemy sign.
 * Does not apply to retrograde planets. Mars may be exempt.
 */
export function shatruKshetraHarana(
  positions: PlanetPosition[],
  treatMarsAsStrong: boolean = true,
): HaranaFactors {
  const factors: HaranaFactors = { [ASCENDANT_SYMBOL]: 1.0 };
  for (let p = 0; p < 7; p++) factors[p] = 1.0;

  const retrograde = planetsInRetrograde(positions);

  for (let p = 0; p < 7; p++) {
    const pos = positions[p + 1];
    if (!pos) continue;
    const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[pos.rasi] ?? 0;
    if (strength === STRENGTH_ENEMY) {
      if (treatMarsAsStrong && p === 2) continue; // Mars exempt
      if (retrograde.includes(p)) continue; // Retrograde exempt
      factors[p] = 2 / 3;
    }
  }
  return factors;
}

/**
 * Chakrapata Harana: Reduce based on planet's position above horizon.
 * Houses 7-12 (relative to Asc) get progressive reduction.
 * Benefics get less reduction than malefics.
 */
export function chakrapataHarana(
  positions: PlanetPosition[],
  subhaGrahas: number[],
  asubhaGrahas: number[],
): HaranaFactors {
  const factors: HaranaFactors = { [ASCENDANT_SYMBOL]: 1.0 };
  for (let p = 0; p < 7; p++) factors[p] = 1.0;

  const ascHouse = positions[0]!.rasi;
  // Reduction factors for houses 7-12 (relative): [subha_factor, asubha_factor]
  const subhaAsubhaFactors: Record<number, [number, number]> = {
    12: [0, 0.5],
    11: [0.5, 0.75],
    10: [2 / 3, 5 / 6],
    9: [3 / 4, 7 / 8],
    8: [4 / 5, 9 / 10],
    7: [5 / 6, 11 / 12],
  };

  for (const pos of positions) {
    const p = pos.planet;
    if (p < 0 || p > 6) continue;
    const relHouse = getRelativeHouseOfPlanet(ascHouse, pos.rasi);
    if (relHouse <= 6) continue;

    const entry = subhaAsubhaFactors[relHouse];
    if (!entry) continue;

    if (subhaGrahas.includes(p)) {
      factors[p] = entry[0];
    } else if (asubhaGrahas.includes(p)) {
      factors[p] = entry[1];
    }
  }
  return factors;
}

/**
 * Krurodaya Harana: Applied when a malefic rises in Lagna.
 * Reduction based on Lagna longitude fraction.
 */
export function krurodayaHarana(
  positions: PlanetPosition[],
  subhaGrahas: number[],
  asubhaGrahas: number[],
): HaranaFactors {
  const factors: HaranaFactors = { [ASCENDANT_SYMBOL]: 1.0 };
  for (let p = 0; p < 7; p++) factors[p] = 1.0;

  const ascLong = positions[0]!.rasi * 30 + positions[0]!.longitude;
  const khFraction = 1.0 - ascLong / 360.0;

  const ascHouse = positions[0]!.rasi;

  // Find malefics in lagna
  const maleficsInLagna: Array<{ planet: number; longDiff: number }> = [];
  for (const p of asubhaGrahas) {
    const pos = positions.find(pp => pp.planet === p);
    if (pos && pos.rasi === ascHouse) {
      maleficsInLagna.push({
        planet: p,
        longDiff: Math.abs(pos.longitude - positions[0]!.longitude),
      });
    }
  }

  if (maleficsInLagna.length === 0) return factors;

  // Sort by closest to lagna degree
  maleficsInLagna.sort((a, b) => a.longDiff - b.longDiff);
  const closestMalefic = maleficsInLagna[0]!.planet;

  // Check if a benefic is also in lagna and closer to lagna degree
  for (const sp of subhaGrahas) {
    const pos = positions.find(pp => pp.planet === sp);
    if (pos && pos.rasi === ascHouse) {
      const spDiff = Math.abs(pos.longitude - positions[0]!.longitude);
      if (spDiff < maleficsInLagna[0]!.longDiff) {
        return factors; // Benefic closer, ignore harana
      }
    }
  }

  let factor = khFraction;

  // If a benefic aspects the lagna, halve the harana
  // Simplified: check if any benefic is in quadrant/trine to lagna
  const beneficInLagna = subhaGrahas.some(sp => {
    const pos = positions.find(pp => pp.planet === sp);
    return pos && pos.rasi === ascHouse;
  });
  if (beneficInLagna) {
    factor = 0.5 * khFraction;
  }

  factors[closestMalefic] = factor;
  return factors;
}

/**
 * Bharana (increase factors) — only for Amsayu.
 * Multiply by 3 for retrograde/exalted/owner; by 2 for vargottama.
 */
export function bharana(positions: PlanetPosition[]): HaranaFactors {
  const factors: HaranaFactors = { [ASCENDANT_SYMBOL]: 1.0 };
  for (let p = 0; p < 7; p++) factors[p] = 1.0;

  const retrograde = planetsInRetrograde(positions);
  const pp9 = getDivisionalChart(positions, 9); // Navamsa
  const pp3 = getDivisionalChart(positions, 3); // Drekkana

  for (let p = 0; p < 7; p++) {
    const pos = positions[p + 1];
    if (!pos) continue;

    const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[pos.rasi] ?? 0;
    const isRetro = retrograde.includes(p);
    const isExalted = strength === STRENGTH_EXALTED;
    const isOwner = strength === STRENGTH_OWNER;

    if (isRetro || isExalted || isOwner) {
      factors[p] = 3.0;
      continue; // 3 takes precedence
    }

    // Check vargottama (rasi == navamsa rasi)
    const navPos = pp9[p + 1];
    const drekPos = pp3[p + 1];
    const isVargottama = navPos && pos.rasi === navPos.rasi;
    const isSvaNavamsa = navPos && (HOUSE_STRENGTHS_OF_PLANETS[p]?.[navPos.rasi] ?? 0) === STRENGTH_OWNER;
    const isSvaDrekkana = drekPos && (HOUSE_STRENGTHS_OF_PLANETS[p]?.[drekPos.rasi] ?? 0) === STRENGTH_OWNER;

    if (isVargottama || isSvaNavamsa || isSvaDrekkana) {
      factors[p] = 2.0;
    }
  }
  return factors;
}

// ============================================================================
// BASE LONGEVITY CALCULATIONS
// ============================================================================

/**
 * Apply all harana factors to base longevity values.
 */
function applyHarana(
  positions: PlanetPosition[],
  baseLongevity: HaranaFactors,
  subhaGrahas: number[],
  asubhaGrahas: number[],
  isAmsayu: boolean = false,
): HaranaFactors {
  const ah = astangataHarana(positions);
  const sh = shatruKshetraHarana(positions);
  const ch = chakrapataHarana(positions, subhaGrahas, asubhaGrahas);
  const kh = krurodayaHarana(positions, subhaGrahas, asubhaGrahas);

  const result: HaranaFactors = {};
  for (const key of Object.keys(baseLongevity)) {
    const k = key === String(ASCENDANT_SYMBOL) ? ASCENDANT_SYMBOL : Number(key);
    const base = baseLongevity[k] ?? 0;
    const a = ah[k] ?? 1.0;
    const s = sh[k] ?? 1.0;
    const c = ch[k] ?? 1.0;
    const kr = kh[k] ?? 1.0;
    result[k] = base * a * s * c * kr;
  }
  return result;
}

/**
 * Calculate Pindayu base longevity for each planet.
 */
export function pindayu(
  positions: PlanetPosition[],
  applyHaranas: boolean = true,
  subhaGrahas: number[] = [4, 5],
  asubhaGrahas: number[] = [0, 2, 6],
): HaranaFactors {
  const baseLongevity: HaranaFactors = {};

  for (let planet = 0; planet < 7; planet++) {
    const pos = positions[planet + 1];
    if (!pos) continue;
    const planetLong = pos.rasi * 30 + pos.longitude;
    const exaltLong = PLANET_DEEP_EXALTATION_LONGITUDES[planet]!;
    const arcOfLongevity = normalizeDegrees(planetLong - exaltLong);
    const effectiveArc = arcOfLongevity > 180 ? arcOfLongevity - 180 : arcOfLongevity;
    baseLongevity[planet] = PINDAYU_FULL_LONGEVITY[planet]! * effectiveArc / 360.0;
  }

  if (applyHaranas) {
    return applyHarana(positions, baseLongevity, subhaGrahas, asubhaGrahas);
  }
  return baseLongevity;
}

/**
 * Calculate Nisargayu base longevity for each planet.
 */
export function nisargayu(
  positions: PlanetPosition[],
  applyHaranas: boolean = true,
  subhaGrahas: number[] = [4, 5],
  asubhaGrahas: number[] = [0, 2, 6],
): HaranaFactors {
  const baseLongevity: HaranaFactors = {};

  for (let planet = 0; planet < 7; planet++) {
    const pos = positions[planet + 1];
    if (!pos) continue;
    const planetLong = pos.rasi * 30 + pos.longitude;
    const exaltLong = PLANET_DEEP_EXALTATION_LONGITUDES[planet]!;
    const arcOfLongevity = normalizeDegrees(planetLong - exaltLong);
    const effectiveArc = arcOfLongevity > 180 ? arcOfLongevity - 180 : arcOfLongevity;
    baseLongevity[planet] = NISARGAYU_FULL_LONGEVITY[planet]! * effectiveArc / 360.0;
  }

  if (applyHaranas) {
    return applyHarana(positions, baseLongevity, subhaGrahas, asubhaGrahas);
  }
  return baseLongevity;
}

/**
 * Calculate Amsayu base longevity for each planet.
 * Includes bharana (strength increase) for Amsayu.
 */
export function amsayu(
  positions: PlanetPosition[],
  applyHaranas: boolean = true,
  method: number = 1,
  subhaGrahas: number[] = [4, 5],
  asubhaGrahas: number[] = [0, 2, 6],
): HaranaFactors {
  const baseLongevity: HaranaFactors = {};

  for (let planet = 0; planet < 7; planet++) {
    const pos = positions[planet + 1];
    if (!pos) continue;
    const planetLong = pos.rasi * 30 + pos.longitude;
    if (method === 2) {
      baseLongevity[planet] = ((planetLong * 60) / 200) % 12; // Varahamihira
    } else {
      baseLongevity[planet] = (planetLong * 108) % 12;
    }
  }

  if (applyHaranas) {
    const bh = bharana(positions);
    const ah = applyHarana(positions, baseLongevity, subhaGrahas, asubhaGrahas, true);
    const result: HaranaFactors = {};
    for (const key of Object.keys(ah)) {
      const k = Number(key);
      result[k] = (ah[k] ?? 0) * (bh[k] ?? 1.0);
    }
    return result;
  }
  return baseLongevity;
}

// ============================================================================
// LAGNA LONGEVITY
// ============================================================================

/**
 * Calculate lagna longevity from positions.
 * Compares rasi lagna lord strength vs navamsa lagna lord strength.
 */
export function lagnaLongevity(
  d1Positions: PlanetPosition[],
  navamsaPositions?: PlanetPosition[],
): number {
  const ascRasi = d1Positions[0]!.rasi;
  const ascLord = getHouseOwnerFromPlanetPositions(d1Positions, ascRasi);
  const ascLong = ascRasi * 30 + d1Positions[0]!.longitude;

  const pp9 = navamsaPositions ?? getDivisionalChart(d1Positions, 9);
  const ascNav = pp9[0]!.rasi;
  const ascNavLord = getHouseOwnerFromPlanetPositions(pp9, ascNav);
  const ascNavLong = ascNav * 30 + pp9[0]!.longitude;

  let lagnaAayu = ascLong / 30.0;
  const rasiStrength = HOUSE_STRENGTHS_OF_PLANETS[ascLord]?.[ascRasi] ?? 0;
  const navStrength = HOUSE_STRENGTHS_OF_PLANETS[ascNavLord]?.[ascNav] ?? 0;

  if (navStrength > rasiStrength) {
    lagnaAayu = ascNavLong / 30.0;
  }
  return lagnaAayu;
}

// ============================================================================
// AAYUR TYPE DETERMINATION
// ============================================================================

/**
 * Determine which Aayu type applies based on strongest of Lagna, Sun, Moon.
 * Returns 0 (Sun/Pindayu), 1 (Moon/Nisargayu), or -1 (Lagna/Amsayu).
 */
export function getAayurType(positions: PlanetPosition[]): number {
  // Compare lagna lord strength, sun position strength, moon position strength
  const ascRasi = positions[0]!.rasi;
  const sunRasi = positions[1]!.rasi;
  const moonRasi = positions[2]!.rasi;

  const ascLord = getHouseOwnerFromPlanetPositions(positions, ascRasi);
  const ascStrength = HOUSE_STRENGTHS_OF_PLANETS[ascLord]?.[ascRasi] ?? 0;
  const sunStrength = HOUSE_STRENGTHS_OF_PLANETS[0]?.[sunRasi] ?? 0;
  const moonStrength = HOUSE_STRENGTHS_OF_PLANETS[1]?.[moonRasi] ?? 0;

  if (sunStrength >= moonStrength && sunStrength >= ascStrength) return 0; // Pindayu
  if (moonStrength >= sunStrength && moonStrength >= ascStrength) return 1; // Nisargayu
  return -1; // Amsayu (Lagna)
}

// ============================================================================
// PUBLIC API
// ============================================================================

/**
 * Calculate Aayu (Longevity) Dhasa.
 * @param d1Positions - D1 planet positions (index 0 = Lagna)
 * @param jd - Julian Day for start date calculation
 * @param aayurType - Force type: 0=Pindayu, 1=Nisargayu, 2=Amsayu, undefined=auto
 * @param includeBhuktis - Include sub-periods
 * @param applyHaranas - Apply strength reductions
 * @returns AayuResult
 */
export function getAayuDhasa(
  d1Positions: PlanetPosition[],
  jd: number,
  aayurType?: number,
  includeBhuktis: boolean = true,
  applyHaranas: boolean = true,
): AayuResult {
  const [subhaGrahas, asubhaGrahas] = beneficsAndMalefics(d1Positions);

  // Determine type
  const sp = aayurType ?? getAayurType(d1Positions);
  let aayurTypeName: string;
  let dhasaDuration: HaranaFactors;

  if (sp === 0) {
    aayurTypeName = 'Pindayu';
    dhasaDuration = pindayu(d1Positions, applyHaranas, subhaGrahas, asubhaGrahas);
  } else if (sp === 1) {
    aayurTypeName = 'Nisargayu';
    dhasaDuration = nisargayu(d1Positions, applyHaranas, subhaGrahas, asubhaGrahas);
  } else {
    aayurTypeName = 'Amsayu';
    dhasaDuration = amsayu(d1Positions, applyHaranas, 1, subhaGrahas, asubhaGrahas);
  }

  // Add lagna longevity
  dhasaDuration[ASCENDANT_SYMBOL] = lagnaLongevity(d1Positions);

  // Get dhasa progression: order planets by kendras from seed
  const seedPlanet = sp === 0 ? 0 : sp === 1 ? 1 : -1; // Sun, Moon, or Lagna
  const seedHouse = d1Positions.find(p => p.planet === seedPlanet)?.rasi ?? d1Positions[0]!.rasi;

  let progression = orderPlanetsFromKendrasOfRaasi(d1Positions.slice(0, 8), seedHouse, true);
  // Ensure seed is first
  if (sp === 0 || sp === 1 || sp === -1) {
    progression = [seedPlanet, ...progression.filter(p => p !== seedPlanet)];
  }

  const oneYearDays = SIDEREAL_YEAR;
  let startJd = jd;

  const mahadashas: AayuDashaPeriod[] = [];
  const bhuktis: AayuBhuktiPeriod[] = [];

  const totalLongevity = Object.values(dhasaDuration).reduce((a, b) => a + b, 0);

  for (const lord of progression) {
    const dd = dhasaDuration[lord] ?? 0;
    mahadashas.push({
      lord,
      lordName: lordName(lord),
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: dd,
    });

    if (includeBhuktis) {
      const ddb = dd / progression.length;
      for (const bhukti of progression) {
        bhuktis.push({
          dashaLord: lord,
          bhuktiLord: bhukti,
          bhuktiLordName: lordName(bhukti),
          startJd,
          startDate: formatJdAsDate(startJd),
          durationYears: ddb,
        });
        startJd += ddb * oneYearDays;
      }
    } else {
      startJd += dd * oneYearDays;
    }
  }

  return {
    aayurType: sp === -1 ? 2 : sp,
    aayurTypeName,
    totalLongevity,
    mahadashas,
    bhuktis,
  };
}
