/**
 * Dosha (Affliction) Calculations
 * Ported from PyJHora dosha.py
 *
 * Provides checks for common doshas in Vedic astrology:
 * Kala Sarpa, Manglik, Pitru, Guru Chandala, Kalathra, Ganda Moola, Ghata, Shrapit
 */

import type { HouseChart } from '@core/types';
import type { PlanetPosition } from './charts';
import {
  getHouseToPlanetList,
  getPlanetToHouseDict,
  getRelativeHouseOfPlanet,
} from './house';
import {
  HOUSE_STRENGTHS_OF_PLANETS,
  JUPITER,
  KETU,
  LEO,
  AQUARIUS,
  MARS,
  NATURAL_MALEFICS,
  RAHU,
  SATURN,
  SUN,
  STRENGTH_FRIEND,
} from '@core/constants';

// ============================================================================
// GANDA MOOLA STARS (1-indexed nakshatra numbers)
// ============================================================================

/** Nakshatras that constitute Ganda Moola dosha */
const GANDA_MOOLA_STARS = [1, 9, 10, 18, 19, 27];

// ============================================================================
// HELPER: Parse HouseChart to planet-to-house dictionary
// ============================================================================

/**
 * Convert a HouseChart (string[12]) to a planet-to-house dictionary.
 * HouseChart entries contain planet IDs separated by '/' and 'L' for Lagna.
 * @param chart - HouseChart array of 12 strings
 * @returns Record mapping planet ID (or 'L') to house index (0-11)
 */
const parsePlanetToHouseFromChart = (
  chart: HouseChart
): Record<string, number> => {
  const result: Record<string, number> = {};
  for (let h = 0; h < 12; h++) {
    const entry = chart[h];
    if (!entry || entry.trim() === '') continue;
    const parts = entry.split('/');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed === 'L') {
        result['L'] = h;
      } else {
        const planetId = parseInt(trimmed, 10);
        if (!isNaN(planetId)) {
          result[String(planetId)] = h;
        }
      }
    }
  }
  return result;
};

// ============================================================================
// KALA SARPA DOSHA
// ============================================================================

/**
 * Check for Kala Sarpa Dosha.
 * All 7 planets (Sun=0 to Saturn=6) must be within one half (7 consecutive
 * houses) from either Rahu or Ketu.
 *
 * @param chart - HouseChart (string[12]) with planet placements
 * @returns true if Kala Sarpa Dosha is present
 */
export const kalaSarpa = (chart: HouseChart): boolean => {
  const pToH = parsePlanetToHouseFromChart(chart);

  const rahuHouseStr = pToH['7'];
  const ketuHouseStr = pToH['8'];

  if (rahuHouseStr === undefined || ketuHouseStr === undefined) return false;

  const rahuHouse = rahuHouseStr;
  const ketuHouse = ketuHouseStr;

  // Check if all planets 0-6 are within 7 consecutive houses from Rahu
  const checkFromNode = (nodeHouse: number): boolean => {
    for (let p = 0; p <= 6; p++) {
      const pHouse = pToH[String(p)];
      if (pHouse === undefined) return false;
      let found = false;
      for (let offset = 0; offset < 7; offset++) {
        if (pHouse === (nodeHouse + offset) % 12) {
          found = true;
          break;
        }
      }
      if (!found) return false;
    }
    return true;
  };

  return checkFromNode(rahuHouse) || checkFromNode(ketuHouse);
};

// ============================================================================
// MANGLIK DOSHA
// ============================================================================

/**
 * Check for Manglik Dosha (Kuja Dosha).
 * Mars in houses 2, 4, 7, 8, or 12 from the reference planet/lagna
 * indicates Manglik dosha.
 *
 * Simplified exceptions implemented:
 * 1. Mars in Leo (4) or Aquarius (10) sign
 * 7. Mars conjunct Jupiter or Saturn (same house)
 * 12. Mars in own/exalted/friend sign (strength >= FRIEND in HOUSE_STRENGTHS_OF_PLANETS)
 *
 * @param positions - Array of PlanetPosition (planet -1=Lagna, 0=Sun, ..., 8=Ketu)
 * @param referencePlanet - Planet ID or 'L' for Lagna (default: 'L')
 * @returns [isManglik, hasExceptions, exceptionIndices]
 */
export const manglik = (
  positions: PlanetPosition[],
  referencePlanet: number | 'L' = 'L'
): [boolean, boolean, number[]] => {
  const manglikHouses = [2, 4, 7, 8, 12];

  // Get reference house
  let refHouse: number;
  if (referencePlanet === 'L') {
    const lagna = positions.find((p) => p.planet === -1);
    if (!lagna) return [false, false, []];
    refHouse = lagna.rasi;
  } else {
    const refPos = positions.find((p) => p.planet === referencePlanet);
    if (!refPos) return [false, false, []];
    refHouse = refPos.rasi;
  }

  // Get Mars position
  const marsPos = positions.find((p) => p.planet === MARS);
  if (!marsPos) return [false, false, []];
  const marsHouse = marsPos.rasi;

  // Calculate relative house of Mars from reference
  const marsRelative = getRelativeHouseOfPlanet(refHouse, marsHouse);

  const isManglik = manglikHouses.includes(marsRelative);

  if (!isManglik) {
    return [false, false, []];
  }

  // Check exceptions
  const exceptionIndices: number[] = [];

  // Exception 1: Mars in Leo (4) or Aquarius (10)
  if (marsHouse === LEO || marsHouse === AQUARIUS) {
    exceptionIndices.push(1);
  }

  // Exception 7: Mars conjunct Jupiter or Saturn (same house)
  const jupiterPos = positions.find((p) => p.planet === JUPITER);
  const saturnPos = positions.find((p) => p.planet === SATURN);
  if (
    (jupiterPos && jupiterPos.rasi === marsHouse) ||
    (saturnPos && saturnPos.rasi === marsHouse)
  ) {
    exceptionIndices.push(7);
  }

  // Exception 12: Mars in own/exalted/friend sign (strength >= FRIEND)
  const marsStrength = HOUSE_STRENGTHS_OF_PLANETS[MARS]?.[marsHouse] ?? 0;
  if (marsStrength >= STRENGTH_FRIEND) {
    exceptionIndices.push(12);
  }

  const hasExceptions = exceptionIndices.length > 0;
  return [true, hasExceptions, exceptionIndices];
};

// ============================================================================
// PITRU DOSHA
// ============================================================================

/**
 * Check for Pitru (Pitra) Dosha.
 *
 * Conditions checked:
 * 1. Sun, Moon, or Rahu in 9th house from Lagna
 * 2. Ketu in 4th house from Lagna
 * 3. Mars or Saturn afflicting (same house as) Sun/Moon/Rahu/Ketu
 * 4. Two or more of Mercury, Venus, Rahu in houses 2, 5, 9, or 12 from Lagna
 * 5. Sun or Moon conjunct Rahu or Ketu
 *
 * @param positions - Array of PlanetPosition (planet -1=Lagna, 0=Sun, ..., 8=Ketu)
 * @returns [hasPitruDosha, conditionIndices]
 */
export const pitruDosha = (
  positions: PlanetPosition[]
): [boolean, number[]] => {
  const pToH = getPlanetToHouseDict(
    positions.map((p) => ({
      planet: p.planet,
      rasi: p.rasi,
      longitude: p.longitude,
    }))
  );

  // Get Lagna house
  const lagnaPos = positions.find((p) => p.planet === -1);
  if (!lagnaPos) return [false, []];
  const lagnaHouse = lagnaPos.rasi;

  const ninthHouse = (lagnaHouse + 8) % 12;
  const fourthHouse = (lagnaHouse + 3) % 12;

  const conditions: boolean[] = [];

  // Condition 1: Sun, Moon, or Rahu in 9th house from Lagna
  const sunH = pToH[SUN];
  const moonH = pToH[1]; // MOON
  const rahuH = pToH[RAHU];
  const pd1 =
    sunH === ninthHouse || moonH === ninthHouse || rahuH === ninthHouse;
  conditions.push(pd1);

  // Condition 2: Ketu in 4th house from Lagna
  const ketuH = pToH[KETU];
  const pd2 = ketuH === fourthHouse;
  conditions.push(pd2);

  // Condition 3: Mars or Saturn afflicting (same house as) Sun/Moon/Rahu/Ketu
  const marsH = pToH[MARS];
  const saturnH = pToH[SATURN];
  const targetPlanets = [SUN, 1, RAHU, KETU]; // Sun, Moon, Rahu, Ketu
  const pd3 = targetPlanets.some((tp) => {
    const tpH = pToH[tp];
    if (tpH === undefined) return false;
    return (marsH !== undefined && marsH === tpH) || (saturnH !== undefined && saturnH === tpH);
  });
  conditions.push(pd3);

  // Condition 4: Two or more of Mercury(3), Venus(5), Rahu(7) in houses 2,5,9,12 from Lagna
  const checkPlanets = [3, 5, 7]; // Mercury, Venus, Rahu
  const checkHouseOffsets = [2, 5, 9, 12]; // 1-based house numbers
  const pd4 = checkHouseOffsets.some((h) => {
    const targetSign = (lagnaHouse + h - 1) % 12;
    const count = checkPlanets.filter((cp) => pToH[cp] === targetSign).length;
    return count > 1;
  });
  conditions.push(pd4);

  // Condition 5: Sun or Moon conjunct Rahu or Ketu
  const pd5 = [SUN, 1].some((p1) => {
    const p1H = pToH[p1];
    return p1H !== undefined && (p1H === rahuH || p1H === ketuH);
  });
  conditions.push(pd5);

  const hasPitruDosha = conditions.some((c) => c);
  if (hasPitruDosha) {
    const indices = conditions
      .map((c, i) => (c ? i + 1 : -1))
      .filter((i) => i > 0);
    return [true, indices];
  }
  return [false, []];
};

// ============================================================================
// GURU CHANDALA DOSHA
// ============================================================================

/**
 * Check for Guru Chandala Dosha.
 * Jupiter conjunct Rahu or Ketu (same house).
 *
 * @param positions - Array of PlanetPosition
 * @returns [hasDosha, jupiterIsStronger]
 */
export const guruChandalaDosha = (
  positions: PlanetPosition[]
): [boolean, boolean] => {
  const jupiterPos = positions.find((p) => p.planet === JUPITER);
  const rahuPos = positions.find((p) => p.planet === RAHU);
  const ketuPos = positions.find((p) => p.planet === KETU);

  if (!jupiterPos) return [false, false];

  if (rahuPos && jupiterPos.rasi === rahuPos.rasi) {
    // Jupiter conjunct Rahu - compare longitudes within the sign
    const jupiterIsStronger = jupiterPos.longitude >= rahuPos.longitude;
    return [true, jupiterIsStronger];
  }

  if (ketuPos && jupiterPos.rasi === ketuPos.rasi) {
    // Jupiter conjunct Ketu - compare longitudes within the sign
    const jupiterIsStronger = jupiterPos.longitude >= ketuPos.longitude;
    return [true, jupiterIsStronger];
  }

  return [false, false];
};

// ============================================================================
// KALATHRA DOSHA
// ============================================================================

/**
 * Check for Kalathra Dosha.
 * ALL natural malefics (Sun, Mars, Saturn, Rahu, Ketu) must be in
 * houses 1, 2, 4, 7, 8, or 12 from the 7th house of the reference.
 *
 * In Python: reference_house = (lagna_rasi + 6) % 12 (i.e. 7th house from Lagna)
 * Then checks all malefics are in houses 1,2,4,7,8,12 from that reference_house.
 *
 * @param positions - Array of PlanetPosition
 * @param referencePlanet - Planet ID or 'L' for Lagna (default: 'L')
 * @returns true if Kalathra Dosha is present
 */
export const kalathra = (
  positions: PlanetPosition[],
  referencePlanet: number | 'L' = 'L'
): boolean => {
  // Determine the reference house (7th from Lagna or 7th from Moon)
  let referenceHouse: number;
  if (referencePlanet === 'L') {
    const lagna = positions.find((p) => p.planet === -1);
    if (!lagna) return false;
    referenceHouse = (lagna.rasi + 6) % 12;
  } else if (referencePlanet === 1) {
    // Moon reference: 7th from Moon
    const moonPos = positions.find((p) => p.planet === 1);
    if (!moonPos) return false;
    referenceHouse = (moonPos.rasi + 6) % 12;
  } else {
    const refPos = positions.find((p) => p.planet === referencePlanet);
    if (!refPos) return false;
    referenceHouse = (refPos.rasi + 6) % 12;
  }

  const kalathraHouses = [1, 2, 4, 7, 8, 12];

  // Check if ALL natural malefics are in the specified houses from reference
  return NATURAL_MALEFICS.every((malefic) => {
    const maleficPos = positions.find((p) => p.planet === malefic);
    if (!maleficPos) return false;
    const relHouse = getRelativeHouseOfPlanet(referenceHouse, maleficPos.rasi);
    return kalathraHouses.includes(relHouse);
  });
};

// ============================================================================
// GANDA MOOLA DOSHA
// ============================================================================

/**
 * Check for Ganda Moola Dosha based on Moon's nakshatra.
 *
 * @param moonStar - 1-indexed nakshatra number of the Moon
 * @returns true if the nakshatra is a Ganda Moola nakshatra
 */
export const gandaMoola = (moonStar: number): boolean => {
  return GANDA_MOOLA_STARS.includes(moonStar);
};

// ============================================================================
// GHATA DOSHA
// ============================================================================

/**
 * Check for Ghata Dosha.
 * Mars and Saturn conjunction (same house/rasi).
 *
 * In Python: planet_positions[3][1][0] == planet_positions[7][1][0]
 * where index 3 = Mars, index 7 = Saturn in Python's 0-indexed (after Lagna).
 *
 * @param positions - Array of PlanetPosition
 * @returns true if Ghata Dosha is present
 */
export const ghata = (positions: PlanetPosition[]): boolean => {
  const marsPos = positions.find((p) => p.planet === MARS);
  const saturnPos = positions.find((p) => p.planet === SATURN);

  if (!marsPos || !saturnPos) return false;
  return marsPos.rasi === saturnPos.rasi;
};

// ============================================================================
// SHRAPIT DOSHA
// ============================================================================

/**
 * Check for Shrapit Dosha.
 * Rahu and Saturn conjunction (same house/rasi).
 *
 * In Python: planet_positions[8][1][0] == planet_positions[7][1][0]
 * where index 8 = Rahu, index 7 = Saturn in Python's 0-indexed (after Lagna).
 *
 * @param positions - Array of PlanetPosition
 * @returns true if Shrapit Dosha is present
 */
export const shrapit = (positions: PlanetPosition[]): boolean => {
  const rahuPos = positions.find((p) => p.planet === RAHU);
  const saturnPos = positions.find((p) => p.planet === SATURN);

  if (!rahuPos || !saturnPos) return false;
  return rahuPos.rasi === saturnPos.rasi;
};
